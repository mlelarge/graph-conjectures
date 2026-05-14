r"""4-edge-cut splice: cubic-graph surgery preserving $S^2$-flow.

Setup. Let $G$ be cubic and $C \subset E(G)$ a cyclic 4-edge cut
separating $G$ into components $G_1, G_2$, each containing a cycle.
Each cut edge has one endpoint in $G_1$ (a "boundary vertex"
$b_i^{(1)}$) and one in $G_2$ ($b_i^{(2)}$). In $G_1$ (resp. $G_2$),
the boundary vertices have degree 2; all other vertices have degree 3.
We call such graphs *4-bordered cubic pieces*.

Splice. Given two 4-bordered cubic pieces $G_1, G_2$ and a bijection
$\mu : \mathrm{boundary}(G_1) \to \mathrm{boundary}(G_2)$, the splice
$G_1 \oplus_4^\mu G_2$ adds 4 edges $b_i^{(1)} b_{\mu(i)}^{(2)}$. The
result is cubic.

Flow. Suppose $G_1$ carries a (partial) $S^2$-flow $\varphi_1$
satisfying Kirchhoff at every *internal* vertex of $G_1$ (the
boundary vertices are degree 2, so their Kirchhoff equation has a
deficit: the sum of the two incident internal flow values is *not*
necessarily zero; it equals minus the cut-edge value that closes the
deficit). Define the *boundary 4-tuple*

  $T_1 = (t_1, t_2, t_3, t_4)$ with $t_i = -(\text{internal sum at } b_i^{(1)})$,

so that $t_i$ is exactly the value of the cut edge incident to
$b_i^{(1)}$ in the original $G$. The boundary 4-tuple sums to zero by
global Kirchhoff over $G_1$.

For the splice to admit an $S^2$-flow:

  $T_1 = T_2 \circ \mu^{-1}$  (under matching $\mu$).

Practically the second flow can be pre-rotated by some
$R \in \mathrm{SO}(3)$ before matching. The new through-edge values are
the matched $t_i$'s, and Kirchhoff is satisfied at every vertex by
construction.

This module implements:

  - ``find_cyclic_4_cuts(G, max_cuts)``: enumerate cyclic 4-edge cuts.
  - ``cut_at_4(G, cut)``: return the two 4-bordered pieces and the
    boundary correspondence.
  - ``boundary_4tuple(G_piece, witness, boundary_vertices)``: compute the
    boundary 4-tuple given a flow on the piece.
  - ``align_4tuples(T2, T1, max_tol)``: search for ``(R, perm)`` with
    ``R @ T2[perm[i]] == T1[i]``.
  - ``splice4_witness(G1, w1, b1, G2, w2, b2, matching=None)``: glue
    two pieces, rotate, and verify.

The cyclic 4-cut finder is $O(\binom{m}{4} \cdot (n + m))$ — feasible
for graphs up to $\sim 50$ edges (Petersen, Blanu\v{s}a, $J_5$, $J_7$).
"""
from __future__ import annotations

import itertools

import networkx as nx
import numpy as np

from graphs import _canonicalize
from witness import orient, verify_witness


# ---------------------------------------------------------------------------
# Cyclic 4-edge cut finder
# ---------------------------------------------------------------------------


def _has_cycle(G_sub: nx.Graph, nodes: set) -> bool:
    """Does the induced subgraph on ``nodes`` contain a cycle?"""
    v = len(nodes)
    e = sum(1 for u, w in G_sub.edges() if u in nodes and w in nodes)
    # In a connected component, |E| >= |V| iff a cycle exists.
    return e >= v


