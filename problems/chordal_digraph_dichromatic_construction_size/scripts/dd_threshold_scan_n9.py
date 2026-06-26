"""N(3) threshold scan at n=9 via TT3-pruning backtracking + cheap dd.

Reuses the VALIDATED early-TT3-prune orientation generator of m3_lb_scan_n9.py
(every TT3-free complete orientation is enumerated; no C_3 digraph skipped),
but computes the cheap directed-degeneracy dd (2-direction peeling) instead of
the SAT dichromatic number.  Goal: least n with a C_3 digraph of dd>=3 => N(3).

EXTRA SOUND PRUNE (base-graph level):
  dd(D)>=3 requires an induced subdigraph H in which every vertex has
  out-deg>=3 AND in-deg>=3, i.e. underlying degree >=6 in H.  Such an H needs
  >=8 vertices (7 vertices with all-degree-6 = K7 contains K4, excluded).
  Hence the UNDERLYING simple graph of D must contain an induced subgraph on
  >=8 vertices with minimum degree >=6.  A connected base graph with no such
  induced subgraph can NEVER yield a dd>=3 orientation, so it is skipped
  losslessly for the dd>=3 search.  (max_dd is still reported correctly for the
  graphs we DO scan; skipped graphs provably have dd<=2.)

Cross-validate at n=6,7,8 (must reproduce n_C3 = 2186, 25258, 479168 and
max_dd over the *scanned* set; the skipped graphs contribute only dd<=2) BUT
note: with the base prune we no longer count all C_3 members, only those on
prune-surviving graphs.  So we run n=6,7,8 in TWO modes:
  --no-prune : full count, must match 2186/25258/479168 & max_dd=2 (validates dd
               routine + generator).
  default    : pruned, must still find max_dd correct (no dd>=3) and be fast.
"""
import sys, os, time, itertools, argparse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import core
import networkx as nx
from multiprocessing import Pool

# reuse validated TT3-pruning generator + k4 test
from m3_lb_scan_n9 import has_k4, _orient


def dd(n, arcs):
    out = [0] * n; inn = [0] * n
    adj_out = [[] for _ in range(n)]; adj_in = [[] for _ in range(n)]
    for u, v in arcs:
        out[u] += 1; inn[v] += 1
        adj_out[u].append(v); adj_in[v].append(u)
    alive = [True] * n
    best = 0; remaining = n
    while remaining:
        mv = None; mk = None
        for v in range(n):
            if not alive[v]:
                continue
            k = out[v] if out[v] < inn[v] else inn[v]
            if mk is None or k < mk:
                mk = k; mv = v
        if mk > best:
            best = mk
        alive[mv] = False; remaining -= 1
        for w in adj_out[mv]:
            if alive[w]:
                inn[w] -= 1
        for w in adj_in[mv]:
            if alive[w]:
                out[w] -= 1
    return best


def can_host_dd3(n, edges):
    """True iff the underlying simple graph has an induced subgraph on >=8
    vertices with min degree >=6.  Lossless prune for the dd>=3 search."""
    G = nx.Graph(); G.add_nodes_from(range(n)); G.add_edges_from(edges)
    if n < 8:
        return False
    # repeatedly delete vertices of degree <6 (6-core-like); if >=8 survive, ok.
    H = G.copy()
    changed = True
    while changed:
        changed = False
        for v in list(H.nodes()):
            if H.degree(v) < 6:
                H.remove_node(v); changed = True
    return H.number_of_nodes() >= 8


def worker(args):
    n, edges, prune = args
    max_dd = 0; n_c3 = 0; witness = None
    edges = [tuple(sorted(e)) for e in edges]
    for arcs in _orient(edges, n):
        if core.has_long_induced_dicycle(n, list(arcs), min_len=4):
            continue
        n_c3 += 1
        d = dd(n, list(arcs))
        if d > max_dd:
            max_dd = d
        if d >= 3 and witness is None:
            witness = list(arcs)
    return (max_dd, n_c3, witness)


def run(n, processes=14, chunksize=2, progress_every=2000, prune=True):
    all_graphs = list(core.all_simple_graphs(n, connected=True))
    kept = [(n, edges, prune) for (gn, edges) in all_graphs
            if not has_k4(n, edges) and (not prune or can_host_dd3(n, edges))]
    print(f"[n={n}] base graphs: {len(all_graphs)} total, kept(after K4 + "
          f"{'dd3-host prune' if prune else 'no prune'})={len(kept)}", flush=True)
    t = time.time()
    max_dd = 0; total_c3 = 0; witness = None; done = 0
    with Pool(processes=processes) as pool:
        for (md, nc3, w) in pool.imap_unordered(worker, kept,
                                                chunksize=chunksize):
            done += 1; total_c3 += nc3
            if md > max_dd:
                max_dd = md
            if w is not None and witness is None:
                witness = w
            if done % progress_every == 0:
                print(f"  [n={n}] {done}/{len(kept)} elapsed={time.time()-t:.0f}s "
                      f"max_dd={max_dd} total_c3={total_c3}", flush=True)
    wall = time.time() - t
    print("=" * 64, flush=True)
    print(f"[n={n}] max_dd(scanned)={max_dd} n_C3(scanned)={total_c3} "
          f"wall={wall:.0f}s dd>=3_witness={'YES' if witness else 'no'}",
          flush=True)
    if witness:
        print(f"[n={n}] FIRST dd>=3 arcs={witness} => N(3) <= {n}", flush=True)
    else:
        print(f"[n={n}] NO dd>=3 on n={n} => N(3) >= {n+1} "
              f"(skipped graphs provably dd<=2)", flush=True)
    return {"n": n, "max_dd": max_dd, "n_C3": total_c3,
            "wall_s": round(wall, 1), "witness": witness}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("n", type=int, nargs="*", default=[9])
    ap.add_argument("-p", "--processes", type=int, default=12)
    ap.add_argument("--no-prune", action="store_true",
                    help="disable dd3-host base prune (full C_3 count, for "
                         "cross-validation against 2186/25258/479168)")
    args = ap.parse_args()
    res = {}
    for n in args.n:
        res[n] = run(n, processes=args.processes, prune=not args.no_prune)
    print("\nSUMMARY:", flush=True)
    for n in sorted(res):
        r = res[n]
        print(f"  n={n}: max_dd={r['max_dd']} n_C3={r['n_C3']} "
              f"wall={r['wall_s']}s witness={'YES' if r['witness'] else 'no'}",
              flush=True)
