# D60: Exact Cut-Cover Criterion for the D42 Pending Core

Date: 2026-06-18.

Artifact: `scripts/d42_cut_cover_inequality_audit.py`.

## Statement

In the D42 capped pending split suite, let the three deficient split-core
prefix cuts be

    Q- = {2,3,4,5,7,8},          core out-size 1,
    Q0 = {2,3,4,5,6,7,8},        core out-size 0,
    Q+ = {2,3,4,5,6,7,8,10},     core out-size 1.

For a chosen set `S` of six pending split arcs, define

    c-(S) = |S cap delta+(Q-)|,
    c0(S) = |S cap delta+(Q0)|,
    c+(S) = |S cap delta+(Q+)|.

Then the D42 split core after adding `S` has `lambda >= 2` if and only if

    c-(S) >= 1,   c0(S) >= 2,   c+(S) >= 1.          (CC)

Equivalently, the pending choice must cover the deficiency vector

    (1,2,1).

## Proof

D53 verified by exact cut enumeration that before adding the pending
split arcs, the only split-core cuts of out-size at most one are
`Q-`, `Q0`, and `Q+`.  Their core out-sizes are respectively `1,0,1`.
Every other directed cut already has out-size at least two.

Adding pending split arcs is monotone on every directed cut.  For each
deficient cut `Q`, the new out-size is exactly

    core_out(Q) + |S cap delta+(Q)|.

Therefore the three deficient cuts become at least two precisely when
`S` supplies at least `1,2,1` new crossing arcs across `Q-`, `Q0`, and
`Q+`.  Since no other cut can drop, these three inequalities are
necessary and sufficient for `lambda >= 2`.

## Atomic Repair Vectors

The audit groups every atomic repairing split arc by its endpoint region
and its cover vector `(Q-,Q0,Q+)`:

    chainK -> chainK : (0,0,1)  via (10,11,12)

    heads -> chainK  : (0,1,0)  via (6,9,10)
    heads -> chainK  : (0,1,1)  via (6,11,12)
    heads -> chainK  : (1,1,0)  via (7,9,10)
    heads -> chainK  : (1,1,1)  via (7,11,12)

    heads -> heads   : (1,0,0)  via (7,11,6)

    u -> chainK      : (1,1,0)  via (2,9,10)
    u -> chainK      : (1,1,1)  via (2,11,12), (2,13,14)

    u -> heads       : (1,0,0)  via (2,11,6), (2,13,6)

    v -> chainK      : (1,1,0)  via (8,9,10)

This table is the corrected replacement for the over-narrow D58 feed
profile.  The D53 subfamily `{u, heads} -> chainK` is a useful
sufficient subsystem, but the exact cut-cover language also includes
original-chain repairs such as `v -> chainK` and `chainK -> chainK`.

## Exact Capped-Suite Check

The executable audit confirms:

    local_counts={9:80, 11:80, 13:80}
    total=512000
    cover_success=84014
    d53_selected=56264
    d53_bad=0
    non_d53_success=27750
    broad_repair_success=19364
    minimal_success_vectors=[(1,2,1)]

Thus D53 is still a clean sufficient predicate with no false positives,
but it misses `27750` successful capped choices.  Among all successful
choices, `19364` use at least one broad D59 repair of type
`v -> chainK` or `chainK -> chainK`.

One explicit broad success has repairing paths

    (6,9,10)   heads -> chainK   vector (0,1,0),
    (10,11,12) chainK -> chainK  vector (0,0,1),
    (2,13,14)  u -> chainK       vector (1,1,1),

whose sum is `(1,2,2)`, hence it covers `(1,2,1)`.

## Consequence for the General Lemma

The Prescribed Pending Missing Entry Lemma should now be formulated as a
cut-cover selection lemma:

> In a sealed multi-crossing chain kernel with the D42 prefix profile,
> the admissible pending split paths can be chosen so that their repair
> vectors dominate `(1,2,1)`.

The older D53 feed predicate remains a convenient sufficient corollary:
one `u -> chainK` path covers `Q-` and one unit of `Q0`; a second
`{u,heads} -> chainK` path into a distinct chain successor supplies the
second `Q0` unit and, because not both such paths can target the first
successor `10`, supplies `Q+`.

The next symbolic task is to prove this cut-cover selection statement
from the sealed-block and forced-chain hypotheses, or else to find a
generalized chain kernel whose admissible repair vectors fail to cover
`(1,2,1)`.

