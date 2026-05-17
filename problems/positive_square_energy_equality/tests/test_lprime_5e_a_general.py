"""Regression tests for lprime_5e_a_general (plan v14 Track 2).

These pin the empirical floor of the joint invariant I(v^*) on the enum
corpus (and the documented global-minimum graph G_*), and verify the
closed-form CS-two-sided lower bound L(u, w0, m, M) <= I(v^*).

Provides regression coverage for:
- Proposition 4.1 (diameter-<= 2 closure = books, I >= 4/3 = 1.3333).
- The corpus floor I(v^*) >= 0.6384 over enum + structured family corpus.
- The headline threshold (T) I(v^*) >= 0.4122 with margin >= 0.22 on max-degsum ears.
- The CS-two-sided lower bound L(...) <= I(v^*) at every max-degsum record.
- The corpus minimum graph G_* = graph6 'I}qcHG`GO' has I = 0.6384.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import networkx as nx
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from clique_tree_invariants import (  # noqa: E402
    clique_tree,
    from_graph6,
    I_at_ear,
    lower_bound_I_from_M2,
    make_book,
    make_two_path,
    max_degsum_ears,
    shape_classify,
)


# ----- the v11 working threshold (carried) -----
T_THRESHOLD = 0.4122
# ----- the binding 2-path asymptotic floor (Phase 10+11) -----
I_INF_L = 1.0157
# ----- the corpus floor (documented in lprime_5e_a_general.md §2.2) -----
CORPUS_FLOOR_I = 0.6384
CORPUS_FLOOR_GRAPH6 = "I}qcHG`GO"


def _compute_I(record: dict) -> float:
    """Compute I = W^- + (M_1^-)^2 / M_2^- from a feature dict."""
    M2m = record["M2_minus"]
    if M2m < 1e-12:
        return record["W_minus"]
    return record["W_minus"] + record["M1_minus"] ** 2 / M2m


# -------------------------------------------------------------------------
# §4.1 Proposition 4.1: diameter-<= 2 closure (books)
# -------------------------------------------------------------------------

@pytest.mark.parametrize("k", [2, 3, 4, 5, 10, 20])
def test_books_have_small_diameter_clique_tree_and_I_at_least_4_3(k):
    """For B_k (k >= 2), T(B_k) has small diameter, and the max-degsum ear
    has I >= 4/3 = 1.3333...

    For B_k, every triangle shares the spine edge {0, 1} with every other,
    so the clique tree is non-unique; any spanning tree of K_k works. The
    canonical 'star' choice has diameter 2 for k >= 3, and the MST in our
    implementation happens to choose a star for k >= 4. For k = 2, the
    clique tree is a single edge (diameter 1); for k = 3, the MST picks a
    path of 3 nodes (diameter 2).
    """
    G = make_book(k)
    T = clique_tree(G)
    if k == 1:
        assert T.number_of_nodes() == 1
        return
    diam = nx.diameter(T)
    # Book diameter: always <= 2
    assert diam <= 2, f"B_{k} clique tree should have diameter <= 2, got {diam}"
    # I(v^*) >= 4/3
    ears = max_degsum_ears(G)
    assert ears, f"B_{k} should have max-degsum ears"
    for v, a, b in ears:
        feats = I_at_ear(G, v, a, b)
        assert feats["I"] >= 4.0 / 3.0 - 1e-9, (
            f"B_{k} ear v={v} has I = {feats['I']:.4f} < 4/3 = 1.3333"
        )


# -------------------------------------------------------------------------
# §1.3 / §3.1 CS-two-sided lower bound: L(u, w, m, M) <= I always
# -------------------------------------------------------------------------

CORPUS_PATH = ROOT / "data" / "joint_invariant_scan_all_ears.json"


@pytest.fixture(scope="module")
def max_degsum_records():
    if not CORPUS_PATH.exists():
        pytest.skip(f"Corpus file missing: {CORPUS_PATH}")
    data = json.loads(CORPUS_PATH.read_text())
    return [r for r in data if r["is_max_degsum"]]


def test_corpus_size_at_least_500(max_degsum_records):
    """Sanity: corpus should be sizeable."""
    assert len(max_degsum_records) >= 500


def test_I_above_T_at_every_max_degsum_record(max_degsum_records):
    """Headline: I(v^*) >= T = 0.4122 on every max-degsum record (with margin)."""
    min_I = float("inf")
    worst = None
    for r in max_degsum_records:
        I = _compute_I(r)
        if I < min_I:
            min_I = I
            worst = r
    assert min_I >= T_THRESHOLD, (
        f"I = {min_I:.6f} < T = {T_THRESHOLD} at {worst.get('source')} "
        f"graph6={worst.get('graph6')}"
    )
    assert min_I >= 0.6, f"Expected corpus-floor I > 0.6, got {min_I:.6f}"


def test_cs_two_sided_lower_bound_holds_at_every_record(max_degsum_records):
    """The closed-form lower bound L(u, w, m, M) <= I always (when defined).

    Tests equation (1.3) / (3.1) of lprime_5e_a_general.md.
    """
    failures = []
    for r in max_degsum_records:
        u = r["W_minus"]
        w0 = r["W_zero"]
        m = -r["M1_minus"]
        # Use the structurally observed M_2 = sigma + 2|T_ab| via M_2^- + M_2^+
        M2_total = r["M2_minus"] + r["M2_plus"]
        bound = lower_bound_I_from_M2(u, w0, m, M2_total)
        if bound is None:
            continue
        I_actual = _compute_I(r)
        if bound > I_actual + 1e-6:
            failures.append((bound, I_actual, r.get("source"), r.get("graph6")))
    assert not failures, (
        f"CS-two-sided lower bound exceeded I at {len(failures)} records: "
        f"first failure {failures[0]}"
    )


def test_cs_bound_corpus_min_is_below_T(max_degsum_records):
    """Diagnostic: the CS-two-sided lower bound, taken across the corpus,
    dips below T = 0.4122 — confirming that (1.3) alone does NOT close (T).

    This is the §3.4 / §5.2 verdict pinned as a regression invariant.
    """
    min_bound = float("inf")
    for r in max_degsum_records:
        u = r["W_minus"]
        w0 = r["W_zero"]
        m = -r["M1_minus"]
        M2_total = r["M2_minus"] + r["M2_plus"]
        b = lower_bound_I_from_M2(u, w0, m, M2_total)
        if b is not None and b < min_bound:
            min_bound = b
    # The corpus min of the bound is around 0.396 — below T.
    assert min_bound < T_THRESHOLD + 1e-3, (
        f"Expected CS-bound min < T; got {min_bound:.4f}"
    )
    assert min_bound > 0.35, (
        f"Expected CS-bound min > 0.35; got {min_bound:.4f}"
    )


# -------------------------------------------------------------------------
# §2.2 The corpus minimum graph G_* and its structure
# -------------------------------------------------------------------------

def test_corpus_floor_graph_has_documented_I_value():
    """The corpus min graph G_* = graph6 'I}qcHG`GO' has I = 0.6384 at one
    of its max-degsum ears."""
    G = from_graph6(CORPUS_FLOOR_GRAPH6)
    assert G.number_of_nodes() == 10
    ears = max_degsum_ears(G)
    assert ears, "G_* should have max-degsum ears"
    Is = [I_at_ear(G, v, a, b)["I"] for v, a, b in ears]
    min_I = min(Is)
    assert abs(min_I - CORPUS_FLOOR_I) < 1e-3, (
        f"G_* min I expected {CORPUS_FLOOR_I}, got {min_I:.4f}"
    )


def test_corpus_floor_graph_has_caterpillar_clique_tree():
    """G_* has a caterpillar clique tree with degree sequence [3, 3, 3, 1, 1, 1, 1, 1]."""
    G = from_graph6(CORPUS_FLOOR_GRAPH6)
    T = clique_tree(G)
    assert T.number_of_nodes() == 8
    assert T.number_of_edges() == 7
    degs = sorted([d for _, d in T.degree()], reverse=True)
    assert degs == [3, 3, 3, 1, 1, 1, 1, 1], f"Got T-degs = {degs}"
    # Diameter 4
    assert nx.diameter(T) == 4


# -------------------------------------------------------------------------
# §2.4 / §4.3 sub-family floors on path clique trees (= 2-paths L_n)
# -------------------------------------------------------------------------

@pytest.mark.parametrize("n", [6, 8, 10, 12, 15])
def test_two_path_I_above_threshold(n):
    """L_n has I(v^*) >= T = 0.4122 by direct computation."""
    G = make_two_path(n)
    ears = max_degsum_ears(G)
    Is = [I_at_ear(G, v, a, b)["I"] for v, a, b in ears]
    assert min(Is) >= T_THRESHOLD, (
        f"L_{n} has min I = {min(Is):.4f} < T = {T_THRESHOLD}"
    )


def test_L6_is_the_finite_2path_minimizer():
    """L_6 has I = 0.7563, the documented 2-path finite minimum."""
    G = make_two_path(6)
    ears = max_degsum_ears(G)
    Is = [I_at_ear(G, v, a, b)["I"] for v, a, b in ears]
    assert abs(min(Is) - 0.7563) < 1e-3


# -------------------------------------------------------------------------
# §2.6 Verdict regressions
# -------------------------------------------------------------------------

def test_T_minus_corpus_min_slack_is_at_least_0_22(max_degsum_records):
    """The corpus minimum I is at least T + 0.22 (pinned regression)."""
    min_I = min(_compute_I(r) for r in max_degsum_records)
    assert min_I - T_THRESHOLD >= 0.22 - 1e-6


def test_harder_target_T_star_is_empirically_violated(max_degsum_records):
    """The harder target I >= I_inf(L) ~ 1.0157 is empirically VIOLATED;
    the corpus has substantial records below this floor."""
    below = sum(1 for r in max_degsum_records if _compute_I(r) < I_INF_L)
    assert below >= 100, (
        f"Expected >= 100 records below I_inf(L) ~ {I_INF_L}; got {below}. "
        f"This pins the F16 (proposed) observation: 2-path is NOT the binding case."
    )
