# Adversarial audit of `proof_criticality.md`

Auditor stance: skeptical. A step is "proved" only if its written argument is
airtight; structural claims are tested on **every** member of `L₃..L₇` (52 members,
all re-confirmed 2-extremal by `h2_oracle.is_2extremal`), not just `L₆∪L₇`. A single
failing member kills a step. Empirical agreement is labelled EVIDENCE, never proof.

All tests used **system `python3`** importing `scripts/h2_oracle.py` and
`scripts/seam_invariant.py`. No `.venv`, no `networkx` (none was present; none
created). The temporary probe script was removed after running.

Bottom line up front: the document's own headline is **honest and correct** — the
criticality angle does NOT close Sub-lemma A-prime, and it says so. The genuine
mathematical contribution (Theorem 3) is **rigorously proved and survives all data**.
The negative refutation's *qualitative* conclusion survives, but its *quantitative*
"37/40" census rests on a "reductive size-2 dicut" definition that is **not pinned
down by any committed script**, so its exact numbers are not independently
reproducible. Lemma 4 is correctly self-labelled as a sketch.

---

## Counts correction (not an error in the proof, but a clarification)

The task prompt and the prose say "7 base + 40 non-base". The seam file's own `base`
field marks **7 base objects = 1 symmetric odd cycle (`7.38`) + 6 generalised wheels
(`6.3, 6.5, 7.9, 7.22, 7.25, 7.30`)**, leaving exactly **40 true non-base** members
of `L₆∪L₇`. The MC/Theorem-3 claims are over these 40. (If one only excludes
symmetric odd cycles, there are 46/49; Theorem 3 and (★) hold on those too — a
stronger statement — see below.)

---

## Step-by-step verdicts

