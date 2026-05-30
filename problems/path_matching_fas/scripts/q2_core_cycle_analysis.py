"""Q2: characterize the forced cycle on the acyclicity-core.

The acyclicity-core = minimal-NO instances with Delta*=2 (= large_width_no
intersect {Delta*=2}).  On such an instance a degree-2 order EXISTS but
every degree-2 order has a CYCLIC back-arc graph.

This script, for each core instance:
  * enumerates ALL degree-2 orders (max back-degree <= 2) via the same
    subset reachability skeleton as degreewidth_exact, then a backtracking
    enumeration restricted to back-degree <= 2 at placement;
  * for each, builds the back-arc graph and records the multiset of cycle
    lengths;
  * reports: min cycle length over all degree-2 orders (the "best" any
    order can do), the set of cycle lengths that appear, and whether a
    SINGLE short cycle is forced (a localized obstruction candidate).

Reuses degreewidth_exact._masks and nonsweep_path_fas builders; no shared
files modified.
"""
from __future__ import annotations

import json
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from degreewidth_exact import _masks, degreewidth  # noqa: E402

Matrix = list[list[int]]


def arcs_of(T: Matrix):
    n = len(T)
    return [(u, v) for u in range(n) for v in range(n) if u != v and T[u][v]]


def enumerate_degree2_orders(T: Matrix, cap: int = 5_000_000):
    """Yield every order whose max back-degree is <= 2.

    Append vertices left->right; bd(v | before=S) is fixed at placement:
        bd = |N+(v) cap S| + (d^-(v) - |N-(v) cap S|).
    Prune when bd > 2.
    """
    n = len(T)
    outmask, inmask, dminus = _masks(T)
    order = []
    used = 0
    out = []

    def rec(used_mask):
        if len(out) >= cap:
            return
        if len(order) == n:
            out.append(tuple(order))
            return
        for v in range(n):
            vb = 1 << v
            if used_mask & vb:
                continue
            before_in = bin(inmask[v] & used_mask).count("1")
            bd = bin(outmask[v] & used_mask).count("1") + (dminus[v] - before_in)
            if bd <= 2:
                order.append(v)
                rec(used_mask | vb)
                order.pop()

    rec(0)
    return out


def back_arc_components(T: Matrix, order):
    """Return (max_degree, cycle_lengths) of the back-arc graph.

    cycle_lengths: list of lengths of cyclic components (each is a single
    cycle since max degree <= 2 means components are paths or cycles).
    """
    pos = {v: i for i, v in enumerate(order)}
    n = len(order)
    deg = [0] * n
    adj = {v: [] for v in order}
    edges = 0
    for (u, v) in arcs_of(T):
        if pos[u] > pos[v]:
            adj[u].append(v)
            adj[v].append(u)
            deg[u] += 1
            deg[v] += 1
            edges += 1
    maxdeg = max(deg) if deg else 0
    # components: a component with #edges == #vertices is a cycle
    seen = set()
    cyc_lengths = []
    for start in order:
        if start in seen:
            continue
        # BFS
        stack = [start]
        comp_v = set()
        comp_e = 0
        while stack:
            x = stack.pop()
            if x in comp_v:
                continue
            comp_v.add(x)
            seen.add(x)
            for y in adj[x]:
                comp_e += 1
                if y not in comp_v:
                    stack.append(y)
        comp_e //= 2
        if comp_e == len(comp_v) and len(comp_v) >= 3:
            cyc_lengths.append(len(comp_v))
    return maxdeg, sorted(cyc_lengths)


def analyze_core(path: str, max_instances: int | None = None, order_cap=2_000_000):
    d = json.load(open(path))
    recs = d["records"]
    core = []
    for r in recs:
        T = r["T"]
        if degreewidth(T) == 2:
            core.append(r)
    if max_instances:
        core = core[:max_instances]
    results = []
    for r in core:
        T = r["T"]
        orders = enumerate_degree2_orders(T, cap=order_cap)
        # for each degree-2 order, get cycle structure
        per_order = [back_arc_components(T, o) for o in orders]
        # all must be cyclic (since it's a NO and degree-2 exists)
        any_acyclic = any(len(cl) == 0 and md <= 2 for (md, cl) in per_order)
        cyc_len_sets = Counter()
        min_total_cyc_vertices = None
        min_num_cycles = None
        single_cycle_orders = 0
        for (md, cl) in per_order:
            cyc_len_sets[tuple(cl)] += 1
            tot = sum(cl)
            if min_total_cyc_vertices is None or tot < min_total_cyc_vertices:
                min_total_cyc_vertices = tot
            if min_num_cycles is None or len(cl) < min_num_cycles:
                min_num_cycles = len(cl)
            if len(cl) == 1:
                single_cycle_orders += 1
        results.append({
            "name": r.get("name"),
            "n": len(T),
            "num_degree2_orders": len(orders),
            "any_acyclic": any_acyclic,
            "min_num_cycles": min_num_cycles,
            "min_cycle_lengths_example": min(
                (cl for (_, cl) in per_order if cl), key=lambda c: (len(c), sum(c)),
                default=[]),
            "distinct_cycle_signatures": len(cyc_len_sets),
            "single_cycle_order_frac": single_cycle_orders / max(1, len(orders)),
        })
    return results


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--n", type=int, default=7)
    p.add_argument("--max", type=int, default=None)
    args = p.parse_args()
    path = f"data/minimal_no_obstruction_catalogue_n{args.n}.json"
    res = analyze_core(path, max_instances=args.max)
    print(f"acyclicity-core instances at n={args.n}: {len(res)}")
    for r in res:
        print(json.dumps(r))
    # aggregate
    print("\n=== aggregate ===")
    print("any_acyclic (should all be False):", set(r["any_acyclic"] for r in res))
    print("min_num_cycles distribution:", Counter(r["min_num_cycles"] for r in res))
    all_minlens = Counter(tuple(r["min_cycle_lengths_example"]) for r in res)
    print("min-cycle-signature distribution:", dict(all_minlens))
    print("num_degree2_orders range:",
          min(r["num_degree2_orders"] for r in res),
          max(r["num_degree2_orders"] for r in res))
