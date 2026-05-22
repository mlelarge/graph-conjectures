"""Random sampling for the true linear-forest ordering target.

This script deliberately uses `is_linear_forest`, not the weaker
max-degree-2 relaxation. It records enough information to separate
size-bound NO instances (`min_fas > n-1`) from combinatorial NO instances
(`min_fas <= n-1` but no linear-forest ordering).
"""
from __future__ import annotations

import argparse
import json
import os
import random
import sys
import time
from collections import Counter, defaultdict
from itertools import permutations

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from random_check import random_tournament  # noqa: E402
from verify import verify  # noqa: E402


PERMS_BY_N: dict[int, list[tuple[int, ...]]] = {}


def perms(n: int) -> list[tuple[int, ...]]:
    if n not in PERMS_BY_N:
        PERMS_BY_N[n] = list(permutations(range(n)))
    return PERMS_BY_N[n]


def score_sequence(T: list[list[int]]) -> tuple[int, ...]:
    return tuple(sorted(sum(row) for row in T))


def analyze_tournament(T: list[list[int]]) -> dict:
    n = len(T)
    min_fas = None
    has_lfo = False
    has_degree2 = False
    has_forest = False
    lfo_order = None
    degree2_cycle_order = None

    for P in perms(n):
        info = verify(T, list(P))
        if min_fas is None or info["count"] < min_fas:
            min_fas = info["count"]
        if info["max_degree"] <= 2:
            has_degree2 = True
            if not info["is_forest"] and degree2_cycle_order is None:
                degree2_cycle_order = list(P)
        if info["is_forest"]:
            has_forest = True
        if info["is_linear_forest"]:
            has_lfo = True
            lfo_order = list(P)

    return {
        "score_sequence": score_sequence(T),
        "min_fas": min_fas,
        "has_lfo": has_lfo,
        "has_degree2_relaxation": has_degree2,
        "has_forest_ordering": has_forest,
        "lfo_order": lfo_order,
        "degree2_cycle_order": degree2_cycle_order,
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--n", type=int, default=7)
    p.add_argument("--samples", type=int, default=1500)
    p.add_argument("--seed", type=int, default=20260521)
    p.add_argument("--out", default=os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "data",
        "lfo_random_n7_seed20260521.json"))
    p.add_argument("--store-yes-examples", type=int, default=3)
    p.add_argument("--store-no-examples", type=int, default=20)
    args = p.parse_args()

    rng = random.Random(args.seed)
    t0 = time.time()
    yes = 0
    no = 0
    size_no = 0
    combinatorial_no = 0
    score_counts: dict[tuple[int, ...], Counter] = defaultdict(Counter)
    yes_examples = []
    no_examples = []

    for idx in range(args.samples):
        T = random_tournament(args.n, rng)
        a = analyze_tournament(T)
        seq = a["score_sequence"]
        if a["has_lfo"]:
            yes += 1
            score_counts[seq]["yes"] += 1
            if len(yes_examples) < args.store_yes_examples:
                yes_examples.append({"index": idx, "T": T, **a})
        else:
            no += 1
            score_counts[seq]["no"] += 1
            if a["min_fas"] > args.n - 1:
                size_no += 1
                kind = "size"
            else:
                combinatorial_no += 1
                kind = "combinatorial"
            if len(no_examples) < args.store_no_examples:
                no_examples.append({"index": idx, "kind": kind, "T": T, **a})

    score_table = [
        {
            "score_sequence": list(seq),
            "yes": counts["yes"],
            "no": counts["no"],
        }
        for seq, counts in sorted(score_counts.items())
    ]

    result = {
        "n": args.n,
        "samples": args.samples,
        "seed": args.seed,
        "lfo_yes": yes,
        "lfo_no": no,
        "size_no": size_no,
        "combinatorial_no": combinatorial_no,
        "score_table": score_table,
        "yes_examples": yes_examples,
        "no_examples": no_examples,
        "seconds": round(time.time() - t0, 2),
    }

    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w") as f:
        json.dump(result, f, indent=2)
    print(json.dumps({k: result[k] for k in (
        "n", "samples", "seed", "lfo_yes", "lfo_no",
        "size_no", "combinatorial_no", "seconds",
    )}, indent=2))
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
