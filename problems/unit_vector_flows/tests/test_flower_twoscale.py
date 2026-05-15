"""Regression tests for the two-scale Procrustes fit machinery.

These pin the *measurement infrastructure*, not the existence of a
good two-scale model -- which the data refutes (see
[flower_twoscale.md](../docs/flower_twoscale.md)).
"""
from __future__ import annotations

import math

import numpy as np
import pytest

from flower_continuation import gauge_fix_state
from flower_transfer import extract_flower_state
from flower_twoscale import (
    candidate_trajectory,
    fit_two_scale,
    flow_residual_of_candidate,
    refine_two_scale,
    scan_periods,
)
from graphs import flower_snark
from witness import find_witness, orient


@pytest.fixture(scope="module", params=[2, 3])
def k(request):
    return request.param


@pytest.fixture(scope="module")
def fixed_state(k):
    n = 2 * k + 1
    G = flower_snark(k)
    r = find_witness(G, restarts=400, seed=2026, residual_threshold=1e-14)
    if r.status != "witness":
        pytest.skip(f"no witness for J_{n}")
    edges, _ = orient(G)
    state = extract_flower_state(G, edges, r.vectors, k)
    fs, _ = gauge_fix_state(state)
    return fs


def test_fit_p1_returns_well_formed(fixed_state):
    fit = fit_two_scale(fixed_state, p=1)
    assert fit.p == 1
    assert fit.R.shape == (3, 3)
    # R is SO(3)
    assert np.isclose(np.linalg.det(fit.R), 1.0, atol=1e-10)
    assert np.allclose(fit.R @ fit.R.T, np.eye(3), atol=1e-10)
    assert len(fit.Y_templates) == 1
    assert fit.Y_templates[0].shape == (3, 3)
    assert fit.rms_residual >= 0
    assert fit.per_step_residual.shape == (fixed_state.n,)


@pytest.mark.parametrize("p", [1, 2, 3])
def test_fit_per_step_residual_consistent_with_rms(fixed_state, p):
    if p >= fixed_state.n:
        pytest.skip(f"p={p} too large for n={fixed_state.n}")
    fit = fit_two_scale(fixed_state, p=p)
    rms_check = float(np.sqrt(np.mean(fit.per_step_residual ** 2)))
    assert np.isclose(rms_check, fit.rms_residual, atol=1e-12)


def test_refine_does_not_increase_residual(fixed_state):
    fit_p2 = fit_two_scale(fixed_state, p=2)
    refined = refine_two_scale(fixed_state, fit_p2)
    # Refinement starts from the Procrustes fit and can only improve
    # (or stay the same up to optimizer tolerance) the residual.
    assert refined.rms_residual <= fit_p2.rms_residual + 1e-8


def test_scan_periods_covers_full_range(fixed_state):
    fits = scan_periods(fixed_state, max_p=4, refine=False)
    n = fixed_state.n
    expected_keys = set(range(1, min(4, n - 1) + 1))
    assert set(fits.keys()) == expected_keys


def test_candidate_trajectory_is_periodic_under_R(fixed_state):
    """The reconstructed $\\hat X_i = R^i Y_{i \\bmod p}$ should
    satisfy $\\hat X_{i+p} = R^p \\hat X_i$ by construction."""
    fit = fit_two_scale(fixed_state, p=2)
    cand = candidate_trajectory(fit, fixed_state.n + 2)
    R_p = np.linalg.matrix_power(fit.R, fit.p)
    for i in range(fixed_state.n):
        expected = R_p @ cand[i]
        assert np.allclose(cand[i + fit.p], expected, atol=1e-10)


def test_flow_residual_well_formed(fixed_state):
    fit = fit_two_scale(fixed_state, p=2)
    cand = candidate_trajectory(fit, fixed_state.n)
    viol = flow_residual_of_candidate(cand, fixed_state)
    for key in [
        "unit_norm_B", "unit_norm_Oc", "unit_norm_Od",
        "chord_B", "chord_c_bulk", "chord_d_bulk",
        "kirchhoff_star", "max_violation",
    ]:
        assert key in viol
        assert viol[key] >= 0
