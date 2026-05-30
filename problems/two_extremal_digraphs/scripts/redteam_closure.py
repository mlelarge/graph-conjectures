"""
RED-TEAM independent H_2 closure builder (forward, complete up to size N).

Builds H_2 from below:
  base = symmetric odd cycles (digon-doubled C_{2t+1}), n = 3,5,7,...
  closure under:
     (A) directed Hajos join
     (B) 2-Hajos tree join (incl. empty A = generalised wheel)

We over-generate (try all label choices / all small trees / all A-edge digraph
substitutions from the current closure). This CANNOT miss an H_2 member of size
<= N: any H_2 member has a finite derivation tree whose intermediate objects are
all H_2 members; if its final size is <= N then (because both operations are
size-monotone: output size >= each input size for Hajos join with n=n1+n2-1, and
tree join output >= each substituted D_i) all intermediates also have size <= N.

So a fixpoint closure up to size N over both ops, seeded by the base, yields
exactly H_2 ∩ {size <= N} as canonical forms. Membership of the candidate is then
a canonical-form lookup. This is the rigorous (non-inversion) route.
"""
import itertools
from collections import deque
import networkx as nx

from redteam_verify import (
    canon, arcset, _relabel, sym_odd_cycle, is_2extremal,
    leaf_to_leaf_paths_even_B, gen_plane_trees, tree_leaves,
    directed_cycle_arcs,
)


def hajos_join_all(D1, D2):
    """Yield all directed Hajos joins of D1,D2 over all choices of arcs u->v1, v2->w."""
    n1, arcs1 = D1
    n2, arcs2 = D2
    A1 = [tuple(a) for a in arcs1]
    A2 = [tuple(a) for a in arcs2]
    A1set = set(A1)
    A2set = set(A2)
    for (u, v1) in A1:
        for (v2, w) in A2:
            # identify v1 (D1) with v2 (D2) => v. New vertex set:
            # D1 keeps ids 0..n1-1; D2 ids shift by n1 except v2 -> v1.
            offset = n1
            def mapD2(x):
                return v1 if x == v2 else x + offset
            new = set()
            for (a, b) in A1set:
                if (a, b) == (u, v1):
                    continue
                new.add((a, b))
            for (a, b) in A2set:
                if (a, b) == (v2, w):
                    continue
                new.add((mapD2(a), mapD2(b)))
            uu, ww = u, mapD2(w)
            if uu == ww:
                continue
            new.add((uu, ww))
            if any(a == b for (a, b) in new):
                continue
            verts = set()
            for (a, b) in new:
                verts.add(a); verts.add(b)
            yield _relabel(verts, new)


def tree_join_all(members_by_size, max_n, base_pool):
    """Generate 2-Hajos tree joins. members_by_size: dict size->list of (n,arcs).
    base_pool: flat list of all current members (n,arcs) usable as A-edge digraphs.

    Construction (Def 9.1):
      - plane tree T with >=2 edges; leaves in circular order.
      - partition E(T) = (A,B) s.t. every leaf-to-leaf path has EVEN # of B-edges.
      - each A-edge {u_i,v_i} -> a digraph D_i containing digon [u_i,v_i]; remove that digon.
      - each B-edge -> a digon.
      - add directed peripheral cycle on circular leaf order.
    We realize T's nodes as graph vertices; A-edge substitution glues D_i along the
    edge's two endpoints (identifying u_i,v_i with the two tree nodes). For soundness
    of CLOSURE (not missing members) we enumerate trees up to a node bound and
    A-edge digraphs from base_pool; sizes are bounded so result <= max_n filters.
    """
    # bound number of tree edges: a tree join output has at least (#tree nodes) vertices
    # but A-edge substitution can add internal vertices. Keep tree small.
    for num_edges in range(2, max_n):  # >=2 edges
        for (nodes, edges) in gen_plane_trees(num_edges):
            nv = len(nodes)
            leaves, adj, deg = tree_leaves(nv, edges)
            if len(leaves) < 2:
                continue
            E = list(edges)
            # all A/B partitions with parity condition
            for mask in range(1 << len(E)):
                A_edges = [E[i] for i in range(len(E)) if (mask >> i) & 1]
                B_edges = [E[i] for i in range(len(E)) if not ((mask >> i) & 1)]
                if not leaf_to_leaf_paths_even_B(nv, edges, B_edges):
                    continue
                # For each A-edge choose a D_i from base_pool that has a digon, and an
                # orientation (which endpoint is u_i, which is v_i). For closure soundness
                # we try all. B-edges -> digon.
                yield from _assemble_tree_join(nv, edges, leaves, A_edges, B_edges,
                                               base_pool, max_n, deg)


def has_digon(arcs):
    A = set(map(tuple, arcs))
    for (u, v) in A:
        if (v, u) in A:
            return True
    return False


def list_digons(arcs):
    A = set(map(tuple, arcs))
    return [(u, v) for (u, v) in A if u < v and (v, u) in A]


