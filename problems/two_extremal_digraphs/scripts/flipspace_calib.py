import sys
sys.path.insert(0, 'scripts')
import h2_oracle as H
from itertools import product

def analyze(n, arcs, label):
    arcset = set(arcs)
    # digon edges (undirected) vs singles
    digons = set()
    singles = []
    for (u,v) in arcs:
        if (v,u) in arcset:
            if u < v:
                digons.add((u,v))
        else:
            singles.append((u,v))
    # build digon forest, find components
    adj = {i: [] for i in range(n)}
    for (u,v) in digons:
        adj[u].append(v); adj[v].append(u)
    comp = [-1]*n
    nc = 0
    comps = []
    for s in range(n):
        if comp[s] == -1:
            stack=[s]; comp[s]=nc; members=[s]
            while stack:
                x=stack.pop()
                for y in adj[x]:
                    if comp[y]==-1:
                        comp[y]=nc; stack.append(y); members.append(y)
            comps.append(members); nc+=1
    # nontrivial components = those with >1 vertex (have at least one digon)
    nontrivial = [c for c in comps if len(c)>1]
    k = len(nontrivial)
    # canonical bipartition within each nontrivial component (2-color the tree)
    color = {}
    for members in comps:
        if len(members)<=1:
            color[members[0]]=0
            continue
        # BFS 2-color
        root = members[0]
        color[root]=0
        stack=[root]
        while stack:
            x=stack.pop()
            for y in adj[x]:
                if y not in color:
                    color[y]=1-color[x]; stack.append(y)
    # map nontrivial component -> bit index
    comp_bit = {}
    for i,members in enumerate(nontrivial):
        cid = comp[members[0]]
        comp_bit[cid] = i
    # For a flip vector f in F2^k, vertex v's color = color[v] XOR f[comp_bit[comp[v]]] if nontrivial else color[v]
    def vcolor(v, f):
        cid = comp[v]
        if cid in comp_bit:
            return color[v] ^ f[comp_bit[cid]]
        return color[v]  # trivial comp: fixed (but its color is free? treat as fixed 0)
    # enumerate single-arc dicycles
    cycles = list(H._directed_cycles(n, singles))
    print(f"=== {label}: n={n}, k(nontrivial comps)={k}, #digons={len(digons)}, #singles={len(singles)}, #single-dicycles={len(cycles)}")
    print(f"    chi_vec={H.chi_vec(n,arcs)}, lambda_D={H.lambda_D(n,arcs)}, 2conn={H.is_2connected(n,arcs)}, strong={H.is_strong(n,arcs)}")
    flips = list(product([0,1], repeat=k)) if k>0 else [()]
    crossing_dicycles=[]
    for cyc in cycles:
        # cyc is a list of vertices forming a directed cycle in singles
        comps_touched = set(comp[v] for v in cyc)
        # restrict to nontrivial
        nt_touched = set(c for c in comps_touched if c in comp_bit)
        c_count = len(nt_touched) if len(nt_touched)>0 else 0
        # count mono flips: cycle is monochromatic when all vertices same color under f
        mono_set = []
        for f in flips:
            cols = set(vcolor(v,f) for v in cyc)
            if len(cols)==1:
                mono_set.append(f)
        mono_frac = len(mono_set)/len(flips)
        is_crossing = len(nt_touched) >= 2
        if is_crossing:
            crossing_dicycles.append((cyc, c_count, mono_frac, len(mono_set), set(mono_set)))
        tag = "CROSS" if is_crossing else ("intra" if len(nt_touched)==1 else "trivial-only")
        print(f"    cycle {cyc}: comps_touched(nt)={sorted(nt_touched)}, c={c_count}, mono_frac={mono_frac:.3f}, mono#={len(mono_set)}/{len(flips)} [{tag}]")
    # Kraft-cross sum over crossing dicycles (parity-consistent => nonempty mono set)
    kraft = sum(2**(-(c-1)) for (_,c,mf,ms,_) in crossing_dicycles if ms>0)
    print(f"    #crossing-dicycles={len(crossing_dicycles)}, Kraft-cross sum={kraft:.3f}")
    # does the union of mono-sets of single-arc dicycles cover all 2^k flips?
    covered=set()
    for cyc in cycles:
        for f in flips:
            cols=set(vcolor(v,f) for v in cyc)
            if len(cols)==1:
                covered.add(f)
    print(f"    coverage of F2^k by mono single-dicycles: {len(covered)}/{len(flips)}  tiles={len(covered)==len(flips)}")
    return k, len(covered), len(flips)

# n=7 chi=3 truth member
n7 = 7
arcs7 = [(0,2),(0,4),(0,5),(1,3),(1,6),(2,0),(2,4),(3,5),(3,6),(4,0),(4,6),(5,0),(5,1),(6,1),(6,2),(6,3)]
analyze(n7, arcs7, "n7-chi3")

# n=6 chi=2 antecedent
n6 = 6
arcs6 = [(0,1),(0,2),(1,3),(1,4),(2,0),(2,3),(2,5),(3,1),(3,4),(3,5),(4,2),(4,3),(5,0),(5,2)]
analyze(n6, arcs6, "n6-chi2")
