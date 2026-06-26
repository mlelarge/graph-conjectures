"""Search for an explicit 4-omega_vec-critical circulant tournament (next_action, D10).

omega_vec(T) <= K-1  IFF  some total order's backedge graph is K_K-free.
A K-clique on order-positions v_1<...<v_K needs every later vertex to beat every
earlier one: v_j -> v_i for i<j.  So a K-clique <=> a TRANSITIVE K-subtournament S
placed in the EXACT REVERSE of its acyclic (domination) order.

Generalized betweenness CNF (extends sat_betweenness_step1.py from K=3 to any K):
 vars p_{u,v} = (u<v), p_{v,u} = -p_{u,v}.
 transitivity 3-clauses: (u<v)&(v<w)->(u<w).
 FORBID each K-clique: for every transitive K-subset with acyclic order
   s_1->s_2->...->s_K (s_a beats s_b for a<b), forbid the placement
   s_K < s_{K-1} < ... < s_1, i.e. clause OR_{a<b}(s_a < s_b)  [negation of all
   the consecutive-reversed atoms; transitivity makes the consecutive atoms
   s_{i+1}<s_i imply the full reversed chain].
 We encode it minimally: forbidding the chain s_K<...<s_1 it suffices to require
   NOT(s_K<s_{K-1} AND s_{K-1}<s_{K-2} AND ... AND s_2<s_1)
   = clause [ (s_{K-1}<s_K), (s_{K-2}<s_{K-1}), ..., (s_1<s_2) ]  (K-1 literals).
 (transitivity then propagates: if all K-1 consecutive reversed atoms held, the
  full reverse order holds, giving the forbidden clique; blocking the conjunction
  of consecutive atoms blocks exactly that one linear arrangement.)

SAT  <=> some order is K_K-free <=> omega_vec <= K-1.
UNSAT <=> every order has a K_K   <=> omega_vec >= K.

VALIDATED below against the exact core.omega_vec / omega_vec_bb on small circulants
(both directions) before being trusted for K=4.
"""
import sys, os, json, time, itertools
sys.path.insert(0, os.path.dirname(__file__))
import core
from pysat.solvers import Cadical153
from pysat.formula import CNF


def circ_arcs(p, g):
    return [(i, (i + d) % p) for i in range(p) for d in g]


def transitive_ksubsets_order(n, beats, K):
    """Yield, for each K-subset that induces a TRANSITIVE tournament, its acyclic
    order (s_1,...,s_K) with s_a -> s_b for all a<b (s_1 = source, s_K = sink)."""
    for S in itertools.combinations(range(n), K):
        # score by out-degree within S; transitive iff scores are a permutation of 0..K-1
        outdeg = {}
        for x in S:
            outdeg[x] = sum(1 for y in S if y != x and beats[x][y])
        scores = sorted(outdeg.values())
        if scores != list(range(K)):
            # not transitive: within-S out-degrees of a transitive K-tournament
            # are exactly a permutation of {0,1,...,K-1}.
            continue
        # acyclic order: descending out-degree = s_1(source,outdeg K-1) ... s_K(sink,0)
        order = sorted(S, key=lambda x: -outdeg[x])
        # verify it is genuinely transitive (s_a beats s_b for a<b)
        ok = all(beats[order[a]][order[b]] for a in range(K) for b in range(a + 1, K))
        if ok:
            yield order


def build_cnf_no_kclique(n, arcs, K):
    """CNF that is SAT iff some total order's backedge graph is K_K-free."""
    beats = core.beats_matrix(n, arcs)
    idx = {}
    nv = 0
    def lit(u, v):
        nonlocal nv
        if (u, v) in idx:
            return idx[(u, v)]
        if (v, u) in idx:
            return -idx[(v, u)]
        nv += 1
        idx[(u, v)] = nv
        return nv
    cnf = CNF()
    # ensure all pair vars exist (so transitivity refs are consistent)
    for u in range(n):
        for v in range(u + 1, n):
            lit(u, v)
    # transitivity
    for u in range(n):
        for v in range(n):
            if v == u: continue
            for w in range(n):
                if w == u or w == v: continue
                cnf.append([-lit(u, v), -lit(v, w), lit(u, w)])
    nclq = 0
    for order in transitive_ksubsets_order(n, beats, K):
        # forbid the reverse placement s_K<...<s_1: block conjunction of consecutive
        # reversed atoms (s_{i+1}<s_i). clause = OR (s_i<s_{i+1}).
        clause = [lit(order[i], order[i + 1]) for i in range(K - 1)]
        cnf.append(clause)
        nclq += 1
    return cnf, nclq


