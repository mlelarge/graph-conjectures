# STATUS — Conjecture 9.2 (arXiv:2304.04690): every 2-extremal digraph lies in H_2

Lead Theorist synthesis. Date: 2026-05-30.

Conjecture 9.2 (informal): the class L of **2-extremal** digraphs (strong, Eulerian
with in=out>=2, underlying graph 2-connected, edge-connectivity lambda=2, dichromatic
number chi_vec=3) coincides with the recursively-built class **H_2** (symmetric odd
cycles, closed under directed Hajos join and 2-Hajos tree join including non-empty A).

---

## 1. VERDICT — survives to n=7; NO trustworthy counterexample

**Conjecture 9.2 SURVIVES to n=7.** The truth set L_n is fully and independently
enumerated for n<=7, and every member is in H_2.

| n | |L_n| | status |
|---|------|--------|
| 3 | 1 | gate (paper-known) — all in H_2 |
| 4 | 1 | gate (paper-known) — all in H_2 |
| 5 | 3 | gate (paper-known) — all in H_2 |
| 6 | 8 | NEW, fully enumerated — all in H_2, **0 flags** |
| 7 | 39 | NEW, fully enumerated — 1 flag raised, **REFUTED** (see below) |

Total: 52 digraphs evaluated. Data on disk: `data/L_3.json` … `data/L_7.json`.
**No L_8 exists** (n=8 not enumerated — see §2).

### The one flag and why it does not survive
Cross-check flagged a single n=7 object as "not-in-H_2":
arcs `[[0,3],[0,4],[1,5],[1,6],[2,4],[2,5],[3,1],[3,5],[4,0],[4,2],[4,6],[5,1],[5,2],[5,3],[6,0],[6,4]]`
(6 digons forming a caterpillar spanning tree, 4 single arcs forming the directed
4-cycle 0->3->1->6->0 on its four leaves).

The flag is a **FALSE ALARM from oracle incompleteness**, refuted by independent
reconstruction (`redteam_verify.py`, `redteam_closure.py`):
- The object **is** a generalised wheel = 2-Hajos tree join with **empty A**, an H_2
  base construction. Digons = caterpillar T (backbone 4—2—5, leaves {0,6}@4, {1,3}@5);
  single arcs = peripheral directed cycle on the leaves; all leaf-to-leaf paths in T
  have even length (4,4,2,2,4,4) so the Def-9.1 parity condition holds; the leaf
  cyclic order (0,3,1,6) is a valid planar circular order.
- A generalised wheel built independently from T + this peripheral cycle is
  **canonically identical** to the candidate (brute force over all 7! relabelings).
- Root cause of the miss: the underlying graph has no articulation point (so 0 Hajos
  inverses — correctly reported), and the oracle's tree-join inverse search did **not
  test the empty-A generalised-wheel realisation** (a documented gap).

**Trustworthiness of the verdict.** HIGH for n<=7 *as empirical verification*, with two
audited caveats:
1. **Enumeration completeness is sound.** Every 2-extremal D is Eulerian with in=out>=2,
   so its underlying simple graph is biconnected min-degree>=2 (exactly the
   `geng -C -d2` class); all digon/single + Eulerian-orientation combinations are
   generated, deduped by pynauty directed certificates, and each member re-passes
   `is_2extremal`. This is a genuinely complete generation of L_n for n<=7.
2. **The oracle (is_in_H2) is SOUND but INCOMPLETE.** Every *True* is backed by an
   explicit derivation into strictly-smaller recognised pieces — no spurious membership.
   But a *False* means only "no derivation found within the searched space"; known gaps
   are `max_internal<=2` on tree-internal vertices, the empty-A generalised-wheel branch
   (the n=7 miss above), single-connected-residual-block tiling, and contiguous-block
   planar leaf assignment. **A "not in H_2" verdict is therefore a CANDIDATE, never a
   proof of non-membership** — exactly as the n=7 episode demonstrated.

**Bottom line:** empirical survival to n=7, every flag refuted by hand. This is
*evidence*, not a theorem. The recon "lean disprove" prior is neither confirmed nor
refuted; no counterexample exists and none is ruled out beyond n=7.

---

## 2. PROOF TRACK — what is established, and the load-bearing open sub-lemma

The proof strategy is an **inductive seam-and-reassembly** program built on the paper's
min-dicut induction (Lemma 3.3), corrected for the k=2 regime (`docs/proof_attempt.md`).

### Established
- **k=2 failure mode of Lemma 3.3 is pinned down.** A strong digraph has no global
  directed cut, so the paper's "size-k dicut" must be read as a minimum (s,t)-dicut
  (the lambda-witness). The reductive size-2 min-(s,t)-dicut in L<=5 occurs **only** on
  C3#C3, exactly where no optimal 3-dicolouring is monochromatic on either side
  (constS=constT=False) — the precise k=2 degradation. Crucially, the min-(s,t)-dicut
  **certifies lambda=2 but is NOT the reassembly seam**: the directed-Hajos seam is a
  single identified vertex; the tree-join seam is a digon. (Corrects the naive
  "contract a dicut side" program.)
