"""Red-team the SPECIFIC claims of proof S3.3 III for the actual 6 'square' quads.

The 6 squares = the 6 minimal infeasible quads that are NOT the 4 outer-source (II) quads.
For EACH square, and each n, we:
  (a) confirm infeasibility (no backedge clique, one rep per cell);
  (b) for the BASE square, verify the proof's branch reduction: in the all-distinct-block
      branch the conditions force {a_r in H, a_s in L} to be common in-neighbours of
      {a_p in H, a_q in L}, one in each band -- and check H17 (common in-nbhd single band).
"""
import sys, itertools

def ac_gen(n):
    m = (n - 1) // 2
    return set(range(1, m)) | {m + 1}

def c(t, m):
    if t == 0: return 3
    if 1 <= t <= m: return 2
    return 1

def cell(a, b, m): return (c(b, m), c(a, m))
def key(a, b, m): return (c(b, m), c(a, m), a, b)

def beats_T(p, q, n, g):
    a, b = p; ap, bp = q
    if a != ap: return ((ap - a) % n) in g
    return ((bp - b) % n) in g

def cell_vertices(cl, n, m):
    return [(a, b) for a in range(n) for b in range(n)
            if (a, b) != (0, 0) and cell(a, b, m) == cl]

def is_bclique(reps, n, g, m):
    o = sorted(reps, key=lambda v: key(v[0], v[1], m))
    for i in range(len(o)):
        for j in range(i + 1, len(o)):
            if not beats_T(o[j], o[i], n, g): return False
    return True

def feasible(cells, n, m, g):
    pools = [cell_vertices(cl, n, m) for cl in cells]
    for combo in itertools.product(*pools):
        if is_bclique(list(combo), n, g, m): return list(combo)
    return None

SQUARES = [
    {(1,1),(1,2),(2,1),(2,2)},   # base
    {(1,1),(1,2),(2,1),(3,2)},
    {(1,1),(1,2),(3,1),(3,2)},
    {(1,1),(2,2),(3,1),(3,2)},
    {(1,2),(2,1),(2,2),(3,1)},
    {(2,1),(2,2),(3,1),(3,2)},
]

def Nminus(v, n, g):
    """in-neighbours of v in AC_n: {u : u beats v} = {u : (v-u) mod n in g}."""
    return set(u for u in range(n) if ((v - u) % n) in g)

def check_H17(n):
    """For x in H=[m+1,2m], y in L=[1,m]: is N^-(x) cap N^-(y) within a single band?"""
    m = (n - 1) // 2
    g = ac_gen(n)
    H = range(m + 1, 2 * m + 1)
    L = range(1, m + 1)
    bad = []
    for x in H:
        for y in L:
            common = Nminus(x, n, g) & Nminus(y, n, g)
            has_H = any((m + 1 <= z <= 2 * m) for z in common)
            has_L = any((1 <= z <= m) for z in common)
            if has_H and has_L:
                bad.append((x, y, sorted(common)))
    return bad

