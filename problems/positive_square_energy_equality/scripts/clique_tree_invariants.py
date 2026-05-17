"""Clique-tree invariants for the 5e.a.general structural attack (plan v14).

Given a 2-tree G and a simplicial deg-2 ear v with neighbours {a, b},
compute the clique-tree structure of G and the clique-tree-local invariants
relevant to the joint-invariant I(v) = W^-(v) + (M_1^-(v))^2 / M_2^-(v).

Key constructions:
- clique_tree(G): returns the (unique, since G is 2-tree) clique tree as a
  networkx graph whose nodes are triangles of G and edges are pairs of
  triangles sharing an edge of G.
- shape_classify(T): label T as 'path', 'star', 'caterpillar', or 'other'.
- I_at_ear(G, v): compute (W^-, M_1^-, M_2^-, sigma, |T_ab|, I) at the
  simplicial deg-2 ear v.
- max_degsum_ears(G): list of simplicial deg-2 ears achieving the maximum
  of deg_{G-v}(a) + deg_{G-v}(b).

Provides the structural backbone for the inductive arguments developed in
docs/lprime_5e_a_general.md (v14 Track 2).
"""
from __future__ import annotations

from typing import Iterable

import networkx as nx
import numpy as np

TOL = 1e-9


def to_graph6(G: nx.Graph) -> str:
    return nx.to_graph6_bytes(G, header=False).decode().strip()


def from_graph6(code: str) -> nx.Graph:
    return nx.from_graph6_bytes(code.encode())


def simplicial_deg2_ears(G: nx.Graph) -> list[tuple[int, int, int]]:
    """Return [(v, a, b), ...] for every simplicial deg-2 vertex v of G."""
    ears = []
    for v in G.nodes():
        if G.degree(v) != 2:
            continue
        nbrs = list(G.neighbors(v))
        if len(nbrs) != 2:
            continue
        a, b = nbrs
        if not G.has_edge(a, b):
            continue
        if G.number_of_nodes() - 1 < 3:
            continue
        ears.append((v, a, b))
    return ears


def max_degsum_ears(G: nx.Graph) -> list[tuple[int, int, int]]:
    """Return the simplicial deg-2 ears achieving the max of
    deg_{G-v}(a) + deg_{G-v}(b)."""
    ears = simplicial_deg2_ears(G)
    if not ears:
        return []
    deg_sums = []
    for v, a, b in ears:
        deg_sums.append(G.degree(a) - 1 + G.degree(b) - 1)
    mx = max(deg_sums)
    return [e for e, d in zip(ears, deg_sums) if d == mx]


def clique_tree(G: nx.Graph) -> nx.Graph:
    """Build the clique tree of a 2-tree G.

    For a 2-tree on n >= 3 vertices, the clique tree T(G) has n-2 nodes
    (triangles) and n-3 edges. Two triangles are adjacent in T(G) iff they
    share an edge of G.

    For a 2-tree this clique tree is unique (since each G-edge is in at
    most 2 triangles), so we just connect any pair of triangles sharing
    a G-edge and take the minimum spanning tree (which equals the unique
    tree).
    """
    triangles = [frozenset(t) for t in nx.enumerate_all_cliques(G) if len(t) == 3]
    T = nx.Graph()
    for i in range(len(triangles)):
        T.add_node(i, vertices=tuple(sorted(triangles[i])))
    edge_to_tri: dict[tuple[int, int], list[int]] = {}
    for i, t in enumerate(triangles):
        tl = sorted(t)
        for a_idx in range(3):
            for b_idx in range(a_idx + 1, 3):
                key = (tl[a_idx], tl[b_idx])
                edge_to_tri.setdefault(key, []).append(i)
    # Build the candidate multigraph of triangle-adjacencies (via shared G-edge),
    # then take an MST.
    H = nx.Graph()
    for i in range(len(triangles)):
        H.add_node(i)
    for edge, tris in edge_to_tri.items():
        if len(tris) >= 2:
            for i in range(len(tris)):
                for j in range(i + 1, len(tris)):
                    H.add_edge(tris[i], tris[j], shared_edge=edge)
    if H.number_of_nodes() <= 1:
        return H
    if not nx.is_connected(H):
        # G is not a 2-tree
        raise ValueError("Clique adjacency graph is not connected; not a 2-tree.")
    T_unique = nx.minimum_spanning_tree(H)
    return T_unique


def shape_classify(T: nx.Graph) -> str:
    """Classify the clique tree T into one of {'empty', 'single', 'path',
    'star', 'caterpillar', 'other_max_deg<k>'}."""
    n = T.number_of_nodes()
    if n == 0:
        return "empty"
    if n == 1:
        return "single"
    degs = sorted([d for _, d in T.degree()], reverse=True)
    if all(d <= 2 for d in degs):
        return "path"
    if degs[0] == n - 1:
        return "star"
    # Caterpillar: removing leaves leaves a path
    leaves = [v for v in T.nodes() if T.degree(v) == 1]
    interior = T.copy()
    interior.remove_nodes_from(leaves)
    if interior.number_of_nodes() == 0:
        return "caterpillar"  # actually star-like; covered above
    if interior.number_of_nodes() == 1:
        return "caterpillar"
    interior_degs = [d for _, d in interior.degree()]
    if all(d <= 2 for d in interior_degs):
        return "caterpillar"
    return f"other_max_deg{degs[0]}"


