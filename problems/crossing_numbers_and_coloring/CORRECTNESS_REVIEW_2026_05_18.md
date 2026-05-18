# Correctness review (2026-05-18)

Independent referee-style audit of the deliverables in
`problems/crossing_numbers_and_coloring/`, focused on the four headline
"side-result" claims (D8 sharpness, D15 list-Albertson at $t \le 18$,
D16 expander Crossing Lemma, D4 Ore enumeration at $(26, 51)$) and the
supporting infrastructure (D2 literature audit, D3 FPS reconstruction,
D5 SymPy verification, D18 withdrawal, v4 plan & v3 review).

The review reads PDFs only where the `.tex` source disagrees with them
or where a specific computation must be checked; algebra was re-derived
by hand to catch silent assumption transfers.

---

## Executive verdict

- **D8 (`sharpness_9_8.tex`).** Mathematically correct. The headline
  witness identity
  $$
    f_{2b}(4/7,\delta) - 9/16 \;=\; 12(\delta-9/8)^2 / [7(4\delta - 1)]
  $$
  is verified line-by-line below and reproduces independently in SymPy
  (`deliverables/D5_sympy_freedelta/witness.log:1-30`). The main theorem
  "$F(\delta) \ge 9/16$ on $(1, 5/4)$, equality iff $\delta = 9/8$" is a
  correct *conditional* statement: it is the sharpness of $\delta = 9/8$
  *within the FPS three-case optimisation as currently formulated*. The
  scope is honestly stated in the abstract and §6 ("Implications"). I find
  no mathematical errors. Two issues are stylistic / framing rather than
  errors: see the dedicated D8 section.

- **D15 (`list_albertson_le_18.tex`).** Already withdrawn (banner at
  line 33), withdrawal is correct. The $t = 5$ counterexample (Voigt
  1993 + Thomassen 1994) is decisive and the proof gap the author
  identified (ACF / BT / Ackerman use sharper critical-graph edge
  bounds than just Dirac) is genuine. **CRITICAL FINDING:** the
  withdrawn paper *itself* contained the small-case argument that
  exposed the error — see lines 458–465, which explicitly invoke
  Thomassen's 5-choosability theorem but only conclude "contradicting
  $t \ge 6$", silently dropping $t = 5$. The "proof" of the main
  theorem therefore does not even cover $t = 5$ on its face; the
  withdrawal banner is necessary and the paper must not be
  resurrected without major repair (see D15 section).

- **D16 (`expander_crossing.tex`).** Mathematically correct after the
  four senior-referee fixes were applied. The headline inequality and
  its derivation through PST + Alon are reproduced cleanly. The
  Albertson corollary is honestly scoped: it does *not* address the
  Cranston residual triples; the paper says so explicitly. This is
  publishable as a packaging / explicit-constants note. No load-bearing
  hallucinations or misattributions found.

- **D2 (literature verification).** Correct. The six KY numbers
  reproduce by direct arithmetic from KY's published formula; the
  Cranston / FPS / BK thresholds are quoted verbatim with sources.
  One real ambiguity flagged honestly (the "+1 non-Ore" lemma is
  combined from KY Thm 3 + Thm 37 sharpness; not a single quotable
  theorem). No phantom citations.

- **D3 (FPS reconstruction).** Faithful, with two correctly-flagged
  unverified items (sign typo at FPS p. 10, dependence of $\alpha^*$
  on $\delta$). Section 8's "Things still to verify" list is candid
  and matches what I find when I do the verification myself. One
  potential weakness: D3 reverse-engineers FPS's choice of $\delta =
  9/8$ as a balancing argument between Case 1 and Case 2b at $\delta/2
  = 9/16$; D8 supersedes this with the correct *monotonicity-transition*
  explanation at $\delta = -3 + \sqrt{17}$. D3 should not be cited as
  the explanation of $\delta = 9/8$ — D8 should.

- **D4 (Ore enumeration at $(26, 51)$).** The 12-graph enumeration via
  the orbit count of $|A| \in \{1, \ldots, 12\}$ is well-justified.
  Per-graph data (edge count 649 matching KY's $F(51, 26)$; degree
  sequence; pynauty canonical certificate dedup) is consistent and
  reproducible. **MAJOR finding:** D4's own README at lines 226–232
  contradicts the v4 Ore-congruence finding by claiming "the same
  arithmetic applies at $k = 25, n = 48$" — this is *false*. The Ore
  composition $O(K_{25}, K_{25})$ has order $25 + 25 - 1 = 49$, not
  48. D4 should be edited to remove this paragraph or correctly note
  that $(25, 48)$ has *no* Ore graphs. See D4 section below.

