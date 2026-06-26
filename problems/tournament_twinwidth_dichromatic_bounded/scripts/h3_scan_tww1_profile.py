"""H3 generic disprove scan (frontier n).

Enumerate ALL tournaments on n vertices (gentourng, one per iso class), keep
those with tww<=1, and tabulate the full (tww, omegaVec, chiVec) distribution.
The disprove avenue (Conj 3.12 contrapositive): find a tww<=1 tournament with
SMALL omegaVec but LARGE chiVec. This script reports max chiVec achievable at
each omegaVec value within the tww<=1 class -- an empirical binding function.

Usage:
  .venv/bin/python scripts/h3_scan_tww1_profile.py <n> [--tww-max K]
"""
from __future__ import annotations
import argparse, json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import core
import oracle
from collections import Counter


def run(n, tww_max=1):
    prof = Counter()
    maxchi_by_omega = {}
    found_chi_ge3 = []
    scanned = 0
    for (_n, arcs) in oracle._all_tournaments(n):
        scanned += 1
        w = core.tww(n, arcs, ub=tww_max + 1)
        if w > tww_max:
            continue
        om = core.omega_vec(n, arcs)
        ch = core.chi_vec(n, arcs)
        prof[(w, om, ch)] += 1
        maxchi_by_omega[om] = max(maxchi_by_omega.get(om, 0), ch)
        if ch >= 3:
            found_chi_ge3.append({"tww": w, "omega_vec": om, "chi_vec": ch,
                                  "arcs": list(arcs)})
    return {
        "n": n, "tww_max": tww_max, "n_scanned": scanned,
        "distribution": {f"{k[0]},{k[1]},{k[2]}": v for k, v in sorted(prof.items())},
        "max_chi_by_omega": maxchi_by_omega,
        "num_chi_ge3": len(found_chi_ge3),
        "found_chi_ge3": found_chi_ge3,
    }


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("n", type=int)
    ap.add_argument("--tww-max", type=int, default=1)
    a = ap.parse_args()
    print(json.dumps(run(a.n, a.tww_max), indent=2, default=str))
