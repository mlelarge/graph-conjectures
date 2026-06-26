"""Min-over-OPTIMAL-orders alpha(backedge graph) for AC_17 (P10 witness).

GROUNDS the literature-reduction proposal (D6):
  AC_17 = Cay(Z/17, g={1,2,3,4,5,6,7,9}), omega_vec = 3.
  An OPTIMAL order has backedge graph G with omega(G) = 3 (= omega_vec).
  Question: min over such optimal orders of alpha(G).

  Ramsey fact (R(4,4)=18, McKay-Radziszowski 1995 uniqueness):
    a graph on 17 vertices with omega=3 AND alpha<=3 is forced iso to Paley(17).
  So min-optimal-order alpha = 3  IFF  some order's backedge graph ~ Paley(17).

Search: branch-and-bound over total orders.  Backedge-graph edges among already
PLACED vertices are FINAL (an edge a-c is fixed once both a,c are placed; a later
vertex b adds edges b-a iff arc b->a).  Hence omega(placed) is monotone
non-decreasing -> prune any prefix whose placed backedge graph already has a K4
(omega>=4): it can never be an optimal (omega=3) order.

AC_17 is vertex-transitive (rotation x->x+1), so the global min over orders is
attained by an order starting at vertex 0 -> fix first vertex 0 (SOUND symmetry
reduction, same one used for the P10 lower bound).

At each completed (omega=3) order we compute alpha(G) exactly and track the min.
We EARLY-EXIT as soon as alpha<=3 is achieved (the discriminating value): if found,
CONFIRM branch (alpha=3 attainable, route pinned at Ramsey ceiling); if the whole
(pruned) tree is exhausted with min alpha > 3, KILL branch (alpha>3 forced).
"""
import sys, os, time
sys.path.insert(0, os.path.dirname(__file__))
import core
import networkx as nx


def build_ac17():
    p = 17
    g = (1, 2, 3, 4, 5, 6, 7, 9)
    arcs = [(i, (i + d) % p) for i in range(p) for d in g]
    assert core.is_tournament(p, arcs)
    return p, g, arcs


def has_k4_with(adj, nb):
    """True iff adding a vertex whose placed-neighbour set is `nb` (bitmask)
    creates a K4: i.e. nb contains a TRIANGLE in the current placed graph.
    `adj[x]` = bitmask of placed neighbours of x.  A triangle inside nb means
    three vertices x,y,z in nb pairwise adjacent. Equivalent: exists x in nb with
    (adj[x] & nb) containing an edge, i.e. exists y in (adj[x]&nb) with adj[y]&adj[x]&nb.
    """
    m = nb
    while m:
        x = (m & -m).bit_length() - 1
        m &= m - 1
        common = adj[x] & nb            # placed nbrs of x that are also nbrs of new vtx
        c = common
        while c:
            y = (c & -c).bit_length() - 1
            c &= c - 1
            if adj[y] & common:         # x,y adjacent (y in common) and share a third in common
                return True
    return False


def alpha_of(adj_list, n):
    """Exact independence number of the placed (complete) backedge graph."""
    g = nx.Graph()
    g.add_nodes_from(range(n))
    for v in range(n):
        a = adj_list[v]
        while a:
            u = (a & -a).bit_length() - 1
            a &= a - 1
            if u > v:
                g.add_edge(v, u)
    comp = nx.complement(g)
    return max((len(c) for c in nx.find_cliques(comp)), default=1)


