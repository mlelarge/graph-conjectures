# Seam-existence setup: the structural heart of Conjecture 9.2 at k=2

**Target.** Aboulker–Aubian–Charbit, *Digraph Colouring and Arc-Connectivity*,
arXiv:2304.04690 (AAC), Conjecture 9.2: every 2-extremal digraph is in `H₂`. The
colouring descent is now KNOWN and OFF the table (see §0); what remains is purely
**structural seam existence** (Lemma A sufficiency). This memo (i) extracts the AAC
Section 5 (Theorem 5.1) proof strategy and pinpoints the EXACT step that degrades at
`k=2`, all read verbatim from the primary-source PDF; (ii) restates what is left to
prove for (SUFF-a)/(SUFF-b), separating the pure structural claim from the
2-extremality bookkeeping; (iii) states the residual structural lemmas the proof
angles should target and why the digon-forest `F_D` is the natural `k=2` handle.

All AAC quotes below are from `pdftotext -layout` of the arXiv PDF (re-extracted this
pass; OCR artefacts of `χ⃗`/`λ`/`K̅` noted inline). BJSS = Bang-Jensen, Bellitto,
Schweser, Stiebitz, *Hajós and Ore constructions for digraphs*, EJC 27(1) 2020 /
arXiv:1908.04096.

---

## 0. The colouring machinery is KNOWN — do not re-derive it

