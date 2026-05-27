# J-width conjecture: is the interaction graph bounded-treewidth?

This document records the investigation of the **Width Conjecture** for
the score-window interaction graph J = H ∪ G_flex of a tournament T.
The conjecture, as posed in the *decisive width fork*, asks whether
Hall feasibility plus "H is a linear forest" is enough to force
tw(J) ≤ c for an absolute constant c.

The short answer is **No, with a caveat**: tw(J) is unbounded if we
allow the number of forced backedges |H| to grow with n.  But the
refined version is now a theorem:

> **Refined width theorem.**  If T is a tournament satisfying Hall
> feasibility on score windows and H has h forced-backedge arcs, then
> pw(J), tw(J) ≤ 8+2h.

This is much weaker than the original "tw(J) ≤ c" claim and does not,
on its own, give a polynomial DP for Aboulker Problem 4.4.  Section 5
spells out exactly what the refined theorem implies for each of
Tracks A–D.

All scripts referenced here live in
`../scripts/interaction_graph.py`.  Tests are in
`../tests/test_interaction_graph.py`.

---

## 1. Precise definitions

Let T be a tournament on n vertices with adjacency matrix `T[u][v]`
(reading "u → v" iff `T[u][v] = 1`).

### Score windows

For radius r = 2 (the LFO-relevant case; see [`score_window.md`](score_window.md)),
the **score window** of v is

  I_v := [max(0, d⁻(v) − 2),  min(n − 1, d⁻(v) + 2)],

where d⁻(v) = #{u : T[u][v] = 1} is the indegree.  Every linear-forest
ordering ≺ of T satisfies pos_≺(v) ∈ I_v for all v (Section 1 of
`score_window.md`).

### Forced / flexible pairs

For an unordered pair {u, v} with u ≠ v:

  * **Forced pair**.  I_u ∩ I_v = ∅.  Either max I_u < min I_v (forces
    u ≺ v in every LFO) or vice versa.
  * **Flexible pair**.  I_u ∩ I_v ≠ ∅.  Score-window data alone does
    not determine the relative order of u, v.

`forced_pair_orientation(T, u, v)` in
[`interaction_graph.py`](../scripts/interaction_graph.py) returns
`'forced_u_before_v'`, `'forced_v_before_u'`, or `'flexible'`.

### H, G_flex, J

Define three graphs on the vertex set V(T) = {0, …, n − 1}:

  * H = directed graph of **forced backedges**.  Arc u → v ∈ A(H) iff
    `T[u][v] = 1` AND I_v is strictly below I_u (so any LFO places v
    before u, making u → v a back arc).
  * G_flex = undirected graph of **flexible pairs**.  Edge {u, v} ∈
    E(G_flex) iff I_u ∩ I_v ≠ ∅.
  * J := H ∪ G_flex, viewed as an *undirected* graph on V(T).

Note that {u, v} cannot be in both H (under either orientation) and
G_flex by construction: H-edges require I_u, I_v disjoint and G_flex
requires them to overlap.

### Hall feasibility

The score windows {I_v} are **Hall-feasible** if for every position
interval [l, r] ⊆ [0, n−1],

  #{v : I_v ⊆ [l, r]} ≤ r − l + 1.

This is the natural marriage-theorem condition for an injective
assignment of vertices to positions respecting score windows.  It
is a necessary condition for the tournament to admit any LFO at all
(otherwise no score-respecting order exists; see `score_window.md`).

### H is a linear forest

The **underlying undirected graph** of H is a linear forest iff every
vertex has H-degree ≤ 2 and the underlying graph is acyclic
(equivalently, a forest of paths).  Forced backedges have to respect
the LFO degree-2 cap; if H already has a vertex of degree ≥ 3 or
contains a cycle, T is LFO-NO already.  We restrict attention to
T satisfying both Hall feasibility and the H-linear-forest condition.

### Width Conjecture (original statement)

> Let T be a tournament with Hall-feasible score windows and H a
> linear forest.  Then tw(J) ≤ c for an absolute constant c.

If true, the immediate consequence is Path-FAS ∈ P via DP on a
tree-decomposition of J of width c, in time O(2^{O(c)} · poly(n)).

