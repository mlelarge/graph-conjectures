"""Ground the blow-up / Turan-densification invariance proposal.

(a) blow-up monotonicity scan: every C_3 digraph D on n in {2..6}, blow_up_t(D)
    for t in {2,3,4}; count cases where is_C3(blowup) AND chi(blowup) > chi(D).
(b) cyclic-tripartite Turan orientation cyclic_partite([s,s,s]) and unbalanced
    [a,b,c] up to s=5 (n<=15): confirm is_C3 and chi_vec at each size.
(c) every C_3 digraph on n<=7: flag out-twin+in-twin pairs; tabulate chi_vec vs
    'twin-reduced'.
"""
from __future__ import annotations

import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import core


def blow_up(n, arcs, t):
    """Replace each vertex by an independent set of size t; each arc u->v by the
    complete bipartite arc-set P_u -> P_v.  No arcs inside a part (independent)."""
    new_arcs = []
    for (u, v) in arcs:
        for i in range(t):
            for j in range(t):
                new_arcs.append((u * t + i, v * t + j))
    return n * t, new_arcs


def part_a2_directed_triangle_blowups():
    """Load-bearing large-t case: blow up the directed 3-cycle (the unique chi=2
    C_3 gadget G_2) to high t and confirm chi stays 2 and it stays in C_3.
    (Directed-triangle blow-up == cyclic-tripartite Turan with equal parts.)"""
    print("=== (a2) directed-triangle (G_2) blow-up, large t ===", flush=True)
    base_n, base_arcs = 3, [(0, 1), (1, 2), (2, 0)]
    chi_base = core.dichromatic_number(base_n, base_arcs)
    viol = []
    for t in range(2, 7):
        bn, barcs = blow_up(base_n, base_arcs, t)
        isc3 = core.is_C3(bn, barcs)
        chi = core.dichromatic_number(bn, barcs, ub=chi_base + 1) if isc3 else None
        print(f"  t={t} bn={bn} is_C3={isc3} chi={chi} (chi_base={chi_base})",
              flush=True)
        if isc3 and chi is not None and chi > chi_base:
            viol.append({"t": t, "bn": bn, "chi": chi})
    return viol


def cyclic_partite(sizes):
    """Cyclic orientation of complete multipartite graph: parts P_0..P_{r-1};
    all arcs P_i -> P_{i+1 mod r}.  For r=3 this is the cyclic-tripartite Turan
    orientation."""
    r = len(sizes)
    offs = [0]
    for s in sizes:
        offs.append(offs[-1] + s)
    n = offs[-1]
    arcs = []
    for i in range(r):
        a0, a1 = offs[i], offs[i + 1]
        j = (i + 1) % r
        b0, b1 = offs[j], offs[j + 1]
        for a in range(a0, a1):
            for b in range(b0, b1):
                arcs.append((a, b))
    return n, arcs


def t_range_for_n(n):
    # keep blow-up ORDER bounded so the exact C_3 test (nx.simple_cycles) and
    # exact chi stay tractable across the FULL base enumeration.
    #   n<=4 -> {2,3,4} (blow-up order <=16)
    #   n=5  -> {2,3}   (order <=15; t=4->20 blows simple_cycles up on dense bases)
    #   n=6  -> {2}     (order 12)
    # The load-bearing large-t directed-triangle family is tested separately in
    # part (b)/(a2) up to s=6 (order 18).
    if n <= 4:
        return (2, 3, 4)
    if n == 5:
        return (2, 3)
    return (2,)


def part_a_blowup_scan(n_lo=2, n_hi=6):
    print("=== (a) blow-up monotonicity scan ===", flush=True)
    violations = []
    n_blowup_C3 = 0
    n_base_C3 = 0
    for n in range(n_lo, n_hi + 1):
        t0 = time.time()
        base_count = 0
        for (gn, edges) in core.all_simple_graphs(n):
            for arcs in core.all_orientations(edges):
                if not core.is_C3(n, arcs):
                    continue
                base_count += 1
                n_base_C3 += 1
                chi_base = None
                for t in t_range_for_n(n):
                    bn, barcs = blow_up(n, arcs, t)
                    if not core.is_C3(bn, barcs):
                        continue
                    n_blowup_C3 += 1
                    if chi_base is None:
                        chi_base = core.dichromatic_number(n, arcs)
                    # only need to detect chi_blow > chi_base: cap ub
                    chi_blow = core.dichromatic_number(bn, barcs, ub=chi_base + 1)
                    if chi_blow > chi_base:
                        violations.append({
                            "n": n, "t": t, "chi_base": chi_base,
                            "chi_blow": chi_blow, "arcs": list(arcs)})
        print(f"  n={n}: base C_3={base_count}  elapsed={time.time()-t0:.1f}s  "
              f"running violations={len(violations)}", flush=True)
    print(f"  TOTAL base C_3 (n={n_lo}..{n_hi})={n_base_C3}  blow-ups staying "
          f"in C_3={n_blowup_C3}  VIOLATIONS={len(violations)}", flush=True)
    return violations


