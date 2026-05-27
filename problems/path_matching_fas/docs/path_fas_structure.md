# Structural notes on the linear-forest ordering problem

This document records the empirical and structural findings from the
attack on Path-FAS / linear-forest ordering (LFO). It does not contain a
polynomial algorithm or an NP-hardness reduction.

## What LFO asks

> **LFO.** Given a tournament $T$, decide whether there exists a total
> order $\prec$ on $V(T)$ such that the back-arc graph
> $\underline{B_\prec(T)}$ is a linear forest (max-degree $\le 2$,
> acyclic).

By the equivalence proved in `path_fas.md`, this is exactly the formal
Problem 4.4 path-FAS question.

## Reformulation in terms of FAS

The exact "FAS = back-arc set" slogan is false. The correct
normalization is:

- if $F$ is a FAS and $\prec$ is a topological order of $T-F$, then
  $B_\prec(T)\subseteq F$;
- conversely, $B_\prec(T)$ is a FAS for every order $\prec$.

Therefore LFO is equivalent to:

> Find a FAS $F \subseteq A(T)$ whose undirected graph is a linear
> forest.

Indeed, if such an $F$ exists, a topological order of $T-F$ has
back-arc set contained in $F$, hence a linear forest. Conversely, if
$B_\prec(T)$ is a linear forest, then it is itself a FAS.

This is also equivalent to formal Path-FAS: any linear forest can be
completed to a path in the complete underlying graph by adding arcs to
the FAS, and deleting extra arcs preserves acyclicity.

For tournaments, "$T \setminus F$ acyclic" is equivalent to "$F$ hits
every cyclic 3-cycle of $T$" (a tournament is transitive iff it has no
3-cycle).

## Necessary conditions and their tightness

### N1. Size bound

A linear forest on $n$ vertices has at most $n-1$ edges. So if LFO
holds, $f(T) \le n - 1$ where $f(T)$ is the minimum FAS size.

This is **not** sufficient: see N3 below.

### N2. Empirical onset at n = 7

The corrected exhaustive sweep `data/lfo_sweep_3_6_corrected.json`
confirms that all 74 non-isomorphic tournaments at $n \le 6$ have LFO.
The first explicit LFO NO examples found are at $n = 7$.

### N3. The Paley tournament Q(7) — size-bound NO

The Paley tournament Q(7) on 7 vertices is 3-regular and is LFO NO.
Reason: every ordering has $|B_\prec(T)| \ge 7$ back-arcs (since
$f(Q(7)) = 7$, the minimum across all orderings is 7), and a linear
forest on 7 vertices has at most $n - 1 = 6$ edges. So LFO NO is
forced by N1.

In particular, Q(7) is also forest-FAS NO and matching-FAS NO. It
violates the size bound by 1.

### N4. The FOREST_NOT_PATH_FAS witness — degree-and-cycle NO

The 7-vertex tournament `FOREST_NOT_PATH_FAS` from
`tests/test_path_fas.py` has $f(T) = 5 < 6$, so the size bound is not
the obstruction. Brute-force enumeration of all 5040 orderings of $T$
gives the following (max_degree, is_forest) distribution:

| max_deg | is_forest=True | is_forest=False |
|---:|---:|---:|
| 2 | 0 | **1** |
| 3 | 6 | 424 |
| 4 | 1 | 2491 |
| 5 | 0 | 1817 |
| 6 | 0 | 300 |

**Crucial fact.** Exactly *one* ordering achieves max-degree 2, and that
ordering's back-arc graph is a 7-cycle (a Hamiltonian cycle in the
undirected back-arc graph). The two natural relaxations of LFO are
both achievable, but never simultaneously:

- "back-arc graph is max-deg $\le 2$" is achieved by exactly 1 ordering
  — and it has a 7-cycle, not a linear forest.
- "back-arc graph is a forest" is achieved by 7 orderings — all with
  max-deg 3 or 4.

Removing the 7-cycle constraint by breaking one back-arc requires a
different ordering, which always pushes max-deg up to 3 or more. The
combinatorial coupling between max-degree and acyclicity is the
genuine obstruction in this example.

## The double-cyclic-triangle hub observation

In `FOREST_NOT_PATH_FAS`, vertex 3 has

- $T[N^+(3)] = T[\{0,1,2\}]$ = cyclic triangle $0 \to 2 \to 1 \to 0$;
- $T[N^-(3)] = T[\{4,5,6\}]$ = cyclic triangle $4 \to 5 \to 6 \to 4$.

**Hypothesis (falsified).** "If $T$ has a vertex $v$ such that
$T[N^+(v)]$ and $T[N^-(v)]$ are both cyclic 3-cycles, then $T$ has no
LFO."

Refutation: exhaustively constructing all 512 tournaments with this
hub structure (varying the 9 $N^+(v) \leftrightarrow N^-(v)$ arc
orientations), **460 of 512 admit a true LFO**. Only 52 are LFO NO.

