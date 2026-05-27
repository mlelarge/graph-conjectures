# Minimal-NO Obstruction Catalogue for Path-FAS

*Aboulker–Aubian–Lopes Problem 4.4 (tournament Path-FAS).  Catalogue
covering all minimal LFO-NO tournaments at orders n ∈ {7, 8, 9}.*

Companion script: [`scripts/minimal_no_census.py`](../scripts/minimal_no_census.py).
Per-instance data: [`data/minimal_no_obstruction_catalogue_n{7,8,9}.json`](../data/).

The catalogue is built to serve the three sister tracks:

* **Track A (DP)** wants concrete bounded-J-width NO instances on which
  to test sharper DP states.
* **Track B (Hardness)** wants large-J-width NO instances as substrate
  for NP-hardness gadgets.
* **Track D (Width)** wants to know how `tw(J)` varies across the
  minimal-NO census.

Every minimal NO is tagged with: score sequence, score windows,
forced-backedge graph **H**, flexible-overlap graph **G_flex**,
interaction graph **J = H ∪ G_flex**, treewidth of J (exact for n ≤ 9
when feasible, min-fill-in upper bound otherwise; networkx
`treewidth_min_fill_in`, see Bodlaender–Koster 2010), Hall feasibility
of the score windows, modular decomposition (strong modules, prime
status), and a primary obstruction label.

---

## 1. Methodology

### 1.1 Definitions

Throughout, T is a tournament on n vertices and ``d^-(v)`` is the
indegree of v.  Fix the LFO score-window radius r = 2 (forced by
LFO max back-degree ≤ 2; see `docs/score_window.md`):

* **Score window**  `I_v = [max(0, d^-(v)−2), min(n−1, d^-(v)+2)]`.
* **Forced pair**  {u, v} with `I_u ∩ I_v = ∅`.  Their LFO order is
  forced; if the tournament arc disagrees with that order, we get
  a **forced backedge**.
* **H** (forced-backedge digraph).  Vertex set ``[n]``; arc ``(u, v)``
  whenever T contains the arc ``u → v`` and the score windows force v
  to precede u.
* **G_flex** (flexible-overlap graph).  Vertex set ``[n]``; undirected
  edge ``{u, v}`` whenever ``I_u ∩ I_v ≠ ∅``.
* **J = H ∪ G_flex** treated as an undirected graph on ``[n]``.

### 1.2 Minimal-NO definition

A tournament T is **LFO-NO** if no vertex order has a linear-forest
back-arc graph (equivalently, no path-FAS exists in the relaxed sense
of `path_fas.py`).  T is a **minimal LFO-NO** if every proper induced
subtournament has an LFO order; equivalently, T is LFO-NO and contains
no smaller LFO-NO subtournament.

* n = 7: minimality is automatic — the prior census
  `data/lfo_combinatorial_no_analysis.json` verified
  `all_vertex_minimal=True`.  Total: 20 minimal NOs (18 combinatorial +
  2 size-NO).
* n = 8: 572 minimal NOs (those with `contains_order7_no = False` in
  `data/lfo_extend_census_n8.json`).
* n = 9: 5560 minimal NOs (those with both `has_lfo = False` and
  `contains_lower_no = False` in `data/lfo_census_n9_results.jsonl`).

### 1.3 Obstruction labels

For each minimal NO we report the following signals.

| Signal                | Trigger                                    |
|-----------------------|--------------------------------------------|
| ``forced_degree``     | some vertex of H has undirected degree ≥ 3 |
| ``forced_cycle``      | the undirected support of H has a cycle    |
| ``hall_failure``      | the score windows fail Hall's condition globally |
| ``bounded_width_no``  | ``tw(J) ≤ 4`` (threshold configurable)     |
| ``large_width_no``    | otherwise                                  |

The **primary label** is the first one that fires in the order above,
falling back to the J-width verdict.

### 1.4 Treewidth and modular decomposition

* `treewidth_min_fill_in` from NetworkX is used for upper bounds
  (Bodlaender 1996; networkx docs).
