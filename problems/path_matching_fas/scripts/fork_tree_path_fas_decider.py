"""Polynomial-time Path-FAS decider on fork-tree pairings.

Section 16 of `docs/exchange_proof_draft.md` shows that the fork-tree
toggle family forces the sleeping-block DP state space to size at
least 2^{n/4}.  This module exhibits a polynomial-time decider on
exactly the same family, using the unified V6 fatal detector (Section
38.3) on each candidate cyclic m-interval ladder.

Decision procedure
==================

Given k and a fork-tree pairing pi:

1.  Enumerate candidate cyclic ladder sets of every supported size
    (m = 1, 2, 3, ...).  Each candidate is a set of selected toggle
    indices whose images form m adjacent-pair intervals on the B-side
    and whose block/interval incidence forms a simple cycle (or, for
    m = 1, 2, the degenerate single-block / two-block analogues).

2.  Apply V6 to each candidate via `unified_v6_probe.predict_v6`,
    extended to handle the single-interval (m = 1, size-2) case by
    Section 22.3's natural-odd-start B-chain pair characterization.

3.  Path-FAS = YES iff at least one candidate is V6-predicted minimal
    fatal.  A V6 minimal-fatal toggle set S immediately certifies a
    non-extendable prefix (its toggle bit pattern epsilon = 1_S).

4.  Path-FAS = NO iff no candidate is V6-predicted minimal fatal.
    Subject to the V6 conjecture (Section 38.3), this rules out every
    non-extendable bit pattern.

Correctness is conditional on the V6 conjecture.  V6 has been
exhaustively verified for sizes m = 1, 2, 3, 4 (Sections 22-29, 37-38)
and is supported by isolated examples at larger m.

Runtime
=======

The cost of enumerating size-2m candidates is O(k^m) for fixed m
(via `itertools.combinations`).  Bounding the candidate size by 2M
gives total enumeration cost O(k^M), and V6 evaluation per candidate
is O(k).  The total runtime is therefore O(k^{M+1}) for fixed M.

The brute-force baseline `count_fork_tree_signatures` is
Omega(2^k * poly(k)) since it sweeps all 2^k toggle prefixes.  The
V6 decider replaces this exponential sweep with a fixed-degree
polynomial structural check.

Usage
=====

    uv run python scripts/fork_tree_path_fas_decider.py \
        --k 5 --pi 1,2,3,4,0

    uv run python scripts/fork_tree_path_fas_decider.py \
        --k 11 --pi 1,3,4,5,6,9,10,2,0,8,7
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Sequence

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cyclic_ladder_probe import (  # noqa: E402
    cyclic_ladder_sets,
    cyclic_ladder_structure,
    predict_cyclic_ladder_minimal_fatal,
)
from rectangle_detachability_probe import (  # noqa: E402
    even_adjacent_blocks,
    two_interval_ladder_sets,
)
from unified_v6_probe import predict_v6  # noqa: E402


# ---------------------------------------------------------------------------
# Candidate enumeration
# ---------------------------------------------------------------------------


def single_block_candidates(k: int, pi: Sequence[int]) -> list[tuple[int, ...]]:
    """Size-2 minimal-fatal candidates: a single even-block whose images
    form an adjacent natural-odd-start B-interval (Section 22).

    Pinned at k = 4, 5, 6 (24 + 120 + 720 = 864 pairings): a size-2
    minimal-fatal set is exactly an even-block (2i, 2i+1) with
    images {a, a+1}, a odd, a >= 1.  The decider returns the
    structural candidates without yet committing to fatality; V6
    fires on them via `predict_v6_extended`.
    """
    out: list[tuple[int, ...]] = []
    for block in even_adjacent_blocks(k):
        images = sorted(pi[i] for i in block)
        if len(images) == 2 and images[1] - images[0] == 1:
            # natural odd-start with chain interior on the B-side
            if images[0] >= 1 and images[0] % 2 == 1:
                out.append(tuple(block))
    return out


def enumerate_candidates(
    k: int,
    pi: Sequence[int],
    max_intervals: int | None = None,
) -> dict[int, list[tuple[int, ...]]]:
    """Return candidate ladder sets grouped by interval count m >= 1.

    By default enumerates every supported size from m = 1 up to
    floor(k / 2).  `max_intervals` restricts to candidates with at
    most that many intervals, giving a strictly polynomial running
    time for fixed M.
    """
    if pi is None or len(pi) != k:
        raise ValueError("pi must be a length-k sequence")
    if sorted(pi) != list(range(k)):
        raise ValueError("pi must be a permutation of range(k)")

    block_count = len(even_adjacent_blocks(k))
    upper_m = block_count if max_intervals is None else min(max_intervals, block_count)

    candidates: dict[int, list[tuple[int, ...]]] = {}
    if upper_m >= 1:
        candidates[1] = single_block_candidates(k, pi)
    if upper_m >= 2:
        candidates[2] = list(two_interval_ladder_sets(k, pi))
    for m in range(3, upper_m + 1):
        candidates[m] = list(cyclic_ladder_sets(k, pi, m))
    return candidates


# ---------------------------------------------------------------------------
# V6 classifier (extended to single-block / size-2 case)
# ---------------------------------------------------------------------------


def _predict_v6_size2(
    k: int,
    pi: Sequence[int],
    selected: Sequence[int],
) -> dict:
    """V6 specialized to the m = 1 (size-2) case.

    By Section 22, a single even-block is minimal-fatal iff its image
    is an adjacent natural-odd-start B-pair {a, a+1} with a odd, a >= 1.
    Equivalently: P4 with a one-interval ladder.  No P3 / P3' trigger
    is needed because the lone-block geometry has no internal filler
    above the high image.
    """
    if len(selected) != 2:
        return {"prediction": "not_a_candidate", "reason": "size_not_2"}
    a, b = sorted(selected)
    if a % 2 != 0 or b != a + 1:
        return {"prediction": "not_a_candidate", "reason": "not_even_block"}
    images = sorted([pi[a], pi[b]])
    if images[1] - images[0] != 1:
        return {"prediction": "not_a_candidate", "reason": "image_not_adjacent"}
    if images[0] < 1:
        return {"prediction": "not_a_candidate", "reason": "image_touches_root"}
    if images[0] % 2 == 1:
        return {
            "prediction": "minimal_fatal",
            "reason": "P4_size2_natural_odd_start",
            "intervals": [list(images)],
        }
    return {
        "prediction": "not_minimal_fatal",
        "reason": "P4_size2_misaligned",
        "intervals": [list(images)],
    }


def predict_v6_extended(
    k: int,
    pi: Sequence[int],
    selected: Sequence[int],
) -> dict:
    """V6 predictor extended to handle size-2 candidates.

    For size-2 selected sets we apply the natural-odd-start rule from
    Section 22.  For size >= 4 we delegate to `predict_v6`.
    """
    selected = tuple(sorted(selected))
    if len(selected) == 2:
        return _predict_v6_size2(k, pi, selected)
    return predict_v6(k, pi, selected)


def classify_minimal_fatal(
    k: int,
    pi: Sequence[int],
    max_intervals: int | None = None,
) -> dict:
    """Apply V6 to every enumerated candidate and collect the
    predicted-minimal-fatal sets.

    Returns
    -------
    A dict with keys:
      - "minimal_fatal": list of tuple-selected sets predicted fatal
      - "by_size": dict m -> list of predicted-fatal selected sets
      - "candidates_seen": dict m -> count of candidates examined
      - "details": list of (selected, prediction) tuples for diagnostics
    """
    candidates = enumerate_candidates(k, pi, max_intervals=max_intervals)
    minimal_fatal: list[tuple[int, ...]] = []
    by_size: dict[int, list[tuple[int, ...]]] = {}
    details: list[dict] = []
    candidates_seen: dict[int, int] = {}

    for m, cand_list in sorted(candidates.items()):
        candidates_seen[m] = len(cand_list)
        by_size.setdefault(m, [])
        for cand in cand_list:
            pred = predict_v6_extended(k, pi, cand)
            details.append({
                "selected": list(cand),
                "m": m,
                "prediction": pred["prediction"],
                "reason": pred.get("reason"),
            })
            if pred["prediction"] == "minimal_fatal":
                minimal_fatal.append(cand)
                by_size[m].append(cand)

    return {
        "minimal_fatal": minimal_fatal,
        "by_size": by_size,
        "candidates_seen": candidates_seen,
        "details": details,
    }


# ---------------------------------------------------------------------------
# Top-level Path-FAS decision
# ---------------------------------------------------------------------------


def decide_fork_tree(
    k: int,
    pi: Sequence[int],
    max_intervals: int | None = None,
) -> dict:
    """Decide Path-FAS on a fork-tree pairing using V6.

    Returns
    -------
    A dict with keys:
      - "path_fas": "YES" if some V6-predicted minimal fatal set
                    exists, else "NO".
      - "witness": one V6 minimal fatal selected set (as a list) if
                   path_fas = YES, else None.  This set's
                   characteristic toggle bit pattern epsilon = 1_S is
                   a concrete non-extendable prefix.
      - "minimal_fatal_sets": every V6 minimal fatal set (sorted by
                              size then index) for diagnostics.
      - "candidates_seen": count of structural candidates examined.
      - "max_intervals": the m-bound used, mirrored back.
    """
    result = classify_minimal_fatal(k, pi, max_intervals=max_intervals)
    fatal = sorted(result["minimal_fatal"], key=lambda s: (len(s), s))
    witness = list(fatal[0]) if fatal else None
    return {
        "k": k,
        "pi": list(pi),
        "path_fas": "YES" if fatal else "NO",
        "witness": witness,
        "witness_bits": (
            [1 if i in set(fatal[0]) else 0 for i in range(k)] if fatal else None
        ),
        "minimal_fatal_sets": [list(s) for s in fatal],
        "candidates_seen": result["candidates_seen"],
        "max_intervals": max_intervals,
    }


# ---------------------------------------------------------------------------
# Runtime documentation
# ---------------------------------------------------------------------------


def decider_runtime_analysis() -> dict:
    """Return a structured summary of the runtime complexity.

    The decider's cost is dominated by candidate enumeration.  For
    each size m in 1..M, where M is the `max_intervals` bound, the
    number of cyclic ladder candidates is at most C(floor(k/2), m),
    which is O(k^m).  Applying V6 to one candidate is O(k) (sorting
    and a linear scan of fillers).  Summing over m = 1..M yields
    O(k^M) total candidates and O(k^{M+1}) total V6 evaluations.

    The brute-force `count_fork_tree_signatures` requires
    Theta(2^k * poly(k)) since it sweeps all 2^k toggle prefixes.
    The V6 decider replaces the 2^k sweep with a structural check of
    polynomial degree.

    For the empirically validated bound M = 4 (covering sizes 2, 4,
    6, 8 -- all observed minimal fatal sizes up to k = 11), the
    decider runs in O(k^5) time.
    """
    return {
        "candidate_enumeration_per_size_m": "O(k^m)",
        "v6_per_candidate": "O(k)",
        "total_for_size_bound_M": "O(k^{M+1})",
        "brute_force_baseline": "Theta(2^k * poly(k))",
        "empirical_size_bound_observed": "M = 4 (sizes 2, 4, 6, 8)",
        "decider_complexity_at_M4": "O(k^5)",
        "v6_correctness": (
            "Subject to the Unified V6 conjecture (Section 38.3). "
            "Exhaustively verified at sizes m = 1, 2, 3, 4; supported "
            "by isolated examples at larger m."
        ),
    }


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--k", type=int, default=None)
    parser.add_argument(
        "--pi",
        type=str,
        default=None,
        help="comma-separated permutation, e.g. '1,2,3,4,0'",
    )
    parser.add_argument(
        "--max-intervals",
        type=int,
        default=None,
        help="cap candidate interval count (default: floor(k/2))",
    )
    parser.add_argument(
        "--show-runtime",
        action="store_true",
        help="print the runtime analysis instead of deciding",
    )
    args = parser.parse_args()

    if args.show_runtime:
        print(json.dumps(decider_runtime_analysis(), indent=2))
        return

    if args.k is None or args.pi is None:
        parser.error("--k and --pi are required unless --show-runtime is set")
    pi = tuple(int(x) for x in args.pi.split(","))
    decision = decide_fork_tree(args.k, pi, max_intervals=args.max_intervals)
    print(json.dumps(decision, indent=2, default=list))


if __name__ == "__main__":
    main()
