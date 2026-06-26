# D59: Prefix Profile Audit and D58 Correction

Date: 2026-06-18.

Artifact: `scripts/chain_prefix_profile_audit.py`.

## Purpose

D58 tried to promote the D53 sufficient feed predicate into the
connectivity half of the Prescribed Pending Missing Entry Lemma.  The
new prefix-profile audit shows that this promotion is too strong.

The correct state is:

* the symbolic prefix-cut substitute obstruction from D58 Lemma 1 is
  still valid;
* the D53 three-cut repair from D58 Lemma 3 is still valid as a
  sufficient criterion;
* D58 Lemma 2 is not proved, because 3-arc-strongness only forces the
  deficient prefix cuts to be repaired somehow, and the D42 prefix-lift
  table has repair paths beyond `{u, heads} -> chainK`.

## Audited D42 Prefix Profile

The audit recomputes the D42 split core from the checked witness and
prints all cuts of split-core out-size at most one.  There are exactly
three:

    Q- = {2,3,4,5,7,8}          out-size 1,
    Q0 = {2,3,4,5,6,7,8}        out-size 0,
    Q+ = {2,3,4,5,6,7,8,10}     out-size 1.

Here the pending host vertices are `(9,11,13)`.  A pending path
`x -> s -> y` repairs one of these cuts precisely when `x` is in the cut
and `y` is outside it.  The audit reports the following repair-region
profiles.

For `Q-`:

    {('heads','chainK'):2,
     ('heads','heads'):1,
     ('u','chainK'):3,
     ('u','heads'):2,
     ('v','chainK'):1}

For `Q0`:

    {('heads','chainK'):4,
     ('u','chainK'):3,
     ('v','chainK'):1}

For `Q+`:

    {('chainK','chainK'):1,
     ('heads','chainK'):2,
     ('u','chainK'):2}

The D53 feed predicate uses only the subfamily
`{u, heads} -> chainK`.  This is a clean sufficient subfamily, but it is
not the whole prefix-lift profile.

## Symbolic Consequences

The middle cut `Q0` has out-size zero in the split core because the
sealed block `B* = C union Heads union {v}` has no residual split-core
exit after the forced `I` vertices are deleted.  Therefore any final
pending choice must put at least two repairing split arcs across `Q0` if
the split core is to become 2-arc-strong.

The prefix-lift table is broader than D58 assumed.  It includes repair
paths with source on the original chain, for example the D42-local
`v -> i1 -> w1` repair of `Q-` and `Q0`, and a later
`chainK -> i_r -> chainK` repair of `Q+`.  Thus
`lambda(D^bullet) >= 3` can witness the missing prefix exits through
original-chain repairs, not only through feeds from `{u} union Heads`.

The two out-size-one cuts are D42-local tight cuts:

* `Q-` is the omitted-head prefix cut; it keeps one old split-core exit.
* `Q+` is the first-successor prefix cut; it also keeps one old
  split-core exit.

These tightness statements are useful facts about the D42 prefix model,
but they are extra profile hypotheses until derived from the general
sealed-block and CL/DT chain-kernel axioms.

## Correction to D58

D58 Lemma 1 remains a valid obstruction for the specific kind of
non-feed substitute arc treated there: if a substitute from a forbidden
tail repairs an early deficient prefix cut, then either it does not
actually cross the cut, it gives a cage vertex a path to `rho` in `D-u`,
or it creates a forbidden shortcut on the unique sealed `v -> rho`
path.

D58 Lemma 3 remains valid as a conditional repair lemma: if a pending
choice contains one `u -> chainK` split path and a second split path from
`u` or `Heads` into a distinct chain successor, then the three D53 cuts
are repaired and the D42 split core has `lambda >= 2`.

D58 Lemma 2 should be replaced.  There are two viable replacements:

1. Prove a broader cut-cover selection lemma using the full repair table
   above, allowing `v -> chainK` and `chainK -> chainK` repairs when the
   sealed-kernel hypotheses permit them.
2. Prove a stronger structural lemma that specifically forces the D53
   sufficient subfamily: two distinct `{u, heads} -> chainK` feeds, at
   least one from `u`.

The Prescribed Pending Missing Entry Lemma therefore has a proved
sufficient criterion, but not yet a general existence proof.

## Next Target

Derive the exact necessary-and-sufficient cut-cover inequalities for
the three deficient cuts from this audit table.  Then prove that the
chain-kernel hypotheses force at least one admissible pending choice
satisfying those inequalities, possibly using the broader repair table
rather than the D53 sufficient predicate.

