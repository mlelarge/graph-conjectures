# Lead Theorist Charter — Round 1

Audience: Structural Specialist, Coder, Probabilist, Auditor. Assumes
`attack_plan.md` v3 and `review.md` v2 are already read.

## 1. WC3 — publishable forms by scenario

The working conjecture is WC3: **every 3-arc-strong digraph has a strong
arc decomposition**. The papers we are committing to depending on outcome:

(a) **WC3 proved in full.** Title: *"Every 3-arc-strong digraph has a strong
arc decomposition."* This settles Bang-Jensen–Yeo with $K=3$. Target:
**Combinatorica** or **JCTB**. Length 30–50 pages. We will not redirect to a
weaker venue.

(b) **WC3 partial.** Two acceptable partial forms, ranked:
  (b1) *Every 3-arc-strong digraph in class $\mathcal{C}$ has a strong arc
       decomposition*, where $\mathcal{C}$ is the new class extracted by the
       Structural Specialist via the controlled-lifting lemma (near-split,
       one-sided locally semicomplete, or bounded independence number).
       Target **JCTB** or **J. Graph Theory**, 15–25 pp.
  (b2) *Every Eulerian digraph with $\lambda \geq C \log n$ has a strong arc
       decomposition* (EC-log, plus whichever sharpening Phase 5 actually
       delivers). Target **J. Graph Theory** or **Discrete Math.**, 6–12 pp.
       EC-log alone is publishable as a short note even with no sharpening.

(c) **WC3 false, finite bad family.** A finite list of 3-arc-strong
    counterexamples certified by independent ILP+SAT runs and audited cores.
    Title: *"A 3-arc-strong digraph without a strong arc decomposition."*
    Target **J. Graph Theory**, 8–15 pp. We *do not* yet claim a new $K$.

(d) **WC3 false, infinite bad family.** Constructive infinite family with a
    parametric tight-cut analysis showing 3-arc-strongness is preserved and
    the obstruction persists, plus an upper bound on what $K$ can possibly
    be. Target **Combinatorica** (the literature's first published lower bound
    above 2), 20–35 pp.

Scenario (a) drives the team's ambitions; scenarios (b1) and (c) are the
realistic median outcomes; (d) is the dream counterexample case.

## 2. Phase priority and budget (post-Phase 2, i.e. after the verifier ships)

| Phase | Effort | Until milestone |
|-------|--------|-----------------|
| 3 — counterexample | 50% | 3 of the 4 Track-B vehicles searched exhaustively at $n \le 16$, or first 3-arc-strong UNSAT confirmed |
| 4 — controlled lifting | 35% | one new class either delivered or formally declared blocked (cf. §5) |
| 5 — Eulerian beyond EC-log | 15% | a *structural* lemma sharpening EC-log appears, not just a probabilistic improvement |

Justifications, terse:

- **50% to Phase 3.** Fastest path to *any* artifact and the only path to
  scenarios (c)/(d). The verifier is dual-use, so Phase 3 effort also exercises
  the infrastructure Phase 4 needs. Lower-bound silence on $K \geq 3$ is the
  single most informative quantity in the field.

- **35% to Phase 4.** Highest expected payoff per page for a positive theorem,
  but slow and lemma-extraction-dependent. Capped below Phase 3 because if
  Bang-Jensen–Wang's argument does not extract cleanly, more bodies do not
  help.

- **15% to Phase 5.** EC-log is on paper in 2 weeks; further Eulerian work is
  high-risk and shares no infrastructure with Phases 3–4. Reserve until
  Phase 3 or 4 produces a structural object Phase 5 can feed on.

Renegotiation triggers: a confirmed 3-arc-strong UNSAT flips Phase 3 to 80%;
a successful class-agnostic lifting lemma flips Phase 4 to 60%.

## 3. Counterexample acceptance checklist

No draft of a (c)/(d) paper starts until **every** item below is signed off
by the Lead and the Auditor:

1. **Independent min-cut.** Recompute $\lambda(D)$ from scratch with a
   max-flow library *outside* the verifier code path. Confirm $\lambda(D)
   \geq 3$.
2. **Simple vs. multi-digraph status declared.** Record whether parallel arcs
   and loops are present; WC3 is normally read for digraphs without 2-cycles
   counting as multi-arcs. State the hypothesis the example refutes.
3. **No 2-arc-strong sub-obstruction trivially explains UNSAT.** Search
   $D$ for an induced sub-digraph isomorphic to a known 2-arc-strong
   obstruction (Ai et al. 2024 split exceptions; BJG–Yeo 2020 four
   semicomplete-composition exceptions; squares of even directed cycles; $S_4$
   and its blow-ups). If one is present, check whether removing/contracting
   it kills UNSAT — if so, the example is not genuinely 3-arc-strong content.
