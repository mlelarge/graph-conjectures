"""Closed-form and high-precision asymptotic moments for the 2-path ear test.

For the candidate ansatz of v11
    I(v) := W^-(v) + (M_1^-(v))^2 / M_2^-(v),
we need to evaluate I on the 2-path family L_n at the boundary ear v* = 1
(equivalently v* = n by reflection), in the limit n -> infinity.

Setup. L_n = P_n^2, A(L_n) is symmetric pentadiagonal Toeplitz with
symbol f(theta) = 2 cos(theta) + 2 cos(2 theta). The max-degsum
simplicial ear v* has H := L_n - v* ~= L_{n-1}, and the test vector is
w = e_1 + e_2 in H. We define

    W^-(L_n) = w^T P^-(A(H)) w,
    M_k^-(L_n) = w^T P^-(A(H)) A(H)^k w,

where P^- projects onto the negative-eigenvalue subspace of A(H).
The asymptotic limits W^-_inf, M_{1, inf}^-, M_{2, inf}^- and the
candidate value I_inf = W^-_inf + (M_{1, inf}^-)^2 / M_{2, inf}^- are
the quantities of interest.

Closed-form result (derived in `docs/lprime_a_two_path.md`). For the
semi-infinite half-line operator T (= A(L_inf) with Dirichlet boundary
at index 0), the spectral measure dmu at w on the negative spectrum
[-9/4, 0] has density

    rho^-(lambda)
        = (1/pi) [ Phi(theta_1) - Phi(theta_2) - sin(theta_2 - theta_1) ]

where Phi(theta) := sin(theta) + sin(2 theta), and theta_1 < theta_2
in (pi/3, pi) are the two preimages of lambda under f, sitting on the
two monotone branches of f on (pi/3, theta_min) and (theta_min, pi)
respectively (theta_min = arccos(-1/4)). Equivalently, in the
x = cos(theta_1) parametrization (with y = cos(theta_2) = -1/2 - x),

    M_k^-_inf
        = (1/pi) int_{-1/4}^{1/2}
              (4x^2 + 2x - 2)^k (4x + 1)
              [ (2x + 1) sqrt(1 - x^2) + 2x sqrt(3/4 - x - x^2) ] dx.

Evaluating with sympy:

    W^-_inf       = 1 - 3 sqrt(3) / (4 pi)            ~ 0.586503328...
    M_{1, inf}^-  = 2/3 - 9 sqrt(3) / (4 pi)          ~ -0.573823348...
    M_{2, inf}^-  = 3 - 81 sqrt(3) / (20 pi)          ~ 0.767117973...

Whence

    I_inf = W^-_inf + (M_{1, inf}^-)^2 / M_{2, inf}^-  ~ 1.0157374829...

This is well above both the v11 working thresholds T = 0.4122 and
T = 0.25. In fact W^-_inf alone (= 0.5865...) already exceeds both
thresholds; the (M_1^-)^2 / M_2^- term contributes another ~0.429 of
slack.

This script:
  1. Computes the closed-form values exactly using sympy and prints
     them as exact symbolic expressions plus 30-digit decimals.
  2. Reproduces W^-(L_n), M_1^-(L_n), M_2^-(L_n) at finite n using
     mpmath at dps = 50, for n in {50, 200, 500, 1000}.
  3. Writes data/two_path_limit_moments.json with the closed-form
     limits, the finite-n values, the slacks vs T in {0.4122, 0.25},
     and the residuals (finite_n - limit).

The expected output: residuals shrink (with O(1) prefactor) as n grows;
finite-n I(L_n) stays above the asymptotic limit by a small margin and
above the thresholds T with huge margin.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import mpmath
import sympy as sp

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "two_path_limit_moments.json"


# ----------------------------- closed-form layer ---------------------------- #

def closed_form_limits() -> dict:
    """Return the closed-form W^-_inf, M_1^-_inf, M_2^-_inf, I_inf as sympy
    expressions, exact decimals at 30 digits, and floats."""
    pi = sp.pi
    sqrt3 = sp.sqrt(3)

    W_minus_inf = 1 - 3 * sqrt3 / (4 * pi)
    M1_minus_inf = sp.Rational(2, 3) - 9 * sqrt3 / (4 * pi)
    M2_minus_inf = 3 - 81 * sqrt3 / (20 * pi)

    I_inf = W_minus_inf + M1_minus_inf ** 2 / M2_minus_inf
    I_inf_simp = sp.simplify(I_inf)

    return {
        "W_minus_inf": {
            "sympy": W_minus_inf,
            "latex": sp.latex(W_minus_inf),
            "exact_decimal_30": str(sp.N(W_minus_inf, 30)),
            "float": float(W_minus_inf),
        },
        "M1_minus_inf": {
            "sympy": M1_minus_inf,
            "latex": sp.latex(M1_minus_inf),
            "exact_decimal_30": str(sp.N(M1_minus_inf, 30)),
            "float": float(M1_minus_inf),
        },
        "M2_minus_inf": {
            "sympy": M2_minus_inf,
            "latex": sp.latex(M2_minus_inf),
            "exact_decimal_30": str(sp.N(M2_minus_inf, 30)),
            "float": float(M2_minus_inf),
        },
        "I_inf": {
            "sympy": I_inf_simp,
            "latex": sp.latex(I_inf_simp),
            "exact_decimal_30": str(sp.N(I_inf_simp, 30)),
            "float": float(I_inf_simp),
        },
    }


def verify_closed_form_via_integral(verbose: bool = False) -> dict:
    """Re-derive M_k^-_inf for k = 0, 1, 2 by symbolic integration of the
    explicit integrand. Used as an internal consistency check inside the
    test suite.
    """
    x = sp.symbols("x", real=True)
    sx = sp.sqrt(1 - x ** 2)
    sy = sp.sqrt(sp.Rational(3, 4) - x - x ** 2)
    # rho dlambda = (1/pi) * (4x+1) * [(2x+1) sx + 2x sy] dx
    integrand_density = (4 * x + 1) * ((2 * x + 1) * sx + 2 * x * sy)
    lam_pol = 4 * x ** 2 + 2 * x - 2

    a, b = -sp.Rational(1, 4), sp.Rational(1, 2)
    M0 = sp.simplify(sp.integrate(integrand_density, (x, a, b)) / sp.pi)
    M1 = sp.simplify(sp.integrate(lam_pol * integrand_density, (x, a, b)) / sp.pi)
    M2 = sp.simplify(sp.integrate(lam_pol ** 2 * integrand_density, (x, a, b)) / sp.pi)
    if verbose:
        print("Integral form M_0^- =", M0)
        print("Integral form M_1^- =", M1)
        print("Integral form M_2^- =", M2)
    return {"M0_minus_inf": M0, "M1_minus_inf": M1, "M2_minus_inf": M2}


# ---------------------------- mpmath finite-n layer ------------------------- #

def build_A_Ln(N: int, dps: int = 50) -> mpmath.matrix:
    """Build A(L_N) as an mpmath integer matrix at given precision (the entries
    are 0/1 integers; dps controls precision for downstream eigendecomp)."""
    M = mpmath.matrix(N, N)
    for i in range(N):
        for j in range(N):
            if abs(i - j) in (1, 2):
                M[i, j] = 1
    return M


def finite_n_moments(n_full: int, dps: int = 50) -> dict:
    """Compute W^-(L_n), M_1^-(L_n), M_2^-(L_n) at the boundary ear v* = 1 of
    L_n. With H := L_n - v* = L_{n-1} relabeled and w = e_1 + e_2 in H.

    Returns a dict containing the three moments, the candidate I value, and
    the negative-eigenvalue count."""
    mpmath.mp.dps = dps
    N = n_full - 1  # size of H
    A = build_A_Ln(N)
    E, U = mpmath.eigsy(A)  # symmetric eigendecomposition at high precision
    # w = e_1 + e_2 in 1-indexed = e_0 + e_1 in 0-indexed
    # c_j = (U^T w)_j = U[0, j] + U[1, j]
    c = [U[0, j] + U[1, j] for j in range(N)]
    eigvals = [E[j] for j in range(N)]
    W_minus = mpmath.mpf(0)
    M1_minus = mpmath.mpf(0)
    M2_minus = mpmath.mpf(0)
    neg_count = 0
    for j in range(N):
        if eigvals[j] < 0:
            cj2 = c[j] ** 2
            W_minus += cj2
            M1_minus += cj2 * eigvals[j]
            M2_minus += cj2 * eigvals[j] ** 2
            neg_count += 1
    I_val = W_minus + M1_minus ** 2 / M2_minus
    return {
        "n_full": n_full,
        "n_H": N,
        "W_minus": W_minus,
        "M1_minus": M1_minus,
        "M2_minus": M2_minus,
        "I": I_val,
        "n_negative_eigvals": neg_count,
    }


# ---------------------------- driver / IO layer ----------------------------- #

THRESHOLDS = [
    ("0.4122", mpmath.mpf("0.4122")),
    ("0.25", mpmath.mpf("0.25")),
]


def to_str(x) -> str:
    """Convert an mpmath/sympy/float number to a decimal string at 30 digits."""
    if isinstance(x, mpmath.mpf):
        return mpmath.nstr(x, 30)
    if isinstance(x, sp.Expr):
        return str(sp.N(x, 30))
    return repr(x)


def main(args):
    print("=== two_path_limit_moments.py ===")
    print()

    # Closed-form symbolic results
    print("1) Closed-form asymptotic moments (n -> infinity, ear v* = 1):")
    cf = closed_form_limits()
    for key in ("W_minus_inf", "M1_minus_inf", "M2_minus_inf", "I_inf"):
        sym = cf[key]["sympy"]
        print(f"   {key:14s} = {sym}")
        print(f"              ~  {cf[key]['exact_decimal_30']}")
    print()
    for label, T in THRESHOLDS:
        I_inf_float = cf["I_inf"]["float"]
        slack = I_inf_float - float(T)
        print(f"   I_inf - {label} = {slack:+.6f}    (I_inf > {label}: {slack > 0})")
    # Also the standalone W^- slacks (useful aside)
    for label, T in THRESHOLDS:
        W_inf_float = cf["W_minus_inf"]["float"]
        slack = W_inf_float - float(T)
        print(f"   W^-_inf - {label} = {slack:+.6f}    (W^-_inf > {label}: {slack > 0})")
    print()

    # Self-check: rederive M_k^- by direct symbolic integration of the density
    print("2) Symbolic consistency: rederive M_k^-_inf via direct integration:")
    rederived = verify_closed_form_via_integral()
    for k, key in enumerate(("M0_minus_inf", "M1_minus_inf", "M2_minus_inf")):
        sym = rederived[key]
        print(f"   M_{k}^-_inf (integration) = {sym}")
    print()

    # Finite-n mpmath computation
    print("3) Finite-n mpmath check (dps = 50, n in {50, 200, 500, 1000}):")
    n_values = args.n_values
    finite_results = []
    for n in n_values:
        t0 = time.time()
        r = finite_n_moments(n, dps=args.dps)
        dt = time.time() - t0
        print(f"   n = {n:5d}   (H size {r['n_H']:5d}, "
              f"{r['n_negative_eigvals']:5d} neg eigvals, "
              f"computed in {dt:6.2f}s)")
        print(f"       W^- (L_n) = {to_str(r['W_minus'])}")
        print(f"       M_1^-(L_n) = {to_str(r['M1_minus'])}")
        print(f"       M_2^-(L_n) = {to_str(r['M2_minus'])}")
        print(f"       I (L_n)    = {to_str(r['I'])}")
        # Residuals vs limit
        W_inf = cf["W_minus_inf"]["float"]
        M1_inf = cf["M1_minus_inf"]["float"]
        M2_inf = cf["M2_minus_inf"]["float"]
        I_inf = cf["I_inf"]["float"]
        res_W = float(r['W_minus']) - W_inf
        res_M1 = float(r['M1_minus']) - M1_inf
        res_M2 = float(r['M2_minus']) - M2_inf
        res_I = float(r['I']) - I_inf
        print(f"       residuals: W^- {res_W:+.3e}, M_1^- {res_M1:+.3e}, "
              f"M_2^- {res_M2:+.3e}, I {res_I:+.3e}")
        finite_results.append({
            "n": n,
            "n_H": r["n_H"],
            "n_negative_eigvals": r["n_negative_eigvals"],
            "W_minus": to_str(r["W_minus"]),
            "M1_minus": to_str(r["M1_minus"]),
            "M2_minus": to_str(r["M2_minus"]),
            "I": to_str(r["I"]),
            "I_minus_T_0.4122": float(r["I"]) - 0.4122,
            "I_minus_T_0.25": float(r["I"]) - 0.25,
            "residual_W_minus": res_W,
            "residual_M1_minus": res_M1,
            "residual_M2_minus": res_M2,
            "residual_I": res_I,
        })
    print()

    # Write data
    output = {
        "schema": "two_path_limit_moments.v1",
        "graph_family": "L_n (P_n^2, 2-path 2-tree)",
        "ear": "v* = 1 (boundary simplicial ear of degree 2)",
        "operator": "A(L_{n-1}) on H = L_n - 1, with w = e_1 + e_2 in H",
        "closed_form_limits": {
            "W_minus_inf": {
                "latex": cf["W_minus_inf"]["latex"],
                "sympy": str(cf["W_minus_inf"]["sympy"]),
                "decimal_30": cf["W_minus_inf"]["exact_decimal_30"],
                "float": cf["W_minus_inf"]["float"],
            },
            "M1_minus_inf": {
                "latex": cf["M1_minus_inf"]["latex"],
                "sympy": str(cf["M1_minus_inf"]["sympy"]),
                "decimal_30": cf["M1_minus_inf"]["exact_decimal_30"],
                "float": cf["M1_minus_inf"]["float"],
            },
            "M2_minus_inf": {
                "latex": cf["M2_minus_inf"]["latex"],
                "sympy": str(cf["M2_minus_inf"]["sympy"]),
                "decimal_30": cf["M2_minus_inf"]["exact_decimal_30"],
                "float": cf["M2_minus_inf"]["float"],
            },
            "I_inf": {
                "latex": cf["I_inf"]["latex"],
                "sympy": str(cf["I_inf"]["sympy"]),
                "decimal_30": cf["I_inf"]["exact_decimal_30"],
                "float": cf["I_inf"]["float"],
            },
        },
        "asymptotic_slack_vs_thresholds": {
            "I_inf_minus_0.4122": cf["I_inf"]["float"] - 0.4122,
            "I_inf_minus_0.25": cf["I_inf"]["float"] - 0.25,
            "W_minus_inf_minus_0.4122": cf["W_minus_inf"]["float"] - 0.4122,
            "W_minus_inf_minus_0.25": cf["W_minus_inf"]["float"] - 0.25,
        },
        "finite_n_mpmath": finite_results,
        "dps": args.dps,
    }
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    DATA_PATH.write_text(json.dumps(output, indent=2))
    print(f"Wrote {DATA_PATH}")


def parse_args(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split("\n\n", 1)[0])
    p.add_argument("--dps", type=int, default=50,
                   help="mpmath decimal precision (default: 50)")
    p.add_argument("--n-values", type=int, nargs="+",
                   default=[50, 200, 500, 1000],
                   help="finite-n grid for mpmath cross-check")
    return p.parse_args(argv)


if __name__ == "__main__":
    main(parse_args())
