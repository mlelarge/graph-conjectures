"""H3 LOWER lever: attempt to lift m(3) >= 18 -> >= 19 by reproducing the
paper's Lemma 4.7 graph-level (orientation-free) 2-dicolourability certificate
at n=18 (the paper stopped at n=17 only for enumeration time).

Procedure faithfully follows arXiv:2403.02298 Sec 4.4 (l.1115-1133):
  - Enumerate biconnected triangle-free graphs with min-degree >= 4,
    max-degree <= n-9, arboricity >= 3  (the only candidate skeletons for a
    3-dicritical object; everything else trivially decomposes).
  - For each, build (X,Y) by the paper's greedy: X={u}, Y=N(u), absorb into X
    every u' with N(u') subset of N(u); maximise |X|+|Y| over u.
  - Z = V \ (X u Y). Accept (certificate) iff condition (iv) holds:
       #{z in Z : deg_{G[Z]}(z) >= 2} <= 8,
       and when the reduced G[Z] (delete degree-1 vertices, iterate) has exactly
       8 such vertices it is not a Lemma 4.9 exception.
    The paper proves (iv) suffices because such a Z is 2-dicolourable with the
    colour-1 class being empty / a single vertex / two adjacent vertices
    (Lemma 4.8 for <=7 deg>=2 vertices, Lemma 4.9 for 8).

If EVERY n=18 candidate passes => m(3) >= 19 (graph-level, all orientations at
once). If one FAILS => the reduction does not lift the bound at n=18.

Also runs the AES premise gate and an oracle sanity cross-check.
"""
from __future__ import annotations
import sys, os, subprocess, itertools, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import networkx as nx
import core

GENG = "/opt/homebrew/bin/geng"


def arboricity_ge(g, k):
    """True iff Nash-Williams arboricity >= k, i.e. some subgraph H has
    e(H) > (k-1)(v(H)-1).  We check the densest subgraph via the max-density
    test: arboricity = max_H ceil(e(H)/(v(H)-1)).  For small graphs we use the
    exact Nash-Williams criterion through a maximum-density subgraph search.
    For k=3 we need a subgraph with e(H) >= 2*(v(H)-1)+1 = 2 v(H) -1.
    Use networkx's maximal density via repeated densest-subgraph (exact small).
    """
    # exact for small n: arboricity = max over connected subgraphs.
    # Cheap sufficient/necessary: use the global bound first.
    n = g.number_of_nodes()
    # Nash-Williams: arboricity(G) = max_{H subgraph, |V(H)|>=2} ceil(e(H)/(|V(H)|-1))
    # We compute max density d* = max_H e(H)/(v(H)-1) exactly via the
    # parametric maxflow / Goldberg densest-subgraph reduction would be overkill;
    # for n<=18 we use networkx's `nx.maximal_independent_set`? No.
    # Use the LP-free exact via subgraph density using the "densest subgraph"
    # Goldberg algorithm implemented through min-cut.
    best = 0.0
    # Goldberg densest subgraph (maximize e(H)/v(H)) gives a good handle but we
    # need e/(v-1). Just do an exact check using max-flow parametric search over
    # the threshold k-1 = 2: G has arboricity >= 3 iff exists subgraph with
    # e(H) - 2*(v(H)) > -2, i.e. e(H) > 2 v(H) - 2.  Test via the matroid-union
    # / orientation criterion: arboricity <= k iff G admits an orientation with
    # max in-degree <= k (Hakimi). Equivalent: every subgraph e(H) <= k(v(H)-1).
    # So arboricity >= 3 iff NOT (every subgraph has e(H) <= 2(v(H)-1)).
    # The maximum of e(H) - 2(v(H)-1) over subgraphs is found by a min-cut.
    return _max_excess(g, 2) > 0


