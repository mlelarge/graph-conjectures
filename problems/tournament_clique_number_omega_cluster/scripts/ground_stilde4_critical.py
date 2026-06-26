"""GROUND the S~_4 = C3[S~_3] (order 27) criticality proposal.

Falsifiable prediction:
  omega_vec(S~_4)=4 (proven Lemma 3.8 lower + check upper)  AND
  S~_4 is 4-omega_vec-critical: every single-vertex deletion has omega_vec=3.
KILL if every single-vertex deletion of S~_4 still has omega_vec=4
(deletion does not drop omega_vec) -- the G3 failure mode.
"""
import sys, os, time, itertools
sys.path.insert(0, os.path.dirname(__file__))
import core
import constructions as C
from search_4critical_circulant import (
    omega_vec_ge_K_via_sat, best_order_upper, build_cnf_no_kclique)


def omega_vec_value_via_sat(n, arcs, lo=1, hi=6):
    """Pin omega_vec exactly using the no-K-clique SAT oracle:
    omega_vec >= K iff no-K-clique CNF UNSAT. Find largest K with UNSAT."""
    val = lo
    details = {}
    for K in range(lo + 1, hi + 1):
        ge, dt, ncl = omega_vec_ge_K_via_sat(n, arcs, K)
        details[K] = {"ge_K": ge, "time": round(dt, 3), "nclauses": ncl}
        if ge:
            val = K
        else:
            break
    return val, details


def main():
    t_all = time.time()
    print("=== Build S~_3 (order 9) and S~_4 = C3[S~_3] (order 27) ===", flush=True)
    n3, a3 = C.S_tilde(3)
    n4, a4 = C.S_tilde(4)
    print(f"S~_3: n={n3}, is_tournament={core.is_tournament(n3, a3)}", flush=True)
    print(f"S~_4: n={n4}, is_tournament={core.is_tournament(n4, a4)}", flush=True)
    assert n3 == 9 and n4 == 27

    # ---- Confirm S~_3 omega_vec = 3 (cross-check, cheap) ----
    print("\n=== omega_vec(S~_3) via SAT ===", flush=True)
    ov3, det3 = omega_vec_value_via_sat(n3, a3, lo=1, hi=5)
    print(f"omega_vec(S~_3) = {ov3}  details={det3}", flush=True)
    # also exact bb on order 9
    ov3_bb = core.omega_vec_bb(n3, a3, ub=5)
    print(f"omega_vec(S~_3) exact bb = {ov3_bb}", flush=True)

    # ---- Confirm omega_vec(S~_4) = 4 ----
    print("\n=== omega_vec(S~_4) (order 27) via SAT no-K-clique ===", flush=True)
    # lower: no-K4 should be UNSAT (>=4, = Lemma 3.8); upper: no-K5 should be SAT (<=4)
    ge4, dt4, ncl4 = omega_vec_ge_K_via_sat(n4, a4, 4)
    print(f"no-K4 UNSAT? {ge4}  (=> omega_vec>=4)  time={dt4:.3f}s nclauses={ncl4}", flush=True)
    ge5, dt5, ncl5 = omega_vec_ge_K_via_sat(n4, a4, 5)
    print(f"no-K5 UNSAT? {ge5}  (=> omega_vec>=5)  time={dt5:.3f}s nclauses={ncl5}", flush=True)
    upper4 = best_order_upper(n4, a4, tries=400)
    print(f"best-order upper bound = {upper4}", flush=True)
    ov4 = 4 if (ge4 and not ge5) else ("?>=5" if ge5 else "<4")
    print(f"=> omega_vec(S~_4) = {ov4}", flush=True)

    # ---- CRITICALITY: test all 27 single-vertex deletions ----
    # S~_4 has automorphisms (Z/3 rotation of the three top blocks + S~_3 automs),
    # but to be fully rigorous and since order-26 SAT is ms-fast, test ALL 27.
    print("\n=== CRITICALITY: omega_vec(S~_4 - v) for all v ===", flush=True)
    deletion_vals = {}
    all_drop = True
    none_drop = True
    for v in range(n4):
        keep = [w for w in range(n4) if w != v]
        nn, sub = core.subtournament(n4, a4, keep)
        # omega_vec(sub): >=3 ? (no-K3 UNSAT) and >=4 ? (no-K4 UNSAT)
        ge3, _, _ = omega_vec_ge_K_via_sat(nn, sub, 3)
        ge4d, _, _ = omega_vec_ge_K_via_sat(nn, sub, 4)
        if ge4d:
            val = ">=4"
            all_drop = False
        elif ge3:
            val = 3
            none_drop = False
        else:
            val = "<3"
            none_drop = False
        deletion_vals[v] = val
        if v < 6 or val != 3:
            print(f"  v={v:2d}: omega_vec(S~_4-v) = {val}  (ge3={ge3}, ge4={ge4d})", flush=True)
    # summary
    from collections import Counter
    hist = Counter(str(x) for x in deletion_vals.values())
    print(f"\nDeletion omega_vec histogram: {dict(hist)}", flush=True)
    print(f"ALL deletions drop to 3 (=> 4-CRITICAL): {all_drop}", flush=True)
    print(f"NONE drop (=> G3 failure mode, KILL): {none_drop}", flush=True)

    is_critical = (ov4 == 4) and all_drop
    print(f"\n=== VERDICT INPUT ===", flush=True)
    print(f"omega_vec(S~_4)=4: {ov4 == 4}", flush=True)
    print(f"S~_4 is 4-omega_vec-critical: {is_critical}", flush=True)
    print(f"total time {time.time()-t_all:.1f}s", flush=True)


if __name__ == "__main__":
    main()
