# Sub-lemma A-prime via a minimal counterexample (Angle 1)

**Target.** Aboulker–Aubian–Charbit, arXiv:2304.04690, Conjecture 9.2, reduced to

> **Sub-lemma A-prime.** Every 2-extremal digraph `D` that is **not** a symmetric
> odd cycle and **not** a generalised wheel admits a Lemma-A seam: either
> **(a)** a directed-Hajós merge vertex, or **(b)** a general non-empty-A 2-Hajós
> tree-join seam.

**This document** assumes a smallest 2-extremal `D` that is non-base and **has no
Lemma-A seam**, and tries to derive a contradiction from the proved arc-decomposition
(P1–P3) plus the mixed-2-cut invariant. Every step is labelled
**[proved]** / **[sketched]** / **[conjectural]** / **[verified n≤7]**. I am explicit
at the end about the two places where it does **not** close.

All computational checks below ran under **system python, no dependencies**, against
`data/L_{3..7}.json` and `data/seam_search_L6_L7.json`, reusing the sound primitives
in `scripts/h2_oracle.py` and `scripts/seam_invariant.py`. Empirical agreement over
`n ≤ 7` is **evidence, never a proof.**

---

## 0. The standing primitives (inputs, all proved elsewhere)

- **[proved] P1 (Menger).** No 2-extremal digraph has a 2-arc-cut digon; `D` is strong
  with `U(D)` 2-connected. The literal "cut digon" seam is vacuous, so clause (b) is
  the *general* non-empty-A tree-join.
- **[proved] P2.** The digon graph `F_D` (vertices of `D`, edges = digons) is a forest.
- **[proved] P3.** The single arcs (reverse absent) are in/out balanced at every vertex,
  hence decompose into arc-disjoint closed directed trails. Each single arc contributes
  one undirected **single edge** to `U(D)`.
- **[proved] Necessity half of the invariant.** If `D` has a directed-Hajós merge
  vertex then `MC(D)=1` (a mixed 2-cut `(v,e)` exists), where a *mixed 2-cut* is a pair
  (vertex `v`, single edge `e={a,b}`, `a,b≠v`) such that `e` is a bridge of `U(D)−v`.
  Contrapositive **[proved]:** `MC(D)=0 ⇒ D has no Hajós merge vertex.`

---

## 1. Reductions that ARE forced on a minimal seamless counterexample

Let `D` be a **smallest** 2-extremal digraph (by `|V|`, ties by `|E|`) that is non-base
(not a symmetric odd cycle, not a generalised wheel) and has **no Lemma-A seam**.

### 1.1 `D` carries single arcs and a non-trivial digon forest. [proved]

`D` is not a symmetric odd cycle, so not every arc is a digon. By P3 the non-digon arcs
are balanced and non-empty, so `D` has `≥1` single edge. Each vertex has in = out `≥ 2`.

**[verified n≤7]** For every non-`SOC` member, `ndig ≤ n−1` and the single-arc set is a
non-empty balanced sub-digraph; for every non-base member it decomposes into directed
cycles of length `≥3` (`single-cycle-lens` table in the run log of §6). The symmetric
odd cycles are exactly the members with `ndig = n` and no single arc.

### 1.2 `D` has `MC(D)=0`. [conditionally proved — see the honest gap]

If `MC(D)=1` then, **conjecturally** (the sufficiency direction of the invariant,
`seam_invariant.md §3.2`), `D` has a genuine directed-Hajós merge vertex, contradicting
seamlessness. So a seamless minimal counterexample must have `MC(D)=0`.

**Status.** This step uses the **unproved** sufficiency direction `MC=1 ⇒ Hajós seam`.
What **is** proved (the necessity half, §0) only gives the *converse*: `MC=0 ⇒ no Hajós
seam`. So I can soundly assume the **weaker** consequence:

> **[proved] 1.2′.** A seamless minimal counterexample has **no Hajós merge vertex**;
> therefore, *if* A-prime is to hold for `D`, it must hold through clause (b). Hence the
> whole burden falls on: *exhibit a non-empty-A tree-join seam for `D`.* If additionally
> `MC(D)=1`, the only way to also kill clause (a) is the conjectural sufficiency; I do
> **not** assume it, and instead carry both `MC=0` and `MC=1` sub-cases. The `MC=1`
> sub-case is where this angle ultimately stalls (§4).

**[verified n≤7]** Among all non-base members of `L₃..L₇`, the ones with `MC(D)=0` are
**exactly** `7.7, 7.14, 7.36` — precisely the three tree-join-only members. So over
`n≤7` the seamless-candidate set under `MC=0` is non-empty and is *exactly* the
tree-join class. (Run log §6, block "NON-BASE, MC=0".)

### 1.3 `U(D)` is 2-connected but **not** 3-connected: a vertex 2-cut exists. [proved + verified]

