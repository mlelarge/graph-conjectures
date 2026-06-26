"""Ground the k=4 dom-route proposal.

Steps:
(1) dom/identity-omega sweep over ALL tournament-circulants Cay(Z/n,g),
    capture (dom>=4 AND id-omega==4) witnesses; save g-lists.
(2) three-fold covering deficiency for each witness.
(3) K4-free SAT (omega<=3) generalized encoding + validation vs core.omega_vec_bb
    on all n<=7 random tournaments (0 mismatches required).
    Then apply to smallest witnesses for a SOUND omega_vec>=4 lower bound.
(4) per-vertex deletion K4-free check -> 4-omega_vec-criticality test.
"""
import os
import sys, time, json, itertools, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import core
from pysat.solvers import Cadical153

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')


def dom_circulant(n, g, ub=5):
    N0 = frozenset({0} | set(d % n for d in g))
    full = set(range(n))
    closed = [set((d + v) % n for d in N0) for v in range(n)]
    for s in range(1, ub + 1):
        for X in itertools.combinations(range(n), s):
            cov = set()
            for x in X:
                cov |= closed[x]
            if cov == full:
                return s
    return ub + 1


def identity_omega(n, g):
    Db = set((n - d) % n for d in g); Db.discard(0)
    adj = [[False] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            if (j - i) in Db:
                adj[i][j] = adj[j][i] = True
    best = 0
    def ex(cl, cand):
        nonlocal best
        if len(cl) > best: best = len(cl)
        if len(cl) + len(cand) <= best: return
        for idx in range(len(cand)):
            v = cand[idx]
            ex(cl + [v], [u for u in cand[idx + 1:] if adj[v][u]])
    ex([], list(range(n)))
    return best


def threefold_deficiency(n, g):
    """min over distinct a<b in {1..n-1} of |Z/n \ (N0 u N0+a u N0+b)|."""
    N0 = set([0]) | set(d % n for d in g)
    full = set(range(n))
    base = N0
    shifts = [set((x + a) % n for x in base) for a in range(n)]
    best = n
    for a in range(1, n):
        for b in range(a + 1, n):
            cov = base | shifts[a] | shifts[b]
            d = len(full - cov)
            if d < best:
                best = d
    return best


def circ_arcs(n, g):
    return [(i, (i + d) % n) for i in range(n) for d in g]


# ----- K4-free SAT encoding (omega<=3) -----
def build_cnf_k4(n, arcs):
    """phi SAT  iff some total order's backedge graph is K4-free (omega<=3).
    A 4-clique in backedge graph = 4 vertices that pairwise have a backward arc
    under the order; that forces them to be a transitive tournament placed in
    the fully-REVERSED (decreasing-by-dominance) order a<b<c<d with d->a,d->b,
    d->c,c->a,c->b,b->a.  Forbid that single arrangement per transitive 4-set.
    """
    beats = core.beats_matrix(n, arcs)
    idx = {}
    nv = 0
    def lit(u, v):
        nonlocal nv
        if (u, v) in idx: return idx[(u, v)]
        if (v, u) in idx: return -idx[(v, u)]
        nv += 1; idx[(u, v)] = nv; return nv
    clauses = []
    # transitivity of the order
    for u in range(n):
        for v in range(n):
            if v == u: continue
            for w in range(n):
                if w == u or w == v: continue
                clauses.append([-lit(u, v), -lit(v, w), lit(u, w)])
    # forbid each transitive 4-tournament placed in reversed order
    n_forb = 0
    rng = range(n)
    for quad in itertools.combinations(rng, 4):
        # find an ordering (s0,s1,s2,s3) with s0->s1->s2->s3 transitive chain
        # i.e. a transitive tournament: source beats all later, etc.
        for perm in itertools.permutations(quad):
            ok = True
            for i in range(4):
                for j in range(i + 1, 4):
                    if not beats[perm[i]][perm[j]]:
                        ok = False; break
                if not ok: break
            if ok:
                # perm = (top, .., sink) source beats all.  backedge 4-clique
                # appears when order places sink<...<top, i.e. perm[3]<perm[2]<perm[1]<perm[0]
                a, b, c, d = perm[3], perm[2], perm[1], perm[0]  # a<b<c<d
                # forbid a<b & b<c & c<d  => clause (b<a | c<b | d<c)
                clauses.append([lit(b, a), lit(c, b), lit(d, c)])
                n_forb += 1
                break  # unique transitive ordering per quad
    return clauses, nv, n_forb


def sat_omega_le3(n, arcs):
    """True iff phi SAT iff omega_vec<=3."""
    clauses, nv, nf = build_cnf_k4(n, arcs)
    with Cadical153(bootstrap_with=clauses) as m:
        sat = m.solve()
    return sat, nf


def validate_encoding():
    """validate K4-free SAT vs core.omega_vec_bb on random n<=7 tournaments."""
    random.seed(12345)
    mism = 0; checked = 0
    details = []
    for n in range(4, 8):
        ntests = 300 if n <= 6 else 200
        for _ in range(ntests):
            # random tournament
            arcs = []
            for i in range(n):
                for j in range(i + 1, n):
                    if random.random() < 0.5: arcs.append((i, j))
                    else: arcs.append((j, i))
            ov = core.omega_vec_bb(n, arcs, ub=n)
            sat, _ = sat_omega_le3(n, arcs)
            sat_le3 = sat
            oracle_le3 = (ov <= 3)
            checked += 1
            if sat_le3 != oracle_le3:
                mism += 1
                details.append({"n": n, "arcs": arcs, "ov": ov, "sat_le3": sat_le3})
    return checked, mism, details


def main():
    out = {}
    # ---- Step 1: sweep witnesses ----
    print("=== Step 1: dom>=4 & id-omega==4 sweep ===", flush=True)
    witnesses = {}
    sweep_summary = []
    for n in [19, 21, 23, 25, 27]:
        m = (n - 1) // 2
        pairs = [(d, n - d) for d in range(1, m + 1)]
        cnt_dom4 = 0
        wlist = []
        min_idom = None
        sweep_t0 = time.time()
        for choice in itertools.product([0, 1], repeat=m):
            g = set(pairs[i][choice[i]] for i in range(m))
            if dom_circulant(n, g, ub=4) >= 4:
                cnt_dom4 += 1
                io = identity_omega(n, g)
                if min_idom is None or io < min_idom: min_idom = io
                if io == 4:
                    wlist.append(sorted(g))
        witnesses[n] = wlist
        sweep_summary.append({"n": n, "n_dom_ge4": cnt_dom4,
                              "min_id_omega_among_dom4": min_idom,
                              "n_witnesses_dom4_idom4": len(wlist)})
        print(f"n={n}: #dom>=4={cnt_dom4}, min_id_omega={min_idom}, "
              f"#(dom>=4 & id-omega==4)={len(wlist)} ({time.time()-sweep_t0:.1f}s)", flush=True)
    out["sweep_summary"] = sweep_summary

    # ---- Step 2: three-fold covering deficiency for witnesses ----
    print("\n=== Step 2: three-fold covering deficiency ===", flush=True)
    defs = {}
    for n in [19, 25, 27]:
        wl = witnesses.get(n, [])
        if not wl:
            print(f"n={n}: no witnesses", flush=True); continue
        # min interval-defect among witnesses
        rows = []
        for g in wl[:50]:
            d3 = threefold_deficiency(n, g)
            rows.append((d3, g))
        rows.sort()
        defs[n] = {"min_3fold_deficiency": rows[0][0],
                   "cleanest_g": rows[0][1],
                   "n_witnesses": len(wl)}
        print(f"n={n}: min 3-fold deficiency = {rows[0][0]} (g={rows[0][1]}), "
              f"{len(wl)} witnesses", flush=True)
    out["threefold_deficiency"] = defs

    # ---- Step 3: validate K4-free SAT encoding ----
    print("\n=== Step 3: validate K4-free SAT vs core.omega_vec_bb (n<=7) ===", flush=True)
    t0 = time.time()
    checked, mism, details = validate_encoding()
    print(f"checked={checked} random tournaments n in 4..7, mismatches={mism} "
          f"({time.time()-t0:.1f}s)", flush=True)
    out["encoding_validation"] = {"checked": checked, "mismatches": mism,
                                  "details": details}
    if mism > 0:
        print("ENCODING INVALID -- abort lower-bound use", flush=True)
        with open(f"{ROOT}/data/k4_ground.json", "w") as f:
            json.dump(out, f, indent=2)
        print(json.dumps(out)); return

    # ---- Step 4: exact omega_vec>=4 + criticality on smallest witnesses ----
    print("\n=== Step 4: K4-free SAT lower bound + criticality on witnesses ===", flush=True)
    crit_results = []
    for n in [19, 25]:
        wl = witnesses.get(n, [])
        if not wl: continue
        # pick the cleanest (smallest 3-fold deficiency) witness
        rows = sorted((threefold_deficiency(n, g), g) for g in wl[:50])
        g = rows[0][1]
        arcs = circ_arcs(n, g)
        t0 = time.time()
        sat, nf = sat_omega_le3(n, arcs)
        dt = time.time() - t0
        # SAT  => omega_vec<=3 (lower-bound route FAILS: not >=4)
        # UNSAT => omega_vec>=4
        lower_ge4 = (not sat)
        # upper bound: identity order omega
        idom = identity_omega(n, g)
        rec = {"n": n, "g": g, "n_forbidden_quads": nf,
               "K4free_SAT": sat, "omega_vec_ge4": lower_ge4,
               "identity_omega(upper)": idom, "sat_time_s": round(dt, 3)}
        print(f"n={n} g={g}: K4free_SAT={sat} => omega_vec>=4? {lower_ge4}; "
              f"id-omega(upper)={idom} ({dt:.3f}s)", flush=True)
        if lower_ge4 and idom == 4:
            # exact omega_vec=4; test 4-criticality via per-vertex deletion
            # (vertex-transitive: all deletions isomorphic, check vertex 0)
            keep = [v for v in range(n) if v != 0]
            sub_n, sub_arcs = core.subtournament(n, arcs, keep)
            # deletion omega_vec: is it <=3 (yes by sub) and is it ==3?
            # check K4-free SAT on deletion (should be SAT => <=3) and that it's
            # not <=2 (omega_vec deletion ==3, not lower) via triangle-free check
            sat_del, _ = sat_omega_le3(sub_n, sub_arcs)
            del_le3 = sat_del
            # is deletion omega_vec >=3? need exact; use omega_vec_bb if feasible
            del_ov = None
            if sub_n <= 20:
                # symmetry not available for deletion; bb may be slow -- bound time
                try:
                    del_ov = core.omega_vec_bb(sub_n, sub_arcs, ub=4)
                except Exception as e:
                    del_ov = f"err:{e}"
            rec["deletion_K4free_SAT(le3)"] = sat_del
            rec["deletion_omega_vec_bb"] = del_ov
            rec["is_4_critical"] = (del_le3 and del_ov == 3)
            print(f"   deletion: K4free_SAT={sat_del} (le3), omega_vec_bb={del_ov}, "
                  f"4-critical(vt)={rec.get('is_4_critical')}", flush=True)
        crit_results.append(rec)
    out["criticality"] = crit_results

    with open(f"{ROOT}/data/k4_ground.json", "w") as f:
        json.dump(out, f, indent=2)
    print("\nSAVED data/k4_ground.json", flush=True)
    print(json.dumps(out))


if __name__ == "__main__":
    main()
