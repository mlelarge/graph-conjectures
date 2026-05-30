#!/usr/bin/env python3
"""
Structural probe for the k=2 min-(s,t)-dicut induction (Conj 9.2, arXiv:2304.04690).

KEY CORRECTION over the first draft: a STRONG digraph has NO global directed cut.
The paper's seam is a minimum (s,t)-dicut F (the lambda-witness): an arc set of size
lambda=2 whose removal destroys all s->t dipaths. Equivalently there is a vertex
partition V=(S,T) with s in S, t in T, EVERY arc from S to T is in F (|F|=2 here),
but arcs from T to S MAY exist (so D is not globally a dicut).

We import validated primitives from enumerate_2extremal_v0_recon.py.

For each 2-extremal D and each ordered pair (s,t) with min-(s,t)-dicut of size 2:
  - enumerate the min-cut vertex partitions (S,T) [closest-to-s and closest-to-t reachability]
  - record the 2 forward arcs F = {(a1,b1),(a2,b2)}, a_i in S, b_i in T
  - classify F: shared tail / shared head / disjoint endpoints
  - test CONTRACTION of T to a single vertex t* (and of S to s*): is the quotient
    still 2-extremal? does it stay strong/2-conn/Eulerian/lambda=2/chi=3?
  - test whether some optimal 3-dicolouring is constant on one side of the cut
    (this is what the paper's induction needs and what fails at k=2).
"""
import sys, os, itertools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from collections import deque
from enumerate_2extremal_v0_recon import (
    out_adj, in_adj, is_strong, is_2connected, is_eulerian_deg,
    lambda_D, chi_vec, can_dicolor_k, has_directed_cycle_in_subset,
    is_2extremal, sym_cycle, L_n, canonical, directed_wheel, maxflow_unit,
)

def min_st_cut_partition(arcs, n, s, t):
    """Return (value, S_set) where S = vertices reachable from s in the residual
    graph after a max-flow (the source side of the min cut). Forward cut arcs are
    arcs from S to V\\S in the ORIGINAL digraph."""
    cap = {}
    adj = [[] for _ in range(n)]
    def add_edge(u,v,c):
        if (u,v) not in cap: cap[(u,v)]=0; adj[u].append(v)
        if (v,u) not in cap: cap[(v,u)]=0; adj[v].append(u)
        cap[(u,v)]+=c
    for (i,j) in arcs: add_edge(i,j,1)
    flow=0
    while True:
        parent={s:None}; q=deque([s]); found=False
        while q:
            u=q.popleft()
            if u==t: found=True; break
            for v in adj[u]:
                if v not in parent and cap[(u,v)]>0:
                    parent[v]=u; q.append(v)
        if not found: break
        v=t
        while parent[v] is not None:
            u=parent[v]; cap[(u,v)]-=1; cap[(v,u)]+=1; v=u
        flow+=1
    # residual-reachable from s = source side
    seen={s}; q=deque([s])
    while q:
        u=q.popleft()
        for v in adj[u]:
            if v not in seen and cap[(u,v)]>0:
                seen.add(v); q.append(v)
    return flow, frozenset(seen)

def contract_side(arcs, n, side, into):
    """Contract all vertices in `side` to a single representative `into` (must be in side).
    Returns (new_arcs, new_n, mapping) with vertices relabeled 0..new_n-1,
    loops dropped, parallel arcs merged (set)."""
    side=set(side)
    # representative gets `into`; map every side vertex to into
    rep=into
    # build a relabel: kept vertices = (V \ side) U {rep}
    kept=[v for v in range(n) if v not in side or v==rep]
    newid={v:i for i,v in enumerate(kept)}
    def m(v): return newid[rep] if (v in side and v!=rep) else newid[v]
    na=set()
    for (a,b) in arcs:
        x,y=m(a),m(b)
        if x!=y: na.add((x,y))
    return frozenset(na), len(kept), m

