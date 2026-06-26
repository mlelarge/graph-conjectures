# D77: Top-Support Clause Audit

Date: 2026-06-20.

Artifact: `scripts/top_support_clause_audit.py`.

## Purpose

D76 isolated the top-support two-exit clause as the missing primitive
for AOC.  This audit checks whether that clause is exactly the local
feature separating the AOC survivors from the AOC failures in the
single-reversal neighbourhood of D42.

## Clause

Let `w1 -> tau` be the unique first-successor outside exit.  The
top-support clause is:

    d^+_{O'}({tau}) >= 2,

where `O' = O \ {w1}`.

In D42 host labels:

    w1 = 10,
    tau = 23.

## Audit Result

The clause holds in all accepted normal forms:

    D42 original,
    D63 reverse-head,
    D66 rho-entry,
    D63 + D66,
    D74 support reversal,
    D74 + D63,
    D74 + D66,
    D74 + D63 + D66.

In all eight cases:

    tau = 23,
    delta^+_{O'}({tau}) = [(23,21),(23,22)],
    AOC holds.

In the full single-reversal neighbourhood:

    structural survivors = 27,
    top-support failures = 2,
    AOC failures = 2,

and the two lists are identical:

    (22,20) -> (20,22), leaving tau exit [(23,22)];
    (22,21) -> (21,22), leaving tau exit [(23,21)].

Thus, at this red-team scale, top-support two-exit is exactly the missing
endpoint condition behind AOC.

## Consequence

The next symbolic proof should first prove the top-support clause from
DT/root-spare support.  In a genuine sealed multi-crossing block, the
unique first-successor exit should land in a support vertex that has two
downward outside choices.  D76's bad reversals are precisely the
forbidden orientations where one of those choices is redirected upward
into the support vertex.

Once this endpoint clause is proved, the remaining AOC proof can be
attacked without carrying the terminal singleton obstruction.
