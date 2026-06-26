"""Step 1 of the two-copy split-sum proposal: verify

  (A1) every MAXIMUM backedge clique of C3[H]^prec meets AT MOST TWO of the 3
       copies, and
  (A2) the direct merged backedge clique number equals the proposal's
       split-sum formula:
         omega_be(prec) == max over the 3 cyclic copy-pairs (Y,X) of
           max_p [ omega_be(Y-prefix before p) + omega_be(X-suffix from p) ]

Grounded against the EXACT oracle (core.backedge_graph / core.clique_number).
ANY mismatch (formula!=direct, or a max clique meeting all 3 copies) KILLS leg A.
"""
import sys, time, itertools, random
sys.path.insert(0, 'scripts')
import core
import networkx as nx

C3_ARCS = [(0, 1), (1, 2), (2, 0)]  # 0->1->2->0


def lex_c3(nH, aH):
    """C3[H]: vertex (a,b) -> a*nH+b.  Arc iff a beats a' in C3 OR (a==a' and b beats b' in H)."""
    bH = core.beats_matrix(nH, aH)
    bT = core.beats_matrix(3, C3_ARCS)
    arcs = [(a * nH + b, ap * nH + bp)
            for a in range(3) for b in range(nH)
            for ap in range(3) for bp in range(nH)
            if (a, b) != (ap, bp) and (bT[a][ap] or (a == ap and bH[b][bp]))]
    return 3 * nH, arcs


def copy_of(v, nH):
    return v // nH


def omega_be_subset(beats, order_subset):
    """ordinary clique number of the backedge graph induced on the given ordered
    list `order_subset` (positions in order; edge a-b for i<j iff beats[order[j]][order[i]])."""
    m = len(order_subset)
    if m == 0:
        return 0
    g = nx.Graph(); g.add_nodes_from(range(m))
    for i in range(m):
        a = order_subset[i]
        for j in range(i + 1, m):
            b = order_subset[j]
            if beats[b][a]:
                g.add_edge(i, j)
    return max((len(c) for c in nx.find_cliques(g)), default=1)


def split_sum_formula(n, beats, order, nH):
    """max over 3 cyclic copy-pairs (Y,X) of max_p [omega_be(Y before p) + omega_be(X from p)].

    The 3 cross-copy precedence directions in C3 that produce a backedge when
    Y-vertex is BEFORE X-vertex are the arcs X->Y in C3.  C3 arcs: 0->1,1->2,2->0,
    so cross-pairs (Y,X) with X->Y are (Y,X) in {(1,0),(2,1),(0,2)}.
    For each such pair, scan a split point p over the order; left part = Y-copy
    vertices before p, right part = X-copy vertices from p on; the cross arcs are
    automatic so the two backedge-cliques combine.  Take the global max.
    """
    pairs = [(1, 0), (2, 1), (0, 2)]
    best = 0
    for (Y, X) in pairs:
        Ypos = [v for v in order if copy_of(v, nH) == Y]
        Xpos = [v for v in order if copy_of(v, nH) == X]
        # split over position p in the full order: Y-vertices with index < p,
        # X-vertices with index >= p
        pos_index = {v: i for i, v in enumerate(order)}
        # candidate split points = all positions 0..n
        for p in range(n + 1):
            left = [v for v in Ypos if pos_index[v] < p]
            right = [v for v in Xpos if pos_index[v] >= p]
            wl = omega_be_subset(beats, left)
            wr = omega_be_subset(beats, right)
            if wl + wr > best:
                best = wl + wr
    return best


def max_clique_meets_three(n, arcs, order, nH):
    """True iff SOME maximum backedge clique of the order meets all 3 copies."""
    g = core.backedge_graph(n, arcs, order)
    omega = core.clique_number(g)
    for c in nx.find_cliques(g):
        if len(c) == omega:
            copies = {copy_of(v, nH) for v in c}
            if len(copies) == 3:
                return True, omega
    return False, omega


def run_one(nH, aH, order):
    n, arcs = lex_c3(nH, aH)
    beats = core.beats_matrix(n, arcs)
    direct = core.omega_of_order(n, arcs, order)
    formula = split_sum_formula(n, beats, order, nH)
    meets3, _ = max_clique_meets_three(n, arcs, order, nH)
    return direct, formula, meets3


def main():
    t0 = time.time()
    fails = []
    three_copy_hits = 0
    n_orders = 0

    # (a) GOLD object: data/ground_h21_skeleton_sat.json (C3[QR_19], witness order)
    import json
    gold = json.load(open('data/ground_h21_skeleton_sat.json'))
    qr19 = sorted({(x * x) % 19 for x in range(1, 19)})
    arcs19 = [(i, (i + d) % 19) for i in range(19) for d in qr19]
    assert core.is_tournament(19, arcs19)
    nH = 19
    n, arcs = lex_c3(nH, arcs19)
    assert n == 57 == gold['order']
    beats = core.beats_matrix(n, arcs)
    wo = gold['witness_order']
    direct = core.omega_of_order(n, arcs, wo)
    formula = split_sum_formula(n, beats, wo, nH)
    meets3, om = max_clique_meets_three(n, arcs, wo, nH)
    print(f"GOLD C3[QR_19] witness: direct={direct} formula={formula} "
          f"max_clique_meets_3copies={meets3}", flush=True)
    if direct != formula:
        fails.append(("GOLD", direct, formula))
    if meets3:
        three_copy_hits += 1
    n_orders += 1

    # (b) random H of orders 4-7, many random orders of C3[H]
    rng = random.Random(20240611)
    for trial in range(20):
        nH = rng.choice([4, 5, 6, 7])
        # random tournament on nH vertices
        aH = []
        for i in range(nH):
            for j in range(i + 1, nH):
                if rng.random() < 0.5:
                    aH.append((i, j))
                else:
                    aH.append((j, i))
        n, arcs = lex_c3(nH, aH)
        beats = core.beats_matrix(n, arcs)
        for _ in range(10):
            order = list(range(n)); rng.shuffle(order)
            direct = core.omega_of_order(n, arcs, order)
            formula = split_sum_formula(n, beats, order, nH)
            meets3, om = max_clique_meets_three(n, arcs, order, nH)
            n_orders += 1
            if direct != formula:
                fails.append(("rand", nH, direct, formula, order))
            if meets3:
                three_copy_hits += 1
                if three_copy_hits <= 3:
                    print(f"  THREE-COPY max clique found nH={nH} omega={om}", flush=True)
        print(f"  trial {trial}: nH={nH} done (cumulative orders={n_orders}, "
              f"fails={len(fails)}, three_copy_hits={three_copy_hits})", flush=True)

    print("=== SUMMARY ===", flush=True)
    print(f"orders tested: {n_orders}", flush=True)
    print(f"formula!=direct mismatches: {len(fails)}", flush=True)
    print(f"max-clique-meets-all-3-copies hits: {three_copy_hits}", flush=True)
    if fails:
        print("FIRST FAILS:", flush=True)
        for f in fails[:5]:
            print("  ", f, flush=True)
    verdict_A = (len(fails) == 0 and three_copy_hits == 0)
    print(f"LEG_A_HOLDS: {verdict_A}", flush=True)
    print(f"elapsed {time.time()-t0:.1f}s", flush=True)


if __name__ == "__main__":
    main()
