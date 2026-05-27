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

## Naive active-bag DP fails

The natural next attempt is an interval-bag DP over the flexible
overlap graph. The first candidate state at position $i$ is:

- the active score-window vertices;
- which active vertices have already been placed;
- the current degrees of active vertices;
- the component partition restricted to active vertices.

This state is still insufficient. The probe
[`../scripts/ff_signature_probe.py`](../scripts/ff_signature_probe.py)
finds a collision already in the 7-vertex component witness. The two
prefixes

```text
5,3,6,1
6,3,5,1
```

have the same prefix vertex set, and at position 4 they have the same
active-bag signature:

```text
active vertices      = {0,1,2,3,4}
placed active        = {1,3}
active degrees       = 0:0, 1:0, 2:0, 3:1, 4:0
active partition     = all five active vertices singleton
```

But the first prefix is not extendable and the second is extendable.
The difference is connectivity carried by forgotten vertices outside
the active bag. Therefore a DP over only the current interval bag is
not sound, even after forced/flexible normalization.

This is the sharpest current obstruction to a polynomial proof. Any DP
must carry some quotient of **latent connectivity**: component
information whose current representatives are outside the active
score-window bag but whose effect can reappear when future vertices are
placed.

## A bounded visible-latent interface

The active-bag failure above does not mean the latent part is arbitrary.
After forced/flexible normalization there is a precise local bound on
the part of the expired prefix that can still be touched by **future
flexible** choices.

Fix a cut after positions $0,\ldots,i-1$ have been filled. Let

- $P_i$ be the placed prefix;
- $R_i$ be the unplaced suffix;
- $A_i=\{v:\ell_v\le i\le h_v\}$ be the active score-window set;
- $X_i=\{p\in P_i:h_p<i\}$ be the expired prefix vertices.

If $p\in X_i$ and $y\in R_i\setminus A_i$, then

$$
h_p<i<\ell_y,
$$

so $I_p$ and $I_y$ are disjoint. Hence the pair $\{p,y\}$ is not a
flexible pair at all: its contribution is already part of the fixed
forced graph. Therefore an expired prefix vertex can still be incident
with a future **flexible** backedge only through an unplaced active
vertex.

Define the old visible ports at cut $i$ by

$$
O_i=\{p\in P_i\setminus A_i:\exists x\in A_i\cap R_i
\text{ with } x\to p \text{ and } I_x\cap I_p\ne\emptyset\}.
$$

Equivalently, in the implementation these are the forgotten prefix
vertices in `flex_outmask[x] & prefix_mask` for unplaced active
vertices $x$.

In any branch that can still extend to an LFO, each unplaced active
vertex $x$ has at most $2-\deg(x)$ such old ports, because all of them
will become back-neighbors of $x$ when $x$ is placed. In particular,
after the standard future-degree pruning,

$$
|O_i|\le 2|A_i\cap R_i|\le 18,
$$

using the Hall bound $|A_i|\le 9$. Thus the vertices relevant to future
flexible choices are contained in the bounded set

$$
A_i\cup O_i,
$$

of size at most $27$.

This gives a sharper candidate DP state than the failed active-bag
state:

- the active vertices $A_i$;
- which active vertices are already placed;
- the current degrees of vertices in $A_i\cup O_i$;
- the component partition induced by the current backedge graph on
  $A_i\cup O_i$;
- for every unplaced active vertex $x$, the old ports in $O_i$ that
  $x$ will hit if $x$ is placed next.

This state is sufficient for all **immediate** degree and cycle tests
caused by placing a currently active vertex: every new flexible
backedge from that vertex goes to the current prefix, and every expired
prefix endpoint it can hit lies in $O_i$.

The probe
[`../scripts/ff_signature_probe.py`](../scripts/ff_signature_probe.py)
implements this visible-latent signature. It still finds the
active-bag collision above, but the strengthened signature separates
that collision: on the same 7-vertex witness, no mixed-extendability
collision is found to depth 5. A full scan of the exact $n=7$ census to
depth 5 likewise found no visible-latent collision:

```bash
python3 scripts/ff_signature_probe.py \
  --census data/lfo_full_n7.json --depth 5 --mode visible
```

