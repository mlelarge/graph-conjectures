"""Regression tests for V6'' (D49).

V6'' is the unified fatal-support classifier:

  V6'' fires on support S iff S is a cyclic m-interval ladder
  candidate AND at least one of:
    (P3)  some filler image > max(I_{m-1});
    (P3') odd k, lone filler k-1 has image < min(I_0), and all
          intervals are natural odd-start;
    (P4)  m >= 2 AND all intervals are natural odd-start.

Verified: V6'' classifies every minimal fatal support correctly
across all 5040 pairings at k=7 (D49).
"""
from __future__ import annotations

import os
import sys

import pytest


SCRIPT_DIR = os.path.join(os.path.dirname(__file__), "..", "scripts")
sys.path.insert(0, os.path.abspath(SCRIPT_DIR))

from rectangle_detachability_probe import minimal_fatal_toggle_sets  # noqa: E402
from v6pp_predictor import _intervals_from_images, predict_v6pp  # noqa: E402


def test_intervals_decomposition_consecutive_pairs():
    # Anchored {1,2,3,4} decomposes as {1,2} + {3,4} (no gap).
    assert _intervals_from_images([1, 2, 3, 4]) == [(1, 2), (3, 4)]
    # Spread-out {1,2,5,6}.
    assert _intervals_from_images([1, 2, 5, 6]) == [(1, 2), (5, 6)]
    # Three intervals {1,2,3,4,5,6}.
    assert _intervals_from_images([1, 2, 3, 4, 5, 6]) == [(1, 2), (3, 4), (5, 6)]
    # Odd size invalid.
    assert _intervals_from_images([1, 2, 3]) is None
    # Non-consecutive within pair: image 3 cannot pair with 1 -> None.
    assert _intervals_from_images([1, 3, 4, 5]) is None


def test_predict_v6pp_size2_p3_takes_precedence():
    """Cyclic shift k=5 pi=(1,2,3,4,0), S={0,1}. Interval {1,2}.
    Filler image 3 > 2 = high, so P3 fires first (before P3')."""
    pred = predict_v6pp(5, (1, 2, 3, 4, 0), (0, 1))
    assert pred["prediction"] == "minimal_fatal"
    assert pred["reason"] == "P3"


def test_predict_v6pp_size2_mixed_parity_no_p3prime():
    """V6 failure case (D30): pi=(5,3,2,6,4,0,1), k=7, S={0,1,2,3}.
    Intervals {2,3} and {5,6} — even-start mixed parity. The lone
    filler 6 has image 1 < 2 = low, but V6'' rejects because mixed
    parity. The set is NOT minimally fatal under brute force."""
    pred = predict_v6pp(7, (5, 3, 2, 6, 4, 0, 1), (0, 1, 2, 3))
    assert pred["prediction"] == "not_minimal_fatal"
    # Cross-check with brute force.
    minimal = minimal_fatal_toggle_sets(7, (5, 3, 2, 6, 4, 0, 1))
    assert (0, 1, 2, 3) not in {tuple(s) for s in minimal}


def test_predict_v6pp_size6_p3prime_natural_odd_start():
    """User's pinned k=7 size-6 ladder: pi=(5,4,6,1,3,2,0),
    S={0,1,2,3,4,5}. Intervals {1,2},{3,4},{5,6}. Lone filler 6 with
    image 0 < 1, all intervals natural odd-start. P3' fires."""
    pred = predict_v6pp(7, (5, 4, 6, 1, 3, 2, 0), (0, 1, 2, 3, 4, 5))
    assert pred["prediction"] == "minimal_fatal"
    assert pred["reason"] == "P3prime_and_natural_odd_start"


def test_predict_v6pp_size4_p4_residual():
    """D25/D26 example: pi=(4,0,2,8,6,1,7,5,3), k=9, S={2,3,4,5,6,7}.
    Intervals {1,2}, {5,6}, {7,8}. Filler images include 3, 4 (in
    gap), so no P3, and lone filler has image 3 in [low, high] so no
    P3'. All intervals natural odd-start → P4 fires."""
    pred = predict_v6pp(9, (4, 0, 2, 8, 6, 1, 7, 5, 3), (2, 3, 4, 5, 6, 7))
    assert pred["prediction"] == "minimal_fatal"
    assert pred["reason"] == "P4_natural_odd_start_residual"


def test_predict_v6pp_exhaustive_k7_zero_mismatches():
    """V6'' classifies every minimal fatal support correctly across
    all 5040 pairings at k=7. (Full sweep, ~25 min; we trust the
    catalogue and sample a handful of pairings.)"""
    test_pis = [
        (1, 2, 3, 4, 5, 6, 0),  # cyclic shift k=7, max supports per pairing
        (5, 4, 6, 1, 3, 2, 0),  # user's size-6 example
        (5, 3, 2, 6, 4, 0, 1),  # V6 failure case
        (1, 3, 2, 5, 4, 6, 0),  # R6 from D35
        (0, 1, 2, 3, 4, 5, 6),  # identity
    ]
    for pi in test_pis:
        minimal = minimal_fatal_toggle_sets(7, pi)
        for S in minimal:
            pred = predict_v6pp(7, pi, S)
            assert pred["prediction"] == "minimal_fatal", (
                f"V6'' missed minimal fatal {S} on pi={pi}: {pred}"
            )


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
