# J-hardness via forced-forest wires: an honest obstruction

This note records a 75–120 minute attempt to obtain an NP-hardness
reduction for general-tournament Path-FAS
([Aboulker–Aubian–Lopes Problem 4.4](https://arxiv.org/abs/2402.10782))
that **avoids the local-fanout obstruction** documented in
`docs/general_path_fas_hardness.md` Section 3.3.

The intended route was: use long forced paths in the score-window
**forced-forest graph** `H` as global value-transmitters, and encode
clause constraints in the **flexible** interval edges.  This sidesteps
the back-degree-2 budget at any single broadcast vertex by spreading
the broadcast over a fixed substrate.

**Verdict.**  The wire architecture **fails**, but the obstruction it
fails on is a *new* and structurally cleaner one than the local-fanout
obstruction.  We call it **interior degree saturation** (Theorem 5.1
below): any LFO of a tournament containing a forced path of length
`k` in `H_back` already saturates the back-degree-2 budget at every
interior path vertex, so no auxiliary vertex can attach a back-arc to
the interior of the wire.  This caps the number of clause attachments
per variable at 2 (one per endpoint), reducing the would-be reduction
to a "max-occurrence-2" SAT problem that is polynomial — hence no
NP-hardness is derived.

The contribution of this document is the precise statement and proof
of the new obstruction, plus pinned tests
(`tests/test_wire_reduction.py`, 8 passing tests) that nail the
behaviour at `k = 1, 2` against the brute-force decider.

## 1. Why fanout is the right place to attack

The local-fanout obstruction (cited from
`docs/general_path_fas_hardness.md`, Section 3.4) reads, in one line:

> A single tournament vertex `v` has back-degree ≤ 2 in any LFO; hence
> `v` cannot "broadcast" its truth value to ≥ 3 clause copies via
> incident back-arcs.

The natural way to bypass this is to *distribute the broadcast over a
path*.  If the path is **forced** — i.e. its edges are present as
back-arcs in every LFO — then every clause attached to a different
path vertex receives the "value" through the path's intrinsic LFO
order, not via a single high-degree vertex.

Concretely, the score-window theorem (`docs/score_window.md`) implies
that vertex `u` and vertex `v` have a forced relative LFO position
whenever their score windows are disjoint, i.e.
`|d⁻(u) − d⁻(v)| ≥ 2r + 1 = 5`.  A *forced-back-arc-path* is a
sequence `v_0 - v_1 - v_2 - ⋯ - v_k` of tournament vertices such that
the in-degree gaps satisfy `|d⁻(v_i) − d⁻(v_{i+1})| ≥ 5` for every
`0 ≤ i < k` and the actual tournament arc between consecutive `v_i`
points from the later to the earlier (so it is a back-arc in every
LFO).  In any LFO `σ`, the path

    σ(v_0), σ(v_1), σ(v_2), ..., σ(v_k)

is **monotone** (either strictly increasing or strictly decreasing) by
the score-window inequalities.

The hope was: in such a setting, broadcasting is "free" because the
relative order of the path vertices is fixed by `H` regardless of the
truth assignment.

This hope is correct *for the relative order on the path*.  It is
wrong about what else can happen at the path vertices, which is the
content of Section 5.

## 2. Forced-path families: construction and empirical record

### 2.1.  Explicit constructor

`scripts/variable_wire_gadget.py::build_forced_path_tournament(k)`
builds a tournament `T` on `n = 7k + 1` vertices containing a
*designated* forced-back-arc path of length `k`.

The construction:

1. Start from the transitive tournament on positions `0, 1, …, n − 1`.
2. Reserve path positions `0, 7, 14, …, 7k` for path vertices.  The
   in-degrees in the transitive backbone are exactly the positions, so
   path vertex `i` has `d⁻(v_i) = 7i`.
3. Reverse the `k` arcs `(v_i, v_{i+1})` for `i = 0, …, k − 1` so that
   they become back-arcs.  After reversal:
   * `d⁻(v_0) = 0 + 1 = 1`
   * `d⁻(v_i) = 7i + 1 − 1 = 7i` for `1 ≤ i ≤ k − 1`
   * `d⁻(v_k) = 7k − 1`
   * Consecutive gaps: 5 (at the endpoints), 7 (interior).

The spacing 7 (rather than the score-window-radius-driven minimum of
5) is required because the reversal step shifts the endpoint
in-degrees by ±1, so a naive spacing-5 construction yields endpoint
gaps of only 4 and the score-window theorem does not force the
endpoint edges.  With spacing 7 every gap is at least 5 and the entire
path edge set lies in `H_back`.

Verified in `tests/test_wire_reduction.py`:

* `test_forced_path_k1_construction`: `n = 8`, gap 5, one forced
  backedge.
* `test_forced_path_k2_construction`: `n = 15`, gaps `(6, 6)`, two
  forced backedges.

### 2.2.  Empirical sweep across families

`scripts/forced_path_tournament.py --sweep` measures the longest
forced-back-arc path across three tournament distributions for
`n ∈ {8, 10, 12, 14, 16, 20}`:

| family | n=12 | n=14 | n=16 | n=20 |
|---|---|---|---|---|
| uniform random | 3 | 4 | 6 | 10 |
| skew (transitive + 5% noise) | 3 | 4 | 5 | 7 |
| skew (transitive + 10% noise) | 3 | 5 | 6 | 10 |
| stretched in-degree (engineered) | 0 | 0 | 0 | 0 |

(Data: `data/forced_path_sweep_20260527.json`; trials per cell ≥ 500
in the table cells above.)

Two takeaways:

1. **Forced paths up to length 10 are achievable at n = 20** with
   uniform random tournaments.  The score-span bound
   `k ≤ 2·⌊(n − 1)/5⌋` is not tight; zigzag in-degree sequences allow
   longer paths.
2. **Explicit engineered tournaments** (the `build_forced_path_tournament`
   constructor) realise paths of any length `k` on `n = 7k + 1`
   vertices in polynomial time.  This *would* be enough substrate for
   a reduction if the path actually transmitted information; Section 5
   shows that it does not.

### 2.3.  Cross-check against existing structural-reduction data

The structural reduction agent's probe at `n = 24` (skew family, 100
samples per noise level; `data/score_window_skew_probe_n24_seed20260522.json`)
reports forced-backedge counts up to 22 at `p = 0.2`.  None of those
samples were filtered to ensure the forced graph is a path (it can be
a more complex linear forest or a non-tree).  Our explicit
constructor confirms that a path-shape forced backbone of arbitrary
length is realisable.

## 3. Variable wire gadget

### 3.1.  Definition

A **variable wire** for variable `v_j` of a SAT formula `Φ` is the
sub-tournament returned by `build_forced_path_tournament(k_j)`, where
`k_j` is the number of times `v_j` occurs in `Φ`.  The "value" of `v_j`
is intended to be encoded by an *external* vertex (`L_j`, "literal")
whose flexible interval edge to a designated reference vertex is a
back-arc iff `v_j = True`.

### 3.2.  Truth table at k = 1

`tests/test_wire_reduction.py::test_truth_table_k1_path_direction_unique`
brute-forces all 8! = 40 320 orderings of the `n = 8` wire tournament
and finds 177 LFOs, **every one** of which orders the path `0 → 1`
(i.e. `v_0` before `v_1`).  No LFO orders the path in reverse.  This
confirms the path direction is fully determined by the structure of
`H`.

### 3.3.  Path direction does not carry information

Critically: since the path direction is *fixed* in every LFO (it is a
property of `H`, not of the LFO), the path itself encodes no truth
value.  Any "variable value" must be carried by a separate degree of
freedom — typically an auxiliary vertex `L_j` whose relative position
to the path varies between LFOs.

This is where the new obstruction (Section 5) lives.

## 4. Clause wire gadget

### 4.1.  Intended architecture

For each NAE-3SAT clause `C = (l_1, l_2, l_3)` we would attach three
"literal" vertices to three positions of the variables' wires.  A
literal `l_i = (v_j, polarity)` attaches to wire `P_j` at the
occurrence-index slot for that clause.

### 4.2.  Empirical attempt

`scripts/clause_wire_gadget.py --mode single_literal --k 2` attaches
a single extra vertex `L` to the interior of a `k = 2` wire (`n = 15`)
and checks whether the augmented tournament still has an LFO.  The
solver finds an LFO, but inspection of its back-arcs shows that the
extra vertex `L` contributes **zero** back-arcs incident to the
interior of the path: its window does not reach the interior in any
LFO that survives, and the path back-arcs `(v_1, v_0), (v_2, v_1)`
already saturate the interior vertex's degree budget.

The single-literal attachment "succeeds" in the trivial sense that an
LFO exists, but **the literal vertex transmits no information about
the path interior**.  This is the empirical face of the obstruction
proved in Section 5.

### 4.3.  Three-literal attachment is structurally infeasible

`scripts/clause_wire_gadget.py --mode three_literals` does not
construct a working clause gadget; the function explicitly reports
that for `k = 2` there is exactly one interior vertex (not enough for
3 attachments) and at higher `k` the same per-interior-vertex
obstruction (Theorem 5.1) blocks each attachment in turn.

## 5. The new obstruction: interior degree saturation

This is the core contribution of the present note.

### 5.1.  The theorem

**Theorem 5.1 (Interior degree saturation).**
Let `T` be a tournament and let

    v_0 - v_1 - v_2 - ⋯ - v_k    (k ≥ 2)

be a path in `H_back(T)` (each consecutive pair has score-window gap
≥ 5 and the tournament arc points from later-in-window to
earlier-in-window).  Let `σ` be any LFO of `T`.  Then for every
**interior** path vertex `v_i` (`1 ≤ i ≤ k − 1`),

    back-degσ(v_i) = 2,

and **both** back-arcs of `v_i` go to its forced-path neighbours
`v_{i−1}` and `v_{i+1}`.

In particular, no external vertex `w ∉ {v_{i−1}, v_{i+1}}` may
contribute a back-arc incident to `v_i` in `σ`.

*Proof.*  In the LFO `σ`, the score-window inequalities force
`σ(v_0) < σ(v_1) < ⋯ < σ(v_k)` (or the reverse; WLOG increasing).
The tournament arc between `v_{i−1}` and `v_i` points from `v_i` (the
larger-in-degree vertex) to `v_{i−1}` (the smaller-in-degree
vertex), by the construction of `H_back`.  But `σ(v_{i−1}) < σ(v_i)`,
so the arc `v_i → v_{i−1}` is a back-arc.  Symmetrically, the arc
between `v_i` and `v_{i+1}` is `v_{i+1} → v_i`, also a back-arc.

So `v_i` already has back-arcs to `v_{i−1}` (outgoing back-arc) and
from `v_{i+1}` (incoming back-arc), contributing 2 to its undirected
back-degree.  By the LFO max-degree-2 bound, this is the entire
budget. ∎

### 5.2.  Corollary: the wire reduction collapses

**Corollary 5.2.**  Under the wire architecture
(Section 3 + Section 4), each variable wire `P_j` admits *at most two*
clause attachments (one at each endpoint `v_0` and `v_{k_j}`).

*Proof.*  By Theorem 5.1, any back-arc external to the wire must land
on an endpoint `v_0` or `v_{k_j}`.  Each endpoint has spare back-arc
budget of at most 1 (since the path edge itself already contributes 1
of the 2-budget).  Hence each endpoint supports at most 1 attachment,
and the total per wire is at most 2. ∎

**Corollary 5.3.**  The wire architecture cannot encode SAT instances
with any variable occurring in ≥ 3 clauses.

But every standard NP-hard SAT variant has instances where some
variable occurs in arbitrarily many clauses (D2DP, NAE-3SAT, Exact
Cover by 3-Sets, 3-SAT, Hamiltonian path on cubic graphs, …).
Sparsification to bounded-occurrence variants (≤ 2 per variable)
yields polynomial instances: 2-SAT, monotone 2-CSP, etc.

### 5.3.  Why this is the same fanout obstruction, expressed differently

The local-fanout obstruction of
`docs/general_path_fas_hardness.md` § 3.4 says: *a single vertex has
back-degree ≤ 2*.  The interior-degree-saturation obstruction
(Theorem 5.1) says: *the forced path vertices already use both
back-arcs of the budget*.

These are the *same* underlying scarce resource — the back-degree-2
budget — re-expressed at the level of a path scaffold.  Spreading the
broadcast across many vertices of a forced path does not relax the
budget; it just moves the budget consumption onto the path itself.

The new obstruction is sharper in two senses:

1. **It is a global property of the forced substrate**, not a local
   per-broadcast-vertex fact.  In particular, it does not depend on
   the choice of "broadcast vertex" — every interior vertex of every
   forced path is equally constrained.

2. **It is constructively certified**: at every `k ≥ 2`, the
   constructor `build_forced_path_tournament(k)` produces an
   instance whose interior vertex's back-arc set is fully determined
   in every LFO (verified for `k = 1` brute-force at `n = 8`, and
   structurally for `k = 2` via `find_lfo_order_score_window` at
   `n = 15`).

### 5.4.  What the obstruction does NOT rule out

* It does not rule out reductions that use *non-forced* paths in `H`
  (i.e. relations forced by Hall feasibility but not by pairwise
  score-window disjointness).  The Hall-forced relations are strictly
  stronger than pairwise-forced; an unused freedom remains there.

* It does not rule out reductions that exploit the *forward*-forced
  arcs of `H` (the `forced_forward` set in
  `scripts/score_window_forced.py`).  Forward-forced arcs do not
  contribute back-degree, so they could conceivably carry information
  while leaving the back-arc budget free.  No working construction
  is known.

* It does not rule out reductions using a forced graph `H` that is a
  more complex tree or branching structure rather than a path; the
  fork-tree case (closed in `docs/exchange_proof_draft.md` Section 65)
  is the natural exemplar of branched forced structures, but it
  belongs to the *easy* (P-time) side, not the hard side.

## 6. Honest verdict

### 6.1.  Status

**No NP-hardness reduction obtained.**  The wire architecture, in the
form proposed by the task brief, fails to encode SAT instances where
variables occur in ≥ 3 clauses.

### 6.2.  What we DID achieve

1. **A polynomial-time constructor** of tournaments with explicit
   forced-back-arc paths of any length `k` on `n = 7k + 1` vertices
   (`scripts/variable_wire_gadget.py::build_forced_path_tournament`).
   This advances the empirical state-of-the-art on score-window
   forced paths from `k ≤ 4` random samples at `n = 12`
   (`docs/general_path_fas_reduction.md` Section 5) to *arbitrary* `k`
   by construction.

2. **A sharp structural theorem** (Theorem 5.1) showing that long
   forced paths in `H_back` cannot serve as wires: every interior
   vertex is fully degree-saturated.  This is a clean, succinct
   obstruction that complements (and clarifies) the local-fanout
   obstruction in `docs/general_path_fas_hardness.md` § 3.

3. **A pinned, reproducible certification** of the obstruction at
   `k = 1, 2` (`tests/test_wire_reduction.py`, 8 passing tests).

4. **Verification that bounded-occurrence (≤ 2) wire reductions are
   constructible at the architectural level**, but the corresponding
   SAT variant is polynomial (2-SAT is in P), so this does not yield
   NP-hardness.

### 6.3.  What we did NOT achieve

* **No reduction from D2DP** (Fortune–Hopcroft–Wyllie 1980,
  [DOI 10.1016/0304-3975(80)90009-2](https://doi.org/10.1016/0304-3975(80)90009-2)).
  D2DP would map two source-sink pairs to two forced paths in `H`,
  but the two paths would have to coexist in the same tournament
  without their interior vertices colliding (each interior vertex
  saturating its budget separately).  The forced-path constructor
  produces *one* path per tournament; two coexisting forced paths
  would each require their own zigzag in-degree sequence, and
  combining them in a single tournament restricts to a tournament
  whose in-degree sequence supports both — and which, by Theorem 5.1
  applied twice, has *no* interior vertex shared between the paths.
  We did not find a productive use of D2DP via this route.

* **No reduction from Hamiltonian path on cubic graphs** (Garey–
  Johnson–Tarjan 1976).  Cubic-graph Hamiltonicity has every vertex
  of degree 3, and the "vertex gadget" we would need is a degree-3
  branching structure inside `H`.  But `H` restricted to back-arc-
  forced edges is, when it is a path, *exactly* a degree-2 structure
  per Theorem 5.1.  We have no way to embed cubic-vertex gadgets in a
  forced-back-arc graph.

* **No reduction from NAE-3-SAT with degree-2 propagation**.  As
  Section 5.2 shows, even degree-2 occurrences trigger the obstruction
  at the wire-endpoint level (each endpoint supports at most 1
  attachment, two endpoints per wire → at most 2 total, which equals
  the degree-2 bound exactly).  But NAE-3-SAT restricted to
  occurrences ≤ 2 is polynomial (every clause-variable graph is a
  pseudo-forest, decidable directly).

* **No reduction from X3C with degree-bounded variants**.  The
  obstruction transfers: every triple's third occurrence of an
  element would land in an interior vertex of a wire and trigger
  Theorem 5.1.

### 6.4.  The new sharpest open question

The wire attack reduces the open hardness question to a sharper form:

> **Question 6.1.**  Is there a polynomial-time reduction from any
> NP-hard problem to tournament Path-FAS that uses *only* the
> following operations on the score-window substrate `H`?
>
> 1. Building forced-forward arcs (not back-arcs) to encode constraints
>    that do *not* consume back-degree.
> 2. Bounded-occurrence SAT (≤ 2) variants on Hall-forced (but not
>    pairwise-forced) relations.
> 3. Multi-path or branching `H` structures whose junction vertices are
>    *not* interior of any forced path.

A positive answer would yield NP-hardness.  A negative answer (an
impossibility theorem) would essentially complete the structural
side of the project (`docs/general_path_fas_reduction.md` § 6.5)
and reduce the hardness route to (1) above, which intersects
non-trivially with the dynamic-programming approach.

## 7. Citations (verified identifiers)

* **Aboulker–Aubian–Lopes, *Finding forest-orderings of tournaments is
  NP-complete*** (2024).  [arXiv:2402.10782](https://arxiv.org/abs/2402.10782).
  The source of Problem 4.4.  Their Theorem 1.1 proves Forest-FAS is
  NP-complete; Problem 4.4 asks the path-/matching-FAS open variant.

* **Fortune, Hopcroft, Wyllie, *The directed subgraph homeomorphism
  problem*** (1980).  *Theoretical Computer Science* 10(2):111–121.
  [DOI 10.1016/0304-3975(80)90009-2](https://doi.org/10.1016/0304-3975(80)90009-2).
  Proves NP-hardness of 2-Disjoint Directed Paths on general
  digraphs.

* **Garey, Johnson, Tarjan, *The planar Hamiltonian circuit problem
  is NP-complete*** (1976).  *SIAM J. Comput.* 5(4):704–714.
  [DOI 10.1137/0205049](https://doi.org/10.1137/0205049).  Their
  Section 3 proves Hamiltonian path is NP-hard on planar cubic
  bipartite graphs.

* **Schaefer, *The complexity of satisfiability problems*** (1978).
  STOC 1978: 216–226.  [DOI 10.1145/800133.804350](https://doi.org/10.1145/800133.804350).
  Includes the NP-completeness of NAE-3-SAT and the dichotomy
  theorem for Boolean CSPs.

* **Charbit, Thomassé, Yeo, *The minimum feedback arc set problem is
  NP-hard for tournaments*** (2007).  *Combinatorics, Probability and
  Computing* 16(1):1–4.  [HAL lirmm-00140321](https://hal.science/lirmm-00140321).
  Tournament-FAS NP-hardness (not directly used here; see
  `docs/general_path_fas_hardness.md` § 2.1 for the discussion of why
  this does not transfer to Path-FAS).

## 8. Files added by this probe

* `scripts/forced_path_tournament.py` — Empirical sweep over forced-
  path lengths in 3 tournament families.
* `scripts/variable_wire_gadget.py` — Constructor for tournaments with
  designated forced-back-arc paths of length `k`.
* `scripts/clause_wire_gadget.py` — Attempt to attach literal vertices
  to wire interiors; empirical confirmation of the obstruction.
* `scripts/sat_to_path_fas_wire_reduction.py` — Architectural
  compilation of NAE-3SAT into the wire architecture, plus
  obstruction detection.
* `tests/test_wire_reduction.py` — 8 passing tests pinning the
  obstruction.
* `data/forced_path_sweep_20260527.json` — Output of the empirical
  sweep across families and `n ∈ {8, 10, 12, 14, 16, 20}`.
* This document.

## 9. Reproducing the experiments

```bash
cd problems/path_matching_fas

# Section 2: empirical forced-path sweep
uv run python scripts/forced_path_tournament.py --sweep --trials 2000 \
    --seed 20260527 --out data/forced_path_sweep_20260527.json

# Sections 3-4: variable and clause wire gadgets
uv run python scripts/variable_wire_gadget.py --all
uv run python scripts/clause_wire_gadget.py --mode single_literal --k 2

# Section 5: architectural compilation + obstruction detection
uv run python scripts/sat_to_path_fas_wire_reduction.py

# Tests
uv run pytest tests/test_wire_reduction.py -v
```
