"""D1 adversarial probe for sleeping-block.

Two complementary tests:

  (P1) depth-6 collision search on ONE_BLOCK_FAILURE_WITNESS (the
       template that broke visible-latent at depth 5).

  (P2) skew-composition: build a tournament composing two independent
       skew obstructions and run depth-5 collision search on it.

If either probe finds a sleeping-block extendability collision, the
candidate state is refuted and the workstream pivots to wake-1 or
beyond. Zero collisions in both is a stronger positive signal.

Usage:
  uv run python scripts/sleeping_block_d1_probe.py --mode depth6
  uv run python scripts/sleeping_block_d1_probe.py --mode compose
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from typing import Sequence

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sleeping_block_skew_sweep import SKEW_TEMPLATES, is_lfo_admissible  # noqa: E402
from wake_signature_probe import find_extendability_collision  # noqa: E402


Matrix = list[list[int]]


def skew_compose(T_left: Matrix, T_right: Matrix) -> Matrix:
    """Concatenate two skew tournaments with all left-to-right arcs forward.

    Vertex indexing: 0..n_l-1 from T_left, then n_l..n_l+n_r-1 from T_right.
    Every cross arc is left -> right. Within each block the original
    orientation is preserved.

    This is a natural "two-copy" tournament where each block carries its
    own skew obstruction. Extendability factors through the blocks: a
    valid LFO must place all of T_left vertices before all of T_right
    vertices (because every cross arc is forward and would otherwise be
    a backedge, polluting the score windows).
    """
    n_l = len(T_left)
    n_r = len(T_right)
    n = n_l + n_r
    out = [[0] * n for _ in range(n)]
    for u in range(n_l):
        for v in range(n_l):
            out[u][v] = T_left[u][v]
    for u in range(n_r):
        for v in range(n_r):
            out[n_l + u][n_l + v] = T_right[u][v]
    # Cross arcs: all left -> right
    for u in range(n_l):
        for v in range(n_r):
            out[u][n_l + v] = 1
    return out


def probe_depth6(timeout_sec: float | None = None) -> dict:
    """Depth-6 sleeping-block extendability collision search on the
    one_block template."""
    T = SKEW_TEMPLATES["one_block"]
    start = time.time()
    sleeping_collision = find_extendability_collision(
        T, depth=6, kind="sleeping", pruned=True,
    )
    elapsed_sleeping = time.time() - start

    start = time.time()
    visible_collision = find_extendability_collision(
        T, depth=6, kind="visible", pruned=True,
    )
    elapsed_visible = time.time() - start

    return {
        "probe": "depth6_one_block",
        "n": len(T),
        "depth": 6,
        "sleeping_collision_found": sleeping_collision is not None,
        "sleeping_collision": sleeping_collision,
        "elapsed_sleeping_sec": round(elapsed_sleeping, 1),
        "visible_collision_found": visible_collision is not None,
        "elapsed_visible_sec": round(elapsed_visible, 1),
    }


def probe_depth_template(template: str, depth: int) -> dict:
    """Depth-`depth` sleeping-block extendability collision search on
    the named skew template."""
    T = SKEW_TEMPLATES[template]
    start = time.time()
    sleeping_collision = find_extendability_collision(
        T, depth=depth, kind="sleeping", pruned=True,
    )
    elapsed_sleeping = time.time() - start

    start = time.time()
    visible_collision = find_extendability_collision(
        T, depth=depth, kind="visible", pruned=True,
    )
    elapsed_visible = time.time() - start

    return {
        "probe": f"depth{depth}_{template}",
        "n": len(T),
        "depth": depth,
        "sleeping_collision_found": sleeping_collision is not None,
        "sleeping_collision": sleeping_collision,
        "elapsed_sleeping_sec": round(elapsed_sleeping, 1),
        "visible_collision_found": visible_collision is not None,
        "elapsed_visible_sec": round(elapsed_visible, 1),
    }


def probe_composition() -> dict:
    """Skew composition of two `one_block` templates at depth 5."""
    T_left = SKEW_TEMPLATES["one_block"]
    T_right = SKEW_TEMPLATES["one_block"]
    T = skew_compose(T_left, T_right)
    n = len(T)
    if not is_lfo_admissible(T):
        return {
            "probe": "compose_one_block_x2",
            "n": n,
            "lfo_admissible": False,
        }

    start = time.time()
    sleeping_collision = find_extendability_collision(
        T, depth=5, kind="sleeping", pruned=True,
    )
    elapsed_sleeping = time.time() - start

    start = time.time()
    visible_collision = find_extendability_collision(
        T, depth=5, kind="visible", pruned=True,
    )
    elapsed_visible = time.time() - start

    return {
        "probe": "compose_one_block_x2",
        "n": n,
        "lfo_admissible": True,
        "depth": 5,
        "sleeping_collision_found": sleeping_collision is not None,
        "sleeping_collision": sleeping_collision,
        "visible_collision_found": visible_collision is not None,
        "elapsed_sleeping_sec": round(elapsed_sleeping, 1),
        "elapsed_visible_sec": round(elapsed_visible, 1),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mode",
        choices=["depth6", "compose", "both", "depth", "template-depth"],
        default="both",
    )
    parser.add_argument("--depth", type=int, default=7)
    parser.add_argument("--template", default="one_block",
                        choices=list(SKEW_TEMPLATES.keys()))
    parser.add_argument("--out")
    args = parser.parse_args()

    results = []
    if args.mode in ("depth6", "both"):
        results.append(probe_depth6())
    if args.mode in ("compose", "both"):
        results.append(probe_composition())
    if args.mode == "depth":
        results.append(probe_depth_template("one_block", args.depth))
    if args.mode == "template-depth":
        results.append(probe_depth_template(args.template, args.depth))

    text = json.dumps(results, indent=2, default=str)
    print(text)
    if args.out:
        with open(args.out, "w") as f:
            f.write(text)


if __name__ == "__main__":
    main()
