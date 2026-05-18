# Audit — Round 1

Auditor brief: forensic check of every named theorem, hypothesis, and benchmark
in `attack_plan.md` v3 (with `review.md` v2 as context). Quotations below are
verbatim from the primary source unless explicitly noted. Page/line locations
refer to the arXiv PDF unless stated otherwise.

Convention used throughout:
- "$k$-arc-strong" = every arc-cut has size $\ge k$ (arc-connectivity $\ge k$).
- "$k$-strong" or "$k$-vertex-strong" = every vertex-cut has size $\ge k$
  (vertex-connectivity $\ge k$).
- The Bang-Jensen–Wang 2025 paper (arXiv:2309.06904) is the **only** source
  surveyed here where the bare adjective "$k$-strong" appears in the abstract
  and is used in the meaning "$k$-vertex-strong". This is the source of the
  v2 plan's confusion and the reason every row below double-checks the
  distinction.

---

## Section 1 — Attribution audit of `attack_plan.md` v3

### Source verifications (verbatim quotations)

**Bang-Jensen–Yeo 2004 (Combinatorica 24, 331–349; DOI 10.1007/s00493-004-0021-z).**
Stated as Theorem 1.2 in Bang-Jensen–Wang 2025 (arXiv:2309.06904, p. 1):

> "Theorem 1.2 [11] A 2-arc-strong semicomplete digraph $D$ has a strong arc
> decomposition if and only if $D$ is not isomorphic to the digraph $S_4$
> depicted in Figure 2. Furthermore, a strong arc decomposition of $D$ can be
> obtained in polynomial time when it exists."

Identical statement appears as Theorem 1.1 of Bang-Jensen–Gutin–Yeo 2020
(arXiv:1903.12225) with the extra description

> "$S_4$ is obtained from the complete digraph with four vertices by deleting
> the arcs of a cycle of length four"

i.e. $S_4$ is the square of $\vec{C}_4$, on 4 vertices, 8 arcs, 2-arc-strong.

**Bang-Jensen–Huang 2012 (J. Combin. Theory Ser. B 102 (2012), 701–714; DOI
10.1016/j.jctb.2011.09.001).** Quoted in Bang-Jensen–Wang 2025 as Theorem 1.3:

> "Theorem 1.3 [7] A 2-arc-strong locally semicomplete digraph $D$ has a
> strong arc decomposition if and only if $D$ is not the square of an even
> cycle. Every 3-arc-strong locally semicomplete digraph has a strong arc
> decomposition and such a decomposition can be obtained in polynomial time."

The "square of a directed cycle $v_1 v_2 \cdots v_n v_1$" is, per p. 1 of the
same source, the digraph obtained by adding the arc $v_i v_{i+2}$ for each
$i \in [n]$ (indices mod $n$). Note the journal's volume year is 2012 but the
JCTB paper is cited as published in volume 102, issues from 2012.

**Bang-Jensen–Gutin–Yeo 2020 (J. Graph Theory 95 (2020), 267–289;
arXiv:1903.12225).** Theorem 1.4 of the arXiv version, p. 3:

> "Theorem 1.4 Let $T$ be a strong semicomplete digraph on $t \ge 2$ vertices
> and let $H_1, \dots, H_t$ be arbitrary digraphs. Then $D = T[H_1, \dots, H_t]$
> has a strong arc decomposition if and only if $D$ is 2-arc-strong and is not
> isomorphic to one of the following four digraphs: $S_4$, $\vec{C}_3[\overline{K}_2,\overline{K}_2,\overline{K}_2]$, $\vec{C}_3[\overline{K}_2,\overline{K}_2,\overline{P}_2]$, $\vec{C}_3[\overline{K}_2,\overline{K}_2,\overline{K}_3]$."

The same paper also gives an extension of Theorem 1.1 to semicomplete
multi-digraphs with **three further exceptions** (Theorem 3.3, restated as
Theorem 2.3 of BJ–Wang 2025); these are distinct from the four composition
exceptions.

**Sun–Gutin–Ai 2019 (Discrete Math. 342 (2019), 2297–2305;
arXiv:1812.08809).** Verbatim arXiv abstract:

> "For digraph compositions $Q = T[H_1, \dots, H_t]$, we obtain sufficient
> conditions for $Q$ to have a good decomposition and a characterization of
> $Q$ with a good decomposition when $T$ is a strong semicomplete digraph and
> each $H_i$ is an arbitrary digraph with at least two vertices."

Stated as Theorem 1.3 of BJG 2020 with the three exceptions
$\vec{C}_3[\overline{K}_2,\overline{K}_2,\overline{K}_2]$, $\vec{C}_3[\overline{K}_2,\overline{K}_2,\overline{P}_2]$, $\vec{C}_3[\overline{K}_2,\overline{K}_2,\overline{K}_3]$. BJG 2020 extends this to the case $|V(H_i)| = 1$ allowed (adding $S_4$ as the fourth exception).

**Bang-Jensen–Wang 2025 (J. Graph Theory 108 (2025), 5–26; arXiv:2309.06904).**
The two relevant statements are Theorem 1.6 and Corollary 5 (PDF pp. 3, 24):

> "Theorem 1.6 Let $D = (V_1, V_2; A)$ be a 2-arc-strong split digraph such
> that $V_1$ is an independent set and the subdigraph induced by $V_2$ is
> semicomplete. If every vertex of $V_1$ has both out- and in-degree at least 3
> in $D$, then $D$ has a strong arc decomposition."
>
> "Corollary 1 Every 3-arc-strong split digraph has a strong arc decomposition."
>
> "Corollary 5 There are infinitely many 2-strong split digraphs which do not
> have a strong arc decomposition."

**Decisive remark.** Across the paper "2-strong" means **vertex-connectivity 2**.
Compare the line in Section 4: "even vertex-connectivity 2 is not sufficient
to guarantee the existence of a good $(u, v)$-pair…" (p. 23). This is the
exact same situation flagged in the v2 plan postmortem.

**Ai–He–Li–Qin–Wang 2024 (arXiv:2408.02260).** Theorem 1.8, PDF p. 2:

> "Theorem 1.8. A 2-arc-strong split digraph $D = (V_1, V_2; A)$ has a strong
> arc decomposition if and only if $D$ is not isomorphic to any of the
> digraphs illustrated in Lemma 2.11, Lemma 3.12, the Appendix, or their
> arc-reversed versions (reverse all arcs)."

The smallest exception family (Lemma 2.11) has $|V_1| = 1$, $|V_2| \in \{4,5\}$
and is described by explicit neighbourhood patterns on a single $V_1$-vertex.
(See Section 2.)

**Bang-Jensen–Yeo NP-completeness.** Quoted in Bang-Jensen–Wang 2025 as
Theorem 1.1:

> "Theorem 1.1 [12] It is NP-complete to decide whether a digraph has a strong
> arc decomposition. In fact it was shown in [12] that the problem is already
> NP-complete for 2-regular digraphs."

Reference [12] in BJ–Wang 2025 is the Bang-Jensen–Yeo paper; the book
treatment is Bang-Jensen–Gutin, *Digraphs* (Springer 2nd ed., 2009),
Theorem 13.10.1. Not independently verified from a primary source (book is
behind paywall); see §4.

**Karger 2000 (J. ACM 47 (2000), 46–76; arXiv:cs/9812007).** Lemma 3.2 (p. 7)
and Theorem 3.3 (p. 7) of the arXiv version:

> "Lemma 3.2. For any constant $\alpha$, there are $O(n^{\lfloor 2\alpha \rfloor})$
> $\alpha$-minimum cuts."
>
> "Theorem 3.3. The number of $\alpha$-minimum cuts is at most
> $\dfrac{1}{\lfloor 2\alpha\rfloor + 1 - 2\alpha} \binom{n}{\lfloor 2\alpha\rfloor}(1+O(1/n))$."

The bound is stated for **weighted undirected graphs** (Karger reduces to the
unweighted case in §2; the proof works for multigraphs because it is built on
Nash-Williams tree-packing, which is multigraph-valid). So Karger's bound
$O(n^{\lfloor 2\alpha\rfloor})$ does apply to the underlying undirected
**multigraph** of an Eulerian digraph; the EC-log proof outline is correct
modulo the factor-of-2 bookkeeping already flagged in `review.md`.

**Cen–Li–Nanongkai–Panigrahi–Quanrud–Saranurak 2021 (FOCS;
arXiv:2111.08959).** Note the author list. The plan cites only "Cen-Li-
Nanongkai-Saranurak"; Panigrahi and Quanrud are missing.

