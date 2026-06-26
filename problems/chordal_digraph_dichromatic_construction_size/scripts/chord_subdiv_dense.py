"""Best-chance variants of the chord-subdivided 3-triangle proposal, to give the
construction its strongest shot at chi>=3 within n<=13.

Variant A: max couplings via shared 'hub' chord vertices (reuse to keep n<=13).
Variant B: all 9 forward cross arcs between consecutive triangles each chorded
           (T0->T1->T2->T0 fully coupled), n grows but capped at 13.
Variant C: dense all-pairs coupling between two triangles only (6 vertices core),
           every cross arc chorded, then attach third triangle.
We push m_arcs / directed-3-cycle density as high as possible while staying C_3.
"""
from __future__ import annotations

import itertools
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import core   # noqa: E402

BASE_ARCS = [(0, 1), (1, 2), (2, 0),
             (3, 4), (4, 5), (5, 3),
             (6, 7), (7, 8), (8, 6)]
T = [(0, 1, 2), (3, 4, 5), (6, 7, 8)]


def report(name, n, arcs):
    r = core.c3_reason(n, arcs)
    out = {"name": name, "n": n, "m_arcs": len(arcs), **r}
    if r["is_C3"]:
        out["chi_vec"] = core.dichromatic_number(n, arcs, ub=3)
    print(json.dumps(out), flush=True)
    return out


def main():
    results = []

    # Variant A: hub chord vertices. Use as many couplings as possible sharing
    # chord vertices. Try every assignment of up to 4 hub vertices to a maximal
    # set of cross pairs, capped n<=13.
    # Simplest strong version: pick consecutive-triangle forward couplings
    # T0->T1, T1->T2, T2->T0 using ONE hub each -> but route many pairs through it.
    vb = [list(t) for t in T]

    # Variant B: fully chord every forward cross arc T_i -> T_{i+1} (i mod 3),
    # one fresh chord per arc. 3 triangles * (3x3=9 forward pairs)?? too many.
    # Keep n<=13 => at most 4 fresh chords. Choose 4 'spanning' couplings that
    # touch all 9 base vertices to maximize interaction.
    spanning_sets = [
        [(0, 3), (4, 6), (7, 1), (5, 8)],   # touches many
        [(0, 4), (3, 7), (6, 1), (2, 5)],
        [(1, 5), (4, 8), (7, 2), (0, 3)],
        [(0, 3), (3, 6), (6, 0), (1, 4)],   # cyclic + extra
        [(2, 3), (5, 6), (8, 0), (1, 4)],
    ]
    for idx, cs in enumerate(spanning_sets):
        arcs = list(BASE_ARCS)
        c = 9
        for (u, w) in cs:
            arcs += [(u, c), (c, w), (w, u)]
            c += 1
        results.append(report(f"varB_{idx}", c, arcs))

    # Variant C: dense coupling of just TWO triangles, every one of the 9 cross
    # arcs (one direction) chorded would need 9 chords (n=15). Cap: chord the 3
    # 'matching' cross arcs 0->3,1->4,2->5 (n=12), plus reverse triangle T2 idle.
    for matching in [
        [(0, 3), (1, 4), (2, 5)],
        [(0, 4), (1, 5), (2, 3)],
        [(0, 3), (1, 4), (2, 5), (3, 6)],   # n=13, extends to T2
    ]:
        arcs = list(BASE_ARCS)
        c = 9
        for (u, w) in matching:
            arcs += [(u, c), (c, w), (w, u)]
            c += 1
        results.append(report(f"varC_{len(matching)}", c, arcs))

    # Variant A (hub): one hub vertex 9 receiving from u-set, sending to w-set,
    # with back-arcs. This risks TT3/digon; let oracle filter.
    hub_specs = [
        # hub 9 between T0 and T1: in from 0,1,2 ; out to 3,4,5 ; back 3->0 etc.
        {"ins": [0], "outs": [3, 4, 5], "backs": [(3, 0), (4, 0), (5, 0)]},
        {"ins": [0, 1, 2], "outs": [3], "backs": [(3, 0), (3, 1), (3, 2)]},
    ]
    for idx, hs in enumerate(hub_specs):
        arcs = list(BASE_ARCS)
        for u in hs["ins"]:
            arcs.append((u, 9))
        for w in hs["outs"]:
            arcs.append((9, w))
        arcs += hs["backs"]
        results.append(report(f"varA_hub{idx}", 10, arcs))

    mx = max((r.get("chi_vec", 0) for r in results), default=0)
    print(json.dumps({"max_chi_dense": mx,
                      "any_chi_ge_3": any(r.get("chi_vec", 0) >= 3
                                          for r in results)}, indent=2),
          flush=True)


if __name__ == "__main__":
    main()
