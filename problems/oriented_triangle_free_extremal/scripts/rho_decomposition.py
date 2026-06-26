"""Ground-plan: DECOMPOSE the a_vec crux via rho = a*/alpha(G).

For triangle-free process graphs G:
  - alpha(G) = independence number = max clique of complement (networkx find_cliques)
  - a* = min over orientations of EXACT core.acyclic_number
  - rho = a*/alpha
Diagnostics: rho/sqrt(log n), rho/log n, consecutive rho-ratio vs sqrt(log b / log a),
plus alpha/sqrt(n log n) (claimed flat ~1.1).

Then test ONE non-random orientation aiming to lower rho:
a proper-2-colouring-layered orientation that keeps within-colour empty and
randomises cross-colour arc directions (NOT a topological order; must create dicycles).

CONFIRM iff that rule gives rho/sqrt(log n) DECLINING.
KILL  iff every rule's rho/sqrt(log n) stays FLAT ~1.07 and rho/log n DECLINES.
"""
from __future__ import annotations

import math
import os
import random
import signal
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import core
import networkx as nx

from lit_reduction_test import triangle_free_process, random_orientation


def alpha_independence(n, edges):
    """Independence number = max clique of the complement graph."""
    G = nx.Graph()
    G.add_nodes_from(range(n))
    G.add_edges_from(edges)
    Gc = nx.complement(G)
    best = 0
    for clq in nx.find_cliques(Gc):
        if len(clq) > best:
            best = len(clq)
    return best


def bipartition_layered_orientation(n, edges, seed):
    """Proper 2-colouring (G triangle-free is NOT bipartite in general, so use a
    greedy/BFS 2-colouring that may leave some same-colour edges; we orient ALL
    edges).  Cross-colour edges: randomise direction (creates dicycles, not a
    topological order).  Same-colour edges: also randomise.  Net effect: a
    balanced-bipartition-aware random orientation."""
    rng = random.Random(seed)
    # greedy 2-colouring via BFS over connected components
    adj = [set() for _ in range(n)]
    for (u, v) in edges:
        adj[u].add(v)
        adj[v].add(u)
    color = [-1] * n
    for s in range(n):
        if color[s] != -1:
            continue
        color[s] = 0
        stack = [s]
        while stack:
            x = stack.pop()
            for y in adj[x]:
                if color[y] == -1:
                    color[y] = 1 - color[x]
                    stack.append(y)
    arcs = []
    for (u, v) in edges:
        if color[u] == 0 and color[v] == 1:
            # canonical cross-colour direction 0->1, but randomise to make dicycles
            arcs.append((u, v) if rng.random() < 0.5 else (v, u))
        elif color[u] == 1 and color[v] == 0:
            arcs.append((u, v) if rng.random() < 0.5 else (v, u))
        else:
            # same-colour (odd structure): randomise
            arcs.append((u, v) if rng.random() < 0.5 else (v, u))
    return arcs


class _TO(Exception):
    pass


def _alarm(signum, frame):
    raise _TO()


def acyclic_with_timeout(n, arcs, secs):
    signal.signal(signal.SIGALRM, _alarm)
    signal.setitimer(signal.ITIMER_REAL, secs)
    try:
        r = core.acyclic_number(n, arcs)
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
    return r


