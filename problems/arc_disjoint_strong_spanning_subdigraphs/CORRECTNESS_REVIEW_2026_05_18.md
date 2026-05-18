# Correctness Review of the Bang-Jensen–Yeo SAD Attack

Reviewer: independent auditor (Claude).
Date: 2026-05-18.
Scope of audit: everything under
`/Users/lelarge/Recherche/graph-conjectures/problems/arc_disjoint_strong_spanning_subdigraphs/`
as committed on 2026-05-17 plus the working notes generated up to that date.

---

## 0. Executive verdict

The project is honest, well-organized, and has rebounded from genuine
mistakes (Conjecture L, OLS route, F3, the original CL1 v1 with
hypothesis (4)) once the user's red-team uncovered them. The two
theorems still standing — **Theorem 1 (EC-log)** and **Theorem 2
(CL1 bilateral lifting)** — are both essentially correct as
*mathematical content*, but I find one concrete arithmetic error in the
EC-log proof that affects the stated constants for small `n`, plus a
mild novelty/citation caveat for CL1. The third standing theorem
(R3*-KS kernel-shell near-split) is out of scope for this review but
should be revisited with the same level of skepticism as the items
below. The verifier code is correct in encoding and in cross-check
discipline. The 4,613-instance negative search (Phase 3 v2) is a
meaningful negative result but its scope is much narrower than the
report's coverage table suggests. Several of the UNSAT benchmark
transcriptions (Lemma 2.11, Lemma 3.12, the four BJG–Yeo composition
exceptions, and the B.2/B.3 cases) are constructed by hand from the
papers and there are at least two transcription wobbles I want to flag.
Below I tag every finding by severity and reference the specific file
and line.