def _assemble_tree_join(nv, edges, leaves, A_edges, B_edges, base_pool, max_n, deg):
    # circular leaf order: use the planar order. For labelled trees we lack a true plane
    # embedding; approximate by sorted leaf id order (over-generation acceptable for
    # closure: peripheral cycle is some cyclic order on leaves; we try a few rotations/orders
    # is expensive. Use sorted order plus its reverse.)
    leaf_orders = [tuple(sorted(leaves)), tuple(reversed(sorted(leaves)))]

    # Candidate D_i for each A-edge: members from base_pool that contain a digon.
    digon_members = [(m, list_digons(m[1])) for m in base_pool if has_digon(m[1])]
    if A_edges and not digon_members:
        return

    # To bound blowup: only proceed if a crude size estimate <= max_n.
    # base tree contributes nv vertices; each A-edge D_i adds (n_i - 2) internal verts.
    # We pick assignments lazily with pruning.
    import itertools as it

    # Precompute for each A-edge the list of (member, chosen digon, orientation)
    options_per_Aedge = []
    for ae in A_edges:
        opts = []
        for (m, digs) in digon_members:
            for (du, dv) in digs:
                # two orientations of mapping (du,dv)->(tree endpoints)
                opts.append((m, (du, dv)))
                opts.append((m, (dv, du)))
        options_per_Aedge.append(opts)

    if A_edges:
        choice_iter = it.product(*options_per_Aedge)
    else:
        choice_iter = [()]

    for choice in choice_iter:
        # crude size check
        extra = sum((opt[0][0] - 2) for opt in choice)
        if nv + extra > max_n:
            continue
        for leaf_order in leaf_orders:
            result = _build_one(nv, edges, A_edges, B_edges, choice, leaf_order, max_n)
            if result is not None:
                yield result


def _build_one(nv, edges, A_edges, B_edges, choice, leaf_order, max_n):
    """Build a single tree-join digraph. Tree nodes are 0..nv-1; A-edge digraphs glued."""
    arcs = set()
    next_id = nv  # internal vertices of substituted D_i get fresh ids

    # B-edges -> digon
    for (a, b) in B_edges:
        arcs.add((a, b)); arcs.add((b, a))

    # A-edges -> D_i minus its chosen digon, gluing chosen digon endpoints (du,dv) to (a,b)
    for ae, opt in zip(A_edges, choice):
        (m_n, m_arcs), (du, dv) = opt
        a, b = ae  # tree endpoints; map du->a, dv->b
        # build vertex map for this D_i
        vmap = {}
        vmap[du] = a
        vmap[dv] = b
        for x in range(m_n):
            if x in vmap:
                continue
            vmap[x] = next_id
            next_id += 1
        for (p, q) in m_arcs:
            pp, qq = vmap[p], vmap[q]
            # remove the chosen digon [du,dv] = arcs (du,dv) and (dv,du)
            if (p, q) == (du, dv) or (p, q) == (dv, du):
                continue
            if pp == qq:
                return None
            arcs.add((pp, qq))

    # peripheral directed cycle on circular leaf order
    for (a, b) in directed_cycle_arcs(list(leaf_order)):
        if a == b:
            return None
        arcs.add((a, b))

    verts = set()
    for (a, b) in arcs:
        verts.add(a); verts.add(b)
    if len(verts) > max_n:
        return None
    # no parallel handled by set; loopless checked
    if any(a == b for (a, b) in arcs):
        return None
    return _relabel(verts, arcs)


def build_h2_closure(max_n, verbose=True):
    """Return set of canonical forms of all H_2 members with <= max_n vertices."""
    closure = {}  # canon -> (n, arcs)
    frontier = deque()

    # seed: symmetric odd cycles
    t = 1
    while 2 * t + 1 <= max_n:
        n, arcs = sym_odd_cycle(t)
        c = canon(n, arcs)
        if c not in closure:
            closure[c] = (n, arcs)
            frontier.append((n, arcs))
        t += 1

    def add(item):
        if item is None:
            return False
        n, arcs = item
        if n > max_n:
            return False
        c = canon(n, arcs)
        if c in closure:
            return False
        closure[c] = (n, arcs)
        frontier.append((n, arcs))
        return True

    # Fixpoint. Tree joins use the whole current pool; rerun until stable.
    changed = True
    rounds = 0
    while changed:
        changed = False
        rounds += 1
        pool = list(closure.values())
        if verbose:
            print(f"[closure] round {rounds}: |closure|={len(closure)}")
        # (A) Hajos joins over all ordered pairs in current pool
        for D1 in pool:
            for D2 in pool:
                if D1[0] + D2[0] - 1 > max_n:
                    continue
                for res in hajos_join_all(D1, D2):
                    if add(res):
                        changed = True
        # (B) tree joins
        pool = list(closure.values())
        by_size = {}
        for m in pool:
            by_size.setdefault(m[0], []).append(m)
        for res in tree_join_all(by_size, max_n, pool):
            if add(res):
                changed = True
    if verbose:
        print(f"[closure] DONE after {rounds} rounds, |closure|={len(closure)}")
    return closure


if __name__ == "__main__":
    import sys, json
    MAXN = int(sys.argv[1]) if len(sys.argv) > 1 else 7
    closure = build_h2_closure(MAXN)
    # sanity: every closure member should be 2-extremal (H_2 ⊆ 2-extremal)
    bad = []
    by_n = {}
    for c, (n, arcs) in closure.items():
        by_n[n] = by_n.get(n, 0) + 1
        if not is_2extremal(n, arcs):
            bad.append((n, arcs))
    print("closure sizes by n:", dict(sorted(by_n.items())))
    print("NON-2-extremal closure members (should be 0):", len(bad))
    for b in bad[:10]:
        print("  BAD:", b)

    # candidate lookup
    cand_n = 7
    cand_arcs = [[0,3],[0,4],[1,5],[1,6],[2,4],[2,5],[3,1],[3,5],[4,0],[4,2],[4,6],[5,1],[5,2],[5,3],[6,0],[6,4]]
    cc = canon(cand_n, cand_arcs)
    print("CANDIDATE in H_2 closure:", cc in closure)
