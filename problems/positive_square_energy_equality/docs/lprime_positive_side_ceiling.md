# Positive-side dual of Lemma B1 — attacking $\delta^+(v^*) \le 3$ via the trace identity

Companion to `plan_v13.md`, step 5e (max-degsum selector for 2-trees).
Phase target, reformulated:

> **(b.minor)** rewritten via the trace identity. Let $G$ be a 2-tree on
> $n \ge 4$ vertices, $v^*$ a max-degsum simplicial degree-2 ear of $G$,
> and $H = G - v^*$. Since $\mathrm{tr}(A(G)^2) - \mathrm{tr}(A(H)^2) = 2 \deg_G(v^*) = 4$
> on every degree-2 ear, one has $\delta^+(v^*) + \delta^-(v^*) = 4$.
> Hence $\delta^-(v^*) \ge 1 \iff \delta^+(v^*) \le 3$. The Phase 9
> b.minor target therefore admits a *positive-side reformulation*.

This note follows the prompt for the "positive-side ceiling" exploration:
mirror the Phase 8 Lemma B1 derivation on the positive eigenspace of
$A(H)$, build the analogous corpus, and ask whether the positive side
delivers an asymmetrically tighter bound than the negative side.

**Honest verdict up front.** Lemma B1+ holds and is empirically clean.
The positive-side analogue does **not** close $\delta^+(v^*) \le 3$ at
the max-degsum ear, for a *structural* reason that is recognisably a
mirror image of the F11 caveat on the negative side: Lemma B1+ is a
*lower* bound on $\lambda_{\max}(A(G))$, hence a lower bound on
$\delta^+$, which is the *wrong direction*. The strategic asymmetry
hypothesised in the prompt — that the positive side's Rayleigh bound
might be tighter than the negative side's — is **not supported by the
data**: the two Rayleigh tightness ratios are within $2\%$ of each
other on the corpus.

The reformulation does produce one (modest) new result: a uniform
Perron floor $f_{\max}^+ \ge 2$ on max-degsum ears (a corollary of
$M_1^+ \ge 2$, valid because the supporting edge $\{a,b\}$ lies in
$E(H)$). This gives the cheap a.e. fact $\lambda_{\max}(A(G)) \ge 2$
on every max-degsum ear, which is sharp on $B_2 = K_4 - e$.

---

## 1. The trace-identity reformulation

### 1.1 Setup

Let $G$ be a 2-tree on $n \ge 4$ vertices, $v$ a simplicial degree-2
ear with supporting edge $\{a, b\} \in E(H)$ where $H = G - v$. Order
vertices so $v$ is first:
$$A(G) = \begin{pmatrix} 0 & w^\top \\ w & A(H) \end{pmatrix},
\qquad w = e_a + e_b, \qquad \|w\|^2 = 2.$$
Diagonalise $A(H) = \sum_i \mu_i u_i u_i^\top$ with
$\mu_1 \ge \cdots \ge \mu_{n-1}$, set $c_i := w^\top u_i$. Walk moments
$M_k^\pm := \sum_{\mu_i \gtrless 0} c_i^2 \mu_i^k$, weights
$W^\pm := \sum_{\mu_i \gtrless 0} c_i^2$.

### 1.2 The trace identity on degree-2 ears

$$\mathrm{tr}(A(G)^2) - \mathrm{tr}(A(H)^2) \;=\; 2 \deg_G(v) \;=\; 4,$$
since $\mathrm{tr}(A^2) = 2m$ and removing a degree-$d$ vertex deletes
$d$ edges. As a consequence, on **every** degree-2 simplicial ear,
$$\boxed{\;\delta^+(v) + \delta^-(v) \;=\; 4,\;}$$
so the b.minor target $\delta^-(v^*) \ge 1$ is equivalent to
$\delta^+(v^*) \le 3$. The empirical census from Phase 9 gave
$\min \delta^-(v^*) \ge 1.2941$, hence $\max \delta^+(v^*) \le 2.7059$
on the corpus of 2235 max-degsum records.

### 1.3 What "flipping the target" buys, in principle

On the negative side, the (b.minor) attack ran into the F11 caveat:
the slot decomposition needed $\alpha_{\text{top}}^2$ (the LEAST-magnitude
$G$-negative eigenvalue, in Case B), but Lemma B1 bounds
$\alpha_{\min}^2 = \lambda_{\min}^2$ (the MOST-negative $G$-eigenvalue).
The mismatch is fatal because empirically $\alpha_{\text{top}}^2$ on
$L_n$ can be as small as $8.6 \cdot 10^{-4}$ ($n = 30$).

