"""Weighted / geometric CDC ansatz for $\\Sigma_4$-flows.

The discrete H_4 construction (MMRT 2025) is dead for snarks: an
oriented 4-CDC on a cubic graph forces a nowhere-zero 4-flow, so no
snark admits one. The relaxation here keeps the *cycle* part of the
construction but replaces basis-vector cycle labels with arbitrary
4-vectors:

  - choose any cycle double cover :math:`\\mathcal{C} = \\{C_1, ..., C_t\\}`
    of G (not required to be orientable in the H_4 sense);
  - assign each cycle a vector :math:`w_k \\in \\mathbb{R}^4` with
    :math:`\\sum_i (w_k)_i = 0`;
  - on each edge :math:`e` covered by cycles :math:`C_i, C_j`, define
    the edge vector

        v_e = sigma_{e,i} w_i + sigma_{e,j} w_j,

    where :math:`\\sigma_{e,k} \\in \\{+1, -1\\}` records whether
    :math:`C_k` traverses :math:`e` in the canonical (lex) direction;
  - require :math:`v_e \\in \\Sigma_4 = \\{x : \\sum x_i = 0,
    \\sum x_i^2 = 2\\}` for every edge.

The sum-to-zero per edge is automatic from the per-cycle constraint;
the only nontrivial per-edge requirement is :math:`\\sum (v_e)_i^2 = 2`.

A solution defines a :math:`\\Sigma_4`-flow, hence an $S^2$-flow via
the isometry between :math:`\\Sigma_4` and a sphere of radius
:math:`\\sqrt{2}` in the 3-plane :math:`\\{\\sum x_i = 0\\}`.

This module provides:

* ``setup_edge_constraints(G, cdc)``: produce the per-edge
  (ci, sigma_i, cj, sigma_j) data from an unoriented CDC and a fixed
  per-cycle list direction.
* ``solve_weighted_cdc(G, cdc, ...)``: nonlinear least-squares search
  for the cycle vectors.
* ``flow_from_weights(G, cdc, W)``: assemble the per-edge :math:`v_e`
  values from the cycle vectors and return them, ready for verification.
* ``sigma4_to_s2(V)``: isometric embedding :math:`\\Sigma_4 \\to S^2`
  for cross-checking against the existing Krawczyk witness format.
"""
from __future__ import annotations

import numpy as np
import networkx as nx
from scipy.optimize import least_squares

from witness import orient


def setup_edge_constraints(
    G: nx.Graph, cdc: list
) -> tuple[list[tuple], list[tuple]]:
    """Compute per-edge (ci, sigma_i, cj, sigma_j) tuples from a CDC.

    Returns ``(edges, constraints)`` where ``edges`` is the canonical
    edge list of G and ``constraints[k]`` is the 4-tuple for ``edges[k]``.

    The "sigma" sign records the orientation of the cycle's traversal
    relative to the canonical edge direction. We do *not* require the
    CDC to be orientable in the H_4 sense; sigmas just reflect the
    arbitrary list-order direction of each cycle. The continuous cycle
    vectors w_k absorb any sign mismatch.
    """
    edges, _ = orient(G)
    edge_index = {e: k for k, e in enumerate(edges)}
    edge_uses: list[list[tuple[int, int]]] = [[] for _ in edges]

    for ci, cyc in enumerate(cdc):
        L = len(cyc)
        for i in range(L):
            u, v = cyc[i], cyc[(i + 1) % L]
            a, b = (u, v) if u < v else (v, u)
            if (a, b) not in edge_index:
                raise ValueError(f"cycle {ci} uses non-edge {a}-{b}")
            k = edge_index[(a, b)]
            sigma = +1 if (u, v) == (a, b) else -1
            edge_uses[k].append((ci, sigma))

    constraints: list[tuple[int, int, int, int]] = []
    for k, uses in enumerate(edge_uses):
        if len(uses) != 2:
            raise ValueError(
                f"edge {edges[k]} is covered {len(uses)} times, expected 2"
            )
        (ci, si), (cj, sj) = uses
        constraints.append((ci, si, cj, sj))
    return edges, constraints


def _residual(params: np.ndarray, n_cycles: int, n_dim: int, constraints: list) -> np.ndarray:
    W = params.reshape(n_cycles, n_dim)
    out: list[float] = []
    # Per-cycle sum-to-zero (so edge vectors automatically sum to zero).
    for c in range(n_cycles):
        out.append(float(W[c].sum()))
    # Per-edge: |sigma_i w_i + sigma_j w_j|^2 == 2.
    for ci, si, cj, sj in constraints:
        v = si * W[ci] + sj * W[cj]
        out.append(float(v @ v - 2.0))
    return np.asarray(out)


