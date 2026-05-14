# Flower-snark transfer map — direct monodromy reduction

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
of "monodromy-fixed" initial conditions for each $n$. The right
follow-on investigation is:

1. **Numerical continuation in $n$.** Use the $J_5$ fixed point as a
   seed and continue through $J_7, J_9, J_{11}, \dots$ Track whether
   the fixed point persists under deformation.
2. **Asymptotics.** Linearise $T$ around a uniform-flow trajectory
   (constant $X_i$) and study the spectral radius of $T^n - \pi$.
3. **Closed-form steps.** The 2D Newton system $(F_1, F_2) = 0$ is
   bilinear/linear in $(\cos\phi, \sin\phi, \cos\psi, \sin\psi)$ and
   reduces to a univariate polynomial of small degree after
   elimination. A closed-form per-step branch might unlock an inductive
   monodromy argument.

These are independent of the gadget closure work — they target the
flower family directly via its own periodic dynamics, not via gluing
smaller cubic pieces.

## Files

- [scripts/flower_transfer.py](../scripts/flower_transfer.py)
- [tests/test_flower_transfer.py](../tests/test_flower_transfer.py)
- [docs/flower_snarks_cdc.md](flower_snarks_cdc.md) — the failed CDC route
- [docs/no_flower_dot_decomposition.md](no_flower_dot_decomposition.md) — the 3-cut wall
- [docs/splice4.md](splice4.md) — the 4-cut wall
