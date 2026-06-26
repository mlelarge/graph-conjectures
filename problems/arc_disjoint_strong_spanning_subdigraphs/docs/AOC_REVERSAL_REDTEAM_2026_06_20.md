# D76: AOC Reversal Red-Team

Date: 2026-06-20.

Artifact: `scripts/aoc_reversal_redteam.py`.

## Purpose

D75 proved that the attachment-aware outside-cut certificate AOC implies
FSQ.  The next question is whether the currently checked sealed-chain
gates already force AOC.

They do not.

## Search

The script enumerates every single D42 arc reversal whose reverse arc is
not already present.  It keeps only variants preserving the checked
structural gates:

* near-split host;
* `lambda(D-bullet)=lambda(host)=3`;
* cage `{1,2,3,4}`;
* unique sealed path `7->8->9->10->11->12->13->rho`;
* forced `D_O` arcs;
* sealed `B*` out-cut.

Among the single reversals, 27 preserve these gates.  Exactly two break
AOC:

    22 -> 20  reversed to  20 -> 22,
    22 -> 21  reversed to  21 -> 22.

Both are top-support reversals at the upper ladder vertex `22`, which is
host/core vertex `23`.

## Surviving Hard Gateway

These are not merely gate-preserving artifacts.  In both variants the
hard gateway survives with a small reroute of the displayed D42 pair.

For `(22,20)->(20,22)`:

    T(22) = 21,
    U(22) = 1.

For `(22,21)->(21,22)`:

    T(22) = 20,
    U(22) = 1.

In both cases:

    X = {1,2,3,4},
    U-exits from X = [(1,10)],
    free exits from X = [(1,5),(1,6),(1,8),(1,12)].

So the same hard-gateway shape remains.

## AOC Failure

In host labels, the new bad outside cut is the top support singleton

    {23}.

For `(22,20)->(20,22)`, the only outside exit of `{23}` is

    (23,22).

For `(22,21)->(21,22)`, the only outside exit of `{23}` is

    (23,21).

Thus AOC fails in both forms:

* the cut not containing `w1`,

      B = {23},

  has only one exit and no return to `w1`;

* the cut containing `w1`,

      {w1} union {23},

  still has only the same one exit, because the first-successor exit
  `10 -> 23` lands inside the cut.

The full outside quotient has extra low cuts:

    {10}, {23}, {10,23}.

So FSQ itself fails for these variants.

## Consequence

D76 does not refute AOC as the intended outside lemma.  It refutes the
claim that AOC follows from the currently checked sealed-chain gates and
hard-gateway structure alone.

The missing primitive is now precise:

**Top-Support Two-Exit Clause.**  The top support vertex reached by the
first-successor exit must retain two downward exits inside `O'`, or more
generally every terminal outside support singleton not attached back to
`w1` must have at least two exits inside the outside quotient.

This is plausibly a DT/root-spare support consequence, not a consequence
of the generic sealed-path gates.  Any symbolic proof of AOC must use
that top-support clause explicitly.

## Next Target

Prove the top-support two-exit clause from DT support:

1. the first successor's unique outside exit lands in a support vertex
   whose support role is nonterminal in the outside quotient;
2. DT/root-spare support gives two downward choices from that support
   vertex, not one;
3. CL maximality and no-shortcut constraints prevent redirecting either
   downward choice back upward without creating a new low outside cut.

Once this top-support endpoint is secured, the remaining AOC cuts can be
attacked by the same attachment-aware cut decomposition from D75.