def find_cyclic_4_cuts(G: nx.Graph, *, max_cuts: int | None = None) -> list[tuple]:
    """Return cyclic 4-edge cuts of G as tuples of frozensets of edges.

    Brute enumeration: for each 4-edge subset, remove them, check that
    the residue has at least 2 components each containing a cycle.
    """
    edges = [tuple(sorted(e)) for e in G.edges()]
    m = len(edges)
    found: list[tuple] = []
    for cut in itertools.combinations(range(m), 4):
        removed = {edges[i] for i in cut}
        H = G.copy()
        H.remove_edges_from(removed)
        if nx.is_connected(H):
            continue
        comps = [set(c) for c in nx.connected_components(H)]
        cyclic = [c for c in comps if _has_cycle(H, c)]
        if len(cyclic) >= 2:
            found.append(tuple(frozenset(e) for e in removed))
            if max_cuts is not None and len(found) >= max_cuts:
                break
    return found


# ---------------------------------------------------------------------------
# Cut into pieces
# ---------------------------------------------------------------------------


def cut_at_4(G: nx.Graph, cut: tuple) -> dict:
    """Cut G along the given 4-edge cut and return the two pieces with
    boundary metadata.

    Returns a dict::

      {
        "piece_1": nx.Graph,      # canonicalised, 4 deg-2 vertices
        "piece_2": nx.Graph,
        "map_1": dict,            # old G-label -> piece_1 label (only for piece_1 vertices)
        "map_2": dict,
        "boundary_1": list[int],  # 4 vertices in piece_1 (deg 2), in cut-edge order
        "boundary_2": list[int],  # 4 vertices in piece_2, in cut-edge order
        "cut_edges_canonical": list[tuple]  # the 4 edges of the cut, sorted tuple
      }

    The order of cut edges is the sorted order on canonical (u, v) tuples
    with u < v. ``boundary_1[i]`` and ``boundary_2[i]`` are the two
    endpoints of the i-th cut edge in piece_1 / piece_2 respectively.
    """
    cut_edges_canonical = sorted(tuple(sorted(e)) for e in (tuple(c) for c in cut))
    H = G.copy()
    H.remove_edges_from(cut_edges_canonical)
    comps = list(nx.connected_components(H))
    if len(comps) < 2:
        raise ValueError("cut does not disconnect G")
    if len(comps) > 2:
        # Could be 3 or 4 components; for a *cyclic* 4-cut we expect 2.
        raise ValueError(f"cut produces {len(comps)} components; expected 2")

    # Identify which component each cut-edge endpoint belongs to.
    comp_of = {v: 0 if v in comps[0] else 1 for v in G.nodes()}

    nodes_1 = set(comps[0])
    nodes_2 = set(comps[1])

    G1_lab = nx.Graph()
    G1_lab.add_nodes_from(nodes_1)
    for u, w in H.edges():
        if u in nodes_1 and w in nodes_1:
            G1_lab.add_edge(u, w)
    G2_lab = nx.Graph()
    G2_lab.add_nodes_from(nodes_2)
    for u, w in H.edges():
        if u in nodes_2 and w in nodes_2:
            G2_lab.add_edge(u, w)

    boundary_1_old: list = []
    boundary_2_old: list = []
    for (a, b) in cut_edges_canonical:
        # a, b is the canonical (sorted) edge. Determine which is in which piece.
        if comp_of[a] == 0:
            boundary_1_old.append(a)
            boundary_2_old.append(b)
        else:
            boundary_1_old.append(b)
            boundary_2_old.append(a)

    piece_1 = _canonicalize(G1_lab)
    piece_2 = _canonicalize(G2_lab)

    sorted_1 = sorted(nodes_1)
    sorted_2 = sorted(nodes_2)
    relabel_1 = {n_: i for i, n_ in enumerate(sorted_1)}
    relabel_2 = {n_: i for i, n_ in enumerate(sorted_2)}

    return {
        "piece_1": piece_1,
        "piece_2": piece_2,
        "map_1": relabel_1,
        "map_2": relabel_2,
        "boundary_1": [relabel_1[v] for v in boundary_1_old],
        "boundary_2": [relabel_2[v] for v in boundary_2_old],
        "cut_edges_canonical": cut_edges_canonical,
    }


# ---------------------------------------------------------------------------
# Boundary 4-tuple
# ---------------------------------------------------------------------------


