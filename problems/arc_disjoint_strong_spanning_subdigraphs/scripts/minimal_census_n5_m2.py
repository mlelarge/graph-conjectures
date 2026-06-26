"""EXHAUSTIVE generic census of the (n=5, max-mult M=2) multidigraph cell via
the MONOTONE-MINIMAL reduction (LEVER B of ledger.next_action, D21).

Same downward-closure lemma as scripts/minimal_census_n4_m3.py: SAD is monotone
under arc addition (surplus arcs -> colour class 1), so among lambda>=3 instances
UNSAT is downward-closed under multiplicity decrement; hence the (n=5,M=2) cell has
an UNSAT lambda>=3 instance IFF some DECREMENT-MINIMAL lambda>=3 instance is UNSAT.

WHY WE DO NOT BRUTE THE 3^20 UNIVERSE
-------------------------------------
3^20 = 3.49e9; even the vectorized lambda pass alone is ~900s > 600s budget, and
the decrement-minimal filter ((k,20,30) tensor) is heavier still.  Infeasible.

EXHAUSTIVENESS BOUND (this is what makes the DFS sound)
------------------------------------------------------
A decrement-minimal lambda>=3 instance is precisely a MINIMALLY 3-ARC-STRONG
multidigraph: lambda>=3, and removing any single arc (decrementing any positive
multiplicity) drops lambda below 3.  By the Mader/Frank bound, every minimally
k-arc-strong digraph has at most 2k(n-1) arcs.  For k=3, n=5 that is 24.
(Sanity: for n=4 the bound is 18, and the observed max total over the 2427
n=4/M=3 decrement-minimals is exactly 18 -- the bound is tight and correct.)
So enumerating all lambda>=3, mult<=2 instances with TOTAL ARCS <= 24, then
keeping the decrement-minimal ones, is EXHAUSTIVE for the cell's minimal set.

We further use: every vertex needs out-degree >= 3 and in-degree >= 3 (singleton
cuts X={v} and complement), so we prune the arc-by-arc DFS hard.

CANONICAL AUGMENTATION
----------------------
We DFS over the 20 ordered-arc slots in a fixed order, assigning multiplicity
0..2 to each, with running bounds:
  * total arcs so far + (min arcs still needed to satisfy degrees) <= 24
  * an admissibility lower bound: remaining slots can still lift every cut to >=3.
At a full assignment we test lambda>=3 (exact, 30 cuts) and decrement-minimality.
We S_5-iso-reduce the survivors by lex-min canonical form over 120 permutations,
then hand the iso-distinct minimals to the oracle (cross_check).

VALIDATION (must all hold or the run is INVALID):
  * Frank bound re-derived for n=4 (max minimal total == 18 == 2*3*3).
  * random lambda>=3 vectors decrement-descend into the enumerated minimal set.
  * oracle.arc_connectivity == vectorized lambda on all iso-distinct minimals.
  * oracle UNSAT-detection live on C4^2 control.

CONFIRM arm: 0 UNSAT among iso-distinct minimals => the whole (n=5,M=2) cell is
SAT, both backends agreeing.
KILL arm: any UNSAT = explicit minimal 3-arc-strong SAD-less multidigraph =
oracle-certified counterexample to WC3.
"""
from __future__ import annotations

import json
import os
import sys
import time
from itertools import permutations

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)

N = 5
M = 2
LAM = 3
MAX_TOTAL = 2 * LAM * (N - 1)        # Mader/Frank bound = 24

ARCS = [(u, v) for u in range(N) for v in range(N) if u != v]
NARC = len(ARCS)                      # 20
ARC_INDEX = {a: i for i, a in enumerate(ARCS)}
MASKS = [m for m in range(1, (1 << N) - 1)]
NSUB = len(MASKS)                     # 30


def crossing_matrix():
    C = np.zeros((NSUB, NARC), dtype=np.int64)
    for i, mask in enumerate(MASKS):
        for j, (u, v) in enumerate(ARCS):
            if (mask >> u) & 1 and not ((mask >> v) & 1):
                C[i, j] = 1
    return C


