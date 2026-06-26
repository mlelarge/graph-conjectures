"""MAX distinct MINIMUM-out-cut ARC-SET census on the alpha=1 core.

Targets H5-DKSTAR-CORE (total #distinct labeled min-out-cut arc-sets <= n^2)
and H6-EPK2 (per-side, i.e. for some root r, #min-out-cut arc-sets with r NOT
in X is <= (n-1)^2).

KILL conditions (any one settles a live hypothesis):
  total > n^2          REFUTES H5-DKSTAR-CORE  (the ledger's own named falsifier)
  per_side > (n-1)^2   KILLS  H6-EPK2 by pigeonhole (no packing enumeration)
INTERMEDIATE:
  n(n-1) < total <= n^2  beats the known tight benchmark n(n-1)
CONFIRM:
  exhaustive max over the FULL generic n=4 mult<=3 layer stays <= n(n-1).

KEY LINEARITY (makes the mult<=3 layer foreground-feasible):
  Fix a simple base D0 with labeled base-arcs a_0..a_{m-1}.  For each proper
  vertex subset X, an arc a=(u,v) CROSSES X iff u in X and v not in X.  This
  crossing PATTERN depends only on X and the base (not on multiplicities).  The
  out-cut SIZE for a multiplicity vector mu is  cut(X) = sum over crossing arcs
  of mu  =  C[X] @ mu, where C is the (#subsets x m) 0/1 crossing matrix.  The
  ARC-SET (the labeled set of base-arcs in delta^+(X)) is exactly the crossing
  PATTERN row C[X] (since all parallels of a base-arc cross together) -- so the
  number of DISTINCT min-out-cut arc-sets = number of DISTINCT crossing rows C[X]
  among the argmin-cut subsets X.  Multiplicities only re-weight which subsets
  are minimum; they never create new arc-set patterns beyond the 2^n-2 rows of C.

  So per base: precompute C (2^n-2 x m) once; for a whole BLOCK of mult vectors
  MU (B x m) compute cuts = MU @ C.T  (B x 2^n-2) with numpy; strong-filter
  (all cuts >= 1), lambda = row-min, and among argmin columns count distinct
  crossing rows -- TOTAL and PER-SIDE (max over roots r of #distinct rows whose
  subset excludes r).

ARM-2: designed parametric probes at n<=16 by direct 2^n cut enumeration.

Every threshold-exceeding witness is self-certified via the oracle
(arc_connectivity, both backends via check_construction cross_check) IN-RUN.
"""
from __future__ import annotations

import json
import math
import os
import subprocess
import sys
import time
from itertools import product

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
import oracle  # noqa: E402


# --------------------------------------------------------------------------- #
#  Crossing matrix for a base (labeled simple-arc list) over proper subsets
# --------------------------------------------------------------------------- #
def crossing_matrix(n, base_arcs):
    """Return (C, subset_masks).

    C[i, j] = 1 iff base_arcs[j]=(u,v) crosses subset i: u in X_i and v not in X_i.
    subset_masks[i] = bitmask of X_i over the 2^n - 2 nonempty proper subsets.
    """
    masks = [m for m in range(1, (1 << n) - 1)]
    m = len(base_arcs)
    C = np.zeros((len(masks), m), dtype=np.int16)
    for i, mask in enumerate(masks):
        for j, (u, v) in enumerate(base_arcs):
            if (mask >> u) & 1 and not ((mask >> v) & 1):
                C[i, j] = 1
    return C, np.array(masks, dtype=np.int64)


def per_side_max(distinct_rows, masks_of_argmin, n):
    """Given the set of distinct crossing rows realized by min-out-cut subsets,
    and for each such distinct row a representative subset mask, return
    max over roots r in 0..n-1 of (# distinct rows whose subset excludes r)."""
    best = 0
    for r in range(n):
        bit = 1 << r
        cnt = 0
        for mask in masks_of_argmin:
            if not (mask & bit):  # r not in X  => head side contains r
                cnt += 1
        if cnt > best:
            best = cnt
    return best


