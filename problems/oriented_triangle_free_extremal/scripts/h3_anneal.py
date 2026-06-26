"""H3 attack: refutation-effort-guided simulated annealing for a chi_vec=3
oriented triangle-free graph on 18<=n<25 (would improve m(3)<=25 to m(3)<=n).

State = a maximal triangle-free graph on n vertices + an orientation.
Objective = R, the number of lazy monochromatic-cycle refutation rounds the
k=2 dicolouring SAT solver needs (smooth hardness gradient toward chi=3).
Whenever a state hits 2-dicolouring UNSAT (dico=False), chi_vec=3 is certified
with the exact oracle.

Run with the problem venv:
  .venv/bin/python scripts/h3_anneal.py
"""
from __future__ import annotations

import itertools
import math
import random
import sys

import core
from pysat.solvers import Solver

import oracle


# --------------------------------------------------------------------------- #
#  Objective: lazy k=2 dicolouring refutation effort
# --------------------------------------------------------------------------- #

def two_dicol_effort(n, arcs):
    """Returns (R, dicolourable). R = number of lazy refutation rounds the k=2
    dicolouring SAT solver runs before terminating; dicolourable=False means the
    digraph is NOT 2-dicolourable (=> chi_vec >= 3)."""
    k = 2

    def var(v, c):
        return v * k + c + 1

    solver = Solver(name="glucose3")
    for v in range(n):
        solver.add_clause([var(v, 0), var(v, 1)])
        solver.add_clause([-var(v, 0), -var(v, 1)])
    R = 0
    while True:
        if not solver.solve():
            solver.delete()
            return R, False
        model = set(solver.get_model())
        colour = {v: (0 if var(v, 0) in model else 1) for v in range(n)}
        added = False
        for c in range(k):
            verts = [v for v in range(n) if colour[v] == c]
            vset = set(verts)
            sub = core._digraph(
                n, [(u, v) for (u, v) in arcs if u in vset and v in vset])
            cyc = core._find_directed_cycle(sub.subgraph(verts))
            if cyc is not None:
                solver.add_clause([-var(v, c) for v in cyc])
                added = True
        R += 1
        if not added:
            solver.delete()
            return R, True


# --------------------------------------------------------------------------- #
#  Maximal triangle-free graphs and the local moves
# --------------------------------------------------------------------------- #

def random_maximal_tri_free(n, rng):
    """A random EDGE-MAXIMAL triangle-free graph: greedily add edges in random
    order, skipping any that would close a triangle. Returns adjacency sets."""
    adj = [set() for _ in range(n)]
    pairs = list(itertools.combinations(range(n), 2))
    rng.shuffle(pairs)
    for u, v in pairs:
        if adj[u] & adj[v]:
            continue
        adj[u].add(v)
        adj[v].add(u)
    return adj


def saturate(adj, rng):
    """Greedily add edges (random order) until edge-maximal triangle-free."""
    n = len(adj)
    pairs = list(itertools.combinations(range(n), 2))
    rng.shuffle(pairs)
    for u, v in pairs:
        if v in adj[u]:
            continue
        if adj[u] & adj[v]:
            continue
        adj[u].add(v)
        adj[v].add(u)
    return adj


def adj_to_edges(adj):
    return [(u, v) for u in range(len(adj)) for v in adj[u] if u < v]


def orient(edges, dirbits):
    """dirbits[e]=0 means (u,v), 1 means (v,u)."""
    return [(u, v) if dirbits[i] == 0 else (v, u)
            for i, (u, v) in enumerate(edges)]


# --------------------------------------------------------------------------- #
#  Simulated annealing per n
# --------------------------------------------------------------------------- #

