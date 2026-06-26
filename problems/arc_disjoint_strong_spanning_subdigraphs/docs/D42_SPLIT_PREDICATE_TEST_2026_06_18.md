# D53: D42 split predicate test

Date: 2026-06-18.

Artifact:

    scripts/d42_split_predicate_tester.py

Status: exact finite certificate for the capped D42 split-choice suite.

## Goal

D52 found that D42 split choices with `lambda(core) >= 2` are enriched
for split arcs feeding `chainK` from `u` and heads.  D53 searches small
threshold predicates and then verifies the cleanest predicate by cuts on
the whole capped D42 local-choice suite.

Run from the repository root:

    uv run python problems/arc_disjoint_strong_spanning_subdigraphs/scripts/d42_split_predicate_tester.py

## Sampled predicate search

With seed `5321`, the 2500-row sample gives:

    lambda_counts={0:879, 1:1191, 2:404, 3:26}
    good(lambda>=2)=430/2500

The best zero-false-positive sampled predicate is:

    u_chainK >= 1  and  u_or_heads_chainK >= 2

Equivalently: one selected split path has type `u -> chainK`, and at
least two selected split paths have source in `{u, heads}` and head in
`chainK`.

On the 2500-row sample it has:

    support=292
    false positives=0
    recall=0.679

The best near miss was weaker in the wrong direction:

    nonroot_to_chainK >= 3  and  u_or_heads_chainK >= 2

It has 68 good rows and 1 bad row, so the `u -> chainK` requirement is
doing real work.

## Exact capped-suite check

The D42 local-choice cap is:

    local_counts={9:80, 11:80, 13:80}
    total=512000

For the split core before adding the six split arcs, only three directed
cuts have out-size at most one:

    out=1: {2,3,4,5,7,8}
    out=0: {2,3,4,5,6,7,8}
    out=1: {2,3,4,5,6,7,8,10}

All other directed cuts already have out-size at least two in the core,
so a split choice has `lambda(core) >= 2` exactly when its six split arcs
repair these three cuts.

The exact cut pass over all `512000` capped choices gives:

    all_repaired=84014
    selected_by_predicate=56264
    repaired_selected=56264
    bad_selected=0

Thus the predicate is an exact sufficient condition on the capped D42
suite and catches `56264/84014 = 66.97%` of the capped choices with
`lambda(core) >= 2`.

## Proof shape

The three deficient cuts are prefix cuts in the D42 chain geometry.
The middle cut `{2,3,4,5,6,7,8}` has no core exit, so it needs two new
exits; any `u/head -> chainK` split arc exits it.  The first cut misses
one head, but a `u -> chainK` arc always exits it.  The last cut already
contains chain vertex `10`; nevertheless two `u/head -> chainK` arcs
force one target beyond `10`, because the available chainK targets are
tied to the forced-chain vertices:

    through 9:  target 10
    through 11: target 12
    through 13: target 14

and each local two-split choice uses a given chain target at most once.

This is now the cleanest D42 combinatorial kernel:

> Find one pending split path `u -> s -> chainK`, and a second pending
> split path from `u` or a head into a later chainK vertex.

## Consequence

D53 changes the next proof obligation.  We no longer need a broad
statistical characterization of successful D42 choices.  The immediate
symbolic target is a Chain-Feed Missing Entry Lemma: in every
non-degenerate sealed multi-crossing chain kernel, the forced-chain
vertices admit two pending split paths into successive chainK vertices,
one of them starting at `u`.

This remains evidence-plus-finite-certificate, not a theorem for all
uncapped local choices or all chain kernels.  It is exact for the D42
`80^3` capped suite and proof-shaped because it reduces to three cuts.
