#!/usr/bin/env python3
"""
ADVERSARIAL verification of proof_condL_hajos_lower_bound.md.

Tries to BREAK Propositions 3.1 (lower bound), 4.1 (gluing), 4.2 (criticality
descent) over a BROAD class of Hajos joins of small ARBITRARY digraphs (not just
symmetric odd cycles). A single failing instance kills a step.

Reuses h2_oracle.py SOUND primitives (chi_vec, _has_dicycle_in_subset).
"""
import sys, os, itertools, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import h2_oracle as O


def chi(n, arcs):
    return O.chi_vec(n, frozenset(arcs))


def hajos_join(n1, A1, u, v1, n2, A2, v2, w):
    """Def 1.5 join. Returns n, arcs, v, u_img, w_img, S1, S2, map1, map2.
    map_i: piece_label -> join_label (so factor D_i = D[S_i]+interface can be
    reconstructed and the restriction of a join-colouring read off)."""
    v_lab = v1
    d2map = {}
    nxt = n1
    for x in range(n2):
        if x == v2:
            d2map[x] = v_lab
        else:
            d2map[x] = nxt; nxt += 1
    n = nxt
    arcs = set()
    for (a, b) in A1:
        if (a, b) == (u, v1):
            continue
        arcs.add((a, b))
    for (a, b) in A2:
        if (a, b) == (v2, w):
            continue
        arcs.add((d2map[a], d2map[b]))
    u_img = u
    w_img = d2map[w]
    arcs.add((u_img, w_img))
    if (u_img, w_img) in (set((a, b) for (a, b) in A1) | set()):
        pass
    S1 = set(range(n1))
    S2 = set(d2map[x] for x in range(n2))
    map1 = {i: i for i in range(n1)}      # D1 labels are identity into join
    map2 = dict(d2map)                     # D2 labels -> join labels
    return n, frozenset(arcs), v_lab, u_img, w_img, S1, S2, map1, map2


def all_digraphs(n, max_extra_arcs=None):
    """Yield strong, loopless digraphs on n vertices that we use as factors.
    To keep it tractable, we enumerate over subsets of possible arcs but only
    KEEP digraphs that are weakly connected and have an arc to use as interface.
    For n<=4 this is feasible."""
    verts = list(range(n))
    pairs = [(i, j) for i in verts for j in verts if i != j]
    # cap arc count
    for r in range(n, min(len(pairs), (max_extra_arcs or len(pairs))) + 1):
        for combo in itertools.combinations(pairs, r):
            yield frozenset(combo)


def is_weakly_connected(n, arcs):
    adj = O.underlying_adj(n, arcs)
    seen = {0}; st = [0]
    while st:
        x = st.pop()
        for y in adj[x]:
            if y not in seen:
                seen.add(y); st.append(y)
    return len(seen) == n


def brute_lower_bound(maxn1=4, maxn2=4, limit=200000, seed=0):
    """Sample arbitrary join factors, check chi(join) >= min(chi1,chi2)."""
    rng = random.Random(seed)
    fails = []
    total = 0
    # pool of small digraphs (random) with at least one arc
    pool = []
    for n in (2, 3, 4):
        verts = list(range(n))
        pairs = [(i, j) for i in verts for j in verts if i != j]
        for _ in range(120):
            k = rng.randint(1, len(pairs))
            A = frozenset(rng.sample(pairs, k))
            if A and is_weakly_connected(n, A):
                pool.append((n, A))
    for _ in range(limit):
        (n1, A1) = rng.choice(pool)
        (n2, A2) = rng.choice(pool)
        A1 = set(A1); A2 = set(A2)
        if not A1 or not A2:
            continue
        (u, v1) = rng.choice(list(A1))
        (v2, w) = rng.choice(list(A2))
        if u == v1 or v2 == w:
            continue
        total += 1
        c1 = chi(n1, A1); c2 = chi(n2, A2)
        n, arcs, *_ = hajos_join(n1, A1, u, v1, n2, A2, v2, w)
        cj = chi(n, arcs)
        if cj < min(c1, c2):
            fails.append(((n1, sorted(A1), u, v1), (n2, sorted(A2), v2, w),
                          c1, c2, cj))
            if len(fails) >= 5:
                break
    return total, fails


