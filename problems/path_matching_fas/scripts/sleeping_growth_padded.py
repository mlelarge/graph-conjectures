"""Growth of sleeping-block state space along the padded skew family.

Pad each skew template with transitive vertices (which raise n by 1
without changing the underlying obstruction structure). Measure the
distinct sleeping-block signature count at each padding level.

If sleeping-block state space grows polynomially in n, the data should
fit a low-degree polynomial. Exponential growth would suggest
sleeping-block alone is not a viable DP state for poly Path-FAS.

Usage:
  uv run python scripts/sleeping_growth_padded.py --max-pad 6
"""
from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sleeping_block_skew_sweep import SKEW_TEMPLATES, is_lfo_admissible  # noqa: E402
from sleeping_state_size_growth import count_reachable_state_signatures  # noqa: E402
from wake_signature_probe import _insert_transitive_padding_vertex  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-pad", type=int, default=4)
    parser.add_argument("--pad-position", type=int, default=11)
    parser.add_argument("--state-budget", type=int, default=200000)
    parser.add_argument("--time-budget-sec", type=float, default=120.0)
    parser.add_argument("--out")
    args = parser.parse_args()

    results = []
    for tmpl_name, T in SKEW_TEMPLATES.items():
        current = [row[:] for row in T]
        for pad in range(0, args.max_pad + 1):
            n = len(current)
            if not is_lfo_admissible(current):
                results.append({
                    "template": tmpl_name,
                    "padding": pad,
                    "n": n,
                    "lfo_admissible": False,
                })
            else:
                out = count_reachable_state_signatures(
                    current,
                    state_budget=args.state_budget,
                    time_budget_sec=args.time_budget_sec,
                )
                results.append({
                    "template": tmpl_name,
                    "padding": pad,
                    "n": n,
                    "lfo_admissible": True,
                    "states_visited": out["states_visited"],
                    "visible_signatures": out["visible_signatures"],
                    "sleeping_signatures": out["sleeping_signatures"],
                    "budget_hit": out["budget_hit"],
                    "elapsed_sec": out.get("elapsed_sec", -1),
                })
                if out.get("budget_hit"):
                    # Don't keep growing; data unreliable past this point.
                    break
            current = _insert_transitive_padding_vertex(
                current, min(args.pad_position, len(current))
            )

    summary = {
        "templates": list(SKEW_TEMPLATES.keys()),
        "max_pad": args.max_pad,
        "pad_position": args.pad_position,
        "state_budget": args.state_budget,
        "time_budget_sec": args.time_budget_sec,
        "results": results,
    }
    text = json.dumps(summary, indent=2)
    print(text)
    if args.out:
        with open(args.out, "w") as f:
            f.write(text)


if __name__ == "__main__":
    main()
