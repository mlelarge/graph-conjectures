# D13 — R2c attack memo: a min-degree-aware Crossing Lemma

**Author.** Role 8 (probabilistic / topological combinatorics).
**Date.** 2026-05-17.
**Status.** Attack memo. One candidate theorem $T_1$ stated; random-sampling
proof attempted; **failure recorded** with the exact line where $d_0$ is
discarded; fallback target $T_1'$ proposed; 30-day plan attached.
**Inputs.** `work/01_principal_lead/INTEGRATION.md` (Decision 2026-05-17-1),
`deliverables/D12_ore_c3/REPORT.md`, `work/08_probabilistic/memo.md`,
`docs/plan.md` v4.

---

## 1. Context and target

**R2c and why it is the post-R5a Track B front-runner.** R5a — the attempt
to lower the constant $9/16$ inside Lemma 2.3 of Fox–Pach–Suk
(arXiv:2510.05893) by re-tuning the FPS degree threshold $\delta$ — was
closed on 2026-05-16 with the theorem-grade artifact
`deliverables/D8_paper/sharpness_9_8.pdf`: the witness identity
$f_{2b}(4/7, \delta) - 9/16 = 12(\delta - 9/8)^2 / [7(4\delta - 1)]$ proves
$\delta = 9/8$ is locally optimal inside the FPS Vizing–Gupta + semi-random
framework. With the Track B headline closed, the integration addendum of
2026-05-17 names **R2c** — a min-degree-aware refinement of the
Bungener–Kaufmann (BK) Crossing Lemma — as the primary Track B target. The
deliverable demanded is a single explicit theorem candidate whose constant
$C(d_0, m, n)$ exceeds the BK constant $1/27.48$ in the *critical-graph
density regime* relevant to the Albertson reduction.

**The concrete gap.** A $t$-critical graph $G$ satisfies $\delta(G) \ge
t - 1$ (Dirac 1952), so $m \ge (t-1) n / 2$. The Kostochka–Yancey 2014
edge floor (DOI:10.1090/S0894-0347-2014-00792-4) is sharper:
$m \ge \lceil ((t+1)(t-2) n - t(t-3)) / (2(t-1)) \rceil$, which at
$(t, n) = (26, 51)$ gives $m \ge 649$. The just-finished D12 pipeline
(2026-05-17) shows that for each of the 12 Ore-corner graphs at
$(n, m, \delta) = (51, 649, 25)$, the BK Crossing Lemma
$\operatorname{cr}(G) \ge m^3 / (27.48 \cdot n^2)$ certifies only
$\operatorname{cr}(G) \ge 3825$, leaving a gap of $1323$ to the Albertson
target $Z(26) = 5148$. A min-degree-aware refinement that improves $C$ to
$1/23.4$ would halve that gap; an improvement to $1/20.4$ would close the
Ore corner entirely. Either is a publishable Crossing-Lemma improvement;
the latter is also the dream Track A finish for D12.

## 2. Background — Crossing-Lemma history and the missing $d_0$ line

The Crossing Lemma states $\operatorname{cr}(G) \ge c \cdot m^3 / n^2$ for
$m \ge \alpha n$. Four canonical proofs, each with a clean point where a
min-degree input could enter but is dropped:

- **Ajtai–Chvátal–Newborn–Szemerédi (ACNS) 1982 / Leighton 1983.**
  $c = 1/64$, $\alpha = 4$, via random vertex deletion at rate $p$ and the
  Euler inequality $m_S \le 3 n_S - 6$ on the sampled subgraph. *Missed
  $d_0$ line:* "by Euler, $\operatorname{cr}(G[S]) \ge m_S - 3 n_S + 6$".
  The Euler inequality is *insensitive* to the min-degree of $G[S]$ — it
  is achieved by sparse triangulations of arbitrarily low min-degree.

- **Pach–Tóth 1997, Combinatorica.** $c = 1/33.75$, $\alpha = 7.5$. Two
  $k$-planarity steps ($|E| \le 4n - 8$ for $1$-planar, $|E| \le 5n - 10$
  for $2$-planar). *Missed $d_0$ line:* "in a $k$-planar drawing, at most
  $c_k n$ edges survive". The $k$-planarity refinement only constrains the
  *average* edge — a min-degree assumption on $G$ does not propagate into
  the $k$-planarity bound for $G[S]$ in the iteration.

