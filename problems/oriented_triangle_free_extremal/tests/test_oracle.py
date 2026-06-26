"""Regression suite pinning the oracle to the paper's known values
(arXiv:2403.02298).  These are the soundness guards: if a future edit to the
solvers breaks any of these, the ground truth is no longer trustworthy.
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
    n, a = C.D25()
    assert n == 25 and len(a) == 125
    assert core.is_oriented(a) and core.is_triangle_free(n, a)
    n4, a4 = C.directed_cycle(4)
    assert core.is_oriented(a4) and core.is_triangle_free(n4, a4)
    n5, a5 = C.transitive_tournament(5)
    assert not core.is_triangle_free(n5, a5)        # tournament has triangles


# ---- exact dichromatic number vs paper's known values ----------------------

@pytest.mark.parametrize("builder,expected", [
    (lambda: C.transitive_tournament(5), 1),        # acyclic
    (lambda: C.directed_cycle(4), 2),               # directed C4
    (lambda: C.paley_tournament(7), 3),             # smallest 3-dichromatic
    (lambda: C.paley_tournament(11), 4),            # smallest 4-dichromatic (unique)
    (lambda: C.D25(), 3),                           # Prop 4.6 headline
])
def test_dichromatic(builder, expected):
    n, a = builder()
    assert core.dichromatic_number(n, a) == expected


# ---- exact acyclic number --------------------------------------------------

def test_acyclic_number():
    n, a = C.transitive_tournament(5)
    assert core.acyclic_number(n, a) == 5           # whole DAG
    n4, a4 = C.directed_cycle(4)
    assert core.acyclic_number(n4, a4) == 3         # drop one vertex


# ---- D25 is 3-dicritical (Prop 4.6) ----------------------------------------

def test_D25_dicritical():
    n, a = C.D25()
    assert oracle.is_dicritical(n, a, 3)


# ---- backward-blowup family: the threshold the paper improves --------------

def test_backward_blowup_threshold():
    # Prop 4.6: C5<-5 (=D25) is already 3-chromatic; smaller blow-ups are not.
    for m, chi in [(2, 2), (3, 2), (5, 3)]:
        n, a = C.backward_blowup_directed_cycle(5, m)
        assert core.is_triangle_free(n, a)
        assert core.dichromatic_number(n, a) == chi


# ---- exact small-n extremal landmarks --------------------------------------

def test_extremal_small_n():
    r3 = oracle.extremal_small_n(3)
    assert r3["t_vec"] == 1                         # no directed cycle fits
    r4 = oracle.extremal_small_n(4)
    assert r4["t_vec"] == 2 and r4["a_vec"] == 3    # directed C4 is extremal
    r5 = oracle.extremal_small_n(5)
    assert r5["t_vec"] == 2


# ---- benchmark wiring ------------------------------------------------------

def test_benchmark_keys():
    n, a = C.D25()
    res = oracle.check_construction(n, a, name="D25")
    for k in ("a_lower_proved", "a_upper_proved", "t_lower_proved",
              "t_upper_proved", "a_conj_scale", "t_conj_scale"):
        assert res["benchmark"][k] > 0
    assert res["alpha_within_proved_band"]          # 13 within [.., ..]
