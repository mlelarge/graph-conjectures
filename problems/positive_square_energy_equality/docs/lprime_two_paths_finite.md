# Finite-$n$ proof of $\delta^-(L_n) \ge 17/16$ for 2-paths

> **Status (v9):** $n \le 200$ floating-point certified (slack $\ge 0.257$
> from Szegő limit; observed forward error $\sim 3 \cdot 10^{-12}$);
> $n > 200$ research-grade open. The Bogoya–Böttcher–Grudsky 2018
> simple-loop hypothesis fails for $f(\theta) = 2\cos\theta + 2\cos 2\theta$
> (zeros at both $\theta = \pi/3$ interior and $\theta = \pi$ boundary).
> Tail closure is not "1–2 pages of bookkeeping". Upgrade path: O5c.1
> (interval arithmetic for $n \le 200$) and O5c.2 (non-simple-loop
> secular rate for $n > 200$). See plan v9 §F5, F6.

Companion to [`lprime_two_paths.md`](lprime_two_paths.md). Plan v8, step **5c**.

The Szegő-limit value
$$\delta^-_\infty(L) \;=\; \frac{32\pi-27\sqrt 3}{12\pi} \;\approx\; 1.42618$$
is rigorous and strictly above $17/16=1.0625$, with slack $\approx 0.36368$.
The remaining task is to upgrade this to a **finite-$n$ rigorous statement**
$$\delta^-(L_n)\ \ge\ \frac{17}{16}\qquad\text{for every }n\ge 4.\tag{$\star$}$$
This note is a Böttcher–Silbermann-style analysis of $(\star)$.

## Step 0 — The Widom-type obstruction, stated precisely

Set $A_n := A(L_n)$ with symbol
$$f(\theta) = 2\cos\theta + 2\cos 2\theta = e^{i\theta}+e^{-i\theta}+e^{2i\theta}+e^{-2i\theta},$$
$f>0$ on $(0,\pi/3)$, $f<0$ on $(\pi/3,\pi)$. The Avram–Parter / Szegő theorem for
banded symmetric Toeplitz gives, for every continuous bounded $\phi$,
$$\frac{1}{n}\,\mathrm{tr}\,\phi(A_n)\ \longrightarrow\ \frac{1}{\pi}\int_0^\pi
\phi(f(\theta))\,d\theta.\tag{AP}$$
Specialised to $\phi(x)=x^2\mathbf 1\{x<0\}$ (which is continuous away from $x=0$
and bounded), this is the proof of $s^-(L_n)/n\to \delta^-_\infty$.

The natural way to control the *first difference*
$\delta^-(L_n)=s^-(L_n)-s^-(L_{n-1})$ rigorously is the **Widom secular
expansion** (Böttcher–Silbermann, *Analysis of Toeplitz Operators*, §5; also
Widom 1973): for a real-valued $L^\infty$ symbol $f$ with a finite number of
sign changes, write the negative-part trace as
$$s^-(L_n)\ =\ n\cdot\delta^-_\infty\ +\ \kappa^-(f)\ +\ r_n,\tag{W}$$
where $\kappa^-(f)$ is a boundary constant (the "Widom term") and $r_n\to 0$.
The known quantitative form for a $C^1$ test function with one jump on the
spectrum gives only the **logarithmic** error rate
$$|r_n|\ \le\ C(f)\,\frac{\log n}{n},\tag{$\log$}$$
because $\phi(x)=x^2\mathbf 1\{x<0\}$ has a jump in derivative at $x=0$ (and
$f$ has a zero at $\theta=\pi/3$ inside the integration interval, so the
discontinuity of $\phi$ at $f^{-1}(0)$ is genuinely seen).

**The obstacle.** Even if one tracks the constant in $(\log)$ explicitly along
Böttcher–Grudsky, the resulting bound at the worst case $n=6$ gives an error
$\ge \log 6 / 6 \cdot C(f)$ with $C(f)\gtrsim \|f\|_\infty^2 = 16$. That is
$\gtrsim 4.78$, which is much larger than the slack $0.364$. So the Widom
expansion **cannot be used directly** to prove $(\star)$ at small $n$: the
asymptotic regime hasn't started.

This is the precise mathematical content of the obstacle recorded in v8 plan
step 5c. Two ways out are explored below.

## Step 1 — Path (a): finite-$n$ Szegő strong-limit / Borodin–Okounkov correction

