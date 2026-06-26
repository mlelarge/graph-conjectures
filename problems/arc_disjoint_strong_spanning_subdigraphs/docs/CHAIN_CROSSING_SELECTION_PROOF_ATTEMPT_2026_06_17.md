# Chain Crossing Selection: proof attempt and exact remaining gap

Date: 2026-06-17.

Status: not promoted.  The D45 witness suite suggests the right proof
shape, and the B3+ conclusion follows formally once one local
entry/ancestor condition is available.  That condition is not yet proved
by the existing chain-kernel notes.

## Target

Let `C=C_u` be the cage of a fixed-root hard gateway at `a=(u,v)` with
`X_a^T=C` and unique `U`-exit `b=(u,y)`.  In a realizable chain kernel
there is a sealed block `B` whose out-cut consists of forced chain arcs
on the shortest `v -> rho` path:

    delta+(B) subseteq {p_i -> p_{i+1}: p_i forced}.

The desired selection lemma is:

> Some U-used forced crossing tail `s`, or a T-ancestor `w` of such a
> tail inside the sealed block, satisfies B3+'s hypotheses: `w` is not on
> the T-ancestor path `A=vT rho`, has a U-free arc into `C` (or the
> current nested set), and the B3+ exit count for `C union S_w` is at
> least two.

Then B3+ gives a good pair immediately by re-hanging `w` into the cage.

## What D45 proves at witness level

`scripts/b3_selection_suite.py` applies the exact B3+ criterion to the
stable explicit hard-gateway inventory:

* `t_eq_u(D10)`: 4/4 candidates good;
* `rho_headless(D17)`: 3/6;
* `dominated(D18)`: 6/11;
* `relay_free(D19)`: 12/17;
* `core_embedding(D28)`: 6/14;
* `blocker_cex(D30)`: 12/17;
* `saturation_kernel(D38)`: 15/18;
* `chain_kernel(D42)`: 32/34, including 2 forced-chain repairs at
  `p5=12`.

The repeated mechanism is:

1. find a vertex `w notin C union A` whose old T-subtree `S_w` contains
   a U-exit from the sealed region;
2. use a U-free entry arc `w -> C`;
3. keep `U` unchanged.  The exits from `C union S_w` are either
   `(u,y)` plus one exit from `S_w`, or two exits from `S_w` when
   `y in S_w`.

## Conditional theorem

The following statement is proved from B3+ and needs no further
global machinery.

**Lemma.**  Let `(T,U)` be a hard gateway pair at `C`, with unique
`U`-exit `b=(u,y)`.  Suppose there is a vertex
`w notin C union A` and an arc `d=(w,c)` with `c in C`, `d notin U`.
Let `S_w` be the old T-subtree at `w`.  If

    [y notin C union S_w]
      + #{s in S_w : U(s) notin C union S_w} >= 2,

then replacing the T-out-arc of `w` by `d` gives a good pair at `a`.

**Proof.**  This is exactly Lemma B3+ from
`ABSORPTION_REPAIR_LEMMA_2026_06_11.md`.  The rehang is acyclic because
`w notin C union A` and the new arc enters `C`; the new `a`-subtree is
the disjoint union `C union S_w`.  The displayed count is precisely the
number of `U`-exits from the enlarged set.  If it is at least two,
Lemma 2.1 gives a strict exit.  QED.

## What remains unproved

To turn the conditional lemma into Chain Crossing Selection, one still
needs the following entry-selection statement.

**Missing Entry Lemma.**  In every realizable in-class chain kernel with
a hard gateway pair at `C`, there is a U-used forced crossing tail `s`,
or a T-ancestor `w` of such a tail inside the sealed block, such that:

1. `w notin A`;
2. `w` has a U-free arc into `C`;
3. the U-exit from the forced crossing tail contributes to
   `#{s in S_w : U(s) notin C union S_w}`, unless `(u,y)` already
   supplies the second exit.

