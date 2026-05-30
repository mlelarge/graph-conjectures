"""Pin the exact degreewidth solver (Held-Karp DP) and the Q1/Q2 facts.

Run: python3 -m unittest tests/test_degreewidth_exact.py
"""
import itertools
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from degreewidth_exact import (  # noqa: E402
    degreewidth,
    degreewidth_le,
    degreewidth_order,
    is_degreewidth_le2,
)
from degreewidth_decomposition import max_backdeg  # noqa: E402


def all_tournaments(n):
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    for bits in itertools.product((0, 1), repeat=len(pairs)):
        T = [[0] * n for _ in range(n)]
        for (i, j), b in zip(pairs, bits):
            if b:
                T[i][j] = 1
            else:
                T[j][i] = 1
        yield T


def dw_fullscan(T):
    """Correct exact degreewidth by full permutation scan (oracle)."""
    n = len(T)
    if n <= 1:
        return 0
    return min(max_backdeg(T, p) for p in itertools.permutations(range(n)))


class TestDegreewidthExact(unittest.TestCase):
    def test_dp_matches_fullscan_exhaustive_n_le_6(self):
        """The Held-Karp DP equals the correct full-permutation-scan min on
        every labeled tournament n ≤ 6 (33,866 tournaments, 0 disagreements).
        Catches the old `<=1` early-exit bug (returned 1 instead of 0)."""
        for n in range(2, 7):
            for T in all_tournaments(n):
                self.assertEqual(degreewidth(T), dw_fullscan(T))

    def test_le_consistency(self):
        for n in range(2, 7):
            for T in all_tournaments(n):
                dw = degreewidth(T)
                self.assertEqual(is_degreewidth_le2(T), dw <= 2)
                self.assertEqual(degreewidth_le(T, 1), dw <= 1)
                self.assertEqual(degreewidth_le(T, 0), dw == 0)

    def test_order_reconstruction_achieves_value(self):
        import random

        rng = random.Random(20260530)
        for n in range(3, 11):
            for _ in range(200):
                T = [[0] * n for _ in range(n)]
                for i in range(n):
                    for j in range(i + 1, n):
                        if rng.random() < 0.5:
                            T[i][j] = 1
                        else:
                            T[j][i] = 1
                val, order = degreewidth_order(T)
                self.assertEqual(sorted(order), list(range(n)))
                self.assertEqual(max_backdeg(T, order), val)
                self.assertEqual(val, degreewidth(T))

    def test_first_last_vertex_necessary_conditions(self):
        """Identity bd(v)=i(v)+d⁻(v)−2b(v): first vertex back-degree = d⁻,
        last vertex back-degree = d⁺.  So Δ*≤2 ⇒ ∃ vertex with d⁻≤2 (a legal
        first) and ∃ vertex with d⁺≤2 (a legal last)."""
        import random

        rng = random.Random(11)
        for n in range(4, 10):
            for _ in range(300):
                T = [[0] * n for _ in range(n)]
                for i in range(n):
                    for j in range(i + 1, n):
                        if rng.random() < 0.5:
                            T[i][j] = 1
                        else:
                            T[j][i] = 1
                if is_degreewidth_le2(T):
                    dminus = [sum(T[u][v] for u in range(n)) for v in range(n)]
                    dplus = [sum(T[v][u] for u in range(n)) for v in range(n)]
                    self.assertTrue(min(dminus) <= 2)
                    self.assertTrue(min(dplus) <= 2)

    def test_path_fas_yes_implies_dw_le_2(self):
        """The load-bearing theorem: Path-FAS YES ⟹ Δ*≤2, on all n≤6."""
        from nonsweep_path_fas import decide_linear_forest_fas_bruteforce as lfo

        for n in range(3, 7):
            for T in all_tournaments(n):
                if lfo(T):
                    self.assertLessEqual(degreewidth(T), 2)


if __name__ == "__main__":
    unittest.main()