This is evidence for the state, not a proof of polynomiality.

The remaining gap is no longer "future flexible edges can touch
arbitrarily many old vertices"; that statement is false after the
locality lemma above. The real gap is **dormant forced-component
propagation**. A forced linear-forest component may cross a cut without
having a currently visible old port. If earlier flexible choices have
merged that component with another component, the merged identity may
matter later when a far endpoint of the forced component enters the
active window. The reversed-matching family is the benign example of
many such dormant forced components; the component-entropy family shows
that connectivity bits can matter. A polynomial proof now has to show
that these dormant forced-component identities admit a bounded or
polynomial quotient, or else exploit them for hardness.

## Step A: forced/flexible normalization kills the entropy family

The 2^k entropy lower bound was built on cut-isolated sums of the
7-vertex component witness, *before* score-window + forced/flexible
normalization. The script
[`../scripts/cut_isolated_visible_test.py`](../scripts/cut_isolated_visible_test.py)
checks whether the FF-normalized DP still sees that entropy.

**Q1 (Hall feasibility).** The cut-isolated sum $T_k$ is Hall-feasible
for every tested $k$. The score windows accommodate the linearly
growing indegrees, so this is not the obstacle.

**Q2 (pattern survival).** Out of the $2^k$ good/bad local patterns,
only a small subset survives the score-window + initial-forced-state
checks at the prefix-construction step. At $k = 3$, **7 of 8 patterns
are killed during prefix construction**:

| pattern | longest valid prefix depth |
|---|---:|
| `(good,good,good)` | 12 of 12 (extendable globally) |
| `(good,good,bad)` | 11 of 12 |
| `(good,bad,*)` | 7 of 12 |
| `(bad,*,*)` | 3 of 12 |

The mechanism at $k \ge 2$: the cross-copy indegree contributions push
the local "suffix" vertex 4 of each copy into the disjoint-window
regime with the local prefix vertices 2 and 3, creating *forced*
backedges $4 \to 2$ and $4 \to 3$ at initialization. These pre-merge
local-2 and local-3 into a single forced linear-forest component
inside each copy. The local *bad* prefix would add flex backedge
$3 \to 2$, which now closes a triangle with the forced $\{2, 4, 3\}$
component, and the cycle test rejects.

So **forced/flexible normalization destroys the bad-pattern entropy
before it can appear**. The original 2^k lower bound does not transfer
to the FF DP state space.

## Sleeping-block tracking is empirically redundant

To probe further, the augmented "sleeping-block signature" tracks the
partition restricted to $A_i \cup O_i \cup F_i$, where $F_i$ is the set
of future-opening unplaced vertices. This is a strict refinement of
visible-latent. See
[`../scripts/sleeping_block_probe.py`](../scripts/sleeping_block_probe.py).

Results so far:

| test set | tournaments | visible classes | sleeping classes | visible collisions | sleeping refines visible |
|---|---:|---:|---:|---:|---:|
| exact $n = 7$ census (depth 5) | 456 | 128,647 | 129,006 | 0 | 50 of 456 |
| random $n = 8$ samples (depth 4) | 30 | 2,650 | 2,650 | 0 | 0 of 30 |
| cut-isolated $k = 2$ (depth 4) | 1 | 49 | 49 | 0 | no |
| cut-isolated $k = 3$ (depth 4) | 1 | 37 | 37 | 0 | no |
| cut-isolated $k = 4$ (depth 4) | 1 | 37 | 37 | 0 | no |

On the cut-isolated entropy family — the precise construction that
motivated the dormant-component concern — sleeping-block tracking is
**completely redundant**: visible and sleeping signatures produce
identical equivalence classes at $k \in \{2, 3, 4\}$.

On the $n = 7$ census, sleeping strictly refines visible on 50 of 456
tournaments, but the refinement is harmless: visible-latent already has
0 collisions across all 456 tournaments, so the extra distinctions made
by sleeping never separate mixed-extendability states.

