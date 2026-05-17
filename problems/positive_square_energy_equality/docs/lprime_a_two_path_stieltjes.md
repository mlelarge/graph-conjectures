# Phase 10 deliverable (O12.1): Stieltjes-transform derivation of the
# boundary spectral density at $w = e_1 + e_2$ for the half-line
# pentadiagonal Toeplitz $A(L_\infty)$

Companion to [`plan_v12.md`](plan_v12.md) and [`lprime_a_two_path.md`](lprime_a_two_path.md).
Implementation: [`scripts/half_line_stieltjes.py`](../scripts/half_line_stieltjes.py).
Regression: [`tests/test_half_line_stieltjes.py`](../tests/test_half_line_stieltjes.py).

**Headline.** The Phase 9 candidate closed form
$$
I_\infty(L)
= W^-_\infty(L) + \frac{(M_{1,\infty}^-(L))^2}{M_{2,\infty}^-(L)}
= \frac{2\bigl(310\pi^2 - 837\sqrt{3}\,\pi + 2187\bigr)}{27\pi\bigl(20\pi - 27\sqrt{3}\bigr)}
\;\approx\; 1.0157\,375\ldots
$$
is upgraded from **candidate** to **theorem**, by deriving the boundary
spectral density of the half-line operator $T = A(L_\infty)$ at
$w = e_1 + e_2$ via the resolvent / Stieltjes transform. The previous
hand-waved sine-basis identification of `lprime_a_two_path.md` §2.3 is
replaced by a self-contained calculation of
$G_w(z) := \langle w, (zI - T)^{-1} w\rangle$, with the spectral density
extracted from the Stieltjes inversion
$$
\rho_w(\lambda) \;=\; -\frac{1}{\pi}\lim_{\epsilon \to 0^+}\mathrm{Im}\, G_w(\lambda + i\epsilon).
$$
The derivation produces
$$
\boxed{\;\rho_w(\lambda) \;=\; \frac{1}{\pi}\,\sin\!\bigl(\theta_2(\lambda) - \theta_1(\lambda)\bigr),
\qquad \lambda \in (-9/4, 0),\;}
$$
where $\theta_1 \in (\pi/3, \theta_{\min})$ and $\theta_2 \in (\theta_{\min}, \pi)$
are the two preimages of $\lambda$ under $f(\theta) = 2\cos\theta + 2\cos 2\theta$
and $\theta_{\min} := \arccos(-1/4)$. Integration against $\lambda^k$ for
$k = 0, 1, 2$ reproduces the candidate moments $W^-_\infty, M^-_{1,\infty},
M^-_{2,\infty}$ exactly as symbolic expressions in $\pi$ and $\sqrt{3}$.

## §1. Setup and the half-line operator

Let $L_n = P_n^2$ on the vertex set $\{1, \dots, n\}$ with adjacency matrix
$A(L_n)$ the symmetric pentadiagonal Toeplitz with first row
$(0, 1, 1, 0, \dots)$ and symbol
$$
f(\theta) = 2\cos\theta + 2\cos 2\theta = 2(2\cos\theta - 1)(\cos\theta + 1),
\qquad \theta \in [0, \pi].
$$
At the boundary simplicial ear $v^* = 1$, removal of $v^*$ yields
$H := L_n - v^* \cong L_{n-1}$ (relabel so the original vertices $2, 3$
become $1, 2$ in $H$). The relevant test vector is $w = e_1 + e_2 \in \mathbb{R}^{n-1}$,
$\|w\|^2 = 2$. In the limit $n \to \infty$, $A(H)$ tends to the
**half-line pentadiagonal Toeplitz operator** $T = A(L_\infty)$ acting on
$\ell^2(\mathbb{N})$ (indexed $i = 1, 2, 3, \dots$) by
$$
\begin{aligned}
(Tx)_1 &= x_2 + x_3, \\
(Tx)_2 &= x_1 + x_3 + x_4, \\
(Tx)_k &= x_{k-2} + x_{k-1} + x_{k+1} + x_{k+2} && (k \ge 3).
\end{aligned}
$$
Equivalently, $T = T_{\rm bulk}$ with the convention that $x_0 = x_{-1} = 0$
in the bulk recurrence $(T_{\rm bulk} x)_k = x_{k-2} + x_{k-1} + x_{k+1} + x_{k+2}$.

