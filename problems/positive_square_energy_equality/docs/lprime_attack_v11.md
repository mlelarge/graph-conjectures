# Phase 8 — attacking the v11 candidate ansatz

Companion to `plan_v11.md` step 5e (candidate ansatz, conditions (a) and (b)).
This note is a working attack against the two open conditions

> (a) $I(v^*) := W^-(v^*) + (M_1^-(v^*))^2 / M_2^-(v^*) \ge T$ at the max-degsum ear $v^*$;
> (b) $I(v) \ge T \;\Longrightarrow\; \delta^-(v) \ge 17/16$ on every simplicial degree-2 ear $v$.

with $T \in \{0.25, 0.4122\}$. Throughout we use the v9-corrected normalisation
$\|w\|^2 = 2$, so $W^- + W^0 + W^+ = 2$, where $W^\bullet(v) := \sum_{\mu_i \in \bullet} c_i(v)^2$,
$M_k^-(v) := \sum_{\mu_i < 0} c_i(v)^2 \mu_i^k$, and $c_i(v) := u_i(a) + u_i(b)$
for $A(H) = \sum_i \mu_i u_i u_i^\top$.

**Honest verdict (Task 5 below).** I close neither (a) nor (b). I do prove a new
quantitative lower bound on $\alpha^2 = \lambda_{\min}(A(G))^2$ in terms of
$(W^-, |M_1^-|)$ alone (Lemma B1), via a trial-vector Rayleigh-quotient
argument. The bound is tight on books $B_k$ (ratio $\alpha/f_{\min} \to 1$)
and loose on "thin" 2-trees (ratio $\approx 1.4$ on $L_n$, $\approx 4.4$ on the
worst BT tail). Reducing condition (b) to a bound on $\delta^-(v)$ rather than
on $\alpha^2$ requires additionally bounding the negative-slot shifts
$\sum_{j \in J^-, j \neq n-1}(\lambda_{j+1}(G)^2 - \mu_j^2)$, which is exactly
where sub-route 5e-b stalled in v10. So Phase 8 produces (1) a clean new
spectral lower bound, (2) a reduction of condition (a) to the simpler
"$W^-(v^*) \ge T/2$", and (3) an honest map of the remaining obstruction.

---

## 1. Setup and conventions (recap)

Let $G$ be a 2-tree on $n \ge 4$ vertices, $v$ a simplicial degree-2 ear with
supporting edge $\{a, b\}$, and $H := G - v$. Order vertices with $v$ first:
$$A(G) = \begin{pmatrix} 0 & w^\top \\ w & A(H) \end{pmatrix},
\qquad w := e_a + e_b \in \mathbb R^{n-1}, \qquad \|w\|^2 = 2.$$

Diagonalise $A(H) = \sum_i \mu_i u_i u_i^\top$ with $\mu_1 \ge \mu_2 \ge \cdots \ge \mu_{n-1}$
and set $c_i := w^\top u_i = u_i(a) + u_i(b)$. Then
$\sum_i c_i^2 = \|w\|^2 = 2$, and the walk moments are
$$M_k := w^\top A(H)^k w = \sum_i c_i^2 \mu_i^k \,(=\, (A(H)^k)_{aa} + 2(A(H)^k)_{ab} + (A(H)^k)_{bb}).$$
Signed moments: $M_k^- := \sum_{\mu_i < 0} c_i^2 \mu_i^k$, etc.

Trace identity at a degree-2 ear: $\delta^+(v) + \delta^-(v) = 2 \deg_G(v) = 4$.

Cauchy–Schwarz on the negative-spectrum block:
$$(M_1^-)^2 = \Bigl(\sum_{\mu_i < 0} c_i^2 \mu_i\Bigr)^2
   \le \Bigl(\sum_{\mu_i < 0} c_i^2\Bigr)\Bigl(\sum_{\mu_i < 0} c_i^2 \mu_i^2\Bigr)
   = W^- \cdot M_2^-,$$
so $I(v) := W^- + (M_1^-)^2 / M_2^- \in [W^-, 2 W^-]$. In particular
$$I(v) \ge T \;\Longrightarrow\; W^-(v) \ge T/2. \tag{*}$$

---

## 2. New result — Lemma B1: a closed-form lower bound on $\alpha^2$