**Conclusion (Step A).** Across all tested instances, including the
entropy family that originally motivated the concern, visible-latent
suffices and sleeping-block tracking adds no distinguishing power. The
augmented DP state can plausibly stay at the bounded $|A_i| \le 9$,
$|O_i| \le 18$ interface.

The result is pinned by `../tests/test_sleeping_block.py`.

## Induction attempt: visible-latent is not a bisimulation

The first attempted proof was the obvious induction:

> If two FF-normalized prefix states at cut $i$ have the same
> visible-latent signature, then for every legal next vertex $x$, the
> child states at cut $i+1$ again have the same visible-latent
> signature.

This would immediately imply extendability-equivalence. It is false.

A 12-vertex light-noise skew tournament gives two valid prefixes

```text
0,1,2,3,5
1,0,2,3,5
```

with identical visible-latent signature at cut 5. Placing vertex 4 next
is legal from both states, but the child visible-latent signatures at
cut 6 differ. The reason is exactly the dormant-component issue: vertex
11 enters the active band at cut 6. In the first prefix, 11 is in a
dormant forced component separate from the visible component containing
5; in the second prefix, the hidden ordering of 0 and 1 has already
merged 11 into that component. The current visible-latent signature at
cut 5 does not see this distinction. The sleeping-block signature does.

So the clean one-step bisimulation proof does **not** work for
visible-latent alone. The pinned test is
`VisibleInductionAttemptTest.test_visible_signature_is_not_a_one_step_bisimulation`
in `../tests/test_sleeping_block.py`.

This does not refute visible-latent extendability-equivalence. In fact,
the pinned parents are rejected by the solver's forced-future degree
prune before branching. What it refutes is the raw, unpruned
bisimulation claim.

The pruned one-step version also fails. A 12-vertex light-noise skew
tournament gives two prefixes

```text
0,1,4,2,3
2,0,4,1,3
```

that both survive Hall and forced-future pruning, have identical
visible-latent signature at cut 5, and have different visible-latent
child transition profiles. This is pinned by
`VisibleInductionAttemptTest.test_visible_pruned_one_step_mismatch_is_not_extendability_collision`.
However, the same witness has no mixed extendability class: all
visible-latent-equivalent pruned prefixes at depth 5 still agree on
whether they complete to an LFO. Thus the surviving target is strictly
weaker than any one-step bisimulation:

> visible-latent-equal pruned states may branch into different
> visible-latent classes, but the set of winning continuations is
> nonempty on one iff it is nonempty on the other.

A proof using visible-latent alone must therefore prove direct
extension-equivalence, or prove a simulation up to a coarser winning
relation. Child-state equality is dead.

The direct extension-equivalence probe has been strengthened so it
groups prefixes by signature first and computes exact completions only
inside duplicate signature classes:

```text
python3 scripts/wake_signature_probe.py \
  --census data/lfo_full_n7.json \
  --depth 5 --kind visible --check extendability
```

Current negative searches for a counterexample:

| test set | result |
|---|---:|
| exact $n=7$ census, depth 5 | 456 checked, no collision |
| padded wake witnesses, horizons 1-4, depth 5 | no collision |
| skew random, $n=12$, $p\in\{0.02,0.05\}$, 20 samples total | no collision |
| skew random, $n=16$, $p\in\{0.02,0.05\}$, 20 samples total | no collision |

This is not a proof, but it sharply narrows the claim. The visible
state provably does not determine the next visible state. It may still
determine the Boolean question "is there at least one completion?"

The stronger same-suffix transfer statement is false. A 10-vertex
skew witness has two visible-latent-equivalent pruned prefixes

```text
0,1,3,2,4
2,1,3,0,4
```

that are both extendable. The suffix

```text
5,6,7,9,8
```

completes the first prefix, but fails on the second prefix: when vertex
8 is placed last, it hits past vertices 3 and 9, which are already in
the same hidden component in the second state. The alternate suffix

```text
5,6,7,8,9
```

completes both. This is pinned by
`VisibleInductionAttemptTest.test_suffix_transfer_is_false_but_extension_survives`.
Thus the proof cannot be "every suffix transfers." It must be a
winning-region proof: hidden differences may force a different suffix,
but should not change existence of some suffix.

