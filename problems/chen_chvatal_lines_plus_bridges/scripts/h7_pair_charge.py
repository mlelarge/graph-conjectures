"""H7 PAIR-INDEXED / shell x shell line-charge functionals for the H5 lever.

Context (ledger D3/D4, graveyard G3+G5): EVERY low-dimensional base-vertex
charge is barred -- diametral-pairs, the single-geodesic spine (G3), the
peripheral pencil/bipencil (G5). The UNIFYING BARRIER says any functional
charging lines to a BOUNDED set of base vertices captures only an O(diam)
fraction of ell, while the surplus that makes ell>=n is GLOBAL-PAIR
(Theta(n^2)). So a surviving H5 lower bound must charge to PAIRS or to
shell x shell adjacency classes.

This script SPECIFIES and oracle-gates several concrete PAIR-INDEXED
functionals, each a PROVABLE SUBSET-OF-LINES lower bound on ell(G) (each is
|{distinct lines over an explicitly exhibited subset of pairs}|, hence <=
ell(G)). For each it reports, over every connected pendant-free diam>=4
graph at the requested orders:

  * value of the functional,
  * margin (functional - n) and whether >= n (the H5 target),
  * minimum margin / #below-n over all graphs of that order,
  * explicit non-collapse behaviour on the three base-vertex-collapse
    witnesses g6 = 'G?B@vo' (n=8), 'H?ABCp{' (n=9), 'H?bB@aW' (n=9).

The pair-indexed functionals (all are distinct-line counts over a chosen
subset P of pairs, so each <= ell):

  F_far(t)      : P = { (a,b) : d(a,b) >= diam - t }.  Lines determined by
                  FAR pairs only. t=0 = diametral pairs; t increases the net.
                  (Pure pair charge -- no fixed base vertex.)

  F_periphery   : P = { (a,b) : ecc(a)=diam AND ecc(b)=diam }.  Lines among
                  the peripheral vertices (shell-d x shell-d cross class).

  F_shellcross  : partition all C(n,2) pairs by the UNORDERED distance class
                  k = d(a,b) in {1..diam}; count, per class k, the number of
                  DISTINCT lines realized by pairs at distance k; report the
                  SUM of per-class distinct-line counts WITH double-counting
                  removed globally (= |all lines from pairs of any distance| =
                  ell, trivial) AND the per-class distinct counts themselves
                  (to LOWER-BOUND bucket SIZES -- the G6 caveat).

  F_nonuniv_far : P = { (a,b): d(a,b) >= diam-1 }, count distinct NON-universal
                  lines only (drop the all-V line). Targets the surplus the
                  universal line cannot absorb.

  F_antipodal_match : pick a maximal set of pairwise 'far' pairs (a greedy
                  matching on the far-pair graph) and count their distinct
                  lines; a Theta(n)-sized pair family by construction.

Every value <= ell(G); F >= n  ==>  ell(G) >= n  ==>  not bad on diam>=4.
"""
from __future__ import annotations
import json
import subprocess
import sys

import core


def diameter_and_ecc(dist, n):
    ecc = [0] * n
    for u in range(n):
        m = 0
        for v in range(n):
            if dist[u][v] is not None and dist[u][v] > m:
                m = dist[u][v]
        ecc[u] = m
    return max(ecc), ecc


def all_pair_lines(dist, n):
    """dict: (a,b) -> frozenset line(a,b); plus d(a,b). a<b."""
    L = {}
    for a in range(n):
        for b in range(a + 1, n):
            L[(a, b)] = core.line_of_pair(dist, n, a, b)
    return L