D45 verifies this statement on every stable explicit hard pair, but the
current symbolic notes prove only fragments:

* if `w in K \ C`, C3 gives two hooks from `w` into `C`, hence a U-free
  entry;
* if a forced tail is an `I`-vertex, it has at least two non-chain
  out-arcs to `K`, but the notes do not prove that one is usable outside
  the T-ancestor path or that its T-parent's subtree has the required
  exit count;
* if `y in S_w`, the D45 examples have two exits from `S_w`, but the
  existing sealed-block/closure theory does not yet force this in every
  abstract chain kernel.

Thus the repeated pattern has reduced the proof to a crisp local lemma:
forced chain tails cannot all be routed through ancestor-path vertices
or through subtrees with only the original `u`-exit.  Proving that lemma
would complete Chain Crossing Selection.  A counterexample to that
lemma would be a generalized chain kernel defeating one-shot B3+ and
would determine the repeated-absorption route.

## Next proof obligation

Prove or refute the Missing Entry Lemma.  The most plausible proof route
is to combine:

* the CL classification of forced chain tails as single-`D_O` path
  vertices;
* shortest-path no-shortcut constraints on `P_v`;
* C3 hooks for every `K \ C` vertex;
* the `d^-(rho) >= 5` / `|R| >= 3` accounting from DT, which forces
  multiple W-entries on one shortest path.

The branch-1 dynamic script is not useful evidence in its present form:
it currently fails its own host-lambda gate (`lambda(host)=2`) in this
workspace.

## D47 addendum: broad one-shot B3+ is false

`scripts/generalized_chain_kernel_b3_defeat.py` constructs a compact
negative witness for the broader all-hard-pairs reading of the D45
suite.  It reuses the in-class D17 rho-headless host but chooses a hard
pair outside the selected D45 representative:

    T = {1:5, 2:1, 3:1, 4:2, 5:0, 6:0, 7:0}
    U = {1:6, 2:3, 3:4, 4:1, 5:0, 6:0, 7:2}

At `a=(1,5)` the cage is `{1,2,3,4}` and the unique `U`-exit is
`(1,6)`.  There are five valid B3+ free-entry rows:
`6->2,3,4` and `7->3,4`.  All remain arc-disjoint from the original
`U`, all keep the enlarged set intermediate, and all have
`exit_count=1`; hence the exact classifier is `exit-count` and there is
no one-shot B3+ repair with `U` unchanged.

This does not refute the non-degenerate D42-style sealed chain-kernel
selection statement, because the witness is a short-chain /
exit-head-in-subtree core rather than a sealed multi-crossing block.
It does kill any attempt to promote "every hard pair has one-shot B3+"
from the D45 selected-pair suite.

## D48 addendum: classifier and lift-search outcome

`scripts/chain_kernel_degeneracy_classifier.py` makes the distinction
machine-checkable.  It labels:

* D47 as `short-chain-exit-head-in-subtree`;
* D42 as `sealed-multi-crossing-b3-good`, with `U`-used forced crossings
  `[10,12]`.

It also confirms that the D10/D17 exhaustive small hard-pair failures are
short-chain/no-free-entry/mixed phenomena, not sealed multi-crossing
failures.

`scripts/d47_lift_search.py` then performs a bounded deterministic lift
attempt on the realized D42 chain kernel: keep the D42 cage hard-pair
`T`, sample alternate `U` arborescences, and ask whether a
sealed-multi-crossing B3+ failure appears.  With seed `4701` and 5000
trials it sees 967 hard pairs, 428 with multi-forced crossings, and no
sealed-multi-crossing B3+ failure; all sampled hard pairs are B3-good.

This remains evidence rather than proof.  The live proof obligation is
now sharper: prove Missing Entry Selection under explicit
sealed-block/multi-forced-crossing hypotheses, or find a genuine
sealed-multi-crossing B3+ failure.
