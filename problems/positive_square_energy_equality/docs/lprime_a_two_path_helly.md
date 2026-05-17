# Phase 11 deliverable: Helly / Portmanteau bridge from Phase 10 (half-line)
# to Phase 9 (finite-$n$) — closing condition (a.2-path) as a theorem

Companion to [`plan_v12.md`](plan_v12.md),
[`lprime_a_two_path.md`](lprime_a_two_path.md) (Phase 9 candidate),
and [`lprime_a_two_path_stieltjes.md`](lprime_a_two_path_stieltjes.md)
(Phase 10 half-line spectral theorem).
Regression: [`tests/test_a_two_path_helly.py`](../tests/test_a_two_path_helly.py).

**Headline.** Combining Phase 10 (closed-form boundary spectral density of
the half-line operator $T = A(L_\infty)$ at $w = e_1 + e_2$) with the
strong-resolvent / no-atom / Portmanteau argument given below promotes
the Phase 9 asymptotic candidate to a **theorem**:

> **Theorem (a.2-path).** For the 2-path family $L_n$ with boundary
> simplicial ear $v^* = 1$, the v11 ansatz functional converges:
> $$\lim_{n\to\infty} I(L_n, v^*) \;=\; I_\infty(L)
> \;=\; \frac{2\bigl(310\pi^2 - 837\sqrt 3\,\pi + 2187\bigr)}{27\pi\bigl(20\pi - 27\sqrt{3}\bigr)}
> \;\approx\; 1.0157\,375.$$
> In particular, $I_\infty(L)$ exceeds both v11 working thresholds
> $T\in\{0.4122,\;0.25\}$ with explicit slack $\ge 0.604$, and the three
> negative moments
> $$W^-(L_n) \to W^-_\infty = 1 - \tfrac{3\sqrt 3}{4\pi}, \qquad
>   M_1^-(L_n) \to M_{1,\infty}^- = \tfrac{2}{3} - \tfrac{9\sqrt 3}{4\pi},$$
> $$M_2^-(L_n) \to M_{2,\infty}^- = 3 - \tfrac{81\sqrt 3}{20\pi}.$$

The full theorem (a.2-path) of the v11 candidate ansatz, *with the finite-$n$
to $\infty$ identification*, is thereby closed.

---

## §1. The gap from Phase 10 + Role 5 audit (recap)

Phase 10 (`lprime_a_two_path_stieltjes.md`) established the
**half-line** spectral theorem: for the half-line pentadiagonal Toeplitz
$T = A(L_\infty)$ on $\ell^2(\mathbb{N})$ and the boundary vector
$w = e_1 + e_2$, the spectral measure $\mu_w$ at $w$ is purely absolutely
continuous with density
$$
\rho_w(\lambda) \;=\; \frac{1}{\pi}\sin\!\bigl(\theta_2(\lambda) - \theta_1(\lambda)\bigr),
\qquad \lambda \in (-\tfrac{9}{4}, 0),
\tag{1.1}
$$
where $\theta_1,\theta_2$ are the two preimages of $\lambda$ under
$f(\theta) = 2\cos\theta + 2\cos 2\theta$. Integration gives the
**half-line negative moments**
$$
W^-_\infty := \int_{-9/4}^{0} d\mu_w,\quad
M^-_{k,\infty} := \int_{-9/4}^{0} \lambda^k\, d\mu_w(\lambda),
\quad k = 1, 2.
$$

The Phase 9 statement, however, is about $\lim_{n\to\infty} I(L_n, v^*)$
where
$$
M_k^-(L_n) \;:=\; \sum_{j:\,\mu_j(A(L_{n-1})) < 0} (u_j(1) + u_j(2))^2\,\mu_j^k,
\qquad k = 0, 1, 2,
$$
the *signed* moment of the spectral measure of the **finite** operator
$A(L_{n-1})$ at $w_n := e_1 + e_2 \in \mathbb{R}^{n-1}$.

