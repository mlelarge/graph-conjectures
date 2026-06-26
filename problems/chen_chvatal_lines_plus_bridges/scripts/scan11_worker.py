"""Streaming parallel falsification scanner for scan(n=11) — H1/H4 gate.

Reads graph6 lines (one per line) from stdin (intended: `geng -c -d2 -q n`),
distributes to worker processes, reports every BAD graph
(connected, pendant-free, ell+br < n), with diameter.

Pure-Python exact invariants (no networkx in the hot path): same metric /
line / bridge semantics as scripts/core.py, independently re-derived here and
asserted equal to core on the n<=8 bad set (see scan11_selftest.py) before
the big run.

Usage:
    geng -c -d2 -q 11 | python scan11_worker.py 11 --procs 8 --out data/scan_n11.json
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from collections import deque
from multiprocessing import Pool


def graph6_to_edges(line):
    b = line.strip().encode("ascii")
    if not b:
        return 0, []
    n = b[0] - 63
    bits = []
    for ch in b[1:]:
        v = ch - 63
        for k in range(5, -1, -1):
            bits.append((v >> k) & 1)
    edges, idx = [], 0
    for j in range(1, n):
        for i in range(j):
            if idx < len(bits) and bits[idx]:
                edges.append((i, j))
            idx += 1
    return n, edges


def adj_of(n, edges):
    adj = [[] for _ in range(n)]
    for (u, v) in edges:
        adj[u].append(v)
        adj[v].append(u)
    return adj


def all_pairs(n, adj):
    dist = [[-1] * n for _ in range(n)]
    for s in range(n):
        ds = dist[s]
        ds[s] = 0
        q = deque([s])
        while q:
            u = q.popleft()
            du = ds[u]
            for w in adj[u]:
                if ds[w] < 0:
                    ds[w] = du + 1
                    q.append(w)
    return dist


def count_lines_and_diam(n, dist):
    lines = set()
    diam = 0
    rng = range(n)
    for a in rng:
        da = dist[a]
        for b in range(a + 1, n):
            dab = da[b]
            if dab > diam:
                diam = dab
            db = dist[b]
            pts = 0
            for x in rng:
                if x == a or x == b:
                    pts |= (1 << x)
                    continue
                dax = da[x]
                dbx = db[x]
                if dax + dbx == dab or dab + dbx == dax or dax + dab == dbx:
                    pts |= (1 << x)
            lines.add(pts)
    return len(lines), diam


def bridges_count(n, adj):
    """Number of bridges (cut edges) in a simple graph, iterative Tarjan."""
    disc = [-1] * n
    low = [0] * n
    cnt = 0
    timer = 0
    for root in range(n):
        if disc[root] != -1:
            continue
        # stack entries: [node, parent, neighbor-index, parent-edge-skipped]
        stack = [[root, -1, 0, False]]
        disc[root] = low[root] = timer
        timer += 1
        while stack:
            entry = stack[-1]
            u, parent, i, skipped = entry
            au = adj[u]
            descended = False
            while i < len(au):
                w = au[i]
                i += 1
                if w == parent and not skipped:
                    skipped = True
                    continue
                if disc[w] == -1:
                    disc[w] = low[w] = timer
                    timer += 1
                    entry[2] = i
                    entry[3] = skipped
                    stack.append([w, u, 0, False])
                    descended = True
                    break
                else:
                    if disc[w] < low[u]:
                        low[u] = disc[w]
            if not descended:
                entry[2] = i
                entry[3] = skipped
                stack.pop()
                if stack:
                    pu = stack[-1][0]
                    if low[u] < low[pu]:
                        low[pu] = low[u]
                    if low[u] > disc[pu]:
                        cnt += 1
    return cnt


def classify(line):
    n, edges = graph6_to_edges(line)
    if n == 0:
        return None
    adj = adj_of(n, edges)
    for a in adj:
        if len(a) < 2:
            return None  # has pendant (or isolated); geng -d2 should preclude
    dist = all_pairs(n, adj)
    ell, diam = count_lines_and_diam(n, dist)
    if ell >= n:
        return None  # br>=0 so ell+br>=n, not bad
    br = bridges_count(n, adj)
    if ell + br < n:
        return {"graph6": line.strip(), "n": n, "m_edges": len(edges),
                "ell": ell, "br": br, "ell_plus_br": ell + br,
                "deficit": n - ell - br, "diam": diam}
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("n", type=int)
    ap.add_argument("--procs", type=int, default=8)
    ap.add_argument("--out", required=True)
    ap.add_argument("--chunk", type=int, default=20000)
    ap.add_argument("--limit", type=int, default=0,
                    help="stop after this many graphs (0=all); benchmarking")
    args = ap.parse_args()

    t0 = time.time()
    total = 0
    bad = []

    def gen():
        nonlocal total
        for line in sys.stdin:
            s = line.strip()
            if not s:
                continue
            total += 1
            if args.limit and total > args.limit:
                break
            yield s

    with Pool(args.procs) as pool:
        for res in pool.imap_unordered(classify, gen(), chunksize=args.chunk):
            if res is not None:
                bad.append(res)
                with open(args.out, "w") as f:
                    json.dump({"n": args.n, "n_seen_so_far": total,
                               "n_bad": len(bad), "bad": bad,
                               "elapsed_sec": time.time() - t0,
                               "complete": False}, f, indent=2)

    out = {"n": args.n, "n_scanned": total, "n_bad": len(bad), "bad": bad,
           "elapsed_sec": time.time() - t0, "procs": args.procs,
           "complete": (args.limit == 0)}
    with open(args.out, "w") as f:
        json.dump(out, f, indent=2)
    print(json.dumps({k: out[k] for k in ("n", "n_scanned", "n_bad",
                      "elapsed_sec", "complete")}))


if __name__ == "__main__":
    main()
