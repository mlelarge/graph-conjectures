# D84: Residual Ladder Skeleton Source Derivation

Date: 2026-06-20.

Artifact: `scripts/residual_ladder_skeleton_source_audit.py`.

## Purpose

D83 proves ER-4 from a residual ladder skeleton.  This note derives that
skeleton from clause-level sealed support data: active first-successor
attachment, distance-graded R2 support boundaries, root/spare domination,
and support shortcut orientations.

This is the right granularity for the current proof file.  The older
CL/DT notes do not yet state every shortcut orientation as one theorem;
D84 names the exact source clauses that the raw sealed-block proof must
deliver.

## Blocks

Use the D83 outside support blocks:

    M = {m},        T = {tau},       S = {s1,s2},
    H = {h1,h2},    L = {ell1,ell2}, P = {p1,p2},
    R = {r0}.

The intended order is

    M -> T -> S -> H -> L -> P -> R -> M.

In D42 labels:

    M={12}, T={23}, S={21,22}, H={19,20},
    L={17,18}, P={15,16}, R={14}.

## Source Clauses

The residual ladder skeleton is the union of the following source
clauses.

**S0, active first successor and returns.**

The first successor has the unique outside exit

    w1 -> tau,

and, by D82's semicomplete attachment lemma,

    x -> w1        for every x in O' \ {tau}.

**S1, middle-to-top support.**

The middle support vertex always has the chain support arc

    m -> tau.

In the robust case it also has one lower ladder support arc

    m -> h1.

In the weak-middle case the robust support arc is absent; this is the
D74-type optional deletion that creates the named middle row.  The arc
`m -> tau` remains.

**S2, distance-graded R2 boundaries.**

The support ladder supplies the endpoint two-fan

    T -> S,

and the complete two-by-two boundaries

    S -> H,    H -> L,    L -> P.

Each two-vertex block also has an internal forward support arc, and `P`
has both internal orientations.

These are the distance-graded R2 pairs: each level has two supports, and
the higher level sends to both supports in the next lower level.

**S3, root/spare boundary and domination.**

The two root/spare supports in `P` enter the terminal root-side vertex:

    P -> R.

They also dominate the upper support region:

    P -> M,T,S,H.

This is the root/spare support supplied by the DT side: the two
root/spare vertices are distinct support vertices and retain their
out-arcs into the upper outside ladder.

**S4, terminal support backfan.**

The terminal root-side support vertex sends back into the nonterminal
ladder:

    R -> M,T,S,H,L.

This is the terminal support/backward package for the last chain support
before `rho`.

**S5, shortcut orientations.**

The semicomplete no-shortcut orientation around the ladder gives:

    S -> M,
    H -> T,
    h2 -> M,
    L -> M,T,S.

These are the shortcut arcs that prevent an unlisted subset from being a
two-exit terminal class.  They are harmless for the shortest path
because they point inside the support system, not to a new earlier
`rho` route.

## Skeleton Derivation Lemma

S0--S5 imply that the D83 residual ladder skeleton is contained in the
outside quotient.

### Proof

List the arcs of D83's skeleton by source.

The attachment arcs `w1 -> tau` and `x -> w1` are exactly S0.

The arcs `m -> tau` and, in the robust case, `m -> h1` are S1.

The endpoint fan `tau -> s1,s2`, the complete boundaries
`S -> H`, `H -> L`, `L -> P`, and the internal block arcs are S2.

The arcs `P -> R` and `P -> M,T,S,H` are S3.

The arcs `R -> M,T,S,H,L` are S4.

The remaining shortcut arcs `S -> M`, `H -> T`, `h2 -> M`, and
`L -> M,T,S` are S5.

These categories are disjoint except for harmless redundancy of meaning,
and their union is exactly the D83 skeleton.  Therefore the skeleton is
contained in the outside quotient.  QED.

## Consequence

Combining D84 with D83 gives ER-4.  Combining ER-4 with D79, D81, and
D82 gives AOC at the endpoint-reduced support-normal-form level.  D75
then gives FSQ.

Thus the outside-cut part has been reduced to proving the source clauses
S1--S5 from the raw sealed-block/CL/DT construction.

## Audit

The audit verifies two facts on D42, D63, D66, D63+D66, and the D74
support-reversal variants:

1. the source categories above are exactly the D83 skeleton;
2. the skeleton is contained in the actual outside quotient.

In the robust variants the skeleton has 67 arcs.  In the weak-middle
variants it has 66 arcs, missing only the robust middle support arc
`m -> h1`.

## Remaining Structural Target

The remaining proof obligation is now sharper than ER-4:

* derive the block decomposition `M,T,S,H,L,P,R`;
* prove the complete R2 support boundaries;
* prove root/spare domination and the terminal backfan;
* prove the shortcut orientations, especially `S -> M`, `H -> T`,
  `h2 -> M`, and `L -> M,T,S`;
* prove that the only allowed weakening is deletion/reversal of the
  single robust middle arc `m -> h1`.

This is the next raw sealed-block/CL/DT target.
