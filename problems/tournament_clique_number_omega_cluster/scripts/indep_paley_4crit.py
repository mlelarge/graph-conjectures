"""INDEPENDENT re-verification of the Paley 4-critical sweep claim.

Own from-scratch no-K-clique SAT encoding (NOT importing s4.build_cnf_no_kclique),
cross-validated vs core.omega_vec on small tournaments, then applied to
QR_19, QR_23, QR_31 (whole) and their vertex-0 deletions.
"""
import os
import sys, time, itertools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import core
from pysat.formula import CNF
from pysat.solvers import Cadical153, Minisat22


def qr_set(p):
    return sorted({(x * x) % p for x in range(1, p)})

def circ_arcs(p, g):
    return [(i, (i + d) % p) for i in range(p) for d in g]

def is_tournament_gen(p, g):
    negg = set((-d) % p for d in g)
    return (not (set(g) & negg)) and len(g) == (p - 1) // 2 and 0 not in g

def beats_matrix(n, arcs):
    b = [[False]*n for _ in range(n)]
    for (u, v) in arcs:
        b[u][v] = True
    return b


def cnf_no_kclique(n, arcs, K):
    """Independent encoding. Variable x_{u,v} (u<v) TRUE means u<v in the order.
    For a pair we use lit(u,v): +var if u<v stored canonically, sign flips for (v,u).
    Backedge graph: edge between a,b iff the LATER one (in order) beats (->) the
    EARLIER one. A reversed (backedge) K-clique on a transitive K-subset
    occurs iff the order is exactly the reverse of the transitive order.
    We forbid that single reversed placement per transitive K-subset.
    """
    b = beats_matrix(n, arcs)
    idx = {}
    nv = 0
    def var(u, v):
        # canonical key with u<v
        nonlocal nv
        key = (u, v) if u < v else (v, u)
        if key not in idx:
            nv += 1
            idx[key] = nv
        lit = idx[key]
        return lit if u < v else -lit
    cnf = CNF()
    for u in range(n):
        for v in range(u+1, n):
            var(u, v)
    # transitivity: u<v and v<w => u<w
    for u in range(n):
        for v in range(n):
            if v == u: continue
            for w in range(n):
                if w in (u, v): continue
                cnf.append([-var(u, v), -var(v, w), var(u, w)])
    nclq = 0
    for S in itertools.combinations(range(n), K):
        outdeg = {x: sum(1 for y in S if y != x and b[x][y]) for x in S}
        if sorted(outdeg.values()) != list(range(K)):
            continue
        # transitive order: source has out-deg K-1 (beats all others in S)
        order = sorted(S, key=lambda x: -outdeg[x])
        if not all(b[order[a]][order[c]] for a in range(K) for c in range(a+1, K)):
            continue
        # backedge K-clique forms iff order reversed: order[K-1]<...<order[0].
        # Forbid: clause = OR_i (order[i] < order[i+1]) -- at least one stays forward.
        clause = [var(order[i], order[i+1]) for i in range(K-1)]
        cnf.append(clause)
        nclq += 1
    return cnf, nclq


def omega_ge_K(n, arcs, K, both=False):
    cnf, nclq = cnf_no_kclique(n, arcs, K)
    with Cadical153(bootstrap_with=cnf.clauses) as m:
        sat_c = m.solve()
    res = {"K": K, "nclauses_forbid": nclq, "cadical_sat": sat_c, "ge_K": (not sat_c)}
    if both:
        with Minisat22(bootstrap_with=cnf.clauses) as m:
            sat_m = m.solve()
        res["minisat_sat"] = sat_m
        res["solvers_agree"] = (sat_c == sat_m)
    return res


def validate():
    print("=== INDEPENDENT VALIDATION vs core.omega_vec ===", flush=True)
    cases = [(7, {1,2,4}), (7, {1,2,3}), (7, {1,3,5}),
             (9, {1,2,3,4}), (9, {1,2,4,7}), (11, {1,2,3,4,6})]
    allok = True
    for p, g in cases:
        if not is_tournament_gen(p, list(g)):
            print(f"  skip ({p},{sorted(g)}) not tournament"); continue
        arcs = circ_arcs(p, list(g))
        ov = core.omega_vec(p, arcs)
        for K in (2, 3, 4):
            r = omega_ge_K(p, arcs, K)
            truth = ov >= K
            ok = (r["ge_K"] == truth)
            allok = allok and ok
            print(f"  C{p}{sorted(g)} ov={ov} K={K} sat_ge={r['ge_K']} truth={truth} {'OK' if ok else 'MISMATCH'}", flush=True)
    print("VALIDATION ALL AGREE:", allok, flush=True)
    return allok


def main():
    assert validate(), "SAT oracle validation FAILED"
    results = {}
    for p in (19, 23, 31):
        g = qr_set(p)
        assert is_tournament_gen(p, g), (p, g)
        arcs = circ_arcs(p, g)
        # vertex-transitivity check: x->x+1 is automorphism (circulant => yes by construction)
        # whole-tournament omega_vec
        ge4 = omega_ge_K(p, arcs, 4, both=True)
        ge5 = omega_ge_K(p, arcs, 5, both=True)
        eq4 = ge4["ge_K"] and (not ge5["ge_K"])
        # deletion of vertex 0 (vertex-transitive => suffices)
        keep = [v for v in range(p) if v != 0]
        sn, sarcs = core.subtournament(p, arcs, keep)
        dge3 = omega_ge_K(sn, sarcs, 3, both=True)
        dge4 = omega_ge_K(sn, sarcs, 4, both=True)
        del_eq3 = dge3["ge_K"] and (not dge4["ge_K"])
        crit = eq4 and del_eq3
        results[p] = {"g_is_QR": g == qr_set(p), "is_tournament": True,
                      "ge4": ge4, "ge5": ge5, "omega_vec_eq4": eq4,
                      "del_ge3": dge3, "del_ge4": dge4, "del_eq3": del_eq3,
                      "is_4_critical": crit}
        print(f"\nQR_{p}: ge4(noK4 UNSAT)={ge4['ge_K']}(agree={ge4['solvers_agree']}), "
              f"ge5={ge5['ge_K']}(agree={ge5['solvers_agree']}) => omega_vec==4? {eq4}", flush=True)
        print(f"   deletion: ge3={dge3['ge_K']}(agree={dge3['solvers_agree']}), "
              f"ge4={dge4['ge_K']}(agree={dge4['solvers_agree']}) => del_eq3? {del_eq3} "
              f"=> 4-CRITICAL? {crit}", flush=True)
    crit_at = [p for p in results if results[p]["is_4_critical"]]
    eq4_at = [p for p in results if results[p]["omega_vec_eq4"]]
    print(f"\nSUMMARY: omega_vec==4 at {eq4_at}; 4-CRITICAL at {crit_at}", flush=True)
    return results


if __name__ == "__main__":
    main()
