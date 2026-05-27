"""Smoke tests for the J-construction in scripts/interaction_graph.py."""

from __future__ import annotations

import os
import sys
import unittest

import networkx as nx

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))

from interaction_graph import (  # noqa: E402
    build_H_and_Gflex,
    build_J,
    flex_treewidth_bound_from_hall,
    forced_pair_orientation,
    hall_feasible,
    is_H_linear_forest,
    max_active_window_count,
    measure,
    refined_pathwidth_bound,
    refined_treewidth_bound,
    score_window,
    score_windows,
    treewidth_upper_bound,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def transitive(n: int) -> list[list[int]]:
    T = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            T[i][j] = 1
    return T


def reversed_matching(m: int) -> list[list[int]]:
    """2m-vertex tournament: transitive, then reverse arcs (i, i+m) for i<m."""
    n = 2 * m
    T = transitive(n)
    for i in range(m):
        T[i][i + m] = 0
        T[i + m][i] = 1
    return T


# ---------------------------------------------------------------------------
# Score window tests
# ---------------------------------------------------------------------------

class ScoreWindowTests(unittest.TestCase):

    def test_transitive_indegrees_match_position(self) -> None:
        T = transitive(7)
        for v in range(7):
            lo, hi = score_window(T, v)
            self.assertEqual(lo, max(0, v - 2))
            self.assertEqual(hi, min(6, v + 2))

    def test_score_windows_clipped_to_range(self) -> None:
        T = transitive(5)
        windows = score_windows(T)
        for lo, hi in windows:
            self.assertGreaterEqual(lo, 0)
            self.assertLessEqual(hi, 4)


# ---------------------------------------------------------------------------
# Forced / flexible classification
# ---------------------------------------------------------------------------

class ForcedFlexibleTests(unittest.TestCase):

    def test_transitive_small_all_flexible(self) -> None:
        """At n <= 5, transitive windows all overlap [0,4], so every pair
        is flexible."""
        T = transitive(5)
        for u in range(5):
            for v in range(u + 1, 5):
                self.assertEqual(forced_pair_orientation(T, u, v), "flexible")

    def test_reversed_matching_forced_pairs(self) -> None:
        """In the m=10 reversed matching, the matching pairs {i, i+10}
        have disjoint windows (indegrees ~i+1 vs ~i+9, gap ≥ 5 for i=0)."""
        T = reversed_matching(10)
        # vertex 0 has indegree 1 (only from vertex 10)
        # vertex 10 has indegree 9 (transitive arcs from {1..9})
        # window(0) = [0, 3], window(10) = [7, 11]; disjoint!
        self.assertEqual(forced_pair_orientation(T, 0, 10),
                         "forced_u_before_v")

    def test_self_pair_classified_flexible(self) -> None:
        """A vertex's window trivially overlaps itself."""
        T = reversed_matching(5)
        for v in range(len(T)):
            self.assertEqual(forced_pair_orientation(T, v, v), "flexible")


# ---------------------------------------------------------------------------
# H and Gflex construction
# ---------------------------------------------------------------------------

class HAndGflexTests(unittest.TestCase):

    def test_transitive_H_empty(self) -> None:
        """Transitive small case: all pairs flexible, so H has no edges
        and G_flex is complete K_n."""
        T = transitive(5)
        H, Gflex = build_H_and_Gflex(T)
        self.assertEqual(H.number_of_edges(), 0)
        # all 10 undirected pairs
        self.assertEqual(Gflex.number_of_edges(), 10)

    def test_reversed_matching_H_is_matching(self) -> None:
        """In reversed_matching m=15: each pair {i, i+m} contributes one
        forced backedge (i+m -> i)."""
        m = 15
        T = reversed_matching(m)
        H, _ = build_H_and_Gflex(T)
        # Each H-edge {i, i+m} should be a forced backedge
        H_undirected = H.to_undirected()
        # |H| equals the number of disjoint matching pairs, which is m
        # but only those whose windows are truly disjoint.
        for i in range(m):
            d_i = sum(T[u][i] for u in range(2 * m))
            d_im = sum(T[u][i + m] for u in range(2 * m))
            lo_i, hi_i = max(0, d_i - 2), min(2 * m - 1, d_i + 2)
            lo_im, hi_im = max(0, d_im - 2), min(2 * m - 1, d_im + 2)
            disjoint = (hi_i < lo_im) or (hi_im < lo_i)
            if disjoint:
                self.assertTrue(H_undirected.has_edge(i, i + m),
                                f"missing H-edge {{{i}, {i + m}}}")

    def test_H_is_linear_forest_for_reversed_matching(self) -> None:
        T = reversed_matching(20)
        H, _ = build_H_and_Gflex(T)
        self.assertTrue(is_H_linear_forest(H))


# ---------------------------------------------------------------------------
# Hall feasibility
# ---------------------------------------------------------------------------

class HallTests(unittest.TestCase):

    def test_transitive_passes(self) -> None:
        self.assertTrue(hall_feasible(transitive(7)))

    def test_reversed_matching_passes(self) -> None:
        self.assertTrue(hall_feasible(reversed_matching(15)))

    def test_known_hall_failure(self) -> None:
        """Two vertices with disjoint windows but only one position
        between."""
        # Make a tournament where many vertices share indegree 0:
        # take regular near-regular Paley-7-like (all indegrees = 3).
        # Then all 7 windows = [1, 5]: 7 vertices fighting over 5 positions.
        n = 7
        T = [[0] * n for _ in range(n)]
        # Paley-7-ish: T[i][j]=1 iff (j-i) % 7 in {1,2,4}
        QR = {1, 2, 4}
        for i in range(n):
            for j in range(n):
                if i == j:
                    continue
                if (j - i) % 7 in QR:
                    T[i][j] = 1
        # confirm all indegrees = 3
        indegs = [sum(T[u][v] for u in range(n)) for v in range(n)]
        self.assertEqual(set(indegs), {3})
        # all windows = [1, 5]: 7 vertices, 5 positions => Hall fails
        self.assertFalse(hall_feasible(T))


# ---------------------------------------------------------------------------
# Width consistency
# ---------------------------------------------------------------------------

class WidthConsistencyTests(unittest.TestCase):

    def test_J_treewidth_at_least_omega_minus_1(self) -> None:
        """For any graph G, tw(G) >= omega(G) - 1."""
        T = reversed_matching(8)
        J = build_J(T)
        omega = max((len(c) for c in nx.find_cliques(J)), default=0)
        tw_ub = treewidth_upper_bound(J)
        self.assertGreaterEqual(tw_ub, omega - 1)

    def test_measure_dataclass_round_trip(self) -> None:
        T = reversed_matching(5)
        rep = measure(T, name="reversed_5", do_exact=True)
        d = rep.as_dict()
        self.assertEqual(d["name"], "reversed_5")
        self.assertEqual(d["n"], 10)
        self.assertTrue(d["hall_ok"])
        self.assertTrue(d["H_is_linear_forest"])

    def test_J_equals_H_union_Gflex(self) -> None:
        """J's edge set is the union of H and Gflex edges."""
        T = reversed_matching(10)
        H, Gflex = build_H_and_Gflex(T)
        J = build_J(T)
        expected = set()
        for u, v in H.edges():
            expected.add(tuple(sorted((u, v))))
        for u, v in Gflex.edges():
            expected.add(tuple(sorted((u, v))))
        actual = {tuple(sorted(e)) for e in J.edges()}
        self.assertEqual(expected, actual)

    def test_hall_bounds_active_window_count_by_nine(self) -> None:
        T = reversed_matching(15)
        self.assertTrue(hall_feasible(T))
        self.assertLessEqual(max_active_window_count(T), 9)
        self.assertEqual(flex_treewidth_bound_from_hall(), 8)

    def test_refined_treewidth_bound_dominates_exact_small_cases(self) -> None:
        for T in (transitive(7), reversed_matching(5), reversed_matching(8)):
            with self.subTest(n=len(T)):
                if not hall_feasible(T):
                    continue
                J = build_J(T)
                exact = treewidth_upper_bound(J)
                bound = refined_treewidth_bound(T)
                self.assertIsNotNone(bound)
                self.assertEqual(refined_pathwidth_bound(T), bound)
                self.assertLessEqual(exact, bound)

    def test_refined_treewidth_bound_absent_when_hall_fails(self) -> None:
        n = 7
        T = [[0] * n for _ in range(n)]
        QR = {1, 2, 4}
        for i in range(n):
            for j in range(n):
                if i != j and (j - i) % n in QR:
                    T[i][j] = 1
        self.assertFalse(hall_feasible(T))
        self.assertIsNone(refined_treewidth_bound(T))


if __name__ == "__main__":
    unittest.main()
