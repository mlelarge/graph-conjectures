from __future__ import annotations

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from path_state_signature import (  # noqa: E402
    extend_known_block_search,
    summarize_two_state_port_block,
)


class PathStateSignatureTest(unittest.TestCase):

    def test_two_state_port_block_signature(self):
        summary = summarize_two_state_port_block()
        self.assertEqual(summary["lfo_order_count"], 2)
        self.assertEqual(sorted(summary["states"]), ["L", "R"])
        self.assertTrue(summary["left_y_endpoint_pair"])
        self.assertTrue(summary["right_n_endpoint_pair"])

    def test_recorded_block_still_has_inactive_port_obstruction(self):
        summary = summarize_two_state_port_block()
        self.assertFalse(summary["left_n_spare_capacity"])
        self.assertFalse(summary["right_y_spare_capacity"])

    def test_one_auxiliary_extension_does_not_fix_inactive_ports(self):
        summary = extend_known_block_search(extra_vertices=1)
        self.assertFalse(summary["found"])
        self.assertEqual(summary["checked_masks"], 128)
        self.assertEqual(summary["exact_two_state_extensions"], 20)
        self.assertEqual(summary["active_port_candidates"], 2)


if __name__ == "__main__":
    unittest.main()