The previously tempting degree-only relaxation is larger: 478 of 512
have some ordering whose back-arc graph has maximum degree at most 2.
Those extra 18 instances fail LFO because the degree-2 graph has an
undirected cycle. The forest-only relaxation is also larger: 496 of 512
have a forest-ordering. Among all 512 instances, 10 even admit a
matching-FAS.

So the double-cyclic-triangle hub is not sufficient. The
$N^+(v) \leftrightarrow N^-(v)$ cross-arcs interact non-locally with
the hub structure.

Among the 52 true LFO NO instances, the cross-arc bit-count
$|\{(x,y) : x \in N^+(v), y \in N^-(v), x \to y\}|$ lies in
$\{5, 6, 7, 8, 9\}$ with distribution

| bit-count | LFO NO count |
|---:|---:|
| 5 | 9 |
| 6 | 24 |
| 7 | 9 |
| 8 | 9 |
| 9 | 1 |

So the hub obstruction requires additional cross-arc structure, but it
is not captured by a single threshold on the number of $N^+\to N^-$
arcs.

## Exact n = 7 census

The full exact non-isomorphic census at $n=7$ is stored in
`data/lfo_full_n7.json`. It was generated by
`scripts/lfo_score_bucket.py --all-scores`, using the fact that
isomorphisms preserve score classes and therefore canonicalization only
has to permute vertices within equal-score blocks.

Across all 456 non-isomorphic tournaments on 7 vertices:

| total | LFO YES | LFO NO | size NO | combinatorial NO |
|---:|---:|---:|---:|---:|
| 456 | 436 | 20 | 2 | 18 |

The LFO NO instances occur in exactly seven score sequences:

| Score sequence | non-isomorphic total | LFO YES | LFO NO | size NO | combinatorial NO |
|---|---:|---:|---:|---:|---:|
| (1,2,3,3,3,4,5) | 47 | 46 | 1 | 0 | 1 |
| (1,2,3,3,4,4,4) | 37 | 36 | 1 | 0 | 1 |
| (2,2,2,3,3,4,5) | 37 | 36 | 1 | 0 | 1 |
| (2,2,2,3,4,4,4) | 22 | 21 | 1 | 0 | 1 |
| (2,2,3,3,3,4,4) | 47 | 42 | 5 | 0 | 5 |
| (2,3,3,3,3,3,4) | 15 | 7 | 8 | 0 | 8 |
| (3,3,3,3,3,3,3) | 3 | 0 | 3 | 2 | 1 |

So the exact census sharpens the random-sample picture:

- all size-bound NO instances at $n=7$ are regular;
- the near-regular bucket $(2,3,3,3,3,3,4)$ is the densest
  combinatorial boundary, with 8 NO out of 15;
- the bucket $(2,2,3,3,3,4,4)$ contributes the next-largest block,
  with 5 NO out of 47;
- four additional score sequences each contribute a single
  combinatorial NO.

The exact census also separates the two relaxations cleanly:

| property | non-isomorphic YES count |
|---|---:|
| matching-FAS | 95 |
| exact connected-path backarcs | 425 |
| formal Path-FAS / LFO | 436 |
| degree-only relaxation | 445 |
| forest-ordering relaxation | 450 |

Thus exact connected-path backarcs are too restrictive by 11
isomorphism classes, degree-only is too permissive by 9, and
forest-ordering is too permissive by 14.

### The 18 combinatorial n = 7 obstructions

The 18 combinatorial NO instances were analyzed separately in
`data/lfo_combinatorial_no_analysis.json`, generated by
`scripts/lfo_obstruction_analysis.py`.

Basic facts:

| invariant | value |
|---|---:|
| combinatorial NO instances | 18 |
| duality orbits | 15 |
| self-dual instances | 12 |
| vertex-minimal instances | 18 |

The vertex-minimality is expected after the corrected $n \le 6$
census, but it is still useful to record explicitly: every deletion of
one vertex from any of the 18 tournaments has LFO.

The 18 instances split by which relaxation succeeds:

| relaxation type | meaning | count |
|---|---|---:|
| coupling | degree-2 orderings exist and forest orderings exist, but never together | 7 |
| degree obstruction | forest orderings exist, but every forest ordering has max-degree at least 3 | 7 |
| cycle obstruction | max-degree-2 orderings exist, but every such ordering has a cycle | 2 |
| both fail | neither relaxation exists | 2 |

Other invariant distributions:

| invariant | distribution |
|---|---|
| cyclic 3-cycle count | 9:1, 10:2, 11:1, 12:5, 13:8, 14:1 |
| automorphism group size | 1:13, 3:3, 7:1, 9:1 |
| double-triangle hub count | 0:12, 1:6 |

Two conclusions are immediate.

First, the double-cyclic-triangle hub is not even necessary: 12 of the
18 exact combinatorial obstructions have no such hub.

Second, the hard part is not a single phenomenon. Seven instances are
genuine degree-vs-acyclicity coupling examples; seven are already
blocked at the degree-2 layer; two are blocked at the forest layer; and
two fail both relaxations.

Because LFO is hereditary under induced subtournaments, these 18
combinatorial obstructions, together with the two size-bound NO
instances, are exactly the order-7 minimal forbidden induced
subtournaments for LFO. They are not, however, the whole obstruction
theory.

