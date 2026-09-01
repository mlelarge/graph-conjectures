"""Enumerate apex-collision blocks (2-connected marked) and characterize them.
For each block with an apex collision among NON-REPS:
  - list collision classes (non-reps sharing one apex value)
  - same-fiber vs cross-fiber
  - the excess vertices (class size - 1, summed)
  - D' lines, and whether the bipartite (excess vertices)~(D' lines containing them)
    saturates the excess (=> global SDR exists => Hall).
Also test a candidate canonical D'-assignment rule.
"""
from __future__ import annotations
import sys, subprocess, itertools, json
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
import networkx as nx


def block_data(n, edges, u):
    dist = core.all_pairs_distances(n, edges)
    S = [x for x in range(n) if x != u]
    du = dist[u]
    fullS = frozenset(S)
    Sigma = {}; A = {}; F = {}
    for s in S:
        dus = du[s]; ds = dist[s]
        ray = set(); apex = set(); far = set()
        for x in S:
            dux = du[x]; dxs = ds[x]
            if dux + dxs == dus or dus + dxs == dux:
                ray.add(x); apex.add(x)
            elif dux + dus == dxs:
                apex.add(x); far.add(x)
        Sigma[s] = frozenset(ray); A[s] = frozenset(apex); F[s] = frozenset(far)
    fibers = defaultdict(list)
    for s in S:
        fibers[Sigma[s]].append(s)
    nonreps = []
    for C, mem in fibers.items():
        ms = sorted(mem, key=lambda s: (du[s], s))
        nonreps.extend(ms[1:])
    dprime = set()
    for a, b in itertools.combinations(range(n), 2):
        L = core.line_of_pair(dist, n, a, b)
        Lv = frozenset(x for x in L)  # vertices (include any), but exclude u-check
        if u not in Lv and Lv != fullS:
            dprime.add(Lv)
    return S, fullS, Sigma, A, F, fibers, nonreps, dprime, du


def run(order, maxex=10):
    proc = subprocess.run(
        ["geng", "-C", "-q", str(order)],
        capture_output=True,
        text=True,
        check=True,
    )
    st = dict(order=order, blocks=0, collision_blocks=0, total_excess=0,
              same_fiber_classes=0, cross_fiber_classes=0,
              excess_saturate_fail=0,    # excess->D' (containment) doesn't saturate
              excess_no_dprime=0,        # some excess vertex on NO D' line
              max_mult=0, ex=[])
    for line in proc.stdout.splitlines():
        g6 = line.strip()
        if not g6:
            continue
        n, edges = core.graph6_to_edges(g6)
        for u in range(n):
            st["blocks"] += 1
            S, fullS, Sigma, A, F, fibers, nonreps, dprime, du = block_data(n, edges, u)
            # apex classes among non-reps
            apexcls = defaultdict(list)
            for s in nonreps:
                apexcls[A[s]].append(s)
            collide = {v: ss for v, ss in apexcls.items() if len(ss) > 1}
            if not collide:
                continue
            st["collision_blocks"] += 1
            # choose canonical rep per apex-class: shallowest; excess = rest
            excess = []
            for v, ss in apexcls.items():
                st["max_mult"] = max(st["max_mult"], len(ss))
                if len(ss) > 1:
                    # same fiber? all share Sigma?
                    sig = set(Sigma[s] for s in ss)
                    if len(sig) == 1:
                        st["same_fiber_classes"] += 1
                    else:
                        st["cross_fiber_classes"] += 1
                    ms = sorted(ss, key=lambda s: (du[s], s))
                    excess.extend(ms[1:])
            st["total_excess"] += len(excess)
            # bipartite excess ~ D'(containment)
            bg = nx.Graph()
            lnodes = [("L", s) for s in excess]
            bg.add_nodes_from(lnodes, bipartite=0)
            for s in excess:
                hit = False
                for D in dprime:
                    if s in D:
                        bg.add_edge(("L", s), ("D", D)); hit = True
                if not hit:
                    st["excess_no_dprime"] += 1
            m = nx.algorithms.bipartite.maximum_matching(bg, top_nodes=lnodes)
            matched = sum(1 for x in lnodes if x in m)
            if matched < len(excess):
                st["excess_saturate_fail"] += 1
                if len(st["ex"]) < maxex:
                    st["ex"].append((g6, u, sorted(excess), len(dprime)))
    return st


if __name__ == "__main__":
    for o in (int(x) for x in (sys.argv[1:] or [7, 8])):
        print(json.dumps(run(o)))