I would not block submission of EC-log and CL1 as a short note **after**
the §2 fix is made and §4 caveats are added. I would block any wider
publishability claim resting on the negative search alone, and I am
skeptical of the "no published bilateral analogue" claim for CL1 until
one more pair of eyes verifies it against BJ–Yeo 2004 (paywalled —
auditor only had BJG–Yeo 2020's re-use of the §3 technique).

---

## 1. Findings by file/claim, severity-tagged

### 1.1 attack_plan.md, paper/draft_v1.md, paper/findings.md

- **(MAJOR, already self-corrected.)** `paper/draft_v1.md` (lines
  936–945) advertised a conditional Theorem 3 resting on **Conjecture
  L**, which `paper/review_v1.md` and the user's $K_4^*$ embedding
  refute on a 4-vertex, 3-arc-strong example. The team's own working
  notes (`team/31_*` lines 126–128) had already recorded the funnel
  obstruction. The publication-framed draft contradicted internal
  notes. `paper/findings.md` is now the authoritative state and
  correctly demotes Theorem 3. No remaining mathematical issue, but it
  is a process flag: a "what is the simplest counterexample to my
  load-bearing conjecture?" check should have caught this in 2 minutes
  rather than after multiple weeks of recoloring/termination work.
  This is exactly the procedural lesson noted in
  `~/.claude/.../feedback_conjecture_framing.md`.

- **(MAJOR, already self-corrected.)** `team/13_publishability_decision.md`
  / `team/14_route_b_ols_extraction.md` claimed a "Route B via the
  BJG–Yeo composition theorem in the round-decomposition setting for
  OLS digraphs," citing a Theorem RD that does not exist as published.
  `team/05_audit.md` Appendix A.6 found that the relevant statement is
  in fact Bang-Jensen–Gutin 1998 **Problem 6.8** — an open
  problem, not a theorem. This is the kind of fluent fabrication noted
  in `~/.claude/.../feedback_citation_verification.md`. The team
  correctly preserved OLS as a side notebook.

- **(MAJOR, already self-corrected.)** F3 ("cross-kind disjointness at
  $\lambda \ge 4$") was treated as a corollary of matroid union by an
  earlier Specialist pass; the audit `team/05_audit.md` A.13 found this
  conflates *cross-kind* packing (Thomassen's open conjecture,
  Bang-Jensen–Bessy–Havet–Yeo 2022, arXiv:2003.02107) with
  *same-direction* packing (Edmonds). Same-direction is in the toolkit;
  cross-kind is NP-complete already at $k = 1$. Correctly demoted in
  `paper/findings.md` §2.

- **(MINOR.)** `attack_plan.md` line 17: "A strong arc decomposition
  immediately yields arc-disjoint in/out branching pairs inside each
  color class with a chosen root." Correct under Edmonds, but worth
  noting it only yields pairs *along which the color class is itself
  $k$-arc-strong*. The plan correctly observes (line 17) that the
  converse is weaker; no fix needed.

- **(NIT.)** `paper/draft_v1.md` line 41's out-cut typo (`v \notin V
  \setminus X` rather than `v \in V \setminus X`) is flagged in
  `paper/review_v1.md` and is a cosmetic LaTeX glitch.

- **(NIT.)** `attack_plan.md` line 19 says "**The correct inference is:
  any positive theorem must use large arc-connectivity structurally."
  This is a heuristic, not a theorem. NP-completeness on 2-regular
  digraphs is consistent with both (i) a positive theorem at large $K$
  and (ii) a structural characterization at small $K$. Acceptable as
  intuition.

### 1.2 team/04_ec_log_proof.md (EC-log) — see §2 below for the line-by-line audit

The most important concrete defect I found in this entire project.

### 1.3 team/11_cl1_proof_v1.md (CL1)

- **(MINOR.)** The proof of R2 (and thus CL1) is **correct** as
  presented in §3 of `team/11_cl1_proof_v1.md`. The branching-stitch
  argument with independent inner-root choices `r_2^+, r_2^-` correctly
  handles the case where the bridges `e^+` and `e^-` do not share a
  common endpoint in $V_2$. The author flags and resolves the wrong
  Step 4 attempt openly, which is the right way to write a proof.

- **(MINOR.)** Lemma R2 in §3 does not actually require that
  $|V_i| \ge 2$ in any deep way — the proof only invokes existence of
  in/out arborescences inside each $D[V_i]$ rooted at chosen vertices,
  which requires $D[V_i]$ to be strongly connected as a hypothesis
  (1)-input. Hypothesis (1)'s "$D[V_i]$ admits a SAD" already implies
  strong connectivity, which in turn implies $|V_i| \ge 1$. The
  $|V_i| \ge 2$ stated in `team/11_cl1_proof_v1.md` line 117 is
  semantic — a single-vertex strong digraph admits a SAD vacuously
  (both color classes are the trivial digraph on one vertex), but it
  also means the bridge sets are the only arcs, and the partition
  hypothesis becomes vacuous. So the stated $|V_i| \ge 2$ is a clean
  hypothesis. Not a bug.

- **(MAJOR — needs external verification.)** The novelty argument in
  `team/11_cl1_proof_v1.md` §4.5 and `team/05_audit.md` A.5 turns on
  "no published bilateral analogue of BJ–Wang 2025 Lemma 2.4." The
  audit specifically lists BJ–Wang 2025 Lemma 2.4 (kernel-shell with
  the shell being an *independent set* in $V_1$, vertices absorbed via
  2-in + 2-out neighbors in $X$) and BJG–Yeo 2020 Lemma 2.3 (same
  shape, composition flavor) as the closest precedents, and says
  neither allows both parts to be SAD-decomposable. **I cannot verify
  this from artifacts alone.** Specifically:
  - The audit (`team/05_audit.md` line 1059) admits "BJ–Kriesell 2009
    survey, paywalled; no preprint; no relevant lemma found in
    secondary sources" — i.e. *not actually checked*. BJ–Kriesell 2009
    is a 5-page survey and may very well restate a bilateral form.
  - Hell–Hernández-Cruz 2017 is also "Paywall residue: unverified."
  - BJ–Yeo 2004 (Combinatorica 24) is paywalled and was audited only
    via its re-use in BJG–Yeo 2020 Lemma 4.1; the actual §3 of BJ–Yeo
    2004 may contain a more general statement.
  - The audit's logic that "CL1 is class-agnostic + bilateral, and no
    published version is both" is plausible but relies on the absence
    of a citation, not its presence.

  This is exactly the kind of load-bearing citation that the
  user's `feedback_citation_verification.md` warns about: confident
  "by Frank/BJG/Schrijver Theorem X.Y.Z" invocations *and their
  negations* ("no precedent exists") both deserve verbatim
  verification, ideally via Crossref / MathSciNet / the actual PDFs
  rather than abstract-only audits. **I recommend NOT submitting CL1
  as standalone novel until BJ–Yeo 2004 §3 has been read line-by-line.**

- **(MINOR.)** The "final form" of CL1 in §5.1 of
  `team/11_cl1_proof_v1.md` (drop hypotheses 2, 3-local-coverage, and
  4 of v1) is much cleaner than v1. Stripping hypothesis (4) is
  correct: once R2 gives strong-connectivity of both color classes,
  every directed cut is bichromatic automatically.

- **(NIT.)** `team/11_cl1_proof_v1.md` §5.1 line 524 writes "the
  bridge sets admit a partition $B^\pm = B^\pm_R \dot\cup B^\pm_B$
  with $B^+_R, B^+_B, B^-_R, B^-_B$ all non-empty" — this is a
  *necessary* condition for any SAD ($D$ must have $\ge 2$ bridges in
  each direction to admit a 2-coloring with non-empty pieces).
  Together with hypothesis (1), it's also sufficient. So CL1 is a
  *necessary-and-sufficient* lifting characterization with respect to
  the chosen bipartition $V_1 \dot\cup V_2$ — not just a sufficient
  condition. The §5.1 statement could be strengthened to a
  biconditional, which `team/11_cl1_proof_v1.md` §6.2 already
  identifies as a possible standalone publication angle.

### 1.4 code/ — ILP and SAT verifiers

- **(NO BUG FOUND, audited carefully.)** Both verifiers correctly
  encode "every directed cut $\delta^+(X)$, $\emptyset \ne X \subsetneq
  V$, meets both color classes." The ILP form (`code/verifier_ilp.py`
  lines 17–22) is the unambiguous mathematical definition. The SAT
  form (`code/verifier_sat.py` lines 6–28) uses arborescence
  witnesses: one out-arborescence + one in-arborescence in each color
  class, both rooted at a chosen root, with level monotonicity for
  acyclicity. These two are mathematically equivalent because $(V, A_c)$
  is strongly connected iff for any chosen root $r$, $A_c$ contains a
  spanning out-arborescence and a spanning in-arborescence rooted at
  $r$. Good.

- **(MINOR.)** `code/verifier_ilp.py` line 125 hard-fixes
  `x[e0] == 1` to break the $A_R \leftrightarrow A_B$ symmetry. This
  is fine for feasibility, but if `e0` is chosen by `min(arcs,
  key=lambda e: (repr(e[0]), repr(e[1]), e[2]))` and the same `e0`
  ends up being a "must be blue" arc in *some* SAD that exists (but
  not in any with `e0` red), then the symmetry break would falsely
  return UNSAT. **However**, since red/blue are symmetric in the
  problem definition, fixing one arc to red just halves the search
  space without losing solutions. Not a bug.

- **(MINOR.)** `code/verifier_ilp.py` lines 131–141 add vertex-singleton
  cut constraints upfront for every $v$. This is a valid strengthening
  (every singleton out-cut $\delta^+(\{v\})$ must be bichromatic if
  $|out(v)| \ge 2$). Good.

- **(MINOR.)** `code/verifier_sat.py` line 111: the root is hard-coded
  to $r = V[0]$ for both colors and both directions. The choice of
  root does not affect existence of a spanning arborescence in a
  strongly connected digraph. Good.

- **(NIT.)** `code/verifier_sat.py` line 145 docstring says "Root has
  level 0: level(r, 1) = 0." This should be "$\ell(r, 1) =$ FALSE,"
  i.e. the boolean variable encoding "level of $r \ge 1$" is forced
  to false. The code (lines 149–152) does this correctly.

- **(NO BUG FOUND.)** Cross-check (`code/cross_check.py` line 35)
  explicitly fails fatally on `SAT vs UNSAT` disagreement. Witness
  re-validation (`code/verifier_ilp.py:_validate_witness` line 59)
  recomputes strong connectivity of both color classes independently
  of the solver. This is a healthy verifier contract.

- **(NIT.)** `code/digraph.py:find_violated_cut` lines 200–215 has a
  long comment with a thinking-out-loud aside ("Wait — arcs from
  X = V\S go to S only via... none, since S is a sink..."). The
  final choice (source SCC) is correct: if `H` is not strongly
  connected, the condensation has at least two nodes; the source SCC
  $S$ has $\delta_H^-(S) = \emptyset$, so $X = V \setminus S$ has
  $\delta_H^+(X) = \emptyset$, which is a violated cut. Good. The
  thinking-out-loud should be trimmed for readability, but the logic
  is right.

### 1.5 The 4,613-instance negative search (Phase 3 v2)

See §3 below for the coverage analysis.

### 1.6 Known obstructions (S₄, semicomplete exceptions of BJGY 2020, split exceptions of AHLQW 2024)

- **($S_4$, OK.)** `code/benchmarks.py:_S4()` builds $C_4^2$ on
  vertices $\{0,1,2,3\}$ with arcs $(i, i+1)$ and $(i, i+2)$ mod 4.
  Verified UNSAT in `code/benchmarks.py:711` and `team/05_audit.md`
  lines 27–40. The citation Bang-Jensen & Yeo Combinatorica 24
  (2004) for "$S_4$ is the unique 2-arc-strong semicomplete digraph
  with no SAD" is the standard statement; the audit verifies it via
  Theorem 1.2 of BJ–Wang 2025. Correct.

- **(BJG–Yeo 2020 exceptions, OK with caveat.)** `_C3_K2_K2_K2`,
  `_C3_K2_K2_P2`, `_C3_K2_K2_K3` in `code/benchmarks.py` build the
  three non-$S_4$ exceptions. The convention for $\overline{K}_2,
  \overline{P}_2, \overline{K}_3$ inner digraphs and the layer
  numbering for $\vec{C}_3 = (1 \to 2 \to 3 \to 1)$ is fixed and
  consistent in the code; the `_compose_C3` helper at lines 121–147
  computes layer arcs correctly. The audit `team/05_audit.md` lines
  59 and 154 confirms the four-exception list matches Theorem 1.4 of
  arXiv:1903.12225. **Caveat**: $\overline{P}_2$ is defined in
  `code/benchmarks.py` line 117 as "the digraph on 2 vertices with
  the single arc from vertex 1 to vertex 2 (per Auditor's reading of
  BJG–Yeo 2020 Figure 2)." This is a *figure-based* attribution, and
  per
  `~/.claude/.../feedback_verifier_safety_net.md` figure-only arcs
  should be marked provisional. The benchmark verifies UNSAT, which
  is consistent with the citation, but the exact arc orientation is
  figure-derived rather than text-forced.

- **(AHLQW 2024 split exceptions, MIXED.)**
  - `_AiEtAl_Lemma211_smallest` (`code/benchmarks.py` lines 208–249)
    builds the smallest 2-arc-strong split digraph containing the
    Lemma 2.11 case-1 substructure. The audit `team/05_audit.md`
    Appendix A.1 contains a careful arc-by-arc derivation from the
    paper's text. Six arcs are text-forced from the Lemma 2.11
    statement, three more from semicompleteness of $V_2$, two more
    from 2-arc-strongness. This is rigorously transcribed.
  - `_AiEtAl_Lemma312_smallest` (`code/benchmarks.py` lines 257–306)
    builds the Lemma 3.12 case-1 substructure with $u^+ = v^+ = w$.
    The audit `team/05_audit.md` Appendix A.2 verifies. This is
    plausible. **Caveat:** the conclusion "$u^+ = v^+ = w$ gives the
    smallest instance" is the auditor's reading of the paper's
    statement, not the paper's explicit smallest example.
  - `_AiEtAl_B2_case_i/ii/iii` and the 10 `_AiEtAl_B3_*` cases
    (`code/benchmarks.py` lines 314–562) are built from the
    Appendix B.2/B.3 of arXiv:2408.02260, which is described in the
    paper via *figures* rather than verbatim arc lists. The audit
    `team/24_appendix_b3_figure_audit.md` explicitly notes that an
    earlier transcription with extra arcs `v_2 -> a` and `b -> v_3`
    produced SAT instead of UNSAT, and the corrected 14-arc core
    matches the paper's expected UNSAT. **The verifier UNSAT output
    is the only thing certifying these arc lists** — the figures are
    the actual source of truth, and the verifier was used to
    eliminate transcription errors. This is the right way to handle
    figure-based citations *if* the paper's UNSAT classification is
    independently believed. It is a less-than-ironclad chain compared
    to text-forced arcs.
  - `_AiEtAl_iv_star_iv` (`code/benchmarks.py` lines 577–621): the
    audit `team/05_audit.md` Appendix A.4 carefully cross-checks each
    arc against pages 30–34 of arXiv:2408.02260 with degree-counting
    arguments. The audit explicitly flags the structural-degree
    inferences (e.g. `v_2 -> a` "forced by $d^-(a) \ge 2$"). This is
    the strongest derivation in the benchmark set.

- **(SAT benchmarks, OK.)** $QR_7$ tournament, $K_5^*$ bidirected,
  and $C_5$-doubled are correctly constructed and the SAT
  expectations follow from BJ–Yeo 2004.

### 1.7 review.md (auditor's prior sign-off)

- **(MAJOR, in retrospect.)** The auditor's prior sign-off in
  `review.md` correctly identified the factor-of-2 bookkeeping in EC-log
  and the "alteration finish" wording. **But** the auditor did not
  catch the off-by-something constant gap at small $n$ in the EC-log
  proof (see §2 below) — the bookkeeping correction was made, but the
  numerical inequalities at small $n$ were not verified. This is a
  symptom of the same issue noted in
  `~/.claude/.../feedback_conjecture_framing.md`: audit passes verify
  framing and citations but not always the load-bearing arithmetic.

- **(OK.)** The auditor's verdict that WC3 is the right working
  conjecture and that the literature is now correctly separated
  (2-vertex-strong BJ–Wang 2025 split families vs. 2-arc-strong
  AHLQW 2024 split exceptions) is sound. This was the previous
  defect in v2 and the fix is correct.

- **(OK.)** The auditor's recommendation to do ILP-first, SAT-second
  is the right engineering order; the verifier code (where SAT
  imports `_validate_witness` from `verifier_ilp` and uses the same
  `_sanity_gate`) reflects this.

- **(OK.)** The auditor correctly flagged that the SAT solver should
  be treated as secondary, and the SAT encoding (arborescence
  witnesses, not reachability transitive closure) is exactly what the
  auditor recommended.

---

## 2. The EC-log proof, line-by-line

This section is the heart of the review. I worked through the proof
in `team/04_ec_log_proof.md` §2 step by step.

### 2.1 §2.1 (Reduction to undirected multigraph)

Steps 1, 2, 3 (lines 33–47) are correct.
- (1): Eulerianness $\Rightarrow |\delta^+(X)| = |\delta^-(X)|$ —
  standard, by summing degrees over $X$.
- (2): $d_G(X) = 2|\delta^+(X)|$ — correct because each arc of $D$
  contributes exactly one edge to $G$ regardless of orientation, and
  the orientation in/out splits the directed cut by Eulerianness.
- (3): $\lambda_G = 2\lambda(D)$ — correct.
- (4): the factor-of-2 between *ordered* directed cuts and *unordered*
  undirected cuts is correctly noted at line 45–47, and the proof
  carries the factor explicitly. This was the previous defect in v3
  that the auditor's `review.md` caught; the v4 proof handles it
  correctly.

### 2.2 §2.2 (Per-cut bound)

Line 51–52: $\Pr[\delta^+(X) \text{ monochromatic}] = 2 \cdot 2^{-s} = 2^{1-s}$. Correct: $s$ arcs are independently colored, and the
probability of all-red OR all-blue is $2^{1-s}$.

### 2.3 §2.3 (Karger's theorem)

Line 60: the statement of Karger's theorem says "the number of distinct
undirected cuts of size at most $\alpha \lambda_G$ is at most $n^{2\alpha}$."

This is *substantially correct* but the constant is slightly nonstandard.
Karger (JACM 2000, Corollary 2.4) actually states the bound as
$\binom{n}{2}^{2\alpha}$ for half-integer $\alpha \ge 1$, which for
integer $\alpha = j+1$ gives $\binom{n}{2}^{2(j+1)} \approx (n^2/2)^{2(j+1)}$,
*tighter* than $n^{2(j+1)}$.

But for the proof's union bound, **the looser form $n^{2\alpha}$ is fine**
and is the statement quoted in many textbook references. **No bug here.**

### 2.4 §2.4–§2.5 (Band decomposition + union bound)

The band $B_j = \{X : j\lambda \le |\delta^+(X)| < (j+1)\lambda\}$.
By the cut correspondence (4) and Karger applied with $\alpha = j+1$,
$|B_j| \le 2 n^{2(j+1)}$. Correct.

Probability bound (7): $\Pr[X \in B_j \text{ mono}] \le 2^{1 - j\lambda}$.
Correct (uses $|\delta^+(X)| \ge j\lambda$).

Union bound (8): $\mathbb{E}[N] \le \sum_{j \ge 1} 2 n^{2(j+1)} \cdot 2^{1-j\lambda}$.
Correct.

### 2.5 §2.5 geometric series and the constant gap (CRITICAL)

This is the only concrete error I found in the project.

Line 82–86 factor out the $j = 1$ exponent:

$$\mathbb{E}[N] \le 4 n^4 \cdot 2^{-\lambda} \cdot \sum_{j \ge 1} \left(\frac{n^2}{2^\lambda}\right)^{j-1}.$$

Correct (the constant 4 arises from $2 \cdot 2^1 = 4$ at $j = 1$, and
the ratio of consecutive terms is $n^2 / 2^\lambda$).

Line 85 then asserts: "If $\lambda \ge 3\log_2 n + 1$ ... the geometric
series sums to at most $4/3 < 2$, and $\mathbb{E}[N] \le 8 n^4 \cdot 2^{-\lambda}$."

The author replaces $4/3$ by $2$, getting $4 \cdot 2 = 8$ instead of the
tight $4 \cdot 4/3 = 16/3$. This is conservative wastage, **no bug**.

Line 88–89: "We need $\mathbb{E}[N] < 1$, i.e. $2^\lambda > 8 n^4 = 2^3 n^4$,
i.e. $\lambda > 4 \log_2 n + 3$."

Correct.

Line 91–94: "Both conditions ($\lambda \ge 3 \log_2 n + 1$ and $\lambda
> 4 \log_2 n + 3$) are implied, for $n \ge 2$, by $\lambda \ge 5 \log_2 n$, $n \ge 2$."

**This is where the proof breaks.** Concretely:

- $5 \log_2 n \ge 3 \log_2 n + 1$ ⟺ $2 \log_2 n \ge 1$ ⟺ $n \ge \sqrt{2}$. OK for $n \ge 2$.
- $5 \log_2 n > 4 \log_2 n + 3$ ⟺ $\log_2 n > 3$ ⟺ **$n \ge 9$** (since for integer $n$, $\log_2 n > 3$ requires $n > 8$).

So $C = 5$ alone does *not* give $\mathbb{E}[N] < 1$ for $n \in \{4, 5,
6, 7, 8\}$. Specifically:

| $n$ | Need: $\lambda \ge $ | $\lceil 5 \log_2 n \rceil$ | Sufficient? |
|---:|---:|---:|:---:|
| 4 | 12 | 10 | NO |
| 5 | 13 | 12 | NO |
| 6 | 13 | 13 | marginal (needs strict $>$, so NO) |
| 7 | 15 | 15 | marginal (NO; strict $>$) |
| 8 | 16 | 15 | NO |
| 9 | 17 | 16 | NO (table at line 130 says 17 needed via different rounding; double-check) |
| 10 | 17 | 17 | OK |

Wait — re-reading the author's table at lines 125–131, the column
"$C=5$: $\lceil 5 \log_2 n \rceil$" at $n = 10$ gives 17 and matches the
"smallest integer $\lambda$ such that $2^\lambda > 8 n^4$" column (also
17). The table is accurate. **The bug is in the author's text claim
at lines 91–94 that "$C = 5$ works for $n \ge 4$."** The correct
threshold from the same proof is more like $n \ge 9$ or $n \ge 10$
depending on whether one accepts the wastage factor $4/3 \to 2$.

The fix is one of:
1. **Increase $C$ to $C' = 6$** (line 21, footnote already records this
   as the "safe" choice), which the author already presents as an
   alternative. With $C' = 6$: need $6 \log_2 n > 4 \log_2 n + 3$ ⟺
   $\log_2 n > 3/2$ ⟺ $n \ge 3$. So $C' = 6$ works for $n \ge 3$.
2. **Tighten the wastage**: use the exact geometric sum $4/3$ to get
   $\mathbb{E}[N] \le (16/3) n^4 \cdot 2^{-\lambda}$. Then $2^\lambda > (16/3) n^4$
   gives $\lambda > 4 \log_2 n + \log_2 (16/3) \approx 4 \log_2 n + 2.42$.
   This still requires $\log_2 n > 2.42$, i.e. $n \ge 6$ — still
   short of the claimed $n \ge 4$.
3. **Add a direct small-$n$ check at $n \in \{4, 5, 6, 7, 8\}$**: the
   author does this for $n \in \{2, 3\}$ at lines 100, but the case
   $n = 4$ (which is precisely $S_4$ as a 4-vertex digraph with
   $\lambda(S_4) = 2$ — *and* $S_4$ is UNSAT) is *not* automatically
   trivial. The lemma's hypothesis at $n = 4$ requires $\lambda \ge
   10$, which forces $D$ to have at least $10$ arcs out of every
   non-trivial $X$; since $|A| \le 4 \cdot 3 = 12$ in any simple
   loop-free digraph and Eulerianness allows multi-arcs, the
   hypothesis at $n = 4$ implicitly demands an Eulerian multigraph
   with average out-degree $\ge 10$, which by Eulerianness means each
   vertex has out-degree $= $ in-degree $\ge 10$, so $|A| \ge 40$ on
   $n = 4$ vertices — perfectly possible as a multigraph.

**Severity: CRITICAL** for the stated constant; **MINOR** for the
theorem's truth, since $C' = 6$ (already in the same document) trivially
fixes it. **Action item**: rewrite §2.5–§2.6 with $C = 6$ as the headline
constant, or add explicit small-$n$ verification for $C = 5$.

### 2.6 §2.6 (First-moment conclusion) and §3 (constants)

Modulo §2.5 above, the conclusion is correct. The author's table at
lines 125–131 is accurate. The asymptotic claim "$C \to 4^+$ is the
limit of this argument" (line 119) is correct.

### 2.7 §4 (Where the argument fails to generalize)

(a) "drop Eulerianness", (b) "replace $\log n$ by a constant", (c)
"bounded-defect Eulerianness" — all three analyses are correct. (a)
correctly identifies that Karger no longer applies; (b) correctly
notes Karger's $n^{2\alpha}$ is asymptotically tight; (c) gives a
clean degradation analysis. **No issues.**

### 2.8 §5 (Sanity check)

Line 211: "$\mathbb{E}[N] \le \sum_j 2 \cdot 4^{2(j+1)} \cdot 2^{1-2j}$"
on doubled $\vec{C}_4$ ($n = 4$, $\lambda = 2$). At $j = 1$: $2 \cdot
4^4 \cdot 2^{-1} = 2 \cdot 256 \cdot 0.5 = 256$. Direct calculation in
the paragraph gives actual $\mathbb{E}[N] = 6.25$. Ratio $\approx 41$.
This is the bound's looseness at small $n$; useful to display, **OK**.

### 2.9 Summary on EC-log

- **Mathematical content**: correct theorem statement, correct proof
  strategy, correct asymptotic.
- **Stated constants**: the headline "$C = 5$, $n_0 = 2$" (line 17)
  is **wrong as written** at small $n$; the proof actually gives
  "$C = 5$ for $n \ge 10$" or "$C = 6$ for $n \ge 3$" or
  "$C = 6 \log_2 n$ unconditionally for $n \ge 2$". The author should
  pick one and rewrite the headline. The substantive theorem is
  unaffected; the publishable paper would just use $C' = 6$.

---

## 3. The 4,613-instance negative search — coverage analysis

`team/07_phase3_report_v2.md` reports 4,613 verified-3-arc-strong
digraphs across four generator vehicles, all SAT under both ILP and
SAT, all in agreement, zero disagreements. Let me audit what this
search actually covers.

### 3.1 Vehicle-by-vehicle coverage

**Vehicle 3 (deficit-aware gluing).** 2,884 verified instances, all
self-gluings or pairwise gluings of the 9 UNSAT templates ($S_4$,
$C_6^{(2)}$, $C_8^{(2)}$, three $C_3[\overline{K}_2 \cdot ]$
compositions, $L_{211}$, $L_{312}$, $iv*iv$). Interface sizes
$|S| \in \{3, 4, 5\}$, deficit-exact bridge multisets. **This is the
right kind of search** if WC3 fails at the "two 2-arc-strong
obstructions glued at a 3-arc interface" level. **But** it has three
substantive coverage gaps:

1. **Asymmetric template pairs are underrepresented.** The
   `verified_per_pair_cap = 100` at line 502 of
   `code/run_phase3_v2.py` caps each unordered pair at 100. This
   means an asymmetric pair like $S_4 + L_{211}$ contributes at most
   100 instances even though the asymmetric gluing space is much
   larger than the symmetric one. The per-pair cap is a diversity
   choice, not an exhaustive sweep.

2. **All 9 templates are at $\lambda = 2$.** The gluings produce
   $\lambda = 3$, but every "side" of the gluing is itself
   $\lambda = 2$. If a 3-arc-strong UNSAT exists *without* sitting
   on a 2-arc-strong UNSAT substructure, this vehicle cannot find it.

3. **$n \le 14$ only.** Self-gluing of $C_8^{(2)}$ at $|S| = 3$
   gives $n = 13$; the report's largest $n$ from Vehicle 3 is 14.
   This is the Lead's "soft warning zone" per the charter.

**Vehicle 2.A ($K_{6,6}$ balanced orientations).** 798 verified
instances, all at $n = 12$. **100% hit rate** for $\lambda = 3$ is
suspicious — let me check. A balanced 6-out-regular orientation of
$K_{6,6}$ on 12 vertices is automatically Eulerian. Vertex-transitivity
of $K_{6,6}$ + uniform random orientation gives $\lambda = 3$
generically because the bipartite structure means every singleton cut
has size exactly 3 (out-degree 3). **OK** — this is just observing
that the singleton cuts already certify $\lambda \le 3$, and the
random balance keeps $\lambda \ge 3$ in 100% of samples. But this
also means: **the only tight cuts are the singletons**. The Vehicle
2.A search is therefore probing a *very* narrow geometry — the
3-arc-strong $K_{6,6}$ orientations have *no tight non-singleton
3-cuts*, so the laminar-2SAT obstruction structure that motivates
Vehicle 1 cannot arise there at all. **This is a coverage limitation
that the report does not flag.** The 798 SAT outcomes are not strong
evidence for WC3 in the "laminar tight 3-cut" regime.

**Vehicle 2.B (perturbed circulants).** 164 verified instances at
$n \in \{10, 12, 14\}$. The perturbation is uniform-random arc
dropping from a 6-out-regular circulant, biased to land at $\lambda
= 3$. This breaks Cayley symmetry and *can* produce tight cuts on
non-singleton sets if the dropped arcs happen to concentrate on a
boundary. But 164 instances is small and the random perturbation is
not steered toward 2SAT-style cut configurations.

**Vehicle 2.C (perturbed bidirected).** 437 instances at $n \in \{8,
10, 12\}$. Similar caveats — random perturbation, not engineered.

**Vehicle 1 v2 (constraints-first laminar).** 330 instances. The
hand-designed shapes S1, S2, S3a, S3c are *explicitly intended* to
hit tight 3-cuts; the report (line 268) honestly admits "the most
aggressive shape, S3c, was specifically engineered as 'three nested
cuts with shared arcs' with the hope of forcing an UNSAT. It is SAT
under both backends. A genuine engineered NAE-3SAT UNSAT shape would
require either (a) more than 3 cuts sharing arcs in a richer pattern
than a laminar family supports natively, or (b) extra unit-clause
propagation from non-cut structure (forcing some arcs to fixed colors
before the NAE-3 applies)."

This is the **honest** finding: the laminar 2SAT obstruction
*conjecturally* sits outside the laminar family, in non-laminar /
overlapping cut systems. The report does not claim otherwise.

### 3.2 Aggregate coverage assessment

The search covers:
- gluings of all 9 known 2-arc-strong UNSAT templates;
- $K_{6,6}$ balanced orientations (singleton cuts only);
- 6-regular Cayley + random perturbations;
- hand-designed laminar tight-3-cut shapes (control + NAE-3 patterns).

The search does **not** cover:
- non-laminar (overlapping) tight-3-cut systems;
- gluings of *3-arc-strong* substructures (this is "Vehicle 6" in
  `team/10_phase4_vehicle6.md`, which is a separate Phase 4 report);
- Cayley digraphs on non-abelian groups (explicitly mentioned in
  attack_plan.md as Vehicle 7, deferred);
- semicomplete compositions $T[H_1, \dots, H_t]$ at $\lambda^{arc}
  = 3$ beyond the four BJG–Yeo 2020 exceptions (note: all
  3-arc-strong semicomplete compositions are SAT by BJG–Yeo 2020
  Theorem, so this is a non-issue);
- substitution / iterated gluings (Vehicle 5, also deferred to v3
  per the report's §5.1);
- canonical iso-classes — the count is "labeled-distinct" (sha256
  of sorted arc list, not `nauty` canon). True iso-classes are
  bounded above by the labeled count.

The report itself flags every one of these caveats in §4 ("What this
does not say"). I cannot find honesty failures in the negative
report. My only flag is that the rhetorical headline "4,613 instances
across four vehicles, zero UNSAT" reads stronger than the
geometrically narrow scope justifies. A bad 3-arc-strong digraph, if
it exists, plausibly does not look like any of the four chosen
families; the search is biased *toward* "small perturbations of
2-arc-strong obstructions" and *toward* singleton-cut-dominated
Eulerian regimes. A 2SAT-style obstruction over overlapping (non-
laminar) cuts is not in scope.

**Verdict on the negative search**: meaningful evidence of WC3's
*compatibility* with the searched families; **not** evidence of WC3's
truth.

---

## 4. What I cannot verify from artifacts alone

These are items where my conclusions are bounded by what is reachable
without external library access.

1. **BJ–Yeo 2004 §3 "good pair" lemma.** The novelty case for CL1
   turns on whether this lemma, in its actual 2004 form, allows two
   non-trivial SAD parts or restricts to "one semicomplete kernel +
   one shell." The audit `team/05_audit.md` lines 1055 admits it was
   not directly accessed (Combinatorica 24 is paywalled). I cannot
   verify CL1's "bilateral" novelty claim without reading BJ–Yeo 2004.

2. **BJ–Kriesell 2009 survey** (Electron. Notes Discrete Math. 34).
   Paywalled, 5 pages. Could contain a bilateral statement the audit
   missed.

3. **Hell–Hernández-Cruz 2017.** Audit flags "paywall residue:
   unverified." Could contain CL1-related material.

4. **Exact page numbers of Lemma 2.11 in arXiv:2408.02260.** The
   audit derives the smallest instance from the lemma's
   *substructure* description; the paper's own smallest realization
   may differ in one or two arcs depending on interpretation of "$|V_2|
   = 4$" boundary case. The verifier UNSAT verdict is the only
   end-to-end check.

5. **Whether $C_3[\overline{P}_2]$ uses the orientation "$1 \to 2$"
   or "$2 \to 1$" as $P_2$'s single arc.** The benchmark uses
   "1 → 2" per the auditor's reading of BJG–Yeo 2020 Figure 2. The
   verifier UNSAT under this choice is consistent with the citation;
   the alternative orientation would also be UNSAT by arc-reversal
   symmetry, so this is not load-bearing — but the figure-based
   provenance is worth keeping flagged.

6. **The auditor's accumulated "novelty verdict" (`team/05_audit.md`
   A.5.4 line 1063, "NOVEL with qualification").** This is the kind
   of assertion that should be confirmed by Crossref / MathSciNet
   keyword search for related theorems, not by abstract-only
   inspection of named precedents. I cannot reproduce that workflow
   from artifacts.

---

## 5. What I am confident about

1. The verifier (`code/verifier_ilp.py` + `code/verifier_sat.py` +
   `code/cross_check.py`) **correctly encodes** strong arc
   decomposition. Both backends compute the same thing
   mathematically; ILP via cut-separation, SAT via arborescence
   witnesses. Witness re-validation is independent of the solver.
   Sanity gates catch trivial UNSAT (not strongly connected, $\lambda
   < 2$). Cross-check fails fatally on disagreement. This is healthy
   software.

2. The EC-log proof's **mathematical content** (Eulerian reduction,
   factor-of-2 cut correspondence, Karger application, geometric
   series bound, first-moment conclusion) is correct. Only the
   stated constants at small $n$ are wrong; the substantive theorem
   "Eulerian digraphs with arc-connectivity $\Omega(\log n)$ admit
   SAD" is proved.

3. The CL1 proof in `team/11_cl1_proof_v1.md` is correct. The
   branching-stitch argument with independent inner-root choices is
   the clean way to handle two non-trivial SAD parts.

4. The 9 UNSAT benchmark instances ($S_4$, the three composition
   exceptions, $L_{211}$, $L_{312}$, three B.2 / ten B.3 / $iv*iv$)
   are correctly classified UNSAT by both backends, and the
   citations to Bang-Jensen & Yeo 2004, BJG–Yeo 2020, and AHLQW
   2024 are correctly attached.

5. The team's process of self-correction — Conjecture L refutation,
   OLS Route B retraction, F3 demotion, CL1 v1 → v2 simplification —
   is exactly the kind of audit-aware research one wants to see.
   The `paper/findings.md` document is the honest knowledge state
   and matches the working notes.

6. The Phase 3 v2 negative search is **honest** about its
   limitations: §4 of `team/07_phase3_report_v2.md` explicitly notes
   "labeled-distinct, not iso-canonical," "up to $n \le 14$," and
   "within the four implemented families." The report does *not*
   make the stronger claim "$f(3) = \infty$" or "WC3 verified
   empirically" — only "no $\lambda = 3$ UNSAT in the chosen
   families up to $n \le 14$."

7. The Bang-Jensen–Wang 2025 vs. Ai–He–Li–Qin–Wang 2024 split
   distinction (2-vertex-strong infinite family vs. 2-arc-strong
   complete characterization) is correctly maintained throughout the
   documents and the benchmarks.

---

## 6. Recommended actions in priority order

1. **(CRITICAL)** Rewrite the EC-log headline as $C = 6$ (or as
   $C = 5$ with the small-$n$ table verified for $n = 4, \dots, 9$
   by direct case analysis or by adding the $n \ge 10$ stipulation).
   See §2.5 above. Effort: 1 page.

2. **(MAJOR)** Get a copy of Bang-Jensen–Yeo 2004 (Combinatorica
   24) and verify or refute the bilateral-novelty claim for CL1
   against §3 of that paper. If §3's "good pair" lemma already has
   a bilateral form, CL1 is *not* novel and should be cited as
   such, not advertised as new. If it doesn't, CL1's novelty stands.

3. **(MAJOR)** Add `pynauty` to the dependency tree and replace the
   labeled-distinct hashes with iso-canonical hashes throughout the
   negative search. This is flagged in `team/07_phase3_report_v2.md`
   §5.1 and would materially strengthen the negative result.

4. **(MINOR)** Extend the Phase 3 negative search to non-laminar /
   overlapping tight-3-cut systems (the report's own §4 honestly
   says "a genuine engineered NAE-3SAT UNSAT shape would require
   either non-laminar cuts or color-forcing side conditions").
   Hand-designed UNSAT-aiming 2SAT geometries are the most
   information-rich next experiment.

5. **(MINOR)** Re-mark the figure-based benchmark arcs (Appendix
   B.2 / B.3 of arXiv:2408.02260; $\overline{P}_2$ orientation in
   BJG–Yeo 2020) as *figure-provenance*, not text-forced. This is
   the procedural rule from
   `~/.claude/.../feedback_verifier_safety_net.md`.

6. **(NIT)** Trim the thinking-out-loud comment in
   `code/digraph.py:find_violated_cut` (lines 200–215).

---

## 7. Final word

This is a serious research project that has done the rare-and-honest
thing of cataloguing its own retracted claims (Conjecture L, OLS
Theorem RD, F3) alongside its standing results. The two surviving
theorems are real. The single concrete defect I found (the EC-log
constant gap at small $n$) is a one-paragraph fix in the existing
write-up. The CL1 novelty case is genuinely unsettled until a paywall
crossing happens. The negative search is honest and limited; it should
not be promoted to anything stronger.

I would sign off on EC-log and CL1 as a publishable short note after
the §6.1 fix and the §6.2 BJ–Yeo 2004 read. I would not sign off on
any version of the manuscript that retains the Conjecture L material
or the OLS Route B as live claims; the project has already retracted
those, and the current `paper/findings.md` is the correct
authoritative document.

End of review.
