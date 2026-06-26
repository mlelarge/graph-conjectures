"""branch1_no_admissible_search.py -- CONSTRUCT-OR-EMPTY for the O2b*
residue branch (1) ("no admissible rho-tail w").

GOAL.  Branch (1) of the four-branch O2b* residue
(docs/O2B_PRESCRIBED_BRANCHING_2026_06_11.md): a strictly rho-headless
HARD gateway in which EVERY w in R\\{v} fails T2-admissibility.  The three
T2-admissibility clauses (Theorem T2 hypothesis) for a candidate absorbed
rho-tail w are:

    (A) v-placement:   v notin X*_w        (FAILS if v in X*_w)
    (B) size bound:    |X*_w| <= n-2       (FAILS if |X*_w| >= n-1)
    (C) head-escape:   some escaped AV_u-head z0 notin X*_w
                       (FAILS if every escaped head is trapped in X*_w)

Here X*_w = cage(C_u) | {w} | trapped(w), exactly the set computed by
relay_free_witness.py: trapped(w) = vertices that cannot reach rho after
deleting C_u | {w} (a node deletion in D^bullet).

DESIGN LEVER (realized).  Make v = head(a) ITSELF a rho-tail (v in R) and
give exactly ONE other rho-tail w0.  Then R\\{v} = {w0} is the unique
candidate.  Wire the escaped AV_u-heads h2,h3 so their ONLY route to rho
goes through w0 (heads do NOT point to v): absorbing w0 then TRAPS both
heads, so clause (C) FAILS and w0 is non-admissible -- branch (1)
existence.  Multiplicity d^-(rho)=3 is restored by giving w0 two rho-arcs
(in the host: w0->p and w0->q), keeping lambda(D^bullet)>=3.

HOST (n=12; vertices 0..11):
  V1 = {p=0, q=1, u=2}, chord p->q; u = an I-vertex (strictly rho-headless).
  V2 (semicomplete) = cage {3,4,5} + v=6 + heads {h2=7,h3=8}
                      + w0=9 + fillers {f1=10,f2=11}.
  Contraction rho=0: D^bullet vertices rho=0,u=1,cage=2,3,4,v=5,
  h2=6,h3=7,w0=8,f1=9,f2=10.

CONFIRM (existential): an explicit host with oracle-certified
lambda(host)>=3, lambda(D^bullet)>=3, SAD(host)=SAT, a machine-verified
strictly rho-headless HARD gateway (one-exit criterion, same assertions
as the witnesses), |R|>=2, v a rho-tail, and for EVERY w in R\\{v} a named
failed admissibility clause -- all wrapped in asserts that PASS.

SIDE ARM: an exhaustive per-clause audit over R\\{v}, recording which
clause fails (here: clause C, head-escape).
"""
from __future__ import annotations

import os
import sys
from collections import Counter

