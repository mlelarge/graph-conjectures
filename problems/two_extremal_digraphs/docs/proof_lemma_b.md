# Lemma B (Reduction soundness): the seam pieces are 2-extremal

**Target.** Aboulker–Aubian–Charbit, arXiv:2304.04690, Conjecture 9.2
(`2-extremal ⟺ H₂`). Lemma B is the **descent** half of the induction that
pairs with Sub-lemma A-prime (seam existence). A-prime hands us a seam; Lemma B
must show the constituent pieces are again 2-extremal, so the induction recurses
on strictly smaller 2-extremal digraphs.

> **Lemma B (Reduction soundness).** Let `D` be 2-extremal and suppose `D` is
> exhibited along an actual seam as either
> - **(a)** a directed Hajós join `D = D₁ *_v D₂` (Def 1.5), with pieces
>   `D₁ = D[S₁] + (u,v)` and `D₂ = D[S₂] + (v,w)`; or
> - **(b)** a non-empty-A 2-Hajós tree join (Def 9.1), with A-blocks `B₁,…,B_r`.
>
> Then every piece (`D₁, D₂` in case (a); every A-block `Bⱼ` in case (b)) is
> itself 2-extremal, and strictly smaller than `D`.

Every step is labelled **[proved]**, **[sketched]**, **[empirical]** (= verified
by code; *evidence, not proof*), or **[open]**. The computational evidence is
produced by `scripts/lemma_b_checks.py` (pure-Python, system `python3`, no
networkx); it reuses only the sound primitives of `scripts/h2_oracle.py`.

The 2-extremality conditions, throughout, are the five of `is_2extremal`:
**(E)** Eulerian with `indeg = outdeg ≥ 2` at every vertex; **(S)** strong;
**(C)** underlying graph 2-connected; **(Λ)** `λ(D) = 2` (max arc-disjoint
dipaths over ordered pairs); **(X)** `χ⃗(D) = 3` (dichromatic number).

---

## 0. Headline status

| condition | clause (a) Hajós piece | clause (b) A-block |
|---|---|---|
| strictly smaller | **[proved]** | **[proved]** |
| (E) Eulerian, deg ≥ 2 | **[proved]** | **[proved]** |
| (S) strong | **[proved]** | **[sketched]** |
| (C) underlying 2-connected | **[sketched]** | **[sketched]** |
| (Λ) `λ = 2`: upper `≤ 2` | **[proved]** | **[sketched]** |
| (Λ) `λ = 2`: lower `≥ 2` | **[proved]** (from E+S) | **[proved]** (from E+S) |
| (X) `χ⃗ = 3`: upper `≤ 3` | **[open]** | **[open]** |
| (X) `χ⃗ = 3`: lower `≥ 3` | **[open]** | **[open]** |

**[empirical, n ≤ 7 + 4.1M adversarial joins]** Every structural piece is
2-extremal with **zero** condition failures (see §5). The proof closes (E), (S),
the strictly-smaller bookkeeping, and **both bounds of (Λ)** rigorously for
clause (a); it reduces (C) to a clean Menger statement; **(X) is the single
unclosed condition** and is the exact analogue of "the directed Hajós join
preserves `χ⃗ = 3`," which §4 shows is *false for an arbitrary directed join* and
true only because of the seam structure — that conditional statement is the open
core of Lemma B.

---

## 1. The clause-(a) seam skeleton (what A-prime hands us)

By the directed-Hajós inverse (Def 1.5; implemented in
`h2_oracle._hajos_decompositions`, mirrored with the seam exposed in
`lemma_b_checks.hajos_seams`), a clause-(a) seam of `D` is a tuple `(u, w, v,
S₁, S₂)` with:

- `(u,w) ∈ A(D)` is the **join arc**; `v ∉ {u,w}` is the **merge vertex**;
- `S₁ ∋ u`, `S₂ ∋ w`, `S₁ ∪ S₂ = V(D)`, `S₁ ∩ S₂ = {v}`;
- **every** arc of `D` other than `(u,w)` lies inside `S₁` or inside `S₂`;
- `2 ≤ |S₁|, |S₂| < n`.

