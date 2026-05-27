"""Regression tests for the four-interval (size-8) ladder generator
and V5 criterion at larger k.

The same (P3, P3') chain-end fatality criterion of V5 is conjectured
to extend to all sizes 2m.  This test pins:

  - The user's k=9 cyclic four-interval ladder is correctly classified
    as fatal (P3' fires for the lone filler index 8 with image 0).
  - A k=10 four-interval candidate with images {2,..,9} and fillers
    images {0,1} is correctly classified as detachable (no filler
    image above the high interval, k even so no lone filler trigger).
"""
import os
import sys
import unittest


SCRIPT_DIR = os.path.join(os.path.dirname(__file__), "..", "scripts")
sys.path.insert(0, os.path.abspath(SCRIPT_DIR))

from four_interval_ladder_probe import (  # noqa: E402
    construct_cyclic_four_interval,
    four_interval_ladder_sets,
    predict_four_interval_fatal,
)
from rectangle_detachability_probe import minimal_fatal_toggle_sets  # noqa: E402


class FourIntervalLadderTest(unittest.TestCase):

    def test_construct_cyclic_four_interval_k9_is_candidate(self):
        pi = construct_cyclic_four_interval(9)
        self.assertIsNotNone(pi)
        candidates = four_interval_ladder_sets(9, pi)
        self.assertEqual(candidates, [(0, 1, 2, 3, 4, 5, 6, 7)])

    def test_v5_classifies_k9_cyclic_four_interval_fatal(self):
        """At k=9 the lone filler index 8 has image 0 < a=1.  P3' fires."""
        pi = construct_cyclic_four_interval(9)
        pred = predict_four_interval_fatal(9, pi, (0, 1, 2, 3, 4, 5, 6, 7))
        self.assertEqual(pred["prediction"], "fatal")
        self.assertEqual(pred["reason"], "P3prime_lone_filler_image_below")

    def test_v5_matches_suffix_walk_on_k9_construction(self):
        pi = construct_cyclic_four_interval(9)
        minimal = minimal_fatal_toggle_sets(9, pi)
        size8 = sorted(s for s in minimal if len(s) == 8)
        self.assertIn((0, 1, 2, 3, 4, 5, 6, 7), size8)

    def test_k10_four_interval_with_low_fillers_is_detachable(self):
        """At k=10 even, four-interval ladder {0,..,7} with image
        {2,..,9} and filler images {0,1} (both below) is NOT a
        minimal fatal set of size 8 (V5 predicts detachable)."""
        pi = (2, 4, 5, 7, 6, 8, 3, 9, 0, 1)
        candidates = four_interval_ladder_sets(10, pi)
        self.assertEqual(candidates, [(0, 1, 2, 3, 4, 5, 6, 7)])
        pred = predict_four_interval_fatal(10, pi, (0, 1, 2, 3, 4, 5, 6, 7))
        self.assertEqual(pred["prediction"], "detachable")
        # The minimal fatal sets do not include this size-8 set.
        minimal = minimal_fatal_toggle_sets(10, pi)
        size8 = [s for s in minimal if len(s) == 8]
        self.assertNotIn((0, 1, 2, 3, 4, 5, 6, 7), size8)


if __name__ == "__main__":
    unittest.main()