### Lemma 1 (2-extremal ⇒ 3-dicritical). VERDICT: EVIDENCE-only (as labelled).
- **Logic**: the `χ⃗(D)=3` half is definitional. The `χ⃗(D−e)=2 ∀e` half is *imported*
  from the paper's dicriticality theory and only re-derived computationally here. The
  document labels this exactly right ("[proved given the paper's dicriticality]; the
  computational re-derivation is [verified]").
- **Data**: I re-checked `χ⃗(D−e)=2` for **every arc** of **all 52** members of
  `L₃..L₇` via `O.can_dicolor_k(n, arcs−e, 2)`. **0 failures.** Stronger than the
  doc's 47-member check.
- Verdict: **empirically supported on `n≤7`**, rests on an un-re-derived paper theorem.
  Not a from-scratch proof. This matches the doc's self-assessment.

### Lemma 2 (digon bichromaticity). VERDICT: PROVED (rigorous).
- A digon is a directed 2-cycle; if both endpoints share a colour the 2-cycle is
  monochromatic, contradicting acyclicity of a colour class. Airtight, one line.

### Corollary 2.1 (forest 2-colouring). VERDICT: PROVED (rigorous), modulo P2.
- Follows from Lemma 2 + P2 (digon graph is a forest). Correct.
- Note the scope: P2's "forest" holds for non-base members. The **base symmetric odd
  cycles** have a digon graph that is an **odd cycle, not a forest** — I confirmed this
  for `3.0, 5.2, 7.38` (edges = n, one component, not a forest). The corollary and
  Theorem 3 are therefore *correctly* restricted to non-base D; see the adversarial
  finding under Theorem 3.

### Corollary 2.2 (obstruction = single-arc dicycle; same-coloured endpoints).
VERDICT: PROVED (rigorous) + EVIDENCE for the endpoint refinement.
- The "monochromatic dicycle avoids digons hence lies in S(D)" half is an immediate
  consequence of Lemma 2 — rigorous.
- The refinement "every 2-dicolouring of `D−e` gives `c(u)=c(w)`" I tested **more
  adversarially than the doc**: I enumerated **ALL** proper 2-dicolourings of `D−e`
  (brute force over `2^n`, filtering acyclic classes), not just "the 2 complementary
  ones." Over **all 274 single arcs** of `L₃..L₇`: **0 violations** — *every*
  2-dicolouring of `D−e` has `c(u)=c(w)`. This is a clean, reproducible result and is
  *stronger* than the doc's wording ("both 2-dicolourings"). Verdict: the structural
  claim **survives**; it remains an `n≤7` fact, not a theorem (the doc does not claim
  otherwise here).

### Theorem 3 (`χ⃗(D)=3 ⇔ (★)`; the angle's payload). VERDICT: PROVED (rigorous),
and SURVIVES all data — the one genuinely new theorem, and it holds.
- **Logic, both directions, scrutinised**:
  - (⇐) Given a forest-2-colouring `c` leaving `S(D)` with no monochromatic dicycle:
    each colour class is acyclic because any monochromatic dicycle avoids digons
    (Lemma 2) hence lies in `S(D)`, and there are none. Correct.
  - (⇒) A 2-dicolouring is digon-proper (Lemma 2) hence restricts to a proper
    `F_D`-2-colouring with no monochromatic `S(D)`-dicycle. Correct.
  - The **"extended arbitrarily to digon-free vertices"** clause is **load-bearing,
    not vacuous**: I found **14 members** of `L₆∪L₇` with digon-free vertices (isolated
    in `F_D`), e.g. `6.0` (vertex 4), `7.20` (vertices 0,5). The proof handles them
    correctly: an isolated `F_D` vertex's only incident arcs are single arcs, so its
    acyclicity constraint is captured by the `S(D)`-dicycle test, and any colour is a
    proper forest colour. The equivalence held on all of these.
- **Data (standalone model vs oracle)**: I implemented the (★) model independently —
  enumerate every proper 2-colouring of `F_D` (each tree component 2 ways; each
  digon-free vertex 2 ways) and test for a monochromatic single-arc dicycle — and
  compared against `O.can_dicolor_k(n,arcs,2)`.
  - On the **49 non-base** members (excluding only symmetric odd cycles, which
    INCLUDES the 6 generalised wheels): **0 model-vs-oracle mismatches**, and **0 (★)
    failures** (every forest-2-colouring leaves a monochromatic single-arc dicycle).
    Every one of these 49 has a genuine-forest `F_D` (verified). So Theorem 3 / (★)
    hold even on the generalised wheels — *stronger* than the doc's 40-member claim.
  - ADVERSARIAL NEGATIVE that is actually a SCOPE CONFIRMATION: the 3 symmetric odd
    cycles `3.0, 5.2, 7.38` are flagged by the model as "2-colourable" (model≠oracle).
    This is **not** a counterexample to Theorem 3: their digon graph is an odd cycle,
    not a forest, so the hypothesis "`F_D` a forest" (P2) fails and the model's
    "forest-2-colouring" enumeration is ill-defined for them (it produces a colouring
    with a monochromatic digon). Theorem 3 is correctly stated only for the non-base
    case where P2 applies. The doc anticipates exactly this (it notes base symmetric
    odd cycles have "no proper 2-colouring" of their odd-cycle digon graph).
- Verdict: **Theorem 3 is a rigorous theorem** (given Lemma 2 + P2, both sound) and
  its empirical (★)-instantiation is clean. This is the document's real, surviving
  contribution. It is a genuine reduction (it removes colouring), but — as the doc
  stresses — it does **not** supply a separator.

### Lemma 4 (merge vertex ⇒ shared-endpoint single-arc size-2 dicut).
VERDICT: SKETCH (correctly self-labelled), with a definitional fragility I expose.
- The written proof is an explicit sketch: "minimality forces the two forward arcs to
  be the two single arcs at v." It does **not** rigorously exclude that a minimum
  `(s,t)`-dicut's forward arcs include a **digon** arc.
- **Adversarial data finding (definition-sensitivity).** When I enumerate minimum
  `(s,t)`-dicuts via the standard source-side min-cut (`dicut_induction_probe.
  min_st_cut_partition`) and keep only non-singleton-side ("reductive") ones, the
  forward arcs are **frequently digon arcs, not single arcs**: e.g. `6.0` yields a
  reductive cut with forward arcs `{(0,4),(3,5)}` where `(0,4)` is a **digon** arc
  (`(4,0)` present). Across the non-base members I found **91** reductive forward-arc
  occurrences that are digon arcs — directly contradicting a literal reading of
  Lemma 4's "forward arcs are single arcs." Hence Lemma 4 is **only** true under a
  *narrower* notion of "reductive cut" (one that pre-restricts forward arcs to single
  arcs, or excludes digon-crossing cuts). That narrower notion is **not defined in any
  committed script**.
- Verdict: **not proved**; the data does not even cleanly support the broad statement.
  The lemma is plausible under a careful definition, but as written it is a sketch
  whose empirical support depends on an unstated definition of "reductive."

### §4.1 negative ("dicut endpoint SHAPE is not the seam discriminator").
VERDICT: qualitative conclusion SURVIVES (and is reproducible); the quantitative
"37/40 / 6.0,7.1,7.20" census is NOT independently reproducible.
- **What IS reproducible and solid (the real point of the negative):**
  - `6.0, 7.1, 7.20` **are** directed-Hajós members (they have a merge vertex):
    `O._hajos_decompositions` yields a decomposition for each. Confirmed.
  - The **MC discriminator is 40/40** on the true non-base members: `SI.MC(n,arcs)`
    equals "has a Hajós seam" (and equals `has_hajos_seam` from the seam file) on
    **all 40**, **0 mismatches**. `MC=1 ⇔ Hajós`, `MC=0 ⇔ tree-join` over the data.
    This is the doc's central positive empirical claim and it **holds** (n≤7 EVIDENCE).
  - So "the seam discriminator is the **global** `MC(D)`, not any single-dicut
    statistic" is **well supported**: `MC` is a property of `U(D)` + the single/digon
    split and predicts the seam type perfectly on the data, whereas any *local*
    dicut-shape statistic provably cannot (some Hajós members have shared- and some
    have only-disjoint endpoint cuts).
- **What is NOT reproducible (a verification gap, not necessarily a falsehood):**
  - The doc's specific claim — `6.0, 7.1, 7.20` have **only disjoint-endpoint
    reductive size-2 dicuts**, giving "37/40" — could **not** be reproduced because
    the operative definition of "reductive size-2 dicut" (and which forward arcs
    count) is not in any committed script. Under my source-side min-cut enumeration
    these members also exhibit shared-tail/shared-head cuts (with digon forward arcs);
    under a strict "both forward arcs single, both sides ≥2" definition they have **0**
    such cuts (so vacuously "no shared-endpoint single-arc cut"). Neither reproduces
    the doc's "only disjoint" wording or its 37/40 count.
  - CONSEQUENCE: treat the "37/40" and the "shared-tail 35 / shared-head 5 /
    disjoint 41,14" census as **unverified prose**. The *direction* it argues (dicut
    shape ≠ seam discriminator) is nonetheless correct, because it is implied by the
    reproducible facts above (local shape varies among Hajós members; MC is global and
    perfect). The negative's conclusion stands on the reproducible facts even though
    its stated statistics do not.