## Exchange-repair target

The 10-vertex suffix-transfer failure suggests the correct local
repair. Suppose visible-equivalent states $S,S'$ are at cut $i$, and a
suffix $\sigma$ that completes $S$ first fails from $S'$ when trying to
place vertex $x$ at suffix position $t$. At that moment, $x$ has past
flexible back-neighbors $a,b$ that are already in the same hidden
component in $S'$. At least one of $a,b$ was placed earlier in the
suffix, not in the original visible interface; otherwise the visible
partition would already record the cycle.

The candidate exchange lemma is:

> Move $x$ left in the suffix, past one of the suffix-created members
> of the hidden component, until $x$ no longer simultaneously hits both
> sides of that component. Then the repaired suffix is still
> score-window-valid and does not create a degree or cycle violation.

This is exactly what happens in the witness: moving 8 before 9 changes
`5,6,7,9,8` into `5,6,7,8,9`.

The probe
[`../scripts/exchange_repair_probe.py`](../scripts/exchange_repair_probe.py)
searches for visible-equivalent states where a completing suffix for
one state fails from the other and no single left-move of the first
failing vertex repairs it. Current results:

| test set | result |
|---|---:|
| exact \(n=7\) census, depth 5 | 41,266 same-remaining transfer checks, no same-suffix failure |
| 10-vertex suffix-transfer witness | no exchange obstruction |
| 10-vertex suffix-transfer witness, all completions | 72 same-suffix failures, 72 one-exchange repairs |
| skew random, $n=10,12$, $p\in\{0.02,0.05,0.1\}$, 120 samples | no exchange obstruction |
| skew random, $n=14$, $p\in\{0.02,0.05\}$, 10 samples | no exchange obstruction |
| uniform random, $n=9,10$, 40 samples | no exchange obstruction |

So the proof bottleneck is now sharper than "dormant components are
irrelevant." Dormant components can matter enough to invalidate a
chosen suffix.  That repair program has now been refuted at two
levels.  First, strict-progress left moves are insufficient.  Second,
one-block right moves are insufficient.  Most importantly, a skew
\(n=12\) witness refutes visible-latent extension-equivalence itself:
two FF-pruned same-prefix-set states have the same visible-latent
signature, but one is extendable and the other is not.

The current formal write-up is
[`exchange_proof_draft.md`](exchange_proof_draft.md). It proves the
score-window/forced-flexible/local-placement pieces, records the repair
counterexamples, and identifies the new positive target: strengthen the
state.  Sleeping-block and wake-1 signatures separate the visible-
latent collision.

A second tempting shortcut also fails. One might hope that sleeping
refinements of a visible-latent class occur only in dead states. They
do not. In a small skew-score probe at $n=16$, visible-latent classes
split by sleeping-block information inside extendable states. The
new \(n=12\) witness goes further: a visible class can split into mixed
extendability, and sleeping-block separates it. Thus sleeping
distinctions are not cosmetic; at least some of them are required.

The straightforward induction does work for the larger sleeping-block
state on the pinned witnesses, because future-opening vertices are
already represented before they enter the active band. But that state
contains all future-opening vertices and is not bounded by the constant
27 interface, so it is a proof device rather than the desired
polynomial DP state.

## Fixed finite wake horizon is not a bisimulation

The next attempted bounded repair was a one-step wake signature. At cut
$i$, augment visible-latent by the vertices whose windows open at
$i+1$, together with the old prefix ports they can already hit by
flexible backedges. This is implemented in
[`../scripts/wake_signature_probe.py`](../scripts/wake_signature_probe.py)
as `wake_signature(..., horizon=1)`.

This repair separates the raw 12-vertex failure above: the two prefixes
have the same visible-latent signature but different horizon-1 wake
signatures. However, horizon 1 is **not** a one-step bisimulation on
the surviving pruned DP state space.

A second 12-vertex skew tournament has two prefixes

```text
0,1,3,2,4
2,0,3,1,4
```

