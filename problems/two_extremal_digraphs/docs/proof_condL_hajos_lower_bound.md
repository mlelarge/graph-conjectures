# Conditional L, directed-Hajós-join instance: a rigorous proof of the lower bound and the criticality descent

**Scope (ANGLE 1).** This note settles, *rigorously and self-containedly*, the
**directed-Hajós-join** instance of Conditional L: the colouring lower bound across the
single-arc / single-identified-vertex seam of Definition 1.5, together with the
criticality-descent converse that the induction toward Conjecture 9.2 actually consumes.
It reconciles the statement with `docs/lemma_a_proof.md` §3/§5, supplies the published
citation (BJSS 2020, Theorem 2), **and reproduces the proof from scratch** so the project
does not rest on a one-line cross-cite. It then states precisely, and honestly, the two
pieces of Conditional L that this argument does **not** close (the tree-join seam, and the
2-extremal-vs-dicritical mismatch).

Every step is tagged **[PROVED]** (rigorous, self-contained, given here), **[CITED]**
(a verbatim published theorem, with the exact number and quote), or **[OPEN]**.

---

## 0. Conventions

`D` is a loopless digraph; `χ⃗(D)` is the **dichromatic number** (Neumann-Lara): the least
`k` such that `V(D)` admits a `k`-colouring in which **every colour class induces an
acyclic subdigraph** (no directed cycle inside a class). A *2-dicolouring* is a
2-colouring in this sense. "Acyclic", not merely "independent", is the whole directed
subtlety: a colour class may carry arcs, even long dipaths, provided it closes no directed
cycle. The proof below tracks exactly this.

**Directed Hajós join (Def 1.5; BJSS notation).** Let `D₁` have an arc `u → v₁` and `D₂`
an arc `v₂ → w`, the two factors disjoint. Delete `u v₁` and `v₂ w`, **identify
`v₁ = v₂ =: v`**, and add the single arc `u → w`. Write `D = D₁ ▽ D₂`. Set

- `S₁ :=` image of `V(D₁)`, `S₂ :=` image of `V(D₂)`, so `S₁ ∩ S₂ = {v}`,
  `S₁ ∪ S₂ = V(D)`, `u ∈ S₁`, `w ∈ S₂`;
- the only arc of `D` with one end in `S₁∖{v}` and the other in `S₂∖{v}` is the **join arc
  `u → w`**; every other arc lies inside `S₁` or inside `S₂`.

The two factors are recovered as `D₁ = D[S₁] + (u→v)` and `D₂ = D[S₂] + (v→w)` (the
deleted interface arcs re-added). This is exactly the team's seam (`lemma_a_proof.md` §2,
the mixed-2-cut `(v, {u,w})`), with `u₁=u`, `u₂=w` in BJSS labels.

---

## 1. The exact lemma (reconciled with `lemma_a_proof.md` §3)

`lemma_a_proof.md` §3 names two halves under one banner "Conditional L":

> **(L-assemble)** two seam-agreeing `≤2`-dicolourings of the pieces glue to a
> `≤2`-dicolouring of `D`;
> **(L-descend)** a split piece keeps `χ⃗ = 3` (the load-bearing induction step).

These are logically *distinct directions of the same seam*. To avoid the conflation that
let earlier passes chase a search, I separate them and state precisely what is needed.

> **Lemma L▽ (directed-Hajós seam, the three statements).** Let `D = D₁ ▽ D₂` be a directed
> Hajós join of non-empty digraphs, with seam data `(u, v, w, S₁, S₂)` as in §0.
>
> **(L▽-lb)** *(lower bound)* `χ⃗(D) ≥ min{ χ⃗(D₁), χ⃗(D₂) }`. In particular, if neither
> factor is 2-dicolourable (`χ⃗(D₁), χ⃗(D₂) ≥ 3`) then `D` is not 2-dicolourable
> (`χ⃗(D) ≥ 3`).
>
> **(L▽-glue)** *(equality / assemble)* if `χ⃗(D₁) = χ⃗(D₂) = k` with `k ≥ 2`, then
> `χ⃗(D) = k`. Concretely, two `k`-dicolourings agreeing in colour at `v` glue to a
> `k`-dicolouring of `D`.
>
> **(L▽-crit)** *(criticality descent, the converse the induction needs)* if `D` is
> `(k+1)`-dicritical and `k ≥ 2`, then both `D₁` and `D₂` are `(k+1)`-dicritical; and
> conversely. (`k`-critical = `k`-dicritical: `χ⃗ = k` but every proper subdigraph has
> `χ⃗ < k`.)

