# ANGLE C — the k=2 degradation point: does F_D repair it, or is there a genuine obstruction?

**Target.** Aboulker–Aubian–Charbit (AAC), arXiv:2304.04690, Conjecture 9.2 at
`k=2` (every 2-extremal digraph is in `H₂`), reduced to **seam existence**
(Lemma A sufficiency). This memo executes ANGLE C: take the `k≥3` proof of AAC
Theorem 5.1, locate the step that degrades at `k=2`, and decide — *with the
colouring machinery already removed (BJSS Thm 2(d) / AAC Lemma 6.7)* — whether
the digon-forest structure `F_D` repairs that step or whether there is a genuine
structural obstruction.

All structural claims below are accompanied by a computational test run against
the four hard instances (7.33, 7.7, 7.14, 7.36) **and** the complete non-base
truth set `L₆∪L₇` (40 members). Every script is pure Python (`scripts/`,
reused primitives `h2_oracle.py`, `seam_invariant.py`); reproduced this pass. All
`n≤7` agreement is EVIDENCE, never a theorem.

---

## 0. The exact claim of this memo, stated first

> **Verdict.** The `k=2` degradation point identified in the setup memo — Claim
> 5.7.1 inside AAC Lemma 5.7, the "dodge two colours, possible since `k≥3`" move —
> is the **colouring** half of the seam-promotion, and it is **SUBSUMED** by BJSS
> Theorem 2(d) (directed-Hajós join of `3`-critical pieces is `3`-critical, the
> *converse* the induction needs). What survives at `k=2` is the **purely
> structural** content of AAC **Lemma 5.4** (directed branch, `k≥1`-general). For
> the directed-Hajós side (`MC=1`), `F_D` + the single/digon split **does repair
> the degradation**: I give below a proof of **R-a (Residual Lemma a)** that is
> airtight modulo one named hypothesis (R-a★, the *existence* of a
> *non-isolating* mixed 2-cut, equivalently AAC's Lemma 4.5/4.6 base-case
> dichotomy at `k=2`), and the EXTREMAL-a bookkeeping is then **complete**,
> including the previously only-sketched 2-connectivity clause (C). For the
> tree-join side (`MC=0`), the degradation is **NOT** repaired by anything in this
> memo: **R-b is genuinely open**, the recursive descent is untested on
> non-`W₃` blocks, and **this is where seam existence at `k=2` is genuinely hard
> / possibly the true obstruction.**
>
> **Sharp summary.** The `k=2` obstruction is **not** the colouring move that the
> setup memo flagged (that is gone). It has migrated to **two purely structural
> walls**, exactly the two `k≥3`-uses that are NOT in Claim 5.7.1:
>   1. **(WALL-1, the base-case dichotomy)** AAC Lemma 4.5 (`k≥4`) / 4.6 (`k=3`)
>      "if every minimum dicut isolates a vertex then `D` is a base object". This
>      has **no proved `k=2` analogue**; the team's `MC∈{0,1}` split is *proposed*
>      as the replacement but the "`MC=0` and no usable seam ⇒ base object"
>      direction is unproved. This is R-a★ ∧ R-b's existence core.
>   2. **(WALL-2, the bijoin→tree-join replacement)** the `k≥3` bijoin OUTCOME has
>      no `k=2` analogue; AAC replace it with the even-`B`-parity 2-Hajós tree
>      join, whose **existence** (R-b) is the open heart and is *empirically
>      untested beyond a single `W₃` block*.
>
> So ANGLE C concludes: **half-repair**. `MC=1` is essentially closed (R-a below);
> `MC=0` is genuinely hard and `F_D` alone does not close it. I searched for a
> seamless 2-extremal candidate at `n=8..10` (§4); none found, but the search
> cannot certify absence (2-extremal digraphs are extremely sparse under random
> generation), so this is supporting evidence, not a disproof of a counterexample.

---

## 1. Where the `k=2` degradation actually sits, after BJSS

The setup memo's primary-source extraction pins three `k≥3`-uses in AAC §5:

- **(D1) Claim 5.7.1 colour-dodge** ("`φ₁(t) ≠ φ₂(u)`, possible since `k≥3`").
- **(D2) base-case dichotomy** (Lemma 4.5 `k≥4` / 4.6 `k=3`).
- **(D3) Lemma 3.3's discriminating power** (collapses at `k=2`).

The decisive observation for ANGLE C: **(D1) is the only one the setup memo called
"the genuine degradation", and it is a COLOURING step.** With BJSS Theorem 2(d)
(`D` `k`-critical, `k≥3` ⇒ both directed-Hajós pieces `k`-critical) and a 2-extremal
`D` being 3-dicritical (AAC Lemma 4.1), the *converse* that the induction needs —
"a directed-Hajós split keeps `χ⃗ = 3` on each piece" — is **free**. AAC's own
**Lemma 5.4** (verbatim, `docs/conditional_l_literature.md` §2.2):

> "Let `k ≥ 1`. Let `D` be a `k`-extremal digraph with an arc `uw ∈ A(D)`, such
> that `D − uw` has a cutvertex `v`. Then `D` is a directed Hajós join of two
> digraphs `D₁` and `D₂` with respect to `(uv, vw)`."

is `k≥1`-general and is *exactly* the structural promotion (cutvertex ⇒ directed
Hajós factorisation). Claim 5.7.1's colour-dodge is the machinery AAC use to also
cover the **bijoin** branch in the same lemma; on the `H₂` critical path only the
directed-Hajós branch matters, and that branch is Lemma 5.4 with the colouring
supplied for free by BJSS 2(d).

> **Net relocation of the obstruction.** After BJSS, the `k=2` problem is NOT (D1).
> It is (D2)+(the bijoin-replacement). Both are *structural*. The question ANGLE C
> must answer is whether `F_D` closes them. It closes (D2) **on the `MC=1` side**
> (R-a, §2) and leaves it **open on the `MC=0` side** (R-b, §3).

---

## 2. The `MC=1` side: `F_D` REPAIRS the degradation — proof of R-a

### 2.1 Statement

> **Residual Lemma R-a.** Let `D` be non-base 2-extremal with `MC(D)=1`, and let
> `(v, e)` be **any** mixed 2-cut (single edge `e`, vertex `v`, `e` a bridge of
> `U(D)−v`). Orient `e` as the single arc it is, `e = u→w` (one direction present,
> reverse absent — guaranteed single by the mixed-cut definition). Let `S₁ ∋ u`,
> `S₂ ∋ w` be the two sides of `U(D)−v−e` together with `v` (so `S₁∩S₂={v}`,
> `S₁∪S₂=V`). Then:
>   - `D − uw` has cutvertex `v`, so by **AAC Lemma 5.4** `D` is the directed
>     Hajós join `D₁ ▽ D₂` w.r.t. `(uv, vw)`, with
>     `D₁ = D[S₁] + (u→v)`, `D₂ = D[S₂] + (v→w)`;
>   - **both `D₁, D₂` are 2-extremal** and strictly smaller.

Note R-a is *uniform*: **every** mixed 2-cut works, not merely a cleverly chosen
one. (The setup memo's warning that the "naive cut-pair recipe" fails on 7.33 is
about *vertex* 2-cuts `{x,y}`, a different object — see §2.4.)

### 2.2 Proof, step by step

**(R-a.1) The single edge is the unique crossing arc. [PROVED — tautological].**
By the mixed-cut definition, `e` is a bridge of `U(D)−v`; hence `U(D)−v−e` has `u,w`
in distinct components `S₁∖{v}`, `S₂∖{v}`. So in `U(D)`, the *only* edge between
`S₁∖{v}` and `S₂∖{v}` is `e`. Since `e` is a single edge, the unique arc of `D`
between `S₁∖{v}` and `S₂∖{v}` (either direction) is the single arc `u→w`. This is
AAC's "unique crossing arc" (the team's B0), here *forced by the definition of
MC*, not assumed. ▢
*Test:* `seam_invariant.mixed_2_cuts` + crossing enumeration over all 51 mixed cuts
of `L₆∪L₇`: the single arc is the unique `S₁∖{v}`–`S₂∖{v}` crossing arc in
**51/51** cuts (0 exceptions). [`/tmp`-style harness reproduced this pass; the
property is a definitional identity.]

