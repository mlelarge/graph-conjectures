# Sub-lemma A-prime — direct structural attempt via the digon forest (ANGLE 2)

**Target.** Aboulker–Aubian–Charbit, arXiv:2304.04690, toward Conjecture 9.2.

**Sub-lemma A-prime (to prove).** Every 2-extremal digraph `D` that is **not** a
symmetric odd cycle and **not** a generalised wheel admits a Lemma-A seam:
either **(a)** a directed-Hajós merge vertex, or **(b)** a general non-empty-A
2-Hajós tree-join seam.

This document attacks A-prime **directly from the digon forest** `F_D` and the
single-arc closed trails, as opposed to the dicut/colouring route of
`docs/proof_attempt.md` and the invariant route of `docs/seam_invariant.md`. It
reuses the three real theorems P1, P2, P3 and the proved necessity direction of
the mixed-2-cut invariant; it does **not** re-derive them.

Every step is labelled **[proved]**, **[sketched]**, or **[conjectural]**.
Computational tests are in `scripts/direct_structural_checks.py` (system Python,
no deps) and run against the full truth sets `L_3 … L_7`; "verified n ≤ 7" means
that script passes. **Empirical agreement over n ≤ 7 is EVIDENCE, never a proof.**

---

## 0. The reductions this angle buys, and the single wall it hits

The argument decomposes A-prime into four claims:

| label | statement | status |
|---|---|---|
| **L1** | every digon-forest leaf carries a single-in and a single-out arc | **[proved]** |
| **S1** | a non-base 2-extremal `D` has `U(D)` vertex-connectivity exactly 2 (only generalised wheels are 3-connected) | **[sketched one direction; conjectural in full]**, verified n ≤ 7 |
| **S2** | a non-base 2-extremal `D` has a **mixed 2-cut** `(v,e)` **or** a **non-edge 2-vertex cut** `{a,b}` | **[conjectural]**, verified 40/40 |
| **D1** | mixed cut ⇒ Hajós seam; only-non-edge-cut ⇒ tree-join seam (W3-type A-block) | **necessity half [proved]; sufficiency [conjectural]**, verified 40/40 |

The **wall** is the *sufficiency* half of D1: turning a combinatorial separator of
`U(D)` into a genuine decomposition into strictly-smaller **2-extremal** blocks.
S1+S2 reduce A-prime to "find a 2-vertex separator and read its type"; D1's
necessity proves the type is *necessary*; what is missing is that the type is
*sufficient* — that the two sides are 2-extremal, not merely an underlying-graph
cut. This is the same wall `seam_invariant.md §3.2` names, reached from a purely
structural side. I make the wall as small as I honestly can and state exactly
the two lemmas that would close it.

---

## 1. Setup and the proved arc decomposition [proved]

Let `D` be 2-extremal: strong, `U(D)` 2-connected, Eulerian with in=out ≥ 2 at
every vertex, `λ(D)=2`, `χ⃗(D)=3`. By **P2** the digons form a forest `F_D`; by
**P3** the single arcs (reverse absent) are balanced (in=out at every vertex) and
decompose into arc-disjoint **closed directed trails**. Write

```
E(D) = F_D  ⊔  Single(D),     U(D) = F_D  ∪  underlying(Single(D)).
```

Each digon contributes one undirected forest edge; each single arc contributes
one undirected "single edge". By **P1** no digon is a 2-arc-cut, so the literal
"cut digon" seam is vacuous and clause (b) is read in its general
non-empty-A tree-join sense (this is settled in `lemma_a.md §1`, reused here).

### Lemma L1 (leaves carry single arcs) [proved]

*Statement.* Every leaf `ℓ` of `F_D` (digon-degree exactly 1) has at least one
single-out arc and at least one single-in arc.

*Proof.* `ℓ` lies on exactly one digon `{ℓ, p}`, contributing one in-arc `p→ℓ`
and one out-arc `ℓ→p`. By the Eulerian min-degree-2 hypothesis `outdeg(ℓ) ≥ 2`,
so `ℓ` has an out-arc `ℓ→x` with `x ≠ p`. If `x→ℓ` were present, `{ℓ,x}` would be
a second digon at `ℓ`, contradicting digon-degree 1; hence `ℓ→x` is a single arc.
Symmetrically `indeg(ℓ) ≥ 2` forces a single in-arc. ∎

