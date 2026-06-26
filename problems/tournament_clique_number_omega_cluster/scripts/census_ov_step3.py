"""STEP 3 of the dic-circulant census: omega_vec of every dic-vertex-critical rep.

For each 4-dic-VERTEX-critical circulant rep from data/census_dic_circulant.json:
  no-K4 CNF (validated build_cnf_no_kclique): UNSAT (Cadical153 AND Minisat22)
  => omega_vec>=4; then no-K5 SAT => omega_vec<=4; then deletion T-0:
  no-K3 UNSAT => ov(T-0)>=3, no-K4 SAT => ov(T-0)<=3 => deletion ov=3
  => 4-omega_vec-critical (all deletions isomorphic by vertex transitivity)
  => verified Prop 6.2 input (4-ov-critical AND 4-dic-vertex-critical).
For each 5-dic-VERTEX-critical rep (r=5 stretch): no-K5 SAT => ov<=4 (kill) /
  UNSAT => ov>=5 (jackpot input candidate).
QR_19 and AC4_21 are flagged 'excluded_from_deliverable' (queued next_action).
"""
import sys, os, json, time
sys.path.insert(0, os.path.dirname(__file__))
from math import gcd
from pysat.solvers import Cadical153, Minisat22
from search_4critical_circulant import build_cnf_no_kclique, circ_arcs


def canon(n, g):
    units = [u for u in range(1, n) if gcd(u, n) == 1]
    return min(tuple(sorted((u * d) % n for d in g)) for u in units)


def no_k_status(n, arcs, K, both=False):
    """returns (sat:bool, time). SAT <=> omega_vec <= K-1."""
    cnf, _ = build_cnf_no_kclique(n, arcs, K)
    t0 = time.time()
    with Cadical153(bootstrap_with=cnf.clauses) as m:
        s1 = m.solve()
    if both:
        with Minisat22(bootstrap_with=cnf.clauses) as m:
            s2 = m.solve()
        assert s1 == s2, f"SOLVER DISAGREEMENT n={n} K={K}"
    return s1, time.time() - t0


def deletion(n, arcs):
    keep = [v for v in range(n) if v != 0]
    idx = {v: i for i, v in enumerate(keep)}
    return n - 1, [(idx[u], idx[v]) for (u, v) in arcs if u != 0 and v != 0]


EXCLUDED = {19: canon(19, {1, 4, 5, 6, 7, 9, 11, 16, 17}),     # QR_19 (P15)
            21: canon(21, {1, 2, 4, 7, 8, 9, 11, 15, 16, 18})}  # AC4_21 (P14)


def main():
    D = json.load(open(os.path.join(os.path.dirname(__file__), '..', 'data',
                                    'census_dic_circulant.json')))
    out = {"dic4_vc": [], "dic5_vc": []}
    for ns in sorted(D, key=int):
        n = int(ns)
        for r in D[ns]['dic_ge4']:
            if not r.get('vertex_critical'):
                continue
            g = r['g']
            arcs = circ_arcs(n, g)
            tag = ''
            if n in EXCLUDED and canon(n, set(g)) == EXCLUDED[n]:
                tag = 'EXCLUDED(QR_19/AC4_21, queued next_action)'
            if r['dic'] == 4:
                sat4, t4 = no_k_status(n, arcs, 4, both=True)
                row = {"n": n, "g": g, "dic": 4, "noK4_sat": sat4,
                       "t": round(t4, 3), "tag": tag}
                if not sat4:  # ov >= 4
                    sat5, _ = no_k_status(n, arcs, 5)
                    row["noK5_sat"] = sat5          # SAT => ov <= 4
                    nn, aa = deletion(n, arcs)
                    s3, _ = no_k_status(nn, aa, 3)  # UNSAT => del ov >= 3
                    s4, _ = no_k_status(nn, aa, 4)  # SAT  => del ov <= 3
                    row["del_noK3_sat"] = s3
                    row["del_noK4_sat"] = s4
                    row["ov"] = 4 if sat5 else ">=5"
                    row["del_ov_eq3"] = (not s3) and s4
                    row["prop62_input"] = (row["ov"] == 4 and row["del_ov_eq3"])
                else:
                    row["ov"] = "<=3"
                    row["prop62_input"] = False
                out["dic4_vc"].append(row)
                print(row, flush=True)
            elif r['dic'] == 5:
                sat5, t5 = no_k_status(n, arcs, 5, both=True)
                row = {"n": n, "g": g, "dic": 5, "noK5_sat": sat5,
                       "ov": "<=4" if sat5 else ">=5", "t": round(t5, 3)}
                out["dic5_vc"].append(row)
                print(row, flush=True)
    n4 = sum(1 for r in out["dic4_vc"] if r.get("prop62_input") and not r["tag"])
    n4x = sum(1 for r in out["dic4_vc"] if r.get("prop62_input") and r["tag"])
    n5 = sum(1 for r in out["dic5_vc"] if r["ov"] == ">=5")
    print(f"SUMMARY: dic4-vc reps={len(out['dic4_vc'])}, "
          f"Prop6.2 inputs (non-excluded)={n4}, excluded-but-input={n4x}; "
          f"dic5-vc reps={len(out['dic5_vc'])}, ov>=5 hits={n5}")
    json.dump(out, open(os.path.join(os.path.dirname(__file__), '..', 'data',
                                     'census_ov_step3.json'), 'w'), indent=1)
    print("saved data/census_ov_step3.json")


if __name__ == "__main__":
    main()
