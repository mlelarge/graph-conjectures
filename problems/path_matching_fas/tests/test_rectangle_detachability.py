"""Regression tests for suffix-walk detachability on fork-tree pairings."""
import os
import sys
import unittest


SCRIPT_DIR = os.path.join(os.path.dirname(__file__), "..", "scripts")
sys.path.insert(0, os.path.abspath(SCRIPT_DIR))

from rectangle_detachability_probe import (  # noqa: E402
    anchored_alternating_ladder_sets,
    all_pairings_summary,
    evaluate_pairing,
    find_completion_suffix,
    fork_prefix_state,
    minimal_fatal_toggle_sets,
    two_interval_ladder_sets,
)


class RectangleDetachabilityProbeTest(unittest.TestCase):

    def test_cyclic_shift_k5_has_only_fatal_pairs(self):
        pi = (1, 2, 3, 4, 0)
        self.assertEqual(
            sorted(minimal_fatal_toggle_sets(5, pi)),
            [(0, 1), (2, 3)],
        )
        out = evaluate_pairing(5, pi)
        self.assertEqual(out["higher_order_minimal_fatal_sets"], [])

    def test_k5_pair_only_detector_is_false(self):
        """There are pairings with no fatal two-toggle set but a minimal
        four-toggle fatal set.  This kills the pair-only V2 target."""
        pi = (1, 3, 2, 4, 0)
        out = evaluate_pairing(5, pi)
        self.assertEqual(out["fatal_pairs"], [])
        self.assertEqual(out["higher_order_minimal_fatal_sets"], [[0, 1, 2, 3]])

    def test_higher_order_example_has_pair_suffix_certificate(self):
        """Every pair in the k=5 higher-order example is detachable:
        the suffix-walk probe returns an explicit completion."""
        pi = (1, 3, 2, 4, 0)
        setup = fork_prefix_state(5, pi, (0, 1))
        self.assertIsNotNone(setup)
        T, cut, state = setup
        cert = find_completion_suffix(T, cut, state)
        self.assertTrue(cert["detachable"])
        self.assertIsNotNone(cert["suffix"])

    def test_k4_has_no_higher_order_minimal_fatal_sets(self):
        out = all_pairings_summary(4)
        self.assertEqual(out["total_pairings"], 24)
        self.assertEqual(out["pairings_with_higher_order_fatal_set"], 0)

    def test_k5_has_higher_order_minimal_fatal_sets(self):
        out = all_pairings_summary(5)
        self.assertEqual(out["total_pairings"], 120)
        self.assertEqual(out["pairings_with_higher_order_fatal_set"], 16)

    def test_k5_higher_order_sets_are_exactly_anchored_ladders(self):
        out = all_pairings_summary(5)
        self.assertEqual(out["anchored_ladder_mismatches"], 0)

    def test_k6_representative_anchored_ladders(self):
        examples = [
            ((1, 3, 2, 4, 0, 5), [(0, 1, 2, 3)]),
            ((1, 3, 0, 5, 2, 4), [(0, 1, 4, 5)]),
            ((0, 5, 1, 3, 2, 4), [(2, 3, 4, 5)]),
        ]
        for pi, expected in examples:
            with self.subTest(pi=pi):
                self.assertEqual(anchored_alternating_ladder_sets(6, pi), expected)
                actual = [
                    s for s in minimal_fatal_toggle_sets(6, pi)
                    if len(s) > 2
                ]
                self.assertEqual(actual, expected)

    def test_interleaving_without_anchor_is_not_fatal(self):
        pi = (0, 2, 1, 3, 4)
        self.assertEqual(anchored_alternating_ladder_sets(5, pi), [])
        self.assertEqual(
            [s for s in minimal_fatal_toggle_sets(5, pi) if len(s) > 2],
            [],
        )

    def test_k7_size_six_ladder_refutes_four_ladder_completeness(self):
        pi = (5, 4, 6, 1, 3, 2, 0)
        self.assertEqual(anchored_alternating_ladder_sets(7, pi), [])
        self.assertEqual(
            [s for s in minimal_fatal_toggle_sets(7, pi) if len(s) > 2],
            [(0, 1, 2, 3, 4, 5)],
        )

    def test_k7_non_initial_four_ladder_is_real(self):
        pi = (3, 5, 4, 6, 1, 2, 0)
        self.assertEqual(anchored_alternating_ladder_sets(7, pi), [])
        self.assertEqual(two_interval_ladder_sets(7, pi), [(0, 1, 2, 3)])
        self.assertEqual(
            [s for s in minimal_fatal_toggle_sets(7, pi) if len(s) > 2],
            [(0, 1, 2, 3)],
        )

    def test_two_interval_ladder_overpredicts_without_order_condition(self):
        pi = (0, 1, 2, 4, 3, 5)
        self.assertEqual(two_interval_ladder_sets(6, pi), [(2, 3, 4, 5)])
        self.assertEqual(
            [s for s in minimal_fatal_toggle_sets(6, pi) if len(s) > 2],
            [],
        )


if __name__ == "__main__":
    unittest.main()
