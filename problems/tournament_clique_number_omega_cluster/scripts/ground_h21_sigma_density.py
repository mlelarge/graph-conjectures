"""GROUND (H21 working-sigma DENSITY scaling law).

Claim under test (asymptotic): for generic ov=3 inner tournaments H of order n,
the discovery density rho(H,n) = P(a sampled optimal sigma of H yields merged
potential-sum clique exactly 4 on C3[H]) decays at most POLYNOMIALLY in n.

Legs:
  baseline_n8 : 13 generic ov=3 order-8 classes (data/scan_c3_inner_b3.json),
                enumerate optimal sigmas (prefix-pruned DFS, deterministic) up
                to a cap, counting per-sigma successes (success = ANY of the 6
                fixed tie-breaks gives merged clique exactly 4).
  baseline_n9 : the 36 hard classes (cap-200 stragglers of D40, indices from
                data/ground_potential_sum_c3_n9_fails_exhaustive.json) + 50
                seeded-random classes of the 1146 generic ov=3 order-9 classes
                (data/skeptic_o9_ov3_classes.json), same counting.
  scale --n N : generate seeded random tournaments of order N, keep the first
                --inners with EXACT ov=3 (two-sided prefix-pruned DFS decision,
                same pruning logic as the sigma generator: ov<=3 iff a clique<=3
                order exists, ov>=3 iff NO clique<=2 order exists), then sample
                up to --sigmas DISTINCT optimal sigmas via seeded random
                branch-order DFS restarts; per sigma test the 6 tie-breaks.

Every SUCCESS (merged clique exactly 4 = k+1) is re-verified with
core.omega_of_order (exact oracle clique routine) up to VERIFY_CAP per inner;
the fast bitmask clique is internal only.  Soundness of the per-sigma success
test: the proven lex lower bound gives omega(C3[H]^prec) >= ov(C3[H]) >= 4 for
every order, so "no 5-clique" <=> "clique exactly 4"; the core re-verification
independently asserts == 4 on every checked witness.
"""

import argparse
import json
import os
import random
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import core  # noqa: E402
from ground_potential_sum_c3 import (  # noqa: E402
    E_POT, TIEBREAK_IDS, beats_masks, bitcount, lex_compose, max_clique_mask,
    merged_order,
)

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")

VERIFY_CAP = 200  # core.omega_of_order re-verifications per inner (successes)

C3_ARCS = [(0, 1), (1, 2), (2, 0)]


def backedge_adj_for_order(beatsC, order):
    m = len(order)
    adj = [0] * m
    for i in range(m):
        a = order[i]
        for j in range(i + 1, m):
            if beatsC[order[j]] >> a & 1:
                adj[i] |= 1 << j
                adj[j] |= 1 << i
    return adj


def has_clique_size(adj, mask, t):
    """True iff the graph (bitmask adjacency) induced on `mask` has a clique
    of size >= t.  Exact branch-and-bound with early exit."""
    found = [False]

    def bk(size, cand):
        if found[0]:
            return
        if size >= t:
            found[0] = True
            return
        if size + bitcount(cand) < t:
            return
        c = cand
        while c and not found[0]:
            if size + bitcount(c) < t:
                return
            v = (c & -c).bit_length() - 1
            c &= c - 1
            bk(size + 1, c & adj[v])

    bk(0, mask)
    return found[0]


def eval_sigma(order, dvals, nH, beatsC, nC, target):
    """Return (success, tb) for one optimal sigma: success iff SOME tie-break
    gives merged backedge clique exactly `target` (== no (target+1)-clique;
    the proven lex lower bound gives clique >= target for every order)."""
    sigma_pos = [0] * nH
    for i, v in enumerate(order):
        sigma_pos[v] = i
    full = (1 << nC) - 1
    for tb in range(6):
        mo = merged_order(nH, sigma_pos, dvals, tb)
        adj = backedge_adj_for_order(beatsC, mo)
        if not has_clique_size(adj, full, target + 1):
            return True, tb, mo
    return False, None, None


