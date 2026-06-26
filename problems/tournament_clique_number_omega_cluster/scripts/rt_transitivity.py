"""Verify vertex-transitivity of AC_n[AC_n] independently, and test several deletions
exactly for n=7 (via the SAT-exact module) to confirm EVERY deletion gives 4, not 5."""
import sys
import rt_sat_exact as RT

def is_automorphism(n, perm_func):
    V, arc = RT.build_T(n)
    Vset = set(V)
    # perm_func maps vertex->vertex; check bijection + arc-preserving
    img = [perm_func(v) for v in V]
    if set(img) != Vset:
        return False
    for u in V:
        for v in V:
            if u==v: continue
            if arc(u,v) != arc(perm_func(u), perm_func(v)):
                return False
    return True

def main():
    n = 7
    # claimed automorphisms: (x,y) -> (x+s, y+t)
    ok = True
    for s in range(n):
        for t in range(n):
            f = lambda v, s=s, t=t: ((v[0]+s)%n, (v[1]+t)%n)
            if not is_automorphism(n, f):
                ok = False
                print(f"NOT auto: s={s} t={t}")
    print(f"n={n}: all (x+s,y+t) automorphisms? {ok}  -> vertex-transitive on n^2 orbit")
    sys.stdout.flush()
    # Since translations act transitively on vertices, omega_vec(T-v) is the same for all v.
    # Still, directly test a non-(0,0) deletion exactly to be safe.
    for delv in [(0,0),(1,0),(0,1),(3,4),(2,5)]:
        Vd, arcd = RT.build_T(n, delete=delv)
        w = RT.omega_vec_exact(Vd, arcd, lo=3, hi=6)
        print(f"  delete {delv}: omega_vec = {w}")
        sys.stdout.flush()

if __name__ == "__main__":
    main()
