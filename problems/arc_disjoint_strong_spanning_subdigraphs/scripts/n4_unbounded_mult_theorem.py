"""UNBOUNDED-MULTIPLICITY WC3 theorem at n<=4 (CRUX-B extension).

CLAIM (universal, scope = ALL multidigraphs on n<=4):
  Every lambda^arc >= 3 multidigraph on n<=4 vertices, with ARBITRARY arc
  multiplicities, admits a SAD.

REDUCTION TO THE FINITE D21 CENSUS via a MULT->3 DECREMENT LEMMA + the
downward-closure (SAD-monotone-under-arc-addition) lemma.

  MULT-4 DECREMENT LEMMA (symbolic).  Let D be a multidigraph with
  lambda^arc(D) >= 3 and let a be an arc of multiplicity m >= 4.  Then
  D - a (one copy of a removed) still has lambda^arc >= 3.
  Proof.  Take any out-cut X = delta^+(X).
    * If a crosses X (tail(a) in X, head(a) notin X), then ALL m copies of a
      cross X, so |delta^+(X)| >= m >= 4; removing one copy leaves >= m-1 >= 3.
    * If a does not cross X, the cut is unchanged, hence still >= lambda >= 3.
  Min over X stays >= 3.  QED.

  CONSEQUENCE.  A DECREMENT-MINIMAL lambda>=3 multidigraph on n<=4 (one where
  every single-copy decrement drops lambda below 3) has EVERY multiplicity <= 3:
  any arc of mult >= 4 could be decremented (lemma), contradicting minimality.
  So the decrement-minimal set of the WHOLE unbounded class is EXACTLY the
  decrement-minimal set of the (n<=4, M<=3) cell -- already enumerated and
  oracle-decided in D21 (2427 labelled / 116 S_4-iso, ALL SAD=SAT).

  By DOWNWARD-CLOSURE (SAD lifts under arc addition: surplus arcs go in colour
  class 1, both classes stay spanning-strong), greedy decrement from ANY
  lambda>=3 n<=4 multidigraph terminates in that SAT minimal set, so the whole
  INFINITE class is SAT.  QED for n<=4.

This script GROUNDS the reduction (it does NOT re-prove the lemma -- the lemma is
the 6-line argument above):
  (1) LEMMA INSTANCE CHECK: random high-mult lambda>=3 vectors; for every arc of
      mult>=4 assert (a) lambda stays >=3 after one decrement (exhaustive 14-cut
      eval) AND (b) the symbolic reason: every cut CONTAINING the arc has size
      >= its multiplicity.
  (2) COVERAGE: greedy-descend each high-mult sample to a decrement-minimal;
      assert all mults <=3 and its S_4-canonical form lies in the freshly
      recomputed D21 minimal set (re-run run_census in-process; assert 2427/116).
  (3) ORACLE: cross_check SAD on high-mult samples + random members of the 116;
      assert all SAT, 0 DISAGREE.
  (4) n=3 arm: same lemma + descent, n=3 census recomputed in-process.

KILL: any lambda>=3 n<=4 instance oracle-UNSAT; OR a decrement-minimal with an
arc of mult>=4; OR a descended minimal NOT in the enumerated set.
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
import minimal_census_n4_m3 as cen4  # noqa: E402


# --------------------------------------------------------------------------- #
#  Generic n-vertex multidigraph machinery (mirrors cen4 but parametric in N)  #
# --------------------------------------------------------------------------- #
def build_layout(N):
    arcs = [(u, v) for u in range(N) for v in range(N) if u != v]
    masks = [m for m in range(1, (1 << N) - 1)]
    C = np.zeros((len(masks), len(arcs)), dtype=np.int64)
    for i, mask in enumerate(masks):
        for j, (u, v) in enumerate(arcs):
            if (mask >> u) & 1 and not ((mask >> v) & 1):
                C[i, j] = 1
    return arcs, masks, C


def lam_of(C, vec):
    return int((C @ np.asarray(vec, dtype=np.int64)).min())


def expand(arcs, vec):
    out = []
    for (u, v), k in zip(arcs, vec):
        out += [(u, v)] * int(k)
    return out


def descend_to_minimal(C, vec, LAM=3):
    """Greedily decrement any arc whose removal keeps lambda>=LAM, until minimal."""
    v = [int(x) for x in vec]
    changed = True
    while changed:
        changed = False
        for a in range(len(v)):
            if v[a] > 0:
                v[a] -= 1
                if lam_of(C, v) >= LAM:
                    changed = True
                    break
                v[a] += 1
    return tuple(v)


def canonical_generic(arcs, vec):
    N = max(max(u, v) for u, v in arcs) + 1
    arc_index = {a: i for i, a in enumerate(arcs)}
    best = None
    for p in permutations(range(N)):
        cand = tuple(int(vec[arc_index[(p[arcs[j][0]], p[arcs[j][1]])]])
                     for j in range(len(arcs)))
        if best is None or cand < best:
            best = cand
    return best


# --------------------------------------------------------------------------- #
def lemma_instance_check(N, arcs, C, rng, n_samples=2000, maxmult=8, LAM=3):
    """For random lambda>=LAM mult-vectors with entries 0..maxmult, every arc of
    mult>=4: (a) one decrement keeps lambda>=LAM (exhaustive cut eval);
    (b) symbolic reason: every cut CONTAINING the arc has size >= its mult."""
    narc = len(arcs)
    checked = 0
    arcs_ge4_checked = 0
    tries = 0
    fail_decrement = []
    fail_symbolic = []
    while checked < n_samples and tries < n_samples * 80:
        tries += 1
        v = rng.integers(0, maxmult + 1, size=narc)
        if lam_of(C, v) < LAM:
            continue
        # need at least one arc of mult>=4 to exercise the lemma
        if not (v >= 4).any():
            continue
        checked += 1
        cuts = C @ v  # (nsub,)
        for a in np.nonzero(v >= 4)[0]:
            arcs_ge4_checked += 1
            # (a) decrement test
            v2 = v.copy()
            v2[a] -= 1
            if lam_of(C, v2) < LAM:
                fail_decrement.append((tuple(int(x) for x in v), int(a)))
            # (b) symbolic: every cut where arc a crosses has size >= v[a]
            cross = C[:, a] == 1
            if cross.any() and int(cuts[cross].min()) < int(v[a]):
                fail_symbolic.append((tuple(int(x) for x in v), int(a),
                                      int(cuts[cross].min()), int(v[a])))
    return {
        "samples_with_mult_ge4": checked,
        "arcs_mult_ge4_checked": arcs_ge4_checked,
        "fail_decrement": fail_decrement,
        "fail_symbolic": fail_symbolic,
    }


def coverage_check(N, arcs, C, minimal_set, rng, n_samples=2000,
                   maxmult=8, LAM=3):
    """Greedy-descend random high-mult lambda>=LAM vectors; assert minimal has all
    mults<=3 and its canonical form is in minimal_set.  Returns sampled minimals
    + offenders."""
    narc = len(arcs)
    canon_minimal = {canonical_generic(arcs, m) for m in minimal_set}
    checked = 0
    tries = 0
    mult_gt3_minimal = []      # KILL: minimal with an arc of mult>=4
    not_in_set = []            # KILL: descended minimal not enumerated
    descended_canon = set()
    while checked < n_samples and tries < n_samples * 80:
        tries += 1
        v = rng.integers(0, maxmult + 1, size=narc)
        if lam_of(C, v) < LAM:
            continue
        checked += 1
        mv = descend_to_minimal(C, v, LAM)
        if max(mv) > 3:
            mult_gt3_minimal.append(mv)
        cm = canonical_generic(arcs, mv)
        descended_canon.add(cm)
        if cm not in canon_minimal:
            not_in_set.append(mv)
    return {
        "samples_descended": checked,
        "distinct_descended_canon": len(descended_canon),
        "n_iso_in_census": len(canon_minimal),
        "fail_minimal_mult_ge4": mult_gt3_minimal,
        "fail_not_in_census": not_in_set,
    }


def oracle_arm(N, arcs, C, minimal_iso, rng, n_high=25, n_members=10,
               maxmult=8, LAM=3):
    """cross_check SAD on high-mult samples + random members of the iso set."""
    narc = len(arcs)
    results = []
    n_unsat = n_disagree = n_unknown = 0
    # high-mult sampled instances
    got = 0
    tries = 0
    while got < n_high and tries < n_high * 200:
        tries += 1
        v = rng.integers(0, maxmult + 1, size=narc)
        if lam_of(C, v) < LAM:
            continue
        if not (v >= 4).any():
            continue
        got += 1
        arcs_e = expand(arcs, v)
        res = oracle.check_construction(N, arcs_e, name="n%d_highmult" % N,
                                        cross_check=True)
        sad = res["sad"]
        cc = res.get("cross_check")
        if sad == "UNSAT":
            n_unsat += 1
        elif sad == "DISAGREE":
            n_disagree += 1
        elif sad == "UNKNOWN":
            n_unknown += 1
        results.append({"kind": "highmult", "mu": [int(x) for x in v],
                        "lambda": res["arc_strong"], "sad": sad,
                        "cross_check": cc})
    # random members of the enumerated iso minimal set
    members = list(minimal_iso)
    rng.shuffle(members)
    for v in members[:n_members]:
        arcs_e = expand(arcs, v)
        res = oracle.check_construction(N, arcs_e, name="n%d_member" % N,
                                        cross_check=True)
        sad = res["sad"]
        cc = res.get("cross_check")
        if sad == "UNSAT":
            n_unsat += 1
        elif sad == "DISAGREE":
            n_disagree += 1
        elif sad == "UNKNOWN":
            n_unknown += 1
        results.append({"kind": "member", "mu": list(v),
                        "lambda": res["arc_strong"], "sad": sad,
                        "cross_check": cc})
    return {
        "n_oracle_calls": len(results),
        "n_UNSAT": n_unsat,
        "n_DISAGREE": n_disagree,
        "n_UNKNOWN": n_unknown,
        "n_SAT": len(results) - n_unsat - n_disagree - n_unknown,
        "kill_witnesses": [r for r in results
                           if r["sad"] in ("UNSAT", "DISAGREE", "UNKNOWN")],
    }


# --------------------------------------------------------------------------- #
def n3_census(LAM=3, M=3):
    """Recompute the n=3, M<=3 decrement-minimal set in-process (tiny)."""
    arcs, masks, C = build_layout(3)
    narc = len(arcs)
    base = M + 1
    total = base ** narc
    minimals = []
    n_lam_ge = 0
    for idx in range(total):
        v = np.empty(narc, dtype=np.int64)
        t = idx
        for j in range(narc):
            v[j] = t % base
            t //= base
        if lam_of(C, v) < LAM:
            continue
        n_lam_ge += 1
        # minimal?  every arc with mult>0 decrement drops lambda below LAM
        is_min = True
        for a in range(narc):
            if v[a] > 0:
                v2 = v.copy()
                v2[a] -= 1
                if lam_of(C, v2) >= LAM:
                    is_min = False
                    break
        if is_min:
            minimals.append(tuple(int(x) for x in v))
    iso = sorted({canonical_generic(arcs, m) for m in minimals})
    return arcs, masks, C, minimals, iso, n_lam_ge


# --------------------------------------------------------------------------- #
def main():
    t0 = time.time()
    rng = np.random.default_rng(20260612)
    report = {}

    # ============================ n = 4 arm ================================ #
    arcs4, masks4, C4 = build_layout(4)
    # sanity: this layout matches cen4's
    assert arcs4 == cen4.ARCS, "arc layout mismatch with minimal_census_n4_m3"

    # recompute the D21 census in-process; assert 2427 / 116
    n_lam_ge4, minimals4 = cen4.run_census()
    iso4 = sorted({cen4.canonical(v) for v in minimals4})
    report["n4_census"] = {
        "n_lambda_ge_3": n_lam_ge4,
        "n_minimal_labelled": len(minimals4),
        "n_iso_distinct": len(iso4),
    }
    assert len(minimals4) == 2427, ("n4 labelled minimal count", len(minimals4))
    assert len(iso4) == 116, ("n4 iso count", len(iso4))
    # every census minimal has all mults <= 3 (D21 cell is M<=3 by construction;
    # confirms no mult>=4 minimal exists -- the lemma's conclusion at n=4)
    assert all(max(m) <= 3 for m in minimals4), "n4 minimal mult>3 found"

    rng4 = np.random.default_rng(101)
    lem4 = lemma_instance_check(4, arcs4, C4, rng4,
                                n_samples=2000, maxmult=8)
    report["n4_lemma_instance"] = lem4
    assert not lem4["fail_decrement"], ("n4 decrement lemma FAIL",
                                        lem4["fail_decrement"][:3])
    assert not lem4["fail_symbolic"], ("n4 symbolic-reason FAIL",
                                       lem4["fail_symbolic"][:3])
    assert lem4["arcs_mult_ge4_checked"] > 0, "n4: no mult>=4 arcs exercised"

    rng4b = np.random.default_rng(202)
    cov4 = coverage_check(4, arcs4, C4, minimals4, rng4b,
                          n_samples=2000, maxmult=8)
    report["n4_coverage"] = cov4
    assert not cov4["fail_minimal_mult_ge4"], ("n4 minimal mult>=4",
                                               cov4["fail_minimal_mult_ge4"][:3])
    assert not cov4["fail_not_in_census"], ("n4 descended NOT in census",
                                            cov4["fail_not_in_census"][:3])

    rng4c = np.random.default_rng(303)
    orc4 = oracle_arm(4, arcs4, C4, iso4, rng4c, n_high=25, n_members=10)
    report["n4_oracle"] = orc4
    assert orc4["n_UNSAT"] == 0 and orc4["n_DISAGREE"] == 0 and \
        orc4["n_UNKNOWN"] == 0, ("n4 ORACLE KILL", orc4["kill_witnesses"])

    # ============================ n = 3 arm ================================ #
    arcs3, masks3, C3, minimals3, iso3, n_lam_ge3 = n3_census()
    report["n3_census"] = {
        "n_lambda_ge_3": n_lam_ge3,
        "n_minimal_labelled": len(minimals3),
        "n_iso_distinct": len(iso3),
    }
    assert all(max(m) <= 3 for m in minimals3), "n3 minimal mult>3 found"

    rng3 = np.random.default_rng(404)
    lem3 = lemma_instance_check(3, arcs3, C3, rng3, n_samples=2000, maxmult=8)
    report["n3_lemma_instance"] = lem3
    assert not lem3["fail_decrement"], ("n3 decrement lemma FAIL",
                                        lem3["fail_decrement"][:3])
    assert not lem3["fail_symbolic"], ("n3 symbolic-reason FAIL",
                                       lem3["fail_symbolic"][:3])
    assert lem3["arcs_mult_ge4_checked"] > 0, "n3: no mult>=4 arcs exercised"

    rng3b = np.random.default_rng(505)
    cov3 = coverage_check(3, arcs3, C3, minimals3, rng3b,
                          n_samples=2000, maxmult=8)
    report["n3_coverage"] = cov3
    assert not cov3["fail_minimal_mult_ge4"], ("n3 minimal mult>=4",
                                               cov3["fail_minimal_mult_ge4"][:3])
    assert not cov3["fail_not_in_census"], ("n3 descended NOT in census",
                                            cov3["fail_not_in_census"][:3])

    rng3c = np.random.default_rng(606)
    orc3 = oracle_arm(3, arcs3, C3, iso3, rng3c, n_high=15, n_members=min(10, len(iso3)))
    report["n3_oracle"] = orc3
    assert orc3["n_UNSAT"] == 0 and orc3["n_DISAGREE"] == 0 and \
        orc3["n_UNKNOWN"] == 0, ("n3 ORACLE KILL", orc3["kill_witnesses"])

    report["elapsed_s"] = round(time.time() - t0, 1)
    report["VERDICT"] = "CONFIRM: unbounded-mult WC3 reduction grounded at n<=4"
    print(json.dumps(report, indent=2, default=str))


if __name__ == "__main__":
    main()
