"""Sleeping-block state-space size growth experiment.

To test whether a sleeping-block DP is plausibly polynomial, count
distinct sleeping-block signatures across full reachable LFO prefix
states (every cut, not just depth-bounded prefixes) on a family of
random tournaments at varying n.

For each n in a chosen range:
  - generate `samples` random tournaments with edge probability p;
  - for each, count distinct sleeping-block signatures across full
    DFS-reachable LFO state space, capped by a time-or-state budget;
  - record the ratio (distinct signatures) / (surviving prefixes).

If the absolute count grows polynomially in n, sleeping-block is a
viable bounded state. If it grows like a! or 2^n, even an extension-
complete sleeping-block won't give a polynomial DP.

For computational tractability, we cap the DFS expansion at
`state_budget` and report whether the budget was hit.

Usage:
  uv run python scripts/sleeping_state_size_growth.py \
    --n-min 8 --n-max 12 --samples 10 --p 0.5 --seed 1
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

from ff_signature_probe import (  # noqa: E402
    _add_flexible_vertex,
    valid_prefix_state_ff,
    visible_latent_signature,
)
from lfo_forced_flexible import _iter_bits  # noqa: E402
from lfo_score_window import hall_interval_ok  # noqa: E402
from sleeping_block_probe import sleeping_block_signature  # noqa: E402
from wake_signature_probe import survives_pruning  # noqa: E402


Matrix = list[list[int]]


def random_tournament(n: int, p: float, rng: random.Random) -> Matrix:
    """Generate a random tournament. Each arc i->j (i<j) is present
    independently with probability p; otherwise j->i."""
    T = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            if rng.random() < p:
                T[i][j] = 1
            else:
                T[j][i] = 1
    return T


def count_reachable_state_signatures(
    T: Matrix,
    state_budget: int = 50000,
    time_budget_sec: float = 60.0,
) -> dict:
    """Count distinct visible-latent and sleeping-block signatures over
    all DFS-reachable surviving LFO states.

    DFS rooted at the initial state, expanding only valid placements
    that survive FF pruning. Each state contributes to both counts.
    Returns counts plus a flag for whether the budget cut off the search.
    """
    n = len(T)
    initial = valid_prefix_state_ff(T, ())
    if initial is None:
        return {
            "lfo_admissible": False,
            "visible_signatures": 0,
            "sleeping_signatures": 0,
            "states_visited": 0,
            "budget_hit": False,
        }

    visible_sigs: set = set()
    sleeping_sigs: set = set()

    initial_prefix_mask, initial_degree, initial_parent, flex_outmask, windows = initial
    all_mask = (1 << n) - 1

    if not hall_interval_ok(all_mask, 0, windows, n):
        return {
            "lfo_admissible": False,
            "visible_signatures": 0,
            "sleeping_signatures": 0,
            "states_visited": 0,
            "budget_hit": False,
        }

    # The DFS-tree of LFO prefixes can have many states with the same
    # (prefix_mask, sleeping_sig) — we record state by (prefix_mask, deg,
    # canonical_parent_partition) to avoid revisiting.
    visited: set = set()
    states_visited = 0
    budget_hit = False
    start = time.time()

    stack = [(0, initial_prefix_mask, initial_degree, initial_parent)]
    while stack:
        if time.time() - start > time_budget_sec or states_visited > state_budget:
            budget_hit = True
            break
        pos, prefix_mask, degree, parent = stack.pop()

        state_key = (prefix_mask, tuple(degree), tuple(parent))
        if state_key in visited:
            continue
        visited.add(state_key)
        states_visited += 1

        # Filter: state must survive pruning to be a real DP state.
        cur_state = (prefix_mask, degree, parent, flex_outmask, windows)
        if not survives_pruning(cur_state, pos, n):
            continue

        v_sig = visible_latent_signature(
            pos, prefix_mask, degree, parent, flex_outmask, windows
        )
        s_sig = sleeping_block_signature(
            pos, prefix_mask, degree, parent, flex_outmask, windows
        )
        visible_sigs.add(v_sig)
        sleeping_sigs.add(s_sig)

        if prefix_mask == all_mask:
            continue
        remaining = all_mask ^ prefix_mask
        for x in _iter_bits(remaining):
            lo, hi = windows[x]
            if not (lo <= pos <= hi):
                continue
            nxt = _add_flexible_vertex(flex_outmask, prefix_mask, degree, parent, x)
            if nxt is None:
                continue
            child_deg, child_par = nxt
            stack.append((pos + 1, prefix_mask | (1 << x), child_deg, child_par))

    return {
        "lfo_admissible": True,
        "visible_signatures": len(visible_sigs),
        "sleeping_signatures": len(sleeping_sigs),
        "states_visited": states_visited,
        "budget_hit": budget_hit,
        "elapsed_sec": round(time.time() - start, 2),
    }


def sweep(
    n_min: int,
    n_max: int,
    samples: int,
    p: float,
    seed: int,
    state_budget: int,
    time_budget_sec: float,
) -> dict:
    rng = random.Random(seed)
    per_n: dict[int, dict] = {}
    for n in range(n_min, n_max + 1):
        admissible = 0
        v_sigs_total = 0
        s_sigs_total = 0
        states_total = 0
        budget_hits = 0
        per_sample = []
        for s in range(samples):
            T = random_tournament(n, p, rng)
            out = count_reachable_state_signatures(
                T, state_budget=state_budget, time_budget_sec=time_budget_sec,
            )
            if out["lfo_admissible"]:
                admissible += 1
                v_sigs_total += out["visible_signatures"]
                s_sigs_total += out["sleeping_signatures"]
                states_total += out["states_visited"]
                if out.get("budget_hit"):
                    budget_hits += 1
                per_sample.append({
                    "visible": out["visible_signatures"],
                    "sleeping": out["sleeping_signatures"],
                    "states": out["states_visited"],
                    "budget_hit": out.get("budget_hit", False),
                })
        per_n[n] = {
            "samples": samples,
            "admissible": admissible,
            "budget_hits": budget_hits,
            "mean_visible_sigs": v_sigs_total / max(admissible, 1),
            "mean_sleeping_sigs": s_sigs_total / max(admissible, 1),
            "mean_states_visited": states_total / max(admissible, 1),
            "per_sample": per_sample,
        }
    return {
        "n_range": [n_min, n_max],
        "samples_per_n": samples,
        "p": p,
        "seed": seed,
        "state_budget": state_budget,
        "time_budget_sec": time_budget_sec,
        "per_n": per_n,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n-min", type=int, default=8)
    parser.add_argument("--n-max", type=int, default=12)
    parser.add_argument("--samples", type=int, default=5)
    parser.add_argument("--p", type=float, default=0.5)
    parser.add_argument("--seed", type=int, default=20260524)
    parser.add_argument("--state-budget", type=int, default=20000)
    parser.add_argument("--time-budget-sec", type=float, default=30.0)
    parser.add_argument("--out", help="JSON output path")
    args = parser.parse_args()

    result = sweep(
        n_min=args.n_min,
        n_max=args.n_max,
        samples=args.samples,
        p=args.p,
        seed=args.seed,
        state_budget=args.state_budget,
        time_budget_sec=args.time_budget_sec,
    )
    text = json.dumps(result, indent=2)
    print(text)
    if args.out:
        with open(args.out, "w") as f:
            f.write(text)


if __name__ == "__main__":
    main()
