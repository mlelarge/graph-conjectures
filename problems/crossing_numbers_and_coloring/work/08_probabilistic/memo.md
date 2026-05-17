# Memo — R2 (Crossing Lemma refinements) and R3.5 ($k$-planar / Schaefer)

Author role: probabilistic / topological combinatorics expert (Role 8).
Owner of: R2 (Crossing Lemma constant chain, including min-degree-aware R2c) and
R3.5 ($k$-planar / Schaefer direction).
Date: 2026-05-16.

Scope. This memo (i) audits the Crossing Lemma constant chain
$$4r \to 3.57r \to 3.03r \to 2.8118r$$
that the plan v3 attributes to ACF $\to$ Barát–Tóth $\to$ Ackerman $\to$ Cranston,
verifying each step against the cited source; (ii) lays out what a min-degree-aware
("R2c") Crossing-Lemma refinement could plausibly give; (iii) maps the $k$-planar /
Schaefer landscape and locates where Albertson is open for graphs with bounded
crossing number; (iv) sketches whether modern probabilistic combinatorics could
realistically yield a new constant in 12 months. Sections numbered as required by
the task spec.

References that I was able to verify against arXiv abstracts during the writing of
this memo are tagged "[abstract OK]". Items I could only confirm by chain-citing
through Cranston 2025 are tagged "[needs PDF read]"; for those, the body of the
memo flags the residual uncertainty explicitly.

---

## 1. The Crossing Lemma chain

**Statement.** For every (simple) graph $G$ drawn in the plane,
$$\operatorname{cr}(G) \;\ge\; c \cdot \frac{|E(G)|^3}{|V(G)|^2}
   \qquad \text{whenever } |E(G)| \;\ge\; \alpha \, |V(G)|.$$

The lemma is *proven* with explicit $(c, \alpha)$; the *true optimal* $(c^\star,
\alpha^\star)$ as $|E|/|V| \to \infty$ is conjectured but not proven. Below, the
column "Source" cites the arXiv ID; "Status" distinguishes proven from
conjecture / unverified-here.

| Step | $(c, \alpha)$ | Source | Status |
|------|---------------|--------|--------|
| ACNS (1982) | $c = 1/64$, $\alpha = 4$ | Ajtai–Chvátal–Newborn–Szemerédi 1982; Leighton 1983 | proven, classical; standard random-deletion proof |
| Pach–Tóth | $c = 1/33.75$ ($> 1/64$), $\alpha = 7.5$ | Pach–Tóth, *Graphs drawn with few crossings per edge*, Combinatorica 1997 | proven [needs PDF read for exact $(c, \alpha)$] |
| PRTT (2006) | $c = 1/31.1$, $\alpha = ?$ ($\sim 7$) | Pach–Radoičić–Tardos–Tóth, *Improving the Crossing Lemma by finding more crossings in sparse graphs*, Discrete & Comput. Geom. 2006 | proven [needs PDF read] |
| Ackerman (2019) | $c = 1/29$, $\alpha = 7$ | arXiv:1509.01932 [abstract OK] | proven; abstract gives the $6n - 12$ bound for $\le 4$ crossings per edge |
| Bungener–Kaufmann (2024) | $c = 1/27.48$, $\alpha = 6.77$ | arXiv:2409.01733 [abstract OK] | proven; **discrepancy with plan v3**: plan v3 quotes $\alpha = 6.95$; the arXiv abstract says $m > 6.77n$. Either Cranston 2025 cites a slightly different threshold form, or the plan's $6.95$ is wrong. **Needs PDF read** to resolve. |

**Believed-optimal constant.** The proof technique (random subgraph + ACNS / iteration / dense-subgraph characterization) is widely believed to be slack. A common heuristic puts the true asymptotic constant around $c^\star \approx 1/15.9$, motivated by extremal random topological graph constructions (Pach–Tóth, *Geom. Funct. Anal.* style); I could not pin a definitive citation in this pass. **No matching proven lower bound exists**, and the chain $1/64 \to 1/27.48$ has been moving by progressively smaller increments — see the Obstruction O1 discussion in the plan.

To make the increments concrete: ACNS $\to$ PT was a $\sim 2\times$ gain ($1/64 \to 1/33.75$); PT $\to$ PRTT was an $\sim 8\%$ gain ($1/33.75 \to 1/31.1$); PRTT $\to$ Ackerman was a $\sim 7\%$ gain ($1/31.1 \to 1/29$); Ackerman $\to$ BK was a $\sim 5\%$ gain ($1/29 \to 1/27.48$). Linear extrapolation of *gains* (each 60–70% of the previous) suggests the next step might be a $\sim 3\%$ gain to $\approx 1/26.6$, and the asymptote of this geometric series is around $1/24$ — well above the heuristic optimum $1/15.9$. The Pach–Tóth chain is **slowing**, which is consistent with the "techniques exhausted" reading in plan §Obstruction O1.

**Where the proof has slack.** The standard ACNS random-deletion proof:

1. Sample each vertex of $G$ with probability $p$ independently; let $G_p$ be the induced subgraph.
2. By the simple Euler-style bound $\operatorname{cr}(H) \ge |E(H)| - 3|V(H)| + 6$ for any graph $H$,
3. $\mathbb{E}[\operatorname{cr}(G_p)] \ge \mathbb{E}[|E(G_p)|] - 3\mathbb{E}[|V(G_p)|] = p^2 |E| - 3 p |V|$.
4. $\mathbb{E}[\operatorname{cr}(G_p)] \le p^4 \operatorname{cr}(G)$ (each crossing survives with probability $p^4$).
5. Optimize $p = 4 |V| / |E|$ for $|E| \ge 4|V|$, get $\operatorname{cr}(G) \ge |E|^3 / (64 |V|^2)$.

The slack lies in (2) and (4). Replacing Euler with a $k$-planar bound (Pach–Tóth) saves on (2); the Ackerman / BK improvements iterate this. The bound (4) is tight only if crossings can be made "independent", which they cannot be in the original drawing — there is residual slack in (4) that has never been systematically exploited. **R2 could in principle bite on (4)** via a correlation inequality on simultaneous crossing survival, but I cannot find a published attempt.