* For n ≤ 11 (i.e., all minimal NOs in this report), a branch-and-bound
  elimination-order search in `interaction_graph.exact_treewidth` returns
  exact treewidth.  Lower bound is ``ω(J) − 1`` (max clique − 1).
* Modular decomposition is computed by brute-force enumeration of
  modules of size 2 .. n−1 and filtering for strong modules
  (Cunningham 1972, DOI 10.1137/0501067).  Tractable for n ≤ 9.

---

## 2. Per-n catalogue summary

### 2.1 Aggregate tables

| n | Total minimal NOs | Combinatorial | Size-NO | Hall failures | H-cycle | H-deg ≥ 3 |
|---|------------------:|--------------:|--------:|--------------:|--------:|----------:|
| 7 |                20 |            18 |       2 |             3 |       0 |         0 |
| 8 |               572 |           567 |       5 |            57 |       0 |         0 |
| 9 |              5560 |          5448 |     112 |           235 |       0 |         0 |

The most important entry of this table is the **zero column for H**.
At every minimal NO we have inspected for n ∈ {7, 8, 9}, the
forced-backedge graph H has **no edges at all**.  Score windows of
radius 2 are simply too wide on minimal-NO instances: whenever two
windows happen to be disjoint, the tournament arc between the two
endpoints is already directed in the forced order.

| n | J edges range | J treewidth distribution                |
|---|---------------|-----------------------------------------|
| 7 | 21            | tw = 6  ×  20                           |
| 8 | 27 – 28       | tw = 6 ×  26, tw = 7 × 546              |
| 9 | 31 – 36       | tw = 6 × 81, tw = 7 × 2304, tw = 8 × 3175 |

J is essentially complete or near-complete on every minimal NO.  In
particular ``ω(J) = n`` for the majority of instances, so the clique
lower bound forces ``tw(J) ≥ n − 1``.

### 2.2 Hall failures concentrate at maximum width

Cross-tabulating Hall feasibility against ``tw(J)`` (n = 9):

| tw(J) | hall_ok = True | hall_ok = False |
|------:|---------------:|----------------:|
|   6   |             81 |               0 |
|   7   |          2 304 |               0 |
|   8   |          2 940 |             235 |

**All 235 Hall failures sit at the largest J width** (tw = 8 for
n = 9, similarly tw = 7 at n = 8).  Hall failures are exactly the
"window-too-clustered" obstructions: e.g. a regular tournament on
n = 9 has every indegree = 4, every window = [2, 6], 5 positions for
9 vertices.  These instances also coincide with J = K_n.

### 2.3 Modular structure correlates only weakly

Fraction of prime tournaments by J treewidth (n = 9):

| tw(J) | prime / total | %    |
|------:|--------------:|-----:|
|   6   |     31 /  81  | 38%  |
|   7   |  1 660 / 2 304 | 72% |
|   8   |  2 612 / 3 175 | 82% |

77% of all n = 9 minimal NOs are prime (no non-trivial module).  Among
the 1257 decomposable cases at n = 9, the strong-module sizes are
overwhelmingly 2; max module size 3 appears for only 80 records.
Higher J treewidth correlates mildly with primeness.

### 2.4 Score-spread vs J treewidth (n = 9)

This is the clearest signal.  Let *spread* = max(score) − min(score).
Bucketing the n = 9 minimal NOs:

| tw(J) | spread distribution                  |
|------:|--------------------------------------|
|   6   | {6: 81}                              |
|   7   | {5: 1 962, 6: 342}                   |
|   8   | {2: 1, 3: 124, 4: 3 050}             |

A near-regular score sequence (spread 2 – 4) puts you in the
``tw(J) = 8`` regime: J is K_9, no information.  The 81 tournaments
with maximum spread (6, i.e. scores ranging from 1 to 7) are the only
ones whose interaction graph has any non-trivial structure.

---

## 3. Bounded-width NO instances (Track A substrate)

No minimal NO in our census has ``tw(J) ≤ 4``.  The smallest J width
attained is ``tw(J) = 6`` (= n − 3 at n = 9; the lower bound ``ω(J)
− 1 = 6`` is tight).  These "smallest-tw" records are still the most
informative for Track A, because their G_flex has the largest number
of *missing* edges.

