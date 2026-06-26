"""
Xu-reduction grounding check (literature-reduction proposal).

Step A: re-confirm the lever. For each 3-connected (underlying node-conn>=3)
        is_2extremal member of L_5..L_7, build M (digon->2 parallel edges,
        single arc->1 edge) and assert all pairwise edge-connectivities == 4
        (M is uniformly 4-edge-connected).

Step B: converse search. Exhaustively generate small multigraphs M that
        - split into parallel-PAIRS forming a forest F_D (digon graph),
        - plus single edges,
        - are uniformly 4-edge-connected (all pairwise capacitated maxflow == 4),
        - underlying simple graph is 3-connected,
        and test whether F_D can EVER be disconnected / non-spanning
        (equiv: M has a 4-edge-cut consisting entirely of single edges).
        For any disconnected-F_D witness: orient singles into a balanced
        single-arc set, build digraph D, call h2_oracle.is_2extremal.

PREDICTION (route alive): no such disconnected-F_D witness has is_2extremal=True.
A disconnected-F_D witness with is_2extremal=True KILLS Step 1.
"""
import os
import sys, json, itertools
from collections import deque
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import h2_oracle as H

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')


# ---------- capacitated max-flow (undirected, integer capacities) ----------
def maxflow_cap(n, cap_edges, s, t):
    # cap_edges: dict {(u,v): c} undirected -> we install both directions
    cap = {}
    adj = [[] for _ in range(n)]

    def add(u, v, c):
        if (u, v) not in cap:
            cap[(u, v)] = 0; adj[u].append(v)
        if (v, u) not in cap:
            cap[(v, u)] = 0; adj[v].append(u)
        cap[(u, v)] += c

    for (u, v), c in cap_edges.items():
        add(u, v, c); add(v, u, c)   # undirected edge of capacity c
    flow = 0
    while True:
        parent = {s: None}
        q = deque([s]); found = False
        while q:
            u = q.popleft()
            if u == t:
                found = True; break
            for w in adj[u]:
                if w not in parent and cap[(u, w)] > 0:
                    parent[w] = u; q.append(w)
        if not found:
            break
        # bottleneck
        b = float('inf'); v = t
        while parent[v] is not None:
            b = min(b, cap[(parent[v], v)]); v = parent[v]
        v = t
        while parent[v] is not None:
            u = parent[v]
            cap[(u, v)] -= b; cap[(v, u)] += b; v = u
        flow += b
    return flow


def all_pairwise_cap(n, cap_edges):
    vals = set()
    for s in range(n):
        for t in range(s + 1, n):
            vals.add(maxflow_cap(n, cap_edges, s, t))
    return vals


def _vertex_conn_pair(n, adj, s, t):
    """min vertex cut separating non-adjacent s,t via vertex-split maxflow.
    node v -> v_in (2v), v_out (2v+1), internal cap 1 (INF for s,t).
    Returns flow."""
    INF = 10 ** 9
    N = 2 * n
    cap = {}
    g = [[] for _ in range(N)]
    def add(u, v, c):
        if (u, v) not in cap:
            cap[(u, v)] = 0; g[u].append(v)
        if (v, u) not in cap:
            cap[(v, u)] = 0; g[v].append(u)
        cap[(u, v)] += c
    for v in range(n):
        c = INF if (v == s or v == t) else 1
        add(2 * v, 2 * v + 1, c)
    for (u, v) in adj:
        add(2 * u + 1, 2 * v, INF)
        add(2 * v + 1, 2 * u, INF)
    src, sink = 2 * s + 1, 2 * t
    flow = 0
    while True:
        parent = {src: None}
        q = deque([src]); found = False
        while q:
            u = q.popleft()
            if u == sink:
                found = True; break
            for w in g[u]:
                if w not in parent and cap[(u, w)] > 0:
                    parent[w] = u; q.append(w)
        if not found:
            break
        b = INF; v = sink
        while parent[v] is not None:
            b = min(b, cap[(parent[v], v)]); v = parent[v]
        v = sink
        while parent[v] is not None:
            u = parent[v]
            cap[(u, v)] -= b; cap[(v, u)] += b; v = u
        flow += b
    return flow


