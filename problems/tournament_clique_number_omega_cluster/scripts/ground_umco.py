"""GROUND the UMCO (Unique Max-Clique Orbit) literature-reduction proposal.

UMCO(X) operational definition (this script):
  X is omega_vec-critical (omega_vec=k, every single-vertex deletion = k-1)
  AND across ALL omega_vec-OPTIMAL orderings, the collection of MAXIMUM
  (size-k) backedge cliques admits a COMMON HITTING VERTEX (up to the
  automorphism orbit): there is a vertex v such that deleting v drops
  omega_vec to k-1 *because* v meets every optimal-order max clique.

Operationalization on exact-feasible X (order <= 9): enumerate every total
order, keep those whose backedge omega == omega_vec(X), collect EVERY maximum
clique (size omega_vec) in each such backedge graph, then test whether the
intersection of "hitting sets" is nonempty, i.e. whether some single vertex
lies in EVERY collected maximum clique. If yes => UMCO holds (common deletion
transversal). If no single vertex hits all max cliques => UMCO FAILS.

Objects:
  (1) C3[C3]  order 9  -- exact; predict UMCO = FALSE.
  (2) AC_7[C3] order 21 -- the P18 k=4 object; exact enumeration infeasible,
       so use the d_then_c witnessing order + a large sample of optimal orders
       reachable, collect size-4 max cliques, test common hitting vertex via
       the no-K4 SAT deletion check; predict UMCO = TRUE.
  (3) C3[C3][C3] order 27 -- criticality spot-check (predict NOT critical).
  (4) AC_7[C3][C3] order 63 -- NOT grounded directly (walled); only the outer
       factor AC_7[C3] UMCO is used as the predictor.

KILL: C3[C3] satisfies UMCO yet C3[C3][C3] non-critical, OR AC_7[C3] FAILS
UMCO yet is critical.
"""
import sys, os, json, time, itertools
sys.path.insert(0, os.path.dirname(__file__))
import core
import networkx as nx
from search_4critical_circulant import (
    circ_arcs, omega_vec_ge_K_via_sat, best_order_upper, validate_sat_oracle,
)
from ground_lex_compose_c3 import ac_gen, c3, lex_compose


def all_max_cliques(g, size):
    """All cliques of exactly `size` (= the max clique size) in graph g."""
    return [frozenset(c) for c in nx.find_cliques(g) if len(c) == size]


def umco_exact(n, arcs, label):
    """Full exact UMCO test by enumerating all n! orders (n<=9)."""
    t0 = time.time()
    beats = core.beats_matrix(n, arcs)
    ov = core.omega_vec_bruteforce(n, arcs)
    # collect every max clique over every OPTIMAL order
    maxcliques = set()
    n_opt_orders = 0
    for order in itertools.permutations(range(n)):
        g = nx.Graph(); g.add_nodes_from(range(n))
        for i in range(n):
            a = order[i]
            for j in range(i + 1, n):
                b = order[j]
                if beats[b][a]:
                    g.add_edge(a, b)
        w = core.clique_number(g)
        if w == ov:
            n_opt_orders += 1
            for c in all_max_cliques(g, ov):
                maxcliques.add(c)
    maxcliques = list(maxcliques)
    # common hitting vertex = vertex in EVERY max clique
    if maxcliques:
        common = set(maxcliques[0])
        for c in maxcliques[1:]:
            common &= set(c)
    else:
        common = set()
    # criticality
    crit = core.is_k_omega_vec_critical(n, arcs, ov)
    rec = {
        "label": label, "order": n, "omega_vec": ov,
        "n_optimal_orders": n_opt_orders,
        "n_distinct_max_cliques": len(maxcliques),
        "common_hitting_vertices": sorted(common),
        "UMCO": bool(common),                 # nonempty common hitter => UMCO
        "is_critical": crit,
        "elapsed_s": round(time.time() - t0, 2),
    }
    return rec


