"""Directed interaction graph J+ for the Path-FAS score-window attack.

J = H union G_flex deliberately forgets arc directions on flexible
pairs.  J+ keeps them:

  * forced backedges are directed as backedges in H;
  * flexible pairs are directed by the tournament arc.

The purpose of this module is diagnostic.  It supplies small directed
width proxies that can be computed on the minimal-NO catalogues:
strong-component size and exact directed feedback-vertex number for
n <= 10.  These are not directed treewidth, but they are hard lower
signals for any DAG-like directed DP.
"""
from __future__ import annotations

import argparse
import itertools
import json
import os
import sys
from collections import Counter
from typing import Sequence

import networkx as nx

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from interaction_graph import build_H_and_Gflex  # noqa: E402


Matrix = Sequence[Sequence[int]]


def build_Jplus(T: Matrix, radius: int = 2) -> nx.DiGraph:
    """Return directed J+ with edge attribute kind in {'H', 'flex'}."""
    H, Gflex = build_H_and_Gflex(T, radius)
    D = nx.DiGraph()
    D.add_nodes_from(range(len(T)))
    for u, v in H.edges():
        D.add_edge(u, v, kind="H")
    for u, v in Gflex.edges():
        if int(T[u][v]):
            D.add_edge(u, v, kind="flex")
        else:
            D.add_edge(v, u, kind="flex")
    return D


def largest_strong_component_size(D: nx.DiGraph) -> int:
    return max((len(c) for c in nx.strongly_connected_components(D)), default=0)


def exact_feedback_vertex_number(D: nx.DiGraph, max_n: int = 10) -> int:
    """Minimum vertices to delete to make D acyclic.

    Exponential; intended for the n <= 9 minimal-NO catalogues.
    """
    n = D.number_of_nodes()
    if n > max_n:
        raise ValueError(f"exact feedback vertex number only supports n <= {max_n}")
    nodes = list(D.nodes())
    if nx.is_directed_acyclic_graph(D):
        return 0
    for r in range(1, n + 1):
        for removed in itertools.combinations(nodes, r):
            keep = set(nodes) - set(removed)
            if nx.is_directed_acyclic_graph(D.subgraph(keep)):
                return r
    return n


def jplus_report(T: Matrix, radius: int = 2, exact_fvs: bool = True) -> dict:
    D = build_Jplus(T, radius)
    H_edges = sum(1 for _u, _v, d in D.edges(data=True) if d["kind"] == "H")
    flex_edges = D.number_of_edges() - H_edges
    out = {
        "n": D.number_of_nodes(),
        "arcs": D.number_of_edges(),
        "H_arcs": H_edges,
        "flex_arcs": flex_edges,
        "is_dag": nx.is_directed_acyclic_graph(D),
        "strong_components": nx.number_strongly_connected_components(D),
        "largest_scc": largest_strong_component_size(D),
    }
    if exact_fvs and D.number_of_nodes() <= 10:
        out["feedback_vertex_number"] = exact_feedback_vertex_number(D)
    else:
        out["feedback_vertex_number"] = None
    return out


def catalogue_report(path: str, max_records: int | None = None) -> dict:
    data = json.load(open(path))
    rows = []
    for rec in data["records"]:
        rows.append(jplus_report(rec["T"]))
        if max_records is not None and len(rows) >= max_records:
            break
    return {
        "path": path,
        "records": len(rows),
        "largest_scc_hist": dict(Counter(r["largest_scc"] for r in rows)),
        "fvs_hist": dict(Counter(r["feedback_vertex_number"] for r in rows)),
        "dag_count": sum(1 for r in rows if r["is_dag"]),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--T", help="Tournament as JSON matrix")
    parser.add_argument("--catalogue", help="minimal_no_obstruction_catalogue JSON")
    parser.add_argument("--max-records", type=int, default=None)
    args = parser.parse_args()
    if args.T:
        print(json.dumps(jplus_report(json.loads(args.T)), indent=2))
        return
    if args.catalogue:
        print(json.dumps(catalogue_report(args.catalogue, args.max_records), indent=2))
        return
    parser.error("pass --T or --catalogue")


if __name__ == "__main__":
    main()