def part_b_turan():
    print("=== (b) cyclic-tripartite Turan orientation ===", flush=True)
    rows = []
    bad = []
    # balanced [s,s,s] up to s=5  (n=3,6,9,12,15)
    for s in range(1, 6):
        n, arcs = cyclic_partite([s, s, s])
        isc3 = core.is_C3(n, arcs)
        chi = core.dichromatic_number(n, arcs, ub=5) if isc3 else None
        rows.append({"sizes": [s, s, s], "n": n, "is_C3": isc3, "chi": chi})
        print(f"  [{s},{s},{s}] n={n} is_C3={isc3} chi={chi}", flush=True)
        if isc3 and chi is not None and chi >= 3:
            bad.append(rows[-1])
    # some unbalanced [a,b,c]
    for sizes in ([1, 2, 3], [2, 3, 4], [1, 1, 5], [3, 3, 4], [4, 4, 5]):
        n, arcs = cyclic_partite(sizes)
        isc3 = core.is_C3(n, arcs)
        chi = core.dichromatic_number(n, arcs, ub=5) if isc3 else None
        rows.append({"sizes": sizes, "n": n, "is_C3": isc3, "chi": chi})
        print(f"  {sizes} n={n} is_C3={isc3} chi={chi}", flush=True)
        if isc3 and chi is not None and chi >= 3:
            bad.append(rows[-1])
    # r=4 cyclic should leave C_3
    n, arcs = cyclic_partite([1, 1, 1, 1])
    print(f"  r=4 [1,1,1,1] is_C3={core.is_C3(n, arcs)} (expect False: "
          f"induced directed 4-cycle)", flush=True)
    return rows, bad


def out_in_twin_pairs(n, arcs):
    """Count pairs u<w that are BOTH out-twins and in-twins (identical out-nbr
    and in-nbr sets, excluding each other)."""
    out, inn = core._out_in(n, arcs)
    pairs = 0
    for u in range(n):
        for w in range(u + 1, n):
            ou, ow = out[u] - {w}, out[w] - {u}
            iu, iw = inn[u] - {w}, inn[w] - {u}
            if ou == ow and iu == iw:
                pairs += 1
    return pairs


def part_c_twins():
    print("=== (c) twin structure of C_3 digraphs n<=7 ===", flush=True)
    # chi_vec vs has-twin-pair tabulation
    table = {}  # (chi, has_twin) -> count
    chi2_with_twin = 0
    chi2_total = 0
    for n in range(1, 8):
        t0 = time.time()
        for (gn, edges) in core.all_simple_graphs(n):
            for arcs in core.all_orientations(edges):
                if not core.is_C3(n, arcs):
                    continue
                chi = core.dichromatic_number(n, arcs, ub=3)
                tw = out_in_twin_pairs(n, arcs) > 0
                table[(chi, tw)] = table.get((chi, tw), 0) + 1
                if chi == 2:
                    chi2_total += 1
                    if tw:
                        chi2_with_twin += 1
        print(f"  n={n} done elapsed={time.time()-t0:.1f}s", flush=True)
    print(f"  chi_vec x has_twin_pair table: {table}", flush=True)
    print(f"  chi=2 C_3 digraphs n<=7: total={chi2_total}  "
          f"with out+in twin pair={chi2_with_twin}  "
          f"twin-reduced(no twins)={chi2_total - chi2_with_twin}", flush=True)
    return table


if __name__ == "__main__":
    viol = part_a_blowup_scan()
    rows, bad = part_b_turan()
    table = part_c_twins()
    print("\n=== SUMMARY ===", flush=True)
    print(f"(a) blow-up monotonicity violations: {len(viol)}", flush=True)
    if viol:
        print(f"    KILL witnesses: {viol[:5]}", flush=True)
    print(f"(b) Turan cyclic-partite chi>=3 hits: {len(bad)}", flush=True)
    if bad:
        print(f"    KILL/m(3)-witness: {bad}", flush=True)
    print(f"(c) twin table: {table}", flush=True)
