# Flower-snark continuation — gauge-fixed reduced system and twist sweep

[flower_monodromy.md](flower_monodromy.md) establishes that the
certified $J_{2k+1}$ fixed points are *transverse modulo gauge* — the
$3 \times 3$ Jacobian has rank 2 with the SO(3)-about-$\hat S$
direction in its kernel. This is **local persistence**, not yet the
infinite-family theorem. To make progress toward a uniform statement
we now:

1. **Gauge-fix explicitly** to a 2-variable reduced system $F(x, \theta) = 0$;
2. **Introduce a continuous parameter** $\theta$;
3. **Track the branch** via predictor-corrector continuation.

## Gauge-fixing

The full SO(3) symmetry has dimension 3. On the conservation surface
for *fixed* $S$, only the SO(2) subgroup of rotations about $\hat S$
preserves $S$ and acts non-trivially. We remove this residual SO(2) by
applying a two-step rotation to the witness state:

- **Step 1.** Rotate every vector by $R_1 \in \mathrm{SO}(3)$ with
  $R_1 S = (0, 0, |S|)$, i.e., align $\hat S$ with $+\hat z$.
- **Step 2.** Rotate about $\hat z$ by the angle needed to put $B_0$
  in the $xz$-plane with non-negative $x$-component:
  $B_0 = (b_x, 0, b_z)$, $b_x \ge 0$.

The implementation is in
[scripts/flower_continuation.py](../scripts/flower_continuation.py)
as `gauge_fix_state(state)`. Both steps preserve all structural
invariants (unit norms, Kirchhoff equations, conservation law) up to
machine precision.

## Reduced 2D residual

The conservation surface is 3-dim; the gauge-fixed quotient is 2-dim
because we have pinned the 1-dim SO(2) gauge orbit. We parameterise
the quotient locally by

$$
x \in \mathbb{R}^2 \;\longmapsto\; X_0(x) = \pi_{(S^2)^3}\bigl(X_0^{\text{ref}} + Q x\bigr),
$$

where $Q \in \mathbb{R}^{9 \times 2}$ is a *reduced tangent basis* at
$X_0^{\text{ref}}$ — an orthonormal basis of the 3-dim tangent space
*orthogonal to the SO(2)-gauge direction*. The reduced residual is

$$
F(x, \theta) \;:=\; Q^\top \bigl(T^n(X_0(x)) - R_\theta\,\pi(X_0(x))\bigr),
$$

where $R_\theta \in \mathrm{SO}(3)$ is rotation by $\theta$ about
$\hat z$ (the post-gauge-fix $\hat S$-axis). At $\theta = 0$ this is
the standard $J_n$ monodromy and $F(0, 0) = 0$ at the witness.

## Reduced Jacobian at the witness

`reduced_jacobian(fixed_state, eps=1e-7)` returns the $2 \times 2$
numerical Jacobian $\partial F / \partial x$ at $x = 0$.

| Family | $n$ | $\sigma_1$ | $\sigma_2$ | $\det J_{\text{red}}$ | $\sigma_1/\sigma_2$ |
|---|---:|---:|---:|---:|---:|
| $J_5$ | 5 | $13.06$ | $0.476$ | $+6.21$ | $27.5$ |
| $J_7$ | 7 | $34.31$ | $0.637$ | $+21.86$ | $53.8$ |
| $J_{11}$ | 11 | $5.92$ | $1.20$ | $+7.13$ | $4.9$ |

All three reduced Jacobians have determinants bounded **away from zero
by at least 6**, and minimum singular values exceeding $0.4$. The
fixed points are *isolated* in the gauge-fixed quotient. This is the
explicit non-degeneracy condition that the implicit function theorem
requires for continuation.

## Predictor-corrector continuation in twist angle

`continuation_in_twist(state, theta_max, n_steps)` sweeps $\theta$
from $0$ to $\theta_{\max}$ in steps of $\theta_{\max} / n_{\text{steps}}$,
using a tangent predictor

$$
\frac{d x}{d \theta} \;=\; -J_{\text{red}}^{-1}\,\frac{\partial F}{\partial \theta}
$$

followed by Newton correction on $F(x, \theta_{\text{new}}) = 0$. Step
size is halved (down to $10^{-3}\cdot$base) if Newton diverges and
slowly grown back if Newton converges in $\le 3$ iterations.

Each branch point records:
- $\theta$,
- local coordinates $x$ in the current reduced basis,
- $\det J_{\text{red}}$, $\sigma_{\min}$, $\sigma_{\max}$,
- Newton residual norm,
- Newton iteration count.

### Empirical branch behaviour (full sweep, $\theta \in [0, 2\pi]$)