def node_connectivity_simple(n, simple_edges):
    """underlying simple node connectivity (kappa) via vertex-split maxflow."""
    if n < 2:
        return 0
    adj_set = [set() for _ in range(n)]
    for (u, v) in simple_edges:
        adj_set[u].add(v); adj_set[v].add(u)
    # connectivity check
    seen = {0}; stk = [0]
    while stk:
        u = stk.pop()
        for w in adj_set[u]:
            if w not in seen:
                seen.add(w); stk.append(w)
    if len(seen) != n:
        return 0
    edges = list(simple_edges)
    kappa = n - 1
    for s in range(n):
        for t in range(s + 1, n):
            if t in adj_set[s]:
                continue
            f = _vertex_conn_pair(n, edges, s, t)
            if f < kappa:
                kappa = f
    # if graph is complete, kappa = n-1
    return kappa


def build_M_from_arcs(n, arcs):
    """digon -> capacity 2 edge, single arc -> capacity 1 edge.
    returns (cap_edges dict, digon_pairs set, single_edges set, simple_edges set)."""
    arcset = set(arcs)
    digon = set()
    single = set()
    for (u, v) in arcs:
        e = (min(u, v), max(u, v))
        if (v, u) in arcset:
            digon.add(e)
        else:
            single.add(e)
    cap = {}
    for e in digon:
        cap[e] = 2
    for e in single:
        cap[e] = 1
    simple = set(digon) | set(single)
    return cap, digon, single, simple


# =================== STEP A ===================
def step_A():
    out = []
    for nn in (5, 6, 7):
        members = json.load(open(f'{BASE}/data/L_{nn}.json'))
        for idx, m in enumerate(members):
            n = m['n']; arcs = [tuple(a) for a in m['arcs']]
            if not H.is_2extremal(n, arcs):
                continue
            nc = node_connectivity_simple(n, build_M_from_arcs(n, arcs)[3])
            if nc < 3:
                continue
            cap, digon, single, simple = build_M_from_arcs(n, arcs)
            vals = all_pairwise_cap(n, cap)
            out.append({
                'file': f'L_{nn}', 'idx': idx, 'n': n,
                'node_conn': nc, 'M_edgeconn_vals': sorted(vals),
                'uniform4': (vals == {4}),
                'n_digon': len(digon), 'n_single': len(single),
            })
    return out


# =================== STEP B ===================
def gen_forests(n, edges_list):
    """yield subsets of edges_list that form a forest spanning subset (acyclic).
    We just yield all acyclic edge subsets (the digon forest F_D)."""
    # DSU helper
    def acyclic(subset):
        par = list(range(n))
        def find(x):
            while par[x] != x:
                par[x] = par[par[x]]; x = par[x]
            return x
        for (u, v) in subset:
            ru, rv = find(u), find(v)
            if ru == rv:
                return False
            par[ru] = rv
        return True
    L = len(edges_list)
    for r in range(0, L + 1):
        for comb in itertools.combinations(edges_list, r):
            if acyclic(comb):
                yield comb


def gen_path_forests(n, edges_list, maxdeg=2):
    """Backtracking generator of acyclic edge subsets with max vertex degree
    <= maxdeg (so the forest is a union of disjoint paths when maxdeg=2).
    Prunes degree/cycle violations during construction."""
    par = list(range(n))
    rank = [0] * n
    deg = [0] * n

    def find(x):
        while par[x] != x:
            x = par[x]
        return x

    chosen = []
    L = len(edges_list)

    def rec(i):
        # yield current forest
        yield tuple(chosen)
        for j in range(i, L):
            u, v = edges_list[j]
            if deg[u] >= maxdeg or deg[v] >= maxdeg:
                continue
            ru, rv = find(u), find(v)
            if ru == rv:
                continue  # would create cycle
            # union
            if rank[ru] < rank[rv]:
                ru, rv = rv, ru
            par[rv] = ru
            inc = (rank[ru] == rank[rv])
            if inc:
                rank[ru] += 1
            deg[u] += 1; deg[v] += 1
            chosen.append((u, v))
            yield from rec(j + 1)
            chosen.pop()
            deg[u] -= 1; deg[v] -= 1
            par[rv] = rv
            if inc:
                rank[ru] -= 1
    yield from rec(0)