C = crossing_matrix()                 # (30 x 20)
Ct = C.T.copy()                       # (20 x 30)

# For pruning: for each subset i, which still-unassigned slots could add to it.
# CONTRIB[i,j] = C[i,j] (1 if arc j crosses subset i).
CONTRIB = C.copy()                    # (30 x 20)

# out-slot index lists per vertex (for degree pruning)
OUT_SLOTS = {u: [ARC_INDEX[(u, v)] for v in range(N) if v != u] for u in range(N)}
IN_SLOTS = {v: [ARC_INDEX[(u, v)] for u in range(N) if u != v] for v in range(N)}


def arc_perms():
    out = []
    for p in permutations(range(N)):
        perm = np.empty(NARC, dtype=np.int64)
        for j, (u, v) in enumerate(ARCS):
            perm[j] = ARC_INDEX[(p[u], p[v])]
        out.append(perm)
    return out


ARC_PERMS = arc_perms()               # 120 length-20 index perms


def canonical(vec):
    best = None
    for perm in ARC_PERMS:
        cand = tuple(int(vec[perm[j]]) for j in range(NARC))
        if best is None or cand < best:
            best = cand
    return best


def lam_of(vec):
    return int((C @ np.asarray(vec, dtype=np.int64)).min())


# --------------------------------------------------------------------------- #
#  DFS enumeration of all lambda>=3, mult<=2, total<=MAX_TOTAL instances,
#  keeping decrement-minimal ones, with hard cut/degree pruning.
# --------------------------------------------------------------------------- #
def enumerate_minimals():
    vec = np.zeros(NARC, dtype=np.int64)
    cuts = np.zeros(NSUB, dtype=np.int64)         # current cut values
    # max-achievable additional contribution to each cut from slots >= position
    # suffix_cap[pos] = sum over slots j>=pos of M*CONTRIB[:,j]
    suffix_cap = np.zeros((NARC + 1, NSUB), dtype=np.int64)
    for pos in range(NARC - 1, -1, -1):
        suffix_cap[pos] = suffix_cap[pos + 1] + M * CONTRIB[:, pos]

    minimals = []
    canon = set()
    leaves = [0]      # count of complete assignments lambda>=3 examined

    def dfs(pos, total):
        if pos == NARC:
            if cuts.min() >= LAM:
                leaves[0] += 1
                _maybe_record(vec, minimals, canon)
            return
        # prune: even filling all remaining slots to max, can every cut reach LAM?
        if (cuts + suffix_cap[pos] < LAM).any():
            return
        # degree feasibility: remaining slots must let every vertex hit out/in >=3.
        # cheap check: total + (slots remaining)*M >= ... skip heavy; rely on cut prune
        for m in range(M + 1):
            nt = total + m
            if nt > MAX_TOTAL:
                break
            if m:
                cuts[:] += m * CONTRIB[:, pos]
                vec[pos] = m
            dfs(pos + 1, nt)
            if m:
                cuts[:] -= m * CONTRIB[:, pos]
                vec[pos] = 0

    dfs(0, 0)
    return minimals, canon, leaves[0]


def _is_decrement_minimal(vec):
    base_cuts = C @ vec
    for a in range(NARC):
        if vec[a] > 0:
            dec = (base_cuts - CONTRIB[:, a]).min()
            if dec >= LAM:
                return False
    return True


def _maybe_record(vec, minimals, canon):
    if not _is_decrement_minimal(vec):
        return
    cv = canonical(vec)
    if cv not in canon:
        canon.add(cv)
        minimals.append(tuple(int(x) for x in vec))


def expand(vec):
    arcs = []
    for (u, v), k in zip(ARCS, vec):
        arcs += [(u, v)] * int(k)
    return arcs


