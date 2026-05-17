r"""Regression tests for the 2-path asymptotic moments closed form.

Companion to ``scripts/two_path_limit_moments.py`` and the research note
``docs/lprime_a_two_path.md``. The asymptotic closed-form values:

    W^-_inf       = 1 - 3 sqrt(3) / (4 pi)            ~ 0.5865033...
    M_{1,inf}^-   = 2/3 - 9 sqrt(3) / (4 pi)          ~ -0.5738233...
    M_{2,inf}^-   = 3 - 81 sqrt(3) / (20 pi)          ~ 0.7671180...
    I_inf         = W^-_inf + (M_1^-_inf)^2 / M_2^-_inf
                  = 2 (-837 sqrt(3) pi + 2187 + 310 pi^2)
                       / (27 pi (20 pi - 27 sqrt(3)))  ~ 1.0157375...

These tests assert:
1. The four closed-form sympy expressions evaluate to the stated decimals
   within 1e-12.
2. Re-deriving M_k^-_inf by direct symbolic integration of the explicit
   integrand recovers the same closed-form values.
3. The boundary-density sanity checks for Phi = sin theta + sin 2 theta:
   moments (\int Phi^2 d theta / pi, \int Phi^2 f d theta / pi,
            \int Phi^2 f^2 d theta / pi) = (1, 1/2, 3),
   confirming Phi is the correct *bulk* (Toeplitz-eigenfunction) factor.
4. I_inf > T for both v11 thresholds T in {0.4122, 0.25} with slack >= 0.60.
5. (Conditional on data/two_path_limit_moments.json existing) the
   finite-n residuals |I(L_n) - I_inf| decrease as n grows through
   {50, 200, 500}.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
import sympy as sp

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from two_path_limit_moments import (  # noqa: E402
    closed_form_limits,
    verify_closed_form_via_integral,
)

DATA_PATH = ROOT / "data" / "two_path_limit_moments.json"

# ----- expected decimal values (to ~1e-15) ---------------------------------- #

EXPECTED = {
    "W_minus_inf":  0.5865033284336559628665051262651,
    "M1_minus_inf": -0.5738233480323654447338179545375,
    "M2_minus_inf": 0.7671179735417421994791276818321,
    "I_inf":        1.0157374828973253270357010742528,
}
TOL = 1e-12


# ---------------------------------------------------------------------------- #
# 1. Symbolic closed-form values
# ---------------------------------------------------------------------------- #

def test_closed_form_values():
    """The four sympy expressions evaluate (numerically) to the expected
    decimal approximations within 1e-12.

    The asymptotic candidate-ansatz value is
        I_inf ~ 1.0157374... > 0.25 > 0.
    Both v11 thresholds T = 0.4122 and T = 0.25 are passed with
    slack > 0.60.
    """
    cf = closed_form_limits()
    for key, expected in EXPECTED.items():
        val = float(cf[key]["sympy"])
        assert abs(val - expected) < TOL, (
            f"{key}: closed form {val} differs from expected {expected} "
            f"by {abs(val - expected):.3e}"
        )


# ---------------------------------------------------------------------------- #
# 2. Direct-integration cross-check of the closed-form values
# ---------------------------------------------------------------------------- #

def test_consistency_via_direct_integration():
    """Re-derive M_k^-_inf for k = 0, 1, 2 by symbolic integration of the
    explicit integrand and check it matches the closed-form layer.

    The two computations have independent code paths (one returns the
    pre-simplified ``a - b sqrt(3)/pi`` expressions, the other returns the
    raw integrals); both must collapse to the same numerical value.
    """
    cf = closed_form_limits()
    rederived = verify_closed_form_via_integral()

    map_keys = {
        "M0_minus_inf": "W_minus_inf",     # M_0^- = W^-_inf
        "M1_minus_inf": "M1_minus_inf",
        "M2_minus_inf": "M2_minus_inf",
    }
    for raw_key, cf_key in map_keys.items():
        v_raw = float(sp.N(rederived[raw_key], 50))
        v_cf = float(cf[cf_key]["sympy"])
        assert abs(v_raw - v_cf) < TOL, (
            f"{raw_key} (integration) = {v_raw} vs closed-form "
            f"{cf_key} = {v_cf}; gap {abs(v_raw - v_cf):.3e}"
        )


# ---------------------------------------------------------------------------- #
# 3. Boundary-density sanity checks
# ---------------------------------------------------------------------------- #

def test_unsigned_moment_sanity_checks():
    """For Phi(theta) = sin(theta) + sin(2 theta) and
    f(theta) = 2 cos(theta) + 2 cos(2 theta), verify
        (1/pi) int_0^pi Phi^2     dtheta = 1,
        (1/pi) int_0^pi Phi^2 f   dtheta = 1/2,
        (1/pi) int_0^pi Phi^2 f^2 dtheta = 3.
    These confirm that Phi is the correct bulk-Toeplitz angular factor
    (modulo boundary contributions that shift the matrix moments
    <w, A^k w> to the slightly larger values (2, 2, 7) -- see
    docs/lprime_a_two_path.md).
    """
    theta = sp.symbols("theta", real=True)
    Phi = sp.sin(theta) + sp.sin(2 * theta)
    f = 2 * sp.cos(theta) + 2 * sp.cos(2 * theta)

    expected = [sp.Integer(1), sp.Rational(1, 2), sp.Integer(3)]
    for k, exp_val in enumerate(expected):
        got = sp.simplify(sp.integrate(Phi**2 * f**k, (theta, 0, sp.pi)) / sp.pi)
        assert sp.simplify(got - exp_val) == 0, (
            f"moment k={k}: got {got}, expected {exp_val}"
        )


# ---------------------------------------------------------------------------- #
# 4. Slack vs the v11 thresholds
# ---------------------------------------------------------------------------- #

@pytest.mark.parametrize("T", [0.4122, 0.25])
def test_threshold_slack(T):
    """I_inf > T with slack >= 0.60 for both v11 working thresholds."""
    cf = closed_form_limits()
    I_inf = float(cf["I_inf"]["sympy"])
    slack = I_inf - T
    assert I_inf > T, f"I_inf = {I_inf} not > T = {T}"
    assert slack >= 0.60, (
        f"slack I_inf - T = {slack:.4f} < required 0.60 for T = {T}"
    )


# ---------------------------------------------------------------------------- #
# 5. Finite-n residuals decrease (conditional on data file)
# ---------------------------------------------------------------------------- #

def test_finite_n_residuals_decrease():
    """The residual |I(L_n) - I_inf| should not increase as n grows through
    the recorded grid {50, 200, 500}.

    If the JSON data file is missing (e.g. on a clean checkout before
    running the script), the test is skipped. With the file present, we
    assert non-increasing-from-first-to-last (a mild monotonicity that
    tolerates parity oscillations within the run).
    """
    if not DATA_PATH.exists():
        pytest.skip(f"{DATA_PATH} not found; run two_path_limit_moments.py first")

    data = json.loads(DATA_PATH.read_text())
    finite = data.get("finite_n_mpmath", [])
    if len(finite) < 2:
        pytest.skip(
            f"finite_n_mpmath has only {len(finite)} entries; need >= 2"
        )

    # sort by n just in case
    finite_sorted = sorted(finite, key=lambda r: r["n"])

    # Residuals are signed in the JSON; track absolute residuals.
    abs_residuals = [abs(r["residual_I"]) for r in finite_sorted]
    ns = [r["n"] for r in finite_sorted]

    # The strict claim: the largest n must have residual <= the smallest n.
    assert abs_residuals[-1] <= abs_residuals[0] + 1e-15, (
        f"|residual| at n = {ns[-1]} is {abs_residuals[-1]:.3e}, larger "
        f"than at n = {ns[0]} ({abs_residuals[0]:.3e}); residuals "
        f"should decay as n -> infinity."
    )

    # Soft monotonicity: at least one strict decrease across consecutive ns.
    decreased_somewhere = any(
        abs_residuals[i + 1] < abs_residuals[i]
        for i in range(len(abs_residuals) - 1)
    )
    assert decreased_somewhere, (
        f"|residuals| {abs_residuals} did not strictly decrease anywhere "
        f"between consecutive ns {ns}; expected convergence to I_inf."
    )


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