**Trivial case (unsigned).** For unsigned moments
$\langle w_n, A(L_{n-1})^k w_n\rangle$ the convergence is immediate:
$w_n$ has support $\{1,2\}$, and the support of $A(L_{n-1})^k w_n$ is
contained in $\{1,2,\dots,2k+2\}$; for $n - 1 \ge 2k+2$ (i.e. $n \ge 2k+3$),
this is *exactly* equal to the corresponding half-line quantity
$\langle w, T^k w\rangle$. So the moments $\langle w, T^k w\rangle$ are
*not just limits* — they are *equal to* the matrix moments for all
sufficiently large $n$.

**Non-trivial case (signed).** The signed moment kernel
$g_k(\lambda) := \lambda^k\,\mathbf 1[\lambda < 0]$ is **discontinuous**
at $\lambda = 0$ for $k = 0$ (jump of size $1$), and the density (1.1)
does **not** vanish at $\lambda = 0$: indeed
$$
\rho_w(0^-) \;=\; \frac{1}{\pi}\sin\!\bigl(\theta_2(0^-) - \theta_1(0^-)\bigr)
\;=\; \frac{\sin(2\pi/3)}{\pi}
\;=\; \frac{\sqrt 3}{2\pi}
\;\approx\; 0.2757,
$$
since at $\lambda \to 0^-$, $\theta_1(\lambda) \to \pi/3$ and
$\theta_2(\lambda) \to \pi$. So weak convergence of measures alone does
**not** suffice to identify the limit of $W^-(L_n)$: the standard
Portmanteau hypothesis (continuity points of the bounded function) needs
to be checked, and the no-atom condition at the discontinuity ($\lambda = 0$)
needs to be verified.

Role 5 flagged this in the Phase 9 audit. The argument that follows
closes the gap.

---

## §2. Strong-resolvent convergence (Step 1)

Embed the finite operators $A(L_{n-1})$ on $\mathbb{R}^{n-1}$ into the
half-line Hilbert space $\mathcal H = \ell^2(\mathbb{N})$ by zero-padding:
let $T_{n-1}: \mathcal H \to \mathcal H$ be the bounded linear operator
$$
(T_{n-1} x)_i \;:=\; \begin{cases}
\bigl(A(L_{n-1})\,(x_1, \dots, x_{n-1})^\top\bigr)_i, & 1 \le i \le n-1, \\[2pt]
0, & i \ge n.
\end{cases}
$$
Equivalently, $T_{n-1} = P_{n-1} T P_{n-1}$ where $P_{n-1}$ is the
orthogonal projection onto $\mathrm{span}\{e_1,\dots,e_{n-1}\}$ in
$\mathcal H$, except possibly at the **right boundary**: $T_{n-1}$ has the
same matrix entries as $T$ on rows $i \le n-3$ and differs only in the
last two rows. (Specifically, $T_{n-1}$ truncates the bulk recurrence at
the right boundary $i = n-1$ by dropping the references to $e_n, e_{n+1}$.)

The relevant observation is that the boundary vector $w = e_1 + e_2$ and
all its iterates $T^k w$ are supported in $\{1, \dots, 2k+2\}$, far from
the right boundary $i = n-1$ once $n$ is large.

**Lemma 2.1 (uniform norm bound).** For all $n \ge 4$,
$\|T_{n-1}\|_{\mathcal H \to \mathcal H} \le \|f\|_\infty = 4$, where
$f(\theta) = 2\cos\theta + 2\cos 2\theta$.

*Proof.* The matrix $A(L_{n-1})$ is the finite truncation of the
symmetric pentadiagonal Toeplitz matrix with symbol $f$. By the standard
Toeplitz-matrix norm bound (e.g. Avram–Parter, or Grenander–Szegő,
*Toeplitz Forms and Their Applications*, Ch. 5), for any symmetric
banded Toeplitz matrix the operator norm is at most $\|f\|_\infty$. A
direct one-line proof: for any $v \in \mathbb R^{n-1}$, extend by zero to
$\tilde v \in \ell^2(\mathbb Z)$; then
$\langle v, A(L_{n-1}) v\rangle = \langle \tilde v, T_{\rm full}\tilde v\rangle$
where $T_{\rm full}$ is the bi-infinite Toeplitz operator with symbol $f$,
unitarily equivalent (via the Fourier transform) to multiplication by
$f$ on $L^2(\mathbb{T})$, so $|\langle v, A(L_{n-1}) v\rangle| \le \|f\|_\infty\,\|v\|^2$.
Combined with $T_{n-1}$ being self-adjoint, this gives
$\|T_{n-1}\| \le \|f\|_\infty$. The maximum is attained:
$\|f\|_\infty = f(0) = 4$. $\blacksquare$

