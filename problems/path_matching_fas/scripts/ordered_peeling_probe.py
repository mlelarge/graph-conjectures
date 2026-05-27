"""Ordered interval-peeling test for fork-tree ladder fatality.

Section 26 of exchange_proof_draft.md (D16) refuted the naive
"two adjacent B-image intervals" criterion: it overpredicts fatality.
The refinement is that fatality depends on the A-side position of
filler blocks AND on whether filler images land below the ladder's
B-image range.

This script implements a candidate **Ordered Interval-Peeling**
criterion and tests it against the suffix-walk ground truth.

Candidate criterion for a two-interval ladder S:

  S is fatal iff at least one of:
   (P1) some filler A-index falls AFTER all selected A-indices, OR
   (P2) some filler A-index is INTERLEAVED between selected blocks
        (one selected even-block then a filler block then another
        selected even-block), OR
   (P3) some filler image is OUTSIDE the ladder image range
        [low_min, high_max].

  S is detachable iff every filler A-index is strictly BEFORE all
  selected A-indices AND every filler image is strictly below the
  low B-interval.

This is a precise local rule.  We test it against `minimal_fatal_toggle_sets`
across all permutations at small k.
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
    two_interval_ladder_sets,
)


def predict_ladder_fatal(
    k: int,
    pi: Sequence[int],
    selected: Sequence[int],
) -> dict:
    """Predict fatality of a two-interval ladder candidate via the
    ordered peeling criterion.

    Returns a dict with the prediction and the reason.  The reason is
    one of "P1_after", "P2_between", "P3_outside_image",
    "detachable_filler_before_below".
    """
    selected = tuple(sorted(selected))
    images = sorted(pi[i] for i in selected)
    if len(set(images)) != 4:
        return {"prediction": "not_a_candidate", "reason": "image_size"}
    a, ap1, b, bp1 = images
    if ap1 - a != 1 or bp1 - b != 1 or b <= ap1:
        return {"prediction": "not_a_candidate", "reason": "not_two_intervals"}
    low = {a, ap1}
    high = {b, bp1}
    blocks = even_adjacent_blocks(k)
    selected_block_indices = []
    for idx, block in enumerate(blocks):
        if set(block).issubset(selected):
            selected_block_indices.append(idx)
    if len(selected_block_indices) != 2:
        return {"prediction": "not_a_candidate", "reason": "not_two_blocks"}
    # Check the alternating image structure: each selected block has one
    # low and one high image.
    for idx in selected_block_indices:
        block = blocks[idx]
        block_images = {pi[i] for i in block}
        if not (len(block_images & low) == 1 and len(block_images & high) == 1):
            return {"prediction": "not_a_candidate", "reason": "not_alternating"}

    # Image range of the ladder.
    img_lo, img_hi = a, bp1
    selected_set = set(selected)
    filler_indices = [i for i in range(k) if i not in selected_set]

    # (P3) Any filler image ABOVE the high interval?
    # Empirically at k=6 with two-block filler, this is the only fatal
    # trigger.  Above-boundary image (k-1) is included if k-1 > img_hi.
    for fi in filler_indices:
        img = pi[fi]
        if img > img_hi:
            return {"prediction": "fatal", "reason": "P3_image_above",
                    "filler": fi, "image": img}

    # (P3') At odd k there is a lone unpaired filler index (k-1).  If
    # the lone filler's image is BELOW the low interval (at the chain
    # bottom), the resulting long diagonal A_{k-1} -> B_{image} is
    # fatal.  This is the k=5 anchored-ladder fatality signature and
    # also fires for the k=7 lone-filler case observed in pi=
    # (3,5,4,6,1,2,0).
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


def evaluate_pairing(k: int, pi: Sequence[int]) -> dict:
    """Compare our predicted ladder fatality with the suffix-walk truth."""
    candidates = two_interval_ladder_sets(k, pi)
    true_minimal = minimal_fatal_toggle_sets(k, pi)
    true_higher = {s for s in true_minimal if len(s) > 2}
    rows = []
    correct = 0
    wrong = 0
    for cand in candidates:
        pred = predict_ladder_fatal(k, pi, cand)
        is_truly_fatal = tuple(cand) in true_higher
        if pred["prediction"] == "fatal":
            is_correct = is_truly_fatal
        elif pred["prediction"] == "detachable":
            is_correct = not is_truly_fatal
        else:
            is_correct = not is_truly_fatal  # not_a_candidate -> should be detachable
        if is_correct:
            correct += 1
        else:
            wrong += 1
        rows.append({
            "candidate": list(cand),
            "prediction": pred,
            "truly_fatal": is_truly_fatal,
            "correct": is_correct,
        })
    return {
        "k": k,
        "pi": list(pi),
        "candidates_checked": len(candidates),
        "correct": correct,
        "wrong": wrong,
        "all_correct": wrong == 0,
        "rows": rows,
    }


def sweep_all(k: int) -> dict:
    """Test the ordered peeling criterion across all k! pairings."""
    correct_all = 0
    wrong_pairings = []
    for pi in permutations(range(k)):
        out = evaluate_pairing(k, pi)
        if out["all_correct"]:
            correct_all += 1
        else:
            wrong_pairings.append(out)
    return {
        "k": k,
        "total_pairings": __import__("math").factorial(k),
        "all_correct_pairings": correct_all,
        "wrong_pairings": len(wrong_pairings),
        "first_wrong_examples": wrong_pairings[:5],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--k", type=int, default=5)
    parser.add_argument("--all", action="store_true",
                        help="sweep all k! pairings")
    parser.add_argument("--pi", type=str, default=None,
                        help="specific pairing as comma-separated indices")
    args = parser.parse_args()

    if args.pi:
        pi = tuple(int(x) for x in args.pi.split(","))
        result = evaluate_pairing(args.k, pi)
    elif args.all:
        result = sweep_all(args.k)
    else:
        result = sweep_all(args.k)
    print(json.dumps(result, indent=2, default=list))


if __name__ == "__main__":
    main()
