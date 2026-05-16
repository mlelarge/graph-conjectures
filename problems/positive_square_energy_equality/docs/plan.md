# Plan: prove (a tractable slice of) Conjecture 9.2 of Akbari–Kumar–Mohar–Pragada–Zhang

Source: arXiv:2506.07264, *Refinement of a conjecture on positive square energy of graphs*, June 2025.

**Revision history.**

- **v6** (this version): incorporates the mathematician pass: make **2-trees** the first
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

## The central obstruction (corrects v1 Step 4)

The $P_3$-removal lemma (Lemma 2.4 of arXiv:2506.07264) says: if $G$ has an induced $P_3$,
there is a vertex $u$ such that
$$s^\pm(G) \ge s^\pm(G - u) + \tfrac{17}{16}.$$
The lemma's $s^+$ and $s^-$ versions are both stated in the source paper, so **no
dualization is needed** (v1 was wrong about this). However, the choice of vertex is
**sign-specific**: the lemma does not assert that the same vertex works for both $s^+$
and $s^-$. Any proof must fix one sign, then iterate certified deletions for that sign
until no induced $P_3$ remains. The residue is a **disjoint union of cliques**
$K_{n_1} \sqcup \cdots \sqcup K_{n_\ell}$; the values of $k,\ell$ and the clique-size
vector may depend on the sign and on the chosen valid deletion sequence.

**The fatal observation (review.md).** The $17/16$ gain does **not** preserve connectivity.
Concrete witness: $G = P_3$ has $s^+(P_3) = s^-(P_3) = 2$; deleting either endpoint gives
$K_2$ with $s^\pm = 1$, a gain of only $1 < 17/16$. The only $u$ that achieves the $17/16$
gain is the **middle vertex**, whose removal leaves two isolated vertices — disconnecting
$G$. So even in the smallest connected example, $P_3$-removal selects a cut vertex.

**Correct residue accounting.** Fix one sign $\sigma\in\{+,-\}$ and one certified
$P_3$-removal sequence for that sign. Let $k$ be the number of removed vertices and
$\ell$ the number of clique components in the residue
$K_{n_1} \sqcup \cdots \sqcup K_{n_\ell}$ ($\sum_j n_j = n - k$). The clique spectra
are $\mathrm{spec}(K_t) = \{t-1, -1^{(t-1)}\}$, giving
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
$$s^+(G) \ge \tfrac{17}{16}k+\sum_j(n_j-1)^2.$$
Equivalently,
$$s^+(G)-(n-1)\ge \tfrac{k}{16}+1+\sum_j\bigl((n_j-1)^2-n_j\bigr).$$
So the $s^+$ residue analysis is not controlled by $\ell$ alone: isolated vertices and
$K_2$ components still hurt, while clique components of order at least $3$ help. A
class-specific strict inequality for $s^+$ may follow from a weaker **residue invariant**
than the $s^-$ condition $\ell < k/16+1$, but that invariant must include the clique-size
distribution, not just the component count.

The **central missing lemma** is therefore either a class-specific control on $\ell$, a
sharper Lemma 2.4 whose slack scales with $\ell$, or a different local deletion lemma
that bypasses induced-$P_3$ removal entirely. The source paper's Thm 8.1 sidesteps the
$\ell$ problem by assuming $\alpha(G)\omega(G) \le n/17$, exactly the regime where the
slack dominates the component count.

## What the modest deliverables look like

After the review, the two "1–2 week" variants of v1 are honestly **short corollaries of
results already in the source paper**, not new theorems. They are worth writing up cleanly
but they are not the project.

### Corollary A — 9.2(i) for connected claw-free graphs

Thm 1.1 of arXiv:2506.07264 proves $s^+(G) \ge n$ strictly for every connected claw-free
graph with $\Delta \ge 3$. So in that class $s^+ = n - 1$ is impossible. The $\Delta \le 2$
case is paths and cycles: paths are trees ($\checkmark$), and cycles have $s^+ > n - 1$
(use Prop. 9.1 of the source paper, or compute directly). **Effort: a paragraph.**

Caveat (review.md): claw-free unicyclic graphs with $m = n$ include the infinite family
$P(j, k, \ell)$. The corollary does not reprove that hard case; it delegates the
$\Delta\ge 3$ members of that family to Theorem 1.1 of the source paper, and handles
only the bare-cycle $\Delta\le 2$ case directly. **The phrase "finite case analysis" in
v1 was misleading and is removed.**

