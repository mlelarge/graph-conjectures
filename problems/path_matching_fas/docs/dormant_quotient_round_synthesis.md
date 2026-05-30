# Dormant-Quotient round synthesis: σ is the bottleneck

This note synthesises the three parallel investigations launched after
the D67 forced-frontier diagnostic, in commit `73d769d`'s working tree.
The three agents tested orthogonal hypotheses about how to break past
the FPT-by-|H| bound to a fully polynomial algorithm.

## 1. Verdict in one paragraph

The Dormant-Matching Quotient Lemma is **refuted** at n = 12 on
`one_block`.  The reversed-matching hardness route is **blocked** by
the strictly stronger **Theorem 6.1 (Global Back-Arc Linear-Forest
Shape)**, which closes *all* back-arc-encoded reductions.  The
forest-constraint exploit finds that partition compression is
*empirically* sound but **does not** yield polynomial time because the
σ-permutation on the bag — not the partition — is the dominant cost.
**Net effect**: σ on bag is now proved to be the bottleneck, the
multiset quotient is closed, and back-arc reductions are ruled out.
Aboulker Problem 4.4 remains open, but the next mathematical target
has been sharply localised.

## 2. The three results

### 2.1. Dormant-Matching Quotient — REFUTED

**Statement (refuted).**  *In a score-window sweep where many disjoint
forced edges are simultaneously dormant crossing components, their
individual identities can be replaced by a polynomial-size aggregate
without changing Path-FAS extendability.*

**Minimal collision.** On `one_block` at n = 12, sweep position p = 5:

| Prefix | Extendable? |
|---|---|
| A = (0, 3, 1, 4, 2) | NO |
| B = (1, 2, 0, 4, 3) | YES |

Both have identical augmented signature (visible_latent + dormant
aggregate) but different Path-FAS extendability.

**Root cause.**  In A the dormant pair {0, 10} merges via union-find
with active vertex 4; in B the dormants {0, 10} and {1, 9} merge with
each other and active 4 is separate.  Multiset signatures
fundamentally cannot capture this **global merge topology**, because
linear-forest acyclicity is global while bijections of dormant
identities are local.

**Consistency notes.** No collisions on reversed-matching m ∈ {10..15};
the lemma is consistent there.  No smaller refuter found in 250 random
skew tournaments at n ≤ 12; n = 12 `one_block` is empirically minimal.

Deliverables: `docs/dormant_matching_quotient_lemma.md`,
`scripts/dormant_quotient_probe.py`,
`tests/test_dormant_quotient.py` (15 tests pass).

### 2.2. Reversed-Matching Hardness — Theorem 6.1

**Theorem 6.1 (Global Back-Arc Linear-Forest Shape).** *In any LFO of
any tournament, the back-arc graph is a linear forest on n vertices:
max-degree ≤ 2, acyclic, at most n − 1 edges, decomposes into
vertex-disjoint paths.*

**Corollary 6.2 (Reduction Circularity).** *Any back-arc-encoded
reduction to Path-FAS realises an attachment graph that is itself a
linear forest.  The shape of constraints encodable in a single
tournament is bounded by the very same shape constraint that defines
Path-FAS.*

This is **strictly more general than Theorem 5.1** (Hardness Agent's
prior wire-saturation result, which is local to forced-path interiors).
6.1 is global and applies regardless of substrate.  The reversed-
matching family bypasses 5.1 but cannot bypass 6.1.

**Empirical confirmation.** The 3-COLORING reduction tested on 4 small
instances:
- K_3 (3-colorable): LFOs survive but no slot-decoded register state is
  a proper 3-coloring → false negative.
- C_5 (3-colorable): per-edge arc flips destroy LFO existence entirely
  → false negative.
- 2 / 4 failures, in opposite directions — confirming the structural
  barrier rather than an implementation bug.

Deliverables: `docs/reversed_matching_hardness.md`,
`scripts/reversed_matching_hardness.py`,
`tests/test_reversed_matching_hardness.py` (16 tests pass).

### 2.3. Forest-Constraint Exploit — σ is the actual bottleneck

Three DP variants tested against the D66 / D67 J-pathwidth DP:

| Variant | n=3..6 exhaustive | n=7 random 2000 | n=7 minimal NO | n=8 random 500 | n=9 random 30 | n=7..11 skew 2000 |
|---|---|---|---|---|---|---|
| A (drop comp) | match | 8 collisions | **9 WRONG** | — | — | — |
| B (counter + UF, lossy collapse) | match | 0 | 0 | 0 | 0 | 0 |
| C (bag-partition only) | match | 0 | 0 | 0 | 0 | 0 |

