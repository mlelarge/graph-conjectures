# D65: Semicomplete Zero-Prefix Reduction

Date: 2026-06-19.

Artifact: `scripts/semicomplete_zero_prefix_reduction_audit.py`.

## Purpose

D64 leaves a structural task: identify the active deficient split-core
cuts.  This note proves the semicomplete part of that task.  Once the
sealed block supplies a zero prefix `Q0`, every possible low cut is
forced into a small list of local cases.

## Sealed Zero Prefix

Work in the chord-contracted digraph `D^bullet`, with `rho` the
contracted chord endpoint.  Let `B` be the CL sealed block and let `I_B`
be the forced pending vertices of `B` that are deleted when forming the
split semicomplete core `C`.

Assume the pending-tail boundary condition:

    delta^+_{D^bullet}(B) has all non-rho tails in I_B,

and assume the no-rho-boundary condition for the middle prefix:

    no vertex of B \ I_B has a rho-label leaving B.

Let

    Q0 = (B \ I_B) in the split core C.

Then

    d_C^+(Q0) = 0.

Indeed, any split-core arc from `Q0` to `C \ Q0` would lift to an arc of
`D^bullet` from `B \ I_B` to `V \ B`, contradicting the pending-tail
boundary condition.  Arcs whose tails lie in `I_B` disappear from the
split core, and rho-label exits are excluded by the no-rho-boundary
condition.

This is the symbolic source of the D42 middle cut
`Q0={2,3,4,5,6,7,8}`.

## Endpoint-Cleanliness

The D62 prefix-plus-pending formula needs endpoint-cleanliness.

Pending independence and absence of pending/chord-endpoint arcs follow
formally from the `(1,0)`-near-split host condition: the independent
side `V1` has only the chord arc `p -> q`, so the extra pending vertices
of `V1` have no arcs to one another and no arcs to or from the chord
endpoints.

For a core prefix `Q`, host arcs from `Q` to the chord endpoints are
exactly rho-label exits of the corresponding `D^bullet` set.  Host arcs
from chord endpoints into `Q` are exactly rho-label entries.  Hence
endpoint-cleanliness for `Q` follows from:

    no rho-label exits from Q,
    no rho-label entries into Q.

For `Q0`, this is the no-rho-boundary condition above plus the usual
strict rho-headless setup for entries into the sealed block.  For side
prefixes `Q0 \ {h}` and `Q0 union {w}`, the same check is local: deleting
`h` cannot create an endpoint exit, and adding `w` is clean exactly when
`w` has no rho-label exit and no rho-label entry relevant to the host
prefix calculation.

Thus endpoint-cleanliness is no longer mixed with the cut-cover algebra:
it is a rho-label exclusion check on the active prefixes.

## Semicomplete Cut Trichotomy

Let `C` be any split semicomplete core and suppose

    d_C^+(Q0) = 0.

Put `O = V(C) \ Q0`.  For any nontrivial cut `S`, write

    A = S cap Q0,
    B = S cap O.

Exactly one of the following holds.

### Internal Cuts

If `S subseteq Q0`, then

    d_C^+(S) = d_{C[Q0]}^+(S).

So internal deficient cuts are exactly low out-cuts inside the sealed
middle block.

For the D42 profile, the only proper internal low cut is the
one-head-deleted prefix `Q-`.  D63 shows this cut can become non-low
after adding a reverse head arc, so it must be included only when its
actual out-size is below two.

### External-Prefix Cuts

If `Q0 subseteq S`, write `S = Q0 union B`.  Since `Q0` has no exits,

    d_C^+(S) = d_{C[O]}^+(B).

Thus external deficient cuts are exactly low out-cuts in the outside
side after adjoining the sealed prefix.  In D42 and D63, the only such
cut is the first-successor prefix `Q+`.

### Mixed Cuts

If `S` is neither contained in nor contains `Q0`, then `B` and
`Q0 \ A` are both nonempty.  The cut has the exact decomposition

    d_C^+(A union B)
      = d_{C[Q0]}^+(A, Q0 \ A)
        + d_{C[O]}^+(B, O \ B)
        + d_C^+(B, Q0 \ A).                     (M)

There is no `A -> O` term because `d_C^+(Q0)=0`.

Since `C` is semicomplete and `Q0` has no exits, every pair
`b in B`, `q in Q0 \ A` has at least one arc `b -> q`.  Therefore

    d_C^+(B, Q0 \ A) >= |B| |Q0 \ A|.            (LB)

Consequently, a mixed cut below two can only be a single-exchange cut:

    |B| = 1 and |Q0 \ A| = 1.

Writing `B={w}` and `Q0 \ A={h}`, such a cut has

    d_C^+((Q0 \ {h}) union {w})
      = d_{C[Q0]}^+(Q0 \ {h}, {h})
        + d_{C[O]}^+({w}, O \ {w})
        + d_C^+({w}, {h}).

The last term is at least one.  Thus a deficient mixed cut can occur
only if both local terms vanish:

    d_{C[Q0]}^+(Q0 \ {h}, {h}) = 0,
    d_{C[O]}^+({w}, O \ {w}) = 0.                (EX)

This is the single-exchange obstruction.  Proving no other split-core
cut is deficient is therefore reduced to:

1. classify low internal cuts of `C[Q0]`;
2. classify low external-prefix cuts of `C[O]`;
3. exclude the single-exchange obstruction (EX).

## Audit

The executable audit verifies this reduction on the original D42 core
and the D63 reverse-head perturbation.

For D42:

    low internal: Q- with out-edge (2,6)
    zero middle:  Q0
    low external: Q+ with out-edge (10,23)
    mixed low:    none
    minimum mixed out-size: 3

For the D63 perturbation:

    low internal: none
    zero middle:  Q0
    low external: Q+
    mixed low:    none
    minimum mixed out-size: 4

The audit checks formula (M) on all `520065` mixed cuts in each core and
asserts that every single-exchange cut has out-size at least two.

## Consequence

D65 narrows the remaining structural proof.  The cut-cover algebra is
D64, and the global cut enumeration is reduced to local semicomplete
facts around the sealed zero prefix.

The next target is now:

> Prove the local internal/external/single-exchange conditions from the
> sealed-block, CL, DT, cage-hook, and shortest-path hypotheses.

In particular, the proof no longer needs an exact `1,0,1` profile.
It needs only the actual low internal and external prefixes, plus the
absence of the single-exchange obstruction.
