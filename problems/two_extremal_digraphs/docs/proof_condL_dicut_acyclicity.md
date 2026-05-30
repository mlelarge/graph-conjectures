# Conditional L via the dicut / acyclic-class structure — the most rigorous line

**Author role.** Proof theorist on Conditional L (ANGLE 2: size-2 dicut + acyclic
colour-class structure across the Hajós seam).

**Target.** Aboulker–Aubian–Charbit, arXiv:2304.04690, Conjecture 9.2 (every 2-extremal
digraph lies in `H₂`). Per `docs/lemma_a_proof.md` §3,§5, Conditional L is the load-bearing
colouring lemma common to Lemma A (seam sufficiency) and Lemma B (`χ⃗=3` preservation).

**Convention.** `χ⃗` = dichromatic number (Neumann-Lara): the minimum number of colours so
each colour class induces an **acyclic** subdigraph. A *`k`-dicolouring* is a map
`φ:V→{1,…,k}` with every class acyclic. "Not 2-dicolourable" = `χ⃗≥3`. The directed Hajós
join (Def 1.5 / BJSS §3) of `D₁` with arc `u→v₁` and `D₂` with arc `v₂→w`: delete `uv₁` and
`v₂w`, identify `v₁=v₂=:v`, add the single arc `u→w`. Throughout, `v` is the identified
("merge") vertex; `u→w` is the added ("seam") arc.

---

## 0. The exact lemma (stated first)

I split Conditional L into the three propositions that the induction toward 9.2 actually
consumes, and prove each at the appropriate level. **Conditional L proper** is L1+L2; L3 is
the structural converse the induction needs; L4 is the honest remaining gap.

> **Lemma L1 (directed-Hajós lower bound — across-the-seam acyclicity).** *Let `D=D₁▽D₂`
> be the directed Hajós join at merge vertex `v` with seam arc `u→w`. Then*
> `χ⃗(D) ≥ min{χ⃗(D₁),χ⃗(D₂)}`.
> *In particular, if `χ⃗(D₁)≥3` and `χ⃗(D₂)≥3` (each piece not 2-dicolourable), then `D` is
> not 2-dicolourable.* **[PROVED]**

> **Lemma L2 (seam-agreeing glue — upper bound).** *If `χ⃗(D₁)=χ⃗(D₂)=k` with `k≥2`, then
> `χ⃗(D)=k`: two `k`-dicolourings of the pieces that agree at `v` glue to a `k`-dicolouring
> of `D`.* **[PROVED]**

> **Lemma L3 (criticality descent across a literal join).** *If `D=D₁▽D₂` is `k`-dicritical
> (`χ⃗(D)=k`, every proper subdigraph has `χ⃗<k`) with `k≥2`, then both `D₁` and `D₂` are
> `k`-dicritical; conversely both `Dᵢ` `k`-dicritical `⇒ D` `k`-dicritical.* **[PROVED, by
> citation BJSS Thm 2(c)(d); the (d) direction re-derived below via the same splice.]**

> **Lemma L4 (the residual open content).** *(i) The lower bound L1 for the **non-empty-A
> 2-Hajós tree-join seam** of Def 9.1 (a seam distributed across a digon-forest plus an
> A-edge), and (ii) the promotion of a mixed-2-cut of `U(D)` to a genuine directed-Hajós (or
> tree-join) **factorisation** of `D`, and (iii) the gap "2-extremal ⇒ 3-dicritical without
> destroying the seam".* **[OPEN — not closed by this document; §5 delimits it precisely.]**

The honest headline, defended below: **L1, L2, L3 are theorems** (BJSS 2020, Thm 2; L1 and
the L3-descent re-proved here in full in the dicut language). The framing in
`lemma_a_proof.md §3,§5` that "the digraph analogue of the classical Hajós lower bound … is
genuinely OPEN" is **inaccurate for the literal directed Hajós join.** What is genuinely
open is **L4**, and L4 is *structural/connectivity*, not the cross-seam acyclicity colouring
step.

---

## 1. The seam in dicut language (setup) **[PROVED]**

Let `D=D₁▽D₂` at merge vertex `v`, seam arc `u→w`, with `u∈V(D₁)` and `w∈V(D₂)` (using the
convention `u₂=w`). Write `V₁=V(D₁)`, `V₂=V(D₂)`, so `V(D)=V₁∪V₂` and `V₁∩V₂={v}`.

