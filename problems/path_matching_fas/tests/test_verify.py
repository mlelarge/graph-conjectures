"""Pin verifier output against hand-checked small tournaments."""
import os, sys, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from verify import verify, classify, back_arcs  # noqa: E402
from brute import decide                         # noqa: E402


def cyclic_triangle():
    # 0->1->2->0
    return [[0, 1, 0], [0, 0, 1], [1, 0, 0]]


def transitive_triangle():
    # 0->1, 0->2, 1->2
    return [[0, 1, 1], [0, 0, 1], [0, 0, 0]]


class VerifyTests(unittest.TestCase):

    def test_classify_empty(self):
        cls = classify([])
        self.assertEqual(cls["count"], 0)
        self.assertEqual(cls["max_degree"], 0)
        self.assertTrue(cls["is_matching"])
        self.assertTrue(cls["is_forest"])
        self.assertTrue(cls["is_linear_forest"])
        self.assertFalse(cls["is_path"])  # empty is not a "path"

    def test_classify_single_edge_is_path_and_matching(self):
        cls = classify([(0, 1)])
        self.assertTrue(cls["is_matching"])
        self.assertTrue(cls["is_path"])
        self.assertTrue(cls["is_linear_forest"])

    def test_classify_two_arcs_path(self):
        cls = classify([(0, 1), (1, 2)])
        self.assertEqual(cls["max_degree"], 2)
        self.assertFalse(cls["is_matching"])
        self.assertTrue(cls["is_path"])
        self.assertTrue(cls["is_linear_forest"])

    def test_classify_two_arcs_matching(self):
        cls = classify([(0, 1), (2, 3)])
        self.assertTrue(cls["is_matching"])
        self.assertFalse(cls["is_path"])           # two components
        self.assertTrue(cls["is_linear_forest"])

    def test_classify_star_K13(self):
        cls = classify([(0, 1), (0, 2), (0, 3)])
        self.assertEqual(cls["max_degree"], 3)
        self.assertTrue(cls["is_forest"])
        self.assertFalse(cls["is_linear_forest"])  # max deg 3
        self.assertFalse(cls["is_path"])
        self.assertFalse(cls["is_matching"])

    def test_cyclic_triangle_orderings(self):
        # 0->1->2->0. Exactly 3 of 6 orderings (the "rotations") give 1
        # back-arc; the other 3 (reflections) give 2 back-arcs.
        T = cyclic_triangle()
        rotations = {(0, 1, 2), (1, 2, 0), (2, 0, 1)}
        for P in [(0, 1, 2), (1, 2, 0), (2, 0, 1), (0, 2, 1), (1, 0, 2), (2, 1, 0)]:
            info = verify(T, list(P))
            if P in rotations:
                self.assertEqual(info["count"], 1)
                self.assertTrue(info["is_matching"])
                self.assertTrue(info["is_path"])
            else:
                self.assertEqual(info["count"], 2)
                # 2 back-arcs that share a vertex => max-degree 2, a path
                # of length 2 on 3 vertices. Not a matching.
                self.assertFalse(info["is_matching"])
                self.assertTrue(info["is_path"])

    def test_cyclic_triangle_decide_matching(self):
        T = cyclic_triangle()
        r = decide(T, "matching")
        self.assertTrue(r["found"])
        self.assertEqual(r["info"]["count"], 1)

    def test_transitive_triangle_zero_back_arcs(self):
        T = transitive_triangle()
        info = verify(T, [0, 1, 2])
        self.assertEqual(info["count"], 0)
        self.assertTrue(info["is_matching"])      # empty back-arc set IS a matching
        self.assertFalse(info["is_path"])         # but not a path

    def test_back_arcs_count_consistency(self):
        # In any order on a tournament of size n, total back-arcs +
        # forward arcs = n(n-1)/2.
        T = cyclic_triangle()
        for P in [(0, 1, 2), (2, 0, 1), (1, 2, 0)]:
            arcs = back_arcs(T, list(P))
            self.assertEqual(len(arcs), 1)


if __name__ == "__main__":
    unittest.main()
