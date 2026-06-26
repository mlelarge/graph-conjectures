#!/usr/bin/env python3
"""
Probe a structural inheritance principle for the MC=0 tree-join side.

Working lemma under test:

    If an A-block used in a 2-Hajos tree join has a mixed 2-cut
    (vertex v, single edge e) leaving a component with neither designated
    interface endpoint, then the joined digraph should also have MC=1.

This matters for the remaining R-b obstruction.  A minimal MC=0 tree-join
counterexample cannot contain a recursively Hajós-seamed A-block unless every
mixed cut of that block is absorbed by the two interface endpoints.  The script
does not prove the lemma; it generates small forward tree joins and checks for
violations.
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
from two_hajos_tree_join import build_tree_join, even_leaf_parity  # noqa: E402


def make_path(k):
    m = k + 1
    root = 0
    children = {i: [i + 1] for i in range(k)}
    children[k] = []
    edges = [(i, i + 1) for i in range(k)]
    return m, root, children, edges


def make_star(k):
    m = k + 1
    root = 0
    children = {0: list(range(1, k + 1))}
    for i in range(1, k + 1):
        children[i] = []
    edges = [(0, i) for i in range(1, k + 1)]
    return m, root, children, edges


def make_caterpillar():
    m = 4
    root = 0
    children = {0: [1], 1: [2, 3], 2: [], 3: []}
    edges = [(0, 1), (1, 2), (1, 3)]
    return m, root, children, edges


TREE_TEMPLATES = [
    ("path2", lambda: make_path(2)),
    ("path3", lambda: make_path(3)),
    ("path4", lambda: make_path(4)),
    ("star3", lambda: make_star(3)),
    ("cat", make_caterpillar),
]


def load_blocks(max_block_n):
    blocks = []
    for n in range(3, max_block_n + 1):
        path = os.path.join(ROOT, "data", f"L_{n}.json")
        if not os.path.exists(path):
            continue
        with open(path) as fp:
            for idx, obj in enumerate(json.load(fp)):
                arcs = frozenset(tuple(a) for a in obj["arcs"])
                digons = sorted(
                    (u, v)
                    for (u, v) in arcs
                    if u < v and (v, u) in arcs
                )
                if digons:
                    blocks.append(
                        {
                            "name": f"L{n}.{idx}",
                            "n": n,
                            "arcs": arcs,
                            "digons": digons,
                            "base": (
                                H.is_symmetric_odd_cycle(n, arcs)
                                or H._is_generalised_wheel(n, arcs)
                            ),
                            "mc": mixed_2_cuts(n, arcs),
                        }
                    )
    return blocks


def cut_avoids_interface(cut, interface):
    v, e = cut
    return v not in interface and not (set(e) & set(interface))


def cut_has_interface_free_component(n, arcs, cut, interface):
    """Historical guarded persistence predicate used for the first probe.

    Deprecated for the proved MC-inheritance lemma: this deliberately returns
    False when the cut touches the interface, which mislabels cuts whose deleted
    vertex is an interface endpoint.  Use
    `tree_join_mc_absorption.has_interface_free_component` for the corrected
    proof predicate.

    True iff deleting cut=(v,e) leaves a component with neither interface
    endpoint, subject to the historical interface-avoidance guard. Such a
    component cannot be reconnected by the ambient tree join, whose external
    attachments enter this A-block only through the interface.
    """
    if not cut_avoids_interface(cut, interface):
        return False
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


def _label_key(n, arcs):
    """Fast labelled key.  We deliberately avoid canonical isomorphism here:
    this is a forward stress test, not an isomorphism census, and brute-force
    canonicalization becomes expensive at n >= 10."""
    return f"{n}|" + ";".join(f"{u},{v}" for (u, v) in sorted(arcs))


def one_a_edge_joins(max_output_n=9, max_block_n=7):
    blocks = load_blocks(max_block_n)
    seen = set()
    rows = []
    violations = []

    for tree_name, maker in TREE_TEMPLATES:
        m, root, children, edges = maker()
        for bits in itertools.product("AB", repeat=len(edges)):
            a_edges = [edges[i] for i, b in enumerate(bits) if b == "A"]
            if len(a_edges) != 1:
                continue
            labels = {edges[i]: bits[i] for i in range(len(edges))}
            parity_ok, _ = even_leaf_parity(edges, labels, children, root, m)
            if not parity_ok:
                continue

            a_edge = a_edges[0]
            for block in blocks:
                for interface in block["digons"]:
                    gadgets = {
                        a_edge: (
                            block["n"],
                            block["arcs"],
                            interface,
                        )
                    }
                    built = build_tree_join(
                        m,
                        edges,
                        parent={},
                        children=children,
                        root=root,
                        labels=labels,
                        gadgets=gadgets,
                    )
                    if built is None:
                        continue
                    arcs, n = built
                    if n > max_output_n:
                        continue
                    if not H.is_2extremal(n, arcs):
                        continue

                    key = _label_key(n, arcs)
                    if key in seen:
                        continue
                    seen.add(key)

                    out_mc = mixed_2_cuts(n, arcs)
                    persistent_cuts = [
                        c
                        for c in block["mc"]
                        if cut_has_interface_free_component(
                            block["n"], block["arcs"], c, interface
                        )
                    ]
                    row = {
                        "n": n,
                        "tree": tree_name,
                        "labels": "".join(bits),
                        "block": block["name"],
                        "block_base": block["base"],
                        "interface": list(interface),
                        "block_mc": len(block["mc"]),
                        "block_persistent_mc": len(persistent_cuts),
                        "output_mc": len(out_mc),
                        "output_hajos": any(
                            True for _ in H._hajos_decompositions(n, arcs)
                        ),
                        "output_base": (
                            H.is_symmetric_odd_cycle(n, arcs)
                            or H._is_generalised_wheel(n, arcs)
                        ),
                        "label_key": key,
                    }
                    rows.append(row)
                    if persistent_cuts and not out_mc:
                        violations.append(row)

    return rows, violations


def main():
    rows, violations = one_a_edge_joins()
    print("# one-A-edge tree-join MC inheritance probe")
    print(f"outputs tested: {len(rows)}")
    print(f"violations: {len(violations)}")

    by_status = Counter(
        (
            r["block_base"],
            r["block_mc"] > 0,
            r["block_persistent_mc"] > 0,
            r["output_mc"] > 0,
            r["output_base"],
        )
        for r in rows
    )
    print("# (block_base, block_MC, block_persistent_MC, output_MC, output_base)")
    for key, count in sorted(by_status.items(), key=lambda kv: (kv[0], kv[1])):
        print(f"{count:3d} {key}")

    if violations:
        print("# VIOLATIONS")
        for row in violations:
            print(json.dumps(row, sort_keys=True))

    mc0_nonbase = [
        row for row in rows if row["output_mc"] == 0 and not row["output_base"]
    ]
    print(f"# MC=0 non-base outputs: {len(mc0_nonbase)}")
    print("# MC=0 non-base outputs by A-block")
    for block, count in sorted(Counter(r["block"] for r in mc0_nonbase).items()):
        print(f"{count:3d} {block}")
    print("# first MC=0 non-base outputs")
    for row in mc0_nonbase[:12]:
        print(json.dumps(row, sort_keys=True))

    return 1 if violations else 0


if __name__ == "__main__":
    raise SystemExit(main())