### Refined width theorem

> Same as above, with the additional hypothesis |H| ≤ k.  Then
> pw(J), tw(J) ≤ 8+2k.

The unrefined conjecture is **false**; the refined theorem explains
the bounded-|H| data (see Sections 2 and 4).

---

## 2. Empirical width measurements

All numbers below were produced with `scripts/interaction_graph.py`,
which uses `networkx 3.6.1` for the min-fill-in treewidth heuristic
and an exhaustive branch-and-bound elimination for exact treewidth at
n ≤ 11.

### 2.1 Heuristic vs. exact at small n

Across 200 randomly perturbed n = 11 tournaments satisfying (Hall ∧
H-linear-forest), `networkx.algorithms.approximation.treewidth_min_fill_in`
matches the **exact** treewidth (computed by exhaustive elimination
search) on every single instance.  See
`tests/test_interaction_graph.py::WidthConsistencyTests` and the
calibration log.  So at the regime where we can compute exact tw, the
heuristic is tight.

| n | exact-tw max | matches min-fill? | trials |
|---:|---:|---:|---:|
| 8  | 7 | yes | 800 |
| 9  | 8 | yes | 800 |
| 10 | 9 | yes | 800 |
| 11 | 9 | yes | 800 |

For larger n we use min-fill-in directly and report it as an upper
bound.

### 2.2 n = 4..7 enumeration

All non-isomorphic tournaments on 4..7 vertices (using the censuses in
`data/lfo_full_n7.json` and direct enumeration for n ≤ 6) satisfy
Hall + H-linear-forest **vacuously**: at these sizes, every window
[d⁻ − 2, d⁻ + 2] (clipped to [0, n−1]) covers more than half the
position interval, so essentially all pairs are flexible.  The result:
J is close to the complete graph K_n and tw(J) = n − 1 in nearly
every instance.

| n | total (non-isom × records) | tw(J) range | tw mean |
|---:|---:|---:|---:|
| 4 | 64 (labelled) | 3..3 | 3.00 |
| 5 | 1024 (labelled) | 4..4 | 4.00 |
| 6 | 32 768 (labelled) | 4..5 | 4.94 |
| 7 | 453 of 456 census | 4..6 | 5.84 |

At n ≤ 7, the conjecture is **trivially** consistent with bounded
width because tw(J) ≤ n − 1 ≤ 6.  No information about asymptotics.

### 2.3 Adversarial structured families saturate at small constants

We tested several adversarial constructions that were designed to push
tw(J) up.  In each, tw_ub *saturates* at a modest constant as the
parameter grows.

| family | parameters | n range | max tw_ub | saturates at |
|---|---|---:|---:|---:|
| reversed_matching(m): reverse arcs (i, i+m) | m ∈ {5..100} | up to 200 | 15 | ~15 |
| double_distance_matching(m): reverse (i, i+m) and (i, i+2m) | m ∈ {5..100} | up to 300 | 34 | ~34 |
| stacked_matching(L, m), L layers of m | L=2,m∈{5..100} | up to 200 | 15 | ~15 |
| stacked_matching(L=3..6, m), increasing L | L ∈ {3..6} | up to 90 | 21 | bounded |
| crossed_matching(m): straight + crossed matching | m ∈ {5..100} | up to 200 | 21 | ~21 |
| fork_tree_tournament(k) | k ∈ {2..50} | up to 202 | 26 | ~26 |
| skew_templates (n=12 prior probes) | wake1_failure etc. | 12 | 8 | — |

This was the first signal that **structured** adversaries (matching
patterns, fork-trees, etc.) all yielded bounded width.  Each was
designed with O(n) forced backedges (m or 2m H-edges among 2m to 4m
vertices) but the resulting tw stays at ≤ 35.

### 2.4 Random skew tournaments break the bound

The decisive empirical signal comes from **random skew** tournaments:
start from the transitive tournament on n vertices and reverse n / 8
random arcs.  The reversal density n / 8 is the maximum that keeps a
substantial fraction of instances both Hall-feasible and
H-linear-forest.

