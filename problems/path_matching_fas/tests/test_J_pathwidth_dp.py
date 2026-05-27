"""Correctness tests for the J-pathwidth DP.

Coverage:
- exhaustive: all tournaments at n in {3, 4, 5, 6}.
- random samples at n in {7, 8, 9} against brute force.
- the 20 documented vertex-minimal n=7 LFO NO instances
  (`data/minimal_no_obstruction_catalogue_n7.json`).
- the three documented n=12 skew templates from
  `scripts/sleeping_block_skew_sweep.py` against the exact
  forced/flexible solver (BF is too slow at n=12).

All tests pass without mismatch.  See `docs/J_pathwidth_dp.md`.
"""
from __future__ import annotations

import itertools
import os
import random
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from J_pathwidth_dp import (  # noqa: E402
    J_graph,
    nice_path_decomposition,
    path_fas_J_pathwidth_dp,
)
from lfo_forced_flexible import find_lfo_order_forced_flexible  # noqa: E402
from path_fas import decide_path_fas_bruteforce  # noqa: E402
from sleeping_block_skew_sweep import SKEW_TEMPLATES  # noqa: E402


def all_tournaments(n: int):
    """Iterate every n x n tournament matrix."""
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    for bits in itertools.product([0, 1], repeat=len(pairs)):
        T = [[0] * n for _ in range(n)]
        for (i, j), b in zip(pairs, bits):
            if b:
                T[i][j] = 1
            else:
                T[j][i] = 1
        yield T


def random_tournament(n: int, rng: random.Random):
    T = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            if rng.random() < 0.5:
                T[i][j] = 1
            else:
                T[j][i] = 1
    return T


class JPathwidthDPCorrectnessTest(unittest.TestCase):

    def _check(self, T):
        dp = path_fas_J_pathwidth_dp(T)
        bf = decide_path_fas_bruteforce(T)["found"]
        return dp, bf

    def test_exhaustive_n3(self):
        for T in all_tournaments(3):
            dp, bf = self._check(T)
            self.assertEqual(dp, bf, msg=f"DP disagrees on T={T}")

    def test_exhaustive_n4(self):
        for T in all_tournaments(4):
            dp, bf = self._check(T)
            self.assertEqual(dp, bf, msg=f"DP disagrees on T={T}")

    def test_exhaustive_n5(self):
        mismatches = []
        for T in all_tournaments(5):
            dp, bf = self._check(T)
            if dp != bf:
                mismatches.append((T, dp, bf))
        self.assertEqual(mismatches, [], msg=f"{len(mismatches)} mismatches at n=5")

    def test_exhaustive_n6(self):
        # n=6 has 2^15 = 32768 tournaments; ~few seconds with this DP.
        mismatches = []
        for T in all_tournaments(6):
            dp, bf = self._check(T)
            if dp != bf:
                mismatches.append((T, dp, bf))
        self.assertEqual(
            mismatches,
            [],
            msg=f"{len(mismatches)} mismatches at n=6; first={mismatches[:3]}",
        )

    def test_random_n7(self):
        rng = random.Random(20260527)
        mismatches = []
        for _ in range(200):
            T = random_tournament(7, rng)
            dp, bf = self._check(T)
            if dp != bf:
                mismatches.append((T, dp, bf))
        self.assertEqual(
            mismatches,
            [],
            msg=f"{len(mismatches)}/200 mismatches at n=7; first={mismatches[:3]}",
        )

    def test_random_n8(self):
        rng = random.Random(20260527)
        mismatches = []
        for _ in range(100):
            T = random_tournament(8, rng)
            dp, bf = self._check(T)
            if dp != bf:
                mismatches.append((T, dp, bf))
        self.assertEqual(
            mismatches,
            [],
            msg=f"{len(mismatches)}/100 mismatches at n=8; first={mismatches[:3]}",
        )

    def test_random_n9(self):
        rng = random.Random(20260527)
        mismatches = []
        for _ in range(30):
            T = random_tournament(9, rng)
            dp, bf = self._check(T)
            if dp != bf:
                mismatches.append((T, dp, bf))
        self.assertEqual(
            mismatches,
            [],
            msg=f"{len(mismatches)}/30 mismatches at n=9; first={mismatches[:3]}",
        )

    def test_n12_skew_templates_match_ff_solver(self):
        """Brute force is too slow at n=12 (12! ~= 479M); compare against
        the exact `find_lfo_order_forced_flexible` solver instead.

        Expected from `docs/exchange_proof_draft.md` Section 14.2:
            one_block: YES, skew_induction: NO, wake1_failure: YES.
        """
        for name, T in SKEW_TEMPLATES.items():
            dp = path_fas_J_pathwidth_dp(T)
            ff = find_lfo_order_forced_flexible(T)["found"]
            self.assertEqual(dp, ff, msg=f"DP/FF disagree on {name}: DP={dp} FF={ff}")

    def test_n7_minimal_NO_instances(self):
        """All 20 documented n=7 LFO-NO instances must be classified as NO."""
        import json
        path = os.path.join(
            os.path.dirname(__file__), "..", "data",
            "minimal_no_obstruction_catalogue_n7.json",
        )
        if not os.path.exists(path):
            self.skipTest("minimal NO catalogue not available")
        with open(path) as f:
            d = json.load(f)
        for r in d["records"]:
            T = r["T"]
            dp = path_fas_J_pathwidth_dp(T)
            self.assertFalse(dp, msg=f"DP incorrectly says YES on n=7 NO {r['name']}")


if __name__ == "__main__":
    unittest.main()
