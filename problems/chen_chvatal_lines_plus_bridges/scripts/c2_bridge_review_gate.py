"""REVIEW: independently test the load-bearing BRIDGE claims that the T1/T2
gates do NOT check.

Over every leaf block of every non-2-connected pendant-free diam>=4 graph at the
given orders, compute (matching the gates' exact definitions) nSigma, nSigmaP, nT,
Adist, D', P, Q, deficit, and test:

 (KEY)   P >= nSigmaP*nT + Adist + D'        <-- the T2-docstring "product gives",
                                                  the bridge for BOTH T1 and T2.
 (T1lo)  nSigmaP*nT + Adist + D' >= |S|      <-- does the route's lower bound reach |S|?
 (T2mid) P - |S| >= nSigmaP*nT - nSigma      <-- what "T1 + product" is claimed to give.
 (4')    nSigma + Adist + D' >= |S|          <-- the block-local target (re-check).
 (star)  Q + nSigmaP*nT - nSigma >= deficit  <-- (*), deficit branch (re-check).

Reports min margins + first counterexamples for each.
"""
import sys, os, subprocess, itertools
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


def induced(g, verts):
    labels = sorted(verts); idx = {v: i for i, v in enumerate(labels)}
    edges = [(idx[a], idx[b]) for a, b in g.subgraph(labels).edges()]
    return labels, idx, core.all_pairs_distances(len(labels), edges)


def block_quantities(n, g, distG, glines, B, u):
    S = set(B) - {u}; Rv = set(range(n)) - S
    full_s = frozenset(S)
    # ---- block-internal (induced metric) : Sigma, Adist, D'  (match c2_t1) ----
    labels, idx, dB = induced(g, B)
    ui = idx[u]
    sigma = {}; apex = {}
    for s in S:
        si = idx[s]; dus = dB[ui][si]; ray = set()
        for x in S:
            xi = idx[x]
            if dB[ui][xi] + dB[xi][si] == dus or dus + dB[si][xi] == dB[ui][xi]:
                ray.add(x)
        sigma[s] = frozenset(ray)
        ln = core.line_of_pair(dB, len(labels), ui, si)
        apex[s] = frozenset(labels[i] for i in ln) - {u}
    dprime = set()
    for a, b in itertools.combinations(labels, 2):
        ln = core.line_of_pair(dB, len(labels), idx[a], idx[b])
        lifted = frozenset(labels[i] for i in ln)
        if u not in lifted and lifted != full_s:
            dprime.add(lifted)
    nSigma = len(set(sigma.values()))
    nSigmaP = len({x for x in sigma.values() if x != full_s})
    Adist = len({a for a in apex.values() if a != full_s})
    Dp = len(dprime)
    # ---- R-side : nT  (match c2_t2, full graph) ----
    s0 = next(iter(S)); r_other = [p for p in Rv if p != u]
    nT = len({frozenset(core.line_of_pair(distG, n, s0, p) & Rv) for p in r_other})
    # ---- P, Z, Q, deficit ----
    Z = sum(1 for L in glines if (L & S) in (set(), full_s))
    P = len(glines) - Z
    _, _, dR = induced(g, Rv)
    ellR = len({core.line_of_pair(dR, len(Rv), a, b) for a, b in itertools.combinations(range(len(Rv)), 2)})
    Q = Z - ellR
    deficit = max(0, len(Rv) - ellR)
    return dict(nS=len(S), nSigma=nSigma, nSigmaP=nSigmaP, nT=nT, Adist=Adist,
                Dp=Dp, P=P, Q=Q, deficit=deficit)


def run(order):
    proc = subprocess.run(
        ["geng", "-c", "-d2", "-q", str(order)],
        capture_output=True,
        text=True,
        check=True,
    )
    stats = {k: [10**9, 0, None] for k in ("KEY", "T1lo", "T2mid", "p4", "star")}  # [min, fails, ce]
    nblocks = ndef = 0
    for line in proc.stdout.splitlines():
        g6 = line.strip()
        if not g6: continue
        n, edges = core.graph6_to_edges(g6)
        if core.has_pendant_edge(n, edges): continue
        distG = core.all_pairs_distances(n, edges)
        if max(distG[i][j] for i in range(n) for j in range(n)) < 4: continue
        g = nx.Graph(); g.add_nodes_from(range(n)); g.add_edges_from(edges)
        if nx.is_biconnected(g): continue
        glines = {core.line_of_pair(distG, n, a, b) for a, b in itertools.combinations(range(n), 2)}
        for (B, u) in leaf_blocks(g):
            q = block_quantities(n, g, distG, glines, B, u)
            nblocks += 1
            checks = {
                "KEY":   q["P"] - (q["nSigmaP"] * q["nT"] + q["Adist"] + q["Dp"]),
                "T1lo":  (q["nSigmaP"] * q["nT"] + q["Adist"] + q["Dp"]) - q["nS"],
                "p4":    (q["nSigma"] + q["Adist"] + q["Dp"]) - q["nS"],
            }
            if q["deficit"] > 0:
                ndef += 1
                checks["T2mid"] = (q["P"] - q["nS"]) - (q["nSigmaP"] * q["nT"] - q["nSigma"])
                checks["star"] = (q["Q"] + q["nSigmaP"] * q["nT"] - q["nSigma"]) - q["deficit"]
            for k, v in checks.items():
                if v < stats[k][0]:
                    stats[k][0] = v
                if v < 0:
                    stats[k][1] += 1
                    if stats[k][2] is None:
                        stats[k][2] = {"g6": g6, "u": u, **q, "margin": v}
    out = {"n": order, "blocks": nblocks, "deficient": ndef}
    for k, (mn, fl, ce) in stats.items():
        out[k] = {"min_margin": (None if mn == 10**9 else mn), "failures": fl, "first_ce": ce}
    return out


if __name__ == "__main__":
    import json
    for n in (int(x) for x in (sys.argv[1:] or [8, 9])):
        print(json.dumps(run(n)))