`U(D)` is 2-connected (P1). **[verified n≤7, strong regularity]** Every non-base member
of `L₅..L₇` has a vertex 2-cut `{a,b}` (deleting both disconnects `U(D)`); **none** is
3-connected (run log §6, "non-base members whose U(D) is 3-connected: []"). Some
*generalised wheels* (5.1, 6.5, 7.25) **are** 3-connected, and some are not — so
"`U(D)` not 3-connected" is **necessary but not sufficient** for non-base.

> **[sketched] Claim 1.3.** A non-base 2-extremal `D` has a vertex 2-cut `{a,b}` in
> `U(D)`. *Idea:* if `U(D)` were 3-connected, the digon forest `F_D` (≤ `n−1` edges,
> P2) plus the single edges would have to realise a 3-connected graph in which the
> non-forest part is two-or-three balanced cycles; pushing the Eulerian/λ=2 constraints
> one shows the only 3-connected realisations are wheels/odd cycles (bases). *Not
> proved* — the wheel witnesses 5.1/6.5/7.25 show 3-connected DOES occur among bases, so
> the claim is genuinely "non-base ⇒ has a 2-cut", and I only have the data, not the
> argument. **This is the first place the angle leans on a conjecture.**

---

## 2. The leaf / minimal-trail attachment analysis (the structural core)

This is the part the brief asks for: focus on a **leaf of the digon forest** and a
**single closed trail of minimal length**, and show 2-extremality constrains the
attachment so tightly that a seam is forced.

### 2.1 Every digon-forest leaf is a "single-degree-1" vertex. [proved]

Let `ℓ` be a leaf of `F_D`: `deg_{F_D}(ℓ)=1`, joined by one digon to its parent `p`.
The digon contributes exactly `1` to `indeg_D(ℓ)` and `1` to `outdeg_D(ℓ)`. Since `D`
is Eulerian with `indeg = outdeg ≥ 2`, the single arcs at `ℓ` satisfy
`single-in(ℓ) = single-out(ℓ) = indeg_D(ℓ) − 1 ≥ 1`.

