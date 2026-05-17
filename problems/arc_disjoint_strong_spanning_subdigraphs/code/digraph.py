"""Minimal digraph data structure built on networkx.MultiDiGraph.

Provides only the predicates and primitives the SAD verifier needs:
 - strong connectivity decision and SCC extraction;
 - arc-connectivity via repeated max-flow (used as a sanity gate before
   spending time on the optimizer);
 - Eulerianness;
 - directed cut extraction (out-cut for a vertex subset).

The verifier code uses these and nothing else; the rest of the verifier never
touches networkx internals directly. That makes it easy to swap out the
graph backend later without changing the optimizer code.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Hashable, Iterable, Iterator

import networkx as nx


Vertex = Hashable
ArcKey = tuple[Vertex, Vertex, int]  # (u, v, k) where k is the parallel-arc key


@dataclass
class Digraph:
    """Thin wrapper around `networkx.MultiDiGraph` with verifier-friendly API."""

    G: nx.MultiDiGraph

    @classmethod
    def from_arcs(
        cls, vertices: Iterable[Vertex], arcs: Iterable[tuple[Vertex, Vertex]]
    ) -> "Digraph":
        G = nx.MultiDiGraph()
        G.add_nodes_from(vertices)
        for u, v in arcs:
            G.add_edge(u, v)
        return cls(G=G)

    # -- basic ----------------------------------------------------------------

    def vertices(self) -> list[Vertex]:
        return list(self.G.nodes())

    def n(self) -> int:
        return self.G.number_of_nodes()

    def arcs(self) -> list[ArcKey]:
        return [(u, v, k) for u, v, k in self.G.edges(keys=True)]

    def m(self) -> int:
        return self.G.number_of_edges()

    def out_neighbors(self, v: Vertex) -> Iterator[Vertex]:
        return iter(self.G.successors(v))

    # -- strong connectivity --------------------------------------------------

    def is_strongly_connected(self) -> bool:
        if self.n() == 0:
            return False
        if self.n() == 1:
            return True
        return nx.is_strongly_connected(self.G)

    def strongly_connected_components(self) -> list[set[Vertex]]:
        return [set(c) for c in nx.strongly_connected_components(self.G)]

    # -- arc-connectivity ----------------------------------------------------

    def arc_connectivity(self) -> int:
        """Minimum number of arcs to delete to destroy strong connectivity.

        Computed via repeated max-flow on a capacitated simple-DiGraph
        projection (parallel arcs collapsed into integer capacities). We
        fix a root r and compute min `r -> v` and `v -> r` cuts for every
        v != r; the minimum over those is the arc-connectivity.

        Note: `networkx.edge_connectivity` does NOT respect capacity
        attributes, so we cannot delegate to it for multigraphs.
        """
        if self.n() < 2:
            return 0
        if not self.is_strongly_connected():
            return 0
        simple = nx.DiGraph()
        simple.add_nodes_from(self.G.nodes())
        cap: dict[tuple[Vertex, Vertex], int] = {}
        for u, v in self.G.edges():
            cap[(u, v)] = cap.get((u, v), 0) + 1
        for (u, v), c in cap.items():
            simple.add_edge(u, v, capacity=c)
        nodes = list(simple.nodes())
        r = nodes[0]
        best = float("inf")
        for v in nodes[1:]:
            best = min(best, nx.maximum_flow_value(simple, r, v))
            best = min(best, nx.maximum_flow_value(simple, v, r))
            if best == 0:
                break
        return int(best)

    # -- Eulerian ------------------------------------------------------------

    def is_eulerian(self) -> bool:
        """An Eulerian digraph: connected (in the underlying sense) plus
        in-degree(v) == out-degree(v) for every v."""
        if not self.is_strongly_connected():
            return False
        for v in self.G.nodes():
            if self.G.in_degree(v) != self.G.out_degree(v):
                return False
        return True

    # -- cuts ----------------------------------------------------------------

    def out_cut(self, X: Iterable[Vertex]) -> list[ArcKey]:
        """Return delta^+(X), the multiset of arcs with tail in X and head outside."""
        Xset = set(X)
        return [
            (u, v, k)
            for u, v, k in self.G.edges(keys=True)
            if u in Xset and v not in Xset
        ]

    def out_cut_size(self, X: Iterable[Vertex]) -> int:
        return len(self.out_cut(X))

    # -- sub-digraph for a subset of arcs ------------------------------------

    def subdigraph_on_arcs(self, arcs: Iterable[ArcKey]) -> "Digraph":
        H = nx.MultiDiGraph()
        H.add_nodes_from(self.G.nodes())
        for u, v, k in arcs:
            H.add_edge(u, v, key=k)
        return Digraph(G=H)

    # -- arc reversal --------------------------------------------------------

    def arc_reverse(self) -> "Digraph":
        """Return the digraph with every arc reversed.

        Multiplicities are preserved (each parallel copy of u -> v becomes
        one copy of v -> u). The vertex set is preserved.
        """
        H = nx.MultiDiGraph()
        H.add_nodes_from(self.G.nodes())
        for u, v in self.G.edges():
            H.add_edge(v, u)
        return Digraph(G=H)


def arc_reverse(D: "Digraph") -> "Digraph":
    """Standalone alias for `Digraph.arc_reverse`; takes (V, A) to (V, A^R)."""
    return D.arc_reverse()


# -- convenience predicates used by callers ------------------------------------


def is_strongly_connected_arcs(
    vertices: Iterable[Vertex], arcs: Iterable[ArcKey]
) -> bool:
    H = nx.MultiDiGraph()
    H.add_nodes_from(vertices)
    for u, v, k in arcs:
        H.add_edge(u, v, key=k)
    if H.number_of_nodes() < 2:
        return H.number_of_nodes() == 1
    return nx.is_strongly_connected(H)


def find_violated_cut(
    vertices: list[Vertex], arcs: list[ArcKey]
) -> set[Vertex] | None:
    """If the (V, arcs) subdigraph is not strongly connected, return a nonempty
    proper subset X of V with delta^+(X) empty. Otherwise return None.

    Used by the ILP lazy callback to extract a violated cut from an integer
    coloring. Picking a leaf SCC in the condensation gives an X with no
    outgoing arcs in this color, hence a directly violated cut inequality.
    """
    H = nx.MultiDiGraph()
    H.add_nodes_from(vertices)
    for u, v, k in arcs:
        H.add_edge(u, v, key=k)
    if H.number_of_nodes() < 2:
        return None
    if nx.is_strongly_connected(H):
        return None
    # condensation: DAG of SCCs, pick any SCC with no outgoing arcs to other
    # SCCs (a sink), then X = V \ S has delta^+(X) empty under "color".
    # Equivalently, the source SCC S in the condensation has delta^+(S) empty.
    cond = nx.condensation(H)
    # source SCCs (out-degree 0 in the *reversed* condensation = SCCs that no
    # other SCC points to). But we want X with no out-going arcs in this
    # color. That is: pick a sink SCC of the condensation; then X = V \ S has
    # no out-arcs (because S is a sink, no arcs leave V \ S into S). Wait —
    # arcs from X = V\S go to S only via... none, since S is a sink so all
    # arcs into S are *from* X, not the other way. We want arcs *leaving* X,
    # which go into V\X = S. So delta^+(X) contains all arcs from V\S to S,
    # which exist (S is reachable). So that's not a violated cut.
    #
    # Correct choice: pick a *source* SCC S of the condensation. Then
    # delta^-(S) is empty in H, equivalently delta^+(V \ S) is empty.
    # Take X = V \ S. Then delta^+(X) = 0 in this color, violating the
    # red-cover (or blue-cover) inequality.
    sources = [n for n in cond.nodes() if cond.in_degree(n) == 0]
    if not sources:
        return None
    S = set(cond.nodes[sources[0]]["members"])
    X = set(vertices) - S
    if not X or X == set(vertices):
        # degenerate: condensation has a single node, but H not strong; this
        # only happens if H has zero vertices or one isolated vertex with no
        # self-loop. Handled by the n<2 check above.
        return None
    return X
