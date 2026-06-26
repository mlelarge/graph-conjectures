# D72: First-Successor Outside Core Lemma

Date: 2026-06-19.

Artifact: `scripts/first_successor_outside_audit.py`.

## Purpose

D70 reduced the external-prefix part of the local normal form to FSQ:
the only outside cut of size below two should be the singleton first
successor `{w1}`.  This note proves FSQ from a smaller outside-core
certificate.

The useful object is not all of `O`, but

    O' = O \ {w1}.

If `O'` is already 2-arc-strong, then the first successor can be treated
as a one-exit ear attached to a robust outside core.

## Outside-Core Certificate

Let `O = V(C) \ Q0`, and let `w1 in O` be the first chain successor
outside the sealed zero prefix.  Put `O' = O \ {w1}`.

Assume:

**OC-1, one first-successor exit.**

    d^+_{C[O]}({w1}) = 1.

**OC-2, robust outside core.**  Every nonempty proper cut of `C[O']`
has at least two exits:

    lambda(C[O']) >= 2.

**OC-3, two returns to the first successor.**

    |A_C(O', {w1})| >= 2.

Then FSQ holds.

## Proof

Let `empty != B proper subset O`.

If `B={w1}`, then OC-1 gives exactly one outside exit.  This is the
allowed low cut.

If `w1 notin B`, then `B subset O'`.  If `B proper subset O'`, OC-2
gives at least two exits from `B` to `O' \ B`, hence at least two exits
from `B` in `O`.  If `B=O'`, then the exits from `B` in `O` are exactly
the returns from `O'` to `{w1}`, and OC-3 gives at least two.

If `w1 in B` and `B != {w1}`, write

    B = {w1} union A

with `empty != A proper subset O'`; the case `A=O'` would make `B=O`,
which is not a proper cut.  By OC-2, `A` has at least two exits to
`O' \ A`.  These arcs also leave `B` in `O`, so `B` has at least two
outside exits.

Thus the only outside cut below two is `{w1}`, and it has one actual
exit.  This is FSQ.  QED.

## D42 Instantiation

For D42 in host labels,

    w1 = 10,
    O' = {12,14,15,16,17,18,19,20,21,22,23}.

The audit verifies, in D42, D63, D66, and combined D63+D66:

    lambda(C[O']) = 2,
    delta^+_{C[O]}({10}) = [(10,23)],
    |A_C(O', {10})| = 10.

So the only outside low cut is `{10}`, and the external-prefix low cut is

    Q0 union {10}

with actual core out-edge `(10,23)`.

## Remaining Primitive Derivation

To finish FSQ from sealed-block/CL/DT, prove the outside-core
certificate for every nonterminal sealed multi-crossing block:

1. OC-1 from the first-successor split-core form: after pending vertices
   are deleted, the first successor has exactly one outside-core exit.
2. OC-2 from the CL/DT support structure on the rest of `W`: the
   support ladder and semicomplete hooks give a 2-arc-strong outside
   core once `w1` is removed.
3. OC-3 from semicompleteness plus the nonterminal multi-crossing
   support: at least two outside-core vertices return to the first
   successor.

D72 proves the cut-theoretic implication.  The remaining work is the
primitive derivation of OC-1..OC-3 from the sealed-chain construction
rather than from the D42 audit.
