#!/usr/bin/env python3
"""
Directly test the LOAD-BEARING CLAIM inside Prop 3.1's proof:

  For every valid k-dicolouring phi of a Hajos join D = D1 v D2, at least one
  of the two side-restrictions phi|_{D1}, phi|_{D2} is a valid k-dicolouring of
  its factor.

This is exactly the "Claim" the splice argument proves. If it ever fails, the
splice argument's conclusion is contradicted (some phi exists but neither
restriction is valid AND yet phi is a valid colouring of D -> the splice cycle W
would have to be both present and absent). We test it for k=2 AND k=3, over
arbitrary small factors, with FULL enumeration of valid dicolourings of the join.

Also: when BOTH restrictions fail, explicitly construct the splice walk
W = (u->w) . P2 . P1 and verify it is a monochromatic closed walk in D that
contains a monochromatic dicycle -> contradiction with phi valid. (We instead
verify the contrapositive: whenever phi is valid on D, the bad case never
occurs.)
"""
import sys, os, itertools, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import h2_oracle as O
from adv_condL_hajos_lb import hajos_join, is_weakly_connected


def valid_k_dicolourings(n, arcs, k):
    oadj = O.out_adj(n, arcs)
    for col in itertools.product(range(k), repeat=n):
        ok = True
        for c in range(k):
            sub = {i for i in range(n) if col[i] == c}
            if O._has_dicycle_in_subset(oadj, sub):
                ok = False; break
        if ok:
            yield col


def restriction_valid(n_piece, arcs_piece, full_col, lab_map, k):
    oadj = O.out_adj(n_piece, arcs_piece)
    col = [full_col[lab_map[i]] for i in range(n_piece)]
    for c in range(k):
        sub = {i for i in range(n_piece) if col[i] == c}
        if O._has_dicycle_in_subset(oadj, sub):
            return False
    return True


def reconstruct_factors(n1, A1, u, v1, n2, A2, v2, w):
    """Return (D1, map1), (D2, map2) where D_i = D[S_i] + interface arc, and
    map_i sends piece labels to join labels. D1 = original A1 (with u->v1),
    D2 = original A2 (with v2->w)."""
    n, arcs, v_lab, u_img, w_img, S1, S2, map1, map2 = hajos_join(
        n1, A1, u, v1, n2, A2, v2, w)
    # D1 reconstructed = (n1, A1) with map1 (identity). D2 = (n2, A2) with map2.
    return (n, arcs), (n1, frozenset(A1), map1), (n2, frozenset(A2), map2)


def test_claim(k, limit=4000, seed=0):
    rng = random.Random(seed)
    pool = []
    for n in (2, 3, 4):
        verts = list(range(n))
        pairs = [(i, j) for i in verts for j in verts if i != j]
        for _ in range(150):
            r = rng.randint(1, len(pairs))
            A = frozenset(rng.sample(pairs, r))
            if A and is_weakly_connected(n, A):
                pool.append((n, A))
    fails = []
    total = 0
    for _ in range(limit):
        (n1, A1) = rng.choice(pool); (n2, A2) = rng.choice(pool)
        A1 = set(A1); A2 = set(A2)
        (u, v1) = rng.choice(list(A1)); (v2, w) = rng.choice(list(A2))
        (n, arcs), (pn1, pA1, m1), (pn2, pA2, m2) = reconstruct_factors(
            n1, A1, u, v1, n2, A2, v2, w)
        for phi in valid_k_dicolourings(n, arcs, k):
            total += 1
            ok1 = restriction_valid(pn1, pA1, phi, m1, k)
            ok2 = restriction_valid(pn2, pA2, phi, m2, k)
            if not (ok1 or ok2):
                fails.append((k, (n1, sorted(A1), u, v1),
                              (n2, sorted(A2), v2, w), phi))
                if len(fails) >= 5:
                    return total, fails
    return total, fails


def main():
    for k in (2, 3):
        t, f = test_claim(k, limit=2500, seed=100 + k)
        print(f"=== Claim of Prop 3.1, k={k} ===")
        print(f"  (phi,join) pairs checked: {t}; "
              f"both-restrictions-fail-yet-phi-valid: {len(f)}")
        for x in f:
            print("   COUNTEREXAMPLE TO CLAIM:", x)
    return 0


if __name__ == "__main__":
    sys.exit(main())