def search(p, arcs, fixed_first=0, time_budget=900.0, alpha_target=3):
    """Enumerate omega<=3 total orders (prefix-pruned on K4), minimize alpha.
    Early-exit when alpha <= alpha_target found. Returns dict of results."""
    bm = core.beats_matrix(p, arcs)
    bdown = [0] * p
    for b in range(p):
        for a in range(p):
            if bm[b][a]:
                bdown[b] |= (1 << a)
    full = (1 << p) - 1
    adj = [0] * p
    start = time.time()
    state = {"min_alpha": p + 1, "best_order": None, "leaves": 0,
             "found_le_target": False, "timed_out": False, "nodes": 0}

    placed_order = []

    def dfs(placed_mask):
        if state["found_le_target"]:
            return
        if time.time() - start > time_budget:
            state["timed_out"] = True
            return
        state["nodes"] += 1
        if placed_mask == full:
            state["leaves"] += 1
            a = alpha_of(adj, p)
            if a < state["min_alpha"]:
                state["min_alpha"] = a
                state["best_order"] = list(placed_order)
            if a <= alpha_target:
                state["found_le_target"] = True
            return
        remaining = full & ~placed_mask
        r = remaining
        while r:
            b = (r & -r).bit_length() - 1
            r &= r - 1
            nb = bdown[b] & placed_mask
            # prune: placing b must not create a K4 among placed (omega would hit 4)
            if has_k4_with(adj, nb):
                continue
            bbit = 1 << b
            mm = nb
            while mm:
                a = (mm & -mm).bit_length() - 1
                mm &= mm - 1
                adj[a] |= bbit
            adj[b] = nb
            placed_order.append(b)
            dfs(placed_mask | bbit)
            placed_order.pop()
            mm = nb
            while mm:
                a = (mm & -mm).bit_length() - 1
                mm &= mm - 1
                adj[a] &= ~bbit
            adj[b] = 0
            if state["found_le_target"] or state["timed_out"]:
                return

    adj[fixed_first] = 0
    placed_order.append(fixed_first)
    dfs(1 << fixed_first)
    state["elapsed"] = time.time() - start
    return state


def backedge_graph_of_order(p, arcs, order):
    bm = core.beats_matrix(p, arcs)
    pos = [0] * p
    for idx, v in enumerate(order):
        pos[v] = idx
    g = nx.Graph()
    g.add_nodes_from(range(p))
    for a in range(p):
        for b in range(a + 1, p):
            u, w = (a, b) if pos[a] < pos[b] else (b, a)
            if bm[w][u]:
                g.add_edge(a, b)
    return g


def paley17_graph():
    p = 17
    QR = {pow(x, 2, p) for x in range(1, p)}  # {1,2,4,8,9,13,15,16}
    g = nx.Graph()
    g.add_nodes_from(range(p))
    for i in range(p):
        for j in range(i + 1, p):
            if (i - j) % p in QR:
                g.add_edge(i, j)
    return g


def main():
    p, gen, arcs = build_ac17()
    print(f"=== alpha-min over OPTIMAL orders of AC_17 = Cay(Z/17,{list(gen)}) ===", flush=True)
    budget = float(os.environ.get("BUDGET", "780"))
    print(f"time_budget={budget}s  fixed_first=0 (vertex-transitive, sound)", flush=True)
    st = search(p, arcs, fixed_first=0, time_budget=budget, alpha_target=3)
    print(f"nodes={st['nodes']}  optimal(omega=3)_leaves={st['leaves']}  "
          f"elapsed={st['elapsed']:.1f}s  timed_out={st['timed_out']}", flush=True)
    print(f"MIN alpha over optimal orders found so far = {st['min_alpha']}", flush=True)
    print(f"found order with alpha<=3 : {st['found_le_target']}", flush=True)

    verdict = None
    if st["found_le_target"] and st["best_order"] is not None:
        G = backedge_graph_of_order(p, arcs, st["best_order"])
        om = max((len(c) for c in nx.find_cliques(G)), default=1)
        al = max((len(c) for c in nx.find_cliques(nx.complement(G))), default=1)
        P = paley17_graph()
        iso = nx.is_isomorphic(G, P)
        print(f"\nWITNESS order achieving alpha<=3: {st['best_order']}", flush=True)
        print(f"  backedge graph: omega={om}, alpha={al}, edges={G.number_of_edges()}", flush=True)
        print(f"  Paley(17) edges={P.number_of_edges()}", flush=True)
        print(f"  is_isomorphic(backedge, Paley17) = {iso}", flush=True)
        verdict = "CONFIRM (alpha=3 attainable; Ramsey ceiling)"
    elif not st["timed_out"]:
        print(f"\nEXHAUSTED omega=3 order tree (no timeout): alpha > 3 FORCED.", flush=True)
        print(f"  min optimal-order alpha = {st['min_alpha']} (> 3).", flush=True)
        verdict = "KILL (alpha>3 forced; alpha<=3 cap vacuous at 17)"
    else:
        print(f"\nTIMED OUT before exhaustion and before finding alpha<=3.", flush=True)
        verdict = "INCONCLUSIVE (timed out)"
    print(f"\nVERDICT: {verdict}", flush=True)
    return st, verdict


if __name__ == "__main__":
    main()
