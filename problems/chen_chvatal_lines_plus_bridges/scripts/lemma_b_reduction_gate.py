"""Independent review of the Lemma B SPQR reduction: ell(G) >= max(D2, BIGTORSO).

For every 2-connected pendant-free diam>=4 graph G (geng -C):
  D2(G)      = #distinct lines from distance-EXACTLY-2 pairs.
  BIGTORSO(G)= max over every 2-cut {a,b} and every component-side Ci of
               ell(torso), torso = Ci ∪ {a,b} + virtual edge ab of weight
               d_rest(a,b)  (rest = (G - Ci); weighted shortest path).
Checks (0 failures expected):
  D2_le_ell      : D2 <= ell
  TORSO_le_ell   : every ell(torso) <= ell  (restriction monotonicity)
  CLAIM_A        : every vertex has >=2 vertices at distance exactly 2
  COMPLEMENT     : max(D2, BIGTORSO) >= n          <-- the load-bearing claim
Counts: D2<n graphs, BIGTORSO<n graphs, fail-both graphs.
"""
import sys, itertools, subprocess
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
import networkx as nx


def wells(verts, base_edges, virt):
    h = nx.Graph(); h.add_nodes_from(verts)
    for x, y in base_edges:
        h.add_edge(x, y, weight=1)
    if virt is not None:
        a, b, w = virt
        if not h.has_edge(a, b):
            h.add_edge(a, b, weight=w)
    W = dict(nx.all_pairs_dijkstra_path_length(h))
    vs = list(verts); lines = set()
    for a, b in itertools.combinations(vs, 2):
        L = {a, b}; dab = W[a][b]
        for x in vs:
            if x == a or x == b: continue
            dax, dbx = W[a][x], W[b][x]
            if dax + dbx == dab or dab + dbx == dax or dax + dab == dbx:
                L.add(x)
        lines.add(frozenset(L))
    return len(lines)


def wdist_ab(verts, edges, a, b):
    vs = sorted(verts); idx = {v: i for i, v in enumerate(vs)}
    W = core.all_pairs_distances(len(vs), [(idx[x], idx[y]) for x, y in edges])
    return W[idx[a]][idx[b]]


def analyze(g6, n, edges):
    g = nx.Graph(); g.add_nodes_from(range(n)); g.add_edges_from(edges)
    if not nx.is_biconnected(g): return None
    if any(d == 1 for _, d in g.degree()): return None
    D = core.all_pairs_distances(n, edges)
    diam = max(D[i][j] for i in range(n) for j in range(n))
    if diam < 4: return None
    glines = {core.line_of_pair(D, n, a, b) for a, b in itertools.combinations(range(n), 2)}
    ell = len(glines)
    D2 = len({core.line_of_pair(D, n, a, b) for a, b in itertools.combinations(range(n), 2) if D[a][b] == 2})
    # CLAIM A
    claimA = all(sum(1 for y in range(n) if D[x][y] == 2) >= 2 for x in range(n))
    # BIGTORSO over all 2-cuts and component-sides
    bigtorso = 0; torso_le_ell = True
    for a, b in itertools.combinations(range(n), 2):
        h = g.copy(); h.remove_nodes_from([a, b])
        if h.number_of_nodes() == 0 or nx.is_connected(h): continue
        comps = [set(c) for c in nx.connected_components(h)]
        for Ci in comps:
            side = Ci | {a, b}
            rest = (set(range(n)) - Ci)  # includes a,b
            rest_edges = [(x, y) for x, y in g.subgraph(rest).edges()]
            w = wdist_ab(rest, rest_edges, a, b)
            side_edges = [(x, y) for x, y in g.subgraph(side).edges()]
            et = wells(sorted(side), side_edges, (a, b, w))
            if et > ell: torso_le_ell = False
            bigtorso = max(bigtorso, et)
    return dict(g6=g6, n=n, ell=ell, D2=D2, bigtorso=bigtorso, diam=diam,
                D2_le_ell=(D2 <= ell), torso_le_ell=torso_le_ell, claimA=claimA,
                complement=(max(D2, bigtorso) >= n),
                D2_lt_n=(D2 < n), bigtorso_lt_n=(bigtorso < n))


def run(order):
    proc = subprocess.run(
        ["geng", "-C", "-q", str(order)],
        capture_output=True,
        text=True,
        check=True,
    )
    F = dict(order=order, graphs=0, D2le_fail=0, torsole_fail=0, claimA_fail=0,
             complement_fail=0, D2_lt_n=0, bigtorso_lt_n=0, fail_both=0,
             cefail=None)
    for line in proc.stdout.splitlines():
        g6 = line.strip()
        if not g6: continue
        n, edges = core.graph6_to_edges(g6)
        r = analyze(g6, n, edges)
        if r is None: continue
        F["graphs"] += 1
        if not r["D2_le_ell"]: F["D2le_fail"] += 1
        if not r["torso_le_ell"]: F["torsole_fail"] += 1
        if not r["claimA"]: F["claimA_fail"] += 1
        if not r["complement"]:
            F["complement_fail"] += 1
            if F["cefail"] is None: F["cefail"] = (g6, r["ell"], r["D2"], r["bigtorso"], n)
        if r["D2_lt_n"]: F["D2_lt_n"] += 1
        if r["bigtorso_lt_n"]: F["bigtorso_lt_n"] += 1
        if r["D2_lt_n"] and r["bigtorso_lt_n"]: F["fail_both"] += 1
    return F


if __name__ == "__main__":
    import json
    if sys.argv[1:] and not sys.argv[1].isdigit():
        for g6 in sys.argv[1:]:
            n, e = core.graph6_to_edges(g6)
            print(json.dumps(analyze(g6, n, e)))
    else:
        for n in (int(x) for x in (sys.argv[1:] or [8, 9])):
            print(json.dumps(run(n)))
