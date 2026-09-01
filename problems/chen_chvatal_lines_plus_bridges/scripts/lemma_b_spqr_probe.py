"""Probe the 2-cut/SPQR route for Lemma B.

Target Lemma B:
    2-connected + diam>=4  ==>  ell(G) >= |G|.

This script does not prove the lemma.  It asks whether the tight 2-connected
diameter>=4 graphs are genuinely 2-separable, and whether the 3-connected
subcase already has large margin.  That is the first decision point for an
SPQR-style proof.
"""
from __future__ import annotations

import argparse
import itertools
import json
import random
import subprocess
import sys
from collections import Counter

import networkx as nx

from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core  # noqa: E402


def graph_diameter(dist, n):
    diam = 0
    for i in range(n):
        for j in range(i + 1, n):
            d = dist[i][j]
            if d is None:
                return None
            diam = max(diam, d)
    return diam


def line_counts(n, dist):
    lines = set()
    for a, b in itertools.combinations(range(n), 2):
        lines.add(core.line_of_pair(dist, n, a, b))
    return len(lines), sum(1 for line in lines if len(line) < n)


def is_three_connected(g):
    if g.number_of_nodes() < 4 or min(dict(g.degree()).values()) < 3:
        return False
    nodes = list(g.nodes())
    for a, b in itertools.combinations(nodes, 2):
        h = g.copy()
        h.remove_nodes_from([a, b])
        if h.number_of_nodes() and not nx.is_connected(h):
            return False
    return True


def two_cuts(g):
    cuts = []
    nodes = list(g.nodes())
    for a, b in itertools.combinations(nodes, 2):
        h = g.copy()
        h.remove_nodes_from([a, b])
        if h.number_of_nodes() and not nx.is_connected(h):
            comps = sorted((len(c) for c in nx.connected_components(h)), reverse=True)
            cuts.append((a, b, comps))
    return cuts


def suppress_degree2_signature(g):
    """Crude SPQR pre-signature: how much of G is degree-2 tubing?"""
    deg = dict(g.degree())
    branch = [v for v, d in deg.items() if d >= 3]
    deg2 = [v for v, d in deg.items() if d == 2]
    return {
        "deg2": len(deg2),
        "branch": len(branch),
        "max_degree": max(deg.values()) if deg else 0,
        "degree_sequence": sorted(deg.values()),
    }


def analyze_graph(g6, n, edges):
    g = nx.Graph()
    g.add_nodes_from(range(n))
    g.add_edges_from(edges)
    if not nx.is_biconnected(g):
        return None
    dist = core.all_pairs_distances(n, edges)
    diam = graph_diameter(dist, n)
    if diam is None or diam < 4:
        return None
    ell, proper = line_counts(n, dist)
    three = is_three_connected(g)
    cuts = [] if three else two_cuts(g)
    sig = suppress_degree2_signature(g)
    best_cut = None
    if cuts:
        best_cut = min(cuts, key=lambda item: (max(item[2]), -len(item[2]), item[0], item[1]))
    return {
        "g6": g6,
        "n": n,
        "m": len(edges),
        "diam": diam,
        "ell": ell,
        "proper": proper,
        "ell_minus_n": ell - n,
        "proper_minus_n": proper - n,
        "three_connected": three,
        "num_2cuts": len(cuts),
        "best_2cut": None if best_cut is None else [best_cut[0], best_cut[1], best_cut[2]],
        **sig,
    }


def analyze_named(graph6_values):
    return [
        analyze_graph(g6, *core.graph6_to_edges(g6))
        for g6 in graph6_values
    ]


def iter_marked_order(order):
    proc = subprocess.run(["geng", "-C", "-q", str(order)], capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr)
    for line in proc.stdout.splitlines():
        g6 = line.strip()
        if not g6:
            continue
        n, edges = core.graph6_to_edges(g6)
        yield g6, n, edges