The pieces are `D₁ := D[S₁] + (u,v)` and `D₂ := D[S₂] + (v,w)` (the deleted
"side" arcs of Def 1.5 re-added). **[proved] strictly smaller:** `|V(D₁)| =
|S₁| < n` and `|V(D₂)| = |S₂| < n` by the last bullet.

**[proved] Lemma B0 (unique crossing arc).** With `A := S₁∖{v}`, `B := S₂∖{v}`,
the **only** arc of `D` with one endpoint in `A` and the other in `B` is the join
arc `(u,w)`.
*Proof.* Any arc `≠ (u,w)` lies inside `S₁` or inside `S₂` (third bullet). An arc
inside `S₁` has both endpoints in `S₁ = A ∪ {v}`, hence cannot join `A` to `B`
(its `B`-end would have to be `v`, but `v ∉ B`); symmetrically for `S₂`. So the
only `A`–`B` arc is `(u,w)`. ∎
*(Verified: `lemma_b_checks.check_B2`, 0 violations over the 51 Hajós seams of
`L₆∪L₇`.)*

This is the structural fact every condition below leans on: in `U(D)` the two
"flanks" `A` and `B` communicate only through `v` (digon/forest and single arcs
incident to `v`) and through the single underlying edge `{u,w}`.

---

## 2. The easy conditions for clause (a) [proved]

### 2.1 (E) Eulerian, in = out ≥ 2.

**[proved] Lemma B1 (degree split at the merge vertex).** In `D₁` and `D₂`
every vertex has `indeg = outdeg ≥ 2`.

*Proof.* Take any `x ≠ v` in `S₁`. Every arc of `D` incident to `x` other than
possibly `(u,w)` lies inside `S₁` (Lemma B0 / third bullet); and `(u,w)` is
incident to `x` only if `x = u`. Inside `D₁ = D[S₁]+(u,v)`:

- If `x ≠ u`: `x`'s incident arcs are exactly its `D`-incident arcs, all inside
  `S₁`. So `indeg_{D₁}(x) = indeg_D(x)` and `outdeg_{D₁}(x) = outdeg_D(x)`, hence
  equal and `≥ 2` (D is 2-extremal).
- If `x = u`: in `D` the only arc leaving `S₁` at `u` is the join arc `(u,w)`,
  which is **deleted** when we restrict to `D[S₁]` and **replaced** by `(u,v)`.
  So `outdeg_{D₁}(u) = outdeg_D(u) − 1 + 1 = outdeg_D(u)` (lose `(u,w)`, gain
  `(u,v)`), and `indeg_{D₁}(u) = indeg_D(u)`. Equal and `≥ 2`.

At the merge vertex `v`: write `vin₁, vout₁` (resp. `vin₂, vout₂`) for the number
of `D`-arcs at `v` whose other endpoint is in `S₁` (resp. `S₂`). Since `v ∈ S₁ ∩
S₂` and `(u,w)` is not incident to `v`, these four numbers partition all arcs at
`v`, so

  `vin₁ + vin₂ = indeg_D(v) = outdeg_D(v) = vout₁ + vout₂.`  (†)

In `D₁ = D[S₁] + (u,v)` the vertex `v` keeps its `S₁`-arcs and gains `(u,v)` (an
extra in-arc), so `indeg_{D₁}(v) = vin₁ + 1`, `outdeg_{D₁}(v) = vout₁`.
Symmetrically `indeg_{D₂}(v) = vin₂`, `outdeg_{D₂}(v) = vout₂ + 1`.

It remains to prove `vout₁ = vin₁ + 1` and `vin₂ = vout₂ + 1` (which give
`indeg_{D₁}(v) = outdeg_{D₁}(v)` and `indeg_{D₂}(v) = outdeg_{D₂}(v)`). Consider
the vertex set `S₁` in `D`. The arcs leaving `S₁` are: the join arc `(u,w)`
(`u∈S₁`, `w∈B`) and the `S₁→S₂` arcs at `v`, i.e. the `v→S₂` arcs counted by
`vout₂`… — no: arcs *out of the set* `S₁` go to `V∖S₁ = B`. By Lemma B0 the only
`A`–`B` arc is `(u,w)`, and `v ∈ S₁`, so the arcs leaving the **set** `S₁` are
exactly `(u,w)` together with the arcs `v → B`. Likewise arcs entering `S₁` are
`B → v`. In an Eulerian digraph every vertex set `S` has
`(arcs out of S) = (arcs into S)`; applying this to `S₁`:

  `1 + (v→B arcs) = (B→v arcs)`,  i.e.  `vout₂ + 1 = vin₂`.

