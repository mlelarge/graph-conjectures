"""Core EXACT oracle for the lines+bridges Chen-Chvatal question (arXiv:1606.06011).

Problem (Aboulker, Matamala, Rochet, Zamora -- "A new class of graphs that
satisfies the Chen-Chvatal conjecture", and the open question on counter-examples
to  ell(G) + br(G) >= |G|).

Definitions (metric / graph-theoretic, all EXACT integer combinatorics):

  * G is a connected simple graph; |G| = n = number of vertices.
  * d(u,v) = shortest-path (hop) distance in G  -- exact via BFS.
  * Betweenness [p q r] holds iff  d(p,q) + d(q,r) = d(p,r)  (q is metrically
    between p and r).
  * For an ordered/unordered pair {a,b} with a != b, the LINE
        ab  =  {a, b} U { x : [a b x] or [a x b] or [x a b] }
    i.e. x lies on the line through a and b iff one of the three points is
    metrically between the other two.  Lines are symmetric: line(a,b)=line(b,a).
  * ell(G) = number of DISTINCT lines (as vertex subsets) over all pairs {a,b}.
  * br(G) = number of bridges (cut-edges) of G.

The Chen-Chvatal "lines" question asks about counter-examples to
        ell(G) + br(G) >= |G| = n.
A graph G is a COUNTER-EXAMPLE iff  ell(G) + br(G) < n.

Everything here is EXACT (pure BFS + set arithmetic, no heuristics, no SAT).
A graph is represented as (n, edges) with edges a list of (u, v),
vertices 0..n-1.  Enumeration of all connected graphs of small order is via
nauty `geng -c`.
"""
from __future__ import annotations

import subprocess
from collections import deque
from itertools import combinations

import networkx as nx


# --------------------------------------------------------------------------- #
#  Basic structure
# --------------------------------------------------------------------------- #

def _adj(n, edges):
    adj = [set() for _ in range(n)]
    for (u, v) in edges:
        adj[u].add(v)
        adj[v].add(u)
    return adj


def all_pairs_distances(n, edges):
    """Exact all-pairs shortest-path (hop) distances via BFS from each vertex.

    Returns an n x n list-of-lists; unreachable pairs get -1 (won't happen on a
    connected graph, which is the only input we score)."""
    adj = _adj(n, edges)
    INF = -1
    dist = [[INF] * n for _ in range(n)]
    for s in range(n):
        ds = dist[s]
        ds[s] = 0
        q = deque([s])
        while q:
            u = q.popleft()
            du = ds[u]
            for w in adj[u]:
                if ds[w] == INF:
                    ds[w] = du + 1
                    q.append(w)
    return dist


def is_connected(n, edges):
    if n <= 1:
        return True
    adj = _adj(n, edges)
    seen = {0}
    q = deque([0])
    while q:
        u = q.popleft()
        for w in adj[u]:
            if w not in seen:
                seen.add(w)
                q.append(w)
    return len(seen) == n


# --------------------------------------------------------------------------- #
#  Lines  (metric betweenness)
# --------------------------------------------------------------------------- #

def line(n, dist, a, b):
    """The line through distinct vertices a, b as a frozenset of vertices.

    x is on line ab iff one of [a b x], [a x b], [x a b] holds, where
    [p q r] := d(p,q)+d(q,r)==d(p,r)."""
    dab = dist[a][b]
    pts = {a, b}
    for x in range(n):
        if x == a or x == b:
            continue
        dax = dist[a][x]
        dbx = dist[b][x]
        # [a b x]: d(a,b)+d(b,x)=d(a,x)  ;  [a x b]: d(a,x)+d(x,b)=d(a,b)
        # [x a b]: d(x,a)+d(a,b)=d(x,b)
        if (dab + dbx == dax) or (dax + dbx == dab) or (dax + dab == dbx):
            pts.add(x)
    return frozenset(pts)


def all_lines(n, edges, dist=None):
    """Set of DISTINCT lines (each a frozenset of vertices) over all pairs."""
    if dist is None:
        dist = all_pairs_distances(n, edges)
    lines = set()
    for a, b in combinations(range(n), 2):
        lines.add(line(n, dist, a, b))
    return lines


def ell(n, edges, dist=None):
    """ell(G) = number of distinct lines."""
    return len(all_lines(n, edges, dist))


# --------------------------------------------------------------------------- #
#  Bridges
# --------------------------------------------------------------------------- #

def bridges(n, edges):
    """List of bridges (cut-edges), each as a sorted tuple (u,v)."""
    G = nx.Graph()
    G.add_nodes_from(range(n))
    G.add_edges_from(edges)
    return [tuple(sorted(e)) for e in nx.bridges(G)]


def br(n, edges):
    """br(G) = number of bridges."""
    return len(bridges(n, edges))


# --------------------------------------------------------------------------- #
#  The predicate
# --------------------------------------------------------------------------- #

def lines_bridges_invariant(n, edges):
    """Compute (ell, br, n) and the predicate  ell + br >= n.

    Returns a dict.  is_counterexample == True iff ell + br < n."""
    dist = all_pairs_distances(n, edges)
    lset = all_lines(n, edges, dist)
    bl = bridges(n, edges)
    l = len(lset)
    b = len(bl)
    return {
        "n": n,
        "m_edges": len(edges),
        "ell": l,
        "br": b,
        "lhs": l + b,
        "predicate_holds": (l + b) >= n,       # ell + br >= n
        "is_counterexample": (l + b) < n,       # ell + br < n
        "n_bridges": b,
        "bridgeless": (b == 0),
        "lines": sorted(sorted(s) for s in lset),
        "bridge_list": bl,
    }


# --------------------------------------------------------------------------- #
#  nauty geng: connected simple graphs
# --------------------------------------------------------------------------- #

def _geng_path():
    for cand in ("geng", "nauty-geng"):
        try:
            subprocess.run([cand, "--help"], capture_output=True)
            return cand
        except FileNotFoundError:
            continue
    raise RuntimeError("nauty geng not found on PATH")


def _graph6_to_edges(line_str):
    """Decode a headerless graph6 line into (n, edges)."""
    b = line_str.strip().encode("ascii")
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


def connected_graphs(n, extra_flags=None):
    """Yield (n, edges) for every connected simple graph on n vertices
    (one per isomorphism class) via `geng -c`."""
    gp = _geng_path()
    flags = [gp, "-c", "-q", str(n)]
    if extra_flags:
        flags = [gp, "-c", "-q", *extra_flags, str(n)]
    proc = subprocess.run(flags, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"geng failed: {proc.stderr}")
    for ln in proc.stdout.splitlines():
        if ln.strip():
            yield _graph6_to_edges(ln)
