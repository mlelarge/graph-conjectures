"""Unified V6'' fatal-support classifier (D49).

V6'' definition (Section 49.3 of exchange_proof_draft.md):

  Given a fork-tree pairing pi at size k and a candidate support
  S subset of [k] of even size 2m >= 2, decide whether S is a minimal
  fatal toggle support of pi.

  V6'' fires iff S is a cyclic m-interval ladder candidate AND at
  least one of:

    (P3)  some filler image > max(I_{m-1}) (above the high interval),
    (P3') odd k, lone filler index k-1 in F with image < min(I_0),
          AND all intervals are natural odd-start,
    (P4)  m >= 2 AND all intervals are natural odd-start.

  This is the user's proposed V6'' (P3 vee (P3' wedge NaturalOddStart)
  vee P4), uniform across sizes m >= 1.

Unlike the prior `predict_cyclic_ladder_minimal_fatal` of
`cyclic_ladder_probe.py`, V6'' does NOT reject candidates of size 2.
"""
from __future__ import annotations

import os
import sys
from typing import Sequence

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def _intervals_from_images(images: Sequence[int]) -> list[tuple[int, int]] | None:
    """Decompose sorted images into consecutive-pair intervals.

    Returns intervals [(a_0, a_0+1), ..., (a_{m-1}, a_{m-1}+1)] if
    every image is in a consecutive 2-pair.  Consecutive intervals
    may be adjacent (e.g., the anchored case {1,2,3,4} decomposes as
    {1,2} and {3,4}); they cannot overlap (impossible since pi is a
    permutation).  Returns None if the image set has odd size or is
    not 2-pair-decomposable.
    """
    if len(images) % 2 != 0:
        return None
    images_sorted = sorted(images)
    intervals: list[tuple[int, int]] = []
    i = 0
    while i < len(images_sorted):
        if i + 1 >= len(images_sorted) or images_sorted[i + 1] - images_sorted[i] != 1:
            return None
        intervals.append((images_sorted[i], images_sorted[i + 1]))
        i += 2
    return intervals


def predict_v6pp(
    k: int,
    pi: Sequence[int],
    S: Sequence[int],
) -> dict:
    """V6'' fatal-support classifier.

    Returns a dict with keys:
      - "prediction": "minimal_fatal" or "not_minimal_fatal" or
        "not_a_candidate".
      - "reason": "P3", "P3prime_and_natural_odd_start", "P4", or a
        rejection reason.
      - "intervals", "natural_odd_start" for diagnostics.
    """
    S_sorted = tuple(sorted(S))
    if len(S_sorted) == 0 or len(S_sorted) % 2 != 0:
        return {"prediction": "not_a_candidate", "reason": "odd_size"}

    pi_S = sorted(pi[i] for i in S_sorted)
    intervals = _intervals_from_images(pi_S)
    if intervals is None:
        return {"prediction": "not_a_candidate", "reason": "not_interval_decomposable"}

    low = intervals[0][0]
    high = intervals[-1][1]
    natural_odd_start = all(iv[0] % 2 == 1 for iv in intervals)
    S_set = set(S_sorted)
    fillers = [i for i in range(k) if i not in S_set]

    diag = {
        "intervals": [list(iv) for iv in intervals],
        "natural_odd_start": natural_odd_start,
    }

    # P3: filler image strictly above the high interval.
    for fi in fillers:
        if pi[fi] > high:
            return {
                "prediction": "minimal_fatal",
                "reason": "P3",
                "filler": fi,
                "image": pi[fi],
                **diag,
            }

    # P3' ∧ NaturalOddStart: odd k, lone filler k-1 with image < low,
    # AND all intervals are natural odd-start.
    if k % 2 == 1:
        lone = k - 1
        if lone in S_set:
            pass  # lone is selected, not a filler
        else:
            if pi[lone] < low and natural_odd_start:
                return {
                    "prediction": "minimal_fatal",
                    "reason": "P3prime_and_natural_odd_start",
                    "filler": lone,
                    "image": pi[lone],
                    **diag,
                }

    # P4: m >= 2 (multi-interval) AND all intervals natural odd-start.
    if len(intervals) >= 2 and natural_odd_start:
        return {
            "prediction": "minimal_fatal",
            "reason": "P4_natural_odd_start_residual",
            **diag,
        }

    return {
        "prediction": "not_minimal_fatal",
        "reason": "no_v6pp_trigger",
        **diag,
    }


if __name__ == "__main__":
    import argparse
    import json

    p = argparse.ArgumentParser()
    p.add_argument("--k", type=int, required=True)
    p.add_argument("--pi", type=str, required=True)
    p.add_argument("--S", type=str, required=True)
    args = p.parse_args()
    pi = tuple(int(x) for x in args.pi.split(","))
    S = tuple(int(x) for x in args.S.split(","))
    print(json.dumps(predict_v6pp(args.k, pi, S), indent=2, default=list))