def _max_excess(g, k):
    """max over nonempty vertex subsets S of  e(G[S]) - k*(|S|-1) ... but we
    want existence of H with e(H) > k(v(H)-1). Equivalent: max_S e(G[S]) -
    k*|S| > -k. We compute max_S (e(G[S]) - k|S|) via the standard
    densest-subgraph min-cut (Goldberg) parametric trick, but since k is fixed
    we can directly solve: maximize sum_{edges in S} 1 - k * |S|.
    Build flow network: source->edge cap 1; edge->its 2 endpoints cap inf;
    vertex->sink cap k. Max profit = (#edges) - mincut. If profit - (-k) ...
    We instead return max_S (e(G[S]) - k*(|S|-1)). Existence of arboricity>=k+1
    iff this max > 0 for some S with |S|>=2.
    """
    import networkx as nx
    m = g.number_of_edges()
    if m == 0:
        return -10**9
    F = nx.DiGraph()
    S, T = "s", "t"
    INF = float("inf")
    for i, (u, v) in enumerate(g.edges()):
        e = ("e", i)
        F.add_edge(S, e, capacity=1.0)
        F.add_edge(e, ("v", u), capacity=INF)
        F.add_edge(e, ("v", v), capacity=INF)
    for v in g.nodes():
        F.add_edge(("v", v), T, capacity=float(k))
    cut_val, (reach, _) = nx.minimum_cut(F, S, T)
    # selected vertices = those on source side
    Ssel = [v for (tag, v) in ((n[0], n[1]) for n in reach if isinstance(n, tuple) and n[0] == "v")]
    if len(Ssel) < 2:
        return -10**9
    sub = g.subgraph(Ssel)
    return sub.number_of_edges() - k * (len(Ssel) - 1)


# ---- Lemma 4.9 exception list (on the deg>=2 reduced graph, 8 vertices) ----
def _is_lemma49_exception(h):
    """h is an undirected simple graph on exactly 8 vertices, all degrees >= 2
    (after reduction). Return True iff h is (the underlying graph of) one of the
    Lemma 4.9 exceptions: two disjoint 4-cycles, the cube, the cube with two
    diagonals, K4,4, K4,4 minus an edge, the K4,4-subgraph with degree sequence
    (2,2,4,4)+(3,3,3,3). We test by isomorphism to these underlying graphs.
    NOTE: Lemma 4.9 exceptions are *digraphs*; condition (iv) failing requires
    the orientation to actually be a bad one, but the paper's GRAPH-level check
    is conservative: it flags G[Z] as "potentially bad" iff its underlying graph
    is one of these. We replicate that conservative graph-level test.
    """
    ex = []
    # two disjoint C4
    g1 = nx.Graph(); g1.add_edges_from([(0,1),(1,2),(2,3),(3,0),(4,5),(5,6),(6,7),(7,4)])
    ex.append(g1)
    # cube Q3
    cube = nx.hypercube_graph(3); cube = nx.convert_node_labels_to_integers(cube)
    ex.append(cube)
    # cube with two diagonals: add two "diagonals" (antipodal pairs). The cube
    # has 4 antipodal pairs; "two diagonals" = add 2 of them.
    cd = cube.copy()
    # antipodal pairs in integer-labeled hypercube: find by complementary bits
    H = nx.hypercube_graph(3); H = nx.convert_node_labels_to_integers(H, label_attribute="bits")
    # just add two arbitrary non-edges that are distance-3 (antipodal)
    sp = dict(nx.all_pairs_shortest_path_length(cube))
    anti = [(u, v) for u in cube for v in cube if u < v and sp[u][v] == 3]
    cd.add_edges_from(anti[:2])
    ex.append(cd)
    # K4,4
    k44 = nx.complete_bipartite_graph(4, 4)
    ex.append(k44)
    # K4,4 minus an edge
    k44e = k44.copy(); k44e.remove_edge(0, 4)
    ex.append(k44e)
    # K4,4 subgraph with degree sequence (2,2,4,4),(3,3,3,3): the paper lists a
    # specific bipartite graph. Build a bipartite graph with one side degrees
    # (2,2,4,4) and other side (3,3,3,3), 12 edges. Construct explicitly.
    g6 = nx.Graph()
    left = [0,1,2,3]; right=[4,5,6,7]
    # degrees left: 2,2,4,4 ; right all 3 -> total edges 12
    # vertices 2,3 connect to all of right (degree 4). vertices 0,1 degree 2.
    g6.add_edges_from([(2,r) for r in right])
    g6.add_edges_from([(3,r) for r in right])
    # right now each has degree 2; need degree 3 each -> add 4 more edges from
    # {0,1} (degree 2 each). 0->{4,5}, 1->{6,7} gives right degrees 3,3,3,3.
    g6.add_edges_from([(0,4),(0,5),(1,6),(1,7)])
    ex.append(g6)
    for e in ex:
        if e.number_of_nodes() == 8 and nx.is_isomorphic(h, e):
            return True
    return False