_HERE = os.path.dirname(os.path.abspath(__file__))
_CODE = os.path.join(os.path.dirname(_HERE), "code")
for _p in (_CODE, _HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from check_lexist_fixedroot import (  # noqa: E402
    subtree_through,
    tree_arcs,
)

# Host vertex names.
P, Q, U = 0, 1, 2
KA, KB, KC = 3, 4, 5
V = 6                      # head(a) -- ALSO a rho-tail
H2, H3 = 7, 8             # escaped AV_u heads
W0 = 9                     # the unique OTHER rho-tail
F1, F2 = 10, 11           # filler outside-O vertices

CAGE = (KA, KB, KC)
OUTK = (V, H2, H3, W0, F1, F2)


def host_arcs():
    """Branch-1 host (simple).  v=6 is a rho-tail; w0=9 the only other.
    Escaped heads 7,8 reach rho ONLY through w0 (they do NOT point to v)."""
    import itertools

    arcs = [(P, Q)]                                          # chord
    arcs += [(x, y) for x in CAGE for y in CAGE if x != y]   # cage digons
    arcs += [(c, U) for c in CAGE]                           # cage -> u
    arcs += [(U, V), (U, H2), (U, H3)]                       # AV_u; a=(u,v)

    # everyone outside dominates the cage (sealing + semicomplete glue)
    arcs += [(x, c) for x in OUTK for c in CAGE]

    # safe outside adjacencies (NO head/filler -> v ; heads reach rho via w0):
    arcs += [(H2, W0), (H3, W0), (H2, H3), (H3, H2)]         # heads -> w0
    arcs += [(W0, V), (W0, H2), (W0, H3), (W0, F1), (W0, F2)]  # w0 dominates
    arcs += [(F1, W0), (F2, W0), (F1, F2), (F2, F1)]         # fillers -> w0
    arcs += [(V, H2), (V, H3), (V, F1), (V, F2), (V, W0)]    # v dominates rest

    # complete the V2 tournament on the remaining unordered pairs, NEVER
    # adding head/filler -> v (would give an alternate rho-route).
    existing = set(arcs)

    def adj(a, b):
        return (a, b) in existing or (b, a) in existing

    for a, b in itertools.combinations(OUTK, 2):
        if adj(a, b):
            continue
        # remaining missing pairs are among {heads}x{fillers}; orient
        # head -> filler (filler then still only escapes via w0, head still
        # cannot reach v).  Generic safe rule below.
        if b == V and a in (H2, H3, F1, F2):
            arcs.append((V, a))
        elif a == V and b in (H2, H3, F1, F2):
            arcs.append((V, b))
        else:
            arcs.append((a, b))
        existing.add(arcs[-1])

    # rho incidences via p/q split (gives the contraction multiplicities):
    #   v -> rho  (mult 1): v -> p
    #   w0 -> rho (mult 2): w0 -> p, w0 -> q     => d^-(rho)=3
    arcs += [(V, P)]
    arcs += [(W0, P), (W0, Q)]
    # rho -> outside (keep strong); rho = {p,q}
    arcs += [(P, V), (Q, W0), (P, H2), (Q, H3), (P, F1), (Q, F2)]

    # dedupe (host is simple; multiplicity lives only post-contraction)
    seen, uniq = set(), []
    for e in arcs:
        if e not in seen:
            seen.add(e)
            uniq.append(e)
    return uniq


def dbullet_arcs():
    """Contract chord p=0 -> q=1 into rho=0; relabel 2..11 -> 1..10.
    Parallel rho-arcs (w0->p, w0->q) survive as a genuine multi-arc."""
    relabel = {P: 0, Q: 0}
    relabel.update({vv: vv - 1 for vv in range(2, 12)})
    out = []
    for x, y in host_arcs():
        if (x, y) == (P, Q):
            continue
        rx, ry = relabel[x], relabel[y]
        if rx != ry:
            out.append((rx, ry))
    return out


def is_in_arb(succ, n, root):
    for start in range(n):
        if start == root:
            continue
        seen, cur = set(), start
        while cur != root:
            if cur in seen or cur not in succ:
                return False
            seen.add(cur)
            cur = succ[cur]
    return True


def x_star(graph, cage, w, n, root):
    import networkx as nx
    reduced = graph.copy()
    reduced.remove_nodes_from(cage | {w})
    trapped = {
        z for z in range(n)
        if z not in cage | {w} and z != root and not nx.has_path(reduced, z, root)
    }
    return cage | {w} | trapped


def clause_audit(graph, cage, R, v, av_heads, n, root):
    out = {}
    for w in R:
        if w == v:
            continue
        Xs = x_star(graph, cage, w, n, root)
        A_ok = v not in Xs
        B_ok = len(Xs) <= n - 2
        escaped_outside = [z for z in av_heads if z not in Xs]
        C_ok = len(escaped_outside) >= 1
        out[w] = {
            "Xstar": sorted(Xs),
            "A_ok_v_placement": A_ok,
            "B_ok_size_bound": B_ok,
            "C_ok_head_escape": C_ok,
            "escaped_heads_outside": escaped_outside,
            "admissible": A_ok and B_ok and C_ok,
            "failed_clauses": [
                name for name, ok in
                [("A_v_placement", A_ok), ("B_size_bound", B_ok),
                 ("C_head_escape", C_ok)] if not ok
            ],
        }
    return out


# --------------------------------------------------------------------------- #
#  Explicit strictly-rho-headless HARD gateway pair (one-exit criterion).
#  Mirrors the construction in rho_headless_witness.py / relay_free_witness.py:
#  X = cage, exactly one U-exit (u,h), every free exit tailed at u, no strict
#  exit (the failing/hard case).
# --------------------------------------------------------------------------- #

def build_hard_gateway(db, mult, cage, a, n, root):
    import itertools
    import networkx as nx

    u = a[0]
    struct_out = {}
    for (x, y) in mult:
        struct_out.setdefault(x, set()).add(y)

    cage_int = sorted(cage - {u})
    outside = sorted(set(range(n)) - cage - {root})

    # an in-arb of the outside-to-rho digraph (T_out)
    H = nx.DiGraph()
    H.add_nodes_from(set(outside) | {root})
    for (x, y) in set(mult):
        if x in outside and y in (set(outside) | {root}):
            H.add_edge(x, y)
    if not all(nx.has_path(H, x, root) for x in outside):
        return {"found": False, "reason": "no outside path to rho"}
    Rev = H.reverse(copy=True)
    out_succ = {}
    for par, child in nx.bfs_tree(Rev, root).edges():
        out_succ[child] = par
    if not all(x in out_succ for x in outside):
        return {"found": False, "reason": "no outside in-arb"}

    # cage routings to u
    def cage_routings():
        choices = []
        for c in cage_int:
            nb = [y for y in struct_out.get(c, ()) if y in cage]
            choices.append([(c, y) for y in nb])
        for combo in itertools.product(*choices):
            succ = dict(combo)
            succ[u] = a[1]
            ok = True
            for c in cage_int:
                seen, cur = set(), c
                while cur != u:
                    if cur in seen or cur not in succ:
                        ok = False
                        break
                    seen.add(cur)
                    cur = succ[cur]
                if not ok:
                    break
            if ok:
                yield dict(combo)

    for cage_succ in cage_routings():
        succT = dict(cage_succ)
        succT[u] = a[1]
        succT.update(out_succ)
        if not is_in_arb(succT, n, root):
            continue
        Tset = tree_arcs(succT)
        X = subtree_through(succT, u, root, n)
        if X != cage:
            continue
        gw = _search_U(mult, struct_out, Tset, X, a, n, root, u)
        if gw.get("found"):
            gw["T"] = {int(k): int(val) for k, val in succT.items()}
            gw["X"] = sorted(X)
            return gw
    return {"found": False, "reason": "no T(X=cage)+hard U"}


def _search_U(mult, struct_out, Tset, X, a, n, root, u):
    import itertools
    nonroot = [vv for vv in range(n) if vv != root]
    choice_lists = []
    total = 1
    for vv in nonroot:
        opts = sorted(struct_out.get(vv, ()))
        choice_lists.append([(vv, y) for y in opts])
        total *= max(1, len(opts))
    if total > 8_000_000:
        return {"found": False, "reason": f"U-space {total} too large"}
    for combo in itertools.product(*choice_lists):
        succU = dict(combo)
        Uset = tree_arcs(succU)
        if not all(mult[e] >= 2 for e in Tset & Uset):
            continue
        if a in Uset and mult[a] < 2:
            continue
        if not is_in_arb(succU, n, root):
            continue
        exits = [(w, z) for (w, z) in Uset if w in X and z not in X]
        if len(exits) != 1:
            continue
        free = [e for e in mult if e[0] in X and e[1] not in X
                and mult[e] - (e in Tset) - (e in Uset) >= 1]
        if not free or not all(e[0] == u for e in free):
            continue
        strict = [b for b in exits
                  if (subtree_through(succU, b[0], root, n) & X) < X]
        if strict:
            continue
        return {
            "found": True,
            "U": {int(k): int(val) for k, val in succU.items()},
            "single_exit": list(exits[0]),
            "free_exits": sorted(free),
        }
    return {"found": False, "reason": "no hard U in structural space"}


def main():
    import json
    import networkx as nx
    import oracle
    from digraph import Digraph
    from generators.near_split import is_one_zero_near_split

    host = host_arcs()
    n_host = 12
    assert len(host) == len(set(host)), "host must be simple"

    V1, V2 = [P, Q, U], list(range(3, 12))
    ok, why = is_one_zero_near_split(
        Digraph.from_arcs(range(n_host), host), V1, V2)
    print("near-split:", ok, why)
    assert ok, why

    lam_host = oracle.arc_connectivity(n_host, host)
    print("lambda(host) =", lam_host)
    assert lam_host >= 3, lam_host

    sad = oracle.check_construction(n_host, host, name="branch1-host")
    print("SAD(host) =", sad["sad"],
          "cross_check_agree =",
          (sad["cross_check"] and sad["cross_check"]["agree"]))
    assert sad["sad"] == "SAT", sad
    if sad["cross_check"] is not None:
        assert sad["cross_check"]["agree"], sad

    db = dbullet_arcs()
    n, root, u = 11, 0, 1
    mult = Counter(db)
    lam_db = oracle.arc_connectivity(n, db)
    print("lambda(D^bullet) =", lam_db)
    assert lam_db >= 3, lam_db
    assert (u, root) not in mult, "u must be strictly rho-headless (I-vertex)"

    graph = nx.MultiDiGraph()
    graph.add_nodes_from(range(n))
    graph.add_edges_from(db)
    without_u = graph.copy()
    without_u.remove_node(u)
    cage = {u} | {
        x for x in range(n)
        if x not in (root, u) and not nx.has_path(without_u, x, root)
    }
    print("cage C_u =", sorted(cage))
    assert cage == {1, 2, 3, 4}, sorted(cage)

    v = 5                                        # contracted label of host v=6
    a = (u, v)
    av_heads = sorted(z for x, z in mult if x == u and z != v)
    R = sorted({x for x, z in mult if z == root})
    print("a =", a, " v =", v, " AV_u heads =", av_heads, " R =", R,
          " rho-mults =", {r: mult[(r, root)] for r in R})
    assert v in R, "design requires v itself a rho-tail"
    assert len(R) >= 2
    rest = [w for w in R if w != v]
    print("R\\{v} =", rest)
    assert rest == [8], rest                     # unique other rho-tail w0=8

    audit = clause_audit(graph, cage, R, v, av_heads, n, root)
    print("\nT2-admissibility clause audit over R\\{v}:")
    for w, cl in audit.items():
        print(f"  w={w}: A(v-place)={cl['A_ok_v_placement']} "
              f"B(size<=n-2)={cl['B_ok_size_bound']} "
              f"C(head-escape)={cl['C_ok_head_escape']} "
              f"admissible={cl['admissible']} "
              f"failed_clauses={cl['failed_clauses']} "
              f"|X*|={len(cl['Xstar'])} X*={cl['Xstar']}")

    all_nonadmissible = all(not audit[w]["admissible"] for w in rest)
    print("\nEVERY w in R\\{v} non-admissible:", all_nonadmissible)

    hg = build_hard_gateway(db, mult, cage, a, n, root)
    print("hard gateway:", hg.get("found"),
          "" if hg.get("found") else f"({hg.get('reason')})")
    if hg.get("found"):
        print("  T =", hg["T"])
        print("  U =", hg["U"])
        print("  X =", hg["X"], " single U-exit =", hg["single_exit"],
              " free exits =", hg["free_exits"])

    # ---- branch-1 CONFIRM asserts (the falsifiable prediction) ----
    assert lam_host >= 3
    assert lam_db >= 3
    assert sad["sad"] == "SAT"
    assert (u, root) not in mult                 # strictly rho-headless
    assert v in R and len(R) >= 2
    assert all_nonadmissible, audit
    # name the failed clause for every w in R\\{v}:
    for w in rest:
        assert audit[w]["failed_clauses"], (w, audit[w])
    assert hg.get("found"), hg

    print("\n=== BRANCH-1 WITNESS CONFIRMED ===")
    print(json.dumps({
        "n": n,
        "lambda_host": lam_host,
        "lambda_dbullet": lam_db,
        "sad_host": sad["sad"],
        "u_strictly_rho_headless": (u, root) not in mult,
        "cage": sorted(cage),
        "a": list(a),
        "v_is_rho_tail": v in R,
        "R": R,
        "R_minus_v": rest,
        "per_w_failed_clause": {w: audit[w]["failed_clauses"] for w in rest},
        "hard_gateway_single_exit": hg["single_exit"],
    }, indent=2))
    print("ALL BRANCH-1 ASSERTIONS PASS -- witness exists; branch (1) is "
          "CONSTRUCTIBLE in-class (the never-binding-clause statistic for the "
          "side arm: only clause C (head-escape) fails here).")


if __name__ == "__main__":
    main()
