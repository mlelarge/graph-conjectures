"""Test the extreme delta- family.

The n=10 minimizer was a book B_{n-3} on (0,1) plus a single extra triangle
attached at one of its outer vertices (degree-3 vertex of the resulting graph).

Concretely, parametrise by k = number of book pages. Vertices:
  0, 1: book spine.
  2..k+1: book page tips.
  Then a triangle on edge (2, k+1)? But that is NOT an edge.

Re-read n=10 g6=I}rEEA_GG:
  Edges: (0,1..8), (1,2..7), (2,8), (2,9), (8,9).
  Vertex 0 deg 8 (spine), vertex 1 deg 7 (spine of small book).
  Pages of large book (on 0,1): 2,3,4,5,6,7  -- but 1 not connected to 8.
  Actually: edges (0,8) exists, but (1,8) does not. So 8 is connected to 0,2,9.
  And 9 connected to 0,2,8.

So 0 is connected to everyone (1..8). The "book" structure is on (0,1) for
vertices 2..7 (six pages: triangles {0,1,2},...,{0,1,7}).
Then an extra triangle {0,2,8} (since 2 is a page tip already adjacent to 0).
Then {0,8,9}? No: (0,9), (2,9), (8,9). So {2,8,9} forms a triangle attached
on the edge (2,8), and (0,9) is part of the triangle {0,2,9} = {0,2,9} since
(0,2),(0,9),(2,9) all present.

Recap: K_1 (vertex 0) join (a path-ish structure). Actually this is the WHEEL-like
"K_1 join G'" where G' is a tree on n-1 vertices. Check: vertex 0 has degree
n-1=9? It has degree 8 (connected to 1..8 but not 9). So almost K_1 join.

Try parametric family: A_k = "book B_k on (0,1), then attach an extra triangle
on edge (0, 2)" -- already computed as Book+ear above; that family has
delta- approaching 1.81 from below, NOT 1.16.

So the n=10 minimizer is yet a different family. Let me reverse-engineer it
exhaustively.

Edges of n=10 minimizer (g6=I}rEEA_GG):
  (0,1),(0,2),(0,3),(0,4),(0,5),(0,6),(0,7),(0,8),
  (1,2),(1,3),(1,4),(1,5),(1,6),(1,7),
  (2,8),(2,9),(8,9).
That's 17 edges. n=10 => 2-tree has 2n-3 = 17 edges. Good.

Construction by simplicial degree-2 additions:
  Start K_3 = {0,1,2}.
  Add 3 on (0,1).
  Add 4 on (0,1).
  Add 5 on (0,1).
  Add 6 on (0,1).
  Add 7 on (0,1).      <- now we have B_6 on edge (0,1) with pages 2..7
  Add 8 on (0,2).      <- new triangle {0,2,8}
  Add 9 on (2,8).      <- new triangle {2,8,9}

So this is a "tripod book": one main book + a small 2-path of 2 extra triangles
hanging off one page.

Generalize family: BOOK_k_TAIL_t
  - book B_k on (0,1), pages 2..k+1
  - 2-path of t triangles attached starting on edge (0, 2)
"""
from __future__ import annotations
import sys
from pathlib import Path
import networkx as nx
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from spectrum_check import s_plus_minus  # noqa: E402


def book_with_tail(k: int, t: int) -> nx.Graph:
    """B_k on (0,1) with pages 2..k+1, then a 2-path of t extra triangles
    hanging off (0,2)."""
    G = nx.Graph()
    G.add_edge(0, 1)
    for j in range(k):
        G.add_edge(0, 2 + j)
        G.add_edge(1, 2 + j)
    # tail: vertex k+2 on edge (0,2), then k+3 on (2, k+2), then ...
    if t >= 1:
        u = k + 2
        G.add_edge(0, u)
        G.add_edge(2, u)
    prev = 2
    prev_partner = k + 2
    for s in range(1, t):
        new_v = k + 2 + s
        G.add_edge(prev, new_v)
        G.add_edge(prev_partner, new_v)
        prev, prev_partner = prev_partner, new_v
    return G


def ear_gains(G):
    full = s_plus_minus(G)
    best_p = (float("inf"), None)
    best_m = (float("inf"), None)
    for v in G.nodes():
        if G.degree(v) != 2: continue
        a, b = list(G.neighbors(v))
        if not G.has_edge(a, b): continue
        H = G.copy(); H.remove_node(v)
        if H.number_of_nodes() < 3: continue
        sub = s_plus_minus(H)
        dp = full["s_plus"] - sub["s_plus"]
        dm = full["s_minus"] - sub["s_minus"]
        if dp < best_p[0]: best_p = (dp, v, H.degree(a), H.degree(b))
        if dm < best_m[0]: best_m = (dm, v, H.degree(a), H.degree(b))
    return best_p, best_m


if __name__ == "__main__":
    print(f"{'k':>3} {'t':>3} {'n':>3} {'min_delta+':>14} {'min_delta-':>14}")
    for t in range(1, 5):
        for k in range(2, 20):
            G = book_with_tail(k, t)
            bp, bm = ear_gains(G)
            print(f"{k:>3} {t:>3} {G.number_of_nodes():>3} "
                  f"{bp[0]:>14.8f} {bm[0]:>14.8f}")
        print()
