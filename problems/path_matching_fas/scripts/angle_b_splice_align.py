"""ANGLE B (part 2): align sigma_0 (cap-00 witness) against sigma_1
(iso-11 crossing witness) on the role-labeled core, to mine the splice.

For each of the 170 cap-00 gadgets sharing the cap-11 signature, AND for
the 6 actual iso-11 EQ_2 gadgets, extract:
  * the 4-endpoint relative order (uP,vP,uQ,vQ) in the witness;
  * the core back-arc edge set (role-labeled);
  * |C(P)|, |C(Q)|.
The iso-11 crossing order (per the TARGET) is WLOG vP < vQ < uP < uQ.
We test: is the sigma_0 4-endpoint order CONSTANT across the cap-00
family, and how does it relate to the iso-11 order?  The splice shape =
the local reorder turning sigma_0's port placement into sigma_1's.
"""
from __future__ import annotations

import os
import sys
from collections import Counter
from itertools import combinations

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fanout_barrier_checks import reps as _reps, disjoint as _disjoint  # noqa: E402
from two_aux_eq3_search import enum_lfos_deg  # noqa: E402

EQ2 = frozenset({(0, 0), (1, 1)})


def arc(T, x, y):
    return (x, y) if T[x][y] else (y, x)


def cset(T, u, v):
    return [w for w in range(len(T))
            if w not in (u, v) and T[v][w] and T[w][u]]


def quad_type(T, verts):
    return tuple(sorted(sum(1 for y in verts if y != x and T[x][y])
                        for x in verts))


def endpoint_order(pos, uP, vP, uQ, vQ):
    roles = {uP: 'uP', vP: 'vP', uQ: 'uQ', vQ: 'vQ'}
    return tuple(roles[v] for v in sorted([uP, vP, uQ, vQ], key=lambda x: pos[x]))


def geometry(pos, a, b, c, d):
    loP, hiP = sorted((pos[a], pos[b]))
    loQ, hiQ = sorted((pos[c], pos[d]))
    if hiP < loQ or hiQ < loP:
        return 'disjoint'
    if (loP < loQ and hiQ < hiP) or (loQ < loP and hiP < hiQ):
        return 'nested'
    return 'crossing'


def run(n=8):
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    pts = [(p, q) for p, q in combinations(pairs, 2) if _disjoint((p, q))]

    cap00_endpoint_orders = Counter()
    cap00_geom = Counter()
    iso11_endpoint_orders = Counter()
    iso11_geom = Counter()
    iso11_examples = []
    # joint: for the SAME gadget when it is iso-11, record both its iso-11
    # order and (if it had cap-00) — but cap_both=0 so never both.

    for T in _reps(n):
        lfos = enum_lfos_deg(T)
        if not lfos:
            continue
        for P, Q in pts:
            a, b = P
            c, d = Q
            uP, vP = arc(T, *P)
            uQ, vQ = arc(T, *Q)
            R = set()
            cap00_pos = None
            iso11_pos = None
            for pos, deg in lfos:
                sP = 1 if pos[uP] > pos[vP] else 0
                sQ = 1 if pos[uQ] > pos[vQ] else 0
                R.add((sP, sQ))
                if (sP, sQ) == (0, 0) and all(deg[v] <= 1 for v in (a, b, c, d)) \
                        and cap00_pos is None:
                    cap00_pos = pos
                if (sP, sQ) == (1, 1) and all(deg[v] == 1 for v in (a, b, c, d)) \
                        and iso11_pos is None:
                    iso11_pos = pos
            if frozenset(R) != EQ2:
                continue
            quad = quad_type(T, (uP, vP, uQ, vQ))
            cross = bool(T[vP][uQ])
            sig = (quad == (1, 1, 2, 2) and cross)

            if iso11_pos is not None:
                # this is an iso-11 (=cap-11) EQ_2 gadget
                eo = endpoint_order(iso11_pos, uP, vP, uQ, vQ)
                ge = geometry(iso11_pos, a, b, c, d)
                iso11_endpoint_orders[eo] += 1
                iso11_geom[ge] += 1
                if len(iso11_examples) < 10:
                    iso11_examples.append({
                        "T": [r[:] for r in T], "P": P, "Q": Q,
                        "uP": uP, "vP": vP, "uQ": uQ, "vQ": vQ,
                        "iso11_order": sorted(range(n),
                                              key=lambda x: iso11_pos[x]),
                        "endpoint_order": eo, "geometry": ge,
                        "CP": cset(T, uP, vP), "CQ": cset(T, uQ, vQ),
                    })
            if sig and cap00_pos is not None and iso11_pos is None:
                eo = endpoint_order(cap00_pos, uP, vP, uQ, vQ)
                ge = geometry(cap00_pos, a, b, c, d)
                cap00_endpoint_orders[eo] += 1
                cap00_geom[ge] += 1

    return {
        "n": n,
        "cap00_4endpoint_order_dist":
            {str(k): v for k, v in cap00_endpoint_orders.most_common()},
        "cap00_geometry_dist": dict(cap00_geom),
        "iso11_4endpoint_order_dist":
            {str(k): v for k, v in iso11_endpoint_orders.most_common()},
        "iso11_geometry_dist": dict(iso11_geom),
        "iso11_examples": iso11_examples,
    }


if __name__ == "__main__":
    import json
    print(json.dumps(run(8), indent=2, default=list))
