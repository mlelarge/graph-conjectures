# Flower-snark asymptotic limit — measurement and honest scope

The infinite-family target

> $\forall k \ge K, \; J_{2k+1}$ admits an $S^2$-flow,

is most naturally approached via a limit object as $n \to \infty$.
If the certified $J_n$ solutions converge (after suitable rescaling)
to a smooth profile, that profile is the candidate "limit fixed
point". One can then prove existence in the limit and lift back to all
sufficiently large odd $n$ by perturbation, leaving only finitely many
small-$n$ cases for direct Krawczyk certification.

This module asks: **do the certified $J_n$ witnesses converge to a
smooth limit as $n$ grows?**

## Diagnostic battery

[scripts/flower_asymptotic.py](../scripts/flower_asymptotic.py)
implements four cross-$n$ diagnostics on a gauge-fixed `FlowerState`:

| Diagnostic | Smooth-limit signature |
|---|---|
| $\|S\|$ (conserved sum magnitude) | should stabilise (or be fixable) across $n$ |
| Kabsch step residual $\Vert R X_{i-1} - X_i\Vert_F$ | should $\to 0$ (steps approaching pure rotations) |
| Step rotation axis $\cdot \hat S$ alignment | should $\to 1$ (rotations about the conserved axis) |
| Dominant Fourier frequency of $\beta_i$ relative to $n$ | should $\to 0$ (low-freq, hence smooth, profile) |

The "smooth-limit score" combines the latter three trends into a
$[0, 3]$ integer score; a smooth limit would score 3.

## Results on Levenberg-Marquardt random witnesses

| $n$ | $\|S\|$ | mean step angle (deg) | mean Kabsch residual | $\|$axis $\cdot \hat z\|$ | dominant freq / $n$ |
|---:|---:|---:|---:|---:|---:|
| 5 | 1.133 | 84.9 | 0.835 | 0.527 | 0.400 |
| 7 | 1.076 | 93.2 | 0.934 | 0.552 | 0.429 |
| 9 | 1.010 | 100.4 | 0.732 | 0.851 | 0.444 |
| 11 | 0.557 | 75.4 | 0.262 | 0.740 | 0.364 |
| 13 | 0.985 | 84.2 | 0.783 | 0.560 | 0.462 |

Trend slopes (linear regression w.r.t. $n$):

- $|S|$ standard deviation across family: $0.205$ (substantial).
- Kabsch step residual: slope $-3.9 \times 10^{-2}$ ($\to 0$ slowly, good).
- Axis $\hat z$-alignment: slope $+1.3 \times 10^{-2}$ ($\to 1$ slowly, good).
- Dominant $\beta$-FFT frequency / $n$: slope $+2.9 \times 10^{-3}$ (*not* shrinking, bad).

**Smooth-limit score: 2 / 3.** Two metrics support the hypothesis;
one rejects it.

## Honest reading

The simple "smooth profile" hypothesis fails on the current data.
Specifically:

1. **The conserved sum $|S|$ varies substantially across the family**
   ($\sigma_{|S|} \approx 0.2$). Different witnesses live on different
   SO(3)-gauge orbits of the conservation surface. There is no single
   $|S|$ that all certified flows share. Either the right limit is
   indexed by $|S|$ (so we need a family parameter, not a single
   point), or the LM witness search lands on inequivalent branches at
   each $n$.

2. **The $\beta$-spoke Fourier spectrum stays high-frequency.** The
   dominant non-zero mode for $J_n$ is consistently near $n/2$, not
   $1$ or $2$. This is the signature of step-to-step *anti-correlation*
   — adjacent $\beta_i$ have negative inner product — not of a smooth
   slow drift. Geometrically the b-cycle trajectory zig-zags rather
   than spiraling.

3. **However, the per-step rotation residual is decreasing and the
   rotation axis is aligning with $\hat S$.** So while $\beta$ itself
   stays oscillatory, the *joint* state $(B, \Omega^c, \Omega^d)$ is
   becoming better approximated by a rotation about the conserved
   axis. The right limit object is probably not a smooth profile of
   $\beta$, but a structural decomposition

$$
X_i \;\approx\; R^{i/n}_{\text{slow}} \cdot X_0 \;+\; \text{high-freq oscillation around the rotation orbit},
$$

with the high-frequency part possibly amenable to a homogenisation
argument.

## What this rules in / out

> **Ruled out.** The naïve hypothesis "rescaled witnesses $X_i$
> converge pointwise to a smooth $X_\infty(\tau)$ as $n \to \infty$"
> on the LM-random witness family.

> **Still open.** A more structured limit object — for example a
> two-scale homogenisation $X_i \approx R^i_{\text{slow}} Y_i^{\text{fast}}$
> with $R_{\text{slow}}$ a slow rotation about $\hat S$ and
> $Y^{\text{fast}}$ a fast-oscillating profile with zero average over a
> period — could still exist. Two of the three diagnostics
> (decreasing Kabsch residual, increasing axis alignment) are
> consistent with this picture.

## Next steps

The current diagnostic suite tells us what to look for next; it does
*not* yet identify the limit.

1. **Constrained witness search.** For each $n$, search for witnesses
   with a fixed $|S|$ (e.g., $|S| = 1$). This removes the
   gauge-orbit variation across the family and isolates a single
   "branch". Levenberg-Marquardt with a penalty term on $|S|$ is the
   simplest way; an interior-point method on the unit-norm + $|S|$
   constrained system is the rigorous way.

2. **Constrained witness search II: cyclic symmetry.** Look for
   witnesses with an exact discrete cyclic symmetry
   $X_i = R^i \cdot X_0$ for some $R \in \mathrm{SO}(3)$ — if any
   exists, the closing condition becomes $R^n = \pi$, which is a
   pure algebraic equation on $R$. This is the cleanest possible
   "limit-compatible" witness.

3. **Two-scale decomposition test.** Given a witness, fit
   $X_i \approx Q_i \cdot X_*$ for a slow $Q_i \in \mathrm{SO}(3)$
   and a fixed reference $X_*$ via Procrustes per step; check whether
   $Q_i$ are themselves smooth as functions of $i$ for large $n$.

4. **Define the candidate limit ODE.** If the Kabsch residual trend
   extrapolates to zero at some finite $n^*$, the corresponding
   "rotation generator" $\Omega \in \mathfrak{so}(3)$ gives a candidate
   ODE $\dot X = \Omega X$ on the conservation surface, whose
   time-$T$ flow is supposed to recover $T^n$ at $T = 1$.

These are concrete and modular. The present module's purpose is to
make any future "we found the limit" claim testable against the
same diagnostic battery — preventing future drift into wishful
thinking.

## Files

- [scripts/flower_asymptotic.py](../scripts/flower_asymptotic.py) — Kabsch step rotation, FFT, autocorrelation, smooth-limit diagnostic
- [tests/test_flower_asymptotic.py](../tests/test_flower_asymptotic.py) — 6 tests pinning the measurement infrastructure
- [docs/flower_monodromy.md](flower_monodromy.md) — transfer-map theory and full 3-by-3 Jacobian
- [docs/flower_continuation.md](flower_continuation.md) — gauge-fix + reduced 2-by-2 Jacobian + twist continuation
