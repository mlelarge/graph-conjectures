"""Size-10 / five-interval ladder probe at k>=11.

Tests whether the unified V6 criterion (P3, P3', P4) extends to
five-interval cyclic ladders.  V6 is verified empirically at sizes
2, 3, 4 in `scripts/unified_v6_probe.py` and `tests/test_unified_v6.py`.

A five-interval ladder consists of:
  - 5 selected even-odd toggle blocks E_0, ..., E_4;
  - their B-images form five adjacent-pair intervals
    I_0, I_1, ..., I_4 of size 2;
  - each selected block hits exactly two distinct intervals (one image
    per interval), and the block-interval incidence graph is a 5-cycle.

To exercise the residual P4 trigger we want constructions where neither
P3 (some filler image above the high interval) nor P3' (odd k, lone
filler image below the low interval) fires.  At k=13 with five
intervals = 10 selected indices, we have three filler indices, so a
genuine residual instance requires the intervals to leave an *internal*
or *external* gap inside [a, b] that fillers can absorb.  We use
the natural odd-start shape I = {1,2},{3,4},{5,6},{7,8},{11,12} and
its even-start translate {2,3},{4,5},{6,7},{8,9},{11,12}.

Usage:
  uv run python scripts/five_interval_ladder_probe.py --k 13
  uv run python scripts/five_interval_ladder_probe.py --k 13 \\
    --pi <comma-separated-perm>
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from itertools import combinations
from typing import Sequence

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cyclic_ladder_probe import (  # noqa: E402
    cyclic_ladder_sets,
    cyclic_ladder_structure,
    predict_cyclic_ladder_minimal_fatal,
    targeted_minimal_fatal_certificate,
)
from rectangle_detachability_probe import (  # noqa: E402
    even_adjacent_blocks,
    minimal_fatal_toggle_sets,
)
from unified_v6_probe import predict_v6  # noqa: E402


def five_interval_ladder_sets(
    k: int,
    pi: Sequence[int],
) -> list[tuple[int, ...]]:
    """Enumerate cyclic five-interval (size-10) ladder candidates."""
    return cyclic_ladder_sets(k, pi, 5)


def construct_cyclic_five_interval(
    k: int,
    odd_start: bool = True,
) -> tuple[int, ...] | None:
    """Construct a five-interval cyclic ladder pairing at minimal k.

    Five intervals of size 2 require 10 selected images.  To leave room
    for fillers whose images sit in [a, b] (avoiding P3 and P3'), we
    introduce a one-position gap between the fourth and fifth interval
    so the fillers can absorb the missing images internally.

    odd_start=True (k>=13):
      I_0={1,2}, I_1={3,4}, I_2={5,6}, I_3={7,8}, I_4={11,12}; gap {9,10}.
      Blocks E_0..E_4 at indices (0,1),(2,3),(4,5),(6,7),(8,9) form a
      5-cycle on the interval graph:
        E_0 -> {1, 3}   (I_0, I_1)
        E_1 -> {4, 5}   (I_1, I_2)
        E_2 -> {6, 7}   (I_2, I_3)
        E_3 -> {8, 11}  (I_3, I_4)
        E_4 -> {12, 2}  (I_4, I_0)
      Fillers at indices 10, 11, 12 take images {0, 9, 10}; lone filler
      index 12 gets image 10 (in [a, b] = [1, 12], no P3').

    odd_start=False (k>=13):
      Shift every interval up by 1: I_0={2,3}, ..., I_3={8,9},
      I_4={11,12}.  Four intervals even-start (only I_4 stays odd-start).
      Blocks E_0..E_4 carry the analogous images.  Fillers at 10, 11, 12
      get {0, 1, 10}; lone filler index 12 gets image 10 (in [2, 12]).

    Returns the pairing pi (tuple of length k), or None if k < 13.
    """
    if k < 13:
        return None
    pi = [-1] * k
    if odd_start:
        # selected blocks
        pi[0], pi[1] = 1, 3
        pi[2], pi[3] = 4, 5
        pi[4], pi[5] = 6, 7
        pi[6], pi[7] = 8, 11
        pi[8], pi[9] = 12, 2
        # fillers: indices 10, 11, 12 get {0, 9, 10}
        # P3' avoided: lone filler index k-1 = 12 has image 10 in [1, 12]
        pi[10] = 0
        pi[11] = 9
        pi[12] = 10
        # remaining indices (if k > 13) get the unused images in order
        used = set(pi[:13])
        remaining = [v for v in range(k) if v not in used]
        for idx, v in enumerate(remaining):
            pi[13 + idx] = v
    else:
        # intervals shifted up by 1 (I_0..I_3 even-start, I_4 odd-start)
        pi[0], pi[1] = 2, 4
        pi[2], pi[3] = 5, 6
        pi[4], pi[5] = 7, 8
        pi[6], pi[7] = 9, 11
        pi[8], pi[9] = 12, 3
        # fillers: 10, 11, 12 -> {0, 1, 10}; lone filler 12 -> 10
        pi[10] = 0
        pi[11] = 1
        pi[12] = 10
        used = set(pi[:13])
        remaining = [v for v in range(k) if v not in used]
        for idx, v in enumerate(remaining):
            pi[13 + idx] = v
    if any(v < 0 for v in pi):
        return None
    return tuple(pi)


def evaluate_pairing_five(
    k: int,
    pi: Sequence[int],
    time_budget_sec: float | None = None,
    run_full_sweep: bool = False,
) -> dict:
    """Compare V6 against suffix-walk truth on one pairing.

    By default we use the *targeted* minimal-fatal certificate
    (a single completion run plus its 10 one-toggle deletions), which
    runs in seconds at k<=13.  Set `run_full_sweep=True` to also
    invoke `minimal_fatal_toggle_sets`; this is slow (~1-2 min at
    k=13) but provides a stronger cross-check.
    """
    candidates = five_interval_ladder_sets(k, pi)
    rows = []
    full_minimal: set[tuple[int, ...]] | None = None
    if run_full_sweep:
        full_minimal = {
            tuple(s) for s in minimal_fatal_toggle_sets(k, pi)
        }
    for cand in candidates:
        struct = cyclic_ladder_structure(k, pi, cand)
        pred_v5 = predict_cyclic_ladder_minimal_fatal(k, pi, cand)
        pred_v6 = predict_v6(k, pi, cand)
        cert = targeted_minimal_fatal_certificate(
            k, pi, cand, time_budget_sec=time_budget_sec
        )
        row = {
            "candidate": list(cand),
            "intervals": [list(iv) for iv in struct["intervals"]] if struct else None,
            "v5_prediction": pred_v5,
            "v6_prediction": pred_v6,
            "minimal_fatal_certificate": cert["minimal_fatal"],
            "certificate_reason": cert["reason"],
        }
        v6_says_fatal = pred_v6["prediction"] == "minimal_fatal"
        row["v6_correct"] = (v6_says_fatal == cert["minimal_fatal"])
        if full_minimal is not None:
            in_full = tuple(cand) in full_minimal
            row["in_full_minimal_sweep"] = in_full
            row["v6_matches_full_sweep"] = (v6_says_fatal == in_full)
        rows.append(row)
    out = {
        "k": k,
        "pi": list(pi),
        "candidates": [list(c) for c in candidates],
        "rows": rows,
    }
    if full_minimal is not None:
        out["full_minimal_fatal_sets"] = sorted(list(s) for s in full_minimal)
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--k", type=int, default=13)
    parser.add_argument("--pi", type=str, default=None)
    parser.add_argument("--odd-start", action="store_true", default=True)
    parser.add_argument("--even-start", dest="odd_start", action="store_false")
    parser.add_argument("--full-sweep", action="store_true", default=False,
                        help="also run minimal_fatal_toggle_sets (slow at k=13)")
    parser.add_argument("--time-budget-sec", type=float, default=None)
    args = parser.parse_args()

    if args.pi:
        pi = tuple(int(x) for x in args.pi.split(","))
    else:
        pi = construct_cyclic_five_interval(args.k, odd_start=args.odd_start)
        if pi is None:
            print(json.dumps({"error": "k too small (need k >= 13)"}, indent=2))
            return

    result = evaluate_pairing_five(
        args.k,
        pi,
        time_budget_sec=args.time_budget_sec,
        run_full_sweep=args.full_sweep,
    )
    print(json.dumps(result, indent=2, default=list))


if __name__ == "__main__":
    main()
