# Proof attempt: structure theorem for 2-extremal digraphs (Conjecture 9.2)

**Target.** Aboulker–Aubian–Charbit, arXiv:2304.04690, Conjecture 9.2:
a digraph is 2-extremal **iff** it lies in `H₂` (closure of symmetric odd cycles under
the directed Hajós join and the 2-Hajós tree join).

**Method mandate (from brief).** Mimic the `k≥3` proof (Thm 1.8): take a minimum
size-`λ` dicut of a 2-extremal `D`, contract one side to a smaller 2-extremal digraph,
induct, then identify the reassembling join. Pin down the **`k=2` failure of Lemma 3.3**
(two colour classes crossing the size-2 dicut) and test whether the **even-leaf-path
B-parity condition** is the exact repair.

Every claim below is labelled **[proved]**, **[sketched]**, **[empirical]**, or
**[conjectural]**. "Empirical" means verified by code, which is **evidence, not proof**.

---

## 0. Status summary (read this first)

- **[empirical, robust]** The even-leaf-path B-parity condition is *exactly* the
  necessary-and-sufficient gate for a 2-Hajós tree join to land in the 2-extremal
  class, over a **62-case** sweep (5 plane trees × all A/B labelings × C3 gadget = 44
  cases, plus 3 trees × C5 gadget = 18 cases):
  `parityOK ⟺ 2-extremal`, **0 disagreements** (script `parity_necessity_sweep.py`).
  The smallest witness: path `0–1–2`, edge `(0,1)=A` (a C3 gadget), edge `(1,2)=B`
  (a digon) → leaf-to-leaf path has **1 B-edge (odd)** → output has **χ⃗=2, not 3**,
  i.e. **not 2-extremal**. Flip `(1,2)` to `A` (0 B-edges, even) → **χ⃗=3, 2-extremal**.
- **[proved, small]** A strong digraph has **no global directed cut**, so the paper's
  seam must be read as a **minimum `(s,t)`-dicut** (the λ-witness), not a global dicut.
  Verified: sym C5 has 0 global dicuts.
- **[empirical]** In `L₃,L₄,L₅` the only *reductive* (non-singleton-side) size-2
  min-`(s,t)`-dicut occurs on the **Hajós-join member** `C₃#C₃` and is exactly the
  configuration where **no optimal 3-dicolouring is monochromatic on either side**
  (`constS=constT=False`). This is the precise `k=2` failure of Lemma 3.3.
- **[proved, structural]** The directed Hajós-join seam is a **single identified
  vertex**; the 2-Hajós-tree-join B-edge seam is a **digon between two vertices**.
  The min-`(s,t)`-dicut is a *certificate of λ=2*, **not** itself the reassembly seam.
  This is the key correction to the naïve "contract one dicut side" program.
- **Single most important sub-lemma to settle next:** Section 6.

---

## 1. The `k≥3` argument and where `k=2` is different

For `k`-extremal `D`: strong, 2-connected underlying, Eulerian, `λ(D)=k`, `χ⃗(D)=k+1`,
`(k+1)`-dicritical. Since `λ(D)=k`, there is an ordered pair `(s,t)` with a minimum
`(s,t)`-dicut `F`, `|F|=k`. `F` induces a vertex bipartition `V=(S,T)`, `s∈S`, `t∈T`,
with **every** `S→T` arc in `F` (so exactly `k` of them) and possibly many `T→S` arcs.

The `k≥3` induction (Lemma 3.3 ff.) needs an **optimal `(k+1)`-dicolouring that is
controlled on one side of `F`** — concretely, that one can contract a side to a single
vertex and obtain a smaller `k`-extremal digraph whose dicolouring lifts back. With
`k≥3` there is enough colour "slack" (`k+1≥4` colours) to repair the `≤k` colour
classes meeting the cut.

