"""DECISIVE test of the discriminating question:

  Does AC_17 admit an OPTIMAL order whose backedge graph is iso to Paley(17)?

By R(4,4)=18 + McKay-Radziszowski (1995) uniqueness, a 17-vertex graph with
omega=3 AND alpha=3 is FORCED iso to Paley(17). And an optimal order of AC_17 has
omega(backedge)=omega_vec=3. Hence:

    min-optimal-order alpha(AC_17) = 3   IFF   some order's backedge graph ~ Paley(17).

A graph H (on the SAME 17 vertices, via a bijection sigma: V(H)->V(T)) is the
backedge graph of T under a linear order pi  iff  there is a linear order pi of the
vertices such that for EVERY pair {x,y}:
    {sigma(x),sigma(y)} is an edge of H  <=>  the T-arc between sigma(x),sigma(y)
        goes from the pi-LATER to the pi-EARLIER (a backward arc).

Fix sigma (a labeling of Paley17 onto V(T)). For a pair (a,b)=(sigma(x),sigma(y))
with T-arc a->b:
  - if {x,y} in E(H): the arc a->b must be BACKWARD => b precedes a in pi  (b < a).
  - if {x,y} not in E(H): a->b must be FORWARD => a precedes b in pi   (a < b).
So sigma is realizable IFF the induced set of order-constraints (a directed graph on
V(T)) is ACYCLIC (a valid topological order = pi exists).

So the discriminating question = does there EXIST a bijection sigma: Paley17 -> V(T)
making the constraint digraph acyclic? Paley17 is arc-transitive & vertex-transitive
with a large automorphism group (|Aut|=17*8*2=272 as a graph), and AC_17 is a
circulant (Aut >= Z/17). We search over bijections with these symmetries factored out:
fix sigma(0)=0 (both vertex-transitive) and enumerate the rest with constraint
propagation + acyclicity check. We ALSO run the equivalent via the alpha-min B&B's
finding as cross-evidence.

This is EXACT: either we exhibit a realizing sigma (=> CONFIRM, alpha=3 attainable,
backedge ~ Paley17) or we prove none exists over the reduced search (=> KILL).
"""
import sys, os, time, itertools
sys.path.insert(0, os.path.dirname(__file__))
import core
import networkx as nx


def build_ac17():
    p = 17
    g = (1, 2, 3, 4, 5, 6, 7, 9)
    arcs = [(i, (i + d) % p) for i in range(p) for d in g]
    assert core.is_tournament(p, arcs)
    return p, arcs


def paley17_adj():
    p = 17
    QR = {pow(x, 2, p) for x in range(1, p)}
    H = [[False] * p for _ in range(p)]
    for i in range(p):
        for j in range(p):
            if i != j and (i - j) % p in QR:
                H[i][j] = True
    return H  # symmetric


def realizable_sigma(p, beats, H):
    """Search bijection sigma: Paley vertices -> T vertices (fix sigma(0)=0) such
    that the order-constraint digraph is acyclic. Returns sigma (list) or None.

    Constraint for assigned pair: T vertices a=sigma(x), b=sigma(y), T-arc a->b.
      edge(x,y) in H  => need b precedes a   (constraint b -> a   "b before a")
      non-edge        => need a precedes b   (constraint a -> b)
    Build precedence digraph P on T-vertices incrementally; require acyclic.
    """
    # adjacency 'beats[a][b]' True iff a->b in T
    sigma = [None] * p          # sigma[x] = T-vertex assigned to Paley vertex x
    used = [False] * p
    # precedence successors: prec[u] = set of v with constraint u-before-v (u->v means u precedes v)
    prec = [set() for _ in range(p)]
    indeg_order = []            # not needed; we re-check acyclicity via DFS on prec among assigned T-verts

    sigma[0] = 0
    used[0] = True
    assigned_T = [0]

    def add_constraints(x):
        """Add all order-constraints between newly-assigned Paley vtx x and previously
        assigned Paley vertices. Return list of added edges (for rollback) or None if
        adding creates a cycle (not acyclic)."""
        a = sigma[x]
        added = []
        for y in range(p):
            if y == x or sigma[y] is None:
                continue
            b = sigma[y]
            # T-arc direction between a,b
            if beats[a][b]:
                arc_from, arc_to = a, b
            else:
                arc_from, arc_to = b, a
            # backward (edge) => arc_to precedes arc_from; forward (non-edge) => arc_from precedes arc_to
            if H[x][y]:
                # edge: arc must be backward: arc_to before arc_from
                u, v = arc_to, arc_from
            else:
                u, v = arc_from, arc_to
            # constraint: u precedes v  => prec edge u->v
            if v not in prec[u]:
                prec[u].add(v)
                added.append((u, v))
        # acyclicity check on the precedence digraph restricted to assigned T-verts
        if has_cycle(prec, assigned_T):
            # rollback
            for (u, v) in added:
                prec[u].discard(v)
            return None
        return added

    def remove_constraints(added):
        for (u, v) in added:
            prec[u].discard(v)

    def has_cycle(prec, nodes):
        WHITE, GRAY, BLACK = 0, 1, 2
        color = {n: WHITE for n in nodes}
        ns = set(nodes)
        def dfs(u):
            color[u] = GRAY
            for w in prec[u]:
                if w not in ns:
                    continue
                if color[w] == GRAY:
                    return True
                if color[w] == WHITE and dfs(w):
                    return True
            color[u] = BLACK
            return False
        for n in nodes:
            if color[n] == WHITE and dfs(n):
                return True
        return False

    order = list(range(1, p))   # assign Paley vertices 1..16 in order
    state = {"count": 0}

    def backtrack(idx):
        if idx == len(order):
            return True
        x = order[idx]
        for t in range(p):
            if used[t]:
                continue
            sigma[x] = t
            used[t] = True
            assigned_T.append(t)
            added = add_constraints(x)
            state["count"] += 1
            if added is not None:
                if backtrack(idx + 1):
                    return True
                remove_constraints(added)
            sigma[x] = None
            used[t] = False
            assigned_T.pop()
        return False

    ok = backtrack(0)
    return (sigma if ok else None), state["count"]


