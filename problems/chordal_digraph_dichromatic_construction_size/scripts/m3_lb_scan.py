"""H5: SOUND complete non-existence scan -> m(3) >= 9.

Goal: prove there is NO C_3 digraph on n=8 vertices with chi_vec >= 3, hence
m(3) >= 9 (raising the exact lower bound from m(3) >= 8).

Method (sound, complete -- NO unsound min-semidegree prefilter, cf. G6):
  * enumerate every connected simple graph on n vertices (nauty geng -c),
  * prune base graphs containing a K4 (LOSSLESS: every tournament on K4
    contains a transitive triangle, so a K4-base admits NO C_3 orientation),
  * for EACH kept base graph enumerate ALL 2^|E| orientations,
  * keep is_C3 members, compute exact chi_vec (capped at ub=3 for speed),
  * report max chi over all C_3 digraphs and ANY chi>=3 witness.

Soundness of restricting to CONNECTED base graphs for the m(3) lower bound:
the dichromatic number of a digraph is the MAX of the dichromatic numbers of
its (weak) components.  So any n=8 C_3 digraph with chi_vec>=3 has a connected
component, on <=8 vertices, that is itself C_3 (C_3 is closed under induced
subdigraphs / disjoint-union components) with chi_vec>=3.  If that component
has <8 vertices it contradicts the already-proved m(3)>=8.  Hence a chi>=3
witness on n=8 must be CONNECTED on all 8 vertices.  Scanning connected base
graphs is therefore lossless for the m(3)>=9 question.

Cross-validation: at n=6 and n=7 this connected+K4-free generator must
reproduce max_chi_in_C3 == 2 (matching the proved m(3)>=8 full scan) BEFORE
the n=8 result is trusted.
"""
import sys, os, time, itertools, argparse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import core
import networkx as nx
from multiprocessing import Pool


def has_k4(n, edges):
    """True if the underlying simple graph contains a 4-clique.

    Sound (lossless) prune: every orientation (tournament) of K4 contains a
    transitive triangle (true for all 2^6 K4-tournaments), so any base graph
    with a K4 admits NO C_3 orientation; skipping it drops no C_3 digraph.
    """
    G = nx.Graph()
    G.add_nodes_from(range(n))
    G.add_edges_from(edges)
    adj = {v: set(G[v]) for v in G}
    for quad in itertools.combinations(range(n), 4):
        s = set(quad)
        if all(len((adj[v] | {v}) & s) == 4 for v in quad):
            return True
    return False


def worker(args):
    n, idx, edges = args
    max_chi = 0
    n_c3 = 0
    witness = None  # first chi>=3 witness arcs, if any
    for arcs in core.all_orientations(edges):
        if not core.is_C3(n, arcs):
            continue
        n_c3 += 1
        cv = core.dichromatic_number(n, arcs, ub=3)
        if cv > max_chi:
            max_chi = cv
        if cv >= 3 and witness is None:
            witness = list(arcs)
    return (max_chi, n_c3, witness)


def run(n, processes=14, chunksize=4, progress_every=1000):
    all_graphs = list(core.all_simple_graphs(n, connected=True))
    graphs = [(n, i, edges) for i, (gn, edges) in enumerate(all_graphs)
              if not has_k4(n, edges)]
    print(f"[n={n}] connected base graphs: {len(all_graphs)} total, "
          f"{len(graphs)} K4-free (scanned)", flush=True)
    t = time.time()
    max_chi = 0
    total_c3 = 0
    witness = None
    done = 0
    with Pool(processes=processes) as pool:
        for (mc, nc3, w) in pool.imap_unordered(worker, graphs,
                                                chunksize=chunksize):
            done += 1
            total_c3 += nc3
            if mc > max_chi:
                max_chi = mc
            if w is not None and witness is None:
                witness = w
            if done % progress_every == 0:
                print(f"  [n={n}] progress {done}/{len(graphs)} "
                      f"elapsed={time.time()-t:.0f}s max_chi={max_chi} "
                      f"total_c3={total_c3}", flush=True)
    wall = time.time() - t
    print("=" * 64, flush=True)
    print(f"[n={n}] max_chi_in_C3= {max_chi}  n_C3= {total_c3}  "
          f"wall={wall:.0f}s", flush=True)
    if witness is not None:
        print(f"[n={n}] chi>=3 WITNESS FOUND -> m(3) <= {n}: arcs= {witness}",
              flush=True)
    else:
        print(f"[n={n}] NO chi>=3 witness: every connected K4-free C_3 digraph "
              f"on {n} vertices has chi_vec <= {max_chi} "
              f"=> (if n=8) m(3) >= {n+1}", flush=True)
    return {"n": n, "max_chi_in_C3": max_chi, "n_C3": total_c3,
            "wall_s": round(wall, 1), "witness": witness}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("n", type=int, nargs="*", default=[6, 7, 8],
                    help="orders to scan (default: cross-validate 6,7 then 8)")
    ap.add_argument("-p", "--processes", type=int, default=14)
    args = ap.parse_args()
    results = {}
    for n in args.n:
        results[n] = run(n, processes=args.processes)
    print("\nSUMMARY:", flush=True)
    for n in sorted(results):
        r = results[n]
        print(f"  n={n}: max_chi={r['max_chi_in_C3']} n_C3={r['n_C3']} "
              f"wall={r['wall_s']}s witness={'YES' if r['witness'] else 'no'}",
              flush=True)


if __name__ == "__main__":
    main()
