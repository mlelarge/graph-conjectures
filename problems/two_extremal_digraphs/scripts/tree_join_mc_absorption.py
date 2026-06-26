#!/usr/bin/env python3
"""
Interior-interface / multi-A-edge absorption probe for the MC-inheritance lemma.

Context.  `tree_join_mc_inheritance.py` tested the heuristic

    persistent mixed cut in an A-block  =>  output has MC=1

over ONE-A-edge tree joins whose single A-edge touches a leaf.  In that regime
NO block mixed cut is ever absorbed (persistent OR not), so the probe does not
exercise the only mechanism by which inheritance could fail.  See the review in
docs/tree_join_mc_inheritance.md.

Mechanism of absorption (worked out explicitly).  A block mixed cut (v,e) splits
the A-block into sides sharing v.  External tree/rim structure attaches to the
block ONLY through its two interface vertices p,q (the designated digon).  So the
output reconnects the two sides of the cut iff p and q lie on DIFFERENT sides --
i.e. the cut SEPARATES the interface pair -- because then an external p..q path
(avoiding v) bridges the cut.  Such a cut is necessarily NON-persistent: every
separated component contains an interface vertex, so there is no interface-free
component.  Conversely a PERSISTENT cut has an interface-free component with no
external attachment, so deleting (v,e) still isolates it -- the cut must survive.

This is exactly the lemma's content.  To put it at risk we need:
  (a) interior A-edges (interface vertices are interior tree nodes, hence attached
      to external structure on BOTH sides), and
  (b) rims beyond the old leaf-edge case, including proper >=3-leaf peripheral
      cycles (we also retain the 2-leaf path4 digon-rim control), and
  (c) A-blocks possessing a mixed cut that separates their interface pair.

The probe builds such tree joins, maps every A-block mixed cut into the output,
classifies it (interface-free? separates-interface?), and checks whether it
SURVIVES as an output mixed cut.  Two questions:

  Q-VIOLATION  Does any INTERFACE-FREE (persistent) cut fail to survive?
               (would REFUTE the lemma)
  Q-SEPARATE   Does any cut ever SEPARATE the interface pair?  (the only route to
               absorption; if always 0 then no cut can be absorbed, and -- by the
               step-3 argument below -- every cut is interface-free, so the
               "persistence" hypothesis does no work: it holds vacuously)

RESULT (2026-06-01; labels corrected 2026-06-02).  Over 5223 distinct 2-extremal
outputs and 4276 block-cut triples, with interior A-edges, up to 2 A-edges, and
rims of size 2 (path4: 4390 outputs) and >=3 (spider3/cat3/h: 833 outputs):

    (interface_free, separates, survived) = (True, False, True) : 4276/4276
    Q-VIOLATION (interface-free cut absorbed)                    : 0
    interface-separating cuts observed                          : 0
    corollary: MC=0 outputs 1841, out_mc<sum(block MC) 0,
               MC=0-output-with-MC-block 0, cut-map injectivity 0

Note: 'interface_free' here is the CORRECTED persistence predicate
(`has_interface_free_component` below), which -- unlike the earlier
tree_join_mc_inheritance guard -- counts a cut whose vertex is an interface
endpoint as persistent (the proof's step 3).  Under it EVERY block mixed cut is
persistent, so the single tally row above is the whole content.

The reason absorption never fires is structural, not numerical -- and it upgrades
the inheritance heuristic to a PROVED lemma (n-independent):

  (1) The interface (p,q) is a DIGON (Def 9.1: [u_i,v_i] subset A(D_i)).  So the
      underlying edge p-q exists and is NOT a single edge.
  (2) A mixed 2-cut deletes a vertex v and a SINGLE edge e.  As e is single,
      e != {p,q}; the digon edge p-q is removed only if v in {p,q}.  Hence no
      mixed cut puts p,q in distinct components -- it never separates the
      interface.  [empirically: 0/264 over all blocks L3..L7]
  (3) A mixed cut has >=2 components; with only TWO interface vertices, if none
      is interface-free then exactly two components split p,q -- impossible by
      (2).  So EVERY block mixed cut is persistent.  (If v in {p,q}, the other
      interface vertex still leaves an interface-free component.)
  (4) A persistent cut's interface-free component C is internal to D_i; external
      structure attaches to D_i only at p,q not in C, so C stays isolated in
      U(D')-v'-e', and e' stays single (>=1 endpoint internal, only D_i feeds
      arcs there).  So (v',e') is a mixed cut of the output.

Conclusion: EVERY mixed 2-cut of EVERY A-block survives any 2-Hajos tree join.
The "persistent / interface-free component" framing of the earlier probe was the
wrong abstraction; the operative fact is simply that the interface is a digon.

Direct corollary for R-b (proved): MC(output) >= sum of MC(blocks), so an MC=0
2-Hajos tree join uses ONLY MC=0 A-blocks (+ base objects).  The recursive MC=0
descent therefore stays inside the MC=0 class -- it cannot launder an MC>=1 block
into an MC=0 output.  (This bounds R-b's recursion; it does NOT establish R-b's
existence half, which remains open.)

This script is the bounded adversarial cross-check of that proof.
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
from seam_invariant import mixed_2_cuts  # noqa: E402
from two_hajos_tree_join import (  # noqa: E402
    build_tree_join,
    even_leaf_parity,
    leaf_circular_order,
)
from tree_join_mc_inheritance import load_blocks  # noqa: E402

OUTPUT_N_CAP = 11


def has_interface_free_component(n, arcs, cut, interface):
    """Corrected 'persistent' predicate matching the proof.

    True iff deleting cut=(v,e) from U(block) leaves a component containing
    NEITHER interface endpoint.  Unlike the earlier
    `tree_join_mc_inheritance.cut_has_interface_free_component`, there is NO
    interface-avoidance guard: when v is itself an interface endpoint, the
    removed vertex is in no component, so a component free of the OTHER endpoint
    still counts as interface-free (exactly the case step (3) of the proof
    relies on).  The earlier guard mislabelled those cuts as non-persistent.
    """
    v, e = cut
    removed_edge = frozenset(e)
    remaining = [x for x in range(n) if x != v]
    adj = {x: set() for x in remaining}
    for a, b in arcs:
        if a == v or b == v:
            continue
        if frozenset((a, b)) == removed_edge:
            continue
        adj[a].add(b)
        adj[b].add(a)
    seen = set()
    for start in remaining:
        if start in seen:
            continue
        stack = [start]
        seen.add(start)
        comp = set()
        while stack:
            x = stack.pop()
            comp.add(x)
            for y in adj[x]:
                if y not in seen:
                    seen.add(y)
                    stack.append(y)
        if comp.isdisjoint(interface):
            return True
    return False


# --------------------------------------------------------------------------
# Plane-tree templates.  ALL provide INTERIOR A-edge candidates.  Rim sizes:
# path4 has 2 leaves (a 2-leaf peripheral DIGON), spider3/cat3/h have proper
# >=3-leaf rims.  We keep path4 because it adds interior + 2-A-edge coverage;
# the proof is rim-independent, but the printed breakdown reports rim size so
# the >=3-leaf contribution is explicit (the earlier probe had ONLY 2-leaf rims
# with the A-edge at a leaf).
# Each returns (m, root, children, edges).
# --------------------------------------------------------------------------

def t_path4():
    # 0-1-2-3-4 ; interior edges (1,2),(2,3) ; leaves {0,4}  -> 2-leaf digon rim
    return 5, 0, {0: [1], 1: [2], 2: [3], 3: [4], 4: []}, [
        (0, 1), (1, 2), (2, 3), (3, 4)]


def t_spider3():
    # centre 0, three arms of length 2 ; leaves {4,5,6} (proper 3-rim)
    return 7, 0, {0: [1, 2, 3], 1: [4], 2: [5], 3: [6], 4: [], 5: [], 6: []}, [
        (0, 1), (1, 4), (0, 2), (2, 5), (0, 3), (3, 6)]


def t_caterpillar3():
    # spine 0-1-2 with one pendant leaf each ; leaves {3,4,5} (proper 3-rim)
    # interior edges (0,1),(1,2)
    return 6, 0, {0: [3, 1], 1: [4, 2], 2: [5], 3: [], 4: [], 5: []}, [
        (0, 3), (0, 1), (1, 4), (1, 2), (2, 5)]


def t_h():
    # two centres 0-1 ; 0 has leaves 2,3 ; 1 has leaves 4,5 (proper 4-rim)
    # the single interior edge is (0,1)
    return 6, 0, {0: [2, 3, 1], 1: [4, 5], 2: [], 3: [], 4: [], 5: []}, [
        (0, 2), (0, 3), (0, 1), (1, 4), (1, 5)]


TEMPLATES = [
    ("path4", t_path4),
    ("spider3", t_spider3),
    ("cat3", t_caterpillar3),
    ("h", t_h),
]


def interior_nodes(m, edges):
    deg = [0] * m
    for u, v in edges:
        deg[u] += 1
        deg[v] += 1
    return {u for u in range(m) if deg[u] >= 2}


# --------------------------------------------------------------------------
# Builder that ALSO returns, per A-edge, the block-vertex -> output-vertex map.
# Vertex-id assignment is identical to build_tree_join (same edge order, same
# fresh-id counter), so outputs coincide; we assert this in the self-test.
# --------------------------------------------------------------------------

def build_with_maps(m, edges, children, root, labels, gadgets):
    arcs = set()
    nxt = m
    maps = {}
    for e in edges:
        u, v = e
        if labels[e] == "B":
            arcs.add((u, v))
            arcs.add((v, u))
            continue
        ni, ai, (p, q) = gadgets[e]
        mp = {}
        for x in range(ni):
            if x == p:
                mp[x] = u
            elif x == q:
                mp[x] = v
            else:
                mp[x] = nxt
                nxt += 1
        for (a, b) in ai:
            if (a, b) == (p, q) or (a, b) == (q, p):
                continue
            x, y = mp[a], mp[b]
            if x != y:
                arcs.add((x, y))
        maps[e] = mp
    leaves = leaf_circular_order(children, root, m)
    if len(leaves) >= 2:
        for i in range(len(leaves)):
            arcs.add((leaves[i], leaves[(i + 1) % len(leaves)]))
    return frozenset(arcs), nxt, maps


def cut_separates_interface(n, arcs, cut, interface):
    """True iff deleting cut=(v,e) puts the two interface vertices in distinct
    components of U(block)-v-e (and neither is v)."""
    v, e = cut
    p, q = interface
    if v in (p, q):
        return False
    removed_edge = frozenset(e)
    remaining = [x for x in range(n) if x != v]
    adj = {x: set() for x in remaining}
    for a, b in arcs:
        if a == v or b == v:
            continue
        if frozenset((a, b)) == removed_edge:
            continue
        adj[a].add(b)
        adj[b].add(a)
    # component of p
    seen = {p}
    stack = [p]
    while stack:
        x = stack.pop()
        for y in adj[x]:
            if y not in seen:
                seen.add(y)
                stack.append(y)
    return q not in seen


def main():
    blocks = load_blocks(7)
    seen = set()
    # tallies over all (output, A-block, block-cut) triples
    tally = Counter()  # (interface_free, separates_iface, survived) -> count
    violations = []   # interface-free cut that did NOT survive  (refutes lemma)
    absorptions = []  # non-interface-free cut that did NOT survive
    n_outputs = 0
    rim_outputs = Counter()      # rim size -> #distinct outputs
    tmpl_outputs = Counter()     # template -> #distinct outputs
    # corollary cross-checks (folded in so one run reproduces every doc number)
    mc0_outputs = 0
    corollary_bad = 0            # out_mc < sum of block MCs
    mc0_with_mc_block = 0        # MC=0 output whose A-block has MC>0
    injectivity_bad = 0          # mapped block cuts collide / miss the output set

    for tname, maker in TEMPLATES:
        m, root, children, edges = maker()
        interior = interior_nodes(m, edges)
        rim_size = len(leaf_circular_order(children, root, m))
        for bits in itertools.product("AB", repeat=len(edges)):
            a_idx = [i for i, b in enumerate(bits) if b == "A"]
            if not (1 <= len(a_idx) <= 2):
                continue
            # require at least one A-edge interior (both endpoints interior)
            if not any(edges[i][0] in interior and edges[i][1] in interior
                       for i in a_idx):
                continue
            labels = {edges[i]: bits[i] for i in range(len(edges))}
            if not even_leaf_parity(edges, labels, children, root, m)[0]:
                continue
            a_edges = [edges[i] for i in a_idx]

            # cap per-edge block order so output stays <= OUTPUT_N_CAP
            budget = OUTPUT_N_CAP - m
            cand = [b for b in blocks if (b["n"] - 2) <= budget]

            def gadget_choices(edge_list, remaining):
                if not edge_list:
                    yield {}
                    return
                e0 = edge_list[0]
                for blk in cand:
                    if (blk["n"] - 2) > remaining:
                        continue
                    for iface in blk["digons"]:
                        head = {e0: (blk, iface)}
                        for tail in gadget_choices(
                                edge_list[1:], remaining - (blk["n"] - 2)):
                            d = dict(head)
                            d.update(tail)
                            yield d

            for choice in gadget_choices(a_edges, budget):
                gadgets = {e: (blk["n"], blk["arcs"], iface)
                           for e, (blk, iface) in choice.items()}
                arcs, n, maps = build_with_maps(
                    m, edges, children, root, labels, gadgets)
                if n > OUTPUT_N_CAP:
                    continue
                # cross-check against the trusted constructor
                ref = build_tree_join(m, edges, {}, children, root, labels,
                                      gadgets)
                assert ref is not None and ref[0] == arcs and ref[1] == n
                if not H.is_2extremal(n, arcs):
                    continue
                key = f"{n}|" + ";".join(
                    f"{u},{v}" for (u, v) in sorted(arcs))
                if key in seen:
                    continue
                seen.add(key)
                n_outputs += 1
                rim_outputs[rim_size] += 1
                tmpl_outputs[tname] += 1

                out_cuts = {(v, frozenset(e)) for (v, e) in mixed_2_cuts(n, arcs)}
                out_mc = len(out_cuts)

                mapped_cuts = []          # for injectivity check on this output
                sum_block_mc = 0
                any_block_mc = False
                for e, (blk, iface) in choice.items():
                    mp = maps[e]
                    sum_block_mc += len(blk["mc"])
                    if blk["mc"]:
                        any_block_mc = True
                    for (cv, ce) in blk["mc"]:
                        interface_free = has_interface_free_component(
                            blk["n"], blk["arcs"], (cv, ce), iface)
                        separates = cut_separates_interface(
                            blk["n"], blk["arcs"], (cv, ce), iface)
                        a, b = tuple(ce)
                        mapped = (mp[cv], frozenset((mp[a], mp[b])))
                        survived = mapped in out_cuts
                        mapped_cuts.append(mapped)
                        tally[(interface_free, separates, survived)] += 1
                        rec = {
                            "tree": tname, "labels": "".join(bits), "n": n,
                            "block": blk["name"], "interface": list(iface),
                            "cut_v": cv, "cut_e": sorted(ce),
                            "interface_free": interface_free,
                            "separates": separates,
                            "survived": survived, "out_mc": out_mc,
                        }
                        if interface_free and not survived:
                            violations.append(rec)
                        if (not interface_free) and (not survived):
                            absorptions.append(rec)

                # corollary cross-checks
                if out_mc < sum_block_mc:
                    corollary_bad += 1
                # injectivity: distinct block cuts -> distinct output cuts, all present
                if len(set(mapped_cuts)) != len(mapped_cuts) or \
                        any(mc not in out_cuts for mc in mapped_cuts):
                    injectivity_bad += 1
                if out_mc == 0:
                    mc0_outputs += 1
                    if any_block_mc:
                        mc0_with_mc_block += 1

    print("# interior / multi-A-edge absorption probe")
    print(f"distinct 2-extremal outputs: {n_outputs}")
    print(f"  by rim size  : {dict(sorted(rim_outputs.items()))}"
          f"   (rim=2 is a peripheral digon; rim>=3 is a proper cycle)")
    print(f"  by template  : {dict(tmpl_outputs)}")
    print(f"block-cut triples examined : {sum(tally.values())}")
    print()
    print("# (interface_free, separates_interface, survived_in_output): count")
    for k in sorted(tally):
        print(f"  {k}: {tally[k]}")
    print()
    print("# corollary cross-checks (in-script, reproducible from this run)")
    print(f"  MC=0 outputs                                : {mc0_outputs}")
    print(f"  outputs with out_mc < sum(block MC)         : {corollary_bad}")
    print(f"  MC=0 outputs whose A-block has MC>0         : {mc0_with_mc_block}")
    print(f"  outputs violating cut-map injectivity/survival: {injectivity_bad}")
    print()
    triples = sum(tally.values())
    n_iface_free = sum(v for k, v in tally.items() if k[0])
    n_separates = sum(v for k, v in tally.items() if k[1])
    n_survived = sum(v for k, v in tally.items() if k[2])
    print(f"Q-VIOLATION  interface-free cuts absorbed (REFUTES lemma): {len(violations)}")
    print(f"all block mixed cuts are interface-free (proof step 3)  : "
          f"{n_iface_free}/{triples}")
    print(f"block mixed cuts that SEPARATE the interface (step 2)   : "
          f"{n_separates}/{triples}")
    print(f"block mixed cuts that SURVIVE in the output (step 4)    : "
          f"{n_survived}/{triples}")
    print(f"absorptions of NON-interface-free cuts (none exist)     : "
          f"{len(absorptions)}")

    if violations:
        print("\n# LEMMA VIOLATIONS (interface-free cut did not survive)")
        for r in violations[:20]:
            print(json.dumps(r, sort_keys=True))
    if absorptions:
        print("\n# ABSORPTIONS (non-interface-free cut killed) -- first few")
        for r in absorptions[:12]:
            print(json.dumps(r, sort_keys=True))

    return 1 if violations else 0


if __name__ == "__main__":
    raise SystemExit(main())
