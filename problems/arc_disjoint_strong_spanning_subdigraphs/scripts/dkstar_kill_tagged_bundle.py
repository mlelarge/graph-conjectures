"""KILL attempt on H5-DKSTAR via tagged-bundle multidigraph T(k,lambda).

T(k,lam) = dkstar_check.fam_private_arc(k, mult=lam):
  V = {s=0, o=1, p_1..p_k};  n = k+2
  arcs: (s,o)*lam, (o,s)*lam, and per toggle p: (s,p)*lam, (p,o)*lam, (p,s)*1.

Proposal claim: lambda(D)=lam (min cut at X={o}); the private tag arc p->s makes
the map S -> delta^+({o} u S) INJECTIVE, so #distinct bounded-size arc-sets blows
up super-polynomially, KILLING universal DK*(alpha) at alpha=2.

We EXHAUSTIVELY enumerate ALL 2^n - 2 nonempty proper X, compute the labeled
arc-set delta^+(X) (frozenset of arc LABELS so parallel arcs are distinct), and
count distinct arc-sets with |delta^+(X)| <= alpha*lam for alpha in {1,4/3,5/3,2}.
Compare to n^{2*alpha}.

Kill points: T(18,10) n=20 alpha=2 (expect >160000); T(22,8) n=24 alpha=2
(expect >331776).  Control T(16,3) must STAY UNDER bound (reproduce D5).
"""
import sys, os, json, time
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import oracle

ALPHAS = [("1", 1.0), ("4/3", 4.0 / 3.0), ("5/3", 5.0 / 3.0), ("2", 2.0)]


def fam_private_arc(k, mult):
    """Identical to dkstar_check.fam_private_arc."""
    s, o = 0, 1
    arcs = [(s, o)] * mult + [(o, s)] * mult
    for j in range(k):
        p = 2 + j
        arcs += [(s, p)] * mult
        arcs += [(p, o)] * mult
        arcs += [(p, s)]            # private cheap tag arc into s
    return (k + 2), arcs


def arcset_census(n, arcs, lam):
    """Exhaustive over all 2^n-2 proper nonempty X, numpy-vectorized.

    Parallel arcs always cross a cut TOGETHER, so the labeled arc-set
    delta^+(X) is fully determined by the SET of distinct crossing (tail,head)
    PAIRS, and the cut SIZE = sum of multiplicities of those crossing pairs.
    We therefore work with distinct pairs P_0..P_{m-1} (mult w_j) and compute,
    for every mask:
       cross_j = bit(tail_j) set AND bit(head_j) clear
       size    = sum_j w_j * cross_j
       fingerprint = integer with bit j set iff pair j crosses (the arc-set)
    This fingerprint is a faithful labeled-arc-set id (one per distinct crossing
    pair-set), and counting distinct fingerprints among masks with size<=thr is
    EXACTLY #distinct labeled arc-sets.
    """
    # distinct pairs with multiplicities
    pair_mult = {}
    for (u, v) in arcs:
        pair_mult[(u, v)] = pair_mult.get((u, v), 0) + 1
    pairs = list(pair_mult.keys())
    m = len(pairs)
    w = np.array([pair_mult[p] for p in pairs], dtype=np.int64)
    tail = np.array([p[0] for p in pairs], dtype=np.int64)
    head = np.array([p[1] for p in pairs], dtype=np.int64)

    full = (1 << n) - 1
    thr = {lbl: a * lam for (lbl, a) in ALPHAS}
    max_thr = max(thr.values())

    out_accum = {lbl: {"vsets": 0, "asets": set()} for (lbl, _a) in ALPHAS}

    # chunk over masks to bound memory; for each mask compute size + fingerprint
    CHUNK = 1 << 18
    mask0 = 1
    while mask0 < full:
        mask1 = min(mask0 + CHUNK, full)
        masks = np.arange(mask0, mask1, dtype=np.int64)  # shape (B,)
        B = masks.shape[0]
        # tail_set[b, j] = bit tail_j of mask b ;  head_set similarly
        tail_bit = ((masks[:, None] >> tail[None, :]) & 1).astype(np.int64)
        head_bit = ((masks[:, None] >> head[None, :]) & 1).astype(np.int64)
        cross = tail_bit & (1 - head_bit)               # (B, m) 0/1
        size = (cross * w[None, :]).sum(axis=1)          # (B,)
        # fingerprint over pairs; pack into 1 or 2 int64 words (<=62 bits each)
        # so the (fp_lo, fp_hi) pair is a faithful labeled-arc-set id.
        lo_m = min(m, 62)
        powers_lo = (np.int64(1) << np.arange(lo_m, dtype=np.int64))
        fp_lo = (cross[:, :lo_m] * powers_lo[None, :]).sum(axis=1)
        if m > 62:
            hi_m = m - 62
            powers_hi = (np.int64(1) << np.arange(hi_m, dtype=np.int64))
            fp_hi = (cross[:, 62:] * powers_hi[None, :]).sum(axis=1)
        else:
            fp_hi = None
        for (lbl, _a) in ALPHAS:
            sel = size <= thr[lbl]
            cnt = int(sel.sum())
            out_accum[lbl]["vsets"] += cnt
            if cnt:
                if fp_hi is None:
                    out_accum[lbl]["asets"].update(fp_lo[sel].tolist())
                else:
                    lo_s = fp_lo[sel].tolist()
                    hi_s = fp_hi[sel].tolist()
                    out_accum[lbl]["asets"].update(zip(lo_s, hi_s))
        mask0 = mask1

    out = {}
    for (lbl, a) in ALPHAS:
        denom = float(n) ** (2.0 * a)
        nstar = len(out_accum[lbl]["asets"])
        out[lbl] = {"n_vsets": out_accum[lbl]["vsets"], "n_arcsets": nstar,
                    "denom_n^2a": denom,
                    "ratio_arcset": nstar / denom,
                    "kill": nstar > denom}
    return out


def run_instance(k, lam, label):
    n, arcs = fam_private_arc(k, lam)
    t0 = time.time()
    lam_oracle = oracle.arc_connectivity(n, arcs)
    cc = arcset_census(n, arcs, lam_oracle)
    rec = {"label": label, "k": k, "lam_param": lam, "n": n,
           "lambda_oracle": lam_oracle, "n_arcs": len(arcs),
           "elapsed_s": round(time.time() - t0, 2)}
    for (lbl, a) in ALPHAS:
        rec[f"alpha={lbl}"] = {
            "n_arcsets": cc[lbl]["n_arcsets"],
            "n_vsets": cc[lbl]["n_vsets"],
            "n^2a": cc[lbl]["denom_n^2a"],
            "ratio": round(cc[lbl]["ratio_arcset"], 5),
            "KILL": cc[lbl]["kill"],
        }
    return rec


def main():
    t0 = time.time()
    results = []
    # Control first (cheapest, reproduces D5 under-bound)
    results.append(run_instance(16, 3, "control_T(16,3)"))
    # Kill point (i): T(18,10) n=20
    results.append(run_instance(18, 10, "kill_T(18,10)_n20"))
    # Kill point (ii): T(22,8) n=24
    results.append(run_instance(22, 8, "kill_T(22,8)_n24"))

    any_kill = any(rec[f"alpha={lbl}"]["KILL"]
                   for rec in results for (lbl, _a) in ALPHAS)
    out = {"total_elapsed_s": round(time.time() - t0, 2),
           "results": results,
           "ANY_DKSTAR_KILL": any_kill}
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
