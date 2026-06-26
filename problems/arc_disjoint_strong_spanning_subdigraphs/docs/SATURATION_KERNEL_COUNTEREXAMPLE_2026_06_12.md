# The D37 saturation kernel exists in-class (D38)

The residual kernel from
`REACH_SATURATION_2026_06_12.md` is realizable.  The checked witness is
`scripts/saturation_kernel_witness.py`.

## Construction

Start with the host from `relay_free_witness.py`, whose named vertices are

    V1: p=0, q=1, u=2
    V2: cage=3,4,5; v=6; heads=7,8;
        layers=9,10,11; rho-tails=12,13,14.

Replace the two arcs `v->10, v->11` by `10->v, 11->v`, and add the
compensation arcs `7->10, 8->11`.  The result is still a simple
`(1,0)`-near-split host, has arc-connectivity 3, and is SAD (SAT with
independent ILP agreement).  Its chord contraction also has
arc-connectivity 3.

In contraction labels:

    rho=0, u=1, cage={2,3,4}, v=5,
    heads={6,7}, layers={8,9,10}, rho-tails={11,12,13}.

The cage is `C_u={1,2,3,4}`, `u->rho` is absent, and the explicit
arc-disjoint pair in the verifier realizes the original hard gateway at
`a=(1,5)`: its `T`-set is the cage and its `U` has the single exit
`(1,6)`, hence no strict exit.

## Kernel tree

Use the shortest path

    P_v = 5 -> 8 -> 12 -> 0

and hence

    X_P = {1,2,3,4,6,7,9,10,11,13},
    O   = {5,8,12}.

The following spanning in-arborescence has `X_a^T=X_P`:

    cage: 2->3, 3->1, 4->1
    a:     1->5
    heads: 6->9, 7->10
    inside: 9->2, 10->3, 11->2, 13->3
    outside: 5->8, 8->12, 12->0.

It is cage-sparing: after deleting its labels, every cage vertex still
reaches `u` inside the cage.

Prescribe the canonical pair `(11,0),(13,0)`.  The resulting reachability
partition is exactly

    REACH = {0,8,9,10,11,12,13},
    Z     = {1,2,3,4,5,6,7}.

The three structural arcs from `Z` to `REACH` are

    5->8, 6->9, 7->10.

All have multiplicity one and all are used by `T`.  Thus the whole
three-arc cut is consumed.  Both roots dominate both heads, while the
heads' only boundary arcs into `O` are `6->5,7->5`, and `v=5` lies in
`Z`.  This is the D37 kernel exactly, including the host-connectivity
gate that killed the earlier G35 construction.

## Exhaustive prescription check

The verifier enumerates every pair of distinct-tail boundary arcs allowed
by the D35 completion statement.  No pair gives full prescribed-residual
reachability.  Therefore:

> The D35/H10 claim that every cage-sparing `T` admits a completing
> prescription pair is false in-class.

This does not refute fixed-root L-exist.  On the same digraph, reroute the
two heads internally as `6->2,7->3`, leaving the other tree arcs
unchanged.  The canonical pair then reaches every vertex.  The correct
existential target must therefore strengthen cage-sparing to prevent `T`
from consuming an entire block cut.  A natural replacement is a
block-sparing or laminar-cut-sparing choice of `T`, not a saturation
argument for arbitrary cage-sparing `T`.
