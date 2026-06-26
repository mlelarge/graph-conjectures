"""H10: STRUCTURE-EXTRACTION on the n=9 PRIME tww<=1 chiVec=3, omegaVec=2 witnesses.

next_action (ledger): characterize the 20 n=9 PRIME tww<=1 tournaments with
omegaVec=2, chiVec=3 (landmark prime_chi_gt_omega_at_n9) -- the first chi>omega
witnesses that are NOT substitution-built.  Find a COMMON forced obstruction /
transferable invariant that drives chiVec above omegaVec while keeping tww=1 and
the tournament PRIME.

Pipeline:
  Pass 1 (collect): full gentourng n=9 -> tww<=1 -> PRIME (maximal modular
    partition length == n) -> record (omega_vec, chi_vec). Split into
      WITNESS group W : prime, tww<=1, omega=2, chi=3
      CONTROL group C : prime, tww<=1, omega=2, chi=2  (the 3807 cell)
  Pass 2 (extract), on W (and contrasted against a C sample):
    (a) minimal chiVec=3 induced sub-tournament ("chi-3 core") of each witness:
        find the smallest vertex subset whose induced sub-tournament has
        chiVec=3.  Canonicalize (nauty-style via networkx weisfeiler/VF2 buckets)
        and tally the multiset of cores across all witnesses.
    (b) induced-subtournament PROFILE: for each k in {5,6,7} the set of
        canonical k-subtournament certificates present, to find a sub-pattern
        common to ALL witnesses but absent / rarer in controls.
    (c) the back-edge graph at an omega-optimal (clique=2 => triangle-free)
        ordering: report its structure.

Soundness: chiVec/omegaVec/tww are the exact oracle invariants (core.*).
Canonical form of a sub-tournament: VF2 isomorphism bucketing (exact, since
sub-tournaments here have <=7 vertices).

Usage: .venv/bin/python scripts/h10_prime_chi_gt_omega.py [--control-sample N]
       [--core-only] [--cache data/h10_witnesses.json]
"""
from __future__ import annotations
import argparse, json, sys, os, itertools, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import core
import oracle
import networkx as nx
from collections import Counter
from h8_closure_membership import _maximal_modular_partition

N = 9


def is_prime(n, arcs):
    A = core._adj(n, arcs)
    parts = _maximal_modular_partition(A, n)
    return len(parts) == n


def _di(n, arcs):
    g = nx.DiGraph()
    g.add_nodes_from(range(n))
    g.add_edges_from(arcs)
    return g


def canon_cert(n, arcs):
    """A canonical certificate (isomorphism-class key) for a small tournament.
    Uses a sorted invariant signature as a fast bucket key; ties are then
    resolved exactly with VF2 in the caller.  Here we return a tuple invariant:
    sorted out-degree sequence + sorted (out,in) score-pair multiset +
    number of 3-cycles. For n<=7 this is a strong (not perfect) invariant;
    callers that need exactness must still VF2-check within a bucket."""
    A = core._adj(n, arcs)
    outdeg = [sum(A[u]) for u in range(n)]
    indeg = [n - 1 - outdeg[u] for u in range(n)]
    # count cyclic triangles
    tri = 0
    for a in range(n):
        for b in range(n):
            if b == a:
                continue
            for c in range(n):
                if c == a or c == b:
                    continue
                if A[a][b] and A[b][c] and A[c][a]:
                    tri += 1
    tri //= 3
    return (tuple(sorted(outdeg)), tuple(sorted(zip(sorted(outdeg), sorted(indeg)))), tri)


def sub_arcs(A, verts):
    idx = {v: i for i, v in enumerate(verts)}
    out = []
    for a in verts:
        for b in verts:
            if a != b and A[a][b]:
                out.append((idx[a], idx[b]))
    return len(verts), out


class IsoClasses:
    """Exact iso-class registry for small tournaments, bucketed by invariant."""
    def __init__(self):
        self.buckets = {}   # cert -> list of (n, arcs, digraph)

    def key(self, n, arcs):
        cert = canon_cert(n, arcs)
        bucket = self.buckets.setdefault(cert, [])
        g = _di(n, arcs)
        for i, (bn, barcs, bg) in enumerate(bucket):
            if bn == n and nx.is_isomorphic(g, bg):
                return (cert, i)
        bucket.append((n, arcs, g))
        return (cert, len(bucket) - 1)


