# Unit vector flows -- literature notes

Companion to [plan.md](plan.md). The goal is to keep verified source facts
separate from strategy and conjectural interpretation.

## Conventions

- **Primary** -- checked directly against arXiv/PDF/DOI text.
- **Secondary** -- paraphrased from a reliable index or summary, still needing
  paper-body verification.
- **Inference** -- a consequence or project interpretation, not a source claim.
- **To verify** -- plausible but not yet checked in the source body.

## Problem statement and disambiguation

- **Primary.** Houdrouge--Miraftab--Morin state Jain's two conjectures as:
  every bridgeless cubic graph has an $S^2$-flow, and there exists a map
  $q:S^2\to\{\pm1,\pm2,\pm3,\pm4\}$ such that antipodal points get opposite
  values and any three equidistant points on a great circle have values
  summing to zero.
- **Primary.** Ulyanov states that if both conjectures were true they would
  imply Tutte's 5-flow conjecture, and gives two counterexamples to the second
  conjecture.
- **Inference.** The live problem is the first conjecture only. Ulyanov does
  not disprove existence of $S^2$-flows on bridgeless graphs.

## Houdrouge--Miraftab--Morin -- 2026

- **Citation.** Hussein Houdrouge, Bobby Miraftab, Pat Morin,
  *2-dimensional unit vector flows*, arXiv:2602.21526v1, submitted
  2026-02-25.
- **Subjects.** math.CO, cs.DM. MSC 05C21, 15A03.
- **Primary abstract facts.**
  - They study nowhere-zero flows assigning unit vectors in $\mathbb{R}^3$.
  - They give a geometric characterization of $S^2$-flows on cubic graphs.
  - They prove the cubic $S^2$-flow class is closed under a natural composition
    operation, including blowing up a vertex into a triangle.
  - Algebraically, if an $S^2$-flow $\varphi$ has
    $\operatorname{rank}(S_\mathbb{Q}(\varphi))\le 2$ and
    $S_\mathbb{Q}(\varphi)$ is odd-coordinate-free, then the graph has a
    nowhere-zero 4-flow.

### Key statements

- **Primary.** Theorem 1: a cubic graph admits an equiangular $S^2$-immersion
  if and only if it admits an $S^2$-flow.
- **Primary.** Observation 9: for unit vectors $v_1,v_2,v_3\in\mathbb{R}^3$,
  $\sum_i v_i=0$ iff the four-point set $\{0,v_1,v_2,v_3\}$ is coplanar and
  every pair of the three unit vectors makes angle $2\pi/3$.
- **Primary.** Lemma 6: after applying their degree-splitting and suppression
  reductions extensively, if the reduced graph has an $A$-flow then the
  original graph has an $A$-flow.
- **Primary.** Theorem 3: if a graph admits an $S^2$-flow satisfying the
  rank/odd-coordinate-free hypothesis above, then it admits a 4-flow.

### Consequences for this project

- **Inference.** HMM's geometric characterization is the right language for
  human-readable positive witnesses.
- **Inference.** Their rank theorem gives a low-complexity obstruction inside
  snarks: a snark cannot have a rank-at-most-2 odd-coordinate-free $S^2$-flow.
  It does not rule out arbitrary $S^2$-flows.
- **To verify.** Exact list of generalized Petersen variants with explicit
  immersions, and exact statement of the graph-injection theorem.

## Ulyanov -- 2026

- **Citation.** Nikolay Ulyanov, *Graph Puzzles II.1: Counterexamples to
  Jain's Second Unit Vector Flows Conjecture*, arXiv:2603.23328v1, submitted
  2026-03-24.
- **Primary abstract facts.**
  - The first Jain conjecture is the $S^2$-flow existence conjecture for
    bridgeless graphs.
  - The second conjecture is the global labeling map
    $S^2\to\{\pm1,\pm2,\pm3,\pm4\}$ with antipodal and triple-sum rules.
  - The paper gives two finite counterexamples to the second conjecture by
    constructing point sets that require values $\{\pm5\}$.
  - Code is linked from the arXiv abstract.

### Counterexample data

- **Primary.** Counterexample 1 uses 25 antipodal representatives, i.e. 50
  points; the SAT instance has 200 variables and 19,765 clauses and is UNSAT
  for labels in $\{\pm1,\ldots,\pm4\}$.