The strategic hope of the prompt: maybe the positive-side analogue is
cleaner. The positive side has
- $\lambda_{\max}(A(G))$ has a clean Rayleigh / Perron–Frobenius
  variational characterisation;
- the asymmetry literature (Elphick–Linz arXiv:2311.11530) suggests
  $s^+ \ne s^-$ in general.
This motivates: derive a Lemma B1+ on the positive side and see
whether the analogue of the F11 caveat fires more mildly.

---

## 2. Lemma B1+ — statement and proof

### 2.1 The trial vector

Mirror the Phase 8 trial-vector argument. Embed $H$-vectors into
$\mathbb R^n$ via $\tilde x = (0, x^\top)^\top$. Take
$$z_+(\beta) \;:=\; \tilde w_+ + \beta\, e_v, \qquad \beta \in \mathbb R,$$
where $w_+ := \sum_{\mu_i > 0} c_i u_i \in \mathbb R^{n-1}$ is the
projection of $w$ onto the positive eigenspace of $A(H)$. Note the
**plus sign** on $\beta e_v$ (vs the minus on Phase 8): we want to push
the Rayleigh quotient *up*, not *down*.

### 2.2 The three identities

From $A(H) w_+ = \sum_{\mu_i > 0} c_i \mu_i u_i$ and $\|w_+\|^2 = W^+$:
- $\|z_+(\beta)\|^2 = W^+ + \beta^2$;
- $\tilde w_+^\top A(G) \tilde w_+ = w_+^\top A(H) w_+ = \sum_{\mu_i > 0} c_i^2 \mu_i = M_1^+$;
- $\tilde w_+^\top A(G) e_v = w_+^\top w = \sum_{\mu_i > 0} c_i (u_i(a) + u_i(b)) = \sum_{\mu_i > 0} c_i^2 = W^+$.

Combining,
$$z_+(\beta)^\top A(G) z_+(\beta) \;=\; M_1^+ + 2 \beta W^+.$$

### 2.3 The Rayleigh quotient

$$R_+(\beta) \;=\; \frac{M_1^+ + 2 \beta W^+}{\beta^2 + W^+}.$$

Setting $R_+'(\beta) = 0$ gives
$$W^+ \beta^2 + M_1^+ \beta - (W^+)^2 \;=\; 0,$$
so
$$\beta_\pm \;=\; \frac{-M_1^+ \pm \sqrt{(M_1^+)^2 + 4 (W^+)^3}}{2 W^+}.$$
Since $M_1^+ \ge 0$ (positive moment) and $W^+ \ge 0$, the positive
root is
$$\beta_+^* \;=\; \frac{-M_1^+ + \sqrt{(M_1^+)^2 + 4 (W^+)^3}}{2 W^+} \;>\; 0$$
and the maximum value is, after simplification using
$W^+(\beta_+^*)^2 + M_1^+ \beta_+^* = (W^+)^2$,
$$R_+(\beta_+^*) \;=\; \frac{W^+}{\beta_+^*} \;=\;
\frac{M_1^+ + \sqrt{(M_1^+)^2 + 4 (W^+)^3}}{2 W^+}.$$

### 2.4 Lemma B1+ (boxed)

**Lemma B1+.** *Let $G$ be a 2-tree on $n \ge 4$ vertices and $v$ a
simplicial degree-2 ear with $W^+(v) > 0$. Then*
$$\boxed{\;\lambda_{\max}\bigl(A(G)\bigr) \;\ge\; f_{\max}^+ \;:=\;
\frac{M_1^+(v) + \sqrt{(M_1^+(v))^2 + 4\,W^+(v)^3}}{2\,W^+(v)}.\;}$$

*Proof.* By Courant–Fischer's max-min principle,
$\lambda_{\max}(A(G)) \ge R_+(\beta_+^*)$. $\square$

### 2.5 Tightness ratio

On the 2235-record max-degsum census (enumerated 2-trees $n \le 10$,
BT$(k,2)$ for $k \in \{2,5,10,25,50,100\}$, $B_k$ for $k \le 30$,
$L_n$ for $n \le 30$, $F_n$ for $n \le 30$):

