"""Certificate-extraction for the open_crux deletion lemma omega_vec(AC_n[C3]-v) <= 3.

For each odd n in {7,9,11}, build D_n := AC_n[C3] - (0,0), call the no-K4 SAT
betweenness oracle, decode the SAT model into an explicit total order whose
backedge graph is K4-free, INDEPENDENTLY re-verify backedge clique == 3 via
networkx, then tabulate the positional rule rank -> (t,h) and test whether a
single n-uniform residue-coupled rule is readable.
"""
import sys, os, json, time, itertools
sys.path.insert(0, os.path.dirname(__file__))
import core
import networkx as nx
from pysat.solvers import Cadical153
from search_4critical_circulant import build_cnf_no_kclique, circ_arcs


def ac_gen(n):
    assert n % 2 == 1
    m = (n - 1) // 2
    return set(range(1, m)) | {m + 1}


def c3():
    return 3, [(0, 1), (1, 2), (2, 0)]


def lex_compose(nT, arcsT, nH, arcsH):
    """T[H]: vertex (a,b) -> flat index a*nH + b. Returns (n, arcs, flat->(a,b))."""
    bT = core.beats_matrix(nT, arcsT)
    bH = core.beats_matrix(nH, arcsH)
    n = nT * nH
    arcs = []
    def idx(a, b):
        return a * nH + b
    coord = {}
    for a in range(nT):
        for b in range(nH):
            coord[idx(a, b)] = (a, b)
    for a in range(nT):
        for b in range(nH):
            for ap in range(nT):
                for bp in range(nH):
                    if a == ap and b == bp:
                        continue
                    if bT[a][ap] or (a == ap and bH[b][bp]):
                        arcs.append((idx(a, b), idx(ap, bp)))
    return n, arcs, coord


def delete_vertex(n, arcs, v, coord):
    """Remove vertex v; relabel remaining 0..n-2; return (n', arcs', newidx->coord)."""
    remaining = [u for u in range(n) if u != v]
    relabel = {old: new for new, old in enumerate(remaining)}
    arcs2 = [(relabel[a], relabel[b]) for (a, b) in arcs if a != v and b != v]
    coord2 = {relabel[old]: coord[old] for old in remaining}
    return n - 1, arcs2, coord2


def decode_order_from_model(n, model_set):
    """The SAT vars: lit(u,v)>0 true means u < v (u before v). Reconstruct the
    relation u<v for all pairs from the model, then total-order by #predecessors.
    We rebuild lit mapping exactly as build_cnf_no_kclique does."""
    # Re-create the same idx map deterministically (same loop order).
    idx = {}
    nv = 0
    def lit(u, v):
        nonlocal nv
        if (u, v) in idx:
            return idx[(u, v)]
        if (v, u) in idx:
            return -idx[(v, u)]
        nv += 1
        idx[(u, v)] = nv
        return nv
    for u in range(n):
        for v in range(u + 1, n):
            lit(u, v)
    # before[u][v] = True iff u precedes v
    less = [[False] * n for _ in range(n)]
    for u in range(n):
        for v in range(n):
            if u == v:
                continue
            l = lit(u, v)
            val = (l in model_set) if l > 0 else ((-l) not in model_set)
            less[u][v] = val
    # rank = number of vertices this one precedes? Order ascending: a vertex
    # that precedes many others is "early" => fewer predecessors. Count predecessors.
    preds = [sum(1 for v in range(n) if v != u and less[v][u]) for u in range(n)]
    order = sorted(range(n), key=lambda u: preds[u])
    # sanity: preds should be a permutation of 0..n-1 if it's a strict total order
    return order, preds


