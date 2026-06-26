"""Sound-oracle regression tests for the chordal-digraph (C_3) dichromatic
construction-size problem (arXiv:2202.01006).

Run:  ../.venv/bin/python -m pytest -q   (from the scripts/ or problem dir)
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

import core
import oracle


# --------------------------- C_3 membership ------------------------------- #

def test_directed_triangle_in_C3_chi2():
    """G_2 = directed triangle: in C_3, chi_vec = 2."""
    n, arcs = 3, [(0, 1), (1, 2), (2, 0)]
    assert core.is_C3(n, arcs)
    assert core.dichromatic_number(n, arcs) == 2


def test_TT3_not_in_C3():
    n, arcs = 3, [(0, 1), (1, 2), (0, 2)]
    assert core.has_transitive_triangle(n, arcs)
    assert not core.is_C3(n, arcs)


def test_directed_C4_not_in_C3():
    n, arcs = 4, [(0, 1), (1, 2), (2, 3), (3, 0)]
    assert core.has_long_induced_dicycle(n, arcs, 4)
    assert not core.is_C3(n, arcs)


def test_digon_not_oriented():
    assert not core.is_oriented([(0, 1), (1, 0)])
    assert not core.is_C3(2, [(0, 1), (1, 0)])


def test_single_vertex_in_C3_chi1():
    assert core.is_C3(1, [])
    assert core.dichromatic_number(1, []) == 1


def test_chordal_path_no_long_dicycle():
    """A transitive-triangle-free oriented graph with a chord that breaks a
    would-be C4 into triangles is allowed only if no TT3 forms; here we just
    confirm a directed triangle plus a pendant stays in C_3."""
    n, arcs = 4, [(0, 1), (1, 2), (2, 0), (3, 0)]  # triangle + arc 3->0
    # 3->0 and triangle: check no TT3 (3->0->1 needs 3->1 to be TT3; absent)
    assert not core.has_transitive_triangle(n, arcs)
    assert core.is_C3(n, arcs)


# --------------------------- known landmarks ------------------------------ #

def test_m1_equals_1():
    res = oracle.m_of_k(1, n_max=2)
    assert res["m_k"] == 1


def test_m2_equals_3():
    """THE reproduced known value: m(2) = 3 (directed triangle = G_2);
    no C_3 digraph with chi_vec >= 2 on 1 or 2 vertices."""
    assert oracle.extremal_small_n(1)["max_chi_in_C3"] == 1
    assert oracle.extremal_small_n(2)["max_chi_in_C3"] == 1
    r3 = oracle.extremal_small_n(3, ub=2)
    assert r3["max_chi_in_C3"] == 2
    res = oracle.m_of_k(2, n_max=3)
    assert res["m_k"] == 3
    # the witness is a directed triangle: 3 arcs, each vertex out-deg 1
    w = res["witness"]
    assert len(w) == 3


def test_m3_lower_bound_n4_n5():
    """Partial reproduction of m(3) >= 8: no C_3 with chi_vec >= 3 on n=4,5
    (full n<=7 scan in the ledger; here we test the cheap end)."""
    assert oracle.extremal_small_n(4, ub=3)["max_chi_in_C3"] == 2
    assert oracle.extremal_small_n(5, ub=3)["max_chi_in_C3"] == 2