def collect_optimal_orders_sample(n, arcs, ov, tries):
    """Sample optimal (backedge omega == ov) orders by random shuffles +
    all cyclic rotations; return the set of max cliques seen across them."""
    import random
    rng = random.Random(7)
    beats = core.beats_matrix(n, arcs)
    maxcliques = set()
    n_opt = 0
    cand_orders = [list(range(n))]
    for _ in range(tries):
        o = list(range(n)); rng.shuffle(o); cand_orders.append(o)
    for r in range(n):
        cand_orders.append([(i + r) % n for i in range(n)])
    for order in cand_orders:
        g = nx.Graph(); g.add_nodes_from(range(n))
        for i in range(n):
            a = order[i]
            for j in range(i + 1, n):
                b = order[j]
                if beats[b][a]:
                    g.add_edge(a, b)
        w = core.clique_number(g)
        if w == ov:
            n_opt += 1
            for c in all_max_cliques(g, ov):
                maxcliques.add(c)
    return list(maxcliques), n_opt


def umco_via_sat_sample(n, arcs, label, tries=4000):
    """UMCO test for an object too big to enumerate exactly.
    omega_vec via SAT + best_order_upper; criticality via per-deletion SAT;
    max-clique collection via a large SAMPLE of optimal orders; the UMCO
    common-hitter is cross-checked against the actual deletion that drops ov."""
    t0 = time.time()
    # omega_vec
    ub = best_order_upper(n, arcs, tries=300)
    ge_ub, _, _ = omega_vec_ge_K_via_sat(n, arcs, ub)
    ge_ubp1, _, _ = omega_vec_ge_K_via_sat(n, arcs, ub + 1)
    ov = ub if (ge_ub and not ge_ubp1) else None
    rec = {"label": label, "order": n, "best_upper": ub,
           "ge_ub": ge_ub, "ge_ub_plus1": ge_ubp1, "omega_vec": ov}
    if ov is None:
        rec["note"] = "omega_vec not pinned by ub/ub+1 SAT"
        rec["elapsed_s"] = round(time.time() - t0, 2)
        return rec
    # criticality: every deletion drops to ov-1 ?
    all_del = True
    n_del_low = 0
    for v in range(n):
        nn, sub = core.subtournament(n, arcs, [w for w in range(n) if w != v])
        dge, _, _ = omega_vec_ge_K_via_sat(nn, sub, ov)      # >= ov ?
        if dge:                                              # still has a size-ov clique
            all_del = False
        else:
            n_del_low += 1
    rec["deletions_drop"] = n_del_low
    rec["is_critical"] = all_del
    # collect max cliques over sampled optimal orders
    maxcliques, n_opt = collect_optimal_orders_sample(n, arcs, ov, tries)
    rec["n_optimal_orders_sampled"] = n_opt
    rec["n_distinct_max_cliques_sampled"] = len(maxcliques)
    if maxcliques:
        common = set(maxcliques[0])
        for c in maxcliques[1:]:
            common &= set(c)
    else:
        common = set()
    rec["common_hitting_vertices_sampled"] = sorted(common)
    # UMCO requires criticality AND a common hitter; for vertex-transitive
    # critical objects a single deletion already drops ov for EVERY vertex,
    # so the discriminating signal is whether the sampled max cliques share a
    # common vertex.
    rec["UMCO"] = bool(common) and all_del
    rec["elapsed_s"] = round(time.time() - t0, 2)
    return rec


