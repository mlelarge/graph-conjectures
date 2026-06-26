# No-full-cover lemma for Step 1b — proof status

Date: 2026-06-03.

## Statement under attack

The useful form of Step 1b is:

> **No-full-cover lemma.** Let `D` satisfy the standing 2-extremal side
> hypotheses except possibly `χ⃗(D)=3`: `D` is strong, Eulerian with
> `indeg=outdeg>=2`, `U(D)` is 3-connected, repo-`λ(D)<=2`, and the digon graph
> `F_D` is a forest. If `F_D` is disconnected, then the bad single-dicycle partial
> assignments do not cover the component-flip cube.

Equivalently, some proper 2-colouring of `F_D` leaves the single-arc subdigraph
acyclic, hence `χ⃗(D)<=2`.

## Why this is not currently a proved lemma

The flip-cube theorem gives:

```text
bad partials cover the cube
  <=> every proper 2-colouring of F_D leaves a monochromatic single dicycle
  <=> chi_vec(D)=3                         (assuming F_D is a forest)
```

So, under the standing side hypotheses, a counterexample to the no-full-cover
lemma would already be:

```text
strong + Eulerian min-degree >=2 + U(D) 3-connected + lambda(D)<=2
+ chi_vec(D)=3 + F_D disconnected.
```

Since `D` is strong and has minimum outdegree at least `2`, repo-`λ(D)` is at
least `2` somewhere; together with `λ(D)<=2`, this gives `λ(D)=2`. Also
3-connected `U(D)` implies the required underlying 2-connectivity. Thus a
full-cover counterexample is exactly a 2-extremal digraph with 3-connected
underlying graph and disconnected `F_D`.

That is the Step 1b crux itself. Proving the no-full-cover lemma would therefore
prove the 3-connected case of the conjecture up to the already-separated
generalised-wheel assembly. It is not a smaller, already-available ingredient.

## What the proof would need

The audits reduce the proof to a concrete Menger/arc-connectivity lift:

> **Menger-lift target.** In a strong Eulerian digraph with `U(D)` 3-connected and
> repo-`λ(D)<=2`, a full flip-cube cover produced by disconnected `F_D` forces
> either a vertex 2-cut in `U(D)` or three arc-disjoint directed paths between
> some ordered pair.

For `k=2` components of `F_D`, the full-cover modes are exactly:

1. **internal mode:** one same-parity single dicycle sits inside one `F_D`
   component and is bad for every flip;
2. **opposite-cross mode:** two cross dicycles impose the two equations
   `x_0 xor x_1 = 0` and `x_0 xor x_1 = 1`.

The data say:

- the internal mode becomes covered only in non-2-connected two-star layouts, or
  has repo-`λ>=3` in the direct 3-connected `K5` stress construction;
- the opposite-cross mode is exactly what appears in the `k=2` truth-set
  obstructions, and every one has `κ(U)=2`;
- the 3-connected near-misses have only one cross parity and hence leave an
  uncovered flip assignment.

The missing proof is to derive these alternatives from Menger in general. The
informal shape is clear: a bad single dicycle plus the bidirected paths in its
digon-tree component gives two directed routes between suitable vertices; if
`U(D)` is 3-connected and there is no vertex 2-cut, the third underlying route
must lift to a third directed arc-disjoint route somewhere, contradicting
repo-`λ<=2`. The orientation/lifting step is precisely what is not yet proved.

## Red-team checks

The short statement survived the following checks:

- exact `K5` search over all `3^10` digon/orientation assignments, without
  Eulerian or strong assumptions: `24` disconnected-forest `λ<=2` candidates,
  `0` full covers;
- exact broad search through `n<=6` strong Eulerian orientations on 3-connected
  underlying graphs: `58` candidates at `n=5`, `238` at `n=6`, `0` full covers;
- previous `fd_cover_cuts.py` audits over the truth set and two-star families.

These checks support the lemma, but they do not replace the Menger-lift proof.

## Progress 2026-06-03b — the lift obstruction made precise + a rigorous partial

Two concrete results on the `k=2` Menger-lift.

### (R1) Cross-endpoint cut lemma. **[PROVED]**

