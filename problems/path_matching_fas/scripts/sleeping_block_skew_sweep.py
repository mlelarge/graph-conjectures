"""Skew-family extension-completeness sweep for sleeping-block.

The visible-latent signature was refuted by the ONE_BLOCK_FAILURE_WITNESS
counterexample (Section 10.4 of exchange_proof_draft.md). The new
candidate DP state is the sleeping-block signature. This script runs the
first decisive empirical experiment on whether sleeping-block survives
the same regime that killed visible-latent.

Two questions:

  (Q1) Does sleeping-block have any extendability collision on a
       sample of skew-like n=12 tournaments? Any single positive
       answer kills sleeping-block as a DP state. Zero across a broad
       sample is a positive empirical signal.

  (Q2) How does the sleeping-block state-space size grow? If it
       remains polynomial in n across the sweep, a poly DP is
       plausible; if it grows exponentially, even an
       extension-complete sleeping-block won't give a poly algorithm.

The "skew family" is built by perturbing the three known skew witnesses
(ONE_BLOCK_FAILURE_WITNESS, SKEW_INDUCTION_WITNESS, WAKE1_FAILURE_WITNESS)
under arc flips that keep the score-window structure non-trivial.

Usage:
  uv run python scripts/sleeping_block_skew_sweep.py --samples 100 --depth 5
"""
from __future__ import annotations

import argparse
import json
import os
import random
import sys
import time
from collections import Counter, defaultdict
from typing import Sequence

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ff_signature_probe import (  # noqa: E402
    has_completion_ff,
    prefixes,
    valid_prefix_state_ff,
    visible_latent_signature,
)
from lfo_score_window import hall_interval_ok, score_windows  # noqa: E402
from sleeping_block_probe import sleeping_block_signature  # noqa: E402
from wake_signature_probe import (  # noqa: E402
    find_extendability_collision,
    survives_pruning,
)


Matrix = list[list[int]]