def reduce_deg1(h):
    """Iteratively delete degree-<=1 vertices; return the reduced graph."""
    h = h.copy()
    changed = True
    while changed:
        changed = False
        for v in list(h.nodes()):
            if h.degree(v) <= 1:
                h.remove_node(v); changed = True
    return h


def lemma47_certificate(n, edges):
    """Return (ok, info). ok=True iff (X,Y,Z) decomposition satisfies (i)-(iv)
    under the paper's greedy construction (graph-level, orientation-free)."""
    g = nx.Graph(); g.add_nodes_from(range(n)); g.add_edges_from(edges)
    # Build all candidate (X,Y) per the paper's greedy (one per starting vertex
    # u), then take those of MAXIMUM |X|+|Y|.  When several attain the maximum,
    # the certificate succeeds if ANY of them yields a Z satisfying (iv): the
    # paper's "kept the couple (X,Y) for which |X|+|Y| is maximised" allows a
    # best-of-the-maximisers reading, and a valid decomposition existing is what
    # makes the graph 2-dicolourable.
    cands = []
    for u in range(n):
        Nu = set(g.neighbors(u))
        X = {u}
        for w in range(n):
            if w == u or w in Nu:
                continue
            if set(g.neighbors(w)) <= Nu:
                X.add(w)
        Y = Nu - X
        cands.append((len(X) + len(Y), frozenset(X), frozenset(Y)))
    best_score = max(c[0] for c in cands)
    opt = [(X, Y) for (s, X, Y) in cands if s == best_score]
    # evaluate each optimal decomposition; accept on the first that satisfies all
    chosen = None
    chosen_info = None
    for X, Y in opt:
        X = set(X); Y = set(Y)
        Z = set(range(n)) - X - Y
        ok_, info_ = _eval_decomp(g, X, Y, Z)
        if chosen is None:
            chosen = (X, Y, Z); chosen_info = (ok_, info_)
        if ok_:
            chosen = (X, Y, Z); chosen_info = (ok_, info_)
            break
    X, Y, Z = chosen
    ok, info = chosen_info
    return ok, info, (g, X, Y, Z)


def lemma47_certificate_enriched(n, edges):
    """Paper-FAITHFUL certificate: in addition to the single-vertex greedy, also
    try X = {u,w} for every edge uw (Lemma 4.7(i)/Lemma 4.8 explicitly allow X
    to be a single vertex OR two adjacent vertices), absorb v with N(v) subset of
    the current Y, and accept if ANY (X,Y) over ALL seeds yields a Z meeting (iv).
    This is the construction the paper's n<=17 PASS_ALL actually relies on."""
    g = nx.Graph(); g.add_nodes_from(range(n)); g.add_edges_from(edges)
    seeds = []
    for u in range(n):
        seeds.append(({u}, set(g.neighbors(u))))
    for (u, w) in g.edges():
        base = (set(g.neighbors(u)) | set(g.neighbors(w))) - {u, w}
        seeds.append(({u, w}, base))
    best_ok = False
    best_info = None
    for X0, Y0 in seeds:
        X = set(X0)
        for v in range(n):
            if v in X or v in Y0:
                continue
            if set(g.neighbors(v)) <= Y0:
                X.add(v)
        Y = Y0 - X
        Z = set(range(n)) - X - Y
        # require X to induce a forest (so D[X] acyclic for every orientation;
        # a 2-adjacent-vertex seed plus absorbed leaves stays a forest in the
        # triangle-free regime, but verify to be safe)
        if not nx.is_forest(g.subgraph(X)):
            continue
        if g.subgraph(Y).number_of_edges() != 0:
            continue
        if any(g.has_edge(x, z) for x in X for z in Z):
            continue
        ok_, info_ = _eval_decomp(g, X, Y, Z)
        if best_info is None:
            best_info = info_
        if ok_:
            return True, info_
    return False, (best_info or {})