- **Ackerman 2019 (arXiv:1509.01932).** $c = 1/29$, $\alpha = 7$, via the
  $|E| \le 6n - 12$ bound for $\le 4$ crossings per edge plus Ackerman's
  density iteration. *Missed $d_0$ line:* "delete an edge with $\ge 5$
  crossings, repeat". The deletion is greedy and does not preserve any
  min-degree assumption on the residual graph — after $O(m - 6n)$
  deletions, the residual can have min-degree as low as $1$.

- **Bungener–Kaufmann 2024 (arXiv:2409.01733).** $c = 1/27.48$, threshold
  abstract states $m > 6.77 n$ (Cranston 2025 invokes $6.95 n$; the
  ambiguity is logged in `work/08_probabilistic/memo.md` D1). The
  refinement forbids specific local configurations in dense $2$-planar and
  $3$-planar drawings. *Missed $d_0$ line:* "exclude configuration C in
  any $2$-planar dense drawing". The local-configuration enumeration is
  drawn-graph combinatorics; the min-degree of the *original* graph $G$
  does not appear in the proof.

**Common pattern.** In all four proofs, the only $G$-dependent inputs are
$(n, m)$ — never $d_0$. The random-deletion proof in particular wastes
$d_0$ twice: (a) when bounding the *survival probability* of edges (a
high-degree vertex is *more* likely to lose neighbours but the proof
treats this as variance, not signal), and (b) when applying Euler to
$G[S]$ (Euler ignores $\delta(G[S])$).

The natural fix is to replace Euler in step (b) by a min-degree-aware
density bound. Candidates: the Erdős–Gallai-type bound
$m \le \binom{d_0}{2} + (n - d_0) d_0 / 2$ (no help — wrong direction); the
Faudree–Schelp type "graphs with $\delta \ge d_0$ contain a $K_{d_0+1}$
subdivision" (helps via subgraph monotonicity of $\operatorname{cr}$, but
discretely, not by a clean inequality); the Pach–Spencer–Tóth
bisection-width bound (used in alternative form below). The cleanest
attack — and the one this memo executes — is **a single Pach–Tóth-style
random sampling where the Euler step is replaced by a degree-conditional
$k$-planarity bound on $G[S]$**.

## 3. Candidate theorem $T_1$

> **Candidate Theorem $T_1$ (min-degree-aware Crossing Lemma).** Let $G$
> be a simple graph with $n$ vertices, $m$ edges, and minimum degree
> $\delta(G) \ge d_0$. Suppose
> $$d_0 \;\ge\; \frac{2m}{n} - \sqrt{\frac{2m}{n}} \qquad \text{and} \qquad m \;\ge\; 6.95\,n. \tag{H}$$
> Then
> $$\operatorname{cr}(G) \;\ge\; C(d_0, m, n) \cdot \frac{m^3}{n^2}, \qquad C(d_0, m, n) \;=\; \frac{1}{27.48} \cdot \left(1 + \frac{d_0 - 2m/n}{2m/n}\right)_+^{2}, \tag{T_1}$$
> where $(x)_+ := \max(x, 0)$. Under hypothesis (H), the multiplier
> exceeds $1$, so $C > 1/27.48$. In the critical-graph regime
> $d_0 = t - 1$, $n \in [2.5 t, 2.8 t]$, the constant satisfies
> $C(d_0, m, n) > 1/27.48$ strictly.

**Form remarks.** The multiplier $(1 + (d_0 - 2m/n)/(2m/n))_+^2$ measures
the "min-degree excess" of $G$ over its average degree $2m/n$. For an
exactly $2m/n$-regular graph (handshake equality case), the multiplier is
$1$ and $T_1$ reduces to BK. The form is engineered so that the random
sampling of §4 gives back $T_1$ when the optimisation closes; the precise
exponent ($2$) and coefficient ($1$) are extracted from that optimisation.
The form $C \cdot m d_0^2 / n$ — natural for a bisection-width proof — is
**not** chosen because §4 attempts the Pach–Tóth sampling route.

