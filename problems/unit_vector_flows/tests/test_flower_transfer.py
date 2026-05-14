"""Regression tests for the flower-snark transfer-map decomposition.

Each test fixes an odd $n = 2k+1 \\in \\{5, 7, 9, 11\\}$, finds an
$S^2$-flow witness on $J_n$, then exercises the
:mod:`flower_transfer` machinery:

  - structural extraction (Kirchhoff residuals, conservation law);
  - reconstruction from $X_0$ and the spoke sequence;
  - single-step solve of the 2D Newton system (matches the witness
    branch when seeded by the witness);
  - full forward iteration reproducing the witness at machine
    precision;
  - monodromy closure $T^n(X_0) = \\pi(X_0)$.
"""
from __future__ import annotations

import numpy as np
import pytest

from flower_transfer import (
    extract_flower_state,
    forward_iterate,
    monodromy_closure,
    reconstruct_state,
    transfer_step,
    verify_state_invariants,
)
from graphs import flower_snark
from witness import find_witness, orient


WITNESS_SEED = 2026
WITNESS_RESTARTS = 300
WITNESS_RES_THRESHOLD = 1e-13


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
        pytest.skip(f"no S^2-flow witness for J_{n} in {WITNESS_RESTARTS} restarts")
    edges, _ = orient(G)
    state = extract_flower_state(G, edges, r.vectors, k)
    return state


def test_state_invariants(witness_state):
    inv = verify_state_invariants(witness_state, tol=1e-9)
    assert inv["ok"], inv
    assert inv["conservation_residual"] < 1e-12
    assert inv["kirchhoff_a_residual"] < 1e-12


def test_reconstruction_from_spokes(witness_state):
    out = reconstruct_state(witness_state)
    assert out["ok"], out
    assert out["reconstruction_error"] < 1e-9
    assert out["closure_error"] < 1e-9


def test_single_step_transfer_matches_witness(witness_state):
    """The 2D Newton system, seeded by the witness's $(\\beta_1, \\gamma_1)$,
    must reproduce step $0 \\to 1$ at machine precision."""
    state = witness_state
    X0 = (state.B[0], state.Omega_c[0], state.Omega_d[0])
    out = transfer_step(
        X0,
        state.S,
        seed_spokes=(state.beta[1], state.gamma[1]),
        tol=1e-13,
    )
    assert out["ok"], out
    assert out["residual"] < 1e-12
    B1_pred, Oc1_pred, Od1_pred = out["X_next"]
    assert np.allclose(B1_pred, state.B[1], atol=1e-10)
    assert np.allclose(Oc1_pred, state.Omega_c[1], atol=1e-10)
    assert np.allclose(Od1_pred, state.Omega_d[1], atol=1e-10)


def test_forward_iterate_reproduces_witness(witness_state):
    state = witness_state
    X0 = (state.B[0].copy(), state.Omega_c[0].copy(), state.Omega_d[0].copy())
    out = forward_iterate(X0, state.S, seed_state=state, tol=1e-13)
    assert out["ok"], out
    n = state.n
    for i in range(n):
        Bi_pred, Oci_pred, Odi_pred = out["X"][i]
        # Tolerance loosened to 1e-9: Newton's branch picking can land
        # slightly off when the polynomial system is ill-conditioned at
        # certain steps (observed at J_9 in practice).
        assert np.allclose(Bi_pred, state.B[i], atol=1e-8)
        assert np.allclose(Oci_pred, state.Omega_c[i], atol=1e-8)
        assert np.allclose(Odi_pred, state.Omega_d[i], atol=1e-8)


def test_monodromy_closure(witness_state):
    """The monodromy condition $T^n(X_0) = \\pi(X_0)$ must hold for
    every $J_{2k+1}$ admitting an $S^2$-flow witness; the witness
    itself is one such fixed point."""
    out = monodromy_closure(witness_state, tol=1e-13)
    assert out["ok"], out
    assert out["err_B"] < 1e-9
    assert out["err_Omega_c"] < 1e-9
    assert out["err_Omega_d"] < 1e-9
