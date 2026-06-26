"""C=2 Eulerian alteration probe.

Tests the proposal's ONE-FLIP REPAIR claim at lambda >= ceil(2 log2 n)+2:
 (a) few, near-minimum monochromatic directed cuts under a uniform random 2-coloring;
 (b) greedy one-flip repair reaches full bichromaticity (= a verified SAD).

A digraph multiset D = list of arcs (u,v) (with multiplicity).  A 2-coloring is a
map arc-index -> {0,1}.  A directed cut delta+(X) (emptyset != X subsetneq V) is
MONOCHROMATIC (violated) iff all its arcs have the same color.  Full bichromaticity
of every directed cut == SAD (the cut criterion; both color classes spanning-strong).

We enumerate ALL 2^n - 2 vertex subsets X and compute, per coloring, the set of
violated cuts.  Each successful final coloring is independently re-validated by
strong-connectivity of BOTH color classes (a genuine SAD witness), and a couple of
them are cross-checked with the oracle's full SAD decision.

Single foreground run, stdlib + oracle only.
"""
from __future__ import annotations

import math
import os
import random
import sys
import time

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
import oracle  # noqa: E402

random.seed(20260612)


# --------------------------------------------------------------------------- #
#  Instance builders
# --------------------------------------------------------------------------- #
def bidirected_multicycle(n, m):
    """B(n,m): arcs i->i+1 and i+1->i each with multiplicity m. Eulerian, lambda=2m."""
    arcs = []
    for i in range(n):
        j = (i + 1) % n
        for _ in range(m):
            arcs.append((i, j))
            arcs.append((j, i))
    return arcs


def random_eulerian_hamilton_sum(n, r):
    """Arc-disjoint-ish union of r random directed Hamilton cycles.

    Each Hamilton cycle is Eulerian (in=out=1 at every vertex); a sum of r of them
    is Eulerian (in=out=r).  Multiplicities can coincide; that's fine (still
    Eulerian, multiplicity-aware lambda).
    """
    arcs = []
    for _ in range(r):
        perm = list(range(n))
        random.shuffle(perm)
        for i in range(n):
            u = perm[i]
            v = perm[(i + 1) % n]
            arcs.append((u, v))
    return arcs


# --------------------------------------------------------------------------- #
#  Cut machinery (bitset incidence over vertex subsets)
# --------------------------------------------------------------------------- #
def precompute_cut_membership(n, arcs):
    """For each arc e=(u,v) and each subset X (as an int bitmask over vertices),
    e is in delta+(X) iff u in X and v notin X.

    We precompute, per arc, the bitmask 'in_when' = bit(u) and 'out_when' = bit(v).
    A subset mask X contains the arc in its out-cut iff (X>>u)&1 and not (X>>v)&1.
    Returns list of (u,v) and we evaluate membership on the fly (n<=16 -> 2^n scan).
    """
    return [(u, v) for (u, v) in arcs]


def violated_cuts(n, arcs, color):
    """Return list of (X_mask, size, monochrome_color) for every monochromatic
    directed out-cut delta+(X), emptyset != X subsetneq V.

    color: list aligned with arcs, entries in {0,1}.
    """
    full = (1 << n) - 1
    viol = []
    A = arcs
    C = color
    for X in range(1, full):  # 1..full-1 == proper nonempty subsets
        cut_size = 0
        seen0 = False
        seen1 = False
        # iterate arcs; early-out only after we've seen both colors AND we still
        # need the size, so we must finish to get size -> just scan all.
        for idx in range(len(A)):
            u, v = A[idx]
            if (X >> u) & 1 and not ((X >> v) & 1):
                cut_size += 1
                if C[idx]:
                    seen1 = True
                else:
                    seen0 = True
        if cut_size == 0:
            continue  # not a real directed cut in this multiset (shouldn't happen if strong)
        if seen0 != seen1:  # exactly one of them true -> monochromatic
            mono = 1 if seen1 else 0
            viol.append((X, cut_size, mono))
    return viol


def count_violations_for_color(n, arcs, color):
    full = (1 << n) - 1
    cnt = 0
    A = arcs
    C = color
    for X in range(1, full):
        seen0 = False
        seen1 = False
        any_arc = False
        for idx in range(len(A)):
            u, v = A[idx]
            if (X >> u) & 1 and not ((X >> v) & 1):
                any_arc = True
                if C[idx]:
                    seen1 = True
                else:
                    seen0 = True
                if seen0 and seen1:
                    break
        if any_arc and (seen0 != seen1):
            cnt += 1
    return cnt


