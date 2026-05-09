"""Graph data and Cartesian-product construction for the pebbling project.

This module is the trusted source for graphs used by the pebbling verifier.
It loads named graphs from `data/pebbling_product/graphs/*.json`, exposes a
small library of toy graphs (paths, cycles, cubes), and builds Cartesian
products with explicit coordinate-preserving vertex labels.

Graphs are represented as `(n, edges)` where `n` is the number of vertices
and `edges` is a sorted list of unordered pairs `(u, v)` with `u < v` and
`0 <= u, v < n`. Every helper validates simple, undirected, connected
input.

The Cartesian product convention is fixed once and for all: vertices of
`G box H` are pairs `(u, v)`, encoded by the bijection
`pair_to_index(u, v) = u * |V(H)| + v`. Two pairs `(u1, v1)` and
`(u2, v2)` are adjacent in `G box H` iff
- `u1 == u2` and `v1 v2` is an edge of `H`; or
- `v1 == v2` and `u1 u2` is an edge of `G`.

Tensor / direct products are intentionally absent.
"""

from __future__ import annotations

import json
from collections import deque
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
GRAPH_DIR = REPO_ROOT / "data" / "pebbling_product" / "graphs"


@dataclass(frozen=True)
class Graph:
    """Simple undirected graph on vertices ``0..n-1``."""

    n: int
    edges: tuple[tuple[int, int], ...]
    name: str = ""

    def adjacency(self) -> list[list[int]]:
        adj: list[list[int]] = [[] for _ in range(self.n)]
        for u, v in self.edges:
            adj[u].append(v)
            adj[v].append(u)
        for row in adj:
            row.sort()
        return adj


def _normalize_edges(edges) -> tuple[tuple[int, int], ...]:
    seen: set[tuple[int, int]] = set()
    for e in edges:
        if len(e) != 2:
            raise ValueError(f"edge {e!r} is not a pair")
        u, v = int(e[0]), int(e[1])
        if u == v:
            raise ValueError(f"self-loop at vertex {u}")
        if u > v:
            u, v = v, u
        if (u, v) in seen:
            raise ValueError(f"duplicate edge ({u},{v})")
        seen.add((u, v))
    return tuple(sorted(seen))


def make_graph(n: int, edges, name: str = "") -> Graph:
    """Construct, validate, and return a simple undirected graph."""
    if n <= 0:
        raise ValueError(f"need n > 0, got {n}")
    norm = _normalize_edges(edges)
    for u, v in norm:
        if not (0 <= u < n and 0 <= v < n):
            raise ValueError(f"edge ({u},{v}) out of range for n={n}")
    g = Graph(n=n, edges=norm, name=name)
    if not is_connected(g):
        raise ValueError(f"graph {name or '<unnamed>'} is not connected")
    return g


def is_connected(g: Graph) -> bool:
    if g.n == 0:
        return False
    adj = g.adjacency()
    seen = {0}
    queue = deque([0])
    while queue:
        u = queue.popleft()
        for w in adj[u]:
            if w not in seen:
                seen.add(w)
                queue.append(w)
    return len(seen) == g.n


def bfs_distances(g: Graph, source: int) -> list[int]:
    """Unweighted shortest-path distances from ``source`` to every vertex."""
    if not 0 <= source < g.n:
        raise ValueError(f"source {source} out of range")
    adj = g.adjacency()
    dist = [-1] * g.n
    dist[source] = 0
    queue = deque([source])
    while queue:
        u = queue.popleft()
        for w in adj[u]:
            if dist[w] == -1:
                dist[w] = dist[u] + 1
                queue.append(w)
    return dist


def cartesian_product(g: Graph, h: Graph, name: str | None = None) -> Graph:
    """Cartesian product ``G box H`` with ``pair_to_index(u, v) = u*|V(H)| + v``.

    Vertices: ``g.n * h.n`` pairs ``(u, v)`` with ``0 <= u < g.n``,
    ``0 <= v < h.n``. Two pairs are adjacent iff they agree on one
    coordinate and the other coordinate forms an edge of the corresponding
    factor.
    """
    n = g.n * h.n
    edges: list[tuple[int, int]] = []
    # H-slice edges: fix u, vary along H.
    for u in range(g.n):
        base = u * h.n
        for a, b in h.edges:
            edges.append((base + a, base + b))
    # G-slice edges: fix v, vary along G.
    for v in range(h.n):
        for a, b in g.edges:
            i = a * h.n + v
            j = b * h.n + v
            edges.append((i, j))
    product_name = name or f"{g.name or 'G'}_box_{h.name or 'H'}"
    return make_graph(n, edges, name=product_name)


def pair_to_index(u: int, v: int, h_n: int) -> int:
    return u * h_n + v


def index_to_pair(idx: int, h_n: int) -> tuple[int, int]:
    return divmod(idx, h_n)


# --- Standard families -----------------------------------------------------


def path_graph(n: int, name: str | None = None) -> Graph:
    """``P_n``: path on n vertices, n-1 edges."""
    if n < 1:
        raise ValueError(f"path needs n >= 1, got {n}")
    edges = [(i, i + 1) for i in range(n - 1)]
    return make_graph(n, edges, name=name or f"P{n}")


def cycle_graph(n: int, name: str | None = None) -> Graph:
    """``C_n``: cycle on n vertices, n edges (n >= 3)."""
    if n < 3:
        raise ValueError(f"cycle needs n >= 3, got {n}")
    edges = [(i, (i + 1) % n) for i in range(n)]
    return make_graph(n, edges, name=name or f"C{n}")


def complete_graph(n: int, name: str | None = None) -> Graph:
    if n < 1:
        raise ValueError(f"complete graph needs n >= 1, got {n}")
    edges = [(i, j) for i in range(n) for j in range(i + 1, n)]
    return make_graph(n, edges, name=name or f"K{n}")


def hypercube(d: int, name: str | None = None) -> Graph:
    """``Q_d``: Boolean hypercube on ``2**d`` vertices."""
    if d < 1:
        raise ValueError(f"hypercube needs d >= 1, got {d}")
    g = path_graph(2, name="Q1")
    for k in range(2, d + 1):
        g = cartesian_product(g, path_graph(2), name=f"Q{k}")
    return Graph(n=g.n, edges=g.edges, name=name or f"Q{d}")


# --- Loading named graphs from data/pebbling_product/graphs ----------------


def load_named_graph(name: str) -> Graph:
    """Load a graph from ``data/pebbling_product/graphs/<name>.json``.

    The loader trusts the JSON's ``edges`` and ``n`` and does not look at
    pebbling-number metadata. The validator still checks simplicity and
    connectivity.
    """
    path = GRAPH_DIR / f"{name}.json"
    with path.open() as fp:
        payload = json.load(fp)
    return make_graph(int(payload["n"]), payload["edges"], name=payload.get("name", name))


def load_metadata(name: str) -> dict:
    """Return the raw JSON metadata associated with ``name``."""
    path = GRAPH_DIR / f"{name}.json"
    with path.open() as fp:
        return json.load(fp)
