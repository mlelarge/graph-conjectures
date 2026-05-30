# Adversarial audit of `proof_minimal_counterexample.md`

**Auditor mandate.** Break the minimal-counterexample attempt at Sub-lemma
A-prime. For every load-bearing step: (1) check the logic; (2) recompute every
"verified n≤7" structural claim from scratch against **all** of `L_3..L_7`
(52 members, 41 non-base) using only the sound primitives in
`scripts/h2_oracle.py` and `scripts/seam_invariant.py`. A single failing member
kills a step. Default skeptical: not-airtight ⇒ not proved.

**Reproduction.** `python3 scripts/audit_minimal_counterexample.py` (system
python, no deps). The audit recomputes the digon/single split, vertex
connectivity, vertex 2-cuts, single-arc cycle structure, the interface-digon
block recipe, `MC`, and the full `is_in_H2` oracle independently of the proof's
run logs. Existing tests (`pytest`, 26 passed under a throwaway `uv` venv,
since removed) all pass; the oracle primitives are intact.

**Headline.** The three new structural lemmas the proof claims as **proved**
(S1 leaf attachment, S2 minimal-trail-is-a-simple-`k≥3`-cycle, S3 W₃ A-edge
mechanism for the three MC=0 members) all SURVIVE. The proof's self-declared
gaps G1/G2/G3 are real and open; my audit additionally finds a concrete
**refutation of the interface-digon decomposition recipe as stated generally in
§3** (it fails on member 7.33), and a **minor logical gap in the necessity
proof** underpinning S4. None of these collapses the proof further than its own
honest accounting — but they sharpen exactly where it is not airtight.

---

## Verdict table

| Step | Claim | Verdict |
|---|---|---|
| S1 | Every digon-forest leaf has single-in = single-out ≥ 1 | **PROVED (logic sound) + verified 0/52 exceptions** |
| S2 | Minimal single trail = simple directed cycle, length 3/4/5 (non-base) | **PROVED (logic sound) + verified**; one caveat below |
| S3 | For 7.7/7.14/7.36 the A-edge interface is a non-adjacent 2-cut; small side = W₃; large side not 2-extremal | **PROVED for those three + verified** |
| S4 / 1.2′ | A seamless minimal counterexample has no Hajós merge vertex | **CONDITIONALLY PROVED** — sound *given* the necessity half; necessity half has a small unaddressed sub-step (below) |
| G1 | non-base ⇒ U(D) not 3-connected (has a vertex 2-cut) | **EMPIRICAL ONLY (41/41)**, not proved; base class is mixed on 3-connectivity |
| G2 | small side of a vertex 2-cut, closed with interface digon, is a strictly-smaller 2-extremal block | **FALSE as stated generally** (breaks at 7.33); holds 40/41 and on all 3 MC=0 members, but is the open decomposition crux |
| G3 | residual is a valid 2-Hajós tree-join (rim + even B-parity) | **EMPIRICAL/FORWARD ONLY**, decomposition direction unproved |

---

## Step-by-step

### S1 — Leaf attachment lemma. SURVIVES (proved).

*Logic.* `ℓ` a leaf of `F_D` ⇒ exactly one incident digon, contributing 1 to
in- and 1 to out-degree. Eulerian in=out≥2 forces single-in(ℓ)=single-out(ℓ)=
in(ℓ)−1≥1. This is a clean, rigorous consequence of P2+P3+Eulerian. **Sound.**

*Recompute.* Over **all 52** members of `L_3..L_7` (including the symmetric odd
cycles, which simply have no forest leaves with single arcs to violate it):
**0 exceptions.** Every `F_D`-leaf has single-in = single-out ≥ 1.

### S2 — Minimal single trail is a simple directed cycle. SURVIVES (proved), with a scope caveat.

*Logic.* P3 ⇒ single arcs are balanced and decompose into closed trails;
minimality + the leaf lemma ⇒ the shortest closed trail is a simple cycle; a
single 2-cycle would be a digon (excluded) ⇒ length ≥ 3. **Sound.**

*Recompute.* Balanced at every vertex: **0 exceptions/52.** No single 2-cycle
anywhere: **0 exceptions/52.** Minimum single-cycle length distribution:

- **non-base only:** `{3: 32, 4: 6, 5: 3}` — exactly the proof's stated 3/4/5.
- **all non-SOC (incl. generalised-wheel bases):** `{3: 35, 4: 9, 5: 4, 6: 1}`.

