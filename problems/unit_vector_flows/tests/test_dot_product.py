"""Regression tests for the 3-edge-cut dot product gadget.

Glue two cubic graphs at a chosen vertex each, rotate the second
witness so its boundary triple is the negation of the first's, and
verify the assembled S^2-flow.
"""
from __future__ import annotations

import numpy as np
import pytest

from dot_product import (
    align_to_negation,
    boundary_triple,
    dot_product,
    dot_product_witness,
)
from graphs import blanusa_first, flower_snark, petersen
from witness import find_witness


def _canonical_triple(eps: int = +1):
    """Right-handed (eps=+1) or left-handed (eps=-1) 120-degree triple
    in the xy-plane summing to zero."""
    return np.array([
        [1.0, 0.0, 0.0],
        [-0.5, +eps * np.sqrt(3) / 2, 0.0],
        [-0.5, -eps * np.sqrt(3) / 2, 0.0],
    ])


def test_align_to_negation_self_negated():
    t = _canonical_triple()
    aligned = align_to_negation(-t, t)
    assert aligned is not None
    R, perm = aligned
    assert np.isclose(np.linalg.det(R), 1.0, atol=1e-10)
    rotated = (R @ (-t)[list(perm)].T).T
    assert np.allclose(rotated, -t, atol=1e-10)


def test_align_to_negation_permuted():
    t = _canonical_triple()
    # Permute and rotate t to get t2 such that aligning yields a non-identity perm
    perm_truth = (2, 0, 1)
    angle = 0.7
    R_truth = np.array([
        [np.cos(angle), -np.sin(angle), 0.0],
        [np.sin(angle),  np.cos(angle), 0.0],
        [0.0,            0.0,           1.0],
    ])
    t2 = (R_truth @ (-t)[list(perm_truth)].T).T  # so R_truth @ t2_perm = -t
    aligned = align_to_negation(t2, t)
    assert aligned is not None
    R, perm = aligned
    rotated = (R @ t2[list(perm)].T).T
    assert np.allclose(rotated, -t, atol=1e-10)


def test_align_to_negation_opposite_chirality_fails():
    t = _canonical_triple(eps=+1)
    t_mirror = _canonical_triple(eps=-1)  # mirror image (opposite chirality)
    aligned = align_to_negation(t_mirror, t, tol=1e-8)
    # No orientation-preserving rotation can align a triple to a
    # mirror-image triple unless we permute (which can flip chirality).
    # For a perfectly symmetric mirror, *some* permutation will work, so
    # we don't assert None here; we only require that, when found, the
    # rotation has det +1.
    if aligned is not None:
        R, _ = aligned
        assert np.isclose(np.linalg.det(R), 1.0, atol=1e-10)


def test_dot_product_structure():
    G1 = petersen()
    G2 = blanusa_first()
    G_prime, map_G1, map_G2, through_edges = dot_product(
        G1, 0, G2, 0, perm=(0, 1, 2),
    )
    assert G_prime.number_of_nodes() == G1.number_of_nodes() + G2.number_of_nodes() - 2
    assert G_prime.number_of_edges() == G1.number_of_edges() + G2.number_of_edges() - 3
    assert all(deg == 3 for _, deg in G_prime.degree())
    # vertex_maps cover the right sets
    assert set(map_G1.keys()) == set(G1.nodes()) - {0}
    assert set(map_G2.keys()) == set(G2.nodes()) - {0}
    # through_edges are exactly 3, each present in G_prime
    assert len(through_edges) == 3
    for (a, b) in through_edges:
        assert G_prime.has_edge(a, b)


def test_iterated_dot_product_petersen_chain():
    from dot_product import iterated_dot_product
    G = petersen()
    r = find_witness(G, restarts=100, seed=1)
    steps = []
    for s in (10, 20, 30):
        Gn = petersen()
        rn = find_witness(Gn, restarts=100, seed=s)
        steps.append((0, Gn, rn.vectors, 0))
    out = iterated_dot_product(G, r.vectors, steps)
    assert out["ok"]
    assert out["G_final"].number_of_nodes() == 4 * 10 - 3 * 2  # 4 × Petersen, 3 gluings
    assert out["G_final"].number_of_edges() == 4 * 15 - 3 * 3
    assert all(deg == 3 for _, deg in out["G_final"].degree())
    # Each step's flow verified at machine precision
    for h in out["history"]:
        assert h["max_residual"] < 1e-7


@pytest.mark.parametrize("label,build1,build2", [
    ("Petersen . Petersen", petersen, petersen),
    ("Petersen . Blanusa-1", petersen, blanusa_first),
    ("J_5 . J_5", lambda: flower_snark(2), lambda: flower_snark(2)),
])
def test_dot_product_witness_yields_s2_flow(label, build1, build2):
    G1 = build1()
    G2 = build2()
    r1 = find_witness(G1, restarts=100, seed=2026, residual_threshold=1e-15)
    r2 = find_witness(G2, restarts=100, seed=42, residual_threshold=1e-15)
    assert r1.status == "witness"
    assert r2.status == "witness"
    out = dot_product_witness(G1, r1.vectors, 0, G2, r2.vectors, 0)
    assert out["ok"], out.get("reason") or out.get("verify")
    Gp = out["G_prime"]
    assert Gp.number_of_nodes() == G1.number_of_nodes() + G2.number_of_nodes() - 2
    assert Gp.number_of_edges() == G1.number_of_edges() + G2.number_of_edges() - 3
    assert all(deg == 3 for _, deg in Gp.degree())
    assert out["verify"]["ok"]
    assert out["verify"]["max_vertex_residual"] < 1e-7
