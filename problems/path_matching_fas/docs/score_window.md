# Score-window attack on LFO

This note records the current algorithmic attack on the Path-FAS /
linear-forest ordering problem. It is not a polynomial-time algorithm,
but it is the first pruning principle found so far that gives strong
global leverage rather than another failed local gadget search.

## Lemma: every LFO has bounded score displacement

Let $T$ be a tournament, let $\prec$ be an order, and put vertices in
0-indexed positions. For a vertex $v$, write

- $i_\prec(v)$ for its position;
- $d^-(v)$ for its indegree in $T$;
- $E_\prec(v)$ for the set of vertices earlier than $v$.

The back-neighbors of $v$ in the back-arc graph are exactly

$$
E_\prec(v)\triangle N^-(v).
$$

Indeed:

- if $u\prec v$ and $v\to u$, then $u$ is an earlier out-neighbor of
  $v$, hence a back-neighbor;
- if $v\prec u$ and $u\to v$, then $u$ is a later in-neighbor of $v$,
  hence also a back-neighbor.

The earlier vertices have size $i_\prec(v)$, and $N^-(v)$ has size
$d^-(v)$. Therefore

$$
\deg_{B_\prec}(v)
= |E_\prec(v)\triangle N^-(v)|
\ge \bigl|\,i_\prec(v)-d^-(v)\,\bigr|.
$$

If $B_\prec(T)$ is a linear forest, then every backdegree is at most
2. Hence every vertex must satisfy

$$
\boxed{\bigl|\,i_\prec(v)-d^-(v)\,\bigr|\le 2.}
$$

So each vertex $v$ has only five possible positions:

$$
i_\prec(v)\in [d^-(v)-2,d^-(v)+2]\cap\{0,\ldots,n-1\}.
$$

This is a very severe constraint near the obstruction boundary. It is
also independent of modular decomposition: it applies equally to prime
tournaments, where the matching-FAS module strategy has nothing to
grab.

