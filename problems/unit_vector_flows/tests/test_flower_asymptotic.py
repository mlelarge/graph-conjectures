"""Regression tests for the asymptotic-limit diagnostics on
flower-snark $S^2$-flows.

These tests pin the measurement infrastructure -- not the existence of
a smooth limit, which is the open research question. They check:

  - the Kabsch best-rotation extraction is consistent (R is SO(3) and
    the residual is the Frobenius norm);
  - the rotation_angle_axis decomposition correctly inverts to
    reconstruct R;
  - the FFT and autocorrelation are computed correctly on a canonical
    test sequence;
  - the smooth-limit diagnostic runs without error and returns a
    well-formed report.
"""
from __future__ import annotations

import math

import numpy as np
import pytest

from flower_asymptotic import (
    asymptotic_report,
    kabsch_rotation,
    rotation_angle_axis,
    smooth_limit_diagnostic,
)
from flower_continuation import gauge_fix_state
from flower_transfer import extract_flower_state
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


def test_kabsch_recovers_known_rotation():
    """Generate a known $R \\in \\mathrm{SO}(3)$, apply it to a random
    3-by-3 matrix, and check Kabsch recovers $R$."""
    rng = np.random.default_rng(42)
    axis = rng.normal(size=3)
    axis = axis / np.linalg.norm(axis)
    angle = 1.2
    K = np.array(
        [
            [0, -axis[2], axis[1]],
            [axis[2], 0, -axis[0]],
            [-axis[1], axis[0], 0],
        ]
    )
    R_true = np.eye(3) + math.sin(angle) * K + (1 - math.cos(angle)) * (K @ K)
    X_prev = rng.normal(size=(3, 3))
    X_curr = R_true @ X_prev
    R, res = kabsch_rotation(X_prev, X_curr)
    assert np.allclose(R, R_true, atol=1e-10)
    assert res < 1e-10
    assert np.isclose(np.linalg.det(R), 1.0, atol=1e-10)


def test_rotation_angle_axis_round_trip():
    """For a known angle/axis, build $R$ and verify the decomposition
    inverts."""
    angle = 0.8
    axis = np.array([1.0, 2.0, -3.0])
    axis = axis / np.linalg.norm(axis)
    K = np.array(
        [
            [0, -axis[2], axis[1]],
            [axis[2], 0, -axis[0]],
            [-axis[1], axis[0], 0],
        ]
    )
    R = np.eye(3) + math.sin(angle) * K + (1 - math.cos(angle)) * (K @ K)
    theta_back, axis_back = rotation_angle_axis(R)
    assert np.isclose(theta_back, angle, atol=1e-10)
    # axis may be flipped if signs differ; normalise to match
    if axis_back @ axis < 0:
        axis_back = -axis_back
        # theta = pi - theta would also be a valid representation, but
        # for small angles the axis convention is fixed.
    assert np.allclose(axis_back, axis, atol=1e-10)


def test_asymptotic_report_well_formed(fixed_state):
    """Run the full asymptotic_report on a witness and check shape /
    sanity of the output."""
    rep = asymptotic_report(fixed_state)
    n = fixed_state.n
    assert rep.n == n
    assert rep.S_magnitude > 0
    assert rep.step_angles_deg.shape == (n,)
    assert rep.step_axes.shape == (n, 3)
    assert rep.step_residuals.shape == (n,)
    assert 0 <= rep.step_axis_z_alignment <= 1.0
    assert rep.beta_fft_normalised.shape == (n,)
    # FFT[0] of beta is the sum of beta_i; since beta_i = B_i - B_{i-1}
    # around a cycle, sum is zero, so FFT[0] is ~0.
    assert rep.beta_fft_normalised[0] < 1e-6
    assert 0 <= rep.beta_dominant_freq <= n // 2
    assert 0 <= rep.beta_dominant_freq_normalised <= 0.5
    assert rep.beta_autocorr.shape == (n,)
    # Autocorr at lag 0 = mean |beta_i|^2 = 1 (unit vectors)
    assert abs(rep.beta_autocorr[0] - 1.0) < 1e-6


def test_smooth_limit_diagnostic_runs(fixed_state):
    """The cross-family diagnostic must return a well-formed dict even
    on a single-element family (degenerate trend slopes = 0)."""
    rep = asymptotic_report(fixed_state)
    diag = smooth_limit_diagnostic({fixed_state.n: rep})
    assert "smooth_limit_score" in diag
    assert "S_magnitudes" in diag
    assert "notes" in diag
    assert isinstance(diag["notes"], list)
    assert diag["smooth_limit_score_max"] == 3.0