- **D18 (combined paper).** Withdrawn correctly with a clear banner.
  The withdrawal note is precise about both failures (the $t = 5$
  counterexample and the proof's wrong-as-stated structural claim).
  The README still says "Ready for submission, pending author/journal
  decisions" — this is **stale and contradicted by the .tex banner**.
  See D18 / hygiene section.

- **tighter_fps_RETRACTED.** Correctly retracted with a clear banner.
  The retraction note identifies the exact silent assumption (FPS's
  $\eta$-monotonicity in Case 2b at *every* $\delta$). The historical
  preservation is useful as a calibration on the project's error mode.

- **`D5_sympy_freedelta/REPORT.md`.** **MINOR but real:** this report
  is the *pre-retraction* report and claims the false improvement
  $F^\star \approx 0.5574 < 9/16$ at $\delta_1 \approx 1.115$. It is
  still on disk with no withdrawal banner; only the
  `case2b_check.log` actually contradicts it. Anyone reading
  `REPORT.md` will be misled. See hygiene section.

Overall: D8 and D16 are publication-quality; the project's hygiene
around obsolete artifacts is uneven; D4 carries a minor false
statement about $(25, 48)$; D5/REPORT is dangerously stale.

---

## Findings by deliverable

### D8 — sharpness of $\delta = 9/8$  (file `deliverables/D8_paper/sharpness_9_8.tex`)

See the dedicated D8 section below for the line-by-line audit.

**Verdict: theorem-grade; no errors.**

### D15 — list-Albertson at $t \le 18$  (file `deliverables/D15_list_albertson_paper/list_albertson_le_18.tex`)

- **CRITICAL.** Theorem 1.3 (the headline; lines 170–173 of the .tex)
  is **false**, as documented in the withdrawal banner at lines 33–60.
  Voigt (1993) constructed a planar graph $G$ with $\chi_\ell(G) > 4$,
  i.e. $\chi_\ell(G) = 5$ (by Thomassen 1994, every planar graph is
  5-choosable), and $\operatorname{cr}(G) = 0 < 1 = \operatorname{cr}(K_5)$.
  This directly refutes Theorem 1.3 at $t = 5$.
- **CRITICAL (proof-structural, internal).** Even setting Voigt aside,
  the small-case argument at lines 452–465 *itself* fails to cover
  $t = 5$. The paper writes:
  > "[…] each is either planar (so $\operatorname{cr}(G) = 0$ which forces
  > $\chi_\ell(G) \le 5$ by Thomassen's theorem, contradicting $t \ge 6$),
  > or it contains $K_t$ as a subgraph […]"
  The parenthetical conclusion silently restricts to $t \ge 6$,
  leaving $t = 5$ uncovered. The Voigt counterexample slots into
  exactly the case-analysis hole the paper writes down on the page.
  This is a *self-inflicted* failure: the structural defect was
  visible in the small-case argument and not caught at draft time.
- **MAJOR (structural).** The withdrawal note (lines 38–58) is also
  correct that the larger ACF / BT / Ackerman chain does **not** in
  fact use $\chi \ge t$ only through $\delta \ge t-1$. Ackerman's
  Section 3.1 invokes the minimum edge-count function $f_r(n)$
  ("Stiebitz-style" bound), and the list-critical analogue
  (Krivelevich 1997) is provably weaker. So the "lifts for free"
  claim was structurally wrong, independent of the $t = 5$ failure.
- **MAJOR.** The D15 README still reads "Status: Draft, ready for
  internal review. […] no mathematical gap was identified" (lines
  88–97). This is **inconsistent with the .tex withdrawal banner**.
  The README should be updated to match.
- **NIT.** The conditional Theorem 4 (lines 583–589) is stated
  honestly as conditional on a list-edge-coloring analogue of FPS
  Lemma 2.3 at the same constant $9/16$, but this conditional
  statement *itself* survives the withdrawal of Theorem 1.3 only as
  far as the auxiliary list-edge-coloring conjecture is itself open.
  It should probably also be flagged in any future revisit; it is
  not currently used downstream so the impact is small.

**Verdict: correctly withdrawn; the README needs to be updated to
match the .tex withdrawal banner.**

### D16 — bisection-width Crossing Lemma for regular spectral expanders  (file `deliverables/D16_expander_crossing_paper/expander_crossing.tex`)

I re-derive Theorem 1.1, Lemma 3.1 (PST), and Corollary 3.3
(spectral bisection) independently and confirm:

- **Lemma 3.1 (PST conservative form).** Starting from
  Pach–Shahrokhi–Szegedy / Sýkora–Vrt'o
  $\operatorname{bw}(G) \le 6.32\sqrt{\operatorname{cr}(G)} + 1.58\sqrt{\sum_v \deg(v)^2}$,
  the identity $1.58 = 6.32/4$ is *exact*. Squaring then $(a + b)^2 \le 2a^2 + 2b^2$
  gives $\operatorname{bw}(G)^2 \le 2 \cdot 6.32^2 (\operatorname{cr}(G) + \tfrac1{16}\sum_v \deg(v)^2)$
  $= 79.8848(\operatorname{cr}(G) + \tfrac1{16}\sum_v \deg(v)^2)$. Dividing
  by $79.8848$ and rounding the leading denominator up to $80$ (which
  makes the bound *weaker*, preserving the inequality direction) gives
  the stated inequality. The proof at lines 299–325 of the .tex is correct.
  The earlier draft's bookkeeping error ("$5.00/79.9 \le 1/16$") has been
  fixed: $79.8848 / 16 = 4.9928 \le 5$, and the relevant step is now
  the exact algebraic identity $1.58 = 6.32 / 4$.
- **Corollary 3.3 (spectral bisection).** Applying the expander mixing
  lemma to $S = A$, $T = B$ in a balanced bipartition with $|A| + |B| = n$,
  $(1 - |A|/n)(1 - |B|/n) = (|A| \cdot |B|)/n^2$, so the EML bound
  collapses to $e(A, B) \ge (1 - \theta) d |A| |B| / n$. For $n$ even,
  $|A| = |B| = n/2$, so $\operatorname{bw} \ge (1 - \theta) d n / 4$;
  for $n$ odd, $|A| \cdot |B| = (n^2 - 1)/4$, so
  $\operatorname{bw} \ge (1 - \theta) d (n^2 - 1) / (4n) = (1 - \theta) d n (1 - 1/n^2) / 4$.
  This odd-$n$ correction is the second senior-referee fix and is now
  recorded both in the headline (line 137) and in the corollary
  statement (line 246). Correct.
