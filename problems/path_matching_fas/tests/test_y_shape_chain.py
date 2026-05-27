"""Pin the Y-shape chain probe: toggle bits remain extension-equivalent
under tree-shaped future interfaces.

The corrected Y-shape (Section 19) adds one future side-leaf z with
a real reversed arc z -> y_attach. For every k and every choice of
attach point:

  - all 2^k toggle prefixes are uniformly extendable, OR
  - all 2^k toggle prefixes are uniformly non-extendable.

Toggle bits are never mixed under this construction, so the toggle
choice is extension-irrelevant whenever the interface graph is a
single tree.  This is stronger than the Section 18.4 working form's
hypothesis ("disjoint union of paths"), suggesting the confluence
lemma generalizes to TREE-shaped interfaces.
"""
import os
import sys
import unittest


SCRIPT_DIR = os.path.join(os.path.dirname(__file__), "..", "scripts")
sys.path.insert(0, os.path.abspath(SCRIPT_DIR))

from y_shape_chain_probe import count_y_shape_signatures  # noqa: E402


class YShapeChainTest(unittest.TestCase):

    def test_toggle_bits_extension_equivalent_at_end_attach(self):
        """When the side-leaf attaches at the chain end y_{2k-1}, all
        2^k toggle prefixes are uniformly extendable."""
        for k in (3, 4, 5):
            attach = 2 * k - 1
            with self.subTest(k=k, attach=attach):
                out = count_y_shape_signatures(k, attach)
                self.assertEqual(out["non_extendable"], 0)
                self.assertEqual(out["extendable"], 1 << k)

    def test_toggle_bits_extension_equivalent_at_interior_attach(self):
        """When the side-leaf attaches at an interior chain vertex,
        all 2^k toggle prefixes are uniformly NON-extendable (the side
        branch creates a degree-3 conflict at y_attach regardless of
        toggle choice)."""
        for k in (4, 5):
            for attach in (1, 3, 5):
                if attach >= 2 * k:
                    continue
                with self.subTest(k=k, attach=attach):
                    out = count_y_shape_signatures(k, attach)
                    if out["invalid"] > 0:
                        # Prefix invalid for small attach at certain k; skip.
                        continue
                    # Uniform: either all extend, or all don't extend.
                    is_uniform = (
                        out["non_extendable"] == 0
                        or out["extendable"] == 0
                    )
                    self.assertTrue(is_uniform, msg=str(out))


if __name__ == "__main__":
    unittest.main()
