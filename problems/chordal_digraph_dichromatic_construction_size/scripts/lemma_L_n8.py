"""Parallel ground of lemma L at n=8 (connected, K4-free base graphs).

Mirrors m3_lb_scan.py (sound + lossless for the chi>=3 / m(3) question) but
additionally computes omega_underlying for every C_3 member and the joint
(chi_vec, omega) distribution + L-violations (chi_vec >= omega_underlying).

Note: connected base graphs only (sound for chi>=3 question; the disconnected
and edgeless members were already enumerated by the serial full-census probe
at n<=7). This run answers the SUBSTANTIVE prediction: does any C_3 digraph on
8 vertices have omega_underlying=3 AND chi_vec=3 (i.e. a non-trivial failure of
L = a witness m(3)<=8), or omega_underlying>=4 (impossible per K4=>TT3).
"""
import sys, os, time, itertools, argparse
from collections import Counter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import core
import networkx as nx
from multiprocessing import Pool


def has_k4(n, edges):
    G = nx.Graph(); G.add_nodes_from(range(n)); G.add_edges_from(edges)
    adj = {v: set(G[v]) for v in G}
    for quad in itertools.combinations(range(n), 4):
        s = set(quad)
        if all(len((adj[v] | {v}) & s) == 4 for v in quad):
            return True
    return False


def omega_underlying(n, arcs):
    G = nx.Graph(); G.add_nodes_from(range(n))
    G.add_edges_from([(u, v) for (u, v) in arcs])
    if G.number_of_edges() == 0:
        return 1
    return max(len(c) for c in nx.find_cliques(G))


def worker(args):
    n, edges = args
    joint = Counter()
    n_c3 = 0
    viol_k4 = 0
    viol_L = None        # first chi>=omega witness
    max_chi = 0
    for arcs in core.all_orientations(edges):
        if not core.is_C3(n, arcs):
            continue
        n_c3 += 1
        om = omega_underlying(n, arcs)
        if om >= 4:
            viol_k4 += 1
        cv = core.dichromatic_number(n, arcs, ub=max(om, 1))
        if cv > max_chi:
            max_chi = cv
        joint[(cv, om)] += 1
        if cv >= om and viol_L is None:
            viol_L = {"arcs": list(arcs), "chi": cv, "omega": om}
    return (max_chi, n_c3, viol_k4, viol_L, dict(joint))


def run(n, processes=14, chunksize=4):
    all_graphs = list(core.all_simple_graphs(n, connected=True))
    graphs = [(n, edges) for (gn, edges) in all_graphs if not has_k4(n, edges)]
    print(f"[n={n}] connected base: {len(all_graphs)} total, "
          f"{len(graphs)} K4-free", flush=True)
    t = time.time()
    max_chi = 0; total_c3 = 0; total_viol_k4 = 0; viol_L = None
    joint = Counter()
    done = 0
    with Pool(processes=processes) as pool:
        for (mc, nc3, vk4, vL, jt) in pool.imap_unordered(worker, graphs,
                                                          chunksize=chunksize):
            done += 1
            total_c3 += nc3
            total_viol_k4 += vk4
            if mc > max_chi:
                max_chi = mc
            if vL is not None and viol_L is None:
                viol_L = vL
            for k, c in jt.items():
                joint[k] += c
            if done % 500 == 0:
                print(f"  progress {done}/{len(graphs)} "
                      f"elapsed={time.time()-t:.0f}s max_chi={max_chi} "
                      f"c3={total_c3} viol_k4={total_viol_k4}", flush=True)
    wall = time.time() - t
    import json
    res = {
        "n": n, "n_C3_connected": total_c3, "max_chi_in_C3": max_chi,
        "viol_k4_omega_ge_4": total_viol_k4,
        "viol_L_chi_ge_omega": viol_L,
        "joint_chi_omega": {f"chi{c}_om{o}": cnt
                            for (c, o), cnt in sorted(joint.items())},
        "wall_s": round(wall, 1),
    }
    print("RESULT " + json.dumps(res), flush=True)
    return res


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("n", type=int, nargs="*", default=[8])
    ap.add_argument("-p", "--processes", type=int, default=14)
    args = ap.parse_args()
    for n in args.n:
        run(n, processes=args.processes)
