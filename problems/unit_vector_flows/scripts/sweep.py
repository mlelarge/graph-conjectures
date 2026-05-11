"""Snark-sweep harness: run the numerical witness oracle on a list of
named cubic bridgeless graphs and persist one JSON certificate per graph.

Use::

    python scripts/sweep.py --out data/sweep_results/<run-id>

The default catalogue is the small snark bench: Petersen, both Blanuša
snarks, and flower snarks J_5, J_7, J_9, J_11. Extend by editing
``CATALOGUE``.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import time
from typing import Callable

import networkx as nx

from certificate import witness_certificate, write_certificate
from graphs import (
    blanusa_first,
    blanusa_second,
    flower_snark,
    is_cubic_bridgeless,
    petersen,
)
from witness import find_witness


CATALOGUE: list[tuple[str, Callable[[], nx.Graph]]] = [
    ("Petersen", petersen),
    ("Blanusa-1", blanusa_first),
    ("Blanusa-2", blanusa_second),
    ("J_5", lambda: flower_snark(2)),
    ("J_7", lambda: flower_snark(3)),
    ("J_9", lambda: flower_snark(4)),
    ("J_11", lambda: flower_snark(5)),
]


def _named_catalogue() -> list[tuple[str, Callable[[], nx.Graph]]]:
    return list(CATALOGUE)


def _graph6_catalogue(path: pathlib.Path) -> list[tuple[str, Callable[[], nx.Graph]]]:
    from graphs import from_graph6

    items: list[tuple[str, Callable[[], nx.Graph]]] = []
    with path.open("r", encoding="ascii") as f:
        for i, line in enumerate(f):
            line = line.strip()
            if not line or line.startswith(">>"):
                continue
            g6 = line
            name = f"{path.stem}_{i:04d}"
            items.append((name, lambda g6=g6: from_graph6(g6)))
    return items


def run_sweep(
    out_dir: pathlib.Path,
    *,
    restarts: int,
    seed: int,
    residual_threshold: float,
    catalogue: list[tuple[str, Callable[[], nx.Graph]]] | None = None,
) -> list[dict]:
    out_dir.mkdir(parents=True, exist_ok=True)
    summary = []
    items = catalogue if catalogue is not None else _named_catalogue()
    for name, build in items:
        G = build()
        if not is_cubic_bridgeless(G):
            raise RuntimeError(f"{name} is not cubic bridgeless; refusing to run")
        t0 = time.time()
        # Try base seed; if the best witness sits at a "saddle plateau"
        # (residual <= threshold but >> machine epsilon, e.g. ~1e-26 instead
        # of ~1e-31), retry with alternate seeds so downstream Krawczyk
        # certification has a chance.
        seeds_to_try = [seed, seed + 100, seed + 200, seed + 300]
        result = None
        for s in seeds_to_try:
            r = find_witness(
                G,
                restarts=restarts,
                seed=s,
                residual_threshold=residual_threshold,
            )
            if result is None or r.best_residual_squared < result.best_residual_squared:
                result = r
            if result.best_residual_squared < 1e-28:
                break
        elapsed = time.time() - t0
        cert = witness_certificate(
            name,
            G,
            result,
            solver="scipy.optimize.least_squares (LM)",
            solver_params={
                "restarts": restarts,
                "residual_threshold": residual_threshold,
                "max_nfev": 4000,
                "xtol": 1e-15,
                "ftol": 1e-15,
                "gtol": 1e-15,
            },
            seed=seed,
        )
        cert["elapsed_seconds"] = elapsed
        path = out_dir / f"{name}.json"
        write_certificate(cert, path)
        row = {
            "name": name,
            "n": G.number_of_nodes(),
            "m": G.number_of_edges(),
            "status": result.status,
            "best_residual_squared": result.best_residual_squared,
            "n_restarts": result.n_restarts,
            "elapsed_seconds": elapsed,
            "certificate": str(path),
        }
        summary.append(row)
        print(
            f"{name:12s} n={row['n']:3d} status={row['status']:8s} "
            f"rss={row['best_residual_squared']:.2e} "
            f"restarts={row['n_restarts']:4d} time={elapsed:.2f}s"
        )
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2))
    return summary


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--out",
        type=pathlib.Path,
        default=pathlib.Path("data/sweep_results/initial"),
    )
    ap.add_argument("--restarts", type=int, default=400)
    ap.add_argument("--seed", type=int, default=2026)
    ap.add_argument("--residual-threshold", type=float, default=1e-10)
    ap.add_argument(
        "--from-catalogue",
        type=pathlib.Path,
        default=None,
        help="Read a graph6 catalogue file (one graph per line). "
        "Bypasses the named built-in catalogue.",
    )
    args = ap.parse_args()
    catalogue = _graph6_catalogue(args.from_catalogue) if args.from_catalogue else None
    run_sweep(
        args.out,
        restarts=args.restarts,
        seed=args.seed,
        residual_threshold=args.residual_threshold,
        catalogue=catalogue,
    )


if __name__ == "__main__":
    main()
