"""next_action lever (A): scan single-orbit circulants on Z/n for dom >= 6.

Property 3.2 (paper, dom(T) <= omega_vec(T)) => dom>=6 forces omega_vec>=6 for FREE.
If ANY non-Paley single-orbit circulant on Z/n with n < 67 reaches dom >= 6, that
KILLS the H18 barrier (cheap two-sided cert to k=6) and is a free omega_vec>=6 lower bound.

dom of a circulant C_n(g): closed out-neighborhood of vertex 0 is N0 = {0} | g.
By vertex-transitivity, dom = smallest number of translates of N0 that cover Z/n
(a cyclic covering-code / set-cover problem on Z/n).

dom <= s  iff  exist offsets t_1..t_s with union_i (N0 + t_i) == Z/n.
dom >= 6  iff  NO 5 translates of N0 cover Z/n.

We compute dom exactly via a covering check. |N0|=(n+1)/2 (>n/2), so 2 translates
nearly cover; dom is typically very small. We compute dom by greedy lower bound +
exact small-s cover search (ILP-free: bitmask set cover over n translates, capped).

The Paley dom-ceiling (ground_dom_dual_qr67 / ground_paley_dom) says dom>=6 is first
reachable at p=67 (Paley). This scan asks: does ANY single-orbit circulant of order < 67
reach dom>=6?  (lever A of next_action). Also report the MAX dom found per n.

Exact dom via exact set-cover: universe Z/n, sets = {N0 + t : t in Z/n} (each a translate,
n distinct sets). dom = min sets covering universe. Since |N0|>n/2, dom is small (2..6).
We search s = 2,3,4,5 for a cover; if none, dom>=6.
"""
import sys, os, json, time, random, itertools
sys.path.insert(0, os.path.dirname(__file__))


def valid(n, g):
    g = set(g)
    ng = set((n - x) % n for x in g)
    return len(g) == (n - 1) // 2 and not (g & ng) and (g | ng) == set(range(1, n))


def N0_mask(n, g):
    """Bitmask of closed out-neighborhood of 0: {0} | g."""
    m = 1  # vertex 0
    for x in g:
        m |= (1 << (x % n))
    return m


def rot(mask, t, n, full):
    """Rotate bitmask by t (translate set by +t mod n)."""
    return ((mask << t) | (mask >> (n - t))) & full


def dom_circulant(n, g, cap=6):
    """Exact domination number of circulant C_n(g) via cyclic set cover.
    Returns dom if dom <= cap else cap+1 (meaning dom > cap, i.e. dom >= cap+1)."""
    full = (1 << n) - 1
    base = N0_mask(n, g)
    # all n translates (by vertex-transitivity one set per offset)
    sets = [rot(base, t, n, full) for t in range(n)]
    # quick: dom=1 iff some set == full (only if |N0|=n, impossible here since g!=all)
    for s in sets:
        if s == full:
            return 1
    # exact cover search for s = 2..cap, with greedy-style pruning.
    # Since translates: fix first translate = base (t=0) WLOG? NO -- cyclic symmetry lets
    # us fix the FIRST chosen translate to t=0 (rotate any cover so one set is base).
    # That reduces the search: remaining s-1 translates from all n offsets.
    for s in range(2, cap + 1):
        # need s sets covering full; fix first = base (sound by cyclic symmetry)
        # remaining s-1 chosen from offsets 0..n-1 (allow repeats irrelevant; use combos w/ t1=0)
        need = full & ~base
        # DFS over offsets to cover `need` with s-1 more translates
        if _cover_dfs(need, sets, s - 1, 0, n):
            return s
    return cap + 1


def _cover_dfs(remaining, sets, k, start, n):
    if remaining == 0:
        return True
    if k == 0:
        return False
    # pick lowest uncovered bit, must be covered by one of the chosen translates
    # (branch on which translate covers it) -- this is the standard set-cover acceleration
    low = remaining & (-remaining)
    pos = low.bit_length() - 1
    for t in range(n):
        if sets[t] & low:
            if _cover_dfs(remaining & ~sets[t], sets, k - 1, t, n):
                return True
    return False


def main():
    random.seed(7)
    # Paley generators (QR set) for reference; dom-ceiling says dom>=6 first at p=67.
    out = {"per_n": [], "dom6_witnesses": []}
    # scan odd n in [37, 65]; for each, sample many valid single-orbit generators,
    # compute dom exactly (cheap), track max dom and any dom>=6.
    ns = list(range(37, 66, 2))  # 37..65 odd
    SAMPLES = 3000
    for n in ns:
        m = (n - 1) // 2
        max_dom = 0
        max_g = None
        dom_hist = {}
        tested = 0
        seen = set()
        t_start = time.time()
        for _ in range(SAMPLES):
            g = frozenset(x if random.random() < 0.5 else n - x for x in range(1, m + 1))
            if g in seen or not valid(n, g):
                continue
            seen.add(g)
            d = dom_circulant(n, g, cap=6)
            tested += 1
            dom_hist[d] = dom_hist.get(d, 0) + 1
            if d > max_dom:
                max_dom = d
                max_g = sorted(g)
            if d >= 6:
                out["dom6_witnesses"].append({"n": n, "g": sorted(g), "dom": d})
                print(f"*** DOM>=6 WITNESS n={n} g={sorted(g)} dom={d} ***", flush=True)
            if time.time() - t_start > 120:
                break
        rec = {"n": n, "tested": tested, "max_dom": max_dom, "max_g": max_g,
               "dom_hist": {str(k): v for k, v in sorted(dom_hist.items())},
               "time_s": round(time.time() - t_start, 1)}
        out["per_n"].append(rec)
        print(f"n={n}: tested={tested} max_dom={max_dom} hist={rec['dom_hist']} ({rec['time_s']}s)", flush=True)
    print("=== SUMMARY ===", flush=True)
    print("dom>=6 witnesses:", out["dom6_witnesses"], flush=True)
    dp = os.path.join(os.path.dirname(__file__), "..", "data", "dom6_scan.json")
    os.makedirs(os.path.dirname(os.path.abspath(dp)), exist_ok=True)
    with open(os.path.abspath(dp), "w") as f:
        json.dump(out, f, indent=2)


if __name__ == "__main__":
    main()
