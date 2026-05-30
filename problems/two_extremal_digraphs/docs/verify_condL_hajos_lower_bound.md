# Adversarial verification of `proof_condL_hajos_lower_bound.md`

**Verdict.** The note's three load-bearing propositions — Prop 3.1 (lower bound),
Prop 4.1 (gluing), Prop 4.2 (criticality descent) — are **rigorously PROVED**, and
the citation (BJSS 2020 Theorem 2) is **correctly quoted** and matches what is used.
I could not break any step logically or computationally. The note is also **honest
about its boundary**: it does NOT close Conditional L in general; it closes only the
single-arc / single-identified-vertex (literal directed Hajós) instance. The two
open items it declares (tree-join seam; cut⇒factorisation) are genuinely open and
correctly flagged. **Net: this is a correct, sound contribution — but it proves a
THEOREM THAT WAS ALREADY PUBLISHED (BJSS Thm 2), not the live open core of the
project.** The project's real walls remain standing.

Tags: **[PROVED]** rigorous; **[CITED-OK]** citation verified; **[EVIDENCE]**
n≤7-style support only; **[OPEN]** not closed.

---

## 1. Citation audit — [CITED-OK]

§2 of the note quotes BJSS, Electron. J. Combin. 27(1) (2020) #P1.63
(arXiv:1908.04096), **Theorem 2(a)–(d)**. Cross-checked verbatim against
`docs/conditional_l_external_lit.md`, which transcribes the EJC PDF directly:

- Thm 2(a) `χ⃗(D) ⩾ min{χ⃗(D₁),χ⃗(D₂)}` — matches note's (L▽-lb). ✓
- Thm 2(b) `χ⃗(D₁)=χ⃗(D₂)=k≥2 ⇒ χ⃗(D)=k` — matches (L▽-glue). ✓
- Thm 2(c)/(d) criticality both directions — matches (L▽-crit). ✓
- BJSS directed Hajós join definition (delete `u₁v₁`,`v₂u₂`, identify `v₁=v₂=v`,
  add `u₁u₂`) is definitionally **identical** to Def 1.5 with `u₁=u`, `u₂=w`. ✓
- BJSS's `χ⃗` (Neumann-Lara: colour classes induce acyclic subdigraphs) = the
  project's `χ⃗`. ✓
- BJSS's own 5-line proof of 2(a) (quoted in the external-lit memo) uses the splice
  `C₁∪C₂ − u₁v₁ − v₂u₂ + u₁u₂` — the SAME cycle the note's Prop 3.1 reconstructs.

The note does NOT depend on the citation for correctness (it reproves 2(a),(b),(d)
from scratch); the cite is provenance. **No misquote, no phantom theorem number.**
The one residual caveat the note itself states honestly: neither it nor I re-fetched
the BJSS PDF in THIS pass — the verbatim text comes from two prior literature memos.
Since §3–§4 are self-contained reproductions, the project does not rest on the cite.
**[CITED-OK]**, with that caveat noted.

Independent corroboration of the citation chain: `conditional_l_literature.md`
confirms the SOURCE paper (2304.04690) itself invokes BJSS Thm 2 as its
"Claim 5.3.1 (Theorem 2 in [3])", and that "2-extremal ⇒ Eulerian + 3-dicritical"
is its **Lemma 4.1** (k≥1 general, l.488). So §5.2's reconciliation
(2-extremal ⇒ 3-dicritical ⇒ Prop 4.2 applies) rests on a real in-paper lemma. ✓

---

## 2. Logical audit of the from-scratch proofs

### 2.1 Prop 3.1 (lower bound) — [PROVED], airtight

Take a `k`-dicolouring `φ` of `D` (`k=χ⃗(D)`). Restrict to each side, fixing `φ(v)`.

- If both restrictions fail: each factor has a mono dicycle forced through its
  deleted interface arc (because `D[Sᵢ]⊆D` is correctly coloured, so the only
  illegal arc available is the re-added interface arc). Peel it off to get
  `P₁: v⇝u` in `S₁` and `P₂: w⇝v` in `S₂`, all colour `α := φ(u)=φ(v)=φ(w)` (the
  three are forced equal because both interface arcs are monochromatic and share
  `v`). The splice `W=(u→w)·P₂·P₁` is a **closed directed walk** in `D`, all colour
  `α`, using the join arc `u→w` (present in `D`) and the identified vertex `v`. A
  closed directed walk contains a directed cycle ⇒ a mono dicycle in a colour class
  of `φ` ⇒ contradicts `φ` valid on `D`.

