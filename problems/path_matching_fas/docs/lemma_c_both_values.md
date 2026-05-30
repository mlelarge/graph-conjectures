# D78: Lemma C corrected to the both-values form, with the saturation mechanism

> **📋 For the consolidated current state, read
> [`fanout_barrier_status.md`](fanout_barrier_status.md) (theorem-status
> note, as of D89): the live conjecture, the proved theorems, the graveyard
> of refuted mechanisms, and the open problem.**  This file is the detailed
> chronological record (D78–D89) behind that note.

> ## ⚠️ D84 (MAJOR CORRECTION, n=8): D80 is FALSE
>
> **D80 ("an iso-11 gadget always realizes a mixed value"), verified
> n ≤ 7 and conjectured for all n, is REFUTED at n = 8.**  Two explicit
> 8-vertex witnesses (verified by brute force, the pruned enumerator, and
> a fully independent fresh checker) are iso-11 yet realize NO mixed
> value — one with R_arc = {(1,1)}, one a full **EQ_2** gadget with
> R_arc = {(0,0),(1,1)}.  So "no iso-11 gadget has R_arc ⊆ {00,11}" and
> "eq2_with_iso11 = 0" are both false at n = 8, and the §2b/§2c **Flip
> Lemma** ("both-isolated ⟹ mixed") fails on the non-adjacent residual.
> The kernelization program (D81/D82/D83) was trying to *prove* D80 for
> all n — which is why every route was blocked.  See **§2h**.  What is
> NOT refuted: the capacity-form barrier "no faithful EQ_2 splitter
> (capacity on **both** 00 and 11)"; the doc's claimed equivalence
> *D80 ⟺ that barrier* was an overclaim (D80 is strictly stronger).
>
> **Follow-up D85 (full n=8 census, §2i): the capacity-form barrier
> SURVIVES at n = 8** — 5430 EQ_2 gadgets, 189 cap-on-00, 6 cap-on-11,
> **0 cap-on-both**.  But its old mechanism is dead: cap-on-11 jumped
> 0 → 6, so the barrier now holds because the two capacities never
> co-occur, not because the 11 value saturates.  Live conjecture is the
> capacity-form Lemma C, verified n ≤ 8, open n ≥ 9.

## 0. The correction

An earlier draft (D76) stated Lemma C in a **one-value** form:
"capacity on an equality value v ⟹ R_T ≠ EQ_k."  That is **false for
k = 2**.  Direct recount with the barrier agent's own enumerator
(`iter_gadget_instances`, n = 7, k = 2):

  * **660** gadget-instances have R_T = EQ_2 = {00,11};
  * of those, **16 have joint capacity on 00**, **16 on 11**, **0 on
    both**.

So 16 EQ_2 gadgets *do* have capacity on 00 — the one-value form is
refuted.  (It happens to hold for k = 3 because an EQ_3 gadget has
capacity on *neither* value, which is why the over-generalisation went
unnoticed.)

**Corrected Lemma C (verified n ≤ 7; conjectural n ≥ 8).**
No EQ_k gadget has joint port capacity on **both** 0^k and 1^k.
Equivalently: **no faithful EQ_k copy/splitter exists.**  This is what
Lemma R needs and what the Fanout Barrier rests on.

Consequence for the proof program: a single-port slide *from one
equality witness* (e.g. a 00-capacity witness) being blocked is
**consistent** with R_T = EQ_2 — the 16 cap-on-00 gadgets are exactly
that.  So the single-port-slide-from-σ0 argument does NOT attack
Lemma C; the both-values statement requires using the structure of
*both* equality values.

## 1. The saturation mechanism (verified n ≤ 7)

For all **16** n = 7 EQ_2 gadgets that have capacity on 00 but not on
11, the minimum-saturation profile over the 11-LFOs is identical:

> on **every** LFO realizing the "11" equality value, **all four port
> endpoints a, b, c, d are saturated** (back-degree ≥ 2).

(Distribution over the 16 gadgets: the min-saturated endpoint set is
`{a,b,c,d}` in all 16 — never fewer.)

