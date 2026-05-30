"""Regression tests for the two-auxiliary-vertex EQ_3 splitter search.

This pins the decisive escape-hatch experiment for the Fanout Barrier
(D73/D74).  The search asks whether TWO auxiliary vertices added to an
n=7 EQ_3 base gadget can produce a faithful free-bit splitter: R_T =
{000,111} on three disjoint ports with JOINT output capacity on BOTH
equality vectors (each realized by an LFO leaving all six port endpoints
at back-degree <= 1).

Verdict pinned here: NO such two-aux splitter exists across the searched
scope (all 31 distinct n=7 EQ_3 base gadgets, both auxiliaries with all
2^15 arc-orientations each, plus the structured pure-auxiliary-coupling
topology).  Many extensions keep R_T = EQ_3, but NONE gains joint
capacity on even one equality vector, let alone both.

The fast pruned LFO enumerator (`enum_lfos_deg`) is validated against the
brute-force enumerator, and the no-capacity verdict on the pinned base
matches the independent serial run.
"""
from __future__ import annotations

import itertools
import os
import sys

import pytest


SCRIPT_DIR = os.path.join(os.path.dirname(__file__), "..", "scripts")
sys.path.insert(0, os.path.abspath(SCRIPT_DIR))

from two_aux_eq3_search import (  # noqa: E402
    EQ3,
    collect_eq3_bases,
    enum_lfos_deg,
    relation_and_joint,
    run_all_bases,
    structured_compose_search,
    two_aux_search_one_base,
    verify_splitter,
)
from port_relation_census import valid_lfos, back_degrees  # noqa: E402
from verify import verify  # noqa: E402
from implication_fanout_census import (  # noqa: E402
    EQ3_GADGET,
    EQ3_GADGET_ORIENT,
    EQ3_GADGET_PORTS,
)


# --------------------------------------------------------------------
# Enumerator validation (trust root)
# --------------------------------------------------------------------

def test_enum_lfos_matches_brute_n7():
    """The pruned backtracking enumerator returns exactly the brute-force
    set of LFOs (positions), validated on several random n=7 tournaments."""
    import random
    rng = random.Random(11)
    for _ in range(8):
        n = 7
        T = [[0] * n for _ in range(n)]
        for i in range(n):
            for j in range(i + 1, n):
                if rng.random() < 0.5:
                    T[i][j] = 1
                else:
                    T[j][i] = 1
        brute = set()
        for P in itertools.permutations(range(n)):
            if verify(T, list(P))["is_linear_forest"]:
                pos = [0] * n
                for k, v in enumerate(P):
                    pos[v] = k
                brute.add(tuple(pos))
        mine = {pos for pos, _deg in enum_lfos_deg(T)}
        assert mine == brute


def test_enum_lfos_degrees_correct():
    """Back-degree vectors from the enumerator match the verifier's."""
    T = EQ3_GADGET
    n = len(T)
    for pos, deg in enum_lfos_deg(T):
        order = [0] * n
        for v, p in enumerate(pos):
            order[p] = v
        ref = back_degrees(T, order)
        assert list(deg) == ref


# --------------------------------------------------------------------
# Base collection
# --------------------------------------------------------------------

def test_collect_eq3_bases_count():
    """The collection of distinct n=7 EQ_3 base gadgets (port-pinned to
    positions (0,1),(2,3),(4,5)) is stable at 31, and every base really
    realizes R_T = EQ_3 on its ports."""
    bases = collect_eq3_bases(7)
    assert len(bases) == 31
    for base in bases:
        T = base["T"]
        ports = [tuple(p) for p in base["ports"]]
        assert ports == [(0, 1), (2, 3), (4, 5)]
        R, _joint = relation_and_joint(T, ports, base["orient"])
        assert R == EQ3


def test_pinned_gadget_is_among_bases_equivalent():
    """The pinned D74 EQ_3 gadget realizes EQ_3 (sanity cross-link)."""
    R, joint = relation_and_joint(EQ3_GADGET, EQ3_GADGET_PORTS,
                                  EQ3_GADGET_ORIENT)
    assert R == EQ3
    assert joint == frozenset()  # D73: no capacity on the bare gadget


# --------------------------------------------------------------------
# One-aux reproduction (cross-check vs D74 baseline) and two-aux verdict
# --------------------------------------------------------------------

def test_one_aux_pinned_reproduces_baseline():
    """The fast enumerator reproduces D74's one-aux baseline on the
    pinned gadget: 13 EQ_3-preserving extensions, none with capacity."""
    pinned = {"T": [r[:] for r in EQ3_GADGET],
              "ports": [list(p) for p in EQ3_GADGET_PORTS],
              "orient": list(EQ3_GADGET_ORIENT)}
    res = two_aux_search_one_base(pinned, n_aux=1)
    assert res["extensions_tried"] == 128
    assert res["eq3_preserved"] == 13
    assert res["both_equality_capacity_found"] is False
    assert res["one_equality_capacity_found"] is False