- **Theorem 1.1 (main inequality).** Substituting Cor. 3.3 into
  Lem. 3.1 and using $\sum_v \deg(v)^2 = d_0^2 n$ for $d_0$-regular
  graphs gives
  $\operatorname{cr}(G) \ge (1 - \theta)^2 d_0^2 (\lfloor n/2 \rfloor \lceil n/2 \rceil)^2 / (80 n^2) - d_0^2 n / 16$.
  For $n$ even this is $(1 - \theta)^2 d_0^2 n^2 / 1280 - d_0^2 n / 16$.
  The headline statement is correct.
- **Numerical illustration at $d_0 = 14, n = 1000, \theta = 2\sqrt{13}/14$.**
  $(1 - \theta)^2 \approx 0.235$. The first bullet at line 388 says
  $\approx 23{,}750$; arithmetic gives $0.235 \cdot 14^2 \cdot 10^6 / 1280
  - 14^2 \cdot 1000 / 16 = 0.235 \cdot 153125 - 12250 = 35984 - 12250 = 23734$.
  Matches within rounding. The Bungener–Kaufmann comparison at $m/n = 7 \ge 6.95$
  is now valid (third senior-referee fix). Correct.
- **Albertson corollary (Corollary 5.1 / equation (10)).** Asks
  $(1 - \theta)^2 d_0^2 n^2 \ge 1280 Z(t) + 80 d_0^2 n$. The proof
  trivially substitutes the theorem inequality and Guy's upper bound
  $\operatorname{cr}(K_t) \le Z(t)$, so the conclusion $\operatorname{cr}(G) \ge \operatorname{cr}(K_t)$
  follows. Correct.
- **Ore-scope claim.** The corrected §6 (lines 541–584) explicitly
  identifies $(26, 51)$ as the only Ore residual triple and is
  consistent with the v4 plan's Ore-congruence observation. Correct.

**Hypothesis-conclusion alignment.** The paper does *not* claim to
close any open case of Albertson; the corollary is explicit that the
"first non-trivial case" is $t = 13$ and that even at $n \approx 30t$
the corollary only becomes non-vacuous under a Ramanujan-quality
expander hypothesis. The honest scope statement at lines 525–537 is
the operational result; downstream readers should not be misled.

**Novelty claim.** "We are not aware of an earlier Crossing-Lemma
inequality with explicit spectral dependence" (abstract; lines 161–166).
This is appropriately hedged. The PST and Alon ingredients are
genuinely classical; the only contribution is the packaging. The
paper says so. No overclaim.

**Verdict: publication-quality. No mathematical errors found in the
algebra, the numerical examples, the case split, or the scope
statements.**

### D2 — literature verification  (file `deliverables/D2_literature_verification.md`)

- **Cranston Theorem 2 triples.** Verbatim quote at lines 14–19;
  matches the .tex source of Cranston 2025. Correct.
- **KY edge-density formula.** $F(k, n) = ((k+1)(k-2)n - k(k-3))/(2(k-1))$.
  Reproduced the three Cranston residual computations:
  - $(25, 48)$: $26 \cdot 23 \cdot 48 - 25 \cdot 22 = 28704 - 550 = 28154$, $28154 / 48 = 586.541\overline{6}$, $\lceil \cdot \rceil = 587$, non-Ore $\ge 588$. ✓
  - $(26, 50)$: $27 \cdot 24 \cdot 50 - 26 \cdot 23 = 32400 - 598 = 31802$, $31802 / 50 = 636.04$, $\lceil \cdot \rceil = 637$, non-Ore $\ge 638$. ✓
  - $(26, 51)$: $27 \cdot 24 \cdot 51 - 26 \cdot 23 = 33048 - 598 = 32450$, $32450 / 50 = 649$ (integer), non-Ore $\ge 650$. ✓
  All six numbers reproduce exactly. The Ore-congruence consequence
  ($48 \equiv 0 \pmod{24}$, $50 \equiv 0 \pmod{25}$, $51 \equiv 1 \pmod{25}$)
  is restated at lines 53–57. Correct.
- **Ore-congruence proof.** Lines 67–74. Trivial induction on the
  composition tree; reproduced and correct. The statement that
  $\mathcal{O}_k$ admissible orders are $k, 2k-1, 3k-2, \ldots$ is
  the standard consequence.
- **BK threshold (6.77 vs 6.95).** Verbatim quotes from both BK
  abstract (line 89) and Cranston Theorem A(ii) (line 96). The
  discrepancy stands; D2 correctly leaves the verdict pending a BK
  PDF read. Honest.

**MINOR.** The "+1 non-Ore" lemma is correctly flagged as not a single
quotable theorem in KY (line 124–127); the team should cite the
appropriate follow-up KY paper (the JCTB paper "A new lower bound …")
before using $|E| \ge \text{KY} + 1$ as a load-bearing constraint in
any SAT model. This is exactly the kind of audit Marc's
`feedback_citation_verification.md` requires; here it is done.

**Verdict: clean, citation-grade.**

### D3 — FPS Claim 3.7 reconstruction  (file `deliverables/D3_R5a_reconstruction.md`)

- **Faithfulness.** Sections 3–6 walk FPS p. 9–10 line-by-line.
  Notation is preserved.
- **Case 1.** $\alpha = 0$ collapses $f$ to $\gamma$, the active
  constraint to $\gamma \le \delta(1-\beta)/(2-\beta)$, decreasing in $\beta$;
  maximum at $\beta = 0$, giving $\delta/2$. Correct.
- **Case 2a.** $\alpha^*(\eta, \delta) = (9 - 3/\eta)/8$ at $\delta = 9/8$;
  $f$ at $\alpha = \alpha^*$ equals $(3 + 1/\eta)/8$; maximum at
  $\eta = 5/7$ gives $11/20$. All correct.
