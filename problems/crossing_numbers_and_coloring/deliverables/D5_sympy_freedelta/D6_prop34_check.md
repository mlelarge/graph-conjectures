# D6 — Robustness of FPS Proposition 3.4 (multiplicity bound) under $\delta < 9/8$

**Date.** 2026-05-16.
**Author.** R5a worker.
**Source.** Fox–Pach–Suk, *Immersions and Albertson's conjecture*,
arXiv:2510.05893v1 (7 Oct 2025).  PDF cached at `/tmp/fps_2510_05893.pdf`;
`pdftotext -layout` extraction at `/tmp/fps_2510_05893.txt`.
**Question (single gate).** D5's SymPy verification showed that Claim 3.7's
algebra, with $\delta$ left free, is minimised at $\delta_1 \approx
1.114907541$ with $F^\star \approx 0.557454 < 9/16$. The improvement is
real **iff** every other piece of FPS Lemma 2.3 still goes through at
$\delta = \delta_1$. The most plausibly $\delta$-fragile piece is
**Proposition 3.4** (multiplicity bound $\mu(H) = o(k)$), because the
$\delta = 9/8$ choice was introduced together with the semi-random
construction whose only stated purpose for the random part is precisely
the Prop-3.4 conclusion (FPS footnote 1, p. 6).

**Verdict, up-front.** **GREEN.** Proposition 3.4's proof uses $\delta$ only
through the single inequality $\delta \le 2$ (cf. line 551 of the text
extract: "$kd/\varphi(k) \le 2k^{1.1}$"), which is trivially satisfied at
$\delta_1 \approx 1.115$. The choice $\delta = 9/8$ is a numerical
convenience, not a structural constraint. The D5 improvement is real.
The remainder of this note backs up that verdict with quote-level evidence.

---

## 1. Statement of Proposition 3.4 (verbatim, FPS p. 11)

From `/tmp/fps_2510_05893.txt` lines 396–399:

> **Proposition 3.4.** With probability $1 - o(1)$ the maximum multiplicity
> $\mu = \mu(H)$ of the edges of the multigraph $H$ satisfies
>
> $\quad \mu = o(k)$, as $k \to \infty$.
>
> In the above two propositions, the $o(1)$ terms tend to 0 as $k \to \infty$.

The statement itself is $\delta$-free (it is an asymptotic guarantee on
$H$). Any $\delta$-dependence must enter through the proof.

For completeness, the surrounding setup is fixed at FPS p. 7 (line 349):

> "Let $d := 9k/8 = 1.125 k$. Let $\varphi(k) = o(k)$ be such that
> $\varphi(k)/k \to 0$ sufficiently slowly (for instance, $\varphi(k) =
> k^{.9}$ will do)."

and the cap on the deterministic part of $U$ (footnote 1, p. 6, lines
308–311):

> "if there is more than $k_i - k_i^{0.9}$ vertices of degree at least
> $d_i$, we only pick $k_i - k_i^{0.9}$ of them to be in $U_i$ and pick an
> additional $k_i^{0.9}$ uniform random vertices to fill out the rest of
> $U_i$. Guaranteeing that there is still a reasonable amount of $U_i$ that
> is picked uniformly at random allows us to obtain that with probability
> $1 - o(1)$ the edge multiplicity of $H_i$ is $o(k_i)$."

So Prop 3.4 depends on (i) the cap $|U(d)| \le k - \varphi(k)$, (ii) the
random-fill of size $\ge \varphi(k)$, and (iii) the threshold $d = \delta
k$ via whatever appears in the proof body.

---

## 2. Proof structure (one paragraph)