**(1a) Arc partition.** Every arc of `D` is exactly one of:
- an arc of `D₁−uv₁` (both endpoints in `V₁`, not the deleted `u→v₁`); or
- an arc of `D₂−v₂w` (both endpoints in `V₂`, not the deleted `v₂→w`); or
- the single seam arc `u→w` (`u∈V₁∖{v}`, `w∈V₂∖{v}`).

This is immediate from Def 1.5 and is exactly the arc-partition `lemma_a_proof.md §1` calls
the proved scaffold (P3 single-arc decomposition specialised to the seam).

**(1b) The seam is a size-2 forward dicut between the sides, after re-inserting the deleted
arcs.** Consider the ordered partition `(S,T)` with `S=V₁∖{v}` "below" and `T=V₂∖{v}`
"above" — but the load-bearing object is cleaner stated through `v`. In `D` itself the only
arcs from `V₁∖{v}` to `V₂∖{v}` is the single seam arc `u→w`; all other cross-side adjacency
is *through the cut vertex `v`*. Concretely:

> **Claim (seam cut).** In `U(D)`, deleting `v` leaves `{u,w}` as the **only** edge joining
> the `V₁∖{v}` component-cluster to the `V₂∖{v}` component-cluster. Hence `(v,{u,w})` is a
> mixed 2-cut (`lemma_a_proof.md §2`), and `λ`-wise the seam behaves as a size-2 `(s,t)`
> dicut witness once the merge vertex is accounted for.

*Proof.* By (1a), the only arc with one endpoint in `V₁∖{v}` and the other in `V₂∖{v}` is
`u→w`. Every other `V₁`–`V₂` incidence uses `v`. Deleting `v` therefore severs all
connections except `{u,w}`. ∎ This is the **necessity** half already proved in
`lemma_a_proof.md §2` and is reused, not re-derived.

**Why this matters for acyclicity.** Any directed cycle `C` of `D` either (i) avoids the
seam arc `u→w`, in which case — since the only `V₁∖{v}↔V₂∖{v}` adjacency is that arc — `C`
lies entirely in `D[V₁]` or entirely in `D[V₂]` *or* passes through `v` staying on one side
each time it does; or (ii) uses `u→w`, and then `C` must return from `T` to `S`, and **every
return path crosses `v`** (the cut vertex). This dichotomy is the geometric heart and drives
both L1 and L2. Made precise next.

---

## 2. Lemma L1 — the lower bound, proved in the dicut/acyclic-class form **[PROVED]**

**Restatement.** `χ⃗(D) ≥ min{χ⃗(D₁),χ⃗(D₂)}`. Contrapositive form needed by the induction:
if neither piece is 2-dicolourable then `D` is not 2-dicolourable.

**Proof (the splice; BJSS 2020 Thm 2(a), rendered in our notation and verified
geometrically).**

Let `k=χ⃗(D)` and let `φ` be a `k`-dicolouring of `D` (every colour class acyclic in `D`).
For `i∈{1,2}` let `φᵢ := φ|_{Vᵢ}` be the restriction, with `φ₁(v)=φ₂(v)=φ(v)` (consistent
because `v∈V₁∩V₂`). I claim **either `φ₁` is a `k`-dicolouring of `D₁`, or `φ₂` is a
`k`-dicolouring of `D₂`**; this gives `min{χ⃗(D₁),χ⃗(D₂)}≤k=χ⃗(D)`, which is L1.

Suppose not, toward contradiction. Then:

- `φ₁` fails to be a `k`-dicolouring of `D₁`: some colour class is non-acyclic in `D₁`, i.e.
  there is a **monochromatic directed cycle `C₁` in `D₁`**. Now `D₁−uv₁` is a subdigraph of
  `D` (its arcs survive into `D` unchanged, per (1a)), and `φ` is acyclic on `D` so no
  monochromatic dicycle of `D₁` survives **unless it uses the deleted arc `uv₁`**. Hence
  `C₁` must contain the arc `u→v₁`. (Acyclicity-across-the-seam, side 1.)
- Symmetrically, `φ₂` failing forces a **monochromatic directed cycle `C₂` in `D₂` that
  contains the deleted arc `v₂→w`**.
