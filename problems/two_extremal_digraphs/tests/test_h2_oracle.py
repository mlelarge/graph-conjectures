#!/usr/bin/env python3
"""
SOUNDNESS tests for the H_2 recognizer (scripts/h2_oracle.py).

Every constructively generated genuine H_2 member MUST recognize as in-H_2:
  * symmetric odd cycles  sym C_3, C_5, C_7
  * generalised wheels    W_3, W_4, W_5   (2-Hajos tree join, EMPTY A)
  * a directed Hajos join C_3 # C_3
  * a genuine NON-EMPTY-A 2-Hajos tree join built by hand (n=9, four sym-C_3
    A-blocks on a 2-internal-vertex plane tree)

Obvious non-members MUST recognize as not-in-H_2:
  * sym C_4 (even cycle: chi_vec = 2, not even 2-extremal)
  * a directed 3-cycle (no digons; chi_vec = 1)

We additionally cross-check every member is 2-extremal (H_2 subset 2-extremal),
and that the hand-built non-empty-A example is recognised SPECIFICALLY through
the tree-join branch (the directed-Hajos inverse yields no decomposition).
"""

import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.join(os.path.dirname(HERE), "scripts")
sys.path.insert(0, SCRIPTS)

import h2_oracle as H  # noqa: E402


# --------------------------------------------------------------------------
# Constructors for known H_2 members
# --------------------------------------------------------------------------

def directed_wheel(m):
    """Generalised wheel W_m: hub `m`, rim directed cycle 0->..->m-1->0, and a
    digon hub<->r for every rim vertex.  This is a 2-Hajos tree join with A=empty
    (star tree, all B-edges, every leaf-leaf path uses 2 B-edges = even)."""
    arcs = set()
    hub = m
    for i in range(m):
        arcs.add((i, (i + 1) % m))
        arcs.add((hub, i))
        arcs.add((i, hub))
    return m + 1, frozenset(arcs)


def hajos_C3_C3():
    """Directed Hajos join of sym C_3 with sym C_3.
    D1 = sym C3 on {0,1,2}, arc u->v1 = 0->1.
    D2 = sym C3, relabelled {0,1,2}->{3,1,4} (identify v2 with v1=1), arc v2->w=1->4.
    Delete 0->1 and 1->4, add u->w = 0->4."""
    _, a1 = H.sym_cycle(3)            # {0,1,2}
    _, a2 = H.sym_cycle(3)
    arcs = set(a1)
    arcs.discard((0, 1))              # delete u->v1
    map2 = {0: 3, 1: 1, 2: 4}         # identify D2's v2(=1) with v1(=1)
    for (x, y) in a2:
        if (x, y) == (1, 2):          # delete v2->w
            continue
        arcs.add((map2[x], map2[y]))
    arcs.add((0, map2[2]))            # add u->w = 0->4
    return 5, frozenset(arcs)


def nonempty_A_tree_join():
    """A genuine NON-EMPTY-A 2-Hajos tree join, built by hand.

    Plane tree on leaves l0=0,l1=1,l2=2 with internal vertices h0=3,h1=4:
        edges  l0-h0, l1-h0, h0-h1, l2-h1     (a caterpillar)
    Parity: all leaves and both internal vertices get parity 0, so ALL four tree
    edges are A-edges and B is empty -> every leaf-leaf path uses 0 B-edges
    (even), parity condition holds.  Each A-edge {x,y} is replaced by a sym-C_3
    block (interface digon [x,y] plus one private vertex z, with digons y-z, z-x)
    minus the interface digon.  Rim = directed cycle 0->1->2->0 on the leaves.

    Result: n=9 digraph with four sym-C_3 A-blocks (private verts 5,6,7,8)."""
    A_edges = [(0, 3), (1, 3), (3, 4), (2, 4)]
    leaf_cyc = [0, 1, 2]
    arcs = set()
    k = len(leaf_cyc)
    for i in range(k):                # peripheral directed cycle on leaves
        arcs.add((leaf_cyc[i], leaf_cyc[(i + 1) % k]))
    nxt = 5                           # private block-internal vertices start at 5
    for (x, y) in A_edges:
        z = nxt
        nxt += 1
        # sym-C_3 block on {x,y,z} = digons xy, yz, zx, with interface digon xy DELETED
        arcs.add((y, z))
        arcs.add((z, y))
        arcs.add((z, x))
        arcs.add((x, z))
    return nxt, frozenset(arcs)


def directed_triangle():
    """Plain directed 3-cycle 0->1->2->0 (no digons).  chi_vec=1; not in H_2."""
    return 3, frozenset([(0, 1), (1, 2), (2, 0)])


# --------------------------------------------------------------------------
# Members: MUST be recognised as in H_2
# --------------------------------------------------------------------------

@pytest.mark.parametrize("m", [3, 5, 7])
def test_symmetric_odd_cycle_in_H2(m):
    n, arcs = H.sym_cycle(m)
    assert H.is_2extremal(n, arcs), f"sym C{m} should be 2-extremal"
    assert H.is_in_H2(n, arcs), f"sym C{m} must be in H_2 (base object)"


@pytest.mark.parametrize("m", [3, 4, 5])
def test_generalised_wheel_in_H2(m):
    n, arcs = directed_wheel(m)
    assert H.is_2extremal(n, arcs), f"W_{m} should be 2-extremal"
    assert H.is_in_H2(n, arcs), f"W_{m} must be in H_2 (empty-A tree join)"


