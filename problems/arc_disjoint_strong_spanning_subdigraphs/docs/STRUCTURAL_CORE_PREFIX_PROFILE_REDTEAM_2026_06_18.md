# D63: Structural Core-Prefix Profile Red-Team

Date: 2026-06-18.

Artifact: `scripts/structural_core_prefix_redteam.py`.

## Verdict

The requested exact structural profile

    Q- subset Q0 subset Q+,     out-sizes 1,0,1

cannot be proved from the currently formalized sealed-block/CL/DT
hypotheses.  The out-size-one clause for `Q-` is not forced.

There is a one-arc perturbation of the D42 chain kernel that preserves
the relevant sealed-chain gates but changes the old `Q-` cut from
out-size `1` to out-size `2`.

## Perturbation

Start from the D42 `D^bullet` chain kernel and add the single arc

    6 -> 5

in `D^bullet` labels.  In host labels this is

    7 -> 6,

the reverse arc between the two head vertices.

The script verifies that the perturbed host still has:

    simple near-split host: yes
    lambda(host)=3
    lambda(D^bullet)=3
    cage={1,2,3,4}
    unique shortest path 7->8->9->10->11->12->13->rho
    forced D_O arcs (7,8), (8,9), (10,11), (12,13)
    B*_out={(8,9),(10,11),(12,13)}
    original hard gateway U-exit={(1,10)}

Thus the sealed block, the CL forced-chain form, the DT-compatible
connectivity, and the hard gateway geometry survive this perturbation.

## Changed Prefix Profile

In the original D42 split core the three low cuts were:

    Q- = {2,3,4,5,7,8}          out=1,
    Q0 = {2,3,4,5,6,7,8}        out=0,
    Q+ = {2,3,4,5,6,7,8,10}     out=1.

After adding `7 -> 6`, the old `Q-` has out-size two:

    old Q- out-edges = (2,6), (7,6).

The remaining low cuts are exactly:

    Q0 = {2,3,4,5,6,7,8}        out=0,
    Q+ = {2,3,4,5,6,7,8,10}     out=1.

So the exact `1,0,1` core-prefix profile is false at the level of the
sealed-block/CL/DT gates currently available in the project.  A proof of
that exact profile would need an extra orientation-minimality or
head-minimality hypothesis forbidding reverse head arcs like `7 -> 6`.

## What Remains True

The perturbation does not harm the pending-decomposition route.  It only
removes a deficient cut.  The D60/D61 machinery needs every deficient
cut to be repaired; if `Q-` already has out-size at least two, it needs
no pending repair.

The corrected structural target should therefore be:

> Derive the sealed prefix `Q0 = B* \ I_forced` with split-core out-size
> zero, derive the successor prefix `Q+` when it is deficient, and prove
> every other split-core cut has out-size at least two.  One-head-deleted
> prefixes `Q0 \ {h}` are included only when their out-size is one.

In this corrected form, D60 must be generalized from the fixed
deficiency vector `(1,2,1)` to the vector consisting only of actually
deficient prefixes.  The old D42 vector remains the sharpest case; the
red-team perturbation is easier, with deficiency vector `(2,1)` for
`Q0,Q+`.

## Structural Consequence

The exact D62 next action is too strong as stated.  The right next move
is either:

1. add and justify an orientation-minimality hypothesis that normalizes
   the head block and recovers an out-size-one `Q-`; or
2. revise the core-prefix theorem to a monotone deficient-prefix form,
   where extra core exits simply delete obligations from the cut-cover
   vector.

Option 2 is safer: it matches the monotonicity of the split-core
connectivity proof and avoids baking a D42-specific head orientation
into the general theorem.