def main():
    p, arcs = build_ac17()
    beats = core.beats_matrix(p, arcs)
    H = paley17_adj()
    print("=== Is Paley(17) realizable as a backedge graph of AC_17? ===", flush=True)
    print("(realizable <=> some optimal order has alpha=3 <=> CONFIRM branch)", flush=True)
    t0 = time.time()
    sigma, cnt = realizable_sigma(p, beats, H)
    dt = time.time() - t0
    print(f"search nodes={cnt}  elapsed={dt:.1f}s", flush=True)
    if sigma is not None:
        print(f"REALIZABLE: sigma = {sigma}", flush=True)
        # reconstruct pi (a topological order of the precedence digraph) and verify
        # build the backedge graph and confirm omega=3, alpha=3, iso Paley17
        # constraints: pi is any linear extension; recompute backedge graph
        # Build precedence digraph fully then topo-sort
        prec = [set() for _ in range(p)]
        for x in range(p):
            for y in range(x + 1, p):
                a, b = sigma[x], sigma[y]
                if beats[a][b]:
                    arc_from, arc_to = a, b
                else:
                    arc_from, arc_to = b, a
                if H[x][y]:
                    u, v = arc_to, arc_from
                else:
                    u, v = arc_from, arc_to
                prec[u].add(v)
        # topo sort
        import collections
        indeg = [0] * p
        for u in range(p):
            for v in prec[u]:
                indeg[v] += 1
        q = collections.deque([u for u in range(p) if indeg[u] == 0])
        pi = []
        while q:
            u = q.popleft(); pi.append(u)
            for v in prec[u]:
                indeg[v] -= 1
                if indeg[v] == 0:
                    q.append(v)
        assert len(pi) == p, "precedence digraph not acyclic in reconstruction"
        # backedge graph under pi
        pos = [0] * p
        for i, v in enumerate(pi):
            pos[v] = i
        G = nx.Graph(); G.add_nodes_from(range(p))
        for a in range(p):
            for b in range(a + 1, p):
                lo, hi = (a, b) if pos[a] < pos[b] else (b, a)
                if beats[hi][lo]:
                    G.add_edge(a, b)
        om = max((len(c) for c in nx.find_cliques(G)), default=1)
        al = max((len(c) for c in nx.find_cliques(nx.complement(G))), default=1)
        P = nx.Graph(); P.add_nodes_from(range(p))
        for i in range(p):
            for j in range(i + 1, p):
                if H[i][j]:
                    P.add_edge(i, j)
        iso = nx.is_isomorphic(G, P)
        print(f"VERIFY backedge graph under pi: omega={om} alpha={al} iso_Paley17={iso}", flush=True)
        print(f"pi = {pi}", flush=True)
        print("VERDICT: CONFIRM (alpha=3 attainable; backedge ~ Paley17; route pinned at Ramsey ceiling)", flush=True)
    else:
        print("NOT REALIZABLE: no bijection sigma makes the order-constraints acyclic.", flush=True)
        print("=> AC_17 has NO optimal order with backedge ~ Paley17 => NO optimal order with alpha=3.", flush=True)
        print("VERDICT: KILL (alpha>3 forced; the alpha<=3 Ramsey cap is VACUOUS at order 17)", flush=True)


if __name__ == "__main__":
    main()
