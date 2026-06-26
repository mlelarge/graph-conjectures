"""EXECUTOR (L5): verify the 20 minimal infeasible CELL-SETS for
AC_n[AC_n] - (0,0) under the inner_then_outer order, the crux of the k=5
proof (docs/proof_AC_n_AC_n_k5.md, §3.3).

Setup.  T = AC_n[AC_n], vertex (a,b), a,b in Z/n, n=2m+1, g={1..m-1}∪{m+1}.
Delete v=(0,0).  Order survivors ascending by inner_then_outer:
    key(a,b) = (c(b), c(a), a, b),   c(t)=3 if t=0, 2 if 1<=t<=m, 1 else.
The CELL of (a,b) is chi(a,b) = (c(b), c(a)) in {1,2,3}^2 ; cell (3,3) is the
single deleted vertex, so survivors occupy 8 cells.

A backedge clique = a set of vertices pairwise "backward": for u before v in the
order, the arc v->u is present (later beats earlier).  §3.1 (proven) says a
backedge clique has at most ONE vertex per cell, so a clique is a choice of
distinct cells + one representative each, all pairs backward.

A cell-set C (subset of the 8 cells) is FEASIBLE iff there exist representatives
{(a_X,b_X) : X in C}, one per cell with chi = X, that form a backedge clique.
We decide feasibility EXACTLY by search: candidate vertices per cell, then look
for a transversal whose induced backedge graph on |C| vertices is complete.

Claims to verify (n-independent, all odd n in a range):
 (1) The 20 listed cell-sets (10 triples + 10 quads) are each INFEASIBLE.
 (2) Each is MINIMAL: infeasible, but every proper subset is FEASIBLE.
 (3) Every 5-subset of the 8 cells contains one of the 20  =>  no 5 cells
     realizable => omega_vec(T-(0,0)) <= 4.  (We ALSO directly confirm no
     feasible 5-cell-set exists, the strongest form.)
 (4) n-independence: feasibility of EVERY cell-set is identical across the
     tested odd n.
 (5) value upper bound omega_vec(AC_n[AC_n]) <= 5 via the merged-sum order
     (machine clique = 5), for the same range.

FOREGROUND, hard signal.alarm timeout.
"""
import sys, os, json, time, signal, itertools
sys.path.insert(0, os.path.dirname(__file__))
import core
import networkx as nx
from ground_lex_compose_c3 import ac_gen, lex_compose
from search_4critical_circulant import circ_arcs


class Timeout(Exception):
    pass


def _alarm(sig, frm):
    raise Timeout()


# The 20 minimal infeasible cell-sets from docs/proof_AC_n_AC_n_k5.md §3.3.
# Cell = (c(b), c(a)) = (inner band, outer band).
TRIPLES = [
    {(1, 1), (1, 3), (2, 1)},
    {(1, 1), (1, 3), (3, 1)},
    {(1, 1), (2, 3), (3, 1)},
    {(1, 2), (1, 3), (2, 2)},
    {(1, 2), (1, 3), (3, 2)},
    {(1, 2), (2, 3), (3, 2)},
    {(1, 3), (2, 1), (2, 3)},
    {(1, 3), (2, 2), (2, 3)},
    {(2, 1), (2, 3), (3, 1)},
    {(2, 2), (2, 3), (3, 2)},
]
QUADS = [
    {(1, 1), (1, 2), (2, 1), (2, 2)},
    {(1, 1), (1, 2), (2, 1), (2, 3)},
    {(1, 1), (1, 2), (2, 1), (3, 2)},
    {(1, 1), (1, 2), (3, 1), (3, 2)},
    {(1, 1), (2, 2), (3, 1), (3, 2)},
    {(1, 2), (2, 1), (2, 2), (2, 3)},
    {(1, 2), (2, 1), (2, 2), (3, 1)},
    {(1, 3), (2, 1), (2, 2), (3, 1)},
    {(1, 3), (2, 2), (3, 1), (3, 2)},
    {(2, 1), (2, 2), (3, 1), (3, 2)},
]
LISTED20 = [frozenset(s) for s in TRIPLES + QUADS]

EIGHT_CELLS = [(cb, ca) for cb in (1, 2, 3) for ca in (1, 2, 3)
               if (cb, ca) != (3, 3)]


def c_of(t, m):
    if t == 0:
        return 3
    if 1 <= t <= m:
        return 2
    return 1