def anneal_n(n, restarts, moves_per_restart, seed, log=True):
    rng = random.Random(seed)
    best_R = -1
    best_state = None
    total_evals = 0

    for r in range(restarts):
        adj = random_maximal_tri_free(n, rng)
        edges = adj_to_edges(adj)
        dirbits = [rng.randint(0, 1) for _ in edges]
        arcs = orient(edges, dirbits)
        R, dico = two_dicol_effort(n, arcs)
        total_evals += 1
        if not dico:
            return _certify(n, arcs, total_evals, "restart-init")

        cur_R = R
        T = 4.0
        cooling = 0.999
        stall = 0
        for step in range(moves_per_restart):
            move_type = rng.random()
            if move_type < 0.6:
                # (a) re-orient a single arc
                i = rng.randrange(len(dirbits))
                dirbits[i] ^= 1
                new_arcs = orient(edges, dirbits)
                nR, ndico = two_dicol_effort(n, new_arcs)
                total_evals += 1
                if not ndico:
                    return _certify(n, new_arcs, total_evals, "reorient")
                accept = nR >= cur_R or rng.random() < math.exp((nR - cur_R) / T)
                if accept:
                    cur_R = nR
                    arcs = new_arcs
                else:
                    dirbits[i] ^= 1  # revert
            else:
                # (b) edge-swap preserving edge-maximal triangle-freeness:
                #     delete one edge, greedily re-saturate, re-orient fresh edges
                if not edges:
                    break
                ei = rng.randrange(len(edges))
                du, dv = edges[ei]
                new_adj = [set(s) for s in adj]
                new_adj[du].discard(dv)
                new_adj[dv].discard(du)
                saturate(new_adj, rng)
                new_edges = adj_to_edges(new_adj)
                new_dirbits = [rng.randint(0, 1) for _ in new_edges]
                new_arcs = orient(new_edges, new_dirbits)
                nR, ndico = two_dicol_effort(n, new_arcs)
                total_evals += 1
                if not ndico:
                    return _certify(n, new_arcs, total_evals, "edge-swap")
                accept = nR >= cur_R or rng.random() < math.exp((nR - cur_R) / T)
                if accept:
                    adj = new_adj
                    edges = new_edges
                    dirbits = new_dirbits
                    arcs = new_arcs
                    cur_R = nR

            if cur_R > best_R:
                best_R = cur_R
                best_state = (n, list(arcs))
                stall = 0
            else:
                stall += 1
            T *= cooling
            if stall > 400:
                break  # restart on stall

        if log and (r % 25 == 0 or r == restarts - 1):
            print(f"  n={n} restart {r+1}/{restarts}: best_R={best_R} "
                  f"evals={total_evals}", flush=True)

    return {"n": n, "hit": False, "best_R": best_R,
            "total_evals": total_evals, "best_arcs": best_state[1] if best_state else None}


def _certify(n, arcs, total_evals, via):
    """Exact-oracle certification of a chi_vec=3 candidate."""
    res = oracle.check_construction(n, arcs, name=f"h3_anneal_n{n}")
    res["hit"] = True
    res["via"] = via
    res["total_evals"] = total_evals
    if res.get("chi_vec") == 3:
        res["is_dicritical"] = oracle.is_dicritical(n, arcs, 3)
    res["arcs"] = arcs
    return res


# --------------------------------------------------------------------------- #
#  Driver
# --------------------------------------------------------------------------- #

def main():
    import json
    restarts = int(sys.argv[1]) if len(sys.argv) > 1 else 200
    moves = int(sys.argv[2]) if len(sys.argv) > 2 else 1000
    ns = [int(x) for x in sys.argv[3].split(",")] if len(sys.argv) > 3 else [24, 23, 22, 21, 20, 19, 18]

    summary = []
    for n in ns:
        print(f"=== ANNEAL n={n} (restarts={restarts}, moves={moves}) ===", flush=True)
        res = anneal_n(n, restarts, moves, seed=1000 + n)
        if res.get("hit"):
            print(json.dumps(res, indent=2, default=str), flush=True)
            print(f"*** HIT at n={n}: chi_vec={res.get('chi_vec')} ***", flush=True)
            summary.append({"n": n, "hit": True, "chi_vec": res.get("chi_vec"),
                            "is_oriented": res.get("is_oriented"),
                            "is_triangle_free": res.get("is_triangle_free"),
                            "is_dicritical": res.get("is_dicritical")})
            # a genuine bound improvement: stop and report
            break
        else:
            print(f"  n={n}: NO chi=3 found. best_R={res['best_R']} "
                  f"evals={res['total_evals']}", flush=True)
            summary.append({"n": n, "hit": False, "best_R": res["best_R"],
                            "total_evals": res["total_evals"]})

    print("=== SUMMARY ===", flush=True)
    print(json.dumps(summary, indent=2), flush=True)


if __name__ == "__main__":
    main()