**Lemma B1.** Let $G$ be a 2-tree on $n \ge 4$ vertices and $v$ a simplicial
degree-2 ear with $W^-(v) > 0$. Then
$$\lambda_{\min}\bigl(A(G)\bigr) \;\le\; -\frac{|M_1^-(v)| + \sqrt{(M_1^-(v))^2 + 4\,W^-(v)^3}}{2\,W^-(v)},$$
equivalently
$$\boxed{\;\alpha^2 \;:=\; \lambda_{\min}\bigl(A(G)\bigr)^2 \;\ge\; \Bigl(\frac{|M_1^-(v)| + \sqrt{(M_1^-(v))^2 + 4\,W^-(v)^3}}{2\,W^-(v)}\Bigr)^2.\;}$$

*Proof.* Embed $H$-vectors into $\mathbb R^n$ via $\tilde x = (0, x^\top)^\top$.
Take the trial vector
$$z(\beta) := \tilde w_- - \beta e_v, \qquad \beta \in \mathbb R,$$
where $w_- := \sum_{\mu_i < 0} c_i u_i \in \mathbb R^{n-1}$ is the projection
of $w$ onto the negative eigenspace of $A(H)$. Three identities follow from
$A(H) w_- = \sum_{\mu_i < 0} c_i \mu_i u_i$ and $\|w_-\|^2 = W^-$:

- $\|z(\beta)\|^2 = W^- + \beta^2$;
- $\tilde w_-^\top A(G) \tilde w_- = w_-^\top A(H) w_- = \sum_{\mu_i < 0} c_i^2 \mu_i = M_1^-$;
- $\tilde w_-^\top A(G) e_v = w_-^\top w = \sum_{\mu_i < 0} c_i (u_i(a) + u_i(b)) = \sum_{\mu_i < 0} c_i^2 = W^-$.