**[verified n≤7]** In **every** member of `L₃..L₇` (run log §6, "leaves with no single
arc: [] count 0") every forest leaf has `single-in = single-out ≥ 1`; and for the three
`MC=0` members **every** forest leaf has exactly `single-in = single-out = 1`, i.e.
total degree `2` in the single-arc digraph and total degree `4` in `D` is **not**
forced — these leaves have `D`-degree `2` (one digon + one single in + one single out).

> **[proved] Leaf attachment lemma.** A leaf `ℓ` of `F_D` with `single-in(ℓ)=
> single-out(ℓ)=1` has, besides its parent digon `{ℓ,p}`, exactly one single in-arc
> `x→ℓ` and one single out-arc `ℓ→y` (`x,y ≠ p` since `{ℓ,p}` is the only digon at
> `ℓ`, and `x,y ≠ ℓ`). Thus `ℓ` lies on exactly one single-arc closed trail, entering
> from `x` and leaving to `y`.

### 2.2 A minimal single trail is a short directed cycle threading the forest. [proved + verified]

Take a closed directed single-arc trail `C` of **minimum length**. By P3 it is a closed
walk; minimality + the leaf lemma make it a **simple directed cycle** `c_0 → c_1 → …
→ c_{k−1} → c_0` of length `k ≥ 3` (`k ≥ 3` because `U(D)` is simple: no `2`-cycle of
*single* arcs, as a `2`-cycle of single arcs `u→w→u` would be a digon, contradiction).

**[verified n≤7]** Every minimal single trail over `L₅..L₇` is a simple cycle of length
`3,4` or `5` (run log §6, `single-cycle-lens`). For `7.7/7.14/7.36` the single arcs are
two disjoint 3-cycles on the leaves.

### 2.3 The rim cycle of a tree-join is exactly such a minimal trail. [sketched]

In a tree-join presentation, the **peripheral directed cycle** runs over the leaves in
plane order; deleting it leaves the digon-forest + A-blocks. So *if* `D` is a tree-join,
a minimal single trail `C` is a candidate **rim**: its vertices are the tree leaves, and
`E(D) ∖ C` should reassemble as `F_D`-digons + A-blocks.

> **[sketched] Rim-recovery step.** For a non-base `D` with `MC(D)=0`: a minimal single
> trail `C` is the rim; the remaining single arcs sit **inside** the contracted forest
> components (they are self-loops of the contracted skeleton `M_D`), and exactly one
> contracted component carries a nontrivial A-block. *Evidence:* contracting `F_D` in
> `7.7/7.14/7.36` yields a 2-vertex skeleton whose only non-rim single arcs are
> **self-loops** internal to one component (run log §6, "contracted single arcs"
> `[(0,0),(0,1),(1,0),(1,1)]` etc.) — i.e. the non-rim single structure is localised to
> one forest component, which is the A-block. *Not proved in general:* that a minimal
> trail is *always* a valid rim (leaves-only, correct plane cyclic order, even B-parity)
> for a general `MC=0` non-base `D`.

### 2.4 The A-block interface is a non-adjacent vertex 2-cut, never a digon. [proved-for-the-three + sketched]

The reason `MC=0` ⇒ no Hajós merge (single-vertex seam) but a tree-join (2-vertex
interface) is needed is now concrete:

**[verified n≤7]** For `7.7/7.14/7.36` the vertex 2-cuts of `U(D)` are exactly
`{0,6}` and `{5,6}` (run log §6); **neither is a digon, neither is a single edge,
neither pair is even adjacent in `D`.** Each cut splits `U(D)` into a 3-vertex side and
a 2-vertex side `{2,4}` (resp. `{1,3}`). Closing the **small side** `{a,b}∪{2,4}` with
the interface digon `{a,b}` gives **exactly the generalised wheel `W₃`** (`is_2extremal
= True`, `_is_generalised_wheel = True`, `|block| = 4`); the **large side** closed the
same way is **not** 2-extremal on its own (run log §6, "+interface-digon 2-extremal").

> **[proved, for these three] A-edge mechanism.** The seam is genuinely a tree-join: the
> minimal nontrivial A-block (`W₃`) attaches through a **2-vertex interface** `{a,b}`
> (an A-edge), so no single identified vertex can separate it. This is the n=4 `W₃/W₄`
> phenomenon (`proof_attempt.md §5`) reappearing as a sub-block. The large side is not a
> clean 2-extremal block — confirming the seam is *distributed* (rim + digons + A-block),
> **not** a two-block Hajós split.

This **proves**, for the three `n=7` `MC=0` members, that A-prime holds through clause
(b) with a concrete `W₃` A-block. It does **not** prove the general step.

---

## 3. The attempted contradiction, assembled

Putting §1–§2 together, a smallest seamless non-base 2-extremal `D` would have to:

1. have `≥1` single edge and a digon forest with `ndig ≤ n−1` (§1.1) **[proved]**;
2. have no Hajós merge vertex (§1.2′) **[proved]**, so survive only by lacking a
   tree-join seam too;
3. have a vertex 2-cut `{a,b}` in `U(D)` (§1.3) **[sketched / verified]**;
4. on the **small** side of some vertex 2-cut, the induced block closed with the
   interface digon would be a **strictly smaller** sub-digraph `B`;
5. by **minimality** of `D`, that smaller block `B`, **if** it is itself 2-extremal,
   lies in `H₂` (it is smaller, so either base or seamed by induction);
6. then `D` is the tree-join of `B` (on the A-edge `{a,b}`) with the residual structure
   (rim minimal trail + remaining digons), giving a clause-(b) seam — **contradiction.**

> **[sketched] The contradiction goes through IF:** (i) every non-base 2-extremal has a
> vertex 2-cut [§1.3, conjectural]; (ii) for some vertex 2-cut, the small side closed
> with its interface digon is **2-extremal** and strictly smaller [the W₃-realisability
> step]; (iii) the residual structure after removing the small block is a valid
> tree-join skeleton with **even B-parity** [the parity/rim step, `proof_attempt.md
> §2, Lemma C`]. **None of (i)–(iii) is proved in general.**

---

## 4. Exactly where it does NOT close (honest accounting)

This angle reduces "seamless minimal counterexample is impossible" to **three** open
sub-claims, two of which were already isolated by the prior passes and one new:

**(G1) [conjectural] Vertex-2-cut existence for non-base.** "Non-base 2-extremal ⇒
`U(D)` not 3-connected." `40/40` over `n≤7`, but the base class is *mixed* (some wheels
are 3-connected, some are not), so this is not a clean dichotomy and I have no proof.
*Why it resists:* 3-connectivity of `U(D)` is a global property; the digon-forest +
balanced-single structure (P2+P3) constrains it but I cannot rule out a 3-connected
non-wheel realisation symbolically. **A clean attack:** show that a 3-connected `U(D)`
with `F_D` a forest and single arcs forming `≤?` disjoint cycles forces `χ⃗ = 2` or a
wheel structure — untried.

**(G2) [conjectural] Small-side 2-extremality (the real crux).** Given a vertex 2-cut
`{a,b}`, that the **small side closed with the interface digon is 2-extremal** (so
minimality applies). Over `n≤7` the small side is always `W₃` — but this is the
*decomposition direction* of the construction, which is exactly the
`MC=1 ⇒ genuine-Hajós-sides` gap (`seam_invariant.md §3.2`) re-expressed for 2-vertex
interfaces. The induction needs: *cutting at a `{a,b}`-interface yields a smaller
2-extremal block.* This is the **Lemma-B-style** soundness gap and is **not** proved.
The `MC=1` sub-case of §1.2′ collapses **into this same gap**: there a single-vertex
split must yield two 2-extremal Hajós factors, equally unproved.

