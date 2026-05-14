r"""Flower-snark $S^2$-flow transfer-map / monodromy reduction.

The flower snark $J_{2k+1}$ has a strongly periodic structure: $n = 2k+1$
identical stars $a_i$ with leaves $(b_i, c_i, d_i)$, an inner b-cycle
$b_0 b_1 \dots b_{n-1} b_0$, and an outer 2n-cycle on the c/d leaves
with the twist $c_{n-1} d_0$ and $d_{n-1} c_0$.

This module reduces the $S^2$-flow problem on $J_{2k+1}$ to a periodic
discrete dynamical system by eliminating the spokes via Kirchhoff at
the spoke endpoints.

Notation
--------
Let $\beta_i, \gamma_i, \delta_i \in S^2$ be the spoke values oriented
**out of** $a_i$ (so Kirchhoff at $a_i$: $\beta_i + \gamma_i + \delta_i
= 0$). Let $B_i$ be the value on edge $b_i b_{(i+1) \bmod n}$ oriented
in the increasing-index direction, and let $\Omega_j$ for $j \in
\{0, \dots, 2n-1\}$ be the values on the outer 2n-cycle oriented in
the cycle direction $c_0 \to c_1 \to \dots \to c_{n-1} \to d_0 \to
\dots \to d_{n-1} \to c_0$. Write
$\Omega^c_i := \Omega_i$ and $\Omega^d_i := \Omega_{n+i}$ for the c-half
and d-half respectively.

Kirchhoff at the leaves gives

  $\beta_i = B_i - B_{(i-1) \bmod n}$
  $\gamma_i = \Omega^c_i - \Omega^c_{(i-1) \bmod n}\quad(i \ge 1)$
  $\gamma_0 = \Omega^c_0 - \Omega^d_{n-1}\quad(\text{twist})$
  $\delta_i = \Omega^d_i - \Omega^d_{(i-1) \bmod n}\quad(i \ge 1)$
  $\delta_0 = \Omega^d_0 - \Omega^c_{n-1}\quad(\text{twist})$

Adding the three spoke equations and using $\beta + \gamma + \delta = 0$,
one finds the conservation law

  $S_i := B_i + \Omega^c_i + \Omega^d_i \;=\; \text{constant}$

valid across **all** stars (the twist preserves it). The unit-vector
constraints become chord constraints

  $|B_i - B_{(i-1)}| = |\Omega^c_i - \Omega^c_{(i-1)}|
   = |\Omega^d_i - \Omega^d_{(i-1)}| = 1$.

Transfer / monodromy
--------------------
Define the **state** $X_i := (B_i, \Omega^c_i, \Omega^d_i) \in (S^2)^3$
on the conservation surface $\{(u, v, w) : u + v + w = S\}$. The
**transfer map** $T : X_{i-1} \mapsto X_i$ is implicitly defined by

  $X_i = X_{i-1} + (\beta_i, \gamma_i, \delta_i)$
  with $\beta_i + \gamma_i + \delta_i = 0$, all unit,
  and $X_i \in (S^2)^3$.

Given $X_{i-1}$, the set of valid $X_i$ is generically a **finite**
algebraic variety (4 dofs in $\beta_i, \gamma_i$ minus 4 scalar
constraints).

The cycle closures impose the **monodromy condition**

  $T^n(X_0) \;=\; \pi(X_0)$

where $\pi : (B, \Omega^c, \Omega^d) \mapsto (B, \Omega^d, \Omega^c)$ is
the twist permutation. Iterating once more gives $T^{2n}(X_0) = X_0$.

Whether the flower admits an $S^2$-flow is then equivalent to whether
the multi-valued $T$ admits a $\pi$-twisted $n$-cycle starting at some
admissible $X_0$.

Functions
---------
- :func:`extract_flower_state` — pull the state $(B, \Omega^c, \Omega^d,
  \beta, \gamma, \delta, S)$ from a stored $J_{2k+1}$ witness.
- :func:`verify_state_invariants` — check unit norms, the conservation
  law, and the chord/Kirchhoff equations at machine precision.
- :func:`transfer_step` — given the previous state, the global $S$, and
  a continuous "branch parameter", produce the next state by solving
  the local 4-equation system numerically.
- :func:`forward_iterate` — apply :func:`transfer_step` $n$ times
  starting at $X_0$, returning the trajectory.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import networkx as nx
from scipy import optimize

from graphs import flower_snark_with_labels
from witness import orient


# ---------------------------------------------------------------------------
# State extraction
# ---------------------------------------------------------------------------


@dataclass
class FlowerState:
    n: int
    B: np.ndarray            # shape (n, 3)
    Omega_c: np.ndarray      # shape (n, 3)
    Omega_d: np.ndarray      # shape (n, 3)
    beta: np.ndarray         # shape (n, 3) -- spoke at b_i, out of a_i
    gamma: np.ndarray        # shape (n, 3)
    delta: np.ndarray        # shape (n, 3)
    S: np.ndarray            # shape (3,) -- the conserved sum


def extract_flower_state(
    G: nx.Graph,
    edges: list[tuple],
    vectors: list[list[float]] | np.ndarray,
    k: int,
) -> FlowerState:
    """Extract a :class:`FlowerState` from an $S^2$-flow witness on
    $J_{2k+1}$.

    The graph ``G`` must be exactly :func:`graphs.flower_snark` ``(k)``,
    so vertex labels are: $a_i = i$, $b_i = n + i$, $c_i = 2n + i$,
    $d_i = 3n + i$ for $i \\in \\{0, \\dots, n-1\\}$, where $n = 2k+1$.
    """
    n = 2 * k + 1
    if G.number_of_nodes() != 4 * n:
        raise ValueError(
            f"expected J_{n} with {4*n} vertices; got {G.number_of_nodes()}"
        )
    X = np.asarray(vectors, dtype=np.float64)
    edge_idx = {tuple(e): k_ for k_, e in enumerate(edges)}

    def lookup(u: int, v: int) -> np.ndarray:
        """Return the flow value oriented from u to v."""
        a, b = (u, v) if u < v else (v, u)
        val = X[edge_idx[(a, b)]]
        return val if (a, b) == (u, v) else -val

    beta = np.zeros((n, 3))
    gamma = np.zeros((n, 3))
    delta = np.zeros((n, 3))
    for i in range(n):
        beta[i] = lookup(i, n + i)            # a_i -> b_i
        gamma[i] = lookup(i, 2 * n + i)       # a_i -> c_i
        delta[i] = lookup(i, 3 * n + i)       # a_i -> d_i

    B = np.zeros((n, 3))
    for i in range(n):
        j = (i + 1) % n
        B[i] = lookup(n + i, n + j)           # b_i -> b_{i+1 mod n}

    Omega = np.zeros((2 * n, 3))
    for j in range(2 * n - 1):
        if j < n - 1:
            Omega[j] = lookup(2 * n + j, 2 * n + j + 1)           # c_j -> c_{j+1}
        elif j == n - 1:
            Omega[j] = lookup(3 * n - 1, 3 * n)                   # c_{n-1} -> d_0 (twist)
        else:
            Omega[j] = lookup(2 * n + j, 2 * n + j + 1)           # d_{j-n} -> d_{j-n+1}
    Omega[2 * n - 1] = lookup(4 * n - 1, 2 * n)                   # d_{n-1} -> c_0 (twist)

    Omega_c = Omega[:n].copy()
    Omega_d = Omega[n:].copy()

    S = B[0] + Omega_c[0] + Omega_d[0]

    return FlowerState(
        n=n, B=B, Omega_c=Omega_c, Omega_d=Omega_d,
        beta=beta, gamma=gamma, delta=delta, S=S,
    )


# ---------------------------------------------------------------------------
# Invariant verification
# ---------------------------------------------------------------------------


def verify_state_invariants(state: FlowerState, *, tol: float = 1e-9) -> dict:
    """Check the structural invariants of a :class:`FlowerState`.

    Returns a dict with key residuals; raises ``AssertionError`` on any
    overshoot. Useful for asserting a freshly extracted state really
    satisfies the algebraic theory.
    """
    n = state.n
    B, Oc, Od = state.B, state.Omega_c, state.Omega_d
    beta, gamma, delta = state.beta, state.gamma, state.delta
    S = state.S

    # 1. Unit norms.
    norms = {
        "B": float(np.max(np.abs(np.linalg.norm(B, axis=1) - 1))),
        "Omega_c": float(np.max(np.abs(np.linalg.norm(Oc, axis=1) - 1))),
        "Omega_d": float(np.max(np.abs(np.linalg.norm(Od, axis=1) - 1))),
        "beta": float(np.max(np.abs(np.linalg.norm(beta, axis=1) - 1))),
        "gamma": float(np.max(np.abs(np.linalg.norm(gamma, axis=1) - 1))),
        "delta": float(np.max(np.abs(np.linalg.norm(delta, axis=1) - 1))),
    }

    # 2. Kirchhoff at a_i: beta + gamma + delta = 0.
    kirchhoff_a = float(np.max(np.linalg.norm(beta + gamma + delta, axis=1)))

    # 3. Spoke from b-cycle: beta_i = B_i - B_{i-1}
    b_kirchhoff = float(
        max(np.linalg.norm(beta[i] - (B[i] - B[(i - 1) % n])) for i in range(n))
    )

    # 4. Spoke from outer cycle (c-side):
    #    gamma_i = Omega_c_i - Omega_c_{i-1} for i >= 1
    #    gamma_0 = Omega_c_0 - Omega_d_{n-1}  (twist)
    c_kirchhoff = float(
        max(
            np.linalg.norm(gamma[i] - (Oc[i] - Oc[i - 1]))
            for i in range(1, n)
        )
    )
    c_kirchhoff_twist = float(
        np.linalg.norm(gamma[0] - (Oc[0] - Od[n - 1]))
    )

    # 5. Spoke from outer cycle (d-side):
    #    delta_i = Omega_d_i - Omega_d_{i-1} for i >= 1
    #    delta_0 = Omega_d_0 - Omega_c_{n-1}  (twist)
    d_kirchhoff = float(
        max(
            np.linalg.norm(delta[i] - (Od[i] - Od[i - 1]))
            for i in range(1, n)
        )
    )
    d_kirchhoff_twist = float(
        np.linalg.norm(delta[0] - (Od[0] - Oc[n - 1]))
    )

    # 6. Conservation: S_i = B_i + Omega_c_i + Omega_d_i = S.
    conservation = float(
        max(np.linalg.norm(B[i] + Oc[i] + Od[i] - S) for i in range(n))
    )

    out = {
        "unit_norm_residuals": norms,
        "kirchhoff_a_residual": kirchhoff_a,
        "b_cycle_kirchhoff_residual": b_kirchhoff,
        "c_cycle_kirchhoff_residual": c_kirchhoff,
        "c_cycle_kirchhoff_twist_residual": c_kirchhoff_twist,
        "d_cycle_kirchhoff_residual": d_kirchhoff,
        "d_cycle_kirchhoff_twist_residual": d_kirchhoff_twist,
        "conservation_residual": conservation,
    }
    max_residual = max(
        max(norms.values()),
        kirchhoff_a, b_kirchhoff,
        c_kirchhoff, c_kirchhoff_twist,
        d_kirchhoff, d_kirchhoff_twist,
        conservation,
    )
    out["max_residual"] = float(max_residual)
    out["ok"] = bool(max_residual < tol)
    return out


# ---------------------------------------------------------------------------
# Transfer map: given (X_{i-1}, S) and the spoke triple, advance to X_i
# ---------------------------------------------------------------------------


def apply_step(
    X_prev: tuple[np.ndarray, np.ndarray, np.ndarray],
    spoke: tuple[np.ndarray, np.ndarray, np.ndarray],
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Advance one state via $(\\beta, \\gamma, \\delta)$.

    Used to reconstruct the trajectory from the stored spoke sequence.
    """
    B_prev, Oc_prev, Od_prev = X_prev
    beta_i, gamma_i, delta_i = spoke
    return B_prev + beta_i, Oc_prev + gamma_i, Od_prev + delta_i


