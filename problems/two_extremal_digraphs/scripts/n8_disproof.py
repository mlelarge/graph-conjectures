#!/usr/bin/env python3
"""
Resumable, checkpointed disproof hunt: a NON-PLANAR 2-extremal digraph would
refute Conjecture 9.2 (since H₂ ⇒ planar is proved, see docs/planarity_of_2extremal.md).

For a target n, sweep all 2-connected min-degree-≥2 graphs by edge count (via geng),
keep the NON-PLANAR ones, and test each for a 2-extremal orientation using the exact
Eulerian-pruned enumerator (scripts/planarity_search.two_extremal_orientations) with a
per-graph node budget.  Progress is checkpointed per edge-count bucket to a JSON file,
so the run can be stopped and resumed (completed buckets are skipped).

A 2-extremal orientation found on any non-planar graph is printed immediately and
written to the checkpoint as a COUNTEREXAMPLE.

Usage:
    PYTHONPATH=problems/two_extremal_digraphs/scripts \
      .venv/bin/python problems/two_extremal_digraphs/scripts/n8_disproof.py [--n 8] [--emax E] [--budget B]

Coverage is reported honestly: a bucket is "certified" only if every graph in it was
searched to exhaustion (not budget-capped).
"""

import argparse
import itertools
import json
import os
import subprocess
import sys
from shutil import which

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import h2_oracle as H  # noqa: E402
import planarity_search as PS  # noqa: E402

try:
    import networkx as nx
except Exception:
    nx = None


def geng_path():
    for cand in ("geng", "nauty-geng"):
        p = which(cand)
        if p:
            return p
    raise RuntimeError("nauty geng not found on PATH")


def max_local_edge_conn(G):
    """Max over vertex pairs of local edge-connectivity λ'(u,v) (= max edge weight
    in a Gomory-Hu tree with unit capacities).  Lemma: 2-extremal ⇒ this ≤ 4
    (since for Eulerian D, λ_D(u,v) ≥ λ'_U(u,v)/2, and λ(D)=2). Strictly stronger
    than κ'(U)≤4 (the min)."""
    import networkx as _nx
    if G.number_of_nodes() < 2:
        return 0
    H = _nx.Graph()
    H.add_nodes_from(G.nodes())
    H.add_edges_from((u, v, {"capacity": 1}) for u, v in G.edges())
    T = _nx.gomory_hu_tree(H, capacity="capacity")
    return int(max((d["weight"] for _, _, d in T.edges(data=True)), default=0))


def _is_forest_edges(n, edge_list):
    """True iff edge_list is acyclic (≤ n-1 edges, no cycle) via union-find."""
    if len(edge_list) > n - 1:
        return False
    p = list(range(n))

    def find(x):
        while p[x] != x:
            p[x] = p[p[x]]
            x = p[x]
        return x
    for (u, v) in edge_list:
        ru, rv = find(u), find(v)
        if ru == rv:
            return False
        p[ru] = rv
    return True


