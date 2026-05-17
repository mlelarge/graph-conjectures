# Memo R3 / R1c / C3 — Exact crossing-number machinery for Albertson at $t = 25, 26$

Role: exact crossing-number algorithms (ILP/SAT/planarization).
Owner: R3.
Author: this memo, 2026-05-16.
References: `docs/plan.md` (v3), `docs/review.md`.
Scope: own R1c (heuristic+exact pipeline) and C3 (certified lower bounds on
$\operatorname{cr}(G)$ at the three Cranston residual orders).

The single sentence to internalise: **only a certified lower bound on
$\operatorname{cr}(G)$ can discard $G$.** A heuristic upper bound, no matter
how large, says nothing about the truth. This memo is structured around what
the team can and cannot deliver under that constraint.

---

## 1. What "exact crossing number" actually means at $n = 48$

The crossing number $\operatorname{cr}(G)$ is the minimum number of edge
crossings over all drawings of $G$ in the plane. Even *deciding* whether
$\operatorname{cr}(G) \le k$ is NP-complete (Garey–Johnson 1983), and the
problem is APX-hard in general; the only polynomial-time tractable subcase of
interest here is "$G$ minus one edge planar" (the *edge insertion* problem,
which is itself NP-hard already for $|F| = 1$ inserted edges if non-planarity
is unbounded — see Chimani 2011, arXiv:1104.5039).

### State of the art for exact computation (best available knowledge)

The honest picture, with caveats:

- **$K_n$ exact values.** $\operatorname{cr}(K_n)$ is known exactly for
  $n \le 12$: the cases $n \le 10$ are classical (Guy / Saaty / others with
  multiple confirmations); $n = 11, 12$ were settled by Pan–Richter 2007
  (*"The crossing number of $K_{11}$ is 100"*, J. Graph Theory). For
  $n \ge 13$ the equality $\operatorname{cr}(K_n) = Z(n)$ is **open**; the
  value is *conjectured* to be $Z(n)$ (the Hill/Zarankiewicz expression). This
  is the heart of Obstruction O2 in plan v3.
- **$K_{m,n}$ exact values.** Known for $\min(m,n) \le 6$ (Kleitman) and a
  small extension by SDP work (de Klerk et al., arXiv:math/0404142, gives an
  *asymptotic* improvement, not new exact finite values).
- **General graphs.** The Chimani et al. (Osnabrück) and OGDF implementations
  of the Buchheim–Chimani branch-and-cut ILP routinely handle small sparse
  graphs (a few dozen vertices and $|E| \le 2|V|$) within seconds to minutes.
  As $|E|/|V|$ grows past 3 or 4, the LP relaxation degrades sharply.
- **What I do not know and cannot fabricate.** TODO: locate a published
  experiment running the Buchheim–Chimani ILP or the Chimani–Mutzel SAT on a
  graph with $n \ge 40$ and $|E| \ge 4n$. The Chimani group's papers
  (arXiv:1104.5039, 1509.07952, 2108.11443) describe planarization
  heuristics and approximations, not exact dense-graph timings. The exact ILP
  benchmark tables I recall from the literature go up to roughly the Rome /
  AT&T graph drawing test suite, which is *sparse* — typical $|E| < 2|V|$.
  I have not found a published exact crossing-number computation on a dense
  graph at $n \sim 50$. **If one exists I owe the team a citation; until
  then, assume it does not, and proceed pessimistically.**

In short: the largest dense graph for which a *certified* exact crossing
number appears in print is, to my knowledge, $K_{12}$ at $n = 12, |E| = 66$;
that already took specialised handwork-augmented argument (Pan–Richter).
There is no published precedent for an exact certificate at the order we
need ($n = 48, |E| \ge 576$, edge density $\approx 12$).

---

## 2. The exact MILP for crossing number

Two families of formulations dominate the literature.

### 2a. Buchheim–Chimani edge-pair ILP (the canonical formulation)

Variables, for a simple graph $G = (V, E)$ with $|V| = n$, $|E| = m$:

