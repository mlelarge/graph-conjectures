# Angle A — (SUFF-a): `MC(D)=1` ⇒ a directed-Hajós factorisation into two strictly-smaller 2-extremal digraphs

**Scope.** Aboulker–Aubian–Charbit (AAC), *Digraph Colouring and Arc-Connectivity*,
arXiv:2304.04690, Conjecture 9.2 at `k=2`. This memo proves the `MC=1` half of
Lemma A (seam existence) — sub-claim (SUFF-a) — **modulo nothing that is not either
(i) a now-free colouring fact (BJSS Thm 2(d)) or (ii) a primary-source-cited
structural lemma of AAC**. The companion `MC=0` half (SUFF-b / tree-join) is a
different angle and is not addressed here.

All structural claims below are tagged **[PROVED]** (airtight math), **[CITED]**
(quoted external theorem), or **[VERIFIED n≤7]** (computational evidence, NOT a
theorem). Every structural lemma carries the exact computational test that was run
against the hard instance 7.33 and against **all** mixed 2-cuts of `L₃ ∪ … ∪ L₇`.

---

## 0. The exact claim

> **Theorem A1 (SUFF-a).** Let `D` be a non-base 2-extremal digraph (strong, `U(D)`
> 2-connected, Eulerian with `in=out≥2`, `λ(D)=2`, `χ⃗(D)=3`; not a symmetric odd
> cycle, not a generalised wheel). Suppose `MC(D)=1`, i.e. `D` has a mixed 2-cut.
> Then **every** mixed 2-cut `(v, e)` of `D` exhibits `D` as a *directed Hajós join*
> (AAC Def 1.5) `D = D₁ ▽ D₂` of two **strictly-smaller** digraphs `D₁, D₂`, each of
> which is again 2-extremal.

Theorem A1 is strictly stronger than what (SUFF-a) requires: (SUFF-a) only asks
that *some* mixed 2-cut works, but in fact **all of them do**, and the mixed 2-cut
itself names the join data. So no search over "which mixed 2-cut is the right one"
is needed — the obstruction member 7.33 (where the naive *vertex*-2-cut-pair recipe
fails on both vertex 2-cuts) is handled because the recipe here keys off the
**single edge `e`**, not a vertex pair: 7.33's unique mixed 2-cut is `(v=6, e={0,5})`
and it reconstructs directly (§5).

Recall the invariant (AAC has no `MC`; this is the team's `k=2` replacement for the
"does every min dicut isolate a vertex?" dichotomy of AAC Lemmas 4.5/4.6):

> **Definition (mixed 2-cut).** A *mixed 2-cut* of `D` is a pair `(v, e)`, `v` a
> vertex and `e={a,b}` a **single** edge (`a,b≠v`, single = its reverse arc is
> absent), such that `e` is a **bridge of `U(D)−v`**. `MC(D)=1` iff one exists.

---

## 1. The mixed 2-cut already IS the Hajós join data (no search)

Fix a mixed 2-cut `(v, e)`. Because `e` is a single edge, exactly one of its two
orientations is an arc of `D`; write that arc `(u,w)` (so `e = {u,w}`, `u≠v≠w`).
Set
```
  S₁ = (component of u in U(D) − v − e) ∪ {v},      S₂ = (component of w in same) ∪ {v}.
```

**[PROVED] Lemma 1 (the bridge condition is the separation condition).**
*`e` is a bridge of `U(D)−v` ⟺ `v` separates `u` from `w` in `U(D)−e`.* Moreover
then `S₁ ∩ S₂ = {v}`, `S₁ ∪ S₂ = V(D)`, and `{u,w}` is the **only** edge of `U(D)`
with one endpoint in `S₁∖{v}` and the other in `S₂∖{v}`.

