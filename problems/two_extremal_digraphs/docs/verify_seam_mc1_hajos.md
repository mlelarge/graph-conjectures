# Adversarial verification of `seam_mc1_hajos.md` (Theorem A1 = SUFF-a, MC=1 Hajós seam)

**Auditor stance:** skeptical. A step is **PROVED** only if it is an airtight
mathematical argument; agreement over `L₃..L₇` is EVIDENCE, never proof.
Every structural claim was re-tested from scratch with the sound primitives of
`scripts/h2_oracle.py` against **every** mixed 2-cut of **every** non-base member
of `L₃..L₇` (52 mixed cuts over 42 non-base members; `|L₅|=3, |L₆|=8, |L₇|=39`).
Verdict legend: **PROVED** / **EMPIRICAL-ONLY** / **CITED (verified)** / **FALSE**.

## Bottom line

**Theorem A1 SURVIVES.** No step is FALSE; no empirical test produced a single
exception across all 52 mixed cuts. The memo's central advance — replacing the
OPEN `k=2` colouring gap (the load-bearing (X)-L hole of `verify_lemma_b.md`)
with a *wholesale criticality import at `k=3`* via BJSS Thm 2(d) — is **logically
sound** and is the genuine contribution. Every structural sub-claim that I could
attack was re-derived independently and held. The honest residue is exactly two
external imports (both genuine theorems, primary-source verified) plus two prose
steps written at "careful sketch" level (§2.4, §2.5-lower) whose conclusions I
nonetheless confirmed both logically and on all 52 instances.

This memo proves **SUFF-a only**. Lemma A = SUFF-a ∨ SUFF-b still needs SUFF-b
(MC=0, tree-join) closed independently; the memo says so correctly.

---

## Summary table

| Step | Claim | Logic verdict | Computational verdict |
|---|---|---|---|
| Lemma 1 | bridge of `U(D)−v` ⟺ `v` separates `u,w` in `U(D)−e`; `{u,w}` unique crossing | **PROVED** (airtight) | 0/1172 mismatches; 0/52 extra-crossing |
| Cor. 1 | mixed cut ⇒ AAC Def 1.5 data, join arc single, both `<n` | **PROVED** (corollary of Lemma 1) | 0/52 |
| §2.1 | `Dᵢ` Eulerian, in=out | **PROVED** (set-balance) | 0/52 |
| §2.2 | in=out≥2 at `v` (`vin_{S₁}≥1` via λ=2 1-dicut) | **PROVED** | 0/52 (`vin_{S₁}≥1`, `vout_{S₂}≥1`, deg≥2 both pieces) |
| §2.3 | `Dᵢ` strong | **PROVED** (airtight) | 0/52 (via `is_2extremal`) |
| §2.4 | `U(Dᵢ)` 2-connected (cut vertex ⇒ separates endpoint from `v`) | **PROVED** (sketch-level prose, conclusion airtight) | 0/52 cut-vertex; 0/52 pieces 2-conn |
| §2.5 ≤ | `λ(Dᵢ)≤2` | **PROVED** (airtight given single-arc) | 0/52 (`λ(piece)==2`) |
| §2.5 ≥ | `λ(Dᵢ)≥2` | **TRUE THEOREM** (prose terse, claim standard) | 0/52 |
| §2.6 | `χ⃗(Dᵢ)=3` | **CITED** BJSS Thm 2(d) @ k=3 | 0/52 (pieces 3-dicritical, not just χ⃗=3) |
| Thm A1 | EVERY mixed cut ⇒ two strictly-smaller 2-extremal pieces | **PROVED** modulo the cited imports | **52/52** Test R |

---

## Per-step audit

### Lemma 1 (bridge ⟺ separation; unique crossing edge) — **PROVED**
The argument is airtight and uses only: (i) `U(D)−v` connected (D is 2-connected,
so deleting one vertex leaves a connected graph — standard); (ii) in a connected
graph an edge is a bridge iff its removal splits it, with the two endpoints in the
two new components. The "unique crossing edge" conclusion follows because any
other `S₁∖{v}`–`S₂∖{v}` edge would survive in `U(D)−v−e` and reconnect.
**Computational:** over **1172** `(v, single-edge e)` pairs of all non-base
`L₃..L₇`, predicate "e bridge of `U(D)−v`" agreed with "v separates endpoints of
e in `U(D)−e`" with **0 mismatches**; for each of the 52 mixed cuts the single
edge `e` was the **unique** `U(D)`-edge crossing `S₁∖{v}`–`S₂∖{v}` (0 failures).
This is a genuine theorem, not n≤7 evidence.

