"""Regression tests for the implication-style fanout census (D74).

Findings pinned (n <= 7):

  * Forward/reverse implication relations are realizable as R_T.
  * Their OUTPUT ports carry residual capacity (unlike EQ, D73) -- the
    lighter loading (3 forbidden vectors vs EQ's 6) leaves room.
  * BUT no forward-split has FULL (all-port) capacity, and the SOURCE
    port saturates exactly on its active value (branching costs the
    branch point degree 2).
  * Faithful free-bit copy = EQ (implication only relaxes, output >=
    input), and EQ has no capacity (D73).  So implication capacity does
    not yield a faithful occurrence->=3 fanout.
"""
from __future__ import annotations

import os
import sys

import pytest


SCRIPT_DIR = os.path.join(os.path.dirname(__file__), "..", "scripts")
sys.path.insert(0, os.path.abspath(SCRIPT_DIR))

from implication_fanout_census import (  # noqa: E402
    EQ3_GADGET,
    EQ3_GADGET_ORIENT,
    EQ3_GADGET_PORTS,
    FWD_ORBIT,
    REV_ORBIT,
    aux_extension_search,
    census,
    implication_relation,
    refined_capacity_audit,
)


def test_relation_definitions():
    # forward split x->y,z (source 0)
    R = implication_relation(0, [1, 2])
    assert R == frozenset({(0, 0, 0), (0, 0, 1), (0, 1, 0), (0, 1, 1), (1, 1, 1)})
    assert len(FWD_ORBIT) == 3   # source in {0,1,2}
    assert len(REV_ORBIT) == 3


def test_n6_forward_has_output_capacity_but_not_full():
    out = census(6)
    assert out["forward_split_as_RT_count"] > 0
    assert out["forward_output_capacity_found"] is True   # output capacity exists
    assert out["forward_full_capacity_found"] is False    # but not all ports


def test_n6_reverse_no_full_capacity():
    out = census(6)
    assert out["reverse_split_as_RT_count"] > 0
    assert out["reverse_full_capacity_found"] is False


def test_refined_audit_n6_no_both_equality_capacity():
    """Refined audit (correcting the earlier overclaim): a forward split
    CAN have joint capacity on 111 (so the source does NOT always
    saturate on its active value), and a reverse split on 000 -- but
    NEITHER has joint capacity on BOTH equality vectors {000,111}, which
    an EQ_3 splitter for a free variable would need."""
    a = refined_capacity_audit(6)
    # overclaim correction: 111-joint capacity IS achievable for forward
    assert a["forward_111_in_joint_found"] is True
    assert a["forward_source_has_bit1_capacity_found"] is True
    assert a["reverse_000_in_joint_found"] is True
    # the binding obstruction: never both equality vectors jointly
    assert a["forward_both_equality_in_joint_found"] is False
    assert a["reverse_both_equality_in_joint_found"] is False


def test_refined_audit_n7_no_both_equality_capacity():
    """Same equality-slice obstruction at n=7 (the first non-trivial
    Path-FAS size): 111-joint achievable for forward, 000-joint for
    reverse, but never both equality vectors jointly."""
    a = refined_capacity_audit(7)
    assert a["forward_111_in_joint_found"] is True
    assert a["reverse_000_in_joint_found"] is True
    assert a["forward_both_equality_in_joint_found"] is False
    assert a["reverse_both_equality_in_joint_found"] is False


def test_one_aux_extension_gains_no_equality_capacity():
    """Pin the one-auxiliary-vertex extension claim: extending the n=7
    EQ_3 gadget by one aux vertex (all 128 orientations) keeps R_T=EQ_3
    in 13 cases, but NONE gains joint capacity on even one equality
    vector.  One auxiliary vertex cannot free the ports."""
    out = aux_extension_search(EQ3_GADGET, EQ3_GADGET_PORTS,
                               EQ3_GADGET_ORIENT, n_aux=1)
    assert out["extensions_tried"] == 128
    assert out["eq3_preserved"] == 13
    assert out["both_equality_capacity_found"] is False
    assert out["one_equality_capacity_found"] is False


def test_eq3_gadget_base_has_no_capacity():
    """Sanity: the pinned EQ_3 gadget realizes {000,111} with empty
    capacity (consistent with D73)."""
    from port_relation_census import build_lfo_cache
    cache = build_lfo_cache(EQ3_GADGET)
    pv = [v for x, y in EQ3_GADGET_PORTS for v in (x, y)]
    R, joint = set(), set()
    for pos, deg in cache:
        raw = tuple(1 if pos[y] < pos[x] else 0 for (x, y) in EQ3_GADGET_PORTS)
        bits = tuple(b ^ o for b, o in zip(raw, EQ3_GADGET_ORIENT))
        R.add(bits)
        if all(deg[v] <= 1 for v in pv):
            joint.add(bits)
    assert frozenset(R) == frozenset({(0, 0, 0), (1, 1, 1)})
    assert joint == set()  # R_comp empty: D73's no-capacity finding


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