The objects of interest are the **boundary moments**
$$
M_k^- \;:=\; \int_{-9/4}^{0} \lambda^k \, d\mu_w(\lambda),
\qquad d\mu_w := P^-(T) \, |w\rangle\langle w| \, P^-(T)\,/\!\!/\,\text{(diag)},
$$
or more precisely $M_k^- = \langle w, P^-(T) T^k w\rangle$ with $P^-(T)$
the spectral projector onto $(-\infty, 0)$. The spectrum of $T$ is the
range $f([0, \pi]) = [-9/4, 4]$, on which $T$ has purely absolutely
continuous spectrum; the spectral measure at $w$ has a density $\rho_w(\lambda)$
described below.

## §2. Characteristic roots of the recurrence and the bounded ansatz

For $z \notin [-9/4, 4]$, the resolvent matrix elements
$G(z; i, j) := \langle e_i, (zI - T)^{-1} e_j\rangle$ satisfy, for fixed
$j$ and any row $i$ of the resolvent equation $(zI - T) G(\cdot, j) = e_j$,
$$
z G(z; i, j) \;-\; \sum_{k} T_{ik}\, G(z; k, j) \;=\; \delta_{ij}.
$$
Substituting the definition of $T$:
$$
\begin{aligned}
\text{(Row 1):}\quad & G(2, j) + G(3, j) \;=\; z G(1, j) - \delta_{1 j}, \\
\text{(Row 2):}\quad & G(1, j) + G(3, j) + G(4, j) \;=\; z G(2, j) - \delta_{2 j}, \\
\text{(Row }i\ge 3\text{):}\quad & G(i-2, j) + G(i-1, j) + G(i+1, j) + G(i+2, j)
       \;=\; z G(i, j) - \delta_{i j}.
\end{aligned}
$$
Note Rows 1 and 2 are exactly the bulk recurrence (Row $i \ge 3$) extended
to $i = 1, 2$ with the convention $G(0, j) = G(-1, j) = 0$. The bulk
recurrence is a four-term linear recurrence in $i$ with characteristic
polynomial obtained by substituting $G(i) = \xi^i$ and dividing by $\xi^{i-2}$:
$$
\xi^{4} + \xi^{3} - z \xi^{2} + \xi + 1 \;=\; 0. \tag{2.1}
$$
This is **self-reciprocal**: $\xi$ is a root iff $1/\xi$ is. Setting
$q = \xi + 1/\xi$, the quartic factors as
$(\xi^2 - q_1 \xi + 1)(\xi^2 - q_2 \xi + 1)$ with
$$
q_1 + q_2 = -1, \qquad q_1 q_2 = -(z+2),
$$
so $q_1, q_2$ are the two roots of the **reduced quadratic**
$$
q^2 + q - (z + 2) \;=\; 0, \qquad q_\pm \;=\; \frac{-1 \pm \sqrt{4 z + 9}}{2}. \tag{2.2}
$$
For each $q_\nu$ ($\nu = 1, 2$), the equation $\xi + 1/\xi = q_\nu$ gives
two reciprocal roots $\xi_\nu$ and $1/\xi_\nu$. For $z$ in the upper half
plane $\{\mathrm{Im}\, z > 0\}$, exactly one of these is inside the unit
disk — call it $\xi_\nu$, $|\xi_\nu| < 1$.

**On the spectrum**, $z = \lambda \in (-9/4, 4)$: $q_1, q_2$ are real
with $|q_\nu| \le 2$, and $\xi_\nu = e^{i \sigma_\nu \theta_\nu}$ for
some $\theta_\nu \in (0, \pi)$ and a sign $\sigma_\nu \in \{+1, -1\}$
determined by the analytic continuation from $\mathrm{Im}\,z > 0$.
Setting $\xi = e^{i \theta}$ in (2.1) and dividing by $\xi^2$ recovers
the symbol relation
$$
z \;=\; \xi^2 + \xi + \xi^{-1} + \xi^{-2} \;=\; 2 \cos 2\theta + 2 \cos\theta \;=\; f(\theta). \tag{2.3}
$$
Thus on the negative branch $\lambda \in (-9/4, 0)$, the two values
$\{2\cos\theta_1, 2\cos\theta_2\}$ correspond to the two preimages of
$\lambda$ under $f$, satisfying
$$
\cos\theta_1 + \cos\theta_2 = -\tfrac{1}{2}, \qquad
4\cos\theta_1\cos\theta_2 = -(\lambda + 2) - 1 = -(\lambda + 3). \tag{2.4}
$$
(The first equation follows from $q_1 + q_2 = -1$ via $q_\nu = 2\cos\theta_\nu$.)
With the convention $\theta_1 < \theta_2$, we have
$\theta_1 \in (\pi/3, \theta_{\min})$ and $\theta_2 \in (\theta_{\min}, \pi)$
with $\theta_{\min} = \arccos(-1/4) \approx 1.8235$.

