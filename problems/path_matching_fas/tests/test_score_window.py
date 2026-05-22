from __future__ import annotations

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from brute import decide  # noqa: E402
from lfo_score_window import (  # noqa: E402
    find_lfo_order_score_window,
    order_respects_windows,
    score_windows,
    window_profile,
)
from sweep import all_tournaments, canonical_key  # noqa: E402
from verify import verify  # noqa: E402

from test_path_fas import FOREST_NOT_PATH_FAS, LF_NOT_EXACT_PATH  # noqa: E402


class ScoreWindowSolverTest(unittest.TestCase):

    def test_window_solver_matches_pinned_yes_no_examples(self):
        yes = find_lfo_order_score_window(LF_NOT_EXACT_PATH)
        self.assertTrue(yes["found"])
        self.assertTrue(order_respects_windows(yes["order"], yes["windows"]))
        self.assertTrue(verify(LF_NOT_EXACT_PATH, yes["order"])["is_linear_forest"])

        no = find_lfo_order_score_window(FOREST_NOT_PATH_FAS)
        self.assertFalse(no["found"])
        self.assertGreater(no["nodes"], 0)

    def test_lfo_orders_respect_score_windows(self):
        brute = decide(LF_NOT_EXACT_PATH, "path_fas")
        self.assertTrue(brute["found"])
        windows = score_windows(LF_NOT_EXACT_PATH)
        self.assertTrue(order_respects_windows(brute["order"], windows))

    def test_window_profile_has_width_at_most_five(self):
        profile = window_profile(LF_NOT_EXACT_PATH)
        self.assertLessEqual(profile["max_width"], 5)
        self.assertTrue(profile["initial_hall"])

    def test_matches_bruteforce_on_nonisomorphic_tournaments_through_n5(self):
        for n in range(3, 6):
            seen = set()
            for T in all_tournaments(n):
                key = canonical_key(T)
                if key in seen:
                    continue
                seen.add(key)
                brute = decide(T, "path_fas")
                window = find_lfo_order_score_window(T)
                self.assertEqual(brute["found"], window["found"])
                if window["found"]:
                    self.assertTrue(verify(T, window["order"])["is_linear_forest"])


if __name__ == "__main__":
    unittest.main()