FPS prove Prop 3.4 in a single self-contained block (lines 542–571), valid
in **both** Cases I and II ("the analysis of $\mu$ below works the same in
both Case I ... and Case II", line 542). They show $\mu \le 3\varphi(k) =
o(k)$ with high probability via three steps:

1. **Step A (preprocessing reduction).** After the edge-swap pre-processing
   and the "ignored edges" device of Prop 3.3, every $u \in U$ behaves as
   if it had degree $\le d$ in $G^\ast$. The number of $w \in W$ with
   $\ge \varphi(k)$ neighbours in $U$ is then at most $kd/\varphi(k) \le
   2k^{1.1}$ (line 551).
2. **Step B (random-fill yields many $W$-neighbours per $u$).** Using the
   cap $\ell \le k - \varphi(k)$ from footnote 1 and the bound $n - k \ge
   \tfrac12(n - \ell)$, each $u \in U$ has expected $\ge (\varphi(k) -
   1)/2$ neighbours in $W$, and by Chernoff $+$ union bound, $\ge
   \varphi(k)/4$ neighbours in $W$ w.h.p. (lines 552–557).
3. **Step C (Azuma on per-pair multiplicity).** For each pair $w, w' \in
   W$ with $\ge \varphi(k)$ $U$-neighbours each — at most $(2k^{1.1})^2 =
   4 k^{2.2}$ such pairs — the probability that
   $f_u(u') = w$ and $f_{u'}(u) = w'$ is $\le (4/\varphi(k))^2$ per pair
   $u, u' \in U$. Hence $\mathbb{E}[Y] \le k^2 (4/\varphi(k))^2 = 16
   k^{0.2}$. Azuma's inequality with bounded differences $\le 2$ then
   gives multiplicity $\le 16 k^{0.2} + 100 (k \log k)^{1/2} \le
   \varphi(k)$ for each pair, with failure probability $\le k^{-3}$. The
   union bound over $4k^{2.2}$ pairs is $o(1)$.

The output is $\mu \le \varphi(k) = k^{0.9} = o(k)$ w.h.p.

---

## 3. Where $\delta$ enters the proof — equation by equation

I now enumerate every occurrence of $d$ (i.e., $\delta k$) or a
$\delta$-derived constant in the proof of Prop 3.4 (lines 542–571).

### 3.1 The "ignored edges" reduction (line 549)

> "this will effectively guarantee that for this purpose the degree of
> each vertex in $U$ is at most $d$."

This is a structural statement: the random-functions construction of
Prop 3.3 reveals at most $d$ edges per $u \in U$. It uses $d$ qualitatively
(every $u$ has $\le d$ revealed edges); the *value* of $d$ is irrelevant
here. **$\delta$-role:** none beyond $d > 0$.

### 3.2 The "high-$U$-degree $W$-vertices" count (line 551)

> "Note that then the number of vertices $w \in W$ adjacent to at least
> $\varphi(k)$ vertices in $U$ is at most $kd/\varphi(k) \le 2k^{1.1}$."

Here the constant **$2$** in $2k^{1.1}$ comes from $kd/\varphi(k) = \delta
k^2 / k^{0.9} = \delta k^{1.1}$, and FPS bound $\delta \le 2$ to get a
clean constant. **The bound $\le 2$ is wildly loose** — any $\delta \le 2$
works equally well (the constant would just change). At $\delta_1
\approx 1.115$, one would write "$\le 1.2 k^{1.1}$" or simply keep
"$\delta k^{1.1}$"; no inequality in the rest of the proof depends on the
numerical value being $2$ vs. $1.125$ vs. $1.115$.

**$\delta$-role:** the proof needs $\delta \le 2$. Any $\delta \in (1, 2)$
suffices. **Not a constraint at $\delta_1 = 1.115$.**

### 3.3 The pair-count (line 562)

> "Fix a pair $w, w' \in W$ of distinct vertices, each of which has at
> least $\varphi(k)$ neighbors in $U$ (there are at most $(2k^{1.1})^2 =
> 4k^{2.2}$ such pairs)."

This is *just the square* of the bound in §3.2 above. **$\delta$-role:**
the same, $\delta \le 2$. The "$4 k^{2.2}$" would become "$\delta^2
k^{2.2}$" at general $\delta$ (so $\approx 1.243 k^{2.2}$ at $\delta_1$);
all downstream bounds carry through the rescaling.

### 3.4 Footnote-1 cap and the random-fill bound (lines 552–557)

> "Each vertex of $G$ (and, hence, each vertex in $U$) has at least
> $k - 1 - \ell \ge \varphi(k) - 1$ neighbors in $V \setminus U(d)$. ...
> $n - k \ge \tfrac12 (n - \ell)$. Hence, for each $u \in U$, the expected
> number of neighbors of $u$ in $W$ is at least $(\varphi(k) - 1)/2$. ...
> each vertex in $U$ has at least $\varphi(k)/4$ neighbors in $W$."

This step uses:
- $\ell \le k - \varphi(k)$ (footnote 1 cap) — **$\delta$-independent**;
- $\deg_G(v) \ge k - 1$ ($G$ is $k$-critical) — **$\delta$-independent**;
- $n \ge 2k - 1$ — **$\delta$-independent**;
- Chernoff/Lemma 3.1(i) — **$\delta$-independent**.

The threshold $d$ does *not* appear here. **$\delta$-role:** none.

### 3.5 The expectation and Azuma bounds (lines 562–571)

> "For each pair $u, u' \in U$, then, the probability that $f_u(u') = w$
> and $f_{u'}(u) = w'$ is at most $(4/\varphi(k))^2$. ... $\mathbb{E}[Y]
> \le k^2 (4/\varphi(k))^2 = 16 k^{0.2}$. ... by Azuma's inequality
> (Lemma 3.1(ii)), the probability that the pair $w, w'$ has edge
> multiplicity at least $100(k \log k)^{1/2}$ is at most $k^{-3}$."

The constant "$4$" in $(4/\varphi(k))^2$ traces back to the random-fill
calculation in §3.4 ("each vertex in $U$ has at least $\varphi(k)/4$
neighbours in $W$"). That "$4$" is itself $\delta$-independent (see §3.4).

The expectation $16 k^{0.2}$ has no $\delta$ dependence; the Azuma bound
$\le 16 k^{0.2} + 100(k \log k)^{1/2}$ has no $\delta$ dependence. The
union bound over $4 k^{2.2}$ pairs introduces only a $\delta^2$ scaling
of the constant prefactor of the failure probability.

**$\delta$-role:** none.

### 3.6 Summary table

| Step / line | Quantity | $\delta$-role | Required constraint |
|---|---|---|---|
| 549 ("ignored edges") | each $u$ has $\le d$ revealed neighbours | qualitative | $d$ is some finite threshold |
| 551 ("$\le 2k^{1.1}$") | $kd/\varphi(k) = \delta k^{1.1}$ | quantitative, but loose | $\delta \le 2$ (any constant works) |
| 552–557 (random fill) | per-$u$ $W$-neighbour count | none | — |
| 562 ($4 k^{2.2}$ pairs) | $(\delta k^{1.1})^2$ | quantitative, but loose | $\delta \le 2$ |
| 564 ($\mathbb{E}[Y] \le 16 k^{0.2}$) | $k^2 (4/\varphi(k))^2$ | none | — |
| 568–570 (Azuma + union bound) | failure probability | none | — |

**Only constraint extracted from the Prop 3.4 proof: $\delta \le 2$**
(and trivially $\delta > 1$, since $d \ge k$ is implicit in calling
"degree at least $d$" a non-trivial threshold). Both are satisfied at
$\delta_1 \approx 1.114907541$.

---

## 4. Admissible $\delta$-range for Prop 3.4

**Claim.** The proof of Prop 3.4 is valid for every $\delta \in (1, 2)$.

**Reason.** Every $\delta$-dependent inequality in the proof body is of
the form $\delta \le c$ for some explicit numerical constant $c \in \{2\}$
(see §3.6). The only quantitative use is the slack bound $\delta k^{1.1}
\le 2 k^{1.1}$, which we may freely rewrite as $\delta k^{1.1} \le C
k^{1.1}$ for any $C \ge \delta$; the downstream Azuma/union argument
absorbs constants via the failure probability $\le k^{-3}$ vs. union over
$\le C^2 k^{2.2}$ pairs.

**Boundary $\delta \to 1$.** The footnote-1 cap requires $\delta$
sufficiently large that the *deterministic* set $U(d)$ is well-defined as
"vertices of degree $\ge d = \delta k$" — meaningful only for $\delta > 1$
(otherwise every vertex of $G$, which has degree $\ge k - 1$, is in
$U(d)$ and the high/low split degenerates). The lower bound is therefore
$\delta > 1$, strict.

**Boundary $\delta \to 2$.** The bound $\delta \le 2$ is needed only to
write "$\le 2 k^{1.1}$" cleanly; at $\delta > 2$ the constant changes but
the asymptotic conclusion $\mu = o(k)$ still holds (provided $\delta$ stays
$< $ some constant). Strictly $\delta \le 2$ is FPS's *cosmetic* bound;
in fact the proof works for any $\delta \le C$ with any fixed $C \ge 1$.

**Conclusion.** Prop 3.4 holds at $\delta = \delta_1 \approx 1.115$
with **no modification** to the proof beyond replacing "$2k^{1.1}$" by
e.g. "$1.2 k^{1.1}$" and propagating the constant through the union
bound (which absorbs it via $k^{-3} \cdot \delta^2 k^{2.2} = o(1)$). The
admissible range is $\delta \in (1, 2)$, and $\delta_1 \in (1, 2)$.

---

## 5. Cross-check on Claims 3.5, 3.6 and Proposition 3.3

D5 already verified Claim 3.7's algebra (the optimisation feeding
Prop 3.3) at general $\delta$. The remaining pieces are Claims 3.5 and
3.6, plus Prop 3.3's Case II.

### 5.1 Claim 3.5 (FPS p. 8, lines 409–414)

> "**Claim 3.5.** With probability $1 - o(1)$, for each vertex $w \in V
> \setminus U(d)$, its number of neighbors in $U$ satisfies
>
> $\quad |U_w| \le \ell_w + (d - \ell_w) \cdot \frac{k - \ell}{2k - \ell -
> 1} + o(k).$" (Equation 4.)

The proof (lines 448–465) applies Lemma 3.2(ii)–(iii) to the random
subset $S = U \setminus U(d)$ of size $s = k - \ell$ inside $F = G^\ast[V
\setminus U(d)]$. The key ingredients:

- "no $w$ exceeds its expected number of neighbors in $S$ by more than
  $\sqrt{n \ln n}$" — **$\delta$-independent**;
- "the upper bound on $|U_w|$ in (7) is decreasing as a function of $n$
  and, hence, is maximized if $n = 2k - 1$" — **$\delta$-independent**;
- "If we are in the case $n \le d^{1.9}$, ... Otherwise, $n > d^{1.9}$,
  and by Lemma 3.2(iii) ... every vertex $w \in V \setminus U(d)$ has
  $|U_w| \le \ell_w + o(k)$" (line 463). This *does* use $d$, but only via
  $d^{1.9} = (\delta k)^{1.9}$, which is $\delta$-monotone but does not
  break: Lemma 3.2(iii) requires $s \le d \le n^{0.9}$, equivalent to
  $\delta \ge 1$ (so $d \ge k \ge s$) and $\delta^{1.9} k^{1.9} \le n$
  in case 2. Both are $\delta$-trivial in the regime $\delta \in (1, 2)$.

**Verdict on Claim 3.5.** Valid for every $\delta > 1$. The asymptotic
form $\gamma \le \alpha + (\delta - \alpha)(1 - \beta)/(2 - \beta)$ used
in Claim 3.7 is recovered with $\delta$ as a free parameter (as D5
already used). **No new constraint.**

### 5.2 Claim 3.6 (FPS p. 8–9, lines 420–498)

> "**Claim 3.6.** With probability $1 - o(1)$, for each vertex $w \in W$,
> its degree in $H$ is at most $k/4$ or at most
>
> $\quad |U_w| - \ell_w \cdot \frac{d - 1 - k}{d - 1 - |U_w|} + o(k).$"
> (Equation 5.)

The proof (lines 468–498) uses the "reduced range" of size $\le d$ for
each $f_u$, applies Chernoff via Lemma 3.1(i) and a union bound. The one
$\delta$-dependent inequality is line 478–479:

> "the number of vertices that can have degree at least $k/4$ in $H$ is
> at most $kd/(k/4) = 4d$."

This requires $4d = 4 \delta k$, and is used at line 490 in the union
bound "the at most $4d < 5k$ vertices $w \in T$". The bound $4d < 5k$
is **$\delta < 5/4 = 1.25$**.

**This is the most $\delta$-fragile inequality in the entire Lemma 2.3
proof.** At FPS's choice $\delta = 9/8 = 1.125$, $4d = 4.5 k < 5k$
with slack $0.5 k$. At $\delta_1 \approx 1.114907541$, $4d \approx 4.4596
k < 5k$ with slack $\approx 0.54 k$. **Satisfied with even more slack.**

In fact the "$4d < 5k$" inequality is also cosmetic: it is used only to
bound a union over "the at most $4d$ vertices $w \in T$", which in
asymptotic terms is "$O(k)$ vertices". Any $\delta = O(1)$ works.

**Verdict on Claim 3.6.** Valid for every $\delta \in (1, 5/4)$ with the
inequality as printed, and trivially for every $\delta = O(1)$ if the
"$5k$" is replaced by "$O(k)$". **Not a constraint at $\delta_1$.**

### 5.3 Proposition 3.3, Case II (FPS p. 10–11, lines 529–540)

> "**Case II:** Suppose $G$ has at least $k - \varphi(k)$ vertices of
> degree at least $d$. Then $\ell = k - \varphi(k)$, where $\varphi(k) =
> k^{.9}$. In this case, we follow the exact argument as in Case I. ...
> apart from the $o(1)$ terms, this becomes a special case (when $\beta =
> 1$) of the optimization problem already studied in Case I. Hence, the
> analysis of this case reduces to that of Case I."

Case II is a reduction to the $\beta = 1$ corner of the Case-I
optimisation. At $\beta = 1$, the Claim 3.5 constraint collapses to
$\gamma \le \alpha + o(1)$, and the objective (6) becomes $\gamma -
\alpha(\delta-1)/(\delta-\gamma)$ over $0 \le \alpha = \gamma \le \delta$
(at the boundary). With $\delta$ free, the resulting one-variable
optimum is $\alpha = \gamma = 0$ (since the objective is increasing in
$\gamma$ but the constraint forces $\gamma = \alpha$, and the corrective
term $\alpha(\delta - 1)/(\delta - \alpha)$ is $0$ at $\alpha = 0$ — i.e.,
the case has degenerate optimum $0$ in the $\beta \to 1$ limit). FPS state
"the analysis of this case reduces to that of Case I"; D5's
$\beta$-sweep at $\delta_1$ confirms this corner is dominated by the
interior $f_{2a}/f_{2b}$ optima.

**Verdict on Case II.** $\delta$-free reduction. **Not a constraint.**

### 5.4 Summary of cross-checks

| Element | $\delta$-constraint extracted | Slack at $\delta_1 = 1.115$ |
|---|---|---|
| Claim 3.5 | $\delta > 1$ | $0.115$ |
| Claim 3.6 ("$4d < 5k$") | $\delta < 5/4 = 1.25$ | $0.135$ |
| Claim 3.7 (Case 1) | $\delta > 0$ | — |
| Claim 3.7 (Case 2a) | $\delta > 1$ | $0.115$ |
| Claim 3.7 (Case 2b) | $\delta > 0$ | — |
| Prop 3.3 Case II | $\delta > 1$ | $0.115$ |
| Prop 3.4 line 551 | $\delta \le 2$ | $0.885$ |
| Prop 3.4 line 562 | $\delta \le 2$ | $0.885$ |

**Aggregate admissible range:** $\delta \in (1, 5/4)$, with all other
constraints having strictly more slack. $\delta_1 \approx 1.114907541 \in
(1, 5/4) = (1, 1.25)$. **All FPS lemmas hold.**

---

## 6. Verdict

**GREEN — Robust.**

The choice $\delta = 9/8$ in FPS is a *numerical convenience* (it makes
Case 1 and Case 2b both evaluate to $9/16$, by happenstance), not a
structural constraint. Proposition 3.4's proof works for every $\delta \in
(1, 2)$; the most restrictive subsidiary lemma is Claim 3.6, which
requires $\delta < 5/4$ as printed. The numerically optimal $\delta_1
\approx 1.114907541$ lies safely inside $(1, 5/4)$ with $\sim 0.12$ of
slack on each side.

**The single sentence from FPS that settles the question** (line 551):

> "Note that then the number of vertices $w \in W$ adjacent to at least
> $\varphi(k)$ vertices in $U$ is at most $kd/\varphi(k) \le 2 k^{1.1}$."

The bound is $\delta k^{1.1} \le 2 k^{1.1}$, i.e. $\delta \le 2$. This is
the *only* place in the Prop 3.4 proof where the numerical value of $d$
(i.e. $\delta$) is invoked, and the slack ($\delta = 1.115$ vs. $\delta
\le 2$) is enormous.

**Consequence for Lemma 2.3.** With $\delta = \delta_1$, FPS's argument
produces

$\quad \chi'(H_i) \le (F^\star + o(1)) k_i$

with $F^\star \approx 0.557454 < 9/16 = 0.5625$. The D5 algebraic
optimum is reachable. **Lemma 2.3 with constant $c \le 0.557454$ holds.**

---

## 7. Implications for D5 and R5a

Since the verdict is GREEN, no re-optimisation of D5 is needed: the
constraint $\delta \in (1, 5/4)$ contains $\delta_1$ strictly, so
$\delta_1$ remains optimal in the Prop-3.4-admissible range, and $F^\star
\approx 0.557454$ is achieved.

**R5a pivot.** The team can move R5a from "verdict mode" to
**"draft an improvement paper"**:

1. **Title (working).** *Tightening the chromatic-index threshold in
   Fox–Pach–Suk's Lemma 2.3.*
2. **Headline result.** Lemma 2.3 holds with $c \le F^\star \approx
   0.557454$, improving FPS's $9/16 = 0.5625$ by $\sim 0.9\%$.
3. **Theorem 1.2 downstream.** Re-derive the vertex coefficient $1.64
   \to ?$ from the improved $c$. (FPS Section 2 derivation, not
   reconstructed here; expected improvement $\sim 0.005$–$0.05$ in the
   coefficient.)
4. **Closed form for $\delta_1, F^\star$.** SymPy `minimal_polynomial`
   on the high-precision numerical root. Listed as a 1-day TODO in D5's
   REPORT.md §"Closed-form status".
5. **Sanity-check the FPS Case-2b sign typo** ($+ 1/\eta$ vs. $- 1/\eta$,
   D3 §8.1) against the SoCG-2025 published version, in case it has been
   corrected.

**Items to mention in the paper (but not blockers).**

- The "$2 k^{1.1}$" bound on line 551 of FPS should be re-stated as
  "$\delta k^{1.1}$" or "$(9/8) k^{1.1}$" for general $\delta$; this is
  a cosmetic edit.
- The "$4d < 5k$" inequality in Claim 3.6 (line 490) should be re-stated
  as "$4 \delta k < 5 k$", with the bound $\delta < 5/4$ flagged
  explicitly. This becomes a *strict* constraint on the admissible
  $\delta$-range.

---

## 8. Things I could not fully verify from the PDF text

1. **The exact derivation of $\alpha^\star = (9 - 3/\eta)/8$ in Case 2a.**
   FPS state it without showing the differentiation (line 510); D5 verified
   it independently in SymPy. **Not a Prop-3.4 issue.**
2. **The "ignored edges" device in the proof of Prop 3.3 (Step 1 of the
   Claim 3.6 reduction, line 473).** "we pick a uniform random subset of
   $d - |N_{G^\ast}(u) \cap U|$ vertices from $W \cap N_{G^\ast}(u)$, and
   we reduce the range of $f_u$ to this random subset." The interpretation
   of this step at general $\delta$ requires $d - |U_u| \ge 0$, i.e.,
   $\delta \ge |U_u|/k$. Since $|U_u| \le k$ trivially and typically much
   smaller, this is fine, but FPS does not write a quantitative bound
   here. **No issue at $\delta_1$.**
3. **The exact statement of Lemma 3.2(iii) hypothesis at general $\delta$**
   (line 463): "we have $n > d^{1.9}$, and by Lemma 3.2(iii) applied to
   $F$ ... every vertex $w \in V \setminus U(d)$ has $|U_w| \le \ell_w +
   o(k)$ neighbors in $U$." Lemma 3.2(iii)'s printed hypothesis (line
   300) is "$s \le d \le n^{0.9}$", which at general $\delta$ requires
   $\delta k = d \le n^{0.9}$, i.e. $\delta \le n^{0.9}/k$. For $n \ge
   2k - 1$ this is $\delta \le (2k - 1)^{0.9}/k \to 0$ as $k \to \infty$,
   which would *fail*. **This is a hypothesis-tracking subtlety I did
   not fully resolve.** However, Claim 3.5 is handled by the
   case-split "$n \le d^{1.9}$ vs. $n > d^{1.9}$" (line 461), and in
   either branch the conclusion (4) is reached; the second branch uses
   Lemma 3.2(iii) with the maximum-degree bound $d$ playing the role of
   the hypothesised "$d$" in 3.2(iii), so the statement "$d \le n^{0.9}$"
   becomes the *opposite* of "$n > d^{1.9}$" — I read this as FPS being
   sloppy about which $d$ is which but logically consistent. **Flagged
   here for completeness; not a Prop-3.4 issue.**

None of these unverified items is a Prop-3.4 issue or a constraint on
$\delta$ tighter than $\delta < 5/4$ (Claim 3.6).

---

## 9. Provenance

- FPS PDF: `/tmp/fps_2510_05893.pdf` (arXiv:2510.05893v1, 7 Oct 2025).
- Text extract: `/tmp/fps_2510_05893.txt` (60 kB, `pdftotext -layout`).
- All quoted line numbers refer to the text extract.
- D5 REPORT: `../REPORT.md` (this directory).
- D3 reconstruction: `../../D3_R5a_reconstruction.md`.

**This note is a paper-reading deliverable only; no Python was run.**
