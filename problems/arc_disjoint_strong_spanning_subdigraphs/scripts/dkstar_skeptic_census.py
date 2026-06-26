"""SKEPTIC generic census for DK*(alpha): exhaustive generic n=6 (min underlying
degree 2 = the relevant lambda>=2 generic regime), time-capped, foreground.
One counterexample (ratio_arcset>1) kills the UNIVERSAL DK*."""
import sys, subprocess, time, json
sys.path.insert(0, 'scripts')
import oracle

t0 = time.time()
ALPHAS = (1.0, 4 / 3, 5 / 3, 2.0)


def census(n, arcs):
    lam = oracle.arc_connectivity(n, arcs)
    if lam < 1:
        return lam, None
    larcs = [(i, u, v) for i, (u, v) in enumerate(arcs)]
    res = {}
    for alpha in ALPHAS:
        thr = alpha * lam
        asets = set()
        for mask in range(1, (1 << n) - 1):
            X = frozenset(i for i in range(n) if (mask >> i) & 1)
            F = frozenset(i for (i, u, v) in larcs if u in X and v not in X)
            if len(F) <= thr:
                asets.add(F)
        res[alpha] = (len(asets), n ** (2 * alpha))
    return lam, res


def main(degflag, n, cap_s):
    geng = subprocess.Popen(['geng', degflag, str(n)], stdout=subprocess.PIPE)
    directg = subprocess.Popen(['directg', '-Tq'], stdin=geng.stdout,
                               stdout=subprocess.PIPE)
    geng.stdout.close()
    worst = {a: (-1.0, None) for a in ALPHAS}
    nread = nlam = lam3 = 0
    kills = []
    capped = False
    for line in directg.stdout:
        if time.time() - t0 > cap_s:
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
        "degflag": degflag, "n": n, "capped": capped,
        "elapsed_s": round(time.time() - t0, 1),
        "n_read": nread, "n_lam_ge1": nlam, "n_lam_ge3": lam3,
        "worst_per_alpha": {str(round(a, 3)): worst[a] for a in ALPHAS},
        "n_kills": len(kills), "kills": kills[:3],
        "DKstar_survives": len(kills) == 0}, indent=2))


if __name__ == '__main__':
    main(sys.argv[1], int(sys.argv[2]), float(sys.argv[3]))
