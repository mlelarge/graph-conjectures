"""Ground the dom-dual QR_67 proposal (round-1 executor).

Falsifiable predictions:
 (A) dom(QR_67) = 5 exactly  => omega_vec(QR_67) >= 5 (free, Property 3.2).
 (D) NO circulant tournament on Z/n has dom>=5 for odd n<67; dom>=4 occurs ONLY
     for QR_p/reverse at n in {19,23}. (We verify the Paley-only-at-{19,23} for
     dom>=4 via the recorded Paley scan, and confirm no Paley dom>=5 below 67.)
 (B) Search for a total order of QR_67 with backedge clique EXACTLY 5
     (omega_of_order=5). If found => omega_vec=5, dom tight. If best stays 6,
     KILL of the k=5-at-67 hope.

Arc convention: i -> (i+d) mod p for d in g  (matches dom_reduction_ground.py).
QR_p generator = nonzero quadratic residues mod p (Paley tournament).
"""
import sys, os, json, time, itertools, random
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
import core


def circulant_arcs(p, g):
    return [(i, (i + d) % p) for i in range(p) for d in g]


def qr_gen(p):
    return sorted({(x * x) % p for x in range(1, p)})


def dom_direct_le(n, arcs, ub):
    """min |X| dominating, brute over subsets up to ub; return ub+1 if > ub."""
    beats = core.beats_matrix(n, arcs)
    closed = []
    for v in range(n):
        s = {v}
        for w in range(n):
            if beats[v][w]:
                s.add(w)
        closed.append(s)
    full = set(range(n))
    for size in range(1, ub + 1):
        for X in itertools.combinations(range(n), size):
            cov = set()
            for x in X:
                cov |= closed[x]
            if cov == full:
                return size
    return ub + 1


def dom_additive_cover(p, N0, ub):
    """min number of translates of N0 covering Z/p (= dom for circulant with
    closed out-nbhd N0). Greedy-lower + exact brute up to ub via translate sets."""
    N0 = set(d % p for d in N0)
    full = set(range(p))
    # translate sets
    trans = [set((d + t) % p for d in N0) for t in range(p)]
    for size in range(1, ub + 1):
        for combo in itertools.combinations(range(p), size):
            cov = set()
            for t in combo:
                cov |= trans[t]
            if cov == full:
                return size
    return ub + 1


def sa_order_for_target(p, arcs, target, time_budget, seed=0):
    """Simulated-annealing-ish local search on total orders to MINIMIZE backedge
    clique, aiming to hit `target`. Returns (best_clique, best_order, iters)."""
    rng = random.Random(seed)
    n = p
    # start from identity rotation min as a decent seed
    best_order = list(range(n))
    cur = list(best_order)
    cur_w = core.omega_of_order(n, arcs, cur)
    best_w = cur_w
    best_o = list(cur)
    t0 = time.time()
    iters = 0
    while time.time() - t0 < time_budget:
        iters += 1
        # random swap or block reversal
        if rng.random() < 0.5:
            i, j = rng.randrange(n), rng.randrange(n)
            cand = list(cur)
            cand[i], cand[j] = cand[j], cand[i]
        else:
            i = rng.randrange(n)
            j = rng.randrange(n)
            if i > j:
                i, j = j, i
            cand = cur[:i] + cur[i:j + 1][::-1] + cur[j + 1:]
        w = core.omega_of_order(n, arcs, cand)
        # accept improving or sideways; small uphill with prob
        if w <= cur_w or rng.random() < 0.05:
            cur, cur_w = cand, w
        if w < best_w:
            best_w, best_o = w, list(cand)
            if best_w <= target:
                break
    return best_w, best_o, iters


def main():
    out = {}
    p = 67
    g = qr_gen(p)
    arcs = circulant_arcs(p, g)
    out["p"] = p
    out["g_size"] = len(g)
    out["is_tournament"] = core.is_tournament(p, arcs)
    print("is_tournament(QR_67):", out["is_tournament"], "|g|=", len(g), flush=True)

    # ---- (A) dom(QR_67) = 5 ----
    t0 = time.time()
    N0 = {0} | set(g)
    dA = dom_additive_cover(p, N0, ub=6)
    out["dom_QR67_additive"] = dA
    out["dom_check_time_s"] = round(time.time() - t0, 2)
    out["pred_A_dom_eq_5"] = (dA == 5)
    print("(A) dom(QR_67) additive cover =", dA, " (pred 5):", dA == 5,
          f"[{out['dom_check_time_s']}s]", flush=True)

    # ---- (D) Paley scan: dom for p=3 mod4 primes < 67, and dom>=5 first at 67 ----
    paley = []
    for q in [7, 11, 19, 23, 31, 43, 47, 59, 67]:
        gg = qr_gen(q)
        aa = circulant_arcs(q, gg)
        N0q = {0} | set(gg)
        dq = dom_additive_cover(q, N0q, ub=6)
        paley.append({"p": q, "dom": dq})
        print(f"(D) Paley p={q} dom={dq}", flush=True)
    out["paley_dom_scan"] = paley
    below67 = [r for r in paley if r["p"] < 67]
    out["pred_D_no_paley_dom_ge5_below_67"] = all(r["dom"] <= 4 for r in below67)
    out["pred_D_dom67_ge5"] = next(r["dom"] for r in paley if r["p"] == 67) >= 5

    # ---- (B) order search target backedge clique = 5 on QR_67 ----
    # foreground, hard time budget
    budget = 700
    t0 = time.time()
    best_w, best_o, iters = sa_order_for_target(p, arcs, target=5,
                                                time_budget=budget, seed=12345)
    out["B_search_time_s"] = round(time.time() - t0, 2)
    out["B_iters"] = iters
    out["B_best_backedge_clique"] = best_w
    # verify with canonical oracle
    out["B_verify_omega_of_order"] = core.omega_of_order(p, arcs, best_o)
    out["pred_B_found_clique5_order"] = (best_w <= 5)
    print(f"(B) best backedge clique found = {best_w} (verify={out['B_verify_omega_of_order']})"
          f" after {iters} iters [{out['B_search_time_s']}s]; target=5 reached:",
          best_w <= 5, flush=True)

    # window conclusion
    lb = 5 if out["pred_A_dom_eq_5"] else None
    out["omega_vec_window"] = [lb, best_w]

    dp = os.path.join(os.path.dirname(__file__), "..", "data", "ground_dom_dual_qr67.json")
    with open(os.path.abspath(dp), "w") as f:
        json.dump(out, f, indent=2)
    print("\n=== SUMMARY ===")
    print(json.dumps({k: v for k, v in out.items() if k != "paley_dom_scan"}, indent=2))


if __name__ == "__main__":
    main()
