"""GROUND the order-robust block-PROJECTION argument for the composition-law
upper bound  omega_vec(T[H]) <= ov(T) + ov(H) - 1.

For each exact-feasible product P = T[H] (nT*nH <= 9 so we can brute-force the
optimal order, plus nT*nH <= 12 for the value via bb):

  (1) compute ov(T), ov(H), ov(P) exactly; check ov(P) == ov(T)+ov(H)-1  (KILL-b if >).
  (2) For an OPTIMAL order pi of P (achieving ov(P)), build the backedge graph and
      enumerate ALL maximum cliques K (networkx find_cliques, take max-size ones).
      For EACH maximum clique K:
        - blocks(K) = set of outer-blocks a met by K.
        - per-block: K restricted to block a is a backedge clique of H under pi|block;
          its size must be <= ov(H).
        - contraction phi(a) = the pi-LAST vertex of K in block a; let
          S = { phi(a) : a in blocks }, ordered by pi-position. TEST whether the
          set of outer-blocks {a} is a backedge clique of T under the order induced
          by pi-position of phi(a)  (KILL-a if it is NOT, i.e. |S| not bounded by ov(T)
          via this map).
        - record |K| vs ov(T)+ov(H)-1, |blocks| vs ov(T).

Reuse core.{beats_matrix, omega_vec, omega_vec_bb, backedge_graph}.
Cross-check the larger (order 10-12) values against the no-K-clique SAT oracle.
"""
import sys, os, json, time, itertools
sys.path.insert(0, os.path.dirname(__file__))
import core
import networkx as nx
from search_4critical_circulant import (
    circ_arcs, omega_vec_ge_K_via_sat, best_order_upper,
)


def ac_gen(n):
    m = (n - 1) // 2
    return set(range(1, m)) | {m + 1}


def c3():
    return 3, [(0, 1), (1, 2), (2, 0)]


def tt(k):
    """transitive tournament 0->1->...->(k-1), all forward."""
    arcs = [(i, j) for i in range(k) for j in range(i + 1, k)]
    return k, arcs


def lex_compose(nT, arcsT, nH, arcsH):
    """T[H]: vertex (a,b) -> flat index a*nH + b.
    arc (a,b)->(a',b') iff beats_T[a][a'] OR (a==a' AND beats_H[b][b'])."""
    bT = core.beats_matrix(nT, arcsT)
    bH = core.beats_matrix(nH, arcsH)
    arcs = []
    def idx(a, b):
        return a * nH + b
    for a in range(nT):
        for b in range(nH):
            for ap in range(nT):
                for bp in range(nH):
                    if a == ap and b == bp:
                        continue
                    # only emit ordered arc once: when this (a,b) beats (ap,bp)
                    if bT[a][ap] or (a == ap and bH[b][bp]):
                        arcs.append((idx(a, b), idx(ap, bp)))
    return nT * nH, arcs


def block_of(v, nH):
    return v // nH


def optimal_order_bruteforce(n, arcs, ov):
    """Return one total order achieving backedge-omega == ov (brute force; n<=9)."""
    beats = core.beats_matrix(n, arcs)
    for order in itertools.permutations(range(n)):
        if core.omega_of_order(n, arcs, order) == ov:
            return list(order)
    return None


def analyze_clique(K, order, nT, nH, beats_T, ov_T, ov_H):
    """K = a maximum clique (set of P-vertices). order = the total order pi (list,
    order[0] = prec-smallest). Returns a dict of the projection diagnostics."""
    pos = {v: i for i, v in enumerate(order)}
    # blocks met
    blocks = sorted({block_of(v, nH) for v in K})
    # per-block clique sizes
    per_block = {}
    for a in blocks:
        per_block[a] = sorted([v for v in K if block_of(v, nH) == a], key=lambda v: pos[v])
    per_block_sizes = {a: len(vs) for a, vs in per_block.items()}
    per_block_ok = all(s <= ov_H for s in per_block_sizes.values())
    # contraction phi(a) = pi-LAST vertex of K in block a
    phi = {a: max(per_block[a], key=lambda v: pos[v]) for a in blocks}
    # build the outer-block backedge graph under the order induced by pi-position of phi(a):
    # blocks a<b in pi-position-of-phi; edge iff arc beats_T[b_blk][a_blk] (back arc in T).
    # i.e. treat the blocks as vertices of T, ordered by pos[phi(a)].
    blk_sorted = sorted(blocks, key=lambda a: pos[phi[a]])
    # T-backedge graph among these blocks: for i<j (a=blk_sorted[i] earlier),
    # edge iff arc b->a in T, i.e. beats_T[b][a]
    Tg = nx.Graph()
    Tg.add_nodes_from(blk_sorted)
    for i in range(len(blk_sorted)):
        a = blk_sorted[i]
        for j in range(i + 1, len(blk_sorted)):
            b = blk_sorted[j]
            if beats_T[b][a]:
                Tg.add_edge(a, b)
    # Is the FULL block set a clique in this T-backedge graph?
    is_T_clique = all(Tg.has_edge(blk_sorted[i], blk_sorted[j])
                      for i in range(len(blk_sorted))
                      for j in range(i + 1, len(blk_sorted)))
    return {
        "clique_size": len(K),
        "n_blocks": len(blocks),
        "per_block_sizes": per_block_sizes,
        "per_block_le_ovH": per_block_ok,
        "max_per_block": max(per_block_sizes.values()),
        "n_blocks_le_ovT": len(blocks) <= ov_T,
        "block_set_is_T_backedge_clique": is_T_clique,
    }


