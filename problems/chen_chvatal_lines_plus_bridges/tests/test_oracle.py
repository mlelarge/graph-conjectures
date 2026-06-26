"""Regression tests for the Chen-Chvatal lines+bridges oracle.

Anchors the EXACT line/bridge invariants against the paper's Lemma 3.1
(arXiv:1606.06011) and the F_0 small-graph picture.  Run:

    .venv/bin/python -m pytest tests/ -q
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

import core
import constructions as C
import oracle


# --------------------------------------------------------------------------- #
#  Lemma 3.1 exact values
# --------------------------------------------------------------------------- #

def test_ell_C4_is_1():
    n, e = C.C4()
    assert core.ell(n, e) == 1            # Lemma 3.1: ell(C4)=1


def test_ell_K23_is_n_minus_1():
    n, e = C.K23()
    assert core.ell(n, e) == n - 1        # Lemma 3.1: ell(H)=|H|-1, H=K2,3


def test_ell_W4_is_n_minus_1():
    n, e = C.W4()
    assert core.ell(n, e) == n - 1        # Lemma 3.1: ell(H)=|H|-1, H=W4


def test_landmarks_all_match():
    lm = oracle.landmarks()
    for name, rec in lm.items():
        assert rec["matches_lemma_3_1"], name
        assert rec["is_bad"], name        # all are F_0 members => bad


# --------------------------------------------------------------------------- #
#  betweenness / line soundness on tiny hand-checkable graphs
# --------------------------------------------------------------------------- #

def test_path_lines_universal():
    # P3 (a-b-c): the single line is the whole vertex set {a,b,c}.
    n, e = C.path(3)
    L = core.all_lines(n, e)
    assert L == {frozenset({0, 1, 2})}
    assert core.ell(n, e) == 1


def test_complete_graph_every_pair_distinct_line():
    # In K_n every pair is at distance 1; no third vertex is between them,
    # so each line is just the pair => ell(K_n) = C(n,2).
    n, e = C.complete(5)
    assert core.ell(n, e) == 10           # C(5,2)


def test_cycle5_all_pairs_distinct():
    n, e = C.cycle(5)
    assert core.ell(n, e) == 10           # C(5,2); C5 is not bad


# --------------------------------------------------------------------------- #
#  bridges, pendant edges
# --------------------------------------------------------------------------- #

def test_bridges_path():
    n, e = C.path(4)                      # every edge of a path is a bridge
    assert core.bridges_count(n, e) == 3
    assert core.has_pendant_edge(n, e)    # endpoints have degree 1


def test_cycle_has_no_bridge():
    n, e = C.cycle(6)
    assert core.bridges_count(n, e) == 0
    assert not core.has_pendant_edge(n, e)


# --------------------------------------------------------------------------- #
#  the BAD classifier + the enumeration picture
# --------------------------------------------------------------------------- #

def test_C4_is_bad():
    n, e = C.C4()
    assert core.is_bad(n, e)              # connected, pendant-free, ell+br<n


def test_K5_is_not_bad():
    n, e = C.complete(5)
    assert not core.is_bad(n, e)          # ell=10 >> 5


def test_scan_n4_finds_only_C4():
    res = oracle.scan(4)
    assert res["n_bad"] == 1
    b = res["bad"][0]
    assert b["ell"] == 1 and b["br"] == 0  # the C4


def test_scan_n7_has_no_bad():
    # No pendant-free bad graph on 7 vertices -- F_0 skips order 7.
    res = oracle.scan(7)
    assert res["n_bad"] == 0


def test_scan_counts_match_F0_picture():
    # n=5: 4 bad; n=6: 3 bad; n=8: 4 bad  (matches Figs 1-3 orders).
    assert oracle.scan(5)["n_bad"] == 4
    assert oracle.scan(6)["n_bad"] == 3
    assert oracle.scan(8)["n_bad"] == 4