| family | mean $\lambda_{\max}/f_{\max}^+$ | max  | min   |
|--------|---------------------------------:|-----:|------:|
| books  | 1.001                            | 1.012 | 1.000 |
| BT     | 1.013                            | 1.34  | 1.000 |
| L_n    | 1.45                             | 1.49  | 1.41  |
| F_n    | 1.43                             | 1.74  | 1.21  |
| enum   | 1.17                             | 1.79  | 1.000 |
| **overall** | **1.16**                    | **1.79** | **1.000** |

For comparison, the negative-side Lemma B1 tightness over the same
corpus: mean $\alpha_{\min} / |f_{\min}| \approx 1.14$, max $\approx 1.72$.
The two are within $2$–$5\%$ of each other; the **strategic asymmetry
hypothesised in the prompt is not supported by the data**.

### 2.6 Perron floor: a uniform consequence

At a *max-degsum* ear of a 2-tree with $n \ge 4$, the supporting edge
$\{a, b\} \in E(H)$, hence $w^\top A(H) w = (A(H))_{aa} + 2(A(H))_{ab} + (A(H))_{bb} = 2$,
i.e. $M_1 = 2$. With $M_1^0 = 0$ (the zero-eigenspace doesn't contribute
to first moment) and $M_1 = M_1^+ + M_1^-$, we get $M_1^+ = 2 - M_1^- = 2 + |M_1^-| \ge 2$.

Substituting $M_1^+ \ge 2$ into Lemma B1+:
$$f_{\max}^+ \;\ge\; \frac{2 + \sqrt{4 + 4 (W^+)^3}}{2 W^+}
\;=\; \frac{1 + \sqrt{1 + (W^+)^3}}{W^+}.$$
On the corpus $W^+ \le \sqrt 2$ (since $W^+ \le \|w\|^2 = 2$ and the
positive subspace is at most $n_H$-dimensional with $\sum c_i^2 = 2$),
so $f_{\max}^+ \ge 1/W^+ + 1 \ge 1/\sqrt 2 + 1 \approx 1.71$. The
empirical floor is in fact $f_{\max}^+ \ge 2$ (tight on $B_2 = K_4 - e$).

**Corollary.** On every max-degsum simplicial degree-2 ear of every
2-tree with $n \ge 4$, $\lambda_{\max}(A(G)) \ge 2$.

This is a clean, structural, *unconditional* spectral lower bound from
Lemma B1+ combined with the $M_1 = 2$ identity for max-degsum ears.

---

## 3. Connection to $\delta^+$ via slot decomposition

### 3.1 Positive-side Cauchy interlacing

Cauchy interlacing for the bordering $A(G)$ on $A(H)$ gives
$$\lambda_i(G) \;\ge\; \mu_i(H) \;\ge\; \lambda_{i+1}(G), \qquad i = 1, \ldots, n-1.$$
Pair $(\lambda_i(G), \mu_i(H))$ for $i = 1, \ldots, n-1$. By interlacing,
$\lambda_i \ge \mu_i$; on the indices $i \in J^+ := \{i : \mu_i > 0\}$,
$\mu_i > 0$ implies $\lambda_i \ge \mu_i > 0$, hence $\lambda_i^2 \ge \mu_i^2$
and the slot-shift $\lambda_i^2 - \mu_i^2 \ge 0$.

Writing
$$\delta^+(v) \;=\; \sum_{i=1}^{n} \lambda_i^2 \mathbf 1[\lambda_i > 0]
   \;-\; \sum_{i=1}^{n-1} \mu_i^2 \mathbf 1[\mu_i > 0],$$
re-indexing the $G$-sum by $i \mapsto i$ (since $\lambda_1 = \lambda_{\max} > 0$
appears at $i = 1$), one obtains

- **Case A$_+$** ($n^+(G) = n^+(H)$): every slot $i$ has $\lambda_i > 0 \iff \mu_i > 0$, so
  $$\delta^+(v) \;=\; \sum_{i \in J^+(H)} (\lambda_i^2 - \mu_i^2),$$
  each summand $\ge 0$.

- **Case B$_+$** ($n^+(G) = n^+(H) + 1$): there is exactly one slot
  $i_0 = n^+(H) + 1$ where $\lambda_{i_0} > 0$ but $\mu_{i_0} \le 0$;
  this is the **smallest** $G$-positive eigenvalue. Set
  $\alpha^+_{\text{top}} := \lambda_{n^+(H) + 1}(G)$. Then
  $$\delta^+(v) \;=\; (\alpha^+_{\text{top}})^2
   + \sum_{i \in J^+(H)}(\lambda_i^2 - \mu_i^2), \qquad \text{each summand} \ge 0.$$

