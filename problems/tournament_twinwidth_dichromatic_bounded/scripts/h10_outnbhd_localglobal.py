"""H10 out-neighbourhood local-to-global probe.

For each of the 20 n=9 PRIME tww<=1, omegaVec=2, chiVec=3 witnesses, and each
vertex v, compute chiVec(N^+(v)) and omegaVec(N^+(v)) of the induced
out-neighbourhood subtournament.

Falsifiable prediction:
  CONFIRM: every witness has max_v chiVec(N^+(v)) == 2 (no out-nbhd reaches chiVec 3).
  KILL   : some witness has an out-nbhd with chiVec==3 AND omegaVec==2 (a <=8-vertex
           tww<=1 induced subtournament with chi=3, omega=2 -> relocates the minimal
           chi>omega prime core below n=9).
"""
import sys, json
sys.path.insert(0, 'scripts')
import core


def induced(arcs, verts):
    vs = list(verts)
    idx = {x: i for i, x in enumerate(vs)}
    sub = [(idx[a], idx[b]) for (a, b) in arcs if a in idx and b in idx]
    return len(vs), sub


def out_nbhd(n, arcs, v):
    aset = set(arcs)
    return [w for w in range(n) if (v, w) in aset]


def main():
    obj = json.load(open('data/h10_witnesses.json'))
    ws = [[tuple(a) for a in W] for W in obj['witnesses']]
    n = 9
    results = []
    kill = []
    for i, arcs in enumerate(ws):
        per_v = []
        for v in range(n):
            nb = out_nbhd(n, arcs, v)
            m, sub = induced(arcs, nb)
            if m == 0:
                cv, ov = 0, 0
            else:
                cv = core.chi_vec(m, sub)
                ov = core.omega_vec(m, sub)
            per_v.append((v, m, cv, ov))
            if cv == 3 and ov == 2:
                kill.append((i, v, m, sub))
        max_chi = max(p[2] for p in per_v)
        # also record any out-nbhd with chiVec==3 regardless of omega
        chi3 = [(p[0], p[1], p[3]) for p in per_v if p[2] == 3]
        results.append({'witness': i, 'max_outnbhd_chi': max_chi,
                        'per_v': per_v, 'chi3_outnbhds': chi3})
        print(f"witness {i:2d}: max_v chiVec(N+(v)) = {max_chi}  "
              f"chi3 out-nbhds: {chi3}")
    print("---SUMMARY---")
    allmax = [r['max_outnbhd_chi'] for r in results]
    print("max_outnbhd_chi over 20 witnesses:", allmax)
    print("all == 2 ?", all(x == 2 for x in allmax))
    print("KILL hits (out-nbhd chi=3 & omega=2):", len(kill))
    for (i, v, m, sub) in kill:
        cv = core.chi_vec(m, sub); ov = core.omega_vec(m, sub); tw = core.tww(m, sub)
        print(f"  KILL witness {i} vertex {v}: m={m} chi={cv} omega={ov} tww={tw}")
    json.dump({'results': results, 'kill': kill}, open('data/h10_outnbhd_localglobal.json', 'w'))


if __name__ == '__main__':
    main()
