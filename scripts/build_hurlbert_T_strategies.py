"""Build a Hurlbert weight-function certificate for pi(L_fpy box L_fpy, (v_1, v_1)) <= 108.

Encodes the four nonbasic tree strategies T_1, T_2, T_3, T_4 from
Figure 5 of G. Hurlbert, *The weight function lemma for graph pebbling*,
J. Combinatorial Optimization 34(2) (2017), 343-361 (arXiv:1101.5641),
Theorem 10. The matrices were transcribed from the layout-preserving
text extraction of the arXiv PDF.

The four strategies are presented in the paper as 8x8 weight matrices on
V(L) x V(L). Their average has every non-root entry >= 1 and total 107,
which combined with dual multipliers alpha_i = 1/4 each gives the
published bound 108. The L labelling used by Hurlbert in the WFL paper
matches the labelling used by Flocco-Pulaj-Yerger 2024
(``data/pebbling_product/graphs/L_fpy.json``): root v_1 has degree 2.

Run as a script to emit the certificate JSON and run the rational
checker. Run from project root.
"""

from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
import sys

sys.path.insert(0, str(REPO_ROOT / "scripts"))

from check_pebbling_weight_certificate import (
    check_certificate,
    parse_certificate,
)
from pebbling_graphs import (
    cartesian_product,
    load_named_graph,
    pair_to_index,
)


# Hurlbert WFL paper, Figure 5: four nonbasic tree strategies for L box L
# at root r = (v_1, v_1). Each matrix is rows v_1..v_8 (1-indexed) by
# columns v_1..v_8. We index here as 0..7 (v_i corresponds to row/col i-1).

T1 = [
    [0, 0, 32, 0, 16, 4, 4, 8],
    [0, 0, 4, 0, 0, 0, 0, 0],
    [0, 0, 4, 0, 2, 2, 2, 4],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 2, 0, 1, 1, 1, 2],
    [0, 0, 2, 0, 1, 1, 1, 0],
    [0, 0, 2, 0, 1, 1, 1, 0],
    [0, 0, 0, 0, 0, 0, 0, 1],
]

T2 = [
    [0, 0, 0, 0, 0, 0, 0, 0],
    [32, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [16, 4, 4, 0, 2, 2, 2, 2],
    [4, 0, 2, 0, 1, 1, 1, 0],
    [4, 0, 2, 0, 1, 1, 1, 2],
    [4, 0, 2, 0, 1, 1, 1, 2],
    [8, 0, 4, 0, 2, 2, 2, 1],
]

T3 = [
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [32, 16, 0, 4, 2, 2, 2, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 8, 0, 2, 1, 1, 1, 1],
    [0, 4, 0, 2, 1, 1, 1, 1],
    [0, 4, 0, 2, 1, 1, 1, 1],
    [0, 4, 0, 2, 1, 1, 1, 1],
]

T4 = [
    [0, 32, 0, 4, 0, 0, 0, 0],
    [0, 16, 0, 8, 4, 4, 4, 4],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 4, 2, 2, 2, 2],
    [0, 0, 0, 2, 1, 1, 1, 1],
    [0, 0, 0, 2, 1, 1, 1, 1],
    [0, 0, 0, 2, 1, 1, 1, 1],
    [0, 0, 0, 2, 1, 1, 1, 1],
]

T_AVG_PUBLISHED = [
    [0, 8, 8, 1, 4, 1, 1, 2],
    [8, 4, 1, 2, 1, 1, 1, 1],
    [8, 4, 1, 1, 1, 1, 1, 1],
    [4, 1, 1, 1, 1, 1, 1, 1],
    [1, 2, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1],
    [2, 1, 1, 1, 1, 1, 1, 1],
]


def verify_avg() -> None:
    """Sanity check: (T1+T2+T3+T4)/4 equals the published averaged matrix."""
    for i in range(8):
        for j in range(8):
            s = T1[i][j] + T2[i][j] + T3[i][j] + T4[i][j]
            avg = T_AVG_PUBLISHED[i][j]
            assert s == 4 * avg, (
                f"mismatch at ({i+1},{j+1}): T1+T2+T3+T4 = {s}, "
                f"4 * T_avg = {4 * avg}"
            )
    total = sum(T_AVG_PUBLISHED[i][j] for i in range(8) for j in range(8))
    assert total == 107, f"sum of T_avg = {total}, expected 107"