def fd_components(n, fd_edges):
    par = list(range(n))
    def find(x):
        while par[x] != x:
            par[x] = par[par[x]]; x = par[x]
        return x
    for (u, v) in fd_edges:
        par[find(u)] = find(v)
    roots = {find(v) for v in range(n)}
    return len(roots)


def orient_balanced(n, single_edges):
    """Try to orient single edges so every vertex is in=out balanced over singles.
    Returns an orientation (list of arcs) or None. Eulerian-orientation:
    each vertex must have even single-degree; then orient along an Euler
    decomposition (closed trails)."""
    deg = [0] * n
    adj = {v: [] for v in range(n)}
    for i, (u, v) in enumerate(single_edges):
        deg[u] += 1; deg[v] += 1
        adj[u].append((v, i)); adj[v].append((u, i))
    if any(d % 2 for d in deg):
        return None
    used = [False] * len(single_edges)
    arcs = []
    # Hierholzer per component
    for start in range(n):
        while adj[start]:
            # find an unused edge from start
            stack = [start]
            path = []
            cur = start
            # standard Euler circuit
            ptr = {v: 0 for v in range(n)}
            # simpler: iterative Hierholzer
            st = [start]
            local = []
            while st:
                v = st[-1]
                advanced = False
                while ptr[v] < len(adj[v]):
                    (w, ei) = adj[v][ptr[v]]
                    ptr[v] += 1
                    if not used[ei]:
                        used[ei] = True
                        st.append(w)
                        advanced = True
                        break
                if not advanced:
                    local.append(st.pop())
            # local is a trail of vertices reversed; build arcs along it
            for a, b in zip(local, local[1:]):
                arcs.append((a, b))
            break
    if not all(used):
        # fallback: not all consumed in one pass; do a clean full pass
        return _orient_full(n, single_edges)
    return arcs


def _orient_full(n, single_edges):
    deg = [0] * n
    if not single_edges:
        return []
    adjL = {v: [] for v in range(n)}
    for i, (u, v) in enumerate(single_edges):
        deg[u] += 1; deg[v] += 1
        adjL[u].append([v, i, False])
        adjL[v].append([u, i, False])
    if any(d % 2 for d in deg):
        return None
    used = [False] * len(single_edges)
    arcs = []
    ptr = {v: 0 for v in range(n)}
    for s in range(n):
        if all(used[ei] for (_, ei, _) in adjL[s]):
            continue
        st = [s]; trail = []
        while st:
            v = st[-1]
            adv = False
            while ptr[v] < len(adjL[v]):
                w, ei, _ = adjL[v][ptr[v]]
                ptr[v] += 1
                if not used[ei]:
                    used[ei] = True
                    st.append(w); adv = True
                    break
            if not adv:
                trail.append(st.pop())
        for a, b in zip(trail, trail[1:]):
            arcs.append((a, b))
    if not all(used):
        return None
    return arcs