**Threshold $\alpha$ matters as much as $c$.** Going from $|E| \ge 7|V|$ (Ackerman) down to $|E| \ge 4|V|$ degrades the constant to roughly $1/64$ (the original ACNS regime). For $t$-critical graphs with $\delta \ge t - 1$ at small $t$ (say $t = 10$), the density $|E|/|V| \ge (t-1)/2 = 4.5$ sits *below* the Ackerman / Bungener–Kaufmann threshold — so the strong constants do not apply, and one is forced to use the worse regime. This is exactly Cranston's failure mode F2 in plan §"Failure modes" and is operationally critical for any push beyond $2.8118r$ at small $t$.

### Why the Crossing Lemma chain hinges on $k$-planar bounds

The pattern in the chain is the same at every step:

1. Prove a sharper edge bound for $k$-planar graphs (where $k = 0, 1, 2, 3, 4$ are the values that have been pushed):
   - $k = 0$: $|E| \le 3|V| - 6$ (Euler).
   - $k = 1$: $|E| \le 4|V| - 8$ (Pach–Tóth 1997, also Bodlaender–Tan and others).
   - $k = 2$: $|E| \le 5|V| - 10$ (Pach–Tóth 1997).
   - $k = 3$: $|E| \le 5.5|V| - 11$ (Pach–Radoičić–Tardos–Tóth 2006; sharpened by Ackerman).
   - $k = 4$: $|E| \le 6|V| - 12$ (Ackerman 2019).
2. Combine: a graph with $\operatorname{cr}(G) \cdot 5 < |E|$ has some edge with $\ge 5$ crossings, contradicting 4-planarity; so deleting that edge reduces $\operatorname{cr}$ by $\ge 5$ at the cost of one edge.
3. Iterate to extract the $|E|^3/|V|^2$ shape.

The BK refinement (forbidding specific local configurations in dense 2- and 3-planar drawings) is a refinement of step 1 at $k = 2, 3$. The next plausible refinement is at $k = 4, 5$ — i.e. a sharper bound than Ackerman's $6|V| - 12$ for dense 4-planar drawings under additional local constraints.

### Bungener–Kaufmann fine structure (arXiv:2409.01733)

The abstract gives two intermediate finite forms that are stronger than the plain $c |E|^3/|V|^2$ shape:

- For $5n < m \le 6n$: $\operatorname{cr}(G) \ge (37/9) m - (155/9)(n - 2)$.
- For $m > 6n$: $\operatorname{cr}(G) \ge 5 m - (203/9)(n - 2)$.

These piecewise *linear-in-$m$* bounds are sharper than the Crossing-Lemma cube in the intermediate-density regime, and they are the actual workhorses behind Cranston's $2.8118r$ exclusion. Any R2 improvement should not just chase $c$ but also chase the piecewise constants $37/9$, $155/9$, $5$, $203/9$ in this finite-density range.

---

## 2. Albertson reduction via Crossing Lemma — verifying the chain

The "ACF skeleton" combines three ingredients:

1. **Criticality $\Rightarrow$ density.** $\delta(G) \ge t - 1$ (Dirac 1952), so
   $|E(G)| \ge \frac{t-1}{2} |V(G)|$.
2. **Crossing Lemma.** $\operatorname{cr}(G) \ge c \cdot |E|^3 / |V|^2$ for $|E| \ge \alpha |V|$.
3. **Target.** $\operatorname{cr}(G) < \operatorname{cr}(K_t) \le Z(t) \sim t^4/64$.

Substitute (1) into (2): write $|V| = n$, so $|E| \ge (t-1)n/2$, hence
$$\operatorname{cr}(G) \;\ge\; c \cdot \frac{((t-1)n/2)^3}{n^2}
   \;=\; \frac{c (t-1)^3}{8} \cdot n.$$

For an MCE, $\operatorname{cr}(G) < \operatorname{cr}(K_t) \le Z(t) \le t^4/64$, so
$$n \;<\; \frac{8 \cdot t^4/64}{c (t-1)^3}
   \;=\; \frac{t^4}{8\,c\,(t-1)^3}
   \;\approx\; \frac{1}{8c} \cdot t
   \quad (\text{as } t \to \infty).$$

So the MCE upper bound is asymptotically $n \le t / (8c)$, modulo the (vanishing) $(t/(t-1))^3$ factor. This is the chain. Verifying each row:

| Source | $c$ | Predicted $n/t$ bound $\approx 1/(8c)$ | Plan v3 figure | Match? |
|--------|-----|----------------------------------------|----------------|--------|
| ACF (uses $c = 1/32$ in old form) | $1/32$ | $n \le 4t$ | $4t$ | yes, by construction |
| Barát–Tóth | improved through density refinement | $n \le 3.57t$ | $3.57t$ | needs PDF for exact constant the BT proof uses |
| Ackerman | $c = 1/29$ via $\le 4$-crossings-per-edge | $n \le 1/(8 \cdot 1/29) = 3.625t$ | $3.03t$ | **does not match $1/(8c)$ naively**; Ackerman's $3.03t$ uses the *finer* $|E| \le 6n - 12$ bound for $\le 4$ crossings/edge, not the raw $1/29$ in the Crossing Lemma. See the correction below. |
| Bungener–Kaufmann (per Cranston) | $c = 1/27.48$, plus the piecewise $5m - 203/9 \cdot (n-2)$ bound | naive: $1/(8 \cdot 1/27.48) = 3.435t$; with the piecewise refinement Cranston extracts $2.8118t$ | $2.8118t$ | the headline Cranston number combines BK with a *finer* edge-density argument and the Fox–Pach–Suk-style chromatic-index lemma, not the raw Crossing Lemma alone. The naive substitution gives only $\approx 3.4t$. |