### Corollary 1 (Hajós data; join arc single; both `<n`) — **PROVED**
Mechanical from Lemma 1: the AAC Def 1.5 inverse hypotheses (single join arc
`(u,w)`, split `v∉{u,w}`, `S₁∩S₂={v}`, `S₁∪S₂=V`, every non-join arc inside one
side) are forced. The join arc is single because `e` is single *by definition of
mixed 2-cut* — this is genuinely built into the invariant, not an after-the-fact
hope. **NOTE on "Test 0":** the memo's claim that the mixed-2-cut set and the
realized-Hajós-seam set "coincide exactly" is, given Lemma 1, essentially
*tautological* — `mixed_2_cuts(D)` and the single-join-arc branch of
`_hajos_decompositions(D)` compute the same separation predicate. I re-checked it
anyway (0/40 mismatches on `L₆∪L₇`), and cross-checked against the independent
ground-truth `has_hajos_seam` flag in `seam_search_L6_L7.json` (0/40
disagreements with MC). So Test 0 is correct, but it is a *consistency* check, not
new evidence for genuineness — genuineness is Test R.

**Minor imprecision (not an error):** the memo says "37/37 members" for Test 0.
There are **40** non-base members in `L₆∪L₇`; 37 carry a Hajós seam (MC≥1) and 3
are tree-join-only (MC=0). The coincidence is over those 37; the phrasing "37/37
members" conflates "members tested" with "MC≥1 members". Substance is correct.

### §2.1 Eulerian — **PROVED**
Set-balance plus the fact that `(u,w)` is the unique crossing arc (Cor. 1).
Re-adding `(u→v)` to the `S₁` side restores balance at `v`; every other vertex
keeps its `D`-degree. Airtight. 0/52 computationally.

### §2.2 in=out≥2 at `v` — **PROVED** (this closes prior gap #7)
The new content is `vin_{S₁}≥1`: if every in-neighbour of `v` lay in `S₂`, then
`∂⁻(S₁∖{v})={(u,w)}` is a 1-arc dicut, contradicting `λ(D)=2`. This is a correct,
self-contained argument and genuinely isolates the step `verify_lemma_b.md` left
at sketch level. The Eulerian identity then upgrades `vin_{S₁}≥1` to
`vout_{S₁}=vin_{S₁}+1≥2`. **Computational:** `vin_{S₁}≥1`, `vout_{S₂}≥1`, and
in=out≥2 at `v` in **both** pieces — 0/52 exceptions.

### §2.3 strong — **PROVED**
Eulerian + connected underlying ⇒ strong (each weak component of an Eulerian
digraph is strong; standard). `U(D₁)` connected since `S₁∖{v}` is one component of
`U(D)−v−e` and `v` has ≥1 neighbour there (§2.2). Airtight.

### §2.4 `U(Dᵢ)` 2-connected — **PROVED (conclusion); prose at sketch level**
The claim "every cut vertex `c` of `U(D[S₁])` separates `u` from `v`, so adding
`{u,v}` kills all cut vertices" is **correct**, but the written proof of the
component-isolation step is terse (the author flags this honestly). I verified the
logic and the conclusion independently and completely:
- For every mixed cut, I computed the cut vertices of `U(D[S₁])` (resp. `U(D[S₂])`)
  *without* the added edge and checked each one separates `u` (resp. `w`) from `v`
  in the underlying induced graph: **0/52 failures**.
- I recomputed `is_2connected` on both reconstructed pieces *with* the added edge:
  **0/52 failures** (104 pieces).
Member **7.19** is the genuine witness: `U(D[S₁])` for cut `(v=4,{0,5})` is NOT
itself 2-connected (cut vertex 6), and the added edge `{0,4}` repairs it — exactly
as the memo claims. So clause (C), previously the "sole §2 sketch" of
`verify_lemma_b.md`, is now correct. A referee would still want the
component-isolation step spelled out with explicit block-tree/Menger language; I
treat the conclusion as proved because I verified both the logic and all instances.

### §2.5 `λ(Dᵢ)=2` — **PROVED (≤) / TRUE THEOREM (≥)**
*Upper:* the reroute argument (use `(u→v)` at most once, divert via `(u,w)` + a
`w⇝v` detour in the strong `D[S₂]`) is airtight given the unique-single-arc
structure. *Lower:* "strong Eulerian with `δ⁺≥2` has no 1-arc dicut" is a correct
standard theorem (a 1-arc out-cut forces by balance a 1-arc in-cut, and a closed-
trail decomposition traps a second out-arc). The prose is terse but the claim is
true and not a conjecture. **Computational:** `λ(piece)==2` for all 104 pieces,
0 failures (independent of the `is_2extremal` filter).

