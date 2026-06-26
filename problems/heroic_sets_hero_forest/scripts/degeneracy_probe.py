"""Strong-component degeneracy probe for Conj 6.2 over the FULL class
Forb_ind(K2_digon, ->C3, S2+).

Falsifiable prediction (the proposal):
  At n=8, over the full class, EVERY non-trivial strong component contains a
  vertex of in-degree <= 2 AND a vertex of out-degree <= 2 (degrees taken
  WITHIN the component).  Equivalently:
      max over all strong comps of (min in-degree)  == 2  (never 3)
      max over all strong comps of (min out-degree) == 2  (never 3)
  KILL: a strong component with min-in-degree >= 3 (every vertex in-deg >=3
        inside the component) retires the 2-in-degeneracy peeling route.
  Independently KILLS H1 if any in-class member has chi_d >= 3.

Usage: degeneracy_probe.py exhaustive <n>
"""
import sys, json, itertools, subprocess
sys.path.insert(0, "scripts")
import core
import networkx as nx

C3 = core.C3()
S2P = core.S2_plus()


def in_class(D):
    return not (core.contains_induced(D, C3) or core.contains_induced(D, S2P))


def all_simple_graphs(n):
    gp = core.dc._geng_path()
    proc = subprocess.run([gp, "-q", str(n)], capture_output=True, text=True)
    for line in proc.stdout.splitlines():
        if line.strip():
            _gn, edges = core.dc._graph6_to_edges(line)
            yield edges


def comp_degeneracy(n, arcs):
    """For each non-trivial strong component, return (min_in_within, min_out_within).
    Returns list of (size, min_in, min_out, nodes)."""
    G = nx.DiGraph()
    G.add_nodes_from(range(n))
    G.add_edges_from(arcs)
    out = []
    for comp in nx.strongly_connected_components(G):
        if len(comp) < 2:
            continue
        sub = G.subgraph(comp)
        min_in = min(sub.in_degree(v) for v in comp)
        min_out = min(sub.out_degree(v) for v in comp)
        out.append((len(comp), min_in, min_out, sorted(comp)))
    return out


def exhaustive(n, compute_chi=True):
    cnt = 0
    maxchi = 0
    chi_viol = None
    chi_checked = 0
    max_minin = 0          # max over comps of (min in-degree within comp)
    max_minout = 0
    mi_witness = None      # the KILL: a comp with min_in >= 3
    mo_witness = None
    n_comps = 0
    dense_extremum = None  # an example comp achieving max_minin
    for edges in all_simple_graphs(n):
        for arcs in core.all_orientations(edges):
            D = (n, arcs)
            if not in_class(D):
                continue
            cnt += 1
            comps = comp_degeneracy(n, arcs)
            member_minin3 = any(mi >= 3 for (_s, mi, _mo, _nd) in comps)
            # chi_d is the SAT bottleneck.  Compute it (a) always when compute_chi,
            # else (b) only on members whose comp degeneracy is the interesting
            # KILL case (min_in>=3) so the independent H1 check still fires there.
            if compute_chi or member_minin3:
                chi = core.dichromatic_number(n, arcs)
                chi_checked += 1
                if chi > maxchi:
                    maxchi = chi
                if chi >= 3 and chi_viol is None:
                    chi_viol = {"n": n, "arcs": arcs, "chi_d": chi}
            else:
                chi = None
            for (size, mi, mo, nodes) in comps:
                n_comps += 1
                if mi > max_minin:
                    max_minin = mi
                    dense_extremum = {"n": n, "arcs": arcs, "comp_size": size,
                                      "comp_nodes": nodes, "min_in": mi, "min_out": mo}
                if mo > max_minout:
                    max_minout = mo
                if mi >= 3 and mi_witness is None:
                    mi_witness = {"n": n, "arcs": arcs, "comp_size": size,
                                  "comp_nodes": nodes, "min_in": mi, "min_out": mo, "chi_d": chi}
                if mo >= 3 and mo_witness is None:
                    mo_witness = {"n": n, "arcs": arcs, "comp_size": size,
                                  "comp_nodes": nodes, "min_in": mi, "min_out": mo, "chi_d": chi}
    return {
        "chi_d_members_checked": chi_checked,
        "label": f"degeneracy_probe exhaustive n={n}",
        "in_class_members": cnt,
        "nontrivial_strong_comps": n_comps,
        "max_chi_d": maxchi,
        "chi_violation": chi_viol,
        "max_min_in_degree": max_minin,
        "max_min_out_degree": max_minout,
        "min_in_kill_witness": mi_witness,   # None => prediction CONFIRMED
        "min_out_kill_witness": mo_witness,
        "dense_extremum_comp": dense_extremum,
        "PREDICTION_CONFIRMED": (mi_witness is None and chi_viol is None),
    }


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "exhaustive":
        compute_chi = not (len(sys.argv) > 3 and sys.argv[3] == "--no-chi")
        print(json.dumps(exhaustive(int(sys.argv[2]), compute_chi=compute_chi), indent=2))
