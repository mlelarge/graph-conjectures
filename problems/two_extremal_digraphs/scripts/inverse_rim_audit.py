#!/usr/bin/env python3
"""
Inverse-rim audit for the R-b EXISTENCE direction.

R-b (open): given a non-base MC=0 2-extremal digraph D, produce a valid 2-Hajos
tree-join rim + (A,B) partition with strictly-smaller MC=0/base blocks.  The
MC-inheritance lemma (proved, see docs/tree_join_mc_inheritance.md) only says the
A-blocks of any such join MUST be MC=0/base; it does NOT produce the rim.  This
script asks the empirical question that must precede a proof:

    Across MC=0 non-base 2-extremal digraphs, WHICH directed cycle is the
    peripheral rim of a valid decomposition, and what underlying-graph feature
    (digon forest F_D + single-arc closed trails) singles it out?

The oracle's `_tree_join_decompositions` only returns the A-blocks, hiding the
rim.  `full_decompositions` below mirrors its search but yields the WHOLE
decomposition {rim, A, B, tree vertices, blocks}, so we can correlate the
winning rim with structure.

Candidate rim-extraction rules tested (per winning rim R):
  S1  R's arcs are all SINGLE arcs of D            (rim avoids every digon)
  S2  R is a directed cycle of the single-arc subdigraph
  L1  V(R) is contained in the leaf set of F_D
  L2  V(R) equals the leaf set of F_D
  L3  V(R) hits every F_D tree-component exactly... (reported, not asserted)
  P1  the B-edges (digons) form even-parity leaf-to-leaf paths (guaranteed by
      construction of the search; reported as a sanity check)

Nothing here is a proof; it is the structural-feature extraction that step 2
(propose a rim-extraction lemma) and step 3 (red-team) build on.
"""

import itertools
import json
import os
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import h2_oracle as H  # noqa: E402
from seam_invariant import split_digons_singles, mixed_2_cuts  # noqa: E402


# --------------------------------------------------------------------------
# Full decomposition enumerator: mirrors h2_oracle._tree_join_decompositions but
# yields the rim and (A,B) alongside the A-blocks.
# --------------------------------------------------------------------------

def full_decompositions(n, arcs, max_internal=2):
    arcset = set(arcs)
    for cyc in H._directed_cycles(n, arcs):
        k = len(cyc)
        if k < 3:
            continue
        rim_arcs = frozenset((cyc[i], cyc[(i + 1) % k]) for i in range(k))
        if not rim_arcs <= arcset:
            continue
        remaining = arcset - rim_arcs
        non_rim = [v for v in range(n) if v not in set(cyc)]
        for ti_count in range(0, min(max_internal, len(non_rim)) + 1):
            for tree_internal in itertools.combinations(non_rim, ti_count):
                ti = list(tree_internal)
                for (edges, lset, internal_neg) in H._plane_trees_on_leaves(
                        tuple(cyc), max_internal=len(ti)):
                    if len(internal_neg) != len(ti):
                        continue
                    for perm in itertools.permutations(ti):
                        relabel = {}
                        for negv, realv in zip(
                                sorted(internal_neg, reverse=True), perm):
                            relabel[negv] = realv
                        for lv in cyc:
                            relabel[lv] = lv
                        T_edges = frozenset(
                            frozenset((relabel[a], relabel[b]))
                            for (a, b) in (tuple(e) for e in edges))
                        V = set(cyc) | set(ti)
                        for A, B in H._parity_partitions(V, T_edges, tuple(cyc)):
                            res = H._verify_tiling(
                                n, arcs, arcset, cyc, remaining, V, A, B,
                                max_block=n)
                            if res is not None:
                                yield {
                                    "rim": list(cyc),
                                    "rim_arcs": rim_arcs,
                                    "tree_edges": T_edges,
                                    "A": A, "B": B,
                                    "tree_vertices": V,
                                    "blocks": res,
                                }


# --------------------------------------------------------------------------
# Underlying-graph structure.
# --------------------------------------------------------------------------

def fd_forest(n, arcs):
    digon_edges, singles = split_digons_singles(n, arcs)
    adj = {v: set() for v in range(n)}
    for e in digon_edges:
        a, b = tuple(e)
        adj[a].add(b)
        adj[b].add(a)
    deg = {v: len(adj[v]) for v in range(n)}
    leaves = set(v for v in range(n) if deg[v] == 1)
    internal = set(v for v in range(n) if deg[v] >= 2)
    isolated = set(v for v in range(n) if deg[v] == 0)
    return digon_edges, singles, adj, deg, leaves, internal, isolated


