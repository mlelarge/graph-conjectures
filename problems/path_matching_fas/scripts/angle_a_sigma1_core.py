"""ANGLE A: sigma_1 core-order shapes of the 6 iso-11 EQ_2 gadgets at n=8.

Enumerates reps(8), finds every (T,P,Q) that is an EQ_2 gadget
(R_arc = {(0,0),(1,1)}) possessing an iso-11 LFO.  For each:
  - picks an iso-11 witness sigma_1 (s_P=s_Q=1, all four port endpoints
    back-degree EXACTLY 1, i.e. both port arcs isolated K_2's),
  - computes C(P) = {w : vP->w and w->uP}, C(Q) = {w : vQ->w and w->uQ}
    (3-cycle partners; the other port's endpoints are INCLUDED if they
    qualify),
  - confirms crossing geometry (v_P < v_Q < u_P < u_Q up to swapping P,Q),
  - prints the RELATIVE ORDER (role-labeled) of the core set
    {uP,vP,uQ,vQ} U C(P) U C(Q) in sigma_1,
  - prints the back-arc edges among the core set, and which vertices lie
    between which port endpoints.

Run from problems/path_matching_fas/:  uv run python scripts/angle_a_sigma1_core.py
"""
import sys
sys.path.insert(0, 'scripts')
from itertools import combinations
from fanout_barrier_checks import reps as _reps, disjoint as _disjoint
from two_aux_eq3_search import enum_lfos_deg


def arc(T, x, y):
    return (x, y) if T[x][y] else (y, x)


def cset(T, u, v):
    # C of the arc u->v : {w : v->w and w->u}
    n = len(T)
    return [w for w in range(n) if w not in (u, v) and T[v][w] and T[w][u]]


def back_arc_edges(T, order):
    pos = {v: i for i, v in enumerate(order)}
    edges = []
    n = len(T)
    for i in range(n):
        for j in range(n):
            if T[i][j] and pos[i] > pos[j]:
                edges.append((i, j))  # back-arc i->j (i later than j)
    return edges


def find_eq2_iso11_gadgets(n=8):
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    pts = [(p, q) for p, q in combinations(pairs, 2) if _disjoint((p, q))]
    EQ2 = frozenset({(0, 0), (1, 1)})
    out = []
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
            iso11_witnesses = []
            cap00 = False
            for pos, deg in lfos:
                sP = 1 if pos[uP] > pos[vP] else 0
                sQ = 1 if pos[uQ] > pos[vQ] else 0
                R.add((sP, sQ))
                if (sP, sQ) == (1, 1) and all(deg[x] == 1 for x in (uP, vP, uQ, vQ)):
                    iso11_witnesses.append(pos)
                if (sP, sQ) == (0, 0) and all(deg[x] <= 1 for x in (uP, vP, uQ, vQ)):
                    cap00 = True
            if frozenset(R) != EQ2 or not iso11_witnesses:
                continue
            out.append({
                "T": [row[:] for row in T],
                "P": P, "Q": Q,
                "uP": uP, "vP": vP, "uQ": uQ, "vQ": vQ,
                "iso11": iso11_witnesses,
                "cap00": cap00,
            })
    return out


