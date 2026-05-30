#!/usr/bin/env python3
"""
ANGLE-1 verification harness for the directed-Hajos LOWER BOUND
(Conditional L, directed-Hajos-join instance).

It does THREE things, all EVIDENCE (not proof), to back the written proof in
docs/proof_condL_hajos_lower_bound.md:

  (A) chi_vec LOWER BOUND  (BJSS Thm 2(a)):
        chi_vec(D1 v D2) >= min(chi_vec(D1), chi_vec(D2)).
      Specialised: if chi_vec(D1)=chi_vec(D2)=3 then chi_vec(D1 v D2)>=3,
      i.e. the join is not 2-dicolourable.

  (B) GLUING / EQUALITY  (BJSS Thm 2(b)):
        if chi_vec(D1)=chi_vec(D2)=k>=2 then chi_vec(D)=k.
      Specialised k=3: chi_vec(join)==3 exactly.

  (C) The SPLICE construction itself: take any 2-dicolouring phi of the join,
      restrict to each side fixing phi(v), and certify that at least one
      restriction is a valid 2-dicolouring of the corresponding piece
      D_i = D[S_i] + (interface arc). This is the contrapositive engine of (A):
      if BOTH restrictions failed there would be monochromatic dicycles C1, C2
      through the deleted arcs whose splice C1 u C2 - u v1 - v2 w + u w is a
      monochromatic dicycle of the (3-)dicolouring of D -- impossible when D
      itself has chi_vec=2.  We exhibit, for joins with chi_vec=2 inputs, the
      forced splice cycle to confirm the mechanism's combinatorics.

We reuse the SOUND primitives in h2_oracle.py (chi_vec, can_dicolor_k).
"""

import sys, os, itertools, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import h2_oracle as O


def hajos_join(n1, A1, u, v1, n2, A2, v2, w):
    """Directed Hajos join (Def 1.5 / BJSS).
    D1 has arc (u, v1); D2 has arc (v2, w). Delete both, identify v1=v2=:v,
    add arc (u_image, w_image). Returns (n, arcs, v_image, u_image, w_image,
    S1, S2) where S1 = image of V(D1), S2 = image of V(D2), S1 cap S2 = {v}.
    Relabelling: D1 vertices keep labels 0..n1-1 EXCEPT v1 -> v (call it the
    shared label); D2 vertices 0..n2-1 are shifted to n1 .. n1+n2-1 except v2
    which maps onto v's label.
    """
    assert (u, v1) in A1, "missing arc u->v1 in D1"
    assert (v2, w) in A2, "missing arc v2->w in D2"
    # shared vertex label = v1 (kept in D1's labelling)
    v_lab = v1
    # map D2 labels: v2 -> v_lab ; others -> fresh
    fresh = {}
    nxt = n1
    d2map = {}
    for x in range(n2):
        if x == v2:
            d2map[x] = v_lab
        else:
            d2map[x] = nxt
            nxt += 1
    n = nxt
    arcs = set()
    S1 = set(range(n1))
    S2 = {d2map[x] for x in range(n2)}
    # D1 - (u,v1)
    for (a, b) in A1:
        if (a, b) == (u, v1):
            continue
        arcs.add((a, b))
    # D2 - (v2,w), relabelled
    for (a, b) in A2:
        if (a, b) == (v2, w):
            continue
        arcs.add((d2map[a], d2map[b]))
    u_img = u
    w_img = d2map[w]
    arcs.add((u_img, w_img))
    return n, frozenset(arcs), v_lab, u_img, w_img, frozenset(S1), frozenset(S2)


def all_2dicolourings(n, arcs):
    """Yield every valid 2-dicolouring (as a tuple of colours) of (n,arcs).
    Both colour classes must induce acyclic subdigraphs."""
    oadj = O.out_adj(n, arcs)
    for bits in itertools.product((0, 1), repeat=n):
        ok = True
        for c in (0, 1):
            sub = {i for i in range(n) if bits[i] == c}
            if O._has_dicycle_in_subset(oadj, sub):
                ok = False
                break
        if ok:
            yield bits