def two_extremal_orientation_budgeted(n, edges, budget):
    """First 2-extremal orientation of G, or 'capped' if the (digon-coset ×
    Eulerian-orientation) search exceeds `budget` candidate digraphs, else None.

    Restricts digon-sets to FORESTS: F_D is provably a forest for any 2-extremal
    digraph, so this loses no orientation and prunes most parity-cosets."""
    count = 0
    for dig in PS._digon_cosets(n, edges):
        digon_edges = [edges[i] for i in dig]
        if not _is_forest_edges(n, digon_edges):
            continue
        singles = [edges[i] for i in range(len(edges)) if i not in dig]
        degdig = [0] * n
        for (u, v) in digon_edges:
            degdig[u] += 1
            degdig[v] += 1
        degsin = [0] * n
        for (u, v) in singles:
            degsin[u] += 1
            degsin[v] += 1
        if any(degdig[v] + degsin[v] // 2 < 2 for v in range(n)):
            continue
        base = set()
        for (u, v) in digon_edges:
            base.add((u, v))
            base.add((v, u))
        for orient in PS._eulerian_orientations(n, singles):
            count += 1
            if count > budget:
                return "capped"
            arcs = frozenset(base | set(orient))
            if H.is_2extremal(n, arcs):
                return sorted(arcs)
    return None


def load_ckpt(path):
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return {"n": None, "buckets": {}, "counterexamples": []}


def save_ckpt(path, ck):
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(ck, f, indent=1)
    os.replace(tmp, path)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=8)
    ap.add_argument("--emax", type=int, default=None,
                    help="max edge count (default: n(n-1)/2)")
    ap.add_argument("--budget", type=int, default=2_000_000,
                    help="per-graph candidate-digraph budget before 'capped'")
    args = ap.parse_args(argv)
    if nx is None:
        print("networkx required (root .venv)")
        return 1
    n = args.n
    emax = args.emax or (n * (n - 1) // 2)
    GENG = geng_path()
    ckpt_path = os.path.join(ROOT, "data", f"n{n}_disproof_ckpt.json")
    ck = load_ckpt(ckpt_path)
    ck["n"] = n

    print(f"# n={n} non-planar 2-extremal disproof hunt  (budget {args.budget}/graph)")
    print(f"# checkpoint: {ckpt_path}")
    for ec in range(9, emax + 1):
        key = str(ec)
        if key in ck["buckets"] and ck["buckets"][key].get("done"):
            b = ck["buckets"][key]
            print(f"  |E|={ec}: (resumed) nonplanar={b['nonplanar']} "
                  f"tested={b['tested']} capped={b['capped']} found={b['found']}",
                  flush=True)
            continue
        out = subprocess.run([GENG, "-C", "-d2", str(n), f"{ec}:{ec}"],
                             capture_output=True, text=True).stdout
        nonplanar = lemma = tested = capped = found = 0
        for line in out.splitlines():
            G = nx.from_graph6_bytes(line.strip().encode())
            if nx.check_planarity(G)[0]:
                continue
            nonplanar += 1
            # Edge-connectivity lemma (strong form): 2-extremal ⇒ max local
            # edge-connectivity λ'(U) ≤ 4. So any pair with ≥5 edge-disjoint paths
            # ⇒ certified (cannot be 2-extremal) without any orientation search.
            if max_local_edge_conn(G) >= 5:
                lemma += 1
                continue
            E = [tuple(sorted(e)) for e in G.edges()]
            r = two_extremal_orientation_budgeted(n, E, args.budget)
            if r == "capped":
                capped += 1
            elif r is not None:
                found += 1
                print(f"  !!! COUNTEREXAMPLE n={n} |E|={ec}: {r}", flush=True)
                ck["counterexamples"].append({"n": n, "arcs": r})
            else:
                tested += 1
        ck["buckets"][key] = {"nonplanar": nonplanar, "lemma": lemma,
                              "tested": tested, "capped": capped,
                              "found": found, "done": True}
        save_ckpt(ckpt_path, ck)
        print(f"  |E|={ec}: nonplanar={nonplanar} lemma-certified(κ'≥5)={lemma} "
              f"searched-tested={tested} capped={capped} found={found}", flush=True)

    total_np = sum(b["nonplanar"] for b in ck["buckets"].values())
    total_lemma = sum(b.get("lemma", 0) for b in ck["buckets"].values())
    total_capped = sum(b["capped"] for b in ck["buckets"].values())
    total_found = sum(b["found"] for b in ck["buckets"].values())
    print(f"# DONE n={n}: non-planar graphs={total_np} "
          f"(lemma-certified κ'≥5: {total_lemma}; searched+capped: "
          f"{total_np-total_lemma}) capped(uncertified)={total_capped} "
          f"counterexamples={total_found}")
    print("# certified buckets (0 capped):",
          [k for k, b in sorted(ck["buckets"].items(), key=lambda kv: int(kv[0]))
           if b["capped"] == 0])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
