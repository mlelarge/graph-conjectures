"""
H6 / Step-1 VERTEX-SPLIT EXPANSION (grounding the explicit-construction proposal).

SEED = the n=7 truth member (oracle-verified this turn: chi_vec=3, lambda_D=2,
is_2extremal=True, is_in_H2=True, node_connectivity = EXACTLY 2):
  arcs7 = [(0,2),(0,4),(0,5),(1,3),(1,6),(2,0),(2,4),(3,5),(3,6),(4,0),(4,6),
           (5,0),(5,1),(6,1),(6,2),(6,3)]
Digon graph F_D has 2 components {0,2,4,5},{1,3,6} (a digon-free cut, k=2),
but the digraph is node-conn 2 (cut-vertex 6 in the 2-cuts).

CONSTRUCTION = split a cut-bearing vertex w into >=2 new vertices, distribute
its incident arcs (digons + single in/out) among the parts, add SINGLE-ARC
(digon-free) connectors among the parts, keeping:
  - Eulerian balance (in=out at every vertex), min in=out >= 2,
  - no parallel arcs / no extra digons across the split connector,
  - F_D still a forest with >=2 components (digon-free cut preserved),
  - lambda_D == 2.
GOAL: lift node-connectivity to >=3 while staying in the H6 antecedent, and
hunt a chi_vec=3 KILL (Step-1 / Conj-9.2 counterexample candidate) or certify
chi=2 (CONFIRM-H6) across the family.

We exhaustively enumerate, for a chosen vertex w with its incident-arc bundle,
every way to:
  (a) partition the digon-partners of w among parts (each part keeps a contiguous
      sub-bundle of digons; each part is a new vertex sharing the partner-digons),
  (b) assign each single in-arc tail and single out-arc head of w to some part,
  (c) add a balancing single-arc structure AMONG the parts (a directed cycle /
      path of single connector arcs) so each part is in=out balanced and the
      parts are strongly tied, with NO digon among parts.
Then feed every resulting digraph to the oracle.

This is a GENERIC expansion generator that PROVABLY reaches H6's 3-connected
antecedent (unlike G13/G14 pinned at lambda=3): a one-vertex split already
produced node-conn>=3 lambda=2 outputs at n=8.
"""
import sys, os, itertools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import h2_oracle as H
import h7_interface_gluing_census as C


SEED = [(0,2),(0,4),(0,5),(1,3),(1,6),(2,0),(2,4),(3,5),(3,6),(4,0),(4,6),
        (5,0),(5,1),(6,1),(6,2),(6,3)]
SEED_N = 7


def incident_bundle(n, arcs, w):
    """Return (digon_partners, in_singles, out_singles) for vertex w."""
    arcset = set(arcs)
    digon_partners, in_singles, out_singles = [], [], []
    for (u, v) in arcset:
        if u == w and (v, u) in arcset:
            digon_partners.append(v)
        elif u == w:
            out_singles.append(v)
        elif v == w and (v, u) not in arcset:
            in_singles.append(u)
    return sorted(set(digon_partners)), sorted(in_singles), sorted(out_singles)


def base_without_vertex(n, arcs, w):
    """Arcs not touching w; remaining vertices relabelled 0..n-2 (drop w)."""
    arcset = set(arcs)
    others = [v for v in range(n) if v != w]
    relabel = {v: i for i, v in enumerate(others)}
    base = set()
    for (u, v) in arcset:
        if u == w or v == w:
            continue
        base.add((relabel[u], relabel[v]))
    return base, relabel, others


