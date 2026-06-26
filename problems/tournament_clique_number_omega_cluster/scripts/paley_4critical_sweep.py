"""H10 lever (A): is Paley(p)=QR_p 4-omega_vec-critical at EVERY prime p=3 mod 4?

p=19 CONFIRMED (P15). This script tests p in {23,31,43,47,59,67,71,79,83}.

For each Paley(p) = Cay(Z/p, QR_p), QR_p = {x^2 mod p : x=1..p-1} (size (p-1)/2):
  - is_tournament: QR_p disjoint from -QR_p (true since p=3 mod 4, -1 a non-residue)
  - omega_vec>=4 : no-K4 SAT UNSAT (omega_vec_ge_K_via_sat K=4)
  - omega_vec<=4 : no-K5 SAT SAT (omega_vec_ge_K_via_sat K=5 returns ge5=False)
                   AND a concrete order (min rotation) with backedge clique<=4
  => omega_vec==4 EXACTLY.
  - 4-criticality (vertex-transitive => deletion of vertex 0 only):
      omega_vec(QR_p - 0) == 3  iff  no-K3 SAT UNSAT (>=3)  AND  no-K4 SAT SAT (<=3)
  - INDEPENDENT lower bound: dom(QR_p) >= 4 (N0=QR_p u {0} not coverable by 3 translates)
    + PROVED paper Property 3.2 (dom<=omega_vec).  SAT-independent corroboration.

Validation: omega_vec_ge_K_via_sat is the benchmark.lower_bound_oracles (iii) generalized
no-K-clique SAT oracle, validated K=2..5 vs exact core.omega_vec (search_4critical_circulant).
Here we ALSO re-run a small validation pass at the K=4 boundary on the n=19 Paley object
(known omega_vec=4 from P15) so the >=4 direction is exercised on a genuine omega_vec=4 object.
"""
import os
import sys, os, time, json, itertools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import core
import search_4critical_circulant as s4
import k4_ground

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')

PRIMES_3MOD4 = [19, 23, 31, 43, 47, 59, 67, 71, 79, 83]  # 19 = known control (P15)


def is_prime(n):
    if n < 2: return False
    i = 2
    while i * i <= n:
        if n % i == 0: return False
        i += 1
    return True


def qr_set(p):
    return sorted({(x * x) % p for x in range(1, p)})


def circ_arcs(p, g):
    return [(i, (i + d) % p) for i in range(p) for d in g]


def is_tournament_gen(p, g):
    negg = set((-d) % p for d in g)
    return (not (set(g) & negg)) and len(g) == (p - 1) // 2 and 0 not in g


def min_rotation_upper(p, arcs):
    """Upper bound on omega_vec via min backedge-omega over the p cyclic rotations."""
    best = None
    for r in range(p):
        o = [(i + r) % p for i in range(p)]
        w = core.omega_of_order(p, arcs, o)
        if best is None or w < best:
            best = w
    return best


