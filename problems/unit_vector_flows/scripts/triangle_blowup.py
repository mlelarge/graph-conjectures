r"""Triangle blow-up: a cubic-graph operation that preserves $S^2$-flow
existence (Houdrouge-Miraftab-Morin, arXiv:2602.21526, 2026).

Operation. Pick a cubic vertex $v$ in $G$ with neighbours $u_1, u_2, u_3$.
The blown-up graph $G'$ removes $v$, adds three new vertices
$v_1, v_2, v_3$ joined in a triangle, and re-attaches each $v_i$ to
the corresponding $u_i$. $G'$ is again cubic.

Closed-form flow extension. Suppose $G$ has an $S^2$-flow $\varphi$
with values $f_i = \varphi(v u_i) \in S^2$ at the three edges incident
to $v$, and the canonical (lex) orientation sends all three edges away
from $v$ so that Kirchhoff at $v$ reads $f_1 + f_2 + f_3 = 0$. The
blown-up flow $\varphi'$ keeps $\varphi'(v_i u_i) = f_i$ and assigns
triangle-edge values

    g_{12} = (f_2 - f_1)/3 + eps * sqrt(2/3) * n,
    g_{13} = -f_1 - g_{12},
    g_{23} = -f_2 + g_{12},

with $n = (f_3 \times (f_2 - f_1)) / \|f_3 \times (f_2 - f_1)\|$ a
unit normal to the plane spanned by $f_1, f_2, f_3$ and
$\epsilon \in \{+1, -1\}$ the chirality of the blow-up. Each $g_{ij}$
is automatically unit-length and the three Kirchhoff equations at
$v_1, v_2, v_3$ are satisfied by construction.

This file:
  - ``triangle_blowup(G, v)`` performs the graph operation and returns
    the new (canonicalised) graph plus a map from $G'$ edges back to
    $G$ edges (for the non-triangle edges) or to a flag (for the
    triangle edges).
  - ``triangle_blowup_flow(f1, f2, f3, *, chirality=+1)`` returns
    ``g12, g13, g23`` via the closed-form above.
  - ``extend_witness_through_blowup(G, witness, v, chirality=+1)``
    builds the full $S^2$-flow on $G'$ from a witness on $G$ and
    verifies it via ``witness.verify_witness``.
"""
from __future__ import annotations

import numpy as np
import networkx as nx

from graphs import _canonicalize
from witness import orient, verify_witness


def triangle_blowup(G: nx.Graph, v: int) -> tuple[nx.Graph, dict, list[tuple], list[tuple]]:
    """Return the cubic graph G' obtained by blowing v into a triangle.

    Returns ``(G_prime, vertex_map, old_to_new_spokes, triangle_edges)``:

      - ``G_prime``: canonicalised blown-up graph (nodes labelled 0..n+1)
      - ``vertex_map``: a dict from every G-vertex other than v to its
        new G_prime label (so old edge (u, w) in G with u, w != v
        becomes ``(vertex_map[u], vertex_map[w])`` in G_prime).
      - ``old_to_new_spokes[i] = ((v, u_i), (v_i, u_i))`` for the three
        edges incident to v in G and their replacements in G' (v_i, u_i
        already in G_prime's integer labels).
      - ``triangle_edges = [(v_1, v_2), (v_1, v_3), (v_2, v_3)]`` are
        the new edges added inside the triangle (G_prime labels).
    """
    if v not in G:
        raise ValueError(f"vertex {v} not in G")
    if G.degree(v) != 3:
        raise ValueError(f"vertex {v} has degree {G.degree(v)}, expected 3")

    neighbours = sorted(G.neighbors(v))  # canonical neighbour order

    # Build a labelled graph that's structurally G - v + triangle.
    # Use the existing node labels for all original vertices except v;
    # introduce three fresh labels for v_1, v_2, v_3 chosen to be larger
    # than any existing label so we can predict the canonical relabel.
    G_lab = nx.Graph()
    G_lab.add_nodes_from(u for u in G.nodes() if u != v)
    for u, w in G.edges():
        if u == v or w == v:
            continue
        G_lab.add_edge(u, w)

    n_max = max(G.nodes()) if G.number_of_nodes() > 0 else -1
    v_new = (n_max + 1, n_max + 2, n_max + 3)
    G_lab.add_nodes_from(v_new)
    # Triangle
    G_lab.add_edge(v_new[0], v_new[1])
    G_lab.add_edge(v_new[0], v_new[2])
    G_lab.add_edge(v_new[1], v_new[2])
    # Spokes
    for vi, u in zip(v_new, neighbours):
        G_lab.add_edge(vi, u)

    # Canonicalise: this relabels nodes sorted ascending to 0..n+1.
    G_prime = _canonicalize(G_lab)

    # Compute the relabel mapping used by _canonicalize so we can
    # translate v_new and neighbours back to G_prime's integer labels.
    sorted_nodes = sorted(G_lab.nodes())
    relabel = {n_: i for i, n_ in enumerate(sorted_nodes)}

    old_to_new_spokes = [
        ((v, u), (relabel[vi], relabel[u]))
        for vi, u in zip(v_new, neighbours)
    ]
    triangle_edges = [
        (relabel[v_new[0]], relabel[v_new[1]]),
        (relabel[v_new[0]], relabel[v_new[2]]),
        (relabel[v_new[1]], relabel[v_new[2]]),
    ]
    vertex_map = {u: relabel[u] for u in G.nodes() if u != v}
    return G_prime, vertex_map, old_to_new_spokes, triangle_edges


