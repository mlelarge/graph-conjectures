r"""Apex-cut probe for the Q2 / Path-FAS problem.

This script tests the proposed non-forward attack:

    For each vertex v, let P_v be the selected neighbours of v in the
    unknown linear forest F.  Since |P_v| <= 2, every directed triangle

        v -> a -> b -> v

    with a,b not in P_v forces the edge ab into F.

Thus triangle hitting is equivalent to the apex-cut closure condition

    E(C_v - P_v) subset F      for every v,

where C_v is the bipartite graph between N+(v) and N-(v) consisting of
arcs a->b.

The probe builds the resulting finite-domain CSP:

    variable v: choose P_v subset V\{v}, |P_v| <= 2;
    symmetry: u in P_v iff v in P_u;
    implication: if a candidate P_v forces edge xy, then y in P_x and
                 x in P_y.

Local candidates additionally require C_v - P_v to be a linear forest, a
necessary condition for any global witness.

This is not claimed polynomial.  The purpose is to see whether the local
apex constraints are already strong enough on the known hard instances, and
to make any failure mode explicit.
"""
from __future__ import annotations

import argparse
import itertools
import json
import os
from dataclasses import dataclass
from functools import lru_cache
from typing import Iterable, Sequence

Matrix = list[list[int]]
Edge = tuple[int, int]


def edge(u: int, v: int) -> Edge:
    return (u, v) if u < v else (v, u)


def all_edges(n: int) -> list[Edge]:
    return [(i, j) for i in range(n) for j in range(i + 1, n)]


def is_linear_forest(n: int, edges: Iterable[Edge]) -> bool:
    edges = set(edges)
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    if any(len(a) > 2 for a in adj):
        return False
    seen = [False] * n
    for s in range(n):
        if seen[s] or not adj[s]:
            continue
        stack = [s]
        seen[s] = True
        verts = []
        degsum = 0
        while stack:
            x = stack.pop()
            verts.append(x)
            degsum += len(adj[x])
            for y in adj[x]:
                if not seen[y]:
                    seen[y] = True
                    stack.append(y)
        if degsum // 2 != len(verts) - 1:
            return False
    return True


def directed_cycles(T: Matrix, k: int) -> list[tuple[int, ...]]:
    n = len(T)
    out = []
    seen = set()
    for verts in itertools.combinations(range(n), k):
        first = verts[0]
        for tail in itertools.permutations(verts[1:]):
            cyc = (first,) + tail
            if all(T[cyc[i]][cyc[(i + 1) % k]] for i in range(k)):
                key = frozenset(edge(cyc[i], cyc[(i + 1) % k])
                                for i in range(k))
                if key not in seen:
                    seen.add(key)
                    out.append(cyc)
    return out


def hits_directed_cycles(T: Matrix, F: set[Edge], k: int) -> bool:
    return all(
        any(edge(cyc[i], cyc[(i + 1) % k]) in F for i in range(k))
        for cyc in directed_cycles(T, k)
    )


def apex_cut_edges(T: Matrix, v: int) -> set[Edge]:
    """Edges ab of cyclic triangles v->a->b->v."""
    n = len(T)
    out = set()
    for a in range(n):
        if a == v or not T[v][a]:
            continue
        for b in range(n):
            if b == v or b == a:
                continue
            if T[b][v] and T[a][b]:
                out.add(edge(a, b))
    return out


def selected_neighbours(n: int, F: set[Edge]) -> list[frozenset[int]]:
    P = [set() for _ in range(n)]
    for u, v in F:
        P[u].add(v)
        P[v].add(u)
    return [frozenset(x) for x in P]


def apex_triangle_closed(T: Matrix, F: set[Edge]) -> bool:
    P = selected_neighbours(len(T), F)
    for v, Pv in enumerate(P):
        for a, b in apex_cut_edges(T, v):
            if a not in Pv and b not in Pv and (a, b) not in F:
                return False
    return True


@dataclass(frozen=True)
class Candidate:
    v: int
    P: frozenset[int]
    forced: frozenset[Edge]
    req: tuple[frozenset[int], ...]


def _req_from(v: int, P: frozenset[int], forced: set[Edge], n: int):
    req = [set() for _ in range(n)]
    for u in P:
        req[u].add(v)
    for a, b in forced:
        req[a].add(b)
        req[b].add(a)
    return tuple(frozenset(x) for x in req)


def candidate_domains(T: Matrix) -> list[list[Candidate]]:
    n = len(T)
    domains: list[list[Candidate]] = []
    for v in range(n):
        others = [u for u in range(n) if u != v]
        Cv = apex_cut_edges(T, v)
        dom = []
        for r in (0, 1, 2):
            for P_tuple in itertools.combinations(others, r):
                P = frozenset(P_tuple)
                forced = {e for e in Cv if e[0] not in P and e[1] not in P}
                if is_linear_forest(n, forced):
                    dom.append(Candidate(
                        v=v,
                        P=P,
                        forced=frozenset(forced),
                        req=_req_from(v, P, forced, n),
                    ))
        domains.append(dom)
    return domains