def census_one_base(n, base_arcs, max_mult, C, masks, block=200_000):
    """Sweep ALL mult vectors in {1..max_mult}^m for this base, return the best
    (max total distinct min-out-cut arc-sets, max per-side) and the witness mult
    vector achieving the max total.  Vectorized over blocks of mult vectors."""
    m = len(base_arcs)
    Ct = C.T.astype(np.int32)  # (m, S)
    S = C.shape[0]

    best_total = -1
    best_total_mu = None
    best_total_mask_info = None
    best_per_side = -1
    best_per_side_mu = None

    # Enumerate mult vectors as base-(max_mult) over offset 1..max_mult.
    total_vecs = max_mult ** m
    vals = np.arange(1, max_mult + 1, dtype=np.int32)

    start = 0
    while start < total_vecs:
        stop = min(start + block, total_vecs)
        B = stop - start
        # decode indices start..stop-1 into mult vectors (B x m), digits base max_mult
        idx = np.arange(start, stop, dtype=np.int64)
        MU = np.empty((B, m), dtype=np.int32)
        tmp = idx.copy()
        for j in range(m):
            MU[:, j] = vals[tmp % max_mult]
            tmp //= max_mult
        # cuts: (B x S) = MU (B x m) @ Ct (m x S)
        cuts = MU @ Ct
        # strong filter: every proper subset has out-cut >= 1
        strong = cuts.min(axis=1) >= 1
        if strong.any():
            cs = cuts[strong]
            lam = cs.min(axis=1)  # (Bs,)
            # for each strong instance, the argmin columns are the min-out-cuts
            Bs = cs.shape[0]
            for bi in range(Bs):
                row = cs[bi]
                lv = lam[bi]
                arg = np.nonzero(row == lv)[0]  # subset-indices achieving min
                # distinct crossing rows among these argmin subsets
                patt = C[arg]  # (k x m) crossing patterns
                # uniquify rows
                uniq, first_idx = np.unique(patt, axis=0, return_index=True)
                total = uniq.shape[0]
                # masks of one representative subset per distinct row
                rep_masks = masks[arg[first_idx]]
                ps = per_side_max(uniq, rep_masks.tolist(), n)
                if total > best_total:
                    best_total = total
                    # recover the mult vector
                    gi = np.nonzero(strong)[0][bi]
                    best_total_mu = MU[gi].tolist()
                    best_total_mask_info = (int(lv), int(total), int(ps))
                if ps > best_per_side:
                    best_per_side = ps
                    gi = np.nonzero(strong)[0][bi]
                    best_per_side_mu = MU[gi].tolist()
        start = stop

    return {
        "best_total": best_total,
        "best_total_mu": best_total_mu,
        "best_total_info": best_total_mask_info,
        "best_per_side": best_per_side,
        "best_per_side_mu": best_per_side_mu,
    }


def parse_directg_T(line):
    toks = line.split()
    n = int(toks[0])
    m = int(toks[1])
    flat = list(map(int, toks[2:]))
    arcs = [(flat[2 * i], flat[2 * i + 1]) for i in range(m)]
    return n, arcs


def gen_bases(n):
    out = subprocess.run(
        f"geng -c -d1 {n} | directg -T",
        shell=True, capture_output=True, text=True, check=True,
    ).stdout
    bases = []
    for line in out.splitlines():
        line = line.strip()
        if not line:
            continue
        bn, arcs = parse_directg_T(line)
        bases.append((bn, arcs))
    return bases


def expand_mult(base_arcs, mu):
    arcs = []
    for (u, v), k in zip(base_arcs, mu):
        arcs += [(u, v)] * int(k)
    return arcs


def certify(n, arcs, label):
    """Oracle-certify lambda (both backends) for a threshold-exceeding witness."""
    lam = oracle.arc_connectivity(n, arcs)
    res = oracle.check_construction(n, arcs, name=label, cross_check=True)
    return {
        "label": label,
        "n": n,
        "lambda": lam,
        "sad": res["sad"],
        "cross_check": res.get("cross_check"),
        "m_arcs": res["m_arcs"],
    }


