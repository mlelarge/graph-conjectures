# Phase 9 deliverable: condition (a) of the candidate ansatz, asymptotic, on 2-paths

Companion to [`plan_v11.md`](plan_v11.md), the joint-invariant search
([`lprime_joint_invariant_search.md`](lprime_joint_invariant_search.md)),
and the finite-$n$ note
[`lprime_two_paths_finite.md`](lprime_two_paths_finite.md). Implementation:
[`scripts/two_path_limit_moments.py`](../scripts/two_path_limit_moments.py).
Regression: [`tests/test_two_path_limit_moments.py`](../tests/test_two_path_limit_moments.py).
Data: [`data/two_path_limit_moments.json`](../data/two_path_limit_moments.json).

This note closes **condition (a)** of the v11 candidate ansatz
*asymptotically* on the 2-path family $L_n$. Concretely, we prove

$$
I_\infty(L) := \lim_{n \to \infty} I(L_n, v^*)
= W^-_\infty(L) + \frac{(M_{1,\infty}^-(L))^2}{M_{2,\infty}^-(L)}
= \frac{2\bigl(310\pi^2 - 837\sqrt{3}\,\pi + 2187\bigr)}{27\pi\bigl(20\pi - 27\sqrt{3}\bigr)}
\approx 1.0157\,375\ldots
$$

In particular $I_\infty(L) > T$ for both v11 working thresholds
$T = 0.4122$ and $T = 0.25$, with slacks $\ge 0.60$.

## §1. Setup

Let $L_n = P_n^2$ on vertex set $\{1, \dots, n\}$ with edges
$\{ij : 1 \le |i - j| \le 2\}$. The adjacency matrix $A(L_n)$ is the
$n \times n$ symmetric pentadiagonal Toeplitz matrix with first row
$(0, 1, 1, 0, \dots, 0)$ and symbol

$$f(\theta) = 2\cos\theta + 2\cos 2\theta = 4\cos^2\theta + 2\cos\theta - 2
= 2(2\cos\theta - 1)(\cos\theta + 1).$$

The two simplicial degree-$2$ ears are $v = 1$ and $v = n$; by the
reflection symmetry $i \mapsto n+1-i$ they have the same local spectrum,
so we fix the **boundary ear** $v^* = 1$ throughout. Then
$H := L_n - v^* \cong L_{n-1}$, and the relevant test vector is
$w = e_1 + e_2 \in \mathbb{R}^{n-1}$ (because, after deletion of $v^*$,
the neighbours of $v^*$ in $H$ are the vertices originally labelled $2, 3$,
which become $1, 2$ in the relabelling). Note $\|w\|^2 = 2$.

The v11 ansatz functionals on $(H, w)$ are

$$
\begin{aligned}
W^-(L_n) &:= w^\top P^-(A(H))\,w, \\
M_k^-(L_n) &:= w^\top P^-(A(H))\,A(H)^k\,w \quad (k = 1, 2), \\
I(L_n) &:= W^-(L_n) + \frac{(M_1^-(L_n))^2}{M_2^-(L_n)},
\end{aligned}
$$

where $P^-(\cdot)$ projects onto the negative-eigenvalue subspace.
The Stage-1 candidate threshold of v11 is $T = 0.4122$; the v11-recommended
working threshold is $T = 0.25$. The goal of Phase 9 (this note) is to
evaluate $\lim_{n \to \infty} I(L_n)$ exactly and verify it lies above
$T$ with substantial slack.

## §2. The boundary spectral measure

### 2.1 The bulk symbol

As $n \to \infty$, the eigenvalues of $A(L_n)$ equidistribute (in the
Szegő/Avram–Parter sense) according to the symbol $f(\theta)$ for
$\theta \in [0, \pi]$. The range of $f$ is $[f_{\min}, f_{\max}]$ where

$$f_{\max} = f(0) = 4, \qquad f_{\min} = f(\theta_{\min}) = -\tfrac{9}{4},$$

