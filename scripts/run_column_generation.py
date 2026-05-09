"""Column-generation loop with simple path strategies as the candidate pool.

Procedure:

1. Start from a base certificate (e.g. the Hurlbert four-strategy
   certificate decomposed by root-branch).
2. Enumerate all simple paths from the root in ``L_fpy box L_fpy`` of
   length in a configurable range (default 2..5). Each path induces a
   basic Hurlbert tree strategy with weights doubling toward the root.
3. Solve the master LP with all candidate columns added at once.
4. Identify the active subset (alpha > 0).
5. Re-solve the reduced LP on the active columns; rationalize the
   resulting alpha exactly via tight-constraint Gauss-Jordan in
   ``Fraction`` arithmetic.
6. Verify dual feasibility rationally and emit a JSON certificate that
   the existing rational checker accepts.

This is a single-pass column-generation; it does not iterate. The
single pass is sufficient when the candidate pool already contains an
LP-improving column, which it does for the Hurlbert L box L (v_1, v_1)
problem: adding simple path strategies of length 2..5 lowers the LP
optimum from 107 to 47021/440 ~= 106.866, giving derived bound 107
(beating Hurlbert's 108).

Usage::

    python scripts/run_column_generation.py [--max-len 5] [--out path.json]
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import deque
from fractions import Fraction
from pathlib import Path

import numpy as np
from scipy.optimize import linprog

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from check_pebbling_weight_certificate import (
    check_certificate,
    load_certificate_file,
)
from optimize_certificate_multipliers import (
    _build_lp,
    _gauss_jordan_solve,
    _is_full_rank,
)
from pebbling_graphs import cartesian_product, load_named_graph


def enumerate_simple_paths(
    adj, root: int, min_len: int = 2, max_len: int = 5
) -> list[tuple[int, ...]]:
    """All simple paths starting at ``root`` of length in [min_len, max_len]."""
    paths: list[tuple[int, ...]] = []

    def dfs(path: list[int]) -> None:
        L = len(path) - 1
        if min_len <= L <= max_len:
            paths.append(tuple(path))
        if L >= max_len:
            return
        for nxt in adj[path[-1]]:
            if nxt not in path:
                path.append(nxt)
                dfs(path)
                path.pop()

    dfs([root])
    return paths


def path_to_strategy(path: tuple[int, ...], root: int) -> dict:
    """Basic Hurlbert path strategy from ``root`` along ``path``.

    Weights: root = 0, leaf at end = 1, doubling toward root."""
    d = len(path) - 1
    weights: dict[int, int] = {root: 0}
    for i in range(1, d + 1):
        weights[path[i]] = 2 ** (d - i)
    edges = [tuple(sorted([path[i], path[i + 1]])) for i in range(d)]
    return {
        "name": f"path len{d} to flat{path[-1]}",
        "tree_edges": [list(e) for e in edges],
        "weights": {str(k): str(v) for k, v in weights.items()},
        "basic": True,
    }


def run_pass(
    base_cert_path: Path,
    max_len: int,
    out_path: Path,
) -> dict:
    L = load_named_graph("L_fpy")
    LL = cartesian_product(L, L)
    n = LL.n
    adj = LL.adjacency()

    with base_cert_path.open() as fp:
        base = json.load(fp)
    root = int(base["root"])

    # Build the candidate pool
    paths = enumerate_simple_paths(adj, root, max_len=max_len)
    candidate_strategies = [path_to_strategy(p, root) for p in paths]

    # Combined pool
    all_strats = list(base["strategies"]) + candidate_strategies
    mega = dict(base)
    mega["strategies"] = all_strats
    mega["dual_multipliers"] = ["0"] * len(all_strats)
    mega["claimed_bound"] = 999

    tmp_path = Path("/tmp/_run_column_gen.json")
    with tmp_path.open("w") as fp:
        json.dump(mega, fp)

    cert, g = load_certificate_file(tmp_path)
    c, A_ub, rhs = _build_lp(cert, g.n)

    # Solve master LP
    res = linprog(
        c=c, A_ub=A_ub, b_ub=rhs,
        bounds=[(0, None)] * len(c),
        method="highs-ds",
    )
    if not res.success:
        raise RuntimeError(f"master LP failed: {res.message}")

    nonzero_idx = [i for i, x in enumerate(res.x) if x > 1e-9]
    sub_c = c[nonzero_idx]
    sub_A = A_ub[:, nonzero_idx]

    # Re-solve sub-LP for high precision
    sub_res = linprog(
        c=sub_c, A_ub=sub_A, b_ub=rhs,
        bounds=[(0, None)] * len(sub_c),
        method="highs-ds",
    )

    # Rationalise alpha via tight-constraint Gauss-Jordan
    n_strats = len(nonzero_idx)
    sub_strats = [cert.strategies[i] for i in nonzero_idx]
    sub_alpha = sub_res.x

    tight_rows: list[tuple[int, list[Fraction]]] = []
    non_root_vertices = [v for v in range(n) if v != cert.root]
    for v in non_root_vertices:
        row = [s.weights.get(v, Fraction(0)) for s in sub_strats]
        lhs = sum(a * float(r) for a, r in zip(sub_alpha, row))
        if abs(lhs - 1.0) < 1e-7:
            tight_rows.append((v, row))

    chosen: list[list[Fraction]] = []
    for v, row in tight_rows:
        test = chosen + [row]
        if _is_full_rank(test, n_strats):
            chosen = test
        if len(chosen) == n_strats:
            break
    if len(chosen) != n_strats:
        raise RuntimeError(
            f"could not find {n_strats} linearly independent tight rows; got {len(chosen)}"
        )

    augmented = [list(row) + [Fraction(1)] for row in chosen]
    alpha_rational = _gauss_jordan_solve(augmented)
    if alpha_rational is None:
        raise RuntimeError("Gauss-Jordan failed (singular system)")
    if any(a < 0 for a in alpha_rational):
        raise RuntimeError(f"negative alpha after rationalisation: {alpha_rational}")

    b_T_rational = [
        sum(
            (w for v, w in s.weights.items() if v != cert.root),
            start=Fraction(0),
        )
        for s in sub_strats
    ]
    sum_ab = sum(
        (a * b for a, b in zip(alpha_rational, b_T_rational)),
        start=Fraction(0),
    )
    derived = sum_ab.numerator // sum_ab.denominator + 1

    # Verify dual feasibility rationally on every non-root vertex
    for v in range(g.n):
        if v == cert.root:
            continue
        t = sum(
            (a * s.weights.get(v, Fraction(0)) for a, s in zip(alpha_rational, sub_strats)),
            start=Fraction(0),
        )
        if t < 1:
            raise RuntimeError(f"dual feasibility fails at v={v}: sum = {t} < 1")

    output = {
        "graph": base["graph"],
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
        "dual_multipliers": [str(a) for a in alpha_rational],
        "notes": (
            f"Column-generation pass with simple path strategies up to length {max_len} "
            f"on top of the input certificate {base_cert_path.name}. "
            f"LP optimum (rational): {sum_ab}. Derived bound = "
            f"floor({sum_ab}) + 1 = {derived}."
        ),
    }
    with out_path.open("w") as fp:
        json.dump(output, fp, indent=2)

    # Cross-check with the existing rational checker
    cert2, g2 = load_certificate_file(out_path)
    check = check_certificate(cert2, g2)

    return {
        "n_candidate_paths": len(paths),
        "n_active_strategies": len(nonzero_idx),
        "lp_optimum_float": float(sub_res.fun),
        "sum_alpha_b_rational": str(sum_ab),
        "derived_bound": derived,
        "checker_accepted": check.accepted,
        "checker_derived": check.derived_bound,
        "out_path": str(out_path),
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument(
        "--base",
        default=str(
            REPO_ROOT
            / "data/pebbling_product/certificates/Hurlbert_decomposed_branches_v1v1.json"
        ),
        help="path to base certificate (will be extended)",
    )
    ap.add_argument("--max-len", type=int, default=5)
    ap.add_argument(
        "--out",
        default=str(
            REPO_ROOT
            / "data/pebbling_product/certificates/Hurlbert_path_augmented_v1v1_le107.json"
        ),
    )
    args = ap.parse_args()
    summary = run_pass(Path(args.base), args.max_len, Path(args.out))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