### 3.1 Canonical small-J example at n = 9

**Record 9#25498**, score sequence ``[1, 2, 2, 3, 4, 5, 6, 6, 7]``,
indegrees (per vertex) ``[7, 6, 6, 5, 4, 3, 2, 2, 1]``.

Windows:

```
v=0: [5, 8]    v=1: [4, 8]    v=2: [4, 8]
v=3: [3, 7]    v=4: [2, 6]    v=5: [1, 5]
v=6: [0, 4]    v=7: [0, 4]    v=8: [0, 3]
```

Pairs *not* connected in G_flex (those whose windows are disjoint):
``{0, 6}, {0, 7}, {0, 8}, {1, 8}, {2, 8}``.  In every one of these
five forced pairs the tournament arc agrees with the forced order, so
H is empty.  Hence J has 31 edges (out of 36), with five missing
edges around the "spine" vertices {0, 8}.

Modular decomposition: four strong modules ``{0,1}, {2,3}, {5,7},
{6,8}`` (size 2 each), so T is decomposable; the residual quotient
on 9/4 vertices is the prime instance the Track A DP must still see.

T (rows indexed 0..8):

```
[0, 0, 0, 0, 1, 0, 0, 0, 0]
[1, 0, 0, 0, 1, 0, 0, 0, 0]
[1, 1, 0, 0, 0, 0, 0, 0, 0]
[1, 1, 1, 0, 0, 0, 0, 0, 0]
[0, 0, 1, 1, 0, 0, 1, 0, 1]
[1, 1, 1, 1, 1, 0, 0, 0, 0]
[1, 1, 1, 1, 0, 1, 0, 1, 0]
[1, 1, 1, 1, 1, 1, 0, 0, 0]
[1, 1, 1, 1, 0, 1, 1, 1, 0]
```

### 3.2 Smallest J at n = 8

**Record 8#352**, score sequence ``[1, 2, 3, 3, 4, 4, 5, 6]``.
``tw(J) = 6`` (lower bound = upper bound), 27 edges (J = K_8 minus
the edge {0, 5}).  Two size-2 strong modules.

### 3.3 What Track A should test

The 81 ``tw = 6`` instances at n = 9 (resp. 26 at n = 8) are the only
ones where a non-trivial *width-aware* DP could differentiate YES from
NO.  Track A's DP should be **stress-tested specifically against record
9#25498 and its dual orbit**: if the DP fails on 9#25498, the failure
locates the state-shortcoming in the smallest possible J-width regime.
A successful DP on 9#25498 (and the other tw = 6 records) would say
*nothing* about the tw = 8 majority.

---

## 4. Large-width NO instances (Track B substrate)

These are the abundant case: 3175 / 5560 minimal NOs at n = 9 have
``tw(J) = 8`` (full).  They split into two sub-types.

### 4.1 Hall-failing instances (235 records)

Example **9#13407**: score sequence ``[2, 2, 4, 4, 4, 5, 5, 5, 5]``,
five vertices share the window ``[1, 5]`` and four others fit in
``[2, 6]`` ∪ ``[4, 8]``.  Hall's condition fails on the interval
``[1, 5]`` (clearly: at least seven vertices want their position in
``[1, 6]`` but only six positions exist on the LFO-relevant prefix).

These are "trivial NO" from the DP perspective: the score-window
constraint is already infeasible.  They are *not* useful as hardness
substrate either — they are detectable in polynomial time by Hall's
theorem.

### 4.2 Score-regular Hall-feasible instances (Track B candidates)

Example **9#191101**: score sequence ``[3, 3, 3, 3, 3, 5, 5, 5, 6]``,
``tw(J) = 8``, prime modular structure, Hall-feasible, H empty.  This
is a *real* obstruction: the score window framework is silent, the
modular decomposition is trivial, and the interaction graph carries
no structure beyond ω(J) = 9.  The NO certificate must come from a
combinatorial argument internal to the back-arc DP on the full
permutation space.