def omega_vec_ge_K_via_sat(n, arcs, K):
    """True iff omega_vec(T) >= K (CNF UNSAT). Returns (ge_K, sat_time)."""
    cnf, nclq = build_cnf_no_kclique(n, arcs, K)
    t0 = time.time()
    with Cadical153(bootstrap_with=cnf.clauses) as m:
        sat = m.solve()
    dt = time.time() - t0
    # sat => exists K-clique-free order => omega_vec <= K-1 ; unsat => omega_vec >= K
    return (not sat), dt, nclq


def identity_order_clique(n, arcs):
    """omega of backedge graph under identity order 0<1<...<n-1 (cheap upper bound)."""
    return core.omega_of_order(n, arcs, list(range(n)))


def best_order_upper(n, arcs, tries):
    """Upper bound on omega_vec: min backedge-omega over identity + a few rotations."""
    import random
    best = identity_order_clique(n, arcs)
    rng = random.Random(12345)
    base = list(range(n))
    for _ in range(tries):
        o = base[:]
        rng.shuffle(o)
        w = core.omega_of_order(n, arcs, o)
        if w < best:
            best = w
    # also all cyclic rotations for circulants (cheap, structured)
    for r in range(n):
        o = [(i + r) % n for i in range(n)]
        w = core.omega_of_order(n, arcs, o)
        if w < best:
            best = w
    return best


def validate_sat_oracle():
    """Cross-check the K-clique SAT encoding vs exact core.omega_vec on small
    circulants (n<=9, both K=3 and K=4 thresholds)."""
    print("=== VALIDATION: SAT no-K-clique vs exact omega_vec ===", flush=True)
    cases = []
    # known: AC_7 ov=3, consec7 ov=2, QR7 ov=3
    cases.append(("AC7", 7, set(range(1, 3)) | {4}))         # {1,2,4}? ac_g(7)={1,2}|{4}
    cases.append(("consec7", 7, {1, 2, 3}))
    cases.append(("QR7", 7, {1, 2, 4}))
    # n=9 circulants: enumerate a few generator sets and compare both K=3,4
    cases.append(("c9_a", 9, {1, 2, 3, 4}))                  # consecutive => ov small
    cases.append(("c9_b", 9, {1, 2, 3, 5}))
    cases.append(("c9_c", 9, {1, 2, 4, 7}))
    cases.append(("Stilde3-like_no", 9, {1, 2, 3, 4}))
    allok = True
    recs = []
    for name, p, g in cases:
        # valid tournament generator? need g disjoint from -g, |g|=(p-1)/2
        negg = set((-d) % p for d in g)
        if g & negg or len(g) != (p - 1) // 2:
            print(f"  {name}: g not a tournament generator, skip")
            continue
        arcs = circ_arcs(p, g)
        ov = core.omega_vec(p, arcs)  # exact
        for K in (3, 4):
            ge, dt, ncl = omega_vec_ge_K_via_sat(p, arcs, K)
            truth = (ov >= K)
            ok = (ge == truth)
            allok = allok and ok
            recs.append({"name": name, "p": p, "g": sorted(g), "exact_omega_vec": ov,
                         "K": K, "sat_says_ge_K": ge, "truth_ge_K": truth, "agree": ok,
                         "nclauses_forbid": ncl, "sat_time_s": round(dt, 4)})
            print(f"  {name:14s} ov={ov} K={K} sat_ge={ge} truth={truth} "
                  f"{'OK' if ok else 'MISMATCH'} ({dt:.4f}s)", flush=True)
    print("VALIDATION ALL AGREE:", allok, flush=True)
    return allok, recs


def k4_identity_upper(p, g):
    """For circulant i->i+d (d in g): identity-order backedge clique upper bound."""
    arcs = circ_arcs(p, g)
    return identity_order_clique(p, arcs)


