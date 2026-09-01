"""Inspect the complement-only excess Hall graph.

This is a diagnostic companion to c2_excess_hall_gate.py.  It searches
2-connected marked graphs with apex-collision excess and reports:

  * Hall-tight subsets of canonical excess vertices;
  * repeated complement lines L(s,w)=L(t,z);
  * per-excess vertex complement-neighborhood sizes.

The goal is to expose the shape of a hypothetical Hall obstruction, not to
serve as a proof gate.
"""
from __future__ import annotations

import argparse
import itertools
import json
import subprocess
import sys
from collections import defaultdict

import networkx as nx

from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core  # noqa: E402


def line_key(line):
    return tuple(sorted(line))


def comparable(dist, u, x, y):
    return dist[u][x] + dist[x][y] == dist[u][y] or dist[u][y] + dist[y][x] == dist[u][x]


def block_data(n, edges, u):
    dist = core.all_pairs_distances(n, edges)
    du = dist[u]
    s_vertices = [x for x in range(n) if x != u]
    full_s = frozenset(s_vertices)

    sigma = {}
    apex = {}
    depth = {s: du[s] for s in s_vertices}
    for s in s_vertices:
        ray = set()
        ap = set()
        for x in s_vertices:
            if comparable(dist, u, x, s):
                ray.add(x)
                ap.add(x)
            elif du[x] + du[s] == dist[x][s]:
                ap.add(x)
        sigma[s] = frozenset(ray)
        apex[s] = frozenset(ap)

    fibers = defaultdict(list)
    for s in s_vertices:
        fibers[sigma[s]].append(s)

    nonreps = []
    for members in fibers.values():
        ordered = sorted(members, key=lambda s: (depth[s], s))
        nonreps.extend(ordered[1:])

    apex_classes = defaultdict(list)
    for s in nonreps:
        apex_classes[apex[s]].append(s)

    duplicated = {ap: ss for ap, ss in apex_classes.items() if len(ss) > 1}
    if not duplicated:
        return None

    excess = []
    class_of = {}
    for ap, members in duplicated.items():
        ordered = sorted(members, key=lambda s: (depth[s], s))
        for s in ordered[1:]:
            excess.append(s)
            class_of[s] = ap

    # Complement-generated line neighborhood for each canonical excess vertex.
    neigh = defaultdict(set)
    witnesses = defaultdict(list)
    class_lines = defaultdict(set)
    line_classes = defaultdict(set)
    repeated = defaultdict(list)
    for ap, members in duplicated.items():
        complement = [w for w in s_vertices if w not in ap]
        for s in members:
            for w in complement:
                line = core.line_of_pair(dist, n, s, w)
                if u in line or line == full_s:
                    continue
                class_lines[ap].add(line)
                line_classes[line].add(ap)
                repeated[line].append((s, w))
                if s in class_of:
                    neigh[s].add(line)
                    witnesses[(s, line)].append(w)

    left = sorted(excess, key=lambda s: (depth[s], s))
    bg = nx.Graph()
    bg.add_nodes_from((("L", s) for s in left), bipartite=0)
    for s in left:
        for line in neigh[s]:
            bg.add_edge(("L", s), ("D", line_key(line)))

    matching = nx.algorithms.bipartite.maximum_matching(bg, top_nodes=[("L", s) for s in left])
    matched = sum(1 for s in left if ("L", s) in matching)
    component_slacks = []
    for nodes in nx.connected_components(bg):
        lcnt = sum(1 for node in nodes if node[0] == "L")
        rcnt = sum(1 for node in nodes if node[0] == "D")
        if lcnt:
            component_slacks.append(rcnt - lcnt)

    tight_subsets = []
    tight_profile = defaultdict(int)
    min_slack_by_size = {}
    if len(left) <= 14:
        for r in range(1, len(left) + 1):
            for subset in itertools.combinations(left, r):
                union = set()
                for s in subset:
                    union |= {line_key(line) for line in neigh[s]}
                slack = len(union) - len(subset)
                min_slack_by_size[r] = min(slack, min_slack_by_size.get(r, slack))
                if len(union) == len(subset):
                    class_count = len({class_of[s] for s in subset})
                    tight_profile[(len(subset), class_count)] += 1
                    tight_subsets.append({
                        "vertices": list(subset),
                        "neighborhood": sorted(union),
                    })
    repeated_classes = [
        {
            "line": line_key(line),
            "pairs": pairs,
            "classes": sorted({line_key(class_of[s]) for s, _w in pairs if s in class_of}),
        }
        for line, pairs in repeated.items()
        if sum(1 for s, _w in pairs if s in class_of) >= 2
    ]

    per_class_hall_fail = 0
    excess_line_classes = defaultdict(set)
    for s in left:
        for line in neigh[s]:
            excess_line_classes[line].add(class_of[s])
    for ap in duplicated:
        class_left = [s for s in left if class_of[s] == ap]
        if not class_left:
            continue
        class_bg = nx.Graph()
        class_bg.add_nodes_from((("L", s) for s in class_left), bipartite=0)
        for s in class_left:
            for line in neigh[s]:
                if line in class_lines[ap]:
                    class_bg.add_edge(("L", s), ("D", line_key(line)))
        class_matching = nx.algorithms.bipartite.maximum_matching(
            class_bg, top_nodes=[("L", s) for s in class_left]
        )
        if sum(1 for s in class_left if ("L", s) in class_matching) < len(class_left):
            per_class_hall_fail += 1

    return {
        "u": u,
        "excess": left,
        "matched": matched,
        "component_slacks": sorted(component_slacks),
        "neigh_sizes": {s: len(neigh[s]) for s in left},
        "classes": [
            {
                "apex": line_key(ap),
                "members": sorted(members, key=lambda s: (depth[s], s)),
                "excess_members": [s for s in left if class_of[s] == ap],
                "complement": [w for w in s_vertices if w not in ap],
                "class_lines": len(class_lines[ap]),
            }
            for ap, members in duplicated.items()
        ],
        "tight_subsets": tight_subsets[:20],
        "num_tight_subsets": len(tight_subsets),
        "tight_profile": {f"size={k[0]},classes={k[1]}": v for k, v in sorted(tight_profile.items())},
        "min_slack_by_size": {str(k): v for k, v in sorted(min_slack_by_size.items())},
        "repeated_lines": repeated_classes[:20],
        "num_repeated_lines": len(repeated_classes),
        "cross_class_line_overlap": sum(1 for aps in line_classes.values() if len(aps) > 1),
        "cross_excess_neigh_overlap": sum(1 for aps in excess_line_classes.values() if len(aps) > 1),
        "per_class_hall_fail": per_class_hall_fail,
        "witnesses": {
            f"{s}:{line_key(line)}": witnesses[(s, line)]
            for s in left
            for line in sorted(neigh[s], key=line_key)[:12]
        },
    }


