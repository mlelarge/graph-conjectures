# Lemma A — strongest VERIFIED line, and the exact remaining hole

**Target.** Aboulker–Aubian–Charbit, arXiv:2304.04690, Conjecture 9.2: the class
`L` of 2-extremal digraphs equals the recursively-built class `H₂` (symmetric odd
cycles, closed under the directed Hajós join (Def 1.5) and the non-empty-A 2-Hajós
tree join (Def 9.1)).

**Lemma A (Seam Existence).** *Every 2-extremal digraph that is not a symmetric odd
cycle and not a generalised wheel admits a Lemma-A seam: either (a) a directed-Hajós
merge vertex, or (b) a non-empty-A 2-Hajós tree-join seam.*

This document assembles **only** steps that survived adversarial verification (the
five audit memos in `docs/verify_*.md`). Each step is tagged **[PROVED]** (airtight
mathematical argument), **[VERIFIED n≤7]** (reproduced computationally on the complete
truth sets `L₃..L₇`; evidence, **not** a theorem), or **[OPEN]**. The bottom line,
stated up front and defended below:

> **Lemma A is NOT proved.** What is proved is one direction of a discriminator
> (the *necessity* half: a Hajós merge vertex forces a computable invariant `MC=1`),
> plus the arc-decomposition scaffold it rests on. The *existence* of a seam — the
> actual content of Lemma A — is **OPEN**. So is its companion **Lemma B**. Therefore
> Conjecture 9.2 does **not** follow for general `n`; §5 states precisely what is
> missing.

---

## 1. The proved scaffold (arc decomposition)

Let `D` be 2-extremal: strong, Eulerian with in = out ≥ 2 at every vertex, underlying
simple graph `U(D)` 2-connected, edge-connectivity `λ(D)=2`, dichromatic number
`χ⃗(D)=3`.

**[PROVED] P2 — the digon graph is a forest.** *(survives the audit; 0/52 exceptions.)*
The digons (arcs whose reverse is present) form a subgraph `F_D` of `U(D)` that is
acyclic. — This is used purely as established structure below; the audits re-derived it
from the arc sets on all 52 members with no exception.

**[PROVED] P3 — single arcs are balanced closed trails.** Every non-digon arc is
*single* (reverse absent). At each vertex, single-in-degree = single-out-degree (since
total in = total out and digons contribute equally to both). Hence the single-arc
sub-digraph is balanced and decomposes into arc-disjoint **closed directed trails**.
Each single arc contributes exactly one undirected **single edge** to `U(D)`.

**[PROVED] No digon is a 2-arc-cut (Menger).** `D` strong with `U(D)` 2-connected ⇒
every vertex pair has two internally-disjoint underlying paths, so a single digon `{x,y}`
is never the only `x`–`y` connection. Consequently the strict literal reading of clause
(b) ("peel a 2-arc-cut digon") is **vacuous** — 0/40 non-base members of `L₆∪L₇` have
any 2-arc-cut digon. Clause (b) **must** be read in the general Def-9.1 tree-join sense
(seam distributed across the digon forest + ≥1 A-edge carrying a smaller block). This is
the load-bearing correction to the earlier `proof_attempt.md`.

These three facts are the *only* fully proved structural inputs. They constrain the
**shape** of `D`; they do not yet produce a seam.

---

## 2. The mixed-2-cut discriminator (one direction PROVED)

The audits agree (`verify_direct_structural.md`, `verify_criticality.md`,
`seam_invariant.md` S3.1) that the following invariant and its **necessity** direction
are a genuine theorem; its **sufficiency** direction is open.

> **Definition (mixed 2-cut).** A *mixed 2-cut* of `D` is a pair `(v, e)` where `v` is a
> vertex and `e={a,b}` is a **single** edge with `a,b ≠ v`, such that deleting both `v`
> and `e` disconnects `U(D)` — equivalently, `e` is a bridge of `U(D) − v`. Set
> `MC(D)=1` iff `D` has at least one mixed 2-cut, else `MC(D)=0`.

`MC(D)` is computable from `F_D` + the single edges alone (`scripts/seam_invariant.py`,
pure Python, no deps); it never calls the Hajós/tree-join decomposition routines.

