"""Regression tests for the heroic-sets / dichromatic oracle (arXiv:2009.13319).

These reproduce the paper's exact finite landmarks.  Run with the symlinked
shared venv:
    .venv/bin/python -m pytest tests/ -q
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

import core      # noqa: E402
import oracle    # noqa: E402


# --------------------------------------------------------------------------- #
#  Named-digraph sanity
# --------------------------------------------------------------------------- #

def test_named_basics():
    assert core.K2sym() == (2, [(0, 1), (1, 0)])
    assert core.C3()[0] == 3
    assert core.P_plus(3) == (4, [(0, 1), (1, 2), (2, 3)])
    assert core.is_oriented(core.P_plus(3)[1])
    assert not core.is_oriented(core.K2sym()[1])  # digon
    assert core.is_triangle_free(*core.P_plus(3))


def test_dichromatic_landmarks():
    assert core.dichromatic_number(*core.K1()) == 1
    assert core.dichromatic_number(*core.K2sym()) == 2     # digon needs 2 colours
    assert core.dichromatic_number(*core.C3()) == 2        # directed triangle
    assert core.dichromatic_number(*core.directed_cycle(4)) == 2


# --------------------------------------------------------------------------- #
#  Induced subdigraph containment
# --------------------------------------------------------------------------- #

def test_induced_containment():
    C4 = core.directed_cycle(4)
    assert core.contains_induced(core.P_plus(3), core.P_plus(3))
    assert not core.contains_induced(C4, core.P_plus(3))   # cycle: no induced path
    assert not core.contains_induced(C4, core.C3())
    assert core.contains_induced(core.C3(), core.C3())
    # transitive tournament TT4 has all chords -> NO induced P+3
    TT4 = (4, [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)])
    assert not core.contains_induced(TT4, core.P_plus(3))
    assert not core.contains_induced(core.C3(), core.K2sym())


# --------------------------------------------------------------------------- #
#  THE primary landmark: Theorem 6.5  chi_d(Forb_ind(K2sym,C3,P+3)) = 2
# --------------------------------------------------------------------------- #

def test_thm_6_5_n6():
    res = oracle.measure_heroic_set(["K2sym", "C3", "P+3"], 6, claimed_bound=2)
    assert res["n_in_Forb_ind"] == 1750
    assert res["max_chi_d"] == 2
    assert res["chi_d_distribution"] == {1: 1304, 2: 446}
    assert res["bound_violated"] is False
    assert res["first_attained"]["2"] == 4          # value 2 first at n=4
    # witness is the directed C4 with the paper's arcs
    w = res["max_witness"]
    assert w["n"] == 4
    assert sorted(map(tuple, w["arcs"])) == sorted([(2, 0), (1, 2), (0, 3), (3, 1)])


# --------------------------------------------------------------------------- #
#  Secondary landmarks: Thm 2.1 identity + the tournament tower
# --------------------------------------------------------------------------- #

def test_cycle_substitution_thm_2_1():
    for base in ["K1", "K2sym", "C3"]:
        for k in [3, 4]:
            r = oracle.cycle_substitution(k, base)
            assert r["matches"], r


def test_tournament_tower():
    for k in range(1, 5):
        r = oracle.tower(k)
        assert r["chi_d"] == k, r
        # each tower digraph is a tournament
        n, arcs = core.tournament_tower(k)
        s = set(map(tuple, arcs))
        for i in range(n):
            for j in range(i + 1, n):
                assert ((i, j) in s) ^ ((j, i) in s)


def test_check_construction_groundtruth():
    r = oracle.check_construction(4, [(2, 0), (1, 2), (0, 3), (3, 1)],
                                  forbidden=["K2sym", "C3", "P+3"])
    assert r["is_oriented"] and r["is_triangle_free"]
    assert r["chi_d"] == 2
    assert r["in_Forb_ind"] is True