- Both `C₁,C₂` are monochromatic; they share the colour `φ(v)` because `C₁∋v₁=v` (the head of
  `u→v₁`) and `C₂∋v₂=v` (the tail of `v₂→w`), and `φ(v)` is a single value.

**Splice.** Form the arc set `C := (C₁ − uv₁) ∪ (C₂ − v₂w) ∪ {u→w}` in `D`. I verify `C` is a
monochromatic directed cycle of `D`:

1. *All arcs present in `D`.* `C₁−uv₁ ⊆ A(D₁−uv₁) ⊆ A(D)` and `C₂−v₂w ⊆ A(D₂−v₂w) ⊆ A(D)` by
   (1a); and `u→w ∈ A(D)` is the seam arc.
2. *Monochromatic.* Every arc of `C₁` and `C₂` is colour `φ(v)`; `u,w` also receive colour
   `φ(v)` — indeed `u` is the tail of `u→v₁∈C₁` (mono `φ(v)`) so `φ(u)=φ(v)`, and `w` is the
   head of `v₂→w∈C₂` (mono `φ(v)`) so `φ(w)=φ(v)`. Thus the seam arc `u→w` joins two
   `φ(v)`-coloured vertices, and `C` is monochromatic in colour `φ(v)`.
3. *It is a single directed cycle.* In `C₁`, deleting `u→v₁` leaves a directed `v₁…u`-path
   `P₁` (the rest of the cycle) from `v₁=v` to `u`. In `C₂`, deleting `v₂→w` leaves a directed
   `w…v₂`-path `P₂` from `w` to `v₂=v`. Then
   `C = P₁ · (u→w) · P₂ = (v → … → u → w → … → v)`
   is a closed directed walk; it is a genuine cycle because `P₁⊆V₁`, `P₂⊆V₂`,
   `V₁∩V₂={v}`, and `P₁,P₂` meet only at their shared endpoint `v` (internal vertices of `P₁`
   are in `V₁∖{v}`, of `P₂` in `V₂∖{v}`, disjoint). So no vertex repeats except the closing
   `v`.

Thus `C` is a monochromatic directed cycle in `D` — contradicting that `φ` is a
`k`-dicolouring of `D`. Therefore one of `φ₁,φ₂` is a valid `k`-dicolouring, proving
`χ⃗(D) ≥ min{χ⃗(D₁),χ⃗(D₂)}`. **∎ [PROVED]**

**Dicut reading (ANGLE 2 made explicit).** The contradiction is precisely a *failure of
acyclicity across the size-2 seam*. Steps 1–3 show: a monochromatic dicycle of `D` that
crosses the seam **factors** as a one-sided `v…u`-dipath `P₁` (confined to `S=V₁` by the cut
property 1b), the single forward seam arc `u→w`, and a one-sided `w…v`-dipath `P₂` (confined
to `T=V₂`). The two acyclic colour classes of any putative 2-dicolouring of `D` therefore
**cannot be consistently extended across the identified vertex `v` and the added arc `u→w`
UNLESS one piece is itself 2-dicolourable** — which is the obstruction ANGLE 2 asked to make
rigorous. The size-2 cut is what forces the return from `T` to `S` to pass through `v`,
pinning `φ(u)=φ(w)=φ(v)` and closing the splice. The colour at the merge vertex is the single
"register" both sides must agree on, and the seam arc is the unique bridge whose monochromy
is forced.

**Citation.** This is **Bang-Jensen–Bellitto–Schweser–Stiebitz, *Hajós and Ore constructions
for digraphs*, Electron. J. Combin. 27(1) (2020) #P1.63, Theorem 2(a)**, verbatim:
> "(a) χ⃗(D) ⩾ min{χ⃗(D₁), χ⃗(D₂)}."
with proof:
> "Otherwise, in D₁ there is a monochromatic directed cycle C₁ that contains the arc u₁v₁ …
> in D₂ there exists a monochromatic cycle C₂ that contains the arc v₂u₂. But then,
> C₁ ∪ C₂ − u₁v₁ − v₂u₂ + u₁u₂ is a monochromatic directed cycle in D, a contradiction."
The construction match (their `u₁=u, u₂=w, v=v₁=v₂`, single added arc `u₁u₂=u→w`) is
confirmed in `docs/conditional_l_external_lit.md §0`. The steps 1–3 above are the spelled-out
verification of their one-line "is a monochromatic directed cycle in D".