**Checks I tried to break it with, all pass:**
- *Is `u→w` in `D`?* Yes, it is the join arc. ✓
- *Does the walk need `P₁,P₂` disjoint?* No — a CLOSED directed walk contains a
  directed cycle regardless of repeated vertices. The note states this correctly
  ("a closed directed walk in a digraph contains a directed cycle"). This is the
  exact place the directed subtlety (acyclic ≠ independent) lives, and it is handled
  correctly: `P₁,P₂` are honest dipaths inside a class; only the closed `W` is
  forbidden. **This is the cross-seam acyclicity that `lemma_a_proof.md` §3 flagged
  "not verified" — it is now verified.** ✓
- Identical to BJSS's published proof of 2(a). ✓

**Verdict: PROVED.** No gap.

### 2.2 Prop 4.1 (gluing) — [PROVED], airtight

`≥` is Prop 3.1. For `≤`: permute `φ₂`'s colours so `φ₂(v)=φ₁(v)` (ok, `k≥2`), glue.
A mono dicycle `C` of the glued `φ` is (i) inside `S₁` ⇒ contradicts `φ₁`; (ii) inside
`S₂` ⇒ contradicts `φ₂`; or (iii) uses the unique cross arc `u→w`, hence enters `S₂`
at `w` and must return to `S₁` through the only shared vertex `v`, giving a `w⇝v`
sub-dipath `Q₂` in `S₂`; then `Q₂+(v→w)` is a mono dicycle of `D₂`, contradicting `φ₂`.
Each case contradictory ⇒ `φ` valid. **Sound; the "return through `v`" step is forced
because `v` is the only `S₁`–`S₂` shared vertex and `u→w` the only cross arc.** ✓

### 2.3 Prop 4.2 (criticality descent) — [PROVED], airtight despite messy prose

The §4.2 prose contains visible self-corrections ("but we must be careful — see
Step 1′", a literal "wait"), but the ARGUMENT it lands on is rigorous:

- **Step 1′ (each factor `χ⃗ ≥ m`):** `D` is `m`-dicritical, so `D[S₁]=D₁−(u→v)`
  and `D[S₂]` are proper subdigraphs with `χ⃗ ≤ k=m−1`; fix `ψ₂` a `k`-dicolouring
  of `D[S₂]`. If `χ⃗(D₁)≤k`, take `χ₁` of `D₁`, permute `ψ₂` to agree at `v`, glue.
  A mono dicycle is inside `S₁` (⊥`χ₁`), inside `S₂` (⊥`ψ₂`), or through `u→w`
  giving `Q₁: v⇝u` in `S₁` with `Q₁+(u→v)` a mono dicycle of `D₁` (⊥`χ₁`). So the
  glue is valid, `χ⃗(D)≤k<m`, contradicting `m`-dicriticality. Hence `χ⃗(D₁)≥m`,
  symmetrically `χ⃗(D₂)≥m`. **Correctly uses the CRITICAL hypothesis (the `ψ₂` on a
  proper subdigraph), not a circular "`χ⃗(D₂)≤k`" assumption.** ✓
- **Step 2 (each factor `χ⃗ ≤ m` and arc-critical):** BJSS's clean route — for every
  arc `a` of `D₂` present in `D`, `D−a = D₁▽(D₂−a)` is a proper subdigraph of the
  `m`-critical `D`, so `χ⃗(D−a)≤m−1`; Prop 3.1 gives `χ⃗(D−a)≥min{m,χ⃗(D₂−a)}`, so
  `χ⃗(D₂−a)≤m−1` for every arc. With `χ⃗(D₂)≥m`, `D₂` is `m`-dicritical, so
  `χ⃗(D₂)=m`. Symmetric for `D₁`. ✓
  - *Minor slack:* "vertex-deletion criticality follows by deleting all arcs at a
    vertex" is glib but correct — vertex deletion removes ≥1 incident arc, and
    arc-criticality already forces `χ⃗ < m` after any single arc deletion.
  - The interface arc `v→w` is not in `D`, so `a` ranges only over arcs actually in
    `D`; `D₂−a` keeps the interface, so `D₁▽(D₂−a)` is well-defined. ✓
- **Converse (BJSS 2c):** both factors `m`-dicritical ⇒ `D` `m`-dicritical, proved
  analogously (Prop 4.1 + arc-deletion case split on factor vs join arc). ✓

**Verdict: PROVED.** The messy exposition is a presentation defect, not a logical
gap. (Recommend cleaning the "wait"/false-start prose, but the math is sound.)

---

## 3. Computational stress tests (EVIDENCE — reused h2_oracle.py primitives)

I went beyond the note's own `cond_l_hajos_lb_check.py` (which only joins symmetric
odd cycles + a small randomised pool) and tested over **arbitrary small digraphs**.

