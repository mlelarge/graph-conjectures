"""GROUND (H21 potential-sum mechanism, FIRST run at k=5 on the tower).

H = AC_7[AC_7]  (order 49, ov=5 PROVEN, P19 / data/verify_k5_ac7ac7.json).
Outer = directed C3.  C3[H] has order 147; lex lower bound gives
omega_vec(C3[H]) >= ov(C3)+ov(H)-1 = 6  (proven >=6).  G49 left a two-sided
[6,7] wall (SAT infeasible at C(147,7)).

H21 mechanism: take an OPTIMAL sigma of H (backedge clique == 5 exactly), with
its per-vertex prefix-clique profile d_sigma(v); order the 147 vertices of
C3[H] by key(c,v) = E_POT[c] + d_sigma(v) with E_POT=(1,1,2) and a tie-break,
then take the EXACT backedge clique of that merged order.  H21 predicts this
equals ov(C3[H]) = 6, i.e. clique <= max(E_POT)+max(d)-1 = ov+1 = 6.

Falsifiable prediction (existential): SOME tested merged order has exact
backedge clique == 6 -> pins omega_vec(C3[AC_7[AC_7]]) = 6 EXACTLY (the >=6 lex
bound is proven), SAT-free.  KILL branch: P19 sigma + all 6 tie-breaks + >=50
distinct exact-verified optimal sigmas ALL give merged clique >= 7.

Single foreground command, signal.alarm hard cap.  Every merged-clique value is
exact (max_clique_mask, branch-and-bound); any ==6 hit is INDEPENDENTLY
re-verified with core.omega_of_order before reporting omega_vec=6.
"""
import json
import os
import random
import signal
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import core  # noqa: E402
from ground_lex_compose_c3 import ac_gen  # noqa: E402
from search_4critical_circulant import circ_arcs  # noqa: E402
from ground_potential_sum_c3 import (  # noqa: E402
    E_POT, TIEBREAK_IDS, backedge_adj_for_order, beats_masks, lex_compose,
    max_clique_mask, merged_order,
)

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")


class Timeout(Exception):
    pass


def _alarm(s, f):
    raise Timeout()


def c_of(t, m=3):
    """Block-class potential of an AC_7 index (verify_k5_ac7ac7.py)."""
    return 3 if t == 0 else (2 if 1 <= t <= m else 1)


def d_profile(nH, beatsH, order):
    """Per-vertex prefix backedge-clique profile d_sigma(v) for an explicit
    order: d_sigma(v) = 1 + (max clique among placed predecessors u with arc
    v->u, in the backedge graph restricted to the prefix).  This is exactly the
    dv computed incrementally in attack_class; here recomputed from scratch for
    an externally supplied order."""
    badj = [0] * nH
    dvals = [0] * nH
    placed = 0
    for v in order:
        nb = beatsH[v] & placed
        dv = 1 + max_clique_mask(badj, nb) if nb else 1
        dvals[v] = dv
        badj[v] = nb
        m = nb
        while m:
            u = (m & -m).bit_length() - 1
            m &= m - 1
            badj[u] |= 1 << v
        placed |= 1 << v
    return dvals