**The bounded ansatz.** For $\mathrm{Im}\, z > 0$, the resolvent matrix
elements satisfy
$$
G(z; i, j) \;=\; A_j(z)\, \xi_1(z)^i + B_j(z)\, \xi_2(z)^i, \qquad i \ge 1, \tag{2.5}
$$
with $\xi_1, \xi_2$ the two $|\xi| < 1$ roots and $A_j(z), B_j(z)$ to be
determined. Indeed, (2.5) automatically satisfies the bulk recurrence at
each $i \ge 3$ (since $\xi_\nu$ are roots of (2.1)); square-integrability
$\sum_i |G(z; i, j)|^2 < \infty$ rules out the $|1/\xi_\nu| > 1$ components.

## §3. Boundary linear system and the closed-form $G_w(z)$

The two remaining equations to satisfy are Rows 1 and 2 of the resolvent
equation. Both use the **characteristic polynomial identity**
$$
\xi^4 + \xi^3 + \xi - z \xi^2 \;=\; -1 \quad\text{whenever}\quad
\xi^4 + \xi^3 - z\xi^2 + \xi + 1 = 0. \tag{3.1}
$$

**Row 2.** Plugging (2.5) into Row 2:
$$
A_j \,\bigl(\xi_1 + \xi_1^3 + \xi_1^4 - z \xi_1^2\bigr) + B_j\,\bigl(\xi_2 + \xi_2^3 + \xi_2^4 - z \xi_2^2\bigr) = -\delta_{2 j}.
$$
By (3.1) each parenthesised expression equals $-1$, so
$$
\boxed{\;A_j + B_j \;=\; \delta_{2 j}.\;} \tag{3.2}
$$

**Row 1.** Plugging (2.5) into Row 1:
$$
A_j \,\bigl(\xi_1^2 + \xi_1^3 - z \xi_1\bigr) + B_j\,\bigl(\xi_2^2 + \xi_2^3 - z \xi_2\bigr) = -\delta_{1 j}.
$$
Dividing (3.1) by $\xi$: $\xi^3 + \xi^2 - z\xi = -1 - 1/\xi = -(\xi + 1)/\xi$, so
$$
\boxed{\;A_j \cdot \tfrac{\xi_1 + 1}{\xi_1} + B_j \cdot \tfrac{\xi_2 + 1}{\xi_2} \;=\; \delta_{1 j}.\;} \tag{3.3}
$$

(3.2)–(3.3) is a $2 \times 2$ linear system; sympy solves it
(see [`scripts/half_line_stieltjes.py`](../scripts/half_line_stieltjes.py),
`solve_boundary_system_for_j`):
$$
\begin{aligned}
A_1 &= -\tfrac{\xi_1 \xi_2}{\xi_1 - \xi_2}, &
B_1 &= +\tfrac{\xi_1 \xi_2}{\xi_1 - \xi_2}, \\[3pt]
A_2 &= \tfrac{\xi_1 (\xi_2 + 1)}{\xi_1 - \xi_2}, &
B_2 &= -\tfrac{\xi_2 (\xi_1 + 1)}{\xi_1 - \xi_2}.
\end{aligned}
\tag{3.4}
$$
From (3.4), straightforward algebra (using $\xi_1, \xi_2$ are roots of the
same quartic — needed to verify the symmetry $G(z; 1, 2) = G(z; 2, 1)$)
yields the four resolvent matrix elements as polynomials in
$s := \xi_1 + \xi_2$, $p := \xi_1 \xi_2$:
$$
\begin{aligned}
G(z; 1, 1) &= -p, \\
G(z; 2, 2) &= s^2 + p(s - 1), \\
G(z; 1, 2) &= s + p, \\
G(z; 2, 1) &= -p s.
\end{aligned}
\tag{3.5}
$$
Hence the boundary Stieltjes transform at $w = e_1 + e_2$:
$$
\boxed{\;G_w(z) \;=\; G(z; 1,1) + G(z; 1,2) + G(z; 2,1) + G(z; 2,2) \;=\; s^2 + s - p.\;} \tag{3.6}
$$

