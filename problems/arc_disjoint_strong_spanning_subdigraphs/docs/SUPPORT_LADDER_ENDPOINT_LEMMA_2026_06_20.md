# D79: Support-Ladder Endpoint Lemma

Date: 2026-06-20.

Artifacts:

* `scripts/top_support_clause_audit.py`;
* `scripts/top_support_dt_gap_audit.py`.

## Purpose

D78 shows that the current DT theorem does not imply the top-support
two-exit clause.  This note states the strengthened local primitive that
does imply it, and records the short proof.

## Support-Ladder Endpoint Primitive

Let `O` be the outside quotient and let `w1` be the first successor
outside the sealed zero prefix.  Put

    O' = O \ {w1}.

Assume `{w1}` is active, so its only outside exit is

    w1 -> tau,        tau in O'.

The strengthened endpoint primitive is:

**SLE, support-ladder endpoint.**  The vertex `tau` entered by `w1` is
the top of a nonterminal outside support two-fan.  That is, there are
distinct vertices `s1,s2 in O' \ {tau}` such that

    tau -> s1,    tau -> s2.

The vertices `s1,s2` are lower support vertices in the distance-graded
outside support ladder.

## Lemma

SLE implies the D77 top-support clause:

    d^+_{C[O']}({tau}) >= 2.

### Proof

Both arcs `tau -> s1` and `tau -> s2` have tail `tau`, heads in `O'`,
and heads outside the singleton `{tau}`.  Since `s1 != s2`, they are two
distinct arcs leaving `{tau}` inside `C[O']`.  Hence

    d^+_{C[O']}({tau}) >= 2.

QED.

## Why This Is The Right Primitive

In the D42 host labels,

    tau = 23,
    {s1,s2} = {21,22},

and the two support arcs are

    23 -> 21,    23 -> 22.

D76's only AOC failures are exactly the two variants that reverse one of
these arcs:

    23 -> 21  becomes  21 -> 23,
    23 -> 22  becomes  22 -> 23.

D78 shows those variants keep the current DT profile unchanged.  Thus
SLE is not redundant with DT as presently written; it is the endpoint
orientation clause that the DT/root-spare support story must supply.

## Consequence For AOC

D75 proves AOC implies FSQ.  D76-D78 show that any proof of AOC must
keep the support-ladder endpoint visible.  D79 supplies the endpoint
step:

    SLE => top-support two-exit.

The remaining AOC proof can now assume this endpoint clause and focus on
non-terminal outside cuts in `O'`, using the attachment terms to and from
`w1` exactly as in D75.

## Next Target

Prove the full AOC inequalities under the strengthened primitive package:

1. AOC-1: `w1` has its single allowed outside exit `w1 -> tau`;
2. SLE: `tau` has two lower support exits in `O'`;
3. nonterminal support expansion: every other nonempty outside cut has
   either two exits inside `O'`, or one exit inside `O'` plus an
   attachment to/from `w1`.

D79 closes item 2.  Item 3 is now the remaining outside-cut proof.
