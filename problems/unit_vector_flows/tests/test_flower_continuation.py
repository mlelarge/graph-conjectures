"""Regression tests for gauge-fixing and the reduced monodromy
continuation framework.

Tests cover:
  - gauge-fixing produces canonical form ($S = (0, 0, |S|)$, $B_0$ in
    $xz$-plane) without disturbing the structural invariants;
  - the reduced tangent basis is 2-by-9 orthonormal and orthogonal to
    the SO(2)-about-$\\hat z$ gauge direction;
  - the reduced 2-by-2 Jacobian at the witness has determinant bounded
    away from zero (the *headline* persistence diagnostic);
  - the predictor-corrector continuation in twist angle $\\theta$
    produces a non-empty branch starting at $\\theta = 0$, with the
    Jacobian determinant remaining bounded.
"""
from __future__ import annotations

import math

import numpy as np
import pytest

from flower_continuation import (
    continuation_in_twist,
    gauge_fix_state,
    reduced_jacobian,
    reduced_residual,
    reduced_tangent_basis,
)
from flower_transfer import extract_flower_state, verify_state_invariants
from graphs import flower_snark
from witness import find_witness, orient


WITNESS_SEED = 2026
WITNESS_RESTARTS = 400
WITNESS_RES_THRESHOLD = 1e-14


@pytest.fixture(scope="module", params=[2, 3, 5])
def k(request):
    return request.param


@pytest.fixture(scope="module")
def fixed_state(k):
    n = 2 * k + 1
    G = flower_snark(k)
    r = find_witness(
        G,
        restarts=WITNESS_RESTARTS,
        seed=WITNESS_SEED,
        residual_threshold=WITNESS_RES_THRESHOLD,
    )
    if r.status != "witness":
        pytest.skip(f"no S^2-flow witness for J_{n}")
    edges, _ = orient(G)
    state = extract_flower_state(G, edges, r.vectors, k)
    fs, _ = gauge_fix_state(state)
    return fs


def test_gauge_fix_canonical_form(fixed_state):
    # S aligned with +z
    S = fixed_state.S
    assert abs(S[0]) < 1e-12 and abs(S[1]) < 1e-12
    assert S[2] > 0
    # B[0] has zero y-component and non-negative x
    B0 = fixed_state.B[0]
    assert abs(B0[1]) < 1e-12
    assert B0[0] >= -1e-12


def test_gauge_fix_preserves_invariants(fixed_state):
    inv = verify_state_invariants(fixed_state, tol=1e-9)
    assert inv["ok"], inv
    assert inv["conservation_residual"] < 1e-12


def test_reduced_tangent_basis_orthonormal(fixed_state):
    X0 = (fixed_state.B[0], fixed_state.Omega_c[0], fixed_state.Omega_d[0])
    basis = reduced_tangent_basis(X0)
    assert basis.shape == (2, 9)
    gram = basis @ basis.T
    assert np.allclose(gram, np.eye(2), atol=1e-10)


def test_reduced_tangent_basis_orthogonal_to_gauge(fixed_state):
    """Each reduced tangent direction must have zero inner product with
    the analytical SO(2)-about-$\\hat z$ gauge direction."""
    X0 = (fixed_state.B[0], fixed_state.Omega_c[0], fixed_state.Omega_d[0])
    basis = reduced_tangent_basis(X0)
    # Build gauge direction: omega = (0, 0, 1), gauge = (omega x B, omega x Oc, omega x Od)
    z = np.array([0.0, 0.0, 1.0])
    g = np.concatenate([np.cross(z, X0[i]) for i in range(3)])
    g_norm = np.linalg.norm(g)
    if g_norm > 1e-10:
        for v in basis:
            assert abs(v @ g) / g_norm < 1e-10


def test_reduced_residual_vanishes_at_origin(fixed_state):
    r = reduced_residual(np.zeros(2), fixed_state)
    assert r is not None
    assert np.linalg.norm(r) < 1e-6


def test_reduced_jacobian_is_nonsingular(fixed_state):
    """The reduced 2-by-2 Jacobian at the witness must have a
    determinant bounded away from zero -- the explicit persistence
    diagnostic after gauge-fixing."""
    out = reduced_jacobian(fixed_state, eps=1e-7)
    assert out["singular_values"][-1] > 1e-3, out
    assert abs(out["det"]) > 0.1, out


def test_continuation_starts_cleanly_from_witness(fixed_state):
    """The continuation in twist angle must produce at least a few
    branch points starting at $\\theta = 0$, with the reduced determinant
    bounded below away from zero over the initial segment."""
    out = continuation_in_twist(
        fixed_state, theta_max=0.5, n_steps=8, newton_tol=1e-10
    )
    assert len(out["branch"]) >= 2, out
    # Initial point should match the witness
    b0 = out["branch"][0]
    assert b0.theta == 0.0
    assert b0.residual_norm < 1e-6
    # Determinant should not collapse over [0, 0.5]
    for bp in out["branch"]:
        assert abs(bp.det_J_reduced) > 1e-3, bp
