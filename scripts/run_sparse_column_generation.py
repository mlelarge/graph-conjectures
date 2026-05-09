"""Sparse, in-memory column generation for one root with a pricing oracle.

For root ``r`` (default ``(0, 0)``), this script:

1. Loads the existing per-orbit certificate as the seed column set.
2. Iteratively:
   - solves the master LP via :func:`sparse_columns.solve_master_lp`;
   - extracts the dual ``y``;
   - runs :func:`price_tree_strategy.price_basic_trees` to find columns
     with negative reduced cost;
   - adds them to the column pool;
   - repeats until no negative column is found or a budget is hit.
3. Round-and-fixes the rationalised alpha at a chosen denominator and
   emits a final certificate JSON via
   :func:`sparse_columns.emit_certificate`.

No JSON file is written for the candidate pool; only the seed
certificate (read) and the final selected certificate (written) touch
disk.

Usage::

    python scripts/run_sparse_column_generation.py \\
        --root-pair 0,0 \\
        --max-depth 5 \\
        --rounds 20 \\
        --denominator 4800 \\
        --out data/pebbling_product/certificates/root_0_0_priced_le_X.json
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from fractions import Fraction
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from check_pebbling_weight_certificate import check_certificate, load_certificate_file
from pebbling_graphs import cartesian_product, load_named_graph
from price_tree_strategy import price_basic_trees
from run_column_generation import enumerate_simple_paths, path_to_strategy
from run_column_generation_robust import round_and_fix
from sparse_columns import (
    StrategyColumn,
    emit_certificate,
    lp_from_columns,
    solve_master_lp,
)


def load_seed_certificate(path: Path) -> tuple[list[StrategyColumn], dict, int]:
    """Load an existing certificate JSON into sparse columns + graph payload + root."""
    cert, g = load_certificate_file(path)
    columns = []
    for s in cert.strategies:
        # Drop the explicit 0 root weight if present
        weights = {v: w for v, w in s.weights.items() if w != 0}
        columns.append(
            StrategyColumn(
                weights=weights,
                tree_edges=list(s.tree_edges),
                name=s.name,
                basic=s.basic,
                source=f"seed:{path.name}",
            )
        )
    with path.open() as fp:
        payload = json.load(fp)
    return columns, payload["graph"], cert.root


def seed_paths_for_root(
    adj: list[list[int]], root: int, max_len: int
) -> list[StrategyColumn]:
    """Build path-only columns for a root if no seed certificate exists."""
    paths = enumerate_simple_paths(adj, root, max_len=max_len)
    cols: list[StrategyColumn] = []
    for p in paths:
        s = path_to_strategy(p, root)
        weights = {int(k): Fraction(v) for k, v in s["weights"].items()}
        weights = {v: w for v, w in weights.items() if w != 0}
        edges = [tuple(e) for e in s["tree_edges"]]
        cols.append(
            StrategyColumn(
                weights=weights,
                tree_edges=edges,
                name=s["name"],
                basic=s["basic"],
                source="seed:path",
            )
        )
    return cols


def column_generation_loop(
    columns: list[StrategyColumn],
    adj: list[list[int]],
    root: int,
    n_vertices: int,
    *,
    max_depth: int,
    rounds: int,
    pricing_top_k: int,
    pricing_time_budget_s: float,
    log: bool = True,
) -> tuple[list[StrategyColumn], np.ndarray, np.ndarray, float]:
    """Run rounds of solve-master-LP + price + add columns.

    Stops when no negative reduced-cost column is found.
    """
    fun = float("inf")
    alpha = np.zeros(0)
    y = np.zeros(n_vertices - 1)
    for r in range(rounds):
        fun, alpha, y = solve_master_lp(columns, n_vertices, root)
        if log:
            n_nz = int((alpha > 1e-9).sum())
            print(
                f"[round {r}] columns={len(columns)} active={n_nz} "
                f"LP optimum = {fun:.6f}",
                flush=True,
            )
        # Pricing
        pr = price_basic_trees(
            adj=adj,
            root=root,
            y=list(y),
            n_vertices=n_vertices,
            max_depth=max_depth,
            top_k=pricing_top_k,
            require_negative_reduced_cost=True,
            time_budget_s=pricing_time_budget_s,
            log=False,
        )
        if not pr.columns:
            if log:
                print(
                    f"[round {r}] pricing found NO negative-reduced-cost column "
                    f"(nodes={pr.nodes_explored}, dt={pr.elapsed_s:.1f}s); "
                    "loop terminates.",
                    flush=True,
                )
            break
        # Add columns whose reduced cost is most negative
        if log:
            print(
                f"[round {r}] pricing found {len(pr.columns)} candidates "
                f"(top reduced cost = {pr.reduced_costs[0]}, "
                f"nodes={pr.nodes_explored}, dt={pr.elapsed_s:.1f}s)",
                flush=True,
            )
        # Avoid duplicates: skip if the weight signature already in pool
        existing = {
            tuple(sorted(c.weights.items())): None for c in columns
        }
        added = 0
        for col in pr.columns:
            sig = tuple(sorted(col.weights.items()))
            if sig in existing:
                continue
            columns.append(col)
            existing[sig] = None
            added += 1
        if added == 0:
            if log:
                print(
                    f"[round {r}] all priced columns are duplicates of existing; "
                    "loop terminates.",
                    flush=True,
                )
            break
    return columns, alpha, y, fun


def rationalise_and_emit(
    columns: list[StrategyColumn],
    alpha_float: np.ndarray,
    *,
    n_vertices: int,
    root: int,
    denominator: int,
    graph_payload: dict,
    out_path: Path,
    notes: str = "",
) -> dict:
    """Round-and-fix the float alpha, verify rationally, write certificate JSON."""
    # Drop zero-alpha columns
    nz_idx = [i for i, a in enumerate(alpha_float) if a > 1e-9]
    sub_cols = [columns[i] for i in nz_idx]
    sub_alpha = [alpha_float[i] for i in nz_idx]
    b_T = [c.b for c in sub_cols]
    alpha_q = round_and_fix(denominator, sub_alpha, sub_cols, b_T, n_vertices, root)
    if alpha_q is None:
        raise RuntimeError(f"round-and-fix failed at D={denominator}")
    sum_ab = sum((a * b for a, b in zip(alpha_q, b_T)), start=Fraction(0))
    derived = sum_ab.numerator // sum_ab.denominator + 1
    payload = emit_certificate(
        sub_cols, alpha_q,
        graph_payload=graph_payload, root=root, notes=notes,
    )
    payload["claimed_bound"] = derived
    payload["dual_multipliers"] = [str(a) for a in alpha_q]
    with out_path.open("w") as fp:
        json.dump(payload, fp, indent=2)
    cert, g = load_certificate_file(out_path)
    res = check_certificate(cert, g)
    return {
        "n_active_columns": len(sub_cols),
        "rationalised_sum_alpha_b": str(sum_ab),
        "denominator": denominator,
        "derived_bound": derived,
        "checker_accepted": res.accepted,
        "checker_derived": res.derived_bound,
        "out_path": str(out_path),
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--root-pair", default="0,0")
    ap.add_argument("--seed", default="auto",
                    help="path to seed certificate; 'auto' loads the best one for the root from the CSV")
    ap.add_argument("--seed-path-len", type=int, default=7,
                    help="if no seed certificate, generate path-only seed at this max_len")
    ap.add_argument("--max-depth", type=int, default=5)
    ap.add_argument("--rounds", type=int, default=10)
    ap.add_argument("--pricing-top-k", type=int, default=16)
    ap.add_argument("--pricing-time-budget-s", type=float, default=30.0)
    ap.add_argument("--denominator", type=int, default=4800)
    ap.add_argument("--out", default="auto",
                    help="output certificate path; 'auto' picks based on root and final bound")
    args = ap.parse_args()

    rp = tuple(int(x) for x in args.root_pair.split(","))
    L = load_named_graph("L_fpy")
    LL = cartesian_product(L, L)
    n = LL.n
    adj = LL.adjacency()
    root = rp[0] * 8 + rp[1]

    if args.seed == "auto":
        # Try to load the best path certificate for this root from the CSV
        import csv
        csv_path = REPO_ROOT / "data/pebbling_product/root_orbit_bounds.csv"
        seed_path: Path | None = None
        with csv_path.open() as fp:
            for row in csv.DictReader(fp):
                if row["root_rep"] == f"({rp[0]},{rp[1]})":
                    seed_path = REPO_ROOT / row["certificate_path"]
                    break
        if seed_path is None or not seed_path.exists():
            # Fall back to generating seed paths
            print(f"no seed cert for root {rp}; generating path-only seed", flush=True)
            columns = seed_paths_for_root(adj, root, args.seed_path_len)
            graph_payload = {
                "n": LL.n,
                "edges": [list(e) for e in LL.edges],
                "name": "L_fpy_box_L_fpy",
            }
        else:
            print(f"loading seed certificate: {seed_path}", flush=True)
            columns, graph_payload, _r = load_seed_certificate(seed_path)
    else:
        seed_path = Path(args.seed)
        columns, graph_payload, _r = load_seed_certificate(seed_path)

    columns, alpha, y, fun = column_generation_loop(
        columns, adj, root, n,
        max_depth=args.max_depth,
        rounds=args.rounds,
        pricing_top_k=args.pricing_top_k,
        pricing_time_budget_s=args.pricing_time_budget_s,
    )

    # Rationalise and emit
    if args.out == "auto":
        out = REPO_ROOT / f"data/pebbling_product/certificates/root_{rp[0]}_{rp[1]}_priced.json"
    else:
        out = Path(args.out)

    summary = rationalise_and_emit(
        columns, alpha,
        n_vertices=n, root=root, denominator=args.denominator,
        graph_payload=graph_payload, out_path=out,
        notes=(
            f"Sparse column generation at root ({rp[0]},{rp[1]}) with "
            f"max_depth={args.max_depth}, {args.rounds} rounds. "
            f"Final LP value (float) = {fun:.6f}."
        ),
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
