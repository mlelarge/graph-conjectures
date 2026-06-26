# REACH saturation: blob structure, two closed cases, one kernel (D37)

Setting: D36 (canonical pair, cage-sparing AS-compliant T, access secured).
`Z = V \ REACH` assumed nonempty.

## Lemma SAT-1 (the blob structure)

1. Every `z in Z` has at most one arc into `REACH`, and it is `z`'s own
   `T`-arc (per-tail consumption; no prescribed tails in `Z`).
2. The u-cage block moves together: `u in REACH => cage subseteq REACH`
   (cage-sparing residual paths live in `D-hat`); `u in Z => cage
   subseteq Z` (cage arcs end in `cage u {u}`).
3. `Z cap (K \ cage) != empty => u in Z`: every such vertex keeps a
   surviving hook into the cage (`>= 2` hooks, at most one `T_in`-consumed
   for `X_P`-vertices, none for `O`-vertices), so a `REACH`-cage forces it
   into `REACH`.
4. `Z cap I != empty => u in Z` (its `>= 2` surviving `K`-arcs would
   otherwise land in `REACH`).
5. Hence `Z != empty => Z` contains the BLOCK `B = {u} u cage u
   {AV_u-heads}` (u's `AV_u` arcs are never consumed, so all heads of
   `Z`'s `u` lie in `Z`), and every boundary arc of a `Z cap X_P` vertex
   heads into `Z cap O` (boundary arcs are never consumed).

## Theorem SAT-2 (two cascade cases)

**Case 1: some `AV_u`-head `h*` has an arc to a root (`h* -> r_i` in
`D`).**  Choose `T_in(h*)` to be a hook (always possible, `h* in K`...
if `h* in I` the arc `h* -> r_i` is one of its `>= 3` `K`-arcs and
`T_in(h*)` can be any other internal arc -- internal continuation to `u`
always exists).  Then `(h*, r_i)` survives, `h* in REACH`, `u in REACH`
(free `AV_u` arc), cage follows (SAT-1.2), every `Z cap (K \ cage)`
vertex follows (SAT-1.3), every `I`-vertex follows (SAT-1.4):
**`Z = empty`.**

**Case 2: some `O cap K` vertex `w` has an arc to a root, and some head
`h*` has a boundary arc `(h*, w)`.**  `(w, r_i)` is an `O -> X_P` arc:
NEVER consumed, so `w in REACH` unconditionally.  `(h*, w)` is a
boundary arc: never consumed, so `h* in REACH`, and the Case-1 cascade
repeats: **`Z = empty`.**

(The same cascade fires whenever any head's boundary arc reaches an
`O`-vertex in `REACH` -- e.g. `p_k` when `mult(p_k, rho) >= 2`.)

## The residual kernel (REALIZED IN-CLASS, D38)

Both cases fail only if: every head is dominated by both roots, no
head's boundary arc reaches a `REACH`-`O`-vertex, and the block `B`'s
`>= 2` non-`a` out-arcs (from `lambda >= 3` at `B`) lead only into
`Z`-side vertices whose own `REACH`-entries are all consumed.  The
candidate tools for killing the kernel: (i) the per-tail survivor
guarantee (a vertex with `k` arcs toward `REACH`-candidates keeps
`>= k-1`), formalized as connectivity in the never-consumed sub-digraph
(boundary arcs + `O -> X_P` arcs + spare labels + hooks-beyond-one);
(ii) the access point's position (AS) -- if access can always be
SECURED AT a head-adjacent vertex, Case 1/2 fire by construction;
(iii) `lambda >= 3` at `B` and at `Z` jointly.

D38 realizes this configuration in-class; see
`SATURATION_KERNEL_COUNTEREXAMPLE_2026_06_12.md` and
`scripts/saturation_kernel_witness.py`.  For its cage-sparing `T`,

    Z = {u} u cage u heads u {v}

and the three arcs from `Z` to `REACH` are exactly three multiplicity-one
`T`-arcs.  Exhaustion of every distinct-tail boundary prescription pair
finds zero completions.  Thus saturation for an arbitrary cage-sparing
`T` is false.  A second tree on the same digraph, routing the heads
through cage hooks, is completed by the canonical pair; the remaining
target is existential selection of a stronger block-sparing `T`.
