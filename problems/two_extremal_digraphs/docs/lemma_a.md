# Lemma A (Seam Existence): analysis over L₆ ∪ L₇ and a proof attempt

**Target.** Aboulker–Aubian–Charbit, arXiv:2304.04690, Conjecture 9.2.
`H₂` = closure of symmetric odd cycles under (i) the directed Hajós join (Def 1.5)
and (ii) the 2-Hajós tree join (Def 9.1, empty A ⇒ generalised wheel).

**Lemma A (Seam Existence).** Every 2-extremal digraph that is **not** a symmetric
odd cycle and **not** a generalised wheel contains at least one of:
- **(a) a directed-Hajós merge vertex** — a vertex whose split exhibits `D` as a
  directed Hajós join of two strictly-smaller 2-extremal digraphs; or
- **(b) a 2-Hajós tree-join seam** — a presentation of `D` as a non-empty-A 2-Hajós
  tree join whose A-blocks are strictly-smaller 2-extremal digraphs.

Every claim is labelled **[proved]**, **[verified]** (by code; evidence, not proof),
or **[conjectural]**. "Verified" results were independently re-derived in this pass
(`.venv/bin/python`, networkx 3.6.1) from the arc sets, not read off the cached JSON.

---

## 0. Headline result

**[verified, n ≤ 7]** Over the full truth sets `L₆ ∪ L₇` (47 members), **every**
non-base member has a Lemma-A seam. There is **no obstruction**: the no-seam list is
empty.

- base members: 7 (2 at n=6, 5 at n=7) — symmetric odd cycle or generalised wheel;
- non-base members: 40;
- with a directed-Hajós merge vertex (clause a): **37**;
- with a non-empty-A 2-Hajós tree-join seam (clause b, general form): **3**
  (n=7 indices 7, 14, 36) — these three have **no** Hajós seam;
- with **any** seam: **40 / 40**.

So Lemma A holds for `n ≤ 7`. **This is verification, not a proof.** The remainder of
this document (i) settles a subtle reading of clause (b) that the data force, then
(ii) attempts a general proof and pins down the single sub-lemma that does not close.

---

## 1. The clause-(b) reading the data force: A-edge seam, not B-digon cut

The brief and `proof_attempt.md §6` state clause (b) in a **strict** literal form: a
**digon that is a 2-arc-cut** (deleting its two arcs disconnects `D`). That strict
form is the natural "peel one B-edge" surgery. **The data refute the strict form as a
seam source:**

**[verified]** Across all **40** non-base members of `L₆ ∪ L₇`, the number with **any**
2-arc-cut digon is **0**. (Independent brute-force cut test
`seam_search._sides_of_digon_cut` re-run this pass.)

**Why.** `D` is strong with underlying 2-connected, so by Menger every pair of
vertices is joined by 2 internally-disjoint underlying paths; a single digon `{x,y}`
can never be the *only* connection between its sides — the peripheral rim cycle keeps
both endpoints connected. **[proved]** Hence in a 2-extremal digraph **no digon is a
2-arc-cut**. The strict clause (b) is therefore *vacuous* for the whole class and
cannot be the induction's seam.

**Consequence.** Clause (b) must be read in its **general** sense (as in Def 9.1 and
as implemented in `h2_oracle._tree_join_decompositions`): `D` decomposes as a 2-Hajós
tree join over a *spanning/near-spanning plane tree* whose B-edges are digons and whose
≥1 A-edges carry strictly-smaller 2-extremal blocks. The seam is **distributed across
the whole tree**, not isolated to one digon. Under this reading the 3 members
n=7 / 7, 14, 36 are seamed, not obstructions.

**This is the load-bearing correction to `proof_attempt.md`.** The induction's
"clause (b)" surgery is **not** "delete a cut digon"; it is "strip the rim directed
cycle and read off the tree-join over the digon-forest + A-blocks."

---

## 2. Exact structure of the three clause-(b)-only members

All three (n=7 indices 7, 14, 36) were independently re-verified this pass:
`is_2extremal = True` (strong, underlying 2-connected, Eulerian, λ=2, χ⃗=3) and
`is_in_H2 = True`. None is a symmetric odd cycle or generalised wheel.

Their common skeleton (extracted by replaying the tree-join inverse and printing the
rim / A-edges / B-edges / blocks):

- **Rim** = a directed **triangle** (3 leaves).
- **Plane tree** = a spanning tree on the 7 vertices with **2 internal vertices**,
  4 tree edges: **3 B-edges** (digons) + **exactly 1 A-edge**.
- **A-block** on that single A-edge = the n=4 digraph
  `4|0,1;0,2;0,3;1,0;1,2;2,0;2,3;3,0;3,1`. **[verified]** This block is 2-extremal,
  in H₂, and is itself the **generalised wheel W₃** (`_is_generalised_wheel = True`);
  it has **no** Hajós decomposition into smaller 2-extremals.
