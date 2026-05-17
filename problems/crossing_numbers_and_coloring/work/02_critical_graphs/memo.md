# Memo — Role 2 (critical-graph / chromatic-graph-theory)

Date: 2026-05-16.
Author: Role 2.
Status: first pass; calibrated to plan.md v3 (2026-05-16) and review.md.
Scope: structural-theory backstop for R1b, R3.6, and a sanity-check log against
plan v3.

This memo is meant to be brutally honest. Where a claim in the wider literature
is folkloric or open, it is marked. Where a claim in plan v3 is mathematically
imprecise it is flagged in Section 4.

---

## 1. What is actually forced for a $t$-critical graph at $t = 25, n = 48$ and $t = 26, n \in \{50, 51\}$

The Cranston Theorem 2 residual triples are
$$(t, n) \in \{(25, 48),\; (26, 50),\; (26, 51)\}.$$
For each of these the structural constraints below are *forced* on any MCE.

### 1.1 Minimum degree

**Theorem (Dirac 1952/1953).** Every $k$-critical graph has $\delta(G) \ge k - 1$.

- Proven. Reference: G.A. Dirac, *A property of 4-chromatic graphs and some
  remarks on critical graphs*, J. London Math. Soc. 27 (1952), 85–92, and
  the elementary "swap a colour" proof reproduced as Lemma 1 of A. Kostochka,
  *Lecture notes on sparse color-critical graphs* (IME-USP 2016, online).
- Consequence: $\delta \ge 24$ at $(25, 48)$ and $\delta \ge 25$ at $(26, 50), (26, 51)$.
- Caveat: this is the minimum degree of the MCE, *not* an upper bound on $\delta$
  or on $\Delta$. The MCE may be far from regular.

### 1.2 Edge-connectivity