that both survive forced-future pruning and have the same horizon-1
wake signature at cut 5. Their horizon-1 child transition profiles
differ. The obstruction has simply shifted: to know the child's
horizon-1 wake data, the parent needs information about vertices waking
two cuts ahead. On this witness, horizon 2 separates the two parent
states, and sleeping-block tracking also separates them, but horizon 1
does not.

So fixed one-step wake tracking is not the missing bounded datum. The
same obstruction can be pushed farther out. The base wake-failure
witness has two surviving prefixes

```text
0,1,3,2,4
2,0,3,1,4
```

with the same horizon-1 wake signature but different horizon-1 child
transition profiles. Inserting one new transitive padding vertex
immediately before the delayed dormant vertex raises that delayed
vertex's indegree by one, hence moves its score window one cut later.
The same two prefixes then have the same horizon-2 wake signature, but
different horizon-2 child transition profiles. Horizon 3 separates that
padded pair.

Iterating the padding gives, for every tested $h\in\{1,2,3,4\}$, a
tournament $T_h$ with two prefixes that:

- survive interval-Hall and forced-future pruning;
- have the same horizon-$h$ wake signature;
- have different horizon-$h$ child transition profiles;
- are separated by horizon $h+1$.

The construction is implemented by
`padded_wake_failure_witness(h)` in
[`../scripts/wake_signature_probe.py`](../scripts/wake_signature_probe.py)
and pinned in
`VisibleInductionAttemptTest.test_padded_witness_defeats_each_tested_finite_horizon`.

This does not prove that no bounded non-horizon summary exists. It does
kill the obvious finite-lookahead ladder: "just track the next $h$
opening layers" cannot be the final DP state if the proof requires
one-step child-signature equality.

This has now been sharpened by a skew \(n=12\) counterexample: visible-
latent extension-equivalence itself is false.  Two FF-pruned prefixes
with the same prefix set and the same visible-latent signature can have
different extendability.  Sleeping-block and wake-1 signatures separate
that collision.

The remaining plausible options are therefore:

- prove soundness for a stronger bounded signature, with sleeping-block
  connectivity as the first candidate;
- find a bounded summary of the *entire wake schedule*, not merely a
  fixed number of opening layers;
- or pivot to hardness using the visible-latent collision / padded
  wake-chain as obstruction families.

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

After the visible-latent collision, the picture has moved again:

- The active-bag-only DP is unsound (the original ff_signature_probe
  active-bag collision still stands).
- The visible-latent DP is unsound: a skew \(n=12\) witness has
  same-prefix-set, same-visible-signature states with different
  extendability.
- Sleeping-block tracking separates the new collision.  On the witness
  tournament at depth 5, visible-latent has 12 extendability
  collisions while sleeping-block has 0.
- Sleeping-block tracking remains redundant on the original
  cut-isolated entropy family.  The cycle-closing test inside
  `_initial_forced_state` combined with the score-window normalization
  kills those bad-pattern branches before they can multiply.

So the empirical picture still supports a *bounded-interface* DP, but
not with the visible-latent state alone.  The next candidate state must
include sleeping/dormant path connectivity.  Its size bound and
soundness are now the central questions.

## Next formal target

After the induction attempt, the cleanest remaining proof obligations
are:

1. **State-refinement theorem (formal).** Identify a bounded refinement
   of visible-latent, starting with sleeping-block connectivity, that
   separates all known extendability collisions and remains bounded by
   score-window geometry.

2. **Constructive DP and complexity bound.** Implement the refined DP
   and measure its worst-case state count empirically. If the count
   stays below $\mathrm{poly}(n) \cdot 2^{O(1)}$ on the
   tested censuses (including stress-tested $n \ge 10$ samples), this
   becomes the polynomial algorithm.

3. **Alternative hardness path.** If a soundness counterexample appears
   at higher $n$ or with a non-cut-isolated construction, that
   immediately gives a refined family for either a hardness reduction
   or a strictly larger but still polynomial DP state.

If the Path-FAS half is in P, the route is now visible:
forced/flexible normalization plus visible-latent DP. If it is not in P,
the obstruction has been narrowed to a specific kind of dormant
forced-component coherence that the score-window normalization does
*not* kill — and we have not yet exhibited such an obstruction.