*Test.* `direct_structural_checks.test_L1` — PASS over all of `L_3 … L_7`.

L1 is the structural fact that lets the leaves of `F_D` play the role of the
peripheral-cycle vertices: every leaf is incident to the single-arc trails, which
is exactly what a rim must satisfy.

---

## 2. The base wall: when `F_D` spans and the rim is one cycle on its leaves

### Proposition 2.1 (generalised-wheel recognition, restated) [proved]

The recognizer `h2_oracle._is_generalised_wheel` is **sound**: `D` is a
generalised wheel iff (i) the digons form a **spanning tree** `T` of `D`,
(ii) the single arcs form **one** directed cycle whose vertex set is **exactly**
the leaves of `T`, in a valid plane circular order, and (iii) every leaf-to-leaf
path of `T` has even length. This is proved in the oracle's docstring (it
exhibits the forward Def-9.1 construction); we take it as given.

### Observation 2.2 (the 3-connected members are exactly the classical wheels) [proved for the listed members; structural reading sketched]

*Verified fact (n ≤ 7).* Among all 2-extremal members of `L_4 … L_7`, the ones
with `U(D)` vertex-connectivity ≥ 3 are **exactly** `W_3, W_4, W_5, W_6`
(`direct_structural_checks.test_S1`), and each has digon forest a **star**
(one hub of digon-degree `k`, `k` leaves of digon-degree 1) with the single arcs
forming one directed `k`-cycle on the leaves — the classical wheel.

*Structural reading [sketched].* If `F_D` is a spanning **star** with hub `h` and
the single arcs are one rim cycle on the `k = n−1` leaves, then `U(D)` is the
graph-theoretic wheel `W_k` (hub adjacent to all, rim a cycle), which is
3-connected for `k ≥ 3`. Conversely a 3-connected `U(D)` cannot have a digon-leaf
whose single arcs all stay "local", because a 3-connected graph has no 2-cut; the
data show the only way to avoid every 2-cut is the full star+rim. A complete
proof of "3-connected ⇒ star+rim wheel" is **not** given here (it is the hard
direction of S1, below).

This pins the **base wall**: the irreducible 2-extremal digraphs that genuinely
resist any 2-cut are the wheels. Everything A-prime must seam is, by S1, *not*
3-connected — so it *has* a 2-vertex separator to exploit.

---

## 3. S1 — every non-base member has a 2-vertex separator

### Claim S1 [conjectural; one direction sketched]

A 2-extremal `D` that is **not** a generalised wheel has `U(D)` of
vertex-connectivity exactly 2; equivalently `U(D)` is **not** 3-connected.

*Status.* Verified n ≤ 7 (`test_S1`: the only 3-connected members are wheels).
**Not proved in general.**

*What is provable [proved].* `U(D)` is 2-connected (hypothesis), so connectivity
is **≥ 2**; S1 asserts it is not **≥ 3**. Equivalently: a 3-connected `U(D)`
forces `D` to be a generalised wheel.

*Attempted proof of the hard direction [sketched, with the gap named].*
Suppose `U(D)` is 3-connected. By L1 every digon-forest leaf is incident to a
single arc. Consider the digon forest `F_D`.

- If `F_D` is **empty** (no digons), then all arcs are single and balanced (P3);
  but then `χ⃗(D)` would have to reach 3 from single-arc trails alone. *Gap: I
  cannot rule this out structurally; data say it never happens for n ≤ 7 (every
  2-extremal member has ≥ 3 digons), but I have no proof that `F_D ≠ ∅`.*
- If `F_D` is a **non-spanning** forest, some vertex `w` has digon-degree 0; its
  ≥ 4 arcs are single. A 3-connected graph has min degree ≥ 3, consistent, so no
  contradiction here directly. *Gap.*
- If `F_D` **spans** but is not a star, it has an internal edge `{x,y}` with both
  `x,y` of digon-degree ≥ 2. Removing the two underlying endpoints of a pendant
  digon subtree should expose a 2-cut, contradicting 3-connectivity — pushing `D`
  toward the star. *This is the most promising sub-argument but I have not closed
  it: a tree that is not a star still need not yield a 2-cut once the single-arc
  rim is overlaid.*