def boundary_4tuple(
    G_piece: nx.Graph,
    witness: list[list[float]] | np.ndarray,
    boundary_vertices: list[int],
) -> np.ndarray:
    """Return the boundary 4-tuple at the four degree-2 vertices.

    For each boundary vertex ``b``, the internal Kirchhoff sum is the
    signed sum of its two incident edges. The "missing" cut-edge value
    equals minus that sum (so that with the cut edge present, Kirchhoff
    holds).
    """
    X = np.asarray(witness, dtype=np.float64)
    edges, sign = orient(G_piece)
    edge_index = {tuple(e): k for k, e in enumerate(edges)}

    T = np.zeros((4, 3), dtype=np.float64)
    for i, b in enumerate(boundary_vertices):
        s = np.zeros(3, dtype=np.float64)
        for k, sigma in sign[b]:
            s += sigma * X[k]
        # internal sum at b is s; cut-edge "incoming at b" carries -s
        # (so that s + (cut edge contribution) = 0); the cut-edge value
        # oriented "outgoing from b" (away from the piece) is -s.
        T[i] = -s
    return T


# ---------------------------------------------------------------------------
# 4-tuple alignment
# ---------------------------------------------------------------------------


def _procrustes_so3(A: np.ndarray, B: np.ndarray) -> tuple[np.ndarray, float]:
    """Kabsch: minimise ||R A - B||_F over R in SO(3)."""
    M = B @ A.T
    U, _, Vt = np.linalg.svd(M)
    d = np.sign(np.linalg.det(U @ Vt))
    D = np.diag([1.0, 1.0, d if d != 0 else 1.0])
    R = U @ D @ Vt
    return R, float(np.linalg.norm(R @ A - B))


def align_4tuples(
    T2: np.ndarray, T1: np.ndarray, *, tol: float = 1e-8
) -> tuple[np.ndarray, tuple[int, int, int, int]] | None:
    """Find ``(R, perm)`` with ``R @ T2[perm[i]] == -T1[i]``, both viewed
    as 4-by-3 matrices of unit vectors summing to zero.

    The negation convention is the splice analogue of ``align_to_negation``
    in :mod:`dot_product`: the cut-edge value as seen "out of $b_i^{(1)}$"
    is $T_1[i]$, but "out of $b_{\\pi(i)}^{(2)}$" (the matched endpoint in
    piece 2) it is $-T_1[i]$. Since $T_2[\\pi(i)]$ is the value oriented
    out of the same boundary vertex of piece 2, after rotating piece 2's
    flow by $R$ we need $R\\,T_2[\\pi(i)] = -T_1[i]$.

    Tries all 24 permutations; returns the first whose Kabsch residual
    is below ``tol``. Returns ``None`` if no alignment works (the two
    4-tuples are not SO(3)-equivalent up to negation under any
    permutation -- common, since the moduli space of 4 unit vectors
    summing to 0 in R^3 has dimension 5).
    """
    A = T2.T            # 3 x 4
    B = (-T1).T         # 3 x 4 (target = -T1)
    for perm in itertools.permutations(range(4)):
        A_perm = A[:, list(perm)]
        R, res = _procrustes_so3(A_perm, B)
        if res < tol:
            return R, perm
    return None


# ---------------------------------------------------------------------------
# Splice
# ---------------------------------------------------------------------------


