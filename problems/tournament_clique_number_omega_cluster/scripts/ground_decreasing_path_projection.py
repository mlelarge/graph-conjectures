"""GROUND the H11 decreasing-path-projection certificate (literature-reduction lens).

Claim under test (the proposal):
  In a substitution product T[H] (vertices (a,b), flat index a*nH+b), for an
  OPTIMAL backedge order, a MAXIMUM clique C of the backedge graph, decoded to
  (block a, internal b) coordinates, satisfies:
    (i)  number of DISTINCT block-values a in C  <=  ov(T)
    (ii) max multiplicity of any single block-value a in C  <=  ov(H)
    (iii) |C| == ov(T) + ov(H) - 1   (the additive overlap law)
  And the block-concatenated order [a*nH+b for a in sigma_T for b in tau_H]
  gives omega STRICTLY ABOVE ov(T)+ov(H)-1 (documents the queued next_action is wrong).

KILL: some exact product has an optimal-order max clique whose block-projection
  visits > ov(T) distinct blocks, OR a single block contributes > ov(H) internals,
  OR omega_vec(T[H]) != ov(T)+ov(H)-1.
"""
import sys, os, json, time, itertools
sys.path.insert(0, os.path.dirname(__file__))
import core
import networkx as nx
from search_4critical_circulant import (
    circ_arcs, omega_vec_ge_K_via_sat, best_order_upper,
)
from ground_lex_compose_c3 import lex_compose, ac_gen


def c3():
    return 3, [(0, 1), (1, 2), (2, 0)]


def tt(k):
    """Transitive tournament TT_k: i->j for i<j. omega_vec=1."""
    return k, [(i, j) for i in range(k) for j in range(i + 1, k)]


def qr(p):
    """Paley / QR tournament on Z/p, p=3 mod 4."""
    res = sorted({(x * x) % p for x in range(1, p)})
    return p, circ_arcs(p, set(res))


# ---- exact optimal order + a witnessing max clique -------------------------- #

def optimal_order_and_clique(n, arcs):
    """Brute-force / search the order minimizing backedge-omega; return
    (omega_vec, an optimal order, a maximum clique of its backedge graph).
    Feasible for n<=~10 by full permutation enumeration."""
    beats = core.beats_matrix(n, arcs)
    best_w = n + 1
    best_order = None
    # full enumeration over orders. n<=10 => 10! = 3.6M; cap to <=9 for full,
    # for n=10 use a rotation+sample fallback but here we only call this for n<=9.
    for order in itertools.permutations(range(n)):
        g = nx.Graph()
        g.add_nodes_from(range(n))
        for i in range(n):
            a = order[i]
            for j in range(i + 1, n):
                b = order[j]
                if beats[b][a]:
                    g.add_edge(a, b)
        w = core.clique_number(g)
        if w < best_w:
            best_w = w
            best_order = order
            if best_w <= 1:
                break
    # rebuild best backedge graph and extract a max clique
    g = core.backedge_graph(n, arcs, list(best_order))
    cliques = list(nx.find_cliques(g))
    maxc = max(cliques, key=len)
    return best_w, list(best_order), sorted(maxc)


