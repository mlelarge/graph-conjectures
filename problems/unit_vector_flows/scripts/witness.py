"""Numerical witness search for S²-flows on cubic graphs.

An S²-flow on a cubic graph G assigns to each edge e a unit vector
:math:`x_e \\in \\mathbb{R}^3` such that, for every vertex v with a fixed
orientation of incident edges, :math:`\\sum_{e\\ni v}\\sigma(v,e) x_e = 0`.

We search via Levenberg–Marquardt least squares. The squared-norm residual
sums over all vertex Kirchhoff equations and all unit-norm constraints:

.. math:: \\mathrm{loss}(X) = \\sum_v \\|\\sum_{e\\ni v}\\sigma(v,e)x_e\\|^2
                            + \\sum_e (\\|x_e\\|^2-1)^2.

A run that drops below ``residual_threshold`` stores a numerical witness.
A run that does not is *not* a proof of nonexistence; that requires the
exact / SOS backend.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from typing import Optional

import networkx as nx
import numpy as np
from scipy.optimize import least_squares


def orient(G: nx.Graph) -> tuple[list[tuple], dict]:
    edges = sorted(tuple(sorted((u, v))) for u, v in G.edges())
    sign: dict = {v: [] for v in G.nodes()}
    for k, (u, v) in enumerate(edges):
        sign[u].append((k, +1.0))
        sign[v].append((k, -1.0))
    return edges, sign


def _residual(x_flat: np.ndarray, sign: dict, m: int) -> np.ndarray:
    X = x_flat.reshape(m, 3)
    out = np.empty(3 * len(sign) + m, dtype=np.float64)
    i = 0
    for terms in sign.values():
        s = np.zeros(3)
        for k, sigma in terms:
            s += sigma * X[k]
        out[i : i + 3] = s
        i += 3
    out[i:] = (X * X).sum(axis=1) - 1.0
    return out


def _random_unit_vectors(m: int, rng: np.random.Generator) -> np.ndarray:
    X = rng.standard_normal(size=(m, 3))
    X /= np.linalg.norm(X, axis=1, keepdims=True)
    return X


@dataclass
class WitnessResult:
    status: str  # "witness" | "unknown"
    best_residual_squared: float
    best_max_abs_residual: float
    n_restarts: int
    converged_restart: Optional[int]
    n_vertices: int
    n_edges: int
    edges: list[tuple] = field(default_factory=list)
    vectors: list[list[float]] = field(default_factory=list)

    def to_json(self) -> str:
        d = asdict(self)
        d["edges"] = [list(e) for e in d["edges"]]
        return json.dumps(d, indent=2)


def find_witness(
    G: nx.Graph,
    *,
    restarts: int = 200,
    residual_threshold: float = 1e-10,
    seed: Optional[int] = None,
    max_nfev: int = 4000,
) -> WitnessResult:
    """Run randomized LM least-squares on G until a witness is found or the
    restart budget is exhausted. Returns the best result seen."""
    edges, sign = orient(G)
    m = len(edges)
    n = len(sign)
    rng = np.random.default_rng(seed)
    best_rss = np.inf
    best_max = np.inf
    best_X: Optional[np.ndarray] = None
    converged_at: Optional[int] = None

    for r in range(restarts):
        X0 = _random_unit_vectors(m, rng)
        result = least_squares(
            _residual,
            X0.ravel(),
            args=(sign, m),
            method="lm",
            max_nfev=max_nfev,
            xtol=1e-15,
            ftol=1e-15,
            gtol=1e-15,
        )
        rss = float(np.sum(result.fun ** 2))
        if rss < best_rss:
            best_rss = rss
            best_max = float(np.max(np.abs(result.fun)))
            best_X = result.x.reshape(m, 3)
            if rss < residual_threshold:
                converged_at = r
                break

    assert best_X is not None
    status = "witness" if best_rss < residual_threshold else "unknown"
    return WitnessResult(
        status=status,
        best_residual_squared=best_rss,
        best_max_abs_residual=best_max,
        n_restarts=(converged_at + 1) if converged_at is not None else restarts,
        converged_restart=converged_at,
        n_vertices=n,
        n_edges=m,
        edges=edges,
        vectors=best_X.tolist(),
    )


def rotate_into_pinning_gauge(
    G: nx.Graph, vectors: list[list[float]] | np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    """Rotate ``vectors`` by an SO(3) element so that the three edges
    incident to vertex 0 (under the canonical orientation) carry exactly

        sigma_i * t_i, where t_0 = (1,0,0),
                              t_1 = (-1/2, sqrt(3)/2, 0),
                              t_2 = (-1/2, -sqrt(3)/2, 0).

    Returns ``(rotated_X, R)`` with ``rotated_X[e] = R @ X[e]`` and
    ``R @ R.T == I``, ``det(R) == +1``. Raises ``ValueError`` if the
    incoming vectors at vertex 0 are not a clean 120-degree triple
    (residual ``> 1e-6``).
    """
    edges, sign = orient(G)
    v0 = next(iter(sign))
    terms = sign[v0]
    if len(terms) != 3:
        raise ValueError("rotate_into_pinning_gauge expects a cubic vertex")
    X = np.asarray(vectors, dtype=np.float64)
    u = [int(s) * X[k] for k, s in terms]
    if np.linalg.norm(sum(u)) > 1e-6:
        raise ValueError("vertex-0 triple does not satisfy Kirchhoff at this tolerance")
    sqrt3 = np.sqrt(3.0)
    f0 = u[0]
    f1 = (u[1] - u[2]) / sqrt3
    f2 = np.cross(f0, f1)
    F = np.stack([f0, f1, f2], axis=1)
    R = F.T
    return X @ R.T, R


def verify_witness(
    G: nx.Graph,
    edges: list[tuple],
    vectors: list[list[float]] | np.ndarray,
    *,
    tol: float = 1e-8,
) -> dict:
    """Independent check: are the vectors unit, and do they satisfy
    Kirchhoff at every vertex under the canonical orientation?"""
    canonical_edges, sign = orient(G)
    if [tuple(e) for e in edges] != canonical_edges:
        return {"ok": False, "reason": "edge order does not match canonical orientation"}
    X = np.asarray(vectors, dtype=np.float64)
    if X.shape != (len(canonical_edges), 3):
        return {"ok": False, "reason": f"shape {X.shape}, expected ({len(canonical_edges)}, 3)"}
    norm_err = float(np.max(np.abs(np.linalg.norm(X, axis=1) - 1.0)))
    vertex_err = 0.0
    for terms in sign.values():
        s = np.zeros(3)
        for k, sigma in terms:
            s += sigma * X[k]
        vertex_err = max(vertex_err, float(np.linalg.norm(s)))
    ok = norm_err < tol and vertex_err < tol
    return {
        "ok": ok,
        "max_norm_error": norm_err,
        "max_vertex_residual": vertex_err,
        "tol": tol,
    }
