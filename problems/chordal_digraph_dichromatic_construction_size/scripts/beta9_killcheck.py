"""Fast SOUND decision of the falsifiable prediction's KILL threshold at n=9.

Falsifiable prediction:
  CONFIRM  if beta*(9) = min_{D in C_3,|D|=9} alpha(D)/9  >= ~0.5
  KILL     if beta*(9) drops below ~0.45  (concretely beta < 0.45).

The KILL boundary on n=9 is exactly alpha=4: 4/9 = 0.444 < 0.45, while
5/9 = 0.556 >= 0.5.  So the prediction is decided by ONE yes/no question:

    Does there exist a C_3 digraph on 9 vertices with acyclic_number <= 4 ?

We answer it WITHOUT computing exact alpha for all 12.6M digraphs, using a
cheap sound test:  alpha(D) >= 5  iff D has SOME induced acyclic vertex set of
size 5.  An induced vertex subset S is acyclic iff the subdigraph D[S] has no
directed cycle.  So for each C_3 digraph we just look for ANY 5-subset whose
induced subdigraph is acyclic; the first one found certifies alpha >= 5 and we
move on (no MaxSAT).  Only if NO acyclic 5-set exists do we have a KILL witness
(alpha <= 4), which we then CONFIRM with the exact oracle core.acyclic_number.

Soundness:
  * connected + K4-free base-graph restriction: identical to the validated
    beta8_scan / m3_lb_scan_n9 recipe (min ratio attained on a connected base
    graph; every K4 carries a TT3 so K4-free is lossless for C_3).
  * "has acyclic induced 5-set => alpha >= 5" is exact (alpha is the MAX acyclic
    induced set size).  "no acyclic induced 5-set => alpha <= 4" is exact too.
  * Enumerating C_3 members reuses the SAME early-TT3 backtracking generator
    validated set-equal to all_orientations at n=5,6 (counts 2186/25258/479168).

Result:
  * If the scan finds NO C_3 digraph with alpha<=4  ->  beta*(9) >= 5/9 = 0.556
    >= 0.5  ->  prediction CONFIRMED at n=9 (no drift below 0.45).
  * If it finds one  ->  KILL witness, beta*(9) <= 4/9 = 0.444 < 0.45.
"""
import sys, os, time, itertools, argparse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import core
import networkx as nx
from multiprocessing import Pool

N = 9


def has_k4(n, edges):
    G = nx.Graph()
    G.add_nodes_from(range(n))
    G.add_edges_from(edges)
    adj = {v: set(G[v]) for v in G}
    for quad in itertools.combinations(range(n), 4):
        s = set(quad)
        if all(len((adj[v] | {v}) & s) == 4 for v in quad):
            return True
    return False


def _creates_tt3(u, v, out, inn):
    if out[v] & out[u]:
        return True
    if inn[u] & inn[v]:
        return True
    if out[u] & inn[v]:
        return True
    return False


def _orient(edges, n):
    m = len(edges)
    out = [set() for _ in range(n)]
    inn = [set() for _ in range(n)]
    chosen = [None] * m

    def rec(i):
        if i == m:
            yield tuple(chosen)
            return
        a, b = edges[i]
        for (u, v) in ((a, b), (b, a)):
            if _creates_tt3(u, v, out, inn):
                continue
            out[u].add(v); inn[v].add(u)
            chosen[i] = (u, v)
            yield from rec(i + 1)
            out[u].discard(v); inn[v].discard(u)
        chosen[i] = None

    yield from rec(0)


def _induced_acyclic(S, succ):
    """True iff the subdigraph induced on vertex set S (frozenset) is acyclic.
    succ[v] = set of out-neighbours of v in the whole digraph."""
    # Kahn topological sort on the induced subgraph.
    Sset = S
    indeg = {v: 0 for v in Sset}
    adj = {v: [w for w in succ[v] if w in Sset] for v in Sset}
    for v in Sset:
        for w in adj[v]:
            indeg[w] += 1
    stack = [v for v in Sset if indeg[v] == 0]
    seen = 0
    while stack:
        v = stack.pop()
        seen += 1
        for w in adj[v]:
            indeg[w] -= 1
            if indeg[w] == 0:
                stack.append(w)
    return seen == len(Sset)


def has_acyclic_5set(n, arcs):
    """True iff some induced 5-subset is acyclic (=> alpha >= 5)."""
    succ = [set() for _ in range(n)]
    for (u, v) in arcs:
        succ[u].add(v)
    for S in itertools.combinations(range(n), 5):
        if _induced_acyclic(frozenset(S), succ):
            return True
    return False


def worker(args):
    n, edges = args
    edges = [tuple(sorted(e)) for e in edges]
    n_c3 = 0
    low = []  # arcs of any C_3 with alpha<=4 (no acyclic 5-set)
    for arcs in _orient(edges, n):
        al = list(arcs)
        if core.has_long_induced_dicycle(n, al, min_len=4):
            continue
        n_c3 += 1
        if not has_acyclic_5set(n, al):
            low.append(al)
    return (n_c3, low)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-p", "--processes", type=int, default=11)
    args = ap.parse_args()
    all_graphs = list(core.all_simple_graphs(N, connected=True))
    graphs = [(N, edges) for (gn, edges) in all_graphs if not has_k4(N, edges)]
    print(f"[n={N}] {len(all_graphs)} connected, {len(graphs)} K4-free scanned",
          flush=True)
    t = time.time()
    total_c3 = 0
    low_all = []
    done = 0
    with Pool(processes=args.processes, maxtasksperchild=200) as pool:
        for (nc3, low) in pool.imap_unordered(worker, graphs, chunksize=2):
            done += 1
            total_c3 += nc3
            low_all.extend(low)
            if done % 5000 == 0:
                print(f"  [n={N}] {done}/{len(graphs)} "
                      f"elapsed={time.time()-t:.0f}s total_c3={total_c3} "
                      f"alpha<=4_found={len(low_all)}", flush=True)
    wall = time.time() - t
    print("=" * 64, flush=True)
    print(f"[n={N}] n_C3={total_c3} wall={wall:.0f}s "
          f"alpha<=4_candidates={len(low_all)}", flush=True)
    if not low_all:
        print(f"[n={N}] NO C_3 digraph with alpha<=4 -> beta*(9) >= 5/9 = "
              f"{5/9:.4f} >= 0.5  => PREDICTION CONFIRMED (no drift below 0.45)",
              flush=True)
    else:
        # confirm with exact oracle
        confirmed = []
        for al in low_all:
            a = core.acyclic_number(N, al)
            if a <= 4:
                confirmed.append((a, al))
        if confirmed:
            a, al = min(confirmed)
            print(f"[n={N}] KILL: exact alpha={a} witness (beta={a/N:.4f} < 0.45): "
                  f"arcs={al}", flush=True)
        else:
            print(f"[n={N}] all {len(low_all)} 5-set-free candidates have exact "
                  f"alpha>=5 (Kahn false-negative impossible -> investigate)",
                  flush=True)


if __name__ == "__main__":
    main()
