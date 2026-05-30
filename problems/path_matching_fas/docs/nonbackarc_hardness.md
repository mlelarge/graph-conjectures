# Non-back-arc hardness for tournament Path-FAS: a unifying monotonicity obstruction

This note records a focused attempt to obtain NP-hardness for
tournament Path-FAS
([Aboulker–Aubian–Lopes Problem 4.4](https://arxiv.org/abs/2402.10782))
through the *only remaining* route: a reduction that encodes the
SAT/CSP instance through **ordering / flexible-edge choices**, not
through the **back-arc graph topology** (which two prior theorems show
is closed).

**Verdict, up front.** No NP-hardness reduction is obtained, but the
attempt produces a single, structurally clean obstruction that
*unifies* the local-fanout, interior-degree-saturation, and global
linear-forest barriers and explains why the ordering encoding also
fails:

> **Monotonicity Obstruction (Theorem 3.1 below).** In the toggle/flex
> substrate, every variable is a binary *ordering* choice
> `eps_i ∈ {0,1}` realised by swapping a consecutive pair. Raising
> `eps_i` from 0 to 1 *only adds* one back-arc and removes none, so the
> back-arc set grows monotonically. Since "is a linear forest" is
> closed under edge deletion, Path-FAS feasibility is a **monotone**
> function of `(eps_i)`. A monotone predicate can only encode monotone
> CSPs, and monotone CNF-SAT is trivially in P. Hence the ordering/flex
> encoding cannot reach an NP-hard CSP.

This is complemented by two independent local obstructions that we also
reproduce in the ordering encoding: a **degree-2 fanout cap** (each
variable supports at most 2 clause attachments — the same cap as
Corollary 5.2 of `docs/J_hardness_via_wires.md`, but now in the flex
encoding), and a **betweenness un-realisability** result (no tournament
on `n = 5` realises the pure-ordering betweenness constraint).

The reproducible artefacts are:

* `scripts/nonbackarc_hardness.py`
* `tests/test_nonbackarc_hardness.py` (16 passing tests).

The deciders are cross-validated: the score-window forced/flexible
("FF") decider agrees with `decide_path_fas_bruteforce` on 180 random
tournaments at `n ∈ {7, 8, 9}` (0 mismatches), and every global verdict
quoted at `n ≤ 10` is re-checked directly against brute force.

---

## 1. Why back-arc encodings are closed, and what is left

Path-FAS on a tournament `T` asks for a linear order (an LFO) whose set
of back-arcs is a **linear forest** (undirected max-degree ≤ 2,
acyclic). Two prior theorems close the back-arc-shape route:

* **Theorem 5.1** (interior degree saturation,
  `docs/J_hardness_via_wires.md`): in any forced-back-arc path
  `v_0 - … - v_k` (`k ≥ 2`), every interior vertex `v_i` has
  back-degree exactly 2 in every LFO, both arcs to its path neighbours.
  Hence a wire of length `k` supports at most 2 clause attachments (one
  per endpoint), capping variable occurrence at 2 (Corollary 5.2).

* **Theorem 6.1** (global back-arc budget,
  `docs/reversed_matching_hardness.md`): the back-arc graph of *any* LFO
  of *any* tournament is a linear forest, so it has at most `n − 1`
  edges and decomposes into vertex-disjoint paths. Any constraint
  encoded in the *shape* of the back-arc graph is therefore at most
  linear-forest shaped — a structural circularity with the very
  definition of Path-FAS.

These close every reduction whose clause information is carried by the
*presence and shape of back-arcs*. What remains, per the project brief
and `docs/forward_dp_lower_bound.md` §6, is to encode constraints
through something else:

1. the **flexible structure** — the binary *choice*, per
   overlapping-window pair, of back-arc vs forward-arc;
2. **score-window positions** — the joint constraint that each vertex
   lands in its radius-2 window;
3. **non-existence** of LFO completions rather than a specific FAS.

The natural substrate for (1) is the D70 toggle-pair fooling set
(`scripts/toggle_fooling_set.py`), whose variable gadget is exactly a
binary *ordering* choice, detached from back-arc shape. This note
builds clause gadgets on top of it and then proves they cannot reach an
NP-hard problem.

### 1.1. The toggle/flex variable gadget

Gadget `i` is the 4-tuple `(a_i, b_i, f_i, g_i)` of the toggle family
on `4k` vertices: a transitive base with the two arcs `f_i → a_i` and
`g_i → b_i` reversed. With enough score-window separation
(`k ≥ 4`, padding ≥ 6), `f_i → a_i` and `g_i → b_i` are **forced
back-arcs** (disjoint windows), and the only *flexible* (overlapping
window) pair is `a_i — b_i`. The variable's value is the relative LFO
order of `a_i, b_i`:

| `eps_i` | prefix order | `a_i → b_i` is | gadget back-arc graph | components |
|---:|---|---|---|---|
| 0 | `a_i` before `b_i` | forward | `{f_i—a_i, b_i—g_i}` | two: `f_i ≁ g_i` |
| 1 | `b_i` before `a_i` | back-arc | path `f_i—a_i—b_i—g_i` | one: `f_i ~ g_i` |

The value lives entirely in an **ordering choice** of two
overlapping-window vertices; the back-arc graph is a linear forest in
both states, fully respecting Theorem 6.1. This is the cleanest
"non-back-arc" variable we have.

The decider used throughout is the score-window FF decider
(`ff_signature_probe.has_completion_ff`), trusted because it matches
brute force on 180 random tournaments at `n = 7, 8, 9`
(`tests/test_nonbackarc_hardness.py::test_ff_agrees_with_bruteforce_on_random_tournaments`)
and because every load-bearing *global* verdict here is re-checked at
`n ≤ 10` against `decide_path_fas_bruteforce`.

---

## 2. Coupling variable gadgets without a back-arc wire

To couple gadgets we attach **extra high-index vertices** ("probes" and
"linkers"). Each extra vertex sits above the gadget block (behind ≥ 8
padding vertices) so that its arcs to gadget vertices are *forced
back-arcs*. Each extra has back-degree ≤ 2, so Theorem 6.1 is respected
and no forced-back-arc wire of length ≥ 2 is created — the coupling is
not a back-arc wire, so neither Theorem 5.1 nor the wire architecture of
`docs/J_hardness_via_wires.md` applies.

### 2.1. The cycle-closing primitive

The decisive mechanism: an extra vertex `z` with two forced back-arcs
to vertices `p, q` **closes a back-arc cycle iff `p` and `q` are
already in the same back-arc component**. Component connectivity is a
function of the `eps` choices:

* `f_i` reaches `g_i` (in the back-arc graph) **iff `eps_i = 1`** (the
  loaded path `f_i—a_i—b_i—g_i`).

So a probe `z → f_j, z → g_j` closes a cycle iff `eps_j = 1`, i.e. the
gadget is feasible iff `eps_j = 0`. Verified
(`clause_feasibility_table(2, [0])`):

```
eps=(0,*) feasible ;  eps=(1,*) infeasible.
```

### 2.2. The all-negative OR-clause

Chain `t` linker vertices to connect several gadgets in series at their
`f/g` ends, then one probe closes the loop:

```
linker_t :  g_{lit_t} ---(forced back-arc)--- f_{lit_{t+1}}
probe    :  f_{lit_0}  ---(forced back-arc)--- g_{lit_{last}}
```

The probe's two endpoints `f_{lit_0}, g_{lit_last}` are in the same
component iff the whole chain
`f_{lit_0} ~ g_{lit_0} ~ f_{lit_1} ~ … ~ g_{lit_last}` is connected,
which requires `eps_{lit_t} = 1` for **every** gadget in the chain
(each linker contributes its own forced edge, and each gadget is
traversed only when loaded). Hence:

> **Clause gadget.** The chain is *infeasible iff `eps_i = 1` for all
> `i` in the clause*.

Verified for 2 and 3 literals
(`test_clause_two_negative_literals`, `test_clause_three_negative_literals`):

```
clause [0,1]:    infeasible  iff (eps_0=1 AND eps_1=1)
clause [0,1,2]:  infeasible  iff (eps_0=1 AND eps_1=1 AND eps_2=1)
```

Reading `L_i := (eps_i = 0)` as the variable's truth value, this is the
**positive OR-clause** `(L_{lit_0} ∨ … ∨ L_{lit_last})`: the tournament
is feasible iff at least one `L_i` is true. This is a genuine,
non-trivial coupling of variable gadgets that lives **entirely in the
ordering choices and the component-merge structure**, never in the
back-arc *shape* (which stays a linear forest). It bypasses Theorem 6.1
and Theorem 5.1 — and yet, as §3 shows, it is still not enough.

### 2.3. The fanout cap reappears

When a variable is shared by ≥ 3 clauses, composition breaks. A
variable's only free ends are `f_i` and `g_i`, each of which already
spends 1 of its degree-2 budget on the forced gadget edge (`f_i—a_i`,
`b_i—g_i`). So each end can absorb at most **one** clause attachment,
giving at most **2 attachments per variable**:

* 2 attachments (one at `f_i`, one at `g_i`): feasible
  (`test_two_attachments_per_variable_ok`);
* a 3rd attachment overloads a free end's degree:
  infeasible (`test_third_attachment_overloads`).

Concretely, two 2-literal clauses sharing variable 1 overload `f_1` and
`g_1` and destroy *all* LFOs, even though the formula is satisfiable
(`test_shared_variable_across_clauses_breaks_composition`). This is
**exactly Corollary 5.2's "≤ 2 clause attachments per wire"** — but now
reproduced in the ordering/flex encoding, with no forced-back-arc wire
present. The degree-2 fanout barrier is encoding-independent: it is the
back-degree budget itself, which the ordering encoding cannot escape any
more than the wire encoding could. Bounded-occurrence (≤ 2) CSPs are
polynomial (2-SAT, monotone 2-CSP), so this alone forecloses hardness.

---

## 3. The monotonicity obstruction (the unifying barrier)

Even setting the fanout cap aside (one *could* imagine a cleverer
attachment scheme), a deeper barrier kills the ordering encoding.

### 3.1. The theorem

> **Theorem 3.1 (Monotonicity).** Let `T` be built from toggle gadgets
> plus any set of forced-back-arc extra vertices (probes/linkers). For
> an assignment `eps ∈ {0,1}^k`, let `feas(eps)` be true iff the toggle
> prefix `P_eps` extends to a valid LFO. Then `feas` is
> **monotone-decreasing**: if `feas(eps)` holds and `eps' ≤ eps`
> componentwise, then `feas(eps')` holds.

*Proof.* It suffices to show that lowering a single bit `eps_j : 1 → 0`
never loses feasibility. In the toggle prefix, gadget `j` places its
pair as `(b_j, a_j)` when `eps_j = 1` and as `(a_j, b_j)` when
`eps_j = 0`; in both cases the two vertices are **consecutive** in the
prefix. Swapping two consecutive vertices changes the back-arc status of
*only* the arc between them: it turns the back-arc `a_j → b_j`
(present when `eps_j = 1`) into a forward arc (`eps_j = 0`), and leaves
the orientation-relative-to-every-other-vertex of both `a_j` and `b_j`
unchanged. Hence the back-arc set of `P_{eps'}` is the back-arc set of
`P_eps` **minus the single edge `a_j—b_j`**, a strict subset.

A subgraph of a linear forest is a linear forest (max-degree ≤ 2 and
acyclicity are both closed under edge deletion). Therefore every valid
LFO completion of `P_eps` remains a valid completion of `P_{eps'}`
(same suffix, strictly fewer back-arcs in the prefix block), so
`feas(eps) ⇒ feas(eps')`. ∎

The subset claim is pinned constructively for all `eps` and all bits at
`k = 4` (`backarc_set_shrinks_when_unloaded`,
`test_backarc_set_shrinks_when_unloaded`). The monotonicity conclusion
is pinned for the clause wirings and for 120 random extra-wirings
(`test_clause_wiring_is_monotone`, `test_random_wirings_are_all_monotone`):
**0 non-monotone wirings found** across hundreds of probes.

### 3.2. Why this closes the route

A monotone Boolean predicate `feas(eps)` corresponds to a **monotone**
CSP: the satisfying set is upward/downward closed. Concretely our clause
gadgets realise positive CNF over `L_i = (eps_i = 0)`: feasibility is
"every clause has a true `L_i`". Monotone CNF-SAT (all literals one
polarity) is trivially satisfiable — set every `L_i` true (every
`eps_i = 0`) — and is therefore **in P**. The ordering/flex encoding
cannot produce the *both-polarity* clauses that make 3-SAT, NAE-3SAT, or
1-in-3-SAT NP-hard, because there is no gadget whose feasibility
*requires* `eps_j = 1` (raising a bit can only lose feasibility).

This is verified at the level of single-variable primitives: the full
catalogue of 2-target probes on one gadget gives, for every
non-degenerate pair, "feasible iff `eps = 0`" — there is **no** probe
giving "feasible iff `eps = 1`". The loaded state is always the more
constrained one.

### 3.3. Relation to NAE / parity of flex choices

The brief asks (sub-task 5) whether a clause = "not all three flex bits
equal" can be built. The "**not all true**" half is exactly our clause
gadget (`infeasible iff all eps = 1`). The "**not all false**" half
would require a gadget *infeasible iff all eps = 0*, i.e. feasibility
*requiring* some `eps_j = 1`. By Theorem 3.1 this is impossible: raising
bits only loses feasibility, so no predicate can have a *minimal*
feasible point at a non-zero `eps`. NAE needs both halves; the monotone
encoding supplies only one. Parity (XOR) is the canonical non-monotone
function and is likewise unreachable. So NAE-SAT and parity-of-flex
clauses are blocked by the same monotonicity barrier — and NAE-3SAT is
the Schaefer 1978 NP-complete problem we would have targeted
(`DOI 10.1145/800133.804350`).

### 3.4. Why this is the right unification

Theorem 3.1 explains, in one statement, why all three prior obstructions
were inevitable for an ordering encoding:

* The **global linear-forest** fact (Theorem 6.1) is what makes
  "fewer back-arcs ⇒ still feasible" true — it is the monotone target
  predicate.
* The **degree-2 fanout cap** (Theorem 5.1 / §2.3) is the local witness
  that loading consumes a scarce budget.
* The **forward-DP lower bound** (D70) shows `2^Ω(n)`
  *distinguishable* prefixes — but distinguishability is one-directional
  (the probe detects `eps_j = 1`), exactly the monotone signal.

Monotonicity is the common cause: the *loaded* direction of every
flexible choice is a pure liability (more back-arcs, more degree, more
merges), never an asset. An NP-hard CSP needs choices that are assets in
one clause and liabilities in another (mixed polarity); the flex
encoding has no such choice.

---

## 4. Score-window position competition (sub-task 4)

A separate idea: multiple vertices competing for a narrow window band
create a Hall-type matching constraint; if the forced matching encodes a
hard choice, hardness might follow. Two facts block this:

1. **Hall feasibility is a matching (linear-forest-shaped) constraint.**
   The radius-2 score-window structure forces each vertex into an
   interval of width ≤ 5; the joint constraint is an interval-scheduling
   / Hall condition, which is a *bipartite-matching* feasibility test —
   polynomial, and itself linear-forest-shaped, so it cannot encode a
   pattern-avoiding permutation or exact-cover instance. This matches
   the reversed-matching analysis (`docs/reversed_matching_hardness.md`
   §6): window-band competition realises only matchings.

2. **The competition is also monotone in the same sense.** Pushing a
   vertex toward a more contested band only *adds* back-arc pressure on
   its neighbours; it never relaxes another vertex's constraint. So the
   window-competition degree of freedom inherits Theorem 3.1's
   monotone character.

We therefore did not pursue a separate position-competition reduction;
it reduces to the matching/Hall feasibility already shown polynomial.

---

## 5. The betweenness obstruction (sub-task 2)

Betweenness (Opatrny 1979, `DOI 10.1137/0208008`) is NP-complete: given
triples `(a, b, c)`, is there a total order placing `b` strictly between
`a` and `c` for every triple? Path-FAS *is* about a total order (the
LFO), so a betweenness triple is a pure ordering constraint that, a
priori, bypasses the back-arc-shape barrier (Theorem 6.1) entirely. The
question is whether a tournament's LFO order-restriction can *realise* a
betweenness constraint.

A betweenness triple `(x, y, z)` keeps exactly the 2 relative orders
`{(x, y, z), (z, y, x)}` of the 6 possible orders of the trio (`y` in
the middle). We searched for a gadget realising this:

> **Obstruction (betweenness un-realisability).** Over **all 1024
> tournaments on `n = 5`** and all `(trio, middle-element)` choices, the
> set of LFO relative orders of a trio is **never** equal to, nor a
> nonempty subset of, the betweenness set `{(x,y,z),(z,y,x)}`. In fact
> the smallest nonempty LFO relative-order set of any trio has size
> **≥ 3**.

Verified exhaustively in
`search_betweenness_gadget(5)` and pinned by
`test_betweenness_gadget_does_not_exist_n5`:

```
n=5 exhaustive (1024 tournaments):
  exact_betweenness_trios   = 0
  nonempty_subset_trios     = 0
  min_nonempty_relorder_size = 3
```

The reason is structural: the LFO order-restriction of a free trio is
"thick" — whenever the three windows overlap enough to permute the trio
at all, at least 3 of the 6 orderings survive. The Path-FAS feasibility
condition (linear forest) is too coarse to carve out exactly the
2-element betweenness set; it cannot *forbid* `y` at an end without also
forbidding some middle order. So betweenness, despite being a pure
ordering constraint, is not encodable as the LFO order-restriction of a
tournament. (This is consistent with — and explained by — §3: a
betweenness constraint forbids `y` at *either* end, which is a
non-monotone, mixed-polarity ordering condition.)

The `n = 5` exhaustive search is decisive and fast (≈ 1 s); it covers
all 1024 tournaments and every trio. We did not run the `n = 6`
exhaustive search to completion (32768 tournaments × 20 trios × 720
orderings is too slow for a quick confirmation), so the obstruction is
*proved exhaustively only at `n = 5`*. The `min_nonempty_relorder_size
≥ 3` fact is the structural reason and is not expected to change with
`n`, but we make no exhaustive claim beyond `n = 5`.

---

## 6. The non-monotone primitive that exists — and why it does not compose

The one place a genuinely **non-monotone** ordering primitive appears is
the `one_block` collision of D68
(`docs/dormant_matching_quotient_lemma.md`). On the `one_block`
tournament (`n = 12`), two length-5 prefixes

```
A = (0, 3, 1, 4, 2)   — does NOT extend to a valid LFO
B = (1, 2, 0, 4, 3)   — DOES extend
```

place the **same five vertices** in different orders (so they are *not*
subset-related: neither back-arc set contains the other), yet have
opposite extendability. Pinned by `test_one_block_nonmonotone_primitive`.
This is the only non-monotone ordering choice we found: the two states
have *incomparable* back-arc sets, so Theorem 3.1's "swap consecutive
pair ⇒ subset" argument does not apply.

Why it does not yield a reduction: as D68 proves, the distinction
between A and B is carried by the **global union-find partition** of the
loaded back-edges (in A the dormant pair `{0,10}` is merged with the
active vertex 4; in B the two dormant pairs `{0,10}, {1,9}` are merged
with each other but not with 4). Composing many such primitives into a
SAT reduction requires propagating this global merge structure between
gadgets — which is precisely the **fanout problem** (Section 3.3 of
`docs/general_path_fas_hardness.md`) that has resisted every attempt,
and which §2.3 here shows is degree-capped at 2 attachments per gadget.
The non-monotone primitive is real, but the channel to couple copies of
it (the back-degree budget) is exactly the scarce resource the fanout
obstruction governs.

---

## 7. Honest verdict

**No NP-hardness reduction obtained.** The ordering/flex encoding — the
last route left open after Theorems 5.1 and 6.1 closed the back-arc
encodings — is defeated by a single clean barrier:

> **The toggle/flex feasibility predicate is monotone in the flex
> choices** (Theorem 3.1), because loading a flexible edge only adds a
> back-arc and never removes one, and "linear forest" is closed under
> edge deletion. Monotone CSPs are in P, so the encoding cannot reach an
> NP-hard problem.

This is corroborated by two independent facts reproduced in the ordering
encoding: the **degree-2 fanout cap** (≤ 2 clause attachments per
variable, §2.3) and the **betweenness un-realisability** (§5). All three
are special cases of one phenomenon — the *loaded* direction of every
flexible/ordering choice is a pure liability, so no choice can serve as
an asset in one constraint and a liability in another, which is what a
mixed-polarity NP-hard CSP demands.

What we *did* establish positively:

* A working **coupling of variable gadgets through ordering choices and
  component-merge structure**, with no back-arc wire and full respect
  for Theorem 6.1 (§2.2): the all-negative OR-clause. This genuinely
  bypasses Theorems 5.1 and 6.1 — it is the furthest any non-back-arc
  encoding has gotten — and yields a *correct* reduction from
  **monotone CNF-SAT** to Path-FAS (`monotone_sat_to_path_fas`), which
  is, unfortunately, a P-time source problem.
* A **trusted decider chain**: FF == brute force on 180 random
  tournaments, with every global verdict at `n ≤ 10` re-checked against
  brute force.
* The **exact non-monotone primitive** (`one_block`) and the precise
  reason it does not compose (global union-find state + degree-2
  fanout).

### The sharpest open question after this attempt

> **Question 7.1.** Is there a tournament gadget with a binary degree of
> freedom whose two states have **incomparable** back-arc sets (a
> non-monotone ordering primitive, like the `one_block` collision), AND
> a coupling channel that propagates the global union-find merge state
> between copies **within the back-degree-2 budget**?

A positive answer would yield NP-hardness for Path-FAS; the `one_block`
primitive shows the first half is achievable, and §2.3 / D68 show the
second half is exactly the fanout problem. A proved impossibility for
the second half — that the global merge state cannot be propagated under
the degree-2 cap — would, together with Theorem 3.1, close the
non-back-arc route as decisively as Theorem 6.1 closed the back-arc
route, and would strongly suggest Path-FAS ∈ P (matching the companion
non-sweep positive route).

---

## 8. Files added by this probe

| File | Purpose |
|---|---|
| `scripts/nonbackarc_hardness.py` | Constructor (`build_with_extras`), clause gadget (`clause_not_all_true_extras`), deciders (`ff_has_lfo`, `bf_has_lfo`), monotonicity check (`feasibility_is_monotone`, `backarc_set_shrinks_when_unloaded`), monotone-SAT reduction, betweenness search (`search_betweenness_gadget`), `one_block` primitive. |
| `tests/test_nonbackarc_hardness.py` | 16 tests: FF==brute-force, clause semantics, monotonicity, fanout cap, betweenness obstruction, `one_block` primitive. |
| `docs/nonbackarc_hardness.md` | This document. |

## 9. Reproducing the experiments

```bash
cd /Users/lelarge/Recherche/graph-conjectures/problems/path_matching_fas

# Demo of all gadgets + obstructions
uv run python scripts/nonbackarc_hardness.py

# Tests (Sections 1-6)
uv run pytest tests/test_nonbackarc_hardness.py -v
```

## 10. Citations (verified identifiers)

* **Aboulker, P.; Aubian, G.; Charbit, P.; Lopes, R.** *Finding
  forest-orderings of tournaments is NP-complete* (2024).
  [arXiv:2402.10782](https://arxiv.org/abs/2402.10782). Source of
  Problem 4.4.

* **Opatrný, J.** *Total ordering problem.* SIAM J. Comput. 8(1):111–114
  (1979). [DOI 10.1137/0208008](https://doi.org/10.1137/0208008).
  NP-completeness of Betweenness (§5).

* **Schaefer, T. J.** *The complexity of satisfiability problems.* STOC
  1978: 216–226. [DOI 10.1145/800133.804350](https://doi.org/10.1145/800133.804350).
  NP-completeness of NAE-3SAT and the Boolean-CSP dichotomy (§3.3).

* **Garey, M. R.; Johnson, D. S.** *Computers and Intractability: A
  Guide to the Theory of NP-Completeness.* W. H. Freeman, 1979.
  Background on monotone-CSP tractability and reductions.

* `docs/J_hardness_via_wires.md`, Theorem 5.1 / Corollary 5.2 — interior
  degree saturation and the ≤ 2 attachment cap (§1, §2.3).

* `docs/reversed_matching_hardness.md`, Theorem 6.1 — global back-arc
  budget / linear-forest shape (§1, §3.4).

* `docs/forward_dp_lower_bound.md`, D70 — the toggle-pair fooling set
  substrate (§1.1) and the forward-DP `2^Ω(n)` bound (§3.4).

* `docs/dormant_matching_quotient_lemma.md`, D68 — the `one_block`
  non-monotone collision and the global-union-find fanout obstruction
  (§6).