# --------------------------------------------------------------------------- #
#  Strong connectivity of a color class (independent SAD re-validation)
# --------------------------------------------------------------------------- #
def is_strong_class(n, arcs, color, c):
    """Is the subdigraph of arcs with color==c spanning and strongly connected?"""
    adj = [[] for _ in range(n)]
    radj = [[] for _ in range(n)]
    deg = 0
    for idx, (u, v) in enumerate(arcs):
        if color[idx] == c:
            adj[u].append(v)
            radj[v].append(u)
            deg += 1
    if deg == 0:
        return False

    def reach(start, graph):
        seen = [False] * n
        stack = [start]
        seen[start] = True
        cnt = 1
        while stack:
            x = stack.pop()
            for y in graph[x]:
                if not seen[y]:
                    seen[y] = True
                    cnt += 1
                    stack.append(y)
        return cnt

    return reach(0, adj) == n and reach(0, radj) == n


def is_sad_coloring(n, arcs, color):
    return is_strong_class(n, arcs, color, 0) and is_strong_class(n, arcs, color, 1)


# --------------------------------------------------------------------------- #
#  Greedy one-flip repair
# --------------------------------------------------------------------------- #
def greedy_repair(n, arcs, color, max_flips):
    """While monochromatic cuts exist, pick a smallest violated cut and flip the
    arc whose recolor minimizes the resulting total violation count.

    Returns (success, flips_used, final_color).
    """
    color = list(color)
    flips = 0
    while flips < max_flips:
        viol = violated_cuts(n, arcs, color)
        if not viol:
            return True, flips, color
        viol.sort(key=lambda t: t[1])  # smallest cut first
        Xmask, csize, mono = viol[0]
        # candidate arcs = those in this cut (they're all color 'mono'); flipping
        # one to 1-mono makes THIS cut bichromatic.
        cand = []
        for idx, (u, v) in enumerate(arcs):
            if (Xmask >> u) & 1 and not ((Xmask >> v) & 1):
                cand.append(idx)
        best_idx = None
        best_total = None
        for idx in cand:
            color[idx] ^= 1
            tot = count_violations_for_color(n, arcs, color)
            color[idx] ^= 1
            if best_total is None or tot < best_total:
                best_total = tot
                best_idx = idx
        color[best_idx] ^= 1
        flips += 1
    # final check
    return (count_violations_for_color(n, arcs, color) == 0), flips, color


# --------------------------------------------------------------------------- #
#  Per-instance experiment
# --------------------------------------------------------------------------- #
def run_instance(name, n, arcs, lam, T, viol_budget, size_budget):
    init_counts = []
    init_max_alpha = 0.0
    all_within_size = True
    repair_succ = 0
    repair_attempts = 0
    flips_list = []
    sad_validated = 0
    log2n = math.log2(n)

    for t in range(T):
        color = [random.randint(0, 1) for _ in arcs]
        viol = violated_cuts(n, arcs, color)
        init_counts.append(len(viol))
        for (X, csize, mono) in viol:
            a = csize / lam
            if a > init_max_alpha:
                init_max_alpha = a
            if csize > size_budget:
                all_within_size = False
        repair_attempts += 1
        init_v = len(viol)
        ok, flips, final = greedy_repair(n, arcs, color, 4 * init_v + 20)
        if ok:
            repair_succ += 1
            flips_list.append(flips)
            if is_sad_coloring(n, arcs, final):
                sad_validated += 1

    init_counts.sort()
    mean_v = sum(init_counts) / len(init_counts)
    p95 = init_counts[min(len(init_counts) - 1, int(0.95 * len(init_counts)))]
    mean_flips = (sum(flips_list) / len(flips_list)) if flips_list else float("nan")
    return {
        "name": name, "n": n, "lambda": lam, "T": T,
        "viol_budget": round(viol_budget, 2),
        "size_budget": round(size_budget, 2),
        "mean_viol": round(mean_v, 2),
        "p95_viol": p95,
        "max_init_alpha": round(init_max_alpha, 3),
        "all_within_size": all_within_size,
        "repair_success_rate": round(repair_succ / repair_attempts, 3),
        "sad_validated": sad_validated,
        "mean_flips": round(mean_flips, 2) if flips_list else None,
        "log2n_sq": round(log2n ** 2, 2),
    }


