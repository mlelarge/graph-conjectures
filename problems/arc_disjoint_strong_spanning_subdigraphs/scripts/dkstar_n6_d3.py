"""Cap-limited generic n=6 -d3 slice for DK*: lambda>=3 regime (the SAD-relevant
part). Self-capping; prints summary at end only."""
import sys, subprocess, time, json
sys.path.insert(0, 'scripts')
import oracle
from collections import defaultdict

t0 = time.time()
ALPHAS = (1.0, 4 / 3, 5 / 3, 2.0)
CAP_S = float(sys.argv[1]) if len(sys.argv) > 1 else 500.0


def census(n, arcs):
    lam = oracle.arc_connectivity(n, arcs)
    if lam < 1:
        return lam, None
    larcs = [(i, u, v) for i, (u, v) in enumerate(arcs)]
    by = defaultdict(set)
    for mask in range(1, (1 << n) - 1):
        X = frozenset(i for i in range(n) if (mask >> i) & 1)
        F = frozenset(i for (i, u, v) in larcs if u in X and v not in X)
        by[len(F)].add(F)
    res = {}
    for a in ALPHAS:
        thr = a * lam
        c = sum(len(s) for sz, s in by.items() if sz <= thr)
        res[a] = (c, n ** (2 * a))
    return lam, res


geng = subprocess.Popen(['geng', '-cd3q', '6'], stdout=subprocess.PIPE)
directg = subprocess.Popen(['directg', '-Tq'], stdin=geng.stdout,
                           stdout=subprocess.PIPE)
geng.stdout.close()
worst = {a: (-1.0, None) for a in ALPHAS}
nread = nlam = lam3 = 0
kills = []
capped = False
for line in directg.stdout:
    if time.time() - t0 > CAP_S:
        capped = True
        break
    line = line.decode().strip()
    if not line:
        continue
    toks = line.split()
    nv = int(toks[0]); nums = list(map(int, toks[2:]))
    arcs = [(nums[i], nums[i + 1]) for i in range(0, len(nums), 2)]
    nread += 1
    lam, res = census(nv, arcs)
    if res is None:
        continue
    nlam += 1
    if lam >= 3:
        lam3 += 1
    for a, (cnt, den) in res.items():
        r = cnt / den
        if r > worst[a][0]:
            worst[a] = (round(r, 4), (nv, lam, cnt, int(den)))
        if r > 1.0:
            kills.append({"alpha": a, "ratio": round(r, 4), "n": nv,
                          "lambda": lam, "arcs": arcs})
try:
    directg.kill(); geng.kill()
except Exception:
    pass
print(json.dumps({
    "slice": "geng -cd3 6 | directg -T", "capped": capped,
    "elapsed_s": round(time.time() - t0, 1),
    "n_read": nread, "n_lam_ge1": nlam, "n_lam_ge3": lam3,
    "worst_per_alpha": {str(round(a, 3)): worst[a] for a in ALPHAS},
    "n_kills": len(kills), "kills": kills[:3],
    "DKstar_survives": len(kills) == 0}, indent=2))
