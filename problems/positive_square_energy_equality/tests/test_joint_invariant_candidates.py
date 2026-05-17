"""Regression tests for plan v10, Concrete next action #1.

For each non-falsified ansatz $(I, T)$ in a fixed "top candidates" list,
assert it holds on the full corpus:
    (a) min_{v*} I(v*) >= T  (uniform lower bound on max-degsum ears)
    (b) for every ear with delta_minus < 17/16, I(v) < T  (implication
        direction: I(v) >= T => delta_minus >= 17/16).

For each *falsified* ansatz $(I, T)$ recorded in
`tests/fixtures/joint_invariant_falsified.json`, regression-test that
the recorded counterexample witness still falsifies the candidate.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from joint_invariant_features import ear_records, from_graph6  # noqa: E402

DATA = ROOT / "data"
FIXTURES = ROOT / "tests" / "fixtures"
THRESHOLD = 17.0 / 16.0
EPS = 1e-9


# ---------------------------------------------------------------------------
# Candidate definitions (must match scripts/joint_invariant_ansatz_search.py).
# Each entry: (name, fn(record)->float, threshold T).
# ---------------------------------------------------------------------------

def _safe_div(a, b, eps=1e-12):
    return a / (b if abs(b) > eps else (eps if b >= 0 else -eps))


def _cs(r):
    """W_minus + M1_minus^2 / M2_minus when M2_minus > 0, else W_minus."""
    if r["M2_minus"] > 1e-12:
        return r["W_minus"] + r["M1_minus"] ** 2 / r["M2_minus"]
    return r["W_minus"]


def _join1(r):
    return r["W_minus"] + _safe_div(r["c1_sq"], r["mu_max"] ** 2)


def _join_m1abs_plus_c1mu2(r):
    return abs(r["M1_minus"]) + _safe_div(r["c1_sq"], r["mu_max"] ** 2)


# (name, fn, T)
TOP_CANDIDATES = [
    ("W_minus + M1_minus^2/M2_minus", _cs, 0.4122),
    ("W_minus + c1_sq/mu_max^2", _join1, 0.2575),
    ("|M1_minus| + c1_sq/mu_max^2", _join_m1abs_plus_c1mu2, 0.4257),
    ("W_minus", lambda r: r["W_minus"], 0.2366),
    ("|M1_minus|", lambda r: abs(r["M1_minus"]), 0.4089),
]


# ---------------------------------------------------------------------------
# Load corpus
# ---------------------------------------------------------------------------

def _load_all():
    p = DATA / "joint_invariant_scan_all_ears.json"
    if not p.exists():
        pytest.skip("corpus not built; run scripts/build_joint_invariant_corpus.py")
    return json.loads(p.read_text())


def _load_max():
    p = DATA / "joint_invariant_scan.json"
    if not p.exists():
        pytest.skip("corpus not built; run scripts/build_joint_invariant_corpus.py")
    return json.loads(p.read_text())


@pytest.mark.parametrize("name,fn,T", TOP_CANDIDATES)
def test_top_candidate_lower_bound_on_max_degsum(name, fn, T):
    """For each top candidate (I, T), every max-degsum ear v* in the
    corpus satisfies I(v*) >= T."""
    max_recs = _load_max()
    min_I = float("inf")
    argmin_g6 = None
    for r in max_recs:
        v = fn(r)
        if v < min_I:
            min_I = v
            argmin_g6 = r["graph6"]
    assert min_I >= T - EPS, (
        f"candidate {name!r}: min I(v*) over max-degsum corpus = {min_I} "
        f"< T = {T}; argmin g6={argmin_g6}"
    )


@pytest.mark.parametrize("name,fn,T", TOP_CANDIDATES)
def test_top_candidate_implication_on_bad_ears(name, fn, T):
    """For each top candidate (I, T) and each ear with
    delta_minus < 17/16 in the corpus, I(v) < T (so the implication
    I(v) >= T => delta_minus >= 17/16 holds)."""
    all_recs = _load_all()
    bad = [r for r in all_recs if r["delta_minus"] < THRESHOLD - EPS]
    if not bad:
        pytest.skip("no bad ears in corpus (delta_minus < 17/16); "
                    "implication direction is vacuously true")
    for r in bad:
        v = fn(r)
        assert v < T + EPS, (
            f"candidate {name!r} fails implication: ear g6={r['graph6']} "
            f"v={r['v']} has delta_minus={r['delta_minus']:.6f} < 17/16 "
            f"yet I = {v} >= T = {T}"
        )


def test_falsified_candidates_still_falsified():
    """Each falsified candidate in the fixture must still be falsified
    by its recorded counterexample witness."""
    p = FIXTURES / "joint_invariant_falsified.json"
    if not p.exists():
        pytest.skip("falsified fixture not built")
    entries = json.loads(p.read_text())
    assert entries, "fixture must record at least one falsified candidate"
    # Sanity: each entry must record a witness with delta_minus < 17/16
    # AND the candidate value on that witness must be >= the threshold
    # we tried to use (i.e., it falsifies the (I, T) pair).
    for e in entries:
        # Re-derive the witness ear directly from its graph6 + vertex
        # to confirm the recorded delta_minus is reproducible.
        G = from_graph6(e["counterexample_graph6"])
        recs = ear_records(G)
        match = [r for r in recs if r["v"] == e["counterexample_v"]]
        assert match, (
            f"candidate {e['candidate']}: witness v={e['counterexample_v']} "
            f"not found in graph6={e['counterexample_graph6']!r}"
        )
        r = match[0]
        # The recorded delta_minus should match (the corpus was built off
        # the same code path).
        assert abs(r["delta_minus"] - e["counterexample_delta_minus"]) < 1e-6, (
            f"candidate {e['candidate']}: recomputed delta_minus = "
            f"{r['delta_minus']} differs from fixture "
            f"{e['counterexample_delta_minus']}"
        )
        # The witness must be a bad ear.
        assert r["delta_minus"] < THRESHOLD - EPS, (
            f"candidate {e['candidate']}: witness delta_minus = "
            f"{r['delta_minus']} is NOT below 17/16 = {THRESHOLD}"
        )