def compatible(a: Candidate, b: Candidate) -> bool:
    i, j = a.v, b.v
    if (j in a.P) != (i in b.P):
        return False
    if not a.req[j].issubset(b.P):
        return False
    if not b.req[i].issubset(a.P):
        return False
    return True


def arc_consistency(domains: list[list[Candidate]]):
    n = len(domains)
    domains = [list(d) for d in domains]
    changed = True
    rounds = 0
    while changed:
        changed = False
        rounds += 1
        for i in range(n):
            kept = []
            for c in domains[i]:
                ok = True
                for j in range(n):
                    if i == j:
                        continue
                    if not any(compatible(c, d) for d in domains[j]):
                        ok = False
                        break
                if ok:
                    kept.append(c)
            if len(kept) != len(domains[i]):
                domains[i] = kept
                changed = True
            if not domains[i]:
                return domains, {"consistent": False, "rounds": rounds}
    return domains, {"consistent": True, "rounds": rounds}


def assignment_edges(assignment: Sequence[Candidate]) -> set[Edge]:
    F = set()
    for c in assignment:
        for u in c.P:
            F.add(edge(c.v, u))
    return F


def assignment_is_valid_path_fas(T: Matrix, assignment: Sequence[Candidate]) -> bool:
    F = assignment_edges(assignment)
    return (
        is_linear_forest(len(T), F)
        and apex_triangle_closed(T, F)
        and hits_directed_cycles(T, F, 4)
    )


def _restrict_and_ac(domains, var: int, cand: Candidate):
    nxt = [list(d) for d in domains]
    nxt[var] = [cand]
    return arc_consistency(nxt)


def search_apex_csp(T: Matrix, node_cap: int = 100_000):
    domains, ac = arc_consistency(candidate_domains(T))
    if not ac["consistent"]:
        return {
            "found": False,
            "nodes": 0,
            "exhausted": True,
            "initial_ac": ac,
            "reason": "arc_consistency_empty",
        }

    n = len(T)
    nodes = 0

    @lru_cache(maxsize=None)
    def rec(key):
        nonlocal nodes
        nodes += 1
        if nodes > node_cap:
            return None
        cur = []
        offset = 0
        for i, d in enumerate(domains):
            size = key[offset]
            offset += 1
            idxs = key[offset:offset + size]
            offset += size
            cur.append([domains[i][idx] for idx in idxs])
        if all(len(d) == 1 for d in cur):
            assignment = [d[0] for d in cur]
            return assignment if assignment_is_valid_path_fas(T, assignment) else False
        var = min((i for i in range(n) if len(cur[i]) > 1), key=lambda i: len(cur[i]))
        for cand in cur[var]:
            nxt, ac2 = _restrict_and_ac(cur, var, cand)
            if not ac2["consistent"]:
                continue
            packed = []
            for i in range(n):
                packed.append(len(nxt[i]))
                # Map candidates back to indices in the original post-AC domains.
                pos = {c: k for k, c in enumerate(domains[i])}
                packed.extend(sorted(pos[c] for c in nxt[i]))
            out = rec(tuple(packed))
            if out is None or out:
                return out
        return False

    packed0 = []
    for i in range(n):
        packed0.append(len(domains[i]))
        packed0.extend(range(len(domains[i])))
    out = rec(tuple(packed0))
    return {
        "found": bool(out),
        "nodes": nodes,
        "exhausted": out is not None,
        "initial_ac": ac,
        "F": sorted(assignment_edges(out)) if out else None,
    }


def summarize(T: Matrix, node_cap: int = 100_000):
    initial = candidate_domains(T)
    ac_domains, ac = arc_consistency(initial)
    search = search_apex_csp(T, node_cap=node_cap)
    return {
        "n": len(T),
        "initial_domain_min": min(len(d) for d in initial),
        "initial_domain_max": max(len(d) for d in initial),
        "initial_domain_sum": sum(len(d) for d in initial),
        "ac_consistent": ac["consistent"],
        "ac_rounds": ac["rounds"],
        "ac_domain_min": min((len(d) for d in ac_domains), default=0),
        "ac_domain_max": max((len(d) for d in ac_domains), default=0),
        "ac_domain_sum": sum(len(d) for d in ac_domains),
        "search_found": search["found"],
        "search_nodes": search["nodes"],
        "search_exhausted": search["exhausted"],
    }


def _load_records(n: int):
    here = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(here, "..", "data", f"minimal_no_obstruction_catalogue_n{n}.json")
    with open(path) as fh:
        return json.load(fh)["records"]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=7)
    parser.add_argument("--max", type=int, default=8)
    parser.add_argument("--node-cap", type=int, default=100_000)
    args = parser.parse_args()

    for r in _load_records(args.n)[:args.max]:
        row = summarize(r["T"], node_cap=args.node_cap)
        row["name"] = r.get("name")
        print(json.dumps(row, sort_keys=True))


if __name__ == "__main__":
    main()
