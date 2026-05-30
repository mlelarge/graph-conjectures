# D71: Port-Relation Census for Q7.1

## 0. The question

Q7.1 (`docs/two_route_final_synthesis.md` §4): **is there a composable
non-monotone ordering primitive** for tournament Path-FAS?  A positive
answer would be the first hardness substrate not killed by Theorems
5.1, 6.1, or toggle monotonicity (Theorem 3.1).  A proved negative
would close the local-gadget hardness route and strongly support
Path-FAS ∈ P.

This note attacks Q7.1 as a **finite, falsifiable** classification —
the experiment to run before investing in the cutting-plane oracle's
polynomial bound (which is a global search, not a local primitive).

Two scoping corrections from the prior round are taken as given:

  * Theorem 3.1 is about the **consecutive-toggle substrate** only
    (lowering a toggle deletes one back-edge, fixes the rest); a
    non-consecutive/global primitive could evade it.
  * The sharp consequence is **downward-closedness** of the
    consecutive-toggle relations (all-zero always feasible), which
    kills SAT-style hardness *for that substrate* — not the broad
    "monotone CSPs are in P."

## 1. Formalization

A **gadget** is a tournament T with k ordered port pairs
(x_1, y_1), …, (x_k, y_k).  Over every valid LFO σ of T (order whose
back-arc graph is a linear forest), the port bits are

    b_i(σ) = 1[σ(y_i) < σ(x_i)]   (y_i placed before x_i),

and the gadget **realizes** the relation

    R_T = { (b_1(σ), …, b_k(σ)) : σ a valid LFO of T } ⊆ {0,1}^k.

**Disjoint ports (composability prerequisite).**  For ports to be
*independently attachable* to other gadgets, they must have pairwise-
disjoint vertex sets (2k distinct vertices).  Shared-vertex ports do
NOT give independent attachment: a vertex in two ports would have to
absorb two external back-arcs, needing residual degree ≥ 2.  Worse,
ports that share *all* vertices of a triangle {u,v,w} make R_T = NAE_3
by pure **order-transitivity** (a total order on 3 vertices has no
3-cycle), which is a betweenness artifact, not a Path-FAS property.
The census therefore restricts to **disjoint** port-tuples.  (At k = 3
this needs n ≥ 6; n = 5, k = 3 has no disjoint ports at all.)

**Composable shadow.**  Composition attaches new back-arcs to the port
endpoints; a bit-vector survives only if some witnessing LFO leaves
every (disjoint) port endpoint with residual back-degree ≥ 1
(degree ≤ 1).  So the relation that survives composition is

    R_comp = { b ∈ R_T : b has a witness σ with every port endpoint
                          at back-degree ≤ 1 }.

**Classification.**  Each relation is tagged:

  * downward-closed (monotone)?
  * Schaefer type: 0-valid, 1-valid, Horn (∧-closed), dual-Horn
    (∨-closed), affine (ternary-⊕-closed), bijunctive (majority-closed).
  * **non-Schaefer** iff none of the six hold.

By Schaefer's dichotomy, a CSP over a relation set is NP-hard iff some
relation is non-Schaefer.  **The decisive object is R_comp, not R_T**:
only R_comp survives composition, so hardness requires *R_comp* to be
non-Schaefer.

## 2. The central phenomenon: NAE collapses under composition

The decisive object is **R_comp**, because only it survives wiring.
Two mechanisms collapse a non-Schaefer R_T to a Schaefer R_comp:

**(a) Orientation matters.**  Non-Schaefer-ness is NOT flip-invariant.
NAE_3 = {0,1}^3 \ {000,111} is non-Schaefer, but complementing one
coordinate gives a relation containing 000, hence 0-valid (Schaefer).
The census enumerates all 2^k port orientations as coordinate
complements; a primitive is hard only if *some* orientation yields a
non-Schaefer R_comp.

**(b) Degree-2 saturation prunes vectors.**  A shared-vertex gadget at
n = 5 realizes R_T = NAE_3 but composable shadow R_comp = {001,100,101}
— only 3 of 6 vectors keep residual capacity, and {001,100,101} is
dual-Horn (Schaefer).  But this gadget's ports share vertices, so it is
a *transitivity artifact* (see §1), not a composable primitive.