def constructive_sigma(nH):
    """The P19 / verify_k5 inner_then_outer-style constructive optimal order of
    H = AC_7[AC_7] (order 49): key (c_of(outer)+c_of(inner), outer, inner).
    verify_k5_ac7ac7.py certifies this merged order has backedge clique 5."""
    return sorted(range(nH),
                  key=lambda f: (c_of(f // 7) + c_of(f % 7), f // 7, f % 7))


def find_optimal_sigma(nH, beatsH, k, deadline, randomize=False, rng=None):
    """Return (order, dvals) for ONE order of H with backedge clique <= k
    (an optimal sigma when k == ov(H)), or None if none found in time.
    Prefix-pruned DFS (identical pruning to ground_potential_sum_c3.attack_class).
    randomize=True shuffles candidate order each node (for restart harvesting)."""
    full = (1 << nH) - 1
    badj = [0] * nH
    order = []
    dvals = [0] * nH
    found = [None]

    def dfs(placed):
        if found[0] is not None:
            return True
        if time.time() > deadline:
            return True
        if placed == full:
            found[0] = (list(order), list(dvals))
            return True
        rest = full & ~placed
        cands = []
        c = rest
        while c:
            v = (c & -c).bit_length() - 1
            c &= c - 1
            cands.append(v)
        if randomize:
            rng.shuffle(cands)
        for v in cands:
            nb = beatsH[v] & placed
            dv = 1 + max_clique_mask(badj, nb) if nb else 1
            if dv > k:
                continue
            badj[v] = nb
            undo = []
            m = nb
            while m:
                u = (m & -m).bit_length() - 1
                m &= m - 1
                badj[u] |= 1 << v
                undo.append(u)
            order.append(v)
            dvals[v] = dv
            if dfs(placed | (1 << v)):
                return True
            order.pop()
            badj[v] = 0
            for u in undo:
                badj[u] &= ~(1 << v)
        return False

    dfs(0)
    return found[0]


def test_merged(nH, sigma, dvals, beatsC, nC, target, deadline):
    """Try the 6 tie-breaks on the merged order. Return list of (tb, clique).
    Stop early on the first clique == target (a HIT)."""
    sigma_pos = [0] * nH
    for i, v in enumerate(sigma):
        sigma_pos[v] = i
    results = []
    full = (1 << nC) - 1
    for tb in range(6):
        if time.time() > deadline:
            break
        mo = merged_order(nH, sigma_pos, dvals, tb)
        adj = backedge_adj_for_order(beatsC, mo)
        w = max_clique_mask(adj, full)
        results.append((tb, w, mo))
        if w == target:
            break
    return results


def main():
    signal.signal(signal.SIGALRM, _alarm)
    HARD = int(os.environ.get("HARD_TIMEOUT", "560"))
    signal.alarm(HARD)
    t0 = time.time()
    out = {"e_potential": list(E_POT), "tiebreaks": TIEBREAK_IDS}
    try:
        # ---- build H = AC_7[AC_7], order 49, ov=5 (P19) ----
        g = ac_gen(7)
        nAC, aAC = 7, circ_arcs(7, g)
        nH, arcsH = lex_compose(nAC, aAC, nAC, aAC)
        assert core.is_tournament(nH, arcsH), "H not a tournament"
        assert nH == 49
        beatsH = beats_masks(nH, arcsH)
        out["nH"] = nH

        k = 5  # ov(H) = 5 (proven); optimal sigma -> backedge clique 5
        target = 6  # ov(C3[H]) = ov(C3)+ov(H)-1 = 6, lex lower bound proven

        # ---- C3[H], order 147 ----
        nC, arcsC = lex_compose(3, [(0, 1), (1, 2), (2, 0)], nH, arcsH)
        assert core.is_tournament(nC, arcsC)
        assert nC == 147
        beatsC = beats_masks(nC, arcsC)
        out["nC"] = nC

        deadline = t0 + HARD - 20

        # ---- (1) P19 constructive inner_then_outer optimal sigma ----
        # (DFS rediscovery of an optimal order over 49! is infeasible in
        #  foreground; we use the verify_k5-certified constructive order.)
        sigma0 = constructive_sigma(nH)
        d0 = d_profile(nH, beatsH, sigma0)
        # verify backedge clique(H^sigma0) == 5 EXACTLY (P19 value)
        w_sigma0 = core.omega_of_order(nH, arcsH, sigma0)
        out["sigma0_backedge_clique_core"] = w_sigma0
        assert w_sigma0 == 5, f"sigma0 clique {w_sigma0} != 5"
        out["d0_max"] = max(d0)

        all_results = []  # list of dicts {sigma_id, source, merged_cliques:{tb:w}}
        hit = None

        def record(sigma, dvals, sid, source):
            nonlocal hit
            res = test_merged(nH, sigma, dvals, beatsC, nC, target, deadline)
            rec = {"sigma_id": sid, "source": source,
                   "merged_cliques": {str(tb): w for (tb, w, _) in res},
                   "min_merged": min((w for (_, w, _) in res), default=None)}
            all_results.append(rec)
            for (tb, w, mo) in res:
                if w == target:
                    # INDEPENDENT re-verification with the exact oracle routine
                    w2 = core.omega_of_order(nC, arcsC, mo)
                    rec["HIT_core_verified"] = w2
                    if w2 == target:
                        hit = {"sigma_id": sid, "source": source, "tiebreak": tb,
                               "tiebreak_rule": TIEBREAK_IDS[tb],
                               "merged_clique_core": w2, "sigma": sigma}
                    return True
            return False

        record(sigma0, d0, 0, "P19_constructive")

        # ---- (2) budgeted batch of >=50 further distinct optimal sigmas ----
        # Harvest by RANDOM in-band permutations of the constructive key: shuffle
        # within each equal-(c_of+c_of) band (and finer tie-bands), keep only
        # those that still have backedge clique == 5 (re-verified by core).  This
        # samples the optimal-sigma neighbourhood the verify_k5 order lives in
        # WITHOUT the infeasible 49! DFS.
        rng = random.Random(12345)
        seen = {tuple(sigma0)}
        sid = 1
        target_distinct = 50
        restart_deadline = deadline - 5
        # band key: coarse merged potential; within a band, order is free-ish
        def band_of(f):
            return c_of(f // 7) + c_of(f % 7)
        bands = {}
        for f in range(nH):
            bands.setdefault(band_of(f), []).append(f)
        band_keys = sorted(bands)
        tried = 0
        while (len(seen) < target_distinct + 1
               and time.time() < restart_deadline
               and tried < 4000):
            tried += 1
            sigma = []
            for bk_ in band_keys:
                blk = bands[bk_][:]
                rng.shuffle(blk)
                sigma.extend(blk)
            key = tuple(sigma)
            if key in seen:
                continue
            ws = core.omega_of_order(nH, arcsH, sigma)
            if ws != 5:
                continue  # not an optimal sigma; discard
            seen.add(key)
            dv = d_profile(nH, beatsH, sigma)
            if record(sigma, dv, sid, "band_permutation"):
                break
            sid += 1
        out["band_permutations_tried"] = tried
        out["distinct_optimal_sigmas_found"] = len(seen)

        out["n_distinct_sigmas_tested"] = len(all_results)
        merged_vals = [rec["min_merged"] for rec in all_results
                       if rec["min_merged"] is not None]
        out["global_min_merged_clique"] = min(merged_vals) if merged_vals else None
        out["global_max_merged_clique"] = max(
            (w for rec in all_results
             for w in [int(x) for x in rec["merged_cliques"].values()]),
            default=None)
        hist = {}
        for rec in all_results:
            for w in rec["merged_cliques"].values():
                hist[w] = hist.get(w, 0) + 1
        out["merged_clique_histogram"] = dict(sorted(hist.items()))
        out["hit"] = hit
        out["pins_omega_vec_eq_6"] = hit is not None
        # sample of per-sigma results (cap to keep JSON small)
        out["results"] = all_results[:80]
    except Timeout:
        out["status"] = out.get("status", "TIMEOUT")
    finally:
        signal.alarm(0)
    out["elapsed_seconds"] = round(time.time() - t0, 2)
    path = os.path.join(DATA, "h21_tower_k5.json")
    with open(os.path.abspath(path), "w") as f:
        json.dump(out, f, indent=1)
    print("=== H21 tower k=5 (C3[AC_7[AC_7]], order 147) ===", flush=True)
    print("nH=", out.get("nH"), "nC=", out.get("nC"),
          "sigma0 clique=", out.get("sigma0_backedge_clique_core"), flush=True)
    print("distinct sigmas tested:", out.get("n_distinct_sigmas_tested"),
          flush=True)
    print("merged clique histogram:", out.get("merged_clique_histogram"),
          flush=True)
    print("global min merged clique:", out.get("global_min_merged_clique"),
          flush=True)
    print("HIT (merged clique == 6, core-verified):", out.get("hit"), flush=True)
    print("pins omega_vec(C3[AC_7[AC_7]]) == 6 ?", out.get("pins_omega_vec_eq_6"),
          flush=True)
    print("status:", out.get("status", "OK"), "elapsed:",
          out["elapsed_seconds"], "s", flush=True)
    print("WROTE", path, flush=True)


if __name__ == "__main__":
    main()
