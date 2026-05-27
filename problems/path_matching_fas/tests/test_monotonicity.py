"""Regression tests for the fork-tree monotonicity theorem (D37).

  Theorem (Section 48):
    Let T_pi be a fork-tree pairing tournament.  For eps, eps' in {0,1}^k
    with eps_i <= eps'_i for all i, if eps' is extendable on T_pi then
    eps is extendable.

Equivalently, R(pi) is downward-closed in the {0,1}^k lattice.

Verified empirically across all pairings at k=4 and k=5 (24 + 120
pairings).
"""
from __future__ import annotations

import os
import sys

import pytest


SCRIPT_DIR = os.path.join(os.path.dirname(__file__), "..", "scripts")
sys.path.insert(0, os.path.abspath(SCRIPT_DIR))

from monotonicity_probe import (  # noqa: E402
    is_downward_closed,
    sweep_all,
    verify_pairing,
)
from relation_miner import extract_relation  # noqa: E402


def test_k4_exhaustive_monotonicity():
    out = sweep_all(4)
    assert out["violations"] == 0
    assert out["pairings_checked"] == 24


def test_k5_exhaustive_monotonicity():
    out = sweep_all(5)
    assert out["violations"] == 0
    assert out["pairings_checked"] == 120


def test_specific_k7_monotonicity_v6_failure_case():
    """V6 failure case from D30: pi=(5,3,2,6,4,0,1).  Verify
    monotonicity holds for this pairing."""
    out = verify_pairing(7, (5, 3, 2, 6, 4, 0, 1))
    assert out["downward_closed"], out


def test_specific_k7_size6_ladder():
    """R6 from D35: pi=(1,3,2,5,4,6,0)."""
    out = verify_pairing(7, (1, 3, 2, 5, 4, 6, 0))
    assert out["downward_closed"], out


def test_specific_k9_pairing():
    """A k=9 pairing — monotonicity should hold."""
    pi = (1, 3, 4, 5, 6, 0, 2, 8, 7)
    out = verify_pairing(9, pi)
    assert out["downward_closed"], out


def test_is_downward_closed_unit():
    # Trivial: full relation is downward-closed.
    R_full = frozenset((i, j, k) for i in (0, 1) for j in (0, 1) for k in (0, 1))
    ok, _ = is_downward_closed(R_full, 3)
    assert ok

    # 1-1-only is NOT downward-closed (missing (0,0)).
    R_bad = frozenset({(1, 1)})
    ok, _ = is_downward_closed(R_bad, 2)
    assert not ok

    # Standard negative-Horn relation: not (x and y).
    R_neg = frozenset({(0, 0), (0, 1), (1, 0)})
    ok, _ = is_downward_closed(R_neg, 2)
    assert ok


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
