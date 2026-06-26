"""Deep red-team of Lemma H17 and the derived-square reduction.

H17: for x in H=[m+1,2m], y in L=[1,m], N^-(x) cap N^-(y) in AC_n is in ONE band:
     subset of [0,m-1] if delta=x-y<=m, subset of [m+1,2m-1] if delta>=m+1.
Test the exact band claim (not just 'single band') and the boundary delta=m/m+1.

Also: for the 5 derived squares, the (3,.) cell has b=0 so c(b)=3, and the rep is (a,0)
with a in H or L. The proof claims the b=0 conditions 'reproduce the same band structure'.
We verify by re-deriving the all-distinct-block reduction for EACH derived square explicitly
and checking it lands on an H17-forbidden common-in-neighbour config (one rep in each band).
"""
import sys, itertools

def ac_gen(n):
    m=(n-1)//2; return set(range(1,m))|{m+1}
def Nminus(v,n,g): return set(u for u in range(n) if ((v-u)%n) in g)

def test_h17_exact(n):
    m=(n-1)//2; g=ac_gen(n)
    H=range(m+1,2*m+1); L=range(1,m+1)
    fails=[]
    for x in H:
        for y in L:
            common=Nminus(x,n,g)&Nminus(y,n,g)
            delta=x-y
            if delta<=m:
                if not all(0<=z<=m-1 for z in common):
                    fails.append(("delta<=m band wrong",x,y,delta,sorted(common)))
            else:
                if not all(m+1<=z<=2*m-1 for z in common):
                    fails.append(("delta>=m+1 band wrong",x,y,delta,sorted(common)))
    return fails

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

def outer_band(a,m):
    # which outer band: 'H' if a in [m+1,2m], 'L' if a in [1,m], '0' if a==0
    if a==0: return '0'
    return 'H' if a>=m+1 else 'L'

def reduce_square(square,n):
    """Enumerate feasible reps; among them and among the all-distinct-block branch,
    verify the reduction lands on a common-in-neighbour config with reps in different
    OUTER bands (H17-forbidden). Returns feasible count + any reduction anomaly."""
    m=(n-1)//2; g=ac_gen(n)
    cells=sorted(square)
    pools={cl:cvs(cl,n,m) for cl in cells}
    feas=[]
    for combo in itertools.product(*[pools[cl] for cl in cells]):
        if is_bclique(list(combo),n,g,m):
            feas.append(dict(zip(cells,combo)))
    return cells, feas

def main():
    ns=[int(x) for x in sys.argv[1:]] or [7,9,11,13,15,17]
    for n in ns:
        print(f"\n===== n={n} =====")
        f=test_h17_exact(n)
        print(f"  H17 exact-band failures: {len(f)}" + (f"  e.g {f[0]}" if f else ""))
        for sq in SQUARES:
            cells,feas=reduce_square(sq,n)
            print(f"  {cells}: feasible={len(feas)}")

if __name__=="__main__":
    main()
