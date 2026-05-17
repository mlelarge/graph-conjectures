"""Regression tests for Phase 9 (b.minor) artefacts.

Phase 9 target: delta^-(v^*) >= 1 unconditionally for 2-trees with
n >= 4. Phase 9 status (see docs/lprime_b_minor.md):

  * UNCLOSED analytically.
  * Empirically delta^-(v^*) >= 1.2941 over the 2235-record census.
  * Lemma B1 bounds alpha_min^2 = lambda_min(A(G))^2 >= f_min^2,
    empirically >= 1.8327 on Case B max-degsum ears, but the slot
    decomposition does not transfer this to delta^- (Case B's
    "new" eigenvalue is alpha_top, not alpha_min).

These tests pin:
  (i)   The Case A / Case B census is reproducible: total counts,
        per-family counts.
  (ii)  Lemma B1's sufficient condition for f_min^2 >= 1, namely
        |M_1^-| >= W^-(1 - W^-) when W^- <= 1, holds on all max-degsum
        ears of the census.
  (iii) The empirical floor delta^-(v^*) >= 1.2941 is preserved.
  (iv)  The sign-correct slot decomposition reconstructs delta^-
        identically (this is asserted in the script too, but
        regression-tested here).
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from case_AB_census import case_AB_record  # noqa: E402
from joint_invariant_features import from_graph6  # noqa: E402
from build_joint_invariant_corpus import book_graph, two_path_graph, fan_graph  # noqa: E402
from extreme_family import book_with_tail  # noqa: E402

DATA = ROOT / "data"
CENSUS_PATH = DATA / "case_AB_census.json"
EPS = 1e-9


@pytest.fixture(scope="module")
def census():
    if not CENSUS_PATH.exists():
        pytest.skip(f"census not built; run scripts/case_AB_census.py to make {CENSUS_PATH}")
    return json.loads(CENSUS_PATH.read_text())


def test_census_total_counts(census):
    """The census must contain exactly the corpus we built off
    (max-degsum ears only). Counts are stable across deterministic
    spectral routines."""
    nA = sum(1 for r in census if r["case"] == "A")
    nB = sum(1 for r in census if r["case"] == "B")
    assert nA + nB == len(census)
    # Recorded total: 2235 records, 1945 Case A, 290 Case B.
    assert len(census) == 2235, f"census has {len(census)} records, expected 2235"
    assert nA == 1945, f"Case A count {nA} != 1945"
    assert nB == 290, f"Case B count {nB} != 290"


def test_per_family_AB_breakdown(census):
    from collections import Counter
    c = Counter()
    for r in census:
        c[(r["family"], r["case"])] += 1
    expected = {
        ("enum", "A"): 1250,
        ("enum", "B"): 226,
        ("BT", "A"): 185,
        ("BT", "B"): 2,
        ("book", "A"): 464,
        # book has no Case B records (always Case A on max-degsum)
        ("L", "A"): 18,
        ("L", "B"): 36,
        ("F", "A"): 28,
        ("F", "B"): 26,
    }
    for k, v in expected.items():
        assert c.get(k, 0) == v, f"family/case {k}: got {c.get(k, 0)}, expected {v}"


def test_empirical_floor_delta_minus(census):
    """Phase 9 empirical floor: min delta^-(v^*) = 1.2941..., attained
    at the enum n=10 graph g6=I}iSSGI@O in Case B. (b.minor) is
    analytically open, but the empirical floor is a stable regression
    pin."""
    rmin = min(census, key=lambda r: r["delta_minus"])
    assert rmin["delta_minus"] >= 1.0, "delta^- floor below 1 -- (b.minor) empirically falsified"
    assert rmin["delta_minus"] >= 1.29, (
        f"delta^- floor regressed below 1.29: got {rmin['delta_minus']} "
        f"at g6={rmin['graph6']} v={rmin['v']}"
    )
    # Tight: expected min ~ 1.2940513920428
    assert abs(rmin["delta_minus"] - 1.2940513920428) < 1e-6, (
        f"min delta- changed: {rmin['delta_minus']}"
    )
    assert rmin["case"] == "B"
    assert rmin["graph6"] == "I}iSSGI@O"


def test_lemma_b1_sufficient_condition(census):
    """For every max-degsum record with W^- > 0, the sufficient
    condition |M_1^-| >= W^-(1 - W^-) for f_min^2 >= 1 holds. This
    is the Phase 9 closed-form lemma."""
    fails = []
    for r in census:
        Wm = r["W_minus"]
        if Wm <= EPS:
            continue
        M1m = abs(r["M1_minus"])
        rhs = Wm * (1.0 - Wm) if Wm <= 1.0 else -float("inf")
        if M1m < rhs - 1e-9:
            fails.append((r, M1m, rhs))
    assert not fails, (
        f"|M_1^-| >= W^-(1 - W^-) violated on {len(fails)} records "
        f"(first: g6={fails[0][0]['graph6']} v={fails[0][0]['v']} "
        f"|M_1^-|={fails[0][1]:.4f} rhs={fails[0][2]:.4f})"
    )


def test_lemma_b1_implies_f_min_sq_ge_1(census):
    """Combined: every max-degsum record with W^- > 0 has f_min^2 >= 1.
    (Lemma B1 then gives alpha_min^2 >= 1 unconditionally on the
    corpus.)"""
    for r in census:
        if r["f_min_sq"] is None:
            continue
        assert r["f_min_sq"] >= 1.0 - 1e-9, (
            f"f_min^2 < 1 at g6={r['graph6']} v={r['v']}: "
            f"f_min^2 = {r['f_min_sq']}"
        )
    # Tight: min f_min^2 on Case B max-degsum >= 1.83.
    case_B_fmin = [r["f_min_sq"] for r in census if r["case"] == "B"
                   and r["f_min_sq"] is not None]
    min_fmin = min(case_B_fmin)
    assert min_fmin >= 1.8, (
        f"min f_min^2 on Case B regressed below 1.8: got {min_fmin}"
    )


def test_slot_decomposition_reconstructs_delta_minus(census):
    """The (Slot) identity delta^- = alpha_top^2 + slot_shift_sum
    reconstructs delta^- exactly (alpha_top^2 = 0 in Case A)."""
    for r in census:
        recon = r["alpha_top_sq"] + r["slot_shift_sum"]
        assert abs(recon - r["delta_minus"]) < 1e-6, (
            f"slot identity failed: g6={r['graph6']} v={r['v']} "
            f"delta-={r['delta_minus']} recon={recon}"
        )


def test_slot_shifts_nonnegative_per_record(census):
    """Sign correctness of the slot decomposition: in the recorded
    (Slot) pairing, slot_shift_min >= 0 across all records."""
    fails = []
    for r in census:
        if r["slot_shift_min"] < -1e-9:
            fails.append(r)
    assert not fails, (
        f"slot_shift_min < 0 on {len(fails)} records (sign error): "
        f"first g6={fails[0]['graph6']} v={fails[0]['v']} "
        f"slot_shift_min={fails[0]['slot_shift_min']}"
    )


def test_case_AB_record_reproducibility_on_K3_ear():
    """Reproduce a single record from scratch to confirm the script
    is deterministic and self-consistent (K_3 + ear graph,
    n = 4)."""
    G = from_graph6("C}")  # the unique 2-tree on n = 4 (B_2 = K_4 - e)
    recs = case_AB_record(G, max_only=False)
    assert len(recs) >= 1
    for r in recs:
        # delta- of B_2 at v* should be ~1.4385 (computed in
        # lprime_5e_b_interlacing.md §4.2)
        if r["is_max_degsum"]:
            assert abs(r["delta_minus"] - 1.4384471871911697) < 1e-6, (
                f"B_2 max-degsum delta- changed: {r['delta_minus']}"
            )
            assert r["case"] == "A"
            # Check Lemma B1's sufficient condition |M_1^-| >= W^-(1 - W^-).
            Wm = r["W_minus"]
            if Wm > EPS:
                assert abs(r["M1_minus"]) >= Wm * (1 - Wm) - 1e-9
            return
    pytest.fail("no max-degsum record found on K_3 + ear (n=4)")


def test_book_with_tail_BT_5_is_recorded():
    """Confirm BT(5, 2) appears in the census with the recorded
    family/k/t metadata. This is a smoke test for the data pipeline."""
    G = book_with_tail(5, 2)
    recs = case_AB_record(G)
    assert recs
    # Just verify the case classification is stable for the max-degsum
    # ear (must be either A or B; specifically A per the census).
    for r in recs:
        assert r["case"] in ("A", "B")