- **Case 2b.** Reconstruction reaches the right value but **catches a
  sign typo in FPS p. 10**: FPS prints $(2 + 1/\eta)/(8 - 7\eta)$ but
  the algebraically correct form is $(2 - 1/\eta)/(8 - 7\eta)$.
  D3 §6 walks through both forms, computes the value at $\eta = 1/2$
  under each, and shows only the $(2 - 1/\eta)$ form gives $9/16$.
  Independent SymPy verification in `D5_sympy_freedelta/witness.py`
  confirms the $(2 - 1/\eta)$ form symbolically. The conclusion $9/16$
  is correct; FPS's printed display has a sign typo that should be
  reported to them.
- **MINOR (D3 §2 reverse-engineering of $\delta = 9/8$).** D3 §2
  asserts that FPS chose $\delta = 9/8$ "so that Case 1 and Case 2b
  both hit $\delta/2 = 9/16$" and explicitly flags this as a guess
  in §8.4. **The actual structural explanation is in D8**: $\delta = 9/8$
  is just inside the regime where the FPS monotonicity argument
  (their $\eta$-monotonicity proof for Case 2b) is valid, the
  threshold being $\delta_{\text{crit}} = -3 + \sqrt{17} \approx 1.12311$.
  D3 §2's reverse-engineering should be retracted in favour of the
  D8 explanation; D3's §8.4 "TODO" is now answered.
- **MINOR (D3 §7).** D3 §7 floats the speculation "lowering $\delta$
  from $9/8$ to $11/10$" would make Case 1 = Case 2b = Case 2a = $11/20$.
  This is **wrong** and is the seed of the retracted `tighter_fps_RETRACTED.tex`.
  D3 §7 itself is honest about the speculation status, and the
  follow-up is the D8 retraction-then-recovery. D3 §7 should be marked
  as a superseded speculation in any future revision.

**Verdict: faithful reconstruction; one FPS-side sign typo
correctly caught; two §-level speculations should be retracted in
favour of the D8 result.**

### D4 — 26-Ore graphs on 51 vertices  (file `deliverables/D4_ore_26_51/README.md`)

- **Construction.** The DHGO composition is described correctly
  (lines 24–50). The reading "identify $x$ with $A$ = $x$ gets $|A|$
  new neighbours, $A$'s vertices stay distinct" matches the count
  $n_1 + n_2 - 1$. The canary checks at $k = 4$ (Moser spindle) and
  $k = 5$ are independently verifiable.
- **Orbit count.** $|A| \in \{1, \ldots, 12\}$ under the $A \leftrightarrow B$
  symmetry $|A| \mapsto 25 - |A|$ (since $25$ is odd, no fixed point);
  12 orbits. pynauty canonical-form dedup confirms they are pairwise
  non-isomorphic. Per-graph data (edge count 649 = $F(51, 26)$,
  $\delta = 25$, $\Delta = \max(24 + a, 49 - a)$ matching the
  computed table) is internally consistent.
- **CRITICAL FINDING (D4 README, lines 222–232).** The README says:
  > "The same arithmetic applies at $k = 25, n = 48$: the partition
  > $|A| \sqcup |B|$ of the 24 neighbours of $z$ in $K_{25}$ gives
  > $|A| \in \{1, \ldots, 11\}$ distinct classes under the symmetry
  > $|A| \mapsto 24 - |A|$ (which has fixed point $|A| = 12$, so the
  > count is 12 classes total: 11 paired plus 1 fixed)."

  This is **false**. The Ore composition $O(K_{25}, K_{25})$ has order
  $25 + 25 - 1 = 49$, not 48. There is no $K_{25} * K_{25}$ output on
  48 vertices, and no $25$-Ore graph on 48 vertices at all (by the
  congruence $|V| \equiv 1 \pmod{24}$; $48 \equiv 0 \pmod{24}$). The
  D4 README contradicts the v4 plan and the senior review (v3 review,
  line 8: "The claimed $25$-Ore family at $(25, 48)$ cannot exist").
  D4 should be edited to retract this paragraph or to state correctly
  that the $25$-Ore family at $(25, 48)$ is **empty**.
- **MINOR.** The 26-criticality of all 12 outputs is asserted via KY
  Theorem 1 (criticality preservation under DHGO composition), with
  empirical canary support at $k = 4, 5$. This is correct as far as
  KY's preservation theorem goes, but the auditor should note that
  *brute verification* of 26-criticality at $n = 51$ is infeasible.
  The "audit-supplied" status of the 26-criticality claim is honest.

**Verdict: enumeration correct; one false paragraph about $(25, 48)$
needs to be removed or corrected.**

### D5 — SymPy verification  (directory `deliverables/D5_sympy_freedelta/`)

- **`witness.py` / `witness.log`.** Verifies $f_{2b}(4/7, \delta) - 9/16
  = 3(8\delta - 9)^2 / [112(4\delta - 1)]$, both as a literal SymPy
  factorisation (lines 7, 17–18 of `witness.log`) and via the
  reparametrisation $s = \alpha = 2 - 1/\eta$ at $s = 1/4$. The result
  is correct and reproduces my hand-derivation. The numerical scan
  (lines 31–45) confirms the witness value approaches $9/16$ from
  above as $\delta \to 9/8$.
- **`case2b_check.py` / `case2b_check.log`.** Verifies the derivative
  $\partial f_{2b} / \partial \eta |_{\eta = 1/2} = -(\delta^2 + 6\delta - 8)/\delta$
  factors with the single relevant root $\delta = -3 + \sqrt{17} \approx 1.12311$.
  The numerical scan at lines 16–38 of the log clearly shows the true
  $f_{2b}^{\max}(\delta_1) \approx 0.5654$ at $\delta_1 \approx 1.115$,
  *not* $\delta/2$ as the original `REPORT.md` claimed. This is the
  symbolic verification that produced the retraction of `tighter_fps`.