## Order-7 obstructions do not explain all larger NOs

LFO heredity gives one sound test:

> If $T$ contains an induced subtournament with no LFO, then $T$ has no
> LFO.

So every tournament containing one of the 20 order-7 NO tournaments is
automatically NO. A tempting conjecture was that, at least near the
small boundary, the converse might hold: every larger NO would contain
one of these 20 order-7 obstructions.

This conjecture is false, and now false exactly at $n=8$.

The exact $n=8$ extension census
(`data/lfo_extend_census_n8.json`) was generated by
`scripts/lfo_extend_census.py`. It extends the 456 exact $n=7$
representatives in all $2^7$ ways, deduplicates by score-respecting
canonicalization, and obtains all 6880 non-isomorphic tournaments on 8
vertices.

The LFO decision in that census uses the pruned exact solver
`scripts/lfo_backtrack.py`: build an order from left to right, and when
a vertex $x$ is appended, add exactly the newly forced back-arcs
$x\to p$ to earlier prefix vertices $p$. A branch is dead as soon as
the partial back-arc graph has degree greater than 2 or an undirected
cycle.

Exact $n=8$ outcome:

| total | LFO YES | LFO NO | size NO | combinatorial NO |
|---:|---:|---:|---:|---:|
| 6880 | 5016 | 1864 | 66 | 1798 |

Order-7 obstruction containment among the 1864 NO instances:

| outcome | count |
|---|---:|
| NO containing an order-7 NO | 1292 |
| NO with no order-7 NO | 572 |

The 572 order-7-NO-free instances are exact order-8 minimal
obstructions. They split into 567 combinatorial NOs and 5 size-bound
NOs. So the order-7 obstruction list misses a large exact family at the
next size, not a few random freak cases.

### The 572 minimal n = 8 obstructions

The 572 exact order-8 minimal obstructions were analyzed in
`data/lfo_minimal8_analysis.json`, generated by
`scripts/lfo_minimal8_analysis.py`.

Basic compression:

| invariant | value |
|---|---:|
| minimal order-8 NO instances | 572 |
| duality orbits | 294 |
| self-dual instances | 16 |
| prime tournaments | 418 |
| tournaments with trivial automorphism group | 568 |

This is the most important negative signal in the computation. The
minimal obstruction set does not collapse under duality, modular
decomposition, or symmetry. It is large, mostly prime, and almost
entirely asymmetric.

The relaxation split is:

| relaxation type | meaning | count |
|---|---|---:|
| degree obstruction | forest orderings exist, but every forest ordering has max-degree at least 3 | 340 |
| coupling | degree-2 orderings exist and forest orderings exist, but never together | 189 |
| both fail | neither relaxation exists | 30 |
| cycle obstruction | max-degree-2 orderings exist, but every such ordering has a cycle | 13 |

Crossing this with the size-bound classification:

| kind | degree obstruction | coupling | cycle obstruction | both fail |
|---|---:|---:|---:|---:|
| combinatorial NO | 340 | 189 | 13 | 25 |
| size NO | 0 | 0 | 0 | 5 |

The minimum FAS distribution among these 572 minimal obstructions is:

| min FAS | count |
|---:|---:|
| 4 | 8 |
| 5 | 128 |
| 6 | 258 |
| 7 | 173 |
| 8 | 5 |

So most minimal obstructions are not close to the trivial size-bound
barrier $f(T)>n-1$. The size-bound accounts for only 5 of 572.

The top score buckets for minimal order-8 obstructions are:

| score sequence | count |
|---|---:|
| (2,3,3,3,4,4,4,5) | 134 |
| (2,2,3,3,4,4,5,5) | 61 |
| (2,2,3,4,4,4,4,5) | 55 |
| (2,3,3,3,3,4,5,5) | 55 |
| (1,3,3,4,4,4,4,5) | 38 |
| (2,3,3,3,3,4,4,6) | 38 |
| (1,3,3,3,4,4,5,5) | 25 |
| (2,2,3,3,4,4,4,6) | 25 |

Other distributions:

| invariant | distribution |
|---|---|
| cyclic 3-cycle count | 12:2, 13:10, 14:42, 15:80, 16:137, 17:124, 18:142, 19:32, 20:3 |
| automorphism group size | 1:568, 3:4 |
| non-trivial module count | 0:418, 1:139, 2:9, 3:6 |
| vertices whose in- and out-neighborhoods both contain a cyclic triangle | 0:222, 1:196, 2:89, 3:48, 4:15, 5:2 |

The module count is especially damning for a modular-decomposition
approach: 418 of 572 minimal obstructions are prime. Modules were the
right organizing principle for matching-FAS; they are mostly absent at
the path-FAS obstruction boundary.

### Exact n = 9 census

The exact order-9 representative set was generated by
`scripts/lfo_representatives.py`, using the refined tournament
canonicalizer in `scripts/tournament_canonical.py`. Extending the 6880
order-8 representatives in all $2^8$ ways and deduplicating gives
191536 non-isomorphic tournaments on 9 vertices, matching the standard
count.

