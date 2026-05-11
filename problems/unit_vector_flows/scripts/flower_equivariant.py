"""Z/(2n)-equivariant ansatz for S²-flows on flower snarks J_{2k+1}.

Setup. Let n = 2k+1 odd. The Isaacs flower snark J_n has vertex set
{a_i, b_i, c_i, d_i : i in Z/n}. There is a graph automorphism σ of
order 2n acting by

    a_i, b_i  ↦  a_{i+1}, b_{i+1}      (indices mod n)
    c_i       ↦  c_{i+1}  for i < n-1,    c_{n-1} ↦ d_0
    d_i       ↦  d_{i+1}  for i < n-1,    d_{n-1} ↦ c_0

It permutes vertices of like type *except* that σ^n swaps every c with
the corresponding d. Equivalently, σ rotates the long 2n-cycle
c_0 c_1 … c_{n-1} d_0 d_1 … d_{n-1} c_0 by one step, while rotating
the b-cycle by one step (= n on its index).

Equivariant ansatz. Pick a rotation R ∈ SO(3) of order 2n (axis
direction × angle π/n). Pose

    φ(a_i b_i) = R^i u_b,                           i ∈ Z/n
    φ(a_i c_i) = R^i u_c,                           i ∈ {0,…,n-1}
    φ(a_i d_i) = R^{n+i} u_c,                       i ∈ {0,…,n-1}
    φ(b_i b_{i+1}) = R^i w_b,                       i ∈ Z/n
    φ(σ^k(c_0 c_1)) = R^k w_c,                      k ∈ {0,…,2n-1}

so the entire flow is parameterised by (u_b, u_c, w_b, w_c, axis) ∈
(S²)⁵, plus the rotation order 2n is fixed.

Local Kirchhoff (orientation: spokes a→x, cycles in σ-direction):

  a_0 :  u_b + u_c + R^n u_c = 0
  b_0 :  u_b = (I − R^{-1}) w_b
  c_0 :  u_c = (I − R^{-1}) w_c
  (d_0 is the σ^n image of c_0; same equation.)

The orbit-size argument. The b-spoke orbit under <σ> has size n
(since σ^n fixes a_0 and shifts b by n ≡ 0 mod n), forcing
R^n u_b = u_b. Similarly the b-cycle orbit has size n, so R^n w_b = w_b.
Since R^n is a 180° rotation about ``axis``, the only unit vectors it
fixes are ±axis. Hence under this ansatz both ``u_b`` and ``w_b`` are
parallel to the rotation axis.

Consequence (algebraic obstruction). Plug w_b ∝ axis into the b_0
equation: ``(I − R^{-1}) (axis) = axis − axis = 0``, so ``u_b = 0``.
But ``|u_b| = 1``, contradiction. So J_n admits no Z/(2n)-equivariant
S²-flow with rotation R of full order 2n.

What this script does. It encodes the residual of the ansatz numerically
and verifies that no zero exists in the Levenberg–Marquardt sense
across many seeds, for each n in {5, 7, 9, 11, 13}. The minimum residual
is bounded away from zero (consistent with the algebraic obstruction
above). Decreasing R's effective order (e.g., assume only Z/n
equivariance, with R of order n) is the natural next attempt, and is
the focus of `_residual_zn` here.
"""
from __future__ import annotations

import argparse
import json
import time
from dataclasses import dataclass

import numpy as np
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation


def _R_from_axis(axis: np.ndarray, angle: float) -> np.ndarray:
    n = np.linalg.norm(axis)
    if n < 1e-12:
        return np.eye(3)
    return Rotation.from_rotvec((angle / n) * axis).as_matrix()


# ---------------------------------------------------------------------------
# Z/(2n)-equivariant ansatz  (the strong symmetry; expected to fail)
# ---------------------------------------------------------------------------