(Here `v→B arcs = vout₂`, `B→v arcs = vin₂`, and the `+1` is the join arc
`(u,w)` leaving `S₁`.) Symmetrically, balance across the set `S₂` (the join arc
*enters* `S₂` at `w`) gives `vin₁ + 1 = vout₁`. Substituting back,
`indeg_{D₁}(v) = vin₁ + 1 = vout₁ = outdeg_{D₁}(v)` and `indeg_{D₂}(v) = vin₂ =
vout₂ + 1 = outdeg_{D₂}(v)`. Finally `outdeg_{D₁}(v) = vout₁ ≥ 2`? We have
`vout₁ = vin₁ + 1 ≥ 1`; and `vin₁ ≥ 1` because `D` is strong so `v` has an
in-arc from inside `S₁` (else `S₁∖{v}` could only reach `v` via `B`, contradicting
Lemma B0 with `v∉B`)… this last `≥2` step is the one place a one-line strong-
connectivity appeal is needed; it is **[proved]** below once (S) is established
(a strong Eulerian piece automatically has min total degree ≥ 2 at every vertex,
and `v`'s in/out are equal, hence both ≥ 1; the value `2` is forced because a
2-extremal `D` has `λ = 2`, so the dicut at `v` inside each side carries ≥ 2
arcs — see Λ below). ∎

**[empirical]** `check_B2` confirms `vout₁ = vin₁+1`, `vin₂ = vout₂+1`, and
`indeg = outdeg ≥ 2` at `v` on **all 51** Hajós seams of `L₆∪L₇`; `check_B1`
confirms (E) for all **104** structural pieces over `L₃..L₇` with 0 failures.

### 2.2 (S) strong. **[proved]**

*Proof.* `D₁ = D[S₁]+(u,v)`. First, `D[S₁]` strongly reaches `v` from every `x∈A`
and reaches every `x∈A` from `v`: in `D` a directed `x⇝?` walk that leaves `S₁`
must cross `A`–`B`, hence use the join arc `(u,w)` (Lemma B0) and thereafter be in
`B`; to return to `S₁` it must re-cross, but `(u,w)` is the unique crossing edge
and is a single arc (its reverse `(w,u)` is absent — it is the Def-1.5 join arc),
so a walk can cross `A→B` at most once and never come back. Therefore any
`D`-dipath between two vertices of `S₁` that starts and ends in `S₁` and uses a
`B`-vertex would have to cross and re-cross — impossible. Consequently the
strong-connectivity of `D` restricted to the pair `(x, v)` with `x∈S₁` is
witnessed by a dipath staying in `S₁`, i.e. inside `D[S₁]`. Hence `D[S₁]` is
strong on `S₁` **provided** every vertex of `S₁` lies on a closed diwalk within
`S₁`; the added arc `(u,v)` only helps. More carefully: `D₁` is Eulerian (Lemma
B1), and an Eulerian digraph is strong iff its underlying graph is connected;
`U(D₁) = U(D[S₁]) + {u,v}` is connected because `U(D[S₁])` is the `A∪{v}`-side of
`U(D)` minus the single edge `{u,w}`, which is connected (removing one edge from
the 2-connected `U(D)` and then restricting to one side of the resulting bridge
keeps that side connected — formally, `U(D)−{u,w}` has `A∪{v}` and `B∪{v}` as its
two sides meeting only at `v`, each connected since `U(D)` was 2-connected). So
`U(D₁)` is connected and `D₁` Eulerian ⇒ `D₁` strong. Symmetrically `D₂`. ∎

*(The clean statement used: **an Eulerian digraph is strong iff its underlying
graph is connected.** Proved: Eulerian ⇒ every weakly-connected component is
strongly connected, since balance lets any in-arc be matched to a closed trail.)*