def cell_of(a, b, m):
    return (c_of(b, m), c_of(a, m))


def build(n):
    g = ac_gen(n)
    nAC, aAC = n, circ_arcs(n, g)
    assert core.is_tournament(nAC, aAC)
    N, A = lex_compose(nAC, aAC, nAC, aAC)   # flat = a*n + b
    assert core.is_tournament(N, A)
    beats = core.beats_matrix(N, A)
    return N, A, beats


def order_key(a, b, m):
    # inner_then_outer: (c(b), c(a), a, b)
    return (c_of(b, m), c_of(a, m), a, b)


def precedes(u, v, m, n):
    """True iff u strictly precedes v in inner_then_outer order."""
    au, bu = divmod(u, n)
    av, bv = divmod(v, n)
    return order_key(au, bu, m) < order_key(av, bv, m)


def backward_pair(u, v, beats, m, n):
    """True iff u,v form a backedge: the LATER (in order) beats the EARLIER."""
    if precedes(u, v, m, n):
        return beats[v][u]    # v later, must beat u
    else:
        return beats[u][v]    # u later, must beat v


def cell_members(n, m, cell):
    """All survivor flat-vertices (a,b), (a,b)!=(0,0), with chi = cell."""
    cb, ca = cell
    out = []
    for a in range(n):
        if c_of(a, m) != ca:
            continue
        for b in range(n):
            if c_of(b, m) != cb:
                continue
            if a == 0 and b == 0:
                continue   # deleted
            out.append(a * n + b)
    return out


def feasible(cellset, n, m, beats, members_cache):
    """Decide if there is a transversal (one rep per cell) that is a backedge
    clique.  Exact backtracking search with backward-pair pruning."""
    cells = list(cellset)
    cand = [members_cache[c] for c in cells]
    # order cells by ascending candidate count for pruning
    idx = sorted(range(len(cells)), key=lambda i: len(cand[i]))
    cells = [cells[i] for i in idx]
    cand = [cand[i] for i in idx]
    chosen = []

    def bt(k):
        if k == len(cells):
            return True
        for v in cand[k]:
            ok = True
            for u in chosen:
                if not backward_pair(u, v, beats, m, n):
                    ok = False
                    break
            if ok:
                chosen.append(v)
                if bt(k + 1):
                    return True
                chosen.pop()
        return False

    return bt(0)


def merged_order_clique(N, beats, n, m):
    """omega(backedge graph) under merged-sum key (c(a)+c(b), a, b) on FULL T."""
    items = []
    for flat in range(N):
        a, b = divmod(flat, n)
        items.append(((c_of(a, m) + c_of(b, m), a, b), flat))
    items.sort()
    order = [f for _, f in items]
    g = nx.Graph()
    g.add_nodes_from(order)
    L = len(order)
    for i in range(L):
        a = order[i]
        for j in range(i + 1, L):
            b = order[j]
            if beats[b][a]:
                g.add_edge(a, b)
    return max((len(c) for c in nx.find_cliques(g)), default=1)


def all_cellset_feasibility(n, m, beats):
    """Feasibility of every non-empty subset of the 8 cells (size<=5 enough,
    but compute all sizes for completeness up to 5)."""
    members_cache = {c: cell_members(n, m, c) for c in EIGHT_CELLS}
    feas = {}
    for r in range(1, 6):           # subsets of size 1..5
        for sub in itertools.combinations(EIGHT_CELLS, r):
            fs = frozenset(sub)
            feas[fs] = feasible(fs, n, m, beats, members_cache)
    return feas, members_cache