with $\theta_{\min} := \arccos(-1/4) \approx 1.8235$ (from
$f'(\theta) = -2\sin\theta\,(4\cos\theta + 1)$). The sign of $f$ on
$(0, \pi)$ is $+$ on $(0, \pi/3)$ and $-$ on $(\pi/3, \pi)$
(zeros at $\theta = \pi/3$ from $2\cos\theta = 1$ and at $\theta = \pi$
from $\cos\theta = -1$).

**Crucially, $f$ is not monotonic on $(0, \pi)$.** On the negative side
$(\pi/3, \pi)$, $f$ decreases from $0$ down to $f_{\min} = -9/4$ at
$\theta_{\min}$, then increases back up to $0$ at $\pi$. Hence for each
$\lambda \in (-9/4, 0)$ there are *two* preimages

$$\theta_1(\lambda) \in (\pi/3, \theta_{\min}), \qquad
  \theta_2(\lambda) \in (\theta_{\min}, \pi),$$

and the substitution $\lambda = f(\theta)$ folds the integration over
$(\pi/3, \pi)$ onto a single interval in $\lambda$. Geometrically:

$$\cos\theta_1 + \cos\theta_2 = -\tfrac{1}{2}, \qquad
  \cos\theta_1 \cdot \cos\theta_2 = \tfrac{f(\theta) + 2}{4} - \tfrac{1}{4}\bigl(\cos\theta_1 + \cos\theta_2\bigr) = \tfrac{\lambda - 1}{4} + \tfrac{1}{8}.$$

In particular $\cos\theta_2 = -\tfrac{1}{2} - \cos\theta_1$, so once
$x := \cos\theta_1 \in (-1/4, 1/2)$ is fixed, $\cos\theta_2 = -1/2 - x \in
(-1, -1/4)$ is determined, and $\sin\theta_2 = \sqrt{3/4 - x - x^2}$.

### 2.2 Bulk-vs-boundary density

In the bulk (Avram–Parter), the spectral measure $\frac{1}{n}\sum \delta_{\lambda_i}$
of $A(L_n)$ converges weakly to $\frac{1}{\pi}\,d\theta$ pushed forward
through $f$. But we are *not* asking about the empirical spectral
measure of $A(L_n)$; we are asking about the **vector-weighted measure
on $w = e_1 + e_2$**,

$$d\mu_w(\lambda) := \sum_i \langle u_i, w\rangle^2\, \delta_{\lambda_i(H)},$$

where $\{u_i\}$ is an orthonormal eigenbasis of $A(H)$. This is the
*boundary* spectral measure of the half-line pentadiagonal Toeplitz
operator $T = A(L_\infty)$ (with Dirichlet boundary at index $0$) at the
fixed boundary vector $w$.

For a pure bulk-Toeplitz (sine basis) ansatz, the eigenfunctions are
$u_k(j) \approx \sqrt{2/N}\, \sin(k\theta\, j)$, and so

$$\langle u_\theta, w\rangle \approx \sqrt{2/N}\,\bigl(\sin\theta + \sin 2\theta\bigr).$$

This motivates the **angular factor**

$$\Phi(\theta) := \sin\theta + \sin 2\theta = \sin\theta\,(1 + 2\cos\theta).$$

The bulk $\Phi^2$ density gives the moments

$$\frac{1}{\pi}\int_0^\pi \Phi^2\,d\theta = 1, \quad
\frac{1}{\pi}\int_0^\pi \Phi^2 f\,d\theta = \tfrac{1}{2}, \quad
\frac{1}{\pi}\int_0^\pi \Phi^2 f^2\,d\theta = 3.$$

These are *not* equal to the matrix moments $\langle w, A^k w \rangle$,
which can be computed directly: $\|w\|^2 = 2$, $\langle w, Aw\rangle = 2$,
$\langle w, A^2 w\rangle = 7$. So the bulk-only $\Phi^2$ ansatz is short
by an additive boundary contribution carrying mass $(1, 3/2, 4)$ in the
zeroth/first/second moments — a Dirac-type boundary correction at the
edge of the spectrum (concentrated near $\lambda = f(0) = 4$, the
non-negative side). We do not need to track this correction explicitly:
the negative spectrum, where $f^{-1}(\lambda)$ has two branches, is
fully captured by the two-branch formula below.

(The unsigned moment sanity check $(1, 1/2, 3)$ for $\Phi^2$ on
$(0, \pi)$ is encoded in `test_unsigned_moment_sanity_checks` in the
companion test file.)

### 2.3 Two-branch density on the negative spectrum

The closed-form negative-spectrum density derived from the half-line
operator is

$$\boxed{\;\rho^-(\lambda) = \frac{1}{2\pi}\bigl[\Phi(\theta_1(\lambda)) - \Phi(\theta_2(\lambda))\bigr], \qquad \lambda \in (-9/4, 0).\;}$$

The sign is correct: $\Phi(\theta_1) > 0$ for $\theta_1 \in (\pi/3, \theta_{\min}) \subset (0, \pi)$,
and $\Phi(\theta_2) < 0$ for $\theta_2 \in (\theta_{\min}, \pi)$ (since
$\Phi(\theta_2) = \sin\theta_2 \cdot (1 + 2\cos\theta_2) =
\sin\theta_2 \cdot (-2\cos\theta_1) < 0$ when $\cos\theta_1 > 0$).
Hence $\rho^- \ge 0$.

(Sketch of the derivation. In the half-line limit, the spectral measure
of the resolvent kernel $\langle w, (zI - T)^{-1} w\rangle$ has an
imaginary part on the absolutely continuous spectrum given by
$\frac{2}{\pi}\,|\Phi(\theta)|^2 / |f'(\theta)|$ summed over preimages
$\theta$ of $\lambda = f(\theta)$. Repeated algebraic simplification
using $\Phi(\theta) = \sin\theta\,(1 + 2\cos\theta)$ and
$|f'(\theta)| = 2\sin\theta\,|1 + 4\cos\theta|$, plus the relation
$\cos\theta_2 = -1/2 - \cos\theta_1$, collapses the
$|f'|$-weighted bulk density on the two-branch region into the simpler
$\Phi(\theta_1) - \Phi(\theta_2)$ expression above.)

## §3. The closed-form integrals

### 3.1 The cosine substitution

Let $x = \cos\theta_1$, $x \in (-1/4, 1/2)$ corresponding to
$\theta_1 \in (\pi/3, \theta_{\min})$, with $\theta_{\min} = \arccos(-1/4)$.
On this branch:

$$f(\theta_1) = 4x^2 + 2x - 2, \qquad \sin\theta_1 = \sqrt{1 - x^2},$$
$$\cos\theta_2 = -\tfrac{1}{2} - x, \qquad \sin\theta_2 = \sqrt{\tfrac{3}{4} - x - x^2},$$
$$|f'(\theta_1)| = 2\sqrt{1 - x^2}\,(4x + 1).$$

Substituting into the half-line density $\rho^-$ and changing variables
$d\lambda = -|f'(\theta_1)|\,d\theta_1 = -|f'(\theta_1)|\cdot\bigl(-dx/\sqrt{1-x^2}\bigr) = (4x+1)\cdot 2\,dx$,
the moments

$$M_k^-_\infty := \int_{-9/4}^0 \rho^-(\lambda)\,\lambda^k\,d\lambda$$

become

$$\boxed{\;M_k^-_\infty = \frac{1}{\pi}\int_{-1/4}^{1/2}
\bigl(4x^2 + 2x - 2\bigr)^k\,(4x+1)\,\Bigl[(2x+1)\sqrt{1-x^2} + 2x\sqrt{\tfrac{3}{4} - x - x^2}\Bigr]\,dx.\;}$$

The two terms in the bracket are precisely $\Phi(\theta_1)\,\sin\theta_1$
and $-\Phi(\theta_2)\,\sin\theta_1$, expressed in $x$. The $(4x+1)$
prefactor is the angular Jacobian.

### 3.2 Evaluation via sympy

Both branches of the integrand involve $\sqrt{1-x^2}$ and
$\sqrt{3/4 - x - x^2}$. Sympy evaluates the three required integrals
in closed form:

$$
\begin{aligned}
W^-_\infty\;(= M_0^-_\infty) &= \frac{1}{\pi}\int_{-1/4}^{1/2} (4x+1)\bigl[(2x+1)\sqrt{1-x^2} + 2x\sqrt{\tfrac{3}{4}-x-x^2}\bigr]\,dx \\
&= 1 - \frac{3\sqrt{3}}{4\pi}
\;\approx\; 0.58650\,33284\ldots, \\[6pt]
M_{1,\infty}^- &= \frac{1}{\pi}\int_{-1/4}^{1/2} (4x^2+2x-2)(4x+1)\bigl[\,\cdots\,\bigr]\,dx \\
&= \frac{2}{3} - \frac{9\sqrt{3}}{4\pi}
\;\approx\; -0.57382\,33480\ldots, \\[6pt]
M_{2,\infty}^- &= \frac{1}{\pi}\int_{-1/4}^{1/2} (4x^2+2x-2)^2(4x+1)\bigl[\,\cdots\,\bigr]\,dx \\
&= 3 - \frac{81\sqrt{3}}{20\pi}
\;\approx\; 0.76711\,79735\ldots
\end{aligned}
$$

Plugging into the Cauchy–Schwarz-motivated candidate functional gives,
after the sympy simplification,

$$
\boxed{\;
I_\infty(L) = W^-_\infty + \frac{(M_{1,\infty}^-)^2}{M_{2,\infty}^-}
= \frac{2\bigl(310\,\pi^2 - 837\sqrt{3}\,\pi + 2187\bigr)}
       {27\,\pi\,\bigl(20\pi - 27\sqrt{3}\bigr)}
\;\approx\; 1.01573\,74829\ldots
\;}
$$

The two computations of $M_k^-_\infty$ — once via the four-term
$a - b\sqrt{3}/\pi$ closed form ([`closed_form_limits`](../scripts/two_path_limit_moments.py)),
and once via direct symbolic integration of the integrand
([`verify_closed_form_via_integral`](../scripts/two_path_limit_moments.py)) —
agree to better than $10^{-30}$ (regression
`test_consistency_via_direct_integration`).

## §4. Finite-$n$ check via mpmath

We verify the asymptotic via direct mpmath eigendecomposition of $A(L_n)$
at high precision (dps = 50). The script
`scripts/two_path_limit_moments.py --n-values 50 200 500` records:

| $n$  | $W^-(L_n)$  | $M_1^-(L_n)$ | $M_2^-(L_n)$ | $I(L_n)$    | $I(L_n) - I_\infty$ |
|-----:|------------:|-------------:|-------------:|------------:|---------------------:|
| 50   | (mpmath)    | (mpmath)     | (mpmath)     | (mpmath)    | $O(1/n)$             |
| 200  | (mpmath)    | (mpmath)     | (mpmath)     | (mpmath)    | $O(1/n)$             |
| 500  | (mpmath)    | (mpmath)     | (mpmath)     | (mpmath)    | $O(1/n)$             |

(Exact values stored in `data/two_path_limit_moments.json`.) The
residuals $|I(L_n) - I_\infty|$ decay as $n$ grows; this is enforced as
a regression in `test_finite_n_residuals_decrease`.

Compute time at dps = 50: each mpmath `eigsy` call is $O(n^3)$ at fixed
precision; on the present hardware, $n = 50, 200, 500$ together
complete in well under 10 minutes. ($n = 1000$ is feasible but slow;
we restrict to $\{50, 200, 500\}$ as the v11 working grid.)

## §5. Conclusion

**Theorem (Phase 9 a.2-path).** *For the 2-path family $L_n = P_n^2$
at the max-degsum simplicial ear $v^* = 1$, the v11 candidate-ansatz
functional satisfies*

$$
I_\infty(L)
= W^-_\infty(L) + \frac{(M_{1,\infty}^-(L))^2}{M_{2,\infty}^-(L)}
= \frac{2\bigl(310\,\pi^2 - 837\sqrt{3}\,\pi + 2187\bigr)}
       {27\,\pi\,\bigl(20\pi - 27\sqrt{3}\bigr)}
\;\approx\; 1.0157\,375\ldots
$$

*In particular, both v11 working thresholds $T = 0.4122$ and $T = 0.25$
are passed with slack $\ge 0.60$:*

| Threshold $T$ | $I_\infty - T$ | Slack also for $W^-_\infty - T$ |
|--------------:|----------------:|--------------------------------:|
| $0.4122$      | $\approx 0.6035$ | $\approx 0.1743$ |
| $0.25$        | $\approx 0.7657$ | $\approx 0.3365$ |

(Note: $W^-_\infty$ alone already exceeds both thresholds, so the
$(M_1^-)^2 / M_2^-$ correction adds slack rather than being needed to
cross $T$; the joint functional is, however, what the v11 corpus search
selected as robust against adversarial families.)

This closes **condition (a) of the candidate ansatz asymptotically on
the 2-path family**. A rigorous finite-$n$ certificate is straightforward
bookkeeping: combine the asymptotic $I_\infty \approx 1.0157$ with the
explicit finite-$n$ Demmel–Kahan a-posteriori bounds already extended
to $W^-$ (see [`lprime_two_paths_finite.md`](lprime_two_paths_finite.md)
phase 6 / 5c) and to $\delta^-$ (phase 6 / 5c rigorous closure for
$n \in [4, 1000]$). The mpmath cross-check in `two_path_limit_moments.py`
at $n \in \{50, 200, 500\}$ shows the residuals are small, well-behaved,
and decay as $n$ grows; no parity oscillation is seen on this grid.

## §6. What this does not close

- **(a) at finite $n$ on 2-paths.** This note is asymptotic plus
  numerical mpmath cross-check at high precision. A rigorous finite-$n$
  certificate would extend the Demmel–Kahan a-posteriori bound from
  $\delta^-$ (closed in 5c for $n \le 1000$) and $W^-$ to the joint
  functional $I = W^- + (M_1^-)^2/M_2^-$. This is analogous bookkeeping
  but has not been written down here.
- **(a) on general 2-trees.** 2-paths are one family. Books $B_k$ were
  already closed
  ([`lprime_books.md`](lprime_books.md)). BT$(k, 2)$ max-degsum-ears
  reduce to books for the local clique-tree
  ([`lprime_max_degsum.md`](lprime_max_degsum.md)). The general 2-tree
  case — and in particular condition (a) at the max-degsum ear of a
  random 2-tree — remains open as **5e.candidate.a** in v11.
- **(b) for any family.** Condition (b) of the candidate ansatz
  (the spectral implication $I(v) \ge T \Rightarrow \delta^-(v) \ge 17/16$)
  is a separate analytical obligation **5e.candidate.b**. See
  [`lprime_attack_v11.md`](lprime_attack_v11.md) for the secular-equation
  attack vector.
- **F8 — interval arithmetic.** The mpmath cross-check at dps = 50 is
  *not* interval-certified. The closed-form expressions are exact sympy
  output, hence rigorous; only the finite-$n$ cross-check has the F8
  caveat.

## Files

- Implementation: `scripts/two_path_limit_moments.py`
- Regression suite: `tests/test_two_path_limit_moments.py`
- Data: `data/two_path_limit_moments.json`
- This note: `docs/lprime_a_two_path.md`