def main():
    out = {"validation": None, "search": [], "found": []}
    allok, vrecs = validate_sat_oracle()
    out["validation"] = {"all_agree": allok, "cases": vrecs}
    if not allok:
        print("!!! SAT oracle FAILED validation; aborting search.", flush=True)
        with open(os.path.join(os.path.dirname(__file__), "..", "data",
                  "search_4critical_circulant.json"), "w") as f:
            json.dump(out, f, indent=2)
        print(json.dumps(out))
        return

    # === SEARCH for 4-omega_vec-critical circulants ===
    # Strategy: for odd n, generator g with |g|=(n-1)/2, valid tournament gen.
    # Heuristic from the structural template: include a couple of LARGE generators
    # (backward diff in (m/2,2m]) to push identity-order clique to 4 but not 5.
    # We DON'T blindly enumerate all generators (2^m too big); we focus the search:
    #   - take a consecutive block {1..a} plus a few "large" generators chosen so
    #     g sqcup -g = {1..n-1}, then scan.
    # We just enumerate ALL valid generator sets for small odd n (n<=15) by choosing,
    # for each pair {d, n-d}, which side is in g (2^m sets, m=(n-1)/2), but PRUNE by
    # identity-order clique == 4 BEFORE any SAT/criticality work.

    import random
    rng = random.Random(2024)
    NS = [13, 15, 17, 19, 21]
    PER_N_CANDIDATE_CAP = 40000   # cap generator sets examined per n
    SAT_TIME_BUDGET = 0.0          # accumulated, just for reporting
    deadline = time.time() + 820   # hard wall (foreground budget)

    for n in NS:
        if time.time() > deadline:
            out["search"].append({"n": n, "status": "skipped_time"})
            print(f"n={n}: skipped (time)", flush=True)
            continue
        m = (n - 1) // 2
        pairs = [(d, n - d) for d in range(1, m + 1)]   # m pairs; choose one of each
        total = 1 << m
        examined = 0
        id4_count = 0
        ge4_count = 0
        crit_found = []
        # enumerate choices; if too many, sample
        choices_iter = range(total) if total <= PER_N_CANDIDATE_CAP else \
            (rng.randrange(total) for _ in range(PER_N_CANDIDATE_CAP))
        seen = set()
        for mask in choices_iter:
            if mask in seen:
                continue
            seen.add(mask)
            if time.time() > deadline:
                break
            examined += 1
            g = set()
            for bit, (d, nd) in enumerate(pairs):
                g.add(d if (mask >> bit) & 1 else nd)
            # quick identity-order clique filter: want exactly 4
            id4 = k4_identity_upper(n, g)
            if id4 != 4:
                continue
            id4_count += 1
            arcs = circ_arcs(n, g)
            # lower bound: omega_vec >= 4 via SAT (UNSAT of no-K4)
            ge4, dt, ncl = omega_vec_ge_K_via_sat(n, arcs, 4)
            SAT_TIME_BUDGET += dt
            if not ge4:
                continue
            ge4_count += 1
            # so omega_vec == 4 (id-order upper=4, sat lower>=4)
            # criticality: every vertex deletion must have omega_vec == 3.
            # vertex-transitive => only need ONE deletion. Check deletion of vertex 0.
            nn, sub = core.subtournament(n, arcs, [w for w in range(n) if w != 0])
            # deletion: upper via best order, lower via SAT
            del_upper = best_order_upper(nn, sub, tries=200)
            del_ge3, dt3, _ = omega_vec_ge_K_via_sat(nn, sub, 3)
            del_ge4, dt4, _ = omega_vec_ge_K_via_sat(nn, sub, 4)
            # deletion omega_vec: >=3 (del_ge3) and <=3 (not del_ge4 and upper<=3)
            del_is3 = del_ge3 and (not del_ge4) and del_upper <= 3
            rec = {"n": n, "g": sorted(g), "id_order_clique": id4,
                   "omega_vec_ge4_sat": ge4,
                   "deletion0_upper": del_upper, "deletion0_ge3": del_ge3,
                   "deletion0_ge4": del_ge4, "deletion0_is3": del_is3}
            crit_found.append(rec)
            print(f"  n={n} g={sorted(g)} ov=4 (id_up=4, sat_ge4=True) "
                  f"del0_upper={del_upper} del0_ge3={del_ge3} del0_ge4={del_ge4} "
                  f"=> deletion=3? {del_is3}", flush=True)
            if del_is3:
                out["found"].append(rec)
                print(f"  *** CANDIDATE 4-CRITICAL CIRCULANT n={n} g={sorted(g)} ***",
                      flush=True)
                # for vertex-transitive (circulant) all deletions isomorphic, so this
                # IS 4-critical. record and move to next n (one witness per n suffices)
                break
        out["search"].append({"n": n, "examined": examined,
                               "id_clique_eq4": id4_count, "omega_vec_eq4": ge4_count,
                               "criticality_candidates": len(crit_found),
                               "found_4critical": [r for r in crit_found if r["deletion0_is3"]]})
        print(f"n={n}: examined={examined} id4={id4_count} ov4={ge4_count} "
              f"crit={sum(1 for r in crit_found if r['deletion0_is3'])} "
              f"(SAT cum {SAT_TIME_BUDGET:.1f}s)", flush=True)

    out["sat_time_total_s"] = round(SAT_TIME_BUDGET, 2)
    dp = os.path.join(os.path.dirname(__file__), "..", "data",
                      "search_4critical_circulant.json")
    with open(os.path.abspath(dp), "w") as f:
        json.dump(out, f, indent=2)
    print("\n=== SUMMARY ===")
    print(json.dumps({"validation_ok": allok,
                      "found_4critical": out["found"],
                      "search": out["search"]}, indent=2))


if __name__ == "__main__":
    main()
