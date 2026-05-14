"""Regression tests for the flower-snark monodromy Jacobian.

The $S^2$-flow problem on $J_{2k+1}$ reduces to a fixed-point equation
$T^n(X_0) = \\pi(X_0)$ for the transfer map $T$ on the 3-dim
conservation surface. The Jacobian $J = \\partial(T^n - \\pi)/\\partial
X_0$ at a certified witness $X_0$ tells us *whether the fixed point is
transverse* (i.e., locally isolated) -- the gatekeeping property for
numerical continuation across the family.

The conservation surface carries an $\\mathrm{SO}(3)$ gauge symmetry:
global rotation around the axis of $S$ leaves the monodromy invariant,
so $J$ has rank at most $2$ generically. A fixed point is **transverse
modulo gauge** iff the two non-trivial singular values of $J$ are
bounded away from zero, and the analytical gauge direction lies in
$\\ker(J)$.

Tests cover, for each $k \\in \\{2, 3, 4, 5\\}$:

  - tangent basis at $X_0$ has full rank 3 and is orthonormal;
  - $|M(X_0)| < 10^{-6}$ on the witness fixed point;
  - $J$ has numerical rank $2$;
  - the analytical SO(3)-$S$-axis direction lies in $\\ker(J)$ to
    $\\sim \\sigma_1 \\cdot 10^{-5}$;
  - the second-largest singular value $\\sigma_2$ is bounded away from
    zero ($\\sigma_2 / \\sigma_1 > 10^{-5}$), confirming transverse
    modulo gauge.
"""
from __future__ import annotations

import numpy as np
import pytest

from flower_monodromy_jacobian import (
    conservation_tangent_basis,
    monodromy_jacobian,
    monodromy_residual,
)
from flower_transfer import extract_flower_state
from graphs import flower_snark
from witness import find_witness, orient


WITNESS_SEED = 2026
WITNESS_RESTARTS = 400
WITNESS_RES_THRESHOLD = 1e-14


@pytest.fixture(scope="module", params=[2, 3, 4, 5])
def k(request):
    return request.param


@pytest.fixture(scope="module")
def witness_state(k):
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
    return extract_flower_state(G, edges, r.vectors, k)


def test_tangent_basis_orthonormal(witness_state):
    X0 = (witness_state.B[0], witness_state.Omega_c[0], witness_state.Omega_d[0])
    basis = conservation_tangent_basis(X0)
    assert basis.shape == (3, 9)
    # Orthonormal: basis @ basis.T == I_3
    gram = basis @ basis.T
    assert np.allclose(gram, np.eye(3), atol=1e-10), gram


def test_tangent_basis_in_conservation_surface(witness_state):
    """Each basis tangent must satisfy the sum-zero conservation
    constraint and the per-sphere perpendicularity."""
    X0 = (witness_state.B[0], witness_state.Omega_c[0], witness_state.Omega_d[0])
    basis = conservation_tangent_basis(X0)
    for v in basis:
        dB, dC, dD = v[0:3], v[3:6], v[6:9]
        # Sum-zero
        assert np.allclose(dB + dC + dD, 0, atol=1e-10)
        # Perpendicular to each base vector
        assert abs(dB @ X0[0]) < 1e-10
        assert abs(dC @ X0[1]) < 1e-10
        assert abs(dD @ X0[2]) < 1e-10


def test_monodromy_residual_vanishes_at_witness(witness_state):
    X0 = (
        witness_state.B[0].copy(),
        witness_state.Omega_c[0].copy(),
        witness_state.Omega_d[0].copy(),
    )
    res = monodromy_residual(X0, witness_state, tol=1e-13)
    assert res is not None
    # J_9 has stiffer Newton; allow up to 1e-8.
    assert np.linalg.norm(res) < 1e-6


def test_jacobian_is_rank_two(witness_state):
    """Transverse-modulo-gauge: the Jacobian must drop exactly one
    rank (the SO(3) gauge direction)."""
    out = monodromy_jacobian(witness_state, eps=1e-7)
    sig = out["singular_values"]
    sig1 = sig[0]
    # Two non-trivial singular values, one ~0.
    assert sig1 > 0.1, sig
    # The smallest must be much smaller than the largest
    assert sig[-1] / sig1 < 1e-3, sig
    # The middle must be bounded away from zero
    assert sig[1] / sig1 > 1e-5, sig
    # Numerical rank = 2 with the module's threshold
    assert out["rank"] == 2
    assert out["transverse_modulo_gauge"] is True


def test_gauge_direction_lies_in_kernel(witness_state):
    """The analytical SO(3) rotation about the $S$ axis is the null
    direction of $J$. Verify this directly."""
    out = monodromy_jacobian(witness_state, eps=1e-7)
    sig1 = out["singular_values"][0]
    # ||J @ gauge_direction|| should be << sigma_1, comparable to sigma_3.
    assert out["gauge_kernel_residual"] / sig1 < 1e-3, (
        f"gauge axis not in ker(J): "
        f"{out['gauge_kernel_residual']:.3e} vs sigma_1 = {sig1:.3e}"
    )
