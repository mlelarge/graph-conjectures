"""DP-only stress test at large n.

The FF backtrack ground-truth check becomes too slow past n~25. To
test sleeping-block DP scaling alone, this script runs the DP on
padded skew tournaments at large n (50, 80, 100, 150) and reports memo
size, states visited, and runtime. No FF cross-check.

If the DP runs in seconds and memo stays in the hundreds at n=100+,
this is strong evidence that the sleeping-block state space is
polynomial in n on the padded skew family.

Usage:
  uv run python scripts/sleeping_dp_dp_only.py --sizes 30 50 80 100 150
"""
from __future__ import annotations

import argparse
import json
import os
import random
import sys
from typing import Sequence

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sleeping_block_dp import sleeping_block_dp_decide  # noqa: E402
from sleeping_dp_stress import padded_skew_tournament  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sizes", nargs="+", type=int,
                        default=[30, 50, 80, 100, 150])
    parser.add_argument("--samples", type=int, default=10)
    parser.add_argument("--seed", type=int, default=20260525)
    parser.add_argument("--time-budget-sec", type=float, default=120.0)
    parser.add_argument("--out")
    args = parser.parse_args()

    rng = random.Random(args.seed)
    per_n = []
    for n in args.sizes:
        admissible = 0
        memo_sizes = []
        states_list = []
        times = []
        budget_hits = 0
        for _ in range(args.samples):
            T = padded_skew_tournament(n, rng)
            if T is None:
                continue
            out = sleeping_block_dp_decide(T, time_budget_sec=args.time_budget_sec)
            if out.get("reason") == "no_initial_state":
                continue
            admissible += 1
            memo_sizes.append(out["memo_size"])
            states_list.append(out["states_visited"])
            times.append(out["elapsed_sec"])
            if out.get("budget_hit"):
                budget_hits += 1
        per_n.append({
            "n": n,
            "samples": args.samples,
            "admissible": admissible,
            "budget_hits": budget_hits,
            "max_memo": max(memo_sizes) if memo_sizes else 0,
            "mean_memo": sum(memo_sizes) / max(len(memo_sizes), 1),
            "max_states": max(states_list) if states_list else 0,
            "mean_states": sum(states_list) / max(len(states_list), 1),
            "max_time_sec": max(times) if times else 0,
            "mean_time_sec": sum(times) / max(len(times), 1),
        })

    result = {
        "sizes": args.sizes,
        "samples_per_size": args.samples,
        "seed": args.seed,
        "per_n": per_n,
    }
    text = json.dumps(result, indent=2, default=str)
    print(text)
    if args.out:
        with open(args.out, "w") as f:
            f.write(text)


if __name__ == "__main__":
    main()