def check_base_branch(n):
    """Enumerate ALL rep choices for the base square and, for those satisfying the
    pure-outer + all-distinct-block branch conditions, verify a_r in H and a_s in L
    are BOTH common in-neighbours (in AC_n) of {a_p in H, a_q in L}. Then any feasible
    such config would violate H17. We confirm NO feasible config exists, and that the
    reduction (forced common-in-nbhd structure) is exactly as the proof claims."""
    m = (n - 1) // 2
    g = ac_gen(n)
    H = set(range(m + 1, 2 * m + 1)); L = set(range(1, m + 1))
    # reps: p in (1,1)->a in H, q in (1,2)->a in L, r in (2,1)->a in H, s in (2,2)->a in L
    # cell (1,1): c(b)=1 (b in H), c(a)=1 (a in H)
    # cell (1,2): c(b)=1 (b in H), c(a)=2 (a in L)
    # cell (2,1): c(b)=2 (b in L), c(a)=1 (a in H)
    # cell (2,2): c(b)=2 (b in L), c(a)=2 (a in L)
    P = cell_vertices((1,1), n, m); Q = cell_vertices((1,2), n, m)
    R = cell_vertices((2,1), n, m); S = cell_vertices((2,2), n, m)
    feasible_found = []
    branch_violations = []
    n_distinct_branch = 0
    for p in P:
        for q in Q:
            for r in R:
                for s in S:
                    if not is_bclique([p,q,r,s], n, g, m):
                        continue
                    feasible_found.append((p,q,r,s))
    # Now independently: in the all-distinct-block branch (a_r!=a_p, a_s!=a_q),
    # the proof claims the 6 conditions force a_r,a_s to be common in-nbrs of {a_p,a_q}.
    # We verify the LOGICAL reduction directly on outer coordinates:
    #   key order is p<q<r<s (since cells ordered (1,1)<(1,2)<(2,1)<(2,2)).
    #   beats: q>p, r>q, s>r, s>p, r>p, s>q  (higher beats lower).
    # All are pure-outer EXCEPT possibly r>p (both c(a)=1 => a in H, same outer band)
    # and s>q (both c(a)=2 => a in L). In all-distinct-block branch those are outer too.
    ap_set = sorted(H); aq_set = sorted(L)
    for ap in H:
        for aq in L:
            for ar in H:
                for as_ in L:
                    if ar == ap or as_ == aq:
                        continue  # all-distinct-block branch only
                    n_distinct_branch += 1
                    # the six OUTER beat conditions (rep beats rep => (a_lo - a_hi) in g):
                    # q>p: (ap-aq) in g ; r>q: (aq-ar) in g ; s>r: (ar-as_) in g
                    # s>p: (ap-as_) in g ; r>p: (ap-ar) in g ; s>q: (aq-as_) in g
                    conds = [
                        ((ap-aq)%n) in g,
                        ((aq-ar)%n) in g,
                        ((ar-as_)%n) in g,
                        ((ap-as_)%n) in g,
                        ((ap-ar)%n) in g,
                        ((aq-as_)%n) in g,
                    ]
                    if all(conds):
                        # The proof's claim: ar,as_ are common in-nbrs of {ap,aq}.
                        # r>p means r beats p: ar beats ap => ap in N^-... wait orientation:
                        # "higher beats lower": r is higher, p lower, r beats p.
                        # r beats p in AC_n: (a_p - a_r) in g  i.e. ap in N^+(ar)?
                        # in-nbr of ap = {u: u beats ap} = {u:(ap-u) in g}. r beats p => ar in N^-(ap).
                        # r>q: r beats q => ar in N^-(aq). So ar common in-nbr of {ap,aq}. (r>p,r>q)
                        # s>p: s beats p => as_ in N^-(ap). s>q: s beats q => as_ in N^-(aq).
                        in_p = Nminus(ap, n, g); in_q = Nminus(aq, n, g)
                        claim_ok = (ar in in_p and ar in in_q and as_ in in_p and as_ in in_q)
                        if not claim_ok:
                            branch_violations.append(("REDUCTION-FAIL", ap,aq,ar,as_))
                        # ar in H, as_ in L both in common in-nbhd of {ap in H, aq in L}
                        # => violates H17. So this should be IMPOSSIBLE.
    return feasible_found, branch_violations, n_distinct_branch

def main():
    ns = [int(x) for x in sys.argv[1:]] or [7, 9, 11, 13, 15]
    for n in ns:
        m = (n - 1) // 2; g = ac_gen(n)
        print(f"\n===== n={n} =====")
        for sq in SQUARES:
            w = feasible(sq, n, m, g)
            print(f"  square {sorted(sq)}: {'FEASIBLE '+str(w) if w else 'infeasible'}")
        bad17 = check_H17(n)
        print(f"  H17 violations (common in-nbhd spanning both bands): {len(bad17)}"
              + (f"  e.g. {bad17[0]}" if bad17 else ""))
        feas, bviol, ndist = check_base_branch(n)
        print(f"  BASE square: feasible rep configs = {len(feas)}; "
              f"all-distinct-block outer-configs satisfying all 6 conds = "
              f"{'see below' if bviol else 0 if not feas else '?'}")
        # count how many all-distinct outer configs satisfy all 6 conditions:
        # recompute count
        cnt = 0; examples=[]
        H = set(range(m+1,2*m+1)); L=set(range(1,m+1))
        for ap in H:
            for aq in L:
                for ar in H:
                    for as_ in L:
                        if ar==ap or as_==aq: continue
                        if (((ap-aq)%n in g) and ((aq-ar)%n in g) and ((ar-as_)%n in g)
                            and ((ap-as_)%n in g) and ((ap-ar)%n in g) and ((aq-as_)%n in g)):
                            cnt+=1; examples.append((ap,aq,ar,as_))
        print(f"    all-distinct-block configs satisfying all 6 outer beat-conds: {cnt}")
        print(f"    reduction-claim violations (conds hold but not common-in-nbhd): {len(bviol)}")
        if examples:
            print(f"    EXAMPLE feasible outer config: {examples[0]} -> would be a counterexample!")

if __name__ == "__main__":
    main()
