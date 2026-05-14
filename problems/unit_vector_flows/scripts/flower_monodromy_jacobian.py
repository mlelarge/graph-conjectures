r"""Transversality / Jacobian analysis of the flower-snark monodromy.

Given a stored $S^2$-flow witness on $J_{2k+1}$ and the extracted
:class:`FlowerState`, this module computes the numerical Jacobian of
the monodromy map

  $M(X_0) \;:=\; T^n(X_0) - \pi(X_0)$

at the certified fixed point $X_0$.

The map $M$ takes the 3-dimensional conservation surface
$\{X = (B, \Omega^c, \Omega^d) : B + \Omega^c + \Omega^d = S\}$ to
itself (in fact to a tangent subspace of $\mathbb{R}^9$).
$M(X_0) = 0$ is the monodromy equation; the witness is by construction
a solution. Transversality says

  $\det J \;\neq\; 0$ where $J = \partial M / \partial X_0$

evaluated in tangent coordinates at $X_0$. A transverse fixed point is
locally isolated and *persists* under perturbation of any parameter
(the twist angle, the conserved sum $S$, ...), making numerical
continuation viable.

Implementation: compute $J$ by finite differences in 3 tangent
directions, after parameterising the conservation surface by an
orthonormal basis built from local frames on each $S^2$ factor.

Each perturbation re-runs :func:`forward_iterate` followed by the
twisted closing step :func:`closing_transfer_step`, all seeded from
the witness's $\phi_i, \psi_i$ angles so the Newton solver follows the
*same algebraic branch* as the original trajectory.
"""
from __future__ import annotations

import numpy as np

from flower_transfer import (
    FlowerState,
    _frame_perp,
    forward_iterate,
    transfer_step,
)


# ---------------------------------------------------------------------------
# Tangent basis on the conservation surface
# ---------------------------------------------------------------------------


def conservation_tangent_basis(
    X0: tuple[np.ndarray, np.ndarray, np.ndarray]
) -> np.ndarray:
    """Return a 3-by-9 matrix whose rows are an orthonormal basis of the
    tangent space to the conservation surface $\\{B + \\Omega^c + \\Omega^d
    = S\\} \\cap (S^2)^3$ at ``X0``.

    The tangent space at $X_0 = (B, \\Omega^c, \\Omega^d)$ is

      $\\{(\\dot B, \\dot \\Omega^c, \\dot \\Omega^d) :
        \\dot B \\perp B, \\dot \\Omega^c \\perp \\Omega^c,
        \\dot \\Omega^d \\perp \\Omega^d,
        \\dot B + \\dot \\Omega^c + \\dot \\Omega^d = 0\\}$,

    which has dimension $2 + 2 + 2 - 3 = 3$ (generically). Build by
    listing 6 sphere-tangent generators and taking the null space of
    the 3-by-6 conservation matrix.
    """
    B, Oc, Od = X0
    e1B, e2B = _frame_perp(B)
    e1C, e2C = _frame_perp(Oc)
    e1D, e2D = _frame_perp(Od)

    # In 6-dim coordinates (a1, a2, b1, b2, c1, c2), the tangent vector
    # in R^9 is (a1*e1B + a2*e2B, b1*e1C + b2*e2C, c1*e1D + c2*e2D).
    # Sum-zero constraint: a1*e1B + a2*e2B + b1*e1C + b2*e2C + c1*e1D + c2*e2D = 0.
    # That is the 3-by-6 matrix M = [e1B e2B e1C e2C e1D e2D]; its null
    # space (3-dim) is the tangent.
    M = np.column_stack([e1B, e2B, e1C, e2C, e1D, e2D])  # 3 x 6

    _, sing, Vh = np.linalg.svd(M, full_matrices=True)
    # Smallest singular values' right singular vectors form the null
    # space basis. SVD has 6 right vectors; take the last 3 (matching
    # zero singular values).
    null_basis = Vh[-3:]  # 3 x 6, each row is (a1, a2, b1, b2, c1, c2)

    # Lift to R^9 tangent vectors and orthonormalise.
    basis = np.zeros((3, 9))
    for i in range(3):
        a1, a2, b1, b2, c1, c2 = null_basis[i]
        dB = a1 * e1B + a2 * e2B
        dC = b1 * e1C + b2 * e2C
        dD = c1 * e1D + c2 * e2D
        basis[i] = np.concatenate([dB, dC, dD])

    # Re-orthonormalise (the basis is theoretically orthonormal in the
    # 6-dim null-space coords but not in R^9).
    Q, _ = np.linalg.qr(basis.T)
    return Q.T  # 3 x 9


