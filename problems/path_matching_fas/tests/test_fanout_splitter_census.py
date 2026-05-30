"""Regression tests for the fanout/splitter census (D73).

Findings pinned here (the Splitter Saturation Invariant, n <= 7):

  * EQ_2 copy gadgets exist at n=6 but never with full output capacity
    (one value is realized only by a zero-residual LFO).
  * EQ_3 splitters exist at n=7 but with EMPTY output capacity
    (R_comp = empty): every equal-LFO saturates a port endpoint.
  * Padding cannot rescue capacity (top padding leaves R_T = EQ_3 and
    R_comp = empty), because pure padding does not change gadget-
    internal port back-degrees.

Consequence: Path-FAS cannot copy an ordering bit to fresh ports under
the degree-2 budget -> fanout is blocked -> the 2-in-3 clause gadget
(D72) cannot be wired into an NP-hardness reduction.
"""
from __future__ import annotations

import os
import sys

import pytest


SCRIPT_DIR = os.path.join(os.path.dirname(__file__), "..", "scripts")
sys.path.insert(0, os.path.abspath(SCRIPT_DIR))

from fanout_splitter_census import (  # noqa: E402
    census,
    eq_relation,
    port_relation_with_capacity,
)
from port_relation_census import build_lfo_cache  # noqa: E402


def test_eq2_copy_exists_but_no_capacity_splitter_n6():
    out = census(6, 2)
    assert out["realizes_EQ_as_RT"] is True       # copy gadget exists
    assert out["capacity_splitter_found"] is False  # but no full capacity


def test_no_eq3_splitter_at_n6():
    out = census(6, 3)
    assert out["realizes_EQ_as_RT"] is False
    assert out["capacity_splitter_found"] is False


def test_no_capacity_eq3_splitter_at_n7():
    """EQ_3 splitters exist at n=7 but with empty output capacity."""
    out = census(7, 3)
    assert out["realizes_EQ_as_RT"] is True          # EQ_3 forced as R_T
    assert out["capacity_splitter_found"] is False    # but R_comp never = EQ_3
    assert out["EQ_with_partial_capacity_found"] is False  # not even partial


def test_padding_does_not_rescue_splitter_capacity():
    """Top padding leaves an EQ_3 gadget's R_comp empty: padding cannot
    add output capacity because it does not change gadget-internal port
    degrees."""
    out = census(7, 3)
    ex = out["realizes_EQ_examples"][0]
    G = ex["T"]
    ports = [tuple(p) for p in ex["ports"]]
    o = tuple(ex["orientation"])
    g = len(G)
    EQ = eq_relation(3)

    def flip(rel):
        return frozenset(tuple(b ^ oi for b, oi in zip(t, o)) for t in rel)

    for E in (1, 2):
        n = g + E
        T = [[0] * n for _ in range(n)]
        for i in range(n):
            for j in range(i + 1, n):
                T[i][j] = 1
        for i in range(g):
            for j in range(g):
                T[i][j] = G[i][j]
        cache = build_lfo_cache(T)
        R, Rc = port_relation_with_capacity(cache, ports)
        assert flip(R) == EQ            # still forces EQ_3
        assert flip(Rc) == frozenset()  # still no capacity


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