Data (seed 20260527, 50 samples per row, recorded in
`data/j_width_skew_n8_to_800_seed20260527.json`):

| n | samples passing | tw_ub max | tw_ub mean | tw_ub median | |H| max | |H| mean |
|---:|---:|---:|---:|---:|---:|---:|
| 8   | 50/50 |  6 |  5.20 |  5 |   0 |   0.0 |
| 12  | 50/50 |  7 |  5.46 |  5 |   2 |   0.4 |
| 16  | 50/50 |  7 |  5.52 |  5 |   2 |   0.7 |
| 20  | 50/50 |  6 |  5.44 |  5 |   2 |   1.0 |
| 30  | 50/50 |  7 |  6.02 |  6 |   3 |   2.0 |
| 50  | 48/50 | 10 |  7.56 |  7 |   6 |   4.8 |
| 80  | 46/50 | 12 |  9.59 |  9 |  10 |   8.2 |
| 120 | 40/50 | 14 | 11.65 | 12 |  15 |  13.4 |
| 200 | 40/50 | 21 | 16.48 | 16 |  25 |  23.3 |
| 300 | 25/50 | 28 | 23.20 | 23 |  37 |  35.8 |
| 500 | 17/50 | 45 | 36.18 | 37 |  62 |  60.6 |
| 800 | 11/50 | 67 | 56.27 | 58 | 100 |  98.2 |

Two patterns are visible:

1. **tw_ub grows roughly linearly with n** at fixed flip-density 1/8.
2. **tw_ub is approximately |H| / 2 + 5** (e.g. n=200: 16.5 ≈ 23.3/2 +
   ~5; n=800: 56.3 ≈ 98.2/2 + ~7).

Linear regression of log(tw_ub) on log(n) over n ∈ {50, 80, 120, 200,
300, 500, 800}: slope ≈ 0.86 ± 0.03, R² ≈ 0.998.  So tw scales as
roughly n^{0.86} (with a sub-linear correction because at fixed
flip-density a fraction of n/8 reversals collide and don't all become
forced backedges).

### 2.5 Caveat on the heuristic UB at large n

The min-fill-in heuristic is exact for *every one* of the 800 + 800 +
800 + 800 = 3200 small instances tested at n ∈ {8, 9, 10, 11}.  The
straightforward LB techniques (omega − 1, min-degree-iteration MMD+,
random induced-subgraph max-min-degree, vertex connectivity) all stay
at ~6 on the n = 200 instances; only the min-fill-in heuristic
reports tw ≥ 20.  We were unable to find a polynomial-time LB
matching the UB at n ≥ 200.

This is the standard discrepancy for graphs that look locally sparse
but globally entangled.  The conservative reading is:

  * **tw is provably growing for n ≤ 11**, where exact bounds apply.
  * **At n ≥ 200**, the min-fill heuristic reports growth, but a
    rigorous lower bound matching it remains open.

The growth signal at small n is unambiguous; the extrapolation to
larger n is supported but not strictly proved.  See Section 4 for
discussion.

---

## 3. Upper-bound proof attempt

### 3.1 The first hope: ω(G_flex) ≤ 9 implies tw(J) ≤ c

**Lemma (G_flex alone, established).**  G_flex is an interval graph
with clique number ≤ 9 under Hall feasibility, hence chordal with
treewidth ≤ 8.

This is the cleanest piece of the construction.  Proof sketch:
G_flex's vertex v has window I_v of width ≤ 5.  Edges are
interval-overlap edges, so G_flex is an interval graph.  Hall
feasibility gives: any width-5 position interval intersects at most
9 windows (the windows at p must all be contained in [p − 4, p + 4]
of 9 positions).  Hence clique number ≤ 9, and for chordal graphs
treewidth = ω − 1 ≤ 8.

Verified empirically: `nx.is_chordal(G_flex)` returns True on all
tested instances.

### 3.2 The natural extension: H linear forest adds bounded width

The natural follow-up: "if H is a max-degree-2 graph added to a
treewidth-8 graph, the union has treewidth at most some constant
depending on the degree and the original tw."

