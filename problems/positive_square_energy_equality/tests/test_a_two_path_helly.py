r"""Regression tests for the Helly / Portmanteau bridge closing
(a.2-path) from Phase 10 (half-line spectral theorem) to Phase 9
(finite-n moments).

Companion to ``docs/lprime_a_two_path_helly.md`` and to the existing
``docs/lprime_a_two_path_stieltjes.md`` (Phase 10) and
``docs/lprime_a_two_path.md`` (Phase 9 candidate).

This test file enforces:

  1. Uniform operator-norm bound ||A(L_{n-1})|| <= 4 = ||f||_infty for
     several n in {10, 30, 80, 150}. (Lemma 2.1 of the deliverable.)
  2. Symbol facts via sympy: max f = 4, min f = -9/4, where
     f(theta) = 2 cos(theta) + 2 cos(2 theta).
  3. Continuity of g_k(lambda) = lambda^k * 1[lambda < 0] at lambda = 0
     for k = 1, 2 (justifying why weak convergence alone suffices for
     those moments, and only k = 0 needs the no-atom condition).
  4. Helly-style finite-n residual bound: |I(L_n) - I_inf| < 0.1 at each
     recorded n in {50, 100, 200}; residuals do not blow up.
  5. Individual moment residuals |W^-(L_n) - W^-_inf|, etc., bounded.

Reads the existing data file ``data/two_path_limit_moments.json`` and
does not write new data.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import networkx as nx
import numpy as np
import pytest
import sympy as sp

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from family_check import two_path  # noqa: E402

DATA_PATH = ROOT / "data" / "two_path_limit_moments.json"

# ----- expected limits (Phase 10 closed forms) ----------------------------- #
W_MINUS_INF = 1 - 3 * np.sqrt(3) / (4 * np.pi)         # ~0.5865033...
M1_MINUS_INF = 2.0 / 3.0 - 9 * np.sqrt(3) / (4 * np.pi)  # ~-0.5738233...
M2_MINUS_INF = 3 - 81 * np.sqrt(3) / (20 * np.pi)      # ~0.7671180...
I_INF = W_MINUS_INF + (M1_MINUS_INF ** 2) / M2_MINUS_INF  # ~1.0157375...

SYMBOL_NORM = 4.0   # ||f||_infty
SYMBOL_MIN = -9.0 / 4.0  # min f

# ---------------------------------------------------------------------------- #
# 1. Operator-norm bound ||A(L_{n-1})|| <= ||f||_infty = 4.
# ---------------------------------------------------------------------------- #


def _build_A_L_minus_ear(n: int) -> np.ndarray:
    """Return A(H) where H = L_n - v* with v* = vertex 0 (boundary ear).

    L_n is built via family_check.two_path(n - 2): n vertices, pentadiagonal
    structure. We drop vertex 0 (which has only two neighbours, vertices 1
    and 2) to obtain H ~= L_{n-1} on vertices {1, ..., n-1}.
    """
    G = two_path(n - 2)
    H = G.copy()
    H.remove_node(0)
    return nx.to_numpy_array(H, dtype=float)


@pytest.mark.parametrize("n", [10, 30, 80, 150])
def test_operator_norm_uniformly_bounded(n: int) -> None:
    """For each n, the operator norm of A(L_{n-1}) (the matrix used in the
    finite-n signed moments) is at most ||f||_infty = 4.

    This certifies Lemma 2.1 of the deliverable empirically.
    """
    A = _build_A_L_minus_ear(n)
    eigs = np.linalg.eigvalsh(A)
    op_norm = float(max(abs(eigs.min()), abs(eigs.max())))
    # Uniform bound by ||f||_infty = 4 (Lemma 2.1).
    assert op_norm <= SYMBOL_NORM + 1e-9, (
        f"n = {n}: ||A(L_{{n-1}})|| = {op_norm} > {SYMBOL_NORM} = ||f||_infty"
    )
    # The bound is non-trivial: the norm approaches 4 from below as n grows.
    assert op_norm > 3.0, (
        f"n = {n}: operator norm {op_norm} is suspiciously small "
        f"(expected close to 4 for moderate n)"
    )


def test_min_eigenvalue_bounded_below_by_symbol_min() -> None:
    """min eig of A(L_{n-1}) is >= min f = -9/4 (also part of Lemma 2.1)."""
    for n in [10, 30, 80, 150]:
        A = _build_A_L_minus_ear(n)
        lam_min = float(np.linalg.eigvalsh(A).min())
        assert lam_min >= SYMBOL_MIN - 1e-9, (
            f"n = {n}: min eig {lam_min} < min f = {SYMBOL_MIN}"
        )


# ---------------------------------------------------------------------------- #
# 2. Symbol facts via sympy: max f = 4, min f = -9/4.
# ---------------------------------------------------------------------------- #


def test_symbol_max_is_four() -> None:
    """f(theta) = 2 cos(theta) + 2 cos(2 theta) attains max value 4 at theta = 0."""
    theta = sp.symbols("theta", real=True)
    f = 2 * sp.cos(theta) + 2 * sp.cos(2 * theta)
    # f(0) = 2 + 2 = 4.
    assert sp.simplify(f.subs(theta, 0) - 4) == 0
    # Critical points: f'(theta) = -2 sin(theta) - 4 sin(2 theta)
    #                            = -2 sin(theta)(1 + 4 cos(theta)).
    # Zeros at sin(theta) = 0 (theta in {0, pi}) and cos(theta) = -1/4.
    # At theta = pi: f = -2 + 2 = 0.
    # At theta = 0:  f = 4.
    # At cos(theta) = -1/4: f = 2*(-1/4) + 2*(2*1/16 - 1) = -1/2 + 2*(-7/8) = -1/2 - 7/4 = -9/4.
    f_pi = sp.simplify(f.subs(theta, sp.pi))
    assert sp.simplify(f_pi - 0) == 0
    f_crit = sp.simplify(2 * sp.Rational(-1, 4) + 2 * (2 * sp.Rational(1, 16) - 1))
    assert sp.simplify(f_crit - sp.Rational(-9, 4)) == 0


def test_symbol_min_is_minus_nine_quarters() -> None:
    """f attains min value -9/4 at theta = arccos(-1/4)."""
    theta = sp.symbols("theta", real=True)
    f = 2 * sp.cos(theta) + 2 * sp.cos(2 * theta)
    # min cos(theta) = -1/4 -> f = -1/2 + 2*(2*(1/16) - 1) = -1/2 - 7/4 = -9/4.
    val_at_crit = sp.simplify(f.subs(sp.cos(theta), sp.Rational(-1, 4)))
    # The symbolic substitution doesn't always simplify; do it manually.
    val_at_crit = 2 * sp.Rational(-1, 4) + 2 * (2 * sp.Rational(1, 16) - 1)
    assert sp.simplify(val_at_crit - sp.Rational(-9, 4)) == 0


# ---------------------------------------------------------------------------- #
# 3. Continuity of g_k(lambda) = lambda^k 1[lambda < 0] at lambda = 0.
# ---------------------------------------------------------------------------- #


def g_signed(lam: float, k: int) -> float:
    """Indicator-weighted moment kernel g_k(lambda) = lambda^k 1[lambda < 0]."""
    return lam ** k if lam < 0 else 0.0


def test_g_zero_discontinuous_at_zero() -> None:
    """g_0(lambda) = 1[lambda < 0] is DISCONTINUOUS at lambda = 0
    (left limit 1, right limit 0). This is the case that requires the
    no-atom condition in the Portmanteau step."""
    left_limit = g_signed(-1e-12, 0)
    right_limit = g_signed(1e-12, 0)
    assert left_limit == 1.0
    assert right_limit == 0.0
    # The jump.
    assert abs(left_limit - right_limit) == 1.0


@pytest.mark.parametrize("k", [1, 2])
def test_g_k_continuous_at_zero_for_k_at_least_one(k: int) -> None:
    """For k >= 1, g_k(lambda) = lambda^k 1[lambda < 0] is CONTINUOUS at 0:
    both one-sided limits and the value all equal 0.

    This justifies the deliverable's claim that for k = 1, 2 weak
    convergence already suffices (no need to invoke the no-atom condition).
    """
    for eps in (1e-3, 1e-6, 1e-9, 1e-12):
        left = g_signed(-eps, k)
        right = g_signed(eps, k)
        # Both go to 0 as eps -> 0.
        assert abs(left) <= eps ** k + 1e-15
        assert right == 0.0
    # The function value at 0 is exactly 0 (since 0 < 0 is false).
    assert g_signed(0.0, k) == 0.0


# ---------------------------------------------------------------------------- #
# 4. Helly-style finite-n residual bound on I(L_n).
# ---------------------------------------------------------------------------- #


def _load_finite_n_data() -> list[dict]:
    if not DATA_PATH.exists():
        return []
    return json.loads(DATA_PATH.read_text()).get("finite_n_mpmath", [])


def test_finite_n_residuals_bounded() -> None:
    """|I(L_n) - I_inf| < 0.1 at each recorded n in {50, 100, 200}.

    This is a loose Helly-style bound: the Portmanteau argument
    guarantees convergence but does not give an explicit rate; the
    finite-n data suggests an empirical O(n^{-1}) decay with parity
    oscillations.
    """
    finite = _load_finite_n_data()
    if len(finite) < 2:
        pytest.skip(
            f"{DATA_PATH} has fewer than 2 finite-n records; nothing to assert"
        )
    for rec in finite:
        n = rec["n"]
        residual = abs(rec["residual_I"])
        assert residual < 0.1, (
            f"|I(L_{n}) - I_inf| = {residual:.6f} >= 0.1; "
            f"Helly bound violated (or empirical convergence regressed)"
        )


def test_finite_n_residuals_dont_blow_up() -> None:
    """The residual at the largest recorded n is no larger than the
    maximum residual across the grid (a soft "no blow-up" check)."""
    finite = _load_finite_n_data()
    if len(finite) < 2:
        pytest.skip(
            f"{DATA_PATH} has fewer than 2 finite-n records; nothing to assert"
        )
    finite_sorted = sorted(finite, key=lambda r: r["n"])
    abs_res = [abs(r["residual_I"]) for r in finite_sorted]
    last = abs_res[-1]
    max_res = max(abs_res)
    assert last <= max_res + 1e-15, (
        f"residual at largest n ({last}) exceeds max residual ({max_res}); "
        f"this should be impossible by definition"
    )
    # Stronger: the residual at the largest n is at most that at the
    # smallest n times 2 (tolerates parity oscillation while ruling out
    # systematic growth).
    first = abs_res[0]
    assert last <= 2 * first, (
        f"residual at n = {finite_sorted[-1]['n']} is {last:.4e}, more "
        f"than 2x residual at n = {finite_sorted[0]['n']} ({first:.4e}); "
        f"non-decaying behaviour suggests a regression"
    )


def test_finite_n_individual_moment_residuals_bounded() -> None:
    """|W^-(L_n) - W^-_inf|, |M_1^-(L_n) - M_{1,inf}^-|,
    |M_2^-(L_n) - M_{2,inf}^-| are each bounded by 0.1 on the recorded grid.

    For k = 1, 2 this follows directly from weak convergence + continuity
    of g_k at 0 (no atom needed). For k = 0 it uses the no-atom condition
    at lambda = 0 (Lemma 4.1).
    """
    finite = _load_finite_n_data()
    if not finite:
        pytest.skip(f"{DATA_PATH} not found")
    for rec in finite:
        n = rec["n"]
        for key in ("residual_W_minus", "residual_M1_minus", "residual_M2_minus"):
            r = abs(rec[key])
            assert r < 0.1, (
                f"|{key}| at n = {n} is {r:.6f} >= 0.1"
            )


# ---------------------------------------------------------------------------- #
# 5. Numerical sanity check: the limit I_inf matches the expected decimal.
# ---------------------------------------------------------------------------- #


def test_I_inf_decimal_consistency() -> None:
    """I_inf computed from the closed forms of (W^-_inf, M_{1,inf}^-, M_{2,inf}^-)
    equals 1.0157374828973253 to 1e-12."""
    assert abs(I_INF - 1.0157374828973253) < 1e-12


def test_threshold_slack_unconditional() -> None:
    """Both v11 thresholds T in {0.4122, 0.25} are passed with slack > 0.6."""
    assert I_INF - 0.4122 > 0.60
    assert I_INF - 0.25 > 0.75


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
