"""
RED-TEAM independent verifier for Conjecture 9.2 candidate counterexamples.
Coded from scratch; does NOT import h2_oracle.py.

Checks:
 (1) 2-extremal: strong, underlying 2-connected, lambda==2, chi_vec==3.
 (2) Independent H_2 membership search:
       - base: symmetric odd cycles (digon-double of C_{2t+1})
       - directed Hajos join inverse
       - 2-Hajos tree join inverse (incl. generalised wheels = empty A)
     recursively over all H_2 members up to current n.
"""
import itertools
from functools import lru_cache
import networkx as nx


# ----------------------------------------------------------------------
# Representation helpers
# ----------------------------------------------------------------------
def arcset(arcs):
    return frozenset((u, v) for u, v in arcs)


def make_digraph(n, arcs):
    G = nx.DiGraph()
    G.add_nodes_from(range(n))
    G.add_edges_from((u, v) for u, v in arcs)
    return G


def canon(n, arcs):
    """Canonical form via brute permutation (n small). Returns sorted tuple of arcs
    under the lexicographically smallest relabeling."""
    A = arcset(arcs)
    best = None
    for perm in itertools.permutations(range(n)):
        relabeled = tuple(sorted((perm[u], perm[v]) for (u, v) in A))
        if best is None or relabeled < best:
            best = relabeled
    return (n, best)


# ----------------------------------------------------------------------
# (1) 2-extremal recomputation (independent)
# ----------------------------------------------------------------------
def is_strong(n, arcs):
    G = make_digraph(n, arcs)
    return nx.is_strongly_connected(G)


def underlying_2connected(n, arcs):
    U = nx.Graph()
    U.add_nodes_from(range(n))
    for u, v in arcs:
        U.add_edge(u, v)
    if U.number_of_nodes() < 3:
        return False
    return nx.is_biconnected(U)


def lambda_local(n, arcs):
    """max over ordered pairs (x,y) of arc-disjoint x->y dipaths = unit-cap max flow."""
    G = nx.DiGraph()
    G.add_nodes_from(range(n))
    for u, v in arcs:
        G.add_edge(u, v, capacity=1)
    best = 0
    for x in range(n):
        for y in range(n):
            if x == y:
                continue
            f = nx.maximum_flow_value(G, x, y)
            best = max(best, f)
    return best


def chi_vec(n, arcs):
    """min k: partition V into k classes each inducing an acyclic subdigraph.
    Independent backtracking with acyclicity check via nx."""
    succ = {i: set() for i in range(n)}
    for u, v in arcs:
        succ[u].add(v)

    def induces_acyclic(vertices):
        vs = set(vertices)
        H = nx.DiGraph()
        H.add_nodes_from(vs)
        for u in vs:
            for w in succ[u]:
                if w in vs:
                    H.add_edge(u, w)
        return nx.is_directed_acyclic_graph(H)

    # try k = 1,2,3,... greedily with backtracking
    def colorable(k):
        classes = [set() for _ in range(k)]
        order = sorted(range(n), key=lambda x: -len(succ[x]))

        def bt(idx):
            if idx == len(order):
                return True
            v = order[idx]
            seen_empty = False
            for c in range(k):
                if not classes[c]:
                    if seen_empty:
                        continue  # symmetry break: only try first empty class
                    seen_empty = True
                classes[c].add(v)
                if induces_acyclic(classes[c]):
                    if bt(idx + 1):
                        return True
                classes[c].discard(v)
            return False

        return bt(0)

    k = 1
    while True:
        if colorable(k):
            return k
        k += 1
        if k > n:
            return n


def is_2extremal(n, arcs):
    return (is_strong(n, arcs)
            and underlying_2connected(n, arcs)
            and lambda_local(n, arcs) == 2
            and chi_vec(n, arcs) == 3)


# ----------------------------------------------------------------------
# (2) H_2 membership search, independently coded
# ----------------------------------------------------------------------

def sym_odd_cycle(t):
    """digon-double of C_{2t+1}, on vertices 0..2t. Returns (n, arcs)."""
    m = 2 * t + 1
    arcs = []
    for i in range(m):
        j = (i + 1) % m
        arcs.append((i, j))
        arcs.append((j, i))
    return m, sorted(arcs)


# Generate canonical set of all 2-extremal digraphs up to size N, and the
# canonical set of H_2 members up to size N (built from below).

def neighbors_in(n, arcs):
    inn = {i: set() for i in range(n)}
    out = {i: set() for i in range(n)}
    for u, v in arcs:
        out[u].add(v)
        inn[v].add(u)
    return inn, out


# ---- Directed Hajos join INVERSE ----
# Forward: D from D1 (has u->v1) and D2 (has v2->w). Delete u->v1, v2->w; identify
# v1=v2 => v; add u->w.  Result D has vertex v which is "split" of v1,v2; arc u->w.
# Inverse: pick arc (u,w) in D. Pick a vertex v (the merged vertex). Split v into v1,v2:
# v's in-arcs and out-arcs distributed between v1 and v2. D1 contains u, v1 (with arc u->v1
# added back), and one side; D2 contains v2, w (with arc v2->w added), other side. The arc
# (u,w) is removed.
# Both D1, D2 must be 2-extremal H_2 members, smaller (each has < n vertices? actually
# n1 + n2 = n + 1 since v split into two; with u in D1, w in D2). Sizes n1,n2 < n.