def gen_splits(n, arcs, w, nparts):
    """Yield candidate (new_n, new_arcs) digraphs obtained by splitting w into
    `nparts` new vertices. Exhaustive over partitions of the digon-partners and
    assignments of singles, with a single directed connector cycle among parts.

    The new vertices get labels (n-1), n, n+1, ... (i.e. parts P_0..P_{nparts-1}),
    after the other original vertices keep their relabelled ids 0..n-2.
    """
    digon_partners, in_singles, out_singles = incident_bundle(n, arcs, w)
    base, relabel, others = base_without_vertex(n, arcs, w)
    base_n = len(others)               # = n-1
    part_ids = [base_n + i for i in range(nparts)]   # new vertex labels
    new_n = base_n + nparts

    # relabel bundle endpoints into the base labelling
    dp = [relabel[x] for x in digon_partners]
    ins = [relabel[x] for x in in_singles]
    outs = [relabel[x] for x in out_singles]

    # Enumerate assignments of each digon-partner to one of the parts.
    # (Each part may take any subset; every part must end nonempty in the sense
    #  that it has degree -- enforced later by balance/min-deg filter.)
    for dp_assign in itertools.product(range(nparts), repeat=len(dp)):
        # enumerate single-in assignments
        for in_assign in itertools.product(range(nparts), repeat=len(ins)):
            for out_assign in itertools.product(range(nparts), repeat=len(outs)):
                # connector: a directed cycle through ALL parts (single arcs),
                # over every cyclic ordering of the parts; for nparts==2 a single
                # directed cycle is a digon -> NOT allowed (would add a digon),
                # so for 2 parts we instead need >=2 single connector arcs that do
                # NOT form a digon: route one connector forward and balance via the
                # external bundle. We therefore enumerate connector multisets:
                # use a directed cycle on the parts of length nparts when nparts>=3,
                # and for nparts==2 enumerate connector arc-counts c>=1 forward +
                # external balancing.
                yield from _assemble(new_n, base, part_ids, dp, ins, outs,
                                     dp_assign, in_assign, out_assign, nparts)


def _assemble(new_n, base, part_ids, dp, ins, outs,
              dp_assign, in_assign, out_assign, nparts):
    """Build the arc set for one assignment and a choice of connector arcs."""
    # external arcs from the bundle
    ext = set()
    # digons: each digon-partner p attaches to part assigned
    for p, part in zip(dp, dp_assign):
        a = part_ids[part]
        ext.add((a, p)); ext.add((p, a))
    # single in-arcs: tail t -> part
    for t, part in zip(ins, in_assign):
        ext.add((t, part_ids[part]))
    # single out-arcs: part -> head h
    for h, part in zip(outs, out_assign):
        ext.add((part_ids[part], h))

    # compute current imbalance at each part (in - out) from external arcs
    def imb(arcset):
        bal = {pid: 0 for pid in part_ids}
        for (u, v) in arcset:
            if v in bal:
                bal[v] += 1
            if u in bal:
                bal[u] -= 1
        return bal

    base_arcs = set(base) | ext

    # Connector arcs among the parts must (i) add no digon, (ii) no parallel arc,
    # (iii) rebalance each part to in=out. We enumerate connector arc-sets over
    # the directed part-graph (no self loops, no 2-cycles) up to a small budget.
    pidx = list(range(nparts))
    possible_conn = [(part_ids[i], part_ids[j]) for i in pidx for j in pidx if i != j]
    # forbid forming a digon among parts: cannot have both (a,b) and (b,a).
    # enumerate subsets of possible_conn of size up to nparts*2
    max_conn = min(len(possible_conn), nparts + 2)
    for size in range(1, max_conn + 1):
        for combo in itertools.combinations(possible_conn, size):
            # no digon among connectors
            cs = set(combo)
            if any((b, a) in cs for (a, b) in cs):
                continue
            # no parallel with external (ext among parts is empty by construction)
            arcset = base_arcs | cs
            bal = imb(arcset)
            if any(bal[pid] != 0 for pid in part_ids):
                continue
            # min in/out degree >= 2 at parts and no part isolated
            ok = True
            for pid in part_ids:
                indeg = sum(1 for (u, v) in arcset if v == pid)
                outdeg = sum(1 for (u, v) in arcset if u == pid)
                if indeg < 2 or outdeg < 2:
                    ok = False; break
            if not ok:
                continue
            yield (new_n, frozenset(arcset))


