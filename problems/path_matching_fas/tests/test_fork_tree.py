"""Regression tests for one-tree fork interfaces with crossing toggles.

The fork-tree probe refutes the loosened "acyclic interface" confluence
hypothesis.  The future dependency interface is a single tree in both
tests below.  Aligned branch toggles are uniformly extendable, but
cyclically shifted branch toggles have mixed extendability.
"""
import os
import sys
import unittest


SCRIPT_DIR = os.path.join(os.path.dirname(__file__), "..", "scripts")
sys.path.insert(0, os.path.abspath(SCRIPT_DIR))

from fork_tree_probe import (  # noqa: E402
    count_fork_tree_signatures,
    shift_pairing,
    shift_one_expected_counts,
    shift_one_predicted_extendable,
)


class ForkTreeProbeTest(unittest.TestCase):

    def test_aligned_fork_tree_is_uniformly_extendable(self):
        for k in range(3, 7):
            with self.subTest(k=k):
                out = count_fork_tree_signatures(k, tuple(range(k)))
                self.assertEqual(out["invalid"], 0)
                self.assertEqual(out["extendable"], 1 << k)
                self.assertEqual(out["non_extendable"], 0)
                self.assertEqual(out["distinct_sleeping_signatures"], 1 << k)

    def test_shifted_fork_tree_has_mixed_extendability(self):
        for k in range(3, 7):
            with self.subTest(k=k):
                out = count_fork_tree_signatures(k, shift_pairing(k, 1))
                self.assertEqual(out["invalid"], 0)
                self.assertGreater(out["extendable"], 0)
                self.assertGreater(out["non_extendable"], 0)
                self.assertEqual(out["distinct_sleeping_signatures"], 1 << k)

    def test_shifted_fork_tree_exact_k5_counts(self):
        out = count_fork_tree_signatures(5, shift_pairing(5, 1))
        self.assertEqual(out["extendable"], 18)
        self.assertEqual(out["non_extendable"], 14)
        self.assertEqual(out["distinct_sleeping_signatures"], 32)

    def test_shifted_fork_tree_forbidden_pair_classification(self):
        for k in range(3, 9):
            with self.subTest(k=k):
                out = count_fork_tree_signatures(k, shift_pairing(k, 1))
                expected = shift_one_expected_counts(k)
                self.assertEqual(out["extendable"], expected["extendable"])
                self.assertEqual(out["non_extendable"], expected["non_extendable"])
                for row in out["by_bits"]:
                    if row["status"] != "ok":
                        continue
                    predicted = shift_one_predicted_extendable(row["bits"])
                    self.assertEqual(
                        row["extendable"],
                        predicted,
                        msg=f"k={k}, row={row}, expected={expected}",
                    )


if __name__ == "__main__":
    unittest.main()
