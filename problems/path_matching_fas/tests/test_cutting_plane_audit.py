"""Regression test for the Cutting-Plane Oracle Structural Audit (D91).

Pins the decisive n=7 result: the full directed+undirected cycle-cut LP is
feasible-fractional on all 20/20 minimal-NO instances (no Farkas/LP
certificate), and the lazy oracle terminates with small integer cut sets.
See docs/cutting_plane_audit_status.md.
"""
from __future__ import annotations

import os
import sys

SCRIPT_DIR = os.path.join(os.path.dirname(__file__), "..", "scripts")
sys.path.insert(0, os.path.abspath(SCRIPT_DIR))

from cutting_plane_audit import (  # noqa: E402
    audit_catalogue, full_cycle_cut_lp, _all_undirected_cycles,
    _all_directed_cycles,
)


def test_cycle_enumeration_complete_and_yes_integral():
    """Validation: complete undirected-cycle enumeration on K_7 (1172),
    and the LP is integral on YES validation examples."""
    T_trans = [[1 if j > i else 0 for j in range(7)] for i in range(7)]
    assert len(_all_undirected_cycles(T_trans)) == 1172   # = Σ C(7,k)(k-1)!/2
    assert len(_all_directed_cycles(T_trans)) == 0        # acyclic
    lp = full_cycle_cut_lp(T_trans)
    assert lp["lp_feasible"] and lp["integral"] and lp["lp_value"] == 0.0
    T_3cycle = [[0, 1, 0], [0, 0, 1], [1, 0, 0]]
    lp3 = full_cycle_cut_lp(T_3cycle)
    assert lp3["lp_feasible"] and lp3["integral"] and lp3["lp_value"] == 1.0


def test_cutting_plane_route_blocked_n7():
    """The full cycle-cut LP is feasible-fractional on all 20/20 n=7
    minimal-NO instances: no LP/Farkas certificate -> route blocked."""
    out = audit_catalogue(7, limit=None, do_lp=True)
    assert out["instances"] == 20
    assert out["oracle_anomalies"] == 0
    assert out["lp_infeasible_cert"] == 0
    assert out["lp_feasible_fractional_GAP"] == 20
    assert out["lp_feasible_integral_BUG"] == 0
    # certificate sizes are small (integer-infeasibility, not LP)
    lo, hi, mean = out["oracle_cut_count_min_max_mean"]
    assert lo == 0 and hi == 20


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
