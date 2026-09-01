"""Probe the remaining (4') gap D' >= excess via excess-only Hall.

For a 2-connected marked graph (B,u), choose the shallowest representative in
each Sigma-fiber.  Among the non-reps, group vertices by their apex value A_s.
The excess is the sum over duplicated apex classes of (class size - 1).

This gate tests two stronger, proof-shaped statements:

  ExHall: canonical excess vertices can be matched injectively to D' lines
          containing them.
  CompHall: canonical excess vertices can be matched injectively to their own
          complement-generated D' lines L(s,w), w notin A_s.
  CompUnion: the union of complement-generated D' lines
          L(s,w), with s in a duplicated apex class and w notin A_s,
          has size at least the total excess.
  PerClassHall: the CompHall matching exists inside each duplicated apex class.
  ComponentSurplus: each connected component of the CompHall incidence graph has
          at least as many line-nodes as excess-vertex nodes.
  LargeTight: exact alternating-reachability test for a tight Hall subset of
          size >= 3.  This replaces the old brute-force cap at excess <= 14.
  LineDegree: diagnostic only; each complement line is incident with at most two
          excess vertices in the small census, but this fails in larger random
          samples.

Either statement implies D' >= excess.  These are probes, not recorded proofs.
"""
from __future__ import annotations

import argparse
import itertools
import json
import random
import subprocess
import sys
from collections import defaultdict

import networkx as nx

from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core  # noqa: E402


