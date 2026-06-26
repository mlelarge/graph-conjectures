#!/usr/bin/env python3
"""Verify the intermediate-cut counterexample to general L-exist.

The support graph is the path 1-0-2-3. Every support edge is replaced by
three parallel arcs in each direction. For root 2 and any labelled copy
of a=(0,2), every arc-disjoint ordered in-arborescence pair (T,U) with
a in T fails the strict-exit condition on X_a^T={0,1}.
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check_lexist
import oracle


def build():
    support_edges = [(1, 0), (0, 2), (2, 3)]
    arcs = []
    for u, v in support_edges:
        arcs.extend([(u, v)] * 3)
        arcs.extend([(v, u)] * 3)
    return 4, arcs


def main():
    n, arcs = build()
    labeled = check_lexist.label_arcs(arcs)
    root = 2
    arbs = list(check_lexist._spanning_in_arborescences(n, labeled, root))
    arc_by_label = {arc[2]: arc for arc in labeled}
    distinguished = [arc for arc in labeled if arc[:2] == (0, 2)]

    per_copy = []
    total_pairs = 0
    total_strict = 0
    all_subtrees = set()
    for a in distinguished:
        pairs = 0
        strict = 0
        for t_labels, t_parent in arbs:
            if a[2] not in t_labels:
                continue
            x = check_lexist._subtree_below((0, 2), t_parent, n, root)
            all_subtrees.add(frozenset(x))
            for u_labels, u_parent in arbs:
                if t_labels & u_labels:
                    continue
                pairs += 1
                if check_lexist._strict_exit_exists(
                    x, u_parent, n, root, arc_by_label, u_labels
                ):
                    strict += 1
        per_copy.append((a[2], pairs, strict))
        total_pairs += pairs
        total_strict += strict

    indegree = [0] * n
    outdegree = [0] * n
    for u, v in arcs:
        outdegree[u] += 1
        indegree[v] += 1

    result = {
        "lambda": oracle.arc_connectivity(n, arcs),
        "eulerian": indegree == outdegree,
        "n_rooted_in_arborescences": len(arbs),
        "distinguished_labels": [a[2] for a in distinguished],
        "per_copy_pairs_and_strict": per_copy,
        "aggregate_pairs": total_pairs,
        "aggregate_strict": total_strict,
        "subtrees": sorted(sorted(x) for x in all_subtrees),
    }
    expected = {
        "lambda": 3,
        "eulerian": True,
        "n_rooted_in_arborescences": 27,
        "aggregate_pairs": 216,
        "aggregate_strict": 0,
        "subtrees": [[0, 1]],
    }
    for key, value in expected.items():
        if result[key] != value:
            raise AssertionError((key, result[key], value))
    if any(pairs != 72 or strict != 0 for _, pairs, strict in per_copy):
        raise AssertionError(per_copy)

    for key, value in result.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
