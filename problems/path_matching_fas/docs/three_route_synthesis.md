# Three-route synthesis: general tournament Path-FAS after fork-tree closure

This note synthesises the three parallel research investigations
launched after the fork-tree adversarial subfamily of Aboulker–
Aubian–Lopes Problem 4.4 was closed in O(k) time (Section 65 of
`docs/exchange_proof_draft.md`).

The three directions are:
1. **Structural reduction** — generalised cycle-core / SCC /
   modular / band-DP / flex-graph approaches.
   Deliverable: `docs/general_path_fas_reduction.md`.
2. **Polynomial DP via stronger quotient** — bounded-port,
   structural multisets, treewidth-based, low-rank band-DP.
   Deliverable: `docs/general_path_fas_dp.md`.
3. **NP-hardness reduction** — Min-FAS / 3-SAT / linear-arrangement
   route.
   Deliverable: `docs/general_path_fas_hardness.md`.

Each direction was investigated independently by a research agent
in parallel.  The three documents are self-contained and the
deliverables this file points to should be read first for the
detailed argument.

## 1. The most important reframing

The NP-hardness investigation surfaced a precise reading of the
target question that all three documents now align on:

> **Aboulker Problem 4.4** (Dec-Path-FAS).  Given a tournament T,
> decide whether there exists a feedback arc set F ⊆ A(T) whose
> underlying undirected graph is a path.

The source is *Aboulker, Aubian, Charbit, Lopes,* "Finding
forest-orderings of tournaments is NP-complete," arXiv:2402.10782
(2024), Problem 4.4 on p. 9 of v1.  This is a pure decision problem
with no prefix, no constraint set, no optimisation.

The **constrained Path-FAS** that appears in `docs/exchange_proof_draft.md`
Section 65 (Theorem 65.A) is the subroutine

> Given a fork-tree tournament T_π and a toggle assignment
> ε ∈ {0, 1}^k, decide whether ε extends to a valid LFO of T_π.

These are not the same question.  On fork-trees, the unconstrained
Aboulker question is trivially YES — the all-zero toggle is always
extendable (Section 65.1).  Section 65 settles the *harder* constrained
question and develops techniques (V6'' classifier, σ*(k), image-graph
oracle) that are candidates for lifting to a general-tournament
attack on Aboulker.

A polynomial algorithm for the constrained extension problem on
**arbitrary** tournaments would, by prefix enumeration over starting
vertices, immediately yield a polynomial algorithm for Aboulker.  So
the fork-tree techniques are a valid attack vector on Problem 4.4 —
just not a direct answer.

## 2. Cumulative findings

### 2.1. Min-FAS NP-hardness does NOT transfer to Path-FAS

Charbit-Thomassé-Yeo (2007, HAL lirmm-00140321) and Alon (2006, DOI
10.1137/050623905) both prove Min-FAS on tournaments is NP-hard.  The
NP-hardness agent verified this does NOT imply Path-FAS NP-hardness:

  * Min-FAS asks about cardinality; Path-FAS about graph shape.
    These are orthogonal.
  * Concrete witness: Paley Q(7) has min FAS size 7 with degree
    sequence (3,3,2,2,2,1,1) (not a path) and Path-FAS = NO.
  * AAL themselves prove Forest-FAS NP-hard and leave Path-FAS open
    in the same paper — if the implication were automatic they
    would not have posed Problem 4.4.

This rules out the most natural negative-direction reduction.

### 2.2. 3-SAT route fails at fanout

Variable gadget (Section-16 toggle, 4 vertices) and clause gadget
(NAE-3SAT cyclic triangle) both work locally.  Empirical search at
n ≤ 9 (exhaustive) + 100 k+ random extensions + 32 768-orientation
external-wiring enumerations all return **0 strict candidates** for a
fanout/broadcast gadget that would force k port-pairs to agree.

The structural reason is sharp: every vertex's back-arc budget is
≤ 2 (path-FAS constraint), but broadcasting a single bit to k clauses
requires back-degree ≥ k.  This is a documented structural barrier,
not a reduction failure.

### 2.3. Cycle-core extraction does NOT generalise

The structural-reduction agent's strongest negative result: at n=7,
the minimal-NO census splits as

  | type | count |
  |---|---|
  | coupling | 7 |
  | degree-only | 7 |
  | cycle-only | 2 |
  | both | 2 |

The 7 "degree-only" instances admit *forest* back-arc graphs in every
order — there is no forced back-arc cycle to extract.  Fork-tree
Lemma 52.1 relies essentially on the pairing's block/interval
scaffolding, which has no analogue in arbitrary tournaments.  **Hard
dead end** for direct cycle-core lifting.

### 2.4. SCC condensation is vacuous on the hard family