def block_data(n, edges, u):
    dist = core.all_pairs_distances(n, edges)
    S = [x for x in range(n) if x != u]
    full_s = frozenset(S)
    du = dist[u]

    sigma = {}
    apex = {}
    for s in S:
        ds = dist[s]
        ray = set()
        ap = set()
        for x in S:
            if du[x] + ds[x] == du[s] or du[s] + ds[x] == du[x]:
                ray.add(x)
                ap.add(x)
            elif du[x] + du[s] == ds[x]:
                ap.add(x)
        sigma[s] = frozenset(ray)
        apex[s] = frozenset(ap)

    fibers = defaultdict(list)
    for s in S:
        fibers[sigma[s]].append(s)

    nonreps = []
    for members in fibers.values():
        ordered = sorted(members, key=lambda s: (du[s], s))
        nonreps.extend(ordered[1:])

    apex_classes = defaultdict(list)
    for s in nonreps:
        apex_classes[apex[s]].append(s)

    duplicated = {a: ss for a, ss in apex_classes.items() if len(ss) > 1}
    if not duplicated:
        return None

    dprime = set()
    for a, b in itertools.combinations(range(n), 2):
        line = core.line_of_pair(dist, n, a, b)
        if u not in line and line != full_s:
            dprime.add(line)

    excess = []
    for members in duplicated.values():
        ordered = sorted(members, key=lambda s: (du[s], s))
        excess.extend(ordered[1:])

    comp_lines = set()
    comp_bg = nx.Graph()
    comp_left = [("L", s) for s in excess]
    comp_bg.add_nodes_from(comp_left, bipartite=0)
    comp_neigh = defaultdict(set)
    class_of = {}
    for ap, members in duplicated.items():
        for s in members:
            class_of[s] = ap
    class_local_fail = 0
    fixed_complement_fail = 0
    per_class_hall_fail = 0
    for ap, members in duplicated.items():
        complement = [w for w in S if w not in ap]
        class_lines = set()
        best_fixed = 0
        for s in members:
            for w in complement:
                line = core.line_of_pair(dist, n, s, w)
                if u not in line and line != full_s:
                    class_lines.add(line)
                    comp_lines.add(line)
                    if s in excess:
                        comp_neigh[s].add(line)
                        comp_bg.add_edge(("L", s), ("D", line))
        for w in complement:
            lines = {
                core.line_of_pair(dist, n, s, w)
                for s in members
            }
            lines = {line for line in lines if u not in line and line != full_s}
            best_fixed = max(best_fixed, len(lines))
        if len(class_lines) < len(members) - 1:
            class_local_fail += 1
        if best_fixed < len(members) - 1:
            fixed_complement_fail += 1
        class_left = [("L", s) for s in excess if class_of[s] == ap]
        if class_left:
            class_bg = nx.Graph()
            class_bg.add_nodes_from(class_left, bipartite=0)
            for node in class_left:
                s = node[1]
                for line in comp_neigh[s]:
                    class_bg.add_edge(node, ("D", line))
            class_matching = nx.algorithms.bipartite.maximum_matching(class_bg, top_nodes=class_left)
            if sum(1 for node in class_left if node in class_matching) < len(class_left):
                per_class_hall_fail += 1

    # Excess-only Hall using containment in all D' lines.
    bg = nx.Graph()
    left = [("L", s) for s in excess]
    bg.add_nodes_from(left, bipartite=0)
    for s in excess:
        for line in dprime:
            if s in line:
                bg.add_edge(("L", s), ("D", line))
    matching = nx.algorithms.bipartite.maximum_matching(bg, top_nodes=left)
    matched = sum(1 for node in left if node in matching)

    comp_matching = nx.algorithms.bipartite.maximum_matching(comp_bg, top_nodes=comp_left)
    comp_matched = sum(1 for node in comp_left if node in comp_matching)

    component_deficit = 0
    for nodes in nx.connected_components(comp_bg):
        lcnt = sum(1 for node in nodes if node[0] == "L")
        rcnt = sum(1 for node in nodes if node[0] == "D")
        if lcnt and rcnt < lcnt:
            component_deficit += 1

    line_to_excess = defaultdict(list)
    for s, lines in comp_neigh.items():
        for line in lines:
            line_to_excess[line].append(s)
    pair_overlap_fail = 0
    cross_overlap_lines = 0
    max_line_degree = max((len(ss) for ss in line_to_excess.values()), default=0)
    line_degree_fail = sum(1 for ss in line_to_excess.values() if len(ss) > 2)
    for line, ss in line_to_excess.items():
        if len({class_of[s] for s in ss}) <= 1:
            continue
        cross_overlap_lines += 1
        for s, t in itertools.combinations(ss, 2):
            if class_of[s] == class_of[t]:
                continue
            if t in apex[s] or s in apex[t] or core.line_of_pair(dist, n, s, t) != line:
                pair_overlap_fail += 1
                break

    large_tight_fail = 0
    large_tight_skipped = 0
    large_tight_witness_size = 0
    large_tight_mismatch = 0
    if comp_matched == len(excess):
        right_to_left = {
            comp_matching[left_node]: left_node
            for left_node in comp_left
            if left_node in comp_matching
        }
        sink = ("SINK", None)
        reverse_dep = defaultdict(list)
        for left_node in comp_left:
            for right_node in comp_bg.neighbors(left_node):
                # Dependency digraph on left vertices: left_node depends on the
                # left vertex matched to right_node; unmatched rights go to sink.
                reverse_dep[right_to_left.get(right_node, sink)].append(left_node)

        seen = {sink}
        stack = [sink]
        while stack:
            node = stack.pop()
            for pred in reverse_dep[node]:
                if pred not in seen:
                    seen.add(pred)
                    stack.append(pred)
        non_reaching = [node for node in comp_left if node not in seen]
        large_tight_witness_size = len(non_reaching)
        large_tight_fail = int(large_tight_witness_size >= 3)

        # Audit the polynomial test against brute force when the brute-force
        # search is still cheap enough to run.
        if len(excess) <= 14:
            brute_fail = 0
            for r in range(3, len(excess) + 1):
                for subset in itertools.combinations(excess, r):
                    union = set()
                    for s in subset:
                        union.update(comp_neigh[s])
                    if len(union) <= len(subset):
                        brute_fail = 1
                        break
                if brute_fail:
                    break
            large_tight_mismatch = int(bool(brute_fail) != bool(large_tight_fail))
    else:
        large_tight_skipped = 1

    return {
        "excess": len(excess),
        "dprime": len(dprime),
        "duplicated_classes": len(duplicated),
        "max_class": max(len(v) for v in duplicated.values()),
        "exhall_ok": matched == len(excess),
        "comp_hall_ok": comp_matched == len(excess),
        "comp_union_ok": len(comp_lines) >= len(excess),
        "per_class_hall_ok": per_class_hall_fail == 0,
        "component_surplus_ok": component_deficit == 0,
        "large_tight_ok": large_tight_fail == 0,
        "line_degree_ok": line_degree_fail == 0,
        "class_local_fail": class_local_fail,
        "per_class_hall_fail": per_class_hall_fail,
        "fixed_complement_fail": fixed_complement_fail,
        "component_deficit": component_deficit,
        "cross_overlap_lines": cross_overlap_lines,
        "max_line_degree": max_line_degree,
        "line_degree_fail": line_degree_fail,
        "pair_overlap_fail": pair_overlap_fail,
        "large_tight_fail": large_tight_fail,
        "large_tight_skipped": large_tight_skipped,
        "large_tight_witness_size": large_tight_witness_size,
        "large_tight_mismatch": large_tight_mismatch,
        "comp_union_slack": len(comp_lines) - len(excess),
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


def random_2connected(order, trials, seed):
    rng = random.Random(seed)
    for _ in range(trials):
        p = rng.uniform(0.16, 0.50)
        for _attempt in range(60):
            g = nx.gnp_random_graph(order, p, seed=rng.randrange(1 << 30))
            if nx.is_biconnected(g):
                g6 = nx.to_graph6_bytes(g, header=False).decode().strip()
                edges = list(g.edges())
                for u in range(order):
                    yield g6, order, edges, u
                break


def run(rows):
    out = {
        "blocks_with_excess": 0,
        "exhall_fail": 0,
        "comp_hall_fail": 0,
        "comp_union_fail": 0,
        "class_local_fail": 0,
        "per_class_hall_fail": 0,
        "fixed_complement_fail": 0,
        "component_deficit": 0,
        "pair_overlap_fail": 0,
        "large_tight_fail": 0,
        "large_tight_skipped": 0,
        "large_tight_mismatch": 0,
        "max_large_tight_witness_size": 0,
        "cross_overlap_lines": 0,
        "line_degree_fail": 0,
        "max_line_degree": 0,
        "max_excess": 0,
        "max_classes": 0,
        "max_class": 0,
        "min_comp_union_slack": None,
        "examples": [],
    }
    for g6, n, edges, u in rows:
        data = block_data(n, edges, u)
        if data is None:
            continue
        out["blocks_with_excess"] += 1
        out["max_excess"] = max(out["max_excess"], data["excess"])
        out["max_classes"] = max(out["max_classes"], data["duplicated_classes"])
        out["max_class"] = max(out["max_class"], data["max_class"])
        slack = data["comp_union_slack"]
        out["min_comp_union_slack"] = slack if out["min_comp_union_slack"] is None else min(out["min_comp_union_slack"], slack)
        if not data["exhall_ok"]:
            out["exhall_fail"] += 1
        if not data["comp_hall_ok"]:
            out["comp_hall_fail"] += 1
        if not data["comp_union_ok"]:
            out["comp_union_fail"] += 1
        out["class_local_fail"] += data["class_local_fail"]
        out["per_class_hall_fail"] += data["per_class_hall_fail"]
        out["fixed_complement_fail"] += data["fixed_complement_fail"]
        out["component_deficit"] += data["component_deficit"]
        out["pair_overlap_fail"] += data["pair_overlap_fail"]
        out["large_tight_fail"] += data["large_tight_fail"]
        out["large_tight_skipped"] += data["large_tight_skipped"]
        out["large_tight_mismatch"] += data["large_tight_mismatch"]
        out["max_large_tight_witness_size"] = max(
            out["max_large_tight_witness_size"],
            data["large_tight_witness_size"],
        )
        out["cross_overlap_lines"] += data["cross_overlap_lines"]
        out["line_degree_fail"] += data["line_degree_fail"]
        out["max_line_degree"] = max(out["max_line_degree"], data["max_line_degree"])
        if (
            not data["exhall_ok"]
            or not data["comp_hall_ok"]
            or not data["comp_union_ok"]
            or data["class_local_fail"]
            or data["per_class_hall_fail"]
            or data["component_deficit"]
            or data["large_tight_fail"]
            or data["large_tight_skipped"]
            or data["large_tight_mismatch"]
        ) and len(out["examples"]) < 8:
            out["examples"].append({"g6": g6, "u": u, **data})
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("orders", nargs="*", type=int, default=[7, 8])
    parser.add_argument("--random", action="store_true", help="sample random 2-connected graphs instead of exhaustive geng -C")
    parser.add_argument("--trials", type=int, default=700)
    parser.add_argument("--seed", type=int, default=20260626)
    args = parser.parse_args()

    results = []
    for order in args.orders:
        rows = random_2connected(order, args.trials, args.seed + order) if args.random else iter_marked(order)
        result = run(rows)
        result["order"] = order
        result["mode"] = "random" if args.random else "marked"
        results.append(result)
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