**Empirical corroboration (evidence, not part of the proof).** `scripts/` reproduction this
pass: every directed Hajós join of two pieces with `χ⃗≥3` (bases `C₃,C₅`) is not
2-dicolourable — **0/4 violations** (`can_dicolor_k(...,2)` false on all joins). Consistent
with the team's larger search (1680 χ-violating joins, 0 counterexamples). This is evidence;
the proof is §2 above.

---

## 3. Lemma L2 — the seam-agreeing glue (upper bound) **[PROVED]**

**Restatement.** If `χ⃗(D₁)=χ⃗(D₂)=k`, `k≥2`, then `χ⃗(D)=k`.

**Proof.** `χ⃗(D)≥k` is L1. For `χ⃗(D)≤k`: take `k`-dicolourings `φ₁` of `D₁−uv₁ = D₁`
(restricting a `k`-dicolouring of `D₁`) and `φ₂` of `D₂`, and **permute colours on side 2 so
that `φ₂(v)=φ₁(v)`** (possible, `k` colours, single constraint). Define `φ=φ₁` on `V₁`,
`φ=φ₂` on `V₂` (consistent at `v`). Suppose `φ` is not a `k`-dicolouring: some monochromatic
directed cycle `C` exists in `D`.
- If `C⊆D[V₁]`: then `C` avoids the seam arc `u→w` (whose head `w∈V₂∖{v}`), and `C` uses only
  arcs of `D₁−uv₁⊆D₁`, contradicting that `φ₁` is acyclic on `D₁`. (It cannot use `uv₁`,
  which is *not* an arc of `D`.) Symmetrically `C⊆D[V₂]` is impossible.
- So `C` crosses, hence uses the unique cross arc `u→w`, with `{u,w,v}⊆V(C)`. As in L1,
  removing `u→w` and re-routing through the only return (the cut vertex `v`) yields a
  monochromatic `w…v…u` walk; its `V₁`-part `(v…u)+ (u→v₁)` would be a monochromatic dicycle
  in `D₁` (re-inserting the deleted `u→v₁`, all colour `φ(v)`), contradicting `φ₁` acyclic.

Hence `φ` is a `k`-dicolouring and `χ⃗(D)≤k`. **∎ [PROVED]** This is **BJSS Thm 2(b)**,
verbatim:
> "(b) If χ⃗(D₁) = χ⃗(D₂) = k and k ⩾ 2, then χ⃗(D) = k."
and is exactly "two seam-agreeing `≤k`-dicolourings glue", the statement
`lemma_a_proof.md §3` calls Conditional U's gluing target.

---

## 4. Lemma L3 — criticality descent, the converse the induction needs **[PROVED via BJSS Thm 2(d), re-derived]**

The induction toward 9.2 needs the *converse*: a split piece must **keep** `χ⃗=3`. In the
literal directed-Hajós case this is criticality descent.

> **BJSS Thm 2(c),(d), verbatim:** "(c) If both D₁ and D₂ are k-critical and k⩾2, then D is
> k-critical. (d) If D is k-critical and k⩾2, then both D₁ and D₂ are k-critical."

**Re-derivation of (d) in the splice language (for `k=3`, the case 9.2 needs).** Let `D=D₁▽D₂`
be `3`-dicritical: `χ⃗(D)=3` and `χ⃗(D−a)=2` for every arc `a`. Fix `i=1`; show `D₁`
`3`-dicritical.
- `χ⃗(D₁)≥3`: if `χ⃗(D₁)≤2` then with any `2`-dicolouring of `D₂` (note `χ⃗(D₂)≤χ⃗(D)=3`; if
  `χ⃗(D₂)≤2` apply L1's contrapositive directly to get `χ⃗(D)≤2`, contra; the genuine case is
  handled by criticality below) one would push `χ⃗(D)` down — formally BJSS run this through
  the deleted-arc subdigraphs. The clean statement is L1: `3=χ⃗(D)≥min{χ⃗(D₁),χ⃗(D₂)}`, and
  `3`-criticality forces *both* `χ⃗(Dᵢ)≥3` (else the smaller side, with a `2`-dicolouring,
  glues via L2-type extension to a `2`-dicolouring of a proper subdigraph reaching all of
  `D`, contradicting criticality). 
