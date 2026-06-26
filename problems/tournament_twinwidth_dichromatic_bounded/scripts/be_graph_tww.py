"""Twin-width of the UNDIRECTED back-edge graph of BST-orderings (bridge lemma test).

Proposal under test (literature-reduction, D-round): the undirected back-edge graph
T^prec of ANY BST-ordering prec of a tww(T)<=1 tournament has BOUNDED undirected
twin-width.  This is the unverified bridge needed to invoke Bourneuf-Thomasse
(bounded-tww => polynomially chi-bounded) on top of Thm 3.3 + Geniet-Thomasse
Thm 3.15 in the tww=1 case of Conj 3.12.

Falsifiable prediction:
  CONFIRM: for every BST-order prec of every tww<=1 tournament (n<=8), the undirected
           back-edge graph has undirected twin-width <= 2 (small constant = f(1)).
  KILL:    some tww<=1 tournament has a BST-order whose back-edge undirected graph
           has undirected twin-width >= 3 (growing with n).

We compute the EXACT undirected twin-width by the same red-degree contraction search
used in core.tww, but on an UNDIRECTED trigraph (edge / non-edge / red).

This is a MEASUREMENT, not a proof of the asymptotic conjecture (discipline_gate
empirical_not_proof).  It only grounds the bridge lemma's CONFIRM/KILL prediction.
"""
from __future__ import annotations

import json
import subprocess
import sys

import core
import constructions as C
from bst_penalty import _bst_orders_subset
import h8_closure_membership as H8


# --------------------------------------------------------------------------- #
#  Undirected twin-width (exact contraction search)
# --------------------------------------------------------------------------- #
#
#  Undirected trigraph model.  state(x,y) in {0:non-edge, 1:edge, 2:red}.
#  Start from a simple undirected graph (no red).  Merge a,b -> a: for every
#  other part z, merged colour = common colour of (a,z),(b,z) if equal & not red,
#  else red.  red degree of part = #z with red.  twin-width = min over contraction
#  orders of max red degree ever seen.  (Symmetric, so we store unordered keys.)

def undirected_tww(n, edges, ub=None):
    """Exact undirected twin-width of the graph on vertices 0..n-1 with edge set
    `edges` (iterable of unordered pairs).  Returns the true minimum."""
    if n <= 2:
        return 0
    E = set()
    for (u, v) in edges:
        if u == v:
            continue
        E.add((u, v) if u < v else (v, u))

    best = [ub if ub is not None else n]

    def key(a, b):
        return (a, b) if a < b else (b, a)

    def initial():
        rel = {}
        for i in range(n):
            for j in range(i + 1, n):
                rel[(i, j)] = 1 if (i, j) in E else 0   # 1 edge, 0 non-edge
        parts = set(range(n))
        return parts, rel

    def red_degree(rel, parts, x):
        d = 0
        for y in parts:
            if y == x:
                continue
            if rel.get(key(x, y), 2) == 2:
                d += 1
        return d

    def search(parts, rel, cur_max):
        if cur_max >= best[0]:
            return
        ids = sorted(parts)
        if len(ids) <= 2:
            best[0] = min(best[0], cur_max)
            return
        for ai in range(len(ids)):
            for bi in range(ai + 1, len(ids)):
                a, b = ids[ai], ids[bi]
                new_rel = dict(rel)
                new_parts = set(parts)
                new_parts.discard(b)              # merge b into a
                for z in new_parts:
                    if z == a:
                        continue
                    ra = rel.get(key(a, z), 2)
                    rb = rel.get(key(b, z), 2)
                    nc = ra if (ra == rb and ra != 2) else 2
                    new_rel[key(a, z)] = nc
                for kk in list(new_rel):
                    if b in kk:
                        del new_rel[kk]
                m = 0
                for x in new_parts:
                    dx = red_degree(new_rel, new_parts, x)
                    if dx > m:
                        m = dx
                local_max = max(cur_max, m)
                if local_max < best[0]:
                    search(new_parts, new_rel, local_max)

    parts, rel = initial()
    search(parts, rel, 0)
    return best[0]


# --------------------------------------------------------------------------- #
#  Back-edge undirected graph of an ordering
# --------------------------------------------------------------------------- #

def backedge_undirected_edges(n, A, order):
    """Undirected back-edge edge set for `order`: edge {u,w} iff the arc between
    them is BACKWARD in `order` (points from the later vertex to the earlier one).
    Same convention as core._backedge_clique_for_order."""
    edges = []
    for i in range(n):
        for j in range(i + 1, n):
            u, w = order[i], order[j]   # u earlier, w later
            if A[w][u]:                 # arc later->earlier == back edge
                edges.append((u, w))
    return edges