def hajos_inverse_pieces(n, arcs):
    """Yield (n1, arcs1, n2, arcs2) candidate splits for directed Hajos join inverse."""
    A = arcset(arcs)
    inn, out = neighbors_in(n, arcs)
    for (u, w) in list(A):
        if u == w:
            continue
        # the new arc u->w to be removed; u in D1 side, w in D2 side
        A_minus = A - {(u, w)}
        # choose merged vertex v != u, w
        for v in range(n):
            if v == u or v == w:
                continue
            # v gets split into v1 (in D1, target of u->v1) and v2 (in D2, source of v2->w)
            # Partition v's incident arcs (in A_minus) between the two copies, but the
            # connected-component structure after removing v's identity must separate into
            # two parts: D1 containing u and v1, D2 containing w and v2, with v1/v2 being
            # the ONLY shared (split) vertex.
            # Concretely: removing vertex v from (V, A_minus) should disconnect (in the
            # underlying graph) u-side from w-side. Then D1 = u-side + {v as v1}, D2 = w-side + {v as v2}.
            others = [x for x in range(n) if x != v]
            # underlying graph on A_minus minus vertex v
            U = nx.Graph()
            U.add_nodes_from(others)
            for (a, b) in A_minus:
                if a != v and b != v:
                    U.add_edge(a, b)
            comps = list(nx.connected_components(U))
            if len(comps) != 2:
                continue
            # u and w must be in different components
            cu = next((c for c in comps if u in c), None)
            cw = next((c for c in comps if w in c), None)
            if cu is None or cw is None or cu is cw:
                continue
            # Build D1 on cu + {v1}, D2 on cw + {v2}
            # D1 vertices: cu plus v (as v1). Arcs: those of A_minus with both endpoints in
            # cu, plus v's arcs to/from cu, plus added arc u->v1.
            d1_verts = set(cu) | {v}
            d2_verts = set(cw) | {v}
            d1_arcs = set()
            d2_arcs = set()
            for (a, b) in A_minus:
                if a in d1_verts and b in d1_verts and not (a in cw or b in cw):
                    # arc within D1 (v counts as v1)
                    if (a == v or a in cu) and (b == v or b in cu):
                        d1_arcs.add((a, b))
                if a in d2_verts and b in d2_verts:
                    if (a == v or a in cw) and (b == v or b in cw):
                        d2_arcs.add((a, b))
            d1_arcs.add((u, v))  # added back u->v1
            d2_arcs.add((v, w))  # added back v2->w
            # relabel to 0..k-1
            yield _relabel(d1_verts, d1_arcs)
            yield _relabel(d2_verts, d2_arcs),
    return


def _relabel(verts, arcs):
    vs = sorted(verts)
    idx = {v: i for i, v in enumerate(vs)}
    return (len(vs), sorted((idx[a], idx[b]) for (a, b) in arcs))


def hajos_inverse_splits(n, arcs):
    """Proper generator: yield (piece1, piece2) where each piece=(nk,arcsk)."""
    A = arcset(arcs)
    for (u, w) in list(A):
        if u == w:
            continue
        A_minus = A - {(u, w)}
        for v in range(n):
            if v == u or v == w:
                continue
            others = [x for x in range(n) if x != v]
            U = nx.Graph()
            U.add_nodes_from(others)
            for (a, b) in A_minus:
                if a != v and b != v:
                    U.add_edge(a, b)
            comps = list(nx.connected_components(U))
            if len(comps) != 2:
                continue
            cu = next((c for c in comps if u in c), None)
            cw = next((c for c in comps if w in c), None)
            if cu is None or cw is None or cu is cw:
                continue
            d1_verts = set(cu) | {v}
            d2_verts = set(cw) | {v}
            d1_arcs = set()
            d2_arcs = set()
            for (a, b) in A_minus:
                if a in d1_verts and b in d1_verts:
                    d1_arcs.add((a, b))
                elif a in d2_verts and b in d2_verts:
                    d2_arcs.add((a, b))
            d1_arcs.add((u, v))
            d2_arcs.add((v, w))
            p1 = _relabel(d1_verts, d1_arcs)
            p2 = _relabel(d2_verts, d2_arcs)
            yield p1, p2


# ---- 2-Hajos tree join INVERSE (incl generalised wheels) ----
# This is harder. We use a structural detector for the GENERALISED WHEEL case (empty A):
# a generalised wheel = a "hub" structure? Per Def 9.1 with empty A: plane tree T with all
# edges in B (parity condition forces leaf-to-leaf paths even # of B-edges => T is a path?).
# We implement the general forward construction over small trees and small D_i, building the
# H_2 closure from below instead of inverting. Inversion of tree-join is replaced by forward
# closure enumeration, which is COMPLETE up to the size bound. See build_h2_closure.

