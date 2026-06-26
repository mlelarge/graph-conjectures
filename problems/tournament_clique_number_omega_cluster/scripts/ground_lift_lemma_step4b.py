"""D31 lift-lemma STEP 4b: strike on C3[X5] (order 147) with CONSTRUCTIVE
dicolorings (no big-n SAT).

X5 = AC_7[AC_7]. Cells C_{a,b} = O_a x I_b where O_*, I_* are the acyclic
classes {0,1,2},{3,4,5},{6} of AC_7 (each transitive). Each cell is acyclic.
A union of cells is acyclic iff no directed triangle spans <=3 of its cells;
search (exact backtracking over the 9 cells) for the minimum m such that a
cell-respecting m-dicoloring of X5 exists; same coloring restricted gives
dicolorings of X5 - v. Then build the preprint template orders on
T6 = C3[X5] and compute exact backedge cliques.
Also: dic-vertex-criticality of C3[AC_7] at 5 (deletion dic<=4? small SAT).
"""
import sys, os, json, time, itertools
sys.path.insert(0, os.path.dirname(__file__))
from lexlib import AC, lex_substitute, is_tournament
from constructions import directed_C3
from ground_lift_lemma_step3 import dicolor_model, sub, beats
import networkx as nx

A7 = AC(7,[1,2,4])
X5 = lex_substitute(A7, A7)   # order 49: vertex (o,i) -> 7*o+i
nI, aI = X5
bI = beats(nI, aI)

K = [[0,1,2],[3,4,5],[6]]     # acyclic classes of AC_7

def has_triangle(S):
    for u,v,w in itertools.combinations(S,3):
        if (bI[u][v] and bI[v][w] and bI[w][u]) or (bI[v][u] and bI[w][v] and bI[u][w]):
            return True
    return False

def cell(a,b):
    return [7*o+i for o in K[a] for i in K[b]]

cells = {(a,b): cell(a,b) for a in range(3) for b in range(3)}
# sanity: each cell acyclic
for c,S in cells.items():
    assert not has_triangle(S), c

cl = list(cells)
# bad pairs / triples of cells (union has a directed triangle)
badpair = set()
for x,y in itertools.combinations(cl,2):
    if has_triangle(cells[x]+cells[y]): badpair.add(frozenset((x,y)))
badtri = set()
for x,y,z in itertools.combinations(cl,3):
    if frozenset((x,y)) in badpair or frozenset((x,z)) in badpair or frozenset((y,z)) in badpair:
        continue
    if has_triangle(cells[x]+cells[y]+cells[z]): badtri.add(frozenset((x,y,z)))
print(f"bad pairs: {len(badpair)}, bad triples (beyond pairs): {len(badtri)}", flush=True)

def cell_coloring(m):
    """exact backtracking: f: 9 cells -> m colors, no monochromatic bad pair/triple."""
    f = {}
    def ok(c, col):
        for d in f:
            if f[d]==col and frozenset((c,d)) in badpair: return False
        for d,e in itertools.combinations([x for x in f if f[x]==col],2):
            if frozenset((c,d,e)) in badtri: return False
        return True
    def bt(i):
        if i==len(cl): return True
        c = cl[i]
        used = set(f.values())
        for col in range(min(m, len(used)+1)):
            if ok(c,col):
                f[c]=col
                if bt(i+1): return True
                del f[c]
        return False
    return dict(f) if bt(0) else None

best = None
for m in range(4, 10):
    f = cell_coloring(m)
    if f:
        best = (m, f); break
m, f = best
print(f"minimum cell-respecting dicoloring of X5: m = {m}", flush=True)
col49 = [None]*49
for c,S in cells.items():
    for v in S: col49[v] = f[c]
# verify
classes = [[v for v in range(49) if col49[v]==i] for i in range(m)]
for S in classes: assert not has_triangle(S)
print("verified: valid %d-dicoloring of X5 (constructive upper bound dic(X5)<=%d)"%(m,m), flush=True)

# ---- build T6 and template orders ----
T6 = lex_substitute(directed_C3(), X5)
n, arcs = T6
bT = beats(n, arcs)
print(f"T6 order {n}", flush=True)

def topo_order(cls_set):
    return sorted(cls_set, key=lambda v: -sum(1 for u in cls_set if u != v and bT[v][u]))

def backedge_clique(nn, aa, order):
    bb = beats(nn, aa)
    pos = {v:i for i,v in enumerate(order)}
    G = nx.Graph(); G.add_nodes_from(range(nn))
    for u in range(nn):
        for v in range(u+1, nn):
            if (pos[u] < pos[v] and bb[v][u]) or (pos[v] < pos[u] and bb[u][v]):
                G.add_edge(u,v)
    clq, w = nx.max_weight_clique(G, weight=None)
    return w

out = dict(m_cell=m, badpairs=len(badpair), badtris=len(badtri))

# (1) FULL layered order: A1<B1<C1<...<Am<Bm<Cm
orderF = []
for i in range(m):
    for off in (0,49,98):
        orderF += topo_order([off+v for v in classes[i]])
assert sorted(orderF)==list(range(n))
t0=time.time(); wF = backedge_clique(n, arcs, orderF)
print(f"FULL layered order clique = {wF} ({time.time()-t0:.1f}s)", flush=True)
out['full_layered_clique'] = wF

# (2) deletion template: x=0 in A; b=49, c=98; m-coloring of each block minus
# its first vertex (use col49 restricted, still valid)
x=0
classesD = [[v for v in range(1,49) if col49[v]==i] for i in range(m)]
order = [49, 98]
for i in range(m):
    for off in (0,49,98):
        order += topo_order([off+v for v in classesD[i]])
surv=[v for v in range(n) if v!=x]
assert sorted(order)==sorted(surv)
idxm={v:i for i,v in enumerate(surv)}
nsub, asub = 146, [(idxm[u],idxm[v]) for (u,v) in arcs if u!=x and v!=x]
t0=time.time(); wD = backedge_clique(nsub, asub, [idxm[v] for v in order])
print(f"deletion template clique = {wD} ({time.time()-t0:.1f}s)", flush=True)
out['deletion_template_clique'] = wD

# (3) merged-sum-style order on T6 = (C3[AC_7])[AC_7] (associativity) skipped:
# G43 showed merged-sum fails for ov=4 outer. Instead: best of a few random
# per-class shuffles of layer order (cheap variants)
import random
rng = random.Random(7)
bestv = wF
for trial in range(5):
    perm = list(range(m)); rng.shuffle(perm)
    o2 = []
    for i in perm:
        blks = [0,49,98]; rng.shuffle(blks)
        for off in blks:
            o2 += topo_order([off+v for v in classes[i]])
    wv = backedge_clique(n, arcs, o2)
    bestv = min(bestv, wv)
    print(f"variant {trial}: clique {wv}", flush=True)
out['best_variant_clique'] = bestv

# (4) dic-vertex-criticality of C3[AC_7] at 5 (small SAT, n=20)
W = lex_substitute(directed_C3(), A7)
nn, aa = sub(*W, 0)
c4,t4 = dicolor_model(nn, aa, 4)
print(f"C3[AC_7]-v dic<=4: {'SAT' if c4 else 'UNSAT'} ({t4:.1f}s) -> C3[AC_7] 5-dic-vertex-critical: {c4 is not None} (VT)", flush=True)
out['C3[AC_7]_del_dic_le4'] = c4 is not None

json.dump(out, open(os.path.join(os.path.dirname(__file__),'..','data','lift_lemma_step4_strike.json'),'w'), indent=1)
print("saved", flush=True)