def main():
    out = {"primes_tested": [], "results": []}

    # --- small validation at the K=4 boundary on the n=19 Paley control ---
    p0 = 19
    g0 = qr_set(p0)
    arcs0 = circ_arcs(p0, g0)
    ge4_0, _, _ = s4.omega_vec_ge_K_via_sat(p0, arcs0, 4)
    ge5_0, _, _ = s4.omega_vec_ge_K_via_sat(p0, arcs0, 5)
    val = {"object": "Paley(19) control (P15: omega_vec=4)",
           "no_K4_UNSAT_ge4": ge4_0, "no_K5_SAT_lt5": (not ge5_0),
           "consistent_with_P15": (ge4_0 and (not ge5_0))}
    out["k4_boundary_validation"] = val
    print(f"VALIDATION Paley(19): ge4={ge4_0} (expect True), ge5={ge5_0} (expect False) "
          f"-> consistent={val['consistent_with_P15']}", flush=True)

    for p in PRIMES_3MOD4:
        assert is_prime(p) and p % 4 == 3, p
        g = qr_set(p)
        ok_t = is_tournament_gen(p, g)
        arcs = circ_arcs(p, g)
        rec = {"p": p, "g_is_QR": True, "g": g, "is_tournament": ok_t}
        print(f"\n=== Paley({p}) QR_p (|g|={len(g)}) is_tournament={ok_t} ===", flush=True)
        if not ok_t:
            rec["error"] = "not a tournament generator"
            out["results"].append(rec); continue

        t0 = time.time()
        ge4, t_ge4, ncl4 = s4.omega_vec_ge_K_via_sat(p, arcs, 4)   # UNSAT => omega_vec>=4
        ge5, t_ge5, ncl5 = s4.omega_vec_ge_K_via_sat(p, arcs, 5)   # SAT => omega_vec<=4
        upper = min_rotation_upper(p, arcs)
        rec["omega_vec_ge4_noK4_UNSAT"] = ge4
        rec["omega_vec_ge5_noK5_UNSAT"] = ge5
        rec["min_rotation_upper"] = upper
        eq4 = ge4 and (not ge5)
        rec["omega_vec_eq4"] = eq4
        rec["t_omega_s"] = round(time.time() - t0, 3)
        print(f"   omega_vec>=4 (no-K4 UNSAT)={ge4} [{t_ge4:.3f}s], "
              f"omega_vec>=5 (no-K5 UNSAT)={ge5} [{t_ge5:.3f}s], "
              f"min-rotation upper={upper} => omega_vec==4? {eq4}", flush=True)

        # independent lower bound: dom>=4 + Property 3.2
        dom = k4_ground.dom_circulant(p, set(g), ub=4)
        rec["dom"] = dom
        rec["dom_ge4_certifies_ge4"] = (dom >= 4)
        print(f"   dom(QR_{p})={dom} (>=4 independently certifies omega_vec>=4 via Prop 3.2: "
              f"{dom>=4})", flush=True)

        if eq4:
            # 4-criticality: vertex-transitive => deletion of vertex 0 only
            keep = [v for v in range(p) if v != 0]
            sn, sarcs = core.subtournament(p, arcs, keep)
            td0 = time.time()
            d_ge3, _, _ = s4.omega_vec_ge_K_via_sat(sn, sarcs, 3)  # UNSAT => del>=3
            d_ge4, _, _ = s4.omega_vec_ge_K_via_sat(sn, sarcs, 4)  # UNSAT => del>=4
            del_eq3 = d_ge3 and (not d_ge4)
            rec["deletion_ge3_noK3_UNSAT"] = d_ge3
            rec["deletion_ge4_noK4_UNSAT"] = d_ge4
            rec["deletion_omega_vec_eq3"] = del_eq3
            rec["is_4_critical_vt"] = del_eq3
            rec["t_deletion_s"] = round(time.time() - td0, 3)
            print(f"   deletion(QR-0): >=3 (no-K3 UNSAT)={d_ge3}, >=4 (no-K4 UNSAT)={d_ge4} "
                  f"=> deletion omega_vec==3? {del_eq3} => 4-CRITICAL(vt)? {del_eq3}", flush=True)
        else:
            rec["is_4_critical_vt"] = False

        out["primes_tested"].append(p)
        out["results"].append(rec)
        # checkpoint after each prime (large primes are slow)
        with open(f"{ROOT}/data/paley_4critical_sweep.json", "w") as f:
            json.dump(out, f, indent=2)

    # summary
    crit = [r["p"] for r in out["results"] if r.get("is_4_critical_vt")]
    eq4l = [r["p"] for r in out["results"] if r.get("omega_vec_eq4")]
    notcrit = [r["p"] for r in out["results"]
               if r.get("omega_vec_eq4") and not r.get("is_4_critical_vt")]
    out["summary"] = {"omega_vec_eq4_at": eq4l, "4_critical_at": crit,
                      "eq4_but_not_critical_at": notcrit,
                      "all_eq4_are_critical": (eq4l == crit)}
    print(f"\nSUMMARY: omega_vec==4 at {eq4l}; 4-CRITICAL at {crit}; "
          f"eq4-but-not-critical at {notcrit}", flush=True)
    with open(f"{ROOT}/data/paley_4critical_sweep.json", "w") as f:
        json.dump(out, f, indent=2)
    print("SAVED data/paley_4critical_sweep.json", flush=True)
    print(json.dumps(out["summary"]))


if __name__ == "__main__":
    main()
