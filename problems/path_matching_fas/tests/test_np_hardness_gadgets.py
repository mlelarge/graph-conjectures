"""Regression tests for the NP-hardness gadget verification toolkit.

These tests pin truth-table results for every candidate gadget that
the reduction theorist has proposed.  Failing tests must NOT be
re-baselined silently: a gadget whose truth table changes is a gadget
whose semantics changed, and the reduction proof has to change with it.
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from np_hardness_gadget_verifier import (  # noqa: E402
    ALLOWED_1IN3,
    ALLOWED_NAE3,
    cross_arc_audit,
    enumerate_extendable_orderings,
    full_truth_table,
    gadget_compose,
    minimal_obstruction_search,
    placement_bit_first_pair_inversion,
    section16_toggle_ports,
    section16_toggle_tournament,
    truth_table_from_gadget,
    verify_clause_gadget,
    verify_variable_gadget,
)


# ------------------------------------------------------------------
# 1. Section 16 toggle gadget (variable candidate)
# ------------------------------------------------------------------


class ToggleVariableGadgetTests(unittest.TestCase):
    """Pin the toggle truth table at k=1 and k=2.

    The toggle gadget on 4 vertices (a_0, b_0, f_0, g_0) is the
    candidate *variable* gadget.  Section 16.6 of the exchange-proof
    draft notes that "all 2^k toggle prefixes complete to a valid LFO."
    What the proof does NOT say is the *total* LFO count over the
    isolated toggle: that count is 13, not 2.  The 2 figure is the
    number of *toggle prefixes* (i.e. orderings of {a_0, b_0} on
    positions 0, 1, with f_0, g_0 following), not the number of full
    LFOs.

    The truth table at port (a_0, b_0) is:
      (False,) -> 9 LFOs   (a_0 before b_0 in P)
      (True,)  -> 4 LFOs   (b_0 before a_0 in P)
    Both port bits are realized: the gadget is "balanced".

    Verdict: as a variable gadget, the Section 16 toggle is balanced
    (both bits realizable) but it does NOT force the *output* bit
    cleanly.  9-vs-4 is asymmetric, and the asymmetry is not enough by
    itself for a clean reduction.  This pins the asymmetry so the
    theorist can decide whether it is exploitable or needs a different
    variable gadget.
    """

    def test_toggle_variable_gadget(self):
        T = section16_toggle_tournament(1)
        port = section16_toggle_ports(1)[0]
        self.assertEqual(port, (0, 1))
        res = verify_variable_gadget(T, port)
        self.assertEqual(
            res["truth_table"],
            {(False,): 9, (True,): 4},
        )
        self.assertTrue(res["is_balanced"])
        self.assertEqual(res["total_lfos"], 13)

    def test_toggle_k2_truth_table(self):
        """Two-toggle composition (4k=8 vertices) — pin the joint
        truth table at the 2 ports (a_0, b_0) and (a_1, b_1).

        This is a direct check of the "exactly 2^k toggle prefixes are
        extendable" claim (Section 16.6) and its converse: do the four
        port assignments (F,F), (F,T), (T,F), (T,T) each correspond to
        many LFOs?  Yes: 20, 5, 14, 3 respectively.  Both bits are
        independently realizable, so the toggle does carry 1 bit of
        information per gadget.
        """
        T = section16_toggle_tournament(2)
        ports = section16_toggle_ports(2)
        tt = full_truth_table(
            T, ports,
            lambda P: placement_bit_first_pair_inversion(P, ports),
            width=2,
        )
        self.assertEqual(
            tt,
            {
                (False, False): 20,
                (False, True): 5,
                (True, False): 14,
                (True, True): 3,
            },
        )

    def test_toggle_enumerate_lfo_count(self):
        T = section16_toggle_tournament(1)
        lfos = enumerate_extendable_orderings(T)
        self.assertEqual(len(lfos), 13)


# ------------------------------------------------------------------
# 2. Clause gadget — naive 3-cyclic-triangle candidate (expected fail)
# ------------------------------------------------------------------


def _cyclic_triangle_3port() -> tuple[list[list[int]], list[tuple[int, int]]]:
    """A 3-vertex cyclic triangle 0->1->2->0, used as a *naive* clause
    candidate.  This is the theorist's "obviously wrong" first attempt:
    we verify it fails the 1-in-3 truth table, document the failure,
    and pin it so future passes do not re-propose it.

    Each port is a degenerate "self-pair" (v, v).  The bit is then
    pos[v] < pos[v], which is always False — so this candidate cannot
    distinguish any of the 8 truth-table entries, which is exactly the
    "naive failure" we want to pin.
    """
    T = [
        [0, 1, 0],
        [0, 0, 1],
        [1, 0, 0],
    ]
    # Use *distinct* port pairs to avoid the degenerate self-pair case:
    # port i is (i, (i+1) % 3) so the bit reads as "next neighbor
    # before vertex i in P".
    ports = [(0, 1), (1, 2), (2, 0)]
    return T, ports


class NaiveClauseCandidateTests(unittest.TestCase):
    """Pin the failure of the trivial 3-vertex clause candidate.

    The cyclic triangle has 3 LFOs (one per cyclic shift; the three
    "anti" orderings are the same triangle reversed and produce the
    full back-arc-triangle which is NOT a linear forest).  Reading the
    standard port bits gives only a small subset of the 8 possible
    patterns — and definitely not the 3 single-true 1-in-3-SAT
    patterns.  Documenting the failure prevents the theorist from
    repeating the experiment.
    """

    def test_cyclic_triangle_fails_1in3(self):
        T, ports = _cyclic_triangle_3port()
        res = verify_clause_gadget(T, ports, mode="1in3")
        # Failure mode: the cyclic triangle DOES realize all 3 of the
        # single-true patterns (missing == empty), but it ALSO realizes
        # 3 of the "two-true" patterns (spurious == 3 elements).  Both
        # the "two-true" patterns (1,1,0), (1,0,1), (0,1,1) leak
        # through, so the gadget cannot enforce the 1-in-3 constraint.
        self.assertFalse(res["ok"])
        self.assertEqual(res["missing"], set())
        self.assertEqual(
            res["spurious"],
            {(True, True, False), (True, False, True), (False, True, True)},
        )

    def test_cyclic_triangle_total_lfos(self):
        T, _ = _cyclic_triangle_3port()
        lfos = enumerate_extendable_orderings(T)
        # All 6 orderings of 3 vertices: which are LFOs?
        # Each ordering produces a single back-arc (size 1 = trivial
        # linear forest), so all 6 are LFOs.
        self.assertEqual(len(lfos), 6)


# ------------------------------------------------------------------
# 3. Composition + cross-arc audit
# ------------------------------------------------------------------


class CompositionTests(unittest.TestCase):
    """Two-toggle composition with explicit cross-arcs.

    The Section 16 toggle k=2 tournament is the canonical "two
    independent toggles glued by transitive cross-arcs" composition.
    Verify that `gadget_compose` reproduces it exactly when we feed
    it two single-toggle gadgets and the transitive cross-arc
    orientation (every cross-arc points from gadget 0 to gadget 1).
    """

    def test_two_toggle_compose_matches_section16_k2(self):
        G1 = section16_toggle_tournament(1)
        G2 = section16_toggle_tournament(1)
        # In Section 16 with k=2, vertex order is
        #   a_0=0, b_0=1, a_1=2, b_1=3,
        #   f_0=4, g_0=5, f_1=6, g_1=7
        # But gadget_compose puts gadget 0 first, then gadget 1,
        # producing
        #   a_0=0, b_0=1, f_0=2, g_0=3,
        #   a_1=4, b_1=5, f_1=6, g_1=7
        # That is a DIFFERENT global numbering -> a different
        # tournament.  What we check is structural equivalence: the
        # composed tournament should still have its per-gadget truth
        # table at the (local) (a, b) port match the isolated toggle.
        cross: dict = {}
        for li in range(4):
            for lj in range(4):
                cross[((0, li), (1, lj))] = 1  # gadget 0 -> gadget 1
        T = gadget_compose([G1, G2], cross)
        self.assertEqual(len(T), 8)
        # Per-gadget local truth tables (restricted to each block):
        tt0 = truth_table_from_gadget(
            T, [(0, 1)],
            lambda P: placement_bit_first_pair_inversion(P, [(0, 1)]),
            vertices_subset=[0, 1, 2, 3],
        )
        tt1 = truth_table_from_gadget(
            T, [(4, 5)],
            lambda P: placement_bit_first_pair_inversion(P, [(4, 5)]),
            vertices_subset=[4, 5, 6, 7],
        )
        # Each block is an isolated toggle -> 9 / 4 split.
        self.assertEqual(tt0, {(False,): 9, (True,): 4})
        self.assertEqual(tt1, {(False,): 9, (True,): 4})

    def test_cross_arc_audit_two_toggles_transitive(self):
        """Audit a single cross-arc orientation (all gadget0 ->
        gadget1).  Per-gadget truth tables should preserve the
        balanced (F,T) realization.
        """
        G1 = section16_toggle_tournament(1)
        G2 = section16_toggle_tournament(1)
        cross: dict = {}
        for li in range(4):
            for lj in range(4):
                cross[((0, li), (1, lj))] = 1
        # Audit just the one fixed orientation by passing it as fixed.
        # Local port labels in each gadget are (0, 1) -- the (a_0, b_0)
        # of that copy.  The audit translates these into the composed
        # tournament's global labels internally.
        result = cross_arc_audit(
            [G1, G2],
            local_port_pairs_per_gadget=[[(0, 1)], [(0, 1)]],
            expected_truth_tables=[{(False,), (True,)}, {(False,), (True,)}],
            fixed_cross_arcs=cross,
        )
        self.assertEqual(result["tested"], 1)
        self.assertEqual(result["ok"], 1)
        self.assertEqual(result["violations"], [])


# ------------------------------------------------------------------
# 4. Minimal obstruction search smoke test
# ------------------------------------------------------------------


class MinimalObstructionTests(unittest.TestCase):
    """Smoke-test the minimal-obstruction search on a known-3-cycle.

    Predicate: "the tournament has at least one cyclic triple."
    The minimal such subgraph is the cyclic triangle (3 vertices).
    """

    def test_minimal_cyclic_triple(self):
        # 4-vertex tournament: transitive on {0,1,2,3} except 3->0.
        T = [
            [0, 1, 1, 0],
            [0, 0, 1, 1],
            [0, 0, 0, 1],
            [1, 0, 0, 0],
        ]

        def has_cycle(M):
            n = len(M)
            for a in range(n):
                for b in range(n):
                    for c in range(n):
                        if a != b != c != a and M[a][b] and M[b][c] and M[c][a]:
                            return True
            return False

        result = minimal_obstruction_search(T, has_cycle)
        self.assertIsNotNone(result)
        self.assertEqual(result["size"], 3)


# ------------------------------------------------------------------
# 5. NAE-3SAT skeleton — verify enumerator on a hand-built clause stub
# ------------------------------------------------------------------


class NAE3SatPlaceholderTests(unittest.TestCase):
    """The reduction theorist has not yet proposed a NAE-3SAT clause
    gadget; this test pins the *expectation* (ALLOWED_NAE3 size = 6)
    so any theorist regression that re-imports the constant catches
    accidental edits to the spec.
    """

    def test_allowed_nae3_size(self):
        self.assertEqual(len(ALLOWED_NAE3), 6)
        self.assertNotIn((False, False, False), ALLOWED_NAE3)
        self.assertNotIn((True, True, True), ALLOWED_NAE3)

    def test_allowed_1in3_size(self):
        self.assertEqual(len(ALLOWED_1IN3), 3)
        for bits in ALLOWED_1IN3:
            self.assertEqual(sum(bits), 1)


if __name__ == "__main__":
    unittest.main()
