# Fanout Barrier: consolidated status (D75 search + D76 theorem)

Two adversarial investigations — a search for a counterexample (D75)
and a proof attempt (D76) — converge on the same picture.  The
NP-hardness route for tournament Path-FAS (Aboulker–Aubian–Lopes
Problem 4.4) is blocked at **fanout**, and the fanout barrier is now
reduced to a single crisp gap, verified well beyond the original
census.

## 1. The reduction (D76, proved)

A 2-in-3 **clause** gadget exists (D72).  NP-hardness needs **fanout**:
a *faithful free-bit splitter* = a gadget realizing R_T = EQ_3 =
{000,111} on three vertex-disjoint ports with joint output capacity on
**both** equality vectors.

  * **Lemma R (PROVED, all n).**  A faithful EQ_k splitter projects to
    a faithful EQ_2 *copy*; capacity transfers to any port subset.  So
    the whole Barrier reduces to a **2-port statement**: no gadget
    realizes R_T = {00,11} with joint capacity on both 00 and 11.
  * **Lemma I (PROVED, all n).**  Each port's tournament arc is a
    back-arc on **exactly one of the two raw port-bit values** (a
    positional tautology; verified over 1,098,720 instances, exact
    50/50).  Consequently *every* LFO realizing that raw bit spends one
    endpoint-degree unit on the port — this is the mechanism of the
    two-value competition.  (Stated per bit-value, not per LFO: a value
    may be realized by many LFOs.)
  * **Lemma C (the gap; corrected to the BOTH-values form).**  No
    EQ_k gadget has joint capacity on **both** 0^k and 1^k (= no
    faithful copy).  **Barrier = R ∧ C.**  Verified exhaustively at
    n ≤ 7; a conjecture for n ≥ 8.  (The earlier one-value phrasing
    "capacity on a value ⟹ R_T ≠ EQ" is FALSE for k=2 — 16 EQ_2
    gadgets have capacity on 00 — and is corrected here; the verified
    fact is the 16/16/**0**-on-both split.)
  * **Lemma C-slide (conditional, all n).**  An endpoint-slide proves
    Lemma C whenever no auxiliary/internal vertex loads a port
    endpoint — the gap is exactly the auxiliary-loading regime.

## 2. The search (D75, no counterexample)

The two-auxiliary-vertex escape — auxiliaries absorbing the
equality-enforcing back-arcs while freeing the ports — was the precise
remaining hole (D74 §5).  Result:

  * **All 31 distinct n = 7 EQ_3 base gadgets** (every n = 7 EQ_3
    gadget up to port-respecting isomorphism), each extended by **two
    auxiliary vertices in all 2^15 = 32768 arc-orientations**
    (1,015,808 extensions), plus a structured pure-auxiliary-coupling
    topology.
  * **5900 extensions keep R_T = EQ_3; ZERO gain joint capacity on even
    one equality vector** — let alone both.
  * Per-base EQ_3-preserving counts varied structurally (84, 154, 188,
    202, 216, 220, 240), confirming the bases are genuinely different
    equality mechanisms, not relabelings — yet all have zero capacity.

This directly probes **Lemma C in the n = 9 two-aux regime** and finds
no counterexample, extending the support from n ≤ 7 (D73) and one-aux
(D74) into the two-aux n = 9 region.

Tooling: a pruned backtracking LFO enumerator (~350× faster than n!),
validated against brute force; early R_T rejection; fork-parallel over
the 31 bases.

## 3. Convergence

| | D76 (proof) | D75 (search) |
|---|---|---|
| object | Lemma C: no EQ with capacity on BOTH values | EQ_3 + capacity on both (= ¬Lemma C) |
| n ≤ 7 | verified (k=2,3) | no splitter |
| n = 9 two-aux | C-slide handles no-aux-load case *modulo an unproved k≥3 window-choice step* | no splitter over 10^6 extensions |
| verdict | Barrier = R ∧ C; C open n ≥ 8 | escape hatch closed over searched scope |

The two are exactly dual, and neither finds a crack: the proof reduces
the Barrier to Lemma C; the search fails to refute Lemma C precisely
where it is unproven.

## 4. Honest open gap (unchanged shape, now much smaller)

Lemma C is **not proved for general n ≥ 8**.  The search covers:
n = 7 bases + two auxiliaries (n = 9) + one structured coupling family.
It does **not** cover:

  * ≥ 3 auxiliary vertices / n ≥ 10;
  * the full n = 9 EQ_3 census (EQ_3 gadgets with no n = 7 EQ_3
    sub-gadget — only partially probed);
  * non-EQ relations that nonetheless project (via Lemma R's converse
    direction) to a faithful copy.

So the Fanout Barrier remains a **strongly supported conjecture**,
reduced to Lemma C, not a theorem.

**Discipline (what the Barrier does and does not give).**  Proving the
Fanout Barrier would **block the known clause-and-fanout reduction
program** — the only concrete NP-hardness route on the table.  It would
**not** prove Path-FAS ∈ P: ruling out one reduction family is not a
polynomial algorithm, and other (non-gadget) hardness routes are not
excluded.  The honest consequence is "the current hardness program is
blocked modulo Lemma C," which is *evidence* toward P, not a proof of
it.

## 5. State of Aboulker Problem 4.4

```
2-in-3 clause gadget exists (D72)
   ∧ no faithful free-bit splitter (Fanout Barrier, = Lemma R ∧ Lemma C)
   ⟹ the clause+fanout NP-hardness program is blocked
      (only read-≤-2 instances encodable; those are polynomial)
   ⟹ no NP-hardness via this gadget family
   [does NOT by itself imply Path-FAS ∈ P]

Status:  Lemma R  PROVED (all n)
         Lemma I  PROVED (all n)
         Lemma C  VERIFIED n ≤ 7 and n = 9 two-aux; OPEN n ≥ 8 general
```

The decisive remaining target is **Lemma C for general n** (the
2-port statement: a gadget with R_T = {00,11} cannot have joint
capacity on both 00 and 11).  Lemma R has already collapsed the
3-port problem onto it, and Lemma C-slide handles the no-auxiliary-load
case — so the proof effort now has a single, sharp, 2-port focus.

## 6. Files and tests

| artefact | location |
|---|---|
| Barrier theorem + reduction | `docs/fanout_barrier_theorem.md` |
| Barrier checkers | `scripts/fanout_barrier_checks.py` + `tests/test_fanout_barrier_checks.py` |
| Two-aux search | `scripts/two_aux_eq3_search.py` + `tests/test_two_aux_eq3_search.py` |
| this synthesis | `docs/fanout_barrier_synthesis.md` |

Fast tests pass (12 across both suites, `-m "not slow"`); slow tests
pin the ~8-min pinned-base and ~30-min full-sweep negatives.  The
`slow` marker is now registered in `pytest.ini`.

## 7. Next step

Prove **Lemma C** (the 2-port copy cannot keep capacity on both
equality values) for general n — via Lemma I's exact-one-back-arc
competition plus a global degree-budget argument that survives
auxiliary loaders.  If proved, the Fanout Barrier becomes a theorem
and the clause-and-fanout NP-hardness program is fully blocked (strong
evidence toward — but not a proof of — Path-FAS ∈ P).  If a
counterexample appears at n ≥ 10, NP-hardness reopens with an explicit
splitter.