The exact LFO census was then computed by
`scripts/lfo_census_from_reps.py`. The key speed-up is hereditary
filtering: before running the backtracking LFO solver, test whether the
order-9 tournament contains one of the 1864 exact order-8 NO
tournaments. If it does, it is automatically NO. This avoided the
backtracker on 118755 of the 124315 NO instances.

Exact $n=9$ outcome:

| total | LFO YES | LFO NO | size NO | combinatorial NO |
|---:|---:|---:|---:|---:|
| 191536 | 67221 | 124315 | 23960 | 100355 |

Order-8 obstruction containment among the 124315 NO instances:

| outcome | count |
|---|---:|
| NO containing an order-8 NO | 118755 |
| NO with no order-8 NO | 5560 |

Thus the obstruction boundary keeps growing: there are 5560 exact
order-9 minimal obstructions.

The compact minimal-order-9 summary is stored in
`data/lfo_minimal9_summary.json`, generated by
`scripts/lfo_minimal9_summary.py`.

| invariant | value |
|---|---:|
| minimal order-9 NO instances | 5560 |
| duality orbits | 2884 |
| self-dual instances | 208 |
| prime tournaments | 4303 |
| combinatorial minimal NO | 5448 |
| size-bound minimal NO | 112 |

The minimum FAS distribution among the 5560 minimal order-9
obstructions is:

| min FAS | count |
|---:|---:|
| 3 | 1 |
| 4 | 30 |
| 5 | 279 |
| 6 | 1266 |
| 7 | 2432 |
| 8 | 1440 |
| 9 | 111 |
| 10 | 1 |

Again the size-bound explanation is marginal: only 112 of 5560 minimal
order-9 obstructions are size-bound NOs.

The top minimal-order-9 score buckets are:

| score sequence | count |
|---|---:|
| (2,3,3,4,4,4,5,5,6) | 704 |
| (2,2,3,4,4,5,5,5,6) | 407 |
| (2,3,3,3,4,4,5,6,6) | 407 |
| (2,2,3,3,4,5,5,6,6) | 357 |
| (2,3,3,3,4,5,5,5,6) | 319 |
| (2,3,3,3,4,4,5,5,7) | 186 |
| (1,3,3,4,4,5,5,5,6) | 186 |
| (2,2,3,4,4,4,5,6,6) | 178 |

The structural compression remains poor:

| invariant | distribution |
|---|---|
| non-trivial module count | 0:4303, 1:1068, 2:141, 3:32, 4:15, 6:1 |
| vertices whose in- and out-neighborhoods both contain a cyclic triangle | 0:941, 1:1738, 2:1632, 3:947, 4:256, 5:46 |

So even after using all order-8 obstructions, order 9 contributes
thousands of new minimal obstructions, and most are still prime. The
finite-forbidden-list viewpoint is not just inconvenient; it is the
wrong lens for solving the problem.

The random forbidden-subtournament test
`scripts/lfo_forbidden7_test.py` is now mainly a smoke test for larger
orders. For a smaller random sample at $n=9$ with seed 20260521
(`data/lfo_forbidden7_random_n9.json`):

| random n=9 outcome | count |
|---|---:|
| LFO YES and order-7-NO-free | 8 |
| LFO NO containing an order-7 NO | 9 |
| LFO NO with no order-7 NO | 3 |
| LFO YES containing an order-7 NO | 0 |

The three order-7-NO-free NO instances at $n=9$ are also
combinatorial NOs. After the exact $n=8$ census was computed, each of
these three was found to contain an induced order-8 NO subtournament.

This kills the finite "forbid the order-7 list" strategy. Any real
solution must either find an infinite obstruction mechanism, give a
global optimization algorithm, or prove hardness.

## Random n = 7 sample

Corrected random sampling of 1500 labeled tournaments at $n = 7$ with
seed 20260521 (`data/lfo_random_n7_seed20260521.json`) gave:

| Score sequence | NO count | YES count |
|---|---:|---:|
| (2,3,3,3,3,3,4) | 26 | 23 |
| (2,2,3,3,3,4,4) | 21 | 162 |
| (1,2,3,3,3,4,5) | 5 | 156 |
| (1,2,3,3,4,4,4) | 2 | 147 |
| (3,3,3,3,3,3,3) | 2 | 0 |

**Empirical pattern.** The regular tournament $(3,3,3,3,3,3,3)$ is
LFO NO with high frequency (every sampled instance, though only 2
were sampled; consistent with N3 since the Paley tournament is the
canonical example). The near-regular sequence $(2,3,3,3,3,3,4)$
is almost evenly split in this sample.

Highly skewed score sequences yield occasional NO instances but YES
dominates.

## Refined classification of NO instances

Among the 456 non-isomorphic tournaments at $n=7$:

- 436 YES.
- 2 *size NO*: $f(T) > n - 1$.
- 18 *combinatorial NO*: $f(T) \le n - 1$ but no LFO.

Among the 6880 non-isomorphic tournaments at $n=8$:

- 5016 YES.
- 66 *size NO*.
- 1798 *combinatorial NO*.

