# Inverse rim extraction — where does the peripheral rim come from? (R-b existence)

Date: 2026-06-02. Script: `scripts/inverse_rim_audit.py`.

## The question

The MC-inheritance lemma (proved, `docs/tree_join_mc_inheritance.md`) settles the
*forward* constraint: the A-blocks of any `MC=0` 2-Hajós tree join must be
`MC=0`/base. It does **not** produce a decomposition. R-b's open half is the
*inverse*:

> Given a non-base `MC=0` 2-extremal digraph `D`, exhibit a valid 2-Hajós tree-join
> **rim** (peripheral directed cycle) and `(A,B)` partition with strictly-smaller
> `MC=0`/base blocks.

So the live obstruction is purely: **which directed cycle of `D` is the rim, and
what underlying-graph feature singles it out?**

## Method

The oracle's `_tree_join_decompositions` returns only the A-blocks, hiding the
rim. `full_decompositions` (in the audit) mirrors the same search but yields the
**whole** decomposition `{rim, A, B, tree vertices, blocks}`, so each recovered
rim can be correlated against the digon forest `F_D` and the single-arc
subdigraph. Recall (proved earlier): `F_D` (the digons) is a forest, and the
single arcs are balanced = a union of closed directed trails.

Candidate rim selectors tested per recovered rim `R`:

- **S1** — `R`'s arcs are all **single** arcs of `D` (the rim avoids every digon).
- **L1** — `V(R) ⊆ leaves(F_D)`.
- **L2** — `V(R) = leaves(F_D)`  (the originally-proposed "rim = leaf set of the
  digon-forest skeleton").

## Result

Corpus = the 3 genuine truth-set `MC=0` non-base members `{L7.7, L7.14, L7.36}`
plus the 11 forward-built recursive `n=9` iso-classes (14 total).

| selector | holds (every recovered rim, every digraph) |
|---|---|
| **S1 — rim is a single-arc directed cycle** | **14/14** |
| L1 — `V(R) ⊆ leaves(F_D)` | 6/14 |
| **L2 — `V(R) = leaves(F_D)`** | **0/14 (REFUTED)** |

**The rim is always a directed cycle of the single-arc subdigraph.** The
single arcs are balanced, so they cycle-decompose (here: two directed triangles,
or a "bowtie" of two triangles sharing a vertex — `L7.36`); the rim is **one of
those single-arc cycles**.

The originally-proposed `F_D`-leaf rule is **wrong**:
- `L2` fails everywhere (the rim is a 3-cycle; `F_D` has 4–6 leaves).
- `L1` is not uniform: `L7.7` has a valid rim `[2,4,6]` running through the
  *internal* `F_D` vertex `6`, while `fwd0` *rejects* the single-arc cycle
  `[1,6,8]` precisely because `8` is internal. So leaf-membership is neither
  necessary nor the selector.

**The selector is single-arc structure, not the digon forest's leaves.**

### Which single-arc cycle? — the selector is GLOBAL, not local (pinned)

When the single arcs split into two cycles, sometimes **both** are valid rims
(`decomps=2`: `L7.7, L7.14, fwd2, fwd5, fwd10`) and sometimes only **one** is
(`decomps=1`: the rest). `pin_selector_probe` (in the audit) tests, over all 28
candidate single-arc cycles of the 14-digraph corpus (20 valid, 8 invalid),
whether any **local** feature of a cycle coincides with being a valid rim:

| local feature of candidate cycle `R` | `== valid` on all 28? |
|---|---|
| `V(R) ⊆ leaves(F_D)` | 14/28 |
| `R` induced in `U(D)` (chordless) | 20/28 |
| `U(D) − V(R)` connected (non-separating, vertices) | 20/28 |
| `U(D)` − rim arcs connected (non-separating, arcs) | 20/28 |
| `R` is a face of a planar embedding of `U(D)` | 20/28 |

**No feature reaches 28/28 — none is a selector.** Strikingly, **every**
candidate single-arc cycle (valid *and* invalid) is a chordless, non-separating,
planar **face**: the invalid `[1,6,8]` of `fwd0` is just as much a face as the
valid `[4,5,7]`. `U(D)` is only 2-connected (not 3-connected), so faces are
embedding-dependent and both triangles bound faces. Validity (20 vs 8) is
**orthogonal** to all of these.

**What actually decides it.** `R` is a valid rim iff `A(D) ∖ R` tiles into
B-digons (even leaf-parity) + valid (`MC=0`/base) A-blocks — the *global,
recursive* tiling condition. Structurally: the single arcs form **nested** rims;
the rim is the **outermost** cycle, and the inner single-arc cycles are the
blocks' own wheel-rims. In `fwd0`, removing `[4,5,7]` leaves the single triangle
`[1,6,8]` as the rim of a 6-vertex generalised-wheel block; removing `[1,6,8]`
leaves `[4,5,7]`, whose digon attachments do **not** form a valid block. So which
cycle is "outermost" is fixed by the whole digon-attachment pattern, not by any
local property of the cycle.

**Consequence for the proof (step 4):** do **not** seek a local rim-selector.
Prove existence by *peeling*: show some single-arc directed cycle can be removed
to leave a strictly-smaller valid structure, then recurse (the `MC`-inheritance
corollary guarantees the residual blocks are `MC=0`/base). The negative result
above tells us the induction must be on the global nesting, not a one-shot local
choice.

**Step 4 attempted — see `docs/peeling_recursion_proof.md`.** Outcome: a clean
reduction `R-b ⟺ Step1∧Step2∧Step3`, with Step 1 **proved** (a single-arc rim
candidate always exists), Step 2 **provable bookkeeping** (`EXTREMAL-b`, the R-a
template), and Step 3 — existence of a *peelable* rim — **open**, equal to the
`k=2` base-case dichotomy AAC leave as Conjecture 9.2. The "peel the outermost
nested rim" lever is gated on `U(D)` being planar with a canonical embedding
(verified 836/836 but unproven, and `U(D)` is only 2-connected). The attempt does
**not** close R-b.

## Red-team (step 3)

Against the corrected absorption builder's **822 non-base `MC=0` outputs** (the
builder's 1841 distinct `MC=0` outputs include base generalised wheels; the 822
are the non-base ones), `n ≤ 11`:

- **822/822** have single arcs that are balanced **and** contain a directed cycle
  — the necessary precondition for a single-arc rim to exist.
- Full rim recovery on a deterministic stride sample of **64**: **64/64** admit
  ≥1 decomposition, and **64/64** have *every* recovered rim single-arc (S1).

**Caveat (honesty).** The 822 are *forward-built* tree joins, so their rim is a
single-arc cycle largely *by construction* — S1 on them is partly circular (the
real content is that no block/B-edge ever reverses a rim arc into a digon, which
S1 confirms). The genuinely independent evidence is the **3 truth-set members**,
where S1 is a real, non-tautological finding. The oracle also caps
`max_internal=2`. A decisive test needs the `n=8` truth set (not yet enumerated)
or non-forward `MC=0` digraphs.

## Revised target for step 4 (proof)

The rim-extraction lemma to attempt is single-arc-based, **not** `F_D`-leaf-based:

> **Rim-extraction lemma (target).** Let `D` be a non-base `MC=0` 2-extremal
> digraph. Its single-arc subdigraph `S` is balanced and non-empty (pure-digon ⇒
> symmetric ⇒ base), hence contains a directed cycle. **Claim:** some directed
> cycle `R ⊆ S` is the peripheral rim of a valid 2-Hajós tree join — i.e.
> `A(D) ∖ R` tiles into digons (B-edges, even leaf-parity) and `MC=0`/base
> A-blocks.

This is a purely underlying-graph statement in the proved vocabulary (`F_D`
forest + single-arc closed trails + `MC=0`). The existence of a candidate rim is
free (balanced ⇒ has a cycle); the work is showing some choice leaves a valid
tiling, and the `MC`-inheritance corollary guarantees any blocks produced are
`MC=0`/base.

## Reproduce

```bash
uv run python problems/two_extremal_digraphs/scripts/inverse_rim_audit.py
```
