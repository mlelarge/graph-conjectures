"""Ground the round / locally-semicomplete localization proposal.

For each nontrivial strong component of each in-class member of
Forb_ind(K2_digon, ->C3, S2+) over all orientations of all simple graphs n=4..N:
  - is_round           : exists cyclic order with interval out-neighbourhoods
  - is_locally_semicomplete (out-version actually trivially true here, so we use
    the IN-version: every IN-neighbourhood induces a tournament)
The proposal's claims:
  (A) round == locally_semicomplete  (per strong comp)
  (B) every round strong comp has chi_d <= 2
  (C) every NON-round strong comp has a vertex whose IN-neighbourhood
      contains an independent pair (embedded in-star S2-)
  (D) deleting that vertex keeps the remainder in-class
"""
import os
import sys, json, itertools, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import core

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


def strong_components(n, arcs):
    import networkx as nx
    g = nx.DiGraph()
    g.add_nodes_from(range(n))
    g.add_edges_from(arcs)
    return [list(c) for c in nx.strongly_connected_components(g)]


def is_round(n, arcs):
    """Exists a cyclic order v_0..v_{n-1} s.t. for each v, both N+(v) and N-(v)
    are consecutive intervals in the cyclic order (Bang-Jensen round digraph).
    Brute force over cyclic orders (fix v0=0, permute rest)."""
    aset = set(map(tuple, arcs))
    if n <= 2:
        return True
    rest = list(range(1, n))
    for perm in itertools.permutations(rest):
        order = [0] + list(perm)
        pos = {v: i for i, v in enumerate(order)}
        ok = True
        for v in range(n):
            # out-neighbours must be a cyclic interval STARTING right after v
            outs = [u for u in range(n) if (v, u) in aset]
            ins = [u for u in range(n) if (u, v) in aset]
            if not _is_cyclic_interval([pos[u] for u in outs], n):
                ok = False; break
            if not _is_cyclic_interval([pos[u] for u in ins], n):
                ok = False; break
        if ok:
            return True
    return False


def _is_cyclic_interval(positions, n):
    if len(positions) <= 1:
        return True
    s = sorted(set(positions))
    if len(s) != len(positions):
        return False
    # check whether s forms a contiguous arc on the cycle Z_n
    full = set(s)
    for start in s:
        run = set((start + k) % n for k in range(len(s)))
        if run == full:
            return True
    return False


def is_locally_semicomplete_in(n, arcs):
    """Every IN-neighbourhood induces a tournament (semicomplete oriented = tour-
    nament for oriented graphs)."""
    aset = set(map(tuple, arcs))
    for v in range(n):
        ins = [u for u in range(n) if (u, v) in aset]
        for i in range(len(ins)):
            for j in range(i + 1, len(ins)):
                a, b = ins[i], ins[j]
                if (a, b) not in aset and (b, a) not in aset:
                    return False  # independent in-pair -> not in-tournament
    return True


def in_neigh_independent_pair_vertex(n, arcs):
    """Return a vertex v whose IN-neighbourhood contains an independent pair, or
    None."""
    aset = set(map(tuple, arcs))
    for v in range(n):
        ins = [u for u in range(n) if (u, v) in aset]
        for i in range(len(ins)):
            for j in range(i + 1, len(ins)):
                a, b = ins[i], ins[j]
                if (a, b) not in aset and (b, a) not in aset:
                    return v, (a, b)
    return None


def run(N):
    rounds_with_high_chi = []         # KILL (i)
    nonround_no_instar = []           # KILL (ii)
    mismatch_round_vs_locsemi = []    # claim (A) failures
    peel_breaks = []                  # claim (D) failures (sampled)
    tally = {}
    round_count = 0
    locsemi_count = 0
    nonround_count = 0
    strong_comp_count = 0
    seen = set()

    for n in range(4, N + 1):
        ex_mismatch = 0
        for edges in all_simple_graphs(n):
            for arcs in core.all_orientations(edges):
                D = (n, arcs)
                if not in_class(D):
                    continue
                for comp in strong_components(n, arcs):
                    if len(comp) < 3:
                        continue
                    sub_n, sub_arcs = core.induced_subdigraph(D, comp)
                    key = (sub_n, tuple(sorted(map(tuple, sub_arcs))))
                    if key in seen:
                        continue
                    seen.add(key)
                    strong_comp_count += 1
                    rnd = is_round(sub_n, sub_arcs)
                    lsc = is_locally_semicomplete_in(sub_n, sub_arcs)
                    if rnd:
                        round_count += 1
                    if lsc:
                        locsemi_count += 1
                    if rnd != lsc:
                        ex_mismatch += 1
                        if len(mismatch_round_vs_locsemi) < 20:
                            mismatch_round_vs_locsemi.append(
                                {"n": sub_n, "arcs": sub_arcs,
                                 "round": rnd, "loc_semicomplete": lsc})
                    if rnd:
                        chi = core.dichromatic_number(sub_n, sub_arcs)
                        if chi >= 3:
                            rounds_with_high_chi.append(
                                {"n": sub_n, "arcs": sub_arcs, "chi_d": chi})
                    else:
                        nonround_count += 1
                        ip = in_neigh_independent_pair_vertex(sub_n, sub_arcs)
                        if ip is None:
                            nonround_no_instar.append(
                                {"n": sub_n, "arcs": sub_arcs})
                        else:
                            # claim (D): peel the vertex, remainder in-class?
                            v = ip[0]
                            keep = [w for w in range(sub_n) if w != v]
                            rem = core.induced_subdigraph((sub_n, sub_arcs), keep)
                            if not in_class(rem):
                                if len(peel_breaks) < 20:
                                    peel_breaks.append(
                                        {"n": sub_n, "arcs": sub_arcs,
                                         "peeled_vertex": v,
                                         "remainder_in_class": False})
        tally[n] = ex_mismatch
    return {
        "N": N,
        "strong_comp_count_distinct": strong_comp_count,
        "round_count": round_count,
        "loc_semicomplete_in_count": locsemi_count,
        "nonround_count": nonround_count,
        "mismatch_round_vs_locsemi_per_n": tally,
        "KILL_i_round_with_chi>=3": rounds_with_high_chi,
        "KILL_ii_nonround_without_instar": nonround_no_instar,
        "claimA_mismatch_examples": mismatch_round_vs_locsemi,
        "claimD_peel_breaks": peel_breaks,
    }


if __name__ == "__main__":
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    print(json.dumps(run(N), indent=2))
