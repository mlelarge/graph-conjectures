"""Generate branching-tree (Y-tree) columns for column generation.

For a fixed root in L_fpy box L_fpy, enumerates basic Hurlbert tree
strategies of more general shape than simple paths. Specifically:

- Y-trees: pairs of simple paths sharing the first edge (root, root-child).
- Trident-trees: triples of simple paths sharing the first edge.
- Pi-trees: pairs of simple paths sharing root-child *and* the first internal
  vertex below it.

All weights are basic (doubling exactly).

The motivation is that Y-trees and tridents have richer dual coverage
than the simple paths used in run_column_generation_robust.py: they
constrain dual y at more vertices simultaneously per unit of b_T cost.

Usage::

    python scripts/branching_tree_columns.py --root-pair 0,1 --max-depth 4 [--out path.json]
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from fractions import Fraction
from itertools import combinations
from pathlib import Path
import time

import numpy as np
from scipy.optimize import linprog

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from check_pebbling_weight_certificate import check_certificate, load_certificate_file
from optimize_certificate_multipliers import _build_lp
from pebbling_graphs import cartesian_product, load_named_graph, pair_to_index
from run_column_generation import enumerate_simple_paths, path_to_strategy
from run_column_generation_robust import round_and_fix


def y_tree_strategy(
    p1: tuple[int, ...],
    p2: tuple[int, ...],
    root: int,
) -> dict | None:
    """Merge two simple paths sharing the same root-child into a Y-tree.

    Both paths must have the same total length (so their weights at the
    root-child agree) and disjoint interior except for the root-child.
    """
    if len(p1) != len(p2) or len(p1) < 3:
        return None
    if p1[0] != root or p2[0] != root:
        return None
    if p1[1] != p2[1]:
        return None  # different root-children
    # Interior of p1 (excluding root, root-child) must be disjoint from p2's interior
    set1 = set(p1[2:])
    set2 = set(p2[2:])
    if set1 & set2:
        return None
    # All vertices distinct (no repeats anywhere)
    all_v = set(p1) | set(p2)
    if len(all_v) != len(p1) + len(p2) - 2:  # share root and root-child
        return None
    d = len(p1) - 1
    weights: dict[int, int] = {root: 0}
    weights[p1[1]] = 2 ** (d - 1)  # root-child
    for i in range(2, len(p1)):
        weights[p1[i]] = 2 ** (d - i)
        weights[p2[i]] = 2 ** (d - i)
    edges: list[tuple[int, int]] = []
    edges.append(tuple(sorted([root, p1[1]])))
    for i in range(1, len(p1) - 1):
        edges.append(tuple(sorted([p1[i], p1[i + 1]])))
        edges.append(tuple(sorted([p2[i], p2[i + 1]])))
    return {
        "name": f"y-tree depth{d} root-child {p1[1]} to leaves {p1[-1]},{p2[-1]}",
        "tree_edges": [list(e) for e in edges],
        "weights": {str(k): str(v) for k, v in weights.items()},
        "basic": True,
    }


def trident_tree_strategy(
    paths: list[tuple[int, ...]],
    root: int,
) -> dict | None:
    """Merge three simple paths sharing the same root-child into a trident."""
    if len(paths) != 3:
        return None
    p1, p2, p3 = paths
    L = len(p1)
    if not (len(p2) == L == len(p3) and L >= 3):
        return None
    if p1[0] != root or p2[0] != root or p3[0] != root:
        return None
    if not (p1[1] == p2[1] == p3[1]):
        return None
    s1 = set(p1[2:]); s2 = set(p2[2:]); s3 = set(p3[2:])
    if (s1 & s2) or (s1 & s3) or (s2 & s3):
        return None
    all_v = set(p1) | set(p2) | set(p3)
    if len(all_v) != 3 * L - 4:  # share root + root-child = 2 vertices
        return None
    d = L - 1
    weights: dict[int, int] = {root: 0}
    weights[p1[1]] = 2 ** (d - 1)
    for p in (p1, p2, p3):
        for i in range(2, L):
            weights[p[i]] = 2 ** (d - i)
    edges: list[tuple[int, int]] = []
    edges.append(tuple(sorted([root, p1[1]])))
    for p in (p1, p2, p3):
        for i in range(1, L - 1):
            edges.append(tuple(sorted([p[i], p[i + 1]])))
    edges = list(set(edges))  # dedupe (root-child edge appears 3 times)
    return {
        "name": f"trident depth{d} root-child {p1[1]} leaves {p1[-1]},{p2[-1]},{p3[-1]}",
        "tree_edges": [list(e) for e in edges],
        "weights": {str(k): str(v) for k, v in weights.items()},
        "basic": True,
    }


def pi_tree_strategy(
    p1: tuple[int, ...],
    p2: tuple[int, ...],
    root: int,
) -> dict | None:
    """Merge two simple paths sharing the first 3 vertices (root, root-child,
    first internal vertex) but diverging at depth 2."""
    if len(p1) != len(p2) or len(p1) < 4:
        return None
    if p1[0] != root or p2[0] != root:
        return None
    if p1[1] != p2[1] or p1[2] != p2[2]:
        return None
    if p1[3] == p2[3]:
        return None  # paths must diverge somewhere
    # Interior of p1 (after the shared prefix) disjoint from p2's
    set1 = set(p1[3:])
    set2 = set(p2[3:])
    if set1 & set2:
        return None
    all_v = set(p1) | set(p2)
    expected = len(p1) + len(p2) - 3  # share 3 vertices
    if len(all_v) != expected:
        return None
    d = len(p1) - 1
    weights: dict[int, int] = {root: 0}
    weights[p1[1]] = 2 ** (d - 1)
    weights[p1[2]] = 2 ** (d - 2)
    for i in range(3, len(p1)):
        weights[p1[i]] = 2 ** (d - i)
        weights[p2[i]] = 2 ** (d - i)
    edges: list[tuple[int, int]] = []
    edges.append(tuple(sorted([root, p1[1]])))
    edges.append(tuple(sorted([p1[1], p1[2]])))
    for i in range(2, d):
        edges.append(tuple(sorted([p1[i], p1[i + 1]])))
        edges.append(tuple(sorted([p2[i], p2[i + 1]])))
    return {
        "name": (
            f"pi-tree depth{d} prefix [{p1[1]},{p1[2]}] "
            f"to leaves {p1[-1]},{p2[-1]}"
        ),
        "tree_edges": [list(e) for e in edges],
        "weights": {str(k): str(v) for k, v in weights.items()},
        "basic": True,
    }


def enumerate_branching_trees(
    paths: list[tuple[int, ...]],
    root: int,
    include_y: bool = True,
    include_trident: bool = True,
    include_pi: bool = True,
    max_depth: int = 4,
) -> list[dict]:
    """Group paths by (length, root-child) and merge into Y / trident / Pi trees."""
    by_key: dict[tuple[int, int], list[tuple[int, ...]]] = defaultdict(list)
    by_key_pi: dict[tuple[int, int, int], list[tuple[int, ...]]] = defaultdict(list)
    for p in paths:
        d = len(p) - 1
        if d > max_depth:
            continue
        if len(p) >= 3 and d >= 2:
            by_key[(d, p[1])].append(p)
        if len(p) >= 4 and d >= 3:
            by_key_pi[(d, p[1], p[2])].append(p)
    out: list[dict] = []
    for (d, rc), grp in by_key.items():
        if include_y:
            for p1, p2 in combinations(grp, 2):
                strat = y_tree_strategy(p1, p2, root)
                if strat is not None:
                    out.append(strat)
        if include_trident and len(grp) >= 3:
            for p1, p2, p3 in combinations(grp, 3):
                strat = trident_tree_strategy([p1, p2, p3], root)
                if strat is not None:
                    out.append(strat)
    if include_pi:
        for (d, rc, internal), grp in by_key_pi.items():
            for p1, p2 in combinations(grp, 2):
                strat = pi_tree_strategy(p1, p2, root)
                if strat is not None:
                    out.append(strat)
    return out


def run_with_branching(
    root_pair: tuple[int, int],
    max_path_len: int,
    branching_max_depth: int,
    denominator: int,
    out_path: Path,
) -> dict:
    L = load_named_graph("L_fpy")
    LL = cartesian_product(L, L)
    n = LL.n
    adj = LL.adjacency()
    root = pair_to_index(root_pair[0], root_pair[1], 8)

    paths = enumerate_simple_paths(adj, root, max_len=max_path_len)
    path_strats = [path_to_strategy(p, root) for p in paths]
    branch_strats = enumerate_branching_trees(
        paths, root, max_depth=branching_max_depth
    )
    print(f"paths: {len(paths)}, branching: {len(branch_strats)}", flush=True)

    payload = {
        "graph": {
            "n": LL.n,
            "edges": [list(e) for e in LL.edges],
            "name": "L_fpy_box_L_fpy",
        },
        "root": root,
        "claimed_bound": 999,
        "strategies": path_strats + branch_strats,
        "dual_multipliers": ["0"] * (len(path_strats) + len(branch_strats)),
    }
    tmp = REPO_ROOT / "data" / "pebbling_product" / "_tmp_branching.json"
    with tmp.open("w") as fp:
        json.dump(payload, fp)

    cert, g = load_certificate_file(tmp)
    c, A_ub, rhs = _build_lp(cert, g.n)
    res = linprog(c=c, A_ub=A_ub, b_ub=rhs, bounds=[(0, None)] * len(c), method="highs-ds")
    print(f"float LP optimum: {res.fun:.6f}", flush=True)

    nonzero_idx = [i for i, x in enumerate(res.x) if x > 1e-9]
    sub_c = c[nonzero_idx]
    sub_A = A_ub[:, nonzero_idx]
    sub_res = linprog(
        c=sub_c, A_ub=sub_A, b_ub=rhs,
        bounds=[(0, None)] * len(sub_c),
        method="highs-ds",
    )
    sub_strats = [cert.strategies[i] for i in nonzero_idx]
    b_T_rational = [
        sum((w for vv, w in t.weights.items() if vv != cert.root), start=Fraction(0))
        for t in sub_strats
    ]
    alpha_q = round_and_fix(denominator, sub_res.x, sub_strats, b_T_rational, g.n, cert.root)
    if alpha_q is None:
        raise RuntimeError(f"round-and-fix failed at D={denominator}")
    sum_ab = sum((a * b for a, b in zip(alpha_q, b_T_rational)), start=Fraction(0))
    derived = sum_ab.numerator // sum_ab.denominator + 1

    output = {
        "graph": payload["graph"],
        "root": cert.root,
        "claimed_bound": derived,
        "strategies": [
            {
                "name": s.name,
                "tree_edges": [list(e) for e in s.tree_edges],
                "weights": {str(k): str(v) for k, v in s.weights.items()},
                "basic": s.basic,
            }
            for s in sub_strats
        ],
        "dual_multipliers": [str(a) for a in alpha_q],
        "notes": (
            f"Branching-tree column generation at root ({root_pair[0]}, {root_pair[1]}). "
            f"max_path_len={max_path_len}, branching_max_depth={branching_max_depth}, "
            f"D={denominator}. Float LP {res.fun:.6f}, rational sum alpha b = {sum_ab}, "
            f"derived = {derived}."
        ),
    }
    with out_path.open("w") as fp:
        json.dump(output, fp, indent=2)

    cert2, g2 = load_certificate_file(out_path)
    chk = check_certificate(cert2, g2)

    return {
        "n_path_columns": len(path_strats),
        "n_branching_columns": len(branch_strats),
        "n_total_columns": len(path_strats) + len(branch_strats),
        "n_active": len(nonzero_idx),
        "lp_optimum_float": float(res.fun),
        "rationalised_sum_alpha_b": str(sum_ab),
        "denominator": denominator,
        "derived_bound": derived,
        "checker_accepted": chk.accepted,
        "checker_derived": chk.derived_bound,
        "out_path": str(out_path),
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--root-pair", default="0,1")
    ap.add_argument("--max-path-len", type=int, default=5)
    ap.add_argument("--branching-max-depth", type=int, default=4)
    ap.add_argument("--denominator", type=int, default=4800)
    ap.add_argument(
        "--out",
        default=str(
            REPO_ROOT
            / "data/pebbling_product/certificates/branching_orbit_test.json"
        ),
    )
    args = ap.parse_args()
    rp = tuple(int(x) for x in args.root_pair.split(","))
    summary = run_with_branching(
        rp, args.max_path_len, args.branching_max_depth, args.denominator, Path(args.out)
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