**Honest verdict on S1.** S1 is the cleanest candidate for a *real theorem* on
this angle (it is a statement purely about `U(D)` plus the digon/single split),
but I do **not** have it. It is verified n ≤ 7 and reduces A-prime's "where do I
find a seam" to "read the guaranteed 2-cut." If S1 falls, A-prime falls with it
on this angle; if S1 is proved, the remaining work is the *type* of the cut (§4).

---

## 4. S2 + D1 — the cut exists in one of two flavours, and the flavour is the seam

Granting S1 (a 2-vertex separator exists), the **digon/single split classifies
the separator** into exactly the two seam flavours.

### Claim S2 (the separator is mixed or a non-edge pair) [conjectural; verified 40/40]

Every non-base 2-extremal `D` has at least one of:
- **(i) a mixed 2-cut** `(v, e)`: a vertex `v` and a **single** edge `e={a,b}`
  (`a,b ≠ v`) with `e` a bridge of `U(D) − v`; or
- **(ii) a non-edge 2-vertex cut** `{a,b}`: a pair of **non-adjacent** vertices
  of `U(D)` whose removal disconnects `U(D)`.

*Test.* `test_S2` — PASS, 40/40 non-base members of `L_6 ∪ L_7`. The full
crosstab (from `direct_structural_checks` / the seam census):

| flavour present | hajós-seamed members | tree-join-only members |
|---|---:|---:|
| mixed 2-cut (MC ≥ 1) | 37 | 0 |
| non-edge 2-vertex cut | 14 (also have MC ≥ 1) | 3 |
| **MC = 0 (only non-edge cut)** | 0 | **3** |

So the 3 tree-join-only members (`7.7, 7.14, 7.36`) are **exactly** the non-base
members with `MC = 0`, and they necessarily fall into flavour (ii). Every Hajós
member has flavour (i).

*Why S2 is not automatic from S1.* A 2-vertex separator `{a,b}` of `U(D)` need not
be "mixed": it could be a digon edge, a single edge, a non-edge, or be replaceable
by a (vertex, edge) mixed pair. S2 asserts the separator can always be chosen in
flavours (i)/(ii). I have **no proof**; only the 40/40 census. (Note: a separator
that is a *digon* edge cannot be a 2-cut at all, by **P1** — this is the one place
P1 genuinely prunes the flavour list, leaving {mixed, single-edge-vertex,
non-edge pair}, and the data collapse the middle case into (i).)

### Claim D1 (flavour = seam type) — necessity proved, sufficiency open

**D1-necessity (Hajós ⇒ mixed 2-cut) [proved].** This is the proved direction of
`seam_invariant.md §3.1`, reused verbatim: if `D = D_1 *_v D_2` is a directed
Hajós join, the join arc `(u,w)` is single and `v` separates the `u`-side from
the `w`-side after deleting `{u,w}`, so `(v,{u,w})` is a mixed 2-cut. Hence

```
   D has a directed-Hajós merge vertex   ⇒   MC(D) = 1.
```

Its contrapositive `MC(D)=0 ⇒ no Hajós merge vertex` is therefore a **theorem**:
the three `MC=0` members provably have **no** clause-(a) seam, so A-prime forces
them into clause (b). This is the load-bearing half and it is proved.

**D1-sufficiency, flavour (i): mixed 2-cut ⇒ Hajós seam [conjectural].** That a
mixed 2-cut `(v,{a,b})` actually splits `D` into two strictly-smaller *2-extremal*
Hajós factors `D_1, D_2` is open. Verified 37/37 on the Hajós members.
*Required lemma (call it B-Hajós).* Given a mixed 2-cut `(v,{a,b})` with `a` on
the `u`-side `S_1∋v` and `b` on the `w`-side `S_2∋v`, the digraphs
`D[S_1] + (a→v)` and `D[S_2] + (v→b)` are each 2-extremal. The 2-connectivity and
Eulerian/balanced parts are routine; the **λ=2 and χ⃗=3 preservation** under the
split is the unproved core (the exact analogue of the paper's reduction lemma at
`k=2`, where the colour slack is tight — see `proof_attempt.md §1`).