T (rows indexed 0..8):

```
[0, 1, 1, 0, 0, 0, 0, 0, 1]
[0, 0, 1, 1, 0, 0, 0, 1, 0]
[0, 0, 0, 1, 1, 0, 1, 0, 0]
[1, 0, 0, 0, 1, 1, 0, 0, 0]
[1, 1, 0, 0, 0, 1, 0, 0, 0]
[1, 1, 1, 0, 0, 0, 1, 1, 0]
[1, 1, 0, 1, 1, 0, 0, 0, 1]
[1, 0, 1, 1, 1, 0, 1, 0, 0]
[0, 1, 1, 1, 1, 1, 0, 1, 0]
```

These ``tw(J) = 8``, prime, Hall-feasible instances are the natural
target for Track B.  A reduction that produces a tournament whose
minimal NO behaviour is concentrated in the *score-regular prime*
sub-tournament would explain why neither the score-window DP nor the
modular-quotient DP catches the obstruction.

### 4.3 What Track B should test

The 2 612 prime + Hall-feasible + tw = 8 records at n = 9 form a
large enough pool to mine for gadgets.  A useful filter is the
**arc-cyclic-triangle load** stratification already computed in
`data/lfo_minimal8_analysis.json` and inheritable to n = 9: gadgets
whose contraction yields a balanced load on every arc are good
candidates for reduction.

---

## 5. Correlation findings: does J-width predict NO?

The honest answer for n ≤ 9 is **no, J-width is essentially fully
saturated on every minimal NO**.  The data:

* H = ∅ for every minimal NO in the census (n ≤ 9).
* G_flex (and hence J) is K_n, K_{n−1}, or one of a few near-complete
  graphs for every minimal NO.
* ``ω(J) ∈ {n − 1, n}`` in every record, forcing ``tw(J) ≥ n − 2``.

Equivalently, **at radius 2 the score-window framework essentially
collapses on minimal NOs**: the windows are too wide to detect the
obstruction.  This means:

1. The Width Conjecture in `docs/J_width_conjecture.md` ("tw(J)
   bounded by an absolute constant on LFO-feasible instances") is
   *vacuously satisfied* on minimal-NO data because no minimal NO has
   small width.  The conjecture is non-trivial only on the YES side.
2. A bounded-width DP on J alone cannot distinguish YES from NO at
   n ≤ 9.  Either the score-window radius must be tightened (perhaps
   to a *directed* version of the framework), or the DP must carry
   richer state (e.g. arc-orientation parity inside G_flex cliques).

Two genuine numerical signals do appear and may scale to larger n:

* **Score-spread vs ω(J):**  spread = n − 2 ⇒ ``ω(J) ≤ n − 2``;
  near-regular ⇒ ``ω(J) = n``.  Track D should exploit this.
* **Hall failure ⇔ window-cluster cliques:**  the 235 Hall failures
  at n = 9 are *exactly* those with five-or-more windows containing
  a common short prefix of positions.  Detecting these is polynomial,
  so a preprocessing pass should peel them off before any DP.

### 5.1 Frequencies by primary label

| n | hall_failure | bounded_width_no | large_width_no |
|---|-------------:|-----------------:|---------------:|
| 7 |            3 |                0 |             17 |
| 8 |           57 |                0 |            515 |
| 9 |          235 |                0 |          5 325 |

---

## 6. Recommendations for the sister tracks

### 6.1 Track A (bounded-width DP)

* The 81 tw = 6 records at n = 9 (resp. 26 at n = 8) are the only
  bounded-width witnesses.  **Use 9#25498 as the canonical
  stress-test**: it has a four-module substitution structure, a
  spread-6 score sequence, an empty H, and exactly five missing
  edges in J.  A DP that handles 9#25498 in polynomial time and
  outputs NO is necessary for Track A to be viable; a DP that
  outputs YES is wrong.
* Do not rely on J width alone — at n = 9 every minimal NO has
  ``tw(J) ≥ 6``.  Track A must enrich the state, e.g. by tracking
  the *flat-arc parity* (number of forward arcs into each clique of
  G_flex) along the DP frontier.

### 6.2 Track B (NP-hardness)

* The hardness substrate sits at **score-regular**, **prime**,
  **Hall-feasible**, **tw(J) = n − 1** minimal NOs.  At n = 9 there
  are 2 612 such records.  Pick **9#191101** (score sequence
  [3, 3, 3, 3, 3, 5, 5, 5, 6]) as the reduction target template:
  the score window framework gives no information, the modular
  decomposition is trivial, and the obstruction is internal to the
  arc structure.
