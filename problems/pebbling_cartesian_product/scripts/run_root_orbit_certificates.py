"""Build a path-based rational certificate for every root orbit of L_fpy box L_fpy.

For each orbit representative ``r`` in V(L_fpy) x V(L_fpy):

1. Enumerate simple paths from ``r`` of length 2..max_len.
2. Build a basic Hurlbert path strategy for each: weights double from
   leaf 1 toward root.
3. Solve the master LP via SciPy HiGHS.
4. Rationalize alpha by round-and-fix at a chosen common denominator.
5. Verify rationally with check_pebbling_weight_certificate.
6. Persist the certificate to
   ``data/pebbling_product/certificates/path_orbit_<r0>_<r1>_max_len<L>.json``.
7. Record the orbit representative, orbit size, derived bound, and other
   metadata in ``data/pebbling_product/root_orbit_bounds.csv``.

Aut(L_fpy) is the symmetric group S_3 acting on the three degree-3
vertices {0, 5, 6}; combined with the L box L coordinate swap this gives
22 root orbits on the 64 vertices of V(L) x V(L). The maximum derived
bound across all orbits is a fully local rational upper bound for
pi(L_fpy box L_fpy).
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from collections import deque
from fractions import Fraction
from itertools import permutations
from pathlib import Path

import numpy as np
from scipy.optimize import linprog

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from check_pebbling_weight_certificate import check_certificate, load_certificate_file
from optimize_certificate_multipliers import _build_lp
from pebbling_graphs import cartesian_product, load_named_graph
from run_column_generation import enumerate_simple_paths, path_to_strategy
from run_column_generation_robust import round_and_fix
from branching_tree_columns import enumerate_branching_trees


def compute_root_orbits(L_n: int, L_edges) -> dict[tuple[int, int], list[tuple[int, int]]]:
    """Compute orbits of V(L) x V(L) under Aut(L) x Z_2 (coord swap).

    Returns a dict mapping orbit representative (lex-smallest) to the
    list of all (a, b) pairs in that orbit.
    """
    adj_set: set[tuple[int, int]] = set()
    deg = [0] * L_n
    for u, v in L_edges:
        adj_set.add((u, v))
        adj_set.add((v, u))
        deg[u] += 1
        deg[v] += 1

    autos: list[tuple[int, ...]] = []
    for perm in permutations(range(L_n)):
        if any(deg[perm[i]] != deg[i] for i in range(L_n)):
            continue
        if all((perm[u], perm[v]) in adj_set for u, v in L_edges):
            autos.append(perm)

    parent = {(a, b): (a, b) for a in range(L_n) for b in range(L_n)}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(x, y):
        rx, ry = find(x), find(y)
        if rx != ry:
            parent[rx] = ry

    for phi in autos:
        for a in range(L_n):
            for b in range(L_n):
                union((a, b), (phi[a], phi[b]))
                union((a, b), (phi[b], phi[a]))

    orbits: dict[tuple[int, int], list[tuple[int, int]]] = {}
    for v in parent:
        r = find(v)
        orbits.setdefault(r, []).append(v)

    # Re-key by lex-smallest representative
    return {min(o): sorted(o) for o in orbits.values()}


def build_certificate_for_root(
    root_pair: tuple[int, int],
    max_len: int,
    denominator: int,
    branching_max_depth: int = 0,
) -> tuple[dict | None, str | None, dict]:
    """Run the column-generation pipeline for one root.

    Returns (certificate_payload, error_message, summary_stats).
    """
    L = load_named_graph("L_fpy")
    LL = cartesian_product(L, L)
    n = LL.n
    adj = LL.adjacency()
    root_flat = root_pair[0] * 8 + root_pair[1]

    paths = enumerate_simple_paths(adj, root_flat, max_len=max_len)
    candidates = [path_to_strategy(p, root_flat) for p in paths]
    if branching_max_depth >= 2:
        candidates += enumerate_branching_trees(
            paths, root_flat, max_depth=branching_max_depth
        )

    payload = {
        "graph": {
            "n": LL.n,
            "edges": [list(e) for e in LL.edges],
            "name": "L_fpy_box_L_fpy",
        },
        "root": root_flat,
        "claimed_bound": 999,
        "strategies": candidates,
        "dual_multipliers": ["0"] * len(candidates),
    }
    tmp = REPO_ROOT / "data" / "pebbling_product" / "_tmp_orbit_cert.json"
    with tmp.open("w") as fp:
        json.dump(payload, fp)

    cert, g = load_certificate_file(tmp)
    if not cert.strategies:
        return None, "no candidate strategies generated", {}

    c, A_ub, rhs = _build_lp(cert, g.n)
    res = linprog(c=c, A_ub=A_ub, b_ub=rhs, bounds=[(0, None)] * len(c), method="highs-ds")
    if not res.success:
        return None, f"LP solve failed: {res.message}", {}

    nonzero_idx = [i for i, x in enumerate(res.x) if x > 1e-9]
    if not nonzero_idx:
        return None, "no active strategies in LP optimum (LP infeasible)", {}

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
        return None, f"round-and-fix failed at D={denominator}", {
            "lp_optimum_float": float(sub_res.fun),
            "n_paths": len(paths),
            "n_active": len(nonzero_idx),
        }

    sum_ab = sum((a * b for a, b in zip(alpha_q, b_T_rational)), start=Fraction(0))
    derived = sum_ab.numerator // sum_ab.denominator + 1

    out_payload = {
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
            f"Path-based column-generation certificate at root "
            f"({root_pair[0]}, {root_pair[1]}) flat={root_flat}. "
            f"max_len={max_len}, n_paths={len(paths)}, "
            f"n_active={len(nonzero_idx)}, "
            f"float LP = {float(sub_res.fun):.6f}, "
            f"rational sum alpha b = {sum_ab}, derived = {derived}, "
            f"D={denominator}."
        ),
    }
    return out_payload, None, {
        "lp_optimum_float": float(sub_res.fun),
        "lp_value_rational": str(sum_ab),
        "n_paths": len(paths),
        "n_active": len(nonzero_idx),
        "denominator": denominator,
        "derived_bound": derived,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--max-len", type=int, default=5)
    ap.add_argument("--branching-max-depth", type=int, default=0,
                    help="if >= 2, also include Y/trident branching trees up to this depth")
    ap.add_argument("--denominator", type=int, default=4800)
    ap.add_argument(
        "--out-dir",
        default=str(REPO_ROOT / "data" / "pebbling_product" / "certificates"),
    )
    ap.add_argument(
        "--csv-out",
        default=str(REPO_ROOT / "data" / "pebbling_product" / "root_orbit_bounds.csv"),
    )
    args = ap.parse_args()

    L = load_named_graph("L_fpy")
    orbits = compute_root_orbits(L.n, L.edges)
    print(f"Found {len(orbits)} root orbits on V(L) x V(L)")

    rows: list[dict] = []
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    for rep in sorted(orbits.keys()):
        orbit = orbits[rep]
        t0 = time.monotonic()
        # Escalate max_len from args.max_len upward if LP is infeasible
        cur_max_len = args.max_len
        payload = None
        err = None
        stats: dict = {}
        while payload is None and cur_max_len <= args.max_len + 3:
            payload, err, stats = build_certificate_for_root(
                rep, cur_max_len, args.denominator,
                branching_max_depth=args.branching_max_depth,
            )
            if payload is None and ("infeasible" in (err or "")):
                cur_max_len += 1
                print(
                    f"  rep ({rep[0]},{rep[1]}): infeasible at max_len={cur_max_len-1}, "
                    f"escalating to {cur_max_len}",
                    flush=True,
                )
                continue
            break
        elapsed = time.monotonic() - t0
        if payload is None:
            print(f"  rep ({rep[0]},{rep[1]}): FAILED: {err} ({elapsed:.1f}s)", flush=True)
            rows.append(
                {
                    "root_rep": f"({rep[0]},{rep[1]})",
                    "orbit_size": len(orbit),
                    "bound": "",
                    "lp_value": "",
                    "num_columns": "",
                    "max_len": cur_max_len,
                    "certificate_path": "",
                    "status": "failed",
                    "notes": err or "",
                    "elapsed_s": f"{elapsed:.1f}",
                }
            )
            continue

        suffix = (
            f"max_len{cur_max_len}"
            if args.branching_max_depth < 2
            else f"max_len{cur_max_len}_branch{args.branching_max_depth}"
        )
        cert_path = out_dir / f"path_orbit_{rep[0]}_{rep[1]}_{suffix}.json"
        with cert_path.open("w") as fp:
            json.dump(payload, fp, indent=2)

        # Verify with checker
        cert2, g2 = load_certificate_file(cert_path)
        chk = check_certificate(cert2, g2)
        status = "accepted" if chk.accepted else "rejected"
        bound = chk.derived_bound if chk.accepted else None

        print(
            f"  rep ({rep[0]},{rep[1]}): orbit size {len(orbit)}, "
            f"bound={bound}, LP={stats.get('lp_optimum_float', 0):.4f}, "
            f"cols={stats.get('n_active', 0)}, max_len={cur_max_len}, "
            f"{elapsed:.1f}s, status={status}",
            flush=True,
        )

        rows.append(
            {
                "root_rep": f"({rep[0]},{rep[1]})",
                "orbit_size": len(orbit),
                "bound": str(bound) if bound is not None else "",
                "lp_value": stats.get("lp_value_rational", ""),
                "num_columns": str(stats.get("n_active", "")),
                "max_len": cur_max_len,
                "certificate_path": str(cert_path.relative_to(REPO_ROOT)),
                "status": status,
                "notes": "",
                "elapsed_s": f"{elapsed:.1f}",
            }
        )

    # Write CSV
    csv_path = Path(args.csv_out)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    cols = [
        "root_rep",
        "orbit_size",
        "bound",
        "lp_value",
        "num_columns",
        "max_len",
        "certificate_path",
        "status",
        "notes",
        "elapsed_s",
    ]
    with csv_path.open("w", newline="") as fp:
        writer = csv.DictWriter(fp, fieldnames=cols)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)
    print(f"\nWrote {csv_path}")

    # Summary
    accepted = [r for r in rows if r["status"] == "accepted" and r["bound"]]
    if accepted:
        bounds = [int(r["bound"]) for r in accepted]
        max_b = max(bounds)
        worst_rows = [r for r in accepted if int(r["bound"]) == max_b]
        print(f"\nGlobal upper bound = max orbit bound = {max_b}")
        print(f"Worst orbit(s):")
        for r in worst_rows:
            print(f"  {r['root_rep']}: bound {r['bound']}, lp_value {r['lp_value']}")
    else:
        print("\nNo orbit produced an accepted certificate.")


if __name__ == "__main__":
    main()
