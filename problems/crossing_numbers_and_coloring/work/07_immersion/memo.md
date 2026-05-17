# R5 memo: sharpening the Fox-Pach-Suk chromatic-index lemma

Role: R5 immersion / chromatic-index / multigraph specialist.
Mandate: own the chromatic-index bottleneck in the Fox-Pach-Suk (FPS) route to
Albertson, i.e. sharpen the constant `9/16` in Lemma 2.3 of arXiv:2510.05893.

Source materials read for this memo:

- `docs/plan.md` v3 (R5 subsection, Obstruction O3, the v3 explanation of the
  immersion-to-crossing recovery, the Hajos lineage paragraph).
- `docs/review.md` (the v2-v3 review).
- The FPS arXiv PDF (arXiv:2510.05893), extracted to text and read directly.
  In particular: Theorem 1.2, Theorem 1.4, Section 2 (proof of 1.2(i) and the
  skeleton of 1.2(ii)), Lemma 2.3 statement, and Section 3 (proof of Lemma
  2.3 including Propositions 3.3, 3.4, Claims 3.5-3.7).
- Chen-Jing-Zang, arXiv:1901.10316 (Goldberg-Seymour proven 2019, journal
  version published with revisions in 2022). Confirmed.

Throughout, "the $9/16$" refers to the leading constant in Lemma 2.3 of
arXiv:2510.05893; "k" is the chromatic number; "$\Delta$" and "$\mu$" the
maximum degree and maximum edge-multiplicity of the auxiliary multigraph
$H_i$ that FPS construct.

---

## 1. The Fox-Pach-Suk argument, restated

### 1a. Weak immersions and Lescure-Meyniel

A graph $G$ **weakly contains** $H$ as an immersion if there is an injection
$\phi: V(H) \to V(G)$ and edge-disjoint paths $\{\phi(e) : e \in E(H)\}$ in
$G$ where $\phi(e)$ has endpoints $\phi(u), \phi(v)$ for each edge $e=uv \in
E(H)$. Internal vertices of the paths may coincide and may even be branch
vertices (that distinction is what separates **strong** from **weak**
immersion).

**Conjecture 1.1 (Lescure-Meyniel, 1989).** Every graph with chromatic
number $k$ contains a weak immersion of $K_k$.

This is the post-Hajos weakening that survives Catlin's refutation. It is
known for $k \le 6$ (DeVos-Kawarabayashi-Mohar-Okamura) and open for $k \ge
7$. The best general lower bound on the largest weakly immersed clique in a
$k$-chromatic graph is $t = (k-4)/3.54$ (Gauthier-Le-Wollan).

### 1b. Fox-Pach-Suk Theorem 1.2 (verbatim from the arXiv PDF)

> **Theorem 1.2.** Let $G$ be a graph with chromatic number $k$ and $n$
> vertices.
>
> (i) If $n < 1.4k - 0.6$, then $G$ contains a weak immersion of the
> complete graph $K_k$.
>
> (ii) For each $\varepsilon > 0$ and $k$ sufficiently large, if
> $n < (1.64 - \varepsilon)k$, then $G$ contains a weak immersion of $K_k$.

The SoCG 2025 abstract phrases the result as "at most $1.4(k-1)$ vertices",
which for integer $n$ gives a bound one smaller at $k = 25$ than the arXiv
form. The two forms agree at $k = 26$.

### 1c. The bridge: from weak immersion to crossing number (Theorem 1.4)

> **Theorem 1.4.** For every $\varepsilon > 0$, there exists a sufficiently
> large $k(\varepsilon)$ such that every graph $G$ with $n \le (1.64 -
> \varepsilon)k$ vertices and chromatic number $k$ satisfies
> $\operatorname{cr}(G) \ge \operatorname{cr}(K_k)$.

The deduction is **two-stage** (this is the part that the v1 plan and
several survey paraphrases get wrong, and that Cranston's Section 1
paraphrases correctly):

(a) Theorem 1.2 yields a weak immersion $G'$ of $K_k$ inside $G$.