The corrected census uses **disjoint ports** and checks whether *any*
orientation of R_comp is non-Schaefer.

## 3. Two composability filters

For a NEGATIVE result the **lenient** shadow R_comp (some witness has
capacity) is the right, conservative object: it over-approximates what
survives composition, so "lenient R_comp always Schaefer" is strong
evidence.  For a POSITIVE claim the lenient filter is too generous — a
vector kept by a single fragile witness need not survive composition,
which can be forced into other witnesses.  The robust gate is the
**strict** shadow R_comp_strict (every witness has port capacity).

  * R_comp        = { b : SOME witness has all port endpoints deg ≤ 1 }.
  * R_comp_strict = { b : EVERY witness has all port endpoints deg ≤ 1 }.

A confirmed hardness primitive needs R_comp_strict non-Schaefer.

## 4. Census results (disjoint ports, all orientations)

Exact: iso-class tournament representatives (extension-generated,
matches OEIS A000568); all valid LFOs by brute force; all disjoint
k-port-tuples; all 2^k orientations.  k = 2 omitted (every binary
relation is bijunctive, hence Schaefer).

| n | k | reps | disjoint ports | distinct R_T | non-Schaefer R_T | **lenient comp. non-Schaefer** | **strict comp. non-Schaefer** |
|---|---|---|---|---|---|---|---|
| 5 | 3 | 12 | 0 (need n ≥ 6) | 0 | none (vacuous) | none (vacuous) |
| 6 | 3 | 56 | 15 | 191 | 11 | **none** | **none** |
| 7 | 3 | 456 | 105 | 245 | 15 | **1 (unresolved)** | **none** |

Reading:

  * **n = 6** (first non-vacuous case): 11 non-Schaefer R_T relations
    exist, but ALL collapse to Schaefer R_comp under both filters.
  * **n = 7** (first size with genuine minimal-NO tournaments; 20 of
    456 reps have no valid LFO): the **lenient** filter finds one
    non-Schaefer shadow — R_comp = {011,101,110} = exactly-2-in-3
    (NP-complete CSP) — on a genuinely disjoint-port gadget
    (ports (0,1),(3,4),(5,6)).  Each of the three vectors has exactly
    ONE capacity-witness out of 4–5 LFOs, so R_comp_strict = ∅.

**The status of the n = 7 candidate is UNRESOLVED — not a confirmed
artifact, not a confirmed primitive.**  A composition test gives a
genuinely mixed verdict:

  * *Idealized composition succeeds.*  If each port vertex could
    reserve exactly one back-degree for an external attachment, the
    realizable port relation is **exactly 2-in-3** (the no-capacity
    witnesses become degree-3-violating and drop out; each 2-in-3
    vector keeps its capacity witness; the loader adds only a pendant
    leaf to the back-arc forest, so no cycle).  Verified directly.
  * *But the reservation is not freely realizable as a tournament.*
    Forcing a back-arc onto a port vertex needs a loader whose score
    window is disjoint (gap ≥ 5).  For the low-degree port vertices
    (0, 1, 3) the naive high-transitive loader has window gap < 5, so
    the reserving back-arc is NOT forced.  The same score-window
    obstruction that governs the whole problem reappears at the
    composition step.

So the strict filter (R_comp_strict = ∅) flags fragility, and the
attempted composition confirms the fragility is real at the
tournament level — but neither rules out a cleverer loading
construction.  This is the first candidate to survive to n = 7, and
resolving it is the sharpest remaining question.

## 5. Verdict (n ≤ 7, k = 3)

Under the robust (strict, uniform-capacity) filter there is **no
confirmed composable non-Schaefer ordering primitive at n ≤ 7,
k = 3**.  At n = 7 the lenient filter exposes one 2-in-3 candidate
whose status is genuinely **unresolved**: its idealized composed
relation is the NP-complete 2-in-3, but realizing the required
per-port degree reservation as a tournament hits the score-window
gap obstruction on low-degree port vertices.

