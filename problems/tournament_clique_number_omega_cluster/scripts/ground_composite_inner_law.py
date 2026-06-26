"""Ground the composite-inner composition law VALUE test (literature-reduction).

Prediction (NSS-style law for COMPOSITE inner H):
  omega_vec(T[H]) = omega_vec(T) + omega_vec(H) - 1.
Tests:
  (a) C3[ C3[C3] ]   order 27, ov(C3)=2, ov(C3[C3])=3  -> pred 4
  (b) AC_7[ C3[C3] ] order 63, ov(AC_7)=3, ov(C3[C3])=3 -> pred 5
  (c) C3[C3]         order 9, control                  -> pred 3

We use the VALIDATED no-K-clique SAT betweenness oracle:
  omega_vec_ge_K_via_sat: SAT => K-clique-free order exists => ov<=K-1;
                          UNSAT => ov>=K.
For pred value V we assert: ov>=V  (no-KV CNF UNSAT) AND ov<=V (no-K(V+1) CNF SAT).

A VALUE exceeding pred for a composite inner KILLS the literature reduction.
Everything wrapped in a hard signal.alarm timeout.
"""
import sys, os, json, time, signal
sys.path.insert(0, os.path.dirname(__file__))
import core
import constructions as C
from law_exact_sweep import lex_compose
from search_4critical_circulant import build_cnf_no_kclique
from pysat.solvers import Cadical153, Minisat22


class Timeout(Exception):
    pass


def _alarm(signum, frame):
    raise Timeout()


def sat_geK(n, arcs, K, secs, solver="cadical"):
    """Return (ge_K, time, nclauses) or None on timeout. ge_K True => ov>=K."""
    cnf, nclq = build_cnf_no_kclique(n, arcs, K)
    signal.signal(signal.SIGALRM, _alarm)
    signal.setitimer(signal.ITIMER_REAL, secs)
    t0 = time.time()
    try:
        S = Minisat22 if solver == "minisat" else Cadical153
        with S(bootstrap_with=cnf.clauses) as m:
            sat = m.solve()
        signal.setitimer(signal.ITIMER_REAL, 0)
        return ((not sat), round(time.time() - t0, 3), nclq)
    except Timeout:
        return None
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)


def circ_arcs(p, g):
    return [(i, j) for i in range(p) for j in range(p)
            if i != j and ((j - i) % p) in g]


def value_via_sat(name, n, arcs, pred, secs):
    """Pin the value by asking ge_V (UNSAT-> ov>=V) and ge_(V+1) (SAT-> ov<=V)."""
    out = {"name": name, "order": n, "pred": pred}
    geV = sat_geK(n, arcs, pred, secs)
    geV1 = sat_geK(n, arcs, pred + 1, secs)
    out["ge_V_raw"] = geV
    out["ge_Vp1_raw"] = geV1
    if geV is None or geV1 is None:
        out["status"] = "timeout"
        out["value"] = None
        out["matches_pred"] = None
        return out
    ge_V = geV[0]          # ov >= pred ?
    ge_Vp1 = geV1[0]       # ov >= pred+1 ?
    out["ov_ge_pred"] = ge_V
    out["ov_ge_pred_plus_1"] = ge_Vp1
    if ge_V and not ge_Vp1:
        out["value"] = pred
        out["matches_pred"] = True
    elif ge_Vp1:
        out["value"] = f">={pred+1}"
        out["matches_pred"] = False   # VALUE EXCEEDS pred -> KILL
    else:
        out["value"] = f"<{pred}"
        out["matches_pred"] = False
    return out


def main():
    t0 = time.time()
    SECS = 600
    res = {"tests": []}

    C3 = C.directed_C3()
    assert core.omega_vec(*C3) == 2
    # inner H = C3[C3], order 9
    nH, aH = lex_compose(C3[0], C3[1], C3[0], C3[1])
    assert core.is_tournament(nH, aH)
    ovH = core.omega_vec(nH, aH)   # exact, order 9
    print(f"H=C3[C3] order={nH} ov_exact={ovH}", flush=True)
    res["H_C3C3"] = {"order": nH, "ov_exact": ovH}

    # (c) control: C3[C3] value (exact already, but also SAT cross-check)
    rc = value_via_sat("C3[C3]_control", nH, aH, 3, SECS)
    rc["ov_exact"] = ovH
    res["tests"].append(rc)
    print("(c)", json.dumps(rc), flush=True)

    # (a) C3[ C3[C3] ] order 27, pred 4
    n_a, a_a = lex_compose(C3[0], C3[1], nH, aH)
    assert core.is_tournament(n_a, a_a)
    print(f"(a) C3[C3[C3]] order={n_a}", flush=True)
    ra = value_via_sat("C3[C3[C3]]", n_a, a_a, 4, SECS)
    # exact bb cross-check on order 27 (reachable)
    try:
        signal.signal(signal.SIGALRM, _alarm)
        signal.setitimer(signal.ITIMER_REAL, SECS)
        ra["ov_exact_bb"] = core.omega_vec_bb(n_a, a_a, ub=5)
        signal.setitimer(signal.ITIMER_REAL, 0)
    except Timeout:
        ra["ov_exact_bb"] = "timeout"
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
    res["tests"].append(ra)
    print("(a)", json.dumps(ra), flush=True)

    # (b) AC_7[ C3[C3] ] order 63, pred 5.  AC_7 = Cay(Z/7,{1,2,4}), ov=3
    nAC, gAC = 7, {1, 2, 4}
    aAC = circ_arcs(nAC, gAC)
    assert core.is_tournament(nAC, aAC)
    ovAC = core.omega_vec(nAC, aAC)
    print(f"AC_7 ov_exact={ovAC}", flush=True)
    res["AC7"] = {"order": nAC, "ov_exact": ovAC, "g": sorted(gAC)}
    n_b, a_b = lex_compose(nAC, aAC, nH, aH)
    assert core.is_tournament(n_b, a_b)
    print(f"(b) AC_7[C3[C3]] order={n_b}", flush=True)
    rb = value_via_sat("AC7[C3[C3]]", n_b, a_b, 5, SECS)
    res["tests"].append(rb)
    print("(b)", json.dumps(rb), flush=True)

    res["elapsed_s"] = round(time.time() - t0, 2)
    dp = os.path.join(os.path.dirname(__file__), "..", "data",
                      "composite_inner_law.json")
    with open(os.path.abspath(dp), "w") as f:
        json.dump(res, f, indent=2)
    print("\n=== SUMMARY ===", flush=True)
    print(json.dumps(res, indent=2), flush=True)


if __name__ == "__main__":
    main()
