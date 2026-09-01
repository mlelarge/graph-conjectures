"""Historical/refutation-only review of the former B1 target G3.

G3 is false by the exhaustive n=12 counterexample recorded as G21. B1 itself
remains open and unrefuted; its live form is the genuinely global inequality
collisions <= surplus. This script retains the old diagnostics and includes the
G21 witness by default so the failed localization is visible. It is not a
recommended proof target.

For a graph G (n,edges): G2=distance-2 graph; degG2(v)=#{u:d(v,u)=2};
collisions = |E(G2)| - D2 (D2=#distinct distance-2 lines); surplus=|E(G2)|-n;
E(S)=sum_{v in S}(degG2(v)-2); DE={v: ecc(v)=diam}.

Checks:
  B1        : D2 >= n
  G3        : 2*collisions <= E(DE ∪ N(DE))          [FALSE localization; G21]
  ALPHA     : every v with ecc(v)>=3 has degG2(v)>=3 [Menger; needs 3-conn]
  STAR      : line(a,p)=line(a,q), d(a,p)=d(a,q)=2, p!=q => d(p,q)=4 and a between
  PERPAIR   : for a diameter pair {p,q}, E({p,q}∪N(p)∪N(q)) >= 2k+2
              (k=#centers a with d(a,p)=d(a,q)=2 and line(a,p)=line(a,q))   [needs 3-conn]
The random sample is retained as historical context; absence of sampled
failures is not evidence that G3 holds. Named 2-separable witnesses and the
3-connected G21 witness exercise known failure modes.
"""
import sys, itertools, random
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
import networkx as nx
from collections import defaultdict


def is3conn(g):
    if g.number_of_nodes() < 4 or min(dict(g.degree()).values()) < 3:
        return False
    for a, b in itertools.combinations(list(g.nodes()), 2):
        h = g.copy(); h.remove_nodes_from([a, b])
        if h.number_of_nodes() and not nx.is_connected(h):
            return False
    return True


def analyze(n, edges):
    D = core.all_pairs_distances(n, edges)
    diam = max(D[i][j] for i in range(n) for j in range(n))
    adj = [set() for _ in range(n)]
    for a, b in edges:
        adj[a].add(b); adj[b].add(a)
    degG2 = [sum(1 for u in range(n) if D[v][u] == 2) for v in range(n)]
    ecc = [max(D[v]) for v in range(n)]
    # distance-2 lines
    pairs2 = [(a, b) for a, b in itertools.combinations(range(n), 2) if D[a][b] == 2]
    line = {}
    linecount = defaultdict(int)
    for a, b in pairs2:
        L = core.line_of_pair(D, n, a, b); line[(a, b)] = L; linecount[L] += 1
    P2 = len(pairs2); D2 = len(linecount)
    collisions = P2 - D2
    surplus = P2 - n
    def E(S): return sum(degG2[v] - 2 for v in S)
    DE = {v for v in range(n) if ecc[v] == diam}
    DEN = set(DE)
    for v in DE: DEN |= adj[v]
    g3 = E(DEN) - 2 * collisions  # >=0 means G3 holds
    # ALPHA
    alpha_fail = any(ecc[v] >= 3 and degG2[v] < 3 for v in range(n))
    # STAR: centers sharing a line on a common pair-endpoint a
    star_fail = 0
    # group distance-2 pairs by line, find STAR (share endpoint a)
    line_to_pairs = defaultdict(list)
    for (a, b), L in line.items():
        line_to_pairs[L].append((a, b))
    for L, prs in line_to_pairs.items():
        for (a1, b1), (a2, b2) in itertools.combinations(prs, 2):
            common = {a1, b1} & {a2, b2}
            if len(common) == 1:  # share exactly one endpoint a
                a = next(iter(common)); p = (b1 if a1 == a else a1); q = (b2 if a2 == a else a2)
                if p != q:
                    if not (D[p][q] == 4 and D[p][a] + D[a][q] == 4):
                        star_fail += 1
    # PERPAIR over diameter pairs (diam==4 only, per lemma)
    perpair_fail = 0
    if diam == 4:
        for p, q in itertools.combinations(range(n), 2):
            if D[p][q] != 4: continue
            k = 0
            for a in range(n):
                if D[a][p] == 2 and D[a][q] == 2 and line.get((min(a, p), max(a, p))) == line.get((min(a, q), max(a, q))):
                    k += 1
            S = {p, q} | adj[p] | adj[q]
            if E(S) < 2 * k + 2:
                perpair_fail += 1
    return dict(n=n, diam=diam, D2=D2, n_=n, D2_minus_n=D2 - n, collisions=collisions,
                surplus=surplus, g3_margin=g3, b1_ok=(D2 >= n), g3_ok=(g3 >= 0),
                alpha_fail=alpha_fail, star_fail=star_fail, perpair_fail=perpair_fail)


if __name__ == "__main__":
    print("=== G21 3-connected counterexample (G3 must FAIL; B1 must hold) ===")
    for g6 in ["K?`DDOqREaQh"]:
        n, e = core.graph6_to_edges(g6)
        r = analyze(n, e)
        print("%-13s n=%d diam=%d D2-n=%+d collisions=%d surplus=%d | G3 margin=%d (G3 %s) | B1 %s"
              % (g6, n, r["diam"], r["D2_minus_n"], r["collisions"], r["surplus"], r["g3_margin"],
                 "holds" if r["g3_ok"] else "FAILS", "holds" if r["b1_ok"] else "FAILS"))

    print("=== random 3-connected diam>=4 (historical diagnostics; G3 is known false) ===")
    rng = random.Random(7)
    for order in (11, 12, 13, 14):
        cnt = 0; att = 0
        agg = dict(g3f=0, b1f=0, af=0, sf=0, pf=0, ming3=99, minD2n=99)
        while cnt < 30 and att < 60000:
            att += 1
            g = nx.gnp_random_graph(order, rng.uniform(0.2, 0.45), seed=rng.randrange(1 << 30))
            if not nx.is_connected(g): continue
            e = list(g.edges()); D = core.all_pairs_distances(order, e)
            if max(D[i][j] for i in range(order) for j in range(order)) < 4: continue
            if not is3conn(g): continue
            cnt += 1
            r = analyze(order, e)
            agg["g3f"] += (not r["g3_ok"]); agg["b1f"] += (not r["b1_ok"])
            agg["af"] += r["alpha_fail"]; agg["sf"] += r["star_fail"]; agg["pf"] += r["perpair_fail"]
            agg["ming3"] = min(agg["ming3"], r["g3_margin"]); agg["minD2n"] = min(agg["minD2n"], r["D2_minus_n"])
        print("n=%2d sampled=%d | B1_fail=%d G3_fail=%d ALPHA_fail=%d STAR_fail=%d PERPAIR_fail=%d | min(D2-n)=%d min(G3 margin)=%d"
              % (order, cnt, agg["b1f"], agg["g3f"], agg["af"], agg["sf"], agg["pf"], agg["minD2n"], agg["ming3"]))
    print("\n=== named 2-separable witnesses (historical failure diagnostics) ===")
    for g6 in ["HCQdarQ", "GCXmeW", "G?qa`o"]:
        n, e = core.graph6_to_edges(g6)
        r = analyze(n, e)
        print("%-9s n=%d diam=%d D2-n=%+d collisions=%d surplus=%d | G3 margin=%d (G3 %s) | B1 %s"
              % (g6, n, r["diam"], r["D2_minus_n"], r["collisions"], r["surplus"], r["g3_margin"],
                 "holds" if r["g3_ok"] else "FAILS", "holds" if r["b1_ok"] else "FAILS"))
