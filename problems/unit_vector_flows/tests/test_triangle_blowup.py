"""Regression tests for the HMM 2026 triangle-blow-up gadget.

The blown-up graph G' is cubic with $n + 2$ vertices and $m + 3$
edges; the induced flow keeps the original spoke values and assigns
the three triangle edges via the closed form in
``triangle_blowup.triangle_blowup_flow``. We verify:

  - The closed-form flow satisfies Kirchhoff at the three triangle
    vertices and unit-norm on every triangle edge, for both chiralities.
  - Applied to Petersen, Blanusa-1, and J_5, the resulting cubic graph
    has a valid $S^2$-flow (Kirchhoff at every vertex, norm 1 on every
    edge), checked by ``witness.verify_witness``.
  - The blown-up graph has the expected n + 2 / m + 3 size.
"""
from __future__ import annotations

import numpy as np
import pytest

from graphs import blanusa_first, flower_snark, petersen
from triangle_blowup import (
    extend_witness_through_blowup,
    triangle_blowup,
    triangle_blowup_flow,
)
from witness import find_witness


@pytest.fixture(scope="module")
def canonical_spokes():
    f1 = np.array([1.0, 0.0, 0.0])
    f2 = np.array([-0.5, np.sqrt(3) / 2, 0.0])
    f3 = np.array([-0.5, -np.sqrt(3) / 2, 0.0])
    return f1, f2, f3


@pytest.mark.parametrize("chirality", [+1, -1])
def test_closed_form_triangle_flow(canonical_spokes, chirality):
    f1, f2, f3 = canonical_spokes
    g12, g13, g23 = triangle_blowup_flow(f1, f2, f3, chirality=chirality)
    # Unit norms
    assert np.isclose(np.linalg.norm(g12), 1.0, atol=1e-12)
    assert np.isclose(np.linalg.norm(g13), 1.0, atol=1e-12)
    assert np.isclose(np.linalg.norm(g23), 1.0, atol=1e-12)
    # Kirchhoff at the three triangle vertices
    assert np.allclose(f1 + g12 + g13, 0.0, atol=1e-12)
    assert np.allclose(f2 - g12 + g23, 0.0, atol=1e-12)
    assert np.allclose(f3 - g13 - g23, 0.0, atol=1e-12)


@pytest.mark.parametrize("name,builder", [
    ("Petersen", petersen),
    ("Blanusa-1", blanusa_first),
    ("J_5", lambda: flower_snark(2)),
])
@pytest.mark.parametrize("chirality", [+1, -1])
def test_blowup_preserves_s2_flow(name, builder, chirality):
    G = builder()
    n0, m0 = G.number_of_nodes(), G.number_of_edges()
    r = find_witness(G, restarts=100, seed=2026, residual_threshold=1e-15)
    assert r.status == "witness"
    result = extend_witness_through_blowup(G, r.vectors, v=0, chirality=chirality)
    G_prime = result["G_prime"]
    assert G_prime.number_of_nodes() == n0 + 2
    assert G_prime.number_of_edges() == m0 + 3
    assert all(deg == 3 for _, deg in G_prime.degree())
    assert result["verify"]["ok"], result["verify"]


def test_blowup_graph_structure_petersen():
    G = petersen()
    G_prime, vertex_map, old_to_new_spokes, triangle_edges = triangle_blowup(G, v=0)
    # vertex_map covers every non-v vertex of G
    assert set(vertex_map.keys()) == set(G.nodes()) - {0}
    # 3 spokes mapped
    assert len(old_to_new_spokes) == 3
    # 3 triangle edges
    assert len(triangle_edges) == 3
    # All triangle edges are present in G_prime
    for a, b in triangle_edges:
        assert G_prime.has_edge(a, b)
    # Each new vertex v_i has degree 3 in G_prime
    new_vs = {vi for ((_, _), (vi, _)) in old_to_new_spokes}
    for vi in new_vs:
        assert G_prime.degree(vi) == 3