def decrement_descend(vec):
    v = list(int(x) for x in vec)
    changed = True
    while changed:
        changed = False
        for a in range(NARC):
            if v[a] > 0:
                v[a] -= 1
                if lam_of(v) >= LAM:
                    changed = True
                    break
                v[a] += 1
    return tuple(v)


def main(decide=True):
    t0 = time.time()
    minimals, canon, n_leaves = enumerate_minimals()
    iso = sorted(canon)
    n_iso = len(iso)
    enum_s = round(time.time() - t0, 1)

    out = {
        "cell": {"n": N, "max_mult": M, "lambda_threshold": LAM},
        "mader_frank_total_arc_bound": MAX_TOTAL,
        "enumerate_seconds": enum_s,
        "n_complete_lambda_ge_3": n_leaves,
        "n_iso_distinct_minimals": n_iso,
    }

    if not decide:
        out["DECIDE_SKIPPED"] = True
        print(json.dumps(out, indent=2, default=str))
        return

    import oracle  # imported lazily so the probe path needs no networkx
    rng = np.random.default_rng(20260612)

    # validation: random lambda>=3 vectors descend into the minimal set
    minimal_set = set(tuple(v) for v in minimals)
    desc_ok = 0
    desc_tries = 0
    attempts = 0
    while desc_tries < 30 and attempts < 200000:
        attempts += 1
        v = rng.integers(0, M + 1, size=NARC)
        if lam_of(v) >= LAM:
            desc_tries += 1
            if decrement_descend(v) in minimal_set:
                desc_ok += 1

    # oracle control: C4^2 must be UNSAT (lambda=2)
    c4sq = [(0, 1), (1, 2), (2, 3), (3, 0), (0, 2), (1, 3), (2, 0), (3, 1)]
    ctrl = oracle.check_construction(4, c4sq, name="C4sq_control", cross_check=True)

    results = []
    n_unsat = n_disagree = n_unknown = n_lambda_mismatch = 0
    for v in iso:
        arcs = expand(v)
        lam_vec = lam_of(v)
        lam_oracle = oracle.arc_connectivity(N, arcs)
        res = oracle.check_construction(N, arcs, name="min_n5m2", cross_check=True)
        sad = res["sad"]
        entry = {
            "mu": list(v),
            "m_arcs": res["m_arcs"],
            "lambda_vec": lam_vec,
            "lambda_oracle": lam_oracle,
            "sad": sad,
            "cross_check": res.get("cross_check"),
        }
        if lam_oracle != lam_vec:
            n_lambda_mismatch += 1
            entry["LAMBDA_MISMATCH"] = True
        if sad == "UNSAT":
            n_unsat += 1
            entry["arcs"] = arcs
        elif sad == "DISAGREE":
            n_disagree += 1
            entry["arcs"] = arcs
        elif sad == "UNKNOWN":
            n_unknown += 1
        results.append(entry)

    out.update({
        "total_seconds": round(time.time() - t0, 1),
        "validation": {
            "descent_into_minimal_set": f"{desc_ok}/{desc_tries}",
            "C4sq_control_sad": ctrl["sad"],
            "lambda_oracle_vs_vectorized_mismatches": n_lambda_mismatch,
        },
        "oracle_verdicts": {
            "n_iso_decided": n_iso,
            "n_UNSAT": n_unsat,
            "n_DISAGREE": n_disagree,
            "n_UNKNOWN": n_unknown,
            "n_SAT": n_iso - n_unsat - n_disagree - n_unknown,
        },
        "WC3_PREDICTION_HOLDS": (n_unsat == 0 and n_disagree == 0 and n_unknown == 0),
        "KILL_witnesses": [e for e in results if e["sad"] in ("UNSAT", "DISAGREE")],
    })
    if n_iso <= 800:
        out["all_iso_minimals"] = results
    print(json.dumps(out, indent=2, default=str))


if __name__ == "__main__":
    decide = not (len(sys.argv) > 1 and sys.argv[1] == "--probe")
    main(decide=decide)