def iter_marked(order):
    proc = subprocess.run(["geng", "-C", "-q", str(order)], capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr)
    for line in proc.stdout.splitlines():
        g6 = line.strip()
        if not g6:
            continue
        n, edges = core.graph6_to_edges(g6)
        for u in range(n):
            yield g6, n, edges, u


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("orders", nargs="*", type=int, default=[8])
    parser.add_argument("--max-examples", type=int, default=8)
    parser.add_argument("--only-tight", action="store_true")
    parser.add_argument("--stats", action="store_true")
    parser.add_argument("--min-excess", type=int, default=1)
    parser.add_argument("--min-class", type=int, default=1)
    parser.add_argument("--require-cross-excess", action="store_true")
    parser.add_argument("--g6")
    parser.add_argument("--u", type=int)
    args = parser.parse_args()

    examples = []
    stats = {
        "blocks": 0,
        "blocks_with_excess": 0,
        "global_hall_fail": 0,
        "component_deficit_blocks": 0,
        "min_component_slack": None,
        "per_class_hall_fail": 0,
        "cross_class_overlap_blocks": 0,
        "cross_class_overlap_lines": 0,
        "cross_excess_overlap_blocks": 0,
        "cross_excess_overlap_lines": 0,
        "tight_blocks": 0,
        "tight_profile": defaultdict(int),
        "min_slack_by_size": {},
        "max_excess": 0,
        "max_min_neigh": 0,
    }
    rows = []
    if args.g6 is not None:
        n, edges = core.graph6_to_edges(args.g6)
        roots = [args.u] if args.u is not None else range(n)
        rows = [(args.g6, n, edges, u) for u in roots]
    else:
        for order in args.orders:
            rows.extend(iter_marked(order))

    for g6, n, edges, u in rows:
        stats["blocks"] += 1
        data = block_data(n, edges, u)
        if data is None:
            continue
        stats["blocks_with_excess"] += 1
        stats["max_excess"] = max(stats["max_excess"], len(data["excess"]))
        if data["neigh_sizes"]:
            stats["max_min_neigh"] = max(stats["max_min_neigh"], min(data["neigh_sizes"].values()))
        if data["matched"] < len(data["excess"]):
            stats["global_hall_fail"] += 1
        if data["component_slacks"]:
            local_min = min(data["component_slacks"])
            stats["min_component_slack"] = min(
                local_min,
                stats["min_component_slack"] if stats["min_component_slack"] is not None else local_min,
            )
        if any(slack < 0 for slack in data["component_slacks"]):
            stats["component_deficit_blocks"] += 1
        if data["per_class_hall_fail"]:
            stats["per_class_hall_fail"] += data["per_class_hall_fail"]
        if data["cross_class_line_overlap"]:
            stats["cross_class_overlap_blocks"] += 1
            stats["cross_class_overlap_lines"] += data["cross_class_line_overlap"]
        if data["cross_excess_neigh_overlap"]:
            stats["cross_excess_overlap_blocks"] += 1
            stats["cross_excess_overlap_lines"] += data["cross_excess_neigh_overlap"]
        if data["tight_subsets"]:
            stats["tight_blocks"] += 1
        for key, value in data["tight_profile"].items():
            stats["tight_profile"][key] += value
        for key, value in data["min_slack_by_size"].items():
            stats["min_slack_by_size"][key] = min(
                value,
                stats["min_slack_by_size"].get(key, value),
            )
        if args.only_tight and not data["tight_subsets"]:
            continue
        if args.require_cross_excess and not data["cross_excess_neigh_overlap"]:
            continue
        if len(data["excess"]) < args.min_excess:
            continue
        if max(len(cls["members"]) for cls in data["classes"]) < args.min_class:
            continue
        if args.stats:
            continue
        examples.append({"g6": g6, "n": n, **data})
        if len(examples) >= args.max_examples:
            break

    if args.stats:
        stats["tight_profile"] = dict(sorted(stats["tight_profile"].items()))
    print(json.dumps(stats if args.stats else examples, indent=2))


if __name__ == "__main__":
    main()