def analyze(g):
    T = g["T"]
    uP, vP, uQ, vQ = g["uP"], g["vP"], g["uQ"], g["vQ"]
    CP = cset(T, uP, vP)
    CQ = cset(T, uQ, vQ)
    core = {uP, vP, uQ, vQ} | set(CP) | set(CQ)

    # role labels (C-vertices labelled cP* / cQ*; mark dual membership)
    role = {uP: 'uP', vP: 'vP', uQ: 'uQ', vQ: 'vQ'}
    # C-vertices that are NOT port endpoints get cP/cQ labels
    cp_only = [w for w in CP if w not in (uP, vP, uQ, vQ)]
    cq_only = [w for w in CQ if w not in (uP, vP, uQ, vQ)]

    results = []
    for pos in g["iso11"]:
        # positions in sigma_1
        order = sorted(core, key=lambda v: pos[v])
        # crossing check: is vQ in C(P) and uP in C(Q)?
        crossing = (vQ in CP) and (uP in CQ)
        # relative order with role labels
        def lbl(v):
            tags = []
            if v in role:
                tags.append(role[v])
            if v in CP and v not in (uP, vP):
                tags.append('cP')
            if v in CQ and v not in (uQ, vQ):
                tags.append('cQ')
            return "/".join(tags) if tags else f"?{v}"
        rel_order = [(v, lbl(v), pos[v]) for v in order]

        # back-arc edges among core
        be = back_arc_edges(T, sorted(range(len(T)), key=lambda v: pos[v]))
        be_core = [(i, j) for (i, j) in be if i in core and j in core]
        be_core_lbl = [(lbl(i), lbl(j)) for (i, j) in be_core]

        # between-ness: which core vertices lie strictly between port endpoints
        def between(x, y):
            lo, hi = sorted((pos[x], pos[y]))
            return [lbl(v) for v in core if lo < pos[v] < hi and v not in (x, y)]
        results.append({
            "crossing": crossing,
            "rel_order_roles": [r[1] for r in rel_order],
            "rel_order_full": rel_order,
            "back_arcs_core": be_core_lbl,
            "between_P": between(uP, vP),
            "between_Q": between(uQ, vQ),
            "between_vP_vQ": between(vP, vQ),
            "between_uP_uQ": between(uP, uQ),
        })
    return {
        "P": g["P"], "Q": g["Q"],
        "uP": uP, "vP": vP, "uQ": uQ, "vQ": vQ,
        "CP": CP, "CQ": CQ,
        "cp_only": cp_only, "cq_only": cq_only,
        "cap00": g["cap00"],
        "witnesses": results,
    }


def normalize_shape(rel_roles):
    """Canonical role-pattern string for uniformity comparison.

    Treats P<->Q swap as a symmetry: produce both the order and its
    P/Q-swapped version, return the lexicographically smaller tuple of
    role-strings (sorting cP/cQ tags consistently)."""
    def swapPQ(r):
        m = {'uP': 'uQ', 'vP': 'vQ', 'uQ': 'uP', 'vQ': 'vP', 'cP': 'cQ', 'cQ': 'cP'}
        parts = r.split('/')
        return "/".join(sorted(m.get(p, p) for p in parts))
    def canon_tags(r):
        return "/".join(sorted(r.split('/')))
    a = tuple(canon_tags(r) for r in rel_roles)
    b = tuple(swapPQ(r) for r in rel_roles)
    # also the reversed reading for the swap (P<->Q usually also reverses order)
    b_rev = tuple(reversed(b))
    return min(a, b, b_rev)


def main():
    gads = find_eq2_iso11_gadgets(8)
    print(f"# EQ_2 gadgets with an iso-11 LFO at n=8: {len(gads)}")
    shapes = set()
    for idx, g in enumerate(gads):
        A = analyze(g)
        print("=" * 70)
        print(f"GADGET {idx}: P={A['P']} Q={A['Q']}  "
              f"(uP={A['uP']},vP={A['vP']},uQ={A['uQ']},vQ={A['vQ']})")
        print(f"  C(P)={A['CP']}  C(Q)={A['CQ']}  "
              f"cp_only={A['cp_only']} cq_only={A['cq_only']}")
        print(f"  cap00 also realizable in same gadget? {A['cap00']}  "
              f"(expect False since cap_both=0)")
        # use first iso-11 witness for the headline shape
        w0 = A['witnesses'][0]
        print(f"  crossing geometry: {w0['crossing']}")
        print(f"  sigma_1 core order (roles): {w0['rel_order_roles']}")
        print(f"  sigma_1 core order (vtx,role,pos): {w0['rel_order_full']}")
        print(f"  back-arcs among core: {w0['back_arcs_core']}")
        print(f"  between uP..vP: {w0['between_P']}")
        print(f"  between uQ..vQ: {w0['between_Q']}")
        print(f"  between vP..vQ: {w0['between_vP_vQ']}")
        print(f"  between uP..uQ: {w0['between_uP_uQ']}")
        # gather all distinct shapes over all iso-11 witnesses of this gadget
        for w in A['witnesses']:
            shapes.add(normalize_shape(w['rel_order_roles']))
    print("=" * 70)
    print(f"\nDISTINCT canonical sigma_1 core-order shapes across all witnesses: "
          f"{len(shapes)}")
    for s in sorted(shapes):
        print("   ", s)
    print(f"\nUNIFORM: {len(shapes) == 1}")


if __name__ == "__main__":
    main()
