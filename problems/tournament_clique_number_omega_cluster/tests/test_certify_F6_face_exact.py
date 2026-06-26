import os
import sys

SCRIPTS = os.path.join(os.path.dirname(__file__), "..", "scripts")
sys.path.insert(0, os.path.abspath(SCRIPTS))

from certify_F6_face_exact import (  # noqa: E402
    certify_scan,
    maximal_boundary_slack,
    relevant_sub45_targets,
)


def test_boundary_slack_formula_matches_known_sub45_targets():
    assert maximal_boundary_slack(5, 7) == (1, 2)
    assert maximal_boundary_slack(6, 6) == (1, 1)
    assert maximal_boundary_slack(5, 8) == (1, 3)
    assert maximal_boundary_slack(6, 7) == (2, 2)
    assert maximal_boundary_slack(4, 11) == (1, 4)


def test_saved_two_cut_scan_certifies_F6_face_exact():
    cert = certify_scan()
    assert cert["F5"] == 25
    assert cert["F6"] == 45
    assert cert["targets_excluded"] == 52
    assert cert["sat_count"] == 0
    assert len(relevant_sub45_targets()) == 52
