"""STRIKE (next_action lever 2): H21 potential-sum mechanism at k=4 on the
PROVEN P22 objects C3[H1*], C3[H2*] (order 75), where ov(C3[H*])=5 is PROVEN.

H21 PREDICTION at k=4: for H with ov(H)=4 there EXISTS an optimal order sigma
of H (backedge clique exactly 4) and one of the 6 fixed tie-breaks such that the
potential-sum merged order key(c,v)=e(c)+d_sigma(v), e=(1,1,2), on C3[H] has
backedge clique EXACTLY 5 (= ov(H)+1 = ov(C3[H*]), the PROVEN value).

This is the FIRST k=4 test of the H21 mechanism on objects where the target
value is proven (unlike C3[QR_19] where ov in {5,6} is undecided and the prior
k=4 probe was negative over 49214 sigmas).

Outcome semantics:
  PASS  (some sigma+tiebreak hits merged clique 5)  -> first k>3 confirmation of
        H21; the merged-order mechanism is NOT k=3-only.
  FAIL  (every enumerated sigma gives merged clique >5, i.e. 6, over the budget)
        -> evidence H21 is k=3-only (refocuses H19/H21). Records min_merged and
        the merged-clique histogram.

We reuse attack_class from ground_potential_sum_c3 (proven lex lower bound gives
merged clique >= ov(C3[H])=5 for EVERY order, so merged clique==5 is exactly the
minimum possible; merged clique 6 = the dic-style overshoot).

DFS stops at the FIRST success (so PASS is cheap if it exists); FAIL is bounded
by sigma_cap / deadline (non-exhaustive over the ~25! optimal-sigma space).
"""
import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lexlib import AC, is_tournament  # noqa: E402
from ground_potential_sum_c3 import attack_class  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")

OBJECTS = {
    "H1star": [1, 2, 3, 4, 5, 6, 7, 9, 10, 12, 14, 17],
    "H2star": [1, 2, 3, 4, 5, 6, 7, 9, 11, 12, 15, 17],
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--obj", choices=list(OBJECTS) + ["both"], default="both")
    ap.add_argument("--sigma-cap", type=int, default=200000)
    ap.add_argument("--seconds", type=float, default=520.0)
    args = ap.parse_args()

    t0 = time.time()
    targets = list(OBJECTS) if args.obj == "both" else [args.obj]
    out = {"leg": "strike_h21_k4_hstar", "k": 4, "target_merged_clique": 5,
           "objects": {}, "args": vars(args)}

    # split the time budget across objects; stop early on first PASS
    n_obj = len(targets)
    for ti, name in enumerate(targets):
        g = OBJECTS[name]
        n, arcs = AC(25, g)
        assert is_tournament(n, arcs)
        remaining = args.seconds - (time.time() - t0)
        budget = remaining / (n_obj - ti)
        deadline = time.time() + budget
        print(f"[{name}] g={g} order=25 -> C3[H*] order 75, budget={budget:.0f}s",
              flush=True)
        res = attack_class(n, arcs, k=4, sigma_cap=args.sigma_cap,
                           deadline=deadline)
        out["objects"][name] = res
        print(f"[{name}] pass={res['pass']} sigmas_tried={res['sigmas_tried']} "
              f"min_merged_clique={res['min_merged_clique']} "
              f"hist={res['merged_clique_histogram']} "
              f"timed_out={res['timed_out']} "
              f"exhausted={res['exhausted_over_optimal_sigmas']}", flush=True)
        if res["pass"]:
            w = res.get("witness", {})
            print(f"[{name}] PASS witness: tiebreak={w.get('tiebreak_rule')} "
                  f"merged_clique_core_verified="
                  f"{w.get('merged_clique_core_verified')}", flush=True)
            break  # a single confirmation settles the qualitative question

    any_pass = any(r["pass"] for r in out["objects"].values())
    out["any_pass"] = any_pass
    out["verdict"] = ("H21 CONFIRMED at k=4 (some optimal sigma reaches merged "
                      "clique 5 = ov+1)" if any_pass else
                      "NO k=4 confirmation within budget (every enumerated sigma "
                      "overshoots to merged clique 6); evidence H21 is k=3-only")
    out["elapsed_seconds"] = round(time.time() - t0, 2)
    path = os.path.join(DATA, "strike_h21_k4_hstar.json")
    json.dump(out, open(path, "w"), indent=1)
    print(f"WROTE {path}", flush=True)
    print("VERDICT:", out["verdict"], flush=True)


if __name__ == "__main__":
    main()
