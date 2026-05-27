"""Tests for forced-frontier diagnostics."""

from __future__ import annotations

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))

from forced_frontier_probe import (  # noqa: E402
    forced_frontier_profile,
    random_skew_tournament,
    reversed_matching_tournament,
    transitive_tournament,
)


class ForcedFrontierProbeTests(unittest.TestCase):

    def test_transitive_has_no_forced_frontier(self) -> None:
        rep = forced_frontier_profile(transitive_tournament(9))
        self.assertTrue(rep.hall_ok)
        self.assertEqual(rep.h_edges, 0)
        self.assertEqual(rep.max_live_h_components, 0)
        self.assertEqual(rep.max_compressed_frontier_size, rep.max_active_count)

    def test_reversed_matching_frontier_is_bounded_by_blunt_endpoint_bag(self) -> None:
        rep = forced_frontier_profile(reversed_matching_tournament(10))
        self.assertTrue(rep.hall_ok)
        self.assertGreater(rep.h_edges, 0)
        self.assertLessEqual(rep.max_active_count, 9)
        self.assertLessEqual(
            rep.max_compressed_frontier_size,
            rep.max_blunt_endpoint_bag_size,
        )

    def test_random_skew_report_has_consistent_cut_counts(self) -> None:
        T = random_skew_tournament(24, 3, seed=20260527)
        rep = forced_frontier_profile(T)
        self.assertEqual(len(rep.cuts), 24)
        for cut in rep.cuts:
            with self.subTest(position=cut.position):
                self.assertEqual(cut.closed_count + cut.active_count + cut.future_count, 24)
                self.assertGreaterEqual(cut.crossing_h_endpoints, cut.crossing_h_edges > 0)
                self.assertEqual(
                    cut.compressed_frontier_size,
                    cut.active_count + 2 * cut.live_h_components,
                )


if __name__ == "__main__":
    unittest.main()