def residual_z2n(params: np.ndarray, n: int) -> np.ndarray:
    u_b = params[0:3]
    u_c = params[3:6]
    w_b = params[6:9]
    w_c = params[9:12]
    axis = params[12:15]
    angle = np.pi / n  # R has order 2n
    R = _R_from_axis(axis, angle)
    Rn = np.linalg.matrix_power(R, n)
    R_inv = R.T  # R is rotation, so R^{-1} = R^T

    res: list[np.ndarray] = []
    res.extend([
        u_b @ u_b - 1.0,
        u_c @ u_c - 1.0,
        w_b @ w_b - 1.0,
        w_c @ w_c - 1.0,
        axis @ axis - 1.0,
    ])
    res.extend((u_b + u_c + Rn @ u_c).tolist())
    res.extend((u_b - (np.eye(3) - R_inv) @ w_b).tolist())
    res.extend((u_c - (np.eye(3) - R_inv) @ w_c).tolist())
    return np.array(res, dtype=np.float64)


# ---------------------------------------------------------------------------
# Z/n-equivariant ansatz  (weaker; allows independent c-spoke / d-spoke and
# independent c-cycle / d-cycle base vectors, plus the two cross edges)
# ---------------------------------------------------------------------------


def residual_zn(params: np.ndarray, n: int) -> np.ndarray:
    """Z/n-equivariant ansatz on J_n with the two cd-cross edges treated
    as standalone unit vectors (Z/n is *not* a graph automorphism of J_n,
    so the equivariance is only partial).

    Variables (27 reals):
        u_b, u_c, u_d           spoke base vectors (φ(a_i x_i) = R^i u_x)
        w_b, w_c, w_d           cycle base vectors (φ(σ_n(x_0 x_1)) = R^i w_x
                                where σ_n: i ↦ i+1 acts on the n-1 internal
                                c-c and d-d edges; for the b-cycle σ_n acts
                                on all n edges)
        x_cd                    standalone unit vector for c_{n-1} d_0
        x_dc                    standalone unit vector for d_{n-1} c_0
        axis                    rotation axis in R^3

    R is rotation by angle 2π/n about ``axis``.

    Conservation orbits. Under R-equivariance the conservation equation
    at every internal vertex of a given orbit reduces to *one* equation
    in the base vectors:

      a_i (n-orbit, i ∈ Z/n):  u_b + u_c + u_d = 0
      b_i (n-orbit):           u_b = (I − R^{-1}) w_b
      c_i for 1 ≤ i ≤ n-2 (internal):  u_c = (I − R^{-1}) w_c
      d_i for 1 ≤ i ≤ n-2 (internal):  u_d = (I − R^{-1}) w_d

    Boundary vertices (involve a cross edge, not in the orbit):

      c_0:       u_c + x_dc = w_c
      d_0:       u_d + x_cd = w_d
      c_{n-1}:   R^{n-1} u_c + R^{n-2} w_c = x_cd
      d_{n-1}:   R^{n-1} u_d + R^{n-2} w_d = x_dc

    Eight vector equations (24 scalars) plus 9 unit-norms gives 33
    residuals in 27 variables — *over-determined*. A zero of this
    residual is a Z/n-equivariant S^2-flow on J_n; failure to find one
    rules out the symmetry class.
    """
    u_b = params[0:3]
    u_c = params[3:6]
    u_d = params[6:9]
    w_b = params[9:12]
    w_c = params[12:15]
    w_d = params[15:18]
    x_cd = params[18:21]
    x_dc = params[21:24]
    axis = params[24:27]
    angle = 2 * np.pi / n
    R = _R_from_axis(axis, angle)
    R_inv = R.T
    I_minus_Rinv = np.eye(3) - R_inv
    R_n_minus_1 = np.linalg.matrix_power(R, n - 1)
    R_n_minus_2 = np.linalg.matrix_power(R, n - 2)

    res: list[float] = []
    for v in (u_b, u_c, u_d, w_b, w_c, w_d, x_cd, x_dc, axis):
        res.append(v @ v - 1.0)

    # a_0
    res.extend((u_b + u_c + u_d).tolist())
    # b_i orbit (single equation):  u_b = (I - R^{-1}) w_b
    res.extend((u_b - I_minus_Rinv @ w_b).tolist())
    # internal c_i for 1 ≤ i ≤ n-2 (single equation):  u_c = (I - R^{-1}) w_c
    res.extend((u_c - I_minus_Rinv @ w_c).tolist())
    # internal d_i for 1 ≤ i ≤ n-2 (single equation):  u_d = (I - R^{-1}) w_d
    res.extend((u_d - I_minus_Rinv @ w_d).tolist())
    # c_0 boundary
    res.extend((u_c + x_dc - w_c).tolist())
    # d_0 boundary
    res.extend((u_d + x_cd - w_d).tolist())
    # c_{n-1} boundary
    res.extend((R_n_minus_1 @ u_c + R_n_minus_2 @ w_c - x_cd).tolist())
    # d_{n-1} boundary
    res.extend((R_n_minus_1 @ u_d + R_n_minus_2 @ w_d - x_dc).tolist())

    return np.array(res, dtype=np.float64)