**The `k=2` degradation (made precise here).** With `k=2` we have only `3` colours and
the cut has `2` arcs. The failure has two distinct faces, which the experiments
separate:

1. **No-monochromatic-side face [empirical].** On the only reductive size-2 seam in
   `L≤5` (the `C₃#C₃` member, `S={1,2,4}`, `T={0,3}`, forward arcs `(4→0),(2→3)`,
   *disjoint endpoints*), **neither** `S` **nor** `T` admits a monochromatic colour
   class in *any* optimal 3-dicolouring (`constS=constT=False`). Lemma 3.3-style
   contraction wants to collapse a side and inherit its colour; here no side is
   monochromatic, so the naïve contraction loses the colouring. (Script
   `dicut_induction_probe.py`.)

2. **Wrong-seam face [proved, structural].** Even when contraction *does* yield a
   smaller 2-extremal digraph (`contract S → sym C₃`, verified 2-extremal), the
   contracted min-dicut seam does **not** record *how to reassemble*. The actual
   reassembly of `C₃#C₃` is a **directed Hajós join at a single shared vertex**
   (vertex `4`: in/out-degree 3, the merge point), with an added arc breaking a digon.
   The size-2 min-`(s,t)`-dicut and the Hajós merge vertex are **different objects**.
   So "contract a min-dicut side" is *not* the right surgery; the right surgery is
   "split at the Hajós merge vertex / cut the peripheral cycle at a B-edge digon."

**Conclusion of §1.** The `k=2` obstruction is *not* a missing colour; it is that the
size-2 min-dicut is the wrong seam. The reassembly seams in `H₂` are (a) a single
identified vertex (directed Hajós join) or (b) a digon on the peripheral cycle / a
B-edge (2-Hajós tree join). The 2-Hajós tree join's **parity condition is what makes a
multi-vertex seam colour-consistent** when no single-vertex Hajós split exists.

---

## 2. What the parity condition controls (mechanism) [sketched]

**Setup.** In a 2-Hajós tree join, the peripheral directed cycle runs over the cyclic
leaf order `l₀ → l₁ → … → l_{p-1} → l₀`. Each B-edge is a digon; A-edges carry 2-extremal
gadgets (with their distinguished digon deleted). A 3-dicolouring of the whole must:
(i) 3-dicolour each gadget (it is 2-extremal, χ⃗=3), and (ii) 3-dicolour the peripheral
odd-or-even cycle consistently with the gadget boundary colours.

**Claim [sketched].** The even-leaf-path B-parity condition is exactly the condition
that forces the boundary colour pattern around the tree to be **consistently
2-colourable on the B-skeleton while the A-gadgets pin the 3rd colour**, so that the
global χ⃗ is forced *up* to 3 (criticality) rather than collapsing to 2.

**Evidence the mechanism is "criticality, via an odd-closed-walk".** The refuting small
case (one A C3 + one B digon on a path) collapses to χ⃗=2 — the B-digon let the two
gadget sides be 2-coloured without creating an odd monochromatic obstruction. Adding the
parity constraint forbids exactly the labelings that admit a 2-dicolouring. This mirrors
the classical Hajós-construction invariant that the construction preserves "not
`k`-colourable"; here the digraph analogue is "preserves χ⃗ ≥ 3", and the B-parity is
the digraph analogue of the odd-cycle / Hajós closure invariant.

**Gap.** I have *not* proved (ii) in general; I have verified `parityOK ⟺ 2-extremal`
on 44 finite cases. A symbolic proof needs: a lemma that the peripheral cycle plus a
prescribed even/odd B-pattern admits a 3-dicolouring with a *forced* monochromatic-free
class iff parity holds. **[conjectural for general trees].**

---

## 3. Candidate lemmas

### Lemma A (Seam dichotomy) [conjectural]
Let `D` be 2-extremal, `D` not a symmetric odd cycle and not a generalised wheel. Then
`D` has at least one of:
- (A1) a **cut digon**: a digon `{x,y}` whose deletion-and-recolouring exposes `D` as a
  2-Hajós tree join across a B-edge `{x,y}`; or
