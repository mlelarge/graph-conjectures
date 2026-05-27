"""Regression tests for the k=6 bijunctive analysis (D34 / Section 45).

Headline results (proved by exhaustive sweep over all 720 permutations
of [6]):

  1. Every minimal fatal toggle support at k=6 has size 2 or size 4.
     (Counts: 288 size-2 supports, 96 size-4 supports.)
  2. Every size-4 minimal fatal support is the union of two even-
     adjacent toggle blocks ({0,1}, {2,3}, {4,5}); the three block-
     pair unions ({0,1,2,3}, {0,1,4,5}, {2,3,4,5}) each occur as a
     minimal fatal support for exactly 32 of the 720 pairings.
  3. In every one of those 96 pairings, the size-4 minimal fatal
     support has NO size-2 fatal subset.  It is a "monogenic" size-4
     constraint.
  4. The V4 (Section 27, P3/P3') closed-form classifier correctly
     predicts every one of the 96 size-4 minimal fatal supports as
     fatal — so V4 is a complete fatal-set certifier at k=6.
  5. R(pi) is majority-closed (bijunctive) iff pi has no size-4
     minimal fatal support.  624 of the 720 pairings have a bijunctive
     R(pi); the other 96 do NOT.

Conclusion: the bijunctive theorem at k=6 is FALSE.  The fork-tree
legality relations at k=6 include genuine 4-clause obstructions of
the form NOT(eps[i] AND eps[j] AND eps[k] AND eps[l]).
"""
import os
import sys
import unittest

from itertools import permutations

SCRIPT_DIR = os.path.join(os.path.dirname(__file__), "..", "scripts")
sys.path.insert(0, os.path.abspath(SCRIPT_DIR))

from bijunctive_k6_probe import (  # noqa: E402
    analyze_pairing,
    legality_relation,
    majority_closure_ok,
    sweep_all,
)
from ordered_peeling_probe import predict_ladder_fatal  # noqa: E402
from rectangle_detachability_probe import (  # noqa: E402
    even_adjacent_blocks,
    minimal_fatal_toggle_sets,
)


_K6_CACHE: dict = {}


def _k6_summary() -> dict:
    """Cache the 720-pairing sweep so tests don't repeat the work."""
    if "result" not in _K6_CACHE:
        _K6_CACHE["result"] = sweep_all(6)
    return _K6_CACHE["result"]


class BijunctiveK6CatalogueTest(unittest.TestCase):

    def test_minimal_fatal_sizes_only_2_or_4(self):
        out = _k6_summary()
        self.assertEqual(out["pairings_with_size_outside_2_or_4"], 0)
        self.assertEqual(sorted(out["minimal_size_totals"].keys()), [2, 4])

    def test_minimal_fatal_counts(self):
        out = _k6_summary()
        # 288 size-2 supports and 96 size-4 supports across all 720 pis.
        self.assertEqual(out["minimal_size_totals"][2], 288)
        self.assertEqual(out["minimal_size_totals"][4], 96)
        self.assertEqual(out["minimal_total"], 384)
        self.assertEqual(out["pairings_with_size4_support"], 96)

    def test_size4_supports_are_three_block_pair_unions(self):
        out = _k6_summary()
        # Every size-4 minimal fatal support is the union of two of the
        # three even-adjacent toggle blocks {0,1},{2,3},{4,5}.
        block_pair_unions = {
            (0, 1, 2, 3),
            (0, 1, 4, 5),
            (2, 3, 4, 5),
        }
        seen: dict[tuple[int, ...], int] = {}
        for entry in out["catalogue"]:
            for s in entry["minimal_fatal_by_size"].get("4", []):
                t = tuple(s)
                self.assertIn(t, block_pair_unions,
                              f"unexpected size-4 support {t} for pi={entry['pi']}")
                seen[t] = seen.get(t, 0) + 1
        # Each of the three block-pair unions appears as a minimal
        # fatal support for exactly 32 pairings.
        self.assertEqual(seen[(0, 1, 2, 3)], 32)
        self.assertEqual(seen[(0, 1, 4, 5)], 32)
        self.assertEqual(seen[(2, 3, 4, 5)], 32)