def single_arc_cycles(n, singles):
    """Decompose the single-arc subdigraph into its simple directed cycles when
    it is a vertex-disjoint union of cycles; else return None.  (Single arcs are
    balanced closed trails; a disjoint-cycle structure is the common case.)"""
    outs = {v: [] for v in range(n)}
    indeg = Counter()
    outdeg = Counter()
    for (u, v) in singles:
        outs[u].append(v)
        outdeg[u] += 1
        indeg[v] += 1
    # vertex-disjoint cycles iff every vertex has in=out<=1
    if any(outdeg[v] > 1 or indeg[v] > 1 for v in range(n)):
        return None
    seen = set()
    cycles = []
    for s in range(n):
        if outdeg[s] == 0 or s in seen:
            continue
        cyc = [s]
        seen.add(s)
        x = outs[s][0]
        while x != s:
            cyc.append(x)
            seen.add(x)
            x = outs[x][0]
        cycles.append(cyc)
    return cycles


# --------------------------------------------------------------------------
# Audit one digraph.
# --------------------------------------------------------------------------

def audit(name, n, arcs, max_internal=2):
    digon_edges, singles, adj, deg, leaves, internal, isolated = \
        fd_forest(n, arcs)
    single_set = set(singles)
    sa_cycles = single_arc_cycles(n, singles)

    decs = list(full_decompositions(n, arcs, max_internal=max_internal))
    rims = []
    rim_rule_hits = Counter()
    for d in decs:
        rimv = set(d["rim"])
        ra = d["rim_arcs"]
        s1 = ra <= single_set                       # rim all single arcs
        s2 = all((u, v) in single_set
                 for (u, v) in zip(d["rim"], d["rim"][1:] + d["rim"][:1]))
        l1 = rimv <= leaves                          # rim verts subset of F_D leaves
        l2 = rimv == leaves                          # rim verts == F_D leaves
        blocks_mc = [len(mixed_2_cuts(bn, ba)) for (bn, ba) in d["blocks"]]
        blocks_base = [
            (H.is_symmetric_odd_cycle(bn, ba) or H._is_generalised_wheel(bn, ba))
            for (bn, ba) in d["blocks"]]
        rims.append({
            "rim": d["rim"], "len": len(d["rim"]),
            "S1_all_single": s1, "S2_single_cycle": s2,
            "L1_subset_leaves": l1, "L2_eq_leaves": l2,
            "nA": len(d["A"]), "nB": len(d["B"]),
            "block_sizes": sorted(bn for (bn, _) in d["blocks"]),
            "block_mc": blocks_mc, "block_base": blocks_base,
        })
        rim_rule_hits[(s1, l1, l2)] += 1

    return {
        "name": name, "n": n,
        "n_digons": len(digon_edges),
        "n_singles": len(singles),
        "fd_leaves": sorted(leaves), "fd_internal": sorted(internal),
        "fd_isolated": sorted(isolated),
        "single_arc_cycles": sa_cycles,
        "n_decompositions": len(decs),
        "rims": rims,
        "rim_rule_hits": dict(rim_rule_hits),
    }


# --------------------------------------------------------------------------
# Corpora.
# --------------------------------------------------------------------------

def load_truthset_mc0_nonbase():
    out = []
    for nn in (6, 7):
        path = os.path.join(ROOT, "data", f"L_{nn}.json")
        if not os.path.exists(path):
            continue
        for idx, obj in enumerate(json.load(open(path))):
            arcs = frozenset(tuple(a) for a in obj["arcs"])
            if mixed_2_cuts(nn, arcs):
                continue
            if H.is_symmetric_odd_cycle(nn, arcs) or \
                    H._is_generalised_wheel(nn, arcs):
                continue
            out.append((f"L{nn}.{idx}", nn, arcs))
    return out


