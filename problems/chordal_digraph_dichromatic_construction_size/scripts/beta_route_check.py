"""Ground-check for the 'linear acyclic set / iterated peeling' asymptotic
lower-bound proposal.

Step 1: soundness anchor for the structural lemma
    alpha(D) >= Delta+(D) + 1   and   alpha(D) >= Delta-(D) + 1
on dense C_3 witnesses (K_{3,3,3} orientation = dd=3 witness; a max-arc C_3
member at n=7).  alpha = core.acyclic_number (oracle-exact).

Step 2: exact beta*(n) = min_{D in C_3, |D|=n} alpha(D)/n, cross-validated
against the known graveyard-G5 values 0.667/0.75/0.80/0.667/0.571/0.625 for
n=3..8, then extended.

Soundness for the minimizer (same as beta8_scan.py): for disconnected D,
alpha/n is a weighted average of component ratios >= min component ratio, so the
global minimizer is attained on a connected base graph -> restrict to connected.
K4-free prune is lossless (every K4-tournament has a TT3).
"""
import sys, os, time, itertools, math, argparse, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import core
import networkx as nx
from multiprocessing import Pool


def out_in_degrees(n, arcs):
    outd = [0] * n
    ind = [0] * n
    for (u, v) in arcs:
        outd[u] += 1
        ind[v] += 1
    return outd, ind


def cyclic_partite(sizes):
    r = len(sizes)
    offs = [0]
    for s in sizes:
        offs.append(offs[-1] + s)
    n = offs[-1]
    arcs = []
    for i in range(r):
        a0, a1 = offs[i], offs[i + 1]
        j = (i + 1) % r
        b0, b1 = offs[j], offs[j + 1]
        for a in range(a0, a1):
            for b in range(b0, b1):
                arcs.append((a, b))
    return n, arcs


def lemma_check_one(name, n, arcs):
    isc3 = core.is_C3(n, arcs)
    alpha = core.acyclic_number(n, arcs)
    outd, ind = out_in_degrees(n, arcs)
    dmax_out = max(outd)
    dmax_in = max(ind)
    ok = (alpha >= dmax_out + 1) and (alpha >= dmax_in + 1)
    print(f"[{name}] n={n} is_C3={isc3} alpha={alpha} "
          f"Delta+={dmax_out} Delta-={dmax_in} "
          f"alpha>=Delta+ +1: {alpha>=dmax_out+1} "
          f"alpha>=Delta- +1: {alpha>=dmax_in+1} LEMMA_OK={ok}", flush=True)
    return {"name": name, "n": n, "is_C3": isc3, "alpha": alpha,
            "Delta_out": dmax_out, "Delta_in": dmax_in, "lemma_ok": ok}


# ---------------- Step 2: exact beta*(n) scan ----------------

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
    n, edges = args
    edges = [tuple(sorted(e)) for e in edges]
    best = None
    besta = None
    bestarcs = None
    n_c3 = 0
    for arcs in _orient(edges, n):
        al = list(arcs)
        if core.has_long_induced_dicycle(n, al, min_len=4):
            continue
        n_c3 += 1
        a = core.acyclic_number(n, al)
        r = a / n
        if best is None or r < best:
            best = r
            besta = a
            bestarcs = al
    return (best, besta, bestarcs, n_c3)


def run_beta(n, processes=12):
    all_graphs = list(core.all_simple_graphs(n, connected=True))
    graphs = [(n, edges) for (gn, edges) in all_graphs if not has_k4(n, edges)]
    t = time.time()
    print(f"[n={n}] base graphs: {len(all_graphs)} connected, "
          f"{len(graphs)} K4-free (scanned)", flush=True)
    best = None
    besta = None
    bestarcs = None
    total_c3 = 0
    done = 0
    with Pool(processes=processes, maxtasksperchild=100) as pool:
        for (b, ba, barcs, nc3) in pool.imap_unordered(worker, graphs, chunksize=2):
            done += 1
            total_c3 += nc3
            if b is not None and (best is None or b < best):
                best = b
                besta = ba
                bestarcs = barcs
            if done % 5000 == 0:
                print(f"  [n={n}] {done}/{len(graphs)} "
                      f"elapsed={time.time()-t:.0f}s running_beta*={best} "
                      f"min_alpha={besta} total_c3={total_c3}", flush=True)
    wall = time.time() - t
    # realized peeling bound: ceil(log_{1/(1-beta*)} n) + 1
    if best is not None and 0 < best < 1:
        peel = math.ceil(math.log(n, 1.0 / (1.0 - best))) + 1
    else:
        peel = None
    print(f"[n={n}] beta*= {best:.6f}  min_alpha= {besta}  n_C3= {total_c3}  "
          f"wall={wall:.0f}s  peel_bound(ceil log_{{1/(1-b)}} n)+1= {peel}",
          flush=True)
    print(f"[n={n}] min-alpha witness arcs= {bestarcs}", flush=True)
    return {"n": n, "beta_star": best, "min_alpha": besta,
            "n_C3": total_c3, "wall_s": round(wall, 1),
            "peel_bound": peel, "witness": bestarcs}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ns", type=int, nargs="*", default=[3, 4, 5, 6, 7, 8])
    ap.add_argument("-p", "--processes", type=int, default=12)
    ap.add_argument("--lemma-only", action="store_true")
    ap.add_argument("--out", type=str, default=None)
    args = ap.parse_args()

    print("=== STEP 1: structural lemma alpha >= Delta(+/-) + 1 ===", flush=True)
    lem = []
    # K_{3,3,3} orientation (dd=3 witness)
    n333, a333 = cyclic_partite([3, 3, 3])
    lem.append(lemma_check_one("K_3,3,3 cyclic", n333, a333))
    # K_{2,2,2} cyclic (octahedron orientation) for comparison
    n222, a222 = cyclic_partite([2, 2, 2])
    lem.append(lemma_check_one("K_2,2,2 cyclic", n222, a222))
    # directed triangle G_2
    lem.append(lemma_check_one("C3 (G_2)", 3, [(0, 1), (1, 2), (2, 0)]))

    if args.lemma_only:
        return

    print("\n=== STEP 2: exact beta*(n) scan ===", flush=True)
    known = {3: 0.667, 4: 0.75, 5: 0.80, 6: 0.667, 7: 0.571, 8: 0.625}
    results = []
    for n in args.ns:
        r = run_beta(n, processes=args.processes)
        if n in known:
            got = round(r["beta_star"], 3)
            exp = known[n]
            match = abs(got - exp) < 0.01
            print(f"[n={n}] cross-validate beta* {got} vs known {exp}: "
                  f"{'MATCH' if match else 'MISMATCH'}", flush=True)
        results.append(r)

    print("\nSUMMARY beta*(n):", flush=True)
    for r in results:
        print(f"  n={r['n']}: beta*={r['beta_star']:.4f} "
              f"min_alpha={r['min_alpha']} n_C3={r['n_C3']} "
              f"peel_bound={r['peel_bound']}", flush=True)

    if args.out:
        with open(args.out, "w") as f:
            json.dump({"lemma": lem, "beta": results}, f, indent=2)
        print(f"wrote {args.out}", flush=True)


if __name__ == "__main__":
    main()
