"""H4/H5 falsification gate: directed local search seeded ONLY from the
oracle-verified tightest diam>=4 pendant-free near-misses (deficit -1).

Seeds (oracle-extracted this round):
  n=8 : G?r@do            (ell=9,  br=0, diam=4, deficit -1)  [unique]
  n=10: I?`bCaWTO         (ell=11, br=0, diam=4, deficit -1)
  n=10: ICOeeOsk_         (ell=11, br=0, diam=4, deficit -1)

Line-suppressing moves, each kept iff result is connected, pendant-free,
diam>=4:
  (i)  all single- and double- non-edge additions
  (ii) one-vertex C4 splice (new deg-2 vertex adjacent to 2 vertices of an
       induced 4-cycle)
  (iii) C4 antipodal merge (identify the two non-adjacent vertices of an
        induced 4-cycle)

KILL H5 iff any kept candidate has deficit n-ell-br >= 0 (is_bad or margin
breach below the +1 floor).
"""
import sys, itertools
sys.path.insert(0, 'scripts')
import core
import networkx as nx


def classify(G):
    G = nx.convert_node_labels_to_integers(G)
    n = G.number_of_nodes()
    edges = list(G.edges())
    if not core.is_connected(n, edges):
        return None
    if any(d == 1 for _, d in G.degree()):
        return None
    dist = core.all_pairs_distances(n, edges)
    diam = max(dist[i][j] for i in range(n) for j in range(n))
    if diam < 4:
        return None
    inv = core.invariants(n, edges)
    return n - inv['ell'] - inv['br'], inv, diam


def induced_c4s(G):
    out = set()
    for quad in itertools.combinations(G.nodes(), 4):
        sub = G.subgraph(quad)
        if sub.number_of_edges() == 4 and all(d == 2 for _, d in sub.degree()):
            out.add(quad)
    return out


def candidates(g6):
    G0 = nx.convert_node_labels_to_integers(nx.from_graph6_bytes(g6.encode()))
    nodes = list(G0.nodes())
    nonedges = [(u, v) for u, v in itertools.combinations(nodes, 2)
                if not G0.has_edge(u, v)]
    out = []
    for e in nonedges:
        H = G0.copy(); H.add_edge(*e); out.append(('add1', H))
    for e1, e2 in itertools.combinations(nonedges, 2):
        H = G0.copy(); H.add_edge(*e1); H.add_edge(*e2); out.append(('add2', H))
    c4s = induced_c4s(G0)
    new = max(nodes) + 1
    for quad in c4s:
        for a, b in itertools.combinations(quad, 2):
            H = G0.copy(); H.add_node(new); H.add_edge(new, a); H.add_edge(new, b)
            out.append(('splice', H))
    for quad in c4s:
        sub = G0.subgraph(quad)
        for a, b in itertools.combinations(quad, 2):
            if not sub.has_edge(a, b):  # antipodal
                H = nx.contracted_nodes(G0.copy(), a, b, self_loops=False)
                out.append(('merge', H))
    return out


def run():
    seeds = ['G?r@do', 'I?`bCaWTO', 'ICOeeOsk_']
    grand_kept = 0
    grand_breach = 0
    overall_min = None
    for g6 in seeds:
        cands = candidates(g6)
        kept = 0
        breaches = []
        mn = None
        for tag, H in cands:
            res = classify(H)
            if res is None:
                continue
            kept += 1
            df, inv, diam = res
            if mn is None or df < mn:
                mn = df
            if df >= 0:
                breaches.append((tag, df, inv['is_bad'], inv['ell'], inv['br'], inv['n']))
        print(f"seed {g6}: candidates={len(cands)} kept(diam>=4,pf,conn)={kept} "
              f"deficit>=0 breaches={len(breaches)} min_deficit={mn}")
        for b in breaches:
            print("   BREACH", b)
        grand_kept += kept
        grand_breach += len(breaches)
        if mn is not None and (overall_min is None or mn < overall_min):
            overall_min = mn
    print(f"TOTAL kept={grand_kept} TOTAL breaches(KILL-H5)={grand_breach} "
          f"overall_min_deficit={overall_min}")
    return grand_breach


if __name__ == '__main__':
    sys.exit(0 if run() == 0 else 1)