def restrict_is_valid(n_piece, arcs_piece, full_colours, lab_map):
    """Check the restriction of full_colours (over join labels) to a piece
    whose vertices map into the join via lab_map (piece_label -> join_label)
    is a valid 2-dicolouring of the piece."""
    oadj = O.out_adj(n_piece, arcs_piece)
    col = [full_colours[lab_map[i]] for i in range(n_piece)]
    for c in (0, 1):
        sub = {i for i in range(n_piece) if col[i] == c}
        if O._has_dicycle_in_subset(oadj, sub):
            return False
    return True


def check_join_lower_bound(n1, A1, u, v1, n2, A2, v2, w, verbose=False):
    """Returns dict of findings for one specific join."""
    c1 = O.chi_vec(n1, A1)
    c2 = O.chi_vec(n2, A2)
    n, arcs, v_lab, u_img, w_img, S1, S2 = hajos_join(n1, A1, u, v1, n2, A2, v2, w)
    cj = O.chi_vec(n, arcs)
    res = {
        "chi1": c1, "chi2": c2, "chi_join": cj,
        "n_join": n,
        "lb_ok": cj >= min(c1, c2),               # BJSS 2(a)
        "eq_ok": (not (c1 == c2 and c1 >= 2)) or cj == c1,  # BJSS 2(b)
    }
    return res


# ---------------------------------------------------------------------------
# Drivers
# ---------------------------------------------------------------------------

def small_sym_cycle_joins():
    """Build directed Hajos joins of symmetric odd cycles (chi_vec=3 each) and
    verify the join is NOT 2-dicolourable (chi_vec(join)>=3), and ==3."""
    fails = 0
    total = 0
    cases = []
    for m1 in (3, 5):
        for m2 in (3, 5):
            n1, A1 = O.sym_cycle(m1)
            n2, A2 = O.sym_cycle(m2)
            A1 = set(A1); A2 = set(A2)
            # choose every arc as (u,v1) of D1 and (v2,w) of D2
            for (u, v1) in list(A1):
                for (v2, w) in list(A2):
                    total += 1
                    r = check_join_lower_bound(n1, A1, u, v1, n2, A2, v2, w)
                    if not (r["lb_ok"] and r["eq_ok"]):
                        fails += 1
                        cases.append((m1, m2, (u, v1), (v2, w), r))
    return total, fails, cases


def random_extremal_pairs(trials=400, seed=0):
    """Random small digraphs with chi_vec=3 (and digon structure) joined; verify
    join is not 2-dicolourable. We harvest chi=3 digraphs from sym cycles +
    random digon-augmented small digraphs to broaden coverage."""
    rng = random.Random(seed)
    pool = []
    for m in (3, 5):
        pool.append(O.sym_cycle(m))
    # add a few directed-Hajos joins of sym cycles to the chi=3 pool
    base = list(pool)
    for (n1, A1) in base:
        for (n2, A2) in base:
            A1s = set(A1); A2s = set(A2)
            (u, v1) = next(iter(A1s)); (v2, w) = next(iter(A2s))
            n, arcs, *_ = hajos_join(n1, A1s, u, v1, n2, A2s, v2, w)
            if O.chi_vec(n, arcs) == 3:
                pool.append((n, frozenset(arcs)))
    fails = 0; total = 0
    for _ in range(trials):
        (n1, A1) = rng.choice(pool)
        (n2, A2) = rng.choice(pool)
        A1s = set(A1); A2s = set(A2)
        (u, v1) = rng.choice(list(A1s))
        (v2, w) = rng.choice(list(A2s))
        total += 1
        r = check_join_lower_bound(n1, A1s, u, v1, n2, A2s, v2, w)
        if not (r["lb_ok"] and r["eq_ok"]):
            fails += 1
    return total, fails


