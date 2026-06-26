# D48: degeneracy classifier and bounded D47 lift search

Date: 2026-06-18.

Artifacts:

    scripts/chain_kernel_degeneracy_classifier.py
    scripts/d47_lift_search.py

Status: tooling result, not a theorem.  The point is to separate the D47
short-chain B3+ defeat from the D42-style sealed multi-crossing case.

## Classifier predicates

For a hard pair `(T,U)` at `a=(u,v)` with cage/current set `X` and unique
`U`-exit `(u,y)`, the classifier runs the exact B3+ row enumeration and
then records:

* `b3-good`: at least one B3+ row is a good pair with `U` unchanged;
* `short-chain-exit-head-in-subtree`: no good row, all rows fail by
  `exit_count`, and at least one candidate subtree swallows the original
  exit head `y`;
* `short-chain-one-exit`: no good row, all rows fail by `exit_count`,
  and no explicit sealed multi-crossing data is present;
* `sealed-multi-crossing-b3-good`: an explicit forced-tail set is
  supplied, at least two forced tails are `U`-used crossings, and a good
  B3+ row absorbs a subtree containing such a forced crossing;
* `sealed-multi-crossing-b3-fail`: the dangerous target not yet seen,
  namely explicit multi-forced crossings but no B3+ good row.

The final label is deliberately conservative: without an explicit
forced-tail set, a failure is treated as short-chain/degenerate rather
than as a sealed chain-kernel refutation.

## Results

Selected hard pairs:

* `t_eq_u(D10)`: `b3-good`;
* `rho_headless(D17)`: `b3-good`;
* `dominated(D18)`: `b3-good`;
* `relay_free(D19)`: `b3-good`;
* `core_embedding(D28)`: `b3-good`;
* `blocker_cex(D30)`: `b3-good`;
* `saturation_kernel(D38)`: `b3-good`;
* `chain_kernel(D42)`: `sealed-multi-crossing-b3-good`, with
  `U`-used forced crossings `[10,12]`;
* `generalized_short_chain(D47)`:
  `short-chain-exit-head-in-subtree`, with 5 candidates, 0 good rows,
  and `exit_count=[1]`.

Small exhaustive failure inventory:

* `D10`: 19,800 hard pairs.  Counts:
  3,564 B3-good, 11,814 exit-count failures, 330 mixed failures,
  4,092 no-free-entry failures.  Representative exit-count failures are
  `short-chain-one-exit`.
* `D17`: 196,416 hard pairs.  Counts:
  63,360 B3-good, 108,768 exit-count failures, 24,288 no-free-entry
  failures.  Representative exit-count failures are
  `short-chain-exit-head-in-subtree`, matching D47.

## Bounded lift search

`scripts/d47_lift_search.py` tries the obvious lift into the already
realized D42 sealed chain kernel: keep the D42 cage hard-pair `T`, sample
alternate `U` arborescences, and ask whether the D47 exit-count failure
survives when at least two forced tails are `U`-used crossings.

Run parameters and result:

    seed=4701
    trials=5000
    hard_pairs_seen=967
    multi_forced_crossing_seen=428
    label_counts={'sealed-multi-crossing-b3-good': 800, 'b3-good': 167}
    sealed-multi-crossing B3+ failure found: False

This is not proof of Chain Crossing Selection.  It is evidence that the
D47 obstruction is genuinely degenerate: when the same search is pushed
into a realized sealed multi-crossing kernel, the sampled hard pairs all
recover one-shot B3+ repairs.

## Next target

The live statement should be the non-degenerate Missing Entry Lemma:
under explicit sealed-block and multi-forced-crossing hypotheses, some
forced crossing tail or T-ancestor inside the sealed block satisfies
B3+'s free-entry and exit-count condition.  The known false statements
remain excluded:

* all-hard-pairs one-shot B3+ is false by D47;
* selected-pair evidence is not a proof;
* bounded D42 sampling is not exhaustive.