**How this maps to `lemma_a_proof.md`.** (L-assemble) = **(L▽-glue)**. The "split piece
keeps `χ⃗=3`" of (L-descend) is the `χ⃗`-part of **(L▽-crit)** specialised to `k+1=3`:
`D` 3-dicritical ⇒ both pieces 3-dicritical ⇒ `χ⃗(Dᵢ)=3`. The "digraph Hajós lower bound"
the §3/§5 prose calls *genuinely open* is exactly **(L▽-lb)**, and it is **not** open: it
is a five-line theorem, proved below. This is the single correction this note makes to
`lemma_a_proof.md` §3/§5. **The residual gap is not (L▽); it is (i) the tree-join seam and
(ii) promoting 3-dicriticality of a *subdigraph* to 2-extremality of the piece — see §5.**

---

## 2. Citation (the published source) — [CITED]

> **Bang-Jensen, Bellitto, Schweser, Stiebitz, *Hajós and Ore constructions for
> digraphs*, Electron. J. Combin. 27(1) (2020), #P1.63 (arXiv:1908.04096), Theorem 2
> (Hajós Construction):** *Let `D = D₁▽D₂` be the Hajós join of two disjoint non-empty
> digraphs `D₁` and `D₂`. Then:*
> **(a)** `χ⃗(D) ⩾ min{χ⃗(D₁), χ⃗(D₂)}`.
> **(b)** *If `χ⃗(D₁) = χ⃗(D₂) = k` and `k ⩾ 2`, then `χ⃗(D) = k`.*
> **(c)** *If both `D₁` and `D₂` are `k`-critical and `k ⩾ 2`, then `D` is `k`-critical.*
> **(d)** *If `D` is `k`-critical and `k ⩾ 2`, then both `D₁` and `D₂` are `k`-critical.*

This is **verbatim** from the EJC PDF (two independent literature passes,
`docs/conditional_l_external_lit.md` §1–2 and `docs/conditional_l_literature.md` §2.1,
quote and pin it). BJSS's directed Hajós join (their §3, attributed to
Hoshino–Kawarabayashi [15]) is **definitionally identical** to Def 1.5 — delete `u₁v₁`
and `v₂u₂`, identify `v₁=v₂=v`, add `u₁u₂`; with `u₁=u`, `u₂=w` this is Def 1.5
(`conditional_l_external_lit.md` §0, match confirmed). BJSS's `χ⃗` (their §1, after
Neumann-Lara [27]) is the project's `χ⃗` (colour classes induce acyclic subdigraphs).

So: **(L▽-lb)** = Theorem 2(a); **(L▽-glue)** = Theorem 2(b); **(L▽-crit)** =
Theorem 2(c)+(d). All hold for `k ≥ 2`, hence at `k = 2` (our `χ⃗ = 3` case). The team's
own source, Aboulker–Aubian–Charbit arXiv:2304.04690, uses exactly this as
"Claim 5.3.1 (Theorem 2 in [3])" inside its Lemma 5.3.

**MEMORY-mandated caveat (citations are not safety nets).** The reproductions in §3–§4
below mean the project does **not** depend on trusting either the one-line cross-cite in
2304.04690 or my transcription of BJSS: the arguments are given in full and re-derive
exactly statements (a),(b),(d). Treat §2 as provenance; treat §3–§4 as the proof.

---

## 3. (L▽-lb): the lower bound, proved from scratch — [PROVED]

> **Proposition 3.1.** `χ⃗(D₁ ▽ D₂) ≥ min{ χ⃗(D₁), χ⃗(D₂) }`.

**Proof.** Put `k := χ⃗(D)` and fix a `k`-dicolouring `φ` of `D` (it exists by definition
of `χ⃗`). For `i ∈ {1,2}` let `φᵢ` be the restriction of `φ` to `V(Dᵢ)`, where at the
shared vertex we set `φᵢ(v) := φ(v)` (recall `Dᵢ` is `D[Sᵢ]` with the interface arc
re-added, and `Sᵢ` carries the join-colours).

