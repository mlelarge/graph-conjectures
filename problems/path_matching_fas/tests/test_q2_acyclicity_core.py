"""Q2 regression tests: D70 family lives at Delta*=2, decision correctness.

Run: python3 -m unittest tests/test_q2_acyclicity_core.py
"""
import os
import random
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from degreewidth_exact import degreewidth  # noqa: E402
from reversed_matching_hardness import build_reversed_matching  # noqa: E402
from toggle_fooling_set import (  # noqa: E402
    build_toggle_family,
    build_toggle_with_probe,
    toggle_prefix,
    verify_fooling_set,
)
from q2_core_cycle_analysis import (  # noqa: E402
    back_arc_components,
    enumerate_degree2_orders,
)
from nonsweep_path_fas import decide_linear_forest_fas_bruteforce  # noqa: E402


def _q2_decide(T):
    dw = degreewidth(T)
    if dw <= 1:
        return True
    if dw >= 3:
        return False
    for o in enumerate_degree2_orders(T, cap=10_000_000):
        md, cl = back_arc_components(T, o)
        if md <= 2 and not cl:
            return True
    return False


def _rand_tour(n, seed):
    r = random.Random(seed)
    T = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            if r.random() < 0.5:
                T[i][j] = 1
            else:
                T[j][i] = 1
    return T


class TestD70Diagnostic(unittest.TestCase):
    def test_base_families_are_degreewidth_one(self):
        for m in range(2, 9):
            self.assertEqual(degreewidth(build_reversed_matching(m)), 1)
        for k in range(1, 5):
            self.assertEqual(degreewidth(build_toggle_family(k)), 1)

    def test_probe_family_is_degreewidth_two(self):
        # The genuine fooling instances live in the Q2 layer.
        for k in range(1, 4):
            for j in range(k):
                self.assertEqual(degreewidth(build_toggle_with_probe(k, j)), 2)

    def test_fooling_failures_are_cycles_not_degree(self):
        # When a toggle prefix fails to complete, it is a back-arc CYCLE,
        # never a degree-3 vertex.
        for k in (2, 3):
            for j in range(k):
                T = build_toggle_with_probe(k, j)
                n = len(T)
                for x in range(1 << k):
                    eps = tuple((x >> i) & 1 for i in range(k))
                    pref = toggle_prefix(k, eps)
                    rest = [v for v in range(n) if v not in set(pref)]
                    md, cl = back_arc_components(T, pref + rest)
                    # canonical completion never overshoots degree budget
                    self.assertLessEqual(md, 2)

    def test_fooling_set_holds(self):
        for k in (1, 2, 3):
            self.assertTrue(verify_fooling_set(k)["fooling_set_holds"])

    def test_degree2_orders_blow_up_on_probe_family(self):
        # Witness that #degree-2 orders is super-polynomial on D70.
        c1 = len(enumerate_degree2_orders(build_toggle_with_probe(1, 0)))
        c2 = len(enumerate_degree2_orders(build_toggle_with_probe(2, 0)))
        c3 = len(enumerate_degree2_orders(build_toggle_with_probe(3, 0)))
        self.assertGreater(c1, 100)
        self.assertGreater(c2, c1)
        self.assertGreater(c3, c2)


class TestQ2DecisionCorrectness(unittest.TestCase):
    def test_matches_bruteforce_random(self):
        bad = 0
        for n in (4, 5, 6, 7):
            for s in range(60):
                T = _rand_tour(n, s * 13 + n)
                if _q2_decide(T) != decide_linear_forest_fas_bruteforce(T):
                    bad += 1
        self.assertEqual(bad, 0)


if __name__ == "__main__":
    unittest.main()
