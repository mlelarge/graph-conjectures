"""Regression tests for the ordered interval-peeling criterion.

The V4 criterion of `ordered_peeling_probe.predict_ladder_fatal`:

  A two-interval ladder candidate S is fatal iff at least one of:
    (P3)  some filler image > high_max (above the high interval), OR
    (P3') at odd k, the lone unpaired filler index (k-1) has image
          strictly below the low interval.

  Otherwise S is detachable.

Pinned facts:
  - V4 perfectly classifies every two-interval ladder candidate at
    k=5 and k=6 (over all 120 + 720 permutations).
  - V4 correctly classifies the user's k=7 non-initial four-ladder
    counterexample as fatal.
  - V4 does NOT generate or classify size-6 ladders; those are an
    open extension.
"""
import os
import sys
import unittest


SCRIPT_DIR = os.path.join(os.path.dirname(__file__), "..", "scripts")
sys.path.insert(0, os.path.abspath(SCRIPT_DIR))

from ordered_peeling_probe import (  # noqa: E402
    evaluate_pairing,
    predict_ladder_fatal,
    sweep_all,
)


class OrderedPeelingCriterionTest(unittest.TestCase):

    def test_v4_perfect_at_k5(self):
        out = sweep_all(5)
        self.assertEqual(out["wrong_pairings"], 0)
        self.assertEqual(out["all_correct_pairings"], 120)

    def test_v4_perfect_at_k6(self):
        out = sweep_all(6)
        self.assertEqual(out["wrong_pairings"], 0)
        self.assertEqual(out["all_correct_pairings"], 720)

    def test_v4_classifies_k7_non_initial_four_ladder(self):
        """User's pinned k=7 case: pi=(3,5,4,6,1,2,0), S={0,1,2,3}
        with images {3,4,5,6}.  P3' fires for the lone filler index
        6 with image 0."""
        pi = (3, 5, 4, 6, 1, 2, 0)
        pred = predict_ladder_fatal(7, pi, (0, 1, 2, 3))
        self.assertEqual(pred["prediction"], "fatal")
        self.assertEqual(pred["reason"], "P3prime_lone_filler_image_below")

    def test_v4_classifies_k7_two_interval_overpredict_case(self):
        """User's k=6 overpredict case generalized: pi=(0,1,2,4,3,5)
        with candidate {2,3,4,5}.  V4 must correctly predict
        detachable (no image above, no lone filler at even k)."""
        pi = (0, 1, 2, 4, 3, 5)
        pred = predict_ladder_fatal(6, pi, (2, 3, 4, 5))
        self.assertEqual(pred["prediction"], "detachable")

    def test_v4_classifies_anchored_with_top_boundary_filler_fatal(self):
        """At k=6 with anchored image {1,2,3,4}, any filler image of 5
        (the top boundary) makes the ladder fatal."""
        pi = (1, 3, 2, 4, 0, 5)
        pred = predict_ladder_fatal(6, pi, (0, 1, 2, 3))
        self.assertEqual(pred["prediction"], "fatal")
        self.assertEqual(pred["reason"], "P3_image_above")

    def test_v4_classifies_k5_anchored_fatal(self):
        """At k=5 anchored ladder, the lone filler index 4 with image
        0 triggers P3'."""
        pi = (1, 3, 2, 4, 0)
        pred = predict_ladder_fatal(5, pi, (0, 1, 2, 3))
        self.assertEqual(pred["prediction"], "fatal")
        self.assertEqual(pred["reason"], "P3prime_lone_filler_image_below")

    def test_v4_classifies_cyclic_shift_k5_fatal_at_pair_level(self):
        """Cyclic shift at k=5 has fatal pair (0,1) — but that's
        size-2, not a two-interval ladder.  V4's `two_interval_ladder_sets`
        does not produce it as a candidate.  This test verifies that
        V4 reports no four-ladder candidate (correctly, because the
        fatal sets are size-2 pairs, not size-4 ladders)."""
        pi = (1, 2, 3, 4, 0)
        out = evaluate_pairing(5, pi)
        # No two-interval-ladder candidates expected (the cyclic shift
        # at k=5 has no size-4 minimal fatal set).
        self.assertEqual(out["candidates_checked"], 0)


if __name__ == "__main__":
    unittest.main()