def _eval_decomp(g, X, Y, Z):
    n = g.number_of_nodes()
    # (i) D[X] acyclic for every orientation iff G[X] has no... acyclic for ALL
    #     orientations requires G[X] to be a forest? No: condition (i) is on the
    #     DIGRAPH D[X]. The graph-level certificate needs X independent (then
    #     D[X] has no arcs => acyclic). The paper notes X,Y are independent sets.
    Xind = g.subgraph(X).number_of_edges() == 0
    Yind = g.subgraph(Y).number_of_edges() == 0
    # (iii) no edge between X and Z
    no_XZ = not any(g.has_edge(x, z) for x in X for z in Z)
    # (iv) #{z in Z: deg_{G[Z]}(z) >= 2} <= 8 and reduced not Lemma4.9 exception
    gz = g.subgraph(Z).copy()
    gz = nx.convert_node_labels_to_integers(gz)
    deg_ge2 = sum(1 for v in gz if gz.degree(v) >= 2)
    red = reduce_deg1(gz)
    nred = red.number_of_nodes()
    cond_iv = False
    exception_flag = None
    if deg_ge2 <= 7:
        cond_iv = True
    elif deg_ge2 == 8:
        red8 = nx.convert_node_labels_to_integers(red)
        if red8.number_of_nodes() == 8:
            exception_flag = _is_lemma49_exception(red8)
            cond_iv = not exception_flag
        elif red8.number_of_nodes() < 8:
            # reduced below 8 deg>=2 vertices -> Lemma 4.8 territory
            cond_iv = True
        else:
            cond_iv = False
    else:
        cond_iv = False
    ok = Xind and Yind and no_XZ and cond_iv
    info = dict(sizeX=len(X), sizeY=len(Y), sizeZ=len(Z), Xind=Xind, Yind=Yind,
                no_XZ=no_XZ, deg_ge2=deg_ge2, nred=nred, cond_iv=cond_iv,
                exception=exception_flag)
    return ok, info


def aes_premise_check(n, dmin=8):
    """Verify every triangle-free graph on n vertices with min-degree >= dmin is
    bipartite (so non-bipartite candidates have min-deg < dmin)."""
    proc = subprocess.Popen([GENG, "-t", f"-d{dmin}", str(n)],
                            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                            text=True)
    total = nonbip = 0
    witnesses = []
    for line in proc.stdout:
        line = line.strip()
        if not line:
            continue
        nn, edges = core._graph6_to_edges(line)
        g = nx.Graph(); g.add_nodes_from(range(nn)); g.add_edges_from(edges)
        total += 1
        if not nx.is_bipartite(g):
            nonbip += 1
            witnesses.append(line)
    proc.wait()
    return total, nonbip, witnesses


