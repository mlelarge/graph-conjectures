"""Subtournament-census certificate ladder for a vertex-transitive circulant.

m(s) = does some induced s-vertex subtournament containing vertex 0 have
omega_vec>=3 (i.e. NOT omega_vec_le2).  By vertex-transitivity restricting to
subsets that contain vertex 0 is sound and covers all subsets up to rotation.

The smallest s with m(s)=True is exactly min_subtournament_order_for_k(T,3) =
the ell(3) certificate floor for this object.
"""
import os
import sys
import time
import json
import itertools

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from circulant_scan_n17 import circulant_arcs, beats_from_arcs
from iso_critical_scan_n9 import omega_vec_le2


def sub_beats(beats, subset):
    """Build a beats matrix on labels 0..len(subset)-1 for the induced subtournament."""
    s = len(subset)
    idx = {v: i for i, v in enumerate(subset)}
    sb = [[False] * s for _ in range(s)]
    for v in subset:
        iv = idx[v]
        bv = beats[v]
        for u in subset:
            if bv[u]:
                sb[iv][idx[u]] = True
    return sb


def census_ladder(p, g, s_lo=7, s_hi=None, time_budget=None):
    if s_hi is None:
        s_hi = p
    arcs = circulant_arcs(p, g)
    beats = beats_from_arcs(p, arcs)
    others = [v for v in range(p) if v != 0]
    results = {}
    smallest_s = None
    t0 = time.time()
    for s in range(s_lo, s_hi + 1):
        found = False
        witness = None
        ncalls = 0
        ts = time.time()
        # subsets of size s containing 0: choose s-1 from the others, prepend 0
        for combo in itertools.combinations(others, s - 1):
            subset = (0,) + combo
            sb = sub_beats(beats, subset)
            ncalls += 1
            if not omega_vec_le2(s, sb):
                found = True
                witness = subset
                break
        dt = time.time() - ts
        results[s] = {"m": found, "ncalls": ncalls, "time_s": round(dt, 3),
                      "witness": list(witness) if witness else None}
        print(f"s={s:2d}  m={found}  calls={ncalls}  time={dt:.2f}s  witness={witness}", flush=True)
        if found:
            smallest_s = s
            break
        if time_budget and (time.time() - t0) > time_budget:
            print(f"TIME BUDGET EXCEEDED at s={s}", flush=True)
            break
    return smallest_s, results


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "p19"
    if which == "ac17":
        p, g = 17, tuple([1, 2, 3, 4, 5, 6, 7, 9])
    elif which == "p19":
        p, g = 19, tuple(range(1, 9)) + (10,)
    else:
        raise SystemExit("unknown target")
    print(f"=== census ladder p={p} g={g} ===", flush=True)
    smallest_s, results = census_ladder(p, g)
    out = {"p": p, "g": list(g), "smallest_s": smallest_s, "results": results}
    outpath = fos.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'subtournament_census_{which}.json')
    with open(outpath, "w") as f:
        json.dump(out, f, indent=2)
    print(f"SMALLEST_S={smallest_s}  saved {outpath}", flush=True)
