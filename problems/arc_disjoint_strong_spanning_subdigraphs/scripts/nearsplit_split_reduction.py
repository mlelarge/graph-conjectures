"""CRUX-A via the SPLIT-digraph characterization (Ai-He-Li-Qin-Wang 2408.02260 /
Bang-Jensen-Wang 2309.06904) -- DELETION reduction, arc-addition lift.

Object: a (1,0)-near-split digraph D with V_1={p,q} (|V_1|=2), V_2={a,b,c}
(|V_2|=3, semicomplete), unique V_1-internal arc e_0=(p,q).  Then D-e_0 has
V_1 independent and V_2 semicomplete, i.e. D-e_0 is a SPLIT digraph.

We exhaustively enumerate ALL such labelled candidates:
  - V_2 semicomplete core: each of the 3 unordered pairs in {a,b,c} gets one of
    {->, <-, digon}  => 3^3 = 27 cores.
  - bridges: each of the 6 ordered pairs (x in V_1, y in V_2) independently has
    arc x->y present? and arc y->x present?  => 4^6 states.
  - e_0=(p,q) always present; (q,p) NEVER present (V_1-internal arcs = {e_0}).
Total 27 * 4^6 = 110592 labelled candidates.

For each candidate D:
  - lam_D  = oracle.arc_connectivity(D)         (exact)
  - keep only lam_D >= 3   (the CRUX-A / WC3 hypothesis)
  - assert lam_{D-e_0} >= 2 (predicted by the deletion-monotonicity claim)
  - SAD-decide D-e_0 and D (cross-check ON for any non-trivial verdict)

Tally the (sad(D-e_0), sad(D)) pairs:
  (SAT,  SAT)   : reduction's normal lift case
  (UNSAT,SAT)   : D-e_0 is an Ai-et-al exception, but D itself still SAT
                  (CONFIRM-2: reduction's closing step survives this instance)
  (UNSAT,UNSAT) : *** WC3 COUNTEREXAMPLE *** (3-arc-strong SAD-less digraph)
  (SAT,non-SAT) : *** LIFT VIOLATION *** (should be impossible: SAD lifts under
                  arc addition)  -- dump arcs.

Run:
  timeout 600 .venv/bin/python scripts/nearsplit_split_reduction.py
"""
import sys, os, json, time, itertools

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import oracle

P, Q = 0, 1            # V_1
A, B, C = 2, 3, 4      # V_2
V2_PAIRS = [(A, B), (A, C), (B, C)]
BRIDGE_PAIRS = [(x, y) for x in (P, Q) for y in (A, B, C)]  # 6 ordered V1xV2 pairs


def core_arcs(core_state):
    """core_state: tuple of 3 in {0:->,1:<-,2:digon} for the 3 V2 pairs."""
    arcs = []
    for (u, v), s in zip(V2_PAIRS, core_state):
        if s == 0:
            arcs.append((u, v))
        elif s == 1:
            arcs.append((v, u))
        else:
            arcs.append((u, v)); arcs.append((v, u))
    return arcs


def bridge_arcs(bridge_state):
    """bridge_state: tuple of 6 in {0:none,1:x->y,2:y->x,3:both} for the 6 pairs."""
    arcs = []
    for (x, y), s in zip(BRIDGE_PAIRS, bridge_state):
        if s in (1, 3):
            arcs.append((x, y))
        if s in (2, 3):
            arcs.append((y, x))
    return arcs


def main():
    n = 5
    t0 = time.time()
    n_cand = 0
    n_lam_ge3 = 0
    # counters keyed by (sad_minus, sad_full)
    pair_counts = {}
    lift_violations = []   # (SAT, non-SAT) dumps
    wc3_counter = []       # (UNSAT, UNSAT) dumps
    lam_minus_lt2 = []     # instances where lam(D-e0) < 2 despite lam(D)>=3
    confirm2_examples = [] # a few (UNSAT, SAT) arc dumps for the record

    for core_state in itertools.product(range(3), repeat=3):
        ca = core_arcs(core_state)
        for bridge_state in itertools.product(range(4), repeat=6):
            ba = bridge_arcs(bridge_state)
            arcs_minus = ca + ba             # D - e_0  (a SPLIT digraph)
            arcs_full = arcs_minus + [(P, Q)]  # D
            n_cand += 1

            lam_full = oracle.arc_connectivity(n, arcs_full)
            if lam_full < 3:
                continue
            n_lam_ge3 += 1

            lam_minus = oracle.arc_connectivity(n, arcs_minus)
            if lam_minus < 2:
                lam_minus_lt2.append({"core": core_state, "bridge": bridge_state,
                                      "lam_full": lam_full, "lam_minus": lam_minus,
                                      "arcs_full": arcs_full})

            rm = oracle.check_construction(n, arcs_minus, cross_check=False)
            rf = oracle.check_construction(n, arcs_full, cross_check=False)
            sm, sf = rm["sad"], rf["sad"]

            # escalate anything not plainly (SAT,SAT) with the ILP cross-check
            if not (sm == "SAT" and sf == "SAT"):
                rm = oracle.check_construction(n, arcs_minus, cross_check=True)
                rf = oracle.check_construction(n, arcs_full, cross_check=True)
                sm, sf = rm["sad"], rf["sad"]

            key = (sm, sf)
            pair_counts[key] = pair_counts.get(key, 0) + 1

            if sm == "SAT" and sf != "SAT":
                lift_violations.append({"arcs_full": arcs_full,
                                        "sad_minus": sm, "sad_full": sf,
                                        "lam_full": lam_full,
                                        "cross_full": rf.get("cross_check")})
            if sm == "UNSAT" and sf == "UNSAT":
                wc3_counter.append({"arcs_full": arcs_full,
                                    "lam_full": lam_full,
                                    "lam_minus": lam_minus,
                                    "cross_full": rf.get("cross_check"),
                                    "cross_minus": rm.get("cross_check")})
            if sm == "UNSAT" and sf == "SAT" and len(confirm2_examples) < 5:
                confirm2_examples.append({"arcs_full": arcs_full,
                                          "lam_full": lam_full,
                                          "lam_minus": lam_minus})

    summary = {
        "n": n,
        "candidates_total": n_cand,
        "lambda_full_ge3": n_lam_ge3,
        "pair_counts": {f"{k[0]}|{k[1]}": v for k, v in sorted(pair_counts.items())},
        "lam_minus_lt2_count": len(lam_minus_lt2),
        "lift_violations_count": len(lift_violations),
        "wc3_counterexamples_count": len(wc3_counter),
        "confirm2_examples": confirm2_examples,
        "lam_minus_lt2_sample": lam_minus_lt2[:5],
        "lift_violations": lift_violations[:5],
        "wc3_counterexamples": wc3_counter[:10],
        "elapsed_s": round(time.time() - t0, 1),
    }
    print(json.dumps(summary, indent=2, default=str))


if __name__ == "__main__":
    main()