def build_tree_for_strategy(
    matrix: list[list[int]],
    factor_n: int,
    factor_adj: list[list[int]],
    root_pair: tuple[int, int],
) -> tuple[list[tuple[int, int]], dict[int, str]]:
    """Greedily build a rooted tree on V(strategy) in L_fpy box L_fpy.

    Vertices in V(strategy) are root plus all (i, j) with matrix[i][j] > 0.
    For each non-root vertex v with weight w > 0, pick a parent in
    V(strategy) that is a neighbour of v in the Cartesian product and
    whose weight is >= 2 * w. Use BFS from the root to ensure
    reachability and avoid cycles.

    Returns (tree_edges_flat, weights_dict_str).
    """
    n_factor = factor_n
    n_total = n_factor * n_factor

    # Identify V(T) as flat indices.
    root_flat = pair_to_index(root_pair[0], root_pair[1], n_factor)
    weights: dict[int, int] = {root_flat: 0}
    for i in range(n_factor):
        for j in range(n_factor):
            if (i, j) == root_pair:
                continue
            if matrix[i][j] > 0:
                weights[pair_to_index(i, j, n_factor)] = matrix[i][j]

    vset = set(weights.keys())

    # Build product-graph adjacency restricted to V(T).
    def product_neighbours(flat: int) -> list[int]:
        u, v = divmod(flat, n_factor)
        out: list[int] = []
        # same first coord, second coord neighbours
        for w in factor_adj[v]:
            other = pair_to_index(u, w, n_factor)
            if other in vset:
                out.append(other)
        # same second coord, first coord neighbours
        for w in factor_adj[u]:
            other = pair_to_index(w, v, n_factor)
            if other in vset:
                out.append(other)
        return out

    # BFS from root, picking each visited non-root vertex's parent to be
    # the visited vertex (enqueue) with weight >= 2 * w(child).
    # Implementation: standard BFS where, for each unvisited neighbour
    # `succ` of the current node `u`, we accept (u, succ) as a tree edge
    # iff w(u) >= 2 * w(succ) AND succ in vset.
    parent: dict[int, int] = {root_flat: -1}
    queue = [root_flat]
    while queue:
        u = queue.pop(0)
        wu = weights[u]
        for succ in product_neighbours(u):
            if succ in parent:
                continue
            ws = weights[succ]
            # Doubling check: if u is root, free weight; else need wu >= 2*ws
            if u == root_flat:
                # any positive weight ok
                pass
            else:
                if wu < 2 * ws:
                    # cannot use u as parent of succ
                    continue
            parent[succ] = u
            queue.append(succ)

    missing = vset - set(parent.keys())
    if missing:
        # Try a second pass with relaxed constraint: maybe some vertex
        # needs parent visited later. Keep iterating until stable or
        # truly stuck.
        for _ in range(len(vset)):
            progress = False
            for succ in list(missing):
                ws = weights[succ]
                # find any visited neighbour with weight >= 2 * ws
                for u in product_neighbours(succ):
                    if u not in parent:
                        continue
                    wu = weights[u]
                    if u == root_flat or wu >= 2 * ws:
                        parent[succ] = u
                        missing.discard(succ)
                        progress = True
                        break
            if not progress:
                break
    if missing:
        raise RuntimeError(
            f"could not assign parents for vertices {sorted(missing)}"
        )

    edges: list[tuple[int, int]] = []
    for v, p in parent.items():
        if p == -1:
            continue
        u, w = (p, v) if p < v else (v, p)
        edges.append((u, w))
    weights_str = {str(k): str(v) for k, v in weights.items()}
    return edges, weights_str


# Permutation found by exhaustive search over 8! relabellings: any of these
# 12 permutations makes all four T_i strategies satisfy Hurlbert's nonbasic
# doubling condition under the resulting L adjacency. We pick the first.
# perm[i] = FPY-L vertex of WFL v_{i+1}.
WFL_TO_FPY = (4, 3, 2, 1, 5, 0, 6, 7)