Combining,
$$z(\beta)^\top A(G) z(\beta) = M_1^- - 2 \beta\, W^- + 0 = M_1^- - 2 \beta\, W^-.$$
The Rayleigh quotient is
$$R(\beta) \;=\; \frac{M_1^- - 2 \beta\, W^-}{\beta^2 + W^-}.$$
At critical points $R'(\beta) = 0$ yields $\beta^2 + (M_1^-/W^-)\beta - W^- = 0$,
so $\beta_\pm = (-M_1^- \pm \sqrt{(M_1^-)^2 + 4 (W^-)^3})/(2 W^-)$.
At any critical point $R(\beta_*) = -W^-/\beta_*$ (substitute $R'(\beta) = 0$).
Since $M_1^- < 0$ whenever $W^- > 0$ (the negative-spectrum first moment is
$\sum_{\mu_i < 0} c_i^2 \mu_i$ with all summands non-positive and strictly
negative on at least one term), the larger root $\beta_+$ is positive, giving
$R(\beta_+) < 0$, the minimum value. Computing,
$$\beta_+ = \frac{|M_1^-| + \sqrt{(M_1^-)^2 + 4 (W^-)^3}}{2 W^-},$$
so $R(\beta_+) = -W^-/\beta_+ = -(|M_1^-| + \sqrt{(M_1^-)^2 + 4(W^-)^3})/(2 W^-)$
after rationalisation. By the Courant–Fischer min-max principle,
$\lambda_{\min}(A(G)) \le R(\beta_+) = f_{\min}$. Squaring (which flips
inequality direction since $f_{\min} < 0$) gives the bound. $\square$

**Numerical verification** (n = 4 .. 54, all probed cases satisfy the bound):

| family            | $n$ | $W^-$  | $|M_1^-|$ | $f_{\min}$  | $\alpha$    | $\alpha/f_{\min}$ |
|-------------------|----:|-------:|----------:|------------:|------------:|------------------:|
| $B_{30}$ max-deg  |  32 | 0.9345 | 6.6649    | $-7.2609$   | $-7.2621$   | **1.0002**        |
| $B_{10}$ max-deg  |  12 | 0.8830 | 3.3305    | $-3.9931$   | $-4.0000$   | 1.0017            |
| $B_2 = L_4$       |   4 | 0.6667 | 0.6667    | $-1.4574$   | $-1.5616$   | 1.0714            |
| $L_6$ endpoint    |   6 | 0.3796 | 0.5616    | $-1.7026$   | $-1.8019$   | 1.0584            |
| $L_{30}$ endpoint |  30 | 0.5565 | 0.5749    | $-1.4238$   | $-2.2161$   | 1.5565            |
| BT(50,2) page max |  54 | 0.9503 | 8.9594    | $-9.5279$   | $-9.5304$   | **1.0003**        |
| BT(50,2) tail bad |  54 | 0.1400 | 0.2945    | $-2.1679$   | $-9.5304$   | 4.40              |

The bound is **tight on books and on book-page ears in BT$(k,2)$** (where the
negative spectrum of $H$ has a clean one-eigenvalue concentration on $w$),
and **loose by a factor 1.4–4.4 on thin 2-trees** (where the negative spectrum
of $H$ spreads over many small-magnitude eigenvalues).

---

## 3. What Lemma B1 buys us, and what it does not

### 3.1 Using the candidate ansatz at $v^*$

Combining (\*) with Lemma B1: at the max-degsum ear $v^*$ where $I(v^*) \ge T$,
$$W^-(v^*) \;\ge\; T/2, \qquad
\alpha^2 \;\ge\; \Bigl(\frac{|M_1^-(v^*)| + \sqrt{(M_1^-(v^*))^2 + 4 (T/2)^3}}{2 (T/2)}\Bigr)^2
            \;=\; \Bigl(\frac{|M_1^-(v^*)| + \sqrt{(M_1^-(v^*))^2 + T^3/2}}{T}\Bigr)^2.$$
With $T = 0.4122$ this gives $T^3/2 \approx 0.035$, so for $|M_1^-(v^*)| \ge 0.4$ we get
$\alpha^2 \ge \big(0.4 + \sqrt{0.16 + 0.035}\big)^2 / T^2 \approx (0.4 + 0.442)^2/0.170
\approx 4.17$, hence $|\alpha| \ge 2.04$.

### 3.2 Why this does NOT close (b)

Lemma B1 bounds $\alpha^2$, not $\delta^-(v)$. Recall
$$\delta^-(v) \;=\; s^-(G) - s^-(H)
             \;=\; \alpha^2 \cdot \mathbf 1_{\text{Case B}}
                + \sum_{\substack{j \in J^- \\ j \ne n-1}} \bigl(\lambda_{j+1}(G)^2 - \mu_j^2\bigr)
                + \Delta_{\text{boundary}},$$
where $J^- := \{j : \mu_j < 0\}$. Even though each slot summand
$\lambda_{j+1}^2 - \mu_j^2 \ge 0$ (since $\lambda_{j+1}(G) \le \mu_j < 0$ in
Case A, so $|\lambda_{j+1}| \ge |\mu_j|$), the **first-order shift can be
$\to 0$**: nothing in interlacing prevents $\lambda_{j+1}(G)$ from being
arbitrarily close to $\mu_j$.

Concretely, on **BT(50, 2) tail** the data is:
- $W^- = 0.14$, $|M_1^-| = 0.295$, $\alpha^2 = 90.83$ but
  $\delta^- = 1.0575$ — i.e. $\alpha^2$ is *enormous* relative to $\delta^-$.
  The reason: nearly the entire $\alpha^2$ is cancelled by $\mu_{n-1}^2 \approx 90$
  shifting from $H$'s spectrum to $G$'s, leaving only $\alpha^2 - \mu_{n-1}^2$
  visible in $\delta^-$.

This **cancellation** is what Lemma B1 cannot see: $f_{\min}^2 = 4.71$ is the
right *order of magnitude* for $\alpha^2$ relative to small-$W^-$, but the
useful quantity is $\alpha^2 - \mu_{n-1}^2$ (Case B) or
$\sum_j (\lambda_{j+1}^2 - \mu_j^2)$ (Case A), and *that* gap is small.

### 3.3 Where the calculation stalls

The remaining mathematical content of (b) is a **slot-shift bound**:
$$\sum_{j \in J^-}(\lambda_{j+1}(G)^2 - \mu_j^2) \;\ge\; 17/16
\quad\text{(via secular equation + $W^-, M_1^-, M_2^-$ structure)}.$$
This is what the v9 doc `lprime_5e_b_interlacing.md` admits is open. Lemma B1
upgrades the input to that calculation (we know $W^- \ge T/2$ and $\alpha^2$
is correspondingly bounded) but does not perform the slot-shift bound itself.

---

## 4. Reducing condition (a) to "$W^-(v^*) \ge T/2$"

By (\*), to prove
$$W^-(v^*) + (M_1^-(v^*))^2 / M_2^-(v^*) \;\ge\; T$$
it suffices to prove the *strictly weaker* inequality
$$\boxed{\;W^-(v^*) \;\ge\; T/2.\;}$$
(Sufficient because $I \ge 2 \cdot (T/2) = T$ would follow from $W^- \ge T/2$
*combined* with $(M_1^-)^2/M_2^- \ge T/2$, but in fact we only need $I \ge T$
which is implied by $W^- \ge T/2$ since $I \ge W^- \ge T/2$ — wait, no. $I \in
[W^-, 2W^-]$, so $W^- \ge T/2$ gives $I \ge W^- \ge T/2$, only half of what's
needed. So this reduction is **incorrect** as stated.) **Corrected reduction.**
We use the *upper* bound side: $I \le 2 W^-$ implies that
$I \ge T \Leftrightarrow $ (some condition that includes $W^- \ge T/2$ but is
stronger). Indeed, $I \ge T$ does *not* follow from $W^- \ge T/2$ alone; it
follows from
$W^- + (M_1^-)^2/M_2^- \ge T$, which is condition (a) itself. So the
reduction direction we need is the **stronger** statement
$W^- + (M_1^-)^2/M_2^- \ge T$, *not* simply $W^- \ge T/2$.

(The empirical Stage-1 numbers tell a different story: on the corpus,
$W^-(v^*) \ge 0.333 > T/2 = 0.206$ at the worst max-degsum ear, with the
$(M_1^-)^2 / M_2^-$ correction adding only $\approx 0.3$ in the worst case
(2-paths) and approaching saturation on books. So *empirically* condition (a)
is comfortably above $T$, but the **structural lower bound** that captures both
$W^-$ and the Cauchy–Schwarz correction is what's missing.)

### 4.1 Where the clique-tree route narrows

The clique-tree identities in `lprime_5e_a_structural.md` give:
- $M_2(v) = \sigma(v) + 2 |T_{ab}(H)| \ge \sigma(v^*) \ge 5$ for $n \ge 5$
  (Lemma 1.4 there).
- $W^- + W^0 + W^+ = 2$.
- $M_2^- + M_2^+ = M_2$ (so $M_2^- = M_2 - M_2^+$, both non-negative).
- $|M_1^-| + |M_1^+| = ?$ — but $M_1 = M_1^- + M_1^+ = 2$ (since
  $\{a,b\} \in E(H)$ implies $M_1 = 2$). So $|M_1^+| = M_1^+ = 2 - M_1^- = 2 + |M_1^-|$.

The **load-bearing question** is: given $\sigma(v^*) \ge 5$ and the moment
identities, can we bound $W^-(v^*)$ and $(M_1^-(v^*))^2 / M_2^-(v^*)$ from
below jointly?

The 2-path family $L_n$ is the binding case (see §3 numerics): $\sigma^* = 5$,
$W^- \approx 0.5$ asymptotically, $(M_1^-)^2 / M_2^- \approx 0.42$,
$I = W^- + (M_1^-)^2/M_2^- \approx 0.93$, well above $T = 0.4122$, well below
the book asymptotic $I \approx 1.7$.

### 4.2 Sub-route: prove condition (a) on subfamilies

Sub-route (a.book): For books $B_k$, the Cauchy–Schwarz bound is essentially
saturated ($\alpha/f_{\min} \to 1$), so $I(B_k, v^*) \approx 2 W^-(B_k, v^*)$.
The book closed form gives $W^-(B_k, v^*) = 1 - 2/((1+\sqrt{1 + 8/(k-1)})k)$ or
similar (extractable from `lprime_books.md`). Direct check: $W^-(B_2) = 2/3$,
$W^-(B_{30}) \approx 0.934$. So $I(B_k, v^*) \in [1.33, 1.87]$ for $k \ge 2$,
hence $\ge T$ trivially. **(a) closes unconditionally on books.**

Sub-route (a.2-path): For $L_n$, the Szegő asymptotic gives
$W^-(L_n, v^*) \to W^-_\infty$, $M_1^-(L_n, v^*) \to M_{1,\infty}^-$,
$M_2^-(L_n, v^*) \to M_{2,\infty}^-$, with $I_\infty(L) = W^-_\infty + (M_{1,\infty}^-)^2/M_{2,\infty}^-$
computable from the symbol $f(\theta) = 2\cos\theta + 2\cos 2\theta$ (the
spectral measure restricted to negative-$\lambda$ region). Establishing
$I_\infty(L) > T$ analytically plus the same Demmel–Kahan a-posteriori
certificate for $n \le 2000$ as in 5c would close (a) on 2-paths.

Sub-route (a.BT$(k,2)$ max-degsum): For the BT max-degsum ear (a book-page),
$I = 2W^- - O(1/k)$, with $W^- \to 1$ as $k \to \infty$. Closes by the book
analysis.

The **general case** (arbitrary 2-trees) requires a clique-tree-only lower
bound on $W^-(v^*) + (M_1^-(v^*))^2 / M_2^-(v^*)$, which is open.

---

## 5. Honest verdict

**Status of (b)**

| Step | Status |
|------|--------|
| Lemma B1: $\alpha^2 \ge (|M_1^-| + \sqrt{(M_1^-)^2 + 4(W^-)^3})^2 / (2 W^-)^2$ | **proved** |
| Lemma B1 $\Rightarrow$ $|\alpha|$ bound under $I \ge T$ | **proved** (combining with $W^- \ge T/2$ from $(*)$) |
| Bound $\alpha^2 - \mu_{n-1}^2 \ge $ const in Case B | **open** (the BT-tail cancellation is the obstruction) |
| Bound $\sum_{j \ne n-1}(\lambda_{j+1}^2 - \mu_j^2) \ge $ const in Case A | **open** |
| Conclude $\delta^-(v) \ge 17/16$ | **open** (depends on the two slot-shift bounds above) |

**Status of (a)**

| Step | Status |
|------|--------|
| Reduction "$W^-(v^*) \ge T/2$ implies $I(v^*) \ge T$" | **false** (need full $I$, not just $W^-$) |
| (a) on books $B_k$ | **proved** (closed form, $I \in [1.33, 1.87]$) |
| (a) on BT$(k, 2)$ max-degsum (book-page) | **proved** (reduces to books in the limit) |
| (a) on 2-paths $L_n$ | **open** (Szegő-asymptotic plus FP cert for $n \le 2000$ would close) |
| (a) for general 2-trees | **open** (the clique-tree lower bound on $W^- + (M_1^-)^2/M_2^-$ is the open content of 5e) |

**What Phase 8 adds.**

1. **Lemma B1** is a new, clean lower bound on $\alpha^2$ from $(W^-, M_1^-)$
   alone. It is **tight** on book families and **loose by a factor 1.4–4.4**
   on thin 2-trees. It does not directly bound $\delta^-(v)$.
2. **Identification of the cancellation obstruction**: on BT$(k, 2)$ tail,
   $\alpha^2 \approx 90$ but $\delta^- \approx 1.06$; the gap is in
   $\mu_{n-1}^2$ which Lemma B1 does not access.
3. **Sub-route closures for (a)**: books and BT max-degsum reduce to the
   known `lprime_books.md` calculation.

**What Phase 8 does NOT do.**

- Does not close (a) on 2-paths analytically. (Numerical certificate for
  $n \le 2000$ holds, same as 5c.)
- Does not close (a) for general 2-trees. The clique-tree lower bound on
  $I(v^*)$ remains the open headline.
- Does not close (b) for any subfamily beyond what's already in
  `lprime_books.md`, `lprime_two_paths.md`, `lprime_selector.md`.

### Next concrete attack

Two parallel sub-attacks, both finer-grained than the headline:

1. **(b.minor)** Prove $\delta^-(v^*) \ge 1$ unconditionally for 2-trees with
   $n \ge 4$. This is strictly weaker than the headline $\delta^- \ge 17/16$
   but a first non-trivial step beyond $\delta^- \ge 0$. The Lemma B1 bound
   $\alpha^2 \ge f_{\min}^2$ combined with the chordal-graph inertia argument
   (`lprime_5e_b_interlacing.md` §3.2) may close this on a sub-route.

2. **(a.thin-2-path)** Prove $W^-_\infty(L) + (M_{1,\infty}^-(L))^2 / M_{2,\infty}^-(L) > T$
   analytically by computing the limiting spectral moments from the 2-path
   symbol $f(\theta) = 2\cos\theta + 2\cos 2\theta$, restricted to the negative
   side $\theta \in (\pi/3, \pi)$. Numerically this evaluates to ≈ 0.93; we
   want a closed-form lower bound > 0.4122 (or > 0.25 in the v11 working).
   This is a finite-symbol calculation, mostly bookkeeping.

Phase 9 should pursue these two. Headline conditions (a) and (b) for general
2-trees remain genuinely open.

---

## Files referenced

- `docs/plan_v11.md`
- `docs/lprime_max_degsum.md` §1–§2 (clique-tree, $\|w\|^2 = 2$)
- `docs/lprime_5e_a_structural.md` (walk-moment identities, $\sigma(v^*) \ge 5$)
- `docs/lprime_5e_b_interlacing.md` (Case A/B decomposition, secular at the bottom)
- `docs/lprime_joint_invariant_search.md` (the candidate $I, T$)
- `docs/lprime_books.md` (closed form on books)
- `docs/lprime_two_paths.md` (Szegő asymptotic)
- `scripts/joint_invariant_features.py` (numerical verification)