def _all_balanced_orientations(n, single_edges, cap_total=64):
    """Yield orientations of single_edges making every vertex in=out (balanced).
    Requires even degree everywhere. For the tight regime each vertex has single-
    degree exactly 2 => the single graph is 2-regular (disjoint cycles); a balanced
    orientation is a choice of direction per cycle. We handle the general even case
    by Euler-decomposing into closed trails and orienting each trail in 2 ways."""
    deg = [0] * n
    for (u, v) in single_edges:
        deg[u] += 1; deg[v] += 1
    if any(d % 2 for d in deg) and single_edges:
        return
    if not single_edges:
        yield []
        return
    # decompose into closed trails (Hierholzer per component)
    adjL = {v: [] for v in range(n)}
    for i, (u, v) in enumerate(single_edges):
        adjL[u].append((v, i)); adjL[v].append((u, i))
    used = [False] * len(single_edges)
    ptr = {v: 0 for v in range(n)}
    trails = []
    for s in range(n):
        while ptr[s] < len(adjL[s]) and used[adjL[s][ptr[s]][1]]:
            ptr[s] += 1
        if ptr[s] >= len(adjL[s]):
            continue
        st = [s]; trail = []
        while st:
            v = st[-1]
            adv = False
            while ptr[v] < len(adjL[v]):
                w, ei = adjL[v][ptr[v]]
                ptr[v] += 1
                if not used[ei]:
                    used[ei] = True
                    st.append(w); adv = True
                    break
            if not adv:
                trail.append(st.pop())
        # trail is a vertex sequence of a closed trail
        if len(trail) >= 2:
            trails.append(trail)
    # safety: if not all used, bail (shouldn't happen for even-degree connected pieces)
    if not all(used):
        return
    ntr = len(trails)
    if 2 ** ntr > cap_total:
        # too many; just yield the canonical (all-forward) orientation
        arcs = []
        for tr in trails:
            for a, b in zip(tr, tr[1:]):
                arcs.append((a, b))
        yield arcs
        return
    for mask in range(2 ** ntr):
        arcs = []
        for ti, tr in enumerate(trails):
            seq = tr if not (mask >> ti) & 1 else tr[::-1]
            for a, b in zip(seq, seq[1:]):
                arcs.append((a, b))
        yield arcs


def arcs_from_M(digon_pairs, single_arcs):
    arcs = []
    for (u, v) in digon_pairs:
        arcs.append((u, v)); arcs.append((v, u))
    arcs.extend(single_arcs)
    return arcs


def _gen_exact_degree_graphs(n, edge_pool, target):
    """Yield simple-edge subsets of edge_pool where each vertex v has degree
    EXACTLY target[v]. Degree-constrained backtracking over the edge pool."""
    if sum(target) % 2 != 0:
        return
    pool = list(edge_pool)
    L = len(pool)
    deg = [0] * n
    chosen = []

    # adjacency of remaining-capacity for feasibility pruning
    def rec(i):
        # all targets met?
        if all(deg[v] == target[v] for v in range(n)):
            yield tuple(chosen)
            return
        if i >= L:
            return
        # feasibility: remaining edges incident to each deficient vertex
        # quick prune: a vertex with deficit but no remaining incident edge fails
        rem_inc = [0] * n
        for j in range(i, L):
            a, b = pool[j]
            rem_inc[a] += 1; rem_inc[b] += 1
        for v in range(n):
            if target[v] - deg[v] > rem_inc[v]:
                return
            if deg[v] > target[v]:
                return
        u, w = pool[i]
        # option 1: take edge i (if both endpoints have capacity)
        if deg[u] < target[u] and deg[w] < target[w]:
            deg[u] += 1; deg[w] += 1
            chosen.append((u, w))
            yield from rec(i + 1)
            chosen.pop()
            deg[u] -= 1; deg[w] -= 1
        # option 2: skip edge i
        yield from rec(i + 1)
    yield from rec(0)


