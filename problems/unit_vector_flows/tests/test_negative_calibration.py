"""Negative calibration: a cubic graph with a bridge admits no S²-flow.

The numerical oracle must refuse it (status="unknown", residual far above
machine epsilon), and the sympy Gröbner backend must certify infeasibility
by reducing the pinned ideal to the unit ideal.
"""
from __future__ import annotations

import networkx as nx
import pytest

from exact import has_one_in_groebner
from graphs import k4_bridge_dumbbell
from witness import find_witness


@pytest.fixture(scope="module")
def G():
    return k4_bridge_dumbbell()


def test_is_cubic_with_a_bridge(G):
    assert all(d == 3 for _, d in G.degree())
    assert nx.edge_connectivity(G) == 1
    assert len(list(nx.bridges(G))) == 1


def test_numerical_oracle_refuses(G):
    r = find_witness(G, restarts=200, seed=2026, residual_threshold=1e-10)
    assert r.status == "unknown", "numerical oracle wrongly produced a witness"
    assert r.best_residual_squared > 1e-3, (
        f"residual {r.best_residual_squared:.3e} suspiciously close to zero"
    )


def test_groebner_certifies_infeasibility(G):
    res = has_one_in_groebner(G, pin=True)
    assert res.contains_one is True
    assert "|GB|=1" in res.note
