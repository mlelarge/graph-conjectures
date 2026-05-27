"""Adversarial probe for the sleeping-block state space bound.

Construct candidate tournaments designed to blow up sleeping-block
state size:

  (P1) cut-isolated sum of k copies of a small skew witness. If
       sleeping-block state space scales as 2^k or k! across copies,
       memo grows super-polynomially. If it stays polynomial in n=block*k,
       the cut-isolated construction does not refute compression.

  (P2) skew_compose chains: concatenate multiple skew templates
       side-by-side (all cross-arcs forward). Each block adds its own
       potential F_i partition entropy.

Run the sleeping-block DP and report memo / state count growth.

Usage:
  uv run python scripts/sleeping_dp_adversarial.py --mode cut_isolated --k-max 5
  uv run python scripts/sleeping_dp_adversarial.py --mode skew_chain --k-max 4
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from typing import Sequence

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pending_state_probe import (  # noqa: E402
    COMPONENT_PREFIX_SET, COMPONENT_WITNESS_T, cut_isolated_sum,
)
from sleeping_block_dp import sleeping_block_dp_decide  # noqa: E402
from sleeping_block_d1_probe import skew_compose  # noqa: E402
from sleeping_block_skew_sweep import SKEW_TEMPLATES, is_lfo_admissible  # noqa: E402


Matrix = list[list[int]]


def chain_skew(name: str, k: int) -> Matrix:
    """Skew-compose k copies of the named template."""
    T = SKEW_TEMPLATES[name]
    out = T
    for _ in range(k - 1):
        out = skew_compose(out, T)
    return out


def probe_cut_isolated(k_max: int, time_budget_sec: float) -> list[dict]:
    results = []
    for k in range(1, k_max + 1):
        T = cut_isolated_sum(COMPONENT_WITNESS_T, COMPONENT_PREFIX_SET, k)
        n = len(T)
        admissible = is_lfo_admissible(T)
        if not admissible:
            results.append({"probe": "cut_isolated", "k": k, "n": n,
                            "lfo_admissible": False})
            continue
        out = sleeping_block_dp_decide(T, time_budget_sec=time_budget_sec)
        results.append({
            "probe": "cut_isolated", "k": k, "n": n,
            "lfo_admissible": True,
            **{kk: v for kk, v in out.items() if kk != "reason"},
        })
        if out.get("budget_hit"):
            break
    return results


def probe_skew_chain(template: str, k_max: int, time_budget_sec: float) -> list[dict]:
    results = []
    for k in range(1, k_max + 1):
        T = chain_skew(template, k)
        n = len(T)
        admissible = is_lfo_admissible(T)
        if not admissible:
            results.append({"probe": f"skew_chain_{template}", "k": k, "n": n,
                            "lfo_admissible": False})
            continue
        out = sleeping_block_dp_decide(T, time_budget_sec=time_budget_sec)
        results.append({
            "probe": f"skew_chain_{template}", "k": k, "n": n,
            "lfo_admissible": True,
            **{kk: v for kk, v in out.items() if kk != "reason"},
        })
        if out.get("budget_hit"):
            break
    return results


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode",
                        choices=["cut_isolated", "skew_chain", "both"],
                        default="both")
    parser.add_argument("--template", default="one_block",
                        choices=list(SKEW_TEMPLATES.keys()))
    parser.add_argument("--k-max", type=int, default=5)
    parser.add_argument("--time-budget-sec", type=float, default=120.0)
    parser.add_argument("--out")
    args = parser.parse_args()

    results = []
    if args.mode in ("cut_isolated", "both"):
        results.extend(probe_cut_isolated(args.k_max, args.time_budget_sec))
    if args.mode in ("skew_chain", "both"):
        results.extend(probe_skew_chain(args.template, args.k_max,
                                        args.time_budget_sec))

    text = json.dumps(results, indent=2, default=str)
    print(text)
    if args.out:
        with open(args.out, "w") as f:
            f.write(text)


if __name__ == "__main__":
    main()
