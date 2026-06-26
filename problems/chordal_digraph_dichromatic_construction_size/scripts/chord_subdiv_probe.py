"""Ground the 'chord-subdivided 3-triangle' proposal against the oracle.

Base: 3 vertex-disjoint directed triangles T0={0,1,2}, T1={3,4,5}, T2={6,7,8}.
Coupling: for an ordered cross pair (u,w), insert a fresh chord vertex c and add
(u,c),(c,w),(w,u) -> directed 3-cycle u->c->w->u.

Sweep t=3 (n=12) and t=4 (n=13) couplings. Cheap C_3 filter first; exact chi only
on C_3 members. Track running max chi and report any chi>=3 hit immediately.
"""
from __future__ import annotations

import itertools
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import core    # noqa: E402

BASE_ARCS = [(0, 1), (1, 2), (2, 0),
             (3, 4), (4, 5), (5, 3),
             (6, 7), (7, 8), (8, 6)]
TRIANGLES = [(0, 1, 2), (3, 4, 5), (6, 7, 8)]


def cross_pairs():
    vb = [list(t) for t in TRIANGLES]
    pairs = []
    for i in range(3):
        for j in range(3):
            if i == j:
                continue
            for u in vb[i]:
                for w in vb[j]:
                    pairs.append((u, w))
    return pairs


def build_candidate(couplings):
    arcs = list(BASE_ARCS)
    c = 9
    for (u, w) in couplings:
        arcs += [(u, c), (c, w), (w, u)]
        c += 1
    return c, arcs


def run_t(t, pairs, max_chi_so_far):
    combos = itertools.combinations(range(len(pairs)), t)
    n_combos = 0
    n_c3 = 0
    max_chi = max_chi_so_far
    chi_dist = {}
    hits = []
    for combo in combos:
        n_combos += 1
        couplings = [pairs[i] for i in combo]
        n, arcs = build_candidate(couplings)
        if not core.is_C3(n, arcs):
            continue
        n_c3 += 1
        cv = core.dichromatic_number(n, arcs, ub=3)
        chi_dist[cv] = chi_dist.get(cv, 0) + 1
        if cv > max_chi:
            max_chi = cv
        if cv >= 3:
            hits.append({"t": t, "n": n, "couplings": couplings, "chi_vec": cv})
            print("HIT chi>=3:", json.dumps(hits[-1]), flush=True)
        if n_combos % 5000 == 0:
            print(f"  t={t} progress: {n_combos} combos, c3={n_c3}, "
                  f"max_chi={max_chi}", flush=True)
    print(f"t={t} DONE: combos={n_combos} c3_members={n_c3} "
          f"max_chi={max_chi} chi_dist={chi_dist} hits={len(hits)}", flush=True)
    return max_chi, hits


def main():
    pairs = cross_pairs()
    print(f"cross pairs = {len(pairs)}", flush=True)
    overall_max = 0
    all_hits = []
    for t in (3, 4):
        overall_max, hits = run_t(t, pairs, overall_max)
        all_hits += hits
        if all_hits:
            break
    print(json.dumps({
        "overall_max_chi": overall_max,
        "n_hits_chi_ge_3": len(all_hits),
        "hits": all_hits[:10],
    }, indent=2), flush=True)


if __name__ == "__main__":
    main()
