import os
import sys

SCRIPTS = os.path.join(os.path.dirname(__file__), "..", "scripts")
sys.path.insert(0, os.path.abspath(SCRIPTS))

from decide_two_cut import certify_parent, decide_two_cut, max_companion_slack  # noqa: E402


def test_two_cut_encoding_validates_on_depth3():
    result = decide_two_cut(3, 3, 5, 1, 2)
    assert result["sat"] and result["verified"]
    assert result["heights"] == (1, 3, 5)
    assert result["first_cut"] <= result["second_cut"]
    assert result["pre1_at_second_cut"] <= 1
    assert result["suf2_after_first_cut"] <= 2


def test_two_cut_certifies_depth4_parent():
    result = decide_two_cut(3, 3, 5, 1, 2)
    certified = certify_parent(result)
    assert certified["certified"]
    assert certified["certified_heights"][0] == 1
    assert certified["certified_product"] <= 15


def test_max_companion_slack_matches_F6_probe_targets():
    assert max_companion_slack(5, 7) == (1, 2)
    assert max_companion_slack(6, 6) == (1, 1)
    assert max_companion_slack(5, 8) == (1, 3)
    assert max_companion_slack(6, 7) == (2, 2)
