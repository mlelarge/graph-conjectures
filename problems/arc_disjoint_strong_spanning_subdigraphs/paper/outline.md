# Paper outline

**Working title.** *Strong arc decompositions of near-split and Eulerian digraphs*

**Author / corresponding author.** (Team)

**Date of outline.** 2026-05-17

**Status.** Outline accompanying the v1 full draft (`draft_v1.md`).

---

## 1. Headline theorem

> **Theorem (Main).** *Conditional on Conjecture L (see §6 of the paper),
> every simple 3-arc-strong $(1,0)$-near-split digraph $D$ on $|V_1| \ge 2$,
> $|V_2| \ge 3$ admits a strong arc decomposition.*

In particular this resolves, conditional on a single finite-combinatorial
statement about pairs of arc-disjoint in-arborescences, the
Bang-Jensen–Yeo strong-arc-decomposition problem for the smallest non-trivial
extension of the split class beyond Bang-Jensen–Wang (J. Graph Theory, 2025)
and Ai–He–Li–Qin–Wang (2024).

Conjecture L is itself an open structural statement about subtree inclusion
between two arc-disjoint spanning in-arborescences with a common root; it is
not a special case of any published result (cf. paper §6).

## 2. Unconditional partial results

Three unconditional results are proved as standalone lemmas of independent
interest.

**Theorem A (EC-log).** *Let $C = 6$ and $n_0 = 3$. Every Eulerian digraph
$D$ on $n \ge n_0$ vertices with $\lambda^{\mathrm{arc}}(D) \ge C \log_2 n$
admits a strong arc decomposition.* Proof: Eulerian-to-undirected reduction,
Karger cut-counting, first moment. Self-contained.
*(Edit 2026-05-18: constants updated from $C = 5$, $n_0 = 2$, per
`CORRECTNESS_REVIEW_2026_05_18.md` §2.5; the $5\log_2 n > 4\log_2 n + 3$
step needs $n \ge 9$, not $n \ge 4$.)*

**Theorem B (CL1, bilateral lifting).** *Let $D = (V, A)$ be a digraph with
$V = V_1 \mathbin{\dot\cup} V_2$, $|V_i| \ge 2$. Suppose (1) each $D[V_i]$
admits a strong arc decomposition $(R_i, B_i)$, and (2) the bridge sets
$B^+ = \delta_D^+(V_1)$, $B^- = \delta_D^+(V_2)$ admit a partition
$B^\pm = B^\pm_R \mathbin{\dot\cup} B^\pm_B$ with all four pieces
$B^+_R, B^+_B, B^-_R, B^-_B$ non-empty. Then $D$ admits a strong arc
decomposition.* Novel relative to Bang-Jensen–Wang Lemma 2.4 in being
**bilateral** (both parts SAD-decomposable, not one part shell of
independent vertices). Audit-verified.

**Theorem C (R3⋆-KS, kernel-shell side-compatible SAD).** *Let $D$ be a
simple 3-arc-strong $(1,0)$-near-split digraph with $|V_2| \ge 3$, and let
$D^\bullet$ be the chord contraction. If $D^\bullet \langle V_2 \rangle$
admits a strong arc decomposition, then so does $D$.* This is an
unconditional sub-case of the main theorem; it cleanly handles every
$(1,0)$-near-split digraph whose semicomplete part is itself
SAD-decomposable, which covers the asymptotically dominant regime
($|V_2| \ge 5$ with $\lambda(D \langle V_2 \rangle) \ge 2$).

## 3. Section structure and target word counts

| § | Title | Target words |
|---|-------|----:|
| 1 | Introduction (problem, lineage, statement of main results) | 1 200 |
| 2 | Preliminaries (definitions, Edmonds, BJ–Wang Lemma 2.4) | 900 |
| 3 | EC-log: a probabilistic SAD theorem | 1 200 |
| 4 | The bilateral lifting lemma CL1 | 1 200 |
| 5 | The $(1, 0)$-near-split theorem (Theorem A) | 4 200 |
| 5.1 | Setup, contraction, side labels | 700 |
| 5.2 | The kernel-shell case (R3⋆-KS) | 1 200 |
| 5.3 | The hard case (R3⋆-HC) and RECOLOR | 1 800 |
| 5.4 | Theorem 3 (conditional on Conjecture L) | 500 |
| 6 | Conjecture L | 1 100 |
| 7 | Computational catalogue | 600 |
| 8 | Open problems | 500 |
| References | (audit-cleared only) | 200 |

