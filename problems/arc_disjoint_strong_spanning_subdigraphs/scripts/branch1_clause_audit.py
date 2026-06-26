"""branch1_clause_audit.py -- SIDE ARM of the branch-(1) attack.

Exhaustive per-clause T2-admissibility audit over EVERY strictly
rho-headless HARD gateway found in the in-class construction-A census
cells (same population as check_lexist_fixedroot.py / lexist_contracted_
part.py).  For each such gateway and each candidate absorbed rho-tail
w in R\\{v}, evaluate the three T2-admissibility clauses

    (A) v-placement:   v notin X*_w
    (B) size bound:    |X*_w| <= n-2
    (C) head-escape:   some escaped AV_u-head outside X*_w

and record (i) how often each clause binds (fails), (ii) whether ANY
gateway has ZERO admissible w (= a branch-(1) instance), (iii) the
distribution of |R| and whether v is itself a rho-tail.

This is structured-cell EVIDENCE only (a biased sample); it is reported
as the never-binding-clause statistic an impossibility lemma would need,
NOT as universal support.
"""
from __future__ import annotations

import json
import os
import sys
from collections import Counter

_HERE = os.path.dirname(os.path.abspath(__file__))
_CODE = os.path.join(os.path.dirname(_HERE), "code")
for _p in (_CODE, _HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import networkx as nx  # noqa: E402

from digraph import Digraph  # noqa: E402
from generators.near_split import (  # noqa: E402
    enumerate_construction_A,
    is_one_zero_near_split,
)
from check_lexist_fixedroot import (  # noqa: E402
    chord_contraction_with_K,
    in_arborescences,
    pair_realizable,
    subtree_through,
    tree_arcs,
)


def _arc_conn(n, arcs):
    return Digraph.from_arcs(range(n), list(arcs)).arc_connectivity()


def x_star(graph, cage, w, n, root):
    reduced = graph.copy()
    reduced.remove_nodes_from(cage | {w})
    trapped = {
        z for z in range(n)
        if z not in cage | {w} and z != root and not nx.has_path(reduced, z, root)
    }
    return cage | {w} | trapped


def audit_instance(n, arcs, K_set):
    """Return per-gateway audit records for strictly rho-headless HARD
    gateways of this contraction (root rho=0)."""
    mult = Counter(arcs)
    root = 0
    records = []

    graph = nx.MultiDiGraph()
    graph.add_nodes_from(range(n))
    graph.add_edges_from(arcs)

    # find the contracted-side structure: u is the unique V1-image (label 0's
    # partner).  In chord_contraction_with_K, p,q -> 0; the OTHER V1 vertex
    # keeps its label.  We instead identify u as a non-root vertex that, with
    # the cage, forms a t==u gateway -- but for the audit we need u explicitly.
    # The near-split contraction has V1 = {p,q,u}; after contraction rho=0 and
    # u is the single remaining V1 vertex.  K_set are V2 images.  u is the
    # unique non-root vertex NOT in K_set and != root.
    non_K = [x for x in range(n) if x != root and x not in K_set]
    if len(non_K) != 1:
        return records
    u = non_K[0]
    if (u, root) in mult:
        return records                       # need strictly rho-headless

    without_u = graph.copy()
    without_u.remove_node(u)
    cage = {u} | {
        x for x in range(n)
        if x not in (root, u) and not nx.has_path(without_u, x, root)
    }
    R = sorted({x for x, z in mult if z == root})

    struct_out = {}
    for (x, y) in mult:
        struct_out.setdefault(x, set()).add(y)
    struct_out = {x: tuple(sorted(vs)) for x, vs in struct_out.items()}
    arbs = [(s, tree_arcs(s)) for s in in_arborescences(n, struct_out, root)]

    # enumerate AV_u out-arcs a=(u,v); for each, look for a HARD gateway pair
    for v in sorted(struct_out.get(u, ())):
        a = (u, v)
        av_heads = sorted(z for z in struct_out[u] if z != v)
        for succT, Tset in arbs:
            if succT.get(u) != v:
                continue
            X = subtree_through(succT, u, root, n)
            if X != cage:
                continue
            for succU, Uset in arbs:
                if not pair_realizable(Tset, Uset, mult):
                    continue
                if a in Uset and mult[a] < 2:
                    continue
                exits = [(w, z) for (w, z) in Uset if w in X and z not in X]
                if len(exits) != 1:
                    continue
                free = [e for e in mult if e[0] in X and e[1] not in X
                        and mult[e] - (e in Tset) - (e in Uset) >= 1]
                if not free or not all(e[0] == u for e in free):
                    continue
                strict = [b for b in exits
                          if (subtree_through(succU, b[0], root, n) & X) < X]
                if strict:
                    continue
                # strictly rho-headless HARD gateway found at a.
                clause_fail = Counter()
                n_admissible = 0
                rest = [w for w in R if w != v]
                per_w = {}
                for w in rest:
                    Xs = x_star(graph, cage, w, n, root)
                    A_ok = v not in Xs
                    B_ok = len(Xs) <= n - 2
                    C_ok = any(z not in Xs for z in av_heads)
                    adm = A_ok and B_ok and C_ok
                    per_w[w] = (A_ok, B_ok, C_ok)
                    if not A_ok:
                        clause_fail["A"] += 1
                    if not B_ok:
                        clause_fail["B"] += 1
                    if not C_ok:
                        clause_fail["C"] += 1
                    if adm:
                        n_admissible += 1
                records.append({
                    "a": (u, v),
                    "v_is_rho_tail": v in R,
                    "abs_R": len(R),
                    "rest": len(rest),
                    "n_admissible_w": n_admissible,
                    "clause_fail": dict(clause_fail),
                })
                # one hard gateway per a is enough for the clause statistic
                break
            else:
                continue
            break
    return records


def main():
    cells = [(2, 3), (3, 3), (2, 4), (2, 5), (3, 4), (4, 3)]
    agg = {
        "cells": [],
        "total_rho_headless_hard_gateways": 0,
        "gateways_with_zero_admissible_w": 0,
        "gateways_with_v_a_rho_tail": 0,
        "abs_R_distribution": Counter(),
        "clause_ever_fails": Counter(),       # which clause binds, summed
        "min_admissible_w_seen": None,
        "zero_admissible_examples": [],
    }
    for (v1, v2) in cells:
        seen = set()
        cell_records = 0
        for inst in enumerate_construction_A(v1, v2):
            D = inst.build()
            ok, _ = is_one_zero_near_split(D, list(inst.V1), list(inst.V2))
            if not ok or _arc_conn(inst.n, list(inst.arcs)) < 3:
                continue
            k, arcs, K_set = chord_contraction_with_K(inst)
            key = (k, tuple(sorted(arcs)))
            if key in seen:
                continue
            seen.add(key)
            if _arc_conn(k, arcs) < 3:
                continue
            for rec in audit_instance(k, arcs, K_set):
                cell_records += 1
                agg["total_rho_headless_hard_gateways"] += 1
                agg["abs_R_distribution"][rec["abs_R"]] += 1
                if rec["v_is_rho_tail"]:
                    agg["gateways_with_v_a_rho_tail"] += 1
                for c, ct in rec["clause_fail"].items():
                    agg["clause_ever_fails"][c] += ct
                m = rec["n_admissible_w"]
                if (agg["min_admissible_w_seen"] is None
                        or m < agg["min_admissible_w_seen"]):
                    agg["min_admissible_w_seen"] = m
                if m == 0:
                    agg["gateways_with_zero_admissible_w"] += 1
                    if len(agg["zero_admissible_examples"]) < 5:
                        agg["zero_admissible_examples"].append(
                            {"cell": f"({v1},{v2})", "k": k, **rec})
        agg["cells"].append({"cell": f"({v1},{v2})",
                             "rho_headless_hard_gateways": cell_records})

    agg["abs_R_distribution"] = dict(agg["abs_R_distribution"])
    agg["clause_ever_fails"] = dict(agg["clause_ever_fails"])
    print(json.dumps(agg, indent=2))


if __name__ == "__main__":
    main()
