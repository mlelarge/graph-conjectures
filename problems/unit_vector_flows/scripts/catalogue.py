"""Catalogue iteration and snark filtering.

Reads graph6 catalogues (one graph per line, no header), canonicalises
the graph through ``_canonicalize`` so its graph6 hash is stable, and
classifies each entry. The standard external source for our purposes
is the cyclically 4-/5-edge-connected snark database from
Brinkmann–Goedgebeur–Häggkvist (snarkhunter / House of Graphs).

Usage::

    python scripts/catalogue.py path/to/snarks.g6 --filter snark
    python scripts/catalogue.py path/to/cubic.g6  --emit-jsonl > cubic.jsonl
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import sys
from dataclasses import dataclass
from typing import Iterator

import networkx as nx

from graphs import _canonicalize, from_graph6, to_graph6


@dataclass
class CatalogueEntry:
    index: int
    source: str
    graph6: str
    n: int
    m: int
    is_cubic: bool
    is_bridgeless: bool
    girth: int | None
    chromatic_index: int | None
    cyclic_edge_connectivity: int | None
    is_chi4_cubic_bridgeless: bool
    is_nontrivial_snark: bool
    sha1: str


def cyclic_edge_connectivity_at_most(G: nx.Graph, k: int) -> int | None:
    """Return the smallest size ``s <= k`` of an edge set whose removal
    disconnects G into components at least two of which contain a cycle,
    or ``None`` if no such cut of size ≤ k exists.

    A "cyclic edge cut" separates G into ≥ 2 components, each containing
    a cycle. The cyclic edge connectivity is the minimum size of such a
    cut. For cubic graphs of girth ≥ 5, the cubic-vertex 3-cuts are
    *trivial* (one side is a single vertex, no cycle), so they do NOT
    count as cyclic cuts.

    Implementation: brute enumeration of all edge subsets of size up to
    k. For typical graph sizes in this project (m ≤ ~50), C(m,4) ≈ 230k
    is acceptable.
    """
    from itertools import combinations

    edges = list(G.edges())
    m = len(edges)

    def has_cycle(comp_nodes: set, removed: set) -> bool:
        # A connected component on `comp_nodes` (nodes) with the edges of
        # G restricted to it (minus `removed`) contains a cycle iff
        # |E| >= |V|.
        v = len(comp_nodes)
        e = 0
        for u, w in G.edges(comp_nodes):
            if (u, w) in removed or (w, u) in removed:
                continue
            if u in comp_nodes and w in comp_nodes:
                e += 1
        return e >= v

    for size in range(1, k + 1):
        for cut in combinations(range(m), size):
            removed_edges = {edges[i] for i in cut}
            removed_set = removed_edges | {(v, u) for (u, v) in removed_edges}
            H = G.copy()
            H.remove_edges_from(removed_edges)
            if nx.is_connected(H):
                continue
            comps = [set(c) for c in nx.connected_components(H)]
            cyclic_count = sum(1 for c in comps if has_cycle(c, removed_set))
            if cyclic_count >= 2:
                return size
    return None


def is_three_edge_colourable_sat(G: nx.Graph) -> bool:
    """SAT-based decision for 3-edge-colourability.

    Encodes the colouring as a CNF in the variables x_{e,c} (edge e gets
    colour c ∈ {0,1,2}): each edge picks at least one and at most one
    colour, and incident edges must have distinct colours. Decided by
    Glucose 4. For ``n = 24`` cubic graphs (m = 36, ≈ 110 vars and a few
    hundred clauses) the solver answers in milliseconds.
    """
    from pysat.formula import CNF
    from pysat.solvers import Glucose4

    edges = list(G.edges())
    m = len(edges)
    if m == 0:
        return True

    def var(e: int, c: int) -> int:
        return e * 3 + c + 1

    cnf = CNF()
    for e in range(m):
        cnf.append([var(e, c) for c in range(3)])
        for c1 in range(3):
            for c2 in range(c1 + 1, 3):
                cnf.append([-var(e, c1), -var(e, c2)])

    incidence: dict = {v: [] for v in G.nodes()}
    for k, (u, v) in enumerate(edges):
        incidence[u].append(k)
        incidence[v].append(k)
    for inc_edges in incidence.values():
        for i in range(len(inc_edges)):
            for j in range(i + 1, len(inc_edges)):
                for c in range(3):
                    cnf.append([-var(inc_edges[i], c), -var(inc_edges[j], c)])

    with Glucose4(bootstrap_with=cnf.clauses) as s:
        return bool(s.solve())


def is_three_edge_colourable(G: nx.Graph, *, time_budget_s: float | None = None) -> bool:
    """Backtracking 3-edge-colouring decision. Cubic-graph oriented; returns
    True if a proper 3-edge-colouring exists. ``time_budget_s`` is a soft
    counter on recursion calls (rough proxy for time).
    """
    edges = list(G.edges())
    m = len(edges)
    incidence: dict = {v: [] for v in G.nodes()}
    for k, (u, v) in enumerate(edges):
        incidence[u].append(k)
        incidence[v].append(k)
    colour = [0] * m
    counter = [0]
    budget = None
    if time_budget_s is not None:
        budget = int(1e6 * time_budget_s)

    def recur(i: int) -> bool:
        if budget is not None:
            counter[0] += 1
            if counter[0] > budget:
                raise TimeoutError("3-edge-colouring search exceeded budget")
        if i == m:
            return True
        u, v = edges[i]
        used = set()
        for k in incidence[u]:
            if colour[k]:
                used.add(colour[k])
        for k in incidence[v]:
            if colour[k]:
                used.add(colour[k])
        for c in (1, 2, 3):
            if c not in used:
                colour[i] = c
                if recur(i + 1):
                    return True
                colour[i] = 0
        return False

    return recur(0)


def classify(G: nx.Graph, *, source: str, index: int) -> CatalogueEntry:
    H = _canonicalize(G)
    g6 = to_graph6(H)
    cubic = all(d == 3 for _, d in H.degree())
    bridgeless = nx.edge_connectivity(H) >= 2 if H.number_of_nodes() > 1 else False
    girth = nx.girth(H) if H.number_of_edges() > 0 else None
    chi: int | None = None
    chi4 = False
    if cubic and bridgeless:
        three = is_three_edge_colourable_sat(H)
        chi = 3 if three else 4
        chi4 = (chi == 4)

    cyclic_lambda: int | None = None
    nontrivial = False
    if chi4 and girth is not None and girth >= 5:
        # Probe for cyclic cuts of size 1, 2, 3. If none exists, the graph
        # is cyclically 4-edge-connected. If any exists, store its size.
        small_cyclic_cut = cyclic_edge_connectivity_at_most(H, 3)
        if small_cyclic_cut is None:
            cyclic_lambda = 4  # at least; tight value not needed for this filter
            nontrivial = True
        else:
            cyclic_lambda = small_cyclic_cut
            nontrivial = False

    return CatalogueEntry(
        index=index,
        source=source,
        graph6=g6,
        n=H.number_of_nodes(),
        m=H.number_of_edges(),
        is_cubic=cubic,
        is_bridgeless=bridgeless,
        girth=girth,
        chromatic_index=chi,
        cyclic_edge_connectivity=cyclic_lambda,
        is_chi4_cubic_bridgeless=chi4,
        is_nontrivial_snark=nontrivial,
        sha1=hashlib.sha1(g6.encode("ascii")).hexdigest(),
    )


def iter_graph6_file(path: pathlib.Path | str) -> Iterator[tuple[int, str]]:
    """Iterate ``(line_index, graph6_string)`` pairs from a graph6 file or
    from stdin (``path == "-"``). Lines starting with ``>>`` (file
    headers) and blank lines are skipped."""
    if str(path) == "-":
        stream = sys.stdin
        close = False
    else:
        stream = pathlib.Path(path).open("r", encoding="ascii")
        close = True
    try:
        for i, line in enumerate(stream):
            line = line.strip()
            if not line or line.startswith(">>"):
                continue
            yield i, line
    finally:
        if close:
            stream.close()


def iter_catalogue(path: pathlib.Path | str) -> Iterator[CatalogueEntry]:
    src = str(path)
    for i, g6 in iter_graph6_file(path):
        try:
            G = from_graph6(g6)
        except Exception as exc:
            print(f"warning: line {i}: failed to parse graph6 ({exc})", file=sys.stderr)
            continue
        yield classify(G, source=src, index=i)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "path",
        help="graph6 catalogue file path, or '-' to read from stdin",
    )
    ap.add_argument(
        "--filter",
        choices=("none", "cubic", "cubic-bridgeless", "chi4", "nontrivial-snark"),
        default="nontrivial-snark",
        help=(
            "chi4: cubic, bridgeless, chromatic-index 4 (loose 'snark'). "
            "nontrivial-snark: chi4 + girth >= 5 + cyclically 4-edge-connected."
        ),
    )
    ap.add_argument("--emit-jsonl", action="store_true", help="write JSONL to stdout")
    ap.add_argument("--limit", type=int, default=None)
    args = ap.parse_args()

    n_total = 0
    n_kept = 0
    for entry in iter_catalogue(args.path):
        n_total += 1
        keep = {
            "none": True,
            "cubic": entry.is_cubic,
            "cubic-bridgeless": entry.is_cubic and entry.is_bridgeless,
            "chi4": entry.is_chi4_cubic_bridgeless,
            "nontrivial-snark": entry.is_nontrivial_snark,
        }[args.filter]
        if not keep:
            continue
        n_kept += 1
        if args.emit_jsonl:
            print(json.dumps(entry.__dict__), flush=True)
        else:
            print(
                f"{entry.index:5d} n={entry.n:3d} m={entry.m:3d} "
                f"cubic={entry.is_cubic} brless={entry.is_bridgeless} "
                f"girth={entry.girth} chi'={entry.chromatic_index} "
                f"cyc_lambda={entry.cyclic_edge_connectivity} "
                f"chi4={entry.is_chi4_cubic_bridgeless} "
                f"nts={entry.is_nontrivial_snark} g6={entry.graph6}"
            )
        if args.limit is not None and n_kept >= args.limit:
            break
    print(f"\n# kept {n_kept} of {n_total}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