**Worked example: the ACF $|V| \le 4t$ bound.** ACF's original derivation uses the Crossing Lemma in the form $\operatorname{cr}(G) \ge |E|^3 / (64 |V|^2)$ (i.e., $c = 1/64$ with the looser threshold $|E| \ge 4|V|$). Combined with $|E| \ge (t-1)|V|/2$ and $\operatorname{cr}(G) < \operatorname{cr}(K_t) \le t(t-1)(t-2)(t-3)/64 < t^4/64$:
$$\frac{((t-1)|V|/2)^3}{64 |V|^2} < \frac{t^4}{64} \;\Rightarrow\; (t-1)^3 |V|/8 < t^4 \;\Rightarrow\; |V| < \frac{8 t^4}{(t-1)^3} \approx 8t \text{ as } t \to \infty.$$
But ACF's actual bound is $|V| \le 4t$ — a factor of 2 better than this naive derivation. The factor of 2 comes from ACF's use of the *exact* $Z(t)$ value and a careful treatment of low-order terms, not from a bigger Crossing Lemma constant. **Lesson: the published $4t, 3.57t, 3.03t, 2.8118t$ constants reflect *combined* improvements (better Crossing Lemma, better edge counts, better target inequalities), not just constant improvements in any one ingredient.**

**The naive arithmetic does not reproduce $2.8118t$, $3.03t$, or $3.57t$ on its own.** Each step in the chain combines the Crossing Lemma with extra structural input:

- Ackerman 2019: the key is $|E| \le 6n - 12$ for graphs drawn with $\le 4$ crossings per edge. Subtracting these "cheap" edges sharpens the cube in $|E|$ to a tighter shape; the resulting $n \le 3.03 t$ is not a one-line Crossing-Lemma substitution.
- Cranston 2025: the $2.8118t$ extracts from BK's *piecewise* bounds in the intermediate density regime $4 \le |E|/|V| \le 7$, which is exactly where a $t$-critical graph sits at small $t$.

This is methodologically important for R2: **a new Crossing-Lemma constant $c$ alone does not move the MCE bound by the naive factor $1/(8c)$ — one must re-run the finer Cranston-style analysis with the new constant plugged in. A 5% improvement on $c$ does *not* automatically yield a 5% improvement on $|V| \le 2.8118 t$.**

### Numerical sanity check at $t = 25$

With Cranston's $2.8118$:
- $|V| \le 2.8118 \cdot 25 = 70.295$, so $|V| \le 70$ for $t = 25$.
- Combined with Cranston's separate exclusion $1.228r \le |V| \le 1.768r$ (so $|V| \notin [30.7, 44.2]$ at $t = 25$, i.e. $|V| \le 30$ or $45 \le |V| \le 70$) and other Cranston propositions, the residual reduces to the three pairs $(25, 48), (26, 50), (26, 51)$ (plan §Background, plan §"Cranston Theorem 2").

So the chain $4t \to 3.57t \to 3.03t \to 2.8118t$ translates into a numerical squeeze that has reduced the $t = 25, 26$ open question from "many orders" to "three exact orders". To push to $2.5t$ would give $|V| \le 62.5 < 70$, which **does not by itself close $(25, 48), (26, 50), (26, 51)$** because all three orders are already below $70$. The next constant improvement only closes new $t$ values, not new orders within those $t$.

**Operational consequence.** A targeted R2 improvement is publishable as a Crossing-Lemma paper in its own right, but the next "Albertson push" (closing $t = 25$ or $t = 26$) does **not** come from R2 — it comes from R1 (computational), R5 (Fox–Pach–Suk chromatic-index refinement), or a structural attack at the three Cranston-residual orders. R2 buys $t = 27, 28, \ldots$ unconditionally, one or two at a time.

---

## 3. Min-degree-aware Crossing Lemma (R2c)

**Setup.** A $t$-critical graph has $\delta \ge t - 1$ (Dirac), so for large $t$ it is *very* dense per vertex. The Crossing Lemma is proven by a random vertex-deletion argument that retains each vertex with probability $p = 4|V|/|E|$ in the ACNS proof, and the density gain is paid against the Euler bound $|E| \le 3|V| - 6$. The Crossing Lemma is *not* min-degree-aware: it uses only $|E|$ and $|V|$.

### Survey of min-degree-aware versions

I am aware of the following directions in the literature; some are sharp under specific
side conditions, none has been packaged as a "min-degree-aware Crossing Lemma" with a
single clean constant analogous to Ackerman 2019.

1. **Pach–Spencer–Tóth (2000), "Crossing numbers of random graphs"**: gives lower bounds on $\operatorname{cr}(G)$ in terms of the bisection width $b(G)$, where the bisection width itself is sensitive to spectral / degree parameters. For $d$-regular graphs with second eigenvalue gap, $b(G) = \Omega(|V|)$ and $\operatorname{cr}(G) = \Omega(|V|^2)$, which is much stronger than the cube of $|E|/|V|^{2/3}$ once $|E|$ is comparable to $|V|^{1+\epsilon}$. [Needs PDF read for the cleanest statement adapted to bounded-degree case; the paper is Pach–Spencer–Tóth, *On the structure of graphs with crossing numbers* / *J. Graph Theory* 2000.]
2. **Pach–Tóth (1997), "Graphs drawn with few crossings per edge"**: implicit min-degree dependence via the $|E| \le k$-planar bound $|E| \le c_k \cdot |V|$ for $c_k$ growing in $k$. Combined with degree-aware density, one can sharpen the Crossing Lemma when the graph is far from being $k$-planar for small $k$. [Needs PDF read.]
3. **Bollobás-type / random regular graph baseline**: for the random $d$-regular graph $G_{n, d}$ with $d$ growing, $\operatorname{cr}(G_{n, d}) = \Theta(n^2 d^2)$ (heuristic; needs reference). The Crossing Lemma gives $\Omega(n d^3)$, which is weaker for $d \ll n$. This is evidence that the Crossing Lemma is *not* tight for random regular graphs and there is meaningful slack to exploit.
4. **Spectral / expander bound (Bezrukov–Chimani–Vinokur style)**: $\operatorname{cr}(G) \ge \frac{1}{8} \beta(G)^2 - |V|^2 / 16$ where $\beta(G)$ is the bisection width. For $t$-critical graphs that are spectral expanders (a side hypothesis to verify), $\beta = \Omega(t \cdot |V|)$ and the bound becomes $\operatorname{cr}(G) = \Omega(t^2 |V|^2)$, which dominates the naive Crossing-Lemma estimate by a factor of $t$ in the regime $|V| = O(t)$. **This is the most promising single lever I see for R2c.**

