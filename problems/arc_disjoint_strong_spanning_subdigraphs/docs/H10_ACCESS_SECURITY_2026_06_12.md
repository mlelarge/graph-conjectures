# H10 attack: survival taxonomy, the access-cut, and access security

Date: 2026-06-12 (D36).  Companion to D35's cage-sparing shaping and
`h10_joint_check.py`.  Setting of Theorem DT / Lemma OUT; canonical
prescriptions `(r1,rho), (r2,rho)` unless stated.

## Lemma ST (survival taxonomy)

In `D-hat(T, e1, e2)` with prescriptions at distinct boundary tails:

* (a) `X_P -> rho` and all other BOUNDARY arcs: never carry T-labels
  (DT); they survive in full at unprescribed tails, and the designated
  arc survives at prescribed tails;
* (b) `O -> X_P` arcs: survive ENTIRELY (tails in `O` are touched only
  by `T_out`, whose heads lie in `O u {rho}`);
* (c) `O -> rho` arcs: lose exactly the `T_out`-labels (at most one per
  tail; in particular `p_k` keeps `mult(p_k,rho) - 1` labels);
* (d) `X_P`-internal arcs: lose at most one label per tail (the tail's
  `T_in`-arc), and ALL non-designated arcs at prescribed tails.

## Lemma AC (the access-cut)

Let `Y = V \ {rho, r1, r2}`.  Then `lambda >= 3` gives

    3 <= sum_{r3 in (R cap X_P) \ {r1,r2}} mult(r3,rho)
         + mult(p_k, rho)
         + #(X_P -> {r1,r2} arcs, tails != r1,r2)
         + #(O -> {r1,r2} arcs),

and the four classes survive as: third-root labels ALWAYS (ST-a);
`p_k`-labels except one (ST-c); `O -> root` arcs ALWAYS (ST-b);
`X_P -> root` arcs unless the tail's own `T_in`-arc is exactly that arc
(ST-d).

## Theorem AS (access security)

There is a choice of `T_in` (cage-sparing, via C7) and, if needed, a
FINITE EXCLUSION refinement of `X_P`, after which at least one arc into
`{rho, r1, r2}` from outside `{rho, r1, r2}` survives in `D-hat` -- an
ACCESS POINT exists.

**Proof.**
If a third root exists, or `mult(p_k,rho) >= 2`, or some `O -> root` arc
exists: access survives unconditionally (ST-a/c/b).  Otherwise Lemma AC
forces `>= 2` arcs `X_P -> {r1,r2}` at distinct tails.  Call a tail
UNFORCED if it has another `X_P`-internal out-arc; then setting its
`T_in`-arc to that alternative is always globally consistent: any
internal out-arc continues to `u` inside `X_P` (every `K cap X_P` vertex
reaches `u` by hooks+cage; every internal head reaches `u` by the
closure definition), so an in-arborescence with that single constraint
exists.  An unforced tail therefore yields a surviving access arc.
A FORCED tail `x` (unique internal out-arc = its root-arc) is an
`I`-vertex: a `K`-vertex always has `>= 2` internal hooks.  If ALL
access tails are forced, EXCLUDE one such `x` from `X_P` (re-close): `x`
joins `O`, it routes outside via its `>= 2` arcs onto `V(P_v)` (it was a
near-`J` path-fan plus the root-arc), and its root-arc becomes an
`O -> X_P` arc -- PERMANENTLY surviving access (ST-b).  Exclusions
remove only `I`-vertices (`K`-vertices are never closure-removed: hooks)
and never touch cage, `u`, `r1`, `r2`; the process terminates.  QED.

Witness inventory (machine-checked, D36): access-cut totals
6/6/6/10/3/16 on the six witnesses (tight = 3 on core_embedding via the
spare `p_k`-label); forced-risk tails exist only on blocker_cex
((15,12),(16,13)) where `O -> root` arcs cover access anyway.

## REACH saturation (REFUTED as a universal step, D38)

With access secured, let `REACH` be the set of vertices reaching `rho`
in `D-hat`, and suppose `Z = V \ REACH` is nonempty (`rho, r1, r2,
access points in REACH`).  Every `Z`-vertex has at most ONE arc into
`REACH`, and that arc is its own `T`-arc (a vertex with two would keep
one: per-tail consumption, and no prescribed tails lie in `Z`).  The
remaining work: show this forces `Z = empty` using cage-sparing
(`cage -> u`), `u`'s free `AV_u` arcs, the hook structure (`Z cap K`
vertices hook into the cage: if the cage reaches `REACH` so do they),
and Lemma-OUT facts for `Z cap O`.  The circular core is `u`: `u in
REACH` iff some `AV_u`-head chain reaches an access point.

The proposed conclusion is false for arbitrary cage-sparing `T`.
`scripts/saturation_kernel_witness.py` gives an in-class host and a
cage-sparing tree for which

    Z = {u} u cage u heads u {v}

and all three arcs from `Z` to `REACH` are multiplicity-one tree arcs.
No distinct-tail boundary prescription pair completes this `T`.  See
`SATURATION_KERNEL_COUNTEREXAMPLE_2026_06_12.md`.

The same digraph has a repaired tree obtained by routing both heads
through cage hooks; the canonical pair then reaches every vertex.
Accordingly ST, AC, AS, SAT-1, and SAT-2 remain valid, but they do not
close branch 2.  The live obligation is existential construction of a
block-sparing tree, not saturation of every cage-sparing tree.
