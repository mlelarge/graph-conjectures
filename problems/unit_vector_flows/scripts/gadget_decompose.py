r"""Inverse gadget operations: detect and undo triangle blow-ups and
3-edge-cut dot products on cubic graphs.

[gadget_closure.md](../docs/gadget_closure.md) gives a constructive
forward direction: starting from the 3 247 certified nontrivial
snarks at $n \le 28$, applying triangle blow-up and 3-edge-cut dot
product yields cubic graphs with explicit $S^2$-flow extensions. This
module gives the **inverse direction**: given a cubic graph $G$, ask
whether $G$ decomposes as a gadget tree over the certified base.

Operations:

1. **Inverse triangle reduction.** A triangle $\{u_1, u_2, u_3\}$ in
   $G$ is *contractible* iff each $u_i$ has exactly one external
   neighbour $e_i$ and $e_1, e_2, e_3$ are pairwise distinct (else the
   contraction creates parallel edges or self-loops). Contraction
   removes the three triangle vertices, adds one new vertex $v$
   adjacent to $\{e_1, e_2, e_3\}$, and returns a cubic graph with
   $|V(G)| - 2$ vertices.

2. **Inverse 3-edge-cut dot product.** A *cyclic 3-edge cut*
   $C = \{e_1, e_2, e_3\} \subset E(G)$ disconnects $G$ into two
   components $G_a, G_b$ each containing a cycle. Add a fresh vertex
   $v_a$ on the $G_a$ side connected to the 3 cut-edge endpoints in
   $G_a$, and similarly $v_b$ on $G_b$. The result is a pair of cubic
   graphs whose dot product (at the new vertices) is $G$.

A graph is **decomposable** over a base set $\mathcal{B}$ iff it is in
$\mathcal{B}$, or it admits one of the two inverse operations whose
output pieces are themselves decomposable.

Functions:

  - :func:`find_contractible_triangles(G)`
  - :func:`contract_triangle(G, triangle)`
  - :func:`find_cyclic_3_cuts(G)`
  - :func:`split_at_3_cut(G, cut)`
  - :func:`decompose_step(G)` — one-step options
  - :func:`decompose_tree(G, base, memo)` — full DP search
"""
from __future__ import annotations

from dataclasses import dataclass, field
import itertools
import shutil
import subprocess

import networkx as nx

from graphs import _canonicalize


_LABELG_PATH: str | None = shutil.which("labelg")


def canonical_graph6(G: nx.Graph) -> str:
    """Return the **canonical** (nauty-style) graph6 string of $G$.

    Two graphs are isomorphic iff their canonical graph6 strings are
    equal. Falls back to the sorted-relabel form of
    :func:`graphs._canonicalize` if ``labelg`` from nauty is not on
    PATH (then graph6 only distinguishes graphs up to vertex labelling,
    not isomorphism — a strictly weaker invariant).
    """
    H = _canonicalize(G)
    raw = nx.to_graph6_bytes(H, header=False).decode().strip()
    if _LABELG_PATH is None:
        return raw
    proc = subprocess.run(
        [_LABELG_PATH, "-q"],
        input=raw + "\n",
        capture_output=True,
        text=True,
        check=True,
    )
    return proc.stdout.strip()


# ---------------------------------------------------------------------------
# Graph hash (graph6)
# ---------------------------------------------------------------------------


def graph6_of(G: nx.Graph) -> str:
    """Canonical (nauty) graph6 string for $G$. Equivalent graphs have
    equal hashes regardless of vertex labelling."""
    return canonical_graph6(G)


# ---------------------------------------------------------------------------
# Inverse triangle reduction
# ---------------------------------------------------------------------------


