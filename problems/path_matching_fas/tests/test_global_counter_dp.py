"""Tests for the global-counter DP variants.

We probe three variants of the J-pathwidth DP where the per-bag
partition component of the state is replaced by progressively richer
global counters.  See `docs/global_counter_dp.md`.

Variant A: drop `comp` entirely (no cycle detection).
  Predicted to over-accept: a tournament whose loaded back-arc graph
  has max degree 2 but a 2-regular component (cycle) is wrongly YES.

Variant B: replace `comp` by global counters (num_open_paths,
  num_deg1_bag), keep an auxiliary union-find on each state value.
  Lossy: only one value per key.  Empirically sound on n <= 9 random
  + n <= 6 exhaustive + n=7 minimal NOs, but not theoretically proved.

Variant C: keep partition restricted to bag vertices only, with
  smallest-bag-vertex representative labels.  Equivalent to the full
  DP (sanity check).

The tests therefore check:
- A *fails* on n=7 minimal NO (expected -- over-accepts cycles).
- B and C agree with brute force on n in {3, 4, 5} exhaustive and
  small random n=6,7.
- B and C agree with `path_fas_J_pathwidth_dp` on a battery of small
  random instances and skew tournaments.
"""
from __future__ import annotations

import itertools
import os
import random
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from J_pathwidth_dp import path_fas_J_pathwidth_dp  # noqa: E402
from global_counter_dp_probe import (  # noqa: E402
    path_fas_variant_A,
    path_fas_variant_B,
    path_fas_variant_C,
)
from path_fas import decide_path_fas_bruteforce  # noqa: E402


def all_tournaments(n):
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    for bits in itertools.product([0, 1], repeat=len(pairs)):
        T = [[0] * n for _ in range(n)]
        for (i, j), b in zip(pairs, bits):
            if b:
                T[i][j] = 1
            else:
                T[j][i] = 1
        yield T


def random_tournament(n, rng):
    T = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            if rng.random() < 0.5:
                T[i][j] = 1
            else:
                T[j][i] = 1
    return T


def random_skew(n, num_flips, rng):
    T = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            T[i][j] = 1
    arcs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    rng.shuffle(arcs)
    for i, j in arcs[:num_flips]:
        T[i][j] = 0
        T[j][i] = 1
    return T


class VariantATests(unittest.TestCase):
    """Variant A drops cycle detection — expected to fail on some NOs."""

    def test_a_collides_on_some_n7_minimal_no(self):
        """Variant A wrongly accepts ≥ 1 NO instance at n=7."""
        import json
        path = os.path.join(
            os.path.dirname(__file__), "..", "data",
            "minimal_no_obstruction_catalogue_n7.json",
        )
        if not os.path.exists(path):
            self.skipTest("minimal NO catalogue not available")
        with open(path) as f:
            d = json.load(f)
        wrong = 0
        for r in d["records"]:
            T = r["T"]
            if path_fas_variant_A(T):
                wrong += 1
        # We expect strictly positive wrong-count, as Variant A drops cycles.
        self.assertGreater(
            wrong, 0,
            "Variant A should over-accept ≥ 1 of the n=7 minimal NO instances",
        )

    def test_a_matches_on_n5_exhaustive(self):
        """Variant A happens to match on n=5 because cycles can't form in
        score-window-respecting LFOs at this size.
        """
        for T in all_tournaments(5):
            self.assertEqual(
                path_fas_variant_A(T),
                decide_path_fas_bruteforce(T)["found"],
            )


class VariantBTests(unittest.TestCase):
    """Variant B uses global counters + auxiliary union-find with lossy
    key collapse. Empirically correct on our test suite.
    """

    def test_b_n3_exhaustive(self):
        for T in all_tournaments(3):
            self.assertEqual(
                path_fas_variant_B(T),
                decide_path_fas_bruteforce(T)["found"],
            )

    def test_b_n4_exhaustive(self):
        for T in all_tournaments(4):
            self.assertEqual(
                path_fas_variant_B(T),
                decide_path_fas_bruteforce(T)["found"],
            )

    def test_b_n5_exhaustive(self):
        mismatches = []
        for T in all_tournaments(5):
            if path_fas_variant_B(T) != decide_path_fas_bruteforce(T)["found"]:
                mismatches.append(T)
        self.assertEqual(mismatches, [], f"{len(mismatches)} mismatches at n=5")

    def test_b_n6_random(self):
        rng = random.Random(20260527)
        for _ in range(300):
            T = random_tournament(6, rng)
            self.assertEqual(
                path_fas_variant_B(T),
                decide_path_fas_bruteforce(T)["found"],
            )

    def test_b_random_skew_n8(self):
        rng = random.Random(20260527)
        for _ in range(50):
            T = random_skew(8, 5, rng)
            self.assertEqual(
                path_fas_variant_B(T),
                path_fas_J_pathwidth_dp(T),
                msg=f"Variant B vs full DP differ on T={T}",
            )

    def test_b_n7_minimal_no(self):
        """All n=7 minimal NO instances must still be NO under Variant B."""
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
            self.assertFalse(
                path_fas_variant_B(T),
                msg=f"Variant B wrongly accepts n=7 NO {r['name']}",
            )


class VariantCTests(unittest.TestCase):
    """Variant C keeps bag-vertex-only partition; should match full DP."""

    def test_c_n3_exhaustive(self):
        for T in all_tournaments(3):
            self.assertEqual(
                path_fas_variant_C(T),
                decide_path_fas_bruteforce(T)["found"],
            )

    def test_c_n4_exhaustive(self):
        for T in all_tournaments(4):
            self.assertEqual(
                path_fas_variant_C(T),
                decide_path_fas_bruteforce(T)["found"],
            )

    def test_c_n5_exhaustive(self):
        mismatches = []
        for T in all_tournaments(5):
            if path_fas_variant_C(T) != decide_path_fas_bruteforce(T)["found"]:
                mismatches.append(T)
        self.assertEqual(mismatches, [], f"{len(mismatches)} mismatches at n=5")

    def test_c_n6_random(self):
        rng = random.Random(20260527)
        for _ in range(200):
            T = random_tournament(6, rng)
            self.assertEqual(
                path_fas_variant_C(T),
                decide_path_fas_bruteforce(T)["found"],
            )

    def test_c_n7_minimal_no(self):
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
            self.assertFalse(
                path_fas_variant_C(T),
                msg=f"Variant C wrongly accepts n=7 NO {r['name']}",
            )


if __name__ == "__main__":
    unittest.main()