def has_optimal_coloring_constant_on(arcs, n, side, k=3):
    """Is there a proper k-dicolouring whose restriction to `side` uses a single colour?"""
    oadj=out_adj(arcs,n); side=set(side)
    assign=[-1]*n; classes=[[] for _ in range(k)]
    def ok(v,c):
        sub=set(classes[c]); sub.add(v)
        return not has_directed_cycle_in_subset(oadj,sub)
    res=[False]
    def bt(v):
        if res[0]: return
        if v==n:
            cols={assign[u] for u in side}
            if len(cols)==1: res[0]=True
            return
        for c in range(k):
            if ok(v,c):
                classes[c].append(v); assign[v]=c
                bt(v+1)
                classes[c].pop(); assign[v]=-1
    bt(0)
    return res[0]

def analyze_D(arcs, n):
    seams=[]  # (s,t,S,fwd,kind)
    seen_partitions=set()
    for s in range(n):
        for t in range(n):
            if s==t: continue
            val,S=min_st_cut_partition(arcs,n,s,t)
            if val!=2: continue
            T=frozenset(range(n))-S
            key=(S,)
            # record per distinct (S) partition
            fwd=[(a,b) for (a,b) in arcs if a in S and b in T]
            if len(fwd)!=2:
                # min cut from residual side should give exactly val forward arcs
                continue
            pkey=(S,tuple(sorted(fwd)))
            if pkey in seen_partitions: continue
            seen_partitions.add(pkey)
            (u1,w1),(u2,w2)=fwd
            if len({u1,u2})==1: kind='shared_tail'
            elif len({w1,w2})==1: kind='shared_head'
            else: kind='disjoint'
            # contraction tests: contract T into t-side rep, and S into s-side rep
            cs=cqs=None
            # contract S
            Sc,nc,_=contract_side(arcs,n,S,min(S))
            s_ext = is_2extremal(Sc,nc) if nc>=3 else False
            s_strong = is_strong(Sc,nc); s_eul=is_eulerian_deg(Sc,nc,2)
            s_lam = lambda_D(Sc,nc) if nc>=2 else 0
            s_chi = chi_vec(Sc,nc) if nc>=1 else 0
            # contract T
            Tc,nt,_=contract_side(arcs,n,T,min(T))
            t_ext = is_2extremal(Tc,nt) if nt>=3 else False
            t_lam = lambda_D(Tc,nt) if nt>=2 else 0
            t_chi = chi_vec(Tc,nt) if nt>=1 else 0
            const_S = has_optimal_coloring_constant_on(arcs,n,S,3)
            const_T = has_optimal_coloring_constant_on(arcs,n,T,3)
            seams.append(dict(s=s,t=t,S=sorted(S),fwd=fwd,kind=kind,
                              sizeS=len(S),sizeT=len(T),
                              contractS=(nc,s_ext,s_lam,s_chi),
                              contractT=(nt,t_ext,t_lam,t_chi),
                              const_S=const_S,const_T=const_T))
    return seams

def main():
    maxn=int(sys.argv[1]) if len(sys.argv)>1 else 5
    for n in range(3,maxn+1):
        Ln=L_n(n)
        print(f"\n=== n={n}: |L_n|={len(Ln)} ===")
        for idx,arcs in enumerate(Ln):
            seams=analyze_D(arcs,n)
            kinds={}
            for sm in seams: kinds[sm['kind']]=kinds.get(sm['kind'],0)+1
            print(f" D{idx}: #distinct-size2-seams={len(seams)} kinds={kinds}")
            for sm in seams[:8]:
                print(f"    (s={sm['s']},t={sm['t']}) S={sm['S']}({sm['sizeS']}|{sm['sizeT']}) "
                      f"fwd={sm['fwd']} [{sm['kind']}] "
                      f"contrS->{sm['contractS']} contrT->{sm['contractT']} "
                      f"constS={sm['const_S']} constT={sm['const_T']}")

if __name__=="__main__":
    main()