def splice4_witness(
    piece_1: nx.Graph,
    witness_1: list[list[float]] | np.ndarray,
    boundary_1: list[int],
    piece_2: nx.Graph,
    witness_2: list[list[float]] | np.ndarray,
    boundary_2: list[int],
    *,
    matching: tuple[int, int, int, int] | None = None,
    tol: float = 1e-7,
) -> dict:
    """Splice ``piece_1`` and ``piece_2`` along their 4-boundaries.

    The 4 new through-edges connect ``boundary_1[i]`` to
    ``boundary_2[matching[i]]`` (default: identity matching after
    automatic 4-tuple alignment).

    Returns a dict with the spliced graph, the assembled flow, and the
    verify result.
    """
    T1 = boundary_4tuple(piece_1, witness_1, boundary_1)
    T2 = boundary_4tuple(piece_2, witness_2, boundary_2)

    if matching is None:
        aligned = align_4tuples(T2, T1, tol=tol)
        if aligned is None:
            return {
                "ok": False,
                "reason": "no SO(3) rotation aligns T2[perm] to -T1 under any permutation",
                "T1": T1, "T2": T2,
            }
        R, perm = aligned
    else:
        perm = matching
        A_perm = T2[list(perm)].T
        R, _ = _procrustes_so3(A_perm, (-T1).T)

    # Rotate piece_2's witness
    X2 = np.asarray(witness_2, dtype=np.float64)
    X2_rot = X2 @ R.T

    # Build the spliced graph: relabel piece_2 vertices to avoid clashing with piece_1.
    n1 = piece_1.number_of_nodes()
    G_lab = nx.Graph()
    G_lab.add_nodes_from(piece_1.nodes())
    G_lab.add_edges_from(piece_1.edges())
    # Shift piece_2 labels by n1
    G_lab.add_nodes_from(v + n1 for v in piece_2.nodes())
    G_lab.add_edges_from((u + n1, w + n1) for u, w in piece_2.edges())
    # Add 4 through-edges
    through_lab: list[tuple] = []
    for i, b1 in enumerate(boundary_1):
        b2 = boundary_2[perm[i]] + n1
        G_lab.add_edge(b1, b2)
        through_lab.append((b1, b2))

    G_prime = _canonicalize(G_lab)
    sorted_nodes = sorted(G_lab.nodes())
    relabel = {n_: i for i, n_ in enumerate(sorted_nodes)}

    edges_prime, _ = orient(G_prime)
    edge_index_prime = {tuple(e): k for k, e in enumerate(edges_prime)}
    X_prime = np.zeros((len(edges_prime), 3), dtype=np.float64)

    # Copy piece_1 edges
    edges_p1, _ = orient(piece_1)
    edge_index_p1 = {tuple(e): k for k, e in enumerate(edges_p1)}
    for (u, w) in edges_p1:
        u2, w2 = relabel[u], relabel[w]
        a, b = (u2, w2) if u2 < w2 else (w2, u2)
        X_prime[edge_index_prime[(a, b)]] = np.asarray(witness_1)[edge_index_p1[(u, w)]]

    # Copy piece_2 edges (with rotated witness)
    edges_p2, _ = orient(piece_2)
    edge_index_p2 = {tuple(e): k for k, e in enumerate(edges_p2)}
    for (u, w) in edges_p2:
        u_shift, w_shift = u + n1, w + n1
        u2, w2 = relabel[u_shift], relabel[w_shift]
        a, b = (u2, w2) if u2 < w2 else (w2, u2)
        X_prime[edge_index_prime[(a, b)]] = X2_rot[edge_index_p2[(u, w)]]

    # Add through-edge values: through edge i carries T1[i] (= rotated T2[perm[i]])
    # oriented "out of boundary_1[i]" (i.e., from piece_1 side to piece_2 side).
    for i, (b1, b2_shift) in enumerate(through_lab):
        u2, w2 = relabel[b1], relabel[b2_shift]
        a, b = (u2, w2) if u2 < w2 else (w2, u2)
        value_out_of_b1 = T1[i]
        if (a, b) == (u2, w2):
            X_prime[edge_index_prime[(a, b)]] = value_out_of_b1
        else:
            X_prime[edge_index_prime[(a, b)]] = -value_out_of_b1

    check = verify_witness(G_prime, edges_prime, X_prime.tolist(), tol=tol)
    return {
        "ok": check["ok"],
        "G_prime": G_prime,
        "edges_prime": edges_prime,
        "vectors_prime": X_prime,
        "verify": check,
        "rotation_R": R,
        "permutation": perm,
        "T1": T1, "T2": T2,
        "T2_after_rotation": (R @ T2.T).T,
    }
