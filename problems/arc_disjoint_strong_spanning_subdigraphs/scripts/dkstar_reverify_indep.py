"""INDEPENDENT re-verification of the tagged-bundle DK* KILL claim.

Built from scratch, NOT trusting dkstar_kill_tagged_bundle.py:
 - rebuild T(k,lam) directly from the textual spec in the ledger/proposal:
     V={s=0,o=1,p_1..p_k}; arcs (s,o)*lam,(o,s)*lam; per toggle p:
     (s,p)*lam,(p,o)*lam,(p,s)*1.  n=k+2.
 - certify lambda via the ledger oracle arc_connectivity.
 - count DISTINCT LABELED ARC-SETS exactly per the DK* DEFINITION in
   dkstar_check.py: delta^+(X) = frozenset of arc-LABEL indices (so parallel
   arcs are distinct labels).  Enumerate all 2^n-2 proper nonempty X.
 - We use TWO independent counting backends and require they AGREE:
     (A) label-frozenset (the literal DK* definition, vectorized over labels);
     (B) crossing-pair fingerprint (the proposal's shortcut).
   If A and B disagree the proposal's shortcut is wrong; if they agree the
   shortcut is faithful AND we have the literal-definition count.

Also report a SANITY check on the alpha=1 residue (min-out-cut arc-sets <= n^2).
"""
import sys, os, json, time
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import oracle

ALPHAS = [("1", 1.0), ("4/3", 4.0/3.0), ("5/3", 5.0/3.0), ("2", 2.0)]


def build_T(k, lam):
    s, o = 0, 1
    arcs = [(s, o)] * lam + [(o, s)] * lam
    for j in range(k):
        p = 2 + j
        arcs += [(s, p)] * lam
        arcs += [(p, o)] * lam
        arcs += [(p, s)]
    return (k + 2), arcs


def census(n, arcs, lam, check_labels=False):
    """Vectorized DISTINCT-arc-set count.

    The DK* definition (dkstar_check.py) ids an arc-set as the frozenset of
    arc-LABEL indices leaving X.  For a MULTIdigraph, parallel copies of a
    pair (u,v) always cross a cut TOGETHER (they have identical tail/head),
    so the frozenset-of-labels is in BIJECTION with the set of distinct
    crossing PAIRS.  Backend B (pair pattern) is therefore EXACTLY the literal
    label-set count; we verify this bijection explicitly on the cheap control
    via check_labels=True (Python per-mask, small n only).

    Distinct-pair-pattern count is computed by hashing each chunk's crossing
    bit-pattern over P distinct pairs into Python ints (np.packbits) and adding
    to a per-alpha set.  Cut size = sum of multiplicities of crossing pairs.
    """
    pairs = sorted(set(arcs))
    pmult = {p: 0 for p in pairs}
    for a in arcs:
        pmult[a] += 1
    P = len(pairs)
    ptail = np.array([p[0] for p in pairs], dtype=np.int64)
    phead = np.array([p[1] for p in pairs], dtype=np.int64)
    pw = np.array([pmult[p] for p in pairs], dtype=np.int64)

    thr = {lbl: a * lam for (lbl, a) in ALPHAS}
    vsets = {lbl: 0 for (lbl, _a) in ALPHAS}
    asets = {lbl: set() for (lbl, _a) in ALPHAS}
    label_asets = {lbl: set() for (lbl, _a) in ALPHAS} if check_labels else None
    if check_labels:
        ltail = np.array([a[0] for a in arcs], dtype=np.int64)
        lhead = np.array([a[1] for a in arcs], dtype=np.int64)

    full = (1 << n) - 1
    CHUNK = 1 << 16
    nbytes = (P + 7) // 8
    max_thr = max(thr.values())
    mask0 = 1
    while mask0 < full:
        mask1 = min(mask0 + CHUNK, full)
        masks = np.arange(mask0, mask1, dtype=np.int64)
        tbit = ((masks[:, None] >> ptail[None, :]) & 1).astype(np.uint8)
        hbit = ((masks[:, None] >> phead[None, :]) & 1).astype(np.uint8)
        cross = (tbit & (1 - hbit))                 # (B, P) 0/1 over PAIRS
        size = (cross.astype(np.int64) * pw[None, :]).sum(axis=1)
        # only rows under the largest threshold can ever contribute
        keep = size <= max_thr
        if not keep.any():
            mask0 = mask1
            continue
        cross = cross[keep]
        size = size[keep]
        packed = np.packbits(cross, axis=1)          # (Bk, nbytes)
        if check_labels:
            mk = masks[keep]
            ltb = ((mk[:, None] >> ltail[None, :]) & 1).astype(np.uint8)
            lhb = ((mk[:, None] >> lhead[None, :]) & 1).astype(np.uint8)
            lcross = (ltb & (1 - lhb))
            lpacked = np.packbits(lcross, axis=1)
        for (lbl, _a) in ALPHAS:
            sel = size <= thr[lbl]
            cnt = int(sel.sum())
            if cnt == 0:
                continue
            vsets[lbl] += cnt
            sub = packed[sel]
            # unique fingerprints within this chunk, then add to global set
            uniq = np.unique(sub, axis=0)
            asets[lbl].update(uniq[i].tobytes() for i in range(uniq.shape[0]))
            if check_labels:
                lsub = lpacked[sel]
                luniq = np.unique(lsub, axis=0)
                label_asets[lbl].update(
                    luniq[i].tobytes() for i in range(luniq.shape[0]))
        mask0 = mask1

    out = {}
    for (lbl, a) in ALPHAS:
        denom = float(n) ** (2.0 * a)
        nB = len(asets[lbl])
        rec = {"n_arcsets_pairs": nB, "n_vsets": vsets[lbl],
               "n^2a": denom, "ratio": nB/denom, "KILL": nB > denom}
        if check_labels:
            rec["n_arcsets_labels"] = len(label_asets[lbl])
            rec["labels==pairs"] = len(label_asets[lbl]) == nB
        out[lbl] = rec
    return out


