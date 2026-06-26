"""D31 lift-lemma STEP 4 strike: C3[X5] with X5 = AC_7[AC_7] (order 147).

Lower bound (preprint Prop 6.2 first-vertex argument, valid for any ordering):
omega_vec(C3[X5]) >= 1 + omega_vec(X5) = 6.

Upper-bound / criticality attempt via the preprint deletion template:
delete x = (A,0); pick b = first vertex of B, c = first vertex of C; take
m-dicolorings of A-x, B-b, C-c (m as small as SAT allows) and order
  b < c < A1 < B1 < C1 < A2 < B2 < C2 < ... < Am < Bm < Cm,
each class in topological (source-first) order. Compute the EXACT backedge
clique of this order on C3[X5]-x (networkx max_weight_clique). If it is 5,
then omega_vec(C3[X5]-x) = 5 and (by vertex-transitivity) C3[X5] is
6-omega_vec-critical with omega_vec = 6 EXACTLY.
Also: layered order on the FULL C3[X5] from dic(X5)-dicolorings of the three
blocks -> an upper bound on omega_vec(C3[X5]).
"""
import sys, os, json, time, itertools
sys.path.insert(0, os.path.dirname(__file__))
from lexlib import AC, lex_substitute, is_tournament
from constructions import directed_C3
from ground_lift_lemma_step3 import dicolor_model, directed_triangles, sub, beats
import networkx as nx

def topo_order(cls_set, b):
    """source-first order of an acyclic class of a tournament (sort by
    within-class outdegree descending)."""
    return sorted(cls_set, key=lambda v: -sum(1 for u in cls_set if u != v and b[v][u]))

def backedge_clique(n, arcs, order):
    b = beats(n, arcs)
    pos = {v:i for i,v in enumerate(order)}
    G = nx.Graph()
    G.add_nodes_from(range(n))
    for u in range(n):
        for v in range(u+1, n):
            if (pos[u] < pos[v] and b[v][u]) or (pos[v] < pos[u] and b[u][v]):
                G.add_edge(u, v)
    clq, w = nx.max_weight_clique(G, weight=None)
    return w, G.number_of_edges()

def min_dicoloring(n, arcs, kstart, kmax=10):
    tris = directed_triangles(n, arcs)
    for k in range(kstart, kmax+1):
        col, t = dicolor_model(n, arcs, k, tris)
        if col is not None:
            return k, col
    return None, None

def main():
    A7 = AC(7,[1,2,4])
    X5 = lex_substitute(A7, A7)          # order 49
    nI, aI = X5
    T6 = lex_substitute(directed_C3(), X5)   # order 147; blocks A=[0,49),B=[49,98),C=[98,147)
    n, arcs = T6
    assert is_tournament(n, arcs)
    print(f"T6 = C3[AC_7[AC_7]] order {n}", flush=True)

    out = {}
    # --- deletion template on T6 - x, x = 0 (in block A) ---
    x = 0; bv = 49; cv = 98
    # m-dicoloring of X5 - 0 (same for A-x; B-b and C-c are also X5 minus first vertex)
    nd, ad = sub(nI, aI, 0)
    m, cold = min_dicoloring(nd, ad, 4)
    print(f"dic(X5 - v) = {m} (first SAT k)", flush=True)
    out['dic_X5_minus_v'] = m
    bT = beats(n, arcs)
    # vertex maps: block A vertices = inner v -> v ; B -> 49+v ; C -> 98+v
    # deleted inner vertex is 0 in each block (b=49+0, c=98+0 are the PICKED b,c,
    # and x=0 deleted). classes from cold over inner indices 1..48 (sub reindexed:
    # inner vertex w>=1 -> index w-1).
    classes = [[] for _ in range(m)]
    for idx in range(nd):
        classes[cold[idx]].append(idx + 1)   # back to inner labels 1..48
    order = [bv, cv]
    for i in range(m):
        for blk, off in (('A',0), ('B',49), ('C',98)):
            cls = [off + w for w in classes[i]]
            order += topo_order(cls, bT)
    surv = [v for v in range(n) if v != x]
    assert sorted(order) == sorted(surv), (len(order), len(surv))
    ns, as_ = n, arcs
    # build subtournament on survivors with order
    keep = surv
    idxm = {v:i for i,v in enumerate(keep)}
    nsub, asub = len(keep), [(idxm[u], idxm[v]) for (u,v) in arcs if u != x and v != x]
    sub_order = [idxm[v] for v in order]
    t0 = time.time()
    w, ne = backedge_clique(nsub, asub, sub_order)
    print(f"deletion template order: backedge clique = {w} (edges {ne}, {time.time()-t0:.1f}s)", flush=True)
    out['deletion_template_clique'] = w

    # --- full-T6 layered order upper bound ---
    M, colf = min_dicoloring(nI, aI, max(4, m), kmax=10)
    print(f"dic(X5) = {M} (first SAT k)", flush=True)
    out['dic_X5'] = M
    classesF = [[] for _ in range(M)]
    for v in range(nI):
        classesF[colf[v]].append(v)
    orderF = []
    for i in range(M):
        for off in (0, 49, 98):
            cls = [off + w for w in classesF[i]]
            orderF += topo_order(cls, bT)
    assert sorted(orderF) == list(range(n))
    t0 = time.time()
    wF, neF = backedge_clique(n, arcs, orderF)
    print(f"full layered order: backedge clique = {wF} (edges {neF}, {time.time()-t0:.1f}s)", flush=True)
    out['full_layered_clique'] = wF
    out['lower_bound_first_vertex'] = 1 + 5
    json.dump(out, open(os.path.join(os.path.dirname(__file__),'..','data','lift_lemma_step4_strike.json'),'w'), indent=1)
    print("saved data/lift_lemma_step4_strike.json", flush=True)

if __name__ == '__main__':
    main()
