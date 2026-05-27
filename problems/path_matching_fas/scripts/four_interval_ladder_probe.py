"""Size-8 / four-interval ladder probe at k>=8.

Tests whether V5 (P3, P3') extends to four-interval cyclic ladders, or
whether new fatality triggers appear at this size.

A four-interval ladder consists of:
  - 4 selected even-odd toggle blocks E_p, E_q, E_r, E_s;
  - their B-images form four adjacent-pair intervals
    I_0 = {a0, a0+1}, ..., I_3 = {a3, a3+1} with a0+1 < a1, etc.;
  - each block has two images, one in each of two distinct intervals;
  - the four (block, interval-pair) assignments together cover the
    "cyclic" pattern: blocks are arranged so the interval-pair edges
    form a 4-cycle in the interval graph.

Concretely, a candidate cyclic ladder has block-image pairs
  (I_0, I_1), (I_1, I_2), (I_2, I_3), (I_3, I_0).

Usage:
  uv run python scripts/four_interval_ladder_probe.py --k 9 \
    --pi <comma-separated-perm>
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from itertools import combinations, permutations
from typing import Sequence

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rectangle_detachability_probe import (  # noqa: E402
    even_adjacent_blocks,
    minimal_fatal_toggle_sets,
)


def four_interval_ladder_sets(k: int, pi: Sequence[int]) -> list[tuple[int, ...]]:
    """Enumerate size-8 four-interval ladder candidates."""
    blocks = even_adjacent_blocks(k)
    if len(blocks) < 4:
        return []
    ladders: set[tuple[int, ...]] = set()
    for quad in combinations(range(len(blocks)), 4):
        selected_blocks = [blocks[i] for i in quad]
        selected = tuple(sorted(sum(selected_blocks, ())))
        images = sorted({pi[i] for i in selected})
        if len(images) != 8:
            continue
        # Four intervals of size 2:
        # images[0,1], images[2,3], images[4,5], images[6,7]
        if (
            images[1] - images[0] != 1
            or images[3] - images[2] != 1
            or images[5] - images[4] != 1
            or images[7] - images[6] != 1
            or images[2] <= images[1]
            or images[4] <= images[3]
            or images[6] <= images[5]
        ):
            continue
        intervals = [
            {images[0], images[1]},
            {images[2], images[3]},
            {images[4], images[5]},
            {images[6], images[7]},
        ]
        # Each block's images must be in two distinct intervals, with
        # exactly one image per interval.
        block_image_pairs = []
        ok = True
        for block in selected_blocks:
            img = {pi[i] for i in block}
            if len(img) != 2:
                ok = False
                break
            in_which = [idx for idx, iv in enumerate(intervals) if img & iv]
            if len(in_which) != 2:
                ok = False
                break
            for idx in in_which:
                if len(img & intervals[idx]) != 1:
                    ok = False
                    break
            if not ok:
                break
            block_image_pairs.append(frozenset(in_which))
        if not ok:
            continue
        # For a "cyclic" four-interval ladder, the four block-pairs
        # should form a 4-cycle on the interval graph: each interval
        # appears in exactly two of the four block-pairs.
        interval_degree = [0] * 4
        for pair in block_image_pairs:
            for idx in pair:
                interval_degree[idx] += 1
        if interval_degree != [2, 2, 2, 2]:
            continue
        ladders.add(selected)
    return sorted(ladders)


def predict_four_interval_fatal(
    k: int,
    pi: Sequence[int],
    selected: Sequence[int],
) -> dict:
    """V5 criterion extended to four-interval ladders.

    Same triggers as V4/V5 for two/three intervals:
      (P3)  any filler image above the highest interval -> fatal;
      (P3') at odd k, lone unpaired filler index k-1 with image below
            the lowest interval -> fatal.
    """
    selected_set = set(selected)
    if len(selected_set) != 8:
        return {"prediction": "not_a_candidate", "reason": "size_not_8"}
    images = sorted({pi[i] for i in selected})
    if len(images) != 8:
        return {"prediction": "not_a_candidate", "reason": "image_size"}
    img_lo = images[0]
    img_hi = images[7]
    filler_indices = [i for i in range(k) if i not in selected_set]

    for fi in filler_indices:
        if pi[fi] > img_hi:
            return {"prediction": "fatal", "reason": "P3_image_above",
                    "filler": fi, "image": pi[fi]}

    if k % 2 == 1:
        lone = k - 1
        if lone in filler_indices and pi[lone] < img_lo:
            return {"prediction": "fatal",
                    "reason": "P3prime_lone_filler_image_below",
                    "filler": lone, "image": pi[lone]}

    return {"prediction": "detachable",
            "reason": "no_filler_image_above_and_no_lone_below"}


def construct_cyclic_four_interval(k: int) -> tuple[int, ...] | None:
    """Construct a representative cyclic four-interval ladder for k>=8.

    Use the cyclic shape:
      E_0 -> {1, 3}  (intervals I_0={1,2}, I_1={3,4})
      E_1 -> {4, 6}  (intervals I_1={3,4}, I_2={5,6})
      E_2 -> {5, 7}  (intervals I_2={5,6}, I_3={7,8})
      E_3 -> {2, 8}  (intervals I_0={1,2}, I_3={7,8})

    Then fillers (if any) get the remaining images.
    Returns a pairing pi or None if construction fails (e.g., k too small).
    """
    if k < 8:
        return None
    pi = [-1] * k
    # selected blocks: E_0..E_3 at indices (0,1),(2,3),(4,5),(6,7)
    pi[0] = 1
    pi[1] = 3
    pi[2] = 4
    pi[3] = 6
    pi[4] = 5
    pi[5] = 7
    pi[6] = 2
    pi[7] = 8
    # remaining indices 8..k-1 get the remaining images
    used = set(pi[:8])
    remaining_images = [v for v in range(k) if v not in used]
    for idx, v in enumerate(remaining_images):
        pi[8 + idx] = v
    return tuple(pi)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--k", type=int, default=9)
    parser.add_argument("--pi", type=str, default=None)
    args = parser.parse_args()

    if args.pi:
        pi = tuple(int(x) for x in args.pi.split(","))
    else:
        pi = construct_cyclic_four_interval(args.k)
        if pi is None:
            print(json.dumps({"error": "k too small"}, indent=2))
            return

    candidates = four_interval_ladder_sets(args.k, pi)
    minimal = minimal_fatal_toggle_sets(args.k, pi)
    size8_fatal = sorted(s for s in minimal if len(s) == 8)
    rows = []
    for cand in candidates:
        pred = predict_four_interval_fatal(args.k, pi, cand)
        is_truly_fatal = tuple(cand) in {tuple(s) for s in size8_fatal}
        rows.append({
            "candidate": list(cand),
            "prediction": pred,
            "truly_fatal": is_truly_fatal,
            "correct": (pred["prediction"] == "fatal") == is_truly_fatal,
        })
    print(json.dumps({
        "k": args.k,
        "pi": list(pi),
        "candidates": [list(c) for c in candidates],
        "true_size8_fatal": [list(s) for s in size8_fatal],
        "rows": rows,
    }, indent=2, default=list))


if __name__ == "__main__":
    main()
