r"""Dot product (Y--Y / 3-edge-cut surgery) of two cubic graphs, with
$S^2$-flow extension.

Operation. Pick $v_1 \in G_1$, $v_2 \in G_2$, both cubic. Remove
$v_1, v_2$. Pair up the six dangling half-edges into three new edges
across the cut via a fixed permutation
$\pi : \{u_1, u_2, u_3\} \to \{w_1, w_2, w_3\}$, where $u_i$ are
$v_1$'s neighbours (sorted) and $w_j$ are $v_2$'s. Result $G$ is cubic
on $|V_1| + |V_2| - 2$ vertices and $|E_1| + |E_2| - 3$ edges.

Flow compatibility. With the convention "spoke value is outgoing from
$v_1$" and analogously from $v_2$, the through-edge $u_i \to w_{\pi(i)}$
carries value $-f_i$ where $f_i = \varphi_1(v_1 u_i)$ (sign on $\varphi_1$
oriented out of $v_1$). At $w_{\pi(i)}$ Kirchhoff then forces
$g_{\pi(i)} = -f_i$, i.e.,

$$
(g_{\pi(1)}, g_{\pi(2)}, g_{\pi(3)}) \;=\; (-f_1, -f_2, -f_3).
$$

Since both triples sum to zero and form a 120-degree equilateral
triangle on a great circle in $\mathbb R^3$, an $R \in \mathrm{SO}(3)$
realising this equality exists for the correct chirality and
permutation. We rotate $G_2$'s witness by such an $R$, then assemble.

This module provides:

  - ``dot_product(G1, v1, G2, v2, perm)`` -> combined graph + maps
  - ``boundary_triple(G, witness, v)`` -> three unit vectors out of $v$
  - ``align_to_negation(triple_2, triple_1)`` -> ``(R, perm)`` such that
    ``R @ triple_2[perm[i]] == -triple_1[i]``, or ``None`` if no
    alignment works.
  - ``dot_product_witness(G1, w1, v1, G2, w2, v2, perm=None)`` -- glue,
    rotate, verify.
"""
from __future__ import annotations

import itertools
import numpy as np
import networkx as nx

from graphs import _canonicalize
from witness import orient, verify_witness


def dot_product(
    G1: nx.Graph, v1: int, G2: nx.Graph, v2: int, perm: tuple[int, int, int]
) -> tuple[nx.Graph, dict, dict, list[tuple]]:
    """Construct the dot product $G_1 \\oplus_\\pi G_2$.

    Returns ``(G_prime, map_G1, map_G2, through_edges)``:

      - ``G_prime``: canonicalised cubic graph
      - ``map_G1``: dict from each non-v1 G1-vertex to its G_prime label
      - ``map_G2``: dict from each non-v2 G2-vertex to its G_prime label
      - ``through_edges``: list of 3 tuples (a, b) (G_prime labels)
        corresponding to ``u_i -- w_{perm(i)}``, in i = 0, 1, 2 order

    Raises ``ValueError`` for non-cubic vertices or bad permutation.
    """
    if G1.degree(v1) != 3 or G2.degree(v2) != 3:
        raise ValueError("v1, v2 must have degree 3")
    if sorted(perm) != [0, 1, 2]:
        raise ValueError("perm must be a permutation of (0, 1, 2)")

    u_list = sorted(G1.neighbors(v1))
    w_list = sorted(G2.neighbors(v2))

    G_lab = nx.Graph()
    # G1 part: keep original labels, drop v1
    for u in G1.nodes():
        if u != v1:
            G_lab.add_node(("g1", u))
    for u, w in G1.edges():
        if u == v1 or w == v1:
            continue
        G_lab.add_edge(("g1", u), ("g1", w))
    # G2 part: tag with "g2", drop v2
    for u in G2.nodes():
        if u != v2:
            G_lab.add_node(("g2", u))
    for u, w in G2.edges():
        if u == v2 or w == v2:
            continue
        G_lab.add_edge(("g2", u), ("g2", w))
    # Through edges
    through_lab: list[tuple] = []
    for i, u_i in enumerate(u_list):
        w_j = w_list[perm[i]]
        G_lab.add_edge(("g1", u_i), ("g2", w_j))
        through_lab.append((("g1", u_i), ("g2", w_j)))

    G_prime = _canonicalize(G_lab)

    sorted_nodes = sorted(G_lab.nodes())
    relabel = {n_: i for i, n_ in enumerate(sorted_nodes)}

    map_G1 = {u: relabel[("g1", u)] for u in G1.nodes() if u != v1}
    map_G2 = {u: relabel[("g2", u)] for u in G2.nodes() if u != v2}

    through_edges: list[tuple] = []
    for (a, b) in through_lab:
        ra, rb = relabel[a], relabel[b]
        through_edges.append((ra, rb) if ra < rb else (rb, ra))

    return G_prime, map_G1, map_G2, through_edges


