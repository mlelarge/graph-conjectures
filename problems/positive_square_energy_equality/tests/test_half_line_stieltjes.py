r"""Regression tests for the half-line Stieltjes derivation.

Companion to ``scripts/half_line_stieltjes.py`` and the research note
``docs/lprime_a_two_path_stieltjes.md``. This test file enforces that:

  1. The symbolic closed-form moments produced by the script equal the
     Phase 9 candidate closed forms exactly (as sympy expressions).
  2. The boundary linear system for (A_j, B_j) collapses to the expected
     2x2 form (small sanity check on the derivation).
  3. The simplification G_w(z) = s^2 + s - p (with s = xi_1 + xi_2,
     p = xi_1 xi_2) holds symbolically.
  4. The numerically-integrated full-spectrum moments
     M_k^{unsigned} = int_{-9/4}^4 lambda^k rho_w(lambda) d lambda
     match the matrix moments <w, A^k w> = (2, 2, 7) for k = 0, 1, 2.
  5. I_inf(L) > 0.4122 and I_inf(L) > 0.25 with explicit slack > 0.6.

If any of these fail, the Stieltjes derivation has regressed.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import pytest
import sympy as sp

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from half_line_stieltjes import (  # noqa: E402
    Gw_in_terms_of_s_p,
    full_spectrum_unsigned_moments,
    moments_negative_branch_closed_form,
    numerical_density_at,
    solve_boundary_system_for_j,
    spectral_density_in_theta,
)


TOL = 1e-12


# ---------------------------------------------------------------------------- #
# 1. Symbolic moment closed forms match Phase 9 candidate exactly.
# ---------------------------------------------------------------------------- #


def test_symbolic_moments_match_candidate_closed_form() -> None:
    """The Stieltjes-derived sympy expressions for (W^-, M_1^-, M_2^-)
    must equal the Phase 9 candidate forms symbolically (after sympy
    simplification).
    """
    moments = moments_negative_branch_closed_form()

    sqrt3, pi = sp.sqrt(3), sp.pi
    expected = {
        "W_minus_inf": 1 - 3 * sqrt3 / (4 * pi),
        "M1_minus_inf": sp.Rational(2, 3) - 9 * sqrt3 / (4 * pi),
        "M2_minus_inf": 3 - 81 * sqrt3 / (20 * pi),
    }
    for key, expected_expr in expected.items():
        actual_expr = moments[key]
        diff = sp.simplify(actual_expr - expected_expr)
        assert diff == 0, (
            f"{key}: symbolic difference is {diff}, expected 0\n"
            f"  actual   = {actual_expr}\n"
            f"  expected = {expected_expr}"
        )


def test_I_inf_closed_form() -> None:
    """I_inf = 2 (310 pi^2 - 837 sqrt(3) pi + 2187) / (27 pi (20 pi - 27 sqrt(3)))."""
    moments = moments_negative_branch_closed_form()

    sqrt3, pi = sp.sqrt(3), sp.pi
    I_expected = 2 * (310 * pi**2 - 837 * sqrt3 * pi + 2187) \
        / (27 * pi * (20 * pi - 27 * sqrt3))
    diff = sp.simplify(moments["I_inf"] - I_expected)
    assert diff == 0, (
        f"I_inf differs symbolically; sympy.simplify gave {diff}, expected 0"
    )


# ---------------------------------------------------------------------------- #
# 2. Boundary linear system has the expected closed-form solution.
# ---------------------------------------------------------------------------- #


def test_boundary_system_for_j1() -> None:
    """For j = 1, the system should yield A_1 = -xi_1 xi_2 / (xi_1 - xi_2)
    and B_1 = +xi_1 xi_2 / (xi_1 - xi_2), implying A_1 + B_1 = 0.
    """
    A1, B1 = solve_boundary_system_for_j(1)
    xi1, xi2 = sp.symbols("xi1 xi2", complex=True)
    expected_A1 = -xi1 * xi2 / (xi1 - xi2)
    expected_B1 = xi1 * xi2 / (xi1 - xi2)
    assert sp.simplify(A1 - expected_A1) == 0
    assert sp.simplify(B1 - expected_B1) == 0
    assert sp.simplify(A1 + B1) == 0


def test_boundary_system_for_j2() -> None:
    """For j = 2, the system should yield A_2 = xi_1 (xi_2 + 1)/(xi_1 - xi_2),
    B_2 = -xi_2 (xi_1 + 1)/(xi_1 - xi_2), implying A_2 + B_2 = 1.
    """
    A2, B2 = solve_boundary_system_for_j(2)
    xi1, xi2 = sp.symbols("xi1 xi2", complex=True)
    expected_A2 = xi1 * (xi2 + 1) / (xi1 - xi2)
    expected_B2 = -xi2 * (xi1 + 1) / (xi1 - xi2)
    assert sp.simplify(A2 - expected_A2) == 0
    assert sp.simplify(B2 - expected_B2) == 0
    assert sp.simplify(A2 + B2 - 1) == 0


# ---------------------------------------------------------------------------- #
# 3. G_w(z) = s^2 + s - p.
# ---------------------------------------------------------------------------- #


def test_Gw_collapses_to_s_squared_plus_s_minus_p() -> None:
    """G_w(z) := G(1, 1) + G(1, 2) + G(2, 1) + G(2, 2) simplifies, after
    rewriting in (s, p) = (xi_1 + xi_2, xi_1 xi_2), to s^2 + s - p.
    """
    Gw = Gw_in_terms_of_s_p()
    s, p = sp.symbols("s p", complex=True)
    assert sp.simplify(Gw - (s**2 + s - p)) == 0


# ---------------------------------------------------------------------------- #
# 4. Spectral density formula.
# ---------------------------------------------------------------------------- #


def test_spectral_density_formula() -> None:
    """rho_w(lambda) = sin(theta_2 - theta_1) / pi (a non-negative quantity)."""
    rho = spectral_density_in_theta()
    theta1, theta2 = sp.symbols("theta_1 theta_2", real=True)
    expected = sp.sin(theta2 - theta1) / sp.pi
    assert sp.simplify(rho - expected) == 0


def test_density_positive_on_negative_branch() -> None:
    """For three sample lambda in (-9/4, 0), rho_w(lambda) > 0 numerically."""
    for lam in (-2.0, -1.0, -0.5):
        rho = numerical_density_at(lam, eps=1e-9)
        assert rho > 0, (
            f"density at lambda = {lam} should be positive, got {rho}"
        )


# ---------------------------------------------------------------------------- #
# 5. Full-spectrum unsigned moments equal the matrix moments (2, 2, 7).
# ---------------------------------------------------------------------------- #


def test_unsigned_moments_match_matrix_moments() -> None:
    r"""Integrating lambda^k rho_w(lambda) over (-9/4, 4) must reproduce
    <w, A(L_infty)^k w> for k = 0, 1, 2.
    Direct combinatorial computation: ||w||^2 = 2, <w, A w> = 2, <w, A^2 w> = 7.

    Tolerance is loose (1e-2) because the numerical integrator is a simple
    midpoint rule sensitive to endpoint singularities. The point of this
    test is to detect order-1 errors in the density formula, not high
    precision.
    """
    fsm = full_spectrum_unsigned_moments(num_steps=4000)
    expected = {"M0_unsigned": 2.0, "M1_unsigned": 2.0, "M2_unsigned": 7.0}
    for key, exp_val in expected.items():
        got = fsm[key]
        assert abs(got - exp_val) < 1e-2, (
            f"{key} = {got}, expected {exp_val}, diff {abs(got - exp_val)}"
        )


# ---------------------------------------------------------------------------- #
# 6. Threshold slack assertions.
# ---------------------------------------------------------------------------- #


@pytest.mark.parametrize(
    "T, required_slack",
    [(0.4122, 0.60), (0.25, 0.75)],
)
def test_I_inf_above_threshold(T: float, required_slack: float) -> None:
    """I_inf > T for the v11 working thresholds, with slack at least the
    given value (loose lower bound on the analytic slack)."""
    moments = moments_negative_branch_closed_form()
    I_inf = float(moments["I_inf"])
    slack = I_inf - T
    assert I_inf > T, f"I_inf = {I_inf} not > T = {T}"
    assert slack > required_slack, (
        f"required slack {required_slack} for T = {T}, got {slack:.4f}"
    )


def test_I_inf_decimal_value() -> None:
    """I_inf(L) approximately 1.0157374... to a tight numerical tolerance."""
    moments = moments_negative_branch_closed_form()
    I_inf = float(moments["I_inf"])
    expected = 1.0157374828973253
    assert abs(I_inf - expected) < 1e-12, (
        f"I_inf = {I_inf}, expected {expected}, diff {abs(I_inf - expected)}"
    )


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