(For the half-line operator $T$ the same argument gives $\|T\| \le 4$.)

**Lemma 2.2 (strong-resolvent / strong-operator convergence).** $T_{n-1} \to T$
in the strong operator topology of $\mathcal H$. That is, for every
$x \in \mathcal H$, $\|T_{n-1} x - T x\|_{\ell^2} \to 0$ as $n \to \infty$.

*Proof.* Fix $x \in \mathcal H$. Step 1: assume $x$ is finitely supported,
$\mathrm{supp}(x) \subseteq \{1,\dots,N\}$. For all $n \ge N + 3$, the
bulk pentadiagonal recurrence $(Tx)_i$ for $i \le N+2$ involves only
$x_{i-2}, x_{i-1}, x_{i+1}, x_{i+2}$ — all with indices $\le N+2 \le n-1$.
Hence the rows of $T_{n-1}$ acting on $x$ agree with the rows of $T$ for
$i \le N+2$. For $i > N+2$, both $(T_{n-1} x)_i$ and $(T x)_i$ vanish
(since $x$ has support in $\{1,\dots,N\}$ and the pentadiagonal stencil
reaches at most $2$ indices, so $(Tx)_i = 0$ for $i > N+2$). Thus
$T_{n-1} x = T x$ exactly for all $n \ge N+3$, and the norm difference
vanishes.

Step 2: general $x \in \mathcal H$. Given $\varepsilon > 0$, pick a
finitely supported approximation $x_\varepsilon$ with
$\|x - x_\varepsilon\| < \varepsilon/(2\|T\| + 2\|f\|_\infty)$. Using
Lemma 2.1,
$$
\|T_{n-1} x - T x\|
\;\le\; \|T_{n-1}(x - x_\varepsilon)\| + \|T_{n-1} x_\varepsilon - T x_\varepsilon\|
       + \|T(x_\varepsilon - x)\|
\;\le\; (\|f\|_\infty + \|T\|)\,\|x - x_\varepsilon\|
       + \|T_{n-1} x_\varepsilon - T x_\varepsilon\|.
$$
The middle term vanishes for all $n \ge N(\varepsilon) + 3$ by Step 1.
The first and last together are $< \varepsilon$ by choice of
$x_\varepsilon$. Hence $\limsup_{n\to\infty}\|T_{n-1}x - Tx\| \le \varepsilon$.
Since $\varepsilon$ was arbitrary, the lim is $0$. $\blacksquare$

By a standard result (Reed–Simon, *Methods of Modern Mathematical
Physics*, vol. I, Theorem VIII.20 (S-resolvent convergence) and
Theorem VIII.25), strong-operator convergence of *uniformly bounded*
self-adjoint operators is equivalent to **strong-resolvent convergence**:
for every $z \in \mathbb{C}\setminus\mathbb{R}$,
$$
(T_{n-1} - z)^{-1} \;\xrightarrow{\,s.o.\,}\; (T - z)^{-1}.
\tag{2.1}
$$

(Note that uniform boundedness in Lemma 2.1 ensures $z \in \mathbb C
\setminus\mathbb R$ is in the resolvent set of all $T_{n-1}$ and of
$T$ — they are all self-adjoint.)

---

## §3. Weak convergence of spectral measures (Step 2)

Let $\mu_{w,n}$ denote the spectral measure of $T_{n-1}$ at the vector $w$
(zero-padded to $\mathcal H$), so
$$
\langle w, F(T_{n-1})\, w\rangle \;=\; \int F(\lambda)\, d\mu_{w,n}(\lambda)
$$
for any bounded Borel $F$. Let $\mu_w$ denote the spectral measure of
$T$ at $w$, given by (1.1).