def boundary_triple(
    G: nx.Graph, witness: list[list[float]] | np.ndarray, v: int
) -> tuple[list[int], np.ndarray]:
    """Return ``(neighbours, triple)`` where ``triple[i]`` is the
    "out-of-v" flow value on the spoke ``(v, neighbours[i])``.

    The neighbours are in sorted (canonical) order. Each ``triple[i]`` is
    a unit 3-vector; their sum is zero (modulo numerical noise) by
    Kirchhoff at v.
    """
    X = np.asarray(witness, dtype=np.float64)
    edges, _ = orient(G)
    edge_index = {tuple(e): k for k, e in enumerate(edges)}
    neighbours = sorted(G.neighbors(v))
    triple = np.zeros((3, 3), dtype=np.float64)
    for i, u in enumerate(neighbours):
        a, b = (v, u) if v < u else (u, v)
        sig = +1.0 if v < u else -1.0
        triple[i] = sig * X[edge_index[(a, b)]]
    return neighbours, triple


def _procrustes_so3(A: np.ndarray, B: np.ndarray) -> tuple[np.ndarray, float]:
    """Solve min_{R in SO(3)} ||R A - B||_F via Kabsch.

    A, B are 3-by-k matrices (column = vector). Returns (R, residual).
    """
    M = B @ A.T
    U, _, Vt = np.linalg.svd(M)
    d = np.sign(np.linalg.det(U @ Vt))
    D = np.diag([1.0, 1.0, d if d != 0 else 1.0])
    R = U @ D @ Vt
    res = float(np.linalg.norm(R @ A - B))
    return R, res


def align_to_negation(
    triple_2: np.ndarray, triple_1: np.ndarray, *, tol: float = 1e-8
) -> tuple[np.ndarray, tuple[int, int, int]] | None:
    """Find ``(R, perm)`` with ``R @ triple_2[perm[i]] == -triple_1[i]``.

    Tries all 6 permutations of (0, 1, 2); for each, computes the
    best-fit SO(3) rotation via Kabsch and accepts the first whose
    residual is below ``tol``. Returns ``None`` if none qualifies (this
    happens when the two triples have opposite chirality, in which case
    no orientation-preserving rotation works).
    """
    f = np.asarray(triple_1, dtype=np.float64).T  # 3-by-3 column matrix
    g = np.asarray(triple_2, dtype=np.float64).T
    target = -f
    for perm in itertools.permutations((0, 1, 2)):
        g_perm = g[:, list(perm)]
        R, res = _procrustes_so3(g_perm, target)
        if res < tol:
            return R, perm
    return None


def iterated_dot_product(
    base_graph: nx.Graph,
    base_witness: list[list[float]] | np.ndarray,
    steps: list[tuple],
    *,
    tol: float = 1e-7,
) -> dict:
    """Chain together a sequence of dot-product gluings.

    Starts with ``(base_graph, base_witness)`` and, for each step
    ``(v_left, G_right, witness_right, v_right)``, replaces the current
    pair with the result of ``dot_product_witness``, glued at
    ``v_left`` in the running graph and ``v_right`` in ``G_right``.

    Returns the final graph + witness + per-step verify status.
    Stops early (with ``ok=False``) if any intermediate step fails to
    align/verify.
    """
    G_cur = base_graph
    X_cur = np.asarray(base_witness, dtype=np.float64)
    history: list[dict] = []
    for i, step in enumerate(steps):
        v_left, G_right, X_right, v_right = step
        out = dot_product_witness(G_cur, X_cur, v_left, G_right, X_right, v_right, tol=tol)
        history.append({
            "step": i,
            "ok": out["ok"],
            "permutation": out.get("permutation"),
            "G_prime_size": (out["G_prime"].number_of_nodes(), out["G_prime"].number_of_edges()) if out.get("ok") else None,
            "max_residual": out["verify"]["max_vertex_residual"] if out.get("ok") else None,
            "reason": out.get("reason"),
        })
        if not out["ok"]:
            return {"ok": False, "history": history, "G_final": G_cur, "vectors_final": X_cur, "failed_at_step": i}
        G_cur = out["G_prime"]
        X_cur = out["vectors_prime"]
    return {
        "ok": True,
        "history": history,
        "G_final": G_cur,
        "vectors_final": X_cur,
    }