**D1-sufficiency, flavour (ii): non-edge cut ⇒ tree-join seam [conjectural].**
When `MC=0`, the minimal separators are non-edge pairs `{a,b}`. Structurally
(verified `test_D1`) the three members each decompose as a tree-join whose unique
A-block is the generalised wheel **W3**, attaching across exactly such a non-edge
pair (the two A-edge endpoints). *Required lemma (call it B-tree).* A non-base
2-extremal `D` with `MC=0` has a non-edge 2-vertex cut `{a,b}` such that one side,
together with the interface digon `[a,b]` re-added, is a strictly-smaller
2-extremal block, and the residue is a smaller 2-extremal tree-join. The interface
is **two** vertices (an A-edge), which is exactly why no single-vertex Hajós merge
exists — consistent with D1-necessity. Open; verified 3/3.

---

## 5. The assembled argument and exactly where it does not close

**Theorem-shaped statement (what the angle would give if S1, S2, B-Hajós, B-tree
held).** Let `D` be 2-extremal, not a symmetric odd cycle, not a generalised
wheel. By **S1** `U(D)` has a 2-vertex separator. By **S2** the separator is a
mixed 2-cut (flavour i) or a non-edge pair (flavour ii). In flavour (i), **B-Hajós**
splits `D` at the merge vertex into two strictly-smaller 2-extremal Hajós factors,
giving clause (a). In flavour (ii), **B-tree** exhibits `D` as a non-empty-A
2-Hajós tree-join over the digon forest with a strictly-smaller 2-extremal A-block,
giving clause (b). Either way `D` has a Lemma-A seam. ∎ *(modulo the four gaps)*

**Proved in this document:**
- **[proved]** L1 (leaves carry single arcs) — full proof, from Eulerian +
  min-degree-2 + digon-degree-1.
- **[proved]** P1's pruning of separator flavours: no digon is a 2-cut, so the
  only admissible 2-vertex separators are mixed / single-edge-vertex / non-edge.
- **[proved, reused]** D1-necessity: Hajós merge ⇒ mixed 2-cut, hence
  `MC=0 ⇒ no Hajós seam` (the three `MC=0` members are *provably* clause-(b)).
- **[proved, reused]** Proposition 2.1 (generalised-wheel recognition soundness).

**NOT proved (the four honest gaps), smallest first:**
1. **B-Hajós sufficiency** (flavour i): mixed 2-cut ⇒ the two split sides are
   genuinely 2-extremal (λ=2 and χ⃗=3 preserved). *This is the original Lemma B /
   the `k=2` reduction lemma. The whole programme rests here.*
2. **B-tree sufficiency** (flavour ii): non-edge cut ⇒ a strictly-smaller
   2-extremal A-block + smaller 2-extremal residue.
3. **S2**: the guaranteed 2-cut can always be chosen in flavour (i) or (ii).
   *Reduces, given S1, to ruling out a "pure single-edge–vertex" cut that is
   neither mixed-usable nor a non-edge pair; data say this never occurs.*
4. **S1**: non-base ⇒ `U(D)` not 3-connected (only wheels are 3-connected).
   *The cleanest candidate for an independent theorem; §3 sketches three sub-cases
   and names where each stalls (empty `F_D`, non-spanning `F_D`, non-star spanning
   `F_D`).*

**Where the angle genuinely helps over the dicut route.** It replaces the opaque
"find the reassembly seam" with a **decidable, local search for a 2-vertex
separator** (S1+S2), and it *proves* (via D1-necessity + P1) that the separator's
combinatorial flavour is a **necessary** invariant of the seam type. The residual
math is concentrated into the two **sufficiency** lemmas B-Hajós and B-tree, plus
the connectivity lemma S1 — three crisply-stated targets, each verified n ≤ 7,
none of which is proved. The honest bottom line is unchanged from the other
angles: **A-prime survives to n = 7 with a clean structural skeleton; the
seam-sufficiency core is open.**

---

## 6. Tests and reproduction

```
cd problems/two_extremal_digraphs
python3 scripts/direct_structural_checks.py   # L1, S1, S2, D1 — all PASS, no deps
python3 scripts/seam_invariant.py             # mixed-2-cut rule, 40/40 + consistency
```

- `test_L1` — PASS (L1 proved; this confirms it).
- `test_S1` — PASS (only wheels 3-connected; S1 conjectural).
- `test_S2` — PASS (mixed-cut or non-edge-cut always present; conjectural).
- `test_D1` — PASS (flavour=seam dichotomy; necessity proved, sufficiency
  conjectural); prints the W3 A-block of each `MC=0` member.

All scripts are pure Python and run under the system interpreter with no
networkx; the `.venv` used elsewhere was removed per the hard rule.