@pytest.mark.slow
def test_two_aux_pinned_no_capacity():
    """Decisive single-base result: two auxiliaries on the pinned n=7
    EQ_3 gadget keep R_T = EQ_3 in 220 of 2^15 extensions, but NONE gains
    joint capacity on even one equality vector.  (~8 min; run with
    `-m slow`.)"""
    pinned = {"T": [r[:] for r in EQ3_GADGET],
              "ports": [list(p) for p in EQ3_GADGET_PORTS],
              "orient": list(EQ3_GADGET_ORIENT)}
    res = two_aux_search_one_base(pinned, n_aux=2)
    assert res["extensions_tried"] == 32768
    assert res["eq3_preserved"] == 220
    assert res["both_equality_capacity_found"] is False
    assert res["one_equality_capacity_found"] is False


# --------------------------------------------------------------------
# Structured pure-auxiliary-coupling search (D74 §5 escape topology)
# --------------------------------------------------------------------

def test_structured_compose_no_capacity():
    """The structured topology (3 ports at a fixed transitive baseline +
    2 auxiliaries free + 1 top-pad) cannot even force R_T = EQ_3 through
    auxiliary coupling alone, so a fortiori has no capacity.  Fast
    (2^13 = 8192 masks)."""
    out = structured_compose_search()
    assert out["extensions_tried"] == 8192
    assert out["eq3_preserved"] == 0
    assert out["both_equality_capacity_found"] is False
    assert out["one_equality_capacity_found"] is False


# --------------------------------------------------------------------
# Full-scope aggregate verdict (slow: the entire 31-base x 2^15 sweep)
# --------------------------------------------------------------------

@pytest.mark.slow
def test_full_sweep_no_capacity_verdict():
    """The decisive verdict, pinned: across ALL 31 distinct n=7 EQ_3
    bases x 2^15 aux-orientations (1,015,808 extensions), 5900 keep
    R_T = EQ_3 and ZERO gain joint capacity on even one equality vector.
    No two-aux EQ_3 splitter exists over an n=7 base.  (~30 min; run with
    `-m slow`.)"""
    out = run_all_bases(n_aux=2)
    assert out["num_bases"] == 31
    assert out["total_eq3_preserved_extensions"] == 5900
    assert out["total_both_capacity"] == 0
    assert out["total_one_capacity"] == 0
    assert out["both_capacity_found"] is False
    assert out["one_capacity_found"] is False
    assert out["both_capacity_example"] is None
    assert out["one_capacity_example"] is None


# --------------------------------------------------------------------
# Verifier behaviour (so a future positive find is checked correctly)
# --------------------------------------------------------------------

def test_verify_splitter_rejects_noncapacity_gadget():
    """The independent verifier correctly reports the bare EQ_3 gadget as
    NOT a faithful splitter (no capacity on either equality vector)."""
    out = verify_splitter(EQ3_GADGET, EQ3_GADGET_PORTS, EQ3_GADGET_ORIENT)
    assert out["is_tournament"] is True
    assert out["ports_disjoint"] is True
    assert out["R_T_is_EQ3"] is True
    assert out["joint_capacity_000"] is False
    assert out["joint_capacity_111"] is False
    assert out["is_faithful_splitter"] is False


def test_verify_splitter_conjunction_is_consistent():
    """The verdict `is_faithful_splitter` is exactly the AND of the four
    independent gates (tournament, disjoint ports, R_T = EQ_3, joint
    capacity on both equality vectors).  Checked on the bare gadget so a
    future positive find would not be silently dropped by a verdict that
    disagrees with its own gates."""
    out = verify_splitter(EQ3_GADGET, EQ3_GADGET_PORTS, EQ3_GADGET_ORIENT)
    expected = (out["is_tournament"] and out["ports_disjoint"]
                and out["R_T_is_EQ3"] and out["joint_capacity_000"]
                and out["joint_capacity_111"])
    assert out["is_faithful_splitter"] == expected


def test_verify_splitter_rejects_n6_iso_reps_all_ports():
    """Independent cross-check via the brute-force verifier: NO 6-vertex
    tournament (over isomorphism-class reps) with any disjoint 3-port
    tuple and any orientation is a faithful EQ_3 splitter (R_T = {000,111}
    with joint capacity on BOTH vectors).  This re-derives D73's
    no-capacity finding at n=6 through `verify_splitter` (which uses the
    brute-force trust-root LFO enumerator), confirming the verifier's
    reject path over the whole n=6 iso-class.  (~10 s.)"""
    import itertools
    from port_relation_census import tournament_iso_reps

    def disjoint(pt):
        seen = set()
        for x, y in pt:
            if x in seen or y in seen:
                return False
            seen.update((x, y))
        return True

    pairs = [(i, j) for i in range(6) for j in range(i + 1, 6)]
    port_tuples = [pt for pt in itertools.combinations(pairs, 3)
                   if disjoint(pt)]
    orientations = list(itertools.product((0, 1), repeat=3))
    any_splitter = False
    for T in tournament_iso_reps(6):
        for pt in port_tuples:
            for o in orientations:
                out = verify_splitter(T, list(pt), o)
                if out["is_faithful_splitter"]:
                    any_splitter = True
                    break
            if any_splitter:
                break
        if any_splitter:
            break
    assert any_splitter is False


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
