import sys, itertools, signal
sys.path.insert(0, 'scripts')
import h2_oracle as H
from itertools import product, combinations

# Generic M-class census: digon-forest with >=2 nontrivial components + balanced single arcs.
# Filter: strong, 2-connected, lambda_D==2. Record chi_vec, k, flip-space tiling.
# Then look for KILL: chi=3 member with k>=3 that tiles F2^k.

def flip_analysis(n, arcs):
    arcset = set(arcs)
    digons = set()
    singles = []
    for (u,v) in arcs:
        if (v,u) in arcset:
            if u<v: digons.add((u,v))
        else:
            singles.append((u,v))
    adj = {i:[] for i in range(n)}
    for (u,v) in digons:
        adj[u].append(v); adj[v].append(u)
    comp=[-1]*n; nc=0; comps=[]
    for s in range(n):
        if comp[s]==-1:
            st=[s]; comp[s]=nc; mem=[s]
            while st:
                x=st.pop()
                for y in adj[x]:
                    if comp[y]==-1:
                        comp[y]=nc; st.append(y); mem.append(y)
            comps.append(mem); nc+=1
    nontrivial=[c for c in comps if len(c)>1]
    k=len(nontrivial)
    color={}
    for mem in comps:
        if len(mem)<=1:
            color[mem[0]]=0; continue
        root=mem[0]; color[root]=0; st=[root]
        while st:
            x=st.pop()
            for y in adj[x]:
                if y not in color:
                    color[y]=1-color[x]; st.append(y)
    comp_bit={}
    for i,mem in enumerate(nontrivial):
        comp_bit[comp[mem[0]]]=i
    def vcolor(v,f):
        cid=comp[v]
        if cid in comp_bit: return color[v]^f[comp_bit[cid]]
        return color[v]
    cycles=list(H._directed_cycles(n,singles))
    flips=list(product([0,1],repeat=k)) if k>0 else [()]
    covered=set()
    n_cross_codim1=0
    kraft=0.0
    for cyc in cycles:
        nt=set(comp[v] for v in cyc if comp[v] in comp_bit)
        c=len(nt)
        mono=[f for f in flips if len(set(vcolor(v,f) for v in cyc))==1]
        for f in mono: covered.add(f)
        if c>=2 and len(mono)>0:
            kraft+=2**(-(c-1))
            if len(mono)==len(flips)//2:  # codim-1
                n_cross_codim1+=1
    return k, len(covered)==len(flips), len(covered), len(flips), n_cross_codim1, kraft

# Generate digon forests on n vertices with >=2 nontrivial components.
# Approach: enumerate forests (sets of undirected edges, acyclic) on n vertices,
# require >=2 components each having >=1 edge (nontrivial). Then add balanced single arcs.
# This is large; we enumerate forests as edge-subsets and prune. Then add singles to make
# the whole digraph strong/eulerian-ish. We brute single-arc sets among non-digon pairs.

def gen_forests(n):
    # all forests (acyclic undirected edge sets) on n vertices via edge subsets, pruned
    pairs=list(combinations(range(n),2))
    # to limit blowup, build forests incrementally
    forests=[]
    def parent_find(par,x):
        while par[x]!=x: par[x]=par[par[x]]; x=par[x]
        return x
    # iterative deepening over edge count using DFS over sorted pairs
    results=[]
    def rec(idx, edges, par):
        results.append(list(edges))
        for j in range(idx,len(pairs)):
            u,v=pairs[j]
            ru,rv=parent_find(par,u),parent_find(par,v)
            if ru!=rv:
                npar=par[:]; npar[ru]=rv
                edges.append((u,v))
                rec(j+1, edges, npar)
                edges.pop()
    rec(0,[],list(range(n)))
    return results

def nontrivial_comp_count(n, edges):
    par=list(range(n))
    def find(x):
        while par[x]!=x: par[x]=par[par[x]]; x=par[x]
        return x
    for u,v in edges:
        par[find(u)]=find(v)
    from collections import Counter
    sizes=Counter(find(i) for i in range(n))
    return sum(1 for s,c in sizes.items() if c>1)

