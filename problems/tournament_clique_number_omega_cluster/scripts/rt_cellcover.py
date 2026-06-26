"""Independently verify the COMBINATORIAL backbone of the deletion upper bound (§3.1-§3.3):

(a) §3.1: within a single cell there are NO backedges (under inner_then_outer order),
    for the FULL graph and deletion, all odd n in range.
(b) The realizable cell-sets: directly compute, for the actual tournament under the
    inner_then_outer order, which sets of cells host a simultaneous backedge clique
    (one rep per cell). Then check: NO 5-cell set is realizable, and the maximal
    realizable cell-sets have size <= 4. This bypasses the 20-minimal-set casework and
    the 'mechanism-matching' hand-waving entirely -- it directly tests the conclusion
    'no 5 cells realizable' for the real graph.
"""
import sys, itertools
def build_T(n, delete=None):
    m=(n-1)//2
    g={x%n for x in (set(range(1,m))|{m+1})}
    V=[(a,b) for a in range(n) for b in range(n)]
    if delete is not None: V=[v for v in V if v!=delete]
    def arc(u,v):
        (a,b),(a2,b2)=u,v
        return ((a2-a)%n in g) if a!=a2 else ((b2-b)%n in g)
    return V,arc,m

def c(t,m):
    if t==0: return 3
    if 1<=t<=m: return 2
    return 1

def cell(v,m): return (c(v[1],m), c(v[0],m))  # (c(b),c(a))

def key(v,m): return (c(v[1],m),c(v[0],m),v[0],v[1])

def main():
    for n in [7,9,11,13]:
        V,arc,m=build_T(n,delete=(0,0))
        order=sorted(V,key=lambda v:key(v,m))
        pos={v:i for i,v in enumerate(order)}
        # (a) within-cell no backedge: for u,v same cell, neither (higher beats lower) backedge
        bad_within=0
        from collections import defaultdict
        cells=defaultdict(list)
        for v in V: cells[cell(v,m)].append(v)
        for cl,vs in cells.items():
            for u in vs:
                for w in vs:
                    if u==w: continue
                    # backedge if later-in-order beats earlier
                    e,l=(u,w) if pos[u]<pos[w] else (w,u)
                    if arc(l,e):  # later beats earlier => backedge within cell
                        bad_within+=1
        # (b) which cell-sets realizable: build max backedge clique and collect cells used;
        # also explicitly test all 5-cell and check none realizable by searching a clique
        # whose vertices lie in those 5 cells with distinct cells.
        N=len(order)
        adj=[set() for _ in range(N)]
        for i in range(N):
            for j in range(i+1,N):
                if arc(order[j],order[i]):
                    adj[i].add(j); adj[j].add(i)
        # find ALL maximal cliques' cell-signatures via Bron-Kerbosch, track max size & cell sets
        cellof=[cell(order[i],m) for i in range(N)]
        max_cliquesize=[0]
        realizable5=[False]
        # max clique
        def bk(R,P,X):
            if not P and not X:
                if len(R)>max_cliquesize[0]: max_cliquesize[0]=len(R)
                if len(R)>=5: realizable5[0]=True
                return
            if len(R)+len(P)<5 and len(R)+len(P)<=max_cliquesize[0]:
                # still need max size; don't prune for max, only note
                pass
            u=next(iter(P|X)) if (P or X) else None
            for v in list(P-(adj[u] if u is not None else set())):
                bk(R|{v},P&adj[v],X&adj[v]); P=P-{v}; X=X|{v}
        bk(set(),set(range(N)),set())
        print(f"n={n} DELETION: within-cell backedges={bad_within}  max_backedge_clique={max_cliquesize[0]}  any5={realizable5[0]}")
        sys.stdout.flush()

if __name__=="__main__":
    main()