def solve_weighted_cdc(
    G: nx.Graph,
    cdc: list,
    *,
    n_dim: int = 4,
    n_restarts: int = 400,
    seed: int = 2026,
    residual_threshold: float = 1e-20,
    max_nfev: int = 4000,
) -> dict:
    """Search numerically for cycle vectors realising a Sigma_n-flow.

    Returns a dict with keys ``status``, ``best_rss``, ``best_max``,
    ``W`` (best cycle-vector matrix), ``n_restarts_used``,
    ``converged_restart`` (None if not converged).
    """
    edges, constraints = setup_edge_constraints(G, cdc)
    n_cycles = len(cdc)
    rng = np.random.default_rng(seed)
    best_rss = float("inf")
    best_max = float("inf")
    best_W: np.ndarray | None = None
    converged_restart: int | None = None
    n_restarts_used = 0

    for r in range(n_restarts):
        n_restarts_used += 1
        x0 = rng.standard_normal(n_cycles * n_dim)
        try:
            result = least_squares(
                _residual, x0,
                args=(n_cycles, n_dim, constraints),
                method="lm",
                max_nfev=max_nfev,
                xtol=1e-15, ftol=1e-15, gtol=1e-15,
            )
        except ValueError:
            # Probably "Method 'lm' doesn't work when #residuals < #vars".
            # Fall back to trust-region reflective.
            result = least_squares(
                _residual, x0,
                args=(n_cycles, n_dim, constraints),
                method="trf",
                max_nfev=max_nfev,
                xtol=1e-15, ftol=1e-15, gtol=1e-15,
            )
        rss = float(np.sum(result.fun ** 2))
        if rss < best_rss:
            best_rss = rss
            best_max = float(np.max(np.abs(result.fun)))
            best_W = result.x.reshape(n_cycles, n_dim)
            if rss < residual_threshold:
                converged_restart = r
                break

    status = "solved" if best_rss < residual_threshold else "unsolved"
    return {
        "status": status,
        "best_rss": best_rss,
        "best_max": best_max,
        "W": best_W,
        "n_cycles": n_cycles,
        "n_dim": n_dim,
        "n_constraints": n_cycles + len(constraints),
        "n_restarts_used": n_restarts_used,
        "converged_restart": converged_restart,
        "edges": edges,
    }


def solve_first_weighted_cdc(
    G: nx.Graph,
    *,
    max_cdcs: int = 50,
    max_cycle_length: int | None = None,
    cdc_time_budget_s: float = 30.0,
    solve_n_restarts: int = 200,
    solve_seed: int = 2026,
    residual_threshold: float = 1e-20,
) -> dict:
    """Iterate CDCs of G until one admits a weighted-CDC Sigma_4 flow.

    Returns the first successful ``solve_weighted_cdc`` result, augmented
    with the CDC itself. If none of ``max_cdcs`` candidates work, returns
    a dict with ``status == "unsolved"`` and the *best* residual seen.
    """
    from cdc import iter_cdcs

    best: dict | None = None
    tried = 0
    for cdc in iter_cdcs(
        G,
        max_cycle_length=max_cycle_length,
        time_budget_s=cdc_time_budget_s,
        max_solutions=max_cdcs,
    ):
        tried += 1
        try:
            res = solve_weighted_cdc(
                G, cdc,
                n_restarts=solve_n_restarts,
                seed=solve_seed,
                residual_threshold=residual_threshold,
            )
        except ValueError:
            continue
        res["cdc"] = cdc
        res["cdc_index"] = tried - 1
        res["cdcs_tried"] = tried
        if res["status"] == "solved":
            return res
        if best is None or res["best_rss"] < best["best_rss"]:
            best = res
    if best is None:
        return {"status": "unsolved", "best_rss": float("inf"), "cdcs_tried": tried, "note": "no CDC found within budget"}
    return best


def flow_from_weights(
    G: nx.Graph, cdc: list, W: np.ndarray
) -> tuple[list[tuple], np.ndarray]:
    """Assemble per-edge Sigma_n vectors from cycle vectors.

    Returns ``(edges, V)`` where ``V`` is an ``(m, n_dim)`` array, one
    Sigma_n vector per edge in canonical edge order.
    """
    edges, constraints = setup_edge_constraints(G, cdc)
    V = np.zeros((len(edges), W.shape[1]), dtype=np.float64)
    for k, (ci, si, cj, sj) in enumerate(constraints):
        V[k] = si * W[ci] + sj * W[cj]
    return edges, V


def sigma4_to_s2(V: np.ndarray) -> np.ndarray:
    """Isometrically map Sigma_4 vectors to unit S^2 in R^3.

    Sigma_4 = {x in R^4 : sum x_i = 0, sum x_i^2 = 2}; the hyperplane
    {sum x_i = 0} is 3-dimensional; we use the orthonormal basis

        b_1 = (+1, -1,  0,  0) / sqrt(2)
        b_2 = (+1, +1, -2,  0) / sqrt(6)
        b_3 = (+1, +1, +1, -3) / sqrt(12)

    A vector with |x|^2 = 2 maps to a vector of length sqrt(2); we
    rescale by 1/sqrt(2) to get a unit vector in R^3.
    """
    basis = np.array([
        [+1.0, -1.0,  0.0,  0.0],
        [+1.0, +1.0, -2.0,  0.0],
        [+1.0, +1.0, +1.0, -3.0],
    ])
    basis[0] /= np.sqrt(2)
    basis[1] /= np.sqrt(6)
    basis[2] /= np.sqrt(12)
    V3 = V @ basis.T
    return V3 / np.sqrt(2)


if __name__ == "__main__":
    import json

    from graphs import petersen
    from cdc import find_cdc, cdc_summary

    G = petersen()
    cdc = find_cdc(G, max_cycle_length=10, time_budget_s=5.0)
    print("CDC:", cdc_summary(cdc, G))
    result = solve_weighted_cdc(G, cdc, n_restarts=200, seed=2026)
    print(f"status={result['status']} rss={result['best_rss']:.3e} max|r|={result['best_max']:.3e} restarts={result['n_restarts_used']}")
    if result["status"] == "solved":
        edges, V = flow_from_weights(G, cdc, result["W"])
        norms = np.linalg.norm(V, axis=1)
        sums = V.sum(axis=1)
        print(f"  edge norms in [{norms.min():.4f}, {norms.max():.4f}] (target sqrt(2)={np.sqrt(2):.4f})")
        print(f"  edge component sums in [{sums.min():.2e}, {sums.max():.2e}] (target 0)")
        V3 = sigma4_to_s2(V)
        n3 = np.linalg.norm(V3, axis=1)
        print(f"  S^2 image: norms in [{n3.min():.6f}, {n3.max():.6f}] (target 1)")