def triangle_blowup_flow(
    f1: np.ndarray, f2: np.ndarray, f3: np.ndarray, *, chirality: int = +1
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Closed-form $S^2$-flow on the triangle.

    Inputs are three unit 3-vectors with ``f1 + f2 + f3 == 0`` (no
    sanity check; caller is responsible). Returns ``(g12, g13, g23)``
    with each entry a unit vector and the three Kirchhoff equations at
    the triangle vertices satisfied for the canonical orientations
    described in the module docstring.

    ``chirality`` chooses the sign of the out-of-plane component; both
    choices yield valid $S^2$-flows.
    """
    f1 = np.asarray(f1, dtype=np.float64)
    f2 = np.asarray(f2, dtype=np.float64)
    f3 = np.asarray(f3, dtype=np.float64)
    diff = f2 - f1
    normal_raw = np.cross(f3, diff)
    norm = np.linalg.norm(normal_raw)
    if norm < 1e-12:
        # f1, f2, f3 are colinear; the three spokes can't be a valid
        # 120-degree triple of unit vectors summing to zero.
        raise ValueError("spoke triple is degenerate (colinear)")
    n = normal_raw / norm
    g12 = diff / 3.0 + chirality * np.sqrt(2.0 / 3.0) * n
    g13 = -f1 - g12
    g23 = -f2 + g12
    return g12, g13, g23


def extend_witness_through_blowup(
    G: nx.Graph,
    witness: list[list[float]] | np.ndarray,
    v: int,
    *,
    chirality: int = +1,
    tol: float = 1e-7,
) -> dict:
    """Blow up vertex v of G, build the extended $S^2$-flow on G', and
    verify it via ``witness.verify_witness``.

    Returns a dict with:
      - ``G_prime``: blown-up graph
      - ``edges_prime``, ``vectors_prime``: the new flow data
      - ``verify``: the verify_witness output (should have ok=True)
    """
    X = np.asarray(witness, dtype=np.float64)
    edges_G, sign_G = orient(G)
    edge_index = {tuple(e): k for k, e in enumerate(edges_G)}

    # Spoke values at v: f_i where the canonical edge is (min(v,u_i), max(v,u_i))
    # and the orientation sign is +1 if v < u_i (edge "leaves" v under canonical lex).
    neighbours = sorted(G.neighbors(v))
    f_list: list[np.ndarray] = []
    for u in neighbours:
        a, b = (v, u) if v < u else (u, v)
        k = edge_index[(a, b)]
        # We want the spoke value "out of v": if v is the tail (v<u), use +x_e; else -x_e.
        sig = +1.0 if v < u else -1.0
        f_list.append(sig * X[k])

    f1, f2, f3 = f_list
    g12, g13, g23 = triangle_blowup_flow(f1, f2, f3, chirality=chirality)

    G_prime, vertex_map, old_to_new_spokes, triangle_edges = triangle_blowup(G, v)
    edges_prime, sign_prime = orient(G_prime)
    edge_index_prime = {tuple(e): k for k, e in enumerate(edges_prime)}

    X_prime = np.zeros((len(edges_prime), 3), dtype=np.float64)

    # Untouched edges keep their old value (translated through vertex_map).
    for k, e in enumerate(edges_G):
        u, w = e
        if u == v or w == v:
            continue
        u2, w2 = vertex_map[u], vertex_map[w]
        a, b = (u2, w2) if u2 < w2 else (w2, u2)
        if (a, b) not in edge_index_prime:
            raise RuntimeError(f"edge {e} -> {(a, b)} missing in G_prime")
        # Both G and G_prime use canonical lex orientation, and vertex_map
        # preserves order (it's monotone since _canonicalize sorts), so
        # the canonical-orientation value is the same.
        X_prime[edge_index_prime[(a, b)]] = X[k]

    # New spoke edges (v_i, u_i): the "out of v_i" value equals f_i. The canonical
    # edge in G' is (min(v_i, u_i), max(v_i, u_i)); apply the sign.
    for (old_edge, new_spoke), f in zip(old_to_new_spokes, f_list):
        vi, u = new_spoke
        a, b = (vi, u) if vi < u else (u, vi)
        sig = +1.0 if vi < u else -1.0
        # X_prime[(a,b)] is the canonical-orientation value: we want
        # sig * X_prime = f, hence X_prime = sig * f (sig**2=1).
        X_prime[edge_index_prime[(a, b)]] = sig * f

    # Triangle edges: by construction (vi -> v_{i+1}) carries g_{ij}.
    # Our triangle_edges list is [(v0, v1), (v0, v2), (v1, v2)] with v0<v1<v2.
    # Canonical orientation: each edge points from the smaller to the larger,
    # i.e. v_0 -> v_1, v_0 -> v_2, v_1 -> v_2. We use g12 := v_0 -> v_1,
    # g13 := v_0 -> v_2, g23 := v_1 -> v_2. The closed-form derivation
    # also used these orientations (see module docstring), so signs match.
    for tri_edge, g in zip(triangle_edges, (g12, g13, g23)):
        a, b = tri_edge  # already sorted, hence canonical orientation +1
        X_prime[edge_index_prime[(a, b)]] = g

    check = verify_witness(G_prime, edges_prime, X_prime.tolist(), tol=tol)
    return {
        "G_prime": G_prime,
        "edges_prime": edges_prime,
        "vectors_prime": X_prime,
        "verify": check,
        "spoke_vectors_at_v": (f1, f2, f3),
        "triangle_vectors": (g12, g13, g23),
        "chirality": chirality,
    }