def test_hajos_join_C3_C3_in_H2():
    n, arcs = hajos_C3_C3()
    assert H.is_2extremal(n, arcs), "C3#C3 should be 2-extremal"
    assert H.is_in_H2(n, arcs), "C3#C3 must be in H_2 (directed Hajos join)"
    # And it is NOT itself a base symmetric odd cycle, so it genuinely exercises
    # the directed-Hajos decomposition branch.
    assert not H.is_symmetric_odd_cycle(n, arcs)


def test_nonempty_A_tree_join_in_H2():
    n, arcs = nonempty_A_tree_join()
    assert n == 9
    assert H.is_2extremal(n, arcs), "non-empty-A tree join should be 2-extremal"
    assert H.is_in_H2(n, arcs), "non-empty-A 2-Hajos tree join must be in H_2"


def test_nonempty_A_uses_tree_join_branch_not_hajos():
    """The hand-built non-empty-A example must be caught by the TREE-JOIN branch:
    the directed-Hajos inverse yields no valid decomposition for it."""
    n, arcs = nonempty_A_tree_join()
    # directed-Hajos inverse: no decomposition at all
    hajos = list(H._hajos_decompositions(n, arcs))
    assert hajos == [], "expected no directed-Hajos decomposition"
    # tree-join inverse: at least one valid decomposition into smaller H_2 blocks
    found = False
    for blocks in H._tree_join_decompositions(n, arcs, max_internal=2):
        if blocks and all(bn < n and H.is_in_H2(bn, ba) for (bn, ba) in blocks):
            found = True
            break
    assert found, "tree-join branch must produce a valid non-empty-A decomposition"


# --------------------------------------------------------------------------
# Non-members: MUST be recognised as NOT in H_2
# --------------------------------------------------------------------------

def test_sym_C4_not_in_H2():
    n, arcs = H.sym_cycle(4)
    # sym C4 is an even symmetric cycle: chi_vec = 2, so not even 2-extremal.
    assert not H.is_2extremal(n, arcs), "sym C4 has chi_vec=2, not 2-extremal"
    assert not H.is_in_H2(n, arcs), "sym C4 must NOT be in H_2"


def test_directed_triangle_not_in_H2():
    n, arcs = directed_triangle()
    assert not H.is_in_H2(n, arcs), "plain directed 3-cycle must NOT be in H_2"


def test_sym_C6_not_in_H2():
    n, arcs = H.sym_cycle(6)
    assert not H.is_in_H2(n, arcs), "sym C6 (even) must NOT be in H_2"


# --------------------------------------------------------------------------
# Cross-check against the enumerated truth sets (regression vs recon).
# --------------------------------------------------------------------------

@pytest.mark.parametrize("n", [3, 4, 5])
def test_all_enumerated_2extremal_recognised(n):
    """Every enumerated 2-extremal digraph on n<=5 vertices must be in H_2
    (the recon ground truth had zero counterexamples through n=5)."""
    from enumerate_2extremal_v0_recon import L_n
    Ln = L_n(n)
    missing = [sorted(a) for a in Ln if not H.is_in_H2(n, a)]
    assert missing == [], f"n={n}: enumerated 2-extremals not recognised: {missing}"


def test_flagged_n7_generalised_wheel_now_in_H2():
    """Regression: the n=7 generalised wheel that the oracle previously flagged
    as NOT-in-H_2 (its spanning tree has 3 internal vertices, exceeding the
    generic tree-join inverse's max_internal cap) must now recognise as in-H_2
    via the dedicated empty-A generalised-wheel recognizer.

    Structure: 6 digons forming a spanning caterpillar tree, 4 single arcs
    forming the peripheral directed cycle 0->3->1->6->0 on the tree's 4 leaves
    {0,1,3,6}; every leaf-to-leaf path has even length."""
    n = 7
    arcs = [[0, 3], [0, 4], [1, 5], [1, 6], [2, 4], [2, 5], [3, 1], [3, 5],
            [4, 0], [4, 2], [4, 6], [5, 1], [5, 2], [5, 3], [6, 0], [6, 4]]
    assert H.is_2extremal(n, arcs), "flagged n=7 object should be 2-extremal"
    assert H._is_generalised_wheel(*H._norm(n, arcs)), \
        "flagged n=7 object must be recognised as a generalised wheel"
    assert H.is_in_H2(n, arcs), \
        "flagged n=7 generalised wheel must now be in H_2"


def test_generalised_wheel_recognizer_sound_rejections():
    """The direct generalised-wheel recognizer must REJECT non-wheels."""
    # sym C_5: digons form a cycle (not a tree) -> reject.
    assert not H._is_generalised_wheel(*H.sym_cycle(5))
    # directed triangle: no digons at all -> reject.
    assert not H._is_generalised_wheel(*directed_triangle())
    # C3#C3 directed-Hajos join: not a wheel -> reject (still in H_2 via Hajos).
    assert not H._is_generalised_wheel(*H._norm(*hajos_C3_C3()))


def test_base_case_predicate_sanity():
    assert H.is_symmetric_odd_cycle(*H.sym_cycle(3))
    assert H.is_symmetric_odd_cycle(*H.sym_cycle(5))
    assert not H.is_symmetric_odd_cycle(*H.sym_cycle(4))
    assert not H.is_symmetric_odd_cycle(*directed_triangle())