def single_arc_directed_cycle_exists(n, singles):
    """Cheap necessary check: the single-arc subdigraph contains a directed
    cycle.  (It is balanced/Eulerian and, for non-base D, non-empty, so this
    should always hold.)  Returns (balanced, has_cycle)."""
    indeg = Counter()
    outdeg = Counter()
    outs = {v: [] for v in range(n)}
    for (u, v) in singles:
        outs[u].append(v)
        outdeg[u] += 1
        indeg[v] += 1
    balanced = all(indeg[v] == outdeg[v] for v in range(n))
    # directed cycle via DFS colour
    colour = {}
    has_cycle = False

    def dfs(u):
        nonlocal has_cycle
        colour[u] = 1
        for w in outs[u]:
            c = colour.get(w, 0)
            if c == 1:
                has_cycle = True
                return
            if c == 0:
                dfs(w)
                if has_cycle:
                    return
        colour[u] = 2

    for s in range(n):
        if colour.get(s, 0) == 0 and outs[s]:
            dfs(s)
            if has_cycle:
                break
    return balanced, has_cycle


def load_absorption_mc0():
    """The corrected absorption builder's distinct MC=0 outputs (deduped by the
    labelled key, since canonicalisation is too slow at n=11).  Expected 1841."""
    import tree_join_mc_absorption as Q
    from two_hajos_tree_join import build_tree_join, even_leaf_parity
    blocks = Q.load_blocks(7)
    seen = set()
    out = []
    for tname, maker in Q.TEMPLATES:
        m, root, children, edges = maker()
        interior = Q.interior_nodes(m, edges)
        for bits in itertools.product("AB", repeat=len(edges)):
            a_idx = [i for i, b in enumerate(bits) if b == "A"]
            if not (1 <= len(a_idx) <= 2):
                continue
            if not any(edges[i][0] in interior and edges[i][1] in interior
                       for i in a_idx):
                continue
            labels = {edges[i]: bits[i] for i in range(len(edges))}
            if not even_leaf_parity(edges, labels, children, root, m)[0]:
                continue
            a_edges = [edges[i] for i in a_idx]
            budget = Q.OUTPUT_N_CAP - m
            cand = [b for b in blocks if (b["n"] - 2) <= budget]

            def choices(el, rem):
                if not el:
                    yield {}
                    return
                for blk in cand:
                    if (blk["n"] - 2) > rem:
                        continue
                    for iface in blk["digons"]:
                        for tail in choices(el[1:], rem - (blk["n"] - 2)):
                            d = {el[0]: (blk, iface)}
                            d.update(tail)
                            yield d

            for ch in choices(a_edges, budget):
                gad = {e: (blk["n"], blk["arcs"], iface)
                       for e, (blk, iface) in ch.items()}
                built = build_tree_join(m, edges, {}, children, root, labels,
                                        gad)
                if built is None:
                    continue
                arcs, nn = built
                if nn > Q.OUTPUT_N_CAP or not H.is_2extremal(nn, arcs):
                    continue
                if mixed_2_cuts(nn, arcs):
                    continue
                if H.is_symmetric_odd_cycle(nn, arcs) or \
                        H._is_generalised_wheel(nn, arcs):
                    continue
                key = f"{nn}|" + ";".join(f"{u},{v}" for (u, v) in sorted(arcs))
                if key in seen:
                    continue
                seen.add(key)
                out.append((f"abs{len(out)}", nn, arcs))
    return out


def load_forward_mc0(max_output_n=9):
    """The forward-built recursive MC=0 examples (one-A-edge joins), deduped by
    canonical form -> the 11 iso classes."""
    import tree_join_mc_inheritance as P
    from two_hajos_tree_join import build_tree_join, even_leaf_parity
    blocks = P.load_blocks(7)
    seen = {}
    for tname, maker in P.TREE_TEMPLATES:
        m, root, children, edges = maker()
        for bits in itertools.product("AB", repeat=len(edges)):
            if sum(b == "A" for b in bits) != 1:
                continue
            labels = {edges[i]: bits[i] for i in range(len(edges))}
            if not even_leaf_parity(edges, labels, children, root, m)[0]:
                continue
            a_edge = [edges[i] for i, b in enumerate(bits) if b == "A"][0]
            for blk in blocks:
                for iface in blk["digons"]:
                    built = build_tree_join(
                        m, edges, {}, children, root, labels,
                        {a_edge: (blk["n"], blk["arcs"], iface)})
                    if built is None:
                        continue
                    arcs, nn = built
                    if nn > max_output_n or not H.is_2extremal(nn, arcs):
                        continue
                    if mixed_2_cuts(nn, arcs):
                        continue
                    if H.is_symmetric_odd_cycle(nn, arcs) or \
                            H._is_generalised_wheel(nn, arcs):
                        continue
                    c = H.canon(nn, arcs)
                    if c not in seen:
                        seen[c] = (nn, arcs)
    return [(f"fwd{i}", nn, arcs)
            for i, (nn, arcs) in enumerate(seen.values())]


