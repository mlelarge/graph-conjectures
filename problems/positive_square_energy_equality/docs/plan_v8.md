# Plan: prove (a tractable slice of) Conjecture 9.2 of Akbari–Kumar–Mohar–Pragada–Zhang

Source: arXiv:2506.07264, *Refinement of a conjecture on positive square energy of graphs*, June 2025.

**Revision history.**

- **v8** (this version): incorporates Phase 4 progress on (L'). Records the
  closed-form proof of (L') for **books $B_k$** and the closed-form Szegő
  asymptotic for **2-paths $L_n$** as proved subfamily theorems, plus the
  BT$(k,2)$ bad-ear asymptotic that quantifies how the universal lemma fails.
  Promotes the trace-identity observation from finite-$n$ to the Szegő limit
  (reviewer correction: pentadiagonal symmetric Toeplitz with exactly $4$
  unit Fourier coefficients gives $\frac{1}{\pi}\int_0^\pi f^2 = 4$ exactly,
  no boundary anomaly). Replaces the previous selector conjecture (O2) by
  the cleaner **max-degsum selector**: the simplicial ear maximizing
  $\deg_{G-v}(a)+\deg_{G-v}(b)$ has $\min(\delta^+,\delta^-) \ge 17/16$,
  verified on all 725 enumerated 2-trees with $n\le 10$ and on
  $\mathrm{BT}(50,2)$, $\mathrm{BT}(100,2)$. Identifies two remaining open
  problems: finite-$n$ rigorous proof for 2-paths (the Widom-type secular
  bound is not sharp at $n=6$ where $\delta^- = 1.319$), and a proof of the
  max-degsum selector for general 2-trees — the **new headline target**.
- **v7**: incorporated the Phase 3 falsification of the universal
  2-tree ear lemma. The plan now records the trace identity
  $\delta^+(v)+\delta^-(v)=4$, the structured $\mathrm{BT}(k,2)$ and random
  counterexamples to "every ear works", and replaces the target by the existential
  ear-selection lemma (L'): at each 2-tree step, find **some** simplicial degree-2 ear
  with both gains at least $17/16$. Regression fixtures for the false universal lemma
  now live under `tests/fixtures/`.
- **v6**: incorporated the mathematician pass: make **2-trees** the first
  serious target, formulate the needed simplicial-ear deletion lemma, and add a dedicated
  computational/proof subtask. This is explicitly a new local spectral lemma, not an
  application of the induced-$P_3$ removal lemma, since a 2-tree ear lies in a triangle.
- **v5**: applied the reviewer pass on v4 — domination number $\le 2$
  is explicitly **connected** and only cited for the $s^+$ side; $P_3$-removal is
  explicitly sign-specific; Conjecture 9.1 is described as adjacent evidence rather
  than the precise equality bottleneck; computational subtasks now specify the
  optimization objective; near-extremal tests exclude allowed tree/$K_n$ endpoints;
  the claw-free caveat is rephrased; and the slack warning no longer demands an
  absolute constant gap.
- **v4**: applied the review of v3 — domination number $\le 2$ is only
  a cited $s^+$ result in the source paper, not a full two-sided EFGW result; removed
  the global ranking of 9.2(i) vs. 9.2(ii); refined the $s^+$ residue condition to depend
  on clique-size distribution, not only $\ell$; clarified that computational
  $P_3$-removal must optimize over existential choices; added the trivial $K_1$ endpoint.
- **v3**: applied the six remaining factual / logical corrections raised in
  [`review.md`](review.md) against v2 — EFGW is for connected graphs (not "no isolated
  vertex"; counterexample $2K_3$); 9.2(i) does not literally imply EFGW for unicyclic
  graphs but its natural proof strategies meet the same obstruction; the clique-residue
  energy is $\sum(n_j-1)$ for $s^-$ but $\sum(n_j-1)^2$ for $s^+$; $\ell < k/16+1$ is
  *sufficient* for the crude telescoping bound, not necessary for the theorem; Lemma 3.1
  has no support restriction; trees and $K_n$ are both equality families for $s^-=n-1$;
  per-class skepticism added; "publishable note" downgraded to "clean internal note".
- **v2**: rewritten after the review of v1. Removed the false claim that connectivity
  propagates through $P_3$-removal (the $17/16$-slack lemma actively selects cut vertices,
  as the $P_3$ example shows), removed the spurious "dualize Lemma 2.4 via $-A$" step,
  removed "all planar" from the EFGW-known classes, downgraded the headline route to
  speculative.
- **v1**: original draft.

## The conjecture (verbatim, Section 9 of the source paper)

Let $G$ be a **connected** graph of order $n$.
- **(i)** $s^+(G) = n - 1$ iff $G$ is a tree.
- **(ii)** $s^-(G) = n - 1$ iff $G$ is a tree or a complete graph $K_n$.

Notation: $\lambda_1 \ge \cdots \ge \lambda_n$ are the adjacency eigenvalues of $G$;
$s^+(G) := \sum_{\lambda_i > 0} \lambda_i^2$, $s^-(G) := \sum_{\lambda_i < 0} \lambda_i^2$;
$\mathrm{tr}(A^2) = 2m = s^+ + s^-$.

## Why this conjecture, and the honest tractability verdict

This problem sits at rank 684 of `ARXIV_OPEN_DIFFICULTY_RANKING.md` (score 1.50, tier 1).
After reading the source paper and absorbing the review, the **honest tractability verdict
is 2/10 for the full conjecture**, and **the previously-headlined Variant 3 route is
speculative, not 4–8 weeks of bookkeeping**. Reasons:

- 9.2(i) does not literally imply EFGW for unicyclic graphs (9.2(i) only forbids
  *equality* $s^+ = n - 1$ for non-trees, not the strict inequality $s^+ < n - 1$).
  But every natural proof strategy for 9.2(i) — lower-bound arguments via $P_3$-removal
  or interlacing — meets the same unicyclic obstruction as the EFGW programme, because
  proving strictness requires controlling sparse non-bipartite unicyclic graphs. The
  source paper's own Conjecture 9.1 is adjacent evidence for this obstruction: it
  predicts the side of \(n\) on which odd unicyclic graphs lie by cycle length mod \(4\),
  but it is not itself the equality-case statement \(s^+=n-1\).
- The two halves have different hard obstructions rather than a clean global difficulty
  ordering: $s^+$ has the sparse unicyclic obstruction, while $s^-$ has the second
  extremal family $K_n$ and near-complete traps.
- The $P_3$-removal lemma with slack $17/16$ is the strongest tool in the source paper,
  but its slack does **not** suffice to close the equality case via residue analysis
  without an extra structural hypothesis — see "The central obstruction" below.
- The source paper gets non-trivial cases (Thm 8.1) by imposing $\alpha(G)\omega(G) \le n/17$
  rather than by controlling connectivity. That is the actual lever; v1 misidentified it.

## Background and easy direction

- **EFGW (2016, arXiv:1409.2079):** for every **connected** graph $G$ of order $n$,
  $\min\{s^+(G), s^-(G)\} \ge n - 1$. The connectedness hypothesis is essential —
  $2K_3$ has $n = 6$ and $s^-(2K_3) = 4 < 5 = n - 1$, so "no isolated vertex" is not
  enough (v2 misstated this). Open in general; theorem for trees, regular graphs,
  bipartite graphs, and a number of structured classes. The source paper proves the
  **$s^+$ side** for **connected** graphs of domination number $\le 2$ (Thm 7.1 of
  arXiv:2506.07264); do not cite it as a full two-sided EFGW theorem without an
  additional $s^-$ reference.
  EFGW is **not** unconditionally known for all planar graphs (sparse planar cases such
  as unicyclic planar graphs are exactly the EFGW bottleneck).
- **Bipartite spectrum is symmetric about $0$**, so for bipartite $G$: $s^+ = s^- = m$.
- **Forward implications (easy):**
  - Tree $T$: $s^+ = s^- = m = n - 1$. $\checkmark$
  - $K_n$: spectrum $\{n-1,\, -1^{(n-1)}\}$, so $s^-(K_n) = n - 1$. $\checkmark$

## The central obstruction

The $P_3$-removal lemma (Lemma 2.4 of arXiv:2506.07264) says: if $G$ has an induced $P_3$,
there is a vertex $u$ such that
$$s^\pm(G) \ge s^\pm(G - u) + \tfrac{17}{16}.$$
The lemma's $s^+$ and $s^-$ versions are both stated in the source paper, so **no
dualization is needed**. However, the choice of vertex is **sign-specific**: the lemma
does not assert that the same vertex works for both $s^+$ and $s^-$. Any proof must fix
one sign, then iterate certified deletions for that sign until no induced $P_3$ remains.
The residue is a **disjoint union of cliques** $K_{n_1} \sqcup \cdots \sqcup K_{n_\ell}$;
the values of $k, \ell$ and the clique-size vector may depend on the sign and on the
chosen valid deletion sequence.

**The fatal observation.** The $17/16$ gain does **not** preserve connectivity.
Concrete witness: $G = P_3$ has $s^+(P_3) = s^-(P_3) = 2$; deleting either endpoint gives
$K_2$ with $s^\pm = 1$, a gain of only $1 < 17/16$. The only $u$ that achieves the
$17/16$ gain is the **middle vertex**, whose removal leaves two isolated vertices —
disconnecting $G$. So even in the smallest connected example, $P_3$-removal selects a
cut vertex.

**Correct residue accounting.** Fix one sign $\sigma \in \{+, -\}$ and one certified
$P_3$-removal sequence for that sign. Let $k$ be the number of removed vertices and
$\ell$ the number of clique components in the residue
$K_{n_1} \sqcup \cdots \sqcup K_{n_\ell}$ ($\sum_j n_j = n - k$). The clique spectra are
$\mathrm{spec}(K_t) = \{t-1, -1^{(t-1)}\}$, giving
$$s^-(K_t) = t - 1, \qquad s^+(K_t) = (t - 1)^2,$$
hence
$$s^-(\text{residue}) = \sum_j (n_j - 1) = n - k - \ell,$$
$$s^+(\text{residue}) = \sum_j (n_j - 1)^2 \;\ge\; \sum_j (n_j - 1) = n - k - \ell,
\quad\text{with equality iff every } n_j \le 2.$$

Telescoping Lemma 2.4 gives the crude lower bound for each sign separately:
$$s^\pm(G) \;\ge\; \tfrac{17}{16} k + (n - k - \ell) \;=\; n + \tfrac{1}{16} k - \ell.$$

To force $s^-(G) > n - 1$ via this crude bound, one needs
$$\ell \;<\; \tfrac{1}{16} k + 1.$$
This is **sufficient** for the crude telescoping argument, **not necessary** for the
theorem. For $s^+$ the exact residue contribution gives
$$s^+(G) \ge \tfrac{17}{16} k + \sum_j (n_j - 1)^2.$$
Equivalently,
$$s^+(G) - (n - 1) \ge \tfrac{k}{16} + 1 + \sum_j \bigl((n_j - 1)^2 - n_j\bigr).$$
So the $s^+$ residue analysis is not controlled by $\ell$ alone: isolated vertices and
$K_2$ components still hurt, while clique components of order at least $3$ help. A
class-specific strict inequality for $s^+$ may follow from a weaker **residue invariant**
than the $s^-$ condition $\ell < k/16 + 1$, but that invariant must include the
clique-size distribution, not just the component count.

The **central missing lemma** is therefore either a class-specific control on $\ell$, a
sharper Lemma 2.4 whose slack scales with $\ell$, or a different local deletion lemma
that bypasses induced-$P_3$ removal entirely. The source paper's Thm 8.1 sidesteps the
$\ell$ problem by assuming $\alpha(G)\omega(G) \le n/17$, exactly the regime where the
slack dominates the component count.

## What the modest deliverables look like

Unchanged from v7. **Corollary A** (9.2(i) for connected claw-free $G$, via Thm 1.1 of
arXiv:2506.07264) and **Corollary B** (9.2(i) for diameter $\le 2$, via Thm 1.2)
remain a clean internal note, not a serious new result. Drafted in
[`corollaries_AB.md`](corollaries_AB.md).

## What a serious result would require, and where to look

The recommendation is to look for a **genuinely new equality argument** in a narrower
class where the residue-component count $\ell$ is controllable. Candidate classes —
**each with the specific reason it might fail**, since these are search directions, not
expected theorems:

- **2-trees / maximal chordal graphs of treewidth 2.** This is the recommended first
  serious target. A 2-tree is obtained from $K_2$ by repeatedly adding a new vertex
  adjacent to both endpoints of an existing edge; equivalently, it is a maximal chordal
  graph of treewidth $2$. It has a perfect elimination ordering by simplicial degree-2
  vertices, and deleting such vertices preserves the class until $K_3$. This suggests a
  route with one clique residue and no $\ell$-explosion. The catch is important: a
  simplicial degree-2 ear lies in a triangle, so deleting it is **not** supplied by the
  induced-$P_3$ removal lemma. One needs a new local spectral ear-deletion lemma.
- **2-connected graphs.** Initial 2-connectivity does **not** prevent later $P_3$-removal
  steps from creating many residue components. The block-cut tree of the *residue* (not
  $G$) is what matters, and Lemma 2.4 says nothing about it.
- **Block graphs** (every biconnected component is a clique). Structural control is
  strong, but $P_3$-removal may repeatedly delete articulation vertices — *exactly the
  bad behavior* (each such deletion bumps $\ell$).
- **Chordal graphs.** A perfect elimination ordering deletes simplicial vertices in a
  natural sequence, but Lemma 2.4 does **not** guarantee the simplicial vertex is the
  one with $17/16$ gain. Compatibility between the elimination order and the spectral
  slack must be proved, not assumed.
- **Cactus graphs / unicyclic subclasses.** Almost-tree structure is attractive, but
  these classes are also closest to the *known bottleneck* (unicyclic with cycle length
  $\equiv 1 \pmod 4$); they are where the obstruction is most likely to bite, not least.
- **Graphs with $\alpha(G)\omega(G)$ moderately large** (the regime opposite to Thm 8.1):
  this is the regime where the obstruction bites; understanding it is essential for any
  proof that hopes to handle the full conjecture.

None of these is a free theorem. The correct posture is: each is a **search direction
where the obstruction *might* break in our favour**, and we should expect most to fail.

### First serious target: 2-trees

Target theorem (unchanged):

> If $G$ is a 2-tree on $n$ vertices, then Conjecture 9.2 holds for $G$: $K_2$ is the
> tree equality case, $K_3$ is the complete-graph equality case for $s^-$, and every
> 2-tree with $n\ge 4$ satisfies $s^+(G)>n-1$ and $s^-(G)>n-1$.

The universal local lemma proposed in v6 — *every* simplicial degree-2 ear $v$ satisfies
$s^\pm(G) \ge s^\pm(G - v) + 17/16$ — is **false**. Counterexamples in two independent
families: the structured $\mathrm{BT}(k, 2)$ tail ear (e.g. $k = 50$ gives
$\delta^- \approx 1.0575$ on $n = 54$ vertices, with limit $\approx 1.034$; the closed
form lives in [`lprime_selector.md`](lprime_selector.md)), and random 2-trees (e.g. a
seed-149 example at $n = 100$ with $\delta^- \approx 1.0610$, recorded as a regression
fixture in `tests/fixtures/two_tree_universal_counterexamples.json`).

The trace identity
$$\delta^+(v)+\delta^-(v)=2\deg_G(v)=4$$
forces $\delta^-(v)$ alone to determine the pair on degree-2 simplicial ears.
The plan therefore targets the existential ear-selection lemma:

> **(L') 2-tree existential ear lemma.** Let $G$ be a 2-tree with $n\ge 4$. Then there
> exists a simplicial degree-2 vertex $v^*$ such that
> $$s^+(G)-s^+(G-v^*)\ge\frac{17}{16}
> \quad\text{and}\quad
> s^-(G)-s^-(G-v^*)\ge\frac{17}{16},$$
> equivalently $\delta^-(v^*)\in[17/16,\,47/16]$.

If (L') holds at each non-base step, iteratively select a good simplicial degree-2 ear
and delete it until $K_3$ remains. With $k = n - 3$,
$$s^-(G) \ge s^-(K_3) + \tfrac{17}{16}(n-3) = n - 1 + \tfrac{n-3}{16} > n - 1,$$
and similarly $s^+(G) \ge s^+(K_3) + \tfrac{17}{16}(n-3) = 4 + \tfrac{17}{16}(n-3) > n - 1$.

A plausible analytical attack is to write $G = H + v$, where $v$ is adjacent exactly to
an edge $ab \in E(H)$, and use the block form
$$A(G) =
\begin{pmatrix}
0 & e_a^T + e_b^T \\
e_a + e_b & A(H)
\end{pmatrix}.$$
The Schur complement
$$\lambda - (e_a + e_b)^T (\lambda I - A(H))^{-1} (e_a + e_b)$$
may be controllable recursively along the clique tree of the 2-tree. The data suggests
that a good selector should prefer ears whose supporting edge $\{a, b\}$ has large
degree sum in $H = G - v$: book-page ears are good for $s^-$, while terminal tail ears
are bad. The candidate rule (formalized as the max-degsum selector below) is
$$\text{choose a simplicial ear maximizing } \deg_H(a) + \deg_H(b).$$
If the full selector lemma is too hard, attack first 2-paths, books, fans, and the
$\mathrm{BT}(k, t)$ family, where the good and bad ears are explicit. Phase 4 (next
section) has carried out exactly that.

### Phase 4 progress (new in v8)

Three proved subfamily results. Full proofs in companion docs.

**Books $B_k$ (proved, [`lprime_books.md`](lprime_books.md)).** For every $k\ge 2$
and every simplicial degree-2 ear $v$ of $B_k$,
$$\delta^-(B_k) \;=\; 2 - \frac{4}{\sqrt{8k+1}+\sqrt{8k-7}}, \qquad
  \delta^+(B_k) \;=\; 2 + \frac{4}{\sqrt{8k+1}+\sqrt{8k-7}}.$$
Both are in $[17/16,47/16]$ for all $k\ge 2$. Minimum is at $k=2$:
$\delta^-(B_2) = (7-\sqrt{17})/2 \approx 1.4385$. As $k\to\infty$,
$\delta^- \uparrow 2$ and $\delta^+ \downarrow 2$. This is **(L') unconditionally
proved on the book family**.

**2-paths $L_n = P_n^2$ (asymptotic theorem proved + finite-$n$ open,
[`lprime_two_paths.md`](lprime_two_paths.md)).**
$L_n$ is pentadiagonal symmetric Toeplitz with symbol
$f(\theta) = 2\cos\theta + 2\cos 2\theta$. The simplicial ears are $v=1$ and $v=n$,
both isomorphic. As $n\to\infty$,
$$\delta^-_\infty(L) \;=\; \frac{32\pi-27\sqrt{3}}{12\pi} \;\approx\; 1.4262, \qquad
  \delta^+_\infty(L) \;=\; \frac{16\pi+27\sqrt{3}}{12\pi} \;\approx\; 2.5738.$$
Both in $[17/16,47/16]$ strictly. **Reviewer correction (incorporated):** the
trace identity $\delta^+ + \delta^- = 4$ holds *in the Szegő limit* as well, not
just at finite $n$, because $f(\theta) = e^{i\theta} + e^{-i\theta} + e^{2i\theta}
+ e^{-2i\theta}$ has exactly $4$ unit Fourier coefficients, so
$\frac{1}{\pi}\int_0^\pi f^2 = \sum |\hat f(k)|^2 = 4$ exactly. No boundary anomaly
for pentadiagonal symmetric Toeplitz. Finite-$n$ numerics in
`data/two_path_ear_gains.json` for $n\le 200$ are all in $[17/16,47/16]$, with the
minimum $\delta^- = 1.319$ attained at $n=6$ approaching the Szegő limit from below.

**BT$(k,2)$ bad ear (asymptotic theorem proved, [`lprime_selector.md`](lprime_selector.md)).**
For the structured family that disproved the universal lemma in v7, the tail ear
satisfies
$$\delta^-_\infty(\mathrm{BT}) \;=\; 4 - \alpha^2 + \beta^2 \;\approx\; 1.0353,$$
where $\alpha$ is the unique real root of $2x^3-7x-3=0$ and $\beta$ is the unique
real root of $2x^3+2x^2-3x-2=0$. This is $<17/16$, so the bad-tail ear is
asymptotically below the (L') threshold by a constant. **This quantifies how much
the universal lemma fails on BT$(k,2)$**: the ear-selection rule has to actively
avoid the tail, by a constant gap, in the limit.

### Refined selector conjecture (replaces v7 O2)

The v7 candidate selector "prefer ears whose supporting edge $\{a,b\}$ has large
degree sum" was too imprecise: at fixed degree-sum threshold the data shows wide
scatter (e.g. $n=10$, degsum-$5$ ears span $\delta^- \in [1.16, 1.53]$). The
refined form supported by the data is:

> **Max-degsum selector.** For every 2-tree $G$ on $n\ge 4$ vertices, the
> simplicial degree-2 ear $v^*$ maximizing $\deg_{G-v^*}(a)+\deg_{G-v^*}(b)$
> (over its two non-$v^*$ neighbours $a,b$) satisfies
> $$\min(\delta^+(v^*), \delta^-(v^*)) \ge 17/16.$$

**Max-degsum selector $\Rightarrow$ (L').** Trivially: the max-degsum ear $v^*$ is the
existence witness in (L'). So a proof of the max-degsum selector for general 2-trees
immediately closes (L'), which in turn closes Conjecture 9.2 for 2-trees via the
telescoping argument above.

Empirical support (recorded in [`lprime_selector.md`](lprime_selector.md) and
`data/two_tree_ear_gains_n*.json`):

- All **725 enumerated 2-trees with $n\le 10$**: min over max-degsum ears
  is $1.2940$ (well above $17/16 = 1.0625$).
- $\mathrm{BT}(50,2)$ and $\mathrm{BT}(100,2)$: the bad-tail ear has constant
  degsum $5$; the book-page ears have linear-in-$k$ degsum $2k+1$. The selector
  correctly avoids the tail and picks a book-page ear, with $\delta^-$ exactly
  as in `lprime_books.md`.

Ties in degsum: not observed to be load-bearing on $n\le 10$; tie-breaking
deferred until a structural attempt produces a specific witness.

This replaces v7's open subtask (O2). The proof of the max-degsum selector for
**general** 2-trees is the new headline target.

### Failure modes for (L')

- The universal lemma is already false; never use an arbitrary simplicial ear.
- The valid ear for $s^+$ and the valid ear for $s^-$ may differ — but on
  degree-2 ears the trace identity ties them together, so a single $\delta^-(v)$
  in $[17/16, 47/16]$ certifies both.
- Highly unbalanced 2-trees may force the selector to avoid long-tail ears.
- The base step $K_3\to K_2$ is genuinely exceptional for $s^-$: the gain is only $1$,
  so the induction must stop at $K_3$.
- (**v8 addition**) The max-degsum selector relies on the *current* graph
  $G$, not the original. Iteration is well-defined because removing a
  simplicial ear keeps the result a 2-tree, but the selector at step $i+1$ runs
  on $G_i := G_{i-1} - v_{i-1}^*$, not on $G$. The empirical evidence covers
  every 2-tree up to $n\le 10$, so this is consistent at small scale; the
  proof obligation for general $n$ is one-step-local plus closure of 2-trees
  under simplicial-ear deletion.

## Revised step-by-step plan

| # | Goal | Technique | Effort | Status |
|---|------|-----------|--------|--------|
| 1 | Easy directions | Bipartite-symmetry for tree; explicit spectrum for $K_n$ | inline | **proved** (§Background) |
| 2 | Corollary A: 9.2(i) for connected claw-free $G$ | Thm 1.1 + paths/cycles split | 1 paragraph | drafted (`corollaries_AB.md`) |
| 3 | Corollary B: 9.2(i) for $\mathrm{diam}(G) \le 2$ | Thm 1.2 + check $K_{1,n-1}, C_5$ | 1 paragraph | drafted (`corollaries_AB.md`) |
| 4 | Write up steps 1–3 as a short note (3–5 pages) | Standard exposition | 1–2 weeks | drafts merged; needs polish |
| 5a | (L') on books $B_k$ for $k\ge 2$ | Closed-form spectrum + telescoping | done | **proved**, `lprime_books.md` |
| 5b | (L') on 2-paths $L_n$ asymptotic | Szegő for pentadiagonal symmetric Toeplitz | done | **proved**, `lprime_two_paths.md` |
| 5c | (L') on 2-paths $L_n$ at finite $n$ | Widom-type secular bound, or alternative | open-ended | open; obstacle at $n=6$ |
| 5d | BT$(k,2)$ bad-ear asymptotic | Symmetry quotient + reduced $6\times 6$ + cubic resolvents | done | **proved**, `lprime_selector.md` |
| 5e | **Headline:** prove max-degsum selector for general 2-trees | Schur-complement / clique-tree recursion + structural induction; supported by 725-graph $n\le 10$ enumeration | open-ended | new headline target |
| 6 | If step 5e succeeds, prove 9.2 for 2-trees | Stop deletion at $K_3$; telescope ear gains | short once 5e holds | not started |
| 7 | Fallback: residue-control classes | Block-cut tree (2-connected); perfect elimination (chordal); structural enumeration (cactus); SDP / Gluing Lemma (Thm 8.1 regime) | open-ended | not started |
| 8 | Near-extremal sanity checks | Direct spectrum / Cauchy interlacing; verify no $s^- = n - 1$ outside trees and $K_n$ at $n \le 30$ | 1 week | not started |

Steps 1–4 remain guaranteed deliverables. Steps 5a, 5b, 5d are **proved subfamily
theorems**. Steps 5c and 5e are the two genuinely open mathematical problems.

## Three attack vectors, restated honestly

### V1 — $P_3$-removal + structural control on the residue
Lemma 2.4 with slack $17/16$ telescopes to $s^\pm(G) \ge n + k/16 - \ell$. The fight is
bounding $\ell$ (number of clique components in the residue). The source paper's Thm 8.1
wins this fight under $\alpha\omega \le n/17$; a class-specific lemma is needed
elsewhere. **Catch:** the lemma's $17/16$ slack actively selects cut vertices, so the
residue is naturally disconnected even when $G$ is connected.

### V2 — SDP duality + complementary slackness
Lemma 3.1 of arXiv:2506.07264 as stated in the source paper (**without** any support
restriction): $s^+(G) = \inf_{M \succeq 0} \|A(G) + M\|_F^2$, the infimum taken over all
positive semidefinite $M$. Equality $s^+ = n - 1$ forces tight KKT conditions at the
optimum. **Catch:** writing slackness for unknown $G$ is messy; SDP duality usually
yields inequalities, not structural classifications. Worth trying as a complement to V1,
not as a stand-alone route.

### V3 — Inertia / sign-pattern arguments
Use the fact that $n^+(T) = n^-(T) = $ matching number, while $n^+(K_n) = 1$,
$n^-(K_n) = n - 1$. The two extremal points have very different inertia. A proof of
9.2 might separate them by inertia first, then handle each component. **Catch:** the
$s^\pm = n - 1$ hypothesis does not directly pin down the inertia.

**Removed (per v2 review):** edge-deletion / edge-monotonicity. Edge-monotonicity of
$s^\pm$ fails in general (Tang–Liu–Wang, arXiv:2410.09830).

## Failure modes to guard against

- **F1. The residue-component count $\ell$ is the whole problem, not a cleanup step.**
  Any plan that bounds $\ell$ by hand-waving is wrong. For $s^-$, the crude sufficient
  condition is $\ell < k/16 + 1$; for $s^+$ one must track the full clique-size
  distribution, since large clique components help and isolated/$K_2$ components hurt.
  Either way, the bound is class-specific and conjectural.
- **F2. Tacit reliance on EFGW in subclasses where it is open.** "Planar" and
  "$K_t$-minor-free for moderate $t$" are not free — sparse planar cases include
  unicyclic. Restrict to classes where the relevant EFGW statement is unconditional, or
  prove the EFGW statement as a byproduct.
- **F3. Near-extremal traps in part (ii).** $K_n - e$, $K_n -$ matching, skewed
  $K_{p,q}$, complete multipartites $K_{1, 1, \ldots, 1, 2}$, $K_1 \vee (K_a \cup K_b)$.
  Numerical verification at $n \le 9$ (paper) and $n \le 30$ (step 8 below) is
  reassuring; an analytical proof must give an explicit positive gap, or a rigorous
  argument that any asymptotic slack remains positive in the relevant range. Do not rely
  on numerical or asymptotic slack that could vanish or change sign.
- **F4. Regularity is not preserved by induced vertex deletion.** Regularity was listed
  in v1 among classes for the induction; this is unusable for any $P_3$-removal route
  and was removed in v2.

## Concrete next action (v8)

1. **Polish steps 2–3** (`corollaries_AB.md`) for the short internal note.
2. **Step 5e (new headline).** Attempt the max-degsum selector for general
   2-trees. The empirical support is strong (725/725 at $n\le 10$, $\min=1.2940$;
   BT$(k,2)$ at $k=50,100$). The natural attack is structural:
   - Use the clique tree of the 2-tree. The maximum-degsum simplicial ear's
     supporting edge $\{a,b\}$ lies in a triangle whose third vertex (in $G-v^*$)
     is the dominant clique-tree node by degree count.
   - Write the Schur complement at $v^*$ as a low-rank update of $A(H)$ and bound
     its effect on $s^\pm$ from below using the cumulative structure of $H$.
   - Reduce ties via a secondary criterion (e.g. cluster-coefficient at the
     supporting edge), if ties ever bite at scale.
3. **Step 5c (finite-$n$ 2-paths).** The Szegő asymptotic is not enough for a
   theorem. The obstacle is that the natural Widom-type secular bound is **not
   sharp** at the $n=6$ worst case ($\delta^- = 1.319$). Two paths:
   - Replace Widom with a finite-$n$ correction term derived from the explicit
     pentadiagonal eigenvalue formula, recovering sharpness in $n$.
   - Or: a direct interlacing argument using $L_n = L_{n-1} + $ rank-2 update,
     which the closed-form $L_n$ spectrum admits explicitly.
4. **Continue the regression harness** in `tests/test_lprime_subfamilies.py`
   (13 passing). Extend to (a) max-degsum selector on $\mathrm{BT}(k,2)$ for
   $k\le 200$, (b) random 2-trees seeded reproducibly at $n=20,30,50$, (c) any
   structural candidate selector proposed during step 5e.

## Critical reading

arXiv:2506.07264 (source), arXiv:1409.2079 (EFGW), arXiv:2303.11930 (Abiad et al.,
equality cases with $\le 2$ positive eigenvalues), arXiv:2311.11530
(Elphick–Linz, $s^+$/$s^-$ asymmetry), arXiv:2410.09830 (Tang–Liu–Wang,
edge-monotonicity fails), arXiv:2409.15504 (Zhang, $n/2$ lower bound),
arXiv:2409.18220 (Akbari–Kumar–Mohar–Pragada, $3n/4$ lower bound + earlier
$P_3$-removal). New in v8: standard references for Szegő's theorem on
Toeplitz matrices (Grenander–Szegő; Böttcher–Silbermann *Analysis of Toeplitz
Operators*, §5) for the 2-paths asymptotic.

## Open subtasks (status updated)

- `scripts/spectrum_check.py` — compute $s^\pm, n^\pm$ on small classes;
  validate residue accounting. **Status: implemented.**
- `tests/near_extremal_sanity.py` — **(fallback, step 8)** explicit spectra for
  $K_n - e$, $K_n + $ pendant, skewed $K_{p,q}$, $K_1 \vee (K_a \cup K_b)$,
  friendship graphs, complete multipartites $K_{1,1,\ldots,1,2}$; assert
  $s^- > n-1$ except at allowed endpoints. **Status: not started.**
- `tests/p3_removal_witness.py` — **(fallback, step 7)** for each connected $G$
  at $n\le 9$, enumerate sign-specific $P_3$-removal sequences and record
  $(k,\ell;n_1,\ldots,n_\ell)$ at termination. Relevant only if the 2-tree route
  fails and the residue-control programme is revived. **Status: not started.**
- `tests/two_tree_ear_gain.py` — enumerate 2-trees up to the largest feasible
  order; for every simplicial degree-2 ear compute $\delta^\pm$. Two jobs:
  (a) regression-test the false universal lemma using `tests/fixtures/`
  (b) test (L') by maximizing $\min(\delta^+,\delta^-)$ over ears.
  **Status: implemented; n≤10 data in `data/two_tree_ear_gains_n*.json`.**
- `tests/test_lprime_subfamilies.py` — proved-subfamily regression tests
  (books, 2-paths $n\le 200$, BT$(k,2)$). **Status: implemented; 13 passing.**
- (**v8 NEW**) `tests/test_max_degsum_selector.py` — for every 2-tree in the
  enumerated set, verify that the max-degsum-selected ear has
  $\min(\delta^+,\delta^-)\ge 17/16$. Extend to seeded random 2-trees at
  $n\in\{20,30,50,100\}$. Status: to be implemented.
- (**v8 NEW**) `tests/test_two_path_widom_tightness.py` — measure the
  finite-$n$ gap between $\delta^-(L_n)$ and the Szegő-limit prediction, and
  the corresponding gap to the Widom-type secular bound, to localize where
  the bound fails to be sharp. Status: to be implemented.

These subtasks reflect the v8 state. The Phase-3 universal-lemma regression
under `tests/fixtures/two_tree_universal_counterexamples.json` is kept
permanently.