### §4.2 (k=2 failure of Lemma 3.3, via (★)). VERDICT: SKETCH (correctly labelled).
- The descriptive structural claims are reproducible: `7.7` and `7.14` have **two
  vertex-disjoint single-arc triangles**; `7.36` has **two single-arc triangles
  sharing exactly one vertex** (the "MC=0 no-pinch" pattern). Confirmed via the
  single-arc subdigraph's directed cycles: `7.7 → {1,2,4},{3,5,6}`;
  `7.14 → {1,2,5},{3,4,6}`; `7.36 → {1,2,4},{4,5,6}`.
- The doc does **not** turn this into a proof that the third-colour dicycle's position
  *forces* a tree-join seam, and says so. Correctly a sketch.

### §5 / Sub-lemma A-prime′. VERDICT: OPEN, correctly identified as the unmoved hole.
- The two sufficiency directions (MC=1 ⇒ genuinely 2-extremal Hajós factors;
  MC=0 ⇒ valid even-parity tree-join into strictly-smaller 2-extremal A-blocks) are
  **conjectural**. Theorem 3 sharpens *what* must be shown but supplies **no
  separator-existence argument**. This is identical to the open step of
  `seam_invariant.md`. The document is honest that A-prime is **not** closed.

---

## Summary table

| step | doc label | audit verdict | basis |
|---|---|---|---|
| Lemma 1 (3-dicriticality) | proved-given-paper / verified | EVIDENCE-only on `n≤7` (52/52); imports a paper theorem | data, all 52 |
| Lemma 2 (digon bichromatic) | proved | **PROVED** (rigorous) | logic |
| Cor 2.1 (forest 2-colouring) | proved | **PROVED** modulo P2 (non-base only) | logic + P2 |
| Cor 2.2 (single-arc obstruction; `c(u)=c(w)`) | proved/verified | mono-half PROVED; endpoint refinement EVIDENCE (274/274, ALL dicolourings) | logic + data |
| **Theorem 3 (`χ⃗=3 ⇔ (★)`)** | **proved** | **PROVED (rigorous), survives all data (49/49 non-base, 0 mismatch)** | logic + data |
| Lemma 4 (merge ⇒ shared-endpoint single-arc dicut) | sketch→proved-on-data | **SKETCH, not proved**; literal reading contradicted by data (91 digon forward arcs) | logic + data |
| §4.1 negative (shape ≠ discriminator) | verified | qualitative SURVIVES; "37/40" census NOT reproducible (no committed def of "reductive") | data |
| MC discriminator (for contrast) | verified 40/40 | **SURVIVES, 40/40, 0 mismatch** (EVIDENCE, `n≤7`) | data |
| §4.2 (k=2 failure mechanism) | sketch | descriptive claims reproduce; mechanism unproved (sketch) | data |
| A-prime′ sufficiency (§5) | conjectural/open | **OPEN** — unchanged load-bearing hole | — |