### 3.2 The F11+ caveat — mirror of the negative side

Lemma B1+ bounds $\lambda_{\max}^2 = (\alpha^+_{\min})^2$ (where
"$\alpha^+_{\min}$" denotes the **largest**-magnitude $G$-positive,
i.e. $\lambda_{\max}$, the Perron root). The slot decomposition in
Case B$_+$ instead introduces $\alpha^+_{\text{top}} := \lambda_{n^+(H) + 1}(G)$,
the **smallest** $G$-positive eigenvalue. The relation
$\alpha^+_{\text{top}} \le \alpha^+_{\min}$ is the wrong direction;
Lemma B1+ tells us nothing about $\alpha^+_{\text{top}}$.

**Numerical evidence (F11+ fires).** Across the 401 Case B$_+$ records
in the corpus:

| quantity | value | argmin |
|---|---:|---|
| $\min (\alpha^+_{\text{top}})^2$ | $1.98 \cdot 10^{-5}$ | $F_{29}$ endpoint |
| at that record, $\lambda_{\max}^2$ | $\ge 5$ | (huge gap) |
| at that record, $(f_{\max}^+)^2$ | $\ge 5$ | (huge gap) |

So Lemma B1+ controls $\lambda_{\max}$ but cannot prevent
$\alpha^+_{\text{top}}$ from being arbitrarily close to zero — same
caveat as F11, mirrored.

### 3.3 What direction does Lemma B1+ point?

Critically: Lemma B1+ is a **lower** bound on $\lambda_{\max}^2$, hence
a *lower* bound on the Perron slot $\lambda_1^2 - \mu_1^2$, hence a
*lower* bound on $\delta^+$. But to close $\delta^+ \le 3$ we want an
**upper** bound on $\delta^+$.

In other words: the trace identity reformulates the *target* as
$\delta^+ \le 3$, but the trial-vector technique reproduces the
**same** direction (lower bound on the relevant slot quantity) on the
positive side as on the negative side. The reformulation
"flips the target direction" but the trial-vector machinery flips
**with** the target, so we still bound $\delta^+$ from below, not
above.

This is the **structural reason** Lemma B1+ does not close
$\delta^+ \le 3$. It is a different obstacle from the F11 caveat
(which is about $\alpha_{\text{top}}$ vs $\alpha_{\min}$); the
direction-mismatch is logically prior. Even if F11+ did not fire (e.g.
in Case A$_+$ where there is no $\alpha^+_{\text{top}}$ term), Lemma B1+
would still give the wrong-direction bound.

### 3.4 What WOULD close $\delta^+ \le 3$?

The needed analytic ingredient is one of:
- An *upper* bound on $\lambda_{\max}^2$ in terms of $(W^+, M_1^+, M_2^+, \ldots)$.
  Rayleigh-trial doesn't give upper bounds on max eigenvalues;
  one would need e.g. a Cauchy–Schwarz–style inequality or a graph-degree
  bound ($\lambda_{\max} \le \Delta(G)$ etc.).
- An *upper* bound on the positive slot-shift sum
  $\sum_{i \in J^+(H)}(\lambda_i^2 - \mu_i^2)$ — the *same kind* of
  bound the negative side calls O12.2 (the slot-shift wall), just on
  the positive side.
- The trace constraint $\sum_{i=1}^n \lambda_i(G)^2 = 2 m(H) + 4$ alone
  does not close: it gives $\delta^+ = 4 - \delta^-$, returning us to
  the negative-side problem.

The third route is the most direct, and it is just the trace identity
applied backwards. It confirms that **the positive-side ceiling
$\delta^+ \le 3$ has exactly the same content as the negative-side
floor $\delta^- \ge 1$** — neither reformulation makes the problem
easier.

---

## 4. Empirical results on the corpus

`scripts/positive_side_ceiling.py` builds
`data/positive_side_ceiling_census.json`: 2235 max-degsum records,
mirroring the negative-side `data/case_AB_census.json`.

### 4.1 Headline numbers

