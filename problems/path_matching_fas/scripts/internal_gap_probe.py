"""Probe the three-interval internal-gap P4 criterion.

This script targets the residual class left after the chain-end
criteria P3/P3' fail: three-interval cyclic ladders with at least one
internal B-image gap.  The current candidate criterion is:

    residual ladder is minimally fatal  iff  all selected intervals are
    natural odd-start B-chain pairs {1,2}, {3,4}, ...

The default CLI runs a small random sample.  Use --exhaustive at k=9 to
reproduce the exact 12288/12288 split recorded in the proof draft.
"""
from __future__ import annotations

import argparse
import json
import os
import random
import sys
import time
from itertools import permutations
from typing import Iterable, Sequence

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cyclic_ladder_probe import (  # noqa: E402
    cyclic_ladder_sets,
    internal_gap_profile,
    predict_cyclic_ladder_minimal_fatal,
    targeted_minimal_fatal_certificate,
)


def residual_internal_gap_rows(
    k: int,
    pi: Sequence[int],
    time_budget_sec: float | None = None,
) -> list[dict]:
    """Classify residual three-interval internal-gap ladders for one pi."""
    rows = []
    for selected in cyclic_ladder_sets(k, pi, 3):
        chain_end = predict_cyclic_ladder_minimal_fatal(k, pi, selected)
        if chain_end["prediction"] != "not_minimal_fatal":
            continue
        profile = internal_gap_profile(k, pi, selected)
        if not profile.get("has_internal_gap"):
            continue
        cert = targeted_minimal_fatal_certificate(
            k, pi, selected, time_budget_sec=time_budget_sec
        )
        predicted_minimal = bool(profile["natural_odd_pairs"])
        actual_minimal = bool(cert["minimal_fatal"])
        rows.append({
            "pi": list(pi),
            "selected": list(selected),
            "intervals": [list(iv) for iv in profile["intervals"]],
            "gaps": [
                {
                    **gap,
                    "between": list(gap["between"]),
                    "values": list(gap["values"]),
                    "filler_indices": list(gap["filler_indices"]),
                }
                for gap in profile["gaps"]
            ],
            "natural_odd_pairs": profile["natural_odd_pairs"],
            "predicted_minimal": predicted_minimal,
            "actual_minimal": actual_minimal,
            "certificate_reason": cert["reason"],
            "correct": predicted_minimal == actual_minimal,
        })
    return rows


def _permutations_to_check(
    k: int,
    exhaustive: bool,
    samples: int,
    seed: int,
) -> Iterable[tuple[int, ...]]:
    if exhaustive:
        yield from permutations(range(k))
        return
    rng = random.Random(seed)
    seen = set()
    while len(seen) < samples:
        pi = tuple(rng.sample(range(k), k))
        if pi in seen:
            continue
        seen.add(pi)
        yield pi


def classify_internal_gap_catalogue(
    k: int,
    exhaustive: bool = False,
    samples: int = 200,
    seed: int = 1,
    time_budget_sec: float | None = None,
) -> dict:
    """Aggregate the P4 residual classification over many pairings."""
    start = time.time()
    counts = {
        "odd_predicted_and_minimal": 0,
        "odd_predicted_not_minimal": 0,
        "misaligned_predicted_minimal": 0,
        "misaligned_not_minimal": 0,
    }
    checked = 0
    wrong = []
    for pi in _permutations_to_check(k, exhaustive, samples, seed):
        for row in residual_internal_gap_rows(
            k, pi, time_budget_sec=time_budget_sec
        ):
            checked += 1
            if row["natural_odd_pairs"] and row["actual_minimal"]:
                counts["odd_predicted_and_minimal"] += 1
            elif row["natural_odd_pairs"] and not row["actual_minimal"]:
                counts["odd_predicted_not_minimal"] += 1
            elif (not row["natural_odd_pairs"]) and row["actual_minimal"]:
                counts["misaligned_predicted_minimal"] += 1
            else:
                counts["misaligned_not_minimal"] += 1
            if not row["correct"] and len(wrong) < 10:
                wrong.append(row)
    return {
        "k": k,
        "mode": "exhaustive" if exhaustive else "sample",
        "samples": None if exhaustive else samples,
        "seed": seed,
        "checked": checked,
        "counts": counts,
        "mismatches": wrong,
        "elapsed_sec": round(time.time() - start, 3),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--k", type=int, default=9)
    parser.add_argument("--samples", type=int, default=200)
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--exhaustive", action="store_true")
    parser.add_argument("--time-budget-sec", type=float, default=None)
    args = parser.parse_args()
    print(json.dumps(
        classify_internal_gap_catalogue(
            args.k,
            exhaustive=args.exhaustive,
            samples=args.samples,
            seed=args.seed,
            time_budget_sec=args.time_budget_sec,
        ),
        indent=2,
    ))


if __name__ == "__main__":
    main()
