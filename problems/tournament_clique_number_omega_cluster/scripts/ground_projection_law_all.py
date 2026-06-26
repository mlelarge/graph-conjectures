"""STRESS the order-robust projection: test the contraction map on EVERY total
order pi (not just one optimal order) and EVERY maximum clique of pi's backedge
graph, for every brute-forceable product. Also test on the SPECIFIC interleaved
optimal order the proposal cites for C3[C3].

KILL-a fires if for ANY order pi and ANY clique K of size > ov(T)+ov(H)-1 the
bound is violated, OR if for an order achieving |K| = ov(T)+ov(H)-1 the
block-contraction does NOT certify the block set as a T-backedge clique.

We focus the contraction test on cliques whose block-span needs the full ov(T)
budget (the interleaving-sensitive case).
"""
import sys, os, json, time, itertools
sys.path.insert(0, os.path.dirname(__file__))
import core
import networkx as nx


def c3():
    return 3, [(0, 1), (1, 2), (2, 0)]

def tt(k):
    return k, [(i, j) for i in range(k) for j in range(i + 1, k)]

def lex_compose(nT, arcsT, nH, arcsH):
    bT = core.beats_matrix(nT, arcsT)
    bH = core.beats_matrix(nH, arcsH)
    arcs = []
    for a in range(nT):
        for b in range(nH):
            for ap in range(nT):
                for bp in range(nH):
                    if a == ap and b == bp:
                        continue
                    if bT[a][ap] or (a == ap and bH[b][bp]):
                        arcs.append((a * nH + b, ap * nH + bp))
    return nT * nH, arcs


