"""Check ear gains for specific 2-tree families: book B_k, fan F_k, 2-path L_k."""
from __future__ import annotations
import sys
from pathlib import Path
import networkx as nx
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from spectrum_check import s_plus_minus  # noqa: E402


def book(k: int) -> nx.Graph:
    """B_k: k triangles sharing a common edge {0,1}. Order = k+2."""
    G = nx.Graph()
    G.add_edge(0, 1)
    for j in range(k):
        G.add_edge(0, 2 + j)
        G.add_edge(1, 2 + j)
    return G


def fan(k: int) -> nx.Graph:
    """F_k: K_1 join P_k (k+1 vertices). 2-tree."""
    G = nx.path_graph(k)
    apex = k
    G.add_node(apex)
    for v in range(k):
        G.add_edge(apex, v)
    return G


def two_path(k: int) -> nx.Graph:
    """L_k: 2-tree whose clique tree is a path; k triangles in chain. Order = k+2."""
    G = nx.Graph()
    G.add_edge(0, 1)
    for j in range(k):
        G.add_edge(j, j + 2)
        G.add_edge(j + 1, j + 2)
    return G


def book_minus_one_triangle_plus_pendant_triangle(k: int) -> nx.Graph:
    """Empirical n=>>=6 minimizer: book B_{k-1} with one extra triangle attached
    at vertex 2 of B_{k-1}.

    Concretely: vertices 0,1 share edge; vertices 2..k form pages of book on (0,1).
    Add vertex k+1 adjacent to 2 and k; add edge (k, k+1)? But (k,k+1) needs to be
    an edge of an existing triangle of the 2-tree.

    From the n=10 minimizer: edges (2,8), (2,9), (8,9) attached to base of
    book B_6 sitting on (0,1). So we attach a new triangle {2, k, k+1} where
    {2, k} must already be an edge. We adopt: place k+1 adjacent to {2, k}
    where (2, k) is a book page edge -- but that doesn't exist directly.

    A cleaner way: take book B_{k-1} on edge {0,1}, then add a new vertex w
    adjacent to vertices 0 and 2 (which are already adjacent via the page triangle).
    """
    G = book(k - 1)  # vertices 0..k
    w = k + 1
    # attach triangle on edge (0, 2)
    G.add_edge(0, w)
    G.add_edge(2, w)
    return G


def family_summary(name: str, family_fn, params):
    print(f"\n--- {name} ---")
    print(f"{'n':>4} {'min_delta+':>14} {'min_delta-':>14} {'argmin_v':>10}")
    for p in params:
        G = family_fn(p)
        n = G.number_of_nodes()
        full = s_plus_minus(G)
        best_plus = (float("inf"), None)
        best_minus = (float("inf"), None)
        for v in G.nodes():
            if G.degree(v) != 2:
                continue
            a, b = list(G.neighbors(v))
            if not G.has_edge(a, b):
                continue
            H = G.copy(); H.remove_node(v)
            if H.number_of_nodes() < 3:
                continue
            sub = s_plus_minus(H)
            dp = full["s_plus"] - sub["s_plus"]
            dm = full["s_minus"] - sub["s_minus"]
            if dp < best_plus[0]:
                best_plus = (dp, v)
            if dm < best_minus[0]:
                best_minus = (dm, v)
        print(f"{n:>4} {best_plus[0]:>14.8f} {best_minus[0]:>14.8f} "
              f"+:{best_plus[1]} -:{best_minus[1]}")


if __name__ == "__main__":
    family_summary("Book B_k", book, range(2, 14))
    family_summary("Fan F_k", fan, range(3, 14))
    family_summary("2-path L_k", two_path, range(2, 14))
    family_summary("Book+ear (n=10 minimizer family)",
                   book_minus_one_triangle_plus_pendant_triangle,
                   range(3, 14))