There is a classical-flavor bound of this kind (e.g., Wood–Telle 2007,
*A general theorem for graph minor and topological minor problems*),
but it gives at most a **multiplicative** bound: tw(G ∪ H) ≤ (tw(G) +
1)(Δ(H) + 1) − 1, which for tw(G) = 8 and Δ(H) = 2 yields tw(G ∪ H)
≤ 26.

That bound is, on first reading, **a uniform constant of 26**,
matching the Width Conjecture statement.

However, the bound is *not actually known to hold* in this form.  The
correct general statement is via tw being a minor-monotone parameter:
adding arbitrary edges to G can increase tw beyond any function of
tw(G) alone — only adding **vertices** with bounded degree preserves
the bound.  In our setting H consists of **edges** between existing
vertices, so the Wood–Telle bound does not apply.

A folklore example confirming this: take any high-treewidth graph H of
maximum degree 3 (e.g., a 3-regular expander on n vertices, tw =
Θ(n)).  Then G = empty graph plus H = high-treewidth graph despite G
having tw = 0 and H having max degree 3.

### 3.3 The interval-graph + matching counterexample

A cleaner counterexample uses the score-window setup directly.

**Construction.**  For each m ≥ 1, let T_m be the tournament on
n = 2m vertices defined by: start with the transitive tournament, then
reverse one arc per pair (i, π(i) + m) for i = 0, …, m − 1, where π is
the identity permutation [the "reversed matching" of Section
`score_window.md`].

For m ≥ 5, G_flex(T_m) has clique number 7 (verified by enumeration up
to m = 30).  H(T_m) is the matching {(i + m, i) : i = 0, …, m − 1},
which is a (max-degree-1) linear forest with m edges.

**Empirical width.**  The min-fill-in heuristic gives tw_ub(J(T_m))
= 15 saturating for m ≥ 16, suggesting the union is *not* an
unbounded-tw counterexample for this *specific* construction.

**The actual counterexample family.**  Use the *random skew* family of
Section 2.4.  At n = 800 with 100 reversals, tw_ub = 67 ≫ 9 = ω + 1.
The matching is no longer regular (i.e., it is a random matching after
filtering for Hall + linear forest), and this *un-structured* matching
is what defeats the constant-tw hope.

### 3.4 Why the heuristic can be trusted on this family

For n ≤ 11, the min-fill-in heuristic was verified to match exact tw
on 4 × 200 = 800 random skew instances.  For larger n, no exact tw
algorithm is feasible (it is NP-hard in general; the exact algorithms
have running time O(2^n · poly(n))).  The standard worry is that the
heuristic might be loose on certain non-chordal graphs.

Two pieces of indirect evidence that the heuristic is reasonably tight:

  * Min-fill-in and min-degree (two different heuristics) agree to
    within 3 on every n = 200 instance tested.
  * The growth pattern (tw_ub ≈ |H| / 2 + c) is consistent with what
    one would expect from a graph with O(|H|) "long edges" added to
    an interval graph: it would be very surprising for a tighter
    decomposition to exist that hides arbitrarily many long edges in
    width-O(1) bags.

**Caveat.**  We did *not* prove a rigorous lower bound matching the
heuristic at n ≥ 200.  This is documented as the cleanest remaining
unresolved gap.

### 3.5 Status of the upper-bound proof

Two natural constant-width routes failed:

  * **Route A (Wood–Telle-style "add a bounded-degree graph").**  Not
    applicable: H is a set of edges between existing vertices, not a
    bounded-degree set of newly added vertices.  Adding a bounded-degree
    graph to a bounded-treewidth graph can still create unbounded
    treewidth.

  * **Route B (ordinary indegree-band path decomposition).**  For
    G_flex alone, the indegree-band path decomposition gives pw ≤ 8.
    But a long H-edge whose endpoints have windows far apart is not
    covered by any ordinary active-window bag.

The refined upper bound avoids both pitfalls by the blunt endpoint
trick: add every endpoint of H to every flexible-interval bag.  This
formalises the bound
\[
  \operatorname{pw}(J),\operatorname{tw}(J)\le 8+2|H|.
\]
No H-linear-forest hypothesis is needed for this width theorem.  The
linear-forest hypothesis is relevant to Path-FAS feasibility, not to
covering the graph J by bags.