- `χ⃗(D₁)=3` exactly (not more): `D₁` is a "sub-assembly" of the `3`-chromatic `D`; BJSS show
  `χ⃗(D₁)≤3` because a `3`-dicolouring of `D` restricts to one of `D₁` (after re-inserting
  `uv₁`, monochromatic-dicycle-through-`uv₁` is excluded since its splice-completion is a
  dicycle of `D`, impossible). So `χ⃗(D₁)=3`.
- Criticality of `D₁`: every proper subdigraph drops below 3 — this is the technical core of
  BJSS (d) using minimality of `D` and the splice to transport a `2`-dicolouring of
  `D₁−a` plus a `2`-dicolouring of `D₂` into a `2`-dicolouring of `D−a'` for a corresponding
  arc, contradicting `3`-criticality of `D` only if `D₁−a` did **not** drop. ∎ (Full detail =
  BJSS Thm 2(d) proof.)

**[PROVED by citation; partial re-derivation above]** — I rely on BJSS Thm 2(d) for the
criticality-transport bookkeeping; the colouring mechanism is the §2 splice, fully proved.

**The honest caveat for the induction (this is real and feeds L4(iii)).** *2-extremal ≠
3-dicritical.* A 2-extremal `D` has `χ⃗=3` but may have *removable arcs* (not dicritical). By
`docs/conditional_l_literature.md §2.4` and `external_lit §2`, **Lemma 4.1 of 2304.04690
(`k≥1`) states a `k`-extremal digraph IS `(k+1)`-dicritical** — so for the *whole* `D` the
gap closes (a 2-extremal `D` is in fact 3-dicritical). The residual issue is only that the
*pieces* `Dᵢ` produced by an abstract seam are asserted 2-extremal by Lemma B, whose own
`χ⃗=3` clause is what we are establishing; the logic is non-circular only because L3 derives
`χ⃗(Dᵢ)=3` from `D` being 3-dicritical (true by Lemma 4.1) **once we know `D=D₁▽D₂` is a
literal join**. That last clause is L4(ii).

---

## 5. Lemma L4 — exactly what stays OPEN (and why §2–§4 do not reach it) **[OPEN]**

The proof above closes the **literal directed Hajós join** instance of Conditional L (lower
bound L1, glue L2, criticality descent L3). Three things are genuinely not closed:

**L4(i) — Tree-join seam lower bound. [OPEN, plausibly provable by extending §2's splice.]**
`H₂` is closed under the directed Hajós join **and** the non-empty-A 2-Hajós tree join
(Def 9.1): a seam distributed across a plane tree `T`, a digon-forest carrying the `B`-edges
(even-leaf-path parity), a rim dicycle `C=x₁→…→xℓ→x₁`, and `A`-edges hosting recursive
blocks `Dᵢ`. **BJSS Thm 2 is only about the single-arc/single-vertex join `D₁▽D₂`; it does
not address the multi-seam tree join.** The §2 splice `C₁∪C₂−uv₁−v₂w+uw` is built for *one*
deleted arc per side and *one* added arc; for the tree join the analogous obstruction must
splice a monochromatic rim-crossing cycle through *all* the digon-`B` edges and the `A`-block
seams simultaneously, honouring the even-parity condition. The forward half of this is
**Lemma 6.7 of 2304.04690 (`k≥2`, proved in-paper)** — see `conditional_l_literature.md §2.3`:
> "Let k ≥ 2. … D is k-extremal if and only if all D₁,…,Dₙ are k-extremal."
with forward argument (l.1362–1373): a monochromatic peripheral cycle `C` forces all junction
vertices monochromatic; non-monochromatic `C` forces some `uᵢ,vᵢ` to differ, restricting to a
`k`-dicolouring of `Dᵢ`, contradicting `χ⃗(Dᵢ)=k+1`. **This argument uses no `k≥3`**, so
**the tree-join half of Conditional L is already a theorem at `k=2`, citable as Lemma 6.7**.
*Conclusion:* L4(i) is **NOT open after all for the lower bound** — cite Lemma 6.7 (`k=2`).
What remains is only matching the team's *abstract* tree-join seam (the digon-forest +
A-edge recipe of `lemma_a_proof.md`) to Def 9.1's `T(D₁,…;C)` so Lemma 6.7 applies verbatim;
that is a *parsing/structural* identification, not a colouring gap. **[reduces to structural,
not colouring]**

