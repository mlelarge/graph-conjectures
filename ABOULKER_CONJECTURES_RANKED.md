# Pierre Aboulker — Conjectures Ranked Easiest → Hardest

Generated 2026-05-21 from `data/arxiv_conjectures.json` matched against the per-record difficulty triage in `ARXIV_OPEN_DIFFICULTY_RANKING.md`. The set is every conjecture/problem/question/informal-open-question stated in arXiv papers co-authored by **Pierre Aboulker** — **56 records across 19 papers**.

## ⚠ Errata vs. the first draft of this file (2026-05-21)

A read-through against the primary papers exposed several status errors and one extraction failure in the initial heuristic draft. The corrections below are applied throughout this file. **Treat this document as a triage map, not as an authoritative status ledger.** Verify every entry against its source paper before using it to choose a research target.

| # | Record | Correction | Source |
|---:|---|---|---|
| 1 | [Conjecture 4.3 (Gyárfás-Sumner for Tournaments)](https://arxiv.org/abs/2310.04265) (arXiv:2310.04265) | open → disproved | arXiv:2401.07776 (Aubian, 2024) — TeX source identifies the refuted statement |
| 2 | [Conjecture 1.4](https://arxiv.org/abs/1710.06282) (arXiv:1710.06282) | open → solved | arXiv:1807.04969 (Cames van Batenburg–Huynh–Joret–Raymond) + grid-minor theorem; the source paper itself notes Conj 1.2 ⇒ Conj 1.4 |
| 3 | [Conjecture 5.6](https://arxiv.org/abs/2310.04265) (arXiv:2310.04265) | unclear → solved | arXiv:2602.09863 (Crew–Fan–Koerts–Moore–Spirkl); uses AACL Conj 5.8 + the inequality dom(T) ≤ ω̄(T) |
| 4 | [Conjecture (Section 9, 2-extremal digraphs)](https://arxiv.org/abs/2304.04690) (arXiv:2304.04690) | statement restored; tier-2 likely understated | TeX source of arXiv:2304.04690, Section 9 |
| 5 | *(file-wide)* `Score` column | Two-decimal precision walked back: `Tier` is the load-bearing signal, `Score` is now flagged as a within-tier tiebreaker only | Rubric in `ARXIV_OPEN_DIFFICULTY_RANKING.md` (heuristic triage, not a fresh per-record review) |

**Other caveats added in this revision:**

- The two-decimal `Score` column inherits a precision the underlying triage heuristic does not actually possess. **Treat `Tier` as the load-bearing signal and `Score` only as a within-tier tiebreaker.**

- The triage source (`ARXIV_OPEN_DIFFICULTY_RANKING.md`) itself disclaims being a fresh web review of all 686 records; abstract-only status checks and PDF/TeX extraction failures (as in 2304.04690) are known failure modes.

- Several `unclear` records in `Clique number of tournaments` (arXiv:2310.04265) plausibly resolve once Aubian 2024 and Crew et al. 2026 are walked through carefully; only the cases above were re-checked for this revision.

## How the order is built

- **Source signal:** every record carries a difficulty score (1.0–5.0) and a tier (1–5) from the triage heuristic; 1 ≈ small/finite combinatorial check, 5 ≈ landmark-programme conjecture. See the rubric in `ARXIV_OPEN_DIFFICULTY_RANKING.md`.

- **Lean:** `prove` means the positive answer looks more plausible; `disprove` means a counterexample looks more plausible; `balanced` means neither side is favoured.

- **What 'easier' means here:** lower-tier statements tend to be narrow algorithmic/structural claims with small search spaces or a finite class to check; higher-tier statements sit inside major open programmes (χ-boundedness for digraphs, dichromatic Erdős–Hajnal, extension-complexity, polynomial Gyárfás–Sumner, etc.).

- **Score vs tier:** scores like 2.55 vs 2.65 imply a precision the process does not have. The tier label (1–5) is the defensible signal; use `Score` only to order within a tier.

- Records with status **solved**, **disproved**, or **unclear** are listed in separate sections at the end; they are not part of the easy→hard ordering of still-open work.

## Counts (after errata)

- Total Aboulker-authored records mined: **56** (across **19** arXiv papers)

- **Open + partial (ranked block, 40 records):** open 32, partial 8

- Excluded from the ranking: unclear 4, solved 10, disproved 2

- Tier mix in the ranked block: 1: 1, 2: 8, 3: 19, 4: 6, 5: 6

## Ranked open/partial conjectures (easiest → hardest)

Score is shown for ordering only; trust `Tier` over the second decimal of `Score`.

| # | Score | Tier | Lean | Status | Record | Paper | One-line statement |
|---:|---:|---:|---|---|---|---|---|
| 1 | 1.50 | 1 | prove | open | [Problem 4.4](https://arxiv.org/abs/2402.10782) | Finding forest-orderings of tournaments is NP-complete | What is the complexity of the `\mathcal{C}`-FAS Problem when `\mathcal{C}` is the set of all paths? when `\mathcal{C}` is the set of graphs … |
| 2 | 1.60 | 2 | prove | open | [Informal Question on Complexity Gap Between Induced Disjoint Paths Variants](https://arxiv.org/abs/2502.05289) | Induced Disjoint Paths Without an Induced Minor | Is there a hereditary graph class in which Induced `k`-Disjoint Paths is NP-complete but Induced Disjoint `S`–`T` Paths with `\|S\|=\|T\|=k` is … |
| 3 | 2.10 | 2 | prove | open | [Conjecture 1.5](https://arxiv.org/abs/2502.05289) | Induced Disjoint Paths Without an Induced Minor | For any subcubic graph `H`, `H`-\textsc{ISC} is in `\mathsf{P}` if and only if `H` is planar. |
| 4 | 2.30 | 2 | prove | open | [Open problem on construction size](https://arxiv.org/abs/2202.01006) | Chordal directed graphs are not $χ$-bounded | It would be interesting to know if the size of the `(k+1)`-dichromatic example in `\mathcal{C}_3` can be reduced below the current bound of … |
| 5 | 2.30 | 2 | prove | open | [Question 5.4](https://arxiv.org/abs/2202.13306) | Heroes in oriented complete multipartite graphs | Let `H` and `F` be digraphs such that `\Delta(1,1,H)` is a hero in `Forb_{ind}(F)` and `H` is a hero in `Forb_{ind}(K_{1}+F)`. Then `\Delta(… |
| 6 | 2.30 | 2 | prove | open | [Conjecture (Section 9, characterization of 2-extremal digraphs)](https://arxiv.org/abs/2304.04690) | Digraph Colouring and Arc-Connectivity | A digraph `D` is 2-extremal if and only if `D \in \mathcal{H}_2`, where `\mathcal{H}_2` is the family of digraphs generated from symmetric o… |
| 7 | 2.30 | 2 | balanced | open | [Question 3.10](https://arxiv.org/abs/2310.04265) | Clique number of tournaments | Is it true that if a class of tournaments `\mathcal{T}` is polynomially `\operatorname{\overrightarrow{\chi}}`-bounded, then so is `\mathcal… |
| 8 | 2.40 | 2 | prove | open | [Problem 4.4](https://arxiv.org/abs/2102.01034) | On the dichromatic number of surfaces | What is the complexity of `\Sigma`-`k`-\textsc{Dicolourability} for `k \in \{4, 5\}` and `\Sigma` different from the sphere? |
| 9 | 2.50 | 2 | prove | open | [Question 1.7](https://arxiv.org/abs/1505.01616) | Colouring graphs with constraints on connectivity | For fixed `k \geq 4`, is there a polynomial-time algorithm that, given a `k`-connected graph `G` with maximal local connectivity `k`, finds … |
| 10 | 2.55 | 3 | prove | open | [FPT on $H_{t,t}$-free graphs for Grundy Coloring and b-Chromatic Core](https://arxiv.org/abs/2001.03794) | Grundy Coloring & friends, Half-Graphs, Bicliques | Are \textsc{Grundy Coloring} and \textsc{b-Chromatic Core} fixed-parameter tractable on `H_{t,t}`-free graphs when parameterized by `k`? |
| 11 | 2.55 | 3 | balanced | open | [Conjecture 4.2](https://arxiv.org/abs/2402.10782) | Finding forest-orderings of tournaments is NP-complete | There is a function `f` such that for every integer `k`, there is a polynomial-time algorithm that, given a tournament `T`, correctly conclu… |
| 12 | 2.55 | 3 | prove | open | [Conjecture 4](https://arxiv.org/abs/2403.02298) | Minimum acyclic number and maximum dichromatic number of oriented triangle-free graphs of a given order | `\vec{t}(n)=\Theta\sqrt{\frac{n}{\log n}}`. |
| 13 | 2.55 | 3 | balanced | open | [Problem 8](https://arxiv.org/abs/2410.23566) | Blow-ups and extensions of trees in tournaments | What is the infimum of all the constants `C` such that for every large enough integer `n`, the `k`-blow-up of every oriented tree of order `… |
| 14 | 2.60 | 3 | balanced | partial | [Conjecture 7](https://arxiv.org/abs/2410.23566) | Blow-ups and extensions of trees in tournaments | If `\cal F` is linearly unavoidable and has bounded maximum average degree, then `{\cal F}[k]` is also linearly unavoidable. |
| 15 | 2.65 | 3 | prove | open | [Conjecture 11](https://arxiv.org/abs/2410.23566) | Blow-ups and extensions of trees in tournaments | If `\cal F` is linearly unavoidable, then the family of `k`-extensions of digraphs in `\cal F` is also linearly unavoidable. |
| 16 | 2.65 | 3 | prove | open | [Problem 12](https://arxiv.org/abs/2410.23566) | Blow-ups and extensions of trees in tournaments | What is the minimum function `f` such that every `k`-extension of every forest of order `n` is `(2^{f(k)}\cdot n)`-unavoidable? |
| 17 | 2.65 | 3 | disprove | open | [Problem 6](https://arxiv.org/abs/2410.23566) | Blow-ups and extensions of trees in tournaments | Let `\alpha` be a positive real number. Does there exist a polynomial `P_{\alpha}` such that `\operatorname{unvd}(D)\leqslant P_{\alpha}(\|V(… |
| 18 | 2.80 | 3 | prove | open | [Conjecture 3](https://arxiv.org/abs/2403.02298) | Minimum acyclic number and maximum dichromatic number of oriented triangle-free graphs of a given order | `\vec{a}(n)=\Theta(\sqrt{n\log n})`. |
| 19 | 2.85 | 3 | prove | open | [Open problem on sublinear round complexity](https://arxiv.org/abs/1802.05582) | Distributed coloring in sparse graphs with fewer colors | It remains interesting to obtain a bound on the round complexity that is sublinear in `n` regardless of the value of `d`. |
| 20 | 2.85 | 3 | prove | open | [Question on randomized list-coloring round complexity](https://arxiv.org/abs/1802.05582) | Distributed coloring in sparse graphs with fewer colors | Is it possible to avoid the multiplicative factor polynomial in `\Delta` in a randomized version of the distributed `\Delta`-list-coloring a… |
| 21 | 2.90 | 3 | disprove | open | [Conjecture 3.12](https://arxiv.org/abs/2310.04265) | Clique number of tournaments | Let `k\geq 1`. The class of tournaments with twin-width at most `k` is `\operatorname{\overrightarrow{\chi}}`-bounded. |
| 22 | 2.90 | 3 | prove | open | [Conjecture 6.1](https://arxiv.org/abs/2310.04265) | Clique number of tournaments | If a class of digraphs `\mathcal{C}` is `\operatorname{\overrightarrow{\chi}}`-bounded, then so is its closure under substitution. |
| 23 | 3.10 | 3 | prove | open | [Research direction: minimal heroic tournament families](https://arxiv.org/abs/2009.13319) | Extension of Gyarfas-Sumner conjecture to digraphs | Characterize all finite and minimal families `\mathcal{H} = \{H_1, H_2, \ldots, H_k\}` of tournaments such that `\{\overrightarrow{K_2}, \ov… |
| 24 | 3.15 | 3 | balanced | partial | [Question 5.9](https://arxiv.org/abs/2310.04265) | Clique number of tournaments | Is there a function `\ell` such that, for every tournament `T`, if `\operatorname{\overrightarrow{\omega}}(T)\geq k`, then `T` has a subtour… |
| 25 | 3.15 | 3 | prove | open | [Conjecture 10](https://arxiv.org/abs/2410.23566) | Blow-ups and extensions of trees in tournaments | There is an absolute constant `C` such that for every integer `k`, every `k`-extension of an oriented tree of order `n` is `C^{k}(2n-2)`-una… |
| 26 | 3.20 | 3 | disprove | open | [Conjecture 2.2](https://arxiv.org/abs/1606.06011) | A new class of graphs that satisfies the Chen-Chvátal Conjecture | There is a finite set of graphs `F_0` such that every connected graph `G \notin F_0` either has a pendant edge or satisfies `\ell(G) + \math… |
| 27 | 3.20 | 3 | prove | open | [Open question on counter-examples to ℓ(G)+br(G)≥\|G\|](https://arxiv.org/abs/1606.06011) | A new class of graphs that satisfies the Chen-Chvátal Conjecture | It remains unknown whether all counter-examples to `\ell(G) + \mathrm{br}(G) \geq \|G\|` can be obtained from a finite set of graphs by replac… |
| 28 | 3.20 | 3 | prove | open | [Conjecture 4.11](https://arxiv.org/abs/2310.04265) | Clique number of tournaments | Let `(M,\prec)` be an ordered graph with maximum degree `1`. Then the class of `(M,\prec)`-free ordered graphs is `\chi`-bounded. |
| 29 | 3.60 | 4 | prove | partial | [Problem 1.2](https://arxiv.org/abs/2009.13319) | Extension of Gyarfas-Sumner conjecture to digraphs | What are the finite sets `\mathcal{F}` of digraphs for which the class `\mathrm{Forb}_{\mathrm{ind}}(\mathcal{F})` has bounded dichromatic n… |
| 30 | 3.95 | 4 | prove | open | [Conjecture 9](https://arxiv.org/abs/2410.23566) | Blow-ups and extensions of trees in tournaments | There exists a constant `C` such that `\operatorname{unvd}(D)\leqslant C\cdot\operatorname{unvd}(D-v)` for every acyclic digraph `D` and for… |
| 31 | 4.05 | 4 | prove | partial | [Conjecture 4.2](https://arxiv.org/abs/2009.13319) | Extension of Gyarfas-Sumner conjecture to digraphs | Let `H` be a hero and let `F` be an oriented forest. The set `\{\overleftrightarrow{K_2}, H, F\}` is heroic if and only if: either `F` is th… |
| 32 | 4.10 | 4 | prove | open | [Conjecture 4](https://arxiv.org/abs/1610.00876) | Subdivisions in digraphs of large out-degree or large dichromatic number | Every oriented tree is `\delta^+`-maderian. |
| 33 | 4.10 | 4 | prove | open | [Problem 12](https://arxiv.org/abs/1610.00876) | Subdivisions in digraphs of large out-degree or large dichromatic number | What is `\mathrm{mader}_{\vec{\chi}}(\vec{K}_n)`? |
| 34 | 4.20 | 4 | prove | open | [Conjecture 7](https://arxiv.org/abs/1610.00876) | Subdivisions in digraphs of large out-degree or large dichromatic number | If `F_1` and `F_2` are `\delta^+`-maderian, then the disjoint union of `F_1` and `F_2` is also `\delta^+`-maderian. |
| 35 | 4.60 | 5 | prove | partial | [Problem 16](https://arxiv.org/abs/1610.00876) | Subdivisions in digraphs of large out-degree or large dichromatic number | Are all digraphs `\kappa`-maderian? `\kappa'`-maderian? |
| 36 | 4.80 | 5 | prove | open | [Conjecture 3](https://arxiv.org/abs/1610.00876) | Subdivisions in digraphs of large out-degree or large dichromatic number | There exists a least integer `\mathrm{mader}_{\delta^0}(TT_k)` such that every digraph `D` with `\delta^0(D) \geq \mathrm{mader}_{\delta^0}(… |
| 37 | 4.80 | 5 | prove | open | [Conjecture 2](https://arxiv.org/abs/1806.00541) | Extension Complexity of the Correlation Polytope | For every `n`-vertex graph `G`, the extension complexity of `\mathrm{COR}(G)` is `2^{\Omega(\mathrm{tw}(G)+\log n)}`. |
| 38 | 4.85 | 5 | prove | partial | [Conjecture 4.4](https://arxiv.org/abs/2009.13319) | Extension of Gyarfas-Sumner conjecture to digraphs | Given an oriented forest `F` and for every integer `k`, `\{\overleftrightarrow{K_2}, K_k, F\}` is heroic. |
| 39 | 5.00 | 5 | prove | partial | [Conjecture 2](https://arxiv.org/abs/1605.07411) | $χ$-bounded families of oriented graphs | `\mathrm{Forb}(H)` is `\chi`-bounded if and only if `H` is a forest. |
| 40 | 5.00 | 5 | prove | partial | [Conjecture 4](https://arxiv.org/abs/1605.07411) | $χ$-bounded families of oriented graphs | For any oriented star `S`, `\mathrm{Forb}(S)` is `\chi`-bounded. |

## Detailed entries (same easiest → hardest order)

### 1. Problem 4.4 — score 1.50, tier 1, lean prove, status open
- **Paper:** [Finding forest-orderings of tournaments is NP-complete](https://arxiv.org/abs/2402.10782) (arXiv:2402.10782)
- **Kind:** Problem
- **Statement:** What is the complexity of the $\mathcal{C}$-FAS Problem when $\mathcal{C}$ is the set of all paths? when $\mathcal{C}$ is the set of graphs with maximum degree $1$?
- **Current state (per review):** Problem 4.4 asks whether the C-FAS Problem is tractable when C is the set of all paths or the set of matchings (graphs with maximum degree at most 1), motivated by the NP-completeness established for forests (Theorem 1.1). No follow-up paper resolving either question was found in the indexed literature as of May 2026. The problem remains open for both cases.

### 2. Informal Question on Complexity Gap Between Induced Disjoint Paths Variants — score 1.60, tier 2, lean prove, status open
- **Paper:** [Induced Disjoint Paths Without an Induced Minor](https://arxiv.org/abs/2502.05289) (arXiv:2502.05289)
- **Kind:** Informal
- **Statement:** Is there a hereditary graph class in which Induced $k$-Disjoint Paths is NP-complete but Induced Disjoint $S$–$T$ Paths with $|S|=|T|=k$ is polynomial-time solvable? The case $k=2$ is of particular interest.
- **Current state (per review):** The informal question asks whether there is a hereditary graph class separating the complexity of Induced k-Disjoint Paths (NP-complete) from Induced Disjoint S–T Paths with |S|=|T|=k (polynomial), with k=2 being the focal case. The source paper (ICALP 2025) motivates this by observing that known polynomial algorithms tend to cover the linkage variant broadly while hardness reductions tend to cover the flow variant; no follow-up resolving or making progress on this separation…

### 3. Conjecture 1.5 — score 2.10, tier 2, lean prove, status open
- **Paper:** [Induced Disjoint Paths Without an Induced Minor](https://arxiv.org/abs/2502.05289) (arXiv:2502.05289)
- **Kind:** Conjecture
- **Statement:** For any subcubic graph $H$, $H$-\textsc{ISC} is in $\mathsf{P}$ if and only if $H$ is planar.
- **Current state (per review):** Conjecture 1.5 from arXiv:2502.05289 proposes that for any subcubic graph $H$, the $H$-ISC problem (detecting $H$ as an induced subdivision) is in $\mathsf{P}$ if and only if $H$ is planar. The source paper provides the key hardness evidence: it exhibits a specific non-planar subcubic graph $H$ for which $H$-ISC is NP-complete (Theorem 3, also appearing as LIPIcs.ICALP.2025.4). No follow-up paper resolving or substantially advancing the full conjecture was found in the litera…

### 4. Open problem on construction size — score 2.30, tier 2, lean prove, status open
- **Paper:** [Chordal directed graphs are not $χ$-bounded](https://arxiv.org/abs/2202.01006) (arXiv:2202.01006)
- **Kind:** Informal
- **Statement:** It would be interesting to know if the size of the $(k+1)$-dichromatic example in $\mathcal{C}_3$ can be reduced below the current bound of $n^{2^{\mathrm{poly}(n)}}$, which is larger than the $2^{\mathrm{poly}(|G_k|)}$ bound achieved by Zykov's construction for triangle-free graphs.
- **Current state (per review):** No follow-up work was found that reduces the $n^{2^{\mathrm{poly}(n)}}$ size bound for the $(k+1)$-dichromatic construction in $\mathcal{C}_3$ from arXiv:2202.01006. The paper appeared in the Electronic Journal of Combinatorics (v29i2p17, 2022). Related work (arXiv:2309.17385, Bessy–Havet–Picasarri-Arrieta, 2023) studies dichromatic numbers of chordal graph orientations but does not address this specific size-reduction question. The open problem of closing the gap between $n^…

### 5. Question 5.4 — score 2.30, tier 2, lean prove, status open
- **Paper:** [Heroes in oriented complete multipartite graphs](https://arxiv.org/abs/2202.13306) (arXiv:2202.13306)
- **Kind:** Question
- **Statement:** Let $H$ and $F$ be digraphs such that $\Delta(1,1,H)$ is a hero in $Forb_{ind}(F)$ and $H$ is a hero in $Forb_{ind}(K_{1}+F)$. Then $\Delta(1,1,H)$ is a hero in $Forb_{ind}(K_{1}+F)$.
- **Current state (per review):** Question 5.4 asks whether a compositional hero property transfers across the $K_1+F$ join operation: if $\Delta(1,1,H)$ is a hero in $\mathrm{Forb}_{\mathrm{ind}}(F)$ and $H$ is a hero in $\mathrm{Forb}_{\mathrm{ind}}(K_1+F)$, must $\Delta(1,1,H)$ also be a hero in $\mathrm{Forb}_{\mathrm{ind}}(K_1+F)$? A broad search over citing papers returned no follow-up work resolving this question. The source paper appeared in the Journal of Graph Theory in 2024, and subsequent work on …

### 6. Conjecture (Section 9, characterization of 2-extremal digraphs) — score 2.30, tier 2, lean prove, status open
- **Paper:** [Digraph Colouring and Arc-Connectivity](https://arxiv.org/abs/2304.04690) (arXiv:2304.04690)
- **Kind:** Conjecture
- **Statement:** A digraph $D$ is 2-extremal if and only if $D \in \mathcal{H}_2$, where $\mathcal{H}_2$ is the family of digraphs generated from symmetric odd cycles by directed Hajós joins and 2-Hajós tree joins.
- **Errata note (this revision):** Statement filled in from the TeX source of arXiv:2304.04690 (Section 9). The pipeline had recorded 'Statement unavailable — Section 9 content absent from PDF extraction'. A full structural characterization of 2-extremal digraphs is plausibly harder than the heuristic tier-2 / score 2.30 suggests; the score is left in place but flagged as likely understated.
- **Current state (per review, rewritten):** The conjecture proposes a structural characterization of 2-extremal digraphs $D$ (those with $\vec{\chi}(D) = \lambda(D)+1 = 3$), complementing the main theorem of arXiv:2304.04690 which already handles $k=1$ and $k \geq 3$. The original triage note here said the verbatim statement could not be extracted from the PDF; that has been overridden in this revision (see *Statement* above and the Errata block), so the only remaining open question is the conjecture itself, on which no follow-up paper was found in the indexed literature as of May 2026.

### 7. Question 3.10 — score 2.30, tier 2, lean balanced, status open
- **Paper:** [Clique number of tournaments](https://arxiv.org/abs/2310.04265) (arXiv:2310.04265)
- **Kind:** Question
- **Statement:** Is it true that if a class of tournaments $\mathcal{T}$ is polynomially $\operatorname{\overrightarrow{\chi}}$-bounded, then so is $\mathcal{T}^{subst}$.
- **Current state (per review):** Question 3.10 asks whether polynomial $\overrightarrow{\chi}$-boundedness of a class of tournaments is preserved under substitution closure, in analogy with the result of Chudnovsky et al. for undirected graphs. The source paper itself establishes that (non-polynomial) $\overrightarrow{\chi}$-boundedness is preserved under substitution but only with an exponential binding function $g(w)=(3wf(w))^w$, motivating the question. No follow-up paper resolving Question 3.10 was found…

### 8. Problem 4.4 — score 2.40, tier 2, lean prove, status open
- **Paper:** [On the dichromatic number of surfaces](https://arxiv.org/abs/2102.01034) (arXiv:2102.01034)
- **Kind:** Problem
- **Statement:** What is the complexity of $\Sigma$-$k$-\textsc{Dicolourability} for $k \in \{4, 5\}$ and $\Sigma$ different from the sphere?
- **Current state (per review):** Problem 4.4 from arXiv:2102.01034 asks for the computational complexity of \Sigma-k-DICOLOURABILITY for k \in {4, 5} and \Sigma different from the sphere; the source paper establishes NP-completeness for k=2 and polynomial-time solvability for k \geq 6, leaving the intermediate cases k=4 and k=5 explicitly open. A wide literature search found no follow-up paper that resolves (or even substantially advances) this complexity question for either value of k on any non-spherical s…

### 9. Question 1.7 — score 2.50, tier 2, lean prove, status open
- **Paper:** [Colouring graphs with constraints on connectivity](https://arxiv.org/abs/1505.01616) (arXiv:1505.01616)
- **Kind:** Question
- **Statement:** For fixed $k \geq 4$, is there a polynomial-time algorithm that, given a $k$-connected graph $G$ with maximal local connectivity $k$, finds a $k$-colouring of $G$, or determines that none exists?
- **Current state (per review):** Question 1.7 asks whether, for fixed k ≥ 4, there is a polynomial-time algorithm for k-colouring k-connected graphs with maximal local (vertex) connectivity k. The source paper settles the k=3 case with a polynomial-time algorithm (the class Ĉ^k_2), but explicitly leaves the case k ≥ 4 open. No subsequent paper resolving or substantially advancing this question was found across five targeted searches covering 2016–2026.

### 10. FPT on $H_{t,t}$-free graphs for Grundy Coloring and b-Chromatic Core — score 2.55, tier 3, lean prove, status open
- **Paper:** [Grundy Coloring & friends, Half-Graphs, Bicliques](https://arxiv.org/abs/2001.03794) (arXiv:2001.03794)
- **Kind:** Problem
- **Statement:** Are \textsc{Grundy Coloring} and \textsc{b-Chromatic Core} fixed-parameter tractable on $H_{t,t}$-free graphs when parameterized by $k$?
- **Current state (per review):** The question of whether Grundy Coloring and b-Chromatic Core are FPT on $H_{t,t}$-free graphs (parameterized by $k$) was explicitly left open in the source paper and remains unresolved as of 2026. A STACS 2025 paper (arXiv:2410.20629) establishes FPT for Grundy Coloring on $K_{i,j}$-free graphs and for Partial Grundy Coloring on general graphs, advancing the broader parameterized landscape for greedy coloring problems, but does not directly address the $H_{t,t}$-free case. No…

### 11. Conjecture 4.2 — score 2.55, tier 3, lean balanced, status open
- **Paper:** [Finding forest-orderings of tournaments is NP-complete](https://arxiv.org/abs/2402.10782) (arXiv:2402.10782)
- **Kind:** Conjecture
- **Statement:** There is a function $f$ such that for every integer $k$, there is a polynomial-time algorithm that, given a tournament $T$, correctly concludes that $\operatorname{\overrightarrow{\omega}}(T)\geq k$, or finds an order $\prec$ of $V(T)$ such that $\omega(T^{\prec})\leq f(k)$
- **Current state (per review):** Conjecture 4.2 asks for a function f and polynomial-time approximation scheme that, given a tournament T and integer k, either certifies the tournament clique number satisfies $\overrightarrow{\omega}(T)\geq k$ or finds an ordering $\prec$ with $\omega(T^{\prec})\leq f(k)$. The k=3 case was settled (with a constant bound) by Aboulker, Aubian, Charbit, and Thomassé (personal communication cited as [2] in the source paper), but the general case for all k remains open. No follow…

### 12. Conjecture 4 — score 2.55, tier 3, lean prove, status open
- **Paper:** [Minimum acyclic number and maximum dichromatic number of oriented triangle-free graphs of a given order](https://arxiv.org/abs/2403.02298) (arXiv:2403.02298)
- **Kind:** Conjecture
- **Statement:** $\vec{t}(n)=\Theta\sqrt{\frac{n}{\log n}}$.
- **Current state (per review):** Conjecture 4 from arXiv:2403.02298 asserts $\vec{t}(n)=\Theta\sqrt{n/\log n}$ for the maximum dichromatic number of oriented triangle-free graphs on $n$ vertices. The paper itself establishes an upper bound $\vec{t}(n)\leq(\sqrt{2}+o(1))\sqrt{n/\log n}$ and a lower bound $\vec{t}(n)\geq\frac{8}{107}\frac{\sqrt{n}}{\log n}$, leaving a $\sqrt{\log n}$ gap on the lower side. No follow-up paper closing this gap or otherwise resolving the conjecture was found in the indexed litera…

### 13. Problem 8 — score 2.55, tier 3, lean balanced, status open
- **Paper:** [Blow-ups and extensions of trees in tournaments](https://arxiv.org/abs/2410.23566) (arXiv:2410.23566)
- **Kind:** Problem
- **Statement:** What is the infimum of all the constants $C$ such that for every large enough integer $n$, the $k$-blow-up of every oriented tree of order $n$ is $(C^{k}\cdot kn)$-unavoidable?
- **Current state (per review):** Problem 8 asks for the infimum of all constants C such that for every large enough n, the k-blow-up of every oriented tree of order n is (C^k · kn)-unavoidable. The paper establishes via Theorem 18 an upper bound of the form 2^(10+18k) · kn, which the authors acknowledge is far from tight; the maximum average degree of the k-blow-up of a tree of order n (equal to 2k − 2k/n) together with Proposition 2 gives a lower bound showing the optimal exponent is 2^Θ(k) · kn, but the pr…

### 14. Conjecture 7 — score 2.60, tier 3, lean balanced, status partial
- **Paper:** [Blow-ups and extensions of trees in tournaments](https://arxiv.org/abs/2410.23566) (arXiv:2410.23566)
- **Kind:** Conjecture
- **Statement:** If $\cal F$ is linearly unavoidable and has bounded maximum average degree, then ${\cal F}[k]$ is also linearly unavoidable.
- **Current state (per review):** Conjecture 7 asks whether the $k$-blow-up operation preserves linear unavoidability under a bounded maximum average degree condition. The source paper itself proves the conjecture for the special case where $\mathcal{F}$ is the family of oriented trees, establishing that $k$-blow-ups of oriented trees are linearly unavoidable. No subsequent paper resolving the full conjecture has been found in the literature as of May 2026.

### 15. Conjecture 11 — score 2.65, tier 3, lean prove, status open
- **Paper:** [Blow-ups and extensions of trees in tournaments](https://arxiv.org/abs/2410.23566) (arXiv:2410.23566)
- **Kind:** Conjecture
- **Statement:** If $\cal F$ is linearly unavoidable, then the family of $k$-extensions of digraphs in $\cal F$ is also linearly unavoidable.
- **Current state (per review):** Conjecture 11 from arXiv:2410.23566 asserts that the k-extension operation preserves linear unavoidability for any family of digraphs. The source paper itself proves a special case (Corollary 25): the family of k-extensions of oriented forests is linearly unavoidable. The general conjecture is noted to follow from the stronger Conjecture 9 (that adding a single vertex multiplies the unavoidability constant by at most a constant). No follow-up paper resolving or making further…

### 16. Problem 12 — score 2.65, tier 3, lean prove, status open
- **Paper:** [Blow-ups and extensions of trees in tournaments](https://arxiv.org/abs/2410.23566) (arXiv:2410.23566)
- **Kind:** Problem
- **Statement:** What is the minimum function $f$ such that every $k$-extension of every forest of order $n$ is $(2^{f(k)}\cdot n)$-unavoidable?
- **Current state (per review):** Problem 12 asks for the minimum function $f$ such that every $k$-extension of every forest of order $n$ is $(2^{f(k)}\cdot n)$-unavoidable in tournaments. As of the source paper (October 2024), the gap between the quadratic upper bound $f(k)\leq\binom{2k+2}{2}$ (Corollary 25) and the linear lower bound from Proposition 28 remains open. No follow-up paper resolving or narrowing this gap was found in a search of the literature up to May 2026.

### 17. Problem 6 — score 2.65, tier 3, lean disprove, status open
- **Paper:** [Blow-ups and extensions of trees in tournaments](https://arxiv.org/abs/2410.23566) (arXiv:2410.23566)
- **Kind:** Problem
- **Statement:** Let $\alpha$ be a positive real number. Does there exist a polynomial $P_{\alpha}$ such that $\operatorname{unvd}(D)\leqslant P_{\alpha}(|V(D)|)$ for every digraph with maximum average degree at most $\alpha$?
- **Current state (per review):** Problem 6 from arXiv:2410.23566 asks whether for each positive real α there exists a polynomial P_α bounding unvd(D) for every digraph with maximum average degree at most α. The question is motivated by Fox, He, and Wigderson's result (arXiv:2105.02383) establishing that acyclic digraphs with bounded maximum degree are not linearly unavoidable, with unavoidability growing as n^{Ω(Δ^{2/3}/log^{5/3}Δ)}. No paper resolving the polynomial question or providing a counterexample wa…

### 18. Conjecture 3 — score 2.80, tier 3, lean prove, status open
- **Paper:** [Minimum acyclic number and maximum dichromatic number of oriented triangle-free graphs of a given order](https://arxiv.org/abs/2403.02298) (arXiv:2403.02298)
- **Kind:** Conjecture
- **Statement:** $\vec{a}(n)=\Theta(\sqrt{n\log n})$.
- **Current state (per review):** Conjecture 3 of arXiv:2403.02298 asserts that the minimum acyclic number over all oriented triangle-free graphs of order n satisfies $\vec{a}(n)=\Theta(\sqrt{n\log n})$. The source paper establishes matching lower bound $(\frac{1}{\sqrt{2}}-\varepsilon)\sqrt{n\log n}$ and upper bound $\frac{107}{8}\sqrt{n}\log n$, leaving a logarithmic gap; the authors conjecture the upper bound can be tightened to $C\sqrt{n\log n}$ via the triangle-free process. No subsequent paper resolving…

### 19. Open problem on sublinear round complexity — score 2.85, tier 3, lean prove, status open
- **Paper:** [Distributed coloring in sparse graphs with fewer colors](https://arxiv.org/abs/1802.05582) (arXiv:1802.05582)
- **Kind:** Problem
- **Statement:** It remains interesting to obtain a bound on the round complexity that is sublinear in $n$ regardless of the value of $d$.
- **Current state (per review):** The open problem asks for a distributed algorithm coloring $d$-degenerate graphs with $(1+\varepsilon)d$ colors in a number of rounds that is sublinear in $n$ for every fixed $d$, without the round bound growing with $d$. The source paper achieves $O(d^4\log^3 n)$ rounds, improvable to $d^3 \cdot 2^{O(\sqrt{\log n})}$ via the Panconesi--Srinivasan network decomposition. The 2020 breakthrough of Rozhoň and Ghaffari (STOC 2020) provides a poly$(\log n)$-time deterministic netwo…

### 20. Question on randomized list-coloring round complexity — score 2.85, tier 3, lean prove, status open
- **Paper:** [Distributed coloring in sparse graphs with fewer colors](https://arxiv.org/abs/1802.05582) (arXiv:1802.05582)
- **Kind:** Question
- **Statement:** Is it possible to avoid the multiplicative factor polynomial in $\Delta$ in a randomized version of the distributed $\Delta$-list-coloring algorithm (Corollary 2.1)?
- **Current state (per review):** The question asks whether a randomized distributed algorithm for Delta-list-coloring can achieve round complexity without a polynomial factor in Delta, analogously to the O(log^3 n / log Delta)-round randomized algorithm of Panconesi and Srinivasan for Delta-coloring. Subsequent work has made substantial progress on randomized Delta-coloring (Ghaffari et al. 2018 reduced to O(log Delta) + 2^{O(sqrt{log log n})} rounds; a 2025 preprint further improved deterministic bounds), a…

### 21. Conjecture 3.12 — score 2.90, tier 3, lean disprove, status open
- **Paper:** [Clique number of tournaments](https://arxiv.org/abs/2310.04265) (arXiv:2310.04265)
- **Kind:** Conjecture
- **Statement:** Let $k\geq 1$. The class of tournaments with twin-width at most $k$ is $\operatorname{\overrightarrow{\chi}}$-bounded.
- **Current state (per review):** Conjecture 3.12 from arXiv:2310.04265 asks whether every class of tournaments with twin-width at most k is χ⃗-bounded. The conjecture is explicitly motivated by the fact that tournaments with bounded twin-width can have arbitrarily large dichromatic number (the tournament S_k has twin-width 1 and dichromatic number k), yet χ⃗-boundedness — dichromatic number bounded as a function of the clique number — may still hold. No follow-up paper resolving this conjecture was found in …

### 22. Conjecture 6.1 — score 2.90, tier 3, lean prove, status open
- **Paper:** [Clique number of tournaments](https://arxiv.org/abs/2310.04265) (arXiv:2310.04265)
- **Kind:** Conjecture
- **Statement:** If a class of digraphs $\mathcal{C}$ is $\operatorname{\overrightarrow{\chi}}$-bounded, then so is its closure under substitution.
- **Current state (per review):** Conjecture 6.1 asks whether the class of $\overrightarrow{\chi}$-bounded digraphs is closed under substitution in full generality. The tournament case is already settled affirmatively by Theorem 3.9 of the source paper, which shows that if a tournament class is $\overrightarrow{\chi}$-bounded then so is its closure under substitution (with an explicit bound). The authors note that key tools used for tournaments fail for general digraphs, so the conjecture remains open for the…

### 23. Research direction: minimal heroic tournament families — score 3.10, tier 3, lean prove, status open
- **Paper:** [Extension of Gyarfas-Sumner conjecture to digraphs](https://arxiv.org/abs/2009.13319) (arXiv:2009.13319)
- **Kind:** Informal
- **Statement:** Characterize all finite and minimal families $\mathcal{H} = \{H_1, H_2, \ldots, H_k\}$ of tournaments such that $\{\overrightarrow{K_2}, \overleftrightarrow{K_2}, H_1, H_2, \ldots, H_k\}$ is a heroic set.
- **Current state (per review):** No paper has been found that directly addresses the characterization of all finite minimal families of tournaments forming heroic sets of the form $\{\overrightarrow{K_2}, \overleftrightarrow{K_2}, H_1, \ldots, H_k\}$; the single-hero case ($|\mathcal{H}|=1$) was already settled by Berger et al. before the source paper. Related activity around heroic sets and dichromatic number bounds has continued (heroes in oriented complete multipartite graphs, chi-boundedness for specific…

### 24. Question 5.9 — score 3.15, tier 3, lean balanced, status partial
- **Paper:** [Clique number of tournaments](https://arxiv.org/abs/2310.04265) (arXiv:2310.04265)
- **Kind:** Question
- **Statement:** Is there a function $\ell$ such that, for every tournament $T$, if $\operatorname{\overrightarrow{\omega}}(T)\geq k$, then $T$ has a subtournament $A$ such that $|A|\leq\ell(k)$ and $\operatorname{\overrightarrow{\omega}}(A)\geq k$.
- **Current state (per review):** Question 5.9 asks whether $\overrightarrow{\omega}(T)\geq k$ is always witnessed by a bounded-size subtournament (i.e., $f$ = identity). A 2026 paper by Crew, Fan, Koerts, Moore, and Spirkl (arXiv:2602.09863) proves a closely related weaker form (their Corollary 7): there exist two functions $f$ and $\ell$ such that $\overrightarrow{\omega}(T)\geq f(k)$ implies a subtournament of size $\leq\ell(k)$ with $\overrightarrow{\omega}\geq k$; this resolves the weaker Conjecture 5.8 …

### 25. Conjecture 10 — score 3.15, tier 3, lean prove, status open
- **Paper:** [Blow-ups and extensions of trees in tournaments](https://arxiv.org/abs/2410.23566) (arXiv:2410.23566)
- **Kind:** Conjecture
- **Statement:** There is an absolute constant $C$ such that for every integer $k$, every $k$-extension of an oriented tree of order $n$ is $C^{k}(2n-2)$-unavoidable.
- **Current state (per review):** Conjecture 10 from arXiv:2410.23566 asserts the existence of an absolute constant C such that every k-extension of an oriented tree of order n is C^k(2n-2)-unavoidable. This would follow from Conjecture 9 (multiplicative stability under vertex addition) combined with Sumner's conjecture, but remains open. The paper itself establishes only a weaker bound of (2·3^{\binom{2k+2}{2}}·|V(F)|)-unavoidability (Corollary 25), with super-exponential dependence on k rather than the conj…

### 26. Conjecture 2.2 — score 3.20, tier 3, lean disprove, status open
- **Paper:** [A new class of graphs that satisfies the Chen-Chvátal Conjecture](https://arxiv.org/abs/1606.06011) (arXiv:1606.06011)
- **Kind:** Conjecture
- **Statement:** There is a finite set of graphs $F_0$ such that every connected graph $G \notin F_0$ either has a pendant edge or satisfies $\ell(G) + \mathrm{br}(G) \geq |G|$.
- **Current state (per review):** Conjecture 2.2 from arXiv:1606.06011 proposes that all counterexamples to ℓ(G) + br(G) ≥ |G| among graphs without a pendant edge form a finite exceptional family F_0; the source paper identified three minimal counterexamples with a bridge. Searches of the subsequent Chen-Chvátal literature (including papers on bisplit graphs, diameter-3 graphs, and improved metric-space lower bounds) found no paper that resolves or substantially advances this specific finite-family conjecture…

### 27. Open question on counter-examples to ℓ(G)+br(G)≥|G| — score 3.20, tier 3, lean prove, status open
- **Paper:** [A new class of graphs that satisfies the Chen-Chvátal Conjecture](https://arxiv.org/abs/1606.06011) (arXiv:1606.06011)
- **Kind:** Informal
- **Statement:** It remains unknown whether all counter-examples to $\ell(G) + \mathrm{br}(G) \geq |G|$ can be obtained from a finite set of graphs by replacing a bridge by a path of arbitrary length.
- **Current state (per review):** The structural question of whether all counter-examples to $\ell(G)+\mathrm{br}(G)\geq|G|$ arise, up to bridge-to-path replacement, from a finite base set of graphs remains unresolved in the published literature found. Subsequent work has characterised counter-examples in restricted graph classes (bipartite graphs by Matamala and Zamora 2020, locally connected and diameter-2 graphs circa 2025) and proved the Chen-Chvátal conjecture for graphs of diameter three (arXiv:2512.120…

### 28. Conjecture 4.11 — score 3.20, tier 3, lean prove, status open
- **Paper:** [Clique number of tournaments](https://arxiv.org/abs/2310.04265) (arXiv:2310.04265)
- **Kind:** Conjecture
- **Statement:** Let $(M,\prec)$ be an ordered graph with maximum degree $1$. Then the class of $(M,\prec)$-free ordered graphs is $\chi$-bounded.
- **Current state (per review):** Conjecture 4.11 of arXiv:2310.04265 asserts that for any ordered graph $(M,\prec)$ with maximum degree $1$, the class of $(M,\prec)$-free ordered graphs is $\chi$-bounded; this would imply $\overrightarrow{\chi}$-boundedness results for certain tournament classes via the paper's backedge-graph correspondence. No paper resolving this conjecture was found. Two papers citing the source were identified via Semantic Scholar — arXiv:2602.09863 (Crew et al., 2026) on characterising …

### 29. Problem 1.2 — score 3.60, tier 4, lean prove, status partial
- **Paper:** [Extension of Gyarfas-Sumner conjecture to digraphs](https://arxiv.org/abs/2009.13319) (arXiv:2009.13319)
- **Kind:** Problem
- **Statement:** What are the finite sets $\mathcal{F}$ of digraphs for which the class $\mathrm{Forb}_{\mathrm{ind}}(\mathcal{F})$ has bounded dichromatic number?
- **Current state (per review):** Problem 1.2 asks for a full characterization of all finite sets of digraphs that are heroic (i.e., whose avoidance guarantees bounded dichromatic number); this characterization remains open. Partial progress includes: locally out-transitive oriented graphs shown to have dichromatic number at most 2 (arXiv:2103.07886); (P6, triangle)-free oriented graphs shown to have dichromatic number at most 382 (arXiv:2212.02272); heroes in oriented complete multipartite graphs nearly full…

### 30. Conjecture 9 — score 3.95, tier 4, lean prove, status open
- **Paper:** [Blow-ups and extensions of trees in tournaments](https://arxiv.org/abs/2410.23566) (arXiv:2410.23566)
- **Kind:** Conjecture
- **Statement:** There exists a constant $C$ such that $\operatorname{unvd}(D)\leqslant C\cdot\operatorname{unvd}(D-v)$ for every acyclic digraph $D$ and for every vertex $v$ of $D$.
- **Current state (per review):** Conjecture 9 from arXiv:2410.23566 asserts that there exists a constant C such that unvd(D) ≤ C·unvd(D−v) for every acyclic digraph D and every vertex v, where unvd(D) is the smallest order of a tournament that contains D. The paper itself proves the special case C=2 when v is a source or sink (Proposition 1), but the general case remains open. No follow-up paper resolving the conjecture was found in a targeted web search covering the period 2024–2026.

### 31. Conjecture 4.2 — score 4.05, tier 4, lean prove, status partial
- **Paper:** [Extension of Gyarfas-Sumner conjecture to digraphs](https://arxiv.org/abs/2009.13319) (arXiv:2009.13319)
- **Kind:** Conjecture
- **Statement:** Let $H$ be a hero and let $F$ be an oriented forest. The set $\{\overleftrightarrow{K_2}, H, F\}$ is heroic if and only if: either $F$ is the disjoint union of oriented stars, or $H$ is a transitive tournament.
- **Current state (per review):** The 'only if' direction of Conjecture 4.2 is established in the source paper, and the case where both conditions hold simultaneously was resolved prior to posting by Chudnovsky–Scott–Seymour. Several special cases of the 'if' direction have since been proved: Aboulker, Aubian, and Charbit (2021) prove the case F = S₂⁺ with H = C₃; Aboulker, Aubian, Charbit, and Thomassé (2022) establish bounded dichromatic number for ⃗P₆-free triangle-free oriented graphs. A 2026 preprint by …

### 32. Conjecture 4 — score 4.10, tier 4, lean prove, status open
- **Paper:** [Subdivisions in digraphs of large out-degree or large dichromatic number](https://arxiv.org/abs/1610.00876) (arXiv:1610.00876)
- **Kind:** Conjecture
- **Statement:** Every oriented tree is $\delta^+$-maderian.
- **Current state (per review):** Conjecture 4 from arXiv:1610.00876, that every oriented tree is $\delta^+$-maderian, remains open as of 2026. The source paper itself established special cases: in-arborescences are $\delta^+$-maderian (Theorem 23) and all oriented paths are $\delta^+$-maderian (Corollary 20), but the general statement is unresolved. A 2024 survey (Stein, arXiv:2310.18719) explicitly notes that minimum-outdegree conditions for oriented trees and paths 'appear to be very difficult' and that re…

### 33. Problem 12 — score 4.10, tier 4, lean prove, status open
- **Paper:** [Subdivisions in digraphs of large out-degree or large dichromatic number](https://arxiv.org/abs/1610.00876) (arXiv:1610.00876)
- **Kind:** Problem
- **Statement:** What is $\mathrm{mader}_{\vec{\chi}}(\vec{K}_n)$?
- **Current state (per review):** Problem 12 asks for the exact value of $\mathrm{mader}_{\vec{\chi}}(\vec{K}_n)$; the source paper only establishes the doubly-exponential upper bound $4^{n^2-2n+1}(n-1)+1$. The most relevant follow-up, Gishboliner–Steiner–Szabó (2020, arXiv:2008.09888), proves $\mathrm{mader}_{\vec{\chi}}(F)=v(F)$ for octus digraphs and orientations of cactus graphs, but the complete digraph $\vec{K}_n$ falls outside these classes and the exact value remains unknown. No paper resolving Proble…

### 34. Conjecture 7 — score 4.20, tier 4, lean prove, status open
- **Paper:** [Subdivisions in digraphs of large out-degree or large dichromatic number](https://arxiv.org/abs/1610.00876) (arXiv:1610.00876)
- **Kind:** Conjecture
- **Statement:** If $F_1$ and $F_2$ are $\delta^+$-maderian, then the disjoint union of $F_1$ and $F_2$ is also $\delta^+$-maderian.
- **Current state (per review):** Conjecture 7 from arXiv:1610.00876 asks whether the class of δ⁺-maderian digraphs is closed under disjoint union; no resolution has been found. The closely related arXiv:2008.13224 (Gishboliner–Steiner–Szabó 2020) proves oriented cycles are δ⁺-maderian (a different conjecture in the same paper), while arXiv:2008.09888 addresses the dichromatic-number analogue (mader_χ) rather than the min-out-degree version. The partial result via Erdős–Pósa (Theorem 8 of the source paper) ha…

### 35. Problem 16 — score 4.60, tier 5, lean prove, status partial
- **Paper:** [Subdivisions in digraphs of large out-degree or large dichromatic number](https://arxiv.org/abs/1610.00876) (arXiv:1610.00876)
- **Kind:** Problem
- **Statement:** Are all digraphs $\kappa$-maderian? $\kappa'$-maderian?
- **Current state (per review):** Problem 16 asks two questions: whether all digraphs are $\kappa$-maderian (large strong connectivity forces subdivisions) and whether all digraphs are $\kappa'$-maderian (large strong arc-connectivity forces subdivisions). The $\kappa'$-maderian question was answered negatively by Gishboliner, Steiner, and Szabó (arXiv:2008.13224, Propositions 10--11), who showed that neither $\overleftrightarrow{K_4}$ nor $\overleftrightarrow{S_4}$ is $\kappa'$-maderian. The $\kappa$-maderia…

### 36. Conjecture 3 — score 4.80, tier 5, lean prove, status open
- **Paper:** [Subdivisions in digraphs of large out-degree or large dichromatic number](https://arxiv.org/abs/1610.00876) (arXiv:1610.00876)
- **Kind:** Conjecture
- **Statement:** There exists a least integer $\mathrm{mader}_{\delta^0}(TT_k)$ such that every digraph $D$ with $\delta^0(D) \geq \mathrm{mader}_{\delta^0}(TT_k)$ contains a subdivision of $TT_k$.
- **Current state (per review):** Conjecture 3 from arXiv:1610.00876 — that a least integer $\mathrm{mader}_{\delta^0}(TT_k)$ exists forcing a $TT_k$ subdivision in every digraph of minimum semi-degree at least that threshold — remains open. It is shown in the source paper to be equivalent to Mader's 1985 conjecture (Conjecture 2) on minimum out-degree; the full conjecture is unresolved even for $k=5$. Related papers in the curated corpus (arXiv:2008.13224, arXiv:2008.09888) make progress on other conjectures…

### 37. Conjecture 2 — score 4.80, tier 5, lean prove, status open
- **Paper:** [Extension Complexity of the Correlation Polytope](https://arxiv.org/abs/1806.00541) (arXiv:1806.00541)
- **Kind:** Conjecture
- **Statement:** For every $n$-vertex graph $G$, the extension complexity of $\mathrm{COR}(G)$ is $2^{\Omega(\mathrm{tw}(G)+\log n)}$.
- **Current state (per review):** The source paper proves the matching upper bound 2^{O(tw(G)+log n)} for the extension complexity of COR(G) and establishes tightness for minor-closed graph classes, but Conjecture 2 — that 2^{Omega(tw(G)+log n)} holds for every n-vertex graph G — remains open in full generality. Five web searches spanning 2019–2026 found no follow-up paper proving or disproving the conjecture for arbitrary graphs. The conjecture would imply 2^{Omega(n)} extension complexity for the stable set…

### 38. Conjecture 4.4 — score 4.85, tier 5, lean prove, status partial
- **Paper:** [Extension of Gyarfas-Sumner conjecture to digraphs](https://arxiv.org/abs/2009.13319) (arXiv:2009.13319)
- **Kind:** Conjecture
- **Statement:** Given an oriented forest $F$ and for every integer $k$, $\{\overleftrightarrow{K_2}, K_k, F\}$ is heroic.
- **Current state (per review):** Conjecture 4.4 — that $\{\overleftrightarrow{K_2}, K_k, F\}$ is heroic for every oriented forest $F$ and every integer $k$ — remains open in full generality. Two follow-up papers from the curated corpus establish special cases: arXiv:2103.07886 handles $F = S_2^+$ (oriented star with two out-edges) and arXiv:2212.02272 handles $F = \overrightarrow{P}_6$ with the clique constraint $\omega \le 2$ (triangle-free). A separate paper (arXiv:2202.13306) is noted to disprove a conjec…

### 39. Conjecture 2 — score 5.00, tier 5, lean prove, status partial
- **Paper:** [$χ$-bounded families of oriented graphs](https://arxiv.org/abs/1605.07411) (arXiv:1605.07411)
- **Kind:** Conjecture
- **Statement:** $\mathrm{Forb}(H)$ is $\chi$-bounded if and only if $H$ is a forest.
- **Current state (per review):** Conjecture 2 from arXiv:1605.07411 — that $\mathrm{Forb}(H)$ is $\chi$-bounded if and only if $H$ is a forest in the directed/oriented setting — is explicitly stated in the source paper to be equivalent to the Gyárfás–Sumner conjecture and remains open in full generality. Substantial partial progress has been made: the conjecture is proved for every orientation of $P_4$ (Cook et al., 2022/2023), for $(\overrightarrow{P}_6, \text{triangle})$-free digraphs (Aboulker et al., 202…

### 40. Conjecture 4 — score 5.00, tier 5, lean prove, status partial
- **Paper:** [$χ$-bounded families of oriented graphs](https://arxiv.org/abs/1605.07411) (arXiv:1605.07411)
- **Kind:** Conjecture
- **Statement:** For any oriented star $S$, $\mathrm{Forb}(S)$ is $\chi$-bounded.
- **Current state (per review):** Conjecture 4 from arXiv:1605.07411 — that Forb(S) is χ-bounded for every oriented star S — remains open in full generality. The source paper proved the cases k=0, k=ℓ=1, and the TT_3-free setting; subsequent work (arXiv:2103.07886) proved the S_2^+ special case (locally out-transitive oriented graphs have dichromatic number at most 2). The related Aboulker–Charbit–Naserasr conjecture for oriented trees has seen additional progress (P4 orientations in arXiv:2209.06171, P6-free…

## Unclear / status not pinned down

Records that the triage layer could not cleanly classify (often because a counter-example to *some* conjecture from the same paper exists but the abstract does not say which). After this revision, **Conjecture 5.6 of 2310.04265 has been moved to *solved*** (see Errata). The remaining unclear set is below; treat them as open but verify against the source paper before working on them.

- **[Question 3.5](https://arxiv.org/abs/2310.04265)** — *Clique number of tournaments*. Is it true that for every tournament $T$, there exists $\prec\in\mathfrak{S}(T)$ such that $\prec$ is both a $\operatorname{\overrightarrow{\omega}}$-ordering and a $\operatorname{\overrightarrow{\chi}}$-ordering?
  - Review note: A follow-up paper arXiv:2401.07776 (Aubian, 2024) titled 'Computing the clique number of tournaments' explicitly provides a counterexample to a conjecture of Aboulker, Aubian, Charbit and Lopes, but its abstract does not specify which conje…
- **[Conjecture 3.13](https://arxiv.org/abs/2310.04265)** — *Clique number of tournaments*. There exists a function $f$, such that for every tournament $T$, there exists an ordering $\prec^{*}$ of $V(T)$ such that:
  - Review note: Conjecture 3.13 from arXiv:2310.04265 asserts the existence of a function f such that every tournament T admits a single vertex ordering simultaneously witnessing structural and coloring properties, and is described as a strengthening that …
- **[Conjecture 3.16](https://arxiv.org/abs/2310.04265)** — *Clique number of tournaments*. There exists a function $f$ such that, for every tournament $T$, there exists a $BST$-ordering $\prec$ of $T$ such:
  - Review note: Conjecture 3.16 specialises Conjecture 3.13 to BST-orderings of tournaments, asserting the existence of a function f such that every tournament admits a BST-ordering satisfying a simultaneous bound on clique number and dichromatic number. A…
- **[Conjecture 5.10](https://arxiv.org/abs/2310.04265)** — *Clique number of tournaments*. For every integer $k\geq 3$, there is an infinite number of $k$-$\operatorname{\overrightarrow{\omega}}$-critical tournaments.
  - Review note: No follow-up paper specifically addressing Conjecture 5.10 (infinitely many k-\overrightarrow{\omega}-critical tournaments for k≥3) was found. A January 2024 paper (arXiv:2401.07776) on NP-completeness of computing the clique number of tour…

## Already resolved (excluded from the easy→hard list)

Listed for completeness — these conjectures are no longer triage targets. Three of these are added in this revision (see Errata).

| Status | Record | Paper | Statement | What happened |
|---|---|---|---|---|
| disproved | [Question 1.4](https://arxiv.org/abs/2202.13306) | Heroes in oriented complete multipartite graphs | Is `\Delta(1,2,2)` a hero in oriented complete multipartite graphs? | Question 1.4 is answered negatively: Δ(1,2,2) is not a hero in oriented complete multipartite graphs. Remark 1.5 of the revised paper (v2, December 2023; published Journal of Graph Theory 105(4):652–669, 2024) records that Bartosz Walczak p… |
| disproved | [Conjecture 4.3 (Gyárfás-Sumner for Tournaments)](https://arxiv.org/abs/2310.04265) | Clique number of tournaments | A tournament `H` is `\operatorname{\overrightarrow{\chi}}`-binding if and only if `H` has a backedge graph which is a forest. | **Added in this revision.** Refuted by Aubian (arXiv:2401.07776, 2024): the construction produces tournaments whose backedge graph is a forest yet whose clique number is 2 with unbounded dichromatic number — directly contradicting the tournament Gyárfás–Sumner statement. Original review (May 2026) tagged this 'open' because the Aubian abstract did not name which AACL conjecture it refuted; the TeX source identifies it as Conjecture 4.3. |
| solved | [Conjecture 5.3 (Large dom implies an ω̄-cluster)](https://arxiv.org/abs/2310.04265) | Clique number of tournaments | There exist two functions `f` and `\ell` such that, for every integer `k`, every tournament `T` with `\operatorname{dom}(T)\geq f(k)` contains a subtournament `… | Conjecture 5.3 asks whether large dom(T) forces a bounded-size subtournament with large clique number ω̄. Crew, Fan, Koerts, Moore, and Spirkl (arXiv:2602.09863, 2026) prove Corollary 7 of their paper, which is exactly Conjecture 5.8 of the… |
| solved | [Conjecture 5.6](https://arxiv.org/abs/2310.04265) | Clique number of tournaments | There exists a function `g` such that, for every integer `t`, if `T` is a tournament such that for every `v\in V(T)`, `\operatorname{\overrightarrow{\omega}}(N^… | **Added in this revision.** Settled by Crew–Fan–Koerts–Moore–Spirkl (arXiv:2602.09863), which proves the AACL Conjecture 5.8 form (bounded-size large-ω̄ certificate from large clique number). Since dom(T) ≤ ω̄(T), this implies the 'large dom forces an ω̄-cluster' conjecture (5.3, also in this paper) and, as the original paper states, the local-to-global implication of Conjecture 5.6. |
| solved | [Conjecture 2](https://arxiv.org/abs/2008.05504) | On the tree-width of even-hole-free graphs | There is a function `f : \mathbb{N} \to \mathbb{N}` such that every even-hole-free graph of degree at most `d` has tree-width at most `f(d)`. | Conjecture 2 from arXiv:2008.05504 — that every even-hole-free graph of degree at most `d` has tree-width at most `f(d)` for some function `f` — was resolved affirmatively within weeks of being posted. Abrishami, Chudnovsky, and Vušković (a… |
| solved | [Conjecture 3](https://arxiv.org/abs/2008.05504) | On the tree-width of even-hole-free graphs | For every `d \in \mathbb{N}` there is a function `f_d : \mathbb{N} \to \mathbb{N}` such that every graph with degree at most `d` and tree-width at least `f_d(k)… | Conjecture 3 from arXiv:2008.05504 was proved by Korhonen (arXiv:2203.13233, JCTB 2023), who showed that every graph of bounded maximum degree and sufficiently large treewidth contains a large wall or the line graph of a large wall as an in… |
| solved | [FPT on $K_{t,t}$-free graphs for Grundy Coloring](https://arxiv.org/abs/2001.03794) | Grundy Coloring & friends, Half-Graphs, Bicliques | Does \textsc{Grundy Coloring} admit a fixed-parameter tractable algorithm on `K_{t,t}`-free graphs when parameterized by `k`? | The open question of whether \textsc{Grundy Coloring} is FPT on `K_{t,t}`-free graphs parameterized by `k` was resolved affirmatively by Agrawal, Lokshtanov, Panolan, Saurabh, and Verma (arXiv:2410.20629, STACS 2025), which provides an FPT … |
| solved | [Parameterized complexity of Partial Grundy Coloring on general graphs](https://arxiv.org/abs/2001.03794) | Grundy Coloring & friends, Half-Graphs, Bicliques | What is the parameterized complexity of \textsc{Partial Grundy Coloring} on general graphs, parameterized by `k`? | The open problem from arXiv:2001.03794 — whether Partial Grundy Coloring on general graphs is FPT when parameterized by k — was resolved affirmatively. Agrawal, Lokshtanov, Panolan, Saurabh, and Verma (STACS 2025, arXiv:2410.20629) give an … |
| solved | [Conjecture 1.2](https://arxiv.org/abs/1710.06282) | A tight Erdős-Pósa function for wheel minors | For every planar graph `H`, the Erdős-Pósa property holds for `H`-models with a `O(k \log k)` bounding function. | Conjecture 1.2 was resolved by Cames van Batenburg, Huynh, Joret, and Raymond in arXiv:1807.04969, submitted just eight days after the journal publication date of the source paper. They prove that for every planar graph H, the Erdős-Pósa pr… |
| solved | [Conjecture 1.4](https://arxiv.org/abs/1710.06282) | A tight Erdős-Pósa function for wheel minors | There is a function `f : \mathbb{N} \to \mathbb{N}` such that for all integers `r, k \geq 1`, every graph `G` of treewidth at least `f(r) \cdot k \log(k + 1)` h… | **Added in this revision.** Settled as a corollary of Conjecture 1.2 (proved by Cames van Batenburg, Huynh, Joret, Raymond, arXiv:1807.04969): take H to be a sufficiently large grid in the planar-minor Erdős–Pósa theorem and apply the grid-minor theorem to convert the H-model packing into a treewidth-r packing. The original paper itself notes that Conj 1.2 implies Conj 1.4. |
| solved | [Conjecture 11](https://arxiv.org/abs/1610.00876) | Subdivisions in digraphs of large out-degree or large dichromatic number | If `T` is an oriented tree of order `k`, then `\mathrm{mader}_{\chi}(T) \leq 2k-2`. | Conjecture 11 states that for every oriented tree T of order k, mader_chi(T) <= 2k-2. The 2020 paper arXiv:2008.09888 (Gishboliner, Steiner, Szabó) proves the stronger result mader_chi(F) = v(F) for all orientations of cactus graphs (Coroll… |
| solved | [Conjecture 5](https://arxiv.org/abs/1605.07411) | $χ$-bounded families of oriented graphs | Let `\mathcal{P}` be a non-empty subset of `\mathrm{Or}(P_4)`. If `\mathcal{P} \neq \{P^+(3)\}` and `\mathcal{P} \neq \{P^+(1,1,1)\}`, then `\mathrm{Forb}(\math… | Conjecture 5 asserts that `\mathrm{Forb}(\mathcal{P})` is `\chi`-bounded for every non-empty `\mathcal{P} \subseteq \mathrm{Or}(P_4)` with `\mathcal{P} \neq \{P^+(3)\}` and `\mathcal{P} \neq \{P^+(1,1,1)\}`. The source paper itself proved t… |

## Source files

- `data/arxiv_conjectures.json` — extracted statements (filtered to entries whose `paper_authors` contains *Pierre Aboulker*).

- `data/arxiv_reviews/<arxiv_id>__<idx>.json` — per-record status + summary used for the *unclear / solved* split.

- `ARXIV_OPEN_DIFFICULTY_RANKING.md` — source of the per-record `score`, `tier`, and `lean` values.

- Errata in this revision come from direct reads of arXiv:2401.07776, arXiv:1807.04969, arXiv:2602.09863, and the TeX source of arXiv:2304.04690.