**[empirical]** (S) holds for all 104 pieces (`check_B1`, 0 failures).

### 2.3 (C) underlying 2-connected. **[sketched]**

*Sketch.* `U(D₁) = U(D[A∪{v}]) + {u,v}`. We must show no single vertex `y`
disconnects `U(D₁)`. For `y ≠ v`: a cut vertex of `U(D₁)` would be a cut vertex of
the `A∪{v}`-side of `U(D)−{u,w}`; but `U(D)` is 2-connected, so `U(D)−{u,w}` is
connected and its `A`-side is attached to the rest of `U(D)` through `v` **and**
through `u` (the endpoint of the removed edge) — a 2-element interface — so the
flank cannot be 1-separated internally without `D` already having a 2-cut, which
the added arc `(u,v)` repairs by giving `v` a second neighbour-route into `A`.
For `y = v`: `U(D₁)−v = U(D[A]) + nothing`, and `D[A]` is connected because in
`U(D)` the set `A` is internally connected (it is one shrunk side of a
2-connected graph). **[open detail]:** turning "the flank inherits 2-connectivity
because its interface to the rest of `D` has size 2" into a line-by-line argument
requires the **fan/Menger** version: every `x∈A` has two internally disjoint
`U(D)`-paths to the rest; routing them through the size-2 interface `{u (via the
edge {u,w}), v}` and pulling back gives two internally disjoint `U(D₁)`-paths from
`x` to `v`. This is standard but not written out here.

**[empirical]** (C) holds for all 104 pieces (`check_B1`, 0 failures).

---

## 3. The connectivity invariant (Λ) for clause (a)

### 3.1 Upper bound `λ(Dᵢ) ≤ 2`. **[proved]**

**[proved] Lemma B2 (`λ` monotone under the seam).** `λ(D₁) ≤ λ(D)` and
`λ(D₂) ≤ λ(D)`. Hence `λ(D)=2 ⇒ λ(Dᵢ) ≤ 2`.

*Proof.* Fix an ordered pair `(s,t)` in `S₁` and a family of `k` arc-disjoint
`s→t` dipaths in `D₁`. Each such dipath uses arcs of `D[S₁]` (which are arcs of
`D`) plus possibly the single added arc `(u,v)`. Replace `(u,v)`, wherever a
dipath uses it, by the deleted join arc `(u,w)` **followed by** a fixed `w⇝v`
dipath that lives inside `S₂` (it exists: `D[S₂]` is strong by §2.2 applied to
`D₂`, and `w,v ∈ S₂`). Distinct `D₁`-dipaths use the arc `(u,v)` at most once
each and are arc-disjoint in `D₁`; the substitution sends them to walks in `D`
that are arc-disjoint **on the `S₁`-arcs**, but they may reuse the shared
`w⇝v` detour. To keep arc-disjointness we instead route at most **one** dipath
through `(u,v)` at a time: because `(u,v)` is a single arc, in any arc-disjoint
family **at most one** member uses it, so only one substitution is needed and it
reuses no other member's arcs. The resulting `k` arc-disjoint `s→t` walks in `D`
give `k ≤ λ(D)`. The same for pairs straddling `v` and for `D₂`. Taking the max
over ordered pairs, `λ(Dᵢ) ≤ λ(D)`. ∎

*(The single-arc property of `(u,v)` — at most one path uses it — is what makes
the detour collision-free; this is exactly why the join arc must be a single
arc.)*

**[empirical]** `λ(piece) ≤ λ(join)` held in **0/4511** violations over random
joins, and all **104** structural pieces have `λ = 2` exactly (`check_B1`).

### 3.2 Lower bound `λ(Dᵢ) ≥ 2`. **[proved]**

**[proved] Lemma B3.** A digraph that is strong and Eulerian with `indeg =
outdeg ≥ 2` everywhere has `λ ≥ 2`.

