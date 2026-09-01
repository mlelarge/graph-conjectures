"""Independently verify the workflow's Lemma A claims, over EVERY leaf block of
every non-2-connected pendant-free diam>=4 graph at n=8,9,10.

For a leaf block (B,u): S=B\\{u}, R=G-S. For each distinct G-line L:
  S-trace = L cap S, R-trace = L cap R.
  Z  = #lines with S-trace in {empty, S}
  P  = #lines with proper-nonempty S-trace  (empty != L cap S != S)
Checks (the PROVEN part):
  (T0) ell(G) = Z + P
  (T1) Z >= ell(R)                       (injection lines(R) -> Z-class)
  (T2) ell(G) >= ell(R) + P              (the proven standalone theorem)
Open inequality (= Lemma A, re-expressed): with Q := Z - ell(R) (>=0 by T1),
  (C2) P + Q >= |S| + max(0, |R| - ell(R))
Reports per-block min margins of C2 (easy branch deficit=0 and deficit branch),
and min over BEST block (what Lemma A actually needs).
Also re-checks the workflow's dead-route counterexamples:
  Claim(II) Q_rmirror := #{L: empty != L cap R != R} >= |R|   -- claimed FALSE at I?AB?rCM?
"""
import sys, subprocess, itertools
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
import networkx as nx


def leaf_blocks(g):
    arts = set(nx.articulation_points(g))
    out = []
    for block in nx.biconnected_components(g):
        block = set(block); cuts = block & arts
        if len(cuts) == 1 and len(block) >= 3:
            out.append((block, next(iter(cuts))))
    return out


def block_data(g6):
    n, edges = core.graph6_to_edges(g6)
    g = nx.Graph(); g.add_nodes_from(range(n)); g.add_edges_from(edges)
    distG = core.all_pairs_distances(n, edges)
    glines = set()
    for a, b in itertools.combinations(range(n), 2):
        glines.add(core.line_of_pair(distG, n, a, b))
    ellG = len(glines)
    rows = []
    for (B, u) in leaf_blocks(g):
        S = B - {u}; Rv = set(range(n)) - S
        Rmap = {v: i for i, v in enumerate(sorted(Rv))}
        Re = [(Rmap[a], Rmap[b]) for a, b in g.subgraph(Rv).edges()]
        distR = core.all_pairs_distances(len(Rv), Re)
        linesR = set()
        for a, b in itertools.combinations(range(len(Rv)), 2):
            linesR.add(core.line_of_pair(distR, len(Rv), a, b))
        ellR = len(linesR)
        Z = P = 0
        Qrmir = 0
        for L in glines:
            st = L & S; rt = L & Rv
            if st == set() or st == S:
                Z += 1
            else:
                P += 1
            if rt != set() and rt != Rv:
                Qrmir += 1
        Q = Z - ellR
        deficit = max(0, len(Rv) - ellR)
        rows.append(dict(
            u=u, nS=len(S), nR=len(Rv), ellR=ellR, ellG=ellG, Z=Z, P=P, Q=Q,
            T0=(ellG == Z + P), T1=(Z >= ellR), T2=(ellG >= ellR + P),
            c2_margin=(P + Q) - (len(S) + deficit),
            easy_Pge=(P - len(S)) if deficit == 0 else None,
            deficit=deficit, Qrmir=Qrmir, Qrmir_ge_R=(Qrmir >= len(Rv)),
        ))
    return rows


def run(n):
    proc = subprocess.run(
        ["geng", "-c", "-d2", "-q", str(n)],
        capture_output=True,
        text=True,
        check=True,
    )
    t0v = t1v = t2v = 0
    min_c2_best = 10**9
    min_c2_anyblock = 10**9
    min_easy_P = 10**9
    qrmir_fail = []
    nb = 0
    for line in proc.stdout.splitlines():
        g6 = line.strip()
        if not g6: continue
        n2, edges = core.graph6_to_edges(g6)
        if core.has_pendant_edge(n2, edges): continue
        dist = core.all_pairs_distances(n2, edges)
        if max(dist[i][j] for i in range(n2) for j in range(n2)) < 4: continue
        g = nx.Graph(); g.add_nodes_from(range(n2)); g.add_edges_from(edges)
        if nx.is_biconnected(g): continue
        nb += 1
        rows = block_data(g6)
        for r in rows:
            if not r["T0"]: t0v += 1
            if not r["T1"]: t1v += 1
            if not r["T2"]: t2v += 1
            min_c2_anyblock = min(min_c2_anyblock, r["c2_margin"])
            if r["easy_Pge"] is not None:
                min_easy_P = min(min_easy_P, r["easy_Pge"])
            if not r["Qrmir_ge_R"]:
                if len(qrmir_fail) < 5:
                    qrmir_fail.append((g6, r["u"], r["Qrmir"], r["nR"]))
        best = max(r["c2_margin"] for r in rows)
        min_c2_best = min(min_c2_best, best)
    return dict(n=n, non_biconnected=nb,
                T0_violations=t0v, T1_violations=t1v, T2_violations=t2v,
                min_c2_margin_BEST_block=min_c2_best,
                min_c2_margin_any_block=min_c2_anyblock,
                min_easy_branch_P_minus_S=(None if min_easy_P == 10**9 else min_easy_P),
                Qrmirror_ge_R_fails=qrmir_fail)


if __name__ == "__main__":
    import json
    for n in (int(x) for x in (sys.argv[1:] or [8, 9])):
        print(json.dumps(run(n)))
