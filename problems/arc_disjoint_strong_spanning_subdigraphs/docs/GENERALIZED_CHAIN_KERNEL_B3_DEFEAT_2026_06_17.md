# D47: generalized chain-kernel core defeating one-shot B3+

Date: 2026-06-17.

Artifact:

    scripts/generalized_chain_kernel_b3_defeat.py

Status: constructed and asserted.  This is a negative witness for the
over-broad statement that every in-class hard gateway pair admits a
one-shot B3+ free-entry repair with the same `U`.

## Construction

Use the in-class D17 rho-headless host, but not the D45 selected hard
pair.  In the contraction:

* `n=8`, `rho=0`, `u=1`;
* the cage is `C={1,2,3,4}`;
* `a=(1,5)`;
* the host is simple `(1,0)`-near-split, has `lambda=3`, and is
  oracle-SAT with ILP agreement;
* the contraction has `lambda=3` and is strictly rho-headless at `u`.

The hard pair is

    T = {1:5, 2:1, 3:1, 4:2, 5:0, 6:0, 7:0}
    U = {1:6, 2:3, 3:4, 4:1, 5:0, 6:0, 7:2}

Then `X_a^T=C`, the unique `U`-exit from `C` is `(1,6)`, and it is not
strict.  The only free exit from the cage is `(1,7)`, so this is a hard
gateway pair.

## Why B3+ fails

The B3+ candidates are exactly:

    w=6 via 6->2, 6->3, 6->4, with S_w={6};
    w=7 via 7->3, 7->4,       with S_w={7}.

All five rehangs are valid trees, remain arc-disjoint from the original
`U`, and keep the enlarged set intermediate.  But every row has
`exit_count=1`.

For `w=6`, the original exit head `6` is absorbed, so the old `(1,6)`
exit disappears and the only remaining `U`-exit is `(6,0)`.

For `w=7`, the old `(1,6)` exit remains, but `U(7)=2` returns into the
cage, so `S_7` supplies no second exit.

Thus the exact B3+ classifier returns `exit-count`, with zero good rows.

## Consequence

D45 remains correct as a selected-pair witness suite, but it cannot be
read as an all-hard-pairs statement.  One-shot B3+ with unchanged `U`
is false even inside an in-class rho-headless hard-gateway contraction.

This does not by itself refute the non-degenerate Chain Crossing
Selection Lemma for D42-style sealed multi-crossing chain kernels:
the D47 witness is a short-chain / exit-head-in-subtree core.  The live
proof obligation should therefore be sharpened to one of:

1. prove Missing Entry Selection with the genuinely non-degenerate
   sealed-block/forced-crossing hypotheses included; or
2. lift this D47 short-chain core into a full sealed chain kernel.
