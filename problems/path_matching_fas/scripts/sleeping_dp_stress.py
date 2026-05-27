"""Stress test for the sleeping-block DP.

Sample random tournaments at increasing n, run the DP, and report:

  - decision agreement with FF backtrack;
  - memo size and states visited;
  - growth of max memo size as n increases.

If the DP's memo size grows polynomially in n on stress samples, this
is strong empirical evidence for sleeping-block as a polynomial DP
state.  If memo blows up exponentially, sleeping-block alone isn't
enough.

Usage:
  uv run python scripts/sleeping_dp_stress.py --n-min 10 --n-max 18 \
                                              --samples 20
"""
from __future__ import annotations

import argparse
import json
import os
import random
import sys
import time
from typing import Sequence

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lfo_forced_flexible import find_lfo_order_forced_flexible  # noqa: E402
from sleeping_block_dp import sleeping_block_dp_decide  # noqa: E402


Matrix = list[list[int]]


def random_tournament(n: int, p: float, rng: random.Random) -> Matrix:
    T = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            if rng.random() < p:
                T[i][j] = 1
            else:
                T[j][i] = 1
    return T


def padded_skew_tournament(n: int, rng: random.Random) -> Matrix:
    """Sample a padded skew tournament at size n via random template
    selection + random arc perturbations + transitive padding to reach n.

    Padded skew tournaments tend to be LFO-admissible even at larger n,
    in contrast to random p=0.5 tournaments.
    """
    from sleeping_block_skew_sweep import SKEW_TEMPLATES, perturb
    from wake_signature_probe import _insert_transitive_padding_vertex

    name = rng.choice(list(SKEW_TEMPLATES.keys()))
    T = [row[:] for row in SKEW_TEMPLATES[name]]
    n_base = len(T)
    if n < n_base:
        return None  # can't shrink
    k_flips = rng.randint(0, 3)
    T = perturb(T, k_flips, rng)
    for _ in range(n - n_base):
        T = _insert_transitive_padding_vertex(T, rng.randint(0, len(T)))
    return T


def stress(
    n_min: int,
    n_max: int,
    samples_per_n: int,
    p: float,
    seed: int,
    time_budget_sec: float,
    generator: str = "random",
) -> dict:
    rng = random.Random(seed)
    per_n = []
    for n in range(n_min, n_max + 1):
        admissible = 0
        agree = 0
        disagree_examples = []
        memo_sizes = []
        states_visited_list = []
        dp_times = []
        ff_times = []
        for s in range(samples_per_n):
            if generator == "random":
                T = random_tournament(n, p, rng)
            elif generator == "padded_skew":
                T = padded_skew_tournament(n, rng)
                if T is None:
                    continue
            else:
                raise ValueError("generator must be 'random' or 'padded_skew'")
            # FF ground truth
            ff_start = time.time()
            ff = find_lfo_order_forced_flexible(T)
            ff_time = time.time() - ff_start
            # DP
            dp_start = time.time()
            dp = sleeping_block_dp_decide(T, time_budget_sec=time_budget_sec)
            dp_time = time.time() - dp_start

            if dp.get("reason") == "no_initial_state":
                continue
            admissible += 1
            if dp["found"] == ff["found"]:
                agree += 1
            elif len(disagree_examples) < 3:
                disagree_examples.append({
                    "T": T,
                    "dp_found": dp["found"],
                    "ff_found": ff["found"],
                    "memo_size": dp["memo_size"],
                    "states_visited": dp["states_visited"],
                })
            memo_sizes.append(dp["memo_size"])
            states_visited_list.append(dp["states_visited"])
            dp_times.append(dp_time)
            ff_times.append(ff_time)

        per_n.append({
            "n": n,
            "samples": samples_per_n,
            "admissible": admissible,
            "agree": agree,
            "disagree": admissible - agree,
            "max_memo": max(memo_sizes) if memo_sizes else 0,
            "mean_memo": sum(memo_sizes) / max(len(memo_sizes), 1),
            "max_states": max(states_visited_list) if states_visited_list else 0,
            "mean_states": sum(states_visited_list) / max(len(states_visited_list), 1),
            "max_dp_time_sec": max(dp_times) if dp_times else 0,
            "max_ff_time_sec": max(ff_times) if ff_times else 0,
            "disagree_examples": disagree_examples,
        })
    return {
        "n_range": [n_min, n_max],
        "samples_per_n": samples_per_n,
        "p": p,
        "seed": seed,
        "time_budget_sec": time_budget_sec,
        "per_n": per_n,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n-min", type=int, default=10)
    parser.add_argument("--n-max", type=int, default=18)
    parser.add_argument("--samples", type=int, default=20)
    parser.add_argument("--p", type=float, default=0.5)
    parser.add_argument("--seed", type=int, default=20260525)
    parser.add_argument("--time-budget-sec", type=float, default=30.0)
    parser.add_argument("--out")
    parser.add_argument("--generator", choices=["random", "padded_skew"],
                        default="random")
    args = parser.parse_args()

    result = stress(
        n_min=args.n_min,
        n_max=args.n_max,
        samples_per_n=args.samples,
        p=args.p,
        seed=args.seed,
        time_budget_sec=args.time_budget_sec,
        generator=args.generator,
    )
    text = json.dumps(result, indent=2, default=str)
    print(text)
    if args.out:
        with open(args.out, "w") as f:
            f.write(text)


if __name__ == "__main__":
    main()