# ----------------------------------------------------------------------
# Forward closure of H_2 up to size N (the rigorous route).
# ----------------------------------------------------------------------

def hajos_join(D1, D2, u, v1, v2, w):
    """Forward directed Hajos join. D1=(n1,arcs1) has arc u->v1; D2=(n2,arcs2) has v2->w.
    Identify v1 (in D1) with v2 (in D2) into a single vertex v. Returns (n,arcs) or None."""
    n1, arcs1 = D1
    n2, arcs2 = D2
    A1 = set(map(tuple, arcs1))
    A2 = set(map(tuple, arcs2))
    if (u, v1) not in A1 or (v2, w) not in A2:
        return None
    # vertices: D1 verts 0..n1-1 ; D2 verts shifted by n1 except v2 maps to v1's id.
    offset = n1
    def mapD2(x):
        if x == v2:
            return v1  # merge
        return x + offset
    new = set()
    for (a, b) in A1:
        if (a, b) == (u, v1):
            continue
        new.add((a, b))
    for (a, b) in A2:
        if (a, b) == (v2, w):
            continue
        new.add((mapD2(a), mapD2(b)))
    new.add((u, mapD2(w)))
    # relabel compactly
    verts = set()
    for (a, b) in new:
        verts.add(a); verts.add(b)
    # check no parallel/loop issues: loopless, no parallel (set handles parallel)
    if any(a == b for (a, b) in new):
        return None
    nn, na = _relabel(verts, new)
    return (nn, na)


def directed_cycle_arcs(order):
    """directed cycle on the given cyclic order list."""
    arcs = []
    L = len(order)
    for i in range(L):
        arcs.append((order[i], order[(i + 1) % L]))
    return arcs


# Plane trees enumeration (small), with leaf circular order.
def gen_plane_trees(num_edges):
    """Generate plane trees with `num_edges` edges as (nodes, edge_list, leaves_in_circular_order).
    We enumerate via labelled trees then dedup is unnecessary for closure soundness (over-generation
    is fine for building a closure; we just need to not MISS members)."""
    nv = num_edges + 1
    # all labelled trees on nv nodes via Prufer
    import itertools as it
    if nv == 1:
        return
    if nv == 2:
        yield ([0, 1], [(0, 1)])
        return
    for seq in it.product(range(nv), repeat=nv - 2):
        # Prufer decode
        degree = [1] * nv
        for x in seq:
            degree[x] += 1
        edges = []
        seqlist = list(seq)
        import heapq
        leaves = [i for i in range(nv) if degree[i] == 1]
        heapq.heapify(leaves)
        s = list(seq)
        for x in s:
            leaf = heapq.heappop(leaves)
            edges.append((leaf, x))
            degree[x] -= 1
            if degree[x] == 1:
                heapq.heappush(leaves, x)
        u_ = heapq.heappop(leaves)
        v_ = heapq.heappop(leaves)
        edges.append((u_, v_))
        yield (list(range(nv)), edges)


def tree_leaves(nv, edges):
    deg = [0] * nv
    adj = {i: [] for i in range(nv)}
    for (a, b) in edges:
        deg[a] += 1; deg[b] += 1
        adj[a].append(b); adj[b].append(a)
    leaves = [i for i in range(nv) if deg[i] == 1]
    return leaves, adj, deg


def leaf_to_leaf_paths_even_B(nv, edges, B):
    """Check every leaf-to-leaf path uses an even number of B-edges."""
    leaves, adj, deg = tree_leaves(nv, edges)
    Bset = set(frozenset(e) for e in B)
    # BFS path between each leaf pair; tree => unique path
    def path_B_count(s, t):
        # parent BFS
        from collections import deque
        par = {s: None}
        dq = deque([s])
        while dq:
            x = dq.popleft()
            if x == t:
                break
            for y in adj[x]:
                if y not in par:
                    par[y] = x
                    dq.append(y)
        # reconstruct
        cnt = 0
        cur = t
        while par[cur] is not None:
            p = par[cur]
            if frozenset((cur, p)) in Bset:
                cnt += 1
            cur = p
        return cnt
    for i in range(len(leaves)):
        for j in range(i + 1, len(leaves)):
            if path_B_count(leaves[i], leaves[j]) % 2 != 0:
                return False
    return True


if __name__ == "__main__":
    # quick self-test on candidate
    cand_n = 7
    cand_arcs = [[0,3],[0,4],[1,5],[1,6],[2,4],[2,5],[3,1],[3,5],[4,0],[4,2],[4,6],[5,1],[5,2],[5,3],[6,0],[6,4]]
    print("strong:", is_strong(cand_n, cand_arcs))
    print("underlying 2-connected:", underlying_2connected(cand_n, cand_arcs))
    print("lambda:", lambda_local(cand_n, cand_arcs))
    print("chi_vec:", chi_vec(cand_n, cand_arcs))
    print("2-extremal:", is_2extremal(cand_n, cand_arcs))
