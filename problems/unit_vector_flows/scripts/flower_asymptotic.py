r"""Asymptotic-limit diagnostics for the flower-snark transfer system.

For an infinite-family theorem $\forall k \ge K, J_{2k+1}$ admits an
$S^2$-flow", a clean route is:

1. Identify a limiting object (an ODE, a fixed configuration, or a
   smooth profile) as $n \to \infty$.
2. Prove existence in the limit.
3. Use the implicit function theorem to lift the limit existence to
   all sufficiently large odd $n$.

This module supplies the **measurement step** — extract profiles from
the certified $J_5, \dots, J_{2K+1}$ witnesses and test whether they
converge to a common limiting structure as $n$ grows. The current
witnesses (from `witness.find_witness`, Levenberg-Marquardt random
seeds) are **not constrained** to lie on a structured branch; finding
a "uniform" family will likely require a constrained search, but the
diagnostics below tell us what to look for.

Diagnostics computed:
  - the conserved sum magnitude $|S|$ as a function of $n$;
  - the Kabsch "best rotation per step" angles and rotation-axis
    distribution (do steps approximate a constant rotation about
    $\hat S$?);
  - the Fourier spectrum $|\hat\beta(\nu)|$ of the spoke sequences
    around the cycle (smooth limit $\Leftrightarrow$ low-frequency
    dominant spectrum);
  - the autocorrelation $\langle \beta_i, \beta_{i+\ell}\rangle$
    (smooth limit $\Leftrightarrow$ slow decay).

Plus a normal-form candidate:
  - :func:`kabsch_rotation` — best $R \in \mathrm{SO}(3)$ taking
    $X_{i-1}$ to $X_i$;
  - :func:`rescale_to_unit_cycle` — re-parameterise the discrete
    trajectory by $\tau = i / n \in [0, 1]$ for cross-$n$ comparison.
"""
from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np

from flower_transfer import FlowerState


@dataclass
class AsymptoticReport:
    n: int
    S_magnitude: float
    step_angles_deg: np.ndarray         # shape (n,) -- per-step Kabsch angle
    step_axes: np.ndarray               # shape (n, 3) -- per-step rotation axis
    step_residuals: np.ndarray          # shape (n,) -- Kabsch residual
    step_axis_z_alignment: float        # mean |axis . z| -- 1 = pure rotation about S
    beta_fft_normalised: np.ndarray     # shape (n,) -- |FFT(beta_i)| / max
    gamma_fft_normalised: np.ndarray    # shape (n,)
    delta_fft_normalised: np.ndarray    # shape (n,)
    beta_dominant_freq: int             # index of the largest non-zero mode
    beta_dominant_freq_normalised: float  # ratio in [0, 1/2] = (dominant / n)
    beta_autocorr: np.ndarray           # shape (n,) -- <beta_i, beta_{i+l}> mean over i


# ---------------------------------------------------------------------------
# Per-step Kabsch rotation
# ---------------------------------------------------------------------------


def kabsch_rotation(X_prev: np.ndarray, X_curr: np.ndarray) -> tuple[np.ndarray, float]:
    """Best $R \\in \\mathrm{SO}(3)$ taking the columns of ``X_prev``
    to the columns of ``X_curr`` in the Frobenius sense.

    Returns ``(R, residual)`` with ``residual = ||R X_prev - X_curr||_F``.
    """
    H = X_curr @ X_prev.T
    U, _, Vh = np.linalg.svd(H)
    d = np.sign(np.linalg.det(U @ Vh))
    D = np.diag([1.0, 1.0, d if d != 0 else 1.0])
    R = U @ D @ Vh
    res = float(np.linalg.norm(R @ X_prev - X_curr))
    return R, res


def rotation_angle_axis(R: np.ndarray) -> tuple[float, np.ndarray]:
    """Extract angle $\\theta$ and axis $\\hat\\omega$ from $R \\in \\mathrm{SO}(3)$.

    Uses the standard $\\mathrm{trace}(R) = 1 + 2\\cos\\theta$ and the
    skew-symmetric part of $R$.
    """
    trace = float(np.trace(R))
    cos_theta = (trace - 1.0) / 2.0
    cos_theta = max(-1.0, min(1.0, cos_theta))
    theta = math.acos(cos_theta)
    if abs(math.sin(theta)) > 1e-10:
        axis = np.array(
            [R[2, 1] - R[1, 2], R[0, 2] - R[2, 0], R[1, 0] - R[0, 1]]
        ) / (2.0 * math.sin(theta))
    else:
        # 0- or pi-rotation: extract axis from R + I (for pi case).
        if cos_theta > 0:
            axis = np.array([0.0, 0.0, 1.0])
        else:
            # 180-deg rotation. R + I has rank 1; the axis is its column.
            M = R + np.eye(3)
            col_norms = np.linalg.norm(M, axis=0)
            axis = M[:, int(np.argmax(col_norms))]
            axis = axis / np.linalg.norm(axis)
    return theta, axis


# ---------------------------------------------------------------------------
# Whole-cycle asymptotic report
# ---------------------------------------------------------------------------