**Total target.** ~11 000 words including the bibliography. Target window
8 000–15 000; we plan inside that envelope with concision in §§3, 4.

## 4. Venue decision

**Recommendation.** Submit to **J. Graph Theory**.

**Why J. Graph Theory rather than J. Combin. Theory Ser. B.**

- The main result is *conditional* on a named, open structural conjecture
  (Conjecture L). JCTB is unlikely to accept a conditional headline as the
  main contribution; J. Graph Theory routinely publishes
  conditional-on-named-conjecture papers and structural lemmas as standalone
  results.
- Two of the three unconditional results (Theorem A on Eulerian digraphs,
  Theorem B on bilateral lifting) are of independent interest and would
  individually merit J. Graph Theory short-notes; the combined paper is the
  natural amalgamation. The lineage is firmly in J. Graph Theory
  (Bang-Jensen–Wang 2025 in J. Graph Theory 108, 5–26; Bang-Jensen–Gutin–Yeo
  2020 in J. Graph Theory 95, 267–289), making it the home venue.
- Bang-Jensen–Wang 2025 published their split-digraph result in
  J. Graph Theory; their result is the immediate predecessor and the most
  cited comparand.
- Length budget at ~11 000 words including references fits J. Graph Theory's
  typical paper length comfortably.

**Fallback if J. Graph Theory rejects.** Discrete Mathematics or Disc. Appl.
Math.; both are appropriate. We do not aim for J. Combin. Theory Ser. B with
a conditional headline.

## 5. Order of section emphasis

The paper builds three independent unconditional engines (§§3, 4) before
the conditional headline (§5). The engines are short and self-contained
relative to the main theorem.

**Loading priority for an editor / referee skim.** §1 (introduction and
statement) → §5.4 (statement of the conditional main theorem) → §4 (CL1) →
§5.2 (kernel-shell, unconditional) → §6 (Conjecture L). §3 (EC-log) is
self-contained and orthogonal; §5.3 is long but consists of well-flagged
sketch-level technical steps reduced to Conjecture L; §7 is a catalogue.

**Mathematical priority.** Section 5 is the structural core; it depends on
§§2, 4. Section 4 (CL1) is the second-most novel ingredient and reads
independently. Section 3 (EC-log) is fully self-contained.

## 6. Citation discipline (operational note for the author)

All citations route via the audit appendices `team/05_audit.md` A.1–A.13.
No new "by Frank/Bang-Jensen–Gutin/Schrijver Theorem X.Y.Z" invocations.
The audit has caught four such over-attributions in the working notes; the
paper repeats none of them. The full audit-cleared list (~12 sources)
appears in the bibliography of `draft_v1.md`.

## 7. What is deliberately *not* in the paper

- **No claim to a strong arc decomposition for general 3-arc-strong
  digraphs.** That is the Bang-Jensen–Yeo conjecture and remains open at
  every $k \ge 3$.
- **No claim that Conjecture L follows from any classical exchange
  property.** Audit A.12 has verified that Schrijver's exchange property
  (Combinatorica 20, 2000, Theorem 1; Vol. B §53.6) is on different
  hypotheses and does not imply Conjecture L.
- **No claim to a cross-kind branching packing theorem.** The strengthening
  of Thomassen's open Conjecture 2 (existence of one arc-disjoint
  out-branching / in-branching pair at high arc-strength) is not within the
  scope of this paper; the paper's proof uses only within-kind Edmonds
  packings (two clean applications of Edmonds' theorem, no matroid union).
- **No statement of an analogous theorem for out-locally-semicomplete or
  in-locally-semicomplete digraphs.** Bang-Jensen–Gutin 1998 Problem 6.8
  (the structural characterization of one-sided locally-semicomplete
  digraphs) remains open; the OLS/ILS extensions of the Bang-Jensen–Yeo
  problem are listed in the open-problems section but not pursued.
- **No probabilistic CL1.** The natural probabilistic extension of CL1 to
  the high-bridge regime via Karger-style counting is open; flagged in §8.

End of outline.
