import sys, itertools as it
sys.path.insert(0,'scripts')
import h2_oracle as H
import flipspace_census as FC
from itertools import combinations

# Decisive KILL test: search for ANY chi=3, strong, 2-connected, lambda_D=2 member
# whose digon-forest has k>=3 nontrivial components. Restrict forest enumeration to k>=3.
# Record k and flip-space tiling for every chi=3 hit.

def run(n, max_subset_total=8000, max_forests=None, prog=100, cyc_cap=50):
    forests=[e for e in FC.gen_forests(n) if len(e)>=2 and FC.nontrivial_comp_count(n,e)>=3]
    if max_forests: forests=forests[:max_forests]
    print(f"n={n}: k>=3 digon-forests processed={len(forests)}", flush=True)
    seen=set()
    chi3=[]
    examined=0
    for fi,edges in enumerate(forests):
        arcs_base=[]; digonset=set()
        for (u,v) in edges:
            arcs_base+=[(u,v),(v,u)]; digonset|={(u,v),(v,u)}
        cands=[(u,v) for u in range(n) for v in range(n) if u!=v and (u,v) not in digonset]
        cyc_list=list(H._directed_cycles(n,cands))
        if len(cyc_list)>cyc_cap: cyc_list=cyc_list[:cyc_cap]
        subsets=[]
        for r in (1,2,3,4):
            for combo in combinations(range(len(cyc_list)), r):
                subsets.append(combo)
                if len(subsets)>=max_subset_total: break
            if len(subsets)>=max_subset_total: break
        for combo in subsets:
            sarcs=set(); ok=True
            for ci in combo:
                cyc=cyc_list[ci]
                for i in range(len(cyc)):
                    a=(cyc[i],cyc[(i+1)%len(cyc)])
                    if a in sarcs: ok=False; break
                    sarcs.add(a)
                if not ok: break
            if not ok or not sarcs: continue
            arcs=arcs_base+list(sarcs)
            key=frozenset(arcs)
            if key in seen: continue
            seen.add(key)
            if not H.is_strong(n,arcs): continue
            if not H.is_2connected(n,arcs): continue
            if H.lambda_D(n,arcs)!=2: continue
            examined+=1
            if H.chi_vec(n,arcs)==3:
                k,tiles,cov,tot,ncod1,kraft=FC.flip_analysis(n,arcs)
                chi3.append((arcs,k,tiles,cov,tot,kraft))
                print(f"   *** chi3 with k={k}: tiles={tiles} cov={cov}/{tot} kraft={kraft:.3f} arcs={arcs}", flush=True)
        if fi%prog==0:
            print(f"   ...forest {fi}/{len(forests)} examined={examined} chi3so far={len(chi3)}", flush=True)
    print(f"n={n}: examined(strong&2conn&lam2, k>=3)={examined}, chi3 found={len(chi3)}", flush=True)
    return chi3

if __name__=='__main__':
    ns=[int(x) for x in sys.argv[1:]] or [7]
    for n in ns:
        run(n)
