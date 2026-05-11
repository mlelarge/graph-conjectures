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

### KY Brooks-type 2018 — primary, from arXiv:1408.0846

A. Kostochka, M. Yancey, *A Brooks-type result for sparse critical
graphs*, Combinatorica 38 (2018) 887–934
([arXiv:1408.0846](https://arxiv.org/abs/1408.0846)).

**Theorem 6** (page 3, verbatim):

> Let $k \ge 4$ and $G$ be a $k$-critical graph. Then $G$ is $k$-extremal
> if and only if it is a $k$-Ore graph. Moreover, if $G$ is not a
> $k$-Ore graph, then $|E(G)| \ge \frac{(k+1)(k-2)|V(G)| - y_k}{2(k-1)}$,
> where $y_k = \max\{2k - 6, k^2 - 5k + 2\}$. Thus $y_4 = 2$, $y_5 = 4$,
> and $y_k = k^2 - 5k + 2$ for $k \ge 6$.

At $k = 12$: $y_{12} = 144 - 60 + 2 = 86$, so non-12-Ore 12-critical $G$ has

$$|E(G)| \ge \left\lceil \frac{130 n - 86}{22} \right\rceil = \left\lceil \frac{65 n - 43}{11} \right\rceil.$$

Comparing to KY's $\lceil (65n - 54)/11 \rceil$: Brooks-type adds
**exactly $11/11 = 1$ edge** for being non-Ore — uniformly in $n$, the
same constant the user warned us $y_k$ would produce.

#### Phase 6 lever: clique structure of $k$-Ore graphs (settled by citation)

**Claim.** Every $k$-Ore graph $G$ contains $K_{k-1}$ as a subgraph; in
fact, it contains $\Omega(|V(G)|)$ vertex-disjoint copies of $K_{k-1}$.

**Provenance.** Gould–Larsen–Postle 2022 (see the GP entry below) define
a subgraph-measuring parameter $T(G) = \max_{H \subseteq G} \{2r + s : H$
is a disjoint union of $r$ copies of $K_{k-1}$ and $s$ copies of
$K_{k-2}\}$ and prove in Lemma 3.3 that $T(G)$ is linearly lower-bounded
by $|V(G)|$ on $k$-Ore graphs (their proof is part of the apparatus for
Theorem 1.8). In particular $T(G) > 0$, so every $k$-Ore graph contains
$K_{k-1}$.

A direct inductive proof on DHGO compositions resisted us. The natural
invariants $\mathbf{P_1}$ ("for every edge some $K_{k-1}$ avoids both
endpoints") and $\mathbf{P_2}$ ("for any two edges some $K_{k-1}$ avoids
both") either fail to propagate or fail in the base case. A
Fact-14-based decomposition splits $G = G[A] \cup G[B]$ with separating
pair $\{x, y\}$ where both $\tilde{G}(x,y) = G[A] + xy$ and
$\check{G}(x,y) = G[B]/(x{=}y)$ are smaller $k$-Ore — but the joint
case "every $K_{k-1}$ in $\tilde{G}$ uses $xy$, and every $K_{k-1}$ in
$\check{G}$ uses $x{*}y$" is logically consistent with $G$ having no
$K_{k-1}$ at all. So the simple inductive approach doesn't close.

GP's Lemma 3.3 closes the matter via the potential-method framework
rather than direct induction. It is a citable, peer-reviewed proof.

**Consequence.** Every 12-Ore graph contains $K_{11}$, hence contains
$K_9$. So every $K_9$-free 12-critical graph is non-12-Ore, and
Brooks-type Theorem 6 applies unconditionally:

$$|E(G)| \ge \left\lceil \frac{65n - 43}{11} \right\rceil$$

for every $K_9$-free 12-critical graph on $n$ vertices. The $n \le 88$
closure is now uncontingent.

#### What Brooks-type closes, what it leaves

Comparing the non-12-Ore bound against the biplanar edge budget:

| $n$ | KY $\lceil(65n-54)/11\rceil$ | Brooks $\lceil(65n-43)/11\rceil$ | biplanar $\le 6n-12$ | KY < biplanar? | Brooks < biplanar? |
|---:|---:|---:|---:|---|---|
| 78 | 456 | 457 | 456 | yes | **NO** |
| 88 | 516 | 517 | 516 | yes | **NO** |
| 89 | 521 | 522 | 522 | yes | yes (tight) |
| 90 | 527 | 528 | 528 | yes | yes (tight) |
| 99 | 581 | 582 | 582 | yes | yes (tight) |
| 100 | 586 | 587 | 588 | yes | yes |
| 150 | 882 | 883 | 888 | yes | yes |

Brooks-type contradicts biplanar exactly for $n \in [78, 88]$. So:

- **KY alone excludes biplanar 12-critical at $n \le 77$.**
- **KY + Brooks-type (i.e. $K_9$-free + 12-critical, via non-Ore) excludes biplanar at $n \le 88$.**
- **At $n \ge 89$ neither bound rules out biplanar 12-critical $K_9$-free.**

So Brooks-type buys 11 more vertex counts (78 through 88) but stalls
exactly at the second sharp interval $n = 89..99$, where we need a
further $\lfloor (n - 67)/11 \rfloor - 1 = 1$ edge of slack. To finish
Phase 6 we need either:

1. **A K_9-free-aware strengthening of Brooks-type** that lowers $y_k$
   below $k^2 - 5k + 2$ when $K_9$ is forbidden. Theorem 6 as written
   has $y_k$ depend only on $k$; the proof in Sections 3–5 may admit
   a $K_p$-free variant with a smaller $y_k$.
2. **Iterated "not Ore-sum of small graphs" arguments.** A 12-critical
   $K_9$-free graph is not the DHGO-composition of two small 12-Ore
   pieces either; this might add another constant. Needs verification.
3. **Direct $K_9$-free + critical density bounds from elsewhere**
   (Kostochka–Stiebitz $K_p$-free addendum, Gao–Postle structure).

### Kostochka–Stiebitz 2000 — primary

A. Kostochka, M. Stiebitz, *On the number of edges in colour-critical
graphs and hypergraphs*, Combinatorica 20 (2000) 521–530
([PDF](https://kostochk.web.illinois.edu/docs/2000/jctb2000Sti.pdf)).

The paper's headline (Theorem 1) is about triangle-free $k$-list-critical
graphs: $|E| \ge (k - o(k))n$, asymptotic in $k$. The $K_p$-free analogue
is stated as a Remark on page 524, derived from the same Theorem 4
applied via Johansson's $K_r$-free chromatic-number bound:

> "Recently, Johansson [8] proved that for every positive integer $r$
> there is a constant $c_r$ such that
> $\chi_l(G) \le (c_r \Delta \log \log \Delta)/\log \Delta$
> for every $K_r$-free graph $G$ with maximum degree at most $\Delta \ge 2$.
> Using this result, Theorem 4 implies that if $r$ is an positive integer,
> then every $k$-list-critical $K_r$-free graph on $n$ vertices has at
> least $(k - o(k))n$ edges."

**Theorem 4 proof gives an explicit error term.** The orientation
argument on page 524 produces $m \ge (k - 2 f(g(k))) n$, where $g(k)$ is
defined by $g(k) f(g(k)) = k^2$ and $f(\Delta) = c_r \Delta \log\log\Delta / \log\Delta$
is Johansson's bound. So the $o(k)$ is concretely $2 f(g(k))$.

**Does this beat $6n - 11$ at $k = 12, r = 9$?** Coefficient must satisfy
$k - 2 f(g(k)) \ge 6$, i.e. $f(g(12)) \le 3$. Solving
$g \cdot f(g) = 144$ at $k = 12$ for a range of plausible Johansson
constants $c_9$:

| $c_9$ | $g(12)$ | $f(g(12))$ | $2 f(g(12))$ | leading coefficient $12 - 2f(g)$ |
|---:|---:|---:|---:|---:|
| 0.1 | 64.85 | 2.22 | 4.44 | **7.56** (beats $6n$) |
| 0.3 | 36.73 | 3.92 | 7.84 | 4.16 (does not beat $6n$) |
| 1.0 | 19.83 | 7.26 | 14.53 | $-2.53$ (vacuous) |
| 3.0 | 11.46 | 12.57 | 25.13 | $-13.1$ (vacuous) |

So the KS + Johansson bound finishes Phase 6 at $k = 12$ iff Johansson's
constant for $K_9$-free graphs satisfies roughly $c_9 \lesssim 0.2$.

**Status.** Johansson's 1996 result is unpublished; the constants are not
stated explicitly in the paper. Modern explicit improvements over Johansson:

- Molloy (2019, *The list chromatic number of graphs with small clique
  number*): for triangle-free, $\chi_l \le (1 + o(1)) \Delta / \log \Delta$.
- Davies, Kang, Pirot, Sereni (later, $K_r$-free generalisations).

Neither of these is yet folded into our audit. The path to finishing
Phase 6 via this route is concrete: **find an explicit $K_9$-free
chromatic-list bound of the form $\chi_l \le c_9 \Delta \log \log \Delta / \log \Delta$
with $c_9 \le 0.2$** (or roughly equivalent). Without such an explicit
constant, KS 2000 alone does not close Phase 6 at the finite $k = 12$
we care about.

### Gould–Larsen–Postle 2022 — primary

R. J. Gould, V. Larsen, L. Postle, *Structure in sparse $k$-critical
graphs*, J. Combin. Theory Ser. B 156 (2022) 194–222
([PDF](https://www.math.emory.edu/~rg/sparse.pdf)).

The relevant statement is **Conjecture 1.6** (due to Postle):

> For every $k \ge 4$, there exists $\varepsilon_k > 0$ such that if $G$ is a
> $k$-critical $K_{k-2}$-free graph, then
> $$|E(G)| \ge \left(\frac{k}{2} - \frac{1}{k-1} + \varepsilon_k\right) |V(G)| - \frac{k(k-3)}{2(k-1)}.$$

This is the right shape for Phase 6: it strengthens KY by a positive
$\varepsilon_k n$ under a clique-exclusion hypothesis. For $k = 12$ the
hypothesis is "$K_{10}$-free", which is *implied by* our $K_9$-free
hypothesis. So the conjecture would apply directly.

**Status at $k = 12$.** The conjecture is **open**. GP prove it for
$k \ge 33$ (Corollary 1.10). The only previously known cases are
$k = 5$ (Postle 2017) and $k = 6$ (their reference [4]). $k = 12$ sits
in the gap.

**Even if it held at $k = 12$, the explicit $\varepsilon_k$ is too small.**
GP construct $\varepsilon = 4/(k^3 - 2k^2 + 3k)$ in Definition 4. At
$k = 12$:

$$\varepsilon_{12}^{GP} = \frac{4}{1728 - 288 + 36} = \frac{4}{1476} \approx 0.00271.$$

The asymptotic Phase 6 gap is $1/(k-1) = 1/11 \approx 0.0909$ per vertex
($\chi_{\rm EM}$-biplanar coefficient 6 minus the KY coefficient $65/11$).
So GP's $\varepsilon_{12}$ is about **3% of what's needed** — even if
the conjecture were proved at $k = 12$ with their constant. To close
Phase 6 the constant has to be roughly $\varepsilon_{12} \ge 1/11$,
which is over 30× the GP value.

So both routes through the published asymptotic literature fail:
- KS 2000 + Johansson: needs explicit $c_9 \le 0.2$ in Johansson; modern
  bounds give $c_9 \sim 8$ to $1800$. Off by 1–4 orders of magnitude.
- GP 2022: conjecture not even proved at $k = 12$; explicit $\varepsilon_{12}$
  in the proven range is 30× too small.

The asymptotic-with-tiny-constant chain is decisively inadequate for the
finite, sharp Earth–Moon application at $k = 12$.

### Useful by-product: $k$-Ore graphs have linearly many $K_{k-1}$'s

GP's Lemma 3.3 (paraphrased): in a $k$-Ore graph, the number $T(G)$ of
disjoint $K_{k-1}$ and $K_{k-2}$ subgraphs is linearly bounded below by
$|V(G)|$. In particular, every $k$-Ore graph contains $K_{k-1}$ as a
subgraph — concretely, **linearly many vertex-disjoint copies**. This
finally gives a citable proof of the Phase 6 lever lemma we left open
above, and resolves the contingency on the $n \le 88$ closure: every
$K_9$-free 12-critical graph really is non-12-Ore, so Brooks-type
applies cleanly.

### Strategic conclusion

The asymptotic literature does not finish Phase 6 at finite $k = 12$.
The path forward is **a bespoke discharging / potential argument
specific to $k = 12$, $K_9$-free**. Specifically, the GP framework
gives the template: define an $\varepsilon$-potential
$\rho(G) = ((k-2)(k+1) + \varepsilon')|V(G)| - 2(k-1)|E(G)| - \delta' T(G)$
and show $\rho(G) \le $ constant via discharging, where $T(G)$ counts
disjoint $K_{k-1}$ / $K_{k-2}$ / $K_9$-forbidden substructures. The
constants $\varepsilon'$, $\delta'$ are free parameters; the goal is
to make $\varepsilon'$ large enough to close $\chi_{\rm EM}$.

This is open mathematical work, not a literature audit.

### Remaining audit queue (largely closed)

The four main candidate routes have all been audited and found
insufficient at $k = 12$:

- KY 2014: closes $n \le 77$. Sharp.
- Brooks-type 2018: closes $n \le 88$, now uncontingent thanks to GP
  Lemma 3.3.
- KS 2000 + Johansson: asymptotic, requires unknown small $c_9$.
- GP 2022: open at $k = 12$ as conjecture; even if true, explicit
  $\varepsilon_{12}$ is 30× too small.

No remaining audit is expected to close the asymptotic case. New work
is required.

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
