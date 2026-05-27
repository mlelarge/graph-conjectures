"""Pinned tests for the formal gadget-as-relation interface.

These tests anchor the worked examples in `docs/fanout_interface.md`:

  * § 10.1 Section 16 toggle (k=1) realises the FULL unary relation
    R = {(0,), (1,)} = {0,1}.
  * § 10.2 Cyclic triangle realises EXACTLY R_NAE = {0,1}^3 \\ {000,111}.
  * § 10.3 Aligned fork-tree at k=2 realises the FULL binary relation
    {0,1}^2 (does NOT realise R_eq^(2) = {(0,0),(1,1)}).
  * § 5.1 Observation N1: disjoint-port placement-bit NEGATION is NOT
    realisable at n <= 5.
  * § 5.2 Constants: no 1-port placement-bit gadget at n <= 4 realises
    a singleton relation {(0,)} or {(1,)}.
  * § 7 Schaefer classification: the cyclic triangle's relation is
    NP-hard as a constraint type; the toggle's relation is in every
    Schaefer class (trivially).

Every test routes through the trust-root verifier and the
relation-miner Schaefer classifier.
"""
import os
import sys
import unittest
from itertools import product

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from np_hardness_gadget_verifier import (  # noqa: E402
    enumerate_extendable_orderings,
    full_truth_table,
    placement_bit_first_pair_inversion,
    section16_toggle_ports,
    section16_toggle_tournament,
)
from np_hardness_reduction import (  # noqa: E402
    cyclic_triangle,
    fanout_candidate_aligned_fork_tree,
)
from relation_miner import (  # noqa: E402
    classify_schaefer,
    is_bijunctive,
    is_horn,
    is_dual_horn,
    is_affine,
    is_np_hard_type,
)


def _relation_from_gadget(T, ports, width):
    """Compute R_G = support of the placement-bit truth table."""
    tt = full_truth_table(
        T, ports,
        lambda P: placement_bit_first_pair_inversion(P, ports),
        width=width,
    )
    return frozenset(
        tuple(int(b) for b in bits)
        for bits, c in tt.items() if c > 0
    )


def _all_tournaments(n):
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    for bits in product([0, 1], repeat=len(pairs)):
        T = [[0] * n for _ in range(n)]
        for (i, j), b in zip(pairs, bits):
            if b:
                T[i][j] = 1
            else:
                T[j][i] = 1
        yield T


# ----------------------------------------------------------------------
# § 10.1  Section 16 toggle (variable gadget)
# ----------------------------------------------------------------------


class ToggleRelationTests(unittest.TestCase):
    """The Section 16 toggle (k=1) realises the FULL unary relation."""

    def test_toggle_relation_is_full_unary(self):
        T = section16_toggle_tournament(1)
        port = section16_toggle_ports(1)[0]
        R = _relation_from_gadget(T, [port], width=1)
        self.assertEqual(R, frozenset({(0,), (1,)}))

    def test_toggle_lfo_count(self):
        T = section16_toggle_tournament(1)
        self.assertEqual(len(enumerate_extendable_orderings(T)), 13)

    def test_toggle_relation_schaefer_classes(self):
        """The full unary relation is trivially in every Schaefer class."""
        R = frozenset({(0,), (1,)})
        cls = classify_schaefer(R)
        self.assertTrue(cls["is_0_valid"])
        self.assertTrue(cls["is_1_valid"])
        self.assertTrue(cls["is_bijunctive"])
        self.assertTrue(cls["is_horn"])
        self.assertTrue(cls["is_dual_horn"])
        self.assertTrue(cls["is_affine"])
        self.assertFalse(is_np_hard_type(R))


# ----------------------------------------------------------------------
# § 10.2  Cyclic triangle (NAE-3 clause gadget)
# ----------------------------------------------------------------------