4. **Cross-solver reproducibility.** UNSAT must reproduce on ILP/cut-separation
   **and** on SAT/arborescence-witness independently, with logs.
5. **Unsat core extracted and human-readable.** Auditor must translate the
   core into a laminar/near-laminar family of tight directed cuts and an
   explicit 2-SAT contradiction over color choices. No core, no paper.
6. **Reproducibility seed.** Re-run from a clean checkout with a fresh
   solver instance; same UNSAT, same core (up to symmetry).
7. **Canonical form.** Canonicalize $D$ with `nauty`/Traces; check it is not
   already in our positive-class catalogue (semicomplete, locally semicomplete,
   semicomplete composition, split).
8. **Isolated vs. family.** "Infinite family" requires (i) a parametric
   construction $D_n$, (ii) a proof — not just verifier sweeps — that
   $\lambda(D_n) \geq 3$ for all $n$, (iii) verifier UNSAT for $n$ up to at
   least 4 distinct values past the smallest, (iv) the cut-laminar structure
   stable under the parameter. Anything less is "isolated example(s)".
9. **Minimization.** Run arc-/vertex-deletion minimization and report the
   minimal certified example, not the discovered one.
10. **Negative-result phrasing audit.** If we are reporting a Phase 3
    dead-end instead, the language must match `attack_plan.md`'s rule: explicit
    $N$, explicit family $\mathcal{F}$, no "$f(3) = \infty$".

## 4. Weekly coordination (cadence: Friday end-of-day)

- **Structural Specialist** — 1-page status on lifting-lemma extraction:
  which hypothesis of the BJ–Wang proof is currently the obstruction, which
  candidate class is being tested this week.
- **Coder** — verifier health report: validation-set pass/fail diff vs. last
  week, largest $n$ solved, list of every UNSAT discovered with cross-solver
  status and core size.
- **Probabilist** — EC-log status until written; afterwards, one paragraph
  on Phase 5 progress or "no movement".
- **Auditor** — one consolidated note: open audit items, items closed, any
  claim in last week's reports that did not pass the §3 checklist.
- **Lead (me)** — Monday: priorities for the week and any renegotiation of
  the §2 budget.
- **Shared artifact.** All UNSAT instances and their cores live in a single
  versioned directory; nothing reported in any 1-pager unless its artifact is
  in that directory.

## 5. Tripwires and exit criteria

- **Phase 3.** Stop if Track-B vehicles 1–4 have been searched exhaustively
  at $n \le 14$ and sampled at $n \le 18$ on each of the four vehicles, with
  no 3-arc-strong UNSAT and no UNSAT core localizing a candidate obstruction
  structure. At that point, write the documented negative search report and
  reallocate to Phase 4. Soft warning at $n \le 12$ exhausted with no signal.
- **Phase 4.** Stop if after 6 weeks of focused extraction effort, no
  hypothesis of the BJ–Wang argument generalizes past split structure with
  color-compatibility intact, **and** none of {near-split, one-sided locally
  semicomplete, bounded independence number} shows a working analog of the
  splitting-off admissibility condition. Document the obstruction (which
  step of BJ–Wang refuses to lift) and reallocate.
- **Phase 5.** Stop unless a *structural* lemma emerges — e.g. a bounded-defect
  Eulerian extension proved via a cut-laminar argument, not via a tighter
  Karger/LLL bound. A constant-$C$ Eulerian theorem proved purely
  probabilistically is acceptable; a $\log\log n$ improvement is not.
- **Global tripwire.** If at 6 months none of the four scenarios in §1 has a
  draft started, the Lead convenes a replan and the §2 budget is rewritten
  from scratch.

## 6. What the Lead does not decide

- **Verifier implementation details.** The ILP-first / SAT-second order is
  fixed (per `review.md`), but encoding choices, solver flags, cut-separation
  heuristics, canonicalization library, and generator code are the Coder's.
- **EC-log proof style.** The Probabilist owns the writeup. The Lead only
  requires the bookkeeping noted in `review.md` (factor of 2; first-moment
  finish, no alteration step).
- **Lemma statements inside Track C.** The Structural Specialist names the
  precise hypotheses of the controlled-lifting lemma and chooses which of the
  three candidate classes to push first. The Lead chooses *that* it must be
  one new class, not which one.
- **Audit procedure.** The Auditor sets the format of the checklist
  enforcement and the certificate archive layout, subject to §3 content.
