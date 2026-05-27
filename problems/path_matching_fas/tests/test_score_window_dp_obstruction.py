from __future__ import annotations

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from score_window_dp_obstruction import (  # noqa: E402
    analyze_reversed_matching,
    crossing_backarcs,
    degree_quota_profile,
    hall_active_bound,
    reversed_matching_tournament,
)
from pending_state_probe import (  # noqa: E402
    analyze_component_family,
    component_family_entropy,
    find_component_connectivity_witness,
)
from lfo_score_window import find_lfo_order_score_window, score_windows  # noqa: E402
from lfo_forced_flexible import find_lfo_order_forced_flexible  # noqa: E402
from ff_signature_probe import (  # noqa: E402
    find_active_signature_collision,
    find_visible_signature_collision,
)
from score_window_forced import (  # noqa: E402
    forced_flexible_decomposition,
    forced_obstruction,
)
from score_window_growth import ols, regress_growth, summarize  # noqa: E402
from score_window_random_probe import (  # noqa: E402
    random_tournament,
    run_skew,
    run_uniform,
    transitive_noise_tournament,
)
from verify import verify  # noqa: E402


class ScoreWindowDpObstructionTest(unittest.TestCase):

    def test_reversed_matching_family_is_lfo_with_unbounded_crossing_edges(self):
        for m in range(1, 13):
            T = reversed_matching_tournament(m)
            order = list(range(2 * m))
            info = verify(T, order)
            self.assertTrue(info["is_linear_forest"])
            self.assertTrue(info["is_matching"])
            self.assertEqual(info["count"], m)
            self.assertEqual(
                set(info["arcs"]),
                {(m + r, r) for r in range(m)},
            )
            self.assertEqual(len(crossing_backarcs(T, order, m)), m)

    def test_reversed_matching_family_has_constant_score_displacement(self):
        for m in range(2, 13):
            T = reversed_matching_tournament(m)
            order = list(range(2 * m))
            profile = degree_quota_profile(T, order)
            self.assertLessEqual(max(abs(row["delta"]) for row in profile), 1)
            for r in range(m):
                early = profile[r]
                late = profile[m + r]
                self.assertEqual(early["delta"], -1)
                self.assertEqual(early["earlier_out"], 0)
                self.assertEqual(early["later_in"], 1)
                self.assertEqual(late["delta"], 1)
                self.assertEqual(late["earlier_out"], 1)
                self.assertEqual(late["later_in"], 0)

    def test_hall_feasible_score_windows_have_bounded_active_count(self):
        for m in range(1, 20):
            T = reversed_matching_tournament(m)
            windows = score_windows(T)
            active = hall_active_bound(windows, 2 * m)
            self.assertTrue(active["hall_ok"])
            self.assertLessEqual(active["max_active"], active["hall_bound"])
            self.assertEqual(active["hall_bound"], 9)

    def test_analysis_records_the_naive_dp_obstruction(self):
        out = analyze_reversed_matching(10)
        self.assertTrue(out["is_lfo"])
        self.assertEqual(out["middle_crossing_backarc_count"], 10)
        self.assertEqual(out["max_abs_score_displacement"], 1)
        self.assertLessEqual(
            out["hall_active_bound"]["max_active"],
            out["hall_active_bound"]["hall_bound"],
        )

    def test_component_partition_changes_extendability(self):
        T = [
            [0, 0, 0, 0, 0, 0, 0],
            [1, 0, 0, 0, 0, 0, 0],
            [1, 1, 0, 0, 0, 0, 1],
            [1, 1, 1, 0, 0, 0, 0],
            [1, 1, 1, 1, 0, 0, 0],
            [1, 1, 1, 1, 1, 0, 0],
            [1, 1, 0, 1, 1, 1, 0],
        ]
        witness = find_component_connectivity_witness(T, depth=4)
        self.assertIsNotNone(witness)
        self.assertEqual(
            witness["state_a"]["prefix_mask"],
            witness["state_b"]["prefix_mask"],
        )
        self.assertEqual(
            witness["state_a"]["degree"],
            witness["state_b"]["degree"],
        )
        self.assertNotEqual(
            witness["state_a"]["components"],
            witness["state_b"]["components"],
        )
        self.assertNotEqual(
            witness["state_a"]["extendable"],
            witness["state_b"]["extendable"],
        )

    def test_component_partition_obstruction_repeats_independently(self):
        all_good = analyze_component_family(["good", "good", "good"])
        one_bad = analyze_component_family(["good", "bad", "good"])
        other_bad = analyze_component_family(["bad", "good", "good"])

        self.assertTrue(all_good["extendable"])
        self.assertFalse(one_bad["extendable"])
        self.assertFalse(other_bad["extendable"])

        self.assertEqual(all_good["prefix_mask"], one_bad["prefix_mask"])
        self.assertEqual(all_good["prefix_mask"], other_bad["prefix_mask"])
        self.assertEqual(all_good["degree"], one_bad["degree"])
        self.assertEqual(all_good["degree"], other_bad["degree"])
        self.assertNotEqual(all_good["components"], one_bad["components"])
        self.assertNotEqual(one_bad["components"], other_bad["components"])

    def test_component_family_has_exponential_pairing_entropy(self):
        out = component_family_entropy(4)
        self.assertEqual(out["states"], 16)
        self.assertEqual(out["coarse_key_count"], 1)
        self.assertEqual(out["component_partition_count"], 16)
        self.assertTrue(out["all_same_coarse_key"])
        self.assertTrue(out["all_component_partitions_distinct"])
        self.assertEqual(out["extendable_count"], 1)
        self.assertEqual(out["extendable_patterns"], [["good"] * 4])

    def test_forced_decomposition_catches_reversed_matching_edges(self):
        T = reversed_matching_tournament(10)
        out = forced_flexible_decomposition(T)
        self.assertTrue(out["hall_ok"])
        self.assertTrue(out["forced_linear_forest_ok"])
        self.assertEqual(
            set(out["forced_backedges"]),
            {(10 + r, r) for r in range(10)},
        )
        self.assertIsNone(forced_obstruction(T))

    def test_forced_decomposition_has_bounded_flexible_overlap(self):
        T = reversed_matching_tournament(10)
        out = forced_flexible_decomposition(T)
        self.assertLessEqual(out["max_active_windows"], 9)
        for u, v in out["flexible_pairs"]:
            lo_u, hi_u = out["windows"][u]
            lo_v, hi_v = out["windows"][v]
            self.assertFalse(hi_u < lo_v)
            self.assertFalse(hi_v < lo_u)

    def test_growth_summary_helpers(self):
        self.assertEqual(summarize([1, 2, 3, 100])["max"], 100)
        self.assertEqual(summarize([1, 2, 3, 100])["median"], 2.5)

        fit = ols([1.0, 2.0, 3.0], [2.0, 4.0, 6.0])
        self.assertAlmostEqual(fit["slope"], 2.0)
        self.assertAlmostEqual(fit["intercept"], 0.0)
        self.assertAlmostEqual(fit["r2"], 1.0)

        growth = regress_growth([
            {"n": 3, "max": 9, "p95": 8},
            {"n": 4, "max": 16, "p95": 14},
            {"n": 5, "max": 25, "p95": 21},
        ])
        self.assertEqual(growth["metric"], "max")
        self.assertEqual(growth["rows"], 3)

    def test_random_probe_helpers_are_deterministic_and_structured(self):
        import random

        rng_a = random.Random(7)
        rng_b = random.Random(7)
        self.assertEqual(random_tournament(5, rng_a), random_tournament(5, rng_b))

        transitive = transitive_noise_tournament(5, 0.0, random.Random(1))
        self.assertTrue(verify(transitive, list(range(5)))["count"] == 0)

        uniform = run_uniform([5], 3, 11, compare_forced_flexible=True)
        self.assertEqual(uniform["mode"], "uniform")
        self.assertEqual(uniform["groups"][0]["summary"]["nodes"]["count"], 3)
        self.assertEqual(uniform["groups"][0]["summary"]["ff_disagreements"], 0)

        skew = run_skew([6], [0.0, 0.2], 2, 11, compare_forced_flexible=True)
        self.assertEqual(skew["mode"], "skew")
        self.assertEqual(len(skew["groups"]), 2)

    def test_forced_flexible_solver_matches_pinned_families(self):
        for m in range(1, 8):
            T = reversed_matching_tournament(m)
            out = find_lfo_order_forced_flexible(T)
            self.assertTrue(out["found"])
            self.assertTrue(verify(T, out["order"])["is_linear_forest"])

    def test_forced_flexible_solver_matches_bruteforce_on_small_random(self):
        import random

        rng = random.Random(23)
        for n in range(3, 7):
            for _ in range(20):
                T = random_tournament(n, rng)
                out = find_lfo_order_forced_flexible(T)
                if out["found"]:
                    self.assertTrue(verify(T, out["order"])["is_linear_forest"])
                # Cross-check against the already-tested score-window solver
                # rather than factorial brute force here; n<=6 keeps this a
                # cheap equivalence test for the forced/flexible split.
                baseline = find_lfo_order_score_window(T)
                self.assertEqual(baseline["found"], out["found"])

    def test_naive_active_bag_signature_has_mixed_extendability(self):
        T = [
            [0, 0, 0, 0, 0, 0, 0],
            [1, 0, 0, 0, 0, 0, 0],
            [1, 1, 0, 0, 0, 0, 1],
            [1, 1, 1, 0, 0, 0, 0],
            [1, 1, 1, 1, 0, 0, 0],
            [1, 1, 1, 1, 1, 0, 0],
            [1, 1, 0, 1, 1, 1, 0],
        ]
        witness = find_active_signature_collision(T, depth=5)
        self.assertIsNotNone(witness)
        self.assertEqual(witness["signature"]["pos"], 4)
        self.assertEqual(
            witness["state_a"]["prefix_mask"],
            witness["state_b"]["prefix_mask"],
        )
        self.assertNotEqual(
            witness["state_a"]["extendable"],
            witness["state_b"]["extendable"],
        )

        repaired = find_visible_signature_collision(T, depth=5)
        self.assertIsNone(repaired)


if __name__ == "__main__":
    unittest.main()