def random_2connected(order, trials, seed):
    rng = random.Random(seed)
    seen = set()
    for _ in range(trials):
        p = rng.uniform(0.14, 0.48)
        for _attempt in range(120):
            g = nx.gnp_random_graph(order, p, seed=rng.randrange(1 << 30))
            if not nx.is_biconnected(g):
                continue
            g6 = nx.to_graph6_bytes(g, header=False).decode().strip()
            if g6 in seen:
                continue
            seen.add(g6)
            yield g6, order, list(g.edges())
            break


def update_min(bucket, row):
    if bucket is None:
        return row
    key = (row["ell_minus_n"], row["proper_minus_n"], row["m"], row["g6"])
    old = (bucket["ell_minus_n"], bucket["proper_minus_n"], bucket["m"], bucket["g6"])
    return row if key < old else bucket


def run(rows, keep_examples):
    out = {
        "graphs": 0,
        "diam4": 0,
        "three_connected": 0,
        "two_separable": 0,
        "min_all": None,
        "min_3conn": None,
        "min_2sep": None,
        "min_margin_by_branch": {},
        "min_margin_by_deg2": {},
        "two_cut_component_patterns": Counter(),
        "tight": [],
    }
    min_by_branch = {}
    min_by_deg2 = {}
    tight_rows = []
    for g6, n, edges in rows:
        out["graphs"] += 1
        row = analyze_graph(g6, n, edges)
        if row is None:
            continue
        out["diam4"] += 1
        out["min_all"] = update_min(out["min_all"], row)
        if row["three_connected"]:
            out["three_connected"] += 1
            out["min_3conn"] = update_min(out["min_3conn"], row)
        else:
            out["two_separable"] += 1
            out["min_2sep"] = update_min(out["min_2sep"], row)
            if row["best_2cut"] is not None:
                out["two_cut_component_patterns"][tuple(row["best_2cut"][2])] += 1
        min_by_branch[row["branch"]] = update_min(min_by_branch.get(row["branch"]), row)
        min_by_deg2[row["deg2"]] = update_min(min_by_deg2.get(row["deg2"]), row)
        if row["ell_minus_n"] <= 5 or row["proper_minus_n"] <= 4:
            tight_rows.append(row)

    tight_rows.sort(key=lambda r: (r["ell_minus_n"], r["proper_minus_n"], r["n"], r["m"], r["g6"]))
    out["tight"] = tight_rows[:keep_examples]
    out["min_margin_by_branch"] = {
        str(k): {
            "ell_minus_n": v["ell_minus_n"],
            "proper_minus_n": v["proper_minus_n"],
            "g6": v["g6"],
            "three_connected": v["three_connected"],
            "deg2": v["deg2"],
        }
        for k, v in sorted(min_by_branch.items())
    }
    out["min_margin_by_deg2"] = {
        str(k): {
            "ell_minus_n": v["ell_minus_n"],
            "proper_minus_n": v["proper_minus_n"],
            "g6": v["g6"],
            "three_connected": v["three_connected"],
            "branch": v["branch"],
        }
        for k, v in sorted(min_by_deg2.items())
    }
    out["two_cut_component_patterns"] = {
        str(list(k)): v for k, v in out["two_cut_component_patterns"].most_common(12)
    }
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("orders", nargs="*", type=int, default=[8, 9, 10])
    parser.add_argument("--random", action="store_true")
    parser.add_argument("--trials", type=int, default=500)
    parser.add_argument("--seed", type=int, default=20260626)
    parser.add_argument("--keep-examples", type=int, default=12)
    parser.add_argument("--g6", nargs="*", help="inspect explicit graph6 strings")
    args = parser.parse_args()

    if args.g6:
        print(json.dumps(analyze_named(args.g6), indent=2))
        return

    results = []
    for order in args.orders:
        rows = (
            random_2connected(order, args.trials, args.seed + order)
            if args.random
            else iter_marked_order(order)
        )
        data = run(rows, args.keep_examples)
        data["order"] = order
        data["mode"] = "random" if args.random else "marked"
        results.append(data)
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