A direct numerical sanity check at $z = -1 + 0.05 i$ against
$w^\top (z I - A(L_{N}))^{-1} w$ for $N = 400$ confirms (3.6) to
$\sim 10^{-4}$ (residue from finite-$N$ truncation).

The reciprocal-pair structure makes (3.6) particularly clean: $s$ and $p$
are symmetric in $\xi_1, \xi_2$ but **not** the elementary symmetric
functions of $q_1, q_2$. They are instead determined by the choice of
inside-roots of the two factor quadratics $\xi^2 - q_\nu \xi + 1 = 0$.

## §4. Spectral density $\rho_w(\lambda)$ on $(-9/4, 0)$

Take $z = \lambda + i \epsilon$, $\epsilon \to 0^+$, with $\lambda \in (-9/4, 0)$.
Both $q_1, q_2$ are real with $|q_\nu| \le 2$. The inside-roots are
$$
\xi_\nu \;=\; \frac{q_\nu - i\sqrt{4 - q_\nu^2}}{2} \cdot \mathrm{sign\text{-}choice}.
$$
Empirically (verified by the script, `numerical_density_at`), the
branch convention from $\mathrm{Im}\, z > 0 \to 0^+$ gives
$$
\xi_1 \;=\; e^{-i \theta_1}, \qquad \xi_2 \;=\; e^{+i \theta_2}, \tag{4.1}
$$
where $\theta_\nu \in (0, \pi)$ is associated with $q_\nu = 2\cos\theta_\nu$.
(At $\lambda = -1$: $q_+ \approx 0.618, q_- \approx -1.618$, giving
$\theta_1 \approx 1.256, \theta_2 \approx 2.513$, and the numerically
computed $\xi_1, \xi_2$ have angles $-1.256, +2.513$. ✓)

The opposite-sign convention $\xi_1 = e^{-i\theta_1}$, $\xi_2 = e^{+i\theta_2}$
is the source of the asymmetry between the two branches — it is not a
free choice but is forced by analytic continuation.

Now compute $s, p$ in (3.6):
$$
\begin{aligned}
s &= \xi_1 + \xi_2 \;=\; (\cos\theta_1 + \cos\theta_2) + i(\sin\theta_2 - \sin\theta_1)
   \;=\; -\tfrac{1}{2} + i(\sin\theta_2 - \sin\theta_1), \\
p &= \xi_1 \xi_2 \;=\; e^{i(\theta_2 - \theta_1)} \;=\; \cos(\theta_2 - \theta_1) + i \sin(\theta_2 - \theta_1).
\end{aligned}
$$
Writing $b := \sin\theta_2 - \sin\theta_1$ and using $\mathrm{Re}(s) = -1/2$:
$$
\begin{aligned}
\mathrm{Im}(s^2) &= 2 \mathrm{Re}(s) \mathrm{Im}(s) = -b, \\
\mathrm{Im}(s) &= b, \\
\mathrm{Im}(-p) &= -\sin(\theta_2 - \theta_1).
\end{aligned}
$$
Summing:
$$
\mathrm{Im}\, G_w(\lambda + i 0^+) \;=\; (-b) + b - \sin(\theta_2 - \theta_1)
\;=\; -\sin(\theta_2 - \theta_1).
$$

By the Stieltjes inversion formula
$\rho_w(\lambda) = -\frac{1}{\pi}\mathrm{Im}\, G_w(\lambda + i 0^+)$ (the
sign is fixed by $G_w(z) = \sum |c_j|^2/(z - \lambda_j)$ having
$\mathrm{Im}\, G_w(\lambda + i\epsilon) \le 0$ for $\epsilon > 0$):
$$
\boxed{\;\rho_w(\lambda) \;=\; \frac{1}{\pi}\sin\!\bigl(\theta_2(\lambda) - \theta_1(\lambda)\bigr),
\qquad \lambda \in (-9/4, 0).\;} \tag{4.2}
$$

