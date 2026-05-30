# D72: Forced-Loader Realizability — the n=7 candidate IS a 2-in-3 clause gadget

## 0. Result

The n=7 port-relation census (D71) found a disjoint-port gadget G whose
lenient composable shadow is the non-Schaefer relation
exactly-2-in-3, {011,101,110}, but whose strict shadow is empty.  The
open question (the **Loader Gap Lemma**) was whether the required
per-port degree reservation can be realized as an actual tournament
without distorting the relation.

**Verdict: the Loader Gap Lemma is FALSE.**  There is an explicit
14-vertex tournament — G plus one padding vertex and six *forced*
loader vertices — whose realized port relation is **exactly
{011,101,110} = 2-in-3**.  So G is a genuine **2-in-3 clause gadget**
for tournament Path-FAS.  This is the first confirmed composable
non-Schaefer ordering primitive.

## 1. The construction

Gadget G (vertices 0..6, D71 candidate), ports (0,1),(3,4),(5,6),
orientation (0,1,1).  Port in-degrees in G: d⁻ = {0:5, 1:5, 3:3, 4:3,
5:1, 6:1}.

Augment with `n_extra = 7` vertices on top (indices 7..13), transitive
among themselves and above the gadget.  Index 7 is pure padding; the
six top vertices are **loaders**, each reverse-pointing to one port
vertex, hardest (highest-degree) port assigned the highest loader:

    loader 13 → 0,  loader 12 → 1,  loader 11 → 3,
    loader 10 → 4,  loader  9 → 5,  loader  8 → 6.

The padding raises the loaders' score windows so that every loader
back-arc ℓ → v is **forced** (disjoint windows):

| loader ℓ → v | win(ℓ) | win(v) | forced |
|---|---|---|---|
| 13 → 0 | [10,13] | [4,8] | yes |
| 12 → 1 | [9,13] | [4,8] | yes |
| 11 → 3 | [8,12] | [2,6] | yes |
| 10 → 4 | [7,11] | [2,6] | yes |
| 9 → 5 | [6,10] | [0,4] | yes |
| 8 → 6 | [5,9] | [0,4] | yes |

## 2. Verification

Independent recomputation (score-window backtracking enumerator,
validated against brute force on G: 35 LFOs, exact match):

  * the augmented graph is a valid tournament on 14 vertices;
  * all six loader back-arcs are forced (table above);
  * the augmented tournament has 50 valid LFOs;
  * the realized port relation is exactly {011,101,110} = 2-in-3;
  * every port vertex has back-degree ≤ 2 in every LFO (the loader
    consumes one unit; the gadget supplies ≤ 1 internally).

The same exact-2-in-3 outcome holds at n_extra = 7 and 8 (n_total 14,
15) with all loaders forced, so the realization is robust to padding.

Pinned in `tests/test_port_loader_realizability.py`.

## 3. Why the earlier "unresolved" became "resolved"

The strict composability filter (R_comp_strict = ∅) was a *sufficient*
rejection test, not a necessary one.  It flagged that no single LFO
keeps capacity on all ports across all witnesses — but composition does
not need that.  The forced loaders **prune exactly the no-capacity
witnesses** (those would push a port vertex to back-degree 3, which is
illegal), leaving precisely the capacity witnesses, whose port-bit
projection is the lenient shadow 2-in-3.  The score-window gap worry
(low loaders not forced) is removed by **padding**: enough top vertices
raise every loader's window above its target's.

So the lenient shadow was the right object after all — *provided* the
reservation is realized by forced loaders, which padding makes
possible.

## 4. Consequence: the barrier is now FANOUT, not clause realizability

A 2-in-3 clause gadget exists.  A full NP-hardness reduction from
2-in-3-SAT (≡ 1-in-3-SAT, NP-complete, Schaefer 1978) additionally
needs **variable reuse / fanout**: a variable appearing in several
clauses must have its order-bit read by several clause gadgets.

Each read attaches a back-arc to a variable's port vertex, and the
linear-forest budget caps each vertex at back-degree 2.  So a variable
can feed at most ~2 clause gadgets before its ports saturate — the same
degree-2 obstruction as Theorem 5.1 (wire-interior saturation) and the
original local-fanout barrier.

The decisive question is therefore now sharply localized:

> **Fanout question.**  Can a single orderable variable-bit be read by
> ≥ 3 clause gadgets within the degree-2 back-arc budget — or does the
> budget cap occurrences at 2?  Bounded-occurrence 2-in-3-SAT at the
> achievable occurrence bound determines NP-hardness:
>   * occurrence ≥ 3 reachable ⇒ NP-hard (Path-FAS ∉ P unless P=NP);
>   * occurrence capped at 2 ⇒ read-twice instances, which are
>     polynomial, so the clause gadget alone does not give hardness.

## 5. Honest status of Aboulker Problem 4.4

This **weakens** the prior P-lean.  Previously the census found no
composable non-Schaefer primitive (through n ≤ 6, and n = 7 unresolved);
that was evidence toward P.  Now a genuine 2-in-3 clause gadget exists,
so the hardness question is live and hinges entirely on fanout.

  * If fanout is achievable (occurrence ≥ 3): **NP-hardness**, settling
    Problem 4.4 negatively.
  * If the degree-2 budget provably caps occurrence at 2: clause
    gadgets do not compose into hard instances, and the P-lean is
    restored — but now with a precise reason (fanout impossibility),
    not just "no clause gadget."

Either way, the clause side is settled and the entire problem reduces
to the fanout question.

## 6. Files and tests

| artefact | location |
|---|---|
| Loader realizability prober + LFO enumerator | `scripts/port_loader_realizability.py` |
| Pinned 14-vertex 2-in-3 realization | `tests/test_port_loader_realizability.py` |
| n=7 candidate origin | `docs/port_relation_census.md` §4 |

## 7. Citations

  * 1-in-3-SAT / 2-in-3-SAT NP-completeness: Schaefer 1978,
    DOI 10.1145/800133.804350.
  * Degree-2 / wire-saturation barrier: Theorem 5.1,
    `docs/J_hardness_via_wires.md`.