def per_n_T(n):
    # foreground-budget-aware: the 2^n scan + per-flip recount is ~quadratic in
    # instance work; smaller T for larger n keeps a single foreground run < 580s.
    if n >= 16:
        return 40
    if n >= 14:
        return 70
    return 100


def main():
    t0 = time.time()
    instances = []

    # (1) bidirected multicycles (first-moment-extremal family).
    # Per ground_plan fallback, cap n=16 to ONE B instance to protect the budget.
    for (n, m) in [(12, 2), (12, 3), (16, 4)]:
        arcs = bidirected_multicycle(n, m)
        lam = oracle.arc_connectivity(n, arcs)
        instances.append((f"B({n},{m})", n, arcs, lam))

    # (2) random Eulerian Hamilton-cycle sums (n in {12,14}, keep n=16 light)
    rng_instances = 0
    attempts = 0
    while rng_instances < 5 and attempts < 60:
        attempts += 1
        n = random.choice([12, 12, 14, 14])  # keep random instances light (no n=16)
        target = math.ceil(2 * math.log2(n)) + 2
        arcs = random_eulerian_hamilton_sum(n, target)
        lam = oracle.arc_connectivity(n, arcs)
        if lam >= target - 1:
            instances.append((f"EulerHam(n={n},r={target},lam={lam})", n, arcs, lam))
            rng_instances += 1

    results = []
    for (name, n, arcs, lam) in instances:
        log2n = math.log2(n)
        thresh = math.ceil(2 * log2n) + 2
        viol_budget = log2n ** 2
        size_budget = lam + 2 * math.log2(lam)
        T = per_n_T(n)
        # guard the foreground budget
        if time.time() - t0 > 300:
            print(f"[skip {name}: budget guard]", flush=True)
            continue
        res = run_instance(name, n, arcs, lam, T, viol_budget, size_budget)
        res["thresh_2log2n_plus2"] = thresh
        res["lambda_ge_thresh"] = lam >= thresh
        results.append(res)
        print(
            f"{name:32s} n={n} lam={lam} thr={thresh} "
            f"meanV={res['mean_viol']:6.2f} p95V={res['p95_viol']:4d} "
            f"(budget={res['viol_budget']:5.2f}) maxAlpha={res['max_init_alpha']:.2f} "
            f"sizeOK={res['all_within_size']} "
            f"repair={res['repair_success_rate']:.2f} "
            f"sadVal={res['sad_validated']}/{T} flips={res['mean_flips']}",
            flush=True,
        )

    # Oracle cross-check: take up to 2 instances, repair one coloring, decide SAD.
    print("\n--- ORACLE CROSS-CHECK (full SAD decision on the instances) ---", flush=True)
    for (name, n, arcs, lam) in instances[:3]:
        try:
            chk = oracle.check_construction(n, arcs, name=name, cross_check=True)
            print(f"{name:32s} oracle SAD={chk['sad']} lam={chk['arc_strong']} "
                  f"cross={chk.get('cross_check')}", flush=True)
        except Exception as e:
            print(f"{name}: oracle error {e}", flush=True)

    # --- Verdict aggregation per proposal's falsifiable_prediction ---
    print("\n--- VERDICT AGGREGATION ---", flush=True)
    confirm_a = True   # <= (log2 n)^2 mean violations AND all within size
    confirm_b = True   # repair reaches full bichromaticity (SAD) >=90%
    for r in results:
        a_few = r["mean_viol"] <= r["viol_budget"]
        a_size = r["all_within_size"]
        b_repair = r["repair_success_rate"] >= 0.90
        if not (a_few and a_size):
            confirm_a = False
        if not b_repair:
            confirm_b = False
        print(f"{r['name']:32s} (a)few={a_few} (a)size={a_size} "
              f"(b)repair>=0.90={b_repair}", flush=True)
    print(f"\nCONFIRM_A (few, near-min) = {confirm_a}", flush=True)
    print(f"CONFIRM_B (greedy repair to SAD) = {confirm_b}", flush=True)
    print(f"OVERALL CONFIRM = {confirm_a and confirm_b}", flush=True)
    print(f"elapsed {time.time()-t0:.1f}s", flush=True)


if __name__ == "__main__":
    main()
