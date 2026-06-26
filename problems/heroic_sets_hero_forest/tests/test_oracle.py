"""Regression tests for the hero-forest heroic-set oracle (arXiv:2009.13319,
Conjecture 4.2; concrete landmarks Theorem 6.1 and Conjecture 6.2).

Run with the symlinked shared venv:
    .venv/bin/python -m pytest tests/ -q
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

import core      # noqa: E402
import oracle    # noqa: E402


# --------------------------------------------------------------------------- #
#  Named-digraph definitions (verified against the paper, Sec 6)
# --------------------------------------------------------------------------- #

def test_named_definitions():
    assert core.K2_digon() == (2, [(0, 1), (1, 0)])
    assert core.C3() == (3, [(0, 1), (1, 2), (2, 0)])
    # ->K2 + K1 : a single arc plus an isolated vertex (3 vertices, 1 arc)
    assert core.arrowK2_plus_K1() == (3, [(0, 1)])
    # S2+ : out-star, centre 0 -> {1,2}
    assert core.S2_plus() == (3, [(0, 1), (0, 2)])
    # S2- : in-star, {1,2} -> centre 0
    assert core.S2_minus() == (3, [(1, 0), (2, 0)])
    assert core.P_plus(2) == (3, [(0, 1), (1, 2)])
    # arrowK2_K1, S2+, S2- are all oriented and triangle-free
    for D in (core.arrowK2_plus_K1(), core.S2_plus(), core.S2_minus()):
        assert core.is_oriented(D[1])
        assert core.is_triangle_free(*D)
    assert not core.is_oriented(core.K2_digon()[1])   # digon


def test_dichromatic_sanity():
    assert core.dichromatic_number(*core.K1()) == 1
    assert core.dichromatic_number(*core.K2_digon()) == 2   # digon
    assert core.dichromatic_number(*core.C3()) == 2         # directed triangle
    assert core.dichromatic_number(*core.directed_cycle(4)) == 2
    # the three 3-vertex oriented forests are acyclic -> chi_d = 1
    for D in (core.arrowK2_plus_K1(), core.S2_plus(), core.S2_minus(),
              core.P_plus(2)):
        assert core.dichromatic_number(*D) == 1


# --------------------------------------------------------------------------- #
#  Induced-containment sanity
# --------------------------------------------------------------------------- #

def test_induced_containment():
    C4 = core.directed_cycle(4)
    # the directed C4 is the canonical witness: it avoids all four obstructions
    for H in (core.K2_digon(), core.C3(), core.arrowK2_plus_K1(), core.S2_plus()):
        assert not core.contains_induced(C4, H)
    # S2+ contains itself; out-star is not an in-star
    assert core.contains_induced(core.S2_plus(), core.S2_plus())
    assert not core.contains_induced(core.S2_plus(), core.S2_minus())
    # arrowK2_K1 (arc + isolated) does NOT occur induced in S2-: the only
    # non-adjacent pair is the two leaves, but they share centre 0 as common
    # neighbour, so no third vertex is isolated from an arc -> absent.
    assert not core.contains_induced(core.S2_minus(), core.arrowK2_plus_K1())
    # but it DOES occur in the directed path P+(2): arc 0->1 with vertex 2... 2
    # is adjacent to 1, so check P+(3) instead: 0->1, with vertex 3 isolated from
    # the arc 0->1 (0-3 and 1-3 both non-edges).
    assert core.contains_induced(core.P_plus(3), core.arrowK2_plus_K1())


def test_oriented_forest_and_star_classifiers():
    assert core.is_oriented_forest(*core.arrowK2_plus_K1())
    assert core.is_oriented_forest(*core.S2_plus())
    assert not core.is_oriented_forest(*core.C3())          # cycle
    assert core.is_disjoint_union_of_oriented_stars(*core.S2_plus())
    assert core.is_disjoint_union_of_oriented_stars(*core.S2_minus())
    # P+(3) is a path on 4 vertices: NOT a union of stars (has 2 deg>1 vertices)
    assert not core.is_disjoint_union_of_oriented_stars(*core.P_plus(3))
    # P+(2) IS a star (one centre of degree 2)
    assert core.is_disjoint_union_of_oriented_stars(*core.P_plus(2))


# --------------------------------------------------------------------------- #
#  PRIMARY LANDMARK: Theorem 6.1  chi_d(Forb_ind(K2_digon, ->C3, ->K2+K1)) = 2
# --------------------------------------------------------------------------- #

def test_thm_6_1_n6():
    res = oracle.thm_6_1(6)
    assert res["n_in_Forb_ind"] == 916
    assert res["max_chi_d"] == 2
    assert res["chi_d_distribution"] == {1: 504, 2: 412}
    assert res["bound_violated"] is False
    assert res["first_attained_n"]["2"] == 4          # chi_d=2 first at n=4
    w = res["max_witness"]
    assert w["n"] == 4 and w["chi_d"] == 2
    # witness is a directed C4
    assert sorted(map(tuple, w["arcs"])) == sorted([(2, 0), (1, 2), (0, 3), (3, 1)])


# --------------------------------------------------------------------------- #
#  SECONDARY LANDMARK: Conjecture 6.2  chi_d(Forb_ind(K2_digon,->C3,S2+)) = 2
# --------------------------------------------------------------------------- #

def test_conj_6_2_n7():
    res = oracle.conj_6_2(7)
    assert res["max_chi_d"] == 2
    assert res["bound_violated"] is False              # consistent with conj = 2
    assert res["first_attained_n"]["2"] == 4
    assert res["chi_d_distribution"] == {1: 426, 2: 96}
    assert res["n_in_Forb_ind"] == 522


# --------------------------------------------------------------------------- #
#  Exact finite identities (cross-check the chi_d engine)
# --------------------------------------------------------------------------- #

def test_tournament_tower():
    for k in range(1, 5):
        r = oracle.tower(k)
        assert r["matches"] and r["chi_d"] == k, r


def test_cycle_substitution():
    for base in ["K1", "K2_digon", "C3"]:
        for k in [3, 4]:
            assert oracle.cycle_substitution(k, base)["matches"]


def test_check_construction_directed_c4():
    r = oracle.check_construction(4, [(0, 1), (1, 2), (2, 3), (3, 0)],
                                  forbidden=["K2_digon", "C3", "arrowK2_K1", "S2+"])
    assert r["is_oriented"] and r["is_triangle_free"]
    assert r["chi_d"] == 2
    assert r["in_Forb_ind"] is True