This is **qualified** evidence for the Q7.1 impossibility direction
through n = 6 (clean: no composable non-Schaefer under either filter),
weakening to **unresolved** at n = 7.  Two honest reads:

  * If the n = 7 candidate ultimately cannot be loaded (score-window
    obstruction is fundamental), the impossibility direction extends to
    n = 7 and a clause gadget for 2-in-3 does not realize — strong for
    Path-FAS ∈ P.
  * If a cleverer loading realizes 2-in-3 as a genuine clause gadget,
    then the *clause side* of a 2-in-3-SAT reduction exists, and the
    only remaining barrier to NP-hardness is **fanout** (variable
    reuse across clauses) — the same degree-2 obstruction that blocked
    Theorems 5.1 and 3.1.  Even then, without fanout the read-once
    2-in-3 instances are polynomial, so this alone is not hardness.

**Decisive next step.**  Settle the n = 7 candidate: either construct a
valid tournament composition that enforces 2-in-3 on three independent
port-bits (→ a real clause gadget, then attack fanout), or prove the
score-window gap obstruction forbids any such loading (→ impossibility
through n = 7).  This is sharper than the cutting-plane oracle and must
come first.

**RESOLVED (D72, `docs/port_loader_realizability.md`).**  The first
branch holds.  A 14-vertex tournament (G + 1 padding + 6 forced
loaders) realizes the port relation exactly = 2-in-3, verified
independently.  The Loader Gap Lemma is FALSE; the n = 7 candidate is a
**genuine 2-in-3 clause gadget**.  Consequently the Q7.1 impossibility
direction does NOT hold at n = 7, and the sole remaining barrier to
NP-hardness is **fanout** (variable reuse under the degree-2 budget).

## 6. Why this precedes the oracle

The cutting-plane oracle asks for a polynomial bound in a *global*
search space — hard to prove.  Q7.1 asks for a *finite, local,
falsifiable* primitive.  The census either:

  * exhibits a composable non-Schaefer gadget (settles NP-hardness via
    Schaefer + a composition lemma), or
  * finds none up to (n, k), giving a concrete impossibility target.

Either outcome is sharper than an open-ended oracle runtime proof.

## 7. Honest limitations

  * The composability filter is a **necessary** condition (a disjoint
    port vector needs a residual-capacity witness to survive *one*
    attachment); it does not prove a gadget composes into an arbitrary
    circuit.  A full composition lemma (relation stable under disjoint
    union + padding + wiring) is the remaining gap before any
    impossibility claim becomes a theorem.  Conversely, the filter is
    *lenient* (one capacity witness per vector suffices), so it
    over-approximates what survives — and even this over-approximation
    yields no non-Schaefer R_comp, which only strengthens the finding.
  * Two corrections were necessary mid-investigation and are baked into
    the final numbers: (i) **orientation** must be enumerated
    (non-Schaefer-ness is not flip-invariant); (ii) ports must be
    **vertex-disjoint** (shared-vertex ports are transitivity
    artifacts and are not independently attachable under degree-2).
    The pre-correction runs spuriously reported both "no non-Schaefer"
    (missing orientations) and "composable non-Schaefer found"
    (shared-vertex artifacts); the corrected census reconciles these.
  * Exact over iso-class representatives at n ≤ 6 (56 classes at n=6,
    verified against OEIS A000568).  n = 7 (456 classes) needs an
    iso-rep source other than brute canonicalization (2^21 tournaments
    × 7! relabelings is too slow); it is future work.

## 8. Files and tests

| artefact | location |
|---|---|
| Census + classification | `scripts/port_relation_census.py` |
| Tests (disjoint-port requirement, transitivity artifact, arity-2 always Schaefer) | `tests/test_port_relation_census.py` (7 pass) |

## 9. Citations

  * Schaefer dichotomy 1978: DOI 10.1145/800133.804350.
  * NAE-SAT NP-completeness: Schaefer 1978 (above).
  * Q7.1 origin: `docs/two_route_final_synthesis.md` §4;
    Theorem 3.1 (monotonicity): `docs/nonbackarc_hardness.md`;
    Theorems 5.1/6.1 (back-arc barriers): `docs/J_hardness_via_wires.md`,
    `docs/reversed_matching_hardness.md`.