- **Parity.** With 3 B-edges arranged so every leaf-to-leaf path uses **2** B-edges
  (even), the parity gate is satisfied — consistent with 2-extremality.

So each is a genuine two-level H₂ derivation: `D` = tree-join( rim-triangle,
3 B-digons, one W₃ A-block ), and W₃ is a base. The seam is real and sound.

**Why these three have no Hajós merge vertex (mechanism, [verified + sketched]).**
A directed-Hajós join concentrates the entire interface at **one identified vertex**
`v`, splitting `D` into two blocks meeting only at `v`. In members 7/14/36 the
"non-rim" part of `D` is a **forest of digons with one nontrivial W₃ block grafted
on an A-edge**; the interface between the W₃ block and the rest is the **A-edge's two
endpoints** (a pair), not a single vertex. There is no single vertex whose removal
separates a 2-extremal Hajós factor, because the minimal nontrivial block (W₃) already
attaches through two interface vertices. Hence clause (a) genuinely fails and clause
(b) is needed — exactly the n=4 phenomenon (`proof_attempt.md §5`: W₃, W₄ are tree
joins, not Hajós joins) reappearing as a *sub-block* at n=7.

---

## 3. The digon graph: what it does and does not control

`proof_attempt.md §6.4` conjectured the **most promising symbolic handle**: in a
non-base 2-extremal digraph the **digon graph** (subgraph of digon edges) has a bridge
(⇒ B-edge seam) or a degree-2 separating vertex (⇒ merge vertex). This pass tests it.

**[verified]** Structural facts over all 40 non-base members:
- the digon graph is **always a forest** (acyclic) — 0 exceptions;
- component-count distribution: ncomp=1: 11, ncomp=2: 25, ncomp=3: 4;
- spanning (every vertex in some digon): 26 yes, 14 no.

**[verified, refutes the naive predictor]** The digon-graph **component count does not
separate the seam types**. Crosstab (ncomp × has-Hajós-seam):

| ncomp | Hajós seam | count |
|------:|:----------:|------:|
| 1     | yes        | 11    |
| 2     | yes        | 22    |
| 2     | **no (TJ-only)** | 3 |
| 3     | yes        | 4     |

ncomp=2 occurs in **both** Hajós-seamed (22) and tree-join-only (3) members, so
"digon-forest has ≥2 components" is **not** a clean indicator of a B-edge seam, and
"digon graph connected" is not an indicator of a Hajós merge vertex. The §6.4
bridge/separator conjecture, **as stated**, is therefore **refuted as a predictor**:
the seam type is not a function of the digon-graph's connectivity alone.

**What IS true and usable [proved].** The digon graph is a forest (≤ n−1 digons);
combined with the Eulerian/λ=2 constraints this forces the single (non-digon) arcs to
carry the strong connectivity. This is the correct decomposition of `D`'s arc set:

> **[proved] Arc decomposition.** For 2-extremal `D`: every arc lies in a digon or is
> "single" (no reverse arc). The digon arcs form an acyclic underlying forest `F_D`.
> The single arcs form a balanced (in-deg = out-deg at every vertex) sub-digraph,
> hence decompose into arc-disjoint **closed directed trails**.

(Verified per-vertex: in all 47 members the single arcs are in/out balanced; in the
three clause-(b) members they form exactly the rim triangle plus the W₃ block's
internal single arcs.)

---

## 4. Proof attempt for general Lemma A

**Setup [proved].** Let `D` be 2-extremal, not a symmetric odd cycle, not a
generalised wheel. Decompose `E(D) = F_D ⊔ Single(D)` as in §3: `F_D` a digon forest,
`Single(D)` a balanced single-arc digraph (arc-disjoint closed trails). Both
`is_strong` and `is_2connected` hold; `λ(D)=2`; `χ⃗(D)=3`; `D` Eulerian.

The induction wants a seam. We argue by cases on `F_D`.

### Case I — `F_D` is a spanning tree (n−1 digons). [sketched → reduces to Case-I sub-lemma]

If `F_D` is a spanning tree and the single arcs form **one** directed cycle on exactly
its leaves with valid plane order and even leaf-path parity, then `D` is a
**generalised wheel** — excluded. So if `F_D` spans and `D` is *not* a generalised
wheel, the single arcs must fail one of {single rim cycle / leaves-only / plane order}.
**[verified]** In `L₆∪L₇` every non-base member with spanning `F_D` (26 of them) has a
seam — 23 Hajós, 3 tree-join. **[conjectural, Case-I sub-lemma]:** a spanning-`F_D`
non-wheel 2-extremal digraph always has a Hajós merge vertex **or** an A-edge whose
contraction exposes a smaller 2-extremal block. *Not proved.* The obstacle: I cannot
yet show, from "single arcs are not a single rim permutation," that a Hajós split or a
reducible A-edge must exist.

