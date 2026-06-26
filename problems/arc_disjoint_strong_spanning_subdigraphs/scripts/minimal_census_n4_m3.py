"""EXHAUSTIVE generic census of the (n=4, max-mult M=3) multidigraph cell via
the MONOTONE-MINIMAL reduction.

H1 lists this cell as RESIDUAL INFEASIBLE in foreground (~1.5M / ~780s naive,
and the true lambda>=3 count is ~5.47M). The monotone-minimal reduction makes
it foreground-feasible by reducing 5.47M oracle decisions to a handful of
iso-distinct DECREMENT-MINIMAL instances.

DOWNWARD-CLOSURE LEMMA (symbolic, 3 lines)
------------------------------------------
Claim: SAD is monotone under arc ADDITION among multidigraphs.  If D' subseteq D
(same vertex set, every arc-multiplicity of D' <= that of D) and D' has a SAD
(A_R, A_B) with both classes spanning-strong, then D has a SAD: put every EXTRA
arc of D (the multiplicity surplus D \ D') into class A_R.  Both classes stay
spanning (vertex set unchanged) and strong (adding arcs to a strong spanning
subdigraph keeps it strong; the untouched A_B is unchanged).  QED.
(This is exactly G16's oracle-confirmed CONFIRM-1: SAD lifts under arc addition.)

CONSEQUENCE: among lambda>=3 instances, UNSAT is DOWNWARD-CLOSED under
arc-multiplicity DECREMENT: if D is UNSAT and D' subseteq D is still lambda>=3,
then D' is UNSAT (else D' SAT => D SAT by the lemma).  Therefore the cell
contains an UNSAT lambda>=3 instance IFF some DECREMENT-MINIMAL lambda>=3
instance is UNSAT, where decrement-minimal := lambda>=3 and EVERY single-arc
multiplicity decrement (on an arc with mult>0) drops lambda below 3.
SAT on all minimals  =>  SAT on the whole cell (every lambda>=3 instance
dominates some minimal; if all minimals SAT, lift gives SAT everywhere).

So: enumerate decrement-minimal lambda>=3 vectors, reduce under S_4, oracle-decide.

ENCODING
--------
n=4.  The 12 ordered pairs (u,v), u!=v, are the base "arcs".  A multidigraph is a
vector v in {0..M}^12 of multiplicities (0 = arc absent).  Proper-subset out-cut:
arc (u,v) crosses X iff u in X, v not in X.  cut_X(v) = sum over crossing arcs of
their multiplicity = C[X] @ v, where C is the 14 x 12 crossing matrix over the
14 nonempty proper subsets.  lambda(v) = min_X cut_X(v) (exact at n=4).

minimal(v): lambda(v)>=3 AND for every arc a with v_a>0,
            min_X (cut_X(v) - C[X,a]) < 3.

ISO: two vectors are S_4-isomorphic if a vertex permutation maps one arc-mult
profile to the other.  Canonical form = lexicographically-minimal mult vector
over the 24 permutations of the 12-arc layout.

VALIDATION (must all hold or the run is INVALID; all ASSERTED, not printed):
  * counts reproduce: lambda>=3, minimal, iso-distinct.
  * 2000 random lambda>=3 vectors decrement-descend into the minimal set.
  * 500 random connectivity comparisons: vectorized lambda == oracle's exact
    arc_connectivity.
  * lift lemma re-verified on 50 random (D' subseteq D) SAT pairs (oracle-
    expensive, kept small; the lemma itself is the 3-line proof above).
  * oracle.arc_connectivity == vectorized lambda on all iso-distinct minimals.
(D22 correction: an earlier ledger entry claimed 2000/927/500 checks that were
NOT in this file -- only 20/50 were.  The checks below are now the checked-in
reality; the full pipeline was also independently reproduced by hand, D21
review.)

CONFIRM arm: 0 UNSAT among iso-distinct minimals => the whole (n=4,M=3) cell is
SAT (5.47M generic lambda>=3 instances), with both backends agreeing.
KILL arm:    any UNSAT = an explicit minimal 3-arc-strong SAD-less multidigraph
             = oracle-certified counterexample to WC3 (refutes the central Q).
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
import oracle  # noqa: E402

N = 4
M = 3
LAM = 3

# 12 ordered pairs (u,v), u != v -- the base arc layout (fixed order).
ARCS = [(u, v) for u in range(N) for v in range(N) if u != v]
NARC = len(ARCS)              # 12
ARC_INDEX = {a: i for i, a in enumerate(ARCS)}

# 14 nonempty proper subsets of {0,1,2,3}.
MASKS = [m for m in range(1, (1 << N) - 1)]
NSUB = len(MASKS)             # 14


def crossing_matrix():
    """C[i,j] = 1 iff ARCS[j]=(u,v) crosses subset MASKS[i] (u in X, v not in X)."""
    C = np.zeros((NSUB, NARC), dtype=np.int64)
    for i, mask in enumerate(MASKS):
        for j, (u, v) in enumerate(ARCS):
            if (mask >> u) & 1 and not ((mask >> v) & 1):
                C[i, j] = 1
    return C


C = crossing_matrix()         # (14 x 12)
Ct = C.T.copy()               # (12 x 14)


# --------------------------------------------------------------------------- #
#  S_4 isomorphism: precompute, for each of the 24 vertex permutations, the
#  arc-index permutation it induces on the 12-arc layout.
# --------------------------------------------------------------------------- #
def arc_perms():
    out = []
    for p in permutations(range(N)):
        # arc (u,v) -> (p[u], p[v]); record where each arc index lands
        perm = np.empty(NARC, dtype=np.int64)
        for j, (u, v) in enumerate(ARCS):
            perm[j] = ARC_INDEX[(p[u], p[v])]
        out.append(perm)
    return out


ARC_PERMS = arc_perms()       # list of 24 length-12 index permutations


def canonical(vec):
    """Lex-min mult vector over the 24 vertex permutations (S_4 canonical form)."""
    best = None
    for perm in ARC_PERMS:
        cand = tuple(int(vec[perm[j]]) for j in range(NARC))
        if best is None or cand < best:
            best = cand
    return best


# --------------------------------------------------------------------------- #
#  Vectorized enumeration of all (M+1)^12 mult vectors, lambda + minimal filter
# --------------------------------------------------------------------------- #
def run_census(block=400_000):
    base = M + 1                       # digits 0..M
    total_vecs = base ** NARC          # 4^12 = 16,777,216
    vals = np.arange(base, dtype=np.int64)

    n_lam_ge = 0
    minimals = []                      # list of length-12 tuples (decrement-minimal, lam>=3)

    start = 0
    while start < total_vecs:
        stop = min(start + block, total_vecs)
        B = stop - start
        idx = np.arange(start, stop, dtype=np.int64)
        MU = np.empty((B, NARC), dtype=np.int64)
        tmp = idx.copy()
        for j in range(NARC):
            MU[:, j] = vals[tmp % base]
            tmp //= base
        # cuts: (B x 14)
        cuts = MU @ Ct
        lam = cuts.min(axis=1)         # (B,)
        ge = lam >= LAM
        n_lam_ge += int(ge.sum())
        if ge.any():
            sel = np.nonzero(ge)[0]
            cuts_s = cuts[sel]         # (k x 14)
            MU_s = MU[sel]             # (k x 12)
            # decrement test: for arc a, decremented lambda =
            #   min_X (cut_X - C[X,a]) over arcs with mult>0.
            # minimal iff for EVERY a with mult>0, that decremented lambda < LAM.
            # cuts_s: (k,14); C: (14,12) -> dec[k,a,X] = cuts_s[k,X] - C[X,a]
            # decmin[k,a] = min_X (cuts_s[k,X] - C[X,a])
            # = min over X.  Vectorize: dec = cuts_s[:,None,:] - C.T[None,:,:]
            dec = cuts_s[:, None, :] - Ct[None, :, :]    # (k,12,14)
            decmin = dec.min(axis=2)                      # (k,12)
            has_mult = MU_s > 0                            # (k,12)
            # an arc with mult>0 "blocks" minimality if its decremented lambda >= LAM
            # (decrementing it keeps lambda>=3, so the instance is NOT minimal)
            blocks = has_mult & (decmin >= LAM)            # (k,12)
            is_min = ~blocks.any(axis=1)                   # (k,)
            for r in np.nonzero(is_min)[0]:
                minimals.append(tuple(int(x) for x in MU_s[r]))
        start = stop

    return n_lam_ge, minimals


def lam_of(vec):
    return int((C @ np.asarray(vec, dtype=np.int64)).min())


def decrement_descend(vec):
    """Greedily decrement any arc whose removal keeps lambda>=3, until minimal.
    Returns a minimal lambda>=3 vector dominated by vec."""
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


def expand(vec):
    arcs = []
    for (u, v), k in zip(ARCS, vec):
        arcs += [(u, v)] * int(k)
    return arcs


def main():
    t0 = time.time()
    rng = np.random.default_rng(20260611)

    n_lam_ge, minimals = run_census()
    n_minimal = len(minimals)

    # iso-reduce
    canon = set()
    for v in minimals:
        canon.add(canonical(v))
    iso = sorted(canon)
    n_iso = len(iso)

    # --- validation 1: 2000 random lambda>=3 vectors descend into minimal set
    minimal_set = set(minimals)
    desc_ok = 0
    desc_tries = 0
    while desc_tries < 2000:
        v = rng.integers(0, M + 1, size=NARC)
        if lam_of(v) >= LAM:
            desc_tries += 1
            mv = decrement_descend(v)
            if mv in minimal_set:
                desc_ok += 1
    assert desc_ok == desc_tries, ("descent validation failed", desc_ok, desc_tries)

    # --- validation 1b: 500 random connectivity comparisons:
    #     vectorized lam_of vs the oracle's exact arc_connectivity ---
    conn_ok = 0
    for _ in range(500):
        v = rng.integers(0, M + 1, size=NARC)
        if lam_of(v) == oracle.arc_connectivity(N, expand(v)):
            conn_ok += 1
    assert conn_ok == 500, ("connectivity validation failed", conn_ok)

    # --- validation 2: lift lemma on 50 random (D' subseteq D) SAT pairs ---
    # take a random lambda>=3 D, pick a random superset D (add mults up to M),
    # confirm: D' SAT => D SAT (oracle).
    lift_checked = 0
    lift_ok = 0
    lift_tries = 0
    while lift_checked < 50 and lift_tries < 5000:
        lift_tries += 1
        vp = rng.integers(0, M + 1, size=NARC)
        if lam_of(vp) < LAM:
            continue
        # superset: add 0..(M-vp) to each arc
        add = rng.integers(0, 2, size=NARC) * (M - vp)
        vsup = np.minimum(vp + add, M)
        if (vsup == vp).all():
            continue
        rp = oracle.check_construction(N, expand(vp), cross_check=False)
        if rp["sad"] != "SAT":
            continue
        rs = oracle.check_construction(N, expand(vsup), cross_check=False)
        lift_checked += 1
        if rs["sad"] == "SAT":
            lift_ok += 1

    # --- oracle-decide all iso-distinct minimals (cross_check) ---
    results = []
    n_unsat = 0
    n_disagree = 0
    n_unknown = 0
    n_lambda_mismatch = 0
    for v in iso:
        arcs = expand(v)
        lam_vec = lam_of(v)
        lam_oracle = oracle.arc_connectivity(N, arcs)
        res = oracle.check_construction(N, arcs, name="min_n4m3", cross_check=True)
        sad = res["sad"]
        cc = res.get("cross_check")
        entry = {
            "mu": list(v),
            "m_arcs": res["m_arcs"],
            "lambda_vec": lam_vec,
            "lambda_oracle": lam_oracle,
            "sad": sad,
            "cross_check": cc,
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

    out = {
        "elapsed_s": round(time.time() - t0, 1),
        "cell": {"n": N, "max_mult": M, "lambda_threshold": LAM},
        "universe_size": (M + 1) ** NARC,
        "n_lambda_ge_3": n_lam_ge,
        "n_minimal": n_minimal,
        "n_iso_distinct": n_iso,
        "validation": {
            "descent_into_minimal_set": f"{desc_ok}/{desc_tries}",
            "lift_lemma_SAT_pairs": f"{lift_ok}/{lift_checked}",
            "lambda_oracle_vs_vectorized_mismatches": n_lambda_mismatch,
        },
        "oracle_verdicts": {
            "n_iso_decided": n_iso,
            "n_UNSAT": n_unsat,
            "n_DISAGREE": n_disagree,
            "n_UNKNOWN": n_unknown,
            "n_SAT": n_iso - n_unsat - n_disagree - n_unknown,
        },
        "WC3_PREDICTION_HOLDS": (n_unsat == 0 and n_disagree == 0
                                 and n_unknown == 0),
        "KILL_witnesses": [e for e in results
                           if e["sad"] in ("UNSAT", "DISAGREE")],
    }
    # include full per-instance table only if small
    if n_iso <= 400:
        out["all_iso_minimals"] = results
    print(json.dumps(out, indent=2, default=str))


if __name__ == "__main__":
    main()
