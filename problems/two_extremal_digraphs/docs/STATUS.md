# STATUS — Conjecture 9.2 (arXiv:2304.04690): every 2-extremal digraph lies in H_2

Lead Theorist synthesis. Date: 2026-05-30.

---

## 0. LEAD VERDICT (this round) — Conditional L is PARTIALLY closed; Conjecture 9.2 does NOT follow

Three independent passes (one literature, two adversarial proof-verifications, re-pulling
BJSS arXiv:1908.04096 / EJC 27(1) #P1.63 and AAC arXiv:2304.04690 from the *primary source
PDFs*) converge on a sharp boundary. Stating only adversarially-survived steps and
correctly-verified citations:

**(1) Is Conditional L proved?**
**SPLIT. The directed-Hajós-join half is CLOSED BY CITATION; the 2-Hajós-tree-join half is OPEN.**

- *Directed-Hajós-join half — CLOSED (known theorem, citation verified against primary source).*
  Conditional L for a literal directed Hajós join `D = D1 ▽ D2` is **BJSS Theorem 2(a)**:
  `χ⃗(D) ≥ min{χ⃗(D1), χ⃗(D2)}`. Setting the needed value (k=3): if `χ⃗(D1),χ⃗(D2) ≥ 3`
  then `χ⃗(D) ≥ 3`. The proof is the 5-line cross-seam splice
  `C1 ∪ C2 − u1v1 − v2u2 + u1u2`. This is **exactly** the "cross-seam acyclicity" that
  earlier drafts (lemma_a_proof.md §3/§5) flagged as the "unverified open heart" — it is
  neither open nor unverified: it is a published theorem, re-pulled verbatim from
  arXiv:1908.04096, and the splice logic was *independently re-derived and adversarially
  survived* (two verifiers, every load-bearing step audited; L1 PROVED). The companion
  gluing/upper bound is **Thm 2(b)** and criticality descent both ways is **Thm 2(c),(d)**.
  The BJSS join definition is definitionally identical to Def 1.5 (u1=u, u2=w); χ⃗ matches
  (Neumann-Lara acyclic colour classes). **CITED-OK.** The 1680/4.16M-join search that
  earlier declared this "open" was chasing an existing theorem.

  *Two verified caveats on the citation, neither fatal:* (D1) BJSS states the hypothesis
  of Thm 2(b)(c)(d) as **k ≥ 3**, not "k ≥ 2" as earlier memos quoted — the induction
  consumes it at **k = 3** (2-extremal ⇒ χ⃗=3 ⇒ 3-dicritical by AAC Lemma 4.1, k≥1,
  source-verified), and 3 ≥ 3, so the application is valid; the "hence at k=2" phrasing in
  the drafts is index-confused and must be corrected. (D2) Thm 2(d) descends **criticality**,
  not full **2-extremality** — see (2) below.

- *2-Hajós-tree-join half — OPEN (NOT closed by citation; an earlier draft's L4(i) claim
  to the contrary is a verified OVERCLAIM).* H_2 (Conjecture 9.2) is closed under the
  **Def-9.1** 2-Hajós tree join: an (A,B) edge-partition with B-edges plain digons and an
  even-number-of-B-edges-per-leaf-path parity condition. AAC **Lemma 6.7** is about the
  **Def-1.6** Hajós tree join (every edge a *block* Di with [ui,vi] ⊆ A(Di)); it has **no**
  A/B partition, no plain-digon B-edges, no parity condition. A B-digon is not a Def-1.6
  block (Di − [ui,vi] would be empty). So Lemma 6.7 does **not** cover the Def-9.1 seam,
  and the claimed "verbatim/parsing" reduction does not exist. The BJSS splice is single-arc
  / single-identified-vertex only; it is not proven to extend to the multi-seam Def-9.1 join.
  **This is the exact smallest remaining colouring hole:** the directed Hajós lower bound for
  the Def-9.1 2-Hajós tree-join seam (B-digons + even-parity), plausibly provable by
  extending the BJSS splice, but **not done and not in the literature.** AAC §9 itself gives
  it no lemma number ("routine work to check"), consistent with it being genuinely unproved.

**(2) Given Conditional L's status, are Lemma A sufficiency and Lemma B's χ⃗=3 closed?**
**NO to both.**