def functionals(n, edges):
    dist = core.all_pairs_distances(n, edges)
    d, ecc = diameter_and_ecc(dist, n)
    if d < 4:
        return None
    pl = all_pair_lines(dist, n)
    univ = frozenset(range(n))

    # ----- F_far(t): distinct lines from pairs at distance >= d - t -----
    def F_far(t, nonuniv=False):
        S = set()
        for (a, b), L in pl.items():
            if dist[a][b] >= d - t:
                if nonuniv and L == univ:
                    continue
                S.add(L)
        return len(S)

    f_far0 = F_far(0)
    f_far1 = F_far(1)
    f_far2 = F_far(2)
    f_far1_nu = F_far(1, nonuniv=True)
    f_far2_nu = F_far(2, nonuniv=True)

    # ----- F_periphery: lines among peripheral (ecc=d) vertices -----
    peri = [v for v in range(n) if ecc[v] == d]
    S = set()
    for i in range(len(peri)):
        for j in range(i + 1, len(peri)):
            a, b = peri[i], peri[j]
            if a > b:
                a, b = b, a
            S.add(pl[(a, b)])
    f_periphery = len(S)

    # ----- per-distance-class distinct-line buckets (lower-bound bucket SIZE) -----
    by_dist = {}  # k -> set of distinct lines
    for (a, b), L in pl.items():
        by_dist.setdefault(dist[a][b], set()).add(L)
    per_class = {k: len(v) for k, v in sorted(by_dist.items())}
    # the sum of per-class distinct counts (overcounts shared lines across classes,
    # but is a genuine "if buckets are big" diagnostic)
    sum_per_class = sum(per_class.values())
    max_class = max(per_class.values())

    # ----- F_antipodal_match: greedy matching on the far(d) pair graph -----
    far_pairs = [(a, b) for (a, b) in pl if dist[a][b] >= d - 1]
    used = set()
    matched_lines = set()
    for (a, b) in far_pairs:
        if a in used or b in used:
            continue
        used.add(a); used.add(b)
        matched_lines.add(pl[(a, b)])
    f_match = len(matched_lines)

    return {
        "n": n, "diam": d,
        "f_far0": f_far0, "f_far1": f_far1, "f_far2": f_far2,
        "f_far1_nonuniv": f_far1_nu, "f_far2_nonuniv": f_far2_nu,
        "f_periphery": f_periphery,
        "f_match": f_match,
        "sum_per_class": sum_per_class,
        "max_class": max_class,
        "per_class": per_class,
        "ell_true": None,  # filled by witness path only (expensive globally)
    }


FUNCS = ["f_far0", "f_far1", "f_far2", "f_far1_nonuniv",
         "f_far2_nonuniv", "f_periphery", "f_match",
         "sum_per_class", "max_class"]


def run_n(N):
    cmd = ["geng", "-c", "-q", "-d2", str(N)]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr)
    total = 0
    min_margin = {f: None for f in FUNCS}
    n_below = {f: 0 for f in FUNCS}
    worst = {f: None for f in FUNCS}
    for line in proc.stdout.splitlines():
        s = line.strip()
        if not s:
            continue
        n, edges = core.graph6_to_edges(s)
        if core.has_pendant_edge(n, edges):
            continue
        r = functionals(n, edges)
        if r is None:
            continue
        total += 1
        for f in FUNCS:
            margin = r[f] - n
            if margin < 0:
                n_below[f] += 1
            if min_margin[f] is None or margin < min_margin[f]:
                min_margin[f] = margin
                worst[f] = {"g6": s, "f": r[f], "margin": margin, "diam": r["diam"]}
    return {
        "N": N,
        "total_diam_ge4_pendant_free": total,
        "min_margin": min_margin,
        "n_below_n": n_below,
        "worst": worst,
    }


def witness_report():
    out = {}
    for g6 in ["G?B@vo", "H?ABCp{", "H?bB@aW"]:
        n, edges = core.graph6_to_edges(g6)
        r = functionals(n, edges)
        if r is None:
            out[g6] = {"note": "diam<4 (unexpected)"}
            continue
        r = dict(r)
        r["ell_true"] = core.ell(n, edges)
        # collapse = best far/periphery functional is <= 1 (i.e. only universal)
        r["collapses"] = max(r["f_far1"], r["f_periphery"], r["f_match"]) <= 1
        out[g6] = r
    return out


if __name__ == "__main__":
    Ns = [int(x) for x in sys.argv[1:]] or [8, 9]
    print("=== H7 WITNESS (non-collapse) REPORT ===", flush=True)
    print(json.dumps(witness_report(), indent=2), flush=True)
    print("=== H7 PAIR-CHARGE GATE over diam>=4 pendant-free ===", flush=True)
    results = {}
    for N in Ns:
        res = run_n(N)
        results[str(N)] = res
        print(json.dumps(res, indent=2), flush=True)
    print("=== SUMMARY ===", flush=True)
    print(json.dumps({n: {
        "total": r["total_diam_ge4_pendant_free"],
        "min_margin": r["min_margin"],
        "n_below_n": r["n_below_n"],
    } for n, r in results.items()}, indent=2), flush=True)