- **MAJOR (hygiene).** `REPORT.md` is the *pre-retraction* report and
  still asserts in its headline (lines 9–22):
  > "$F^\star \approx 0.5574 < 9/16$" "Re-tuning $\delta$ from $9/8$
  > to $\delta^* \approx 1.11491$ improves the constant from $9/16 =
  > 0.5625$ to $F^* \approx 0.557454$. The improvement is $\approx 0.9\%$."

  This is **factually wrong** (as the corrected `case2b_check.log`
  proves), and the file has no withdrawal banner. A reader who finds
  `REPORT.md` first and does not run `case2b_check.py` will leave with
  the false impression. The file should either be retracted with a
  banner or rewritten to match the D8 outcome.
- **MINOR.** `D6_prop34_check.md` is preserved as historical record;
  was load-bearing only for the now-retracted improvement claim. The
  pre-fix multiplicity-robustness analysis is still mathematically
  correct as written, but it is no longer used for anything; the
  README correctly flags this.

**Verdict: symbolic verification is sound; `REPORT.md` needs a
withdrawal banner because its headline contradicts the corrected
verification.**

### D17 — submission packets  (directory `deliverables/D17_submission_packets/`)

The README and `paper_D8.md`, `paper_D16.md` are consistent with the
two-paper ship plan (D8 + D16). `paper_D15.md` and `paper_D18.md` are
correctly marked withdrawn. The README correctly records the
trajectory.

**MINOR.** The bundling history (Option B → withdrawal → 2-paper)
is recorded in three places (`INTEGRATION.md`,
`D17/README.md`, `D17/bundling_recommendation.md`). They are consistent
but verbose; a single reader-facing summary in `D17/README.md` would
serve better. Not a correctness issue.

### D18 — combined paper  (directory `deliverables/D18_combined_observations/`)

- **`two_structural_observations.tex` (line 33)**: WITHDRAWN banner is
  correct and explicit about both failure modes (the $t = 5$
  counterexample and the structural defect in the lift argument).
- **`README.md` (line 81)**: still says
  > "**Ready for submission**, pending author/journal decisions in the
  > companion D17 submission packet directory."

  This is **stale and contradicts the .tex withdrawal banner**. The
  README should be updated to mark D18 as withdrawn.
- **Internal cross-references.** I scanned the active papers (D8,
  D16) and verified that no live citation chain points to D18 or D15
  as a positive result. D16 was rewritten with `\Cref{lem:list-dirac}`
  replaced by an in-paper lemma after the de-merge (`paper_D16.md`
  confirms). D8 cites neither D15 nor D18. Good.

**Verdict: withdrawal is complete and load-bearing references have
been cleaned, but D18 README needs a one-line withdrawal note for
consistency.**

---

## A dedicated section on D8

The headline "closed" theorem is the only paper in the bundle that is
*both* a positive result and being shipped. I therefore audit it in
detail.

### Statement (paper Theorem 1, lines 100–110)

> Let $F : (1, 5/4) \to \mathbb{R}$ denote the supremum of the
> Case 1, Case 2a, and Case 2b objectives of [FPS Claim 3.7] as a
> function of the degree threshold $\delta$. Then $F(\delta) \ge 9/16$
> for every $\delta \in (1, 5/4)$, with equality if and only if
> $\delta = 9/8$.

This is correctly scoped — it does **not** claim that $9/16$ is the
optimum constant for FPS Lemma 2.3 in any wider sense; it claims that
$\delta = 9/8$ is the unique optimum *within the existing three-case
optimisation*. The implications section makes this explicit.

### Proof of Theorem 1 (lines 393–415)

Three cases:

1. **$\delta \in [9/8, 5/4)$.** $f_1(\delta) = \delta/2 \ge 9/16$,
   with equality only at $\delta = 9/8$. Trivially correct.
2. **$\delta = 9/8$.** $F(9/8) = 9/16$ by FPS Claim 3.7. Cited
   correctly.
3. **$\delta \in (1, 9/8)$.** By Corollary 8, $f_{2b}^{\max}(\delta) >
   9/16$, hence $F(\delta) > 9/16$. Reduces to the witness identity
   in Lemma 7.

The interesting case is (3), which depends on the witness identity.

### Lemma 7 / Lemma 8 (witness identity, lines 309–391)

**The identity.**
$$f_{2b}(4/7, \delta) - 9/16 = 12 (\delta - 9/8)^2 / [7 (4\delta - 1)].$$

**Hand verification.**
At $\eta = 4/7$, $\alpha = \beta = 2 - 7/4 = 1/4$, so
$\gamma = (4/7)(1/4) + (3/7)\delta = 1/7 + 3\delta/7 = (1 + 3\delta)/7$
and $\delta - \gamma = \delta - (1 + 3\delta)/7 = (7\delta - 1 - 3\delta)/7
= (4\delta - 1)/7$. Substituting into
$f_{2b} = \gamma - \alpha(\delta - 1)/(\delta - \gamma)$:
$$f_{2b}(4/7, \delta) = (1 + 3\delta)/7 - (1/4)(\delta - 1) \cdot 7/(4\delta - 1)
= (1 + 3\delta)/7 - 7(\delta - 1)/[4(4\delta - 1)].$$
Bring to a common denominator $28(4\delta - 1)$:
$$= \frac{4(1 + 3\delta)(4\delta - 1) - 49(\delta - 1)}{28(4\delta - 1)}.$$
Numerator: $4(4\delta - 1 + 12\delta^2 - 3\delta) - 49\delta + 49
= 4(12\delta^2 + \delta - 1) - 49\delta + 49
= 48\delta^2 + 4\delta - 4 - 49\delta + 49
= 48\delta^2 - 45\delta + 45$.
So $f_{2b}(4/7, \delta) = (48\delta^2 - 45\delta + 45)/[28(4\delta - 1)]
= 3(16\delta^2 - 15\delta + 15)/[28(4\delta - 1)]$. ✓

