"""Exhaustive sparse-band census of the H5 2-connected core.

For given n and an edge band [emin,emax], enumerate every 2-connected
(geng -C) graph, keep diam>=4, and compute ell, #proper-lines.

Reports per-edge-count the min ell-n and min proper-n (to see the U-shape),
global minima, and ALL witnesses with ell<n (H5 BREACH) or proper<n
(sharpening breach), plus the tightest near-misses.

Blocking, parallel (ProcessPoolExecutor). Not backgrounded.
"""
import sys, os, subprocess, itertools, time
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor

from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core


def analyze(g6):
    n, edges = core.graph6_to_edges(g6)
    dist = core.all_pairs_distances(n, edges)
    diam = 0
    for i in range(n):
        row = dist[i]
        for j in range(i + 1, n):
            d = row[j]
            if d is None:
                return None
            if d > diam:
                diam = d
    if diam < 4:
        return None
    lines = set()
    for a, b in itertools.combinations(range(n), 2):
        lines.add(core.line_of_pair(dist, n, a, b))
    ell = len(lines)
    proper = sum(1 for L in lines if len(L) < n)
    return (len(edges), ell, proper, n, g6)


def scan_band(n, emin, emax, chunk=20000):
    cmd = ["geng", "-C", "-q", str(n), f"{emin}:{emax}"]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, text=True, bufsize=1 << 20)
    per_edge_min_ell = defaultdict(lambda: 10**9)
    per_edge_min_proper = defaultdict(lambda: 10**9)
    per_edge_diam4 = defaultdict(int)
    global_min_ell_n = 10**9
    global_min_proper_n = 10**9
    argmin_ell = None      # (g6, ell, proper, m)
    breaches_ell = []      # ell < n
    breaches_proper = []   # proper < n
    near = []              # proper-n <= 1
    total = 0
    diam4 = 0
    t0 = time.time()

    workers = max(2, (os.cpu_count() or 4) - 2)
    with ProcessPoolExecutor(max_workers=workers) as ex:
        batch = []
        def flush(batch):
            nonlocal total, diam4, global_min_ell_n, global_min_proper_n, argmin_ell
            for res in ex.map(analyze, batch, chunksize=400):
                total += 1
                if res is None:
                    continue
                m, ell, proper, nn, g6 = res
                diam4 += 1
                per_edge_diam4[m] += 1
                if argmin_ell is None or ell - nn < argmin_ell[1] - nn:
                    argmin_ell = (g6, ell, proper, m)
                if ell < per_edge_min_ell[m]:
                    per_edge_min_ell[m] = ell
                if proper < per_edge_min_proper[m]:
                    per_edge_min_proper[m] = proper
                global_min_ell_n = min(global_min_ell_n, ell - nn)
                global_min_proper_n = min(global_min_proper_n, proper - nn)
                if ell < nn:
                    breaches_ell.append((g6, ell, proper, m))
                if proper < nn:
                    breaches_proper.append((g6, ell, proper, m))
                if proper - nn <= 1:
                    near.append((g6, ell, proper, m, proper - nn))
        for line in proc.stdout:
            g6 = line.strip()
            if not g6:
                continue
            batch.append(g6)
            if len(batch) >= chunk:
                # we want total to count even skipped; but skipped graphs are
                # cheap to recount via len; use map over the whole batch.
                flush(batch)
                batch = []
        if batch:
            flush(batch)
    returncode = proc.wait()
    if returncode != 0:
        raise subprocess.CalledProcessError(returncode, cmd)
    near.sort(key=lambda r: r[4])
    return dict(
        n=n, band=(emin, emax), total_2conn=total, diam4=diam4,
        global_min_ell_minus_n=(None if global_min_ell_n == 10**9 else global_min_ell_n),
        global_min_proper_minus_n=(None if global_min_proper_n == 10**9 else global_min_proper_n),
        argmin_ell=argmin_ell,
        n_breaches_ell_lt_n=len(breaches_ell),
        n_breaches_proper_lt_n=len(breaches_proper),
        breaches_ell=breaches_ell[:10],
        breaches_proper=breaches_proper[:10],
        per_edge_min_ell={k: per_edge_min_ell[k] for k in sorted(per_edge_min_ell)},
        per_edge_min_proper={k: per_edge_min_proper[k] for k in sorted(per_edge_min_proper)},
        per_edge_diam4={k: per_edge_diam4[k] for k in sorted(per_edge_diam4)},
        tightest_near=near[:15],
        elapsed_sec=round(time.time() - t0, 1),
    )


if __name__ == "__main__":
    import json
    n = int(sys.argv[1])
    emin = int(sys.argv[2])
    emax = int(sys.argv[3])
    print(json.dumps(scan_band(n, emin, emax), indent=2))
