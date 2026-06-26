"""GROUND the k=4 circulant proposal via the VALIDATED SAT-betweenness K-clique
lower-bound oracle (benchmark.lower_bound_oracles), because the proposal's
planned exact core.omega_vec_bb(n,arcs,ub=4) is INFEASIBLE at n=13/15 (a single
call did not finish in >180s; the bb prune only fires once the placed clique
reaches 4, which on a dense backedge graph happens very deep).

The SAT oracle is SOUND and validated against exact omega_vec (search_4critical_circulant.validate_sat_oracle).

For each valid circulant generator g on Z/n with IDENTITY-order clique == 4
(necessary upper-bound filter, since omega_vec <= omega_of_order(identity)),
decide:
  omega_vec >= 4  via SAT (UNSAT of no-K4 CNF)
  upper bound      via best_order_upper (identity + rotations + random)
  => omega_vec == 4 iff (sat says >=4) and (best_upper == 4)
  4-criticality: for EVERY vertex deletion, omega_vec(T-v) == 3
       i.e. SAT says >=3 (UNSAT no-K3) AND NOT >=4 (SAT no-K4).
       (vertex-transitive circulants: one deletion's value holds for all, but we
        check all to be safe / for non-vertex-transitive nothing here.)

Also settle the two n=19 dom>=4 candidates (QR_19 and reverse).
"""
import sys, os, json, time, itertools
sys.path.insert(0, os.path.dirname(__file__))
import core
from search_4critical_circulant import (
    circ_arcs, omega_vec_ge_K_via_sat, identity_order_clique,
    best_order_upper, validate_sat_oracle,
)


def valid_generators(n):
    m = (n - 1) // 2
    pairs = [(x, n - x) for x in range(1, m + 1)]
    for choice in itertools.product(*pairs):
        yield frozenset(choice)


def omega_vec_exact_via_sat(n, arcs, cap=6):
    """Exact omega_vec by climbing K=2..cap with the SAT oracle: smallest K with
    NOT(omega>=K+1), found as: omega_vec = max K such that omega>=K.
    Returns the value (or f'>{cap}')."""
    val = 1
    for K in range(2, cap + 1):
        ge, _, _ = omega_vec_ge_K_via_sat(n, arcs, K)
        if ge:
            val = K
        else:
            return val
    return f">{cap}"


def is_4_critical_sat(n, arcs):
    """omega_vec(T)==4 and omega_vec(T-v)==3 for all v, via SAT oracle.
    Returns (is_crit, detail)."""
    # whole: >=4 and not >=5
    ge4, _, _ = omega_vec_ge_K_via_sat(n, arcs, 4)
    if not ge4:
        return False, "omega_vec<4"
    ge5, _, _ = omega_vec_ge_K_via_sat(n, arcs, 5)
    if ge5:
        return False, "omega_vec>=5"
    # deletions: each must be exactly 3
    for v in range(n):
        nn, sub = core.subtournament(n, arcs, [w for w in range(n) if w != v])
        d3, _, _ = omega_vec_ge_K_via_sat(nn, sub, 3)
        if not d3:
            return False, f"deletion v={v} omega_vec<3"
        d4, _, _ = omega_vec_ge_K_via_sat(nn, sub, 4)
        if d4:
            return False, f"deletion v={v} omega_vec>=4"
    return True, "4-critical"