- A binary crossing variable $x_{ef} \in \{0, 1\}$ for each *unordered*
  non-adjacent edge pair $\{e, f\}$, with $x_{ef} = 1$ iff $e$ and $f$ cross
  in the chosen drawing. Number of variables: roughly $\binom{m}{2}$ minus
  the number of edge pairs sharing a vertex; on the order of
  $m^2/2 - O(m \cdot \Delta)$.

Constraints:

- **Planarity (the hard part).** For each subset $S \subseteq E$ of edges
  inducing a non-planar subgraph, the sum of crossing-variables among
  edge-pairs in $S$ must be at least $\operatorname{cr}(S) \ge 1$. This is
  enforced via *Kuratowski cuts*: for each $K_5$ or $K_{3,3}$ subdivision
  found in the drawing-graph induced by the current LP solution, add the
  constraint $\sum_{\{e,f\} \in \text{Kuratowski edge pairs}} x_{ef} \ge 1$.
  The Kuratowski subdivision is found by a planarity tester (Boyer–Myrvold)
  applied to the "auxiliary graph" where each crossing has been split.
- **Realizability constraints.** Not every $\{0,1\}$-assignment to $x$
  corresponds to an actual planar drawing; one needs *RAC-style*
  realizability cuts (three-edge cycles of crossings cannot be
  simultaneously satisfied without rotation conflicts). These are added
  on-demand as the branch-and-cut tree explores fractional solutions.
- **Symmetry-breaking.** Automorphism orbits on $E$ are computed by
  `nauty`/`bliss` and fed in as orbit-based branching priorities.

Variable count for our target: $n = 48, m \approx 576$, so
$\binom{576}{2} \approx 1.66 \times 10^5$ crossing variables. After removing
adjacent-edge pairs ($48 \times \binom{24}{2} = 13\,248$ adjacent pairs per
vertex doubled and de-duped, roughly $1.3 \times 10^4$), one still has
$\sim 1.5 \times 10^5$ binary variables.

Constraint count: Kuratowski cuts are added lazily; the *total* number ever
added is bounded by the number of $K_5$ / $K_{3,3}$ subdivisions explored,
which is exponential in the worst case. The LP at any one node has roughly
$O(m \cdot n^{O(1)})$ active constraints, but the *cumulative* cut pool can
grow without bound.

Plain English assessment for $n = 48, |E| \ge 576$: **this formulation is
beyond the LP-relaxation comfort zone by 2–3 orders of magnitude.** Existing
benchmark runs are on the Rome graphs ($n \le 100$ but $|E| \le 1.5 n$); ours
is the opposite regime — small $n$ but $|E| = 12 n$. The Kuratowski cut pool
will be the bottleneck because dense graphs have astronomically many
Kuratowski subdivisions to find and prune.

### 2b. Chimani–Mutzel SAT / MaxSAT reformulation

Variables: for each pair $(e, k)$ of an edge $e \in E$ and a "crossing slot"
$k \in \{0, 1, \ldots, K\}$ (where $K$ is an upper bound on the number of
crossings), boolean variables encoding the crossing pattern. Plus boolean
variables encoding the combinatorial embedding (rotation system) of the
planarised graph. Constraints encode (i) planarity of the planarised
"crossing-as-vertex" graph and (ii) consistency of the rotation system.

Variable count: $O(m K)$ for crossing-slot variables. With $K = Z(25) = 4356$
and $m = 576$ this is $\sim 2.5 \times 10^6$ booleans — possibly tractable for
modern CDCL solvers (Kissat, CaDiCaL) but the encoding size will dominate I/O.

Constraint count: a planarity check on the planarised graph contributes
$O(n + K)$ clauses per check; the full encoding has $O(m^2 K + n^2)$ clauses
in the standard pre-compilation. For our regime, $\sim 10^9$ clauses; this
will not fit in RAM on a typical 256 GB cluster node, and incremental SAT
will be slower than the ILP's LP relaxation on the same instance.