# ---------------------------------------------------------------------------
# Search drivers
# ---------------------------------------------------------------------------


@dataclass
class AnsatzResult:
    ansatz: str
    n: int
    best_residual_squared: float
    best_max_abs_residual: float
    n_restarts_used: int
    n_seeds_tried: int
    converged_seed: int | None


def search_ansatz(
    n: int,
    *,
    ansatz: str,
    seeds=(2026, 42, 1, 7, 17, 31337, 99, 1000),
    restarts: int = 50,
    max_nfev: int = 4000,
    residual_threshold: float = 1e-20,
) -> AnsatzResult:
    if ansatz == "z2n":
        residual = residual_z2n
        n_params = 15
    elif ansatz == "zn":
        residual = residual_zn
        n_params = 27
    else:
        raise ValueError(f"unknown ansatz {ansatz!r}")

    best_rss = np.inf
    best_max = np.inf
    converged_seed: int | None = None
    n_seeds_tried = 0
    n_restarts_used = 0

    for seed in seeds:
        n_seeds_tried += 1
        rng = np.random.default_rng(seed)
        for r in range(restarts):
            n_restarts_used += 1
            x0 = rng.standard_normal(n_params)
            for s in range(0, n_params, 3):
                v = x0[s : s + 3]
                norm = np.linalg.norm(v)
                if norm > 1e-12:
                    x0[s : s + 3] = v / norm
            method = "lm"
            try:
                _probe = residual(x0, n)
                if len(_probe) < n_params:
                    method = "trf"  # under-determined system
            except Exception:
                pass
            result = least_squares(
                residual, x0, args=(n,), method=method,
                max_nfev=max_nfev, xtol=1e-15, ftol=1e-15, gtol=1e-15,
            )
            rss = float(np.sum(result.fun ** 2))
            if rss < best_rss:
                best_rss = rss
                best_max = float(np.max(np.abs(result.fun)))
                if rss < residual_threshold:
                    converged_seed = seed
                    return AnsatzResult(
                        ansatz=ansatz, n=n,
                        best_residual_squared=best_rss,
                        best_max_abs_residual=best_max,
                        n_restarts_used=n_restarts_used,
                        n_seeds_tried=n_seeds_tried,
                        converged_seed=converged_seed,
                    )

    return AnsatzResult(
        ansatz=ansatz, n=n,
        best_residual_squared=best_rss,
        best_max_abs_residual=best_max,
        n_restarts_used=n_restarts_used,
        n_seeds_tried=n_seeds_tried,
        converged_seed=converged_seed,
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ansatz", choices=("z2n", "zn", "both"), default="both")
    ap.add_argument("--orders", type=int, nargs="+", default=[5, 7, 9, 11, 13])
    ap.add_argument("--restarts", type=int, default=50)
    args = ap.parse_args()

    targets = (
        [args.ansatz] if args.ansatz != "both" else ["z2n", "zn"]
    )
    rows: list[dict] = []
    for ansatz in targets:
        for n in args.orders:
            t0 = time.time()
            r = search_ansatz(n, ansatz=ansatz, restarts=args.restarts)
            elapsed = time.time() - t0
            line = {
                "ansatz": r.ansatz, "n": r.n,
                "best_rss": r.best_residual_squared,
                "best_max": r.best_max_abs_residual,
                "n_seeds_tried": r.n_seeds_tried,
                "n_restarts_used": r.n_restarts_used,
                "converged_seed": r.converged_seed,
                "elapsed_seconds": elapsed,
            }
            rows.append(line)
            print(json.dumps(line))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
