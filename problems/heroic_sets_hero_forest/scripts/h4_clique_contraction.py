"""H4 mechanism test (next_action in ledger.json).

Over the FULL class Forb_ind(K2_digon, ->C3, S2+) -- all orientations of all
simple graphs on n vertices, filtered to induced ->C3-free and S2+-free -- we
test the two predictions of live hypothesis H4:

  (a) every out-neighbourhood N+(x) induces a TRANSITIVE TOURNAMENT
      (predicted forced by S2+-free + digon/->C3-free).

  (b) build the CLIQUE-CONTRACTION quotient of each strong component and
      measure its dichromatic number.  H4 predicts the quotient is
      "functional-like / single-directed-cycle" with a chi_d-lift capping the
      whole class at 2.

The clique-contraction here: within a strong component S, take the relation
"x ~ y iff x,y mutually reachable through a chain where each step's
out-neighbourhood is a transitive clique containing the other" -- but to keep
the test CONCRETE and falsifiable we use the cleanest contraction that H4
names: contract maximal vertex sets that induce a transitive tournament AND are
"modules" (same out/in neighbourhood outside the set).  We report, per member:

  - n+(x) transitive-tournament: all-pass / first counterexample
  - per strong component: size, whether it is itself a transitive tournament,
    the module-clique quotient, and the quotient's chi_d.

A member with a non-transitive-tournament N+(x) REFUTES prediction (a).
A member whose strong-component quotient has chi_d > 2 REFUTES prediction (b)
(and would localize where any 2-colouring proof must do work).

Usage:  h4_clique_contraction.py <n>
"""
import os
import sys, json, itertools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import core
import networkx as nx

C3 = core.C3()
S2P = core.S2_plus()


def in_class(D):
    return not (core.contains_induced(D, C3) or core.contains_induced(D, S2P))


def all_simple_graphs(n):
    import subprocess
    gp = core.dc._geng_path()
    proc = subprocess.run([gp, "-q", str(n)], capture_output=True, text=True)
    for line in proc.stdout.splitlines():
        if line.strip():
            yield core.dc._graph6_to_edges(line)


def out_neighbourhood(n, arcset, x):
    return [y for y in range(n) if (x, y) in arcset]


def induces_transitive_tournament(arcset, verts):
    """True iff `verts` induce a tournament that is transitive (== acyclic)."""
    m = len(verts)
    # tournament: exactly one of (a,b),(b,a) for each pair
    for i in range(m):
        for j in range(i + 1, m):
            a, b = verts[i], verts[j]
            ab = (a, b) in arcset
            ba = (b, a) in arcset
            if ab == ba:  # both or neither -> not a tournament
                return False
    # transitive == the induced subdigraph is acyclic (no directed cycle)
    idx = {v: i for i, v in enumerate(verts)}
    sub_arcs = [(idx[a], idx[b]) for a in verts for b in verts
                if a != b and (a, b) in arcset]
    return core.is_acyclic(m, sub_arcs)


def strong_components(n, arcs):
    g = nx.DiGraph()
    g.add_nodes_from(range(n))
    g.add_edges_from(arcs)
    return [list(c) for c in nx.strongly_connected_components(g)]


