"""Path-decomposition-based DP for Path-FAS on tournaments.

This implements the bounded-pathwidth DP outlined in the task description
for the *interaction graph*

    J(T) = H(T) ∪ G_flex(T)

where
- H(T) is the forced-backedge graph (T-arc u->v with v's window ending
  before u's window begins, i.e. u must lie later in any LFO);
- G_flex(T) is the interval-overlap graph on flexible pairs (windows
  overlap, both directions allowed by score windows).

Crucial observation that makes a path-decomposition DP on J even
plausible: every pair {u, v} whose window relation is "flexible" is an
edge of J.  Hence two vertices with non-comparable score windows always
co-exist in some bag of any path decomposition of J.  Forgotten
vertices have NO flexible-window relation to future-introduced
vertices, so their relative LFO order is forced by the windows alone.

State at a bag B = (b_0, ..., b_w):
- `sigma`: a linear order on B representing the LFO-order restricted to
  the bag (a permutation of the bag).
- `degree`: per bag-vertex, current loaded-backedge degree in {0, 1, 2}.
- `comp`: union-find partition on bag vertices recording the
  loaded-backedge components.

Transitions (nice path decomposition):
- **Introduce v**: append v to bag B; choose σ-position for v anywhere
  in the order (subject to score-window forced inequalities to other
  bag vertices); fresh component, degree 0.  Then for every J-edge
  {v, u} with u in the bag, *load* it iff (u is later than v in σ but
  T has v->u) or (u is earlier than v in σ but T has u->v) — i.e., iff
  the arc points "backward" in σ.  Check degree ≤ 2 and acyclicity.
- **Forget v**: drop v from B, σ, degree, comp; the J-edges incident to
  v with future-introduced bag vertices DO NOT EXIST (path-decomp
  invariant), so v's loaded-degree / component never change again.

Acceptance: at the final empty bag, all vertices have been visited and
all their J-edges loaded; if any history was consistent (no cycle, no
degree>2 vertex), the tournament admits a Path-FAS.

WARNING (honest runtime). At pathwidth w, the bag-state count is at
most (w+1)! · 3^{w+1} · Bell(w+1).  For w = 8 (the empirical upper
bound on flex-graph pathwidth in this repository) that is roughly
9! · 3^9 · 21147 ≈ 1.5 · 10^14 — a constant in n but huge in absolute
terms.  This implementation is therefore primarily a CORRECTNESS
SPECIFICATION, not a practical solver.  We exercise it on n ≤ 9 only.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Dict, List, Sequence, Tuple

import networkx as nx
from networkx.algorithms.approximation import treewidth_min_fill_in

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lfo_score_window import score_windows  # noqa: E402
from path_fas import decide_path_fas_bruteforce  # noqa: E402
from score_window_forced import forced_order  # noqa: E402

Matrix = Sequence[Sequence[int]]


# ---------------------------------------------------------------------------
# 1. The interaction graph J = H ∪ G_flex.
# ---------------------------------------------------------------------------

def J_graph(T: Matrix, radius: int = 2) -> Tuple[nx.Graph, List[Tuple[int, int]], List[Tuple[int, int]], List[Tuple[int, int]]]:
    """Return (J, H_edges, flex_edges, forced_inequalities).

    `H_edges`: pairs {u, v} that contribute a forced backedge in every
        score-respecting LFO (T-arc disagrees with the score-window
        forced relative order).
    `flex_edges`: pairs {u, v} whose score-windows overlap (the LFO can
        place them in either order).
    `forced_inequalities`: list of (earlier, later) where the score
        windows are disjoint with hi_earlier < lo_later -- so any LFO
        must respect earlier < later.  Includes pairs whose T-arc agrees
        with the forced order (NOT in H) AND pairs in H.  In other
        words, the full forced partial order on V(T).
    """
    n = len(T)
    windows = score_windows(T, radius)
    H_edges: List[Tuple[int, int]] = []
    flex_edges: List[Tuple[int, int]] = []
    forced_inequalities: List[Tuple[int, int]] = []
    for u in range(n):
        for v in range(u + 1, n):
            fixed = forced_order(windows, u, v)
            if fixed is None:
                flex_edges.append((u, v))
                continue
            earlier, later = fixed
            forced_inequalities.append((earlier, later))
            # H_edge: T-arc disagrees with forced relative order
            # (so the T-arc is forced to be a backedge under the LFO).
            if T[later][earlier]:
                H_edges.append(tuple(sorted((earlier, later))))
    J = nx.Graph()
    J.add_nodes_from(range(n))
    for u, v in H_edges:
        J.add_edge(u, v)
    for u, v in flex_edges:
        J.add_edge(u, v)
    return J, H_edges, flex_edges, forced_inequalities


def is_backedge_in_LFO(T: Matrix, u: int, v: int, sigma_pos: Dict[int, int]) -> bool:
    """Return True iff the T-arc between u and v is a back-arc under LFO σ.

    Requires u != v and both u, v positioned in sigma_pos.
    """
    if T[u][v]:
        return sigma_pos[u] > sigma_pos[v]
    if T[v][u]:
        return sigma_pos[v] > sigma_pos[u]
    raise ValueError(f"no arc between {u} and {v}")


# ---------------------------------------------------------------------------
# 2. Nice path decomposition from min-fill-in treewidth heuristic.
# ---------------------------------------------------------------------------

def _vertex_ordering_path_decomp(G: nx.Graph, order: List[int]) -> List[frozenset]:
    """Convert a vertex ordering into a *valid* path decomposition.

    For an ordering π = (v_1, ..., v_n), define the "active set" at
    step i to be all vertices v_j (j ≤ i) that either equal v_i or have
    at least one neighbor v_k with k > i.  The sequence of these sets,
    indexed by i = 0, 1, ..., n (with B_0 = ∅), is a path decomposition
    because:
      (a) each vertex's appearance is contiguous (from first inclusion
          to the last edge to a later vertex);
      (b) every G-edge {v_j, v_k} (j < k) has both endpoints in B_k.

    Width of this decomposition = max_i |B_i| − 1.  This is the
    "vertex separation number" of the ordering, which is an upper bound
    on pathwidth (with equality for the optimal ordering).
    """
    n_order = len(order)
    pos = {v: i for i, v in enumerate(order)}
    # For each vertex v, last time it is "live" = max(pos[v], max pos of neighbors).
    last_live: Dict[int, int] = {}
    for v in order:
        nbrs = [pos[u] for u in G.neighbors(v) if u in pos]
        last_live[v] = max([pos[v]] + nbrs)
    bags: List[frozenset] = [frozenset()]
    active: set = set()
    for i, v in enumerate(order):
        active.add(v)
        # Drop any vertex w with last_live[w] < i.
        # (We do this AFTER adding v since v itself stays at least until pos[v].)
        bags.append(frozenset(active))
        # Now prune: any w with last_live[w] == i is finished after this bag.
        # We drop them in the next iteration's bag (so their range includes i).
        finished = [w for w in active if last_live[w] == i]
        for w in finished:
            active.discard(w)
    # Append a final empty bag.
    bags.append(frozenset())
    return bags


def _greedy_min_degree_order(G: nx.Graph) -> List[int]:
    """Greedy min-degree elimination ordering.

    Repeatedly pick the vertex of smallest current degree; record it;
    make its neighbors a clique; remove it.  The resulting order is a
    heuristic for low-width path decompositions (it underlies the
    standard `min_degree_treewidth_heuristic`).
    """
    adj: Dict[int, set] = {v: set(G.neighbors(v)) for v in G.nodes()}
    remaining = set(adj.keys())
    order: List[int] = []
    while remaining:
        v = min(remaining, key=lambda x: len(adj[x] & remaining))
        order.append(v)
        nbrs = list(adj[v] & remaining)
        for i in range(len(nbrs)):
            for j in range(i + 1, len(nbrs)):
                adj[nbrs[i]].add(nbrs[j])
                adj[nbrs[j]].add(nbrs[i])
        remaining.discard(v)
    return order


def nice_path_decomposition(G: nx.Graph) -> Tuple[List[frozenset], int]:
    """Return (nice path decomposition, width) for G.

    Strategy: build a vertex-ordering path decomposition via two
    heuristics — greedy min-degree on G and an order derived from the
    min-fill-in tree decomposition — then keep the narrower one.

    A *nice* path decomposition starts with an empty bag, ends with an
    empty bag, and every transition is either an Introduce (add 1
    vertex) or a Forget (remove 1 vertex).  The width returned is the
    max bag size minus 1.
    """
    if G.number_of_nodes() == 0:
        return [frozenset()], 0

    candidates: List[List[frozenset]] = []
    # Heuristic 1: greedy min-degree.
    candidates.append(_vertex_ordering_path_decomp(G, _greedy_min_degree_order(G)))
    # Heuristic 2: order vertices by their tree-decomposition DFS order.
    try:
        _, T_tree = treewidth_min_fill_in(G)
        # DFS the tree-decomposition; flatten encountered bags into an order.
        root = max(T_tree.nodes(), key=lambda b: len(b))
        seen_bags = set()
        seen_vertices = set()
        order2: List[int] = []
        stack = [root]
        while stack:
            b = stack.pop()
            if b in seen_bags:
                continue
            seen_bags.add(b)
            for v in sorted(b):
                if v not in seen_vertices:
                    seen_vertices.add(v)
                    order2.append(v)
            for nb in T_tree.neighbors(b):
                if nb not in seen_bags:
                    stack.append(nb)
        # Append any missing vertices.
        for v in G.nodes():
            if v not in seen_vertices:
                seen_vertices.add(v)
                order2.append(v)
        candidates.append(_vertex_ordering_path_decomp(G, order2))
    except Exception:  # noqa: BLE001
        pass

    # Pick the candidate with smallest max bag size.
    best = min(candidates, key=lambda bags: max(len(b) for b in bags))
    # Convert to nice path decomposition: pad with introduce/forget
    # between consecutive bags so transitions are single-vertex changes.
    nice: List[frozenset] = [frozenset()]
    prev: frozenset = frozenset()
    for bag in best:
        cur = prev
        for v in sorted(cur - bag):
            cur = cur - {v}
            nice.append(cur)
        for v in sorted(bag - cur):
            cur = cur | {v}
            nice.append(cur)
        prev = bag
    # Ensure final empty bag.
    cur = prev
    for v in sorted(cur):
        cur = cur - {v}
        nice.append(cur)
    width = max(len(b) for b in nice) - 1
    # Sanity check: every vertex appears in a contiguous range of nice bags.
    # (This is the path-decomp invariant.)
    first_seen: Dict[int, int] = {}
    last_seen: Dict[int, int] = {}
    for i, b in enumerate(nice):
        for v in b:
            if v not in first_seen:
                first_seen[v] = i
            last_seen[v] = i
    for v, fi in first_seen.items():
        li = last_seen[v]
        for j in range(fi, li + 1):
            if v not in nice[j]:
                raise AssertionError(
                    f"path-decomp invariant violated: vertex {v} missing from bag {j}"
                )
    return nice, width


# ---------------------------------------------------------------------------
# 3. The DP.
# ---------------------------------------------------------------------------

def _canonicalize(bag: Sequence[int], sigma: Sequence[int], degree: Dict[int, int], comp: Dict[int, int]) -> Tuple:
    """Canonical hashable signature of the bag-DP state.

    The state is:
    - sigma: tuple of bag vertices in their LFO-order
    - degree: tuple in same order as sigma giving deg
    - comp: tuple giving component representative per bag vertex, in
      canonical relabeling (rep = smallest vertex in that component).
    """
    sigma_t = tuple(sigma)
    deg_t = tuple(degree[v] for v in sigma_t)
    # Canonical comp: group bag vertices into their components, label
    # each by the smallest σ-index in the component.
    reps: Dict[int, int] = {}
    for v in sigma_t:
        r = comp[v]
        reps.setdefault(r, v)
    comp_t = tuple(reps[comp[v]] for v in sigma_t)
    return (sigma_t, deg_t, comp_t)


def path_fas_state_signature(bag_vertices, sigma, degree, comp):
    """Public API: hashable signature for the bag-DP state.

    `bag_vertices`: iterable of vertex labels in the bag (order
        irrelevant; encoded into σ).
    `sigma`: a tuple/list giving the LFO order on bag vertices.
    `degree`: mapping v -> degree in {0, 1, 2}.
    `comp`: mapping v -> component representative.
    """
    return _canonicalize(tuple(bag_vertices), sigma, dict(degree), dict(comp))


def path_fas_J_pathwidth_dp(
    T: Matrix,
    decomposition: List[frozenset] | None = None,
    radius: int = 2,
) -> bool:
    """Decide formal Path-FAS for T using the bag-by-bag DP on J.

    If `decomposition` is None, compute one from networkx's min-fill-in
    treewidth heuristic.

    Returns True iff there exists an LFO σ of V(T) compatible with the
    score-window forced partial order whose loaded backedge multigraph
    (every T-arc forced or chosen as a backedge) is a linear forest.
    """
    n = len(T)
    windows = score_windows(T, radius)
    J, _, _, _ = J_graph(T, radius)
    if decomposition is None:
        decomposition, _ = nice_path_decomposition(J)

    # Forced inequalities: u must precede v if hi_u < lo_v.
    # We use them whenever inserting a new vertex into σ to constrain
    # admissible positions w.r.t. other bag vertices.
    def must_precede(u: int, v: int) -> bool:
        """True iff every LFO has σ(u) < σ(v) -- forced by windows."""
        hi_u = windows[u][1]
        lo_v = windows[v][0]
        if hi_u < lo_v:
            return True
        return False

    # State = (sigma, degree, comp) restricted to current bag.
    # We store reachable states as a set of canonical signatures
    # together with the "full" data needed to extend them.

    StateKey = Tuple
    # We maintain bag_states: dict[StateKey, (sigma, degree, comp)]
    # where the latter are concrete dictionaries reproducing the state.

    initial_bag = decomposition[0]
    assert len(initial_bag) == 0, "nice path decomposition must start empty"
    bag_states: Dict[StateKey, Tuple[Tuple[int, ...], Dict[int, int], Dict[int, int]]]
    bag_states = {((), (), ()): ((), {}, {})}

    cur_bag = initial_bag
    for nxt_bag in decomposition[1:]:
        new_states: Dict[StateKey, Tuple[Tuple[int, ...], Dict[int, int], Dict[int, int]]] = {}
        diff_introduce = nxt_bag - cur_bag
        diff_forget = cur_bag - nxt_bag
        if diff_introduce and diff_forget:
            raise ValueError("transition is not a single introduce/forget")
        if diff_introduce:
            v = next(iter(diff_introduce))
            # For every reachable state, insert v at every admissible σ-position
            # and try every valid backedge-loading of the J-edges between v and
            # bag-mates.
            for key, (sigma, degree, comp) in bag_states.items():
                bag_mates = list(sigma)
                # Determine admissible σ-positions for v.
                # σ-position i means inserting v so its rank is i (0 <= i <= len(sigma)).
                # Constraint: every bag mate u with must_precede(u, v) must have
                #   rank(u) < i (i.e. u sits before v); symmetrically for must_precede(v, u).
                allowed_positions: List[int] = []
                for i in range(len(sigma) + 1):
                    ok = True
                    for j, u in enumerate(sigma):
                        # if j < i: u sits before v
                        # if j >= i: u sits at or after v (v inserted at rank i bumps u to j+1)
                        u_before_v = (j < i)
                        if must_precede(v, u) and u_before_v:
                            ok = False
                            break
                        if must_precede(u, v) and not u_before_v:
                            ok = False
                            break
                    if ok:
                        allowed_positions.append(i)
                for pos in allowed_positions:
                    new_sigma = list(sigma[:pos]) + [v] + list(sigma[pos:])
                    new_degree = dict(degree)
                    new_degree[v] = 0
                    new_comp = dict(comp)
                    new_comp[v] = v
                    # Load J-edges {v, u} for each bag-mate u with v adjacent to u in J.
                    sigma_pos = {x: i for i, x in enumerate(new_sigma)}
                    feasible = True
                    # Build a fresh union-find over bag vertices (and any
                    # forgotten-vertex reps still referenced by new_comp).
                    parent_local: Dict[int, int] = {x: new_comp[x] for x in new_sigma}
                    for x in new_sigma:
                        r = new_comp[x]
                        if r not in parent_local:
                            # Forgotten rep: make it a self-loop so find_local
                            # treats it as a placeholder component root.
                            parent_local[r] = r

                    def find_local(x: int, _p=parent_local) -> int:
                        while _p[x] != x:
                            _p[x] = _p[_p[x]]
                            x = _p[x]
                        return x

                    def union_local(a: int, b: int, _p=parent_local) -> bool:
                        ra = find_local(a)
                        rb = find_local(b)
                        if ra == rb:
                            return False
                        _p[rb] = ra
                        return True

                    for u in bag_mates:
                        if not J.has_edge(v, u):
                            continue
                        # Determine if this J-edge becomes a backedge under new_sigma.
                        if is_backedge_in_LFO(T, v, u, sigma_pos):
                            # Load it.
                            if new_degree[v] >= 2 or new_degree[u] >= 2:
                                feasible = False
                                break
                            if find_local(v) == find_local(u):
                                feasible = False
                                break
                            new_degree[v] += 1
                            new_degree[u] += 1
                            union_local(v, u)
                    if not feasible:
                        continue
                    # Update new_comp to reflect the local union-find.
                    final_comp: Dict[int, int] = {}
                    for x in new_sigma:
                        r = find_local(x)
                        final_comp[x] = r
                    sig_key = _canonicalize(new_sigma, new_sigma, new_degree, final_comp)
                    if sig_key not in new_states:
                        new_states[sig_key] = (tuple(new_sigma), dict(new_degree), dict(final_comp))
        elif diff_forget:
            v = next(iter(diff_forget))
            for key, (sigma, degree, comp) in bag_states.items():
                # Drop v from sigma, degree, comp.
                new_sigma = tuple(x for x in sigma if x != v)
                new_degree = {x: degree[x] for x in new_sigma}
                # When v leaves, all its J-edges to future bag mates would
                # have to exist via path-decomp; but they cannot (by the
                # path-decomp invariant since v is forgotten).  So v's
                # final state is fixed.
                # Re-canonicalize comp: if v was the rep of a component,
                # promote another bag-vertex in that component to rep;
                # if no other bag-vertex shared v's component, then that
                # component is now "external" — its rep is v (no future
                # interaction needed).
                old_rep = comp[v]
                # Relabel comp_dict: any vertex x with comp[x] == old_rep
                # whose "owner" is gone: promote a new rep among remaining
                # bag vertices with same comp[x].
                # Simpler: just store comp[x] unchanged for remaining x.
                # The canonicalize function relabels by smallest σ-index.
                new_comp = {x: comp[x] for x in new_sigma}
                sig_key = _canonicalize(new_sigma, new_sigma, new_degree, new_comp)
                if sig_key not in new_states:
                    new_states[sig_key] = (new_sigma, new_degree, new_comp)
        else:
            # Identity transition (cur_bag == nxt_bag): pass through.
            new_states = dict(bag_states)
        bag_states = new_states
        cur_bag = nxt_bag
        if not bag_states:
            return False

    final_bag = decomposition[-1]
    assert len(final_bag) == 0, "nice path decomposition must end empty"
    # Any surviving state at the empty final bag is a YES.
    return len(bag_states) > 0


# ---------------------------------------------------------------------------
# 4. CLI / smoke tests.
# ---------------------------------------------------------------------------

def _smoke() -> None:
    # Trivial transitive tournament: always YES (back-arc graph is empty).
    n = 4
    T = [[1 if i < j else 0 for j in range(n)] for i in range(n)]
    for i in range(n):
        T[i][i] = 0
    J, H, F, _ = J_graph(T)
    print("transitive J edges:", list(J.edges()))
    decomp, w = nice_path_decomposition(J)
    print("decomp width:", w, "bags:", [tuple(sorted(b)) for b in decomp])
    print("dp:", path_fas_J_pathwidth_dp(T))
    print("brute:", decide_path_fas_bruteforce(T)["found"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--T", help="Tournament as JSON matrix")
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()
    if args.smoke:
        _smoke()
    elif args.T:
        T = json.loads(args.T)
        verdict = path_fas_J_pathwidth_dp(T)
        print(json.dumps({"verdict": verdict}))
    else:
        parser.print_help()
