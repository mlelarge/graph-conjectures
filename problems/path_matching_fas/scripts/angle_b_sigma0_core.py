"""ANGLE B: sigma_0 core-order shapes of cap-00 EQ_2 gadgets sharing the
cap-11 (= iso-11) port-local signature.

Goal (Crossing Splice Lemma mining).  Among all EQ_2 gadgets (R_arc =
{(0,0),(1,1)}, back-arc framing) at n=8, the cap-11 (= iso-11) family of
6 gadgets shares a port-local signature (D86):

    port-quad score-seq (1,1,2,2)  AND  cross-arc vP -> uQ.

About 170 cap-00 gadgets share that SAME signature.  This probe takes
those cap-00 gadgets, picks a cap-00 witness sigma_0 (an LFO with both
ports forward and all four port endpoints at back-degree <= 1), and
prints the role-labeled RELATIVE ORDER of the core set

    core = {uP, vP, uQ, vQ} U C(P) U C(Q)

in sigma_0, plus the back-arc edges among the core, and where each
C-vertex sits relative to v_P / v_Q (the D87 lever says <= 1 C(P)-vertex
on each side of v_P, similarly for Q).

We then test whether the sigma_0 core-order SHAPE is UNIFORM (a single
role pattern up to the symmetric P<->Q swap), to decide if the splice
shape is provable or whether to recommend the n=9 hunt.

Role labels:
  uP, vP  = endpoints of P's tournament arc (uP -> vP, uP beats vP)
  uQ, vQ  = endpoints of Q's tournament arc (uQ -> vQ)
  cP_i    = the i-th C(P) vertex (3-cycle partner of P, between uP,vP in
            an isolated order)
  cQ_i    = the i-th C(Q) vertex
A C-vertex that is in BOTH C(P) and C(Q) is labelled cPQ_i.
"""
from __future__ import annotations

import os
import sys
from collections import Counter, defaultdict
from itertools import combinations

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fanout_barrier_checks import reps as _reps, disjoint as _disjoint  # noqa: E402
from two_aux_eq3_search import enum_lfos_deg  # noqa: E402

EQ2 = frozenset({(0, 0), (1, 1)})


def arc(T, x, y):
    return (x, y) if T[x][y] else (y, x)


def cset(T, u, v):
    """C of the arc u->v : 3-cycle partners w with v->w and w->u."""
    return [w for w in range(len(T))
            if w not in (u, v) and T[v][w] and T[w][u]]


def quad_type(T, uP, vP, uQ, vQ):
    verts = (uP, vP, uQ, vQ)
    return tuple(sorted(sum(1 for y in verts if y != x and T[x][y])
                        for x in verts))


def core_order_string(pos, roles, core):
    """Role-labeled left-to-right order of the core vertices in sigma_0."""
    ordered = sorted(core, key=lambda v: pos[v])
    return " < ".join(roles[v] for v in ordered)


def back_arcs_among(T, pos, core):
    """Back-arcs (u->v with pos[u]>pos[v]) with BOTH endpoints in core."""
    edges = []
    cs = set(core)
    for u in cs:
        for v in cs:
            if u != v and T[u][v] and pos[u] > pos[v]:
                edges.append((u, v))
    return edges


def find_cap00_witness(T, P, Q, lfos):
    """Pick a cap-00 witness sigma_0: an LFO with both ports forward
    (s_P=s_Q=0) and all four port endpoints at back-degree <= 1.
    Returns (pos, deg) or None."""
    a, b = P
    c, d = Q
    uP, vP = arc(T, *P)
    uQ, vQ = arc(T, *Q)
    for pos, deg in lfos:
        sP = 1 if pos[uP] > pos[vP] else 0
        sQ = 1 if pos[uQ] > pos[vQ] else 0
        if (sP, sQ) == (0, 0) and all(deg[v] <= 1 for v in (a, b, c, d)):
            return pos, deg
    return None


