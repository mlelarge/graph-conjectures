"""CONSOLIDATED verification of the rigorous easy-branch chain for C2.

Per leaf block (B,u), S=B\\{u}, R=G-S:
  (M)   d_G(r,s) = d_R(r,u)+d_B(u,s)  for r in R, s in S.
  (CRS) line_G(s,p) = Sigma_s ⊔ T_p ; Sigma_s indep of p, T_p indep of s;
        #distinct mixed lines = nSigma*nT (no collapse).
  (R2)  R: every vertex != u has deg_R >= 2  (pendant-free except at u).
  (rays) nSigma >= 2 ; nT_proper >= 2.
  (Lmix)   #P_mix >= nSigmaP*nT_proper  (>= nSigma).
  (Lup)    #P_upper (R-trace=R) >= Adist (#distinct proper apex traces).
  (Lin)    #P_inside (R-trace=empty) == D' (#lines of B avoiding u, != S).
  (4')     nSigma + Adist + D' >= |S|.
  (final)  P >= |S|.
Reports failure counts + min margins. Any non-zero *_fail refutes a sub-claim.
"""
import sys, subprocess, itertools, json
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


def run(n):
    proc = subprocess.run(
        ["geng", "-c", "-d2", "-q", str(n)],
        capture_output=True,
        text=True,
        check=True,
    )
    agg = dict(n=n, nb=0, blocks=0,
               M_fail=0, CRS_indep_fail=0, CRS_collapse_fail=0,
               R2_fail=0, nSigma_lt2=0, nTp_lt2=0,
               Lmix_fail=0, Lup_fail=0, Lin_fail=0, four_fail=0, P_lt_S=0,
               min_four=10**9, min_PmS=10**9, ex=[])
    for line in proc.stdout.splitlines():
        g6 = line.strip()
        if not g6: continue
        n2, edges = core.graph6_to_edges(g6)
        if core.has_pendant_edge(n2, edges): continue
        distG = core.all_pairs_distances(n2, edges)
        if max(distG[i][j] for i in range(n2) for j in range(n2)) < 4: continue
        g = nx.Graph(); g.add_nodes_from(range(n2)); g.add_edges_from(edges)
        if nx.is_biconnected(g): continue
        agg["nb"] += 1
        glines = set()
        for a, b in itertools.combinations(range(n2), 2):
            glines.add(core.line_of_pair(distG, n2, a, b))
        for (B, u) in leaf_blocks(g):
            agg["blocks"] += 1
            S = set(B) - {u}; Rv = set(range(n2)) - S
            fS = frozenset(S); fR = frozenset(Rv)
            Slist = sorted(S); Rother = [p for p in sorted(Rv) if p != u]
            # induced B and R metrics
            Blist = sorted(B); Bidx = {v: i for i, v in enumerate(Blist)}
            Be = [(Bidx[a], Bidx[b]) for a, b in g.subgraph(B).edges()]
            dB = core.all_pairs_distances(len(Blist), Be)
            Rlist = sorted(Rv); Ridx = {v: i for i, v in enumerate(Rlist)}
            Re = [(Ridx[a], Ridx[b]) for a, b in g.subgraph(Rv).edges()]
            dR = core.all_pairs_distances(len(Rlist), Re)
            # (M)
            for s in Slist:
                for r in Rlist:
                    if distG[s][r] != dB[Bidx[u]][Bidx[s]] + dR[Ridx[u]][Ridx[r]]:
                        agg["M_fail"] += 1
            # (R2)
            for r in Rlist:
                if r == u: continue
                if g.degree(r) < 2: agg["R2_fail"] += 1
            # rays Sigma_s (indep of p check), T_p (indep of s), CROSS collapse
            Sig = {}
            for s in Slist:
                tr = set(frozenset(core.line_of_pair(distG, n2, s, p) & S) for p in Rother)
                if len(tr) != 1: agg["CRS_indep_fail"] += 1
                Sig[s] = next(iter(tr))
            Tp = {}
            for p in Rother:
                tr = set(frozenset(core.line_of_pair(distG, n2, s, p) & Rv) for s in Slist)
                if len(tr) != 1: agg["CRS_indep_fail"] += 1
                Tp[p] = next(iter(tr))
            mixed = set()
            for s in Slist:
                for p in Rother:
                    mixed.add(core.line_of_pair(distG, n2, s, p))
            nSigma = len(set(Sig.values()))
            nT = len(set(Tp.values()))
            if len(mixed) != nSigma * nT:   # no-collapse: #mixed lines = nSigma*nT
                agg["CRS_collapse_fail"] += 1
            nSigmaP = sum(1 for v in set(Sig.values()) if v != fS)
            nT_proper = sum(1 for v in set(Tp.values()) if v != fR)
            if nSigma < 2: agg["nSigma_lt2"] += 1
            if nT_proper < 2: agg["nTp_lt2"] += 1
            # apex traces & D'  (map line_of_pair INDICES back to Blist labels)
            Apex = {}
            for s in Slist:
                L = core.line_of_pair(dB, len(Blist), Bidx[u], Bidx[s])
                Lv = frozenset(Blist[i] for i in L) - {u}
                Apex[s] = Lv
            Adist = len(set(v for v in Apex.values() if v != fS))
            Dp = set()
            for a, b in itertools.combinations(Blist, 2):
                L = core.line_of_pair(dB, len(Blist), Bidx[a], Bidx[b])
                Lv = frozenset(Blist[i] for i in L)
                if u not in Lv and Lv != fS: Dp.add(Lv)
            Dprime = len(Dp)
            # actual P families
            Pmix = Pup = Pin = 0
            for L in glines:
                st = L & S; rt = L & Rv
                if st and st != fS:
                    if rt == fR: Pup += 1
                    elif not rt: Pin += 1
                    else: Pmix += 1
            P = Pmix + Pup + Pin
            if Pmix < nSigmaP * nT_proper: agg["Lmix_fail"] += 1
            if Pup < Adist: agg["Lup_fail"] += 1
            if Pin != Dprime: agg["Lin_fail"] += 1
            if nSigma + Adist + Dprime < len(Slist): agg["four_fail"] += 1
            if P < len(Slist): agg["P_lt_S"] += 1
            agg["min_four"] = min(agg["min_four"], nSigma + Adist + Dprime - len(Slist))
            agg["min_PmS"] = min(agg["min_PmS"], P - len(Slist))
    return agg


if __name__ == "__main__":
    for n in (int(x) for x in (sys.argv[1:] or [8, 9])):
        print(json.dumps(run(n)))