**[PROVED] Necessity: a Hajós merge vertex ⇒ `MC(D)=1`.**
Suppose `D = D₁ *_v D₂` is a directed Hajós join at merge vertex `v` (Def 1.5). Then
there is a **single** join arc `(u,w)` and the vertex `v ≠ u,w` such that, after deleting
the underlying edge `{u,w}`, `v` articulates `U(D)` into the `S₁`-side (containing `u`)
and the `S₂`-side (containing `w`), with `S₁ ∩ S₂ = {v}` and every non-join arc inside
`S₁` or inside `S₂`. The join arc is single because a present reverse `(w,u)` would be a
second `A–B` crossing arc, contradicting uniqueness of the crossing arc (Lemma B0, §3) —
this closes the textual sub-step the audit flagged in `seam_invariant.md` S3.1 (verified
0/52 seams have a digon join arc). Deleting `v` leaves `{u,w}` as the only `S₁`–`S₂`
connection in `U(D)`; deleting `{u,w}` as well disconnects `U(D)`. Hence `(v,{u,w})` is a
mixed 2-cut and `MC(D)=1`. ∎

**[PROVED] Contrapositive (load-bearing for clause (b)).** `MC(D)=0 ⇒ D has no Hajós
merge vertex.` So any non-base member with `MC(D)=0` **provably** cannot be seamed by
clause (a); if it is seamed at all, it must be by clause (b). The three tree-join-only
members `7.7, 7.14, 7.36` all have `MC=0` and are therefore *provably* clause-(b)-only.

**[OPEN] Sufficiency: `MC(D)=1 ⇒` a genuine Hajós seam exists.** That the two underlying
sides `S₁,S₂` of a mixed 2-cut are *genuinely 2-extremal blocks* (and not merely an
underlying-graph cut) is **unproved**. This is the heart of the gap: a mixed 2-cut is a
cut of `U(D)`, and nothing proved here promotes it to a directed-Hajós factorisation.

**[OPEN] `MC(D)=0 ⇒` a tree-join seam exists.** Unproved; only the oracle's
membership test certifies it, and only on 3 members.

### Verification (reproduced this pass — evidence, not proof)

`python3 scripts/seam_invariant.py` ⇒ **PASS**:
- `L₆∪L₇` non-base (40 members): the rule `Hajós-seam ⇔ MC=1` is correct **40/40**.
  37 Hajós members all have `MC≥1`; the 3 tree-join-only members all have `MC=0`.
- `L₃..L₅` consistency (`MC=1` iff a genuine Hajós decomposition exists, via
  `h2_oracle._hajos_decompositions`): **all 5 consistent** — `L3.0`(C₃) `MC=0`,
  `L4.0`(W₃) `MC=0`, `L5.0`(non-base) `MC=1`, `L5.1`(gen-wheel) `MC=0`, `L5.2`(C₅) `MC=0`.
- Proved-direction check: **no** member is Hajós-seamed with `MC=0` — 0 violations.
- `MC=2` members are exactly those for which the oracle records two alternative Hajós
  seams — an independent cross-check that mixed-2-cut multiplicity tracks Hajós-seam
  multiplicity.

**Caveats the audits surfaced and that bound this evidence (not theorems):**
- The merge vertex `v` need not lie in `F_D` (member `7.17`: valid mixed 2-cut
  `(v=3, e={4,0})` with `v` isolated in `F_D`), so the invariant must be read on
  `U(D)` + the single/digon split, not "trails through forest leaves" only.
- `verify_minimal_counterexample.md` **refuted at n=7** the natural "interface-digon
  decomposition recipe" (member `7.33`: `MC=1`, both sides of both vertex 2-cuts are
  non-2-extremal, yet the true seam is a single-vertex Hajós join at `v=6` with single
  join arc `{0,5}`). So *sufficiency cannot be closed by the cut-pair recipe* — it needs
  a genuine seam-type case split that does not exist.
- All agreement is over `n ≤ 7`. Evidence, never a theorem.

---

## 3. Lemma B (reduction soundness) — partly PROVED, core OPEN