class CyclicTriangleRelationTests(unittest.TestCase):
    """The cyclic triangle realises EXACTLY R_NAE = {0,1}^3 \\ {000,111}."""

    def test_cyclic_triangle_relation_is_NAE3(self):
        T, ports = cyclic_triangle()
        R = _relation_from_gadget(T, ports, width=3)
        expected = frozenset(
            tuple(int(b) for b in bits)
            for bits in product([0, 1], repeat=3)
            if not (all(b == 0 for b in bits) or all(b == 1 for b in bits))
        )
        self.assertEqual(R, expected)
        self.assertEqual(len(R), 6)

    def test_NAE3_is_NP_hard_as_constraint_type(self):
        T, ports = cyclic_triangle()
        R = _relation_from_gadget(T, ports, width=3)
        cls = classify_schaefer(R)
        # Document the precise Schaefer breakdown of NAE-3.
        self.assertFalse(cls["is_0_valid"])
        self.assertFalse(cls["is_1_valid"])
        self.assertFalse(cls["is_bijunctive"])
        self.assertFalse(cls["is_horn"])
        self.assertFalse(cls["is_dual_horn"])
        self.assertFalse(cls["is_affine"])
        self.assertTrue(is_np_hard_type(R))

    def test_NAE3_not_bijunctive_concrete_witness(self):
        """Majority of (0,1,1),(1,0,1),(1,1,0) is (1,1,1) NOT in R_NAE."""
        R_NAE = frozenset({
            (0, 0, 1), (0, 1, 0), (0, 1, 1),
            (1, 0, 0), (1, 0, 1), (1, 1, 0),
        })
        a, b, c = (0, 1, 1), (1, 0, 1), (1, 1, 0)
        self.assertIn(a, R_NAE)
        self.assertIn(b, R_NAE)
        self.assertIn(c, R_NAE)
        maj = tuple(int(x + y + z >= 2) for x, y, z in zip(a, b, c))
        self.assertEqual(maj, (1, 1, 1))
        self.assertNotIn(maj, R_NAE)
        self.assertFalse(is_bijunctive(R_NAE))

    def test_cyclic_triangle_lfo_count(self):
        """All 6 orderings of a 3-vertex tournament are LFOs (1 back-arc)."""
        T, _ = cyclic_triangle()
        self.assertEqual(len(enumerate_extendable_orderings(T)), 6)


# ----------------------------------------------------------------------
# § 10.3  Aligned fork-tree at k=2 (the failed equality fanout)
# ----------------------------------------------------------------------


class AlignedForkTreeRelationTests(unittest.TestCase):
    """The aligned fork-tree at k=2 realises the FULL binary relation.

    This is the central NEGATIVE finding for the fanout problem: the
    natural candidate does NOT realise R_eq^(2) = {(0,0),(1,1)}; it
    realises the full {0,1}^2.
    """

    def test_fork_tree_k2_realises_full_binary(self):
        T, ports = fanout_candidate_aligned_fork_tree(2)
        # The fork-tree at k=2 has n = 4*2+2 = 10 vertices -- at the
        # enumeration limit but tractable.
        R = _relation_from_gadget(T, ports, width=2)
        expected_full = frozenset({(0, 0), (0, 1), (1, 0), (1, 1)})
        self.assertEqual(R, expected_full)

    def test_fork_tree_k2_is_not_equality_fanout(self):
        T, ports = fanout_candidate_aligned_fork_tree(2)
        R = _relation_from_gadget(T, ports, width=2)
        R_eq = frozenset({(0, 0), (1, 1)})
        self.assertNotEqual(R, R_eq)
        # The disagreement patterns (0,1) and (1,0) leak through.
        self.assertIn((0, 1), R)
        self.assertIn((1, 0), R)


# ----------------------------------------------------------------------
# § 5.2  Observation: no small constant 1-port gadget under placement-bit
# ----------------------------------------------------------------------