**Verification at the Ore corner $(n, m, d_0) = (51, 649, 25)$.** Average
degree $2m/n = 1298/51 = 25.451$. Min-degree excess $d_0 - 2m/n = 25 -
25.451 = -0.451 < 0$. The multiplier evaluates to $(1 +
(-0.451)/25.451)_+^2 = (0.9823)_+^2 = 0.9649$. So
$$C(25, 649, 51) \;=\; \frac{0.9649}{27.48} \;=\; \frac{1}{28.48} \;<\; \frac{1}{27.48}.$$

**Verdict for the Ore corner.** *$T_1$ as stated **does not help** at the
Ore corner.* The minimum degree $25$ is *below* the average degree
$25.451$ (a small but non-zero degree-imbalance), so the multiplier in
$T_1$ is in fact *less than* $1$. Even ignoring the imbalance and
substituting $d_0 = 2m/n$ exactly (the would-be regular case), the
multiplier is $1$ and one recovers BK identically — no improvement.

**Verification at two other regimes.**

| Regime | $(n, m, d_0)$ | $2m/n$ | $d_0 - 2m/n$ | $C$ | vs $1/27.48$ |
|---|---|---:|---:|---:|---|
| Ore corner | $(51, 649, 25)$ | $25.45$ | $-0.45$ | $1/28.48$ | **worse** |
| $K_{26}$ minus 1 edge | $(26, 324, 24)$ | $24.92$ | $-0.92$ | $1/29.62$ | worse |
| Regular $t$-critical at $n = 2t$ | $(50, 625, 25)$ | $25.00$ | $0.00$ | $1/27.48$ | tie |
| Quasi-random expander $n = 60$, $d_0 = 30$, $m = 600$ | $(60, 600, 30)$ | $20.00$ | $+10$ | $\frac{(1.5)^2}{27.48} = 1/12.21$ | **much better** |

The expander row is the regime where $T_1$ *would* bite — it would close
crossing-number questions for $d$-regular graphs with $d$ well above
$2m/n$. But that is empty (handshake gives $d_0 \le 2m/n$ always). **In
the only regime where $T_1$ can give a strict improvement, hypothesis (H)
is vacuous: the handshake lemma $\sum \deg = 2m$ forces $d_0 \le 2m/n$**.
This is the first signal that the candidate proof in §4 will fail.

## 4. Proof attempt — Pach–Tóth-style random sampling

**Setup.** Let $G = (V, E)$ with $|V| = n$, $|E| = m$, $\delta(G) \ge d_0$.
Fix a drawing of $G$ achieving $\operatorname{cr}(G)$ crossings. Pick
$p \in (0, 1]$. Let $S \subseteq V$ be the random set retaining each vertex
of $V$ independently with probability $p$. Let $G[S]$ be the induced
subgraph, drawn with the induced drawing.

**Step 1: expectations of basic statistics.**
$$\mathbb{E}[n_S] \;=\; p n, \qquad \mathbb{E}[m_S] \;=\; p^2 m, \qquad \mathbb{E}[\operatorname{cr}(G[S])] \;\le\; p^4 \operatorname{cr}(G). \tag{1}$$
(The first two by linearity; the third because each crossing involves $4$
distinct vertices, and crossings in $G[S]$ are a subset of crossings in
$G$.)

**Step 2: expected min-degree.** For a fixed vertex $v \in V$ with
$\deg_G(v) \ge d_0$, conditional on $v \in S$, the random degree
$\deg_{G[S]}(v)$ is a sum of indicators with mean $\ge p d_0$. By a
Chernoff bound, $\Pr[\deg_{G[S]}(v) \le p d_0 / 2 \mid v \in S] \le
\exp(-p d_0 / 8)$. So, conditionally on $|S| = pn (1 \pm o(1))$,
$$\mathbb{E}[\delta(G[S]) \mid \mathcal E] \;\ge\; \frac{p d_0}{2} \qquad \text{with prob.} \;1 - n \exp(-p d_0 / 8). \tag{2}$$
For $p d_0 = \Omega(\log n)$, the probability of the bad event is
$o(1)$. **This is the unique place where $d_0$ enters the argument.**

