# D83: Residual Ladder Separator For ER-4

Date: 2026-06-20.

Artifact: `scripts/residual_ladder_separator_audit.py`.

## Purpose

D81 reduced AOC to ER-0--ER-4.  D82 proved the named middle-support and
root-complement rows.  This note proves the remaining clause, ER-4, at
the support-ladder normal-form level: every unlisted AOC row has value
at least three.

The proof uses a directed ladder skeleton contained in the outside
quotient.  Extra semicomplete arcs only increase the counted cut values,
so it is enough to prove the residual inequalities on this skeleton.

## Ladder Skeleton

Use the D81 notation

    O = {w1} disjoint_union O',

and let the outside support blocks be

    M = {m},        T = {tau},       S = {s1,s2},
    H = {h1,h2},    L = {ell1,ell2}, P = {p1,p2},
    R = {r0}.

The cyclic support order is

    M -> T -> S -> H -> L -> P -> R -> M.

The skeleton consists of the following arcs.

**Attachment arcs.**

    w1 -> tau,
    x -> w1          for every x in O' \ {tau}.

**Forward ladder arcs.**

    m -> tau,
    tau -> s1, tau -> s2,
    S -> H,
    H -> L,
    L -> P,
    P -> r0.

Here `S -> H`, `H -> L`, and `L -> P` mean all four arcs between the two
two-vertex blocks; `P -> r0` means both `p1 -> r0` and `p2 -> r0`.

**Support shortcuts.**

The skeleton also keeps the shortcut arcs supplied by the support
normal form:

    S -> M,
    H -> T,
    L -> M,T,S,
    P -> M,T,S,H,
    R -> M,T,S,H,L,

together with one internal forward arc in each two-vertex block
`S,H,L`, and both internal arcs in `P`.

In the non-weak middle case there is one extra middle support arc

    m -> h1.

In the weak middle case this extra arc is absent; that is exactly the
D74 middle-support row.

The D42 labels are

    m=12, r0=14, P={15,16}, L={17,18},
    H={19,20}, S={21,22}, tau=23.

## Skeleton Separator Lemma

On the ladder skeleton:

1. every nonempty `B subseteq O'`, except `B={tau}` and, in the weak
   middle case, `B={m}`, satisfies `eta(B) >= 3`;
2. every nonempty proper `A subset O'`, except `A={tau}`,
   `A=O'\{r0}`, and, in the weak middle case, `A={m}` and
   `A={m,tau}`, satisfies `zeta(A) >= 3`.

### Proof

First consider `eta`.  Every vertex of `O' \ {tau}` has the attachment
arc back to `w1`.  Hence any `B` containing at least three vertices
outside `{tau}` already has `eta(B) >= 3` from attachment arcs alone.

So a possible residual failure has at most two vertices outside
`{tau}`.  If `B={tau}`, it is the named endpoint row.  If the weak middle
case has `B={m}`, it is the named middle row.  All remaining small cases
have enough ladder exits:

* a robust singleton `{m}` has `m -> tau`, `m -> h1`, and `m -> w1`;
* any other singleton outside `{tau}` has at least two skeleton exits
  inside `O'` and the attachment to `w1`;
* any two-set not containing `tau` has two attachment arcs and at least
  one ladder exit, since no two vertices form a terminal class in the
  cyclic skeleton;
* any set `{tau,x}` has the attachment `x -> w1` and at least two
  ladder exits, unless it is the weak named row `{m,tau}` in the zeta
  direction; for eta even `{m,tau}` has the two endpoint exits plus
  `m -> w1`.

Thus every unlisted eta row has value at least three.

Now consider `zeta`.  If `tau notin A`, then the attachment term counts
`w1 -> tau`.  The ladder skeleton on `O' \ {tau}` has no one-exit
proper cut, except the weak singleton `{m}`.  Therefore every unlisted
row with `tau notin A` has

    zeta(A) >= 1 + 2 = 3.

The weak singleton `{m}` is exactly the named middle row.

It remains to handle `tau in A`.  The attachment term is then zero, so
we must count exits inside `O'`.  Walk around the cyclic ladder from

    T -> S -> H -> L -> P -> R -> M -> T.

If `A` first fails to contain a whole next block at one of the
boundaries `S -> H`, `H -> L`, or `L -> P`, then the complete two-by-two
boundary gives at least four exits.  If the first missing block is `S`,
then `tau -> s1,tau -> s2` gives the two endpoint exits; this is tight
only for the named endpoint row `{tau}` and, in the weak middle case,
for `{m,tau}`.  Any additional nonterminal block in `A` supplies another
shortcut or ladder exit.  If the first missing block is `R`, the
boundary `P -> R` gives exactly two exits only when

    A = O' \ {r0},

the named root-complement row; otherwise another omitted block creates
an additional ladder boundary.  Finally, if `R` is in `A` but `M` is
missing, the shortcut package `R -> M,T,S,H,L` and the incoming support
from the preceding blocks give at least three exits to the omitted
part.

Thus every tau-containing zeta row not already named has at least three
exits.  This proves the skeleton separator lemma.  QED.

## ER-4

The actual outside quotient contains the ladder skeleton.  The audit
checks this containment on D42, D63, D66, D63+D66, and the D74 support
reversal variants.  Since eta and zeta are monotone increasing when arcs
are added, the skeleton separator lemma implies the same residual lower
bounds in the actual quotient:

    eta(B) >= 3

for every nonempty `B subseteq O'` except the endpoint singleton and the
optional weak middle singleton; and

    zeta(A) >= 3

for every nonempty proper `A subset O'` except the endpoint singleton,
the root-complement row, and the optional weak middle rows.

This is exactly ER-4.

## Consequence

At the support-ladder normal-form level, the AOC lower-bound package
ER-0--ER-4 is now available:

* ER-0 is the active first-successor exit;
* ER-1 is SLE;
* ER-2 and ER-3 are D82;
* ER-4 is the residual ladder separator proved here.

Therefore AOC holds for the endpoint-reduced outside quotient, with the
exact tight rows listed in D81 once the endpoint and row-cleanliness
equalities from the normal form are included.  By D75, AOC implies FSQ.

## Remaining Structural Work

The remaining raw sealed-block task is no longer an outside-cut
calculation.  It is to derive the residual ladder skeleton itself from
the written sealed-block/CL/DT primitives: the cyclic block order, the
complete two-by-two support boundaries, the shortcut orientations, and
the optional weak-middle deletion of `m -> h1`.