- *Lemma A sufficiency (cut ⇒ factorisation) — OPEN, no external help.* Promoting a
  mixed-2-cut of U(D) to a genuine 2-extremal Hajós/tree-join factorisation is a
  connectivity/structure recognition problem; BJSS Thm 2 **assumes** D = D1 ▽ D2 is given
  and says nothing about recognising a join from connectivity data. AAC's own k≥3
  decomposition (Thm 5.1) has **no k=2 analogue**. The cut⇒factorisation recipe was
  empirically refuted-as-recipe at n=7 (member 7.33). This wall stands.

- *Lemma B's χ⃗=3 — only partially closed.* For the **directed-Hajós seam on a dicritical
  D**, χ⃗(Di) ≥ 3 follows from BJSS Thm 2(d). But **2-extremal ≠ 3-dicritical**: a
  2-extremal D has χ⃗=3 yet may carry removable arcs, and reducing to a dicritical
  subdigraph can **destroy the seam**. So Thm 2(d) does not directly give "split ⇒ both
  pieces 2-extremal"; the Eulerian/strong/λ=2/underlying-2-connected bookkeeping is separate
  structural work (BJSS Thm 8 supplies only the strong-connectivity clause for the Hajós
  seam). And for the **tree-join seam**, even the χ⃗=3 half is unavailable until the
  Def-9.1 lower bound (open, above) is proved.

**(3) Does Conjecture 9.2 follow for general n?**
**NO.** It SURVIVES empirically to n≤7 (52 digraphs, 0 flags, complete truth set, sound
oracle) — *evidence, not a theorem* (per MEMORY: finite-n enumeration is verification, not
proof). Three genuinely open items block the induction: (i) the **Def-9.1 tree-join lower
bound** (the live half of Conditional L), (ii) **cut ⇒ factorisation** (Lemma A
sufficiency / seam EXISTENCE at k=2 — the paper itself leaves this open), and (iii) the
**2-extremality descent** beyond criticality (Lemma B). The directed-Hajós sub-instance now
closed by citation was *already* a published theorem and does **not** by itself advance any
of the three open walls.

**Honest bottom line:** the only thing genuinely settled this round is that the
directed-Hajós half of Conditional L is a known theorem (BJSS Thm 2), correctly cited and
its splice independently survived — which *removes* that sub-problem from the open list and
*corrects* an earlier misdiagnosis, but does **not** close Lemma A, Lemma B, or Conjecture
9.2. Empirical n≤7 survival is not a proof.

**SINGLE MOST DECISIVE NEXT STEP:** Prove the directed Hajós lower bound for the **Def-9.1
2-Hajós tree-join seam** (B-digons + even-B-parity) by extending the BJSS single-arc splice
`C1 ∪ C2 − u1v1 − v2u2 + u1u2` to the multi-seam join — i.e. show a forced monochromatic
peripheral structure splices across the digon forest into a monochromatic dicycle of D.
This is the unique remaining *colouring* hole; it is the live half of Conditional L, it is
not in the literature, and the BJSS proof is the right mechanism to generalise. (Seam
EXISTENCE / cut⇒factorisation remains a separate structural wall and is the next target
after the colouring half closes.)

---

Conjecture 9.2 (informal): the class L of **2-extremal** digraphs (strong, Eulerian
with in=out>=2, underlying graph 2-connected, edge-connectivity lambda=2, dichromatic
number chi_vec=3) coincides with the recursively-built class **H_2** (symmetric odd
cycles, closed under directed Hajos join and 2-Hajos tree join including non-empty A).

---

## 1. VERDICT — survives to n=7, oracle now clears all 52 with ZERO flags

**Conjecture 9.2 SURVIVES to n=7.** The truth set L_n is fully and independently
enumerated for n<=7, and with the corrected H_2 oracle **every member classifies
in-H_2 with 0 not-in-H_2 flags**.

| n | |L_n| | status (corrected oracle) |
|---|------|---------------------------|
| 3 | 1  | gate (paper-known) — in H_2 |
| 4 | 1  | gate (paper-known) — in H_2 |
| 5 | 3  | gate (paper-known) — in H_2 |
| 6 | 8  | fully enumerated — in H_2, **0 flags** |
| 7 | 39 | fully enumerated — in H_2, **0 flags** |

Total: 52 digraphs, **0 flags**. Data on disk: `data/L_3.json` … `data/L_7.json`.
**No L_8 exists yet** (n=8 not enumerated — see §3).

