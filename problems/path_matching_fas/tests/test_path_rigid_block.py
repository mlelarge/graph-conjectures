from __future__ import annotations

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from path_rigid_block import (  # noqa: E402
    aal_figure1_summary,
    verify_anchor_safe_block,
    verify_path_rigid_block,
)


class PathRigidBlockTest(unittest.TestCase):

    def test_aal_figure1_block_is_not_path_safe(self):
        info = aal_figure1_summary()
        self.assertEqual(info["forest_order_count"], 1)
        self.assertEqual(info["identity_max_degree"], 4)

    def test_recorded_replacement_block_is_path_rigid(self):
        cert = verify_path_rigid_block()
        self.assertEqual(cert["forest_order_count"], 1)
        self.assertEqual(cert["lfo_order_count"], 1)
        self.assertEqual(cert["path_order_count"], 1)
        self.assertEqual(cert["unique_order"], tuple(range(8)))
        self.assertEqual(cert["unique_max_degree"], 2)
        self.assertTrue(cert["unique_is_path"])

    def test_anchor_safe_replacement_block_has_spare_anchor_degree(self):
        cert = verify_anchor_safe_block()
        self.assertEqual(cert["forest_order_count"], 1)
        self.assertEqual(cert["lfo_order_count"], 1)
        self.assertEqual(cert["path_order_count"], 1)
        self.assertEqual(cert["unique_order"], tuple(range(9)))
        self.assertEqual(cert["unique_max_degree"], 2)
        self.assertTrue(cert["unique_is_path"])
        self.assertEqual(cert["anchor_degree"], 1)
        self.assertTrue(cert["anchor_can_accept_one_more_edge"])


if __name__ == "__main__":
    unittest.main()