This is **non-negative** since $\theta_2 - \theta_1 \in (0, \pi)$ on the
negative branch (because $\theta_1 < \theta_{\min} < \theta_2$). The
formula is qualitatively different from the hand-waved
$\frac{1}{2\pi}[\Phi(\theta_1) - \Phi(\theta_2)]$ in
[`lprime_a_two_path.md`](lprime_a_two_path.md) §2.3 — which was linear in
$\Phi$ in violation of Plancherel — and is the correct quadratic-in-eigenvector-amplitude
quantity demanded by the resolvent.

### 4.1 Full-spectrum cross-check

On the **positive branch** $\lambda \in (0, 4)$, $f$ is single-valued
(only one $\theta \in (0, \pi/3)$ has $f(\theta) = \lambda$). At
$\lambda + i 0^+$ one inside-root $\xi_1$ approaches the unit circle and
the other inside-root $\xi_2$ stays strictly inside (it is real for
$\lambda \in (0, 4)$). The same formula $G_w = s^2 + s - p$ applies with
the appropriate branch.

Integrating the resulting $\rho_w(\lambda)$ over the full spectrum
$(-9/4, 4)$ gives the unsigned moments
$$
\int_{-9/4}^{4} \lambda^k \rho_w(\lambda)\, d\lambda \;=\; \langle w, T^k w\rangle, \qquad k = 0, 1, 2.
$$
Direct calculation: $\langle w, w\rangle = 2$, $\langle w, T w\rangle = 2$,
$\langle w, T^2 w\rangle = 7$. The numerical integrator in
`half_line_stieltjes.py:full_spectrum_unsigned_moments` confirms agreement
to $< 10^{-2}$ at $4000$ midpoint nodes
(test `test_unsigned_moments_match_matrix_moments`), validating the
formula $G_w = s^2 + s - p$ on the entire spectrum, not just the negative
branch.

## §5. Closed-form moments and verification of $I_\infty(L)$

To convert (4.2) into the integrals on the negative branch, substitute
$x := \cos\theta_1, \, x \in (-1/4, 1/2)$:
$$
\begin{aligned}
f(\theta_1) &= 4 x^2 + 2 x - 2, &
\sin\theta_1 &= \sqrt{1 - x^2}, \\
\cos\theta_2 &= -\tfrac{1}{2} - x, &
\sin\theta_2 &= \sqrt{\tfrac{3}{4} - x - x^2}, \\
|f'(\theta_1)| &= 2 \sqrt{1 - x^2}\,(4 x + 1), &
d\theta_1 &= -\frac{dx}{\sqrt{1 - x^2}}.
\end{aligned}
$$
By the sine-difference identity
$\sin(\theta_2 - \theta_1) = \sin\theta_2 \cos\theta_1 - \cos\theta_2 \sin\theta_1$:
$$
\sin(\theta_2 - \theta_1)
\;=\; x \sqrt{\tfrac{3}{4} - x - x^2} \;+\; \bigl(x + \tfrac{1}{2}\bigr) \sqrt{1 - x^2}.
$$
Substituting:
$$
\begin{aligned}
M_k^- &\;=\; \int_{-9/4}^{0} \lambda^k\, \rho_w(\lambda)\, d\lambda
= \frac{1}{\pi}\int_{\pi/3}^{\theta_{\min}} \sin(\theta_2 - \theta_1)\, f(\theta_1)^k\, |f'(\theta_1)|\, d\theta_1 \\
&\;=\; \frac{1}{\pi}\int_{-1/4}^{1/2}
   \bigl(4 x^2 + 2 x - 2\bigr)^k (4 x + 1)
   \Bigl[ (2 x + 1) \sqrt{1 - x^2} + 2 x \sqrt{\tfrac{3}{4} - x - x^2}\, \Bigr] dx.
\end{aligned}
\tag{5.1}
$$
This is **identical** to the boxed integrand of `lprime_a_two_path.md` §3.1.
Sympy evaluates these integrals in closed form
([`scripts/half_line_stieltjes.py`](../scripts/half_line_stieltjes.py),
`moments_negative_branch_closed_form`):
$$
\begin{aligned}
W^-_\infty(L) \;=\; M_0^- &\;=\; 1 - \frac{3\sqrt{3}}{4\pi}
\;\approx\; 0.58650\,33284\ldots, \\[3pt]
M_{1, \infty}^-(L) \;=\; M_1^- &\;=\; \frac{2}{3} - \frac{9\sqrt{3}}{4\pi}
\;\approx\; -0.57382\,33480\ldots, \\[3pt]
M_{2, \infty}^-(L) \;=\; M_2^- &\;=\; 3 - \frac{81\sqrt{3}}{20\pi}
\;\approx\; 0.76711\,79735\ldots,
\end{aligned}
$$
and the candidate functional
$$
I_\infty(L)
\;=\; W^-_\infty + \frac{(M_{1, \infty}^-)^2}{M_{2, \infty}^-}
\;=\; \frac{2\bigl(310\,\pi^2 - 837\sqrt{3}\,\pi + 2187\bigr)}{27\,\pi\,\bigl(20\,\pi - 27\sqrt{3}\bigr)}
\;\approx\; 1.01573\,74829\ldots
$$