def enumerate_and_check(n, maxdeg=None, mindeg=4):
    if maxdeg is None:
        maxdeg = n - 9
    cmd = [GENG, "-tC", f"-d{mindeg}", f"-D{maxdeg}", str(n)]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                            stderr=subprocess.DEVNULL, text=True)
    total = arb3 = passed = fail_count = 0
    enr_pass = enr_fail = 0
    fails = []          # literal (proposal single-vertex greedy) fails
    enr_fails = []      # paper-faithful enriched fails
    pass_graphs = []
    for line in proc.stdout:
        line = line.strip()
        if not line:
            continue
        nn, edges = core._graph6_to_edges(line)
        g = nx.Graph(); g.add_nodes_from(range(nn)); g.add_edges_from(edges)
        total += 1
        if not arboricity_ge(g, 3):
            continue
        arb3 += 1
        ok, info, _ = lemma47_certificate(nn, edges)
        if ok:
            passed += 1
            if len(pass_graphs) < 5:
                pass_graphs.append((line, edges))
        else:
            fail_count += 1
            if len(fails) < 50:
                fails.append((line, info))
        # paper-faithful enriched certificate
        eok, einfo = lemma47_certificate_enriched(nn, edges)
        if eok:
            enr_pass += 1
        else:
            enr_fail += 1
            if len(enr_fails) < 50:
                enr_fails.append((line, einfo))
    proc.wait()
    return dict(total=total, arb3=arb3, passed=passed, fails=fails,
                fail_count=fail_count, enr_pass=enr_pass, enr_fail=enr_fail,
                enr_fails=enr_fails, pass_graphs=pass_graphs,
                cmd=" ".join(cmd))


def oracle_sanity(pass_graphs, n, seeds=3):
    """For a few PASS graphs and random orientations, confirm 2-dicolourable."""
    rng = random.Random(12345)
    results = []
    for line, edges in pass_graphs[:3]:
        for s in range(seeds):
            arcs = []
            for (u, v) in edges:
                if rng.random() < 0.5:
                    arcs.append((u, v))
                else:
                    arcs.append((v, u))
            two = core.is_k_dicolourable(n, arcs, 2)
            results.append((line, s, two))
    return results


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 18
    print(f"=== H3 LOWER lever, n={n} ===")

    print("\n[Step 1] AES premise: triangle-free, min-deg>=8 graphs all bipartite?")
    total, nonbip, wit = aes_premise_check(n, dmin=8)
    print(f"  geng -t -d8 {n}: total={total}, non-bipartite={nonbip}")
    if nonbip > 0:
        print("  AES PREMISE FALSE -- witnesses:", wit[:3])
    else:
        print("  AES premise holds: non-bipartite candidates have min-deg <= 7.")

    print(f"\n[Step 2-3] Enumerate biconnected tri-free min-deg>=4 max-deg<={n-9} "
          f"arboricity>=3, run Lemma 4.7 greedy certificate")
    res = enumerate_and_check(n)
    print("  cmd:", res["cmd"])
    print(f"  total biconnected candidates: {res['total']}")
    print(f"  arboricity>=3 survivors:      {res['arb3']}")
    print(f"  [LITERAL single-vertex greedy = proposal's ground_plan Step 3]")
    print(f"    PASS: {res['passed']}   FAIL: {res['fail_count']}")
    for line, info in res["fails"][:8]:
        print("      FAIL graph6:", line, info)
    print(f"  [ENRICHED paper-faithful (1- and 2-adjacent-vertex X seeds)]")
    print(f"    PASS: {res['enr_pass']}   FAIL: {res['enr_fail']}")
    for line, info in res["enr_fails"][:8]:
        print("      ENR-FAIL graph6:", line, info)
    if res["enr_fail"] == 0 and res["arb3"] > 0:
        print(f"  RESULT: PASS_ALL (enriched) at n={n} -> paper certificate "
              f"reproduced => m(3) >= {n+1}")
    elif res["arb3"] > 0:
        print(f"  RESULT: enriched certificate has {res['enr_fail']} FAILs at "
              f"n={n} -> does NOT lift m(3); these graphs need orientation check")

    print("\n[Step 4] Oracle sanity on PASS graphs (random orientations 2-dicolourable?)")
    sane = oracle_sanity(res["pass_graphs"], n)
    for line, s, two in sane:
        print(f"  {line} seed{s}: is_2_dicolourable={two}")
    if sane and not all(t for _, _, t in sane):
        print("  WARNING: a PASS graph had a non-2-dicolourable orientation!!")
