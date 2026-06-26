# ER: the canonical tree, the closure theory, and the chain kernel (D40)

Setting: D36-D39 (canonical pair; X_P with AS exclusions available).

## Theorem CT (the canonical tree)

The assignment

    T*_in :  cage part := one arb of the C7 cage packing;
             every K \ cage vertex := one of its cage hooks;
             every I-vertex := any internal arc (choice rule below)

is ALWAYS a valid in-arborescence of `D[X_P]` rooted at `u`.

**Proof.**  The classes point strictly inward: `I`-vertices point at
`K`-vertices (`I`-arcs head into `K` only), `K \ cage` vertices point at
the cage, the cage points to `u` through the packing arb.  No cycle can
form across strata, and each stratum is internally acyclic (hooks and
`I`-choices are single arcs into a lower stratum; the packing arb is an
arb).  QED.

Consequences: (i) ALL R3-style sparing demands at `K`-vertices are
satisfiable SIMULTANEOUSLY (hooks consume only block-internal/cage
arcs); (ii) the only T*-consumed arcs outside the cage and hooks are one
internal arc per `I`-vertex -- and the `I`-choice rule can avoid any
single designated arc whenever the vertex has two internal arcs.

## The closure theory (R1/R2/R3)

Let `W` be the closure of `{rho, r1, r2} u (AS access)` under:
  R1: a NEVER-CONSUMED arc into `W` (boundary, O->X_P, AV_u, spare
      labels) puts its tail in `W`;
  R2: TWO arcs into `W` put the tail in `W` (per-tail consumption);
  R3: ONE consumable arc into `W` plus an alternative T-target puts the
      tail in `W` (sparing; conflict-free under T* by CT).

**Theorem CL.**  With T* and maximal `W`: every arc from `B* = V \ W \
{rho}` into `W` is the FORCED consumption of its tail -- and the forced
tails are exhaustively: (a) `I`-vertices of `X_P` whose unique internal
arc is their `W`-arc -- REMOVABLE by the AS exclusion (the arc becomes
O->X_P, never consumed, putting the tail in `W`); (b) `O`-vertices whose
unique `D_O`-arc is their `W`-arc -- these lie on `P_v` (J-vertices are
>=3-fans onto the path, never single), so they are CHAIN ARCS
`(p_i, p_{i+1})` with `p_{i+1} in W`, plus possibly the single
`(p_k, rho)` label.

**Proof sketch (assembled from proved pieces).**  Boundary and `O->X_P`
arcs into `W` contradict `W`-maximality via R1; internal `X`-arcs at
`K`-tails are R3-securable by hooks (CT); internal arcs at `I`-tails
with two internal arcs are R3-securable by the `I`-choice rule;
`J`-vertices have >= 3 `D_O`-arcs (path-fans), so R2/R3 applies.  What
survives is exactly (a) and (b).  QED.

## The chain kernel (the FINAL configuration of branch 2)

After AS-exclusions, `Z != empty` requires `delta+(B*) >= 3` to consist
ENTIRELY of forced `P_v`-chain arcs (plus possibly one `(p_k,rho)`
label): the shortest path alternates `B*`/`W` segments at least twice,
each forced crossing `p_i` has the chain arc as its ONLY `D_O`-arc (no
backward arcs, no rho-arc, no `J`-arcs) with all its other arcs heading
into `X \ W`, and each `W`-segment of the path contains an `O`-vertex
that entered `W` via a root-arc or spare label.  Realize this in-class
(host lambda gate! explicit pair!) or prove it impossible (the
candidate count: the alternation forces multiple `O`-side root-arcs and
single-`D_O`-arc path vertices simultaneously on ONE shortest path,
against `d^-(rho) >= 5` tightness and the path-fan structure of `J`).

Empirical status: the chain kernel is unrealized on all seven
witnesses (BS-1+AS trees complete 116/120; the 4 failures are
R3-conflicts now dissolved by T*, to be re-verified with the canonical
tree).
