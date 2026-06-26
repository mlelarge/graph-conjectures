"""G22: Grotzsch-seeded backward-blowup attack on m(4)<=209.

Build Grotzsch graph M4 (Mycielskian of C5): 11 vertices, triangle-free, chi=4, alpha=5.
Pick orientations of it; form t-backward-blowup (D25 pattern):
  vid(x,j) = x*t + j
  for each ARC (x,y): forward x_j -> y_j' for j!=j', plus matched backward y_j -> x_j.
Ask oracle whether ANY (orientation, t<=18) backward-blowup is non-3-dicolourable.
A non-3-dicolourable witness at t<=18 -> n=11t<=198 < 209 beats m(4)<=209.
"""
import os, sys, signal, random, itertools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import core

# ---- Grotzsch graph = Mycielskian of C5 ----
def grotzsch_edges():
    # C5 on 0..4, edges i~i+1 mod5
    C5 = [(i, (i+1) % 5) for i in range(5)]
    edges = set()
    for (a, b) in C5:
        edges.add(frozenset((a, b)))
    # shadow u_i = 5+i adjacent to the two C5-neighbours of v_i
    for i in range(5):
        ui = 5 + i
        for nb in ((i-1) % 5, (i+1) % 5):
            edges.add(frozenset((ui, nb)))
    # apex 10 adjacent to all u_i
    for i in range(5):
        edges.add(frozenset((10, 5 + i)))
    return [tuple(sorted(e)) for e in edges]

GROTZSCH = grotzsch_edges()  # undirected edges of 11-vertex graph

def backward_blowup(orient, t):
    """orient: list of directed arcs (x,y) on the 11-vertex base.
    Return arc list on n=11*t."""
    def vid(x, j):
        return x * t + j
    arcs = []
    for (x, y) in orient:
        for j in range(t):
            for jp in range(t):
                if j != jp:
                    arcs.append((vid(x, j), vid(y, jp)))   # forward off-diagonal
            arcs.append((vid(y, j), vid(x, j)))            # matched backward
    return arcs

# ---- per-instance timeout via fork ----
def call_with_timeout(fn, timeout_s):
    pid = os.fork()
    if pid == 0:
        # child
        r, w = (None, None)
        try:
            res = fn()
            os._exit(0 if res else 1)   # encode bool result in exit code
        except Exception:
            os._exit(2)
    else:
        import time
        t0 = time.time()
        while True:
            wpid, status = os.waitpid(pid, os.WNOHANG)
            if wpid == pid:
                if os.WIFEXITED(status):
                    code = os.WEXITSTATUS(status)
                    if code == 0:
                        return True
                    if code == 1:
                        return False
                    return None
                return None
            if time.time() - t0 > timeout_s:
                try:
                    os.kill(pid, signal.SIGKILL)
                    os.waitpid(pid, 0)
                except Exception:
                    pass
                return "TIMEOUT"
            time.sleep(0.05)

def main():
    random.seed(0)
    # verify base graph
    base_arcs_check = [(a, b) for (a, b) in GROTZSCH]  # arbitrary orient just for tri-free check
    n11 = 11
    print("Grotzsch: |V|=11, |E|=%d" % len(GROTZSCH))
    print("triangle_free(base):", core.is_triangle_free(n11, base_arcs_check))
    print("chi(base undirected) via dichromatic of symmetric? skip; use alpha")
    # alpha + chi of undirected: use oracle dichromatic on the *symmetric* digraph is not it.
    # Just trust ledger anchor; but verify chi=4 by undirected colouring quickly.
    import networkx as nx
    G = nx.Graph(); G.add_nodes_from(range(11)); G.add_edges_from(GROTZSCH)
    # chromatic number by brute (11 vtx small)
    def chromatic(G):
        import networkx.algorithms.coloring as col
        for k in range(1, 12):
            # try greedy exact via ILP-free backtracking
            if _kcolourable(G, k):
                return k
        return 11
    def _kcolourable(G, k):
        nodes = list(G.nodes()); colour = {}
        def bt(i):
            if i == len(nodes): return True
            v = nodes[i]
            used = {colour[u] for u in G.neighbors(v) if u in colour}
            for c in range(k):
                if c not in used:
                    colour[v] = c
                    if bt(i+1): return True
                    del colour[v]
            return False
        return bt(0)
    chi = chromatic(G)
    alpha = max((len(s) for s in _independent_sets(G)), default=0)
    print("chi(Grotzsch) =", chi, " alpha(Grotzsch) =", alpha)

    # build orientations
    edges = GROTZSCH
    orientations = {}
    # acyclic / topological: orient low->high
    orientations["acyclic_lohi"] = [(a, b) for (a, b) in edges]
    # 30 random
    for s in range(30):
        rnd = random.Random(100 + s)
        orientations["rand%d" % s] = [ (a, b) if rnd.random() < 0.5 else (b, a) for (a, b) in edges ]
    # Eulerian/balanced near-regular: orient to balance out-degrees greedily
    orientations["balanced"] = _balanced_orientation(edges, 11)

    TIMEOUT = 120
    results = []
    found = []  # (n, t, oname)
    # descend t from 18 to 2 (smallest-n threshold search; but to find ANY beat we test all)
    # We test t from small to large is cheaper; but proposal wants smallest n. Test 2..18.
    for t in range(2, 19):
        n = 11 * t
        any_nondicol = False
        for oname, orient in orientations.items():
            arcs = backward_blowup(orient, t)
            if not core.is_oriented(arcs):
                results.append((t, oname, "NOT_ORIENTED"))
                continue
            if not core.is_triangle_free(n, arcs):
                results.append((t, oname, "NOT_TRIFREE"))
                continue
            res = call_with_timeout(lambda a=arcs, nn=n: core.is_k_dicolourable(nn, a, 3), TIMEOUT)
            tag = {True: "3DICOL", False: "NON3DICOL", "TIMEOUT": "TIMEOUT", None: "ERR"}[res]
            results.append((t, oname, tag))
            print("t=%2d n=%3d %-12s -> %s" % (t, n, oname, tag), flush=True)
            if res is False:
                found.append((n, t, oname))
                any_nondicol = True
        if found:
            break  # found a beat; stop at smallest t
    print("\n=== SUMMARY ===")
    if found:
        n, t, oname = min(found)
        print("BEAT: non-3-dicolourable at n=%d (t=%d, %s) < 209" % (n, t, oname))
    else:
        # tally
        from collections import Counter
        c = Counter(tag for (_, _, tag) in results)
        print("NO BEAT. All (orientation,t in 2..18) outcomes:", dict(c))
    # print full table for the record
    print("FULL:", results[:200])

def _independent_sets(G):
    import networkx as nx
    comp = nx.complement(G)
    import networkx.algorithms.clique as clq
    return nx.find_cliques(comp)

def _balanced_orientation(edges, n):
    out = [0]*n; arcs=[]
    for (a, b) in sorted(edges):
        if out[a] <= out[b]:
            arcs.append((a, b)); out[a]+=1
        else:
            arcs.append((b, a)); out[b]+=1
    return arcs

if __name__ == "__main__":
    main()
