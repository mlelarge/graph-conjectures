"""Interaction graph J = H union G_flex for the score-window attack.

Background.  Each vertex v of a tournament T has a *score window*

    I_v = [d^-(v) - 2, d^-(v) + 2]

(clipped to [0, n-1]).  Every linear-forest ordering (LFO) of T must
place v inside I_v (see docs/score_window.md).  For an unordered pair
{u, v} two cases arise:

  * Forced pair:  I_u and I_v are disjoint.  Then the LFO order of u
    and v is determined: the vertex whose window is below comes first.
  * Flexible pair:  the windows overlap.  Either LFO order is possible
    from the score-window standpoint alone.

Define
  H        = directed graph of forced backedges (u -> v in T together
             with the forced LFO order placing v before u).
  G_flex   = undirected graph of flexible pairs.
  J        = H ∪ G_flex viewed as an undirected graph.

The decisive question (Width Conjecture in docs/J_width_conjecture.md):
when H is a linear forest (max degree <= 2, acyclic) and the score
windows are Hall-feasible, is tw(J) bounded by an absolute constant?

This module provides the construction primitives plus a
treewidth-measurement driver.  It deliberately does NOT bake in any
guess about the bound c; it just computes things.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass
from typing import Iterable, Sequence

import networkx as nx

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

Matrix = Sequence[Sequence[int]]


# ---------------------------------------------------------------------------
# Basic primitives
# ---------------------------------------------------------------------------

def indegrees(T: Matrix) -> list[int]:
    n = len(T)
    return [sum(int(T[u][v]) for u in range(n)) for v in range(n)]


def score_window(T: Matrix, v: int, radius: int = 2) -> tuple[int, int]:
    """Return (lo, hi) = the score window of v clipped to [0, n-1]."""
    n = len(T)
    d = sum(int(T[u][v]) for u in range(n))
    return (max(0, d - radius), min(n - 1, d + radius))


def score_windows(T: Matrix, radius: int = 2) -> list[tuple[int, int]]:
    return [score_window(T, v, radius) for v in range(len(T))]


def forced_pair_orientation(
    T: Matrix, u: int, v: int, radius: int = 2,
) -> str:
    """Return 'forced_u_before_v', 'forced_v_before_u', or 'flexible'."""
    lo_u, hi_u = score_window(T, u, radius)
    lo_v, hi_v = score_window(T, v, radius)
    if hi_u < lo_v:
        return "forced_u_before_v"
    if hi_v < lo_u:
        return "forced_v_before_u"
    return "flexible"


# ---------------------------------------------------------------------------
# H and G_flex
# ---------------------------------------------------------------------------

def build_H_and_Gflex(
    T: Matrix, radius: int = 2,
) -> tuple[nx.DiGraph, nx.Graph]:
    """Return (H, G_flex).

    H is a DiGraph: each arc (u -> v) is a *forced backedge*.  This
    means T has the arc u -> v, and score windows force v to come
    before u in every score-respecting order.

    G_flex is an undirected Graph: vertex set {0, .., n-1}, edge
    {u, v} iff I_u and I_v share at least one position.
    """
    n = len(T)
    H = nx.DiGraph()
    Gflex = nx.Graph()
    H.add_nodes_from(range(n))
    Gflex.add_nodes_from(range(n))
    windows = score_windows(T, radius)

    for u in range(n):
        for v in range(u + 1, n):
            lo_u, hi_u = windows[u]
            lo_v, hi_v = windows[v]
            if hi_u < lo_v:
                # forced: u first, v second.  Arc v -> u (if present)
                # is a forced backedge.
                if int(T[v][u]):
                    H.add_edge(v, u)
            elif hi_v < lo_u:
                if int(T[u][v]):
                    H.add_edge(u, v)
            else:
                Gflex.add_edge(u, v)
    return H, Gflex


def build_J(T: Matrix, radius: int = 2) -> nx.Graph:
    """Return J = H ∪ G_flex as an undirected graph on {0,..,n-1}."""
    H, Gflex = build_H_and_Gflex(T, radius)
    J = nx.Graph()
    J.add_nodes_from(range(len(T)))
    for u, v in H.edges():
        J.add_edge(u, v)
    for u, v in Gflex.edges():
        J.add_edge(u, v)
    return J


# ---------------------------------------------------------------------------
# Hall feasibility on the score windows
# ---------------------------------------------------------------------------

def hall_feasible(T: Matrix, radius: int = 2) -> bool:
    """True iff the score windows {I_v} admit an injective placement
    of all vertices into [0, n-1], i.e., for every position interval
    [l, r], at most r - l + 1 windows are contained in [l, r].

    Since all domains are intervals, checking all interval-of-positions
    suffices.
    """
    n = len(T)
    if n == 0:
        return True
    windows = score_windows(T, radius)
    for left in range(n):
        for right in range(left, n):
            covered = sum(1 for lo, hi in windows
                          if left <= lo and hi <= right)
            if covered > right - left + 1:
                return False
    return True


def max_active_window_count(T: Matrix, radius: int = 2) -> int:
    """Maximum number of score windows containing a common position."""
    n = len(T)
    windows = score_windows(T, radius)
    best = 0
    for p in range(n):
        best = max(best, sum(1 for lo, hi in windows if lo <= p <= hi))
    return best


def flex_treewidth_bound_from_hall(radius: int = 2) -> int:
    """Treewidth bound for the score-window overlap graph under Hall.

    For radius r, every window containing a position p is contained in
    [p-2r, p+2r].  Hall feasibility permits at most 4r+1 such windows.
    Interval graphs have treewidth omega-1, so the flexible graph has
    treewidth at most 4r.  For Path-FAS r=2, this is 8.
    """
    return 4 * radius


def refined_treewidth_bound(T: Matrix, radius: int = 2) -> int | None:
    """Return the proved bound tw(J), pw(J) <= 4r + 2|H|, if Hall holds.

    If Hall fails, the score-window feasibility pre-pass already rejects,
    so no width bound is relevant for the LFO decision algorithm.
    """
    if not hall_feasible(T, radius):
        return None
    H, _Gflex = build_H_and_Gflex(T, radius)
    return flex_treewidth_bound_from_hall(radius) + 2 * H.number_of_edges()


def refined_pathwidth_bound(T: Matrix, radius: int = 2) -> int | None:
    """Alias for the same bound, emphasizing the path-decomposition use."""
    return refined_treewidth_bound(T, radius)


def is_H_linear_forest(H: nx.DiGraph) -> bool:
    """True iff the underlying undirected graph of H is a linear forest
    (max degree <= 2 and acyclic)."""
    U = H.to_undirected()
    if any(d > 2 for _, d in U.degree()):
        return False
    # acyclic <=> forest
    return nx.is_forest(U)


# ---------------------------------------------------------------------------
# Width measurement
# ---------------------------------------------------------------------------

def treewidth_upper_bound(G: nx.Graph) -> int:
    """Return a treewidth upper bound via min-fill-in elimination."""
    if G.number_of_nodes() == 0:
        return 0
    tw, _ = nx.algorithms.approximation.treewidth_min_fill_in(G)
    return tw


def treewidth_min_degree(G: nx.Graph) -> int:
    if G.number_of_nodes() == 0:
        return 0
    tw, _ = nx.algorithms.approximation.treewidth_min_degree(G)
    return tw


def exact_treewidth(G: nx.Graph) -> int:
    """Exhaustive treewidth: tries all elimination orders up to ~10 nodes.

    For larger graphs this is exponential and should not be called; we
    fall back to the min-fill-in upper bound."""
    n = G.number_of_nodes()
    if n <= 1:
        return 0
    if n > 11:
        raise ValueError("exact_treewidth only supports n <= 11")
    # exhaustive over elimination orders is n! ; we do branch-and-bound.
    nodes = list(G.nodes())
    adj = {u: set(G.neighbors(u)) for u in nodes}
    best = [n - 1]  # trivial UB: clique-cover

    def recurse(remaining: set, cur_max: int):
        if cur_max >= best[0]:
            return
        if not remaining:
            best[0] = min(best[0], cur_max)
            return
        # Lower bound via min-degree among remaining
        for u in sorted(remaining):
            nbrs = adj[u] & remaining
            new_max = max(cur_max, len(nbrs))
            if new_max >= best[0]:
                continue
            # eliminate u: add clique on nbrs
            added: list[tuple[int, int]] = []
            nbrs_list = list(nbrs)
            for i in range(len(nbrs_list)):
                for j in range(i + 1, len(nbrs_list)):
                    x, y = nbrs_list[i], nbrs_list[j]
                    if y not in adj[x]:
                        adj[x].add(y)
                        adj[y].add(x)
                        added.append((x, y))
            remaining.remove(u)
            recurse(remaining, new_max)
            remaining.add(u)
            for x, y in added:
                adj[x].discard(y)
                adj[y].discard(x)

    recurse(set(remaining := set(nodes)), 0)
    return best[0]


def clique_lower_bound(G: nx.Graph) -> int:
    """tw(G) >= omega(G) - 1.  Returns omega - 1 from an exact max-clique
    on small graphs, else an approximation."""
    if G.number_of_nodes() == 0:
        return 0
    if G.number_of_nodes() <= 30:
        # exact
        # networkx find_cliques enumerates all maximal cliques
        omega = max((len(c) for c in nx.find_cliques(G)), default=0)
        return max(0, omega - 1)
    # approximation
    omega_lb = nx.algorithms.approximation.large_clique_size(G)
    return max(0, omega_lb - 1)


# ---------------------------------------------------------------------------
# A measurement record
# ---------------------------------------------------------------------------

@dataclass
class JWidthReport:
    name: str
    n: int
    hall_ok: bool
    H_is_linear_forest: bool
    H_edges: int
    Gflex_edges: int
    J_edges: int
    omega_J: int
    tw_lb: int  # omega(J) - 1
    tw_ub: int  # min-fill-in heuristic
    tw_exact: int | None  # only computed when n small

    def as_dict(self) -> dict:
        return {
            "name": self.name,
            "n": self.n,
            "hall_ok": self.hall_ok,
            "H_is_linear_forest": self.H_is_linear_forest,
            "H_edges": self.H_edges,
            "Gflex_edges": self.Gflex_edges,
            "J_edges": self.J_edges,
            "omega_J": self.omega_J,
            "tw_lb": self.tw_lb,
            "tw_ub": self.tw_ub,
            "tw_exact": self.tw_exact,
        }


def measure(T: Matrix, name: str = "", radius: int = 2,
            do_exact: bool = False) -> JWidthReport:
    H, Gflex = build_H_and_Gflex(T, radius)
    J = nx.Graph()
    J.add_nodes_from(range(len(T)))
    for u, v in H.edges():
        J.add_edge(u, v)
    for u, v in Gflex.edges():
        J.add_edge(u, v)
    omega = max((len(c) for c in nx.find_cliques(J)), default=0) if J.number_of_nodes() else 0
    tw_ub = treewidth_upper_bound(J)
    tw_exact: int | None = None
    if do_exact and J.number_of_nodes() <= 11:
        tw_exact = exact_treewidth(J)
    return JWidthReport(
        name=name,
        n=len(T),
        hall_ok=hall_feasible(T, radius),
        H_is_linear_forest=is_H_linear_forest(H),
        H_edges=H.number_of_edges(),
        Gflex_edges=Gflex.number_of_edges(),
        J_edges=J.number_of_edges(),
        omega_J=omega,
        tw_lb=max(0, omega - 1),
        tw_ub=tw_ub,
        tw_exact=tw_exact,
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _from_jsonl_iter(path: str) -> Iterable[Matrix]:
    with open(path) as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            d = json.loads(line)
            yield d["T"]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--T", help="Tournament as JSON matrix")
    parser.add_argument("--census", help="lfo_full_n7-style JSON dataset")
    parser.add_argument("--max-records", type=int, default=None)
    parser.add_argument("--exact", action="store_true")
    args = parser.parse_args()

    if args.T:
        T = json.loads(args.T)
        rep = measure(T, name="cli", do_exact=args.exact)
        print(json.dumps(rep.as_dict(), indent=2))
        return

    if args.census:
        data = json.load(open(args.census))
        n_done = 0
        for bucket in data["buckets"]:
            for rec in bucket["records"]:
                rep = measure(rec["T"], name=f"iso_{rec['iso_index']}",
                              do_exact=args.exact)
                d = rep.as_dict()
                d["has_lfo"] = rec.get("has_lfo")
                print(json.dumps(d))
                n_done += 1
                if args.max_records is not None and n_done >= args.max_records:
                    return
        return

    parser.error("must pass --T or --census")


if __name__ == "__main__":
    main()
