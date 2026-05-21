"""Validate the polynomial-time MFAS decider.

For every YES answer, also verify that the returned matching M actually
makes T xor M transitive — closing the loop between Theorem 1 (the
structural characterization) and Theorem 2 (the algorithm).
"""
from __future__ import annotations
import os, sys, unittest, random
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from poly_mfas import decide_mfas_poly                  # noqa: E402
from brute import decide                                # noqa: E402
from sweep import all_tournaments, canonical_key        # noqa: E402
from random_check import random_tournament              # noqa: E402


def apply_M(T: list[list[int]], M: list[tuple[int, int]]) -> list[list[int]]:
    n = len(T)
    T2 = [row[:] for row in T]
    for (u, v) in M:
        assert T2[u][v] == 1, f"arc {u}->{v} not in T"
        assert T2[v][u] == 0
        T2[u][v] = 0
        T2[v][u] = 1
    return T2


def is_transitive(T: list[list[int]]) -> bool:
    n = len(T)
    # Topological sort exists iff acyclic. Since tournament, acyclic iff
    # transitive iff topological sort gives a total order.
    indeg = [0] * n
    for u in range(n):
        for v in range(n):
            if T[u][v]:
                indeg[v] += 1
    order: list[int] = []
    remaining = set(range(n))
    while remaining:
        sources = [v for v in remaining if indeg[v] == 0]
        if len(sources) != 1:
            # Transitive tournament has exactly one source at each step.
            return False
        s = sources[0]
        order.append(s)
        remaining.remove(s)
        for w in range(n):
            if T[s][w] and w in remaining:
                indeg[w] -= 1
    return len(order) == n


def is_matching(M: list[tuple[int, int]]) -> bool:
    seen: set[int] = set()
    for (u, v) in M:
        if u in seen or v in seen:
            return False
        seen.add(u); seen.add(v)
    return True


class PolyValidator(unittest.TestCase):

    def _check_yes_certificate(self, T: list[list[int]], M: list) -> None:
        # M must be a matching of arcs of T, and T xor M must be transitive.
        self.assertTrue(is_matching(M), f"M not a matching: {M}")
        T2 = apply_M(T, M)
        self.assertTrue(is_transitive(T2),
                        f"T xor M not transitive; T={T}, M={M}")

    def test_exhaustive_n3_to_6(self):
        for n in range(3, 7):
            seen = set()
            count = 0
            for T in all_tournaments(n):
                k = canonical_key(T)
                if k in seen:
                    continue
                seen.add(k)
                count += 1
                poly = decide_mfas_poly(T)
                br = decide(T, "matching")
                self.assertEqual(poly["found"], br["found"],
                                 f"poly/brute disagree at n={n} T={T}")
                if poly["found"]:
                    self._check_yes_certificate(T, poly["M"])

    def test_random_n7_n8(self):
        for n in (7, 8):
            rng = random.Random(n)
            samples = 50 if n == 8 else 100
            for _ in range(samples):
                T = random_tournament(n, rng)
                poly = decide_mfas_poly(T)
                br = decide(T, "matching")
                self.assertEqual(poly["found"], br["found"])
                if poly["found"]:
                    self._check_yes_certificate(T, poly["M"])


if __name__ == "__main__":
    unittest.main()