### Why min-degree should help — heuristic

The ACNS random sampling argument retains each vertex with probability $p$. If $G$ has min-degree $\delta_0$, the surviving graph $G_p$ has expected min-degree $\sim p \delta_0$ (more precisely, the expected number of neighbours of a surviving vertex in $G_p$ is $p \delta_0$). For $p \delta_0$ large, $G_p$ remains *dense*, and the Euler bound used at step (2) of the ACNS proof is far from tight for dense $G_p$. Replacing the Euler bound with an Ackerman or BK bound for the surviving subgraph gives a better expectation; the gain compounds with $\delta_0$.

Concretely: if $\delta_0 \ge \alpha \cdot |E|/|V|$ for a constant $\alpha \le 1$ (which is *automatic* by the handshake lemma in the degree-regular regime), then the BK bound applies to $G_p$ whenever $p \cdot |E|/|V| \ge 6.77$, i.e. $p \ge 6.77 |V|/|E|$. The optimal $p$ in the original argument is $p = 4|V|/|E|$, so the threshold for applying BK to $G_p$ is *higher* than the standard optimum — but for *min-degree $\delta_0$* graphs, one can afford to sample at a higher $p$ because the surviving graph is still dense, and the gain on the constant compensates. Working this out carefully should give an explicit $c^\star(\delta_0)$ improvement.

This is the same observation that drives the Pach–Spencer–Tóth bisection-width bound (random regular graphs have $\operatorname{cr} \gg$ Crossing-Lemma lower bound) but cast for the *deterministic* min-degree class.

### Conjecture (mine, not in the literature as stated)

**R2c Conjecture.** There exists a function $c^\star(\delta_0) > c$ such that for every graph $G$ with $\delta(G) \ge \delta_0$ and $|E(G)| \ge 6.77 |V(G)|$,
$$\operatorname{cr}(G) \;\ge\; c^\star(\delta_0) \cdot \frac{|E(G)|^3}{|V(G)|^2},$$
with $c^\star(\delta_0)/c \to \infty$ as $\delta_0 \to \infty$. In particular, for $\delta_0 = t - 1$ and the family of $t$-critical graphs at $|V| = O(t)$, $c^\star(t - 1) \ge \kappa$ for an absolute constant $\kappa > 1/27.48$.

**Honesty.** This conjecture is *my own framing*; I cannot point to a published theorem in this exact form. Closest published cousin is the random-regular crossing-number folklore in Pach–Spencer–Tóth and follow-ups, but those bounds are stated for specific random or quasi-random graphs, not for the family of all min-degree-$\delta_0$ graphs. The R2c conjecture is *plausible* (the random-deletion proof of the Crossing Lemma has slack proportional to $\delta_0 / \alpha$ in the retained subgraph), but a clean constant would require a careful re-execution of the ACNS argument with min-degree retention rather than uniform vertex sampling. **This is a 6–12 month research target, not a known result.**

**Quantitative target.** If R2c yields $c^\star(t - 1) = 1/20$ (a $\sim 30\%$ improvement) for $\delta_0 = t - 1$, plugging into the Cranston pipeline (with the necessary re-execution of the piecewise BK bounds in the min-degree-aware form) should push $2.8118t \to \approx 2.4t$, which would close $t = 27, 28$ (one or two new values), but **not** $t = 25, 26$ (those still require closing the residual triples, where the bound is already $\le 70$).

---

## 4. R3.5 — $k$-planar / Schaefer direction

### What is known about $\chi$ for $k$-planar graphs

A graph $G$ is $k$-planar if it admits a drawing with $\le k$ crossings per edge. The Pach–Tóth chain gives edge-density bounds:

| Class | Edge bound | $\chi$ bound (via $\chi \le 1 + \max \delta$ on degeneracy) |
|-------|-----------|--------|
| Planar (0-planar) | $|E| \le 3|V| - 6$ | $\chi \le 4$ (Four Colour) |
| 1-planar | $|E| \le 4|V| - 8$ | $\chi \le 7$ (Borodin 1984) |
| 2-planar | $|E| \le 5|V| - 10$ | $\chi \le 9$ |
| 3-planar | $|E| \le 5.5|V| - 11$ | $\chi \le 11$ |
| 4-planar | $|E| \le 6|V| - 12$ (Ackerman 2019) | $\chi \le 12$ via degeneracy |
| $k$-planar (Pach–Tóth) | $|E| \le 4.108 \sqrt{k} \cdot |V|$ | $\chi \le O(\sqrt{k})$ |

### Bounded crossing number $\Rightarrow$ chromatic bound

**Schaefer's theorem.** If $\operatorname{cr}(G) \le k$, then $\chi(G) = O(k^{1/4})$.

This is the "Schaefer weak Albertson" — Albertson would give $\chi(G) \le \chi(K_t)$ such that $\operatorname{cr}(K_t) \ge k$, i.e. $\chi(G) = O(k^{1/4})$. So Schaefer's bound has the right *exponent* but is off by a constant factor. To upgrade Schaefer to Albertson at finite $k$, one needs to nail the leading constant.

**Concrete restricted statement.** *Albertson restricted to $k$-planar graphs.* The constraint $\operatorname{cr}(G) \le \binom{|E|}{2}$ is much weaker than $k$-planarity ($\le k$ crossings per *edge*), so this is genuinely a different restriction than "$\operatorname{cr}(G) \le k$".

Is Albertson on $k$-planar graphs open?

