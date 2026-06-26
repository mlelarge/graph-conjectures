"""Probe: iterated DIRECTED LINE-DIGRAPH construction as a chi-lifter in C_3.

Ground plan (literature-reduction proposal):
  seed = directed triangle G_2 = (3, [(0,1),(1,2),(2,0)])
  L(D): nodes = arcs of D; line-arc (u,v)->(v,w) for arcs (u,v),(v,w) of D.
  Two realizations of L:
    (a) PLAIN line digraph:        line-arc (a)->(b) is a single arc.
    (b) TRIANGLE-REALIZED variant: each line-arc (a)->(b) replaced by a fresh
        directed triangle a -> b -> z -> a through a new chord vertex z (to
        inject directed cycles so the result is not acyclic).
  Also the CYCLIC SHIFT variant over Z_m: vertices = ordered pairs (i,i+1 mod m),
  triangle-realized shift coupling.

Oracle-check every iterate: c3_reason flags + exact dichromatic_number.
"""
import sys
sys.path.insert(0, 'scripts')
import core


def report(name, n, arcs):
    arcs = list(dict.fromkeys(arcs))  # dedup, keep order
    r = core.c3_reason(n, arcs)
    chi = None
    if r["is_C3"]:
        chi = core.dichromatic_number(n, arcs)
    print(f"{name}: n={n} m={len(arcs)} is_C3={r['is_C3']} "
          f"has_TT3={r['has_TT3']} long_dicycle>=4={r['has_long_induced_dicycle_ge4']} "
          f"chi_vec={chi}")
    return r, chi


# ---------------------------------------------------------------- plain line
def line_digraph(n, arcs):
    """Plain directed line digraph. Returns (N, line_arcs, idx_map)."""
    idx = {a: i for i, a in enumerate(arcs)}
    out_arcs = {}  # v -> list of arcs (v,w)
    for (u, v) in arcs:
        out_arcs.setdefault(v, [])
    larcs = []
    for (u, v) in arcs:
        for (v2, w) in arcs:
            if v == v2:
                larcs.append((idx[(u, v)], idx[(v2, w)]))
    return len(arcs), larcs, idx


def line_digraph_triangle(n, arcs):
    """Triangle-realized line digraph: each line-arc a->b becomes a directed
    triangle a -> b -> z -> a through a fresh chord vertex z."""
    idx = {a: i for i, a in enumerate(arcs)}
    N = len(arcs)
    larcs = []
    for (u, v) in arcs:
        for (v2, w) in arcs:
            if v == v2:
                larcs.append((idx[(u, v)], idx[(v2, w)]))
    out = []
    nxt = N
    for (a, b) in larcs:
        z = nxt; nxt += 1
        out += [(a, b), (b, z), (z, a)]
    return nxt, out


# ---------------------------------------------------------------- cyclic shift
def cyclic_shift_triangle(m):
    """Vertices = ordered pairs (i,(i+1)%m) over Z_m; for the directed shift
    (i,j)->(j,k) with j=i+1,k=j+1, realize each as a directed triangle through
    a fresh chord vertex."""
    pairs = [(i, (i + 1) % m) for i in range(m)]
    idx = {p: i for i, p in enumerate(pairs)}
    N = len(pairs)
    larcs = []
    for (i, j) in pairs:
        for (j2, k) in pairs:
            if j == j2:
                larcs.append((idx[(i, j)], idx[(j2, k)]))
    out = []
    nxt = N
    for (a, b) in larcs:
        z = nxt; nxt += 1
        out += [(a, b), (b, z), (z, a)]
    return nxt, out


def cyclic_shift_plain(m):
    pairs = [(i, (i + 1) % m) for i in range(m)]
    idx = {p: i for i, p in enumerate(pairs)}
    out = []
    for (i, j) in pairs:
        for (j2, k) in pairs:
            if j == j2:
                out.append((idx[(i, j)], idx[(j2, k)]))
    return len(pairs), out


if __name__ == "__main__":
    print("=== seed ===")
    seed_n, seed_arcs = 3, [(0, 1), (1, 2), (2, 0)]
    report("seed G_2", seed_n, seed_arcs)

    print("\n=== plain line-digraph iterates L^j(seed) ===")
    D_n, D_arcs = seed_n, seed_arcs
    for j in range(1, 4):
        D_n, D_arcs, _ = line_digraph(D_n, D_arcs)
        if D_n > 40 or not D_arcs:
            report(f"L^{j} plain", D_n, D_arcs)
            print(f"   (stop: n={D_n} arcs={len(D_arcs)})")
            break
        report(f"L^{j} plain", D_n, D_arcs)

    print("\n=== triangle-realized line-digraph iterates ===")
    base_n, base_arcs = seed_n, seed_arcs
    for j in range(1, 4):
        tn, tarcs = line_digraph_triangle(base_n, base_arcs)
        report(f"L^{j} tri-realized (over base n={base_n})", tn, tarcs)
        # iterate plain line on the plain-line graph to grow base
        base_n, base_arcs, _ = line_digraph(base_n, base_arcs)
        if base_n > 12:
            print(f"   (base grew to n={base_n}; tri-realization would exceed 40)")
            break

    print("\n=== cyclic shift variants ===")
    for m in range(4, 9):
        pn, parcs = cyclic_shift_plain(m)
        report(f"cyclic shift plain m={m}", pn, parcs)
    print()
    for m in range(4, 9):
        tn, tarcs = cyclic_shift_triangle(m)
        if tn <= 40:
            report(f"cyclic shift TRI m={m}", tn, tarcs)
        else:
            print(f"cyclic shift TRI m={m}: n={tn} > 40, skip")
