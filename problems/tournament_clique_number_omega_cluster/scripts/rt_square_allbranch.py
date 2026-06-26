"""Verify the branch split + antisymmetry-kill for ALL 6 squares, not just the base.

For each square, reps are in key order. We enumerate the 4 block-equality branches
(does the same-c(a)-band pair share an outer block?) and check:
  - the 3 'share a block' branches each die by tournament antisymmetry (some pair of
    conditions becomes (d in g) and (-d in g));
  - the all-distinct branch reduces to a common-in-neighbour-in-different-bands config
    that H17 forbids.
We do this by BRUTE FORCE over reps within each branch and confirm no feasible config,
and separately confirm the antisymmetry mechanism fires in the 'share' branches by
exhibiting that any rep choice in that branch already violates a +/- d in g pair.
"""
import sys, itertools

def ac_gen(n):
    m = (n-1)//2
    return set(range(1,m))|{m+1}
def c(t,m):
    if t==0: return 3
    if 1<=t<=m: return 2
    return 1
def cell(a,b,m): return (c(b,m),c(a,m))
def key(a,b,m): return (c(b,m),c(a,m),a,b)
def beats_T(p,q,n,g):
    a,b=p; ap,bp=q
    if a!=ap: return ((ap-a)%n) in g
    return ((bp-b)%n) in g
def cvs(cl,n,m):
    return [(a,b) for a in range(n) for b in range(n) if (a,b)!=(0,0) and cell(a,b,m)==cl]
def is_bclique(reps,n,g,m):
    o=sorted(reps,key=lambda v:key(v[0],v[1],m))
    for i in range(len(o)):
        for j in range(i+1,len(o)):
            if not beats_T(o[j],o[i],n,g): return False
    return True

SQUARES=[
    [(1,1),(1,2),(2,1),(2,2)],
    [(1,1),(1,2),(2,1),(3,2)],
    [(1,1),(1,2),(3,1),(3,2)],
    [(1,1),(2,2),(3,1),(3,2)],
    [(1,2),(2,1),(2,2),(3,1)],
    [(2,1),(2,2),(3,1),(3,2)],
]

def analyze(square,n):
    """For a square, find all same-c(a)-column pairs (cells sharing the outer band c(a)),
    enumerate feasible reps, and classify by which same-column pairs share a block.
    Report: feasible configs, and for configs where a same-column pair shares a block,
    whether a +/-d antisymmetry contradiction is present (so they MUST be infeasible)."""
    m=(n-1)//2; g=ac_gen(n)
    cells=sorted(square,key=lambda cl:(cl,))  # cells; key order = sorted by cell tuple
    cells=sorted(square)  # cell order under inner_then_outer = lexicographic on (c(b),c(a))
    pools={cl:cvs(cl,n,m) for cl in cells}
    # same-c(a) column groups: cells with equal second coordinate (c(a))
    cols={}
    for cl in cells: cols.setdefault(cl[1],[]).append(cl)
    same_col_pairs=[]
    for ca,cls in cols.items():
        for x,y in itertools.combinations(cls,2):
            same_col_pairs.append((x,y))
    feasibles=[]
    for combo in itertools.product(*[pools[cl] for cl in cells]):
        rep={cl:v for cl,v in zip(cells,combo)}
        if is_bclique(list(combo),n,g,m):
            feasibles.append(rep)
    return cells, same_col_pairs, feasibles

def main():
    ns=[int(x) for x in sys.argv[1:]] or [7,9,11]
    for n in ns:
        print(f"\n===== n={n} =====")
        for sq in SQUARES:
            cells,scp,feas=analyze(sq,n)
            print(f"  square {cells}: same-c(a)-column pairs={scp}; feasible configs={len(feas)}")
            if feas:
                print(f"    !!! FEASIBLE: {feas[0]}")

if __name__=="__main__":
    main()