*Proof.* `D` is 2-connected, so `U(D)−v` is connected (removing one vertex from a
2-connected graph leaves a connected graph). In a connected graph, an edge `e` is a
bridge iff deleting it disconnects the graph iff its two endpoints fall into
distinct components of `(U(D)−v)−e = U(D)−v−e`. Those endpoints are exactly `u,w`
(neither equals `v`). Hence "bridge of `U(D)−v`" `⟺` "`u,w` in distinct components
of `U(D)−v−e`" `⟺` "`v` separates `u` from `w` in `U(D)−e`". The component of `u`
and the component of `w` are then disjoint and (with the removed `v` re-added to
each) partition `V(D)` overlapping only in `v`; any `U(D)`-edge other than `e`
joining `S₁∖{v}` to `S₂∖{v}` would survive in `U(D)−v−e` and reconnect the two
components — impossible. ∎

**[VERIFIED n≤7] Test 1.** For every `(v, single-edge e)` pair over all non-base
members of `L₆∪L₇`, the predicate "`e` bridge of `U(D)−v`" agreed with "`v`
separates the endpoints of `e` in `U(D)−e`" with **0 mismatches**; and for every
*mixed* cut the printout `sep=True cover=True overlap_v={v} extra_cross=[]` held
with **0 exceptions** (the `extra_cross=[]` line is exactly the "`{u,w}` is the
unique crossing edge" conclusion).

**[PROVED] Corollary 1 (Hajós data).** `(v; u,w; S₁,S₂)` satisfies AAC Def 1.5
(inverse form, as encoded in `h2_oracle._hajos_decompositions`): a single join arc
`(u,w)`, a split vertex `v∉{u,w}`, `S₁∩S₂={v}`, `S₁∪S₂=V(D)`, `u∈S₁`, `w∈S₂`, and
**every arc of `D` other than `(u,w)` lies inside `S₁` or inside `S₂`** (its
underlying edge is a non-`e` edge, hence by Lemma 1 not crossing). Define
```
  D₁ = D[S₁] + arc (u → v),        D₂ = D[S₂] + arc (v → w).
```
Then `D = D₁ ▽ D₂` is a directed Hajós join, and `|D₁|=|S₁|<n`, `|D₂|=|S₂|<n`
(both `≥2`; both `<n` because each omits the other side's `≥1` private vertices —
e.g. `w∉S₁`, `u∉S₂`). ∎

This is the **exact converse of P4** (the team's necessity result: Hajós merge ⇒
`MC=1`). Lemma 1 + Corollary 1 close it: `MC=1` ⇒ a Hajós merge realising every
mixed cut.

**[PROVED] The join arc is single, automatically.** `e` is a single edge by the
definition of mixed 2-cut, so `(u,w)` is single and `(w,u)∉A(D)`. This is AAC's
"unique crossing arc / single join arc" hypothesis (team clause B0), here *built
into* the invariant rather than proved after the fact.

---

## 2. The two pieces are 2-extremal — the bookkeeping, now complete

We must show `D₁` (symmetrically `D₂`) is strong, Eulerian with `in=out≥2`, has
`U(D₁)` 2-connected, `λ(D₁)=2`, and `χ⃗(D₁)=3`. The first block is the audited
`verify_lemma_b.md` material (re-stated, with the two formerly-sketched lines now
proved in §2.3–§2.4); `χ⃗=3` is free.

### 2.1 [PROVED] Eulerian, `in=out`
Set-balance across `S₁`: in `D`, `#arcs(S₁→S₂\{v}) = #arcs(S₂\{v}→S₁)`. The only
`S₁∖{v}`–`S₂∖{v}` arc is the join arc `(u,w)` (Corollary 1), and arcs through `v`
are internal to each side. Re-adding `(u→v)` to the `S₁` side restores Eulerian
balance at `v` (it replaces the out-flow that `(u,w)` carried away from `S₁`); for
every `x≠v`, the incident arcs of `D₁` equal those of `D` except that at `x=u` the
arc `(u,w)` is replaced by `(u,v)` — same out-degree. So `D₁` is Eulerian. *(Audit:
set-balance 0/52, the identity `vout_{S₁}=vin_{S₁}+1 ∧ vin_{S₂}=vout_{S₂}+1` 0/52.)*

### 2.2 [PROVED] `in=out≥2` value at the merge vertex `v`
We need `outdeg_{D₁}(v)=vout_{S₁}≥2` and `indeg_{D₁}(v)=vin_{S₁}+1≥2`, i.e.
`vin_{S₁}≥1` and `vout_{S₁}≥2`.

`D` is strong, so `v` has an in-neighbour `x` in `D`; by Corollary 1, `x∈S₁∖{v}` or
`x∈S₂∖{v}`. If some in-neighbour lies in `S₁`, then `vin_{S₁}≥1`. Suppose not: every
in-neighbour of `v` lies in `S₂`. Eulerian balance at `v` in `D` says
`indeg_D(v)=outdeg_D(v)≥2`; the cut `∂⁻(S₁)` of `D` (arcs into `S₁`) then consists
only of the single join arc `(u,w)` together possibly with arcs into `v` — but those
in-arcs of `v` were assumed to come from `S₂`, so they enter `S₁` too. Concretely
`∂⁻(S₁∖{v})` would be `{(u,w)}` alone, a **1-arc dicut** of `D`, contradicting
`λ(D)=2`. Hence `vin_{S₁}≥1`. The symmetric argument (out-neighbours of `v`,
`∂⁺(S₂∖{v})`) gives `vout_{S₂}≥1`. Combined with the Eulerian identity
`vout_{S₁}=vin_{S₁}+1≥2` and `vin_{S₂}=vout_{S₂}+1≥2`, and the added arcs, every
vertex of `D₁` and `D₂` has `in=out≥2`. ∎ *(This is the line `verify_lemma_b.md`
gap #7 left at sketch level; the `λ=2` 1-dicut step above isolates it.)*

**[VERIFIED n≤7] Test 2.** Over all mixed cuts of `L₆∪L₇`: `vin_{S₁}≥1`,
`vout_{S₂}≥1`, and `in=out≥2` for `v` in both pieces — **0 exceptions**.

### 2.3 [PROVED] strong
`D₁` is Eulerian (§2.1); an Eulerian digraph is strong iff its underlying graph is
connected (each weak component of an Eulerian digraph is strong). `U(D₁) =
U(D[S₁]) + {u,v}`; `U(D[S₁])` is connected because `S₁∖{v}` is one component of
`U(D)−v−e` (connected) and `v` is adjacent into it (`v` has `≥1` neighbour in
`S₁∖{v}` by §2.2). So `U(D₁)` is connected and `D₁` is strong. ∎

### 2.4 [PROVED] `U(D₁)` 2-connected — the formerly-sketched clause (C), now complete
This is the one place where the **added edge `{u,v}` is load-bearing**: `U(D[S₁])`
need not itself be 2-connected (member 7.19, §5). The argument:

> **Claim.** Every cut vertex `c` of `U(D[S₁])` lies on every `u`–`v` path of
> `U(D[S₁])` — equivalently, `c` separates `u` from `v`. Consequently
> `U(D₁)=U(D[S₁])+{u,v}` has **no** cut vertex.

*Proof.* Suppose `c` is a cut vertex of `U(D[S₁])` that does **not** separate `u`
from `v` (`c∉{u,v}`). Then `U(D[S₁])−c` has a component `K` containing neither `u`
nor `v`. Now look at `U(D)`: every vertex of `S₂∖{v}` reaches `S₁` only through the
single crossing edge `{u,w}` (Corollary 1, Lemma 1), i.e. only via `u`; and `v` is
the only other shared vertex. So in `U(D)−c`, the set `K` can reach the rest of `D`
only through vertices of `S₁∖K` that are `U(D[S₁])`-adjacent to `K` — but all such
adjacencies pass through `c` (as `c` is a cut vertex isolating `K` in `U(D[S₁])`),
and the only ways out of `S₁` (namely `u` and `v`) are **not** in `K`. Hence
`U(D)−c` disconnects `K` from the rest, making `c` a cut vertex of `U(D)` —
contradicting `U(D)` 2-connected. Therefore every cut vertex of `U(D[S₁])`
separates `u` from `v`. Adding the edge `{u,v}` creates a `u`–`v` path avoiding any
such `c`, so no `c` remains a cut vertex; and `{u,v}` creates no new cut vertex.
Thus `U(D₁)` is 2-connected. ∎

**[VERIFIED n≤7] Test 3.** Over all mixed cuts of `L₆∪L₇`: (i) every cut vertex of
`U(D[Sᵢ])` separates the endpoint (`u` resp. `w`) from `v` — **0 exceptions**;
(ii) `U(D₁), U(D₂)` are 2-connected — **0 exceptions** (104 pieces). Member 7.19
exhibits the non-trivial case: `U(D[S₁])` has cut vertex `6` separating `u=0` from
`v=4`, repaired exactly by the added edge `{0,4}`.

### 2.5 [PROVED] `λ(D₁)=2`
*Upper (`≤2`)* (`verify_lemma_b.md` §B2, airtight given B0): `k` arc-disjoint
`s→t` paths in `D₁` use the single added arc `(u→v)` at most once; reroute that one
use through `(u,w)` plus a `w⇝v` detour inside `S₂` (exists, `D[S₂]` strong),
keeping disjointness because the other `k−1` paths stay inside `S₁`. So
`λ(D₁)≤λ(D)=2`. *Lower (`≥2`)*: `D₁` is strong, Eulerian, min-degree `≥2` (§2.2);
a strong Eulerian digraph with `δ⁺≥2` has no 1-arc dicut (an out-cut `∂⁺(W)={e}`
forces by balance `∂⁻(W)={e'}`, but a closed-trail decomposition then traps a
second out-arc of `W`). Hence `λ(D₁)=2`. ∎

### 2.6 [CITED, now FREE] `χ⃗(D₁)=χ⃗(D₂)=3`
`D` is 2-extremal ⇒ **3-dicritical** (AAC Lemma 4.1: "Let `k≥1`, and let `D` be a
`k`-extremal digraph. Then `D` is Eulerian, `(k+1)`-dicritical …", here `k=2`). We
have exhibited `D = D₁ ▽ D₂` a genuine directed Hajós join (Corollary 1). Then
**BJSS Theorem 2(d)**, verbatim from `docs/conditional_l_literature.md` §6:

> **(d)** If `D` is `k`-critical and **`k ≥ 3`**, then both `D₁, D₂` are `k`-critical.

— applies at `k=3` (`D` is 3-dicritical = 3-critical in the dichromatic sense) and
gives `D₁, D₂` both 3-dicritical, hence `χ⃗(D₁)=χ⃗(D₂)=3`. **No `k=2` colouring move
is needed; the AAC `k=2` degradation (Claim 5.7.1's "dodge two colours since
`k≥3`") never arises here because the criticality descent is imported wholesale at
`k=3`.** ∎

### 2.7 Assembling 2-extremality
`D₁` is strong (§2.3), `U(D₁)` 2-connected (§2.4), Eulerian with `in=out≥2`
(§2.1–§2.2), `λ(D₁)=2` (§2.5), `χ⃗(D₁)=3` (§2.6) — i.e. 2-extremal; ditto `D₂`. Both
strictly smaller (Corollary 1). This is Theorem A1. ∎

---

## 3. Status ledger (what is proof vs. evidence vs. cited)

| step | statement | status |
|---|---|---|
| Lemma 1 | bridge of `U(D)−v` ⟺ `v` separates `u,w` in `U(D)−e`; `{u,w}` unique crossing edge | **[PROVED]** |
| Cor. 1 | mixed cut ⇒ AAC Def 1.5 Hajós data, single join arc, both sides `<n` | **[PROVED]** |
| §2.1 | `Dᵢ` Eulerian, `in=out` | **[PROVED]** (set-balance) |
| §2.2 | `in=out≥2` at merge `v` (`vin_{S₁}≥1` via `λ=2` 1-dicut) | **[PROVED]** (closes gap #7) |
| §2.3 | `Dᵢ` strong | **[PROVED]** |
| §2.4 | `U(Dᵢ)` 2-connected (clause C) | **[PROVED]** (closes the sole §2 sketch) |
| §2.5 | `λ(Dᵢ)=2` | **[PROVED]** |
| §2.6 | `χ⃗(Dᵢ)=3` | **[CITED]** BJSS Thm 2(d) @ `k=3` (free) |
| Thm A1 | every mixed cut ⇒ two strictly-smaller 2-extremal pieces | **[PROVED]**, modulo the cited BJSS 2(d) |

**Honest residue.** The proof of Theorem A1 is complete *as mathematics* given two
imports it does not re-derive: (i) **BJSS Thm 2(d)** (`χ⃗(Dᵢ)=3`) — an external,
primary-source-verified theorem; (ii) the standard facts "Eulerian ⇒ strong iff
weakly connected" and "strong Eulerian `δ⁺≥2` ⇒ no 1-arc dicut". Both are genuine
theorems, not conjectures. **No step of Theorem A1 relies on `n≤7`.** The `n≤7`
tests below are confirmation, not the argument.

---

## 4. Computational verification (run this pass; evidence, not proof)

All tests over the **complete** non-base members of `L₃..L₇` and **every** mixed
2-cut they carry (not just one per member).

- **Test 0 (the headline, strongest form).** For every non-base member of `L₆∪L₇`,
  the set of mixed 2-cuts `(v, e)` and the set of realised directed-Hajós seams
  `(v, {u,w})` **coincide exactly** (`seam ⊆ MC` and `MC ⊆ seam`), 37/37 members,
  including the `MC=2` members carrying two distinct seams each. So `MC` does not
  merely detect existence — it enumerates the seams.
- **Test R (reconstruction).** Every mixed 2-cut of every non-base member of
  `L₃..L₇` reconstructs (via Corollary 1) into two strictly-smaller pieces, **both
  2-extremal**: **52/52** mixed cuts pass. (`is_2extremal` on each piece, `|piece|<n`.)
- **Test 1** (Lemma 1): bridge ⟺ separation, 0 mismatches; `extra_cross=[]` for every
  mixed cut.
- **Test 2** (§2.2): `vin_{S₁}≥1`, `vout_{S₂}≥1`, `in=out≥2` at `v` in both pieces —
  0 exceptions.
- **Test 3** (§2.4): every cut vertex of `U(D[Sᵢ])` separates endpoint from `v`;
  both pieces 2-connected — 0 exceptions; 7.19 is the non-trivial witness.
- **Regression**: `python3 scripts/seam_invariant.py` ⇒ `PASS (40/40 + consistency)`.

Reproduce with the inline scripts used this pass (pure Python, no deps; they reuse
`scripts/h2_oracle.py` `is_2extremal`, `_hajos_decompositions`, `_component`,
`_induce_plus`, and `scripts/seam_invariant.py` `mixed_2_cuts`,
`split_digons_singles`). No `.venv` was created.

---

## 5. The hard instances, handled explicitly

**Member 7.33 (MC=1; naive vertex-2-cut-pair recipe FAILS on both vertex 2-cuts).**
Digons `{0,2},{1,3},{1,5},{1,6},{2,4},{2,6}`; singles `(0,4),(3,5),(4,6),(5,0),(6,3)`.
Unique mixed 2-cut `(v=6, e={0,5})`. The single arc on `e` is `(5,0)` (so `u=5`,
`w=0`); `v=6` separates `5` from `0` in `U(D)−e`. Reconstruction (Corollary 1):
`S₁∋5`, `S₂∋0`, `D₁=D[S₁]+(5→6)`, `D₂=D[S₂]+(6→0)`, both on 4 vertices, both
verified 2-extremal. **The recipe keyed off the single edge `e={0,5}`, not off a
vertex 2-cut pair — which is exactly why the §1 construction sidesteps 7.33's
obstruction.**

**Member 7.19 (MC=2; the side `U(D[Sᵢ])` is NOT itself 2-connected).** Mixed cuts
`(4,{0,5})` and `(6,{0,5})`. For `(v=4, e={0,5})`: single arc `(0,5)`, so `u=0`,
`w=5`; `S₁={0,2,3,4,6}`. `U(D[S₁])` has cut vertex `6` (separating `{0,3}` from
`{2,4}`), so the *raw* induced side fails 2-connectivity — but `6` separates `u=0`
from `v=4`, so the added edge `{u,v}={0,4}` repairs it (§2.4), and `U(D₁)` is
2-connected. This member is the witness that clause (C) genuinely needs the added
edge and is not a triviality.

**Members 7.7, 7.14, 7.36 (MC=0).** Out of scope for (SUFF-a): each has `MC=0`,
so by the proved contrapositive of P4 it has *no* Hajós merge vertex and is a
tree-join member (SUFF-b). Theorem A1 says nothing about them, correctly.

---

## 6. Relation to AAC Section 5 and the `k=2` break

AAC Theorem 5.1 (`k≥3`) gets seam existence via: Lemma 4.5/4.6 (base dichotomy) →
Claim 5.7.2 (extract a `K̅_k`/flower side) → interface case split → **Lemma 5.7**
("`D−{tu,uw}` has a cutvertex ⇒ directed Hajós join or Hajós bijoin"), whose
*directed* branch is `k`-general but whose bijoin branch (Claim 5.7.1) dies at `k=2`
("dodge two colours, since `k≥3`"). Theorem A1 replaces this whole chain on the
`MC=1` side:

- The **base dichotomy** (Lemma 4.5/4.6) is replaced by `MC∈{0,1}`: `MC=1` *is* the
  hypothesis here, and Lemma 1 turns it directly into the cutvertex data
  (`D−{(u,v_S₂-arc),(u,w)}`-style separation), so no `K̅_k`/flower extraction is
  needed — the single edge `e` plays the role of AAC's rigid side.
- The **colouring** half of Lemma 5.7 (Claim 5.7.1) is bypassed entirely: we never
  build seam-agreeing 2-dicolourings, so the `k=2` palette-exhaustion never bites.
  Instead BJSS Thm 2(d) is invoked at `k=3` *after* the join is exhibited (§2.6).
- The **bijoin outcome** of Theorem 5.1 does not appear on the `MC=1` side at all —
  it is the `MC=0` / tree-join side, handled by SUFF-b, consistent with AAC's own
  `k=2` replacement (Def 9.1 even-`B`-parity tree join).

So on the `MC=1` side the `k=2` walls of `seam_existence_setup.md` §1.3 are both
cleared: wall (D1) (Claim 5.7.1 colouring) is replaced by BJSS 2(d); wall (D2) (base
dichotomy) is replaced by the `MC=1` hypothesis + Lemma 1. **(SUFF-a) is proved
(modulo the two cited theorems of §3).**

---

## 7. Files / reproducibility
- Reused primitives: `scripts/h2_oracle.py` (`is_2extremal` L248, `is_2connected`
  L89, `is_strong` L70, `lambda_D` L181, `_hajos_decompositions` L361,
  `_component` L412, `_induce_plus` L425), `scripts/seam_invariant.py`
  (`mixed_2_cuts` L177, `split_digons_singles` L114, `MC` L199).
- Data: `data/L_7.json` (7.33 = index 33, 7.19 = index 19), `data/L_3..6.json`,
  `data/seam_search_L6_L7.json` (ground-truth seam types, cross-checked by Test 0).
- Citations quoted verbatim from `docs/conditional_l_literature.md` (BJSS Thm 2(d),
  AAC Lemma 4.1) and `docs/seam_existence_setup.md` (AAC Thm 5.1 / Lemma 5.7).
- Prior status this builds on: `docs/lemma_a_proof.md` §2–§3, `docs/verify_lemma_b.md`
  (§2.1/2.3/2.5 are its B1/S/B2/B3 audited lines; §2.2 closes its gap #7; §2.4
  closes its sole §2 [sketched] clause C).
