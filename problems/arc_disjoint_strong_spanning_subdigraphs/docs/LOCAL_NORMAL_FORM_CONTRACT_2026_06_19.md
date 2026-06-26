# D68: Local Normal-Form Contract

Date: 2026-06-19.

Artifact: `scripts/local_normal_form_audit.py`.

## Purpose

D65 reduces the global low-cut problem to three local questions around
the sealed zero prefix `Q0`.  D67 handles the one-sided endpoint
bookkeeping.  This note states a local normal-form contract that is
sufficient to finish the D65 structural profile.

The contract is intentionally explicit: it separates what is now a
finite local lemma from the still-open task of deriving that local lemma
from the written sealed-block/CL/DT notes.

## Local Objects

Let

    Q0 = C union H union {v}

where:

* `C=C_u` is the cage;
* `H` is the head block of escaped `AV_u` heads kept inside the sealed
  middle block;
* `v` is the first vertex of the sealed shortest path;
* `O = V(C_core) \ Q0` is the outside core.

Let `w1` be the first chain successor outside `Q0`.

The D42 host-label instance has

    C={2,3,4,5},   H={6,7},   v=8,   w1=10.

## Contract

The local normal-form contract is:

**LNF-0.** `Q0` is a zero prefix: `d^+(Q0)=0`.

**LNF-1.** The only proper internal cuts of `C_core[Q0]` with out-size
below two are one-head-deleted cuts `Q0 \ {h}`.  Such a cut is included
as active only when its actual out-size is one.

**LNF-2.** The only nonempty proper outside cut `B subset O` with
out-size below two in `C_core[O]` is `{w1}`.  Hence the only possible
low external-prefix cut is `Q0 union {w1}`, again included only when its
actual out-size is one.

**LNF-3.** For every `h in Q0` and `w in O`, the single-exchange cut

    (Q0 \ {h}) union {w}

has out-size at least two.

**LNF-4.** Active prefixes have no rho-label exits.  Rho-label entries
are irrelevant by D67.

## Consequence

Assuming LNF-0 through LNF-4, the monotone deficient-prefix profile
follows.

### Proof

By D65, every split-core cut is internal, external-prefix, or mixed.

Internal cuts are handled by LNF-1: the only candidates below two are
one-head-deleted prefixes, and D64 keeps only those whose actual demand
`max(0,2-b(Q))` is positive.

External-prefix cuts are handled by LNF-2: the only candidate below two
is the first-successor prefix `Q0 union {w1}`, again retained only when
its actual demand is positive.

Mixed cuts are reduced by D65 to single-exchange cuts.  LNF-3 excludes
all of them.

Finally, LNF-4 and D67 give the prefix-plus-pending formula for every
active prefix.  Combining D67 with D64 gives the pending cut-cover
selection and repairs the split core to `lambda >= 2`.  QED.

## Why LNF-3 Is Local

For a single-exchange cut, D65 gives the exact formula

    d^+((Q0 \ {h}) union {w})
      = d^+_{Q0}(Q0 \ {h}, {h})
        + d^+_O({w}, O \ {w})
        + d^+({w}, {h}).

The last term is at least one by semicompleteness and `d^+(Q0)=0`.
Thus the only way a single-exchange cut could be deficient is if both
local terms vanished:

    d^+_{Q0}(Q0 \ {h}, {h}) = 0,
    d^+_O({w}, O \ {w}) = 0.

So excluding single-exchange cuts is not a global cut problem.  It is
equivalent to saying that no head/core vertex `h` is simultaneously
unentered from `Q0 \ {h}` while some outside vertex `w` is a sink in
`O`.

In D42, the minimum single-exchange cut is

    (Q0 \ {6}) union {10}

with three exits

    (2,6), (10,6), (10,23).

The D63 reverse-head perturbation only adds another exit `(7,6)`.

## Audit

The executable audit checks D42 and the corrected variants:

    D42 original,
    D63 reverse-head,
    D66 rho-entry,
    D63 + D66 combined.

Results:

* D42 and D66 have one internal low cut:

      Q- = {2,3,4,5,7,8},   out-edge (2,6).

* D63 and D63+D66 have no internal low cut; the reverse head arc adds
  `(7,6)`.

* All four variants have the same external low cut:

      Q0 union {10},        outside out-edge (10,23).

* No variant has a single-exchange low cut.  The minimum
  single-exchange out-size is `3` in D42/D66 and `4` in D63/D63+D66.

* D66 variants have endpoint entries into `Q0,Q+`, but no endpoint
  exits, as required by D67.

## Remaining Symbolic Work

D68 proves that LNF-0 through LNF-4 are sufficient.  It does not claim
that the current written CL/DT notes already prove LNF-1 and LNF-2.
Those notes establish the sealed boundary and forced-chain form, but
they do not yet spell out the head-block quotient or the outside
first-successor quotient as named consequences.

The next symbolic target is therefore exactly:

1. derive LNF-1 from cage hooks, cage packing, `AV_u` heads, and the
   shortest-path orientation of the head block;
2. derive LNF-2 from the CL forced-chain classification plus the DT
   support vertices entering `W`;
3. derive LNF-3 from the singleton forms in LNF-1 and LNF-2.

Once these are written, the structural monotone deficient-prefix profile
will be closed at the level needed by D64/D67.
