# Flower-snark two-scale model — negative result

[flower_asymptotic.md](flower_asymptotic.md) left open whether a
two-scale model

$$
X_i \;\approx\; R_{\text{slow}}^i \; Y_{i \bmod p}
$$

could explain the contradictory diagnostics observed on LM-random
witnesses: per-step Kabsch residuals shrink and rotation axes align
with $\hat S$ (suggesting a slow rotation), while the spoke spectrum
stays high-frequency dominated (suggesting a fast template). This
module tests that hypothesis directly.

## Method

For each candidate period $p$, the fit picks the slow rotation
$R \in \mathrm{SO}(3)$ such that $R^p X_i \approx X_{i+p}$ on average,
and then averages $R^{-i} X_i$ over $i \bmod p$ to get the templates
$Y_0, \ldots, Y_{p-1}$. A nonlinear refinement step
(`scipy.optimize.minimize`, Nelder-Mead on the 3-vector $\omega$
parameterising $R = \exp(\hat\omega)$) re-optimises the slow rotation
with the templates implicitly defined by the Procrustes average.

`scripts/flower_twoscale.py` provides

- `fit_two_scale(state, p)` — initial Kabsch-Procrustes fit
- `refine_two_scale(state, fit)` — nonlinear refinement of $R$
- `scan_periods(state, max_p)` — fit $p \in \{1, \ldots, \max_p\}$
- `candidate_trajectory(fit, n)` — reconstruct $\hat X_i = R^i Y_{i \bmod p}$
- `flow_residual_of_candidate(cand, state)` — measure unit-norm,
  Kirchhoff, and chord constraint violations of the reconstructed
  trajectory.

## Empirical result

After the nonlinear refinement, RMS residuals
$\sqrt{\frac{1}{n} \sum_i \|R^i Y_{i \bmod p} - X_i\|^2}$ on the
gauge-fixed witnesses are:

| $n$ | $p=1$ | $p=2$ | $p=3$ | $p=4$ | best $p$ | best RMS | candidate flow violation |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 5  | 1.14 | 0.86 | 0.80 | 0.43 | 4 | 0.43 | 1.00 |
| 7  | 1.41 | 1.36 | 1.04 | 0.83 | 4 | 0.83 | 0.77 |
| 9  | 1.28 | 1.05 | 0.93 | 0.91 | 4 | 0.91 | 0.74 |
| 11 | 1.36 | 1.40 | 1.15 | 0.95 | 4 | 0.95 | 0.46 |
| 13 | 1.39 | 1.37 | 1.32 | 1.15 | 4 | 1.15 | 0.85 |

Three observations:

1. **All RMS residuals are $\mathcal{O}(1)$, not $\mathcal{O}(\varepsilon)$.**
   A successful two-scale model would have residuals shrinking to
   machine precision; instead they sit between 0.4 and 1.2.

2. **The "best $p$" is always the largest one tested.** This is the
   signature of overfitting: increasing $p$ adds 9 degrees of freedom
   per template, so larger $p$ always reduces in-sample residual. The
   model is not picking up genuine periodic structure -- it is
   absorbing every wrinkle into more parameters.

3. **The fit *worsens* with $n$.** The best-$p$ RMS climbs from 0.43
   at $n = 5$ to 1.15 at $n = 13$. The opposite of what one would
   expect if a genuine two-scale model existed.

The candidate flow violations (max unit-norm, Kirchhoff, chord
violations on the reconstructed $\hat X_i$) sit at $0.46$–$1.00$ —
the candidate trajectories are not close to valid $S^2$-flows by any
measure. They cannot serve as productive LM initialisers (the
violations are larger than the typical LM starting residual on a
random init).

## Structural obstruction: divisibility

A subtler issue surfaces on inspection. The flower-snark monodromy
condition is $X_n = \pi(X_0)$ where $\pi$ is the c/d-swap. For an
exact two-scale ansatz with period $p$ to close, we need

$$
R^n Y_{n \bmod p} \;=\; \pi(Y_0).
$$

If $p \nmid n$, the indices $n \bmod p \ne 0$, so the closing involves
templates "out of phase" with the start — no consistent assignment
unless $Y_k$ are all equal (degenerate, $p = 1$).