20/20 of n=7 LFO-NO instances are strongly connected; 1758/1798 of
combinatorial n=8 NO instances are too.  SCC condensation is therefore
a no-op on the cases that matter.  Modular decomposition handles
~50% of n=7,8 NO instances, but the residual prime cases are exactly
the open problem.

### 2.5. Bounded-port DP fails on a concrete n=12 collision

The DP agent reproduced the Section 16 2^(n/4) sleeping-block lower
bound and then probed bounded-port DP quotients.  All three structural
quotients (component multiset, half-block signature, image-interval)
inherit the same n=12 collision

  prefix (0, 1, 2, 5, 3) vs (1, 2, 0, 5, 3) on `one_block`, depth 5

at every truncation radius K ∈ {0, 1, 2, 3}.  Multiset additionally
re-introduces 2^k state count.

Bounded-reversal-distance is also refuted: concrete radius-1 collision
at n = 5, prefix (0, 3, 1, 4) vs (1, 3, 0, 4).

The score-window flex graph has clique number ≤ 9 (Hall's condition)
and interval treewidth ≤ 8, but the LFO ordering choice breaks the
naïve treewidth DP.

### 2.6. Band-DP exact but exponential

`(placed_mask, deg, UF)` summary keys give exact decisions on all
456 n = 7 census records, all 1798 n = 8 combinatorial NO records,
and random n ∈ {7, 8, 9, 10, 12}.  **But the state-space size is
empirically exponential** in the skew-noise regime (75 → 12 081
states from n = 11 → n = 12).  Exactness without polynomial bound
is not a polynomial algorithm.

## 3. Cross-route verdict

| direction | clean positive | clean negative | concrete obstruction |
|---|---|---|---|
| structural reduction | no | yes (cycle-core dead end) | degree-only NO instances at n = 7 |
| polynomial DP | no | yes (every quotient collides) | n = 5 radius-1, n = 12 depth-5 collisions |
| NP-hardness | no | yes (no fanout gadget) | back-arc budget 2 vs needed k |

**No direction yields a clean settlement of Aboulker Problem 4.4.**
All three close their respective natural attack vectors with
documented structural barriers.

The aggregate is mildly more consistent with **Path-FAS ∈ P** than
with NP-hardness (because the fanout obstruction is sharper than the
"cycle-core doesn't lift" obstruction), but neither side has a proof.

## 4. Next moves implied by the three investigations

Each document independently recommends a follow-up.  Aggregated:

1. **Ordering-aware treewidth DP** (DP agent, §4).  The interval
   treewidth bound ≤ 8 is constant but the ordering choice breaks
   the DP; an ordering-aware refinement might close the gap.
2. **Non-fanout NP-hardness** (hardness agent, §5).  If a SAT
   reduction sidesteps fanout (e.g., via global structure rather
   than local broadcast), the structural barrier may not apply.
3. **Refined structural parameter** (reduction agent, §6).  Modular
   decomposition handles ~50% of NO instances; the residual prime
   cases need a finer structural parameter than treewidth /
   pathwidth / branchwidth.  An interesting candidate: combine
   FF-signature with score-window structure.

These are the three concrete deliverables for a next iteration.  None
is itself a settled direction, but each starts from a clean
documented gap rather than an open-ended search.

## 5. Files

| direction | document | scripts |
|---|---|---|
| structural reduction | `docs/general_path_fas_reduction.md` | `scripts/band_decomposition_probe.py` |
| polynomial DP | `docs/general_path_fas_dp.md` | `scripts/bounded_port_dp_probe.py`, `scripts/structural_quotient_probe.py`, `scripts/treewidth_probe.py`, `scripts/flex_graph_treewidth.py`, `scripts/band_rank_probe.py`, `scripts/bounded_reversal_dp_probe.py` |
| NP-hardness | `docs/general_path_fas_hardness.md` | — (used existing `decide_path_fas_bruteforce`) |
| this synthesis | `docs/three_route_synthesis.md` | — |

## 6. Citations verified

All load-bearing citations have DOI or arXiv identifiers:

  * AAL Problem 4.4: arXiv:2402.10782 v1 p. 9 (quoted verbatim by
    the NP-hardness agent).
  * Charbit-Thomassé-Yeo 2007: HAL lirmm-00140321.
  * Alon 2006: SIAM J. Discrete Math. 20(1):137–142, DOI
    10.1137/050623905.
  * Kenyon-Mathieu, Schudy 2007 STOC: DOI 10.1145/1250790.1250806.
  * AAL Forest-FAS NP-completeness: arXiv:2402.10782 Thm 1.1.

The three agents independently re-derived the obstructions in §§
2.1–2.6 from scratch (no shared computational state).
