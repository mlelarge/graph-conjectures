# Fanout Barrier — theorem-status note (as of D89)

Consolidated current state of the **capacity-form Fanout Barrier** for the
clause-and-fanout NP-hardness route to Aboulker Problem 4.4 (Path-FAS on
tournaments).  Supersedes the framing of the scattered D78–D89 sections in
`lemma_c_both_values.md`; those remain as the detailed record.

**Scope disclaimer (unchanged).**  Proving the barrier would **block the
clause-and-fanout reduction family** — it would *not* prove Path-FAS ∈ P.
Refuting it (a faithful splitter) would *re-open* that hardness route but
would not by itself prove NP-hardness (the splitter must still compose with
the D72 2-in-3 clause gadget into a full reduction).

Conventions: back-arc framing.  Tournament `T`; an **LFO** is an order
whose back-arc graph is a linear forest.  Port `P` has tournament arc
`u_P → v_P`; `s_P = 1` iff that arc is a back-arc.  `R_arc = {(s_P,s_Q)}`
over all LFOs.  **EQ_2 gadget**: `R_arc = {(0,0),(1,1)}` (no mixed value).
**cap-00**: an LFO realizing `(0,0)` with all four port endpoints at
back-degree ≤ 1.  **cap-11 / iso-11**: an LFO realizing `(1,1)` likewise;
for EQ_2 gadgets these coincide (see Theorem 3).  `C(P) = {w : v_P→w and
w→u_P}` (3-cycle partners of P's arc).

---

## 1. The live conjecture (exact statement)

> **Capacity-form Lemma C.**  No EQ_2 gadget has joint capacity on both
> equality values: there is no tournament with two disjoint ports such that
> `R_arc = {(0,0),(1,1)}` **and** cap-00 **and** cap-11.  Equivalently
> (Theorem 3): no EQ_2 gadget is simultaneously **cap-00** and **iso-11**.

A witness to the negation is a **faithful EQ_2 splitter**, the missing
ingredient of the clause-and-fanout reduction.  **Status: open.**  Verified
absent for `n ≤ 9` (Theorem 5).

The difficulty is the **non-co-occurrence** of the two capacities: cap-00
gadgets are common (1 806 at n = 9) and iso-11 gadgets exist (108 at n = 9),
but no gadget carries both.

---

## 2. Theorems (proved)

1. **Lemma R (projection), all n.**  A faithful EQ_k splitter (k ≥ 2) yields
   a faithful EQ_2 copy (project to two coordinates; capacity transfers
   down).  ⇒ the whole barrier reduces to the k = 2 statement above.

2. **Lemma I, all n.**  A port's tournament arc is a back-arc on **exactly
   one** of the two equality values.  (Positional tautology; the mechanism
   of the two-value competition.)

3. **cap-11 = iso-11, all n.**  For an EQ_2 gadget, capacity on the
   both-back-arc value forces each port endpoint's only back-arc to be its
   own port arc (the arc already gives degree 1; capacity caps it at 1), so
   both ports are isolated K_2's = iso-11; conversely iso-11 gives capacity
   on 11.

4. **3-Cycle Characterization, all n.**  If P's arc `u_P→v_P` is an isolated
   degree-1 back-arc in an order, every vertex strictly between `v_P` and
   `u_P` forms a 3-cycle `u_P→v_P→w→u_P`; hence `C(P)` = the between-vertices
   of P in any isolated order.

5. **Adjacent-Port Flip Lemma, all n.**  If an iso-11 order has a port pair
   **adjacent**, swapping it flips exactly that port to forward, realizing a
   mixed value (⇒ the gadget is not EQ_2).

6. **cap-00 lever (D87), all n — PROVED.**  cap-00 ⟹ `|C(P)| ≤ 2` and
   `|C(Q)| ≤ 2`.  *Proof:* in a cap-00 order `u_P` precedes `v_P` and each
   endpoint has back-degree ≤ 1; each `w ∈ C(P)` contributes a back-arc at
   `v_P` (if `w` before `v_P`) or at `u_P` (if after, hence after `u_P`),
   and distinct partners give distinct such back-arcs, so ≤ 1 partner on
   each side of `v_P`. Hence `|C(P)| ≤ 2`; symmetric for Q. ∎
   *(Implemented checks agree through n ≤ 8: 0 violations.)*

7. **Nested case closed, all n.**  If the iso-11 order has the two ports
   **nested**, the conjecture holds: `C(P) ⊇ {u_Q,v_Q} ∪ C(Q)` (Theorem 4),
   so the lever (Theorem 6) forces `|C(Q)| = 0`, i.e. Q is adjacent, and the
   Adjacent-Port Flip Lemma (Theorem 5) yields a mixed value — contradiction.
   *(Currently vacuous in the observed data: all iso-11 EQ_2 gadgets at
   n ≤ 8 are crossing; n = 9 adds transitive-port-quad shapes.  The genuine
   case is non-nested.)*

8. **Capacity barrier verified `n ≤ 9`.**  Exhaustive census over all
   tournament iso-classes: cap_both = 0.

   | n | EQ_2 gadgets | cap-00 | iso-11 (= cap-11) | **cap-both** |
   |---|---|---|---|---|
   | 6 | 2      | 1     | 0   | 0 |
   | 7 | 223    | 16    | 0   | 0 |
   | 8 | 5 430  | 189   | 6   | **0** |
   | 9 | 81 875 | 1 806 | 108 | **0** |

   (n = 8 canonical brute-force cross-check: eq2_with_iso11 = 6,
   iso11_with_no_mixed = 29 over iso-reps, D80_holds = false.  n = 9: my
   parallel census over 191 536 classes, logic validated vs canonical at
   n ≤ 8.)

---

## 3. Refuted mechanisms (the graveyard)

Every explanatory mechanism tried so far is **false** — the barrier, if
true, is *not* controlled by a port-local or small statistical invariant.

| mechanism | claim | verdict |
|---|---|---|
| one-value Lemma C (D76) | capacity on a value ⟹ R ≠ EQ | **false** (k = 2; D78) |
| D80 / non-adjacent flip lemma | iso-11 ⟹ a mixed value | **false at n = 8** (D84) |
| saturation of the 11-value | every 11-LFO saturates a port endpoint (cap-11 = 0) | **false at n = 8** (cap-11 jumps 0→6; D85) |
| local deletion / kernel criteria | a vertex-local rule identifies deletable vertices | **false** — deletability is non-local (D82) |
| rung compression | same-(role,parity) rungs are contractible | **false** (D83) |
| crossing splice | splice σ₀,σ₁ into a mixed order | **false** — always a back-deg-3 overflow (D88) |
| out-degree separator | iso-11 ⟹ (<,<); cap-00 ⟹ no '<' | **false at n = 9** (4 cap-00 share (<,<); D89) |
| relation-level / shape mining | a transition-graph cut certificate | **no global certificate** — localizes to the crux degree-3 wall only (D90) |

Common thread: each is a port-endpoint statistic or a bounded-locality move.
All collapse on a large enough sample.  The capacity difference between a
cap-00 gadget and an iso-11 gadget lives in the **global** arrangement of
the non-port vertices, not in any invariant of the four port endpoints.

---

## 4. The remaining open problem

> Explain the **non-co-occurrence of cap-00 and iso-11** in an EQ_2 gadget
> by a genuinely **global** invariant — one not reducible to port-endpoint
> degrees, 3-cycle-partner counts, port-quad shape, or local reorder moves.

The proved fragments bound the problem (Lemma R reduces k → 2; the cap-00
lever bounds `|C|`; the nested case is closed; the Adjacent-Port Flip Lemma
disposes of adjacent ports) but do not close it: the residual is the
**crossing, non-adjacent** iso-11 configuration with `|C(P)| = |C(Q)| = 2`
(1 such gadget at n = 8, 12 at n = 9), where every local mechanism fails.

**Relation-level mining — DONE (D90); no new certificate; route PAUSED.**
The transition-graph / witness-set mining (treat each EQ_2 gadget as
`(LFO_00^cap, LFO_11^iso)`, look for a cut certificate) was run on the full
n = 8 set.  Two findings:

  1. **Mixed-wall separation (confirmed).**  In the LFO transition graph
     (vertices = LFOs, edges = adjacent transpositions staying within
     LFOs), **every component is value-monochromatic** — 00-LFOs and
     11-LFOs are never connected (a single adjacent transposition flipping
     a port lands on a mixed ordering, which is not an LFO for an EQ_2
     gadget).  So the cap-00 and iso-11 regions are genuinely separated by
     the absent mixed LFOs — but this is essentially tautological for EQ_2
     and gives no new leverage.
  2. **Shape-realizability decomposition (n = 8 full).**  The *wrong-side*
     capacity **shape** is mostly **geometrically unrealizable**: 189/189
     cap-00 gadgets have **no ordering at all** with the iso-11 shape (four
     endpoints isolated back-arcs), and 5/6 iso-11 gadgets have no cap-00-
     shaped ordering.  The **sole exception is the crux gadget**
     P = (1,3), Q = (4,6): the cap-00 shape *is* realizable there, but only
     as a non-LFO with **defect 1 — a degree-3 at non-port (C-set)
     vertices, never a cycle** (reconfirming the D88 obstruction over all
     shape-orderings, not just splice paths).

So the non-co-occurrence **decomposes** into "wrong shape unrealizable"
(easy; 194/195 gadgets at n = 8) **+** "degree-3 wall on the crux."  This
**localizes** the difficulty but is **not a global certificate**: the crux
family **grows** (1 at n = 8 → 12 at n = 9), so the shape-unrealizable
convenience does **not** cover the hard case, and the persistent open core
is exactly the **crux degree-3 wall** where D88 already left it.  Like the
out-degree separator, "wrong shape unrealizable" is a per-gadget pattern,
not the global mechanism.

**Decision (per protocol): the fanout route is PAUSED.**  The mining
produced structure (the decomposition above) but **no new proof path**
cracking the crux degree-3 wall.  Capacity-form Lemma C is now a
**well-documented open subproblem** — verified n ≤ 9, eight distinct
local/statistical attacks refuted or exhausted, obstruction localized to
the crux degree-3 wall — **not an active proof path**.  The recommended
next move is to **return to the positive Path-FAS algorithmic side**.

---

## 5. One-line bottom line

The capacity-form Fanout Barrier is **empirically robust (cap_both = 0,
n ≤ 9)** and **mechanism-resistant (8 distinct local/statistical proof
attempts refuted or exhausted)**.  The obstruction is localized to the
**crux degree-3 wall** on the growing `|C| = (2,2)`-crossing iso-11 family,
but no global certificate is in hand.  **The fanout route is PAUSED** as a
well-documented open subproblem; it does not, either way, decide
Path-FAS ∈ P.  Next: the positive Path-FAS algorithmic side.
