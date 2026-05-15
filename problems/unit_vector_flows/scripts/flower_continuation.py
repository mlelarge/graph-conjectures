r"""Predictor-corrector continuation of the flower-snark monodromy
fixed point in a continuous deformation parameter.

The monodromy fixed-point equation $M(X_0) := T^n(X_0) - \pi(X_0) = 0$
is $\mathrm{SO}(3)$-equivariant; on the 3-dim conservation surface the
residual $\mathrm{SO}(2)$ rotation about the $S$-axis is the only
gauge freedom. This module **explicitly gauge-fixes** by rotating the
state to put $\hat S = \hat z$ and $B_0$ in the $xz$-plane, leaving a
genuine 2-parameter reduced system $F(x, \theta) = 0$.

For the deformation we use the twist parameter $\theta$:
$$
F(x, \theta) \;:=\; M_\theta(X_0(x)),
\qquad
M_\theta(X_0) := T^n(X_0) - R_\theta\,\pi(X_0),
$$
where $R_\theta \in \mathrm{SO}(3)$ is rotation by $\theta$ about $\hat z$
(the $S$-axis after gauge-fixing). At $\theta = 0$ this is the
standard $J_n$ monodromy and the certified witness is a solution.

Implementation:
  - :func:`gauge_fix_state` — rotate state so $S = (0, 0, |S|)$ and
    $B_0 = (b_x, 0, b_z)$ with $b_x \ge 0$.
  - :func:`reduced_tangent_basis` — 2x9 orthonormal basis of the
    gauge-fixed tangent space at $X_0$ (i.e., the 3-dim conservation
    tangent quotiented by the $\hat z$-rotation gauge).
  - :func:`reduced_jacobian` — 2x2 numerical Jacobian of $F$ w.r.t. $x$.
  - :func:`continuation_in_twist` — predictor-corrector sweep over
    $\theta$, recording branch diagnostics
    (reduced det, smallest singular value, step residual).
"""
from __future__ import annotations

from dataclasses import dataclass, replace
import math

import numpy as np
from scipy import optimize

from flower_monodromy_jacobian import (
    conservation_tangent_basis,
    monodromy_map,
)
from flower_transfer import FlowerState, forward_iterate, transfer_step


# ---------------------------------------------------------------------------
# Gauge fixing
# ---------------------------------------------------------------------------


