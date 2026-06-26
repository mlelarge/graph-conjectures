"""CORRECTED red-team of proof_AC_n_AC_n_k5.md §3.3.

A backedge clique under the FIXED inner_then_outer order prec is a vertex set S
s.t. for all u prec v in S, v beats u (every prec-later beats every prec-earlier).
The order is NOT free; it is key(a,b)=(c(b),c(a),a,b) ascending.

We enumerate, for each subset of the 8 cells, whether there is one rep per cell
making a backedge clique under prec.  Max realizable cell-count and whether any 5
is realizable.
"""
import sys
from itertools import combinations


def ac_g(n):
    m = (n - 1) // 2
    return set(range(1, m)) | {m + 1}


def cval(t, m):
    if t == 0:
        return 3
    if 1 <= t <= m:
        return 2
    return 1


def beats(u, v, n, g):
    a, b = u; a2, b2 = v
    if a != a2:
        return (a2 - a) % n in g
    return (b2 - b) % n in g


def key(v, m):
    a, b = v
    return (cval(b, m), cval(a, m), a, b)


def cell(v, m):
    a, b = v
    return (cval(b, m), cval(a, m))


def is_backedge_clique(verts, n, g, m):
    """Under prec (key ascending): every prec-later beats every prec-earlier."""
    s = sorted(verts, key=lambda v: key(v, m))
    k = len(s)
    for i in range(k):
        for j in range(i + 1, k):
            # s[i] prec s[j]; need s[j] beats s[i]
            if not beats(s[j], s[i], n, g):
                return False
    return True


def realize(cellset, cells, n, g, m):
    cl = list(cellset)

    def bt(i, chosen):
        if i == len(cl):
            return list(chosen)
        for v in cells[cl[i]]:
            cand = chosen + [v]
            if is_backedge_clique(cand, n, g, m):
                r = bt(i + 1, cand)
                if r is not None:
                    return r
        return None

    return bt(0, [])


def analyze(n):
    m = (n - 1) // 2
    g = ac_g(n)
    cells = {}
    for a in range(n):
        for b in range(n):
            if (a, b) == (0, 0):
                continue
            cells.setdefault(cell((a, b), m), []).append((a, b))
    eight = sorted(cells.keys())
    assert len(eight) == 8

    def feasible(cs):
        return realize(cs, cells, n, g, m) is not None

    # max realizable cell-count
    best = 0; best_ex = None; best_v = None
    for s in range(8, 0, -1):
        f = None
        for cs in combinations(eight, s):
            r = realize(cs, cells, n, g, m)
            if r is not None:
                f = (cs, r); break
        if f:
            best, best_ex, best_v = s, f[0], f[1]; break

    # all 5-subsets
    realizable5 = [cs for cs in combinations(eight, 5) if feasible(cs)]
    # minimal infeasible sets of size <=4
    minimal_infeasible = []
    for s in (3, 4):
        for cs in combinations(eight, s):
            if not feasible(cs):
                # minimal: no proper subset infeasible
                if all(feasible(sub) for r in range(2, s) for sub in combinations(cs, r)):
                    minimal_infeasible.append(cs)
    # check cover: every 5-subset contains a minimal infeasible
    uncovered = []
    for five in combinations(eight, 5):
        if not any(set(mi) <= set(five) for mi in minimal_infeasible):
            uncovered.append(five)
    return dict(eight=eight, best=best, best_ex=best_ex, best_v=best_v,
                realizable5=realizable5, minimal_infeasible=minimal_infeasible,
                uncovered=uncovered)


def main():
    ns = [int(x) for x in sys.argv[1:]] or [7, 9, 11, 13, 15]
    for n in ns:
        r = analyze(n)
        print(f"n={n}: MAX realizable cell-count = {r['best']}  (proof claims 4)")
        print(f"   example cellset = {r['best_ex']}")
        print(f"   example verts   = {r['best_v']}")
        print(f"   # realizable 5-cellsets = {len(r['realizable5'])}  (proof claims 0)")
        if r['realizable5']:
            print(f"   REALIZABLE 5s: {r['realizable5'][:5]}{'...' if len(r['realizable5'])>5 else ''}")
        print(f"   # minimal infeasible sets (size 3 or 4) = {len(r['minimal_infeasible'])}  (proof says 20)")
        print(f"   minimal infeasible = {r['minimal_infeasible']}")
        print(f"   5-subsets NOT covered by any minimal infeasible = {len(r['uncovered'])}")
        if r['uncovered']:
            print(f"      uncovered: {r['uncovered']}")
        print()


if __name__ == "__main__":
    main()