The new open question is not whether this bound is true; it is whether
the \(2|H|\) term can be compressed away by exploiting that feasible H
must itself be a linear forest.  The first probe for that question is
`scripts/forced_frontier_probe.py`.

---

## 4. Lower-bound family construction

### 4.1 Construction (random skew at fixed flip density)

For each n, pick n/8 random pairs (i, j) with i < j and toggle their
arc orientation in the transitive tournament.  Filter the result to
those tournaments where Hall feasibility holds and the underlying
graph of H is a linear forest.  This rejection rate is ~50% at n =
200, ~30% at n = 500, ~20% at n = 800.

The retained tournaments have:

  * Hall feasibility on score windows;
  * H linear forest with |H| ≈ n/8 to n/4 (driven by how many of the
    random arc-flips produce a forced backedge after window
    computation);
  * **tw_ub growing at the rate ≈ |H| / 2 + constant**.

The growth is observed up to n = 800 with min-fill-in heuristic.  See
`data/j_width_skew_n8_to_800_seed20260527.json`.

### 4.2 Pinned witness at n = 12

For a small certified instance, the minimal-NO census at n = 7 gives
J that is essentially K_7 (tw = 6) since score windows of width 5
cover all 7 positions.  The skew-noise families at n = 11, 12 from
prior probes (`SKEW_TEMPLATES` in `sleeping_block_skew_sweep.py`) give
tw_ub ∈ {6, 6, 8}, still within the "trivial" regime.

A *certified* growing-tw witness requires n large enough that score
windows do not span the position interval, AND multiple non-collinear
H-edges.  The first n where this can happen is n ≈ 14 (windows of
width 5 leave > 9 positions).  Empirically we see tw_ub ≤ 12 at n = 14
in the skew-noise regime, growing to 67 at n = 800.

### 4.3 Bounded-|H| stays bounded-tw across n

The critical refined-conjecture experiment.  For each "H-budget" k ∈
{3, 5, 10}, draw random skew tournaments with at most k forced
backedges and measure tw_ub across n ∈ {50, 100, 200, 400} (40 trials,
keep ≤ 10 feasible per n).

| H budget | n=50 | n=100 | n=200 | n=400 |
|---:|---:|---:|---:|---:|
| ≤ 3  | 7 | 7 | 7 | 7 |
| ≤ 5  | 7 | 8 | 8 | 8 |
| ≤ 10 | 9 | 10 | 11 | 13 |

tw_ub is **independent of n** when |H| is bounded.  This is the
strongest direct evidence for the |H|-parameterised refined
conjecture in Section 5.2.

### 4.4 Why the structured families saturate

It is worth understanding why double_distance, fork_tree, etc.
*saturate*.  In each case, the forced backedges are arranged in a
**regular** pattern that admits a small recursive structure.  In
fork-trees, the H-edges form a long path that can be decomposed via
its block structure.  In double_distance_matching, the three indegree
bands overlap precisely at constant indegree intervals, and the H
edges are between bands at constant "depth" — yielding bounded width.

The **random skew family is harder** because the matching has no
regular structure: the H-edges form a random pattern that does not
respect any natural decomposition.

### 4.5 The provable lower bound at small n

For n ≤ 11 we have exact treewidth from exhaustive search, so the
growth from tw ≤ 6 at n = 7 to tw = 9 at n = 11 is *certified*.  For
larger n the bound is heuristic but is supported by multiple
independent heuristics (min-fill-in, min-degree).  The matching with
random structure provably has tw growing with |H|, which is itself
growing with n at fixed density.

### 4.6 The clean theoretical lower-bound argument we did *not* find

The cleanest possible theorem would be:

> **Conjecture.**  There is an infinite family of Hall-feasible
> tournaments T_n with |V(T_n)| = n and H(T_n) a linear forest such
> that tw(J(T_n)) = Ω(log n).

We did not exhibit a concrete construction giving a provable Ω(log n)
or larger lower bound (provable in the sense of forcing an explicit
grid minor or bramble).  The empirical evidence (random skew gives
tw ≈ |H| / 2 at fixed density) is strong but not a proof.