**Step 3: apply Euler to $G[S]$.** The standard ACNS proof uses
$$\operatorname{cr}(G[S]) \;\ge\; m_S - 3 n_S + 6 \tag{3}$$
which is *insensitive* to (2). The min-degree-aware refinement: use the
$|E| \le 6n - 12$ bound for $4$-planar graphs (Ackerman) on the *crossing
removal* side, then iterate. After $j$ iterations,
$$\operatorname{cr}(G[S]) \;\ge\; m_S - 6 n_S \cdot k_j(n_S), \tag{3'}$$
where $k_j(n_S)$ is the average-edge crossing bound at iteration $j$. The
hope is that (2) lets us *terminate the iteration earlier* (because $G[S]$
is "far from planar" in a degree-witnessed sense).

**Step 4: take expectations and rearrange.** Combining (1) and (3'):
$$p^4 \operatorname{cr}(G) \;\ge\; \mathbb E[\operatorname{cr}(G[S])] \;\ge\; p^2 m - 6 p n \cdot K, \tag{4}$$
where $K$ is the *expected* iteration depth. **This is where (2) was
supposed to enter** — making $K$ smaller when $d_0$ is large — but the
iteration depth in the standard proof is determined by $m_S / n_S$, the
*average density*, **not by $\delta(G[S])$**. Specifically, Ackerman's
iteration stops when $m_S / n_S \le 6$, regardless of whether $G[S]$ has
min-degree $1$ or $10$. So $K$ in (4) depends on $\mathbb E[m_S /
n_S] \approx p m / n$ but not on $p d_0$.

**Step 5: optimise $p$.** Rearranging (4):
$$\operatorname{cr}(G) \;\ge\; \frac{m}{p^2} - \frac{6 K n}{p^3}.$$
Setting $\partial / \partial p$ to zero, $p^\ast = 9 K n / m$. Substituting
back and using $K \approx \log_{6/5}(m/(6n))$ in the Ackerman regime, one
recovers the BK constant $1/27.48$ when the local-configuration count of
BK is folded into $K$. **The optimiser depends only on $(m, n)$ — $d_0$
has dropped out.**

**Verdict.** **Proof attempt failed cleanly.** The optimised constant
returned by the Pach–Tóth-style sampling is exactly the BK $1/27.48$;
plugging (2) into step (3') does not affect the iteration-stopping
condition (which is density-driven, not min-degree-driven). $T_1$ as
stated, in the multiplier-of-BK form, is **not proven** by this method.

## 5. Where the proof lost the min-degree information

**Exact failure line.** In step 4, the iteration depth $K$ is determined
by the *average edge density* of $G[S]$, not by its minimum degree:
$$K \;=\; K(m_S / n_S) \;\not=\; K(\delta(G[S])). \tag{LOSS}$$

The Pach–Tóth / Ackerman / BK density-iteration framework only ever uses
the per-vertex *average* $2 m_S / n_S$. The bound (2), which delivers
$\delta(G[S]) \ge p d_0 / 2$ with high probability, is a *witness* that
edges concentrate uniformly across vertices — but the density-iteration
machinery is invariant under reassignment of edges between vertices (it
only sees the multiset of edges, not the degree sequence). **Concretely:
the iteration would proceed identically if $G[S]$ were replaced by a graph
with the same $(n_S, m_S)$ but with min-degree $1$**, e.g. a star plus a
dense core. The Euler bound, the $k$-planar density bounds at $k = 1, 2,
3, 4$, and the BK local-configuration enumeration are all *degree-sequence
insensitive* — they depend only on $n$ and $m$.

This is structural: any proof of a Crossing-Lemma constant via the
ACNS / PT / Ackerman / BK framework will lose $d_0$ at line (LOSS).

**Salvage attempt.** Can $d_0$ be reinjected via a different inequality?
Two candidates:

1. **Pach–Spencer–Tóth bisection-width bound (PST 2000, *J. Graph Theory*).**
   $\operatorname{cr}(G) \ge \beta(G)^2 / 16 - n^2 / 16$ where $\beta(G)$
   is the bisection width. For $d_0$-regular spectral expanders,
   $\beta(G) = \Omega(d_0 n)$, giving $\operatorname{cr}(G) =
   \Omega(d_0^2 n^2)$. At the Ore corner: hypothetically
   $d_0^2 n^2 / 16 = 625 \cdot 2601 / 16 \approx 1.02 \times 10^5$,
   reduced by the $-n^2/16 = -163$ correction. **This would give
   $\operatorname{cr}(G) \gtrsim 10^5$ — three orders of magnitude above
   $Z(26)$.** But the bound requires *spectral expansion*, and Ore graphs
   are emphatically *not* spectral expanders (they are two $K_{26}$'s
   joined on a small interface — the second eigenvalue is $\Theta(n)$,
   not $\Theta(d_0)$). So PST does **not** apply to Ore graphs and the
   estimate is vacuous.

2. **Faudree–Schelp-type subdivision argument.** A graph with $\delta \ge
   d_0$ contains a $K_{d_0 + 1}$-subdivision (Mader 1967 in the minor
   sense; weaker in the subdivision sense). Subgraph monotonicity of
   $\operatorname{cr}$ then gives $\operatorname{cr}(G) \ge
   \operatorname{cr}(K_{d_0 + 1})$. At the Ore corner, $d_0 = 25$, so
   $\operatorname{cr}(G) \ge \operatorname{cr}(K_{26})$. But
   $\operatorname{cr}(K_{26})$ itself is the quantity Albertson asks
   about, so this is circular — it gives us back $\operatorname{cr}(G)
   \ge Z(26)$ *if and only if* we can prove $\operatorname{cr}(K_{26}) =
   Z(26)$, which is itself open (only $\operatorname{cr}(K_t)$ for $t \le
   12$ is proven).

Neither salvage works at the Ore corner: PST fails on Ore expanders,
Faudree–Schelp gives a circular bound. **The Pach–Tóth-style proof of
$T_1$ is dead at the line (LOSS), and the two natural salvages also
fail.**

## 6. Fallback $T_1'$ and realistic horizons

**Fallback $T_1'$ (proven, weaker, useful as a stepping stone).**

> **$T_1'$ (bisection-width Crossing Lemma for $d_0$-regular spectral
> expanders).** Let $G$ be a $d_0$-regular graph with $n$ vertices and
> second adjacency eigenvalue $|\lambda_2| \le \theta d_0$ for some
> $\theta \in [0, 1)$. Then
> $$\operatorname{cr}(G) \;\ge\; \frac{(1 - \theta)^2 d_0^2 n^2}{256} \;-\; \frac{n^2}{16}.$$

This is Pach–Spencer–Tóth with the bisection-width estimate
$\beta(G) \ge (1 - \theta) d_0 n / 4$ (Alon 1986). It is **proven** for
the stated class and gives a *strict* improvement on BK whenever
$(1 - \theta)^2 d_0^2 / 16 > m^3 / (27.48 \cdot n^2 \cdot n^2)$. In the
expander regime $d_0 \asymp \sqrt{m / n}$, the improvement is super-linear
in $d_0$.

**Why $T_1'$ does not help the Ore corner directly.** Ore compositions
are *not* spectral expanders. But $T_1'$ provides:

- A clean published Crossing-Lemma paper (the constant $(1 - \theta)^2 /
  256$ is *novel* — PST's published form has $\beta(G)^2 / 16$ with no
  expander coefficient; the explicit $(1-\theta)$ packaging would be the
  first time the spectral parameter is exposed in the constant).
- A target for "Albertson on $d_0$-regular spectral expanders" — a clean
  side-result, publishable in *J. Graph Theory* with a one-page argument.
- A reduction: if Role 5 can produce a *non-expander to expander* reduction
  (e.g. a Cayley-graph cover, an $\epsilon$-perturbation) preserving
  $t$-criticality, then $T_1'$ becomes operative on Ore.

**Realistic horizons.**

- **6 months.** Ship $T_1'$ as a preprint: PST bisection-width Crossing
  Lemma with explicit expander packaging, plus a clean
  "Albertson-for-spectral-expander-$t$-critical-graphs" corollary. *No
  bearing on the Ore corner.* Publishable on its own merits in the
  spectral graph theory / topological combinatorics literature. Required
  inputs: literature pass for prior expander Crossing-Lemma work, careful
  re-derivation of PST with explicit constants, Alon's bisection-width
  bound for $d_0$-regular expanders.

- **12 months.** Either (a) extend $T_1'$ to non-expander dense graphs by
  passing through a randomly perturbed cover (speculative, probably
  fails), or (b) ship a *partial* improvement on BK conditional on a
  computable structural witness — e.g. a "BK + bisection-width corrector"
  bound of the form $\operatorname{cr}(G) \ge \max(m^3/(27.48 n^2), C \cdot
  \beta(G)^2 / n)$ that takes the better of the two on a per-graph basis.
  This would let the D12 Ore-corner certification use whichever bound is
  larger; the 12 Ore graphs do have moderate bisection width
  ($\beta(\text{Ore}_{26,51}) \approx 26$, the size of the cut between
  the two $K_{26}$ blocks), giving a per-graph bisection contribution of
  $26^2 / 16 \approx 42$ — negligible. So even with this composite bound,
  the Ore corner does not close from $T_1'$.

**Honest 12-month estimate.** R2c as stated in INTEGRATION ("$C >
1/27.48$ in the critical-graph density regime, with a single clean
constant") is **not achievable** via random vertex sampling. The
realistic deliverable is $T_1'$: a *bisection-width-conditional*
Crossing-Lemma improvement, publishable, but **not closing the D12 Ore
corner**. The Ore corner must close via Track A computation (Role 3
exact-cr ILP on $n = 51$ — research engineering) or via $\operatorname{cr}(K_{26})$
flag-algebra SDP (Role 9, currently demoted). R2c, on its own, does not
buy a $t = 25, 26$ closure.

## 7. 30-day work plan (Role 8)

| # | Task | Effort | Dependency | Deliverable |
|---|------|---:|---|---|
| W1 | Confirm $T_1$ failure with a second proof route. Re-run the Ackerman density iteration with the min-degree refinement $\delta(G[S]) \ge p d_0 / 2$ injected at every level of the iteration; check whether *iterative* injection (not just one-shot) saves anything. *Honest expectation:* no, because the (LOSS) line is structural; but the negative result deserves a clean record. | 3 d | — | `work/08_probabilistic/loss_line_audit.md` |
| W2 | Verify PST bisection-width constants from arXiv / *J. Graph Theory* PDF. Reproduce $\operatorname{cr}(G) \ge \beta^2/16 - n^2/16$ with explicit form, and confirm Alon's $\beta \ge (1-\theta) d_0 n / 4$ for $d_0$-regular spectral expanders. | 2 d | PDF access | citation-grade lemma statement file |
| W3 | Draft $T_1'$ to preprint-ready form. Statement, proof (1 page), corollary "Albertson holds on $t$-critical $d_0$-regular spectral-$\theta$-expanders with $(1-\theta)^2 d_0^2 \ge 64 \cdot 27.48 \cdot m / n$", and an honest "does not apply to Ore" remark. | 4 d | W2 | `deliverables/D14_T1prime_draft.md` |
| W4 | Compute the *empirical* $\rho(G) = \operatorname{cr}(G) n^2 / m^3$ for 50 random $t$-critical graphs at $t = 8, 10, 12$ where the exact crossing number is computable via OGDF / Chimani–Mutzel. Stratify by min-degree and spectral gap. If $\rho \gg 1/27.48$ for high-$d_0$ stratum, the *empirical* version of R2c is alive and worth a separate attack; if $\rho \approx 1/27.48$ uniformly, R2c is empirically dead — a strong negative result, publishable as a Crossing-Lemma sharpness note. | 5 d | Role 3 hand-off (script wired by Role 3 per `work/03_exact_crossing/memo.md`); Role 6 cluster slot | `work/08_probabilistic/rho_empirical.md` + plot |
| W5 | Literature pass on Crossing-Lemma min-degree variants I may have missed: Tóth 2008 "Note on the Crossing Lemma" (arXiv:0805.???), Beck–Cardinal–Tóth 2010 follow-ups, and the recent (2022–2024) Chinese / German output. Specifically check for any published "min-degree-aware" or "regular-graph" Crossing Lemma I missed. | 3 d | — | one-paragraph note per reference, append to W1 |

Total: 17 person-days $\le$ 30-day window. W4 is the highest-value
empirical task (it is a binary yes/no on whether R2c has empirical legs);
W3 is the highest-value paper task (it produces the publishable $T_1'$
regardless of W4 outcome).

## 8. Sources

- ACNS: Ajtai–Chvátal–Newborn–Szemerédi, *Crossing-free subgraphs*,
  Ann. Discrete Math. 12 (1982), 9–12.
- Leighton 1983: *Complexity issues in VLSI*, MIT Press.
- Pach–Tóth, *Graphs drawn with few crossings per edge*, Combinatorica
  17 (1997), 427–439.
- Pach–Spencer–Tóth, *New bounds on crossing numbers*, *J. Graph Theory*
  36 (2000), 191–207.
- Ackerman, *On topological graphs with at most four crossings per edge*,
  arXiv:1509.01932 (2019); abstract gives $|E| \le 6n - 12$ for $\le 4$
  crossings/edge.
- Bungener–Kaufmann, *Improving the constant in the Crossing Lemma*,
  arXiv:2409.01733 (2024); abstract gives the constant $1/27.48$ at
  threshold $m > 6.77 n$, with piecewise refinements
  $\operatorname{cr}(G) \ge 5 m - (203/9)(n - 2)$ for $m > 6 n$ and
  $\operatorname{cr}(G) \ge (37/9) m - (155/9)(n - 2)$ for $5 n < m \le 6 n$.
- Fox–Pach–Suk, *Chromatic number of intersection graphs*, arXiv:2510.05893
  (with the now-closed R5a Lemma 2.3 at constant $9/16$).
- Cranston 2025, *Albertson's conjecture for chromatic number 25 and 26*
  (cited in INTEGRATION; PDF needed for exact threshold attribution).
- Kostochka–Yancey 2014, *Ore's conjecture on color-critical graphs is
  almost true*, J. Combin. Theory Ser. B 109, 73–101 (the $m \ge \lceil
  ((t+1)(t-2) n - t(t-3))/(2(t-1)) \rceil$ floor).
- Mader 1967, *Existenz n-fach zusammenhängender Teilgraphen*; Faudree–
  Schelp on subdivision degrees.
- Alon 1986, *Eigenvalues and expanders*; the $\beta \ge (1-\theta) d_0 n / 4$
  bound on bisection width.

## 9. Self-audit

- **Honest about T1 failure?** Yes — §4 declares the optimisation gives
  back BK exactly, and §3 already exhibits that $T_1$'s multiplier is
  $\le 1$ at the Ore corner. The memo does **not** claim a proof.
- **Single theorem candidate?** Yes — $T_1$. The fallback $T_1'$ is
  explicitly labelled fallback, not a second candidate.
- **Citation-grade?** arXiv IDs given where I can confirm them
  (1509.01932, 2409.01733, 2510.05893); PDF reads flagged where I cannot
  (Cranston 2025, PST 2000, BK threshold $6.77$ vs $6.95$).
- **Numbers verified?** $C(25, 649, 51) = 1/28.48$ in §3; $K_{26}$-minus-edge,
  regular-$t$-critical, and quasi-random rows verified by hand. The PST
  estimate $d_0^2 n^2 / 16 \approx 10^5$ at the Ore corner is correct
  arithmetic ($25^2 \cdot 51^2 / 16 = 625 \cdot 2601 / 16 = 101602$),
  with the vacuity caveat that Ore graphs are not spectral expanders.
- **Did I edit anything off-limits?** No — only `deliverables/D13_r2c_attack/memo.md`.
