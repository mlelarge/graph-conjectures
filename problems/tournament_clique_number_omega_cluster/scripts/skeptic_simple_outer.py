import sys, os, time
sys.path.insert(0, os.path.dirname(__file__))
import core
from search_4critical_circulant import omega_vec_ge_K_via_sat

C3_n = 3; C3_arcs = [(0, 1), (1, 2), (2, 0)]
def circ(p, g): return [(i, (i + d) % p) for i in range(p) for d in g]
AC7_n = 7; AC7_arcs = circ(7, [1, 2, 4])

def beats(n, arcs):
    b = [[False] * n for _ in range(n)]
    for u, v in arcs: b[u][v] = True
    return b

def lex(on, oa, inn, ia):
    bo = beats(on, oa); bi = beats(inn, ia)
    N = on * inn; arcs = []
    for o1 in range(on):
        for a1 in range(inn):
            u = o1 * inn + a1
            for o2 in range(on):
                for a2 in range(inn):
                    v = o2 * inn + a2
                    if u == v: continue
                    if o1 == o2:
                        if bi[a1][a2]: arcs.append((u, v))
                    else:
                        if bo[o1][o2]: arcs.append((u, v))
    return N, arcs

N1, A1 = lex(AC7_n, AC7_arcs, C3_n, C3_arcs)
print("AC7[C3] order", N1, "is_tournament", core.is_tournament(N1, A1), flush=True)
N, A = lex(C3_n, C3_arcs, N1, A1)
print("C3[AC7[C3]] order", N, "is_tournament", core.is_tournament(N, A), flush=True)
N0, A0 = lex(C3_n, C3_arcs, AC7_n, AC7_arcs)
print("anchor C3[AC7] order", N0, "is_tournament", core.is_tournament(N0, A0), flush=True)

ge5a, dt5a, _ = omega_vec_ge_K_via_sat(N0, A0, 5)
ge4a, dt4a, _ = omega_vec_ge_K_via_sat(N0, A0, 4)
print("anchor ge5", ge5a, "(%.3fs)" % dt5a, "ge4", ge4a, "(%.3fs)" % dt4a, flush=True)

from pysat.solvers import Cadical153
from pysat.formula import CNF
import itertools
# Rebuild the K=6 CNF here with an EXPLICIT lit map so we can reconstruct the order from the model,
# then certify the upper bound SAT-FREE via core.omega_of_order.
beats = [[False]*N for _ in range(N)]
for u,v in A: beats[u][v]=True
idx={}; nv=0
def lit(u,v):
    global nv
    if (u,v) in idx: return idx[(u,v)]
    if (v,u) in idx: return -idx[(v,u)]
    nv+=1; idx[(u,v)]=nv; return nv
cnf=CNF()
for u in range(N):
    for v in range(u+1,N): lit(u,v)
for u in range(N):
    for v in range(N):
        if v==u: continue
        for w in range(N):
            if w==u or w==v: continue
            cnf.append([-lit(u,v),-lit(v,w),lit(u,w)])
nclq=0
from search_4critical_circulant import transitive_ksubsets_order
for order in transitive_ksubsets_order(N, beats, 6):
    cnf.append([lit(order[i],order[i+1]) for i in range(5)]); nclq+=1
t0=time.time()
with Cadical153(bootstrap_with=cnf.clauses) as m:
    sat6=m.solve(); model=m.get_model() if sat6 else None
dt6=time.time()-t0
print("DECISION ge6(>=6?):", (not sat6), "sat=", sat6, "(%.2fs, %d clq)"%(dt6,nclq), flush=True)
if sat6:
    truth={abs(l): (l>0) for l in model}
    # u<v iff lit(u,v) true
    def less(u,v):
        l=lit(u,v); var=abs(l)
        val=truth[var]
        return val if l>0 else (not val)
    order=sorted(range(N), key=lambda u: sum(1 for v in range(N) if v!=u and less(v,u)))
    w=core.omega_of_order(N,A,order)
    print("SAT-FREE constructive upper bound from model order:", w, flush=True)
