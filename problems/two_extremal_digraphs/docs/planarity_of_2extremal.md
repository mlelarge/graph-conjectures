# Planarity of 2-extremal digraphs — a proved direction, a new disproof target, and why route (a) is circular

Date: 2026-06-03. Follow-up to `docs/peeling_recursion_proof.md` (route (a):
"prove `U(D)` planar to unlock the outer-face rim route").

## TL;DR

1. **[THEOREM, proved]** `D ∈ H₂  ⇒  U(D)` is planar. Structural induction; the
   one non-trivial step (directed Hajós join preserves planarity) is proved below.
2. **[COROLLARY]** Every **non-planar** 2-extremal digraph is a **counterexample to
   Conjecture 9.2**. This is a new, concrete *disproof* target.
3. **[CONJECTURE-P]** `2-extremal ⇒ U(D)` planar. This is exactly "no such
   counterexample exists." It is the **necessary-condition** form of Conjecture 9.2
   (implied by it via the Theorem), **not** an independent foothold.
4. **Planarity is NOT MC-specific.** All 52 genuine truth-set members (`L₃..L₇`,
   `MC=0` and `MC≥1` alike) are planar; so is every generator output. The earlier
   "836/836 `MC=0` planar" was reading an MC-independent fact through an MC-shaped
   window.
5. **Route (a) is circular.** Using planarity to *prove* R-b needs the forward
   direction `2-extremal ⇒ planar` (CONJECTURE-P), which we can only obtain from
   `H₂`-membership — i.e. from the very conclusion R-b is meant to establish. The
   only planarity we can prove (`H₂ ⇒ planar`) is useless for R-b.

---

## 1. Theorem: `H₂ ⇒ U(D)` planar

*By structural induction on the `H₂` construction.*

- **Base — symmetric odd cycle.** `U` is a cycle: planar. ✓
- **2-Hajós tree join `T(D₁,…,D_a; C)`.** `T` is a *plane* tree; draw it in the
  plane. Replace each B-edge by a digon (parallel edges in the same slot — planar),
  each A-edge `{u_i,v_i}` by `U(D_i)` (planar by induction) drawn inside a small
  disk around that tree edge with `u_i,v_i` on the disk boundary, and the rim `C`
  as a directed cycle through the leaves along the outer boundary. The whole figure
  is plane. ✓
