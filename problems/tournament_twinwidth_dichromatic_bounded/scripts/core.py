"""Core exact invariants for arXiv:2310.04265 (Aboulker, Aubian, Charbit, Lopes,
"Clique number of tournaments"), Conjecture 3.12.

Objects are *tournaments*: for every ordered pair {u,v} exactly one of u->v, v->u.
A tournament on n vertices is represented as (n, arcs) with arcs a list of (u, v),
vertices 0..n-1.  (We re-use the repo's exact dichromatic-number solver.)

Three invariants, ALL exact (no heuristics):

  (1) chiVec(T)   -- dichromatic number = least k s.t. V partitions into k acyclic
                     sets.  Re-uses engine/lib/digraph_core (SAT + lazy cycle).

  (2) omegaVec(T) -- the paper's "clique number of a tournament":
                     omegaVec(T) = min over all vertex orderings prec of
                     omega( backedge-graph T^prec ), where T^prec is the UNDIRECTED
                     graph with edge {u,v} iff the arc between u and v goes BACKWARD
                     w.r.t. prec (i.e. from the later vertex to the earlier one).
                     omega(.) is the ordinary (undirected) clique number.
                     Computed by brute-force minimisation over all n! orderings
                     (exact; fine for n <= ~10-11).  A faster exact branch-and-bound
                     prunes orderings whose partial backedge clique already exceeds
                     the best full value found.

  (3) tww(T)      -- twin-width of the tournament's arc-relation, via exact
                     contraction-sequence search (finite combinatorial minimisation).
                     Re-uses the standard red-graph / error-degree definition on the
                     2-coloured (black=arc-agree, red=disagree) trigraph.

Sound ground truth: every reported value is the true optimum.
"""
from __future__ import annotations

import itertools
import os
import sys
from functools import lru_cache

# Re-use the repo's verified exact dichromatic-number solver (path relative to
# this file so the module imports from a fresh clone in any location).
sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "engine", "lib"))
import digraph_core as _dc  # noqa: E402

import networkx as nx  # noqa: E402


# --------------------------------------------------------------------------- #
#  Structure checks
# --------------------------------------------------------------------------- #

def is_tournament(n, arcs):
    """True iff (n, arcs) is a tournament: exactly one arc per unordered pair,
    no loops, no 2-cycles."""
    seen = set()
    for (u, v) in arcs:
        if u == v:
            return False
        key = frozenset((u, v))
        if key in seen:
            return False
        seen.add(key)
    return len(seen) == n * (n - 1) // 2


def _adj(n, arcs):
    """Boolean arc matrix: A[u][v] True iff u->v."""
    A = [[False] * n for _ in range(n)]
    for (u, v) in arcs:
        A[u][v] = True
    return A


# --------------------------------------------------------------------------- #
#  (1) Dichromatic number  (exact, re-used)
# --------------------------------------------------------------------------- #

def chi_vec(n, arcs, ub=None):
    """Dichromatic number chiVec(T); EXACT when ub is None.

    Delegates to the shared solver: with ub=k returns the exact value if
    chiVec <= k, else the sentinel k+1 (">k"), per dichromatic_number's contract.
    """
    return _dc.dichromatic_number(n, arcs, ub=ub)


def is_k_dicolourable(n, arcs, k):
    return _dc.is_k_dicolourable(n, arcs, k)


# --------------------------------------------------------------------------- #
#  (2) omegaVec : min over orderings of the backedge clique number
# --------------------------------------------------------------------------- #
#
#  Given an ordering pi = (v_0, v_1, ..., v_{n-1}) (position(v_i) = i), the
#  backedge graph has an undirected edge {u, w} iff the tournament arc between
#  them points from the LATER vertex to the EARLIER vertex (a "back arc").
#  omegaVec = min_pi omega(backedge graph of pi).

def _backedge_clique_for_order(n, A, order):
    """omega of the backedge graph induced by `order` (a list = the ordering;
    order[i] is the vertex in position i)."""
    pos = [0] * n
    for i, v in enumerate(order):
        pos[v] = i
    # back edge {u,w}: the arc points from the later-positioned to the earlier.
    g = nx.Graph()
    g.add_nodes_from(range(n))
    for i in range(n):
        for j in range(i + 1, n):
            u, w = order[i], order[j]   # u earlier, w later
            # arc from later (w) to earlier (u) ?
            if A[w][u]:
                g.add_edge(u, w)
    return _clique_number(g)


def _clique_number(g):
    if g.number_of_edges() == 0:
        return 1 if g.number_of_nodes() > 0 else 0
    return nx.graph_clique_number(g) if hasattr(nx, "graph_clique_number") \
        else max((len(c) for c in nx.find_cliques(g)), default=1)