def main():
    out = {}
    ok, recs = validate_sat_oracle()
    out["sat_validation_all_agree"] = ok
    out["sat_validation"] = recs
    if not ok:
        print("SAT ORACLE VALIDATION FAILED - ABORT", flush=True)
        json.dump(out, open(_path(), "w"), indent=2)
        return

    scan = {}
    for n in [13, 15]:
        hist = {}
        ov4_gens = []
        crit_gens = []
        nid4 = 0
        t0 = time.time()
        for g in valid_generators(n):
            arcs = circ_arcs(n, g)
            if identity_order_clique(n, arcs) != 4:
                continue
            nid4 += 1
            ub = best_order_upper(n, arcs, tries=40)
            ge4, _, _ = omega_vec_ge_K_via_sat(n, arcs, 4)
            if ge4 and ub == 4:
                ov = 4
            elif not ge4:
                # omega_vec <= 3; pin exact small value
                ov = omega_vec_exact_via_sat(n, arcs, cap=3)
            else:
                # ge4 True but best upper >4: omega_vec >=4, climb
                ov = omega_vec_exact_via_sat(n, arcs, cap=6)
            hist[str(ov)] = hist.get(str(ov), 0) + 1
            if ov == 4:
                ov4_gens.append(sorted(g))
                is_c, _ = is_4_critical_sat(n, arcs)
                if is_c:
                    crit_gens.append(sorted(g))
        scan[n] = {
            "n_identity_clique_eq_4": nid4,
            "omega_vec_hist": hist,
            "omega_vec_eq_4_generators": ov4_gens,
            "four_critical_generators": crit_gens,
            "time_s": round(time.time() - t0, 2),
        }
        print(f"[SAT scan] n={n}: idclique4={nid4} hist={hist} "
              f"ov4={len(ov4_gens)} crit4={len(crit_gens)} "
              f"crit_gens={crit_gens} ({scan[n]['time_s']}s)", flush=True)
    out["sat_scan"] = scan
    smallest = next((n for n in [13, 15] if scan[n]["four_critical_generators"]), None)
    out["smallest_4critical_order_in_13_15"] = smallest

    # n=19 dom>=4 candidates
    qr19 = frozenset({pow(x, 2, 19) for x in range(1, 19)})
    rev19 = frozenset((19 - x) % 19 for x in qr19)
    n19 = {}
    for name, g in [("QR_19", qr19), ("reverse_QR_19", rev19)]:
        arcs = circ_arcs(19, g)
        rec = {"g": sorted(g), "is_tournament": core.is_tournament(19, arcs),
               "identity_clique": identity_order_clique(19, arcs)}
        ub = best_order_upper(19, arcs, tries=200)
        rec["best_upper"] = ub
        ge4, t4, _ = omega_vec_ge_K_via_sat(19, arcs, 4)
        ge5, t5, _ = omega_vec_ge_K_via_sat(19, arcs, 5)
        rec["omega_vec_ge4_sat"] = ge4
        rec["omega_vec_ge5_sat"] = ge5
        rec["sat_time_ge4_s"] = round(t4, 4)
        if ge4 and not ge5:
            rec["omega_vec"] = 4 if ub == 4 else f"in[4,{ub}]"
        # 4-criticality (vertex-transitive: deletion of vertex 0 represents all)
        if ge4 and not ge5:
            nn, sub = core.subtournament(19, arcs, [w for w in range(19) if w != 0])
            d3, _, _ = omega_vec_ge_K_via_sat(nn, sub, 3)
            d4, _, _ = omega_vec_ge_K_via_sat(nn, sub, 4)
            ubd = best_order_upper(nn, sub, tries=100)
            rec["deletion0_ge3_sat"] = d3
            rec["deletion0_ge4_sat"] = d4
            rec["deletion0_best_upper"] = ubd
            rec["deletion0_omega_vec"] = 3 if (d3 and not d4 and ubd == 3) else \
                (f"in[{3 if d3 else '?'},{ubd}]")
            rec["is_4_critical_via_vt_deletion0"] = bool(d3 and not d4 and ubd == 3 and ge4 and not ge5)
        n19[name] = rec
        print(f"[n=19 {name}] {rec}", flush=True)
    out["n19_dom_ge4_candidates"] = n19

    json.dump(out, open(_path(), "w"), indent=2)
    print("SAVED", os.path.abspath(_path()), flush=True)


def _path():
    return os.path.join(os.path.dirname(__file__), "..", "data", "scan_k4_sat.json")


if __name__ == "__main__":
    main()