Of the 1864 total NO instances at $n=8$, 1292 contain an induced
order-7 NO, while 572 do not. Those 572 are exact order-8 minimal
obstructions: 567 combinatorial and 5 size-bound.

Among the 191536 non-isomorphic tournaments at $n=9$:

- 67221 YES.
- 23960 *size NO*.
- 100355 *combinatorial NO*.

Of the 124315 total NO instances at $n=9$, 118755 contain an induced
order-8 NO, while 5560 do not. Those 5560 are exact order-9 minimal
obstructions: 5448 combinatorial and 112 size-bound.

Among 1500 random labeled tournaments at $n = 7$:

- 1444 YES.
- 1 *size NO*: $f(T) > n - 1$. The Paley-type obstruction.
- 55 *combinatorial NO*: $f(T) \le n - 1$ but no LFO. The
  FOREST_NOT_PATH_FAS-type obstruction.

The labeled random sample is biased by automorphism-class sizes, but it
agrees with the exact census on the qualitative point: combinatorial NO
instances dominate size-bound NO instances. They are the algorithmically
interesting case.

## Why the matching 2-SAT does not extend

For matching-FAS the necessary and sufficient conditions are

- (N) every back-arc is no-shortcut;
- (C) every cyclic 3-cycle contributes exactly one back-arc.

The proof relied on: with max-degree $\le 1$, at most one back-arc lies
in any 3-vertex subtournament. In the path case (max-deg $\le 2$), this
is no longer true. The per-triangle flip table now reads:

For a cyclic triangle of $T$:
- 0 flipped: still cyclic, forbidden.
- 1 or 2 flipped: transitive, allowed.
- 3 flipped: cyclic, forbidden, and also impossible because the
  flipped triple would form a triangle in the back-arc graph.

For a transitive triangle $a \succ b \succ c$ of $T$:
- 0 or 1 short-arc flip: transitive, allowed.
- 1 long-arc flip: cyclic, forbidden.
- 2 short flips: cyclic, forbidden.
- 1 long flip + 1 short flip: transitive, allowed.

The new permissible patterns are "1 long + 1 short" in transitive
triangles, and "2 flips" in cyclic triangles. These admit V-shaped
back-arc configurations at a vertex, which the matching's per-vertex
degree-$\le 1$ constraint ruled out.

In 2-SAT terms, the transitive-triangle constraint is no longer a
single "long arc forbidden" predicate. It becomes: "if the long arc is
selected, then exactly one of the two short arcs is also selected".
This is a 3-variable constraint, not 2-SAT-expressible in general.

A separate global constraint — the back-arc graph is acyclic — has to
be enforced; with max-degree $\le 2$ alone, undirected cycles are
possible. The FOREST_NOT_PATH_FAS example shows this is a genuine
obstruction: it has a max-deg-2 ordering and several forest
orderings, but no ordering is both.

## Score-window attack

The strongest algorithmic observation found so far is a global
position constraint.

For any order $\prec$ and vertex $v$, the back-neighbors of $v$ are
exactly

$$
E_\prec(v)\triangle N^-(v),
$$

where $E_\prec(v)$ is the set of earlier vertices. Hence

$$
\deg_{B_\prec}(v)\ge |i_\prec(v)-d^-(v)|.
$$

Every LFO has maximum backdegree at most 2, so every vertex must lie in
the five-position score window

$$
i_\prec(v)\in[d^-(v)-2,d^-(v)+2].
$$

This gives a sharply pruned exact solver:
[`../scripts/lfo_score_window.py`](../scripts/lfo_score_window.py).
The solver builds the order left to right, requires the next vertex to
lie in its score window, checks interval-Hall feasibility for the
unplaced vertices, and prunes using forced future backedges from
unplaced vertices to the fixed prefix.

Validation so far:

| test set | records | disagreements | worst nodes |
|---|---:|---:|---:|
| exact non-isomorphic $n\le 6$ | 74 | 0 | 46 |
| full exact $n=7$ census | 456 | 0 | 120 |
| exact known n=8 NO records | 1864 | 0 | 163 |
| sampled exact n=9 census slice | 1916 | 0 | 237 |

The old backtracker needed 3070 nodes on the worst n=8 NO examples
tested here; the score-window solver needs 163. This is not merely a
speed tweak. It identifies the likely route to a polynomial algorithm:
the active score-window band is bounded by 9 after Hall pruning, so
the next vertex is chosen from a constant-size set.

The missing proof is the long-range state-compression step. The active
band is bounded, but the number of already-placed vertices with
obligations to far-future vertices is not. The transitive tournament
with a reversed matching of size $m$ is an LFO-YES instance whose
identity-order backedge graph is that matching; all score displacements
are $\pm1$, but the middle cut has $m$ crossing backedges. Thus a DP
that remembers only active score-window vertices is invalid.

