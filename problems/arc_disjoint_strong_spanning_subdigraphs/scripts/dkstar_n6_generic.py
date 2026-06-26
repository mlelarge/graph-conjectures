"""GENERIC EXHAUSTIVE n=6 census for DK*(alpha) — the universal gate.

For n=6 there are only 2^6-2 = 62 proper nonempty subsets. So for each digraph
I enumerate ALL subsets ONCE, computing simultaneously:
  - lambda = min over proper nonempty X of |delta^+(X)|  (EXACT arc-strong conn;
    for a strongly-connected digraph this equals arc-strong connectivity),
  - the distinct labeled arc-sets delta^+(X) bucketed by size.
Then DK*(alpha) ratio = #distinct arc-sets of size<=alpha*lambda / n^{2alpha}.

This sidesteps the per-graph oracle call (the census bottleneck): lambda is
computed directly from the same subset sweep, EXACTLY. I only keep digraphs that
are strongly connected (lambda>=1). Generation: geng -c 6 | directg -T (ALL
orientations incl digons, ALL lambda strata) — the full generic class at n=6,
NOT a structured sub-family.

KILL = any digraph+alpha with ratio>1.
"""
import sys, os, json, time, subprocess

ALPHAS = [("1", 1.0), ("4/3", 4.0/3.0), ("5/3", 5.0/3.0), ("2", 2.0)]
N = 6
DENOM = {lbl: N ** (2.0*a) for (lbl, a) in ALPHAS}


def census_one(arcs):
    """Return (lambda, {alpha: n_distinct_arcsets}) or None if not strong."""
    larcs = [(i, u, v) for i, (u, v) in enumerate(arcs)]
    # precompute per-subset out-arc-set; track min cut and arcsets by size
    by_size = {}  # size -> set of frozenset(labels)
    lam = 10**9
    full = (1 << N) - 1
    for mask in range(1, full):  # 1..full-1 => proper nonempty
        F = frozenset(i for (i, u, v) in larcs
                      if ((mask >> u) & 1) and not ((mask >> v) & 1))
        s = len(F)
        if s == 0:
            return None  # not strongly connected
        if s < lam:
            lam = s
        by_size.setdefault(s, set()).add(F)
    res = {}
    for (lbl, a) in ALPHAS:
        thr = a * lam
        cnt = set()
        for s, fs in by_size.items():
            if s <= thr:
                cnt |= fs
        res[lbl] = len(cnt)
    return lam, res


def gen():
    geng = subprocess.Popen(["geng", "-cq", str(N)], stdout=subprocess.PIPE)
    directg = subprocess.Popen(["directg", "-Tq"], stdin=geng.stdout,
                               stdout=subprocess.PIPE)
    geng.stdout.close()
    for line in directg.stdout:
        toks = line.split()
        if not toks:
            continue
        nums = list(map(int, toks[2:]))
        arcs = [(nums[i], nums[i+1]) for i in range(0, len(nums), 2)]
        yield arcs
    directg.wait(); geng.wait()


def main():
    t0 = time.time()
    nread = 0; nstrong = 0
    worst = {lbl: -1.0 for (lbl, _a) in ALPHAS}
    worst_info = {lbl: None for (lbl, _a) in ALPHAS}
    kills = []
    lam_hist = {}
    for arcs in gen():
        nread += 1
        r = census_one(arcs)
        if r is None:
            continue
        nstrong += 1
        lam, res = r
        lam_hist[lam] = lam_hist.get(lam, 0) + 1
        for (lbl, a) in ALPHAS:
            ratio = res[lbl] / DENOM[lbl]
            if ratio > worst[lbl]:
                worst[lbl] = ratio
                worst_info[lbl] = {"ratio": round(ratio, 5), "lambda": lam,
                                   "n_arcsets": res[lbl],
                                   "arcs": [list(x) for x in arcs]}
            if ratio > 1.0:
                kills.append({"alpha": lbl, "ratio": round(ratio, 5),
                              "lambda": lam, "n_arcsets": res[lbl],
                              "arcs": [list(x) for x in arcs]})
    out = {"elapsed_s": round(time.time()-t0, 2),
           "n": N, "n_read": nread, "n_strong": nstrong,
           "lambda_hist": dict(sorted(lam_hist.items())),
           "worst_ratio_per_alpha": {k: round(v, 5) for k, v in worst.items()},
           "worst_info": worst_info,
           "n_kills": len(kills),
           "kills_first5": kills[:5],
           "DKstar_survives_n6": len(kills) == 0}
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
