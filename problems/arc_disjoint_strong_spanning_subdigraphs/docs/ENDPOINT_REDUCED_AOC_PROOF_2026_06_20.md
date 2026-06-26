# D81: Endpoint-Reduced AOC Proof

Date: 2026-06-20.

Inputs:

* `docs/ATTACHED_OUTSIDE_CUT_LEMMA_2026_06_20.md`;
* `docs/SUPPORT_LADDER_ENDPOINT_LEMMA_2026_06_20.md`;
* `docs/ENDPOINT_REDUCED_AOC_PROFILE_2026_06_20.md`.

## Purpose

D80 isolated the tight outside rows that remain after the
support-ladder endpoint `tau` is protected by SLE.  This note proves the
endpoint-reduced AOC profile symbolically from the strengthened local
outside-support package.

The result is deliberately conditional on the remaining expansion
primitive.  D76-D78 show that the old sealed-chain/DT checks alone do
not imply it; the endpoint and nonterminal support clauses have to stay
visible.

## Notation

Let `C` be the local outside quotient.  Write

    O = {w1} disjoint_union O',

where `w1` is the first outside successor.  For `B subseteq O'` define

    eta(B) = d^+_{C[O']}(B) + |A_C(B,{w1})|,

and for `A subset O'` define

    zeta(A) = d^+_{C[O']}(A) + |A_C({w1},O'\A)|.

Thus AOC is exactly:

    d^+_{C[O]}({w1}) = 1,
    eta(B) >= 2       for every nonempty B subseteq O',
    zeta(A) >= 2      for every nonempty proper A subset O'.

Let `tau in O'` be the head of the unique outside exit from `w1`.
There may also be one weak middle-support vertex `m`; if it is absent,
all clauses involving `m` are ignored.  Finally let `r0 in O'` be the
root-side vertex whose complement gives the co-root row.

In the D42 labels used by the audits,

    w1 = 10,    tau = 23,    r0 = 14,

and in the D74 support-reversal variants the optional weak middle vertex
is

    m = 12.

## Endpoint-Reduced Support Package

The package has five clauses.

**ER-0, active first successor.**

The only outside exit of `w1` is

    w1 -> tau.

Equivalently,

    d^+_{C[O]}({w1}) = 1.

**ER-1, endpoint two-fan.**

There are distinct vertices `s1,s2 in O' \ {tau}` such that

    tau -> s1,    tau -> s2.

For the exact tight-row profile, the counted endpoint row is clean:

    eta({tau}) = zeta({tau}) = 2.

The lower bound is the SLE consequence from D79; the equality is the
endpoint-cleanliness part observed in the D80 normal forms.  Only the
lower bound is needed for AOC; equality is used to identify the exact
tight-row profile.

**ER-2, optional middle-support attachment.**

If the weak middle vertex `m` exists, then

    m -> tau,    m -> w1,    w1 -> tau,

and the singleton middle rows are clean:

    eta({m}) = 2,    zeta({m}) = 2.

Also the endpoint two-fan leaves the pair `{m,tau}` cleanly:

    zeta({m,tau}) = 2.

In the D74 labels these are the rows repaired by `(12,23)+(12,10)`,
`(12,23)+(10,23)`, and then by the two exits from `23`.

**ER-3, root-complement return.**

For the co-root row

    R = O' \ {r0},

there are two counted exits from `R` to `r0`, and no additional counted
exit from `w1` to `r0`:

    zeta(R) = d^+_{C[O']}(R) = 2.

In the D42 labels these exits are `(15,14)` and `(16,14)`.

**ER-4, residual outside-support expansion.**

Every row not named above has slack at least three:

    eta(B) >= 3

for every nonempty `B subseteq O'` except `B={tau}` and, when `m`
exists, `B={m}`; and

    zeta(A) >= 3

for every nonempty proper `A subset O'` except `A={tau}`,
`A=O'\{r0}`, and, when `m` exists, `A={m}` and `A={m,tau}`.

This is the nonterminal support-expansion assertion that still has to be
derived from the sealed-block/CL/DT primitives.  It is stronger than AOC
only on residual rows; on the named rows the attachment and endpoint
clauses above give the exact value two.

## Lemma

Under ER-0--ER-4, AOC holds.  Moreover the AOC rows of value exactly two
are precisely the endpoint-reduced rows:

* if no weak middle vertex exists:

      eta-tight rows:  {tau}
      zeta-tight rows: {tau}, O'\{r0};

* if the weak middle vertex `m` exists:

      eta-tight rows:  {m}, {tau}
      zeta-tight rows: {m}, {tau}, {m,tau}, O'\{r0}.

## Proof

ER-0 is exactly AOC-1.

Now let `B` be a nonempty subset of `O'`.  If `B={tau}`, ER-1 gives
`eta(B)=2`.  If the weak middle vertex exists and `B={m}`, ER-2 gives
`eta(B)=2`.  Every other nonempty `B subseteq O'` is residual, so ER-4
gives `eta(B)>=3`.  Therefore AOC-2 holds for every nonempty `B`, and
the only `eta`-rows of value two are the stated singleton rows.

Next let `A` be a nonempty proper subset of `O'`.  If `A={tau}`, ER-1
gives `zeta(A)=2`.  If the weak middle vertex exists and `A={m}`, ER-2
gives `zeta(A)=2`: the internal support exit is `m -> tau`, and the
attachment term contributes `w1 -> tau` because `tau notin {m}`.  If
`A={m,tau}`, ER-2 gives `zeta(A)=2`; here the `w1 -> tau` arc is internal
to `{w1} union A`, so the two counted exits are the endpoint exits from
`tau`.  If `A=O'\{r0}`, ER-3 gives `zeta(A)=2`.  Every other nonempty
proper `A subset O'` is residual, so ER-4 gives `zeta(A)>=3`.

Thus AOC-3 holds for every nonempty proper `A`, and the only
`zeta`-rows of value two are exactly the listed rows.

Combining AOC-1, AOC-2, and AOC-3 proves AOC.  The exact tight-row
profile follows at the same time from the equalities in ER-1--ER-3 and
the strict residual slack in ER-4.  QED.

## Consequence

D75 proves that AOC implies FSQ: the only outside cut in `C[O]` with
out-size below two is the permitted singleton `{w1}`.  Therefore
ER-0--ER-4 imply FSQ.

This proof also explains why W2 was the wrong target.  A weak middle
support singleton may have only one exit inside `C[O']`; AOC remains
true because the missing count is supplied by the attachment to or from
`w1`.

## Remaining Derivation Target

The endpoint-reduced AOC proof is now reduced to deriving ER-2--ER-4
from the primitive local structure:

1. middle-support attachment for every weak middle singleton;
2. root-complement return for every co-root row;
3. residual outside-support expansion, giving slack at least three on
   all unlisted outside rows.

D79 supplies the endpoint lower bound in ER-1, while the endpoint
cleanliness equality is only needed for exact tightness.  The open work
is to derive the nonterminal clauses from the sealed-block
classification, CL maximality, DT support vertices, semicompleteness,
and shortest-path no-shortcut constraints.
