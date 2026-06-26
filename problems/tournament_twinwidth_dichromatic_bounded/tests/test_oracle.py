"""Regression suite pinning the oracle to the paper's known values
(arXiv:2310.04265, Conjecture 3.12).  These are the soundness guards: if a future
edit to the solvers breaks any of these, the ground truth is no longer trustworthy.
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

import core                       # noqa: E402
import constructions as C        # noqa: E402
import oracle                    # noqa: E402


# ---- structure -------------------------------------------------------------

def test_structure():
    for k in range(1, 5):
        n, a = C.S(k)
        assert core.is_tournament(n, a), f"S_{k} not a tournament"
    for m in range(1, 4):
        n, a = C.S_tilde(m)
        assert core.is_tournament(n, a), f"S~_{m} not a tournament"
    # sizes: |S_k| = 2^k - 1
    for k in range(1, 6):
        n, _ = C.S(k)
        assert n == 2 ** k - 1
    # |S~_m| = 3^{m-1}
    for m in range(1, 5):
        n, _ = C.S_tilde(m)
        assert n == 3 ** (m - 1)


# ---- chiVec(S_k) = k  (the paper's headline) -------------------------------

@pytest.mark.parametrize("k,expected", [(1, 1), (2, 2), (3, 3), (4, 4)])
def test_chiVec_S(k, expected):
    n, a = C.S(k)
    assert core.chi_vec(n, a) == expected


# ---- omegaVec known values: omegaVec(S_1..S_4) = 1,2,2,3 -------------------

@pytest.mark.parametrize("k,expected", [(1, 1), (2, 2), (3, 2)])
def test_omegaVec_S_small(k, expected):
    n, a = C.S(k)
    # brute force and B&B must agree on the small cases
    assert core.omega_vec_bruteforce(n, a) == expected
    assert core.omega_vec(n, a) == expected


@pytest.mark.slow
def test_omegaVec_S4_upper():
    # omegaVec(S_4) <= 3: a witness ordering with back-edge clique 3 exists (fast,
    # ~0.1s). The full equality omegaVec(S_4)=3 is the paper's last KNOWN value;
    # the >=3 (no clique-<=2 ordering) direction is an exact n=15 exhaustion that
    # is compute-heavy -- run it explicitly, not in the default suite.
    n, a = C.S(4)
    A = core._adj(n, a)
    assert core._exists_order_within(n, A, 3)        # omegaVec(S_4) <= 3
    assert not core._exists_order_within(n, A, 1)    # omegaVec(S_4) >= 2 (cheap)


@pytest.mark.slow
def test_omegaVec_S4_exact():
    # FULL exact equality omegaVec(S_4) == 3 (paper's boundary KNOWN value).
    # Marked slow: the >=3 direction exhausts all clique-<=2 orderings on 15 vtx.
    n, a = C.S(4)
    assert core.omega_vec(n, a) == 3


# ---- S~_m: omegaVec(S~_m) >= m and twin-width 1 ----------------------------

@pytest.mark.parametrize("m,expected", [(1, 1), (2, 2), (3, 3)])
def test_omegaVec_Stilde(m, expected):
    n, a = C.S_tilde(m)
    assert core.omega_vec_bruteforce(n, a) == expected   # >= m, in fact == m here


# ---- twin-width: TT=0, C3=1, S_k (k>=2)=1, S~_m=1 --------------------------

def test_tww():
    n, a = C.transitive_tournament(4)
    assert core.tww(n, a) == 0                       # transitive => all twins
    n, a = C.directed_triangle()
    assert core.tww(n, a) == 1
    for k in (2, 3):
        n, a = C.S(k)
        assert core.tww(n, a) == 1                   # paper: tww(S_k)=1, k>=2
    for m in (2, 3):
        n, a = C.S_tilde(m)
        assert core.tww(n, a) == 1                   # paper: tww(S~_m)=1


# ---- pipeline landmark: smallest 3-dichromatic tournament has 7 vertices ---

def test_smallest_3_dichromatic():
    # no tournament on <=6 vertices has chiVec 3; n=7 (Paley P7) does
    r5 = oracle.scan_small_tournaments(5)
    assert r5["max_chi_among_kept"] == 2
    r7 = oracle.scan_small_tournaments(7, want_chi_ge=3)
    assert r7["max_chi_among_kept"] == 3
    assert len(r7["found_chi_ge"]) >= 1


# ---- oracle wiring ---------------------------------------------------------

def test_check_construction_keys():
    n, a = C.S(3)
    res = oracle.check_construction(n, a, name="S_3")
    assert res["is_tournament"]
    for k in ("chi_vec", "omega_vec", "tww", "chi_over_omega"):
        assert k in res
    assert res["chi_vec"] == 3 and res["omega_vec"] == 2 and res["tww"] == 1