def brute_gluing(limit=80000, seed=1):
    """Prop 4.1: chi1==chi2==k>=2 => chi(join)==k. Check equality exactly."""
    rng = random.Random(seed)
    pool = []
    for n in (2, 3, 4):
        verts = list(range(n))
        pairs = [(i, j) for i in verts for j in verts if i != j]
        for _ in range(200):
            k = rng.randint(1, len(pairs))
            A = frozenset(rng.sample(pairs, k))
            if A and is_weakly_connected(n, A):
                pool.append((n, A))
    fails = []
    total = 0
    for _ in range(limit):
        (n1, A1) = rng.choice(pool); (n2, A2) = rng.choice(pool)
        A1 = set(A1); A2 = set(A2)
        c1 = chi(n1, A1); c2 = chi(n2, A2)
        if not (c1 == c2 and c1 >= 2):
            continue
        (u, v1) = rng.choice(list(A1)); (v2, w) = rng.choice(list(A2))
        total += 1
        n, arcs, *_ = hajos_join(n1, A1, u, v1, n2, A2, v2, w)
        cj = chi(n, arcs)
        if cj != c1:
            fails.append((c1, cj, (n1, sorted(A1), u, v1),
                          (n2, sorted(A2), v2, w)))
            if len(fails) >= 5:
                break
    return total, fails


def is_dicritical(n, arcs, m):
    """True iff chi==m and every arc-deletion drops chi below m
    AND every vertex-deletion drops chi below m."""
    arcs = set(arcs)
    if chi(n, arcs) != m:
        return False
    for a in list(arcs):
        if chi(n, arcs - {a}) >= m:
            return False
    return True


def brute_crit_descent(limit=4000, seed=2):
    """Prop 4.2: if join D is m-dicritical (arc-criticality) then both factors
    are m-dicritical. We construct joins, test whether D is m-dicritical, and if
    so verify both factors are too. Also test the CONVERSE (4.2's converse / BJSS
    2(c)): both factors m-dicritical => D m-dicritical."""
    rng = random.Random(seed)
    # build a pool that includes chi=2 and chi=3 critical-ish digraphs
    pool = []
    # directed cycles C_k are 2-dicritical (chi=2)
    for k in (2, 3, 4, 5):
        if k == 2:
            A = frozenset({(0, 1), (1, 0)})  # digon, chi=2, 2-dicritical
            pool.append((2, A))
        else:
            A = frozenset((i, (i + 1) % k) for i in range(k))
            pool.append((k, A))
    # symmetric odd cycles are 3-dicritical
    for m in (3, 5):
        pool.append(O.sym_cycle(m))
    fwd_fail = []   # both crit but join not crit
    desc_fail = []  # join crit but a factor not crit
    total_fwd = total_desc = 0
    arcs_pool = []
    for (n, A) in pool:
        arcs_pool.append((n, set(A)))
    for _ in range(limit):
        (n1, A1) = rng.choice(arcs_pool); (n2, A2) = rng.choice(arcs_pool)
        A1 = set(A1); A2 = set(A2)
        (u, v1) = rng.choice(list(A1)); (v2, w) = rng.choice(list(A2))
        n, arcs, *_ = hajos_join(n1, A1, u, v1, n2, A2, v2, w)
        c1 = chi(n1, A1); c2 = chi(n2, A2)
        cj = chi(n, arcs)
        # CONVERSE (BJSS 2c): both factors m-dicritical => D m-dicritical
        if c1 == c2 and c1 >= 2:
            m = c1
            if is_dicritical(n1, A1, m) and is_dicritical(n2, A2, m):
                total_fwd += 1
                if not is_dicritical(n, arcs, m):
                    fwd_fail.append((m, (n1, sorted(A1)), (n2, sorted(A2)),
                                     (n, sorted(arcs))))
        # DESCENT (BJSS 2d): D m-dicritical => both factors m-dicritical
        if cj >= 2 and is_dicritical(n, arcs, cj):
            m = cj
            total_desc += 1
            f1 = is_dicritical(n1, A1, m)
            f2 = is_dicritical(n2, A2, m)
            if not (f1 and f2):
                desc_fail.append((m, f1, f2, (n1, sorted(A1), u, v1),
                                  (n2, sorted(A2), v2, w)))
    return (total_fwd, fwd_fail), (total_desc, desc_fail)


def main():
    print("=== Prop 3.1 lower bound, ARBITRARY small factors ===")
    t, f = brute_lower_bound(limit=60000, seed=7)
    print(f"  joins: {t}; lower-bound FAILURES: {len(f)}")
    for x in f:
        print("   FAIL", x)

    print("=== Prop 4.1 gluing equality, ARBITRARY factors ===")
    t, f = brute_gluing(limit=40000, seed=11)
    print(f"  joins (chi1==chi2>=2): {t}; equality FAILURES: {len(f)}")
    for x in f:
        print("   FAIL", x)

    print("=== Prop 4.2 criticality (converse 2c & descent 2d) ===")
    (tf, ff), (td, df) = brute_crit_descent(limit=6000, seed=13)
    print(f"  2(c) converse  both-crit=>D-crit: tested {tf}; FAILURES {len(ff)}")
    for x in ff:
        print("   FAIL-2c", x)
    print(f"  2(d) descent   D-crit=>both-crit: tested {td}; FAILURES {len(df)}")
    for x in df:
        print("   FAIL-2d", x)

    ok = True
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