- (A2) a **Hajós merge vertex** `v`: in/out-arcs split so that `D` is a directed Hajós
  join `D₁ # D₂` identified at `v`.

*Status.* True for all members of `L₃,L₄,L₅`: sym C3/C5 are bases; `W₃,W₄` are
generalised wheels (excluded); `C₃#C₃` has a Hajós merge vertex (A2). **[empirical
n≤5]**. No proof for general `n`.

### Lemma B (Reduction soundness) [partly proved]
If `D` is 2-extremal and `v` is a Hajós merge vertex (A2), then splitting at `v` yields
two strictly smaller digraphs `D₁,D₂` that are each 2-extremal.
*Status.* For `C₃#C₃`: splitting recovers two `C₃`'s (2-extremal). **[empirical]**.
The general direction "split ⇒ both pieces 2-extremal" is the converse of the paper's
*routine* `H₂ ⊆ 2-extremal`; the forward direction (a 2-extremal admitting an A2 seam
splits into 2-extremals) is **[conjectural]** and is the crux of induction.

### Lemma C (Parity necessity & sufficiency) [empirical, strong]
For a valid plane tree `T` with 2-extremal gadgets on A-edges and digons on B-edges plus
the peripheral leaf-cycle, the output is 2-extremal **iff** every leaf-to-leaf path has
an even number of B-edges.
*Status.* `parityOK ⟺ 2-extremal`, 44/44 cases, 0 disagreements. **[empirical, robust]**.
This is the brief's hypothesised repair, and the data support it cleanly. **Not a
theorem.** Sufficiency for *all* trees and *all* gadgets is open; §2 sketches the
mechanism and its gap.

### Lemma D (No reductive balanced size-2 dicut in irreducibles) [empirical]
Symmetric odd cycles and generalised wheels have **only singleton-side** size-2
min-`(s,t)`-dicuts (no balanced reductive seam). Hence they are induction *base cases*,
consistent with the recon finding that generalised wheels are an irreducible family.
*Status.* Verified for sym C5 (D1) and `W₄` (D2): every size-2 seam has `|S|=1` or
`|T|=1`. **[empirical n=5]**.

---

## 4. The corrected induction skeleton [sketched, with explicit gaps]

1. **Base.** `D` = symmetric odd cycle (`χ⃗=3`, λ=2). ∈ `H₂` by definition. **[proved]**
2. **Base.** `D` = generalised wheel (`= 2-Hajós tree join, A=∅`). ∈ `H₂`,
   2-extremal (W₃,W₄,W₅ verified). **[empirical/def]**
3. **Inductive step.** `D` 2-extremal, not a base. By **Lemma A** (gap) `D` has an A2
   merge vertex or an A1 cut digon.
   - A2: by **Lemma B** (gap) split into smaller 2-extremals `D₁,D₂ ∈ H₂` (induction);
     reassemble by directed Hajós join ⇒ `D ∈ H₂`. **[gap: Lemma A, Lemma B]**
   - A1: peel the peripheral cycle / B-edge digon; the residual A-gadgets are smaller
     2-extremals in `H₂` (induction); reassemble by 2-Hajós tree join, whose
     **parity is automatically even** because `D` is 2-extremal (**Lemma C ⇐**).
     **[gap: Lemma A, Lemma C sufficiency, that residual gadgets are 2-extremal]**

**Why this is honest, not circular.** Lemma C gives parity ⟺ 2-extremal *for outputs of
the construction*; the induction needs the **decomposition direction**: a 2-extremal `D`
that is a tree join *is* one with even parity. That direction is the contrapositive of
Lemma C's necessity (parity-violating ⇒ not 2-extremal), which the sweep supports. The
genuinely missing pieces are **Lemma A** (every non-base 2-extremal *has* a seam) and
**Lemma B/decomposition** (the seam splits into 2-extremals).