def I_at_ear(G: nx.Graph, v: int, a: int, b: int) -> dict:
    """Compute the joint-invariant features at the simplicial ear v in G.

    Returns a dict with keys:
      W_minus, M1_minus, M2_minus, M1, M2, sigma, T_ab_in_H, I
    where I = W^- + (M_1^-)^2 / M_2^-  (defining 0/0 := 0 if M_2^- = 0).
    """
    H = G.copy()
    H.remove_node(v)
    nodes = sorted(H.nodes())
    idx = {u: i for i, u in enumerate(nodes)}
    A = nx.to_numpy_array(H, nodelist=nodes, dtype=float)
    mu, U = np.linalg.eigh(A)
    mu = mu[::-1]
    U = U[:, ::-1]
    ia, ib = idx[a], idx[b]
    c = U[ia, :] + U[ib, :]
    c_sq = c * c
    neg_mask = mu < -TOL
    pos_mask = mu > TOL
    zero_mask = ~(neg_mask | pos_mask)
    W_minus = float(np.sum(c_sq[neg_mask]))
    W_zero = float(np.sum(c_sq[zero_mask]))
    W_plus = float(np.sum(c_sq[pos_mask]))
    M1_minus = float(np.sum(c_sq[neg_mask] * mu[neg_mask]))
    M2_minus = float(np.sum(c_sq[neg_mask] * mu[neg_mask] ** 2))
    M1_plus = float(np.sum(c_sq[pos_mask] * mu[pos_mask]))
    M2_plus = float(np.sum(c_sq[pos_mask] * mu[pos_mask] ** 2))
    M1 = M1_minus + M1_plus
    M2 = M2_minus + M2_plus
    sigma = H.degree(a) + H.degree(b)
    T_ab_in_H = len(set(H.neighbors(a)) & set(H.neighbors(b)))
    if M2_minus < TOL:
        I = W_minus
    else:
        I = W_minus + (M1_minus ** 2) / M2_minus
    return {
        "W_minus": W_minus,
        "W_zero": W_zero,
        "W_plus": W_plus,
        "M1_minus": M1_minus,
        "M2_minus": M2_minus,
        "M1_plus": M1_plus,
        "M2_plus": M2_plus,
        "M1": M1,
        "M2": M2,
        "sigma": sigma,
        "T_ab_in_H": T_ab_in_H,
        "I": I,
    }


def lower_bound_I_from_M2(W_minus: float, W_zero: float, m: float, M2: float) -> float | None:
    """Compute the universal Cauchy-Schwarz two-sided lower bound on I.

    Given the observed values W^-, W^0, m = |M_1^-|, and M_2 = sigma + 2|T_ab|,
    the bound
        I >= W^- + m^2 / (M_2 - (2+m)^2 / (2 - W^- - W^0))
    holds provided W^+ = 2 - W^- - W^0 > 0 and the denominator is positive.

    Returns None if the bound is undefined (e.g. infeasible parameters).
    """
    W_plus = 2.0 - W_minus - W_zero
    if W_plus <= 0:
        return None
    denom = M2 - (2 + m) ** 2 / W_plus
    if denom <= 0:
        return None
    return W_minus + m ** 2 / denom


def ear_full_record(G: nx.Graph) -> list[dict]:
    """For every simplicial deg-2 ear v of G, return a full diagnostic record."""
    out = []
    g6 = to_graph6(G)
    ears = simplicial_deg2_ears(G)
    md_ears = set(max_degsum_ears(G))
    for v, a, b in ears:
        feats = I_at_ear(G, v, a, b)
        feats["graph6"] = g6
        feats["n"] = G.number_of_nodes()
        feats["v"] = int(v)
        feats["a"] = int(a)
        feats["b"] = int(b)
        feats["is_max_degsum"] = (v, a, b) in md_ears
        m = -feats["M1_minus"]
        feats["I_lower_bound_CS"] = lower_bound_I_from_M2(
            feats["W_minus"], feats["W_zero"], m, feats["M2"]
        )
        out.append(feats)
    return out


# --- Test fixtures / sub-family closures -------------------------------------

def make_book(k: int) -> nx.Graph:
    """B_k: book with k pages, n = k+2 vertices. Spine {0,1}, apex {2,...,k+1}."""
    G = nx.Graph()
    G.add_edge(0, 1)
    for i in range(k):
        G.add_edge(0, 2 + i)
        G.add_edge(1, 2 + i)
    return G


def make_two_path(n: int) -> nx.Graph:
    """L_n: 2-path on n >= 3 vertices."""
    G = nx.Graph()
    for i in range(n - 2):
        G.add_edge(i, i + 1)
        G.add_edge(i, i + 2)
    G.add_edge(n - 2, n - 1)
    return G


def make_fan(n: int) -> nx.Graph:
    """F_n: fan, n >= 4. Hub 0, path 1-2-...-(n-1), all connected to 0."""
    G = nx.Graph()
    for i in range(1, n):
        G.add_edge(0, i)
    for i in range(1, n - 1):
        G.add_edge(i, i + 1)
    return G


if __name__ == "__main__":
    # Demonstrate on the global-minimum graph
    g6 = "I}qcHG`GO"
    G = from_graph6(g6)
    T = clique_tree(G)
    print(f"Graph {g6}, n={G.number_of_nodes()}")
    print(f"  Clique tree shape: {shape_classify(T)}")
    print(f"  Clique tree degree sequence: {sorted([d for _, d in T.degree()], reverse=True)}")
    print(f"  Max-degsum ears: {max_degsum_ears(G)}")
    for v, a, b in max_degsum_ears(G):
        feats = I_at_ear(G, v, a, b)
        m = -feats["M1_minus"]
        bound = lower_bound_I_from_M2(feats["W_minus"], feats["W_zero"], m, feats["M2"])
        print(f"    ear v={v}: I = {feats['I']:.4f}, sigma = {feats['sigma']}, "
              f"|T_ab(H)| = {feats['T_ab_in_H']}, M_2 = {feats['M2']:.2f}, "
              f"CS-lower bound = {bound:.4f}" if bound else "    bound undefined")
