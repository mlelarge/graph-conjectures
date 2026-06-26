# D61: Generalized Cut-Cover Selection Lemma

Date: 2026-06-18.

Status: proved in profile form.  The proof uses the full D42-style
prefix profile, including cuts obtained by adding arbitrary pending
vertices to the three deficient prefixes.  Deriving that profile from
the bare CL/DT sealed-chain axioms remains a separate global task.

## Statement

Let `K` be a non-degenerate sealed multi-crossing chain kernel with the
D42 prefix profile.  Let

    Q- subset Q0 subset Q+

be the three deficient split-core prefix cuts, with core out-sizes

    b- = 1,   b0 = 0,   b+ = 1.

Let the forced pending vertices be `I = {i_1,...,i_t}`.  A pending
two-step path `x -> i -> y` has repair vector

    r(x,i,y) = (1_{x in Q-, y notin Q-},
                1_{x in Q0, y notin Q0},
                1_{x in Q+, y notin Q+}).

Then the pending split paths can be chosen so that the sum of their
repair vectors dominates

    (1,2,1).

Consequently, after the pending split-off, the split semicomplete core
has `lambda >= 2`.

## Prefix-Plus-Pending Profile

The proof needs the following explicit form of the D42 prefix profile.
For each of the three prefixes `Q in {Q-,Q0,Q+}` and every subset
`J subseteq I`, the cut `Q union J` is a legitimate cut of the original
3-arc-strong graph.  Since pending vertices are independent, its out-cut
has the form

    d^+(Q union J)
      = b(Q)
        + sum_{i notin J} e_i(Q)
        + sum_{i in J} f_i(Q),

where:

* `b(Q)` is the split-core out-size of `Q`;
* `e_i(Q)` is the number of arcs from `Q` into the pending vertex `i`;
* `f_i(Q)` is the number of arcs from `i` to the complement of `Q`.

Since the original graph is 3-arc-strong, this quantity is at least
three for every `J`.  Taking the minimizing choice of `J` independently
for each pending vertex gives

    sum_i min(e_i(Q), f_i(Q)) >= 3 - b(Q).        (1)

Thus

    Q- : sum_i min(e_i(Q-), f_i(Q-)) >= 2,
    Q0 : sum_i min(e_i(Q0), f_i(Q0)) >= 3,
    Q+ : sum_i min(e_i(Q+), f_i(Q+)) >= 2.

The term `min(e_i(Q), f_i(Q))` is exactly the maximum number of
pairwise source-and-target-disjoint pending paths through `i` that cross
`Q`, because every entry into `i` can be paired with every exit from
`i`.

## Interval Compression Lemma

Refine the nested prefixes into four slabs:

    L0 = Q-,
    L1 = Q0 \ Q-,
    L2 = Q+ \ Q0,
    L3 = V \ Q+.

A pending path from slab `La` to slab `Lb`, with `a < b`, is an interval
`[a,b)` on the three boundaries.  It covers exactly the cuts whose
boundaries lie between `a` and `b`.

**Lemma.**  Suppose a finite list of pending paths through one fixed
pending vertex contributes cover vector `c = (c-,c0,c+)`.  Then, using
only entries and exits already present in that list, it can be replaced
by at most two legal pending paths through the same vertex whose cover
vector dominates

    (min(c-,1), min(c0,2), min(c+,1)).

### Proof

If no listed path crosses the middle boundary `Q0`, then the only
possible requirements are the two side units.  One left-crossing path
and one right-crossing path, if present, suffice.

Assume some listed path crosses `Q0`.  If only one middle unit is needed,
choose a middle-crossing path and stretch it, if necessary, by replacing
its source with the leftmost listed source and its target with the
rightmost listed target.  Complete local pairability through the pending
vertex keeps the resulting two-step path legal, and stretching an
interval cannot lose a covered boundary.

If two middle units are needed, choose two listed middle-crossing paths
with distinct sources and distinct targets.  If the pair misses the left
boundary but the original list covered it, replace the source of the
first path by a listed source in `L0`.  Its target is still beyond `Q0`,
so it still crosses the middle boundary and now also crosses `Q-`.  If
the pair misses the right boundary but the original list covered it,
replace the target of the second path by a listed target in `L3`.  Its
source is still before `Q+`, so it still crosses the middle boundary and
now also crosses `Q+`.

If the two repairs try to use the same endpoint, use the other
middle-crossing path for one of the two replacements; if both side
repairs belong to the same original path, replacing one selected path by
the interval from its source to its target covers both side boundaries
at once.  In every case we keep two distinct sources and two distinct
targets.  Therefore the replacement is a legal local two-split choice
and dominates the truncated cover vector.  QED.

## Proof of the Selection Lemma

For each prefix `Q`, inequality (1) gives a local matching of pending
paths crossing `Q` of size at least `3 - b(Q)`.  Choose:

* one path crossing `Q-`;
* two paths crossing `Q0`;
* one path crossing `Q+`.

Before enforcing the per-pending-vertex limit, these four witnesses
already dominate the desired deficiency vector `(1,2,1)`.

Now group the chosen witnesses by their pending vertex.  Apply the
Interval Compression Lemma separately to each group.  The compression
uses only entries and exits already present at that pending vertex,
keeps at most two paths through that vertex, and does not reduce any
coordinate below what is globally needed: side coordinates are only
needed once, and the middle coordinate is only needed twice.

After compressing every group, the union of the compressed local choices
is a legal partial pending split choice and still dominates `(1,2,1)`.
Each pending vertex with one prescribed path has a second local mate by
the pending-completion part of the D42 profile; vertices with two
prescribed paths already have distinct sources and targets by the
compression lemma.  Complete all remaining forced pending vertices
arbitrarily.

Thus there is a full admissible pending split choice whose repair vector
dominates `(1,2,1)`.

By D60, covering `(1,2,1)` is necessary and sufficient to repair the
three deficient split-core cuts.  Every other split-core cut already has
out-size at least two and adding split arcs is monotone on directed
out-cuts.  Hence the resulting split semicomplete core has
`lambda >= 2`.  QED.

## Consequence

This proves the generalized cut-cover selection lemma at the profile
level:

> Once the D42 prefix profile is present, 3-arc-strongness of the
> original kernel forces enough pending split paths to cover `(1,2,1)`;
> the D53 `{u,heads}->chainK` predicate is only one convenient
> sufficient subcase.

What remains for a full CRUX-A closure is not this selection step.  The
remaining structural obligation is to derive the full prefix-plus-pending
profile from the general sealed-block, CL, and DT hypotheses, and then
to supply the external colour-prescribed semicomplete
pending-completion theorem.