# --------------------------------------------------------------------------- #
#  ARM-1: exhaustive generic census
# --------------------------------------------------------------------------- #
def run_arm1(n, max_mult, time_budget, t0):
    bases = gen_bases(n)
    n2 = n * n
    nn1 = n * (n - 1)
    nm1sq = (n - 1) ** 2
    glob = {
        "n": n,
        "max_mult": max_mult,
        "num_bases": len(bases),
        "n2": n2,
        "n(n-1)": nn1,
        "(n-1)^2": nm1sq,
        "max_total": -1,
        "max_total_witness": None,
        "max_per_side": -1,
        "max_per_side_witness": None,
        "exceed_n2": [],          # total > n^2  (kills H5)
        "exceed_perside": [],     # per_side > (n-1)^2  (kills H6)
        "exceed_nn1": [],         # total > n(n-1)  (beats benchmark)
        "bases_done": 0,
        "coverage_complete": True,
    }
    for bidx, (bn, base_arcs) in enumerate(bases):
        if time.time() - t0 > time_budget:
            glob["coverage_complete"] = False
            glob["_stopped_at_base"] = bidx
            break
        C, masks = crossing_matrix(bn, base_arcs)
        r = census_one_base(bn, base_arcs, max_mult, C, masks)
        glob["bases_done"] += 1
        if r["best_total"] > glob["max_total"]:
            glob["max_total"] = r["best_total"]
            glob["max_total_witness"] = {
                "base_idx": bidx, "base_arcs": base_arcs,
                "mu": r["best_total_mu"], "info(lam,total,perside)": r["best_total_info"],
            }
        if r["best_per_side"] > glob["max_per_side"]:
            glob["max_per_side"] = r["best_per_side"]
            glob["max_per_side_witness"] = {
                "base_idx": bidx, "base_arcs": base_arcs, "mu": r["best_per_side_mu"],
            }
        # threshold checks -> certify
        if r["best_total"] > n2:
            arcs = expand_mult(base_arcs, r["best_total_mu"])
            glob["exceed_n2"].append(
                {"count": r["best_total"], "cert": certify(bn, arcs, f"arm1_b{bidx}_n2")})
        if r["best_per_side"] > nm1sq:
            arcs = expand_mult(base_arcs, r["best_per_side_mu"])
            glob["exceed_perside"].append(
                {"per_side": r["best_per_side"], "cert": certify(bn, arcs, f"arm1_b{bidx}_ps")})
        if nn1 < r["best_total"] <= n2:
            arcs = expand_mult(base_arcs, r["best_total_mu"])
            glob["exceed_nn1"].append(
                {"count": r["best_total"], "cert": certify(bn, arcs, f"arm1_b{bidx}_nn1")})
    return glob


# --------------------------------------------------------------------------- #
#  ARM-2: designed parametric probes (direct 2^n enumeration)
# --------------------------------------------------------------------------- #
def count_min_arcsets(n, arcs):
    """Direct 2^n enumeration: count distinct labeled min-out-cut arc-sets
    (total) and per-side max.  Arc-set = frozenset of (u,v,occurrence-label).
    Since parallels cross together, the arc-set is determined by which base
    (u,v) pairs cross AND their multiplicity -> use the multiset of crossing
    (u,v) with count = number of parallel copies crossing."""
    # label each arc by index so parallels are distinct
    larcs = list(enumerate(arcs))
    best_lam = None
    cuts = {}  # mask -> frozenset of crossing labels
    for mask in range(1, (1 << n) - 1):
        cut = frozenset(
            lab for (lab, (u, v)) in larcs
            if (mask >> u) & 1 and not ((mask >> v) & 1))
        sz = len(cut)
        cuts[mask] = (sz, cut)
        if sz >= 1 and (best_lam is None or sz < best_lam):
            best_lam = sz
    # strong?
    if any(sz == 0 for (sz, _c) in cuts.values()):
        return {"strong": False}
    minmasks = [mask for mask, (sz, _c) in cuts.items() if sz == best_lam]
    distinct = set(cuts[mask][1] for mask in minmasks)
    total = len(distinct)
    # per-side
    best_ps = 0
    for r in range(n):
        bit = 1 << r
        seen = set()
        for mask in minmasks:
            if not (mask & bit):
                seen.add(cuts[mask][1])
        if len(seen) > best_ps:
            best_ps = len(seen)
    return {"strong": True, "lambda": best_lam, "total": total,
            "per_side": best_ps}


