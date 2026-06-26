# D50: prescribed pending-decomposition probe

Date: 2026-06-18.

Artifact:

    scripts/pending_decomposition_prescribed_probe.py

Status: diagnostic evidence, stronger than D49 but still not a theorem.

## Probe

D49 inspected whatever red/blue colouring the SAT solver returned on the
split-off semicomplete core.  D50 strengthens this: after choosing two
split-off paths `x -> s -> y` through each independent-side vertex
`s in V1\{p,q}`, the script forces one split arc to be red and the other
to be blue before solving the core SAD instance.

A `prescribed-hit` means the split core admits a SAD under those forced
split colours.  This is closer to a pending-decomposition proof: the
colours needed to lift through `s` are prescribed, not discovered after
the fact.

## Results

Run:

    .venv/bin/python scripts/pending_decomposition_prescribed_probe.py

Results:

* `rho_headless_D17_and_D47_host`: `prescribed-hit`;
* `dominated_D18_host`: `prescribed-hit`;
* `relay_free_D19_host`: `prescribed-hit`;
* `saturation_kernel_D38_host`: `prescribed-hit`;
* `chain_kernel_D42_host`: `prescribed-hit`;
* `core_embedding_D28_host`: `no-prescribed-hit`.

For D42, the first split choice already works with prescribed colours:

    s=9:  2 -> 9  -> 3   red,  8 -> 9  -> 10  blue
    s=11: 10 -> 11 -> 7  red, 15 -> 11 -> 4   blue
    s=13: 2 -> 13 -> 14  red, 12 -> 13 -> 7   blue

The split core has `lambda=2` and admits a SAD under those forced colour
constraints.

## Consequence

The D42 chain kernel is not merely compatible with an accidental pending
colouring.  It admits a colour-prescribed pending split-off core.  This
is the strongest evidence so far that the recent split-digraph pending
decomposition machinery is the right import for the non-degenerate chain
kernel.

D28 remains the exception in this naive two-split formulation.  This is
consistent with the older ledger state: D28 is the tournament-core
example and has been handled by multi-w/cut-avoidance phenomena rather
than by the simple relay/pending picture.

## Next proof target

Try to formulate a **Prescribed Pending Missing Entry Lemma**:

> In a non-degenerate sealed multi-crossing chain kernel, the independent
> forced-chain vertices admit two split-off paths each, with prescribed
> opposite colours, such that the split semicomplete core has a SAD.
> Lifting that SAD either directly completes the host or yields the B3+
> entry/exit-count condition.

The next script should test robustness beyond the first found split
choice: for D42 and the positive witnesses, count how many local split
choices admit both colour orientations, and isolate the exact obstruction
in D28.

## D51 follow-up

`scripts/pending_decomposition_robustness_count.py` now performs that
count.  The one-independent-vertex positive hosts are fully robust:
18/18 split choices and 36/36 colour prescriptions complete on each of
D17/D47 host, D18, D19, and D38.  D42 is sparser but positive: in a
deterministic sample of 120 split choices, 24 choices have some SAT
prescription and 98/960 prescribed orientations complete.  D28 remains
0/18 choices and 0/36 prescriptions, with every split core at
`lambda=1`.
