from __future__ import annotations

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from brute import decide  # noqa: E402
from lfo_backtrack import find_lfo_order  # noqa: E402
from path_fas import (  # noqa: E402
    complete_backarc_linear_forest_to_path_fas,
    decide_path_fas_bruteforce,
    verify_path_fas_certificate,
)
from verify import verify  # noqa: E402


# Formal Path-FAS YES, but exact connected path back-arc graph NO.
LF_NOT_EXACT_PATH = [
    [0, 0, 1, 1, 0, 1, 1],
    [1, 0, 1, 0, 1, 1, 1],
    [0, 0, 0, 1, 0, 0, 1],
    [0, 1, 0, 0, 1, 0, 0],
    [1, 0, 1, 0, 0, 1, 1],
    [0, 0, 1, 1, 0, 0, 0],
    [0, 0, 0, 1, 0, 1, 0],
]
LF_ORDER = [1, 0, 4, 2, 5, 6, 3]


# Forest-FAS YES, but formal Path-FAS NO.
FOREST_NOT_PATH_FAS = [
    [0, 0, 1, 0, 1, 1, 1],
    [1, 0, 0, 0, 1, 1, 1],
    [0, 1, 0, 0, 1, 1, 0],
    [1, 1, 1, 0, 0, 0, 0],
    [0, 0, 0, 1, 0, 1, 0],
    [0, 0, 0, 1, 0, 0, 1],
    [0, 0, 1, 1, 1, 0, 0],
]


class PathFasFormalizationTest(unittest.TestCase):

    def test_formal_path_fas_is_linear_forest_not_exact_path(self):
        exact = decide(LF_NOT_EXACT_PATH, "path")
        formal = decide(LF_NOT_EXACT_PATH, "path_fas")
        linear = decide(LF_NOT_EXACT_PATH, "linear_forest")
        self.assertFalse(exact["found"])
        self.assertTrue(formal["found"])
        self.assertEqual(formal["found"], linear["found"])

    def test_linear_forest_order_completes_to_path_fas(self):
        info = verify(LF_NOT_EXACT_PATH, LF_ORDER)
        self.assertTrue(info["is_linear_forest"])
        self.assertFalse(info["is_path"])

        F = complete_backarc_linear_forest_to_path_fas(LF_NOT_EXACT_PATH, LF_ORDER)
        self.assertTrue(verify_path_fas_certificate(LF_NOT_EXACT_PATH, F))
        self.assertGreaterEqual(set(F), set(info["arcs"]))

    def test_forest_ordering_does_not_imply_path_fas(self):
        forest = decide(FOREST_NOT_PATH_FAS, "forest")
        formal = decide(FOREST_NOT_PATH_FAS, "path_fas")
        self.assertTrue(forest["found"])
        self.assertFalse(formal["found"])

    def test_bruteforce_returns_actual_path_fas_certificate(self):
        result = decide_path_fas_bruteforce(LF_NOT_EXACT_PATH)
        self.assertTrue(result["found"])
        self.assertTrue(verify_path_fas_certificate(
            LF_NOT_EXACT_PATH,
            result["path_fas"],
        ))

    def test_pruned_lfo_backtracker_matches_pinned_examples(self):
        yes = find_lfo_order(LF_NOT_EXACT_PATH)
        self.assertTrue(yes["found"])
        self.assertTrue(verify(LF_NOT_EXACT_PATH, yes["order"])["is_linear_forest"])

        no = find_lfo_order(FOREST_NOT_PATH_FAS)
        self.assertFalse(no["found"])


if __name__ == "__main__":
    unittest.main()