Subtract $9/16$:
$$\frac{3(16\delta^2 - 15\delta + 15)}{28(4\delta - 1)} - \frac{9}{16}
= \frac{48(16\delta^2 - 15\delta + 15) - 9 \cdot 28(4\delta - 1)/4}{112(4\delta - 1)}
\cdot \frac{1}{1}.$$
Common denominator $112(4\delta - 1)$ requires multiplying the first
fraction's numerator by $4$ and the second by $7(4\delta - 1)$:
$$= \frac{4 \cdot 3(16\delta^2 - 15\delta + 15) - 9 \cdot 7(4\delta - 1)}{112(4\delta - 1)}
= \frac{192\delta^2 - 180\delta + 180 - 252\delta + 63}{112(4\delta - 1)}
= \frac{192\delta^2 - 432\delta + 243}{112(4\delta - 1)}.$$

Factor the numerator:
$192\delta^2 - 432\delta + 243 = 3(64\delta^2 - 144\delta + 81) = 3(8\delta - 9)^2$.
Hence
$$f_{2b}(4/7, \delta) - 9/16 = 3(8\delta - 9)^2 / [112(4\delta - 1)].$$
Convert: $(8\delta - 9)^2 = 64(\delta - 9/8)^2$, and $3 \cdot 64 / 112 = 192/112 = 12/7$,
so
$$f_{2b}(4/7, \delta) - 9/16 = 12(\delta - 9/8)^2 / [7(4\delta - 1)],$$
which is the .tex eq. (10). ✓

**The denominator $4\delta - 1$ is positive throughout $(1, 5/4) \subset (1/4, \infty)$;
the squared numerator is non-negative with equality iff $\delta = 9/8$.
Hence $f_{2b}(4/7, \delta) > 9/16$ for $\delta \in (1, 9/8) \cup (9/8, 5/4)$,
which together with $f_1(\delta) \ge 9/16$ on $[9/8, 5/4)$ gives the theorem.**

I verified each step by hand and confirm both the algebra and the sign
of the inequality. The SymPy script `witness.py` independently reproduces
the perfect-square factorisation; the `witness.log` printout at lines
3–7 matches verbatim.

### Range of validity of the witness  (Corollary 8, lines 351–391)

The witness $\eta = 4/7$ must lie in the Case 2b interval
$[1/2, \eta_b(\delta))$. The paper proves
$\eta_b(\delta) > 4/7 \iff \delta < (41 + 7\sqrt{37})/66 \approx 1.2663$.
Solving $\eta_b(\delta) = 4/7$:
$\sqrt{\delta(\delta-1)} - 1 = (4/7)(\delta - 2)$ (the $\delta - 2 < 0$
flip is handled in the paper at line 376), $7\sqrt{\delta(\delta-1)} = 4\delta - 1$,
squaring: $49\delta(\delta - 1) = 16\delta^2 - 8\delta + 1$,
$33\delta^2 - 41\delta - 1 = 0$, $\delta = (41 + 7\sqrt{37})/66$.
Numerically $\approx 1.2663$. Since $5/4 = 1.25 < 1.2663$, the witness
is valid throughout $(1, 5/4)$. Correct.

### Lemma 4 (monotonicity transition, lines 242–269)

$\partial f_{2b}/\partial \eta |_{\eta = 1/2} = -(\delta^2 + 6\delta - 8)/\delta$.
The proof is a textbook quotient-rule calculation; I reproduced it
mentally and the SymPy `case2b_check.log` at line 5 confirms
`-delta - 6 + 8/delta`, which is the same expression. The root
$\delta = -3 + \sqrt{17}$ is the positive root of $\delta^2 + 6\delta - 8 = 0$.
Correct.

This is what makes $\delta = 9/8 = 1.125$ structurally "just inside"
the regime where FPS's monotonicity-in-$\eta$ argument for Case 2b is
valid: $-3 + \sqrt{17} \approx 1.12311$, and $9/8 - 1.12311 < 0.002$.
This is a clean and surprising structural explanation for the FPS
choice. It supersedes the D3 §2 reverse-engineering "FPS chose $\delta = 9/8$
to balance Case 1 and Case 2b at $\delta/2$".

### Remark 11 (the cubic at $\delta_1$, lines 475–500)

The "naive" optimisation that takes $f_{2b}^{\max}(\delta) = \delta/2$
at *every* $\delta$ (which is true only at $\delta = 9/8$) gives the
equation $\delta/2 = f_{2a}^{\max}(\delta)$ after substituting
the closed form for $f_{2a}^{\max}$. Rationalising by squaring gives a
degree-5 polynomial in $\delta$ that factorises over $\mathbb{Q}$ as
$$-\tfrac{1}{4}(\delta - 1)(3\delta - 4)(\delta^3 + 3\delta^2 - \delta - 4).$$
The cubic factor is irreducible (no rational roots; discriminant $229 > 0$,
three real roots) with unique root in $(1, 5/4)$ at
$\delta_1 = -1 + (4/\sqrt 3) \cos((1/3)\arccos(3\sqrt 3 / 16)) \approx 1.114907$.

This **was** the proposed "improvement" in `tighter_fps_RETRACTED.tex`.
The remark now correctly notes that the assumption $f_{2b}^{\max} = \delta/2$
fails on $(1, -3 + \sqrt{17})$ — i.e. precisely the interval containing
$\delta_1$ — and that the cubic root $\delta_1$ is therefore not the
true optimum. The numerical $F(\delta_1) \approx 0.5654 > 9/16$ in the
table (line 449) confirms this directly. Correct retraction-handling
inside the paper.

