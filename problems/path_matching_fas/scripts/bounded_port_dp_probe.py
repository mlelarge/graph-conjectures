"""Bounded-port DP probe for general tournament Path-FAS.

This is a polynomial-DP investigation in the spirit of Section 17 of
`docs/exchange_proof_draft.md`.  The active window has at most 9
vertices (radius-2 score windows), so the *active* part of the state
has polynomial size.  The non-polynomial part is the sleeping-block
component partition.

The candidate here keeps:

  1. position `pos`;
  2. the active vertex set A and its placed subset;
  3. degrees of active vertices;
  4. for each unplaced active x, its flex-hit interface into a
     **bounded back-port set** B_K (the K-step backward closure of A
     under flex-out arcs, intersected with placed vertices);
  5. the union-find partition restricted to A ∪ B_K;
  6. a **bounded forward-port set** F_K of unplaced vertices that can
     hit some placed-active vertex within K future steps, plus their
     interfaces — but with sleeping component identities ABSTRACTED
     beyond F_K.

K is the radius bound.  K=0 recovers the active-bag signature;
K=infinity recovers the dependency-relevant quotient of Section 17;
small finite K interpolates between them.

The "smashing test" compares the bounded-port signature against
extendability for every depth-<=5 FF-pruned prefix of the three known
skew templates plus the toggle / chain-seeded toggle families.  An
extendability collision (two prefixes with same signature but different
extendability) is a concrete refutation of the candidate.  A state-count
explosion (more than poly(n) distinct signatures on the toggle families)
is a *signature*-level failure (Q2 from Section 16.6).

We report:

  - smallest extendability collision in (n, depth);
  - state-count growth on toggle / chain-seeded toggle families at
    varying K.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from collections import defaultdict
from itertools import product
from typing import Sequence

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ff_signature_probe import (  # noqa: E402
    has_completion_ff,
    prefixes,
    valid_prefix_state_ff,
)
from lfo_forced_flexible import _find, _iter_bits  # noqa: E402
from quotient_signature_probe import (  # noqa: E402
    chain_seeded_toggle_prefix,
    chain_seeded_toggle_tournament,
)
from sleeping_block_skew_sweep import SKEW_TEMPLATES  # noqa: E402
from sleeping_bound_refutation import (  # noqa: E402
    toggle_prefix,
    toggle_tournament,
)
from wake_signature_probe import survives_pruning  # noqa: E402


Matrix = Sequence[Sequence[int]]


def bounded_port_signature(
    pos: int,
    prefix_mask: int,
    degree: Sequence[int],
    parent: Sequence[int],
    flex_outmask: Sequence[int],
    windows: Sequence[tuple[int, int]],
    K: int = 1,
) -> tuple:
    """Active bag + radius-K port closure on both sides.

    K=0: pure active-bag signature (no ports kept).
    K=1: ports adjacent to active by one flex arc.
    K>=diam: equivalent to dependency-relevant quotient.
    """
    n = len(windows)
    active = [v for v, (lo, hi) in enumerate(windows) if lo <= pos <= hi]
    active_set = set(active)
    placed = {v for v in range(n) if (prefix_mask >> v) & 1}
    unplaced = [v for v in range(n) if not ((prefix_mask >> v) & 1)]
    placed_active = tuple(v for v in active if v in placed)
    unplaced_active = [v for v in active if v not in placed]

    # Back-port closure: K rounds of flex-out reachability from
    # unplaced active into placed vertices, then bouncing back across
    # unplaced vertices.
    back_ports: set[int] = set()
    front: set[int] = set(unplaced_active)
    for _ in range(K):
        new_back: set[int] = set()
        for x in front:
            for p in _iter_bits(flex_outmask[x] & prefix_mask):
                if p not in active_set:
                    new_back.add(p)
        if not new_back - back_ports:
            break
        back_ports.update(new_back)

    # Forward-port closure: unplaced (non-active) vertices that hit a
    # placed-active vertex within K steps.
    fwd_ports: set[int] = set()
    placed_active_set = set(placed_active)
    for x in unplaced:
        if x in active_set:
            continue
        if any(((flex_outmask[x] >> p) & 1) for p in placed_active_set):
            fwd_ports.add(x)
    # Extend by K-1 backward flex-dependency steps among unplaced
    # vertices to expand fwd_ports.
    for _ in range(max(0, K - 1)):
        added = False
        for y in unplaced:
            if y in fwd_ports or y in active_set:
                continue
            # y hits some fwd_ports element via a flexible arc
            if any(((flex_outmask[y] >> r) & 1) for r in fwd_ports):
                fwd_ports.add(y)
                added = True
        if not added:
            break

    # Union-find labels on the active set + back_ports.  Active vertices
    # use their own identifiers; back/forward ports are recorded by
    # label only (anonymous past/future).
    par = list(parent)
    root_labels: dict[int, int] = {}

    def label(v: int) -> int:
        root = _find(par, v)
        if root not in root_labels:
            root_labels[root] = len(root_labels)
        return root_labels[root]

    active_partition = tuple(
        (v, degree[v], label(v)) for v in active
    )
    back_partition = tuple(
        sorted((degree[v], label(v)) for v in back_ports)
    )
    fwd_partition = tuple(
        sorted((degree[v], label(v)) for v in fwd_ports)
    )

    # Active interfaces: for each unplaced active x, the multiset of
    # (port-label, port-degree) it would hit if placed now.
    active_interfaces = []
    for x in unplaced_active:
        hits = []
        for p in _iter_bits(flex_outmask[x] & prefix_mask):
            if p in active_set:
                hits.append(("act", p, degree[p], label(p)))
            elif p in back_ports:
                hits.append(("back", degree[p], label(p)))
            else:
                hits.append(("opaque", degree[p]))
        active_interfaces.append((x, tuple(sorted(hits))))

    return (
        pos,
        tuple(active),
        placed_active,
        active_partition,
        back_partition,
        fwd_partition,
        tuple(active_interfaces),
    )


# ----------------------------------------------------------------------
# Smashing tests
# ----------------------------------------------------------------------


def find_collision(T: Matrix, depth: int, K: int, *, pruned: bool = True) -> dict | None:
    """Find smallest depth at which a bounded-port collision appears."""
    n = len(T)
    buckets: dict[tuple, list[dict]] = defaultdict(list)
    checked = 0

    for prefix in prefixes(n, depth):
        state = valid_prefix_state_ff(T, prefix)
        if state is None:
            continue
        pos = len(prefix)
        if pruned and not survives_pruning(state, pos, n):
            continue
        checked += 1
        prefix_mask, degree, parent, flex_outmask, windows = state
        sig = bounded_port_signature(
            pos, prefix_mask, degree, parent, flex_outmask, windows, K=K
        )
        ext = has_completion_ff(
            T, pos, prefix_mask, degree, parent,
            tuple(flex_outmask), tuple(windows),
        )
        row = {"prefix": tuple(prefix), "extendable": ext, "pos": pos}
        for other in buckets[sig]:
            if other["extendable"] != ext:
                return {
                    "n": n,
                    "K": K,
                    "depth": depth,
                    "checked_surviving_prefixes": checked,
                    "state_a": other,
                    "state_b": row,
                    "class_size_before_collision": len(buckets[sig]) + 1,
                }
        buckets[sig].append(row)
    return None


def count_signatures_toggle(k: int, K: int) -> dict:
    """How many bounded-port signatures does the toggle family give?"""
    T = toggle_tournament(k)
    n = len(T)
    cut = 2 * k
    seen: dict[tuple, list[tuple[int, ...]]] = defaultdict(list)
    for bits in product((0, 1), repeat=k):
        prefix = toggle_prefix(k, bits)
        state = valid_prefix_state_ff(T, prefix)
        if state is None:
            continue
        if not survives_pruning(state, cut, n):
            continue
        prefix_mask, degree, parent, flex_outmask, windows = state
        sig = bounded_port_signature(
            cut, prefix_mask, degree, parent, flex_outmask, windows, K=K
        )
        seen[sig].append(bits)
    return {
        "k": k,
        "n": n,
        "K": K,
        "distinct_signatures": len(seen),
        "expected_prefixes": 1 << k,
        "largest_class": max((len(v) for v in seen.values()), default=0),
    }


def count_signatures_chain_seeded(k: int, K: int) -> dict:
    """Bounded-port signatures on the chain-seeded toggle family."""
    T = chain_seeded_toggle_tournament(k)
    n = len(T)
    cut = 2 * k + 1
    seen: dict[tuple, list[tuple[int, ...]]] = defaultdict(list)
    extendabilities: set[bool] = set()
    for bits in product((0, 1), repeat=k):
        prefix = chain_seeded_toggle_prefix(k, bits)
        state = valid_prefix_state_ff(T, prefix)
        if state is None:
            continue
        if not survives_pruning(state, cut, n):
            continue
        prefix_mask, degree, parent, flex_outmask, windows = state
        sig = bounded_port_signature(
            cut, prefix_mask, degree, parent, flex_outmask, windows, K=K
        )
        seen[sig].append(bits)
        extendabilities.add(has_completion_ff(
            T, cut, prefix_mask, degree, parent,
            tuple(flex_outmask), tuple(windows),
        ))
    return {
        "k": k,
        "n": n,
        "K": K,
        "distinct_signatures": len(seen),
        "expected_prefixes": 1 << k,
        "largest_class": max((len(v) for v in seen.values()), default=0),
        "extendabilities": sorted(extendabilities),
    }


# ----------------------------------------------------------------------
# Main benchmark
# ----------------------------------------------------------------------


def benchmark(K_values=(0, 1, 2, 3), max_toggle_k=6, depth=5) -> dict:
    out: dict = {"K_values": list(K_values), "depth": depth}
    out["toggle"] = []
    out["chain_seeded"] = []
    for K in K_values:
        out["toggle"].append(
            [count_signatures_toggle(k, K) for k in range(1, max_toggle_k + 1)]
        )
        out["chain_seeded"].append(
            [count_signatures_chain_seeded(k, K) for k in range(1, max_toggle_k + 1)]
        )
    out["templates"] = {}
    for name, T in SKEW_TEMPLATES.items():
        out["templates"][name] = {}
        for K in K_values:
            col = find_collision(T, depth=depth, K=K)
            out["templates"][name][f"K={K}"] = {
                "collision": col is not None,
                "detail": col,
            }
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-toggle-k", type=int, default=6)
    parser.add_argument("--depth", type=int, default=5)
    parser.add_argument(
        "--K", type=int, nargs="+", default=[0, 1, 2, 3],
    )
    args = parser.parse_args()
    res = benchmark(
        K_values=tuple(args.K),
        max_toggle_k=args.max_toggle_k,
        depth=args.depth,
    )
    print(json.dumps(res, indent=2, default=list))


if __name__ == "__main__":
    main()