- **Primary.** Counterexample 2 produces a 36-point subset with 13 triples; its
  nonexistence SAT instance for the nz5 labeling has 144 variables and 6,710
  clauses, while an nz6 labeling exists.
- **Primary.** The author reports Lean 4 verification via `bv_decide` in the
  accompanying repository.

### Consequences for this project

- **Inference.** Do not spend effort on the global finite-labeling conjecture
  except as a source of finite point-set obstruction ideas.
- **Inference.** The paper's planned "Graph Puzzles II.2: $S^2$-flows of cubic
  graphs" reference is in preparation in Ulyanov's bibliography; as of the
  checked arXiv page, that is not a cited available paper.

## Mattiolo--Mazzuoccolo--Rajnik--Tabarelli -- 2023

- **Citation.** Davide Mattiolo, Giuseppe Mazzuoccolo, Jozef Rajnik, Gloria
  Tabarelli, *On $d$-dimensional nowhere-zero $r$-flows on a graph*,
  arXiv:2304.14231v1, submitted 2023-04-27.
- **Primary abstract facts.**
  - An $(r,d)$-NZF assigns vectors in $\mathbb{R}^d$ with norm in
    $[1,r-1]$.
  - The $d$-dimensional flow number $\phi_d(G)$ is the least such $r$.
  - For every bridgeless graph, they prove $\phi_2(G)\le 1+\sqrt5$.
  - The oriented 5-cycle double cover conjecture implies
    $\phi_2(G)\le\tau^2$, where $\tau$ is the golden ratio.
  - They propose $\tau^2$ as a plausible upper bound for all bridgeless graphs.

### Project relevance

- **Primary.** They conjecture the Petersen graph has
  $\phi_2(P)=1+\sqrt{7/3}$, and show computational examples including a bound
  for Isaacs' snark $J_5$.
- **Inference.** This is about two-dimensional vector spaces
  ($\mathbb{R}^2$), not directly the unit $S^2\subset\mathbb{R}^3$ case. It is
  relevant for methods and for cycle-cover geometry, not a direct decision
  oracle for Jain's surviving conjecture.

## Mattiolo--Mazzuoccolo--Rajnik--Tabarelli -- 2025

- **Citation.** Davide Mattiolo, Giuseppe Mazzuoccolo, Jozef Rajnik, Gloria
  Tabarelli, *Geometric description of $d$-dimensional flows of a graph*,
  arXiv:2510.19411v1, submitted 2025-10-22.
- **Primary abstract facts.**
  - They give a geometric description of some $d$-dimensional flows.
  - They prove that existence of a suitable cycle double cover is equivalent
    to existence of such a geometrically constructed $(r,d)$-NZF.
  - The approach gives upper bounds for $\phi_{d-2}(G)$ and
    $\phi_{d-1}(G)$ assuming an oriented $d$-cycle double cover.

### Project relevance

- **Primary.** Proposition 7 says the Oriented 5-Cycle Double Cover Conjecture
  implies the $S^2$-flow conjecture in their indexed setting for $d\ge 4$.
- **Primary.** More generally, if a graph has an oriented $d$-cycle double
  cover, it has an $S^{d-2}$-flow.
- **Inference.** For Jain's $S^2$ target, oriented 4-cycle double covers would
  be the dimension-matched object under the formula $S^{d-2}$, while the
  proposition explicitly discusses the 5-cycle double-cover conjecture in a
  higher-dimensional implication. The indexing must be handled carefully.
- **Inference.** Their cycle-double-cover machinery is a positive construction
  route unless a converse is proved for all $S^2$-flows.

## Snark catalogues and generators

- **To verify.** Standard sources for the sweep: Brinkmann--Goedgebeur--Hagglund
  snark generation work, House of Graphs snark lists, and `snarkhunter`.
- **To verify.** Exact catalogue sizes up to each order and the reproducible
  graph6 source for cyclically 4-/5-edge-connected snarks.

## Immediate open checks

1. Read HMM Sections 3--5 in full and transcribe Theorems 15, 17, and 19.
2. Verify the ordinary 4-flow-to-$S^2$-flow construction in the notation used
   here and add it as a short lemma.
3. Find whether Ulyanov's promised cubic-graph paper has appeared after
   arXiv:2603.23328.
4. Decide whether the first exact backend should be Sage/SymPy, Mathematica,
   Macaulay2, or a standalone SOS pipeline.