### Numerical illustration table (lines 442–457)

Selected values cross-verified:

- $\delta = 9/8$: $f_1 = 0.5625$, $f_{2a}^{\max} = 11/20 = 0.55$,
  $f_{2b}(4/7) = 9/16 = 0.5625$ (since $\delta = 9/8$ makes the
  witness numerator zero), $f_{2b}^{\max} = 9/16$, $F = 9/16$. ✓
- $\delta = 1.10$: $f_1 = 0.55$, $f_{2a}^{\max} \approx 0.5713$,
  $f_{2b}(4/7) = 9/16 + 12(0.025)^2/[7(3.4)] = 0.5625 + 0.00007500/23.8
  = 0.5625 + 0.0003151 \approx 0.5628$. ✓
- $\delta = 9/8$, exact identity: numerator $(8 \cdot 9/8 - 9)^2 = 0$. ✓

All entries reproduce.

### Scope honesty (Implications, §6, lines 502–544)

The implications section is appropriately scoped:
- Lemma 2.3's constant $9/16$ cannot be improved by re-tuning $\delta$
  in the existing FPS three-case optimisation;
- Any improvement requires changing something else: replace
  Vizing–Gupta with Goldberg–Seymour / Kahn, sharpen the multiplicity
  bound, or modify the semi-random construction.
This is the right framing. It does **not** claim a closure of any
Albertson case, nor does it claim that $9/16$ is unimprovable in
absolute terms — both claims would be false.

### Stylistic / framing issues (NIT)

- **NIT.** Lemma 4 (monotonicity transition) is described in the
  abstract (line 54) as one of "two structural reasons" underlying
  sharpness. In the proof of Theorem 1, however, Lemma 4 is *not*
  used: the proof goes via the witness identity (Lemma 7), which is
  self-contained and does not depend on monotonicity. Lemma 4 is
  expository, not load-bearing. The abstract should make this
  hierarchy clearer; otherwise a reader may worry that the proof
  depends on the monotonicity, which transitions at a value
  ($-3 + \sqrt{17} \approx 1.12311$) that is awkwardly close to but
  not exactly $9/8 = 1.125$.
- **NIT.** The acknowledgments (lines 546–558) thank an unnamed
  "referee-style audit" and Marc's `feedback_citation_verification.md`
  is implicitly in the background; this is appropriate for an
  internal draft but should be edited or generalised before submission.

**D8 verdict: theorem-grade. The witness identity is correct, the
case split is honest, the scope is honestly stated, and the
historical record (the retracted draft, the cubic remnant) is
acknowledged inside the paper rather than being papered over.**

---

## A dedicated section on D15 and D16 publication-readiness

### D15

