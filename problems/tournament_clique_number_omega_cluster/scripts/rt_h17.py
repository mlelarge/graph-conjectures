"""Independently verify Lemma H17: for x in H=[m+1,2m], y in L=[1,m], the common
in-neighbourhood N^-(x) ∩ N^-(y) in AC_n lies entirely in one band (never both an
H-residue and an L-residue). Brute force for odd n up to 41."""
import sys
def check(n):
    m=(n-1)//2
    g={x%n for x in (set(range(1,m))|{m+1})}
    H=set(range(m+1,2*m+1)); L=set(range(1,m+1))
    Nin=lambda v:{(v-d)%n for d in g}  # in-neighbours: u->v iff (v-u) in g iff u=v-d
    bad=0
    for x in H:
        for y in L:
            common=Nin(x)&Nin(y)
            hasH=any(z in H for z in common)
            hasL=any(z in L for z in common)
            if hasH and hasL:
                bad+=1
                print(f"  n={n} x={x} y={y}: common={sorted(common)} has both H and L")
    return bad
total=0
for n in range(7,42,2):
    b=check(n); total+=b
print(f"H17: violations total = {total}")
sys.stdout.flush()