**(G3) [conjectural] Rim/parity validity.** That the residual (minimal trail as rim +
remaining digons + the A-block) is a **valid** 2-Hajós tree join: rim = leaves in plane
cyclic order, and every leaf-to-leaf path uses an **even** number of B-edges. The
parity ⟺ 2-extremal equivalence is `Lemma C` (`proof_attempt.md §2`), verified
`44/44` on the *forward* construction but **not** proved for the **decomposition**
direction, and the "minimal trail is a valid rim" geometric step (§2.3) is only sketched.

### What IS new and solid from this angle

- **[proved] §2.1 Leaf attachment lemma** and **§2.2 minimal-trail-is-a-simple-cycle**
  (`k≥3`): rigorous consequences of P2+P3+Eulerian, verified `0` exceptions over `n≤7`.
- **[proved, for the three `MC=0` members] §2.4 A-edge mechanism**: the tree-join
  interface is a **non-adjacent vertex 2-cut**, the small side closed is exactly `W₃`,
  the large side is *not* independently 2-extremal — so the seam is provably
  *distributed*, not a two-block split. This pins the precise reason clause (a) fails
  and clause (b) is forced, and it is a theorem **about those members**.
- **[proved] §1.2′**: a seamless minimal counterexample has **no Hajós merge vertex**
  (contrapositive of the proved necessity half), so the entire weight is on exhibiting a
  **tree-join** seam — narrowing the target to G2+G3.

### One-line status

The minimal-counterexample contradiction **reduces** to the conjunction (G1) ∧ (G2) ∧
(G3). (G2) is the genuine crux — it is the unproved *decomposition-soundness* step (cut
yields a smaller 2-extremal block), the same wall the Hajós-sufficiency and Lemma-B
gaps hit. **The angle sharpens, but does not close, Sub-lemma A-prime.**

---

## 5. Concrete next attacks (priority)

1. **[do next, symbolic — targets G2] χ⃗=3 criticality on a vertex 2-cut.** `D` is
   3-dicritical. Fix a vertex 2-cut `{a,b}` with small side `S`. For a single arc `e`
   inside `S`, `D−e` is 2-dicolourable; its 2-dicolouring restricted to the boundary
   `{a,b}` must be one of `≤ 3` patterns. Show the small side closed with `{a,b}`-digon
   inherits a *forced* 3-dicritical structure (hence is 2-extremal) **or** the boundary
   pattern forbids `λ=2` on the large side. This is the digraph analogue of "a critical
   edge sits in a small separator", and it directly attacks **G2**, the crux.
2. **[do next, symbolic — targets G1] 3-connectivity ⇒ base.** Prove: a 2-extremal `D`
   with `U(D)` 3-connected is a generalised wheel or symmetric odd cycle. The forest
   `F_D` plus `≤ t` disjoint single cycles (P2+P3) realising a 3-connected graph is very
   rigid; enumerate the realisations.
3. **[verification, raises support] Reach `L₈`** (`enumerate.py`). A seamless / `MC=0`
   non-tree-join member at `n=8`, or a non-base with no vertex 2-cut, would refute G1 or
   G3 and would be a real structural obstruction (re-verify per README discipline).
   Its absence raises support to `n≤8`.

---

## 6. Reproduction (system python, no deps)

```
cd problems/two_extremal_digraphs
python3 scripts/seam_invariant.py        # MC invariant, 40/40 + L3..L5 consistency
```
The structural run logs cited above (`single-cycle-lens`; "leaves with no single arc:
[] count 0"; "non-base members whose U(D) is 3-connected: []"; the vertex-2-cut and
W₃-block tables for `7.7/7.14/7.36`) are produced by the inline probes recorded in this
pass; they reuse `h2_oracle.is_2extremal`, `_is_generalised_wheel`,
`_hajos_decompositions`, and `seam_invariant.{split_digons_singles, mixed_2_cuts,
underlying_edges, _components_minus}` only. No `.venv` / networkx is required; any
`.venv` created during this pass was removed per the hard rule.

**Honest bottom line.** This angle yields three genuinely **proved** structural lemmas
(leaf attachment, minimal-trail = simple `k≥3` cycle, the W₃ A-edge mechanism for the
three `MC=0` members) and **provably** confines a seamless minimal counterexample to the
tree-join clause with no Hajós merge vertex. It then **reduces** the impossibility to
(G1) vertex-2-cut existence, (G2) small-side 2-extremality, (G3) rim/parity validity —
with **(G2)** the load-bearing, still-open *decomposition-soundness* crux. Empirical
agreement is `n ≤ 7`; this is verification, not a proof.
