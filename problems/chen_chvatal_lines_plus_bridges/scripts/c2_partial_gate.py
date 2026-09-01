"""Independently verify the C2-closer's headline claims, over every leaf block of
every non-2-connected pendant-free diam>=4 graph at n=8,9,10.

Sigma_s = line_G(s,p0) cap S  (u-ray of B at s; indep of p0 by CROSS)
T_p     = line_G(s0,p) cap R  (u-ray of R at p; indep of s0)
nSigma  = #distinct Sigma_s ; nSigmaP = #distinct proper (!=S) Sigma_s
nT      = #distinct T_p
Checks:
 (LEVER)  P >= nSigmaP * nT
 (n2)     nSigma>=2, nT>=2
 (EASY)   in no-deficit blocks: P >= |S| ; and coverage of {nSigmaP*nT >= |S|}
 (RESID)  blocks with nSigmaP*nT < |S| all have nT==2
 (DEFICIT)in deficit blocks: |S|+max(ell(R),|R|) == n  (so C2 == ell(G)>=n)
 (COUPLED)(P-|S|)+Q >= deficit  with margin
"""
import sys, subprocess, itertools
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
import networkx as nx


def leaf_blocks(g):
    arts = set(nx.articulation_points(g)); out = []
    for block in nx.biconnected_components(g):
        block = set(block); cuts = block & arts
        if len(cuts) == 1 and len(block) >= 3:
            out.append((block, next(iter(cuts))))
    return out


def analyze_block(n, edges, distG, glines, ellG, B, u):
    S = B - {u}; Rv = set(range(n)) - S
    p0 = next(iter(Rv - {u}))
    s0 = next(iter(S))
    Sig = {frozenset(core.line_of_pair(distG, n, s, p0) & S) for s in S}
    T = {frozenset(core.line_of_pair(distG, n, s0, p) & Rv) for p in (Rv - {u})}
    nSigma = len(Sig); nSigmaP = len({x for x in Sig if x != S}); nT = len(T)
    # R standalone ell
    Rmap = {v: i for i, v in enumerate(sorted(Rv))}
    g = nx.Graph(); g.add_nodes_from(range(n)); g.add_edges_from(edges)
    Re = [(Rmap[a], Rmap[b]) for a, b in g.subgraph(Rv).edges()]
    distR = core.all_pairs_distances(len(Rv), Re)
    linesR = {core.line_of_pair(distR, len(Rv), a, b) for a, b in itertools.combinations(range(len(Rv)), 2)}
    ellR = len(linesR)
    Z = sum(1 for L in glines if (L & S) in (set(), S))
    P = len(glines) - Z
    Q = Z - ellR
    deficit = max(0, len(Rv) - ellR)
    return dict(nS=len(S), nR=len(Rv), ellR=ellR, P=P, Q=Q, Z=Z,
                nSigma=nSigma, nSigmaP=nSigmaP, nT=nT, deficit=deficit,
                lever_ok=(P >= nSigmaP * nT), n2_ok=(nSigma >= 2 and nT >= 2),
                easyP=(P - len(S)),
                covered=(nSigmaP * nT >= len(S)),
                resid=(nSigmaP * nT < len(S)),
                resid_nT2=(nT == 2),
                deficit_eq_n=(len(S) + max(ellR, len(Rv)) == n),
                coupled=( (P - len(S)) + Q - deficit ))


def run(n):
    proc = subprocess.run(
        ["geng", "-c", "-d2", "-q", str(n)],
        capture_output=True,
        text=True,
        check=True,
    )
    nb = 0; lever_fail = n2_fail = 0
    easy_fail = 0; resid_total = 0; resid_not_nT2 = 0
    deficit_total = 0; deficit_eq_fail = 0; coupled_fail = 0
    min_coupled = 10**9; min_easyP = 10**9
    covered_easy = 0; easy_total = 0
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
        distG = dist
        glines = {core.line_of_pair(distG, n2, a, b) for a, b in itertools.combinations(range(n2), 2)}
        ellG = len(glines)
        for (B, u) in leaf_blocks(g):
            r = analyze_block(n2, edges, distG, glines, ellG, B, u)
            if not r["lever_ok"]: lever_fail += 1
            if not r["n2_ok"]: n2_fail += 1
            if r["resid"]:
                resid_total += 1
                if not r["resid_nT2"]: resid_not_nT2 += 1
            if r["deficit"] > 0:
                deficit_total += 1
                if not r["deficit_eq_n"]: deficit_eq_fail += 1
                if r["coupled"] < 0: coupled_fail += 1
                min_coupled = min(min_coupled, r["coupled"])
            else:
                easy_total += 1
                if r["covered"]: covered_easy += 1
                if r["easyP"] < 0: easy_fail += 1
                min_easyP = min(min_easyP, r["easyP"])
    return dict(n=n, non_biconnected=nb,
                LEVER_failures=lever_fail, n2_failures=n2_fail,
                EASY_Pge_S_failures=easy_fail, min_easy_P_minus_S=(None if min_easyP==10**9 else min_easyP),
                easy_blocks=easy_total, covered_by_product=covered_easy,
                residual_blocks=resid_total, residual_not_nT2=resid_not_nT2,
                deficit_blocks=deficit_total, deficit_eq_n_failures=deficit_eq_fail,
                COUPLED_failures=coupled_fail, min_coupled_margin=(None if min_coupled==10**9 else min_coupled))


if __name__ == "__main__":
    import json
    for n in (int(x) for x in (sys.argv[1:] or [8, 9])):
        print(json.dumps(run(n)))