class BijunctiveK6MonogenicSize4Test(unittest.TestCase):

    def test_size4_supports_have_no_contained_size2_fatal(self):
        out = _k6_summary()
        self.assertEqual(
            out["pairings_with_size4_missing_contained_pair"], 96,
            "every size-4 minimal fatal support at k=6 should be "
            "monogenic — i.e., contain no fatal pair as a subset",
        )

    def test_v4_detects_every_size4_minimal_fatal(self):
        out = _k6_summary()
        misses = 0
        total = 0
        for entry in out["catalogue"]:
            pi = tuple(entry["pi"])
            for s in entry["minimal_fatal_by_size"].get("4", []):
                total += 1
                pred = predict_ladder_fatal(6, pi, tuple(s))
                if pred["prediction"] != "fatal":
                    misses += 1
        self.assertEqual(total, 96)
        self.assertEqual(misses, 0,
                         "V4 must classify every size-4 minimal fatal "
                         "support as fatal at k=6")


class BijunctiveK6MajorityClosureTest(unittest.TestCase):

    def test_majority_closure_exactly_iff_no_size4_minimal(self):
        out = _k6_summary()
        # The dichotomy: a pairing's R is majority-closed iff it has
        # no size-4 minimal fatal support.
        for entry in out["catalogue"]:
            has_size4 = "4" in entry["minimal_fatal_by_size"]
            closed = entry["majority_closed"]
            self.assertEqual(closed, not has_size4,
                             f"closure-vs-size4 mismatch for pi={entry['pi']}")
        # The aggregate count: 96 pairings violate majority closure.
        self.assertEqual(out["pairings_with_majority_failure"], 96)

    def test_majority_failure_witness_for_canonical_example(self):
        """At pi=(1,3,2,4,0,5) the size-4 minimal fatal support is
        {0,1,2,3}.  R(pi) consists of all eps not having all four bits
        in positions 0..3 set.  This is the canonical 4-NAND, which is
        not majority-closed (the standard non-bijunctive obstruction)."""
        pi = (1, 3, 2, 4, 0, 5)
        R = legality_relation(6, pi)
        # R has 64 - 4 = 60 members.
        self.assertEqual(len(R), 60)
        # Concretely, no eps with eps[0..3] all 1 is in R.
        for eps in R:
            self.assertFalse(eps[0] == 1 and eps[1] == 1 and
                             eps[2] == 1 and eps[3] == 1)
        # Witness triple for majority failure: a = 001100, b = 110100,
        # c = 111000 are all in R; their majority is 111100 (NOT in R).
        a = (0, 0, 1, 1, 0, 0)
        b = (1, 1, 0, 1, 0, 0)
        c = (1, 1, 1, 0, 0, 0)
        m = (1, 1, 1, 1, 0, 0)
        self.assertIn(a, R)
        self.assertIn(b, R)
        self.assertIn(c, R)
        self.assertNotIn(m, R)


class BijunctiveK6TheoremStatusTest(unittest.TestCase):

    def test_bijunctive_theorem_at_k6_is_false(self):
        """The bijunctive theorem at k=6 is FALSE: there exist
        pairings whose legality relation R(pi) is not 2-SAT-expressible.

        The 96 counterexample pairings are exactly those with a size-4
        minimal fatal toggle support; each such R(pi) contains the
        4-clause NOT(eps[i] AND eps[j] AND eps[k] AND eps[l]) for a
        block-pair union {i,j,k,l}, and 4-clauses are not majority-
        closed.
        """
        out = _k6_summary()
        self.assertGreater(out["pairings_with_majority_failure"], 0)
        self.assertEqual(out["pairings_with_majority_failure"], 96)


if __name__ == "__main__":
    unittest.main()
