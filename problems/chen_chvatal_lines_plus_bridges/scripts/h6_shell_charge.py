"""H6 GLOBAL BFS-shell line-charge functional for the H5 lever.

Context (ledger D3 / G3): the single-geodesic SPINE route to
'pendant-free + diam>=4 => ell(G)>=|G|' is DEAD -- the spine lines
line(v0,vi) along one longest geodesic collapse (often to the universal
line). The residual H6 must charge lines GLOBALLY and must NOT collapse on
the spine-route witnesses g6='G?B@vo' (n=8) and 'H?ABCp{' (n=9).

This script specifies and oracle-gates SEVERAL concrete shell-indexed
line-charging functionals, each a LOWER BOUND on ell(G) by construction
(each is the cardinality of an explicitly exhibited SUBSET of the set of
all lines), and reports, over every connected pendant-free diam>=4 graph
at given orders:

  * the value of the functional,
  * whether it is >= n (the H5 target),
  * the minimum margin (functional - n) over all graphs of that order,
  * explicit behaviour on the two G3 witnesses (does it collapse?).

Functionals (each charges to a peripheral-vertex pencil / shells):

  F_pencil(v0)  = |{ line(v0, w) : w in V, w != v0 }|
        the PENCIL of lines through a fixed peripheral vertex v0.
        (Superset-aware lower bound on ell; the dead spine route used only
         the w lying on ONE geodesic -- this uses ALL w.)
  F_pencil_max  = max over peripheral v0 of F_pencil(v0).
  F_pencil_min  = min over peripheral v0 of F_pencil(v0)  (worst case).

  F_shell_new   = a shell-stratified count: process shells S_0..S_d in
        order of distance from v0; a line is 'charged to shell k' if its
        defining pair (v0,w) has w in S_k and the line is not equal to any
        line already charged at a strictly smaller shell index. This is
        exactly |F_pencil| but reported per-shell to expose WHERE lines are
        born (diagnostic for a future symbolic shell-by-shell bound).

  F_bipencil    = |{ line(v0,w) } U { line(vd,w) }| using BOTH endpoints of
        a longest geodesic (v0 peripheral, vd a farthest vertex). A larger,
        still-explicit subset of lines.

'peripheral v0' = a vertex whose eccentricity equals the diameter d
(so some w has dist(v0,w)=d). Every functional value is <= ell(G), so
F >= n  ==>  ell(G) >= n  ==>  G is not bad on the diam>=4 axis.
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
    d = max(ecc)
    return d, ecc


def pencil_lines(dist, n, v0):
    """Set of distinct lines line(v0, w), w != v0."""
    S = set()
    for w in range(n):
        if w == v0:
            continue
        S.add(core.line_of_pair(dist, n, v0, w))
    return S


def shell_birth(dist, n, v0):
    """Per-shell line birth: shells S_k = {w: dist(v0,w)=k}. Returns a list
    new_per_shell[k] = number of pencil lines line(v0,w), w in S_k, not
    already seen at a strictly smaller shell index, plus cumulative."""
    d = max(x for x in dist[v0] if x is not None)
    shells = [[] for _ in range(d + 1)]
    for w in range(n):
        dk = dist[v0][w]
        shells[dk].append(w)
    seen = set()
    new_per_shell = []
    for k in range(d + 1):
        cnt = 0
        for w in shells[k]:
            if w == v0:
                continue
            L = core.line_of_pair(dist, n, v0, w)
            if L not in seen:
                seen.add(L)
                cnt += 1
        new_per_shell.append(cnt)
    return new_per_shell, len(seen)


def analyze_graph(g6, n, edges):
    dist = core.all_pairs_distances(n, edges)
    d, ecc = diameter_and_ecc(dist, n)
    if d < 4:
        return None
    peripheral = [v for v in range(n) if ecc[v] == d]

    pencil_vals = {v: len(pencil_lines(dist, n, v)) for v in peripheral}
    f_pencil_max = max(pencil_vals.values())
    f_pencil_min = min(pencil_vals.values())

    # bi-pencil over a (v0 peripheral, vd farthest) pair
    f_bipencil = 0
    best_pair = None
    for v0 in peripheral:
        # a farthest vertex from v0
        vd = max(range(n), key=lambda w: (dist[v0][w] if dist[v0][w] is not None else -1))
        S = pencil_lines(dist, n, v0) | pencil_lines(dist, n, vd)
        if len(S) > f_bipencil:
            f_bipencil = len(S)
            best_pair = (v0, vd)

    return {
        "g6": g6, "n": n, "diam": d,
        "f_pencil_max": f_pencil_max,
        "f_pencil_min": f_pencil_min,
        "f_bipencil": f_bipencil,
        "n_peripheral": len(peripheral),
    }


def run_n(N, witness_detail=False):
    cmd = ["geng", "-c", "-q", "-d2", str(N)]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr)
    total = 0
    # track min margins for each functional
    min_margin = {"pencil_max": None, "pencil_min": None, "bipencil": None}
    n_below = {"pencil_max": 0, "pencil_min": 0, "bipencil": 0}
    worst = {"pencil_max": None, "pencil_min": None, "bipencil": None}
    for line in proc.stdout.splitlines():
        s = line.strip()
        if not s:
            continue
        n, edges = core.graph6_to_edges(s)
        if core.has_pendant_edge(n, edges):
            continue
        r = analyze_graph(s, n, edges)
        if r is None:
            continue
        total += 1
        for key, fval in (("pencil_max", r["f_pencil_max"]),
                          ("pencil_min", r["f_pencil_min"]),
                          ("bipencil", r["f_bipencil"])):
            margin = fval - n
            if margin < 0:
                n_below[key] += 1
            if min_margin[key] is None or margin < min_margin[key]:
                min_margin[key] = margin
                worst[key] = {"g6": s, "n": n, "diam": r["diam"], "f": fval, "margin": margin}
    return {
        "N": N,
        "total_diam_ge4_pendant_free": total,
        "min_margin": min_margin,
        "n_below_n": n_below,
        "worst": worst,
    }


def witness_report():
    out = {}
    for g6 in ["G?B@vo", "H?ABCp{"]:
        n, edges = core.graph6_to_edges(g6)
        dist = core.all_pairs_distances(n, edges)
        d, ecc = diameter_and_ecc(dist, n)
        peripheral = [v for v in range(n) if ecc[v] == d]
        per_v = {}
        for v0 in peripheral:
            nps, total = shell_birth(dist, n, v0)
            per_v[v0] = {"new_per_shell": nps, "pencil_size": total}
        f_pencil_max = max(p["pencil_size"] for p in per_v.values())
        f_pencil_min = min(p["pencil_size"] for p in per_v.values())
        out[g6] = {
            "n": n, "diam": d, "ell_true": core.ell(n, edges),
            "n_peripheral": len(peripheral),
            "f_pencil_max": f_pencil_max,
            "f_pencil_min": f_pencil_min,
            "collapses": f_pencil_min <= 1,  # spine route collapsed to 1 (universal) line
            "per_peripheral_shell_birth": per_v,
        }
    return out


if __name__ == "__main__":
    Ns = [int(x) for x in sys.argv[1:]] or [8, 9, 10]
    print("=== G3 WITNESS (non-collapse) REPORT ===", flush=True)
    wr = witness_report()
    print(json.dumps(wr, indent=2), flush=True)
    print("=== SHELL-CHARGE GATE over diam>=4 pendant-free ===", flush=True)
    results = {}
    for N in Ns:
        res = run_n(N)
        results[str(N)] = res
        print(json.dumps(res, indent=2), flush=True)
    print("=== SUMMARY (min margin = min over graphs of F - n) ===")
    print(json.dumps({n: {
        "total": r["total_diam_ge4_pendant_free"],
        "min_margin": r["min_margin"],
        "n_below_n": r["n_below_n"],
    } for n, r in results.items()}, indent=2))
