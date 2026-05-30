"""ANGLE C: matched-pair alignment & candidate reorder for the Crossing
Splice Lemma (capacity-form Lemma C heart).

Re-extracts (n=8, back-arc framing):
  * the 6 iso-11 (= cap-11) EQ_2 gadgets, each with a sigma_1 witness
    (a (1,1) LFO with all four port endpoints at back-degree EXACTLY 1);
  * the signature-matched cap-00 EQ_2 gadgets (same port-local signature:
    quad-type (1,1,2,2), cross-arc vP->uQ, score order uP<vP<uQ<vQ), each
    with a sigma_0 witness (a (0,0) LFO with all four endpoints deg <= 1).

For each matched (iso-11, cap-00) pair it:
  * aligns the role-labeled CORE = {uP,vP,uQ,vQ} U C(P) U C(Q);
  * lays out the role positions in sigma_1 and sigma_0 restricted to core;
  * computes the SINGLE local reorder of one port pair (move uQ before vQ,
    or move uP after vP, ...) that, applied to sigma_1, flips exactly that
    port's s-bit; reports whether the SAME move is uniform across pairs.

Roles (canonical, from the score order uP<vP<uQ<vQ and crossing geometry
v_P < v_Q < u_P < u_Q in sigma_1):
  uP = head of P's arc (uP->vP), vP = tail;
  uQ = head of Q's arc (uQ->vQ), vQ = tail.
s_P = 1 iff pos[uP] > pos[vP] (P's arc is a back-arc).
"""
from __future__ import annotations

import os
import sys
from itertools import combinations
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fanout_barrier_checks import reps as _reps, disjoint as _disjoint  # noqa: E402
from two_aux_eq3_search import enum_lfos_deg  # noqa: E402

EQ2 = frozenset({(0, 0), (1, 1)})


def arc(T, x, y):
    return (x, y) if T[x][y] else (y, x)


def cset(T, u, v):
    """C of the arc u->v: {w : v->w and w->u} (3-cycle partners)."""
    return [w for w in range(len(T))
            if w not in (u, v) and T[v][w] and T[w][u]]


def extract_gadgets(n=8):
    """Return (iso11_list, cap00_matched_list).

    iso11 record: dict with T, P, Q, roles (uP,vP,uQ,vQ), CP, CQ,
      sigma1 (an iso-11 order: list of vertices), sigma1_pos, deg1.
    cap00 record (only those sharing the iso-11 port-local signature):
      same fields but with sigma0 (a cap-00 order) and deg0; plus the
      signature so we can match.
    """
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    pts = [(p, q) for p, q in combinations(pairs, 2) if _disjoint((p, q))]

    iso11 = []
    cap00 = []
    for T in _reps(n):
        lfos = enum_lfos_deg(T)
        if not lfos:
            continue
        for P, Q in pts:
            a, b = P
            c, d = Q
            uP, vP = arc(T, *P)
            uQ, vQ = arc(T, *Q)
            roles = {uP: 'uP', vP: 'vP', uQ: 'uQ', vQ: 'vQ'}
            R = set()
            cap00_pos = None
            cap00_deg = None
            iso11_pos = None
            iso11_deg = None
            for pos, deg in lfos:
                sP = 1 if pos[uP] > pos[vP] else 0
                sQ = 1 if pos[uQ] > pos[vQ] else 0
                R.add((sP, sQ))
                if (sP, sQ) == (0, 0) and all(deg[x] <= 1 for x in (a, b, c, d)):
                    if cap00_pos is None:
                        cap00_pos, cap00_deg = pos, deg
                if (sP, sQ) == (1, 1) and all(deg[x] == 1 for x in (a, b, c, d)):
                    if iso11_pos is None:
                        iso11_pos, iso11_deg = pos, deg
            if frozenset(R) != EQ2:
                continue
            CP, CQ = cset(T, uP, vP), cset(T, uQ, vQ)
            # port-local signature
            s = {r: sum(T[v]) for v, r in roles.items()}
            order = tuple(sorted(('uP', 'vP', 'uQ', 'vQ'), key=lambda r: s[r]))
            quad = tuple(sorted(sum(1 for y in (uP, vP, uQ, vQ)
                                    if y != x and T[x][y])
                                for x in (uP, vP, uQ, vQ)))
            vpuq = 'vP->uQ' if T[vP][uQ] else 'uQ->vP'
            sig = (order, quad, vpuq)
            rec_common = {
                "T": [row[:] for row in T], "P": P, "Q": Q,
                "uP": uP, "vP": vP, "uQ": uQ, "vQ": vQ,
                "CP": CP, "CQ": CQ, "sig": sig,
            }
            if iso11_pos is not None:  # cap-11 == iso-11
                rec = dict(rec_common)
                rec["sigma1_pos"] = list(iso11_pos)
                rec["deg1"] = list(iso11_deg)
                iso11.append(rec)
            elif cap00_pos is not None:
                rec = dict(rec_common)
                rec["sigma0_pos"] = list(cap00_pos)
                rec["deg0"] = list(cap00_deg)
                cap00.append(rec)
    return iso11, cap00


