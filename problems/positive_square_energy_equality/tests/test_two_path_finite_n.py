"""Finite-n basic bound for the 2-path family L_n.

Conjecture (finite-n form, basic bound):
    For all n in {4, ..., 200},
        delta-(L_n) >= 17/16 and delta+(L_n) >= 17/16.

This is companion to test_two_path_widom_tightness.py (Role 2) but cleanly
separable: that test is about Widom sharpness, while this one is about the
basic finite-n threshold.

Data source: data/two_path_ear_gains.json (precomputed). If missing for a
particular n, fall back to direct spectral computation via spectrum_check.s_plus_minus
applied to the 2-path graph L_{n-2} (= k+2 vertices, where k = n - 2).
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import networkx as nx
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from spectrum_check import s_plus_minus  # noqa: E402
from family_check import two_path  # noqa: E402

THRESHOLD = 17.0 / 16.0
EPS = 1e-12

DATA_PATH = ROOT / "data" / "two_path_ear_gains.json"


# ----------------------------------------------------------------------
# Data loading
# ----------------------------------------------------------------------

def _load_two_path_data() -> dict:
    """Load {n: (delta+, delta-)} from data/two_path_ear_gains.json.
    Returns empty dict if file missing."""
    if not DATA_PATH.exists():
        return {}
    raw = json.loads(DATA_PATH.read_text())
    ns = raw["n"]
    dp = raw["delta_plus"]
    dm = raw["delta_minus"]
    return {int(n_i): (float(dp_i), float(dm_i))
            for n_i, dp_i, dm_i in zip(ns, dp, dm)}


_CACHED = _load_two_path_data()


def delta_plus_minus_two_path(n: int) -> tuple[float, float]:
    """Return (delta+(L_n), delta-(L_n)) for the 2-path with n vertices.

    Use cached data if available; otherwise compute via spectrum_check.
    L_n has n vertices; family_check.two_path(k) returns L_{k+2}.
    """
    if n in _CACHED:
        return _CACHED[n]
    k = n - 2
    G = two_path(k)
    H = two_path(k - 1)
    full = s_plus_minus(G)
    sub = s_plus_minus(H)
    return (full["s_plus"] - sub["s_plus"],
            full["s_minus"] - sub["s_minus"])


# ----------------------------------------------------------------------
# Test 1: parametrized over n in [4, 200]
# ----------------------------------------------------------------------

@pytest.mark.parametrize("n", list(range(4, 201)))
def test_two_path_min_delta_above_threshold(n):
    """delta+(L_n) >= 17/16 AND delta-(L_n) >= 17/16."""
    d_plus, d_minus = delta_plus_minus_two_path(n)
    assert d_minus >= THRESHOLD - EPS, (
        f"n={n}: delta-(L_n) = {d_minus} < 17/16 = {THRESHOLD}"
    )
    assert d_plus >= THRESHOLD - EPS, (
        f"n={n}: delta+(L_n) = {d_plus} < 17/16 = {THRESHOLD}"
    )


# ----------------------------------------------------------------------
# Test 2: trace identity delta+ + delta- = 4
# ----------------------------------------------------------------------

@pytest.mark.parametrize("n", [4, 5, 6, 10, 20, 50, 100, 200])
def test_two_path_trace_identity(n):
    """|delta+(L_n) + delta-(L_n) - 4| < 1e-9."""
    d_plus, d_minus = delta_plus_minus_two_path(n)
    s = d_plus + d_minus
    assert abs(s - 4.0) < 1e-9, (
        f"n={n}: delta+ + delta- = {s}, expected 4 (gap {abs(s-4):.2e})"
    )


# ----------------------------------------------------------------------
# Test 3: convergence to Szego limit
# ----------------------------------------------------------------------

def szego_limit_delta_minus() -> float:
    """delta-_inf(L) = (32 pi - 27 sqrt 3) / (12 pi)."""
    return (32.0 * math.pi - 27.0 * math.sqrt(3.0)) / (12.0 * math.pi)


def test_two_path_convergence_to_szego():
    """|delta-(L_200) - (32 pi - 27 sqrt 3)/(12 pi)| < 1e-3."""
    _, d_minus_200 = delta_plus_minus_two_path(200)
    lim = szego_limit_delta_minus()
    gap = abs(d_minus_200 - lim)
    assert gap < 1e-3, (
        f"n=200: delta-(L_200) = {d_minus_200}, Szego limit = {lim}, "
        f"gap = {gap:.6e} (expected < 1e-3)"
    )


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
