"""hardcase_trichotomy.py -- ground the BJY2004 HARD-CASE TRICHOTOMY proposal
for CRUX-A.

PROPOSAL OBJECTS (verbatim from the proposal):
  K := the INDUCED kernel D<V_2>  (proposal calls it D^bullet<V_2>; this is the
       SAME object the G9 graveyard entry analyses -- the bare induced
       subdigraph, NO contracted vertex r). BJY2004 (2-arc-strong semicomplete
       => SAD, unique exception S4) is applied to K.
  D^bullet := the genuine chord CONTRACTION (delete e_0=(p,q), identify p,q->r),
       the object L-exist actually quantifies over (3-arc-strong by team/21 S1.3).

T1 (trichotomy bookkeeping, the KILL test):
  Over an exhaustive labelled enumeration of 3-arc-strong (1,0)-near-split hosts
  in cells (|V1|,|V2|) in {(2,3),(3,3)}, the count of hosts with
     SAD(K) = UNSAT  AND  lambda(K) >= 2  AND  K not isomorphic to S4
  is predicted to be ZERO. ANY nonzero count means BJY2004 (as the proposal
  states it) or the object bookkeeping is WRONG -> kills the reduction.

We tally the full trichotomy:
  - lambda(K) <= 1                          (proposal hard-case (i))
  - K isomorphic to S4 (= C4^2)             (proposal hard-case (ii))
  - lambda(K) >= 2 and K !~ S4 and SAD(K)=SAT   (the BJY2004 "easy" case)
  - lambda(K) >= 2 and K !~ S4 and SAD(K)=UNSAT (the FORBIDDEN bucket; T1 KILL)
"""
from __future__ import annotations

import itertools
import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_CODE = os.path.join(os.path.dirname(_HERE), "code")
for p in (_CODE, _HERE):
    if p not in sys.path:
        sys.path.insert(0, p)

import oracle  # noqa: E402
from generators.near_split import (  # noqa: E402
    enumerate_construction_A,
    is_one_zero_near_split,
)


def _S4_arcs():
    # S4 = C4^2: square of the directed 4-cycle on {0,1,2,3}
    a = []
    for i in range(4):
        a.append((i, (i + 1) % 4))
        a.append((i, (i + 2) % 4))
    return sorted(a)


_S4 = _S4_arcs()


def _is_iso_S4(k, arcs):
    """Brute-force directed isomorphism test of (k, arcs) against S4=C4^2."""
    if k != 4:
        return False
    A = set(arcs)
    if len(A) != len(_S4):
        return False
    for perm in itertools.permutations(range(4)):
        mapped = set((perm[u], perm[v]) for (u, v) in A)
        if mapped == set(_S4):
            return True
    return False


def induced_kernel(inst):
    """K := D<V_2> -- the induced subdigraph on V_2 (NO contraction, no r).
    Relabel V_2 to 0..|V2|-1. Parallel arcs cannot occur in a SIMPLE host, but
    we preserve any duplicates defensively (the oracle takes a list)."""
    V2 = sorted(inst.V2)
    idx = {v: i for i, v in enumerate(V2)}
    arcs = []
    for (x, y) in inst.arcs:
        if x in idx and y in idx:
            arcs.append((idx[x], idx[y]))
    return len(V2), arcs


def run(v1_size, v2_size, orient_cap, bridge_cap, max_hosts=0):
    n_hosts = 0
    n_3arc = 0
    # trichotomy buckets
    b_lam_le1 = 0
    b_S4 = 0
    b_easy_sat = 0
    b_forbidden = 0          # lambda(K)>=2, K!~S4, SAD(K)=UNSAT  <-- T1 KILL
    forbidden_examples = []
    lamK_hist = {}
    sadK_hist = {}

    for inst in enumerate_construction_A(
        v1_size, v2_size,
        cap_per_v2_orientation=orient_cap,
        bridge_cap_per_pair=bridge_cap,
    ):
        if max_hosts and n_hosts >= max_hosts:
            break
        D = inst.build()
        ok, _ = is_one_zero_near_split(D, list(inst.V1), list(inst.V2))
        if not ok:
            continue
        n_hosts += 1
        lamD = oracle.arc_connectivity(inst.n, list(inst.arcs))
        if lamD < 3:
            continue
        n_3arc += 1

        k, Karcs = induced_kernel(inst)
        lamK = oracle.arc_connectivity(k, Karcs)
        lamK_hist[lamK] = lamK_hist.get(lamK, 0) + 1

        isS4 = _is_iso_S4(k, Karcs)

        if lamK <= 1:
            b_lam_le1 += 1
            continue
        if isS4:
            b_S4 += 1
            continue
        # lambda(K) >= 2 and K !~ S4: BJY2004 predicts SAD(K)=SAT
        res = oracle.check_construction(k, Karcs, cross_check=True)
        sad = res["sad"]
        sadK_hist[sad] = sadK_hist.get(sad, 0) + 1
        if sad == "SAT":
            b_easy_sat += 1
        else:
            b_forbidden += 1
            if len(forbidden_examples) < 8:
                forbidden_examples.append({
                    "host": inst.name, "lambdaD": lamD, "k": k,
                    "lambdaK": lamK, "sadK": sad, "K_arcs": Karcs,
                })

    return {
        "cell": f"(|V1|,|V2|)=({v1_size},{v2_size})",
        "n_nearsplit_hosts": n_hosts,
        "n_3arcstrong_hosts": n_3arc,
        "lambdaK_hist": {str(a): b for a, b in sorted(lamK_hist.items())},
        "trichotomy": {
            "hard_i_lambdaK_le_1": b_lam_le1,
            "hard_ii_K_iso_S4": b_S4,
            "easy_lambdaK_ge2_notS4_SAD_SAT": b_easy_sat,
            "FORBIDDEN_lambdaK_ge2_notS4_SAD_UNSAT": b_forbidden,
        },
        "T1_KILL_count": b_forbidden,
        "sadK_hist_easy_branch": sadK_hist,
        "forbidden_examples": forbidden_examples,
    }


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("v1", type=int)
    ap.add_argument("v2", type=int)
    ap.add_argument("--orient-cap", type=int, default=4096)
    ap.add_argument("--bridge-cap", type=int, default=100000)
    ap.add_argument("--max-hosts", type=int, default=0)
    args = ap.parse_args()
    print(json.dumps(run(args.v1, args.v2, args.orient_cap, args.bridge_cap,
                         args.max_hosts), indent=2))


if __name__ == "__main__":
    main()