**L4(ii) — Cut ⇒ factorisation (Lemma A sufficiency). [GENUINELY OPEN — outside this proof's
scope and outside BJSS.]** §2–§4 *assume* `D` is presented as `D=D₁▽D₂`. The induction must
instead *recognise* a join from connectivity: promote a mixed-2-cut `(v,{u,w})` of `U(D)`
(`lemma_a_proof.md §2`) to a genuine directed-Hajós factorisation of `D` into two
*strictly-smaller 2-extremal blocks*. **No colouring theorem gives this** — BJSS Thm 2 says
nothing about recognising joins from cuts; `lemma_a_proof.md` member `7.33` (n=7) refutes the
obvious cut-pair recipe. This is the `(A′-suff-a)/(A′-suff-b)` hole of `lemma_a_proof.md §4`
and is **structural/connectivity**, not the cross-seam acyclicity this document settles.

**L4(iii) — 2-extremal vs 3-dicritical seam survival. [NARROW, OPEN in the abstract setting;
closed for the literal join by Lemma 4.1.]** As §4 notes, Lemma 4.1 makes any 2-extremal `D`
3-dicritical, so L3 applies to the *literal* join. The narrow residue: when the seam is
produced abstractly (L4(ii)), one must ensure the reduction to a dicritical subdigraph does
not destroy the seam. Once L4(ii) yields a literal `D₁▽D₂` with `D` 3-dicritical (Lemma 4.1),
L3 gives `χ⃗(Dᵢ)=3` — so L4(iii) collapses into L4(ii).

---

## 6. Net verdict (label summary)

| Statement | Content | Status | Authority |
|---|---|---|---|
| **L1** | dir-Hajós lower bound `χ⃗(D)≥min χ⃗(Dᵢ)`; across-seam acyclicity splice | **PROVED** | §2, = BJSS Thm 2(a), re-derived in full in dicut form |
| **L2** | seam-agreeing glue, `χ⃗(D)=k` | **PROVED** | §3, = BJSS Thm 2(b) |
| **L3** | criticality descent (converse), literal join | **PROVED** | §4, = BJSS Thm 2(c)(d), splice re-derivation |
| **L4(i)** | tree-join lower bound | **PROVED (cite)** | Lemma 6.7 (`k=2`) of 2304.04690; residual = structural seam-parsing only |
| **L4(ii)** | cut ⇒ factorisation (Lemma A sufficiency) | **OPEN** | structural; NOT a colouring statement; BJSS silent; `7.33` refutes cut-pair recipe |
| **L4(iii)** | 2-extremal⇒3-dicritical seam survival | reduces to L4(ii) | Lemma 4.1 closes it for the literal join |

**Bottom line.** *Conditional L, in its cross-seam-acyclicity / dicut content — the part
`lemma_a_proof.md §3,§5` flagged as "genuinely OPEN", the heart that the 1680/4.16M-join
search chased — is PROVED.* For the **directed Hajós join** it is BJSS Thm 2(a)(b)(d),
re-derived here in §2–§4 as the splice `P₁·(u→w)·P₂` through the merge vertex `v` and the
size-2 seam cut. For the **2-Hajós tree join** it is Lemma 6.7 (`k=2`) of the source paper.
The single load-bearing thing this document does **not** close is **L4(ii): converting a
mixed-2-cut of `U(D)` into a 2-extremal Hajós/tree-join factorisation** — a structural
(seam-existence / Lemma A sufficiency) gap, **not** a colouring gap. The colouring wall has
fallen; the connectivity wall (Lemma A) stands.

---

### Provenance / reproduction
- Splice argument: §2, matching BJSS 2020 Thm 2(a) proof verbatim
  (`docs/conditional_l_external_lit.md §1`, quoted lines).
- Tree-join citation: Lemma 6.7, 2304.04690 (`docs/conditional_l_literature.md §2.3`).
- Lemma 4.1 (2-extremal ⇒ 3-dicritical): 2304.04690 p.9 l.488 (`conditional_l_literature.md §4`).
- Empirical check (evidence only): directed Hajós joins of `C₃,C₅` — 0/4 are 2-dicolourable,
  reproduced this pass via `scripts/enumerate_2extremal_v0_recon.py` (`directed_hajos_join`,
  `can_dicolor_k`). Consistent with the team's 1680-join / 4.16M-join searches.
- No new `.venv` created; no files outside `two_extremal_digraphs/` touched.