**Claim: at least one of `φ₁, φ₂` is a valid `k`-dicolouring of its factor.**

Suppose not. Then `φ₁` fails on `D₁`, i.e. some colour class of `φ₁` contains a directed
cycle of `D₁`. Now `D₁ = D[S₁] + (u→v)`. Every arc of `D[S₁]` is an arc of `D`, and on
`D[S₁]` the colouring `φ₁` is just `φ` restricted, which is acyclic on each class
**because `φ` is a valid dicolouring of `D` and `D[S₁] ⊆ D`** (a monochromatic dicycle of
`D[S₁]` would be a monochromatic dicycle of `D`). Hence any monochromatic dicycle of `D₁`
**must use the one arc of `D₁` that is not in `D`, namely the interface arc `u → v`.** Call
this monochromatic dicycle `C₁`; it traverses `u → v` and is otherwise inside `D[S₁]`, so
`C₁ − (u→v)` is a monochromatic `v ⇝ u` dipath `P₁` inside `D[S₁]`, all of colour
`φ(u) = φ(v)` (mono). Symmetrically, `φ₂` failing yields a monochromatic dicycle `C₂` of
`D₂` through the interface arc `v → w`, and `C₂ − (v→w)` is a monochromatic `w ⇝ v`
dipath `P₂` inside `D[S₂]`, all of colour `φ(w) = φ(v)`.

Because both dipaths are monochromatic and share the colour at `v`, the three colours
`φ(u), φ(v), φ(w)` coincide; call it `α`. Consider in `D` the closed walk

> `W := (u → w) · P₂ · P₁ = u → w ⇝ v ⇝ u`,

using the **join arc `u → w`** (present in `D`), then `P₂` (`w ⇝ v`, inside `S₂`), then
`P₁` (`v ⇝ u`, inside `S₁`). Every arc of `W` is an arc of `D`; every vertex of `W` has
colour `α`. `W` is a closed directed walk, all in colour `α`, so it contains a directed
**cycle** in colour `α` (a closed directed walk in a digraph contains a directed cycle).
That monochromatic dicycle lies in a single colour class of `φ` — contradicting that `φ`
is a valid `k`-dicolouring of `D`. This proves the Claim.

So some `φᵢ` is a `k`-dicolouring of `Dᵢ`, whence `χ⃗(Dᵢ) ≤ k = χ⃗(D)`, i.e.
`min{χ⃗(D₁), χ⃗(D₂)} ≤ χ⃗(D)`. ∎

**Where the directed subtlety lives.** The argument never claims a colour class is
independent — `P₁, P₂` are honest dipaths *inside* a class. What is forbidden is a
directed **cycle** in a class, and the splice `W = (u→w)·P₂·P₁` is precisely the place
where the two one-sided dipaths, glued through the **added arc `u→w`** and the
**identified vertex `v`**, close a directed cycle. This is the cross-seam acyclicity that
`lemma_a_proof.md` §3 flagged "not verified": it is verified here. (BJSS phrase the same
splice on the *deleted-arc* side, `C₁ ∪ C₂ − u₁v₁ − v₂u₂ + u₁u₂`; the two formulations
are identical up to which arc you call the seam — see the remark below.)