def probe(name, n, arcs, glob):
    r = count_min_arcsets(n, arcs)
    n2, nn1, nm1sq = n * n, n * (n - 1), (n - 1) ** 2
    entry = {"name": name, "n": n, "m_arcs": len(arcs)}
    entry.update(r)
    if r.get("strong"):
        entry["thresholds"] = {"n2": n2, "n(n-1)": nn1, "(n-1)^2": nm1sq}
        if r["total"] > n2 or r["per_side"] > nm1sq or r["total"] > nn1:
            entry["cert"] = certify(n, arcs, name)
    glob.append(entry)
    return r


def bidir_two_cycles(n, perm, mults):
    """Two bidirected Hamiltonian cycles on orders id and perm, with (m1,m2)."""
    m1, m2 = mults
    arcs = []
    for i in range(n):
        a, b = i, (i + 1) % n
        arcs += [(a, b)] * m1 + [(b, a)] * m1
    for i in range(n):
        a, b = perm[i], perm[(i + 1) % n]
        arcs += [(a, b)] * m2 + [(b, a)] * m2
    return arcs


def interval_distinct_cycle(n, mults):
    """Graded-mult doubled cycle C_n^2-ish: bidirected cycle with graded mults
    -> the n(n-1) calibration control (consecutive intervals distinct)."""
    arcs = []
    for i in range(n):
        k = mults[i % len(mults)]
        arcs += [(i, (i + 1) % n)] * k + [((i + 1) % n, i)] * k
    return arcs


def bidir_complete_bipartite(a, b, mult=1):
    """Bidirected K_{a,b}: parts {0..a-1},{a..a+b-1}, all cross arcs both ways."""
    n = a + b
    arcs = []
    for u in range(a):
        for v in range(a, a + b):
            arcs += [(u, v)] * mult + [(v, u)] * mult
    return n, arcs


def sunflower_chain(t, mult=2):
    """G20-style: bidirected path 0-1-..-t with doubled arcs + chords back to 0
    making many min cuts share lambda-1 arcs."""
    n = t + 1
    arcs = []
    for i in range(t):
        arcs += [(i, i + 1)] * mult + [(i + 1, i)] * mult
    for i in range(2, t + 1):
        arcs += [(i, 0), (0, i)]
    return n, arcs


def run_arm2():
    import random
    glob = []
    rng = random.Random(12345)
    # (a) two bidirected cycles, designed + random perms
    for n in (5, 6, 7, 8):
        ident = list(range(n))
        rev = list(reversed(range(n)))
        shift = [(i + 1) % n for i in range(n)]
        designed = {"id": ident, "rev": rev, "shift1": shift}
        for pname, perm in designed.items():
            for mults in ((1, 1), (1, 2), (2, 3)):
                probe(f"2cyc_n{n}_{pname}_m{mults}", n,
                      bidir_two_cycles(n, perm, mults), glob)
        for t in range(6):
            perm = list(range(n))
            rng.shuffle(perm)
            for mults in ((1, 1), (1, 2)):
                probe(f"2cyc_n{n}_rand{t}_m{mults}", n,
                      bidir_two_cycles(n, perm, mults), glob)
    # (b) interval_distinct calibration control
    for n in (5, 6, 7, 8, 10, 12):
        probe(f"interval_distinct_n{n}", n,
              interval_distinct_cycle(n, [1, 2, 3]), glob)
    # (c) bidirected K_{2,k}, K_{3,k}
    for b in (2, 3, 4, 5, 6):
        n, arcs = bidir_complete_bipartite(2, b, 1)
        probe(f"bidirK_2_{b}", n, arcs, glob)
        n, arcs = bidir_complete_bipartite(2, b, 2)
        probe(f"bidirK_2_{b}_m2", n, arcs, glob)
    for b in (2, 3, 4, 5):
        n, arcs = bidir_complete_bipartite(3, b, 1)
        probe(f"bidirK_3_{b}", n, arcs, glob)
    # (d) sunflower chains
    for t in (3, 4, 5, 6, 8, 10, 12, 15):
        n, arcs = sunflower_chain(t, 2)
        probe(f"sunflower_t{t}", n, arcs, glob)
    return glob