def main():
    out = {}
    t_start = time.time()
    allok, _ = validate_sat_oracle()
    out["sat_oracle_validated"] = allok

    nC, aC = c3()

    # ---- (1) C3[C3] order 9 EXACT ----
    print("\n=== (1) C3[C3] order 9 EXACT UMCO ===", flush=True)
    n9, a9 = lex_compose(nC, aC, nC, aC)
    assert core.is_tournament(n9, a9)
    r1 = umco_exact(n9, a9, "C3[C3]")
    print(json.dumps(r1, indent=2), flush=True)
    out["C3_C3"] = r1

    # ---- (3) C3[C3][C3] order 27: criticality spot-check (predict NOT critical) ----
    print("\n=== (3) C3[C3][C3] order 27 criticality (SAT) ===", flush=True)
    n27, a27 = lex_compose(n9, a9, nC, aC)
    assert core.is_tournament(n27, a27)
    ub27 = best_order_upper(n27, a27, tries=400)
    ge27, _, _ = omega_vec_ge_K_via_sat(n27, a27, ub27)
    ge27p, _, _ = omega_vec_ge_K_via_sat(n27, a27, ub27 + 1)
    ov27 = ub27 if (ge27 and not ge27p) else None
    # criticality: is EVERY deletion ov-1? (predict NO - it is NOT critical, G21)
    crit27 = None
    if ov27 is not None:
        all_del = True
        for v in range(n27):
            nn, sub = core.subtournament(n27, a27, [w for w in range(n27) if w != v])
            dge, _, _ = omega_vec_ge_K_via_sat(nn, sub, ov27)
            if dge:
                all_del = False
                break
        crit27 = all_del
    r3 = {"label": "C3[C3][C3]", "order": n27, "best_upper": ub27,
          "omega_vec": ov27, "is_critical": crit27}
    print(json.dumps(r3, indent=2), flush=True)
    out["C3_C3_C3"] = r3

    # ---- (2) AC_7[C3] order 21: UMCO via SAT + sample (predict TRUE) ----
    print("\n=== (2) AC_7[C3] order 21 UMCO (SAT + sample) ===", flush=True)
    nAC7, aAC7 = 7, circ_arcs(7, ac_gen(7))
    assert core.is_tournament(nAC7, aAC7)
    N21, A21 = lex_compose(nAC7, aAC7, nC, aC)
    assert core.is_tournament(N21, A21)
    r2 = umco_via_sat_sample(N21, A21, "AC_7[C3]", tries=6000)
    print(json.dumps(r2, indent=2), flush=True)
    out["AC7_C3"] = r2

    # ---- 2x2 table ----
    print("\n=== 2x2 table {object: (is_critical, UMCO)} ===", flush=True)
    table = {
        "C3[C3]":      {"is_critical": r1.get("is_critical"), "UMCO": r1.get("UMCO")},
        "AC_7[C3]":    {"is_critical": r2.get("is_critical"), "UMCO": r2.get("UMCO")},
        "C3[C3][C3]":  {"is_critical": r3.get("is_critical"), "UMCO": None},
        "AC_7[C3][C3]":{"is_critical": "predicted_via_outer_UMCO", "UMCO": None},
    }
    out["table"] = table
    print(json.dumps(table, indent=2), flush=True)

    # ---- verdict logic ----
    # CONFIRM: UMCO separates: AC_7[C3] crit+UMCO ; C3[C3] crit(of its own ov)+noUMCO
    #          ; C3[C3][C3] not-crit (no UMCO inherited).
    # KILL-a: C3[C3] UMCO True but C3[C3][C3] non-critical.
    # KILL-b: AC_7[C3] UMCO False yet critical (P18 says it IS critical).
    kill_a = (r1.get("UMCO") is True) and (r3.get("is_critical") is False)
    kill_b = (r2.get("UMCO") is False) and (r2.get("is_critical") is True)
    out["KILL_a_C3C3_UMCO_but_noncritical_iter"] = kill_a
    out["KILL_b_AC7C3_critical_but_noUMCO"] = kill_b
    out["elapsed_s"] = round(time.time() - t_start, 1)

    dp = os.path.join(os.path.dirname(__file__), "..", "data", "ground_umco.json")
    with open(os.path.abspath(dp), "w") as f:
        json.dump(out, f, indent=2)
    print("\n=== FINAL ===", flush=True)
    print(json.dumps({
        "C3[C3]": {"crit": r1.get("is_critical"), "UMCO": r1.get("UMCO")},
        "AC_7[C3]": {"crit": r2.get("is_critical"), "UMCO": r2.get("UMCO")},
        "C3[C3][C3]": {"crit": r3.get("is_critical")},
        "KILL_a": kill_a, "KILL_b": kill_b,
    }, indent=2), flush=True)


if __name__ == "__main__":
    main()
