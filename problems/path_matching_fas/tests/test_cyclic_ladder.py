"""Regression tests for the generic cyclic ladder probe."""
import os
import sys
import unittest


SCRIPT_DIR = os.path.join(os.path.dirname(__file__), "..", "scripts")
sys.path.insert(0, os.path.abspath(SCRIPT_DIR))

from cyclic_ladder_probe import (  # noqa: E402
    completion_certificate,
    contracted_obstructive_witness,
    contracted_trigger_real_witness,
    construct_cyclic_ladder,
    cyclic_ladder_sets,
    internal_gap_profile,
    predict_cyclic_ladder_minimal_fatal,
    predict_three_interval_internal_gap_fatal,
    targeted_minimal_fatal_certificate,
    top_interval_peel_summary,
    virtual_contraction_sequence,
)


class CyclicLadderProbeTest(unittest.TestCase):

    def test_size8_k9_generic_construction_is_minimal_fatal(self):
        pi = construct_cyclic_ladder(9, 4)
        selected = tuple(range(8))
        self.assertEqual(cyclic_ladder_sets(9, pi, 4), [selected])
        pred = predict_cyclic_ladder_minimal_fatal(9, pi, selected)
        self.assertEqual(pred["prediction"], "minimal_fatal")
        self.assertEqual(pred["reason"], "P3prime_lone_filler_image_below")
        cert = targeted_minimal_fatal_certificate(9, pi, selected)
        self.assertTrue(cert["minimal_fatal"])

    def test_size10_k11_cyclic_ladder_is_minimal_fatal(self):
        pi = construct_cyclic_ladder(11, 5)
        selected = tuple(range(10))
        self.assertEqual(cyclic_ladder_sets(11, pi, 5), [selected])
        pred = predict_cyclic_ladder_minimal_fatal(11, pi, selected)
        self.assertEqual(pred["prediction"], "minimal_fatal")
        self.assertEqual(pred["reason"], "P3prime_lone_filler_image_below")
        cert = targeted_minimal_fatal_certificate(11, pi, selected)
        self.assertTrue(cert["minimal_fatal"])

    def test_size10_k12_even_low_fillers_is_not_minimal_fatal(self):
        pi = construct_cyclic_ladder(12, 5)
        selected = tuple(range(10))
        self.assertEqual(cyclic_ladder_sets(12, pi, 5), [selected])
        pred = predict_cyclic_ladder_minimal_fatal(12, pi, selected)
        self.assertEqual(pred["prediction"], "not_minimal_fatal")
        cert = targeted_minimal_fatal_certificate(12, pi, selected)
        self.assertFalse(cert["minimal_fatal"])
        self.assertEqual(cert["reason"], "some_deletion_not_detachable")

    def test_size10_with_top_filler_triggers_p3(self):
        pi = construct_cyclic_ladder(12, 5, low_start=1)
        selected = tuple(range(10))
        pred = predict_cyclic_ladder_minimal_fatal(12, pi, selected)
        self.assertEqual(pred["prediction"], "minimal_fatal")
        self.assertEqual(pred["reason"], "P3_image_above")
        cert = targeted_minimal_fatal_certificate(12, pi, selected)
        self.assertTrue(cert["minimal_fatal"])

    def test_top_interval_peel_requires_contraction(self):
        pi = construct_cyclic_ladder(11, 5)
        selected = tuple(range(10))
        summary = top_interval_peel_summary(11, pi, selected)
        self.assertEqual(summary["status"], "ok")
        self.assertFalse(summary["delete_is_cycle"])
        self.assertTrue(summary["contracted_is_cycle"])
        self.assertEqual(summary["virtual_edge"], (0, 3))

    def test_v5_predictor_does_not_cover_size_two_pairs(self):
        pi = construct_cyclic_ladder(11, 5)
        pred = predict_cyclic_ladder_minimal_fatal(11, pi, (0, 1))
        self.assertEqual(pred["prediction"], "not_a_candidate")
        self.assertEqual(pred["reason"], "size_too_small")

    def test_contraction_sequence_keeps_virtual_cycles(self):
        pi = construct_cyclic_ladder(11, 5)
        selected = tuple(range(10))
        out = virtual_contraction_sequence(11, pi, selected)
        self.assertEqual(out["status"], "ok")
        self.assertTrue(all(row["cycle_ok"] for row in out["states"]))
        self.assertEqual(
            [row["active_intervals"] for row in out["states"]],
            [[0, 1, 2, 3, 4], [0, 1, 2, 3], [0, 1, 2]],
        )

    def test_triggered_ladder_triggers_before_any_contraction(self):
        pi = construct_cyclic_ladder(11, 5)
        selected = tuple(range(10))
        out = virtual_contraction_sequence(11, pi, selected)
        self.assertEqual(out["first_trigger_step"], 0)
        self.assertEqual(
            out["first_trigger"]["trigger"]["reason"],
            "P3prime_lone_filler_image_below",
        )

    def test_no_trigger_nonminimal_ladder_triggers_after_contraction(self):
        pi = construct_cyclic_ladder(12, 5)
        selected = tuple(range(10))
        out = virtual_contraction_sequence(12, pi, selected)
        self.assertEqual(out["states"][0]["trigger"]["prediction"], "not_minimal_fatal")
        self.assertEqual(out["first_trigger_step"], 1)
        self.assertEqual(out["first_trigger"]["trigger"]["reason"], "P3_image_above")
        self.assertEqual(out["first_trigger"]["absorbed_blocks"], [[6, 7], [8, 9]])

    def test_size8_no_trigger_case_triggers_after_one_contraction(self):
        pi = construct_cyclic_ladder(10, 4)
        selected = tuple(range(8))
        out = virtual_contraction_sequence(10, pi, selected)
        self.assertEqual(out["states"][0]["trigger"]["prediction"], "not_minimal_fatal")
        self.assertEqual(out["first_trigger_step"], 1)
        self.assertEqual(out["first_trigger"]["trigger"]["reason"], "P3_image_above")

    def test_original_trigger_witness_is_whole_ladder(self):
        pi = construct_cyclic_ladder(11, 5)
        selected = tuple(range(10))
        out = contracted_trigger_real_witness(11, pi, selected)
        self.assertEqual(out["status"], "original_trigger")
        self.assertEqual(out["trigger_step"], 0)
        self.assertEqual(out["witness"], list(selected))
        self.assertTrue(out["certificate"]["minimal_fatal"])

    def test_later_trigger_translates_to_absorbed_real_pair(self):
        pi = construct_cyclic_ladder(12, 5)
        selected = tuple(range(10))
        out = contracted_trigger_real_witness(12, pi, selected)
        self.assertEqual(out["status"], "absorbed_block_witness")
        self.assertEqual(out["trigger_step"], 1)
        self.assertEqual(out["witness"], [6, 7])
        self.assertTrue(out["certificate"]["minimal_fatal"])

    def test_size8_later_trigger_translates_to_absorbed_real_pair(self):
        pi = construct_cyclic_ladder(10, 4)
        selected = tuple(range(8))
        out = contracted_trigger_real_witness(10, pi, selected)
        self.assertEqual(out["status"], "absorbed_block_witness")
        self.assertEqual(out["trigger_step"], 1)
        self.assertEqual(out["witness"], [4, 5])
        self.assertTrue(out["certificate"]["minimal_fatal"])

    def test_later_external_trigger_can_be_harmless(self):
        pi = (0, 7, 8, 2, 3, 5, 9, 6, 1, 4)
        selected = (2, 3, 4, 5, 6, 7, 8, 9)
        out = contracted_trigger_real_witness(10, pi, selected)
        self.assertEqual(out["status"], "trigger_not_absorbed")
        self.assertEqual(out["trigger_step"], 1)
        self.assertEqual(out["trigger"]["reason"], "P3_image_above")
        self.assertTrue(completion_certificate(10, pi, selected)["detachable"])

    def test_cyclic_ladder_images_must_be_above_root_zero(self):
        """The generic ladder definition excludes selected image 0.

        Without this restriction, step-0 P3 can overpredict: the
        selected prefix below is detachable even though an external
        filler lies above its image range after naive classification.
        """
        pi = (4, 5, 1, 3, 6, 0, 7, 2)
        selected = (0, 1, 2, 3, 4, 5)
        self.assertEqual(cyclic_ladder_sets(8, pi, 3), [])
        pred = predict_cyclic_ladder_minimal_fatal(8, pi, selected)
        self.assertEqual(pred["prediction"], "not_a_candidate")
        self.assertEqual(pred["reason"], "not_adjacent_intervals")
        self.assertTrue(completion_certificate(8, pi, selected)["detachable"])

    def test_obstructive_classifier_ignores_external_trigger(self):
        pi = (0, 7, 8, 2, 3, 5, 9, 6, 1, 4)
        selected = (2, 3, 4, 5, 6, 7, 8, 9)
        out = contracted_obstructive_witness(10, pi, selected)
        self.assertEqual(out["status"], "no_obstructive_trigger")
        self.assertTrue(out["selected_detachable"])
        self.assertEqual(len(out["ignored_external_triggers"]), 1)

    def test_obstructive_classifier_keeps_absorbed_trigger(self):
        pi = construct_cyclic_ladder(12, 5)
        selected = tuple(range(10))
        out = contracted_obstructive_witness(12, pi, selected)
        self.assertEqual(out["status"], "absorbed_block_witness")
        self.assertEqual(out["witness"], [6, 7])
        self.assertTrue(out["certificate"]["minimal_fatal"])

    def test_obstructive_classifier_keeps_step_zero_trigger(self):
        pi = construct_cyclic_ladder(11, 5)
        selected = tuple(range(10))
        out = contracted_obstructive_witness(11, pi, selected)
        self.assertEqual(out["status"], "original_trigger")
        self.assertEqual(out["witness"], list(selected))
        self.assertTrue(out["certificate"]["minimal_fatal"])

    def test_obstructive_classifier_finds_contained_pair_base_case(self):
        pi = (5, 6, 4, 2, 1, 7, 3, 0)
        selected = (0, 1, 2, 3, 4, 5)
        out = contracted_obstructive_witness(8, pi, selected)
        self.assertEqual(out["status"], "contained_pair_witness")
        self.assertEqual(out["witness"], [0, 1])
        self.assertTrue(out["certificate"]["minimal_fatal"])

    def test_obstructive_classifier_finds_contained_ladder_base_case(self):
        pi = (2, 5, 1, 6, 3, 0, 7, 4)
        selected = (0, 1, 2, 3, 6, 7)
        out = contracted_obstructive_witness(8, pi, selected)
        self.assertEqual(out["status"], "contained_ladder_witness")
        self.assertEqual(out["witness"], [0, 1, 2, 3])
        self.assertTrue(out["certificate"]["minimal_fatal"])

    def test_step_zero_trigger_can_reduce_to_contained_ladder(self):
        pi = (2, 5, 0, 6, 8, 3, 7, 4, 1)
        selected = (0, 1, 4, 5, 6, 7)
        out = contracted_obstructive_witness(9, pi, selected)
        self.assertEqual(out["status"], "contained_ladder_witness")
        self.assertEqual(out["trigger_step"], 0)
        self.assertEqual(out["witness"], [4, 5, 6, 7])
        self.assertTrue(out["certificate"]["minimal_fatal"])

    def test_internal_gap_filler_refutes_unified_v5(self):
        """No P3/P3' trigger appears, but the size-6 ladder is
        minimally fatal.  The missing trigger is an internal gap filler
        between B-image intervals."""
        pi = (4, 0, 2, 8, 6, 1, 7, 5, 3)
        selected = (2, 3, 4, 5, 6, 7)
        out = contracted_obstructive_witness(9, pi, selected)
        self.assertEqual(out["status"], "internal_gap_witness")
        self.assertEqual(out["witness"], list(selected))
        self.assertTrue(out["certificate"]["minimal_fatal"])
        seq = out["sequence"]
        self.assertIsNone(seq["first_trigger_step"])
        self.assertEqual(seq["states"][0]["trigger"]["prediction"], "not_minimal_fatal")

    def test_internal_gap_profile_records_tautological_filler_fill(self):
        pi = (4, 0, 2, 8, 6, 1, 7, 5, 3)
        selected = (2, 3, 4, 5, 6, 7)
        profile = internal_gap_profile(9, pi, selected)
        self.assertEqual(profile["status"], "ok")
        self.assertEqual(profile["intervals"], [(1, 2), (5, 6), (7, 8)])
        self.assertEqual(profile["gaps"][0]["values"], (3, 4))
        self.assertEqual(profile["gaps"][0]["filler_indices"], (8, 0))
        self.assertTrue(profile["gaps"][0]["fully_filled_by_fillers"])
        self.assertTrue(profile["natural_odd_pairs"])

    def test_p4_classifies_natural_odd_internal_gap(self):
        pi = (4, 0, 2, 8, 6, 1, 7, 5, 3)
        selected = (2, 3, 4, 5, 6, 7)
        pred = predict_three_interval_internal_gap_fatal(9, pi, selected)
        self.assertEqual(pred["prediction"], "minimal_fatal")
        self.assertEqual(pred["reason"], "P4_natural_odd_internal_gap")
        cert = targeted_minimal_fatal_certificate(9, pi, selected)
        self.assertTrue(cert["minimal_fatal"])

    def test_misaligned_internal_gap_at_k8_is_detachable(self):
        pi = (0, 3, 1, 4, 2, 6, 5, 7)
        selected = (2, 3, 4, 5, 6, 7)
        pred = predict_three_interval_internal_gap_fatal(8, pi, selected)
        self.assertEqual(pred["prediction"], "not_minimal_fatal")
        self.assertEqual(pred["reason"], "P4_misaligned_internal_gap")
        self.assertFalse(pred["profile"]["natural_odd_pairs"])
        self.assertTrue(completion_certificate(8, pi, selected)["detachable"])

    def test_even_top_aligned_internal_gap_at_k10_is_detachable(self):
        pi = (1, 5, 8, 6, 7, 2, 3, 9, 0, 4)
        selected = (2, 3, 4, 5, 6, 7)
        pred = predict_three_interval_internal_gap_fatal(10, pi, selected)
        self.assertEqual(pred["prediction"], "not_minimal_fatal")
        self.assertEqual(pred["reason"], "P4_misaligned_internal_gap")
        self.assertEqual(pred["profile"]["intervals"], [(2, 3), (6, 7), (8, 9)])
        self.assertTrue(completion_certificate(10, pi, selected)["detachable"])

    def test_p4_classifies_larger_natural_odd_internal_gap(self):
        pi = (3, 1, 0, 8, 4, 9, 6, 5, 2, 10, 7)
        selected = (0, 1, 4, 5, 8, 9)
        pred = predict_three_interval_internal_gap_fatal(11, pi, selected)
        self.assertEqual(pred["prediction"], "minimal_fatal")
        self.assertEqual(pred["reason"], "P4_natural_odd_internal_gap")
        self.assertEqual(pred["profile"]["intervals"], [(1, 2), (3, 4), (9, 10)])
        cert = targeted_minimal_fatal_certificate(11, pi, selected)
        self.assertTrue(cert["minimal_fatal"])


if __name__ == "__main__":
    unittest.main()
