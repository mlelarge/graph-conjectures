"""ASYMPTOTIC-ARGUMENT probe (lens=asymptotic-argument).

CLAIM (the move): For the almost-consecutive circulant family
   C_p(g),  g(p) = {1,...,(p-3)/2} u {(p+1)/2}   (p an odd prime, p>=7),
the deletion  T-0 = C_p(g) minus vertex 0  has  omega_vec(T-0) = 2  for ALL p,
witnessed by the SINGLE EXPLICIT, p-UNIFORM total order  1 < 2 < ... < p-1
(the identity order on the surviving vertices).  Its backedge graph is
TRIANGLE-FREE (=> omega <= 2), and contains a directed C3 (=> omega_vec >= 2),
so omega_vec(T-0) = 2 EXACTLY -- as a THEOREM-shaped certificate, not a per-p
oracle branch-and-bound.

WHY (the asymptotic mechanism, to be turned into a proof):
Under identity order, edge {i,j} (i<j, i,j in 1..p-1) is a backedge iff
(j-i) mod p in -g.  On 1..p-1 the realizable differences j-i lie in [1,p-2],
and  (-g) cap [1,p-2] = { (p-1)/2 }  U  { (p+3)/2, (p+3)/2+1, ..., p-2 }.
A triangle needs i<j<k with all of (j-i),(k-j),(k-i) backedge differences.
For any two backedge differences d1,d2 from this set, d1+d2 >= (p-1)/2 + (p+3)/2
= p+1 > p-2, so the closing difference (k-i)=d1+d2 EXCEEDS the maximum
realizable difference p-2 -- hence NO triangle can close. This is a clean
counting/size obstruction that holds for every p, i.e. an ASYMPTOTIC argument.

This is the piece G9's surviving kill-ground (1) demanded: vertex-transitivity
forces all deletions EQUAL; this certificate proves that common value is = 2
uniformly, removing the per-p oracle dependence for the deletion direction.
The remaining open gap for an infinite 3-critical family is ONLY the
whole-tournament LOWER bound omega_vec(C_p(g)) >= 3 (the p=19 executor probe).

FALSIFIER: if for ANY prime p>=7 in the family the identity order's backedge
graph on the deletion is NOT triangle-free (a triangle exists), or if the
size bound d1+d2>p-2 fails, the uniform certificate is dead and the deletion
value must be re-checked per p (the move is killed). Also cross-checked against
the CANONICAL oracle core.omega_vec_bb(T-0, ub=3) on small p to confirm == 2.
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import core


def acgen(p):
    return set(range(1, (p - 3) // 2 + 1)) | {(p + 1) // 2}


def circ_arcs(p, g):
    arcs = []
    for i in range(p):
        for d in g:
            arcs.append((i, (i + d) % p))
    return arcs


def neg(p, g):
    return set((p - d) % p for d in g)


def is_prime(n):
    if n < 2:
        return False
    i = 2
    while i * i <= n:
        if n % i == 0:
            return False
        i += 1
    return True


def identity_order_triangle_free(p):
    """On deletion verts 1..p-1 in identity order, test backedge graph triangle-free.
    Returns (is_tf, witness_triangle_or_None, backedge_diffs, max_diff_sum)."""
    g = acgen(p)
    ng = neg(p, g)
    verts = list(range(1, p))
    adj = {v: set() for v in verts}
    for a in range(len(verts)):
        for b in range(a + 1, len(verts)):
            i, j = verts[a], verts[b]
            if (j - i) % p in ng:  # backward arc j->i exists iff (i-j) in g iff (j-i) in -g
                adj[i].add(j)
                adj[j].add(i)
    tf, tri = True, None
    for v in verts:
        for w in adj[v]:
            if w > v and (adj[v] & adj[w]):
                tf, tri = False, (v, w, sorted(adj[v] & adj[w])[0])
                break
        if not tf:
            break
    diffs = sorted(d for d in ng if 1 <= d <= p - 2)
    max_sum = (diffs[0] + diffs[1]) if len(diffs) >= 2 else None  # smallest two
    return tf, tri, diffs, max_sum


def main():
    primes = [p for p in range(7, 80) if is_prime(p)]
    print(f"{'p':>3} {'idTF':>5} {'min2sum':>8} {'p-2':>4} {'gap_ok':>7} {'oracle_del':>11}")
    all_ok = True
    for p in primes:
        tf, tri, diffs, msum = identity_order_triangle_free(p)
        gap_ok = (msum is not None and msum > p - 2)
        oracle_val = ""
        if p <= 23:  # canonical cross-check only where bb is fast
            g = acgen(p)
            arcs = circ_arcs(p, g)
            assert core.is_tournament(p, arcs)
            keep = list(range(1, p))
            n2, arcs2 = core.subtournament(p, arcs, keep)
            oracle_val = str(core.omega_vec_bb(n2, arcs2, ub=3))
        ok = tf and gap_ok and (oracle_val in ("", "2"))
        all_ok = all_ok and ok
        print(f"{p:>3} {str(tf):>5} {str(msum):>8} {p-2:>4} {str(gap_ok):>7} {oracle_val:>11}")
        if not tf:
            print(f"    !!! TRIANGLE at {tri} -- CERTIFICATE FALSIFIED for p={p}")
    print("ALL_OK =", all_ok)
    print("\nINTERPRETATION: ALL_OK=True  =>  uniform identity-order certificate")
    print("proves omega_vec(C_p(g)-0)=2 for the whole family (deletion direction")
    print("of 3-criticality is THEOREM-shaped). Remaining open = whole-tournament")
    print("lower bound omega_vec(C_p(g))>=3 only.")
    print("ALL_OK=False at some p  =>  move KILLED, deletion not uniformly =2.")


if __name__ == "__main__":
    main()
