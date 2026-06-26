"""Ground the literature-reduction proposal's lemma L.

L: chi_vec(D) <= omega_underlying(D) - 1 for every D in C_3.

Also records the (chi_vec, omega_underlying) joint distribution and flags:
  * KILL-A: any C_3 digraph with omega_underlying >= 4  (would contradict
    the proven K4 => TT3 fact; impossible sanity check)
  * KILL-B: any C_3 digraph with chi_vec >= omega_underlying (breaks L below
    the paper bound; would settle m(3) <= n)

Sound complete enumeration over ALL simple graphs on n vertices x ALL
orientations, keeping C_3 members (mirrors oracle.extremal_small_n).
"""
import sys, os, time, argparse
from collections import Counter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import core
import networkx as nx


def omega_underlying(n, arcs):
    G = nx.Graph()
    G.add_nodes_from(range(n))
    G.add_edges_from([(u, v) for (u, v) in arcs])
    if G.number_of_edges() == 0:
        return 1 if n >= 1 else 0
    return max(len(c) for c in nx.find_cliques(G))


def run(n):
    joint = Counter()          # (chi_vec, omega) -> count
    n_c3 = 0
    viol_k4 = 0                # omega >= 4 members
    viol_L = []                # chi_vec >= omega witnesses
    max_chi = 0
    t = time.time()
    for (gn, edges) in core.all_simple_graphs(n):
        for arcs in core.all_orientations(edges):
            if not core.is_C3(n, arcs):
                continue
            n_c3 += 1
            om = omega_underlying(n, arcs)
            if om >= 4:
                viol_k4 += 1
            # cap dichromatic search at omega (enough to test L: chi<=omega-1)
            cv = core.dichromatic_number(n, arcs, ub=max(om, 1))
            if cv > max_chi:
                max_chi = cv
            joint[(cv, om)] += 1
            if cv >= om:
                viol_L.append({"arcs": list(arcs), "chi": cv, "omega": om})
                if len(viol_L) > 20:
                    viol_L = viol_L[:20]
    wall = time.time() - t
    return {
        "n": n,
        "n_C3": n_c3,
        "max_chi_in_C3": max_chi,
        "viol_k4_omega_ge_4": viol_k4,
        "viol_L_count": len(viol_L),
        "viol_L_examples": viol_L[:5],
        "joint_chi_omega": {f"chi{c}_om{o}": cnt
                            for (c, o), cnt in sorted(joint.items())},
        "wall_s": round(wall, 1),
    }


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("n", type=int, nargs="*", default=[3, 4, 5, 6, 7])
    args = ap.parse_args()
    import json
    for n in args.n:
        r = run(n)
        print(json.dumps(r), flush=True)