class NoSmallConstantsTests(unittest.TestCase):
    """Pin observation: no 1-port placement-bit gadget at n <= 4 realises
    a singleton relation R = {(0,)} or R = {(1,)}.

    This is the empirical evidence behind the "constants-not-available"
    Schaefer case for Path-FAS-realisable relations.
    """

    def test_no_constants_at_n_eq_3(self):
        n = 3
        for T in _all_tournaments(n):
            for port in [(i, j) for i in range(n) for j in range(n) if i != j]:
                R = _relation_from_gadget(T, [port], width=1)
                # R must contain both bit values, or be empty.
                self.assertNotEqual(R, frozenset({(0,)}),
                                    f"unexpected constant-0 at T={T}, port={port}")
                self.assertNotEqual(R, frozenset({(1,)}),
                                    f"unexpected constant-1 at T={T}, port={port}")

    def test_no_constants_at_n_eq_4(self):
        n = 4
        # Sample-budget: enumerate all 64 tournaments, all 12 port choices.
        for T in _all_tournaments(n):
            for port in [(i, j) for i in range(n) for j in range(n) if i != j]:
                R = _relation_from_gadget(T, [port], width=1)
                self.assertNotEqual(R, frozenset({(0,)}))
                self.assertNotEqual(R, frozenset({(1,)}))


# ----------------------------------------------------------------------
# § 5.1  Observation N1: no disjoint-port NEGATION at n <= 5
# ----------------------------------------------------------------------


class NegationViaPortReversalTests(unittest.TestCase):
    """Two pinned facts:

      (a) For ANY gadget G with a port (x,y), reusing the SAME pair
          as (y,x) flips the bit -- this is the trivial reversal
          construction (§ 5.1).
      (b) Disjoint-port placement-bit NEGATION (i.e. R = {(0,1),(1,0)})
          via two disjoint port pairs is NOT realisable at n <= 5
          (exhaustive search).
    """

    def test_port_reversal_flips_bit(self):
        T = section16_toggle_tournament(1)
        a, b = section16_toggle_ports(1)[0]
        # Same gadget, two ports: (a,b) and (b,a).  The two bits must be
        # complementary in every LFO.
        ports = [(a, b), (b, a)]
        R = _relation_from_gadget(T, ports, width=2)
        # Every realised tuple must satisfy bit1 = 1 - bit0.
        for t in R:
            self.assertEqual(t[0] + t[1], 1,
                             f"port reversal failed: {t}")

    def test_no_disjoint_port_negation_at_n_eq_4(self):
        n = 4
        ports = [(0, 1), (2, 3)]
        for T in _all_tournaments(n):
            R = _relation_from_gadget(T, ports, width=2)
            self.assertNotEqual(R, frozenset({(0, 1), (1, 0)}),
                                f"unexpected n=4 disjoint NEG: T={T}")

    def test_no_disjoint_port_negation_at_n_eq_5(self):
        n = 5
        ports = [(0, 1), (2, 3)]
        for T in _all_tournaments(n):
            R = _relation_from_gadget(T, ports, width=2)
            self.assertNotEqual(R, frozenset({(0, 1), (1, 0)}),
                                f"unexpected n=5 disjoint NEG")


# ----------------------------------------------------------------------
# § 6  Target relations are well-defined
# ----------------------------------------------------------------------


