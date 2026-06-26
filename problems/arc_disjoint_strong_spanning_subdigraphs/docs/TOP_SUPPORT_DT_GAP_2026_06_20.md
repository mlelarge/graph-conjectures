# D78: Top-Support Is Not A Consequence Of Current DT

Date: 2026-06-20.

Artifact: `scripts/top_support_dt_gap_audit.py`.

## Purpose

D77 identified the top-support two-exit clause as the endpoint primitive
needed for AOC:

    if w1 -> tau is the unique first-successor outside exit, then
    d^+_{O'}({tau}) >= 2.

The natural next thought was to prove this from DT/root-spare support.
This note separates the current DT theorem from the stronger
support-ladder endpoint needed here.

## Audit

Compare D42 with the two D76 top-support reversals:

    (22,20) -> (20,22),
    (22,21) -> (21,22).

All three have the same DT profile:

    P_v = (7,8,9,10,11,12,13,rho),
    R = {13,14,15},
    R cap P_v = {13},
    R cap X_P = {14,15}.

Thus the existing DT theorem still holds unchanged: the two off-path
rho-tails remain in `X_P`, and the distinct-tail conclusion is intact.

But the top-support endpoint changes:

* in D42, `tau=23` has exits `(23,21),(23,22)`;
* after `(22,20)->(20,22)`, `tau=23` has only `(23,22)`;
* after `(22,21)->(21,22)`, `tau=23` has only `(23,21)`.

The two reversed variants fail both top-support and AOC, and by D76 they
still preserve the checked sealed-chain gates and a repaired hard
gateway.

## Conclusion

The current DT theorem does not imply top-support two-exit.  It controls
rho-tail exits from `X_P`; it does not control the orientation of the
outside support fan reached by the first successor.

The needed proof target is therefore a strengthened support-ladder
endpoint clause:

> In a genuine sealed multi-crossing block, the support vertex `tau`
> entered by the first-successor exit belongs to a downward two-fan in
> `O'`.

Equivalently, the D76 bad reversals must be excluded by an explicit
distance-graded support-ladder primitive, not by DT as currently stated.

## Next Target

State and prove a **support-ladder endpoint lemma**:

1. `w1 -> tau` enters the first outside support vertex of a nonterminal
   `W` segment;
2. the support-ladder construction supplies two lower support vertices
   `r1,r2 in O'`;
3. the orientations are `tau -> r1` and `tau -> r2`;
4. reversing either orientation creates a forbidden terminal support
   singleton, hence violates the strengthened support-ladder hypothesis.

This lemma is enough to recover the D77 top-support clause.  It is also
the right local primitive to use inside the eventual AOC proof.