For odd $n = 2k + 1$ (the flower-snark sequence), the small candidate
periods break down as follows:

| $p$ | divides odd $n$ iff | applies to |
|---:|---|---|
| 1 | always | every $J_{2k+1}$ |
| 2 | never (odd $n$) | nothing |
| 3 | $n \equiv 0 \pmod 3$ | $J_9, J_{15}, J_{21}, \ldots$ |
| 4 | never | nothing |
| 5 | $n \equiv 0 \pmod 5$ | $J_5, J_{15}, J_{25}, \ldots$ |
| 6 | never | nothing |

So **for $J_5, J_7, J_{11}, J_{13}$ — the bulk of the small family —
only $p = 1$ admits an *exact* closing two-scale model, and $p = 1$
fits worst.** Other small $p$ values can only ever be approximate.
The empirical RMS $\mathcal{O}(1)$ is then expected: the model is
inconsistent at the boundary by construction.

## Decision

Per the user's success criterion stated when this experiment was
proposed:

> If no stable small period appears, the flower route is likely not
> going to give a clean theorem soon. Then I'd stop and return to
> gadget closure / other named snark families.

The data says:

- No stable small period (best $p$ ≡ $p_{\max}$, classic overfitting).
- The RMS grows with $n$, not shrinks.
- There is a structural divisibility obstruction for the small $p$
  values that *would* give exact closure.

The flower-snark direct-monodromy route has now hit a wall on three
independent attempts:

1. **CDC / weighted-CDC** — parity obstruction on the flower's odd
   star count ([flower_snarks_cdc.md](flower_snarks_cdc.md)).
2. **Dot / splice gadget decomposition** — $J_n$ for $n \ge 7$ are
   cyclically $\ge 6$-edge-connected, so no 3- or 4-cut decomposition
   exists ([no_flower_dot_decomposition.md](no_flower_dot_decomposition.md),
   [splice4.md](splice4.md)).
3. **Asymptotic / two-scale reduction** — no smooth limit; no stable
   small-period decomposition; divisibility obstruction for $p \ne 1$.

The local results — transverse-mod-gauge fixed points on
$J_5, J_7, J_9, J_{11}$ and the existence-with-Krawczyk certificates
for all nontrivial snarks at $n \le 28$ — remain solid. But a uniform
infinite-family flower theorem looks structurally hard to come by via
the routes attempted.

## Recommended pivot

Two reasonable directions, neither of which goes through the flower
family:

1. **Gadget closure characterisation
   ([gadget_closure.md](gadget_closure.md)).** Enumerate
   $\mathcal{F}_k$, the set of cubic graphs reachable from the
   certified base $\mathcal{F}_0$ (3 247 nontrivial snarks at
   $n \le 28$) by $k$ rounds of triangle blow-up + dot product. This
   gives concrete infinite families of $S^2$-flow-equipped cubic
   graphs whose construction is explicit and machine-checkable. No
   reliance on the flower monodromy.

2. **Other named cubic-snark families.** Goldberg snarks, Loupekine
   snarks, Blanuša families (after Blanuša-1 and Blanuša-2),
   generalised Petersen $\mathrm{GP}(m, k)$. Each is parametric, and
   the cyclic-edge-connectivity / structural-decomposition picture is
   different — possibly more amenable to gadget reduction than the
   flower.

The flower question itself stays open. The infrastructure built here
(transfer map, Jacobian + transversality, gauge-fix, continuation,
asymptotic + two-scale diagnostics) is available to anyone who wants
to attack it with a new ansatz, but the simple ones are now ruled out.

## Files

- [scripts/flower_twoscale.py](../scripts/flower_twoscale.py) — Procrustes + nonlinear refinement
- [tests/test_flower_twoscale.py](../tests/test_flower_twoscale.py) — 16 tests
- [docs/flower_asymptotic.md](flower_asymptotic.md) — preceding asymptotic-diagnostic work
- [docs/flower_monodromy.md](flower_monodromy.md) — transfer-map theory
- [docs/flower_continuation.md](flower_continuation.md) — gauge-fixed reduced system
- [docs/gadget_closure.md](gadget_closure.md) — the recommended alternative direction