# ---------------------------------------------------------------------------
# Closing step (twisted transfer)
# ---------------------------------------------------------------------------


def closing_transfer_step(
    X_prev: tuple[np.ndarray, np.ndarray, np.ndarray],
    S: np.ndarray,
    *,
    seed_spokes: tuple[np.ndarray, np.ndarray] | None = None,
    tol: float = 1e-13,
) -> dict:
    """Apply the twisted closing transfer step at star $a_0$.

    Maps $X_{n-1} = (B_{n-1}, \\Omega^c_{n-1}, \\Omega^d_{n-1})$ to
    the predicted $X_n = (B_0, \\Omega^c_0, \\Omega^d_0)$ via the spoke
    triple $(\\beta_0, \\gamma_0, \\delta_0)$ where the c/d roles are
    swapped due to the twist.

    Concretely: this is :func:`transfer_step` applied to
    $(B_{n-1}, \\Omega^d_{n-1}, \\Omega^c_{n-1}) = \\pi(X_{n-1})$.
    """
    B, Oc, Od = X_prev
    return transfer_step((B, Od, Oc), S, seed_spokes=seed_spokes, tol=tol)


def monodromy_map(
    X0: tuple[np.ndarray, np.ndarray, np.ndarray],
    state: FlowerState,
    *,
    tol: float = 1e-13,
) -> dict:
    """Apply $T^n$ starting at $X_0$, seeded by the witness's spoke
    angles so the algebraic branch is the same as the certified
    trajectory.

    Returns a dict with keys ``ok``, ``X_n`` (the predicted next-state
    = $T^n(X_0)$, expected to equal $X_0$ if the monodromy holds), and
    ``max_step_residual``.
    """
    n = state.n
    S = sum(X0)  # use the actual conserved sum at X0 (handles perturbations)
    fwd = forward_iterate(X0, S, seed_state=state, n=n, tol=tol)
    if not fwd["ok"]:
        return {"ok": False, "reason": fwd["reason"]}
    X_last = fwd["X"][-1]
    out = closing_transfer_step(
        X_last,
        S,
        seed_spokes=(state.beta[0], state.gamma[0]),
        tol=tol,
    )
    if not out["ok"]:
        return {"ok": False, "reason": out.get("reason", "closing failed")}
    return {
        "ok": True,
        "X_n": out["X_next"],
        "max_step_residual": max(fwd["max_residual"], out["residual"]),
    }


def monodromy_residual(
    X0: tuple[np.ndarray, np.ndarray, np.ndarray],
    state: FlowerState,
    *,
    tol: float = 1e-13,
) -> np.ndarray | None:
    """Return $T^n(X_0) - X_0 \\in \\mathbb{R}^9$ (with the c/d-swap
    convention: $T^n$ is computed via :func:`monodromy_map` which already
    untwists the closing). $X_0$ is a witness fixed point iff this is
    zero."""
    out = monodromy_map(X0, state, tol=tol)
    if not out["ok"]:
        return None
    X_n = out["X_n"]
    return np.concatenate([X_n[i] - X0[i] for i in range(3)])


# ---------------------------------------------------------------------------
# Numerical Jacobian
# ---------------------------------------------------------------------------


