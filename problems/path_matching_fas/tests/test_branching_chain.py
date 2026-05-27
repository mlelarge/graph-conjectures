"""Regression test for the branching-chain probe.

The branching two-chain toggle family is the structural justification
for the single-chain hypothesis of the confluence/irrelevance lemma:

  - Without future chain (toggle family, Section 16): all 2^k extendable.
  - Single chain (chain-seeded toggle, Section 17.6): all 2^k extendable.
  - Two independent chains (this script): MIXED extendability at k>=3.

Hence sleeping-block correctly distinguishes the branching case, and any
sound confluence quotient must NOT collapse the branching toggle bits.
"""
import os
import sys
import unittest


SCRIPT_DIR = os.path.join(os.path.dirname(__file__), "..", "scripts")
sys.path.insert(0, os.path.abspath(SCRIPT_DIR))

from branching_chain_probe import count_branching_signatures  # noqa: E402


class BranchingChainTest(unittest.TestCase):

    def test_branching_chains_extendability_is_mixed_at_k_ge_3(self):
        """For k=3,4,5, the two-chain branching toggle family has at
        least one extendable and at least one non-extendable prefix.
        This pins the necessity of the single-chain hypothesis."""
        for k in (3, 4, 5):
            with self.subTest(k=k):
                out = count_branching_signatures(k)
                self.assertGreater(out["extendable"], 0)
                self.assertGreater(out["non_extendable"], 0)

    def test_branching_chains_full_signature_count_at_k_5(self):
        """At k=5 there are 32 distinct sleeping-block sigs (gadgets
        independent), of which 18 extend and 14 do not. Pinning the
        exact numbers detects accidental drift."""
        out = count_branching_signatures(5)
        self.assertEqual(out["extendable"], 18)
        self.assertEqual(out["non_extendable"], 14)
        self.assertEqual(out["distinct_sleeping_signatures"], 32)


if __name__ == "__main__":
    unittest.main()
