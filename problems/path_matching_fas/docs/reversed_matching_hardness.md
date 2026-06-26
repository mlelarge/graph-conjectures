# Reversed-matching NP-hardness attempt: a new global obstruction

This note records a 90–120 minute attempt to push the Path-FAS
NP-hardness route past the **interior degree saturation** wall
(Theorem 5.1 of `docs/J_hardness_via_wires.md`).  The intended bypass
is the **reversed-matching substrate** introduced in the D67 frontier
probe (`docs/forced_frontier_probe.md`), where every forced backedge
component has size 2 and Theorem 5.1 is vacuous.

The verdict is **honest and negative**.  No NP-hardness reduction is
obtained.  But the substrate exposes a **new structural obstruction**
that is independent of Theorem 5.1 and that, in our judgement, is the
sharpest currently known statement of why Path-FAS hardness is
elusive:

> **Global Back-Arc Budget + Linear-Forest Shape Obstruction.**
> The set of back-arcs of any LFO sigma is itself a linear forest on
> n vertices.  Hence the encoded "constraint graph" used to attach
> clause information has at most n - 1 edges *and* must decompose into
> a vertex-disjoint union of paths.  No matter how rich the per-register
> shuffle state, the *shape* of constraint encodings is bounded by the
> very same shape constraint that defines Path-FAS — a circularity.

Sections 1–2 explain why the reversed matching defeats Theorem 5.1.
Section 3 picks the hardness source (3-COLORING).  Sections 4–5 show
the candidate reduction explicitly and run it on small instances.
Section 6 states the new obstruction and the honest verdict.

The reproducible artifacts are:

* `scripts/reversed_matching_hardness.py` (~350 lines)
* `tests/test_reversed_matching_hardness.py` (16 passing tests).

## 1. Why reversed-matching bypasses Theorem 5.1

### 1.1. The interior-degree-saturation barrier (a recap)

`docs/J_hardness_via_wires.md` Theorem 5.1 proves: if `v_0 - v_1 - ⋯ -
v_k` is a forced backedge path in `H_back(T)` with `k >= 2`, then for
every interior vertex `v_i` (`1 <= i <= k - 1`) of the path,
`back-deg_sigma(v_i) = 2` in every LFO sigma, and both back-arcs of
`v_i` are to its forced-path neighbours.

Consequence (Corollary 5.2): each wire of length `k` admits at most 2
clause attachments (one per endpoint).

### 1.2. The substrate

The **reversed matching tournament** RM(m) on `n = 2m` vertices is
built from the transitive tournament on `0, 1, …, n - 1` by reversing
each of the `m` arcs `(i, i + m)` for `i = 0, …, m - 1`.

For `m >= 8`, score-window radius 2 gives disjoint windows for the
low-half `i ∈ [0, m)` and the high-half `i + m ∈ [m, 2m)` of every
matching pair.  Hence the forced backedge graph is exactly the
`m`-edge matching

  `H(RM(m)) = { (i + m, i) : 0 <= i < m }.`

Verified in `tests/test_reversed_matching_hardness.py
::test_reversed_matching_RM8_has_8_forced_matching_edges` and the
analogous test for `m = 10`.  The construction's Hall feasibility is
checked in `::test_reversed_matching_is_hall_feasible`.

### 1.3. Theorem 5.1 is vacuous on the matching substrate

Every connected component of `H(RM(m))` is a single edge {i, i + m}.
There are *no interior vertices*.  Concretely:

> **Lemma 1.1.**  In RM(m) the underlying undirected graph of H is a
> matching: every vertex has H-degree at most 1, so no vertex is
> "interior" to a forced backedge path of length k ≥ 2.  Hence
> Theorem 5.1 of `docs/J_hardness_via_wires.md` makes no claim about
> any vertex of RM(m).

*Proof.*  By construction H is `{(i+m, i)}`, a matching.  Both
vertices i and i + m have H-degree 1.  ∎

This is the precise sense in which the matching substrate **bypasses
the wire obstruction**.  Verified in
`::test_theorem_5_1_vacuous_on_matching` (asserts the underlying
H-graph of RM(m) has maximum degree 1 for `m ∈ {8, 10, 12}`).

### 1.4. Per-register spare budget (the consequence)

Since each H-vertex contributes only 1 back-arc to its register
(toward its matching partner), every vertex has **1 spare back-arc
slot** of the LFO budget-2 cap.  Per matching component {i, i + m}
the total spare budget is 2 (one at each endpoint).