Let `V_0,V_1` be the two `F_D`-components, `P ⊆ V_0` / `Q ⊆ V_1` the sets of
vertices incident to a cross single arc. *If `|Q| ≤ 2` and `V_1 ∖ Q ≠ ∅`, then `Q`
is a vertex cut of `U(D)` of size `≤2`.* (Every vertex of `V_1∖Q` reaches `V_0`
only through cross arcs, all incident to `Q`; inside `V_1` it reaches the rest only
through the digon tree, i.e. through `Q`. Deleting `Q` isolates `V_1∖Q`.)
Symmetrically for `P`. Since `U(D)` is 2-connected, `|P|,|Q| ≥ 2`; and **3-connected
⇒ for each side either `≥3` cross-endpoints or the whole component is
cross-endpoints** (`V_i = ` its endpoint set). This rules out the "few cross
endpoints" route to a 2-cut but does **not** capture the actual 2-cut, which in
every example is `{tree-hub, cross-bottleneck}` — a *tree-structural* cut, not a
cross-endpoint cut.

### (R2) Why the lift is not automatic — the single-source tree bottleneck.

Contract each component `T_i` to a point: the cross arcs give a 2-vertex digraph
with `m` arcs each way, so the contracted pair has `m` arc-disjoint cross paths.
But these **do not lift** to `m` arc-disjoint paths between any *single* `u∈V_0`
and *single* `w∈V_1`: routing `u → (tail of cross arc)` happens inside the **digon
tree** `T_0`, where paths from one source share their initial arcs. Three
arc-disjoint `u→w` dipaths would require `u` to have `≥3` tree-subtrees each
carrying a forward cross arc **and** `w` to be enterable from `≥3` `V_1`-points
arc-disjointly in `T_1`. The 2-extremal examples avoid exactly this — and the
device that prevents it is the `{hub, bottleneck}` 2-cut. **So the lift from
undirected 3-connectivity to `repo-λ≥3` genuinely needs the orientation of the
tree-routing, which 3-connectivity alone does not supply.** This is the precise
reason the Menger-lift is hard, and why (R1) — a purely undirected cut argument —
cannot finish it.

### Empirical sharpening

- For `k=2`, the inter-component cross count is **`m=2` in every truth-set member**
  (`m=1` occurs only between components in `k≥3` layouts). So the `k=2` case is the
  `m=2` case: exactly 4 cross arcs, on 4 distinct underlying edges.
- **Step 1b stress test (exact):** all 3-connected 2-extremal digraphs on `n≤7`
  (= wheels `W₃..W₆`) have **connected `F_D`** (0 disconnected) — consistent with
  the lemma.

## Try 1 (2026-06-03c) — the opposite-cross attack: discriminator pinned, lift still open

Attacking the `k=2`, `m=2`, opposite-cross Menger-lift directly. Two outcomes.

### (R3) Both *arc* parities are NECESSARY but INSUFFICIENT (the sufficient condition is *both constraint parities* = opposite-cross). **[VERIFIED 25/25 necessary direction]**

> **Correction (post-review, see R5):** the "both parities" here is at the
> **arc** level (cross arcs of each `δ`). R5's `K4` example has both arc-parities
> yet `χ⃗=2`, so arc-level "both parities" is **necessary but not sufficient**. The
> sufficient/correct condition is R6's **both *constraint* parities** (actual
> monochromatic cross dicycles). The 25/25 below is genuine but is the necessary
> direction only.

Colour each component by its bipartition (baseline `x=0`); a cross single arc
`e` between `V_0,V_1` has **parity** `δ(e) = side₀(end₀) ⊕ side₁(end₁)`. A
monochromatic cross dicycle uses only cross arcs of one parity `δ` and imposes
`x_0⊕x_1=δ`. So **full cover of the `k=2` flip cube via cross dicycles ⟺ cross
arcs (and closing monochromatic paths) of *both* parities `δ=0,1` exist** =
"opposite-cross".

- **Genuine `k=2` 2-extremal members: both parities present in 25/25.**
- **The two-star near-misses have only `δ=0`** — *structurally*: their single cover
  sits on the star **leaves**, all on the outer bipartition side, so every cross
  arc is leaf↔leaf ⇒ `side=side` ⇒ `δ=0`. A `δ=1` arc must touch a **non-outer**
  vertex (in a star, the hub). This is exactly why the near-misses are 3-connected
  yet `χ⃗=2`, and why they are **not** counterexamples: they miss the second parity.
- With `m=2`, the two forward cross arcs then carry **different parities** (one
  `δ=0`, one `δ=1`); verified across all 25.