### Corollary B — 9.2(i) for graphs of diameter $\le 2$

Diameter $0$: $G=K_1$ is trivial, with $s^+=0=n-1$. Diameter $1$: $G = K_n$ with $n\ge 2$,
$s^+(K_n) = (n-1)^2$, so $s^+ = n - 1$ forces $n = 2$, i.e. $G = K_2$, a tree. $\checkmark$

Diameter exactly $2$: Thm 1.2 of arXiv:2506.07264 gives $s^+(G) \ge n$ except for
$G \in \{K_{1, n-1}, C_5\}$. Of these, $K_{1, n-1}$ is a tree and $s^+(K_{1, n-1}) = n - 1$
$\checkmark$, while $s^+(C_5) = 4.76393\ldots > 4 = n - 1$. **Effort: a paragraph.**

These two corollaries are a **clean internal note** but are not a serious new result —
they are not by themselves a paper, and should be treated as warm-up exposition that
verifies the toolkit, not as a deliverable.

## What a serious result would require, and where to look

The review's recommendation is to look for a **genuinely new equality argument** in a
narrower class where the residue-component count $\ell$ is controllable. Candidate
classes — **each with the specific reason it might fail**, since these are search
directions, not expected theorems:

- **2-trees / maximal chordal graphs of treewidth 2.** This is now the recommended first
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

Target theorem:

> If $G$ is a 2-tree on $n$ vertices, then Conjecture 9.2 holds for $G$: $K_2$ is the
> tree equality case, $K_3$ is the complete-graph equality case for $s^-$, and every
> 2-tree with $n\ge 4$ satisfies $s^+(G)>n-1$ and $s^-(G)>n-1$.

The whole target reduces to the following local lemma.

> **2-tree ear deletion lemma.** Let $G$ be a 2-tree with $n\ge 4$, and let $v$ be a
> simplicial vertex of degree $2$. Then, for the desired sign,
> $$s^\pm(G)\ge s^\pm(G-v)+\frac{17}{16}.$$

If this lemma holds for both signs, iteratively delete simplicial degree-2 vertices
until $K_3$ remains. With $k=n-3$,
$$s^-(G)\ge s^-(K_3)+\frac{17}{16}(n-3)
      =n-1+\frac{n-3}{16}>n-1,$$
and
$$s^+(G)\ge s^+(K_3)+\frac{17}{16}(n-3)
      =4+\frac{17}{16}(n-3)>n-1.$$

This is not a proof yet; it isolates the real local spectral inequality. A plausible
attack is to write $G=H+v$, where $v$ is adjacent exactly to an edge $ab\in E(H)$, and
use the block form
$$A(G)=
\begin{pmatrix}
0 & e_a^T+e_b^T\\
e_a+e_b & A(H)
\end{pmatrix}.$$
The Schur complement
$$\lambda-(e_a+e_b)^T(\lambda I-A(H))^{-1}(e_a+e_b)$$
may be controllable recursively along the clique tree of the 2-tree. If the full lemma
is too hard, first attack **2-paths**, the case where the clique tree is a path.

Immediate failure modes to test:

- The lemma may hold only for **some** simplicial ears, not every simplicial ear.
- The valid ear for $s^+$ and the valid ear for $s^-$ may differ.
- Highly unbalanced 2-trees may push the ear gain down toward $17/16$.
- The base step $K_3\to K_2$ is genuinely exceptional for $s^-$: the gain is only $1$,
  so the induction must stop at $K_3$.

## Revised step-by-step plan