The refined target is to quotient-compress the expired pending part:
remember enough about long-range degree obligations and component
connectivity to detect future degree and cycle violations, without
listing all crossing edges. A small 7-vertex probe also shows that
component connectivity cannot be dropped: two partial states can have
the same placed set and the same current degree vector but different
component partitions and different extendability.
That probe is repeatable by a cut-isolated sum construction, so the
connectivity issue can occur independently across many components; it
is not a one-off small-order pathology. For $k$ copies, the construction
gives $2^k$ partial states with the same placed set and the same degree
vector, but pairwise distinct component partitions; in the tested
family, exactly the all-good pattern extends.
Simple quotient signatures have now been tested against this family:
degree-only, component-count, component-size multiset, and
low-degree-set-plus-component-count all collapse extendable and
non-extendable states into the same bucket. Full component partition is
the first tested signature that separates them.

A more promising reformulation is now recorded in
[`score_window.md`](score_window.md): split pairs into **forced** pairs
with disjoint score windows and **flexible** pairs with overlapping
score windows. Every LFO must contain all forced backedges, so a
non-linear-forest forced graph is an immediate NO certificate. The
remaining choices live in the interval overlap graph of the score
windows, whose clique number is at most 9 after Hall feasibility. Thus
the current positive target is: fixed forced linear forest plus
bounded-clique interval choices.

The observed score-window search growth remains small on existing data.
Using exact all-record data through $n=7$, exact n=8 NO records, and a
stride-500 n=9 sample, the mixed maximum node counts are
$5,7,10,46,120,163,169$ for $n=3,\ldots,9$. A descriptive log-log fit
to the maxima gives exponent about $3.78$; a fit to p95 nodes gives
about $2.88$. This is not asymptotic evidence, because the n=8 and n=9
rows are not the same population as the exact small rows, but it is
strong evidence that the score-window pruning is attacking the right
state space.

A labeled random $n=10$ probe strengthens this empirical picture:
2000 uniform random tournaments, 205 LFO YES, 1022 initial Hall
failures, max 266 score-window nodes, p95 63, median 0. This lands on
the same small-node trend.

Skew-score probes using transitive tournaments with independent arc
reversal probability $p$ show where forced/flexible becomes active. The
mean forced-backedge counts for $n=12,16,20,24$ and
$p=0.02,0.05,0.10,0.20$ are:

| n | p=0.02 | p=0.05 | p=0.10 | p=0.20 |
|---:|---:|---:|---:|---:|
| 12 | 0.28 | 0.765 | 0.995 | 1.11 |
| 16 | 0.955 | 2.16 | 3.35 | 4.555 |
| 20 | 1.84 | 4.145 | 7.45 | 11.595 |
| 24 | 2.89 | 7.18 | 13.26 | 21.68 |

So the forced scaffold is not visible in the tiny exact censuses, but
it becomes measurable on larger skew-score instances. The hard search
regime in this model is light noise, around $p=0.02$ to $0.05$: Hall
usually passes and occasional instances are much harder than the
uniform random samples.

The forced/flexible split has also been implemented as an exact solver:
preload the forced graph and search only over flexible overlapping
windows. It agrees with the score-window solver on all exact
non-isomorphic tournaments through $n=7$. On a 50-sample $n=24$
light-noise comparison it improves most instances and cuts p95 in the
$p=0.02$ group from 2266 to 1137 nodes, but rare spikes remain. Thus
preloading forced edges is the right normalization for the DP attempt,
not the final algorithm.

The naive interval-bag DP after forced/flexible normalization has been
falsified. A state containing only the active score-window vertices,
placed-active subset, active degrees, and component partition restricted
to active vertices has mixed extendability already on the 7-vertex
component witness. The missing datum is latent connectivity through
forgotten vertices outside the active bag. Any polynomial DP must
quotient this latent connectivity, not merely use the active interval
bag.

The next refinement is now precise. At a cut $i$, an expired prefix
vertex can still be touched by a future **flexible** backedge only if
it is beaten by an unplaced active vertex. If $p$ is expired and $y$ is
not yet active, then $h_p<i<\ell_y$, so the pair $\{p,y\}$ has
disjoint score windows and is already part of the forced scaffold. In
any extendable branch each unplaced active vertex has at most two such
old ports, and there are at most nine active vertices after Hall
pruning. Thus the old-prefix ports relevant to future flexible choices
are bounded by 18, and the active-plus-visible-old interface is bounded
by 27. `ff_signature_probe.py` implements this visible-latent
signature. It separates the known active-bag collision and no
mixed-extendability collision was found in the exact $n=7$ census to
depth 5. The naive child-signature induction is false even on the
pruned state space: a 12-vertex skew witness has two
visible-latent-identical prefixes at depth 5 whose legal child
transition profiles differ. That same witness still has no
mixed-extendability visible class, so the remaining target is direct
extension-equivalence, not one-step bisimulation. A stronger
same-suffix-transfer statement is also false: a 10-vertex skew witness
has two visible-equivalent extendable prefixes where suffix
`(5,6,7,9,8)` works from one prefix and closes a hidden cycle from the
other, while `(5,6,7,8,9)` works from both. Thus a proof must allow
different completing suffixes. Later skew \(n=12\) probes sharpened
this substantially: first-failing-vertex left moves are insufficient,
one-block right moves are insufficient, and visible-latent extension-
equivalence itself is false. The proof draft
[`exchange_proof_draft.md`](exchange_proof_draft.md) now records the
counterexample: two FF-pruned same-prefix-set states have identical
visible-latent signatures, but one is extendable and the other is not.
Sleeping-block and wake-1 signatures separate this collision. The next
positive target is therefore a bounded refinement of visible-latent,
not another repair lemma for the same state.

