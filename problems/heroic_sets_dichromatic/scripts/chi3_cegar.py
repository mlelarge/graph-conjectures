"""CEGAR search for an orientation of a FIXED triangle-free graph with chi_d>=3.

Vars: d_k in {0,1} = direction of edge k (1 => (a,b), 0 => (b,a)).
Loop:
  - SAT-solve current clause DB for an orientation.
  - Build arcs, test 2-dicolourability exactly (oracle).
  - If NOT 2-dicolourable: chi_d>=3 witness, return.
  - Else oracle gives a 2-colouring (A,B) acyclic on both sides. We must defeat
    THIS colouring for any future orientation that keeps both sides acyclic.
    Within-A and within-B the current orientation is acyclic. Block the conjunction
    of (these within-part edge directions) so the solver must flip >=1 internal
    edge of A or B. This is sound (never blocks a real chi_d>=3 orientation: such
    an orientation has a monochromatic cycle for (A,B), hence differs on >=1
    internal edge from the acyclic pattern) and forces progress => terminates.
"""
import sys, json, time, os
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
import core
sys.path.insert(0, os.path.join(_HERE, "..", "..", "..", "engine", "lib"))
from pysat.solvers import Solver

def two_colouring(n, arcs):
    """Return (A,B) acyclic 2-colouring if 2-dicolourable, else None."""
    import digraph_core as dc
    k=2
    def var(v,c): return v*k+c+1
    s=Solver(name='glucose3')
    for v in range(n):
        s.add_clause([var(v,c) for c in range(k)])
        s.add_clause([-var(v,0),-var(v,1)])
    while True:
        if not s.solve():
            s.delete(); return None
        model=set(s.get_model())
        col={v:(0 if var(v,0) in model else 1) for v in range(n)}
        added=False
        for c in range(k):
            verts=[v for v in range(n) if col[v]==c]
            sub=dc._digraph(n,[(u,v) for (u,v) in arcs if u in verts and v in verts])
            cyc=dc._find_directed_cycle(sub.subgraph(verts))
            if cyc is not None:
                s.add_clause([-var(v,c) for v in cyc]); added=True
        if not added:
            s.delete()
            A=[v for v in range(n) if col[v]==0]; B=[v for v in range(n) if col[v]==1]
            return (A,B)

def cegar(name, n, edges, time_budget=300):
    edges=list(edges); m=len(edges)
    eidx={frozenset(e):k for k,e in enumerate(edges)}
    o=Solver(name='glucose3')
    # edge var k -> SAT var k+1
    t0=time.time(); iters=0
    while time.time()-t0 < time_budget:
        if not o.solve():
            o.delete(); return None, iters, 'UNSAT_orientations_exhausted'
        model=set(o.get_model())
        dirs={k:(1 if (k+1) in model else 0) for k in range(m)}
        arcs=[]
        for k,(a,b) in enumerate(edges):
            arcs.append((a,b) if dirs[k]==1 else (b,a))
        iters+=1
        col=two_colouring(n,arcs)
        if col is None:
            o.delete(); return arcs, iters, 'FOUND'
        A,B=col; Aset=set(A); Bset=set(B)
        # internal edges of A and of B with their current direction; block this pattern
        lits=[]
        for k,(a,b) in enumerate(edges):
            same = (a in Aset and b in Aset) or (a in Bset and b in Bset)
            if same:
                # current literal that is TRUE; block conjunction => add negation
                lits.append(-(k+1) if dirs[k]==1 else (k+1))
        if not lits:
            # no internal edges? shouldn't happen for connected; block full assignment
            lits=[-(k+1) if dirs[k]==1 else (k+1) for k in range(m)]
        o.add_clause(lits)
    o.delete(); return None, iters, 'TIMEOUT'

if __name__=='__main__':
    from chi3_search import c5_blowup, grotzsch
    which=sys.argv[1]; budget=int(sys.argv[2]) if len(sys.argv)>2 else 300
    if which=='c5t3': n,e=c5_blowup(3); name='C5blowup_t3'
    elif which=='c5t4': n,e=c5_blowup(4); name='C5blowup_t4'
    elif which=='c5t2': n,e=c5_blowup(2); name='C5blowup_t2'
    elif which=='grotzsch': n,e=grotzsch(); name='Grotzsch'
    print(f'=== CEGAR {name}: n={n} |E|={len(e)} budget={budget}s ===', flush=True)
    arcs,iters,status=cegar(name,n,e,time_budget=budget)
    if arcs is not None:
        print('RESULT '+json.dumps({'name':name,'n':n,'FOUND_chi_d>=3':True,'iters':iters,'arcs':arcs}), flush=True)
    else:
        print(f'RESULT {{"name":"{name}","n":{n},"FOUND":false,"status":"{status}","iters":{iters}}}', flush=True)