def omega_vec_bruteforce(n, arcs):
    """Exact omegaVec by full enumeration of all n! orderings.  Small n only."""
    if n == 0:
        return 0
    A = _adj(n, arcs)
    best = n
    for order in itertools.permutations(range(n)):
        w = _backedge_clique_for_order(n, A, list(order))
        if w < best:
            best = w
            if best == 1:
                break
    return best


def _greedy_order_ub(n, A, rng_seed=0, restarts=40):
    """A heuristic ordering minimising the backedge clique number, used to SEED the
    branch-and-bound with a tight upper bound.  At each step greedily appends the
    vertex that keeps the running backedge clique number smallest (ties broken by
    fewer back arcs, then randomly), with several random restarts."""
    import random
    rng = random.Random(rng_seed)
    best = n
    for r in range(restarts):
        placed = []
        placed_set = [False] * n
        g = nx.Graph(); g.add_nodes_from(range(n))
        cur_clique = 0
        for _step in range(n):
            cands = [w for w in range(n) if not placed_set[w]]
            rng.shuffle(cands)
            best_w, best_key = None, None
            for w in cands:
                ne = [(w, p) for p in placed if A[w][p]]
                g.add_edges_from(ne)
                cq = _clique_number(g)
                key = (cq, len(ne))
                g.remove_edges_from(ne)
                if best_key is None or key < best_key:
                    best_key, best_w = key, w
            w = best_w
            ne = [(w, p) for p in placed if A[w][p]]
            g.add_edges_from(ne)
            placed.append(w); placed_set[w] = True
            cur_clique = best_key[0]
        if cur_clique < best:
            best = cur_clique
    return best


def _max_clique_containing(v, adj, allowed):
    """Size of the largest clique that contains vertex v, using only vertices in
    `allowed` (a set) and the back-edge adjacency `adj` (dict v -> set).  Plain
    Bron-Kerbosch-style recursion restricted to N(v); used only on the small
    neighbourhoods that arise during the ordering DFS."""
    # candidates = back-neighbours of v already placed
    cand = adj[v] & allowed
    best = [1]

    def expand(clique_size, cands):
        if not cands:
            best[0] = max(best[0], clique_size)
            return
        if clique_size + len(cands) <= best[0]:
            return
        for u in list(cands):
            expand(clique_size + 1, cands & adj[u])

    expand(1, cand)
    return best[0]


def _exists_order_within(n, A, target):
    """True iff some vertex ordering has backedge clique number <= target.

    DFS building the ordering position by position.  The back-edge graph is kept
    incrementally as adjacency sets.  When a vertex w is appended, ANY new clique
    must contain w, so it suffices to check the largest clique through w (within
    its back-neighbourhood); if that exceeds `target`, prune (clique number only
    grows).  Early-exits on the first witness."""
    placed_set = [False] * n
    adj = {v: set() for v in range(n)}    # back-edge adjacency among placed verts
    found = [False]
    n_placed = [0]

    def rec():
        if found[0]:
            return
        if n_placed[0] == n:
            found[0] = True
            return
        cands = [w for w in range(n) if not placed_set[w]]
        placed = [p for p in range(n) if placed_set[p]]
        cands.sort(key=lambda w: sum(1 for p in placed if A[w][p]))
        placed_now = set(placed)
        for w in cands:
            back = {p for p in placed_now if A[w][p]}   # back arcs w->p
            for p in back:
                adj[w].add(p)
                adj[p].add(w)
            placed_set[w] = True
            n_placed[0] += 1
            # new clique through w must lie in w + its back-neighbours
            cl = _max_clique_containing(w, adj, placed_now | {w}) if back else 1
            if cl <= target:
                rec()
            # undo
            n_placed[0] -= 1
            placed_set[w] = False
            for p in back:
                adj[w].discard(p)
                adj[p].discard(w)
            if found[0]:
                return

    rec()
    return found[0]


def omega_vec(n, arcs, verbose=False):
    """Exact omegaVec via iterative-deepening branch-and-bound over orderings.

    Start from a greedy upper bound U.  Decrement the target while a witness
    ordering still exists: omegaVec = the smallest t for which SOME ordering has
    backedge clique number <= t.  Each `_exists_order_within` call is exact (no
    heuristics): it either finds a witness or PROVES none exists by exhaustion
    with the clique-growth prune.  Small n only (<= ~12).
    """
    if n == 0:
        return 0
    if n == 1:
        return 1
    A = _adj(n, arcs)

    ub = min(omega_vec_quick_ub(n, A), _greedy_order_ub(n, A))
    # Lower the answer as long as a strictly smaller target is still achievable.
    ans = ub
    while ans > 1:
        if _exists_order_within(n, A, ans - 1):
            ans -= 1
            if verbose:
                print(f"  omega_vec: ordering with clique <= {ans} exists")
        else:
            break
    return ans