**Caveat (not a refutation).** The proof's S2 sentence "every minimal single
trail over n≤7 has length 3, 4, or 5" is true **only under its non-base scope**.
There is a **length-6** minimal single cycle: member **7.25**, which is a
*generalised wheel* (a base object), with single-arc rim
`{(0,3),(3,1),(1,5),(5,2),(2,4),(4,0)}`. The proof never claims S2 for bases, so
its argument is unaffected, but the unqualified "over n≤7" phrasing is loose:
read it as "over non-base members."

### S3 — A-edge mechanism for 7.7 / 7.14 / 7.36. SURVIVES (proved for those three).

*Recompute (independent of the proof's run log).* For each of 7.7, 7.14, 7.36:

- vertex 2-cuts of `U(D)` are exactly `{0,6}` and `{5,6}`;
- both cut pairs are **non-adjacent in D** (neither a single arc nor a digon —
  verified directly from the arc set);
- closing the **small (size-4) side** `comp ∪ {a,b}` with the interface digon
  `{a,b}` yields a block that is `is_2extremal = True` **and**
  `_is_generalised_wheel = True` (the W₃);
- closing the **large (size-5) side** the same way is **not** 2-extremal
  (`is_2extremal = False`), confirming the seam is *distributed*, not a clean
  two-block split.

Cross-check via the sound oracle: each of the three is realised by a
**non-empty-A tree-join** with exactly one size-4 block, and that block is in
`H₂` (`is_in_H2 = True`). So the forward construction genuinely holds for these
three, and `is_in_H2 = True` for all three. **The theorem-about-those-members
is solid.**

### S4 / 1.2′ — Seamless MC counterexample has no Hajós merge vertex. CONDITIONALLY PROVED.

*Logic.* The proof derives this as the contrapositive of the **necessity** half
("Hajós merge vertex ⇒ MC(D)=1"), which `seam_invariant.md §3.1` asserts as a
theorem. Granting necessity, `MC(D)=0 ⇒ no Hajós merge vertex` is immediate and
**sound**. This is the one genuinely load-bearing thing the angle adds beyond the
prior passes, and it is valid *modulo* the necessity proof.

*Recompute.* `MC(D)=0 ⇒ no Hajós decomposition exists`: **0 violations/52**
(no member has MC=0 together with a Hajós decomposition). The non-base MC=0
members are **exactly** `{7.7, 7.14, 7.36}`, matching the proof.

**Gap I found in the necessity proof (small but real).** `seam_invariant.md §3.1`
argues that a Hajós merge produces a mixed 2-cut `(v, {u,w})` where `{u,w}` is
the join arc. The *mixed-2-cut definition requires `{u,w}` to be a **single**
edge* (reverse absent). The necessity argument **silently assumes** the join arc
`u→w` has its reverse `w→u` absent; per Def 1.5 the join arc is added fresh after
deleting `u→v₁` and `v₂→w`, and nothing in the written proof rules out `w→u`
surviving on one of the sides (which would make `{u,w}` a digon, disqualifying
the mixed-2-cut witness). **Empirically this never happens:** across all 52
members, **every** Hajós-join witness `(u,w,v)` has the join arc single
(reverse absent) — `0` digon-join witnesses. So the necessity half holds 52/52,
but the *written argument* has an unfilled sub-step ("the join arc is single").
Mark necessity **proved-modulo-this-sub-step**; it should be closed explicitly.

### G1 — non-base ⇒ U(D) not 3-connected. EMPIRICAL ONLY.

*Recompute.* All **41/41** non-base members have a vertex 2-cut (none is
3-connected). But the base class is genuinely **mixed**: the 3-connected bases
are exactly **4.0 (W₃), 5.1, 6.5, 7.25** — wheels that *are* 3-connected — while
other bases are not. So "U not 3-connected" is necessary-but-not-sufficient for
non-base; there is no clean dichotomy and **no proof**. The proof labels this
[sketched/conjectural] and that label is correct. **Unproved.**

### G2 — small-side 2-extremality (THE CRUX). FALSE AS STATED GENERALLY.

This is the load-bearing decomposition-soundness step, and the audit produces a
**concrete break of the recipe as written in §3 (steps 4–5) and §2.4**.

The proof's recipe: take a vertex 2-cut `{a,b}`, close the **small side** with
the interface digon `{a,b}`, claim the result is a *strictly-smaller 2-extremal
block* to which minimality applies.

*Recompute over all non-base members.* For **40/41** non-base members, **some**
vertex 2-cut's small side closed with its interface digon IS a strictly-smaller
2-extremal block. The single exception is member **7.33**:

- 7.33 is non-base, **MC=1**, vertex 2-cuts `{0,6}` and `{5,6}`;
- for **both** cuts, **both** sides closed with the interface digon are
  **`is_2extremal = False`** (and not in H₂);
- yet 7.33 *is* in H₂ — via a genuine **directed-Hajós join** at merge vertex
  `v=6` with single join arc `{0,5}` (mixed 2-cut `(6,{0,5})`), splitting into
  two size-4 2-extremal blocks. The interface-digon-on-the-cut-pair recipe
  simply does **not** describe how 7.33 decomposes.

**Consequence.** The §3 step "the small side closed with the interface digon is
2-extremal" is **not a universal structural truth**; it is refuted at n=7 by
7.33. The proof's *narrowed* argument survives this only because it invokes the
recipe **exclusively for MC=0 members** (where 7.33, being MC=1, is excluded):
restricted to MC=0 non-base members the recipe holds (3/3), and on all non-base
members the recipe holds 40/41 with the lone failure being a clause-(a) member.
But as a general decomposition lemma the recipe is **false**, confirming G2 is
genuinely open and **cannot be closed by the stated recipe alone** — a correct
decomposition must be case-split on the seam type, exactly the wall the proof
identifies. **The crux remains open; the proposed mechanism is refuted in
general.**

### G3 — rim/parity validity (decomposition direction). EMPIRICAL/FORWARD ONLY.

*Recompute.* The **forward** direction holds where it must: the three MC=0
members are each realised by a valid non-empty-A tree-join (single size-4 W₃
block, in H₂), and the **sound** oracle certifies `is_in_H2 = True` for **all
41/41** non-base members. So the *existence* of an H₂ derivation is verified
n≤7. But this is the oracle confirming membership, **not** a proof that "a
minimal single trail is always a valid rim with even B-parity" in the
decomposition direction. The proof labels §2.3 [sketched] and G3 [conjectural];
correct. **Unproved.**

---

## What survives as rigorously proved (auditor's confirmation)

1. **S1 leaf attachment** — sound logic, 0/52 exceptions.
2. **S2 minimal-trail = simple `k≥3` cycle** — sound logic, 0/52 exceptions
   (lengths 3/4/5 for non-base; one length-6 *base* case, outside scope).
3. **S3 A-edge mechanism for 7.7/7.14/7.36** — fully verified, oracle-confirmed
   in H₂. A genuine theorem about those three members.
4. **S4 / 1.2′** — sound **given** the necessity half; necessity half holds
   52/52 but its written argument omits the "join arc is single" sub-step.

## What is only empirically supported (n≤7, NOT proved)

- **G1** vertex-2-cut existence (41/41, base class mixed → no dichotomy);
- **G3** rim/parity in the decomposition direction (forward + oracle only).

## What is FALSE / refuted

- **G2 as a general structural claim**: the interface-digon-on-a-vertex-2-cut
  recipe yields a 2-extremal smaller block on **40/41** non-base members but
  **fails on 7.33** (MC=1; both sides of both 2-cuts are non-2-extremal, while
  the true seam is a single-vertex Hajós join). The recipe is therefore **not**
  a universal decomposition; G2 is open and the proposed mechanism cannot close
  it without a seam-type case split.

## Minor issues

- The necessity-direction proof (`seam_invariant.md §3.1`) needs the explicit
  sub-step "the Hajós join arc `(u,w)` is single (reverse absent)". True 52/52,
  but unargued in text.
- S2's "over n≤7" should read "over non-base members" (a length-6 minimal single
  cycle exists among generalised-wheel bases, member 7.25).

## Bottom line

The audit **confirms the proof's own honest status**: it sharpens but does not
close Sub-lemma A-prime. The three claimed structural lemmas (S1, S2, S3) and the
confinement step (S4/1.2′) are sound (S4 modulo one textual sub-step). G1 and G3
are empirical only. **G2 — the crux — is not merely unproved but its proposed
interface-digon mechanism is refuted at n=7 by member 7.33**, so the
decomposition-soundness step provably requires more than the recipe on the
table. Impossibility of a seamless minimal counterexample remains
`(G1) ∧ (G2) ∧ (G3)` with G2 load-bearing and open. Empirical agreement is n≤7;
verification, not proof.
