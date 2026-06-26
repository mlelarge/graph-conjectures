"""H6: SOUND complete non-existence scan -> m(3) >= 10 (push to n=9).

Same sound recipe as m3_lb_scan.py (connected K4-free base graphs x ALL
orientations, keep is_C3, exact chi capped ub=3), but with a BACKTRACKING
orientation generator that prunes the moment a transitive triangle TT3 is
forced on the partially-oriented base graph.  This makes the n=9 scan
tractable: the vast majority of orientations of a dense-ish base graph carry a
TT3, and the naive 2^|E| enumeration of m3_lb_scan.py wastes all that work.

Soundness:
  * K4-free base-graph prune is LOSSLESS (every K4-tournament has a TT3), same
    as the validated n<=8 scan.
  * Restricting to CONNECTED base graphs is lossless for the m(3) lower bound
    (chi_vec = max over weak components; a chi>=3 component on <9 vertices would
    contradict m(3)>=9).  See m3_lb_scan.py docstring.
  * The early-TT3 prune is EXACT: orienting the remaining edges of a partial
    orientation that already contains a TT3 can never remove that TT3, so the
    whole subtree carries a TT3 and is (correctly) outside C_3.  Every
    TT3-free COMPLETE orientation is still fully enumerated, then handed to the
    SAME is_C3 / dichromatic_number oracle as before.  No C_3 digraph is
    skipped and no chi computation is approximated.

MANDATORY cross-validation: at n=6,7,8 this generator must reproduce the
brute-force counts (n_C3 = 2186, 25258, 479168) and max_chi_in_C3 == 2 of the
validated m3_lb_scan.py run BEFORE the n=9 number is trusted.  Run e.g.
    m3_lb_scan_n9.py 6 7 8
to check, then
    m3_lb_scan_n9.py 9
"""
import sys, os, time, itertools, argparse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import core
import networkx as nx
from multiprocessing import Pool


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
    """Given we are about to ADD arc u->v, does it complete a transitive
    triangle with the arcs already placed?  A TT3 on {u,v,w} containing arc
    u->v arises in exactly these patterns:
      (a) u->v, v->w, u->w   : w in out[v] & out[u]
      (b) w->u, u->v, w->v   : w in inn[u] & inn[v]
      (c) u->w, w->v, u->v   : w in out[u] & inn[v]
    Checking u->v as the new arc against all three covers every TT3 the new
    arc can close (the apex/middle/base roles).
    """
    if out[v] & out[u]:        # (a) v->w and u->w
        return True
    if inn[u] & inn[v]:        # (b) w->u and w->v
        return True
    if out[u] & inn[v]:        # (c) u->w and w->v
        return True
    return False


def _orient(edges, n):
    """Yield every TT3-free complete orientation of `edges` (list of (a,b),
    a<b) as a frozenset-free tuple of arcs, via DFS with early TT3 pruning."""
    m = len(edges)
    out = [set() for _ in range(n)]
    inn = [set() for _ in range(n)]
    chosen = [None] * m  # chosen[i] = (u,v) actual oriented arc

    def add(u, v):
        out[u].add(v); inn[v].add(u)

    def remove(u, v):
        out[u].discard(v); inn[v].discard(u)

    def rec(i):
        if i == m:
            yield tuple(chosen)
            return
        a, b = edges[i]
        for (u, v) in ((a, b), (b, a)):
            if _creates_tt3(u, v, out, inn):
                continue
            add(u, v)
            chosen[i] = (u, v)
            yield from rec(i + 1)
            remove(u, v)
        chosen[i] = None

    yield from rec(0)


def worker(args):
    n, idx, edges = args
    max_chi = 0
    n_c3 = 0
    witness = None
    edges = [tuple(sorted(e)) for e in edges]
    for arcs in _orient(edges, n):
        # arcs are TT3-free by construction; still need oriented (guaranteed,
        # each edge once) + no long induced dicycle.
        if core.has_long_induced_dicycle(n, list(arcs), min_len=4):
            continue
        n_c3 += 1
        cv = core.dichromatic_number(n, list(arcs), ub=3)
        if cv > max_chi:
            max_chi = cv
        if cv >= 3 and witness is None:
            witness = list(arcs)
    return (max_chi, n_c3, witness)


def run(n, processes=14, chunksize=2, progress_every=2000):
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
              f"=> (sound) m(3) >= {n+1}", flush=True)
    return {"n": n, "max_chi_in_C3": max_chi, "n_C3": total_c3,
            "wall_s": round(wall, 1), "witness": witness}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("n", type=int, nargs="*", default=[6, 7, 8])
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
