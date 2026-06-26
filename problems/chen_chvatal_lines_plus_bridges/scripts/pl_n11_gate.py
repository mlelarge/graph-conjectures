"""n=11 falsification gate for H5': scan pendant-free (-d2) diam>=4 graphs
and report ANY with pl<11 (= disproof seed). Time-boxed prefix probe."""
import subprocess, sys, itertools, time
sys.path.insert(0, "scripts")
import core

def diameter(n, edges):
    dist = core.all_pairs_distances(n, edges)
    d = 0
    for i in range(n):
        row = dist[i]
        for j in range(n):
            if row[j] is None:
                return None, dist
            if row[j] > d:
                d = row[j]
    return d, dist

LIMIT_SEC = float(sys.argv[1]) if len(sys.argv) > 1 else 300.0
p = subprocess.Popen(["geng", "-c", "-d2", "11"], stdout=subprocess.PIPE, text=True)
t0 = time.time()
total = 0; diam4 = 0; min_pl = None; witnesses = []
for line in p.stdout:
    g6 = line.strip()
    if not g6:
        continue
    total += 1
    n, edges = core.graph6_to_edges(g6)
    dm, dist = diameter(n, edges)
    if dm is None or dm < 4:
        if time.time() - t0 > LIMIT_SEC:
            break
        continue
    diam4 += 1
    lines = set()
    for a, b in itertools.combinations(range(n), 2):
        lines.add(core.line_of_pair(dist, n, a, b))
    pl = sum(1 for L in lines if len(L) < n)
    if min_pl is None or pl < min_pl:
        min_pl = pl
    if pl < n:
        witnesses.append((g6, pl))
    if time.time() - t0 > LIMIT_SEC:
        break
p.kill()
print({"n": 11, "scanned_total": total, "scanned_diam4": diam4,
       "min_pl": min_pl, "n_pl_lt_11": len(witnesses),
       "witnesses": witnesses[:5], "elapsed_sec": round(time.time()-t0,1),
       "completed_full_sweep": False})