def main():
    ns = [20, 30, 40, 50]
    cs = [1.5, 2.0, 2.5]
    n_seeds = 4
    per_call_to = 100.0  # seconds per exact a* call

    rows = []
    for n in ns:
        t0 = time.time()
        best = None  # (a_star_random, alpha, edges) minimizing a_star_random
        best_layer = None
        for c in cs:
            p = c / math.sqrt(n)
            m_cap = int(p * n * (n - 1) / 2)
            for s in range(n_seeds):
                n2, edges = triangle_free_process(n, m_cap, seed=1000 * int(c * 10) + s + n)
                if not core.is_triangle_free(n2, edges):
                    continue
                alpha = alpha_independence(n2, edges)
                # random orientation a*
                try:
                    arcs = random_orientation(edges, seed=7 * s + 3)
                    a_rand = acyclic_with_timeout(n2, arcs, per_call_to)
                except _TO:
                    continue
                if best is None or a_rand < best[0]:
                    best = (a_rand, alpha, edges, c, s)
                # layered orientation a*
                try:
                    larcs = bipartition_layered_orientation(n2, edges, seed=11 * s + 5)
                    assert core.is_oriented(larcs)
                    a_lay = acyclic_with_timeout(n2, larcs, per_call_to)
                except _TO:
                    a_lay = None
                if a_lay is not None and (best_layer is None or a_lay < best_layer[0]):
                    best_layer = (a_lay, alpha, c, s)
            if time.time() - t0 > 360:
                break
        if best is None:
            rows.append((n, None))
            continue
        a_rand, alpha, edges, c, s = best
        rho = a_rand / alpha
        snln = math.sqrt(n * math.log(n))
        snlogn = math.sqrt(n) * math.log(n)
        lay = best_layer
        rows.append({
            "n": n,
            "best_c": c,
            "alpha": alpha,
            "a_rand": a_rand,
            "rho_rand": rho,
            "alpha/sqrt(nlogn)": alpha / snln,
            "a_rand/sqrt(nlogn)": a_rand / snln,
            "a_rand/(sqrtn logn)": a_rand / snlogn,
            "rho/sqrt(logn)": rho / math.sqrt(math.log(n)),
            "rho/logn": rho / math.log(n),
            "layer_a": (lay[0] if lay else None),
            "layer_alpha": (lay[1] if lay else None),
            "layer_rho": (lay[0] / lay[1] if lay else None),
            "layer_rho/sqrt(logn)": (lay[0] / lay[1] / math.sqrt(math.log(n)) if lay else None),
            "secs": round(time.time() - t0, 1),
        })
        print(f"n={n} done in {time.time()-t0:.1f}s: alpha={alpha} a_rand={a_rand} "
              f"rho={rho:.3f} layer_rho={(lay[0]/lay[1] if lay else None)}", flush=True)

    print("\n=== TABLE ===")
    keys = ["n", "best_c", "alpha", "a_rand", "rho_rand",
            "alpha/sqrt(nlogn)", "a_rand/sqrt(nlogn)", "a_rand/(sqrtn logn)",
            "rho/sqrt(logn)", "rho/logn",
            "layer_a", "layer_rho", "layer_rho/sqrt(logn)"]
    for r in rows:
        if not isinstance(r, dict):
            print(r)
            continue
        print({k: (round(r[k], 4) if isinstance(r[k], float) else r[k]) for k in keys})

    # consecutive rho-ratio vs sqrt(log b / log a)
    print("\n=== rho-growth vs sqrt(log) prediction ===")
    drows = [r for r in rows if isinstance(r, dict)]
    for i in range(1, len(drows)):
        a_, b_ = drows[i - 1]["n"], drows[i]["n"]
        rr = drows[i]["rho_rand"] / drows[i - 1]["rho_rand"]
        pred = math.sqrt(math.log(b_) / math.log(a_))
        print(f"n {a_}->{b_}: rho-ratio={rr:.4f}  sqrt(log) pred={pred:.4f}")

    # layered rho-growth too
    print("\n=== LAYERED rho-growth ===")
    lrows = [r for r in drows if r["layer_rho"] is not None]
    for i in range(1, len(lrows)):
        a_, b_ = lrows[i - 1]["n"], lrows[i]["n"]
        rr = lrows[i]["layer_rho"] / lrows[i - 1]["layer_rho"]
        pred = math.sqrt(math.log(b_) / math.log(a_))
        print(f"n {a_}->{b_}: layer-rho-ratio={rr:.4f}  sqrt(log) pred={pred:.4f}")


if __name__ == "__main__":
    main()