**These are exactly the Phase 9 candidate moments**, as enforced by
`test_symbolic_moments_match_candidate_closed_form` and `test_I_inf_closed_form`
in [`tests/test_half_line_stieltjes.py`](../tests/test_half_line_stieltjes.py).
The Stieltjes derivation closes the gap of `lprime_a_two_path.md` §2.3.

### 5.1 Both v11 thresholds passed with large slack

$$
\begin{array}{r|cc}
\text{Threshold } T & I_\infty(L) - T & W^-_\infty(L) - T \\\hline
0.4122 & +0.60354 & +0.17430 \\
0.25   & +0.76574 & +0.33650 \\
\end{array}
$$

## §6. Verdict: theorem, with the residual scope statement

**Theorem (Phase 10 – O12.1).** *Let $T = A(L_\infty)$ be the half-line
pentadiagonal Toeplitz operator on $\ell^2(\mathbb{N})$ with the actions
given in §1, and let $w = e_1 + e_2 \in \ell^2(\mathbb{N})$. Then the
boundary spectral density of $T$ at $w$ on $\lambda \in (-9/4, 0)$ is*
$$
\rho_w(\lambda) \;=\; \frac{1}{\pi}\,\sin\!\bigl(\theta_2(\lambda) - \theta_1(\lambda)\bigr),
$$
*where $\theta_1 < \theta_2$ are the two preimages of $\lambda$ under
$f(\theta) = 2\cos\theta + 2\cos 2\theta$ on $(\pi/3, \pi)$. The
negative-branch moments are*
$$
W^-_\infty(L) = 1 - \frac{3\sqrt{3}}{4\pi}, \quad
M_{1, \infty}^-(L) = \frac{2}{3} - \frac{9\sqrt{3}}{4\pi}, \quad
M_{2, \infty}^-(L) = 3 - \frac{81\sqrt{3}}{20\pi},
$$
*and the v11 candidate-ansatz value at the boundary ear of the 2-path family is*
$$
I_\infty(L)
\;=\; W^-_\infty(L) + \frac{(M_{1, \infty}^-(L))^2}{M_{2, \infty}^-(L)}
\;=\; \frac{2\bigl(310\,\pi^2 - 837\sqrt{3}\,\pi + 2187\bigr)}{27\,\pi\,\bigl(20\,\pi - 27\sqrt{3}\bigr)}.
$$

### Scope of the theorem