A 2-extremal digraph is **3-dicritical** (AAC Lemma 4.1: "Let `k≥1`, and let `D` be a
`k`-extremal digraph. Then `D` is Eulerian, `(k+1)`-dicritical …"). BJSS Theorem 2,
for the directed Hajós join `D = D1 ▽ D2` (verified verbatim against the BJSS PDF in
`docs/conditional_l_literature.md` §6):

- **(a)** `χ⃗(D) ≥ min{χ⃗(D1), χ⃗(D2)}`  — no `k` restriction.
- **(d)** If `D` is `k`-critical and **`k ≥ 3`**, then both `D1, D2` are `k`-critical.

Since a 2-extremal `D` is 3-dicritical, **once a genuine directed-Hajós factorisation
`D = D1 ▽ D2` is exhibited, BJSS Thm 2(d) at `k=3` gives `D1, D2` both 3-dicritical**,
hence `χ⃗(D1) = χ⃗(D2) = 3` **for free**. The tree-join lower bound at `k=2` is AAC
**Lemma 6.7** (`k≥2`, self-contained, both directions) — also free.

> **Consequence.** The dichromatic condition `χ⃗(piece) = 3` is NO LONGER an open part
> of Lemma A / Lemma B. The earlier "Conditional L" (cross-seam acyclicity gluing) and
> "Conditional U" (`χ⃗ ≤ 3`) are both subsumed: 2(d) gives 3-dicriticality of the
> pieces, which is *stronger* than `χ⃗ = 3`. Everything that remains is STRUCTURAL: that
> a seam EXISTS and that the two pieces are 2-extremal in the **connectivity** sense
> (strong / underlying-2-connected / `λ = 2` / underlying-Eulerian). This memo is
> scoped to exactly that residue.

---

## 1. AAC Section 5 = Theorem 5.1: the `k≥3` seam-existence proof, and where it dies at `k=2`

### 1.1 What Theorem 5.1 actually says (verbatim)

> **Theorem 5.1.** Let `k ≥ 3`. If `D` is `k`-extremal, then:
> • either `D = K̅_{k+1}` [symmetric complete graph on `k+1` vertices]
> • or `D` is a symmetric odd wheel (only in the case `k = 3`),
> • or `D` is a directed Hajós join of two `k`-extremal digraphs,
> • or `D` is a Hajós bijoin of two `k`-extremal digraphs.

(Note: the WebFetch paraphrase that reduced this to "directed Hajós join of two
`k`-extremal digraphs" alone is WRONG — there are **four** cases, and the bijoin case
is the engine. Do not trust paraphrased "verbatim" from the summarising model.)

`H_k` (`k≥3`) base objects = `K̅_{k+1}` (`k≥4`) or symmetric odd wheels (`k=3`); closure
under directed Hajós join + Hajós tree join. At `k=2` the bijoin is REPLACED by the
restricted **2-Hajós tree join** with even-`B`-parity (Def 9.1), and the base objects
are symmetric odd cycles + generalised wheels — which is why §9 is a separate
conjecture, not a corollary.

### 1.2 The proof STRATEGY of Section 5.3 (induction on `|V|`)

Assume `D` `k`-extremal is none of the four outcomes; derive a contradiction.

1. **Find a non-isolating minimum dicut and contract it (AAC Lemma 4.5 / 4.6 / 4.4).**
   Lemma 4.5 (`k≥4`): if *every* minimum dicut isolates a vertex then `D = K̅_{k+1}`.
   Lemma 4.6 (`k=3`): the same hypothesis forces `D` = symmetric odd wheel or a
   (bi)directed Hajós join. So a non-base `D` has a minimum dicut `(A, Ā)` with
   `|A|,|Ā| > 1`; Lemma 4.4 makes `D/A` `k`-extremal so induction applies to it.

2. **Pull a structured side out of the inductive decomposition of `D/A` (Claim 5.7.2).**
   > **Claim 5.7.2.** `D` has a minimum dicut `(X, X̄)` such that either `k ≥ 4` and
   > `D[X] = K̅_k`, or `k = 3` and `D[X]` is a *flower* of `D`. Moreover, if
   > `D[X] = K̅_k`, then each vertex of `X` has exactly one inneighbour and one
   > outneighbour in `X̄`.

   (A *flower* = symmetric even path `P` + a centre `x` joined by digons to all of `P`;
   the `k=3` shadow of `K̅_k`.) This is got by un-contracting `a` inside the side that
   `D/A`'s induction produced.

3. **Split on the interface across `(X, X̄)`** into two cases:
   - **Case 1 (mixed interface): ∃ `v ∈ X̄`, `u, w ∈ X`, `u≠w`, `uv, vw ∈ A(D)`.** Set
     `D' = D − {uv, vw} + {uw}`. Show `χ⃗(D') ≥ k+1` (Lemma 3.5 keeps `λ(D')≤k`; a
     mono dicycle in `D` through `uv,vw` re-routes through `uw`), so `D'` is
     `k`-extremal-or-not-biconnected; the size-`(k−1)` dicut `∂⁺(X)` forces `D'`
     **not** `k`-extremal (Lemma 4.1), hence `D'` has a **cutvertex** `a`. Then by
     **Lemma 5.7** `D` is a directed Hajós join or a Hajós bijoin — contradiction.
   - **Case 2 (digon-only interface): all `X`–`X̄` arcs are digons.** Subcases on
     `D[X]` strong / biconnected; uses **Lemma 3.3** ("`a₁, aₙ` receive the same colour
     in every `k`-dicolouring of `D[X̄]`") to add an interface edge `[a, b]`, recurse on
     `D[X̄] + [a, b]`, and again invoke Lemma 5.7 to extract a Hajós/bijoin.

4. **The cutvertex→seam engine (Lemma 5.7), verbatim:**
   > **Lemma 5.7.** Let `k ≥ 3`. Let `D` be a `k`-extremal digraph. Suppose there
   > exists `tu` and `uw` in `A(D)`, such that `D − {tu, uw}` has a cutvertex. Then `D`
   > is a directed Hajós join or a Hajós bijoin.

   This is the AAC analogue of the team's (SUFF-a): "a cut of `U(D) − {two arcs at u}`
   promotes to a genuine Hajós/bijoin factorisation". Its proof (via Lemma 5.4 for the
   directed case, Claim 5.7.1 for the bijoin case) is where the colouring is used to
   certify the pieces.

### 1.3 The EXACT step that needs `k ≥ 3` (the degradation point)

There are **three** distinct `k≥3`-uses; the load-bearing one for the `H₂` path is in
Lemma 5.7 / Claim 5.7.1.

**(D1) — the genuine degradation: Claim 5.7.1 inside Lemma 5.7 (the seam-promotion
gluing).** To certify the bijoin pieces, AAC builds dicolourings `φ₁` of `D₁+aw` and
`φ₂` of `D₂` that agree at `a` and additionally separate a colour:
> "• `φ₁(a) = φ₂(a)` and,
>  • if `φ₁(a) ≠ φ₁(t)`, then `φ₁(t) ≠ φ₂(u)` **(which is always possible up to
>  permuting colours, since `k ≥ 3`)**."

This is the precise step that DIES at `k=2`. With only `k=2` colours one cannot in
general make `φ₁(t)` avoid **both** `φ₁(a)` (forced) **and** `φ₂(u)` — two forbidden
values exhaust the 2-colour palette. The same "pick a third colour to dodge two
constraints" move recurs:
- Lemma 5.5 (bijoin lower bound) `k≥3`: "(this can always be done because `k ≥ 3`)".
- The whole bijoin OUTCOME of Theorem 5.1 has no `k=2` analogue — at `k=2` AAC replace
  it with the even-`B`-parity 2-Hajós tree join (Def 9.1), which is *why* Conj 9.2 is
  open.

**(D2) — the base-case split (Lemma 4.5 vs 4.6).** Lemma 4.5 needs `k≥4` and yields
the clean base `K̅_{k+1}`; at `k=3` it is replaced by Lemma 4.6 (a much harder
"super-special partition / obstruction" argument) whose base object is the symmetric
odd wheel. At `k=2` neither is available; the team's base objects (symmetric odd cycles
+ generalised wheels) and the `MC` discriminator are the replacement, and **no `k=2`
analogue of the Lemma 4.5/4.6 "every min dicut isolates ⇒ base object" dichotomy is
proved** — this is structurally the second wall.