## What survives as rigorously PROVED
- Lemma 2, Corollary 2.1 (modulo P2), the monochromatic-avoids-digon half of
  Corollary 2.2, and **Theorem 3** (`χ⃗(D)=3 ⇔ (★)`). Theorem 3 is the angle's real
  yield and it is airtight given the already-proved P2 and Lemma 2, and it survives
  every data test (no member breaks it).

## What is EMPIRICALLY supported only (`n≤7`), not proved
- Lemma 1 (3-dicriticality, also leans on an un-re-derived paper theorem); the
  `c(u)=c(w)` endpoint refinement (274/274, all dicolourings); the **MC=40/40**
  discriminator; the descriptive triangle structure of `7.7/7.14/7.36`.

## What is FALSE-as-written / NOT reproducible (verification gaps)
- **Lemma 4 as literally stated** ("reductive cut forward arcs are single arcs") is
  contradicted by the data under the natural source-side min-cut definition (91
  digon forward arcs); it is only a sketch and is true at best under an unstated
  narrower "reductive" notion.
- The **quantitative "37/40" refutation census** (`6.0,7.1,7.20` have "only
  disjoint-endpoint reductive size-2 dicuts") could not be reproduced — there is no
  committed definition/script of "reductive size-2 dicut." Its *qualitative*
  conclusion (dicut shape ≠ seam discriminator; MC is the global discriminator)
  nonetheless follows from reproducible facts and stands.

## Headline
The document does not close Sub-lemma A-prime, and it correctly says so. Its one
new rigorous theorem (Theorem 3) is genuinely proved and survives all data; the
separator-existence step (A-prime′) is **unchanged and open**. Two supporting
claims (Lemma 4; the "37/40" census) are weaker than written and not independently
reproducible, but they are not load-bearing for the (honest) conclusion.