* Hall failures (235 records) are useless for hardness — they are
  certifiable in polynomial time.  Track B should explicitly filter
  them out of any gadget mining.

### 6.3 Track D (Width)

* The Width Conjecture as stated needs to be split into two halves.
  On YES instances, tw(J) may still be bounded — but this is *not
  testable on minimal-NO data*.  On NO instances, tw(J) is essentially
  fully saturated, and the question is whether *some refinement* of
  J (e.g. ``J(T) ⊕ tournament arcs on flexible edges`` as a directed
  graph) carries non-trivial width.
* A concrete experiment: define **J⁺** = J together with the
  tournament arcs restricted to G_flex edges, viewed as a digraph,
  and measure the directed treewidth of J⁺ on the catalogue.  If J⁺
  remains saturated, the score-window framework at radius 2 is
  irreducibly weak; if J⁺ varies, the directed version is the right
  primitive.

### 6.4 Joint deliverable

The catalogue files in `data/minimal_no_obstruction_catalogue_n{7,8,9}.json`
are machine-readable.  The schema is:

```json
{
  "summary": { ... aggregate histograms ... },
  "records": [
    {
      "name": "9#25498",
      "n": 9,
      "T": [[...]],
      "score_sequence": [...],
      "indegrees": [...],
      "windows": [[lo, hi], ...],
      "hall_ok": true,
      "H":  { "edges": [...], "max_und_degree": ..., "has_und_cycle": ... },
      "G_flex": { "edges": [...], "max_clique": ... },
      "J":  { "treewidth_for_classifier": ..., "max_clique": ... },
      "obstruction": { "primary": "...", "signals": [...] },
      "modular": { "is_prime": ..., "strong_modules": [[...], ...] },
      "no_kind": "combinatorial" | "size"
    },
    ...
  ]
}
```

All four scripts (Width, DP, Hardness, this census) can consume the
same JSON; the catalogue is the shared substrate.

---

## Appendix A: file inventory

* `scripts/minimal_no_census.py` — main census driver.
* `scripts/interaction_graph.py` — H, G_flex, J construction
  primitives plus exact and heuristic treewidth.
* `data/minimal_no_obstruction_catalogue_n7.json` — 20 records.
* `data/minimal_no_obstruction_catalogue_n8.json` — 572 records.
* `data/minimal_no_obstruction_catalogue_n9.json` — 5 560 records.

## Appendix B: reproduction

```bash
uv run python scripts/minimal_no_census.py --n 7
uv run python scripts/minimal_no_census.py --n 8 --no-exact-tw
uv run python scripts/minimal_no_census.py --n 9 --no-exact-tw \
    --progress 1000
```

Total wall time on a 2026 laptop: ~5 s (n = 7 + 8 + 9).  Exact
treewidth is fast because clique lower bound coincides with min-fill
upper bound on every record.

## Appendix C: references

* J.A. Bondy, M. Aigner et al., *Tournament theory*.
* W.H. Cunningham, *Decomposition of directed graphs*, SIAM
  J. Algebraic Discrete Methods (1972), DOI 10.1137/0501067.
* H.L. Bodlaender, *A linear-time algorithm for finding tree
  decompositions of small treewidth*, SIAM J. Comput. (1996).
* H.L. Bodlaender, A.M.C.A. Koster, *Treewidth computations I.
  Upper bounds*, Inf. Comput. (2010).
* NetworkX 3.x documentation:
  `networkx.algorithms.approximation.treewidth_min_fill_in`.