SKEW_TEMPLATES: dict[str, Matrix] = {
    "one_block": [
        [0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1],
        [0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1],
        [1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1],
        [0, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1],
        [0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 1],
        [0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1],
        [0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1],
        [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1],
        [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1],
        [1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    ],
    "skew_induction": [
        [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
        [0, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1],
        [0, 0, 0, 1, 1, 1, 1, 0, 1, 1, 1, 0],
        [0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0],
        [0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 1, 1],
        [0, 1, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1],
        [0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1],
        [0, 0, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1],
        [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 1],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0],
    ],
    "wake1_failure": [
        [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
        [0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [0, 0, 0, 0, 1, 1, 1, 1, 0, 1, 1, 1],
        [0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1],
        [0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1],
        [0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1],
        [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1],
        [0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 1, 1],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
    ],
}


def perturb(T: Matrix, k_flips: int, rng: random.Random) -> Matrix:
    """Apply k random arc flips to T.

    Each flip picks a pair (i,j) with i<j and toggles T[i][j], T[j][i].
    Result remains a tournament.
    """
    n = len(T)
    M = [row[:] for row in T]
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    chosen = rng.sample(pairs, k=k_flips)
    for i, j in chosen:
        M[i][j], M[j][i] = M[j][i], M[i][j]
    return M


def is_lfo_admissible(T: Matrix) -> bool:
    """The tournament passes initial Hall + has a valid (initial) state.

    A tournament that fails initial Hall has no LFO; we filter those
    out because they give no non-trivial prefix-state sweep.
    """
    n = len(T)
    state = valid_prefix_state_ff(T, ())
    if state is None:
        return False
    pm, deg, par, flex, win = state
    if not hall_interval_ok((1 << n) - 1, 0, win, n):
        return False
    return True


def signature_class_counts(
    T: Matrix,
    depth: int,
    sigfun_name: str,
) -> dict:
    """Count distinct signatures of `sigfun_name` over depth-bounded
    surviving prefixes."""
    sigfun = {
        "visible": visible_latent_signature,
        "sleeping": sleeping_block_signature,
    }[sigfun_name]

    sig_count: Counter = Counter()
    n = len(T)
    surviving = 0
    for prefix in prefixes(n, depth):
        state = valid_prefix_state_ff(T, prefix)
        if state is None:
            continue
        pos = len(prefix)
        if not survives_pruning(state, pos, n):
            continue
        surviving += 1
        prefix_mask, deg, par, flex, win = state
        sig = sigfun(pos, prefix_mask, deg, par, flex, win)
        sig_count[sig] += 1
    return {
        "surviving_prefixes": surviving,
        "distinct_signatures": len(sig_count),
    }


def sweep(
    n_samples: int,
    depth: int,
    seed: int,
    flips_range: tuple[int, int],
    template_names: Sequence[str] | None = None,
) -> dict:
    rng = random.Random(seed)
    if template_names is None:
        template_names = list(SKEW_TEMPLATES.keys())

    sleeping_collisions: list[dict] = []
    visible_collisions: list[dict] = []
    admissible = 0
    inadmissible = 0
    per_template = defaultdict(lambda: {
        "tried": 0, "admissible": 0,
        "sleeping_collisions": 0, "visible_collisions": 0,
        "visible_classes_sum": 0, "sleeping_classes_sum": 0,
        "surviving_prefixes_sum": 0,
    })

    start = time.time()
    for sample_idx in range(n_samples):
        template_name = rng.choice(list(template_names))
        template = SKEW_TEMPLATES[template_name]
        k = rng.randint(*flips_range)
        T = perturb(template, k, rng)
        per_template[template_name]["tried"] += 1

        if not is_lfo_admissible(T):
            inadmissible += 1
            continue
        admissible += 1
        per_template[template_name]["admissible"] += 1

        # Sleeping-block collision check.
        sleeping_col = find_extendability_collision(
            T, depth=depth, kind="sleeping", pruned=True,
        )
        # Visible-latent collision check (control).
        visible_col = find_extendability_collision(
            T, depth=depth, kind="visible", pruned=True,
        )
        # State-space sizes.
        v_count = signature_class_counts(T, depth, "visible")
        s_count = signature_class_counts(T, depth, "sleeping")

        per_template[template_name]["visible_classes_sum"] += v_count["distinct_signatures"]
        per_template[template_name]["sleeping_classes_sum"] += s_count["distinct_signatures"]
        per_template[template_name]["surviving_prefixes_sum"] += s_count["surviving_prefixes"]

        if sleeping_col is not None:
            per_template[template_name]["sleeping_collisions"] += 1
            sleeping_collisions.append({
                "sample_idx": sample_idx,
                "template": template_name,
                "k_flips": k,
                "T": T,
                "collision": {
                    "state_a": sleeping_col["state_a"],
                    "state_b": sleeping_col["state_b"],
                    "class_size": sleeping_col["signature_class_size"],
                },
            })
        if visible_col is not None:
            per_template[template_name]["visible_collisions"] += 1
            visible_collisions.append({
                "sample_idx": sample_idx,
                "template": template_name,
                "k_flips": k,
            })

    elapsed = time.time() - start
    return {
        "n_samples": n_samples,
        "depth": depth,
        "seed": seed,
        "flips_range": list(flips_range),
        "templates": list(template_names),
        "admissible": admissible,
        "inadmissible": inadmissible,
        "total_sleeping_collisions": len(sleeping_collisions),
        "total_visible_collisions": len(visible_collisions),
        "per_template": {k: dict(v) for k, v in per_template.items()},
        "sleeping_collision_examples": sleeping_collisions[:3],
        "elapsed_sec": round(elapsed, 2),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--samples", type=int, default=100)
    parser.add_argument("--depth", type=int, default=5)
    parser.add_argument("--seed", type=int, default=20260524)
    parser.add_argument("--flips-min", type=int, default=0)
    parser.add_argument("--flips-max", type=int, default=4)
    parser.add_argument("--templates", nargs="*",
                        choices=list(SKEW_TEMPLATES.keys()))
    parser.add_argument("--out", help="write JSON output to this path")
    args = parser.parse_args()

    result = sweep(
        n_samples=args.samples,
        depth=args.depth,
        seed=args.seed,
        flips_range=(args.flips_min, args.flips_max),
        template_names=args.templates,
    )
    text = json.dumps(result, indent=2, default=str)
    print(text)
    if args.out:
        with open(args.out, "w") as f:
            f.write(text)


if __name__ == "__main__":
    main()