def bst_backedge_tww_max(n, arcs):
    """MAX over distinct BST-order back-edge undirected graphs of undirected_tww,
    plus the number of distinct back-edge graphs and the per-graph distribution."""
    A = core._adj(n, arcs)
    full = tuple(range(n))
    seen = set()
    max_tww = 0
    hist = {}
    n_orders = 0
    for order in _bst_orders_subset(A, full):
        n_orders += 1
        edges = backedge_undirected_edges(n, A, list(order))
        fe = frozenset(edges)
        if fe in seen:
            continue
        seen.add(fe)
        t = undirected_tww(n, edges)
        hist[t] = hist.get(t, 0) + 1
        if t > max_tww:
            max_tww = t
    return {"max_bst_be_tww": max_tww, "n_distinct_be_graphs": len(seen),
            "n_bst_orders": n_orders, "be_tww_hist": hist}


def free_backedge_tww_among_omega_optimal(n, arcs):
    """For grounding the anchor: max undirected_tww over back-edge graphs of
    omega-OPTIMAL FREE orderings (all orderings achieving omegaVec).  Small n only.
    Returns max and the omegaVec value."""
    import itertools
    A = core._adj(n, arcs)
    ov = core.omega_vec(n, arcs)
    max_tww = 0
    for order in itertools.permutations(range(n)):
        if core._backedge_clique_for_order(n, A, list(order)) == ov:
            edges = backedge_undirected_edges(n, A, list(order))
            t = undirected_tww(n, edges)
            if t > max_tww:
                max_tww = t
    return {"omega_vec": ov, "max_free_omegaopt_be_tww": max_tww}


# --------------------------------------------------------------------------- #
#  gentourng helpers
# --------------------------------------------------------------------------- #

def _parse_gentourng_line(n, line):
    s = line.strip()
    bits = [c for c in s if c in "01"]
    if len(bits) != n * (n - 1) // 2:
        return None
    arcs = []
    idx = 0
    for i in range(n):
        for j in range(i + 1, n):
            arcs.append((i, j) if bits[idx] == "1" else (j, i))
            idx += 1
    return arcs


def scan(n):
    """Over all tww<=1 tournaments on n vertices (gentourng), compute the MAX over
    distinct BST-order back-edge graphs of undirected twin-width.  Split by
    closure membership.  Decisive number: global max of bst-be-tww."""
    proc = subprocess.run(["gentourng", "-q", str(n)],
                          capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"gentourng failed: {proc.stderr}")
    n_total = 0
    n_tww1 = 0
    global_max = 0
    argmax = None
    hist_in = {}      # max-bst-be-tww histogram, closure-IN members
    hist_out = {}     # closure-OUTSIDE members
    for line in proc.stdout.splitlines():
        arcs = _parse_gentourng_line(n, line)
        if arcs is None:
            continue
        n_total += 1
        if core.tww(n, arcs, ub=2) > 1:     # cap search: only need tww<=1 filter
            continue
        # re-confirm exact tww<=1 (ub=2 search returns exact value if <2)
        t_dir = core.tww(n, arcs)
        if t_dir > 1:
            continue
        n_tww1 += 1
        info = bst_backedge_tww_max(n, arcs)
        mx = info["max_bst_be_tww"]
        inside = H8.in_closure(n, arcs)
        h = hist_in if inside else hist_out
        h[mx] = h.get(mx, 0) + 1
        if mx > global_max:
            global_max = mx
            argmax = {"arcs": arcs, "in_closure": inside, **info}
    return {"n": n, "n_total": n_total, "n_tww1": n_tww1,
            "global_max_bst_be_tww": global_max,
            "hist_in_closure": hist_in, "hist_outside_closure": hist_out,
            "argmax": argmax}


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "anchor"
    if cmd == "anchor":
        # S_3 anchor: tww, omegaVec, max BST back-edge-graph tww, free omega-opt tww
        n, a = C.S(3)
        out = {"S_3": {"n": n, "tww": core.tww(n, a),
                       **bst_backedge_tww_max(n, a),
                       **free_backedge_tww_among_omega_optimal(n, a)}}
        print(json.dumps(out, indent=2, default=str))
    elif cmd == "scan":
        lo = int(sys.argv[2])
        hi = int(sys.argv[3]) if len(sys.argv) > 3 else lo
        res = {}
        for n in range(lo, hi + 1):
            res[n] = scan(n)
            print(json.dumps({n: res[n]}, indent=2, default=str), flush=True)
        print("=== SUMMARY ===")
        print(json.dumps({n: {"global_max_bst_be_tww": res[n]["global_max_bst_be_tww"],
                              "n_tww1": res[n]["n_tww1"]} for n in res},
                         indent=2, default=str))
    else:
        print("usage: be_graph_tww.py [anchor | scan LO [HI]]")
