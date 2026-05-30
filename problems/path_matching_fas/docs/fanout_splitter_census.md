# D73: Fanout / Splitter census — value propagation is blocked

## 0. Result

D72 confirmed a genuine exactly-2-in-3 **clause** gadget.  NP-hardness
from 2-in-3-SAT additionally needs **fanout**: one variable bit read by
≥ 3 clauses.  Sharing a single port pair across three clauses is
degree-blocked, so the only escape is a **splitter** that copies a bit
to fresh port pairs, each retaining capacity to feed one clause.

**Verdict: no capacity splitter exists at n ≤ 7, and padding cannot
create one.**  Enforcing all-equal on disjoint ports consumes the full
degree-2 budget at the port endpoints, leaving no residual capacity to
feed downstream clauses.  Path-FAS cannot copy an ordering bit to fresh
ports under degree 2.  Fanout is blocked.

This **restores the P-lean** with a precise structural reason:
non-Schaefer clause gadgets exist, but value propagation / fanout does
not — so the clause gadgets cannot be wired into a hardness reduction.

## 1. The target

A **splitter** realizes an all-equal relation on disjoint ports

    EQ_k = { 00…0, 11…1 } ⊆ {0,1}^k

with every port endpoint at internal back-degree ≤ 1 (residual ≥ 1) so
each output can accept one clause loader (cf. D72, where each clause
port is fed by one forced loader).

  * **EQ_3 splitter** (one gadget, 3 equal ports): feed each port to a
    distinct clause → variable read by 3 clauses → occurrence-3 →
    hardness.
  * **EQ_2 copy**: chaining copies to fan out hits a degree-3 wall at
    internal chain nodes (a middle node feeds two copies + one clause),
    so EQ_3-direct is the meaningful target.

## 2. Census results (disjoint ports, all orientations, iso-reps)

| relation | n | realizes EQ as R_T | **capacity splitter** (R_comp = EQ) |
|---|---|---|---|
| EQ_2 (copy) | 4, 5 | no (EQ ⊊ R_T) | no |
| EQ_2 (copy) | 6 | **yes** | **no** (only partial: one value keeps capacity) |
| EQ_3 (split) | 6 | no | no |
| EQ_3 (split) | 7 | **yes** | **no** (R_comp = ∅) |

Two structural readings:

  * **EQ_2 at n = 6 is asymmetric.**  A copy gadget with R_T = {00,11}
    exists, but the two values are not symmetric in capacity: value
    (1,1) has 8 capacity witnesses, value (0,0) is realized by a single
    LFO with a port vertex at back-degree 2 (zero residual).  So the
    copy can transmit one value with capacity, not a free bit.
  * **EQ_3 at n = 7 has empty capacity.**  Gadgets force R_T = {000,111}
    but R_comp = ∅: in *every* equal-LFO at least one port endpoint is
    at back-degree 2.  Not even one output is freely feedable.

## 3. Padding cannot rescue capacity (structural)

In D72 the clause gadget's strict-capacity gap was fixed by padding +
forced loaders.  That worked because the clause must *receive* inputs
and its lenient capacity was already non-empty; padding only made the
loaders forced.

For the splitter the situation is structurally different and padding
**provably does not help**:

  * **Top padding** (extra vertices above the gadget, transitive):
    every gadget vertex keeps its in-degree (gadget → padding arcs are
    forward), so gadget score windows and gadget-internal orderings are
    unchanged.  Port back-degrees are unchanged.  R_comp stays empty.
  * **Bottom padding** (extra vertices below): all gadget in-degrees
    increase by the same constant, shifting every window uniformly;
    relative orderings, hence port degrees, are unchanged.  R_comp
    stays empty.

Verified at n = 7 + top-padding E = 1, 2: R_T stays EQ_3, R_comp stays
∅.  The only way to change a port's back-degree is to attach a reversed
arc (a loader) to it — but loaders *consume* capacity (they are the
downstream clause connection), they never add it.  So no extension
gives an EQ_3 splitter output capacity.

## 4. The invariant (conjectured, strongly supported)

> **Splitter Saturation Invariant.**  Any tournament gadget whose port
> relation on k ≥ 2 disjoint ports is the all-equal relation EQ_k
> forces, in every realizing LFO, at least one port endpoint to
> back-degree 2.  Equivalently, enforcing equality across disjoint
> ports has no residual capacity to feed a downstream gadget.

Supported by: the full n ≤ 7 census (EQ_2 asymmetric, EQ_3 empty
capacity) and the padding-robustness argument (§3).  A full proof would
show that the back-arcs needed to forbid all 2^k − 2 mixed vectors on
disjoint ports necessarily saturate a port endpoint.

## 5. Consequence for Aboulker Problem 4.4

The hardness reduction needs **clause ∧ fanout**.  D72 gives the clause
(2-in-3); D73 blocks the fanout (no capacity splitter).  So:

  * **NP-hardness via local gadgets is blocked** at the fanout step —
    the same degree-2 wall as Theorem 5.1 (wire saturation) and
    Theorem 3.1 (monotonicity), now isolated to value propagation.
  * **The P-lean returns**, but sharpened: it is no longer "no
    non-Schaefer clause exists" (one does — D72) but "non-Schaefer
    clauses exist, yet their inputs cannot be fanned out under the
    linear-forest degree-2 budget."

The clean structural picture:

    degree-2 budget  ⟹  clause gadgets OK, fanout impossible
                     ⟹  read-once non-Schaefer formulas only
                     ⟹  no NP-hardness reduction
                     ⟹  Path-FAS plausibly ∈ P

Read-once / bounded-occurrence formulas over a non-Schaefer relation
are polynomial, so a clause gadget without fanout cannot encode general
SAT.

## 6. Honest limitations

  * Census is exact at n ≤ 7 (456 iso-classes).  The Splitter
    Saturation Invariant is conjectured, supported by n ≤ 7 + the
    padding-robustness argument, not proved for all n.
  * Only **EQ-style** (all-equal) splitters were searched.
    Implication-style (Horn) fanout — e.g. x → y, x → z plus a reverse
    gadget — is a logically distinct mechanism not ruled out here, and
    is the natural next thing to census.  (A faithful free-bit copy
    needs equivalence, not mere implication, so EQ is the primary
    target; but implication chains deserve a check.)
  * "Capacity ≥ 1 feeds a clause" is the D72 model (one forced loader
    per port).  A clause needing a different attachment degree would
    change the bar.

## 7. Files and tests

| artefact | location |
|---|---|
| Splitter census + capacity tracking | `scripts/fanout_splitter_census.py` |
| Pinned no-capacity-splitter + padding-robustness | `tests/test_fanout_splitter_census.py` |
| Clause gadget (D72) | `docs/port_loader_realizability.md` |

## 8. Citations

  * 1-in-3 / 2-in-3-SAT NP-completeness: Schaefer 1978,
    DOI 10.1145/800133.804350.
  * Degree-2 wire-saturation barrier: Theorem 5.1,
    `docs/J_hardness_via_wires.md`.
  * Monotonicity barrier: Theorem 3.1, `docs/nonbackarc_hardness.md`.
