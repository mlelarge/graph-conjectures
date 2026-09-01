"""INDEPENDENT review of the T1link proof. Different code path from the user's
gates: apex/Adist computed directly as L_G(u,s) cap S (and R-trace of L_G(u,s)
checked == R), partition checked exhaustive, subsidiary lemmas checked.

Per leaf block, over all non-2-connected pendant-free diam>=4 graphs:
 (PART)  Pmix+Pup+Pin == P  (partition of proper-S-trace lines by R-trace)
 (UPPER) for every s: R-trace of L_G(u,s) == R   (so apex line is a P_upper line)
 (AX)    Adist via G (L_G(u,s) cap S) == Adist via dB (gate)   [cross-check]
 (Lmix=) Pmix == nSigmaP*nT_proper
 (Lup>=) Pup  >= Adist
 (Lin==) Pin  == Dprime
 (PINdef)Pin  == #{G-lines L : empty != L proper-subset-of S}
 (sub)   nSigma>=2, nT_proper>=2, nSigmaP>=nSigma-1
 (T1)    P >= nSigma + Adist + Dprime
 (STRONG)P >= nSigmaP*nT_proper + Adist + Dprime
"""
import sys, subprocess, itertools, json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
import networkx as nx


def leaf_blocks(g):
    arts = set(nx.articulation_points(g)); out = []
    for B in nx.biconnected_components(g):
        B = set(B); cuts = B & arts
        if len(cuts) == 1 and len(B) >= 3:
            out.append((B, next(iter(cuts))))
    return out


def run(n):
    proc = subprocess.run(
        ["geng", "-c", "-d2", "-q", str(n)],
        capture_output=True,
        text=True,
        check=True,
    )
    F = dict(n=n, blocks=0, PART=0, UPPER=0, AX=0, Lmix_eq=0, Lup=0, Lin_eq=0,
             PINdef=0, nSigma_lt2=0, nTp_lt2=0, nSigmaP=0, T1=0, STRONG=0,
             min_T1=10**9, min_strong=10**9, ce=None)
    for line in proc.stdout.splitlines():
        g6 = line.strip()
        if not g6: continue
        m, edges = core.graph6_to_edges(g6)
        if core.has_pendant_edge(m, edges): continue
        dG = core.all_pairs_distances(m, edges)
        if max(dG[i][j] for i in range(m) for j in range(m)) < 4: continue
        g = nx.Graph(); g.add_nodes_from(range(m)); g.add_edges_from(edges)
        if nx.is_biconnected(g): continue
        gl = {core.line_of_pair(dG, m, a, b) for a, b in itertools.combinations(range(m), 2)}
        for (B, u) in leaf_blocks(g):
            F["blocks"] += 1
            S = set(B) - {u}; Rv = set(range(m)) - S
            fS = frozenset(S); fR = frozenset(Rv)
            p0 = next(iter(Rv - {u})); s0 = next(iter(S))
            # CROSS traces from G
            Sig = {s: frozenset(core.line_of_pair(dG, m, s, p0) & S) for s in S}
            Tp = {p: frozenset(core.line_of_pair(dG, m, s0, p) & Rv) for p in (Rv - {u})}
            nSigma = len(set(Sig.values()))
            nSigmaP = len({v for v in set(Sig.values()) if v != fS})
            nT_proper = len({v for v in set(Tp.values()) if v != fR})
            # apex via G directly: A_s = L_G(u,s) cap S ; check R-trace == R
            Aset = {}
            for s in S:
                Lus = core.line_of_pair(dG, m, u, s)
                if frozenset(Lus & Rv) != fR:
                    F["UPPER"] += 1
                Aset[s] = frozenset(Lus & S)
            Adist_G = len({v for v in Aset.values() if v != fS})
            # apex via dB (gate's way)
            Blist = sorted(B); Bi = {v: i for i, v in enumerate(Blist)}
            Be = [(Bi[a], Bi[b]) for a, b in g.subgraph(B).edges()]
            dB = core.all_pairs_distances(len(Blist), Be)
            ApexB = {}
            for s in S:
                L = core.line_of_pair(dB, len(Blist), Bi[u], Bi[s])
                ApexB[s] = frozenset(Blist[i] for i in L) - {u}
            Adist_B = len({v for v in ApexB.values() if v != fS})
            if Adist_G != Adist_B:
                F["AX"] += 1
            # D' via dB
            Dp = set()
            for a, b in itertools.combinations(Blist, 2):
                L = core.line_of_pair(dB, len(Blist), Bi[a], Bi[b])
                Lv = frozenset(Blist[i] for i in L)
                if u not in Lv and Lv != fS:
                    Dp.add(Lv)
            Dprime = len(Dp)
            # partition of P by R-trace, on G
            Pmix = Pup = Pin = 0
            Pin_def = 0
            for L in gl:
                st = L & S; rt = L & Rv
                if st and st != S:
                    if rt == Rv: Pup += 1
                    elif not rt: Pin += 1
                    else: Pmix += 1
                if L and L <= S and L != S:  # nonempty proper subset of S
                    Pin_def += 1
            P = Pmix + Pup + Pin
            nS = len(S)
            # checks
            if Pmix + Pup + Pin != P: F["PART"] += 1   # trivially true; kept for shape
            if Pmix != nSigmaP * nT_proper: F["Lmix_eq"] += 1
            if Pup < Adist_B: F["Lup"] += 1
            if Pin != Dprime: F["Lin_eq"] += 1
            if Pin != Pin_def: F["PINdef"] += 1
            if nSigma < 2: F["nSigma_lt2"] += 1
            if nT_proper < 2: F["nTp_lt2"] += 1
            if nSigmaP < nSigma - 1: F["nSigmaP"] += 1
            t1 = P - (nSigma + Adist_B + Dprime)
            strong = P - (nSigmaP * nT_proper + Adist_B + Dprime)
            if t1 < 0:
                F["T1"] += 1
                if F["ce"] is None:
                    F["ce"] = dict(g6=g6, u=u, nS=nS, nSigma=nSigma, Adist=Adist_B,
                                   Dprime=Dprime, P=P, Pmix=Pmix, Pup=Pup, Pin=Pin, t1=t1)
            if strong < 0: F["STRONG"] += 1
            F["min_T1"] = min(F["min_T1"], t1)
            F["min_strong"] = min(F["min_strong"], strong)
    return F


if __name__ == "__main__":
    for n in (int(x) for x in (sys.argv[1:] or [8, 9])):
        print(json.dumps(run(n)))