**Not publishable in any form**. The main theorem is provably false at
$t = 5$. The withdrawal is the correct action. The structural defect
(claim that the ACF/BT/Ackerman chain uses $\chi \ge t$ only through
$\delta \ge t - 1$, when in fact Ackerman's f_r(n) is used) is the
deeper problem — even repairing the $t = 5$ small-case argument would
not save the paper, because Ackerman's input is a tighter
critical-graph edge bound than the list-critical analogue (Krivelevich)
provides.

The withdrawal mechanism (banner in .tex; PDF rebuilt with banner)
is correct. **The README is stale** (still says "Draft, ready for
internal review; no mathematical gap was identified") and should be
edited to be consistent with the banner. Otherwise, future readers
who hit the README first will misread the status.

**A salvage path** would be: state and prove a *weaker* list version
of Albertson with the constants known to lift (e.g. via the list
Dirac bound alone, perhaps to a smaller $t$ threshold than 18). Any
such salvage requires a fresh proof, not a "list-coloring lift" of
the ACF/BT/Ackerman chain.

### D16

**Publishable as a graph-theory note**. The two ingredients (PST
inequality, EML / Alon spectral bisection) are classical; the
contribution is the explicit packaging of the spectral parameter
$\theta$ inside the Crossing-Lemma constant. The novelty claim is
appropriately hedged ("we are not aware of an earlier such
inequality"). The Albertson corollary is honest about its scope: it
does **not** close any Cranston residual case; it does become
non-vacuous in a moderately-dense Ramanujan regime ($n \gtrsim 20 t$,
or $n \gtrsim 10 t$ with the sharper PST $1/40$ constant).

All four senior-referee fixes are visible in the .tex:
1. Odd-$n$ floor in the spectral bisection bound: now stated at line 246.
2. PST bookkeeping: now derived inline at lines 299–325, exact ratio
   $1.58 = 6.32/4$ used, no false rounding step. ✓
3. Numerical illustration at $d_0 = 14, n = 1000, \theta = 2\sqrt{13}/14$
   (so $m / n = 7 \ge 6.95$, BK threshold met): now used at lines 386–412. ✓
4. Ore-scope claim: §6 correctly limits Ore candidates to $(26, 51)$. ✓

I would recommend the following minor edits before submission:
- Change the second-eigenvalue notation from $\lambda_2(G)$ to
  $\lambda(G) := \max(|\lambda_2|, |\lambda_n|)$ throughout (this is
  the convention in HLW and elsewhere; the paper uses both at lines
  220–225 inconsistently).
- The "Density threshold" paragraph at lines 424–435 derives the
  threshold $n > 80/(1 - \theta)^2$ for the inequality to be
  non-vacuous; this should be cross-referenced to Corollary 5.1 so
  readers know which regime the corollary actually lives in.
- The $\theta$-bound in Corollary 5.1's hypothesis (b) is implicit
  in eq. (10); writing it explicitly as a closed-form
  $\theta \le 1 - \sqrt{80 t^2 / n^2 + 80 / n}$ (as already done in
  the "Simplified asymptotic form" paragraph) would help reviewers.

**No mathematical errors found**.

---

## What I cannot verify from artifacts alone

- **Cranston Theorem 2 itself.** I quoted the .tex's verbatim
  rendering of Cranston's Theorem 2 (D2 lines 14–19) but did not
  fetch and re-read the arXiv:2512.08020 PDF. The team's D2 .md says
  the text is verbatim from p. 1 of the PDF.
- **Bungener–Kaufmann threshold (6.77 vs 6.95).** The discrepancy
  between the BK abstract and Cranston's invocation is honestly
  flagged in D2 (lines 87–119) and in the v4 plan. The team has
  *not* read the BK PDF in full; resolving 6.77 vs 6.95 requires
  reading BK §4. Until then, both numbers should be qualified as
  the team has been doing.
- **FPS Claim 3.7 in the SoCG-2025 published version.** The team
  works from arXiv:2510.05893v1. The displayed sign typo in FPS p. 10
  ($(2 + 1/\eta)$ vs. $(2 - 1/\eta)$) may or may not have been
  corrected in the SoCG version. I cannot verify this from the local
  artifacts.
- **The "+1 non-Ore" KY lemma.** Cited in D2 as combining KY Theorem
  3 + Theorem 37 sharpness, with a follow-up KY paper providing the
  clean lemma form. The team has not fetched that follow-up; if
  $|E| \ge \text{KY} + 1$ becomes a load-bearing SAT constraint, the
  follow-up must be cited.
- **The 26-criticality of the 12 graphs in D4.** Direct brute-force
  verification is infeasible at $n = 51$. The team relies on KY's
  preservation theorem (and the $|E| = 649 = F(51, 26)$ extremality
  is consistent with this).
- **Krivelevich 1997 list-critical edge bound vs. the chain we'd
  need for list-Albertson.** The withdrawal note correctly identifies
  Krivelevich as the source of the weaker list-critical edge floor,
  but the exact comparison "Krivelevich vs. Ackerman's $f_r(n)$" was
  not done by me.

---

## What I am confident about

- **D8's main theorem and witness identity are correct.** The
  algebra reproduces by hand and in SymPy. The case split,
  scope, and historical handling of the retracted draft are
  all honest.
- **D16's main theorem and Albertson corollary are correct.** The
  PST + Alon + EML packaging is sound; all four senior-referee
  fixes are visible in the .tex; the scope claim ("does not close
  Cranston residual") is correctly recorded both in the body of the
  paper and in the README.
- **D15 is correctly withdrawn.** The $t = 5$ Voigt counterexample
  is decisive; the proof's structural defect is genuine and is
  visible in its own small-case argument.
- **D18 is correctly withdrawn.** The .tex banner is precise; load-
  bearing citations from active papers have been cleaned.
- **D4's 12-graph enumeration at $(26, 51)$ is correct**, except
  for the false paragraph claiming the same arithmetic applies at
  $(25, 48)$.
- **D2's KY arithmetic is correct.** Reproduced all six numbers
  $587, 588, 637, 638, 649, 650$ by hand.
- **The v4 plan's main correction** (delete the false $25$-Ore
  path; congruence excludes $(25, 48)$ and $(26, 50)$) is sound and
  is now consistent across the plan, the v3 review, D2, and the
  active papers. The only remaining inconsistency is the D4 README
  paragraph above.
- **The project's error-recovery mechanism works.** The
  `tighter_fps_RETRACTED` retraction, the D15/D18 withdrawal, and
  the D16 fix-cycle all follow a consistent pattern: identify the
  error precisely, preserve the historical artifact with a banner,
  and update downstream references. This is good scientific
  hygiene. The remaining hygiene gaps are localised and named in
  this review.

---

## Action items (recommended, in priority order)

1. **CRITICAL.** Edit `deliverables/D4_ore_26_51/README.md` lines
   222–232 to retract the false claim about $(25, 48)$ supporting
   $25$-Ore graphs. The correct statement is: "$48 \not\equiv 1
   \pmod{24}$, so the $25$-Ore family at $n = 48$ is empty (no
   $K_{25} * K_{25}$ on 48 vertices; the composition gives $n = 49$)."
2. **MAJOR.** Add a withdrawal banner to
   `deliverables/D5_sympy_freedelta/REPORT.md` directing readers to
   D8 / `case2b_check.log` for the corrected analysis. Current state:
   the file's headline claims $F^\star \approx 0.5574 < 9/16$, which
   is the (now-retracted) claim that motivated `tighter_fps_RETRACTED`.
3. **MAJOR.** Edit `deliverables/D15_list_albertson_paper/README.md`
   to state the paper is withdrawn (currently still says "Draft,
   ready for internal review"). Similarly
   `deliverables/D18_combined_observations/README.md` (line 81 still
   says "Ready for submission").
4. **MINOR.** In `deliverables/D3_R5a_reconstruction.md`, retract
   §7's speculation about $\delta = 11/10$ and §2's reverse-engineering
   of the FPS choice of $\delta = 9/8$, in favour of the D8 result
   (the actual structural explanation is the monotonicity transition
   at $\delta = -3 + \sqrt{17}$).
5. **NIT.** Email the FPS team about the sign typo in their p. 10
   Case 2b objective ($(2 + 1/\eta)/(8 - 7\eta) \to (2 - 1/\eta)/(8 - 7\eta)$).
   The conclusion $9/16$ is unaffected but the display is wrong.
6. **NIT.** In D16, unify the notation $\lambda_2(G) := \max(|\lambda_2|, |\lambda_n|)$
   throughout, and write the $\theta$-bound in Corollary 5.1 explicitly
   in closed form for ease of refereeing.
