"""Measure full reachable sleeping-block state-space size on the skew
family.

For each skew template and a few perturbations, count distinct
sleeping-block / visible-latent signatures across the FULL DFS-reachable
LFO state space (not depth-bounded). This shows whether sleeping-block
state-space size is small in absolute terms at n=12.

For a polynomial DP using sleeping-block as state, the state space must
be polynomial in n. At n=12, polynomial means roughly 10^2 to 10^4
states; exponential means 10^5+.

Usage:
  uv run python scripts/sleeping_full_state_space.py
"""
from __future__ import annotations

import argparse
import json
import os
import random
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sleeping_block_skew_sweep import (  # noqa: E402
    SKEW_TEMPLATES, is_lfo_admissible, perturb,
)
from sleeping_state_size_growth import count_reachable_state_signatures  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--perturbations", type=int, default=5)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--state-budget", type=int, default=200000)
    parser.add_argument("--time-budget-sec", type=float, default=120.0)
    parser.add_argument("--out")
    args = parser.parse_args()

    rng = random.Random(args.seed)
    results = []

    for tmpl_name, T in SKEW_TEMPLATES.items():
        # Unperturbed
        if is_lfo_admissible(T):
            out = count_reachable_state_signatures(
                T, state_budget=args.state_budget,
                time_budget_sec=args.time_budget_sec,
            )
            results.append({
                "template": tmpl_name,
                "k_flips": 0,
                "lfo_admissible": True,
                "states_visited": out["states_visited"],
                "visible_signatures": out["visible_signatures"],
                "sleeping_signatures": out["sleeping_signatures"],
                "budget_hit": out["budget_hit"],
                "elapsed_sec": out.get("elapsed_sec", -1),
            })
        else:
            results.append({
                "template": tmpl_name,
                "k_flips": 0,
                "lfo_admissible": False,
            })

        # k perturbations
        attempts = 0
        added = 0
        while added < args.perturbations and attempts < args.perturbations * 10:
            attempts += 1
            k = rng.randint(1, 3)
            T_pert = perturb(T, k, rng)
            if not is_lfo_admissible(T_pert):
                continue
            out = count_reachable_state_signatures(
                T_pert, state_budget=args.state_budget,
                time_budget_sec=args.time_budget_sec,
            )
            results.append({
                "template": tmpl_name,
                "k_flips": k,
                "lfo_admissible": True,
                "states_visited": out["states_visited"],
                "visible_signatures": out["visible_signatures"],
                "sleeping_signatures": out["sleeping_signatures"],
                "budget_hit": out["budget_hit"],
                "elapsed_sec": out.get("elapsed_sec", -1),
            })
            added += 1

    summary = {
        "templates": list(SKEW_TEMPLATES.keys()),
        "perturbations_per_template": args.perturbations,
        "state_budget": args.state_budget,
        "time_budget_sec": args.time_budget_sec,
        "results": results,
    }
    print(json.dumps(summary, indent=2))
    if args.out:
        with open(args.out, "w") as f:
            json.dump(summary, f, indent=2)


if __name__ == "__main__":
    main()