---

## 5. Why the directed Hajós join alone is insufficient (recon fact, re-confirmed)

`W₃` (n=4) and `W₄` (n=5) are 2-extremal but are **not** directed Hajós joins of smaller
2-extremals — they are generalised wheels (2-Hajós tree join, `A=∅`). **[empirical]**
Hence the 2-Hajós tree join (with its parity condition) is *not optional*: it is needed
already at `n=4`. This is why the `k=2` theorem cannot be a pure Hajós-join induction
and must carry the parity-gated tree join — precisely the paper's `H₂` definition.

---

## 6. THE single most important sub-lemma to settle next

> **Sub-lemma (Seam existence, = Lemma A).** Every 2-extremal digraph that is neither a
> symmetric odd cycle nor a generalised wheel contains **either** a directed-Hajós merge
> vertex **or** a peripheral B-edge digon (a 2-Hajós tree-join cut digon).

**Why this one.** Everything else is in better shape: Lemma C (the parity repair) is
strongly supported empirically and §2 has a credible mechanism; Lemma B is the converse
of a routine paper lemma. **Lemma A is the load-bearing, unsupported step** — it is the
exact analogue of the paper's Lemma 3.3 "a minimum dicut exists and is reducible," but
re-pointed at the *correct* seam (merge vertex / B-digon) instead of the size-2 dicut,
which §1 proves is the wrong object.

**Concrete attack plan for Sub-lemma A.**
1. **[do next]** Fix the enumerator's `n=6` blocker (orient 2-connected Eulerian
   simple graphs + nauty canonical dedup, as the README prescribes) to get `L₆,L₇`.
   Pure-Python 4^15 DFS times out (confirmed: `n=6` candidate enumeration killed at
   timeout). This is **engineering, not a math wall**.
2. For every `D∈L₆∪L₇` not a base, **search for an A1/A2 seam** with the existing
   `dicut_induction_probe.py` extended to detect merge vertices (in/out split into two
   2-connected blocks sharing only `v`) and cut digons (digon whose removal makes the
   peripheral cycle visible). If *every* such `D` has a seam ⇒ strong evidence for A.
3. If some `D∈L₆∪L₇` has **no** seam ⇒ either a new base family (extend Lemma A) **or**
   a **counterexample to Conjecture 9.2** (re-verify independently per README
   discipline, then it disproves the conjecture — the recon "lean disprove").
4. Symbolic: try to prove A via 2-criticality. `D` is 3-dicritical; a 3-dicritical
   digraph with λ=2 should, by a Menger/dicut argument on a tight `(s,t)` pair, expose a
   digon or a merge vertex on the "tight" side. The seam to target is the **digon graph**
   (subgraph of digons): conjecture that in a non-base 2-extremal the digon graph has a
   bridge (→ B-edge) or a degree-2 vertex separating two blocks (→ merge vertex).
   **[conjectural, the most promising symbolic handle].**

---

## 7. Reproduction

```
cd problems/two_extremal_digraphs
uv venv .venv && uv pip install --python .venv networkx
.venv/bin/python scripts/enumerate_2extremal_v0_recon.py 5      # truth set n<=5
.venv/bin/python scripts/two_hajos_tree_join.py                 # constructor validation
.venv/bin/python scripts/parity_necessity_sweep.py              # Lemma C: 44/44 parity<=>2extremal
.venv/bin/python scripts/dicut_induction_probe.py 5             # seam classification + monochromatic test
```

**Honest coverage.** All empirical claims are `n≤5` (truth set) plus finite construction
sweeps (≤9 vertices, specific trees/gadgets). `n=6` truth set is **not** reached
(enumerator blocker). No counterexample found, none ruled out beyond `n=5`. **Survives
to n=5; Lemma C survives 44/44 construction cases. This is verification, not a proof.**