def find_contractible_triangles(G: nx.Graph) -> list[tuple[int, int, int]]:
    """Return every triangle in $G$ whose contraction would yield a
    simple cubic graph.

    For a cubic graph, a triangle $\\{u_1, u_2, u_3\\}$ requires each
    $u_i$ to have one external neighbour $e_i$. We further require
    that $e_1, e_2, e_3$ are pairwise distinct and none equals any
    $u_j$ (which would imply an edge to a fellow triangle vertex
    outside the triangle structure).
    """
    triangles: list[tuple[int, int, int]] = []
    nodes = sorted(G.nodes())
    for u1, u2, u3 in itertools.combinations(nodes, 3):
        if not (G.has_edge(u1, u2) and G.has_edge(u1, u3) and G.has_edge(u2, u3)):
            continue
        externals: list[int] = []
        ok = True
        for u in (u1, u2, u3):
            nbrs = [w for w in G.neighbors(u) if w not in (u1, u2, u3)]
            if len(nbrs) != 1:
                ok = False
                break
            externals.append(nbrs[0])
        if not ok:
            continue
        # Externals must be pairwise distinct (else parallel edges on
        # contraction).
        if len(set(externals)) != 3:
            continue
        triangles.append((u1, u2, u3))
    return triangles


def contract_triangle(
    G: nx.Graph, triangle: tuple[int, int, int]
) -> tuple[nx.Graph, dict[int, int]]:
    """Contract a contractible triangle and return the reduced cubic
    graph plus the relabel map.

    The new vertex is created with a label larger than any in $G$ so
    the canonical relabelling is predictable. Returns
    ``(G_reduced, relabel)`` where ``relabel`` maps every surviving
    label (vertices in $G \\setminus \\{u_1, u_2, u_3\\}$ plus the new
    vertex) to the canonical integer label in $G_{\\text{reduced}}$.
    """
    u1, u2, u3 = triangle
    externals = []
    for u in (u1, u2, u3):
        nbrs = [w for w in G.neighbors(u) if w not in triangle]
        externals.append(nbrs[0])
    e1, e2, e3 = externals
    if len({e1, e2, e3}) != 3:
        raise ValueError("triangle not contractible (external coincidences)")

    H = nx.Graph()
    for u in G.nodes():
        if u not in triangle:
            H.add_node(u)
    for u, w in G.edges():
        if u in triangle or w in triangle:
            continue
        H.add_edge(u, w)
    v_new = max(G.nodes()) + 1
    H.add_node(v_new)
    H.add_edge(v_new, e1)
    H.add_edge(v_new, e2)
    H.add_edge(v_new, e3)
    G_red = _canonicalize(H)
    sorted_nodes = sorted(H.nodes())
    relabel = {n_: i for i, n_ in enumerate(sorted_nodes)}
    return G_red, relabel


# ---------------------------------------------------------------------------
# Inverse cyclic 3-edge cut (dot product)
# ---------------------------------------------------------------------------


def _has_cycle_in_component(G: nx.Graph, nodes: set[int]) -> bool:
    """Does the induced subgraph on the connected component ``nodes``
    contain a cycle?"""
    nv = len(nodes)
    ne = sum(1 for u, w in G.edges() if u in nodes and w in nodes)
    return ne >= nv


def find_cyclic_3_cuts(
    G: nx.Graph, *, max_cuts: int | None = None
) -> list[tuple[tuple[int, int], ...]]:
    """Return cyclic 3-edge cuts: subsets of 3 edges whose removal
    disconnects $G$ into exactly two components, each containing a
    cycle.

    Brute over $\\binom{m}{3}$ — feasible for $m \\le ~60$.
    """
    edges = [tuple(sorted(e)) for e in G.edges()]
    m = len(edges)
    out: list[tuple] = []
    for idx in itertools.combinations(range(m), 3):
        cut = tuple(edges[i] for i in idx)
        H = G.copy()
        H.remove_edges_from(cut)
        if nx.is_connected(H):
            continue
        comps = [set(c) for c in nx.connected_components(H)]
        if len(comps) != 2:
            continue
        if not all(_has_cycle_in_component(H, c) for c in comps):
            continue
        out.append(cut)
        if max_cuts is not None and len(out) >= max_cuts:
            break
    return out