def contraction_ok(K, order, nT, nH, beats_T, ov_T, ov_H):
    pos = {v: i for i, v in enumerate(order)}
    blocks = sorted({v // nH for v in K})
    per_block = {a: [v for v in K if v // nH == a] for a in blocks}
    per_block_ok = all(len(vs) <= ov_H for vs in per_block.values())
    phi = {a: max(per_block[a], key=lambda v: pos[v]) for a in blocks}
    blk_sorted = sorted(blocks, key=lambda a: pos[phi[a]])
    # T-backedge graph among blocks under phi-order
    is_T_clique = True
    for i in range(len(blk_sorted)):
        a = blk_sorted[i]
        for j in range(i + 1, len(blk_sorted)):
            b = blk_sorted[j]  # later in pi-position-of-phi
            if not beats_T[b][a]:   # need back arc b->a to be an edge
                is_T_clique = False
    n_blk_ok = len(blocks) <= ov_T
    return per_block_ok, is_T_clique, n_blk_ok, len(blocks), max(len(v) for v in per_block.values())


def stress_product(name, nT, aT, nH, aH, max_order_full=9):
    N, A = lex_compose(nT, aT, nH, aH)
    assert core.is_tournament(N, A)
    ov_T = core.omega_vec(nT, aT)
    ov_H = core.omega_vec(nH, aH)
    ov_P = core.omega_vec(N, A) if N <= max_order_full else core.omega_vec_bb(N, A)
    law_pred = ov_T + ov_H - 1
    beats_T = core.beats_matrix(nT, aT)

    rec = {"name": name, "order": N, "ov_T": ov_T, "ov_H": ov_H,
           "law_pred": law_pred, "ov_P": ov_P,
           "law_holds": ov_P == law_pred, "law_exceeded": ov_P > law_pred}

    if N > max_order_full:
        rec["full_order_scan"] = "skipped"
        return rec, False, False

    # iterate over ALL orders; for each, all maximum cliques. Track worst cases.
    kill_a = False               # contraction fails on a law-saturating clique
    kill_b_local = False         # some order yields a clique > law_pred (cannot happen if ov_P==law)
    orders_checked = 0
    optimal_orders = 0
    interleaved_optimal = 0
    saturating_clique_checks = 0
    saturating_contraction_fail = 0
    example_interleaved = None
    for order in itertools.permutations(range(N)):
        orders_checked += 1
        g = core.backedge_graph(N, A, list(order))
        cliques = list(nx.find_cliques(g))
        msz = max((len(c) for c in cliques), default=0)
        if msz < ov_P:
            continue  # not an optimal order; the projection bound concerns optimal orders
        optimal_orders += 1
        # is this order block-interleaved (some block split)?
        blkseq = [v // nH for v in order]
        # split if any block's positions are non-contiguous
        split = False
        for a in range(nT):
            ppos = [i for i, b in enumerate(blkseq) if b == a]
            if ppos and (max(ppos) - min(ppos) + 1) != len(ppos):
                split = True
                break
        if split:
            interleaved_optimal += 1
            if example_interleaved is None:
                example_interleaved = list(order)
        for K in cliques:
            if len(K) > law_pred:
                kill_b_local = True
            if len(K) == law_pred:  # law-saturating clique: contraction must certify
                saturating_clique_checks += 1
                pb_ok, isTclq, nblk_ok, nblk, maxpb = contraction_ok(
                    set(K), list(order), nT, nH, beats_T, ov_T, ov_H)
                if not (pb_ok and isTclq and nblk_ok):
                    saturating_contraction_fail += 1
                    kill_a = True
                    rec.setdefault("kill_a_examples", []).append({
                        "order": list(order), "clique": sorted(K),
                        "per_block_le_ovH": pb_ok, "block_set_T_clique": isTclq,
                        "n_blocks_le_ovT": nblk_ok, "n_blocks": nblk, "max_per_block": maxpb})

    rec.update({
        "orders_checked": orders_checked,
        "optimal_orders": optimal_orders,
        "interleaved_optimal_orders": interleaved_optimal,
        "example_interleaved_optimal": example_interleaved,
        "saturating_clique_checks": saturating_clique_checks,
        "saturating_contraction_fails": saturating_contraction_fail,
    })
    return rec, kill_a, kill_b_local


def main():
    out = {"products": []}
    t0 = time.time()
    nC, aC = c3()
    products = [
        ("C3[C3]", nC, aC, nC, aC),       # order 9, ov 3, the interleaved case
        ("C3[TT2]", nC, aC, *tt(2)),      # order 6
        ("TT2[C3]", *tt(2), nC, aC),      # order 6
        ("TT3[C3]", *tt(3), nC, aC),      # order 9
        ("C3[TT3]", nC, aC, *tt(3)),      # order 9
        ("TT2[TT2]", *tt(2), *tt(2)),     # order 4, ov 1
    ]
    any_kill_a = False
    any_kill_b = False
    all_law = True
    for p in products:
        if time.time() - t0 > 540:
            print(f"TIME BUDGET hit before {p[0]}", flush=True)
            break
        name = p[0]
        nT, aT = p[1], p[2]
        nH, aH = p[3], p[4]
        rec, ka, kb = stress_product(name, nT, aT, nH, aH)
        out["products"].append(rec)
        any_kill_a = any_kill_a or ka
        any_kill_b = any_kill_b or kb or rec["law_exceeded"]
        all_law = all_law and rec["law_holds"]
        print(f"[{name}] order={rec['order']} ov_T={rec['ov_T']} ov_H={rec['ov_H']} "
              f"law_pred={rec['law_pred']} ov_P={rec['ov_P']} law_holds={rec['law_holds']} "
              f"opt_orders={rec.get('optimal_orders')} interleaved_opt={rec.get('interleaved_optimal_orders')} "
              f"satur_checks={rec.get('saturating_clique_checks')} "
              f"contraction_fails={rec.get('saturating_contraction_fails')} "
              f"KILL_a={ka} KILL_b={kb}", flush=True)

    out["elapsed_s"] = round(time.time() - t0, 1)
    dp = os.path.join(os.path.dirname(__file__), "..", "data", "ground_projection_law_all.json")
    with open(os.path.abspath(dp), "w") as f:
        json.dump(out, f, indent=2)
    print("\n=== SUMMARY ===", flush=True)
    print(f"all law_holds: {all_law}", flush=True)
    print(f"ANY KILL-a (contraction fails on a saturating clique in ANY order): {any_kill_a}", flush=True)
    print(f"ANY KILL-b (clique exceeds law bound): {any_kill_b}", flush=True)


if __name__ == "__main__":
    main()
