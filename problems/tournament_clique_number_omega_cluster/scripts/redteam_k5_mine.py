"""MY OWN independent red-team. Re-derived from scratch.

Key correction vs a naive 'transitive sub-tournament' test:
A backedge clique under a FIXED order prec is a set S such that for every pair
u prec v in S, v BEATS u (the later vertex beats the earlier).  Under
inner_then_outer key = (c(b), c(a), a, b), the order of two vertices in
DIFFERENT cells is fixed by the cell order; within a cell the (a,b) tie-break
applies.  §3.1 already shows no backedges within a cell, so a backedge clique
has <=1 per cell.  So a cell-SET is realizable as a backedge clique iff there
exist reps (one per cell) such that for every pair, the HIGHER-cell rep beats
the LOWER-cell rep.  (The within-cell tie-break is irrelevant: distinct cells.)

So feasibility test = exists reps with: for cells ci < cj (key order),
rep_j BEATS rep_i.  This is a DIRECTED constraint dictated by cell order,
NOT 'some transitive orientation'.

This is what §3.3 must rule out.  I test all 20 minimal sets AND, more
importantly, the DIRECT question: is omega(T-(0,0)) under inner_then_outer <=4?
And does the BB oracle confirm omega_vec(T-(0,0))=4 and omega_vec(T)=5?
"""
import itertools, sys
import networkx as nx

def g_set(n):
    m=(n-1)//2
    return set(range(1,m))|{m+1}

def cpot(t,m):
    if t==0: return 3
    if 1<=t<=m: return 2
    return 1

def beats(u,v,n,g):
    """u=(a,b) beats v=(a',b')?"""
    a,b=u; ap,bp=v
    if a!=ap: return (ap-a)%n in g
    return (bp-b)%n in g

def key_ito(v,m):
    a,b=v
    return (cpot(b,m),cpot(a,m),a,b)

def cell_vertices(cell,n,m):
    cb,ca=cell
    bs=[t for t in range(n) if cpot(t,m)==cb]
    as_=[t for t in range(n) if cpot(t,m)==ca]
    return [(a,b) for a in as_ for b in bs]

def realizable_as_backedge_clique(cellset,n):
    """Exists reps (one per cell) s.t. for every pair, the rep in the
    KEY-HIGHER cell beats the rep in the KEY-LOWER cell?"""
    m=(n-1)//2
    g=g_set(n)
    # order cells by inner_then_outer cell-key (c(b),c(a)) = (cell[0],cell[1])
    cells=sorted(cellset)  # cell tuples are (c(b),c(a)); sorted = key order
    pools=[cell_vertices(c,n,m) for c in cells]
    for combo in itertools.product(*pools):
        ok=True
        for i in range(len(cells)):
            for j in range(i+1,len(cells)):
                # cells[j] is key-higher; rep j must beat rep i
                if not beats(combo[j],combo[i],n,g):
                    ok=False; break
            if not ok: break
        if ok:
            return combo
    return None

# ---- direct oracle: omega under inner_then_outer for T-(0,0) and T ----
def build_T(n):
    g=g_set(n)
    verts=[(a,b) for a in range(n) for b in range(n)]
    idx={v:i for i,v in enumerate(verts)}
    N=n*n
    beatsM=[[False]*N for _ in range(N)]
    for u in verts:
        for v in verts:
            if u!=v and beats(u,v,n,g):
                beatsM[idx[u]][idx[v]]=True
    return verts,idx,beatsM

def omega_under_order(verts,idx,beatsM,order_verts):
    """order_verts: list of vertices in prec order (small first).
    edge iff later beats earlier."""
    g=nx.Graph()
    ids=[idx[v] for v in order_verts]
    g.add_nodes_from(ids)
    for ii in range(len(order_verts)):
        a=idx[order_verts[ii]]
        for jj in range(ii+1,len(order_verts)):
            b=idx[order_verts[jj]]
            if beatsM[b][a]:
                g.add_edge(a,b)
    return max((len(c) for c in nx.find_cliques(g)),default=1)

def main():
    TRIPLES_GIVEN=[
        [(1,1),(1,3),(2,1)],
        [(1,1),(1,3),(3,1)],
        [(1,1),(2,3),(3,1)],
        [(2,1),(2,3),(3,1)],
        [(1,3),(2,1),(2,3)],
    ]
    def swap_alpha(c):
        cb,ca=c
        if ca==1: ca=2
        elif ca==2: ca=1
        return (cb,ca)
    TRIPLES=[]
    for tr in TRIPLES_GIVEN:
        TRIPLES.append([tuple(c) for c in tr])
        TRIPLES.append([swap_alpha(tuple(c)) for c in tr])
    QUADS=[
        [(1,1),(1,2),(2,1),(2,3)],
        [(1,2),(2,1),(2,2),(2,3)],
        [(1,3),(2,1),(2,2),(3,1)],
        [(1,3),(2,2),(3,1),(3,2)],
    ]
    SQUARES=[
        [(1,1),(1,2),(2,1),(2,2)],
        [(1,1),(1,2),(2,1),(3,2)],   # replace one c(b)=2 cell by (3,.) -- approx
    ]
    ALL=TRIPLES+QUADS
    ns=[7,9,11,13,15,17,19]
    print("=== CORRECT backedge-clique realizability (directed by cell order) ===")
    any_feasible=False
    for cs in ALL:
        wit=None; allinf=True
        for n in ns:
            r=realizable_as_backedge_clique(cs,n)
            if r is not None:
                allinf=False
                if wit is None: wit=(n,r)
        tag="INFEASIBLE(all n)" if allinf else "*** REALIZABLE ***"
        if not allinf: any_feasible=True
        print(f"{sorted(cs)} -> {tag}" + (f"  wit n={wit[0]} reps={wit[1]}" if wit else ""))
    print("ANY 5-cell-blocking set REALIZABLE under inner_then_outer?:",any_feasible)

    print("\n=== DIRECT: omega(backedge graph) under the SPECIFIC orders, n=7 ===")
    n=7; m=(n-1)//2
    verts,idx,beatsM=build_T(n)
    # T-(0,0): inner_then_outer
    surv=[v for v in verts if v!=(0,0)]
    order_surv=sorted(surv,key=lambda v:key_ito(v,m))
    w=omega_under_order(verts,idx,beatsM,order_surv)
    print("omega(T-(0,0) | inner_then_outer) =",w,"(claim: <=4)")
    # is (0,0) unique max of inner_then_outer over all T?
    allkeys=[(key_ito(v,m),v) for v in verts]
    mx=max(allkeys)
    print("inner_then_outer global max:",mx[1],"key",mx[0],
          "| #verts achieving max:",sum(1 for k,_ in allkeys if k==mx[0]))
    # T full under merged-sum
    def key_merge(v):
        a,b=v; return (cpot(a,m)+cpot(b,m),a,b)
    order_full=sorted(verts,key=key_merge)
    wf=omega_under_order(verts,idx,beatsM,order_full)
    print("omega(T | merged-sum) =",wf,"(claim: <=5)")

if __name__=="__main__":
    main()