**MaxSAT lower-bound mode.** A useful subcase: instead of computing the
exact crossing number, certify $\operatorname{cr}(G) \ge L$ by proving that
no drawing with $L - 1$ crossings exists. This is a *single* SAT call (UNSAT)
rather than an optimisation. With $L$ as a tight target (e.g., $L = Z(25) =
4356$), the encoding is bounded by $L$, not by the full $\binom{m}{2}$, so
the size is $O(m L)$ booleans, $O(m^2 + n L)$ clauses. For $L = 4356$, $m =
576$, that is $\sim 2.5 \times 10^6$ booleans and $\sim 2.5 \times 10^6$
clauses — *plausibly* tractable, but a single UNSAT proof at this size on a
dense graph would itself be a publishable solver result. I would not bet on
it returning within a week of wall-clock per instance.

### 2c. Concrete estimate for the target

| Quantity | Value at $n=48, m = 576$ |
|---|---|
| Edge-pair ILP binary variables | $\sim 1.5 \times 10^5$ |
| Kuratowski cuts (cumulative, worst case) | unbounded; $10^6$–$10^9$ in practice |
| LP at a node, active constraints | $10^4$–$10^5$ |
| MaxSAT bool variables ($K = Z(25)$) | $\sim 2.5 \times 10^6$ |
| MaxSAT clauses (full encoding) | $\sim 10^9$, infeasible in RAM |
| Lower-bound UNSAT call, vars | $\sim 2.5 \times 10^6$ |
| Lower-bound UNSAT call, clauses | $\sim 2.5 \times 10^6$ |

**Brutal honest verdict:** on a cluster node with 256 GB RAM and 64 cores,
the *single-instance* exact crossing-number ILP at $n = 48, m \ge 576$ is
**not expected to terminate within a week**, and possibly not within a month.
The team should plan for either (a) lower-bound certificates that fall short
of the full exact value but exceed $Z(25)$ — the *silver* certificate, see
Section 3 — or (b) structurally restricted sub-cases where the ILP relaxes.

---

## 3. C3 deliverables — three certificate levels

The conjecture's right-hand side is $\operatorname{cr}(K_t)$, which is itself
unknown for $t \ge 13$ (see Section 5 for what we can do). For now, assume
the team has a finite certified lower bound $\underline{L}(t)$ on
$\operatorname{cr}(K_t)$. To discard a candidate $G$ as a counterexample, we
need to certify $\operatorname{cr}(G) \ge \underline{L}(t)$ — and the safe
operational threshold (which also proves the strong form, $\operatorname{cr}(G) \ge Z(t)$)
is the upper-bound target $Z(t)$.

### Gold: full optimal ILP solve with proof log

- **What it is.** A complete branch-and-cut tree from the Buchheim–Chimani
  ILP, terminating with a proven optimum $\operatorname{cr}(G) = c^\star$. The
  proof log is the sequence of LP relaxations and Kuratowski cuts that close
  the gap between LP bound and integer-feasible solution.
- **What it certifies.** $\operatorname{cr}(G) = c^\star$; if $c^\star \ge
  Z(t)$, the candidate is discarded.
- **Compute per graph (target $n = 48, m \ge 576$).** Not feasible with
  today's solvers and a one-week wall-clock budget. Honest estimate: weeks
  to months per instance on a 64-core node, and likely *non-termination*.

### Silver: LP-relaxation-derived bound with verified-cut certificate

- **What it is.** Run the LP relaxation at the root of the Buchheim–Chimani
  tree with a *fixed* family of Kuratowski cuts (enumerated up to some depth
  bound). The LP value is a valid lower bound on $\operatorname{cr}(G)$. The
  certificate is the dual LP solution plus the list of cuts; both can be
  re-verified by an independent LP solver, and the cuts can be re-verified
  by Boyer–Myrvold planarity testing on the corresponding planarised graphs.
- **What it certifies.** $\operatorname{cr}(G) \ge \lceil \text{LP root bound}
  \rceil$. If this exceeds $Z(t)$, the candidate is discarded with a fully
  machine-verifiable certificate (the dual solution and Kuratowski-witness
  subdivisions can be re-checked in seconds independently).
- **Compute per graph (target $n = 48, m \ge 576$).** Estimate $\sim 10$–$100$
  CPU-hours per instance for a Kuratowski cut pool of $10^4$–$10^5$ cuts.
  This is the **realistic working level** for the team. Crucially, the LP
  bound *will often be too weak* to reach $Z(t) = 4356$ for our dense
  candidates; the silver certificate is useful but does not automatically
  succeed.
