import sys, time
sys.path.insert(0, "scripts")
import core
from search_4critical_circulant import omega_vec_ge_K_via_sat

def beats_set(n, arcs):
    b = [[False]*n for _ in range(n)]
    for (u,v) in arcs:
        b[u][v] = True
    return b

def lex_substitute(outer, inner):
    """outer[X] := T[H] = lexicographic product. Block per outer vertex.
    flat index o*ni + a. Within block: inner arc. Between blocks: outer arc."""
    (no, ao) = outer
    (ni, ai) = inner
    bo = beats_set(no, ao)
    bi = beats_set(ni, ai)
    N = no*ni
    arcs = []
    for o1 in range(no):
        for a1 in range(ni):
            u = o1*ni + a1
            for o2 in range(no):
                for a2 in range(ni):
                    v = o2*ni + a2
                    if u >= v:
                        continue
                    # decide orientation u vs v
                    if o1 == o2:
                        beat = bi[a1][a2]
                    else:
                        beat = bo[o1][o2]
                    if beat:
                        arcs.append((u, v))
                    else:
                        arcs.append((v, u))
    return N, arcs

def AC(n, g):
    arcs = []
    gs = set(x % n for x in g)
    for i in range(n):
        for j in range(n):
            if i==j: continue
            if (j - i) % n in gs:
                arcs.append((i,j))
    return n, arcs

def is_tournament(n, arcs):
    seen = set()
    for (u,v) in arcs:
        if (v,u) in seen: return False
        seen.add((u,v))
    return len(arcs) == n*(n-1)//2

C3 = (3, [(0,1),(1,2),(2,0)])
AC7 = AC(7, {1,2,4})

# Inner objects
AC7_C3 = lex_substitute(AC7, C3)      # order 21, composite proven-4-critical
C3_AC7 = lex_substitute(C3, AC7)      # order 21, anchor (simple inner)
C3_AC7_C3 = lex_substitute(C3, AC7_C3) # order 63, the decision target

print("is_tournament C3[AC7] (21):", is_tournament(*C3_AC7))
print("is_tournament AC7[C3] (21):", is_tournament(*AC7_C3))
print("is_tournament C3[AC7[C3]] (63):", is_tournament(*C3_AC7_C3))
sys.stdout.flush()

# STEP 1: anchor C3[AC7] order 21: expect omega_vec=4 (no-K5 UNSAT False=> not>=5 ... wait)
# omega_vec_ge_K_via_sat returns (ge_K,...). anchor: omega_vec=4 => ge_4 True, ge_5 False.
n,arcs = C3_AC7
t=time.time()
ge4,dt4,_ = omega_vec_ge_K_via_sat(n,arcs,4)
ge5,dt5,_ = omega_vec_ge_K_via_sat(n,arcs,5)
print(f"ANCHOR C3[AC7] (21): ge_4={ge4} ({dt4:.3f}s) ge_5={ge5} ({dt5:.3f}s)  => omega_vec={'4' if (ge4 and not ge5) else 'OTHER'}")
sys.stdout.flush()