| Family | Tracked $\theta$ range | $\min|\det J|$ | $\min \sigma_{\min}$ | Stop reason |
|---|---|---:|---:|---|
| $J_5$ | $[0, 1.815]$ ($\approx 0.58\pi$) | $4.97$ | $0.48$ | underlying `transfer_step` Newton failed (branch jump) |
| $J_7$ | $[0, 2.511]$ ($\approx 0.80\pi$) | $13.12$ | $0.43$ | `transfer_step` Newton failed |
| $J_{11}$ | $[0, 1.414]$ ($\approx 0.45\pi$) | $0.22$ | $0.014$ | $\sigma_{\min}$ collapsing — approaching a **fold** |

Three observations:

1. **Local persistence is robust.** $J_5$ tracks for more than half of
   $[0, 2\pi]$ with $|\det J| > 4.97$; $J_7$ goes further with even
   stiffer conditioning. Neither shows a fold in the tracked interval —
   the failure is on the *inner* `transfer_step` Newton (a branch-jump
   artefact of the seeded-Newton trajectory tracking, not a singularity
   of the monodromy).
2. **$J_{11}$ has a fold near $\theta \approx \pi/2$.** $\sigma_{\min}$
   drops monotonically from $1.20$ at $\theta = 0$ to $0.014$ at the
   stopping point; $|\det J|$ collapses to $0.22$. This is the
   signature of an approaching turning point. Continuing past it
   would require switching to arc-length continuation.
3. **Conditioning is family-dependent.** $J_5$ and $J_7$ stay
   well-conditioned over a long interval; $J_{11}$ folds earlier. No
   uniform guarantee across the family — each $n$ has its own branch
   geometry.

## What this establishes — and what it doesn't

> **Established (local).** For each $J_{2k+1}$ with $k \in \{2, 3, 5\}$
> the certified fixed point persists as a smooth $\theta$-branch in a
> nontrivial open neighbourhood of $\theta = 0$, with the reduced
> Jacobian $\det J_{\text{red}}$ remaining bounded away from zero over
> that neighbourhood. By the implicit function theorem the branch
> exists for $\theta$ in some open interval around $0$.

> **Not yet established (global / cross-family).** The current
> continuation parameter $\theta$ deforms the *closing twist* at fixed
> $n$. It does **not** connect $J_5$ to $J_7$ to $J_9$. To get a true
> infinite-family theorem we need a parameterisation in which different
> integer values of a *single* parameter recover different $J_n$'s.

## Toward cross-family continuation

Per the user-proposed plan, a natural family is
$\theta = \pi / (2k+1)$. To realise this we would need the transfer
map $T$ itself to depend on a continuous parameter $\nu$ in a way that
collapses to the integer $n$-step discrete iteration at $\nu = 1/n$.

One concrete possibility: replace the $n$-fold composition
$T \circ T \circ \dots \circ T$ by the time-$1$ flow of an
autonomous ODE whose generator is a "logarithm" of $T$ scaled by $\nu$,
plus a closing condition that depends on $\nu$. At $\nu = 1/n$ for
integer $n$ this should agree with the discrete monodromy. The two
hard parts are (i) defining $\log T$ unambiguously on the branched
algebraic correspondence and (ii) writing a closing condition that
specialises to the c/d-swap $\pi$ at integer $n$.

Independent of that, the present module already gives:
- a clean **2-variable reduced** system, suitable for
  certified-arithmetic enclosure work (Krawczyk / radii polynomial);
- a robust **branch-tracking** infrastructure that can be re-used as
  soon as a cross-family parameter is defined.

## Interval certification (next phase)

Once a cross-family parameter is in place, the next step (Krawczyk
or radii-polynomial validation) is purely mechanical:

1. Cover the parameter interval $\theta \in [\theta_{\min}, \theta_{\max}]$
   with a finite collection of overlapping closed boxes.
2. For each box, use interval arithmetic (mpmath `iv`) on the reduced
   $F(x, \theta)$ and the Krawczyk operator
   $K(x_0; \theta) = x_0 - J^{-1}_{\text{red}}(x_0; \theta) F(x_0; \theta) + (I - J^{-1}_{\text{red}} J_F(B; \theta))(B - x_0)$.
3. If $K(x_0; \theta) \subset B$ for the box $B \ni x_0$, the box
   contains a unique fixed point; combine boxes to cover the parameter
   interval.

The existing `scripts/interval.py` already implements Krawczyk
operators with the schema-v2 replayable certificate format; extending
to a parameterised system is mostly a question of varying $\theta$ in
the polynomial system definition.

## Files

- [scripts/flower_continuation.py](../scripts/flower_continuation.py) — gauge-fix, reduced tangent basis, reduced Jacobian, predictor-corrector continuation
- [tests/test_flower_continuation.py](../tests/test_flower_continuation.py) — 21 tests across $k \in \{2, 3, 5\}$
- [docs/flower_monodromy.md](flower_monodromy.md) — the underlying transfer/Jacobian theory
- [scripts/flower_monodromy_jacobian.py](../scripts/flower_monodromy_jacobian.py) — full 3-dim Jacobian (pre-gauge-fix)
- [scripts/interval.py](../scripts/interval.py) — Krawczyk infrastructure for future certification