def analyze(n=8, max_print=200):
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    pts = [(p, q) for p, q in combinations(pairs, 2) if _disjoint((p, q))]

    matches = []          # cap-00 gadgets sharing the cap-11 signature
    shape_counter = Counter()
    side_lever_counter = Counter()  # (#C(P) left of vP, #C(P) right) etc.
    examples = []

    for Tn, T in enumerate(_reps(n)):
        lfos = enum_lfos_deg(T)
        if not lfos:
            continue
        for P, Q in pts:
            a, b = P
            c, d = Q
            uP, vP = arc(T, *P)
            uQ, vQ = arc(T, *Q)
            R = set()
            cap00 = False
            for pos, deg in lfos:
                sP = 1 if pos[uP] > pos[vP] else 0
                sQ = 1 if pos[uQ] > pos[vQ] else 0
                R.add((sP, sQ))
                if (sP, sQ) == (0, 0) and all(deg[v] <= 1 for v in (a, b, c, d)):
                    cap00 = True
            if frozenset(R) != EQ2 or not cap00:
                continue
            # port-local signature filter: quad (1,1,2,2) AND vP->uQ
            quad = quad_type(T, uP, vP, uQ, vQ)
            cross_vp_uq = bool(T[vP][uQ])
            if quad != (1, 1, 2, 2) or not cross_vp_uq:
                continue
            # this cap-00 gadget shares the cap-11 signature
            matches.append((T, P, Q))

            wit = find_cap00_witness(T, P, Q, lfos)
            if wit is None:
                continue
            pos, deg = wit

            CP = cset(T, uP, vP)
            CQ = cset(T, uQ, vQ)
            # role labels (handle C(P) cap C(Q))
            roles = {uP: 'uP', vP: 'vP', uQ: 'uQ', vQ: 'vQ'}
            both = set(CP) & set(CQ)
            cp_only = [w for w in CP if w not in both]
            cq_only = [w for w in CQ if w not in both]
            # order C-vertices by position for stable labelling
            for i, w in enumerate(sorted(both, key=lambda v: pos[v])):
                roles[w] = f'cPQ{i}'
            for i, w in enumerate(sorted(cp_only, key=lambda v: pos[v])):
                roles[w] = f'cP{i}'
            for i, w in enumerate(sorted(cq_only, key=lambda v: pos[v])):
                roles[w] = f'cQ{i}'

            core = set([uP, vP, uQ, vQ]) | set(CP) | set(CQ)
            shape = core_order_string(pos, roles, core)
            shape_counter[shape] += 1

            # lever sides: count C(P) vertices left / right of vP
            cp_left = sum(1 for w in CP if pos[w] < pos[vP])
            cp_right = sum(1 for w in CP if pos[w] > pos[vP])
            cq_left = sum(1 for w in CQ if pos[w] < pos[vQ])
            cq_right = sum(1 for w in CQ if pos[w] > pos[vQ])
            side_lever_counter[
                (cp_left, cp_right, cq_left, cq_right)] += 1

            if len(examples) < max_print:
                examples.append({
                    "T": [row[:] for row in T],
                    "P": P, "Q": Q,
                    "uP": uP, "vP": vP, "uQ": uQ, "vQ": vQ,
                    "CP": CP, "CQ": CQ,
                    "sigma0_order": [v for v in sorted(range(n),
                                                       key=lambda x: pos[x])],
                    "core_shape": shape,
                    "core_backarcs": [(roles[u], roles[v])
                                      for (u, v) in back_arcs_among(
                                          T, pos, core)],
                    "lever_sides": {
                        "CP_left_of_vP": cp_left, "CP_right_of_vP": cp_right,
                        "CQ_left_of_vQ": cq_left, "CQ_right_of_vQ": cq_right},
                })

    # canonicalize shapes under the P<->Q role swap to detect uniformity
    def swap_pq(shape):
        # swap uP<->uQ, vP<->vQ, cP<->cQ tokens
        toks = shape.split(" < ")
        out = []
        for t in toks:
            if t.startswith('uP'):
                out.append('uQ')
            elif t.startswith('uQ'):
                out.append('uP')
            elif t.startswith('vP'):
                out.append('vQ')
            elif t.startswith('vQ'):
                out.append('vP')
            elif t.startswith('cPQ'):
                out.append(t)  # symmetric
            elif t.startswith('cP'):
                out.append('cQ' + t[2:])
            elif t.startswith('cQ'):
                out.append('cP' + t[2:])
            else:
                out.append(t)
        return " < ".join(out)

    canon = Counter()
    for shape, cnt in shape_counter.items():
        s2 = swap_pq(shape)
        key = min(shape, s2)
        canon[key] += cnt

    return {
        "n": n,
        "num_cap00_sharing_cap11_signature": len(matches),
        "distinct_core_shapes": len(shape_counter),
        "core_shape_distribution": dict(shape_counter.most_common()),
        "core_shape_canonical_under_PQ_swap":
            dict(canon.most_common()),
        "uniform_up_to_PQ_swap": len(canon) == 1,
        "lever_side_distribution": {str(k): v for k, v
                                    in side_lever_counter.most_common()},
        "examples": examples,
    }


if __name__ == "__main__":
    import json
    out = analyze(8, max_print=200)
    # print summary without the huge examples list first
    summary = {k: v for k, v in out.items() if k != "examples"}
    print(json.dumps(summary, indent=2, default=list))
    print("\n=== FIRST 25 EXAMPLES (role-labeled) ===")
    for ex in out["examples"][:25]:
        print(json.dumps(ex, default=list))