def module_clique_quotient(n, arcset, comp):
    """Contract maximal modules that induce a transitive tournament.

    A set M subset comp is a MODULE if every vertex outside M sees all of M
    identically (same arc direction / non-arc) -- standard module def restricted
    to comp.  We greedily contract pairs {u,v} that (i) are a module of size 2
    relative to the whole digraph and (ii) induce an arc (a 2-vertex transitive
    tournament), iterating to a fixpoint.  Returns the quotient digraph
    (qn, qarcs) on the contracted vertex set.
    """
    # work on the induced subdigraph of comp
    verts = list(comp)
    # union-find over comp vertices
    parent = {v: v for v in verts}

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    def is_module_pair(u, v):
        # u,v must be adjacent (form an arc, either direction) -> transitive TT2
        if not (((u, v) in arcset) ^ ((v, u) in arcset)):
            # need exactly one arc between them (a clique edge, oriented)
            if not ((u, v) in arcset or (v, u) in arcset):
                return False
        # every w outside {u,v} relates identically to u and to v
        for w in range(n):
            if w == u or w == v:
                continue
            if ((w, u) in arcset) != ((w, v) in arcset):
                return False
            if ((u, w) in arcset) != ((v, w) in arcset):
                return False
        return True

    changed = True
    while changed:
        changed = False
        reps = sorted(set(find(v) for v in verts))
        for u, v in itertools.combinations(reps, 2):
            if is_module_pair(u, v):
                parent[find(u)] = find(v)
                changed = True
                break

    classes = {}
    for v in verts:
        classes.setdefault(find(v), []).append(v)
    rep_list = sorted(classes.keys())
    qidx = {r: i for i, r in enumerate(rep_list)}
    qn = len(rep_list)
    qarcs = set()
    for r1 in rep_list:
        for r2 in rep_list:
            if r1 == r2:
                continue
            # arc r1->r2 in quotient iff some (a in class r1, b in class r2) has arc
            if any((a, b) in arcset for a in classes[r1] for b in classes[r2]):
                qarcs.add((qidx[r1], qidx[r2]))
    return qn, sorted(qarcs), [classes[r] for r in rep_list]


def run(n):
    arcset_failures_a = []   # members with a non-transitive-tournament N+(x)
    quotient_violations = [] # strong comps whose quotient chi_d > 2
    members = 0
    max_chi = 0
    max_quotient_chi = 0
    max_scc_size = 0
    quotient_chi_dist = {}
    scc_is_tt_count = 0
    scc_total = 0

    for (gn, edges) in all_simple_graphs(n):
        for arcs in core.all_orientations(edges):
            D = (n, arcs)
            if not in_class(D):
                continue
            members += 1
            arcset = set(arcs)

            # prediction (a): every N+(x) induces a transitive tournament
            for x in range(n):
                nb = out_neighbourhood(n, arcset, x)
                if len(nb) >= 2 and not induces_transitive_tournament(arcset, nb):
                    if len(arcset_failures_a) < 5:
                        arcset_failures_a.append(
                            {"n": n, "arcs": arcs, "x": x, "Nplus": nb})

            chi = core.dichromatic_number(n, arcs)
            max_chi = max(max_chi, chi)

            # prediction (b): per strong component, clique-contraction quotient chi_d
            for comp in strong_components(n, arcs):
                if len(comp) < 2:
                    continue
                scc_total += 1
                max_scc_size = max(max_scc_size, len(comp))
                # is the SCC itself a transitive tournament? (it can't be, TT is acyclic)
                comp_arcs = [(a, b) for a in comp for b in comp
                             if a != b and (a, b) in arcset]
                qn, qarcs, classes = module_clique_quotient(n, arcset, comp)
                qchi = core.dichromatic_number(qn, qarcs)
                max_quotient_chi = max(max_quotient_chi, qchi)
                quotient_chi_dist[qchi] = quotient_chi_dist.get(qchi, 0) + 1
                if qchi > 2 and len(quotient_violations) < 5:
                    quotient_violations.append(
                        {"n": n, "comp": comp, "comp_arcs": comp_arcs,
                         "quotient_n": qn, "quotient_arcs": qarcs,
                         "classes": classes, "quotient_chi_d": qchi})

    return {
        "n": n,
        "members_checked": members,
        "max_chi_d": max_chi,
        "prediction_a_Nplus_transitive_tournament": {
            "all_pass": len(arcset_failures_a) == 0,
            "first_failures": arcset_failures_a,
        },
        "prediction_b_clique_contraction_quotient": {
            "strong_components_checked": scc_total,
            "max_strong_component_size": max_scc_size,
            "max_quotient_chi_d": max_quotient_chi,
            "quotient_chi_d_distribution": quotient_chi_dist,
            "quotient_chi_d_gt_2": len(quotient_violations) == 0
                                   and "none -- all quotients chi_d<=2"
                                   or quotient_violations,
        },
    }


if __name__ == "__main__":
    n = int(sys.argv[1])
    print(json.dumps(run(n), indent=2))