def dot_product_witness(
    G1: nx.Graph,
    witness1: list[list[float]] | np.ndarray,
    v1: int,
    G2: nx.Graph,
    witness2: list[list[float]] | np.ndarray,
    v2: int,
    *,
    perm: tuple[int, int, int] | None = None,
    tol: float = 1e-7,
) -> dict:
    """Glue G1 and G2 at v1, v2 (with through-edge permutation perm) and
    return the combined S^2-flow built from the two input witnesses.

    If ``perm`` is None, both perm and the SO(3) rotation on G2's
    witness are computed by ``align_to_negation``. If ``perm`` is given,
    only the rotation is computed (and the boundary triples must be
    compatible under that perm; otherwise the result will not verify).

    Returns a dict with G_prime, the assembled flow, the verify
    result, and the chosen rotation + permutation.
    """
    X1 = np.asarray(witness1, dtype=np.float64)
    X2 = np.asarray(witness2, dtype=np.float64)

    u_list, triple_1 = boundary_triple(G1, X1, v1)
    w_list, triple_2 = boundary_triple(G2, X2, v2)

    if perm is None:
        aligned = align_to_negation(triple_2, triple_1, tol=tol)
        if aligned is None:
            return {
                "ok": False,
                "reason": "no SO(3) rotation aligns triple_2 to -triple_1 under any permutation; "
                          "the two boundary triples have incompatible chirality.",
                "triple_1": triple_1,
                "triple_2": triple_2,
            }
        R, perm = aligned
    else:
        # Compute R to align under the given perm.
        g_perm = triple_2[list(perm)].T
        target = -triple_1.T
        R, _ = _procrustes_so3(g_perm, target)

    # Rotate G2's entire witness by R.
    X2_rot = X2 @ R.T

    G_prime, map_G1, map_G2, through_edges = dot_product(G1, v1, G2, v2, perm)
    edges_prime, _ = orient(G_prime)
    edge_index_prime = {tuple(e): k for k, e in enumerate(edges_prime)}
    X_prime = np.zeros((len(edges_prime), 3), dtype=np.float64)

    # Copy G1 edges (excluding v1's spokes)
    edges_G1, _ = orient(G1)
    edge_index_G1 = {tuple(e): k for k, e in enumerate(edges_G1)}
    for e in edges_G1:
        u, w = e
        if u == v1 or w == v1:
            continue
        u2, w2 = map_G1[u], map_G1[w]
        a, b = (u2, w2) if u2 < w2 else (w2, u2)
        # Both canonical orientations preserve sign because map_G1 is monotone-preserving
        X_prime[edge_index_prime[(a, b)]] = X1[edge_index_G1[(u, w)]]

    # Copy G2 edges (excluding v2's spokes), using rotated witness
    edges_G2, _ = orient(G2)
    edge_index_G2 = {tuple(e): k for k, e in enumerate(edges_G2)}
    for e in edges_G2:
        u, w = e
        if u == v2 or w == v2:
            continue
        u2, w2 = map_G2[u], map_G2[w]
        a, b = (u2, w2) if u2 < w2 else (w2, u2)
        X_prime[edge_index_prime[(a, b)]] = X2_rot[edge_index_G2[(u, w)]]

    # Through edges: by construction, through_edges[i] = (u_i mapped, w_{perm(i)} mapped),
    # and the value is -triple_1[i] = R @ triple_2[perm[i]]
    # In canonical orientation (a, b) with a < b: if a == map_G1[u_i] (the u-side is
    # smaller), sign +1 means "out of u_i" which equals -triple_1[i]. If a == map_G2[w]
    # (the w-side is smaller), we'd be writing the value as "out of w_{perm(i)}", which
    # is +triple_1[i] (the negation of -triple_1[i] from u_i's side).
    for i, u_i in enumerate(u_list):
        w_j = w_list[perm[i]]
        side_u = map_G1[u_i]
        side_w = map_G2[w_j]
        value_out_of_u = -triple_1[i]  # what the through edge carries when oriented u_i -> w_j
        a, b = (side_u, side_w) if side_u < side_w else (side_w, side_u)
        if (a, b) == (side_u, side_w):
            # canonical orientation matches "u -> w", so value is +value_out_of_u
            X_prime[edge_index_prime[(a, b)]] = value_out_of_u
        else:
            # canonical orientation is "w -> u", so value flips
            X_prime[edge_index_prime[(a, b)]] = -value_out_of_u

    check = verify_witness(G_prime, edges_prime, X_prime.tolist(), tol=tol)
    return {
        "ok": check["ok"],
        "G_prime": G_prime,
        "edges_prime": edges_prime,
        "vectors_prime": X_prime,
        "verify": check,
        "rotation_R": R,
        "permutation": perm,
        "boundary_triple_1": triple_1,
        "boundary_triple_2": triple_2,
        "boundary_triple_2_after_rotation": (R @ triple_2.T).T,
    }
