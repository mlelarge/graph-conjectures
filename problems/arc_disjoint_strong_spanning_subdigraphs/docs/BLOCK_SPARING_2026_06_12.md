# Block-sparing: Lemma BS-1, the cascade, and the regress (D39)

Setting: D36-D38 (canonical pair, X_P with AS exclusion available).

## Lemma BS-1 (the block escape is always securable)

There is a valid `T_in` (cage part from the C7 packing; each AV_u-head
assigned a hook or block-internal retreat when one exists) such that at
least one arc from the block `B = {u} u cage u heads` to `V \ B`
survives in `D-hat`.

**Proof.**  `lambda >= 3` at `B` gives `delta+(B) >= 3`; `u` contributes
only `a` (its other arcs head into the heads), the cage contributes
nothing (gated), so the heads carry `>= 2` out-of-`B` arcs.  Boundary
arcs among them are never consumed (ST-a).  Internal ones are consumed
only by their own tail's `T_in`-arc.  A `K`-head always has `>= 2` cage
hooks, so its retreat spares ALL its out-of-`B` arcs.  An `I`-head whose
unique internal arc is its out-of-`B` arc cannot retreat -- but then its
remaining `>= 2` mult-1 arcs head into `K cap O`: boundary, never
consumed.  In every case some out-of-`B` arc survives.  QED.

(This dissolves the I-head worry: forced consumption at an I-head
IMPLIES never-consumed boundary escapes at the same head.)

## Theorem BSC-1 (conditional cascade)

If the surviving block-escape `(h*, z*)` has `z* in REACH`, then
`Z = empty`: `h* in REACH`, then `u` (free AV_u arc), then the cage
(cage-sparing), then all of `K \ cage` (hooks), then all `I`-vertices
(spares).  [SAT-1 + SAT-2 machinery.]

## The regress (ER, open) and the empirical state

The open residue is exactly: secure `z* in REACH` -- the escape target's
own reachability, one level out of the block, recursively.  Machine
data (this round): the BS-1 recipe alone completes 58/70 trials on the
seven witnesses (kernel witness 10/10 -- the D38 repair IS BS-1);
adding AS access-avoidance lifts the five in-scope witnesses plus
kernel to 116/120.  The four residual failures (dominated 1,
core_embedding 2, blocker_cex 1) are the regress made visible: some
non-head vertex's T_in-arc consumes the escape-chain's next link.  The
remaining work: either a third sparing rule closing the chain (with a
termination argument: each sparing is local, conflicts only at
single-internal-arc vertices, which carry never-consumed boundary arcs
by the BS-1 argument -- the same dissolution may iterate), or the
global formulation: choose T_in as a MINIMAL-consumption in-arborescence
over an escape-hierarchy ordering.

t_eq_u scores 0/10 under this recipe: out of scope (rho-heads; T1
territory), noted for honesty.