So the discriminator between "3-connected near-miss (`χ⃗=2`)" and "genuine
2-extremal (`χ⃗=3`)" is precisely the **second cross-parity**, which forces a cross
arc onto an inner (non-uniform-side) vertex.

### (R4) What remains. **[GAP]**

The lift is now sharpened to:

> **opposite-cross target.** `k=2`, `m=2`, strong, Eulerian, `U(D)` 2-connected,
> repo-`λ≤2`, cross arcs of **both** parities ⇒ `U(D)` has a vertex 2-cut.

This is no longer refutable by the leaf-only near-misses (they lack the second
parity). But I could not close the implication "both parities ⇒ 2-cut": the second
parity forces an inner-touching cross arc, yet turning that into the
`{hub, bottleneck}` 2-cut still needs the directed tree-routing argument of (R2).
The casework (which forward/backward arc carries which parity, where the closing
monochromatic paths run) is finite but did not collapse to a uniform cut.

**Net of try 1:** the discriminator is now an exact, verified algebraic condition
(both cross-parities), explaining the near-misses precisely; the remaining proof
obligation is the strictly smaller "both-parity ⇒ 2-cut" statement, still gated on
the (R2) orientation step.

## Verdict

I do not currently have a rigorous proof of the no-full-cover lemma. (R1) is a
rigorous partial; (R2) localises the obstruction to the tree-routing orientation;
(R3) pins the exact discriminator (both cross-parities, verified 25/25) and
explains why the near-misses are not counterexamples; (R4) is the remaining
"both-parity ⇒ 2-cut" gap. The honest next target is (R4) — smaller than before,
but still open and still gated on the directed-routing step.

## Try 2 (2026-06-03d) — R4 as phrased is false; corrected R4 survives

Attempting to grind the finite `k=2,m=2` casework exposed a necessary correction.

### (R5) "Both arc parities" is too weak. **[REFUTED]**

There is a 4-vertex example:

```text
digons: 0<->1, 2<->3
single arcs: 0->2, 1->3, 3->0, 2->1
```

Its underlying graph is `K4`, so `κ(U)=3`; it is strong, Eulerian with
`indeg=outdeg=2`, and repo-`λ=2`. The four cross single arcs have both parities:

```text
0->2, 1->3 have δ=0; 3->0, 2->1 have δ=1.
```

But the single arcs form one directed 4-cycle using **both** parities at once.
No monochromatic cross-dicycle constraint is produced:

```text
mode=none, covered=False, chi_vec=2, vertex_2_cuts=[]
```

So the R4 shorthand

```text
both cross-arc parities present => vertex 2-cut
```

is false. This does **not** refute Step 1b, because Step 1b needs full flip-cover,
not mere parity occurrence among arcs.

### (R6) Corrected R4. **[SUPPORTED n<=6 exact; proof still open]**

The correct finite target is:

> **corrected opposite-cross target.** `k=2`, `m=2`, strong, Eulerian
> `indeg=outdeg>=2`, `U(D)` 2-connected, repo-`λ<=2`, and **both constraint
> parities** occur (i.e. actual same-parity cross dicycles impose
> `x_0 xor x_1 = 0` and `x_0 xor x_1 = 1`) ⇒ `U(D)` has a vertex 2-cut.

Equivalently, "both parity classes occur among cross arcs" must be replaced by
"both parity classes occur as bad partial assignments of simple single dicycles."

The new script `scripts/r4_opposite_cross_casework.py` makes this distinction
explicit and exhaustively enumerates labelled `k=2,m=2` completions through `n=6`.
Result:

```text
both arc parities but not cover: one K4 example printed above
opposite-cross + side hypotheses + repo-lambda<=2 + U 2-connected:
  n=6, |V0|=1: 240 examples, all kappa_U=2
  n=6, |V0|=3: 144 examples, all kappa_U=2
R4 counterexamples through n<=6: 0
```

All opposite-cross examples with `κ(U)>=3` in this exact search have
repo-`λ=3`, not `<=2`. Representative certificate:

```text
digon tree components:
  T0 = edge 0-1
  T1 = star 2-{3,4,5}
cross arcs:
  0->3, 1->3, 4->0, 5->1
internal singles:
  3->4, 3->5
```

Here the two bad dicycles are `0->3->4->0` and `1->3->5->1`; the tree edge
`2<->3` has three arc-disjoint directed `2->3` paths:

```text
2->3
2->4->0->3
2->5->1->3
```

Thus repo-`λ>=3`. This is exactly the directed-detour mechanism the proof needs.

### (R7, reformulated 2026-06-03e) Shared-junction lemma. **[invariant census-verified (not proved); implication OPEN]**

R7's original "a digon-tree edge spanned by both dicycles" is **wrong** (in its own
certificate the constraint dicycles use no digon-tree arc). Reformulated around the
verified shared-vertex invariant:

> **Shared-junction invariant [VERIFIED on the `κ_U≥3` `n≤6` census; SUPPORTED on
> the truth set — not proved].** In a `k=2,m=2` opposite-cross configuration the two
> opposite-parity constraint dicycles `C₀,C₁` share at least one vertex `w`.
> *Census:* **2784/2784** over `κ_U≥3`, `n≤6`. On the genuine `κ_U=2` truth-set
> members it holds in **23/25**; the two exceptions are genuine layouts with
> vertex-disjoint opposite-parity cycles, not enumeration artefacts. Thus shared
> junction is a property of the searched 3-connected subfamily, not of
> opposite-cross configurations in general.

> **Shared-junction lemma (target, OPEN).** If additionally `U(D)` has no vertex
> 2-cut, then the figure-8 at `w` (two dicycles meeting at `w`) **plus** the digon
> trees yield an ordered pair with three arc-disjoint directed paths, so
> repo-`λ(D)≥3`.

Two facts make this the honest form, and show why it is **not** a single clean
detour identity:

1. **Shared-`w` is necessary but not sufficient.** It holds in the genuine `κ_U=2`,
   `λ=2` members too (23/25) — there the would-be third path is bottlenecked by the
   2-cut. So the operative hypothesis is *shared-`w` **and** no 2-cut*; `w` alone
   gives nothing.
2. **The 3-path construction is configuration-dependent.** The certificate's tidy
   case — `w` a leaf, its digon-neighbour hub `h` reaching a vertex of each
   dicycle, giving 3 arc-disjoint `h→w` paths — covers only **96/2784** of the
   `κ_U≥3` census. In the remaining majority the repo-`λ=3` witness pair lies *among
   the dicycle vertices* (e.g. `n=5`: dicycles `0→1→4→0`, `0→2→3→0` share `w=0`, but
   the 3 arc-disjoint paths run between `1` and `2`), combining the figure-8
   junction with a digon-tree route. There is **no uniform "tree edge with two
   detours"** pattern.

So the reformulation pins the **verified invariant** (shared junction `w`) and the
**exact open implication** (`w` shared + no 2-cut ⇒ repo-`λ≥3`), but it is *not* a
proved lemma and does *not* reduce to one explicit detour. Closing it is still the
(R2) directed-routing step — now anchored at the junction `w` rather than a tree
edge.

**Honest smallest target, current form:** `k=2,m=2` opposite-cross with the two
constraint dicycles sharing `w`, and `U(D)` 2-connected with no 2-cut ⇒
repo-`λ(D)≥3`. Verified exactly `n≤6` (0 counterexamples); proof open.

## Proof attempt — singleton subcase (2026-06-03f). **[clean reduction; core still open]**

The cleanest entry is `|V_1|=1`, say `V_1={z}` (`z` isolated in `F_D`: in-arcs
from `s_1,s_2`, out-arcs to `q_1,q_2`, all single, `m=2`).

**(S1) Reduction [PROVED + VERIFIED 10/10].** `U(D)−z = U(D[V_0])`. If `U(D[V_0])`
has a cutvertex `c`, then `{z,c}` is a vertex 2-cut of `U(D)`. So in the singleton
subcase, *Step 1b reduces to: `U(D[V_0])` has a cutvertex.* Verified on all 10
singleton-component `k=2` truth-set members (`U(D[V_0])` has connectivity exactly 1
in every case).

**(S2) Chord structure [PROVED].** In `D[V_0]` the vertices `s_i` get in-excess `+1`
("sinks"), `q_j` out-excess `+1` ("sources"); the intra-`V_0` single arcs (chords)
carry exactly this excess. A monochromatic constraint path uses **only same-side
chords** (a digon/tree edge flips the proper 2-colouring, so cannot be
monochromatic). Opposite-cross therefore forces a same-side chord-path on **each**
bipartition side of `T_0`. Min-degree-2 forces every tree-leaf of `T_0` to be a
cross-endpoint or carry a chord.

