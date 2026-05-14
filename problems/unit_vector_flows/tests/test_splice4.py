"""Regression tests for the 4-edge-cut splice gadget.

The 4-cut splice cuts a cubic graph $G$ along a cyclic 4-edge cut $C$
into two 4-bordered cubic pieces, then re-glues two such pieces through
a matching of their boundaries with an $\\mathrm{SO}(3)$ rotation that
aligns the boundary 4-tuples (the cut-edge values seen from each side).

Tests cover:
  - structural sanity of ``find_cyclic_4_cuts`` and ``cut_at_4``;
  - the alignment convention ``R @ T2[perm] = -T1`` enforced by
    ``align_4tuples``;
  - the boundary 4-tuple is unit and sums to zero on a real witness;
  - the round-trip: cut $G$ at a cyclic 4-cut, restrict the global
    witness to each piece, then splice the pieces back together — the
    spliced flow must verify at machine precision.
"""
from __future__ import annotations

import numpy as np
import pytest

from graphs import blanusa_first, flower_snark, petersen
from splice4 import (
    align_4tuples,
    boundary_4tuple,
    cut_at_4,
    find_cyclic_4_cuts,
    splice4_witness,
)
from witness import find_witness, orient


# ---------------------------------------------------------------------------
# Cyclic 4-cut finder structural sanity
# ---------------------------------------------------------------------------


def test_petersen_has_no_cyclic_4_cut():
    """Petersen is cyclically 5-edge-connected; no cyclic 4-cut exists."""
    G = petersen()
    cuts = find_cyclic_4_cuts(G, max_cuts=1)
    assert cuts == []


def test_blanusa_first_has_a_cyclic_4_cut():
    """Blanuša-1 admits cyclic 4-cuts (cyclically 4-edge-connected)."""
    G = blanusa_first()
    cuts = find_cyclic_4_cuts(G, max_cuts=1)
    assert len(cuts) == 1
    cut = cuts[0]
    assert len(cut) == 4


@pytest.mark.parametrize("k", [2, 3, 4, 5])
def test_flower_snark_has_no_cyclic_4_cut(k):
    """Empirically every $J_{2k+1}$ for $k \\in \\{2, 3, 4, 5\\}$
    (i.e., $J_5, J_7, J_9, J_{11}$) is cyclically $\\ge 5$-edge-connected;
    moreover, for $k \\ge 3$ it is cyclically $\\ge 6$-edge-connected.
    No cyclic 4-edge cut exists in any of these graphs. (Recorded as
    a regression so future families can be compared at a glance.)"""
    G = flower_snark(k)
    cuts = find_cyclic_4_cuts(G, max_cuts=1)
    assert cuts == [], (
        f"Surprise: J_{2*k+1} has a cyclic 4-edge cut; docs claim it does not."
    )


# ---------------------------------------------------------------------------
# cut_at_4 structural sanity
# ---------------------------------------------------------------------------


def test_cut_at_4_structure_blanusa():
    G = blanusa_first()
    cut = find_cyclic_4_cuts(G, max_cuts=1)[0]
    result = cut_at_4(G, cut)
    p1, p2 = result["piece_1"], result["piece_2"]
    # Vertex count partitions:
    assert p1.number_of_nodes() + p2.number_of_nodes() == G.number_of_nodes()
    # Edge count: each piece keeps its internal edges; 4 cut edges removed:
    assert (
        p1.number_of_edges() + p2.number_of_edges() + 4
        == G.number_of_edges()
    )
    # Each piece has exactly 4 degree-2 vertices (the boundary) and the rest
    # are degree-3.
    for piece in (p1, p2):
        degs = sorted(d for _, d in piece.degree())
        assert degs.count(2) == 4
        assert degs.count(3) == piece.number_of_nodes() - 4
        # all degrees are 2 or 3
        assert set(degs) <= {2, 3}
    # boundary lists have length 4 and the vertices are degree-2
    assert len(result["boundary_1"]) == 4
    assert len(result["boundary_2"]) == 4
    for b in result["boundary_1"]:
        assert p1.degree(b) == 2
    for b in result["boundary_2"]:
        assert p2.degree(b) == 2


# ---------------------------------------------------------------------------
# Boundary 4-tuple
# ---------------------------------------------------------------------------


def _restrict_witness_to_piece(G, X_G, edges_G, piece, inv_map):
    """Restrict a flow on G to the edges of a piece by indexing through
    the inverse vertex map."""
    edges_G_set = {tuple(sorted(e)): k for k, e in enumerate(edges_G)}
    edges_p, _ = orient(piece)
    X_p = np.zeros((len(edges_p), 3), dtype=np.float64)
    for k, (u, w) in enumerate(edges_p):
        u_old, w_old = inv_map[u], inv_map[w]
        idx = edges_G_set[tuple(sorted((u_old, w_old)))]
        X_p[k] = X_G[idx]
    return X_p