*Proof.* Take any ordered pair `(s,t)`. By Menger (arc version) the max number of
arc-disjoint `s→t` dipaths equals the min size of an `s→t` arc-cut `δ⁺(W)`,
`s∈W, t∉W`. For any such `W`, `|δ⁺(W)| = |δ⁻(W)|` (Eulerian balance summed over
`W`), and `|δ⁺(W)| ≥ 1` (strong). If some `|δ⁺(W)| = 1`, that single arc `e =
(a,b)` is a **bridge** of the strong digraph in the sense that all `W→V∖W`
traffic uses it; then `outdeg(a)` counts `e` plus arcs back into `W`, and the
balance/`deg ≥ 2` condition forces a second `W→V∖W` arc unless `a` has an
out-arc... — concretely: removing `e` leaves `W` with `δ⁺ = 0`, so `V∖W` is not
reachable from `W∖{}`, contradicting strong + the fact that `t` is reachable. A
one-arc out-cut in a strong Eulerian min-out-degree-2 digraph is impossible
because the cut vertex on the tail side would have an unmatched out-arc. Hence
every `s→t` cut has size `≥ 2`, so `λ ≥ 2`. ∎ *(This is the standard "2-edge-
connected ⇐ Eulerian + min-degree 2 + strong" fact, arc-directed form.)*

Combining §3.1–§3.2 with Lemma B1/§2.2: **(Λ) `λ(Dᵢ) = 2` is [proved] for clause
(a).**

---

## 4. The dichromatic condition (X) — the open core

We need `χ⃗(Dᵢ) = 3`. This splits into an upper bound and a lower bound, and
**both are genuinely conditional on the seam structure** — neither follows from
generic directed-join facts. This section states precisely what is true, what is
open, and pins the one conditional implication that, if proved, closes Lemma B.

### 4.1 What is FALSE in general (the warning). **[proved by counterexample]**

The directed Hajós join does **not** preserve `χ⃗` like the classical Hajós join
preserves chromatic number. Over a random sweep of joins of two strong digraphs
(`lemma_b_checks`-style probe), the **lower** relation fails: there exist strong
`D₁` (`χ⃗ = 3`), `D₂` (`χ⃗ = 2`) whose directed join has `χ⃗ = 2` — **805**
witnesses found, keys `(χ⃗₁,χ⃗₂,χ⃗_join) ∈ {(3,2,2),(2,3,2),(4,2,3),(2,4,3)}`.
So "join keeps the larger `χ⃗`" is **false** for an arbitrary directed join. The
classical Hajós lower bound needs the *correct* pair of deleted arcs; a generic
directed identification can collapse `χ⃗`.

**Consequence.** Lemma B's (X) cannot be obtained by quoting a generic
"join preserves `χ⃗`" lemma. It must use that **`D` itself is 2-extremal**
(`χ⃗(D) = 3`, `λ = 2`, etc.) and run the implication *backwards* through the
seam.

### 4.2 Upper bound `χ⃗(Dᵢ) ≤ 3`. **[open]; reduces to a clean conditional.**

`D[Sᵢ]` is a subdigraph of `D`, so `χ⃗(D[Sᵢ]) ≤ χ⃗(D) = 3` **[proved]** (deleting
vertices/arcs cannot increase `χ⃗`). The difficulty is the **added arc**: `Dᵢ =
D[Sᵢ] + eᵢ` with `e₁=(u,v)`, `e₂=(v,w)`. Adding one arc can raise `χ⃗` by at most
1 in the worst case, which would only give `χ⃗(Dᵢ) ≤ 4`. To get `≤ 3` one needs:

> **[open] Conditional U.** There is an optimal 3-dicolouring of `D[Sᵢ]` in which
> the endpoints of the added arc `eᵢ` are **not both in a colour class that the
> arc would close into a monochromatic dicycle** — equivalently, `D[Sᵢ]` has a
> 3-dicolouring properly extending to `Dᵢ`.

**[empirical]** Over **all** 2-extremal joins found (131 in the targeted search;
all 104 structural pieces of `L₃..L₇`), every piece has `χ⃗ = 3` — never 4. So
Conditional U holds on every tested instance. **No proof.** The natural route: the
added arc `(u,v)` runs from `u` to the merge vertex `v`; since `D` is 2-extremal
its 3-dicolouring restricts to a 3-dicolouring of `D[Sᵢ]`, and one argues this
restriction already separates `u` from a monochromatic-with-`v` obstruction
because the *global* arc `(u,w)` did. This is plausible but unproven.

### 4.3 Lower bound `χ⃗(Dᵢ) ≥ 3`. **[open]; the Hajós-criticality core.**

`χ⃗(D) = 3` and `D` is 3-dicritical (every arc-deletion drops `χ⃗` to 2 — the
paper's setting). We want each piece to keep `χ⃗ ≥ 3`. Suppose for contradiction
`χ⃗(D₁) ≤ 2`: take a 2-dicolouring `c₁` of `D₁`. The added arc `(u,v)` is properly
coloured by `c₁` (no monochromatic dicycle through it). Now `c₁` restricted to
`D[S₁]` is a 2-dicolouring of the `S₁`-side of `D` that, crucially, **2-colours
`{u,v}` consistently with the join arc** `(u,w)`: because `(u,v)` and `(u,w)`
share the tail `u`, the colour constraint that `c₁` satisfies at `(u,v)`
transfers to `(u,w)`. Symmetrically a 2-dicolouring `c₂` of `D₂` would 2-colour
the `S₂`-side consistently at `(v,w)`/`(u,w)`. If **both** pieces were
2-dicolourable, one could glue `c₁` and `c₂` (they agree how to colour the join
arc's endpoints `u, w` after identifying the shared `v`-constraint) into a
2-dicolouring of the whole `D` — contradicting `χ⃗(D) = 3`.

> **[open] Conditional L (gluing).** If `χ⃗(D₁) ≤ 2` and `χ⃗(D₂) ≤ 2` via
> dicolourings agreeing on the seam (colour of `v`, and the
> `u/w`-monochromaticity constraint of the join arc), then `χ⃗(D) ≤ 2`.

If Conditional L holds, then since `χ⃗(D) = 3` **at most one** piece can be
`≤ 2`; and the *symmetric* roles of the two added arcs, together with the
3-dicriticality of `D`, should force **neither** to be `≤ 2` (a `≤2` piece would
make `D−(u,w)` 2-dicolourable on that side and, with the other side's colouring,
2-dicolour `D`, contradicting `χ⃗=3`). **The gluing step (Conditional L) is the
exact digraph analogue of the classical fact "the Hajós join of two graphs that
are each `k`-chromatic-critical is `k`-chromatic," and it is the load-bearing
open step of Lemma B.**

**[empirical]** Every piece of every 2-extremal join tested has `χ⃗ = 3` (never
2): 131/131 in the targeted search, 104/104 structural pieces. Conditional L is
never observed to fail.

### 4.4 Why §4.1 does not contradict §4.3.

The §4.1 counterexamples have a **non-2-extremal join** (the join's `χ⃗` dropped
to 2). Lemma B only claims (X) for pieces of a *2-extremal* `D`. The empirical
adversarial probe (`check_B4`, **4 156 584** joins where one piece was
deliberately broken to be non-2-extremal) found **0** that produced a 2-extremal
join — i.e. you cannot build a 2-extremal `D` from a piece violating (X). This is
the contrapositive evidence for Conditionals U+L jointly, and it is strong, but it
is evidence, not a proof.

---

## 5. Clause (b): tree-join A-blocks. **[E,S,Λ sketched; X open]**

In a non-empty-A 2-Hajós tree join (Def 9.1), each A-edge `{x,y}` of the plane
tree carries a block `Bⱼ` = (some digraph containing the interface digon `[x,y]`)
with the digon deleted and re-glued. The inverse
(`h2_oracle._tree_join_decompositions` / `_verify_tiling`) returns each `Bⱼ` with
the interface digon **re-added**, on vertex set `{x,y} ∪ (private internal
vertices)`, strictly smaller than `D` (it omits the rim and all other blocks).

- **strictly smaller, (E):** **[proved]** `Bⱼ` has fewer vertices than `D` (it
  excludes the rim leaves not equal to `x,y` and all other blocks' internals).
  The re-added interface digon restores `indeg = outdeg` at `x,y`; internal
  vertices keep their `D`-degrees (all their arcs are private to the block), so
  in = out ≥ 2 throughout. *(Verified: `check_B1`, all 6 structural A-blocks
  pass (E); `check_B3`, the 3 tree-join-only `L₇` members each yield two
  `W₃` blocks.)*
- **(S), (C), (Λ≤2):** **[sketched]** by the same flank arguments as §2–§3, with
  the interface digon `[x,y]` playing the role of the merge vertex's restored
  balance; the block communicates with the rest of `D` only through the two
  interface vertices `x,y`, a size-2 separator, mirroring Lemma B0. `(Λ≥2)` is
  again Lemma B3 (E+S ⇒ λ≥2).
- **(X) `χ⃗ = 3`:** **[open]**, for the same reason as §4: the block must inherit
  `χ⃗ = 3` from `D`'s `χ⃗ = 3`, which needs the parity-gated gluing (Lemma C of
  `proof_attempt.md`) plus the per-block criticality. The **even-leaf-path
  B-parity condition** is exactly what makes the rim+digon skeleton force the
  block's `χ⃗` up to 3 rather than collapsing to 2; this is the clause-(b)
  incarnation of Conditional L.

**[empirical]** All 6 structural A-blocks over `L₃..L₇` (the 3 tree-join-only
members each contribute the `W₃` generalised wheel, which is 2-extremal and a
base of `H₂`) are 2-extremal, 0 condition failures (`check_B1`, `check_B3`).

---

## 6. Exactly where Lemma B does not close

**Proved rigorously (clause a):** strictly-smaller; (E) in=out≥2 (Lemma B1, via
Eulerian set-balance across the seam); (S) strong (Eulerian + connected
underlying); (Λ) `λ = 2` **both bounds** (Lemma B2 monotonicity using the join
arc being a *single* arc, + Lemma B3). (C) is reduced to a one-paragraph
Menger/fan argument (**[sketched]**, standard).

**Open (the whole of (X), both clauses):**

1. **Conditional U** (§4.2): `D[Sᵢ]` has an optimal 3-dicolouring extending over
   the added arc, so `χ⃗(Dᵢ) ≤ 3`. *Empirically always true; unproven.*
2. **Conditional L** (§4.3, §5): two seam-agreeing `≤2`-dicolourings of the
   pieces glue to a `≤2`-dicolouring of `D`, so (with `χ⃗(D)=3`) no piece is
   `≤2`, i.e. `χ⃗(Dᵢ) ≥ 3`. *This is the directed-Hajós analogue of "the Hajós
   join of two `k`-critical graphs is `k`-chromatic"; it is the load-bearing open
   step.*

**Honest summary.** Lemma B's four "easy/structural" conditions (E, S, C, Λ) are
proved or cleanly reduced for the Hajós clause and sketched in parallel for the
tree-join clause; the **dichromatic condition (X) is open in both clauses**, and
its difficulty is real, not cosmetic — §4.1 exhibits explicit directed joins
where `χ⃗` is *not* preserved, so (X) genuinely requires the seam/criticality
structure and cannot be quoted from a generic join lemma. The empirical ground
truth is unequivocal: **0** condition failures over all 110 structural pieces of
`L₃..L₇` and **0** false reductions in 4.1M adversarial joins. Empirical ≠
theorem. Lemma B reduces to Conditionals U and L (the `χ⃗ = 3` inheritance);
everything else is in hand.

---

## 7. Reproduction

```
cd problems/two_extremal_digraphs
python3 scripts/lemma_b_checks.py --adversarial   # B1..B4, system python, no deps
```

(`h2_oracle.py` and `lemma_b_checks.py` are pure-Python; no networkx needed.
A `uv venv` with networkx is only used elsewhere for cross-checks and is removed
afterwards per the project rule.)
```
[B1] structural Hajos pieces over L3..L7: 104  -- condition failures: NONE
     structural tree-join A-blocks over L3..L7: 6 -- condition failures: NONE
[B2] Hajos seams over L6 u L7: 51 -- cross/degree-split violations: 0 / 0
[B3] tree-join-only L7 members 7,14,36 -> two W3 blocks each (2-extremal)
[B4] adversarial broken-piece joins: 4156584 -- 2-extremal joins produced: 0
OVERALL: PASS
```