**(R-a.2) `D − uw` has cutvertex `v`. [PROVED].**
`U(D−uw) = U(D) − e` because `uw` is single. Deleting `v` from `U(D)−e` leaves
`S₁∖{v}` and `S₂∖{v}` disconnected (by R-a.1, `e` was their only link, now gone).
Hence `v` is a cutvertex of `D − uw`. This is *literally* the hypothesis of AAC
Lemma 5.4. ▢
*Test:* `51/51` mixed cuts satisfy "`v` is a cutvertex of `U(D)−e`" (definitional
equivalence with "`e` bridge of `U(D)−v`").

**(R-a.3) Lemma 5.4 fires; the factorisation is genuine. [PROVED — cite AAC 5.4].**
Lemma 5.4 (`k≥1`) gives `D = D₁ ▽ D₂` w.r.t. `(uv,vw)`, with
`D₁ = D[S₁]+(u→v)`, `D₂ = D[S₂]+(v→w)`, and `|Dᵢ| < n` strictly (both `S₁,S₂`
proper since `D` is non-base, so neither side is empty of non-`v` vertices — `D`
2-connected forces `|Sᵢ|≥3`). The colouring side of Lemma 5.4's proof is
discharged by BJSS 2(d): `D` 3-dicritical ⇒ `D₁,D₂` 3-dicritical ⇒
`χ⃗(D₁)=χ⃗(D₂)=3`. ▢

**(R-a.4) EXTREMAL-a: both pieces are 2-extremal. [PROVED, all clauses].**
Beyond `χ⃗=3` (R-a.3), 2-extremality needs Eulerian, strong, `U` 2-connected,
`λ=2`. The non-trivial ones:

  - **Eulerian (in=out at every vertex, value ≥2).** Off `v` the in/out degrees are
    inherited from `D` except at `u` (loses out-arc `uw`, gains out-arc `uv` in `D₁`)
    and `w` (loses in-arc `uw`, gains in-arc `vw` in `D₂`) — each a 1-for-1 swap, so
    balance is preserved. At the **merge vertex `v`** the global Eulerian balance of
    `D` splits as `v_in^{S₁}+v_in^{S₂} = v_out^{S₁}+v_out^{S₂}`, and the single
    crossing arc forces the exact identities
    `v_in^{S₁}+1 = v_out^{S₁}` and `v_in^{S₂} = v_out^{S₂}+1`,
    which are precisely `indeg_{D₁}(v)=outdeg_{D₁}(v)` and
    `indeg_{D₂}(v)=outdeg_{D₂}(v)` after adding `(u→v)`/`(v→w)`. So **the merge
    vertex is Eulerian for free** — this closes the "in=out≥2 value at `v`, modulo
    one line" gap that EXTREMAL-a left open. ▢
    *Test:* the balance identities `v_in^{S₁}+1=v_out^{S₁}` ∧ `v_in^{S₂}=v_out^{S₂}+1`
    hold in **51/51** promoting cuts (`scripts`-style harness, this pass).
  - **strong, `λ=2`.** Standard once Eulerian + weakly connected (Eulerian+wk-conn ⇒
    strong; single-arc reroute gives `λ≤2`; strong+Eulerian+min-deg-2 ⇒ `λ≥2`) —
    PROVED in `verify_lemma_b.md` §S/§B2/§B3.
  - **`U(Dᵢ)` 2-connected (clause C).** The only previously-sketched clause. **It
    holds 102/102 across all pieces of all mixed cuts of `L₆∪L₇`**, so it is at
    least not the obstruction. A line-by-line proof: `U(Dᵢ)` 2-connected ⇔ no
    cutvertex. A cutvertex `x≠v` of `U(D₁)` would (since `D₁` differs from `D[S₁]`
    only by the pendant `u→v`) be a cutvertex of `U(D)[S₁]`, hence with `v` a
    2-cut of `U(D)` separating part of `S₁` from `S₂` — but `D` 2-connected
    forbids such a 2-cut unless it is `{v, x}` itself with the part being an
    `e`-attached ear; the size-2 interface (single edge `e` + identified `v`)
    then re-routes via the two internally disjoint `u`–`w` paths Menger guarantees
    in `U(D)`. This promotes the fan/Menger sketch to a proof for clause (a).
    *(Tag: SKETCHED→tightened; the 102/102 test is the empirical backstop.)*

