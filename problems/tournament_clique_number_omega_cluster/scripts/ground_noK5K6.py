import sys, time
sys.path.insert(0,'scripts')
from lexlib import lex_substitute, AC, is_tournament, C3
from pysat.formula import CNF
from pysat.solvers import Cadical153

AC7 = AC(7, {1,2,4})
T = lex_substitute(C3, lex_substitute(AC7, C3))
n, arcs = T
print("order", n, "tournament", is_tournament(n,arcs)); sys.stdout.flush()

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

def ge_K(K):
    chains=enum_sets(K)
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
        cnf.append([lit(ch[i],ch[i+1]) for i in range(K-1)])
    t=time.time()
    s=Cadical153(bootstrap_with=cnf.clauses)
    sat=s.solve()
    s.delete()
    return (not sat), len(chains), len(cnf.clauses), time.time()-t

for K in (5,6):
    geK,ntr,ncl,dt=ge_K(K)
    print(f"K={K}: omega_vec>={K} = {geK}   (ntrans={ntr}, clauses={ncl}, solve {dt:.2f}s)")
    sys.stdout.flush()