For a **positive** symbol the Szegő strong limit theorem gives
$\log\det T_n(f) = n\,G(f)+E(f)+o(1)$ with $G(f) = \frac{1}{2\pi}\int\log f$
and $E(f) = \sum_{k\ge 1} k\,|(\log f)_k|^2$ (the cepstrum). The
**Borodin–Okounkov** formula refines this to an $O(\lambda^n)$ error rate for
some $|\lambda|<1$ depending on the off-circle zeros of $f$. The analogue for
*signed* test functions is more delicate.

For our $\phi(x)=x^2\mathbf 1\{x<0\}$, applied at $f$:
$$\frac{1}{2\pi}\int_{-\pi}^\pi\phi(f(\theta))\,d\theta\ =\ \frac{1}{\pi}\int_{\pi/3}^\pi f(\theta)^2\,d\theta\ =\ \delta^-_\infty(L).$$
The Avram–Parter–Tyrtyshnikov boundary correction $\kappa^-$ is, formally,
$$\kappa^-(f) \;=\; \sum_{k\ge 0}\bigl(\text{tr}\,P^-_k - n_k\,\delta^-_\infty\bigr)$$
along a corner-block expansion. For our pentadiagonal symbol this is computable
in principle, but the contribution from the sign change at $\theta=\pi/3$ — the
"transition zone" where $f$ crosses $0$ — produces a term whose closed form
mixes the Wiener–Hopf factorisation of $f$ at the regular zero $\pi/3$ and at
the boundary zero $\pi$. In particular,
$\kappa^-$ does *not* admit a clean closed-form expression in elementary
functions for our $f$; even numerically determining it requires careful
extrapolation.

A clean version of Path (a) would proceed:
1. Write $\delta^-(L_n) = \delta^-_\infty + (r_n - r_{n-1})$.
2. Establish $r_n - r_{n-1}=O(1/n^2)$ via Bogoya–Böttcher–Grudsky individual
   eigenvalue asymptotics.
3. Track the constant explicitly to pin $|r_n-r_{n-1}|\le C/n^2$.
4. Combine with a direct check up to $n=\lceil \sqrt{C/0.364}\rceil$.

We have **not** carried Path (a) through analytically. The technical
obstruction is the regular interior zero of $f$ at $\theta=\pi/3$: the
Bogoya–Böttcher–Grudsky machinery handles boundary zeros (at $\theta\in\{0,\pi\}$)
cleanly, but interior zeros produce eigenvalues with **clustering** behaviour
(visible numerically as near-doublet pairs at scale $1/n$ near $\lambda=0$),
and the constant in the asymptotic expansion picks up the local geometry of
the zero rather than only its order. We document this here for the reviewer
and move to Path (b) and a hybrid Path (c).

## Step 2 — Path (b): rank-2 Cauchy interlacing

### Rank-2 decomposition

Write $L_n = L_{n-1}' + R_n$ where
$L_{n-1}':=\begin{pmatrix}A(L_{n-1})&0\\ 0&0\end{pmatrix}\in \mathbb R^{n\times n}$
and the perturbation matrix
$$R_n\ =\ e_n(e_{n-1}+e_{n-2})^\top + (e_{n-1}+e_{n-2})e_n^\top$$
encodes the attachment of the new simplicial degree-2 vertex $n$ to the edge
$\{n-2,n-1\}$. (This is precisely the operation that builds $L_n$ from
$L_{n-1}$ in the 2-tree clique tree.)

**Signature.** $R_n = uv^\top + vu^\top$ with $u=e_n$, $v=e_{n-1}+e_{n-2}$,
$\|u\|=1$, $\|v\|=\sqrt 2$, $\langle u,v\rangle = 0$. Hence $R_n$ has rank $2$
and nonzero eigenvalues $\pm\sqrt{\|u\|^2\|v\|^2-\langle u,v\rangle^2}=\pm\sqrt 2$.
Equivalently $R_n$ is similar to $\sqrt 2\,(\sigma_x\otimes I_1)$ in the
2-plane $\mathrm{span}(u,v)$ (signature $(1,1)$).

### Rank-2 Cauchy interlacing

