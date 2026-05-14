# Flower-snark monodromy — transfer map and transversality

The CDC/gadget routes to a flower-snark $S^2$-flow theorem all run
into hard structural walls:

- The weighted-CDC ansatz on a parametric flower CDC fails by a parity
  argument ([flower_snarks_cdc.md](flower_snarks_cdc.md)).
- The 3-edge-cut dot product cannot reach the flower family
  ([no_flower_dot_decomposition.md](no_flower_dot_decomposition.md)).
- The 4-edge-cut splice cannot either: empirically
  $J_5, J_7, J_9, J_{11}$ are cyclically $\ge 5$-edge-connected
  ([splice4.md](splice4.md)).

This file documents the next route: a **direct
monodromy reduction** of the $S^2$-flow problem on $J_{2k+1}$,
using the flower's own periodic structure.

## The reduction

Recall $J_n$ ($n = 2k+1$) consists of $n$ stars $a_i$ with leaves
$(b_i, c_i, d_i)$, the inner b-cycle $b_0 b_1 \dots b_{n-1} b_0$, and
the twisted outer 2n-cycle
$c_0 c_1 \dots c_{n-1} d_0 d_1 \dots d_{n-1} c_0$.

Let $\beta_i, \gamma_i, \delta_i \in S^2$ be the spoke values oriented
out of $a_i$. Kirchhoff at $a_i$ gives $\beta_i + \gamma_i + \delta_i =
0$. Kirchhoff at the leaf vertices $b_i, c_i, d_i$ (each of degree 3)
expresses each spoke as a "chord step" along its cycle:

$$
\beta_i = B_i - B_{(i-1) \bmod n}, \qquad
\gamma_i = \Omega^c_i - \Omega^c_{(i-1)}, \qquad
\delta_i = \Omega^d_i - \Omega^d_{(i-1)},
$$

where $B_i$ is the value on edge $b_i b_{(i+1) \bmod n}$ oriented
forward, $\Omega^c_i := \Omega_i$ on the c-half of the outer cycle,
and $\Omega^d_i := \Omega_{n+i}$ on the d-half. The twist enters as

$$
\gamma_0 = \Omega^c_0 - \Omega^d_{n-1}, \qquad
\delta_0 = \Omega^d_0 - \Omega^c_{n-1}.
$$

Summing the three Kirchhoff equations at $a_i$ and substituting the
chord forms gives the **conservation law**

$$
S_i \;:=\; B_i + \Omega^c_i + \Omega^d_i \;=\; S_{i-1}
\qquad (\text{constant across all stars, twist included}),
$$

so a single $S \in \mathbb{R}^3$ characterises the entire flow.

## The state and the transfer map

Define the **state** at index $i$

$$
X_i \;:=\; (B_i, \Omega^c_i, \Omega^d_i) \in (S^2)^3
\quad \text{with} \quad
B_i + \Omega^c_i + \Omega^d_i \,=\, S.
$$

The transition $X_{i-1} \to X_i$ is determined by the unit-triangle
step $(\beta_i, \gamma_i, \delta_i)$ with $\beta + \gamma + \delta = 0$,
each unit, satisfying the three "$2\pi/3$-from-previous" angle
constraints

$$
\langle \beta_i, B_{i-1} \rangle = -\tfrac{1}{2}, \quad
\langle \gamma_i, \Omega^c_{i-1} \rangle = -\tfrac{1}{2}, \quad
\langle \delta_i, \Omega^d_{i-1} \rangle = -\tfrac{1}{2}.
$$

Parameterise $\beta_i, \gamma_i$ by angles $\phi, \psi$ on their
$2\pi/3$-circles around $B_{i-1}, \Omega^c_{i-1}$ respectively (each
a 1-dim circle on $S^2$). The reduced system has 2 unknowns and 2
equations:

$$
F_1(\phi, \psi) \;:=\; \langle \beta(\phi), \gamma(\psi) \rangle + \tfrac{1}{2} = 0,
\qquad
F_2(\phi, \psi) \;:=\; \langle \beta(\phi) + \gamma(\psi), \Omega^d_{i-1} \rangle - \tfrac{1}{2} = 0,
$$

where $F_2$ is linear in $(\cos\phi, \sin\phi, \cos\psi, \sin\psi)$ and
$F_1$ is bilinear. Generically the system has a finite, branched
solution set (Bezout bound $\le 4$).

The **monodromy** is the periodic closing: with the twist,

$$
T^n(X_0) \;=\; \pi(X_0), \qquad \pi : (B, \Omega^c, \Omega^d) \mapsto (B, \Omega^d, \Omega^c).
$$

So $J_n$ admits an $S^2$-flow iff there exists an initial state $X_0$
(with global $S$) and a *consistent branch* of $T$ such that after
$n$ steps the state is the c/d-swap of $X_0$.

## Empirical verification on $J_5, J_7, J_9, J_{11}$

The implementation in [scripts/flower_transfer.py](../scripts/flower_transfer.py)
covers:

- `extract_flower_state(G, edges, vectors, k)` — pulls
  $(B, \Omega^c, \Omega^d, \beta, \gamma, \delta, S)$ from an
  $S^2$-flow witness on $J_{2k+1}$, indexed by the canonical
  $a_i = i$, $b_i = n+i$, $c_i = 2n+i$, $d_i = 3n+i$ labels.
- `verify_state_invariants(state)` — checks all unit norms, the
  Kirchhoff equation $\beta + \gamma + \delta = 0$ at each star, the
  chord equations on the three cycles (including the twist), and the
  conservation $S_i = S$.
- `transfer_step(X_prev, S, seed_spokes)` — solves the 2D Newton system
  $(F_1, F_2) = 0$ for the angles $(\phi, \psi)$ and returns the next
  state.
- `forward_iterate(X0, S, seed_state)` — applies $T$ $n - 1$ times
  starting at $X_0$.
- `monodromy_closure(state)` — applies the closing step $i = 0$ (with
  the twist) to $X_{n-1}$ and asserts the result equals $X_0$.

Running on machine-precision witnesses from
[witness.find_witness](../scripts/witness.py):

| Family | $n$ | $S$ (one sample) | Forward-iterate max-err | Monodromy max-err |
|---|---:|---|---:|---:|
| $J_5$ | 5 | $(-0.69, -0.88, +0.21)$ | $1.4\cdot 10^{-15}$ | $1.5\cdot 10^{-15}$ |
| $J_7$ | 7 | $(+0.94, -0.53, -0.02)$ | $6.4\cdot 10^{-15}$ | $6.4\cdot 10^{-15}$ |
| $J_9$ | 9 | $(-0.67, +0.21, -0.72)$ | $2.3\cdot 10^{-10}$ | $2.3\cdot 10^{-10}$ |
| $J_{11}$ | 11 | $(+0.22, -0.50, +0.12)$ | $7.2\cdot 10^{-15}$ | $6.2\cdot 10^{-15}$ |

All four families satisfy the monodromy closure to better than
$10^{-9}$. The $J_9$ run sits at $\sim 10^{-10}$ because one
Newton step on that trajectory lands near a near-singular Jacobian; the
test tolerance accommodates this without changing the conclusion.

The 20 tests in
[tests/test_flower_transfer.py](../tests/test_flower_transfer.py)
exercise the full chain
(extract $\to$ verify $\to$ reconstruct $\to$ single-step $\to$
forward-iterate $\to$ monodromy closure) across $k \in \{2, 3, 4, 5\}$.

## What the empirical result establishes

Per family, the witness *is* a fixed point of the $\pi$-twisted
monodromy. This **confirms** the monodromy reduction is faithful: the
2D Newton system seeded by the witness reproduces every chord step at
machine precision, and the closing step matches $\pi(X_0)$.

What it does **not yet** prove is a uniform existence theorem for all
odd $n$: each $J_{2k+1}$ requires its own witness to seed the
trajectory.

## Toward an infinite-family theorem

A clean flower theorem would establish: for every odd $n$, the
$\pi$-twisted monodromy $T^n - \pi$ has a zero on the conservation
surface.

Dimension count:
- Initial state $X_0$ on the conservation surface: $3$ dofs.
- Closing equation $T^n(X_0) - \pi(X_0) = 0$: $3$ scalar equations
  (the closing must hit the right state on the conservation
  surface).

So generically the zero set is $0$-dimensional — a finite collection
of "monodromy-fixed" initial conditions for each $n$.

## Transversality at the certified fixed points

The Jacobian
$$
J \;:=\; \left.\frac{\partial M}{\partial X_0}\right|_{X_0 = \text{witness}},
\qquad M(X_0) := T^n(X_0) - \pi(X_0),
$$
controls whether the fixed point is isolated and persistent under
perturbation. It is computed numerically in
[scripts/flower_monodromy_jacobian.py](../scripts/flower_monodromy_jacobian.py)
by finite differences in 3 tangent directions on the conservation
surface, each step seeded by the witness's $\phi_i, \psi_i$ angles so
the 2D Newton solver follows the same algebraic branch as the
certified trajectory.

### Gauge symmetry

The problem is $\mathrm{SO}(3)$-equivariant: rotating every vector by a
global $R$ rotates $(X_0, S)$ together. Restricting to the conservation
surface for *fixed* $S$, only the 1-dim subgroup of rotations *around
the $S$-axis* preserves $S$. So $\ker J$ contains the analytical
gauge direction
$$
\xi_{\text{gauge}}(X_0) \;:=\; (\hat S \times B, \hat S \times \Omega^c, \hat S \times \Omega^d),
\qquad \hat S = S/|S|,
$$
and we expect $\mathrm{rank}\,J \le 2$. The fixed point is called
**transverse modulo gauge** iff $\mathrm{rank}\,J = 2$ — equivalently,
the second-largest singular value $\sigma_2$ is bounded away from
zero, and $\xi_{\text{gauge}}$ accounts for the entire null space.

### Empirical Jacobian spectrum across the family

Using $\varepsilon = 10^{-7}$ central differences on the certified
witnesses (`witness.find_witness`, seed 2026, 400 restarts):