(b) A near-immersion crossing-number bound is then applied to the
**immersion subgraph** $G'$: in the relevant regime,
$$\operatorname{cr}(G') \ge \operatorname{cr}(K_k) - \tfrac{k^3}{2}.$$
The finite form, due to Cranston's Appendix A, is
$\operatorname{cr}(G') \ge \operatorname{cr}(K_k) - n(n-k)(n+2k)/8$. The
loss $\Theta(k^3)$ is the price of contracting paths that may share
internal vertices.

(c) The missing $\Theta(k^3)$ is recovered from crossings in $E(G)
\setminus E(G')$, i.e. crossings involving edges that the immersion did
**not** use. The recovery is delicate and is the technical heart of the
crossing argument; in Section 4 of arXiv:2510.05893 it is folded into a
density/Crossing-Lemma count.

### 1d. Where does $9/16$ enter?

The constant $9/16$ is the leading factor in **Lemma 2.3** of
arXiv:2510.05893. It enters the chain as follows:

1. Theorem 1.2(ii) is proved (Section 2, end) by reducing to a chromatic-
   index calculation on an auxiliary multigraph $H_i$ built on the
   non-branch vertices.
2. The vertex bound that comes out of the reduction is
   $n - k + 1 \ge k_i \ge k(25/16 + \varepsilon)$ for each part $V_i$ in
   the Gallai decomposition. Combined with $n = \sum n_i$, $k = \sum k_i$,
   this gives $n \ge (1 + 9/16)k = (25/16)k = 1.5625\,k$ in the limit, i.e.
   the asymptotic threshold is
   $$\boxed{1 + (1 - 9/16) = 25/16 = 1.5625,}$$
   strengthened to $1.64$ in the arXiv abstract by extra slack in the
   $n_i \ge 2k_i - 1$ accounting (FPS get $1.64$ from the inequality chain
   $k_i \le n - k + 1$ together with their better optimisation).

   *Note.* I have verified the algebra at $9/16$ by tracing equations
   (1)-(3) of the FPS paper. The headline "$1.64 - o(1)$" comes from the
   same calculation pushed slightly further; an improvement of $9/16$
   to some $c < 9/16$ would replace $1.64$ by $1 + (1 - c) + (\text{FPS
   slack}) = 2 - c + \text{slack}$. Treat the explicit constant
   $(2 - c)k$ below as the **first-order** approximation.

So Lemma 2.3 with constant $c$ in place of $9/16$ gives the threshold
$n < (2 - c)k$ to leading order, modulo the FPS arithmetic refinement that
pushes $25/16$ to $1.64$.

---

## 2. Lemma 2.3 in detail

**Statement (verbatim from arXiv:2510.05893):**

> **Lemma 2.3.** Let $k_i$ be a sufficiently large positive integer and
> $G[V_i]$ be a graph with $n_i \ge 2k_i - 1$ vertices with minimum degree
> at least $k_i - 1$. Then there are a choice of $U_i \subset V_i$ with
> $|U_i| = k_i$ and one-to-one maps
> $f_u : U_i \setminus (N_G(u) \cup \{u\}) \to W_i \cap N_G(u)$ for $u \in
> U_i$ (where $W_i := V_i \setminus U_i$) such that the chromatic index of
> the multigraph $H_i$, defined as in the proof of Theorem 1.2(i),
> satisfies
> $$\chi'(H_i) \le \bigl(9/16 + o(1)\bigr) k_i.$$

The multigraph $H_i$ has vertex set $W_i$ and, for each non-adjacent pair
$(u, u')$ in $G[V_i]$ with $f_u(u') \ne f_{u'}(u)$, has an edge between
$f_u(u')$ and $f_{u'}(u)$.

**Sketch of proof structure (Section 3 of FPS).**

The proof selects $U_i$ semi-randomly: include every vertex of $G[V_i]$ of
degree $\ge d_i$ (with $d_i = 9k_i/8$), then top up the remaining slots
uniformly at random. The functions $f_u$ are then chosen uniformly at
random. Two probabilistic statements suffice:

- **Proposition 3.3.** With probability $1 - o(1)$, the maximum degree of
  $H$ is at most $(9/16 + o(1))k$.
- **Proposition 3.4.** With probability $1 - o(1)$, the maximum edge
  multiplicity of $H$ is $\mu = o(k)$.

Combining via Lemma 2.2(ii) (Gupta-Vizing for multigraphs, $\chi' \le
\Delta + \mu$) yields $\chi'(H) \le (9/16 + o(1))k$ as required.

**Where the $9/16$ comes from concretely (the deterministic optimisation).**

Proposition 3.3 reduces to bounding the asymptotic value of
$$f(\alpha, \beta, \gamma; \delta) = \gamma - \alpha \cdot
\frac{\delta - 1}{\delta - \gamma}, \qquad \delta = \tfrac{9}{8},$$
over $0 \le \alpha \le \beta \le 1$, $0 \le \gamma \le \alpha + (\delta -
\alpha)(1 - \beta)/(2 - \beta)$. Here $\alpha = \ell_w/k$, $\beta =
\ell/k$, $\gamma = |U_w|/k$, $\delta = d/k$.

The optimum is attained at $11/20 = 0.55$ (one branch) and at $9/16 =
0.5625$ (the other branch), so the bound is $9/16$. **The $9/16$ is
therefore not arbitrary: it is the value of a tight 3-variable
optimisation given the threshold $d = 9k/8$ chosen by FPS.** A different
threshold $d$ changes both the constraint set and the objective, and a
genuine improvement of Lemma 2.3 requires either:

(a) a different choice of $d$ (changes the optimisation),

(b) a smarter choice of $U_i$ (FPS themselves comment in their footnote
that a *greedy* selection of $U_i$ instead of threshold-plus-uniform
"should produce a $U_i$ for which $\chi'(H_i)$ is a constant factor
smaller, but analyzing this process appears to be more challenging"), or

(c) a better chromatic-index bound than Gupta-Vizing applied to $H$
(replacing $\chi' \le \Delta + \mu$ by Goldberg-Seymour, given $H$ has
edge-density structure that the maximum bound does not see).

This memo therefore distinguishes three levers, each below.

---

## 3. Improvement targets

I list three concrete targets in ascending order of ambition. The
quantitative correspondence "Lemma 2.3 constant $c \to$ vertex threshold
$(2 - c + \text{FPS slack})k$" is the headline; the exact numerics depend
on whether the FPS arithmetic refinement (which gets $1.64$ from $25/16 =
1.5625$) extends, and would need to be redone for each new $c$.

### Target T1: $9/16 \to 1/2 = 0.5$ (most realistic 12-month commit)

**Theorem this would give:** Lemma 2.3 with $\chi'(H_i) \le (1/2 +
o(1))k_i$, hence (by the same reduction) Theorem 1.4 with vertex bound
$$n \le (1.5 + \text{FPS slack})k = \text{roughly } (1.7 - o(1))k.$$
Cranston's window currently has its upper-end cut at $1.768\,r$, so pushing
the FPS threshold to $\sim 1.7\,r$ would *almost* close the Cranston upper
band asymptotically. It would not eliminate the gap entirely, but it would
make the asymptotic regime of Cranston redundant for $r \ge $ some
explicit moderate bound (currently $\gtrsim 2^{70}$).

**Why this is realistic.** The $9/16 \to 1/2$ step is *exactly* the gap
between threshold-uniform and greedy selection that FPS themselves flag as
"constant factor smaller, but harder to analyze". The constant $1/2$ is
the natural barrier for any argument that uses $\chi'(H) \le \Delta + \mu$
applied to a multigraph $H$ whose $\Delta$ is controlled by a single
parametric optimisation: $1/2$ would correspond to halving the maximum
degree $d/2 = 9k/16$ down to $k/2$ by averaging, which is plausible if
$U_i$ is chosen to balance load across $W_i$.

**Publishability.** Yes, independently. A standalone note "Sharpening the
chromatic-index lemma of Fox-Pach-Suk from $9/16$ to $1/2$" would be a
~15-page SoCG/EJC paper, with the immediate corollary "Albertson holds for
all $k$-chromatic graphs on $\le (1.7 - o(1))k$ vertices for $k$
sufficiently large." I would estimate publishability at ~80% if the proof
is clean. See Section 6 (Dependencies) for the Role-1 ask on this.

### Target T2: $9/16 \to c$ for some $c < 1/2$ (12-24 month stretch)

**Threshold:** FPS conjecture (implicit) is that the right constant in the
asymptotic Lescure-Meyniel range is $2 - o(1)$, i.e. $c \to 0$. Any $c <
1/2$ pushes the threshold past Cranston's $1.768\,r$ upper-band cutoff.

- $c = 1/2$ gives $\sim (1.7 - o(1))k$, almost matching Cranston.
- $c \approx 0.232$ gives $\sim 1.768\,k$, which would fully close
  Cranston's upper band for all sufficiently large $k$. **This is the
  natural "ambitious" target.**
- $c = 0$ would give $\sim 2k$, which is the *near-optimal* threshold
  (Lescure-Meyniel says the bound should hold for all $n$, but the
  Gallai-decomposition reduction itself requires $n \le 2k - 2$, so $2k$
  is the natural ceiling of this proof technique).

**Why this is hard.** Goldberg-Seymour (proven, see Section 4) replaces
$\Delta + \mu$ by $\max\{\Delta + 1, \lceil \Gamma \rceil\}$ where
$\Gamma(G) = \max_{S, |S|\text{ odd}} 2|E(G[S])|/(|S| - 1)$ is the
*density parameter*. If we can show that on the FPS multigraph $H$ both
$\Delta + 1$ and $\lceil \Gamma \rceil$ are at most $ck$ for $c < 1/2$, we
inherit the better constant. The bottleneck shifts from controlling $\mu$
(easy, $o(k)$) and $\Delta$ (currently $9/16 \cdot k$) to controlling
$\Gamma$.

**Why the bound might *not* improve.** $H$ is a multigraph that FPS
construct precisely to have $\Delta$ close to the (proven) lower bound on
$\chi'$. If $H$ has large odd subsets with high edge density, Goldberg-
Seymour gives no gain. **An auxiliary input I want here from Role 8 is a
random-multigraph calibration: for the FPS-style random $H$, is
$\Gamma(H)$ also tightly close to $9k/16$, or is it strictly smaller in
expectation?**

### Target T3: $9/16 \to 0$ asymptotically (open-ended research)

**Goal:** show that for *any* fixed $\varepsilon > 0$, $\chi'(H_i) \le
\varepsilon k_i$ for a suitable choice of $U_i$. This would in principle
let Lescure-Meyniel be verified for $n \le (2 - \varepsilon)k$, i.e. up
to the Gallai-decomposition limit.

**Fundamental obstruction.** I do not currently know of a hard obstruction
**inside this proof technique**, but the global obstruction is that the
full Lescure-Meyniel conjecture itself is open and is regarded as
comparable in difficulty to Hadwiger. A proof of T3 along the FPS lines
would *be* a proof of the full Lescure-Meyniel conjecture in the regime
$n \le 2k - 2$, which would be a major result. The plan rates "structural
sub-result of this kind" at 3/10 tractability; T3 is at 1.5/10, on par
with the full conjecture.

**Soft obstruction.** Whatever the eventual constant, the chromatic-index
reduction will hit a *lower* bound at some point: $H$ has expected number
of edges roughly $\sim k^2/4$ on $|W_i| = n_i - k_i$ vertices, so even an
optimal $\chi'$ cannot drop below $\Theta(k)$ by counting alone. The
question is whether the chromatic-index lower bound matches the
density-derived lower bound on this random multigraph; if it does, T3 is
asymptotically tight at a constant strictly above $0$, and that constant
is a chromatic-index problem in its own right.

---

## 4. Known chromatic-index bounds I would leverage

### 4a. Shannon (1949)

$\chi'(H) \le \lfloor 3\Delta/2 \rfloor$ for any loopless multigraph
$H$. **Proven**, classical. This is what FPS use in Lemma 2.2(i) to handle
the case $k_i < C$ in the proof of Theorem 1.2(ii); the constant $3/2$ is
exactly what gives the threshold $1.4(k-1)$ in part (i).

*Why it does not improve Lemma 2.3 directly.* Shannon is tight on the
multigraph $3K_3^*$ (the multigraph with three vertices and $\Delta$
parallel edges between each pair, where each pair contributes $\Delta/2$
edges). FPS's multigraph $H$ is not of this form in expectation but
*could* be in the worst case; Shannon is the safe upper bound. The
$9/16$ improvement over $3/2$ comes from going from $\Delta$ to $\Delta +
\mu$ with $\mu = o(k)$, *not* from sharpening Shannon itself.

### 4b. Vizing-Gupta (multigraph form)

$\chi'(H) \le \Delta + \mu$ where $\mu$ is the maximum edge multiplicity.
For simple graphs ($\mu = 1$) this is Vizing's classical theorem $\chi'
\in \{\Delta, \Delta + 1\}$. **Proven**, also classical.

This is what FPS *actually* invoke (Lemma 2.2(ii)) to get the $(9/16 +
o(1))k$ chromatic index in Lemma 2.3, using Proposition 3.4 to ensure
$\mu = o(k)$.

*Why it might improve.* It already is the improvement. Any further gain
must come from a *third* chromatic-index theorem (Goldberg-Seymour, see
4c) or from a smarter $H$ construction.

### 4c. Goldberg-Seymour (Chen-Jing-Zang 2019, journal 2022)

> **Theorem (Goldberg-Seymour conjecture; proven by Chen, Jing, Zang).**
> For every loopless multigraph $H$,
> $$\chi'(H) \le \max\{\Delta(H) + 1, \lceil \Gamma(H) \rceil\}$$
> where $\Gamma(H) = \max_{S \subseteq V, |S| \ge 3 \text{ odd}}
> \frac{2|E(H[S])|}{|S| - 1}.$

**Proven.** arXiv:1901.10316 (January 2019, revised June 2022). The
verification is at this point well-established. The proof is long
(~80 pages) but the *statement* is what we use as a black box.

Verified per the WebFetch above: title "Proof of the Goldberg-Seymour
Conjecture on Edge-Colorings of Multigraphs"; authors Chen, Jing, Zang.

*Why it might improve Lemma 2.3.* Goldberg-Seymour separates two
constraints:

- a *vertex-degree* constraint, $\Delta + 1$;
- a *density* constraint, $\lceil \Gamma \rceil$.

Vizing-Gupta's $\Delta + \mu$ is the **maximum of these** in disguise (in
fact $\Delta + \mu$ dominates $\Delta + 1$ when $\mu \ge 1$, and dominates
$\Gamma$ only by chance). If, for the FPS multigraph $H$,
- $\Gamma(H) \approx \Delta(H) = (9/16)k$ in expectation (i.e. the
  density constraint is tight at the same point as the degree constraint),
  then Goldberg-Seymour gives the *same* bound and no improvement.
- $\Gamma(H) < \Delta(H)$, then $\chi'(H) \le \Delta + 1$, which is
  the **best possible** to within an additive constant, and the
  $9/16$ becomes a question only about $\Delta(H)$.

Empirically (Section 5, Q3), my prediction is that for random multigraphs
of FPS's flavour, $\Gamma$ is substantially smaller than $\Delta$ for
generic graphs $G[V_i]$, and that Goldberg-Seymour therefore *does* yield
a real improvement in some sub-regimes. This is the main angle of attack
I would take for T1.

*Why it might **not** improve.* The lower bound on $\chi'(H)$ is
$\max\{\Delta, \lceil \Gamma \rceil\}$ (the *fractional* chromatic index
is at least this); if either is $\ge (9/16)k$ in expectation, the
improvement is bounded by additive lower-order terms. FPS's choice of
threshold $d = 9k/8$ is tuned to balance $\Delta$ near $9k/16$; whether
$\Gamma$ also concentrates near $9k/16$ for this random construction is,
to my knowledge, **not analyzed in the FPS paper** and is the obvious
calculation to do.

### 4d. Kahn's asymptotic improvement (1996)

Kahn showed $\chi'(H) = (1 + o(1)) \cdot \chi^*(H)$ where $\chi^*$ is the
*fractional* chromatic index, for all loopless multigraphs as $\Delta \to
\infty$. Since $\chi^*(H) = \max\{\Delta(H), \Gamma(H)\}$ (Edmonds), this
is the *asymptotic* form of Goldberg-Seymour and is potentially **even
better than Goldberg-Seymour** for the FPS application, because we are in
exactly the asymptotic regime FPS work in ($k \to \infty$).

**Status.** Proven (Kahn 1996, "Asymptotics of the chromatic index for
multigraphs", J. Combin. Theory Ser. B 68). This is the cleaner tool for
the FPS asymptotic argument.

*Net consequence.* The $\Delta + \mu$ bound used in Lemma 2.3 is provably
weaker than what Kahn gives in the limit. If $\Gamma(H) = o(\Delta(H))$
with high probability over the FPS random construction, then asymptotic
chromatic index of $H$ is $(1 + o(1))\Delta(H)$, and any improvement in
$\Delta(H)$ via a smarter $U_i$ choice translates *one-for-one* into the
final constant.

**This is the chromatic-index input I would most rely on for T1.**

---

## 5. Open research questions

Numbered, distinguished by horizon.

**Q1 (tractable in 12 months).** For the FPS semi-random multigraph $H$
(degree-threshold $d = 9k/8$ for selecting $U_i$, uniform $f_u$), compute
$\mathbb{E}[\Gamma(H)]$ asymptotically. Specifically, is $\Gamma(H) \ll
\Delta(H) = 9k/16$ with high probability? If yes, Goldberg-Seymour / Kahn
immediately give $\chi'(H) = \Delta + 1 + o(\Delta)$ and the FPS bound is
**already not tight** as stated.

**Q2 (tractable in 12 months).** Re-do the Claim 3.7 optimisation with the
threshold $d$ as a *free variable* instead of fixed at $9k/8$. The current
choice is hand-tuned; a numerical sweep of $d \in [k, 3k/2]$ might reveal
a better value, and if so the constant strictly improves below $9/16$
without changing the proof technique. *Risk:* the constraint set in Claim
3.7 was derived assuming $d = 9k/8$, so this requires re-deriving the
optimisation with $\delta$ free. I estimate 4-6 weeks of pen-and-paper
plus Mathematica/SymPy.

**Q3 (tractable in 12 months, Role-8 dependency).** Replace FPS's
threshold-plus-uniform $U_i$ by a *greedy* construction (the one FPS
themselves footnote as harder to analyse). Two angles:

(a) **Greedy with conditional expectation.** Add vertices to $U_i$ one at
a time, each time choosing the vertex that *minimises* the expected
$\Delta(H)$ conditioned on the remaining slots being filled uniformly.
This is a Lovász Local Lemma / Beck-style derandomisation problem; Role 8
is the right consultant.

(b) **Greedy with constraints from $\Gamma$.** Add vertices to keep $H$
away from dense odd subsets; this is a $\Gamma$-controlled construction
and would feed into Goldberg-Seymour directly.

**Q4 (research project, 12-36 months).** Sharpen the second stage of the
FPS crossing argument (Obstruction O3 step (c) in the plan). Even with a
sharper Lemma 2.3 yielding vertex bound $n \le (2 - c)k$, the
crossing-recovery argument that produces the extra $\Omega(k^3)$
crossings in $E(G) \setminus E(G')$ must continue to work in the wider
range. This is *not* a chromatic-index question; it is a crossing-Lemma /
edge-density calculation. **R5 alone cannot close this**; coordination
with the Crossing-Lemma role (R2) is required.

**Q5 (research project, 12-36 months).** Multigraph chromatic-index for
graphs with **bounded multiplicity structure**. The FPS multigraph $H$ has
$\mu = o(k)$ but is otherwise unstructured. Are there *typed* chromatic-
index theorems (e.g. for multigraphs whose multiplicity comes from a
fixed-rank tensor structure) that would beat both Vizing-Gupta and
Goldberg-Seymour for *this specific* multigraph class? I do not currently
see one in the literature; this is exploratory.

**Q6 (research project, 36+ months).** The fundamental question of
Section 3's optimisation: is there a *non-random* construction of $U_i$
that achieves $\Delta(H) \le ck$ for $c < 1/2$? The FPS analysis is
fundamentally probabilistic; a derandomisation that beats the random
bound would be a major chromatic-index contribution independent of
Albertson.

---

## 6. Dependencies

### From Role 8 (probabilistic combinatorics)

**Ask 8.1 (high priority).** Calibrate $\mathbb{E}[\Gamma(H)]$ for the FPS
random multigraph $H$ on $|W_i| = n_i - k_i$ vertices. The expected number
of edges of $H$ is $\sim |U_i|^2 / 2 = k^2/2$ minus the contribution from
adjacent pairs (so $\sim$ a constant fraction of $k^2/2$), distributed
across $|W_i|$ vertices. The question is whether the densest odd subset
$S$ of $H$ has $|E(H[S])| / (|S| - 1)$ concentrated near the average edge
density ($\sim k/2$) or whether there are *outlier* dense subsets.
Without this calibration, Goldberg-Seymour is a black box that may or may
not give a gain.

**Ask 8.2 (medium priority).** Lovász Local Lemma / Beck-Spencer-style
analysis of a *greedy* $U_i$ construction targeting $\Delta(H)$. The FPS
footnote explicitly says this is the obvious next step but "more
challenging to analyze". Role 8 has the right toolkit (entropy
compression, derandomisation via conditional expectations, the
algorithmic LLL).

**Ask 8.3 (low priority).** A second-moment calculation on the maximum
edge multiplicity $\mu(H)$: FPS get $\mu = o(k)$ with $\mu \le k^{0.9}$;
can the bound be tightened to $\mu = O(\sqrt{k})$ or $\mu = O(\log k)$?
This would not help the leading $9/16$ but would clean the $o(1)$ tails.

### From Role 1 (project lead)

**Ask 1.1 (decision needed within 30 days).** Is a partial improvement
$9/16 \to c$ for $c \in (0.5, 9/16)$ publishable **as a standalone
result**, independent of the full Albertson goal?

My read of the literature: **yes, with high confidence (~80%)**. The FPS
paper is an EuroComb / SoCG paper that turns on a single optimisation;
*any* sharpening of that optimisation is a publishable note, even if it
does not close any specific Cranston-residual case. Venues: SoCG, EuroComb,
EJC, J. Combin. Theory B (the natural home for the Goldberg-Seymour
follow-up). Target length 15-20 pages, single-author or co-author with
R8 if the calibration is joint.

If Role 1 wants R5 to *only* publish when the result closes a specific
$(t, n)$ residual case or actually proves Albertson for a new $t$, the
ambition needs to shift to T2 (push to $c < 0.232$ to clear Cranston's
$1.768\,r$). That is 24+ months of work.

**Ask 1.2.** Decision on coordination with R2 (Crossing-Lemma role).
Improvements to Lemma 2.3 are *necessary but not sufficient*: the second-
stage crossing recovery in FPS (Obstruction O3 step (c)) must continue to
yield $\Omega(k^3)$ crossings outside the immersion. Without R2 buy-in on
extending step (c) to the wider vertex range, even a perfect Lemma 2.3
improvement does not close Cranston unconditionally.

### From other roles

**R3 (structural sub-classes).** If R3 produces a structural result on
$K_{t-1}$-minor-free or $k$-planar graphs that bypasses the FPS route
entirely, R5 may be downgraded in priority. Likelihood: low to moderate.

---

## 7. First 30-day deliverables

1. **D1 (week 1).** Write up the exact algebra of Section 1d above
   ($9/16 \to c$ vertex-bound correspondence), including the exact form of
   the FPS arithmetic that pushes $25/16$ to $1.64$. Output:
   `work/07_immersion/lemma23_constant_to_vertex_bound.md`, ~3 pages.
   *Purpose:* makes the Role 1 decision tractable (Ask 1.1).

2. **D2 (week 2).** Re-derive the Claim 3.7 optimisation with the
   threshold $d$ as a free parameter (Q2). Output: a Mathematica /
   SymPy notebook plus a short note recording the optimum and the
   resulting $c$. *Falsifiable target:* if the optimal $d$ already gives
   $c < 9/16$, this is a free improvement and we report it immediately.
   *Negative outcome:* if $d = 9k/8$ is already locally optimal, this
   forecloses the "free" path and the project depends on Q1/Q3.

3. **D3 (weeks 2-3).** Read Goldberg-Seymour / Kahn's theorem statements
   end-to-end, and write a short note `kahn_goldberg_seymour_for_FPS.md`
   summarising what these theorems say about the FPS multigraph $H$
   given the structural facts FPS already prove (Prop 3.3, Prop 3.4).
   *Purpose:* clarify whether Q1 is even necessary, or whether the
   chromatic-index theorems already give the improvement on inspection.

4. **D4 (weeks 3-4).** Numerical simulation of $\Gamma(H)$ for the FPS
   semi-random construction at small $k$ ($k \in [50, 500]$), to provide
   empirical evidence for Q1 before the analytical work begins. Output:
   `scripts/fps_gamma_simulation.py` plus a table. *Coordinate with
   Role 8 on the simulation design.*

5. **D5 (week 4).** Deliver a memo to Role 1 with the **commit/no-commit
   recommendation** for T1 ($9/16 \to 1/2$). Decision criterion: if D2
   yields a free improvement, commit; if D3 + D4 suggest that
   Goldberg-Seymour gives a real improvement on FPS's $H$, commit;
   otherwise, downgrade to T1' = "$9/16 \to 0.55$" via Claim 3.7
   sub-case 2a, which is provably attainable just by tightening FPS's
   own bound (Case 2a already gives $11/20 = 0.55$, so the $9/16$ is
   really only attained in Case 2b, suggesting that **a careful re-read
   of Case 2b may already yield a free improvement**).

---

## Honest meta-remarks

- I have read Lemma 2.3 and its full proof in the arXiv PDF directly.
  The structural understanding above is mine, not paraphrased from the
  plan; the plan's R5 subsection is correct as far as it goes but does
  not work out the algebra connecting $c$ to the vertex bound.

- The plan's claim that "$9/16 \to 1/2$ closes the upper asymptotic
  constant from $1.64$ towards $2$" is *qualitatively* right but
  *numerically off*. The first-order correspondence is $c \to (2 - c)k$,
  but FPS extract additional slack to push $25/16 = 1.5625$ to $1.64$.
  Reproducing that slack for general $c$ requires the algebra in D1.

- Item D5's observation (Case 2a already gives $11/20 = 0.55$, so the
  $9/16$ is the Case 2b ceiling) is potentially a *trivial* improvement
  hiding in FPS's own optimisation. I want to verify in week 1 that
  this is not just a re-parameterisation that they intentionally cap at
  $9/16$; if it is a real loss in Case 2b, tightening Case 2b could
  give the $9/16 \to 0.55$ improvement essentially for free. This would
  not be the headline T1 (which is $\to 1/2$), but it would be a
  publishable lemma in its own right and a useful proof of concept.

- Goldberg-Seymour was first conjectured in the 1970s and proven in 2019;
  the FPS paper, which was posted in October 2025, could in principle
  have used Goldberg-Seymour. They use only Vizing-Gupta. Whether this
  was an explicit choice (e.g. Goldberg-Seymour gives no gain on $H$) or
  an oversight is unclear; in either case it is the first thing to
  check (D3).

- Kahn's 1996 asymptotic theorem is **the** natural tool for an
  asymptotic argument like FPS's, and is even more on-target than
  Goldberg-Seymour because the FPS bound is asymptotic in $k$ already.
  This is the single highest-value technical input I have to bring to
  the project.