### §2.6 `χ⃗(Dᵢ)=3` — **CITED (BJSS Thm 2(d)), verified** — the key advance
This is the load-bearing replacement for the OPEN (X)-L hole of
`verify_lemma_b.md`. The logic: D is 2-extremal ⇒ 3-dicritical (AAC Lemma 4.1,
k=2); D = D₁ ▽ D₂ is a genuine directed Hajós join (Cor. 1); BJSS Thm 2(d) at
**k=3** gives both pieces 3-dicritical, hence `χ⃗=3`. **No `k=2` colouring move is
performed**, so the AAC `k=2` palette-exhaustion (Claim 5.7.1) never arises. This
is logically sound. Verifications I performed:
- The BJSS Thm 2(d) quote in the memo ("If `D` is `k`-critical and `k ≥ 3`, then
  both `D₁, D₂` are `k`-critical") matches **verbatim** the primary-source-verified
  statement in `docs/conditional_l_literature.md` §"Independent citation
  verification (2026-05-30)". The `k≥3` hypothesis is satisfied (k=3).
- The orientation convention `D₁=D[S₁]+(u→v)`, `D₂=D[S₂]+(v→w)` matches BJSS
  Def 1.5 verbatim (`uv₁∈A(D₁)`, `v₂w∈A(D₂)`, identify, add `uw`) — quoted in the
  same literature doc. The memo and `_induce_plus` agree with this.
- AAC Lemma 4.1 (k-extremal ⇒ (k+1)-dicritical) is the correct cited source for
  "D is 3-dicritical".
- **Stronger empirical confirmation than the memo claims:** I verified each D is
  3-*dicritical* (χ⃗=3 AND every vertex-deletion drops χ⃗), and each reconstructed
  piece is 3-dicritical — not merely χ⃗=3 — **0/52 failures** on both pieces.
This step is correctly tagged CITED, and the citation is accurate. It is the right
fix and it lands.

### §2.7 / Thm A1 — **PROVED modulo the two cited imports**
Assembling §2.1–§2.6 gives 2-extremality of both strictly-smaller pieces. **Test R
(the master test): every one of the 52 mixed cuts reconstructs, via Cor. 1, into
two pieces that are EACH 2-extremal recomputed from scratch (`is_2extremal`:
strong + 2-connected + λ=2 + χ⃗=3) and strictly smaller — 52/52, 0 failures.**

---

## The existence question (the hard part) — **PROVED, not merely observed**

The task's central worry is: is "some mixed 2-cut works" *proved* or only *seen on
n≤7*? Theorem A1's design answers this. The existence of a usable seam is NOT an
empirical observation here:
- The hypothesis `MC(D)=1` literally *means* a mixed 2-cut exists.
- Lemma 1 + Cor. 1 turn **every** mixed 2-cut, unconditionally, into valid Hajós
  data. There is no search and no "right one" to find — the construction is
  total over mixed cuts and keyed off the single edge `e`, which is why member
  **7.33** (whose naive vertex-2-cut-pair recipe fails on both vertex 2-cuts) is
  handled: its unique mixed cut `(v=6, e={0,5})` with single arc `(5,0)`
  reconstructs directly. I verified 7.33's data exactly (digons and singles match
  the memo; unique mixed cut `(6,{0,5})`; `(5,0)∈A`, `(0,5)∉A`) and the
  reconstruction yields two 2-extremal pieces.
So existence is reduced to the *hypothesis* MC=1; the genuineness of the pieces is
the proved part. The n≤7 tests confirm but do not carry the argument. This is a
real strengthening over the conjectural `seam_invariant.py` status (which left
"MC=1 ⇒ genuine Hajós merge" CONJECTURAL): the memo upgrades it to a theorem.

---

## Honest residue (what is NOT closed)

1. **Scope:** SUFF-a only. Lemma A still needs **SUFF-b** (MC=0 ⇒ non-empty-A
   tree-join into strictly-smaller 2-extremal blocks) proved independently. The
   memo states this. Members **7.7, 7.14, 7.36** (MC=0) are correctly out of scope
   here.
2. **Two cited imports** (genuine theorems, not re-derived):
   (i) **BJSS Thm 2(d)** for `χ⃗(Dᵢ)=3` — primary-source verified, quote exact,
   k≥3 hypothesis met. (ii) The two standard facts "Eulerian ⇒ strong iff weakly
   connected" and "strong Eulerian `δ⁺≥2` ⇒ no 1-arc dicut" (§2.3, §2.5-lower).
3. **Exposition gaps (not logical holes):** §2.4's component-isolation step and
   §2.5's λ≥2 prose are at "careful sketch" level. I confirmed both the logic and
   all 52 instances, so I rate them PROVED, but a referee would ask for the §2.4
   step in explicit block-tree/Menger language.
4. **Test 0 is a tautology-grade consistency check**, not independent evidence for
   genuineness (Lemma 1 makes MC-set ≡ single-arc-Hajós-seam-set by construction).
   The genuineness evidence is Test R. The memo slightly over-sells Test 0 as "MC
   enumerates the seams" — true, but it is true *by Lemma 1*, not as an empirical
   discovery.

## Reproduction / environment
All tests are pure Python reusing `scripts/h2_oracle.py`
(`is_2extremal`, `_hajos_decompositions`, `_component`, `_induce_plus`,
`is_2connected`, `lambda_D`, `chi_vec`) and `scripts/seam_invariant.py`
(`mixed_2_cuts`, `split_digons_singles`, `MC`). Regression
`python3 scripts/seam_invariant.py` ⇒ `PASS (40/40 + consistency)`. No `.venv`
created. Counts: 52 mixed cuts over 42 non-base members of `L₃..L₇`; 1172
`(v, single-edge)` pairs for Lemma 1; all reconstructions cross-checked with a
from-scratch `is_2extremal` and a from-scratch 3-dicriticality check.

**Verdict: Theorem A1 (SUFF-a) survives this adversarial pass. No FALSE step. The
χ⃗=3 fix via BJSS@k=3 is sound and is the real contribution. SUFF-b remains the
open half of Lemma A.**