- **Honest caveat.** The LP relaxation of the Buchheim–Chimani ILP for dense
  graphs at this scale has not been studied (to my knowledge) — the bound's
  *tightness ratio* (LP / IP) on dense graphs is unknown. We will discover it
  empirically and the answer may be "the LP bound is hopelessly slack".

### Bronze: heuristic-derived bound — explicitly excluded

- **What it is.** A planarization heuristic (OGDF, Chimani's `Crossing
  Minimization Suite`) returns an *upper* bound on $\operatorname{cr}(G)$ —
  the number of crossings in a heuristic drawing.
- **What it certifies.** Nothing about $\operatorname{cr}(G)$ as a lower
  bound. It can never discard a candidate. Per plan v3 F4, this is *not*
  a valid elimination, and must not be used as one.
- **What it is used for.** *Flagging* candidates: a heuristic drawing with
  $\overline{\operatorname{cr}}(G) < \underline{L}(t)$ is a suspected
  counterexample worth deep investigation (Gold/Silver-level lower bound to
  certify $\operatorname{cr}(G) < \underline{L}(t)$ via a *complementary*
  silver certificate — see Section 4 step (c)).

---

## 4. R1c pipeline

Input: a stream of graph6 candidates from Role 5 (enumeration) and Role 8
(probabilistic / random $t$-critical generation). Each candidate is a
$t$-critical graph on the appropriate Cranston order: $(t, n) \in \{(25,
48), (26, 50), (26, 51)\}$.

Output, per candidate: a triple
$(\overline{\operatorname{cr}}(G), \underline{\operatorname{cr}}(G), \text{verdict})$
where the verdict is one of `DISCARD` (silver/gold certificate proves
$\operatorname{cr}(G) \ge Z(t)$), `FLAG` (heuristic upper bound below the
finite certified $\underline{L}(t)$, demands escalation), or `OPEN`
(insufficient bound; queue for re-attack).

```
                  graph6 stream from Role 5 / Role 8
                                  |
                                  v
            +-----------------------------------------+
            | Stage 0: pre-filter                     |
            | - reject if not t-critical (Role 2)     |
            | - reject if delta < t-1                 |
            | - canonicalise via nauty (dedup)        |
            +-----------------------------------------+
                                  |
                                  v
            +-----------------------------------------+
            | Stage 1: heuristic UB                   |
            | - OGDF planarization-based draw        |
            | - Iterative crossing reduction         |
            | - 5-10 random restarts, take min       |
            | budget: ~1 CPU-min per graph           |
            | output: cr_upper(G)                     |
            +-----------------------------------------+
                                  |
                                  v
            +-----------------------------------------+
            | Stage 2: cheap LB                       |
            | - Crossing Lemma lower bound:           |
            |   |E|^3 / (27.48 |V|^2)                 |
            |   = 576^3 / (27.48 * 48^2)              |
            |   ~= 3019                               |
            | - Plus criticality refinements          |
            |   (R2c, target ~3500+)                  |
            | budget: ~1 CPU-sec per graph            |
            | output: cr_lower_easy(G)                |
            +-----------------------------------------+
                                  |
                                  v
            +-----------------------------------------+
            | Stage 3: silver LP-relaxation bound     |
            | - Buchheim-Chimani LP root with         |
            |   bounded-depth Kuratowski cut pool     |
            | - Cut depth budget: ~10^4 cuts          |
            | budget: ~10-100 CPU-hours per graph    |
            | output: cr_lower_silver(G)              |
            +-----------------------------------------+
                                  |
                                  v
            +-----------------------------------------+
            | Stage 4: decision                       |
            | if cr_lower_silver(G) >= Z(t):          |
            |     DISCARD (silver certificate)        |
            | elif cr_upper(G) < L_underline(t):      |
            |     FLAG (escalate to forensic)         |
            | else:                                   |
            |     OPEN (queue for gold attempt)       |
            +-----------------------------------------+
                                  |
                                  v
                  (loop / log / archive)
```

### Throughput estimate

- **Stage 0:** ~ $10^4$ graphs/CPU-day. Bottleneck: `nauty` canonicalisation.
- **Stage 1 (heuristic UB):** ~ $10^3$ graphs/CPU-day.
- **Stage 2 (Crossing Lemma):** ~ $10^6$ graphs/CPU-day. Trivial; arithmetic.
- **Stage 3 (silver LP-relaxation):** **~ $1$ graph/CPU-day** in the
  optimistic case ($10$ CPU-hours per graph); **~ $0.1$ graphs/CPU-day** in
  the realistic case ($100$ CPU-hours per graph). This is the binding
  constraint.
- **Stage 4 / Gold ILP:** **~ $10^{-2}$ graphs/CPU-day** at best, more
  likely *non-terminating*.

With a 256-core cluster running 24/7, the silver-tier throughput is
~ $250$ graphs/day optimistic, ~ $25$ graphs/day realistic. Whether this is
enough depends on the candidate stream from Roles 5 and 8.

### Honest pessimistic ceiling

If the candidate stream from Role 5 (structurally restricted enumeration of
$25$-critical graphs on $48$ vertices) is in the $10^4$–$10^6$ range — which
is what we should plan for under R1b's *most aggressive* structural
restrictions — the silver pipeline alone needs $40$–$4000$ cluster-days to
process. That is the order-of-magnitude budget, and assumes the silver bound
actually reaches $Z(25) = 4356$ on the candidates it processes. **If it does
not** (i.e. the LP bound saturates well below $Z(25)$), the pipeline
produces a stream of `OPEN` verdicts and discards nothing.

---

## 5. The $\operatorname{cr}(K_t)$ value problem (Obstruction O2)

This is the most insidious issue in the whole project, and the reviewer was
emphatic on the point. Quoting plan v3: "Lower bounds on $\operatorname{cr}(K_t)$
are useful for falsification, not for proving Albertson."

The conjecture is $\operatorname{cr}(G) \ge \operatorname{cr}(K_t)$. We have
two ways to use this:

1. **Prove Albertson on $G$:** show $\operatorname{cr}(G) \ge U(t)$ for an
   *upper* bound $U(t) \ge \operatorname{cr}(K_t)$. The Hill/Zarankiewicz
   value $Z(t)$ works because $\operatorname{cr}(K_t) \le Z(t)$ is a *proven*
   inequality (a specific drawing of $K_t$ achieves $Z(t)$ crossings). This
   is the only operational path the team can take to "discard $G$" in the
   pipeline above.
2. **Falsify Albertson on $G$:** show $\operatorname{cr}(G) < L(t)$ for a
   *finite, certified, proven* lower bound $L(t) \le \operatorname{cr}(K_t)$.
   This is what Section 6 (Role 9) needs to deliver.

### (a) Which finite lower bounds on $\operatorname{cr}(K_t)$ are *proven*?

Honest enumeration:

- **$t \le 12$:** $\operatorname{cr}(K_t) = Z(t)$ exactly. Pan–Richter 2007
  settles $t = 11, 12$; smaller cases classical.
- **$t \ge 13$:** the equality is open. What *is* known:
  - **Counting recurrences (folklore / Guy).** Trivial inequalities of the
    form $\operatorname{cr}(K_{t+1}) \ge \operatorname{cr}(K_t) \cdot \binom{t+1}{4} /
    \binom{t}{4} \cdot \frac{1}{c}$ for various $c$ that come from
    edge-deletion or removal-and-redraw arguments. These give
    $\operatorname{cr}(K_t) \ge \frac{\binom{t}{4}}{\binom{12}{4}} \cdot
    \operatorname{cr}(K_{12}) = \frac{\binom{t}{4}}{495} \cdot 150$. For
    $t = 25$: $\operatorname{cr}(K_{25}) \ge \binom{25}{4} \cdot 150/495
    = 12650 \cdot 150 / 495 \approx 3833$. (Sanity: $Z(25)/Z(12)
    = 4356/150 = 29.04$ and $\binom{25}{4}/\binom{12}{4} = 12650/495 = 25.56$,
    so this recurrence gives a constant $\approx 0.88 \cdot Z(25)$. This is
    the kind of bound that I expect to be *strict* — i.e. there is published
    work giving better constants — but the simple counting argument is
    proven and finite.)
  - **De Klerk et al. (arXiv:math/0404142):** $0.83 \cdot Z(n)$ in the
    $\liminf_n$ sense — **asymptotic**, not a finite certificate for
    $t = 25$ without explicit extraction from their SDP computations.
  - **Balogh–Lidický–Salazar (arXiv:1711.08958):** $0.98559895 \cdot Z(n)$
    in the $\liminf_n$ sense — **asymptotic**, same caveat.
  - **Possible finite extracts from BLS / de Klerk SDP ancillary files.**
    Their flag-algebra SDPs yield, for any specific $t$, a finite lower bound
    by running the SDP with that fixed $t$. To my knowledge no one has
    published the extracted finite numbers for $t = 25, 26$. Extracting them
    is exactly Role 9's job.

So the *best published finite* lower bound on $\operatorname{cr}(K_{25})$ is
something like $\binom{25}{4} \cdot 150/495 \approx 3833$ from the simple
counting argument (and refinements thereof in the small-$t$ literature push
this up by single-digit percentage points). This is below $Z(25) = 4356$ by
~12%, and below the asymptotic BLS extrapolation by ~10%.

### (b) What the R1c pipeline does given only such finite bounds

The pipeline discards $G$ when $\underline{\operatorname{cr}}(G) \ge Z(25) =
4356$, which proves $\operatorname{cr}(G) \ge Z(25) \ge \operatorname{cr}(K_{25})$,
i.e. it proves *strong-form Albertson* on $G$ — which is *strictly stronger*
than Albertson on $G$. The strong form implies Albertson, so this discard is
sound.

For *falsification*, the pipeline flags $G$ when $\overline{\operatorname{cr}}(G) <
\underline{L}(25)$ for the best finite certified lower bound. With $\underline{L}(25) =
3833$ (counting argument), any candidate with a heuristic drawing below 3833
crossings is a serious flag. With Role 9 providing $\underline{L}(25) \approx
4290$ (an extracted finite BLS bound, if Role 9 delivers), the falsification
threshold tightens substantially — the difference between "any $G$ with
$\overline{\operatorname{cr}}(G) < 3833$ is suspect" and "any $G$ with
$\overline{\operatorname{cr}}(G) < 4290$ is suspect" is large in practice.

### (c) When can the team legitimately use $Z(25) = 4356$ as a threshold?

**Only as an upper bound target for proof, not as a lower bound on
$\operatorname{cr}(K_{25})$.** Specifically:

- Discarding $G$ when $\underline{\operatorname{cr}}(G) \ge Z(25)$:
  **legitimate**, because this proves the strong form.
- Falsifying Albertson on $G$ when $\overline{\operatorname{cr}}(G) < Z(25)$:
  **illegitimate**, because $\operatorname{cr}(K_{25})$ might be strictly less
  than $Z(25)$.
- Using $Z(25)$ as if it equalled $\operatorname{cr}(K_{25})$: **illegitimate
  for falsification**, but the team has not proven (and is not about to
  prove) the Hill/Zarankiewicz value for $K_{25}$.

I flag this honestly because plan v2 collapsed the distinction and the v3
revision is correct but reads as legalistic — it is not. It is the single
most important constraint on what the pipeline can claim.

---

## 6. Dependency on Role 9 (SDP)

What I need from Role 9 by month 3:

- **A certified finite lower bound $\underline{L}(25)$ on
  $\operatorname{cr}(K_{25})$**, extracted from a flag-algebra SDP (in the BLS
  or de Klerk lineage) and presented with a numerically certified dual
  solution.
- **Likewise $\underline{L}(26)$ for $\operatorname{cr}(K_{26})$.**
- **Both as machine-checkable certificates.** Specifically: the SDP dual
  solution plus a high-precision verification that the certified value is a
  lower bound. (See e.g. the rational-arithmetic SDP-rounding techniques in
  the flag-algebra literature, Petr et al.)

The realistic target Role 9 should aim at, based on the BLS asymptotic
constant $0.98559895$ and a credible extrapolation to finite $t = 25$, is
$\underline{L}(25) \in [4150, 4290]$, with the lower end being a comfortable
conservative number and the upper end being the optimistic extraction. Both
are below $Z(25) = 4356$, so neither *closes* the gap that defines the
strong form.

**If Role 9 cannot deliver:**

- The pipeline still functions in *strong-form* mode: it can discard $G$
  whenever a silver/gold certificate gives $\underline{\operatorname{cr}}(G)
  \ge Z(25)$. This proves the strong form for $G$, which implies Albertson
  for $G$.
- The pipeline *cannot* falsify Albertson — only the strong form. A
  candidate $G$ with $\overline{\operatorname{cr}}(G) < Z(25)$ would be a
  *strong-form* counterexample (interesting but weaker than what plan v3
  considers a real counterexample) and would have to be re-cast as
  "candidate Albertson counterexample, contingent on the team eventually
  proving $\operatorname{cr}(K_{25}) > \overline{\operatorname{cr}}(G)$
  finitely". This is a soft outcome.

A reasonable fallback: in absence of a Role 9 deliverable, the team can use
the counting-argument lower bound $\underline{L}_{\text{cnt}}(25) \approx
3833$ as a fallback finite certified bound. This is much weaker than the
BLS-derived extraction would be, but it is *proven* and finite, and it lets
the pipeline run with a real (if conservative) falsification threshold.

---

## 7. Failure modes — owner per mode

| # | Failure | Owner | Mitigation |
|---|---------|-------|-----------|
| FM1 | ILP solver bug (CPLEX/Gurobi miscount crossings; LP relaxation produces invalid dual) | R3 | Cross-check every silver certificate with a *second* solver (HiGHS) and re-verify all Kuratowski cuts via Boyer–Myrvold independently |
| FM2 | Numerical errors in LP relaxation (floating-point dual gives invalid bound) | R3 | All silver certificates re-verified in exact rational arithmetic via `flint`/`SoPlex`-exact before claiming the bound |
| FM3 | Isomorphism collisions (same graph processed twice as if different) | R5 (enumeration) + R3 | All candidates canonicalised via `nauty` at Stage 0 and at Stage 4 (before archival); hash collisions checked weekly |
| FM4 | OGDF heuristic produces drawing with self-intersecting edges (invalid drawing → invalid upper bound) | R3 | Validate every OGDF output by re-counting crossings in the rendered drawing independently in Python via shapely / a planarity-check on the planarised graph |
| FM5 | Kuratowski cut pool grows unboundedly, OOM kill | R3 + R6 (HPC) | Hard cap on cut pool size; eviction policy keeps top-$10^4$ active cuts by dual value; falls back to Stage 4 `OPEN` if cap reached |
| FM6 | LP relaxation bound stalls well below $Z(25)$ on every dense candidate | R3 (escalate to R9) | If stall is universal, pipeline cannot discard; have Role 9 deliver $\underline{L}(25)$ tighter, and/or escalate Stage 3 to Stage 4 (gold ILP) on a sub-sample |
| FM7 | Wrong arXiv ID / wrong citation imported from plan / review (a v2 risk) | R3 | All citations cross-checked at first use; bibliography frozen at month 1 |
| FM8 | "Discarded" set contains a false negative due to FM1 / FM2 | R3 + R5 | Random spot-check 1% of discarded set with an independent solver and re-verification |
| FM9 | Confusing $\operatorname{cr}(K_t)$ with $Z(t)$ in code (Failure F1 in plan v3) | R3 | Pipeline uses two separate constants `Z_t` and `L_t_finite`; assertions enforce that `Z_t` is used only as upper-bound target and `L_t_finite` only for flag-threshold |
| FM10 | Pipeline produces a `FLAG` that is actually a heuristic artifact | R3 + R8 | Every `FLAG` immediately re-verified by *increasing* the heuristic budget 10x and re-running multiple OGDF restarts; if still below threshold, escalate to gold ILP attempt |

---

## 8. First 30-day deliverables

1. **D1 (day 1–5): freeze the citation table and bibliography.** Verify the
   Bungener–Kaufmann constant ($1/27.48$, $|E| \ge 6.95|V|$) against
   arXiv:2409.01733 directly. Verify Pan–Richter 2007 values for
   $\operatorname{cr}(K_{11}), \operatorname{cr}(K_{12})$. Verify ACF arXiv
   ID `1006.3783` (not the v2 typo). Verify the Cranston residual triples
   $(25, 48), (26, 50), (26, 51)$ from arXiv:2512.08020 Theorem 2.
   **Owner: R3.** Deliverable: `work/03_exact_crossing/refs.md`.

2. **D2 (day 5–14): install and benchmark the Buchheim–Chimani ILP and
   OGDF planarization on small dense graphs.** Reproduce the
   $\operatorname{cr}(K_n)$ values for $n = 7, 8, 9, 10$ (known to be $9, 18,
   36, 60$) as a smoke test, then extend to $K_{11}, K_{12}$ (known: $100,
   150$) and *attempt* $K_{13}$ (unknown; will demonstrate solver behaviour
   on a dense graph at the edge of feasibility). Record timings, RAM, and
   whether termination is achieved. **Owner: R3.** Deliverable:
   `work/03_exact_crossing/benchmarks_small.md`. **Honest expected outcome:**
   $K_{12}$ may already take days; $K_{13}$ may not terminate. This is the
   honest measurement of where the technology actually is.

3. **D3 (day 10–20): implement the cheap lower bound (Crossing Lemma + R2c
   refinement) and the OGDF heuristic upper bound as Stages 1 and 2 of the
   pipeline, on synthetic 48-vertex dense graphs (random 24-regular).**
   Establish baseline gap: how far below $Z(25) = 4356$ does the easy lower
   bound sit on typical candidates? Likely answer: ~3000, leaving a ~1400
   gap for Stage 3 to close. **Owner: R3.** Deliverable:
   `work/03_exact_crossing/stages_1_2.py` and `gap_baseline.md`.

4. **D4 (day 15–25): prototype the silver LP-relaxation bound (Stage 3) on
   one candidate at $n = 48$.** This is the make-or-break experiment. If
   the LP bound on a random $25$-critical-like 48-vertex graph saturates at
   $\sim 3500$ (well below $Z(25)$), the pipeline cannot discard on
   reasonable instances and R3 must escalate to Stage 4 / gold ILP, which
   will not scale. If the LP bound reaches $\sim 4300$ or higher, the
   silver pipeline is viable. **Owner: R3.** Deliverable:
   `work/03_exact_crossing/stage_3_prototype.md` with the empirical LP
   bound on at least 3 sample 48-vertex candidates.

5. **D5 (day 20–30): write the C3 / R1c spec document and lock the
   interfaces with Roles 2, 5, 8, 9.** Specifically: input graph6 format,
   output JSON certificate format, and the precise statement of what
   `DISCARD` / `FLAG` / `OPEN` mean. Coordinate with Role 9 on the
   finite-$\underline{L}(t)$ format and target month-3 delivery. **Owner:
   R3.** Deliverable: `work/03_exact_crossing/spec.md`.

---

## Coda

The hardest single fact in this memo is in Section 1: I do not know of a
published exact crossing-number computation on a dense graph at $n \sim 50$,
and the literature suggests the largest dense instance ever exactly solved
is $K_{12}$. If that is right, the team is being asked to push the exact
crossing-number frontier by a factor of $\sim 4$ in vertex count and a
factor of $\sim 10$ in edge count, on graphs that we already expect to be
"hardest" because of their criticality structure. The silver-tier LP
relaxation is the only realistic working level; whether the bound it
produces is strong enough to reach $Z(25) = 4356$ on candidates is an
*empirical* question that D4 will answer in week 4.

If D4 reveals the LP bound saturates well below $Z(25)$, the team should
either: (a) accept that R1c discards almost nothing, with the role's value
shifting entirely to the *flag* side (i.e., counterexample hunting under a
finite $\underline{L}(25)$ delivered by Role 9), or (b) coordinate with R2
to obtain a sharper Crossing Lemma constant *for critical graphs at this
density* so that Stage 2 already approaches $Z(25)$ and Stage 3 becomes
non-essential. The latter is the path of mathematical least resistance, and
should be explored in parallel with Stage 3 prototyping.