So the two equality values are **not symmetric**:

  * on one equality value the two port arcs are *forward* — the four
    endpoints carry only whatever else loads them, and capacity (all
    ≤ 1) is achievable;
  * on the other equality value **both port arcs are back-arcs**
    (Lemma I: each port arc is a back-arc on exactly one raw bit value;
    here both ports' back-arc value coincides), contributing one unit
    to each of the four endpoints, and the EQ-enforcement back-arcs
    that forbid the mixed vectors {10, 01} add a second unit — pushing
    all four to degree 2.

**This is the corrected "two-value competition":** a gadget can buy
capacity on the forward-arc value, but the back-arc value spends a
unit at every port endpoint before enforcement even begins, and
enforcement spends the second — so capacity on *both* values is
impossible.

## 2. The reduced sub-claim (general n)

The both-values Lemma C now reduces to a single saturation statement:

> **Saturation sub-claim.**  Let (T, {P, Q}, o) realize R_T = EQ_2,
> and let V be the equality value on which both port arcs are
> back-arcs.  Then every LFO realizing V has at least one saturated
> port endpoint (in fact, empirically, all four).

Given the sub-claim, Lemma C follows: the value V never has capacity,
so capacity holds on at most the other value — never both.

The sub-claim is the place the linear-forest degree-2 budget should
bite: on V the four endpoints already each carry their port back-arc
(degree ≥ 1), and forbidding the two mixed vectors forces an additional
incident back-arc at (at least one of) them.  A proof needs to show the
EQ-enforcement cannot be entirely offloaded onto non-port (auxiliary)
vertices — exactly the n ≥ 8 / auxiliary regime that the two-aux search
(D75) probed without finding an escape.

## 2b. The proof structure (validated n ≤ 5) and the residual gap

> **⚠️ QUARANTINED by D84 (§2h).**  This section, §2c and §2d develop the
> Flip-Lemma route — "iso-11 (both-isolated on the 11 value) ⟹ a mixed
> vector is realizable" — as a path to Lemma C.  **That implication is
> FALSE at n = 8** (§2h: explicit iso-11 EQ_2 gadgets with no mixed
> vector).  These sections are retained as **historical negative
> evidence and proved fragments**, NOT proof scaffolding for Lemma C.
> Specifically: the **Adjacent-Port Flip Lemma** and the **3-Cycle
> Characterization** (§2c) remain TRUE theorems; what is dead is the
> non-adjacent Flip Lemma, the saturation mechanism, and the claim that
> any of this proves the capacity-form Lemma C.  Step 3 below ("a MIXED
> vector is realizable") is exactly the false step.

Following the comparison-of-value-classes route:

1. **Assume** R_T = EQ_2 and an LFO σ realizing the both-back-arc value
   with joint capacity (all four endpoints degree ≤ 1).
2. Since both port arcs are back-arcs on this value, each endpoint has
   degree ≥ 1 from its port edge; with capacity (≤ 1), each has degree
   **exactly 1**, so {a,b} and {c,d} are **isolated K_2 components** of
   the linear forest.
3. **Flip Lemma (step 4, the crux).**  From such a both-isolated
   configuration, a MIXED vector (1,0) or (0,1) is realizable by some
   valid LFO.
4. A realizable mixed vector means R_T ⊋ EQ_2 — contradiction.
5. Hence no EQ_2 gadget has capacity on its both-back-arc value, so
   capacity holds on at most one value: **Lemma C**.

Steps 1, 2, 4, 5 are immediate.  The **Flip Lemma (step 3)** is the
crux.  Note it is *equivalent* to the Saturation sub-claim (and hence
to Lemma C): "both-isolated ⟹ mixed realizable" contraposes to
"R_T = EQ_2 ⟹ no both-isolated LFO on the both-back-arc value."  So
proving it in full is proving Lemma C; what follows is a rigorous
*partial* result plus the precise residual.

> **Adjacent-Port Flip Lemma (PROVED, all n).**  Let σ be a valid LFO
> realizing the both-back-arc value with both port edges isolated K_2's
> (all four endpoints degree 1), and suppose a port pair — say a, b —
> is **adjacent** in σ.  Then a mixed vector is realizable; hence
> R_T ≠ EQ_2.

*Proof.*  Swap the adjacent pair a, b.  An adjacent transposition
changes the loaded/forward status of **only** the {a, b} arc (no other
pair's relative order changes).  In σ that arc is a back-arc (P-bit 1);
after the swap it is forward (P-bit 0), and a, b drop from degree 1 to
degree 0.  Every other arc is unchanged, so the new back-arc graph is
B_σ with the single edge {a, b} deleted — still a linear forest.  The
swapped order is therefore a valid LFO realizing P-bit 0, Q-bit 1, i.e.
the mixed vector (0, 1).  So (0, 1) ∈ R_T ≠ EQ_2.  ∎

This rigorously proves Lemma C for every gadget whose both-back-arc
value admits an isolated LFO with an adjacent port pair.

**The non-adjacent residual (the open core).**  The adjacent reduction
covers ~66% of configs (30/48 at n=4, 2130/3228 at n=5).  The remaining
~34% have **no** both-isolated LFO with an adjacent port pair, yet a
mixed vector is still realizable — verified, but with no clean
construction:

  * single-**endpoint** reinsertion (freeze all else): fails ~40% of
    isolated-edge flips — too weak;
  * single-**vertex** relocation from a both-isolated σ (move any one
    vertex): reaches a mixed vector for 18/18 (n=4) and **1038/1098**
    (n=5) of the non-adjacent configs — but **60 configs at n=5 still
    need a multi-vertex reorder**.

So no bounded-local-move construction proves the non-adjacent case;
it is the irreducible open core of Lemma C (and thus of the
"clause-and-fanout program is blocked" claim).

## 2c. Framing correction and the 3-Cycle Characterization (PROVED)

**Framing correction.**  "Both-isolated" must be defined by *back-arc
status*, not by the port *bit*.  The port bit `1[pos(b)<pos(a)]`
depends on orientation and equals "port arc is a back-arc" only when
the tournament arc runs from the later to the earlier endpoint.  The
structurally meaningful condition is: **the port arc itself is the
isolated degree-1 back-arc**.  In this framing the counts are clean —
n = 5: **1800** both-arc-isolated configs, flip lemma holds 1800/1800;
n = 4: 72/72.  (An earlier bit-based census over-counted at 3228 and
produced spurious "3-cycle violations" — those were the framing bug,
now removed.)

**3-Cycle Characterization (PROVED, all n; verified n ≤ 5, 0
violations over 3600 + 96 instances).**

> Let σ be a valid LFO in which port {a,b}'s tournament arc u→v
> (u, v ∈ {a,b}) is a back-arc and is the **only** back-arc at both u
> and v (isolated K_2).  Then every vertex w strictly between v and u
> in σ forms a directed 3-cycle u → v → w → u in T.

*Proof.*  u→v is a back-arc, so pos(u) > pos(v); a between-vertex w has
pos(v) < pos(w) < pos(u).  Since the port arc is u's only back-arc, u
has no other out-back-arc: every x with pos(x) < pos(u), x ≠ v, has
x→u — in particular w→u.  Since it is v's only back-arc, v has no other
in-back-arc: every y with pos(y) > pos(v), y ≠ u, has v→y — in
particular v→w.  With u→v this gives the 3-cycle u → v → w → u.  ∎

**C(P) = between-vertices (PROVED; verified 0 violations, 108000/108000
at n=6).**  Let C(P) = {w : v→w and w→u} be the 3-cycle partners of P.
In an isolated config, isolation forces C(P) to be *exactly* the
between-vertices: u's only back-arc is u→v, so every w→u (w ∈ C(P)) is
forward ⟹ w before u; v's only back-arc is u→v, so every v→w is forward
⟹ v before w.  Hence v < w < u for all w ∈ C(P).  So |C(P)| = (port
gap) − 1.

**Charging ⟹ |C(P)| ≤ 4 is NECESSARY to flip P (PROVED).**  If u→v is
made forward (u before v), then for *every* w ∈ C(P): w before u makes
v→w a back-arc (loads v); w after u makes w→u a back-arc (loads u).
Either way w loads u or v.  Since u, v absorb ≤ 2 back-arcs each, at
most 4 partners can be accommodated: |C(P)| ≤ 4.  (Verified: every
flippable port has |C| ≤ 4, 100% at n ≤ 6.)  This is why no fixed-size
move proves the Flip Lemma — |C(P)| = port gap − 1 grows with the gap.

**But |C(P)| ≤ 4 is NOT sufficient (REFUTED at n=6).**  3600 ports have
|C(P)| ≤ 4 yet are not flippable — flippability depends on the finer
structure (the between-vertices' mutual arcs and the cycle/degree
interaction), not on |C(P)| alone.  So the clean "|C| ≤ 4 ⟺ flippable"
characterization fails, and the Flip Lemma does **not** reduce to a
counting condition on C.  The full Flip Lemma — every isolated config
has *some* flippable port — remains open (verified n ≤ 5); the proved
fragments (C = between, |C| ≤ 4 necessary, charging) bound the problem
but do not close it.

## 2d. The two-port coupled flip theorem (D80) and the cycle-coupling

> **⚠️ QUARANTINED by D84 (§2h).**  D80 ("iso-11 ⟹ mixed") is FALSE at
> n = 8.  The **Equivalence Lemma** below is a tautology and remains
> valid, but the sentence "D80-for-all-n ⟺ the both-values Lemma C" is an
> **overclaim**: D80 is strictly stronger than the capacity-form Lemma C,
> and only D80 is false.  Read this section as the (correct) n ≤ 6/7
> obstruction *structure* — nested geometry, coupling cycle, the ladder —
> not as a reduction of Lemma C.

The single-port Flip Lemma — "*every* isolated config has a flippable
port" — has resisted a bounded-move proof (§2b, §2c).  The right
statement is **two-port and coupled**, and it uses *both* equality
values at once.  Throughout, "iso-11" means an LFO realizing the
both-back-arc value with both ports isolated K_2 (all four endpoints
back-degree exactly 1), and bits are in the **back-arc-status framing**
(D79): s_P = 1 iff P's tournament arc is a back-arc.

> **Two-port coupled flip theorem (verified n ≤ 7).**  If (T, {P, Q})
> admits an iso-11 LFO, then a **mixed** vector (1,0) or (0,1) is in
> R_arc.  Equivalently: the "both-nonflippable" case never occurs;
> equivalently, **no iso-11 gadget has R_arc ⊆ {00,11}**.

Note the hypothesis is iso-11 *alone* — the earlier "and a 00-LFO
exists" requirement is **not needed** (at n = 6, of the 720 iso-11
configs with no 00-LFO, zero are both-nonflippable).

### Verification

`two_port_coupled_flip` (configs with iso-11 ∧ 00, back-arc framing):

| n | iso-11 ∧ 00 | (T,T) | (F,T) | (T,F) | **(F,F)** |
|---|---|---|---|---|---|
| 5 | 1800  | 1800  | 0    | 0    | **0** |
| 6 | 53280 | 49680 | 1800 | 1800 | **0** |

`iso11_eq2_backarc_count` (the full condition, over tournament
iso-reps, back-arc framing):

| n | iso-11 gadgets | with R_arc ⊆ {00,11} | EQ_2 gadgets | EQ_2 with iso-11 |
|---|---|---|---|---|
| 6 | 103 | **0** | 2   | **0** |
| 7 | 588 | **0** | 223 | **0** |

**Framing caveat — resolves an apparent contradiction with D78.**  §1
reports, via the bit-framing enumerator, "16 EQ_2 gadgets with capacity
on 11" at n = 7.  That is *not* a back-arc-framing iso-11: the bit
enumerator ranges over all 2^k orientations, and flipping the
orientation swaps the roles of 0 and 1, so a single physical
capacity is double-counted as "cap on 00" under one orientation and
"cap on 11" under the other.  In the unambiguous back-arc framing,
capacity sits **only on the forward (00) value, never on the
both-back-arc (11) value** — exactly D80, and exactly the saturation
mechanism of §1.  (Had this not been checked, D80 would have looked
false at n = 7; it is not.)

### Structure of the obstruction (verified n ≤ 6)

For each of the 3600 nonflippable ports at n = 6:

1. **Obstruction is a CYCLE, never degree.**  The best P-forward/Q-back
   order is never a linear forest, but in **all 3600** cases a
   degree-feasible order exists (no endpoint forced to back-degree 3)
   and the unavoidable defect is a **back-arc cycle**.  This sharpens
   §2c: nonflippability is internal cycle structure, not saturation —
   which is why the |C(P)| ≤ 4 count is necessary but not sufficient.

2. **Interval geometry is always NESTED** (3600/3600).  In the iso-11
   order, one port's interval lies strictly inside the other's — never
   disjoint, never crossing.

3. **The block is always COUPLED** (3600/3600, **0 intrinsic**).  A
   nonflippable port P becomes flippable the moment Q's back-arc
   constraint is dropped (`intrinsic_vs_coupled`): the obstruction
   genuinely needs Q to remain a back-arc.  So the cycle truly couples
   the two ports.

4. **Cycle shape (the ladder).**  The *shortest* blocking cycle has
   length 3 (1440) or 6 (2160).  The length-6 cycles thread **both
   full port arcs** {u_P,v_P,u_Q,v_Q} plus two between-vertices — the
   alternating ladder coupling the two intervals.  The length-3 cycles
   are transitive triangles fully reversed; ~25 % of *shortest* cycles
   are intra-single-port triangles, but (by item 3) these are never the
   only obstruction — a coupling cycle always coexists; the shortest
   metric just prefers the triangle.

### Why this does NOT yet close Lemma C (the no-free-lunch wall)

> **Equivalence Lemma (proved, all n).**  Given an iso-11 LFO,
> [P and Q both nonflippable] ⟺ [R_arc ∩ {(0,1),(1,0)} = ∅] ⟺
> [R_arc ⊆ {(0,0),(1,1)}].
>
> *Proof.*  P nonflippable ⟺ (0,1) ∉ R_arc; Q nonflippable ⟺
> (1,0) ∉ R_arc; conjunction ⟺ no mixed vector ⟺ R_arc ⊆ {00,11}. ∎

Hence **D80 for all n ⟺ no iso-11 gadget has R_arc ⊆ {00,11} ⟺ the
both-values Lemma C** (in particular D80 ⟹ no EQ_2 gadget has capacity
on 11, which with §1's "capacity on 00 may exist" gives "at most one
value").  Proving D80 *is* proving Lemma C.

Every structural route collapses back onto this same core:

  * **"Always coupled" for all n** = "from an iso-11 LFO, P alone is
    flippable when Q is free" = the **single-port Flip Lemma** of §2b —
    open at n ≥ 6 (the non-adjacent residual).
  * **"Ladder ⟹ mixed flip or opposite-value saturation"** is the
    incompatibility step; making it a theorem (not a per-n check) is
    again equivalent to the above.

So the alternating ladder is the **verified mechanism** of the
obstruction (n ≤ 6), and D80 itself is **verified n ≤ 7** — but no
all-n proof has been found, and the incompatibility argument is
*provably equivalent* to Lemma C rather than a reduction of it.

> **Honest status.**  D80 (iso-11 ⟹ mixed) is verified n ≤ 7, with the
> obstruction characterized (cycle / nested / coupled / ladder) at
> n ≤ 6.  The all-n statement is equivalent to the both-values Lemma C
> and **remains open**.  This is structural machinery toward the Fanout
> Barrier; it does **not** prove Path-FAS ∈ P.

## 2e. The kernelization route (D81) — foundation, and why local moves were the wrong method

> **⚠️ QUARANTINED by D84 (§2h).**  The kernelization aimed to prove D80
> for all n by bounding a minimal counterexample.  **D80 is false at
> n = 8**, so no such bound exists — the "minimal counterexample" is a
> real n = 8 object, not an impossibility.  Facts 1, 2 and the Clean-Cut
> Insertability Lemma are still correct *as stated*; D82/D83 (which found
> every kernel route blocked) were correct red-teaming whose negative
> results are now *explained* by D84.  Retained as historical method, not
> as a live route to Lemma C.

Local-move refinement (§2b–§2d) keeps re-deriving the open core because
it characterizes individual obstructions.  The route with all-n leverage
is **minimal-counterexample kernelization**: show that if D80 fails it
fails on a tournament of *bounded size*, then settle the bounded case by
the existing census.  A bound ≤ 7 would *prove* Lemma C outright
(`iso11_eq2_backarc_count` already covers n ≤ 7); a bound ≤ 9 makes the
next finite search decisive.

**Setup.**  A *counterexample* is (T, P, Q) with an iso-11 LFO and
R_arc(T) ⊆ {00,11} (no mixed value).  Fix one with the fewest non-port
vertices.  Two facts (`kernel_lemmas_check`, 0 violations at n ≤ 5)
control deletion of a non-port vertex w:

> **Fact 1 (iso-11 preserved, all n).**  T−w has an iso-11 LFO.
> *Proof.*  Restrict the iso-11 σ to V∖{w}: the back-arc graph is
> B_σ minus the edges at w — a subgraph of a linear forest, hence a
> linear forest.  Port endpoints had back-degree exactly 1 in σ (their
> port arc only, so no back-arc to w), so the two port arcs remain
> isolated K_2's.  Port values are unchanged. ∎

> **Fact 2 (deletion only RELAXES, all n).**  R_arc(T) ⊆ R_arc(T−w).
> *Proof.*  Any LFO τ of T realizing value v restricts to τ−w, an LFO
> of T−w (subforest) with the same port values. ∎

Fact 2 is the load-bearing orientation: deletion can only **add**
realizable values, so a no-mixed counterexample is only ever *destroyed*
(never created) by deletion.  Hence in a **minimal** counterexample
every non-port vertex w is **essential**: deleting it adds a mixed
value (R_arc(T−w) ∩ {01,10} ⊋ R_arc(T) ∩ {01,10}).  Equivalently, some
mixed LFO τ′ of T−w does **not** lift to T — i.e. w is *un-insertable*
into τ′.

> **Clean-Cut Insertability Lemma (proved, all n).**  Let τ′ be an LFO
> of T−w.  If some gap of τ′ has all in-neighbors of w before it and all
> out-neighbors after it, inserting w at that gap yields an LFO of T
> with the same port values.  *Proof.*  At that gap w has no back-arc
> (out-neighbors-before = in-neighbors-after = ∅), so w is isolated in
> the back-arc graph; B is otherwise unchanged. ∎

So an essential w must be *positionally twisted* in **every** mixed LFO
of T−w: its in- and out-neighbors interleave with no clean cut.  The
kernel bound therefore reduces to the **Insertability Lemma**: bounding
how many vertices can be simultaneously twisted-against-all-mixed-orders.
By the structure of §2d the twist is exactly the nested ladder, so the
conjecture is: *interior ladder rungs admit a clean cut (are deletable);
only an O(1) core is essential.*

> **Essential ⟹ on-structure (verified n ≤ 6, the key localization).**
> Over all 54000 iso-11 configs at n = 6, there are **7200** essential
> vertices (deletion adds a mixed value), and **every one lies between
> some port's endpoints** (w ∈ C(P) ∪ C(Q)) — `essential_offstructure`
> = 0.  No essential vertex sits outside both port intervals.  So the
> essential set is confined to the (nested) ladder region, exactly as
> the kernelization needs: a minimal counterexample has all its
> non-port vertices inside the two coupled intervals.

**Intrinsic limit of the census (important).**  The kernel bound cannot
be observed below the bound: an n-vertex iso-11 config has only n−4
non-port vertices, so at n ≤ 7 there are ≤ 3 of them — too few to
distinguish a constant kernel from a growing one.  At n = 5 (one
non-port vertex) **no** vertex is essential (the mixed witness already
lives in the 4-vertex port core); at n = 6 essential vertices appear
(7200) but each iso-11 config has only **two** non-port vertices, so the
essential *count* per config is ≤ 2 by arithmetic alone.  So this route
is **proof-only**: the deletion facts, the localization (essential ⟹
on-structure), and the Insertability Lemma are theorems/verified, but
the *bound* must be proved, not censused.

**Caution from D79.**  Single-vertex relocation already failed to cover
60/1098 non-adjacent flips at n = 5 (multi-vertex moves needed).  That
is direct evidence the Insertability Lemma's single-vertex core is
non-trivial: some twisted vertices may genuinely resist a clean cut, so
the "interior rungs are deletable" step is exactly where the difficulty
concentrates.

> **Honest status (D81).**  Facts 1, 2 and the Clean-Cut Insertability
> Lemma are proved (all n; 0 violations n ≤ 6), and the localization
> "essential ⟹ on-structure" is verified n ≤ 6 (7200/7200 at n = 6).
> The minimal-counterexample framing is sound and reduces the kernel
> bound to the Insertability Lemma.  The bound itself is unproved and
> not census-observable at n ≤ 7.  No proof of Lemma C; no consequence
> for Path-FAS ∈ P.

## 2f. The Insertability bound is NOT local (D82, red-team, n=6)

§2e reduces the kernel bound to the Insertability Lemma: among the
between-vertices (ladder rungs) of a counterexample, enough must be
*deletable* (= non-essential: deleting them does not add a mixed value)
that only an O(1) **essential** core survives.  The natural way to prove
this is a **local** sufficient condition for deletability — "a vertex of
type X is always deletable" — applied to interior rungs.  This section
**refutes the three most natural such conditions** on the n = 6 census
(`essential_locality_refutation`, `tests/test_lemma_c_both_values.py`),
showing deletability is *not* captured by any local invariant of the
vertex.  Essentiality is as in `kernel_lemmas_check` (deletion changes
R_arc ∩ {01,10}); over all 54000 iso-11 configs at n = 6 there are
**7200** essential vertices.

| candidate "X ⟹ deletable" | essential vertices of type X | verdict |
|---|---|---|
| **(C1)** X = σ-isolated (back-degree 0 in the iso-11 order σ) | **1440** | REFUTED |
| **(C2)** X = single-C ("outer rung": in exactly one of C(P), C(Q), not the coupled core) | **5760** | REFUTED |
| **(C3)** X = low-degree (min(indeg, outdeg) ≤ 1 in T) | **1440** (profiles (1,4): 720, (4,1): 720) | REFUTED |

Raw structure of the 7200 essential vertices: σ-back-degree
distribution {0: 1440, 1: 5760}; role distribution {cP: 2880, cQ: 2880,
cP∩cQ: 1440}.

**Reading of the refutations.**

  * **(C1)** kills "only σ-loaded vertices can be essential" — a vertex
    isolated in the iso-11 back-arc graph can still be essential.  So
    essentiality is not inherited from the σ-forest structure.
  * **(C2)** kills "outer rungs are deletable, only the coupled core
    C(P)∩C(Q) is essential" — a vertex in just one port's interval (an
    outer rung) is essential 5760 times.  This directly contradicts the
    optimistic §2e picture ("interior ladder rungs admit a clean cut").
  * **(C3)** kills "essential ⟹ in/out-degree ≥ 2" — a vertex that beats
    only one vertex (or is beaten by only one) can be essential.  The
    only clean degree fact survives: a **sink** (outdeg 0) or **source**
    (indeg 0) is always off-structure (it cannot satisfy v_P → w → u_P),
    hence never essential — but those are exactly the off-structure
    vertices a minimal counterexample already lacks, so this gives no
    reduction of the on-structure core.

**Consequence for the program.**  Deletability is **not** a local
property of w (its σ-degree, its interval membership, or its tournament
degree).  The kernel bound therefore cannot be obtained by a
local-criterion argument; it must invoke the **global** coupled-ladder
structure (the "always coupled" finding of §2d) — i.e. whether w is
deletable depends on how its deletion reshapes the *entire* coupling
cycle, not on w's own neighbourhood.  This is the precise reason the
single-vertex relocation route failed (D79: 60/1098 needed multi-vertex
moves) and why §2c's |C(P)| ≤ 4 count was necessary but not sufficient:
all three are local, and the obstruction is not.

**Semantics caveat (sharpening §2e's "not census-observable").**  At
n ≤ 7 every iso-11 config already realizes a mixed value (no
counterexample exists), so the censused "essential" means *deletion
unlocks the **second** mixed value*; a minimal counterexample's
essential means *unlocks the **first***.  The two relations need not
coincide, so these are refutations of locality for the **n ≤ 7
essentiality relation** — strong heuristic evidence, **not proof**, that
the counterexample-version is also non-local.  Since the
counterexample-version lives only at n ≥ 8 (unobservable), this is the
best evidence currently obtainable, and it points the same way as the
n ≤ 6 obstruction structure: the bound is a global-coupling theorem, not
a local-deletion lemma.

> **Honest status (D82).**  Three natural local sufficient conditions
> for deletability are refuted at n = 6 (1440 / 5760 / 1440 essential
> counterexamples; 0 at n = 5).  This is a NEGATIVE result: it closes
> off the local-criterion route to the Insertability Lemma and redirects
> the bound toward the global coupled-ladder structure.  It does not
> prove (or disprove) the bound, and does not bear on Path-FAS ∈ P.

## 2g. The Rung-Compression Lemma is FALSE (D83, global-ladder red-team)

D82 closed the *local* route (deletability is not a vertex-local
property).  The proposed global replacement (the **compression
theorem**) was:

> **Rung-Compression Lemma (conjectured).**  In a minimal D80
> counterexample, contracting the interval between two consecutive rungs
> of the same *role* and same *attachment parity* preserves iso-11 and
> preserves absence of mixed values — so a coupled ladder shortens to one
> of finitely many terminal patterns, giving an O(1) kernel.

This is the right *frame* (it uses the whole ladder word, not one
vertex's degree), and it would give a kernel bound by pigeonhole over the
finitely many role×parity types.  Tested over the iso-rep iso-11 census
(`rung_compression_refutation`, `tests/test_lemma_c_both_values.py`,
back-arc framing), **it is false.**

**Ladder structure (the object).**  The rungs (non-port on-structure
vertices, in C(P) ∪ C(Q)) carry a back-arc graph in σ that is a linear
forest — paths and isolated vertices.  At n = 7 the shapes are: 1 rung
(200), a 2-path (90) or 2 isolated (139), a 3-path (49), edge+isolated
(45), or 3 isolated (4).

**Refutation 1 — no attachment parity works (n = 6).**  For every natural
binary rung invariant (side relative to the inner port; arc to u_Q / v_Q;
σ-back-degree; arc to u_P / v_P), there exist two same-role same-parity
rungs that are **both essential** (`ladder7` probe).  The σ-back-degree
of the two rungs is moreover *always equal* (the rung forest on two
vertices is an edge or two isolated points), so it cannot separate them
at all.  No candidate parity makes essential rungs distinct-typed.

**Refutation 2 — contractions do not preserve the relation (n = 7).**

| contraction | applicable | mixed-set preserved |
|---|---|---|
| remove **middle** of a 3-rung path | 49 | **26** |
| …with all three rungs same role | 13 | **9** |
| remove a **leaf** of a 3-rung path | 98 | **77** |
| remove an **isolated** rung | 535 | 492 |

Each operation changes the realized mixed set on a substantial fraction —
so contracting a same-type segment can **unlock a mixed value**, exactly
what a counterexample-preserving move must not do.

**Refutation 3 — the memory mechanism: jointly-essential twins.**  A
*twin* pair (two rungs with identical arcs to all four port endpoints) is
maximally "redundant", yet **40 of 184** twin pairs at n = 7 (and 2 at
n = 6) are **both essential**: the pair *jointly* blocks a mixed value
that neither blocks alone.  Concretely (n = 6, σ = [5,3,4,1,2,0],
P = 0→5, Q = 2→1): rungs 3 and 4 are twins forming the back-arc edge
{3,4}; R_arc = {00,10,11} (no 01); deleting **either** unlocks 01.  This
is the long-range memory — it lives on the rung back-arc *paths*, not on
single vertices, and removing one end of a path releases the constraint.

**Refutation 4 — rigid all-essential cores exist at every observable
size.**  Distribution of (#rungs, #rungs whose deletion preserves the
mixed set) at n = 7: every rung count contains **rigid** configs (no safe
single deletion) — 11 of 200 at 1 rung, **44 of 229** at 2 rungs, **15 of
98** at 3 rungs.  In the counterexample-like single-mixed regime the
rigidity is total: **100%** of 1-rung (11/11) and 2-rung (44/44)
single-mixed configs are rigid, and 15/53 at 3 rungs.  Note the
all-or-nothing law at 2 rungs (only (2,0) and (2,2) occur, never (2,1)):
the two rungs act as a single coupled unit.

**What this means.**  The kernel bound cannot come from a same-type
contraction lemma: rigid cores resist *every* single-vertex compression,
and the obstruction is genuinely a property of rung *paths* (twins, the
2-rung coupled unit), i.e. long-range memory along the ladder.  The
finite-terminal-pattern pigeonhole fails because the "type" of a rung
does not determine its removability — its neighbours on the path do.

> **Honest status (D83).**  The Rung-Compression Lemma is refuted at
> n ≤ 7 (no parity separates essential rungs; middle/leaf/twin
> contractions fail to preserve the mixed set; rigid cores exist at
> 1, 2, 3 rungs).  This is a NEGATIVE result: it closes the
> contraction-based kernel route just as D82 closed the local-deletion
> route.  It does **not** disprove the kernel *bound* itself (rigid-core
> size is observable only up to 3 rungs, ≤ n = 7), and it has no bearing
> on Path-FAS ∈ P.  The exposed memory — coupled rung paths / twin pairs
> — is the structure any future kernel argument must control, and the
> n ≥ 8 census (first size with ≥ 4 rungs) is where rigid-core growth
> would first become visible.

## 2h. D80 is FALSE at n=8 — the kernel program was chasing a false claim (D84)

D81–D83 reduced "prove D80 for all n" to a kernel bound and then showed
every route to that bound is blocked (local deletion non-local, D82;
same-type contraction fails, D83; rigid cores grow, D83).  The user's
decisive fork was: *do rigid all-essential rung cores grow past 3 rungs
at n = 8?*  A **targeted** n = 8 search (extend each of the 98 pure
3-rung iso-11 n = 7 configs by one vertex over all orientations;
`/tmp` driver, promoted witnesses in `single_port_slide.py`) answers
**yes — and more strongly than expected.**

**The result.**  Among the iso-11 n = 8 extensions:
  * **268** are 4-rung **rigid** cores (all four rungs essential) — so
    rigid cores do grow past 3 rungs;
  * **92** realize **no mixed value at all** (R_arc ⊆ {00,11}) — these
    are outright **D80 counterexamples**: 84 with R_arc = {(1,1)} and
    **8 full EQ_2 gadgets** with R_arc = {(0,0),(1,1)}.

**Two enshrined witnesses** (`D80_COUNTEREXAMPLES_N8`,
`verify_d80_counterexamples`, test `test_d80_refuted_at_n8`), each
re-verified by a self-contained brute-force LFO scan with no shared code:

  1. R_arc = {(1,1)}, ports (0,4)/(5,6), 13 LFOs, iso-11 order
     [6,7,4,2,5,3,1,0] (all four endpoints back-degree 1).  *Every* LFO
     puts both ports as back-arcs.
  2. R_arc = {(0,0),(1,1)} (a genuine **EQ_2** gadget), ports (0,1)/(3,5),
     17 LFOs, iso-11 (capacity on the 11 value).

**Canonical confirmation (4th independent path).**  The project's own
`iso11_eq2_backarc_count(8)` — brute-force `build_lfo_cache` over all 6880
iso-classes, code-disjoint from the extension search, the pruned
enumerator, and the fresh checker — reports at n = 8:
`eq2_gadgets = 5430` (matches the D85 pruned census exactly),
`iso11_gadgets_total = 4146`, `eq2_with_iso11 = 6`,
`iso11_with_no_mixed = 29`, and **`D80_holds_iso11_implies_mixed =
false`**.  So D80 is refuted via the canonical path too, with 29 iso-rep
counterexamples.  (This run takes ~70 min; it is recorded here rather
than pinned as a CI test — the fast `verify_d80_counterexamples` test
locks the witnesses instead.)

**What is refuted (all at n = 8).**
  * **D80** ("iso-11 ⟹ a mixed value") and its restatement "no iso-11
    gadget has R_arc ⊆ {00,11}" (§2d).
  * **"eq2_with_iso11 = 0"** (§3, the n ≤ 7 census claim): 8 EQ_2 gadgets
    are iso-11 at n = 8.
  * The **§2b/§2c Flip Lemma** "both-isolated on the 11 value ⟹ a mixed
    vector is realizable."  The **adjacent**-port sub-case (proved, all
    n) survives — both witnesses are **non-adjacent** (no port pair is
    σ-adjacent), so the failure is exactly the D79 "non-adjacent
    residual," now shown to contain genuine counterexamples.
  * The **saturation mechanism** (§1, §2): an EQ_2 gadget *can* carry an
    isolated (capacity) witness on its both-back-arc value without that
    forcing a mixed vector.

**What is NOT refuted — the equivalence was an overclaim.**  §2d asserted
"D80-for-all-n ⟺ the both-values Lemma C."  That is wrong: D80 ("iso-11
⟹ mixed") is **strictly stronger** than the capacity-form Lemma C ("no
EQ_2 gadget has joint capacity on **both** 0^k and 1^k" = no faithful
splitter).  In the targeted search, of **122** EQ_2 n = 8 gadgets,
**0** have capacity on 00, 8 have capacity on 11 (the iso-11 ones), and
**0 have capacity on both** — so no faithful splitter appears here.  The
Fanout Barrier's actual obligation (capacity-form Lemma C) is therefore
**not** refuted by this search.

**Caveat (search is biased, not a census).**  The extension family is
seeded by iso-11 n = 7 configs, so it is biased toward the 11-value side
and **excludes** capacity-on-00 gadgets (which at n = 7 already exist,
§1).  Hence "0 faithful splitters" here is *not* a proof that the
capacity-form barrier holds at n = 8.  The decisive remaining check is a
**full n = 8 capacity census** (`both_values_saturation_profile`-style,
capacity on both values over all 6880 iso-classes) — the canonical
`iso11_eq2_backarc_count(8)` confirms the D80 refutation (iso11_with_no
_mixed > 0, eq2_with_iso11 > 0) but does not test capacity-on-both.

**Consequences for the program.**
  * D81/D82/D83 were sound *as red-teaming*: they kept finding the kernel
    route blocked because the statement they were trying to prove (D80
    for all n) is **false**.  The "rigid cores grow / long-range memory"
    findings of D82–D83 were the shadow of the n = 8 counterexamples.
  * The Fanout Barrier must be re-grounded directly on the capacity-form
    Lemma C, decoupled from the (false) D80.  Whether that barrier holds
    at n ≥ 8 is now the open question; it is **not** settled here.
  * Methodological: a "verified n ≤ 7, conjectured all n" claim broke at
    the first untested size — exactly the empirical-vs-symbolic caution.

> **Honest status (D84).**  D80 is **disproved** at n = 8 with explicit,
> triply-verified witnesses (test-pinned).  The downstream capacity-form
> Lemma C / Fanout Barrier is **neither proved nor disproved** here — the
> claimed D80⟺LemmaC equivalence was an overclaim, and the biased search
> found no faithful splitter but cannot certify their absence.  Nothing
> here decides Path-FAS ∈ P (refuting an obstruction-conjecture does not
> build a reduction; failing to find a splitter does not build an
> algorithm).

## 2i. The capacity-form barrier SURVIVES at n=8 (D85, decisive census)

D84 decoupled the question: D80 is dead, but the Fanout Barrier's real
obligation is the **capacity-form** both-values Lemma C — *no EQ_2 gadget
has joint capacity on both equality values* (= no faithful EQ_2
splitter).  D85 settles its first untested size by the full census
(`eq2_capacity_census`, pruned LFO enumerator over all tournament
iso-reps, back-arc framing; `tests/test_lemma_c_both_values.py`):

| n | EQ_2 gadgets | cap on 00 | cap on 11 | **cap on both** |
|---|---|---|---|---|
| 6 | 2    | 1   | 0 | **0** |
| 7 | 223  | 16  | 0 | **0** |
| 8 | 5430 | 189 | 6 | **0** |

**The barrier survives at n = 8: cap-on-both = 0** over all 6880
iso-classes — no faithful EQ_2 splitter exists at n ≤ 8.

**But the mechanism changed — the old saturation story is dead.**  At
n ≤ 7 the barrier held because **cap-on-11 = 0**: every realization of the
both-back-arc value saturated a port endpoint (D78 §1, "the 11 value
always saturates").  At n = 8, **cap-on-11 = 6 > 0** — those are exactly
the D84 iso-11 EQ_2 gadgets: an EQ_2 gadget *can* realize 11 with all four
endpoints at back-degree ≤ 1.  So the barrier no longer holds because "11
has no capacity"; it holds because **capacity on 00 (189 gadgets) and
capacity on 11 (6 gadgets) never co-occur in the same gadget**.  The
n ≤ 7 saturation proof sketch (§1, §2) therefore cannot generalize — any
real proof of the barrier must explain the **non-co-occurrence** of the
two capacities directly, not argue that either value individually lacks
capacity.

**Reframed open problem (post-D84/D85).**

> **Capacity-form Lemma C (the live conjecture).**  For every tournament
> and disjoint port pair with R_arc = {(0,0),(1,1)}: not both of "some
> (0,0)-LFO leaves all four endpoints at back-degree ≤ 1" and "some
> (1,1)-LFO leaves all four endpoints at back-degree ≤ 1" hold.
> Verified n ≤ 8 (cap-both = 0).  Open n ≥ 9.

This is the clean statement the Fanout Barrier needs — independent of D80,
the Flip Lemma, and the (dead) saturation mechanism.

> **Honest status (D85).**  No faithful EQ_2 splitter at n ≤ 8 (decisive
> census, cap-both = 0).  The barrier is *empirically* intact one size
> past the D80 collapse, but its old proof mechanism is refuted
> (cap-on-11 > 0 at n = 8), so it has no proof — only verification to
> n = 8.  Per the project's standing caution, n ≤ 8 verification is not a
> theorem.  Nothing here bears on Path-FAS ∈ P.

## 2j. Mining the capacity non-co-occurrence — the separator is GLOBAL (D86)

D85 left one question: *why* do cap-00 and cap-11 never co-occur?  D86
mines the n = 8 dataset (`eq2_capacity_profile`, the first size where both
phenomena appear separately: 189 cap-00, 6 cap-11, 0 cap-both) for a
**separating invariant**.

**First, a surviving equivalence: cap-11 = iso-11.**  Capacity on the
both-back-arc value forces each port endpoint's only back-arc to be its
own port arc (the arc already gives degree 1; capacity caps it at 1), so
both ports are isolated K_2's — that *is* iso-11; conversely iso-11 gives
capacity on 11.  (This is the §2b structural step, which survives D84 —
only "iso-11 ⟹ mixed" was refuted.)  So cap-11 EQ_2 = iso-11 EQ_2, and
cap-both = "iso-11 AND cap-00."

**The cap-11 family is port-locally uniform.**  All 6 cap-11 gadgets are
*distinct* iso-classes yet share a single port-local signature:

  * port-endpoint score order **score(uP) < score(vP) < score(uQ) <
    score(vQ)** (each arc u→v an "upset", P-port below Q-port);
  * 4-vertex port sub-tournament score-sequence **(1,1,2,2)** with the
    cross-arc **vP→uQ**;
  * on the 00 value, the minimum saturated endpoint set is **always
    exactly {vP, uQ}** — the endpoints of that vP→uQ arc.

**But NO port-local invariant separates cap-00 from cap-11.**  Every
candidate overlaps:

| candidate port-local invariant | separates cap-00 vs cap-11? |
|---|---|
| cross-arc pattern (4 bits) | no — (0,0,1,0) in all classes |
| score sequence of T | no |
| port-endpoint score order | no — **2** cap-00 gadgets share uP<vP<uQ<vQ |
| port-quad iso-type | no — **170** cap-00 gadgets share (1,1,2,2) |
| vP–uQ arc direction | no — 170 cap-00 also have vP→uQ |

So **170 cap-00 gadgets are port-locally indistinguishable from the 6
cap-11 gadgets** (same quad-type and cross-arc), and 2 even match the full
port-score-order.  The capacity difference therefore lives in the
**global** arrangement of the between-vertices, not in any statistic of
the four port endpoints — the same non-locality that defeated local
deletion (D82) and same-type contraction (D83).

**Consequence — the proof target is global.**  The user's hoped-for
"incompatible structural **parity**" is not a port-local property; a proof
of the capacity-form Lemma C must argue globally.  The sharpest clean
reformulation:

> **Capacity-form Lemma C (global form).**  No tournament is
> simultaneously **iso-11** (some LFO realizes both port arcs as isolated
> back-arc K_2's) **and cap-00** (some LFO realizes both port arcs forward
> with all four endpoints at back-degree ≤ 1).  These two LFO structures
> cannot coexist in one tournament.  Verified n ≤ 8; open n ≥ 9.

The empirical hook for a proof: in every cap-11 gadget the **unique**
00-witness saturates exactly {vP, uQ} (the vP→uQ arc's endpoints) — i.e.
the iso-11 structure forces that one 00-order to overload that arc.  Why
the global iso-11 arrangement forces this on *every* 00-order (not just
the witnessed one) is the open mechanism.

> **Honest status (D86).**  The capacity separator is empirically
> GLOBAL: no port-local invariant distinguishes the 6 cap-11 from 170
> port-locally identical cap-00 gadgets at n = 8.  cap-11 = iso-11 is a
> proved equivalence.  No separator ⇒ (per the agreed protocol) the next
> empirical move is an n = 9 capacity hunt; the next *proof* move is a
> global argument for iso-11 / cap-00 incompatibility.  Nothing here bears
> on Path-FAS ∈ P.

## 2k. Global proof attempt — the cap-00 lever, and where it stalls (D87)

Target (≡ capacity-form Lemma C ≡ no faithful EQ_2 splitter):

> No EQ_2 gadget (R_arc = {00,11}, **no mixed value**) is both **iso-11**
> (an LFO σ₁ with both port arcs isolated back-arc K_2's) and **cap-00**
> (an LFO σ₀ with both port arcs forward, all four endpoints back-degree
> ≤ 1).

Throughout, C(P) = {w : v_P→w and w→u_P} are the 3-cycle partners of P's
arc; by the 3-Cycle Characterization (proved) these are exactly the
between-vertices of P in any order where P is an isolated back-arc — in
particular in σ₁.

> **The cap-00 lever (PROVED; verified n ≤ 8, 0 violations).**  cap-00 ⟹
> |C(P)| ≤ 2 and |C(Q)| ≤ 2.
>
> *Proof.*  In σ₀ both port arcs are forward, so u_P precedes v_P, and
> each endpoint has back-degree ≤ 1.  Take w ∈ C(P).  If w is before v_P,
> the arc v_P→w runs backward, a back-arc at v_P.  If w is after v_P
> (hence after u_P, since u_P < v_P), the arc w→u_P runs backward, a
> back-arc at u_P.  Distinct partners give distinct such back-arcs, so
> #{w∈C(P): before v_P} ≤ deg_{σ₀}(v_P) ≤ 1 and #{w∈C(P): after v_P} ≤
> deg_{σ₀}(u_P) ≤ 1.  Hence |C(P)| ≤ 2; symmetrically |C(Q)| ≤ 2. ∎

This is the first structural consequence extracted from the cap-00
witness: a faithful-splitter candidate has *tiny* 3-cycle-partner sets.

**Clean conditional finish (nested geometry).**  Suppose in σ₁ the ports
are **nested** — say Q's interval lies inside P's.  Every vertex strictly
between v_P and u_P is in C(P) (3-Cycle Characterization), and that
includes u_Q, v_Q and all of C(Q); so C(P) ⊇ {u_Q,v_Q} ∪ C(Q) and
|C(P)| ≥ 2 + |C(Q)|.  With the lever (|C(P)| ≤ 2) this forces |C(Q)| = 0,
i.e. u_Q, v_Q are **adjacent** in σ₁.  Then the **Adjacent-Port Flip
Lemma** (proved, all n; §2b) swaps them to realize a mixed value,
contradicting EQ_2. ∎ (nested case)

**Where it stalls — the geometry is crossing, and the lever is not
sufficient.**  Two facts (verified n ≤ 8, `cap00_3cycle_bound`) block the
finish:

  1. **Every iso-11 EQ_2 gadget at n ≤ 8 is CROSSING**, never nested
     (6/6 at n = 8; none at n ≤ 7).  So the clean nested finish above is
     *vacuous* at the sizes we can see — the real case is crossing, where
     C(P) and C(Q) each contain exactly one endpoint of the *other* port
     (v_Q ∈ C(P), u_P ∈ C(Q)) but neither contains the other.  Neither
     port is forced adjacent, so the Adjacent-Port Flip Lemma does not
     apply.
  2. **|C| ≤ 2 is NOT sufficient.**  There is a crossing iso-11 EQ_2
     gadget (P = (1,3), Q = (4,6) on an explicit n = 8 tournament) with
     |C(P)| = |C(Q)| = 2 and **no mixed value** — it satisfies the
     cap-00 *conclusion* |C| ≤ 2 yet is *not* cap-00.  So "iso-11 ∧
     |C(P)| ≤ 2 ∧ |C(Q)| ≤ 2 ⟹ mixed" is **false**; the proof must use
     the cap-00 witness σ₀ *beyond* the |C|-bound it implies.

So the global proof reduces to the **crossing case**, and there the
cap-00 hypothesis must be exploited more fully than via |C(P)|, |C(Q)|
≤ 2 alone — e.g. by combining σ₀ (the light 00-order) and σ₁ (the
isolated 11-order) into an explicit mixed order, which the |C| ≤ 2 bound
makes structurally small (the core has ≤ 2 non-port on-structure
vertices) but does not by itself construct.

> **Honest status (D87).**  Genuine partial progress on a *global* proof:
> the cap-00 lever (|C| ≤ 2) is a new theorem (verified n ≤ 8), and the
> nested case is closed cleanly via the Adjacent-Port Flip Lemma.  But
> the proof is **NOT complete**: the realized geometry is crossing (where
> the nested finish is vacuous), and |C| ≤ 2 is provably insufficient, so
> the crossing case using the full strength of cap-00 remains open.
> Nothing here bears on Path-FAS ∈ P.

## 2l. Expert-team attack on the Crossing Splice Lemma (D88)

A 6-agent workflow (4 parallel miners → synthesis → prove/verify/decide,
adversarial verifiers) attacked the crossing case of §2k.  Every
load-bearing claim below was **independently re-verified** with separate
code (`eq2_outdeg_separator`, `tests/test_lemma_c_both_values.py`).

**Result 1 — the Crossing Splice Lemma is REFUTED (as a local reorder).**
All 6 iso-11 EQ_2 gadgets at n = 8 are crossing with a rigid σ₁ core word
v_Q < [C(Q)] < v_P < u_Q < [C(P)] < u_P (both port arcs isolated K_2's,
v_P ∈ C(Q), u_Q ∈ C(P), adjacent at the center).  The natural splice
move — flip one port forward by sliding its far endpoint across its own
C-set — is uniform in *shape* across all 6 gadgets but **never yields a
linear forest**: over every mixed-bit ordering the minimum back-degree
excess is exactly **+1**, always a single C-vertex driven to back-degree
3, never a cycle (12/12 cases).  Mechanism: C(P), C(Q) are the
between-vertices of an isolated back-arc (3-Cycle Characterization), so
the ladder wedges a C-vertex between v_P and u_Q; that vertex absorbs the
third back-arc the instant a port flips.  The cap-00 "lightness" that
would avoid the overload is antithetical to iso-11 port-isolation.  (Also:
cap-00 σ₀ witnesses are geometrically bimodal — both crossing and
disjoint occur — while iso-11 is uniformly crossing, so no single
σ₀→σ₁ template even aligns.)  So no splice closes the crossing case.

**Result 2 — a clean GLOBAL out-degree separator (verified n ≤ 8).**  On
the port-local-signature-matched family (port-quad score-seq (1,1,2,2)
AND cross-arc v_P→u_Q), with out-degrees in the full tournament:

  * **iso-11 ⟹** out(u_P) < out(v_P) **and** out(u_Q) < out(v_Q) — sign
    pattern (<,<); moreover every iso-11 EQ_2 gadget is
    signature-matched.  [6/6 at n = 8]
  * **cap-00 ⟹** *neither* out(u_P) < out(v_P) *nor* out(u_Q) < out(v_Q).
    [170/170 at n = 8 — of which 156 strict (>,>) and **14 with one
    tie**.]

These are mutually exclusive, so cap_both = 0 on the matched family; and
since iso-11 ⟹ matched, the separator covers all iso-11 gadgets — a
**re-derivation of the capacity-form barrier from a single global
out-degree invariant**.  (Correction enshrined: the cap-00 side is "no
'<' on either port", **not** strict (>,>); the latter fails 14/170 at
n = 8.  The lone cap-00 gadget with the iso-11 sign (<,<), rep
P=(0,3),Q=(5,7), is *not* signature-matched — quad (2,3,4,5), cross-arc
u_Q→v_P — so it does not break the matched-family invariant.)

**The residual is SINGULAR.**  Over the 6 iso-11 EQ_2 gadgets the
C-sizes are {(3,2):2, (3,3):1, (2,3):2, (2,2):1}; the D87 lever (cap-00
⟹ |C| ≤ 2) already kills the 5 with a |C| = 3 port.  Exactly **one**
gadget — the crossing |C| = (2,2) case P=(1,3), Q=(4,6) — survives the
lever and is the entire crux.

> **Honest status (D88).**  The splice route is dead (refuted).  The
> out-degree separator is a clean, independently-verified global invariant
> that re-derives cap_both = 0 — but it is **verified n ≤ 8, not proved**,
> and at n = 8 the whole residual is a single gadget, too thin to certify
> that a global proof generalizes.  Recommended next step is the **n = 9
> capacity hunt** (measured feasible: reps(9) ≈ 191 536 classes, full
> pruned census ≈ 38 min single-thread / ≈ 5 min on 8 cores — no sampling
> needed): if cap_both > 0 the barrier collapses (a faithful splitter
> exists — decisive negative); if cap_both = 0 with a richer iso-11
> sample, promote the out-degree invariant to the proof target.  Nothing
> here bears on Path-FAS ∈ P.

## 2m. The n=9 capacity hunt — barrier SURVIVES, separator DIES (D89)

Full exhaustive n = 9 capacity census, parallelized over all 191 536
tournament iso-classes (12 workers, pruned enumerator, ~5.4 min wall;
my own census code, logic validated vs the canonical census at n ≤ 8).

**Headline — the Fanout Barrier survives n = 9: cap_both = 0.**

| n | EQ_2 gadgets | cap-00 | cap-11 (= iso-11) | **cap-both** |
|---|---|---|---|---|
| 8 | 5 430  | 189   | 6   | **0** |
| 9 | 81 875 | 1 806 | 108 | **0** |

No faithful EQ_2 splitter at n ≤ 9 — strong new evidence for the
capacity-form Lemma C.  (Detection is sign-independent: every worker
flags iso-11 and cap-00 separately for every gadget, so cap_both = 0
means no gadget carries both, regardless of out-degrees.)

**The D88 out-degree separator is REFUTED at n = 9.**  The n = 8
separator was overfit to the 6-gadget iso-11 sample; with 108 iso-11
gadgets it collapses on every clause:

  * iso-11 is **not** always (<,<): sign multisets are {<,<}: 100 and
    **{<,=}: 8** (a tie).
  * iso-11 is **not** always signature-matched: **4 iso-11 gadgets have
    a transitive port-quad (0,1,2,3) and the *opposite* cross-arc
    u_Q→v_P** — the n = 8 "signature" (quad (1,1,2,2), v_P→u_Q) is not
    necessary for iso-11.
  * the **weaker** form fails too: over *all* cap-00 gadgets the sign
    multisets are {>,>}: 1394, {=,>}: 388, {=,=}: 12, {<,>}: 8, and
    **{<,<}: 4** — so 4 cap-00 gadgets share iso-11's (<,<) sign.  An
    explicit such gadget was fresh-brute-verified (upper-triangle bits
    `000000000110000001000001101000101010`, P=(1,4), Q=(6,8); arcs 1→4,
    6→8; out(uP)=3<out(vP)=4 and out(uQ)=5<out(vQ)=6): R_arc={00,11},
    cap-00 holds, **not** iso-11.  No out-degree multiset separates
    iso-11 from cap-00.

So the out-degree separator route joins local deletion (D82), same-type
contraction (D83), and the crossing splice (D88) on the pile of
**refuted local/statistical mechanisms**: cap_both = 0 holds through
n = 9 but is *not* explained by any port-endpoint statistic.  The
separator, if one exists, is genuinely global.

**The residual is no longer singular.**  At n = 8 the D87 lever (cap-00
⟹ |C| ≤ 2) left a single |C| = (2,2)-crossing iso-11 gadget as the crux;
at n = 9 there are **12** such gadgets, and the iso-11 family (108) is
now a real sample for structural analysis (4 even have transitive port
quads, a shape absent at n = 8).

> **Honest status (D89).**  capacity-form Lemma C / the Fanout Barrier is
> verified n ≤ 9 (cap_both = 0; 81 875 EQ_2 gadgets at n = 9) — robust
> empirical support.  But every proposed proof mechanism is now refuted
> (local deletion, contraction, splice, out-degree separator), and the
> n = 9 data killed the most recent candidate (D88) on a richer sample.
> No proof; the barrier holds for reasons not captured by any
> port-endpoint invariant found so far.  Per the standing caution,
> n ≤ 9 verification is not a theorem.  Nothing here bears on
> Path-FAS ∈ P; it bounds one NP-hardness reduction family.

## 3. Status

  * **Corrected Lemma C** (both-values): the operative statement.
  * **Saturation mechanism**: verified exhaustively at n ≤ 7 (all 16
    cap-on-00 EQ_2 gadgets saturate all four endpoints on the 11
    value).
  * **Adjacent-Port Flip Lemma: PROVED (all n)** — §2b.  Proves Lemma C
    for every gadget whose both-back-arc value has an isolated LFO with
    an adjacent port pair (≈ 66% of configs at n ≤ 5).
  * **Non-adjacent residual: the irreducible open core.**  Equivalent
    to Lemma C on the remaining ≈ 34%.  Verified n ≤ 5 (Flip Lemma
    holds: 3228/3228); single-vertex relocation covers 1038/1098 but
    60 need multi-vertex moves, so no bounded-local-move proof.  Open
    n ≥ 6 in general.
  * The single-port slide (D77) gives the blocker classification
    (Lemmas S1, S3) but from one witness only re-establishes
    consistency with EQ_2 — not a both-values attack.
  * **Two-port coupled flip theorem (D80): verified n ≤ 7** — §2d.
    iso-11 ⟹ a mixed value (the 00 hypothesis is not needed).  Over
    iso-reps in the unambiguous back-arc framing: 0 iso-11 gadgets with
    R_arc ⊆ {00,11} at n = 6 (103 iso-11) and n = 7 (588 iso-11);
    0 EQ_2 gadgets with iso-11.  Obstruction (n ≤ 6): always a **cycle**
    (3600/3600, 0 degree), geometry always **nested**, block always
    **coupled** (0 intrinsic), shortest cycle a triangle or a 6-cycle
    threading both port arcs (the ladder).  **Equivalence Lemma (all n):
    both-nonflippable ⟺ R_arc ⊆ {00,11}, so D80-for-all-n ⟺ the
    both-values Lemma C** — every route returns to the open core; no
    all-n proof found.
  * **Insertability bound is non-local (D82): negative result** — §2f.
    The three natural local sufficient conditions for deletability
    (σ-isolation, single-C "outer rung" membership, degree floor) are
    each refuted at n = 6 (1440 / 5760 / 1440 essential counterexamples;
    0 essential at n = 5).  Deletability is not a local property of w;
    the kernel bound must invoke the global coupled-ladder structure.
  * **Rung-Compression Lemma is FALSE (D83): negative result** — §2g.
    The global-ladder replacement (contract between two same-role
    same-parity rungs ⟹ relation preserved) fails at n ≤ 7: no parity
    separates essential rungs; removing the middle / leaf of a same-role
    rung path preserves the mixed set only 9/13, 77/98; 40/184 twin pairs
    are jointly essential (the long-range memory); rigid all-essential
    cores exist at 1, 2 and 3 rungs (11/44/15) and are 100% of
    single-mixed configs at 1–2 rungs.  The kernel bound cannot come from
    same-type contraction — the obstruction lives on rung back-arc paths.
  * **⚠️ D80 is FALSE at n=8 (D84): the conjecture being chased was
    false** — §2h.  Targeted n=8 search: 268 four-rung rigid cores and
    **92 no-mixed counterexamples** (84 with R_arc={11}, 8 EQ_2), two
    triply-verified and test-pinned.  Refutes D80, "no iso-11 gadget has
    R_arc⊆{00,11}", "eq2_with_iso11=0", the Flip Lemma (non-adjacent
    residual) and the saturation mechanism.  The D80⟺Lemma C equivalence
    was an OVERCLAIM; the capacity-form Fanout Barrier (no EQ_2 with
    capacity on both) is NOT refuted here (0/122) but not certified
    either (biased search).  D81/D82/D83 were blocked because D80 is
    false.
  * **Capacity-form barrier SURVIVES at n=8 (D85): decisive census** —
    §2i.  Full census (all 6880 iso-classes): 5430 EQ_2 gadgets, 189
    cap-on-00, **6 cap-on-11**, **0 cap-on-both** — no faithful EQ_2
    splitter at n ≤ 8.  Old "11 always saturates" mechanism DEAD
    (cap-on-11 0→6); barrier now holds via non-co-occurrence of the two
    capacities.  Live conjecture: capacity-form Lemma C, verified n ≤ 8,
    open n ≥ 9.
  * **Capacity separator is GLOBAL (D86): mining result** — §2j.
    cap-11 = iso-11 (proved equivalence).  The 6 cap-11 gadgets share a
    uniform port-local signature (score-order uP<vP<uQ<vQ, quad (1,1,2,2),
    vP→uQ, 00-saturation {vP,uQ}) — but **170 cap-00 gadgets share it**,
    so NO port-local invariant separates the classes.  The separator is
    global; the proof target is "no tournament is both iso-11 and
    cap-00."
  * **Global proof attempt: cap-00 lever, partial (D87)** — §2k.
    PROVED (verified n≤8): **cap-00 ⟹ |C(P)| ≤ 2 ∧ |C(Q)| ≤ 2** (charging
    in σ₀; C = 3-cycle partners).  Nested case closed via Adjacent-Port
    Flip Lemma.  But iso-11 EQ_2 gadgets are all CROSSING at n≤8 (nested
    finish vacuous), and |C|≤2 is provably insufficient (a crossing
    iso-11 EQ_2 gadget with |C|=(2,2), no mixed, exists).  Crossing case
    using full cap-00 strength remains OPEN; proof incomplete.
  * **Expert-team attack: splice refuted, out-degree separator found
    (D88)** — §2l.  Crossing Splice Lemma REFUTED as a local reorder (the
    uniform flip always drives a C-vertex to back-degree 3, +1 excess,
    never a cycle; 12/12).  GLOBAL out-degree separator that held at n=8
    (iso-11 ⟹ (<,<) ∧ matched, 6/6; cap-00 matched ⟹ no '<', 170/170) —
    but it was a small-sample artifact (see D89).
  * **n=9 hunt: barrier SURVIVES, separator DIES (D89)** — §2m.  Full
    parallel n=9 census (191 536 classes): 81 875 EQ_2, 1 806 cap-00,
    108 iso-11, **cap_both = 0** ⟹ Fanout Barrier survives n ≤ 9.  But the
    D88 out-degree separator is REFUTED on the richer 108-gadget sample:
    iso-11 not always (<,<) (8 are {<,=}), iso-11 not always matched (4
    transitive-quad/u_Q→v_P), and 4 cap-00 gadgets share iso-11's {<,<}
    sign (fresh-verified) — no out-degree multiset separates the classes.
    All local/statistical mechanisms (D82/D83/D88/D89) refuted; the
    separator is genuinely global and still unknown.

## 4. Honest scope and what this does NOT give

Proving the Saturation sub-claim (hence Lemma C, hence the Fanout
Barrier) would **block the clause-and-fanout NP-hardness program** —
it would **not** prove Path-FAS ∈ P (ruling out one reduction family is
not a polynomial algorithm).

## 5. Files and tests

| artefact | location |
|---|---|
| Recount + saturation profile | `scripts/single_port_slide.py` (probe), `tests/test_lemma_c_both_values.py` |
| Corrected Lemma C statement | `docs/fanout_barrier_theorem.md` §4, `docs/fanout_barrier_synthesis.md` |
| Single-port slide (blocker classification) | `docs/single_port_slide.md` |
| Two-port coupled flip (D80, §2d) | `scripts/single_port_slide.py::two_port_coupled_flip`, `tests/test_lemma_c_both_values.py` |
| D80 full check + framing resolution (n≤7) | `scripts/single_port_slide.py::iso11_eq2_backarc_count` |
| Obstruction structure (nested / coupled / ladder) | `scripts/single_port_slide.py::coupling_structure`, `intrinsic_vs_coupled` |
| Kernelization foundation (D81, §2e) | `scripts/single_port_slide.py::kernel_lemmas_check`, `tests/test_lemma_c_both_values.py` |
| Insertability-bound-is-non-local (D82, §2f) | `scripts/single_port_slide.py::essential_locality_refutation`, `tests/test_lemma_c_both_values.py` |
| Rung-Compression-Lemma-refuted (D83, §2g) | `scripts/single_port_slide.py::rung_compression_refutation`, `tests/test_lemma_c_both_values.py` |
| D80-refuted-at-n8 witnesses (D84, §2h) | `scripts/single_port_slide.py::{D80_COUNTEREXAMPLES_N8,verify_d80_counterexamples}`, `tests/test_lemma_c_both_values.py::test_d80_refuted_at_n8` |
| Capacity-form census (D85, §2i, decisive) | `scripts/single_port_slide.py::eq2_capacity_census`, `tests/test_lemma_c_both_values.py::test_eq2_capacity_census_*` |
| Capacity separator mine (D86, §2j) | `scripts/single_port_slide.py::eq2_capacity_profile`, `tests/test_lemma_c_both_values.py::test_eq2_capacity_profile_no_local_separator_n8` |
| cap-00 lever + proof attempt (D87, §2k) | `scripts/single_port_slide.py::cap00_3cycle_bound`, `tests/test_lemma_c_both_values.py::test_cap00_3cycle_bound_lever_n7_n8` |
| Out-degree separator (D88, §2l) | `scripts/single_port_slide.py::eq2_outdeg_separator`, `tests/test_lemma_c_both_values.py::test_outdeg_separator_n8` |
| n=9 capacity hunt (D89, §2m) | `scripts/single_port_slide.py::{eq2_capacity_census,eq2_outdeg_separator}` at n=9 (slow, single-thread ≈ 56 min; parallelize over `reps(9)` chunks for ≈ 5 min) |