This is the current positive proof target, not the final theorem. The
remaining gap is dormant forced-component propagation: a forced
linear-forest component can cross a cut without exposing a visible old
port, but earlier flexible choices may have merged its identity with
another component. A polynomial proof has to quotient those dormant
forced-component identities, or a hardness proof has to exploit them.

The first bounded repair, finite-horizon wake tracking, is not enough
for a one-step induction. A wake-$h$ signature records vertices whose
windows open within the next $h$ cuts and the old prefix ports they can
already hit. The base wake-chain witness defeats horizon 1; inserting
transitive padding before the delayed dormant vertex shifts the same
obstruction one cut later. Horizons 1-4 are pinned: same horizon-$h$
signature, different horizon-$h$ child transition profiles, separated
by horizon $h+1$. This points to an outward-shifting wake obstruction,
not a finite-lookahead repair.

See [`score_window.md`](score_window.md) for the lemma, instrumentation
tables, the reversed-matching obstruction, and the proposed compressed
DP target.

## Candidate algorithms tried and abandoned

### A1. "Min FAS is a linear forest" check

If $T$ has min FAS $\le n-1$, check whether *some* minimum FAS is a
linear forest. If yes, LFO YES.

Falsified by FOREST_NOT_PATH_FAS: min FAS = 5 (achieved by 2
orderings), but both min FAS orderings have max-degree 3, not 2. And
no larger forest-ordering achieves max-deg $\le 2$ either.

### A2. Matching 2-SAT with augmented triangle clauses

Extend the matching 2-SAT to encode "exactly one or two arcs per
cyclic triangle." Falsified by the 3-variable nature of the
transitive-triangle constraint (see above).

### A3. Min-FAS-parametrized subexponential algorithm

FAS in tournaments is solvable in $O^*(2^{O(\sqrt{k})})$ where $k$ is
the FAS size. With $k \le n-1$ (LFO bound), this is
$O^*(2^{O(\sqrt{n})})$ — subexponential but not polynomial. Even then,
enumerating all FASes of size $\le k$ is exponential, so we cannot
just brute-force-check all of them for linear-forest structure.

## Open problem

> **Is LFO in P or is it NP-complete?**

The known reductions both leave LFO open: AAL's NP-hardness uses
arbitrary forests (degree unbounded), and the matching 2-SAT
reduction does not transfer. The empirical signal is mixed:

- The first NO instance is at $n = 7$, very late.
- 436 of 456 non-isomorphic tournaments at $n=7$ are LFO YES.
- NO instances are concentrated near regular score sequences.
- The combinatorial structure of NO instances does not match any
  simple "forbidden subtournament" pattern we identified.

AAL-style hardness has now been attacked directly and is blocked at the
local-composition level. The first pass is recorded in
[`hardness_route.md`](hardness_route.md). Direct reuse of AAL fails:
their rigid Figure 1 block has a unique forest-ordering whose backedge
tree has maximum degree 4. An anchor-safe 9-vertex rigid block with a
unique path backedge graph has been found and exhaustively certified.
A separate 7-vertex gadget has exactly two LFO states and switches
which of two port pairs is exposed as path endpoints. The remaining
obstacle is external wiring: inactive ports in that first two-state
block do not all have spare degree for forced back-arc matchings;
exhausting all one- and two-auxiliary extensions of that block does not
repair this; and the direct asymmetric-wiring search with one or two
external vertices gives no strict compositional wiring.

That failure does not prove polynomiality, but it changes the best next
target. The current leading direction is the score-window dynamic
programming attempt described above: compress the exact
`lfo_score_window.py` search state. The naive active-frontier DP is now
known to be insufficient because of the reversed-matching family; the
visible-latent locality lemma bounds the old ports relevant to future
flexible choices, and the real remaining target is a quotient of
dormant forced-component identities.

## Files

- [`scripts/lfo_sweep.py`](../scripts/lfo_sweep.py) — exhaustive LFO
  sweep over non-isomorphic tournaments. Bottleneck: `canonical_key`
  is $O(n!)$ per tournament, so $n = 7$ is impractical without
  smarter isomorphism rejection. **A 1-hour run at $n = 3..7$
  timed out at $n = 7$.** The corrected exhaustive output for
  $n \le 6$ is `data/lfo_sweep_3_6_corrected.json`; the corrected
  random-sample data for $n=7$ is
  `data/lfo_random_n7_seed20260521.json`.
  Rewriting the sweep with score-sequence bucketing is a follow-up.
- [`scripts/analyze_obstruction.py`](../scripts/analyze_obstruction.py)
  — per-tournament analysis: min FAS, max-deg distribution, double-
  triangle hubs.
