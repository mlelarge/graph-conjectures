"""Regression tests for the reduction-theorist deliverables (D31).

These tests pin the empirical findings reported in Section D31 of
`docs/exchange_proof_draft.md`:

  * the Section 16 toggle is a balanced (9/4) but asymmetric variable
    gadget;
  * the cyclic triangle is a valid NAE-3SAT clause gadget in isolation;
  * the cyclic triangle fails 1-in-3-SAT in isolation (3 spurious);
  * the aligned fork-tree does NOT force agreement of fanout copies
    (it is therefore not a fanout in the reduction sense);
  * the NAE-3SAT composition skeleton emits the expected vertex
    layout and flags the unresolved fanout obligation.

The tests therefore pin both the *positive* gadget findings and the
*negative* fanout / 1-in-3 findings.  Any future change to the
underlying tournaments or verifier should re-baseline these tests
**only after re-checking the corresponding section of the proof draft**.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from np_hardness_reduction import (  # noqa: E402
    build_nae3sat_skeleton,
    cyclic_triangle,
    fanout_agreement_evidence,
    fanout_candidate_aligned_fork_tree,
    variable_gadget,
    verify_clause_in_isolation_1in3,
    verify_clause_in_isolation_nae3,
)
from np_hardness_gadget_verifier import (  # noqa: E402
    full_truth_table,
    placement_bit_first_pair_inversion,
    verify_variable_gadget,
)


class VariableGadgetTests(unittest.TestCase):
    """T1: Section 16 toggle is the variable gadget."""

    def test_single_toggle_balanced(self) -> None:
        T, ports = variable_gadget(num_vars=1)
        r = verify_variable_gadget(T, ports[0])
        self.assertTrue(r["is_balanced"])
        self.assertEqual(r["truth_table"][(False,)], 9)
        self.assertEqual(r["truth_table"][(True,)], 4)
        self.assertEqual(r["total_lfos"], 13)

    def test_two_toggle_joint_table_realizes_all_patterns(self) -> None:
        T, ports = variable_gadget(num_vars=2)
        tt = full_truth_table(
            T, ports,
            lambda P: placement_bit_first_pair_inversion(P, ports),
            width=2,
        )
        for bits in [(False, False), (False, True), (True, False), (True, True)]:
            self.assertGreater(
                tt[bits], 0,
                f"two-toggle joint table failed to realize bit pattern {bits}",
            )


class ClauseGadgetNAE3Tests(unittest.TestCase):
    """T3: cyclic triangle is the NAE-3SAT clause gadget."""

    def test_cyclic_triangle_is_valid_nae3_clause(self) -> None:
        r = verify_clause_in_isolation_nae3()
        self.assertTrue(r["ok"])
        self.assertEqual(r["missing"], set())
        self.assertEqual(r["spurious"], set())

    def test_cyclic_triangle_truth_table_pins_constant_forbidden(self) -> None:
        r = verify_clause_in_isolation_nae3()
        tt = r["truth_table"]
        self.assertEqual(tt[(False, False, False)], 0)
        self.assertEqual(tt[(True, True, True)], 0)

    def test_cyclic_triangle_each_nae_pattern_has_one_lfo(self) -> None:
        r = verify_clause_in_isolation_nae3()
        tt = r["truth_table"]
        # The 6 non-constant patterns each have exactly one LFO.
        for bits, count in tt.items():
            if bits in ((False, False, False), (True, True, True)):
                continue
            self.assertEqual(
                count, 1,
                f"cyclic triangle pattern {bits} should have 1 LFO, got {count}",
            )


class ClauseGadget1in3FailureTests(unittest.TestCase):
    """T3 (negative): no 3-vertex cyclic triangle works for 1-in-3-SAT."""

    def test_cyclic_triangle_fails_1in3(self) -> None:
        r = verify_clause_in_isolation_1in3()
        self.assertFalse(r["ok"])
        # Three spurious patterns: the 2-True patterns.
        self.assertEqual(len(r["spurious"]), 3)
        self.assertIn((True, False, True), r["spurious"])
        self.assertIn((True, True, False), r["spurious"])
        self.assertIn((False, True, True), r["spurious"])


class FanoutNegativeResultTests(unittest.TestCase):
    """T2: the aligned fork-tree does NOT force agreement.

    This pins the negative empirical finding documented in Section 43
    (D31) of the proof draft.  If this test ever passes by claiming
    `forces_agreement`, something deep has changed about the fork-tree
    structure and the corresponding proof section must be updated.
    """

    def test_aligned_fork_tree_does_not_force_agreement_k2(self) -> None:
        r = fanout_agreement_evidence(k=2)
        self.assertEqual(r["verdict"], "does_not_force_agreement")
        self.assertFalse(r["all_lfos_agree"])
        # All 4 patterns realized -> aligned fork-tree is transparent.
        self.assertEqual(len(r["patterns_realized"]), 4)


class CompositionSkeletonTests(unittest.TestCase):
    """T4: the skeleton emits the expected layout for a tiny formula."""

    def test_skeleton_vertex_counts(self) -> None:
        clauses = [
            ((0, True), (1, True), (2, True)),
            ((0, False), (1, True), (2, False)),
        ]
        r = build_nae3sat_skeleton(num_vars=3, clauses=clauses)
        # 3 variables * 4 vertices + 2 clauses * 3 vertices = 12 + 6 = 18.
        self.assertEqual(r["total_vertices_so_far"], 18)
        self.assertEqual(r["num_variables"], 3)
        self.assertEqual(r["num_clauses"], 2)
        self.assertEqual(r["variable_offsets"], [0, 4, 8])
        self.assertEqual(r["clause_offsets"], [12, 15])

    def test_skeleton_flags_unresolved_fanout(self) -> None:
        clauses = [((0, True), (1, True), (2, True))]
        r = build_nae3sat_skeleton(num_vars=3, clauses=clauses)
        self.assertEqual(r["status"], "skeleton_only")
        # Every linkage entry must say `fanout_NOT_IMPLEMENTED`.
        for entry in r["intended_linkage"]:
            self.assertEqual(entry["via"], "fanout_NOT_IMPLEMENTED")
        # Open-problems list must mention T2 (fanout).
        self.assertTrue(
            any("T2" in p and "fanout" in p.lower() for p in r["open_problems"]),
            "open_problems should call out the T2 fanout obligation",
        )


if __name__ == "__main__":
    unittest.main()
