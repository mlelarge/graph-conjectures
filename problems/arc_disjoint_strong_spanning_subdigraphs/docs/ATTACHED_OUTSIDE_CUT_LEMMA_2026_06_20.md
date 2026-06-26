# D75: Attached Outside-Cut Lemma

Date: 2026-06-20.

Artifact: `scripts/attached_outside_cut_audit.py`.

## Purpose

D74 refuted W2 as a primitive consequence of sealed-block/CL/DT:
`C[O \ {w1}]` need not be 2-arc-strong.  The failure was harmless for
FSQ because the weak outside-core cut also exits to the first successor
`w1`.

This note replaces D72's W2-based outside-core certificate with the exact
attachment-aware certificate needed for FSQ.

## Statement

Let `O` be the outside quotient, let `w1 in O` be the first successor,
and put

    O' = O \ {w1}.

Assume:

**AOC-1, one first-successor exit.**

    d^+_{C[O]}({w1}) = 1.

**AOC-2, cuts not containing `w1`.**  For every nonempty
`B subseteq O'`,

    d^+_{C[O']}(B) + |A_C(B,{w1})| >= 2.

The case `B=O'` is included; it is exactly the two-return condition.

**AOC-3, cuts containing `w1`.**  For every nonempty proper
`A subset O'`,

    d^+_{C[O']}(A) + |A_C({w1}, O' \ A)| >= 2.

Then FSQ holds: the only nonempty proper outside cut in `C[O]` with
out-size below two is `{w1}`, and its actual outside out-size is one.

## Proof

Let `S` be a nonempty proper subset of `O`.

If `S={w1}`, then AOC-1 gives the allowed singleton low cut, with one
actual exit.

If `w1 notin S`, then `S subseteq O'` and the exits of `S` inside `O`
are exactly

    A_C(S, O' \ S) union A_C(S,{w1}).

AOC-2 gives at least two such exits.  This also covers the case
`S=O'`, where the first term is empty and the exits are exactly the
returns to `w1`.

If `w1 in S` and `S != {w1}`, write

    S = {w1} union A

with `empty != A proper subset O'`; the case `A=O'` would give
`S=O`, not a proper cut.  The exits of `S` inside `O` are exactly

    A_C(A, O' \ A) union A_C({w1}, O' \ A).

AOC-3 gives at least two such exits.

Therefore every outside cut other than `{w1}` has at least two exits,
and `{w1}` has exactly one.  This is FSQ.  QED.

## Relation To D72

D72's certificate was:

    d^+({w1}) = 1,
    lambda(C[O']) >= 2,
    |A_C(O',{w1})| >= 2.

That certificate implies AOC-1 and AOC-2.  It also implies AOC-3 only
after discarding the helpful `w1`-exit term.  D74 shows this discard is
too expensive: a cut can have only one exit inside `O'` and still be
safe because the missing exit is supplied by the attachment to `w1`.

Thus D72 remains a valid sufficient route, but it is not the right
primitive target.

## Audit

The audit checks eight variants:

    D42 original,
    D63 reverse-head,
    D66 rho-entry,
    D63 + D66 combined,
    D74 support reversal,
    D74 + D63,
    D74 + D66,
    D74 + D63 + D66.

All preserve the sealed-chain gates and `lambda(D-bullet)=lambda(host)=3`.
All satisfy

    w1_exits = [(10,23)],
    low_outside = [({10}, [(10,23)])].

For the original D42/D63/D66 cases, the tight AOC rows are not the W2
obstruction:

    min_no_w1   = {23}, with exits (23,21),(23,22);
    min_with_w1 = O' \ {14}, with exits (15,14),(16,14).

For the D74 reversal variants, the certificate is tight exactly at the
new weak core cut:

    min_no_w1   = {12}, with exits (12,23) and (12,10);
    min_with_w1 = {12}, with exits (12,23) and (10,23).

This explains why W2 fails while FSQ survives.

## Next Primitive Target

The live outside primitive is now AOC, not W2.  A symbolic proof should
derive AOC-1..3 from the sealed-chain classification, CL maximality, DT
support vertices, semicompleteness, and the shortest-path no-shortcut
constraints.

In particular, the proof must keep the `w1` attachment terms visible:
removing them reproduces the false W2 demand.
