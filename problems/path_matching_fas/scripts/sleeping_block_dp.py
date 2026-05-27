"""Polynomial Path-FAS solver using sleeping-block as DP state.

Implements a memoized DFS over LFO prefix states, keyed on the
sleeping-block signature.  If sleeping-block is extension-complete
(empirically supported by Section 12.5 + Section 13.7 transition
certificate) and the number of distinct sleeping-block signatures is
polynomial in n (open), this solver runs in polynomial time.

The decision returned matches the brute / FF-pruned solver on every
instance where sleeping-block is extension-complete.  When it does not,
the brute / FF solver is the ground truth.

Two metrics drive the bounded-compression question:

  (M1) `memo_size`: number of distinct sleeping-block signatures seen
       during the run.
  (M2) `states_visited`: total recursion calls including memo hits.

If M1/M2 grows polynomially in n on the skew family, this is the
strongest empirical signal that sleeping-block gives a polynomial DP.

Usage:
  uv run python scripts/sleeping_block_dp.py --T <json>
  uv run python scripts/sleeping_block_dp.py --benchmark
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from typing import Sequence

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ff_signature_probe import (  # noqa: E402
    _add_flexible_vertex,
    valid_prefix_state_ff,
)
from lfo_forced_flexible import _iter_bits  # noqa: E402
from lfo_score_window import hall_interval_ok  # noqa: E402
from sleeping_block_probe import sleeping_block_signature  # noqa: E402
from wake_signature_probe import survives_pruning  # noqa: E402


Matrix = Sequence[Sequence[int]]


def sleeping_block_dp_decide(
    T: Matrix,
    time_budget_sec: float | None = None,
) -> dict:
    """Decide whether T has a valid LFO using a memoized sleeping-block DP.

    Returns dict with:
      - "found": bool, True iff a valid LFO exists (modulo the
        sleeping-block extension-equivalence hypothesis).
      - "memo_size": distinct sleeping-block signatures memoized.
      - "states_visited": total recursion calls.
      - "elapsed_sec": wall time.
      - "budget_hit": True if time_budget_sec reached.
    """
    n = len(T)
    initial = valid_prefix_state_ff(T, ())
    if initial is None:
        return {
            "found": False, "reason": "no_initial_state",
            "memo_size": 0, "states_visited": 0, "elapsed_sec": 0.0,
            "budget_hit": False,
        }

    prefix_mask0, degree0, parent0, flex_outmask, windows = initial
    all_mask = (1 << n) - 1
    if not hall_interval_ok(all_mask, 0, windows, n):
        return {
            "found": False, "reason": "initial_hall_fail",
            "memo_size": 0, "states_visited": 0, "elapsed_sec": 0.0,
            "budget_hit": False,
        }

    memo: dict[tuple, bool] = {}
    states_visited = 0
    start = time.time()
    budget_hit = False

    def rec(pos: int, prefix_mask: int, degree, parent) -> bool:
        nonlocal states_visited, budget_hit
        if budget_hit:
            return False
        if time_budget_sec is not None and time.time() - start > time_budget_sec:
            budget_hit = True
            return False
        states_visited += 1
        if prefix_mask == all_mask:
            return True
        state = (prefix_mask, degree, parent, flex_outmask, windows)
        if not survives_pruning(state, pos, n):
            return False
        sig = sleeping_block_signature(
            pos, prefix_mask, degree, parent, flex_outmask, windows
        )
        if sig in memo:
            return memo[sig]
        # Lock in a tentative False to break ties on revisits; correct
        # at end.  (Path-FAS DAG has no cycles in the search graph since
        # placing a vertex strictly grows prefix_mask, so this is
        # actually unnecessary; but cheap.)
        memo[sig] = False
        remaining = all_mask ^ prefix_mask
        candidates = sorted(
            [v for v in _iter_bits(remaining)
             if windows[v][0] <= pos <= windows[v][1]],
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
            child_deg, child_par = nxt
            if rec(pos + 1, prefix_mask | (1 << x), child_deg, child_par):
                memo[sig] = True
                return True
        return False

    found = rec(0, prefix_mask0, degree0, parent0)
    return {
        "found": found,
        "memo_size": len(memo),
        "states_visited": states_visited,
        "elapsed_sec": round(time.time() - start, 3),
        "budget_hit": budget_hit,
    }


def benchmark_skew_growth(
    max_padding: int = 6,
    time_budget_sec: float = 60.0,
) -> dict:
    """Benchmark the DP on padded skew templates at growing n."""
    from sleeping_block_skew_sweep import SKEW_TEMPLATES, is_lfo_admissible
    from wake_signature_probe import _insert_transitive_padding_vertex

    results = []
    for tmpl_name, base_T in SKEW_TEMPLATES.items():
        T = [row[:] for row in base_T]
        for pad in range(max_padding + 1):
            n = len(T)
            if not is_lfo_admissible(T):
                results.append({
                    "template": tmpl_name,
                    "padding": pad,
                    "n": n,
                    "lfo_admissible": False,
                })
            else:
                out = sleeping_block_dp_decide(T, time_budget_sec=time_budget_sec)
                results.append({
                    "template": tmpl_name,
                    "padding": pad,
                    "n": n,
                    "lfo_admissible": True,
                    **{k: v for k, v in out.items() if k != "reason"},
                })
                if out.get("budget_hit"):
                    break
            T = _insert_transitive_padding_vertex(T, min(11, len(T)))
    return {
        "max_padding": max_padding,
        "time_budget_sec": time_budget_sec,
        "results": results,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--T", help="Tournament as JSON matrix")
    parser.add_argument("--benchmark", action="store_true",
                        help="Run the padded skew benchmark")
    parser.add_argument("--max-padding", type=int, default=6)
    parser.add_argument("--time-budget-sec", type=float, default=60.0)
    parser.add_argument("--out")
    args = parser.parse_args()

    if args.benchmark:
        result = benchmark_skew_growth(
            max_padding=args.max_padding,
            time_budget_sec=args.time_budget_sec,
        )
    else:
        if not args.T:
            parser.error("either --T <json> or --benchmark is required")
        T = json.loads(args.T)
        result = sleeping_block_dp_decide(T, time_budget_sec=args.time_budget_sec)

    text = json.dumps(result, indent=2, default=str)
    print(text)
    if args.out:
        with open(args.out, "w") as f:
            f.write(text)


if __name__ == "__main__":
    main()