def asymptotic_report(state: FlowerState) -> AsymptoticReport:
    """Compute the full asymptotic-diagnostic battery for one state."""
    n = state.n
    B, Oc, Od = state.B, state.Omega_c, state.Omega_d

    # Step Kabsch rotations
    angles = np.zeros(n)
    axes = np.zeros((n, 3))
    residuals = np.zeros(n)
    for i in range(n):
        prev_i = (i - 1) % n
        Xp = np.column_stack([B[prev_i], Oc[prev_i], Od[prev_i]])
        Xc = np.column_stack([B[i], Oc[i], Od[i]])
        R, res = kabsch_rotation(Xp, Xc)
        theta, axis = rotation_angle_axis(R)
        angles[i] = math.degrees(theta)
        axes[i] = axis
        residuals[i] = res

    # Step axis z-alignment (S-axis after gauge fix)
    axis_z_alignment = float(np.mean(np.abs(axes[:, 2])))

    # FFT of spoke sequences
    def fft_mag_normalised(M: np.ndarray) -> np.ndarray:
        f = np.fft.fft(M, axis=0)
        mags = np.linalg.norm(f, axis=1)
        peak = float(np.max(mags))
        return mags / peak if peak > 0 else mags

    beta_fft = fft_mag_normalised(state.beta)
    gamma_fft = fft_mag_normalised(state.gamma)
    delta_fft = fft_mag_normalised(state.delta)

    # Dominant frequency (ignoring DC = index 0)
    if n > 1:
        nonzero = beta_fft.copy()
        nonzero[0] = 0
        dom_idx = int(np.argmax(nonzero))
        # Wrap to "frequency" in [0, n/2]
        dom_freq = min(dom_idx, n - dom_idx)
    else:
        dom_idx = 0
        dom_freq = 0

    # Autocorrelation of beta around the cycle
    autocorr = np.zeros(n)
    for lag in range(n):
        autocorr[lag] = float(
            np.mean([state.beta[i] @ state.beta[(i + lag) % n] for i in range(n)])
        )

    return AsymptoticReport(
        n=n,
        S_magnitude=float(np.linalg.norm(state.S)),
        step_angles_deg=angles,
        step_axes=axes,
        step_residuals=residuals,
        step_axis_z_alignment=axis_z_alignment,
        beta_fft_normalised=beta_fft,
        gamma_fft_normalised=gamma_fft,
        delta_fft_normalised=delta_fft,
        beta_dominant_freq=dom_freq,
        beta_dominant_freq_normalised=dom_freq / float(n),
        beta_autocorr=autocorr,
    )


# ---------------------------------------------------------------------------
# Cross-family convergence test
# ---------------------------------------------------------------------------


def smooth_limit_diagnostic(reports: dict[int, AsymptoticReport]) -> dict:
    """Score how close the family of reports is to a "smooth limit".

    A smooth limit would manifest as:
      - dominant FFT frequency at small / fixed fraction of $n$
        (not scaling like $n/2$);
      - Kabsch step residuals approaching zero (steps approaching pure
        rotations);
      - rotation-axis z-alignment approaching 1 (pure $\\hat S$-axis
        rotations).

    Returns a dict reporting whether each metric trends toward the
    smooth-limit signature as $n$ grows.
    """
    ns = sorted(reports.keys())
    dom_freqs = [reports[n].beta_dominant_freq_normalised for n in ns]
    mean_resids = [float(np.mean(reports[n].step_residuals)) for n in ns]
    z_aligns = [reports[n].step_axis_z_alignment for n in ns]
    S_mags = [reports[n].S_magnitude for n in ns]

    # Trend: dominant freq going down with n means low-freq dominant
    dom_freq_trend = float(np.polyfit(ns, dom_freqs, 1)[0]) if len(ns) >= 2 else 0.0
    resid_trend = float(np.polyfit(ns, mean_resids, 1)[0]) if len(ns) >= 2 else 0.0
    align_trend = float(np.polyfit(ns, z_aligns, 1)[0]) if len(ns) >= 2 else 0.0
    S_mag_std = float(np.std(S_mags))

    smooth_limit_score = 0.0
    notes: list[str] = []
    # Each "trends-toward-smooth" pattern is worth points; out of 3 max.
    if dom_freq_trend < -0.01:
        smooth_limit_score += 1.0
    else:
        notes.append(
            f"dominant beta-FFT freq does not decrease with n (slope = {dom_freq_trend:+.3e})"
        )
    if resid_trend < -0.01:
        smooth_limit_score += 1.0
    else:
        notes.append(
            f"Kabsch step residual does not decrease with n (slope = {resid_trend:+.3e})"
        )
    if align_trend > 0.01:
        smooth_limit_score += 1.0
    else:
        notes.append(
            f"step axis does not approach $\\hat z$ (z-alignment slope = {align_trend:+.3e})"
        )

    return {
        "ns": ns,
        "S_magnitudes": S_mags,
        "S_magnitude_std": S_mag_std,
        "dominant_freq_normalised": dom_freqs,
        "dominant_freq_trend": dom_freq_trend,
        "mean_step_residual": mean_resids,
        "mean_step_residual_trend": resid_trend,
        "step_axis_z_alignment": z_aligns,
        "step_axis_z_alignment_trend": align_trend,
        "smooth_limit_score": smooth_limit_score,
        "smooth_limit_score_max": 3.0,
        "notes": notes,
    }
