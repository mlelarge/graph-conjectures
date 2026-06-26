"""Directed-degeneracy threshold scan over C_3 digraphs.

dd(D) = max over induced subdigraphs H of min_{v in H} min(d+_H(v), d-_H(v)),
computed by repeatedly deleting the vertex with smallest min(d+,d-) (2-direction
peeling).  Sound bound: chi_vec(D) <= 1 + dd(D).

For each n: K4-free lossless prune (every K4 tournament has a TT3), then ALL
2^|E| orientations of each connected base graph, keep is_C3, compute dd.
Report max_dd and the FIRST dd>=3 witness => threshold N(3).
"""
import sys, os, time, argparse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from multiprocessing import Pool
import core
import networkx as nx


def has_k4(n, edges):
    G = nx.Graph(); G.add_nodes_from(range(n)); G.add_edges_from(edges)
    for c in nx.find_cliques(G):
        if len(c) >= 4:
            return True
    return False


def dd(n, arcs):
    out = [0] * n
    inn = [0] * n
    adj_out = [[] for _ in range(n)]
    adj_in = [[] for _ in range(n)]
    for u, v in arcs:
        out[u] += 1; inn[v] += 1
        adj_out[u].append(v); adj_in[v].append(u)
    alive = [True] * n
    cur = list(range(n))
    best = 0
    remaining = n
    while remaining:
        # find alive vertex with smallest min(out,inn)
        mv = None; mk = None
        for v in cur:
            if not alive[v]:
                continue
            k = out[v] if out[v] < inn[v] else inn[v]
            if mk is None or k < mk:
                mk = k; mv = v
        if mk > best:
            best = mk
        # delete mv
        alive[mv] = False
        remaining -= 1
        for w in adj_out[mv]:
            if alive[w]:
                inn[w] -= 1
        for w in adj_in[mv]:
            if alive[w]:
                out[w] -= 1
    return best


def worker(args):
    n, edges = args
    max_dd = 0
    n_c3 = 0
    witness = None
    for arcs in core.all_orientations(edges):
        if not core.is_C3(n, arcs):
            continue
        n_c3 += 1
        d = dd(n, arcs)
        if d > max_dd:
            max_dd = d
        if d >= 3 and witness is None:
            witness = list(arcs)
    return (max_dd, n_c3, witness)


def run(n, processes=14, chunksize=4, progress_every=2000):
    all_graphs = list(core.all_simple_graphs(n, connected=True))
    graphs = [(n, edges) for (gn, edges) in all_graphs if not has_k4(n, edges)]
    print(f"[n={n}] base graphs: {len(all_graphs)} total, {len(graphs)} K4-free",
          flush=True)
    t = time.time()
    max_dd = 0; total_c3 = 0; witness = None; done = 0
    with Pool(processes=processes) as pool:
        for (md, nc3, w) in pool.imap_unordered(worker, graphs,
                                                chunksize=chunksize):
            done += 1
            total_c3 += nc3
            if md > max_dd:
                max_dd = md
            if w is not None and witness is None:
                witness = w
            if done % progress_every == 0:
                print(f"  [n={n}] {done}/{len(graphs)} elapsed={time.time()-t:.0f}s "
                      f"max_dd={max_dd} total_c3={total_c3}", flush=True)
    wall = time.time() - t
    print("=" * 64, flush=True)
    print(f"[n={n}] max_dd={max_dd} n_C3={total_c3} wall={wall:.0f}s "
          f"dd>=3_witness={'YES' if witness else 'no'}", flush=True)
    if witness:
        print(f"[n={n}] FIRST dd>=3 arcs={witness}", flush=True)
    return {"n": n, "max_dd": max_dd, "n_C3": total_c3,
            "wall_s": round(wall, 1), "witness": witness}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("n", type=int, nargs="*", default=[6, 7, 8])
    ap.add_argument("-p", "--processes", type=int, default=14)
    args = ap.parse_args()
    res = {}
    for n in args.n:
        res[n] = run(n, processes=args.processes)
    print("\nSUMMARY:", flush=True)
    for n in sorted(res):
        r = res[n]
        print(f"  n={n}: max_dd={r['max_dd']} n_C3={r['n_C3']} "
              f"wall={r['wall_s']}s witness={'YES' if r['witness'] else 'no'}",
              flush=True)
