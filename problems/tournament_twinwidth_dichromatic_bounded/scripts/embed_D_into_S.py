"""Embedding search for the literature-reduction proposal (arXiv:2602.09863).

Tests the proposal's falsifiable prediction WITHOUT the (absent) paper PDF:
the D_n tower D_n = Delta(D_{n-1}, D_{n-1}, D_1) is fully specified by the
recursion in the proposal, so we can directly ask:

  For each k, what is the largest n with D_n an INDUCED subtournament of S_k?

A tournament is determined by its arc directions on every pair, so "induced
subtournament" = induced sub-DiGraph isomorphism (an injective vertex map that
preserves the arc on EVERY pair, both presence and direction).  We use
networkx VF2 induced subgraph monomorphism on the DiGraph (which, since both
host and pattern have exactly one arc per pair among the chosen vertices, is
exactly induced subtournament containment).

CONFIRM (proposal): largest embeddable D_n grows with k.
KILL (proposal):    largest embeddable D_n stays BOUNDED while omegaVec(S_k)
                    independently keeps climbing.

Prints REAL results only.
"""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import networkx as nx
import constructions as C
import core


def to_digraph(n, arcs):
    g = nx.DiGraph()
    g.add_nodes_from(range(n))
    g.add_edges_from(arcs)
    return g


def contains_induced(host, pattern):
    """True iff `pattern` (a tournament DiGraph) is an INDUCED sub-tournament of
    `host` (a tournament DiGraph).  For tournaments, an injective vertex map f
    with: for every ordered pair (a,b) of pattern vertices, arc a->b in pattern
    IFF arc f(a)->f(b) in host.  Since both are tournaments, a subgraph
    monomorphism that preserves all present arcs of the pattern AND whose image
    induces the same arc directions is exactly induced containment.  VF2
    subgraph_is_isomorphic with the induced semantics does this when we match the
    pattern as an INDUCED subgraph: use GraphMatcher.subgraph_monomorphisms is
    non-induced; instead enumerate induced via vf2 'subgraph_is_isomorphic' on
    the host restricted -- but the clean exact route for tournaments is: a
    pattern P on p vertices is an induced subtournament of host H on h vertices
    iff some injection phi with arc-direction agreement on all pairs.  We test
    this with networkx DiGraphMatcher.subgraph_is_isomorphic, which checks
    induced subgraph isomorphism (node-induced)."""
    gm = nx.algorithms.isomorphism.DiGraphMatcher(host, pattern)
    return gm.subgraph_is_isomorphic()


def largest_D_in_S(k, n_max=8):
    host = to_digraph(*C.S(k))
    best = 0
    detail = {}
    for n in range(1, n_max + 1):
        pat = to_digraph(*C.D(n))
        if pat.number_of_nodes() > host.number_of_nodes():
            detail[n] = "pattern-too-big"
            break
        ok = contains_induced(host, pat)
        detail[n] = ok
        if ok:
            best = n
        else:
            # D_n monotone in induced-containment? Not guaranteed, but record.
            break
    return best, detail


def main():
    out = {"note": "D_n=Delta(D_{n-1},D_{n-1},D_1), D_1=pt; |D_n|=1,3,7,15,31",
           "D_sizes": {}, "S_sizes": {}, "largest_D_induced_in_S": {},
           "detail": {}}
    for n in range(1, 6):
        nn, _ = C.D(n)
        out["D_sizes"][n] = nn
    for k in range(2, 6):
        nn, _ = C.S(k)
        out["S_sizes"][k] = nn
    for k in range(2, 6):
        best, detail = largest_D_in_S(k, n_max=6)
        out["largest_D_induced_in_S"][k] = best
        out["detail"][k] = detail
        print(f"k={k} |S_k|={out['S_sizes'][k]:>3}  largest induced D_n: n={best}"
              f"  (|D_{best}|={C.D(best)[0] if best else 0})  detail={detail}",
              flush=True)
    print(json.dumps(out, indent=2, default=str))


if __name__ == "__main__":
    main()