### The former n=7 flag: root-caused and repaired (not patched away)
The single previously-flagged n=7 object
(arcs `[[0,3],[0,4],[1,5],[1,6],[2,4],[2,5],[3,1],[3,5],[4,0],[4,2],[4,6],[5,1],[5,2],[5,3],[6,0],[6,4]]`)
was a **false alarm from oracle incompleteness**, now resolved by a sound recognizer
rather than by special-casing:

- **Object structure (independently re-verified).** 6 digons form a spanning caterpillar
  tree on 7 vertices (leaves {0,1,3,6}); the 4 single arcs form exactly the directed
  cycle `0->3->1->6->0` on precisely those leaves; every leaf-to-leaf tree path has even
  length; the rim leaf order (0,3,1,6) is a valid plane (non-crossing/laminar) circular
  order. This is a 2-Hajos tree join with **empty A** — a generalised wheel, an H_2 base.
- **Root cause.** The empty-A case had been routed only through the generic tree-join
  inverse, whose completeness cap is `max_internal=2`. This object's spanning digon-tree
  has **3** internal vertices (2,4,5), so the capped machinery never reached it.
- **Fix.** New `_is_generalised_wheel(n,arcs)` in `scripts/h2_oracle.py`, wired into
  `_compute_in_H2` right after the symmetric-odd-cycle base case, with **no
  `max_internal` cap**. It is **SOUND**: every accept exhibits an explicit Def-9.1
  empty-A presentation by checking (i) digons = exactly n-1 edges forming a spanning
  tree; (ii) single arcs = exactly one directed cycle on exactly the tree leaves; (iii)
  rim order is a valid plane circular leaf order; (iv) all leaves share one colour in T's
  proper 2-colouring (equivalent to all leaf-leaf paths even, since every tree edge is a
  B-edge). The non-crossing/laminar test is the standard correct characterization of
  plane-realizable cyclic leaf orders for a tree, re-derived and verified on the object.

### Trustworthiness of the verdict — HIGH for n<=7 as empirical verification
Two audited caveats remain (both unchanged in kind from prior rounds):
1. **Enumeration is complete.** Every 2-extremal D is Eulerian, in=out>=2, so its
   underlying simple graph is biconnected min-degree>=2 (the `geng -C -d2` class); all
   digon/single + Eulerian-orientation combinations are generated, deduped by directed
   certificates, and each member re-passes `is_2extremal`. Genuine complete generation
   of L_n for n<=7.
2. **The oracle is SOUND but still INCOMPLETE off the empty-A branch.** Every *True* is
   backed by an explicit derivation into strictly-smaller recognised pieces — no spurious
   membership. The empty-A generalised-wheel branch is now searched in **full** (no cap)
   and is sound by forward construction. But the **non-empty-A** 2-Hajos tree-join
   inverse still carries `max_internal<=2` plus contiguous-block plane-tree and
   connected-block tiling assumptions. **A "not in H_2" verdict therefore remains a
   CANDIDATE, never a proof of non-membership** — exactly the failure mode the n=7
   episode exhibited.

Regression guard: `tests/test_h2_oracle.py` now includes
`test_flagged_n7_generalised_wheel_now_in_H2` and
`test_generalised_wheel_recognizer_sound_rejections`. Pytest: **18 passed.**
Soundness spot-checks: W_3..W_7 accepted (and 2-extremal); recognizer rejects symmetric
C_5 (digons form a cycle not a tree), the directed triangle (no digons), C3#C3 (a genuine
Hajos join, not a wheel), and a tampered rim (one single arc dropped).

**Bottom line:** empirical survival to n=7 with a clean 0-flag sweep and the lone false
flag root-caused and soundly repaired. This is *evidence*, not a theorem.

---

## 2. LEMMA A (Seam Existence) — n<=7 supported, NOT proved; clause (b) corrected

> **Lead-theorist synthesis (2026-05-30).** The strongest VERIFIED line is assembled in
> **`docs/lemma_a_proof.md`**. Verdict: **Lemma A is NOT proved; Lemma B is NOT proved;
> Conjecture 9.2 does NOT follow for general n.** What IS proved: the arc-decomposition
> scaffold (P2/P3 forest + balanced closed trails; no digon 2-arc-cut) and the
> **necessity** half of the mixed-2-cut discriminator — *Hajos merge vertex => MC(D)=1*,
> contrapositive *MC(D)=0 => no Hajos seam* (so the 3 tree-join-only members are
> provably clause-(b)-only). Proved facts constrain seam TYPE only, never seam
> EXISTENCE. The two open theorems are (i) **mixed-2-cut sufficiency** (MC=1 => genuine
> 2-extremal Hajos factors; refuted-as-recipe at n=7 by member 7.33) and (ii) **Lemma B
> Conditional L** — the chi_vec=3 / directed-Hajos-criticality gluing — which is the
> common load-bearing core of both walls. Empirical survival to n<=7 is evidence, not a
> theorem. Scripts `seam_invariant.py` and `lemma_b_checks.py` both reproduce PASS.

