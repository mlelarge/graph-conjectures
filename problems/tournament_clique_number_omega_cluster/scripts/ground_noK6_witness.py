import sys, time
sys.path.insert(0,'scripts')
import core
from lexlib import lex_substitute, AC, is_tournament, C3
from pysat.formula import CNF
from pysat.solvers import Cadical153

AC7 = AC(7, {1,2,4})
T = lex_substitute(C3, lex_substitute(AC7, C3))
n, arcs = T
beats = [[False]*n for _ in range(n)]
for (u,v) in arcs: beats[u][v]=True
out=[0]*n
for u in range(n):
    m=0
    for v in range(n):
        if beats[u][v]: m|=(1<<v)
    out[u]=m

def enum_sets(K):
    chains=[]; ap=chains.append
    def rec(chosen,cand):
        if len(chosen)==K: ap(tuple(chosen)); return
        m=cand
        while m:
            v=(m&-m).bit_length()-1; m&=m-1
            rec(chosen+[v], cand&out[v])
    for s in range(n): rec([s], out[s])
    return chains

chains=enum_sets(6)
idx={}; nv=[0]
def lit(u,v):
    if (u,v) in idx: return idx[(u,v)]
    if (v,u) in idx: return -idx[(v,u)]
    nv[0]+=1; idx[(u,v)]=nv[0]; return nv[0]
for u in range(n):
    for v in range(u+1,n): lit(u,v)
cnf=CNF()
for u in range(n):
    for v in range(n):
        if v==u: continue
        for w in range(n):
            if w==u or w==v: continue
            cnf.append([-lit(u,v),-lit(v,w),lit(u,w)])
for ch in chains:
    cnf.append([lit(ch[i],ch[i+1]) for i in range(5)])
t=time.time()
s=Cadical153(bootstrap_with=cnf.clauses)
sat=s.solve()
print("no-K6 SAT (re-run):", sat, "%.2fs"%(time.time()-t)); sys.stdout.flush()
assert sat, "expected SAT"
model=set(s.get_model()); s.delete()
# reconstruct order: u before v iff lit(u,v) true.  Build tournament '<' and topo-sort.
# define less[u][v]: u precedes v
import functools
def precedes(u,v):
    l=lit(u,v)
    return (l in model) if l>0 else ((-l) not in model)
# total order via sort with comparator
verts=list(range(n))
def cmp(a,b):
    if a==b: return 0
    return -1 if precedes(a,b) else 1
order=sorted(verts, key=functools.cmp_to_key(cmp))
w=core.omega_of_order(n,arcs,order)
print("INDEPENDENT CHECK: backedge clique of SAT-witness order =", w)
print("=> omega_vec(C3[AC7[C3]]) <=", w, "(sound, no SAT)")
print("proven lex lower bound = 5 => omega_vec = 5" if w==5 else "anomaly w=%d"%w)