**(D3) — Lemma 3.3's "colour class crosses the min dicut" is `k`-general but its USE
degrades.** Lemma 3.3 itself ("Let `k ≥ 1`. … `(X₁,X₂)` a dicut of size ≤ `k` with both
sides `k`-dicolourable … *either* a unique colour `i` on side 1 carries all out-arcs
*or* symmetrically") holds at `k=1` too. The Hall-theorem core (perfect matching in the
complement `H` of the cross-cut bipartite graph `B` ⇒ a `k`-dicolouring of `D`,
contradiction) is `k`-general. **But the structural conclusion it feeds is weak at
`k=2`:** at `k=2` "every colour class incident to exactly one cross-arc each way" gives
only a 2-class statement, and the side-1/side-2 asymmetry that drives the `k≥3` case
split (one side mono-coloured at the cut, other side balanced) carries far less
structure when there are only 2 colours. So Lemma 3.3 is available verbatim at `k=2`
but its discriminating power (Claim 5.7.2's `K̅_k`/flower side) collapses — the side
`D[X]` is then just a digon-path or a single digon, not a rigid `K̅_2`.

> **Net diagnosis.** Section 5's seam-existence proof has TWO genuinely `k≥3` walls:
> the base-case dichotomy (Lemma 4.5/4.6, → AAC's `MC`-free contraction machinery) and
> the seam-PROMOTION gluing (Lemma 5.7 / Claim 5.7.1's "dodge two colours, `k≥3`").
> The colouring half of the second wall is now removed by BJSS 2(d) (§0). What survives
> for the team is the **structural** content of Lemma 5.7 (cutvertex ⇒ factorisation)
> and the **`k=2` base-case dichotomy** (the team's `MC ∈ {0,1}` split), and the
> connectivity bookkeeping of the pieces.

---

## 2. Cleanest restatement of what remains, with the colouring removed

Throughout, `D` is non-base 2-extremal (not a symmetric odd cycle, not a generalised
wheel), so by definition: strong, `U(D)` 2-connected, Eulerian `in=out≥2`, `λ(D)=2`,
`χ⃗(D)=3` (hence 3-dicritical, AAC Lemma 4.1). `MC(D)∈{0,1}` is the mixed-2-cut
invariant (P4): `MC=1` iff some `(v, single edge e={a,b}, a,b≠v)` has `e` a bridge of
`U(D)−v`. `MC∈{0,1}` is always decidable, so **(SUFF-a) ∨ (SUFF-b) IS Lemma A**.

### 2.1 (SUFF-a): `MC(D)=1` ⇒ directed-Hajós factorisation

Split into **(STRUCT-a)** + **(EXTREMAL-a)**.

- **(STRUCT-a) [pure structure, OPEN — the heart].** `MC(D)=1` ⇒ there is a mixed
  2-cut `(v, {u,w})` (with `uv, vw ∈ A(D)`, `uw` the single join arc) such that
  `D − {uv, vw}` has cutvertex `v`, i.e. `U(D)` splits at `v` into sides `S₁ ∋ u`,
  `S₂ ∋ w` with `S₁ ∩ S₂ = {v}` and `{u,w}` the unique `S₁`–`S₂` edge. This is exactly
  the hypothesis of **AAC Lemma 5.7** with `t=u` (directed case). **What is NOT free:
  EXISTENCE of the RIGHT mixed 2-cut.** Member 7.33 (MC=1) proves the obvious
  vertex-2-cut-pair recipe FAILS — both naive sides are non-2-extremal — yet the true
  seam is `(v=6, {0,5})`. So (STRUCT-a) is "the digon-forest/single-edge bridge that
  *is* a Hajós seam exists", not "any mixed 2-cut works".

- **(EXTREMAL-a) [bookkeeping of the two pieces `D₁, D₂`].** Per
  `docs/lemma_a_proof.md` §3 and `docs/verify_lemma_b.md`, with status updated by §0:
  | piece condition | status | source |
  |---|---|---|
  | `|Dᵢ| < n` strictly smaller | **PROVED** | seam def |
  | unique crossing arc `(u,w)`, join arc SINGLE | **PROVED** (B0) | verify_lemma_b §B0; 0/52 |
  | Eulerian, `in=out` | **PROVED** (set-balance) | verify_lemma_b §B1 |
  | `in=out ≥ 2` value at merge `v` | **PROVED-modulo-1-line** (`λ=2` dicut, not isolated) | verify_lemma_b §B1 gap #7 |
  | strong | **PROVED** (Eulerian+wk-conn ⇒ strong) | verify_lemma_b §S |
  | `λ(Dᵢ) ≤ 2` | **PROVED** (single-arc reroute) | verify_lemma_b §B2 |
  | `λ(Dᵢ) ≥ 2` | **PROVED** (closed-trail; standard) | verify_lemma_b §B3 |
  | `U(Dᵢ)` 2-connected | **SKETCHED only** (size-2 interface fan/Menger) | verify_lemma_b §C |
  | **`χ⃗(Dᵢ) = 3`** | **FREE via BJSS 2(d)** at `k=3` (was OPEN) | §0 here |

  So (EXTREMAL-a) reduces to ONE genuine remaining line — **clause (C): `U(Dᵢ)`
  2-connected** — plus tightening the already-true `in=out≥2` `λ`-dicut line. The
  dichromatic condition is removed.

### 2.2 (SUFF-b): `MC(D)=0` ⇒ non-empty-A 2-Hajós tree-join

Split into **(STRUCT-b)** + **(EXTREMAL-b)**.

- **(STRUCT-b) [pure structure, OPEN — the heart].** `MC(D)=0` ⇒ `D` has a non-empty-A
  2-Hajós tree-join decomposition (Def 9.1): a plane tree `T` with edge-partition
  `(A,B)`, `B`-edges plain digons, ≥1 `A`-edge carrying a strictly-smaller 2-extremal
  block, peripheral directed cycle on the leaves, even number of `B`-edges on every
  leaf-to-leaf path. The interface for an `A`-block is a **2-vertex `[uᵢ,vᵢ]` digon**,
  NOT a single merge vertex (templates: members 7.7, 7.14, 7.36 — each one W₃ A-block,
  2-vertex interface). The contrapositive of P4 (`MC=0 ⇒ no Hajós merge vertex`) is
  PROVED, so clause-(b) is *provably the only* option when `MC=0`; existence of the
  tree-join itself is OPEN.

- **(EXTREMAL-b) [bookkeeping of the A-blocks].** Strictly-smaller and Eulerian are
  PROVED; strong / `U` 2-connected / `λ≤2` are **SKETCHED only** ("parallel to clause
  (a)", never line-by-line), and `χ⃗(block)=3` is now **FREE via AAC Lemma 6.7 (`k=2`,
  in-paper, both directions)** — see §0. WEAKNESS to flag: over `L₃..L₇` every tree-join
  A-block is the base W₃, so the recursive descent is *untested* and the oracle's
  `max_internal=2` cap means larger tree shapes are not searched (verify_lemma_b §clause-b).

### 2.3 One-line summary of the residue

> **Lemma A = (STRUCT-a) ∨ (STRUCT-b)** — pure existence of a usable seam — plus the
> single connectivity bookkeeping line **(C) `U(Dᵢ)` 2-connected** for the pieces. The
> Eulerian / strong / `λ=2` bookkeeping is PROVED; `χ⃗=3` is FREE (BJSS 2(d) for clause
> a, AAC Lemma 6.7 for clause b). **The proof effort should now spend 100% of its
> structural budget on (STRUCT-a)/(STRUCT-b) existence and the (C) flank.**

---

## 3. The residual structural lemma(s) to target, and why `F_D` is the natural handle

### 3.1 The precise lemmas to prove

**Residual Lemma R-a (directed-Hajós seam existence — the (SUFF-a) heart).** *Let `D`
be non-base 2-extremal with `MC(D)=1`. Then there exist `u, w ∈ V(D)` with `uw` a single
arc and a common neighbour `v` (`uv, vw ∈ A(D)`) such that `D − {uv, vw}` has cutvertex
`v`.* — i.e. the team's mixed-2-cut promotes to the **hypothesis of AAC Lemma 5.7**
(`t=u`, directed branch). Given R-a, AAC Lemma 5.4/5.7's *directed* branch
("`D − tu` has a cutvertex ⇒ directed Hajós join", Lemma 5.4, `k≥1`-general, structural)
exhibits the factorisation; BJSS 2(d) certifies `χ⃗=3` of the pieces; only clause (C)
remains for full 2-extremality. **R-a is the exact converse of P4** (P4 = necessity:
Hajós merge ⇒ `MC=1`; R-a = sufficiency: `MC=1` ⇒ a Hajós merge realising it). Member
7.33 forbids any "pick a vertex-2-cut pair" shortcut: R-a must locate the *single edge
that bridges `U(D)−v`*, not an arbitrary 2-cut.

**Residual Lemma R-b (tree-join seam existence — the (SUFF-b) heart).** *Let `D` be
non-base 2-extremal with `MC(D)=0`. Then `D` admits a non-empty-A 2-Hajós tree-join
(Def 9.1) into strictly-smaller 2-extremal blocks.* The `MC=0` hypothesis means there is
NO single bridge of any `U(D)−v`; the seam is distributed across the **digon forest**
plus ≥1 `A`-edge carrying a block, with even `B`-parity on leaf-to-leaf paths.

**Residual bookkeeping line R-C (`U(Dᵢ)` 2-connected).** Promote the size-2-interface
fan/Menger sketch (verify_lemma_b §C) to a line-by-line proof, for both clauses.

### 3.2 Why the digon-forest `F_D` is the natural `k=2`-specific handle

`F_D` (digon subgraph of `U(D)`) is a **forest** — P2, a `k=2`-only feature ABSENT at
`k≥3` (at `k≥3` the base objects `K̅_{k+1}` and symmetric odd wheels are digon-dense, so
the digon subgraph contains cycles; the whole AAC §5 machinery is run on min-dicuts and
`K̅_k`/flower sides, never on a digon forest). Three reasons it is the right handle:

1. **`F_D` replaces the `K̅_k`/flower side of Claim 5.7.2.** At `k≥3` the rigid side
   `D[X]` carrying the seam is `K̅_k` (`k≥4`) or a flower (`k=3`). At `k=2` the analogue
   is a piece of the digon forest: AAC's flower is "even symmetric path + digon centre"
   — a `k=3` shadow of a single `F_D`-path. The team's seam, when `MC=1`, runs through a
   *single edge bridging `U(D)−v`*; when `MC=0`, it runs through `F_D`-paths (the
   `B`-edges of Def 9.1 are exactly digons = edges of `F_D`). So the `MC=0`/`MC=1`
   dichotomy is literally a dichotomy on how the seam sits relative to `F_D`.

2. **The even-`B`-parity of Def 9.1 is a parity condition ON `F_D`-paths.** "Even number
   of `B`-edges on every leaf-to-leaf path" = even number of digons of `F_D` on each
   peripheral path. This is a forest/parity statement — tractable precisely because
   `F_D` is acyclic (unique paths between leaves). The `k≥3` bijoin has no such clean
   parity handle, which is exactly why AAC's `k≥3` bijoin and the `k=2` tree-join
   diverge.

3. **The single-arc closed-trail structure (P3) + `F_D` forest = a global seam
   certificate.** Single arcs decompose into balanced closed directed trails (P3); the
   digons form a forest (P2). A directed-Hajós seam is a single arc `uw` whose removal
   (with the two `v`-arcs) bridges `U(D)−v`; a tree-join seam is a forest-distributed
   digon configuration. So the `MC` invariant — computed from `F_D` + single edges
   alone — is the natural `k=2` replacement for AAC's "does a min dicut isolate a
   vertex?" dichotomy (Lemma 4.5/4.6). **R-a and R-b are the two halves of proving the
   `MC`-dichotomy is a genuine seam dichotomy**, and `F_D` is where both live.

### 3.3 Caveats the angles MUST respect (from the truth-set audits)

- The merge vertex `v` need NOT lie in `F_D` (member 7.17: valid `(v=3, e={4,0})`, `v`
  isolated in `F_D`). So R-a is a statement on `U(D)` + the single/digon split, not
  "trails through forest leaves" only.
- The naive cut-pair recipe is REFUTED at `n=7` (member 7.33). R-a must find the right
  single-edge bridge, provably, not the obvious 2-cut.
- All `n≤7` agreement (40/40 `MC` predicts seam type; 41/41 non-base members seamed) is
  EVIDENCE, never a theorem.

---

## 4. Pointers (primitives to reuse; pure Python, no deps)

- `scripts/h2_oracle.py`: `is_2extremal` (L248), `is_strong` (L70), `is_2connected`
  (L89), `lambda_D` (L181), `_hajos_decompositions` (L361),
  `_tree_join_decompositions` (L688, `max_internal=2` cap), `_is_generalised_wheel`
  (L917, sound recognizer).
- `scripts/seam_invariant.py`: `MC` and the `Hajós-seam ⇔ MC=1` harness.
- Data: `data/L_7.json` (index members 7.33, 7.7, 7.14, 7.36, 7.17),
  `data/seam_search_L6_L7.json` (ground-truth seam types).
- Prior analysis: `docs/lemma_a_proof.md` (§2 `MC`, §3 Lemma B), `docs/verify_lemma_b.md`
  (per-condition status), `docs/conditional_l_literature.md` (BJSS Thm 2 verbatim, §6).
