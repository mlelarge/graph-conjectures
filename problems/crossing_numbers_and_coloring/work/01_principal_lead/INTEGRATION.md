# INTEGRATION — Albertson team working document

Principal Investigator (Role 1). Anchored to `docs/plan.md` **v4** (2026-05-16)
and the senior post-team audit at `docs/review_v3.md`. This document is the
contract between the nine sub-teams. Anything contradicting v4 is wrong here,
not in v4; do not edit `plan.md`.

**v4 changes that altered this document (2026-05-16 sync):**

- Track A reframed from "close $t = 25$" to **subfamily certification + counterexample hunt** (per PI directive after Roles 3/4/5/6 compute-team consensus).
- Track B now has an explicit **headline**: **R5a — re-derive FPS Claim 3.7 with Case 2b isolated** (per `review_v3.md`).
- The Cranston residual order $(25, 48)$ has **no Ore counterexample candidate** (Ore-order congruence $|V| \equiv 1 \pmod{k-1}$); $(26, 50)$ likewise; $(26, 51)$ is the **only Ore corner**.
- **Non-Ore Kostochka–Yancey edge floors** ($|E| \ge 588 / 638 / 650$ at the three orders) are now **mandatory R1a SAT/CEGAR constraints**, not optional refinements.
- **Role 9 is no longer on the positive-proof critical path.** Finite $\underline L(t)$ matters only for falsification (per `review_v3.md` and Role 9's own memo). Role 9 is demoted to literature audit + falsification support.

**R5a closeout (2026-05-16 — outcome (ii), theorem-grade).**

- **R5a as "tune $\delta$ inside FPS Claim 3.7 to beat $9/16$": CLOSED.** The $\delta = 9/8$ choice is sharp.
- **Outcome:** $c = 9/16$ is binding within the FPS Vizing–Gupta + semi-random framework. **Proven**, not "appears to be".
- **Artifact:** `deliverables/D8_paper/sharpness_9_8.pdf` (7 pages, zero warnings, theorem-grade). Witness identity $f_{2b}(4/7, \delta) - 9/16 = 12(\delta - 9/8)^2/[7(4\delta - 1)]$ gives a two-line analytic proof. The earlier draft `tighter_fps_RETRACTED.pdf` is preserved with retraction banner.
- **Trajectory:** intermediate draft `tighter_fps.tex` (improvement claim, $\delta_1 \approx 1.115$) → retraction after senior referee fix #3 surfaced the unproven Case 2b monotonicity assumption → corrected check (`case2b_check.py`) confirmed $\delta_1$ is *worse* than $9/8$ → obstruction note `sharpness_9_8.tex` v1 (analytic gap in proof, EC only) → witness $\eta = 4/7$ closes the gap analytically → current theorem-grade note.
- **Track B alternatives still open:** R2c (min-degree-aware Crossing Lemma), R3.6 (fractional/list/DP Albertson). Both are now the front-runners for a positive Track B 12-month result; R5a's three §7 routes (Goldberg–Seymour, sharper $\mu$, modified construction) are the only paths back to attacking $9/16$ directly.

---

## Status addendum (2026-05-17)

The Mission Statement and per-track milestones in §1 and §4 below predate
the R5a closeout above and the textual fixes to D8 of 2026-05-17.
**Where they conflict, this addendum supersedes them.** The body of the
document is left intact for traceability — do not re-read §1 / §4 in
isolation for the project's current state.

- **R5a is CLOSED.** The "Track B headline = R5a" language in
  §1 outcome (c) is **stale**. R5a is no longer pursued at all; the
  obstruction (sharpness of $9/16$ within FPS Claim 3.7) is now a
  theorem-grade artifact at `deliverables/D8_paper/sharpness_9_8.pdf`.
- **New Track B front-runners** (in priority order):
  - **R2c.** A min-degree-refined Crossing Lemma. The concrete target
    is a theorem of the form
    \[
       cr(G) \ge C(d_0, m, n) \cdot \frac{m^3}{n^2}
       \quad\text{for } G \text{ with } \delta(G) \ge d_0,
    \]
    where $C(d_0, m, n)$ improves the BK / Cranston chain in the
    critical-graph density regime. **First deliverable:** a 5-page
    attack memo (Role 8) with one explicit theorem candidate and a
    written record of where each natural proof attempt loses the
    min-degree information. **Owner:** Role 8.
  - **R3.6.** Fractional / list / DP-chromatic Albertson. **Owner:** Role 2.
- **Track A is NARROWED.** The wording in §1 outcome (d) and §4 Track A
  permits "one named non-Ore subfamily" as a flexible target; that
  generality is now further restricted to:
  - **A1 (immediate):** Certify the $(26, 51)$ Ore corner. The 12 graphs
    from `deliverables/D4_ore_26_51/` are the input; the goal is
    $cr(G) \ge Z(26) = 5148$ with certificates on all 12, giving a
    finite "no Ore counterexample at $(26, 51)$" result.
    **Deliverable:** D12, `deliverables/D12_ore_c3/`.
  - **A2 (conditional on A1 outcome):** one explicit non-Ore subfamily
    named by Role 2, at $(25, 48)$ or $(26, 50)$.
- **Parked, do NOT pursue.** Per PI directive 2026-05-17:
  unrestricted enumeration / SAT for $(25, 48)$ or $(26, 50)$;
  finite $\underline{L}(25)$ lower bounds (unless project pivots to
  falsification); any attempt to rescue the retracted FPS-improvement
  draft.

**End-of-day update (2026-05-17, second revision): two-paper bundle locked after D18 retraction.**

The morning's Option B bundling (D8 + combined D15+D16 as D18) was
**partly retracted** in the afternoon: a senior referee pass found
D15's main theorem (list-Albertson at $t \le 18$) is **provably false
at $t = 5$** — Voigt's planar non-4-choosable graph has $\chi_\ell = 5$
and $\operatorname{cr} = 0 < 1 = \operatorname{cr}(K_5)$. The structural
cause is that the ACF/BT/Ackerman chain does \emph{not} use the
chromatic-number hypothesis only through Dirac's $\delta \ge t - 1$;
Ackerman~(arXiv:1509.01932) §3.1 uses minimum-edge-count machinery
$f_r(n)$ for $r$-critical graphs, and the list-critical analogue
(Krivelevich 1997) is strictly weaker. The "lifts for free" claim was
unjustified even apart from the $t = 5$ counterexample.

D15 and D18 are withdrawn with explanatory banners (PDFs preserved
with retraction notices for historical record). D16's spectral
content survived the audit cleanly; four fixable errors were
identified and patched (odd-$n$ floor in the spectral bisection bound,
PST proof bookkeeping rounding step, BK-threshold-compliant numerical
illustration, corrected Ore-scope claim). D16 is reinstated as Paper 2.

**Final shipping plan (2 papers):**

- **D8** — R5a sharpness theorem, 7 pp, stand-alone → *Discrete Math* Note.
- **D16** — *A bisection-width Crossing Lemma for regular spectral expanders, with an Albertson corollary*, 10 pp, stand-alone → *Journal of Graph Theory*.

The standalone D15 source remains at
`deliverables/D15_list_albertson_paper/` (with WITHDRAWN banner;
**do not submit**). The D18 combined source remains at
`deliverables/D18_combined_observations/` (with WITHDRAWN banner;
**do not submit**). See Decision 2026-05-17-5 below.

The Cranston residual at $t \in \{25, 26\}$ remains open and outside
the team's accessible toolkit; D12's certified bound is $3825 < Z(26)
= 5148$ and the gap of $1323$ is not closable by R2c or R3.6. The
project's realistic mathematical contribution is the two-paper bundle,
not a closure of Albertson.

### Decision 2026-05-17-1

- Owner: Role 1
- Type: re-scope + go on A1 + go on R2c memo
- Subject: Project pivot after R5a closeout.
- Inputs: `deliverables/D8_paper/sharpness_9_8.pdf` (theorem); senior
  referee directive 2026-05-17.
- Decision: (1) R5a as a research route is permanently closed.
  (2) Front-runners for Track B are R2c (primary) and R3.6 (secondary).
  (3) Track A immediate target is the 12-graph Ore corner certification
  (D12). (4) Track A may add one named non-Ore subfamily at
  $(25, 48)$ or $(26, 50)$, contingent on Role 2 producing the spec
  and Role 1 approving the scope. (5) The parked items above remain
  parked.
- Credit grade attached: N/A
- Next checkpoint: 2026-06-17 (1-month: R2c memo + D12 outcome).
- Dissenters: none recorded.

### Decision 2026-05-17-5 (D15/D18 withdrawal + D16 reinstatement)

- Owner: Role 1
- Type: partial retraction + reinstatement
- Subject: Withdraw D15 and D18 (false main theorem at $t = 5$); reinstate D16 as Paper 2 with four senior-referee fixes.
- Inputs:
  - Senior referee verdict identifying Voigt's planar non-4-choosable graph as a $t = 5$ counterexample to the D15/D18 main theorem.
  - Acknowledgement that Ackerman §3.1 uses $f_r(n)$ critical-graph edge floors, not merely Dirac, so the list-lift also fails structurally beyond the explicit counterexample.
  - Four specific D16 errors flagged: (i) odd-$n$ floor in `cor:bw-spec` (proof gave $(1 - 1/n^2)$ weakening, not stated); (ii) `lem:PST` proof bookkeeping step "$5.00/79.9 \le 1/16$" is false ($0.0626 > 0.0625$); (iii) numerical illustration at $(d_0, n) = (10, *)$ has $m/n = 5$, below the BK $6.95n$ threshold, so the BK comparison is invalid; (iv) §5 claim that the residual triples are "populated by Ore compositions of $K_{26}$" is wrong — by congruence $|V| \equiv 1 \pmod{k-1}$, only $(26, 51)$ admits Ore candidates.
- Decision:
  - **D15 withdrawn.** WITHDRAWN banner added to `deliverables/D15_list_albertson_paper/list_albertson_le_18.tex`; PDF recompiled (10 pp including banner). Preserved for historical record.
  - **D18 withdrawn.** WITHDRAWN banner added to `deliverables/D18_combined_observations/two_structural_observations.tex`; PDF recompiled (16 pp including banner). Preserved for historical record.
  - **D16 reinstated as Paper 2** with all four fixes applied:
    - `cor:bw-spec` restated with $\lfloor n/2 \rfloor \lceil n/2 \rceil / n$ form; even-$n$ simplification and odd-$n$ $(1 - 1/n^2)$-factor displayed explicitly.
    - `lem:PST` proof now uses the exact identity $1.58 = 6.32/4$ so the $1/16$ second-term factor is exact (not approximate rounding).
    - Numerical illustration moved to $d_0 = 14$ (Ramanujan, $m/n = 7 > 6.95$), valid for BK comparison.
    - §5 Cranston-residual discussion corrected: only $(26, 51)$ admits Ore candidates; $(25, 48)$ and $(26, 50)$ excluded by congruence.
  - D16 main theorem updated to display the $\lfloor n/2 \rfloor \lceil n/2 \rceil / n$ form in the headline, with even-$n$ clean form and odd-$n$ $(1 - 1/n^2)^2$ weakening explicit. Recompiled (10 pp, zero errors, zero overfull boxes).
- Per-paper grades: D8 = **T**, D16 = **T** (both compile cleanly post-fix).
- Final shipping plan: **2 papers (D8 + D16), both stand-alone**.
- Next checkpoint: 2026-06-17 — two submissions pending Marc's author-list and journal-target decisions.
- Dissenters: none recorded.

### Decision 2026-05-17-4 (Option B: two-paper bundle locked — superseded by 2026-05-17-5 after D18 retraction)

- Owner: Role 1
- Type: re-scope (3 papers → 2 papers) + lock final shipping plan
- Subject: Bundle the project's 12-month output as a two-paper set per Option B of the bundling review.
- Inputs:
  - `deliverables/D17_submission_packets/bundling_recommendation.md` (critical re-read of D15/D16 + lit pass on D16 novelty claim).
  - `deliverables/D18_combined_observations/two_structural_observations.pdf` (15 pp, clean compile).
  - Updated `deliverables/D17_submission_packets/paper_D18.md` and updated `README.md`.
- Decision:
  - **D8 stand-alone** (R5a sharpness, 7 pp) → *Discrete Math* Note. Has a genuinely new identity (the witness identity $f_{2b}(4/7, \delta) - 9/16 = 12(\delta-9/8)^2/[7(4\delta-1)]$).
  - **D18 combined** (Two structural observations, 15 pp, merging D15+D16) → *Discrete Math* regular article (or EJC as fallback). Both halves are honestly framed as observations / packagings of existing chains.
  - D15 and D16 standalone source files **preserved for traceability** but **not separately submitted**.
  - D18 includes the patch flagged in the bundling review: D16's "first Crossing-Lemma improvement..." overstatement softened to match D16's own §1 hedge "we are not aware of an earlier such inequality".
  - D18 removes the now-internal cross-citations (D13 internal memo; D15→D16 cross-cite folded into in-paper `\Cref`); D8 remains a cited companion (the R5a paper is shipped separately).
  - Project's realistic mathematical contribution is **two** theorem-grade papers, not three, with no closure of the Cranston residual.
- Per-paper grades: D8 = **T**, D18 = **T** (both compile cleanly after the D17b/D17a QA passes and the Option B editorial merge).
- Next checkpoint: 2026-06-17 — two submissions (or coordinated arXiv posts), pending Marc's author-list and journal-target decisions per each paper's README.
- Dissenters: none recorded.

### Decision 2026-05-17-3 (three-paper bundle as initial 12-month deliverable — superseded by 2026-05-17-4 above)

- Owner: Role 1
- Type: project closeout (subject to author-list + journal-target decisions)
- Subject: Lock the project's 12-month output as a three-paper theorem-grade bundle.
- Inputs:
  - `deliverables/D8_paper/sharpness_9_8.pdf` (7 pp, Role 7).
  - `deliverables/D15_list_albertson_paper/list_albertson_le_18.pdf` (9 pp, Role 2).
  - `deliverables/D16_expander_crossing_paper/expander_crossing.pdf` (9 pp, Role 8).
- Decision: All three papers are theorem-grade, compile cleanly, and are
  ready for a co-author review pass + submission.
  - **D8 (R5a sharpness)** — proves $\delta = 9/8$ is sharp in FPS Claim 3.7
    via the witness identity $f_{2b}(4/7, \delta) - 9/16 = 12(\delta-9/8)^2/[7(4\delta-1)]$.
    Honest contribution: an obstruction theorem; not a sharpening of $9/16$.
  - **D15 (List-Albertson $t \le 18$)** — lifts ACF/BT/Ackerman from
    chromatic to list-chromatic, unconditional at $t \le 18$, conditional
    at $t \le 24$ (the list-version of FPS Lemma 2.3's $9/16$ constant
    is open). Honest contribution: clean assembly, not new heavy machinery.
  - **D16 (Expander Crossing Lemma)** — first explicit $(1-\theta)$
    packaging of the spectral parameter in the PST bisection-width
    Crossing Lemma, with corrected constants
    $\operatorname{cr}(G) \ge (1-\theta)^2 d_0^2 n^2/640 - d_0^2 n/16$
    for $d_0$-regular $\theta$-spectral expanders; plus an Albertson
    corollary on regular spectral-expander critical graphs (honestly
    vacuous in the Dirac-floor regime).
  - **None of the three closes the Cranston residual** at
    $(t, n) \in \{(25, 48), (26, 50), (26, 51)\}$. Closure requires
    either Role 9 SDP work on $\operatorname{cr}(K_t)$ (parked) or
    state-of-the-art exact crossing-number ILP at $n \sim 51$ (beyond
    current SOTA per Role 3's memo). The Cranston residual remains
    open as a project deliverable.
- Per-paper grades attached: D8 = **T**, D15 = **T**, D16 = **T** (each
  after a co-author review pass; D16 has one revision item: re-prove
  the PST constant $1/40$ inline rather than citing it).
- Next checkpoint: 2026-06-17 — three submissions (or coordinated
  arXiv posts), pending Marc's author-list and journal-target
  decisions per each paper's README.
- Project narrative for external description: "Three theorem-grade
  papers in the neighbourhood of Albertson's conjecture: an
  obstruction theorem on FPS's framework (D8), a clean lift of the
  conjecture to list-coloring at $t \le 18$ (D15), and a refined
  Crossing Lemma for regular spectral expanders (D16). The
  conjecture itself remains open at $t \in \{25, 26\}$; closure is
  beyond this team's accessible toolkit."
- Dissenters: none recorded.

### Decision 2026-05-17-2 (R2c verdict + Track B re-prioritisation)

- Owner: Role 1
- Type: accept negative result + re-prioritise Track B
- Subject: D13 R2c attack memo + D12 Ore-corner pipeline outcomes.
- Inputs: `deliverables/D13_r2c_attack/memo.md` (Role 8 attack memo,
  384 lines, **proof failed cleanly**, structural obstruction
  identified); `deliverables/D12_ore_c3/REPORT.md` (0/12 Ore graphs
  certified, best certified bound 3825 vs $Z(26)=5148$).
- Decision:
  - **D13 is accepted as Role 8's month-1 deliverable.** The negative
    verdict is theorem-grade in its own right: the random-sampling
    proof discards $d_0$ at the iteration-stopping step, and the
    natural salvages (Pach–Spencer–Tóth bisection-width;
    Faudree–Schelp $K_t$-subdivision) both fail at the Ore corner.
  - **Track B headline pivots from R2c to R3.6** (fractional / list /
    DP-chromatic Albertson; Role 2). R2c is downgraded to a
    secondary fallback under Role 8's proposed bisection-width
    salvage $T_1'$, with the honest caveat that $T_1'$ is
    publishable but orthogonal to the Cranston residual.
  - **Track A** (D12 Ore-corner certification) is **parked** until
    either Role 9 SDP work or a sharper $\operatorname{cr}(K_t)$
    finite lower bound becomes available; the gap of $1323$ at
    $(26, 51)$ is structural and not closable by current methods.
  - **Role 2 to ship D14 (R3.6 attack memo)** by 2026-06-17. Same
    5-page format as D13. Same "one explicit theorem candidate +
    honest failure documentation" rules.
  - Project's realistic 12-month output now framed as: (i) the R5a
    sharpness theorem (D8 — shipped), (ii) Role 8's R2c
    bisection-width fallback $T_1'$ if developed, (iii) D14 R3.6
    candidate if proved. None close any Cranston residual; together
    they constitute a bundle of partial results.
- Credit grade attached: D13 = **EC** (honest negative result with
  structural identification; publishable as a follow-up to BK).
- Next checkpoint: 2026-06-17 (D14 R3.6 memo; Role 8 $T_1'$ progress).
- Dissenters: none recorded.

---

## 1. Mission statement

Over a 12-month horizon, this team's job is to convert the v3 plan into either
(a) a theorem, or (b) a clean, citable negative / structural result. The v3
tractability scores (1/10 full conjecture, 2/10 closing $t = 25, 26$, 3/10 a
structural sub-result) are the calibration. We do not pretend to attack the
full conjecture; we run two coordinated tracks (Section 4) whose union has a
realistic shot at *something* publishable. Concretely we book:

- **(a) Full proof of Albertson.** Probability $\le 1\%$ in 12 months. The
  obstruction chain O1–O3 in v4 has resisted four decades of refinements;
  nothing in our toolkit threatens it. Listed for completeness; not pursued.
- **(b) Close $t = 25$ and/or $t = 26$.** **Removed as a 12-month target.**
  The compute-team consensus (Roles 3, 4, 5, 6 memos) is that unrestricted
  closure at $(25, 48)$ or $(26, 50)$ is infeasible in 1 cluster-year and
  likely 100. We now book closure attempts only on *named* sub-families
  (outcome (d)); the residual itself remains open as a project deliverable.
- **(c) Structural sub-result via R5a (headline), R2c, R3.x.** Probability
  $\ge 50\%$ if Roles 7, 8, 2 execute. **The headline is R5a**: re-derive
  FPS Claim 3.7 with Case 2b isolated. Minimum publishable outcome: any
  $c < 9/16$ in Lemma 2.3 of arXiv:2510.05893. Stretch: $c = 11/20$.
  Dream: $c = 1/2$. Secondary structural targets: R2c (min-degree-refined
  Crossing Lemma on critical graphs), R3.5 ($k$-planar Albertson up to a
  fixed $k$), R3.6 (fractional / DP-chromatic Albertson).
- **(d) Clean sub-family certification.** Probability $\ge 30\%$. Two
  concrete targets: (i) the $(26, 51)$ Ore corner — plausibly a small
  one-composition family from two $K_{26}$s; Role 5 enumerates, Role 3
  certifies. (ii) one named non-Ore subfamily at $(25, 48)$ or $(26, 50)$
  — Role 2 names it, Role 4 + Role 5 close it under SAT/CEGAR using the
  non-Ore KY edge floor as a mandatory constraint. This closes
  *sub-families*, not the residual, and is honest about that.
- **(e) Counterexample to Albertson.** Probability $\le 2\%$. The conjecture
  is widely believed; counterexample-hunt is a bounded side activity, not
  a headline. Role 9's role attaches here only.

Anything not on this list is out of scope for the 12-month horizon.

---

## 2. Theorem-credit decision rules

For each computational outcome a sub-team could plausibly deliver, the PI
adjudicates **a priori** the level of credit it gets. This prevents disputes
mid-year about whether a result is "essentially a theorem".

We use four grades:

- **T (theorem)** — provable, citable, machine-checkable lower bounds with a
  reproducible certificate. Suitable for a journal claim.
- **EC (essentially complete)** — would be a theorem after a finite amount of
  certificate-cleaning that does not require new ideas. Suitable for an
  arXiv preprint with the caveat noted.
- **SE (suggestive evidence)** — non-trivial computational signal that
  constrains future search but does not by itself prove anything. Suitable
  for an internal report or a "computational note".
- **N (no credit)** — does not change our state of knowledge.

### Decision rules by outcome

| # | Outcome | Grade | Conditions / notes |
|---|---------|-------|--------------------|
| D1 | An ILP solver (Role 3) reports $\underline{cr}(G) \ge Z(25)$ for every $G$ in the R1b residual sub-family at $n = 48$ | **T** *only if* the ILP produces a per-instance certificate (LP dual or branch-and-bound proof tree) that is independently re-checked by a second solver or by hand on a sample of $\ge 20$ instances; otherwise **EC** | Per v3 §C3, certified lower bound is the only valid elimination. An "unverified" solver claim is **N** until certificates are reproduced. |
| D2 | Same as D1 but the residual sub-family is the *entire* set of 25-critical graphs on 48 vertices with $\delta \ge 24$ (Role 5 supplies the graph6 file, Role 3 grinds) | **Removed as a 12-month target in v4.** | Per the v4 audit, unrestricted closure of $(25, 48)$ is infeasible. D2 is parked. Sub-family elimination (D4-style) is the only Track A target that ships. |
| D3 | Flag-algebra SDP (Role 9) returns a finite certified $\underline L(25) = 4250$ | **EC** until the SDP rounding is converted to an explicit combinatorial argument; **T** if rationalized | A floating-point SDP is **not** a theorem in the topological-graph community. Per v3 §C6 and the v3 obstruction O2 rewrite, the *asymptotic* Balogh–Lidický–Salazar / de Klerk constants are explicitly **not** finite certificates. A *finite* certified $\underline L(25)$ requires rational rounding plus a positivity certificate (SOS or similar). The PI will accept rational SOS as **T** but not raw SDP output. |
| D4 | SAT (Role 4) returns UNSAT for "$\exists$ a 25-critical graph on 48 vertices with $\delta \ge 24$, fixed $K_{24}$ in a fixed position, $\overline{cr}(G) < Z(25)$" | **SE** unless the SAT proof log is independently verified by DRAT-trim or similar and the encoding is independently audited (Role 6 + Role 2) | Per v3 §F5, R1a is research-grade and the encoding of criticality is the hardest part. UNSAT on a *restricted* sub-case eliminates that sub-case from the counterexample search. It does **not** close the residual; that requires unioning over all sub-families, which is a separate combinatorial coverage proof Role 2 owes us. |
| D5 | SAT (Role 4) returns SAT (a witness graph $G$) for the same encoding | **EC** if and only if Role 3 independently computes $\underline{cr}(G) < \underline L(t)$ for a finite certified $\underline L(t)$ | A SAT witness is a *candidate* counterexample, not a counterexample. Per v3 §P3 and Obstruction O2, $\overline{cr}(G) < Z(25)$ falsifies only the *strong form*; outright Albertson falsification requires $\overline{cr}(G) < \underline L(25)$. If Role 9 has not yet shipped a finite $\underline L(25)$, D5 is parked. |
| D6 | Role 2 proves a Kostochka–Stiebitz-style structural lemma: every $t$-critical graph on $\le 2t$ vertices with $\delta \ge t - 1$ contains a $K_{t-1}$-subgraph (or one of a small list of named gadgets) | **T** | A genuine theorem in critical-graph structure, independently publishable, *and* it reduces R1b's sub-family to a tractable enumeration. This is the single most leveraged structural result on the table. |
| D7 | Role 7 / Role 8 push Lemma 2.3 of arXiv:2510.05893 from $9/16$ to something strictly smaller (**R5a** in v4) | **T** | **Headline 12-month target.** Standalone publishable chromatic-index result. Tiers: $c < 9/16$ (minimum publishable), $c = 11/20$ (stretch), $c = 1/2$ (dream). Per v4 §R5a, this is also the lever for pushing the FPS asymptotic constant from $1.64$ toward $2$. |
| D8 | Role 8 proves a min-degree-refined Crossing Lemma constant $c(\delta) > 1/27.48$ for $\delta \ge t - 1$ (R2c in v3) | **T** | Standalone publishable Crossing-Lemma improvement. Per v3 §R2, the realistic payoff is "improve the constant by another $\le 5\%$, push Albertson unconditionally from $t \le 24$ to $t \le 25$". |
| D9 | Role 5 ships `25_crit_n48_delta24.g6` claiming to enumerate the entire residual | **N** as a coverage proof unless accompanied by a written coverage argument. **SE** as a candidate seed for Roles 3, 4 | Per v3 §R1 and F5, brute enumeration at $n = 48, \delta \ge 24$ is infeasible. A non-empty file is *not* the same as a coverage proof. |
| D10 | Role 7 finds a weak $K_{25}$-immersion in some heuristic candidate $G$ (C7) | **SE** | Per v3 Obstruction O3 and F6, a weak immersion alone is **not** a witness for Albertson; the second-stage crossing recovery is mandatory. The PI will not accept any "immersion witness" as a theorem-grade result. |
| D11 | Role 2 (or anyone) proves Albertson on $K_{t-1}$-minor-free graphs | **T but vacuous in the open range** | Per v3 §R3.1, this is vacuous *conditional on Hadwiger*; unconditionally Hadwiger is open for $t \ge 7$. So this is a theorem only in the small-$t$ range where Hadwiger is proven ($t \le 6$), where Albertson is already known. **N** as progress on the open range. |
| D12 | Role 9 ships an SDP value that *matches* the asymptotic Balogh–Lidický–Salazar constant for finite $t = 25, 26$ as floating-point output | **N** as a certificate; **SE** as a sanity check on the SDP code | Per v3 §F1b, asymptotic ratios are not finite certificates. The PI will not accept floating-point asymptotic constants as operational thresholds. |

### Standing rules

- "Verified by a second solver" means: a different solver family (e.g.
  Gurobi $\to$ SCIP+CPLEX, or kissat $\to$ cadical+DRAT-trim) reproduces the
  result. Role 6 owns the parallel-runner harness.
- "Independently re-checked by hand" means: Role 2 or Role 7 spot-checks the
  certificate logic on a representative sample, with a written note in the
  decision log (Section 6).
- The PI may upgrade an **EC** to **T** only after the certificate-cleaning
  task is itemized in the decision log and completed.

---

## 3. Dependency graph

```mermaid
flowchart TD
    R5[Role 5: nauty / canonical labeling] -->|graph6 files| R3[Role 3: exact crossing-number]
    R5 -->|seed instances| R4[Role 4: SAT/CP/CEGAR]
    R2[Role 2: critical-graph structure] -->|structural restriction R1b| R5
    R2 -->|criticality encoding rules| R4
    R2 -->|target sub-family spec C1| R3
    R6[Role 6: HPC] -->|cluster scheduling| R3
    R6 -->|cluster scheduling| R4
    R6 -->|cluster scheduling| R9
    R9[Role 9: SDP / flag algebra] -->|finite L_bar(25), L_bar(26)| R3
    R9 -->|finite L_bar| R4
    R8[Role 8: probabilistic / topological] -->|min-degree Crossing Lemma constant R2c| R3
    R8 -->|min-degree Crossing Lemma constant R2c| R2
    R7[Role 7: immersion / chromatic-index] -->|R5 Lemma 2.3 refinement| R2
    R7 -->|C7 immersion fingerprint| R3
    R3 -->|certified bounds back| R1[Role 1: PI]
    R4 -->|UNSAT / SAT outcomes| R1
    R9 -->|finite certificates| R1
    R2 -->|structural theorems| R1
    R7 -->|R5 chromatic-index result| R1
    R8 -->|R2c constant| R1
    R1 -->|coverage / scope decisions| R2
    R1 -->|stop / continue calls| R6
```

### Numbered edges (with critical-path annotations)

1. **R2 → R5**: structural restriction theorem (D6-class) that bounds the
   enumerable sub-family of $25$-critical graphs on $48$ vertices. *On the
   critical path.* Without this, R5 has nothing tractable to enumerate.
2. **R5 → R3**: graph6/sparse6 file `25_crit_n48_delta24_restricted.g6`. *On
   the critical path.* Estimated size depends entirely on edge 1.
3. **R5 → R4**: seed instances and canonical-form pruning for SAT/CEGAR.
4. **R2 → R4**: criticality-as-SAT-clause specification (the hardest part of
   the R1a encoding per v3 §R1a). *On the critical path for R1a.* Role 2
   must hand Role 4 a clause schema, not a hand-wave.
5. **R2 → R3**: target sub-family spec (C1 in v3 §C1), telling R3 which
   $(t, n, \delta, \text{structure})$ tuples to run ILP on.
6. **R6 → R3, R6 → R4, R6 → R9**: cluster scheduling, checkpointing,
   deterministic re-runs, artifact storage. *On the critical path for any
   compute-heavy outcome.*
7. **R9 → R3, R9 → R4**: finite certified $\underline L(25), \underline L(26)$
   (D3-class). **Off the positive-proof critical path entirely in v4.**
   Per `review_v3.md`, positive proof only needs $Z(t)$ as an *upper* bound
   on $cr(K_t)$ — Role 3 / Role 4 target $\overline{cr}(G) \ge Z(t)$, not
   $\overline{cr}(G) \ge \underline L(t)$. Edge 7 matters only for falsification
   (outcome (e)). Role 9 is reassigned to literature audit + falsification.
8. **R8 → R3, R8 → R2**: R2c min-degree-refined Crossing Lemma constant. If
   R8 ships D8, R2's structural restrictions become easier and R3's
   certified lower-bound targets shrink.
9. **R7 → R2**: R5 chromatic-index Lemma 2.3 refinement (D7-class). If R7
   ships, R2 can rephrase its structural restrictions in the new asymptotic
   regime — but at finite $t = 25, 26$ this is at best a sanity result.
10. **R7 → R3**: immersion fingerprint (C7). *Not on critical path*; the
    fingerprint is **SE** at best per D10.
11. **R3 → R1, R4 → R1, R9 → R1, R2 → R1, R7 → R1, R8 → R1**: reporting back
    to the PI for the decision log.
12. **R1 → R2, R1 → R6**: scope and budget decisions; kill-switches on
    routes whose milestones slip past 3-month and 6-month checkpoints.

### Critical path (v4)

The v3-era "close $t = 25$" critical path is **deprecated** — outcome (b) is
no longer a 12-month target. The two v4 critical paths are:

**Path 1 — Track B headline (R5a).** Role 7 (D3 reconstruction of FPS Claim
3.7) → Role 7 (improvement attempt) → Role 8 (chromatic-index / probabilistic
verification if needed). No external dependencies; this path is fully under
the structural sub-teams. If R5a yields nothing by 6 months, Track B pivots
to R2c (Role 8) or R3.6 (Role 2) as the headline.

**Path 2 — Track A sub-family certification.** Edges 1 → 2 → 6 still hold,
but the target is now a *named sub-family* (Ore corner at $(26, 51)$, or one
non-Ore subfamily named by Role 2), not the full residual. The non-Ore KY
edge floor is a *mandatory* R1a/R4 constraint, no longer optional. Falls
through to D4 / D5, not D2.

**Edge 7 (R9 → R3)** is no longer critical for any positive outcome.

### Surfaced findings from the dependency graph

- **Finding F-DG-1 (v4 update).** Edge 1 (R2 → R5) was the critical
  bottleneck under v3's "close $t = 25$" framing. Under v4, outcome (b) is
  removed; edge 1 is no longer existential. Role 5's deliverable is now the
  $(26, 51)$ Ore corner (small, finite, week-1) plus one named non-Ore
  subfamily once Role 2 specifies it. The "Role 2 owes Role 5 a
  D6-grade structural restriction or the plan collapses" framing is **stale**.
- **Finding F-DG-2 (v4 update).** Role 9 is off the positive-proof critical
  path entirely. SDP work matters only for outcome (e) (falsification). The
  PI's expected Role 9 output is a literature audit (no later than month 3)
  + a falsification-support note, not a finite $\underline L(t)$ certificate.
- **Finding F-DG-3.** Roles 7 and 8 are now on the *only* critical path for
  outcome (c). Track B consciously hands them all the structural budget.
  R5a is the headline; R2c is the fallback.
- **Finding F-DG-4.** The PI's own role (Role 1) does not appear as a source
  of theorem-grade output; that is correct. Role 1 produces *coordination
  artifacts* — this document, the decision log, milestone calls — not
  theorems.
- **Finding F-DG-5 (v4 new).** The Cranston residual $(25, 48)$ has **no
  $25$-Ore counterexample candidate** (congruence $48 \not\equiv 1 \pmod{24}$).
  $(26, 50)$ likewise ($50 \not\equiv 1 \pmod{25}$). Only $(26, 51)$ admits
  Ore candidates. Any v3-era plan or role-memo treating $(25, 48)$ Ore as
  reachable is wrong (specifically: Role 2 memo's "$25$-Ore family at
  $(25, 48)$ is essentially a single graph" — retracted in v4).

---

## 4. Two-track strategy

We split the team into Track A (close the Cranston residual) and Track B
(structural / asymptotic). The PI manages the two tracks separately and
re-balances at the 3- and 6-month checkpoints.

### Track A — subfamily certification + counterexample hunt (v4)

**Composition.** Roles 2, 3, 4, 5, 6 (Role 9 only for counterexample-hunt
side per F-DG-2).

**Goal.** Bounded. **Not** "close $t = 25$"; that goal is removed in v4 per
the Roles 3/4/5/6 compute-team consensus. The two concrete sub-targets are:
(i) **$(26, 51)$ Ore corner**: enumerate Ore compositions $K_{26} * K_{26}$
up to isomorphism (small, finite), then certify each via the C3 pipeline.
(ii) **One named non-Ore subfamily** at one of the three Cranston residuals,
using the non-Ore Kostochka–Yancey edge floor ($|E| \ge 588 / 638 / 650$) as
a *mandatory* R1a SAT encoding constraint.

**Milestones.**

- **1 week (D4 deliverable).** Role 5 ships the $(26, 51)$ Ore enumeration
  with graph6 files. Role 2 ships the literature-verification bundle (D2 in
  `deliverables/`) confirming the six KY numbers and the BK threshold.
- **3 months.** Role 5 ships C1 (residual spec script: $(t, n, Z(t), $ trivial
  floor, KY floor, non-Ore KY floor, Ore-allowed flag, FPS finite thresholds$)$).
  Role 2 ships a named non-Ore subfamily with formal definition. Role 4
  ships a working SAT encoding skeleton on $t = 4, 5$ toy cases with the
  non-Ore KY floor wired in and verified.
- **6 months.** Role 3 ships C3 running on the $(26, 51)$ Ore corner (small
  case — should terminate). Role 4 ships a SAT/CEGAR result on the named
  non-Ore subfamily — verdict may be "did not terminate" (acceptable; pivot
  to Track B headline).
- **12 months.** Realistic: a D4-grade SE outcome on $(26, 51)$ Ore (either
  certified, or "all but $k$ candidates certified") + a parked non-Ore
  subfamily run. Anything more is upside.

**Honest assessment.** Track A is the bounded track in v4. Its job is to
*not consume the project*. If Role 4's SAT pipeline does not produce a
verdict on a named subfamily by month 6, Track A goes to maintenance mode
and all remaining budget shifts to Track B.

### Track B — structural / asymptotic (v4 headline = **R5a**)

**Composition.** Roles 7 (lead), 8, 2 (and Role 6 for compute when needed).

**Goal.** Outcome (c) via R5a, R2c, R3.6 in priority order. The headline is
**R5a: re-derive FPS Claim 3.7 with Case 2b isolated** (per `review_v3.md`
and Role 7's memo identifying Case 2b as binding). Tiers:

- **MPO (minimum publishable outcome):** any constant $c < 9/16$ in FPS
  Lemma 2.3, with the binding inequality identified.
- **Stretch:** $c = 11/20$ (matches Case 2a's $0.55$).
- **Dream:** $c = 1/2$, i.e. pushing FPS Theorem 1.2 to vertex bound
  $\sim 1.7(k - 1)$.

**Milestones.**

- **1 week (D3 deliverable).** Role 7 ships the faithful reconstruction of
  Claim 3.7 in own notation, with the binding inequality in Case 2b
  isolated. **No new theorem is expected this week.** The deliverable is
  the reconstruction artifact at `deliverables/D3_R5a_reconstruction.md`.
- **1 month.** Role 7 ships the **R5a Claim 3.7 verdict**: is $9/16$ a real
  obstruction or an artifact of Case 2b's slack? Three possible outcomes:
  - $c < 9/16$ achievable: immediate theorem target; Role 7 drafts the
    improvement.
  - $c = 9/16$ binding: pivot R5a from "improve" to "obstruction note" —
    still publishable.
  - Algebra unclear: assign Role 8 to probabilistic / optimization
    verification of Case 2b.
- **3 months.** Role 7 ships a draft R5a result (improvement or obstruction
  note). Role 8 ships R2c attack plan + empirical Crossing Lemma slack
  (C4). Role 2 ships R3.6 attack plan.
- **6 months.** Role 7 ships R5a as preprint-ready. Role 8 ships R2c lemma
  in draft. Role 2 ships R3.6 in draft.
- **12 months.** R5a as a standalone publishable theorem (D7). R2c, R3.6
  as preprints if they materialize.

**Honest assessment.** Track B is the only realistic source of a publishable
12-month theorem. R5a is the highest-leverage local calculation in the whole
plan; that is also why the week-1 reconstruction matters more than any other
single deliverable.

### What we explicitly do *not* commit to (v4)

- **Unrestricted $(25, 48)$ enumeration or SAT closure.** Per the v4 audit
  and the Roles 3/4/5/6 compute-team consensus, this is not a 12-month
  target. Sub-family work only.
- **Large SAT cluster jobs before the encoding is audited.** Per PI
  directive: implement the constraint model on toy cases ($k = 4, 5$;
  known critical graphs; verify KY floors and criticality clauses) before
  launching any cluster compute.
- **Finite $cr(K_{25})$ lower bounds for positive proof.** Per
  `review_v3.md`: positive proof only needs the *upper* bound $Z(t)$ on
  $cr(K_t)$, not a finite lower bound. Role 9 work on $\underline L(t)$
  is justified *only* for outcome (e) (falsification).
- **Heuristic crossing-number drawings as eliminations.** Per v4 §F4: a
  heuristic upper bound on $cr(G)$ says nothing about whether $G$ falsifies
  Albertson; it can only flag candidates for certified bounding. The PI
  will reject any pipeline that eliminates a graph on heuristic grounds.
- **Track A consuming the project.** Per v4 §F5 and the compute-team
  consensus: Track A is bounded. If it is not yielding by month 6, all
  remaining budget shifts to Track B (R5a).
- **Using the Balogh–Lidický–Salazar / de Klerk asymptotic constants as
  finite thresholds.** Per v4 §F1b and the v3 revision-history correction.
- **A "full proof of Albertson" allocation.** 1/10 score; not a 12-month
  target; pursued only as a by-product of Track B sub-results.

---

## 5. Cross-cutting risks

Each risk has a named owner. The owner is responsible for monitoring,
reporting in the decision log at each checkpoint, and proposing mitigation.

### Risk R-1. Solver bug in R1a giving a wrong UNSAT

**Owner.** Role 4 (with Role 6 for harness).

**Description.** SAT solvers have shipped wrong-UNSAT bugs (kissat, glucose,
maple-sat all have known historical issues). If R4 reports UNSAT on a
sub-family at $t = 25, n = 48$ and that result is wrong, we publish a
retraction.

**Mitigation.** Every UNSAT result is run on at least two independent
solvers (different code lineages) and the proof log is verified by DRAT-trim
or equivalent. Per D4, this is a precondition for **SE** credit, not a
post-hoc check.

### Risk R-2. Flag-algebra SDP is not a true proof (v4: demoted in priority)

**Owner.** Role 9 (with Role 1 adjudicating credit).

**Description.** Floating-point SDP output is not a theorem in the
topological-graph community. Per D3 and v4 §F1b, the asymptotic
Balogh–Lidický–Salazar / de Klerk constants are *not* finite certificates.
**v4 update:** since Role 9 is no longer on the positive-proof critical
path (per `review_v3.md` and F-DG-2), this risk only fires if Role 9 is
asked to ship a falsification-grade finite $\underline L(t)$. The PI's
default is to not ask.

**Mitigation.** Role 9 ships a literature audit at month 3 (extracting any
extractable finite constants from BLS / de Klerk ancillary data). Any
rational SOS rounding work is deferred to a Track B falsification-side
escalation, only if outcome (e) becomes a serious consideration.

### Risk R-3. Nauty enumeration secretly missing a subfamily

**Owner.** Role 5 (with Role 2 reviewing the coverage argument).

**Description.** Role 5 ships a graph6 file, claims it is the entire
residual at $t = 25, n = 48, \delta \ge 24$, but a sub-family is missed
because of a canonical-labeling bug or a too-aggressive filter. Any
elimination based on the file is then vacuous.

**Mitigation.** Role 5 ships a *coverage proof* — a written argument that
the filters used are correct and exhaustive — alongside any graph6 file.
Per D9, a file without a coverage proof is **N**. The PI also requires Role
2 to independently audit the coverage argument before any **T** or **EC**
credit attaches to an enumeration-based result.

### Risk R-4. $cr(K_t)$ on the RHS of Albertson is conjectural for $t \ge 13$

**Owner.** Role 9 (with Role 1 adjudicating).

**Description.** Per v3 Obstruction O2 (rewritten), $cr(K_t)$ is unknown for
$t \ge 13$. Proving $cr(G) \ge L(t)$ for some $L(t) \le cr(K_t)$ does **not**
prove Albertson; it proves a weaker statement. Proving $cr(G) \ge Z(t)$ does
prove Albertson (and the strong form), because $Z(t) \ge cr(K_t)$. Confusing
upper and lower bounds on $cr(K_t)$ — as the v2 plan did and the review
caught — would invalidate any positive proof.

**Mitigation.** Every script and every paper draft must explicitly state
whether it is targeting $Z(t)$ (positive proof side) or $\underline L(t)$
(falsification side). The PI will reject any draft that conflates these.
Per v3 §F1 and §F1b, this is a hard rule.

### Risk R-5. Track A residual sub-family does not cover the full residual

**Owner.** Role 2 (with Role 1 adjudicating credit per D2).

**Description.** Even if Role 4 closes a structurally-restricted sub-family
of $25$-critical graphs on $48$ vertices via SAT UNSAT, the residual is only
*closed* if the sub-family is the *entire* residual (or its complement is
also closed by some other argument). Otherwise we ship a sub-family
elimination, not a residual closure.

**Mitigation.** Role 2 owes a written coverage decomposition: the residual
is partitioned into named sub-families, each sub-family has an assigned
attack route, and the PI tracks coverage progress in the decision log. A
single sub-family elimination is **SE**, not closure. The PI will not let a
sub-family elimination be reported as closure of the residual.

### Risk R-6. The exact crossing-number ILP/SAT is infeasible at $n \sim 50, m \sim 600$

**Owner.** Role 3 (with Role 6 for compute and Role 4 for the SAT-side
alternative).

**Description.** Per v3 transparency note, exact crossing-number
computation at $n = 48, m = 576$ is at or beyond the state of the art. The
Buchheim–Chimani ILP and the Chimani–Mutzel SAT encoding have published
results around $n \sim 40$ for sparse graphs; pushing to $n = 50$ with
$m = 600$ is itself a research engineering problem.

**Mitigation.** Role 3 commits at the 3-month checkpoint to either (a) a
demonstrated scaling result on dense graphs at $n = 40$ comparable to the
target, or (b) a written argument for why C3 should be re-scoped. If
neither lands, the PI re-scopes outcome (b) at the 6-month checkpoint.

### Risk R-7. Track B drafts stall and Roles 7, 8, 9 produce nothing publishable

**Owner.** Role 1 (re-scoping authority).

**Description.** Pen-and-paper structural mathematics is hard to schedule.
Even with attack plans in place at month 3, a chromatic-index lemma or a
min-degree Crossing-Lemma constant can simply fail to yield. If Roles 7, 8,
9 all stall, Track B produces nothing.

**Mitigation.** At the 6-month checkpoint, the PI evaluates each Track B
draft. Any role with no draft at 6 months is reassigned to Track A
auxiliary tasks (certificate-cleaning, literature audits, integration
testing). The PI will not let Track B "drift" past the 6-month checkpoint
without intervention.

### Risk R-8. Confusing weak immersion with Albertson (F6)

**Owner.** Role 7.

**Description.** Per v3 Obstruction O3 and F6, a weak $K_t$ immersion alone
does **not** certify Albertson; the second-stage crossing recovery is
mandatory. If Role 7 ships a C7 immersion-witness pipeline and labels the
output as "Albertson-certified", the result is wrong.

**Mitigation.** Per D10, an immersion witness is **SE** at best. Role 7
labels its C7 output as a structural fingerprint, never as a verdict on
Albertson.

---

## 6. Decision log template

The team maintains a date-stamped decision log in this section. Each entry
is a go/no-go call by the PI (or a recommendation by a sub-team
escalated to the PI). Format:

```
### Decision YYYY-MM-DD-N

- Owner: <role>
- Type: <go | no-go | re-scope | escalate compute | publish intermediate | kill route>
- Subject: <route / outcome / risk>
- Inputs: <links to artifacts, drafts, test runs>
- Decision: <one paragraph>
- Credit grade attached (if applicable): T | EC | SE | N
- Next checkpoint: <date>
- Dissenters: <names, with one-line rationale each>
```

Initial entries to populate in the first 30 days:

### Decision 2026-05-16-1

- Owner: Role 1
- Type: go
- Subject: Adopt v3 plan and INTEGRATION.md as the team's working contract.
- Inputs: `docs/plan.md` v3, `docs/review.md`, this document.
- Decision: All nine roles work to v3 only. v2 is deprecated.
- Credit grade attached: N/A
- Next checkpoint: 2026-06-16 (1-month checkpoint).
- Dissenters: none recorded at kickoff.

### Decision 2026-05-16-2 (v4 adoption)

- Owner: Role 1
- Type: re-scope
- Subject: Adopt plan v4 + `docs/review_v3.md`; bring INTEGRATION.md into sync.
- Inputs: `docs/plan.md` v4 (1123 lines), `docs/review_v3.md`, role memos in `work/01–09/`, deliverables D2 + D3 (week-1).
- Decision:
  - Outcome (b) "close $t = 25$" is **removed** as a 12-month target; Track A reframed as subfamily certification + counterexample hunt.
  - **R5a is the Track B headline** (re-derive FPS Claim 3.7 with Case 2b isolated).
  - $(26, 51)$ is the **only Ore corner** (Ore-order congruence $|V| \equiv 1 \pmod{k-1}$).
  - Non-Ore Kostochka–Yancey edge floors ($\ge 588 / 638 / 650$) are **mandatory** R1a SAT/CEGAR constraints.
  - Role 9 is **off the positive-proof critical path** (per `review_v3.md`); reassigned to literature audit + falsification-only.
  - Role 2's v3 memo claim "$25$-Ore family at $(25, 48)$ is essentially a single graph" is **retracted** (impossible by congruence).
  - $(k - 1)$-edge-connectivity of $k$-critical graphs attributed to **Dirac 1953**, not Kostochka–Stiebitz.
  - BK Crossing-Lemma threshold: arXiv abstract gives $|E| \ge 6.77|V|$; Cranston invokes $6.95|V|$; D2 verification recommends **using $6.95$ for Cranston-chain calculations** but reading the BK PDF body for the final SAT encoding constraint.
- Credit grade attached: N/A
- Next checkpoint: 2026-05-23 (week-1 closeout: D2 / D3 / D4 reviewed).
- Dissenters: none recorded.

### Decision 2026-05-16-3 (R5a closeout)

- Owner: Role 1
- Type: kill route + close with theorem-grade artifact
- Subject: R5a as "tune $\delta$ inside FPS Claim 3.7 to beat $9/16$".
- Inputs: `deliverables/D8_paper/sharpness_9_8.pdf` (theorem-grade sharpness note); `deliverables/D8_paper/tighter_fps_RETRACTED.pdf` (retraction); D5 SymPy scripts including `witness.py`.
- Decision: **R5a closed.** $c = 9/16$ binding in the FPS framework; proof analytic, not numerical. Front-running Track B alternatives are R2c (Role 8) and R3.6 (Role 2). No new R5a route opened.
- Credit grade attached: **T** (theorem-grade) — the witness identity $f_{2b}(4/7, \delta) - 9/16 = 12(\delta - 9/8)^2/[7(4\delta - 1)]$ closes the analytic sign gap that previously kept the note at EC.
- Next checkpoint: 2026-06-16 (1-month general checkpoint; R2c / R3.6 attack plans expected).
- Dissenters: none recorded.

### Decision 2026-06-16-? (placeholder)

- Owner: Role 1
- Type: go-or-no-go on Track A
- Subject: Has Role 2 shipped a partial structural restriction (Section 4 Track A 3-month milestone)?
- Inputs: Role 2's 3-month report.
- Decision: TBD.

### Decision 2026-08-16-? (placeholder)

- Owner: Role 1
- Type: go-or-no-go on R9
- Subject: Has Role 9 shipped either a finite certified $\underline L(25)$ or a written argument for re-scoping (Track A 6-month milestone)?
- Inputs: Role 9's 6-month report.
- Decision: TBD.

### Decision 2026-11-16-? (placeholder)

- Owner: Role 1
- Type: re-scope or kill
- Subject: Track B 6-month checkpoint — at least one of R2c, R5, R3.6 in draft form?
- Inputs: Role 7, Role 8, Role 2 reports.
- Decision: TBD.

---

## 7. First 30-day plan

Per-role ordering instructions for May 16 – June 16, 2026. Each bullet is a
concrete task tied to a v3 section number. Roles report status at the
2026-06-16 checkpoint.

### Role 1 (PI)

- Maintain this document and the decision log. Add an entry for every
  go/no-go call.
- Author the 3-, 6-, 12-month milestone tracker (mirror of Section 4).
- Adjudicate cross-team disputes (especially R1c discard rule per F4 and the
  $cr(K_t)$ vs. $Z(t)$ direction per F1).

### Role 2 — Critical-graph expert (v4)

- **Week 1**: ship the literature-verification bundle D2 (Cranston triples,
  KY six numbers, Ore congruence proof, BK threshold). **Done** —
  `deliverables/D2_literature_verification.md`.
- **Month 1**: name one non-Ore subfamily at $(25, 48)$ or $(26, 50)$ as
  the Track A SAT target. Formal definition; coverage statement (what
  fraction of the residual it captures, honestly stated).
- **Month 1–3**: scope R3.6 (fractional / list / DP-chromatic Albertson)
  as Track B fallback. Sanity-check Role 7's R5a algebra if asked.
- **Standing**: any structural claim about $t$-critical graphs goes through
  Role 2 review before SAT encoding. Specifically, the v3 misattribution
  $(k-1)$-edge-conn $\to$ Kostochka–Stiebitz vs. **Dirac 1953** is fixed
  in v4; Role 2 owns keeping this correct downstream.

### Role 3 — Exact crossing-number algorithms

- Audit the Buchheim–Chimani ILP and Chimani–Mutzel SAT implementations
  (links and code) for feasibility at $n = 40$ dense graphs as a scaling
  baseline. Deliverable: a written scaling report.
- Draft the C3 pipeline (v3 §C3) with the v3-corrected discard rule
  (heuristic upper bounds only flag, certified lower bounds eliminate; per
  F4 invalid eliminations are forbidden).
- Coordinate with Role 5 on the graph6 input format and with Role 6 on
  cluster job submission.

### Role 4 — SAT/CP/CEGAR engineer (v4)

- **Per PI directive**: no large SAT cluster jobs before the encoding is
  audited. Implement the constraint model on toy cases ($k = 4, 5$;
  known critical graphs) first; verify the non-Ore KY floors and
  criticality clauses behave correctly.
- **Month 1**: SAT encoding skeleton with the **non-Ore KY edge floor as a
  mandatory hard constraint** ($|E| \ge 588$ at $(25, 48)$, $\ge 638$ at
  $(26, 50)$, $\ge 650$ at $(26, 51)$). Target predicate:
  $\overline{cr}(G) < Z(t)$ (positive-proof / strong-form side).
- **Month 2**: SAT termination on $t \in \{4, 5, 12\}$ small cases.
- **Month 3+**: SAT/CEGAR on Role 2's named non-Ore subfamily — only after
  the encoding has been audited.
- Coordinate with Role 2 on the criticality-as-SAT-clause schema (edge 4).

### Role 5 — Enumeration / nauty / canonical-labeling (v4)

- **Week 1**: D4 — enumerate all Ore compositions $K_{26} * K_{26}$ up to
  isomorphism; export graph6 and DIMACS at
  `deliverables/D4_ore_26_51/`. **In progress**.
- **Month 1**: stand up `nauty`/`pynauty` toolchain for canonical-labeling.
  Draft the coverage-proof template that any future graph6 file ships with
  (per D9 and R-3).
- **Month 2+**: once Role 2 names a non-Ore subfamily (month 1 milestone),
  enumerate it (likely small if the family is well-chosen).
- **Standing**: never ship a graph6 file without a coverage statement.

### Role 6 — HPC / scientific software

- Stand up the team's cluster workflow: checkpointing, deterministic
  re-runs, artifact storage.
- Implement the parallel-runner harness (terminal-per-bucket workers per
  user's preference, with per-item timeout) so Roles 3, 4, 9 can all
  share infrastructure.
- Audit the team's reproducibility story: pin solver versions, store proof
  logs, version graph6 files by SHA.

### Role 7 — Immersion / chromatic-index / multigraph (v4 — **R5a lead**)

- **Week 1**: D3 — faithful reconstruction of FPS Claim 3.7 with the
  binding inequality in Case 2b isolated. **Done** —
  `deliverables/D3_R5a_reconstruction.md`.
- **Month 1**: deliver the **R5a Claim 3.7 verdict** (see Track B
  milestone). The PI expects either (i) a candidate improvement $c < 9/16$,
  (ii) an obstruction note that $9/16$ is genuinely binding, or (iii) a
  written escalation request to Role 8 for probabilistic verification.
- **Month 3+**: if (i), draft the improvement. If (ii), draft the
  obstruction note (still publishable). If (iii), hand off and pivot to
  R5 secondary work (Shannon/Vizing refinements).
- **De-prioritized in v4**: the v3 §C7 immersion-witness pipeline. The
  PI considers this **SE at best** (per D10) and prefers the R5a budget.

### Role 8 — Probabilistic / topological combinatorics

- Implement v3 §C4 (`crossing_lemma_refinement.py`): empirical measurement
  of the Crossing Lemma slack for random $t$-critical graphs at small $t$.
- Read Pach–Tóth and follow-ups on minimum-degree-aware Crossing Lemma
  variants; produce a written attack plan for R2c. Deliverable: 5-page
  attack plan circulated to the team.
- Start scoping R3.5 ($k$-planar Albertson) in parallel.

### Role 9 — SDP / flag algebra / numerical certification (v4 — demoted)

- **Per v4 PI directive**: do not spend Role 9 effort on finite $cr(K_{25})$
  lower bounds unless the objective is falsification. Role 9 is off the
  positive-proof critical path.
- **Month 3**: ship the BLS / de Klerk literature audit (extractable
  finite constants at $t = 25, 26$ or "not extractable; SDP rounding from
  scratch required"). Single written deliverable; no compute.
- **Month 3+**: rational-SOS rounding work is parked until and unless
  Role 1 escalates outcome (e) (falsification) as a priority. Default
  assumption is that it remains parked.
- **Standing**: the v3 §C6 two-column finite-vs-asymptotic table is still
  shipped, in publishable form, for future-reference value.

---

## Closing notes (PI, v4)

This document is the contract. The roadmap is `docs/plan.md` **v4**; the
audit that prompted v4 is `docs/review_v3.md`. This document tells the team
*who does what and what counts as success*.

The biggest single piece of v4 honesty: **outcome (b) ("close $t = 25$") is
removed.** It was always low-probability; the compute-team consensus
(Roles 3/4/5/6) is that it is infeasible in 1 cluster-year. Track A is now
bounded subfamily certification + counterexample hunt. The real 12-month
target is **R5a in Track B** (re-derive FPS Claim 3.7, isolate Case 2b,
attempt $c < 9/16$).

The single most important *positive* finding from week 1: Role 7's D3
reconstruction identified the binding inequality in Case 2b as
$\gamma \le \delta / 2 = 9/16$ at the boundary $\alpha = 0, \beta = 0$,
which **cannot be improved by sharpening multiplicity machinery** — only by
lowering $\delta$ (the FPS degree threshold) or replacing Vizing–Gupta. The
next experiment is a ~1-hour SymPy re-derivation with $\delta$ as a free
parameter; binary outcome (free improvement to $11/20$, or $\delta = 9/8$
is locally optimal). This is the highest-leverage local calculation in the
whole plan, and it is now scoped to one decision-log entry on 2026-05-23.