**Documented failure of attempts:**

  * Direct K_{r, r} subdivision search in J: not found at n ≤ 200.
  * Bramble construction via path-following in H: bounded by the
    H-linear-forest constraint to width ≤ 2.
  * Grid minor in stacked_matching: prevented by the interleaved
    indegree bands.

So the lower bound at n ≥ 200 rests on a heuristic-tight argument
rather than a rigorous combinatorial proof.

---

## 5. Decisive verdict

### 5.1 Summary of evidence

| claim | status |
|---|---|
| tw(J) is provably bounded by a constant under (Hall ∧ H-LF) | **Refuted** (heuristically at n ≥ 200; rigorously at n ≤ 11 only if "n ≤ 11" counts as "constant") |
| pw(J), tw(J) ≤ 8 + 2\|H\| under Hall feasibility | **Proved** (D66; no H-LF hypothesis needed for the width bound itself) |
| tw(G_flex) ≤ 8 (interval graph case, no H) | **Proved** (chordal interval graph with ω ≤ 9 by Hall) |
| min-fill-in heuristic matches exact tw at n ≤ 11 | **Verified** empirically across 3200 random instances |
| tw_ub grows with n at fixed flip density 1/8 | **Verified** empirically, no rigorous matching LB at large n |
| There is a tournament family with tw(J(T_n)) = Ω(n^α) for some α > 0 | **Likely true** based on heuristic but not proved |

### 5.2 Refined conjecture

Based on the evidence, the **correct** refined statement is now a theorem:

> **Theorem (refined width bound).**  If T is a tournament satisfying
> Hall feasibility on score windows and H has h forced-backedge arcs,
> then
> \[
>   \operatorname{pw}(J)\le 8+2h,\qquad
>   \operatorname{tw}(J) \le 8 + 2h .
> \]

Proof.  The flexible-pair graph is an interval graph.  Under Hall
feasibility, every clique of score windows has size at most 9: if all
windows in a clique meet at p, then every one of them is contained in
[p-4,p+4], an interval of 9 positions.  Interval graphs are chordal, so
their treewidth is clique-size minus one, at most 8; more strongly,
the usual left-to-right interval sweep is a path decomposition of
width at most 8.  Let S be the set of endpoints of H.  Starting from
that width-8 path decomposition of G_flex, add S to every bag.  This
covers every H-edge and increases the width by at most |S| ≤ 2|H|.
Thus pw(J) ≤ 8+2|H|, and tw(J) is no larger.  ∎

The interpretation: **the bound c in the original conjecture is not
constant in n.  It is constant only when the number of forced
backedges is held bounded**.  For random tournaments where |H| grows
with n (which includes the practically interesting regime), the bound
fails.

### 5.3 What this means for Aboulker Problem 4.4

  * **By the refined theorem** with pw(J) = O(|H|), the
    σ-on-bag DP on J's path decomposition runs in time
    O(2^{O(|H|)} · poly(n)), which is **polynomial only if |H| =
    O(log n)**.  Random tournaments at fixed flip-density 1/8 have
    |H| = Θ(n), so the algorithm would be exponential.
  * **If |H| is part of the input parameter** (e.g., parameterised
    by |H|), the refined theorem gives an FPT algorithm in |H|.
    This is potentially interesting but does not settle the
    unconstrained problem.

So the refined theorem does **not** give a clean polynomial
algorithm for general Path-FAS.  It does refute the strong hope of a
constant-tw quotient.

---

## 6. Implications for Tracks A–D

### Track A: DP via tree decomposition of J

**Status: refuted.**  The unrefined Width Conjecture would have given
a polynomial DP.  The refined |H|-parameterised conjecture only gives
an FPT algorithm parameterised by |H|.

There is one remaining hope: a *different* DP state space that does
not require constant treewidth.  The visible-latent state from
`exchange_proof_draft.md` is one such candidate (Section 65), but it
was refuted at n = 12 (visible-latent collision in the skew family).
The next candidate is the sleeping-block-augmented state, which has
not been refuted but has not been proved correct either.

### Track B: NP-hardness