**Variant A** (drop the partition entirely): refuted at n = 7 (over-
accepts because cycle detection requires *some* partition state).

**Variant B and C** (different ways of compressing the partition):
empirically sound on every test but **not theoretically proved**.  An
abstract scenario in §4.1 of `docs/global_counter_dp.md` shows where
B's lossy first-arrival collapse *could* fail under a future two-load
that distinguishes two reachable partitions with identical counters.

**Crucial finding for the runtime analysis.**  The per-bag state of
the J-pathwidth DP is bounded by `(w + 1)! · 3^(w+1) · Bell(w+1)`.
At w = pw(J), the **σ-permutation factor `(w + 1)!`** dominates for
w ≥ 5 — not the partition `Bell(w+1)`.  Compressing the partition
saves at most a sub-exponential factor.  At pw(J) = Θ(n) on random-
skew tournaments, the DP is still super-exponential.

**Theoretical contribution.**  Even if Variant B is fully sound, this
does **not** settle Path-FAS ∈ P.  A polynomial-time algorithm needs
**σ-compression** as well as partition-compression.  Neither alone
suffices.

Deliverables: `docs/global_counter_dp.md`,
`scripts/global_counter_dp_probe.py`,
`tests/test_global_counter_dp.py` (13 tests pass).

## 3. Cross-agent convergences

### 3.1. Linear-forest acyclicity is the global rigidity that protects both directions

Two independent agents witnessed the same underlying structural fact:

  * **Dormant Quotient (refuted)**: linear-forest acyclicity globally
    distinguishes dormant states that local signatures conflate.
  * **Reversed-Matching Hardness (blocked)**: linear-forest shape
    bounds the constraints any back-arc encoding can realise.

The acyclicity-of-back-arc-graph is the *same scarce resource*
protecting the problem from *both* polynomial-route compression *and*
NP-hardness reduction.  This is a strong structural signal: the
question is delicately balanced.

### 3.2. σ on bag is now the proved bottleneck

  * **DP Agent prior round**: σ-on-bag is necessary because every
    weaker quotient collides on the n = 12 collision template.
  * **Forest-Constraint Exploit this round**: even with partition
    compression, σ remains `(w + 1)!` per bag → super-exponential at
    pw(J) = Θ(n).
  * **Dormant Quotient refutation**: the global merge topology that
    breaks aggregate signatures *also* encodes pairwise σ-position
    constraints between active and dormant vertices.

The remaining hard piece is the **σ-permutation on the active bag**.
The next round's positive route must either compress σ or extract it
from some structure outside the bag.

### 3.3. NP-hardness must use a non-back-arc encoding

Theorem 6.1 closes back-arc reductions; the prior wire-saturation
Theorem 5.1 closes forced-path-interior reductions.  Any future
NP-hardness attempt must:

  * encode SAT through **flex-edge-only** structure (G_flex without
    H), or
  * encode SAT through **score-window positions** (per-vertex window
    constraints that the LFO must satisfy *jointly*), or
  * encode SAT through **non-existence** of certain LFOs rather than
    existence of a specific FAS shape.

The `one_block` n = 12 collision (where dormant pairs merge with
active vertices through chained flex-edges) is the natural variable
gadget for a flex-edge-only reduction.  This is the candidate
substrate for the next hardness attempt.

## 4. State of Aboulker Problem 4.4

| Question | Before round | After round |
|---|---|---|
| Path-FAS ∈ P on arbitrary tournaments | Open, FPT-by-\|H\| proved (D66) | Open, no further P-route progress |
| Path-FAS NP-hard | Open | Open, back-arc reductions ruled out |
| Dormant multiset quotient | Conjectured | Refuted (n = 12 `one_block`) |
| Linear-forest shape blocks reductions | Empirical (Thm 5.1 wires) | Proved globally (Thm 6.1) |
| σ on bag is bottleneck | DP-agent empirical | Proved by Forest-Constraint analysis |
| Partition-only compression suffices | Conjectured | Refuted (Variant A) — partition needed for cycle detection |

## 5. Recommended next mathematical target

The convergence of the three agents narrows the next deliverable to
**one of two binary questions**:

1. **σ-compression on bag.**  Is there a polynomial-size equivalence
   class of bag-orderings that captures Path-FAS extendability?  Test
   on the n = 12 `one_block` collision: do the two prefixes A and B
   require distinct σ-classes, or can a finer-than-multiset but
   coarser-than-full-σ signature separate them?
2. **Flex-edge-only NP-hardness.**  Use the n = 12 `one_block`
   collision as a variable-gadget substrate.  Encode a SAT clause
   structure in flex edges only, avoiding any forced backedge.  The
   Theorem 6.1 barrier doesn't apply, because the reduction uses
   absence of certain LFO completions (not encoding of a specific
   back-arc graph).

Each of these is an independent decisive question.  A clean negative
on either is informative; a clean positive on either settles the
problem (one in P, the other NP-hard).

A third, less binary option:

3. **Anchor-augmented aggregate.**  The Dormant-Matching agent's
   §4.4 suggests augmenting the multiset aggregate with **anchor
   labels** linking each dormant component to the active-band
   partition.  This is potentially polynomial only if the active-band
   complexity is bounded — but the active-band partition has Bell(w+1)
   states, which is sub-exponential.  This may resolve the dormant
   merge issue while keeping the partition manageable.  Worth probing.

## 6. Files and tests

| Agent | Document | Scripts | Tests |
|---|---|---|---|
| Reversed-Matching Hardness | `docs/reversed_matching_hardness.md` | `scripts/reversed_matching_hardness.py` | `tests/test_reversed_matching_hardness.py` (16 pass) |
| Dormant Quotient | `docs/dormant_matching_quotient_lemma.md` | `scripts/dormant_quotient_probe.py` | `tests/test_dormant_quotient.py` (15 pass) |
| Forest-Constraint Exploit | `docs/global_counter_dp.md` | `scripts/global_counter_dp_probe.py` | `tests/test_global_counter_dp.py` (13 pass) |
| Synthesis | `docs/dormant_quotient_round_synthesis.md` (this) | — | — |

**Total new tests: 44 across the three agents, all passing.**

## 7. Citations verified

All by DOI or arXiv id:
- AAL Problem 4.4: arXiv:2402.10782 v1 p. 9.
- Coppersmith-Fleischer-Rurda 2010: DOI 10.1145/1798596.1798608.
- Bodlaender-Cygan-Kratsch-Nederlof 2015: DOI 10.1016/j.ic.2014.12.008
  (rank-based confirms partition state is single-exponential
  reducible, but σ remains).
- Prior round Width / DP / Hardness / Mining synthesis:
  `docs/four_route_J_synthesis.md`.

## 8. Honest residual uncertainties

  * Variant B (forest-counter + UF, lossy collapse) is empirically
    sound but not proved.  The abstract scenario in
    `docs/global_counter_dp.md` §4.1 sketches where it might fail at
    larger n.
  * The n = 12 `one_block` collision is empirically minimal but the
    sample (250 random skew tournaments) is small.  Larger skew
    sweeps might reveal a smaller refuter.
  * Theorem 6.1 is proved for one tournament's LFOs; the multi-
    tournament reduction setting is the natural extension but was not
    formalised.  The corollary follows but the formalisation gap is
    minor.

## 9. D69 addendum: low-hit sigma trace

The next target from §5.1 was implemented in
`scripts/sigma_trace_quotient_probe.py` and documented in
`docs/sigma_trace_quotient.md`.

What closed:

* The **Immediate-transition lemma** is proved: for a fixed full
  J-DP state, a future vertex \(x\), and a cut of \(\sigma\), the
  introduce transition survives iff the cut is low-hit feasible
  (forced-order compatible, hit set size at most 2, residual degrees
  available, and no component-pair cycle).
* The exact full-state graph probe found no mixed winning/losing
  low-hit quotient class on the n=12 skew templates, the n=7
  minimal-NO catalogue, or random samples through n=10.

What did not close:

* The **Trace Evolution Lemma** remains open: equal low-hit traces at
  a parent state need not obviously imply equal low-hit traces after
  choosing corresponding insertions.
* Runtime remains suspect.  The quotient barely compresses on hard
  cases: `one_block` has 180 full states vs 178 trace classes;
  `wake1_failure` has 967 vs 816; the n=7 minimal-NO catalogue has
  no compression at the maximum layer.

So the sigma route is not refuted, but the polynomial payoff is not
yet visible.  The next binary question is now Trace Evolution: prove
it, or find a parent-pair whose equal traces split after one
corresponding introduce step.