def omega_vec_quick_ub(n, A):
    """A cheap upper bound on omegaVec from a single greedy ordering: place the
    vertices in an order minimising created back arcs greedily (here just the
    identity order's backedge clique)."""
    g = nx.Graph()
    g.add_nodes_from(range(n))
    order = list(range(n))
    pos = {v: i for i, v in enumerate(order)}
    for i in range(n):
        for j in range(i + 1, n):
            u, w = order[i], order[j]
            if A[w][u]:
                g.add_edge(u, w)
    return _clique_number(g)


# --------------------------------------------------------------------------- #
#  (3) Twin-width via exact contraction-sequence search
# --------------------------------------------------------------------------- #
#
#  Trigraph model on the arc relation.  Start: for each ordered pair (u,v) the
#  "colour" is BLACK if the relation agrees with the original tournament and RED
#  if it is uncertain.  We contract pairs of (super)vertices; two super-vertices
#  x,y get a RED edge to a third z iff x and z, resp. y and z, do not have the
#  SAME relation (both-arc-directions considered).  twin-width = min over
#  contraction orders of the max red degree ever seen.
#
#  For a tournament the relevant relation between two parts is the pair of
#  directions.  We model each unordered pair {x,y} with a colour in:
#     state(x,y) in { '->', '<-', 'red' }
#  Contraction of (a,b) into a: for every other part z, the merged colour is
#     - the common colour of (a,z) and (b,z) if they are EQUAL and not red
#     - red otherwise
#  red degree of a part = number of z with state red.  twin-width = min over all
#  contraction sequences of the maximum red degree encountered.

def tww(n, arcs, ub=None):
    """Exact twin-width of the tournament via DFS contraction search with
    branch-and-bound.

    Trigraph model.  The relation between two (super)vertices x and z is stored
    DIRECTED, in a dict `rel[(x, z)]` with rel[(x,z)] = rel[(z,x)]'s mirror:
        0  -> x dominates z (every original arc between the parts goes x->z)
        1  -> z dominates x
        2  -> RED (mixed / uncertain)
    Storing it directed (relative to each endpoint) is essential: a tournament's
    cyclic structure (e.g. C3) cannot be encoded by an undirected "which way"
    colour keyed on (min,max), which would spuriously merge cyclically-related
    parts.  Merging parts a,b toward z: red unless rel[(a,z)] == rel[(b,z)] and
    neither is red.  red degree of a part = number of z with rel == red.
    twin-width = min over contraction sequences of the max red degree ever seen.

    Exponential in general; intended for n <= ~9.  EXACT when ub is None; with
    ub=k the search is capped at k, so the return is the exact twin-width when
    tww <= k but is CLAMPED to k when tww > k (NOT the exact value).  A caller
    using ub as a "<= k" filter must read a return of k as "tww >= k", not as an
    exact value."""
    if n <= 2:
        return 0
    A = _adj(n, arcs)

    best = [ub if ub is not None else n]

    def initial():
        rel = {}
        for i in range(n):
            for j in range(n):
                if i == j:
                    continue
                rel[(i, j)] = 0 if A[i][j] else 1   # 0: i->j, 1: j->i
        parts = {i: frozenset([i]) for i in range(n)}
        return parts, rel

    def red_degree(rel, part_ids, x):
        d = 0
        for y in part_ids:
            if y == x:
                continue
            if rel.get((x, y), 2) == 2:
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
                new_parts = dict(parts)
                new_parts[a] = parts[a] | parts[b]
                del new_parts[b]
                others = [z for z in new_parts if z != a]
                for z in others:
                    ra = rel.get((a, z), 2)
                    rb = rel.get((b, z), 2)
                    nc = ra if (ra == rb and ra != 2) else 2
                    new_rel[(a, z)] = nc
                    # mirror toward z (directed): z->a is the mirror of a->z
                    new_rel[(z, a)] = (1 - nc) if nc != 2 else 2
                # drop all keys mentioning b
                for k in list(new_rel):
                    if b in k:
                        del new_rel[k]
                part_ids = list(new_parts)
                m = 0
                for x in part_ids:
                    dx = red_degree(new_rel, part_ids, x)
                    if dx > m:
                        m = dx
                local_max = max(cur_max, m)
                if local_max < best[0]:
                    search(new_parts, new_rel, local_max)

    parts, rel = initial()
    search(parts, rel, 0)
    return best[0]