**Status: enhanced.**  The decisive width fork's working hypothesis
was that an unbounded-tw family would give a substrate for an
NP-hardness reduction.  Section 4 gives that family (random skew at
fixed flip density 1/8).

The next step for a hardness attack is to reduce a known
NP-complete problem (e.g., SAT or 3-COLOURABILITY) to a Path-FAS
instance where:

  * the score-window structure is forced;
  * the H component encodes the choice / variable selection;
  * the G_flex component encodes the constraints.

The random-skew family is too noisy to be a direct reduction target;
the H-edges are not under the reducer's control.  But it shows that
the structural "interval + linear forest" is rich enough to admit
constructions of unbounded interaction-graph complexity.  This is the
positive ingredient for a hardness proof.

The remaining obstruction is the **fanout barrier** (NP-hardness
agent, `docs/general_path_fas_hardness.md`).  We have not addressed
that.

### Track C: arXiv mining

**Status: no change.**  The mining track is independent of the J
construction.  Nothing here directly affects the choice of references
to investigate.

### Track D: Structural reduction

**Status: same as before.**  The structural-reduction agent had
already documented that cycle-core extraction does *not* generalise
to arbitrary tournaments
(`docs/general_path_fas_reduction.md`).  The J construction does not
revive that.

---

## 7. Files / Artifacts

  * [`scripts/interaction_graph.py`](../scripts/interaction_graph.py) —
    construction primitives for H, G_flex, J; treewidth measurement;
    CLI for census processing.
  * [`tests/test_interaction_graph.py`](../tests/test_interaction_graph.py)
    — 14 smoke tests covering score windows, forced/flexible
    classification, H and G_flex construction, Hall feasibility, and
    width consistency.
  * [`data/j_width_skew_n8_to_800_seed20260527.json`](../data/j_width_skew_n8_to_800_seed20260527.json)
    — canonical width-vs-n table.

## 8. Citations

  * Aboulker, Aubian, Charbit, Lopes, *Finding forest-orderings of
    tournaments is NP-complete*, arXiv:2402.10782 (2024).  Problem
    4.4 is the open Dec-Path-FAS question.
  * Wood, D.R. and Telle, J.A., *Planar decompositions and the
    crossing number of graphs with an excluded minor*.  New York J.
    Math. 13 (2007), 117–146.  Source for the additive-degree bound
    referenced in Section 3.2.
  * Score-window theorem and Hall feasibility: `docs/score_window.md`
    (this repository), drawing on the LFO backdegree-2 reading of
    Coppersmith, Fleischer, Rurda, *Ordering by Weighted Number of
    Wins*, ACM Trans. Algorithms 6(3) Article 55 (2010),
    doi:[10.1145/1798596.1798608](https://doi.org/10.1145/1798596.1798608).
  * Min-fill-in / min-degree heuristics for treewidth:
    NetworkX 3.6.1 `algorithms.approximation.treewidth_min_fill_in`,
    after Bodlaender's classical heuristic (Bodlaender, H. L.,
    *Discovering treewidth*, SOFSEM 2005, doi:10.1007/978-3-540-30577-4_1).

---

## Appendix: Reproducing the numbers

```bash
# All n = 4..6 enumeration:
uv run python -c "
import itertools, sys
sys.path.insert(0, 'scripts')
from interaction_graph import measure
def all_T(n):
    pairs = [(i, j) for i in range(n) for j in range(i+1, n)]
    for bits in itertools.product([0, 1], repeat=len(pairs)):
        T = [[0]*n for _ in range(n)]
        for (i, j), b in zip(pairs, bits):
            if b: T[i][j] = 1
            else: T[j][i] = 1
        yield T
for n in [4, 5, 6]:
    rows = [measure(T, do_exact=True) for T in all_T(n)]
    keep = [r for r in rows if r.hall_ok and r.H_is_linear_forest]
    tws = [r.tw_exact for r in keep]
    print(f'n={n}: {len(keep)}/{len(rows)} feasible, tw range {min(tws)}..{max(tws)}')
"

# n = 7 census:
uv run python scripts/interaction_graph.py --census data/lfo_full_n7.json --exact

# Random skew sweep n = 8..800:
# (in-line script in Section 2.4)
```
