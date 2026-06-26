"""Exact graph invariants for Chen-Chvatal Conjecture 2.2
(arXiv:1606.06011, Beaudou-Kahn-Rochet, "A new class of graphs that
satisfies the Chen-Chvatal Conjecture").

Everything here is finite and EXACTLY computable (no heuristics, no
asymptotics).  The three invariants:

  ell(G)  = number of distinct LINES of G.
            For a pair {a,b}, a<>b, the line determined by a,b is
              line(a,b) = {a,b} U {x : [abx] or [axb] or [xab]}
            where [uvw] is the metric-betweenness relation
              [uvw]  iff  d(u,v) + d(v,w) = d(u,w)
            with d the (unweighted) graph-distance metric (BFS / APSP).
            ell(G) = | { line(a,b) : a < b } |  (distinct sets).
            Only defined / counted on a CONNECTED graph (finite metric).

  br(G)   = number of bridges (cut-edges) of G.

  pendant = G has a pendant edge  iff some vertex has degree 1
            (a pendant edge is a bridge incident to a degree-1 vertex;
             equivalently G has a degree-1 vertex).

The Chen-Chvatal "universal line / Chen-Chvatal Conjecture" context:
a graph has a UNIVERSAL line (a line equal to the whole vertex set) or
at least |G| distinct lines.  Conjecture 2.2 of the paper states there
is a FINITE set F_0 of connected graphs such that every connected graph
G not in F_0 either has a pendant edge OR satisfies ell(G)+br(G) >= |G|.

A graph is "BAD" (a potential obstruction) iff it is connected,
pendant-edge-free, and ell(G) + br(G) < |G|.  The paper's F_0 (Figs 1-3)
lists the known small bad graphs.
"""
from __future__ import annotations

import itertools
from collections import deque

import networkx as nx


# --------------------------------------------------------------------------- #
#  graph6 decoding (headerless, n < 63) -- mirrors engine/lib/digraph_core
# --------------------------------------------------------------------------- #

def graph6_to_edges(line):
    """Decode a headerless graph6 line into (n, edges)."""
    b = line.strip().encode("ascii")
    if not b:
        return 0, []
    if b[0] == 126:
        raise NotImplementedError("n>=63 graph6 not needed here")
    n = b[0] - 63
    bits = []
    for ch in b[1:]:
        v = ch - 63
        for k in range(5, -1, -1):
            bits.append((v >> k) & 1)
    edges, idx = [], 0
    for j in range(1, n):
        for i in range(j):
            if idx < len(bits) and bits[idx]:
                edges.append((i, j))
            idx += 1
    return n, edges


# --------------------------------------------------------------------------- #
#  exact graph-distance metric (unweighted BFS all-pairs)
# --------------------------------------------------------------------------- #

def all_pairs_distances(n, edges):
    """n x n matrix of exact BFS shortest-path distances.
    Unreachable pairs get a sentinel of None (graph not connected)."""
    adj = [[] for _ in range(n)]
    for (u, v) in edges:
        adj[u].append(v)
        adj[v].append(u)
    INF = None
    dist = [[INF] * n for _ in range(n)]
    for s in range(n):
        ds = dist[s]
        ds[s] = 0
        q = deque([s])
        while q:
            u = q.popleft()
            du = ds[u]
            for w in adj[u]:
                if ds[w] is None:
                    ds[w] = du + 1
                    q.append(w)
    return dist


def is_connected(n, edges):
    if n <= 1:
        return True
    adj = [[] for _ in range(n)]
    for (u, v) in edges:
        adj[u].append(v)
        adj[v].append(u)
    seen = [False] * n
    seen[0] = True
    q = deque([0])
    cnt = 1
    while q:
        u = q.popleft()
        for w in adj[u]:
            if not seen[w]:
                seen[w] = True
                cnt += 1
                q.append(w)
    return cnt == n


# --------------------------------------------------------------------------- #
#  betweenness + lines
# --------------------------------------------------------------------------- #

def line_of_pair(dist, n, a, b):
    """The set line(a,b) as a frozenset of vertices.
       x in line(a,b) iff [abx] or [axb] or [xab], i.e. one of a,b,x is
       metrically between the other two.  a and b are always included."""
    dab = dist[a][b]
    pts = {a, b}
    for x in range(n):
        if x == a or x == b:
            continue
        dax = dist[a][x]
        dbx = dist[b][x]
        # [axb]: x between a and b  -> d(a,x)+d(x,b)=d(a,b)
        if dax + dbx == dab:
            pts.add(x)
            continue
        # [abx]: b between a and x  -> d(a,b)+d(b,x)=d(a,x)
        if dab + dbx == dax:
            pts.add(x)
            continue
        # [xab]: a between x and b  -> d(x,a)+d(a,b)=d(x,b)
        if dax + dab == dbx:
            pts.add(x)
            continue
    return frozenset(pts)


def all_lines(n, edges):
    """Set of distinct lines (each a frozenset of vertices).  Requires a
    connected graph (finite metric)."""
    if n <= 1:
        return set()
    if not is_connected(n, edges):
        raise ValueError("ell(G) is only defined on a connected graph")
    dist = all_pairs_distances(n, edges)
    lines = set()
    for a, b in itertools.combinations(range(n), 2):
        lines.add(line_of_pair(dist, n, a, b))
    return lines


def ell(n, edges):
    """ell(G) = number of distinct lines."""
    return len(all_lines(n, edges))


# --------------------------------------------------------------------------- #
#  bridges, pendant edges, degrees  (networkx, exact)
# --------------------------------------------------------------------------- #

def _nx_graph(n, edges):
    g = nx.Graph()
    g.add_nodes_from(range(n))
    g.add_edges_from(edges)
    return g


def bridges_count(n, edges):
    """br(G) = number of bridges (cut-edges), exact via networkx."""
    g = _nx_graph(n, edges)
    return sum(1 for _ in nx.bridges(g))


def degrees(n, edges):
    deg = [0] * n
    for (u, v) in edges:
        deg[u] += 1
        deg[v] += 1
    return deg


def has_pendant_edge(n, edges):
    """True iff some vertex has degree 1 (i.e. G has a pendant edge)."""
    return any(d == 1 for d in degrees(n, edges))


# --------------------------------------------------------------------------- #
#  the conjecture predicate
# --------------------------------------------------------------------------- #

def invariants(n, edges):
    """All exact invariants + the Conjecture-2.2 classification for a
    connected graph."""
    conn = is_connected(n, edges)
    out = {
        "n": n,
        "m_edges": len(edges),
        "connected": conn,
    }
    if not conn:
        out["note"] = "disconnected -- ell/lines undefined"
        return out
    L = all_lines(n, edges)
    el = len(L)
    br = bridges_count(n, edges)
    pend = has_pendant_edge(n, edges)
    out.update({
        "ell": el,
        "br": br,
        "ell_plus_br": el + br,
        "has_pendant_edge": pend,
        "satisfies_ell_plus_br_geq_n": (el + br >= n),
        # "bad" = the conjecture's obstruction candidate:
        #   connected, pendant-free, and ell+br < n.
        "is_bad": (not pend) and (el + br < n),
    })
    return out


def is_bad(n, edges):
    """A graph is BAD (an F_0-candidate obstruction) iff it is connected,
    pendant-edge-free, and ell(G)+br(G) < |G|."""
    if not is_connected(n, edges):
        return False
    if has_pendant_edge(n, edges):
        return False
    return ell(n, edges) + bridges_count(n, edges) < n
