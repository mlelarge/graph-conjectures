"""Column-generation experiment: shortest-path single-anchor strategies on L_fpy box L_fpy.

For each non-root vertex u of L_fpy box L_fpy, build the basic Hurlbert
tree strategy supported on the unique BFS shortest path from the root
``(v_1, v_1)`` to ``u``: weights double from leaf (weight 1 at u) toward
root. Adds each such strategy to Hurlbert's four published strategies
and re-runs the master LP from
``scripts/optimize_certificate_multipliers.py``. If any strategy
produces an LP optimum strictly less than 107 it is reported as an
improvement candidate.

This is a deliberately narrow column-generation pass: it does not
search the full space of valid Hurlbert strategies. It is intended as
a sanity check that the four published strategies are not trivially
beaten by a single additional path strategy. The null result --
no single-anchor BFS path strategy lowers the LP below 107 -- is
itself useful evidence that the four-strategy optimum is robust.

Run from project root::

    PYTHONPATH=scripts python scripts/column_generate_path_strategies.py
"""

from __future__ import annotations

import json
from collections import deque
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
import sys

sys.path.insert(0, str(REPO_ROOT / "scripts"))

from optimize_certificate_multipliers import optimize_multipliers
from pebbling_graphs import (
    cartesian_product,
    load_named_graph,
    pair_to_index,
)


@dataclass
class AnchorResult:
    anchor_flat: int
    anchor_pair: tuple[int, int]
    depth: int
    lp_sum_alpha_b: Fraction
    alpha_rational: list[Fraction]


def _bfs_shortest_path(adj, src: int, dst: int) -> list[int]:
    pred = {src: None}
    q = deque([src])
    while q:
        v = q.popleft()
        if v == dst:
            break
        for w in adj[v]:
            if w not in pred:
                pred[w] = v
                q.append(w)
    if dst not in pred:
        return []
    path = []
    cur = dst
    while cur is not None:
        path.append(cur)
        cur = pred[cur]
    path.reverse()
    return path


def _single_anchor_strategy(root: int, anchor: int, adj) -> dict | None:
    path = _bfs_shortest_path(adj, root, anchor)
    if not path:
        return None
    d = len(path) - 1
    weights: dict[int, int] = {root: 0}
    for i, v in enumerate(path[1:], start=1):
        weights[v] = 2 ** (d - i)
    edges = [tuple(sorted([path[i], path[i + 1]])) for i in range(len(path) - 1)]
    return {
        "weights": weights,
        "edges": edges,
        "depth": d,
    }


def run_column_generation(base_cert_path: Path) -> dict:
    with base_cert_path.open() as fp:
        base_payload = json.load(fp)

    L = load_named_graph("L_fpy")
    LL = cartesian_product(L, L)
    n = LL.n
    adj = LL.adjacency()

    # Determine root from the certificate
    root = int(base_payload["root"])

    # Try every non-root vertex as anchor
    results: list[AnchorResult] = []
    improvements: list[AnchorResult] = []

    for anchor in range(n):
        if anchor == root:
            continue
        s = _single_anchor_strategy(root, anchor, adj)
        if s is None:
            continue
        new_strat = {
            "name": f"single-anchor BFS strategy at flat {anchor}",
            "tree_edges": [list(e) for e in s["edges"]],
            "weights": {str(k): str(v) for k, v in s["weights"].items()},
            "basic": True,
        }
        new_payload = dict(base_payload)
        new_payload["strategies"] = list(base_payload["strategies"]) + [new_strat]
        new_payload["dual_multipliers"] = ["1/5"] * 5
        new_payload["claimed_bound"] = 999  # placeholder

        tmp_path = Path("/tmp/_col_gen_candidate.json")
        with tmp_path.open("w") as fp:
            json.dump(new_payload, fp)

        try:
            opt = optimize_multipliers(tmp_path)
        except RuntimeError:
            continue

        ar = AnchorResult(
            anchor_flat=anchor,
            anchor_pair=tuple(divmod(anchor, 8)),
            depth=s["depth"],
            lp_sum_alpha_b=opt.sum_alpha_b_rational,
            alpha_rational=list(opt.alpha_rational),
        )
        results.append(ar)
        if opt.sum_alpha_b_rational < 107:
            improvements.append(ar)

    return {
        "n_candidates": len(results),
        "n_improvements": len(improvements),
        "best_lp_value": min(
            (r.lp_sum_alpha_b for r in results), default=Fraction(108)
        ),
        "improvements": [
            {
                "anchor_flat": r.anchor_flat,
                "anchor_pair": list(r.anchor_pair),
                "depth": r.depth,
                "lp_sum_alpha_b": str(r.lp_sum_alpha_b),
                "alpha": [str(a) for a in r.alpha_rational],
            }
            for r in improvements
        ],
    }


def main() -> None:
    cert_path = (
        REPO_ROOT
        / "data"
        / "pebbling_product"
        / "certificates"
        / "Hurlbert_T1_T2_T3_T4_v1v1_le108.json"
    )
    summary = run_column_generation(cert_path)
    print(json.dumps(summary, indent=2))
    if summary["n_improvements"] == 0:
        print(
            "\nNegative result: no single-anchor BFS shortest-path-tree strategy "
            "lowers the LP optimum below 107 when added to Hurlbert's four "
            "strategies. The four-strategy optimum is robust against this class "
            "of mutations."
        )


if __name__ == "__main__":
    main()
