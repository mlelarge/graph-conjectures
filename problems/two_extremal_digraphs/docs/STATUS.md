# STATUS — Conjecture 9.2 (arXiv:2304.04690): every 2-extremal digraph lies in H_2

Lead Theorist synthesis. Date: 2026-05-30.

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
