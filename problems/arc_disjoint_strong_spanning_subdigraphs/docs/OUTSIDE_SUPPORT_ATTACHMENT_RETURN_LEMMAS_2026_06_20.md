# D82: Outside Support Attachment And Root Return

Date: 2026-06-20.

Artifact: `scripts/outside_support_clause_audit.py`.

## Purpose

D81 reduced AOC to the endpoint-reduced package ER-0--ER-4.  This note
proves the two named nonterminal clauses that do not require a global
residual separator theorem:

* weak middle-support attachment;
* root-complement return.

The remaining clause after this note is ER-4: residual outside-support
expansion, i.e. no other AOC row has value two.

## Notation

Keep the notation from D81:

    O = {w1} disjoint_union O',

`w1 -> tau` is the unique outside exit of the active first successor,
and

    eta(B)  = d^+_{C[O']}(B) + |A_C(B,{w1})|,
    zeta(A) = d^+_{C[O']}(A) + |A_C({w1},O'\A)|.

The outside quotient is semicomplete.

## First-Successor Attachment Lemma

Assume `w1` is active and has the unique outside exit

    w1 -> tau.

Then every `x in O' \ {tau}` has an arc

    x -> w1.

### Proof

Fix `x in O' \ {tau}`.  Since the outside quotient is semicomplete, at
least one of the arcs between `w1` and `x` is present.  The arc
`w1 -> x` is impossible because `w1 -> tau` is the unique outside exit
of `w1` and `x != tau`.  Hence the semicomplete pair is oriented back as
`x -> w1`.  QED.

This is the symbolic source of the `m -> w1` attachment in the D74 row;
it is not a separate ad hoc edge.

## Middle-Support Attachment Lemma

Let `m in O' \ {tau}` be a weak middle-support singleton.  Assume the
support ladder supplies its forward support arc

    m -> tau,

and that the endpoint fan from SLE has distinct lower heads

    tau -> s1,    tau -> s2,

with `s1,s2 notin {m,tau}`.

Then the middle rows satisfy

    eta({m}) >= 2,
    zeta({m}) >= 2,
    zeta({m,tau}) >= 2.

If the middle singleton is clean, meaning `m -> tau` is its only exit
inside `C[O']` and the endpoint fan contributes exactly the two counted
exits from `{m,tau}`, then these three inequalities are equalities.

### Proof

By the first-successor attachment lemma, `m -> w1`.  Therefore
`eta({m})` counts at least the two arcs

    m -> tau,    m -> w1.

For `zeta({m})`, the first-successor exit `w1 -> tau` is counted because
`tau notin {m}`.  Together with `m -> tau`, this gives two counted arcs:

    m -> tau,    w1 -> tau.

For `zeta({m,tau})`, the arc `w1 -> tau` is internal to
`{w1,m,tau}` and is no longer counted.  The two SLE endpoint arcs leave
the pair because `s1,s2 notin {m,tau}`:

    tau -> s1,    tau -> s2.

Thus the three middle rows have value at least two.  Under the stated
cleanliness assumptions there are no additional counted arcs in these
rows, so the values are exactly two.  QED.

## Root-Complement Return Lemma

Let `r0 in O' \ {tau}` be the root-side outside vertex.  Assume the
root/spare support package supplies two distinct predecessors
`p1,p2 in O' \ {r0}` with

    p1 -> r0,    p2 -> r0.

Put

    R = O' \ {r0}.

Then

    zeta(R) >= 2.

If the root-complement row is clean, meaning the only counted exits from
`R` to `{r0}` are `p1 -> r0` and `p2 -> r0`, then

    zeta(R) = 2.

### Proof

Since `r0 != tau` and `w1 -> tau` is the unique outside exit of `w1`,
there is no arc `w1 -> r0`.  Thus the attachment term in `zeta(R)` is
zero:

    |A_C({w1}, O'\R)| = |A_C({w1},{r0})| = 0.

The two root/spare predecessor arcs both leave `R` inside `C[O']` and
enter the omitted vertex `r0`.  Hence

    d^+_{C[O']}(R) >= 2,

so `zeta(R) >= 2`.  Under the cleanliness assumption these are exactly
the two counted exits, giving equality.  QED.

## Consequence For ER-2 And ER-3

The middle-support attachment lemma proves the lower-bound part of
ER-2, and proves the exact D81 tight rows when the middle singleton is
clean.  The root-complement return lemma proves the lower-bound part of
ER-3, and proves the exact co-root tight row when the root-complement
row is clean.

In the D42 labels audited by the script:

    w1 = 10,    tau = 23,    m = 12,    r0 = 14,
    {p1,p2} = {15,16},    {s1,s2} = {21,22}.

The audit verifies, across D42, D63, D66, D63+D66, and the D74 support
reversal variants:

* `w1_exits = ((10,23),)`;
* every vertex in `O' \ {23}` returns to `10`;
* in the weak middle variants, `12 -> 23` and `12 -> 10`;
* `15 -> 14` and `16 -> 14`;
* after excluding the D81 named rows, every remaining AOC row has value
  at least three.

## Remaining Target

ER-4 is now the only nonterminal endpoint-reduced clause not proved in
this note.  Its exact target is:

* every nonempty `B subseteq O'`, except the endpoint singleton and the
  optional weak middle singleton, has `eta(B) >= 3`;
* every nonempty proper `A subset O'`, except the endpoint singleton,
  the optional middle rows, and the root-complement row, has
  `zeta(A) >= 3`.

This should be proved as a residual support-ladder separator theorem:
any unlisted outside row must cross either a three-arc ladder boundary,
or a two-fan boundary plus the forced first-successor attachment.  The
D82 audit confirms this statement on the current normal forms, but the
symbolic derivation from sealed-block/CL/DT remains the next target.