def min_chi3_cores(n, arcs, iso: IsoClasses):
    """Return the set of iso-keys of MINIMAL induced sub-tournaments with
    chiVec==3 (smallest vertex count; if several at that size, all of them).
    The smallest 3-dichromatic tournament has 7 vertices (Paley P7), so the
    minimal chi-3 core has exactly 7 vertices if chi(T)=3 and T is on 9."""
    A = core._adj(n, arcs)
    for size in range(7, n + 1):
        cores = set()
        for verts in itertools.combinations(range(n), size):
            sn, sarcs = sub_arcs(A, list(verts))
            if core.chi_vec(sn, sarcs) == 3:
                cores.add(iso.key(sn, sarcs))
        if cores:
            return size, cores
    return None, set()


def collect():
    """Pass 1: collect witnesses and controls."""
    witnesses = []   # prime, tww<=1, omega=2, chi=3
    control = []     # prime, tww<=1, omega=2, chi=2
    other = Counter()
    scanned = 0
    t0 = time.time()
    for (_n, arcs) in oracle._all_tournaments(N):
        scanned += 1
        w = core.tww(N, arcs, ub=2)
        if w > 1:
            continue
        if not is_prime(N, arcs):
            continue
        ov = core.omega_vec(N, arcs)
        ch = core.chi_vec(N, arcs)
        if ov == 2 and ch == 3:
            witnesses.append(list(arcs))
        elif ov == 2 and ch == 2:
            control.append(list(arcs))
        else:
            other[(w, ov, ch)] += 1
    return witnesses, control, dict(other), scanned, time.time() - t0


def be_graph_at_optimal(n, arcs):
    """Find an omega-optimal ordering (back-edge clique == omega_vec) and report
    the back-edge graph's structure (edges, triangle count). For omega=2 the
    optimal back-edge graph is triangle-free."""
    A = core._adj(n, arcs)
    ov = core.omega_vec(n, arcs)
    best = None
    # search orderings via the same B&B logic is internal; just brute a bound:
    # for n=9 full perms is 362880 -- feasible but slow per witness. Use greedy
    # restarts to FIND an optimal order, then report it.
    import random
    rng = random.Random(0)
    found = None
    for _ in range(2000):
        order = list(range(n)); rng.shuffle(order)
        # local hill-climb by adjacent swaps minimizing back-edge clique
        def bec(o):
            return core._backedge_clique_for_order(n, A, o)
        cur = bec(order)
        improved = True
        while improved:
            improved = False
            for i in range(n - 1):
                order[i], order[i+1] = order[i+1], order[i]
                c2 = bec(order)
                if c2 < cur:
                    cur = c2; improved = True
                else:
                    order[i], order[i+1] = order[i+1], order[i]
        if cur <= ov:
            found = order
            break
    if found is None:
        return {"omega_vec": ov, "found_optimal": False}
    # build back-edge graph
    pos = {v: i for i, v in enumerate(found)}
    g = nx.Graph()
    g.add_nodes_from(range(n))
    for i in range(n):
        for j in range(i + 1, n):
            u, w = found[i], found[j]
            if A[w][u]:
                g.add_edge(u, w)
    deg = sorted(d for _, d in g.degree())
    ntri = sum(nx.triangles(g).values()) // 3
    return {"omega_vec": ov, "found_optimal": True,
            "be_num_edges": g.number_of_edges(),
            "be_degree_seq": deg, "be_triangles": ntri,
            "be_is_forest": nx.is_forest(g),
            "be_is_bipartite": nx.is_bipartite(g)}