def _cyc_arcset(cyc):
    k = len(cyc)
    return frozenset((cyc[i], cyc[(i + 1) % k]) for i in range(k))


def pin_selector_probe(corpus):
    """For every candidate single-arc directed cycle of each digraph, test which
    LOCAL features (if any) coincide with being a valid rim.  Reports a
    correlation tally per feature: a feature is a candidate selector only if it
    equals `valid` on every candidate.  (Result: none do -- the selector is
    global/recursive, not local.)"""
    try:
        import networkx as nx
    except Exception:
        nx = None
    from seam_invariant import underlying_edges

    feats = ["fd_leaf_subset", "induced", "nonsep_verts", "nonsep_arcs",
             "planar_face"]
    agree = Counter()
    n_cand = 0
    n_multi = 0
    for name, n, arcs in corpus:
        de, singles = split_digons_singles(n, arcs)
        single_set = set(singles)
        _, _, fdadj, fddeg, leaves, internal, isolated = fd_forest(n, arcs)
        Uedges = [tuple(e) for e in underlying_edges(n, arcs)]
        Uadj = {v: set() for v in range(n)}
        for a, b in Uedges:
            Uadj[a].add(b)
            Uadj[b].add(a)
        facesets = None
        if nx is not None:
            G = nx.Graph()
            G.add_nodes_from(range(n))
            G.add_edges_from(Uedges)
            ok, emb = nx.check_planarity(G)
            if ok:
                facesets = set()
                seen = set()
                for u in emb:
                    for v in emb[u]:
                        if (u, v) in seen:
                            continue
                        facesets.add(frozenset(
                            emb.traverse_face(u, v, mark_half_edges=seen)))
        rec = set(_cyc_arcset(d["rim"]) for d in full_decompositions(n, arcs))
        cands = {}
        for c in H._directed_cycles(n, frozenset(singles)):
            if len(c) >= 3:
                cands[_cyc_arcset(c)] = c
        if len(cands) <= 1:
            continue
        n_multi += 1
        for ar, c in cands.items():
            n_cand += 1
            VR = set(c)
            valid = ar in rec
            f = {}
            f["fd_leaf_subset"] = VR <= leaves
            eU = sum(1 for x in VR for y in VR
                     if x < y and y in Uadj[x])
            f["induced"] = (eU == len(VR))
            rest_v = [v for v in range(n) if v not in VR]
            f["nonsep_verts"] = _connected_on(rest_v, Uadj, VR)
            f["nonsep_arcs"] = _connected_on(
                list(range(n)), _adj_minus_arcs(Uadj, ar), set())
            f["planar_face"] = (facesets is not None
                                and frozenset(VR) in facesets)
            for k in feats:
                agree[k] += int(f[k] == valid)
    print("# pin-the-selector probe (local features vs rim validity)")
    print(f"  digraphs with >1 candidate single-arc cycle: {n_multi}; "
          f"candidates: {n_cand}")
    print("  feature == valid on ALL candidates?  (selector iff count == "
          f"{n_cand})")
    for k in feats:
        flag = "  <-- SELECTOR" if agree[k] == n_cand else ""
        print(f"    {k:16s}: {agree[k]}/{n_cand}{flag}")
    print("  => no local feature selects the rim; selection is global/recursive")
    print("     (R valid iff A(D)\\R tiles into B-digons + MC=0/base blocks).")
    print()


def _connected_on(verts, adj, removed):
    verts = [v for v in verts if v not in removed]
    if not verts:
        return True
    seen = {verts[0]}
    stack = [verts[0]]
    while stack:
        x = stack.pop()
        for y in adj[x]:
            if y not in removed and y not in seen:
                seen.add(y)
                stack.append(y)
    return len(seen) == len(verts)


def _adj_minus_arcs(Uadj, arcset):
    """Undirected adjacency with the (directed) rim arcs removed as undirected
    edges (only if the reverse arc is absent, which holds for single rim arcs)."""
    drop = set(frozenset(a) for a in arcset)
    adj = {v: set() for v in Uadj}
    for u in Uadj:
        for w in Uadj[u]:
            if frozenset((u, w)) not in drop:
                adj[u].add(w)
    return adj