def main():
    out = {"products": []}
    t0 = time.time()
    nC, aC = c3()

    products = []
    # exact brute-forceable (order <= 9)
    products.append(("C3[C3]", (nC, aC), (nC, aC)))
    products.append(("C3[TT2]", (nC, aC), tt(2)))
    products.append(("TT2[C3]", tt(2), (nC, aC)))
    products.append(("TT3[C3]", tt(3), (nC, aC)))      # order 9
    products.append(("C3[TT3]", (nC, aC), tt(3)))      # order 9
    products.append(("C3[TT2]b", (nC, aC), tt(2)))     # dup harmless
    # AC7-like sub-block tests, order 7..9 outer * inner small
    # AC5 is not 3-critical but ov(AC5)? we just need exact value; use C3 outer with bigger inner
    products.append(("C3[C3]_2", (nC, aC), (nC, aC)))

    for name, (nT, aT), (nH, aH) in products:
        rec = {"name": name, "nT": nT, "nH": nH}
        assert core.is_tournament(nT, aT), f"{name}: T not tournament"
        assert core.is_tournament(nH, aH), f"{name}: H not tournament"
        N, A = lex_compose(nT, aT, nH, aH)
        assert core.is_tournament(N, A), f"{name}: product not tournament"
        rec["order"] = N
        ov_T = core.omega_vec(nT, aT)
        ov_H = core.omega_vec(nH, aH)
        rec["ov_T"] = ov_T
        rec["ov_H"] = ov_H
        rec["law_pred"] = ov_T + ov_H - 1

        if N <= 9:
            ov_P = core.omega_vec(N, A)
        else:
            ov_P = core.omega_vec_bb(N, A)
        rec["ov_P"] = ov_P
        rec["law_holds"] = (ov_P == ov_T + ov_H - 1)
        rec["law_exceeded"] = (ov_P > ov_T + ov_H - 1)   # KILL-b

        beats_T = core.beats_matrix(nT, aT)

        # find an optimal order and enumerate ALL maximum cliques
        clique_diags = []
        kill_a = False
        kill_a_detail = None
        if N <= 9:
            opt_order = optimal_order_bruteforce(N, A, ov_P)
            rec["found_optimal_order"] = opt_order
            # block sequence of the optimal order
            rec["block_sequence"] = [block_of(v, nH) for v in opt_order]
            g = core.backedge_graph(N, A, opt_order)
            all_cliques = list(nx.find_cliques(g))
            maxsz = max((len(c) for c in all_cliques), default=0)
            rec["backedge_omega_of_opt"] = maxsz
            max_cliques = [c for c in all_cliques if len(c) == maxsz]
            rec["n_max_cliques"] = len(max_cliques)
            for K in max_cliques:
                d = analyze_clique(set(K), opt_order, nT, nH, beats_T, ov_T, ov_H)
                clique_diags.append(d)
                if not d["block_set_is_T_backedge_clique"]:
                    kill_a = True
                    kill_a_detail = {"clique": sorted(K), "diag": d}
                if not d["per_block_le_ovH"]:
                    kill_a = True
                    kill_a_detail = {"clique": sorted(K), "diag": d,
                                     "reason": "per_block exceeds ov_H"}
            rec["clique_diags"] = clique_diags
        else:
            rec["found_optimal_order"] = "skipped (n>9, value via bb/SAT only)"

        rec["KILL_a_projection_fails"] = kill_a
        rec["KILL_a_detail"] = kill_a_detail
        out["products"].append(rec)
        print(f"[{name}] order={N} ov_T={ov_T} ov_H={ov_H} law_pred={ov_T+ov_H-1} "
              f"ov_P={ov_P} law_holds={rec['law_holds']} "
              f"KILL_b(exceeded)={rec['law_exceeded']} "
              f"n_max_cliques={rec.get('n_max_cliques')} "
              f"KILL_a={kill_a}", flush=True)
        if clique_diags:
            for d in clique_diags[:6]:
                print(f"    clique sz={d['clique_size']} nblocks={d['n_blocks']} "
                      f"maxperblk={d['max_per_block']}(<=ovH? {d['per_block_le_ovH']}) "
                      f"nblk<=ovT? {d['n_blocks_le_ovT']} "
                      f"T-backedge-clique? {d['block_set_is_T_backedge_clique']}",
                      flush=True)

    out["elapsed_s"] = round(time.time() - t0, 1)
    dp = os.path.join(os.path.dirname(__file__), "..", "data", "ground_projection_law.json")
    with open(os.path.abspath(dp), "w") as f:
        json.dump(out, f, indent=2)

    # overall verdict pieces
    any_kill_b = any(p.get("law_exceeded") for p in out["products"])
    any_kill_a = any(p.get("KILL_a_projection_fails") for p in out["products"])
    all_law = all(p["law_holds"] for p in out["products"])
    print("\n=== SUMMARY ===", flush=True)
    print(f"all law_holds (ov_P == ov_T+ov_H-1): {all_law}", flush=True)
    print(f"ANY KILL-b (law exceeded): {any_kill_b}", flush=True)
    print(f"ANY KILL-a (projection/contraction fails): {any_kill_a}", flush=True)


if __name__ == "__main__":
    main()