def test_boundary_4tuple_unit_and_sums_to_zero():
    G = blanusa_first()
    r = find_witness(G, restarts=200, seed=2026)
    assert r.status == "witness"
    X_G = np.asarray(r.vectors, dtype=np.float64)

    cut = find_cyclic_4_cuts(G, max_cuts=1)[0]
    result = cut_at_4(G, cut)
    p1, p2 = result["piece_1"], result["piece_2"]
    b1, b2 = result["boundary_1"], result["boundary_2"]
    inv_map_1 = {v_new: v_old for v_old, v_new in result["map_1"].items()}
    inv_map_2 = {v_new: v_old for v_old, v_new in result["map_2"].items()}

    X_p1 = _restrict_witness_to_piece(G, X_G, r.edges, p1, inv_map_1)
    X_p2 = _restrict_witness_to_piece(G, X_G, r.edges, p2, inv_map_2)

    T1 = boundary_4tuple(p1, X_p1, b1)
    T2 = boundary_4tuple(p2, X_p2, b2)

    assert np.allclose(np.linalg.norm(T1, axis=1), 1.0, atol=1e-10)
    assert np.allclose(np.linalg.norm(T2, axis=1), 1.0, atol=1e-10)
    assert np.allclose(T1.sum(axis=0), 0.0, atol=1e-10)
    assert np.allclose(T2.sum(axis=0), 0.0, atol=1e-10)
    # Through-edges connect b1[i] to b2[i]; oriented out of b1, value
    # equals T1[i]; oriented out of b2 (other end of same cut edge),
    # value equals T2[i] = -T1[i].
    assert np.allclose(T2, -T1, atol=1e-10)


# ---------------------------------------------------------------------------
# 4-tuple alignment
# ---------------------------------------------------------------------------


def _canonical_4tuple(eps: int = +1) -> np.ndarray:
    """4-tuple of unit vectors summing to zero in R^3. Tetrahedral
    vertices: 4 unit vectors at the corners of a regular tetrahedron,
    e.g. (+,+,+), (+,-,-), (-,+,-), (-,-,+) all normalised. Tetrahedron
    is achiral (its mirror is congruent to itself), so a single sample
    does not test the chirality structure -- the 5-dim moduli space of
    4 unit vectors summing to 0 is the right test bed."""
    sign = 1.0 if eps > 0 else -1.0
    T = np.array(
        [
            [+1.0, +1.0, +sign * 1.0],
            [+1.0, -1.0, -sign * 1.0],
            [-1.0, +1.0, -sign * 1.0],
            [-1.0, -1.0, +sign * 1.0],
        ]
    ) / np.sqrt(3.0)
    return T


def test_align_4tuples_self_negation():
    T = _canonical_4tuple()
    # We want R @ T2[perm] = -T1. Take T2 = T, T1 = T: solution is
    # R = -I (det=-1, not in SO(3)) UNLESS some permutation flips a sign.
    # For a regular tetrahedron, the negation -T is the same set of
    # points under a 180-degree rotation about an axis through the
    # midpoint of opposite edges -- so a permutation + rotation exists.
    aligned = align_4tuples(T, T, tol=1e-8)
    assert aligned is not None
    R, perm = aligned
    assert np.isclose(np.linalg.det(R), 1.0, atol=1e-10)
    rotated = (R @ T[list(perm)].T).T
    assert np.allclose(rotated, -T, atol=1e-8)


def test_align_4tuples_generic_pair_with_known_solution():
    """Build T2 from -T1 by a known (R, perm), then check alignment
    recovers the (R, perm) up to the redundancy of the alignment."""
    T1 = _canonical_4tuple()
    perm_truth = (2, 0, 3, 1)
    angle = 0.7
    R_truth = np.array(
        [
            [np.cos(angle), -np.sin(angle), 0.0],
            [np.sin(angle), +np.cos(angle), 0.0],
            [0.0, 0.0, 1.0],
        ]
    )
    # R_truth @ T2[perm_truth] = -T1  =>  T2[perm_truth] = R_truth.T @ (-T1)
    # Build T2 by un-permuting:
    target = (R_truth.T @ (-T1).T).T  # shape (4, 3) at indices perm_truth
    T2 = np.zeros_like(T1)
    for i, j in enumerate(perm_truth):
        T2[j] = target[i]
    aligned = align_4tuples(T2, T1, tol=1e-8)
    assert aligned is not None
    R, perm = aligned
    assert np.isclose(np.linalg.det(R), 1.0, atol=1e-10)
    rotated = (R @ T2[list(perm)].T).T
    assert np.allclose(rotated, -T1, atol=1e-8)


# ---------------------------------------------------------------------------
# Round-trip: cut + splice == original
# ---------------------------------------------------------------------------


def test_splice4_roundtrip_blanusa_first():
    G = blanusa_first()
    r = find_witness(G, restarts=200, seed=2026)
    assert r.status == "witness"
    X_G = np.asarray(r.vectors, dtype=np.float64)

    cut = find_cyclic_4_cuts(G, max_cuts=1)[0]
    result = cut_at_4(G, cut)
    p1, p2 = result["piece_1"], result["piece_2"]
    b1, b2 = result["boundary_1"], result["boundary_2"]
    inv_map_1 = {v_new: v_old for v_old, v_new in result["map_1"].items()}
    inv_map_2 = {v_new: v_old for v_old, v_new in result["map_2"].items()}

    X_p1 = _restrict_witness_to_piece(G, X_G, r.edges, p1, inv_map_1)
    X_p2 = _restrict_witness_to_piece(G, X_G, r.edges, p2, inv_map_2)

    out = splice4_witness(p1, X_p1, b1, p2, X_p2, b2, tol=1e-7)
    assert out["ok"], out.get("reason") or out.get("verify")
    Gp = out["G_prime"]
    assert Gp.number_of_nodes() == G.number_of_nodes()
    assert Gp.number_of_edges() == G.number_of_edges()
    assert all(deg == 3 for _, deg in Gp.degree())
    assert out["verify"]["max_vertex_residual"] < 1e-7
    # R should be (approximately) the identity for a self-splice
    R = out["rotation_R"]
    assert np.isclose(np.linalg.det(R), 1.0, atol=1e-10)