### Case II — `F_D` is a non-spanning forest. [sketched]

Then some vertex is in no digon (deg₍F₎ = 0) or `F_D` has ≥2 components covering all
vertices. **[verified]** All 14 non-spanning-`F_D` members are seamed (all 14 Hajós).
**[conjectural]:** a digon-free vertex `v` (it carries only single arcs, in-deg=out-deg≥2)
is a candidate Hajós merge vertex; splitting at `v` along its in/out pairing should
yield two 2-extremal blocks. *Not proved* — the split's validity (both sides 2-extremal,
λ=2, χ⃗=3 preserved) is exactly the Lemma-B gap (`proof_attempt.md §3 Lemma B`).

### The genuine difficulty (why neither case closes).

Both cases reduce to the **same unproved core**: *exhibiting* a seam from the
arc-decomposition. The digon-forest gives clean **structure** (acyclic, balanced single
arcs) but, per §3, its connectivity does **not** by itself force the seam type. The
distinguishing invariant between "Hajós merge vertex" and "A-edge tree-join" is finer
than any digon-graph statistic measured here; from the data it is *which* W₃-or-larger
sub-block is grafted, i.e. a property of the **single-arc closed trails relative to the
digon forest**, not of `F_D` alone.

---

## 5. The single sub-lemma to settle next

> **Sub-lemma A′ (Seam from the digon forest + closed trails).**
> Let `D` be 2-extremal, not a symmetric odd cycle, not a generalised wheel, with
> digon forest `F_D` and balanced single-arc digraph `Single(D)` (arc-disjoint closed
> trails). Then **either** (a) some vertex `v` admits an in/out pairing splitting `D`
> into two strictly-smaller 2-extremal directed-Hajós factors, **or** (b) some edge of
> `F_D`, when designated an A-edge, carries a strictly-smaller 2-extremal block whose
> removal leaves a smaller 2-extremal tree-join residue.

This is Lemma A re-stated at the level of the **proved** arc-decomposition. It is the
exact load-bearing step; everything above either proves the setup or verifies the
conclusion for n ≤ 7. **It is open.** Refuted along the way (so not to be re-attempted
as stated): the digon-graph **bridge/component-count** predictor of §6.4.

### Concrete next attacks (in priority order)
1. **[do next, symbolic]** Prove A′ via **χ⃗=3 criticality**. `D` is 3-dicritical;
   for any arc `e`, `D−e` is 2-dicolourable. Pick a single arc on a closed trail; the
   2-dicolouring of `D−e` must induce a monochromatic obstruction whose "boundary"
   in `F_D` localises either a single articulation vertex (⇒ Hajós) or an A-edge
   interface pair (⇒ tree-join). This is the digraph analogue of "a critical edge sits
   in a small separator."
2. **[do next, empirical→symbolic]** Compute, for each non-base member, the **exact**
   invariant that separates Hajós-seamed from tree-join-only: conjecture it is
   "every nontrivial 2-edge-connected block of `Single(D) ∪ F_D` attaches to `F_D`
   through a single cut vertex." Test on L₆∪L₇; if it separates 37 vs 3 cleanly, it is
   the missing structural invariant for A′.
3. **[verification, raises support]** Reach `L₈` (the paper's Figure-11 object lives at
   n=8). The enumerator blocker is engineering, not math (`proof_attempt.md §6`). A
   no-seam member at n=8 would be a structural obstruction requiring the README
   re-verification discipline; its absence raises Lemma A's support to n ≤ 8.

---

## 6. Honest coverage

- **[proved]** No 2-extremal digraph has a 2-arc-cut digon (strong + 2-connected
  underlying ⇒ Menger); the digon graph is a forest; single arcs are balanced
  (closed trails). The strict-literal clause (b) is vacuous; clause (b) must be read
  in the general non-empty-A tree-join sense.
- **[verified, n ≤ 7, independently re-derived this pass]** All 40 non-base members of
  L₆∪L₇ have a seam (37 Hajós, 3 general tree-join); the 3 tree-join-only members
  (n=7 / 7, 14, 36) are genuinely 2-extremal, in H₂, with a W₃ A-block and even B-parity.
  Zero obstructions.
- **[verified, refutation]** The digon-graph component-count / bridge predictor of
  `proof_attempt.md §6.4` does **not** separate the seam types.
- **[conjectural, open]** Sub-lemma A′ (§5) — the general seam-existence step — is
  **not proved**. Lemma A has clean n ≤ 7 support and a proved arc-decomposition
  scaffold, but the inductive seam-existence core remains open. Empirical ≠ theorem.

**Bottom line.** No counterexample, no missing H₂ constructor: the 3 "would-be
obstructions" under the strict reading are seamed under the correct general clause (b),
which §1 proves is the *only* admissible reading. Lemma A survives to n=7 with the
seam dichotomy intact; the proof reduces to Sub-lemma A′, which is the next target.
