"""INDEPENDENT review of the (4') reduction produced by the workflow.

For a 2-connected graph B with marked u (mode --marked: B = whole geng -C graph;
default: H5 leaf blocks), S=V(B)\\{u}, d=d_B:
  Sigma_s = {x in S : comparable(u,x,s)} ;  fibers = group by Sigma_s ;
  rep = shallowest (min depth, tie min id) member of each fiber ; non-reps = rest.
  A_s = line_B(u,s) cap S .  Adist = #distinct A_s != S (over ALL s).
  a = #distinct A_s over NON-reps ;  excess = #non-reps - a .
  D' = #distinct B-lines avoiding u, != S .  B1 = sum_fibers max(0,size-2).
  margin4 = nSigma + Adist + D' - |S|.
Checks (0 failures expected unless noted):
  F3        : every non-rep has A_s != S         [claimed PROVED]
  AdistGEa  : Adist >= a                          [follows from F3]
  IDENT     : margin4 == (Adist-a)+(D'-excess)    [pure algebra sanity]
  four      : margin4 >= 0  (= (4'))
  Dge_exc   : D' >= excess                        [the reduced GAP]
  DgeB1     : D' >= B1                            [the proposed partial]
Reports failures + min slacks + first counterexamples.
"""
import sys, subprocess, itertools, json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
import networkx as nx


def comparable(d, u, x, y):
    return d[u][x] + d[x][y] == d[u][y] or d[u][y] + d[y][x] == d[u][x]


def leaf_blocks(g):
    arts = set(nx.articulation_points(g)); out = []
    for B in nx.biconnected_components(g):
        B = set(B); cuts = B & arts
        if len(cuts) == 1 and len(B) >= 3:
            out.append((B, next(iter(cuts))))
    return out


def block_quantities(Blist, dB, Bidx, u):
    """All (4')-reduction quantities for block on Blist (relabelled metric dB)."""
    ui = Bidx[u]
    S = [v for v in Blist if v != u]
    fS = frozenset(S)
    # Sigma, depth
    Sig = {}
    for s in S:
        si = Bidx[s]
        Sig[s] = frozenset(x for x in S if comparable(dB, ui, Bidx[x], si))
    fibers = {}
    for s in S:
        fibers.setdefault(Sig[s], []).append(s)
    nSigma = len(fibers)
    reps = set()
    for mem in fibers.values():
        reps.add(min(mem, key=lambda s: (dB[ui][Bidx[s]], s)))
    nonreps = [s for s in S if s not in reps]
    # apex A_s = line_B(u,s) cap S
    A = {}
    for s in S:
        L = core.line_of_pair(dB, len(Blist), ui, Bidx[s])
        A[s] = frozenset(Blist[i] for i in L) & fS
    Adist = len({v for v in A.values() if v != fS})
    a = len({A[s] for s in nonreps})
    excess = len(nonreps) - a
    # D'
    Dp = set()
    for x, y in itertools.combinations(range(len(Blist)), 2):
        L = core.line_of_pair(dB, len(Blist), x, y)
        Lv = frozenset(Blist[i] for i in L)
        if u not in Lv and Lv != fS:
            Dp.add(Lv)
    Dprime = len(Dp)
    B1 = sum(max(0, len(mem) - 2) for mem in fibers.values())
    margin4 = nSigma + Adist + Dprime - len(S)
    F3_bad = sum(1 for s in nonreps if A[s] == fS)
    return dict(nS=len(S), nSigma=nSigma, Adist=Adist, a=a, excess=excess,
                Dprime=Dprime, B1=B1, margin4=margin4, F3_bad=F3_bad,
                nonreps=len(nonreps))


def iter_blocks(order, marked):
    if marked:
        proc = subprocess.run(
            ["geng", "-C", "-q", str(order)],
            capture_output=True,
            text=True,
            check=True,
        )
        for line in proc.stdout.splitlines():
            g6 = line.strip()
            if not g6: continue
            n, edges = core.graph6_to_edges(g6)
            Blist = list(range(n)); Bidx = {v: v for v in Blist}
            dB = core.all_pairs_distances(n, edges)
            for u in range(n):
                yield g6, Blist, dB, Bidx, u
    else:
        proc = subprocess.run(
            ["geng", "-c", "-d2", "-q", str(order)],
            capture_output=True,
            text=True,
            check=True,
        )
        for line in proc.stdout.splitlines():
            g6 = line.strip()
            if not g6: continue
            n, edges = core.graph6_to_edges(g6)
            if core.has_pendant_edge(n, edges): continue
            dG = core.all_pairs_distances(n, edges)
            if max(dG[i][j] for i in range(n) for j in range(n)) < 4: continue
            g = nx.Graph(); g.add_nodes_from(range(n)); g.add_edges_from(edges)
            if nx.is_biconnected(g): continue
            for (B, u) in leaf_blocks(g):
                Blist = sorted(B); Bidx = {v: i for i, v in enumerate(Blist)}
                Be = [(Bidx[a], Bidx[b]) for a, b in g.subgraph(B).edges()]
                dB = core.all_pairs_distances(len(Blist), Be)
                yield g6, Blist, dB, Bidx, u


def run(order, marked):
    F = dict(order=order, mode=("marked" if marked else "leaf"), blocks=0,
             F3_fail=0, AdistGEa_fail=0, IDENT_fail=0, four_fail=0,
             Dge_exc_fail=0, DgeB1_fail=0, min_Dme=10**9, min_DmB1=10**9,
             ce_F3=None, ce_De=None)
    for g6, Blist, dB, Bidx, u in iter_blocks(order, marked):
        q = block_quantities(Blist, dB, Bidx, u)
        F["blocks"] += 1
        if q["F3_bad"] > 0:
            F["F3_fail"] += 1
            if F["ce_F3"] is None: F["ce_F3"] = (g6, u, q)
        if q["Adist"] < q["a"]: F["AdistGEa_fail"] += 1
        if q["margin4"] != (q["Adist"] - q["a"]) + (q["Dprime"] - q["excess"]):
            F["IDENT_fail"] += 1
        if q["margin4"] < 0: F["four_fail"] += 1
        if q["Dprime"] < q["excess"]:
            F["Dge_exc_fail"] += 1
            if F["ce_De"] is None: F["ce_De"] = (g6, u, q)
        if q["Dprime"] < q["B1"]: F["DgeB1_fail"] += 1
        if q["excess"] > 0:
            F["min_Dme"] = min(F["min_Dme"], q["Dprime"] - q["excess"])
        if q["B1"] > 0:
            F["min_DmB1"] = min(F["min_DmB1"], q["Dprime"] - q["B1"])
    if F["min_Dme"] == 10**9: F["min_Dme"] = None
    if F["min_DmB1"] == 10**9: F["min_DmB1"] = None
    return F


if __name__ == "__main__":
    marked = "--marked" in sys.argv
    args = [x for x in sys.argv[1:] if x.isdigit()]
    for n in (int(x) for x in (args or [5, 6, 7])):
        print(json.dumps(run(n, marked)))