`scripts/adv_condL_hajos_lb.py` (broad random factors on 2–4 vertices):
```
Prop 3.1 lower bound :  60000 joins ; FAILURES 0
Prop 4.1 gluing eq.  :  12679 joins (chi1==chi2>=2) ; FAILURES 0
Prop 4.2 converse 2c :   3339 cases ; FAILURES 0
Prop 4.2 descent 2d  :   3339 cases ; FAILURES 0
```

`scripts/adv_condL_splice.py` (the LOAD-BEARING Claim of Prop 3.1: every valid
`k`-dicolouring of the join has ≥1 valid side-restriction — the splice never fires
when `φ` exists), FULL enumeration of dicolourings:
```
k=2 :  30342 (phi,join) pairs ; both-restrictions-fail-yet-phi-valid = 0
k=3 : 415134 (phi,join) pairs ; both-restrictions-fail-yet-phi-valid = 0
```

`scripts/cond_l_hajos_lb_check.py` (the note's own): **PASS** (256 + 400 joins).

**No counterexample at any scale tested.** This is consistent with the proof being
correct — but it is EVIDENCE only; the theorem stands on §2 of this report (the
logical audit), not on these runs.

---

## 4. What is NOT closed — the honest boundary (the note states this correctly)

The note is **not over-claimed**: its title and §5 explicitly restrict to the
directed-Hajós (single-arc/single-vertex) instance. I confirm the two declared gaps
are genuinely open:

1. **[OPEN] Tree-join seam (Conjecture 9.2 clause b).** Prop 3.1's splice `W` is a
   single added arc + single identified vertex. The Def-9.1 tree join glues across a
   digon forest + peripheral directed cycle + ≥1 A-block — a MULTI-seam. The note
   does NOT reprove the lower bound there; it only CITES Lemma 6.7 of 2304.04690 for
   `k=2`. A from-scratch multi-seam splice is deferred. This is the live half of
   Conditional L per `conditional_l_external_lit.md` §4. **Correctly flagged OPEN.**

2. **[OPEN] Cut ⇒ factorisation (Lemma A sufficiency).** No colouring theorem
   recognises a Hajós join from a `U(D)` mixed-2-cut. The note assumes `D=D₁▽D₂` is
   GIVEN. Promoting a cut to a 2-extremal factorisation is the structural hole
   (`lemma_a_proof.md` §4; refuted recipe at member 7.33). Open even in the source at
   `k=2` (its decomposition Thm 5.1 is `k≥3` only). **Correctly flagged OPEN.**

3. **[caveat, correctly noted]** Prop 4.2 descends 3-DICRITICALITY, not full
   2-extremality (strong / 2-conn underlying / λ=2). Those structural clauses are
   the separate Lemma B bookkeeping, not this note. The note says so.

---

## 5. The one substantive criticism (framing, not correctness)

The note's correctness is not in dispute. The substantive issue is **what it buys
the project**:

- `lemma_a_proof.md` §3 listed Conditional L's lower-bound half as "genuinely OPEN…
  no proof over the 1680/4.16M search". The note correctly diagnoses this as a
  **misidentification**: that half is BJSS Thm 2(a), a published 5-line theorem. The
  team was chasing an existing result. **This correction is valuable and correct.**
- BUT the note's reconciliation that "this CLOSES the `χ⃗(Dᵢ)=3`-preservation
  (Conditional L) for clause (a)" is true ONLY for clause (a) = a LITERAL directed
  Hajós seam on a 3-dicritical `D`. Per `lemma_a_proof.md` §5, the load-bearing
  induction step is the COMMON CORE across BOTH Lemma A seam-sufficiency AND Lemma B.
  The genuinely open content (tree-join lower bound from scratch; cut⇒factorisation)
  is untouched. **So the "open heart" of Conjecture 9.2 is NOT closed by this note;
  the directed-Hajós SUB-instance of it is — and that sub-instance was already a
  citable theorem.** The note's own §5/self-declared gaps say exactly this; I am
  confirming it, not contradicting it.

**Bottom line.** Everything tagged [PROVED] in the note IS rigorously proved (I could
not break it logically or over 0.5M computational instances), and the citation is
clean. The note does precisely what it claims — and honestly states that it does not
close the project's live walls. It is airtight on its stated scope; its stated scope
is a published theorem, not the open frontier.

---

### Files
- `docs/verify_condL_hajos_lower_bound.md` — this audit.
- `scripts/adv_condL_hajos_lb.py` — broad-factor stress of Prop 3.1/4.1/4.2 (0 fails).
- `scripts/adv_condL_splice.py` — full-enumeration test of Prop 3.1's Claim (0 fails).
- Audited: `docs/proof_condL_hajos_lower_bound.md`, `scripts/cond_l_hajos_lb_check.py`.
- Cites cross-checked: `docs/conditional_l_external_lit.md`,
  `docs/conditional_l_literature.md`, `docs/lemma_a_proof.md`.