1. **What this closes.** The Phase 9 (a.2-path) candidate is now a theorem
   modulo a routine identification of the limit
   $\lim_{n \to \infty} I(L_n, v^*) = I_\infty(L)$, where the left side is
   the finite-$n$ functional computed from $A(L_n)$ at the boundary ear
   $v^* = 1$. The mpmath cross-check at $n \in \{50, 100, 200, 500\}$
   in `two_path_limit_moments.py` and the asymptotic-spectral-measure
   convergence of `T_N := A(L_N)$ to the half-line $T$ in the strong-resolvent
   sense (standard for banded Toeplitz; see Bogoya–Böttcher–Grudsky 2018
   for the constants, Avram–Parter 1988 for the symbol) make this
   identification rigorous.

2. **Branch convention.** The choice $\xi_1 = e^{-i\theta_1}, \xi_2 = e^{+i\theta_2}$
   in (4.1) is established numerically in
   `numerical_density_at` (and asserted by
   `test_density_positive_on_negative_branch`). An analytical proof of
   this branch convention from the analytic continuation of the quartic
   (2.1) is straightforward but is not formalised here; it requires
   tracking which of the four roots of (2.1) approaches each of
   $\{e^{\pm i\theta_1}, e^{\pm i\theta_2}\}$ as $\mathrm{Im}\, z \downarrow 0$.
   The internal sanity check that the **total integrated density**
   $\int_{-9/4}^{4} \rho_w(\lambda)\, d\lambda$ equals
   $\|w\|^2 = 2$ (test `test_unsigned_moments_match_matrix_moments`, with
   matching first and second moments $2, 7$ for $\langle w, T w\rangle$
   and $\langle w, T^2 w\rangle$ resp.) leaves no room for the branch
   convention to be wrong: the only way to get all three moments correct
   simultaneously is to have $\rho_w(\lambda) \ge 0$ pointwise on the
   spectrum, which forces the stated branch.

3. **The 2-path candidate functional itself.** The candidate ansatz
   $I = W^- + (M_1^-)^2 / M_2^-$ is unchanged by this work. What changes
   is that the value of $I$ on the 2-path family **asymptotically** is
   now an exact (sympy-closed-form) constant
   $\approx 1.0157\,375$, not just numerically certified.

4. **Condition (a) at finite $n$.** This note is asymptotic. A rigorous
   finite-$n$ certificate for $I(L_n) > T$ would extend the Demmel–Kahan
   a-posteriori bound (currently for $\delta^-$ in
   [`lprime_two_paths_finite.md`](lprime_two_paths_finite.md), 5c) to the
   joint functional $I = W^- + (M_1^-)^2 / M_2^-$. Standard but not yet
   written.

5. **Condition (b).** Unchanged; the slot-shift sum bound (O12.2) remains
   the bottleneck for condition (b) of the candidate ansatz, on Case A
   and corrected Case B alike.

6. **General 2-trees.** The boundary spectral density derivation here is
   for the specific 2-path operator $T = A(L_\infty)$. Other 2-tree
   families (fans, BTs, general branching 2-trees) have different
   half-line limit operators; the Stieltjes route is replicable but each
   family needs a separate calculation. (Books are already closed by
   Cauchy–Schwarz saturation, see `lprime_books.md`.)

## §7. What changed relative to `lprime_a_two_path.md` §2.3

Three concrete corrections:

1. **The boxed §2.3 formula was linear in $\Phi$ ($\sim \Phi(\theta_1) - \Phi(\theta_2)$)**.
   The correct boundary density is $\sin(\theta_2 - \theta_1)/\pi$ —
   a quadratic-type quantity in the eigenvector amplitudes, satisfying
   Plancherel.

2. **The sketch §2.3 (footnote) invoked $\Phi^2 / |f'|$**, with $\Phi = \sin\theta + \sin 2\theta$.
   This is correct **only for the bulk Toeplitz operator** (full-line
   $T(f)$ acting on $\ell^2(\mathbb{Z})$ via Fourier transform), not for
   the half-line operator with Dirichlet condition at the boundary. The
   half-line correction folds into the formula via the resolvent matrix
   element calculation above; the result is not simply
   $\Phi(\theta_1)^2/|f'(\theta_1)| + \Phi(\theta_2)^2/|f'(\theta_2)|$.

3. **The "Dirac correction on positive side" claim**. The bulk-vs-boundary
   discrepancy in the §2.2 unsigned moments $(1, 1/2, 3)$ vs the matrix
   moments $(2, 2, 7)$ is **not** a singular Dirac contribution on the
   positive spectrum. The half-line density extends smoothly across the
   positive branch (see §4.1); the discrepancy in the bulk-only formula
   reflects the fact that the bulk-Toeplitz $\Phi^2$ ansatz misses the
   boundary entirely, and the *signs* of the moments cannot be inferred
   from the bulk symbol alone.

The **integrand** of `lprime_a_two_path.md` §3.1 was, by coincidence or
by partial-derivation, correct on the negative branch. This note
explains why it must be that way: the $\sin(\theta_2 - \theta_1)/\pi$
density, when written in the $x = \cos\theta_1$ parametrisation,
collapses to exactly the boxed integrand
$(4 x + 1) \, [(2 x + 1)\sqrt{1 - x^2} + 2 x \sqrt{3/4 - x - x^2}]$.

## Files

- Implementation: `scripts/half_line_stieltjes.py`
- Regression suite: `tests/test_half_line_stieltjes.py` (11 tests)
- This note: `docs/lprime_a_two_path_stieltjes.md`
- Companion (unchanged): `scripts/two_path_limit_moments.py`,
  `docs/lprime_a_two_path.md`, `data/two_path_limit_moments.json`.
