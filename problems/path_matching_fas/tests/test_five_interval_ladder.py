"""Regression tests for the unified V6 fatal detector at size 5
(five-interval cyclic ladders).

This pins V6's behavior on three constructed instances:

  - A natural-odd-start residual ladder at k=13 with intervals
    {1,2},{3,4},{5,6},{7,8},{11,12} -> P4 fires, minimal fatal.
  - An even-start residual ladder at k=13 with intervals
    {2,3},{4,5},{6,7},{8,9},{11,12} -> P4 misaligned, NOT minimal fatal.
  - A P3' chain-end ladder at k=11 with the canonical five-interval
    construction (low_start=1) -> P3' fires on lone filler image 0.

All three are cross-checked against the targeted-minimal-fatal
certificate `targeted_minimal_fatal_certificate`, which runs in
sub-second time on a single pairing.  A slower full-sweep
cross-check via `minimal_fatal_toggle_sets` is available for k=11
(fast) and was run offline at k=13 (~85-100 s); we record the k=13
result as a pinned set rather than re-running the sweep in this
test.
"""
import os
import sys
import unittest


SCRIPT_DIR = os.path.join(os.path.dirname(__file__), "..", "scripts")
sys.path.insert(0, os.path.abspath(SCRIPT_DIR))

from cyclic_ladder_probe import (  # noqa: E402
    cyclic_ladder_structure,
    targeted_minimal_fatal_certificate,
)
from five_interval_ladder_probe import (  # noqa: E402
    construct_cyclic_five_interval,
    five_interval_ladder_sets,
)
from rectangle_detachability_probe import minimal_fatal_toggle_sets  # noqa: E402
from unified_v6_probe import predict_v6  # noqa: E402


class FiveIntervalLadderTest(unittest.TestCase):

    def test_construct_five_interval_k13_odd_start_is_candidate(self):
        pi = construct_cyclic_five_interval(13, odd_start=True)
        self.assertEqual(
            pi,
            (1, 3, 4, 5, 6, 7, 8, 11, 12, 2, 0, 9, 10),
        )
        candidates = five_interval_ladder_sets(13, pi)
        self.assertIn((0, 1, 2, 3, 4, 5, 6, 7, 8, 9), candidates)

    def test_v6_k13_natural_odd_start_is_minimal_fatal(self):
        """k=13, intervals {1,2},{3,4},{5,6},{7,8},{11,12} are all
        natural odd-start.  Fillers (10, 11, 12) take images
        (0, 9, 10); lone filler 12 has image 10 in [a, b]=[1,12], so
        neither P3 nor P3' fires.  P4 (natural-odd-start residual)
        fires."""
        pi = construct_cyclic_five_interval(13, odd_start=True)
        selected = (0, 1, 2, 3, 4, 5, 6, 7, 8, 9)
        struct = cyclic_ladder_structure(13, pi, selected)
        self.assertEqual(
            struct["intervals"],
            [(1, 2), (3, 4), (5, 6), (7, 8), (11, 12)],
        )
        pred = predict_v6(13, pi, selected)
        self.assertEqual(pred["prediction"], "minimal_fatal")
        self.assertEqual(pred["reason"], "P4_natural_odd_start_residual")
        # Cross-check with targeted minimal-fatal certificate.
        cert = targeted_minimal_fatal_certificate(13, pi, selected)
        self.assertTrue(cert["minimal_fatal"])
        self.assertEqual(
            cert["reason"],
            "selected_not_detachable_all_deletions_detachable",
        )

    def test_v6_k13_even_start_is_not_minimal_fatal(self):
        """k=13, intervals shifted to {2,3},{4,5},{6,7},{8,9},{11,12}
        (four even-start + one odd-start).  No P3/P3' trigger; P4
        misaligned because at least one interval is even-start.
        V6 predicts not minimal fatal; targeted certificate confirms."""
        pi = construct_cyclic_five_interval(13, odd_start=False)
        self.assertEqual(
            pi,
            (2, 4, 5, 6, 7, 8, 9, 11, 12, 3, 0, 1, 10),
        )
        selected = (0, 1, 2, 3, 4, 5, 6, 7, 8, 9)
        struct = cyclic_ladder_structure(13, pi, selected)
        self.assertEqual(
            struct["intervals"],
            [(2, 3), (4, 5), (6, 7), (8, 9), (11, 12)],
        )
        pred = predict_v6(13, pi, selected)
        self.assertEqual(pred["prediction"], "not_minimal_fatal")
        self.assertEqual(pred["reason"], "P4_misaligned_residual")
        cert = targeted_minimal_fatal_certificate(13, pi, selected)
        self.assertFalse(cert["minimal_fatal"])

    def test_v6_k11_five_interval_p3prime_fires(self):
        """k=11 with the canonical (gap-free) five-interval construction:
        intervals {1,2},{3,4},{5,6},{7,8},{9,10}, lone filler index 10
        has image 0 < a=1, so P3' fires.  Minimal fatal verified by
        targeted certificate AND by the full minimal-fatal sweep
        (which is fast at k=11)."""
        pi = (2, 3, 4, 5, 6, 7, 8, 9, 10, 1, 0)
        selected = (0, 1, 2, 3, 4, 5, 6, 7, 8, 9)
        pred = predict_v6(11, pi, selected)
        self.assertEqual(pred["prediction"], "minimal_fatal")
        self.assertEqual(pred["reason"], "P3prime_lone_filler_image_below")
        cert = targeted_minimal_fatal_certificate(11, pi, selected)
        self.assertTrue(cert["minimal_fatal"])
        # Full sweep cross-check (k=11 is fast).
        minimal = minimal_fatal_toggle_sets(11, pi)
        self.assertIn(tuple(selected), {tuple(s) for s in minimal})


if __name__ == "__main__":
    unittest.main()