**(S3) The residual [OPEN].** Prove `U(D[V_0]) = T_0 + (within-side chords)` has a
cutvertex whenever repo-`λ(D)=2`. This did not close: same-side chords can in
principle patch the tree toward 2-connectivity, and ruling that out needs
repo-`λ=2` in the directed-routing way of (R2) — the same wall.

**Method note (a caught error).** A brute-force "find a 3-connected singleton-`z`
2-extremal" search first reported 6 hits; on inspection all were **classical
wheels** mis-generated by a digon-merge bug (`s_i = q_j` makes `z` non-singleton).
Corrected (forcing `z` isolated in `F_D`): **0** counterexamples — but the
corrected construction only reached `n≤6`, below the real singleton examples
(`n≥7`), so it is consistent-with but not a proof of S3.

## Overall verdict (2026-06-03f)

After R1–R7, the reformulation, and the singleton attempt, the 3-connected
sub-theorem ("3-connected 2-extremal ⇒ generalised wheel", = the 3-connected case
of Conjecture 9.2) is **not closed**, and every reduction re-hits the same
directed-routing/orientation wall (R2). What *is* secured and reusable:
proved P1, L0, the assembly, R1, R5's correction, the shared-junction invariant
(census-verified), and the clean singleton reduction S1+S2. The remaining core
(S3 / the shared-junction lemma) is genuine open research — it is a special case
of a published open conjecture — and is unlikely to fall to further short attempts.

**Historical status (superseded 2026-06-07).** At this point only the assembly
was banked. The later conditional structural lemma proves Steps 2–4 once `F_D`
is connected, and the two-component exclusion below closes the R6/R7 case.
See the current theorem inventory in `docs/three_connected_wheel.md`.

## Criticality closure of the two-component case (2026-06-07). **[PROVED]**

The earlier R6/R7 routing wall can be bypassed once the full 3-dicriticality of a
2-extremal digraph is used.

If `F_D` has exactly two components, an internal bad dicycle is impossible:
it is monochromatic under every proper forest colouring, so deleting any single
arc outside it would leave `χ⃗=3`, contradicting arc-criticality; if no such arc
exists, the two digon components are not joined. Thus full cover is necessarily
opposite-cross.

Arc-criticality then forces the single arcs to be **exactly two arc-disjoint
directed cycles**, one for each relative flip parity. For each digon-tree edge,
T2 supplies a tight `(1,3)` cut; its two crossing single edges belong to exactly
one of the two cycles. Hence, inside each digon tree, the two cycles' Steiner
subtrees are edge-disjoint. The unique connector path between them has one vertex
bottleneck; choosing one bottleneck in each digon component gives a vertex 2-cut.
Therefore:

> **Two-component exclusion theorem.** A 3-connected 2-extremal digraph cannot
> have exactly two components in its digon forest.

The full proof is in `docs/three_connected_wheel.md`, Step 1a. This supersedes
R7 as an open target in the `k=2` case. The remaining Step 1 frontier is
`k(F_D)≥3`.

The same argument gives a general **critical-cover lemma**: every single arc has
a private flip assignment under which all monochromatic dicycles contain that
arc. Hence the union of any bad-dicycle cover of the component-flip cube is
exactly the whole single-arc subdigraph. For `k(F_D)=3`, selecting one bad
dicycle per flip reduces `S` to the union of at most four dicycles. This is the
current smallest open case.

## Three-component line-cover exclusion (2026-06-07). **[PROVED]**

The three-member branch of that `k=3` reduction is now closed.

If a bad dicycle visits exactly two digon components, its bad set is an affine
line of the two-dimensional flip cube, and a minimum cover has three members.
The line member is arc-disjoint from the other two: otherwise the two cycles
contain a directed theta whose branch vertices lie in one digon component, and
the bidirected tree path between them gives a third arc-disjoint directed path,
contradicting repo-`λ≤2`. Balance then forces the remaining two cycles to be
arc-disjoint as well.

T2 consequently makes the three cycle-Steiner subtrees edge-disjoint in every
digon tree. For each of the two components visited by the line cycle, take the
Steiner hull of the other two cycle layers. That hull cannot use an edge of the
line cycle's Steiner subtree: the tight cut at such an edge would be crossed
only by the line cycle and would place the other two cycles on opposite sides,
whereas the finite affine cover classification gives those cycles a common
outside digon component and forces them onto the same side. The line subtree
and the other-layer hull therefore have one connector bottleneck in each of the
line's two components. Those two bottlenecks form a vertex 2-cut.