**Theorem (Dirac 1953, attributed via "Kopon's proof" in Kostochka's notes).** Every
$k$-critical graph $G$ is $(k - 1)$-edge-connected.

- Proven. Reference: Lemma 1 of Kostochka, *Lecture notes on sparse color-critical
  graphs*, attributing the result to Dirac with the short colour-permutation proof
  by Kopon. **This is Dirac's theorem, not a Kostochka–Stiebitz sharpening.** See
  Sanity-check item 4.1 below.
- Consequence: $\lambda(G) \ge 24$ at $(25, 48)$ and $\lambda(G) \ge 25$ at the
  $t = 26$ pairs.
- Combined with $\delta = k - 1$ this is sharp: at $\delta = k - 1$ the trivial
  cut at a min-degree vertex already attains the lower bound, so the bound is
  *attained* unless every vertex has degree $\ge k$.

### 1.3 Vertex-connectivity (the v2/v3 correction)

**Status: not forced beyond $\kappa(G) \ge 2$.**

- Plan v3 correctly removed the v2 over-claim that $\kappa(G) \ge t - 1 = 24$ for
  a $25$-critical $G$. The correct statement: $k$-critical graphs are
  $2$-connected (folklore, immediate from criticality + connectivity); higher
  vertex-connectivity is *not* in general forced. Kostochka–Yancey's $k$-Ore
  extremal critical graphs explicitly have separators of size $2$ (Theorem 17
  of the Kostochka lecture notes: "every $k$-extremal graph distinct from $K_k$
  has a separating set of size $2$"). So $k$-Ore graphs witness that $\kappa = 2$
  is consistent with $k$-criticality.
- However: an MCE is dense by Cranston ($|G| \le 2.8118 r$ rules out the sparse
  regime where $k$-Ore extremes live with many vertices). At $n = 48, t = 25$
  the density is well above $k$-Ore-extremal, so the *generic* MCE in the residual
  range is structurally far from $k$-Ore. It is therefore *plausible* that small
  vertex cuts can be excluded for these specific $(t, n)$ triples by an ad-hoc
  argument, but no such theorem is in the literature.

### 1.4 Edge-count lower bounds

The tight bound is **Kostochka–Yancey 2014** (arXiv:1209.1050,
J. Combin. Theory Ser. B 109 (2014), 73–101):
$$|E(G)| \;\ge\; F(n, k) := \left\lceil \frac{(k+1)(k-2)\, n - k(k-3)}{2(k-1)} \right\rceil
\qquad (k \ge 4, n \ge k, n \ne k+1).$$
Proven. Equivalently $|E(G)|/n \ge \tfrac{k}{2} - \tfrac{1}{k-1} - O(1/n)$, so
$\phi_k := \lim_{n} f(n,k)/n = \tfrac{k}{2} - \tfrac{1}{k-1}$ (Corollary 15 of
Kostochka's notes).

Plugged into the residual triples:

| $(t, n)$ | $F(n, t)$ | Dirac trivial $\lceil (t-1)n/2 \rceil$ | KY surplus |
|---|---|---|---|
| $(25, 48)$ | $\lceil (26 \cdot 23 \cdot 48 - 25 \cdot 22)/48 \rceil = \lceil (28704 - 550)/48 \rceil = \lceil 586.54 \rceil = 587$ | $576$ | $+11$ |
| $(26, 50)$ | $\lceil (27 \cdot 24 \cdot 50 - 26 \cdot 23)/50 \rceil = \lceil (32400 - 598)/50 \rceil = \lceil 636.04 \rceil = 637$ | $625$ | $+12$ |
| $(26, 51)$ | $\lceil (27 \cdot 24 \cdot 51 - 26 \cdot 23)/50 \rceil = \lceil (33048 - 598)/50 \rceil = \lceil 649.0 \rceil = 649$ | $638$ | $+11$ |

(I have folded the $2(k-1)$ denominator: $2(k-1) = 48$ at $k=25$, $= 50$ at $k=26$.)

So the Kostochka–Yancey bound improves the trivial Dirac edge count by roughly
$11$–$12$ at the residual triples. **This is the strongest edge bound in the
literature and is tight on $k$-Ore graphs.** Plan v3 cites only the Dirac trivial
bound $|E| \ge (t-1)n/2$ — it should cite Kostochka–Yancey instead. See
Sanity-check item 4.2.

Stronger off-extremal bound (Kostochka–Yancey, Theorem 17 of the Kostochka notes):
if $G$ is $k$-critical and *not* a $k$-Ore graph, then
$$|E(G)| \;\ge\; \frac{(k+1)(k-2) n - y_k}{2(k-1)}, \qquad y_k = k^2 - 5k + 2 \text{ for } k \ge 6.$$
At $k = 25$: $y_{25} = 625 - 125 + 2 = 502$, vs. $k(k-3) = 25 \cdot 22 = 550$, so
non-Ore $25$-critical graphs have $|E| \ge \lceil (28704 - 502)/48 \rceil = 588$ —
i.e. one more edge than the bare KY bound. The MCE in the residual is therefore
either $25$-Ore (in which case it has a 2-separator and is highly structured) or
$|E| \ge 588$.

Earlier weaker bounds in the chain (all proven; cited for context):

- Dirac (1957): $2|E| \ge (k-1)n + k - 3$ for $k$-critical $G \ne K_k$
  (Theorem 3 of Kostochka's notes).
- Gallai (1963): $|E(G)| \ge \tfrac{k-1}{2} n + \tfrac{k-3}{2(k^2-3)} n$ via the
  Gallai-tree theorem (Theorem 7 of Kostochka's notes).
- Krivelevich (1997, 1998): $|E(G)| \ge \tfrac{k-1}{2} n + \tfrac{k-3}{2(k^2 - 2k - 1)} n$
  (eq. (18) of Kostochka's notes).
- Kostochka–Stiebitz (1999, 2003): $|E(G)| \ge \tfrac{k-1}{2} n + \tfrac{k-3}{k^2 + 6k - 11 - 6/(k-2)} n$
  for $k \ge 6$ (eq. (19) of Kostochka's notes).

All are dominated by Kostochka–Yancey.

### 1.5 Gallai-tree structure of the low-degree vertex set

**Theorem (Gallai 1963).** Let $G$ be $k$-critical and $B = B(G) = \{v : d_G(v) = k-1\}$
the set of "low" vertices. Then each block of $G[B]$ is either a complete graph
or an odd cycle, i.e. $G[B]$ is a *Gallai tree*.

- Proven. Reference: Theorem 5 of Kostochka's lecture notes; classical proof in
  Gallai's 1963 paper (T. Gallai, *Kritische Graphen I*, Magyar Tud. Akad. Mat.
  Kutató Int. Közl. 8 (1963), 165–192).
- Same conclusion holds for *list*-$k$-critical graphs by Borodin / ERT
  (Theorem 10 of the notes).
- Consequence at $t = 25$: the subgraph induced by vertices of degree exactly $24$
  is a Gallai tree with $\Delta \le 24$. In particular it cannot contain $K_{25}$
  and has $|E| \le (k - 2 + 2/(k-1)) |B| / 2 = (23 + 1/12)|B|/2$ on its low-degree
  blocks (Lemma 8 of the notes). For $t = 25$ this gives $|E(G[B])| \le
  (23 + 1/12)|B|/2 < 11.55 |B|$.

### 1.6 Stiebitz two-component theorem

**Theorem (Stiebitz 1985).** If $G$ is $k$-critical and $B = B(G)$ its low-degree
set, then $G - B$ has at least $2$ components.

- Proven. Reference: M. Stiebitz, *$K_5$ is the only double-critical 5-chromatic
  graph*, Discrete Math. 64 (1985); also discussed in the lecture notes proof of
  Theorem 20.
- Consequence: the "high" vertex set $H = V(G) - B$ is not connected. This is a
  strong structural restriction that should feed directly into R1b enumeration.

### 1.7 Forbidden subgraphs in the low-degree set

By the Gallai tree theorem combined with $\delta \ge k - 1$:

- No $K_k$ subgraph inside $G[B]$ (every block is $K_r$ for $r \le k - 1$ or an
  odd cycle).
- In particular at $t = 25$: $G[B]$ contains no $K_{25}$ subgraph.
- If $G[B]$ contains a $K_{k-1} = K_{24}$ block, then that block is a leaf in the
  Gallai tree sense, and the cut vertex into the rest has higher degree.

### 1.8 What is *not* forced (frequent confusions)

- $\kappa(G) \ge k - 1$. Not forced (Section 1.3 above; $k$-Ore witnesses).
- $G$ is regular or near-regular. Not forced. Plenty of $k$-critical graphs have
  $\Delta(G) \gg \delta(G)$.
- $G$ contains $K_{k-1}$ as a subgraph. **Open**. There is no theorem forcing
  this at $t = 25$.
- $G$ is vertex-transitive. Wildly not forced; vertex-transitive critical graphs
  are a sparse special family.
- $G$ has girth $\ge 4$. Not forced; $K_{25}$ itself is $25$-critical and has
  girth $3$.
- $G$ contains an $(t - 1)$-immersion of $K_{t}$. This is the Lescure–Meyniel
  conjecture; open. Fox–Pach–Suk's $1.4(k-1)$ unconditional bound is the only
  partial result.
- $G$ has no $K_t$-minor. This would be a *Hadwiger counterexample*; for $t = 25$
  Hadwiger is wide open, so the question is undetermined.

---

## 2. R1b candidate restrictions

I list five candidate restrictions for the $25$-critical, $48$-vertex search.
For each I record (a) definition, (b) coverage in the full residual MCE space,
(c) implied search-space size, (d) the theorem one would obtain on closing it.

### 2.1 $K_{24}$-containing $25$-critical graphs on $48$ vertices

(a) **Definition.** $G$ is $25$-critical, $|V| = 48$, $\delta \ge 24$, and $G$
contains a $K_{24}$ subgraph.

(b) **Coverage.** Unknown. There is no theorem saying every $25$-critical $48$-
vertex graph contains $K_{24}$. The Hadwiger contrapositive (under conditional
Hadwiger) gives $K_{25}$-minor (weaker — minor, not subgraph) and is in any
case conditional. So this restriction is **proper**; its share of the residual
space cannot be quantified without additional structural input.

(c) **Search-space size.** Fix a $K_{24}$ on vertices $\{1, \dots, 24\}$. The
remaining $24$ vertices each have $\ge 24$ neighbours; at least $24$ of those
must lie in the fixed $K_{24}$ (else $\delta$ drops). With careful canonical-form
SAT encoding and breaking the symmetry of the $K_{24}$, the encoding has
$\binom{24}{r}$-style bipartite-extension choices on the $24 \times 24$ bipartite
"outside" graph. Concretely: each outside vertex's neighbourhood in $K_{24}$ is
a subset of size $\ge $ some value, and the outside-outside subgraph must satisfy
$\delta_{\rm outside} \ge $ (24 - inside-degree). This is *much* smaller than the
full $48$-vertex search but not yet trivial; rough estimate is $\sim 2^{500}$
variables before symmetry breaking, which SAT can in principle handle if the
$25$-criticality propagation is good.

(d) **Theorem on closure.** "Every $25$-critical graph on $48$ vertices that
contains a $K_{24}$ subgraph satisfies $\operatorname{cr}(G) \ge \operatorname{cr}(K_{25})$."
This is a partial-Albertson theorem; publishable, but does not close Albertson
for $t = 25$.

### 2.2 $k$-Ore $25$-critical graphs on $48$ vertices

(a) **Definition.** $G$ is in the closure of $\{K_{25}\}$ under DHGO-composition,
with $|V(G)| = 48$. By Kostochka–Yancey Theorem 17, equivalently $G$ is
$25$-extremal, i.e. attains $|E(G)| = F(48, 25) = 587$.

(b) **Coverage.** Proper subset, **but with a hard structural lemma the
coverage may be characterised**: $25$-Ore graphs on $48$ vertices arise from
$O(K_{25}, K_{25})$-style operations. The DHGO composition adds $k - 1 = 24$
vertices per step, so from $K_{25}$ we reach $|V| \in \{25, 48, 71, \dots\}$.
The "$48$" case is exactly **one DHGO composition** of two copies of $K_{25}$.
So $25$-Ore graphs on exactly $48$ vertices form a *finite, structurally
explicit* family — count is the number of ways to choose a split vertex in
$K_{25}$ and an edge in $K_{25}$ up to automorphism, which is a single
isomorphism class up to relabelling.

(c) **Search-space size.** Essentially $O(1)$ — there is a single $25$-Ore graph
on $48$ vertices up to isomorphism. The crossing number can be computed by ILP.

(d) **Theorem on closure.** "The unique $25$-Ore graph on $48$ vertices
satisfies $\operatorname{cr}(G) \ge \operatorname{cr}(K_{25})$." This rules out
the *Ore* corner of the residual space. Combined with: "an MCE on $48$ vertices
that is not $25$-Ore has $|E| \ge 588$" (Kostochka–Yancey Theorem 17), this is
actual content. **This is the most concrete short-term R1b deliverable I see.**

### 2.3 $25$-critical graphs with bounded list-chromatic gap

(a) **Definition.** $G$ is $25$-critical on $48$ vertices with $\chi_\ell(G) - \chi(G) \le c$
for fixed small $c$ (e.g. $c = 0$, "$25$-list-critical"; or $c = 1$).

(b) **Coverage.** Likely large fraction. List-chromatic number is at least the
chromatic number, and the gap is bounded for many natural critical families
(e.g. Gallai trees have $\chi_\ell = \chi$). The exact fraction is unknown;
**this is the kind of restriction that needs a structural lemma to be
quantified**.

(c) **Search-space size.** Restricting to list-critical does not reduce the
search drastically, but it does *enable a different encoding*: list-critical
graphs have additional structural constraints (Theorem 10 of Kostochka's notes),
which feed SAT propagation.

(d) **Theorem on closure.** "Every $25$-list-critical graph on $48$ vertices
satisfies $\operatorname{cr}(G) \ge \operatorname{cr}(K_{25})$." This is a
**list-Albertson** statement and is publishable; combined with the analogous
result for non-list-critical $25$-critical graphs it would close $t = 25$.

### 2.4 $25$-critical graphs with a Gallai-tree low-degree set of bounded
diameter

(a) **Definition.** $G$ is $25$-critical on $48$ vertices and the Gallai tree
$G[B]$ on the low-degree vertices has bounded diameter (e.g. $\le 5$).

(b) **Coverage.** Unknown. The Gallai tree can in principle be anything; "small
diameter" is a genuine restriction.

(c) **Search-space size.** Bounded-diameter Gallai trees on a set of
$\le 24$ vertices (the maximum $|B|$ when most vertices have degree $24$) form
a finite, enumerable family. By Stiebitz, $G - B$ has $\ge 2$ components, so the
$H = V - B$ side splits structurally. Combined with the $K_{24}$-extension
encoding of 2.1, the search becomes a SAT instance of size $\sim 2^{200}$ —
borderline tractable.

(d) **Theorem on closure.** "$25$-critical $48$-vertex graphs whose low-degree
Gallai tree has diameter $\le 5$ satisfy Albertson." Genuine partial result.

### 2.5 $25$-critical graphs with $|B(G)| \ge 24$ (almost-regular low-degree)

(a) **Definition.** $G$ is $25$-critical on $48$ vertices and at least half its
vertices have degree exactly $24$, i.e. $|B(G)| \ge 24$.

(b) **Coverage.** Large. By Kostochka–Yancey, the edge surplus at $(25, 48)$
above the trivial $|E| \ge 576$ is only $\ge 11$, so on average at most $\sim 22$
"high" vertices contribute that surplus — most vertices are at degree exactly
$24$ in the extremal regime. So $|B(G)| \ge 24$ is **plausibly close to
$100\%$ coverage** for MCE candidates, but I cannot prove this without an
average-edge-density argument.

(c) **Search-space size.** $|B| \ge 24$ Gallai trees on $48$ vertices with
$\Delta \le 24$ are still a large family, but the Stiebitz two-component theorem
forces $G - B$ to split, and each half has $\le 12$ vertices. So the high-degree
"side" decomposes into $\le 12$-vertex pieces, which is very small.

(d) **Theorem on closure.** "$25$-critical $48$-vertex graphs with $\ge 24$
low-degree vertices satisfy Albertson." Genuine partial result; combined with
the "few low-degree vertices" complementary case (which is forced into
$|E| \ge $ much more, by Kostochka–Yancey), this would close $(25, 48)$.

### 2.6 Restrictions to *reject*

- "**WLOG vertex-transitive.**" Reject. Vertex-transitive critical graphs are
  a measure-zero special family; restricting to them trivialises the conjecture
  without WLOG.
- "**WLOG $\delta(G) = \Delta(G) = t - 1$** (i.e. regular)." Reject. Critical
  graphs are not in general regular; $k$-Ore graphs have degree variation.
- "**WLOG contains $K_t$ as a subgraph.**" Trivially reject: if $G$ contains
  $K_t$, then $\operatorname{cr}(G) \ge \operatorname{cr}(K_t)$ by the
  subgraph monotonicity of crossing number, and Albertson is immediate. So this
  is the *trivial* case, not a "WLOG".
- "**WLOG $\kappa(G) \ge t - 1$.**" Reject — see Section 1.3. Plan v3 already
  removed this.

---

## 3. R3.6 — Fractional / list / DP / online Albertson extensions

### 3.1 The variants

Let $\chi^*(G)$ stand for a chromatic-number variant. The corresponding
Albertson variant reads:
$$\chi^*(G) \ge t \;\Longrightarrow\; \operatorname{cr}(G) \ge \operatorname{cr}(K_t).$$

Variants:

1. **Fractional Albertson.** $\chi^* = \chi_f$, the fractional chromatic number.
2. **List Albertson.** $\chi^* = \chi_\ell$, the list chromatic number.
3. **DP-Albertson.** $\chi^* = \chi_{\rm DP}$, the DP-chromatic / correspondence
   chromatic number (Dvořák–Postle).
4. **Online (paintability) Albertson.** $\chi^* = \chi_{\rm OL}$, the online
   list chromatic number / paint number (Schauz; Zhu).
5. **Hall / $\chi_d$ ("diff-chromatic") Albertson.** Less standard.

For *every* graph $G$ the hierarchy is:
$$\chi_f(G) \le \chi(G) \le \chi_\ell(G) \le \chi_{\rm OL}(G) \le \chi_{\rm DP}(G) \le \Delta(G) + 1.$$

So a hypothesis "$\chi^*(G) \ge t$" with $\chi^*$ further to the *right* is a
*weaker* hypothesis on $G$ (it covers more graphs), and an Albertson statement
under that hypothesis is correspondingly *stronger* — proving it implies
Albertson for all weaker chromatic variants.

### 3.2 Comparison to Albertson

- **Fractional Albertson is strictly weaker than Albertson.** A graph with
  $\chi_f \ge t$ has $\chi \ge \lceil t \rceil \ge t$ (if $t$ integer), so
  $\{G : \chi_f \ge t\} \subseteq \{G : \chi \ge t\}$. Albertson on the latter
  set implies Albertson on the former. So a *proof* of fractional Albertson
  would be a partial Albertson result (only for graphs that already have
  $\chi_f \ge t$), **not** intermediate progress towards Albertson.
  Actually, wait — let me redo this carefully.
  $\chi_f \le \chi$, so $\chi_f \ge t$ is a *stronger* hypothesis on $G$
  (fewer graphs satisfy it). Therefore:
  - Fractional Albertson is implied by Albertson (it's about a smaller graph
    class), hence **strictly weaker as a theorem** — proving it is
    *intermediate*, not stronger.
- **List Albertson is strictly stronger than Albertson.** $\chi_\ell \ge t$ is a
  weaker condition than $\chi \ge t$ (more graphs satisfy it), so List
  Albertson covers more cases. **Proving list Albertson implies Albertson.**
- **DP-Albertson is strictly stronger than List Albertson** (and hence than
  Albertson). Same reasoning.
- **Online Albertson** sits between list and DP-chromatic; strictly stronger
  than list Albertson.

The picture:
```
fractional Albertson  <  Albertson  <  list Albertson  <  online Albertson  <  DP-Albertson
       (weaker)                                       (stronger)
```
(Where "$<$" means "is implied by".)

### 3.3 What is known

To my knowledge as of mid-2026:

- **Fractional Albertson.** No published result. **Open.** Should be the
  easiest variant — fractional chromatic number behaves better under tensor
  products and limits, and Lovász-style bounds can be brought to bear.
- **List Albertson.** Unpublished as far as I know; this is the most natural
  strengthening. **Open.** Note that Kostochka–Yancey-type edge bounds extend
  to *list-critical* graphs (Remark 1 in Kostochka's notes, eq. (15)), so the
  full ACF / Barát–Tóth / Ackerman / Cranston chain *should* go through with
  list-chromatic number replacing chromatic number, modulo bookkeeping. This
  is a publishable target.
- **DP-Albertson.** Open and likely the hardest. Bernshteyn–Kostochka have
  studied DP-chromatic analogues of Hadwiger; the corresponding Albertson
  question is plausibly attackable by their methods but I have not seen it
  written.
- **Online Albertson.** Open. Probably implied by DP-Albertson; doing it
  independently is not the most efficient use of effort.
- **Schaefer's variants** (rectilinear $\overline{\operatorname{cr}}$, pair,
  odd, $k$-planar): these change the *crossing-number* side, not the chromatic
  side. Independent research direction; not what the question asks.

### 3.4 Warm-up recommendation

**List Albertson** is the best warm-up.

Reasons:

1. **Edge-count infrastructure already exists** for list-critical graphs.
   Krivelevich, Kostochka–Stiebitz, and Kostochka–Yancey all have list-critical
   analogues (Remark 1 of the lecture notes; Postle's PhD thesis and follow-ups).
2. The Gallai-tree theorem extends to list-critical graphs (Borodin / ERT,
   Theorem 10 of the lecture notes).
3. The Crossing Lemma is *not* aware of list-vs-ordinary chromatic number,
   so the ACF / Bungener–Kaufmann pipeline carries over verbatim — what changes
   is the criticality hypothesis, not the analytic input.
4. **Direct value to R1b.** A proof of list Albertson at $t = 25, 26$ on a
   sub-family would let R1b restrict the candidate space without losing
   coverage — every $25$-critical graph is $25$-list-critical for the trivial
   list assignment, but the converse fails, so closing list Albertson on a
   sub-family is *more* than closing Albertson on that sub-family.
5. **Concrete first target.** "Verify list Albertson for $t \le 18$ by adapting
   Ackerman's $1/29$-Crossing-Lemma argument." If this works it pushes the list
   threshold to match the ordinary one.

DP-Albertson is the right *follow-up*, but list Albertson is the cleanest
warm-up.

### 3.5 Independent angle: $\chi_f$ for the residual triples

A small Role 2 calculation worth doing: for each candidate counterexample
generated by R1c, compute $\chi_f(G)$ and see whether $\chi_f(G) \ge 25$ already.
If a candidate has $\chi_f(G) < 25$ but $\chi(G) = 25$, it is a particularly
interesting "fractional Albertson gap" example — a place where the fractional
relaxation fails to certify chromatic-number $25$. Such graphs are exactly the
ones the literature has the *least* control over and would be the natural
candidate counterexamples to *both* Albertson and a hypothetical fractional
Albertson.

---

## 4. Sanity-check log against plan v3

I scanned plan v3 for every concrete structural claim about critical graphs.

### 4.1 Edge-connectivity attribution — incorrect

**Lines 272–273, 821, 874:** "moreover it is $(t-1)$-edge-connected by the
sharpened criticality results of Kostochka–Stiebitz."

**Correction:** $(k-1)$-edge-connectivity of $k$-critical graphs is **Dirac's
theorem** (1953), proved by Kopon's short colour-permutation argument. This is
Lemma 1 of Kostochka's lecture notes, where the attribution is unambiguously
to Dirac. Kostochka–Stiebitz contributed *sparseness* refinements (eq. (19) of
the notes; the inequality $|E(G)| \ge \tfrac{k-1}{2}n + \tfrac{k-3}{k^2 + 6k - 11 - 6/(k-2)} n$)
and the Stiebitz two-component theorem (after deleting $B(G)$), but **not**
edge-connectivity. Same error at line 119–120 of the revision history
("attributed minimum-degree result to Dirac (1952) with sharpening by
Kostochka–Stiebitz") — the sharpening is to *edge density*, not to
*edge-connectivity*.

This is a real mathematical error; please fix in v4.

### 4.2 Edge-count bound — uses only the trivial Dirac bound

**Line 276–277:** "Edge count. $|E(G)| \ge \tfrac{t-1}{2}|V(G)|$ (a direct
consequence of $\delta \ge t-1$)."

**Correction (not an error, but an omission):** the strongest available edge
bound is **Kostochka–Yancey 2014** (arXiv:1209.1050):
$|E(G)| \ge \lceil ((k+1)(k-2)n - k(k-3))/(2(k-1)) \rceil$. At $(25, 48)$ this
is $587$ vs. the trivial $576$. The Kostochka–Yancey bound is what should
feed into the R1b SAT encodings and into the R2 Crossing-Lemma calculation.
The trivial Dirac bound discards real structural content.

### 4.3 Vertex-connectivity — correctly stated in v3

✓ Lines 274–276: "Vertex connectivity of $t$-critical graphs is **not** in
general forced to $t - 1$ — critical graphs can have small vertex cuts." This
is the v2 correction and it is now right. Witness: $k$-Ore graphs have
$\kappa = 2$ (Theorem 17 of the Kostochka notes).

### 4.4 $\chi(K(n, k))$ — Lovász formula correctly stated

✓ Lines 583–588: "$\chi(K(n, k)) = n - 2k + 2$... the correct chromatic-$t$
Kneser family is $K(2k + t - 2,\, k)$." This is the correct Lovász formula.

### 4.5 Schrijver subgraphs — correctly stated

✓ Lines 588–589: "Schrijver subgraphs $SG(n, k)$ inherit the same chromatic
number while being vertex-critical." This is Schrijver's 1978 theorem.

### 4.6 Mycielski graph claim — correctly hedged in v3 as conjecture

✓ Lines 670–675 and 760–769: framed as a *prediction to test*, not an asymptotic
fact. v3 fixed the v2 over-claim.

### 4.7 Hadwiger / $K_{t-1}$-minor-free correctly flagged as conditional

✓ Lines 532–541: now explicitly conditional on Hadwiger and notes that
Hadwiger is open for $t \ge 7$. Good.

### 4.8 Cranston Theorem 2 residual triples — correctly stated

✓ Lines 331–334 and 425–432: $(25, 48), (26, 50), (26, 51)$. Matches the
Cranston paper.

### 4.9 Fox–Pach–Suk thresholds — both forms correctly cited

✓ Lines 297–308: both the arXiv form $n < 1.4k - 0.6$ and the SoCG form
$\le 1.4(k-1)$ are given. The two-form ambiguity is acknowledged.

### 4.10 R1b candidates — incomplete but not wrong

Lines 450–465: the four candidate restrictions listed are fine as written. They
do not include the $k$-Ore restriction (Section 2.2 above) or the bounded-
$|B(G)|$ restriction (Section 2.5), both of which I believe are more concrete
than what is currently in R1b. Suggested for v4: add these.

### 4.11 Gallai-tree structure missing

Plan v3 does not mention the Gallai-tree theorem (Section 1.5 above) or the
Stiebitz two-component theorem (Section 1.6). Both are central to R1b
SAT/CEGAR encodings; without them the search has missed structural
constraints worth $\sim 2^{|B|}$ pruning power.

### 4.12 Kostochka–Yancey not cited anywhere

Search of plan v3 returns 0 hits for "Kostochka–Yancey". This is a serious
omission: their theorem is the tight edge bound, and their characterisation of
extremal $k$-critical graphs (Theorem 17, $k$-Ore graphs) is the single most
useful structural handle on the residual MCE candidates.

### Summary

- 2 mathematical errors (4.1, attribution; 4.2 ought to cite stronger bound).
- 3 substantive omissions (4.11, 4.12, and Kostochka–Yancey not in references).
- The v2-corrected claims (vertex-connectivity, Hadwiger, Kneser, Mycielski)
  are all clean in v3.

---

## 5. Open questions for the rest of the team

### To Role 3 (exact crossing number)

1. **Definition.** Which crossing-number variant are you computing — *planar*
   crossing number, *rectilinear* crossing number, or *pair* crossing number?
   The Albertson conjecture is stated for the planar number; Schaefer notes
   that the pair crossing number can differ at small graphs and is what some
   ILP encodings actually solve. I need a clear answer before I encode candidates.
2. **Scaling.** What is the largest order $n$ at which your ILP / SAT pipeline
   has produced a *certified* exact crossing number, and at what wall-clock
   cost? I am sending you candidates at $n = 48$–$51$ and $|E| \in [580, 700]$;
   I need to know what to budget.
3. **Lower-bound certificates.** Can you give a *certified* lower bound on
   $\operatorname{cr}(K_{25})$ that exceeds the trivial $0.83 \cdot Z(25) \approx
   3615$? If so I will use that as the operational falsification threshold
   $\underline{L}(25)$ in C3. If not, we are stuck using the strong-form
   threshold $Z(25) = 4356$, which only falsifies the strong form.

### To Role 4 (SAT/CEGAR)

1. **Critical-graph encoding.** Does your SAT encoding distinguish *vertex-
   deletion critical* ($\chi(G - v) < \chi(G)$ for every $v$) from
   *edge-deletion critical* ($\chi(G - e) < \chi(G)$ for every $e$)? These
   are different and the Kostochka–Yancey theorem is for the *vertex-deletion*
   version. Please confirm.
2. **Kostochka–Yancey constraint.** Are you encoding the edge bound
   $|E(G)| \ge F(n, k) = 587$ at $(25, 48)$ as a propagator? If not, the
   solver is missing structural pruning.
3. **Gallai-tree propagator.** Same question for the Gallai-tree structure on
   the low-degree set: do you encode "every block of $G[\{v : d(v) = k-1\}]$ is
   either $K_r$ or $C_{2s+1}$"? This is a strong propagator that the literature
   suggests is missed by generic SAT.
4. **Symmetry breaking.** $K_{24}$-subgraph-containing $G$ has a $24!$
   symmetry group on the $K_{24}$. Are you symmetry-breaking? If yes, how?

### To Role 5 (enumeration)

1. **Generator definition.** Are you using `nauty geng` with criticality as a
   post-filter, or are you generating $k$-critical graphs natively (e.g. via
   DHGO compositions starting from $K_k$)? The DHGO route produces only the
   $k$-Ore graphs, which are a measure-zero subset of $k$-critical graphs but
   are exactly the *extremal* family.
2. **$k$-Ore enumeration.** Can you produce the (essentially unique up to
   automorphism) $25$-Ore graph on $48$ vertices? It is one DHGO composition of
   $K_{25}$ with $K_{25}$. If you produce it, I will hand-verify its crossing
   number bound.
3. **Scope.** Are you targeting *vertex-critical* or *list-critical* graphs?
   If list-critical, you cover more cases per generation step.

### To Role 9 (SDP)

1. **Finite extraction.** Can the flag-algebra SDP used by Balogh–Lidický–
   Salazar be re-run for $t = 25$ specifically to produce a *finite, certified*
   lower bound on $\operatorname{cr}(K_{25})$? The published asymptotic
   constant $0.98559895$ is not by itself a finite certificate; an explicit
   finite SDP run for $n = 25$ would close the gap between Plan v3's
   strong-form threshold $Z(25)$ and the actual Albertson threshold.
2. **Numerical precision.** What is the *certified* numerical precision of your
   SDP outputs? Albertson at $t = 25, n = 48$ depends on a sub-1\% gap; if your
   SDP returns $\operatorname{cr}(K_{25}) \ge 4290$ (i.e. $0.985 \cdot Z(25)$
   reproduced rigorously at $t = 25$) the gap to $Z(25) = 4356$ is $66$
   crossings.
3. **Critical-graph SDP?** Has anyone formulated an SDP relaxation directly
   for the question "does there exist a $25$-critical graph $G$ on $48$
   vertices with $\operatorname{cr}(G) < L$?" — i.e., not for $K_{25}$ itself
   but for the residual MCE? If not, this is an independent SDP target worth
   formulating.

### Cross-role

- Define a single shared notion of "$t$-critical" and stick with it. I propose
  **vertex-deletion critical** as default (the classical Dirac / Gallai /
  Kostochka–Yancey notion). Edge-deletion critical is a different object.
- The Kostochka–Yancey bound and the $k$-Ore characterisation should be
  baked into every encoding (SAT, enumeration, SDP).

---

## 6. First 30-day deliverables (Role 2)

Five items, each scoped to $\le 6$ person-days.

### D1 (3 days). Kostochka–Yancey constraint propagator for R1b/R1a.

Write a short formal note: encode the Kostochka–Yancey edge bound
$|E(G)| \ge F(n, k)$ and the Gallai-tree theorem (Theorem 5 of Kostochka's
notes) as CNF propagators suitable for Role 4's SAT encoder. Deliverable:
text file with the CNF clauses, complexity analysis, and a small unit test
on $n = 10, k = 4$ where the propagator should immediately give
$|E| \ge \lceil (5 \cdot 2 \cdot 10 - 4)/6 \rceil = 16$.

### D2 (4 days). $25$-Ore graph on 48 vertices — closing the Ore corner.

Construct explicitly the (essentially unique) $25$-Ore graph $G_{\rm Ore}$ on
$48$ vertices as $O(K_{25}, K_{25})$. Compute $\overline{\operatorname{cr}}(G_{\rm Ore})$
via OGDF planarisation and submit to Role 3 for exact lower-bound certification.
Deliverable: graph file (graph6 or DIMACS), heuristic upper bound, and a
Role 3 query. Expected outcome: $\operatorname{cr}(G_{\rm Ore}) \ge
\operatorname{cr}(K_{25})$ since $G_{\rm Ore}$ "contains" two $K_{24}$s in
DHGO position, but this needs verification — *if* it fails, that is the
candidate counterexample everyone is looking for, on a silver platter.

### D3 (5 days). Sanity-check log handed to the team.

Polished version of Section 4 above as a stand-alone document, to be circulated
to Roles 1, 3, 4, 5, 9 before they bake errors into their code. Deliverable:
PDF / Markdown with each numbered claim and its status.

### D4 (5 days). List-Albertson literature scan and first lemma.

Produce a *signed* literature scan of fractional / list / DP Albertson —
which has been published, by whom, where it stops. Deliverable: bibliography
plus a *first-attempt* lemma transcribing the ACF $|V| \le 4t$ argument from
ordinary critical to list-critical (using Krivelevich's list-edge bound
eq. (15) of the lecture notes). If the argument goes through verbatim, we have
*list-ACF* for free, which is publishable on its own.

### D5 (6 days). Empirical Kostochka–Yancey tightness at the residual triples.

Implement a small SageMath script that for each $(t, n) \in \{(25, 48), (26, 50),
(26, 51)\}$ generates *random* $t$-critical graphs (by DHGO composition from
$K_t$ followed by random edge-additions) and measures
- $|E(G)|$ relative to $F(n, k)$;
- $|B(G)|$ relative to $n$;
- the number of components of $G - B(G)$;
- whether $G$ contains $K_{t-1}$ as a subgraph.
Deliverable: a table summarising 100+ generated examples per triple. This
calibrates the R1b coverage claims of Section 2 against real data.

---

## Appendix A — Quick reference of cited theorems

| # | Theorem | Source | Status | What it says |
|---|---|---|---|---|
| A1 | Dirac (1952) | J. London Math. Soc. 27, 85 | proven | $\delta(G) \ge k - 1$ for $k$-critical $G$ |
| A2 | Dirac (1953) edge-conn | Kopon proof in Kostochka notes Lemma 1 | proven | $G$ $k$-critical $\Rightarrow$ $\lambda(G) \ge k - 1$ |
| A3 | Dirac (1957) edges | Kostochka notes Theorem 3 | proven | $2|E| \ge (k-1)n + (k-3)$ for $k$-critical $G \ne K_k$ |
| A4 | Gallai (1963) | Kostochka notes Theorem 5 | proven | $G[B(G)]$ is a Gallai tree |
| A5 | Gallai (1963) edges | Kostochka notes Theorem 7 | proven | $|E| \ge \tfrac{k-1}{2}n + \tfrac{k-3}{2(k^2-3)}n$ |
| A6 | Stiebitz (1985) | Kostochka notes (proof of Thm 20) | proven | $G - B(G)$ has $\ge 2$ components |
| A7 | Krivelevich (1997/98) | Kostochka notes eq. (18) | proven | tighter $|E|$ bound, see Section 1.4 |
| A8 | Kostochka–Stiebitz (1999/2003) | Kostochka notes eq. (19) | proven | even tighter $|E|$ bound for $k \ge 6$ |
| A9 | Kostochka–Yancey (2014) | arXiv:1209.1050 | proven | $|E| \ge \lceil \tfrac{(k+1)(k-2)n - k(k-3)}{2(k-1)} \rceil$ |
| A10 | Kostochka–Yancey (2014) extremal | Kostochka notes Theorem 17 | proven | equality iff $G$ is $k$-Ore; $k$-Ore have $\kappa = 2$ |
| A11 | Lovász (1978) | Combinatorica | proven | $\chi(K(n, k)) = n - 2k + 2$ |
| A12 | Schrijver (1978) | Niew Archief Wisk. | proven | $SG(n, k)$ is $\chi$-critical with $\chi = n - 2k + 2$ |
| A13 | Hadwiger | open | open for $k \ge 7$ | $\chi \ge k \Rightarrow $ $K_k$-minor |
| A14 | Lescure–Meyniel (1989) | open | open in general | $\chi \ge k \Rightarrow$ $K_k$ weak immersion |
| A15 | Fox–Pach–Suk (2025) | arXiv:2510.05893 | proven | partial Lescure–Meyniel at $|V| < 1.4k - 0.6$ |
| A16 | Albertson–Cranston–Fox (2009) | arXiv:1006.3783 | proven | MCE has $|V| \le 4t$; Albertson for $t \le 12$ |
| A17 | Barát–Tóth (2009) | arXiv:0909.0413 | proven | Albertson for $t \le 16$; MCE $|V| \le 3.57t$ |
| A18 | Ackerman (2019) | arXiv:1509.01932 | proven | Albertson for $t \le 18$; MCE $|V| \le 3.03t$ |
| A19 | Cranston (2025) | arXiv:2512.08020 | proven | Albertson for $t \le 24$; residual triples |
| A20 | Bungener–Kaufmann (2024) | arXiv:2409.01733 | proven | Crossing Lemma constant $1/27.48$ for $|E| \ge 6.95|V|$ |

---

*End of memo.*
