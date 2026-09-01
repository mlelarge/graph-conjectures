"""Examine TIGHT cases of the B-only bound nSigma+Adist+D' = |S| to guide a proof,
and verify the three lifting lemmas hold EXACTLY (so the chain is sound):
  L_mix:   #P_mix lines >= nSigma
  L_upper: #P_upper lines (R-trace=R) >= Adist  (and = #distinct proper apex traces)
  L_inside:#P_inside lines (R-trace=empty) >= D' (and = #proper lines of B avoiding u)
We recompute P_mix/P_upper/P_inside on G directly and compare to nSigma/Adist/D'.
"""
import sys, subprocess, itertools, json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
import networkx as nx
from collections import defaultdict


def leaf_blocks(g):
    arts = set(nx.articulation_points(g))
    out = []
    for block in nx.biconnected_components(g):
        block = set(block); cuts = block & arts
        if len(cuts) == 1 and len(block) >= 3:
            out.append((block, next(iter(cuts))))
    return out


def analyze(g6, dump=False):
    n, edges = core.graph6_to_edges(g6)
    g = nx.Graph(); g.add_nodes_from(range(n)); g.add_edges_from(edges)
    distG = core.all_pairs_distances(n, edges)
    glines = set()
    for a, b in itertools.combinations(range(n), 2):
        glines.add(core.line_of_pair(distG, n, a, b))
    rows = []
    for (B, u) in leaf_blocks(g):
        S = set(B) - {u}; Rv = set(range(n)) - S
        fS = frozenset(S); fR = frozenset(Rv)
        Blist = sorted(B); Bidx = {v: i for i, v in enumerate(Blist)}
        Be = [(Bidx[a], Bidx[b]) for a, b in g.subgraph(B).edges()]
        dB = core.all_pairs_distances(len(Blist), Be)
        ui = Bidx[u]
        Slist = [v for v in Blist if v != u]
        Sigma = {}; A = {}
        for s in Slist:
            si = Bidx[s]
            ray = set(); apex = set()
            for sp in Slist:
                spi = Bidx[sp]
                usp = dB[ui][spi]; sps = dB[spi][si]; us = dB[ui][si]
                if (usp + sps == us) or (us + sps == usp):
                    ray.add(sp); apex.add(sp)
                elif usp + us == sps:
                    apex.add(sp)
            Sigma[s] = frozenset(ray); A[s] = frozenset(apex)
        nSigma = len(set(Sigma.values()))
        Adist = len(set(v for v in A.values() if v != fS))
        Dlines = set()
        for a, b in itertools.combinations(Blist, 2):
            L = core.line_of_pair(dB, len(Blist), Bidx[a], Bidx[b])
            Lv = frozenset(Blist[i] for i in L)
            if u not in Lv and Lv != fS:
                Dlines.add(Lv)
        D = len(Dlines)
        # G-side actual counts
        Pmix = Pup = Pin = 0
        for L in glines:
            st = L & S; rt = L & Rv
            if st and st != fS:
                if rt == fR: Pup += 1
                elif not rt: Pin += 1
                else: Pmix += 1
        rows.append(dict(
            u=u, nS=len(Slist), nSigma=nSigma, Adist=Adist, D=D,
            Pmix=Pmix, Pup=Pup, Pin=Pin,
            margin=nSigma + Adist + D - len(Slist),
            Lmix_ok=(Pmix >= nSigma), Lup_ok=(Pup >= Adist), Lin_ok=(Pin >= D),
        ))
        if dump:
            print(f"  u={u} |S|={len(Slist)} nSigma={nSigma} Adist={Adist} D={D} "
                  f"sum={nSigma+Adist+D} | Pmix={Pmix} Pup={Pup} Pin={Pin}")
            cls = defaultdict(list)
            for s in Slist: cls[Sigma[s]].append(s)
            for sig, mem in cls.items():
                print(f"     ray {sorted(sig)}: members {sorted(mem)} "
                      f"apex {[sorted(A[s]) for s in sorted(mem)]}")
            print(f"     D-lines (avoid u): {sorted(sorted(L) for L in Dlines)}")
    return rows


if __name__ == "__main__":
    if len(sys.argv) > 1 and not sys.argv[1].isdigit():
        for g6 in sys.argv[1:]:
            print(f"=== {g6} ===")
            analyze(g6, dump=True)
    else:
        for n in (int(x) for x in (sys.argv[1:] or [8])):
            proc = subprocess.run(
                ["geng", "-c", "-d2", "-q", str(n)],
                capture_output=True,
                text=True,
                check=True,
            )
            agg = dict(n=n, nb=0, Lmix_fail=0, Lup_fail=0, Lin_fail=0,
                       tight=0, tight_ex=[])
            for line in proc.stdout.splitlines():
                g6 = line.strip()
                if not g6: continue
                n2, edges = core.graph6_to_edges(g6)
                if core.has_pendant_edge(n2, edges): continue
                dist = core.all_pairs_distances(n2, edges)
                if max(dist[i][j] for i in range(n2) for j in range(n2)) < 4: continue
                g = nx.Graph(); g.add_nodes_from(range(n2)); g.add_edges_from(edges)
                if nx.is_biconnected(g): continue
                agg["nb"] += 1
                for r in analyze(g6):
                    if not r["Lmix_ok"]: agg["Lmix_fail"] += 1
                    if not r["Lup_ok"]: agg["Lup_fail"] += 1
                    if not r["Lin_ok"]: agg["Lin_fail"] += 1
                    if r["margin"] == 0:
                        agg["tight"] += 1
                        if len(agg["tight_ex"]) < 12: agg["tight_ex"].append((g6, r["u"], r["nS"], r["nSigma"], r["Adist"], r["D"]))
            print(json.dumps(agg))