def split_at_3_cut(
    G: nx.Graph, cut: tuple[tuple[int, int], ...]
) -> tuple[nx.Graph, nx.Graph]:
    """Split $G$ along a cyclic 3-edge cut and return the two cubic
    pieces obtained by adding a fresh degree-3 vertex on each side.
    """
    cut_edges = [tuple(sorted(e)) for e in cut]
    H = G.copy()
    H.remove_edges_from(cut_edges)
    comps = [set(c) for c in nx.connected_components(H)]
    if len(comps) != 2:
        raise ValueError(f"cut does not split into exactly 2 components ({len(comps)})")
    comp_of = {v: 0 if v in comps[0] else 1 for v in G.nodes()}

    # Identify the 3 boundary vertices on each side.
    boundary = ([], [])  # boundary[0] = vertices on side 0 with cut endpoints, in cut order
    for (a, b) in cut_edges:
        if comp_of[a] == 0:
            boundary[0].append(a)
            boundary[1].append(b)
        else:
            boundary[0].append(b)
            boundary[1].append(a)

    pieces: list[nx.Graph] = []
    for side in (0, 1):
        nodes = sorted(comps[side])
        H_side = nx.Graph()
        H_side.add_nodes_from(nodes)
        for u, w in G.edges():
            if u in nodes and w in nodes:
                H_side.add_edge(u, w)
        new_label = max(nodes) + 1
        H_side.add_node(new_label)
        for b in boundary[side]:
            H_side.add_edge(new_label, b)
        pieces.append(_canonicalize(H_side))
    return pieces[0], pieces[1]


# ---------------------------------------------------------------------------
# One-step decomposition options
# ---------------------------------------------------------------------------


@dataclass
class DecompStep:
    op: str                              # "BASE", "TRIANGLE", "DOT"
    children: list[str] = field(default_factory=list)   # graph6 of pieces
    detail: dict = field(default_factory=dict)


def decompose_step(G: nx.Graph) -> list[DecompStep]:
    """Return every one-step decomposition option for $G$ as
    :class:`DecompStep` records.

    The empty list means $G$ is irreducible under the two operations.
    """
    options: list[DecompStep] = []

    for tri in find_contractible_triangles(G):
        G_red, _ = contract_triangle(G, tri)
        options.append(
            DecompStep(op="TRIANGLE", children=[graph6_of(G_red)],
                       detail={"triangle": tri})
        )

    for cut in find_cyclic_3_cuts(G):
        try:
            G_a, G_b = split_at_3_cut(G, cut)
        except ValueError:
            continue
        options.append(
            DecompStep(op="DOT",
                       children=[graph6_of(G_a), graph6_of(G_b)],
                       detail={"cut": cut})
        )

    return options


# ---------------------------------------------------------------------------
# DP over graph6: full decomposition tree search
# ---------------------------------------------------------------------------


@dataclass
class DecompTree:
    op: str
    graph6: str
    children: list["DecompTree"] = field(default_factory=list)

    def leaves(self) -> list[str]:
        if not self.children:
            return [self.graph6]
        out: list[str] = []
        for c in self.children:
            out.extend(c.leaves())
        return out

    def depth(self) -> int:
        if not self.children:
            return 0
        return 1 + max(c.depth() for c in self.children)


def decompose_tree(
    G: nx.Graph,
    base: frozenset[str],
    *,
    memo: dict[str, DecompTree | None] | None = None,
    max_depth: int = 12,
    _depth: int = 0,
) -> DecompTree | None:
    """Return a full decomposition tree of $G$ whose leaves all lie in
    ``base``, or ``None`` if no such tree exists.

    Memoised over graph6 strings to avoid revisiting subproblems.
    """
    if memo is None:
        memo = {}
    g6 = graph6_of(G)
    if g6 in memo:
        return memo[g6]
    if g6 in base:
        tree = DecompTree(op="BASE", graph6=g6)
        memo[g6] = tree
        return tree
    if _depth >= max_depth:
        memo[g6] = None
        return None
    # Mark as in-progress to avoid cycles
    memo[g6] = None
    options = decompose_step(G)
    for opt in options:
        child_trees: list[DecompTree] = []
        ok = True
        for child_g6 in opt.children:
            if child_g6 in base:
                child_trees.append(DecompTree(op="BASE", graph6=child_g6))
                continue
            if child_g6 in memo and memo[child_g6] is None:
                ok = False
                break
            # Need to rebuild the child graph from g6 for recursion.
            child_G = nx.from_graph6_bytes(child_g6.encode())
            sub = decompose_tree(
                child_G, base, memo=memo,
                max_depth=max_depth, _depth=_depth + 1,
            )
            if sub is None:
                ok = False
                break
            child_trees.append(sub)
        if ok:
            tree = DecompTree(op=opt.op, graph6=g6, children=child_trees)
            memo[g6] = tree
            return tree
    memo[g6] = None
    return None