- **B-parity is the correct extremality criterion (strongly supported).** Over a
  combined 62-case sweep (44 with C3 gadget, 18 with C5; 5 plane trees x all A/B
  labelings, up to 11 vertices), the even-leaf-path B-parity condition is
  **necessary-and-sufficient** for a 2-Hajos tree join to be 2-extremal, with **zero**
  disagreements. Smallest witness: path 0-1-2, one A-edge + one B-digon -> 1 B-edge
  (odd) -> chi_vec=2 (not extremal); flip B->A -> 0 B-edges (even) -> chi_vec=3 (extremal).
  This confirms the brief's hypothesised repair.
- **Directed Hajos join alone is insufficient** — W3 (n=4), W4 (n=5) are generalised
  wheels (empty-A tree joins) and are needed already at n=4.

### The load-bearing open sub-lemma
**Lemma A (Seam Existence).** *Every 2-extremal digraph that is not a symmetric odd
cycle and not a generalised wheel contains either a directed-Hajos merge vertex or a
peripheral B-edge cut digon.*

This is the single unsupported crux of the induction. It currently has only n<=5
support and **no proof**. Two supporting steps are also conjectural:
- **Lemma B** (a split forces both pieces 2-extremal) — verified only on C3#C3.
- **Lemma C** sufficiency (B-parity => 2-extremal for *all* trees/gadgets) — open;
  only a criticality / odd-closed-walk mechanism sketch, no symbolic proof of the
  peripheral-cycle colouring step.

---

## 3. THE SINGLE MOST DECISIVE NEXT STEP

**Test Lemma A (Seam Existence) on the full enumerated truth sets L_6 and L_7 — the
first dataset large enough to either break the proof program or harden it.**

This is decisive because Lemma A is the only load-bearing unproved step, and we now
hold, for the first time, complete truth sets (47 members across n=6,7) that were
unavailable when `proof_attempt.md` was written (its empirical claims stopped at n=5).
Concretely, for every member of L_6 ∪ L_7 that is neither a symmetric odd cycle nor a
generalised wheel:
1. Search for a directed-Hajos merge vertex (articulation point of the underlying
   graph) **or** a peripheral B-edge cut digon (a digon whose removal separates the
   digon-subgraph). Record which seam type appears, or NONE.
2. **If any member has NO seam -> Lemma A is FALSE**, the induction as stated is dead,
   and that member is the structural obstruction to characterise (a new base class or a
   third join). This would be the highest-value outcome.
3. **If every member has a seam**, additionally verify Lemma B on each split (both
   pieces land back in the enumerated L_{<n}). A clean pass over 47 members would
   promote Lemma A from n<=5 to n<=7 support and justify investing in its symbolic
   proof via the "digon-graph bridge/separator" handle already sketched.

Prerequisite, cheap and high-leverage: **patch the oracle's empty-A generalised-wheel
branch** (the documented n=7 miss) so the seam-search is run against a correct H_2
classifier — otherwise generalised wheels will be misrouted into the Lemma-A search and
produce spurious "no-seam" results. This patch is a few lines and was already specified
by the verify pass (detect a spanning digon-tree whose leaves carry the single-arc
peripheral directed cycle with even leaf-to-leaf parity).

Secondary, only if engineering budget allows: a C-accelerated strong/lambda primitive
to push enumeration to n=8 (the paper's Figure-11 prize regime). The pure-Python
enumerator is measured to exceed budget at n=8 (7123 biconnected graphs, >100M Eulerian
orientations). This extends *evidence* but, unlike the Lemma-A test, does not advance
the *proof*.

---

### Discipline reminder
Empirical survival to n=7 is **not** a theorem. The entire characterisation rests on
the unproved Lemma A. Every "not-in-H_2" verdict from the current oracle is a candidate
requiring hand verification (the oracle is sound but incomplete), as the refuted n=7
flag concretely showed.

### Key artifacts
- Enumerator: `scripts/enumerate.py`; truth sets `data/L_3.json`…`data/L_7.json`
- Oracle (sound, incomplete): `scripts/h2_oracle.py` (+ `tests/test_h2_oracle.py`)
- Proof analysis: `docs/proof_attempt.md`; constructors/probes
  `scripts/two_hajos_tree_join.py`, `scripts/parity_necessity_sweep.py`,
  `scripts/dicut_induction_probe.py`
- Red-team refutation of the n=7 flag: `docs/counterexample_verification.md`,
  `scripts/redteam_verify.py`, `scripts/redteam_closure.py`
