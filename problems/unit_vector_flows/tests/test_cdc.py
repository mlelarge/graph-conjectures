"""Regression tests for the CDC search in scripts/cdc.py.

We verify that:
  - the search finds *some* CDC on small named snarks;
  - the resulting CDC has every edge covered exactly twice;
  - an orientable CDC exists for Petersen, Blanuša, and J_5 within a
    reasonable budget (and the orient_cdc routine returns a list of the
    same length, properly cancelling on every edge).
"""
from __future__ import annotations

import networkx as nx
import pytest

from cdc import cdc_summary, find_oriented_cdc, find_cdc, iter_cdcs, orient_cdc
from graphs import blanusa_first, flower_snark, petersen


def _check_cdc(G, cdc):
    summary = cdc_summary(cdc, G)
    assert summary["all_edges_covered_twice"], summary


def _check_oriented(G, oriented):
    # Each directed edge appears in exactly one cycle going "forward" and one going "reverse".
    arc_counts: dict = {}
    for cyc in oriented:
        L = len(cyc)
        for i in range(L):
            u, v = cyc[i], cyc[(i + 1) % L]
            arc_counts[(u, v)] = arc_counts.get((u, v), 0) + 1
    for (u, v), c in arc_counts.items():
        # The reverse arc must also be present the same number of times
        rev = arc_counts.get((v, u), 0)
        assert c == 1 and rev == 1, f"arc {(u, v)} count={c} rev={rev}"
    # Every undirected edge should appear as a forward arc somewhere
    for (u, v) in G.edges():
        assert (u, v) in arc_counts or (v, u) in arc_counts


@pytest.mark.parametrize("name,builder", [
    ("Petersen", petersen),
    ("Blanusa-1", blanusa_first),
    ("J_5", lambda: flower_snark(2)),
])
def test_find_cdc_basic(name, builder):
    G = builder()
    cdc = find_cdc(G, time_budget_s=15.0)
    assert cdc is not None, f"{name}: no CDC within 15s"
    _check_cdc(G, cdc)


@pytest.mark.parametrize("name,builder", [
    ("Petersen", petersen),
    ("Blanusa-1", blanusa_first),
    ("J_5", lambda: flower_snark(2)),
])
def test_find_oriented_cdc(name, builder):
    G = builder()
    oriented = find_oriented_cdc(G, time_budget_s=15.0, max_cdcs_to_check=500)
    assert oriented is not None, f"{name}: no orientable CDC found"
    _check_oriented(G, oriented)


def test_orient_petersen_pentagons_fails():
    # Petersen's 6-pentagon CDC is the canonical *non-orientable* CDC.
    # The first CDC the backtracker finds is the pentagon one; it must
    # fail to orient. This is a sanity guard against orient_cdc
    # accidentally accepting a non-orientable cover.
    G = petersen()
    cdc = next(iter(iter_cdcs(G, max_cycle_length=5, time_budget_s=10.0)))
    assert all(len(c) == 5 for c in cdc)
    assert len(cdc) == 6
    assert orient_cdc(cdc, G) is None