def density_attack(nH, arcsH, k, sigma_cap, deadline, mode="exhaustive",
                   seed=0, per_restart=60, max_restarts=400):
    """Count working sigmas among sampled/enumerated optimal sigmas.

    mode=exhaustive: deterministic prefix-pruned DFS, first `sigma_cap` sigmas.
    mode=random    : seeded random branch-order DFS restarts, up to `sigma_cap`
                     DISTINCT sigmas (dedup by tuple).
    """
    beatsH = beats_masks(nH, arcsH)
    nC, arcsC = lex_compose(3, C3_ARCS, nH, arcsH)
    beatsC = beats_masks(nC, arcsC)
    target = k + 1
    full = (1 << nH) - 1

    st = {"n_sigmas": 0, "n_success": 0, "first_rank": None,
          "exhausted": True, "timed_out": False, "n_verified": 0,
          "verify_mismatch": 0}
    seen = set() if mode == "random" else None
    rng = random.Random(seed)

    def handle_sigma(order, dvals):
        st["n_sigmas"] += 1
        ok, tb, mo = eval_sigma(order, dvals, nH, beatsC, nC, target)
        if ok:
            st["n_success"] += 1
            if st["first_rank"] is None:
                st["first_rank"] = st["n_sigmas"]
            if st["n_verified"] < VERIFY_CAP:
                w2 = core.omega_of_order(nC, arcsC, mo)
                st["n_verified"] += 1
                if w2 != target:
                    st["verify_mismatch"] += 1
                assert w2 == target, f"core says {w2} != {target}"
        return st["n_sigmas"] >= sigma_cap

    def dfs(placed, order, dvals, badj, randomize):
        """Returns True to abort the whole DFS (cap/deadline)."""
        if time.time() > deadline:
            st["timed_out"] = True
            st["exhausted"] = False
            return True
        if placed == full:
            if seen is not None:
                key = tuple(order)
                if key in seen:
                    return False
                seen.add(key)
            if handle_sigma(order, dvals):
                st["exhausted"] = False
                return True
            return False
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
            stop = dfs(placed | (1 << v), order, dvals, badj, randomize)
            order.pop()
            badj[v] = 0
            for u in undo:
                badj[u] &= ~(1 << v)
            if stop:
                return True
        return False

    if mode == "exhaustive":
        dfs(0, [], [0] * nH, [0] * nH, randomize=False)
    else:
        st["exhausted"] = False  # sampling is never an exhaustive claim
        restarts = 0
        while (restarts < max_restarts and st["n_sigmas"] < sigma_cap
               and time.time() < deadline):
            restarts += 1
            base = st["n_sigmas"]
            # per-restart sub-cap: stop this restart after per_restart NEW sigmas
            sub_deadline = min(deadline, time.time() + 30)
            orig_cap = sigma_cap
            cap_now = min(sigma_cap, base + per_restart)

            def handle_capped(order, dvals, _cap=cap_now):
                st["n_sigmas"] += 1
                ok, tb, mo = eval_sigma(order, dvals, nH, beatsC, nC, target)
                if ok:
                    st["n_success"] += 1
                    if st["first_rank"] is None:
                        st["first_rank"] = st["n_sigmas"]
                    if st["n_verified"] < VERIFY_CAP:
                        w2 = core.omega_of_order(nC, arcsC, mo)
                        st["n_verified"] += 1
                        if w2 != target:
                            st["verify_mismatch"] += 1
                        assert w2 == target
                return st["n_sigmas"] >= _cap

            # local dfs with the restart sub-cap
            def dfs_r(placed, order, dvals, badj):
                if time.time() > sub_deadline:
                    return True
                if placed == full:
                    key = tuple(order)
                    if key in seen:
                        return False
                    seen.add(key)
                    return handle_capped(order, dvals)
                rest = full & ~placed
                cands = []
                c = rest
                while c:
                    v = (c & -c).bit_length() - 1
                    c &= c - 1
                    cands.append(v)
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
                    stop = dfs_r(placed | (1 << v), order, dvals, badj)
                    order.pop()
                    badj[v] = 0
                    for u in undo:
                        badj[u] &= ~(1 << v)
                    if stop:
                        return True
                return False

            dfs_r(0, [], [0] * nH, [0] * nH)
        if time.time() > deadline:
            st["timed_out"] = True

    res = {
        "n": nH, "k": k,
        "n_sigmas": st["n_sigmas"],
        "n_success": st["n_success"],
        "success_frac": (st["n_success"] / st["n_sigmas"]
                         if st["n_sigmas"] else None),
        "first_rank": st["first_rank"],
        "exhausted_over_optimal_sigmas": st["exhausted"],
        "timed_out": st["timed_out"],
        "n_core_verified": st["n_verified"],
        "verify_mismatch": st["verify_mismatch"],
        "mode": mode,
    }
    return res


# ------------------------------------------------------------------------- #
#  Exact ov(H)=3 decision (same pruning logic, two-sided)
# ------------------------------------------------------------------------- #

def exists_order_clique_le(nH, beatsH, k, deadline):
    """True iff H has a total order with backedge clique <= k.  Exact
    prefix-pruned DFS (d_sigma(v)<=k for all v <=> clique<=k).
    Returns None on timeout."""
    full = (1 << nH) - 1
    badj = [0] * nH
    timed = [False]

    def dfs(placed):
        if time.time() > deadline:
            timed[0] = True
            return False
        if placed == full:
            return True
        rest = full & ~placed
        c = rest
        while c:
            v = (c & -c).bit_length() - 1
            c &= c - 1
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
            if dfs(placed | (1 << v)):
                return True
            badj[v] = 0
            for u in undo:
                badj[u] &= ~(1 << v)
        return False

    r = dfs(0)
    if timed[0] and not r:
        return None
    return r


def is_ov3(nH, arcsH, deadline):
    beatsH = beats_masks(nH, arcsH)
    le3 = exists_order_clique_le(nH, beatsH, 3, deadline)
    if le3 is not True:
        return False if le3 is False else None
    le2 = exists_order_clique_le(nH, beatsH, 2, deadline)
    if le2 is None:
        return None
    return not le2  # ov<=3 and not ov<=2  =>  ov==3


