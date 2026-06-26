import sys, itertools as it
sys.path.insert(0,'scripts')
import h2_oracle as H
import flipspace_census as FC
from itertools import combinations

# Targeted, less-biased k>=3 search. For each k>=3 digon-forest, enumerate ALL candidate
# directed single-cycles (no cap), classify each by which nontrivial components it touches,
# and build balanced single-arc sets as arc-disjoint unions of cycles that COLLECTIVELY touch
# all k components (so the digraph can be strong). Prioritize crossing/full-support cycles.

def comp_of(n, edges):
    par=list(range(n))
    def find(x):
        while par[x]!=x: par[x]=par[par[x]]; x=par[x]
        return x
    for u,v in edges: par[find(u)]=find(v)
    root={}
    comp=[0]*n
    for i in range(n):
        r=find(i); comp[i]=r
    # relabel nontrivial
    from collections import Counter
    sizes=Counter(comp)
    nt=[r for r,c in sizes.items() if c>1]
    ntidx={r:i for i,r in enumerate(nt)}
    return comp, ntidx

def run(n, max_unions=4000, prog=2000):
    forests=[e for e in FC.gen_forests(n) if len(e)>=2 and FC.nontrivial_comp_count(n,e)>=3]
    print(f"n={n}: k>=3 forests={len(forests)}", flush=True)
    seen=set(); chi3=[]; examined=0
    for fi,edges in enumerate(forests):
        comp,ntidx=comp_of(n,edges)
        k=len(ntidx)
        arcs_base=[]; ds=set()
        for (u,v) in edges: arcs_base+=[(u,v),(v,u)]; ds|={(u,v),(v,u)}
        cands=[(u,v) for u in range(n) for v in range(n) if u!=v and (u,v) not in ds]
        cl=list(H._directed_cycles(n,cands))
        # classify cycles by set of nontrivial comps touched
        info=[]
        for cyc in cl:
            t=frozenset(ntidx[comp[v]] for v in cyc if comp[v] in ntidx)
            info.append((cyc,t))
        # candidate building: greedily union arc-disjoint cycles until all k comps covered.
        # enumerate unions of size 1..3 prioritizing crossing (|t|>=2) cycles and full-support.
        cross=[x for x in info if len(x[1])>=2]
        # sort: full-support first
        cross.sort(key=lambda x:-len(x[1]))
        unions=0
        # single full-support cycles
        cand_unions=[]
        for (cyc,t) in cross:
            cand_unions.append([(cyc,t)])
        # pairs/triples of cross cycles
        for r in (2,3):
            for combo in combinations(range(len(cross)), r):
                cand_unions.append([cross[i] for i in combo])
                unions+=1
                if unions>=max_unions: break
            if unions>=max_unions: break
        for grp in cand_unions:
            sarcs=set(); ok=True; touched=set()
            for (cyc,t) in grp:
                touched|=t
                for i in range(len(cyc)):
                    a=(cyc[i],cyc[(i+1)%len(cyc)])
                    if a in sarcs: ok=False;break
                    sarcs.add(a)
                if not ok:break
            if not ok or len(touched)<k: continue  # must reach all components
            arcs=arcs_base+list(sarcs)
            key=frozenset(arcs)
            if key in seen: continue
            seen.add(key)
            if not H.is_strong(n,arcs): continue
            if not H.is_2connected(n,arcs): continue
            if H.lambda_D(n,arcs)!=2: continue
            examined+=1
            if H.chi_vec(n,arcs)==3:
                kk,tiles,cov,tot,ncod1,kraft=FC.flip_analysis(n,arcs)
                chi3.append((arcs,kk,tiles,cov,tot,kraft))
                print(f"   *** chi3 k={kk} tiles={tiles} cov={cov}/{tot} kraft={kraft:.3f} arcs={arcs}", flush=True)
        if fi%prog==0:
            print(f"   ...forest {fi}/{len(forests)} examined={examined} chi3={len(chi3)}", flush=True)
    print(f"n={n}: examined(strong&2conn&lam2, full-support k>=3)={examined}, chi3 k>=3 found={len(chi3)}", flush=True)
    return chi3

if __name__=='__main__':
    ns=[int(x) for x in sys.argv[1:]] or [8]
    for n in ns: run(n)