| # | Goal | Technique | Effort | Status |
|---|------|-----------|--------|--------|
| 1 | Easy directions | Bipartite-symmetry for tree; explicit spectrum for $K_n$ | 1 paragraph | not started |
| 2 | Corollary A: 9.2(i) for connected claw-free $G$ | Thm 1.1 + paths/cycles split | 1 paragraph | not started |
| 3 | Corollary B: 9.2(i) for $\mathrm{diam}(G) \le 2$ | Thm 1.2 + check $K_{1,n-1}, C_5$ | 1 paragraph | not started |
| 4 | Write up steps 1–3 as a short note (3–5 pages) | Standard exposition | 1–2 weeks | not started |
| 5 | **First serious target:** prove or refute the 2-tree ear deletion lemma | Schur complement / clique-tree recursion; start with 2-paths | open-ended | not started |
| 6 | If step 5 succeeds, prove 9.2 for 2-trees | Stop deletion at $K_3$; telescope ear gains | short once 5 holds | not started |
| 7 | If 2-trees fail, return to residue-control classes; bound the residue strongly enough to force strictness — for $s^-$ the sufficient crude bound is $\ell < k/16 + 1$, while for $s^+$ the useful invariant is the full clique-size distribution through $\sum (n_j - 1)^2$ | Block-cut tree analysis (2-connected); perfect elimination (chordal); structural enumeration (cactus); SDP / Gluing Lemma (Thm 8.1 regime) | open-ended | not started |
| 8 | Near-extremal sanity checks: $K_n - e$, $K_n + $ pendant, skewed $K_{p,q}$, $K_1 \vee (K_a \cup K_b)$, friendship graphs, complete multipartites | Direct spectrum / Cauchy interlacing; verify no $s^- = n - 1$ outside trees and $K_n$ at $n \le 30$ | 1 week | not started |

Steps 1–4 are guaranteed deliverables. Step 5 is the **actual research problem** now
chosen for attack. If it fails, step 7 is the fallback version of the original
residue-control programme.

## Three attack vectors, restated honestly

### V1 — $P_3$-removal + structural control on the residue (the route above)
Lemma 2.4 with slack $17/16$ telescopes to $s^\pm(G) \ge n + k/16 - \ell$. The fight
is bounding $\ell$ (number of clique components in the residue). The source paper's
Thm 8.1 wins this fight under $\alpha\omega \le n/17$; a class-specific lemma is needed
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

**Removed from v1 (per review):** edge-deletion / edge-monotonicity. Edge-monotonicity
of $s^\pm$ fails in general (Tang–Liu–Wang, arXiv:2410.09830). Listed in v1 with a
warning; v2 drops it entirely.

## Failure modes to guard against (updated)

- **F1. The residue-component count $\ell$ is the whole problem, not a cleanup step.**
  Any plan that bounds $\ell$ by hand-waving is wrong. v1 fell into this; v2/v3 make
  the bound explicit. For $s^-$, the crude sufficient condition is $\ell < k/16 + 1$;
  for $s^+$ one must track the full clique-size distribution, since large clique
  components help and isolated/$K_2$ components hurt. Either way, the bound is
  class-specific and conjectural.
- **F2. Tacit reliance on EFGW in subclasses where it is open.** "Planar" and "$K_t$-minor-free
  for moderate $t$" are not free — sparse planar cases include unicyclic. Restrict to
  classes where the relevant EFGW statement is unconditional, or prove the EFGW
  statement as a byproduct.
- **F3. Near-extremal traps in part (ii).** $K_n - e$, $K_n -$ matching, skewed $K_{p,q}$,
  complete multipartites $K_{1, 1, \ldots, 1, 2}$, $K_1 \vee (K_a \cup K_b)$. Numerical
  verification at $n \le 9$ (paper) and $n \le 30$ (step 7 above) is reassuring; an
  analytical proof must give an explicit positive gap, or a rigorous argument that any
  asymptotic slack remains positive in the relevant range. Do not rely on numerical or
  asymptotic slack that could vanish or change sign.
- **F4. Regularity is not preserved by induced vertex deletion.** v1 listed "regular"
  among classes for the induction; this is unusable for any $P_3$-removal route and is
  removed in v2.

## Concrete next action

1. Write Corollaries A and B (steps 2–3) as a self-contained note; verify by hand on
   small examples.
2. In parallel, set up `scripts/spectrum_check.py` (NetworkX + NumPy) to compute
   $s^+, s^-, n^+, n^-$ for given $G$, and sweep classes at $n \le 12$ to:
   - validate the residue accounting on random small graphs using certified sign-specific
     deletion sequences (this is what step 5 needs to design around),
   - confirm no $s^- = n - 1$ counterexamples in the near-extremal list of step 7.
3. Prioritize **2-trees**. First implement the computational ear-gain check below, then
   attempt the 2-tree ear deletion lemma analytically. Treat it as an open-ended
   research direction with a kill criterion: if a counterexample appears, record its
   structure and return to the broader residue-control programme; if no counterexample
   appears after exhaustive small checks, attack 2-paths first.