- [`scripts/test_double_triangle_obstruction.py`](../scripts/test_double_triangle_obstruction.py)
  — 512-instance test of the falsified double-triangle hypothesis; output
  is stored in `data/double_triangle_lfo_corrected.json`.
- [`scripts/lfo_random_sample.py`](../scripts/lfo_random_sample.py) —
  corrected true-LFO random sampler that separates size-bound NO from
  combinatorial NO.
- [`scripts/lfo_score_bucket.py`](../scripts/lfo_score_bucket.py) —
  exact non-isomorphic enumeration inside selected score-sequence
  buckets, or all score buckets with `--all-scores`, using
  score-respecting canonicalization. Full $n=7$ output is stored in
  `data/lfo_full_n7.json`; the earlier three-bucket output is stored in
  `data/lfo_score_buckets_n7.json`.
- [`scripts/lfo_backtrack.py`](../scripts/lfo_backtrack.py) —
  pruned exact LFO solver used for the $n=8$ and $n=9$ censuses.
- [`scripts/lfo_score_window.py`](../scripts/lfo_score_window.py) —
  score-window exact solver using the $|i_\prec(v)-d^-(v)|\le 2$
  lemma, interval-Hall pruning, and forced-future degree/cycle pruning.
- [`scripts/lfo_forced_flexible.py`](../scripts/lfo_forced_flexible.py)
  — exact forced/flexible solver: preload forced backedges, then search
  only over overlapping-window choices.
- [`scripts/ff_signature_probe.py`](../scripts/ff_signature_probe.py)
  — active-bag and visible-latent signature collision search for the
  forced/flexible DP attempt.
- [`scripts/wake_signature_probe.py`](../scripts/wake_signature_probe.py)
  — wake-horizon signature and one-step transition-profile probes for
  the forced/flexible DP attempt, including padded finite-horizon
  counterexamples.
- [`scripts/exchange_repair_probe.py`](../scripts/exchange_repair_probe.py)
  — suffix-transfer failure detector and repair probe for the
  visible-latent proof attempt. It now includes left moves, right-block
  moves, adjacent internal swaps, and the skew \(n=12\) counterexample
  showing visible-latent extension-equivalence is false.
- [`scripts/score_window_growth.py`](../scripts/score_window_growth.py)
  — descriptive search-node growth summaries and log/log-log fits.
- [`scripts/score_window_random_probe.py`](../scripts/score_window_random_probe.py)
  — labeled random n=10 growth probe and skew-score forced/flexible
  experiments.
- [`scripts/score_window_forced.py`](../scripts/score_window_forced.py)
  — forced/flexible pair decomposition: disjoint score-window pairs give
  forced backedges; overlapping-window pairs are the local choices.
- [`scripts/score_window_dp_obstruction.py`](../scripts/score_window_dp_obstruction.py)
  — reversed-matching family showing that bounded active score windows
  do not bound the number of crossing backedges.
- [`scripts/pending_state_probe.py`](../scripts/pending_state_probe.py)
  — searches for partial states proving that component connectivity
  cannot be compressed down to placed set plus degree vector.
- [`scripts/tournament_canonical.py`](../scripts/tournament_canonical.py)
  — dependency-free tournament canonicalizer using
  individualization/refinement; needed for regular order-9 tournaments.
- [`scripts/lfo_representatives.py`](../scripts/lfo_representatives.py)
  — compact JSONL representative generator. It produces
  `data/lfo_reps_n8.jsonl` and `data/lfo_reps_n9.jsonl`.
- [`scripts/lfo_extend_census.py`](../scripts/lfo_extend_census.py) —
  exact $n=8$ census by extending the exact $n=7$ representatives and
  deduplicating; output is `data/lfo_extend_census_n8.json`.
- [`scripts/lfo_census_from_reps.py`](../scripts/lfo_census_from_reps.py)
  — resumable exact census from compact representatives, with hereditary
  lower-order NO filtering; output is `data/lfo_census_n9_results.jsonl`
  and `data/lfo_census_n9_results_summary.json`.
- [`scripts/lfo_obstruction_analysis.py`](../scripts/lfo_obstruction_analysis.py)
  — duality, vertex-deletion, relaxation-type, and small-invariant
  analysis of the 18 exact combinatorial $n=7$ NO instances; output is
  `data/lfo_combinatorial_no_analysis.json`.
- [`scripts/lfo_minimal9_summary.py`](../scripts/lfo_minimal9_summary.py)
  — compact structural summary of the 5560 exact order-9 minimal
  obstructions; output is `data/lfo_minimal9_summary.json`.
- [`scripts/lfo_forbidden7_test.py`](../scripts/lfo_forbidden7_test.py)
  — random test of whether larger LFO NO instances are explained by
  induced order-7 NO subtournaments; outputs are
  `data/lfo_forbidden7_random_n8.json` and
  `data/lfo_forbidden7_random_n9.json`.
- [`scripts/lfo_no_analysis.py`](../scripts/lfo_no_analysis.py) —
  post-sweep analysis of NO instances (depends on the sweep JSON;
  use random sampling if the sweep has not completed).
