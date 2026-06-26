# D70: Local Quotient Lemma Package

Date: 2026-06-19.

Artifact: `scripts/local_quotient_profile_audit.py`.

## Purpose

D68 stated the local normal-form contract, and D69 found no bounded
gate-preserving deletion counterkernel.  This note rewrites the
remaining local proof in the smallest symbolic form that is actually
needed.

The right local objects are not the deficient cuts themselves, but their
quotients:

* complements of internal cuts inside the sealed zero prefix `Q0`;
* outside cuts in `O = V(C) \ Q0`.

In this form, the single-exchange obstruction is no longer an
independent global condition.  It follows from the singleton terms of
the two quotient lemmas.

## Notation

Let `C` be the split semicomplete core.  Assume `Q0` is the sealed zero
prefix supplied by D65:

    d_C^+(Q0) = 0.

Put

    O = V(C) \ Q0.

For `empty != T proper subset Q0`, write

    in_Q0(T) = A_C(Q0 \ T, T).

Thus, for `S = Q0 \ T`,

    d^+_{C[Q0]}(S) = |in_Q0(T)|.

Let `w1` be the first chain successor outside `Q0`.

## Quotient Hypotheses

The two local quotient hypotheses are:

**HBQ, head-block quotient.**  If

    empty != T proper subset Q0
    and |in_Q0(T)| <= 1,

then `T = {h}` for a weak head `h`.  Moreover every such weak head has
one actual entry:

    |in_Q0({h})| = 1.

So an internal low cut is exactly `Q0 \ {h}`, and it is active only when
the actual singleton entry count is one.  If an extra reverse-head arc
raises the entry count to two, the cut disappears from the active list.

**FSQ, first-successor quotient.**  If

    empty != B proper subset O
    and d^+_{C[O]}(B) <= 1,

then `B = {w1}`.  Moreover the first successor has one actual outside
exit when it is active:

    d^+_{C[O]}({w1}) = 1.

So the only external-prefix low cut is `Q0 union {w1}`, again included
only when its actual out-size is one.

These hypotheses are weaker than the refuted exact `1,0,1` profile.
They allow the old `Q-` cut to become non-low, as in D63.

## Local Quotient Theorem

Assume:

1. `C` is semicomplete;
2. `d_C^+(Q0)=0`;
3. HBQ;
4. FSQ;
5. the active prefixes have no rho-label exits.

Then LNF-0 through LNF-4 of D68 hold.  Consequently D65, D67, and D64
give the monotone deficient-prefix repair profile.

### Proof

LNF-0 is assumption 2.

For LNF-1, let `S` be a nonempty proper internal cut of `C[Q0]`, and put
`T = Q0 \ S`.  Then

    d^+_{C[Q0]}(S) = |A_C(S,T)| = |in_Q0(T)|.

If this value is below two, HBQ gives `T={h}` for a weak head `h`, and
the actual value is one.  Hence the only internal low cuts are the
one-head-deleted cuts `Q0 \ {h}` that are actually low.

For LNF-2, let `S` be an external-prefix cut, so `S = Q0 union B` with
`empty != B proper subset O`.  Since `Q0` has no exits,

    d_C^+(Q0 union B) = d^+_{C[O]}(B).

If this value is below two, FSQ gives `B={w1}`, with one actual outside
exit.  Hence the only external-prefix low cut is the first-successor
prefix `Q0 union {w1}` when it is actually low.

It remains to prove LNF-3.  Consider a single-exchange cut

    (Q0 \ {h}) union {w},        h in Q0, w in O.

D65 gives the exact formula

    d^+((Q0 \ {h}) union {w})
      = |A_C(Q0 \ {h}, {h})|
        + d^+_{C[O]}({w})
        + |A_C({w}, {h})|.

The last term is at least one: `C` is semicomplete, and `h -> w` is
impossible because `d_C^+(Q0)=0`, so some arc `w -> h` exists.

If `h` is not a weak head, HBQ gives
`|A_C(Q0 \ {h}, {h})| >= 2`.  If `w != w1`, FSQ gives
`d^+_{C[O]}({w}) >= 2`.  In the only remaining case,
`h` is weak and `w=w1`, the singleton terms are both equal to one by
HBQ and FSQ.  Therefore every single-exchange cut has size at least

    1 + 1 + 1 = 3,

and no single-exchange low cut exists.  This proves LNF-3.

LNF-4 is assumption 5, which is exactly the one-sided rho-exit
cleanliness used by D67.  Combining LNF-0..4 with D68 completes the
local-to-global assembly.  QED.

## What Remains From Sealed-Block/CL/DT

D70 does not claim that the current written CL/DT notes already prove
HBQ and FSQ.  It isolates the exact two statements that have to be
derived.

### Head-Block In-Cut Lemma

For the sealed middle block

    Q0 = cage union escaped_heads union {v},

prove HBQ: every nonempty proper complement `T subset Q0` receives at
least two entries from `Q0 \ T`, except possibly a singleton escaped
head whose only entry is the root-head arc from `u`.

This is the corrected internal target.  It must use the local
semicomplete head-block orientation, C3 hooks, C7 cage packing, and
3-arc-strongness.  It must not assert that the weak-head singleton is
always active: D63 shows a reverse-head arc can raise its entry count
from one to two.

### First-Successor Outside Lemma

For the outside quotient `O`, prove FSQ: every nonempty proper
`B subset O` has at least two exits in `C[O]`, except possibly the
singleton first successor `{w1}`, whose actual outside exit count is
one.

This is the corrected external target.  It should be proved from CL's
forced-chain classification, DT's support vertices entering `W`, and
shortest-path no-shortcut constraints.  Larger outside cuts and later
chain successors must have a second exit supplied by the `W` support or
by a non-forced semicomplete hook.

Once these two quotient lemmas are proved from the primitive
sealed-block machinery, the D64/D65/D67 route is closed at the split-core
cut-cover level.

## Audit

The executable audit checks the quotient form on:

    D42 original,
    D63 reverse-head,
    D66 rho-entry,
    D63 + D66 combined.

Results:

    D42:
      low_head_complements = [({6}, [(2,6)])]
      low_outside_cuts     = [({10}, [(10,23)])]
      min_singleton_terms  = 3

    D63 reverse-head:
      low_head_complements = []
      low_outside_cuts     = [({10}, [(10,23)])]
      min_singleton_terms  = 4

The rho-entry variants have the same quotient profile as their
non-rho-entry partners.  This is expected: rho entries are harmless for
directed out-cut bookkeeping by D67.