def _frame_perp(u: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Orthonormal basis $(e_1, e_2)$ of the plane perpendicular to $u$.

    Constructed deterministically: pick the world axis least aligned
    with $u$ to seed the first basis vector.
    """
    u = u / np.linalg.norm(u)
    axes = np.eye(3)
    seed_idx = int(np.argmin(np.abs(u)))
    seed = axes[seed_idx]
    e1 = seed - (seed @ u) * u
    e1 = e1 / np.linalg.norm(e1)
    e2 = np.cross(u, e1)
    return e1, e2


def _spoke_on_circle(u_prev: np.ndarray, phi: float) -> np.ndarray:
    """Return the unit vector at angle $2\\pi/3$ from $u_{prev}$ in the
    plane parameterized by ``phi``: the circle of valid "next-step"
    spoke vectors emerging from $u_{prev}$."""
    e1, e2 = _frame_perp(u_prev)
    return -0.5 * u_prev + (np.sqrt(3) / 2.0) * (np.cos(phi) * e1 + np.sin(phi) * e2)


def transfer_step(
    X_prev: tuple[np.ndarray, np.ndarray, np.ndarray],
    S: np.ndarray,
    *,
    seed_angles: tuple[float, float] | None = None,
    seed_spokes: tuple[np.ndarray, np.ndarray] | None = None,
    tol: float = 1e-12,
) -> dict:
    """Solve the local 2D system for $(\\beta_i, \\gamma_i)$ that
    advances the state by one step.

    Given $X_{prev} = (B_{prev}, \\Omega^c_{prev}, \\Omega^d_{prev})$
    on the conservation surface $\\{u + v + w = S\\}$, the next-state
    spokes $(\\beta, \\gamma, \\delta)$ satisfy

      - $\\beta \\in $ circle perpendicular to $B_{prev}$ at polar
        angle $2\\pi/3$ (one parameter $\\phi$);
      - $\\gamma \\in $ analogous circle around $\\Omega^c_{prev}$ (one
        parameter $\\psi$);
      - $\\delta = -\\beta - \\gamma$;
      - constraint $F_1$: $\\langle \\beta, \\gamma \\rangle = -1/2$
        (so $\\delta$ is unit);
      - constraint $F_2$: $\\langle \\beta + \\gamma, \\Omega^d_{prev}
        \\rangle = 1/2$ (so $\\delta$ at $2\\pi/3$ from $\\Omega^d_{prev}$,
        i.e., $|\\Omega^d_{prev} + \\delta| = 1$).

    Returns a dict with keys ``ok``, ``X_next``, ``spoke``, ``angles``,
    ``residual``.

    Seeding: pass ``seed_angles=(phi, psi)`` directly, or pass
    ``seed_spokes=(beta, gamma)`` and we extract the angles from them.
    If neither is provided, seed at $(0, 0)$ in the local frame --
    rarely converges to the physical branch from cold start, so prefer
    seeding from a witness step.
    """
    B_prev, Oc_prev, Od_prev = (np.asarray(u, dtype=np.float64) for u in X_prev)

    e1B, e2B = _frame_perp(B_prev)
    e1C, e2C = _frame_perp(Oc_prev)

    if seed_angles is not None:
        phi0, psi0 = seed_angles
    elif seed_spokes is not None:
        beta_seed, gamma_seed = (np.asarray(u, dtype=np.float64) for u in seed_spokes)
        # Project onto local frames to recover angles.
        bx = (beta_seed + 0.5 * B_prev) / (np.sqrt(3) / 2.0)
        gx = (gamma_seed + 0.5 * Oc_prev) / (np.sqrt(3) / 2.0)
        phi0 = float(np.arctan2(bx @ e2B, bx @ e1B))
        psi0 = float(np.arctan2(gx @ e2C, gx @ e1C))
    else:
        phi0, psi0 = 0.0, 0.0

    def residuals(angles: np.ndarray) -> np.ndarray:
        phi, psi = float(angles[0]), float(angles[1])
        beta = _spoke_on_circle(B_prev, phi)
        gamma = _spoke_on_circle(Oc_prev, psi)
        F1 = beta @ gamma + 0.5
        F2 = (beta + gamma) @ Od_prev - 0.5
        return np.array([F1, F2])

    sol = optimize.root(residuals, x0=np.array([phi0, psi0]), method="hybr", tol=tol)
    if not sol.success:
        return {
            "ok": False,
            "reason": sol.message,
            "angles": (float(sol.x[0]), float(sol.x[1])),
            "residual": float(np.linalg.norm(sol.fun)),
        }
    phi, psi = float(sol.x[0]), float(sol.x[1])
    beta = _spoke_on_circle(B_prev, phi)
    gamma = _spoke_on_circle(Oc_prev, psi)
    delta = -beta - gamma
    X_next = (B_prev + beta, Oc_prev + gamma, Od_prev + delta)
    return {
        "ok": True,
        "X_next": X_next,
        "spoke": (beta, gamma, delta),
        "angles": (phi, psi),
        "residual": float(np.linalg.norm(sol.fun)),
    }


def forward_iterate(
    X0: tuple[np.ndarray, np.ndarray, np.ndarray],
    S: np.ndarray,
    seed_state: FlowerState | None = None,
    *,
    n: int | None = None,
    tol: float = 1e-12,
) -> dict:
    """Iterate :func:`transfer_step` ``n`` times from ``X0``.

    If ``seed_state`` is supplied, each step is seeded by the
    corresponding $(\\beta_i, \\gamma_i)$ in the stored state -- this
    follows the physical branch and is the right tool to *reproduce*
    a known witness trajectory.

    Returns a dict with the trajectory ``X``, the recovered spoke
    sequence, and the max step residual.
    """
    if n is None:
        if seed_state is None:
            raise ValueError("supply either n or seed_state")
        n = seed_state.n

    X = [X0]
    spokes: list[tuple] = []
    max_res = 0.0
    for i in range(1, n):
        if seed_state is not None:
            seed_spokes = (seed_state.beta[i], seed_state.gamma[i])
        else:
            seed_spokes = None
        out = transfer_step(X[-1], S, seed_spokes=seed_spokes, tol=tol)
        if not out["ok"]:
            return {"ok": False, "reason": out["reason"], "X": X, "step": i}
        X.append(out["X_next"])
        spokes.append(out["spoke"])
        max_res = max(max_res, out["residual"])
    return {
        "ok": True,
        "X": X,
        "spokes": spokes,
        "max_residual": max_res,
    }


def monodromy_closure(state: FlowerState, *, tol: float = 1e-12) -> dict:
    """Check the monodromy condition $T^n(X_0) = \\pi(X_0)$ on a stored
    witness.

    Uses :func:`forward_iterate` seeded by the witness spoke sequence
    to follow the physical branch all the way to $i = n$. The final
    state is then compared to $\\pi(X_0) = (B_0, \\Omega^d_0, \\Omega^c_0)$.

    The closing step $i = n$ also has an explicit form because it is
    the "$i = 0$" star (with the twist): $X_n$ comes from $X_{n-1}$ by
    adding $(\\beta_0, \\gamma_0, \\delta_0)$ from the witness, and the
    result must equal $\\pi(X_0)$.
    """
    n = state.n
    X0 = (state.B[0].copy(), state.Omega_c[0].copy(), state.Omega_d[0].copy())
    fwd = forward_iterate(X0, state.S, seed_state=state, n=n, tol=tol)
    if not fwd["ok"]:
        return {"ok": False, "reason": fwd["reason"]}
    X_last = fwd["X"][-1]  # at index n - 1

    # Closing step: i = 0 spoke with the twist.
    # Predicted closing applies (beta_0, gamma_0, delta_0). Since the
    # outer cycle's twist swaps c <-> d at the wrap, the closing reads:
    #   B_n          = B_{n-1} + beta_0     should equal B_0
    #   Omega_c_n    = Omega_d_{n-1} + gamma_0  should equal Omega_c_0
    #   Omega_d_n    = Omega_c_{n-1} + delta_0  should equal Omega_d_0
    B_close = X_last[0] + state.beta[0]
    Oc_close = X_last[2] + state.gamma[0]   # X_last[2] = Omega_d_{n-1}; the twist
    Od_close = X_last[1] + state.delta[0]   # X_last[1] = Omega_c_{n-1}; the twist

    err_B = float(np.linalg.norm(B_close - state.B[0]))
    err_C = float(np.linalg.norm(Oc_close - state.Omega_c[0]))
    err_D = float(np.linalg.norm(Od_close - state.Omega_d[0]))
    return {
        "ok": max(err_B, err_C, err_D) < 1e-9,
        "err_B": err_B,
        "err_Omega_c": err_C,
        "err_Omega_d": err_D,
        "max_step_residual": fwd["max_residual"],
    }


def reconstruct_state(state: FlowerState) -> dict:
    """Re-derive $(B_i, \\Omega^c_i, \\Omega^d_i)$ from $X_0$ and the
    stored spoke sequence; compare to the extracted values.

    Returns the maximum reconstruction error. Should be at machine
    precision if the extraction is consistent.
    """
    n = state.n
    X = (state.B[0].copy(), state.Omega_c[0].copy(), state.Omega_d[0].copy())
    err = 0.0
    for i in range(1, n):
        X = apply_step(X, (state.beta[i], state.gamma[i], state.delta[i]))
        err = max(
            err,
            float(np.linalg.norm(X[0] - state.B[i])),
            float(np.linalg.norm(X[1] - state.Omega_c[i])),
            float(np.linalg.norm(X[2] - state.Omega_d[i])),
        )
    # Close the loop with the i=0 step (twist applies for the outer):
    # B_n = B_{n-1} + beta_0 should equal B_0.
    # Omega_c_n via the twist arrives at Omega_d_0:
    # Omega_d_{n-1} + gamma_0 = Omega_c_0 (the twist), and
    # Omega_c_{n-1} + delta_0 = Omega_d_0 (the twist).
    B_close = state.B[n - 1] + state.beta[0]
    Oc_close = state.Omega_d[n - 1] + state.gamma[0]
    Od_close = state.Omega_c[n - 1] + state.delta[0]
    closure_err = max(
        float(np.linalg.norm(B_close - state.B[0])),
        float(np.linalg.norm(Oc_close - state.Omega_c[0])),
        float(np.linalg.norm(Od_close - state.Omega_d[0])),
    )
    return {
        "reconstruction_error": err,
        "closure_error": closure_err,
        "ok": err < 1e-9 and closure_err < 1e-9,
    }
