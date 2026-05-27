"""Regression tests for the three-interval (size-6) ladder generator
and V5 criterion.

  - `three_interval_ladder_sets` enumerates size-6 ladder candidates
    that match the alternating cyclic structure described in Section 28
    of `exchange_proof_draft.md`.
  - `predict_three_interval_fatal` implements V5: (P3) any filler image
    above the highest B-interval, or (P3') at odd k a lone unpaired
    filler index k-1 with image below the lowest interval.
"""
import os
import sys
import unittest


SCRIPT_DIR = os.path.join(os.path.dirname(__file__), "..", "scripts")
sys.path.insert(0, os.path.abspath(SCRIPT_DIR))

from three_interval_ladder_probe import (  # noqa: E402
    evaluate_pairing_three,
    predict_three_interval_fatal,
    three_interval_ladder_sets,
)


class ThreeIntervalLadderTest(unittest.TestCase):

    def test_user_pinned_k7_size6_is_candidate(self):
        """User's pinned pi=(5,4,6,1,3,2,0) at k=7 has a size-6 ladder
        candidate at {0,1,2,3,4,5}."""
        pi = (5, 4, 6, 1, 3, 2, 0)
        candidates = three_interval_ladder_sets(7, pi)
        self.assertEqual(candidates, [(0, 1, 2, 3, 4, 5)])

    def test_v5_classifies_user_pinned_k7_fatal(self):
        """V5's P3' fires for the lone filler index 6 with image 0
        below the low interval [1,2]."""
        pi = (5, 4, 6, 1, 3, 2, 0)
        pred = predict_three_interval_fatal(7, pi, (0, 1, 2, 3, 4, 5))
        self.assertEqual(pred["prediction"], "fatal")
        self.assertEqual(pred["reason"], "P3prime_lone_filler_image_below")

    def test_v5_evaluate_user_pinned_k7(self):
        """The full evaluator agrees with the suffix-walk truth on the
        user's pinned k=7 case: one candidate, correctly classified as
        fatal."""
        pi = (5, 4, 6, 1, 3, 2, 0)
        out = evaluate_pairing_three(7, pi)
        self.assertEqual(out["candidates_checked"], 1)
        self.assertEqual(out["predictions_correct"], 1)
        self.assertEqual(out["predictions_wrong"], 0)
        self.assertEqual(out["missing_from_candidates"], [])

    def test_no_three_interval_candidate_at_k4(self):
        """k=4 has only two blocks, so no three-interval ladder can
        exist."""
        for pi in [(0, 1, 2, 3), (3, 0, 2, 1)]:
            self.assertEqual(three_interval_ladder_sets(4, pi), [])

    def test_no_three_interval_candidate_at_k5(self):
        """k=5 has two blocks plus one lone vertex, still no size-6
        ladder."""
        for pi in [(0, 1, 2, 3, 4), (1, 3, 2, 4, 0)]:
            self.assertEqual(three_interval_ladder_sets(5, pi), [])


if __name__ == "__main__":
    unittest.main()