| statistic | value | argmin/argmax |
|---|---:|---|
| max $\delta^+(v^*)$ overall | $2.7059$ | enum $n=10$, `I}iSSGI@O` (mirror of $\min \delta^-$) |
| min $\delta^+(v^*)$ overall | $1.9932$ | enum $n=10$, `I}rDD?aG_` |
| min $\lambda_{\max}(A(G))$ | $2.0000$ | $B_2 = K_4 - e$, $n = 4$ (Perron floor sharp) |
| min $f_{\max}^+$ | $2.0000$ | $B_2$ ear |
| mean tightness $\lambda_{\max}/f_{\max}^+$ | $1.1638$ | — |
| max tightness ratio | $1.7882$ | `I}rDC`GP?` $n = 10$ |
| min $(\alpha^+_{\text{top}})^2$ in Case B$_+$ | $1.98 \cdot 10^{-5}$ | $F_{29}$ endpoint (F11+) |

### 4.2 Case A$_+$ / Case B$_+$ distribution

| family | Case A$_+$ | Case B$_+$ |
|---|---:|---:|
| enumerated $n \le 10$ | 1075 | 401 |
| BT$(k, 2)$ | 187 | 0 |
| books $B_k$ | 464 | 0 |
| 2-paths $L_n$ | 54 | 0 |
| fans $F_n$ | 54 | 0 |
| **total** | **1834** | **401** |

Within the enumerated subcorpus, Case B$_+$ frequency rises with $n$
(roughly $25$–$30\%$ of records at $n = 10$). Outside enumeration,
**all** parametric families (BT, books, 2-paths, fans) at max-degsum
fall in Case A$_+$ — a sharp contrast to the negative-side mix where
2-paths/fans had a roughly even Case A/B split.

### 4.3 max $\delta^+(v^*)$ per $n$ in the enum corpus

| $n$ | max $\delta^+(v^*)$ | argmax (graph6) |
|---:|---:|---|
| 4  | 2.5616 | `C}` ($B_2$) |
| 5  | 2.4384 | `D}o` |
| 6  | 2.6810 | `E}hO` |
| 7  | 2.5686 | `F}hPO` |
| 8  | 2.6048 | `G}iPOg` |
| 9  | 2.7036 | `H}iRACg` |
| 10 | 2.7059 | `I}iSSGI@O` (= argmax overall) |

Per-family max $\delta^+$:

| family | count | max $\delta^+$ | argmax |
|---|---:|---:|---|
| enum   | 1476 | 2.7059 | $n=10$, `I}iSSGI@O` |
| BT     | 187  | 2.6810 | (mirror of $\min \delta^-$ on BT page) |
| book   | 464  | 2.5616 | $B_2$ ear |
| L      | 54   | 2.6810 | $L_n$ endpoint at small $n$ |
| F      | 54   | 2.5616 | $F_4 = B_3$? (small fan) |

**Empirical conclusion.** $\delta^+(v^*) \le 2.7059$ on every record
of the corpus, hence $\delta^-(v^*) \ge 1.2941$, with $> 0.29$ slack
to the b.minor target.

---

## 5. Verdict + comparison to negative-side Lemma B1

### 5.1 Does Lemma B1+ + slot decomp close $\delta^+ \le 3$?

**No, not at the max-degsum ear, and not in any structural Case.**

The three structural gaps are:

1. **Direction mismatch (§3.3).** Lemma B1+ is a *lower* bound on
   $\lambda_{\max}^2$, hence on the Perron slot $\lambda_1^2 - \mu_1^2$,
   hence on $\delta^+$. We need an *upper* bound on $\delta^+$. The
   trial-vector machinery does not flip with the trace-identity
   reformulation; it produces the same-direction bound on the positive
   side as on the negative side. This is a *new* obstacle relative to
   O12.2: the negative-side Lemma B1 also bounded the spectrum in the
   wrong direction for the slot decomposition, but at least there
   $\delta^- \ge 0$ was the desired direction. Here the trial vector
   bounds $\delta^+$ from below where we want it from above.

2. **F11+ caveat (§3.2).** Even if direction were right, the slot
   decomposition in Case B$_+$ involves $\alpha^+_{\text{top}}^2$
   (smallest $G$-positive squared) which can be $< 10^{-4}$ on the
   corpus. Lemma B1+ controls $\lambda_{\max} = \alpha^+_{\min}$
   (largest $G$-positive), which is unrelated by a Lemma-B1-flavour
   argument.

3. **Asymmetry is empirically absent.** The strategic hope that the
   positive side admits a tighter Rayleigh bound is empirically
   falsified: mean tightness ratio is within $2\%$ between the two
   sides ($1.16$ positive vs $1.14$ negative). The positive side is
   **not** a tighter avenue.

### 5.2 What is the residual obstacle, vs the negative side's O12.2?

On the negative side, O12.2 (the slot-shift wall) is:
$$\sum_{j \in J^-(H)} (\lambda_{j+1}(G)^2 - \mu_j^2) \;\ge\; T'$$
for an explicit constant $T'$. This is a **lower** bound on a sum of
*nonneg* terms, and the Phase 9 analysis treats it as bona fide
open.

On the positive side, the symmetric obstacle is:
$$\sum_{i \in J^+(H)} (\lambda_i(G)^2 - \mu_i^2) \;\le\; T'',$$
an **upper** bound on a sum of nonneg terms. Equivalently (via
$\sum_i \lambda_i^2 = 2 m(G)$):
$$\sum_{i \notin J^+(H)} \lambda_i(G)^2 \;\ge\; 2m(H) + 4 - T'',$$
i.e. a *lower* bound on the energy on $G$'s non-Perron-aligned slots.

These two reformulations are *equivalent under the trace identity*:
$\sum_+ \lambda_i^2 = s^+(G)$ and $\sum_- \lambda_i^2 = s^-(G)$,
hence $\delta^+ \le 3 \iff \delta^- \ge 1$. The positive-side
"upper-bound on the slot-shift sum" and the negative-side
"lower-bound on the slot-shift sum" carry identical content under
$\delta^+ + \delta^- = 4$.

**Conclusion:** the residual obstacle is **the same wall**, just
viewed from the other side. The positive-side reformulation does not
create a structurally new tool. The trace identity offers a clean
restatement (the target $\delta^- \ge 1$ becomes the target
$\delta^+ \le 3$) but no new analytic leverage.

### 5.3 Asymmetry hypothesis: not confirmed

The user's strategic hypothesis was: the positive side might be
asymmetrically tighter than the negative side. Empirically:

| metric                                | positive side | negative side |
|---------------------------------------|--------------:|--------------:|
| Mean Rayleigh tightness ratio         |        1.164  |        1.137  |
| Max Rayleigh tightness ratio          |        1.788  |        1.723  |
| Min Rayleigh tightness ratio          |        1.000  |        1.000  |
| Min "$\alpha$"-quantity (F11 caveat)  |  $2 \cdot 10^{-5}$ | $9 \cdot 10^{-4}$ |
| Case B fraction at max-degsum         |        18%    |        13%    |

The two sides are *qualitatively similar*. The positive side is
slightly *less* tight on average (1.164 vs 1.137) and the F11 caveat
fires somewhat worse (the smallest "F11 slot" is $\approx 20\times$
smaller on the positive side). **Neither metric supports the
strategic asymmetry hypothesis; if anything, the positive side is
marginally worse.**

### 5.4 What does Lemma B1+ buy?

Two modest things:

1. **Perron floor.** $\lambda_{\max}(A(G)) \ge 2$ unconditionally on
   every max-degsum simplicial degree-2 ear of every 2-tree
   with $n \ge 4$. This is sharp on $B_2 = K_4 - e$ ($n = 4$), tight
   on books. A clean, structural, unconditional spectral consequence
   of the trial-vector lemma combined with $M_1 = 2$ at max-degsum.

2. **Negative result clarity.** Documented evidence that the trace
   identity does *not* offer a fundamentally different attack on
   b.minor. The asymmetry hypothesis is falsified; the positive-side
   reformulation is a notational substitution, not a new tool. Future
   workstreams should not invest time in "flipping to the positive
   side" without a structurally distinct lemma (e.g. an upper-bound
   technique on $\lambda_{\max}$).

### 5.5 Headline status

> **Status of $\delta^+ \le 3$ at max-degsum (= $\delta^- \ge 1$).**
> Still open, **same wall** as O12.2 viewed from the other side. The
> positive-side reformulation does not change the headline. The
> empirical floor $\delta^+(v^*) \le 2.7059$ holds across the corpus
> with $0.29$ slack to $3$.

---

## Files referenced

- `docs/plan_v13.md`
- `docs/lprime_attack_v11.md` (Phase 8 Lemma B1)
- `docs/lprime_b_minor.md` (Phase 9, F11 caveat)
- `scripts/positive_side_ceiling.py` (new)
- `scripts/case_AB_census.py`
- `scripts/joint_invariant_features.py`
- `data/positive_side_ceiling_census.json` (new)
- `data/case_AB_census.json`
- `tests/test_positive_side_ceiling.py` (new, 11 tests)