def main():
    out = {"results": [], "uniform_analysis": {}}
    rules = {}
    for n in (7, 9, 11):
        m = (n - 1) // 2
        g = ac_gen(n)
        nAC, aAC = n, circ_arcs(n, g)
        nC, aC = c3()
        N, A, coord = lex_compose(nAC, aAC, nC, aC)
        assert core.is_tournament(N, A), f"AC_{n}[C3] not a tournament"
        # delete v=(0,0) flat index 0
        v = 0
        Nd, Ad, coordd = delete_vertex(N, A, v, coord)
        assert core.is_tournament(Nd, Ad), "deletion not a tournament"

        # ---- no-K4 SAT (omega_vec <= 3 certificate) ----
        cnf, nclq = build_cnf_no_kclique(Nd, Ad, 4)
        t0 = time.time()
        with Cadical153(bootstrap_with=cnf.clauses) as solver:
            sat = solver.solve()
            model = solver.get_model() if sat else None
        dt = time.time() - t0

        rec = {"n": n, "order": N, "Nd": Nd, "nclauses": len(cnf.clauses),
               "no_K4_SAT": bool(sat), "sat_time_s": round(dt, 4)}

        if not sat:
            # KILL branch (a): UNSAT => omega_vec >= 4, contradicts framing
            rec["KILL_unsat"] = True
            out["results"].append(rec)
            print(f"n={n}: no-K4 UNSAT (KILL) time={dt:.4f}s", flush=True)
            continue

        # also confirm omega_vec(D_n) == 3 exactly: no-K3 must be UNSAT
        cnf3, _ = build_cnf_no_kclique(Nd, Ad, 3)
        with Cadical153(bootstrap_with=cnf3.clauses) as s3:
            sat3 = s3.solve()
        rec["no_K3_SAT"] = bool(sat3)  # expect False => omega_vec >= 3
        rec["omega_vec_eq_3"] = (sat and not sat3)

        # ---- decode order ----
        model_set = set(x for x in model if x > 0)
        order, preds = decode_order_from_model(Nd, model_set)
        is_perm = sorted(preds) == list(range(Nd))
        rec["preds_is_permutation"] = is_perm

        # ---- INDEPENDENT re-verification of backedge clique via networkx ----
        bclique = core.omega_of_order(Nd, Ad, order)
        rec["backedge_clique_decoded_order"] = bclique
        # also build the graph and run find_cliques directly as a 2nd check
        beats = core.beats_matrix(Nd, Ad)
        G = nx.Graph()
        G.add_nodes_from(range(Nd))
        pos = {u: i for i, u in enumerate(order)}
        for u in range(Nd):
            for w in range(u + 1, Nd):
                a, b = (u, w) if pos[u] < pos[w] else (w, u)
                # edge iff later beats earlier (backward arc)
                if beats[b][a]:
                    G.add_edge(u, w)
        nx_clique = max((len(c) for c in nx.find_cliques(G)), default=0)
        rec["backedge_clique_networkx"] = nx_clique
        rec["clique_exactly_3"] = (bclique == 3 and nx_clique == 3)

        # ---- positional rule: rank -> (t,h) ----
        # order[i] is the vertex at rank i. Map to coordinate.
        rank_to_coord = [coordd[order[i]] for i in range(Nd)]
        rec["rank_to_coord"] = rank_to_coord
        # within-block h-ordering: for each block t, the ranks of its h-members
        block_h_order = {}
        for i, (t, h) in enumerate(rank_to_coord):
            block_h_order.setdefault(t, []).append((i, h))
        # for each t, sort by rank and record h sequence
        h_seq = {t: [h for (i, h) in sorted(v)] for t, v in block_h_order.items()}
        rec["within_block_h_sequence_by_t"] = {str(t): seq for t, seq in h_seq.items()}
        rules[n] = {"rank_to_coord": rank_to_coord, "h_seq": h_seq, "m": m}

        out["results"].append(rec)
        print(f"n={n}: SAT={sat} time={dt:.4f}s nclq={nclq} ov==3:{rec['omega_vec_eq_3']} "
              f"backedge_clique decoded={bclique} nx={nx_clique}", flush=True)

    # ---- uniformity / residue-coupling analysis ----
    if all(n in rules for n in (7, 9, 11)):
        # (A) does within-block h-order depend on residue t, not just t-class?
        # classes: t=0, t in [1,m], t in [m+1,2m] (the template's 3 classes).
        analysis = {}
        for n in (7, 9, 11):
            m = rules[n]["m"]
            h_seq = rules[n]["h_seq"]
            def cls(t):
                if t == 0: return "c0"
                if 1 <= t <= m: return "c1"
                return "c2"
            # group blocks by class; within a class, are all h-sequences identical?
            byclass = {}
            for t, seq in h_seq.items():
                byclass.setdefault(cls(t), {})[t] = tuple(seq)
            class_uniform = {}
            distinct_within_class = {}
            for c, d in byclass.items():
                seqs = set(d.values())
                class_uniform[c] = (len(seqs) == 1)
                distinct_within_class[c] = sorted([list(s) for s in seqs])
            analysis[n] = {
                "class_h_order_uniform": class_uniform,
                "distinct_h_seqs_within_class": distinct_within_class,
            }
        out["uniform_analysis"]["per_n"] = analysis
        # the prediction's key test: within-block h-order depends on residue t
        # (NOT merely its class) <=> some class has >1 distinct h-sequence.
        residue_coupled = {}
        for n in (7, 9, 11):
            cu = analysis[n]["class_h_order_uniform"]
            residue_coupled[n] = any(not v for v in cu.values())
        out["uniform_analysis"]["residue_coupled_within_block"] = residue_coupled

    dp = os.path.join(os.path.dirname(__file__), "..", "data", "extract_deletion_order.json")
    with open(dp, "w") as f:
        json.dump(out, f, indent=1)
    print("\n=== SUMMARY ===", flush=True)
    for r in out["results"]:
        print(json.dumps({k: r[k] for k in r if k not in ("order", "rank_to_coord",
              "within_block_h_sequence_by_t")}), flush=True)
    print("uniform_analysis:", json.dumps(out.get("uniform_analysis", {}), indent=1), flush=True)
    print("saved", dp, flush=True)


if __name__ == "__main__":
    main()