def random_tournament(n, rng):
    arcs = []
    for i in range(n):
        for j in range(i + 1, n):
            arcs.append((i, j) if rng.random() < 0.5 else (j, i))
    return arcs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--leg", required=True,
                    choices=["baseline_n8", "baseline_n9", "scale"])
    ap.add_argument("--n", type=int, default=10)
    ap.add_argument("--inners", type=int, default=20)
    ap.add_argument("--sigmas", type=int, default=3000)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--cap", type=int, default=20000)
    ap.add_argument("--per-class-seconds", type=float, default=25.0)
    args = ap.parse_args()
    t0 = time.time()
    out = {"leg": args.leg, "tiebreaks": TIEBREAK_IDS,
           "e_potential": list(E_POT), "args": vars(args)}

    if args.leg == "baseline_n8":
        d = json.load(open(os.path.join(DATA, "scan_c3_inner_b3.json")))
        results = []
        for i, cl in enumerate(d["per_class"]):
            arcs = [tuple(a) for a in cl["inner_arcs"]]
            assert core.omega_vec(8, arcs) == 3
            r = density_attack(8, arcs, 3, args.cap,
                               time.time() + args.per_class_seconds)
            r["inner_class_index"] = cl["inner_class_index"]
            results.append(r)
            print(f"[n8 {i}] idx={cl['inner_class_index']} "
                  f"succ={r['n_success']}/{r['n_sigmas']} "
                  f"rho={r['success_frac']:.4g} first={r['first_rank']} "
                  f"exh={r['exhausted_over_optimal_sigmas']}", flush=True)
        out["results"] = results

    elif args.leg == "baseline_n9":
        fe = json.load(open(os.path.join(
            DATA, "ground_potential_sum_c3_n9_fails_exhaustive.json")))
        hard_idx = sorted(r["class_index"] for r in fe["results"])
        s = json.load(open(os.path.join(DATA, "skeptic_o9_ov3_classes.json")))
        by_idx = {cl["class_index"]: cl for cl in s["classes"]}
        rng = random.Random(args.seed)
        pool = [cl["class_index"] for cl in s["classes"]
                if cl["class_index"] not in set(hard_idx)]
        rand_idx = rng.sample(pool, 50)
        results = []
        for tag, idxs in (("hard36", hard_idx), ("random50", rand_idx)):
            for ci in idxs:
                arcs = [tuple(a) for a in by_idx[ci]["arcs"]]
                r = density_attack(9, arcs, 3, min(args.cap, args.sigmas),
                                   time.time() + args.per_class_seconds)
                r["class_index"] = ci
                r["subset"] = tag
                results.append(r)
                print(f"[n9 {tag}] idx={ci} succ={r['n_success']}/"
                      f"{r['n_sigmas']} rho={r['success_frac']:.4g} "
                      f"first={r['first_rank']}", flush=True)
        out["results"] = results

    else:  # scale
        n = args.n
        rng = random.Random(args.seed)
        inners = []
        tried = 0
        gen_deadline = time.time() + 240
        while len(inners) < args.inners and time.time() < gen_deadline:
            tried += 1
            arcs = random_tournament(n, rng)
            v = is_ov3(n, arcs, time.time() + 20)
            if v is True:
                inners.append(arcs)
        out["candidates_tried"] = tried
        out["n_inners"] = len(inners)
        print(f"[scale n={n}] kept {len(inners)} ov=3 inners "
              f"of {tried} candidates, {time.time()-t0:.0f}s", flush=True)
        results = []
        budget_per = (840 - (time.time() - t0)) / max(1, len(inners))
        for i, arcs in enumerate(inners):
            r = density_attack(n, arcs, 3, args.sigmas,
                               time.time() + budget_per, mode="random",
                               seed=args.seed * 1000 + i)
            r["inner_index"] = i
            r["arcs"] = arcs
            results.append(r)
            print(f"[scale n={n} inner {i}] succ={r['n_success']}/"
                  f"{r['n_sigmas']} rho={r['success_frac']} "
                  f"first={r['first_rank']} timeout={r['timed_out']}",
                  flush=True)
        out["results"] = results

    fr = [r["success_frac"] for r in out.get("results", [])
          if r.get("success_frac") is not None]
    if fr:
        fr2 = sorted(fr)
        out["median_success_frac"] = fr2[len(fr2) // 2]
        out["min_success_frac"] = fr2[0]
        out["n_inners_with_no_success"] = sum(
            1 for r in out["results"] if r["n_success"] == 0)
    out["elapsed_seconds"] = round(time.time() - t0, 2)
    suffix = args.leg if args.leg != "scale" else f"scale_n{args.n}"
    path = os.path.join(DATA, f"h21_sigma_density_{suffix}.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=1)
    print(f"WROTE {path} median_rho="
          f"{out.get('median_success_frac')} elapsed={out['elapsed_seconds']}s",
          flush=True)


if __name__ == "__main__":
    main()