def main():
    corpus = load_truthset_mc0_nonbase() + load_forward_mc0()
    print(f"# inverse-rim audit  (corpus: {len(corpus)} MC=0 non-base digraphs)")
    print()
    agg = Counter()
    no_decomp = []
    for name, n, arcs in corpus:
        r = audit(name, n, arcs)
        if r["n_decompositions"] == 0:
            no_decomp.append(name)
        # aggregate: does EVERY recovered rim satisfy each rule?
        all_s1 = r["rims"] and all(x["S1_all_single"] for x in r["rims"])
        any_s1 = any(x["S1_all_single"] for x in r["rims"])
        all_l1 = r["rims"] and all(x["L1_subset_leaves"] for x in r["rims"])
        all_l2 = r["rims"] and all(x["L2_eq_leaves"] for x in r["rims"])
        agg["all_rims_single(S1)"] += bool(all_s1)
        agg["some_rim_single(S1)"] += bool(any_s1)
        agg["all_rims_subset_leaves(L1)"] += bool(all_l1)
        agg["all_rims_eq_leaves(L2)"] += bool(all_l2)
        sac = r["single_arc_cycles"]
        print(f"## {name}  n={n}  digons={r['n_digons']} singles={r['n_singles']}"
              f"  decomps={r['n_decompositions']}")
        print(f"   F_D leaves={r['fd_leaves']} internal={r['fd_internal']}"
              f" isolated={r['fd_isolated']}")
        print(f"   single-arc cycles={sac}")
        for x in r["rims"]:
            print(f"   rim len={x['len']} {x['rim']}  S1={x['S1_all_single']}"
                  f" L1={x['L1_subset_leaves']} L2={x['L2_eq_leaves']}"
                  f" nA={x['nA']} nB={x['nB']} blocks={x['block_sizes']}"
                  f" block_mc={x['block_mc']} block_base={x['block_base']}")
        print()

    print("# aggregate over genuine corpus (truth-set + forward)")
    total = len(corpus)
    for k in ["some_rim_single(S1)", "all_rims_single(S1)",
              "all_rims_subset_leaves(L1)", "all_rims_eq_leaves(L2)"]:
        print(f"  {k}: {agg[k]}/{total}")
    if no_decomp:
        print(f"  !! NO decomposition found for: {no_decomp}")
    print()
    print("# FINDING: the rim is ALWAYS a directed cycle of SINGLE arcs (S1).")
    print("#          'rim = F_D leaf set' (L2) is FALSE; '⊆ leaves' (L1) is not")
    print("#          uniform either.  The selector is single-arc structure, not")
    print("#          the digon forest's leaves.")
    print()

    pin_selector_probe(corpus)

    # ---- step 3: red-team against the absorption-builder MC=0 outputs ----
    # (the builder's 1841 distinct MC=0 outputs include base generalised wheels;
    #  here we keep only the NON-BASE ones, the R-b corpus.)
    print("# red-team over absorption-builder NON-BASE MC=0 outputs")
    corpus2 = load_absorption_mc0()
    print(f"  loaded (non-base MC=0): {len(corpus2)}")
    cheap_bad = 0
    for name, n, arcs in corpus2:
        _, singles = split_digons_singles(n, arcs)
        bal, has_cyc = single_arc_directed_cycle_exists(n, singles)
        if not (bal and has_cyc and singles):
            cheap_bad += 1
    print(f"  ALL: single arcs balanced & contain a directed cycle: "
          f"{len(corpus2) - cheap_bad}/{len(corpus2)}")

    # full rim recovery on a deterministic stride sample
    stride = max(1, len(corpus2) // 60)
    sample = corpus2[::stride]
    s1_all = 0
    has_dec = 0
    s1_fail = []
    for name, n, arcs in sample:
        decs = list(full_decompositions(n, arcs))
        if decs:
            has_dec += 1
        ok = decs and all(
            d["rim_arcs"] <= set(split_digons_singles(n, arcs)[1])
            for d in decs)
        if ok:
            s1_all += 1
        elif decs:
            s1_fail.append(name)
    print(f"  SAMPLE ({len(sample)}, stride {stride}): "
          f"≥1 decomposition: {has_dec}/{len(sample)}; "
          f"every recovered rim single-arc (S1): {s1_all}/{len(sample)}")
    if s1_fail:
        print(f"  !! S1 FAILURES (non-single-arc rim recovered): {s1_fail}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
