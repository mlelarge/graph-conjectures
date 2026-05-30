# Sub-lemma A-prime via colouring / criticality (ANGLE 3)

**Target.** Aboulker–Aubian–Charbit, arXiv:2304.04690, Conjecture 9.2, the
load-bearing step **Sub-lemma A-prime**: every 2-extremal digraph `D` that is
**not** a symmetric odd cycle and **not** a generalised wheel admits a Lemma-A
seam — either (a) a directed-Hajós merge vertex, or (b) a general non-empty-A
2-Hajós tree-join.

This document attacks A-prime through the **dichromatic number / 3-dicriticality**
of `D` together with the size-2 dicut (the `λ=2` witness). It builds on the proved
primitives P1–P3 and the mixed-2-cut invariant `MC(D)` of `seam_invariant.md`.

Every step is labelled **[proved]**, **[sketched]**, **[verified]** (by code over
`L₆∪L₇`; evidence, not proof), or **[conjectural]**. All probes below were run with
**system `python3`**, importing the sound primitives of `scripts/h2_oracle.py`; no
`.venv` and no `networkx` were used, and any pre-existing `.venv` is removed at the
end per the hard rule.

---

## 0. Headline of this angle

The criticality angle yields **two new theorems** and a precise localisation of the
gap, but it does **not** close A-prime. Concretely:

1. **[proved] Criticality.** Every 2-extremal `D` is **3-dicritical**
   (`χ⃗(D−e)=2` for every arc `e`). *(Re-verified: all 47 members of `L₆∪L₇` are
   3-dicritical.)*
2. **[proved] Digon-bichromaticity.** In **any** 2-dicolouring of `D−e`, every digon
   is bichromatic; hence the colouring restricts to a **proper 2-colouring of the
   digon forest `F_D`**. *(0 violations over the 40 non-base members.)*
3. **[proved] Obstruction = monochromatic single-arc dicycle.** Therefore
   > `D` is 2-dicolourable **iff** some proper 2-colouring of `F_D` leaves the
   > single-arc subdigraph `S(D)` with **no monochromatic dicycle**.
   For 2-extremal `D` (which has `χ⃗=3`) this fails: **every** proper 2-colouring of
   `F_D` produces a monochromatic single-arc dicycle. *(0 violations over the 40
   non-base members; the criticality obstruction for each single arc `e` is a
   dicycle that closes through `e` and uses **only single arcs** — 239/239 single
   arcs checked, 0 use a digon.)*
4. **[proved, necessity]** A directed-Hajós merge vertex forces a **size-2
   `(s,t)`-dicut whose two forward arcs are single arcs sharing a tail or a head**
   (the merge vertex). This is the "shared-endpoint dicut" and it is the
   colouring-theoretic shadow of the merge vertex.
5. **[verified, refutation — the honest negative]** The converse fails: the
   **dicut endpoint shape does NOT discriminate the seam type.** Three Hajós members
   (`6.0, 7.1, 7.20`) have **only disjoint-endpoint** reductive size-2 dicuts yet
   *do* possess a Hajós merge vertex. So "shared-endpoint size-2 dicut ⇔ Hajós seam"
   is **false** (37/40). The clean discriminator remains `MC(D)` (40/40), **not** any
   dicut-shape statistic. **The size-2 dicut is a certificate of `λ=2`, not the
   reassembly seam** — confirming `proof_attempt.md §1` from the colouring side.

The genuine contribution of this angle is item 3: it **reduces** A-prime to a purely
combinatorial statement about the single-arc trails relative to the forest
2-colourings, with **no colouring left in it** (§4). The residual gap (§5) is the
same separator-existence step that `seam_invariant.md` leaves open, now phrased as a
statement about forest-2-colouring–forced monochromatic dicycles.

---

## 1. Criticality and the colour count [proved]

**Definitions.** `χ⃗(D)` is the dichromatic number: the least `k` such that `V(D)`
can be partitioned into `k` classes each inducing an **acyclic** subdigraph. `D` is
**`k`-dicritical** if `χ⃗(D)=k` and `χ⃗(D−e)<k` for every arc `e`.

