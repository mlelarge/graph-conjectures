# The peeling-recursion proof of R-b — attempt, and the precise gap

Date: 2026-06-03. Companion to `docs/inverse_rim_extraction.md`.

> **Up front.** Fully proving the peeling lemma **is** proving Conjecture 9.2 at
> `k=2`, which arXiv:2304.04690 leaves open (it has no `k=2` analogue of its
> base-case dichotomy, Lemma 4.5/4.6). This memo does **not** close it. It gives a
> clean reduction `R-b ⟺ Step1 ∧ Step2 ∧ Step3`, **proves Step 1**, argues **Step 2**
> is provable bookkeeping (the `EXTREMAL-b` analogue of the completed `R-a`), and
> isolates **Step 3** as the irreducible open core — showing *why* the pinned
> "no-local-selector" result forces any proof to be global/recursive, and where the
> minimal-counterexample argument stalls. Tags: **[PROVED]**, **[PROVABLE/sketch]**,
> **[VERIFIED, not proven]**, **[GAP]**, **[CONJECTURE]**.

## The lemma and the induction

**Peeling Lemma (target).** Let `D` be a non-base `MC=0` 2-extremal digraph. Then
its single-arc subdigraph `S` contains a directed cycle `R` (the *rim*) such that
`A(D) ∖ R` is a 2-Hajós tree-join interior: a plane tree `T` with an even-leaf-parity
`(A,B)` partition, `leaves(T) = V(R)` in cyclic order, each B-edge realised as a
digon of `D∖R`, each A-edge realised as a strictly-smaller 2-extremal block `D_i`,
and `R` the peripheral cycle, so `D = T(D_1,…,D_a; R)`.

**This gives R-b by induction on `|V(D)|`.** Base objects (symmetric odd cycles,
generalised wheels) are in `H₂` by definition. For non-base `D`: if `MC(D)=1` use
the proved directed-Hajós side (R-a, modulo R-a★); if `MC(D)=0` apply the Peeling
Lemma, recurse into each block `D_i` (smaller, and `MC=0`/base by the proved
inheritance corollary, so the recursion stays in this same case until it hits base
objects). Hence `D ∈ H₂`. ∎ *(modulo the three steps below.)*

## Notation and standing facts (all previously established)

`D` 2-extremal ⇒ Eulerian (`indeg=outdeg≥2`), strong, `U(D)` 2-connected, `λ=2`,
`χ⃗=3`, and 3-dicritical. Write `F_D` for the digon graph (**a forest**, proved) and
`S` for the single arcs. At every vertex `s⁺(v)=s⁻(v)=:s(v)` (singles balanced),
and `d_F(v)+s(v) = indeg(v) ≥ 2`.

---

## Step 1 — a candidate rim exists. **[PROVED]**

*Claim.* `S` is non-empty and contains a directed cycle.

*Proof.* If `S=∅` then every arc lies in a digon, so `D` is symmetric. For a
symmetric digraph `χ⃗(D)=χ(U(D))` and `λ(D)=` edge-connectivity of `U(D)`;
2-extremality + 3-dicriticality make `U(D)` a 3-chromatic vertex-critical graph,
which (Dirac/Gallai) is an **odd cycle** — a base object. As `D` is non-base,
`S≠∅`. Since `S` is balanced (`s⁺=s⁻` everywhere) and non-empty, following
out-arcs must repeat a vertex, yielding a directed cycle. ∎

**Refinement [VERIFIED, not proven].** A non-base `MC=0` 2-extremal has **≥2**
distinct single-arc directed cycles (so the rim choice is genuinely non-unique).
*Verified 836/836* (`{2:749, 3:87}`); generalised wheels have exactly 1. The
clean boundary statement behind it,

> **(W)** if `S` is a *single* directed cycle then `D` is a generalised wheel,

is **[CONJECTURE]**: its proof needs the leaf cyclic-order to match a plane
embedding — the same embedding gap that appears in Step 3 — so it is *not* an
independent lever.

---

## Step 2 — any valid peel yields smaller 2-extremal `MC=0`/base blocks. **[PROVABLE/sketch]**

Suppose `R` is peelable with blocks `D_i = D[V_i] + [u_i,v_i]` (interface digon
re-added). This is the `EXTREMAL-b` analogue of the **completed** `EXTREMAL-a`
(`docs/seam_k2_degradation.md §2`); the clauses transfer:

- **`a ≥ 1` and blocks proper/smaller [PROVED].** If `a=0` the interior is all
  B-digons, making `D` a generalised wheel — base, contradiction. So `a≥1`; rim
  vertices and pure-B tree-nodes lie outside every `V_i`, so `|V_i|<|V(D)|`.
- **`MC=0`/base [PROVED].** Immediate from the proved MC-inheritance corollary
  (an `MC=0` tree join uses only `MC=0`/base A-blocks).
- **Eulerian [PROVED, identical to R-a.4].** Off `{u_i,v_i}` in/out are inherited;
  the re-added interface digon `[u_i,v_i]` restores balance at `u_i,v_i` by the
  same one-for-one swap as the R-a merge-vertex computation.
- **strong, `λ=2`, `U(D_i)` 2-connected [SKETCH, R-a template].** The block is a
  "side" of the join, attached to the rest only at `{u_i,v_i}`; the interface digon
  plus block-internal connectivity give 2-connectivity, and Eulerian + weakly
  connected ⇒ strong, single-arc reroute ⇒ `λ=2`. Mirrors R-a §2.2 clauses; not
  re-derived here.
