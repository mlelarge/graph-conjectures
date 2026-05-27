"""Bijunctive analysis of fork-tree legality relations at k=6.

The legality relation of a fork-tree pairing pi at size k is

    R(pi) = { eps in {0,1}^k : eps is extendable on fork-tree(k, pi) }.

This script proves (computationally, by exhaustive sweep over the 720
permutations of [6]) the following at k=6:

  1. Every minimal fatal toggle support has size 2 or 4.
  2. Every minimal fatal toggle support of size 4 contains *at least*
     one V4-detected fatal pair as a subset.  (In fact: more is true.)
  3. R(pi) is closed under the ternary majority operation maj.
  4. Hence R(pi) is bijunctive (2-SAT expressible) for every pi in S_6.

Outputs a JSON catalogue suitable for inclusion in the regression suite
and Section 45 (D34) of the proof draft.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from itertools import combinations, permutations, product
from typing import Sequence

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fork_tree_probe import count_fork_tree_signatures  # noqa: E402
from ordered_peeling_probe import predict_ladder_fatal  # noqa: E402
from rectangle_detachability_probe import (  # noqa: E402
    even_adjacent_blocks,
    exact_toggle_status,
    minimal_fatal_toggle_sets,
    two_interval_ladder_sets,
)


def majority(a: int, b: int, c: int) -> int:
    """Ternary majority on {0,1}."""
    return 1 if a + b + c >= 2 else 0


def maj_tuple(
    a: Sequence[int], b: Sequence[int], c: Sequence[int]
) -> tuple[int, ...]:
    return tuple(majority(ai, bi, ci) for ai, bi, ci in zip(a, b, c))


def legality_relation(k: int, pi: Sequence[int]) -> set[tuple[int, ...]]:
    """Return the set of extendable toggle bit vectors."""
    out = count_fork_tree_signatures(k, pi)
    return {tuple(row["bits"]) for row in out["by_bits"]
            if row["status"] == "ok" and row["extendable"]}


def majority_closure_ok(
    R: set[tuple[int, ...]], max_witnesses: int = 5
) -> tuple[bool, list[dict]]:
    """Check if R is closed under ternary majority.

    Returns (ok, witnesses).  witnesses lists at most max_witnesses
    violating triples.  Early-exits on first failure if max_witnesses=0.
    """
    witnesses: list[dict] = []
    R_list = sorted(R)
    # Speed: enumerate ordered triples; majority is symmetric so we
    # could restrict to combinations_with_replacement, but the full
    # enumeration is small enough at k=6 (|R|<=64).
    for a in R_list:
        for b in R_list:
            for c in R_list:
                m = maj_tuple(a, b, c)
                if m not in R:
                    witnesses.append({"a": list(a), "b": list(b),
                                      "c": list(c), "maj": list(m)})
                    if max_witnesses == 0 or len(witnesses) >= max_witnesses:
                        return False, witnesses
    return (not witnesses), witnesses


def fatal_pairs_from_v4(k: int, pi: Sequence[int]) -> set[tuple[int, ...]]:
    """V4 detects fatal *pairs* directly through exact status; we also
    surface ladder-style fatal pairs predicted by predict_ladder_fatal.

    For our purposes here we use the *exact* fatal-pair set computed by
    the suffix-walk (minimal_fatal_toggle_sets).  This is the ground
    truth that V4 was checked against.
    """
    pairs: set[tuple[int, ...]] = set()
    for s in minimal_fatal_toggle_sets(k, pi):
        if len(s) == 2:
            pairs.add(tuple(sorted(s)))
    return pairs


def analyze_pairing(k: int, pi: Sequence[int]) -> dict:
    """Full bijunctive analysis of one pairing."""
    minimal = minimal_fatal_toggle_sets(k, pi)
    by_size: dict[int, list] = {}
    for s in minimal:
        by_size.setdefault(len(s), []).append(list(s))

    # Decompose size-4 minimal supports.
    fatal_pairs = fatal_pairs_from_v4(k, pi)
    size4_analysis = []
    for s in minimal:
        if len(s) != 4:
            continue
        s_set = set(s)
        contained_pairs = [
            list(p) for p in fatal_pairs if set(p).issubset(s_set)
        ]
        size4_analysis.append({
            "support": list(s),
            "contained_fatal_pairs": contained_pairs,
        })

    # Majority closure on R(pi).
    R = legality_relation(k, pi)
    closed, witnesses = majority_closure_ok(R)

    # All minimal fatal supports have size 2 or 4?
    sizes = sorted(by_size.keys())
    sizes_ok = set(sizes).issubset({2, 4})

    return {
        "k": k,
        "pi": list(pi),
        "R_size": len(R),
        "minimal_fatal_count": len(minimal),
        "minimal_fatal_by_size": {str(sz): lst for sz, lst in by_size.items()},
        "all_sizes_in_2_or_4": sizes_ok,
        "size4_supports_have_contained_pair": all(
            len(row["contained_fatal_pairs"]) >= 1 for row in size4_analysis
        ),
        "size4_analysis": size4_analysis,
        "majority_closed": closed,
        "majority_violations": witnesses,
    }


def sweep_all(k: int) -> dict:
    """Sweep all k! pairings and aggregate results."""
    total = 0
    pi_with_higher = []
    pi_majority_fail = []
    pi_size_outside_2_or_4 = []
    pi_size4_pair_missing = []
    size_histogram: dict[int, int] = {}
    minimal_total = 0
    minimal_size_totals: dict[int, int] = {}

    # For the catalogue we keep a compact per-pi summary.
    catalogue: list[dict] = []

    for pi in permutations(range(k)):
        total += 1
        out = analyze_pairing(k, pi)
        minimal_total += out["minimal_fatal_count"]
        for sz_str, lst in out["minimal_fatal_by_size"].items():
            sz = int(sz_str)
            minimal_size_totals[sz] = minimal_size_totals.get(sz, 0) + len(lst)
        # Number of pairings with any size-4 fatal support
        if "4" in out["minimal_fatal_by_size"]:
            pi_with_higher.append(out["pi"])
        if not out["majority_closed"]:
            pi_majority_fail.append({"pi": out["pi"],
                                     "witnesses": out["majority_violations"]})
        if not out["all_sizes_in_2_or_4"]:
            pi_size_outside_2_or_4.append({
                "pi": out["pi"],
                "minimal_fatal_by_size": out["minimal_fatal_by_size"],
            })
        if not out["size4_supports_have_contained_pair"]:
            pi_size4_pair_missing.append({
                "pi": out["pi"],
                "size4_analysis": out["size4_analysis"],
            })
        catalogue.append({
            "pi": out["pi"],
            "minimal_fatal_by_size": out["minimal_fatal_by_size"],
            "all_sizes_in_2_or_4": out["all_sizes_in_2_or_4"],
            "size4_supports_have_contained_pair":
                out["size4_supports_have_contained_pair"],
            "majority_closed": out["majority_closed"],
        })

    return {
        "k": k,
        "total_pairings": total,
        "minimal_total": minimal_total,
        "minimal_size_totals": minimal_size_totals,
        "pairings_with_size4_support": len(pi_with_higher),
        "pairings_with_majority_failure": len(pi_majority_fail),
        "pairings_with_size_outside_2_or_4": len(pi_size_outside_2_or_4),
        "pairings_with_size4_missing_contained_pair":
            len(pi_size4_pair_missing),
        "size_outside_2_or_4_examples": pi_size_outside_2_or_4[:5],
        "size4_missing_pair_examples": pi_size4_pair_missing[:5],
        "majority_failure_examples": pi_majority_fail[:5],
        "catalogue": catalogue,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--k", type=int, default=6)
    parser.add_argument("--pi", type=str, default=None,
                        help="comma-separated permutation")
    parser.add_argument("--out", type=str, default=None,
                        help="path for full JSON output")
    parser.add_argument("--summary-only", action="store_true",
                        help="print only the headline summary")
    args = parser.parse_args()

    if args.pi:
        pi = tuple(int(x) for x in args.pi.split(","))
        out = analyze_pairing(args.k, pi)
        print(json.dumps(out, indent=2, default=list))
        return

    result = sweep_all(args.k)
    if args.out:
        with open(args.out, "w") as f:
            json.dump(result, f, default=list)
    if args.summary_only:
        keys = [
            "k", "total_pairings", "minimal_total", "minimal_size_totals",
            "pairings_with_size4_support",
            "pairings_with_majority_failure",
            "pairings_with_size_outside_2_or_4",
            "pairings_with_size4_missing_contained_pair",
        ]
        compact = {k: result[k] for k in keys}
        print(json.dumps(compact, indent=2, default=list))
    else:
        # Strip the catalogue from stdout to keep size sane.
        compact = {k: v for k, v in result.items() if k != "catalogue"}
        print(json.dumps(compact, indent=2, default=list))


if __name__ == "__main__":
    main()
