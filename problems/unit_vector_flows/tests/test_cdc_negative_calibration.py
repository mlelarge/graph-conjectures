"""Negative calibration for the oriented-4-CDC route.

An oriented 4-CDC gives an H4-flow.  On a cubic graph, every H4-flow
induces a nowhere-zero Z_2^2-flow, so it cannot exist on a snark.
"""
from __future__ import annotations

import networkx as nx

from catalogue import is_three_edge_colourable_sat
from cdc import H4Certificate, h4_flow_induces_nz4_flow, verify_h4_flow
from graphs import blanusa_first, k4, petersen
from witness import orient


def test_handcrafted_k4_h4_flow_induces_nz4_flow():
    G = k4()
    edges, _ = orient(G)
    assert edges == [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]
    cert = H4Certificate(
        edges=edges,
        values=[(0, 1), (1, 2), (2, 0), (3, 1), (0, 3), (3, 2)],
    )
    assert verify_h4_flow(G, cert)["ok"]
    induced = h4_flow_induces_nz4_flow(G, cert)
    assert induced["ok"], induced
    assert all(v in (1, 2, 3) for v in induced["z2x2_values"])


def test_petersen_and_blanusa_are_not_three_edge_colourable():
    # If either graph admitted an oriented 4-CDC, it would induce a
    # nowhere-zero Z_2^2-flow, equivalently a 3-edge-colouring for cubic
    # graphs.  This regression catches the false CDC route.
    for builder in (petersen, blanusa_first):
        G = builder()
        assert all(d == 3 for _, d in G.degree())
        assert nx.edge_connectivity(G) >= 2
        assert not is_three_edge_colourable_sat(G)