- **$k = 0$ (planar)**: trivial. $\chi \le 4$, $\operatorname{cr}(K_4) = 0$. Done.
- **$k = 1$ (1-planar)**: $\chi \le 7$ (Borodin), $\operatorname{cr}(K_7) = 9$. Need to show every 1-planar $G$ with $\chi(G) = 7$ has $\operatorname{cr}(G) \ge 9$. This appears **open** in the literature but is at the boundary of "small enough to be doable by hand"; I cannot find a definitive reference confirming it is settled. Schaefer's CRC 2018 book is the most likely place this is discussed; **needs PDF read of Schaefer Ch. 6**.
- **$k = 2$ (2-planar)**: $\chi \le 9$. $\operatorname{cr}(K_9) = 36$. Conjecturally open.
- **$k = 3, 4$**: similar, open.
- **General $k$-planar**: open, and the upper bound on $\chi$ scales as $O(\sqrt{k})$ via Pach–Tóth's edge density, so for large $k$ Albertson would need $\operatorname{cr}(G) \ge \operatorname{cr}(K_{\Theta(\sqrt{k})}) \sim k^2$. Compare to the trivial $\operatorname{cr}(G) \le \binom{k|V|/2}{2} \cdot k$ for $k$-planar graphs; the comparison is not obvious. **This is a clean R3.5 target: prove Albertson for 1-planar and 2-planar graphs unconditionally.**

### Schaefer's $O(k^{1/4})$ result, derived

The derivation is short enough to record. Given $G$ with $\operatorname{cr}(G) \le k$:

1. If $\chi(G) = t$, the $t$-critical subgraph $G' \subseteq G$ satisfies $|E(G')| \ge (t-1)|V(G')|/2$ (Dirac).
2. Applying the Crossing Lemma to $G'$: $\operatorname{cr}(G') \ge c |E(G')|^3 / |V(G')|^2 \ge c (t-1)^3 |V(G')| / 8$.
3. Since $\operatorname{cr}(G') \le \operatorname{cr}(G) \le k$: $|V(G')| \le 8k / (c (t-1)^3)$.
4. Also $|V(G')| \ge t$ (a $t$-critical graph has $\ge t$ vertices).
5. So $t \le 8k / (c (t-1)^3)$, hence $(t-1)^4 \le 8k/c$, hence $t \le 1 + (8k/c)^{1/4}$.

With $c = 1/27.48$, the constant is $(8 \cdot 27.48)^{1/4} = 219.84^{1/4} \approx 3.85$. So $\chi(G) \le 3.85 \cdot k^{1/4} + O(1)$ for any graph with $\operatorname{cr}(G) \le k$. Compare to Albertson, which predicts $\operatorname{cr}(K_t) \le k$, i.e. $Z(t) \approx t^4/64 \le k$, i.e. $\chi(G) \le t \le (64 k)^{1/4} \approx 2.83 k^{1/4}$. So the *constant gap* between Schaefer and Albertson is $3.85 / 2.83 \approx 1.36$, which is exactly what R2 / R2c is meant to close. **A min-degree-aware Crossing-Lemma constant $c^\star$ with $(8 / c^\star)^{1/4} \le 2.83$ — i.e. $c^\star \ge 1/8 \cdot (1/2.83)^{-4} = 8/(2.83)^4 \approx 1/8.0$ — would close Schaefer to Albertson asymptotically.** That is a very aggressive target ($1/8$ vs current $1/27.48$) and almost certainly not achievable; but it tells us the *target rate* for the constant.

### Schaefer's catalogue (CRC 2018)

The book *Crossing Numbers of Graphs* (Marcus Schaefer, CRC, 2018) lists ten or so crossing-number variants:
- $\operatorname{cr}(G)$ (standard / topological / Jordan curve);
- $\operatorname{cr}_\square(G)$ (rectilinear, straight-line drawings);
- $\operatorname{pair-cr}(G)$ (count pairs of edges that cross, not crossings);
- $\operatorname{odd-cr}(G)$ (count pairs that cross an odd number of times — Hanani–Tutte);
- $\operatorname{cr}_k$ (only counts crossings in pairs that cross at most $k$ times);
- $k$-planar crossing number, $k$-quasi-planar, etc.

Albertson is *trivially false* for some variants (the rectilinear analogue, because $\operatorname{cr}_\square(K_n) > \operatorname{cr}(K_n)$), but the *odd crossing number* satisfies $\operatorname{odd-cr}(G) \le \operatorname{cr}(G)$ trivially and is *strictly smaller in general* (Pelsmajer–Schaefer–Štefankovič). An "odd-crossing Albertson" $\operatorname{odd-cr}(G) \ge \operatorname{odd-cr}(K_t)$ is a possibly easier statement; **I do not know whether it is open or known.** This is worth a literature pass.

### How $k$-planar interacts with Albertson's MCE bound

A different angle: *is an MCE for Albertson at $t \ge 25$ necessarily $k$-planar for some small $k$?* The Cranston MCE bound $|V| \le 2.8118 t$ and the criticality bound $|E| \ge (t-1)|V|/2$ give

$$|E|/|V| \ge (t-1)/2 \in [12, 12.5] \quad \text{at } t = 25, 26.$$

A 1-planar graph satisfies $|E|/|V| \le 4 - 8/|V| < 4$, so an MCE at $t = 25, 26$ is **not** 1-planar. Similarly not 2-planar ($\le 5$) or 3-planar ($\le 5.5$). It *could* be $\Theta(t^2)$-planar (since $|E|/|V| = O(t)$ and the Pach–Tóth bound gives $|E|/|V| = O(\sqrt{k})$ for $k$-planar). Concretely, $|E|/|V| = 12 \Rightarrow k \ge 8.5$ via Pach–Tóth's $|E| \le 4.108\sqrt{k}|V|$; so an MCE at $t = 25$ must have *some edge crossed at least 9 times* in any drawing. This is a (very weak) structural constraint on a counterexample, and feeds plan §C7.

### Concrete R3.5 deliverable: Albertson for 1-planar graphs

If 1-planar Albertson is open, the deliverable is: combine Borodin's $\chi \le 7$ with the edge bound $|E| \le 4|V| - 8$ and show that any $1$-planar 7-chromatic graph has $\ge 9$ crossings. Sketch: a 7-chromatic graph has $\delta \ge 6$, so $|E| \ge 3|V|$, so $|V| \le \frac{|E| + 8}{4}$ and $|V| \le 2(|E|)/6 \le |E|/3$. Combine with the Crossing Lemma at the appropriate density threshold. The arithmetic is small enough that the conjecture for 1-planar might be a one-month problem, not a research programme — but it requires confirming the open / closed status first.

---

## 5. Random / probabilistic angles

The Crossing Lemma is proven by a random argument: sample each vertex independently with probability $p$, apply the Euler bound to the surviving graph, take expectations, set $p$ to optimize. Improvements (Pach–Tóth, PRTT, Ackerman, BK) sharpen the constants by:

- Replacing Euler with the $k$-planar density bound $|E| \le c_k |V|$, then iterating.
- (BK 2024) Characterizing local configurations in dense 2- / 3-planar graphs and forbidding them — a *structural* refinement, not a new probabilistic technique.

### What modern probabilistic combinatorics could add

1. **Entropy compression** (Moser–Tardos / Dujmović). The standard ACNS argument uses union bound on expectations. An entropy-compression refinement of the random vertex deletion could in principle save a factor on the constant by encoding "bad" outcomes more efficiently. **Speculative**: I do not see a clean route, but the technique has surprising payoffs in extremal combinatorics (e.g., acyclic chromatic index, non-repetitive colorings).
2. **Container method** (Saxton–Thomason, Balogh–Morris–Samotij). The container method counts independent sets / sparse structures; for crossing numbers, the relevant "independent" set is a planar (or $k$-planar) subgraph. A container-style analysis of the family of $k$-planar subgraphs of a dense graph could yield a sharper density-vs-crossing trade. **Speculative; no existing application I know of.**
3. **Dependent random choice** (Fox–Sudakov style). Already used implicitly in Fox–Pach–Suk's chromatic-index argument. A direct DRC bound for "many edge-disjoint dense subgraphs" inside a $t$-critical graph could feed into a refined Crossing Lemma. **Plausible**; this is the direction closest to current Fox–Pach–Suk machinery.
4. **Regularity** (Szemerédi). Crossing-number bounds via regularity tend to be order-of-magnitude correct but with bad constants. Probably not the right tool for *constant* improvement.
5. **Spectral / expander** approaches via Pach–Spencer–Tóth bisection-width bounds (see §3 above). This is the most concrete probabilistic-combinatorics lever I see for R2c.

### Specific probabilistic levers I would try first

**Lever A — sharpen step (4) of ACNS via correlation.** Crossings in the original drawing of $G$ are *not* independent: two crossings that share an edge are positively correlated under vertex sampling (both die when that edge dies). A FKG / Janson-style correlation inequality applied to the random variable $\operatorname{cr}(G_p)$ could give $\mathbb{E}[\operatorname{cr}(G_p)] \le \beta(p) \cdot p^4 \operatorname{cr}(G)$ for some $\beta(p) < 1$, sharpening the constant by $1/\beta$. This is the cleanest "modern probabilistic" idea I can think of that has not been tried. Risk: $\beta$ might be very close to 1 for sparse correlations; needs a careful crossing-multigraph variance calculation.

**Lever B — entropy compression on the Ackerman iteration.** Ackerman 2019 iterates a $\le k$-crossings-per-edge analysis. Each iteration loses a small constant. An entropy-compression formulation should be able to lump the iterations into a single combinatorial argument, possibly saving the cumulative loss. This is closer to a *re-proof* than a new bound, but a clean entropy-compression Crossing Lemma is itself a publishable contribution.

**Lever C — random regular crossing-number folklore.** For random $d$-regular $G_{n, d}$ with $d = \Theta(\log n)$ (say), it is known (folklore? Pach–Spencer–Tóth?) that $\operatorname{cr}(G_{n, d}) = \Theta(n^2 d^2)$ with high probability, which exceeds the Crossing-Lemma cube $\Theta(n d^3)$ by a factor of $n / d$. If one could *extract* the constant in this bound and make it deterministic for $d$-regular graphs with sufficient expansion (spectral gap), R2c would follow. This is the route closest to a concrete 12-month result.

**Lever D — large-deviations bisection-width.** Bezrukov–Chimani–Vinokur (and earlier Leighton) give $\operatorname{cr}(G) \ge \Omega(b(G)^2 - |V|^2)$ where $b(G)$ is the bisection width. For $t$-critical graphs with expander spectrum, $b(G) = \Omega(t |V|)$ and $\operatorname{cr}(G) = \Omega(t^2 |V|^2 - |V|^2)$. At $|V| = O(t)$, this is $\Omega(t^4)$, matching $\operatorname{cr}(K_t) \sim t^4/64$ at the right order. The constant on the front is the unknown; this is what to chase.

### Realistic 12-month yield from probabilistic tools

A *new* Crossing-Lemma constant $c < 1/27.48$ via probabilistic combinatorics is plausible-but-not-guaranteed; the increments in the published chain have been small (PT $\to$ PRTT $\to$ Ackerman $\to$ BK each gained a few percent). A min-degree-aware constant $c^\star(\delta_0)$ via spectral / expander bounds is the most promising single sub-route. **My commitment target**: aim for $2.8118t \to 2.5t$ for $t$-critical graphs (a min-degree-aware refinement), with $2.8118t \to 2.7t$ as a generic Crossing-Lemma improvement (without min-degree assumption). Both would close $t = 27$ or $t = 28$ unconditionally; neither closes $t = 25, 26$ on its own.

**Calibration against the published cadence.** The Albertson-via-Crossing-Lemma chain has produced one constant improvement per published paper, roughly one paper every 5–10 years (ACF 2009, BT 2009, Ackerman 2019, Cranston 2025). Each paper closes 1–2 new values of $t$. A 12-month research effort that produces *one* new constant in this chain — pushing $2.8118 t$ down by $5$–$10\%$ — sits exactly at the published cadence and is the realistic ambition. The R2c min-degree-aware refinement, if it works, would be the *first* paper in the chain to use a structurally different idea (min-degree retention in random sampling, rather than $k$-planar density iteration); this is a real differentiator and would be publishable independent of its numerical payoff.

**Negative outcomes are also informative.** If R2c fails — i.e., if the empirical $\rho(G)$ measurement in Role 3 D6 shows that $t$-critical graphs sit on the worst-case Crossing-Lemma bound — that is *itself* a publishable observation, because it would mean the Crossing Lemma is tight for the family that Albertson cares about, and Albertson would have to be attacked via *non-Crossing-Lemma* tools (Fox–Pach–Suk R5, structural R3, computational R1). Such a negative result would significantly clarify the project's priorities.

---

## 6. Dependencies

### Ask of Role 7 (chromatic index)

The Fox–Pach–Suk Lemma 2.3 chromatic-index bound (their "$9/16$" leading constant; arXiv:2510.05893 §2) drives the asymptotic $(1.64 - o(1))k$ vertex bound. If Role 7 can push $9/16$ down — even by a few percent — the resulting bound on $|V|/k$ for weak-immersion existence climbs from $1.64$ toward $1.768$ (the Cranston upper-window cutoff). This is the **R5** lever in plan v3, but R2c interacts with it: a min-degree-aware Crossing Lemma combined with a sharper chromatic-index bound could *jointly* push Albertson by 2–3 values of $t$ rather than 1, **assuming the second-stage Fox–Pach–Suk crossing recovery scales — which is not free** (plan O3).

**Specific ask**: a clean statement of how Lemma 2.3 of arXiv:2510.05893 depends on the min-degree of the multigraph being edge-coloured. If min-degree input tightens the chromatic-index bound (which it does in Vizing-type analyses), the R2c $\to$ R5 hand-off is well-defined.

### Ask of Role 3 (exact crossing-number computation)

R2 / R2c progress is testable empirically: for randomly generated $t$-critical graphs at $t = 10, \ldots, 18$ (the range where exact crossing-number computation is feasible via Buchheim–Chimani ILP / Chimani–Mutzel SAT), measure the empirical ratio
$$\rho(G) := \operatorname{cr}(G) \cdot |V|^2 / |E|^3.$$
If $\rho(G)$ is robustly larger than $1/27.48$ for $t$-critical graphs with $\delta = t - 1$, the R2c conjecture has empirical legs and the publishable target is "prove $\rho \ge 1/c^\star(\delta_0)$ rigorously". If $\rho$ hugs $1/27.48$, R2c is dead. Plan §C4 already specifies a script for this; I would like Role 3 to run it as a priority, and to *stratify by min-degree* (R2c hypothesis) and by *spectral gap* (R2c Lever D). 30-day ask.

### Ask of Role 1 (project leader)

**Question**: is a Crossing-Lemma improvement from $c = 1/27.48$ to $c = 1/25$ (a $\sim 10\%$ improvement) — yielding Albertson for $t \le 27$ or $t \le 28$ unconditionally — itself a publishable result? My read of the field:

- Yes, in *Combinatorica* / *J. Combin. Theory Ser. B* — the constant chain is itself the subject of papers (BK 2024 is a full paper for a 5% improvement).
- A Crossing-Lemma constant improvement is publishable even if it does *not* close any new Albertson $t$.
- An Albertson push from $t \le 24$ to $t \le 27$ via Crossing Lemma is publishable on its own (Cranston 2025 is a recent example for a single-$t$ push).

Confirmation requested before committing to a 12-month R2 sub-target.

---

## 7. First 30-day deliverables

| # | Deliverable | Verification |
|---|-------------|--------------|
| D1 | Resolve the $6.77|V|$ vs $6.95|V|$ threshold discrepancy in BK 2024. Read arXiv:2409.01733 PDF and update the plan's threshold value if needed. | A one-paragraph note in `work/08_probabilistic/bk_threshold.md` citing the BK theorem statement verbatim. |
| D2 | Reproduce the $2.8118t$ derivation in Cranston 2025 from the piecewise BK bounds. Confirm whether the dominant tight constraint is the $5m - 203/9(n - 2)$ branch or the cube branch. | A short note tracing each constant from BK $\to$ Cranston, with the Albertson-MCE arithmetic step-by-step. Output: identify *which* line in BK is the bottleneck that R2 must improve to push $2.8118 \to 2.5$. |
| D3 | Map the open / closed status of Albertson on $k$-planar graphs for $k = 1, 2, 3$. Check Schaefer CRC 2018 Ch. 6, Pach–Tóth 1997, and the Borodin 1984 7-colour theorem chain. | Output: a table marking each $(k, t)$ pair as `proven`, `open`, or `vacuous`. If $k = 1$ Albertson is open, draft an attempt. |
| D4 | Pin down the min-degree-aware Pach–Spencer–Tóth bisection-width bound. Specifically: for $t$-critical graphs with $\delta \ge t - 1$, what does the spectral / bisection-width bound give for $\operatorname{cr}(G)$ at $|V| = O(t)$? | A clean inequality $\operatorname{cr}(G) \ge f(t, |V|)$ derived from PST + criticality, with a comparison to $\operatorname{cr}(K_t)$ at $|V| = 2.8118t, 2.5t, 2t$. |
| D5 | Draft the **R2c conjecture** in a publishable form: min-degree-aware Crossing Lemma with explicit $c^\star(\delta_0)$, target $\delta_0 = t - 1$, and a clear separation between the proven part (PST / spectral) and the conjectural part (constant improvement). | A 5-page draft, with the conjecture stated precisely, a literature review of all min-degree-aware Crossing Lemma variants I can find, and a 12-month attack plan. |
| D6 | Coordinate with Role 3 on the empirical $\rho(G)$ measurement (above). Define the stratification, the random-generation scheme, and the output table format. | A small Python harness + spec, written by Role 3, reviewed by me. |
| D7 | Pin down 1-planar Albertson status from Schaefer CRC 2018 Ch. 6 and Borodin's 7-chromatic result. If open, attempt the small-case proof. | Either a one-paragraph "settled in [reference]" or a draft proof sketch in `work/08_probabilistic/one_planar_albertson.md`. |

---

---

## 8. Cross-cutting risk register for R2 / R3.5

- **R-1 (likelihood: high).** A Crossing-Lemma constant improvement from $1/27.48$ to $1/25$ exists but does not close $t = 25, 26$. **Mitigation**: scope the deliverable as a Crossing-Lemma paper, not an Albertson paper; coordinate with Role 1 on whether this counts as a project milestone.
- **R-2 (likelihood: medium).** The min-degree-aware refinement (R2c) cannot be cleanly stated as a single constant $c^\star(\delta_0)$; instead, one gets a parameter family (e.g., one constant per density regime). **Mitigation**: target a clean *2-parameter* statement $c^\star(\delta_0, \alpha)$ that recovers BK at $\delta_0 = \alpha$ and improves smoothly above it.
- **R-3 (likelihood: medium).** The 1-planar Albertson statement (R3.5 D3) turns out to already be known — i.e., it is a small-case theorem hidden in Schaefer CRC 2018 or in some Hungarian-school survey I have not read. **Mitigation**: D3 starts with a literature pass; if it is already settled, pivot to 2-planar Albertson (smaller chance of being settled).
- **R-4 (likelihood: low but non-trivial).** The Pach–Spencer–Tóth bisection-width bound used in R2c Lever D was *for random graphs*, and the deterministic extraction fails because $t$-critical graphs need not be spectral expanders (in fact $K_t$ itself is the worst spectral expander). **Mitigation**: state Lever D conditionally on a spectral gap hypothesis; explore whether *all* $t$-critical graphs at the Cranston-residual orders satisfy the hypothesis (computational check via R1c machinery, lifted from Role 1).
- **R-5 (likelihood: low).** The Bungener–Kaufmann argument is specific to 2-planar and 3-planar dense graphs and does not extend to higher-$k$-planar (where it would need a much more delicate combinatorial characterization). A "BK for 4-planar" might not be possible in 12 months. **Mitigation**: R2c is not blocked on extending BK; it can compose with BK as-is.

## 9. Summary table — where R2 / R3.5 sits in the project

| Sub-route | 12-month realistic outcome | Closes new Albertson $t$? | Publishable on its own? |
|-----------|----------------------------|---------------------------|--------------------------|
| R2a: density-refined Crossing Lemma for $t$-critical | $c = 1/27.48 \to 1/25$ | $t = 27$ (maybe 28) | yes — Crossing Lemma paper |
| R2b: Ackerman $6|V| - 12$ refinement for critical | $6|V| - 12 \to (6 - \epsilon)|V|$ | maybe $t = 27$ | yes — Ackerman-style paper |
| R2c: min-degree-aware Crossing Lemma | $c^\star(t-1) = 1/20$ for $\delta_0 = t - 1$ | $t = 27, 28$, possibly 29 | yes — structurally novel |
| R3.5: 1-planar Albertson | settle for $k = 1$, attempt $k = 2$ | none (small-$t$ cases) | yes if open; small contribution if proved |
| R3.5: $k$-planar Albertson, general | identify a generic argument | none directly | yes — Schaefer-CRC adjacent |

The honest project-level assessment: **R2 / R3.5 will not close $t = 25, 26$**, and the leadership should plan accordingly. R2c is the highest-impact deliverable I can commit to; R3.5 is a "publishable adjacency" deliverable that complements the main project.

## Appendix — uncertainties flagged

- **BK threshold $\alpha$.** Plan v3 says $\alpha = 6.95$; arXiv abstract says $m > 6.77n$. **Needs PDF read.** This is a 0.3 difference, which matters at the boundary regime $4 \le |E|/|V| \le 7$ where $t$-critical graphs at $t \approx 10$ sit.
- **Pach–Tóth 1997 exact $(c, \alpha)$.** Plan v3 implies $c \approx 1/33.75$ via the chain; the abstract of the Combinatorica paper is paywalled. **Needs PDF read** to confirm.
- **PRTT 2006 exact $(c, \alpha)$.** Similar. Plan v3 quotes $c \approx 1/31.1$. Needs PDF read.
- **Schaefer's $O(k^{1/4})$ chromatic bound for crossing-$k$ graphs.** The exponent is well-known folklore; the constant is not. **Needs PDF read** of Schaefer CRC 2018 to confirm the constant matters for finite $k$.
- **1-planar Albertson status.** I could not confirm open / closed status from arXiv abstracts; D3 above covers this.
- **The R2c conjecture.** Stated above as mine. If a literature search uncovers a stronger published version, the conjecture should be retired or cited; **needs literature pass** before public commitment.
- **Random regular crossing-number folklore** (Lever C). I claimed $\operatorname{cr}(G_{n, d}) = \Theta(n^2 d^2)$ for random $d$-regular graphs at $d = \Theta(\log n)$. This is at the edge of what I remember; the actual reference may give a different exponent (e.g., $\Theta(n^2 d^2 / \log d)$ or with an extra polylog), and the implied R2c constant would change accordingly. **Needs PDF read** of Pach–Spencer–Tóth, *On the crossing number of random graphs*, *J. Graph Theory* circa 2000.
- **The 1.36 factor between Schaefer's $O(k^{1/4})$ and Albertson's prediction.** Derived above as $3.85 / 2.83 \approx 1.36$. This used $\operatorname{cr}(K_t) \approx t^4/64$ asymptotically, but the actual $\operatorname{cr}(K_t)$ for finite $t$ is *lower* than $Z(t)$ by an unknown ratio (the de Klerk / Balogh asymptotic ratios apply only at infinity). So the finite gap may be slightly different; for the asymptotic R3.5 deliverable the factor is correct, but for any finite-$t$ Schaefer-to-Albertson statement, this needs to be re-derived with care.