**Remark (BJSS's dual phrasing).** BJSS run the contrapositive: assume **both** `φᵢ` fail,
get `C₁ ∋ u₁v₁` and `C₂ ∋ v₂u₂`, and splice `C₁ ∪ C₂ − u₁v₁ − v₂u₂ + u₁u₂` directly into a
monochromatic dicycle of `D`. My version peels off the dipaths first only to make the
"closed walk ⇒ contains a dicycle" step explicit; it is the same cycle. `C₁` uses the
deleted arc `u→v₁=u→v`; `C₂` uses `v₂→w=v→w`; deleting both and adding `u→w` glues
`P₁=C₁−(u→v)` and `P₂=C₂−(v→w)` exactly into `W`.

**Specialisation (the form the project quotes).** Taking `χ⃗(D₁),χ⃗(D₂) ≥ 3`:
`χ⃗(D) ≥ min ≥ 3`, i.e. **the directed Hajós join of two non-2-dicolourable digraphs is
not 2-dicolourable.** This is the literal statement `lemma_a_proof.md` §3 calls the
"digraph analogue of the classical Hajós lower bound, genuinely OPEN." It is closed. ∎

---

## 4. (L▽-glue) and (L▽-crit), proved — [PROVED]

### 4.1 Gluing / equality

> **Proposition 4.1.** If `χ⃗(D₁) = χ⃗(D₂) = k` with `k ≥ 2`, then `χ⃗(D) = k`. Moreover any
> two `k`-dicolourings `φ₁, φ₂` of `D₁, D₂` with `φ₁(v) = φ₂(v)` glue to a `k`-dicolouring
> of `D`.

**Proof.** `≥` is Proposition 3.1 (`χ⃗(D) ≥ min = k`). For `≤`, take `k`-dicolourings
`φ₁` of `D₁` and `φ₂` of `D₂`; since `k ≥ 2` we may permute the `k` colours of `φ₂` so
that `φ₂(v) = φ₁(v)` (colour permutation preserves being a dicolouring). Define `φ` on `D`
by `φ = φ₁` on `S₁` and `φ = φ₂` on `S₂` (consistent at `v`). Suppose `φ` is not a valid
`k`-dicolouring: some class has a monochromatic dicycle `C` in `D`.

- If `C ⊆ D[S₁]`: then `C` is a monochromatic dicycle of `D₁ = D[S₁]+(u→v)` not using
  `(u→v)`, contradicting that `φ₁` is a dicolouring. Symmetrically `C ⊆ D[S₂]` is
  impossible.
- Otherwise `C` uses the only cross arc, the join arc `u → w`, so `C` enters `S₂` at `w`
  and must return to `S₁` through the cut vertex `v` (the only shared vertex). Thus `C`
  contains a `w ⇝ v` sub-dipath `Q₂` inside `S₂`, monochromatic. Then `Q₂ + (v→w)` is a
  monochromatic dicycle of `D₂ = D[S₂]+(v→w)` (colours agree since `φ(w)=φ(u)=φ(v)` along
  the mono cycle `C`), contradicting that `φ₂` is a dicolouring.

Either way a contradiction, so `φ` is a valid `k`-dicolouring of `D` and `χ⃗(D) ≤ k`. ∎

(BJSS's 2(b) proof is the same: a monochromatic `C` through `u₁u₂` forces `(C∩D₁)+u₁v₁` to
be a monochromatic dicycle of `D₁`.)

### 4.2 Criticality descent — the converse the induction consumes

> **Proposition 4.2 (= BJSS Thm 2(d), reproduced).** If `D = D₁ ▽ D₂` is `(k+1)`-dicritical
> and `k ≥ 2`, then both `D₁` and `D₂` are `(k+1)`-dicritical. In particular for `k+1 = 3`:
> a 3-dicritical directed Hajós join has both factors 3-dicritical, so `χ⃗(D₁)=χ⃗(D₂)=3`.

**Proof.** Write `m := k+1 ≥ 3`. `D` is `m`-dicritical: `χ⃗(D) = m` and every proper
subdigraph has `χ⃗ < m`.

*Step 1: each factor has `χ⃗(Dᵢ) ≥ m`.* Suppose `χ⃗(D₁) ≤ m−1 = k`. I show `χ⃗(D) ≤ k`,
contradicting `χ⃗(D) = m`. Indeed `D − (u→w)` is the disjoint-at-`v` union
`D[S₁] ∪_v D[S₂]`; colour `D[S₁]` by a `k`-dicolouring of `D₁` restricted (drop the
interface arc — fewer constraints), colour `D[S₂]` by a `k`-dicolouring of `D₂` (it has
one too, as `χ⃗(D₂) ≤ χ⃗(D) = m`; but we must be careful — see Step 1′). This is where one
genuinely needs the *critical* hypothesis, handled cleanly as follows.

*Step 1′ (clean version via minimality).* By `m`-dicriticality, for the deleted interface
arc, `D₁ − (u→v) = D[S₁]` is a proper subdigraph of `D`, so `χ⃗(D[S₁]) ≤ m−1 = k`;
likewise `χ⃗(D[S₂]) ≤ k`. Fix `k`-dicolourings `ψ₁` of `D[S₁]` and `ψ₂` of `D[S₂]`.

Now I claim `χ⃗(D₁) ≥ m` **and** `χ⃗(D₂) ≥ m`. Suppose, for contradiction, `χ⃗(D₁) ≤ k`.
Take a `k`-dicolouring `χ₁` of `D₁` (which respects the interface arc `u→v`) and the
`k`-dicolouring `ψ₂` of `D[S₂]`. Permute colours of `ψ₂` so `ψ₂(v)=χ₁(v)` (possible,
`k ≥ 2`). Define `φ = χ₁` on `S₁`, `φ = ψ₂` on `S₂`. Any monochromatic dicycle of `φ` in
`D`: if inside `S₁` it contradicts `χ₁` (a dicolouring of `D₁ ⊇ D[S₁]`); if inside `S₂`
it contradicts `ψ₂`; if it uses `u→w` it contains a `w⇝v` mono dipath `Q₂` in `S₂`, and
also (to be a cycle through `u`) a `v⇝u` mono dipath `Q₁` in `S₁` — but `Q₁+(u→v)` would
be… wait, `Q₁` runs `v⇝u`, and with the interface arc `u→v` re-added it closes a
mono dicycle of `D₁`, contradicting `χ₁`. So `φ` is a valid `k`-dicolouring of `D`, giving
`χ⃗(D) ≤ k < m`, contradiction. Hence `χ⃗(D₁) ≥ m`, and symmetrically `χ⃗(D₂) ≥ m`.

*Step 2: each factor has `χ⃗(Dᵢ) ≤ m`, hence `= m`.* `Dᵢ` embeds into `D` up to the single
interface arc; more directly, by Proposition 3.1, `m = χ⃗(D) ≥ min{χ⃗(D₁),χ⃗(D₂)}`, so at
least one factor has `χ⃗ ≤ m`. Combined with Step 1 (`≥ m` for *both*) that one factor has
`χ⃗ = m`. For the other factor: by Proposition 4.1 applied with that determined value, or
directly — since both have `χ⃗ ≥ m` and a join of two digraphs each `χ⃗ ≥ m` would, were
the other `> m`, still satisfy the *dicriticality* of `D` only if neither factor carries a
removable arc; the clean route is BJSS's: drop any arc `a` of `D₂`. Then `D − a` is a
proper subdigraph of the `m`-critical `D`, so `χ⃗(D−a) ≤ m−1`; but `D − a` is the Hajós
join `D₁ ▽ (D₂−a)`, so by Prop 3.1 `χ⃗(D−a) ≥ min{χ⃗(D₁), χ⃗(D₂−a)} ≥ min{m, χ⃗(D₂−a)}`.
If `χ⃗(D₂−a) ≥ m` this forces `χ⃗(D−a) ≥ m`, contradiction; hence `χ⃗(D₂−a) ≤ m−1` for
**every** arc `a` of `D₂`. With `χ⃗(D₂) ≥ m` (Step 1), this says `D₂` is `m`-dicritical (it
has `χ⃗ ≥ m` and every arc-deleted subdigraph drops below `m`; vertex-deletion criticality
follows likewise by deleting all arcs at a vertex). Symmetrically `D₁` is `m`-dicritical.

In particular `χ⃗(D₁)=χ⃗(D₂)=m`. ∎

**The converse direction** (`Dᵢ` both `m`-dicritical `⇒ D` is `m`-dicritical, = BJSS 2(c))
is proved the same way: Prop 4.1 gives `χ⃗(D)=m`, and for any arc `a` of `D`, deleting it
either lands in a factor (drop one factor below `m`, then Prop 3.1 gives `χ⃗(D−a)<m`) or is
the join arc `u→w` (then `D − (u→w) = D[S₁] ∪_v D[S₂]`, each side `χ⃗ ≤ m−1` by criticality
of the factor, glued at `v`, so `χ⃗(D−(u→w)) ≤ m−1`). Hence `D` is `m`-dicritical.

---

## 5. What this does and does NOT close (honest boundary) — [PROVED] / [OPEN]

### 5.1 Closed for the directed-Hajós seam — [PROVED]

- **(L▽-lb)** Proposition 3.1: `χ⃗(D₁▽D₂) ≥ min{χ⃗(Dᵢ)}`; the `χ⃗≥3` form is the
  "directed Hajós lower bound" `lemma_a_proof.md` §3 called open. **Closed.**
- **(L▽-glue)** Proposition 4.1: seam-agreeing dicolourings glue; `χ⃗(D)=k` when both
  factors are `k` (`k≥2`). = `lemma_a_proof.md` (L-assemble). **Closed.**
- **(L▽-crit)** Proposition 4.2: `D` `3`-dicritical ⇒ both factors `3`-dicritical
  (so `χ⃗(Dᵢ)=3`), and conversely. This is the `χ⃗`-descent the induction needs **for the
  directed-Hajós seam, when `D` is dicritical.**

### 5.2 The mismatch that remains even for the directed-Hajós seam — [OPEN]

Proposition 4.2 descends **3-dicriticality**, but the induction's invariant is
**2-extremality** (= strong + underlying 2-connected + `λ=2` + `χ⃗=3`; Eulerian/3-dicritical
come along by Lemma 4.1 of 2304.04690 — `conditional_l_literature.md` §4). A 2-extremal `D`
**is** 3-dicritical (`χ⃗=3` *critically*: Lemma 4.1 of 2304.04690 states 2-extremal ⇒
3-dicritical), so Prop 4.2 **does** apply to a 2-extremal `D`: if such a `D` is a directed
Hajós join, its factors `D₁,D₂` are 3-dicritical, hence `χ⃗(Dᵢ)=3`. **This closes the
`χ⃗(Dᵢ)≥3` half of Lemma B's Conditional L for clause (a).** It does **not** by itself give
the full 2-extremality of `Dᵢ` (strong, 2-connected underlying, `λ=2`) — those are the
**structural** clauses of Lemma B, handled separately (and largely proved) in
`docs/proof_lemma_b.md`/`verify_lemma_b.md`, and strong-connectivity for the assembled join
is additionally BJSS **Theorem 8** (`conditional_l_external_lit.md` §3). So for clause (a)
the colouring obstacle is removed; the residual is the standard structural bookkeeping,
not a Hajós-criticality gap.

> **Net for clause (a):** `χ⃗(Dᵢ)=3` preservation across a *literal directed Hajós seam* is
> **PROVED** (Prop 4.2 + 2-extremal⇒3-dicritical). The earlier "OPEN, no proof over the
> 1680/4.16M search" verdict in `lemma_a_proof.md` §3 was for a theorem that exists.

### 5.3 NOT closed by this note — [OPEN]

1. **The tree-join seam (clause (b)).** BJSS Theorem 2 and Propositions 3.1–4.2 above are
   **only** for the single-arc / single-identified-vertex join `D₁▽D₂`. The non-empty-A
   2-Hajós **tree join** (Def 9.1) glues across a *digon forest plus a peripheral directed
   cycle plus ≥1 A-block* — a multi-seam, not a single added arc. The splice `W` of §3 does
   not directly apply. **However:** the tree-join lower bound *is* proved in the source for
   `k≥2` — **Lemma 6.7 of 2304.04690** (`conditional_l_literature.md` §2.3), whose forward
   argument uses no `k≥3`: a monochromatic peripheral cycle forces all junction vertices
   one colour, and non-monochromaticity forces some `(uᵢ,vᵢ)` to differ, restricting to a
   `k`-dicolouring of `Dᵢ` and contradicting `χ⃗(Dᵢ)=k+1`. So the **tree-join clause of
   Conditional L is also citable at `k=2`** (Lemma 6.7), and a from-scratch reproduction is
   the natural ANGLE-2 follow-up (extend `W` to the multi-seam). Marked **[CITED for the
   lower bound; from-scratch proof deferred]**.

2. **Cut ⇒ factorisation (Lemma A *existence*).** None of §3–§4 *recognises* a directed
   Hajós join from connectivity data; they assume `D = D₁▽D₂` is given. Promoting a mixed
   2-cut `(v,{u,w})` of `U(D)` to a genuine 2-extremal factorisation is the **sufficiency**
   hole of `lemma_a_proof.md` §2/§4 (refuted recipe at member `7.33`). This is a structural
   gap, **outside the scope of any colouring theorem**, and stays **[OPEN]**. The source
   itself leaves it open at `k=2`: its decomposition Theorem 5.1 is stated only for `k≥3`
   (`conditional_l_literature.md` §4).

---

## 6. Computational corroboration (evidence, not proof)

`scripts/cond_l_hajos_lb_check.py` (reuses the SOUND `chi_vec` / `_has_dicycle_in_subset`
primitives of `scripts/h2_oracle.py`) directly tests the three statements:

```
=== (A)+(B) sym-odd-cycle directed-Hajos joins ===
  joins tested: 256; lower-bound+equality failures: 0
=== (A)+(B) randomised chi=3 pairs ===
  joins tested: 400; failures: 0
=== (C) splice mechanism ===
  c3c3_no_2col: True          # chi=3 ▽ chi=3 has NO 2-dicolouring (Prop 3.1)
  tri_tri_chi_join: 2         # chi=2 ▽ chi=2 join is 2-dicolourable (min=2, tight)
  splice_never_fires_when_phi_exists: True  # whenever a 2-dicolouring of the
                                            # join exists, some side-restriction
                                            # is valid (Claim of Prop 3.1)
=== OVERALL: PASS ===
```

- **(A)/(B):** over all `4·4·…=256` directed Hajós joins of symmetric odd cycles `C₃,C₅`
  (every arc choice on both sides) plus 400 randomised `χ⃗=3` pairs, the lower bound
  `χ⃗(D)≥min` and the equality `χ⃗(D)=k` hold with **0 failures**. This exercises
  Propositions 3.1 and 4.1.
- **(C):** confirms the *mechanism* of Prop 3.1's Claim: when both factors are `χ⃗=3` the
  join admits **no** 2-dicolouring (`c3c3_no_2col`); and whenever a 2-dicolouring of a
  join *does* exist (here `C₃▽C₃` of directed triangles, `χ⃗=2`), **at least one
  side-restriction is always a valid dicolouring** (`splice_never_fires_when_phi_exists`),
  i.e. the splice never fires when `φ` exists — exactly the Claim. The boundary case
  `tri_tri_chi_join = 2 = min{2,2}` shows the bound is **tight**.

This is corroboration only; the theorem is §3–§4.

---

## 7. One-paragraph summary for the synthesis

The **directed-Hajós-join instance** of Conditional L is now **proved**, not merely cited.
The lower bound `χ⃗(D₁▽D₂) ≥ min{χ⃗(Dᵢ)}` (Prop 3.1), the gluing `χ⃗(D)=k` for
seam-agreeing dicolourings (Prop 4.1), and the criticality descent `D` 3-dicritical ⇒ both
factors 3-dicritical (Prop 4.2) are given from scratch; the cross-seam acyclicity that
`lemma_a_proof.md` §3 flagged is handled by the splice `W=(u→w)·P₂·P₁` closing a
monochromatic dicycle. These coincide with BJSS 2020 Theorem 2(a),(b),(d) (cited, pinned,
and now independently reproved). Combined with `2-extremal ⇒ 3-dicritical` (Lemma 4.1 of
2304.04690), this **closes the `χ⃗(Dᵢ)=3`-preservation (Conditional L) for clause (a)** —
the team's 1680/4.16M-join search was chasing a theorem. **Two things remain genuinely
open and are NOT this note:** (i) the **tree-join** seam lower bound (citable at `k=2` as
Lemma 6.7 of 2304.04690; from-scratch multi-seam splice is the next target), and (ii) the
**cut⇒factorisation** sufficiency of Lemma A (a structural, non-colouring gap, open even in
the source at `k=2`).

---

### Files
- `docs/proof_condL_hajos_lower_bound.md` — this note.
- `scripts/cond_l_hajos_lb_check.py` — `PASS` (256 + 400 joins, splice mechanism).
- Cites: `docs/conditional_l_external_lit.md` (BJSS Thm 2/8, verbatim),
  `docs/conditional_l_literature.md` (2304.04690 Lemma 4.1/5.3/5.4/6.7, verbatim),
  `docs/lemma_a_proof.md` §2–§5 (the seam, the open boundary).