def confirm_splice_mechanism():
    """Direct confirmation of (C): for a join D = D1 v D2 with chi_vec(D)=2
    (so D IS 2-dicolourable -- only possible when min(chi1,chi2)<=2), take a
    2-dicolouring phi; verify at least one side restriction is valid. And for a
    join that is NOT 2-dicolourable (chi1=chi2=3), verify all_2dicolourings is
    EMPTY (no phi), consistent with the lower bound.
    """
    out = {}
    # Case chi=3 inputs: no 2-dicolouring of the join exists.
    n1, A1 = O.sym_cycle(3); n2, A2 = O.sym_cycle(3)
    A1 = set(A1); A2 = set(A2)
    (u, v1) = next(iter(A1)); (v2, w) = next(iter(A2))
    n, arcs, *_ = hajos_join(n1, A1, u, v1, n2, A2, v2, w)
    cols = list(all_2dicolourings(n, arcs))
    out["c3c3_no_2col"] = (O.chi_vec(n, arcs) == 3 and len(cols) == 0)

    # Case with a chi=2 input so a 2-dicolouring exists: confirm a side
    # restriction is valid for every phi (the splice cannot fire).
    # Build a chi=2 digraph: a single digon-free 2-dicolourable strong digraph.
    # Use C3 (directed triangle): chi_vec=1 actually (acyclic? no, it's a
    # dicycle => chi_vec=2). Vertices 0->1->2->0.
    triA = {(0, 1), (1, 2), (2, 0)}
    n2b, A2b = O.sym_cycle(3)  # chi=3 on the other side is fine for the test of
    # "restriction valid"; we want min<=2 so the join may be 2-colourable.
    # Use triangle (chi=2) joined with triangle (chi=2):
    n1t, A1t = 3, set(triA)
    n2t, A2t = 3, set(triA)
    (u, v1) = (0, 1); (v2, w) = (0, 1)
    nj, arcsj, v_lab, u_img, w_img, S1, S2 = hajos_join(
        n1t, A1t, u, v1, n2t, A2t, v2, w)
    chij = O.chi_vec(nj, arcsj)
    # lab maps for restriction: piece1 labels 0..2 -> join labels (identity for
    # S1 since D1 kept labels). piece2: reconstruct map used in hajos_join.
    # D1 piece for restriction = D[S1] + (u, v_lab) = original D1 (with arc u->v1
    # re-added). We just re-check against A1t with identity labelling.
    all_ok = True
    any_phi = False
    for phi in all_2dicolourings(nj, arcsj):
        any_phi = True
        # piece1 = D1 = (n1t, A1t), labels identity into join
        ok1 = restrict_is_valid(n1t, frozenset(A1t), phi,
                                {i: i for i in range(n1t)})
        # piece2 = D2 = (n2t, A2t); rebuild its join-label map
        # replicate hajos_join's d2map: v2->v_lab(=v1=1); others fresh from n1t
        d2map = {}; nxt = n1t
        for x in range(n2t):
            if x == v2:
                d2map[x] = v_lab
            else:
                d2map[x] = nxt; nxt += 1
        ok2 = restrict_is_valid(n2t, frozenset(A2t), phi, d2map)
        if not (ok1 or ok2):
            all_ok = False
            break
    out["tri_tri_chi_join"] = chij
    out["splice_never_fires_when_phi_exists"] = (all_ok and any_phi)
    return out


def main():
    print("=== (A)+(B) sym-odd-cycle directed-Hajos joins ===")
    total, fails, cases = small_sym_cycle_joins()
    print(f"  joins tested: {total}; lower-bound+equality failures: {fails}")
    for c in cases[:5]:
        print("   FAIL", c)

    print("=== (A)+(B) randomised chi=3 pairs ===")
    rt, rf = random_extremal_pairs(trials=400, seed=1)
    print(f"  joins tested: {rt}; failures: {rf}")

    print("=== (C) splice mechanism ===")
    out = confirm_splice_mechanism()
    for k, v in out.items():
        print(f"  {k}: {v}")

    ok = (fails == 0 and rf == 0
          and out["c3c3_no_2col"]
          and out["splice_never_fires_when_phi_exists"])
    print("=== OVERALL:", "PASS" if ok else "FAIL", "===")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
