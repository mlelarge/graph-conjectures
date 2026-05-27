"""Structural quotient candidates for general tournament Path-FAS.

This probe tests three quotients that are coarser than the
sleeping-block signature but try to keep extendability information:

  Q-multiset: active-bag signature + multiset of (size, edge-count)
              of every dormant (no active-window vertex) backedge
              component containing at least one not-yet-placed
              future-opening vertex.

  Q-halfblock: active-bag + half-block signature, recording for each
               toggle pair whether 0, 1, or 2 of its members are
               placed.  This is the analogue of Section 51's block
               parity.

  Q-imageinterval: active-bag + a coarse interval signature on the
                   image graph, recording for each "block" of 5
                   consecutive positions the size of its currently
                   placed-active subset.

For each quotient we run the same smashing test:
  1. count distinct signatures on the toggle / chain-seeded toggle
     families to test polynomial bound (Q2);
  2. search depth-<=5 prefixes of the three SKEW_TEMPLATES for an
     extendability collision (Q1 soundness).
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter, defaultdict
from itertools import product
from typing import Sequence

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ff_signature_probe import (  # noqa: E402
    active_signature,
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


# ---------------------------------------------------------------------
# Q-multiset: dormant component multiset
# ---------------------------------------------------------------------


def multiset_quotient_signature(
    pos: int,
    prefix_mask: int,
    degree: Sequence[int],
    parent: Sequence[int],
    flex_outmask: Sequence[int],
    windows: Sequence[tuple[int, int]],
) -> tuple:
    """Active bag + multiset of dormant components.

    Dormant component: a backedge-graph component that contains no
    active-window vertex.  We record only its (size, total-degree)
    pair, and only if it contains at least one not-yet-placed vertex
    (otherwise it cannot affect future extendability).
    """
    n = len(windows)
    active = active_signature(pos, prefix_mask, degree, parent, windows)
    active_set = {v for v, (lo, hi) in enumerate(windows) if lo <= pos <= hi}

    par = list(parent)
    comp_members: dict[int, list[int]] = defaultdict(list)
    for v in range(n):
        comp_members[_find(par, v)].append(v)

    dormant: list[tuple[int, int]] = []
    for root, members in comp_members.items():
        if any(m in active_set for m in members):
            continue
        # Has at least one unplaced future-opening vertex?
        unplaced_in_comp = [m for m in members if not ((prefix_mask >> m) & 1)]
        if not unplaced_in_comp:
            # All members placed and inactive — can never re-emerge in
            # active form, so identity is moot.  Skip.
            continue
        size = len(members)
        edges = sum(degree[m] for m in members) // 2
        dormant.append((size, edges))

    return (active, tuple(sorted(dormant)))


# ---------------------------------------------------------------------
# Q-halfblock: half-block signature
# ---------------------------------------------------------------------


def halfblock_quotient_signature(
    pos: int,
    prefix_mask: int,
    degree: Sequence[int],
    parent: Sequence[int],
    flex_outmask: Sequence[int],
    windows: Sequence[tuple[int, int]],
) -> tuple:
    """Active bag + per-window-block half-block parity.

    Group vertices into score-window blocks of width 5 (positions
    [5b, 5b+4]).  For each block, record (#placed, #unplaced) in the
    block.  This is the analogue of Section 51 block parity.
    """
    n = len(windows)
    active = active_signature(pos, prefix_mask, degree, parent, windows)
    block_count: Counter = Counter()
    for v in range(n):
        d_minus = (windows[v][0] + windows[v][1]) // 2  # ~indegree
        b = d_minus // 5
        placed = (prefix_mask >> v) & 1
        block_count[(b, "placed" if placed else "unplaced")] += 1
    return (active, tuple(sorted(block_count.items())))


# ---------------------------------------------------------------------
# Q-imageinterval: image-interval signature
# ---------------------------------------------------------------------


def image_interval_quotient_signature(
    pos: int,
    prefix_mask: int,
    degree: Sequence[int],
    parent: Sequence[int],
    flex_outmask: Sequence[int],
    windows: Sequence[tuple[int, int]],
) -> tuple:
    """Active bag + image-interval load.

    For every position interval [pos+5j, pos+5j+4] (j=-1,0,1,2),
    record the multiset of (windows-overlap-with-interval) for placed
    and unplaced vertices.
    """
    n = len(windows)
    active = active_signature(pos, prefix_mask, degree, parent, windows)
    bands = []
    for j in range(-1, 3):
        lo = pos + 5 * j
        hi = lo + 4
        in_band = [v for v in range(n) if windows[v][0] <= hi and windows[v][1] >= lo]
        placed = sum(1 for v in in_band if (prefix_mask >> v) & 1)
        unplaced = len(in_band) - placed
        bands.append((j, placed, unplaced))
    return (active, tuple(bands))


# ---------------------------------------------------------------------
# Smashing tests
# ---------------------------------------------------------------------


SIGNATURES = {
    "multiset": multiset_quotient_signature,
    "halfblock": halfblock_quotient_signature,
    "image_interval": image_interval_quotient_signature,
}


def find_collision(T: Matrix, depth: int, sigfun, *, pruned: bool = True) -> dict | None:
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
        sig = sigfun(pos, prefix_mask, degree, parent, flex_outmask, windows)
        ext = has_completion_ff(
            T, pos, prefix_mask, degree, parent,
            tuple(flex_outmask), tuple(windows),
        )
        row = {"prefix": tuple(prefix), "extendable": ext, "pos": pos}
        for other in buckets[sig]:
            if other["extendable"] != ext:
                return {
                    "n": n, "depth": depth,
                    "checked_surviving_prefixes": checked,
                    "state_a": other,
                    "state_b": row,
                    "class_size_before_collision": len(buckets[sig]) + 1,
                }
        buckets[sig].append(row)
    return None


def count_signatures_toggle(k: int, sigfun) -> int:
    T = toggle_tournament(k)
    n = len(T)
    cut = 2 * k
    seen: set[tuple] = set()
    for bits in product((0, 1), repeat=k):
        prefix = toggle_prefix(k, bits)
        state = valid_prefix_state_ff(T, prefix)
        if state is None:
            continue
        if not survives_pruning(state, cut, n):
            continue
        prefix_mask, degree, parent, flex_outmask, windows = state
        sig = sigfun(cut, prefix_mask, degree, parent, flex_outmask, windows)
        seen.add(sig)
    return len(seen)


def count_signatures_chain_seeded(k: int, sigfun) -> int:
    T = chain_seeded_toggle_tournament(k)
    n = len(T)
    cut = 2 * k + 1
    seen: set[tuple] = set()
    for bits in product((0, 1), repeat=k):
        prefix = chain_seeded_toggle_prefix(k, bits)
        state = valid_prefix_state_ff(T, prefix)
        if state is None:
            continue
        if not survives_pruning(state, cut, n):
            continue
        prefix_mask, degree, parent, flex_outmask, windows = state
        sig = sigfun(cut, prefix_mask, degree, parent, flex_outmask, windows)
        seen.add(sig)
    return len(seen)


def benchmark(depth=5, max_toggle_k=6) -> dict:
    out: dict = {"depth": depth, "max_toggle_k": max_toggle_k}
    for name, sigfun in SIGNATURES.items():
        entry: dict = {"name": name}
        entry["toggle"] = [
            {"k": k, "distinct": count_signatures_toggle(k, sigfun)}
            for k in range(1, max_toggle_k + 1)
        ]
        entry["chain_seeded"] = [
            {"k": k, "distinct": count_signatures_chain_seeded(k, sigfun)}
            for k in range(1, max_toggle_k + 1)
        ]
        entry["templates"] = {
            tname: find_collision(T, depth=depth, sigfun=sigfun)
            for tname, T in SKEW_TEMPLATES.items()
        }
        out[name] = entry
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--depth", type=int, default=5)
    parser.add_argument("--max-toggle-k", type=int, default=6)
    args = parser.parse_args()
    res = benchmark(depth=args.depth, max_toggle_k=args.max_toggle_k)
    print(json.dumps(res, indent=2, default=list))


if __name__ == "__main__":
    main()