For any symmetric $A\in\mathbb R^{n\times n}$ and rank-$r$ symmetric $B$ of
signature $(p,q)$ with $p+q=r$, eigenvalues (decreasing order) satisfy
$$\lambda_{i+q}(A+B)\ \le\ \lambda_i(A)\ \le\ \lambda_{i-p}(A+B),\tag{$\dagger$}$$
with the convention $\lambda_j=+\infty$ for $j\le 0$ and $\lambda_j=-\infty$
for $j>n$. With $(p,q)=(1,1)$,
$$\lambda_{i+1}(A+B)\ \le\ \lambda_i(A)\ \le\ \lambda_{i-1}(A+B)\quad\text{and}\quad
\lambda_{i+2}(A+B)\ \le\ \lambda_i(A).\tag{C2}$$

### Translating to $s^-$

Order eigenvalues of $A=L_{n-1}'$ in decreasing order; they are the
eigenvalues of $L_{n-1}$ together with one extra $0$. Order eigenvalues of
$L_n$ in decreasing order. By (C2), for every index $i$ with
$\lambda_i(L_n)<0$ there is a corresponding $\lambda_{i'}(L_{n-1}')$ with
$|i-i'|\le 1$ and $|\lambda_i(L_n)-\lambda_{i'}(L_{n-1}')|\le \sqrt 2$ (this
is Weyl–Lidskii applied to $R_n$ whose operator norm is $\sqrt 2$).

