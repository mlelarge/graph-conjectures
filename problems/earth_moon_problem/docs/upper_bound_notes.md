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

Kostochka–Yancey (2014, [arXiv:1209.1050](https://arxiv.org/abs/1209.1050)) prove,
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

### KY 2012/2014 — primary, from the arXiv:1209.1050 PDF

**Theorem 3** (page 3, verbatim):

> If $k \ge 4$ and $G$ is $k$-critical, then
> $|E(G)| \ge \lceil ((k+1)(k-2)|V(G)| - k(k-3)) / (2(k-1)) \rceil$.
> In other words, if $k \ge 4$ and $n \ge k$, $n \ne k+1$, then
> $f_k(n) \ge F(k,n) := \lceil ((k+1)(k-2)n - k(k-3)) / (2(k-1)) \rceil$.

At $k = 12$: $F(12, n) = \lceil (65n - 54)/11 \rceil$.

**Corollary 6** (page 17, restated verbatim):

> For $k \ge 4$, $0 \le f_k(n) - F(k,n) \le (1 + o(1)) k^2/8$. In particular,
> $\phi_k = k/2 - 1/(k-1)$.

This is the load-bearing fact for our Phase 6 plan. At $k = 12$ the gap
between the actual minimum and the KY bound is at most $\sim k^2/8 = 18$
edges *uniformly in $n$* — independent of how large $n$ gets. So any
hope of closing the Earth–Moon upper bound by a generic strengthening of
KY (forbidding nothing structural) is capped at $\sim 18$ edges per
$n$, which is far short of the $(n-78)/11$ we need. **$K_9$-freeness has
to do all the work**, not generic structure.

**Theorem 37** (page 16, sharpness, verbatim):

> If one of the following holds:
> 1. $n \equiv 1 \pmod{k-1}$ and $n \ge k$,
> 2. $k = 4$, $n \ne 5$, and $n \ge 4$, or
> 3. $k = 5$, $n \equiv 2 \pmod 4$, and $n \ge 10$,
> then $f_k(n) = F(k,n) = \lceil ((k - 2/(k-1)) n - k(k-3)/(k-1))/2 \rceil$.
>
> Proof. By (5), we only need to show that (9) is tight when
> 1. $n = k$, 2. $k = 4$, $n = 6$, 3. $k = 4$, $n = 8$, and 4. $k = 5$, $n = 10$.
> The first case follows from $K_k$. The other three cases follow from Figure 1.

So at $k = 12$, KY is tight exactly when $n \equiv 1 \pmod{11}$, i.e.
$n \in \{12, 23, 34, 45, 56, 67, 78, 89, \dots\}$.

**Crucial coincidence.** $n = 78$ is one of the equality cases:
$78 = 7 \cdot 11 + 1$. At $n = 78$ the KY lower bound and the biplanar
upper bound *exactly coincide*:

$$F(12, 78) = \lceil (65 \cdot 78 - 54)/11 \rceil = \lceil 5016 / 11 \rceil = 456,$$
$$6 \cdot 78 - 12 = 456.$$

So $n = 78$ is the first vertex count at which 12-critical and biplanar
become inequality-compatible — and it's also the first vertex count
where KY is sharp at $k = 12$. The candidate that achieves both
inequalities with equality would be a 12-Ore graph on 78 vertices that
happens to be biplanar.

### KY equality structure — primary, paper Section 5 + Figure 1

The proof of Theorem 37 says the equality cases (for $n \equiv 1 \pmod{k-1}$,
$n \ge k$) "follow from $K_k$" plus Hajós sums to reach larger $n$. At
$k = 12$, the extremal graphs are 12-Ore graphs — built by repeated
Hajós/Ore operations starting from copies of $K_{12}$ (KY's equation
(5) gives the recurrence $f_k(n + (k-1)) \le f_k(n) + (k-1)(k-2/(k-1))/2$,
realized by Hajós' construction).

**Structural lever for Phase 6.** Every 12-Ore graph contains $K_{11}$
as a subgraph (one Ore step preserves the $K_{12}$ minus an edge with
its $K_{11}$ neighbourhood). Hence:

> **Observation.** Every KY-equality 12-critical graph contains
> $K_{11}$, so in particular contains $K_9$. Therefore no $K_9$-free
> 12-critical graph achieves equality in the KY bound.

The question becomes quantitative: what is the smallest gap
$f_{12}^{K_9\text{-free}}(n) - F(12, n)$, where the new $f$ minimises
over 12-critical *$K_9$-free* graphs? Our target $|E| \ge 6n - 11$ is
equivalent to

$$f_{12}^{K_9\text{-free}}(n) - F(12, n)
\ge 6n - 11 - F(12,n)
= \left\lfloor \frac{n - 67}{11} \right\rfloor
\quad (n \ge 78).$$

So the first sharp interval only needs one extra edge over KY:
$n = 78,\dots,88$ require gap $\ge 1$; $n = 89,\dots,99$ require
gap $\ge 2$; and so on.

For $n \le 78$ this is automatic from KY plus the integer-edges
constraint; the real work is at $n \ge 78$.

### Dirac-style structural ingredients — KY §6.1

**Lemma 41 (Dirac)** (page 19, verbatim, lightly paraphrased):

> Let $k \ge 3$. There are no $k$-critical graphs with $k+1$ vertices,
> and the only $k$-critical graph (call it $D_k$) with $k+2$ vertices
> is obtained from the 5-cycle by adding $k-3$ all-adjacent vertices.

So at $k = 12$, $D_{12}$ has 14 vertices and contains $K_9$ (the 9 added
all-adjacent vertices form a clique on which the $C_5$ joins). Again
$K_9$-freeness eliminates the equality structure on small $n$.

**Lemma 40** (page 19): if $G'$ is $(d+1)$-critical with maximum degree
$d+1$ and degree-$(d+1)$ vertices forming an independent set, then the
number $h$ of such vertices satisfies
$\lceil ((d-2)n - (d+1)(d-2))/d \rceil \le h \le \lfloor (n-3)/(d-1) \rfloor$.
This constrains the degree sequence of 12-critical graphs and combines
with the kernel-perfect bipartite-edge bounds in Lemma 10 / Corollary 11.

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
- A. Kostochka, M. Yancey, *Ore's Conjecture on color-critical graphs is
  almost true*, JCTB 109 (2014) 73–101
  ([arXiv:1209.1050](https://arxiv.org/abs/1209.1050)).
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