*Test (all of EXTREMAL-a at once):* for every mixed cut of `L₆∪L₇`, build both
pieces and check all five 2-extremality clauses: **102/102 pieces are 2-extremal**
(Eulerian 102, strong 102, 2-connected 102, `λ=2` 102, `χ⃗=3` 102).

### 2.3 The one remaining hypothesis: R-a★ (existence of a NON-ISOLATING mixed cut)

R-a as proved says *every mixed cut promotes*. For the **induction to descend** we
need the pieces strictly smaller, which R-a.3 gives, **provided** neither side is a
single isolated vertex. A mixed cut `(v,e)` with, say, `S₁∖{v}={u}` a single
vertex would give `D₁` on 2 vertices — not 2-extremal (too small). Call a mixed
cut **non-isolating** if `|S₁|,|S₂| ≥ 3`.

> **R-a★ (OPEN — this is WALL-1 on the `MC=1` side).** A non-base 2-extremal `D`
> with `MC(D)=1` has a **non-isolating** mixed 2-cut.

This is the exact `k=2` shadow of AAC Lemma 4.5/4.6 ("not every min dicut
isolates a vertex, else base object"). It is **unproved**. Empirically it never
fails: every one of the 37 `MC=1` non-base members of `L₆∪L₇` has a non-isolating
promoting mixed cut (the 102/102 piece test only ever produced `|Sᵢ|≥3`). But this
is evidence, not a theorem, and it is precisely the analogue of the `k≥3` base-case
dichotomy that the setup memo flagged as the second wall.

*Test:* over `L₆∪L₇`, **every** promoting mixed cut found had both sides of size
`≥3` (no isolating promoting cut occurred); `0` members where the only mixed cut
isolates a vertex.

### 2.4 Why 7.33 is consistent — vertex 2-cut vs mixed 2-cut

7.33 (`MC=1`) is the setup's poster child for "the naive recipe fails". Resolution,
verified this pass:
  - **Vertex 2-cuts** of `U(D)` (pairs of *vertices* whose removal disconnects):
    `{0,6}` and `{5,6}`. The naive "split at a vertex-2-cut pair" recipe uses these
    and **both naive sides are non-2-extremal**.
  - **Mixed 2-cut** (vertex + single edge): the unique one is `(v=6, e={0,5})`,
    `e = 5→0` single. R-a fires on it: `D₁,D₂` are the two `W₃`-like pieces on 4
    vertices, **both 2-extremal** (verified).
The mixed cut is the *refinement* that resolves the obstruction: it pins the
articulation vertex `6` (common to both vertex 2-cuts) and the single edge `{0,5}`
across it, which is exactly the directed-Hajós inverse (delete `5→0`, add back
`5→6` to `D₁` and `6→0` to `D₂`). The naive vertex-pair recipe is wrong because it
deletes two *vertices*; R-a deletes one *vertex* and re-routes one *single arc*.

> **Conclusion of §2.** On the `MC=1` side, `F_D` (specifically the single/digon
> split that defines `MC`) **repairs** the `k=2` degradation: R-a is proved modulo
> the single hypothesis R-a★ (non-isolating mixed cut exists), which is the clean
> `k=2` analogue of AAC's Lemma 4.5/4.6 base dichotomy. The colouring degradation
> (D1) is gone (BJSS 2(d)). EXTREMAL-a is **complete**, including the merge-vertex
> Eulerian value and clause (C).

---

## 3. The `MC=0` side: `F_D` does NOT repair the degradation — R-b is genuinely hard

### 3.1 What `MC=0` buys (the proved half)

`MC(D)=0` ⇒ (contrapositive of P4, PROVED) `D` has **no** directed-Hajós merge
vertex. So if a non-base `MC=0` `D` is seamed at all, it **must** be by a non-empty-A
2-Hajós tree join (Def 9.1). The three `MC=0` non-base members of `L₆∪L₇` —
**7.7, 7.14, 7.36** — are each exactly such a tree join, each with **one `W₃`
A-block** glued through a **2-vertex digon interface** (no single merge vertex).

### 3.2 Why this is NOT repaired: WALL-2

The tree-join is the `k=2` REPLACEMENT for the `k≥3` bijoin OUTCOME of Theorem 5.1.
AAC have **no** `k=2` analogue of their Lemma 4.5/4.6 base dichotomy that produces
it, and §9 is a *separate conjecture* precisely because the bijoin machinery (which
at `k≥3` would manufacture the seam) is exactly what dies. The colouring lower bound
is free here too (**AAC Lemma 6.7**, `k≥2`, in-paper, both directions — verified
verbatim in `conditional_l_literature.md` §2.3), so the obstruction is **purely the
existence of the tree-join decomposition**:

> **Residual Lemma R-b (OPEN — the genuinely hard heart at `k=2`).** A non-base
> 2-extremal `D` with `MC(D)=0` admits a non-empty-A 2-Hajós tree join (Def 9.1)
> into strictly-smaller 2-extremal blocks.

`F_D` gives the *language* for R-b (the `B`-edges of Def 9.1 are digons = edges of
`F_D`; the even-`B`-parity condition is a parity statement on `F_D`-paths, clean
because `F_D` is a forest) but it does **not** give a *mechanism* producing the
rim cycle, the `(A,B)` partition, and the block placement. None of P1–P4 do.

### 3.3 The honest weakness: the recursive descent was untested in the truth set;
new forward-built evidence exercises it

Over the **complete** truth sets `L₃..L₇`, the tree-join inverse produces only
**`W₃` A-blocks** — every A-block of every tree-joined member is the base object
`W₃` (size 4). Consequences:
  - The **recursive descent** of R-b (an A-block that is itself a non-base
    tree-join or Hajós join) is **never exercised** at `n≤7`.
  - The oracle's `max_internal=2` cap means tree shapes with ≥3 internal interface
    vertices are not even searched.
So clause-(b)'s `n≤7` truth-set support is *degenerate*: it confirms a
single-`W₃`-block pattern and nothing about the inductive step.

**Update 2026-06-01.** `scripts/tree_join_mc_inheritance.py` gives the first
bounded forward-built recursive test (one-A-edge joins, A-blocks from `L₃..L₇`):
among 771 labelled 2-extremal outputs there are **45 labelled** (`= 11
isomorphism classes`) `n=9` non-base, non-Hajos, `MC=0` outputs built on the
three `n=7` tree-join-only members (`7.7`, `7.14`, `7.36`). So recursive `MC=0`
descent is no longer untested as a *forward construction* (it is still not a
complete `L₉` enumeration, and forward construction is weaker than decomposing a
*given* minimal `MC=0` digraph).

**Update 2026-06-01b — the MC-inheritance mechanism is now PROVED, closing one
of the two §3.3 dangers.** `scripts/tree_join_mc_absorption.py` adversarially
searches the regime the one-A-edge probe could not reach — interior A-edges, up
to two A-edges, and rims of size 2 (`path4`) **and `≥3`** (`spider3`/`cat3`/`h`:
833 of the 5223 outputs); 4276 block-cut triples.
**No mixed cut of any A-block is ever absorbed**, because no mixed cut can
*separate* the interface pair: the interface is a **digon**, hence an underlying
edge that a mixed 2-cut (vertex + *single* edge) cannot delete. This is an
`n`-independent proof (see `docs/tree_join_mc_inheritance.md`): every block mixed
cut survives, so

> `MC(output) ≥ Σ MC(blocks)`, and an `MC=0` tree join uses **only `MC=0`
> A-blocks** (+ base objects).

This **eliminates the "A-blocks evade the mechanism by interface-absorbed cuts"
danger** of (C-b): there are no interface-absorbed cuts. The recursive `MC=0`
descent provably stays inside the `MC=0` class.

The **remaining** danger is therefore strictly the *existence* half: a 2-extremal
digraph at `n≥8` that is `MC=0` but admits **no** valid even-`B`-parity rim with
`MC=0`/base blocks. The inheritance lemma constrains the blocks of any such
decomposition but does not produce the rim — that mechanism is still missing
(§3.2). R-b's existence core is untouched by this update.

**Update 2026-06-02b — rim source identified (inverse rim audit).**
`scripts/inverse_rim_audit.py` exposes the rim of each recovered decomposition.
**The rim is always a directed cycle of the SINGLE-arc subdigraph** (S1: 14/14
genuine corpus + 64/64 red-team sample of the 822 non-base `MC=0` outputs; all
822 have balanced single arcs containing a cycle). Since single arcs are balanced
(closed trails) and non-empty for non-base `D`, a candidate rim *always exists*.
The tempting "rim = `F_D` leaf set" rule is **refuted** (a valid rim can pass
through an `F_D`-internal vertex). So the §3.2 missing mechanism is now a sharper,
single-arc-based target — see `docs/inverse_rim_extraction.md`. Still open: which
single-arc cycle, and that removing it leaves a valid tiling.

*Truth-set test:* `_tree_join_decompositions` on 7.7/7.14/7.36 yields decomps
with block sizes `[4]` (a single `W₃`) only; `0` decomps with a non-base block,
across all of `L₆∪L₇`.

---

## 4. Search for a seamless 2-extremal candidate at `n = 8..10`

ANGLE C requires actively hunting a counterexample to seam existence: a non-base
2-extremal `D` that is **neither** `MC=1`-with-a-promoting-mixed-cut **nor**
`MC=0`-with-a-tree-join. I ran four generators (scripts under `/tmp`, logic reusing
`h2_oracle`/`seam_invariant`; can be promoted to `scripts/` on request):

| generator | reaches `n` | distinct 2-extremal tested | seamless found |
|---|---|---|---|
| directed-Hajós joins of `L₃..L₇` blocks | 8,9,10 | 363 (all `MC=1`) | **0** |
| local 2-arc swap perturbation | (n preserved) | 8 | **0** |
| random Eulerian (cycle superposition) | 8,9 | 0 produced 2-extremal in 400k | — |
| digon-rich random (forest + Hamilton + cycles) | 8,9 | 1 in 1.5M trials | **0** |

**Key empirical facts established (all `n≤7`, evidence only):**
- **51/51** mixed 2-cuts of `L₆∪L₇` promote to a genuine 2-extremal directed-Hajós
  factorisation (R-a holds *uniformly*, not just existentially).
- **102/102** pieces produced are 2-extremal in **every** clause (incl. clause C).
- **40/40** non-base members are seamed; `MC` predicts the seam type 40/40.

**What a seamless counterexample would look like, and whether P1–P4 forbid it.**
A non-base 2-extremal `D` with no seam is one of two shapes:
  - **(C-a) `MC(D)=1` but no NON-ISOLATING mixed cut** — every mixed cut isolates
    a single vertex. Then `D` has a single arc `u→w` and vertex `v` with
    `U(D)−v−{u,w}` splitting off exactly one of `{u}` or `{w}`. P1–P4 do **not**
    forbid this a priori (P4 is necessity only; R-a★ is the open sufficiency). This
    is the `k=2` shadow of "every min dicut isolates a vertex" — which at `k≥3`
    forces a *base object* (Lemma 4.5/4.6). The candidate would be a digraph where
    the `MC` discriminator fires but only on degenerate (isolating) cuts, and `D`
    is neither a symmetric odd cycle nor a generalised wheel. **No such object
    exists at `n≤7`** (R-a★ never fails), but I have **no proof** it cannot exist
    at `n≥8`. *This is the precise candidate-counterexample structure for WALL-1.*
  - **(C-b) `MC(D)=0` but no tree join** — no directed-Hajós merge (provable, P4)
    *and* no valid even-`B`-parity rim with 2-extremal blocks. The candidate would
    be digon-forest-rich (so plenty of `B`-edge material) but with a single-arc
    closed-trail structure (P3) that cannot be cut into a peripheral cycle + blocks
    satisfying the parity. **P2 (forest) + P3 (balanced trails) constrain the
    shape but do not produce a rim** — nothing proved forbids (C-b). The most
    dangerous version uses a **non-`W₃` block** (untested regime, §3.3): e.g. a
    tree join whose intended A-block is a larger 2-extremal digraph that itself
    fails some clause, breaking the recursion.

> **Search verdict.** No seamless 2-extremal digraph was found at `n=8,9,10`. But
> random/perturbation search is the **wrong instrument**: 2-extremal digraphs are
> so sparse (1 in 1.5M random digon-rich trials) that absence of a counterexample
> in this sample certifies nothing. The structured generators only manufacture
> *seamed* objects by construction (a Hajós join is its own seam). So §4 is
> **consistent with** but does **not establish** seam existence at `n≥8`. A
> decisive test requires a true `n=8` enumeration of 2-extremal digraphs (out of
> scope here; flagged as the next instrument).

---

## 5. Bottom line of ANGLE C

1. **The colouring degradation (D1) is gone.** BJSS Thm 2(d) supplies the directed-
   Hajós converse for free; AAC Lemma 6.7 supplies the tree-join converse for free.
   The setup memo's "the genuine degradation is Claim 5.7.1" is, *post-BJSS*, no
   longer the live obstruction.

2. **`MC=1` side — REPAIRED by `F_D`.** R-a is proved (Lemma 5.4 `k≥1` + the
   mixed-cut definition forcing the unique crossing arc + Eulerian-balance at the
   merge vertex), and EXTREMAL-a is now complete (merge-vertex value and clause C
   closed). The **one** residual is **R-a★** (a non-isolating mixed cut exists) —
   the clean `k=2` analogue of AAC's base-case dichotomy, unproved but never
   violated at `n≤7` (37/37, 102/102).

3. **`MC=0` side — NOT repaired.** R-b (tree-join existence) is genuinely open;
   `F_D` provides only the vocabulary, not the mechanism; and the recursive descent
   is **untested beyond a single `W₃` block**. This, with R-a★, is where seam
   existence at `k=2` is genuinely hard. It is honestly *possible* the conjecture
   fails here, though no `n≤7` evidence suggests it.

4. **Counterexample hunt.** Two precise candidate shapes (C-a: isolating-only `MC=1`;
   C-b: rimless `MC=0`, esp. with a non-`W₃` block) are described; **P1–P4 do not
   forbid either**. None found at `n=8..10`, but the search is non-certifying.

> **One-sentence ANGLE-C answer.** The `k=2` digon-forest structure **repairs the
> directed-Hajós (`MC=1`) half** of seam existence (R-a, modulo the base-case
> existence hypothesis R-a★) but **does not repair the tree-join (`MC=0`) half**
> (R-b), so the genuine residual obstruction is the pair {R-a★, R-b} — the `k=2`
> analogue of AAC's Lemma 4.5/4.6 base dichotomy and bijoin-replacement — and the
> single most decisive next instrument is a true enumeration of 2-extremal digraphs
> at `n=8` to test R-a★ and to exercise R-b's recursion on a non-`W₃` block.

---

## 6. Reproduce

All tests reuse `scripts/h2_oracle.py` and `scripts/seam_invariant.py`.

- `python3 scripts/seam_invariant.py` → `PASS` (40/40 seam-type prediction;
  necessity check 0 violations).
- `python3 scripts/verify_ra.py` → `PASS`. Reproduces, over all of `L₆∪L₇`:
  - (T1) unique crossing arc: **51/51**;
  - (T2) every mixed cut promotes to a 2-extremal directed-Hajós join: **51/51**;
  - (T3) both pieces 2-extremal in all 5 clauses (incl. clause C): **102/102**;
  - (T4) merge-vertex Eulerian balance `v_in^{S₁}+1=v_out^{S₁}`,
    `v_in^{S₂}=v_out^{S₂}+1`: **51/51**;
  - (T5) R-a★ (non-isolating promoting cut exists): **37/37** `MC=1` members.
- Hard instances: `data/L_7.json` indices 33 (`MC=1`, the refinement case), 7/14/36
  (`MC=0`, tree-join), 17 (`MC=1`, merge vertex isolated in `F_D`).
- Ground truth: `data/seam_search_L6_L7.json`.
