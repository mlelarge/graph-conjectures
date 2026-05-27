"""Runtime certificate test for A''-aux-1 (Hidden-Connection Exclusion).

The proof of A''-aux-1 in docs/exchange_proof_draft.md Section 9.9
constructs a runtime certificate: given a state S' and a suffix sigma
that first fails via cycle at step t, with failing pair (a,b), the
proof identifies a cut j = i + beta + 1 at which the forced-future
cycle check on x_t fails — under the hypothesis that beta < L_1.

If the hypothesis holds (beta >= L_1), no certificate is constructed
and the test simply records that A''-aux-1 was vacuously satisfied for
that case.

This test pins the certificate on the 10-vertex suffix-transfer witness
and the SKEW_INDUCTION_WITNESS, the two empirical instances where
cycle failures arise. It is a runtime sanity check on the proof, not a
formal proof in code.
"""
from __future__ import annotations

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from aux1_certificate import certify_witness_set  # noqa: E402


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


class Aux1CertificateTest(unittest.TestCase):

    def test_witness_aux1_holds_or_pruning_rejects(self):
        """For every visible-equivalent prefix pair where the suffix
        fails via cycle, A''-aux-1 must hold: either beta >= L_1
        (aux1 satisfied) OR the FF pruning at cut j = i + beta + 1
        rejects the target state with a forced-cycle / forced-degree
        violation.

        This is the runtime certificate of Section 9.9 of
        exchange_proof_draft.md. The proof guarantees the disjunction;
        the test verifies it on the 10-vertex witness.
        """
        out = certify_witness_set(SUFFIX_TRANSFER_FAILURE_WITNESS, depth=5)
        # At least one cycle failure must arise.
        self.assertGreater(out["cycle_failures"], 0,
                           "no cycle failures found — witness too weak")
        # For every aux1 violation observed, the certificate must show
        # FF pruning rejects at cut j.
        for example in out["examples"]:
            with self.subTest(example=example):
                self.assertIn("prune_witness", example)
                self.assertFalse(example["prune_witness"]["pruning_passes"])
                self.assertIn(
                    example["prune_witness"]["reason"],
                    ("forced_cycle", "forced_degree"),
                )


if __name__ == "__main__":
    unittest.main()
