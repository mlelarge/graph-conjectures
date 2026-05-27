"""Tests for directed J+ diagnostics."""
from __future__ import annotations

import os
import sys
import unittest

import networkx as nx

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))

from directed_interaction_graph import (  # noqa: E402
    build_Jplus,
    exact_feedback_vertex_number,
    jplus_report,
)
from interaction_graph import build_H_and_Gflex  # noqa: E402


def transitive(n: int) -> list[list[int]]:
    T = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            T[i][j] = 1
    return T


def reversed_matching(m: int) -> list[list[int]]:
    n = 2 * m
    T = transitive(n)
    for i in range(m):
        T[i][i + m] = 0
        T[i + m][i] = 1
    return T


class DirectedInteractionGraphTests(unittest.TestCase):

    def test_transitive_Jplus_is_acyclic(self) -> None:
        D = build_Jplus(transitive(7))
        self.assertTrue(nx.is_directed_acyclic_graph(D))
        self.assertEqual(exact_feedback_vertex_number(D), 0)

    def test_Jplus_preserves_H_and_flex_arc_counts(self) -> None:
        T = reversed_matching(8)
        H, Gflex = build_H_and_Gflex(T)
        D = build_Jplus(T)
        self.assertEqual(D.number_of_edges(), H.number_of_edges() + Gflex.number_of_edges())
        self.assertEqual(
            sum(1 for _u, _v, d in D.edges(data=True) if d["kind"] == "H"),
            H.number_of_edges(),
        )

    def test_paley7_Jplus_is_strongly_connected(self) -> None:
        n = 7
        T = [[0] * n for _ in range(n)]
        QR = {1, 2, 4}
        for i in range(n):
            for j in range(n):
                if i != j and (j - i) % n in QR:
                    T[i][j] = 1
        rep = jplus_report(T)
        self.assertEqual(rep["largest_scc"], 7)
        self.assertGreaterEqual(rep["feedback_vertex_number"], 2)


if __name__ == "__main__":
    unittest.main()