**Lemma A.** *Every 2-extremal digraph that is not a symmetric odd cycle and not a
generalised wheel admits a Lemma-A seam: either (a) a directed-Hajos merge vertex, or
(b) a 2-Hajos tree-join seam.*

### Seam census over L_6 ∪ L_7 (47 members; independently re-verified from arc sets)
- **7 base** (2 at n=6, 5 at n=7), **40 non-base.**
- **37/40** have a directed-Hajos merge vertex (clause a).
- **3/40** (n=7 indices 7, 14, 36) have NO Hajos seam but a genuine non-empty-A
  **tree-join** seam (clause b).
- **40/40 non-base members are seamed. NO-SEAM list is EMPTY** — zero obstructions, zero
  missing H_2 constructors.

So **Lemma A holds for n<=7** (empirical, complete truth set), with **0 obstructions.**

### The decisive correction to clause (b) [PROVED]
The literal reading of clause (b) as "a peripheral B-edge **cut digon** (a 2-arc-cut
digon)" is **VACUOUS**: **0 of 40** non-base members possess *any* 2-arc-cut digon.
Reason (Menger): a strong, underlying-2-connected digraph can never have a digon as its
only x–y connection, so no digon is a 2-arc-cut. The induction seam therefore **cannot**
be a single cut digon; clause (b) **must** be stated in the general Def-9.1 tree-join
sense. This refutes the cut-digon mechanism of `docs/proof_attempt.md` §6 and is the
load-bearing repair to the lemma statement.

### The 3 tree-join-only members are NOT counterexamples [re-verified]
Each n=7 member (indices 7,14,36) is genuinely 2-extremal, non-base, in H_2, with no
Hajos merge vertex and no 2-arc-cut digon, but a real non-empty-A 2-Hajos tree-join seam:
a directed-triangle rim + spanning plane tree (2 internal vertices, 3 B-digons + 1 A-edge)
joined to one 4-vertex 2-extremal A-block equal to **W3**. They lack a Hajos merge vertex
precisely because the minimal nontrivial block (W3) attaches through a **2-vertex A-edge
interface**, not a single identified vertex — the n=4 phenomenon (W3/W4 are tree-joins,
not Hajos-joins) recurring as a sub-block at n=7.

### Proved structural scaffold (independent of n<=7 enumeration)
- **No 2-extremal digraph has a 2-arc-cut digon** (Menger).
- **The digon graph is always a forest** (40/40 verified; consistent with the spanning
  digon-tree structure of all observed seams).
- **Single arcs are in/out balanced** — they decompose into closed directed trails.
- **The §6.4 component-count predictor is REFUTED**: ncomp=2 occurs in 22 Hajos-seamed
  AND in all 3 tree-join-only members, so component count does **not** separate seam
  types. The invariant distinguishing Hajos-seam from tree-join-seam members is finer
  than any digon-graph statistic.

### The single open core
**Sub-lemma A′ (Seam from the arc decomposition).** *Given the proved decomposition of a
2-extremal digraph into a digon forest + balanced single-arc closed trails, a Lemma-A
seam always exists.* Both the spanning-F_D and non-spanning-F_D cases reduce to A′, and
A′ is **OPEN** — the inductive core does not close. The distinguishing invariant is
identified as a property of the single-arc closed trails relative to the digon forest,
but is not formalized.

Two further supporting steps also remain conjectural:
- **Lemma B** (a split forces both pieces 2-extremal) — the converse-of-routine gap from
  `proof_attempt.md`; verified case-wise, not proved.
- **Lemma C** sufficiency (even-leaf-path B-parity => 2-extremal for all trees/gadgets) —
  strongly supported by the 62-case sweep, no symbolic proof of the peripheral-cycle
  colouring step.

Full analysis: `docs/lemma_a.md`. Search artifact: `data/seam_search_L6_L7.json`.

---

## 3. THE SINGLE MOST DECISIVE NEXT STEP

