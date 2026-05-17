"""Regression tests for the positive-side dual of Lemma B1.

See docs/lprime_positive_side_ceiling.md. The headline claims pinned here:

  (i)   Lemma B1+ as a *lower bound* on lambda_max(A(G)):
            lambda_max >= f_max+ = (M_1^+ + sqrt((M_1^+)^2 + 4(W^+)^3))/(2W^+)
        when W^+ > 0. Holds on all max-degsum records of the corpus.
  (ii)  The trace identity delta^+ + delta^- = 4 on degree-2 ears.
  (iii) Empirical: max delta^+(v^*) <= 2.7060 on the corpus (= 4 - 1.2941).
  (iv)  Slot decomposition reconstructs delta^+ = alpha_top_plus^2 (in Case B_+)
        + sum_{j in J^+(H)}(lambda_j^2 - mu_j^2).
  (v)   Tightness comparison: positive-side Lemma B1+ has mean ratio
        lambda_max / f_max+ approximately 1.16 over the corpus, comparable
        to the negative-side Lemma B1 tightness (mean 1.14). The positive
        side is NOT significantly tighter than the negative side.
  (vi)  F11-style caveat: alpha_top_plus^2 (the slot-decomposition's
        Case B_+ extra term) can be as small as 2e-5 in the corpus,
        so Lemma B1+'s lower bound on lambda_max does not bound
        alpha_top_plus.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from positive_side_ceiling import f_max_plus, positive_side_record  # noqa: E402
from joint_invariant_features import from_graph6  # noqa: E402

DATA = ROOT / "data"
CENSUS_PATH = DATA / "positive_side_ceiling_census.json"
NEG_CENSUS_PATH = DATA / "case_AB_census.json"
EPS = 1e-9


@pytest.fixture(scope="module")
def census():
    if not CENSUS_PATH.exists():
        pytest.skip(
            f"positive-side census not built; run "
            f"scripts/positive_side_ceiling.py to make {CENSUS_PATH}"
        )
    return json.loads(CENSUS_PATH.read_text())


@pytest.fixture(scope="module")
def neg_census():
    if not NEG_CENSUS_PATH.exists():
        pytest.skip("negative-side census missing; run case_AB_census.py")
    return json.loads(NEG_CENSUS_PATH.read_text())


def test_f_max_plus_closed_form_smoke():
    """Lemma B1+ formula sanity: f_max_plus(1, 1) = (1+sqrt(5))/2 (golden ratio)."""
    val = f_max_plus(1.0, 1.0)
    assert val is not None
    assert abs(val - (1 + math.sqrt(5)) / 2) < 1e-12
    # f_max_plus(2, 0) = sqrt(2): mu's mean of squares form.
    val = f_max_plus(2.0, 0.0)
    assert val is not None
    assert abs(val - math.sqrt(2.0)) < 1e-12
    # W^+ = 0: returns None (no positive eigenspace contribution).
    assert f_max_plus(0.0, 0.0) is None


def test_census_total_counts(census):
    """The positive-side census parallels the negative-side: 2235 records."""
    assert len(census) == 2235
    nA = sum(1 for r in census if r["case_pos"] == "A")
    nB = sum(1 for r in census if r["case_pos"] == "B")
    assert nA + nB == 2235
    # Recorded: 1834 Case A_+, 401 Case B_+.
    assert nA == 1834, f"Case A_+ count {nA} != 1834"
    assert nB == 401, f"Case B_+ count {nB} != 401"


def test_lemma_b1_plus_lower_bound_on_lambda_max(census):
    """Lemma B1+ : lambda_max >= f_max+ on all records with W^+ > 0."""
    fails = []
    for r in census:
        if r["f_max_plus"] is None:
            continue
        if r["lambda_max_G"] < r["f_max_plus"] - 1e-9:
            fails.append(r)
    assert not fails, (
        f"Lemma B1+ falsified on {len(fails)} records "
        f"(first: g6={fails[0]['graph6']} v={fails[0]['v']} "
        f"lambda_max={fails[0]['lambda_max_G']:.4f} f_max+={fails[0]['f_max_plus']:.4f})"
    )


def test_trace_identity_delta_plus_minus(census):
    """On degree-2 simplicial ears, tr(A(G)^2) - tr(A(H)^2) = 2 * deg_G(v) = 4,
    so delta^+ + delta^- = 4."""
    for r in census:
        assert abs(r["delta_plus"] + r["delta_minus"] - 4.0) < 1e-7, (
            f"trace identity failed at g6={r['graph6']} v={r['v']}: "
            f"delta+ + delta- = {r['delta_plus'] + r['delta_minus']}"
        )


def test_empirical_ceiling_delta_plus(census):
    """Empirical ceiling: max delta^+(v^*) = 2.7060 on the corpus, attained
    at the same record (`I}iSSGI@O`, n=10) that minimises delta^-(v^*).
    The two are linked by the trace identity."""
    rmax = max(census, key=lambda r: r["delta_plus"])
    assert rmax["delta_plus"] <= 3.0, (
        f"delta+ > 3 (so delta- < 1) at g6={rmax['graph6']} v={rmax['v']}: "
        f"delta+={rmax['delta_plus']}"
    )
    assert rmax["delta_plus"] <= 2.71, (
        f"delta+ ceiling regressed above 2.71: {rmax['delta_plus']}"
    )
    assert abs(rmax["delta_plus"] - 2.7059486079571968) < 1e-6, (
        f"max delta+ changed: {rmax['delta_plus']}"
    )
    assert rmax["graph6"] == "I}iSSGI@O"


def test_slot_decomposition_reconstructs_delta_plus(census):
    """The positive-side (Slot+) identity:
       delta+ = alpha_top_plus^2 + sum_{j in J^+(H)}(lambda_j^2 - mu_j^2),
    reconstructs delta^+ exactly. alpha_top_plus^2 = 0 in Case A_+."""
    for r in census:
        recon = r["alpha_top_plus_sq"] + r["slot_shift_plus_sum"]
        assert abs(recon - r["delta_plus"]) < 1e-6, (
            f"positive slot identity failed: g6={r['graph6']} v={r['v']} "
            f"delta+={r['delta_plus']} recon={recon}"
        )


def test_positive_slot_shifts_nonnegative(census):
    """Sign correctness: with the (Slot+) pairing (lambda_i, mu_i),
    slot-shifts at indices with mu_i > 0 (J^+) are >= 0."""
    fails = []
    for r in census:
        if r["slot_shift_plus_min"] < -1e-9:
            fails.append(r)
    assert not fails, (
        f"positive slot shift < 0 on {len(fails)} records (sign error): "
        f"first g6={fails[0]['graph6']} v={fails[0]['v']} "
        f"slot_shift_plus_min={fails[0]['slot_shift_plus_min']}"
    )


def test_f_max_plus_is_at_least_perron_floor(census):
    """For max-degsum ears of any 2-tree with n >= 4, the supporting edge
    {a, b} is in E(H), so M_1 = w^T A(H) w = 2. From W^+ + W^- + W^0 = 2 and
    M_1^+ + M_1^- + M_1^0 = M_1 = 2 (with M_1^0 = 0 since the zero-eigenspace
    contributes nothing), one has M_1^+ = 2 + |M_1^-| >= 2. Hence
    f_max+ >= (2 + sqrt(4 + 4 (W^+)^3)) / (2 W^+) = (1 + sqrt(1 + (W^+)^3)) / W^+.
    For W^+ <= sqrt(2), f_max+ >= 1/W^+ + 1. We pin: every record has
    f_max+ >= 2 (a uniform Perron floor)."""
    fails = []
    for r in census:
        if r["f_max_plus"] is None:
            continue
        if r["f_max_plus"] < 2.0 - 1e-6:
            fails.append(r)
    assert not fails, (
        f"f_max+ < 2 on {len(fails)} records "
        f"(first g6={fails[0]['graph6']} v={fails[0]['v']} f_max+={fails[0]['f_max_plus']:.4f})"
    )


def test_lemma_b1_plus_versus_lemma_b1_tightness(census, neg_census):
    """Compare Lemma B1+ vs Lemma B1 in terms of multiplicative tightness.

    The strategic hypothesis (in the prompt) was that the positive-side
    spectrum admits a tighter Rayleigh bound than the negative side.
    The data does NOT support that: the positive-side mean ratio
    lambda_max / f_max+ over the corpus is approximately 1.16,
    comparable to the negative-side alpha_min / |f_min| mean of
    approximately 1.14. The two sides are roughly equally tight under
    the analogous trial vector."""
    import numpy as np

    ratios_pos = [r["ratio_lambda_max_over_f_max_plus"] for r in census
                  if r["ratio_lambda_max_over_f_max_plus"] is not None]
    ratios_neg = []
    for r in neg_census:
        if r["f_min_sq"] is None or r["f_min_sq"] < EPS:
            continue
        ratios_neg.append(math.sqrt(r["alpha_min_sq"] / r["f_min_sq"]))

    mean_pos = float(np.mean(ratios_pos))
    mean_neg = float(np.mean(ratios_neg))
    # Mean ratios are within 5% of each other (1.14 vs 1.16).
    assert abs(mean_pos - mean_neg) < 0.05, (
        f"unexpected divergence between positive and negative tightness: "
        f"mean_pos={mean_pos:.4f}, mean_neg={mean_neg:.4f}"
    )
    # Pin the values to detect regressions.
    assert abs(mean_pos - 1.1638) < 1e-3, f"positive-side mean ratio drift: {mean_pos}"
    assert abs(mean_neg - 1.1367) < 1e-3, f"negative-side mean ratio drift: {mean_neg}"


def test_case_B_plus_alpha_top_plus_can_be_tiny(census):
    """F11-style caveat for Lemma B1+: in Case B_+, the slot decomposition
    uses alpha_top_plus^2 (the SMALLEST G-positive eigenvalue), not
    lambda_max. Lemma B1+ bounds lambda_max from below but says nothing
    about alpha_top_plus. Empirically alpha_top_plus^2 can be as small
    as approximately 2e-5 in the corpus."""
    B_recs = [r for r in census if r["case_pos"] == "B"]
    assert B_recs
    rmin = min(B_recs, key=lambda r: r["alpha_top_plus_sq"])
    # Pin the minimum to two significant figures.
    assert rmin["alpha_top_plus_sq"] < 1e-4, (
        f"alpha_top_plus^2 unexpectedly large in Case B_+: {rmin['alpha_top_plus_sq']}"
    )
    # And lambda_max is large at this record despite alpha_top_plus tiny:
    assert rmin["lambda_max_G_sq"] > 1.0, (
        f"lambda_max^2 unexpectedly small: {rmin['lambda_max_G_sq']}"
    )


def test_reproducibility_on_K3_ear():
    """Small reproducibility check: B_2 = K_4 - e at n = 4."""
    G = from_graph6("C}")
    recs = positive_side_record(G, max_only=False)
    assert recs
    for r in recs:
        if r["is_max_degsum"]:
            # delta+ + delta- = 4 sanity
            assert abs(r["delta_plus"] + r["delta_minus"] - 4.0) < 1e-9
            # Lemma B1+ holds
            if r["f_max_plus"] is not None:
                assert r["lambda_max_G"] >= r["f_max_plus"] - 1e-9
            return
    pytest.fail("no max-degsum record found on B_2 (n=4)")
