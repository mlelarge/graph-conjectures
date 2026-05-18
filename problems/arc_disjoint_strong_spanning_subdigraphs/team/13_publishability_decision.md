# 13 — Publishability decision memo

Author: Lead Digraph Theorist
Date: 2026-05-16
Status: decision memo, written before the Auditor's novelty verdict
returns. The recommendation in §3 is therefore **branched** on that
verdict. The Coder, Structural Specialist, Probabilist and Auditor are
the audience.

Companions: `team/01_lead_theorist_charter.md` (the four-scenario
charter from round 1), `team/02_structural_program.md` (class
roster), `team/04_ec_log_proof.md` (the proved Eulerian log-arc-
strong lemma), `team/08_phase4_lifting_lemma_v1.md` (CL1 v1 and the
identified gap), `team/10_phase4_vehicle6.md` (V6 empirical sweep),
`team/11_cl1_proof_v1.md` (CL1 R2-cleaned form, proved).

No mathematics is restated below. Lemma content lives in `team/02`,
`team/04`, `team/08`, `team/11`. This file is operational.

---

## §1 — State of the project at decision time

The team holds: (i) a proved bilateral lifting lemma CL1 (R2 form,
`team/11`), reduced to two hypotheses, §3-gap closed; (ii) a proved
EC-log lemma at $C = 6$, $n_0 = 3$ (`team/04`, post-2026-05-18 correction; the prior headline $C = 5$, $n_0 = 2$ had an arithmetic gap surfaced in `CORRECTNESS_REVIEW_2026_05_18.md` §2.5), with documented
bounded-defect extension; (iii) ~9 200 verified 3-arc-strong search
instances across Phase 3 vehicles 1–5 and Phase 4 Vehicle 6, **zero
UNSAT** and zero ILP/SAT disagreements; (iv) verifier with `pynauty`
canonicalization, cross-solver agreement, mandatory witness logging;
(v) self-testing SAD-decomposable inner-part library (10 families);
(vi) 56 + 2 471 logged SAT witnesses with canonical hashes and
per-instance pattern records. **No counterexample, no class-level
positive theorem.** CL1 is a tool not yet applied. The Auditor's
novelty verdict on CL1 is in flight and gates everything below.

## §2 — The three candidate publication routes

### Route A — CL1 standalone

**Publishable statement.** The R2-cleaned form in `team/11` §5.1
(bilateral lifting under SAD-decomposable parts plus a bridge
2-coloring with each (direction, color) class non-empty), plus V6
empirical validation (2 471 SAT witnesses, no failures) as numerical
support and the biconditional form of `team/11` §6.2 as a stronger
headline if it survives the Auditor.

- **Length / venue.** 6–12 pp. J. Graph Theory or Discrete Math.
  Neither Combinatorica nor JCTB will accept a tool-only short note
  without a class application.
- **Primary owner.** Structural Specialist (lemma write-up); Coder
  (empirical sweep as supplement); Auditor (novelty letter).
- **Riskiest sub-task.** Novelty defense. The Auditor's verdict on CL1
  vs. BJ–Wang Lemma 2.4 and BJ–Yeo 2004 §3 "good pair" is the single
  load-bearing item. Everything else is straightforward write-up.