def relabel_matrix(M_wfl: list[list[int]], perm: tuple[int, ...]) -> list[list[int]]:
    """M_fpy[perm[i]][perm[j]] = M_wfl[i][j]; return M in FPY labelling."""
    n = len(M_wfl)
    M_fpy = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            M_fpy[perm[i]][perm[j]] = M_wfl[i][j]
    return M_fpy


def build_certificate() -> dict:
    """Construct the full Hurlbert certificate for L_fpy box L_fpy at the WFL root."""
    L = load_named_graph("L_fpy")
    n = L.n
    adj = L.adjacency()
    LL = cartesian_product(L, L, name="L_fpy_box_L_fpy")

    # WFL root v_1 maps to FPY vertex WFL_TO_FPY[0] in our L_fpy.
    root_fpy = WFL_TO_FPY[0]
    root_pair = (root_fpy, root_fpy)
    root_flat = pair_to_index(root_pair[0], root_pair[1], n)

    strategies = []
    for label, mat_wfl in (("T_1", T1), ("T_2", T2), ("T_3", T3), ("T_4", T4)):
        mat_fpy = relabel_matrix(mat_wfl, WFL_TO_FPY)
        edges, weights = build_tree_for_strategy(mat_fpy, n, adj, root_pair)
        strategies.append(
            {
                "name": f"Hurlbert WFL Theorem 10 Figure 5 {label}",
                "tree_edges": [list(e) for e in edges],
                "weights": weights,
                "basic": False,
            }
        )

    return {
        "graph": {
            "n": LL.n,
            "edges": [list(e) for e in LL.edges],
            "name": "L_fpy_box_L_fpy",
        },
        "root": root_flat,
        "claimed_bound": 108,
        "strategies": strategies,
        "dual_multipliers": ["1/4", "1/4", "1/4", "1/4"],
        "notes": (
            "Hurlbert 2017 WFL paper Theorem 10 (arXiv:1101.5641). "
            "Four nonbasic tree strategies whose weight matrices average to the "
            "T_avg published bound for pi(L box L, (v_1, v_1)) <= 108. "
            "Hurlbert WFL uses a different vertex labelling of L than FPY: "
            f"v_1..v_8 (WFL) = vertices {list(WFL_TO_FPY)} of L_fpy. "
            "Found by exhaustive search; 12 such permutations exist (all "
            "isomorphic via Aut(L)). Tree edges chosen by greedy BFS from "
            "the root respecting the nonbasic doubling rule w(parent) >= 2 w(child)."
        ),
        "wfl_to_fpy_relabeling": list(WFL_TO_FPY),
    }


def main() -> None:
    verify_avg()
    print("(T_1 + T_2 + T_3 + T_4) / 4 == published averaged matrix: OK")

    payload = build_certificate()

    # Persist for inspection / downstream use.
    out = (
        REPO_ROOT
        / "data"
        / "pebbling_product"
        / "certificates"
        / "Hurlbert_T1_T2_T3_T4_v1v1_le108.json"
    )
    with out.open("w") as fp:
        # The JSON is large because the L box L edge list is included
        # (208 edges). Keep it readable but compact.
        json.dump(payload, fp, indent=2)
    print(f"wrote {out}")

    # Run the checker.
    cert = parse_certificate(payload)
    from pebbling_graphs import make_graph

    gp = payload["graph"]
    g = make_graph(int(gp["n"]), gp["edges"], name=gp["name"])
    res = check_certificate(cert, g)
    print(f"\nchecker accepted: {res.accepted}")
    print(f"derived bound: {res.derived_bound}")
    print(f"claimed bound: {res.claimed_bound}")
    print(f"sum alpha_i b_i = {res.sum_alpha_b}")
    if res.failure:
        print("failure stage:", res.failure.get("stage"))
        print("failure reason:", res.failure.get("reason", "")[:200])
    if res.extra:
        print("per-strategy contributions:")
        for s in res.extra.get("per_strategy", []):
            print(f"  {s['name']}: alpha = {s['alpha']}, b_T = {s['b_T']}, "
                  f"alpha*b = {s['alpha_b']}")


if __name__ == "__main__":
    main()