class TargetRelationSchaeferTests(unittest.TestCase):
    """Pin the Schaefer classifications of the three target relations
    (R_eq, R_imp, R_NAE) from § 6 of the interface document.
    """

    def test_R_eq_k2_is_all_classes(self):
        R = frozenset({(0, 0), (1, 1)})
        cls = classify_schaefer(R)
        self.assertTrue(cls["is_0_valid"])
        self.assertTrue(cls["is_1_valid"])
        self.assertTrue(cls["is_bijunctive"])
        self.assertTrue(cls["is_horn"])
        self.assertTrue(cls["is_dual_horn"])
        self.assertTrue(cls["is_affine"])
        self.assertFalse(is_np_hard_type(R))

    def test_R_eq_k3_is_all_classes(self):
        R = frozenset({(0, 0, 0), (1, 1, 1)})
        cls = classify_schaefer(R)
        self.assertTrue(cls["is_0_valid"])
        self.assertTrue(cls["is_1_valid"])
        self.assertTrue(cls["is_bijunctive"])
        self.assertTrue(cls["is_horn"])
        self.assertTrue(cls["is_dual_horn"])
        self.assertTrue(cls["is_affine"])

    def test_R_imp_is_horn(self):
        # R_imp = {(x,y,z) : x => y AND x => z} = 6 tuples
        R = frozenset({
            (0, 0, 0), (0, 0, 1), (0, 1, 0), (0, 1, 1),
            (1, 1, 0), (1, 1, 1),
        })
        # (1, 1, 0) is x=1 forces y=1 and z=0... wait, x=>z means z>=x; so
        # (1,1,0) violates x=>z.  Recompute.
        # x=>y iff y >= x; x=>z iff z >= x.
        # Tuples with x=0: any (y,z) -- 4 tuples.
        # Tuples with x=1: y=1 and z=1 -- 1 tuple.
        # Total = 5, not 6.  Correct R_imp:
        R_correct = frozenset({
            (0, 0, 0), (0, 0, 1), (0, 1, 0), (0, 1, 1),
            (1, 1, 1),
        })
        cls = classify_schaefer(R_correct)
        self.assertTrue(cls["is_horn"],
                        "R_imp = conjunction of two implications must be Horn")
        # Not necessarily in every other class.

    def test_R_NAE_is_in_no_class(self):
        R = frozenset({
            (0, 0, 1), (0, 1, 0), (0, 1, 1),
            (1, 0, 0), (1, 0, 1), (1, 1, 0),
        })
        self.assertTrue(is_np_hard_type(R))


# ----------------------------------------------------------------------
# § 4.2  Composition monotonicity (the C1 assertion)
# ----------------------------------------------------------------------


class CompositionMonotonicityTests(unittest.TestCase):
    """C1: R_composed subseteq R_G1 join R_G2.

    Pin: composing two cyclic triangles by joining their first ports
    (identifying vertex 0 of G1 with vertex 0 of G2) shrinks the
    composed relation relative to the natural join.
    """

    def test_composition_can_only_lose_satisfying_assignments(self):
        from np_hardness_gadget_verifier import gadget_compose
        # Two cyclic triangles.  G1 has ports (0,1),(1,2),(2,0); G2 has
        # the same locally.  After composition (which doubles vertices),
        # local truth tables of EACH triangle restricted to its own 3
        # vertices must still be in R_NAE.
        T1 = [[0, 1, 0], [0, 0, 1], [1, 0, 0]]
        T2 = [[0, 1, 0], [0, 0, 1], [1, 0, 0]]
        # All cross-arcs gadget0 -> gadget1.
        cross = {}
        for li in range(3):
            for lj in range(3):
                cross[((0, li), (1, lj))] = 1
        T = gadget_compose([T1, T2], cross)
        self.assertEqual(len(T), 6)
        # Local truth table at G1's ports, restricted to vertices {0,1,2}:
        from np_hardness_gadget_verifier import truth_table_from_gadget
        tt0 = truth_table_from_gadget(
            T,
            [(0, 1), (1, 2), (2, 0)],
            lambda P: placement_bit_first_pair_inversion(
                P, [(0, 1), (1, 2), (2, 0)]),
            vertices_subset=[0, 1, 2],
        )
        observed0 = frozenset(
            tuple(int(b) for b in bits)
            for bits, c in tt0.items() if c > 0
        )
        R_NAE = frozenset({
            (0, 0, 1), (0, 1, 0), (0, 1, 1),
            (1, 0, 0), (1, 0, 1), (1, 1, 0),
        })
        # Local observed relation must be subseteq R_NAE.
        self.assertTrue(observed0.issubset(R_NAE),
                        f"local relation leaked: {observed0 - R_NAE}")


if __name__ == "__main__":
    unittest.main()
