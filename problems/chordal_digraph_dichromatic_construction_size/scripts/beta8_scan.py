"""Parallel exhaustive scan for beta(8) = min alpha_vec(D)/n over C_3 digraphs on n=8.

Distributes connected base graphs across worker processes. Fully exhaustive
(no edge cap): every connected simple graph on n=8 and every orientation is
tested for C_3 membership; acyclic_number is computed for every C_3 digraph.

Soundness for the minimizer: a disconnected D has alpha_vec = sum of component
alpha_vec and n = sum of component orders, so its ratio is a weighted average of
component ratios and is >= the min component ratio; hence the global minimizer of
alpha_vec/n is attained on a connected digraph. Restricting base graphs to
connected is therefore sound for finding beta(n).
"""
import sys, os, time, itertools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import core
import networkx as nx
from multiprocessing import Pool

N = 8


def has_k4(edges):
    """True if the underlying graph contains a 4-clique.

    Sound prune: every orientation (tournament) of K4 contains a transitive
    triangle (verified exhaustively over all 2^6 K4-tournaments). Hence any base
    graph containing a K4 admits NO C_3 orientation and can be skipped without
    enumerating its 2^|E| orientations. This loses no C_3 digraph.
    """
    G = nx.Graph()
    G.add_nodes_from(range(N))
    G.add_edges_from(edges)
    adj = {v: set(G[v]) for v in G}
    for a, b, c, d in itertools.combinations(range(N), 4):
        s = {a, b, c, d}
        if all(len(s & (adj[v] | {v})) == 4 for v in (a, b, c, d)):
            return True
    return False


def worker(args):
    idx, edges = args
    best = None
    besta = None
    bestarcs = None
    n_c3 = 0
    for arcs in core.all_orientations(edges):
        if not core.is_C3(N, arcs):
            continue
        n_c3 += 1
        a = core.acyclic_number(N, arcs)
        r = a / N
        if best is None or r < best:
            best = r
            besta = a
            bestarcs = list(arcs)
    return (best, besta, bestarcs, n_c3)


def main():
    all_graphs = list(core.all_simple_graphs(N, connected=True))
    graphs = [(i, edges) for i, (gn, edges) in enumerate(all_graphs)
              if not has_k4(edges)]
    print(f"connected base graphs n={N}: {len(all_graphs)} total, "
          f"{len(graphs)} K4-free (scanned)", flush=True)
    t = time.time()
    best = None
    besta = None
    bestarcs = None
    total_c3 = 0
    done = 0
    with Pool(processes=14) as pool:
        for (b, ba, barcs, nc3) in pool.imap_unordered(worker, graphs, chunksize=4):
            done += 1
            total_c3 += nc3
            if b is not None and (best is None or b < best):
                best = b
                besta = ba
                bestarcs = barcs
            if done % 1000 == 0:
                print(f"  progress {done}/{len(graphs)} elapsed={time.time()-t:.0f}s "
                      f"running_best_beta={best} alpha={besta} total_c3={total_c3}",
                      flush=True)
    import math
    print("=" * 60, flush=True)
    print(f"beta({N})= {best} min_alpha= {besta} "
          f"count_bound_chi= {math.ceil(N/besta)}", flush=True)
    print(f"n_C3= {total_c3} wall={time.time()-t:.0f}s", flush=True)
    print(f"arcs= {bestarcs}", flush=True)


if __name__ == "__main__":
    main()