def step_B(nmax=9, nmin=6):
    """Search for disconnected-F_D uniformly-4-edge-connected M with 3-conn
    underlying simple graph. The decisive output is whether any such M, oriented,
    is_2extremal=True."""
    global _RESULTS
    results = {'examined': 0, 'disconnected_FD_M': 0,
               'witness_2extremal': [], 'disconnected_FD_examples': [],
               'by_n': {}}
    _RESULTS = results

    for n in range(nmin, nmax + 1):
        cnt_examined = 0
        cnt_disc = 0
        # All possible simple edges
        all_edges = [(i, j) for i in range(n) for j in range(i + 1, n)]
        # Strategy: choose digon set D (a forest) and single set S (disjoint from D),
        # forming M with cap(D)=2, cap(S)=1. To keep search finite we bound:
        #   - F_D forest must be DISCONNECTED (>=2 comps) to be a candidate Step-1 break
        #   - single edges form the all-single 4-cut crossing components.
        # Enumerate forests F_D (digon graphs). For each disconnected forest,
        # enumerate single-edge sets among remaining edges that make M uniformly
        # 4-edge-connected with 3-conn simple graph.
        #
        # To stay feasible we cap single-edge subset sizes and total degree.
        # Each vertex in uniform-4-edge-conn M has total capacity-degree >= 4.
        forest_iter = gen_path_forests(n, all_edges, maxdeg=2)
        for fd in forest_iter:
            ncomp = fd_components(n, fd)
            if ncomp < 2:
                continue  # we want DISCONNECTED F_D (the Step-1 break candidate)
            fd_set = set(fd)
            remaining = [e for e in all_edges if e not in fd_set]
            # capacity-degree from digons:
            cap_deg_digon = [0] * n
            for (u, v) in fd:
                cap_deg_digon[u] += 2; cap_deg_digon[v] += 2
            # Tight regime: cap-deg exactly 4 everywhere => single-degree of v is
            # EXACTLY target[v] = 4 - 2*digon_deg[v] in {0,2,4}. Generate single
            # graphs with this exact degree sequence (degree-constrained backtracking).
            digon_deg = [cap_deg_digon[v] // 2 for v in range(n)]
            target = [4 - 2 * digon_deg[v] for v in range(n)]
            if any(t < 0 for t in target):
                continue
            # singles drawn from `remaining` (no parallel to digons, simple)
            for singles in _gen_exact_degree_graphs(n, remaining, target):
                # singles automatically: each vertex single-degree == target (even),
                # cap-deg == 4 everywhere.
                simple = set(fd_set) | set(singles)
                if len(simple) < n:
                    continue
                cnt_examined += 1
                results['examined'] += 1
                if cnt_examined % 50000 == 0:
                    print(f"    [n={n}] examined={cnt_examined} disc={cnt_disc}",
                          file=sys.stderr, flush=True)
                cap = {}
                for e in fd_set:
                    cap[e] = 2
                for e in singles:
                    cap[e] = 1
                vals = all_pairwise_cap(n, cap)
                if vals != {4}:
                    continue
                nc = node_connectivity_simple(n, simple)
                if nc < 3:
                    continue
                cnt_disc += 1
                results['disconnected_FD_M'] += 1
                is2e_any = False
                chosen = None
                for orient in _all_balanced_orientations(n, list(singles)):
                    arcs = arcs_from_M(list(fd_set), orient)
                    if H.is_2extremal(n, arcs):
                        is2e_any = True
                        chosen = orient
                        break
                rec = {'n': n, 'fd': [list(e) for e in fd_set],
                       'singles': [list(e) for e in singles],
                       'ncomp_FD': ncomp, 'node_conn': nc,
                       'is_2extremal': is2e_any}
                if chosen is not None:
                    rec['orientation'] = [list(a) for a in chosen]
                if len(results['disconnected_FD_examples']) < 20:
                    results['disconnected_FD_examples'].append(rec)
                if is2e_any:
                    results['witness_2extremal'].append(rec)
        results['by_n'][n] = {'examined': cnt_examined, 'disconnected_FD_M': cnt_disc}
        print(f"  n={n}: examined={cnt_examined} disconnected_FD_uniform4_3conn={cnt_disc} "
              f"witness_2extremal_so_far={len(results['witness_2extremal'])}",
              file=sys.stderr, flush=True)
    return results


_RESULTS = None

if __name__ == '__main__':
    import signal, os
    def handler(signum, frame):
        if _RESULTS is not None:
            r = dict(_RESULTS)
            r['TIMEOUT'] = True
            r['disconnected_FD_examples'] = r.get('disconnected_FD_examples', [])[:5]
            print(json.dumps({'step_B': r}, indent=2))
        else:
            print("TIMEOUT_NO_PARTIAL", flush=True)
        sys.exit(0)
    signal.signal(signal.SIGALRM, handler)
    signal.alarm(int(os.environ.get('XU_ALARM', '560')))

    mode = sys.argv[1] if len(sys.argv) > 1 else 'A'
    if mode == 'A':
        a = step_A()
        print(json.dumps({'step_A': a}, indent=2))
    else:
        nmax = int(sys.argv[2]) if len(sys.argv) > 2 else 9
        nmin = int(sys.argv[3]) if len(sys.argv) > 3 else 6
        b = step_B(nmax, nmin)
        # summarize
        b['disconnected_FD_examples'] = b['disconnected_FD_examples'][:5]
        print(json.dumps({'step_B': b}, indent=2))
