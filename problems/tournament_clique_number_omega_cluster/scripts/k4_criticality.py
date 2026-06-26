"""Fast SAT-only k=4 sandwich + criticality check.

For each (dom>=4, id-omega==4) witness circulant on Z/n:
  - omega_vec>=4 : K4-free SAT (build_cnf_k4) UNSAT      [validated, 0 mismatch n<=7]
  - omega_vec<=4 : identity order backedge clique == 4   [explicit witness]
  => omega_vec == 4 EXACTLY (the sandwich closes).
  - 4-criticality (vertex-transitive => check deletion of vertex 0 only):
      deletion omega_vec == 3  iff  K4-free SAT (<=3)  AND  triangle-free UNSAT (>=3)
    All via ms SAT, no slow unrestricted omega_vec_bb.

Both SAT encodings are validated against the exact core.omega_vec_bb:
 - triangle-free (omega<=2): the original D8 oracle (sat_betweenness_step1), 1200+ n<=7, 0 mism
 - K4-free      (omega<=3): k4_ground.validate_encoding, 1100 n<=7, 0 mism (re-run here)
"""
import os
import sys, time, json, itertools, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import core
import k4_ground
import sat_betweenness_step1 as sb
from pysat.solvers import Cadical153

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')


def circ_arcs(n, g):
    return [(i, (i + d) % n) for i in range(n) for d in g]


def sat_tri_free(n, arcs):
    """True (SAT) iff some order triangle-free iff omega_vec<=2."""
    cnf, _ = sb.build_cnf(n, arcs)
    with Cadical153(bootstrap_with=cnf.clauses) as m:
        return m.solve()


def sat_k4_free(n, arcs):
    """True (SAT) iff some order K4-free iff omega_vec<=3."""
    clauses, _, nf = k4_ground.build_cnf_k4(n, arcs)
    with Cadical153(bootstrap_with=clauses) as m:
        return m.solve(), nf


def exact_omega_vec_via_sat(n, arcs, hi=4):
    """Return exact omega_vec in {1,2,3,>=4} via the two validated SAT oracles
    (only meaningful up to omega_vec=4, which is all we need)."""
    if sat_tri_free(n, arcs):       # SAT => omega_vec<=2
        # distinguish 1 vs 2 cheaply via identity? omega_vec>=2 unless transitive;
        # we only care about >=3 boundary, so report '<=2'
        return "<=2"
    # omega_vec>=3
    k4sat, _ = sat_k4_free(n, arcs)
    if k4sat:                       # SAT => omega_vec<=3, and >=3 => ==3
        return 3
    return ">=4"


def witnesses_for(n):
    m = (n - 1) // 2
    pairs = [(d, n - d) for d in range(1, m + 1)]
    out = []
    for choice in itertools.product([0, 1], repeat=m):
        g = set(pairs[i][choice[i]] for i in range(m))
        if k4_ground.dom_circulant(n, g, ub=4) >= 4 and k4_ground.identity_omega(n, g) == 4:
            out.append(sorted(g))
    return out


def validate_both_encodings():
    random.seed(999)
    mism_k4 = mism_tri = 0; checked = 0
    for n in range(4, 8):
        for _ in range(200):
            arcs = []
            for i in range(n):
                for j in range(i + 1, n):
                    arcs.append((i, j) if random.random() < 0.5 else (j, i))
            ov = core.omega_vec_bb(n, arcs, ub=n)
            checked += 1
            if sat_tri_free(n, arcs) != (ov <= 2): mism_tri += 1
            k4sat, _ = sat_k4_free(n, arcs)
            if k4sat != (ov <= 3): mism_k4 += 1
    return checked, mism_tri, mism_k4


def main():
    out = {}
    print("=== validate both SAT encodings vs core.omega_vec_bb (n<=7) ===", flush=True)
    checked, mt, mk = validate_both_encodings()
    print(f"checked={checked}  tri-free mismatches={mt}  K4-free mismatches={mk}", flush=True)
    out["validation"] = {"checked": checked, "tri_free_mismatches": mt, "k4_free_mismatches": mk}
    if mt or mk:
        print("ENCODING INVALID");
        json.dump(out, open(f"{ROOT}/data/k4_criticality.json", "w"), indent=2)
        print(json.dumps(out)); return

    results = []
    for n in [19, 25, 27]:
        ws = witnesses_for(n)
        print(f"\n=== n={n}: {len(ws)} (dom>=4 & id-omega==4) witnesses ===", flush=True)
        found_critical = None
        # check ALL witnesses for exact omega_vec==4 and 4-criticality
        per_n = []
        for g in ws:
            arcs = circ_arcs(n, g)
            t0 = time.time()
            k4sat, nf = sat_k4_free(n, arcs)
            ge4 = not k4sat
            idom = k4_ground.identity_omega(n, g)
            exact4 = ge4 and idom == 4
            rec = {"n": n, "g": g, "omega_vec_ge4": ge4, "id_omega_upper": idom,
                   "omega_vec_eq4": exact4}
            if exact4:
                # 4-criticality: vertex-transitive => deletion of vtx 0 only.
                keep = [v for v in range(n) if v != 0]
                sn, sarcs = core.subtournament(n, arcs, keep)
                dov = exact_omega_vec_via_sat(sn, sarcs)
                rec["deletion_omega_vec"] = dov
                rec["is_4_critical_vt"] = (dov == 3)
                if dov == 3 and found_critical is None:
                    found_critical = g
            rec["t_s"] = round(time.time() - t0, 3)
            per_n.append(rec)
        # summary
        n_eq4 = sum(1 for r in per_n if r["omega_vec_eq4"])
        n_crit = sum(1 for r in per_n if r.get("is_4_critical_vt"))
        print(f"   omega_vec==4 (sandwich closes): {n_eq4}/{len(ws)} witnesses", flush=True)
        print(f"   4-omega_vec-critical (vt):       {n_crit}/{len(ws)} witnesses", flush=True)
        if found_critical:
            print(f"   FIRST 4-critical circulant: n={n}, g={found_critical}", flush=True)
        results.append({"n": n, "n_witnesses": len(ws), "n_omega_vec_eq4": n_eq4,
                        "n_4_critical": n_crit, "first_4_critical_g": found_critical,
                        "per_witness": per_n})
    out["results"] = results
    json.dump(out, open(f"{ROOT}/data/k4_criticality.json", "w"), indent=2)
    print("\nSAVED data/k4_criticality.json", flush=True)


if __name__ == "__main__":
    main()