def gen_splits_joint(n, arcs, w1, w2, nparts_each=2):
    """Split TWO vertices w1,w2 (w1<w2) simultaneously, each into nparts_each
    parts, to reach larger n (e.g. n=7 -> n=9 with two 2-splits). We do this by
    composing gen_splits: split w2 first (relabels), then split the corresponding
    image of w1 in the new digraph. Yields (new_n, arcs)."""
    # split w2 first; its parts get labels >= n-1; w1 keeps its (relabelled) id.
    for (m1, arcs1) in gen_splits(n, arcs, w2, nparts_each):
        # w1's label after dropping w2: vertices !=w2 are relabelled by removing w2
        others = [v for v in range(n) if v != w2]
        relabel = {v: i for i, v in enumerate(others)}
        w1_new = relabel[w1]
        for (m2, arcs2) in gen_splits(m1, sorted(arcs1), w1_new, nparts_each):
            yield (m2, arcs2)


def run(nparts_list=(2, 3), vertices=(6, 5), max_emit=None):
    results = {"antecedent": 0, "chi3_flags": [], "examples": []}
    seen = set()
    n_eval = 0
    for w in vertices:
        for nparts in nparts_list:
            for (nn, arcs) in gen_splits(SEED_N, SEED, w, nparts):
                n_eval += 1
                # cheap filters first
                if not H.is_eulerian_deg(nn, arcs, min_deg=2):
                    continue
                if not H.is_strong(nn, arcs):
                    continue
                if not H.is_2connected(nn, arcs):
                    continue
                comps = C.digon_components(nn, arcs)
                if len(comps) < 2:
                    continue
                kappa = C.node_connectivity(nn, arcs)
                if kappa < 3:
                    continue
                if not H.lambda_at_most(nn, arcs, 2):
                    continue
                if H.lambda_D(nn, arcs) != 2:
                    continue
                cuts = C.find_digon_free_22_cuts(nn, arcs)
                if not cuts:
                    continue
                cc = H.canon(nn, arcs)
                if cc in seen:
                    continue
                seen.add(cc)
                cv = H.chi_vec(nn, arcs)
                results["antecedent"] += 1
                rec = {"n": nn, "w": w, "nparts": nparts,
                       "arcs": sorted(arcs), "chi_vec": cv,
                       "kappa": kappa, "k_comps": len(comps)}
                if cv == 3:
                    results["chi3_flags"].append(rec)
                else:
                    if len(results["examples"]) < 10:
                        results["examples"].append(rec)
    results["n_eval"] = n_eval
    results["distinct_antecedent"] = len(seen)
    return results


if __name__ == "__main__":
    import json
    res = run(nparts_list=(2, 3), vertices=(6, 5))
    print("candidates evaluated:", res["n_eval"])
    print("DISTINCT H6-antecedent outputs (kappa>=3, lambda=2, Eulerian, digon-free 2/2 cut):",
          res["distinct_antecedent"])
    print("chi_vec=3 KILLS:", len(res["chi3_flags"]))
    print("-" * 60)
    for ex in res["examples"][:5]:
        print(f"  n={ex['n']} w={ex['w']} nparts={ex['nparts']} kappa={ex['kappa']} "
              f"k_comps={ex['k_comps']} chi_vec={ex['chi_vec']}")
        print("    arcs:", ex["arcs"])
    if res["chi3_flags"]:
        print("=" * 60)
        print("!!! chi_vec=3 KILL CANDIDATES (HAND-VERIFY is_in_H2) !!!")
        for rec in res["chi3_flags"]:
            print(json.dumps(rec))
    else:
        print("=" * 60)
        print("0 chi=3 kills -> CONFIRM-H6 across this vertex-split expansion family.")
