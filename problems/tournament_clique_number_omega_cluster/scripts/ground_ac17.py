"""GROUND the AC_17 proposal: Cay(Z/17, g={1,2,3,4,5,6,7,9}) claimed to be a
VERTEX-TRANSITIVE 3-omega_vec-critical tournament (order 17).

Uses ONLY validated oracle routines from circulant_scan_n17 / iso_critical_scan_n9
(the fast bitmask omega_vec_le2 / le_t, validated vs canonical oracle in ledger P9b)
plus the canonical core for an independent recomputation on small deletions.
"""
import sys, os, time, itertools
sys.path.insert(0, os.path.dirname(__file__))
import core
from circulant_scan_n17 import (
    circulant_arcs, beats_from_arcs, omega_vec_le2_vt,
    circulant_3critical_fast, cross_check, is_consecutive,
)
from iso_critical_scan_n9 import omega_vec_le2, omega_vec_le_t, sub_beats


def omega_of_order(p, beats, order):
    """omega(backedge graph) for one explicit order (canonical via networkx)."""
    import networkx as nx
    pos = [0] * p
    for idx, v in enumerate(order):
        pos[v] = idx
    g = nx.Graph(); g.add_nodes_from(range(p))
    for a in range(p):
        for b in range(a + 1, p):
            u, w = (a, b) if pos[a] < pos[b] else (b, a)  # u earlier
            if beats[w][u]:
                g.add_edge(a, b)
    return max((len(c) for c in nx.find_cliques(g)), default=1)


def main():
    p = 17
    g = (1, 2, 3, 4, 5, 6, 7, 9)
    print(f"=== AC_17 = Cay(Z/17, g={list(g)}) ===", flush=True)

    # ---- 0. validity / generator-set check
    neg = sorted((p - x) % p for x in g)
    print(f"g={list(g)}  -g mod 17={neg}  |g|={len(g)} (need {(p-1)//2})", flush=True)
    assert sorted(set(list(g) + neg)) == list(range(1, p)), "g,-g do not partition {1..16}"
    arcs = circulant_arcs(p, g)
    assert core.is_tournament(p, arcs), "AC_17 is not a tournament"
    print("is_tournament=True ; g,-g partition {1..16} OK", flush=True)
    print("consecutive(g)=", is_consecutive(p, g),
          " (non-consecutive => dodges G7 locality)", flush=True)
    # is g == any QR? 17 == 1 mod 4 => NO Paley tournament exists; informational
    print("17 mod 4 =", p % 4, "(==1 => no QR/Paley tournament, dodges G2)", flush=True)

    beats = beats_from_arcs(p, arcs)

    # ---- 1. SOUNDNESS GUARD on the symmetry reduction:
    # On the order-16 deletion T-0 (NOT vertex-transitive) the fast le2 is the
    # unrestricted one; we already trust le2 (P9b). Here we instead validate the
    # SYM reduction self-consistency: for AC_17 itself, le2_vt should be a valid
    # proxy. We cannot run unrestricted le2 on order 17 cheaply as a guard for the
    # FALSE answer, so we rely on cross_check (P8/P9/QR_11) which DOES compare
    # le2_vt vs le2 on orders 11,13 where both are feasible.
    print("\n--- cross-check fast pipeline vs PROVED ledger witnesses (P8,P9,QR_11) ---", flush=True)
    ok = cross_check()
    print("CROSS-CHECK PASS =", ok, flush=True)
    if not ok:
        print("ABORT: fast pipeline disagrees with proved witnesses", flush=True)
        sys.exit(2)

    # ---- 2. LOWER BOUND: omega_vec(AC_17) >= 3  <=>  no triangle-free order.
    print("\n--- lower bound: triangle-free-order search (omega_vec<=2 ?) ---", flush=True)
    t0 = time.time()
    le2 = omega_vec_le2_vt(p, beats, fixed_first=0)
    dt = time.time() - t0
    print(f"omega_vec_le2_vt(AC_17) = {le2}  ({dt:.1f}s)   "
          f"(False => NO triangle-free order => omega_vec >= 3)", flush=True)

    # ---- 3. UPPER BOUND: exhibit an explicit order with omega(backedge)=3.
    print("\n--- upper bound: witnessing order with omega(backedge)=3 ---", flush=True)
    best_w, best_order = p, None
    # try identity + all cyclic rotations + a few greedy/random orders
    import random
    rng = random.Random(0)
    cand_orders = [list(range(p))]
    cand_orders += [[(i + s) % p for i in range(p)] for s in range(p)]
    for _ in range(50):
        o = list(range(p)); rng.shuffle(o); cand_orders.append(o)
    for o in cand_orders:
        w = omega_of_order(p, beats, o)
        if w < best_w:
            best_w, best_order = w, o
            if best_w <= 3:
                break
    print(f"min omega(backedge) over sampled orders = {best_w}", flush=True)
    assert best_w == 3, f"upper bound not 3 (got {best_w})"
    print("=> omega_vec(AC_17) <= 3 (explicit witnessing order found)", flush=True)
    print("witness order:", best_order, flush=True)

    # combine: >=3 and <=3 => == 3
    assert le2 is False, "le2_vt returned True => omega_vec<=2, contradicts proposal"
    print("\n>>> omega_vec(AC_17) = 3  (>=3 from triangle-free search False, <=3 from witness)", flush=True)

    # ---- 4. CRITICALITY: deletion of vertex 0 => omega_vec = 2.
    print("\n--- criticality: deletion T-0 (vertex-transitive => one deletion suffices) ---", flush=True)
    m, sb = sub_beats(p, beats, 0)
    t0 = time.time()
    del_le2 = omega_vec_le2(m, sb)         # UNRESTRICTED (T-0 not vertex-transitive)
    dt = time.time() - t0
    score = [sum(sb[u][v] for v in range(m)) for u in range(m)]
    transitive = sorted(score) == list(range(m))
    print(f"omega_vec_le2(AC_17 - 0) = {del_le2}  transitive={transitive}  ({dt:.1f}s)", flush=True)
    # independent recomputation via the canonical core on the order-16 deletion
    keep = [w for w in range(p) if w != 0]
    relabel = {w: i for i, w in enumerate(keep)}
    ks = set(keep)
    sub_arcs = [(relabel[u], relabel[v]) for (u, v) in arcs if u in ks and v in ks]
    t0 = time.time()
    can_del = core.omega_vec_bb(m, sub_arcs, ub=3)
    print(f"CANONICAL core.omega_vec_bb(AC_17 - 0, ub=3) = {can_del}  "
          f"({time.time()-t0:.1f}s)  (independent recomputation)", flush=True)

    # ---- 5. fast pipeline verdict
    print("\n--- fast pipeline circulant_3critical_fast ---", flush=True)
    t0 = time.time()
    w_class, is_crit, _ = circulant_3critical_fast(p, g)
    print(f"circulant_3critical_fast: omega_vec_class={w_class} 3critical={is_crit} "
          f"({time.time()-t0:.1f}s)", flush=True)

    print("\n=== SUMMARY ===", flush=True)
    print(f"omega_vec(AC_17) = 3 : {le2 is False and best_w == 3}", flush=True)
    print(f"omega_vec(AC_17 - 0) = 2 : {del_le2 is True and not transitive and can_del == 2}", flush=True)
    print(f"3-omega_vec-critical (vertex-transitive collapse): "
          f"{le2 is False and del_le2 is True and not transitive and can_del == 2}", flush=True)


if __name__ == "__main__":
    main()
