"""Tests for the non-sweep Path-FAS formulations.

Ground truth is `scripts/path_fas.py::decide_path_fas_bruteforce`.  We check:

  * the linear-forest-FAS reformulation agrees with the brute-force decider
    on all small tournaments (exhaustive n<=5, random n=6,7, certified
    minimal-NO n=7);
  * the exact cutting-plane ILP (directed-cycle + undirected-cycle cuts +
    degree<=2) is a correct decision oracle, including on the certified
    minimal-NO instances where the *relaxed* (triangle-only / degree-only)
    model gives false positives;
  * the documented obstructions (non-matroid acyclic system; relaxation gap)
    are reproduced as concrete witnesses.
"""
from __future__ import annotations

import itertools
import json
import os
import random
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from nonsweep_path_fas import (  # noqa: E402
    arcs_of,
    decide_linear_forest_fas_bruteforce,
    ilp_exact_linear_forest_fas,
    ilp_linear_forest_fas_feasible,
    is_acyclic,
    underlying_is_linear_forest,
)
from path_fas import decide_path_fas_bruteforce  # noqa: E402

DATA = os.path.join(os.path.dirname(__file__), "..", "data")


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


def random_tournament(n, seed):
    rng = random.Random(seed)
    T = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            if rng.random() < 0.5:
                T[i][j] = 1
            else:
                T[j][i] = 1
    return T


class ReformulationTest(unittest.TestCase):
    def test_lf_fas_equals_pathfas_exhaustive_small(self):
        for n in range(2, 6):
            for T in all_tournaments(n):
                self.assertEqual(
                    decide_linear_forest_fas_bruteforce(T),
                    decide_path_fas_bruteforce(T)["found"],
                    msg=f"mismatch on n={n} T={T}",
                )

    def test_lf_fas_equals_pathfas_random(self):
        for n in (6, 7):
            for seed in range(12):
                T = random_tournament(n, seed)
                self.assertEqual(
                    decide_linear_forest_fas_bruteforce(T),
                    decide_path_fas_bruteforce(T)["found"],
                    msg=f"mismatch n={n} seed={seed}",
                )


class ExactIlpTest(unittest.TestCase):
    def test_exact_ilp_random(self):
        for n in range(3, 8):
            for seed in range(8):
                T = random_tournament(n, seed)
                bf = decide_linear_forest_fas_bruteforce(T)
                ex = ilp_exact_linear_forest_fas(T, max_rounds=60)
                self.assertEqual(ex["feasible"], bf,
                                 msg=f"exact ILP mismatch n={n} seed={seed}")

    def test_exact_ilp_on_certified_minimal_no(self):
        recs = json.load(
            open(os.path.join(DATA, "minimal_no_obstruction_catalogue_n7.json"))
        )["records"]
        # Use a subset for speed; every one of these is a certified NO.
        for r in recs[:8]:
            T = r["T"]
            self.assertFalse(decide_linear_forest_fas_bruteforce(T))
            ex = ilp_exact_linear_forest_fas(T, max_rounds=80)
            self.assertFalse(ex["feasible"],
                             msg=f"exact ILP false-positive on NO {r['name']}")


class ObstructionWitnessTest(unittest.TestCase):
    def test_relaxation_gap_witness(self):
        """The triangle+degree relaxation is NOT a sound model: it can be
        feasible with an integer point that is not a linear-forest FAS,
        because degree<=2 permits an undirected cycle in S."""
        recs = json.load(
            open(os.path.join(DATA, "minimal_no_obstruction_catalogue_n7.json"))
        )["records"]
        T = recs[0]["T"]  # certified NO
        self.assertFalse(decide_linear_forest_fas_bruteforce(T))
        rel = ilp_linear_forest_fas_feasible(T)
        # relaxed model is feasible (false positive) but the integer point is
        # not a genuine FAS.
        self.assertTrue(rel["ilp_feasible"])
        self.assertFalse(rel["genuine"])

    def test_acyclic_system_not_matroid_witness(self):
        """Minimal n=4 tournament whose acyclic-subgraph independence system
        violates the matroid exchange axiom."""
        T = [[0, 0, 0, 1], [1, 0, 0, 0], [1, 1, 0, 0], [0, 1, 1, 0]]
        arcs = arcs_of(T)
        # I and J are both acyclic, |I| < |J|, no extension of I from J.
        I = [(0, 3), (1, 0), (2, 0)]
        J = [(1, 0), (2, 0), (3, 1), (3, 2)]
        self.assertTrue(is_acyclic(4, I))
        self.assertTrue(is_acyclic(4, J))
        self.assertLess(len(I), len(J))
        extendable = any(is_acyclic(4, set(I) | {e}) for e in set(J) - set(I))
        self.assertFalse(extendable, "exchange axiom unexpectedly satisfied")

    def test_degree_constraint_alone_allows_undirected_cycle(self):
        """The 4-cycle 3-1-4-2-3 is degree-<=2 and (as a digraph) the kept
        complement is acyclic, yet it is not a linear forest."""
        T = json.load(
            open(os.path.join(DATA, "minimal_no_obstruction_catalogue_n7.json"))
        )["records"][0]["T"]
        S = [(0, 6), (3, 1), (3, 2), (4, 1), (4, 2), (6, 5)]
        n = len(T)
        # every vertex has degree <= 2 in S, and T - S is a (directed) DAG ...
        self.assertTrue(is_acyclic(n, set(arcs_of(T)) - set(S)))
        # ... but S is NOT a linear forest (undirected 4-cycle 3-1-4-2-3).
        self.assertFalse(underlying_is_linear_forest(S))


if __name__ == "__main__":
    unittest.main()