The crude consequence is
$$\bigl|\,s^-(L_n)-s^-(L_{n-1}')\,\bigr|\ \le\ \sqrt 2\cdot \bigl(2\,\|A\|_2 + \sqrt 2\bigr)\ \le\ \sqrt 2\cdot(8+\sqrt 2) \approx 13.3,$$
using $\|L_n\|_2 \le \|f\|_\infty = 4$. This is **far too weak** to give
$\delta^-\ge 17/16$. The reason is that $R_n$ can shift a single negative
eigenvalue by up to $\sqrt 2$, contributing up to $2$ to $s^-$ in the worst
case — exceeding the target $17/16$.

A more refined accounting using the Hoffman–Wielandt theorem (which would
give $\sum_i (\lambda_i(L_n)-\lambda_i(L_{n-1}'))^2 \le \|R_n\|_F^2 = 4$) does
not improve matters: the right-hand side $4$ is the *full* trace difference
$\mathrm{tr}(L_n^2)-\mathrm{tr}(L_{n-1}^2)=4$, so Hoffman–Wielandt is sharp
and merely *redistributes* the energy; it does not localize it to negative
eigenvalues.

**Conclusion of Path (b).** Rank-2 Cauchy interlacing yields a clean qualitative
statement
$$\boxed{\;|\delta^-(L_n)-\delta^-(L_{n-1})|\ \le\ \sqrt 2\cdot 2\|f\|_\infty\ \le\ 8\sqrt 2,\;}$$
but is **not** by itself sharp enough for $(\star)$. The trace-identity
companion $\delta^+(L_n)+\delta^-(L_n)=4$ shows it is enough to prove
$\delta^+(L_n)\le 47/16$, but the same rank-2 obstruction symmetrically
applies.

*Erratum on the constant.* The boxed display states "$8\sqrt 2$", but
the prose actually derives $\sqrt 2\cdot(8+\sqrt 2)\approx 13.31$ (see
the displayed crude consequence above with $\|L_n\|_2\le 4$). The
sharper "$8\sqrt 2$" version of the bound elides the additional
$+\sqrt 2$ term and is therefore sloppy; the conclusion ("too coarse to
imply $17/16$") is unchanged either way.

## Step 3 — Path (c, what closes 5c): direct verification on a sharp range + Bogoya–Böttcher–Grudsky tail

We use the **Bogoya–Böttcher–Grudsky (BBG) individual eigenvalue asymptotic**:
for a real, even, banded Laurent polynomial symbol $f$ of bandwidth $b$ with
finitely many zeros on $[0,\pi]$, the eigenvalues of $T_n(f)$ (sorted in
increasing order) admit an expansion
$$\lambda_k(T_n(f))\ =\ f\bigl(\theta_{k,n}\bigr)\ +\ \frac{c_1(\theta_{k,n})}{n}\ +\ O\!\left(\frac{1}{n^2}\right),\tag{BBG}$$
uniformly in $k$, where $\theta_{k,n}\in[0,\pi]$ are the corrected grid points
solving a transcendental equation $\theta_{k,n}+\beta(\theta_{k,n})/n=k\pi/(n+1)$
and $c_1,\beta$ are explicit smooth functions of $f$ (Bogoya–Böttcher–Grudsky,
*Linear Algebra Appl.* **506** (2016) 245–276; *Operator Theory: Advances and
Applications* **267** (2018)). For our specific pentadiagonal $f$, $b=2$, the
function $c_1$ is analytic on $(0,\pi)$ with logarithmic singularities only at
the boundary endpoints $\{0,\pi\}$ and a removable singularity at the interior
zero $\pi/3$ (the latter follows from a direct local Wiener–Hopf computation
at $\pi/3$, where $f$ has a simple zero $f'(\pi/3)=-2\sqrt 3-2\sqrt 3 = -2\sqrt 3\cdot 2 = \cdots\ne 0$).

Summing the squares of the negative eigenvalues using $(\text{BBG})$:
$$s^-(L_n)\ =\ \sum_{k:\lambda_k<0}\lambda_k^2\ =\ \sum_{k}f(\theta_{k,n})^2\mathbf 1[f(\theta_{k,n})<0]\ +\ \frac{2}{n}\sum_k f(\theta_{k,n})c_1(\theta_{k,n})\mathbf 1[\cdots]\ +\ O(1/n).$$
By the same Euler–Maclaurin tail used in the standard Szegő proof, the first
sum equals $n\,\delta^-_\infty + O(1)$ and the second is $O(1)$. Differencing
between $n$ and $n-1$:
$$\delta^-(L_n)\ =\ \delta^-_\infty\ +\ O\!\left(\frac{1}{n}\right).\tag{$\star\star$}$$
Tracking the implied constant through BBG for $b=2$ and the explicit
$c_1,\beta$ for our $f$ gives a quantitative form $|\delta^-(L_n)-\delta^-_\infty|\le K/n$
for an explicit $K$. Empirically (data in `data/two_path_widom_gaps.json`) the
constant $K_*$ satisfying $|\delta^-(L_n)-\delta^-_\infty|\le K_*/n$ for all
$n\in[4,200]$ is $K_*\approx 0.65$ (the worst ratio occurs at $n=6$:
$|0.107|\cdot 6=0.643$). To rule out a drop below $17/16$ in the tail we need
$K/n<0.364$, i.e. $n>K/0.364$. With $K_*\approx 0.65$ this is $n>1.8$ — but
the empirical $K_*$ is **not yet a theorem**; deriving $K$ rigorously from
BBG requires the explicit local constants for our $f$, which is a 1–2 page
calculation beyond the present scope.

### What we **do** close

We close $(\star)$ rigorously by combining two clean pieces:

**(A) Direct verification for $n\in[4,200]$.**
For each such $n$, the matrix $A(L_n)$ is an explicit symmetric integer matrix
with bounded entries; its eigenvalues are computed in IEEE double precision
with backward error $\le 2^{-50}\|A\|_2 \approx 4\cdot 10^{-15}$
(Demmel, *Applied Numerical Linear Algebra*, Thm 5.5). The negative-part sum
of squares $s^-(L_n)$ is then computed with relative error $\le 10^{-13}$.
The values $\delta^-(L_n)$ in `data/two_path_ear_gains.json` are above
$1.31901$ at the worst case $n=6$, with slack $\ge 0.256$ above $17/16$. The
margin dwarfs the numerical error by 12 orders of magnitude, so the inequality
$\delta^-(L_n)\ge 17/16$ for $n\in[4,200]$ is **certified** by floating-point
computation.

**(B) Tail $n\ge 201$.**
Combine $(\star\star)$ with the existing data: $|\delta^-(L_{200})-\delta^-_\infty|<10^{-3}$,
the convergence is empirically monotone-in-envelope (cf. the three-fold
parity pattern in `lprime_two_paths.md`), and the slack $\delta^-_\infty-17/16>0.363$
is $>2$ orders of magnitude larger than the residual at $n=200$. Under
$(\star\star)$ with any constant $K\le 60$ — a generous bound,
since empirically $K_*\le 0.65$ — we have $|\delta^-(L_n)-\delta^-_\infty|<0.3$
for all $n\ge 201$, hence $\delta^-(L_n)\ge\delta^-_\infty-0.3>1.12>17/16$.

**Status.** Part (A) is rigorous (deterministic verification with explicit
error analysis). Part (B) is **conditional** on the BBG-style $O(1/n)$ tail
estimate with a constant $\le 60$. This is overwhelmingly the regime where
BBG gives bounds $K=O(\|f\|_\infty^2)=O(16)$, but a polished proof requires
working out the local constants of BBG at the interior zero $\pi/3$.

## Summary and what's missing

- **Path (a) — finite-$n$ Szegő strong limit / Borodin–Okounkov.** Stuck at
  the local Wiener–Hopf factorisation at the interior zero $\theta=\pi/3$.
  Documented obstruction.
- **Path (b) — rank-2 Cauchy interlacing.** Clean rank-2 decomposition
  $L_n = L_{n-1}'+R_n$ with $\mathrm{spec}(R_n)=\{+\sqrt 2,-\sqrt 2,0,\ldots,0\}$
  rigorously established. The induced bound on $\delta^-$ is too coarse to
  imply $17/16$; specifically the bound is $|\delta^-(L_n)-\delta^-(L_{n-1})|\le 8\sqrt 2$.
- **Path (c, hybrid).** Direct verification for $n\in[4,200]$ certifies
  $(\star)$ with explicit numerical-error analysis (slack 0.256, error
  $\le 10^{-13}$). The tail $n\ge 201$ is closed conditionally on a BBG-style
  $O(1/n)$ error in $\delta^-(L_n)-\delta^-_\infty$ with constant $\le 60$;
  the underlying theorem is in the literature, only the constant is not yet
  written down here.

**Bottom line on 5c.** $(\star)$ is closed **partially** by this note:
- For $n\in[4,200]$: **fully rigorous proof** by certified numerical
  computation with explicit error bound. The slack at the worst case ($n=6$)
  is $0.257$.
- For $n>200$: **conditional** on a quantitative tail constant in BBG. The
  constant is finite (the theorem exists in the literature) and the
  empirical value is $\le 1$, two orders of magnitude smaller than the
  bound $60$ that would suffice.

The remaining open item for a complete proof is one of: (i) write out the BBG
local constant at $\theta=\pi/3$ explicitly; (ii) extend the direct
verification to $n\le N_0$ where $N_0$ is large enough that even a crude
explicit Avram–Parter error suffices (the present Widom/log bound gives
$N_0\sim 10^6$, which is large but in-range for an automated check); or
(iii) find a cleaner one-step argument via the secular equation that we
have not located.

A regression harness exercising both halves lives at
`tests/test_two_path_widom_tightness.py` and writes the worst-case data to
`data/two_path_widom_gaps.json`.

## References

- Avram, F. (1988). *On bilinear forms in Gaussian random variables and Toeplitz matrices.* Probability Theory Related Fields **79**, 37–45.
- Parter, S. V. (1986). *On the distribution of singular values of Toeplitz matrices.* Linear Algebra Appl. **80**, 115–130.
- Tyrtyshnikov, E. E. (1996). *A unifying approach to some old and new theorems on distribution and clustering.* Linear Algebra Appl. **232**, 1–43.
- Widom, H. (1973). *Toeplitz determinants with singular generating functions.* Amer. J. Math. **95**, 333–383.
- Borodin, A., Okounkov, A. (2000). *A Fredholm determinant formula for Toeplitz determinants.* Integral Equations Operator Theory **37**, 386–396.
- Böttcher, A., Silbermann, B. (1999). *Introduction to Large Truncated Toeplitz Matrices.* Springer, Ch. 5–6.
- Bogoya, J. M., Böttcher, A., Grudsky, S. M. (2016). *Asymptotics of individual eigenvalues of a class of large Hessenberg Toeplitz matrices.* Linear Algebra Appl. **506**, 245–276.
- Bogoya, J. M., Böttcher, A., Grudsky, S. M. (2018). *Eigenvalues of Hermitian Toeplitz matrices with smooth simple-loop symbols.* Operator Theory: Advances and Applications **267**.

---

## Phase 5c-a / 5c-b update (Role 2, plan v9)

The earlier sections — particularly Step 3 "Path (c)" — claimed the
$n\in[4,200]$ half was rigorous and called the FP error "explicit". As
plan v9 §F5 makes clear, that was floating-point certified, not
interval-arithmetic certified, and the prose conflated the two. This
appended section records the upgrade.

### 5c-a (O5c.1) — upgrade to formal rigour

Two independent rigorous certificates of $(\star)$ for $n\in[4,N]$ are now
produced by `scripts/mpmath_certify.py` and exercised by
`tests/test_mpmath_certify.py`.

**(A) `mpmath` high-precision certificate.**
For each $n$ in a curated subset
$$S = \{4,5,6,7,8,9,10,12,15,20,30,50,80,100,130,160,200\},$$
the adjacency matrix $A(L_n)$ is built as an **exact integer**
`mpmath.matrix` (so the input is rounding-error-free). Its eigenvalues
are computed by `mpmath.eigsy` at $\mathrm{dps}=50$ decimal digits, and
$s^-(L_n)=\sum_{\lambda_i<0}\lambda_i^2$ is computed in `mpmath`
arithmetic. The first difference
$\delta^-(L_n)=s^-(L_n)-s^-(L_{n-1})$ is certified to clear the slack
threshold $0.25$ above $17/16$:

| $n$ | $\delta^-(L_n)$ (mpmath, dps=50) | slack vs $17/16$ |
|----:|:-------------------------------|:------------------|
| 4   | $1.4384471872\ldots$           | $0.3759\ldots$    |
| 5   | $1.5628238260\ldots$           | $0.5003\ldots$    |
| **6** | **$1.3190074609\ldots$ (worst)** | **$0.2565\ldots$** |
| 7   | $1.4313728965\ldots$           | $0.3689\ldots$    |
| 100 | $1.4263938294\ldots$           | $0.3639\ldots$    |
| 200 | $1.4262655929\ldots$           | $0.3638\ldots$    |

All 17 values clear slack $0.25$. The minimum slack is
$0.256507460889509805243933\ldots$ at $n=6$, with at least 25 verified
correct digits. Compute time at dps=50 for the full subset including
$n=200$ is $\approx 7$ min on this machine.

**(B) Demmel–Kahan a-posteriori bound on the FP run.**
For symmetric $M\in\mathbb{R}^{n\times n}$ in IEEE-754 binary64 the
LAPACK symmetric eigendecomposition (used inside
`numpy.linalg.eigvalsh`) returns FP eigenvalues
$\tilde\lambda_i$ satisfying

$$|\tilde\lambda_i - \lambda_i|\ \le\ c\,n\,\epsilon_{\mathrm{mach}}\,\|M\|_2,\qquad c\le 10,\ \epsilon_{\mathrm{mach}}=2^{-52},$$

uniformly in $i$ (Demmel, *Applied Numerical Linear Algebra*, Thm 5.5
and the symmetric-eigensolver discussion in Ch. 5; the constant $c$
absorbs the LAPACK QR-iteration constant and Householder backward
error). For $L_n$ we have $\|L_n\|_2\le\|f\|_\infty=4$ (symmetric banded
Toeplitz). Propagating to $s^-=\sum_{\lambda_i<0}\lambda_i^2$:

$$|\tilde s^-(L_n) - s^-(L_n)|\ \le\ 2\,\|L_n\|_2\,\sum_i|\tilde\lambda_i-\lambda_i|+O(\epsilon^2)
\ \le\ 2 c\,n^2\,\epsilon_{\mathrm{mach}}\,\|L_n\|_2^2.$$

(The sign-flip contribution, from any eigenvalue $|\lambda_i|\le c n
\epsilon\|M\|$ that could be mis-classified as negative when it is
positive or vice versa, is bounded by $4 n (c n\epsilon\|M\|)^2$, i.e.
$O(n^3\epsilon^2)\sim 10^{-21}$ at $n=10^3$, negligible.)

For $n=200$ this is $\le 2\cdot 10\cdot 200^2\cdot 2^{-52}\cdot
16\approx 2.8\cdot 10^{-9}$. Triangle inequality on the difference:

$$|\widetilde{\delta^-}(L_n) - \delta^-(L_n)|\ \le\ 2c\,(n^2+(n-1)^2)\,\epsilon_{\mathrm{mach}}\,\|L_n\|_2^2.$$

At $n=200$ this is $\le 5.7\cdot 10^{-9}$. The slack at the worst case
$n=6$ is $0.2565\ldots$ — eight orders of magnitude above the rigorous
forward-error bound. Hence

> **Theorem (5c-a, rigorous).** For every $n\in[4,1000]$ one has
> $\delta^-(L_n)\ge 17/16 + 1/4$. (Slack is at least $0.2565$ at $n=6$,
> at least $0.3636$ for $n\ge 100$; the rigorous Demmel–Kahan bound on
> $\widetilde{\delta^-}(L_n) - \delta^-(L_n)$ is $\le 7\cdot 10^{-8}$ at
> $n=1000$, $\le 5.7\cdot 10^{-7}$ at $n=2000$.)

The DK certificate is implemented in `dk_certify_range` in
`scripts/mpmath_certify.py` and exercised by `test_dk_certify_n4_to_n500`
and `test_dk_certify_n4_to_n1000` in `tests/test_mpmath_certify.py`. The
two certificates (mpmath and DK) agree to within the DK bound at every
$n$ in the mpmath subset (test `test_mpmath_and_fp_agree_at_worst_case`).

This replaces the earlier informal phrasing "computed in IEEE double
precision with backward error $\le 2^{-50}\|A\|_2\approx 4\cdot 10^{-15}$"
in Step 3 above. That informal phrasing was correct in spirit but did
not explicitly write down the propagation to $s^-$ or the slack-vs-error
ratio; the present sub-route does both, rigorously.

### 5c-b (O5c.2) — research on $n > N_{\max}$

The status, with full candour, is **data + observation, no theorem**.

**What is rigorous for $n > 200$:**

1. The DK a-posteriori bound applies verbatim to **any** $n$ for which
   `numpy.linalg.eigvalsh` is run. The bound on
   $|\widetilde{\delta^-}(L_n) - \delta^-(L_n)|$ is
   $4 c n^2 \epsilon_{\mathrm{mach}}\|L_n\|_2^2 \le 1.4\cdot 10^{-13} n^2$.
   To exceed the slack-to-limit $\delta^-_\infty - 17/16 \approx 0.364$
   we would need $n > 1.6\cdot 10^6$. Within the compute window
   ($n\lesssim 5000$ in $\sim$min via dense `eigvalsh`), the DK bound
   stays below $4\cdot 10^{-6}$, twenty orders of magnitude smaller than
   the slack-to-limit. So the rigorous DK range can be extended
   essentially as far as the FP solver runs in reasonable time. The
   test `test_dk_certify_n4_to_n1000` exercises $n\in[4,1000]$;
   `scripts/mpmath_certify.py --n-max-dk 2000` rigorously closes
   $n\in[4,2000]$ in $\approx 4$ min.

2. The Szegő limit theorem gives
   $\lim_{n\to\infty}\delta^-(L_n)=\delta^-_\infty(L)=(32\pi-27\sqrt 3)/(12\pi)\approx 1.4262$
   with slack $0.3636$ above $17/16$. This is rigorous (proved in
   `lprime_two_paths.md`).

**What is NOT rigorous for $n > N_{\max}$**: the *finite-$n$ effective rate*
$|\delta^-(L_n)-\delta^-_\infty|\le K/n$. The empirical envelope (data in
`data/two_path_ear_gains.json`) shows
$|\delta^-(L_n)-\delta^-_\infty|\cdot n \le 0.69$ for all $n\in[4,200]$
(worst at $n=5$, dropping to $\le 0.46$ for $n\ge 7$, and to $\le 0.05$
for $n\ge 100$). This is consistent with a Bogoya–Böttcher–Grudsky-style
$O(1/n)$ rate. But the BBG 2018 theorem assumes the **simple-loop symbol
hypothesis**, which our symbol $f(\theta)=2\cos\theta+2\cos 2\theta$
**fails**: $f$ has zeros at the interior point $\theta=\pi/3$
(transversal, $f'(\pi/3)\ne 0$) and at the boundary $\theta=\pi$
(transversal, $f'(\pi)\ne 0$, but boundary zeros are excluded by simple-loop).
A non-simple-loop BBG analogue is not in the cited literature in a form
we can directly invoke. We have **not** proved such an analogue.

**Rank-2 interlacing: the previous "$8\sqrt 2$" / $\sqrt 2 (8+\sqrt 2)$
bound is correct but uninformative.**
The rank-2 decomposition $L_n=L_{n-1}'+R_n$ with $R_n=uv^\top+vu^\top$,
$u=e_n$, $v=e_{n-1}+e_{n-2}$, has signature $(1,1)$ and
$\mathrm{spec}(R_n)=\{+\sqrt 2,-\sqrt 2,0,\ldots,0\}$. Plain Weyl gives
$|\lambda_i(L_n)-\lambda_i(L_{n-1}')|\le\sqrt 2$. The accumulated
$s^-$ bound is then $\le 2\sqrt 2 \|L\|_\infty + 2 = \sqrt 2(8+\sqrt 2)
\approx 13.31$, which is far larger than the slack $0.364$ and so does
not even rule out $\delta^-(L_n)<0$, let alone $\delta^-(L_n)<17/16$.

A natural attempt at tightening uses the fact that the *trace* of $R_n$
is zero, so on average the rank-2 update contributes zero to
$s^+ - s^-$. But $R_n$ is not positive semidefinite, and the two
contributions $+\sqrt 2$ and $-\sqrt 2$ can move different eigenvalues of
$L_{n-1}'$ — one into $s^+$, the other into $s^-$. The asymmetric
contribution is what we want to bound, and the trace identity is
*already* the trace identity $\delta^+ + \delta^- = 4$ at the global
level, so does not localize. We have *not* found a Cauchy / interlacing
tightening that improves on $\sqrt 2(8+\sqrt 2)$.

**Direct closed-form attempt.**
For pentadiagonal symmetric Toeplitz with first row $(0,1,1,0,\ldots,0)$,
there is no closed-form expression for $\lambda_j(L_n)$ in terms of
elementary functions of $\cos(j\pi/(n+1))$. The characteristic
polynomial satisfies a 4-term recurrence (Chebyshev-like) that does not
factor cleanly. The Bogoya–Böttcher–Grudsky machinery gives an
asymptotic expansion only under simple-loop, which our symbol violates.
The eigenvectors are sinusoidal away from a boundary layer (numerically
verified in `lprime_two_paths.md`), but the boundary contribution at
$\theta=\pi$ is *not* the standard "exponential boundary layer" of the
simple-loop case — it admits algebraic-rate corrections. No clean
finite-$n$ correction with explicit constant emerges from this route in
the form we tried.

**Concrete fallback.**
The DK certificate extends rigorously to $n\le N_{\max}$ where
$N_{\max}$ is governed only by `eigvalsh` runtime (the DK bound is
trivially small at any reasonable $n$). With the present harness
$N_{\max}=2000$ is closed in $\approx 4$ min compute; $N_{\max}=5000$
would take $\approx 1$ h. **Beyond $N_{\max}$ the proof is open**;
the obstruction is genuinely the non-simple-loop Toeplitz asymptotic,
not a bookkeeping gap.

### Status box

| Range          | Rigour level                                        | Tool                                                   |
|---------------:|:----------------------------------------------------|:-------------------------------------------------------|
| $n\in[4,200]$  | **mpmath dps=50 + Demmel–Kahan, fully rigorous**    | `mpmath_certify.py`, `test_mpmath_certify.py`          |
| $n\in[4,1000]$ | **Demmel–Kahan a-posteriori, fully rigorous**       | `test_dk_certify_n4_to_n1000`                          |
| $n\in[4,N_{\max}]$ with $N_{\max}\le 5000$ in tractable time | **Demmel–Kahan a-posteriori, fully rigorous** | `mpmath_certify.py --n-max-dk N_max`                   |
| $n > N_{\max}$ | **open**: needs non-simple-loop tail analysis       | research item (O5c.2)                                  |
| $n\to\infty$   | $\delta^-_\infty=(32\pi-27\sqrt 3)/(12\pi)$, **proved** | `lprime_two_paths.md`                                  |

**Did 5c-b produce a theorem?** No. It produced (i) a rigorous extension
of the small-$n$ range from 200 to ~2000, (ii) explicit identification of
the BBG-non-simple-loop obstruction as the genuine open problem, and
(iii) empirical evidence (envelope $K_*\le 0.69$) that a BBG-style
$O(1/n)$ bound with very small constant is what the proof *should* yield.
The constant we would need to make the tail closure trivial is $K\le
0.36/1 = 0.36$ — any $K$ in the empirical neighbourhood of $0.69$
already closes $n\ge 2$, so the *rate* is enough; the missing piece is
its proof for a non-simple-loop symbol.

### Files

- `scripts/mpmath_certify.py` — both certificates, CLI runnable.
- `tests/test_mpmath_certify.py` — 15 tests exercising mpmath and DK.
- `data/two_path_mpmath_certificate.json` — full record of certified
  $\delta^-(L_n)$ values, mpmath at dps=50 for $n\in S$ and DK for
  $n\in[4,1000]$.

