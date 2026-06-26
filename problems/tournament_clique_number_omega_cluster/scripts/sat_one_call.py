"""Single SAT no-K-clique call as a SUBPROCESS (so the parent can hard-kill it
via OS `timeout` even though Cadical releases the GIL).

Usage: sat_one_call.py <kind> <args-json>
  kind = 'mixed'  args = {"outer":[nT,arcsT], "blocks":[[nb,ab],...], "K":k}
  kind = 'lex'    args = {"nT":..,"arcsT":..,"nH":..,"arcsH":..,"K":k}
Prints JSON {"ge":bool,"t":sec,"ncl":n} to stdout.
"""
import sys, os, json, time
sys.path.insert(0, os.path.dirname(__file__))
import core
from search_4critical_circulant import omega_vec_ge_K_via_sat


def mixed_sub(nT, arcsT, blocks):
    bT = core.beats_matrix(nT, arcsT)
    bH = [core.beats_matrix(nb, ab) for (nb, ab) in blocks]
    offset = []
    o = 0
    for (nb, _) in blocks:
        offset.append(o)
        o += nb
    arcs = []
    for a in range(nT):
        na = blocks[a][0]
        for b in range(na):
            for ap in range(nT):
                nap = blocks[ap][0]
                for bp in range(nap):
                    if a == ap and b == bp:
                        continue
                    if bT[a][ap] or (a == ap and bH[a][b][bp]):
                        arcs.append((offset[a] + b, offset[ap] + bp))
    return o, arcs


def main():
    payload = json.loads(sys.argv[1])
    K = payload["K"]
    nT, arcsT = payload["outer"]
    arcsT = [tuple(e) for e in arcsT]
    blocks = [(nb, [tuple(e) for e in ab]) for (nb, ab) in payload["blocks"]]
    n, arcs = mixed_sub(nT, arcsT, blocks)
    ge, dt, ncl = omega_vec_ge_K_via_sat(n, arcs, K)
    print(json.dumps({"order": n, "K": K, "ge": ge, "t": round(dt, 2), "ncl": ncl}))


if __name__ == "__main__":
    main()
