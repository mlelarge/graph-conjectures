"""GROUND H21 at inner-ov=5 on C3[AC_7[AC_7]] (order 147).

X = AC_7[AC_7] = lex_compose(AC_7, AC_7), AC_7 = Cay(Z/7,{1,2,4}), order 49,
ov(X)=5 PROVEN (P19/P20).  H21 predicts: there EXISTS an optimal order sigma of X
(backedge clique exactly 5) such that the potential-sum merged order on C3[X]
(key(c,v)=e(c)+d_sigma(v), e=(1,1,2), tie-break (d,c,pos) etc.) has backedge
clique EXACTLY 6 = ov(X)+1.  With the PROVEN lex lower bound ov(C3[X])>=6, a
merged clique of 6 PINS ov(C3[X])=6 EXACTLY -- the second explicit ov=6
tournament (order 147), SAT-free.

Reuses attack_class from ground_potential_sum_c3 (the H21 mechanism, exact
clique via internal bitmask + core.omega_of_order cross-check), exactly as the
k=4 strike on C3[H1*]/C3[H2*] did.

PASS = some optimal sigma reaches merged clique 6.
FAIL = every enumerated sigma overshoots to merged clique >=7 within the budget.
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import core  # noqa: E402
from ground_potential_sum_c3 import attack_class, lex_compose  # noqa: E402
from lexlib import AC, is_tournament  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")


def main():
    seconds = float(sys.argv[1]) if len(sys.argv) > 1 else 560.0
    sigma_cap = int(sys.argv[2]) if len(sys.argv) > 2 else None
    t0 = time.time()

    # (1) build X = AC_7[AC_7]
    n1, a1 = AC(7, [1, 2, 4])
    assert is_tournament(n1, a1), "AC_7 not a tournament"
    nX, arcsX = lex_compose(n1, a1, n1, a1)
    assert nX == 49, nX
    assert is_tournament(nX, arcsX), "X=AC_7[AC_7] not a tournament"
    print(f"X = AC_7[AC_7]: order {nX}, arcs {len(arcsX)} "
          f"(expect {nX*(nX-1)//2})", flush=True)

    # (2) HARD SANITY: ov(X) must be 5 (the proven record). We confirm the
    #     UPPER bound ov(X)<=5 by exhibiting an order of X with backedge
    #     clique 5 (the lower bound >=5 is the proven no-K5 UNSAT, not re-run
    #     here -- attack_class's DFS only enumerates clique-<=5 orders, so if
    #     no clique-5 order existed the run would itself be vacuous).
    #     attack_class with k=5 enumerates optimal (clique==5) sigmas of X.

    # (3)+(4)+(5) run the H21 mechanism on C3[X] (order 147), stop at first
    #     success (merged clique == 6), cross-check witness with core.
    deadline = t0 + seconds
    print(f"running attack_class(X, k=5) on C3[X] order 147, "
          f"budget={seconds:.0f}s, sigma_cap={sigma_cap}", flush=True)
    res = attack_class(nX, arcsX, k=5, sigma_cap=sigma_cap, deadline=deadline)

    out = {
        "leg": "ground_h21_k5_c3_ac7ac7",
        "inner": "AC_7[AC_7]", "inner_order": nX, "inner_ov_claimed": 5,
        "C3_inner_order": 3 * nX, "k": 5, "target_merged_clique": 6,
        "result": res,
        "elapsed_seconds": round(time.time() - t0, 2),
    }
    out["verdict"] = (
        "H21 CONFIRMED at inner-ov=5: some optimal sigma reaches merged clique 6 "
        "= ov+1; ov(C3[AC_7[AC_7]])=6 PINNED (lex lower 6 + this upper 6)"
        if res["pass"] else
        "NO confirmation within budget: every enumerated sigma overshoots "
        "(merged clique >=7)"
    )
    path = os.path.join(DATA, "ground_h21_k5_c3_ac7ac7.json")
    json.dump(out, open(path, "w"), indent=1)

    print("--- RESULT ---", flush=True)
    print(f"pass={res['pass']} sigmas_tried={res['sigmas_tried']} "
          f"min_merged_clique={res['min_merged_clique']} "
          f"hist={res['merged_clique_histogram']} "
          f"timed_out={res['timed_out']} "
          f"exhausted={res['exhausted_over_optimal_sigmas']}", flush=True)
    if res["pass"]:
        w = res["witness"]
        print(f"WITNESS tiebreak={w['tiebreak_rule']} "
              f"merged_clique_core_verified={w['merged_clique_core_verified']}",
              flush=True)
        # explicit independent recheck of the 147-vertex witness order
        nC, arcsC = lex_compose(3, [(0, 1), (1, 2), (2, 0)], nX, arcsX)
        assert nC == 147
        wcheck = core.omega_of_order(nC, arcsC, w["merged_order"])
        print(f"INDEP core.omega_of_order on the 147-vertex order = {wcheck} "
              f"(must be 6)", flush=True)
    print("VERDICT:", out["verdict"], flush=True)
    print(f"WROTE {path}", flush=True)


if __name__ == "__main__":
    main()