def run(control_sample=200, core_only=False, cache=None):
    if cache and os.path.exists(cache):
        with open(cache) as f:
            cached = json.load(f)
        witnesses = cached["witnesses"]; control = cached["control"]
        other = cached.get("other", {}); scanned = cached.get("scanned", -1)
        collect_secs = cached.get("collect_secs", -1)
    else:
        witnesses, control, other, scanned, collect_secs = collect()
        if cache:
            with open(cache, "w") as f:
                json.dump({"witnesses": witnesses, "control": control,
                           "other": {str(k): v for k, v in other.items()},
                           "scanned": scanned, "collect_secs": collect_secs}, f)

    result = {
        "n": N, "n_scanned": scanned, "collect_secs": round(collect_secs, 1),
        "num_witnesses_prime_tww1_o2_c3": len(witnesses),
        "num_control_prime_tww1_o2_c2": len(control),
        "other_cells": {str(k): v for k, v in (other.items() if isinstance(other, dict) else [])},
    }

    iso = IsoClasses()
    # (a) minimal chi-3 cores across all witnesses
    witness_core_size = Counter()
    witness_core_multiset = Counter()          # iso-key -> #witnesses containing it
    per_witness_cores = []
    universal_cores = None
    for arcs in witnesses:
        size, cores = min_chi3_cores(N, arcs, iso)
        witness_core_size[size] += 1
        for c in cores:
            witness_core_multiset[c] += 1
        per_witness_cores.append(sorted([str(c) for c in cores]))
        cores_set = set(cores)
        universal_cores = cores_set if universal_cores is None else (universal_cores & cores_set)
    result["witness_min_chi3_core_size_dist"] = dict(witness_core_size)
    result["num_distinct_chi3_cores_in_witnesses"] = len(witness_core_multiset)
    result["chi3_core_occurrence"] = {str(k): v for k, v in
                                      sorted(witness_core_multiset.items(), key=lambda x: -x[1])}
    result["universal_chi3_core_present_in_ALL_witnesses"] = \
        [str(c) for c in (universal_cores or set())]
    result["num_universal_chi3_cores"] = len(universal_cores or set())

    if not core_only:
        # (b) does the SAME minimal chi-3 core appear in controls? (controls have
        #     chi=2, so by definition they contain NO chi-3 sub-tournament --
        #     this is the trivial discriminator; record it explicitly as a sanity
        #     check / floor.)
        # Instead the meaningful contrast: 7-vertex induced sub-tournament
        # PROFILE. Compare the multiset of 7-vtx iso-classes in witnesses vs a
        # control sample to see if a NON-chi3 sub-pattern also discriminates.
        def seven_profile(arcs):
            A = core._adj(N, arcs)
            keys = set()
            for verts in itertools.combinations(range(N), 7):
                sn, sarcs = sub_arcs(A, list(verts))
                keys.add(iso.key(sn, sarcs))
            return keys
        wit_seven = [seven_profile(a) for a in witnesses]
        univ_seven_wit = set.intersection(*wit_seven) if wit_seven else set()
        cs = control[:control_sample]
        ctrl_seven = [seven_profile(a) for a in cs]
        # 7-classes present in EVERY witness but NO control in the sample
        ctrl_union = set().union(*ctrl_seven) if ctrl_seven else set()
        discriminating7 = univ_seven_wit - ctrl_union
        result["num_7vtx_classes_in_every_witness"] = len(univ_seven_wit)
        result["control_sample_size"] = len(cs)
        result["num_7vtx_classes_in_every_witness_but_no_control"] = len(discriminating7)
        result["discriminating_7vtx_classes"] = [str(c) for c in discriminating7]

        # (c) back-edge graph at omega-optimal ordering for each witness
        be = [be_graph_at_optimal(N, a) for a in witnesses]
        result["be_optimal_found_count"] = sum(1 for b in be if b.get("found_optimal"))
        result["be_forest_count"] = sum(1 for b in be if b.get("be_is_forest"))
        result["be_bipartite_count"] = sum(1 for b in be if b.get("be_is_bipartite"))
        result["be_triangle_counts"] = Counter(b.get("be_triangles") for b in be)
        result["be_num_edges_dist"] = dict(Counter(b.get("be_num_edges") for b in be))
        result["be_examples"] = be[:5]

    return result


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--control-sample", type=int, default=200)
    ap.add_argument("--core-only", action="store_true")
    ap.add_argument("--cache", default="data/h10_witnesses.json")
    a = ap.parse_args()
    out = run(a.control_sample, a.core_only, a.cache)
    # Counters aren't json-serializable as-is in nested places; coerce
    def coerce(o):
        if isinstance(o, Counter):
            return {str(k): v for k, v in o.items()}
        return str(o)
    print(json.dumps(out, indent=2, default=coerce))