def _rotation_to_align(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Return $R \\in \\mathrm{SO}(3)$ with $R a = b$ (both unit vectors).

    Uses Rodrigues' formula. If $a, b$ are antiparallel returns a
    180-degree rotation about any perpendicular axis.
    """
    a = a / np.linalg.norm(a)
    b = b / np.linalg.norm(b)
    dot = float(np.clip(a @ b, -1.0, 1.0))
    if dot > 1.0 - 1e-14:
        return np.eye(3)
    if dot < -1.0 + 1e-14:
        # 180-deg rotation about any axis perpendicular to a.
        axes = np.eye(3)
        seed = axes[int(np.argmin(np.abs(a)))]
        axis = seed - (seed @ a) * a
        axis = axis / np.linalg.norm(axis)
        K = np.array(
            [
                [0, -axis[2], axis[1]],
                [axis[2], 0, -axis[0]],
                [-axis[1], axis[0], 0],
            ]
        )
        return np.eye(3) + 2.0 * (K @ K)
    cross = np.cross(a, b)
    s = float(np.linalg.norm(cross))
    K = np.array(
        [
            [0.0, -cross[2], cross[1]],
            [cross[2], 0.0, -cross[0]],
            [-cross[1], cross[0], 0.0],
        ]
    )
    return np.eye(3) + K + (K @ K) * ((1.0 - dot) / (s * s))


def _rotate_state(state: FlowerState, R: np.ndarray) -> FlowerState:
    """Apply a global rotation $R$ to every vector in the state."""
    def rot(M: np.ndarray) -> np.ndarray:
        return M @ R.T

    return FlowerState(
        n=state.n,
        B=rot(state.B),
        Omega_c=rot(state.Omega_c),
        Omega_d=rot(state.Omega_d),
        beta=rot(state.beta),
        gamma=rot(state.gamma),
        delta=rot(state.delta),
        S=R @ state.S,
    )


def gauge_fix_state(state: FlowerState) -> tuple[FlowerState, np.ndarray]:
    """Return a gauge-fixed copy of ``state`` and the applied rotation.

    After the fix:
      - $S = (0, 0, |S|)$ (the conserved sum is along $+\\hat z$);
      - $B_0 = (b_x, 0, b_z)$ with $b_x \\ge 0$ (residual SO(2) about
        $\\hat z$ is pinned).
    """
    # Step 1: rotate S onto +z.
    R1 = _rotation_to_align(state.S, np.array([0.0, 0.0, 1.0]))
    s1 = _rotate_state(state, R1)

    # Step 2: rotate about z so B[0] is in xz-plane with non-negative x.
    b = s1.B[0]
    angle = math.atan2(b[1], b[0])  # angle of (b_x, b_y) in xy-plane
    # Want to rotate by -angle about z so the projection lands on +x.
    c, s_ = math.cos(-angle), math.sin(-angle)
    R2 = np.array(
        [
            [c, -s_, 0.0],
            [s_, c, 0.0],
            [0.0, 0.0, 1.0],
        ]
    )
    s2 = _rotate_state(s1, R2)
    return s2, R2 @ R1


# ---------------------------------------------------------------------------
# Reduced (gauge-fixed) tangent space
# ---------------------------------------------------------------------------


def _gauge_direction(
    X0: tuple[np.ndarray, np.ndarray, np.ndarray]
) -> np.ndarray:
    """The SO(2)-about-$\\hat S$ gauge direction at $X_0$ as a 9-vector."""
    S_axis = X0[0] + X0[1] + X0[2]
    nS = float(np.linalg.norm(S_axis))
    if nS < 1e-12:
        return np.zeros(9)
    omega = S_axis / nS
    return np.concatenate(
        [np.cross(omega, X0[i]) for i in range(3)]
    )


def reduced_tangent_basis(
    X0: tuple[np.ndarray, np.ndarray, np.ndarray]
) -> np.ndarray:
    """Return a 2x9 orthonormal basis of the gauge-fixed tangent space
    at $X_0$ -- i.e., the orthogonal complement (inside the 3-dim
    conservation tangent) of the SO(2)-about-$\\hat S$ gauge direction.
    """
    full = conservation_tangent_basis(X0)  # 3 x 9
    g = _gauge_direction(X0)
    g_norm = float(np.linalg.norm(g))
    if g_norm < 1e-12:
        # Degenerate; return the first two basis rows.
        return full[:2]
    g = g / g_norm
    # Project the 3-dim basis onto the orthogonal complement of g.
    # Express g in the 3-dim basis coords: alpha = full @ g (shape 3).
    alpha = full @ g
    # Build a 3x3 reflector that zeros alpha; use QR to get a basis.
    Q, _ = np.linalg.qr(np.column_stack([alpha, np.eye(3)]))
    # Columns of Q: first is along alpha, last two span complement in coord-space.
    reduced_in_coords = Q[:, 1:].T  # 2 x 3 in coord-space
    reduced_ambient = reduced_in_coords @ full  # 2 x 9
    # Re-orthonormalise in R^9.
    Qa, _ = np.linalg.qr(reduced_ambient.T)
    return Qa.T[:2]


# ---------------------------------------------------------------------------
# Twist-deformed monodromy
# ---------------------------------------------------------------------------


def _rotation_about_z(theta: float) -> np.ndarray:
    c, s = math.cos(theta), math.sin(theta)
    return np.array(
        [
            [c, -s, 0.0],
            [s, c, 0.0],
            [0.0, 0.0, 1.0],
        ]
    )


def reduced_residual(
    local_coords: np.ndarray,
    state: FlowerState,
    *,
    theta: float = 0.0,
    tol: float = 1e-13,
) -> np.ndarray | None:
    """Evaluate $F(x, \\theta) := T^n(X_0(x)) - R_\\theta\\,\\pi(X_0(x))$
    projected onto the reduced (gauge-fixed) tangent basis at the
    state's $X_0$.

    Returns ``None`` if the underlying monodromy iteration fails.
    """
    X0_ref = (state.B[0], state.Omega_c[0], state.Omega_d[0])
    basis = reduced_tangent_basis(X0_ref)  # 2 x 9
    ambient = basis.T @ local_coords  # 9-vector
    B = X0_ref[0] + ambient[0:3]
    Oc = X0_ref[1] + ambient[3:6]
    Od = X0_ref[2] + ambient[6:9]
    X_pert = (
        B / np.linalg.norm(B),
        Oc / np.linalg.norm(Oc),
        Od / np.linalg.norm(Od),
    )
    out = monodromy_map(X_pert, state, tol=tol)
    if not out["ok"]:
        return None
    Xn = out["X_n"]
    # Twist: apply R_theta about z to pi(X_pert) before comparing.
    R = _rotation_about_z(theta)
    Xn_target = (
        R @ X_pert[0],
        R @ X_pert[1],
        R @ X_pert[2],
    )
    diff = np.concatenate(
        [Xn[i] - Xn_target[i] for i in range(3)]
    )
    return basis @ diff


def reduced_jacobian(
    state: FlowerState,
    *,
    local_coords: np.ndarray | None = None,
    theta: float = 0.0,
    eps: float = 1e-7,
    tol: float = 1e-13,
) -> dict:
    """2x2 numerical Jacobian of :func:`reduced_residual` w.r.t. the
    local coordinates, at the requested ``local_coords`` (default origin)
    and ``theta``.

    Returns a dict with ``J`` (2x2), ``f0`` (residual at base point),
    ``singular_values``, ``det``, ``cond`` (sigma_1 / sigma_2)."""
    if local_coords is None:
        local_coords = np.zeros(2)
    f0 = reduced_residual(local_coords, state, theta=theta, tol=tol)
    if f0 is None:
        raise RuntimeError("reduced_residual failed at base point")
    J = np.zeros((2, 2))
    for j in range(2):
        e = np.zeros(2)
        e[j] = eps
        f_plus = reduced_residual(local_coords + e, state, theta=theta, tol=tol)
        f_minus = reduced_residual(local_coords - e, state, theta=theta, tol=tol)
        if f_plus is None or f_minus is None:
            raise RuntimeError(f"Jacobian column {j} failed")
        J[:, j] = (f_plus - f_minus) / (2.0 * eps)
    _, sing, _ = np.linalg.svd(J)
    det = float(np.linalg.det(J))
    cond = float(sing[0] / sing[-1]) if sing[-1] > 0 else float("inf")
    return {
        "J": J,
        "f0": f0,
        "singular_values": sing,
        "det": det,
        "cond": cond,
    }


# ---------------------------------------------------------------------------
# Predictor-corrector continuation
# ---------------------------------------------------------------------------


@dataclass
class BranchPoint:
    theta: float
    x: np.ndarray          # local coords in the *current* reduced tangent
    det_J_reduced: float
    sigma_min: float
    sigma_max: float
    residual_norm: float
    newton_iters: int


def _newton_corrector(
    local_coords: np.ndarray,
    state: FlowerState,
    *,
    theta: float,
    max_iters: int = 20,
    tol: float = 1e-12,
    fd_eps: float = 1e-7,
) -> dict:
    """Newton iteration on $F(x, \\theta) = 0$ in 2 unknowns."""
    x = local_coords.copy()
    last_res = None
    for it in range(max_iters):
        r = reduced_residual(x, state, theta=theta)
        if r is None:
            return {"ok": False, "reason": "residual failed", "x": x, "iters": it}
        last_res = float(np.linalg.norm(r))
        if last_res < tol:
            return {
                "ok": True,
                "x": x,
                "residual": r,
                "residual_norm": last_res,
                "iters": it,
            }
        # Jacobian via FD.
        J = np.zeros((2, 2))
        ok = True
        for j in range(2):
            e = np.zeros(2)
            e[j] = fd_eps
            f_plus = reduced_residual(x + e, state, theta=theta)
            f_minus = reduced_residual(x - e, state, theta=theta)
            if f_plus is None or f_minus is None:
                ok = False
                break
            J[:, j] = (f_plus - f_minus) / (2.0 * fd_eps)
        if not ok:
            return {"ok": False, "reason": "Jacobian failed", "x": x, "iters": it}
        try:
            dx = np.linalg.solve(J, -r)
        except np.linalg.LinAlgError:
            return {"ok": False, "reason": "singular J", "x": x, "iters": it}
        x = x + dx
    return {
        "ok": False,
        "reason": "max iters",
        "x": x,
        "residual_norm": last_res,
        "iters": max_iters,
    }


def continuation_in_twist(
    state: FlowerState,
    *,
    theta_max: float = 2.0 * math.pi,
    n_steps: int = 64,
    fd_eps: float = 1e-7,
    newton_tol: float = 1e-10,
) -> dict:
    """Sweep $\\theta \\in [0, \\theta_{\\max}]$ tracking the
    gauge-fixed monodromy fixed point.

    The state is assumed already gauge-fixed (use :func:`gauge_fix_state`
    first). At each $\\theta$ we Newton-correct the local coordinates
    starting from the previous step's solution; if Newton diverges we
    halve the step size up to a limit.

    Returns a dict with ``branch`` (list of :class:`BranchPoint`),
    ``ok``, and ``fail_at_theta`` if it stopped early.
    """
    dtheta_base = theta_max / n_steps
    theta = 0.0
    x = np.zeros(2)
    branch: list[BranchPoint] = []

    # Initial corrector to confirm we start on the branch.
    init = _newton_corrector(x, state, theta=theta, tol=newton_tol)
    if not init["ok"]:
        return {"ok": False, "branch": branch, "fail_at_theta": 0.0,
                "reason": init.get("reason")}
    x = init["x"]
    jac0 = reduced_jacobian(state, local_coords=x, theta=theta, eps=fd_eps)
    branch.append(
        BranchPoint(
            theta=theta,
            x=x.copy(),
            det_J_reduced=jac0["det"],
            sigma_min=float(jac0["singular_values"][-1]),
            sigma_max=float(jac0["singular_values"][0]),
            residual_norm=init["residual_norm"],
            newton_iters=init["iters"],
        )
    )

    dtheta = dtheta_base
    while theta < theta_max - 1e-12:
        # Step.
        new_theta = min(theta + dtheta, theta_max)
        # Predictor: linear extrapolation in x using J^{-1} ∂F/∂theta.
        Jinfo = reduced_jacobian(state, local_coords=x, theta=theta, eps=fd_eps)
        if Jinfo["singular_values"][-1] < 1e-10:
            return {"ok": False, "branch": branch, "fail_at_theta": theta,
                    "reason": "Jacobian became singular"}
        # ∂F/∂theta via FD.
        f_plus = reduced_residual(x, state, theta=theta + fd_eps)
        f_minus = reduced_residual(x, state, theta=theta - fd_eps)
        if f_plus is None or f_minus is None:
            return {"ok": False, "branch": branch, "fail_at_theta": theta,
                    "reason": "theta-derivative failed"}
        dFdtheta = (f_plus - f_minus) / (2.0 * fd_eps)
        try:
            dx_dtheta = np.linalg.solve(Jinfo["J"], -dFdtheta)
        except np.linalg.LinAlgError:
            return {"ok": False, "branch": branch, "fail_at_theta": theta,
                    "reason": "predictor singular"}
        x_pred = x + dx_dtheta * (new_theta - theta)

        # Corrector.
        corr = _newton_corrector(
            x_pred, state, theta=new_theta, tol=newton_tol, fd_eps=fd_eps
        )
        if not corr["ok"]:
            if dtheta > dtheta_base * 1e-3:
                dtheta *= 0.5
                continue
            return {"ok": False, "branch": branch, "fail_at_theta": new_theta,
                    "reason": corr.get("reason")}

        theta = new_theta
        x = corr["x"]
        Jinfo2 = reduced_jacobian(state, local_coords=x, theta=theta, eps=fd_eps)
        branch.append(
            BranchPoint(
                theta=theta,
                x=x.copy(),
                det_J_reduced=Jinfo2["det"],
                sigma_min=float(Jinfo2["singular_values"][-1]),
                sigma_max=float(Jinfo2["singular_values"][0]),
                residual_norm=corr["residual_norm"],
                newton_iters=corr["iters"],
            )
        )
        # Grow step back toward base if Newton was easy.
        if corr["iters"] <= 3 and dtheta < dtheta_base:
            dtheta = min(dtheta * 1.5, dtheta_base)

    return {"ok": True, "branch": branch}
