"""Regression tests for the three-interval internal-gap P4 probe."""
import os
import sys
import unittest


SCRIPT_DIR = os.path.join(os.path.dirname(__file__), "..", "scripts")
sys.path.insert(0, os.path.abspath(SCRIPT_DIR))

from internal_gap_probe import residual_internal_gap_rows  # noqa: E402


class InternalGapProbeTest(unittest.TestCase):

    def test_residual_rows_classify_p4_counterexample(self):
        pi = (4, 0, 2, 8, 6, 1, 7, 5, 3)
        rows = residual_internal_gap_rows(9, pi)
        target = next(row for row in rows if row["selected"] == [2, 3, 4, 5, 6, 7])
        self.assertTrue(target["natural_odd_pairs"])
        self.assertTrue(target["predicted_minimal"])
        self.assertTrue(target["actual_minimal"])
        self.assertTrue(target["correct"])

    def test_residual_rows_classify_misaligned_detachable(self):
        pi = (0, 3, 1, 4, 2, 6, 5, 7)
        rows = residual_internal_gap_rows(8, pi)
        target = next(row for row in rows if row["selected"] == [2, 3, 4, 5, 6, 7])
        self.assertFalse(target["natural_odd_pairs"])
        self.assertFalse(target["predicted_minimal"])
        self.assertFalse(target["actual_minimal"])
        self.assertTrue(target["correct"])


if __name__ == "__main__":
    unittest.main()
