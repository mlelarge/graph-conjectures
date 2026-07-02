"""Independent EXHAUSTIVE n=12 B1 census (review of the workflow's claim):
  - count 3-connected diam>=4 graphs at n=12 (claimed 479,322)
  - check B1 (D2 >= n) on every one (claimed 0 failures)
  - also recount G3 failures (claimed 3 at n=12).

Pipeline per geng -C -d3 12 m:m stream line (headerless graph6):
  1. bitmask diam>=4 filter: reject iff every vertex reaches all within 3 steps.
  2. 3-connectivity: min-deg>=3 guaranteed; brute check no 2-vertex cut (bitmask BFS).
  3. B1: D2 (#distinct distance-2 lines) >= 12; also G3 margin.
Blocking, ProcessPoolExecutor, per-band.
"""
import sys, os, subprocess, itertools, time
from concurrent.futures import ProcessPoolExecutor

N = 12
FULL = (1 << N) - 1


def parse_g6(line):
    b = line.encode()
    n = b[0] - 63
    bits = []
    for ch in b[1:]:
        v = ch - 63
        for k in range(5, -1, -1):
            bits.append((v >> k) & 1)
    adj = [0] * n
    idx = 0
    for j in range(1, n):
        for i in range(j):
            if bits[idx]:
                adj[i] |= 1 << j
                adj[j] |= 1 << i
            idx += 1
    return adj


def diam_ge4(adj):
    # reject iff all vertices reach everything within 3 steps
    for v in range(N):
        r1 = adj[v] | (1 << v)
        r2 = r1
        m = adj[v]
        while m:
            u = (m & -m).bit_length() - 1
            r2 |= adj[u]
            m &= m - 1
        if r2 == FULL:
            continue
        r3 = r2
        m = r2 & ~r1
        while m:
            u = (m & -m).bit_length() - 1
            r3 |= adj[u]
            m &= m - 1
        if r3 != FULL:
            return True
    return False


def connected_masked(adj, mask, start):
    seen = 1 << start
    frontier = seen
    while frontier:
        nxt = 0
        m = frontier
        while m:
            u = (m & -m).bit_length() - 1
            nxt |= adj[u] & mask
            m &= m - 1
        nxt &= ~seen
        seen |= nxt
        frontier = nxt
    return seen == mask


def three_connected(adj):
    for a in range(N):
        for b in range(a + 1, N):
            mask = FULL & ~(1 << a) & ~(1 << b)
            start = (mask & -mask).bit_length() - 1
            if not connected_masked(adj, mask, start):
                return False
    return True


def bfs_all(adj):
    dist = []
    for s in range(N):
        d = [-1] * N
        d[s] = 0
        frontier = 1 << s
        seen = frontier
        lev = 0
        while frontier:
            lev += 1
            nxt = 0
            m = frontier
            while m:
                u = (m & -m).bit_length() - 1
                nxt |= adj[u]
                m &= m - 1
            nxt &= ~seen
            mm = nxt
            while mm:
                u = (mm & -mm).bit_length() - 1
                d[u] = lev
                mm &= mm - 1
            seen |= nxt
            frontier = nxt
        dist.append(d)
    return dist


def analyze(line):
    adj = parse_g6(line)
    if not diam_ge4(adj):
        return None
    if not three_connected(adj):
        return None
    dist = bfs_all(adj)
    diam = max(max(r) for r in dist)
    # distance-2 lines
    lines = {}
    P2 = 0
    for a in range(N):
        for b in range(a + 1, N):
            if dist[a][b] != 2:
                continue
            P2 += 1
            L = 0
            for x in range(N):
                dax, dbx, dab = dist[a][x], dist[b][x], 2
                if dax + dbx == dab or dab + dbx == dax or dax + dab == dbx:
                    L |= 1 << x
            lines[L] = lines.get(L, 0) + 1
    D2 = len(lines)
    collisions = P2 - D2
    # G3: E(DE u N(DE)) vs 2*collisions
    ecc = [max(r) for r in dist]
    degG2 = [sum(1 for u in range(N) if dist[v][u] == 2) for v in range(N)]
    DEN = 0
    for v in range(N):
        if ecc[v] == diam:
            DEN |= (1 << v) | adj[v]
    E_DEN = 0
    m = DEN
    while m:
        u = (m & -m).bit_length() - 1
        E_DEN += degG2[u] - 2
        m &= m - 1
    return (line, D2, collisions, P2 - N, E_DEN - 2 * collisions)  # (g6, D2, coll, surplus, g3margin)


def run_band(m_edges):
    import os as _os
    rm=_os.environ.get("RESMOD")
    cmd = ["geng", "-C", "-d3", "-q", str(N), f"{m_edges}:{m_edges}"] + ([rm] if rm else [])  # RESMOD
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, text=True, bufsize=1 << 22)
    t0 = time.time()
    total = 0
    kept = 0
    b1_fail = []
    g3_fail = []
    minD2n = 10**9
    workers = max(2, (os.cpu_count() or 4) - 2)
    with ProcessPoolExecutor(max_workers=workers) as ex:
        batch = []
        def flush(batch):
            nonlocal total, kept, minD2n
            for res in ex.map(analyze, batch, chunksize=2000):
                total += 1
                if res is None:
                    continue
                kept += 1
                g6, D2, coll, surplus, g3m = res
                if D2 < N:
                    b1_fail.append((g6, D2))
                if g3m < 0:
                    g3_fail.append((g6, D2, coll, g3m))
                if D2 - N < minD2n:
                    minD2n = D2 - N
        for line in proc.stdout:
            s = line.strip()
            if s:
                batch.append(s)
            if len(batch) >= 200000:
                flush(batch); batch = []
        if batch:
            flush(batch)
    proc.wait()
    return dict(m=m_edges, total=total, three_conn_diam4=kept,
                B1_failures=b1_fail[:5], n_B1_fail=len(b1_fail),
                G3_failures=g3_fail[:8], n_G3_fail=len(g3_fail),
                min_D2_minus_n=(None if minD2n == 10**9 else minD2n),
                sec=round(time.time() - t0, 1))


if __name__ == "__main__":
    import json
    for m_edges in (int(x) for x in sys.argv[1:]):
        print(json.dumps(run_band(m_edges)), flush=True)