Lemma B is the converse-of-routine step: *if `D` splits at a Lemma-A seam, both pieces
`Dᵢ` are again 2-extremal* (so the induction descends into the truth set). Per
`verify_lemma_b.md` (every step re-tested on all of `L₃..L₇`, nothing FALSE):

**[PROVED], clause (a):**
- **B0** unique crossing arc (only `A–B` arc is `(u,w)`) — airtight; 0/52.
- join arc is **single** — corollary of B0; 0/52 digon joins.
- **(E)** `Dᵢ` Eulerian, in = out — airtight Eulerian set-balance; 0/52.
- **(S)** `Dᵢ` strong — airtight (Eulerian + weakly connected ⇒ strong); 0/104 pieces.
- **(Λ≤2)** `λ(Dᵢ)≤2` — airtight single-arc reroute; 0/4511 + 0/104.
- **(Λ≥2)** `λ(Dᵢ)≥2` — correct standard theorem (strong+Eulerian+min-deg-2 ⇒ no 1-arc
  cut); proof prose should be replaced by the closed-trail argument, but the claim holds;
  0/24437 random + 0/104.

**[PROVED modulo one line]** the `in=out ≥ 2` *value* at the merge vertex (needs
`vin_{S₁}≥1`): true and provable from strong + `λ=2`, but not isolated in the text.
Confirmed 0/52.

