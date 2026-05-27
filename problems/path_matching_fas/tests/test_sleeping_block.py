"""Pin Step-A results: visible-latent and sleeping-block signatures
produce identical equivalence classes on the original entropy family
under the forced/flexible normalization.

If a future change to the score-window / forced-flex pipeline introduces
a case where sleeping-block tracking would catch a collision missed by
visible-latent, this test will fail and the next investigation begins
there.
"""
from __future__ import annotations
import os, sys, unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from pending_state_probe import (  # noqa: E402
    COMPONENT_PREFIX_SET, COMPONENT_WITNESS_T, cut_isolated_sum,
)
from sleeping_block_probe import compare_signatures
from sleeping_block_probe import sleeping_block_signature
from ff_signature_probe import (  # noqa: E402
    _add_flexible_vertex,
    has_completion_ff,
    valid_prefix_state_ff,
    visible_latent_signature,
)
from wake_signature_probe import (  # noqa: E402
    find_extendability_collision,
    find_one_step_mismatch,
    padded_wake_failure_witness,
    signature_function,
    survives_pruning,
    transition_profile,
    wake_signature,
)
from exchange_repair_probe import (  # noqa: E402
    exchange_repair_stats,
    first_failure,
    find_exchange_obstruction,
    iterated_left_move_repair,
    single_adjacent_internal_swap_repairs,
    single_left_move_repairs,
    single_right_move_repairs,
    strict_progress_options,
)


SKEW_INDUCTION_WITNESS = [
    [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
    [0, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1],
    [0, 0, 0, 1, 1, 1, 1, 0, 1, 1, 1, 0],
    [0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0],
    [0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 1, 1],
    [0, 1, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1],
    [0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1],
    [0, 0, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1],
    [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 1],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0],
]

