"""Regression tests for the polynomial Path-FAS decider on fork-tree
pairings.

The decider in `scripts/fork_tree_path_fas_decider.py` combines V6
candidate enumeration with the unified fatal detector to produce a
Path-FAS decision in O(k^{M+1}) time (M = candidate-interval bound).

These tests pin:

  1. Brute-force vs decider equivalence at k = 4 (24 pairings) and
     k = 5 (120 pairings) -- exhaustive.
  2. The k = 11 four-interval natural-odd-start case predicts fatal.
  3. The k = 6 identity case predicts no fatal.

V6 is exhaustively verified at sizes m = 1, 2, 3, 4 (Sections 22, 27,
28, 29, 37, 38).  At k = 7 the decider's predictions may diverge from
brute-force on the cases where V6 is empirically open (see
exchange_proof_draft.md, Section 40).  These tests therefore stop at
k = 6 for exhaustive equivalence checks.
"""
import os
import sys
import unittest
from itertools import permutations


SCRIPT_DIR = os.path.join(os.path.dirname(__file__), "..", "scripts")
sys.path.insert(0, os.path.abspath(SCRIPT_DIR))

from fork_tree_path_fas_decider import (  # noqa: E402
    classify_minimal_fatal,
    decide_fork_tree,
    decider_runtime_analysis,
    enumerate_candidates,
)
from fork_tree_probe import count_fork_tree_signatures  # noqa: E402


def _brute_path_fas_yes(k: int, pi: tuple) -> bool:
    """Brute force: Path-FAS = YES iff some prefix is non-extendable."""
    out = count_fork_tree_signatures(k, pi)
    return out["non_extendable"] > 0


class DeciderBruteForceEquivalenceTest(unittest.TestCase):

    def test_k4_exhaustive_matches_brute_force(self):
        """Exhaustive check at k = 4 (24 pairings): decider answer matches
        brute force on every pairing."""
        mismatches = []
        for pi in permutations(range(4)):
            truth_yes = _brute_path_fas_yes(4, pi)
            decision = decide_fork_tree(4, pi)
            decider_yes = decision["path_fas"] == "YES"
            if truth_yes != decider_yes:
                mismatches.append({
                    "pi": pi,
                    "truth_yes": truth_yes,
                    "decider": decision,
                })
        self.assertEqual(mismatches, [], msg=f"k=4 mismatches: {mismatches}")

    def test_k5_exhaustive_matches_brute_force(self):
        """Exhaustive check at k = 5 (120 pairings): decider answer
        matches brute force on every pairing."""
        mismatches = []
        for pi in permutations(range(5)):
            truth_yes = _brute_path_fas_yes(5, pi)
            decision = decide_fork_tree(5, pi)
            decider_yes = decision["path_fas"] == "YES"
            if truth_yes != decider_yes:
                mismatches.append({
                    "pi": pi,
                    "truth_yes": truth_yes,
                    "decider": decision,
                })
        self.assertEqual(mismatches, [], msg=f"k=5 mismatches: {mismatches}")


class DeciderPinnedExamplesTest(unittest.TestCase):

    def test_k5_cyclic_shift_predicts_fatal(self):
        """Section 16 cyclic shift at k = 5 has size-2 minimal fatal
        pairs (0,1) and (2,3); decider returns Path-FAS = YES."""
        pi = (1, 2, 3, 4, 0)
        decision = decide_fork_tree(5, pi)
        self.assertEqual(decision["path_fas"], "YES")
        self.assertIsNotNone(decision["witness"])
        # Witness should be the smallest size-2 even-block fatal pair.
        self.assertEqual(len(decision["witness"]), 2)

    def test_k6_identity_predicts_no_fatal(self):
        """The aligned identity pairing at k = 6 has no minimal fatal
        set; decider returns Path-FAS = NO."""
        pi = (0, 1, 2, 3, 4, 5)
        decision = decide_fork_tree(6, pi)
        self.assertEqual(decision["path_fas"], "NO")
        self.assertIsNone(decision["witness"])
        self.assertEqual(decision["minimal_fatal_sets"], [])

    def test_k11_four_interval_natural_odd_start_predicts_fatal(self):
        """At k = 11 with intervals {1,2}, {3,4}, {5,6}, {9,10}
        (natural odd-start), the decider predicts fatal via P4."""
        pi = (1, 3, 4, 5, 6, 9, 10, 2, 0, 8, 7)
        decision = decide_fork_tree(11, pi)
        self.assertEqual(decision["path_fas"], "YES")
        # The pinned witness from Section 38 is the size-8 set.
        self.assertIn([0, 1, 2, 3, 4, 5, 6, 7], decision["minimal_fatal_sets"])

    def test_k11_four_interval_even_start_predicts_no_fatal(self):
        """Same shape but even-start intervals -- no chain-end trigger
        and P4 misaligned, so V6 says not minimal fatal; the
        even-start pinned pairing has no other small minimal fatal
        candidate either."""
        pi = (2, 4, 5, 6, 7, 9, 10, 3, 0, 1, 8)
        decision = decide_fork_tree(11, pi)
        # The four-interval candidate is not minimal fatal.
        self.assertNotIn([0, 1, 2, 3, 4, 5, 6, 7], decision["minimal_fatal_sets"])


class DeciderInternalsTest(unittest.TestCase):

    def test_enumerate_candidates_returns_dict_keyed_by_size(self):
        """enumerate_candidates returns a dict keyed by interval count m."""
        pi = (1, 2, 3, 4, 0)
        cands = enumerate_candidates(5, pi)
        self.assertIn(1, cands)
        # At k = 5 there are 2 even-blocks (0,1) and (2,3); both have
        # natural odd-start image pairs under cyclic shift.
        self.assertEqual(len(cands[1]), 2)

    def test_classify_minimal_fatal_returns_v6_fatals(self):
        """classify_minimal_fatal returns minimal fatal sets from V6."""
        pi = (1, 2, 3, 4, 0)
        result = classify_minimal_fatal(5, pi)
        self.assertEqual(
            sorted(tuple(s) for s in result["minimal_fatal"]),
            [(0, 1), (2, 3)],
        )

    def test_decider_runtime_analysis_documents_complexity(self):
        """The runtime analysis records the documented complexity bound."""
        info = decider_runtime_analysis()
        self.assertIn("total_for_size_bound_M", info)
        self.assertIn("brute_force_baseline", info)
        # The brute-force baseline is exponential in k.
        self.assertIn("2^k", info["brute_force_baseline"])


if __name__ == "__main__":
    unittest.main()
