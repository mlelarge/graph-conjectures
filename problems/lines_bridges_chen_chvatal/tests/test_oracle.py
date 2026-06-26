"""Regression tests for the lines+bridges oracle (arXiv:1606.06011).

These pin the EXACT known values the substrate was verified against:
  * C4: ell=1, br=0, n=4 -> ell+br=1<4, the unique smallest (bridgeless) CE.
  * full connected-graph census n=4..7:
      n=4: 1 CE (1 bridgeless, 0 bridge)
      n=5: 4 CE (4 bridgeless, 0 bridge)
      n=6: 4 CE (3 bridgeless, 1 bridge)
      n=7: 2 CE (0 bridgeless, 2 bridge)
Plus sanity on lines/bridges of small named graphs.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

import core
import oracle


# --------------------------------------------------------------------------- #
#  C4 -- the keystone known value
# --------------------------------------------------------------------------- #

def test_c4_single_universal_line():
    n, edges = oracle.cycle(4)
    res = oracle.check_construction(n, edges, name="c4")
    assert res["ell"] == 1, res
    assert res["br"] == 0, res
    assert res["n"] == 4
    assert res["is_counterexample"] is True
    assert res["bridgeless"] is True
    # the single line is the universal line on all four vertices
    assert res["lines"] == [[0, 1, 2, 3]], res["lines"]


# --------------------------------------------------------------------------- #
#  Sanity: bridges and lines of basic graphs
# --------------------------------------------------------------------------- #

def test_path_all_bridges():
    n, edges = oracle.path(5)          # P5: every edge is a bridge
    assert core.br(n, edges) == 4


def test_cycle_no_bridges():
    n, edges = oracle.cycle(6)
    assert core.br(n, edges) == 0


def test_complete_k4_lines():
    # K4: diameter 1, every pair gives the line {a,b} only (no x is between);
    # so there are C(4,2)=6 distinct 2-element lines, ell=6, br=0, 6>=4 holds.
    n, edges = oracle.complete(4)
    res = oracle.check_construction(n, edges, name="k4")
    assert res["br"] == 0
    assert res["ell"] == 6, res
    assert res["predicate_holds"] is True
    assert res["is_counterexample"] is False


def test_distances_exact():
    # P4: 0-1-2-3, d(0,3)=3
    n, edges = oracle.path(4)
    dist = core.all_pairs_distances(n, edges)
    assert dist[0][3] == 3
    assert dist[1][2] == 1


# --------------------------------------------------------------------------- #
#  Full census n=4..7 -- the verified truth table
# --------------------------------------------------------------------------- #

_CENSUS = {
    4: dict(total=6,   ce=1, bridgeless=1, bridge=0),
    5: dict(total=21,  ce=4, bridgeless=4, bridge=0),
    6: dict(total=112, ce=4, bridgeless=3, bridge=1),
    7: dict(total=853, ce=2, bridgeless=0, bridge=2),
}


def test_census_n4_to_7():
    for n, exp in _CENSUS.items():
        res = oracle.enumerate_counterexamples(n, store_witnesses=False)
        assert res["n_connected_graphs"] == exp["total"], (n, res)
        assert res["n_counterexamples"] == exp["ce"], (n, res)
        assert res["n_counterexamples_bridgeless"] == exp["bridgeless"], (n, res)
        assert res["n_counterexamples_with_bridge"] == exp["bridge"], (n, res)