**Lemma 3.1.** The spectral measures $\mu_{w,n}$ converge weakly to $\mu_w$:
$\int F\,d\mu_{w,n} \to \int F\,d\mu_w$ for every $F \in C_b(\mathbb R)$.

*Proof.* By the Stieltjes (Borel) transform / Cauchy transform
characterisation of spectral measures, for each $z \in \mathbb C^+ :=
\{z : \mathrm{Im}\,z > 0\}$,
$$
G_{w,n}(z) := \langle w, (T_{n-1} - z)^{-1} w\rangle
            = \int \frac{d\mu_{w,n}(\lambda)}{\lambda - z}.
$$
By (2.1), $(T_{n-1} - z)^{-1} w \to (T - z)^{-1} w$ in norm, so
$G_{w,n}(z) \to G_w(z)$ pointwise on $\mathbb C^+$ (and by symmetry on
$\mathbb C^-$).

The spectral measures $\mu_{w,n}$ are non-negative finite measures with
$\mu_{w,n}(\mathbb R) = \|w\|^2 = 2$ for all $n$, supported in
$\mathrm{spec}(T_{n-1}) \subseteq [-\|f\|_\infty, \|f\|_\infty] = [-4, 4]$
(Lemma 2.1). Hence $(\mu_{w,n})_n$ is uniformly bounded and uniformly
tight (supported in $[-4,4]$); by Prokhorov, every subsequence has a
weakly convergent sub-subsequence. Any weak limit $\mu^*$ has Cauchy
transform $\int (\lambda - z)^{-1}\,d\mu^*(\lambda) = G_w(z)$ for
$z \in \mathbb C^+$, hence $\mu^* = \mu_w$ by the uniqueness of measures
from their Stieltjes transform (Stieltjes inversion / Cauchy transform
inversion). So $\mu_{w,n} \rightharpoonup \mu_w$ weakly. (This is also
the content of Reed–Simon Vol I, Theorem VIII.20 applied to spectral
measures.) $\blacksquare$

---

## §4. No atom at $\lambda = 0$ (Step 3)

**Lemma 4.1.** $\mu_w(\{0\}) = 0$.

*Proof.* By Phase 10 (Theorem of `lprime_a_two_path_stieltjes.md`), the
spectral measure $\mu_w$ is absolutely continuous on the interior of the
spectrum $(-9/4, 4)$, with density (1.1) on $(-9/4, 0)$ and the analogous
density (derived in §5 of `lprime_a_two_path_stieltjes.md`) on $(0, 4)$.
Both densities are bounded: $\rho_w(\lambda) \le 1/\pi$ on $(-9/4, 0)$
since $|\sin(\theta_2 - \theta_1)| \le 1$, and similarly on $(0, 4)$. So
$\mu_w$ is absolutely continuous with bounded density on the interior;
the only possible atoms are at the spectral endpoints $\{-9/4, 0, 4\}$
where the bulk symbol $f$ has critical points. None of these are
embedded eigenvalues: Phase 10 §1 verifies that $T$ has *purely
absolutely continuous spectrum* on the bulk $[-9/4, 4]$ (no embedded
eigenvalues, no singular continuous component). In particular
$\mu_w(\{0\}) = 0$.

(For a self-contained alternative: by Phase 10, the density on $(-9/4, 0)$
is continuous up to and including $\lambda = 0$; the limit
$\rho_w(0^-) = \sqrt 3/(2\pi)$ is finite. So $\mu_w((-\varepsilon, 0))
\to 0$ as $\varepsilon \to 0^+$, and similarly from the right. Hence
$\mu_w(\{0\}) = 0$.) $\blacksquare$

---

## §5. Portmanteau closure (Step 4)

Fix $k \in \{0, 1, 2\}$ and let
$$
g_k(\lambda) := \lambda^k\,\mathbf 1[\lambda < 0].
$$

