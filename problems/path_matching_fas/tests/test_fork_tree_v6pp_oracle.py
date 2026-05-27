"""Regression tests for the V6'' separation oracle."""
from __future__ import annotations

import os
import sys
import unittest
from itertools import permutations, product


SCRIPT_DIR = os.path.join(os.path.dirname(__file__), "..", "scripts")
sys.path.insert(0, os.path.abspath(SCRIPT_DIR))

from fork_tree_v6pp_oracle import (  # noqa: E402
    assignment_extendable_v6pp,
    brute_force_v6pp_positive_core_exists,
    find_v6pp_positive_core,
)


class V6PPSeparationOracleTest(unittest.TestCase):

    def _assert_matches_brute(self, k: int) -> None:
        mismatches = []
        for pi in permutations(range(k)):
            for eps in product((0, 1), repeat=k):
                oracle = find_v6pp_positive_core(k, pi, eps)
                brute = brute_force_v6pp_positive_core_exists(k, pi, eps)
                if (oracle is not None) != brute["exists"]:
                    mismatches.append({
                        "pi": pi,
                        "eps": eps,
                        "oracle": oracle,
                        "brute": brute,
                    })
                    return
        self.assertEqual(mismatches, [])

    def test_exhaustive_k2_to_k5_matches_candidate_enumeration(self):
        for k in range(2, 6):
            with self.subTest(k=k):
                self._assert_matches_brute(k)

    def test_k6_sample_matches_candidate_enumeration(self):
        samples = [
            (0, 1, 2, 3, 4, 5),
            (1, 2, 3, 4, 5, 0),
            (5, 4, 3, 2, 1, 0),
            (2, 4, 1, 5, 0, 3),
        ]
        for pi in samples:
            for eps in product((0, 1), repeat=6):
                oracle = find_v6pp_positive_core(6, pi, eps)
                brute = brute_force_v6pp_positive_core_exists(6, pi, eps)
                self.assertEqual(oracle is not None, brute["exists"], (pi, eps, oracle, brute))

    def test_v6_failure_case_is_not_false_positive(self):
        pi = (5, 3, 2, 6, 4, 0, 1)
        eps = (1, 1, 1, 1, 0, 0, 0)
        out = assignment_extendable_v6pp(7, pi, eps)
        self.assertTrue(out["extendable"])
        self.assertIsNone(out["forbidden_core"])

    def test_k7_cyclic_shift_finds_size2_core(self):
        pi = (1, 2, 3, 4, 5, 6, 0)
        eps = (1, 1, 0, 0, 0, 0, 0)
        out = assignment_extendable_v6pp(7, pi, eps)
        self.assertFalse(out["extendable"])
        self.assertEqual(out["forbidden_core"]["kind"], "single_block")
        self.assertEqual(out["forbidden_core"]["support"], [0, 1])

    def test_k9_internal_gap_p4_core_detected(self):
        pi = (4, 0, 2, 8, 6, 1, 7, 5, 3)
        eps = tuple(1 if i in {2, 3, 4, 5, 6, 7} else 0 for i in range(9))
        out = assignment_extendable_v6pp(9, pi, eps)
        self.assertFalse(out["extendable"])
        self.assertEqual(out["forbidden_core"]["kind"], "P4_natural_odd_cycle")
        self.assertEqual(out["forbidden_core"]["support"], [2, 3, 4, 5, 6, 7])


if __name__ == "__main__":
    unittest.main()