- **Directed Hajós join `D₁ ▽ D₂`** (w.r.t. arcs `u→v₁ ∈ D₁`, `v₂→w ∈ D₂`: delete
  them, identify `v₁=v₂=:v`, add `u→w`). `U(D₁),U(D₂)` planar by induction, both
  2-connected. In a 2-connected plane graph every edge lies on a face, so:
  embed `U(D₁)` with edge `{u,v}` on the boundary of a face `F₁` (so `u,v ∈ ∂F₁`);
  embed `U(D₂)` with `{v,w}` on its outer face (so `v,w` on the outer boundary).
  `v` is a **cut-vertex** of the vertex-amalgam, so insert the entire `U(D₂)`
  drawing into face `F₁`, attached only at `v`. The outer face of `U(D₂)` then
  merges with `F₁` into a single face whose boundary contains `u` (from `D₁`'s side)
  and `w` (from `D₂`'s side). Hence `u,w` are co-facial: add edge `{u,w}` inside
  that face without crossings. Deleting the arcs only removes edges. The result is
  plane. ∎

*Computational check:* every `H₂`-built digraph tested is planar — 52 genuine
truth-set members (`L₃..L₇`), 12 698 distinct directed-Hajós joins (`N≤10`,
exhaustive over join-arc pairs of `L₃..L₇` blocks), and the 836 tree-join `MC=0`
outputs. **0 non-planar.**

## 2. Corollary and the disproof target

Contrapositive of the Theorem: **a non-planar 2-extremal digraph cannot be in `H₂`,
so it disproves Conjecture 9.2.** This is attractive because it is a *single
local-ish certificate* (a `K₅`/`K₃,₃` subdivision in `U(D)`) rather than a global
seam-existence failure. The `H₂`-based generators **cannot** find it (they only
build planar members, by the Theorem); a counterexample must come from direct
enumeration or from orienting a non-planar graph.

**Search so far (no counterexample found):**
- `K₅`: all `3^{10}=59 049` digon/orientation assignments — **0** are 2-extremal.
- `K₃,₃`: all `3^{9}=19 683` assignments — **0** are 2-extremal.
- `geng` sweep of non-planar 2-connected min-deg-≥2 graphs, **exact**
  Eulerian-pruned 2-extremal-orientation search (`scripts/planarity_search.py`,
  validated against naïve `3^{|E|}`): `n=7, |E|≤16` → 155 non-planar graphs, **all
  exhaustively tested, 0** admit a 2-extremal orientation; `n=8, |E|≤18` → 3418
  non-planar graphs, **all exhaustively tested, 0**. (The earlier capped
  `4·10⁵`/graph sweep is superseded — the Eulerian-pruned enumerator removes the
  cap. Coverage caveat: `|E|≤2n+2` excludes dense non-planar graphs at `n=8`, but
  those have high connectivity and are unlikely to be `λ=2`.)

So CONJECTURE-P (`2-extremal ⇒ planar`) survives every test; equivalently no
non-planar-certificate counterexample to 9.2 has surfaced.

## 3. Why route (a) does not unlock R-b — it is circular

The peeling proof's planar route (3-pl) needs: *a non-base `MC=0` 2-extremal `D`
has planar `U(D)`, with a face bounded by a single-arc dicycle whose removal opens
`D` into the tree-of-blocks.* The **planarity premise** is CONJECTURE-P (forward
direction). But:

- `H₂ ⇒ planar` is proved — yet it presupposes `D ∈ H₂`, which for an `MC=0`
  non-base `D` is *exactly* what R-b must establish. Useless as an input to R-b.
- `2-extremal ⇒ planar` (the usable premise) is the **necessary-condition form of
  Conjecture 9.2** and we have **no independent proof** of it; obtaining it would
  itself be a substantial advance (or it would follow from the conjecture).

So planarity cannot be *assumed* en route to R-b without circularity, and the only
planarity we can *prove* is the wrong direction. **Route (a) does not crack Step 3.**

It does, however, convert into route (a′): **attack Conjecture 9.2 by disproof** —
hunt a non-planar 2-extremal digraph (now a clean, well-defined search), or prove
CONJECTURE-P independently (a real, possibly-easier-than-9.2 sub-theorem, since it
is only a necessary condition). Even the latter would not prove 9.2, but a failure
of CONJECTURE-P *would* refute it.

## 4. Status of CONJECTURE-P

| evidence | result |
|---|---|
| genuine truth set `L₃..L₇` (52, all MC) | planar 52/52 |
| directed-Hajós joins, `N≤10` (12 698) | planar 12 698/12 698 |
| tree-join `MC=0` outputs (836) | planar 836/836 |
| `K₅`, `K₃,₃` (exact, Eulerian-pruned) | 2-extremal 0 |
| `geng` non-planar `n=7` (all `|E|`, exact) | 2-extremal 0/25 graphs |
| `geng` non-planar `n=8, |E|≤23` (exact) | 2-extremal **0/4210** graphs |
| `geng` non-planar `n=8, |E|≥24` (20 near-`K₈`) | 2-extremal **0/20** (15 by lemma, 5 by forest search) |
| `geng` non-planar `n=9` (all `|E|`, 157570) | 2-extremal **0** (21920 by lemma, 135650 searched) |
| **⇒ no non-planar 2-extremal at `n≤9`** | **fully certified** |

Decisive open test: the **`n=8` truth set** (the long-standing enumeration
barrier) would check CONJECTURE-P on all genuine `n=8` 2-extremal digraphs at once.

**Edge-connectivity lemma [PROVED].** *Every 2-extremal digraph has **max local
edge-connectivity** `λ'(U(D)) ≤ 4`* — i.e. no pair of vertices has `≥5`
edge-disjoint paths in `U(D)`. (This is strictly stronger than `κ'(U)≤4`, which is
the *minimum* local edge-connectivity and follows as a corollary.)

*Proof.* Write `D` = digons `F_D` + single arcs `S`; `S` is balanced (Eulerian),
so for every cut `S₀` the single arcs split evenly, giving
`arcs(S₀→S̄₀) = d + |E_single(S₀)|/2 = (d + |E_U(S₀)|)/2` where `d` = digons
crossing. Hence for any pair `u,v`,
`λ_D(u,v) = min_{S₀ sep u,v}(d + |E_U(S₀)|)/2 ≥ λ'_U(u,v)/2`. Since `λ(D) = max_{u,v}
λ_D(u,v) = 2`, we get `λ'_U(u,v) ≤ 4` for **every** pair. ∎
*(Verified: all 52 truth-set members have `λ'(U) ≤ 4` — and `κ'(U) ≤ 3`.)*

This lemma is the workhorse of the disproof: any non-planar graph with a pair of
`≥5` edge-disjoint paths cannot host a 2-extremal orientation, certified by a
single Gomory-Hu computation with no orientation search.

**`n=8` disproof hunt — COMPLETE (2026-06-04, `scripts/n8_disproof.py` +
edge-connectivity lemma).** Over **all 4230** non-planar 2-connected min-degree-2
graphs on `n=8`: **0 admit a 2-extremal orientation.**
- `|E|≤23` (4210 graphs): exhaustive via the exact Eulerian-pruned enumerator.
- `|E|≥24` (20 near-`K₈`): **15** killed immediately by the edge-connectivity
  lemma (`κ'(U)≥5`); the remaining **5** (`κ'≤4`) certified by a forest-constrained
  exhaustive search (using `F_D` forest ⇒ `≤7` digon edges; ≤10⁶ candidate
  digraphs each, all rejected).

So **no non-planar 2-extremal digraph exists at `n≤8`** (fully certified). No
counterexample to Conjecture 9.2.

**`n=9` disproof — COMPLETE (2026-06-06).** Over **all 157570** non-planar
2-connected min-degree-2 graphs on `n=9`: **0 admit a 2-extremal orientation.**
- `|E|≤22` (135650 graphs): exhaustive Eulerian-pruned search (no caps).
- `|E|≥23` (21920 graphs): **all** killed by the max-local-edge-connectivity lemma
  (`λ'(U)≥5`), instantly — this is what made `n=9` tractable (the earlier `κ'≤4`
  form was too weak and the run stalled on dense `|E|=23` until the strong lemma
  replaced it).

So **no non-planar 2-extremal digraph exists at `n≤9`** (fully certified, gap-free).
CONJECTURE-P (`2-extremal ⇒ planar`) survives through `n=9`; no counterexample to
Conjecture 9.2. The max-local-edge-connectivity-`≤4` lemma is an unconditional
structural constraint on all 2-extremal digraphs and the key enabler.

## Reproduce

The `K₅`/`K₃,₃`/`geng` disproof search and the 3-connected classification are in
`scripts/planarity_search.py` (exact Eulerian-pruned enumerator, validated against
naïve `3^{|E|}`):

```bash
PYTHONPATH=problems/two_extremal_digraphs/scripts \
  .venv/bin/python problems/two_extremal_digraphs/scripts/planarity_search.py
```

The `H₂`/truth-set/Hajós-join planarity tallies reuse `h2_oracle`, `seam_invariant`,
and `networkx.check_planarity`.