Therefore:

> **Line-cover exclusion theorem.** In a 3-connected 2-extremal digraph with
> `k(F_D)=3`, every bad dicycle visits all three digon components.

The exact remaining `k=3` core is now the **pure point cover**: four
full-support bad dicycles, one for each flip, and no two-component bad dicycle.
The earlier gaps (cover overlap and the connector 3-cut) survive only in that
configuration. The complete proof is in `docs/three_connected_wheel.md`,
Step 1c.

The pure-point core splits cleanly:

- if the four selected cycles overlap, their excess multiplicity is a nonzero
  balanced circulation; the target is to show that this forces repo-`λ≥3`;
- if they are arc-disjoint, criticality makes each selected cycle the **unique**
  bad dicycle at its flip. This branch is now **excluded**: T2 makes every cycle
  layer peripheral to the hull of the other three in each digon tree. Tree
  medians in any two components give three disjoint fan arms to the same three
  cycles, and the corresponding directed cycle segments join them into three
  arc-disjoint paths. Hence repo-`λ≥3`.

Both boundaries are realized by explicit 9-vertex, 3-connected, 3-dicritical
pure-point examples in `scripts/step1_two_component_exclusion.py`: one
overlapping and one arc-disjoint. Both have repo-`λ=3`, no line-bad dicycle, and
exactly four bad dicycles. The arc-disjoint example is now a sharp witness for
the proved three-fan lemma. The **sole remaining `k=3` case** is the overlapping
pure-point cover.

## Review (2026-06-03e) — R5/R6 solid; R7 mis-stated; cleaner invariant found

Verified the corrected work and stress-tested R7:

- **R5 (K4 counterexample): CONFIRMED.** `U=K4`, `κ=3`, strong Eulerian min-deg-2,
  repo-`λ=2`, `MC=0`, `F_D` disconnected, both **arc**-parities, yet `χ⃗=2` (the
  singles form one mixed-parity 4-dicycle, no monochromatic constraint cycle). A
  genuine counterexample to the arc-level R4.
- **R6 (corrected target): CONFIRMED.** Exact census `n≤6`: 0 counterexamples, and
  **every** opposite-cross example with `κ_U≥3` has repo-`λ=3` (never `≤2`). The
  representative certificate checks out: pair `(2,3)` has `maxflow=3` via `2→3`
  (digon) + `2→4→0→3` + `2→5→1→3`.
- **R7 (detour-edge lemma): the STATEMENT is wrong / non-uniform.** In R7's own
  certificate the two constraint dicycles `0→3→4→0`, `1→3→5→1` use **only cross and
  internal-single arcs — no digon-tree edge**. So "a digon-tree edge `a↔b` spanned
  by the two dicycles in the same direction" does **not** hold: the 3 arc-disjoint
  `2→3` paths use tree edges `2-3, 2-4, 2-5`, but the *dicycles* span none of them.
  The actual mechanism is: a vertex `w` lies on **both** constraint dicycles, and a
  digon-neighbour `h` of `w` is also digon-adjacent to a vertex of each dicycle, so
  `h→w` gets the digon arc plus one detour per dicycle.
- **Cleaner invariant [VERIFIED].** *The two opposite-parity constraint dicycles
  share a common vertex* — **2784/2784** across all `κ_U≥3` opposite-cross examples
  `n≤6` (and 23/25 of the genuine `κ=2` truth-set members). The two truth-set
  misses are genuine vertex-disjoint cycle pairs. This shared vertex is `w`
  above; it is a census feature of the 3-connected subfamily, not a general
  opposite-cross invariant.

**Net of review:** the *target* (corrected R6) is right and well-supported; the
*proposed lemma* (R7) needs restatement around the shared-vertex `w`, and the
remaining gap is unchanged in spirit — deriving the third arc-disjoint `h→w` path
from `w` shared + no-2-cut is again the (R2) digon-tree routing step. So R7 is not
yet a correct stand-alone lemma; the honest smallest target is:

> `k=2,m=2` opposite-cross, the two constraint dicycles share `w`; if `U(D)` has no
> 2-cut then the digon-tree component of `w` supplies a third arc-disjoint route
> into `w`, forcing repo-`λ≥3`.
