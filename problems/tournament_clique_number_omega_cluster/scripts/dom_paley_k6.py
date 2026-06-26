"""EXACT domination number of Paley tournaments QR_p via bitset branch-and-bound.

Arc convention (matches ground_paley_dom.py / probe_p19.py):
  i -> (i+d) mod p for d in g, g = quadratic residues mod p (p % 4 == 3).
Closed out-neighborhood N^+[v] = {v} | {v+d : d in g} = v + N0, N0 = {0} | QR_p.

dom(T) = min # of closed out-neighborhoods whose union = Z/p.

Bitset model: closed_mask[v] = p-bit Python int; full = (1<<p)-1.
We want the minimum number of masks (any vertices) whose OR == full.

By vertex-transitivity every minimum cover is a translate of one containing
vertex 0, so for the dom>=6 certificate we FIX mask[0] in the cover and search
for 4 more (i.e. decide whether dom<=5 with 0 in the cover). If no size-<=5
cover containing 0 exists, then by transitivity no size-<=5 cover exists at all.

We use exact set-cover branch & bound with a greedy lower bound:
  remaining uncovered set U; best single mask covers at most maxcov elements;
  lower bound on #masks still needed >= ceil(|U|/maxcov). Prune when
  depth + ceil(|U|/maxcov) >= best.
This is exact (finds the true minimum) and fast for these structured instances.
"""
import sys, os, json, time, math

def qr_set(p):
    return sorted({(x * x) % p for x in range(1, p)})

def build_masks(p):
    qr = qr_set(p)
    N0 = [0] + qr
    masks = []
    for v in range(p):
        m = 0
        for d in N0:
            m |= (1 << ((v + d) % p))
        masks.append(m)
    return masks

def popcount(x):
    return bin(x).count("1")

def exact_dom(p, masks, cap):
    """Exact minimum set cover size, but stop/return cap+1 if min > cap.
    Returns the true dom if dom <= cap, else cap+1.
    Uses fix-vertex-0 symmetry: every cover has a translate containing 0,
    so a minimum cover containing vertex 0 exists; we force mask[0] in."""
    full = (1 << p) - 1
    nbits = [popcount(m) for m in masks]
    maxcov_global = max(nbits)
    best = [cap + 1]  # upper bound on dom; we want to know if <= cap

    # Forced first pick: vertex 0 (symmetry). depth counts picks made.
    sys.setrecursionlimit(10000)

    def lb_needed(U):
        # lower bound on additional masks to cover U: ceil(|U| / maxcov_global)
        if U == 0:
            return 0
        return -(-popcount(U) // maxcov_global)

    def search(U, depth, last_idx):
        # U = still-uncovered bitset; depth = masks already chosen
        if U == 0:
            if depth < best[0]:
                best[0] = depth
            return
        if depth + lb_needed(U) >= best[0]:
            return
        # choose an uncovered vertex with the FEWEST covering masks (MRV heuristic)
        # to branch on which mask covers it. Find lowest set bit of U.
        # pick the uncovered element v0 = lowest bit
        v0 = (U & -U).bit_length() - 1
        # candidate masks: those that cover v0 (i.e. v0 in mask)
        # iterate masks covering v0, ordered by coverage of U descending
        cands = []
        for idx, m in enumerate(masks):
            if (m >> v0) & 1:
                cands.append((popcount(m & U), idx, m))
        cands.sort(reverse=True)
        for cov, idx, m in cands:
            if depth + 1 + lb_needed(U & ~m) >= best[0] and (U & ~m) != 0:
                # prune if even after this pick we can't beat best
                # (still must allow exact when U&~m==0 handled above)
                pass
            search(U & ~m, depth + 1, idx)
            if best[0] <= depth + 1:
                # can't do better than current depth+1 from this node
                pass

    # force vertex 0 in: start with U = full & ~masks[0], depth=1
    search(full & ~masks[0], 1, 0)
    return best[0]

def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("primes", nargs="*", type=int)
    ap.add_argument("--cap", type=int, default=6)
    args = ap.parse_args()

    primes = args.primes or [199, 211, 223, 227, 239, 251]
    cap = args.cap
    out = []
    for p in primes:
        if p % 4 != 3:
            print(f"p={p}: SKIP (p%4={p%4}, not a Paley tournament prime)", flush=True)
            continue
        masks = build_masks(p)
        # sanity: union of all masks == full
        u = 0
        for m in masks:
            u |= m
        assert u == (1 << p) - 1, f"masks do not cover Z/{p}"
        t0 = time.time()
        d = exact_dom(p, masks, cap)
        dt = round(time.time() - t0, 2)
        res = "%d" % d if d <= cap else ">%d" % cap
        print(f"p={p}: exact dom = {res}   ({dt}s)", flush=True)
        out.append({"p": p, "dom": d if d <= cap else None, "dom_cap": cap,
                    "dom_str": res, "time_s": dt})
    print(json.dumps(out))

if __name__ == "__main__":
    main()