- **`χ⃗(D_i)=3` [SKETCH, BJSS].** Lower bound: BJSS Lemma 6.7 (the tree-join
  colouring bound, `k≥2`, in-paper) forces each block to need 3 colours. Upper
  bound: restrict a 3-dicolouring of `D` to `V_i` and fix the interface digon.
  Exact citation/verification flagged, as in the R-a colouring discharge.

So Step 2 is bookkeeping of the same character as the closed `EXTREMAL-a`; the two
fully-airtight clauses are `a≥1` and `MC=0`/base, the rest follow the R-a template.

---

## Step 3 — a peelable rim exists. **[GAP] = the `k=2` base-case dichotomy**

This is the open heart. Two clean reformulations:

- **(3-bc) block-cut form.** `∃` single-arc dicycle `R` such that `U(D)` minus
  `R`'s edges has block-cut tree `=` a tree whose 2-connected blocks are the
  (smaller, 2-extremal) A-blocks, with bridge/cut structure realising B-digons of
  even leaf-parity. *(Removing `R` must drop `U(D)` from 2-connected to a tree of
  2-connected blocks — verified: 0/14 stay 2-connected after rim removal.)*
- **(3-pl) planar form.** `U(D)` is planar **[CONJECTURE; VERIFIED 836/836
  non-base `MC=0`]**, and `∃` a face whose boundary is a single-arc dicycle whose
  removal opens `D` into the tree-of-blocks — the "outer face" of the tree-join
  embedding.

### Why no local argument can discharge it

`pin_selector_probe` (see `inverse_rim_extraction.md`) shows the valid rim is **not**
singled out by any local feature: across 28 candidate single-arc dicycles (20
valid, 8 invalid) none of `F_D`-leaf-membership, induced-ness, vertex/arc
non-separation, or planar-face-membership coincides with validity — *every*
candidate is a chordless, non-separating, planar face, valid or not. So Step 3
cannot be met by "choose the cycle with local property X"; it requires a global /
recursive certificate: `R` is valid **iff** `A(D)∖R` tiles, which is the very
decomposition we are trying to produce. This self-reference is exactly the missing
base-case dichotomy.

### Minimal-counterexample attempt, and where it stalls

Let `D` be a smallest non-base `MC=0` 2-extremal with **no** peelable single-arc
dicycle. By Step 1 (refined) `D` has `≥2` single-arc dicycles `R_1,…,R_m`. For each
`R_j`, removing it fails to give a valid interior — some 2-connected piece of
`U(D)∖R_j` is not 2-extremal, or parity fails, or a tree-node-to-tree-node arc is
left uncovered. **To reach a contradiction one must either**

1. *repair* a failing `R_j` into a peelable cycle (re-route through other single
   arcs), or
2. *contract/delete* to a smaller non-base `MC=0` 2-extremal and lift its peel.

Both stall for the same reason: nothing in `{2\text{-extremal}, MC=0, \text{non-base}}`
**produces** a single-arc dicycle whose complement is a tree-of-blocks. The pinned
no-local-selector result says the choice can't be made locally; the global
condition is self-referential; and there is no `k=2` structure theorem (the `k≥3`
proof used Lemma 4.5/4.6 here, which has no `k=2` analogue). This is precisely the
wall AAC leave as Conjecture 9.2.

### The one structural lever that survives, and its limit

The single arcs decompose into nested rims (outer = peripheral, inner = blocks'
wheel-rims; verified on the corpus). A proof would induct on this nesting: peel the
**outermost** single-arc dicycle. But "outermost" is only definable via a plane
embedding (3-pl), and `U(D)` is merely 2-connected (faces are not unique), so
"outermost" is not pinned without first proving planarity **and** canonicity of the
embedding — neither of which is in hand. Hence even the nesting lever reduces to
(3-pl), not to an independent combinatorial fact.

---

## Verdict

- **R-b ⟺ Step1 ∧ Step2 ∧ Step3**, a clean reduction.
- **Step 1: proved.** A single-arc-dicycle rim candidate always exists.
- **Step 2: provable bookkeeping** (two clauses airtight; the rest the R-a/BJSS
  template), so a *valid* peel always recurses correctly.
- **Step 3: open**, and `≡` the `k=2` base-case dichotomy. The pinned
  no-local-selector result shows it cannot be local; the natural global lever
  (peel outermost) is gated on the unproven planarity+canonical-embedding
  conjecture (3-pl). The minimal-counterexample argument has no mechanism to
  *construct* the rim. **This is the genuine residual obstruction of Conjecture 9.2
  at `k=2`; the attempt does not close it.**

## Caveats (honesty)

- **Oracle completeness.** `_tree_join_decompositions`/`full_decompositions` cap
  `max_internal=2`. At least one non-base `MC=0` example (`abs760`, `n=11`, two
  A-blocks) decomposes **only** at `max_internal≥3` — so the red-team's
  "every sampled digraph decomposes" coverage figure is conditional on lifting the
  cap; the **S1** finding (rim is single-arc) is unaffected and still holds at
  `max_internal=3` (`abs760`: 4 decompositions, all single-arc rims, `a=2`).
- **Forward-built circularity.** The 822 absorption-corpus members are forward-built
  tree joins, so "their rim is single-arc" is partly tautological; the independent
  evidence remains the 3 truth-set members and the `n=8` truth set is still unbuilt.
- **`a=2` confirmed.** The general multi-block case does occur in-corpus (`abs760`),
  so the gap is not an artifact of only testing single-block joins.

## Reproduce

```bash
PYTHONPATH=problems/two_extremal_digraphs/scripts \
  .venv/bin/python problems/two_extremal_digraphs/scripts/inverse_rim_audit.py
```
(`.venv` = the root environment with `networkx`, used for the planarity / face
checks; the script degrades gracefully without it.)