def role_layout(rec, pos_key):
    """Return list of (position, vertex, role-label) sorted by position,
    restricted to the core set {uP,vP,uQ,vQ} U C(P) U C(Q)."""
    pos = rec[pos_key]
    uP, vP, uQ, vQ = rec["uP"], rec["vP"], rec["uQ"], rec["vQ"]
    role = {uP: 'uP', vP: 'vP', uQ: 'uQ', vQ: 'vQ'}
    for w in rec["CP"]:
        role.setdefault(w, []) if False else None
    # label C-vertices by membership; a vertex can be in both
    def clabel(w):
        tags = []
        if w in rec["CP"]:
            tags.append('cP')
        if w in rec["CQ"]:
            tags.append('cQ')
        return "/".join(tags) if tags else None
    core = set([uP, vP, uQ, vQ]) | set(rec["CP"]) | set(rec["CQ"])
    items = []
    for w in core:
        lbl = role.get(w) or clabel(w)
        items.append((pos[w], w, lbl))
    items.sort()
    return [(lbl, w) for (_p, w, lbl) in items]


def candidate_reorder(rec):
    """In the iso-11 witness sigma_1, identify the single local move of one
    port pair that flips that port's s-bit while keeping the OTHER port's
    arc orientation.

    sigma_1 has s_P=s_Q=1, i.e. uP after vP and uQ after vQ (both port arcs
    are back-arcs). To flip P to s_P=0 we must move uP BEFORE vP (or vP
    after uP). We report the adjacent-transposition move on the port pair,
    its crossed core vertices, and which port arcs become forward.
    """
    pos = rec["sigma1_pos"]
    uP, vP, uQ, vQ = rec["uP"], rec["vP"], rec["uQ"], rec["vQ"]
    n = len(rec["T"])
    order = [0] * n
    for v in range(n):
        order[pos[v]] = v

    def core_between(x, y):
        lo, hi = sorted((pos[x], pos[y]))
        out = []
        for k in range(lo + 1, hi):
            w = order[k]
            tag = []
            if w in rec["CP"]:
                tag.append('cP')
            if w in rec["CQ"]:
                tag.append('cQ')
            if w in (uP, vP, uQ, vQ):
                tag = [{uP: 'uP', vP: 'vP', uQ: 'uQ', vQ: 'vQ'}[w]]
            out.append("/".join(tag) if tag else "free")
        return out

    # Flip P: move uP leftward past vP (uP is after vP in sigma_1).
    flipP = {
        "move": "uP leftward past vP (turn P forward, s_P:1->0)",
        "uP_after_vP": pos[uP] > pos[vP],
        "gap": abs(pos[uP] - pos[vP]) - 1,
        "between_uP_vP_roles": core_between(uP, vP),
    }
    flipQ = {
        "move": "uQ leftward past vQ (turn Q forward, s_Q:1->0)",
        "uQ_after_vQ": pos[uQ] > pos[vQ],
        "gap": abs(pos[uQ] - pos[vQ]) - 1,
        "between_uQ_vQ_roles": core_between(uQ, vQ),
    }
    return {"flipP": flipP, "flipQ": flipQ}


def sigma1_role_word(rec):
    """The role-labeled left-to-right word of sigma_1 over the core."""
    return [lbl for (lbl, _w) in role_layout(rec, "sigma1_pos")]


def sigma0_role_word(rec):
    return [lbl for (lbl, _w) in role_layout(rec, "sigma0_pos")]


def main():
    iso11, cap00 = extract_gadgets(8)
    print(f"iso-11 (cap-11) EQ_2 gadgets at n=8: {len(iso11)}")
    print(f"cap-00 EQ_2 gadgets at n=8 (total): {len(cap00)}")

    # signature match: cap00 sharing the iso-11 full signature
    iso_sigs = Counter(r["sig"] for r in iso11)
    print("\niso-11 signatures:")
    for s, c in iso_sigs.items():
        print(f"  {s}: {c}")

    matched_cap00 = [r for r in cap00 if r["sig"] in set(iso_sigs)]
    quad_match = [r for r in cap00 if r["sig"][1] == (1, 1, 2, 2)]
    print(f"\ncap-00 sharing FULL iso-11 signature: {len(matched_cap00)}")
    print(f"cap-00 sharing quad-type (1,1,2,2): {len(quad_match)}")

    print("\n=== iso-11 sigma_1 role words (core, L->R) ===")
    words1 = Counter()
    reorders = []
    for r in iso11:
        w = tuple(sigma1_role_word(r))
        words1[w] += 1
        cr = candidate_reorder(r)
        reorders.append(cr)
        print(f"  P={r['P']} Q={r['Q']} |CP|={len(r['CP'])} |CQ|={len(r['CQ'])}")
        print(f"    sigma1 core word: {w}")
        print(f"    flipP: uP_after_vP={cr['flipP']['uP_after_vP']} "
              f"gap={cr['flipP']['gap']} between={cr['flipP']['between_uP_vP_roles']}")
        print(f"    flipQ: uQ_after_vQ={cr['flipQ']['uQ_after_vQ']} "
              f"gap={cr['flipQ']['gap']} between={cr['flipQ']['between_uQ_vQ_roles']}")
    print(f"\n  distinct sigma_1 core words: {dict(words1)}")

    print("\n=== matched cap-00 sigma_0 role words (core, L->R) ===")
    words0 = Counter()
    for r in matched_cap00:
        w = tuple(sigma0_role_word(r))
        words0[w] += 1
    for w, c in words0.items():
        print(f"  {c}x  {w}")

    # uniformity of flip move
    flipP_between = Counter(tuple(cr["flipP"]["between_uP_vP_roles"]) for cr in reorders)
    flipQ_between = Counter(tuple(cr["flipQ"]["between_uQ_vQ_roles"]) for cr in reorders)
    print("\n=== flip-move uniformity across the 6 iso-11 gadgets ===")
    print(f"  flipP between-roles: {dict(flipP_between)}")
    print(f"  flipQ between-roles: {dict(flipQ_between)}")


if __name__ == "__main__":
    main()
