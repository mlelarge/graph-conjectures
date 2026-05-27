"""Probe quotient signatures below sleeping-block.

The toggle-pair family refutes polynomial state counting for the full
sleeping-block signature: it creates 2^k different sleeping partitions
that are all extendable.  This module tests a coarser candidate.

The candidate keeps only the part of the sleeping partition that can be
reached by future flexible-hit dependencies from the current placed
ports.  If no unplaced vertex can ever hit a placed vertex in a sleeping
component, the exact internal partition of that sleeping component is
ignored.

This is an empirical probe, not a proof.  The key regression checks are:

  * collapse the toggle family to O(1), ideally one class;
  * preserve the sleeping-block separation on the known visible-latent
    counterexample templates.
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
from sleeping_bound_refutation import (  # noqa: E402
    toggle_prefix,
    toggle_tournament,
)
from sleeping_block_skew_sweep import SKEW_TEMPLATES  # noqa: E402
from wake_signature_probe import survives_pruning  # noqa: E402


Matrix = Sequence[Sequence[int]]


def chain_seeded_toggle_tournament(k: int) -> list[list[bool]]:
    """Return the 4k+1 vertex chain-seeded toggle tournament.

    Vertices are
      a_i = 2i, b_i = 2i+1, p = 2k,
      y_j = 2k+1+j for 0 <= j < 2k,
    with f_i = y_{2i} and g_i = y_{2i+1}.

    Start with the transitive tournament.  Reverse f_i -> a_i and
    g_i -> b_i, as in the toggle lower bound.  Then add a dependency
    seed by reversing y_0 -> p and y_j -> y_{j-1}.  At the cut after p
    is placed, the quotient relevance closure contains the whole future
    chain, so it retains every toggle bit.
    """
    if k <= 0:
        raise ValueError("k must be positive")
    n = 4 * k + 1
    seed = 2 * k
    T = [[False] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            T[i][j] = True
            T[j][i] = False

    for i in range(k):
        a = 2 * i
        b = 2 * i + 1
        f = 2 * k + 1 + 2 * i
        g = f + 1
        T[f][a] = True
        T[a][f] = False
        T[g][b] = True
        T[b][g] = False

    y0 = 2 * k + 1
    T[y0][seed] = True
    T[seed][y0] = False
    for j in range(1, 2 * k):
        y = 2 * k + 1 + j
        prev = y - 1
        T[y][prev] = True
        T[prev][y] = False
    return T


def chain_seeded_toggle_prefix(k: int, bits: Sequence[int]) -> tuple[int, ...]:
    """Toggle prefix plus the dependency seed vertex p."""
    if len(bits) != k:
        raise ValueError("bits length must equal k")
    prefix: list[int] = []
    for i, bit in enumerate(bits):
        a = 2 * i
        b = 2 * i + 1
        if bit:
            prefix.extend((b, a))
        else:
            prefix.extend((a, b))
    prefix.append(2 * k)
    return tuple(prefix)


def dependency_quotient_signature(
    pos: int,
    prefix_mask: int,
    degree: Sequence[int],
    parent: Sequence[int],
    flex_outmask: Sequence[int],
    windows: Sequence[tuple[int, int]],
) -> tuple:
    """Return the dependency-relevant quotient of sleeping-block.

    Let P be the set of already placed vertices that some unplaced
    vertex can hit by a flexible backedge.  These are the current
    placed ports into the future.  A future vertex y is relevant if
    y can hit a relevant vertex after that vertex is placed; formally,
    relevance is the backward closure of P under arcs y -> r encoded by
    `flex_outmask[y]`.

    We record degrees and component labels only on this relevance
    closure.  Active-window identities and placed-active identities are
    still retained for scheduling, but active vertices with no path to a
    placed port no longer force their sleeping component identity into
    the state.
    """
    n = len(windows)
    active = tuple(v for v, (lo, hi) in enumerate(windows) if lo <= pos <= hi)
    placed = {v for v in range(n) if (prefix_mask >> v) & 1}
    unplaced = [v for v in range(n) if not ((prefix_mask >> v) & 1)]
    placed_active = tuple(v for v in active if v in placed)

    placed_ports: set[int] = set()
    for x in unplaced:
        placed_ports.update(_iter_bits(flex_outmask[x] & prefix_mask))

    relevant: set[int] = set(placed_ports)
    changed = True
    while changed:
        changed = False
        for y in unplaced:
            if y in relevant:
                continue
            if any((flex_outmask[y] >> r) & 1 for r in relevant):
                relevant.add(y)
                changed = True

    par = list(parent)
    root_labels: dict[int, int] = {}

    def label(v: int) -> int:
        root = _find(par, v)
        if root not in root_labels:
            root_labels[root] = len(root_labels)
        return root_labels[root]

    relevant_order = tuple(sorted(relevant))
    relevant_partition = tuple(
        (v, degree[v], label(v))
        for v in relevant_order
    )

    # For currently active unplaced vertices, record only the future-hit
    # interface into the relevance closure.  Hits outside the closure are
    # precisely the ones this quotient declares irrelevant.
    active_hit_interface = []
    for x in active:
        if (prefix_mask >> x) & 1:
            continue
        hits = tuple(
            (p, degree[p], label(p))
            for p in _iter_bits(flex_outmask[x] & prefix_mask)
            if p in relevant
        )
        active_hit_interface.append((x, hits))

    return (
        pos,
        active,
        placed_active,
        tuple(sorted(placed_ports)),
        relevant_partition,
        tuple(active_hit_interface),
    )


def count_toggle_quotient_signatures(k: int) -> dict:
    """Count dependency-quotient classes on the toggle family."""
    T = toggle_tournament(k)
    n = len(T)
    cut = 2 * k
    signatures: dict[tuple, list[tuple[int, ...]]] = defaultdict(list)
    invalid: list[dict] = []

    for bits in product((0, 1), repeat=k):
        prefix = toggle_prefix(k, bits)
        state = valid_prefix_state_ff(T, prefix)
        if state is None:
            invalid.append({"bits": bits, "reason": "invalid_prefix"})
            continue
        if not survives_pruning(state, cut, n):
            invalid.append({"bits": bits, "reason": "ff_pruned"})
            continue
        prefix_mask, degree, parent, flex_outmask, windows = state
        sig = dependency_quotient_signature(
            cut, prefix_mask, degree, parent, flex_outmask, windows
        )
        signatures[sig].append(bits)

    return {
        "k": k,
        "n": n,
        "cut": cut,
        "expected_prefixes": 1 << k,
        "quotient_signatures": len(signatures),
        "largest_class": max((len(v) for v in signatures.values()), default=0),
        "invalid": invalid[:5],
    }


def count_chain_seeded_quotient_signatures(k: int) -> dict:
    """Count quotient classes on the chain-seeded toggle family."""
    T = chain_seeded_toggle_tournament(k)
    n = len(T)
    cut = 2 * k + 1
    signatures: dict[tuple, list[tuple[int, ...]]] = defaultdict(list)
    invalid: list[dict] = []
    extendabilities: set[bool] = set()

    for bits in product((0, 1), repeat=k):
        prefix = chain_seeded_toggle_prefix(k, bits)
        state = valid_prefix_state_ff(T, prefix)
        if state is None:
            invalid.append({"bits": bits, "reason": "invalid_prefix"})
            continue
        if not survives_pruning(state, cut, n):
            invalid.append({"bits": bits, "reason": "ff_pruned"})
            continue
        prefix_mask, degree, parent, flex_outmask, windows = state
        sig = dependency_quotient_signature(
            cut, prefix_mask, degree, parent, flex_outmask, windows
        )
        signatures[sig].append(bits)
        extendabilities.add(has_completion_ff(
            T, cut, prefix_mask, degree, parent,
            tuple(flex_outmask), tuple(windows),
        ))

    collisions = [patterns for patterns in signatures.values() if len(patterns) > 1]
    return {
        "k": k,
        "n": n,
        "cut": cut,
        "expected_prefixes": 1 << k,
        "quotient_signatures": len(signatures),
        "largest_class": max((len(v) for v in signatures.values()), default=0),
        "collisions": len(collisions),
        "extendabilities": sorted(extendabilities),
        "invalid": invalid[:5],
    }


def find_quotient_extendability_collision(
    T: Matrix,
    depth: int = 5,
    pruned: bool = True,
) -> dict | None:
    """Search for an extendability collision under the quotient."""
    n = len(T)
    buckets: dict[tuple, list[dict]] = defaultdict(list)
    checked = 0
    completion_checked = 0

    for prefix in prefixes(n, depth):
        state = valid_prefix_state_ff(T, prefix)
        if state is None:
            continue
        pos = len(prefix)
        if pruned and not survives_pruning(state, pos, n):
            continue
        checked += 1
        prefix_mask, degree, parent, flex_outmask, windows = state
        sig = dependency_quotient_signature(
            pos, prefix_mask, degree, parent, flex_outmask, windows
        )
        ext = has_completion_ff(
            T, pos, prefix_mask, degree, parent,
            tuple(flex_outmask), tuple(windows),
        )
        completion_checked += 1
        row = {"prefix": tuple(prefix), "extendable": ext, "pos": pos}
        for other in buckets[sig]:
            if other["extendable"] != ext:
                return {
                    "n": n,
                    "depth": depth,
                    "checked_surviving_prefixes": checked,
                    "checked_completion_prefixes": completion_checked,
                    "state_a": other,
                    "state_b": row,
                    "signature_class_size": len(buckets[sig]) + 1,
                }
        buckets[sig].append(row)
    return None


def benchmark(max_toggle_k: int = 8, depth: int = 5) -> dict:
    return {
        "toggle": [
            count_toggle_quotient_signatures(k)
            for k in range(1, max_toggle_k + 1)
        ],
        "chain_seeded_toggle": [
            count_chain_seeded_quotient_signatures(k)
            for k in range(1, max_toggle_k + 1)
        ],
        "templates": {
            name: find_quotient_extendability_collision(T, depth=depth)
            for name, T in SKEW_TEMPLATES.items()
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-toggle-k", type=int, default=8)
    parser.add_argument("--depth", type=int, default=5)
    args = parser.parse_args()
    print(json.dumps(
        benchmark(max_toggle_k=args.max_toggle_k, depth=args.depth),
        indent=2,
        default=list,
    ))


if __name__ == "__main__":
    main()