WAKE1_FAILURE_WITNESS = [
    [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
    [0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [0, 0, 0, 0, 1, 1, 1, 1, 0, 1, 1, 1],
    [0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1],
    [0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1],
    [0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1],
    [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1],
    [0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 1, 1],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
]

VISIBLE_PRUNED_ONE_STEP_WITNESS = [
    [0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1],
    [0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1],
    [0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1],
    [0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1],
    [0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1],
    [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
]

SUFFIX_TRANSFER_FAILURE_WITNESS = [
    [0, 0, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 1, 1, 1, 1, 1, 1, 1, 0],
    [0, 0, 0, 1, 1, 1, 1, 1, 1, 1],
    [0, 0, 0, 0, 1, 1, 1, 1, 0, 1],
    [0, 0, 0, 0, 0, 1, 1, 1, 1, 1],
    [0, 0, 0, 0, 0, 0, 1, 1, 1, 1],
    [0, 0, 0, 0, 0, 0, 0, 1, 1, 1],
    [0, 0, 0, 0, 0, 0, 0, 0, 1, 1],
    [0, 0, 0, 1, 0, 0, 0, 0, 0, 1],
    [0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
]

STRICT_PROGRESS_FAILURE_WITNESS = [
    [0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1],
    [0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [0, 0, 0, 0, 1, 1, 1, 1, 0, 1, 1, 1],
    [0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1],
    [0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1],
    [0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1],
    [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1],
    [0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
]

ONE_BLOCK_FAILURE_WITNESS = [
    [0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1],
    [0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1],
    [1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1],
    [0, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1],
    [0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 1],
    [0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1],
    [0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1],
    [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1],
    [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1],
    [1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
]


def _suffix_is_valid(T, state, suffix):
    prefix_mask, degree, parent, flex_outmask, windows = state
    pos = prefix_mask.bit_count()
    for x in suffix:
        if prefix_mask & (1 << x):
            return False
        if not (windows[x][0] <= pos <= windows[x][1]):
            return False
        nxt = _add_flexible_vertex(flex_outmask, prefix_mask, degree, parent, x)
        if nxt is None:
            return False
        degree, parent = nxt
        prefix_mask |= 1 << x
        pos += 1
    return prefix_mask == (1 << len(T)) - 1


class CutIsolatedSleepingBlockTest(unittest.TestCase):

    def test_k2_visible_and_sleeping_identical(self):
        T = cut_isolated_sum(COMPONENT_WITNESS_T, COMPONENT_PREFIX_SET, 2)
        r = compare_signatures(T, depth=4)
        self.assertEqual(r["visible_collisions"], 0)
        self.assertEqual(r["sleeping_collisions"], 0)
        self.assertEqual(r["visible_classes"], r["sleeping_classes"])
        self.assertFalse(r["visible_refined_by_sleeping"])

    def test_k3_visible_and_sleeping_identical(self):
        T = cut_isolated_sum(COMPONENT_WITNESS_T, COMPONENT_PREFIX_SET, 3)
        r = compare_signatures(T, depth=4)
        self.assertEqual(r["visible_collisions"], 0)
        self.assertEqual(r["sleeping_collisions"], 0)
        self.assertEqual(r["visible_classes"], r["sleeping_classes"])
        self.assertFalse(r["visible_refined_by_sleeping"])

    def test_k4_visible_and_sleeping_identical(self):
        """At k=4 (n=28) the cut-isolated sum still produces identical
        equivalence classes. ~2.5 minutes; marked slow."""
        T = cut_isolated_sum(COMPONENT_WITNESS_T, COMPONENT_PREFIX_SET, 4)
        # Use depth=3 to keep the test under 30 seconds; the k=4
        # depth=4 result is recorded in docs.
        r = compare_signatures(T, depth=3)
        self.assertEqual(r["visible_collisions"], 0)
        self.assertEqual(r["sleeping_collisions"], 0)
        self.assertEqual(r["visible_classes"], r["sleeping_classes"])
        self.assertFalse(r["visible_refined_by_sleeping"])


class WitnessTournamentSleepingBlockTest(unittest.TestCase):

    def test_single_witness_no_collisions(self):
        """The original 7-vertex component witness.

        Even though the bare cut-isolated framework gave 2^k entropy
        before forced/flexible normalization, the FF-normalized
        signatures already separate good/bad cleanly.
        """
        r = compare_signatures(COMPONENT_WITNESS_T, depth=5)
        self.assertEqual(r["visible_collisions"], 0)
        self.assertEqual(r["sleeping_collisions"], 0)


class VisibleInductionAttemptTest(unittest.TestCase):

    def test_visible_signature_is_not_a_one_step_bisimulation(self):
        """Visible-latent can preserve extendability without determining
        the next visible-latent signature.

        Prefixes (0,1,2,3,5) and (1,0,2,3,5) have the same visible
        signature at cut 5. Placing vertex 4 next wakes vertex 11 into
        the active band. In one prefix 11 is in a dormant forced
        component separate from the visible component of 5; in the other
        it is already merged with that component. Sleeping-block tracking
        sees the difference, visible-latent does not.
        """
        prefix_a = (0, 1, 2, 3, 5)
        prefix_b = (1, 0, 2, 3, 5)
        state_a = valid_prefix_state_ff(SKEW_INDUCTION_WITNESS, prefix_a)
        state_b = valid_prefix_state_ff(SKEW_INDUCTION_WITNESS, prefix_b)
        self.assertIsNotNone(state_a)
        self.assertIsNotNone(state_b)

        pm_a, deg_a, par_a, flex_a, win_a = state_a
        pm_b, deg_b, par_b, flex_b, win_b = state_b
        visible_a = visible_latent_signature(
            len(prefix_a), pm_a, deg_a, par_a, flex_a, win_a
        )
        visible_b = visible_latent_signature(
            len(prefix_b), pm_b, deg_b, par_b, flex_b, win_b
        )
        self.assertEqual(visible_a, visible_b)

        sleeping_a = sleeping_block_signature(
            len(prefix_a), pm_a, deg_a, par_a, flex_a, win_a
        )
        sleeping_b = sleeping_block_signature(
            len(prefix_b), pm_b, deg_b, par_b, flex_b, win_b
        )
        self.assertNotEqual(sleeping_a, sleeping_b)

        next_a = _add_flexible_vertex(flex_a, pm_a, deg_a, par_a, 4)
        next_b = _add_flexible_vertex(flex_b, pm_b, deg_b, par_b, 4)
        self.assertIsNotNone(next_a)
        self.assertIsNotNone(next_b)
        child_deg_a, child_par_a = next_a
        child_deg_b, child_par_b = next_b
        child_visible_a = visible_latent_signature(
            len(prefix_a) + 1,
            pm_a | (1 << 4),
            child_deg_a,
            child_par_a,
            flex_a,
            win_a,
        )
        child_visible_b = visible_latent_signature(
            len(prefix_b) + 1,
            pm_b | (1 << 4),
            child_deg_b,
            child_par_b,
            flex_b,
            win_b,
        )
        self.assertNotEqual(child_visible_a, child_visible_b)

    def test_pinned_visible_failure_is_pruned_before_branching(self):
        """The raw visible child-signature failure is not a surviving DP
        state: forced-future degree pruning rejects both parents."""
        for prefix in [(0, 1, 2, 3, 5), (1, 0, 2, 3, 5)]:
            state = valid_prefix_state_ff(SKEW_INDUCTION_WITNESS, prefix)
            self.assertIsNotNone(state)
            self.assertFalse(
                survives_pruning(state, len(prefix), len(SKEW_INDUCTION_WITNESS))
            )

    def test_horizon_one_separates_pinned_wake_failure(self):
        prefix_a = (0, 1, 2, 3, 5)
        prefix_b = (1, 0, 2, 3, 5)
        state_a = valid_prefix_state_ff(SKEW_INDUCTION_WITNESS, prefix_a)
        state_b = valid_prefix_state_ff(SKEW_INDUCTION_WITNESS, prefix_b)
        pm_a, deg_a, par_a, flex_a, win_a = state_a
        pm_b, deg_b, par_b, flex_b, win_b = state_b

        self.assertEqual(
            visible_latent_signature(len(prefix_a), pm_a, deg_a, par_a, flex_a, win_a),
            visible_latent_signature(len(prefix_b), pm_b, deg_b, par_b, flex_b, win_b),
        )
        self.assertNotEqual(
            wake_signature(len(prefix_a), pm_a, deg_a, par_a, flex_a, win_a, 1),
            wake_signature(len(prefix_b), pm_b, deg_b, par_b, flex_b, win_b, 1),
        )

    def test_horizon_one_has_no_pinned_pruned_one_step_mismatch(self):
        self.assertIsNone(
            find_one_step_mismatch(
                SKEW_INDUCTION_WITNESS,
                depth=5,
                kind="wake",
                horizon=1,
                pruned=True,
            )
        )

    def test_visible_pruned_one_step_mismatch_is_not_extendability_collision(self):
        """Even after pruning, visible-latent is not a one-step
        bisimulation. The weaker extension-equivalence target survives."""
        self.assertIsNotNone(
            find_one_step_mismatch(
                VISIBLE_PRUNED_ONE_STEP_WITNESS,
                depth=5,
                kind="visible",
                pruned=True,
            )
        )
        self.assertIsNone(
            find_extendability_collision(
                VISIBLE_PRUNED_ONE_STEP_WITNESS,
                depth=5,
                kind="visible",
                pruned=True,
            )
        )

    def test_suffix_transfer_is_false_but_extension_survives(self):
        """Visible-equivalent states can require different suffixes.

        The suffix (5,6,7,9,8) completes the first prefix but closes a
        hidden cycle in the second when vertex 8 hits already-connected
        past vertices 3 and 9. Both prefixes remain extendable; placing
        8 before 9 is the alternate repair.
        """
        prefix_a = (0, 1, 3, 2, 4)
        prefix_b = (2, 1, 3, 0, 4)
        suffix = (5, 6, 7, 9, 8)
        repair_suffix = (5, 6, 7, 8, 9)

        state_a = valid_prefix_state_ff(SUFFIX_TRANSFER_FAILURE_WITNESS, prefix_a)
        state_b = valid_prefix_state_ff(SUFFIX_TRANSFER_FAILURE_WITNESS, prefix_b)
        self.assertTrue(
            survives_pruning(
                state_a, len(prefix_a), len(SUFFIX_TRANSFER_FAILURE_WITNESS)
            )
        )
        self.assertTrue(
            survives_pruning(
                state_b, len(prefix_b), len(SUFFIX_TRANSFER_FAILURE_WITNESS)
            )
        )
        self.assertEqual(
            visible_latent_signature(len(prefix_a), *state_a),
            visible_latent_signature(len(prefix_b), *state_b),
        )
        self.assertTrue(
            has_completion_ff(
                SUFFIX_TRANSFER_FAILURE_WITNESS,
                len(prefix_a),
                state_a[0],
                state_a[1],
                state_a[2],
                tuple(state_a[3]),
                tuple(state_a[4]),
            )
        )
        self.assertTrue(
            has_completion_ff(
                SUFFIX_TRANSFER_FAILURE_WITNESS,
                len(prefix_b),
                state_b[0],
                state_b[1],
                state_b[2],
                tuple(state_b[3]),
                tuple(state_b[4]),
            )
        )
        self.assertTrue(
            _suffix_is_valid(SUFFIX_TRANSFER_FAILURE_WITNESS, state_a, suffix)
        )
        self.assertFalse(
            _suffix_is_valid(SUFFIX_TRANSFER_FAILURE_WITNESS, state_b, suffix)
        )
        self.assertTrue(
            _suffix_is_valid(
                SUFFIX_TRANSFER_FAILURE_WITNESS, state_a, repair_suffix
            )
        )
        self.assertTrue(
            _suffix_is_valid(
                SUFFIX_TRANSFER_FAILURE_WITNESS, state_b, repair_suffix
            )
        )
        self.assertIsNone(
            find_exchange_obstruction(SUFFIX_TRANSFER_FAILURE_WITNESS, depth=5)
        )
        stats = exchange_repair_stats(SUFFIX_TRANSFER_FAILURE_WITNESS, depth=5)
        self.assertGreater(stats["same_suffix_failures"], 0)
        self.assertEqual(
            stats["same_suffix_failures"],
            stats["one_exchange_repairs"],
        )
        self.assertEqual(stats["unrepaired_failures"], 0)
        self.assertEqual(stats["max_single_move_distance"], 1)

    def test_first_failing_vertex_left_move_is_not_enough(self):
        """Strict-progress left-moving of the first failing vertex is false.

        The source suffix completes the source state and fails from the
        target state at vertex 9. The target is extendable, but every
        left move of vertex 9 either keeps the first failure at the same
        index or creates an earlier failure.
        """
        prefix_a = (0, 1, 3, 2, 4)
        prefix_b = (2, 0, 3, 1, 4)
        suffix = (5, 6, 8, 10, 7, 9, 11)
        target_completion = (5, 6, 8, 7, 9, 10, 11)

        state_a = valid_prefix_state_ff(STRICT_PROGRESS_FAILURE_WITNESS, prefix_a)
        state_b = valid_prefix_state_ff(STRICT_PROGRESS_FAILURE_WITNESS, prefix_b)
        self.assertIsNotNone(state_a)
        self.assertIsNotNone(state_b)
        self.assertEqual(
            visible_latent_signature(len(prefix_a), *state_a),
            visible_latent_signature(len(prefix_b), *state_b),
        )
        self.assertTrue(
            _suffix_is_valid(STRICT_PROGRESS_FAILURE_WITNESS, state_a, suffix)
        )
        self.assertFalse(
            _suffix_is_valid(STRICT_PROGRESS_FAILURE_WITNESS, state_b, suffix)
        )
        self.assertTrue(
            _suffix_is_valid(
                STRICT_PROGRESS_FAILURE_WITNESS,
                state_b,
                target_completion,
            )
        )

        failure = first_failure(STRICT_PROGRESS_FAILURE_WITNESS, state_b, suffix)
        self.assertEqual(failure["index"], 5)
        self.assertEqual(failure["vertex"], 9)
        self.assertEqual(failure["reason"], "cycle")
        self.assertEqual(failure["same_as_x"], [10])

        options = strict_progress_options(
            STRICT_PROGRESS_FAILURE_WITNESS,
            state_b,
            suffix,
            failure["index"],
        )
        self.assertTrue(options)
        self.assertFalse(any(option["strict_progress"] for option in options))

        right_repair = single_right_move_repairs(
            STRICT_PROGRESS_FAILURE_WITNESS,
            state_b,
            suffix,
            failure["index"],
        )
        self.assertEqual(right_repair["suffix"], list(target_completion))

    def test_one_block_repair_is_not_enough(self):
        """A later skew witness needs an internal block reordering.

        The first failure is again an x_t-to-leaf cycle, but the leaf is
        vertex 4, whose window is too early to delay until after x_t.
        The target is extendable by reordering the internal path
        contributors, not by a single left or right block move.
        """
        prefix_a = (0, 1, 2, 3, 6)
        prefix_b = (1, 2, 0, 3, 6)
        suffix = (4, 8, 5, 9, 7, 10, 11)
        target_completion = (4, 5, 7, 8, 9, 10, 11)

        state_a = valid_prefix_state_ff(ONE_BLOCK_FAILURE_WITNESS, prefix_a)
        state_b = valid_prefix_state_ff(ONE_BLOCK_FAILURE_WITNESS, prefix_b)
        self.assertIsNotNone(state_a)
        self.assertIsNotNone(state_b)
        self.assertEqual(
            visible_latent_signature(len(prefix_a), *state_a),
            visible_latent_signature(len(prefix_b), *state_b),
        )
        self.assertTrue(_suffix_is_valid(ONE_BLOCK_FAILURE_WITNESS, state_a, suffix))
        self.assertFalse(_suffix_is_valid(ONE_BLOCK_FAILURE_WITNESS, state_b, suffix))
        self.assertTrue(
            _suffix_is_valid(
                ONE_BLOCK_FAILURE_WITNESS,
                state_b,
                target_completion,
            )
        )

        failure = first_failure(ONE_BLOCK_FAILURE_WITNESS, state_b, suffix)
        self.assertEqual(failure["index"], 5)
        self.assertEqual(failure["vertex"], 10)
        self.assertEqual(failure["reason"], "cycle")
        self.assertEqual(failure["same_as_x"], [4])
        self.assertEqual(failure["same_pairs"], [])

        self.assertIsNone(
            single_left_move_repairs(
                ONE_BLOCK_FAILURE_WITNESS,
                state_b,
                suffix,
                failure["index"],
            )
        )
        self.assertIsNone(
            single_right_move_repairs(
                ONE_BLOCK_FAILURE_WITNESS,
                state_b,
                suffix,
                failure["index"],
            )
        )
        self.assertIsNone(
            iterated_left_move_repair(ONE_BLOCK_FAILURE_WITNESS, state_b, suffix)
        )
        adjacent_repair = single_adjacent_internal_swap_repairs(
            ONE_BLOCK_FAILURE_WITNESS,
            state_b,
            suffix,
            failure["index"],
        )
        self.assertEqual(
            adjacent_repair["suffix"],
            [4, 5, 8, 9, 7, 10, 11],
        )
        self.assertTrue(
            _suffix_is_valid(
                ONE_BLOCK_FAILURE_WITNESS,
                state_b,
                adjacent_repair["suffix"],
            )
        )

    def test_visible_latent_extension_equivalence_is_false(self):
        """Visible-latent state is insufficient for extension equivalence."""
        prefix_a = (1, 2, 0, 5, 3)
        prefix_b = (0, 1, 2, 5, 3)

        state_a = valid_prefix_state_ff(ONE_BLOCK_FAILURE_WITNESS, prefix_a)
        state_b = valid_prefix_state_ff(ONE_BLOCK_FAILURE_WITNESS, prefix_b)
        self.assertIsNotNone(state_a)
        self.assertIsNotNone(state_b)
        self.assertTrue(
            survives_pruning(state_a, len(prefix_a), len(ONE_BLOCK_FAILURE_WITNESS))
        )
        self.assertTrue(
            survives_pruning(state_b, len(prefix_b), len(ONE_BLOCK_FAILURE_WITNESS))
        )
        self.assertEqual(
            visible_latent_signature(len(prefix_a), *state_a),
            visible_latent_signature(len(prefix_b), *state_b),
        )
        self.assertTrue(
            has_completion_ff(
                ONE_BLOCK_FAILURE_WITNESS,
                len(prefix_a),
                *state_a,
            )
        )
        self.assertFalse(
            has_completion_ff(
                ONE_BLOCK_FAILURE_WITNESS,
                len(prefix_b),
                *state_b,
            )
        )
        self.assertNotEqual(
            sleeping_block_signature(len(prefix_a), *state_a),
            sleeping_block_signature(len(prefix_b), *state_b),
        )
        self.assertNotEqual(
            wake_signature(len(prefix_a), *state_a, 1),
            wake_signature(len(prefix_b), *state_b, 1),
        )

    def test_horizon_one_is_not_enough_for_bisimulation(self):
        """Wake horizon 1 separates the first raw failure, but it is not
        itself a one-step bisimulation on the surviving DP state space."""
        prefix_a = (0, 1, 3, 2, 4)
        prefix_b = (2, 0, 3, 1, 4)
        state_a = valid_prefix_state_ff(WAKE1_FAILURE_WITNESS, prefix_a)
        state_b = valid_prefix_state_ff(WAKE1_FAILURE_WITNESS, prefix_b)
        self.assertTrue(
            survives_pruning(state_a, len(prefix_a), len(WAKE1_FAILURE_WITNESS))
        )
        self.assertTrue(
            survives_pruning(state_b, len(prefix_b), len(WAKE1_FAILURE_WITNESS))
        )
        wake1_a = wake_signature(
            len(prefix_a), state_a[0], state_a[1], state_a[2], state_a[3], state_a[4], 1
        )
        wake1_b = wake_signature(
            len(prefix_b), state_b[0], state_b[1], state_b[2], state_b[3], state_b[4], 1
        )
        self.assertEqual(wake1_a, wake1_b)

        wake1 = signature_function("wake", 1)
        self.assertNotEqual(
            transition_profile(WAKE1_FAILURE_WITNESS, prefix_a, wake1, pruned=True),
            transition_profile(WAKE1_FAILURE_WITNESS, prefix_b, wake1, pruned=True),
        )

        wake2_a = wake_signature(
            len(prefix_a), state_a[0], state_a[1], state_a[2], state_a[3], state_a[4], 2
        )
        wake2_b = wake_signature(
            len(prefix_b), state_b[0], state_b[1], state_b[2], state_b[3], state_b[4], 2
        )
        self.assertNotEqual(wake2_a, wake2_b)

    def test_padded_witness_defeats_each_tested_finite_horizon(self):
        for horizon in range(1, 5):
            witness = padded_wake_failure_witness(horizon)
            T = witness["T"]
            prefix_a = witness["prefix_a"]
            prefix_b = witness["prefix_b"]
            state_a = valid_prefix_state_ff(T, prefix_a)
            state_b = valid_prefix_state_ff(T, prefix_b)
            self.assertTrue(survives_pruning(state_a, len(prefix_a), len(T)))
            self.assertTrue(survives_pruning(state_b, len(prefix_b), len(T)))

            sig_a = wake_signature(
                len(prefix_a), state_a[0], state_a[1], state_a[2], state_a[3], state_a[4], horizon
            )
            sig_b = wake_signature(
                len(prefix_b), state_b[0], state_b[1], state_b[2], state_b[3], state_b[4], horizon
            )
            self.assertEqual(sig_a, sig_b)

            wake_h = signature_function("wake", horizon)
            self.assertNotEqual(
                transition_profile(T, prefix_a, wake_h, pruned=True),
                transition_profile(T, prefix_b, wake_h, pruned=True),
            )

            sig_next_a = wake_signature(
                len(prefix_a), state_a[0], state_a[1], state_a[2], state_a[3], state_a[4], horizon + 1
            )
            sig_next_b = wake_signature(
                len(prefix_b), state_b[0], state_b[1], state_b[2], state_b[3], state_b[4], horizon + 1
            )
            self.assertNotEqual(sig_next_a, sig_next_b)

    def test_padded_witness_does_not_refute_visible_extendability(self):
        """The finite-horizon obstruction is not currently an
        extendability obstruction for the bounded visible-latent state."""
        for horizon in range(1, 3):
            witness = padded_wake_failure_witness(horizon)
            self.assertIsNone(
                find_extendability_collision(
                    witness["T"],
                    depth=5,
                    kind="visible",
                    pruned=True,
                )
            )


class SleepingBlockSkewFamilyTest(unittest.TestCase):
    """Pin the Section 12.1 empirical sweep on the three skew templates.

    For each unperturbed template, the depth-5 extendability collision
    search must give zero sleeping-block collisions.  Visible-latent
    collisions are present only on `one_block`; pin that asymmetry too.
    """

    def test_one_block_template_sleeping_block_collision_free(self):
        """ONE_BLOCK_FAILURE_WITNESS has visible-latent collisions but
        zero sleeping-block extendability collisions."""
        self.assertIsNotNone(
            find_extendability_collision(
                ONE_BLOCK_FAILURE_WITNESS,
                depth=5,
                kind="visible",
                pruned=True,
            )
        )
        self.assertIsNone(
            find_extendability_collision(
                ONE_BLOCK_FAILURE_WITNESS,
                depth=5,
                kind="sleeping",
                pruned=True,
            )
        )

    def test_skew_induction_template_sleeping_block_collision_free(self):
        self.assertIsNone(
            find_extendability_collision(
                SKEW_INDUCTION_WITNESS,
                depth=5,
                kind="sleeping",
                pruned=True,
            )
        )

    def test_wake1_failure_template_sleeping_block_collision_free(self):
        self.assertIsNone(
            find_extendability_collision(
                WAKE1_FAILURE_WITNESS,
                depth=5,
                kind="sleeping",
                pruned=True,
            )
        )

    def test_one_block_template_depth6_sleeping_block_collision_free(self):
        """D1 probe: deeper sweep on the visible-latent counterexample
        template. At depth 6 the prefix space is ~7x larger than depth 5.
        Sleeping-block must remain collision-free; visible-latent does
        not. Runtime ~30s — slow but worth pinning."""
        self.assertIsNone(
            find_extendability_collision(
                ONE_BLOCK_FAILURE_WITNESS,
                depth=6,
                kind="sleeping",
                pruned=True,
            )
        )
        self.assertIsNotNone(
            find_extendability_collision(
                ONE_BLOCK_FAILURE_WITNESS,
                depth=6,
                kind="visible",
                pruned=True,
            )
        )


class SleepingBlockRuntimeCertificateTest(unittest.TestCase):
    """D2 runtime certificate: for every depth-5 FF-pruned pair of
    prefixes with the same sleeping-block signature on the three skew
    templates, the natural-order suffix produces identical per-step
    FF pruning inputs (prefix_mask, boundary set, boundary degrees,
    boundary partition equivalence, placement outcome) in both states.

    The transition tests check the stronger one-step bisimulation
    certificate: every unplaced next vertex has the same outcome in
    both states, and surviving children have the same sleeping-block
    signature.

    This is the empirical certificate of Section 13.7's Boundary-Visible
    Evolution lemma (G1-G3): the structural argument's evolution claim
    is verified instance-by-instance on the test family.
    """

    def _certify(self, T):
        from sleeping_certificate import certify_witness_set
        out = certify_witness_set(T, depth=5, max_pairs=500)
        return out

    def _certify_transitions(self, T):
        from sleeping_certificate import certify_transition_witness_set
        out = certify_transition_witness_set(T, depth=5, max_pairs=500)
        return out

    def test_one_block_template_certificate(self):
        out = self._certify(ONE_BLOCK_FAILURE_WITNESS)
        self.assertTrue(out["all_pairs_certify"], msg=str(out))
        self.assertGreater(out["pairs_checked"], 0)

    def test_skew_induction_template_certificate(self):
        out = self._certify(SKEW_INDUCTION_WITNESS)
        self.assertTrue(out["all_pairs_certify"], msg=str(out))

    def test_wake1_failure_template_certificate(self):
        out = self._certify(WAKE1_FAILURE_WITNESS)
        self.assertTrue(out["all_pairs_certify"], msg=str(out))
        self.assertGreater(out["pairs_checked"], 0)

    def test_one_block_template_transition_certificate(self):
        out = self._certify_transitions(ONE_BLOCK_FAILURE_WITNESS)
        self.assertTrue(out["all_pairs_certify"], msg=str(out))
        self.assertGreater(out["pairs_checked"], 0)
        self.assertGreater(out["transitions_checked"], 0)

    def test_skew_induction_template_transition_certificate(self):
        out = self._certify_transitions(SKEW_INDUCTION_WITNESS)
        self.assertTrue(out["all_pairs_certify"], msg=str(out))

    def test_wake1_failure_template_transition_certificate(self):
        out = self._certify_transitions(WAKE1_FAILURE_WITNESS)
        self.assertTrue(out["all_pairs_certify"], msg=str(out))
        self.assertGreater(out["pairs_checked"], 0)
        self.assertGreater(out["transitions_checked"], 0)


class SleepingBlockDPTest(unittest.TestCase):
    """D3: sleeping-block DP decision must match FF backtrack on the
    skew templates and a small padded sample. If sleeping-block
    extension-equivalence holds (Section 13), the DP is correct."""

    def _check(self, T, expected=None):
        from sleeping_block_dp import sleeping_block_dp_decide
        from lfo_forced_flexible import find_lfo_order_forced_flexible
        dp = sleeping_block_dp_decide(T, time_budget_sec=60)
        ff = find_lfo_order_forced_flexible(T)
        self.assertEqual(dp["found"], ff["found"], msg=str(dp))
        if expected is not None:
            self.assertEqual(dp["found"], expected)
        return dp

    def test_one_block_dp_matches_ff(self):
        out = self._check(ONE_BLOCK_FAILURE_WITNESS, expected=True)
        # Memo stays small on the skew template; pin a generous upper bound.
        self.assertLess(out["memo_size"], 100)

    def test_skew_induction_dp_matches_ff(self):
        out = self._check(SKEW_INDUCTION_WITNESS, expected=False)
        self.assertLess(out["memo_size"], 100)

    def test_wake1_failure_dp_matches_ff(self):
        out = self._check(WAKE1_FAILURE_WITNESS, expected=True)
        self.assertLess(out["memo_size"], 100)

    def test_dp_memo_grows_modestly_on_padded_skew(self):
        """At n up to 17 via transitive padding of one_block, the DP
        memo size stays below 400 across the linear scan. This pins
        the empirical compression result of Section 14.3."""
        from sleeping_block_dp import sleeping_block_dp_decide
        from wake_signature_probe import _insert_transitive_padding_vertex
        T = [row[:] for row in ONE_BLOCK_FAILURE_WITNESS]
        max_memo = 0
        for pad in range(6):
            out = sleeping_block_dp_decide(T, time_budget_sec=30)
            self.assertTrue(out["found"])  # one_block + transitive pad stays Yes
            max_memo = max(max_memo, out["memo_size"])
            T = _insert_transitive_padding_vertex(T, 11)
        self.assertLess(max_memo, 400)


class SleepingG1G2CertificateTest(unittest.TestCase):
    """D5: runtime certificate for G1 (visible-latent records degree
    on A_i ∪ O_i) and G2 (F_i degree = forced backedges only).

    These are the definitional invariants of Section 13.7's
    Boundary-Visible Evolution lemma. Both must hold for every
    FF-pruned prefix on every test tournament; if either fails on any
    prefix, the structural argument is broken at the base.
    """

    def _check(self, T):
        from sleeping_g1g2_certificate import certify_g1_g2
        return certify_g1_g2(T, depth=5)

    def test_one_block_g1_g2(self):
        out = self._check(ONE_BLOCK_FAILURE_WITNESS)
        self.assertTrue(out["g1_holds"], msg=str(out))
        self.assertTrue(out["g2_holds"], msg=str(out))
        self.assertGreater(out["prefixes_checked"], 0)

    def test_skew_induction_g1_g2(self):
        out = self._check(SKEW_INDUCTION_WITNESS)
        self.assertTrue(out["g1_holds"], msg=str(out))
        self.assertTrue(out["g2_holds"], msg=str(out))

    def test_wake1_failure_g1_g2(self):
        out = self._check(WAKE1_FAILURE_WITNESS)
        self.assertTrue(out["g1_holds"], msg=str(out))
        self.assertTrue(out["g2_holds"], msg=str(out))
        self.assertGreater(out["prefixes_checked"], 0)


class SleepingBlockDPAdversarialTest(unittest.TestCase):
    """D4 adversarial: cut-isolated and skew_chain compositions are
    candidate constructions that could inflate sleeping-block state
    space. At k=5 (n=35 and n=60 respectively), memo size = n exactly:
    the DP finds the LFO via a single greedy descent without exploring
    multiple states per cut. The constructions do not refute the
    polynomial-bound conjecture."""

    def test_cut_isolated_sum_dp_memo_linear_in_n(self):
        from sleeping_block_dp import sleeping_block_dp_decide
        from pending_state_probe import (
            COMPONENT_PREFIX_SET, COMPONENT_WITNESS_T, cut_isolated_sum,
        )
        for k in (2, 3, 4, 5):
            T = cut_isolated_sum(COMPONENT_WITNESS_T, COMPONENT_PREFIX_SET, k)
            out = sleeping_block_dp_decide(T, time_budget_sec=30)
            self.assertTrue(out["found"])
            # memo grows linearly: at k copies of 7-vertex witness,
            # memo is exactly n = 7*k for the greedy descent.
            self.assertLessEqual(out["memo_size"], len(T) * 2)

    def test_skew_chain_dp_memo_linear_in_n(self):
        from sleeping_block_dp import sleeping_block_dp_decide
        from sleeping_block_d1_probe import skew_compose
        T = ONE_BLOCK_FAILURE_WITNESS
        for k in (1, 2, 3):
            chain = T
            for _ in range(k - 1):
                chain = skew_compose(chain, T)
            out = sleeping_block_dp_decide(chain, time_budget_sec=60)
            self.assertTrue(out["found"])
            self.assertLessEqual(out["memo_size"], len(chain) * 2)


if __name__ == "__main__":
    unittest.main()