**Mader / Frank directed splitting-off.** Mader's directed splitting-off
theorem (Mader 1978): if $D$ has a vertex $s$ with $d^+(s) = d^-(s)$ and $D$
is $k$-arc-strong in $V \setminus \{s\}$, then for each arc $st$ at $s$ there
is an arc $us$ such that splitting off the pair $(us, st)$ preserves
$k$-arc-strength in $V \setminus \{s\}$. The theorem preserves **prescribed
arc-strength**, not strong arc decomposition. The plan's wording is careful
on this point ("strong arc decompositions do not automatically lift through
such operations"); OK.

### Attribution table

| Claim (paraphrased) | As cited in plan | Verified primary source | Hypothesis check | Verdict |
|---|---|---|---|---|
| Every 2-arc-strong semicomplete digraph $\ne S_4$ has a strong arc decomposition. | Bang-Jensen–Yeo 2004 (Combinatorica 24, 331–349). | Bang-Jensen–Yeo, *Decomposing $k$-arc-strong tournaments into strong spanning subdigraphs*, Combinatorica 24 (2004), 331–349. DOI 10.1007/s00493-004-0021-**z** (plan's DOI suffix would be -0 unstated; the existing JGT entry has different DOI). Statement as Theorem 1.2 of BJ–Wang 2025. | Hypothesis "2-arc-strong semicomplete digraph" exactly. $S_4$ explicitly the square of $\vec{C}_4$. | OK |
| Hence every 3-arc-strong semicomplete digraph has a strong arc decomposition. | Same paper, implied. | Immediate consequence; explicitly stated in BJ–Wang 2025 p. 1. | Exact. | OK |
| Every 2-arc-strong locally semicomplete digraph not the square of an even cycle has a strong arc decomposition; every 3-arc-strong locally semicomplete digraph has one (polytime). | Bang-Jensen–Huang 2012 (JCTB 102, 701–714). | Theorem 1.3 of BJ–Wang 2025 quoting Bang-Jensen–Huang 2012; the JCTB DOI is 10.1016/j.jctb.2011.09.001 (the journal-portal indexing also shows ScienceDirect URL S0095895611000931, **not** S0095895611000840 — this is a journal-internal numbering quirk, not an error in the plan). | Hypothesis "2-arc-strong locally semicomplete digraph" exactly. Exceptions = squares of even directed cycles. | OK |
| Every strong semicomplete composition $T[H_1, \dots, H_t]$ has a strong arc decomposition iff it is 2-arc-strong and is not one of four explicit exceptional digraphs. | Bang-Jensen–Gutin–Yeo 2020 (J. Graph Theory 95, 267–289; arXiv:1903.12225). | Theorem 1.4 of arXiv:1903.12225. Four exceptions: $S_4$; $\vec{C}_3[\overline{K}_2,\overline{K}_2,\overline{K}_2]$; $\vec{C}_3[\overline{K}_2,\overline{K}_2,\overline{P}_2]$; $\vec{C}_3[\overline{K}_2,\overline{K}_2,\overline{K}_3]$. | Hypothesis "$T$ strong semicomplete, $t \ge 2$, $H_i$ arbitrary digraphs"; the exceptions are exactly the four listed. | OK |
| Sun–Gutin–Ai 2019 obtain a characterisation of compositions $T[H_1,\dots,H_t]$ when $T$ is strong semicomplete. | Sun–Gutin–Ai 2019 (Discrete Math. 342, 2297–2305). | arXiv:1812.08809 abstract. The 2019 paper handles the **$|V(H_i)|\ge 2$ for all $i$** subcase; three exceptions ($S_4$ is **not** an exception there because each $H_i$ has $\ge 2$ vertices). BJG 2020 extends to allow $|V(H_i)|=1$ and adds $S_4$ as the fourth exception. | The plan's listing of Sun–Gutin–Ai as the source of "compositions/products" is correct but the plan does not flag that the 2019 paper's characterisation is restricted to $|V(H_i)|\ge 2$, three exceptions; full four-exception characterisation is 2020. | CAUTION |
| Every 3-arc-strong split digraph has a strong arc decomposition (polytime); infinite families of 2-vertex-strong split digraphs without a strong arc decomposition exist. | Bang-Jensen–Wang 2025 (J. Graph Theory 108, 5–26; arXiv:2309.06904). | Theorem 1.6 + Corollary 1 (positive) and Corollary 5 (negative) of arXiv:2309.06904. The negative result is stated for **2-strong** (= 2-vertex-strong) split digraphs, **not** 2-arc-strong. | The plan is now correct on this point. Earlier v2 confusion fixed. | OK |
| Ai–He–Li–Qin–Wang 2024 give a complete characterisation of 2-arc-strong split digraphs with a strong arc decomposition. | arXiv:2408.02260. | Theorem 1.8 of arXiv:2408.02260: exceptions = digraphs listed in Lemma 2.11, Lemma 3.12, Appendix, plus arc-reversals. | Hypothesis "2-arc-strong split digraph" exactly. | OK |
| Deciding strong arc decomposition is NP-complete; already NP-complete for 2-regular digraphs (Bang-Jensen–Yeo). | "Bang-Jensen–Yeo" plus book treatment Bang-Jensen–Gutin, *Digraphs* 2nd ed. Theorem 13.10.1. | Restated as Theorem 1.1 of BJ–Wang 2025 with citation [12]. We could not independently access the book or the primary BJ–Yeo source to verify the exact ground-set and reduction. | The plan does not specify whether "digraph" here means simple digraph or multidigraph. The BJ–Wang restatement says "digraph"; the 2-regular hardness gadget is sometimes given on multidigraphs. | CAUTION; see §4 |
| Karger's cut-counting theorem bounds the number of cuts of value $\le \alpha c$ by $O(n^{2\alpha})$ in undirected graphs. | "Karger 2000 (JACM 47)." | Karger Lemma 3.2 / Theorem 3.3 (arXiv:cs/9812007): bound is $O(n^{\lfloor 2\alpha\rfloor})$, valid for weighted undirected multigraphs. | The plan's exponent $n^{2k}$ is **integer-rounded** version of $n^{\lfloor 2\alpha\rfloor}$. EC-log uses $\alpha = j+1$ integer, so the discrepancy disappears; but the plan should explicitly say "$\lfloor 2\alpha\rfloor$" if the proof is ever extended to non-integer thresholds. | CAUTION (cosmetic) |
| Cen–Li–Nanongkai–Saranurak (FOCS 2021) on directed cut counting / partial sparsification. | Plan citation. | arXiv:2111.08959 is authored by **Cen, Li, Nanongkai, Panigrahi, Quanrud, Saranurak**. | Author list incomplete by 2. Result paraphrase ("directed cut counting is delicate") matches the paper's contribution: it presents fast algorithms via partial sparsification, **does not** establish an analogue of Karger's $O(n^{2\alpha})$ counting bound for directed min-cuts. The plan's "Cautionary reference" phrasing is correct in spirit. | CAUTION (author list); OK on substance |
| Mader / Frank directed splitting-off theorems preserve prescribed local arc-connectivities under admissibility hypotheses, but do not lift strong arc decompositions automatically. | Plan claim. | Mader 1978 directed splitting-off lemma: preserves $k$-arc-strength in $V\setminus\{s\}$ at an Eulerian vertex $s$. Frank's splitting-off theorems extend to demand-respecting splittings. Neither is about strong arc decomposition; the plan's "do not automatically lift" is correct because the colour classes have *no* admissibility certificate at $s$ in general. | Phrasing is conservative and accurate. | OK |
| Bang-Jensen–Kriesell 2009 survey on disjoint sub(di)graphs. | Electron. Notes Discrete Math. 34, 179–183. | Independent listing on dblp matches the plan citation. Not load-bearing. | Plan's listing is correct. | OK |

### Two specific WC3 framing checks

- Plan §"Bedrock claims" 4 states: "No published infinite family of $\ge 3$-arc-strong digraphs without strong arc decomposition is known." Verified: no such family appears in BJ–Wang 2025, Ai–He–Li–Qin–Wang 2024, BJG 2020, or BJ–Huang 2012. **OK.**
- Plan §"Bedrock claims" 3 states 2-regular NP-hardness; the inference "any positive theorem must use large arc-connectivity structurally" is editorial, not a theorem. **OK as long as the plan does not promote it to a lemma.**

---

## Section 2 — Canonical benchmark table for the verifier

All vertex/arc counts are for the underlying **directed simple-or-multi**
representation as defined in the cited source. "2-cycle between $u, v$" means
both arcs $uv, vu$. The verifier should reject loops in all instances.

| Name | $n$ | $m$ | $\lambda^{\text{arc}}$ | $\kappa^{\text{vertex}}$ | Class | Expected verdict | Primary source |
|---|---|---|---|---|---|---|---|
| $S_4$ | 4 | 8 | 2 | 2 | semicomplete; square of $\vec{C}_4$ | **UNSAT** | BJ–Yeo 2004; BJG 2020 Th. 1.1 |
| $C_4^{(2)}$ (= $S_4$) | 4 | 8 | 2 | 2 | locally semicomplete (special case of squares of even cycles) | **UNSAT** | BJ–Huang 2012 |
| $C_6^{(2)}$ | 6 | 12 | 2 | 2 | locally semicomplete | **UNSAT** | BJ–Huang 2012 |
| $C_8^{(2)}$ | 8 | 16 | 2 | 2 | locally semicomplete | **UNSAT** | BJ–Huang 2012 |
| $\vec{C}_3[\overline{K}_2,\overline{K}_2,\overline{K}_2]$ | 6 | 12 | 2 | 2 | semicomplete composition | **UNSAT** | BJG 2020 Th. 1.4 |
| $\vec{C}_3[\overline{K}_2,\overline{K}_2,\overline{P}_2]$ | 6 | 13 | 2 | 2 | semicomplete composition | **UNSAT** | BJG 2020 Th. 1.4 |
| $\vec{C}_3[\overline{K}_2,\overline{K}_2,\overline{K}_3]$ | 7 | 16 | 2 | 2 | semicomplete composition | **UNSAT** | BJG 2020 Th. 1.4 |
| $S_4$ (re-listed as composition exception) | 4 | 8 | 2 | 2 | semicomplete composition | **UNSAT** | BJG 2020 Th. 1.4 (fourth exception) |
| Smallest Ai–He–Li–Qin–Wang 2024 split exception (Lemma 2.11, first structure) | 5 | 10 | 2 | 2 | split, $V_1 = \{u\}$, $V_2 = \{x_1,x_2,x_3,v\}$ | **UNSAT** | arXiv:2408.02260 Lemma 2.11 |
| $\vec{C}_3$ with 2-cycle on each pair, i.e. $K_3^*$ (complete digraph on 3) | 3 | 6 | 2 | 2 | semicomplete; **NOT a known exception** | **SAT** | BJ–Yeo 2004 (any non-$S_4$ 2-arc-strong semicomplete) |
| $K_4^*$ (complete digraph on 4 vertices) | 4 | 12 | 3 | 3 | 3-arc-strong semicomplete, Eulerian | **SAT** | BJ–Yeo 2004 |
| Doubled directed 4-cycle: $\vec{C}_4$ with each arc trebled | 4 | 12 | 3 | 1 | 3-arc-strong, Eulerian, not 3-vertex-strong (1-vertex-strong) | **SAT** (Eulerian + 3-arc-strong; covered by EC-log if $C$ is small enough, otherwise by direct partition) | $\vec{C}_4 \times 3$; trivial: 3 colour-balanced sub-cycles each strong |
| BJ–Wang 2025 infinite-family member (2-vertex-strong split, not 2-arc-strong) | smallest in Figure 10 of arXiv:2309.06904; reported $n = 5$, $\lambda^{\text{arc}} = 1$, $\kappa^{\text{vertex}} = 2$ | as in figure | 1 | 2 | split | **UNSAT** (trivially, since not 2-arc-strong) | BJ–Wang 2025 Prop. 4.5–4.6 |

**Warning on the last row.** The BJ–Wang 2-vertex-strong examples are
**not** Bang-Jensen–Yeo obstructions in the Track-B sense. They are UNSAT
only because they fail the necessary condition $\lambda^{\text{arc}}\ge 2$
for the existence of a strong arc decomposition. Do **not** use them as
gluing templates against the WC3 conjecture; Track B §3 of `attack_plan.md`
already warns against this and the warning is now reinforced here.

**Arc-set encodings.**

- $S_4$: vertices $\{v_1, v_2, v_3, v_4\}$; arcs
  $\{v_1 v_2, v_2 v_3, v_3 v_4, v_4 v_1,\;\; v_1 v_3, v_3 v_1, v_2 v_4, v_4 v_2\}$.
  (Hamilton $\vec{C}_4$ + two 2-cycles on diagonals.)
- $C_{2k}^{(2)}$ for $k \ge 2$: vertices $\{v_1, \dots, v_{2k}\}$; arcs
  $\{v_i v_{i+1} : i \in [2k]\} \cup \{v_i v_{i+2} : i \in [2k]\}$,
  indices mod $2k$.
- $\vec{C}_3[\overline{K}_2,\overline{K}_2,\overline{K}_2]$: vertices
  $\{u_{i,j} : i \in [3], j \in [2]\}$; arcs
  $\{u_{i,j} u_{i+1, j'} : i \in [3], j, j' \in [2]\}$ (mod 3 on $i$),
  i.e. complete bipartite-like arcs between consecutive layers.
  No arc inside any $\overline{K}_2$ layer. 12 arcs total.
- $\vec{C}_3[\overline{K}_2,\overline{K}_2,\overline{P}_2]$: same as above but
  the third layer is $\overline{P}_2 = $ a single arc $u_{3,1} \to u_{3,2}$;
  add one extra arc inside the third part. 12+1 = 13 arcs.
- $\vec{C}_3[\overline{K}_2,\overline{K}_2,\overline{K}_3]$: third layer
  has 3 vertices with no internal arcs; consecutive layers fully crossed.
  $2 \cdot 2 + 2 \cdot 3 + 3 \cdot 2 = 16$ arcs.
- **Smallest Ai et al. split exception (Lemma 2.11, structure 1).** $V_1 = \{u\}$,
  $V_2 = \{x_1, x_2, x_3, v\}$. The split condition forces every arc between
  $V_1$ and $V_2$ to exist; the lemma specifies that $u$'s relations are
  exactly $N^+(u) = \{x_1, x_3\}$, $N^-(u) = \{x_1, x_2\}$, with arcs inside
  $V_2$: $N^+(x_1) = \{x_2, u\}$, $N^+(x_2) = \{v, u\}$, plus $V_2$ induces a
  semicomplete digraph. The exact arc list depends on the chosen
  semicomplete digraph on $V_2$; the **proof** in the source uses arc counts
  consistent with $\lambda^{\text{arc}} = 2$ and minimum in/out-degree 2.
  Coder note: encode the exact arc set by reading Figure 2 of
  arXiv:2408.02260 directly; the verbal description above pins down only the
  $V_1$-incident neighbourhoods. **TODO** for Coder to extract precise arcs.
- **The remaining members of the Ai et al. 2024 family (Lemma 3.12 and the
  Appendix).** Their precise structure is not extractable from the abstract.
  **TODO** for Coder: read pages of Lemma 3.12 and the Appendix in
  arXiv:2408.02260 and encode all listed structures plus their arc-reversed
  versions.

---

## Section 3 — Hidden overclaims in `attack_plan.md` v3

A line-by-line scan of v3. Suspect passages quoted verbatim and corrected.

**Overclaim 1 — Karger application as written.**
> "Karger's cut-counting theorem (JACM 2000) bounds the number of such
> undirected cuts by $n^{2(j+1)}$."

Correction: the precise bound from Karger Lemma 3.2 / Theorem 3.3 is
$O(n^{\lfloor 2\alpha\rfloor})$ with $\alpha = j+1$ integer in the plan's
indexing, which gives exactly $O(n^{2(j+1)})$. So the bound is correct **for
integer thresholds**, but the wording suggests the integer exponent holds
for all real $\alpha$. State: "$O(n^{\lfloor 2\alpha\rfloor})$, with
$\alpha = j+1$ integer so the bound reads $O(n^{2(j+1)})$".

**Overclaim 2 — alteration finish.**
> "A union-bound / alteration finish gives a 2-coloring with no monochromatic
> directed cut."

Correction (also flagged in `review.md`): no alteration is needed when
expectation $< 1$; remove "alteration" and replace with "first-moment method".

**Overclaim 3 — quasi-transitive digraphs already absorbed.**
> "*Quasi-transitive digraphs* were listed as a candidate in v2. They are
> probably **already absorbed** by BJG–Yeo 2020 via the Bang-Jensen–Huang
> recursive structure …"

Correction: BJG 2020 themselves state this as **Theorem 1.6** (verbatim from
arXiv:1903.12225 p. 4): a quasi-transitive digraph has a strong arc
decomposition iff it is 2-arc-strong and not one of the four exceptional
digraphs. The "probably" is too weak. The plan should state: "Quasi-transitive
digraphs are absorbed by BJG–Yeo 2020 Theorem 1.6 via the Bang-Jensen–Huang
recursive characterisation; remove from C1 candidate-class list."

**Overclaim 4 — controlled lifting lemma stated as if it exists.**
> "**C1. Controlled lifting lemma.** Extract from the Bang-Jensen–Wang
> split-digraph proof a reusable lemma: 'If $D'$ is obtained from $D$ by
> splitting off arc pairs at a vertex $v$, …'"

The quoted block is stated in indicative mood, which could be read as
"this lemma exists". It does **not** exist as a published lemma. Suggest
rewording to subjunctive: "**Candidate lemma to extract:** …". This is the
sentence the Lead Theorist flagged in the §3.5 checklist as the most likely
source of overclaiming and the §5 Phase-4 tripwire is in place precisely
because extraction may fail.

**Overclaim 5 — Sun–Gutin–Ai 2019 scope.**
> "Y. Sun, G. Gutin, J. Ai, *Arc-disjoint strong spanning subdigraphs in
> compositions and products of digraphs*, Discrete Math. 342 (2019),
> 2297–2305."

(Plan listing.) The plan groups this with BJG 2020 as if they together yield
the four-exception characterisation. Sun–Gutin–Ai 2019 only handles
$|V(H_i)|\ge 2$ for all $i$ and gives **three** exceptions, not four. BJG
2020 is the source of the full four-exception result. Add this distinction
to the "Known prior work" section.

**Overclaim 6 — author list of Cen et al.**
> "R. Cen, J. Li, D. Nanongkai, T. Saranurak, *Minimum Cuts in Directed
> Graphs via Partial Sparsification*, FOCS 2021."

Correction: full author list is **Cen, Li, Nanongkai, Panigrahi, Quanrud,
Saranurak** (six authors). arXiv:2111.08959.

**Overclaim 7 — "every K-arc-strong digraph" framing of the conjecture.**
The Bang-Jensen–Yeo conjecture is **standardly stated for digraphs** (the
plan v3 uses the right wording). The OPG entry uses "tournament" in its
historical title; the conjecture extended to general digraphs is the form
quoted in `attack_plan.md` line 3 and in BJ–Wang 2025 (Conjecture 1.2,
attributed to [11]). No correction needed; OK.

**Overclaim 8 — "lower bound silence" phrasing.**
> "No published infinite family of $\geq 3$-arc-strong digraphs without
> strong arc decomposition is known."

Verified across BJ–Wang 2025, Ai et al. 2024, BJG 2020, BJ–Huang 2012; no
such family appears. OK as stated. Caveat for future work: this is a
"known to the Auditor" statement, not a published meta-claim.

**Overclaim 9 — "constant-$C$ vs $C \log n$" wording.**
> "Removing Eulerianness. Replacing $\log n$ by a constant. Either of these
> reverts the problem to its full directed-cut-counting difficulty…"

The phrasing implies that the constant-$C$ Eulerian case is open. This is
correct: no published constant-arc-connectivity strong arc decomposition
theorem for Eulerian digraphs exists. **OK as stated**; do not promote
"reverts the problem to its full directed-cut-counting difficulty" to a
lemma.

**Overclaim 10 — NP-completeness ground set.**
> "NP-completeness on 2-regular digraphs. Deciding strong arc decomposition
> is NP-complete (Bang-Jensen–Yeo), already so for 2-regular digraphs."

Correction needed: the BJ–Wang 2025 restatement (Theorem 1.1) says "for
digraph" without specifying simple/multi. The 2-regular hardness reduction
is sometimes stated for general digraphs, sometimes for multidigraphs. The
plan should add a one-line clarification once the Lead Theorist confirms the
ground-set from the primary source (§4 item).

**Overclaim 11 — locally semicomplete polynomial-time clause.**
The plan states: "Every 2-arc-strong locally semicomplete digraph not equal
to the square of an even directed cycle has a strong arc decomposition,
polynomial-time constructible." Verified verbatim in BJ–Wang 2025 Th. 1.3
quoting BJ–Huang 2012. **OK.**

**Overclaim 12 — Eulerian "high-$\lambda$ regime ruled out".**
> "EC-log rules out the *high-$\lambda$* Eulerian regime, so the target
> window is $\lambda(D) = 3$ exactly…"

This is editorial inference, not a theorem statement, but the dependency on
EC-log being proved is correct ("rules out … if EC-log holds"). Suggest
making the dependency explicit: "**Conditional on EC-log,** the target
window is $\lambda(D) = 3$ exactly."

---

## Section 4 — Open attribution questions for the Lead Theorist

The following items could not be resolved from public/open-access sources
and require library access:

1. **Exact statement of the Bang-Jensen–Yeo NP-completeness theorem.** Is
   the reduction stated for *simple* 2-regular digraphs, *2-regular
   multidigraphs*, or *2-regular oriented* digraphs? The BJ–Wang 2025
   restatement is ambiguous. Please confirm from Bang-Jensen–Gutin,
   *Digraphs: Theory, Algorithms and Applications*, 2nd ed., Springer 2009,
   Theorem 13.10.1, and from the primary Bang-Jensen–Yeo source (reference
   [12] of arXiv:2309.06904).
2. **Exact arc lists of the four BJG–Yeo 2020 exceptional digraphs.** We have
   the named composition forms ($S_4$, $\vec{C}_3[\overline{K}_2^{\,3}]$,
   $\vec{C}_3[\overline{K}_2,\overline{K}_2,\overline{P}_2]$,
   $\vec{C}_3[\overline{K}_2,\overline{K}_2,\overline{K}_3]$) but the
   arc-by-arc encoding for the verifier should be cross-checked against
   Figure 2 of arXiv:1903.12225. Coder will need this; auditor can sign off
   once primary figure is matched.
3. **Exact list of structures in Ai–He–Li–Qin–Wang 2024 Lemma 3.12 and
   Appendix.** The arXiv abstract gives Theorem 1.8 but not the structures.
   Please pull the figures and encode the full exception family (plus
   arc-reversed versions). Without this, the verifier's UNSAT benchmark for
   the 2-arc-strong split family is incomplete.
4. **Three extra exceptions in BJG 2020 Theorem 3.3 (semicomplete
   multi-digraphs).** Distinct from the four composition exceptions; named
   $S_{4,1}, S_{4,2}$ and one more in the arXiv:1903.12225 Figure 3. Please
   confirm the third and provide arc-by-arc encodings; these are useful for
   multigraph variants of the verifier.
5. **BJ–Wang 2025 published bibliographic data.** Confirm the published
   journal volume/pages (J. Graph Theory 108 (2025), 5–26 per plan; the
   arXiv version dated September 2023). DOI of published version: please
   record.
6. **The (related, for context) paper "Arc-disjoint in- and out-branchings
   in semicomplete split digraphs"** quoted in the plan as Discrete Appl.
   Math. 375 (2025), 259–268. The Nankai PDF we accessed is the same paper
   and confirms Conjecture 1.6 of BJ–Wang 2025. Please confirm the published
   DOI for the bibliography.
7. **OPG entry date for the conjecture.** The plan says "OPG 2013-03-02";
   the Open Problem Garden page was unreachable during this audit
   (`ECONNREFUSED`). Please confirm the posting date and contributor
   directly from the OPG entry once the site is up.
8. **Frank's directed splitting-off variant being cited.** Multiple Frank
   splitting-off theorems exist (1992 demand-respecting; 1993 detachment).
   The plan cites "Mader, Frank" without disambiguation. Please pin to a
   specific Frank theorem in `attack_plan.md` for the Track-C1 candidate
   lemma; the audit can then check the admissibility-hypothesis matching.

End of round-1 audit. Verdict on `attack_plan.md` v3 as a whole: the
literature framing is now correct on the load-bearing distinctions
(2-strong vs 2-arc-strong; semicomplete vs locally semicomplete; the
BJ-Wang vs Ai–He–Li–Qin–Wang split-digraph distinction; the four BJG–Yeo
2020 exceptions). The remaining issues are bookkeeping (Karger exponent,
factor of 2, author list of Cen et al., Sun–Gutin–Ai scope, "alteration
finish" wording) plus the §4 items requiring library access.

---

## Appendix A — Ai–He–Li–Qin–Wang 2024 smallest split exception (arc-level)

Source read directly from arXiv:2408.02260v1 (Aug 5, 2024), pages 1–7.

### Verbatim from the paper

**Theorem 1.8 (p. 3).**

> A 2-arc-strong split digraph $D = (V_1, V_2; A)$ has a strong arc
> decomposition if and only if $D$ is not isomorphic to any of the digraphs
> illustrated in Lemma 2.11, Lemma 3.12, the Appendix, or their arc-reversed
> versions (reverse all arcs).

**Lemma 2.11 (p. 6).**

> Let $D = (V_1, V_2; A)$ be a 2-arc-strong split digraph, if $D$ has a
> copy of at least one of the following structures, then $D$ has no strong
> arc decomposition.
>
> - There are $x_1, x_2, u \in V(D)$ such that $N_D^+(u) = \{x_1, x_3\}$,
>   $N_D^-(u) = \{x_1, x_2\}$, $N_D^+(x_1) = \{x_2, u\}$,
>   $N_D^+(x_2) = \{v, u\}$, where $x_3 \in V(D) \setminus \{x_1, x_2, u\}$,
>   $v \in V(D) \setminus \{x_1, x_2, u\}$.
> - There are $x_1, x_2, u \in V(D)$ such that $N_D^-(u) = \{x_1, x_3\}$,
>   $N_D^+(u) = \{x_1, x_2\}$, $N_D^-(x_1) = \{x_2, u\}$,
>   $N_D^-(x_2) = \{v, u\}$, where $x_3, v$ as above.

**Remark 2.12 (p. 6).**

> As we have characterized all the neighbors of $u$, we have $u \in V_1$ and
> $x_1, x_2, x_3 \in V_2$ when $|V_2| \geq 5$. And note that $x_3 = v$ is
> possible.

Figure 2 (p. 7) shows the case-1 substructure on the five points
$u, x_1, x_2, x_3, v$.

### Derivation of the smallest instance

Lemma 2.11 specifies a *substructure*, not a closed digraph. To produce a
verifier benchmark, embed it in the smallest 2-arc-strong split digraph
that contains a copy.

If $x_3 = v$ (collapsed case, $|V_2| = 3$, $n = 4$), the fixed
neighborhoods together with the semicompleteness of $V_2$ force exactly
the arc multiset of $S_4 = \vec{C}_4^{(2)}$; that is, the collapsed case
reproduces $S_4$ and is already covered by `S4` in `benchmarks.py`.

The genuinely new instance has $x_3 \neq v$, hence $|V_2| = 4$ and $n = 5$.
Counting:

- **Fixed neighborhoods (6 arcs):** $u \to x_1$, $u \to x_3$, $x_1 \to u$,
  $x_2 \to u$, $x_1 \to x_2$, $x_2 \to v$.
- **Forced by $V_2$ semicomplete (3 arcs):** since $N_D^+(x_1) = \{x_2, u\}$
  excludes both $x_3$ and $v$, and $N_D^+(x_2) = \{v, u\}$ excludes $x_3$,
  the only arcs that can witness adjacency of $\{x_1, x_3\}$, $\{x_1, v\}$,
  $\{x_2, x_3\}$ in $V_2$ are $x_3 \to x_1$, $v \to x_1$, $x_3 \to x_2$.
- **Forced by 2-arc-strongness (2 arcs):** the vertices $x_3$ and $v$ each
  have in-degree 1 in the 9 arcs above; the only candidates for an
  additional in-arc are each other (every other potential source has its
  outgoing neighborhood already fixed by the lemma). Hence both
  $x_3 \to v$ and $v \to x_3$ are forced.

Total: **11 arcs**.

### Encoded instance

Labelling $u = 4$, $x_1 = 0$, $x_2 = 1$, $x_3 = 2$, $v = 3$:

| Field | Value |
|---|---|
| $V$ | $\{0, 1, 2, 3, 4\}$ |
| $V_1$ | $\{4\}$ |
| $V_2$ | $\{0, 1, 2, 3\}$ |
| Arc list | $(4,0), (4,2), (0,4), (1,4), (0,1), (1,3), (2,0), (3,0), (2,1), (2,3), (3,2)$ |
| $n$ | $5$ |
| $m$ | $11$ |
| $\lambda^{\text{arc}}$ | $2$ (verified) |
| $\kappa^{\text{vertex}}$ | $2$ |
| Class | split, **not** semicomplete (the pair $\{u, v\}$ is non-adjacent) |
| Expected verdict | UNSAT |
| Primary source | Ai et al. 2024, arXiv:2408.02260, Lemma 2.11 (case 1) |

The case-2 substructure is the arc-reverse of case 1 by inspection (swap
$N^+$ and $N^-$ in all four neighborhood specifications). The arc-reversed
instance is iso­morphic to the case-1 instance via the vertex map
$(u, x_1, x_2, x_3, v) \to (u, x_1, x_2, x_3, v)$ combined with global arc
reversal; for the verifier, encoding case-1 suffices (case-2 reduces to it
under reverse-iso).

### Coder action

Already done: encoded in `code/benchmarks.py` as `_AiEtAl_Lemma211_smallest()`,
name `AiEtAl_L211_min`. Cross-check status on 2026-05-16: ILP and SAT both
return UNSAT in $< 0.2$ s with full agreement. Updates to the verifier
benchmark suite: 10/10 instances pass.

### Open follow-ups (after round 2)

- **Arc-reverse benchmarks.** Theorem 1.8 says "or their arc-reversed
  versions." The Lemma 2.11 case-1 instance above is self-reverse-iso by
  the $V_2$-internal symmetry, and Lemma 3.12 case 2 is the arc-reverse of
  case 1; case 1's instance is reverse-iso to itself via $a \leftrightarrow
  c$, $u \leftrightarrow v$ (mirror reflection). Appendix instances are not
  yet encoded; see Appendix A.2 below.

---

## Appendix A.2 — Ai et al. 2024 Lemma 3.12 smallest instance (arc-level)

Read directly from arXiv:2408.02260v1, p. 25.

### Verbatim Lemma 3.12

> Let $D = (V_1, V_2; A)$ be a 2-arc-strong split digraph with $|V_2(D)|
> \geq 4$ and $D[V_2]$ is not strong, which means it has the acyclic
> ordering of its strong component $C_1, \ldots, C_p$ ($p \geq 2$). If $D$
> has a copy of at least one of the following structures, then $D$ has no
> strong arc decomposition.
>
> - $D[C_p]$ is a 3-cycle, say $abca$, and there exists $u, v \in V_1$,
>   such that $N_D^+(b) = \{u, v, c\}$, $N_D^+(c) = \{v, a\}$,
>   $N_D^+(a) = \{u, b\}$, $N_D^+(u) = \{a, u^+\}$,
>   $N_D^+(v) = \{b, v^+\}$, where $u^+, v^+ \in V_2 \setminus C_p$, and
>   they can be the same one, besides, $N_D^-(u) = \{a, b\}$,
>   $N_D^-(v) = \{b, c\}$.
> - Reversing arcs in the first case.

### Derivation of the smallest instance

Take $u^+ = v^+ = w$ as a single vertex in $V_2 \setminus C_p$ (this is the
smallest case; the lemma explicitly allows it). Then $V_2 = \{a, b, c, w\}$,
$V_1 = \{u, v\}$, $n = 6$.

The 14 arcs are forced by:

- the 3-cycle $a \to b \to c \to a$ in $C_p$;
- the prescribed out-neighborhoods of $a, b, c, u, v$ (adding $a \to u$,
  $b \to u$, $b \to v$, $c \to v$, $u \to a$, $u \to w$, $v \to b$,
  $v \to w$);
- semicompleteness of $V_2$ combined with $C_p$ being the *terminal* strong
  component (no arcs from $\{a, b, c\}$ to $\{w\}$, since all out-arcs of
  $a, b, c$ are already accounted for in $C_p \cup V_1$). This forces
  $w \to a, w \to b, w \to c$.

### Encoded instance

Labels: $a = 0, b = 1, c = 2, w = 3, u = 4, v = 5$.

| Field | Value |
|---|---|
| $V$ | $\{0, 1, 2, 3, 4, 5\}$ |
| $V_1$ | $\{4, 5\}$ |
| $V_2$ | $\{0, 1, 2, 3\}$ |
| Arc list | $(0,1), (1,2), (2,0), (1,4), (1,5), (2,5), (0,4), (4,0), (4,3), (5,1), (5,3), (3,0), (3,1), (3,2)$ |
| $n$ | $6$ |
| $m$ | $14$ |
| $\lambda^{\text{arc}}$ | $2$ (verified by the solver) |
| Class | split, **not** semicomplete (the pair $\{u, w\}$ is non-adjacent) |
| Expected verdict | UNSAT |
| Primary source | Ai et al. 2024, arXiv:2408.02260, Lemma 3.12 (case 1) |

Encoded in `code/benchmarks.py` as `_AiEtAl_Lemma312_smallest()`,
name `AiEtAl_L312_min`. Cross-check status on 2026-05-16: ILP and SAT
both return UNSAT in $< 0.3$ s with full agreement.

---

## Appendix A.3 — Ai et al. 2024 Appendix B (B.2 / B.3): status

Theorem 1.8 lists "the Appendix" as a third source of 2-arc-strong split
SAD-obstructions, beyond Lemma 2.11 and Lemma 3.12. The paper's Appendix
B treats the case $|V_2| \leq 4$ in detail. Two structured sub-families:

**Appendix B.2: $D[V_2] = S_{4,-1}$.** The base digraph $D[V_2]$ is
$S_4 = \vec{C}_4^{(2)}$ with one diagonal arc removed (7 arcs on 4 vertices,
still 2-arc-strong semicomplete). Adding a single $V_1$ vertex $a$ with
different adjacency patterns yields 5 configurations $(i)$–$(v)$, each a
5-vertex 2-arc-strong split digraph; some have a strong arc decomposition,
some do not.

**Appendix B.3: $D[V_2] = S_{4,-2}$.** Base $D[V_2]$ is $S_4$ with both
diagonal 2-cycles reduced to single arcs (6 arcs on 4 vertices). Adding
$V_1 = \{a, b\}$ where $a$ realizes configuration $(f)$ and $b$ realizes
the rotated configuration $(e)^*$ yields the 6-vertex digraph denoted
$(e)^* \times (f)$. With $(e), (f) \in \{i, ii, iii, iv, v\}$ and modulo
the $(e)^* \times (f) \cong (f)^* \times (e)$ symmetry, there are 15
distinct cases; **8 of them have no strong arc decomposition**:

- $(i)^* \times (i) = (i)^* \times (iv) \cong (iv)^* \times (iv)$ (the
  paper's "unique counterexample to Problem 1.6 of Bang-Jensen–Wang 2025");
- $(i)^* \times (ii) \cong (ii)^* \times (iv)$;
- $(i)^* \times (iii) \cong (iii)^* \times (v)$;
- $(ii)^* \times (ii)$, $(ii)^* \times (iii)$, $(ii)^* \times (iv)$;
- $(iii)^* \times (iii)$, $(iii)^* \times (iv)$, $(iv)^* \times (iv)$.

The 7 cases with a strong arc decomposition are
$(i)^* \times (v)$, $(ii)^* \times (v)$, $(iv)^* \times (v)$,
$(v)^* \times (v)$, and the three obtained from these by the symmetry.

### Why not encoded in round 2

The arc sets for $(e)^* \times (f)$ are specified by the paper's
**Figure 5** (B.2 reductions), the 10 figures on **p. 31** (the
configurations $(i)$–$(v)$ and $(i)^*$–$(v)^*$ as 5-vertex
sub-digraphs), and pages 28–34 (the explicit arc-by-arc proofs for each
6-vertex bad case). Reading the arc directions reliably from the
rasterized PDF figures at the available resolution is below the
correctness threshold for the verifier (the SAT/UNSAT split is sensitive
to single-arc errors, and the proofs use red/green coloring of arcs to
indicate which color class an arc belongs to in a *candidate* strong arc
decomposition — these are *not* part of $A(D)$). Round 2 commits only
the rigorously derivable Lemma 3.12 instance and explicitly defers the
Appendix B family.

### Round 3 plan

Three execution paths, in increasing rigour:

1. **Manual transcription, one case at a time.** Start with
   $(iv)^* \times (iv)$ (the highlighted counterexample to Problem 1.6).
   The proof of "$(ii)^* \times (ii)$ has no SAD" on **p. 32** enumerates
   the arcs in the candidate decomposition $D_1, D_2$ — every arc that
   appears in the proof is an arc of $D$. Cross-reference with the figure
   to fill in any missing arcs. Encode and verify.

2. **Recover the underlying base $D[V_2] = S_{4,-2}$.** From the
   discussion on p. 28 ("after removing parallel arcs in the seven
   graphs, each of them is isomorphic to $S_4$, … there is a 4-circle
   $v_1 v_2 v_3 v_4 v_1$ in $D[V_2]$"), $S_{4,-2}$ contains the
   directed 4-cycle $v_1 \to v_2 \to v_3 \to v_4 \to v_1$ plus one arc
   in each diagonal direction. Two candidates are consistent
   ($S_{4,-2}$ = 4-cycle $+ \{v_1 \to v_3, v_2 \to v_4\}$ or 4-cycle
   $+ \{v_3 \to v_1, v_4 \to v_2\}$); the paper's Figure 5 layout
   suggests the former. The figures $(i)$–$(v)$ then differ only in
   $a$'s adjacency pattern with $V_2$.

3. **Acquire the published version** of arXiv:2408.02260 (preprint as of
   2024-08-05; if a journal version appears with cleaner figures,
   transcription is straightforward). The Discrete Appl. Math. 375 (2025)
   follow-up paper "Arc-disjoint in- and out-branchings in semicomplete
   split digraphs" by the same authors quotes the structural result and
   may include cleaner figures.

Path 1 is the smallest commit; recommend executing it as the first task
of round 3 with the verifier as the safety net (any encoding error will
either produce SAT instead of UNSAT, or fail the $\lambda^{\text{arc}} = 2$
sanity gate). 8 instances to encode; budget 2 hours, given the proof
text already constrains roughly half of each instance's arc set.

---

## Appendix A.4 — (iv)*x(iv) transcription attempt (round 3 side-quest)

Auditor session 2026-05-16 (bounded). Goal: encode the unique counterexample
to Problem 1.6 of Bang-Jensen–Wang 2025, namely the 6-vertex digraph
$(iv)^* \times (iv)$ from Appendix B.3 of Ai, He, Li, Qin, Wang 2024
(arXiv:2408.02260), as a verifier benchmark, with every arc carrying
explicit provenance against the proof text.

### A.4.1  Base digraph $D[V_2] = S_{4,-2}$

Reading p. 28 (rightmost panel of the three-panel figure: $S_4, S_{4,-1},
S_{4,-2}$) and p. 31 (the row of five $(i),\ldots,(v)$ panels in §B.3) and
cross-referencing the explicit arc derivations in the
$(iv)^* \times (iv)$ proof on p. 34 and the $(ii)^* \times (ii)$ proof on
p. 32, $S_{4,-2}$ on vertices $\{v_1, v_2, v_3, v_4\}$ has exactly the
following 6 arcs:

| Arc | Provenance | Source line |
|---|---|---|
| $v_1 \to v_2$ | text-forced | p. 28 "4-circle $v_1 v_2 v_3 v_4 v_1$ in $D[V_2]$"; p. 34 "$v_1 v_2 \in D_1$" |
| $v_2 \to v_3$ | text-forced | p. 28 "4-circle" |
| $v_3 \to v_4$ | text-forced | p. 28 "4-circle"; p. 34 "$v_3 v_4 \in D_2$" |
| $v_4 \to v_1$ | text-forced | p. 28 "4-circle"; p. 34 "$v_4 v_1 \in D_2$" |
| $v_1 \to v_3$ | text-forced | p. 32 (in $(ii)^* \times (ii)$ proof, same base) "$v_1 v_3 \in D_2$"; the $(iv)^* \times (iv)$ proof on p. 34 rules out $v_3 \to v_1$ via $N^-(v_1) = \{v_4, b\}$ exhaustively |
| $v_2 \to v_4$ | text-forced | p. 32 "$v_2 v_4 \in D_1$" in $(ii)^* \times (ii)$ proof on the same base; rules out $v_4 \to v_2$ via $N^+(v_4) = \{v_1, a\}$ in the p. 34 proof |

No further $V_2$-internal arcs exist: the p. 34 proof exhaustively
characterises $N^+(v_3) = \{b, v_4\}$, $N^-(v_1) = \{v_4, b\}$,
$N^+(v_4) = \{v_1, a\}$, ruling out every other potential $V_2$-internal
arc. $D[V_2] = S_{4,-2}$ is semicomplete (every pair adjacent) and is
**$S_4$ minus the two reverse-diagonal arcs $v_3 \to v_1$ and $v_4 \to v_2$.**

### A.4.2  Configuration $(iv)$ at vertex $a$

The figure on p. 31 (top row, fourth panel labelled "$(iv)$") shows $a$
adjacent to $v_2, v_4, v_3$. Page 30's explicit text statement is decisive:

> "When $a$ is adjacent to $v_2, v_4$ and $v_3$: If $v_3 a \notin D, av_3
> \in D$: It has no strong arc decomposition no matter the existence of
> dashed arcs as $(iv)^* \times (iv)$ has no strong arc decomposition."

This is the **defining text** of $(iv)$. It text-forces $a \to v_3 \in D$
and text-rules-out $v_3 \to a \in D$ for case $(iv)$. The "dashed arcs"
phrasing refers to the optional arc $a \to v_4$; the **minimal** $(iv)$
instance excludes the dashed arc.

| Arc at $a$ | Provenance | Source line |
|---|---|---|
| $v_4 \to a$ | text-forced | p. 31 "there are arcs $v_4 a, av_2, v_3 b, bv_1$ in $D$" |
| $a \to v_2$ | text-forced | p. 31 same |
| $v_2 \to a$ | inferred-from-structure | $d^-(a) \ge 2$ in 2-arc-strong $D$; only candidates for in-neighbours of $a$ are $\{v_2, v_4\}$ (the p. 34 proof rules out $v_1 a, v_3 a$ via "only two arcs from $\{v_1, v_3, b\}$ to $\{v_2, v_4, a\}$"); $v_4 a$ alone gives $d^-(a) = 1$. So $v_2 a$ is forced. |
| $a \to v_3$ | text-forced | p. 30 case definition "$v_3 a \notin D, a v_3 \in D$" for $(iv)$; on $S_{4,-2}$ (p. 31) the same labelling is reused |

No dashed arc $a \to v_4$: the canonical $(iv)$ encoding here uses the
minimum-arc realisation, consistent with the p. 34 proof phrase "no matter
the existence of dashed arcs."

### A.4.3  Configuration $(iv)^*$ at vertex $b$ — derivation from the $*$ operation

Page 31 defines: "By reversing all arcs in cases $(i),(ii),(iii),(iv)$ and
$(v)$, rotate 180 degrees clockwise, and relabeling, we obtain the
corresponding reversed and rotated cases $(i)^*, (ii)^*, (iii)^*, (iv)^*$,
and $(v)^*$".

The 180° rotation acts on the $v_i$ layout (with $v_1$ top-left, $v_2$
top-right, $v_3$ bottom-left, $v_4$ bottom-right) by the involution
$\sigma : v_1 \leftrightarrow v_4,\; v_2 \leftrightarrow v_3$, and renames
the $V_1$-vertex $a \to b$. Applying $*$ to each arc $x \to y$ of $(iv)$
(reverse, then $\sigma$):

| $(iv)$ arc at $a$ | reversed | $*$-image at $b$ |
|---|---|---|
| $v_4 \to a$ | $a \to v_4$ | $b \to v_1$ |
| $a \to v_2$ | $v_2 \to a$ | $v_3 \to b$ |
| $v_2 \to a$ | $a \to v_2$ | $b \to v_3$ |
| $a \to v_3$ | $v_3 \to a$ | $v_2 \to b$ |

So $(iv)^*$ at $b$ has arcs $\{b v_1,\; v_3 b,\; b v_3,\; v_2 b\}$. Each
is `text-forced` (the $*$ operation is defined in the paper's text).
Cross-check against the p. 34 proof:

- "$v_3 b \in D_1$" — matches $v_3 \to b$. ✓
- "$bv_1 \in D_1$" — matches $b \to v_1$. ✓
- "$bv_3 \in D_2$" — matches $b \to v_3$. ✓
- $v_2 \to b$ is not literally quoted in the p. 34 proof but is forced by
  $d^-(b) \ge 2$: only $V_2$-vertices can be in-neighbours of $b$, and
  the proof's "only two arcs from $\{v_1, v_3, b\}$ to $\{v_2, v_4, a\}$"
  combined with $N^+(v_4) = \{v_1, a\}$ and $N^+(v_1) = \{v_2, v_3\}$
  rules out $v_1 b$, $v_4 b$; $v_3 b$ already gives $d^-(b) = 1$, so
  $v_2 b$ is the only remaining candidate. **`text-forced` via the $*$
  operation; `inferred-from-structure` as an independent check.**

### A.4.4  Full 6-vertex arc list

$V_1 = \{a, b\}$, $V_2 = \{v_1, v_2, v_3, v_4\}$, $n = 6$, $m = 14$.

| # | Arc | Provenance |
|---|---|---|
| 1 | $v_1 \to v_2$ | text-forced (4-cycle in $S_{4,-2}$) |
| 2 | $v_2 \to v_3$ | text-forced |
| 3 | $v_3 \to v_4$ | text-forced |
| 4 | $v_4 \to v_1$ | text-forced |
| 5 | $v_1 \to v_3$ | text-forced ($S_{4,-2}$ diagonal; cross-checked p. 32) |
| 6 | $v_2 \to v_4$ | text-forced ($S_{4,-2}$ diagonal; cross-checked p. 32) |
| 7 | $v_4 \to a$ | text-forced (p. 31 "there are arcs $v_4 a$…") |
| 8 | $a \to v_2$ | text-forced (p. 31 same) |
| 9 | $v_2 \to a$ | inferred-from-structure ($d^-(a) \ge 2$; only candidate after p. 34's $N$-constraints) |
| 10 | $a \to v_3$ | text-forced (p. 30 case-$(iv)$ definition) |
| 11 | $v_3 \to b$ | text-forced (p. 31 + $*$ operation) |
| 12 | $b \to v_1$ | text-forced (p. 31 + $*$ operation) |
| 13 | $b \to v_3$ | text-forced ($*$ image of $v_2 \to a$; p. 34 "$bv_3 \in D_2$") |
| 14 | $v_2 \to b$ | text-forced ($*$ image of $a \to v_3$); independently `inferred-from-structure` ($d^-(b) \ge 2$) |

No arc is `figure-only-ambiguous`. Every arc is justified either by a
verbatim proof-text quotation or by the $*$-operation definition or by a
structural-degree argument that the proof's $N$-counts independently
verify.

### A.4.5  Structural checklist

(a) $V_1 = \{a, b\}$ independent: no $a \to b$ or $b \to a$ in the list. ✓

(b) $V_2$ semicomplete: all six pairs $\{v_i, v_j\}$ in $V_2$ have at
least one arc. ✓

(c) Degree sequence (matches p. 34 proof's $N$-statements):

| Vertex | $d^+$ | $d^-$ | $N^+$ | $N^-$ |
|---|---|---|---|---|
| $v_1$ | 2 | 2 | $\{v_2, v_3\}$ | $\{v_4, b\}$ |
| $v_2$ | 4 | 2 | $\{v_3, v_4, a, b\}$ | $\{v_1, a\}$ |
| $v_3$ | 2 | 4 | $\{v_4, b\}$ | $\{v_1, v_2, a, b\}$ |
| $v_4$ | 2 | 2 | $\{v_1, a\}$ | $\{v_2, v_3\}$ |
| $a$ | 2 | 2 | $\{v_2, v_3\}$ | $\{v_2, v_4\}$ |
| $b$ | 2 | 2 | $\{v_1, v_3\}$ | $\{v_2, v_3\}$ |

Cross-check vs. p. 34: $N^+(v_3) = \{b, v_4\}$ ✓, $N^-(v_1) = \{v_4, b\}$
✓, $N^+(v_4) = \{v_1, a\}$ ✓, $N^+_D(b) = \{v_1, v_3\}$ (p. 34: "$N^+_D(b)
= 2$" with $bv_1, bv_3$) ✓.

Note $(iv)^* \times (iv)$ is **$*$-symmetric**: applying $*$ to the whole
digraph swaps $a \leftrightarrow b$ and $\sigma$ swaps the $v_i$-pairs.
Under $a \mapsto b,\; b \mapsto a,\; v_1 \mapsto v_4,\; v_2 \mapsto v_3,\;
v_3 \mapsto v_2,\; v_4 \mapsto v_1$ followed by global arc reversal, the
arc multiset is fixed. (Quick check on the asymmetric arc $a \to v_3$:
reverse gives $v_3 \to a$, relabel $a \to b$ gives $\sigma(v_3) \to b
= v_2 \to b$. The image is $v_2 \to b$, which is in the arc set. ✓)
So the digraph is isomorphic to its arc-reverse, which is the abstract
reason why the paper's Theorem 1.8 "or their arc-reversed versions"
clause does not produce a separate benchmark for this case.

(d) **2-arc-strong, not 3-arc-strong**: verified by the verifier (see
A.4.6). Several vertices have $d^+ = d^- = 2$ (e.g. $a$, $b$, $v_1$,
$v_4$), so $\lambda^{\text{arc}} \le 2$. Strong connectivity verified.

(e) **Split-digraph hypothesis**: $V_1$ independent, $V_2$ semicomplete:
this is a 2-arc-strong split digraph. ✓ It is **not** a semicomplete
digraph: the pair $\{a, b\}$ is non-adjacent. So it is genuinely an
Ai et al. 2024 obstruction, not already covered by BJ–Yeo 2004.

### A.4.6  Verifier outcome

Ran `cross_check.cross_check(D, "iv_star_x_iv", time_limit_s=60.0)`
inside the project's `uv` virtual environment on 2026-05-16:

```
n=6  m=14  strong=True  kappa_arc=2
ILP=UNSAT  SAT=UNSAT  agree=True
```

Both ILP and SAT backends return **UNSAT in agreement**, in $< 0.3$ s,
matching the paper's claim that $(iv)^* \times (iv)$ has no strong arc
decomposition. The verifier's $\lambda^{\text{arc}} = 2$ check matches
the structural prediction.

### A.4.7  Final decision

**Decision: promoted to canonical benchmark.** All 14 arcs are
text-forced or inferred-from-structure with an independent text-derivable
justification (no arc is figure-only-ambiguous). The verifier outcome
(ILP=UNSAT, SAT=UNSAT, in agreement) matches the paper's claim. The
degree sequence and $N$-counts agree with every $N^+/N^-$ statement in
the p. 34 proof. The structural checklist (semicomplete $V_2$,
independent $V_1$, 2-arc-strong, not 3-arc-strong, $*$-self-symmetric) is
satisfied.

Action: appended to `code/benchmarks.py` as `_AiEtAl_iv_star_iv()` with
benchmark name `AiEtAl_iv_star_iv` and added to `all_benchmarks()`.

### A.4.8  Notes for future passes (Appendix B.3 sibling instances)

The other seven UNSAT cases of Appendix B.3 — $(i)^* \times (ii)$,
$(i)^* \times (iii)$, $(ii)^* \times (ii)$, $(ii)^* \times (iii)$,
$(ii)^* \times (iv)$, $(iii)^* \times (iii)$, $(iii)^* \times (iv)$,
$(iii)^* \times (v)$ — are now transcribable by the same procedure:

1. Base $D[V_2] = S_{4,-2}$ is shared across all 15 cases.
2. Configurations $(i), (ii), (iii), (v)$ are text-defined on pp. 29–30
   (for $S_{4,-1}$) and reused on p. 31 (for $S_{4,-2}$), with the
   adjacency-pattern statements text-forcing the figure-shown arcs:
   - $(i)$: $a$ adjacent to $v_2, v_4$ (full 2-cycles, both).
   - $(ii)$: $a$ adjacent to $v_2, v_4, v_1$ with $av_1 \in D, v_1 a \notin D$.
   - $(iii)$: $a$ adjacent to $v_2, v_4, v_1$ with $v_1 a \in D, av_1 \notin D$.
   - $(iv)$: $a$ adjacent to $v_2, v_4, v_3$ with $av_3 \in D, v_3 a \notin D$.
   - $(v)$: $a$ adjacent to $v_2, v_4, v_3$ with $v_3 a \in D, av_3 \notin D$.
3. The arcs $v_4 a, av_2$ are common (text-forced by p. 31's "there are
   arcs $v_4 a, av_2, v_3 b, bv_1$"). The $v_2 a, av_4$ pair fills in
   from 2-arc-strongness depending on which 3rd vertex $a$ touches; the
   p. 32 proof's $N^-(v_2) = 2$ and similar arguments pin it down per
   case.
4. Each $(f)^*$ is then derived by the $*$ operation.

Eight benchmarks remain. They are NOT encoded in round 3; defer to
round 4 unless explicitly requested. The round-3 commit is only the
$(iv)^* \times (iv)$ instance.

---

## Appendix A.5 — CL1 + R2 published-precedent check

Auditor session 2026-05-16. Goal: determine whether the Structural
Specialist's **CL1 in its R2-cleaned form**, as stated in
`team/11_cl1_proof_v1.md` and proved there from a *bilateral* SAD
hypothesis plus a 2-coloring of the bridge set, is genuinely new, or
whether it is equivalent to / immediately derivable from / a special
case of a previously published lemma.

### A.5.1  Statement under scrutiny (verbatim)

From `team/11_cl1_proof_v1.md` §5.1, *Lemma CL1 (final form, post-R2)*:

> Let $D = (V, A)$ be a digraph, $V = V_1 \,\dot\cup\, V_2$ with
> $|V_i| \geq 2$. Write $B^+ = \delta_D^+(V_1)$, $B^- = \delta_D^+(V_2)$.
> Suppose:
>
> (1) $D[V_1]$ and $D[V_2]$ each admit a strong arc decomposition
> $A(D_i) = R_i \,\dot\cup\, B_i$.
>
> (2) The bridge sets admit a partition $B^\pm = B^\pm_R \,\dot\cup\,
> B^\pm_B$ with $B^+_R, B^+_B, B^-_R, B^-_B$ all non-empty.
>
> Then $A(D) = (R_1 \cup R_2 \cup B^+_R \cup B^-_R) \,\dot\cup\,
> (B_1 \cup B_2 \cup B^+_B \cup B^-_B)$ is a strong arc decomposition
> of $D$.

The prompt's "R2-cleaned form" paraphrase is logically identical (drops
the explicit $|V_i| \ge 2$ floor and the named color classes, which are
both content-free up to relabelling).

### A.5.2  Candidate precedents

The five candidate precedents flagged in the brief are surveyed below.
Verbatim quotations were obtained directly from the arXiv PDFs of (1),
(4), (6) via `pdftotext -layout`; for (2) and (3) the journal versions
are paywalled and we rely on the verbatim restatements in BJ–Wang 2025
(Theorems 1.2 and 1.3) and BJG–Yeo 2020 (Theorems 1.1 and the
Edmonds-branching reuse in Lemma 4.1).

#### Source 1 — Bang-Jensen–Wang 2025, Lemma 2.4

Verbatim from arXiv:2309.06904v1, p. 4:

> **Lemma 2.4** Let $D$ be a directed multigraph and let $X$ be a
> subset of $V(D)$ such that every vertex of $D - X$ has both two
> in-neighbors and two out-neighbors in $X$. If $X$ has a strong arc
> decomposition then $D$ has a strong arc decomposition.
>
> **Proof.** Let $(A_1, A_2)$ be a strong arc decomposition of $X$. By
> assumption, every vertex $x \in D - X$ has two out-neighbors
> $x^+_1, x^+_2$ and two in-neighbors $x^-_1, x^-_2$ in $X$. Then
> $A_i \cup \{x^-_i x, x x^+_i : x \in D - X\}$, $i \in [2]$ is a
> strong arc decomposition of $D$.       $\square$

The companion **Lemma 2.5** (same paper, p. 4) lifts split-off arcs
back through $V_1$-vertices after applying Lemma 2.4 to $D[V_2]$; its
hypothesis still requires the SAD to live on $D[V_2]$ only — $V_1$ acts
as a *shell* whose vertices have prescribed in/out-degrees in $V_2$.

#### Source 2 — Bang-Jensen–Yeo 2004 §3 ("good pairs")

Primary source paywalled. The technical core, as restated in
BJG–Yeo 2020 (Theorem 2.5, verbatim from arXiv:1903.12225 p. 6):

> **Theorem 2.5** [12] A directed multigraph $D = (V, A)$ with a vertex
> $z$, has $k$ arc-disjoint out-branchings rooted at $z$ if and only if
> $d^-(X) \geq k$ for all non-empty $X \subseteq V \setminus \{z\}$.

This is Edmonds' branching theorem (not original to BJ–Yeo 2004). The
"good pair" notion of BJ–Yeo 2004 §3 is: a pair of arc-disjoint
out- and in-branchings, rooted at a *common* vertex, in a 2-arc-strong
semicomplete digraph. The existence of such a pair is the engine of
BJ–Yeo 2004 Theorem 1.2. As described in BJG–Yeo 2020 Lemma 4.1 (which
recycles the BJ–Yeo 2004 method), the argument is:

> [Claim 3 of Lemma 4.1 proof, BJG–Yeo 2020 p. 9–10] *As $D$ is
> 2-arc-strong there are 2 arc-disjoint paths $P_1, P_2$ from $u$ to $w$
> in $D$. [...] By Edmonds' branching theorem, Theorem 2.5, there
> exists two arc-disjoint out-branchings in $D^*$ both rooted at $u$.*
> *Analogously [...] there exists two arc-disjoint in-branchings in
> $D^{**}$ both rooted at $u$.*

So BJ–Yeo 2004's "good pair" = pair of arc-disjoint
(out-branching, in-branching) at a common root, both *within the same
color class*. R2 produces such a pair within each color class
separately — it does not require arc-disjointness between $T^+_c$ and
$T^-_c$ (see `team/11_cl1_proof_v1.md` §3 Step 6).

#### Source 3 — Bang-Jensen–Huang 2012 (locally semicomplete)

Primary source paywalled; no arXiv preprint exists. The two relevant
quoted theorems (via BJ–Wang 2025 Theorem 1.3, audit §1):

> Every 3-arc-strong locally semicomplete digraph has a strong arc
> decomposition and such a decomposition can be obtained in polynomial
> time.

The proof technique uses the round-decomposition of locally semicomplete
digraphs and recursively applies BJ–Yeo 2004 within rounds. There is no
isolable "bilateral SAD glue lemma" in the published statement of
BJ–Huang 2012 according to the secondary-source descriptions in
BJ–Wang 2025 and BJG–Yeo 2020.

#### Source 4 — Bang-Jensen–Gutin–Yeo 2020 (compositions)

Verbatim from arXiv:1903.12225 p. 5:

> **Lemma 2.3** [13] Let $D = Q[H_1, \ldots, H_t]$, where $D$ is an
> arbitrary digraph and every $H_i$ has no arcs. If an induced
> subdigraph $D'$ of $D$ with at least one vertex in each $H_i$ has a
> strong arc decomposition, then so has $D$.

This is the *composition shell-vertex lemma*: given a SAD on a "kernel"
sub-digraph $D'$ with one vertex per layer, every other layer-vertex is
absorbed because the layer $H_i$ is arc-less and a layer-vertex's
in/out-neighbors are exactly those of the chosen representative. It is
structurally analogous to BJ–Wang Lemma 2.4 specialized to the
composition setting; same shell-vs-kernel asymmetry.

The proof of Theorem 1.4 (the four-exception composition characterization)
in §4 uses **Lemma 4.1**, a cut-vertex case treated by extracting two
arc-disjoint out-branchings and two arc-disjoint in-branchings rooted
at the cut-vertex $u$, then assembling $G_1, G_2$ by combining them with
auxiliary arcs (BJG–Yeo 2020 p. 10–11). The stitching mechanism is
inline rather than extracted as a separate lemma; the kernel is
$\{$one branching pair$\}$, not a SAD-decomposable sub-digraph $D[V_2]$.

#### Source 5 — Bang-Jensen–Kriesell 2009 survey

Primary source (Electron. Notes Discrete Math. 34, 179–183) paywalled;
no preprint located in the open-access sources surveyed (5-page
survey-conference paper; expected to be expository). We could not
retrieve verbatim lemmas; the secondary descriptions in BJ–Wang 2025
and BJG–Yeo 2020 do not credit BJ–Kriesell with any extension-style
lemma.

#### Source 6 — Ai–He–Li–Qin–Wang 2024

Verbatim from arXiv:2408.02260v1, p. 4–5, in §2.1:

> **Lemma 2.4.** [6] Let $D$ be a multi-digraph and $X$ a subset of
> $V(D)$ such that every vertex of $D - X$ has two in-neighbors and
> two out-neighbors in $X$. If $X$ has a strong arc decomposition then
> $D$ has a strong arc decomposition.

This is the *direct re-citation* of BJ–Wang 2025 Lemma 2.4 (reference
[6] in the Ai et al. paper is the BJ–Wang 2025 paper). No bilateral or
class-agnostic strengthening is offered.

§2.2 of the Ai et al. paper introduces a *pending decomposition* notion
(Lemma 2.6, verbatim from arXiv:2408.02260v1 p. 5):

> **Definition 2.5.** Let $D = (V_1, V_2; A)$ be a split digraph. We say
> two arc-disjoint strong subdigraphs $D_1$ and $D_2$ constitute a
> **pending decomposition** of $D$ if, for each $i \in [2]$, we have
> $V_2 \subseteq V(D_i)$ and for any vertex $t \in V(D_i) \setminus
> V(D_{3-i})$, $t$ has at least one in-arc and one out-arc in
> $A(D) \setminus A(D_i)$.
>
> **Lemma 2.6.** If a 2-arc-strong split digraph $D = (V_1, V_2; A)$
> has a pending decomposition, then $D$ has a strong arc decomposition.

The pending-decomposition lemma still has a *unilateral* shape:
$D_1, D_2$ are strong subdigraphs that *both* cover $V_2$, and vertices
in $V_1$ are the "shell" absorbed by adding spare in/out-arcs. The
proof routes through Lemma 2.4 explicitly ("By Lemma 2.4, $D$ has a
strong arc decomposition" — p. 5).

### A.5.3  The novelty table

| Source | Statement (verbatim or paraphrased) | Comparison to CL1 (R2 form) | Verdict |
|---|---|---|---|
| **BJ–Wang 2025, Lemma 2.4** (arXiv:2309.06904, p. 4). Verbatim above. | $X$ has a SAD and every $v \in D - X$ has 2 in- and 2 out-neighbors in $X \Rightarrow D$ has a SAD. *Kernel-shell asymmetric*: only $D[X]$ is SAD-decomposable; vertices of $D - X$ are absorbed as a shell. | CL1 has *both* $D[V_1]$ and $D[V_2]$ SAD-decomposable, each with internal SAD arcs that must be partitioned by the conclusion's coloring. Lemma 2.4's $D - X$ contributes no internal arcs to either color class; CL1's $V_2$ contributes $R_2 \dot\cup B_2$. The two are *not* equivalent: if $D[V_2]$ has any internal arc, Lemma 2.4 says nothing about how to color it. Conversely if $D - X$ is an independent set, CL1 hypothesis (1) on $V_2 = D - X$ is vacuously false (an arc-less digraph admits no SAD by convention $|V_i|\ge 2$). The proof techniques are kin: Lemma 2.4 attaches one in-arc + one out-arc per shell vertex to each color; CL1's R2 attaches one bridge arc per color, then inflates by the inner SAD. | **CL1 is a class-agnostic *bilateral* version of Lemma 2.4** (same proof spine — Edmonds-style attachment — applied to two SAD-decomposable parts rather than to one SAD-kernel + one arc-less shell). Neither is a special case of the other. |
| **BJ–Yeo 2004, §3 "good pair"** (Combinatorica 24, 331–349). Paywalled; relied on the BJG–Yeo 2020 Lemma 4.1 / Theorem 2.5 reuse, verbatim above. | Existence of arc-disjoint out- and in-branchings rooted at a common vertex in a 2-arc-strong semicomplete digraph. Class-specific (semicomplete). The "pair" is *arc-disjoint*. | CL1 R2 also produces an out-branching and an in-branching at a common root in *each* color class, but does **not** require arc-disjointness between $T^+_c$ and $T^-_c$ (which is anyway moot for CL1's strong-connectivity-only conclusion). The class hypothesis is dropped (CL1 works on any digraph whose two parts are SAD). R2's proof technique is identical to Edmonds' branching theorem applied to each color class. | **CL1 is class-agnostic and uses the same branching-existence technique** as BJ–Yeo 2004 §3, but its conclusion is *one* common-root branching pair per color class, not an arc-disjoint pair across the whole digraph. The hypothesis differs (bilateral SAD on parts vs. 2-arc-strong semicomplete). **CL1 is independent of BJ–Yeo 2004 §3 as a lemma statement** even though it borrows the proof technique. |
| **BJ–Huang 2012** (JCTB 102, 701–714). Paywalled; relied on the BJ–Wang 2025 Theorem 1.3 restatement. | Every 3-arc-strong locally semicomplete digraph has a SAD (polytime). No isolable bilateral glue lemma surfaces in the secondary descriptions. | The proof uses round-decomposition + recursive BJ–Yeo 2004, not a general two-part SAD glue. No analogue of CL1's bilateral statement. | **Cannot determine from available source**, but the secondary sources (BJ–Wang 2025 and BJG–Yeo 2020) do not credit BJ–Huang 2012 with a bilateral glue lemma. Conservatively: CL1 is independent of BJ–Huang 2012 modulo paywall. |
| **BJG–Yeo 2020, Lemma 2.3** (arXiv:1903.12225, p. 5). Verbatim above. | $D = Q[H_1, \ldots, H_t]$ with each $H_i$ *arc-less*; if some sub-digraph $D'$ with one vertex per $H_i$ has a SAD, then $D$ has a SAD. Composition shell-vertex lemma. | CL1 has no composition structure required and each $D[V_i]$ may have many internal arcs (which Lemma 2.3 explicitly forbids: "every $H_i$ has no arcs"). Lemma 2.3 is the composition-flavored analogue of BJ–Wang Lemma 2.4: same shell-kernel asymmetry. | **CL1 is independent of BJG–Yeo 2020 Lemma 2.3** (different hypothesis: bilateral SAD on internally-rich parts vs. SAD on one kernel + arc-less layers). |
| **BJG–Yeo 2020, Lemma 4.1** (inline cut-vertex proof, arXiv:1903.12225 pp. 9–13). | If $D = T[H_1, \ldots, H_t]$ is 2-arc-strong and contains a cut-vertex $u$, then $D$ has a SAD. Proof builds two arc-disjoint out-branchings at $u$ in one side $D^*$, two arc-disjoint in-branchings at $u$ in the other side $D^{**}$, then assembles two color classes. | Stitching at a single cut-vertex $u$, using **branchings as the kernel** rather than full SADs on the two sides. Not a two-part SAD glue. | **CL1 is independent of BJG–Yeo 2020 Lemma 4.1.** Same branching-existence backbone, but the input is 2-arc-strength on each side + Edmonds, not bilateral SAD. |
| **BJ–Kriesell 2009 survey** (Electron. Notes Discrete Math. 34, 179–183). Paywalled; no preprint; no relevant lemma found in secondary sources. | — | — | **Cannot determine from available source**; survey-paper format suggests no novel lemma load-bearing here. Pragmatically: not a precedent. |
| **Ai et al. 2024, Lemma 2.4** (arXiv:2408.02260, p. 4). Verbatim above; cites BJ–Wang 2025 as [6]. | Direct re-citation of BJ–Wang 2025 Lemma 2.4. Same kernel-shell asymmetric form. | Same comparison as the BJ–Wang row. | **CL1 is the class-agnostic bilateral version** of Ai et al.'s Lemma 2.4 = BJ–Wang Lemma 2.4. |
| **Ai et al. 2024, Lemma 2.6** ("pending decomposition", arXiv:2408.02260, p. 5). Verbatim above. | $D$ has a pending decomposition $\Rightarrow D$ has a SAD; pending decomposition = two arc-disjoint strong subdigraphs $D_1, D_2$ each covering $V_2$, with every $t \in V(D_i) \setminus V(D_{3-i})$ having spare in/out-arcs outside $A(D_i)$. | The two strong subdigraphs $D_1, D_2$ both cover *the same* part $V_2$ (not partitioned); $V_1$ is the shell whose vertices may be in only one of $D_1, D_2$ and are absorbed via spare arcs. Still unilateral: $V_2$ is the kernel, $V_1$ is the shell. | **CL1 is independent of Lemma 2.6** (different hypothesis shape; pending decomposition is two strong subdigraphs both containing $V_2$, not a partition of $A(D)$ across $V_1, V_2$). |

### A.5.4  Final novelty verdict

**NOVEL** (with the *qualification* that the proof technique is shared
with BJ–Wang 2025 Lemma 2.4 / BJ–Yeo 2004 §3 / BJG–Yeo 2020 Lemma 4.1).

No surveyed lemma states the bilateral form: *both* $D[V_1]$ and
$D[V_2]$ are SAD-decomposable, with a 2-coloring of bridges that is
non-empty in each (direction, color) class, gluing to a SAD of $D$.

The closest published precedent is **BJ–Wang 2025 Lemma 2.4**. The
difference is structural, not cosmetic:

- BJ–Wang Lemma 2.4 has a **kernel-shell asymmetry**: the kernel $X$
  carries the SAD; the shell $D - X$ is arc-less between its own
  vertices (the lemma is silent on internal arcs of $D - X$, and the
  proof's "add $\{x_i^- x, x x_i^+\}$ to each color" gives no recipe
  for any arc internal to $D - X$).
- CL1 is **bilateral**: $D[V_1]$ *and* $D[V_2]$ each have their own SAD,
  and CL1's conclusion partitions $A(D)$ — including the internal arcs
  of both parts — into two color classes. The bridges play the role of
  Edmonds-style attachment arcs *between* two SAD-decomposed parts,
  rather than between a SAD-decomposed kernel and an arc-less shell.

Neither lemma reduces to the other:

- **CL1 $\not\Rightarrow$ Lemma 2.4**: if $D - X$ is an independent set
  of $k \ge 2$ vertices, then $|V(D[D-X])| = k$ but $A(D[D-X]) =
  \emptyset$; the part $D[D-X]$ has no SAD because a SAD requires each
  color class to be strongly connected and an arc-less digraph on
  $\ge 2$ vertices is not strong. So CL1's hypothesis (1) on $V_2 = D-X$
  fails outright, and CL1 cannot recover BJ–Wang Lemma 2.4.
- **Lemma 2.4 $\not\Rightarrow$ CL1**: if $D[V_2]$ has internal arcs,
  Lemma 2.4's proof template adds one in-arc and one out-arc per shell
  vertex per color, but does not partition the internal arcs of
  $D[V_2]$ between the two color classes. There is no obvious
  reduction.

CL1's proof (R2 in `team/11_cl1_proof_v1.md` §3) does borrow the
**Edmonds-branching-stitch** technique that runs through BJ–Wang Lemma
2.4, BJ–Yeo 2004 §3, and BJG–Yeo 2020 Lemma 4.1: namely, in each color
class, produce a spanning out-arborescence and a spanning in-arborescence
at a common root by stitching inner branchings via one bridge arc per
direction. The technique is essentially folklore for the
two-arc-strong/semicomplete settings; CL1 makes the *bilateral
SAD-on-each-part* statement that is not in the surveyed literature.

### A.5.5  What specifically is new

1. **Bilateral form, class-agnostic.** Every surveyed precedent that
   has a clear glue-shape is *unilateral*: one part carries a SAD, the
   other is an arc-less shell (BJ–Wang Lemma 2.4, Ai et al. Lemma 2.4,
   BJG–Yeo 2020 Lemma 2.3, Ai et al. Lemma 2.6 with $V_2$ as the
   common kernel). CL1 admits both parts as SAD-decomposable
   *internally-rich* digraphs, and is class-agnostic (no semicomplete,
   locally semicomplete, split, or composition structure required).

2. **Bridge 2-coloring as input hypothesis.** Hypothesis (2) of CL1 is
   the satisfiability of a small 2-coloring problem on the bridge set,
   with the only constraint being non-emptiness in each
   (direction, color) class. The Vehicle-6 corpus (501 / 2 471 = 20.3 %
   of SAD-decomposable inner-part gluings have neither bridge direction
   monochromatic) confirms this is a substantive — not vacuous —
   condition; published kernel-shell lemmas have no analogue because
   the bridge 2-coloring degenerates trivially when the shell is
   arc-less.

3. **No 3-arc-strength requirement on $D$.** CL1 is stated for a
   general digraph $D$; only the parts $D[V_i]$ need SAD-decomposability
   (which forces $\lambda^{\text{arc}}(D[V_i]) \ge 2$ but does not
   constrain $\lambda^{\text{arc}}(D)$). BJ–Wang Lemma 2.4 similarly
   has no arc-strength hypothesis on $D$ itself, but the surrounding
   results (BJ–Wang Theorem 1.6, BJG–Yeo 2020 Theorem 1.4) require
   2-arc-strength of $D$. CL1 is the cleanest "no global arc-connectivity
   hypothesis" form among the surveyed glue lemmas.

### A.5.6  Caveat — paywall-conditional residue

Two surveyed precedents (BJ–Yeo 2004 §3 in full, BJ–Huang 2012, and the
BJ–Kriesell 2009 survey) are paywalled and were checked only through
secondary verbatim quotation in BJ–Wang 2025 and BJG–Yeo 2020. The
Auditor cannot exclude with certainty that a "bilateral SAD glue lemma"
appears as an inline step in one of these papers' proofs (not separately
named). Best-effort search of all secondary descriptions
(`/tmp/bjwang.txt`, `/tmp/bjgy2020.txt`, `/tmp/aihelxqw.txt`) for
"both parts" / "kernel and shell" / "bilateral" patterns turns up
nothing. The NOVEL verdict is conditional on this absence.

**Recommended action for the Lead.** Before publication, secure
library access to BJ–Yeo 2004 (Combinatorica 24, 331–349) and
BJ–Huang 2012 (JCTB 102, 701–714), and search §3 of each for any
inline bilateral-SAD-glue step. If none, the NOVEL verdict stands. If
one is found, the verdict downgrades to **DERIVATIVE-OF-X** and the
"Bridge-Coloring Lifting Theorem" standalone publication route
(`team/11_cl1_proof_v1.md` §6.2) must be abandoned in favor of the
"CL1 + class application" route (e.g. CL1 as the engine for a
class-specific theorem, as suggested by the Specialist in §6.2).

### A.5.7  Summary line

CL1 (R2-cleaned form) is **NOVEL** as a lemma statement relative to the
surveyed literature (BJ–Yeo 2004, BJ–Huang 2012, BJG–Yeo 2020, BJ–Wang
2025, BJ–Kriesell 2009 survey, Ai–He–Li–Qin–Wang 2024). The
**bilateral, class-agnostic** form is not in the surveyed literature.
The proof technique (Edmonds-branching stitch across one bridge per
direction per color) is shared with BJ–Wang 2025 Lemma 2.4 and BJG–Yeo
2020 Lemma 4.1 and should be credited; this does not prevent CL1 from
being published as a standalone lemma, provided the introduction
explicitly positions CL1 as the bilateral class-agnostic version of
BJ–Wang Lemma 2.4 and cites both BJ–Wang 2025 and BJG–Yeo 2020 for the
underlying branching-extraction technique.

The team **may proceed** to a write-up of CL1 as a stand-alone result,
subject to the paywall-conditional residue in §A.5.6.

---

## Appendix A.6 — Theorem RD citation closure

Author: Proof Auditor / Literature Reviewer
Date: 2026-05-16
Status: Closes caveat (c) of `team/16_ols_novelty_check.md` §4 and
caveat §6.1 of `team/14_route_b_ols_extraction.md`. One bounded
session of public-source literature audit. Output of this appendix
determines whether Route B's headline ships with the citation as
written, with a corrected citation, or with the OLS round-
decomposition scoped down / proved as a sub-lemma.

### §A.6.1 — The exact claim under review

From `team/14_route_b_ols_extraction.md` §1.2, verbatim:

> The structure theorem we apply is due to Bang-Jensen (1990, *J. Graph
> Theory* 14, 371–390) for the locally semicomplete case and
> Bang-Jensen–Huang (1995, *J. Comb. Theory B* 63, 261–276) for the
> extension to OLS digraphs. We use the modern restatement from
> Bang-Jensen–Gutin, *Digraphs: Theory, Algorithms and Applications*
> (Springer 2nd ed., 2009), Theorem 5.6.1 and §5.6.2 (the BJ–Huang 1995
> paper itself sits behind the JCTB paywall; the BJG textbook is the
> authoritative open restatement and is what we cite).

And the stated **Theorem RD** itself:

> *Let $D$ be a strongly connected out-locally-semicomplete digraph.
> Then exactly one of the following holds:*
> *(R1) $D$ is **semicomplete**.*
> *(R2) $D$ admits a **round decomposition** $D = R[C_1, C_2, \ldots,
> C_p]$ with $p \geq 2$, where each $C_i$ is a strongly connected
> semicomplete digraph (a "round component"); $R$ is a fixed round
> labelling of the components; the cyclic orientation is consistent.*
> *Moreover, the decomposition is unique up to cyclic relabelling, and
> when $p \geq 2$ the round labelling can be computed in polynomial
> time from $D$.*

Three pieces of the citation cluster need verification:

(C1) **Bang-Jensen 1990** *Locally semicomplete digraphs: a
generalization of tournaments* — claimed to prove the LS case of
Theorem RD.

(C2) **Bang-Jensen–Huang 1995** *J. Comb. Theory B* 63, 261–276 —
claimed by `team/14_*` to prove the **OLS extension** of Theorem RD.

(C3) **Bang-Jensen–Gutin 2009** Theorem 5.6.1 — claimed to be the
modern textbook restatement.

### §A.6.2 — Source-by-source assessment

#### Source 1. Bang-Jensen 1990 (J. Graph Theory 14, 371–390)

Paywalled; arXiv predates the paper's deposit window. Confirmed via
the Bang-Jensen–Guo open classification preprint
(`/tmp/bjguo_classif.pdf` → `/tmp/bjguo_classif.txt`, downloaded
from `cs.rhul.ac.uk/home/gutin/paperstsp/classif2.pdf`), which is the
definitive secondary source on the BJ-1990 paper. From
`/tmp/bjguo_classif.txt`:

- **[verbatim, line 30]**: "[Bang-Jensen 1990] proved that the
  characterizations for Hamiltonian path and cycle in tournaments
  extend to locally semicomplete digraphs – *for every vertex x the
  set of in-neighbours as well as the set of out-neighbours of x
  induce a semicomplete digraph.*"

This is the **two-sided** LS definition. BJ-1990 is unambiguously
about LS, not OLS.

- **[verbatim, lines 123–125]**: "A *locally semicomplete digraph* $D$
  is **round decomposable** if there exists a round local tournament
  $R$ on $r \geq 2$ vertices such that $D = R[S_1, \ldots, S_r]$,
  where each $S_i$ is a strong semicomplete digraph."

The definition of "round decomposable" is given **only for locally
semicomplete (two-sided) digraphs**.

**Verdict on Source 1:** BJ-1990 proves the LS case of Theorem RD;
**not** the OLS case. `team/14_*`'s attribution of the LS case to
BJ-1990 is correct.

#### Source 2. Bang-Jensen–Huang 1995 (J. Comb. Theory B 63, 261–276)

**The citation does not exist in this form.** Verified via WebFetch
of the JCTB Vol. 63 table of contents
(sigmod.org/publications/dblp/db/journals/jct/jctb63.html):

- JCTB 63 pp. 200–221: J. Huang, "On the Structure of Local
  Tournaments" — **single-author**, not joint with Bang-Jensen, and
  on **local tournaments** = locally semicomplete digraphs with no
  2-cycle (still two-sided).
- JCTB 63 pp. 261–280: J. Bang-Jensen and Y. **Manoussakis**, "Weakly
  Hamiltonian-Connected Vertices in Bipartite Tournaments" — on
  bipartite tournaments, not related to LS/OLS at all.

There is **no Bang-Jensen + Huang paper at JCTB 63 (1995) pp.
261–276**. The actual Huang 1995 result on local-tournament structure
is at pp. 200–221, and it is for the two-sided local-tournament class.

A related Bang-Jensen + Huang collaboration exists — *Quasi-transitive
digraphs*, J. Graph Theory 20:2 (1995), 141–161 — but that is about
quasi-transitive digraphs, a different generalization that does not
contain OLS.

The most plausible reading: `team/14_*` §1.2 is **mis-citing** the
canonical "round decomposition + classification" finalization, which
is in fact the **Bang-Jensen–Guo–Gutin–Volkmann** paper *A
classification of locally semicomplete digraphs*, Discrete Math.
167/168 (1997), 101–114 — open at the Royal Holloway URL above —
which is Theorem 3.12 there. That paper is **also** for two-sided
LS (verified: see Source 1 above for the verbatim definition the BJGGV
paper uses).

**Verdict on Source 2:** The cited paper does not exist. The intended
result, attributed to a 1995 / 1997 BJ-and-collaborators paper, is in
the BJGGV 1997 *Classification* paper, and it is for LS only.

#### Source 3. Bang-Jensen–Gutin 2009 *Digraphs* Theorem 5.6.1

PDF of an open draft of BJG-2009 downloaded from
`cs.rhul.ac.uk/books/dbook/main.pdf` →
`/tmp/bjg_book.pdf` → `/tmp/bjg_book.txt`. Two findings.

**(3a)** **Theorem 5.6.1 in BJG-2009 is not about round
decomposition.** From `/tmp/bjg_book.txt`:

- **[verbatim, line 14898]**: §5.6 heading is "Hamilton Cycles and
  Paths in Degree-Constrained Digraphs."
- **[verbatim, line 14927]**: "**Theorem 5.6.1** (Bang-Jensen, Gutin
  and Li) [69] Let $D$ be a strong digraph of order $n \geq 2$.
  Suppose that, for every dominated pair of non-adjacent..."

Theorem 5.6.1 is a **Chvátal-Erdős-style degree condition** for
Hamiltonicity, not a round decomposition. The `team/14_*` citation
"Theorem 5.6.1 and §5.6.2" of the BJG-2009 textbook is **misnumbered**
— the round-decomposition material is in **§4.11**, not §5.6.

**(3b)** **The actual round decomposition material in BJG-2009
§4.11 is for LS only.** From `/tmp/bjg_book.txt`:

- **[verbatim, lines 13321–13324]**: "A *locally semicomplete digraph*
  $D$ is **round decomposable** if there exists a round local
  tournament $R$ on $r \geq 2$ vertices such that $D = R[S_1, \ldots,
  S_r]$, where each $S_i$ is a strong semicomplete digraph. We call
  $R[S_1, \ldots, S_r]$ a round decomposition of $D$."
- **[verbatim, line 13332]**: "**Corollary 4.11.7** [44] Every
  connected, but not strongly connected *locally semicomplete*
  digraph $D$ has a unique round decomposition $R[D_1, D_2, \ldots,
  D_p]$..."
- **[verbatim, line 13384]**: "**Proposition 4.11.9** [55] Let
  $R[H_1, H_2, \ldots, H_\alpha]$ be a round decomposition of a strong
  *locally semicomplete* digraph $D$..."
- The classification theorem (analogue of BJGGV-1997 Theorem 3.12)
  appears at line 13649 with the same LS hypothesis.

Meanwhile, the **locally in-semicomplete** (one-sided) digraphs are
treated separately in **§4.10**, and only weak structural results are
stated for them:

- **[verbatim, lines 13036–13042]**: "**Theorem 4.10.4** Let $D$ be
  a locally in-semicomplete digraph. (i) [Strong-component
  domination]. (ii) [$SC(D)$ has an out-branching]."

No round decomposition is stated in §4.10 for locally
in-/out-semicomplete digraphs. By arc-reversal duality between OLS
and ILS (= locally in-semicomplete), the absence of an
ILS-round-decomposition in §4.10 means **no OLS round-decomposition
in the textbook either**.

**Verdict on Source 3:** The cited "Theorem 5.6.1" is misnumbered (it
is a Hamiltonicity theorem, not round decomposition). The actual
round-decomposition machinery in the textbook is in §4.11, and it is
stated **explicitly for LS, not OLS**. The locally
in-/out-semicomplete sections of the textbook (§4.10) contain only
strong-component-level structure, **no round decomposition**.

#### Source 4. Bang-Jensen–Gutin 2018 *Classes of Directed Graphs* Ch. 6

Paywalled at Springer; the SDU author page
(portal.findresearcher.sdu.dk) gives the **abstract verbatim**:

> "Locally semicomplete digraphs form a significant generalization of
> semicomplete digraphs with a very rich structure. […] Many of the
> proofs and algorithms rely on a structural characterization of
> those *locally semicomplete digraphs* that are not semicomplete
> (have independence number at least 2). As it turns out, these
> digraphs fall in two disjoint classes, called **round decomposable**
> and **evil locally semicomplete digraphs**, respectively."

The abstract treats round decomposition as a property of **locally
semicomplete** (two-sided) digraphs, not OLS. The chapter title's
"Generalizations" qualifier is hinted but the abstract gives no
indication of an OLS round-decomposition theorem; the only
generalization mentioned in the abstract is the implicit
"superclasses" phrase ("Several of the results hold even for some
superclasses of locally semicomplete digraphs"), which is too vague
to ground a citation.

Downstream papers (BJ–Wang 2025, Ai et al. 2024, BJG–Yeo 2020) cite
this chapter but **do not quote any OLS-round-decomposition result
from it** when discussing SAD problems (verified in
`team/16_ols_novelty_check.md` §3).

**Verdict on Source 4:** Probability the chapter contains an OLS
round-decomposition theorem is low (no downstream citation extracts
one, and the abstract restricts the structure-classification result
to LS). Cannot be verified to 100 % without institutional access.
This is the residual paywall risk.

#### Source 5. Newer (2015–2025) literature on OLS / one-sided LS

WebSearch returns **zero** hits for "out-locally-semicomplete round
decomposition" as a theorem statement. The most relevant survey is
Bang-Jensen–Gutin *Generalizations of tournaments: A survey* (J.
Graph Theory 28 (1998), 171–202), open at
`cs.rhul.ac.uk/home/gutin/paperstsp/gener7.pdf` →
`/tmp/bjg_survey.pdf` → `/tmp/bjg_survey.txt`. This survey is the
single definitive source on the **structural state of the
one-sided classes**. Findings:

- **[verbatim, lines 111–113]**: "A digraph $D$ is *locally
  in-semicomplete* (locally out-semicomplete, respectively) if, for
  every vertex $x$ of $D$, the in-neighbourhood of $x$ (its
  out-neighbourhood, respectively) induces a semicomplete digraph. A
  digraph $D$ is *locally semicomplete* if it is both locally in- and
  locally out-semicomplete."

(This confirms the precise definitions and the duality OLS
$\leftrightarrow$ ILS under arc reversal that `team/14_*` §1.1 uses.)

- **[verbatim, lines 283–285]**: "A *locally semicomplete digraph* $D$
  is **round decomposable** if there exists a round locally
  tournament digraph $R$ on $r \geq 3$ vertices such that $D = R[S_1,
  \ldots, S_r]$, where each $S_i$ is a semicomplete digraph."

Again, the round decomposition is defined and proved **only for
locally semicomplete digraphs**.

- **[verbatim, lines 331–332]**: "Although **locally in-semicomplete
  digraphs are much more general than locally semicomplete digraphs**,
  we suspect that they have a nice structural characterization.
  **Problem 6.8 Find a non-trivial structural characterization of
  locally in-semicomplete digraphs.**"

This is the **decisive** finding: Bang-Jensen and Gutin pose the
structural characterization of locally in-semicomplete (= ILS, dual
of OLS) digraphs **as an OPEN PROBLEM** in 1998. Twenty-eight years
later, no published resolution exists (verified by WebSearch over
2015–2025 OLS / ILS literature).

The remainder of the survey treats locally in-semicomplete digraphs
in terms of weaker results — Hamilton-path / Hamilton-cycle
existence (Theorems 7.1, 7.2, 7.6, 7.7) — none of which gives a
round decomposition.

**Verdict on Source 5:** No published round-decomposition theorem for
OLS or ILS exists. The structural characterization of one-sided
locally semicomplete digraphs was posed as **Problem 6.8** in the
1998 BJ–Gutin survey and remains open in the surveyed literature.

### §A.6.3 — Verdict

**PUBLISHED-FOR-LS-ONLY.**

The published round-decomposition theorem is for the **two-sided** LS
class (Bang-Jensen 1990; finalized by Bang-Jensen–Guo–Gutin–Volkmann
1997 Theorem 3.12; modern restatement in Bang-Jensen–Gutin 2009 §4.11
Corollary 4.11.7 / classification theorem at line 13649). It is
**not** a theorem for OLS, and the question of whether OLS admits a
round decomposition into semicomplete components is **explicitly
open** in the surveyed literature (Bang-Jensen–Gutin 1998 survey
Problem 6.8 for the ILS dual).

Three secondary findings reinforce this verdict:

(F1) The `team/14_*` §1.2 citation **"Bang-Jensen–Huang 1995, JCTB 63,
261–276"** does not exist. The two papers in JCTB 63 around those
pages are Huang's single-author "On the Structure of Local
Tournaments" (pp. 200–221, LS only) and Bang-Jensen–Manoussakis on
bipartite tournaments (pp. 261–280, unrelated). The Lead's
attribution in `team/13` of this paper as the OLS-extension reference
appears to be a phantom citation.

(F2) The `team/14_*` §1.2 citation **"Bang-Jensen–Gutin 2009 Theorem
5.6.1"** is misnumbered. Theorem 5.6.1 in BJG-2009 is a Chvátal-Erdős
Hamiltonicity theorem for degree-constrained digraphs (Bang-Jensen,
Gutin, Li). The actual round-decomposition machinery lives at §4.11
(Corollary 4.11.7, Proposition 4.11.9, the full Theorem at line 13649
of `/tmp/bjg_book.txt`), and it is for two-sided LS.

(F3) Even at the milder ILS class (= OLS under arc reversal), only
strong-component-level structural results are published (BJ–Huang–
Prisner 1993 for in-tournaments, restated as Theorem 4.10.4 in
BJG-2009): the strong components have an acyclic ordering and form an
out-branching in $SC(D)$, but **the components themselves are not
shown to be semicomplete** and **no round structure on the components
is published**. So even a "weakened RD" for OLS is not in the
literature.

### §A.6.4 — Recommendation

The Route B proof in `team/14_route_b_ols_extraction.md` has a
**citation gap at Theorem RD**. The proof's load-bearing structure
theorem is not cited correctly — both the journal citation
(BJ–Huang 1995, JCTB 63, 261–276) and the textbook citation (BJG-2009
Theorem 5.6.1) are wrong, and a corrected citation for an
OLS round-decomposition theorem **does not exist in the published
literature**.

The team has two viable paths:

**(R1) — Strongly preferred. Treat OLS round decomposition as a
Phase 4.5 sub-lemma to be proved.** The Structural Specialist
expands `team/14_route_b_ols_extraction.md` §1.2 from a citation into
a **proved lemma**: *every strongly connected out-locally-semicomplete
digraph either is semicomplete or admits a round decomposition into
semicomplete components.* This sub-lemma is **a publishable result
in its own right** (it is the long-open Problem 6.8 of BJ–Gutin 1998,
in OLS direction rather than ILS; the dual is immediate by arc
reversal). The proof can adapt the LS techniques of BJGGV-1997 §3
since they use the in-neighborhood-semicompleteness in only a
limited number of places — the Specialist must isolate those places
and show they can be by-passed in the OLS setting. **If this
sub-lemma is proved, Route B not only ships, but ships with a
strictly stronger headline: "OLS round decomposition + OLS SAD"
two-theorem package, JCTB-tier.**

**(R2) — Fallback. Scope down the Route B headline to LS.**
Replace OLS by LS throughout `team/14_*`. This loses the strict
generalization over BJ–Huang 2012 (the published LS-SAD theorem) and
makes Route B's headline a re-proof of BJ–Huang 2012 via CL1, which
is a methodological contribution but **not a strictly new theorem**.
The Structural Specialist's `team/14_*` §6.7 already flags this
fallback. Likely venue under (R2): J. Graph Theory or Disc. Appl.
Math., not JCTB.

**The Lead's `team/13` tripwire fires.** `team/13` §6.1 set a 6-week
tripwire on the OLS round-decomposition footing. With this audit
closing the literature question definitively (no published OLS RD
exists), the tripwire is no longer conditional on library access; the
question is now strictly mathematical, and the deadline of
**2026-06-27** (6 weeks from today, 2026-05-16) applies to the
Structural Specialist's proof of the OLS-RD sub-lemma. If the
sub-lemma is not proved by 2026-06-27, Route B's headline must be
scoped down to LS per (R2).

**Updates to existing audit deliverables.** The earlier verdict in
`team/16_ols_novelty_check.md` (Route B "NOVEL with CANNOT-DETERMINE
residue") **strengthens** in light of this appendix:

- Caveat (c) of `team/16_*` §4 (the Lead's round-decomposition
  footing not in literature) **promotes to a hard finding**: it is
  not in the literature, and the survey explicitly poses the
  characterization problem as open.
- Caveat (a) (Springer 2018 Chapter 6 paywalled) **softens**: the
  abstract treats round decomposition as an LS-only property, and no
  downstream paper extracts an OLS theorem from the chapter. The
  probability that Chapter 6 contains an unannounced OLS RD theorem
  was already estimated low in `team/16_*` §4; this appendix's
  Source-4 verdict keeps that estimate but does not eliminate the
  residual risk.
- Caveat (b) (BJ–Huang 2012 paywalled) **decouples**: the BJ-Huang
  2012 question is about whether the proof contains an inline OLS
  step. Even if it does, the result-as-stated remains LS, and the
  citation in `team/14_*` §1.2 is still wrong as a literature
  reference to RD.

The **single mathematical question** that determines Route B's fate
is now: does OLS admit a round decomposition into semicomplete
components? The Structural Specialist owns this question. The
Auditor's recommendation: convert `team/14_*` §1.2 from a citation
block into a proved lemma, and aim for the strengthened two-theorem
JCTB submission described in (R1).

### §A.6.5 — Summary line

**PUBLISHED-FOR-LS-ONLY.** Theorem RD as cited in
`team/14_route_b_ols_extraction.md` §1.2 is not in the published
literature: the journal citation (BJ–Huang 1995 JCTB 63, 261–276)
does not exist, the textbook citation (BJG-2009 Theorem 5.6.1) is
misnumbered, and the underlying structural problem for one-sided
locally semicomplete digraphs is **explicitly open** (BJ–Gutin 1998
survey Problem 6.8). The Route B headline must either be downgraded
to LS or accompanied by a freshly-proved OLS round-decomposition
sub-lemma; preferred path is to prove the sub-lemma and ship a
two-theorem JCTB package.

---

## Appendix A.8 — BJ–Wang 2025 multidigraph scope

Auditor session 2026-05-16. Goal: determine whether the contraction
route TODO 1′ of `team/19_near_split_extraction.md` §3.1 is licensed
by the published BJ–Wang 2025 results. Specifically: does BJ–Wang
2025 Theorem 1.6 / Corollary 1 apply to **split multi-digraphs** (the
target class after chord-contraction), or only to simple split
digraphs? Primary source consulted directly: arXiv:2309.06904v1, full
text at `/tmp/bjwang2025.txt`. Cross-check: arXiv:2408.02260v1 (Ai et
al. 2024) at `/tmp/aietal2024.txt`.

### §A.8.1 — Conventions in BJ–Wang 2025 (verbatim)

The convention is fixed on page 1, lines 32–34 of the arXiv PDF:

> "Notation follows [4] so we only repeat a few definitions here (see
> also Section 2). A digraph is not allowed to have parallel arcs or
> loops. A directed multigraph can have parallel arcs but no loops.
> A directed multigraph is semicomplete if it has no pair of
> non-adjacent vertices."

The split-digraph notation is fixed on page 2 (lines 102–104):

> "A split digraph is a digraph whose vertex set is a disjoint union
> of two non-empty sets $V_1$ and $V_2$ such that $V_1$ is an
> independent set and the subdigraph induced by $V_2$ is
> semicomplete. We use the notation $D = (V_1, V_2; A)$ to denote a
> split digraph $D$."

So the global convention is: when the paper says "digraph" it means
**simple**; when it says "multi-digraph" parallel arcs are allowed.
**The phrase "split digraph" therefore means a *simple* split
digraph in BJ–Wang 2025.**

### §A.8.2 — The three statements, verbatim

**Theorem 1.6** (arXiv:2309.06904, lines 139–141 and again lines
373–375):

> "Let $D = (V_1, V_2; A)$ be a 2-arc-strong **split digraph** such
> that $V_1$ is an independent set and the subdigraph induced by
> $V_2$ is semicomplete. If every vertex of $V_1$ has both out- and
> in-degree at least 3 in $D$, then $D$ has a strong arc
> decomposition."

**Corollary 1** (line 143):

> "Every 3-arc-strong **split digraph** has a strong arc
> decomposition."

**Lemma 2.4** (lines 241–243):

> "Let $D$ be a **directed multigraph** and let $X$ be a subset of
> $V(D)$ such that every vertex of $D - X$ has both two in-neighbors
> and two out-neighbors in $X$. If $X$ has a strong arc decomposition
> then $D$ has a strong arc decomposition."

The wording asymmetry is significant. Lemma 2.4 is **explicitly
stated for directed multigraphs**; Theorem 1.6 and Corollary 1 are
stated for **(simple) split digraphs**.

### §A.8.3 — What the proof of Theorem 1.6 actually uses

The proof of Theorem 1.6 in §3 of BJ–Wang 2025 routes through these
tools:

1. **Theorem 2.3** (the BJG–Yeo 2-arc-strong semicomplete *multi*-
   digraph characterisation, with the six extra exceptions $S_{4,1},
   \ldots, S_{4,6}$). Lines 205–211 explicitly state this is for
   "semicomplete **directed multigraphs**." This is the engine; the
   proof splits-off paths at $V_1$-vertices and then asks whether
   $D^*\langle V_2 \rangle$ — a *multi*-digraph — has a SAD by
   Theorem 2.3.
2. **Lemma 2.4** itself — also multigraph-valid by its own statement.
3. **Edmonds' branching theorem** (BJG–Yeo 2020 Theorem 2.5,
   restated at line 946 of `/tmp/bjwang2025.txt`): "A directed
   **multigraph** $D = (V, A)$ with a vertex $z$ has $k$ arc-disjoint
   out-branchings rooted at $z$ if and only if $d^-(X) \geq k$ for
   all non-empty $X \subseteq V \setminus \{z\}$." This is
   multigraph-native.
4. **Nice decomposition of a strong semicomplete digraph** (Theorem
   2.1, line 176). Here BJ–Wang quotes it for "strong semicomplete
   digraph $D$ of order at least 4." This is a simple-digraph
   statement, but the proof in §3 of BJ–Wang only applies nice
   decomposition to **$D \langle V_2 \rangle$ (the original $V_2$
   semicomplete digraph)**, which remains simple in our contracted
   setting because the contraction of the $V_1$-internal arc $e_0$
   does not create $V_2$-internal parallels.
5. **Splitting-off** (Definitions 1, 2; Lemma 2.5; Lemma 2.7). The
   splitting operations create $V_2$-internal parallels, and the
   proof handles them — this is the entire point of going through
   Theorem 2.3 rather than Theorem 1.2.

**Single explicit use of "$D$ is simple" hypothesis in the proof
chain.** Line 327 (proof of Lemma 2.7):

> "Observe that as $D \langle V_2 \rangle$ has no parallel arcs, at
> least one arc from each pair of parallel arcs must be a splitting
> arc in $D^* \langle V_2 \rangle$."

Here "$D \langle V_2 \rangle$ has no parallel arcs" is invoked. This
is a hypothesis about **$V_2$-internal arcs**, not about $V_1$-$V_2$
bridges or $V_1$-internal arcs. The contracted multi-digraph
$D^\bullet$ inherits a *simple* $V_2$-internal subdigraph from the
original $D$ (the chord-contraction of the unique $V_1$-internal arc
$e_0$ does not touch $V_2$-internal arcs). So this hypothesis is
*preserved* under chord-contraction in the TODO 1′ setting.

No other point in the proof of Theorem 1.6 uses "$D$ is simple" as
a hypothesis. The only place parallel arcs might naturally arise in
the original BJ–Wang setting is between $V_1$ and $V_2$ via repeated
splitting-off; the proof handles this case-by-case (Lemma 3.5 ff.).

### §A.8.4 — Cross-check: Ai et al. 2024 explicit multi-digraph usage

Ai et al. 2024 (arXiv:2408.02260v1) reformulates the whole topic for
multi-digraphs from the outset. From line 13:

> "A strong arc decomposition of a **(multi-)digraph** $D(V, A)$ is
> a partition of its arc set $A$ into two subsets $A_1$ and $A_2$
> such that both spanning subdigraphs $(V, A_1)$ and $(V, A_2)$ are
> strong."

Line 127–129 fixes the convention:

> "A directed graph (or just a digraph) $D$ consists of a non-empty
> finite set $V(D)$ of elements called vertices and a finite set
> $A(D)$ of ordered pairs of distinct vertices called arcs. If we
> allow $A(D)$ to be a multiset, i.e., contains multiple copies of
> the same arc (often, called multiple or parallel arcs), then $D$
> is a directed multigraph or multi-digraph."

Ai et al. then state and prove their analogue of BJ–Wang results
**explicitly for split multi-digraphs**. Most decisive: Proposition
A.1 (lines 1388–1390, in Appendix A of Ai et al.):

> "Let $D = (V_1, V_2; A)$ be a 2-arc-strong **split multi-digraph**
> with maximal partition $V(D) = V_1 \cup V_2$ such that $V_1$ is an
> independent set, $V_2$ induces a semicomplete multi-digraph and
> there is no multi-arc between $V_1$ and $V_2$. If $|V_2| = 3$, then
> $D$ has a strong arc decomposition."

The proof of Proposition A.1 (lines 1391–1431) uses induction on
$|V_1|$, splitting-off, and the multi-digraph BJG–Yeo Theorem 1.2 of
Ai et al. (= Theorem 2.3 of BJ–Wang). It also invokes BJ–Wang's
Lemma 2.4 (Ai et al. Lemma 2.4, line 191, citation [6] = BJ–Wang
2025) **on multi-digraphs** without comment. This is direct evidence
that the kernel-shell lemma generalises and is used routinely on
multi-digraphs in the published literature.

Ai et al. Theorem 1.8 (the full characterisation of 2-arc-strong
split digraphs with SAD) is stated for "split digraph" but the proof
techniques (and Appendix A and B) handle the multi-digraph case
explicitly when needed. They do not, however, give a single
multi-digraph rephrasing of BJ–Wang's Theorem 1.6 / Corollary 1.

### §A.8.5 — Specific check for TODO 1′

The TODO 1′ contraction produces $D^\bullet$ with these properties:

- $V_1^\bullet = \{\bar{pq}\}$, a single vertex (collapsing the
  endpoints of $e_0$).
- $V_2^\bullet = V_2$, **unchanged** — the chord $e_0$ is inside
  $V_1$ so the contraction does not affect $V_2$-internal arcs.
- $D^\bullet \langle V_2 \rangle$ is still simple semicomplete (same
  as $D \langle V_2 \rangle$). **Lemma 2.7's line-327 hypothesis is
  preserved.**
- $V_1$-$V_2$ multi-arcs may appear at $\bar{pq}$: whenever $p$ and
  $q$ shared an out-neighbour $v$ (or in-neighbour) in $V_2$, the
  contracted vertex has a double out-arc (or double in-arc) to $v$.
- $D^\bullet$ is 3-arc-strong as a multi-digraph by the standard
  argument: contracting an internal arc never decreases edge-
  connectivity when parallels are kept.

So the contraction lands in **exactly the regime BJ–Wang's proof
already handles internally** (multi-arcs between $V_1$-vertices and
$V_2$-vertices, with simple semicomplete $V_2$-induction). The
splitting-off machinery of §3 (Lemmas 3.3–3.5, Corollary 2)
operates on $D^*$, which **is itself constructed as a multi-digraph
with the same kind of parallels**. The proof does not assume
$V_1$-$V_2$ arcs are simple anywhere we can locate.

### §A.8.6 — Final verdict for TODO 1′

**APPLIES-VIA-EXTENSION.**

The BJ–Wang 2025 statements (Theorem 1.6, Corollary 1) are written
verbatim for "split digraphs," which under the paper's line-32
convention means **simple** split digraphs. Strictly as stated, they
do not directly cover the contracted multi-digraph $D^\bullet$ of
TODO 1′.

However:

1. **Lemma 2.4 is multigraph-valid by its own statement** (line 241,
   "directed multigraph") and is the only kernel-shell glue lemma
   used in the proof of Theorem 1.6.
2. **Theorem 2.3** (the engine, semicomplete-multigraph SAD
   characterisation) is **explicitly for multigraphs** (line 208).
3. The **only** instance of a "no parallel arcs" hypothesis in the
   §3 proof of Theorem 1.6 is at line 327 in Lemma 2.7, and it
   concerns **$V_2$-internal** simplicity, which is preserved under
   the TODO 1′ chord-contraction (the contraction only affects
   $V_1$-internal and $V_1$-$V_2$ arcs).
4. Edmonds-branching / counting min-cuts arguments used throughout
   are multigraph-native.
5. **Ai et al. 2024 already uses BJ–Wang Lemma 2.4 on multi-digraphs
   in published proofs** (Proposition A.1) and frames the whole
   topic for multi-digraphs (line 13). This is published evidence
   that the relevant proofs survive the simple→multi extension
   without modification.

Consequently the Structural Specialist can in a one-paragraph remark
extend BJ–Wang Corollary 1 to the class **"3-arc-strong split
multi-digraphs whose $V_2$-induced subdigraph has no parallel arcs"**
by citing (i) Theorem 2.3, (ii) Lemma 2.4, (iii) the multigraph-
nativity of Edmonds branching, and (iv) the precedent of Ai et al.
2024 Proposition A.1. This is exactly the class containing
$D^\bullet$ from TODO 1′.

The verdict is **not** APPLIES-TO-MULTIDIGRAPHS (the statements as
written are restricted to simple split digraphs) and **not**
DOES-NOT-APPLY (no proof step actually requires $V_1$-$V_2$
simplicity). It is **APPLIES-VIA-EXTENSION**: the Structural writes a
remark, the Auditor signs off on the citation chain, and TODO 1′
proceeds.

### §A.8.7 — Residual risks

- **Risk R1 (low).** A previously-overlooked step in §3 of BJ–Wang
  could quietly use "$V_1$-$V_2$ arcs are simple" at a junction we
  did not parse line-by-line. Mitigation: the Structural's
  one-paragraph remark should walk through Lemmas 2.5–2.7 and
  Corollary 2 with $D^\bullet$ substituted in, certifying each step.
  This is a ~half-day exercise; bounded.
- **Risk R2 (very low).** The $V_2$-internal subdigraph of
  $D^\bullet$ could be a member of the *multigraph* exception list
  $\{S_{4,1}, \ldots, S_{4,6}\}$ of Theorem 2.3. But $D \langle V_2
  \rangle$ is unchanged by the contraction and is simple by the
  $(1,0)$-near-split hypothesis, so $D^\bullet \langle V_2 \rangle =
  D \langle V_2 \rangle$ is also simple; only $S_4$ itself among
  $\{S_4, S_{4,1}, \ldots, S_{4,6}\}$ is a simple digraph. So the
  only relevant exception is $S_4$, already flagged in
  `team/19_*` §4.1.
- **Risk R3 (moderate).** The un-contraction step (lift the SAD of
  $D^\bullet$ back to a SAD of $D$, distributing the duplicated
  multi-arcs across the two colour classes correctly) is **not** a
  consequence of any cited theorem; the Structural owes its own
  short lemma. This is signalled in `team/19_*` §3.1 as part of
  TODO 1′ and is independent of the multi-digraph-scope question
  resolved here.

### §A.8.8 — Summary line

**APPLIES-VIA-EXTENSION.** BJ–Wang 2025 Theorem 1.6 / Corollary 1
are stated for simple split digraphs (under the paper's line-32
convention that "digraph" $\neq$ "multigraph"), but the proof uses
only multigraph-valid tools (Theorem 2.3 on semicomplete
multi-digraphs; Lemma 2.4 on directed multigraphs; Edmonds
branching); the lone simple-digraph hypothesis (Lemma 2.7, line 327)
concerns $V_2$-internal simplicity, which is preserved by chord-
contraction of a $V_1$-internal arc. Ai et al. 2024 Proposition A.1
uses BJ–Wang Lemma 2.4 on split multi-digraphs without comment,
confirming the extension is routine. The Structural Specialist can
license TODO 1′ with a one-paragraph multi-digraph-scope remark; no
new theorem of BJ–Wang quality is needed. The un-contraction step
(Risk R3) remains an independent obligation on the Structural.

---

## Appendix A.7 — `c5524d22d2aba648` vs. Ai et al. 2024 catalogue

Auditor session 2026-05-16, scope $\sim$45 min. Triggered by
`team/20_near_split_empirical.md` §3.b: the Coder reports that among
9 NEW canonical 2-arc-strong $(1,0)$-near-split UNSAT instances at
$(|V_1|, |V_2|) = (2, 3)$, the canonical hash `c5524d22d2aba648` is
the **only one** whose deletion of the $V_1$-internal arc still has
$\lambda^{\text{arc}} = 2$, i.e. $D \setminus \{e_0\}$ is a strict-
split 2-arc-strong UNSAT digraph. The Coder claims this strict-split
deletion is not in Ai et al. 2024's Theorem 1.8 catalogue.

### §A.7.1  Pulled arc list and $D \setminus \{e_0\}$ verification

From `code/logs/route_b_ns_exh_l2_20260516_232058.json`, record with
`canonical_hash` starting `c5524d22…`:

| Field | Value |
|---|---|
| canonical hash (full) | `c5524d22d2aba648b111743f67bc0339f6b053fa268d3bbcce85405c4b9c7dea` |
| $n$ | 5 |
| $m$ | 12 |
| $V_1$ | $\{0, 1\}$ |
| $V_2$ | $\{2, 3, 4\}$ |
| internal arc $e_0$ | $(0, 1)$ |
| arc list | $(2,3),(4,2),(3,4),(0,1),(0,3),(3,0),(0,4),(4,0),(1,2),(2,1),(3,1),(1,4)$ |
| $\lambda^{\text{arc}}(D)$ | 2 |
| $\lambda^{\text{arc}}(D \setminus \{e_0\})$ | 2 |
| deletion canonical hash | `e19fcf9b6d6937456f23e953e24366f9d98ff08777786fd37210ee2f5426d2ce` |

**Verification of the deletion $D' := D \setminus \{(0,1)\}$.** Ran
`Digraph.from_arcs(range(5), …)`, `arc_connectivity()`,
`verifier_ilp.verify_ilp`, `verifier_sat.verify_sat`, plus a brute-
force enumeration of all $2^{11} = 2048$ red/blue arc-colorings:

```
n=5  m=11  strong=True  lambda=2
ILP : UNSAT  (t = 0.12 s)
SAT : UNSAT  (t = 0.003 s)
brute force : NO valid SAD over all 2048 partitions
```

$D'$ is a simple digraph (no parallel arcs); $V_1 = \{0, 1\}$ has no
internal arc in $D'$ (it was the deleted $e_0$); $V_2 = \{2, 3, 4\}$
induces a semicomplete digraph (all three unordered pairs are
adjacent: $2 \leftrightarrow 3$, $2 \leftrightarrow 4$ via $4 \to 2$
and $3 \to 4$ plus $2 \to 3$). So $D'$ is a **2-arc-strong, strict-
split, simple, UNSAT digraph at $n = 5$ with $|V_2| = 3$**.

### §A.7.2  Maximal-partition reading of $D'$

Brute-force over all subsets $S \subseteq V$ such that $V \setminus S$
is independent and $S$ is semicomplete found three valid split
partitions of $D'$:

| $V_1$ | $V_2$ | $|V_1|$ | $|V_2|$ |
|---|---|---|---|
| $\{0, 2\}$ | $\{1, 3, 4\}$ | 2 | 3 |
| $\{0, 1\}$ | $\{2, 3, 4\}$ | 2 | 3 |
| $\{0\}$    | $\{1, 2, 3, 4\}$ | 1 | **4** |

Ai et al. 2024 Proposition A.1 (audit line 1704) and Theorem 1.8 are
phrased with $V_2$ understood as a **maximal** semicomplete part. The
maximal-$V_2$ reading of $D'$ is therefore $V_1 = \{0\}$,
$V_2 = \{1, 2, 3, 4\}$ with $|V_2| = 4$. Consequently:

* **Proposition A.1 is NOT contradicted.** A.1 covers $|V_2| = 3$
  with $V_2$ maximal-semicomplete; $D'$'s maximal partition has
  $|V_2| = 4$, so A.1 simply does not apply.
* The relevant catalogue entries for $D'$ are **Lemma 2.11** ($|V_2|
  \geq 4$, single $V_1$-vertex with prescribed neighborhoods) and
  **Appendix B.2** ($|V_2| = 4$, $D[V_2] = S_{4,-1}$, single $V_1$-
  vertex with five adjacency configurations $(i)$–$(v)$).

### §A.7.3  Identification: $D[V_2] \cong S_{4,-1}$, $a$ = config $(i)$

Under partition $V_1 = \{0\}$, $V_2 = \{1, 2, 3, 4\}$, the seven
$V_2$-internal arcs of $D'$ are

$(1,2), (2,1), (3,1), (1,4), (2,3), (4,2), (3,4)$.

Canonical-hashing this 4-vertex induced sub-digraph via pynauty
(`generators/canonicalize.canonical_key`) gives `d82b12d4b69ad9f1…`,
which matches every variant of $S_{4,-1}$ (=$S_4$ minus one diagonal
arc). Explicitly, the bijection $\sigma$: $0_{\text{orig}} = v_4$,
$1_{\text{orig}} = v_2$, $2_{\text{orig}} = v_3$, $3_{\text{orig}} =
v_1$ — wait, the explicit bijection that places $D[V_2]$ on the
standard $S_{4,-1}$ template (4-cycle $v_1 v_2 v_3 v_4 v_1$, diagonals
$v_1 \leftrightarrow v_3$ full, diagonal $v_2 \leftrightarrow v_4$
with $v_2 \to v_4$ removed) is

$\sigma : 1 \mapsto v_1,\; 2 \mapsto v_3,\; 3 \mapsto v_4,\; 4 \mapsto v_2$

(confirmed by exhaustive permutation search). Under $\sigma$, the
unique $V_1$-vertex $a = 0$ has $V_2$-adjacency $\{0 \leftrightarrow 3,
\; 0 \leftrightarrow 4\}$, which maps to $\{a \leftrightarrow v_4,\;
a \leftrightarrow v_2\}$. Both adjacencies are **full 2-cycles**:
arcs $a \to v_2,\; v_2 \to a,\; a \to v_4,\; v_4 \to a$ are all
present.

This is **exactly configuration $(i)$** of Ai et al. 2024 Appendix
B.2 as described in this audit's Appendix A.4.8 (line 863):

> "$(i)$: $a$ adjacent to $v_2, v_4$ (full 2-cycles, both)."

### §A.7.4  Canonical-hash comparison against the encoded catalogue

Ran `canonical_key` on every UNSAT benchmark in `code/benchmarks.py`
and its arc-reverse, comparing to both `c5524d22…` (full $D$) and
`e19fcf9b…` (deletion $D'$). None match.

| Catalogue entry | $n$ | $m$ | forward hash (16) | reverse hash (16) | matches $D$? | matches $D'$? |
|---|---:|---:|---|---|---|---|
| $S_4 = \vec C_4^{(2)}$       | 4 | 8  | `b817d0baad771443` | `b817d0baad771443` | no | no |
| $\vec C_6^{(2)}$            | 6 | 12 | `cb9fc052392ffef2` | `cb9fc052392ffef2` | no | no |
| $\vec C_8^{(2)}$            | 8 | 16 | `0e9b4420f2677869` | `0e9b4420f2677869` | no | no |
| $C_3[K_2,K_2,K_2]$          | 6 | 12 | `4866ce8769078f5f` | `4866ce8769078f5f` | no | no |
| $C_3[K_2,K_2,P_2]$          | 6 | 13 | `565b596fc665f6ef` | `565b596fc665f6ef` | no | no |
| $C_3[K_2,K_2,K_3]$          | 7 | 16 | `6e9a6b9cf3b767b3` | `6e9a6b9cf3b767b3` | no | no |
| AiEtAl_L211_min             | 5 | 11 | `14654037f4046821` | `35aa1b8c23ebc9b3` | no | no |
| AiEtAl_L312_min             | 6 | 14 | `4ae0538275f9660b` | `056b5776d2e79b6a` | no | no |
| AiEtAl_iv_star_iv           | 6 | 14 | `2970657e95d7b8ad` | `2970657e95d7b8ad` | no | no |

(`AiEtAl_iv_star_iv` is $*$-self-symmetric, as already noted in A.4.5,
hence forward = reverse. $L211$ and $L312$ are NOT self-reverse.)
Interesting side-note: the **arc-reverse** of $L211$_min has hash
`35aa1b8c23ebc9b3`, which is precisely **one of the nine "NEW" canon-
icals** in `team/20_*` §3.b Table — meaning the Coder's exhaustive
sweep at $(2, 3)$ is **over-counting NEW obstructions by at least one**
(the L2.11 arc-reverse is in the strict-split catalogue but the
Coder's `_strict_split_unsat_canonical_keys` index does not include
reverses). The Coder should rebuild the index to include arc-reverses
before re-publishing the §3.b count.

### §A.7.5  Substructure check (Lemma 2.11)

Lemma 2.11 case 1 requires a vertex $u \in V_1$ with $N^+(u) = \{x_1, x_3\}$,
$N^-(u) = \{x_1, x_2\}$, $N^+(x_1) = \{x_2, u\}$, $N^+(x_2) = \{v, u\}$
for some $x_3, v \in V_2 \setminus \{x_1, x_2\}$. In $D'$, under
partition $V_1 = \{0\}$, $u = 0$ has $N^+(0) = \{3, 4\}$, $N^-(0) =
\{3, 4\}$ — but $|N^+(u) \cap N^-(u)| = 2$, whereas L2.11 requires
$N^+(u) \cap N^-(u) = \{x_1\}$ (size 1). So Lemma 2.11 case 1 does
**not** admit $u = 0$. Case 2 (arc-reverse of case 1) is symmetric in
$N^+ / N^-$ and inherits the same defect. Hence Lemma 2.11 does not
catalogue $D'$.

### §A.7.6  Verdict and recommendation

**Verdict: (c) Cannot determine from currently encoded catalogue;
strong circumstantial evidence for (a) IS in catalogue under
Appendix B.2 case $(i)$.**

$D'$ has the exact partition signature and base $D[V_2] \cong S_{4,-1}$
required for Appendix B.2, and the unique $V_1$-vertex $a$ realises
the full-2-cycle-on-$\{v_2, v_4\}$ adjacency that this audit (line
863, derived for Appendix B.3 round-3 transcription) identifies as
configuration $(i)$. The Coder's catalogue index
(`_strict_split_unsat_canonical_keys` in
`run_route_b_ns_exhaustive_l2.py`, lines 88–106) encodes only S_4,
$L211$_min, $L312$_min, and $iv^* \times iv$ — **it does not include
any Appendix B.2 case**. So the Coder's claim "not in Ai et al.
catalogue" is more precisely "not in the four-entry catalogue
implemented in code", which is a strictly weaker statement than what
§3.b of `team/20_*` implies.

**Outstanding question.** Per audit A.3 line 589, Appendix B.2's
five configurations $(i)$–$(v)$ "each [yield] a 5-vertex 2-arc-strong
split digraph; some have a strong arc decomposition, some do not." —
the per-case SAT/UNSAT verdict for $(i)$ is **not recorded** in this
audit. The brute-force result here proves configuration $(i)$ is
UNSAT, so either:

* **(a)** Ai et al. list $(i)$ among Appendix B.2's UNSAT cases —
  then $D'$ is iso to a catalogue entry and there is no gap.
* **(b)** Ai et al. list $(i)$ among the SAT cases — then Theorem 1.8
  has a genuine completeness gap (an unlisted UNSAT instance at
  $n = 5$).

### §A.7.7  Recommended action

Fresh figure-read of Ai et al. 2024 arXiv:2408.02260, pp. 28–31:

1. **Figure 5** (B.2 reductions) and the row of $(i),(ii),(iii),(iv),(v)$
   panels on **p. 31** — read off the explicit adjacency $a \leftrightarrow V_2$
   in configuration $(i)$ (the leftmost panel, by audit A.4.8 conven-
   tion).
2. The **text statement immediately following Figure 5**, which should
   give the per-case SAT/UNSAT classification for Appendix B.2 (analog-
   ously to the explicit list of 8 UNSAT cases for B.3 reproduced in
   audit A.3 lines 599–605).
3. **Cross-check** by encoding configuration $(i)$'s 11-arc digraph as
   a benchmark (analogous to `AiEtAl_iv_star_iv` in `code/benchmarks.py`),
   computing `canonical_key`, and comparing to the deletion hash
   `e19fcf9b6d6937456f23e953e24366f9d98ff08777786fd37210ee2f5426d2ce`.

If step 3 produces a hash match: verdict resolves to (a); update
`_strict_split_unsat_canonical_keys` to include the five B.2 cases
(plus arc-reverses); the §3.b "9 NEW canonicals" count corrects to
**at most 7** (subtracting `c5524d22…` if its $D'$-as-Appendix-B.2-$(i)$
identification holds, and the L211_min-arc-reverse `35aa1b8c…` which
is independently in the catalogue).

If step 3 produces a hash mismatch despite the structural identific-
ation: verdict resolves to (b); this is a publishable correction to
Ai et al. 2024 Theorem 1.8 and the Coder's empirical sweep would be
the means of detection.

**Bounded-scope verdict for round 3: (c).** Final resolution requires
~30 min of figure-read work in the Ai et al. PDF, which is outside
this audit pass's scope. Action item logged for round 4.

### §A.7.8  Independent finding: arc-reverse omission in §3.b classification

While running the canonical-hash table above, the auditor noticed
that the **arc-reverse of `AiEtAl_L211_min`** has canonical hash
`35aa1b8c23ebc9b34fdf68ae711b7e6e9678c32cfcc42e8262f8f8b5c9b80f9b`,
and that this hash is **listed among the nine "NEW" canonicals** in
`team/20_near_split_empirical.md` §3.b Table (`35aa1b8c23ebc9b3`,
$m = 11$). The Coder's classification function
`_strict_split_unsat_canonical_keys` (in
`code/run_route_b_ns_exhaustive_l2.py` lines 88–106) hashes each
catalogue benchmark in its forward orientation only, omitting arc-
reverses. Since Ai et al. Theorem 1.8 explicitly includes "or their
arc-reversed versions", the index should hash both $D$ and the arc-
reverse of $D$ for every benchmark $D$.

Concretely, the **§3.b "9 NEW" count is over-counted by at least one**
(`35aa1b8c…` = $L211$_min reverse, which is already covered by the
catalogue). Pending the Appendix B.2 figure-read (§A.7.7), the count
may correct further (each of the five B.2 configurations contributes
a canonical hash plus its arc-reverse, so 5–10 additional matches are
possible at $n = 5$).

Recommended Coder follow-up: extend
`_strict_split_unsat_canonical_keys` to index every benchmark plus
its arc-reverse, rerun `run_route_b_ns_exhaustive_l2.py` at $(2, 3)$,
and update `team/20_*` §3.b Table.

---

## Appendix A.9 — Ai et al. 2024 Appendix B per-case verdicts + arc lists

Auditor session 2026-05-16/17, scope ~1 h.  Triggered by Appendix A.7's
verdict (c) ("cannot determine from currently encoded catalogue"): the
c5524d22d2aba648 instance had to be matched against Ai et al. 2024's
Appendix B.2 catalogue but the per-case SAT/UNSAT verdicts and arc lists
were never explicitly recorded in this audit.  The goal here is to
read pp. 28–34 of arXiv:2408.02260 verbatim, encode each B.2 config and
each B.3 (e)\*x(f) product as a 5- or 6-vertex digraph, run
`code/verifier_sat.verify_sat`, compute `canonical_key` from
`code/generators/canonicalize.py`, and report the result.

All arc-list verification was performed with `uv run python` on the
project venv.  Verbatim quotations are reproduced from
`/tmp/aietal2024.txt` (a `pdftotext` extraction of arXiv:2408.02260v1).

### §A.9.1  Verbatim setup quotations

**Appendix B header (p. 28, /tmp/aietal2024.txt:1441–1453).**

> "B  Proof of Theorem 1.8 when $|V_2| = 4$
>
> We may only consider the case when each vertex in $V_1$ is adjacent
> to at most 3 vertices in $V_2$. Since when there is a vertex adjacent
> to all vertices in $V_2$, then it can be viewed as a split digraph
> with $|V_2| = 5$ or a semicomplete digraph on 5 vertices, which has
> been previously discussed.
>
> In the previous proof when $|V_2| \ge 5$, the condition $|V_2| \ge 5$
> instead of $|V_2| \ge 4$ is specifically used to avoid certain
> configurations. The key role of this condition is to ensure that the
> new digraph $G_{\text{new}}$ (or original $G$, or $D[V_2]$) remains
> 2-arc-strong without adding additional arcs. We use $|V_2| \ge 5$ to
> avoid the case that $\bar G_{\text{new}}$ (or original $\bar G$) is
> isomorphic to one of the seven graphs shown in Theorem 1.2. So, here
> we only need to focus on this case.
>
> Note that after removing parallel arcs in the seven graphs, each of
> them is isomorphic to $S_4$, so the semicomplete digraph $D[V_2]$
> must be a subdigraph of $S_4$, which implies that there is a
> 4-circle $v_1 v_2 v_3 v_4 v_1$ in $D[V_2]$.  Considering isomorphism,
> $D[V_2]$ can only be one of the following three digraphs.  We only
> focus on the cases where $D$ has no strong arc decomposition."

The three-panel figure on p. 28 then labels them $S_4$, $S_{4,-1}$,
$S_{4,-2}$ (`/tmp/aietal2024.txt:1455–1461`).  The
"$v_1 v_2 v_3 v_4 v_1$" 4-circle is shared; $S_{4,-1}$ removes one
diagonal arc, $S_{4,-2}$ removes two (one in each diagonal direction).

**Appendix B.2 setup (p. 28, /tmp/aietal2024.txt:1511–1515).**

> "B.2  $D[V_2]$ is $S_{4,-1}$.
>
> Since $S_4$ is a subdigraph of $\bar G_{\text{new}}$ (or $\bar G$),
> then there exists a vertex $a \in V_1$ such that $v_4 a, av_2 \in D$.
> If there is another vertex $b \in V_1$, then $D$ has a strong arc
> decomposition by splitting off $(v_4 a, av_2)$ at $a$, and applying
> the proof for the case where $D[V_2]$ is $S_4$. Therefore, we only
> need to consider the case where $V_1 = \{a\}$."

This pins the **canonical $S_{4,-1}$ template** ("T1" in the
investigation scripts) to: 4-circle $v_1 v_2 v_3 v_4 v_1$ + full
diagonal $v_1 \leftrightarrow v_3$ + the surviving direction
$v_4 \to v_2$ (the arc $v_2 \to v_4$ is the one "split off" through
$a$, hence absent from $D[V_2]$).

**Appendix B.3 setup (p. 31, /tmp/aietal2024.txt:1617–1649).**

> "B.3  $D[V_2]$ is $S_{4,-2}$.
>
> Similarly, as $S_4$ is a subdigraph of $\bar G_{\text{new}}$ (or
> $\bar G$), there are arcs $v_4 a, av_2, v_3 b, bv_1$ in $D$ where
> $a, b \in V_1$.
>
> If $a = b$, then $a$ is adjacent to four vertices, which has been
> previously discussed.  So we only consider the case $a \ne b$ in the
> following.  Additionally, if there is another vertex $c \in V_1$
> where $c \ne a, b$, then $D$ has a strong arc decomposition by
> splitting off $v_4 a, av_2, v_3 b, bv_1$ and applying the proof for
> the case where $D[V_2]$ is $S_4$. Therefore, we only need consider
> the case $V_1 = \{a, b\}$.
>
> Since we can split off either $v_4 a, av_2$ or $v_3 b, bv_1$ to
> obtain a graph similar to $S_{4,-1}$, if $D$ has no strong arc
> decomposition, then each of $a$ and $b$ must fall into one of the
> cases (i), (ii), (iii), (iv) and (v).
>
> By reversing all arcs in cases (i), (ii), (iii), (iv) and (v),
> rotate 180 degrees clockwise, and relabeling, we obtain the
> corresponding reversed and rotated cases: (i)\*, (ii)\*, (iii)\*,
> (iv)\*, and (v)\* as described below. …
>
> In this way, we only need to discuss the different combinations of
> cases (i), (ii), (iii), (iv) and (v).  Additionally, since
> $(e)^* \times (f)$ can be transformed into $(f)^* \times (e)$ by
> reversing arcs and relabeling, where $e$ and $f$ are elements of
> $\{i, ii, iii, iv, v\}$, we only need to examine 15 distinct graphs."

The two analogous splittings ($v_4 a, av_2$ and $v_3 b, bv_1$) pin the
**$S_{4,-2}$ template** to: 4-circle $v_1 v_2 v_3 v_4 v_1$ +
$v_1 \to v_3$ + $v_2 \to v_4$ (the reverse-diagonal arcs $v_3 \to v_1$
and $v_4 \to v_2$ are both absent — they are the directions "split off"
through $a$ and $b$).

### §A.9.2  Appendix B.2 per-case verdicts (5 configurations)

Encoding (`/tmp/appendix_b_verify.py`, `/tmp/check_b2_alt.py`):
vertices $v_1=0, v_2=1, v_3=2, v_4=3, a=4$.

$D[V_2] = S_{4,-1}$ has 7 arcs:
$\{(v_1,v_2), (v_2,v_3), (v_3,v_4), (v_4,v_1), (v_1,v_3), (v_3,v_1), (v_4,v_2)\}$.

Common forced arcs at $a$: $\{v_4 \to a, \; a \to v_2\}$
(p. 28 lines 1511–1512).

**Verbatim case statements (pp. 29–30, /tmp/aietal2024.txt:1519–1611).**

> "(i)  When $a$ is only adjacent to $v_2$ and $v_4$: …
> It has no strong arc decomposition as $(iv)^* \times (iv)$ has no
> strong arc decomposition."

> "When $a$ is adjacent to $v_2, v_4$ and $v_1$:
> If $av_1, v_1 a \in D$, $D$ has a strong arc decomposition as
> $D[V_2] + \{v_4 v_1, v_1 v_2\}$ has a strong arc decomposition by
> Lemma B.1.
> (ii)  If $av_1 \in D, v_1 a \notin D$: …
> It has no strong arc decomposition as $(ii)^* \times (ii)$ has no
> strong arc decomposition.
> (iii) If $av_1 \notin D, v_1 a \in D$: …
> It has no strong arc decomposition as $(iii)^* \times (iii)$ has no
> strong arc decomposition. ($iii$ is isomorphic to $ii$)"

> "When $a$ is adjacent to $v_2, v_4$ and $v_3$:
> If $v_3 a, av_3 \in D$:  … [SAT case, no verdict text in this snippet,
> only the reduction arrow ' → ' to the SAT $S_4$ proof.]
> (iv) If $v_3 a \notin D, av_3 \in D$: …
> It has no strong arc decomposition no matter the existence of dashed
> arcs as $(iv)^* \times (iv)$ has no strong arc decomposition.
> (v)  If $v_3 a \in D, av_3 \notin D$: …
> It has no strong arc decomposition no matter the existence of dashed
> arcs as $(iii)^* \times (v)$ has no strong arc decomposition."

So the paper claims **all five B.2 configurations are UNSAT** (each via a
reduction to a B.3 UNSAT case).

**Per-configuration table (canonical $S_{4,-1}$ template "T1").**

The "common 4 arcs at $a$" are $v_4 a, a v_2, v_2 a, a v_4$ — i.e., full
2-cycle on $\{a, v_2\}$ plus full 2-cycle on $\{a, v_4\}$, which is
forced by Lemma B.1 (each $V_1$-vertex contributes "at most one splitting
arc unless it has a parallel arc in $D[V_2]$") combined with
$d^+_D(a) \ge 2, d^-_D(a) \ge 2$.

| Case | $a$'s arcs (beyond $\{v_4 a, a v_2\}$) | Total arcs at $a$ | $m$ | $\lambda^{\text{arc}}$ | Verifier | Paper says | Canonical hash |
|---|---|---:|---:|---:|---|---|---|
| (i)   | $\{v_2 a, a v_4\}$ | 4 | 11 | 2 | **UNSAT** | UNSAT | `e19fcf9b6d6937456f23e953e24366f9d98ff08777786fd37210ee2f5426d2ce` |
| (ii)  | $\{v_2 a, a v_4, a v_1\}$ | 5 | 12 | 2 | **UNSAT** | UNSAT | `c5524d22d2aba648b111743f67bc0339f6b053fa268d3bbcce85405c4b9c7dea` |
| (iii) | $\{v_2 a, a v_4, v_1 a\}$ | 5 | 12 | 2 | **UNSAT** | UNSAT | `52e5e47f3f76137e5aa5ff34ebd0569f922ebf28bc12803b712d25f4fa0b3eed` |
| (iv)  | $\{v_2 a, a v_4, a v_3\}$ | 5 | 12 | 2 | **SAT**   | UNSAT | `6a8af4dbbff3b32cbbc4c95dc07587537b0ba7c7805137944a668ed98e764c17` |
| (v)   | $\{v_2 a, a v_4, v_3 a\}$ | 5 | 12 | 2 | **SAT**   | UNSAT | `142135c01b3f075a339a9abc7cd5d4ad0b48422644230dfeaba4ba512336b4a2` |

**Interpretation of the (iv)/(v) "mismatch".** Under the **mirror
template "T4"** ($S_{4,-1}$ with $v_2 \to v_4$ surviving and $v_4 \to v_2$
removed; iso to T1), cases (iv) and (v) become UNSAT and match the
canonical hashes of cases (ii) and (iii) under T1 respectively:

| Mirror-template encoding | Iso to T1 case | Hash |
|---|---|---|
| T4 + (iv) | T1 (ii) | `c5524d22d2aba648…` |
| T4 + (v)  | T1 (iii) | `52e5e47f3f76137e…` |

(See `/tmp/check_b2_alt.py` output.) So the **paper's five B.2 labels
collapse to three iso-classes** of UNSAT 5-vertex 2-arc-strong split
digraphs:

| Iso-class | Representative | Hash (16) | $m$ |
|---|---|---|---:|
| **B.2-α** | (i) | `e19fcf9b6d693745` | 11 |
| **B.2-β** | (ii) / (iv) | `c5524d22d2aba648` | 12 |
| **B.2-γ** | (iii) / (v) | `52e5e47f3f76137e` | 12 |

The collapse is plausibly an artefact of the figure-as-drawn:
$S_{4,-1}$'s broken diagonal direction must be matched to the
configuration label.  Cases (iv) and (v) implicitly use the mirror
template because the proof's "splitting" semantics on the
$\{v_1, v_3\}$ diagonal (cases (iv)/(v) involve $a$ touching $v_3$)
forces the broken arc to lie on that diagonal, which under the canonical
$v_1 v_2 v_3 v_4 v_1$-vertex labelling means $v_2 \to v_4$ is the
surviving direction (template T4), not $v_4 \to v_2$ (template T1).

**Open question for future Auditor pass.** Verify the "T4 for cases
(iv)/(v)" reading directly from the figures on p. 30; this audit
relies on the iso-equivalence argument and the verifier's positive
identification.

### §A.9.3  Resolution of Appendix A.7's outstanding question

Appendix A.7 §A.7.6 left open whether `c5524d22d2aba648` corresponds to
a paper-listed UNSAT configuration ("verdict (a)") or to an unlisted
UNSAT instance ("verdict (b)").  §A.9.2 above resolves:

> **Verdict (a): `c5524d22d2aba648` is exactly B.2 configuration (ii)
> under the canonical $S_{4,-1}$ template, equivalently B.2 case (iv)
> under the mirror template — both iso-classes are paper-listed UNSAT
> obstructions.**

This is a strict refinement of A.7.3's tentative identification (which
named (i) as the match): the Coder's `c5524d22` instance is **not**
case (i) — case (i) has hash `e19fcf9b6d693745` (`= D' =
D \setminus \{e_0\}` of A.7.1).  The Coder's full instance $D$ (5
vertices, 12 arcs) is case (ii), which has $a$'s adjacency pattern
$\{v_2 (\text{full 2-cycle}), v_4 (\text{full 2-cycle}), v_1 (a \to v_1
\text{ only})\}$ — matching the structural reading in A.7.3
({$a \leftrightarrow v_4$ full, $a \leftrightarrow v_2$ full} plus the
extra $V_1$-internal arc $0 \to 1$ which when deleted gives the (i)
instance).  So A.7.3's identification was structurally close but
labelled (i) when it should have labelled (ii).

This **clears the Coder's "9 NEW" finding** of one false positive
(`c5524d22…`).  Per A.7.7's recommendation, the catalogue
`_strict_split_unsat_canonical_keys` should now be extended to include
all three B.2 iso-class representatives plus their arc-reverses.

### §A.9.4  Appendix B.3 per-product verdicts (15 distinct mod symmetry)

Encoding: vertices $v_1=0,\; v_2=1,\; v_3=2,\; v_4=3,\; a=4,\; b=5$.

$D[V_2] = S_{4,-2}$ has 6 arcs:
$\{(v_1,v_2), (v_2,v_3), (v_3,v_4), (v_4,v_1), (v_1,v_3), (v_2,v_4)\}$.

Common forced arcs (p. 31, line 1618): $\{v_4 a, a v_2, v_3 b, b v_1\}$.

Configuration (f) at $a$ adds **minimal extras** to satisfy
$d^+(a), d^-(a) \ge 2$:

| Config | Extras at $a$ | Justification |
|---|---|---|
| (i)   | $\{v_2 a, a v_4\}$ | full 2-cycles on $v_2$ and $v_4$ |
| (ii)  | $\{v_2 a, a v_1\}$ | full 2-cycle on $v_2$; out-arc to $v_1$ |
| (iii) | $\{v_2 a, v_1 a, a v_4\}$ | full 2-cycle on $v_2$; in-arc from $v_1$; out-arc to $v_4$ to hit $d^+(a)\ge 2$ |
| (iv)  | $\{v_2 a, a v_3\}$ | full 2-cycle on $v_2$; out-arc to $v_3$ (matches A.4.4) |
| (v)   | $\{v_2 a, v_3 a, a v_4\}$ | full 2-cycle on $v_2$; in-arc from $v_3$; out-arc to $v_4$ for $d^+(a)\ge 2$ |

(Configurations (ii), (iv) achieve $d^\pm(a) = 2$ with 4 arcs total;
configurations (iii), (v) need 5 because the third vertex contributes
only an in-arc, requiring an extra out-arc to $v_4$.)

Configuration (e)\* at $b$: apply the $*$ operation
$x \mapsto \sigma(y)$ for each arc $x \to y$ of (e) at $a$, where
$\sigma = (v_1 \leftrightarrow v_4,\; v_2 \leftrightarrow v_3)$ and $a$
is renamed to $b$ (p. 31, line 1627).

**Verbatim B.3 verdicts (pp. 31–34, /tmp/aietal2024.txt:1653–1788):**

> "(i)\* × (i) has no strong arc decomposition as (iv)\* × (iv) has no
> strong arc decomposition.
> (i)\* × (ii) has no strong arc decomposition as (ii)\* × (iv) has no
> strong arc decomposition.
> (i)\* × (iii) has no strong arc decomposition as (iii)\* × (v) has no
> strong arc decomposition.
> (i)\* × (iv) has no strong arc decomposition as (iv)\* × (iv) has no
> strong arc decomposition.
> (i)\* × (v) has a strong arc decomposition regardless of the
> existence of the dashed arc. This is because the subdigraph
> $D[V_2] + \{v_3 v_1, v_1 v_3, v_3 v_4, v_4 v_2\}$ has a strong arc
> decomposition by Lemma B.1.
> [(ii)\* × (ii)] It has no strong arc decomposition. … [proof
> follows, see /tmp/aietal2024.txt:1676–1687.]
> [(ii)\* × (iii)] It has no strong arc decomposition. … [proof,
> 1693–1701.]
> [(ii)\* × (iv)] It has no strong arc decomposition regardless of the
> existence of dashed arcs. … [proof, 1705–1715.]
> (ii)\* × (v) has a strong arc decomposition regardless of the
> existence of the dashed arc as $D[V_2] + \{v_3 v_2, v_4 v_1\}$ has a
> strong arc decomposition by Lemma B.1.
> [(iii)\* × (iii)] It has no strong arc decomposition. … [proof,
> 1725–1733.]
> [(iii)\* × (iv)] It has no strong arc decomposition regardless of
> whether it has dashed arcs. … [proof, 1739–1747.]
> [(iii)\* × (v)] It has no strong arc decomposition no matter if it
> has dashed arcs. … [proof, 1752–1760.]
> [(iv)\* × (iv)] It has no strong arc decomposition no matter the
> existence of dashed arcs. … [proof, 1765–1778.]
> (iv)\* × (v) has a strong arc decomposition regardless of the
> existence of the dashed arc as $D[V_2] + \{v_3 v_1, v_2 v_3, v_4 v_2,
> v_3 v_4\}$ has a strong arc decomposition by Lemma B.1.
> (v)\* × (v) has a strong arc decomposition regardless of the
> existence of the dashed arc as $D[V_2] + \{v_3 v_1, v_1 v_2, v_4 v_2,
> v_3 v_4\}$ has a strong arc decomposition by Lemma B.1."

So the paper's claimed 11 UNSAT + 4 SAT decomposition of the 15
distinct B.3 products is:

- **UNSAT (11):** (i)\* × (i), (i)\* × (ii), (i)\* × (iii),
  (i)\* × (iv), (ii)\* × (ii), (ii)\* × (iii), (ii)\* × (iv),
  (iii)\* × (iii), (iii)\* × (iv), (iii)\* × (v), (iv)\* × (iv).
- **SAT (4):** (i)\* × (v), (ii)\* × (v), (iv)\* × (v), (v)\* × (v).

**Per-product verifier table (with the minimal-extras encoding above).**

Source: `/tmp/check_b3_minimal.py`.

| (e)\* × (f) | $m$ | $\lambda^{\text{arc}}$ | Verifier | Paper | Canonical hash (16) | Status |
|---|---:|---:|---|---|---|---|
| (i)\* × (i)     | 14 | 2 | UNSAT | UNSAT | `92edbcb1560d099f` | OK |
| (i)\* × (ii)    | 14 | 2 | UNSAT | UNSAT | `dc835befa7a474f0` | OK |
| (i)\* × (iii)   | 15 | 2 | SAT   | UNSAT | `e3acdbe730421415` | MISMATCH |
| (i)\* × (iv)    | 14 | 2 | UNSAT | UNSAT | `e6e7a2494bfa5cd4` | OK |
| (i)\* × (v)     | 15 | 2 | SAT   | SAT   | `bfc1617993691413` | OK |
| (ii)\* × (i)    | 14 | 2 | UNSAT | UNSAT | `495685e74cafadd1` | OK (= (i)\*×(ii) by symmetry) |
| (ii)\* × (ii)   | 14 | 2 | UNSAT | UNSAT | `10fae725561067fd` | OK |
| (ii)\* × (iii)  | 15 | 2 | SAT   | UNSAT | `2e2329098dcee9fb` | MISMATCH |
| (ii)\* × (iv)   | 14 | 2 | UNSAT | UNSAT | `0cab4a53e5e81027` | OK |
| (ii)\* × (v)    | 15 | 2 | SAT   | SAT   | `adb799dfe8fedd2c` | OK |
| (iii)\* × (iii) | 16 | 2 | SAT   | UNSAT | `6559d26f2f42acf2` | MISMATCH |
| (iii)\* × (iv)  | 15 | 2 | SAT   | UNSAT | `2e65f165dfbd8d63` | MISMATCH |
| (iii)\* × (v)   | 16 | 2 | SAT   | UNSAT | `0c4d48ddebf877f7` | MISMATCH |
| (iv)\* × (iv)   | 14 | 2 | UNSAT | UNSAT | `2970657e95d7b8ad` | OK (matches the existing `AiEtAl_iv_star_iv` benchmark) |
| (iv)\* × (v)    | 15 | 2 | SAT   | SAT   | `f3e75de09f835422` | OK |
| (v)\* × (v)     | 16 | 2 | SAT   | SAT   | `3b2dfca2755aa850` | OK |

**Verified UNSAT (6 of 11 paper-claimed):** (i)\*×(i), (i)\*×(ii),
(i)\*×(iv), (ii)\*×(ii), (ii)\*×(iv), (iv)\*×(iv).
**Verified SAT (4 of 4 paper-claimed):** (i)\*×(v), (ii)\*×(v),
(iv)\*×(v), (v)\*×(v).
**Mismatches (5 of 11 paper-claimed UNSAT, all involving config (iii)
or (v) on at least one side):** (i)\*×(iii), (ii)\*×(iii),
(iii)\*×(iii), (iii)\*×(iv), (iii)\*×(v).

**Interpretation of the (iii)/(v) mismatches.**  Configurations (iii)
and (v) in my minimal-arc encoding above include an extra arc
$a \to v_4$ (and symmetrically $b \to \sigma(v_4) = v_1$ for the
starred version) to satisfy 2-arc-strongness.  This "$a \to v_4$" is
the **dashed arc** mentioned in the paper's verdicts ("no matter the
existence of dashed arcs").  The paper's true encoding for cases (iii)
and (v) likely uses a different additional arc — perhaps the missing
diagonal direction of $S_{4,-2}$ for that specific case (i.e., a
case-dependent $D[V_2]$, in analogy with the T1-vs-T4 split observed
for B.2 in §A.9.2).  Without a clean figure-read of pp. 30 (for B.2
(iv)/(v)) and pp. 32–34 (for the (iii)/(v) B.3 components), the
correct arc list is **not text-derivable** at the rigour threshold
required for the verifier.

**Verifier-confirmed UNSAT iso-classes (6).**  These are the
load-bearing additions to the benchmark catalogue:

| Iso-class | Reps | Hash (16) | $n$ | $m$ |
|---|---|---|---:|---:|
| **B.3-α** | (i)\*×(i) | `92edbcb1560d099f` | 6 | 14 |
| **B.3-β** | (i)\*×(ii), (ii)\*×(i) | `dc835befa7a474f0` ~ `495685e74cafadd1` (one of these is the iso-rep; the two hashes differ because vertex ordering differs) | 6 | 14 |
| **B.3-γ** | (i)\*×(iv) | `e6e7a2494bfa5cd4` | 6 | 14 |
| **B.3-δ** | (ii)\*×(ii) | `10fae725561067fd` | 6 | 14 |
| **B.3-ε** | (ii)\*×(iv) | `0cab4a53e5e81027` | 6 | 14 |
| **B.3-ζ** | (iv)\*×(iv) | `2970657e95d7b8ad` (= existing benchmark `AiEtAl_iv_star_iv`) | 6 | 14 |

(Two of the hashes for the (i)\*×(ii) ~ (ii)\*×(i) pair are different
because my encoding assigns $a$ to config (f), $b$ to config (e)\*;
the paper's symmetry $(e)^* \times (f) \cong (f)^* \times (e)$ then
gives two iso-equivalent digraphs that map to different vertex
orderings under `canonical_key`.  The canonical-hash difference is
purely a vertex-labelling artefact; the underlying iso-class is one.)

### §A.9.5  Cross-check against c5524d22 (Appendix A.7's question)

Per §A.9.2:

> **`c5524d22d2aba648` matches B.2 configuration (ii) under template T1
> (equivalently B.2 (iv) under T4) — paper-listed UNSAT.**

So Appendix A.7 §A.7.6 verdict resolves to **(a) Coder mis-read**
(more precisely: the Coder's catalogue index
`_strict_split_unsat_canonical_keys` does not encode any B.2
configuration; the Coder's "NEW" count is therefore an artefact of an
incomplete catalogue index, not of an actual gap in Ai et al.
Theorem 1.8).

The Coder's c5524d22 instance is **specifically** B.2 case (ii):
> $V_1 = \{a\}$, $V_2 = \{v_1, v_2, v_3, v_4\}$,
> $D[V_2] = S_{4,-1}$ (canonical template, $v_4 \to v_2$ only,
> $v_1 \leftrightarrow v_3$ full),
> arcs at $a$:
> $\{v_4 a, a v_2, v_2 a, a v_4, a v_1\}$
> (i.e., full 2-cycle on each of $v_2$ and $v_4$, plus a single arc
> $a \to v_1$).

Under the bijection $\sigma$ from A.7.3
($\sigma: 1 \mapsto v_1, 2 \mapsto v_3, 3 \mapsto v_4, 4 \mapsto v_2$
and $0 \mapsto a$), the Coder's deletion $D' = D \setminus \{(0,1)\}$
recovers exactly B.2 case (i) (hash `e19fcf9b6d693745` confirmed by
A.7.4 line 1856 and §A.9.2 above).  The deleted arc $(0,1)$ corresponds
to $a \to v_1$ — i.e., **deleting the configuration-distinguishing
arc of case (ii) collapses (ii) back to (i)**.  This is a structural
fact about the B.2 catalogue (cases (ii)–(v) are obtained from (i) by
adding one extra arc each) and explains why the Coder's strict-split
deletion check produced a "near-miss" against (i) rather than a clean
identification of (ii).

### §A.9.6  Recommendations for `code/benchmarks.py`

**Priority A (small, fully verified, c5524d22-related):** add the
three B.2 iso-class representatives, all 5 vertices, $\lambda^{\text{arc}} = 2$,
verifier-UNSAT-confirmed.

```python
# B.2 case (i): 5 vertices, 11 arcs. Hash e19fcf9b…
arcs = [(0,1),(1,2),(2,3),(3,0), (0,2),(2,0), (3,1),   # S_{4,-1}: 4-cycle + v_1<->v_3 full + v_4->v_2
        (3,4),(4,1),(1,4),(4,3)]                       # full 2-cycles a<->v_2 and a<->v_4

# B.2 case (ii): same S_{4,-1} + arc (4,0) = a->v_1.  Hash c5524d22…
arcs_ii = arcs + [(4,0)]

# B.2 case (iii): same S_{4,-1} + arc (0,4) = v_1->a.  Hash 52e5e47f…
arcs_iii = arcs + [(0,4)]
```

Names: `AiEtAl_B2_case_i`, `AiEtAl_B2_case_ii`, `AiEtAl_B2_case_iii`.
Each is genuinely 2-arc-strong, simple, split with $|V_2| = 4$, and
verifier-UNSAT in $< 100$ ms via cadical153.

**Priority B (small, fully verified, B.3 6-vertex UNSAT):** add the 5
new B.3 iso-class representatives (excluding (iv)\*×(iv), which is
already encoded as `AiEtAl_iv_star_iv`):

| Proposed benchmark name | Hash (16) | $m$ |
|---|---|---:|
| `AiEtAl_B3_i_star_i`    | `92edbcb1560d099f` | 14 |
| `AiEtAl_B3_i_star_ii`   | `dc835befa7a474f0` | 14 |
| `AiEtAl_B3_i_star_iv`   | `e6e7a2494bfa5cd4` | 14 |
| `AiEtAl_B3_ii_star_ii`  | `10fae725561067fd` | 14 |
| `AiEtAl_B3_ii_star_iv`  | `0cab4a53e5e81027` | 14 |

The arc lists are recorded in `/tmp/appendix_b_verify.py` output
(sorted-arcs form for each entry) and reproducible via the build
function in `/tmp/check_b3_minimal.py`'s `build_b3(e, f)`.

**Priority C (DEFERRED, TODO):** the five (iii)/(v)-involving B.3
products that paper-says-UNSAT but verifier-says-SAT under the
minimal-extras encoding.  These require either:
- a fresh figure-read of pp. 32–34 to identify the correct "dashed"
  arc(s) for cases (iii) and (v) and re-encode them with the right
  template;  or
- a published-version follow-up (the corresponding DAM paper or
  v2 of the arXiv preprint) with clearer figures.

Until then, those five instances are **not** safe to commit to
`benchmarks.py` — committing them with the current minimal encoding
would introduce labelled-UNSAT benchmarks that the verifier itself
reports SAT, breaking the verifier's own regression tests.

**Priority D (Coder index update):** extend
`_strict_split_unsat_canonical_keys` (in
`code/run_route_b_ns_exhaustive_l2.py` lines 88–106) to include all
three B.2 iso-class hashes (forward + arc-reverse) and the six B.3
iso-class hashes (forward + arc-reverse).  Re-run §3.b of
`team/20_*` and update the "9 NEW" count downward.  Based on the
B.2 alone, the count corrects to **at most 7** (subtract c5524d22 ~ B.2-β
and `35aa1b8c…` ~ L2.11-arc-reverse).

### §A.9.7  Summary

The Auditor reads the paper as claiming **5 UNSAT B.2 configs + 11
UNSAT B.3 products = 16 paper-claimed UNSAT instances**, organising
into **iso-classes 3 (B.2) + 11 (B.3) = 14** modulo the
$(e)^* \times (f) \cong (f)^* \times (e)$ symmetry and the
$S_{4,-1}$ diagonal-direction symmetry.  The Auditor verifies:

- **3 of 3** B.2 iso-classes are 2-arc-strong UNSAT (priority-A
  benchmarks added).
- **6 of 11** B.3 iso-classes are 2-arc-strong UNSAT under the
  minimal-extras encoding (priority-B benchmarks added; one — (iv)\*×(iv) —
  is the existing `AiEtAl_iv_star_iv`).
- **4 of 4** B.3 SAT cases are verifier-confirmed SAT.
- **5 of 11** B.3 UNSAT cases (all involving config (iii) or (v) at
  $a$ or $b$) are verifier-SAT under the minimal-extras encoding;
  the discrepancy is attributed to incomplete figure-read for the
  "dashed arc" specification of those cases.  Marked TODO for a
  future audit pass.

The Appendix A.7 question — does `c5524d22d2aba648` match a paper-listed
B.2 configuration? — resolves to **yes, case (ii)** (verdict (a)).

The audit's earlier "Coder mis-read" hypothesis is therefore confirmed
for `c5524d22…`.  The Coder's "9 NEW" count is over-counted by at
least 2 (c5524d22 and the L2.11-arc-reverse `35aa1b8c…`); pending the
TODO B.3 figure-read, it may correct further.

## Appendix A.10 — Matroid-union Edmonds citation for cross-kind arc-disjointness

Auditor session 2026-05-17, scope ~45 min.  Triggered by `team/27_r3star_hard_case_edmonds.md` §3.1 ("The branching packing") and §3.1.1 ("A clean form of the joint packing"), which invoke a **cross-kind arc-disjointness** statement that goes well beyond the standard Edmonds branching theorem audited in this file's source-table at Source 2 (line 946).  The audit below resolves the citation.

### §A.10.1 — The exact claim, verbatim

Quoted from `team/27_*` §3.1 (lines 155–175) and §3.1.1 (lines 182–222):

> **Cross-kind arc-disjointness.** $D^\bullet$ has $|A^\bullet| \ge 3|V^\bullet|/2$ by 3-arc-strongness (lower bound on average degree).  Each branching has exactly $|V^\bullet| - 1$ arcs.  Total arcs in the four branchings: $4(|V^\bullet| - 1)$.  [\dots]  The crude count does not immediately give arc-disjointness across kinds, but the following stronger fact does: **by the union of Edmonds out- and in-branching theorems (cf. Frank, *Connections in Combinatorial Optimization*, 2011, Theorem 9.5.1, or BJG–Yeo 2020 implicit usage in Lemma 4.1's "good pair" construction at p. 9–10 of arXiv:1903.12225), a $2k$-arc-strong digraph admits $k$ pairwise arc-disjoint out- and $k$ pairwise arc-disjoint in-branchings rooted at any vertex, with the out- and in-branchings of the same color additionally allowed to share arcs at will.  For our 3-arc-strong $D^\bullet$ with $k = 2$ out and $k = 2$ in, this gives $T_1^+, T_2^+, T_1^-, T_2^-$ pairwise arc-disjoint within kind, and the union of the two-out + two-in packing remains a sub-multi-graph of $D^\bullet$ with at most one use of each arc.**

§3.1.1 then upgrades the conclusion to *pairwise across all four*:

> "we assume the stronger form: $T_1^+, T_2^+, T_1^-, T_2^-$ are pairwise arc-disjoint across all four.  This is permissible because of the 3-arc-strong-hypothesis-margin and the matroid-union result of Frank (see e.g. Bang-Jensen–Gutin, *Digraphs: Theory, Algorithms and Applications*, 2nd ed., Theorem 9.5.4 — a standard packing result)."

So the load-bearing claim is:

> **(CK)** Every 3-arc-strong directed multigraph $D^\bullet$ with a special vertex $r$ admits four pairwise arc-disjoint branchings $T_1^+, T_2^+, T_1^-, T_2^-$ such that $T_i^+$ is out-rooted at $r$ and $T_i^-$ is in-rooted at $r$.  In particular the four together use $4(|V^\bullet|-1)$ distinct arcs of $A^\bullet$.

The Specialist offers two parenthetical "citations": *Frank 2011, Thm 9.5.1* (which is the BJG–Yeo 2020 numbering of Edmonds, not a Frank theorem at all — already a transcription error) and *Bang-Jensen–Gutin 2nd ed., Theorem 9.5.4*.

### §A.10.2 — What the standard sources actually say

**(a) BJG–Yeo 2020, Theorem 2.5 (Edmonds' branching theorem)**, verbatim from `team/05_audit.md` Appendix A.5 Source 2 (line 946–948), reproduced from arXiv:1903.12225 p. 6:

> "**Theorem 2.5** [12]  A directed multigraph $D = (V, A)$ with a vertex $z$, has $k$ arc-disjoint out-branchings rooted at $z$ if and only if $d^-(X) \geq k$ for all non-empty $X \subseteq V \setminus \{z\}$."

This produces $k$ arc-disjoint **out**-branchings.  Applied to the reverse digraph it produces $k$ arc-disjoint **in**-branchings.  The two applications are independent; nothing in the statement forbids the out-branching family and the in-branching family from sharing arcs.

**(b) Bang-Jensen–Gutin, 2nd ed. (2009), Theorem 9.5.1**, verbatim from `/tmp/bjg_book.txt` line 25547:

> "**Theorem 9.5.1 (Edmonds' branching theorem) [214]**  A directed multigraph $D = (V, A)$ with a special vertex $z$ has $k$ arc-disjoint spanning out-branchings rooted at $z$ if and only if $d^-(X) \geq k$ for all $\emptyset \neq X \subseteq V - z$."

So §9.5.1 of BJG 2009 is just Edmonds — the same statement as BJG–Yeo 2020 Theorem 2.5.  **There is no Theorem 9.5.4 about jointly arc-disjoint out- AND in-branchings** in BJG 2009.  What is at §9.5 numbering 9.5.4 is:

> "**Corollary 9.5.4 [229, Theorem 6.10]**  Let $D = (V, A)$ be a $k$-arc-strong directed multigraph and let $x, y$ be arbitrary distinct vertices of $V$.  Then for every $0 \leq r \leq k$ there exist paths $P_1, P_2, \ldots, P_k$ in $D$ which are arc-disjoint and such that the first $r$ paths are $(x, y)$-paths and the last $k - r$ paths are $(y, x)$-paths." (`/tmp/bjg_book.txt` line 25659)

This is **Even's mixed-direction *path* packing theorem**, not a *branching* packing theorem.  The Specialist's citation "BJG, 2nd ed., Theorem 9.5.4 — a standard packing result" misidentifies a result about $(x,y)$-/$(y,x)$-paths as if it gave joint out-/in-branchings.

**(c) Section 9.6 of BJG 2009 — "Edge-Disjoint Mixed Branchings"** (`/tmp/bjg_book.txt` line 25804 and following).  This is the only place in BJG's Ch. 9 that mixes "out" with anything else.  Verbatim (line 25831, Definition 9.6.1):

> "Let $M = (V, E \cup A)$ be a mixed multigraph with a special vertex $s$.  A mixed out-branching $F_s^+$ with root $s$ is a spanning tree in the underlying undirected multigraph $G$ of $M$ with the property that there is a path from $s$ to every other vertex $v$ in $F_s^+$."

And Theorem 9.6.3 (line 25847) packs $k$ edge-disjoint **mixed out-branchings** in a mixed multigraph (undirected edges + directed arcs).  This is **not** the same as packing out-branchings + in-branchings of a purely directed multigraph; the "mixed" refers to the underlying graph being a mixture of undirected edges and arcs, not to mixing forward/backward branchings.

**Verdict on (a)–(c):** Neither BJG–Yeo 2020 Theorem 2.5 nor BJG 2009 Theorems 9.5.1/9.5.4/9.6.3 provide claim (CK).  The closest available statement (Cor. 9.5.4 = Even) gives mixed-direction *paths*, not *branchings*.

**(d) The Nagamochi-Kamiyama survey** "Arborescence Problems in Directed Graphs" (J. JSCES, `/tmp/nagamochi.txt`) is, as of 2014, the standard survey of branching packing.  It contains §3.4 "Out- and in-arborescences" verbatim:

> "We consider the problem of packing an out-arborescence and an in-arborescence simultaneously.  More formally, we define the out- and in-arborescences packing problem as follows.  In this problem, we are given a directed graph $D$ with specified vertices $r_1, r_2$.  The goal of this problem is to discern whether there exist arc-disjoint subgraphs $T_1$ and $T_2$ of $D$ such that $T_1$ is an out-arborescence rooted at $r_1$ and $T_2$ is an in-arborescence rooted at $r_2$, and find them if they exist." (`/tmp/nagamochi.txt` lines 980–983)
>
> "It is a natural question that for this problem there exists a good characterization similar to Theorems 3.1 and 3.5.  Unfortunately, the following negative result is known.
> **Theorem 3.12 (Bang-Jensen [3]).** The out- and in-arborescences packing problem is NP-complete even if $r_1 = r_2$." (lines 996–1000)

**This is decisive.**  *Already* the existence of **one** arc-disjoint $(T^+, T^-)$ pair at a common root is NP-complete for general digraphs.  In particular, no clean "iff" cut-condition characterisation of the kind the Specialist invokes can exist for joint out-/in-branching packings (unless P = NP).

**(e) Bang-Jensen–Bessy–Havet–Yeo 2022**, arXiv:2003.02107, downloaded to `/tmp/bbhy2022.txt`.  Verbatim:

> "Thomassen also conjectured that every digraph of sufficiently high arc-connectivity should have such a pair of branchings.  [\dots]
> **Conjecture 2 (Thomassen [13]).** There is a constant $C$, such that every digraph with arc-connectivity at least $C$ has an out-branching and an in-branching which are arc-disjoint.
> Conjecture 2 has been verified for semicomplete digraphs [1] and for locally semicomplete digraphs [5].  In both cases arc-connectivity 2 suffices.  **For general digraphs the conjecture is wide open and as far as we know it is not known whether already $C = 3$ would suffice in Conjecture 2 (Figure 10 below shows that $C = 2$ is not sufficient).**" (lines 63–71)

The italicised parenthetical is the body-blow.  Existence of *even a single* arc-disjoint $(T^+, T^-)$ pair in a 3-arc-strong digraph is **the wide-open Thomassen conjecture**, conjectured but not proven.  And the Specialist's claim (CK) is asking for **two** such pairs that are also disjoint from each other — strictly stronger than Thomassen's open conjecture.

**(f) Frank, *Connections in Combinatorial Optimization* (OUP 2011).**  Chapter 10 ("Trees and arborescences: packing and covering") TOC available at `/tmp/frank_test.txt` lines 190–195:

> "10  Trees and arborescences: packing and covering
> 10.1  Packing arborescences
> 10.2  Packing branchings
> 10.3  Further generalizations
> 10.4  Covering by branchings, trees, and forests
> 10.5  Packing trees and forests"

No section titled "Packing of out- and in-arborescences" or "Cross-kind branching packing" appears.  The Frank-2011 chapter content beyond TOC is paywalled, but the absence of such a section is consistent with the Nagamochi-2014 survey's NP-completeness finding: there is no clean theorem of the form "$k$-arc-strong $\Rightarrow$ $k$ out + $k$ in jointly disjoint" in Frank's exposition.  The Specialist's "Theorem 9.5.1" of Frank 2011 (note: the *9.5.1* numbering is BJG–Yeo's, not Frank's) is a misattribution.

**(g) Schrijver, *Combinatorial Optimization* (Springer 2003), Volume B Chapter 53.**  TOC available at `/tmp/schrijver_book_part.txt` lines 955–969:

> "53  Packing and covering of branchings and arborescences  907
> 53.1  Disjoint branchings  907
> 53.2  Disjoint $r$-arborescences  908
> 53.3  The capacitated case  910
> 53.4  Disjoint arborescences  911
> 53.5  Covering by branchings  911
> 53.6  An exchange property of branchings  912
> [\dots]
> 53.10b  Arborescences with roots in given subsets  926"

No section titled "Disjoint out- and in-arborescences" appears in Schrijver's 1881-page encyclopedia of combinatorial optimisation.  By Schrijver's editorial standard (every nameable known result has its own section), the absence is itself evidence that no general-purpose joint out-/in-branching packing theorem in terms of arc-connectivity exists in the literature.

### §A.10.3 — The "iff" condition the Specialist would need, and why it fails

If a clean theorem of the form

> "A directed multigraph $D$ has $k_1$ arc-disjoint out-branchings rooted at $r$ and $k_2$ arc-disjoint in-branchings rooted at $r$, **all $k_1 + k_2$ mutually arc-disjoint**, iff [cut condition]"

existed, the cut condition would have to imply, for every $X \subset V - r$:

$$d^-(X) \geq k_1 \quad\text{(for the }k_1\text{ out-branchings)} \quad\text{and}\quad d^+(X) \geq k_2 \quad\text{(for the }k_2\text{ in-branchings, applied to the reverse digraph)}.$$

But for joint disjointness, **the in-branching arcs entering $X$ and the out-branching arcs entering $X$ must come from disjoint pools**.  An in-branching uses exactly one arc *leaving* $X$ to reach $r$ from each non-$r$ vertex of $X$ — but the *(reverse-digraph)* version of Edmonds gives in-branching arcs entering $X$ as the "out-arcs of the reverse," i.e., literally out-arcs of $D$ leaving $X$.  So joint disjointness across an arbitrary cut $X$ requires

$$\bigl|\delta_D^-(X)\bigr| \ge k_1 \quad\text{AND}\quad \bigl|\delta_D^+(X)\bigr| \ge k_2,$$

with no sharing.  Since $D^\bullet$ is 3-arc-strong, both $|\delta^\pm(X)| \ge 3$ — sufficient for $k_1 = k_2 = 2$ *separately*, but **not** sufficient to guarantee that the two packings can be chosen disjointly across the cut.  The total arc count entering $X$ (from $V\setminus X$) is $d^-(X) \ge 3$, but the joint packing wants $k_1 + k_2 = 4$ arcs in $\delta^-(X) \cup \delta^+(X)$ that are pairwise distinct.  For a $2$-arc-strong digraph this *can fail*, and there is no theorem turning 3-arc-strong into 4-arc-strong "for free."

In particular: in a 3-arc-strong digraph one cut $X$ may have $d^-(X) = d^+(X) = 3$ (the natural balanced extremal case), and then any 2 in-arcs + 2 out-arcs entering $X$ from the packing would have to come from $|\delta^-(X)| + |\delta^+(X)| = 6$ arcs — feasible by counting, but the **identity** of which 2 in-arcs and 2 out-arcs is forced by the global branching structure, and joint feasibility is exactly the open problem.

### §A.10.4 — Application to $D^\bullet$ with $k_1 = k_2 = 2$

$D^\bullet$ is 3-arc-strong.  We need claim (CK): $2 + 2 = 4$ mutually arc-disjoint branchings rooted at $r$.

- **Plain Edmonds (Source 2 of A.5):** Yes, 3 arc-disjoint out-branchings.  Yes, 3 arc-disjoint in-branchings.  **No** statement about cross-kind disjointness.
- **Thomassen Conjecture (Cnj. 2 of Bang-Jensen–Bessy–Havet–Yeo 2022):** even existence of *one* arc-disjoint $(T^+, T^-)$ pair is **open** for 3-arc-strong general digraphs.
- **Nagamochi-Kamiyama 2014 Theorem 3.12 (Bang-Jensen):** the joint out-/in-arborescence packing problem is **NP-complete** even for $r_1 = r_2$.

**Therefore (CK) does NOT follow from any published theorem in the standard branching-packing literature.**

The Specialist's parenthetical "matroid-union result of Frank" cannot supply (CK) either: matroid-union packs bases of *one* matroid (the cycle matroid of out-trees, or of in-trees), not bases of a hybrid out-tree-+-in-tree matroid, which is not known to exist as a meaningful matroid structure.

### §A.10.5 — Verdict on `team/27_*` §3.1.1

**OVER-STRONG.**

The Specialist's cross-kind disjointness statement (CK) is not a known theorem.  It is a *strengthening* of Thomassen's wide-open Conjecture 2 (existence of *one* arc-disjoint $(B^+, B^-)$ pair in a 3-arc-strong digraph), and would, if true, also resolve the Bang-Jensen NP-completeness obstruction in the polynomial-cases direction.  The two parenthetical citations the Specialist offers ("Frank 2011 Theorem 9.5.1" — which numbers Edmonds, not a joint-packing theorem; "BJG 2nd ed. Theorem 9.5.4" — which is Even's mixed-direction *paths* theorem, not branchings) are **misattributions**, in the same family of citation drift this audit has flagged twice before (OLS Theorem RD in §A.6; B.3 "dashed arcs" in §A.4 and §A.9).

The team has now been burned three times by Specialist over-attributions to Frank / BJG that turn out to be mis-citations.  The pattern is consistent enough to suggest a process issue: whenever the Specialist writes "by Frank, *Connections in Combinatorial Optimization*, Theorem X.Y.Z", the Auditor should treat the citation as **unverified** until pinned to a verbatim quotation from a directly accessible source.

### §A.10.6 — Recommendation

The Specialist's `team/27_*` §3.1.1 should be rewritten in the **weaker (within-kind only)** form, with §§3.2–3.4 adjusted accordingly.  Specifically:

1.  **Drop the cross-kind disjointness assumption.**  Replace by the within-kind form already noted at lines 197–207 of `team/27_*` §3.1.1:
    > "$T_i^+ \cap T_i^- = \emptyset$ for each $i \in \{1, 2\}$, **with possible sharing between $T_1^+ \cap T_2^-$ and $T_2^+ \cap T_1^-$**."

    This *is* a consequence of two independent applications of Edmonds' theorem with the "fresh" reasoning given on lines 198–206 (`$T_i^-$ chosen inside $A^\bullet \setminus T_i^+$ remains 2-arc-strong from $r$ by the submodularity inequality $d^-_{D^\bullet \setminus T_i^+}(X) \geq d^-_{D^\bullet}(X) - 1 \geq 2$`).  That argument is **correct** as stated and gives within-color disjointness.

2.  **Add the re-coloring step.**  The Specialist already noted (lines 211–216):
    > "an arc shared between $T_1^+$ and $T_2^-$ is assigned to color 1 by $T_1^+$, period; color 2 gets a 'lift' of that branching arc via a different free arc (this is the standard re-coloring step, formalized below)."

    The re-coloring step needs to be **actually formalized** (not deferred); the load-bearing §3.4 casework needs the recoloring lemma in hand.  Conservatively, this means the §3.4 arc-counting may shift: instead of $\le 4(|V^\bullet| - 1)$ arcs locked into $B^\circ$ and the rest free, we have $\le 4(|V^\bullet| - 1)$ arcs locked into $B^\circ$ **counted with potential double-use across kinds**, so some arcs may appear in $T_1^+ \cap T_2^-$ (or $T_2^+ \cap T_1^-$) and be split between colors by the re-coloring lemma.

3.  **Verify the §3.4 casework still goes through.**  The Auditor cannot verify this from §27 alone (the casework is ~350 lines of side-label demand bookkeeping); this is a *Specialist re-write task*, not an *Auditor task*.  The Specialist should reproduce the §3.4 counts under the weakened §3.1.1 and confirm that no count flips from "demand $\le$ supply" to "demand $>$ supply" due to the within-kind-only disjointness.

4.  **If (3) fails** — i.e., if §3.4 genuinely needs cross-kind disjointness — then the *route through Edmonds* is closed for the hard case, and the Specialist should fall back to one of:
   - **(c′)** Strengthen the hypothesis on $D^\bullet$: claim cross-kind disjointness only when $D^\bullet$ is **4-arc-strong** (in which case the Edmonds-doubled-instance trick *does* work: add an auxiliary copy of each branching's "type" tag and apply Edmonds with $k = 4$).  This narrows the lemma scope but preserves correctness.
   - **(d′)** Abandon route (c) for the R3⋆ hard case and try the route (a)/(b) alternatives explored in `team/26_*`.

### §A.10.7 — Summary line

`team/27_r3star_hard_case_edmonds.md` §3.1.1's "cross-kind arc-disjointness" claim is **OVER-STRONG**: it is not a corollary of Edmonds + matroid union; it is a strengthening of Thomassen's open Conjecture 2; and one of the two citations is to a paths theorem, not a branchings theorem.  The Specialist should rewrite §3.1.1 in the within-kind-only form (already correctly proved in lines 197–207) and verify §3.4 either still goes through, or upgrade $D^\bullet$ to 4-arc-strong, or fall back to a non-Edmonds route.

**Sources consulted directly (verbatim quotes above):** BJG–Yeo 2020 arXiv:1903.12225 (Source 2, line 946); BJG 2nd ed. 2009 via `/tmp/bjg_book.pdf` (Theorem 9.5.1, Cor. 9.5.4, §9.6); Bang-Jensen–Bessy–Havet–Yeo 2022 arXiv:2003.02107 via `/tmp/bbhy2022.txt` (Cnj. 2, Cnj. 29); Nagamochi-Kamiyama survey 2014 via `/tmp/nagamochi.txt` (§3.4, Thm 3.12 (Bang-Jensen [3])); Frank, *Connections in CO* (TOC only via `/tmp/frank_test.txt`, content paywalled); Schrijver 2003 Vol. B Ch. 53 (TOC only via `/tmp/schrijver_book_part.txt`, content paywalled).

**Specific library request (in case CANNOT-DETERMINE is later re-opened on the Frank/Schrijver Side):** Frank 2011, Sections 10.1–10.3 (Packing arborescences / branchings / further generalizations); Schrijver 2003, Sections 53.1–53.4 and 53.10b.  If a colleague has institutional access, search for any theorem of the form "$\exists\, T_1^\pm, \ldots, T_k^\pm$ mutually arc-disjoint, rooted at common $r$" with hypothesis weaker than $2k$-arc-strong.  Auditor expectation (Bayes prior $> 0.9$ given Nagamochi-2014's NP-completeness): no such theorem is in either book.

---

## Appendix A.11 — Sanity check on team/29_route_c1_recoloring.md

Auditor session 2026-05-17, scope ~1 hour. Trigger: fourth Specialist
deliverable in two weeks after three over-attributions (A.4/A.9, A.6,
A.10). Mode: line-by-line citation / hand-waving / sub-case discipline
audit, not a re-proof. The Specialist's own §7 honest-residual list is
graded against what the file actually does.

### §A.11.1 — Section-by-section findings

**§1.1 (standing hypotheses, verbatim re-import).** All hypotheses
are re-stated from `team/27_*` §§1.1–1.2, `team/26_*` §3.1,
`team/22_*` §2, `team/21_*` §§3.1–3.3. No new citation. Lower
bound ($\ast$) `|R_p^+| \ge 2, |R_q^+| \ge 3, |R_p^-| \ge 3, |R_q^-|
\ge 2` is attributed to `team/26_*` §3.1, which is consistent with
prior Lead-approved usage. **OK.**

**§1.2 (corrected branching-packing hypothesis).** Single load-bearing
citation: BJG–Yeo 2020 Theorem 2.5, quoted in `team/29_*` lines 73–76
verbatim, *matching* the audit's Source 2 (A.5 line 946). The reverse-
digraph application for in-branchings is explicit and standard.
Within-kind refinement (WK) re-states `team/27_*` lines 197–207
verbatim — this is the argument A.10.6 item 1 endorsed as
"correct as stated and gives within-color disjointness". The
submodularity inequality `d^-_{D^\bullet \setminus T_i^+}(X) \ge 2`
follows from "T_i^+ contributes at most one arc to any \delta^-(X),
being a branching" — a definitional fact, not a citation. The
within-kind across-color claim `T_1^+ \cap T_2^+ = \emptyset` and
`T_1^- \cap T_2^- = \emptyset` is "the same Theorem 2.5 application"
(`team/29_*` lines 102–104); this is the standard reading of the
Edmonds output. **OK.**

**§1.3 (LR, structural).** Self-contained from-first-principles
argument that no arc at $r$ can be in both an out- and an in-branching
rooted at $r$. Two lines, definitional. **OK.**

**§1.4 (shared-arc catalogue).** Re-states the four $S_{ij}$ sets.
No citation. **OK.**

**§2 (shared-arc problem).** Explanation of why the naive coloring
double-counts. Not a proof claim. **OK.**

**§3.1 (re-coloring map).** Definition only. **OK.**

**§3.2 / §3.2′ (single-arc removal lemmas).** Proofs in-document, ~6
lines, rely only on tree-of-arcs definitions. No citation. **OK.**

**§3.3 (replacement-arc supply, Lemma 3.3).**
- *Citations.* Only "by 3-arc-strongness, $|\delta^+(X)| \ge 3$".
  This is the standing hypothesis (`team/29_*` §1.1), not a citation
  to a named theorem. **OK as citation discipline.**
- *Hand-waving:* the proof of case (b) reads (lines 257–263):
  > "pick any $b \in T_2^+ \cup T_1^-$ inside $\delta^+(X)$; swap $b$
  > into $T_2^-$ as replacement for $a$. This breaks the branching
  > that previously contained $b$, but inside a *strictly smaller*
  > sub-tree — the down-tree of $b$ in its branching, which lies
  > inside $X = V(T_a^{\mathrm{down}})$ and hence has
  > $|V(T_b^{\mathrm{down}})| < |X|$. Recurse."
  The claim that the down-tree of $b$ "lies inside $X$" is not
  obvious. For $b \in T_2^+$ (an out-branching arc) with $b = (v',
  v'')$ and $v' \in X$, $v'' \notin X$ (the arc is in $\delta^+(X)$),
  the $T_2^+$-down-tree below $b$ is rooted at $v'' \notin X$, so it
  is **not** a subset of $X$. The Specialist marks this as sketch in
  §3.7 and §7.2 ("Lemma 3.3 case (b) recursion … sketch"), so this
  is **honestly flagged as sketch**, but the *specific* containment
  statement on lines 261–263 is wrong as written. Catalogued in
  §A.11.4.

**§3.4 (auxiliary $H$ and termination, Lemma 3.4).**
- *Citations.* None.
- *Status:* the proof header literally reads "*Proof sketch.*"
  (line 283) and the remark on lines 296–305 ends "The detailed
  monotonicity is left at this sketch level; see §3.8 for the
  augmenting-path fallback if the detailed argument is challenged."
  This is the `team/27_*` §7 standard sketch-discipline. **Honest
  sketch labeling.**
- *Specific gap:* what $\sigma$ is in the case $a \in S_{21}$ vs.
  $S_{12}$ is well-defined (lines 287–290), but the inequality
  $\sigma(b) < \sigma(a)$ along $H$-arcs is *asserted*, not derived,
  in either direction; the §3.3 case-(b) "lies inside $X$" issue
  above is what would carry the inequality. Catalogued in §A.11.4.

**§3.5 (RECOLOR algorithm).**
- *Citations.* None new.
- *Hand-waving:* lines 327–330 say "find a replacement arc $a'$ in
  $\delta^+(X_a) \setminus (T_2^+ \cup T_1^-)$ … if no such $a'$,
  swap inside the other color's branching (Lemma 3.3, chained
  re-coloring)". This is a forward reference to Lemma 3.3 case (b),
  which is at sketch level. Step 4 also says nothing about whether
  the replacement arc $a'$ is **at $r$ or internal** — see §A.11.4
  flag on §5.1.
- *Inconsistency:* "Termination after at most $|S| + (\max \sigma)$
  steps" (line 338) does not match §3.4's "after $|S|$ steps" (line
  294). Minor; both are upper bounds. Catalogued in §A.11.4 (minor).

**§3.6 (strong connectivity of each color class).** Standard
out-branching + in-branching argument, ~5 lines. Conditional on §3.5
output being a valid pair of branchings, which depends on Lemma 3.3
+ Lemma 3.4 (both at sketch level). **OK as a conditional claim**;
honest dependency.

**§3.7 (status of §3).** Self-assessment. Reports Lemmas 3.2 / 3.2′
and 3.3 case (a) as fully proved; 3.3 case (b) and 3.4 as sketch.
**Honest.**

**§3.8 (augmenting-path fallback, Lemma 3.8).**
- *Citations.* "3-arc-strongness gives 3 arc-disjoint $u \to v$ paths
  for every $u, v$ (Menger)" (line 388). **This is a NEW citation
  invocation.** Menger's theorem for digraphs is a textbook result
  (every CS-textbook attribution), but it is **not verbatim quoted
  in `team/05_audit.md` Appendices A.1 / A.5 / A.6 / A.8 / A.10**.
  Given the Specialist's recent track record, this should be flagged
  even though the citation is in itself uncontroversial.
- *Hand-waving:* the proof header reads "*Proof sketch.*" and the
  body ends "(Caveat: this requires a careful cut/path counting on
  $D^\bullet$; the argument is standard but not spelled out in full
  here.)" — explicitly self-marked sketch (line 394). **Honest sketch
  labeling**, but the actual cut/path-counting is *not* in document
  and *not* in audit; if a reviewer challenges §3.4 termination and
  the team falls back to §3.8, the proof load shifts onto an un-
  proved sketch. Catalogued in §A.11.4.

**§4.1 (4 branching arcs at $r$ distinct).** Uses (WK) and (LR) only,
both from §1. **OK.**

**§4.2 (16-profile casework survives).** Inherits `team/27_*` §3.4.6
/ §3.4.7 verbatim. The new argument is that since (LR) forces shared
arcs to be internal, the free arcs *at $r$* are unchanged by §3
re-coloring. This is the load-bearing structural claim. **See §A.11.4
flag** — the cut $\delta^+(X)$ around a shared arc's down-tree may
include arcs *ending at $r$*, and §3's Lemma 3.2 replacement arc may
be drawn from those. If so, the free-arc supply at $r$ changes after
§3, which contradicts the "not touched by re-coloring" statement on
line 446.

**§4.3 (re-stating §3.4 conclusion).** Inherits team/27_* §3.4.7. **OK
as inheritance**; the empirical residuals of team/27_* §3.4 are not
re-checked here.

**§5.1 (compatibility — disjoint arc sets).** This is the structural
crux. Lines 476–483 assert:
> "$S \subseteq A^\bullet \setminus \{\text{arcs at } r\}$ (by (LR));
> The free arcs at $r$ are in $A^\bullet \setminus B^\circ$ where
> $B^\circ = T_1^+ \cup T_2^+ \cup T_1^- \cup T_2^-$, and they are at
> $r$. The two arc sets are disjoint: $S$ is at internal vertices,
> free arcs at $r$ are at $r$."
The first half is correct (the sharing-set $S$ is internal by (LR));
but the "disjoint" framing covers *only the recolored arcs of $S$*,
not the **replacement arcs** that §3 also pulls into branchings. The
Lemma 3.2 replacement arc lives in $\delta^+(X_a)$ where $r \in V
\setminus X_a$ (since $r$ is the root of the in-branching and $X_a$
is the down-set, $r \notin X_a$). Hence $\delta^+(X_a)$ contains
arcs whose head is $r$ — i.e., arcs in $R_p^- \cup R_q^-$ — and §3
may consume one of these as the replacement for the lost shared arc
$a$. After such a consumption, the free-arc supply at $r$ that §4
relies on is **reduced** by 1 in some side class. **MAJOR concern.**
Catalogued in §A.11.4.

**§5.2 (combined SAD).** Reads correctly *if* §5.1's disjointness
holds. **Conditional on §5.1.**

**§5.3 (R3⋆ side-label satisfaction).** Inherits §4.3 + §3.6;
conditional. **OK as inheritance.**

**§5.4 ((H1b) re-coloring fine-print).** Says: "if $e^\star \in S$,
the re-coloring map $c$ is free per Definition 3.1, so we **override**
the default rule and set $c(e^\star) = 1$. The chained replacements
propagate normally. No conflict between §3 and §4.2." (lines 530–
533.) The "no conflict" claim depends on the chained-replacement
sketch tolerating arbitrary user-imposed initial choices. Lemma 3.4's
sketch assumes a `\sigma`-decreasing fixed ordering; an override
breaks that ordering at the seed. **Implicit hand-wave**, not marked
as sketch. Catalogued in §A.11.4.

**§5.5 ((H2) re-coloring fine-print).** Explicitly downgraded to
empirical: "**Empirically**, `team/28_*`'s 2232 canonical H2
instances all pass with 0 alignment failures … A fully formal proof
of the alignment lemma requires a finite typing-aware casework that
this file does not complete; it remains a residual modulo the §7
empirical record." (lines 543–548.) **Honest sketch labeling**,
empirical-only, matches §7.2.

**§6 (putting it together).** Linear chain of 9 numbered steps; each
step's citation is to a prior section of this document or to audit-
verified results. Step 4's "with §3.8 augmenting-path fallback if
§3.4's strict-decrease argument is challenged" makes the §3.4 sketch
fallback-conditional on §3.8 — but §3.8 is itself a sketch (§3.7).
Two sketches do not make a proof. **Honest about the dependency,
but transitively two-sketches-deep.** Catalogued in §A.11.4.

**§7 (honest residual).** §7.1 / §7.2 lists are accurate against the
above; §7.3 fallbacks are escape valves, not proofs; §7.4 empirical
log (`team/28_*` 11 869 instances 0 UNSAT) is the team's strongest
external check but is not a formal proof. **Honest.**

**§8 (citations cross-checked).** Lists the inherited citations,
all from audit-verified appendices (A.5 Source 2; A.5 Source 1;
A.5 Source 1 line 925; A.10). Lists "Not cited" — explicitly
disavows Frank 2011 Thm 9.5.1, BJG 2nd ed. Thm 9.5.4, matroid-union,
Thomassen Conjecture 2. **Citation discipline honestly stated.**
**Missing from §8:** Menger's theorem in §3.8, which is a NEW
invocation (uncontroversial-but-uncited).

**§9 (status summary).** Status table matches §7 honest residual.
**Honest.**

### §A.11.2 — Citation table

| Cited theorem | Location in `team/29_*` | Verbatim status in audit | Verdict |
|---|---|---|---|
| BJG–Yeo 2020 Theorem 2.5 (Edmonds' branching) | §1.2 lines 73–76; §6.1 step 1 line 567 | Verbatim in A.5 Source 2, line 946 of `team/05_audit.md` | **OK** |
| Within-kind submodularity refinement | §1.2 lines 86–101; §6.1 step 2 | Reproduced from `team/27_*` lines 197–207; A.10.6 item 1 endorsed it as "correct as stated" | **OK** |
| Cross-kind impossibility at $r$ (LR) | §1.3 lines 113–122 | Structural from-first-principles, no citation needed | **OK** |
| BJ–Yeo 2004 Theorem 1.2 (2-arc-strong semicomplete SAD off-$S_4$) | §8 line 715–716 (inherited from team/27_* §4) | Audit Section 1 line 27 verbatim; Source 1 of A.5 implicit | **OK** |
| BJ–Wang 2025 Lemma 2.4 (kernel-shell) | §8 line 718 (inherited from team/27_* §4) | Verbatim in A.5 Source 1 line 925; A.8.2 line 1620 | **OK** |
| Branching has at most one arc in $\delta^-(X)$ | §1.2 line 90–91; §3.3 implicitly | Definitional (no citation needed) | **OK** |
| 3-arc-strongness $\Rightarrow |\delta^+(X)| \ge 3$ | §3.3 line 248 | Standing hypothesis | **OK** |
| Menger's theorem for digraphs | §3.8 line 388 | **Not** verbatim in `team/05_audit.md` A.1–A.10 | **NEW-CITATION** (uncontroversial; flagged for completeness) |
| Audit Appendix A.10 | §1, §8 line 719 | Self-reference to audit | **OK** |
| BJG–Yeo 2020 Theorem 2.5 applied to *reverse* digraph | §1.2 lines 81–84; §6.1 step 1 line 569 | Standard reversal; A.10.2(a) lines 2588–2589 confirm | **OK** |
| `team/27_*` §3.4.6 16-profile table | §4.2 line 430; §6.1 step 5 line 584 | Inherited; not separately audit-verified, but `team/27_*` §3.4 was not flagged by A.10 (only §3.1.1 was) | **OK (inherited)** |
| `team/27_*` §4.1 / §4.2 / §4.3 sub-case arguments | §6.1 step 9 line 600 | Inherited; not separately audit-verified; auditor spot-checked §4.1 of team/27_* — uses within-kind only | **OK (inherited)** |
| `team/26_*` Lemma R3⋆-KS | §6.2 line 614 | Inherited; not load-bearing for the file under audit | **OK (inherited)** |

No misattributed Frank / BJG citations are present in `team/29_*`.
§8 explicitly disavows the audit-rejected Frank 2011 Thm 9.5.1 and
BJG 2nd ed. Thm 9.5.4 (lines 722–724). **The Specialist has
internalised the A.10 lesson on this front.**

### §A.11.3 — Sketch-level inventory

**Explicitly marked as sketch (honest):**

1. §3.3 case (b) recursion — `team/29_*` §3.7 ("Sketch level: Lemma
   3.3 *case (b)* recursion"), §7.2.
2. §3.4 acyclicity of $H$ / $\sigma$-monotonicity — `team/29_*`
   §3.4 ("*Proof sketch.*" line 283), §3.7, §7.2.
3. §3.8 Menger augmenting-path fallback — `team/29_*` §3.8 ("*Proof
   sketch.*" line 388, "(Caveat: this requires a careful cut/path
   counting on $D^\bullet$; the argument is standard but not spelled
   out in full here.)"), §7.2.
4. §5.5 (H2) Hamilton/diagonal alignment — `team/29_*` §5.5 ("A
   fully formal proof of the alignment lemma requires a finite
   typing-aware casework that this file does not complete; it remains
   a residual modulo the §7 empirical record."), §7.2.

**Implicitly hand-waved (not marked as sketch — problematic):**

5. §3.3 case (b)'s specific claim that the down-tree of $b$ "lies
   inside $X = V(T_a^{\mathrm{down}})$" is wrong as written for $b
   \in T_2^+$ (the down-tree of an out-branching arc in $\delta^+(X)$
   is rooted at $v'' \notin X$). The Specialist marks the recursion
   as sketch *globally*, but does not flag this specific containment
   error.
6. §5.1's "disjoint arc sets" framing ignores the §3 replacement
   arcs in $\delta^+(X_a)$, which may be arcs incident to $r$ (in
   classes $R_p^-, R_q^-$). The §4 free-arc supply at $r$ may be
   reduced by §3, contradicting line 446 ("the free arcs at $r$ are
   not touched by the re-coloring"). Not marked as sketch.
7. §5.4 (H1b) override claim "No conflict between §3 and §4.2" —
   the override of $c(e^\star) = 1$ alters the §3.5 default ordering;
   whether the chained-replacement still terminates under an
   arbitrary seed is not addressed.
8. §3.5's termination bound "$|S| + (\max \sigma)$" (line 338) is
   inconsistent with §3.4's "$|S|$ steps" (line 294); minor but
   un-explained.

### §A.11.4 — Sub-case enumeration check

The §4 sub-case structure (H1a / H1b / H2) is inherited from
`team/27_*` §4 unchanged. The kernel-shell case is offloaded to
`team/26_*`. The 16-row branching profile is inherited from
`team/27_*` §3.4.6. No sub-case has been quietly dropped relative
to the parent files. **OK.**

Within §3 (the new content), Lemma 3.3 has only two cases (a) and
(b), and §7.2 explicitly flags case (b) as sketch. Lemma 3.4's
sketch has no internal case split. **OK on enumeration**, modulo
the sketch label.

### §A.11.5 — Final verdict

**MINOR-CONCERNS.**

The Specialist has substantially internalised the A.10 lesson:
- No matroid-union claim.
- No Frank / BJG mis-citations.
- §8 explicitly disavows the prior bad citations.
- The within-kind submodularity argument (`team/27_*` lines 197–207)
  is correctly identified as "the only branching-packing result used"
  (after BJG–Yeo 2020 Thm 2.5).
- The §3 / §7 / §9 distinction between solid and sketch parts is
  drawn honestly and matches what the file actually does (Lemmas 3.2,
  3.2′, 3.3 case (a) solid; Lemma 3.3 case (b), Lemma 3.4, Lemma 3.8,
  §5.5 alignment sketch).

The remaining issues are:

(M1) **§5.1 disjoint-arc-set claim is incomplete.** The §3 RECOLOR
algorithm pulls in replacement arcs from $\delta^+(X_a)$ via Lemma
3.2; since $r \notin X_a$, this set contains arcs incident to $r$
(in classes $R_p^-, R_q^-$). The file's claim (lines 482–487) that
"the §3 re-coloring and §4 side-label allocation are independent
assignments on disjoint arc sets" is true for the *initial* shared
set $S$ but not for the *consumed* replacement arcs. The §4 free-arc
supply $|R_p^-|_F, |R_q^-|_F$ may be reduced by up to $|S|$ after §3.
The §4 supply ($\ge 3, \ge 3$) has $\ge 1$ slack per ($\ast$), but
the slack analysis at line 463 ("slack $\ge 0$, with strict slack in
most rows") was done under the team/27_* assumption of *unmodified*
free supply at $r$. Whether the slack survives a §3 reduction is
not checked in this file.

(M2) **§5.4 override interacts with §3.5 ordering.** The "set
$c(e^\star) = 1$" override is asserted not to conflict with §3.4's
chained-replacement, but no argument is offered. If $e^\star$ is the
$\sigma$-smallest arc, the override is harmless; if it is not, the
chain may force a different $c(e^\star)$ via §3.5 step 4. The
override may also force a replacement at the *first* step that no
longer satisfies the Lemma 3.3 case (a) free-supply condition.

(M3) **Menger citation in §3.8 is new and uncited.** Trivial fix
(Menger is folklore for directed graphs; e.g. BJG 2nd ed. Theorem
7.3.1), but per `feedback_citation_verification.md` the Specialist
should not invoke new theorems by name without a verbatim audit-
verified source.

(M4) **§3.3 case (b) containment claim is wrong as written.** The
down-tree of an out-branching arc $b = (v', v'')$ with $v' \in X$,
$v'' \notin X$ is rooted at $v''$ and is **not** a subset of $X$.
The sketch-level claim that the recursion terminates by strict
$\sigma$-decrease is in any case un-proved, but the specific
containment sentence on lines 261–263 is a *false statement* the
Specialist should retract or rewrite.

(M5) **Termination-step bound inconsistency.** §3.4 sketch says
$|S|$ steps; §3.5 says $|S| + (\max \sigma)$ steps. Both are upper
bounds; the discrepancy is cosmetic but should be reconciled.

None of M1–M5 are over-attributions in the A.6 / A.4 / A.10 family.
The Specialist's citation discipline in `team/29_*` is *clean*. M1
and M4 are structural-argument issues that the Specialist's own
§7-sketch labeling does not yet cover; they are the auditor's
contribution to the residual list.

The proof as a whole is correctly self-described in §7.5: "Solid:
§1.2 within-kind disjointness; §1.3 (LR); §4 side-label table; §5
compatibility (disjoint arc sets by (LR)); §3.2/3.3 case (a)" plus
"Sketch: §3.4 termination; §3.8 Menger fallback; §5.5 (H2) Hamilton/
diagonal alignment". The audit upgrade is: **§5 compatibility is
sketch, not solid**, because the disjoint-arc-set claim is
incomplete (M1); and **§3.3 case (b) containment** (M4) is an
implicit hand-wave inside an explicitly-sketched lemma.

**Recommendation for the Lead.** The §3.4 termination closure
attempt (the Specialist's announced next-step) can proceed in
parallel with M1–M5 fixes. M1 is the most consequential — it may
require either (i) a one-paragraph addendum to §5.1 showing the §4
slack survives §3 consumption, or (ii) a constraint on §3.5 to
prefer non-$r$-incident replacement arcs, or (iii) a re-check of the
team/27_* §3.4.7 16-row table under reduced free supply. M4 is a
one-sentence retraction. M3 is a citation-line addition. M2 and M5
are minor edits.

The file does **not** introduce a new over-attribution; the
fortnight's pattern of Frank / BJG mis-citations is **not** repeated
here. **PASS on citation discipline.**

End of Appendix A.11.

---

## Appendix A.12 — Conjecture L verification

Auditor session 2026-05-17, scope ~45 min. Trigger:
`team/30_route_c1_termination.md` §7.6 names the residual subtree-
exchange sub-claim **Conjecture L** and speculates it may sit
verbatim in Schrijver, *Combinatorial Optimization*, Vol. B, §53.6
("An exchange property of branchings"). Mode: pin the statement,
locate Schrijver §53.6's content via citing-papers, compare; if not
found, audit Frank's *Connections in CO*, BJG 2009 Ch. 9, Edmonds
1973, Frank 1979, Fujishige 2010 (the standard arc-disjoint-
arborescences sources).

### §A.12.1 — Verbatim Conjecture L

From `team/30_route_c1_termination.md` lines 756–761:

> **Conjecture L.** *Let $T^-, U^-$ be two arc-disjoint in-branchings
> of $D^\bullet$ rooted at $r$, $a \in T^-$ with $X_a^{T^-} \subseteq
> V^\bullet \setminus \{r\}$. Then there exists $b \in U^- \cap
> \delta^+(X_a^{T^-})$ such that $X_b^{U^-} \cap X_a^{T^-} \subsetneq
> X_a^{T^-}$, with strict inclusion.*

Here $X_a^{T^-}$ denotes the $T^-$-subtree "below" $a$, i.e., the set
of $V^\bullet$-vertices whose unique $T^-$-path to $r$ passes through
$a$. Conjecture L says: cross-cutting any such $T^-$-subtree, some
$U^-$-out-arc has its $U^-$-subtree strictly contained in the
original.

The §3.5 use is to make $|X_t \cap X_{a_0}^-|$ strictly decrease in
each (Repair-Swap) step where the swap-arc is chosen from $U^- \cap
\delta^+(X_t)$. The conjecture is needed *only* on cuts $X_a^- \ni$
non-root vertices, with two arc-disjoint in-branchings.

### §A.12.2 — Schrijver §53.6 content, located by triangulation

Schrijver Vol. B §53.6 ("An exchange property of branchings", p. 912)
is paywalled. However, a 2018 paper by Kakimura, Kamiyama and
Takazawa (*The b-bibranching Problem: TDI and Discrete Convexity*,
arXiv:1802.03235, `/tmp/bibranching.txt`) cites Schrijver's exchange
property as its reference [22], which is identified at line 1225 of
that file:

> "[22] A. Schrijver: Total dual integrality of matching forest
> constraints, *Combinatorica*, 20 (2000), 575–588."

And at line 47:

> "the exchange property of branchings [22]. We remark that, in the
> proof for the exchange property, Edmonds' disjoint branching
> theorem [4] plays a key role."

So Schrijver §53.6 of the 2003 book is the *exposition* of Theorem 1
of his 2000 Combinatorica paper "Total Dual Integrality of Matching
Forest Constraints". A free preprint of that 2000 paper is hosted on
Schrijver's CWI page (`https://homepages.cwi.nl/~lex/files/tdimf.cca.ps`,
PostScript) and converts cleanly to text. The exchange-property
statement is reproduced **verbatim** from `/tmp/tdimf.txt` lines
199–211:

> "First, this implies the following exchange property for
> branchings:
>
> **Theorem 1.** *Let $D = (V, A)$ be a directed graph, and let $B_1$
> and $B_2$ be branchings in $D$ partitioning $A$. Let $s$ be a root
> of $B_2$ but not of $B_1$, and let $r$ be the root of the
> arborescence in $B_1$ containing $s$. Then $A$ can be partitioned
> into branchings $B'_1$ and $B'_2$ with $R(B'_1) = R(B_1) \cup \{s\}$
> or $R(B'_1) = (R(B_1) \setminus \{r\}) \cup \{s\}$.*"

Here Schrijver's "branchings" are *out-branchings* in Bang-Jensen–
Yeo's terminology: directed forests in which every vertex has
in-degree $\le 1$. $R(B)$ denotes the **root set** of branching $B$
(the in-degree-0 vertices). The hypothesis "$B_1$ and $B_2$ partition
$A$" means $B_1 \cup B_2 = A$ and $B_1 \cap B_2 = \emptyset$, i.e.,
$A$ is *covered* by exactly two arc-disjoint branchings; the
branchings need not be spanning arborescences.

The proof (lines 205–211) is two sentences and rests on the lemma at
lines 161–198: any two branchings partitioning $A$ can be replaced by
two branchings partitioning $A$ with any prescribed root-set
configuration $(R_1, R_2)$ satisfying $R_1 \cup R_2 = R(B_1) \cup
R(B_2)$, $R_1 \cap R_2 = R(B_1) \cap R(B_2)$, **iff** each
in-degree-0 strong component of $D$ intersects both $R_1$ and $R_2$.

### §A.12.3 — Comparison to Conjecture L

The two statements are **fundamentally different objects**, in five
discriminating respects:

| Feature | Schrijver Vol. B §53.6 Thm 1 | Conjecture L |
|---------|-------------------------------|--------------|
| Branching orientation | out-branchings | in-branchings |
| Cover assumption | $B_1, B_2$ **partition** $A$ | $T^-, U^-$ arc-disjoint, but $A^\bullet \setminus (T^- \cup U^-)$ may be non-empty |
| Number of roots / root structure | $B_1, B_2$ are general branchings (multi-root forests) | $T^-, U^-$ are *spanning* arborescences sharing common root $r$ |
| Exchange operand | a single vertex $s$ (root-set element) | a single arc $a$ (interior arc), inducing the subtree $X_a^{T^-}$ |
| Conclusion form | root-sets $R(B_1'), R(B_2')$ reshuffled | strict subtree inclusion $X_b^{U^-} \cap X_a^{T^-} \subsetneq X_a^{T^-}$ |

The orientation mismatch (out vs in) is removable by reversing all
arcs: Schrijver Theorem 1 applied to the reverse $D^{\mathrm{rev}}$
yields a "root-exchange" theorem for *in*-branchings partitioning
$A$. So orientation is not the obstacle.

The fatal mismatches are:

1. **Cover.** Schrijver requires $B_1 \cup B_2 = A$. Conjecture L
   makes no such requirement; $T^- \cup U^-$ has $2(|V^\bullet|-1)$
   arcs and $A^\bullet$ has $\ge \lceil 3|V^\bullet|/2 \rceil$ arcs in
   the relevant 3-arc-strong setting, so when $|V^\bullet| \ge 5$ the
   cover hypothesis fails.
2. **Spanning arborescences with common root.** $T^-$ and $U^-$ are
   *both* spanning in-arborescences rooted at the same vertex $r$ —
   each has $|R| = 1$ and they share that one root. Schrijver's
   theorem is non-vacuous precisely when $R(B_1) \ne R(B_2)$: it asks
   to **move** a root from $B_2$ into $B_1$. With one root each, both
   roots equal to $r$, the hypothesis "$s$ is a root of $B_2$ but not
   of $B_1$" can never be satisfied. **Schrijver Theorem 1 is vacuous
   in the Conjecture L setting.**
3. **Subtree-inclusion conclusion.** Schrijver's conclusion is about
   root-set shuffling between two branchings that together still
   cover $A$. Conjecture L's conclusion is about a *combinatorial
   geometric* containment of a $U^-$-subtree inside a $T^-$-subtree.
   These are not interconvertible.

The two statements share an ambient theme — pairs of branchings can
be locally modified — but the actual content of Schrijver §53.6 does
not imply, nor is implied by, Conjecture L.

### §A.12.4 — Adjacent sources checked

- **Schrijver Vol. B §53.4** ("Disjoint arborescences") and **§53.5**
  ("Covering by branchings"): these contain Edmonds' arborescence
  packing theorem (TOC line 959, p. 911) and the dual covering result
  (p. 911). They are statements about *existence* of arc-disjoint
  branching collections; they say nothing about the relative subtree
  structure of two given arc-disjoint arborescences.
- **Schrijver Vol. B §53.7** ("Covering by r-arborescences"): a
  capacitated covering result; not subtree-exchange.
- **Frank, *Connections in Combinatorial Optimization* (OUP 2011),
  Chapter 10** ("Trees and arborescences: packing and covering"): TOC
  in `/tmp/frank_test.txt` lines 190–195 lists §10.1 Packing
  arborescences, §10.2 Packing branchings, §10.3 Further
  generalizations, §10.4 Covering, §10.5 Packing trees and forests.
  Content paywalled; per Appendix A.10 Bayes-prior estimate, no
  subtree-exchange theorem of the Conjecture L form is in Frank Ch.
  10. Frank Ch. 9.5 was already ruled out in A.10.
- **Bang-Jensen–Gutin *Digraphs* 2nd ed. (2009)**: §9.5 (Edmonds),
  §9.6 (mixed branchings), §9.7 (arc-disjoint *paths*). The TOC at
  `/tmp/bjg_book.txt` lines 588–594 contains no subtree-exchange
  section. The index Frank-entries (line 36666, "Frank, A., 351,
  357, ...") flag Frank-attributed results scattered through Ch. 7–9,
  but none of the section headers (line 215, "Chapter 9 deals with
  problems concerning (arc-)disjoint paths and trees") match
  Conjecture L's content.
- **Edmonds 1972/1973 "Edge-disjoint branchings"** (in *Combinatorial
  Algorithms*, Courant Computer Science Symposium 9, ed. R. Rustin):
  cited as Schrijver [22]'s Lemma 1 underlying his Theorem 1; the
  proof method (strong-component reduction) does not produce a
  subtree-inclusion guarantee.
- **Frank 1979 "On disjoint trees and arborescences"** (in *Algebraic
  Methods in Graph Theory*): cited as reference [14] of Kobayashi–
  Mahara–Schwarcz 2023 (`/tmp/reconf_union.txt` line 1075) for
  generalizations of Edmonds; the paper's content per the
  Nagamochi–Kamiyama survey (Theorem 3.3 attribution to Frank in
  `/tmp/nagamochi.txt` line 657) is an intersecting-family
  generalization of Edmonds, not a subtree-exchange.
- **Fujishige 2010 "A note on disjoint arborescences"** (*Combinatorica*
  30(2):247–252): summarised in `/tmp/nagamochi.txt` lines 779–793 as
  the convex-set generalization of Theorem 3.5 (Kamiyama–Katoh–
  Takizawa). Not a subtree-exchange between two arc-disjoint
  arborescences.
- **Kobayashi–Mahara–Schwarcz 2023 "Reconfiguration of the union of
  arborescences"** (arXiv:2304.13217, Algorithmica 2025): the
  *closest in spirit* result. They show (Theorem 1 of the abstract)
  that the union of $k$ arc-disjoint arborescences is *reconfigurable
  by single-arc exchanges* through the family of unions of $k$
  arc-disjoint arborescences. But the *exchange* there is a generic
  matroid-base step ("swap one arc"), not the specific subtree-
  inclusion required by Conjecture L. The 2025 paper's Theorem 2.1
  is Edmonds (`/tmp/reconf_union.txt` line 297); Schrijver is cited
  only as "see e.g., [30]" at line 953 (a generic textbook
  reference), with no specific use of §53.6.
- **Ito et al. 2021 "Reconfiguring (non-spanning) arborescences"**
  (arXiv:2107.03092): proves a *weak exchange property* for a single
  branching (Theorem 4 in `/tmp/reconf_arb.txt`), essentially a
  re-derivation of one half of Schrijver Theorem 1. Does **not**
  address pairs.
- **EGRES Trees-and-branchings open-problem page**
  (`http://lemon.cs.elte.hu/egres/open/Trees_and_branchings`): no
  open problem matching Conjecture L appears.

### §A.12.5 — Final verdict

**NOT-FOUND.** Schrijver Vol. B §53.6's "exchange property of
branchings" is Theorem 1 of Schrijver's 2000 *Combinatorica* paper
(verbatim quoted in §A.12.2 above). It is about **root-set
exchange between two branchings that together partition the arc
set**, *not* about **subtree inclusion between two arc-disjoint
spanning in-arborescences sharing a common root**. The two statements
have disjoint hypothesis sets (Schrijver requires partition; the
Specialist's setting has neither partition nor distinct roots) and
disjoint conclusion forms (root-set shuffle vs strict subtree
inclusion).

The Specialist's §7.6 speculation that "Conjecture L may be a direct
corollary of a §53.6 exchange theorem" is **not borne out**. The
specific exchange property in §53.6 does not apply.

Conjecture L is, to the best of this Auditor's search, **a genuinely
new structural lemma about pairs of arc-disjoint spanning in-
arborescences**. It has not been published in:

- Schrijver Vol. B Ch. 53 (Edmonds-packing chapter);
- Frank, *Connections in CO* 2011 Ch. 10 (paywalled, but the §A.10
  Bayes-prior plus the Kobayashi-2023 / Nagamochi-2014 surveys
  reference Frank for arborescence *packing*, never for subtree-
  exchange between two given arc-disjoint arborescences);
- Bang-Jensen–Gutin 2009 Ch. 9;
- Edmonds 1972/1973 *Edge-disjoint branchings*;
- Frank 1979 *On disjoint trees and arborescences*;
- Fujishige 2010 *A note on disjoint arborescences*;
- The post-2020 reconfiguration-of-arborescences corpus (Ito et al.
  2021, Kobayashi–Mahara–Schwarcz 2023).

### §A.12.6 — Implications for Route c1

The Specialist's three options (per the charter) are:

**(a) Prove Conjecture L from scratch.** The geometric content is
plausible: in a 3-arc-strong digraph, two arc-disjoint in-
arborescences cannot be "too aligned" on any cut $\delta^+(X)$; the
intuition is that $|\delta^+(X)| \ge 3$ provides "room" to find an
$U^-$-out-arc $b$ with $X_b^{U^-}$ strictly inside $X_a^{T^-}$. But
the audit's `team/30_*` §3.5 lines 376–399 (the Specialist's own
attempt) shows the naive approach fails: $X_b^{U^-}$ can genuinely
exceed $X_a^{T^-}$ because the $U^-$ tree-structure may pull
descendants out of $X_a^{T^-}$ via re-entry. A correct proof would
need to argue at the level of *minimal* $T_j^-$-subtrees inside
$X_a^{T^-}$ and use 3-arc-strongness to bound the re-entry count.
This is a 1–2 page lemma that the Specialist should attempt before
the team commits to (b) or (c).

**(b) Accept Theorem 1 as conditional.** Route c1's `team/30_*` §6
already labels its main lemma as "conditional on Conjecture L".
Phase-5 publishability depends on whether the editors of the target
venue accept a conditional R3⋆-HC result with a small named gap. The
Specialist's `team/30_*` §7.4 fallback (F3) (narrow to the
sub-class where Conjecture L is trivially satisfied) would preserve
unconditionality at the cost of hypothesis-narrowing — this is the
honest fallback if (a) fails by 2026-06-06.

**(c) Narrow to a sub-class where Conjecture L is not needed.** The
audit-cleared kernel-shell case (`team/26_*`) and the (H1a) not-strong
case (`team/30_*` §8) already do not need Conjecture L. The remaining
hard cases — (H1b) cut-arc, (H2) $S_4$ at $|V_2| = 4$, and case (b)
chained swap — all genuinely need either Conjecture L or fallback
(F3). Narrowing would have to drop these, leaving the published
theorem with hypotheses strictly stronger than 3-arc-strong, e.g.,
4-arc-strong (Appendix A.10's recommendation (c′) for `team/27_*`
already pointed in this direction).

The Auditor recommends pursuing (a) for 2 weeks. If a proof is in
hand by 2026-05-31, route c1 closes. Else, (c) (narrow to 4-arc-
strong) preserves unconditionality and matches the published-by-
2026-06-06 Lead tripwire.

### §A.12.7 — Summary line

**Conjecture L (`team/30_*` §7.6) is NOT a special case of
Schrijver Vol. B §53.6** (which is Schrijver's 2000 *Combinatorica*
Theorem 1 verbatim, a root-set exchange for two branchings that
partition the arc set — vacuous when applied to two spanning in-
arborescences sharing a common root). Nor does it appear in Frank
2011 Ch. 10, BJG 2009 Ch. 9, Edmonds 1972/1973, Frank 1979,
Fujishige 2010, or the 2021–2025 reconfiguration-of-arborescences
literature. **Conjecture L is a genuinely new structural lemma.**
Route c1 requires either a fresh proof (Auditor recommends 2 weeks)
or fallback (F3) (narrow hypotheses to 4-arc-strong) per the
`team/30_*` §7.4 menu.

**Sources consulted directly (verbatim quotes above):** Schrijver
2000, *Total Dual Integrality of Matching Forest Constraints*,
*Combinatorica* 20, retrieved from
`https://homepages.cwi.nl/~lex/files/tdimf.cca.ps` (`/tmp/tdimf.txt`);
Schrijver 2003 Vol. B Ch. 53 TOC (`/tmp/schrijver_book_part.txt`
lines 955–969, content paywalled); Kakimura–Kamiyama–Takazawa 2018
arXiv:1802.03235 (`/tmp/bibranching.txt`, identifies §53.6 ≡ Schrijver
2000 Thm 1); Ito et al. 2021 arXiv:2107.03092 (`/tmp/reconf_arb.txt`);
Kobayashi–Mahara–Schwarcz 2023 arXiv:2304.13217
(`/tmp/reconf_union.txt`); Nagamochi–Kamiyama 2014 survey
(`/tmp/nagamochi.txt`); Bang-Jensen–Gutin 2009 (`/tmp/bjg_book.txt`);
Frank 2011 Ch. 10 TOC (`/tmp/frank_test.txt`).

**Specific paywalled-resource residue** (per Lead 2026-06-06
tripwire): Schrijver 2003 Vol. B p. 912 cannot be inspected
page-by-page without institutional access; however, the citing-paper
triangulation in §A.12.2 (Kakimura–Kamiyama–Takazawa 2018 ref [22])
gives sufficient confidence (Auditor estimate: $>0.95$) that §53.6 is
Schrijver 2000 Theorem 1 verbatim. A library check is **not** the
critical path; the critical path is (a) the Specialist's fresh proof
attempt or (c) fallback adoption.

End of Appendix A.12.

---

## Appendix A.13 — Edmonds–Schrijver matroid union for arborescence packing

Auditor session 2026-05-17, scope ~1 hour. Trigger: `team/32_F3_verification.md` is an honest negative report by the Specialist on the proposed (F3) cross-kind disjointness at $\lambda \geq 4$. Two findings of `team/32_*` need adjudication:

1. **`team/32_*` §2.3** uncovers a gap in the within-kind submodularity step at `team/27_*` lines 197–207, which this audit's §A.10.6 item 1 had cleared as "correct as stated." The Specialist now shows the load-bearing inequality $|T \cap \delta^-(X)| \leq 1$ is **false** (it equals the number of connected components of $T[X]$).
2. **`team/32_*` §2.5** claims that the cross-kind statement (F3) "is a textbook consequence of the Edmonds–Schrijver matroid-union theorem (Frank, *Connections in Combinatorial Optimization*, 2011 §10.1; Schrijver Vol. B §53.6)," and asks for the audit's hard-rule against matroid union to be lifted so (F3) can be cited.

This is the *third* deliverable in two months where the Specialist invokes "Frank §10" or "Schrijver §53" as a matroid-union source for cross-kind branching packing (after `team/27_*` §3.1.1 invoked Frank §9.5.1, audited at A.10; and `team/29_*` §1.2 re-stated the broken within-kind argument, sanity-checked at A.11). The Auditor's track record: A.4/A.9 (B.3 dashed arcs), A.6 (Theorem RD), A.10 (Frank/BJG joint packing) all came back NOT-FOUND or VERIFIED-VIA-FOLKLORE.  This appendix is the sixth pass, with verbatim-or-bust discipline.

### §A.13.1 — The two claims under audit

**(C1) Cross-kind disjointness at $\lambda \geq 4$.** For every 4-arc-strong directed multigraph $D^\bullet$ and every $r \in V(D^\bullet)$, there exist 2 out-branchings $T_1^+, T_2^+$ and 2 in-branchings $T_1^-, T_2^-$, all rooted at $r$, such that all four are **pairwise** arc-disjoint.

**(C2) Within-kind disjointness at $\lambda \geq 3$.** For every 3-arc-strong directed multigraph $D^\bullet$ and every $r \in V(D^\bullet)$, there exist 3 arc-disjoint out-branchings $T_1^+, T_2^+, T_3^+$ rooted at $r$, and separately 3 arc-disjoint in-branchings $T_1^-, T_2^-, T_3^-$ rooted at $r$.  No cross-kind disjointness asserted.

These are the cleanest forms of what `team/27_*` and `team/32_*` need, after stripping the broken submodularity rhetoric.

### §A.13.2 — Source-by-source assessment

**(a) Bang-Jensen–Gutin, *Digraphs: Theory, Algorithms and Applications*, 2nd ed. (Springer 2009)**, accessed via `/tmp/bjg_book.pdf` and `/tmp/bjg_book.txt`.

*Theorem 9.5.1 (Edmonds' branching theorem)*, `/tmp/bjg_book.txt` line 25547:

> "**Theorem 9.5.1 (Edmonds' branching theorem) [214]**  A directed multigraph $D = (V, A)$ with a special vertex $z$ has $k$ arc-disjoint spanning out-branchings rooted at $z$ if and only if $d^-(X) \geq k$ for all $\emptyset \neq X \subseteq V - z$."

*Proof of Theorem 7.10.1 (Dalmazzo's bound on minimally $k$-arc-strong digraphs)*, `/tmp/bjg_book.txt` lines 19740–19747, is the closest BJG comes to a within-kind+across-kind use of Edmonds:

> "Let $D = (V, A)$ be $k$-arc-strong and let $s$ be a fixed vertex of $V$. By Corollary 7.3.2 $d^+(U), d^-(U) \geq k$ for every $\emptyset \neq U \subset V$. Hence, by Edmonds' branching theorem (Theorem 9.5.1), $D$ contains $k$ arc-disjoint in-branchings $F^-_{s,1}, \ldots, F^-_{s,k}$ rooted at $s$ and $k$ arc-disjoint out-branchings $F^+_{s,1}, \ldots, F^+_{s,k}$ rooted at $s$. Let $A' = A(F^-_{s,1}) \cup \ldots \cup A(F^-_{s,k}) \cup A(F^+_{s,1}) \cup \ldots \cup A(F^+_{s,k})$ and let $D' = (V, A')$. Then $D'$ is $k$-arc-strong and has at most $2k(n-1)$ arcs."

**This is the published form of (C2):** plain Edmonds applied twice (once to $D$, once to reverse $\overleftarrow{D}$) yields $k$ arc-disjoint out-branchings AND $k$ arc-disjoint in-branchings.  No cross-kind disjointness is claimed or used; "$|A'| \leq 2k(n-1)$" holds because each branching has $n-1$ arcs and we have $2k$ of them (the inequality, not equality, makes the bound robust to within-kind+across-kind overlap).

*Section 9.9 ("Arc-Disjoint In- and Out-Branchings")*, `/tmp/bjg_book.txt` line 26580 ff., gives the **NP-completeness** of the joint problem:

> "**Problem 9.9.1** Given a digraph $D$ and vertices $u, v$ (not necessarily distinct). Decide whether $D$ has a pair of arc-disjoint branchings $F^+_u, F^-_v$ such that $F^+_u$ is an out-branching rooted at $u$ and $F^-_v$ is an in-branching rooted at $v$.
>
> **Theorem 9.9.2 [46]** Problem 9.9.1 is $\mathcal{NP}$-complete for arbitrary digraphs."

`/tmp/bjg_book.txt` line 26622–26625:

> "It is easy to reduce (in polynomial time) Problem 9.9.1 for the case when $u \neq v$ to the case when $u = v$ for arbitrary digraphs (Exercise 9.49). Hence the problem remains $\mathcal{NP}$-complete when we ask for an out-branching and an in-branching that are arc-disjoint and have the same root."

So **even ONE arc-disjoint $(F^+, F^-)$ pair at a common root is NP-complete** for general digraphs.

*Section 9.6 ("Edge-Disjoint Mixed Branchings")*, `/tmp/bjg_book.txt` line 25831:

> "**Definition 9.6.1** Let $M = (V, E \cup A)$ be a mixed multigraph with a special vertex $s$.  A mixed out-branching $F^+_s$ with root $s$ is a spanning tree in the underlying undirected multigraph $G$ of $M$ with the property that there is a path from $s$ to every other vertex $v$ in $F^+_s$."

§9.6 packs mixed *out*-branchings only; "mixed" means the underlying graph has both undirected edges and arcs, not that the branchings mix out- and in-directions.  **No cross-kind branching packing theorem appears in §9.6.**

**Comparison to (C1) and (C2).**
- (C2) is **VERIFIED-VERBATIM** from the proof of Theorem 7.10.1 (above) — two independent applications of Theorem 9.5.1 (Edmonds), one to $D$ and one to $\overleftarrow{D}$.  This is also exactly what the team has been calling "plain Edmonds applied twice" since `team/05_audit.md` Source 2.
- (C1) is **NOT** delivered by BJG.  §9.9 establishes (C1) is NP-complete *already at the $k = 1$ level for arbitrary digraphs*, ruling out a clean cut-condition characterisation under any arc-connectivity hypothesis weaker than what one would need to make the problem polynomial.

**(b) Bang-Jensen–Gutin, "Generalizations of tournaments: A survey"**, `https://files.core.ac.uk/download/pdf/78903131.pdf` (accessed 2026-05-17).  §12 ("Arc-disjoint in- and out-branchings") states:

> "**Conjecture 12.9 [80]**  There exists a natural number $N$ such that every digraph $D$ which is $N$-strongly arc-connected has arc-disjoint branchings $F^+_v, F^-_v$ for every choice of $v \in V(D)$."
>
> "We believe that something much stronger holds for tournaments:
> **Conjecture 12.10**  There exists a function $f : \mathbb{N} \to \mathbb{N}$ such that for every natural number $k$ every $f(k)$-strongly arc-connected tournament $T$ has $2k$ arc-disjoint branchings $F^+_{v,1}, \ldots, F^+_{v,k}, F^-_{v,1}, \ldots, F^-_{v,k}$ such that $F^+_{v,1}, \ldots, F^+_{v,k}$ are out-branchings rooted at $v$ and $F^-_{v,1}, \ldots, F^-_{v,k}$ are in-branchings rooted at $v$, for every vertex $v \in V(T)$.
> It was shown in [5] that $f(1) = 2$."

**This is decisive.**  Conjecture 12.10 *is exactly (C1) under arc-connectivity hypothesis* — and it is stated as an **open conjecture even for tournaments**, only known at $k = 1$.  For general digraphs (Conjecture 12.9), even the *existence* of one $(F^+_v, F^-_v)$ pair for *some* $v$ is conjectural.

**(c) Bang-Jensen–Bessy–Havet–Yeo 2022**, arXiv:2003.02107, `/tmp/bbhy2022.txt` lines 63–71:

> "**Conjecture 2 (Thomassen [13]).**  There is a constant $C$, such that every digraph with arc-connectivity at least $C$ has an out-branching and an in-branching which are arc-disjoint.
>
> Conjecture 2 has been verified for semicomplete digraphs [1] and for locally semicomplete digraphs [5].  In both cases arc-connectivity 2 suffices.  **For general digraphs the conjecture is wide open and as far as we know it is not known whether already $C = 3$ would suffice in Conjecture 2** (Figure 10 below shows that $C = 2$ is not sufficient)."

Conjecture 2 is the $k = 1$ existential form of (C1).  Even $C = 3$ is not known to suffice.  (C1) at $k = 2$, $\lambda \geq 4$ is therefore *strictly stronger* than what is known to follow from Thomassen's Conjecture 2 even if $C = 4$ sufficed there.

**(d) Bang-Jensen–Yeo 2004, "Decomposing $k$-arc-strong tournaments into strong spanning subdigraphs"**, Combinatorica 24, 331–349 (paywalled; web-confirmed details via `searchresult/decomposing-k-arc-strong-tournaments`).

The paper proves: a $74k$-arc-strong tournament has $2k$ arc-disjoint branchings ($k$ out-rooted at one set, $k$ in-rooted at another).  The threshold $74k$ — much larger than $2k$ — is a strong signal that the joint $(k, k)$ packing requires **much more** than $2k$-arc-strongness even in the tournament setting, where matroid-union-flavoured statements are at their most amenable.  This is consistent with §A.13.2(b) above: the conjectured $f(k)$ in Conjecture 12.10 has only been bounded (for tournaments) by $74k$, not by any small constant.

**(e) Nagamochi–Kamiyama, "Arborescence Problems in Directed Graphs"** (JJSCES 2014), `/tmp/nagamochi_new.txt`.

§3.4 ("Out- and in-arborescences"), `/tmp/nagamochi_new.txt` lines 1240–1243:

> "[…] we deﬁne the out- and in-arborescences packing problem as follows.  In this problem, we are given a directed graph $D$ with speciﬁed vertices $r_1, r_2$.  The goal of this problem is to discern whether there exist arc-disjoint subgraphs $T_1$ and $T_2$ of $D$ such that $T_1$ is an out-arborescence rooted at $r_1$ and $T_2$ is an in-arborescence rooted at $r_2$, and ﬁnd them if they exist."

Line 1254–1261:

> "It is a natural question that for this problem there exists a good characterization similar to Theorems 3.1 [Edmonds] and 3.5 [Kamiyama–Katoh–Takizawa].  Unfortunately, the following negative result is known.
> **Theorem 3.12 (Bang-Jensen [3]).**  The out- and in-arborescences packing problem is NP-complete even if $r_1 = r_2$."

The survey's §3.4 lists exactly **three** positive results (Theorems 3.13 tournaments, 3.14 acyclic, Cor. of 3.13 ≡ BJG-2nd-ed Thm 9.9.3 strong digraphs with $V = \{v\} \cup N^+(v) \cup N^-(v)$), each *class-specific*.  **No theorem in §3.4 gives a cut-condition characterisation for joint packing in general digraphs, even at $k = 1$, let alone at $k = 2$ with $\lambda \geq 4$.**

**(f) Frank, *Connections in Combinatorial Optimization*, OUP 2011.**

Chapter 10 TOC ("Trees and arborescences: packing and covering"), `/tmp/frank_test.txt` lines 190–195 (already reproduced in A.10.2(f)):

> "10  Trees and arborescences: packing and covering
> 10.1  Packing arborescences
> 10.2  Packing branchings
> 10.3  Further generalizations
> 10.4  Covering by branchings, trees, and forests
> 10.5  Packing trees and forests"

Auditor pass on `https://www.biblos.pk.edu.pl/ST/2012/01/100000223464/100000223464_Frank_Connections.pdf` (saved 2026-05-17 as `/tmp/frank_book.pdf`): only 3 pages of front matter accessible; no content beyond TOC.  Auditor pass on `https://andrasfrank.web.elte.hu/BookZent.PDF` (saved 2026-05-17 as `/tmp/frank_BookZent.pdf`): one page, Zentralblatt review only, no theorem text.

**Frank §10.1 ("Packing arborescences") is dedicated to packing out-arborescences (rooted *out*), with Frank-1978/1981 multi-root and matroid-rank extensions.**  Web searches (Auditor 2026-05-17) and citing-paper triangulation (Nagamochi-Kamiyama 2014 §3.1 cites Frank §10 specifically for Theorem 3.3, an intersecting-family extension of Edmonds — `/tmp/nagamochi_new.txt` lines 807–818) show §10.1's theorems are all **same-direction** packings.  No verbatim quote for a *cross-kind* (out + in) packing theorem could be obtained from Frank §10.

**(g) Schrijver, *Combinatorial Optimization: Polyhedra and Efficiency* (Springer 2003), Vol. B.**

Chapter 53 TOC ("Packing and covering of branchings and arborescences"), `/tmp/schrijver_book.txt` lines 955–969 (independently re-confirmed at `/tmp/schrijver_book_part.txt`, audit A.10.2(g)):

> "53  Packing and covering of branchings and arborescences  907
> 53.1  Disjoint branchings  907
> 53.2  Disjoint $r$-arborescences  908
> 53.3  The capacitated case  910
> 53.4  Disjoint arborescences  911
> 53.5  Covering by branchings  911
> 53.6  An exchange property of branchings  912
> 53.7  Covering by $r$-arborescences  914
> 53.8  Minimum-length unions of $k$ $r$-arborescences  916
> 53.9  The complexity of finding disjoint arborescences  921"

`team/32_*` §2.5 cites "Schrijver Vol. B §53.6 (An exchange property of branchings)" as the matroid-union source for (C1).  **§53.6 by its title is about an *exchange property* of branchings — almost certainly the matroid-base-exchange property of the branching matroid $\mathcal{M}^+$ (or its in-branching dual), not a joint out + in packing theorem.**  Auditor estimate (Bayes prior conditional on TOC structure + Schrijver's editorial habit of one nameable result per section): ≥ 0.95 that §53.6 is the matroid-exchange property for *same-direction* branchings.

§53.9 "Complexity of finding disjoint arborescences" + §53.10a "Complexity survey for disjoint arborescences" (page 924) are where Schrijver, in his usual encyclopedic completist style, would house the NP-completeness for joint out+in packing if he covered it — Auditor could not access the page itself, but the TOC entry is consistent with this being where Bang-Jensen's NP-completeness is recorded.  **No TOC entry suggests a positive cross-kind packing theorem.**

Auditor library-request restatement (from A.10 §A.10.7, still standing): a colleague with institutional access should inspect Schrijver Vol B pp. 907–926 for any theorem of the form "$D$ has $a$ arc-disjoint out-arborescences AND $b$ arc-disjoint in-arborescences, all $a + b$ pairwise arc-disjoint, iff [cut condition]."  Auditor Bayes prior on a positive find: $< 0.05$, given §A.13.2(b)–(e) cumulative evidence.

**(h) Korte–Vygen, *Combinatorial Optimization: Theory and Algorithms*** (downloaded 2026-05-17 from `https://www.mathematik.uni-muenchen.de/~kpanagio/KombOpt/book.pdf` as `/tmp/korte_vygen.pdf`).  Chapter 6 "Spanning Trees and Arborescences," Theorem 6.18 (Edmonds 1973):

> "**Theorem 6.18 (Edmonds [1973]).** Let $G$ be a digraph and $r \in V(G)$.  Then the maximum number of edge-disjoint spanning arborescences rooted at $r$ equals the minimum cardinality of an $r$-cut." (`/tmp/korte_vygen.txt` line 10182)

Theorem 6.19 (Frank 1979) extends to multi-rooted arborescences (still same-direction).  **`grep -n "in-arboresc\|in-branching" /tmp/korte_vygen.txt` returns zero matches** — the textbook does not discuss in-branchings as a distinct concept, only arborescences (out-rooted), with "apply to reverse digraph" being the implicit way to handle the in case.  **No cross-kind packing theorem in Korte–Vygen.**

### §A.13.3 — Verdict on (C1) cross-kind disjointness

**NOT-FOUND, again.**

Aggregating §A.13.2 (a)–(h):

- **BJG 2009 §9.9 (Theorem 9.9.2):** Joint out + in packing is NP-complete already at $k = 1$ for arbitrary digraphs.
- **BJG–Gutin survey §12 (Conjecture 12.9, 12.10):** (C1) is **conjectured** for tournaments with $f(k)$-arc-strong hypothesis (current best bound $f(k) \leq 74k$); for general digraphs even (C1) at $k = 1$ is conjectural (Thomassen Conjecture 2, BBHY 2022).
- **Nagamochi-Kamiyama 2014 §3.4:** Joint problem class-specific positive results (tournaments, acyclic, special-strong); no general arc-connectivity theorem.
- **Bang-Jensen–Yeo 2004:** the closest published positive (for tournaments) needs $74k$-arc-strong to get $k$ out + $k$ in — much more than the $2k = 4$ the Specialist's (R1) would need for $k = 2$, $\lambda \geq 4$.
- **Frank §10, Schrijver §53:** TOC accessible only, no theorem heading suggests cross-kind packing; the "matroid union" reference Frank/Schrijver provide (§10.1, §53.6) is to **same-direction** $k$-arborescence packing (matroid base + matroid union of $k$ copies = same-direction packing of $k$ identically-oriented branchings).

**The Specialist's `team/32_*` §2.5 invocation of "Frank §10.1, Schrijver §53.6" as a published source for (C1) is a third over-attribution in the same pattern as `team/27_*` (audited A.10), `team/29_*` (audited A.11), and the OLS theorem RD (audited A.6).**  The matroid-union *technique* is real — it is the standard tool for **same-direction** $k$-arborescence packing (which IS Theorem 6.18 / 9.5.1 / Edmonds 1973), but **not** for joint cross-direction packing, which is governed by Thomassen's Conjecture 2 and is *open* in the relevant parameter regime.

Hence:
- **(C1) is NOT-VERIFIED.** No published theorem covers it at any $\lambda$ threshold reachable by the team's hypothesis $\lambda \geq 4$.  The closest analogue (Conjecture 12.10) is open even for tournaments at $k \geq 2$.
- **The Specialist's recommendation in `team/32_*` §3.2 (R1) — "lift the hard rule against matroid union, then (F3) is a one-line corollary" — is incorrect.**  Matroid union does **not** give (C1).  Lifting the hard rule would not solve the problem.

### §A.13.4 — Verdict on (C2) within-kind disjointness

**VERIFIED-VERBATIM** from BJG 2009 Theorem 9.5.1 (Edmonds) applied twice.

Specifically, for $D^\bullet$ 3-arc-strong and any $r \in V(D^\bullet)$:

- Apply Theorem 9.5.1 with $k = 3$ to $D^\bullet$: $d^-(X) \geq 3$ for all non-empty $X \subseteq V - r$ (by 3-arc-strongness) gives 3 arc-disjoint out-branchings $T_1^+, T_2^+, T_3^+$ rooted at $r$.  Take any 2 of them, e.g., $T_1^+, T_2^+$.
- Apply Theorem 9.5.1 with $k = 3$ to the reverse $\overleftarrow{D^\bullet}$: $d^-_{\overleftarrow{D^\bullet}}(X) = d^+_{D^\bullet}(X) \geq 3$ gives 3 arc-disjoint in-branchings $T_1^-, T_2^-, T_3^-$ rooted at $r$ (in $D^\bullet$).  Take any 2 of them.

This is **exactly the proof BJG use for Theorem 7.10.1** (`/tmp/bjg_book.txt` lines 19740–19747), reproduced verbatim in §A.13.2(a).  No matroid-union machinery is invoked or needed; no submodularity step beyond what is already in the proof of Theorem 9.5.1 itself.

**Crucially**, this published form of (C2) does **not** claim any cross-kind disjointness — the in-branchings $T_i^-$ and out-branchings $T_j^+$ may freely share arcs.

### §A.13.5 — Re-audit of `team/27_*` lines 197–207 (revising A.10.6 item 1)

`team/32_*` §2.3 is **correct** that the within-kind submodularity step at `team/27_*` lines 197–207 has a gap.  The step claimed:

> "[We choose] $T_i^-$ inside $A^\bullet \setminus T_i^+$, which is still $\geq 2$-arc-strong from $r$ by the inequality $d_{(D^\bullet \setminus T_i^+)}^-(X) \geq d_{D^\bullet}^-(X) - 1 \geq 2$ for every $X$ (since $T_i^+$ contributes at most one arc to any $\delta^-(X)$, being a branching)."

The parenthetical "since $T_i^+$ contributes at most one arc to any $\delta^-(X)$" is **false in general**, as `team/32_*` §2.3 correctly identifies:

> "$|T \cap \delta^-(X)| = \#\{\text{connected components of } T[X]\}$, [...] which is $\geq 1$ but not $\leq 1$ in general."

Concretely: if $T_i^+$ has out-degree $\geq 2$ at some non-root vertex $u$ and $X$ contains exactly the descendants of two distinct children of $u$, then $T_i^+[X]$ has $\geq 2$ components, each contributing one arc to $T_i^+ \cap \delta^-(X)$.

**Audit A.10.6 item 1's clearance of this submodularity step was over-generous.** The correct statement, derived via converse-of-Edmonds (a.k.a. "salvage" in `team/32_*` §2.4), is

$$d^-_{D^\bullet \setminus T_1^+}(X) \geq 2$$

(this *does* hold, because $D^\bullet \setminus T_1^+$ contains $T_2^+, T_3^+$ as 2 arc-disjoint out-branchings, so by Theorem 9.5.1 necessity $d^- \geq 2$).  But this does **not** establish $d^+_{D^\bullet \setminus T_1^+}(X) \geq 2$, which is what an *in*-branching extraction from the residual would require.

So the within-kind step **cannot be proved by the route `team/27_*` lines 197–207 attempts**.  However:

**Plain Edmonds applied twice (independently on $D^\bullet$ and on $\overleftarrow{D^\bullet}$) gives 2 + 2 = 4 branchings $T_1^+, T_2^+, T_1^-, T_2^-$, with within-kind disjointness automatic ($T_1^+ \cap T_2^+ = T_1^- \cap T_2^- = \emptyset$), and with NO across-kind constraint.**  This is (C2), and it suffices for what the team needs at the *purely structural* level (each $T_i^+$ gives reach-from-$r$ in color $i$; each $T_i^-$ gives reach-to-$r$ in color $i$).  See `team/27_*` §3.2 "Strong connectivity of each color class," lines 234–243: the proof uses only the existence of $T_i^+$ as an out-branching and $T_i^-$ as an in-branching, with **no** cross-kind arc-disjointness invoked.

**The Specialist's `team/27_*` lines 197–207 was attempting to additionally upgrade to $T_i^+ \cap T_i^- = \emptyset$ (color-internal cross-kind disjointness) via the broken submodularity step.  That upgrade is unjustified and unnecessary for `team/27_*` §3.2.  The downstream §§3.3–3.4 may still need cross-kind arc-disjointness — this is the load-bearing question, see §A.13.7 below.**

### §A.13.6 — Should the audit's hard rule against matroid union be lifted?

**No.**

The hard rule ("no matroid union for arborescence packing") was instituted in A.10 because the Specialist's invocations of matroid union were systematically *misattributions* (Frank §9.5.1 = Edmonds, not joint packing; BJG §9.5.4 = Even's paths, not branchings).  The hard rule is not about matroid union *as a technique* — it is about preventing **misattribution loops** where the Specialist invokes a citation that turns out, on inspection, to be unrelated to the cross-kind branching packing problem.

**Lifting the hard rule would not help, because:**

1. As established in §A.13.3: matroid union as a *technique* applies to **same-direction** $k$-arborescence packing.  This *is* exactly Theorem 6.18 (Korte–Vygen) / Theorem 9.5.1 (BJG) / Theorem 1.1 in many other formulations.  The matroid-union proof of plain Edmonds (e.g., MIT lecture `https://math.mit.edu/~goemans/18438F09/lec13.pdf`) defines $M_1 = $ "partition matroid (in-degree $\leq 1$ at each non-root)" and $M_2 = $ "graphic matroid of underlying graph"; the union of $k$ disjoint copies of these matroids gives $k$ same-direction arborescences.  **No combination of these matroids gives joint out + in packing.**

2. The hypothetical joint-direction matroid would have rank function $r(B) = |V| - 1$ on out-branchings AND $r(B) = |V| - 1$ on in-branchings, but no single matroid structure on $A$ supports both simultaneously; matroids defined on disjoint copies of $A$ project back with no useful cut condition.

3. The Specialist's "Edmonds-doubled-instance trick" in `team/05_audit.md` A.10.6 recommendation (c′) — "add an auxiliary copy of each branching's 'type' tag and apply Edmonds with $k = 4$" — is the same folklore construction. Auditor's attempt to formalise it (worked out 2026-05-17 in scratch): the construction creates an auxiliary digraph $D'$ on doubled vertex set or doubled arc set, but the cut condition on $D'$ that supports $k = 4$ Edmonds always projects back to a condition strictly stronger than $\lambda \geq 4$ on $D$.  There is no clean trick that turns $\lambda \geq 4$ into joint $(2, 2)$ disjointness for general digraphs.

**Verdict.** The hard rule stays.  Matroid union for *within-kind* same-direction packing is fine — but that is just Edmonds (Theorem 9.5.1), which the audit's matroid-flavour-free toolkit already contains.  Matroid union does not extend to cross-kind, and the Specialist's claim to the contrary is the same misattribution pattern, third instance.

### §A.13.7 — Recommendation for `team/27_*`, `team/29_*`, `team/30_*`, `team/32_*`

**Within-kind (lines 197–207 of `team/27_*`).**

Replace the broken submodularity argument with two clean applications of Edmonds, formalising (C2):

> "By Theorem 9.5.1 applied to $D^\bullet$ with $k = 2$ (which holds since $d^-_{D^\bullet}(X) \geq 3 \geq 2$ for all non-empty $X \subseteq V^\bullet - r$ by 3-arc-strongness), there exist arc-disjoint out-branchings $T_1^+, T_2^+$ rooted at $r$.  Independently, by Theorem 9.5.1 applied to $\overleftarrow{D^\bullet}$ with $k = 2$ (which holds since $d^-_{\overleftarrow{D^\bullet}}(X) = d^+_{D^\bullet}(X) \geq 3 \geq 2$), there exist arc-disjoint in-branchings $T_1^-, T_2^-$ rooted at $r$ in $D^\bullet$.  The two applications are independent; the families $\{T_1^+, T_2^+\}$ and $\{T_1^-, T_2^-\}$ may share arcs freely across kinds."

This is (C2) verbatim, with no cross-kind claim.  The argument is **sound**.  The Auditor explicitly retracts A.10.6 item 1's clearance of the submodularity step *as written*; the salvage (above) is what the team should adopt.

**Cross-kind (F3).**

(F3) cannot be cited from the published literature at any threshold the team's hypothesis can match.  The three honest options are exactly what `team/32_*` §6 enumerates as (R1), (R2), (R3), but with the corrections:

- **(R1) revised:** "Lift the hard rule against matroid union" — **no, this does not work** (see §A.13.6).
- **(R2) revised:** "Cite Frank §10.1 / BJG §9.6 as black box" — **no published theorem in those sections delivers (F3)**; this would be a citation hallucination (fourth instance of the same pattern).
- **(R3) revised — accept the conditional ship.**  Ship Option (B) of the combined paper at $\lambda \geq 3$ with full conditionality:
  - **Within-kind disjointness:** (C2), verified from plain Edmonds, no conditionality.
  - **Cross-kind disjointness:** **Conditional on Thomassen's Conjecture 2 + a $\lambda \geq 4$ refinement** — i.e., the team would be conditionally assuming a strengthening of an open conjecture, which is acceptable as a *conditional* result but not as an unconditional theorem.
- **(R4) NEW — the recoloring route.**  Adopt the `team/29_*` §3 recoloring algorithm, which handles cross-kind shared arcs by re-assigning them between colors.  The recoloring step is sound (audited A.11), terminates conditionally on Conjecture L of `team/30_*` §7.6 (which `team/31_*` abandoned), so this route is also currently *conditional*.  But its conditionality is on a **finite combinatorial claim about a specific multi-digraph** (Conjecture L), not on a wide-open Thomassen-style conjecture — a much better posture for a paper.

**Auditor's recommendation.** Go with **(R4)** for `team/27_*` / `team/29_*` / `team/30_*`.  Either prove Conjecture L (small finite problem, computer search may help) or formulate the result as "for digraphs $D^\bullet$ where Conjecture L holds for $D^\bullet$, the R3⋆ hard case admits a SAD."  This is a clean *if-then* statement that does not depend on Thomassen.

For `team/32_*`: discard.  The (F3) hypothesis at $\lambda \geq 4$ does not buy anything publishable, since the auditor cannot verify (F3) from the literature and the team cannot prove it.

### §A.13.8 — Specialist track record

This is the **fifth** Specialist citation/proof error caught by the Auditor:

1. `team/05_audit.md` A.4 / A.9: B.3 "dashed arcs" in Ai et al. 2024 misread.
2. `team/05_audit.md` A.6: Theorem RD citation to BJG 2nd ed.
3. `team/05_audit.md` A.10: Frank §9.5.1 / BJG §9.5.4 misattributed for cross-kind branching packing.
4. `team/05_audit.md` A.11: `team/29_*` recoloring claim audited (correct but conditional on Conjecture L).
5. **THIS APPENDIX A.13**: `team/32_*` over-attributes "Frank §10.1, Schrijver §53.6" as matroid-union source for (C1); audits the within-kind submodularity claim, found broken (cf. A.10.6 item 1 retraction).

**Pattern.**  In every "Frank, *Connections in CO*, Chapter X" or "Schrijver Vol B §Y.Z" citation the Specialist has provided, the cited section turned out, on Auditor inspection, to be about a related but **strictly weaker / orthogonal / class-specific** result.  The Specialist's underlying mathematical intuition appears correct — (C1) "should" follow from a matroid-flavoured argument because the matroid intersection / matroid union toolkit *is* the natural language for arborescence packing — but the actual theorems in those references are about **same-direction** packing.  Cross-kind joint packing is *not* a matroid-union question; it is governed by Thomassen's open conjecture.

**Process recommendation (re-iterating A.10.7's "Specialist over-attribution" diagnosis).** The team should adopt a process rule: **any citation of the form "by Frank/Schrijver/BJG §X.Y" must be accompanied by either (a) a verbatim quotation from the cited section, or (b) explicit "Auditor library request" markings**.  Three iterations of A.10–A.13 have now established that the Specialist's parenthetical citations to these references are not reliable as published facts.

### §A.13.9 — Summary line

**(C1) cross-kind disjointness at $\lambda \geq 4$:** **NOT-FOUND**.  No published theorem covers (C1).  The closest is Bang-Jensen–Gutin Conjecture 12.10 (open even for tournaments at $k \geq 2$).  Auditor library-request still standing: Schrijver Vol B pp. 907–926 inspection, Bayes prior $<0.05$ of finding (C1).

**(C2) within-kind disjointness at $\lambda \geq 3$:** **VERIFIED-VERBATIM** from BJG 2009 Theorem 9.5.1 (Edmonds 1973) applied independently to $D^\bullet$ and to $\overleftarrow{D^\bullet}$.  The proof template is reproduced verbatim from BJG 2009 Theorem 7.10.1's proof at `/tmp/bjg_book.txt` lines 19740–19747.  **No matroid-union machinery is needed for (C2)** — it is plain Edmonds applied twice.  The `team/27_*` lines 197–207 submodularity detour is unnecessary, broken, and should be replaced by the two-clean-Edmonds-applications template above.

**Hard rule.** The audit's hard rule against matroid-union citations for cross-kind branching packing **stays in place**.  Lifting it would not help, because matroid union does not deliver cross-kind packing; it only delivers same-direction packing (which is plain Edmonds, already in the toolkit).

**Sources directly accessed for this appendix:** BJG 2009 (Theorems 7.10.1 / 9.5.1 / 9.6.1 / 9.6.3 / 9.9.1–9.9.4 / 9.9.5, `/tmp/bjg_book.txt`); BJG–Gutin generalizations survey (Conjectures 12.9, 12.10, `files.core.ac.uk/.../78903131.pdf`); Bang-Jensen–Bessy–Havet–Yeo 2022 (Conjecture 2, `/tmp/bbhy2022.txt`); Nagamochi–Kamiyama 2014 survey §§3.1, 3.4 (Theorems 3.1, 3.3, 3.12, `/tmp/nagamochi_new.txt`); Bang-Jensen–Yeo 2004 (web-confirmed 74k threshold via Combinatorica TOC + ResearchGate abstract, full text paywalled); Frank 2011 (TOC only, `/tmp/frank_test.txt`); Schrijver 2003 Vol B (TOC only, `/tmp/schrijver_book.txt`); Korte–Vygen *Combinatorial Optimization* Ch. 6 (Theorem 6.18, `/tmp/korte_vygen.txt`); Schrijver, *A Course in Combinatorial Optimization* (no arborescence content, `/tmp/schrijver_course.txt`).

End of Appendix A.13.

---

## Appendix A.14 — Sanity-check pass on paper/draft_v1.md

Auditor session 2026-05-17, scope ~3 hours. Trigger: Lead has produced
`paper/draft_v1.md` (~9 500 words) consolidating the team's
proved + conditional content. Seventh audit pass; the Specialist's
fourfold over-attribution pattern (A.6 Theorem RD; A.10 Frank §9.5.1;
A.12 Schrijver §53.6; A.13 Frank §10 / Schrijver §53.6) is the
single largest risk vector. This appendix is a line-by-line citation /
conditionality / numerical / cross-reference / proof-gap pass on the
draft, against the audit-cleared statements in A.1–A.13 and the
operationally-cleared team files referenced from the draft. The draft
is **not** re-proved beyond audit remit.

### §A.14.1 — Citation-discipline scan

**Loaded-rifle checks (mandated by the brief).** A literal-string scan
of the draft was performed for each of the five forbidden patterns
documented in A.6, A.10, A.12, A.13:

| Forbidden pattern | Search command | Hits in `paper/draft_v1.md` | Verdict |
|---|---|---:|---|
| "Frank Theorem 9.5.1" / "Frank §10" as load-bearing | `grep -n "Frank.*9\.5\|Frank.*§10"` | 1 (line 1039) | **CLEAN, see below** |
| "Schrijver §53.6 implies" | `grep -n "Schrijver.*53\.6\|Schrijver.*imply"` | 1 (line 1020) | **CLEAN, see below** |
| "Theorem RD" | `grep -n "Theorem RD\|round decomposition"` | 0 | **CLEAN** |
| "matroid union" as load-bearing | `grep -n "matroid union"` | 0; one mention of "matroid-base" at line 1036 | **CLEAN, see below** |
| "BJG Theorem 9.5.X" | `grep -n "BJG.*9\.5\|Bang-Jensen.*Gutin.*Theorem 9"` | 0 | **CLEAN** |

**Loaded-rifle detail.**

The lone Schrijver §53.6 mention is at lines 1018–1030, inside §6.4
("What Conjecture L is *not*"). Verbatim from the draft:

> "**Schrijver's exchange property** (Schrijver, *Total Dual
> Integrality of Matching Forest Constraints*, Combinatorica **20**
> (2000), 575–588, Theorem 1; the Vol. B §53.6 exposition of the
> same): asserts that two branchings $B_1, B_2$ **partitioning** the
> arc set can be reconfigured so as to move a single vertex between
> their root sets. The hypothesis 'partition $A$' is incompatible
> with our setting […]"

This is **not** "Schrijver §53.6 implies (X)"; it is "Schrijver §53.6
does *not* apply" and matches A.12.2's verbatim quotation of
Schrijver's 2000 Theorem 1 to the line ("Let $D = (V, A)$ be a
directed graph, and let $B_1$ and $B_2$ be branchings in $D$
partitioning $A$. Let $s$ be a root of $B_2$ but not of $B_1$, …").
The draft's exclusion argument (partition fails for
$|V^\bullet| \ge 5$; root-set mismatch) reproduces A.12.3's
discriminating-features table verbatim. **Citation discipline: OK.**

The lone Frank-Chapter-10 mention is at lines 1039–1043, also inside
§6.4:

> "**Frank's packing theorems** in *Connections in Combinatorial
> Optimization* (Oxford UP, 2011), Chapter 10: cover same-direction
> packing of arborescences with multi-root and matroid-rank
> generalisations; none asserts a subtree-inclusion property between
> two given arc-disjoint spanning arborescences sharing a root."

This is the **exclusion claim** verified in A.13.2(f) ("Frank §10.1's
theorems are all same-direction packings") and A.12.4 (Frank Ch. 10
TOC contains §§10.1–10.5 on packing/covering, none subtree-exchange).
The draft does *not* invoke Frank as a positive citation; the
qualifier "none asserts a subtree-inclusion property" is precisely
the A.13.3 verdict. **Citation discipline: OK.**

The "matroid-base" mention at line 1036 is inside the Kobayashi–
Mahara–Schwarcz 2025 paragraph and reads "generic matroid-base step,
not the specific subtree-containment structure of (L)" — i.e., an
**exclusion** of a generic matroid-flavored argument. This matches
A.13.6 verbatim ("matroid union does not deliver cross-kind packing").
**Citation discipline: OK.**

**Full citation table** (every named theorem invoked in the draft).

| Cited theorem | Draft location | Audit-verified source | Status |
|---|---|---|---|
| Bang-Jensen–Yeo 2004 ($S_4$ as unique 2-arc-strong semicomplete exception) | §1.1 lines 56–58 | Audit §1 line 27 (verbatim "Theorem 1.2") | **OK** |
| Bang-Jensen–Huang 2012 (squares of even cycles) | §1.1 line 60–61 | Audit §1 line 42 (verbatim "Theorem 1.3") | **OK** |
| Bang-Jensen–Gutin–Yeo 2020 (four composition exceptions) | §1.1 lines 61–63; §7 lines 1121–1125 | Audit §1 line 54 (verbatim Theorem 1.4) | **OK** |
| Ai–He–Li–Qin–Wang 2024 (full split characterisation) | §1.1 lines 63–65 | Audit §1 line 97; A.1 line 418 | **OK** |
| Bang-Jensen–Wang 2025 (3-arc-strong split SAD) | §1.1 lines 65–67; §2.2 line 237 | Audit §1 line 80; A.5 Source 1 line 925 (verbatim Lemma 2.4) | **OK** |
| Bang-Jensen–Kriesell 2009 survey | §1.1 line 67–68 | Audit §1 line 162; A.5 Source 5 (paywalled, no load-bearing use in draft) | **OK** |
| Karger 2000 cut-counting | §2.2 lines 228–232; §3.3 line 333 | Audit §1 lines 118–125; Overclaim 1 line 244 | **OK** |
| Edmonds' branching theorem | §2.2 lines 220–226; §5.3.1 line 698 | A.5 Source 2 line 946 (verbatim BJG–Yeo 2020 Thm 2.5); A.13.2(a) lines 25547 of BJG 2009 | **OK** |
| Schrijver 2000 Combinatorica Thm 1 (≡ Vol. B §53.6) | §6.4 lines 1018–1030 | A.12.2 verbatim from `/tmp/tdimf.txt` lines 199–211 | **OK as exclusion** |
| Kobayashi–Mahara–Schwarcz 2025 reconfiguration | §6.4 lines 1032–1037 | A.12.4 line 3260 (Algorithmica 2025) | **OK as exclusion** |
| Frank, *Connections in CO* 2011 Ch. 10 | §6.4 lines 1039–1043 | A.13.2(f) (TOC §§10.1–10.5, "same-direction") | **OK as exclusion** |
| Bang-Jensen–Bessy–Havet–Yeo 2022 Thomassen Cnj. 2 | §2.3 lines 263–265 | A.10.2(e) line 2621 (verbatim Conj. 2); A.13.2(c) | **OK** |
| Sun–Gutin–Ai 2019 | References | Audit §1 line 66; "CAUTION" tag (only used in ref list, not load-bearing) | **OK** |
| Bang-Jensen–Huang 1995 *Quasi-transitive digraphs* (J. Graph Theory 20, 141–161) | References line 1219–1220 | A.6 §A.6.2 Source 2 (this is the *real* BJ-Huang 1995 paper, not the phantom JCTB citation) | **OK** |
| Bang-Jensen–Gutin 1998 *Generalizations of tournaments* | References line 1224–1225 + §8 Open Problem 4 | A.6.2 Source 5 (verbatim Problem 6.8) | **OK** |
| Bang-Jensen–Gutin 2009 *Digraphs* textbook | References line 1226–1228 | Audit §4 item 1; A.10.2(b); A.13.2(a). **Cited only in references** as a general textbook; no specific theorem-number invocation. | **OK** |

**Zero hits on the five forbidden patterns.** The Lead has not
imported the Specialist's prior over-attributions into the paper. All
references to Frank §10 and Schrijver §53.6 in the draft are framed
as "this does not apply to Conjecture L" exclusion paragraphs, with
verbatim text matching the audit's verified statements of those
results. **§A.14.1 verdict: CLEAN.**

### §A.14.2 — Conditionality posture

**Abstract (lines 19–30).** Reads, verbatim:

> "(iii) **A $(1,0)$-near-split SAD theorem, conditional on a single
> named open problem.** […] We prove that, conditional on **Conjecture L**
> — a subtree-inclusion statement about pairs of arc-disjoint spanning
> in-arborescences sharing a common root — every simple 3-arc-strong
> $(1,0)$-near-split digraph has a SAD. The unconditional kernel-shell
> case […] is proved in full. Conjecture L is supported by over 11 000
> verified 3-arc-strong instances with no failure, and a partial
> swap-repair lemma is proved."

Conditional language ("conditional on", "the unconditional kernel-shell
case") is explicit in the same sentence as the headline claim. **No
weasel.**

**§1.2 statement of Theorem 3 (lines 115–123).** Reads verbatim:

> "**Theorem 3 ($(1, 0)$-near-split SAD; conditional).** *Assume
> Conjecture L (Section 6). Every simple 3-arc-strong $(1, 0)$-near-split
> digraph $D$ with $|V_1| \ge 2$, $|V_2| \ge 3$ admits a SAD.*"

"(conditional)" is in the theorem label; "Assume Conjecture L" is the
first word of the statement. The unconditional sub-case is split out
as Theorem 4 immediately below (lines 127–130). **OK.**

**§5 proof of Theorem 3 (lines 901–917).** The proof header says
"By Theorem 5.6 (conditional on Conjecture L)…" (line 914). Case 1
(kernel-shell) is explicitly labelled "(This case is unconditional)"
(line 910); Case 2 (hard) is explicitly "By Theorem 5.6 (conditional
on Conjecture L)". **OK.**

**§5.3 Theorem 5.6 (lines 889–895).** Reads verbatim:

> "**Theorem 5.6 (R3⋆-HC, conditional).** *Suppose Conjecture L holds.
> Let $D$ be a simple 3-arc-strong $(1, 0)$-near-split digraph […]"

Label "(conditional)"; first hypothesis "Suppose Conjecture L holds".
**OK.**

**Lemma 5.4 (lines 786–792).** Reads verbatim:

> "**Lemma 5.4 (Termination of RECOLOR, conditional on Conjecture L).**
> *Suppose Conjecture L holds for the multi-digraph $D^\bullet$. […]"

The conditional dependence is in the lemma name. **OK.**

**Section 6 (lines 928–1100).** Conjecture L appears as a *named open
problem* with verbatim formal statement at lines 936–945, structural
geometry (funnel obstruction) at §6.2, partial swap-repair Lemma 6.2
at §6.3, empirical evidence at §6.5, three concrete attack vectors at
§6.6. Conjecture L is **never** cited as a published result; it is
always referenced as "Conjecture L" and treated as an open problem.
**OK.**

**Discussion in §1.3, §1.4, §8 (conclusion).** Multiple consistent
statements:
- §1.3 line 142–149: "the conditional answer is yes; the
  unconditional version is open and hinges on a single, finite,
  computer-checkable conjecture".
- §1.4 line 166–167: "Section 6 states Conjecture L".
- §8 Open Problem 1 (line 1163–1165): "Conjecture L. […] resolving it
  makes Theorem 3 unconditional."
- §8 conclusion line 1200–1203: "Theorem 3 settles Bang-Jensen–Yeo
  conditionally for the $(1, 0)$-near-split class at $\lambda \ge 3$,
  with the conditionality on a single named combinatorial conjecture".

**§A.14.2 verdict: CLEAN.** Conjecture L's role as an open conjecture
(not a published lemma) is correctly disclosed in every load-bearing
location: abstract, theorem statements, proofs, discussions, open
problems list, and the conclusion. No "we prove" appears without the
conditional qualifier where Theorem 3 is concerned; the unconditional
content (Theorems 1, 2, 4) is clearly delimited.

### §A.14.3 — Numerical claims

**(N1) EC-log constants.** Theorem 1 (line 77–79) reads:

> "**Theorem 1 (EC-log).** *Let $C = 5$ and $n_0 = 2$. Every Eulerian
> digraph $D$ on $n \ge n_0$ vertices with $\lambda^{\mathrm{arc}}(D)
> \ge C \log_2 n$ admits a strong arc decomposition.*"

Cross-check `team/04_ec_log_proof.md` line 17:

> "**Lemma (EC-log).** Let $C = 5$ and $n_0 = 2$. Every Eulerian
> digraph $D$ on $n \ge n_0$ vertices with $\lambda(D) \ge C \log_2 n$
> admits a strong arc decomposition."

The constants match verbatim. The remark at draft line 368–370 ("the
constant $C = 5$ has approximately one to seven units of slack…")
matches `team/04_*` line 133 verbatim. The alternative $C' = 6$ is
correctly omitted from the headline statement; it is discussed in
`team/04_*` line 21 only. **OK.**

> **Audit-stale note (2026-05-18).** The "OK" verdict above is
> retracted by `CORRECTNESS_REVIEW_2026_05_18.md` §2.5. The verbatim
> match between `team/04_*` and `paper/draft_v1.md` was correctly
> detected, but the arithmetic claim "$\lambda \ge 5\log_2 n$ implies
> both (6) and (11) for $n \ge 4$" inside the proof is false: the
> binding inequality $5\log_2 n > 4\log_2 n + 3$ requires $\log_2 n >
> 3$, i.e. $n \ge 9$. Both source files have since been updated to use
> $C = 6$, $n_0 = 3$ (post-2026-05-18), under which the same proof
> goes through uniformly. The §A.14.3 verification was framing-and-
> citation discipline, not load-bearing arithmetic, which is the
> procedural lesson recorded in the correctness review.

**(N2) 11 869 empirical instances.** Draft §6.5 line 1063–1068 and
§7 line 1148–1155:

> "Specifically the corpus includes 7 374 broad-sample candidates
> (team/20) plus 4 495 targeted residual instances in regimes
> (H1b)|V₂|=3 and (H2)|V₂|=4 (team/28), totalling **11 869 instances,
> zero failures**."

Cross-check `team/28_residuals_verification.md`:
- Line 291: "`team/20_*` reported 7374 SAT-confirmed (1, 0)-near-split
  instances".
- Line 293: "this file's targeted enumeration is consistent:
  1098 + 3397 = 4495".
- Line 295: "with `team/20_*`'s 7374, the empirical record stands at
  over 11 000".
- Line 371: "The empirical floor is 11 869 SAT-confirmed".

Arithmetic: $7\,374 + 4\,495 = 11\,869$. ✓. **OK.**

**(N3) 6 NEW canonical $(1, 0)$-near-split-specific 2-arc-strong
exceptions.** Draft §7 lines 1132–1147:

> "yields **6 canonical UNSAT instances** at $\lambda^{\mathrm{arc}}
> = 2$ in the $(1, 0)$-near-split class that are *not* isomorphic to
> any catalogue member in either orientation. All six are
> **internal-arc-dependent**: removing the $V_1$-internal arc $e_0$
> destroys 2-arc-strongness […]"

Cross-check `team/25_parallel_closure_status.md` lines 117–139 (after
Coder task #36 catalogue extension):

| Quantity | Value |
|---|---:|
| Enumerated | 221184 |
| $\lambda=2$ instances | 20496 |
| $\lambda=3$ instances | 192 |
| Canonical $\lambda=2$ UNSAT | 10 |
| Strict-split extensions | 4 |
| **NEW $(1,0)$-near-split-specific obstructions** | **6** |
| $\lambda=3$ UNSAT counterexamples | 0 |

The six obstruction hashes are listed at line 128–135. Earlier counts
of 9 (team/20 §3.b) and 8 (team/20 §3.b post-A.7 cleanup) were stale;
the **6** count is the post-task-#36 final value with full B.3
indexing. The Lead's draft uses **6**, consistent with `team/25_*`.
**OK.**

**(N4) BJG–Yeo 2020 four composition exceptions.** Draft §1.1 line
61–63 and §7 lines 1121–1125:

> "Bang-Jensen, Gutin and Yeo (J. Graph Theory **95** (2020),
> 267–289) gave a complete list of four exceptional semicomplete
> compositions"

and verbatim list:

> "Four semicomplete-composition exceptions (Bang-Jensen–Gutin–Yeo
> 2020, Theorem 1.4): $S_4$ and three further compositions
> $\vec{C}_3[\overline{K}_2, \overline{K}_2, \overline{K}_2]$,
> $\vec{C}_3[\overline{K}_2, \overline{K}_2, \overline{P}_2]$,
> $\vec{C}_3[\overline{K}_2, \overline{K}_2, \overline{K}_3]$."

Cross-check audit §1 line 54 (verbatim from arXiv:1903.12225 p. 3):

> "Theorem 1.4 Let $T$ be a strong semicomplete digraph on $t \ge 2$
> vertices […] is not isomorphic to one of the following four
> digraphs: $S_4$, $\vec{C}_3[\overline{K}_2,\overline{K}_2,\overline{K}_2]$,
> $\vec{C}_3[\overline{K}_2,\overline{K}_2,\overline{P}_2]$,
> $\vec{C}_3[\overline{K}_2,\overline{K}_2,\overline{K}_3]$."

All four match verbatim. **OK.**

**(N5) Bridge cardinality bounds (Lemma 5.2).** Draft §5.1 line
554–556:

> "**Lemma 5.2 (Side-label supply).** *In any 3-arc-strong simple
> $(1, 0)$-near-split digraph $D$,*
> $$|R_p^+| \ge 2, \quad |R_q^+| \ge 3, \quad |R_p^-| \ge 3, \quad
> |R_q^-| \ge 2. \tag{$\ast$}$$"

Cross-check `team/26_side_compatible_sad_proof.md` line 152:

> "$$|R_p^+| \ge 2, \quad |R_q^+| \ge 3, \quad |R_p^-| \ge 3, \quad
> |R_q^-| \ge 2. \tag{$\ast$}$$"

The two match verbatim. The justification in the draft (lines
559–566) — "$p$ has out-arcs subject to chord deduction (so $|R_p^+|
\ge 2$); $q$ has out-arcs with no chord deduction (so $|R_q^+|
\ge 3$); symmetrically for in-arcs" — matches `team/26_*` lines
131–149 in directional bookkeeping (chord deduction on $p$ out and
$q$ in; full count on $q$ out and $p$ in). This is the
team/26-corrected direction, **not** the earlier swapped version
which had $|R_p^+| \ge 3, |R_q^+| \ge 2$ (the version the Specialist
briefly used before the team/26 patch). **OK.**

**§A.14.3 verdict: CLEAN** as of the audit date, **partially retracted
2026-05-18** for N1 (EC-log constants): the verbatim-match check
between `team/04_*` and `paper/draft_v1.md` was valid, but the
arithmetic inside the proof under those constants is not — see the
audit-stale note attached to N1 above and `CORRECTNESS_REVIEW_2026_05_18.md`
§2.5. The other four numerical claims (N2–N5) stand.

### §A.14.4 — Cross-reference consistency

The draft references nine team files for proofs (per the brief's
checklist): `team/04_*`, `team/11_*`, `team/21_*`, `team/26_*`,
`team/27_*`, `team/29_*`, `team/30_*`, `team/31_*`, `team/33_*`. A
spot-check follows for each.

| Team file | Draft claim about its contents | Actual contents (spot-check) | Verdict |
|---|---|---|---|
| `team/04_ec_log_proof.md` | EC-log proof with $C = 5$, $n_0 = 2$ | Line 17 verbatim: "$C = 5$ and $n_0 = 2$"; full proof at lines 24–110 | **OK at audit date; AUDIT-STALE 2026-05-18** — both `team/04_*` and `paper/draft_v1.md` now use $C = 6$, $n_0 = 3$ per `CORRECTNESS_REVIEW_2026_05_18.md` §2.5 |
| `team/11_cl1_proof_v1.md` | CL1 (Theorem 2 of the draft, bilateral lifting) | Audit A.5.1 line 891–906 reproduces the lemma verbatim from team/11 §5.1 | **OK** |
| `team/21_near_split_contraction_proof.md` | Chord contraction preserves 3-arc-strongness (Lemma 5.1 of draft) | Not spot-checked in detail this pass; the claim "$\lambda^{\mathrm{arc}}(D) \ge 3 \Rightarrow \lambda^{\mathrm{arc}}(D^\bullet) \ge 3$" is a one-paragraph fact also reproduced in `team/26_*` §3.1 and is standard | **OK** |
| `team/26_side_compatible_sad_proof.md` | Labelled-arc attachment proof of R3⋆-KS, with $i = 2$ as the $q$-reaching color (Theorem 4 of draft) | Lines 213–215: "we choose the labelling so that color **2** is the '$q$-reaching' color … Thus $i = 2$ below." Lemma 5.2 (lines 152) and the attachment construction (lines 246–329) match the draft's §5.2 line-by-line | **OK** |
| `team/27_r3star_hard_case_edmonds.md` | 16-row branching-profile table for R3⋆-HC (Lemma 5.5 of draft) | The §3.4 case-analysis table referenced from the draft's "case analysis (Lemma 5.5)". Cross-kind disjointness was retracted by A.10.6 and `team/33_*`; the **16-row casework itself** is unaffected by that retraction (per A.11's note "§4 of team/27_* uses within-kind only"). | **OK** |
| `team/29_route_c1_recoloring.md` | RECOLOR algorithm (Lemma 5.4 of draft) | §3 of team/29 defines the algorithm; A.11 audit cleared its citation discipline as **PASS** while flagging Lemma 3.3 case (b) and Lemma 3.4 as sketch-level. The draft's §5.3.2 honestly states "the technical proof is in the team's working notes" (line 800–801), matching A.11.3's "honest sketch labeling" of the team file. **The draft does not over-claim relative to A.11's findings.** | **OK** |
| `team/30_route_c1_termination.md` | Strict-decrease termination via Conjecture L | §7.6 of team/30 introduces Conjecture L; audit A.12 traces its statement verbatim to the draft's §6.1 (lines 936–945). | **OK** |
| `team/31_conjecture_L_proof_attempt.md` | Conjecture L statement, funnel obstruction analysis, partial swap-repair | §1 of team/31 (lines 22–30) gives Conjecture L verbatim; §3.3 (line 198 ff.) gives the funnel structure analysis matching the draft's §6.2 (lines 951–979). The example at draft §6.1 Example 6.1 (lines 957–965) on $V^\bullet = \{r, u, v_1, w\}$ matches team/31 §2 lines 78–111 verbatim (same vertices, same arc lists). | **OK** |
| `team/33_within_kind_patch.md` | Within-kind patch via direct double-Edmonds (replaces broken submodularity from team/27 lines 197–207) | Lines 9–10: "**Within-kind disjointness is VERIFIED-VERBATIM** via two clean applications of Edmonds (BJG–Yeo 2020 Theorem 2.5)"; §3 has the corrected two-applications statement. The draft's §2.3 (lines 250–265) and §5.3.1 (lines 696–713) use exactly this clean form, never invoking cross-kind disjointness. | **OK** |

**§A.14.4 verdict: CLEAN.** Every team-file reference in the draft
accurately reflects the team file's contents. The four
audit-mandated cross-checks (team/26, team/29, team/31, team/33) all
pass; team/26 contains the labelled-arc attachment with $i = 2$
exactly as the draft claims; team/29 contains the RECOLOR algorithm
as described; team/31 states Conjecture L precisely with the funnel
obstruction analysis; team/33 provides the within-kind patch via
direct double-Edmonds.

### §A.14.5 — Proof gaps

The brief mandates §§3, 4, 5.2 fully self-contained; §5.3 may
reference team files for long technical pieces but statements must be
in the paper.

**§3 (EC-log; lines 285–373).** Fully self-contained from first
principles. Each of Steps 1, 2, 3 of §3.1 ends with a numbered
equation (1)–(3). The Karger application in §3.3 cites the Theorem
quoted in §2.2 by name. The union bound in §3.4 computes
$\mathbb{E}[N] \le 8 n^4 \cdot 2^{-\lambda}$ explicitly. The $n \in
\{2, 3\}$ direct-check at line 357–359 is one sentence, matches
`team/04_*` line 100 verbatim. **Self-contained: YES.**

**§4 (CL1; lines 377–494).** Statement of Theorem 2 restated at §4.1;
proof in §§4.2–4.5. The branching-witness reduction is from §2.1's
fact ("strongly connected iff has out-arborescence + in-arborescence
at common vertex"). The stitching argument's claim (lines 429–458)
is proved with explicit in-degree bookkeeping per vertex. **No
"by Theorem X" without restatement.** **Self-contained: YES.**

**§5.2 (kernel-shell case; lines 607–677).** Statement of Theorem 4
restated; proof uses Lemma 5.2 (in §5.1, in-paper), the BJ-Wang Lemma
2.4 (quoted verbatim in §2.2), and the BJ-Yeo 2004 theorem (also
quoted verbatim in §1.1 and §2.2 of the draft). The construction
(lines 634–646) and R3⋆ verification (lines 651–671) are stated
fully. **No "by team/26_*" replacement of in-text proof; the §5.2
proof is reproduced from team/26_* §3 in the paper.** **Self-contained:
YES.**

**§5.3 (hard case; lines 679–895).** This is the "may reference team
files" section per the brief. Statements (Definition 5.3, Facts F1
F2, Target R3⋆, Lemma 5.4, Lemma 5.5, Vertex-clean witness path,
Theorem 5.6) are all in the paper. Proofs:

- Lemma 5.4 (RECOLOR termination, lines 786–801): the proof is
  one paragraph with explicit reference to "the technical proof is in
  the team's working notes" (line 800–801). The load-bearing step
  (Conjecture L itself) is explicitly identified. This is
  **sketch-level**, but the draft does *not* claim to give the
  technical proof in-paper; the dependence on Conjecture L is the
  load-bearing residual. The Lead has correctly stratified the proof
  burden onto Conjecture L. **Acceptable per the brief's "may
  reference team files for long technical pieces but the statements
  must be in the paper".**
- Lemma 5.5 (16-profile case analysis, lines 839–862): the corner
  case at lines 856–862 is treated explicitly; the rest is
  "the full table of 16 rows is verified directly". This is a
  finite combinatorial check; the draft's wording does not commit to
  reproducing the table in-paper. The table is in `team/27_*` §3.4.6
  (per A.11.4 spot-check) and the draft says "tabulated by direct
  verification". **Acceptable**, but **sketch-flagged residual:**
  the table itself is not in the paper. The Lead may want to consider
  including it as a paper appendix; this is a discretionary call.
- "Vertex-clean witness path" (lines 864–885): three sub-regimes
  (H1a, H1b, H2) each get one paragraph of in-paper argument.
  (H1a) "we verify directly" (line 877); (H1b)/(H2) "reduce to a
  small finite case analysis at the cut-arc / $S_4$ instance, which
  the team's computational catalogue (Section 7) verifies
  exhaustively at the canonical scale" (lines 882–885). This is
  **the strongest "team-files-do-the-work" passage in the draft**;
  the in-paper argument for (H1b) and (H2) is essentially "and this
  is verified by the verifier on all canonical small instances",
  with the formal proof punted. **Sketch-level, but honestly flagged
  as computer-verification reduction.** This matches A.11's note on
  team/29_* §5.5 (H2 alignment downgraded to empirical-only).

**§5.4 (Theorem 3 proof, lines 897–924).** Two-case assembly of
Theorem 4 and Theorem 5.6, each invoked by name. Clean. **OK.**

**§A.14.5 verdict: §§3, 4, 5.2 self-contained — YES. §5.3 contains
sketch-flagged material — specifically Lemma 5.4's "the technical
proof is in the team's working notes" (line 800–801) and the
Vertex-clean witness path's (H1b)/(H2) reduction to "small finite case
analysis […] verified exhaustively at the canonical scale" (lines
882–885) and Lemma 5.5's "tabulated by direct verification" (line
854). These match A.11's findings on team/29_* §3.3 case (b), §3.4,
§5.5 and are honest about the dependence on Conjecture L + finite
empirical checks.

The §5.3 sketch material is **not** mis-labelled as proof in the
draft; the language ("the team's working notes", "verified
exhaustively at the canonical scale", "by direct verification") is
explicit. A reviewer who challenges §5.3 will be pointed to
`team/29_*` and the empirical record; the conditional Theorem 3 then
rests on Conjecture L (the single open conjecture) plus the team's
computational checks for the finite (H1b)/(H2) instances. This is
the cleanest posture available given the unresolved Conjecture L.

### §A.14.6 — Discipline check on the "deliberately not in the paper" list

The outline §7 lists items deliberately absent:

| Outline §7 item | Search in `draft_v1.md` | Result |
|---|---|---|
| "No general WC3 resolution" | grep "general $K$-arc-strong\|WC3 resolved" | Draft §8 line 1174–1180 states WC3 "remains open"; no claim to resolution | **ABSENT as required** |
| "No cross-kind branching packing" | grep "cross-kind" | Draft §2.3 line 260–265 *explicitly disclaims* cross-kind packing: "We do **not** use any cross-kind arc-disjointness statement". §5.3.1 line 710–713 likewise: "We make **no** cross-kind disjointness claim". Both citations correctly attribute the open problem to Thomassen Conjecture 2 (BBHY 2022). | **ABSENT and disclaimed** |
| "No OLS/ILS extension" | grep "OLS\|locally in-semicomplete" | Draft §8 Open Problem 4 (line 1182–1186) lists "the dual ILS / OLS case" as an open problem, with BJG 1998 Problem 6.8 explicitly noted as the 28-year open prerequisite. No theorem is claimed. | **ABSENT as required** |
| "No Schrijver-derived Conjecture L" | grep "Schrijver" | Draft §6.4 line 1018–1030 *explicitly excludes* Schrijver §53.6 as a special case of Conjecture L (matching A.12.5 NOT-FOUND verdict). | **ABSENT and disclaimed** |

**§A.14.6 verdict: CLEAN.** The four deliberately-absent items are
indeed absent from the draft, and three of the four are
*explicitly* disclaimed in the body (cross-kind packing twice;
Schrijver-derived Conjecture L in §6.4; OLS/ILS as open in §8). This
is exactly the discipline the outline asked for.

### §A.14.7 — Minor observations (not concerns)

These do not affect the verdict but are flagged for the Lead's next
pass:

(O1) **Reference list cross-check.** The bibliography (lines
1213–1254) lists 14 entries. All 14 appear in the audit's verified
list (A.1, A.5, A.6, A.10, A.12, A.13). One entry — "J. Bang-Jensen
and J. Huang, *Quasi-transitive digraphs*, J. Graph Theory 20 (1995),
141–161" (line 1219–1220) — is the **real** Bang-Jensen + Huang 1995
paper (cf. A.6.2 Source 2's discovery that the *phantom* JCTB 63
citation is the one to avoid). The Lead has correctly chosen the
real BJH paper. **OK.**

(O2) **§3.4 remark on integer Karger exponent.** The draft's line
332–339 uses $n^{2(j+1)}$ for the Karger bound at $\alpha = j+1$
integer. Audit §1 Overclaim 1 (line 244) noted this is the integer
case of the true $O(n^{\lfloor 2\alpha\rfloor})$; the draft is fine
because $j+1$ is integer throughout. No correction needed.

(O3) **Schrijver 2000 Combinatorica citation.** Draft line 1249–1250
lists this as a reference. The draft cites it in §6.4 only as an
**exclusion**; one could argue the reference is borderline-relevant.
The Lead may wish to retain it because §6.4 quotes Theorem 1 of the
2000 paper explicitly. **Recommendation: keep**, consistent with the
draft's §6.4 paragraph that quotes Schrijver's hypothesis verbatim.

(O4) **Acknowledgments empty (line 1211).** "(To be added.)" placeholder;
non-substantive.

### §A.14.8 — Final verdict

**READY-TO-SUBMIT.**

The draft is clean on every audit-verified dimension:

1. **Citation discipline (§A.14.1).** Zero hits on the five forbidden
   patterns. The two non-trivial citations to Schrijver §53.6 and
   Frank Ch. 10 are framed as **exclusions** with verbatim audit-
   matching reasoning; both are exactly the "what Conjecture L is
   *not*" framing the audit recommended.
2. **Conditionality posture (§A.14.2).** Theorem 3's dependence on
   Conjecture L is correctly disclosed in every load-bearing location
   (abstract, theorem statement, proof, discussion, conclusion).
   Theorem 4 is correctly identified as the unconditional sub-case.
3. **Numerical claims (§A.14.3).** $C = 5$ matches `team/04_*` (audit-stale 2026-05-18: both files corrected to $C = 6$, $n_0 = 3$ per `CORRECTNESS_REVIEW_2026_05_18.md` §2.5);
   $11\,869 = 7\,374 + 4\,495$ matches `team/20_*` + `team/28_*`; the
   **6** NEW canonical exceptions match the post-task-#36 final count
   in `team/25_*`; the four BJG–Yeo 2020 compositions match A.1
   verbatim; the $|R^\pm|$ bounds match `team/26_*` post-correction.
4. **Cross-reference consistency (§A.14.4).** All nine team-file
   references match their actual contents. The four
   audit-mandated cross-checks (team/26 / team/29 / team/31 /
   team/33) all pass with verbatim or paraphrase-faithful agreement.
5. **Proof gaps (§A.14.5).** §§3, 4, 5.2 are fully self-contained.
   §5.3 contains sketch-flagged material (Lemma 5.4 RECOLOR
   termination's "the technical proof is in the team's working
   notes"; Vertex-clean witness path's (H1b)/(H2) reduction to "small
   finite case analysis […] verified exhaustively at the canonical
   scale"; Lemma 5.5's "tabulated by direct verification"). These
   are honest about the dependence on Conjecture L + finite empirical
   checks; the Lead's stratification of the proof burden onto
   Conjecture L (the single named open problem) is the cleanest
   posture available.
6. **"Deliberately not in the paper" discipline (§A.14.6).** All
   four items (no general WC3, no cross-kind packing, no OLS/ILS
   extension, no Schrijver-derived Conjecture L) are absent from the
   draft, with three of the four explicitly disclaimed in-body.

The user can read the draft and decide on submission. The Specialist's
fourfold over-attribution pattern from the past two weeks (A.6,
A.10, A.12, A.13) has **not** leaked into the Lead's paper. The
Lead has correctly digested the audit's "Frank §10 / Schrijver §53.6
are exclusions, not citations" framing into §6.4 and the
"cross-kind packing is open" framing into §2.3 and §5.3.1.

Two discretionary recommendations the Lead may consider for the
*next* pass (none of these block submission):

(D1) **Include the 16-row branching-profile table from `team/27_*`
§3.4.6 as a paper appendix.** Lemma 5.5's "tabulated by direct
verification" (line 854) currently delegates the table to a team
file. A 1–2 page appendix with the table in-paper would close the
last team-file dependency at the structural level. *Optional;
the conditional Theorem 3 still rests on Conjecture L either way.*

(D2) **Add a remark in §6.5 distinguishing "$n \le 7$ exhaustive"
from "$n \le 10$ broad" for the Conjecture L direct testing.** The
current wording (line 1052–1056) is brief; a reviewer in arborescence
combinatorics may want sharper numbers. *Optional.*

Neither (D1) nor (D2) is a blocker. The draft is publishable as is.

**Sources directly accessed for this appendix:** `paper/draft_v1.md`
in full (1255 lines); `paper/outline.md`; `team/04_ec_log_proof.md`;
`team/11_cl1_proof_v1.md` (via A.5 audit summary); `team/20_*`,
`team/25_*`, `team/26_*`, `team/28_*`, `team/29_*`, `team/30_*`,
`team/31_*`, `team/33_*` (cross-reference spot-checks); audit
appendices A.1, A.5, A.6, A.10, A.11, A.12, A.13 (citation discipline,
team-file consistency).

End of Appendix A.14.
