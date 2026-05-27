"""Three-interval (size-6) ladder generator and detection.

Section 27.5 of exchange_proof_draft.md proposes that fatal ladders
generalize from size-4 (two-interval) to size-2m (m+1-interval).

This module implements the size-6 (three-interval) case.

A three-interval ladder candidate S consists of:
  - three even-odd toggle blocks E_p, E_q, E_r selected;
  - their union of B-images forms three pairwise-adjacent intervals
    of size 2 each:  {a, a+1}, {b, b+1}, {c, c+1}  with  a+1 < b
    and b+1 < c;
  - each block has exactly two images, each in a different interval;
  - the three (block, interval-pair) assignments cover all three
    pairs out of the three intervals (the cyclic alternating structure).

The user's k=7 example pi=(5,4,6,1,3,2,0) has S={0,1,2,3,4,5} with
  E_0=(0,1) -> {5,4} in intervals {3,4} and {5,6};
  E_1=(2,3) -> {6,1} in intervals {1,2} and {5,6};
  E_2=(4,5) -> {3,2} in intervals {1,2} and {3,4}.

Usage:
  uv run python scripts/three_interval_ladder_probe.py --k 7
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


def three_interval_ladder_sets(k: int, pi: Sequence[int]) -> list[tuple[int, ...]]:
    """Three-interval (size-6) ladder candidates.

    Three pairwise-adjacent B-intervals of size 2 each, three selected
    even-odd toggle blocks, with each block having one image in each
    of two distinct intervals AND all three interval-pairs covered.
    """
    blocks = even_adjacent_blocks(k)
    if len(blocks) < 3:
        return []
    ladders: set[tuple[int, ...]] = set()
    for triple in combinations(range(len(blocks)), 3):
        block_a, block_b, block_c = (blocks[i] for i in triple)
        selected = tuple(sorted(block_a + block_b + block_c))
        images = sorted({pi[i] for i in selected})
        if len(images) != 6:
            continue
        # Need three intervals of size 2:  images = {a,a+1, b,b+1, c,c+1}
        # with a+1<b, b+1<c.
        if (
            images[1] - images[0] != 1
            or images[3] - images[2] != 1
            or images[5] - images[4] != 1
            or images[2] <= images[1]
            or images[4] <= images[3]
        ):
            continue
        intervals = [
            {images[0], images[1]},
            {images[2], images[3]},
            {images[4], images[5]},
        ]
        # Each block's images must be in two distinct intervals.
        block_image_pair = []
        ok = True
        for block in (block_a, block_b, block_c):
            img = {pi[i] for i in block}
            in_which = [idx for idx, iv in enumerate(intervals) if img & iv]
            if len(in_which) != 2 or len(img) != 2:
                ok = False
                break
            # Each block must hit exactly one image in each of its two intervals.
            for idx in in_which:
                if len(img & intervals[idx]) != 1:
                    ok = False
                    break
            if not ok:
                break
            block_image_pair.append(frozenset(in_which))
        if not ok:
            continue
        # The three (block, interval-pair) assignments must cover all
        # three pairs out of three intervals (cyclic structure).
        if len(set(block_image_pair)) == 3:
            ladders.add(selected)
    return sorted(ladders)


def predict_three_interval_fatal(
    k: int,
    pi: Sequence[int],
    selected: Sequence[int],
) -> dict:
    """V5: extend V4 criterion to three-interval ladders.

      (P3)  some filler image > c+1 (above the high interval) -> fatal.
      (P3') at odd k, the lone unpaired filler index k-1 has image < a
            (below the low interval) -> fatal.
      otherwise -> detachable.
    """
    selected_set = set(selected)
    if len(selected_set) != 6:
        return {"prediction": "not_a_candidate", "reason": "size_not_6"}
    images = sorted({pi[i] for i in selected})
    if (
        len(images) != 6
        or images[1] - images[0] != 1
        or images[3] - images[2] != 1
        or images[5] - images[4] != 1
        or images[2] <= images[1]
        or images[4] <= images[3]
    ):
        return {"prediction": "not_a_candidate", "reason": "not_three_intervals"}
    img_lo = images[0]
    img_hi = images[5]
    filler_indices = [i for i in range(k) if i not in selected_set]

    # P3: filler image above high interval.
    for fi in filler_indices:
        if pi[fi] > img_hi:
            return {"prediction": "fatal", "reason": "P3_image_above",
                    "filler": fi, "image": pi[fi]}

    # P3': lone filler at odd k with image below low interval.
    if k % 2 == 1:
        lone = k - 1
        if lone in filler_indices:
            img_lone = pi[lone]
            if img_lone < img_lo:
                return {"prediction": "fatal",
                        "reason": "P3prime_lone_filler_image_below",
                        "filler": lone, "image": img_lone}

    return {"prediction": "detachable",
            "reason": "no_filler_image_above_and_no_lone_below"}


def evaluate_pairing_three(k: int, pi: Sequence[int]) -> dict:
    """Compare three-interval candidates with the suffix-walk truth."""
    candidates = three_interval_ladder_sets(k, pi)
    true_minimal = minimal_fatal_toggle_sets(k, pi)
    true_size6 = {s for s in true_minimal if len(s) == 6}
    rows = []
    correct = 0
    wrong = 0
    for cand in candidates:
        pred = predict_three_interval_fatal(k, pi, cand)
        is_truly_fatal = tuple(cand) in true_size6
        if pred["prediction"] == "fatal":
            is_correct = is_truly_fatal
        else:
            is_correct = not is_truly_fatal
        rows.append({
            "candidate": list(cand),
            "prediction": pred,
            "truly_fatal": is_truly_fatal,
            "correct": is_correct,
        })
        if is_correct:
            correct += 1
        else:
            wrong += 1
    # Also report fatal size-6 sets not captured as candidates.
    missing = sorted(true_size6 - {tuple(c) for c in candidates})
    return {
        "k": k,
        "pi": list(pi),
        "candidates_checked": len(candidates),
        "true_size6_count": len(true_size6),
        "predictions_correct": correct,
        "predictions_wrong": wrong,
        "missing_from_candidates": [list(m) for m in missing],
        "rows": rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--k", type=int, default=7)
    parser.add_argument("--pi", type=str, default=None)
    args = parser.parse_args()

    if args.pi:
        pi = tuple(int(x) for x in args.pi.split(","))
        result = evaluate_pairing_three(args.k, pi)
        print(json.dumps(result, indent=2, default=list))
        return

    # Otherwise, find all pairings with a size-6 minimal fatal set.
    captured = 0
    missed = 0
    overpredictions = 0
    examples_missed = []
    examples_over = []
    for pi in permutations(range(args.k)):
        out = evaluate_pairing_three(args.k, pi)
        captured += out["true_size6_count"] - len(out["missing_from_candidates"])
        missed += len(out["missing_from_candidates"])
        wrong_fatal = [
            r for r in out["rows"]
            if r["prediction"]["prediction"] == "fatal" and not r["truly_fatal"]
        ]
        overpredictions += len(wrong_fatal)
        if out["missing_from_candidates"] and len(examples_missed) < 5:
            examples_missed.append({
                "pi": list(pi),
                "missing": out["missing_from_candidates"],
            })
        if wrong_fatal and len(examples_over) < 5:
            examples_over.append({
                "pi": list(pi),
                "wrong_candidates": [r["candidate"] for r in wrong_fatal],
            })
    summary = {
        "k": args.k,
        "captured": captured,
        "missed_size6_fatal_sets": missed,
        "overpredicted_detachable_as_candidate": overpredictions,
        "examples_missed": examples_missed,
        "examples_over": examples_over,
    }
    print(json.dumps(summary, indent=2, default=list))


if __name__ == "__main__":
    main()