**[SKETCHED, not proved]** (C) underlying 2-connectivity of `Dᵢ` (clause a — only a
fan/Menger sketch); and **all** of (S),(C),(Λ≤2) for **clause (b)** (asserted "parallel
to clause a", never written line by line).

**[OPEN] — the real content of Lemma B: the dichromatic condition `χ⃗(Dᵢ)=3`.**
- **Conditional U** (`χ⃗(Dᵢ)≤3`): the added/interface arc could a priori push `χ⃗` to 4;
  no argument it does not. 110/110 pieces have `χ⃗=3` exactly — evidence only.
- **Conditional L** (`χ⃗(Dᵢ)≥3`, the load-bearing directed-Hajós-criticality gluing):
  two seam-agreeing ≤2-dicolourings must glue to a ≤2-dicolouring of `D`; directed
  acyclicity of the colour classes across the seam is **not** verified. This is the
  digraph analogue of the classical Hajós lower bound and is genuinely **OPEN**.
  Adversarial searches (1680 χ-violating joins; 4.16M broken-piece joins; full `L₃..L₇`
  exhaustion) produced **no counterexample and no proof**.

**[WEAKNESS the audit surfaced]** Clause (b)'s empirical support is **degenerate**:
over the complete truth sets the tree-join inverse yields only 6 A-blocks and **every one
is the base object W₃**. The non-trivial recursive descent for clause (b) is therefore
**never exercised**, and the oracle's `max_internal=2` cap means larger tree shapes are
not even searched. Treat clause (b)'s conditions as essentially **untested** on
non-trivial blocks, not "0-failure verified".

`python3 scripts/lemma_b_checks.py` ⇒ **PASS** (B0/E/S/Λ on 104 Hajós pieces + 6
tree-join blocks; merge-vertex degree split 0 violations).

---

## 4. Answers to the three questions

**(1) Is Sub-lemma A′ / Lemma A PROVED?** **NO.** The strongest *proved* facts are the
arc-decomposition scaffold (§1) and the **necessity** half of the mixed-2-cut
discriminator (§2): *Hajós merge vertex ⇒ MC=1*, equivalently *MC=0 ⇒ no Hajós seam*.
These prove only the **seam TYPE constraint**, never **seam EXISTENCE**.

> **Smallest remaining hole (the exact open step):**
> Prove the **sufficiency** direction of the discriminator. Concretely, for a non-base
> 2-extremal `D`:
> **(A′-suff-a)** `MC(D)=1 ⇒` some mixed 2-cut `(v,{u,w})` actually exhibits `D` as a
>   directed Hajós join of two *strictly-smaller 2-extremal* digraphs (i.e. the two
>   `U(D)`-sides are genuine 2-extremal blocks, not merely a cut); **and**
> **(A′-suff-b)** non-base `D` with `MC(D)=0 ⇒` `D` has a non-empty-A 2-Hajós tree-join
>   into strictly-smaller 2-extremal blocks.
> Note `MC(D)∈{0,1}` is **always** decidable, so (A′-suff-a)∨(A′-suff-b) **is** Lemma A.
> The hole is converting a *cut of `U(D)`* into a *2-extremal factorisation of `D`* —
> and the n=7 member `7.33` proves the obvious cut-pair recipe does not do it.

**(2) Is Lemma B proved?** **NO — only partly.** Clause-(a) structural conditions
`E, S, Λ` are airtight theorems; `(C)` clause-(a) and all of clause-(b) are sketches;
and the dichromatic condition `χ⃗=3` — **Conditional U and the load-bearing Conditional
L (Hajós-criticality gluing)** — is **OPEN in both clauses**. So Lemma B does not yet
certify that a split yields 2-extremal pieces.

**(3) Does Conjecture 9.2 follow for general `n`?** **NO.** The intended induction is:
> *Base:* symmetric odd cycles and generalised wheels are in `H₂` (this part is sound:
> `_is_generalised_wheel` is a SOUND, cap-free recognizer — see STATUS §1).
> *Step:* a non-base 2-extremal `D` on `n` vertices has a seam **(Lemma A)** splitting it
> into pieces `Dᵢ` with `|Dᵢ|<n`, each of which is again 2-extremal **(Lemma B)**; by
> the induction hypothesis each `Dᵢ ∈ H₂`; the `H₂` constructor that defines the seam
> then re-assembles `D`, so `D ∈ H₂`.
>
> This induction **requires both Lemma A and Lemma B**, and **neither is proved**:
> - Lemma A is missing seam *existence* (§2 sufficiency).
> - Lemma B is missing the *χ⃗=3 preservation* (§3 Conditional L) — without it a split
>   piece need not be 2-extremal, so even granting a seam the induction hypothesis does
>   not apply, and the re-assembly direction (Conditional L) is itself the Hajós lower
>   bound that is unproved.
>
> Every "in-`H₂`" verdict for `n≤7` is the **sound-but-incomplete** oracle confirming
> membership (it never produces a spurious membership), not a proof of the induction.
> All agreement is `n≤7`; there is **no argument bounding behaviour for `n≥8`.**

**Honest bottom line.** Over the complete truth sets `L₃..L₇` (52 digraphs, 41 non-base)
there is **no counterexample and no missing `H₂` constructor**: every non-base member is
seamed (38 Hajós + 3 tree-join) and lies in `H₂`. The conjecture's *empirical* status is
maximally favourable. But the **proof** reduces to exactly two open theorems —
**mixed-2-cut sufficiency (Lemma A)** and **χ⃗=3 gluing (Lemma B / Conditional L)** —
and empirical survival to `n≤7` is **evidence, not a theorem**.

---

## 5. The single most decisive next step

**Prove Conditional L** — that two seam-agreeing 2-dicolourings glue to a 2-dicolouring
of `D` (directed acyclicity of colour classes across the seam). This single directed
Hajós-criticality lower-bound lemma is the common load-bearing core: it is the open heart
of Lemma B, and the same `χ⃗=3`-preservation argument is exactly what would promote a
mixed 2-cut from a *cut of `U(D)`* to a *genuine 2-extremal Hajós factorisation*,
closing the sufficiency hole in Lemma A as well. Settle Conditional L and both walls fall
together; leave it open and `n≤7` remains evidence only.

---

### Files (all pure Python, no deps; reproduced this pass)
- `scripts/seam_invariant.py` — `MC`, the rule, full harness (§2). `PASS`.
- `scripts/lemma_b_checks.py` — B0/E/S/Λ + merge-vertex split (§3). `PASS`.
- `scripts/h2_oracle.py` — sound (incomplete off empty-A) membership oracle.
- Audits: `docs/verify_seam_invariant`(in `seam_invariant.md`),
  `docs/verify_direct_structural.md`, `docs/verify_criticality.md`,
  `docs/verify_lemma_b.md`, `docs/verify_minimal_counterexample.md`.
- `tests/test_seam_invariant.py`, `tests/test_h2_oracle.py`.