def census(n, time_budget=600):
    start_signal()
    digon_forests=[e for e in gen_forests(n) if len(e)>=2 and nontrivial_comp_count(n,e)>=2]
    found_chi3=[]
    kill_candidates=[]  # chi=3, k>=3, tiles
    n_strong_lam2=0
    chi3_total=0
    # For each forest, the digon arcs are fixed. Remaining ordered pairs (not digon, not loop)
    # can carry single arcs. We need balanced (closed trails). Brute over single-arc subsets is huge;
    # restrict: pick single arcs as a directed subgraph that is balanced (in=out per vertex).
    # Enumerate via choosing a set of arcs from candidate ordered pairs whose in/out degrees match.
    # To keep feasible, cap candidate single-arc count and use the same approach as D4 generic search:
    # enumerate small balanced single-arc sets.
    seen=set()
    for edges in digon_forests:
        digonset=set()
        arcs_base=[]
        for (u,v) in edges:
            arcs_base.append((u,v)); arcs_base.append((v,u))
            digonset.add((u,v)); digonset.add((v,u))
        # candidate single ordered pairs: not a digon edge, u!=v
        cands=[(u,v) for u in range(n) for v in range(n) if u!=v and (u,v) not in digonset]
        # We need balanced single arcs. Enumerate subsets is 2^|cands| too big.
        # Use random/structured: generate balanced sets as unions of directed cycles among singles.
        # Build directed cycles among cands (length<=n) and take small unions.
        # For tractability, find all simple directed cycles in cand-graph (length 2..n) then
        # take unions of up to a few that are arc-disjoint.
        cyc_list=list(H._directed_cycles(n, cands))
        # take unions of subsets of these cycles (arc-disjoint not required; but avoid parallel duplicate arcs)
        # to bound, try single cycles and pairs and triples
        import itertools as it
        subsets=[]
        for r in (1,2,3):
            for combo in it.combinations(range(len(cyc_list)), r):
                subsets.append(combo)
                if len(subsets)>3000: break
            if len(subsets)>3000: break
        for combo in subsets:
            sarcs=set()
            ok=True
            for ci in combo:
                cyc=cyc_list[ci]
                for i in range(len(cyc)):
                    a=(cyc[i], cyc[(i+1)%len(cyc)])
                    if a in sarcs: ok=False; break
                    sarcs.add(a)
                if not ok: break
            if not ok or len(sarcs)==0: continue
            arcs=arcs_base+list(sarcs)
            key=frozenset(arcs)
            if key in seen: continue
            seen.add(key)
            # filters
            if not H.is_strong(n,arcs): continue
            if not H.is_2connected(n,arcs): continue
            if H.lambda_D(n,arcs)!=2: continue
            n_strong_lam2+=1
            cv=H.chi_vec(n,arcs)
            k,tiles,cov,tot,ncod1,kraft=flip_analysis(n,arcs)
            if cv==3:
                chi3_total+=1
                found_chi3.append((arcs,k,tiles,cov,tot,ncod1,kraft))
                if k>=3 and tiles:
                    kill_candidates.append((arcs,k,tiles,cov,tot,ncod1,kraft))
    return n_strong_lam2, chi3_total, found_chi3, kill_candidates

# timeout guard
def start_signal():
    pass

if __name__=='__main__':
    import argparse
    ns=[int(x) for x in sys.argv[1:]] or [6,7]
    for n in ns:
        nsl, c3, found, kills = census(n)
        # distribution of k among chi3
        from collections import Counter
        kdist=Counter(x[1] for x in found)
        tiledist=Counter((x[1],x[2]) for x in found)
        print(f"n={n}: strong&2conn&lambda2 examined={nsl}, chi3 found={c3}")
        print(f"   chi3 k-distribution: {dict(kdist)}")
        print(f"   chi3 (k,tiles)-distribution: {dict(tiledist)}")
        print(f"   KILL candidates (chi3,k>=3,tiles): {len(kills)}")
        for kc in kills[:5]:
            print(f"      KILL: arcs={kc[0]} k={kc[1]} tiles={kc[2]} cov={kc[3]}/{kc[4]} kraft={kc[6]:.3f}")
        # also any chi3 with k>=3 regardless of tiling
        k3=[x for x in found if x[1]>=3]
        print(f"   chi3 with k>=3 (any tiling): {len(k3)}")
        for x in k3[:5]:
            print(f"      k>=3: arcs={x[0]} k={x[1]} tiles={x[2]} cov={x[3]}/{x[4]} ncodim1={x[5]} kraft={x[6]:.3f}")
        sys.stdout.flush()