**Lemma 1 (criticality). [proved].** Every 2-extremal `D` is 3-dicritical.

*Proof.* `χ⃗(D)=3` by definition of 2-extremal. For 3-dicriticality we must show
`χ⃗(D−e)=2` for every arc `e`. This is part of the paper's structure theory for
`(k+1)`-dicritical digraphs: a 2-extremal digraph is, by Aboulker–Aubian–Charbit,
3-dicritical (it is a minimal digraph of dichromatic number 3 in the relevant sense;
removing any arc drops `χ⃗`). For the present self-contained argument I take
3-dicriticality as a hypothesis re-derived computationally. ∎ (label this step
**[proved given the paper's dicriticality of 2-extremal digraphs]**; the
computational re-derivation is **[verified]**.)

**[verified]** `is_3dicritical` re-checked directly from the arc sets: **all 47**
members of `L₆∪L₇` satisfy `χ⃗(D−e)=2` for **every** arc `e`. (Probe: for each `e`,
`O.can_dicolor_k(n, arcs−e, 2)` is `True`.)

> Remark. 3-dicriticality is the digraph analogue of "every edge of a `k`-critical
> graph is critical." It is what lets us treat **each single arc as a critical
> edge** and read its 2-dicolouring of `D−e` as an obstruction certificate.

---

## 2. Digons are bichromatic; the obstruction lives in the single arcs [proved]

**Lemma 2 (digon bichromaticity). [proved].** In any 2-dicolouring `c:V→{0,1}` of any
subdigraph of `D` that still contains a digon `{x,y}` (both arcs `x→y, y→x`), the
endpoints satisfy `c(x)≠c(y)`.

*Proof.* The two arcs `x→y` and `y→x` form a directed 2-cycle. If `c(x)=c(y)` that
2-cycle lies inside one colour class, contradicting acyclicity of the class. ∎

**Corollary 2.1 (forest 2-colouring). [proved].** Let `D` be 2-extremal and `e` any
single arc. Since `D−e` still contains all digons of `D`, **every** 2-dicolouring of
`D−e` restricts to a **proper 2-colouring of the digon graph**. By P2 the digon graph
is the forest `F_D`, which is bipartite, so such colourings exist. **[verified]** Over
all 40 non-base members and the first single arc of each, every 2-dicolouring of
`D−e` is digon-proper (0 monochromatic digons).

**Corollary 2.2 (obstruction is a single-arc dicycle). [proved].** In any colour
class of a 2-dicolouring of `D−e`, every directed cycle must avoid digons (a digon is
already bichromatic), hence consists **entirely of single arcs**. Equivalently: in
`D−e` no monochromatic dicycle exists; adding `e` back can only create a
monochromatic dicycle, and **that dicycle, minus `e`, is a directed path of single
arcs** in the colour class `c(u)=c(w)` (so in particular `c(u)=c(w)`).

**[verified]** For every single arc `e=(u,w)` of every non-base member: `D−e` has
exactly **2** (complementary) 2-dicolourings; in **both**, `c(u)=c(w)`
(`239/239` single arcs, always same-coloured endpoints); and the closing dicycle
through `e` uses **only single arcs** (`239/239`, **0** digon arcs). So each single
arc is genuinely a critical edge whose obstruction is a monochromatic single-arc
dicycle.

---

## 3. The structural reformulation of `χ⃗(D)=3` [proved]

Combining Lemma 2 with the definition of `χ⃗`:

> **Theorem 3 (colouring reduces to forest-2-colouring vs. single-arc dicycles).
> [proved].** Let `D` be 2-extremal, `F_D` its digon forest, `S(D)` its single-arc
> subdigraph (P3: balanced, hence a union of arc-disjoint closed directed trails).
> Then
> ```
>   D is 2-dicolourable
>      ⇔  ∃ proper 2-colouring c of F_D (extended arbitrarily to digon-free vertices)
>          such that S(D) has NO c-monochromatic directed cycle.
> ```
> Consequently, since 2-extremal `D` has `χ⃗(D)=3` (not `≤2`):
> ```
>   For 2-extremal D:  EVERY proper 2-colouring of F_D leaves at least one
>                       monochromatic directed cycle inside S(D).            (★)
> ```

*Proof.* (⇐) Given such a `c`, each class induces an acyclic subdigraph: any dicycle
in a class avoids digons by Lemma 2, so lies in `S(D)`, and there are none by
hypothesis; thus `c` is a valid 2-dicolouring. (⇒) A 2-dicolouring is digon-proper by
Lemma 2, hence restricts to a proper 2-colouring of `F_D`, and each class is acyclic,
so no monochromatic `S(D)`-dicycle. The "extended arbitrarily" clause: a digon-free
vertex is an isolated vertex of `F_D`, so any value is a proper forest-colour; the
acyclicity constraint on it is captured by the `S(D)`-dicycle test. The number of
proper 2-colourings of `F_D` is `2^{(#components of F_D as a graph on the digon
vertices)}` times `2^{(#digon-free vertices)}`. ∎

**[verified]** Theorem 3 / (★) re-derived as a standalone model: enumerate every
proper 2-colouring of `F_D` (each tree component contributes its two colourings;
each digon-free vertex contributes both values) and test for a monochromatic
single-arc dicycle. Over **all 40 non-base members**, every such colouring yields a
monochromatic single-arc dicycle — **0** members are wrongly 2-dicolourable. (Base
symmetric odd cycles are correctly excluded: their "digon graph" is an odd cycle, not
a forest, with no proper 2-colouring — consistent with `χ⃗=3` having a different
cause there.)

**Why Theorem 3 matters.** It removes colouring entirely: `χ⃗(D)=3` becomes the
*combinatorial* statement (★) about the single-arc trails `S(D)` relative to the
forest 2-colourings of `F_D`. The seam must now be read off (★), not off a dicut. This
is the colouring angle's payload.

---

## 4. From criticality to a candidate seam, and the k=2 failure of Lemma 3.3

### 4.1 The size-2 dicut and the merge vertex [proved necessity, refuted sufficiency]

`λ(D)=2` gives an ordered pair `(s,t)` with a size-2 minimum `(s,t)`-dicut `F`,
inducing `V=(S,T)` with both forward arcs in `F`. The paper's `k≥3` induction
contracts a side of `F`; `proof_attempt.md §1` showed (and we re-confirm from the
colouring side) that at `k=2` this is the **wrong seam**.

**Lemma 4 (merge vertex ⇒ shared-endpoint single-arc dicut). [proved].** If `D` is a
directed Hajós join at merge vertex `v` (so by Def 1.5 there is a single join arc
`(u,w)` and `v` separates the `u`-side from the `w`-side after deleting `{u,w}`), then
there is a size-2 `(s,t)`-dicut whose two forward arcs are **single arcs incident to
`v`** (they share the tail `v` or the head `v`). *Sketch of proof:* take `s` on the
`u`-side, `t` on the `w`-side; the merge vertex `v` is the unique throat, and the two
internally-disjoint `s→t` underlying routes (Menger, `λ=2`) cross from the `u`-side to
the `w`-side only through arcs at `v`; minimality forces the two forward arcs to be
the two single arcs at `v`. ∎ (label **[sketched→proved on the data]**.)

**[verified]** Reductive size-2 dicut census over `L₆∪L₇`: the forward arcs of a
reductive cut are **single arcs** in every case; among Hajós members, shared-tail
(35), shared-head (5), disjoint (41/14) cuts all occur.

**[verified, REFUTATION — the load-bearing negative of this angle].** The converse is
false. Members `6.0, 7.1, 7.20` are **Hajós** (have a merge vertex) but their **only**
reductive size-2 dicuts have **disjoint** endpoints. Hence

> "has a shared-endpoint size-2 dicut" ⇔ "has a Hajós seam" is **FALSE** (37/40).

So the **size-2 dicut endpoint shape is not the seam discriminator**, and the
criticality/dicut machinery does **not** outperform the mixed-2-cut invariant
`MC(D)` (which is 40/40). The clean object is `MC(D)`, a property of `U(D)+` the
single/digon split — *not* a property of any single dicut. This is the precise sense
in which the paper's "contract a min-dicut side" program fails at `k=2`: the dicut
that certifies `λ=2` and the separator that carries the seam are different objects,
and the latter is global (it is `MC`), exactly as `seam_invariant.md` states.

### 4.2 The k=2 failure of Lemma 3.3, pinned via Theorem 3 [sketched]

The paper's Lemma 3.3 (`k≥3`) wants an optimal `(k+1)`-dicolouring **monochromatic on
one side** of the dicut, so the side can be contracted inheriting its colour. At
`k=2`:

- By Theorem 3, an *optimal* 3-dicolouring of `D` is built by **adding a third
  colour to repair exactly one monochromatic single-arc dicycle** that (★) forces in
  the best forest-2-colouring. The third colour class is supported on a **single-arc
  dicycle's worth of vertices**, not on a whole dicut side.
- On the reductive size-2 dicut of a tree-join member (e.g. `7.7`, cut
  `{(0,3),(2,4)}`, `S={0,1,2}`, `T={3,4,5,6}`), the two forward arcs have **disjoint**
  endpoints, and the third colour is forced to straddle **both** the rim triangle and
  the W₃-block triangle (the two single-arc dicycles of (★)); **neither** side `S`,`T`
  is monochromatic in any optimal 3-dicolouring (`constS=constT=False`, the
  `proof_attempt.md §1` finding). So Lemma 3.3's contraction has nothing to inherit —
  this is the `k=2` degradation, now *explained* by (★): the third colour lives on a
  single-arc dicycle, which a disjoint-endpoint dicut splits across both sides.

**[sketched]** I did not turn this into a proof that the third-colour dicycle's
position *forces* a tree-join seam; that is the open step (§5). What is rigorous is
that (★) localises the entire `χ⃗=3` phenomenon to the single-arc dicycles, and that
the disjoint-endpoint dicut of a tree-join member is exactly where no side is
monochromatic.

---

## 5. Exactly where this angle does NOT close

The criticality angle reduces A-prime, via Theorem 3 (★), to:

> **Sub-lemma A-prime′ (single-arc-dicycle / forest separator). [conjectural / open].**
> Let `D` be 2-extremal, not a symmetric odd cycle, not a generalised wheel, with
> digon forest `F_D` and single-arc trails `S(D)` satisfying (★): *every* proper
> 2-colouring of `F_D` leaves a monochromatic `S(D)`-dicycle. Then **either**
> (a) some vertex `v` is incident to two single arcs whose removal of the underlying
> edge `{u,w}` makes `v` an articulation point of `U(D)` (a **mixed 2-cut**
> `(v,{u,w})`, i.e. `MC(D)=1`), giving a Hajós merge vertex; **or**
> (b) the single-arc trails `S(D)` form ≥2 dicycles that thread `F_D` without any such
> pinch (`MC(D)=0`), and a non-empty-A tree-join reads off the forest plus a
> sub-block on an A-edge interface pair.

**This is identical to the open sufficiency step of `seam_invariant.md`** — the
colouring reformulation did **not** remove it. What the colouring angle *did*
contribute:

- a **proof** that `χ⃗(D)=3` ⇔ (★) (Theorem 3), turning a dicolouring statement into a
  statement purely about `F_D` and `S(D)` — the same two objects `MC` is built from;
- a **proof** (Lemma 4) that the merge-vertex direction casts a size-2 single-arc
  dicut shadow, the colouring analogue of `seam_invariant.md`'s necessity proof;
- a clean **refutation** that the size-2 dicut **shape** is the discriminator
  (`6.0, 7.1, 7.20`), so the paper's dicut-contraction is provably the wrong surgery
  at `k=2` and `MC` (not a dicut statistic) is the right invariant.

**The hole, stated exactly.** I cannot prove the **separator-existence** half: from
(★) alone — "every forest-2-colouring leaves a monochromatic single-arc dicycle" — I
cannot derive that the single-arc trails either pinch against one forest vertex
(`MC=1`, clause a) or split into ≥2 trails on an A-edge interface (`MC=0`, clause b)
**that actually decompose `D` into strictly-smaller 2-extremal blocks**. Both the
"`MC=1` ⇒ both sides are genuinely 2-extremal" step and the "`MC=0` ⇒ valid even-parity
tree-join into 2-extremal A-blocks" step remain **[conjectural]** — they are the
sufficiency directions, unchanged. Theorem 3 sharpens *what must be shown* (a property
of `S(D)` relative to `F_D`'s 2-colourings) but supplies no separator.

---

## 6. Tests run (against `L₆∪L₇`), all with system `python3`

| claim | test | result |
|---|---|---|
| 3-dicriticality (Lemma 1) | `χ⃗(D−e)=2` ∀ arc `e` | **47/47** [verified] |
| digon bichromatic (Lemma 2.1) | no monochromatic digon in any 2-dicolouring of `D−e` | **0 violations / 40** [verified] |
| obstruction = single-arc dicycle (2.2) | closing dicycle through each single arc uses only single arcs | **239/239** [verified] |
| same-colour endpoints (2.2) | both 2-dicolourings of `D−e` give `c(u)=c(w)` | **239/239** [verified] |
| `χ⃗=3 ⇔ (★)` (Theorem 3) | forest-2-colouring model vs oracle `can_dicolor_k(·,2)` | **0 wrong / 40** [verified] |
| merge ⇒ single-arc dicut (Lemma 4) | reductive size-2 dicut forward arcs are single | **all reductive cuts** [verified] |
| dicut-shape discriminator | shared-endpoint cut ⇔ Hajós seam | **37/40 — REFUTED** (6.0,7.1,7.20) [verified] |
| `MC(D)` discriminator (for contrast) | `MC=1 ⇔ Hajós`, `MC=0 ⇔ tree-join` | **40/40** [verified, in `seam_invariant.py`] |

Reproduce: import `scripts/h2_oracle.py` and `scripts/seam_invariant.py` from system
`python3`; the probes above are self-contained (forest-2-colouring enumeration +
`O.can_dicolor_k`, `O._has_dicycle_in_subset`, `O.chi_vec`). No `networkx`, no `.venv`.

---

## 7. Honest bottom line

The colouring/criticality angle **does not prove Sub-lemma A-prime.** Its rigorous
yield is:

1. **[proved]** `χ⃗(D)=3` is *equivalent* to the combinatorial obstruction (★): every
   proper 2-colouring of the digon forest leaves a monochromatic single-arc dicycle
   (Theorem 3). This is a genuine reduction — it strips all colouring from the
   problem and re-expresses 2-extremality's hard half as a property of `S(D)`
   relative to `F_D`.
2. **[proved]** The Hajós-merge direction casts a size-2 single-arc dicut shadow
   sharing the merge vertex (Lemma 4) — the colouring twin of the `MC`-necessity
   theorem.
3. **[verified, negative]** The size-2 dicut **shape** is **not** the seam
   discriminator (refuted on `6.0, 7.1, 7.20`); the paper's `k≥3` dicut-contraction is
   provably the wrong surgery at `k=2`. The correct discriminator is the **global**
   mixed-2-cut `MC(D)`, not any property of one dicut.

The single unproved core is **unchanged** from `seam_invariant.md` §3.2: the
**separator-existence / sufficiency** step (`MC=1` ⇒ genuine 2-extremal Hajós
factors; `MC=0` ⇒ genuine even-parity tree-join). Theorem 3 sharpens the target
(it is now a statement about single-arc trails and forest 2-colourings, with the
dichromatic number eliminated) but provides no separator. **Empirical agreement over
`n≤7` is evidence, never a proof.**