| Family | $n$ | $\sigma_1$ | $\sigma_2$ | $\sigma_3 / \sigma_1$ | $\Vert J\,\xi_{\text{gauge}}\Vert / \sigma_1$ | rank | transverse mod gauge |
|---|---:|---:|---:|---:|---:|---:|:---:|
| $J_5$ | 5 | $13.5$ | $1.11$ | $3.9 \cdot 10^{-10}$ | $5.5 \cdot 10^{-10}$ | $2$ | ✓ |
| $J_7$ | 7 | $65.6$ | $1.45$ | $9.4 \cdot 10^{-11}$ | $1.9 \cdot 10^{-9}$  | $2$ | ✓ |
| $J_9$ | 9 | $3.4 \cdot 10^{5}$ | $122$ | $1.5 \cdot 10^{-6}$ | $8.8 \cdot 10^{-4}$ | $2$ | ✓ |
| $J_{11}$ | 11 | $8.88$ | $1.37$ | $1.7 \cdot 10^{-10}$ | $2.5 \cdot 10^{-9}$  | $2$ | ✓ |

Two observations:

1. **All four certified fixed points are transverse modulo gauge.**
   The null direction is identified *analytically* with the SO(3)
   rotation about $\hat S$ to better than $10^{-3}$ relative precision
   in every case (and to $10^{-9}$ for the well-conditioned families).
2. **Conditioning is non-monotone in $n$.** The largest singular value
   spikes to $\sim 3 \cdot 10^{5}$ at $J_9$ — a particular witness on a
   numerically stiff branch — yet still drops back to $\sim 9$ at
   $J_{11}$. The "expansion factor" $\sigma_1$ is *not* an increasing
   function of $n$; it depends on the specific branch the
   Levenberg-Marquardt witness search lands on.

### Consequence for continuation

The transversality result is the *gatekeeping condition* for the
infinite-family attack:

> **Claim (implicit-function-theorem corollary).** Let
> $M_\lambda : X_0 \mapsto T_\lambda^n(X_0) - \pi(X_0)$ depend smoothly
> on a deformation parameter $\lambda$ (twist angle, conserved sum
> $S$, or a continuous interpolation between $J_n$ and $J_{n+2}$).
> If at $\lambda = \lambda_0$ the map $M_{\lambda_0}$ has a transverse
> (modulo gauge) zero $X_0^{(0)}$, then for $\lambda$ in an open
> neighbourhood of $\lambda_0$ there exists a smooth family
> $X_0^{(\lambda)}$ of zeros.

This says: any well-conditioned $J_n$ fixed point persists under
*continuous* deformation. It does *not* yet say the family persists
across the discrete jump $n \to n + 2$. The right follow-up is a
**continuation in twist angle** that bridges $J_n$ to $J_{n+2}$ via a
parameterised intermediate structure (see "next steps" below).

## Next steps

1. ~~**Compute the monodromy Jacobian** at the certified fixed points
   and check transversality.~~ Done above.
2. **Continuation in twist angle.** Replace the discrete twist $\pi$
   by a one-parameter family $\pi_\theta = R_\theta \circ \pi$ where
   $R_\theta$ is a rotation about $\hat S$ (the gauge axis) by angle
   $\theta$. The witness fixed point sits at $\theta = 0$; sweep
   $\theta \in [0, 2\pi)$ and check whether the fixed point persists
   continuously. If $J$ is the *only* obstacle to continuation, this
   sweep should produce a closed orbit of fixed points.
3. **Uniform/periodic ansatz.** Look for fixed or low-period points
   of $T$ before the swap: states $X^*$ with $T(X^*) = X^*$ (or
   $T^p(X^*) = X^*$ for $p | n$). A constant trajectory $X_i = X^*$
   bypasses the closing equation if $\pi(X^*) = X^*$ (i.e.,
   $\Omega^c_* = \Omega^d_*$), and the monodromy then reduces to one
   algebraic step plus a parity condition.
4. **Symbolically eliminate the 2D Newton step.** The system
   $(F_1, F_2) = 0$ is linear in $(\cos\phi, \sin\phi, \cos\psi,
   \sin\psi)$ for $F_2$ and bilinear for $F_1$. Gröbner-eliminate to a
   univariate resolvent. Once explicit, $T$ becomes an iterated
   algebraic correspondence and the monodromy equation an
   $n$-fold composition of small-degree maps.

## Files

- [scripts/flower_transfer.py](../scripts/flower_transfer.py) — state extraction, transfer step, forward iteration, monodromy closure
- [scripts/flower_monodromy_jacobian.py](../scripts/flower_monodromy_jacobian.py) — tangent basis, twisted closing step, numerical Jacobian
- [tests/test_flower_transfer.py](../tests/test_flower_transfer.py)
- [tests/test_flower_monodromy_jacobian.py](../tests/test_flower_monodromy_jacobian.py)
- [docs/flower_snarks_cdc.md](flower_snarks_cdc.md) — the failed CDC route
- [docs/no_flower_dot_decomposition.md](no_flower_dot_decomposition.md) — the 3-cut wall
- [docs/splice4.md](splice4.md) — the 4-cut wall