- **Time to draft.** 3–6 weeks, conditional on a NOVEL verdict.
- **Realistic risk we are buying.** Even with NOVEL, a referee may
  read CL1 as "a class-agnostic restatement of an existing lemma"
  (the Structural Specialist's own framing in `team/11` §4.5) and
  reject with "interesting but no application."

### Route B — CL1 + class application

**Publishable statement.** CL1 (R2 form) + a strong-arc-decomposition
theorem for a new class $\mathcal{C}$, derived via CL1. The
publishable form must be sharp: not "CL1 applies to $\mathcal{C}$"
but "every 3-arc-strong $D \in \mathcal{C}$ admits a strong arc
decomposition, modulo a finite list of obstructions $\{E_1, \dots,
E_k\}$." The class is chosen in §4 below.

- **Length / venue.** 15–25 pp. JCTB if the class application is
  genuinely new and the obstruction list is finite; J. Graph Theory
  otherwise. The charter (`team/01` §1.b1) lists JCTB as the target.
- **Primary owner.** Structural Specialist (the class application is
  research, not write-up); Coder (V6-style empirical sweep on the
  chosen class); Auditor (verifies class application's novelty
  against BJ–Huang 2012 for ILS/OLS, against BJ–Wang 2025 for
  near-split).
- **Riskiest sub-task.** The class application itself. CL1 gives
  the lifting step; we still need to *find a kernel* inside an
  arbitrary $D \in \mathcal{C}$ that induces a SAD-decomposable
  sub-digraph with bridges admitting the required 2-coloring. **T3**
  in `team/02` §1 flags this as the real obstacle; no shortcut.
- **Time to draft.** 3–6 months. The 6-week tripwire in `team/01` §5
  applies: if no Phase-1 progress on the class application appears
  by mid-July, we re-evaluate.
- **Realistic risk we are buying.** One of the candidate classes
  may already be solved (Auditor closed quasi-transitive in round 1;
  others are flagged but unverified). If the chosen class is
  solved, we burn 6 weeks. The §4 selection is gated on the
  Auditor's class-novelty check (deliverable `team/16_*`).

### Route C — CL1 + EC-log + class application

**Publishable statement.** The bundle: CL1 (R2 form), EC-log at
$C = 6$ (post-2026-05-18 correction; see `CORRECTNESS_REVIEW_2026_05_18.md` §2.5) with the bounded-defect extension of `team/04` §4(c), and the
Route-B class application — but now the application also handles the
high-bridge-multiplicity regime probabilistically via EC-log. The
charter (`team/01` §1.a) reserves Combinatorica for the full WC3
proof; we are *not* claiming WC3, so we cannot use the §1.a slot. The
honest Combinatorica pitch is "two structural results plus a class
theorem unified by the bridge-coloring technique."

- **Length / venue.** 25–40 pp. Combinatorica is the only target
  that justifies the bundling; if the package is judged a step below
  Combinatorica quality, the team should split it into a Route-A
  short note plus a Route-B paper rather than aim mid-tier.
- **Primary owner.** Lead (bundling); Structural Specialist (class
  application); Probabilist (EC-log integration, including the
  probabilistic CL1 conjectured in `team/11` §6.3 P1); Auditor
  (cross-novelty audit).
- **Riskiest sub-task.** The probabilistic-CL1 lift of `team/11` §6.3
  P1. We have no proof that a uniform random bridge coloring with
  $|B^\pm| \geq C \log n$ satisfies CL1's hypothesis (2) w.h.p.;
  this is conjectured but not started. If it fails, EC-log and CL1
  remain two parallel papers rather than one Combinatorica bundle.
- **Time to draft.** 6–12 months. The Probabilist is currently on
  watch, not active.
- **Realistic risk we are buying.** Two independent risks compound
  (class application + EC-log–CL1 integration); the joint success
  probability does not justify the time horizon over Route B.

### Tabulated summary

| Route | Headline | Venue | Owner | Top risk | Time |
|---|---|---|---|---|---|
| A | CL1 standalone | J. Graph Theory / Discrete Math. | Struct. Spec. | Auditor verdict on novelty | 3–6 wk |
| B | CL1 + new class theorem | JCTB | Struct. Spec. | Class application stalls at kernel-extraction | 3–6 mo |
| C | CL1 + EC-log + class theorem | Combinatorica | Lead / Probabilist | Probabilistic CL1 unproven | 6–12 mo |

## §3 — Decision matrix gated on Auditor verdict

The Auditor is checking CL1 (R2 form) against (a) BJ–Wang 2025 Lemma
2.4, (b) BJ–Yeo 2004 §3 "good pair" construction, (c) BJG–Yeo 2020
composition theorem, (d) BJ–Huang 2012 locally semicomplete
classification. The four possible verdicts and the recommendation in
each:

| Auditor verdict | Route | Justification |
|---|---|---|
| **NOVEL** | **B**, with **A** as a fallback short note if the class application stalls past the 6-week tripwire | NOVEL means CL1 is a genuinely new lemma in the literature. Route B is the highest-EV option: it earns JCTB tier on the back of a class theorem with CL1 as the engine, and the 6-week tripwire bounds downside. Route A is the safety net: if the class application fails, we still have a publishable short note. We do *not* go to C from NOVEL alone — C demands a separate probabilistic result that has not been started. |
| **DERIVATIVE-OF-X** (CL1 is a corollary of a known result $X$) | **B**, but reframed: CL1 is no longer the headline; the class theorem is the headline and CL1 is presented as an instance of $X$ specialized to the bilateral case | The class application still has value: it is the first systematic use of bilateral lifting in class $\mathcal{C}$. The paper becomes "Strong arc decompositions of 3-arc-strong $\mathcal{C}$-digraphs," with the bilateral-lift step credited to $X$. Venue drops one tier (J. Graph Theory rather than JCTB) because the engine is not new. Route A is dead in this branch. |
| **EQUIVALENT-TO-Y** (CL1 is the same statement as a known result $Y$ up to relabeling) | **B**, but only if the chosen class is **not** already solved by $Y$'s standard application; otherwise abort and reallocate to Phase 3 / Phase 5 | EQUIVALENT-TO-Y collapses Routes A and C's CL1-headline entirely. The class application becomes the *only* publishable artifact, and only if $Y$ + its known applications do not already cover the chosen class. If they do, we have no novel content and must redirect: charter (`team/01`) §5 Phase 3 tripwire applies, and the team reallocates to Track B (counterexample search) until a fresh angle appears. |
| **CANNOT-DETERMINE** | **A** as a "registration" short note (5–8 pp, framing CL1 as a clean restatement worth recording) **in parallel with** Route B work | CANNOT-DETERMINE is the realistic verdict given the literature's sparse explicit statements and the Auditor's limited bibliographic access. We do not let it block publication: we send the short note to a workshop or arXiv as a *registration*, then proceed with Route B as if NOVEL. The short note is low-cost insurance against priority loss. If the Auditor later resolves to EQUIVALENT-TO-Y, the registration is withdrawn or footnoted; if NOVEL, the registration becomes the J. Graph Theory paper. |

**Pessimistic prior on the verdicts.** Reading `team/11` §4.5–§6.3
and `team/02` §1: CANNOT-DETERMINE most likely (~50 %), DERIVATIVE
~30 %, EQUIVALENT ~15 %, NOVEL ~5 %. The Structural Specialist's
own §4.5 calls CL1 "at most a class-agnostic restatement of BJ–Wang
Lemma 2.4," which is a DERIVATIVE self-assessment. Plan for the
DERIVATIVE / CANNOT-DETERMINE branches and treat NOVEL as a bonus.

## §4 — Choice of candidate class for Routes B and C

The class roster from `team/02` §3 ranks five candidates. The Lead's
selection for Route B (and Route C if it is later promoted) is:

**Out-locally semicomplete (OLS) digraphs.**

Justification:

1. **Kernel comes for free.** Strong OLS digraphs admit a round
   decomposition (BJ–Huang 1995 / Huang 1995); each component is
   semicomplete, hence SAD-decomposable via BJG–Yeo 2020. Pick any
   component as CL1's kernel $V_2$; the remainder $V_1$ inherits
   in-degree $\geq 3$ from 3-arc-strongness. **The structural
   ingredient CL1 needs is already a theorem.**
2. **Strictly beyond BJ–Huang 2012.** Locally semicomplete (both-
   sided) is classified by BJ–Huang 2012; OLS strictly contains LS
   and the BJ–Huang argument does not port to OLS. A 3-arc-strong-
   OLS theorem is genuinely new content if proved.
3. **Verifier reach adequate.** OLS digraphs of order $\leq 8$
   enumerable in days via the existing `pynauty` stack; the
   inner-part library already contains $K_n^*$ and $QR_p$, both
   extremal OLS instances.
4. **Lineage precedent.** BJ–Yeo 2004 (semicomplete) and BJ–Wang
   2025 (split) both used kernel-plus-shell decompositions that CL1
   abstracts. OLS is the cleanest next step in the same line.

We pass on the alternatives. **In-locally semicomplete (ILS)** would
be a symmetric option; we prefer OLS because the round
decomposition's *out*-side is the side that interacts naturally with
out-arborescences, which is the half of CL1's branching argument
(`team/11` §3 Steps 3 and 5) that does the load-bearing work. We
will not pursue both ILS and OLS in parallel; if OLS settles
cleanly, the ILS theorem follows by reversal and is a corollary, not
a separate paper.

**$(k,0)$-near-split digraphs** (rank 2 in `team/02` §3) is the
fallback. If the OLS kernel-extraction stalls at the 6-week
tripwire, the Structural Specialist switches to $(1,0)$-near-split
with the parametric extension explicitly written into the paper
title.

**Bounded independence number** (rank 4) is on hold: the kernel
extraction is exploratory and the path to a publishable theorem is
not visible.

The precise Route-B target statement is therefore:

> Every 3-arc-strong out-locally-semicomplete digraph admits a
> strong arc decomposition, modulo the exception family inherited
> from BJG–Yeo 2020's semicomplete-composition obstructions
> ($S_4$, $\vec C_3[\overline K_2^3]$, $\vec C_3[\overline K_2,
> \overline K_2, P_2]$, $\vec C_3[\overline K_2, \overline K_2,
> \overline K_3]$) when they appear as the round-component kernel.

This is the §4-anchored "specific decision" the prompt's operational
rule demands.

## §5 — Next agent assignments (Route B post-audit)

Assuming the Auditor returns NOVEL or CANNOT-DETERMINE (the latter
treated as effectively NOVEL per §3), Route B begins immediately.
Specifically:

- **Structural Specialist.** Deliver `team/14_route_b_ols_extraction.md`
  by 2026-06-27 (6 weeks from today). Content: extraction of the
  CL1 kernel from the OLS round decomposition; proof or disproof that
  every 3-arc-strong OLS digraph has a round component whose
  complement satisfies CL1's hypothesis (1) on the remainder; explicit
  handling of the BJG–Yeo composition exceptions when they appear as
  the kernel.

- **Coder.** Deliver `team/15_v6_ols_empirical.md` by 2026-06-13
  (4 weeks from today). Content: V6-style empirical sweep restricted
  to 3-arc-strong OLS digraphs at $n \leq 10$; verify zero UNSAT;
  pattern-check CL1's bridge 2-coloring satisfiability on the
  round-decomposition kernel choice. The library
  `code/generators/sad_inner_parts.py` is reused; a new enumerator
  `code/generators/ols_digraphs.py` is needed.

- **Auditor.** Deliver `team/16_ols_novelty_check.md` by 2026-06-06
  (3 weeks). Content: literature check for prior strong-arc-
  decomposition results on OLS digraphs. Specifically: does
  Bang-Jensen–Huang 1995, Huang 1995, or any subsequent paper
  contain a strong-arc-decomposition theorem for OLS or for any
  superclass that subsumes 3-arc-strong OLS? This is the analogue
  of the round-1 quasi-transitive absorption check.

- **Probabilist.** **On watch.** No new deliverable unless EC-log
  needs revision or Route C is promoted. The Probabilist is asked
  to keep `team/11` §6.3 P1 (probabilistic CL1 at $|B^\pm| \geq
  C \log n$) in their thinking queue but not to start work on it
  until Route B's class application clears the 6-week tripwire.

- **Lead.** Weekly Monday status. Decision review at 2026-06-27
  on whether Route B is converging or whether to fall back to
  $(1,0)$-near-split or to Route A as a registration note.

Deliverable filenames are committed: `team/14_*`, `team/15_*`,
`team/16_*`. Slipping these by more than a week without a written
status note is a tripwire (§6).

## §6 — Tripwires for re-evaluation

The decision in §3–§5 is provisional. We revisit when any of the
following fires:

1. **Route B stall.** If `team/14_route_b_ols_extraction.md` does not
   show *Phase 1 progress* (a precise statement of which step of CL1
   extraction is the obstruction, with a concrete sub-conjecture to
   attack) by 2026-06-27, the Lead convenes a re-plan. Options:
   (a) switch to $(1,0)$-near-split, (b) demote to Route A as a
   short note, (c) reallocate to Phase 3 counterexample search.
2. **3-arc-strong UNSAT discovery.** If any V6, Phase-3, or OLS
   sweep produces a 3-arc-strong digraph for which both ILP and SAT
   verifiers return UNSAT with cross-solver agreement, **all routes
   above are paused** and the team executes the counterexample
   protocol (`team/01` §3 checklist; charter scenario (c) or (d)).
   Route W (counterexample write-up) overrides A, B, C.
3. **EC-log retraction or sharpening.** If the Probabilist or Auditor
   identifies a flaw in `team/04`'s proof, Route C is dead until
   repaired; Routes A and B are unaffected. Conversely, if EC-log is
   sharpened to a structural-cut-laminar form (the Phase 5 target in
   `team/01` §2), Route C is *promoted* and a fresh §3 decision matrix
   is drawn.
4. **Auditor verdict revision.** If the Auditor returns
   CANNOT-DETERMINE and later upgrades to EQUIVALENT-TO-Y (e.g. on a
   second-pass literature review), the registration short note (§3
   CANNOT-DETERMINE row) is withdrawn within 1 week of the revised
   verdict.
5. **Global 6-month tripwire (charter §5).** If at 2026-11-16 no
   draft of any of A, B, C is started, the Lead rewrites the §2
   budget from scratch.

The default policy is: re-read this memo at every Friday cadence
(`team/01` §4), and replace it with a `team/13_v2_*` only on a §6
fire. Otherwise the decision stands.

---

**Cover paragraph.** We cannot write a Combinatorica paper. We can
write a J. Graph Theory short note now (Route A) or a JCTB paper in
3–6 months (Route B), conditional on the Auditor. The Lead's call is
Route B with OLS as target, running a Route-A registration note in
parallel iff the Auditor returns CANNOT-DETERMINE. Route C is a
promotion path, not the active plan. §3 is the authoritative
branching rule; §4's OLS choice is load-bearing; §5's deliverables
are committed.

---

## §7 — Amendment 2026-05-16: Route B pivots to $(1,0)$-near-split

§4's "OLS as target" choice was load-bearing on a Theorem RD citation
that does not exist as a published result. The Auditor's
`team/05_audit.md` Appendix A.6 found three independent failures (a
phantom journal citation, a misnumbered textbook theorem, and a result
claimed as published that is in fact Bang-Jensen–Gutin 1998
**Problem 6.8** — a 28-year open structural characterization
problem). The OLS round-decomposition this proof requires is not an
unwritten lemma; it is essentially Problem 6.8 itself.

**Lead's amended call.** Route B pivots to the **$(1,0)$-near-split**
class (`team/02_structural_program.md` §3 rank-2 fallback). The
amended headline:

> *Every 3-arc-strong $(1,0)$-near-split digraph admits a strong arc
> decomposition.*

A $(1,0)$-near-split digraph has $V = V_1 \dot\cup V_2$ with $V_2$
inducing a semicomplete digraph, arcs between $V_1$ and $V_2$
unrestricted, and **exactly one arc inside $V_1$** (otherwise $V_1$
independent). This is the smallest perturbation of the split-digraph
class for which the BJ–Wang 2025 / Ai et al. 2024 toolkit may not
directly apply.

**Why this is the right pivot.** (1) Explicit semicomplete core, so
CL1's hypothesis (1) on $V_2$ comes from BJ–Yeo 2004 + BJG–Yeo 2020
modulo a finite exception list. (2) Non-core side is tiny and
controlled. (3) Bang-Jensen–Wang split methods are directly relevant
as a baseline. (4) The verifier can enumerate $n \leq 10$ exhaustively.
(5) Plausibly new but does not require solving a 28-year-old structure
problem first.

**OLS is preserved as a side notebook**, not the main line; see
`team/17_ols_rd_problem.md`. No main-budget effort goes to OLS round
decomposition until either a counterexample to it appears or a new
structural lemma weaker than full Problem 6.8 but sufficient for CL1
emerges.

**Amended §5 deliverables, agents reassigned:**

| File | Owner | Successor of |
|---|---|---|
| `team/18_near_split_novelty.md` | Auditor | `team/16_*` (OLS-specific novelty) |
| `team/19_near_split_extraction.md` | Structural Specialist | `team/14_*` (blocked) |
| `team/20_near_split_empirical.md` + `code/generators/near_split.py` | Coder | `team/15_*` (OLS-specific) |
| `team/17_ols_rd_problem.md` | Lead (this file) | n/a, side notebook |

**Decision matrix from §3 still applies** with "Route B" now meaning
the $(1,0)$-near-split application. Auditor verdict on near-split
novelty (in `team/18_*`) gates the publication framing exactly as the
OLS verdict gated it before.

**Tripwire from §6.1** carries over: if `team/19_*` does not produce
a working proof of the amended headline by 2026-06-27, Route B
re-pivots (to $(2,0)$-near-split, bounded-independence-number
digraphs, or a different class — to be decided then).

**OLS as a future option.** If the team ever wants to revisit
Problem 6.8 as a major undertaking (Combinatorica-tier if resolved),
the existing `team/14_*` and `team/17_*` are the starting points. It
is no longer the load-bearing route for *this* project, but a
publishable side-quest if a path opens.