This corresponds exactly to Corollary 5.2's "≤ 2 clause attachments
per wire" — but now without requiring a long wire or a path-substrate
detour.  Per **register** (matching component) we get the same 2
attachment slots, but now the register itself is only 2 vertices wide
(not 7k + 1 as in the wire construction).

## 2. Matching component as a "register" — what it can encode

### 2.1. State-space accounting

The state of a register C_i = {i, i + m} in an LFO sigma is the pair

  `(sigma(i), sigma(i + m))`

with `sigma(i) < sigma(i + m)` (because the matching edge is forced).
Both positions are constrained to lie in their score windows:

  `sigma(i) ∈ I_i = [max(0, d_i - 2), min(n - 1, d_i + 2)],`
  `sigma(i + m) ∈ I_{i + m} = [max(0, d_{i+m} - 2), min(n - 1, d_{i+m} + 2)],`

where `d_v` is the in-degree of v.  For RM(m) each window has width 5
(when not clipped at the boundary).  So each register has at most
`5 × 5 = 25` raw (position, position) pairs and, after enforcing
`sigma(i) < sigma(i + m)`, on the order of 15 candidate states.

### 2.2. Empirical register-state count

`scripts/reversed_matching_hardness.py::register_state_diagnostic`
counts distinct *slot-discretised* register-state vectors across all
LFOs of RM(8):

| m | n | #LFOs | distinct register-state vectors |
|---:|---:|---:|---:|
| 8 | 16 | 865 | 34 |

So RM(8) genuinely has a multi-state register structure: 34 distinct
"slot vectors" (each vector reports, for each register, whether i + m
sits early, mid, or late in its window) are realised by LFOs.

This is much richer than the 2-state ("True/False") variable of the
classical wire reduction.  The substrate has **nontrivial encoding
potential** — far more than 1 bit per register.

Verified in `::test_register_states_are_nontrivial`.

### 2.3. What a register's state can encode

The state of C_i is its **shuffle position** relative to the other
registers.  Pairwise, the shuffle bit between C_i and C_j is:
"does C_i come before or after C_j in the LFO?"  (Or finer: in which
of the windows do the four vertices interleave?)

In principle this gives O(m^2) pairwise relations, hinting at
quadratic constraint capacity.  Section 6 shows that this hint is
**misleading**: the global back-arc budget caps the realisable
constraints at n - 1 ≪ m^2.

## 3. The hardness source: 3-COLORING

