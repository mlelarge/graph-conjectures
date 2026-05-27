"""Regression tests for the unified V6 fatal detector.

V6 combines:
  - chain-end triggers P3 (filler image above high interval),
    P3' (odd-k lone filler image below low interval),
  - residual P4 (all intervals natural odd-start when P3/P3' don't fire).

The user's Section 37 (D26) established P4 at three intervals.  This
test pins V6 at four intervals (k=11) as well, supporting the
conjecture that natural-odd-start is the universal residual trigger.
"""
import os
import sys
import unittest


SCRIPT_DIR = os.path.join(os.path.dirname(__file__), "..", "scripts")
sys.path.insert(0, os.path.abspath(SCRIPT_DIR))

from rectangle_detachability_probe import minimal_fatal_toggle_sets  # noqa: E402
from unified_v6_probe import predict_v6  # noqa: E402


class UnifiedV6Test(unittest.TestCase):

    def test_v6_four_interval_natural_odd_start_at_k11(self):
        """At k=11 with intervals {1,2},{3,4},{5,6},{9,10} (all
        natural odd-start), no P3/P3' triggers — P4 fires."""
        pi = (1, 3, 4, 5, 6, 9, 10, 2, 0, 8, 7)
        selected = (0, 1, 2, 3, 4, 5, 6, 7)
        pred = predict_v6(11, pi, selected)
        self.assertEqual(pred["prediction"], "minimal_fatal")
        self.assertEqual(pred["reason"], "P4_natural_odd_start_residual")
        # Cross-check with suffix walk.
        minimal = minimal_fatal_toggle_sets(11, pi)
        self.assertIn(tuple(selected), {tuple(s) for s in minimal})

    def test_v6_four_interval_even_start_at_k11_detachable(self):
        """Same shape, but even-start intervals → no P4 trigger, no
        chain-end trigger, predicted not minimally fatal."""
        pi = (2, 4, 5, 6, 7, 9, 10, 3, 0, 1, 8)
        selected = (0, 1, 2, 3, 4, 5, 6, 7)
        pred = predict_v6(11, pi, selected)
        self.assertEqual(pred["prediction"], "not_minimal_fatal")
        # And suffix walk confirms.
        minimal = minimal_fatal_toggle_sets(11, pi)
        self.assertNotIn(tuple(selected), {tuple(s) for s in minimal})

    def test_v6_three_interval_odd_start_at_k9(self):
        """User's D25/D26 pinned example: three-interval natural
        odd-start at k=9."""
        pi = (4, 0, 2, 8, 6, 1, 7, 5, 3)
        selected = (2, 3, 4, 5, 6, 7)
        pred = predict_v6(9, pi, selected)
        self.assertEqual(pred["prediction"], "minimal_fatal")
        minimal = minimal_fatal_toggle_sets(9, pi)
        self.assertIn(tuple(selected), {tuple(s) for s in minimal})

    def test_v6_p3_trigger_takes_precedence(self):
        """When P3 fires, V6 returns P3 reason (chain-end trigger),
        not P4."""
        pi = (1, 3, 2, 4, 0, 5)  # k=6, S={0,1,2,3}, filler 5 above
        pred = predict_v6(6, pi, (0, 1, 2, 3))
        self.assertEqual(pred["prediction"], "minimal_fatal")
        self.assertEqual(pred["reason"], "P3_image_above")


if __name__ == "__main__":
    unittest.main()