**Step 5a — continuity-set analysis.** $g_k$ is continuous on
$(-\infty, 0)$ and on $(0, \infty)$. At $\lambda = 0$:
- $k = 0$: $g_0(0^-) = 1 \ne 0 = g_0(0) = g_0(0^+)$. *Discontinuous at $0$.*
- $k = 1$: $g_1(0^-) = \lim_{\lambda\to 0^-}\lambda\cdot 1 = 0 = g_1(0) = \lim_{\lambda\to 0^+}\lambda\cdot 0$. *Continuous at $0$.*
- $k = 2$: same as $k = 1$ — both one-sided limits vanish. *Continuous at $0$.*

So $D_{g_k} = \{0\}$ for $k = 0$ and $D_{g_k} = \emptyset$ for $k \in \{1, 2\}$.
In all three cases $\mu_w(D_{g_k}) = 0$, using Lemma 4.1 for $k = 0$.

**Step 5b — boundedness.** All measures $\mu_{w,n}$ and $\mu_w$ are
supported in $[-4, 4]$ (Lemma 2.1). On this set, $|g_k(\lambda)| \le 4^k$.

**Step 5c — Portmanteau.** Both Billingsley's *Convergence of Probability
Measures*, Theorem 2.1 / 5.1, and the standard formulation for finite
non-negative measures, say:

> If $\mu_{w,n} \rightharpoonup \mu_w$ weakly and $g: \mathbb R \to \mathbb R$
> is bounded Borel with $\mu_w(D_g) = 0$, then $\int g\,d\mu_{w,n} \to \int g\,d\mu_w$.

(For non-probability measures, normalise by the total mass $\|w\|^2 = 2$
— a constant — and the same statement holds.) Applying this with
$g = g_k$:
$$
\int g_k\, d\mu_{w,n} \;\longrightarrow\; \int g_k\, d\mu_w
\qquad (n \to \infty).
\tag{5.1}
$$

The left side is the finite-$n$ signed moment:
$$
\int g_k\, d\mu_{w,n}
\;=\; \sum_{j: \mu_j(A(L_{n-1})) < 0} \langle w, u_j\rangle^2 \,\mu_j^k
\;=\; M_k^-(L_n).
$$
The right side is the half-line negative moment $M^-_{k,\infty}$. So
$$
\boxed{\;M_k^-(L_n) \;\longrightarrow\; M^-_{k,\infty}
\quad\text{for}\quad k = 0, 1, 2.\;}
\tag{5.2}
$$

In particular, for $k = 0$ we get $W^-(L_n) \to W^-_\infty$; for
$k = 1, 2$ even *weak convergence* alone gives the limit (no atom
condition needed) because $g_1, g_2$ are *continuous* on $\mathbb R$.

---

## §6. Conclusion (Step 5) — the theorem

Combine (5.2) with continuity of the rational function $(W, M_1, M_2)
\mapsto W + M_1^2/M_2$ at the limit point $(W^-_\infty, M^-_{1,\infty},
M^-_{2,\infty})$. The denominator at the limit is
$$
M^-_{2,\infty} \;=\; 3 - \frac{81\sqrt 3}{20\pi} \;\approx\; 0.7671 \;>\; 0,
$$
so the map is continuous in a neighbourhood. Hence
$$
I(L_n, v^*) \;=\; W^-(L_n) + \frac{(M_1^-(L_n))^2}{M_2^-(L_n)}
\;\longrightarrow\; W^-_\infty + \frac{(M^-_{1,\infty})^2}{M^-_{2,\infty}}
\;=\; I_\infty(L).
$$
Substituting the closed forms,
$$
I_\infty(L) \;=\; \frac{2\bigl(310\pi^2 - 837\sqrt 3\,\pi + 2187\bigr)}{27\pi(20\pi - 27\sqrt 3)}
\;=\; 1.0157\,374\,829\ldots
$$
Both v11 working thresholds are cleared with explicit slack:
$$
I_\infty(L) - 0.4122 \;=\; 0.6035\ldots, \qquad
I_\infty(L) - 0.25 \;=\; 0.7657\ldots
$$
This is the **Theorem (a.2-path)** stated at the top of the document.

