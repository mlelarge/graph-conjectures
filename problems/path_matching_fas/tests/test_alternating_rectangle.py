"""Regression test pinning the empirical characterization of fatal
toggle patterns on fork-tree pairings.

The Local Alternating-Rectangle Criterion (Section 22 of
exchange_proof_draft.md, working form) predicts:

  A toggle pair (i, i+1) is fatal iff some local-block condition
  combined with |pi(i+1) - pi(i)| = 1 holds.

This test verifies:

  (1) On all 24 pairings at k=4, the minimal fatal toggle pair is
      exactly (i, i+1) for some i, with i even and pi(i), pi(i+1)
      adjacent.  No fatal pair has i odd.

  (2) Identity-like and aligned-pairing cases have no fatal pattern,
      ruling out the simplest "adjacent + intra-block" criterion.
"""
import os
import sys
import unittest
from itertools import permutations


SCRIPT_DIR = os.path.join(os.path.dirname(__file__), "..", "scripts")
sys.path.insert(0, os.path.abspath(SCRIPT_DIR))

from fork_tree_probe import count_fork_tree_signatures  # noqa: E402


def _minimal_fatal_pairs(k, pi):
    """Return list of (i, j, pi[i], pi[j]) for two-bit minimal fatal sets."""
    out = count_fork_tree_signatures(k, pi)
    fatal = []
    for i in range(k):
        for j in range(i + 1, k):
            bits = [0] * k
            bits[i] = 1
            bits[j] = 1
            match = [
                r for r in out["by_bits"]
                if r["bits"] == bits and r["status"] == "ok"
            ]
            if match and not match[0]["extendable"]:
                fatal.append((i, j, pi[i], pi[j]))
    return fatal


class AlternatingRectangleEmpiricsTest(unittest.TestCase):

    def test_k4_all_pairings_minimal_fatal_has_even_adjacent_structure(self):
        """At k=4, every minimal fatal toggle pair satisfies:
          - j = i + 1 (consecutive gadget indices)
          - i is even
          - |pi(i+1) - pi(i)| = 1 (adjacent in B-chain)
        """
        for pi in permutations(range(4)):
            with self.subTest(pi=pi):
                fatal = _minimal_fatal_pairs(4, pi)
                for i, j, pi_i, pi_j in fatal:
                    self.assertEqual(j, i + 1, msg=f"non-consecutive {i},{j}")
                    self.assertEqual(i % 2, 0, msg=f"odd i={i}")
                    self.assertEqual(
                        abs(pi_i - pi_j),
                        1,
                        msg=f"non-adjacent pi-values {pi_i},{pi_j}",
                    )

    def test_k4_aligned_pairings_have_no_fatal(self):
        """Identity and identity-with-distant-swaps have no fatal pattern.
        This rules out the bare 'consecutive + adjacent pi-image' as a
        sufficient condition for fatality."""
        for pi in [(0, 1, 2, 3), (1, 0, 2, 3), (0, 1, 3, 2), (1, 0, 3, 2)]:
            with self.subTest(pi=pi):
                fatal = _minimal_fatal_pairs(4, pi)
                self.assertEqual(fatal, [])

    def test_k5_aligned_identity_has_no_fatal(self):
        """Identity at k=5 has no fatal pattern even though both
        (0,1) and (2,3) would naively be candidate rectangles."""
        fatal = _minimal_fatal_pairs(5, (0, 1, 2, 3, 4))
        self.assertEqual(fatal, [])

    def test_k5_cyclic_shift_fatal_pairs(self):
        """The cyclic shift pi(i) = i+1 mod 5 has exactly
        (0,1) and (2,3) as minimal fatal pairs."""
        fatal = _minimal_fatal_pairs(5, (1, 2, 3, 4, 0))
        self.assertEqual(
            sorted([(i, j) for (i, j, _, _) in fatal]),
            [(0, 1), (2, 3)],
        )


if __name__ == "__main__":
    unittest.main()