def decode(v, nH):
    return (v // nH, v % nH)


def block_concat_order(nT, sigmaT, nH, tauH):
    """[a*nH+b for a in sigmaT for b in tauH] -- the queued next_action's order."""
    return [a * nH + b for a in sigmaT for b in tauH]


def main():
    out = {"products": []}
    t0 = time.time()

    nC, aC = c3()
    nT2, aT2 = tt(2)
    nT3, aT3 = tt(3)
    nQR7, aQR7 = qr(7)

    factors = {
        "C3": (nC, aC, 2),
        "TT2": (nT2, aT2, 1),
        "TT3": (nT3, aT3, 1),
        "QR7": (nQR7, aQR7, 3),
    }
    # confirm ov of each factor exactly (small)
    for name, (n, a, claimed) in factors.items():
        ov = core.omega_vec(n, a)
        out.setdefault("factor_ov", {})[name] = {"n": n, "ov": ov, "claimed": claimed,
                                                 "agree": ov == claimed}
        print(f"factor {name}: n={n} ov={ov} (claimed {claimed})", flush=True)

    # grid of products. EXACT-feasible (order<=9 for full perm optimal-order)
    # vs SAT-only (order 10..21).
    exact_pairs = [
        ("C3", "C3"),    # 9
        ("C3", "TT2"),   # 6
        ("C3", "TT3"),   # 9
        ("TT2", "C3"),   # 6
        ("TT3", "C3"),   # 9
        ("TT2", "TT3"),  # 6
        ("TT3", "TT2"),  # 6
        ("TT2", "TT2"),  # 4
        ("TT3", "TT3"),  # 9
    ]
    sat_pairs = [
        ("QR7", "C3"),   # 21
        ("QR7", "TT2"),  # 14
        ("QR7", "TT3"),  # 21
        ("C3", "QR7"),   # 21
        ("TT2", "QR7"),  # 14
        ("TT3", "QR7"),  # 21
    ]

    print("\n=== EXACT products: optimal order, max-clique projection ===", flush=True)
    for (tn, hn) in exact_pairs:
        nT, aT, _ = factors[tn]
        nH, aH, _ = factors[hn]
        ovT = core.omega_vec(nT, aT)
        ovH = core.omega_vec(nH, aH)
        N, A = lex_compose(nT, aT, nH, aH)
        assert core.is_tournament(N, A), f"{tn}[{hn}] not a tournament"
        predicted = ovT + ovH - 1

        w, order, clique = optimal_order_and_clique(N, A)
        decoded = [decode(v, nH) for v in clique]
        blocks = [a for (a, b) in decoded]
        distinct_blocks = len(set(blocks))
        from collections import Counter
        block_mult = Counter(blocks)
        max_block_mult = max(block_mult.values())

        # block-concat counter-check (sigma_T, tau_H = optimal orders of T, H)
        _, sigmaT, _ = optimal_order_and_clique(nT, aT)
        _, tauH, _ = optimal_order_and_clique(nH, aH)
        concat = block_concat_order(nT, sigmaT, nH, tauH)
        concat_omega = core.omega_of_order(N, A, concat)

        rec = {
            "product": f"{tn}[{hn}]", "order": N, "ov_T": ovT, "ov_H": ovH,
            "predicted": predicted, "actual_ov": w,
            "clique_decode": decoded, "distinct_blocks": distinct_blocks,
            "max_block_mult": max_block_mult, "clique_size": len(clique),
            "concat_order_omega": concat_omega,
            "law_agree": (w == predicted),
            "cert_distinct_ok": distinct_blocks <= ovT,
            "cert_mult_ok": max_block_mult <= ovH,
            "cert_size_ok": len(clique) == predicted,
            "concat_strictly_above": concat_omega > predicted,
        }
        out["products"].append(rec)
        print(f"  {tn}[{hn}] order={N}: ov={w} pred={predicted} "
              f"distinct_blocks={distinct_blocks}(<= {ovT}? {rec['cert_distinct_ok']}) "
              f"max_block_mult={max_block_mult}(<= {ovH}? {rec['cert_mult_ok']}) "
              f"size={len(clique)}(== {predicted}? {rec['cert_size_ok']}) "
              f"concat_omega={concat_omega}(> {predicted}? {rec['concat_strictly_above']})",
              flush=True)
        print(f"      clique decode={decoded}", flush=True)

    print("\n=== SAT products: pin omega_vec, confirm == ov(T)+ov(H)-1 ===", flush=True)
    for (tn, hn) in sat_pairs:
        if time.time() - t0 > 520:
            out["products"].append({"product": f"{tn}[{hn}]", "status": "skipped_time"})
            print(f"  {tn}[{hn}]: skipped (time budget)", flush=True)
            continue
        nT, aT, _ = factors[tn]
        nH, aH, _ = factors[hn]
        ovT = core.omega_vec(nT, aT)
        ovH = core.omega_vec(nH, aH)
        N, A = lex_compose(nT, aT, nH, aH)
        assert core.is_tournament(N, A), f"{tn}[{hn}] not a tournament"
        predicted = ovT + ovH - 1
        # pin omega_vec via SAT: ge_pred (UNSAT) and not ge_{pred+1} (SAT) and upper==pred
        ge_p, dtp, _ = omega_vec_ge_K_via_sat(N, A, predicted)
        ge_p1, dtp1, _ = omega_vec_ge_K_via_sat(N, A, predicted + 1)
        upper = best_order_upper(N, A, tries=200)
        pinned = ge_p and (not ge_p1) and (upper == predicted)
        rec = {
            "product": f"{tn}[{hn}]", "order": N, "ov_T": ovT, "ov_H": ovH,
            "predicted": predicted, "ge_pred_UNSAT": ge_p,
            "ge_predplus1": ge_p1, "best_upper": upper,
            "omega_vec_pinned": (predicted if pinned else None),
            "law_agree": pinned,
        }
        out["products"].append(rec)
        print(f"  {tn}[{hn}] order={N}: pred={predicted} ge{predicted}(UNSAT)={ge_p} "
              f"ge{predicted+1}={ge_p1} upper={upper} => pinned=={predicted}? {pinned} "
              f"(t={dtp:.2f}/{dtp1:.2f}s)", flush=True)

    out["elapsed_s"] = round(time.time() - t0, 1)
    dp = os.path.join(os.path.dirname(__file__), "..", "data",
                      "ground_decreasing_path_projection.json")
    with open(os.path.abspath(dp), "w") as f:
        json.dump(out, f, indent=2)
    print("\n=== DONE ===", flush=True)


if __name__ == "__main__":
    main()
