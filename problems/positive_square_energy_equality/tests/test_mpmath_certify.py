"""Tests for the high-precision and Demmel–Kahan certificates of
    delta^-(L_n) >= 17/16        for L_n = P_n^2 (2-path 2-tree).

Realises sub-route 5c-a (O5c.1) of plan v9. Two independent rigour
levels are exercised:

(A) **mpmath at high precision.** For a small curated subset of n the
    eigenvalues of A(L_n) are computed at 50 decimal digits via
    ``mpmath.eigsy`` and s^-(L_n) is computed in mpmath arithmetic.
    The slack delta^-(L_n) - 17/16 must clear 0.25.

(B) **Demmel–Kahan a-posteriori bound.** For larger n the floating-point
    eigenvalues from ``numpy.linalg.eigvalsh`` are accepted, but the
    forward-error bound

        |tilde s^- - s^-|  <=  2 * c * n^2 * eps * ||M||_2^2

    is computed explicitly (c=10 conservative LAPACK constant, eps =
    2^-52, ||L_n||_2 <= ||f||_infty = 4). The propagated lower bound
    on delta^- = s^-(L_n) - s^-(L_{n-1}) must clear 0.25 + threshold.

The two paths agree to ~12 decimal digits where they overlap; mpmath is
the gold standard.
"""
from __future__ import annotations

import sys
from pathlib import Path

import mpmath
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from mpmath_certify import (  # noqa: E402
    SLACK_REQUIRED,
    THRESHOLD,
    dk_certify_range,
    eigvalues_mpmath,
    fp_spectrum_with_dk_bound,
    s_minus_mpmath,
)


# ---------------------------------------------------------------------------
# (A) mpmath certificates at the worst-case n's
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def mpmath_dps_30():
    """Set mpmath precision to 30 decimal digits for the spot tests.

    30 digits is enough for headroom of ~25 digits on every computed
    quantity, given that all matrix entries are exact integers and the
    spectrum is bounded by 4. The full 50-digit run is in the offline
    script; the test suite trades precision for runtime.
    """
    old = mpmath.mp.dps
    mpmath.mp.dps = 30
    yield
    mpmath.mp.dps = old


# Curated subset: includes the empirical minimiser n=6 (slack 0.2565)
# and one larger n=100 sample. Skips n=200 to keep the test under ~15s.
@pytest.mark.parametrize("n", [4, 5, 6, 7, 8, 10, 20, 50, 100])
def test_mpmath_slack_above_quarter(mpmath_dps_30, n):
    """mpmath at 30 dps certifies delta^-(L_n) >= 17/16 + 0.25 = 1.3125."""
    eigs_n = eigvalues_mpmath(n)
    eigs_prev = eigvalues_mpmath(n - 1)
    sm_n = s_minus_mpmath(eigs_n)
    sm_prev = s_minus_mpmath(eigs_prev)
    delta = sm_n - sm_prev
    slack = delta - THRESHOLD
    assert slack >= SLACK_REQUIRED, (
        f"n={n}: delta^- = {mpmath.nstr(delta, 15)}, "
        f"slack = {mpmath.nstr(slack, 15)} < {SLACK_REQUIRED}"
    )


def test_mpmath_worst_case_n6(mpmath_dps_30):
    """The empirical minimiser n=6 should have slack ~0.2565, clearly > 0.25."""
    eigs6 = eigvalues_mpmath(6)
    eigs5 = eigvalues_mpmath(5)
    sm6 = s_minus_mpmath(eigs6)
    sm5 = s_minus_mpmath(eigs5)
    delta6 = sm6 - sm5
    slack6 = delta6 - THRESHOLD
    # Reference: 0.25650746088950980524...
    expected_min = mpmath.mpf("0.2565")
    expected_max = mpmath.mpf("0.2566")
    assert expected_min <= slack6 <= expected_max, (
        f"n=6 slack {mpmath.nstr(slack6, 20)} not in [{expected_min}, {expected_max}]"
    )


# ---------------------------------------------------------------------------
# (B) Demmel–Kahan a-posteriori bound on FP eigenvalues
# ---------------------------------------------------------------------------


def test_dk_certify_n4_to_n200():
    """The DK bound rigorously certifies n in [4, 200] with slack >= 0.25.

    This is the formal upgrade of the previous floating-point certificate:
    the a-posteriori error bound is explicit, the slack is at the worst
    case (n=6) ~ 0.2565, and the bound on |tilde delta^- - delta^-| is
    ~ 7e-12 << 0.0065.
    """
    result = dk_certify_range(4, 200)
    assert result["worst_n"] == 6
    assert result["worst_slack_rigorous_lower"] >= float(SLACK_REQUIRED)


def test_dk_certify_n4_to_n500():
    """Extend the DK certification to n=500: still rigorously clearing 0.25."""
    result = dk_certify_range(4, 500)
    assert result["worst_slack_rigorous_lower"] >= float(SLACK_REQUIRED)


@pytest.mark.slow
def test_dk_certify_n4_to_n1000():
    """Push DK certification to n=1000 (sub-route 5c-b: extend rigorous range).

    Marked 'slow' so it can be skipped in fast CI; takes ~10s on this machine.
    """
    result = dk_certify_range(4, 1000)
    assert result["worst_slack_rigorous_lower"] >= float(SLACK_REQUIRED)
    # Sanity: at n=1000 the DK error bound on delta^- should still be tiny.
    last = result["records"][-1]
    assert last["n"] == 1000
    assert last["error_bound_on_delta_minus"] < 1e-6


def test_dk_error_bound_is_tiny():
    """At n=200 the DK error bound on s^- is ~1e-9, far below slack 0.2565."""
    info = fp_spectrum_with_dk_bound(200)
    assert info["s_minus_error_bound"] < 1e-6, (
        f"unexpected large DK bound {info['s_minus_error_bound']:.3e}"
    )


def test_mpmath_and_fp_agree_at_worst_case(mpmath_dps_30):
    """mpmath at 30 dps and FP+DK agree to within the DK bound at n=6."""
    eigs6_mp = eigvalues_mpmath(6)
    eigs5_mp = eigvalues_mpmath(5)
    sm6_mp = float(s_minus_mpmath(eigs6_mp))
    sm5_mp = float(s_minus_mpmath(eigs5_mp))
    delta_mp = sm6_mp - sm5_mp

    info6 = fp_spectrum_with_dk_bound(6)
    info5 = fp_spectrum_with_dk_bound(5)
    delta_fp = info6["s_minus_fp"] - info5["s_minus_fp"]
    err = info6["s_minus_error_bound"] + info5["s_minus_error_bound"]

    assert abs(delta_mp - delta_fp) <= err + 1e-14, (
        f"FP/mpmath disagree at n=6: |delta_mp - delta_fp| = "
        f"{abs(delta_mp - delta_fp):.3e}, DK bound = {err:.3e}"
    )


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
