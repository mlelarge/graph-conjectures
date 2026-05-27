"""Suffix-walk detachability probe for fork-tree rectangles.

The pair-only Alternating-Rectangle Criterion from Section 22 is too
weak once arbitrary fork pairings are allowed.  This module implements
the more literal "approach A": run a suffix-walk search and extract
minimal fatal toggle sets.

For a fork-tree pairing pi and a toggle set S:

  * S is detachable if the FF-pruned state with exactly S toggles has a
    completing suffix.
  * S is minimally fatal if it is not detachable, but every one-toggle
    deletion S\\{x} is detachable.

This is still an exact probe, not a polynomial proof.  Its value is
that it separates the real target from false pair-only slogans:

  * at k=4, all minimal fatal sets are fatal pairs of the Section 22
    type;
  * at k=5, higher-order minimal fatal sets already occur.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from functools import lru_cache
from itertools import combinations, permutations, product
from typing import Sequence

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ff_signature_probe import (  # noqa: E402
    _add_flexible_vertex,
    _canonical_parent,
    valid_prefix_state_ff,
)
from fork_tree_probe import (  # noqa: E402
    count_fork_tree_signatures,
    fork_tree_prefix,
    fork_tree_tournament,
)
from lfo_forced_flexible import _forced_future_ok_flexible, _iter_bits  # noqa: E402
from lfo_score_window import hall_interval_ok  # noqa: E402
from wake_signature_probe import survives_pruning  # noqa: E402


Matrix = Sequence[Sequence[int]]
State = tuple[int, tuple[int, ...], tuple[int, ...], Sequence[int], Sequence[tuple[int, int]]]


def bits_from_set(k: int, selected: Sequence[int]) -> tuple[int, ...]:
    bits = [0] * k
    for i in selected:
        if not (0 <= i < k):
            raise ValueError(f"toggle index {i} outside [0,{k})")
        bits[i] = 1
    return tuple(bits)


def fork_prefix_state(
    k: int,
    pi: Sequence[int],
    selected: Sequence[int],
) -> tuple[list[list[bool]], int, State] | None:
    """Return the FF state for the fork-tree prefix with selected toggles."""
    T = fork_tree_tournament(k, pi)
    cut = 2 * k + 1
    prefix = fork_tree_prefix(k, bits_from_set(k, selected))
    state = valid_prefix_state_ff(T, prefix)
    if state is None:
        return None
    if not survives_pruning(state, cut, len(T)):
        return None
    return T, cut, state


def find_completion_suffix(
    T: Matrix,
    cut: int,
    state: State,
    time_budget_sec: float | None = None,
) -> dict:
    """Return one completing suffix, if any, using exact FF recursion."""
    n = len(T)
    all_mask = (1 << n) - 1
    prefix_mask0, degree0, parent0, flex_outmask, windows = state
    start = time.time()
    nodes = 0
    budget_hit = False

    @lru_cache(maxsize=None)
    def rec(
        pos: int,
        prefix_mask: int,
        degree: tuple[int, ...],
        parent: tuple[int, ...],
    ) -> tuple[int, ...] | None:
        nonlocal nodes, budget_hit
        nodes += 1
        if time_budget_sec is not None and time.time() - start > time_budget_sec:
            budget_hit = True
            return None
        if prefix_mask == all_mask:
            return ()
        remaining = all_mask ^ prefix_mask
        if not hall_interval_ok(remaining, pos, windows, n):
            return None
        ok, _reason = _forced_future_ok_flexible(
            flex_outmask,
            prefix_mask,
            remaining,
            degree,
            parent,
        )
        if not ok:
            return None
        candidates = [
            v for v in _iter_bits(remaining)
            if windows[v][0] <= pos <= windows[v][1]
        ]
        candidates.sort(
            key=lambda x: (
                (flex_outmask[x] & prefix_mask).bit_count(),
                -windows[x][1],
            ),
            reverse=True,
        )
        for x in candidates:
            nxt = _add_flexible_vertex(flex_outmask, prefix_mask, degree, parent, x)
            if nxt is None:
                continue
            child_degree, child_parent = nxt
            suffix = rec(
                pos + 1,
                prefix_mask | (1 << x),
                child_degree,
                _canonical_parent(child_parent),
            )
            if suffix is not None:
                return (x,) + suffix
        return None

    suffix = rec(cut, prefix_mask0, degree0, _canonical_parent(parent0))
    return {
        "detachable": suffix is not None,
        "suffix": list(suffix) if suffix is not None else None,
        "nodes": nodes,
        "budget_hit": budget_hit,
    }


def exact_toggle_status(k: int, pi: Sequence[int]) -> dict[tuple[int, ...], bool]:
    """Map every toggle bit vector to exact extendability."""
    out = count_fork_tree_signatures(k, pi)
    status: dict[tuple[int, ...], bool] = {}
    for row in out["by_bits"]:
        if row["status"] != "ok":
            continue
        status[tuple(row["bits"])] = bool(row["extendable"])
    return status


def minimal_fatal_toggle_sets(k: int, pi: Sequence[int]) -> list[tuple[int, ...]]:
    """Return inclusion-minimal non-detachable toggle sets."""
    status = exact_toggle_status(k, pi)
    minimal: list[tuple[int, ...]] = []
    for bits, extendable in sorted(status.items(), key=lambda item: (sum(item[0]), item[0])):
        if extendable:
            continue
        selected = tuple(i for i, b in enumerate(bits) if b)
        if all(tuple(1 if j in selected and j != i else 0 for j in range(k)) in status
               and status[tuple(1 if j in selected and j != i else 0 for j in range(k))]
               for i in selected):
            minimal.append(selected)
    return minimal


def even_adjacent_blocks(k: int) -> list[tuple[int, int]]:
    """Return the even-odd adjacent toggle blocks (0,1), (2,3), ... ."""
    return [(i, i + 1) for i in range(0, k - 1, 2)]


def anchored_alternating_ladder_sets(k: int, pi: Sequence[int]) -> list[tuple[int, ...]]:
    """Candidate higher-order fatal sets found by the suffix-walk probe.

    A low-order higher fatal set is an anchored alternating ladder when:

      * it is the union of two even-odd adjacent toggle blocks;
      * its four images are exactly the first four B-chain positions
        above the root, {1,2,3,4}; and
      * each toggle block receives one low image from {1,2} and one
        high image from {3,4}.

    This is not asserted as the final theorem for all k.  It is the
    exact static description of the k=5 and k=6 higher-order catalogue.
    """
    ladders: list[tuple[int, ...]] = []
    low = {1, 2}
    high = {3, 4}
    for block_a, block_b in combinations(even_adjacent_blocks(k), 2):
        selected = tuple(sorted(block_a + block_b))
        images = {pi[i] for i in selected}
        if images != {1, 2, 3, 4}:
            continue
        image_a = {pi[i] for i in block_a}
        image_b = {pi[i] for i in block_b}
        if (
            len(image_a & low) == 1
            and len(image_a & high) == 1
            and len(image_b & low) == 1
            and len(image_b & high) == 1
        ):
            ladders.append(selected)
    return ladders


def two_interval_ladder_sets(k: int, pi: Sequence[int]) -> list[tuple[int, ...]]:
    """Naive generalized four-ladder candidates.

    This loosens `anchored_alternating_ladder_sets`: the four images no
    longer have to be {1,2,3,4}.  Instead they may be any two adjacent
    B-chain intervals {a,a+1} and {b,b+1}, with a >= 1, b > a, and each
    even-odd toggle block taking one image from each interval.

    The function is intentionally exposed because it is the next false
    candidate: it finds real non-initial fatal ladders at k=7, but it
    also overpredicts.  That overprediction pins the fact that
    detachability depends on A-side placement of the filler blocks, not
    only on the image set.
    """
    ladders: set[tuple[int, ...]] = set()
    for block_a, block_b in combinations(even_adjacent_blocks(k), 2):
        selected = tuple(sorted(block_a + block_b))
        images = {pi[i] for i in selected}
        if 0 in images or len(images) != 4:
            continue
        sorted_images = sorted(images)
        for low_pair in combinations(sorted_images, 2):
            low = set(low_pair)
            high = images - low
            if len(high) != 2:
                continue
            if max(low) - min(low) != 1 or max(high) - min(high) != 1:
                continue
            image_a = {pi[i] for i in block_a}
            image_b = {pi[i] for i in block_b}
            if len(image_a & low) == 1 and len(image_b & low) == 1:
                ladders.add(selected)
    return sorted(ladders)


def pair_detachability_report(
    k: int,
    pi: Sequence[int],
    time_budget_sec: float | None = None,
) -> list[dict]:
    """Run suffix-walk detachability on all two-toggle sets."""
    rows: list[dict] = []
    for i, j in combinations(range(k), 2):
        setup = fork_prefix_state(k, pi, (i, j))
        if setup is None:
            rows.append({"pair": [i, j], "status": "invalid_or_pruned"})
            continue
        T, cut, state = setup
        det = find_completion_suffix(T, cut, state, time_budget_sec=time_budget_sec)
        rows.append({
            "pair": [i, j],
            "status": "ok",
            "detachable": det["detachable"],
            "suffix": det["suffix"],
            "nodes": det["nodes"],
            "f1_candidate": (
                j == i + 1
                and i % 2 == 0
                and abs(pi[i] - pi[j]) == 1
            ),
        })
    return rows


def evaluate_pairing(k: int, pi: Sequence[int]) -> dict:
    """Summarize minimal fatal sets and pair-detachability."""
    minimal = minimal_fatal_toggle_sets(k, pi)
    pair_rows = pair_detachability_report(k, pi)
    fatal_pairs = [
        tuple(row["pair"]) for row in pair_rows
        if row["status"] == "ok" and not row["detachable"]
    ]
    higher = [s for s in minimal if len(s) > 2]
    ladder_sets = anchored_alternating_ladder_sets(k, pi)
    two_interval_ladders = two_interval_ladder_sets(k, pi)
    return {
        "k": k,
        "pi": list(pi),
        "minimal_fatal_sets": [list(s) for s in minimal],
        "fatal_pairs": [list(s) for s in fatal_pairs],
        "higher_order_minimal_fatal_sets": [list(s) for s in higher],
        "anchored_alternating_ladder_sets": [list(s) for s in ladder_sets],
        "two_interval_ladder_sets": [list(s) for s in two_interval_ladders],
        "anchored_ladder_matches_higher_order": sorted(higher) == sorted(ladder_sets),
        "pair_rows": pair_rows,
    }


def all_pairings_summary(k: int) -> dict:
    """Sweep all k! pairings and report higher-order obstructions."""
    rows = [evaluate_pairing(k, pi) for pi in permutations(range(k))]
    with_fatal = [r for r in rows if r["minimal_fatal_sets"]]
    with_higher = [r for r in rows if r["higher_order_minimal_fatal_sets"]]
    ladder_mismatches = [
        {
            "pi": r["pi"],
            "higher_order_minimal_fatal_sets": r["higher_order_minimal_fatal_sets"],
            "anchored_alternating_ladder_sets": r["anchored_alternating_ladder_sets"],
        }
        for r in rows
        if not r["anchored_ladder_matches_higher_order"]
    ]
    compact_higher = [
        {
            "pi": r["pi"],
            "minimal_fatal_sets": r["minimal_fatal_sets"],
            "fatal_pairs": r["fatal_pairs"],
            "higher_order_minimal_fatal_sets": r["higher_order_minimal_fatal_sets"],
            "anchored_alternating_ladder_sets": r["anchored_alternating_ladder_sets"],
        }
        for r in with_higher[:5]
    ]
    return {
        "k": k,
        "total_pairings": len(rows),
        "pairings_with_any_fatal_set": len(with_fatal),
        "pairings_with_higher_order_fatal_set": len(with_higher),
        "anchored_ladder_mismatches": len(ladder_mismatches),
        "anchored_ladder_mismatch_examples": ladder_mismatches[:5],
        "higher_order_examples": compact_higher,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--k", type=int, default=5)
    parser.add_argument("--pi", nargs="*", type=int,
                        help="explicit permutation; default uses cyclic shift")
    parser.add_argument("--all", action="store_true")
    args = parser.parse_args()

    if args.all:
        result = all_pairings_summary(args.k)
    else:
        pi = tuple(args.pi) if args.pi else tuple((i + 1) % args.k for i in range(args.k))
        result = evaluate_pairing(args.k, pi)
    print(json.dumps(result, indent=2, default=list))


if __name__ == "__main__":
    main()