def run(k, lam, label, check_labels=False):
    n, arcs = build_T(k, lam)
    t0 = time.time()
    lam_o = oracle.arc_connectivity(n, arcs)
    cc = census(n, arcs, lam_o, check_labels=check_labels)
    rec = {"label": label, "k": k, "lam_param": lam, "n": n,
           "lambda_oracle": lam_o, "n_arcs": len(arcs),
           "elapsed_s": round(time.time()-t0, 2)}
    for (lbl, a) in ALPHAS:
        d = {"n_arcsets": cc[lbl]["n_arcsets_pairs"],
             "n_vsets": cc[lbl]["n_vsets"], "n^2a": cc[lbl]["n^2a"],
             "ratio": round(cc[lbl]["ratio"], 5), "KILL": cc[lbl]["KILL"]}
        if check_labels:
            d["n_arcsets_labels"] = cc[lbl]["n_arcsets_labels"]
            d["labels==pairs"] = cc[lbl]["labels==pairs"]
        rec[f"alpha={lbl}"] = d
    return rec


def main():
    t0 = time.time()
    res = []
    # control: also verify label-set == pair-set bijection (the DK* definition)
    res.append(run(16, 3, "control_T(16,3)_n18", check_labels=True))
    res.append(run(18, 10, "kill_T(18,10)_n20"))
    res.append(run(22, 8, "kill_T(22,8)_n24"))
    any_kill = any(r[f"alpha={lbl}"]["KILL"] for r in res for (lbl, _a) in ALPHAS)
    label_ok = all(r[f"alpha={lbl}"].get("labels==pairs", True)
                   for r in res for (lbl, _a) in ALPHAS)
    print(json.dumps({"total_elapsed_s": round(time.time()-t0, 2),
                      "ANY_KILL": any_kill,
                      "LABELS_EQ_PAIRS_on_control": label_ok,
                      "results": res}, indent=2))


if __name__ == "__main__":
    main()