The use of indegree as a ranking proxy is standard in the feedback-arc
set/rank-aggregation literature; for example, Coppersmith, Fleischer,
and Rurda analyze ordering weighted tournaments by weighted indegree in
ACM Transactions on Algorithms 6(3), Article 55 (2010),
doi: [`10.1145/1798596.1798608`](https://doi.org/10.1145/1798596.1798608).
The point here is narrower: an LFO certificate with maximum backdegree
2 forces a radius-2 displacement window around indegree.

## Consequence: Hall-feasible active windows are bounded

For radius $2$, each score window has width at most $5$. Suppose the
window assignment itself is feasible: the vertices can be injectively
assigned to positions inside their windows. Equivalently for interval
domains, Hall's condition holds on every interval of positions.

Then at any position $p$, at most $9$ windows can be active.

Reason: if a width-$5$ interval $[a,b]$ contains $p$, then
$a\ge p-4$ and $b\le p+4$. Thus all windows active at $p$ are contained
in the position interval $[p-4,p+4]$, which has at most $9$ positions.
Hall's condition forbids more than $9$ vertices whose windows are all
contained in that interval.

So the score-window band really is bounded after Hall pruning. The
constant is $4r+1$ for radius $r$, hence $9$ in the LFO case.

## Degree quota table

The displacement also determines the possible split between past and
future back-neighbors.

Let

- $\delta=i_\prec(v)-d^-(v)$;
- $b(v)$ be the number of earlier out-neighbors of $v$;
- $f(v)$ be the number of later in-neighbors of $v$.

Then $b(v)$ and $f(v)$ are exactly the past and future back-neighbors
of $v$, and

$$
\delta=b(v)-f(v),\qquad \deg_{B_\prec}(v)=b(v)+f(v).
$$

Under the degree-$2$ condition, the only possibilities are:

| $\delta$ | earlier out-neighbors $b$ | later in-neighbors $f$ | backdegree |
|---:|---:|---:|---:|
| -2 | 0 | 2 | 2 |
| -1 | 0 | 1 | 1 |
| 0 | 0 or 1 | 0 or 1, same as $b$ | 0 or 2 |
| 1 | 1 | 0 | 1 |
| 2 | 2 | 0 | 2 |

This table is more useful than the raw inequality. It says exactly how
many already-placed backedges a vertex is allowed to have when it is
put at a given displacement, and exactly how many future backedges it
still requires.

## Exact solver

[`../scripts/lfo_score_window.py`](../scripts/lfo_score_window.py)
implements an exact branch-and-prune solver using the score windows.
It builds the order left to right.

At position $i$, a candidate vertex must have $i$ in its score window.
Before branching, the solver also checks:

1. **Interval Hall feasibility.** The remaining vertices must be
   assignable injectively to the remaining positions respecting their
   score windows. Since all domains are intervals, this can be checked
   by testing position intervals.
2. **Forced future degree.** Once a prefix is fixed, every remaining
   vertex $x$ with $x\to p$ for a placed vertex $p$ will necessarily
   create the future backedge $xp$. If these unavoidable future
   backedges already force degree $>2$, the branch is dead.
3. **Forced future cycle.** If a remaining vertex has two unavoidable
   future backedges to vertices already in the same current backedge
   component, then adding that vertex later will close an undirected
   cycle. The branch is dead.

The solver is exact: a returned order is verified by the independent
back-arc verifier, and a rejected branch is rejected only by necessary
conditions.

## Validation

The unit tests in
[`../tests/test_score_window.py`](../tests/test_score_window.py)
check the solver against brute force on all non-isomorphic tournaments
through order 5, and on pinned YES/NO separating examples.

Additional one-off instrumentation produced these checks.

### Exact non-isomorphic tournaments through n = 6

| n | total | LFO YES | max search nodes | disagreements |
|---:|---:|---:|---:|---:|
| 3 | 2 | 2 | 5 | 0 |
| 4 | 4 | 4 | 7 | 0 |
| 5 | 12 | 12 | 10 | 0 |
| 6 | 56 | 56 | 46 | 0 |

### Full exact n = 7 census

The solver was checked against all 456 non-isomorphic tournaments in
`../data/lfo_full_n7.json`.

| class | count | max nodes | median nodes | mean nodes |
|---|---:|---:|---:|---:|
| LFO YES | 436 | 79 | 12.0 | 16.82 |
| combinatorial NO | 18 | 120 | 61.0 | 58.39 |
| size NO | 2 | 0 | 0.0 | 0.0 |

There were zero disagreements with the existing census. The two
size-bound NO instances are rejected immediately by the initial Hall
test.

### Exact n = 8 NO records

The solver was checked against the 1864 known NO records in
`../data/lfo_extend_census_n8.json`.

| class | count | max nodes | median nodes | mean nodes |
|---|---:|---:|---:|---:|
| combinatorial NO | 1798 | 163 | 37.0 | 39.78 |
| size NO | 66 | 0 | 0.0 | 0.0 |

There were zero disagreements. The worst n=8 NO records required only
163 recursive nodes under the score-window solver; the old exact
backtracker needed 3070 nodes on the same worst examples.

### Sampled n = 9 census records

Sampling every hundredth representative/result pair from the exact
order-9 census gave 1916 checked tournaments.

| class | count | max nodes | median nodes | mean nodes |
|---|---:|---:|---:|---:|
| LFO YES | 660 | 139 | 19.0 | 24.67 |
| combinatorial NO | 1022 | 237 | 22.0 | 29.83 |
| size NO | 234 | 41 | 0.0 | 2.21 |

Again there were zero disagreements, and every returned YES order was
verified as a genuine linear-forest ordering.

### Empirical node growth

[`../scripts/score_window_growth.py`](../scripts/score_window_growth.py)
collects score-window search-node statistics and fits two descriptive
regressions. With the current data settings

```bash
python3 scripts/score_window_growth.py --n9-stride 500
```

the mixed summary is:

| n | source | records | max nodes | p95 nodes | median nodes |
|---:|---|---:|---:|---:|---:|
| 3 | exact all non-isomorphic | 2 | 5 | 5 | 4.5 |
| 4 | exact all non-isomorphic | 4 | 7 | 7 | 5.5 |
| 5 | exact all non-isomorphic | 12 | 10 | 10 | 7.0 |
| 6 | exact all non-isomorphic | 56 | 46 | 15 | 9.0 |
| 7 | exact all non-isomorphic | 456 | 120 | 48 | 12.0 |
| 8 | exact NO records only | 1864 | 163 | 94 | 36.0 |
| 9 | stride-500 sample | 384 | 169 | 76 | 18.0 |

The regressions are deliberately labeled descriptive, not asymptotic:
$n=8$ is NO-records only and $n=9$ is a stride sample.

| metric | log(nodes) vs n slope | R^2 | log(nodes) vs log(n) exponent | R^2 |
|---|---:|---:|---:|---:|
| max | 0.690785 | 0.929154 | 3.783468 | 0.917974 |
| p95 | 0.533117 | 0.934676 | 2.879693 | 0.898166 |

This is compatible with polynomial growth on the tested range, but the
range is far too small to infer an asymptotic law. The useful takeaway
is operational: the score-window pruning has reduced the observed
search to hundreds of nodes where brute force is already factorial.

An additional labeled random probe at $n=10$ is stored in
`../data/score_window_random_n10_seed20260522.json`, generated by

```bash
python3 scripts/score_window_random_probe.py \
  --mode uniform --ns 10 --samples 2000 --seed 20260522
```

It gives:

| n | model | samples | LFO YES | Hall failures | max nodes | p95 nodes | median nodes |
|---:|---|---:|---:|---:|---:|---:|---:|
| 10 | uniform labeled random | 2000 | 205 | 1022 | 266 | 63 | 0 |

The median is zero because more than half the random $n=10$ sample is
rejected immediately by the initial interval-Hall test. Among the
instances that pass Hall, the search is still small: the maximum over
the whole sample is 266 nodes.

## What this proves, and what it does not

This proves a strong necessary positional theorem and gives a much
better exact solver. It does **not** prove LFO is in P.

The remaining difficulty is that the state of the back-arc graph is
not determined by the score windows alone. The solver still tracks
partial degrees and connected components of the current backedge
forest. In the worst case, that is not yet compressed into a
polynomially bounded dynamic program.

The striking empirical fact is that the active score-window frontier is
tiny in all tested instances: the maximum candidate frontier observed
in the n=7 full census, the n=8 NO census, and the n=9 sample is 5.
The Hall argument above gives a theorem-level bound of 9 on active
windows in any feasible score-window assignment. However, this still
does not give a polynomial algorithm by itself: long-range backedges can
cross far beyond the active score band.

## Why the naive bounded-frontier DP fails

There is an infinite LFO-YES family with bounded active score windows
but unbounded crossing backedges.

For $m\ge 1$, take the transitive tournament on
$0,1,\ldots,2m-1$ in the identity order and reverse exactly the
matching edges

$$
(0,m),(1,m+1),\ldots,(m-1,2m-1).
$$

Equivalently, in the resulting tournament the back-arcs of the identity
order are exactly

$$
(m,0),(m+1,1),\ldots,(2m-1,m-1).
$$

Thus the identity order is not merely an LFO; its back-arc graph is a
matching. Every vertex has score displacement exactly $1$ in absolute
value:

- vertices $0,\ldots,m-1$ have $\delta=-1$ and one future back-neighbor;
- vertices $m,\ldots,2m-1$ have $\delta=1$ and one past back-neighbor.

The score-window active set is Hall-feasible and bounded by 9. But at
the middle cut after the first $m$ vertices, all $m$ backedges cross the
cut. The number of already-placed vertices with obligations to
far-future vertices is therefore unbounded.

This family is generated and tested by
[`../scripts/score_window_dp_obstruction.py`](../scripts/score_window_dp_obstruction.py)
and
[`../tests/test_score_window_dp_obstruction.py`](../tests/test_score_window_dp_obstruction.py).

So a DP state consisting only of the active score-window vertices is
dead. It forgets old vertices whose score windows have expired but which
still have future backedge obligations. The state must also summarize
long-range pending components.

## Component connectivity is load-bearing

A second probe rules out an even coarser compression: keeping only the
placed set and the current degree vector.

[`../scripts/pending_state_probe.py`](../scripts/pending_state_probe.py)
searches for two valid partial construction states with the same

$$
(\text{placed vertex set},\ \text{current degree vector})
$$

but different partial backedge component partitions and different
extendability to a full LFO.

It finds such a witness already on 7 vertices. In the tournament

```text
[0,0,0,0,0,0,0]
[1,0,0,0,0,0,0]
[1,1,0,0,0,0,1]
[1,1,1,0,0,0,0]
[1,1,1,1,0,0,0]
[1,1,1,1,1,0,0]
[1,1,0,1,1,1,0]
```

the two prefixes

```text
5,2,6,3
6,3,5,2
```

place the same vertex set $\{2,3,5,6\}$ and give the same current
degree vector

```text
(0,0,1,1,0,1,1).
```

But their component partitions differ:

```text
{2,3}, {5,6}       not extendable
{2,6}, {3,5}       extendable
```

So component connectivity is not cosmetic. It can change the answer
even when the placed vertices and all current degrees are identical.

The witness also repeats independently. The script constructs a
cut-isolated sum of several copies: all cross-copy arcs are oriented
forward with respect to the cut order, so no cross-copy backedges are
introduced by the intended prefix/suffix decomposition. Each copy can
be put in its good or bad local component pairing. For example, with
three copies:

```text
good, good, good       extendable
good, bad,  good       not extendable
bad,  good, good       not extendable
```

These states have the same global placed set and the same global degree
vector; only the component pairings differ. This does not prove that no
polynomial compression exists, but it kills the next naive hope: the
expired component information is not a bounded-size accident. The same
connectivity bit can be planted repeatedly.

More explicitly, for $k$ cut-isolated copies there are $2^k$ partial
states with:

- the same placed vertex set;
- the same current degree vector;
- pairwise distinct component partitions;
- exactly one extendable pattern, namely all copies in the good local
  pairing.

For $k=4$, the script reports:

```json
{
  "states": 16,
  "coarse_key_count": 1,
  "component_partition_count": 16,
  "extendable_count": 1
}
```

So the quotient problem has an exponential entropy source. A successful
polynomial DP cannot merely argue that component information is "small
in practice"; it needs a theorem that many of these pairings are
equivalent under all future tests, or it needs a different global
formulation.

The script also tests several candidate component-state quotients on
this entropy family. For $k=4$ copies:

```json
{
  "degree_only": "unsound",
  "component_count": "unsound",
  "component_size_multiset": "unsound",
  "low_degree_set_and_component_count": "unsound",
  "component_partition": "sound on this family"
}
```

The first four signatures each put all 16 states in one bucket, mixing
extendable and non-extendable states. Only the full component partition
separates them. This does not rule out a subtler quotient, but it says
exactly where the next attempted compression has to improve.

## Forced/flexible decomposition

There is, however, one positive structural move.

Given score windows $I_v=[d^-(v)-2,d^-(v)+2]$, an unordered pair
$\{u,v\}$ is of one of two types.

1. **Forced pair.** The windows are disjoint. If
   $\max I_u < \min I_v$, then every score-respecting order has
   $u\prec v$. The pair contributes a forced backedge exactly when
   $v\to u$ in $T$.
2. **Flexible pair.** The windows overlap. The relative order of $u$
   and $v$ is not fixed by the score-window condition.

This gives a necessary decomposition:

$$
B_\prec(T)=B_{\mathrm{forced}}\cup B_{\mathrm{flex}}(\prec).
$$

Every LFO order must contain all forced backedges. Therefore:

> If the forced backedge graph is not a linear forest, then $T$ is LFO
> NO.

The flexible-pair graph is an interval overlap graph of the score
windows. After Hall feasibility, its clique number is at most $9$.

This is the first clean positive formulation after the failed naive
frontier DP:

> Start with a fixed forced linear forest $H$. Then choose an
> assignment of vertices to positions inside their score windows, and
> thereby choose local flexible backedges from an interval graph of
> clique number at most $9$, so that $H$ plus the chosen flexible
> backedges remains a linear forest.

The decomposition is implemented in
[`../scripts/score_window_forced.py`](../scripts/score_window_forced.py).

[`../scripts/lfo_forced_flexible.py`](../scripts/lfo_forced_flexible.py)
turns the same split into an exact solver. It preloads the forced
backedge graph, rejects immediately if that graph is not a linear
forest, and then searches only over flexible overlapping-window
backedges. This is not yet the polynomial DP, but it is the executable
baseline for that DP.

Cross-checks:

- all non-isomorphic tournaments through $n=6$: zero disagreements with
  the score-window solver;
- the full exact $n=7$ census: zero disagreements, max 120 nodes;
- every returned YES order is verified independently as an LFO.

It also explains why the reversed-matching family is not itself a proof
against a polynomial algorithm. In that family, the $m$ long crossing
backedges are all forced by disjoint windows. They can be preloaded as
a fixed matching; the remaining choice graph is still local.

On the exact small censuses, this forced test has limited bite because
$n\le 9$ score windows overlap heavily:

| test set | immediate forced/Hall NOs | breakdown |
|---|---:|---|
| exact $n=7$ NOs | 3 of 20 | 2 size-bound + 1 combinatorial, all by Hall |
| exact known $n=8$ NO records | 423 of 1864 | all by Hall |
| sampled exact $n=9$ records | 87 of 384 sampled NOs | all by Hall |

The forced backedge graph is usually empty at these orders. That is not
a contradiction; score windows of width 5 cover most of a 7-, 8-, or
9-vertex tournament. The decomposition becomes meaningful in larger or
more skew-score tournaments.

The skew-score probe
[`../scripts/score_window_random_probe.py`](../scripts/score_window_random_probe.py)
tests this directly by starting from a transitive tournament and
reversing each arc independently with probability $p$. Output is stored
in:

- `../data/score_window_skew_probe_seed20260522.json` for
  $n\in\{12,16,20\}$ with 200 samples per $(n,p)$;
- `../data/score_window_skew_probe_n24_seed20260522.json` for $n=24$
  with 100 samples per $p$.

The forced backedge count grows with $n$ and with noise:

| n | p=0.02 | p=0.05 | p=0.10 | p=0.20 |
|---:|---:|---:|---:|---:|
| 12 | 0.28 | 0.765 | 0.995 | 1.11 |
| 16 | 0.955 | 2.16 | 3.35 | 4.555 |
| 20 | 1.84 | 4.145 | 7.45 | 11.595 |
| 24 | 2.89 | 7.18 | 13.26 | 21.68 |

Forced-degree obstructions also begin to appear:

| n | p=0.02 | p=0.05 | p=0.10 | p=0.20 |
|---:|---:|---:|---:|---:|
| 12 | 0 | 0 | 0 | 0 |
| 16 | 1 | 5 | 6 | 1 |
| 20 | 1 | 12 | 50 | 1 |
| 24 | 3 | 20 | 17 | 0 |

This confirms the forced/flexible decomposition is not just formal
bookkeeping: on larger skew-score tournaments it starts producing a
nontrivial forced scaffold and immediate NO certificates. The hard
search regime in this model is light noise, especially around
$p\in\{0.02,0.05\}$: Hall usually passes, forced obstructions are
present but not dominant, and rare samples can require hundreds of
thousands of score-window nodes.

Comparing the plain score-window solver to the forced/flexible solver
on the hard $n=24$ light-noise regime gives:

| model | samples | baseline max | FF max | baseline p95 | FF p95 | FF improved | disagreements |
|---|---:|---:|---:|---:|---:|---:|---:|
| $n=24,p=0.02$ | 50 | 170216 | 162731 | 2266 | 1137 | 41 | 0 |
| $n=24,p=0.05$ | 50 | 36462 | 36265 | 16667 | 16017 | 42 | 0 |

The forced/flexible split improves most instances and sometimes cuts
p95 substantially, but it does not eliminate the rare search spikes.
So preloading forced edges is the right normalization, not the whole
algorithm. The remaining hard branching is inside the flexible
bounded-overlap part.

## Next formal target

The right next move is narrower than the previous "bounded frontier"
slogan. The active score-window band is bounded, but the crossing
backedge set is not. A viable polynomial DP must therefore compress the
unbounded pending part.

At position $i$, vertices with windows entirely before $i$ must already
be placed, vertices with windows entirely after $i$ cannot yet be
placed, and only vertices whose windows meet a short band around $i$
can be chosen next. The plausible DP state must record:

- the active vertices in the score window frontier;
- their current backdegrees;
- the partition of active vertices induced by current backedge
  components;
- a compressed representation of expired vertices with pending future
  backedges;
- enough component information to decide whether a future vertex with
  two past back-neighbors would close a cycle.

The reversed-matching family shows that the pending representation
cannot be "list every open crossing edge"; that list can have size
$\Theta(n)$ even in matching-FAS YES instances. The repeated component
family shows that endpoint pairings can carry $\Theta(k)$ independent
bits while all coarse degree data stays fixed. The next mathematical
subproblem is therefore:

> Can the expired pending part be quotient-compressed without losing
> the degree and cycle tests?

Equivalently, after the forced/flexible decomposition:

> Can a fixed forced linear forest be combined with bounded-clique
> interval choices in polynomial time while preserving maximum degree
> $2$ and acyclicity?

If yes, the Path-FAS half is in P. If no, the obstruction should be
strong enough to guide a non-AAL hardness reduction.