## Critical reading

- arXiv:2506.07264 — source paper. Especially: Lemma 2.4 (statement covers both $s^+$
  and $s^-$, both with slack $17/16$), Lemma 3.1 (SDP duality), Lemma 3.2 (Gluing),
  Thm 3.1 (super-additivity), Thm 1.1–1.3 (claw-free, diameter-2, domination), Thm 7.1
  (domination $\le 2$), Thm 8.1 ($\alpha\omega \le cn$), Prop. 9.1 (cycle spectra),
  Conjectures 9.1–9.5.
- arXiv:1409.2079 — original Elphick–Farber–Goldberg–Wocjan paper.
- arXiv:2303.11930 — Abiad et al., equality cases for graphs with $\le 2$ positive
  eigenvalues; line graphs; hyper-energetic graphs.
- arXiv:2311.11530 — Elphick–Linz, asymmetry between $s^+$ and $s^-$. Trees and complete
  graphs are the two obvious equality families for $s^- = n - 1$; the asymmetry
  literature explains why $K_n$ is a special second extremal point for $s^-$. Relevant
  to 9.2(ii).
- arXiv:2410.09830 — Tang–Liu–Wang, edge-monotonicity of $s^\pm$ fails in general.
  Relevant to F3 and to dropping V3 of v1.
- arXiv:2409.15504 — Zhang, extremal values for the square energies; $\min\{s^+, s^-\}
  \ge n/2$.
- arXiv:2409.18220 — Akbari–Kumar–Mohar–Pragada, $3n/4$ lower bound; earlier $P_3$-removal
  lemma with $\epsilon = 1$.

## Open subtasks (to spawn into `scripts/` and `tests/` once execution starts)

- `scripts/spectrum_check.py` — compute $s^+, s^-, n^+, n^-$ for $G$; sweep small classes
  ($n \le 12$) to validate the residue accounting (the crude bound $s^\pm(G) \ge n + k/16
  - \ell$ for both signs; the exact equality $s^-(\text{residue}) = n - k - \ell$; the
  strict inequality $s^+(\text{residue}) = \sum (n_j - 1)^2 > n - k - \ell$ whenever any
  $n_j \ge 3$).
- `tests/near_extremal_sanity.py` — explicit spectrum for $K_n - e$, $K_n + $ pendant,
  skewed $K_{p,q}$, $K_1 \vee (K_a \cup K_b)$, friendship graphs, complete multipartites
  $K_{1, 1, \ldots, 1, 2}$; assert $s^- > n - 1$ strictly except for the allowed
  tree/$K_n$ endpoints. Add parameter restrictions so, for example, skewed $K_{p,q}$
  excludes stars unless the test is explicitly checking equality cases.
- `tests/p3_removal_witness.py` — for each connected $G$ at $n \le 9$, run the $P_3$-removal
  search and record possible $(k, \ell; n_1,\ldots,n_\ell)$ outcomes at termination. The
  lemma is existential, so the script must enumerate induced $P_3$'s and vertices whose
  deletion actually gives the $17/16$ gain for the chosen sign, then optimize over
  deletion sequences rather than follow an arbitrary greedy choice. The default
  objective should be **existence of a good sign-specific sequence**: minimize $\ell-k/16$
  for the $s^-$ direction, and maximize
  $\tfrac{k}{16}+1+\sum_j((n_j-1)^2-n_j)$ for the $s^+$ direction. A separate
  "worst valid sequence" mode can be useful diagnostically but is stronger than needed
  for a proof.
- `tests/two_tree_ear_gain.py` — generate 2-trees up to the largest feasible order
  (deduplicating isomorphism if practical, otherwise labelled construction histories);
  for every simplicial degree-2 vertex $v$ with $G-v\ne K_2$, compute
  $$s^\pm(G)-s^\pm(G-v)$$
  and search for gains below $17/16$. Record the extremal graph, supporting edge, clique
  tree shape, and whether the minimizing ear differs between $s^+$ and $s^-$. Also run
  a random 2-tree search at larger $n$ for highly unbalanced clique trees.

These are not started; create them when (and if) step 5 produces a concrete class-specific
conjectural lemma to test.
