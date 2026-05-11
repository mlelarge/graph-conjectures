# Earth–Moon upper-bound notes — Phase 6 working file

Companion to [`plan.md`](plan.md) Phase 6 and to [`literature_notes.md`](literature_notes.md).
Tracks the density-theorem route to $\chi_{\rm EM} \le 11$ and what's needed
from the colour-critical-graph literature.

## Target lemma

> **Lemma (target).** Every 12-critical $K_9$-free graph $G$ satisfies
> $|E(G)| \ge 6n - 11$ (equivalently $|E(G)| > 6n - 12$).

Combined with the biplanar edge bound $|E(G)| \le 6n - 12$, this would
exclude any 12-critical $K_9$-free biplanar graph, hence
$\chi_{\rm EM} \le 11$.

## The gap and what closing it means

Kostochka–Yancey (2014, [arXiv:1209.4255](https://arxiv.org/abs/1209.4255)) prove,
for every $k$-critical graph,

$$|E(G)| \ge \frac{(k+1)(k-2)}{2(k-1)} \, n - \frac{k(k-3)}{2(k-1)}.$$

At $k = 12$ this specialises to

$$|E(G)| \ge \frac{65 n - 54}{11}.$$

The biplanar edge bound is

$$|E(G)| \le 6n - 12 = \frac{66 n - 132}{11}.$$

So the remaining gap, expressed as biplanar-budget minus KY-lower-bound, is

$$\frac{66 n - 132}{11} - \frac{65 n - 54}{11} = \frac{n - 78}{11}.$$

For $n \ge 78$ the two inequalities are jointly satisfiable. To make them
contradict, a $K_9$-free strengthening must improve over KY by **more than
$(n-78)/11$ edges**. Asymptotically that is roughly $n/11$ extra edges
per vertex, which is *not* an arbitrarily small $\epsilon n$ — the
coefficient matters.

Equivalent form: prove $|E(G)| \ge (66 n - 121)/11 = 6n - 11$ for every
12-critical $K_9$-free $G$.

## What is and is not on offer in the literature

This is a Phase 6 audit checklist. Sources to read carefully and report
back on; do not cite anything in publication-grade form before verifying
via the cited PDF.

### Generic KY equality / near-equality structure

- KY proves $k$-Ore graphs achieve equality in their bound. A
  *$k$-Ore graph* is built from copies of $K_k$ by repeated Ore-sum
  operations; the base case is $K_k$ itself.
- For $k = 12$: extremal 12-critical graphs are 12-Ore. Every
  12-Ore graph contains $K_{11}$ (in fact many copies, since each Ore
  sum keeps near-cliques). So any $K_9$-free 12-critical graph is far
  from KY equality — by a $K_8 \to K_{11}$ gap on local clique number.
- Open question for this project: does $K_9$-freeness force enough extra
  edges to close $(n-78)/11$? Working hypothesis: yes for $n$ large
  enough, but the constant must be made explicit.

### Sparse-critical / large-clique-free density refinements

- Kostochka–Yancey, *A Brooks-type result for sparse critical graphs*,
  Combinatorica 2018. Cited by user as relevant. To verify: which
  exclusion gives how much density improvement, and whether the proof
  goes through for $k = 12$, $K_9$-free, finite $n$ (not just asymptotic).
- *Structure in sparse $k$-critical graphs* (Gao, Postle et al., 2022).
  To verify: their structural theorem and any explicit edge-density
  consequence at small $k$.
- Kostochka–Stiebitz, *On the number of edges in colour-critical graphs
  and hypergraphs.* Combinatorica 20 (2000) 521–530. Pre-KY. To verify:
  whether their $K_p$-free addendum gives a useful explicit improvement
  for $k = 12$, $p = 9$.

### Direct $K_9$-freeness route

- Rabern (2011) and follow-ups: density improvements from forbidding a
  large clique. Mostly aimed at Reed's conjecture territory ($\Delta$,
  $\omega$, $\chi$ inequalities). Worth checking whether any such bound
  gives $|E| \ge 6n - 11$ for 12-critical $K_9$-free directly.

## Concrete next steps

1. **Audit KY structural lemmas.** Read Kostochka–Yancey 2014 §3–4 for the
   characterisation of equality (12-Ore graphs) and the structural
   ingredients of the proof (potential method, dischargings, edge counts at
   degree-$(k-1)$ vertices). Record what fails when $K_9$ is forbidden.
2. **Audit Brooks-type and sparse-critical results.** Tabulate each result
   as "what is excluded → what extra density is gained at $k=12$". Skip any
   bound that is asymptotic-only or unspecified-$\epsilon$.
3. **Direct check on small $n$.** For $78 \le n \le 100$, do 12-critical
   $K_9$-free biplanar graphs exist computationally? KSS-style SAT search
   on this exact predicate (fix $\delta \ge 11$, $K_9$-free, biplanar,
   non-11-colourable) would give an empirical floor for whether the
   inequality $|E| \ge 6n - 11$ holds in the regime we care about. Likely
   infeasible past $n \sim 25$, but illuminating for small cases.
4. **Formulate the target lemma.** If existing literature falls short,
   identify the smallest novel structural ingredient that closes the gap
   — e.g., "every 12-critical $K_9$-free graph has at least $\alpha n$
   vertices of degree $\ge 12$, for $\alpha = \dots$". Start from KY's
   discharging weights and see where $K_9$-freeness can buy back density.

## What I have not yet read directly

The following are referenced in the Phase 6 framing but only as titles /
DBLP entries. Each needs a verification pass before any claim depends on
it.

- A. Kostochka, M. Yancey, *Ore's conjecture for $k = 4$ and Grötzsch's
  theorem*, Combinatorica 34 (2014) 781–797.
- A. Kostochka, M. Yancey, *Density of $k$-critical graphs*, JCTB 2014
  ([arXiv:1209.4255](https://arxiv.org/abs/1209.4255)).
- A. Kostochka, M. Yancey, *A Brooks-type result for sparse critical
  graphs*, Combinatorica (2018).
- Z. Gao, D. Liu, L. Postle (or similar authorship), *Structure in sparse
  $k$-critical graphs*, JCTB 2022.
- A. Kostochka, M. Stiebitz, *On the number of edges in colour-critical
  graphs and hypergraphs*, Combinatorica 20 (2000) 521–530.
- L. Rabern, *A note on Reed's conjecture*, SIAM J. Discrete Math. 22
  (2008) 820–827 (and the 2011 / 2014 follow-ups).

This file is the working ledger; promote any of the above to primary
quotes in `literature_notes.md` as we actually read them.
