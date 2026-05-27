import os
import sys
import unittest


SCRIPT_DIR = os.path.join(os.path.dirname(__file__), "..", "scripts")
sys.path.insert(0, os.path.abspath(SCRIPT_DIR))

from quotient_signature_probe import (  # noqa: E402
    count_chain_seeded_quotient_signatures,
    count_toggle_quotient_signatures,
    find_quotient_extendability_collision,
)
from sleeping_block_skew_sweep import SKEW_TEMPLATES  # noqa: E402


class DependencyQuotientSignatureTest(unittest.TestCase):
    def test_dependency_quotient_collapses_toggle_family(self):
        for k in range(4, 8):
            with self.subTest(k=k):
                out = count_toggle_quotient_signatures(k)
                self.assertEqual(out["invalid"], [])
                self.assertEqual(out["quotient_signatures"], 1)
                self.assertEqual(out["largest_class"], 1 << k)

    def test_chain_seeded_toggle_refutes_dependency_quotient_bound(self):
        for k in range(3, 7):
            with self.subTest(k=k):
                out = count_chain_seeded_quotient_signatures(k)
                self.assertEqual(out["invalid"], [])
                self.assertEqual(out["quotient_signatures"], 1 << k)
                self.assertEqual(out["largest_class"], 1)
                self.assertEqual(out["collisions"], 0)
                self.assertEqual(out["extendabilities"], [True])

    def test_dependency_quotient_has_no_depth5_skew_collision(self):
        for name, T in SKEW_TEMPLATES.items():
            with self.subTest(template=name):
                self.assertIsNone(
                    find_quotient_extendability_collision(T, depth=5)
                )

    def test_dependency_quotient_survives_one_block_depth6(self):
        self.assertIsNone(
            find_quotient_extendability_collision(
                SKEW_TEMPLATES["one_block"],
                depth=6,
            )
        )


if __name__ == "__main__":
    unittest.main()