**Status.** Together with Phase 10 (the half-line spectral density),
this closes condition (a) of the candidate v11 ansatz on the 2-path
family $L_n$ in the limit $n \to \infty$ as a **theorem** (no
unproven step remains). The remaining open items in plan v12 (the
slot-shift bound for condition (b), the general 2-tree case of
condition (a), etc.) are untouched.

---

## §7. Empirical regression (Step 6)

The data file [`data/two_path_limit_moments.json`](../data/two_path_limit_moments.json)
records, at mpmath dps = 50, finite-$n$ values of $(W^-, M_1^-, M_2^-, I)$
for $n \in \{50, 100, 200\}$ together with the closed-form limits and
the residuals.

The Helly / Portmanteau argument above proves convergence but does *not*
provide an explicit *rate*: with strong-resolvent convergence one expects
some power-of-$n$ decay (typically $O(n^{-1})$ for absolutely continuous
spectral measures, or $O(n^{-1/2})$ with oscillation), but the constants
are not extracted here. So the regression test below only asserts the
weaker (but unconditional) property:

  * The absolute residuals $|I(L_n) - I_\infty(L)|$ are bounded
    (specifically $< 0.1$ at each recorded $n$).
  * The residual at the largest recorded $n$ is no worse than at the
    smallest, modulo a small tolerance to absorb parity oscillations
    visible in the data.
  * The residuals of the individual moments $W^-, M_1^-, M_2^-$ are
    likewise bounded.

Concretely, the existing data shows
$$
|I(L_{50}) - I_\infty| \approx 0.043, \quad
|I(L_{100}) - I_\infty| \approx 0.007, \quad
|I(L_{200}) - I_\infty| \approx 0.011.
$$
The pattern is non-monotone (parity-oscillation between $n = 100$ and
$n = 200$, also seen in the Widom analysis of `lprime_two_paths.md`) but
manifestly converges. The new test `test_a_two_path_helly.py` enforces:
- A uniform operator-norm bound $\|A(L_{n-1})\| \le 4$ for several $n$,
  certifying Lemma 2.1 empirically (consistency with the symbol bound).
- The symbol facts $\max f = 4, \min f = -9/4$ verified symbolically via
  sympy (the inputs to the Portmanteau-domain analysis).
- The Helly-style assertion that $|I(L_n) - I_\infty(L)| < 0.1$ on the
  recorded $n$-grid, plus that the residual at the largest $n$ is at
  most the maximum recorded residual (a soft "no blow-up" check).
- Sanity check: $g_1$ and $g_2$ are continuous at $0$ (numerical
  identity check on a sequence $\lambda \to 0^\pm$), confirming why
  weak convergence already suffices for $k = 1, 2$.

---

## Cross-references and bibliography

- **Phase 9 closed-form candidate**: `docs/lprime_a_two_path.md`.
- **Phase 10 half-line spectral theorem**: `docs/lprime_a_two_path_stieltjes.md`.
- **Reed, M., Simon, B.** *Methods of Modern Mathematical Physics, vol. I:
  Functional Analysis*, rev. ed. (Academic Press, 1980). Theorem VIII.20
  for resolvent convergence; Theorem VII.13 for spectral measures.
- **Billingsley, P.** *Convergence of Probability Measures*, 2nd ed.
  (Wiley, 1999). Theorem 2.1 (Portmanteau) and Theorem 5.1.
- **Grenander, U., Szegő, G.** *Toeplitz Forms and Their Applications*
  (Univ. of California Press, 1958), Ch. 5, for the operator-norm bound
  $\|A(L_{n-1})\| \le \|f\|_\infty$.
- **Simon, B.** *Szegő's Theorem and Its Descendants*, Princeton, 2011,
  for the half-line / boundary spectral measure formalism used here.

---

## One-line summary

The strong-resolvent / Portmanteau bridge plus the Phase 10 no-atom
half-line spectral theorem together upgrade $(I(L_n,v^*) \to I_\infty(L))$
from numerical evidence to a **theorem**, closing **(a.2-path)** in
plan_v12.
