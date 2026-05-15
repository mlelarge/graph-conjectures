"""Regression tests for inverse gadget operations and the decomposition
tree DP.
"""
from __future__ import annotations

import pytest

import networkx as nx

from dot_product import dot_product
from gadget_decompose import (
    canonical_graph6,
    contract_triangle,
    decompose_step,
    decompose_tree,
    find_contractible_triangles,
    find_cyclic_3_cuts,
    graph6_of,
    split_at_3_cut,
)
from graphs import (
    blanusa_first,
    blanusa_second,
    flower_snark,
    petersen,
)
from triangle_blowup import triangle_blowup


# ---------------------------------------------------------------------------
# Canonical graph6 (nauty)
# ---------------------------------------------------------------------------


def test_canonical_graph6_is_isomorphism_invariant():
    """A relabelling of $G$ must give the same canonical graph6."""
    G = petersen()
    perm = list(G.nodes())
    perm.reverse()
    H = nx.relabel_nodes(G, {old: new for old, new in zip(G.nodes(), perm)})
    assert canonical_graph6(G) == canonical_graph6(H)


def test_canonical_graph6_distinguishes_non_isomorphic():
    assert canonical_graph6(petersen()) != canonical_graph6(blanusa_first())
    assert canonical_graph6(petersen()) != canonical_graph6(flower_snark(2))
    assert canonical_graph6(blanusa_first()) != canonical_graph6(blanusa_second())


# ---------------------------------------------------------------------------
# Inverse triangle reduction
# ---------------------------------------------------------------------------


def test_petersen_has_no_triangles():
    """Petersen is triangle-free (girth 5)."""
    assert find_contractible_triangles(petersen()) == []


def test_triangle_blowup_creates_exactly_one_contractible_triangle():
    """Triangle blow-up adds one triangle; it must be the only
    contractible one."""
    G_blown, _, _, _ = triangle_blowup(petersen(), 0)
    tris = find_contractible_triangles(G_blown)
    assert len(tris) == 1


def test_contract_triangle_recovers_original():
    """Blow up Petersen at every vertex; contracting recovers Petersen
    (up to isomorphism)."""
    P_g6 = canonical_graph6(petersen())
    for v in range(petersen().number_of_nodes()):
        G_blown, _, _, _ = triangle_blowup(petersen(), v)
        tris = find_contractible_triangles(G_blown)
        assert tris, f"no contractible triangle after blow-up at v={v}"
        G_red, _ = contract_triangle(G_blown, tris[0])
        assert canonical_graph6(G_red) == P_g6, (
            f"blow-up at v={v} then contract did not recover Petersen"
        )


# ---------------------------------------------------------------------------
# Inverse cyclic 3-edge cut (dot product)
# ---------------------------------------------------------------------------


def test_petersen_has_no_cyclic_3_cuts():
    """Petersen is cyclically 5-edge-connected."""
    assert find_cyclic_3_cuts(petersen()) == []


def test_dot_product_creates_cyclic_3_cut():
    G_dot, _, _, _ = dot_product(petersen(), 0, petersen(), 0, perm=(0, 1, 2))
    cuts = find_cyclic_3_cuts(G_dot, max_cuts=1)
    assert len(cuts) >= 1


def test_split_at_3_cut_recovers_pieces():
    """Dot-product Petersen . Blanusa-1, then split at the 3-cut, must
    recover the two original pieces up to isomorphism."""
    P_g6 = canonical_graph6(petersen())
    B_g6 = canonical_graph6(blanusa_first())
    G_dot, _, _, _ = dot_product(petersen(), 0, blanusa_first(), 0, perm=(0, 1, 2))
    cuts = find_cyclic_3_cuts(G_dot, max_cuts=1)
    assert cuts
    G_a, G_b = split_at_3_cut(G_dot, cuts[0])
    ga, gb = canonical_graph6(G_a), canonical_graph6(G_b)
    assert {ga, gb} == {P_g6, B_g6}


# ---------------------------------------------------------------------------
# decompose_step + decompose_tree
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def base_set():
    return frozenset(
        {
            canonical_graph6(petersen()),
            canonical_graph6(blanusa_first()),
            canonical_graph6(blanusa_second()),
            canonical_graph6(flower_snark(2)),
        }
    )


def test_decompose_tree_base_case(base_set):
    """Any graph in the base must give a depth-0 BASE tree."""
    P = petersen()
    tree = decompose_tree(P, base_set)
    assert tree is not None
    assert tree.op == "BASE"
    assert tree.depth() == 0
    assert tree.leaves() == [canonical_graph6(P)]


def test_decompose_tree_returns_none_on_unreachable():
    """A graph that is irreducible and not in the base returns None."""
    # Blanuša-2 is irreducible (nontrivial snark) and not in this base.
    base = frozenset({canonical_graph6(petersen())})
    assert decompose_tree(blanusa_second(), base) is None


def test_decompose_tree_finds_single_blowup(base_set):
    G_blown, _, _, _ = triangle_blowup(petersen(), 0)
    tree = decompose_tree(G_blown, base_set)
    assert tree is not None
    assert tree.op == "TRIANGLE"
    assert tree.depth() == 1
    assert tree.leaves() == [canonical_graph6(petersen())]


def test_decompose_tree_finds_single_dot_product(base_set):
    G_dot, _, _, _ = dot_product(
        petersen(), 0, blanusa_first(), 0, perm=(0, 1, 2)
    )
    tree = decompose_tree(G_dot, base_set)
    assert tree is not None
    assert tree.op == "DOT"
    assert tree.depth() == 1
    assert sorted(tree.leaves()) == sorted(
        [canonical_graph6(petersen()), canonical_graph6(blanusa_first())]
    )


def test_decompose_tree_finds_multi_step_dot_product(base_set):
    G1, _, _, _ = dot_product(petersen(), 0, petersen(), 0, perm=(0, 1, 2))
    G2, _, _, _ = dot_product(G1, 0, blanusa_first(), 0, perm=(0, 1, 2))
    tree = decompose_tree(G2, base_set, max_depth=8)
    assert tree is not None
    assert tree.depth() >= 2
    leaves = tree.leaves()
    assert all(leaf in base_set for leaf in leaves)
    # Three pieces in total.
    assert len(leaves) == 3
    assert leaves.count(canonical_graph6(petersen())) == 2
    assert leaves.count(canonical_graph6(blanusa_first())) == 1


def test_decompose_tree_finds_mixed_blowup_and_dot(base_set):
    """Blow up a dot-product graph; the decomposition tree must mix
    TRIANGLE and DOT operations."""
    G_dot, _, _, _ = dot_product(petersen(), 0, blanusa_first(), 0, perm=(0, 1, 2))
    G_mixed, _, _, _ = triangle_blowup(G_dot, 0)
    tree = decompose_tree(G_mixed, base_set, max_depth=8)
    assert tree is not None
    # The top operation must be TRIANGLE (the most recent op);
    # somewhere below must be a DOT.
    assert tree.op == "TRIANGLE"
    leaves = tree.leaves()
    assert all(leaf in base_set for leaf in leaves)
    # We expect Petersen + Blanusa-1.
    assert canonical_graph6(petersen()) in leaves
    assert canonical_graph6(blanusa_first()) in leaves