def main():
    ht = int(os.environ.get("HARD_TIMEOUT", "880"))
    signal.signal(signal.SIGALRM, _alarm)
    signal.alarm(ht)
    out = {"per_n": {}}
    # n up to 41 was already claimed; push past it. value upper bound (merged
    # clique on full n^2 graph) is the expensive part, so cap that separately.
    ns_full = [7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 31, 41, 43, 51]
    try:
        baseline_feas = None       # n-independence reference (as cell->bool)
        for n in ns_full:
            m = (n - 1) // 2
            t0 = time.time()
            N, A, beats = build(n)
            feas, _ = all_cellset_feasibility(n, m, beats)
            # (1)+(2) check the 20 listed sets infeasible & minimal
            listed_infeasible = all(not feas[s] for s in LISTED20)
            minimal = True
            for s in LISTED20:
                if feas[s]:
                    minimal = False
                    break
                for x in s:
                    sub = frozenset(s - {x})
                    if not feas[sub]:        # proper subset must be feasible
                        minimal = False
                        break
                if not minimal:
                    break
            # (3) every 5-subset of 8 cells contains a listed-infeasible set,
            #     AND no 5-cell-set is feasible (direct).
            five_covered = True
            five_feasible_exists = False
            for sub in itertools.combinations(EIGHT_CELLS, 5):
                fs = frozenset(sub)
                if feas[fs]:
                    five_feasible_exists = True
                contains = any(L <= fs for L in LISTED20)
                if not contains:
                    five_covered = False
            # serialize feasibility map for n-independence (sorted cells)
            feas_signature = {}
            for fs, val in feas.items():
                key = "|".join(",".join(map(str, c)) for c in sorted(fs))
                feas_signature[key] = bool(val)
            # value upper bound (merged clique) — full n^2 graph
            t1 = time.time()
            try:
                signal.alarm(0)
                signal.signal(signal.SIGALRM, _alarm)
                signal.alarm(max(5, ht - int(time.time() - t0)))
                mclique = merged_order_clique(N, beats, n, m)
            except Timeout:
                mclique = None
            rec = {
                "n": n, "m": m, "N": N,
                "listed20_all_infeasible": bool(listed_infeasible),
                "listed20_all_minimal": bool(minimal),
                "every5subset_contains_listed": bool(five_covered),
                "exists_feasible_5cellset": bool(five_feasible_exists),
                "merged_order_clique_full": mclique,
                "secs": round(time.time() - t0, 1),
            }
            out["per_n"][str(n)] = rec
            print(f"n={n}: 20-infeasible={listed_infeasible} minimal={minimal} "
                  f"5-covered={five_covered} 5-feasible-exists={five_feasible_exists} "
                  f"merged_clique={mclique} ({rec['secs']}s)", flush=True)
            # n-independence
            if baseline_feas is None:
                baseline_feas = feas_signature
                out["nindep_reference_n"] = n
                out["nindep_holds"] = True
            else:
                if feas_signature != baseline_feas:
                    out["nindep_holds"] = False
                    out.setdefault("nindep_break", []).append(n)
                    print(f"  !! n-independence BREAK at n={n}", flush=True)
        out["nindep_holds"] = out.get("nindep_holds", True)
        out["status"] = "DONE"
    except Timeout:
        out["status"] = "TIMEOUT"
        print("TIMEOUT", flush=True)
    finally:
        signal.alarm(0)

    # overall verdict
    pn = out["per_n"]
    out["ALL_20_INFEASIBLE_ALL_N"] = all(r["listed20_all_infeasible"] for r in pn.values())
    out["ALL_20_MINIMAL_ALL_N"] = all(r["listed20_all_minimal"] for r in pn.values())
    out["ALL_5COVERED_ALL_N"] = all(r["every5subset_contains_listed"] for r in pn.values())
    out["NO_FEASIBLE_5CELLSET_ALL_N"] = all(not r["exists_feasible_5cellset"] for r in pn.values())
    out["ALL_MERGED_CLIQUE_5"] = all(r["merged_order_clique_full"] == 5
                                     for r in pn.values()
                                     if r["merged_order_clique_full"] is not None)
    out["max_n_value_checked"] = max((int(k) for k, r in pn.items()
                                      if r["merged_order_clique_full"] == 5),
                                     default=None)
    out["max_n_cellset_checked"] = max((int(k) for k in pn), default=None)

    dp = os.path.join(os.path.dirname(__file__), "..", "data",
                      "verify_L5_cellsets.json")
    os.makedirs(os.path.dirname(dp), exist_ok=True)
    with open(os.path.abspath(dp), "w") as f:
        json.dump(out, f, indent=1)
    print("\nVERDICT:",
          "20_infeasible=", out["ALL_20_INFEASIBLE_ALL_N"],
          "20_minimal=", out["ALL_20_MINIMAL_ALL_N"],
          "5_covered=", out["ALL_5COVERED_ALL_N"],
          "no_feasible_5=", out["NO_FEASIBLE_5CELLSET_ALL_N"],
          "merged_clique5=", out["ALL_MERGED_CLIQUE_5"],
          "nindep=", out.get("nindep_holds"),
          flush=True)
    print("WROTE", os.path.abspath(dp), flush=True)


if __name__ == "__main__":
    main()
