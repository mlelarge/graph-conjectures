"""H9: BST-penalty beta(T)=bstOmega(T)-omegaVec(T) on the CLOSURE-OUTSIDE
tww<=1 stratum (the generic case located by H8).

next_action (ledger): push beta to n=9 on the OUTSIDE subset of tww<=1 only.
Decisive test:
  * beta stays bounded (beta<=g(omegaVec))  => Conj 3.16 hence Conj 3.12 at
    tww<=1 via the paper's Thm 3.14 + Geniet-Thomasse 3.15 chain (citation-self
    -contained PROVE route survives on the generic stratum).
  * some closure-outside family pushes beta>=2 => the paper's preferred BST
    route provably CANNOT prove 3.12 (sharp barrier).

Pipeline per iso-class (gentourng):
  tww(<=1 filter)  ->  in_closure (skip IN-closure)  ->  omega_vec, bst_omega
  -> beta.  beta is informative at every n (sidesteps Neumann-Lara chiVec>=4).

Usage: .venv/bin/python scripts/h9_beta_outside_closure.py <n> [--tww-max W]
"""
from __future__ import annotations
import argparse, json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import core
import oracle
from collections import Counter
from h8_closure_membership import in_closure
from bst_penalty import bst_omega


def run(n, tww_max=1):
    scanned = 0
    kept_tww = 0
    outside = 0
    beta_hist = Counter()                 # beta -> count (outside only)
    omega_to_beta = {}                    # omega_vec -> {beta:count}
    omega_to_max_bst = {}                 # omega_vec -> max bst_omega
    cell_dist = Counter()                 # (tww,omega,chi) outside
    max_beta = -1
    argmax = None
    beta_ge2_examples = []
    for (_n, arcs) in oracle._all_tournaments(n):
        scanned += 1
        w = core.tww(n, arcs, ub=tww_max + 1)
        if w > tww_max:
            continue
        kept_tww += 1
        if in_closure(n, arcs):
            continue
        outside += 1
        ov = core.omega_vec(n, arcs)
        bo = bst_omega(n, arcs, lb=ov)
        assert bo >= ov, f"SOUNDNESS VIOLATION n={n}: bst={bo}<ov={ov} arcs={arcs}"
        b = bo - ov
        beta_hist[b] += 1
        omega_to_beta.setdefault(ov, Counter())[b] += 1
        omega_to_max_bst[ov] = max(omega_to_max_bst.get(ov, 0), bo)
        ch = core.chi_vec(n, arcs)
        cell_dist[(w, ov, ch)] += 1
        if b >= 2 and len(beta_ge2_examples) < 30:
            beta_ge2_examples.append({"tww": w, "omega_vec": ov, "bst_omega": bo,
                                      "chi_vec": ch, "beta": b, "arcs": list(arcs)})
        if b > max_beta:
            max_beta = b
            argmax = {"tww": w, "omega_vec": ov, "bst_omega": bo, "beta": b,
                      "arcs": list(arcs)}
    return {
        "n": n, "tww_max": tww_max,
        "n_scanned": scanned, "kept_tww<=max": kept_tww,
        "num_outside_closure": outside,
        "beta_histogram_outside": dict(sorted(beta_hist.items())),
        "max_beta_outside": max_beta,
        "omega_to_beta_outside": {str(k): dict(sorted(v.items()))
                                  for k, v in sorted(omega_to_beta.items())},
        "omega_to_max_bstOmega_outside": {str(k): v
                                          for k, v in sorted(omega_to_max_bst.items())},
        "outside_cell_dist_tww_omega_chi": {f"{k[0]},{k[1]},{k[2]}": v
                                            for k, v in sorted(cell_dist.items())},
        "argmax_beta": argmax,
        "beta_ge2_examples": beta_ge2_examples,
        "loose_form_holds": (max_beta <= 1),
    }


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("n", type=int)
    ap.add_argument("--tww-max", type=int, default=1)
    a = ap.parse_args()
    print(json.dumps(run(a.n, a.tww_max), indent=2, default=str))
