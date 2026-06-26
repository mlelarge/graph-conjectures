"""H1/H3: hunt for a small C_3 witness with chi_vec >= 3 (settles/upper-bounds m(3)).

Strategy:
  (A) Substitution / lexicographic products built from G_2 (directed triangle),
      which is the unique chi=2 C_3 gadget. Test whether any stays in C_3 and
      lifts chi to 3.
  (B) A randomized/structured local search over small oriented digraphs that are
      C_3 members, maximizing chi_vec, for n in a tractable range.

Every candidate is GROUNDED by oracle.check_construction (exact C_3 + exact chi).
"""
from __future__ import annotations

import itertools
import json
import random
import sys

import core
import oracle


def substitute(Gn, Garcs, Hn, Harcs):
    """Lexicographic substitution G[H]: replace each vertex i of G by a fresh
    copy of H (block i). Within block i put H's arcs. Between blocks i,j: if
    i->j in G put ALL arcs (copy_i_u -> copy_j_v) for all u,v.
    Vertex (i,u) -> index i*Hn + u."""
    idx = lambda i, u: i * Hn + u
    N = Gn * Hn
    arcs = []
    # within-block H copies
    for i in range(Gn):
        for (u, v) in Harcs:
            arcs.append((idx(i, u), idx(i, v)))
    # between-block, follow G direction, complete bipartite
    Gset = set(Garcs)
    for (i, j) in Gset:
        for u in range(Hn):
            for v in range(Hn):
                arcs.append((idx(i, u), idx(j, v)))
    return N, arcs


def report(name, n, arcs, compute_chi=True):
    res = oracle.check_construction(n, arcs, name=name, compute_chi=compute_chi)
    return res


def main():
    G2n, G2arcs = 3, [(0, 1), (1, 2), (2, 0)]
    results = []

    # (A) G_2[G_2]: directed triangle of directed triangles (lexicographic).
    n, arcs = substitute(G2n, G2arcs, G2n, G2arcs)
    results.append(report("G2[G2]_lex", n, arcs))

    # (A') single-vertex substitution variants won't change anything; try
    # substituting only ALONG a triangle but using *single arcs* between blocks
    # (one representative arc per ordered block pair) to avoid TT3 blowups.
    def sub_single(Gn, Garcs, Hn, Harcs, rep_u=0, rep_v=0):
        idx = lambda i, u: i * Hn + u
        N = Gn * Hn
        arcs = []
        for i in range(Gn):
            for (u, v) in Harcs:
                arcs.append((idx(i, u), idx(i, v)))
        for (i, j) in set(Garcs):
            arcs.append((idx(i, rep_u), idx(j, rep_v)))
        return N, arcs
    n, arcs = sub_single(G2n, G2arcs, G2n, G2arcs)
    results.append(report("G2[G2]_single_arc", n, arcs))

    # (B) randomized local search over C_3 members maximizing chi_vec.
    rng = random.Random(20260605)
    best = {"chi_vec": 0}
    for n in range(7, 13):
        # build candidates: random tournaments-ish oriented digraphs, then
        # repair to C_3 by deleting offending arcs greedily.
        for trial in range(4000):
            # random oriented digraph: each underlying edge present w.p. p, dir random
            p = rng.uniform(0.3, 0.7)
            arcs = []
            for u in range(n):
                for v in range(u + 1, n):
                    if rng.random() < p:
                        if rng.random() < 0.5:
                            arcs.append((u, v))
                        else:
                            arcs.append((v, u))
            # quick C_3 filter (cheap combinatorial)
            if core.has_transitive_triangle(n, arcs):
                continue
            if core.has_long_induced_dicycle(n, arcs, 4):
                continue
            if not core.is_oriented(arcs):
                continue
            cv = core.dichromatic_number(n, arcs, ub=4)
            if cv > best["chi_vec"]:
                best = {"chi_vec": cv, "n": n, "arcs": list(arcs)}
                results.append({"name": f"search_n{n}_trial{trial}",
                                "n": n, "chi_vec": cv, "m_arcs": len(arcs),
                                "is_C3": True, "arcs": list(arcs)})
                if cv >= 3:
                    # confirm via full oracle
                    conf = oracle.check_construction(n, list(arcs),
                                                     name=f"search_n{n}_CONFIRM")
                    results.append(conf)
                    print(json.dumps({"FOUND_chi3": conf}, default=str))
                    print(json.dumps({"results": results}, indent=2, default=str))
                    return
        results.append({"name": f"search_done_n{n}",
                        "best_chi_so_far": best["chi_vec"], "n_scanned": n})

    print(json.dumps({"results": results, "best": best}, indent=2, default=str))


if __name__ == "__main__":
    main()