def _normalise_state(
    X: tuple[np.ndarray, np.ndarray, np.ndarray]
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Project each component back onto $S^2$ via normalisation."""
    return tuple(u / np.linalg.norm(u) for u in X)


def monodromy_jacobian(
    state: FlowerState,
    *,
    eps: float = 1e-7,
    tol: float = 1e-13,
    rank_threshold: float = 1e-4,
) -> dict:
    """Compute the 3-by-3 numerical Jacobian of $M(X_0) = T^n(X_0) - X_0$
    in tangent-space coordinates at the witness fixed point.

    Tangent perturbation of size ``eps`` in each of the 3 basis directions;
    re-normalise each $S^2$ factor; re-run :func:`monodromy_map`; project
    the 9-dim ambient residual back onto the tangent basis at $X_0$.

    The conservation surface carries an $\\mathrm{SO}(3)$ gauge: global
    rotation around the axis of $S$ leaves the monodromy invariant.
    Hence the Jacobian has rank at most $3 - 1 = 2$ generically; a fixed
    point is *transverse modulo gauge* iff the two non-trivial singular
    values are bounded away from zero.

    Returns a dict with:
      - ``J``: the 3-by-3 Jacobian.
      - ``f0``: $M(X_0)$ in tangent coordinates (should be $\\approx 0$).
      - ``singular_values``: SVD spectrum of $J$.
      - ``det``: $\\det J$.
      - ``rank``: numerical rank using ``rank_threshold`` relative to the
        largest singular value.
      - ``transverse_modulo_gauge``: bool, ``rank >= 2``.
      - ``gauge_null_residual``: $\\sigma_3 / \\sigma_1$ -- how close
        to the expected gauge-null direction.
      - ``basis``: the 3-by-9 tangent basis.
    """
    X0 = (state.B[0].copy(), state.Omega_c[0].copy(), state.Omega_d[0].copy())
    basis = conservation_tangent_basis(X0)  # 3 x 9

    def eval_M(local_coords: np.ndarray) -> np.ndarray | None:
        """Evaluate M(X) in 3-dim tangent-projected coordinates.

        ``local_coords`` is a 3-vector in the tangent basis at X0; lift
        to a 9-vector, add to X0, renormalise to (S^2)^3, evaluate M,
        and project the 9-vector residual back to the tangent basis at
        X0.
        """
        ambient = basis.T @ local_coords  # 9-vector
        B_pert = X0[0] + ambient[0:3]
        Oc_pert = X0[1] + ambient[3:6]
        Od_pert = X0[2] + ambient[6:9]
        X_pert = _normalise_state((B_pert, Oc_pert, Od_pert))
        res = monodromy_residual(X_pert, state, tol=tol)
        if res is None:
            return None
        return basis @ res  # 3-vector

    f0 = eval_M(np.zeros(3))
    if f0 is None:
        raise RuntimeError("monodromy_residual failed at X0")

    J = np.zeros((3, 3))
    for j in range(3):
        e_j = np.zeros(3)
        e_j[j] = eps
        f_plus = eval_M(e_j)
        f_minus = eval_M(-e_j)
        if f_plus is None or f_minus is None:
            raise RuntimeError(f"perturbation along direction {j} failed")
        J[:, j] = (f_plus - f_minus) / (2.0 * eps)

    # Predicted gauge direction: at X0, the infinitesimal rotation about
    # the S-axis maps X to omega x X componentwise. Within the
    # conservation surface this is a tangent vector. Verify it lies in
    # ker(J) (an *analytic* check, independent of the numerical SVD).
    S_axis = (X0[0] + X0[1] + X0[2])  # = state.S, the conserved sum
    n_S = float(np.linalg.norm(S_axis))
    if n_S > 1e-12:
        omega = S_axis / n_S
        gauge_dB = np.cross(omega, X0[0])
        gauge_dC = np.cross(omega, X0[1])
        gauge_dD = np.cross(omega, X0[2])
        gauge_ambient = np.concatenate([gauge_dB, gauge_dC, gauge_dD])
        gauge_norm = float(np.linalg.norm(gauge_ambient))
        if gauge_norm > 1e-12:
            gauge_local = basis @ gauge_ambient
            gauge_local = gauge_local / np.linalg.norm(gauge_local)
            # J @ gauge should be ~0
            J_times_gauge = J @ gauge_local
            gauge_kernel_residual = float(np.linalg.norm(J_times_gauge))
        else:
            gauge_kernel_residual = float("nan")
    else:
        gauge_kernel_residual = float("nan")

    U, sing, Vh = np.linalg.svd(J)
    det = float(np.linalg.det(J))
    rank = int(np.sum(sing > rank_threshold * sing[0])) if sing[0] > 0 else 0
    transverse_modulo_gauge = bool(rank >= 2)
    gauge_null_residual = float(sing[-1] / sing[0]) if sing[0] > 0 else float("inf")
    return {
        "J": J,
        "f0": f0,
        "singular_values": sing,
        "det": det,
        "rank": rank,
        "transverse_modulo_gauge": transverse_modulo_gauge,
        "gauge_null_residual": gauge_null_residual,
        "gauge_kernel_residual": gauge_kernel_residual,
        "basis": basis,
        "U": U,
        "Vh": Vh,
    }
