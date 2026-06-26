"""GROUNDING the out-local-tournament literature-reduction proposal.

For the FULL class Forb_ind(K2_digon,->C3,S2+) (= oriented, ->C3-free,
out-local-tournament digraphs), per STRONG member D test the proposal's four
predictions:

 (1) every N+(x) induces a TRANSITIVE tournament.
 (2) build quotient Q(D) by contracting maximal transitive-tournament MODULES
     inside each strong component (same module-clique contraction as h4).
 (3) Q(D) locally semicomplete (both N+ and N- induce tournaments) AND its
     round-quotient (contract "similar" classes) has underlying simple digraph
     equal to a SINGLE directed cycle C_k (k>=2) -- i.e. it IS round with a
     single-cycle round-quotient.
 (4) chi_d(Q(D)) == chi_d(D) <= 2.

KILL if any strong member has: non-transitive N+(x), OR a round-quotient that is
NOT a single directed cycle, OR chi_d(Q)>2, OR chi_d(D)>=3.

Usage: ground_outlocal_reduction.py <n>
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


def is_tournament_set(n_local, verts, aset):
    for i in range(len(verts)):
        for j in range(i + 1, len(verts)):
            a, b = verts[i], verts[j]
            if ((a, b) in aset) == ((b, a) in aset):
                return False
    return True


def induces_transitive_tournament(aset, verts):
    if not is_tournament_set(None, verts, aset):
        return False
    idx = {v: i for i, v in enumerate(verts)}
    sub = [(idx[a], idx[b]) for a in verts for b in verts
           if a != b and (a, b) in aset]
    return core.is_acyclic(len(verts), sub)


def strong_components(n, arcs):
    g = nx.DiGraph(); g.add_nodes_from(range(n)); g.add_edges_from(arcs)
    return [list(c) for c in nx.strongly_connected_components(g)]


def is_strong(n, arcs):
    if n <= 1:
        return True
    g = nx.DiGraph(); g.add_nodes_from(range(n)); g.add_edges_from(arcs)
    return nx.is_strongly_connected(g)


def module_clique_quotient(n, aset, comp):
    verts = list(comp)
    parent = {v: v for v in verts}

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]; a = parent[a]
        return a

    def is_module_pair(u, v):
        if not ((u, v) in aset or (v, u) in aset):
            return False
        for w in range(n):
            if w in (u, v):
                continue
            if ((w, u) in aset) != ((w, v) in aset):
                return False
            if ((u, w) in aset) != ((v, w) in aset):
                return False
        return True

    changed = True
    while changed:
        changed = False
        reps = sorted(set(find(v) for v in verts))
        for u, v in itertools.combinations(reps, 2):
            if is_module_pair(u, v):
                parent[find(u)] = find(v); changed = True; break

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
            if any((a, b) in aset for a in classes[r1] for b in classes[r2]):
                qarcs.add((qidx[r1], qidx[r2]))
    return qn, sorted(qarcs), [classes[r] for r in rep_list]


def is_locally_semicomplete(qn, qarcs):
    aset = set(qarcs)
    for x in range(qn):
        out = [y for y in range(qn) if (x, y) in aset]
        inn = [y for y in range(qn) if (y, x) in aset]
        if not is_tournament_set(qn, out, aset):
            return False
        if not is_tournament_set(qn, inn, aset):
            return False
    return True


def round_quotient_is_single_cycle(qn, qarcs):
    """Contract 'similar' vertices of a (strong, locally-semicomplete) digraph:
    x~y iff N+(x)\{y}==N+(y)\{x} and N-(x)\{y}==N-(y)\{x} (round-decomposition
    similarity). Then test the contracted quotient's UNDERLYING SIMPLE digraph
    is exactly a single directed cycle C_k (k>=2 means strong cyclic order)."""
    aset = set(qarcs)
    Nout = {x: set(y for y in range(qn) if (x, y) in aset) for x in range(qn)}
    Nin = {x: set(y for y in range(qn) if (y, x) in aset) for x in range(qn)}
    parent = list(range(qn))

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]; a = parent[a]
        return a

    changed = True
    while changed:
        changed = False
        reps = sorted(set(find(v) for v in range(qn)))
        for u, v in itertools.combinations(reps, 2):
            if (Nout[u] - {v}) == (Nout[v] - {u}) and (Nin[u] - {v}) == (Nin[v] - {u}):
                parent[find(u)] = find(v); changed = True; break
        if changed:
            # rebuild N within class representatives lazily via original membership
            # (similarity defined on original neighbourhoods; recompute on reps)
            classes = {}
            for x in range(qn):
                classes.setdefault(find(x), []).append(x)
            Nout2 = {}; Nin2 = {}
            for r, members in classes.items():
                outs = set(); ins = set()
                for m in members:
                    outs |= Nout[m]; ins |= Nin[m]
                Nout2[r] = set(find(t) for t in outs) - {r}
                Nin2[r] = set(find(t) for t in ins) - {r}
            Nout = Nout2; Nin = Nin2

    classes = {}
    for x in range(qn):
        classes.setdefault(find(x), []).append(x)
    reps = sorted(classes.keys())
    rn = len(reps)
    ridx = {r: i for i, r in enumerate(reps)}
    rarcs = set()
    for r1 in reps:
        for t in Nout[r1]:
            r2 = find(t)
            if r2 != r1:
                rarcs.add((ridx[r1], ridx[r2]))
    # underlying-simple single directed cycle: each vertex out-deg 1 & in-deg 1,
    # exactly rn arcs, strongly connected. For rn==1 (acyclic quotient) -> not a cycle.
    if rn < 2:
        return False, rn, sorted(rarcs)
    outdeg = [0] * rn; indeg = [0] * rn
    for (a, b) in rarcs:
        outdeg[a] += 1; indeg[b] += 1
    is_cycle = (len(rarcs) == rn and all(d == 1 for d in outdeg)
                and all(d == 1 for d in indeg) and is_strong(rn, list(rarcs)))
    return is_cycle, rn, sorted(rarcs)


def run(n):
    members = strong_members = 0
    max_chi = 0
    fail_a = []          # non-transitive N+(x)
    fail_loc_semi = []   # quotient not locally semicomplete
    fail_round = []      # round-quotient not a single cycle
    fail_chi = []        # chi_d(Q) != chi_d(D) or > 2
    chi3 = []            # any member chi_d>=3
    round_k_dist = {}

    for (gn, edges) in all_simple_graphs(n):
        for arcs in core.all_orientations(edges):
            D = (n, arcs)
            if not in_class(D):
                continue
            members += 1
            aset = set(arcs)
            chi = core.dichromatic_number(n, arcs)
            max_chi = max(max_chi, chi)
            if chi >= 3 and len(chi3) < 5:
                chi3.append({"n": n, "arcs": arcs, "chi_d": chi})

            # check (1) for ALL vertices
            for x in range(n):
                nb = [y for y in range(n) if (x, y) in aset]
                if len(nb) >= 2 and not induces_transitive_tournament(aset, nb):
                    if len(fail_a) < 5:
                        fail_a.append({"n": n, "arcs": arcs, "x": x, "Nplus": nb})

            # proposal restricts (2)-(4) to STRONG members
            if not is_strong(n, arcs):
                continue
            strong_members += 1
            qn, qarcs, classes = module_clique_quotient(n, aset, list(range(n)))
            qchi = core.dichromatic_number(qn, qarcs)
            if not is_locally_semicomplete(qn, qarcs) and len(fail_loc_semi) < 5:
                fail_loc_semi.append({"n": n, "arcs": arcs,
                                      "quotient_n": qn, "quotient_arcs": qarcs})
            is_cyc, rn, rarcs = round_quotient_is_single_cycle(qn, qarcs)
            round_k_dist[rn] = round_k_dist.get(rn, 0) + 1
            if not is_cyc and len(fail_round) < 8:
                fail_round.append({"n": n, "arcs": arcs, "quotient_n": qn,
                                   "quotient_arcs": qarcs, "round_n": rn,
                                   "round_arcs": rarcs})
            if (qchi > 2 or qchi != chi) and len(fail_chi) < 5:
                fail_chi.append({"n": n, "arcs": arcs, "chi_d_D": chi,
                                 "quotient_n": qn, "quotient_arcs": qarcs,
                                 "chi_d_Q": qchi})

    return {
        "n": n,
        "members_checked": members,
        "strong_members_checked": strong_members,
        "max_chi_d": max_chi,
        "pred1_Nplus_transitive": {"all_pass": len(fail_a) == 0, "failures": fail_a},
        "pred3a_quotient_locally_semicomplete": {
            "all_pass": len(fail_loc_semi) == 0, "failures": fail_loc_semi},
        "pred3b_round_quotient_single_cycle": {
            "all_pass": len(fail_round) == 0, "failures": fail_round,
            "round_quotient_size_distribution": round_k_dist},
        "pred4_chi_Q_eq_chi_D_le2": {"all_pass": len(fail_chi) == 0, "failures": fail_chi},
        "kill_any_member_chi_ge3": {"found": len(chi3) > 0, "witnesses": chi3},
    }


if __name__ == "__main__":
    print(json.dumps(run(int(sys.argv[1])), indent=2))
