r"""Two-scale Procrustes fit for flower-snark witness trajectories.

[flower_asymptotic.md](../docs/flower_asymptotic.md) showed that LM-random
witnesses for $J_{2k+1}$ have

  - Kabsch step residual *decreasing* with $n$ (joint state aligns
    with a rotation),
  - axis $\hat z$-alignment *increasing* with $n$ (rotations are
    about the conserved-sum axis),

but the spoke Fourier spectrum remains high-frequency dominated. The
simplest reconciliation is a **two-scale model**

$$
X_i \;\approx\; R^i \, Y_{i \bmod p}
$$

where $R \in \mathrm{SO}(3)$ is a slow rotation (encoding the global
alignment) and $Y_0, \ldots, Y_{p-1} \in (S^2)^3$ is a short
fast-oscillation template (encoding the high-frequency content).
We write $X_i$ as the $3 \times 3$ column matrix $[B_i | \Omega^c_i |
\Omega^d_i]$, so the action $R^i Y_k$ is left-multiplication on each
column.

If a stable small $p$ explains the witnesses across the family, the
$S^2$-flow problem reduces to a finite-dimensional ansatz with
$3 + 2p$ degrees of freedom (3 for $R$, 2 per $Y_k$ on the conservation
surface mod gauge) -- a tractable algebraic system, candidate for a
direct flower theorem.

This module provides:
  - :func:`fit_two_scale` -- given a witness and a candidate period $p$,
    estimate $R$ and the template $Y_0, \ldots, Y_{p-1}$ by Procrustes
    averaging and report the RMS residual.
  - :func:`scan_periods` -- run :func:`fit_two_scale` for $p \in
    \{1, 2, 3, 4\}$ and identify the best fit.
  - :func:`candidate_trajectory` -- reconstruct $\hat X_i := R^i Y_{i
    \bmod p}$ from the fitted parameters.
  - :func:`flow_residual_of_candidate` -- evaluate the actual
    $S^2$-flow constraints (unit norms, Kirchhoff at every vertex)
    on a candidate trajectory; returns the maximum violation.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.linalg import expm, logm
from scipy.optimize import minimize

from flower_transfer import FlowerState


# ---------------------------------------------------------------------------
# Two-scale fit
# ---------------------------------------------------------------------------


@dataclass
class TwoScaleFit:
    p: int
    R: np.ndarray              # 3x3, slow rotation
    R_p: np.ndarray            # 3x3, R^p (used to fit R)
    Y_templates: list[np.ndarray]  # length p, each 3x3
    rms_residual: float        # mean ||R^i Y_{i mod p} - X_i|| over i
    per_step_residual: np.ndarray
    rotation_angle_rad: float  # angle of R (in radians)
    rotation_axis: np.ndarray  # unit axis of R


def _project_to_so3(M: np.ndarray) -> np.ndarray:
    """Closest $\\mathrm{SO}(3)$ rotation to $M$ in Frobenius norm."""
    U, _, Vh = np.linalg.svd(M)
    d = np.sign(np.linalg.det(U @ Vh))
    D = np.diag([1.0, 1.0, d if d != 0 else 1.0])
    return U @ D @ Vh


def _matrix_log_skew(R: np.ndarray) -> np.ndarray:
    """Antisymmetric matrix logarithm of $R \\in \\mathrm{SO}(3)$,
    forcing symmetric numerical noise to zero."""
    L = logm(R)
    L = 0.5 * (L - L.T)
    return np.real(L)


def fit_two_scale(state: FlowerState, p: int) -> TwoScaleFit:
    """Fit $X_i \\approx R^i Y_{i \\bmod p}$ on the b/c/d state.

    Algorithm:
      1. Form the state-matrix sequence $X_i = [B_i | \\Omega^c_i |
         \\Omega^d_i] \\in \\mathbb{R}^{3 \\times 3}$ for $i = 0, \\ldots,
         n-1$.
      2. For each pair $(i, i + p)$ inside the cycle, compute the
         Kabsch rotation $R^p_i$ taking $X_i \\to X_{i+p}$.
      3. Take the orthogonal-Procrustes mean: project the arithmetic
         mean onto $\\mathrm{SO}(3)$.
      4. Extract $R$ via $R = \\exp((\\log R^p) / p)$.
      5. Estimate templates $Y_k = $ average of $R^{-i} X_i$ over
         $i$ with $i \\bmod p = k$.
      6. Report the RMS residual of the model on the original data.
    """
    if p < 1:
        raise ValueError("p must be >= 1")
    n = state.n
    if p >= n:
        raise ValueError(f"p={p} too large for n={n}")

    X = [
        np.column_stack([state.B[i], state.Omega_c[i], state.Omega_d[i]])
        for i in range(n)
    ]

    # Step 2 + 3: orthogonal Procrustes mean of Kabsch rotations R_p_i.
    R_p_list: list[np.ndarray] = []
    for i in range(n - p):
        H = X[i + p] @ X[i].T
        R_p_list.append(_project_to_so3(H))
    if not R_p_list:
        raise ValueError(f"too few pairs for p={p}")
    R_p_mean = np.mean(np.stack(R_p_list), axis=0)
    R_p = _project_to_so3(R_p_mean)

    # Step 4: R = R_p^{1/p}.
    L = _matrix_log_skew(R_p)
    R = expm(L / p)
    R = _project_to_so3(R)  # numerical cleanup

    # Step 5: template Y_k averaged over i mod p = k.
    Y_sums: list[np.ndarray] = [np.zeros((3, 3)) for _ in range(p)]
    counts: list[int] = [0] * p
    R_pow_inv = np.eye(3)  # = R^0
    for i in range(n):
        k = i % p
        Y_sums[k] += R_pow_inv @ X[i]
        counts[k] += 1
        # Next R_pow_inv = R^{-1} * current
        R_pow_inv = R.T @ R_pow_inv
    Y_templates = [Y_sums[k] / counts[k] for k in range(p)]

    # Step 6: residual.
    R_pow = np.eye(3)
    per_step = np.zeros(n)
    for i in range(n):
        k = i % p
        X_pred = R_pow @ Y_templates[k]
        per_step[i] = float(np.linalg.norm(X_pred - X[i]))
        R_pow = R @ R_pow
    rms = float(np.sqrt(np.mean(per_step ** 2)))

    # Decompose R: angle + axis.
    L_R = _matrix_log_skew(R)
    angle = float(np.linalg.norm(np.array([L_R[2, 1], L_R[0, 2], L_R[1, 0]])))
    axis = np.array([L_R[2, 1], L_R[0, 2], L_R[1, 0]])
    if angle > 1e-12:
        axis = axis / angle
    else:
        axis = np.array([0.0, 0.0, 1.0])

    return TwoScaleFit(
        p=p,
        R=R,
        R_p=R_p,
        Y_templates=Y_templates,
        rms_residual=rms,
        per_step_residual=per_step,
        rotation_angle_rad=angle,
        rotation_axis=axis,
    )


def _skew_from_vec(w: np.ndarray) -> np.ndarray:
    return np.array(
        [[0.0, -w[2], w[1]], [w[2], 0.0, -w[0]], [-w[1], w[0], 0.0]]
    )


def _R_from_axis_angle_vec(w: np.ndarray) -> np.ndarray:
    return expm(_skew_from_vec(w))


def _residual_given_R(state_matrices: list[np.ndarray], R: np.ndarray, p: int) -> float:
    """For a fixed slow rotation $R$ and period $p$, the optimal
    templates are $Y_k = \\text{mean}_{i \\equiv k} R^{-i} X_i$.
    Return the total squared residual at that optimum."""
    n = len(state_matrices)
    Y_sums = [np.zeros((3, 3)) for _ in range(p)]
    counts = [0] * p
    R_inv = R.T
    R_pow_inv = np.eye(3)
    R_inv_pows = [R_pow_inv]
    for i in range(n - 1):
        R_pow_inv = R_inv @ R_pow_inv
        R_inv_pows.append(R_pow_inv)
    for i in range(n):
        k = i % p
        Y_sums[k] += R_inv_pows[i] @ state_matrices[i]
        counts[k] += 1
    Y_templates = [Y_sums[k] / counts[k] for k in range(p)]
    R_pow = np.eye(3)
    total = 0.0
    for i in range(n):
        k = i % p
        diff = R_pow @ Y_templates[k] - state_matrices[i]
        total += float(np.sum(diff * diff))
        R_pow = R @ R_pow
    return total


def refine_two_scale(state: FlowerState, init_fit: TwoScaleFit) -> TwoScaleFit:
    """Nonlinear refinement: re-optimise the slow rotation $R$ over
    $\\mathfrak{so}(3)$ (3 parameters, axis times angle), keeping the
    templates as the Procrustes-optimal $Y_k(R)$ at each evaluation.
    Returns a refined :class:`TwoScaleFit`.
    """
    n = state.n
    p = init_fit.p
    X = [
        np.column_stack([state.B[i], state.Omega_c[i], state.Omega_d[i]])
        for i in range(n)
    ]
    # Initial parameter: axis * angle as a 3-vector.
    w0 = init_fit.rotation_axis * init_fit.rotation_angle_rad

    def objective(w):
        R_w = _R_from_axis_angle_vec(w)
        return _residual_given_R(X, R_w, p)

    res = minimize(objective, w0, method="Nelder-Mead",
                   options={"xatol": 1e-10, "fatol": 1e-14, "maxiter": 5000})
    w_opt = res.x
    R_opt = _R_from_axis_angle_vec(w_opt)
    R_opt = _project_to_so3(R_opt)

    # Recompute templates + residual at the refined R.
    Y_sums = [np.zeros((3, 3)) for _ in range(p)]
    counts = [0] * p
    R_inv_pows = [np.eye(3)]
    for i in range(n - 1):
        R_inv_pows.append(R_opt.T @ R_inv_pows[-1])
    for i in range(n):
        k = i % p
        Y_sums[k] += R_inv_pows[i] @ X[i]
        counts[k] += 1
    Y_templates = [Y_sums[k] / counts[k] for k in range(p)]
    R_pow = np.eye(3)
    per_step = np.zeros(n)
    for i in range(n):
        k = i % p
        X_pred = R_pow @ Y_templates[k]
        per_step[i] = float(np.linalg.norm(X_pred - X[i]))
        R_pow = R_opt @ R_pow
    rms = float(np.sqrt(np.mean(per_step ** 2)))
    angle = float(np.linalg.norm(w_opt))
    axis = w_opt / angle if angle > 1e-12 else np.array([0.0, 0.0, 1.0])
    R_p_refined = np.linalg.matrix_power(R_opt, p)
    return TwoScaleFit(
        p=p,
        R=R_opt,
        R_p=R_p_refined,
        Y_templates=Y_templates,
        rms_residual=rms,
        per_step_residual=per_step,
        rotation_angle_rad=angle,
        rotation_axis=axis,
    )


def scan_periods(state: FlowerState, max_p: int = 4, refine: bool = True) -> dict[int, TwoScaleFit]:
    """Run :func:`fit_two_scale` for $p = 1, 2, \\ldots, \\min(\\max_p,
    n - 1)$ and return all fits keyed by $p$."""
    n = state.n
    out: dict[int, TwoScaleFit] = {}
    for p in range(1, min(max_p, n - 1) + 1):
        try:
            fit = fit_two_scale(state, p)
            if refine:
                fit = refine_two_scale(state, fit)
            out[p] = fit
        except Exception:
            continue
    return out


# ---------------------------------------------------------------------------
# Candidate witness reconstruction
# ---------------------------------------------------------------------------


def candidate_trajectory(fit: TwoScaleFit, n: int) -> list[np.ndarray]:
    """Return $\\hat X_i = R^i Y_{i \\bmod p}$ as a list of 3-by-3
    matrices, $i = 0, \\ldots, n-1$."""
    out: list[np.ndarray] = []
    R_pow = np.eye(3)
    for i in range(n):
        out.append(R_pow @ fit.Y_templates[i % fit.p])
        R_pow = fit.R @ R_pow
    return out


def flow_residual_of_candidate(
    candidate: list[np.ndarray], state: FlowerState
) -> dict:
    """Measure how close a two-scale candidate trajectory is to a real
    $S^2$-flow.

    Checks:
      - column-unit norms ($B_i, \\Omega^c_i, \\Omega^d_i$ on $S^2$);
      - per-star Kirchhoff: $\\beta_i + \\gamma_i + \\delta_i = 0$
        where $\\beta_i = B_i - B_{(i-1) \\bmod n}$ etc., with c/d
        twist at $i = 0$;
      - per-leaf unit-step (chord constraint $|B_i - B_{i-1}| = 1$
        etc.).
    """
    n = state.n
    Bs = np.array([candidate[i][:, 0] for i in range(n)])
    Ocs = np.array([candidate[i][:, 1] for i in range(n)])
    Ods = np.array([candidate[i][:, 2] for i in range(n)])

    # Unit-norm violations.
    unit_B = float(np.max(np.abs(np.linalg.norm(Bs, axis=1) - 1)))
    unit_Oc = float(np.max(np.abs(np.linalg.norm(Ocs, axis=1) - 1)))
    unit_Od = float(np.max(np.abs(np.linalg.norm(Ods, axis=1) - 1)))

    # Chord constraints |X_i - X_{(i-1) mod n}| = 1 for B (no twist)
    chord_B = float(
        np.max([np.abs(np.linalg.norm(Bs[i] - Bs[(i - 1) % n]) - 1) for i in range(n)])
    )
    # For c/d, the twist applies at i=0: gamma_0 = Omega_c_0 - Omega_d_{n-1}
    chord_c_bulk = float(
        np.max([np.abs(np.linalg.norm(Ocs[i] - Ocs[i - 1]) - 1) for i in range(1, n)])
    )
    chord_c_twist = float(np.abs(np.linalg.norm(Ocs[0] - Ods[n - 1]) - 1))
    chord_d_bulk = float(
        np.max([np.abs(np.linalg.norm(Ods[i] - Ods[i - 1]) - 1) for i in range(1, n)])
    )
    chord_d_twist = float(np.abs(np.linalg.norm(Ods[0] - Ocs[n - 1]) - 1))

    # Kirchhoff at a_i: beta + gamma + delta = 0.
    # beta_i = B_i - B_{(i-1) mod n}
    # gamma_i = Omega_c_i - Omega_c_{i-1} for i>=1; Omega_c_0 - Omega_d_{n-1} for i=0.
    # delta_i = Omega_d_i - Omega_d_{i-1} for i>=1; Omega_d_0 - Omega_c_{n-1} for i=0.
    kirchhoff = 0.0
    for i in range(n):
        b = Bs[i] - Bs[(i - 1) % n]
        if i == 0:
            g = Ocs[0] - Ods[n - 1]
            d = Ods[0] - Ocs[n - 1]
        else:
            g = Ocs[i] - Ocs[i - 1]
            d = Ods[i] - Ods[i - 1]
        kirchhoff = max(kirchhoff, float(np.linalg.norm(b + g + d)))

    max_violation = max(
        unit_B, unit_Oc, unit_Od,
        chord_B, chord_c_bulk, chord_c_twist, chord_d_bulk, chord_d_twist,
        kirchhoff,
    )
    return {
        "unit_norm_B": unit_B,
        "unit_norm_Oc": unit_Oc,
        "unit_norm_Od": unit_Od,
        "chord_B": chord_B,
        "chord_c_bulk": chord_c_bulk,
        "chord_c_twist": chord_c_twist,
        "chord_d_bulk": chord_d_bulk,
        "chord_d_twist": chord_d_twist,
        "kirchhoff_star": kirchhoff,
        "max_violation": max_violation,
    }
