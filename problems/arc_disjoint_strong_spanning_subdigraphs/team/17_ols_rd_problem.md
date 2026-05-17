# 17 — OLS round-decomposition notebook (side problem, frozen)

Author: Lead Digraph Theorist, 2026-05-16
Status: **side notebook, not the main route.** The OLS structural
characterization is a 28-year open problem (Bang-Jensen–Gutin 1998
Problem 6.8); the team has chosen to pivot Route B to $(1,0)$-near-split
rather than attempt it. This file records the state of OLS for any
future revisit.

## 1. What happened

Phase 4's Structural Specialist deliverable `team/14_route_b_ols_extraction.md`
proved a clean two-case lifting argument for an OLS theorem **conditional
on a "Theorem RD" round-decomposition theorem for OLS digraphs.**

The Auditor's `team/05_audit.md` Appendix A.6 found three independent
problems with Theorem RD:

1. **Phantom journal citation.** "Bang-Jensen–Huang 1995, *J. Comb.
   Theory B* 63, 261–276" — those pages are a different paper
   (Bang-Jensen–Manoussakis on bipartite tournaments). Huang's 1995
   single-author paper on local tournaments is at pp. 200–221 and is
   **two-sided** local.
2. **Misnumbered textbook citation.** Bang-Jensen–Gutin 2009 §5.6.1
   (in the textbook *Digraphs: Theory, Algorithms and Applications*,
   2nd ed.) is a Chvátal–Erdős Hamiltonicity result, not a round
   decomposition. The round-decomposition material is in §4.11 and
   is **explicitly for two-sided LS only**.
3. **Result claimed as published is actually a published open
   problem.** Bang-Jensen–Gutin 1998 survey *Generalizations of
   tournaments* poses **Problem 6.8**: "Find a non-trivial structural
   characterization of locally in-semicomplete digraphs" (the dual of
   OLS, mathematically equivalent via arc-reversal). Still unresolved
   as of 2026.

## 2. The actual published state of round decomposition for one-sided LS

- **Two-sided LS:** Bang-Jensen 1990 (*J. Graph Theory* 14, 371–390)
  defined LS digraphs. Huang 1995 (*J. Comb. Theory B*, single-author)
  gave the structural characterization for LS, finalized in Bang-Jensen–
  Guo 2004. BJG 2009 textbook §4.11 is the canonical reference.
- **One-sided (OLS / ILS):** BJG 2009 §4.10 (Locally in-/out-
  semicomplete digraphs) gives only weak strong-component-level
  structure (Theorem 4.10.4). No round decomposition.
- **Open problem.** BJ–Gutin 1998 survey Problem 6.8 explicitly asks
  for a structural characterization. 28 years open.

## 3. The dependency chain in `team/14_*` that the citation failure broke

`team/14_*` §1.2 → §3 (proof of OLS-SAD theorem) uses Theorem RD in
the inductive-step case analysis, specifically the "alternating case"
which assumes the round structure splits into mixed-direction round
components. The argument needs to know:

- $D$ admits a partition $V = C_1 \sqcup C_2 \sqcup \cdots \sqcup C_p$
  with $D[C_i]$ semicomplete;
- inter-component arcs go between consecutive components only;
- some consistent forward/backward direction structure across the
  cycle.

These are exactly the conditions Theorem RD provides — and they are
not derivable from the published OLS results (§5.6 strong-component
structure is too weak).

## 4. Salvageable ideas from `team/14_*` if OLS is ever attacked

The Structural Specialist's proof in `team/14_*` is not all wasted. Two
specific pieces are worth keeping for any future attack on Problem 6.8
or its OLS dual:

1. **Contiguous-block partition along two switch positions.** §3.3 of
   `team/14_*` introduces a partition strategy that bypasses the naive
   "remove one round component" failure mode (which the Coder
   independently identified in `team/15_*`). The partition picks two
   "switch positions" where the alternating direction changes, then
   takes the contiguous block between them as $V_1$. If an OLS round
   decomposition is ever proved, this partition is the right CL1 input.
2. **Round-cyclic vs. alternating case split.** §3.1 vs. §3.3
   distinguishes two regimes: round-cyclic (reduces to BJG–Yeo 2020
   directly via composition) and alternating (needs CL1 + the
   contiguous-block partition). This is OLS-specific and may extend.

## 5. Why we are not attempting Problem 6.8 as the main route

The user's 2026-05-16 pivot directive made this explicit:

> The OLS round-decomposition citation failure is not a nuisance; it
> destroys Route B's foundation. The "OLS round decomposition" is not
> an uncited lemma waiting to be written up. It is essentially Bang-
> Jensen–Gutin Problem 6.8, a long-open structural characterization
> problem for one-sided locally semicomplete digraphs. Building the SAD
> project on top of that is reckless.
>
> Option A is intellectually attractive but strategically wrong. The
> current project is strong arc decompositions under high arc-
> connectivity, not the resolution of a 28-year-old open structure
> problem.

## 6. Freeze conditions

The OLS branch is frozen unless one of the following materializes:

- A **counterexample** to OLS round decomposition (would close Problem
  6.8 in the negative, and reshape the SAD landscape for one-sided
  classes — itself publishable).
- A **genuinely new structural lemma** weaker than full Problem 6.8
  but sufficient for CL1 (i.e., enough structure to enable the
  contiguous-block partition without requiring the full round
  decomposition).

If either appears, this file is the starting point for a Phase 4.5
side investigation. Until then, no main-budget effort goes here.

## 7. Pointers

- Phantom-citation evidence: `team/05_audit.md` Appendix A.6
- Auditor's PDFs (saved): `/tmp/bjguo_classif.pdf`, `/tmp/bjg_book.pdf`,
  `/tmp/bjg_survey.pdf`
- Blocked OLS proof: `team/14_route_b_ols_extraction.md` (header notice)
- Empirical Route B sweep (OLS digraphs, 355 SAT, 0 UNSAT, all confirm
  the OLS theorem is empirically true): `team/15_v6_ols_empirical.md`
- Novelty audit (Route B headline NOVEL conditional on Theorem RD):
  `team/16_ols_novelty_check.md`
- Memory: `feedback_citation_verification.md` — agent-produced citations
  in proofs require independent Crossref / MathSciNet verification
