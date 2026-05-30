# Seam invariant for Sub-lemma A-prime: the MIXED 2-CUT

**Goal.** Distinguish, from the digon forest `F_D` and the single-arc closed
trails alone, which Lemma-A seam a non-base 2-extremal digraph admits:
a directed-Hajos merge vertex (clause a) or a non-empty-A 2-Hajos tree-join
(clause b).

**Why a new invariant is needed.** The seam census
(`data/seam_search_L6_L7.json`) shows the obvious candidates fail. Component
count of `F_D` is `2` in BOTH the Hajos-seamed members (e.g. 6.0, 6.1, 7.3) and
in tree-join-only members (7.7, 7.14, 7.36); the multiset of component sizes also
collides (`[2,5]` appears as Hajos in 7.3/7.15/7.28 and as tree-join in 7.14;
`[1,6]` appears as Hajos in 7.1/7.13/... and as tree-join in 7.36). So neither
component count nor component sizes separate the two seam types.

---

## 1. The invariant (computable from `F_D` + single arcs)

Let `U(D)` be the simple underlying graph of `D`. By **P2** its edges split into
the **forest edges** (digons of `F_D`) and, by **P3**, the **single edges** (the
underlying images of the single arcs; each single arc has its reverse absent, so
it contributes exactly one undirected edge).

> **Definition (mixed 2-cut).** A *mixed 2-cut* of `D` is a pair `(v, e)` where
> `v` is a vertex and `e = {a,b}` is a **single** edge with `a,b != v`, such that
> deleting both `v` and `e` disconnects `U(D)`. Equivalently, `e` is a **bridge
> of `U(D) - v`**.

Define the boolean invariant

```
MC(D) = 1   iff   D has at least one mixed 2-cut,   else 0.
```

`MC(D)` is computed in `scripts/seam_invariant.py` (`mixed_2_cuts`, `MC`) directly
from the digon/single split and the underlying graph; it never calls the heavy
Hajos/tree-join decomposition routines.

**Trail-threading reading.** `D` is 2-connected, so no single vertex and no
single edge is a cut; a mixed 2-cut is the *minimal mixed obstruction*. Contract
each tree of `F_D` to a point; the single arcs become the edges of a multigraph
`M_D` on the forest components, and the single-arc closed trails (P3) are the
closed walks carrying its cycle space. `MC(D)=1` exactly when one trail strand
`e` is "pinched" against a single articulating vertex `v` so that `{v, e}`
separates `D` — i.e. the single-arc trails thread the forest with a one-vertex,
one-strand bottleneck. The forest-component count is blind to this pinch; the
mixed 2-cut sees it. This is the finer invariant the census was asking for.

---

## 2. The rule (conjectural)

For a **non-base** 2-extremal `D` (not a symmetric odd cycle, not a generalised
wheel):

```
  D has a directed-Hajos merge vertex     <=>   MC(D) = 1
  D needs a non-empty-A tree-join seam     <=>   MC(D) = 0
```

so the predicted seam type is **hajos** if `MC(D)=1` and **tree-join** otherwise.

---

## 3. Status of each piece

| claim | status |
|---|---|
| `MC(D)` is computable from `F_D` + single arcs | **proved** (it is a property of `U(D)` plus the digon/single split) |
| Hajos merge vertex `=>` `MC(D)=1` (necessity) | **proved** (below) |
| `MC(D)=1` `=>` genuine Hajos merge vertex (sufficiency) | **conjectural** — verified 40/40 on L6 u L7, consistent on L3..L5 |
| non-base & `MC(D)=0` `=>` tree-join seam exists | **conjectural** — verified on the 3 tree-join-only members + oracle |

### 3.1 Proved direction (necessity)

Suppose `D` is a directed Hajos join at merge vertex `v`. By Def. 1.5 (and the
sound recognizer `_hajos_decompositions` in `h2_oracle.py`) there is a single arc
`(u,w)` of `D` and a vertex `v != u,w` such that, after removing the underlying
edge `{u,w}`, the vertex `v` is an articulation point separating the side `S1`
(containing `u`) from the side `S2` (containing `w`), with `S1 ∩ S2 = {v}` and
every non-join arc inside `S1` or inside `S2`. Then in `U(D)`, deleting `v`
leaves the only `S1`–`S2` connection across the edge `{u,w}`; deleting that edge
too disconnects `U(D)`. Hence `(v, {u,w})` is a mixed 2-cut and `MC(D)=1`. ∎

The contrapositive — `MC(D)=0 => no Hajos merge vertex` — is therefore also a
theorem, and is the load-bearing half for clause (b): a non-base member with
`MC(D)=0` provably has **no** clause-(a) seam, so A-prime forces it into clause
(b). The data confirms this never fails: every Hajos-seamed member has `MC>=1`
(`verify_necessity_direction`, 0 violations).

### 3.2 Conjectural direction (sufficiency)

That `MC(D)=1` implies the two underlying sides `S1, S2` are *genuinely*
2-extremal blocks (not merely an underlying-graph cut) is the open step. It holds
on all 37 Hajos-seamed non-base members of L6 u L7 and on L5.0.

---

## 4. Verification (run `scripts/seam_invariant.py`)

```
[L6 u L7 non-base members]  rule predicts seam type: 40/40 correct
   actual hajos     : 37  (all MC>=1: True)
   actual tree-join : 3   (all MC==0: True)
   tree-join-only members:
     7.7  : actual=tree-join predicted=tree-join MC=0
     7.14 : actual=tree-join predicted=tree-join MC=0
     7.36 : actual=tree-join predicted=tree-join MC=0

[L3..L5 consistency: MC(D)=1  iff  Hajos decomposition exists]
   L3.0 base=1 hajos_decomp=0 MC=0 consistent=True   (symmetric C3)
   L4.0 base=1 hajos_decomp=0 MC=0 consistent=True   (W3, gen. wheel)
   L5.0 base=0 hajos_decomp=1 MC=1 consistent=True   (non-base, has Hajos seam)
   L5.1 base=1 hajos_decomp=0 MC=0 consistent=True   (gen. wheel)
   L5.2 base=1 hajos_decomp=0 MC=0 consistent=True   (symmetric C5)

[PROVED-direction check: no member is Hajos-seamed with MC=0]  violations: NONE

OVERALL: PASS (40/40 + consistency)
```

`MC=2` rows (e.g. 7.3, 7.10, 7.37) carry two distinct mixed 2-cuts; these are
exactly the members for which the oracle records two alternative Hajos seams,
giving an independent cross-check that the mixed-2-cut multiplicity tracks the
Hajos-seam multiplicity.

### Notes / caveats

- The merge vertex `v` need **not** lie in the digon forest: member 7.17 has a
  valid mixed 2-cut `(v=3, e={4,0})` with `v` isolated in `F_D`. So the invariant
  must be phrased on `U(D)` + the single/digon split, **not** as "trails through
  forest leaves" only. The contracted-skeleton `M_D` reading subsumes this case.
- Empirical agreement over `n <= 7` is EVIDENCE, never a proof. The open step is
  the sufficiency direction in §3.2.

## 5. Files

- `scripts/seam_invariant.py` — invariant `MC`, rule, full verification harness.
- `tests/test_seam_invariant.py` — pytest pinning 40/40 + L3..L5 consistency +
  the proved necessity direction.