> **SUPERSEDED by §0 (2026-05-30).** The framing below treated the *directed-Hajós-join*
> Conditional L as the open heart and as a core common to both walls. That is now known to
> be **inaccurate**: the directed-Hajós half is BJSS Theorem 2(a) (published, cited-OK,
> splice independently survived), so it is *not* open and does *not* by itself promote a
> U(D)-cut to a factorisation (Lemma A sufficiency is a separate structural problem outside
> BJSS's scope). The corrected decisive step is in §0: **prove the directed Hajós lower
> bound for the Def-9.1 2-Hajós tree-join seam** (the live half of Conditional L), by
> extending the BJSS splice to the multi-seam join. The original text is retained below for
> context only.

**Prove Conditional L — that two seam-agreeing 2-dicolourings glue to a 2-dicolouring
of D (directed acyclicity of colour classes across the seam).** This single directed
Hajos-criticality lower-bound lemma is the common load-bearing core: it is the open
heart of Lemma B (chi_vec=3 preservation), and the same chi_vec=3-preservation argument
is exactly what promotes a mixed 2-cut from a cut of U(D) to a genuine 2-extremal Hajos
factorisation, closing the Lemma-A sufficiency hole as well. Settle Conditional L and
both walls (Lemma A sufficiency + Lemma B) fall together. See `docs/lemma_a_proof.md` §5.

Superseded framing (kept for context):
**Prove Sub-lemma A′ — seam existence from the (already proved) digon-forest +
balanced-closed-trail arc decomposition.**

This is now the unique load-bearing crux. We have, this round, converted the abstract
"Lemma A" into a concrete reduction whose hypotheses are *proved* (digon graph is a
forest; single arcs are balanced closed trails; no digon is a 2-arc-cut) and whose
conclusion is the *only* missing inductive step. The empirical situation is maximally
favorable: Lemma A holds with **0 obstructions over the complete L_6 ∪ L_7** (47
members), and the seam mechanism has been corrected (general tree-join, not cut digon).
There is no counterexample to chase and no missing constructor to invent; the entire
remaining risk sits in A′.

Concrete plan:
1. Formalize the finer invariant separating Hajos-seam members (single identified merge
   vertex) from tree-join-seam members (2-vertex A-edge interface). The seam census shows
   component count fails; the candidate handle is how the single-arc closed trails thread
   the leaves of the digon forest. Pin this to a graph invariant computable from
   (F_D, closed-trail set).
2. Prove that in every non-base configuration this invariant forces at least one of:
   a forest cut edge realizable as a tree-join seam into two strictly-smaller 2-extremal
   blocks, or an articulation point realizable as a directed-Hajos merge vertex. The 3
   tree-join-only n=7 members are the canonical hard case (W3 sub-block, no merge vertex)
   and should be the worked template.
3. Close **Lemma B** in parallel (split => both pieces 2-extremal); A′ + B together give
   the inductive step, and the corrected sound oracle already mechanically certifies the
   base/recursion for n<=7.

Secondary, only if A′ stalls or for an independent stress test: push enumeration to
**n=8** (the paper's Figure-11 prize regime) with a C-accelerated strong/lambda
primitive — the pure-Python enumerator exceeds budget there (7123 biconnected graphs,
>10^8 Eulerian orientations). This extends *evidence* and would be the first test of the
corrected oracle and of Lemma A beyond n=7, but unlike proving A′ it does not advance the
*proof*.

---

### Discipline reminder
Empirical survival to n=7 with a 0-flag sweep is **not** a theorem. The characterisation
rests entirely on the open Sub-lemma A′ (plus Lemma B). Every "not in H_2" verdict from
the non-empty-A branch of the oracle remains a candidate requiring hand verification (the
oracle is sound but still incomplete off the empty-A branch), exactly as the now-repaired
n=7 flag showed.

### Key artifacts
- Enumerator: `scripts/enumerate.py`; truth sets `data/L_3.json`…`data/L_7.json`
- Oracle (sound; empty-A complete, non-empty-A still capped): `scripts/h2_oracle.py`
  (+ regression tests in `tests/test_h2_oracle.py`, 18 passed)
- Seam search: `scripts/seam_search.py`; results `data/seam_search_L6_L7.json`
- Lemma A analysis + proved scaffold + open Sub-lemma A′: `docs/lemma_a.md`
- k=2 induction analysis and clause-(b) correction context: `docs/proof_attempt.md`