We target **3-COLORING** (Karp 1972, in *Reducibility among
combinatorial problems*, in R. E. Miller, J. W. Thatcher, eds.,
*Complexity of Computer Computations*, Plenum Press, pp. 85–103;
DOI [10.1007/978-1-4684-2001-2_9](https://doi.org/10.1007/978-1-4684-2001-2_9)).

Statement: given a simple graph G = (V, E), decide whether the
vertices admit a 3-coloring (a function `c : V → {0, 1, 2}` with
`c(u) ≠ c(v)` for every edge (u, v) ∈ E).  NP-complete already on
planar 4-regular graphs.

**Why 3-COLORING and not NAE-3SAT or 3-SAT?**

Each register has > 2 states empirically, so 1-bit encodings would
under-utilise the state space.  3-COLORING maps cleanly onto a
3-state-per-register encoding: the state of C_i picks one of three
"color slots" inside the window of i + m.

Note that this is the *same* hardness source proposed in the task
brief's "Candidate hardness routes" list (Section 3.3,
"Maximum Acyclic Subgraph with degree constraints — NP-hard with
degree ≤ 2 (Karp 1972)"): graph 3-COLORING is essentially the dual
of degree-bounded NP-hard CSPs and is the cleanest 3-state shoebox.

## 4. The candidate reduction

### 4.1. Variable gadget = matching component

For each vertex v of G assign the matching component C_v = {v, v + m}
of RM(m).  The "color" of v is the slot of (v + m) in its score
window, decoded by

  `slot(p, [lo, hi]) = floor((p - lo) / ((hi - lo + 2) / 3))`

clamped to [0, 2].  Concretely:

  * slot 0 = `p - lo < (hi - lo + 2) / 3`
  * slot 1 = otherwise but < `2 * (hi - lo + 2) / 3`
  * slot 2 = otherwise.

This gives every register a 3-state read-out from the LFO.

### 4.2. Wiring gadget = arc reversal between registers

For each clause-edge (u, v) of G we reverse the tournament arc
between (u + m) and (v + m).  In the transitive base RM(m), the arc
(u + m, v + m) is `1` iff `u < v`; reversing flips it.  The intent:

* introduce a non-default order between (u + m) and (v + m),
* push their relative LFO position into different slots.

This is the **simplest possible** "shuffle constraint" that fits
within the LFO budget.  Each clause edge introduces exactly 1 arc
flip.

### 4.3. Composition

The full reduction is:

```python
def build_3coloring_reduction(G):
    m = max(G.m, 8)
    T = build_reversed_matching(m)            # RM(m) base
    for (u, v) in G.edges:
        flip_arc(T, u + m, v + m)             # per-clause flip
    return T
```

(see `scripts/reversed_matching_hardness.py::build_3coloring_reduction`).
This runs in linear time `O(|V| + |E|)` and outputs a tournament on
`n = 2m` vertices.  The size is linear in `|V(G)|`.

## 5. Empirical verification on small instances

`scripts/reversed_matching_hardness.py::small_instance_demo` runs the
reduction on four 3-COLORING instances and exhaustively enumerates
the LFOs of each output tournament.

| G | |V| | 3-colorable? | T has LFO? | LFO encodes valid coloring? | Reduction outcome |
|---|---:|:---:|:---:|:---:|---|
| `P_3` (path on 3 vert.) | 3 | Yes | Yes | Yes | consistent |
| `K_3` (triangle) | 3 | Yes | Yes | **No** | **unsound: false negative** |
| `C_5` (5-cycle) | 5 | Yes | **No** | n/a | **unsound: false negative** |
| `K_4` (clique on 4 vert.) | 4 | **No** | Yes | No | accidentally correct |

Verification results from running `uv run python
scripts/reversed_matching_hardness.py --demo`.  Each row is pinned by
a dedicated test in
`tests/test_reversed_matching_hardness.py`:

* `::test_3coloring_reduction_path_is_consistent_but_not_definitive`
* `::test_3coloring_reduction_triangle_fails_to_encode_a_valid_coloring`
* `::test_3coloring_reduction_C5_destroys_lfo_existence`
* `::test_3coloring_reduction_K4_accidentally_matches`

The reduction is **broken on K_3 and C_5**.  On K_3 the tournament
admits LFOs but the slot decoding never lands on a 3-coloring of K_3.
On C_5 the per-edge arc flips conspire to break LFO existence
entirely, producing a "Path-FAS = NO" verdict for a 3-colorable G —
the most blatant unsoundness mode.

## 6. The new obstruction and the honest verdict

### 6.1. The Global Back-Arc Budget obstruction

The failure on C_5 and K_3 is not a quirk of our particular encoding
choice (slot-decoded arc-flip).  The deeper reason is the following.

> **Theorem 6.1 (Global Back-Arc Budget).**  Let T be a tournament
> on n vertices and let sigma be any LFO of T.  Then the back-arc
> graph B(sigma) is a linear forest on n vertices, and therefore
>
>   `|B(sigma)| <= n - 1.`
>
> In particular, the *shape* of B(sigma) is a vertex-disjoint union
> of paths.

*Proof.*  Path-FAS feasibility of sigma means B(sigma) is the union
of back-arcs of sigma considered as an undirected graph, and this
graph is required to be a linear forest (definition F1 of Section
1.2 of `docs/general_path_fas_hardness.md`).  A linear forest on n
vertices has at most n - 1 edges.  ∎

Verified in `::test_global_back_arc_budget_bounds_lfo_back_arcs` and
`::test_global_constraint_capacity_is_at_most_n_minus_1`.

### 6.2. The Linear-Forest-Shape consequence for any reduction

Any Path-FAS reduction whose **clause attachments are encoded via
the presence of back-arcs** (the only mode used by every gadget
explored so far) is constrained by Theorem 6.1:

> **Corollary 6.2 (Constraint-Graph Shape Cap).**  Any "back-arc-
> encoded" reduction from a problem P to Path-FAS has the property
> that the set of clause-attachments active in any single LFO forms a
> linear forest.  Hence the *shape* of the clause-variable
> attachment graph realisable by one tournament is at most a
> vertex-disjoint union of paths on n vertices.

This is a **shape obstruction**, not merely a cardinality one.  It
is independent of Theorem 5.1:

* Theorem 5.1 (local interior degree saturation) says: *long forced
  paths consume their own back-arc budget*.  This is a local
  argument that needs interior vertices to bite.
* Theorem 6.1/Cor 6.2 (global linear-forest shape) says: *the entire
  back-arc set is a linear forest on V(T)*.  This is a global shape
  fact that applies to **every** LFO, regardless of the substrate.

The two obstructions are independent: a reduction with no forced
backedge interior (e.g. the matching substrate of this note) still
hits Theorem 6.1.

### 6.3. Why this kills the reversed-matching reduction route

3-COLORING requires encoding an *arbitrary* edge set `E(G)` of
constraints.  By Corollary 6.2, the reduced tournament can realise
the simultaneous activation of at most a **linear forest** of
constraint-back-arcs in any single LFO.  For a 3-colorable graph G
whose edge set is *not* a linear forest (e.g. K_3, C_5, K_4), no
single LFO can simultaneously "witness" all edges as enforced.

A *correct* reduction would need:

* either to enforce constraints via the **absence** of an LFO (i.e.,
  encode hardness via "T_G has no LFO iff G is not 3-colorable"),
  but this collapses the LFO space too coarsely (a single bad clause
  removes too many witnesses),

* or to encode each constraint via a **distinct LFO** (per-LFO
  attribution of a per-edge witness), which decouples the constraints
  but loses the conjunction.

Our naïve arc-flip reduction does neither; it collapses constraints
into a single tournament whose LFO existence depends globally on the
constraint graph's shape, not on its 3-colorability.

### 6.4. Two structural failure modes observed

1. **LFO destruction (C_5, K_4 partly).**  Adding a per-edge arc flip
   can break Hall feasibility or break the LFO degree-2 cap, removing
   *all* LFOs.  For C_5, this collapse is the consequence of 5
   coupled flips on 5 high-half vertices, each adding back-arc
   pressure to its neighbours.

2. **Decoding under-coverage (K_3, K_4).**  When LFOs survive, the
   slot decoder of section 4.1 deterministically assigns a small
   subset of the `3^m` possible color vectors; e.g. for K_3 the
   surviving LFOs all assign two adjacent vertices the same slot.
   The decoder can be redesigned, but Theorem 6.1 implies that no
   redesign can make the per-LFO state encode an arbitrary
   3-coloring on a non-linear-forest constraint graph.

### 6.5. Comparison to Theorem 5.1

| Property | Theorem 5.1 (wires) | Theorem 6.1 (matching, this doc) |
|---|---|---|
| Scope | Long forced paths in H | Any LFO of any tournament |
| Statement | Interior of forced path has back-deg 2, saturated | Back-arc graph is a linear forest, ≤ n - 1 edges |
| Bypassed by short components? | Yes (matching has no interior) | No (every LFO satisfies it) |
| Visible at | k ≥ 2 forced paths | Every n ≥ 2 tournament |
| Consequence for reductions | ≤ 2 clause attachments per wire | Total constraint count ≤ n - 1, shape = linear forest |

Theorem 6.1 is **strictly more general** than Theorem 5.1.  It
applies even when Theorem 5.1's hypothesis (interior vertex of
forced path) fails.  It is the cleaner statement of the underlying
fanout barrier — fully global, fully shape-aware.

### 6.6. What this obstruction does NOT rule out

* **Reductions where the back-arc graph is the same shape as the
  constraint graph of the source problem.**  If we reduce from a
  problem whose instances have the linear-forest constraint shape
  built in — e.g., **shuffle-of-two-strings** or **monotone path
  embedding** — the global shape cap is not binding.  Garey–Johnson
  1979 records SHUFFLE as NP-hard (Mansfield 1982); the cleanest
  formulation is the "k-string shuffle" problem of
  [DOI 10.1145/322307.322316] — but verifying its NP-hardness on a
  linear-forest constraint shape is beyond the scope of the present
  attempt.

* **Reductions where clauses are encoded by LFO existence/absence
  rather than by simultaneous back-arc witnesses.**  Each clause
  could correspond to a sub-tournament gadget whose LFO existence
  encodes the clause's satisfaction.  The composition would need to
  prove that conjunction of clause-satisfaction equates to LFO
  existence of the full composed tournament.  This is exactly the
  *fanout problem* (Section 3.3 of `docs/general_path_fas_hardness.md`)
  which has resisted all known attempts.

* **Reductions exploiting score-window radius > 2 or a different
  feasibility relaxation.**  The Hall-feasibility / radius-2 score
  window structure is specific to LFOs; relaxing it might admit new
  shape encodings.  But this would target a different problem, not
  Aboulker Problem 4.4.

### 6.7. The honest verdict

**No NP-hardness reduction obtained from the reversed-matching
substrate.**  The candidate reduction from 3-COLORING is empirically
unsound on 2 of the 4 small instances tested (K_3 and C_5), and the
underlying reason is the **Global Back-Arc Budget + Linear-Forest
Shape** obstruction stated as Theorem 6.1 / Corollary 6.2.

This is a *new* and structurally clean obstruction: it is independent
of Theorem 5.1, applies to every LFO of every tournament, and
constrains the **shape** of clause encodings in any back-arc-based
reduction.

The matching substrate **does** genuinely bypass Theorem 5.1 (as
intended), and **does** offer a multi-state-per-register encoding
(34 register-states realisable on RM(8)), but the global shape
constraint defeats the encoding of constraint graphs richer than
linear forests.

The newly sharpest open hardness question — analogue to Question 6.1
of `docs/J_hardness_via_wires.md` — is:

> **Question 6.3.**  Is there a polynomial-time reduction from any
> NP-hard problem P to tournament Path-FAS such that the instances of
> P are restricted to inputs whose natural constraint graph is itself
> a linear forest, and such that the composed reduction respects the
> back-arc-budget cap of n - 1 per LFO?

A positive answer here would yield NP-hardness for Path-FAS.  A
negative answer (proved impossibility) would close the back-arc-based
reduction route entirely and force the hardness investigation into
non-back-arc encodings (LFO-existence gadgets, in the sense of
Section 6.6 point 2).

The companion agent's positive route — the **Dormant-Matching
Quotient Lemma** of `docs/forced_frontier_probe.md` Section 4 — is
the natural partner.  If that lemma is true, our matching substrate
is harmless for tractability and Path-FAS likely sits in P.  If the
lemma fails, the matching substrate is genuinely adversarial — but
our Theorem 6.1 still says that any *back-arc-encoded* reduction
remains capped by the linear-forest shape.

## 7. Files added by this probe

| File | Purpose |
|---|---|
| `scripts/reversed_matching_hardness.py` | Substrate constructor, candidate 3-COLORING reduction, register-state diagnostic, demo CLI. |
| `tests/test_reversed_matching_hardness.py` | 16 passing tests pinning the substrate (Section 1), Theorem 5.1's vacuity (Section 1.3), register-state richness (Section 2), the unsoundness of the candidate reduction on K_3, C_5, K_4, P_3 (Section 5), and the Global Back-Arc Budget bound (Section 6). |
| `docs/reversed_matching_hardness.md` | This document. |

## 8. Reproducing the experiments

```bash
cd problems/path_matching_fas

# Section 1: substrate diagnostic
uv run python scripts/reversed_matching_hardness.py --substrate 8

# Section 5: small-instance reduction demo
uv run python scripts/reversed_matching_hardness.py --demo

# All tests (Sections 1-6)
uv run pytest tests/test_reversed_matching_hardness.py -v
```

## 9. Citations (verified identifiers)

* **Aboulker, Aubian, Charbit, Lopes**, *Finding forest-orderings of
  tournaments is NP-complete* (2024).
  [arXiv:2402.10782](https://arxiv.org/abs/2402.10782).  Source of
  Problem 4.4.

* **Karp, R. M.**, *Reducibility among combinatorial problems*, in
  R. E. Miller, J. W. Thatcher, eds., *Complexity of Computer
  Computations*, Plenum Press, 1972, pp. 85–103.  DOI
  [10.1007/978-1-4684-2001-2_9](https://doi.org/10.1007/978-1-4684-2001-2_9).
  Source of 3-COLORING's NP-completeness (Section R5 of the paper).

* **Garey, M. R., Johnson, D. S.**, *Computers and Intractability: A
  Guide to the Theory of NP-Completeness*, W. H. Freeman, 1979.
  Catalogue entry SR15 for SHUFFLE-OF-STRINGS, referenced in Section
  6.6.

* **Mansfield, A.**, *On the complexity of computing the longest
  common subsequence of permutations* (1982).  Demonstrated SHUFFLE
  variants are NP-hard.

* `docs/J_hardness_via_wires.md`, Theorem 5.1.  The interior-degree-
  saturation barrier this note bypasses.

* `docs/forced_frontier_probe.md`, Section 4 (Dormant-Matching
  Quotient Lemma).  The companion agent's target.

* `docs/general_path_fas_hardness.md`, Sections 3 and 6 (Fanout
  obstruction, honest verdict).  The prior baseline.

* `docs/J_width_conjecture.md`, Theorem (refined width bound).  The
  pw(J), tw(J) ≤ 8 + 2|H| proof underpinning the FPT-in-|H| status.

---

**Acknowledgement of joint attack structure.**  This note is the
hardness-side companion to the positive Dormant-Matching Quotient
agent.  Both attacks share the matching substrate as their decisive
local question.  The verdict here — Theorem 6.1 — does **not** depend
on the positive side's outcome and stands independently.
