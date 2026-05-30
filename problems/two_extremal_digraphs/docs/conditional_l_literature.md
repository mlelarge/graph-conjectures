# Conditional L vs. the source paper: what the directed-Hajós lower bound actually gives

**Source.** Pierre Aboulker, Guillaume Aubian, Pierre Charbit, *Digraph Colouring and
Arc-Connectivity*, arXiv:2304.04690. Text below quoted verbatim from the arXiv PDF
(`pdftotext -layout`, page/line numbers are from that extraction; minor OCR artefacts of
the vector-symbol `χ⃗`/`λ` are noted inline).

**Bottom line (answer to the brief).** The paper does **not** contain a proof of the
`k=2` directed-Hajós lower bound that Conditional L needs. For `k≥3` the paper proves
**both** directions (forward lower bound *and* the converse "split piece stays extremal")
— and the converse is exactly the analogue of what the induction toward Conjecture 9.2
requires. But for the `k=2` case (Conjecture 9.2) the paper **explicitly defers** the
entire "`H₂` ⊆ 2-extremal" direction with the single sentence *"It is a routine work to
check that digraphs in H2 are 2-extremal"* (no lemma, no proof). The one general lemma
that is stated for `k≥2` (Lemma 6.7, tree join) covers the **tree-join** lower bound at
`k=2`, but the **directed-Hajós-join** lower bound is proved only via Lemma 5.3, which
routes the dichromatic part through a **cited** external result (Claim 5.3.1 = "Theorem 2
in [3]", Bang-Jensen–Bellitto–Schweser–Stiebitz). So Conditional L for the directed Hajós
join is, in the source, *cited* rather than *self-contained* — and the converse direction
the induction needs is exactly the half that [3]'s Hajós theorem gives in the *dicritical*
setting. Details and the precise gap below.

---

## 1. The objects (exact definitions)

**Condition (2) — what "extremal" optimises (p.7, l.156-159).** The paper characterises
digraphs with
> `χ⃗(D) = λ(D) + 1`   (2)

where `λ(D)` is the *maximum local arc-connectivity* `max_{u≠v} λ(u,v)`, and
`χ⃗(D) ≤ λ(D)+1 ≤ Δ_max(D)+1` always (Neumann-Lara [28]).

**k-extremal (p.7, l.178-182), verbatim:**
> "a digraph `D` is *k-extremal* if `D` is strong, its underlying graph is 2-connected,
> and `χ⃗(D) = λ(D) + 1 = k + 1`."

So **2-extremal** = strong + underlying 2-connected + `χ⃗ = λ+1 = 3`. (This matches the
team's working definition; Lemma 4.1 below adds Eulerian + 3-dicritical for free.)

**Definition 1.5 (Directed Hajós join), verbatim (p.4, l.200-207):**
> "Let `D1` and `D2` be two digraphs, with `uv1 ∈ A(D1)` and `v2 w ∈ A(D2)`. The directed
> Hajós join of `D1` and `D2` with respect to `(uv1, v2 w)` is the digraph `D` obtained
> from the disjoint union of `D1 − uv1` and `D2 − v2 w`, by identifying `v1` and `v2` to a
> new vertex `v`, and adding the arc `uw`."

This is exactly the team's seam: identified vertex `v = v1 = v2`, single added arc `u→w`.

**Definition 9.1 (2-Hajós tree join), verbatim core (p.32-33, l.1787-1846):** built from a
plane tree `T` with `≥2` edges, an edge-partition `(A,B)` of `T` with
> "every leaf to leaf path in `T` contains an even number of edges of `B`,"

a circular leaf ordering `C`, and for each `A`-edge `u_i v_i` a digraph `D_i` with
`[u_i,v_i] ⊆ A(D_i)`. Then
> "we define the 2-Hajós tree join `T(D1,…,Da;C)` to be the digraph obtained from `T` by
> replacing each edge `u_i v_i ∈ A` by `D_i − [u_i,v_i]`, each edge `x_i y_i ∈ B` by a
> digon and by adding the directed cycle `C = x1 → x2 → … → xℓ → x1`."

> "Observe that, in the definition of 2-Hajós tree joins, if `A = ∅`, then the resulting
> digraphs is a generalised wheel." (l.1848-1849)

**Conjecture 9.2, verbatim (p.33, l.1850-1854):**
> "Let `H2` be the smallest class of digraphs containing symmetric odd cycle and closed
> under taking directed Hajós join and 2-Hajós tree join. **It is a routine work to check
> that digraphs in H2 are 2-extremal.** We conjecture that they are the only ones.
> **Conjecture 9.2.** A digraph is 2-extremal if and only if it is in H2."

The boldface sentence is the *entire* published justification of the "`H₂` ⊆ 2-extremal"
forward direction (which contains Conditional L). There is **no** Lemma/Proposition number
attached to it in §9; the supporting machinery lives in §5–§6 and is stated for `k≥3`.

---

## 2. The directed-Hajós LOWER bound, exactly as the paper proves it

### 2.1 Lemma 5.3 — the directed-Hajós join preserves extremality (both directions)

**Lemma 5.3, verbatim (p.13, l.726-727):**
> "Let `k ≥ 1`. Let `D` be the directed Hajós join of two digraphs `D1` and `D2`. Then `D`
> is `k`-extremal if and only if both `D1` and `D2` are."

**The dichromatic content is CITED, not proved here.** The proof opens (l.731):
> "**Claim 5.3.1 (Theorem 2 in [3]).** `D` is `k+1`-dicritical if and only if both `D1`
> and `D2` are."

i.e. the whole "`χ⃗` is preserved" heart of the directed Hajós join — the digraph Hajós
lower bound `χ⃗(D)≥k+1` together with its converse — is delegated to:

> **[3]** J. Bang-Jensen, T. Bellitto, T. Schweser, and M. Stiebitz. *Hajós and Ore
> constructions for digraphs.* Electronic Journal of Combinatorics, 27(1):1–63, 2020.

Everything Lemma 5.3 itself proves is the *arc-connectivity* bookkeeping `λ(D)=k`
(via Lemma 3.5: `λ(D + uv − A(P)) ≤ λ(D)`), given the dicriticality from [3]. So:

- The **forward** lower bound "`D1,D2` extremal ⇒ `D` extremal" (the part the team calls
  Conditional L / the digraph Hajós lower bound) is, in the source, **Claim 5.3.1's**
  "if both `D1` and `D2` are `(k+1)`-dicritical then `D` is `(k+1)`-dicritical" — **a
  cited theorem of [3]**, valid for all `k≥1`, hence including `k=2`.
- The **converse** "`D` extremal ⇒ both pieces extremal" is the OTHER half of Claim 5.3.1
  ("`D` dicritical ⇒ both `Di` dicritical"), also from [3], also `k`-general.

### 2.2 Lemma 5.4 — the converse-seam lemma, with a SELF-CONTAINED gluing proof

This is the lemma whose proof is the directed-Hajós **gluing** argument written out in
full (the only place in the paper where it is), and it is the structural template for
"a `U(D)`-cut promotes to a directed-Hajós factorisation":

**Lemma 5.4, verbatim (p.13, l.748-749):**
> "Let `k ≥ 1`. Let `D` be a `k`-extremal digraph with an arc `uw ∈ A(D)`, such that
> `D − uw` has a cutvertex `v`. Then `D` is a directed Hajós join of two digraphs `D1` and
> `D2` with respect to `(uv, vw)`."

**Proof gluing core, verbatim (l.752-758):**
> "Assume by contradiction `uv ∈ A(D)`. By Lemma 4.1, `D` is `k+1`-dicritical, so `Di` has
> a `k`-dicolouring `ϕi` for `i = 1,2`. Since `uv` is an arc, there is no monochromatic
> `vu`-dipath with respect to `ϕ1`. Up to permuting colours, we may assume that
> `ϕ2(v) = ϕ1(v)`. Let `ϕ … ϕ(x) = ϕ1(x)` if `x ∈ V(D1)`, and `ϕ(x) = ϕ2(x)` if
> `x ∈ V(D2)`. We claim that `ϕ` is a `k`-dicolouring of `D`. Indeed, by construction of
> `ϕ` there is no monochromatic dicycle included in `D1` or `D2`, and a dicycle
> intersecting both `D1` and `D2` contains a `vu`-dipath included in `D1`, and thus cannot
> be monochromatic. Thus `ϕ` is a `k`-dicolouring of `D`, a contradiction."

**This is precisely the cross-seam acyclicity argument Conditional L is missing** — and it
is `k≥1`-general (uses only Lemma 4.1, the structural fact that `k`-extremal ⇒ `k+1`-
dicritical, valid for all `k`). The mechanism: a monochromatic dicycle crossing the
identified vertex `v` must traverse a `v…u`-dipath confined to one side, which the side's
own `k`-dicolouring already forbids being monochromatic. **However** Lemma 5.4 proves the
*contrapositive shape* (it derives a contradiction to rule out a chord `uv`); it is NOT a
standalone proof that "two seam-agreeing `≤2`-dicolourings glue". It presupposes the pieces
are `k`-extremal and uses their dicolourings to glue. So it is structurally the right tool
but it is not, by itself, the `χ⃗`-preservation theorem.

### 2.3 Lemma 6.7 — the tree-join lower bound, the ONLY general (k≥2) self-contained proof

**Lemma 6.7, verbatim (p.23, l.1344-1345):**
> "Let `k ≥ 2`. Let `D, D1, …, Dn` be digraphs such that `D` is a Hajós tree join of the
> `Di`. Then `D` is `k`-extremal if and only if all digraphs `D1, …, Dn` are `k`-extremal."

This is stated **for `k ≥ 2`**, and (unlike Lemma 5.3) the dichromatic lower bound is
proved *in the paper*. The forward lower-bound argument, verbatim (l.1362-1373):
> "Assume `D` is `k`-dicolourable. Then in any `k`-dicolouring of `D`, the vertices of `T`
> do not all get the same colour (otherwise `C` would [be] monochromatic). So there is a
> digraph `Di` such that the vertices `ui` and `vi` get distinct colours. But this provides
> a proper `k`-dicolouring of the corresponding `Di`. Hence, if `D` is `k`-dicolourable,
> then `min_i χ⃗(Di) ≤ k`. … if each `Di` is `k`-extremal, then `D` is `k`-extremal."

**This argument uses NO `k≥3` hypothesis** — it is pure: a monochromatic peripheral cycle
`C` forces all junction vertices to one colour; non-monochromaticity of `C` forces some
`u_i,v_i` to differ, which restricts to a `k`-dicolouring of `D_i − [u_i,v_i]` extending
across the digon, contradicting `χ⃗(D_i)=k+1`. So **for the tree-join part, the directed
Hajós lower bound at `k=2` IS proved in the paper** (Lemma 6.7 with `k=2`). This is the
piece of "routine work" that genuinely is routine, and the team can cite Lemma 6.7
directly for the tree-join clause of Conditional L / clause (b).

The converse direction of Lemma 6.7 (l.1377-1418) extends a tree colouring (Claim 6.7.1)
and uses **Lemma 4.3** (digon endpoints get equal colour in any `≤k`-dicolouring of
`D_i−[u_i,v_i]`); Lemma 4.3 is stated for `k≥1` (l.533), so this converse is also `k≥2`.

### 2.4 Lemma 5.5 — the BIJOIN lower bound, where `k≥3` is genuinely used

**Lemma 5.5, verbatim (p.14, l.766-767):**
> "Let `k ≥ 3`. Let `D` be a Hajós bijoin of two digraphs `D1` and `D2`. If `D` is
> `k`-extremal, then both `D1` and `D2` are `k`-extremal."

Its `χ⃗(D1)≥k+1` step (l.790-806) constructs `ϕ2` with `ϕ2(u)≠ϕ1(t)` and notes
> "(this can always be done because `k ≥ 3`)" (l.793).

So the **bijoin** lower bound truly needs `k≥3`; it has **no** `k=2` analogue in the paper.
But note: the directed **Hajós join** (Lemma 5.3) and the **tree join** (Lemma 6.7) do NOT
have this restriction — `5.3` is `k≥1` (via [3]); `6.7` is `k≥2` and self-contained. Since
`H₂` is closed only under directed Hajós join and 2-Hajós tree join (Def 9.1 / Conj 9.2),
**not** under the general bijoin, the `k≥3`-only Lemma 5.5 is not on the `H₂` critical path.

---

## 3. Does any of this already imply Conditional L / the `χ⃗=3` preservation?

**Restate Conditional L** (per `docs/lemma_a_proof.md` §3, §5): in the directed-Hajós-join
setting, two seam-agreeing `≤2`-dicolourings of the pieces glue to a `≤2`-dicolouring of
`D`; equivalently the digraph Hajós **lower bound** — the directed Hajós join of two
digraphs each *not 2-dicolourable* is again not 2-dicolourable — and the induction's
contrapositive/converse form (a split piece keeps `χ⃗=3`).

**Verdict, three parts:**

**(a) The directed-Hajós-join lower bound at `k=2` IS a cited theorem — Claim 5.3.1 /
Theorem 2 of [3].** The forward statement "`D1,D2` both `3`-dicritical ⇒ their directed
Hajós join is `3`-dicritical" is exactly Conditional L's lower-bound half, and it is
asserted in the paper (l.731) as Theorem 2 of Bang-Jensen–Bellitto–Schweser–Stiebitz [3]
for all `k`. **Caveat the team must resolve before citing as closed:** the paper does not
reproduce [3]'s proof, and `χ⃗(D)=3` *dicriticality of the join* is the chain
`3-dicritical pieces ⇒ 3-dicritical join`; the team's Conditional L is phrased on *general*
2-extremal pieces glued at a seam (with the added arc / identified vertex), which is the
*same* operation but the load-bearing acyclicity-across-the-seam step is precisely what [3]
proves for the dicritical case. This is a genuine citation to verify against [3] directly
(MEMORY: route load-bearing citations to source; do not assert "known" on the paper's
say-so). Specifically: confirm that [3, Thm 2] is stated for the **directed** (single added
arc `uw`) Hajós join and gives the **lower** bound (`χ⃗ ≥ k+1`) and not only the
edge-density/upper results suggested by [3]'s title.

**(b) Lemma 5.4 supplies the explicit `k`-general gluing mechanism** — the cross-`v` dicycle
must contain a one-sided `v…u`-dipath that the side's own dicolouring keeps non-mono. This
is the proof *idea* the team should lift for a self-contained Conditional L, sidestepping
the [3] dependency. It is written for the contrapositive (no chord), but the colour-merge
construction `ϕ = ϕ1 on D1, ϕ2 on D2` with `ϕ1(v)=ϕ2(v)` and the dicycle case-split
(inside `D1`; inside `D2`; crossing ⇒ uses a `vu`-dipath in one side) is exactly a
seam-agreeing glue. **It does not, by itself, prove `χ⃗(piece) = 3` for a split piece** — it
assumes the pieces are extremal and glues their colourings; it is the *forward* (assemble)
direction, not the *converse* (descend) direction.

**(c) The induction needs the CONVERSE, and that is NOT given by the forward lower bound.**
The induction toward Conjecture 9.2 is (per `lemma_a_proof.md` §3,§4): a non-base 2-extremal
`D` splits at a seam into pieces `D_i`, and we need **`D_i` again 2-extremal** — in
particular `χ⃗(D_i) = 3` (the team's "Conditional L = `χ⃗(D_i) ≥ 3` preservation"). The
*forward* Hajós lower bound (`D_i` extremal ⇒ `D` extremal) does **not** give this. The
matching *converse* in the paper is:
  - directed-Hajós join: the "only if" half of Lemma 5.3 = the converse half of
    Claim 5.3.1 / Thm 2 of [3] ("`D` dicritical ⇒ both `D_i` dicritical"), `k`-general;
  - tree join: the "only if" half of Lemma 6.7 (`k≥2`, proved in-paper).
**So the converse the induction needs is, for `k=2`:** (i) the directed-Hajós-join converse
= the converse half of [3, Thm 2] at `k=2` (CITED, must be verified against [3]); and
(ii) the tree-join converse = Lemma 6.7 at `k=2` (PROVED in-paper). Neither is the bijoin
Lemma 5.5 (that one is `k≥3`-only, off the `H₂` path).

**Net:** *The forward directed-Hajós lower bound alone does NOT close Conditional L.* The
exact theorem the induction needs is the **converse** ("split piece keeps `χ⃗=3`"). For the
**tree-join** clause this converse is already a theorem at `k=2`: **Lemma 6.7, `k=2`**,
self-contained, citable now. For the **directed-Hajós-join** clause this converse is the
`k=2` instance of **Claim 5.3.1 = [3, Theorem 2]** — cited in the paper but not reproduced;
it must be checked directly in Bang-Jensen–Bellitto–Schweser–Stiebitz [3] before being
treated as established. This is the single literature action item that could collapse the
directed-Hajós half of Conditional L from OPEN to "cited and verified".

---

## 4. The `k≥3` machinery cannot be black-boxed to `k=2` — why the paper stops at 3

The paper's full characterisation (Theorem 1.8 / Theorem 6.8) is **for `k≥3`** and `k=1`,
and §9's first sentence says it leaves `k=2` open. Two concrete `k≥3` dependencies that
**fail or are absent at `k=2`** (so the team cannot just "set `k=2`" in §5–§6):

1. **Lemma 5.5 (bijoin lower bound) needs `k≥3`** explicitly (l.793, "because `k≥3`"). The
   bijoin/degenerate-bijoin decomposition (Theorem 5.1, third/fourth bullets) is the engine
   of the `k≥3` structure theorem; at `k=2` the paper replaces the general bijoin by the
   restricted **2-Hajós tree join** with the *even-`B`-parity* condition (Def 9.1), which is
   why §9 is a separate conjecture and not a corollary.
2. **The decomposition Theorem 5.1 is stated for `k≥3`** ("Let `k≥3`. If `D` is
   `k`-extremal, then … directed Hajós join … or Hajós bijoin …", l.688-694). The `k=2`
   structural decomposition (the *existence* of a seam = the team's Lemma A) has **no
   counterpart** in the paper; it is exactly what §9 leaves open. So the source gives the
   *constructors* (`H₂` closure, Def 9.1) and asserts they yield 2-extremal digraphs
   ("routine"), but provides **no** `k=2` decomposition theorem — consistent with the
   team's finding that Lemma A (seam existence) is the open wall.

For completeness, **Lemma 4.1** (p.9, l.488): "Let `k≥1`, and let `D` be a `k`-extremal
digraph. Then `D` is Eulerian, `(k+1)`-dicritical and …" — `k`-general, so the team's
"2-extremal ⇒ Eulerian + 3-dicritical" base facts are theorems of the paper, valid at `k=2`.

---

## 5. Exact citations to carry into the proof docs

| Claim the team needs | Where in 2304.04690 | `k=2`? | Status |
|---|---|---|---|
| Directed Hajós join (Def) | Def 1.5, p.4 l.200-207 | yes | definition |
| 2-Hajós tree join (Def) | Def 9.1, p.32-33 l.1787-1846 | yes | definition |
| `H₂` ⊆ 2-extremal (the forward whole) | §9 l.1851 "routine work" | yes | **asserted, no proof** |
| Dir-Hajós lower bound (`χ⃗` preserve), fwd+conv | Lemma 5.3 via **Claim 5.3.1 = [3, Thm 2]** | yes (`k≥1`) | **CITED [3], not reproduced** |
| Dir-Hajós gluing mechanism (cross-seam acyclicity) | Lemma 5.4 proof, l.752-758 | yes (`k≥1`) | **PROVED in-paper** (template for Conditional L) |
| Tree-join lower bound, fwd+conv | **Lemma 6.7, l.1344-1418** | **yes (`k≥2`)** | **PROVED in-paper** |
| Digon endpoints equal-colour | Lemma 4.3, l.533 | yes (`k≥1`) | PROVED in-paper |
| 2-extremal ⇒ Eulerian + 3-dicritical | Lemma 4.1, l.488 | yes (`k≥1`) | PROVED in-paper |
| Bijoin lower bound | Lemma 5.5, l.766 | **NO (`k≥3` used l.793)** | off the `H₂` path |
| `k≥3` decomposition (seam existence) | Theorem 5.1, l.688 | **NO (`k≥3`)** | no `k=2` analogue = team's Lemma A, OPEN |

Reference entries, verbatim:
> **[3]** J. Bang-Jensen, T. Bellitto, T. Schweser, and M. Stiebitz. *Hajós and ore
> constructions for digraphs.* Electronic Journal of Combinatorics, 27(1):1–63, 2020.
> **[28]** V. Neumann-Lara. *The dichromatic number of a digraph.* Journal of Combinatorial
> Theory, Series B, 33(3):265–270, 1982.
> **[27]** B. Mohar. *Eigenvalues and colourings of digraphs.* Linear Algebra and its
> Applications. (directed Brooks)
> **[18]** R. Hoshino, K. Kawarabayashi. *The edge density of critical digraphs.*
> Combinatorica, 35:619–631, 2015. (cited at l.198 as where the *directed* Hajós join "was
> first introduced".)

> Directed Brooks (Theorem 1.3) is cited as Mohar [27], "see also [1]" = Aboulker–Aubian,
> *Four proofs of the directed Brooks' theorem*, Discrete Math. 2022.

---

## 6. Recommended next action for the proof effort

1. **Pull [3] (Bang-Jensen–Bellitto–Schweser–Stiebitz, EJC 27(1), 2020) and read its
   "Theorem 2".** Confirm it states, for the **directed** Hajós join (single added arc
   `uw`, identified vertex), the **iff** `D` is `(k+1)`-dicritical ⇔ both pieces are, with
   the lower bound proved. If so, the **directed-Hajós half of Conditional L is closed by
   citation** for `k=2` (the converse "split piece stays 3-dicritical" is the ⇒ half).
   *Do not treat the present paper's one-line "Claim 5.3.1 (Theorem 2 in [3])" as
   sufficient provenance* — verify the exact statement and direction in [3] itself.
2. **For the tree-join clause, cite Lemma 6.7 with `k=2` directly** — it is self-contained
   and proves both directions at `k≥2`, so the tree-join half of Conditional L is already a
   theorem (modulo the team's seam-existence/Lemma A, which is a *structural* not a
   *colouring* gap).
3. **The genuine remaining colouring gap** (if [3, Thm 2] turns out not to cover the
   converse, or covers only dicriticality and not the connectivity-preserving 2-extremality)
   should be filled by lifting the **Lemma 5.4 gluing proof** (l.752-758) to a standalone
   "seam-agreeing 2-dicolourings glue" statement — that proof is `k`-general and is the
   exact mechanism. Even then, this only closes the *forward/assemble* and the
   *dicriticality-converse*; it does **not** supply seam EXISTENCE (Lemma A), which the
   paper itself leaves open at `k=2` (no `k=2` analogue of Theorem 5.1).

---

## Independent citation verification (2026-05-30, primary source)

BJSS = Bang-Jensen, Bellitto, Schweser, Stiebitz, *Hajós and Ore constructions for
digraphs*, arXiv:1908.04096. Theorem 2 read directly from the PDF (lines 190–245 of the
pdftotext extraction). **Verbatim**, for the directed Hajós join `D = D1 ▽ D2`:

- **(a)** `χ⃗(D) ≥ min{ χ⃗(D1), χ⃗(D2) }`  — *no `k` hypothesis*; general.
- **(b)** If `χ⃗(D1) = χ⃗(D2) = k` and **`k ≥ 3`**, then `χ⃗(D) = k`.
- **(c)** If both `D1, D2` are `k`-critical and **`k ≥ 3`**, then `D` is `k`-critical.
- **(d)** If `D` is `k`-critical and **`k ≥ 3`**, then both `D1, D2` are `k`-critical.

Proof of (a) is the splice `C1 ∪ C2 − u1v1 − v2u2 + u1u2` (the cross-seam acyclicity heart).

**Conclusions confirmed:** (i) Conditional L, directed-Hajós half = Thm 2(a), no `k`
restriction → at the induction's `k=3` it gives `χ⃗(Dᵢ) ≥ 3 ⇒ χ⃗(D) ≥ 3`. (ii) The
criticality descent the induction needs is Thm 2(d); its hypothesis is **`k ≥ 3`** (NOT
`k ≥ 2` — an earlier memo misquote, now corrected), satisfied because a 2-extremal digraph
is 3-dicritical (`k=3 ≥ 3`). (iii) The **2-Hajós tree-join** lower bound and **seam
existence** at `k=2` are NOT supplied by BJSS and remain open.
