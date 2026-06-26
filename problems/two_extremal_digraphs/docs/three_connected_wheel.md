# 3-connected 2-extremal ⇒ generalised wheel — proof attempt along the 4-step route

Date: 2026-06-03. Target sub-theorem (the 3-connected case of Conjecture 9.2,
reached **without** invoking the full conjecture):

> **Theorem (target).** If `D` is 2-extremal and `U(D)` is 3-connected, then `D`
> is an empty-A 2-Hajós tree join — i.e. a **generalised wheel**.

Route (reviewer's): **(1)** `F_D` is a spanning tree; **(2)** the single arcs form
one simple directed cycle; **(3)** that cycle's vertex set is exactly the leaves of
`F_D`; **(4)** the even leaf-parity / plane-order condition holds. Then `D` is an
empty-A tree join by definition.

Tags: **[PROVED]**, **[VERIFIED]** (exhaustive on the corpus), **[GAP]**.

## Standing facts

`D` 2-extremal ⇒ Eulerian (`indeg=outdeg≥2`), strong, `U(D)` 2-connected (here
3-connected), `λ=2`, `χ⃗=3`, 3-dicritical. `F_D` (digon graph) is a **forest**
(proved earlier); `S` (single arcs) is **balanced** (`s⁺(v)=s⁻(v)=:s(v)`).

**Corpus for verification.** All 3-connected 2-extremal digraphs on `n=4..7`
(exact, via the Eulerian-pruned enumerator `scripts/planarity_search.py`; at `n≤7`
these are exactly the classical wheels `W₃..W₆`) **plus** non-classical 3-connected
generalised wheels built directly (`n=10` 3-regular, `n=13` root-of-three-triples).
Result: **Steps 1, 2, 3 all hold on 15/15** of the `n≤7`+`n=10` corpus, and on the
`n=13` example; `is_generalised_wheel` confirms 15/15; `F_D` disconnected in 0
cases. Forward-direction check (`planarity_search.py`): among **all** 3-connected
graphs `n=5,6,7`, every graph admitting a 2-extremal orientation does so only as a
generalised wheel (0 exceptions). *Side finding:* empty-A trees that **violate
even leaf-parity** (e.g. a root with children `{leaf, two-leaf-stars}`) produce
digraphs that are **not 2-extremal** — confirming Step 4's parity is *necessary*
for 2-extremality, not an extra assumption.

## Proved ingredients

### (P1) 3-connected ⇒ `MC=0`. **[PROVED]**

`U(D)` 3-vertex-connected ⇒ `U(D)−v` 2-connected ⇒ bridgeless ⇒ deleting one edge
keeps it connected. So no `(vertex, single edge)` cut: `MC(D)=0`.

### (L0) Colouring lever. **[PROVED]**

In any 2-dicolouring of `D`, the two endpoints of every digon get **different**
colours (a monochromatic digon is a monochromatic 2-dicycle). So a 2-dicolouring
restricts to a **proper 2-colouring of `F_D`**. As `F_D` is a forest it is
bipartite, so proper 2-colourings exist; `χ⃗(D)=3` says **none** of them makes both
single-arc classes acyclic. If `F_D` is a *spanning tree* (Step 1), its proper
2-colouring is **unique** up to swap, pinning the colour classes.

### (Assembly) Steps 1–4 ⇒ generalised wheel. **[PROVED — by Def 9.1]**

If `F_D` is a spanning tree `T`, `S` is a single directed cycle whose vertex set is
`leaves(T)` in an order realisable by a plane embedding of `T`, and every
leaf-to-leaf path of `T` has even length, then setting all tree edges `=B` (digons)
and the cycle `=` rim gives exactly the empty-A 2-Hajós tree join `T(\,;C)` whose
underlying digraph is `D`. So `D` is a generalised wheel.

## The four steps

### Step 1 — `F_D` is a spanning tree. **[OPEN — the irreducible χ⃗=3 core; proven to need colouring]**

`F_D` is a forest (known); spanning tree = connected + spanning.

**Reformulation [PROVED].** `F_D` is a spanning tree ⟺ `U(D)` has **no digon-free
cut** (a vertex bipartition `(S,S̄)` with no digon crossing). (`F_D` disconnected
or non-spanning ⇒ the cut `(C, ·)` around any `F_D`-component `C` is digon-free;
conversely a spanning tree crosses every cut, so all digons-within-components ⇒ a
digon-free cut ⇒ `F_D` disconnected.)

**Cut-floor [PROVED].** From uniform `λ_D=2` (T2), `λ̄_D=2`, so by (T1) **every**
vertex cut has `d_S + |E_U(S)| ≥ 4`. A digon-free cut (`d_S=0`) therefore has
`|E_U(S)| ≥ 4`, i.e. `m ≥ 2` single arcs each way; and (R1) `3`-connectivity forces
`≥3` cross-endpoints on each side.

**Why connectivity/λ alone cannot finish Step 1 [PROVED — a meta-obstruction].**
The two-star **near-miss** (`scripts/step1b_fd_connectivity.py`) is a digraph that
satisfies **every** structural hypothesis available — `U` 3-connected, a digon-free
cut (disconnected `F_D`), `MC=0`, uniform `λ_D=2`, `λ'(U)≤4` — yet has **`χ⃗=2`**
(verified). So no argument from connectivity, `MC`, or arc-/edge-connectivity can
exclude a digon-free cut; **`χ⃗=3` is indispensable.** A natural sufficient
universal target is:

> **Colouring target:** under all standing side hypotheses, `U` 3-connected +
> digon-free cut + uniform `λ_D=2` ⇒ `χ⃗(D) ≤ 2`.

Its contrapositive on the target class gives Step 1. Conversely, a
3-connected 2-extremal counterexample to Step 1 would refute this target, so the
two universal statements have the same counterexamples once all standing
hypotheses are retained. This is the published `k=2` seam-existence colouring
core. The near-miss shows that a proof must genuinely use `χ⃗=3`; it does not
identify a particular colouring construction as necessary.

**Colouring-lemma attempt (2026-06-07) — useful sufficient construction, but not
an equivalence.**
A natural 2-dicolouring of `D` given a digon-free cut `(S,S̄)`: **(I)** flip
`F_D`-components so that every cross single arc is **bichromatic** (endpoints of
different colour), then **(II)** each side has no monochromatic single-dicycle.
Then no monochromatic dicycle can cross the cut, and (II) kills the within-side
ones — a valid 2-dicolouring, i.e. `χ⃗≤2`.

- **(I) is solvable ⟺ the cross-arc parity requirements are consistent.** Each
  cross arc `s→t` imposes `x_{C(s)} ⊕ x_{C(t)} = 1 ⊕ base(s) ⊕ base(t)`; (I) is
  this 2-colouring system on the `F_D`-components, solvable iff no inconsistent
  component-cycle. *Verified:* the near-miss has all cross arcs requiring the same
  parity (consistent) and (I) succeeds (`χ⃗=2`, both 2-dicolourings make all 4
  cross arcs bichromatic).

The converse is false. R5's 4-vertex `K4` example has inconsistent cross-arc
equations (both arc parities occur), but it is **not** opposite-cross and has
`χ⃗=2`: its one single dicycle mixes the two arc parities. Thus failure of (I)
only says that this particular sufficient construction fails. It does not imply
`χ⃗=3`, full flip-cover, or the shared-junction configuration.

The valid equivalence is narrower: when `F_D` has exactly two components, there
is no internal bad dicycle, and the flip cube is fully covered, the two relative
flip classes must be covered by opposite-parity cross dicycles. This is the
`opposite-cross` mode of R6. The shared-junction property was only census-verified
inside the 3-connected opposite-cross subfamily; it was never equivalent to the
general colouring lemma.

### Step 1a — exactly two digon components are impossible. **[PROVED 2026-06-07]**

> **Two-component exclusion theorem.** If `D` is 2-extremal and `U(D)` is
> 3-connected, then `F_D` does not have exactly two components.

*Proof.* Write the two digon-tree components as `T_0,T_1`.

1. **Internal mode is impossible by 3-dicriticality.** An internal bad
   single-dicycle is monochromatic under every proper 2-colouring of `F_D`.
   If a single arc `e` lies outside that dicycle, the same dicycle survives in
   `D-e`, contradicting `χ⃗(D-e)=2`. Hence every single arc would lie on that
   internal dicycle, leaving no single arc between `T_0,T_1`, contrary to
   strong connectivity. Therefore there is no internal bad dicycle.

2. **The singles are exactly two arc-disjoint dicycles.** There are only two
   proper forest colourings up to global swap, indexed by the relative flip
   `δ∈{0,1}`. Since `χ⃗(D)=3`, each relative flip has a monochromatic cross
   dicycle; call the corresponding families `𝒞_0,𝒞_1`. For every single arc
   `e`, 3-dicriticality gives a proper forest colouring of `D-e`. Under its
   relative flip `δ`, every dicycle in `𝒞_δ` must contain `e`. Hence every
   single arc belongs to
   `K_0∪K_1`, where `K_δ=⋂_{C∈𝒞_δ}E(C)`.
   Choose `C_δ∈𝒞_δ`. Then
   `E(S)⊆E(C_0)∪E(C_1)`, while the reverse inclusion is immediate, so equality
   holds. Since `S` is balanced, `E(C_0)∩ E(C_1)` is a balanced subgraph of a
   simple directed cycle; it is therefore empty or the whole cycle. The latter
   would give the same cross-parity, impossible. Thus `C_0,C_1` are arc-disjoint,
   `S=C_0⊔C_1`, and each `𝒞_δ` consists only of `C_δ`.

3. **T2 separates the two cycle-Steiner subtrees.** Fix a tree edge
   `e=uv` of `T_i`. A tight cut separating `u,v` has
   `d+|δ_U|=4`. It cannot have `d=0`, and `d≥2` together with
   `|δ_U|≥3` would give an even sum at least `6`; hence it has type `(1,3)`.
   Its sole crossing digon is `e`, so it is obtained from one component of
   `T_i-e` by placing the whole other digon tree on one side. Exactly two single
   edges cross. Each directed cycle crosses an undirected cut evenly, so exactly
   one of `C_0,C_1` crosses this cut, and it crosses twice. In particular, the
   two cycles cannot both have vertices on both sides of `T_i-e`. Equivalently,
   `e` cannot lie in both of the two Steiner subtrees
   `R_{iδ}=Steiner_{T_i}(V(C_δ)∩V(T_i))`.
   Therefore `R_{i0},R_{i1}` are edge-disjoint. In the tree `T_i` there is a
   unique connector path `P_i` between them; it may have length zero when the
   two subtrees meet in one vertex.

4. **The two connector bottlenecks give a 2-cut.** For each `i`, choose a vertex
   `w_i` on `P_i`: an internal vertex if one exists; if `P_i` is a single edge,
   choose its endpoint in `R_{i0}`; if it has length zero, choose the common
   vertex. Every path from the `C_0`-Steiner layer to the `C_1`-Steiner layer
   must use `P_0` or `P_1`, because all tree routes stay inside one `T_i` and
   every single arc lies on `C_0` or `C_1`. Hence deleting `{w_0,w_1}` separates
   the two layers. Both leave a vertex: each `C_δ` is a simple dicycle of length
   at least three, so deleting at most its two chosen connector endpoints cannot
   erase it completely. This contradicts 3-connectivity. ∎

So the open Step 1 is now reduced to excluding **at least three** components of
`F_D` (and in particular includes the digon-free-vertex cases). The
two-component opposite-cross/shared-junction wall is closed by criticality plus
the tight-cut identity; no directed path casework is needed.

### Step 1b — critical-cover lemma for the remaining cube. **[PROVED]**

Let `F_D` have `k≥2` components and identify proper forest colourings up to global
swap with the `(k-1)`-dimensional flip cube `Ω`.

> **Critical-cover lemma.**
> 1. There is no internal bad dicycle (one monochromatic under every flip).
> 2. For every single arc `e`, there is a flip `x_e∈Ω` such that **every**
>    `x_e`-monochromatic single dicycle contains `e`.
> 3. Consequently, if `𝒦` is any collection of bad single dicycles whose bad
>    subcubes cover `Ω`, then
>    `E(S)=⋃_{C∈𝒦}E(C)`.

*Proof.* For (1), an internal bad dicycle survives `D-e` for every single arc
outside it, contradicting 3-dicriticality. If every single arc lies on it, no
single arc joins its `F_D`-component to the others, contradicting strong
connectivity. For (2), take a 2-dicolouring of `D-e`; all digons remain, so it is
a proper forest colouring, hence a flip `x_e`. Any `x_e`-monochromatic dicycle
not using `e` would survive in `D-e`, impossible. For (3), some member of the
cover `𝒦` is bad at `x_e`, and by (2) it contains `e`. Thus every single arc lies
in the union; the reverse inclusion is immediate. ∎

This recovers the two-cycle reduction when `k=2`.

> **Three-component cube classification [PROVED].** If `k=3`, a minimum bad-cycle
> cover has either:
> - exactly **three** dicycles, if any bad dicycle visits only two components; or
> - exactly **four** dicycles, all visiting all three components (one for each
>   flip), otherwise.

Indeed `|Ω|=4`. With internal bad dicycles excluded, a dicycle visiting two
components covers two flips (an affine line of the square), while one visiting
all three covers one flip. A two-member cover would have to be two complementary
parallel lines, hence two cycles using the same pair of `F_D`-components. By the
critical-cover lemma their union would contain every single arc, leaving the
third component unjoined and contradicting strong connectivity. Thus a minimum
cover has size at least three. If a line is available, it plus one bad set through
each uncovered point gives a three-member cover; if no line is available, all bad
sets are points and all four are required.

Consequently, for `k=3` the whole single-arc subdigraph is the union of either
three covering dicycles, or four full-support dicycles. The four known `k=3`
truth-set members are all in the three-dicycle case (two codimension-one
constraints plus one full-support constraint); in all four, those three dicycles
are arc-disjoint and partition `S`.

### Step 1c — the three-cycle `k=3` branch is impossible. **[PROVED 2026-06-07]**

> **Line-cover exclusion theorem.** If `F_D` has three components in a
> 3-connected 2-extremal digraph, then no bad dicycle can visit exactly two
> components. Equivalently, the minimum cube cover cannot have three members.

*Proof.* Suppose a minimum cover is `C_0,C_1,C_2`, where `C_0` is a line
constraint supported on digon components `T_a,T_b`.

1. **The three cover dicycles are arc-disjoint.** A bad dicycle `C` determines,
   for every two components that it visits, one affine equality between their
   flips. Hence, if two bad dicycles have bad sets whose union contains at least
   three cube points, all their common vertices lie in at most one digon
   component: common vertices in two components would force both bad sets into
   the same two-point affine line.

   In an essential three-set cover of the square, the union of the bad set of
   `C_0` with that of either other member has at least three points. If `C_0`
   shared an arc with `C_j`, the two distinct directed cycles would contain a
   directed theta: two arc-disjoint directed paths between two common vertices.
   Those common vertices lie in one `T_i`, whose bidirected tree path supplies a
   third arc-disjoint path, contradicting `λ_D≤2`. Thus `C_0` is arc-disjoint
   from `C_1,C_2`.

   Now
   `(\mathbf1_{C_0}+\mathbf1_{C_1}+\mathbf1_{C_2})-\mathbf1_S`
   is a nonnegative balanced circulation, because every `C_j` and `S` is
   balanced. Since `C_0` has no overlap, this circulation is exactly
   `C_1∩C_2`. A balanced subgraph of a simple directed cycle is empty or the
   whole cycle. The latter would give `C_1=C_2`, impossible in an essential
   cover. Hence `S=C_0⊔C_1⊔C_2`.

2. **T2 gives a Steiner tiling.** For a tree edge `e` of `T_i`, a tight cut
   separating its endpoints has type `(1,3)`: its only crossing digon is `e`
   and exactly two single edges cross. Each cover cycle crosses an undirected
   cut evenly, so exactly one `C_j` crosses. Therefore the Steiner subtrees
   `R_{ij}=Steiner_{T_i}(V(C_j)∩V(T_i))` are pairwise edge-disjoint.

3. **The other two layers have a hull disjoint from the line layer.** Fix
   `i∈{a,b}` and let `H_i` be the Steiner hull in `T_i` of all terminals of
   `C_1,C_2` that lie in `T_i`. We claim `E(R_{i0})∩E(H_i)=∅`.
   Otherwise take an edge `e` in the intersection. The tight cut for the
   endpoints of `e` is crossed by `C_0`, since `e∈R_{i0}`; `C_0` therefore
   consumes its two crossing single edges, so neither `C_1` nor `C_2` crosses.
   Pairwise Steiner edge-disjointness says that `e∈H_i` can only mean that
   `C_1` and `C_2` lie on opposite sides. But whenever both have terminals in
   `T_i`, the finite three-cover classification gives them a common component
   `T_h` with `h≠i` (two point constraints; or a line and a point sharing the
   line's other component). The tight cut crosses no digon in `T_h`, so all of
   `T_h` is on one side and `C_1,C_2` must be on that same side, a contradiction.

4. **Two hull bottlenecks form a 2-cut.** In each of `T_a,T_b`, the connected
   subtrees `R_{i0}` and `H_i` are edge-disjoint and therefore have a unique
   connector path (possibly of length zero). Choose one bottleneck vertex `w_i`
   on it, exactly as in Step 1a. Every path from the `C_0` layer to either other
   layer must pass through `w_a` or `w_b`: tree paths stay in one digon
   component, `C_0` has no vertex in the third component, and switching between
   arc-disjoint cover cycles can occur only at a common vertex, which is the
   zero-length connector and is chosen as `w_i`. Deleting `{w_a,w_b}` separates
   a remaining vertex of `C_0` from a remaining vertex of `C_1∪C_2`, contrary
   to 3-connectivity. ∎

Thus the `k=3` frontier is now the single **pure point-cover** configuration:

> there is no two-component bad dicycle, and `S` is the union of four
> full-support bad dicycles, one for each flip.

This closes both former gaps (G1) and (G2) for the entire three-cycle branch.
They remain open only for the four-full-support branch. For `k≥4`, the cover can
have more complicated affine subcubes and remains open.

### Step 1d — exact residual `k=3` core. **[PARTIAL — open]**

Write the four flips as `x∈Ω` and choose an `x`-bad full-support dicycle `C_x`.
The critical-cover lemma gives `S=⋃_{x∈Ω}C_x`. There are now exactly two cases.

1. **Overlap case.** The nonnegative multiplicity
   `H=Σ_x 1_{C_x}-1_S` is a nonzero balanced circulation. Hence its support
   contains a directed cycle all of whose arcs occur in at least two point
   constraints.

   There is a useful normalization. If the support of `H` contains a bad
   dicycle `Q` at flip `x`, replace `C_x` by `Q`. This is still a cube cover, so
   the critical-cover lemma says its union is still all of `S`. Moreover every
   edge of `Q` remains in one of the other three cycles: before replacement it
   had multiplicity at least two, and removing the old `C_x` deletes at most one
   copy. Thus `Q` is a **covered point cycle** and the other three cycles already
   union to `S`.

   If those three supplier cycles are arc-disjoint, the three-fan argument from
   case 2 below applies to them directly and gives repo-`λ≥3`. If two suppliers
   contain a directed theta whose branch vertices lie in one digon component,
   its two directed branches plus the bidirected tree path again give
   repo-`λ≥3`.
   Consequently the unresolved overlap core has two precise parts:

   > **P4-A (cycle extraction).** The overlap circulation contains a bad
   > dicycle.
   >
   > **P4-B (cross-only suppliers).** In covered-cycle normal form, if the three
   > suppliers overlap but no supplier pair has a same-component directed
   > theta, then repo-`λ_D≥3`.

   This target is sharp. The script contains a 9-vertex pure-point,
   3-connected, 3-dicritical example with overlapping cover cycles and
   repo-`λ=3`; it has exactly four bad dicycles, no line constraint, and is
   already in the covered-cycle/arc-disjoint-suppliers normal form.

2. **Arc-disjoint case. [EXCLUDED]** Then `S=⊔_{x∈Ω}C_x`, and criticality gives
   more than the cover lemma:

   > **Unique-cycle lemma [PROVED].** For each flip `x`, `C_x` is the unique
   > `x`-bad dicycle.

   Indeed, for `e∈E(C_x)`, a 2-dicolouring of `D-e` cannot use another flip
   `y`, because the arc-disjoint cycle `C_y` survives. It must use `x`, so every
   `x`-bad dicycle contains `e`. This holds for every edge of `C_x`; a simple
   dicycle containing all of `C_x` is `C_x` itself.

   T2 makes the four Steiner subtrees `R_{ix}` pairwise edge-disjoint in each
   digon tree. In fact each `R_{ix}` is edge-disjoint from the **hull of the
   other three layers**. If an edge `e` belonged to both, its tight endpoint cut
   would be crossed by `C_x`, so `C_x` would consume the two crossing single
   edges and the other three cycles would not cross. But all three visit every
   other digon component, which lies wholly on one side of the cut; hence they
   all lie on the same side, contradicting `e` being in their hull.

   Fix three cycle labels `x,y,z` and two digon components `T_i,T_j`. In `T_i`,
   the three peripheral subtrees `R_{ix},R_{iy},R_{iz}` have a tree median
   `h_i` with three pairwise edge-disjoint paths to terminals
   `a_{ix},a_{iy},a_{iz}` on the corresponding cycles. The same holds in `T_j`
   from terminals `a_{jx},a_{jy},a_{jz}` to a median `h_j`. For each label,
   concatenate the `T_i` fan arm, the directed segment of its cover cycle from
   `a_{i*}` to `a_{j*}`, and the reversed `T_j` fan arm. The three resulting
   `h_i→h_j` paths are arc-disjoint: their tree arms are disjoint inside each
   component and their single-arc portions lie on arc-disjoint cover cycles.
   Thus repo-`λ_D(h_i,h_j)≥3`, a contradiction.

   So a pure point cover **cannot be arc-disjoint** under repo-`λ≤2`. The
   9-vertex arc-disjoint stress example in the script has repo-`λ=3`, exactly
   as this proof predicts.

Therefore the sole remaining `k=3` target is:

> **P4-overlap target.** A pure four-point cover with nonzero overlap
> circulation forces repo-`λ_D≥3`; equivalently, close P4-A and P4-B above.

Connectivity, criticality, and the affine cover alone do not prove this target:
the explicit overlapping stress witness satisfies them and has repo-`λ=3`.
The decisive unused hypothesis is exactly uniform repo-`λ=2`.

There is also a useful cut reformulation. Replace each digon edge by two parallel
undirected edges and each single arc by one undirected edge, obtaining a
multigraph `M`. T1 says
`λ_M(u,v)=2λ_D(u,v)`. Under the 3-connected target hypotheses, T2 therefore says
that **every pair of vertices of `M` has edge-connectivity exactly 4**. In other
words, `M` is uniformly 4-edge-connected. The pure-point targets can equivalently
be attacked through the global minimum 4-cut structure of `M`, rather than by
choosing tight cuts pair by pair.

A potentially relevant external tool appeared in 2026: L. Xu,
["Uniformly k-edge-connected graphs"](https://doi.org/10.1016/j.disc.2026.115039),
proves a construction theorem from the two-vertex `k`-parallel-edge multigraph.
That theorem is not used above; importing its operations for `k=4` and imposing
the special doubled-forest/single-edge decomposition of `M` is a concrete next
route for P4-A/P4-B.

### Earlier Step 1c attempt (2026-06-07) — obstacle now partly superseded

Attempting the `k=3` proof via cover-classification + T2 exposed a **decisive
obstacle**, and a correction to the earlier plan:

1. **The four `k=3` truth-set members violate T2.** They are `κ(U)=2` (not
   3-connected), and several of their digon fundamental cuts are crossed by **4**
   single edges, not 2 (`L7.8`: digons `0-2` and `0-4` each crossed by 4). T2's
   "exactly two crossings" is a *3-connectivity* property; these members fail it.
   So they are **not models of the 3-connected `k=3` hypothesis** — they cannot
   ground, test, or guide the proof, and the empirical "single-vertex-attachment
   2-cut works 4/4" was measured on the *wrong* class. A genuine 3-connected `k=3`
   digraph has **no examples** (that is the theorem), so the argument must be
   entirely symbolic.

2. **Symbolic gaps identified at that stage:**
   - **(G1) Arc-disjoint cover.** The Steiner-tiling step (each tree edge owned by
     exactly one cover dicycle, hence `R_{ij}` edge-disjoint) needs the cover to be
     arc-disjoint, so that a fundamental cut's two crossing single edges lie on a
     single cover dicycle. For `k=2` arc-disjointness was *forced* (balanced
     subgraph of a simple cycle). For `k≥3` it is **not established**.
   - **(G2) The connector cut over-counts.** Even granting the Steiner-tiling, the
     `k=2` connector construction yields one connector per component = a **`k`-cut**,
     which for `k=3` is a 3-cut — *consistent* with 3-connectivity, hence **not a
     contradiction**. The real contradiction needs the single-vertex-attachment
     2-cut, which is not forced symbolically (and can't be calibrated on data, by
     point 1).

3. **The `d_H(v)∈{0,2}` lever does not extend.** The conditional structural lemma's
   branch argument (`k=1`) used that `U−v`'s only super-nodes are the branches of
   `T−v`; for `k≥2`, the other digon components add `H`-endpoints at `v`, breaking
   the `d_H(v)≤2` count. So that technique is `k=1`-specific.

**Current verdict.** The argument above closes (G1)+(G2) whenever a line
constraint exists. The pure four-point cover still has neither an arc-disjointness
proof nor a two-vertex separator: all four cycles visit all three components, so
the connector construction again gives only a 3-cut. Thus `k=3` is still open,
but only in this one cover type.

**Step-1b attack update (2026-06-03).** The separator-only formulation above is
too strong unless it uses the full `χ⃗=3` obstruction. There are clean near-misses
with disconnected `F_D` and highly connected underlying graph:

- the cyclic regular tournament `T5` has `F_D=∅`, `U(D)=K5` (4-connected),
  `MC=0`, Eulerian/strong, and repo-`λ=2`, but `χ⃗=2`;
- two disjoint digon `3`-stars with balanced single-arc cycle covers give many
  examples with `U(D)` 3-connected, `MC=0`, repo-`λ=2`, disconnected `F_D`; all
  are again `χ⃗=2`.

So the correct Step-1b target is not a bare separator lemma. It is the colouring
lemma:

> **Step 1b′.** If `U(D)` is 3-connected, repo-`λ(D)≤2`, and `F_D` is disconnected,
> then some proper 2-colouring of `F_D` leaves the single-arc subdigraph acyclic;
> equivalently `D` is 2-dicolourable.

This would contradict `χ⃗(D)=3` and force `F_D` connected for 2-extremal `D`.
The near-miss script `scripts/step1b_fd_connectivity.py` prints explicit witnesses
for the 2-dicolourings and shows exactly why the naive separator route fails.

Equivalently, choose one bipartition `b_i` of each component `T_i` of `F_D`.
Every proper forest-colouring is obtained by independent component flips
`x_i`, with colour `c(v)=b_i(v)⊕x_i`. A single-arc dicycle is monochromatic
exactly when its arcs impose a consistent system of equations on the flips and
that system is satisfied. Step 1b′ is therefore a finite "bad dicycle equations
do not cover the whole flip cube" statement under the 3-connected/repo-`λ≤2`
hypotheses. The near-misses all have an uncovered flip assignment; a 2-extremal
counterexample would require the single dicycles to cover every assignment.

`scripts/fd_flip_cube.py` makes this audit explicit:

- `T5`: `F_D=∅`, `U=K5`, `MC=0`, repo-`λ=2`, but the bad sets cover only
  `22/32` flip assignments; `χ⃗=2`.
- two disjoint digon `3`-stars plus balanced single cycle-covers: **72** near
  misses with `U` 3-connected, `MC=0`, repo-`λ=2`, disconnected `F_D`; in all
  **72/72**, the bad sets fail to cover the cube (uncovered-count histogram
  `{2:72}`), so `χ⃗=2`.
- larger two disjoint digon `4`-stars: **8988** balanced single cycle-cover
  layouts. Here **420** layouts do cover the flip cube, but **0** satisfy
  `U` 3-connected + repo-`λ≤2` + `MC=0`: the covered layouts are either
  disconnected (`36`) or have a cutvertex and mixed cuts (`384`).
- truth set `L₃..L₇` excluding symmetric odd cycles: every genuine 2-extremal
  member has bad sets covering the cube. The **29** members with disconnected
  `F_D` are all covered and all have `U` not 3-connected.

So the remaining proof obligation is very sharp: prove that a disconnected
`F_D` can cover the whole flip cube only by creating a vertex 2-cut (as in the
truth-set examples), while 3-connected disconnected-`F_D` layouts always leave
at least one flip assignment uncovered.

**Step-1b next move (flip-cover cuts, 2026-06-03).** The follow-up audit
`scripts/fd_cover_cuts.py` isolates the first genuine obstruction.

For `k=2` components of `F_D` there is an exact dichotomy. A bad single dicycle
which lives in one component and uses one side of that component's bipartition is
monochromatic for **every** flip assignment. Otherwise every bad cross dicycle
imposes one parity equation `x_0 xor x_1 = δ`; hence full cover of the four-point
cube requires cross dicycles of **both** parities `δ=0,1`.

The audit results are:

- truth set `L_3..L_7`, non-SOC, `k=2`: **25/25** covered examples are exactly the
  `opposite-cross` mode, with no internal obstruction; all have `κ(U)=2`.
  The three `MC=0` cases still have non-edge vertex 2-cuts.
- truth set `L_3..L_7`, non-SOC, `k=3`: **4/4** covered examples have `κ(U)=2`,
  `MC=1`, and a minimum cover by three single dicycles (two size-2 bad constraints
  plus one size-3 constraint).
- two digon `3`-stars: **72/72** 3-connected near-misses have only one cross
  parity, so the cube is not covered and `χ⃗=2`.
- two digon `4`-stars: the **420** covered layouts are all internal-obstruction
  examples, and none is even 2-connected (`κ(U)=0` or `1`).

Thus the current proof target is not "find a separator from disconnected `F_D`".
It is the sharper **no-full-cover lemma**:

> If `U(D)` is 3-connected, repo-`λ(D)≤2`, and `F_D` is disconnected, then the bad
> single-dicycle partial assignments do not cover the component-flip cube.

For `k=2`, this reduces further to excluding the two cover modes above under the
3-connected/`λ≤2` hypotheses. The `opposite-cross` mode is the most promising
case: in every actual 2-extremal example it visibly produces a vertex 2-cut, while
the 3-connected near-misses fail precisely because only one parity equation is
present.

**Proof-status caveat.** See `docs/no_full_cover_lemma.md`. The no-full-cover
lemma is not presently proved. Under the standing side hypotheses, a full-cover
counterexample is already a 3-connected 2-extremal digraph with disconnected
`F_D`; hence proving the lemma is exactly the Step-1b crux, not a smaller
ingredient. The remaining non-circular target is a Menger/arc-connectivity lift:
show that the `internal` or `opposite-cross` full-cover modes force either a
vertex 2-cut in `U(D)` or repo-`λ(D)>=3`. Try 2 sharpened this further: mere
presence of both cross-arc parities is false as a discriminator; the needed
condition is both **constraint** parities, realised by actual same-parity
single dicycles.

### Steps 2–4 — now PROVED via the conditional structural lemma (2026-06-07)

Given **Step 1** (`F_D = T` a spanning tree), Steps 2, 3, 4 are **proved**. Write
`H` = single-arc edges (undirected); `H` has even degrees (singles balanced) and
`D` 3-connected ⇒ `U=T∪H` is 3-connected (min degree ≥3).

**Hypothesis (from T2): every fundamental tree-cut is crossed by exactly two
`H`-edges.** For a tree edge (digon) `xy`, the only tree edge whose removal
separates `x,y` is `xy` itself, so by (T2) the tight cut for the pair `(x,y)`
(`λ_D=2`, sum `=4`, even) crosses exactly one tree edge; it must be `xy`'s
fundamental cut (a cut crossing 2 tree edges has type `(2,0)`, a 2-edge-cut of `U`,
excluded by 3-edge-connectivity; `(0,4)` crosses 0 tree edges, can't separate
`x,y`). Type `(1,3)` ⇒ besides `xy` it crosses exactly **2** `H`-edges. ∎

> **Conditional structural lemma [PROVED].** Let `U = T ∪ H`, `T` a spanning tree,
> `U` 3-connected, `H` even-degree, every fundamental tree-cut crossed by exactly
> two `H`-edges. Then `H` is a single cycle whose vertex set is exactly the leaves
> of `T`, in a plane-realizable order.

*Proof.*
**(a) `d_H(v) ∈ {0,2}`; leaves have `d_H=2`.** Fix `v`; let `B_1,…,B_d`
(`d=deg_T(v)`) be the branches of `T−v`. By hypothesis each fundamental cut
`(B_i, ·)` is crossed by exactly 2 `H`-edges, so `B_i` has exactly 2 boundary
`H`-edges. Let `a_i` = how many go to `v`; then `d_H(v)=Σa_i`, and the number of
*inter-branch* `H`-edges is `(Σ(2−a_i))/2 = d − d_H(v)/2`. In `U−v` the branches
are joined only by inter-branch `H`-edges, and `U−v` is connected (3-connected), so
`d − d_H(v)/2 ≥ d−1`, giving `d_H(v) ≤ 2`; with `d_H(v)` even, `d_H(v) ∈ {0,2}`. A
leaf `ℓ` has `deg_T(ℓ)=1`, and min-degree ≥3 forces `d_H(ℓ)≥2`, so `=2`. Hence `H`
is a disjoint union of cycles, containing all leaves.

**(b) Exactly one cycle.** Each tree edge `e` is crossed by exactly 2 `H`-edges,
and a cycle crosses any cut an even number of times, so for each `e` exactly one
cycle `C_{j(e)}` crosses it (twice). Thus the Steiner trees `Steiner(V(C_i))` are
**edge-disjoint** (a shared edge would be crossed ≥4 times) and partition `E(T)`.
If there were ≥2 cycles, two such subtrees meet at a single tree-vertex `w`
(cutvertex of `T`). Each cycle is confined to its own subtree's side of `w`, so no
`H`-edge crosses between the two sides; deleting `w` disconnects `U` — contradicting
3-connectivity. So `H` is a single cycle `C`.

**(c) `V(C)` = leaves.** All leaves are on `C` (by (a)). Suppose an internal vertex
`u` (`deg_T(u)=d≥2`) is on `C`. Its 2 `H`-edges go to two *different* branches `B_1,
B_2` (both into one branch would confine `C` to `B_1∪{u}`, leaving a leaf-bearing
branch with no `H`-edges — impossible). Then in `U−u`, branch `B_1` keeps only its
*single* non-`u` boundary `H`-edge `pq` (`q∉B_1∪{u}`); deleting `{u,q}` disconnects
`B_1` from the rest — a 2-cut, contradicting 3-connectivity. So no internal vertex
is on `C`: `V(C) =` leaves of `T`.

**(d) Plane order.** The cyclic sequence of leaves along `C` traverses, via
consecutive tree-paths, each tree edge exactly twice (it crosses each fundamental
cut exactly twice). A cyclic order of all leaves whose consecutive tree-paths cover
every edge exactly twice is exactly a plane-embedding (Euler-tour) leaf order. ∎

**Step 4 even parity (for the 2-extremal `D`).** `D = ` digons `T` + directed cycle
`C` on the leaves. Any 2-dicolouring uses the unique proper 2-colouring `c` of `T`
(L0). Within a colour class the only arcs are single arcs of `C`. If the leaves
were split between the two classes, `c` would leave no monochromatic dicycle and be
a valid 2-dicolouring, forcing `χ⃗≤2` — contradicting `χ⃗=3`. So **all leaves lie in
one class of `T`**, i.e. every leaf-to-leaf tree path has even length — even leaf
parity. By the Assembly, `D` is a generalised wheel. ∎

*(Every link verified on the 3-connected examples `W₃..W₆`, `n=10`, `n=13`:
spanning-tree, 2-cross hypothesis, `d_H∈{0,2}`, one cycle, `V(C)=`leaves, generalised
wheel — all hold.)*

> **Consequence.** "3-connected 2-extremal `⇒` generalised wheel" is now **proved
> modulo Step 1 alone** (`F_D` is a spanning tree). Steps 2–4 are theorems.

## Current theorem inventory (authoritative claim labels)

> **Bankable theorems:** the unconditional lemmas **P1, L0, R1, T1 (cut identity),
> T2 (`λ'(U)≤4`; uniform `λ_D=2` + tight-cut for 3-connected)**, and the
> **two-component exclusion theorem**, plus the conditional structural theorem
> **"3-connected 2-extremal + connected `F_D` ⇒ generalised wheel."** The
> unconditional sub-theorem "3-connected 2-extremal ⇒ generalised wheel" is
> **NOT** yet proved because `F_D` might a priori have at least three components.

| status | item |
|---|---|
| **PROVED** | (P1) 3-connected ⇒ `MC=0` |
| **PROVED** | (L0) any 2-dicolouring properly 2-colours `F_D`; if `F_D` is a spanning tree the colouring is unique |
| **PROVED** | (Assembly) Steps 1–4 ⇒ generalised wheel (Def 9.1) — **the bankable conditional theorem** |
| **PROVED** | (R1) cross-endpoint cut lemma |
| **PROVED** | (R5 correction) "both *arc* parities" is necessary, not sufficient (K4 witness) |
| **PROVED** | (S1) singleton subcase reduces to "`U(D[V₀])` has a cutvertex"; (S2) chord structure |
| **PROVED** | (T1) cut identity `λ_D(u,v)=min_S(d_S+|E_U(S)|)/2` for Eulerian `D` |
| **PROVED** | (T2) `λ'(U)≤4`; and 3-connected 2-extremal ⇒ uniform `λ_D=2` + tight-cut `(d_S,|E_U|)∈{(0,4),(1,3)}` per pair |
| **PROVED (conditional on Step 1)** | **Steps 2,3,4** — the conditional structural lemma: given `F_D` a spanning tree, `H`(=singles) is one cycle on exactly the leaves, plane order, even parity ⇒ generalised wheel. So **"3-connected 2-extremal ⇒ generalised wheel" holds modulo Step 1 alone.** |
| **PROVED** | **Two-component exclusion:** a 3-connected 2-extremal digraph cannot have exactly two components in `F_D` |
| **PROVED** | **Three-component line-cover exclusion:** if `k(F_D)=3`, no bad dicycle can visit only two components |
| **PROVED** | **Pure-point arc-disjoint exclusion:** four full-support point cycles cannot be arc-disjoint under T2; two tree fans force repo-`λ≥3` |
| **VERIFIED, not proved** | the full sub-theorem at `n≤8` (via λ'≤4 lemma + forest search) + non-classical `n=10,n=13` |
| **PROVED (meta)** | Step 1 is equivalent to "no digon-free cut" within the target class; the all-cross-arcs-bichromatic equation system is only a sufficient colouring construction, not an equivalent formulation (R5 `K4`) |
| **OPEN — SOLE remaining obstruction** | Exclude the **overlapping pure four-point cover when `k(F_D)=3`**, and then `k(F_D)≥4`, in a 3-connected 2-extremal digraph. Once proved, the 3-connected sub-theorem is fully proved. |

Details and the R-series are in `docs/no_full_cover_lemma.md`.

## New tools from the disproof work (2026-06-06) — a cleaner foundation

The `n≤9` disproof produced two exact, proved facts that re-base the 3-connected
case on cleaner ground than the earlier flip-cube/shared-junction framing.

### (T1) Cut identity. **[PROVED]**

For an Eulerian digraph `D = F_D ⊔ S` (digons + single arcs), the single arcs are
balanced, so across **every** vertex cut `S₀`,
`arcs(S₀→S̄₀) = d_{S₀} + |E_single(S₀)|/2 = (d_{S₀} + |E_U(S₀)|)/2`, where
`d_{S₀}` = number of digons crossing. Hence by Menger, for every ordered pair,
`λ_D(u,v) = min_{S₀ sep u,v} (d_{S₀} + |E_U(S₀)|)/2`.

### (T2) `λ'(U) ≤ 4`, and uniform arc-connectivity. **[PROVED]**

From (T1), `λ_D(u,v) ≥ λ'_U(u,v)/2`, so `λ(D)=2 ⇒ λ'(U) ≤ 4` (max local
edge-connectivity; the disproof's workhorse lemma).

**Evenness.** `arcs(S₀→S̄₀) = (d_{S₀}+|E_U(S₀)|)/2` is an integer, so
`d_{S₀}+|E_U(S₀)|` is **even** (`|E_U(S₀)| ≡ d_{S₀} mod 2`) for every cut. This is
what turns the `3-edge-connected` bound `(d+|E_U|)/2 ≥ 3/2` into `λ_D ≥ 2`
(sum `≥3` and even `⇒ ≥4 ⇒ λ_D≥2`), and pins each tight cut's type. For a
**3-connected** 2-extremal `D`: `U` is 3-edge-connected, so `|E_U(S₀)| ≥ 3`, hence
`λ_D ≥ 2` for every pair; with `λ(D)=2` this forces

> **every ordered pair has `λ_D(u,v) = 2` (uniform), and a *tight* separating cut
> with `d_S + |E_U(S)| = 4`, i.e. `(d_S,|E_U|) ∈ {(0,4),(1,3)}`; and
> `λ'_U(u,v) ∈ {3,4}`.**

*(Verified: all 4 truth-set 3-connected members have uniform `λ_D=2`.)* This is a
much cleaner handle than the flip-cube cover: the digon-vs-edge split of every
tight cut is pinned to two cases.

### Verification extended

`scripts/n8_disproof` machinery (λ'≤4 lemma + forest-restricted search) verifies the
**full sub-theorem at `n=8`**: of 2388 3-connected graphs, 2036 are killed instantly
by `λ'≥5`; the rest searched — only `W₇` admits a 2-extremal orientation, and it is a
generalised wheel with connected `F_D`. **0 non-generalised-wheel, 0 disconnected-`F_D`.**
So the sub-theorem now holds for `n≤8` (was `n≤7`); `n=9` is inconclusive by search
(too slow on the `λ'≤4` 3-connected graphs).

## Crux — now a single obstruction

With Steps 2–4 and the two-component exclusion proved, the **sole** remaining gap is

> **Rule out `k(F_D)≥3`** for a 3-connected 2-extremal `D`.

Everything else in "3-connected 2-extremal ⇒ generalised wheel" is now a theorem.
The earlier separator-only phrasing is false outside the full 2-extremal package,
and the all-cross-arcs-bichromatic equations are not a complete colouring test.
The remaining case has at least three independent forest flips; it is a genuine
hypercube-cover problem rather than the two-parity R6/R7 configuration.

## Reproduce

Sub-theorem verification (n≤8): `scripts/verify_3connected_subtheorem.py --n 8`.
Conditional-lemma chain on the examples (`W₃..W₆`, `n=10`, `n=13`): the session
verification (reuses `planarity_search`, `h2_oracle`, `seam_invariant`,
`two_hajos_tree_join`).

Near-misses for Step 1b and the corrected colouring target:

```bash
python3 problems/two_extremal_digraphs/scripts/step1b_fd_connectivity.py
```

Flip-cube audit for the bad single-dicycle equations:

```bash
python3 problems/two_extremal_digraphs/scripts/fd_flip_cube.py
```