# --------------------------------------------------------------------------- #
def main():
    t0 = time.time()
    budget = 540.0  # leave margin under the 580 wall

    # ARM-2 first (cheap, designed candidates most likely to exceed n(n-1))
    arm2 = run_arm2()
    arm2_max_total_ratio = max(
        (e["total"] / (e["n"] ** 2) for e in arm2 if e.get("strong")), default=0)
    arm2_max_total_vs_nn1 = max(
        (e["total"] - e["n"] * (e["n"] - 1) for e in arm2 if e.get("strong")),
        default=None)
    arm2_max_perside_ratio = max(
        (e["per_side"] / ((e["n"] - 1) ** 2) for e in arm2 if e.get("strong")),
        default=0)
    arm2_exceed = [e for e in arm2 if e.get("strong") and (
        e["total"] > e["n"] ** 2 or e["per_side"] > (e["n"] - 1) ** 2
        or e["total"] > e["n"] * (e["n"] - 1))]

    # ARM-1 exhaustive: n=3 mult<=4 (small, ~6.4k instances), then n=4 mult<=3
    # (the big layer, ~1.565M instances).  Both share the same wall budget.
    arm1_n3 = run_arm1(3, 4, budget, t0)
    arm1_n4 = run_arm1(4, 3, budget, t0)

    out = {
        "elapsed_s": round(time.time() - t0, 1),
        "ARM1_n3_mult4": arm1_n3,
        "ARM1_n4_mult3": arm1_n4,
        "ARM2_summary": {
            "max_total_ratio_vs_n2": round(arm2_max_total_ratio, 4),
            "max_total_minus_n(n-1)": arm2_max_total_vs_nn1,
            "max_per_side_ratio_vs_(n-1)^2": round(arm2_max_perside_ratio, 4),
            "num_probes": len(arm2),
            "threshold_exceeders": arm2_exceed,
        },
        # top-line verdict scalars
        "max_total_ratio_vs_n2": round(max(
            arm1_n3["max_total"] / arm1_n3["n2"],
            arm1_n4["max_total"] / arm1_n4["n2"],
            arm2_max_total_ratio), 4),
        "max_per_side_ratio_vs_(n-1)^2": round(max(
            arm1_n3["max_per_side"] / arm1_n3["(n-1)^2"],
            arm1_n4["max_per_side"] / arm1_n4["(n-1)^2"],
            arm2_max_perside_ratio), 4),
        "ARM1_n4_max_total_vs_n(n-1)": (arm1_n4["max_total"], arm1_n4["n(n-1)"]),
        "ARM1_n4_max_total_vs_n2": (arm1_n4["max_total"], arm1_n4["n2"]),
        "ARM1_n4_max_per_side_vs_(n-1)^2": (arm1_n4["max_per_side"], arm1_n4["(n-1)^2"]),
        "KILLS_H5_total_gt_n2": bool(arm1_n4["exceed_n2"] or arm1_n3["exceed_n2"]
                                     or any(e["total"] > e["n"]**2 for e in arm2_exceed)),
        "KILLS_H6_perside_gt_(n-1)^2": bool(
            arm1_n4["exceed_perside"] or arm1_n3["exceed_perside"]
            or any(e["per_side"] > (e["n"]-1)**2 for e in arm2_exceed)),
        "BEATS_benchmark_total_gt_n(n-1)": bool(
            arm1_n4["exceed_nn1"] or arm1_n3["exceed_nn1"]
            or any(e["total"] > e["n"]*(e["n"]-1) for e in arm2_exceed)),
    }
    print(json.dumps(out, indent=2, default=str))


if __name__ == "__main__":
    main()
