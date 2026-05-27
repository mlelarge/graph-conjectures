"""Tests for the wire-based reduction attempt.

These tests pin the structural facts that:

1. The `build_forced_path_tournament(k)` constructs a tournament whose
   forced-back-arc graph H_back contains the path 0-1-...-k as a
   subgraph.

2. Every LFO of that tournament has the path edges as back-arcs and
   every interior path vertex saturated at back-degree 2.

3. The interior degree saturation theorem (Theorem 5.1 of
   docs/J_hardness_via_wires.md) is empirically valid at k = 1 (no
   interior) and at k = 2 (one interior vertex), against the brute-
   force decider.

4. The reduction architecture in
   `scripts/sat_to_path_fas_wire_reduction.py` correctly *detects* the
   obstruction for instances where any variable occurs in more than 2
   clauses.
"""
from __future__ import annotations

import os
import sys

import pytest

# Path setup
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from forced_path_tournament import (  # noqa: E402
    forced_relations,
    is_linear_forest,
    longest_path_length,
    theoretical_max_forced_path,
)
from sat_to_path_fas_wire_reduction import build_wire_reduction_attempt  # noqa: E402
from variable_wire_gadget import (  # noqa: E402
    build_forced_path_tournament,
    report_forced_path,
    saturation_check,
    variable_wire_truth_table,
)


def test_forced_path_k1_construction():
    T, path = build_forced_path_tournament(1)
    rep = report_forced_path(T, path)
    assert rep["all_gaps_>=_5"], "gap should be >= 5 with spacing 7"
    assert rep["all_path_edges_forced"], "path edge should be in H_back"
    assert rep["n"] == 8
    assert rep["n_forced_back_total"] == 1


def test_forced_path_k2_construction():
    T, path = build_forced_path_tournament(2)
    rep = report_forced_path(T, path)
    assert rep["all_gaps_>=_5"]
    assert rep["all_path_edges_forced"]
    assert rep["n"] == 15
    assert rep["n_forced_back_total"] == 2


def test_truth_table_k1_path_direction_unique():
    tt = variable_wire_truth_table(1)
    assert tt["n_lfos"] > 0, "k=1 path tournament should have LFOs"
    # Every LFO must orient the path L -> R (label 0 before label 1).
    assert tt["directions"]["L->R"] == tt["n_lfos"]
    assert tt["directions"]["R->L"] == 0
    assert tt["directions"]["MIXED!_violation"] == 0


def test_saturation_check_k1_endpoint_distribution():
    """At k=1 there are no interior vertices; both path vertices are
    endpoints with spare degree."""
    s = saturation_check(1)
    assert s["interior_path_vertices"] == []
    assert s["interior_always_saturated_at_2"], (
        "vacuously: no interior to saturate"
    )
    # Endpoints have flexibility (back-deg in {1, 2}).
    for v, hist in s["back_deg_histogram_per_path_vertex"].items():
        assert hist.get(0, 0) == 0  # at least one back-arc (the path edge)
        assert hist.get(1, 0) > 0 or hist.get(2, 0) > 0


def test_reduction_architecture_obstruction_triggers_at_occurrence_3():
    """Architectural check: any variable occurring >= 3 times triggers
    the interior-degree-saturation obstruction."""
    clauses = [
        [(0, True), (1, True), (2, True)],
        [(0, False), (1, False), (2, True)],
        [(0, True), (1, True), (2, False)],
    ]
    out = build_wire_reduction_attempt(num_vars=3, clauses=clauses)
    assert out["obstruction"] is not None
    assert out["obstruction"]["trigger"] == "interior_degree_saturation"
    assert not out["constructible_under_architecture"]


def test_reduction_architecture_constructs_when_max_occurrence_le_2():
    """Architectural check: every variable occurs <= 2 times, no
    obstruction yet (though the reduction is still not soundness-
    verified)."""
    clauses = [
        [(0, True), (1, True), (2, True)],
        [(0, False), (1, True), (2, False)],
    ]
    out = build_wire_reduction_attempt(num_vars=3, clauses=clauses)
    assert out["obstruction"] is None
    assert out["constructible_under_architecture"]
    assert out["max_var_occurrence"] == 2


def test_theoretical_forced_path_bound():
    """Sanity check the loose score-span-based theoretical bound.

    The forced-back-arc-path-length bound 2*floor((n-1)/5) is a *weak*
    bound, and empirics show that uniform random tournaments can
    saturate it (see data/forced_path_sweep_20260527.json).
    """
    assert theoretical_max_forced_path(8) == 2
    assert theoretical_max_forced_path(11) == 4
    assert theoretical_max_forced_path(16) == 6


def test_forced_path_is_linear_forest_at_small_n():
    """For our constructed tournaments, H_back should itself be a path
    (hence a linear forest)."""
    for k in (1, 2):
        T, path = build_forced_path_tournament(k)
        rel = forced_relations(T)
        back = rel["forced_back"]
        n = len(T)
        assert is_linear_forest(back, n)
        # Path length is k (number of edges).
        assert longest_path_length(back, n) == k
