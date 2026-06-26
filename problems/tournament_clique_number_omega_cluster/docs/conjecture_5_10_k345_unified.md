# Infinitely many k-ω̄-critical tournaments for k = 3, 4, 5

**Conjecture 5.10** of Aboulker, Aubian, Charbit and Lopes (*The clique number of
tournaments*, arXiv:2310.04265) asserts that for every `k ≥ 3` there are infinitely many
`k`-ω̄-critical tournaments. This note proves it for **`k = 3, 4, 5`** with a single,
uniform family of circulant-based constructions, and deduces that the associated local–global
**Question 5.9** fails at `k = 3, 4, 5`.

> **Theorem.** For every odd integer `n ≥ 7`, the three tournaments
> `AC_n`, `AC_n[C₃]`, `AC_n[AC_n]` are respectively `3`-, `4`-, `5`-ω̄-critical. Each gives an
> infinite family, so **Conjecture 5.10 holds at `k = 3, 4, 5`**, and **Question 5.9 fails at
> `k = 3, 4, 5`** (no bound `ℓ(k)` exists).

The detailed proofs live in `proof_conj_5_10_k3.md` (k=3), `proof_omega_AC_n_C3.md` +
`proof_deletion_AC_n_C3.md` (k=4), and `proof_AC_n_AC_n_k5.md` (k=5). This document gives the
common framework, the three constructions, the load-bearing lemmas, and the precise barrier to
general `k`.

---

## 1. Preliminaries

**The tournament clique number `ω̄`.** For a tournament `T` and a total order `≺` of `V(T)`,
the *backedge graph* `T^≺` has an edge `{u,v}` (`u≺v`) iff the arc is `v→u` (backward). Then
`ω̄(T) = min_≺ ω(T^≺)`: a *backedge clique* is a set listed by `≺` in reverse-topological
order (every later vertex beats every earlier one). `T` is **k-ω̄-critical** if `ω̄(T)=k` and
`ω̄(T−v)=k−1` for every vertex `v`.

**Question 5.9 vs Conjecture 5.10.** Q5.9 asks for a function `ℓ` with: every `T` with
`ω̄(T)≥k` contains a subtournament `A`, `|A|≤ℓ(k)`, `ω̄(A)≥k`. Conjecture 5.10 (infinitely many
`k`-ω̄-critical tournaments for every `k≥3`) **implies** Q5.9 fails — but the two are not
equivalent (Q5.9 fails as soon as it fails at *one* `k`; 5.10 quantifies over all `k`). For
each `k∈{3,4,5}` our family settles **both** directly: an infinite `k`-critical family, and
(by monotonicity, §6) the non-existence of `ℓ(k)`.

**Two standard tools.**
- *(Sandwich.)* `dom(T) ≤ ω̄(T) ≤ dic(T)` — Property 3.2 of arXiv:2310.04265. We use only the
  left inequality (`dom ≤ ω̄`) to certify lower bounds at `k=3`.
- *(Substitution lower bound.)* For tournaments `S, H`,
  `ω̄(S[H]) ≥ ω̄(S) + ω̄(H) − 1`, where `S[H]` is the lexicographic substitution
  (`(s,h)→(s',h')` iff `s→s'` in `S`, or `s=s'` and `h→h'` in `H`). Proof: order `S[H]`
  arbitrarily; the block reps form a backedge `ω̄(S)`-clique in `S`, and *fattening its source
  block* by a backedge `ω̄(H)`-clique of `H` yields a backedge clique of size `ω̄(S)+ω̄(H)−1`
  (full argument in `proof_omega_AC_n_C3.md` §lower bound). Substitution also preserves
  vertex-transitivity, so for our families a single vertex deletion suffices.

**The base circulant.** Fix `n = 2m+1`, `m ≥ 3`, and
`g = {1,…,m−1} ∪ {m+1} ⊆ ℤ/n`. The **almost-consecutive circulant**
`AC_n = Cay(ℤ/n, g)` has arc `i→j ⟺ (j−i) mod n ∈ g`. It is a vertex-transitive tournament
(`g ⊔ (−g) = ℤ/n∖{0}`), with the **four arc-facts** used throughout (band
`H:=[m+1,2m]`, band `L:=[1,m]`):

| | `a∈g` | `(−a)∈g` |
|---|---|---|
| `a∈H` | `a=m+1` | `a∈[m+2,2m]` |
| `a∈L` | `a∈[1,m−1]` | `a=m` |

and the **gap fact**: within a length-`m` interval, a difference is in `g` only when it is
`≤m−1` (never the wrap value `m+1`). The asymmetry between the two bands (the `(−a)` column:
an *interval* in `H`, a single *point* in `L`) is genuine and is handled explicitly at each `k`.

---

## 2. k = 3 : `AC_n` is `3`-ω̄-critical

**Upper bound `ω̄(AC_n) ≤ 3`.** In the identity order, a backedge gap lies in
`D = {m}∪{m+2,…,2m} ⊆ [m,2m]`, so every gap is `≥m`. A backedge clique `a_1<⋯<a_k` has spread
`≥(k−1)m` and `≤2m`, forcing `k≤3`; the unique back­edge triangle is `{0,m,2m}`.

**Lower bound `ω̄(AC_n) ≥ 3`** via `dom(AC_n)≥3` and the sandwich. With `N₀=\{0\}∪g`
(the closed out-neighbourhood, an interval `{0,…,m+1}` minus the point `m`), `dom≤2` iff some
translate makes `N₀∪(N₀+t)=ℤ/n`, i.e. `|N₀∩(N₀+t)|=1` for some `t≠0`. This never happens:

> **Lemma H8 (autocorrelation).** For every odd `n=2m+1≥7`, `min_{t≠0}|N₀∩(N₀+t)| = 2`.

*Proof idea.* `N₀=J∖{m}` for the interval `J={0,…,m+1}`; using `|J∩(J+t)| = 3+|K∩(K+t)|`
for the complementary interval `K`, and tracking the two removed points, one gets the closed
form `|N₀∩(N₀+t)| = m−1, m+1−t, 2` for `t=1`, `2≤t≤m−1`, `t=m` — all `≥2` for `m≥3`. (Full
proof: `proof_conj_5_10_k3.md` §H8.)

So `dom(AC_n)≥3`, hence `ω̄(AC_n)=3`.

**Criticality.** Deleting any vertex (say `0`) removes the unique backedge triangle, so the
identity order is triangle-free on the rest: `ω̄(AC_n−0)≤2`; and `AC_n−0` still contains the
directed triangle `1→2→(m+3)→1` (gaps `1,m+1,m−1∈g`), so `ω̄(AC_n−0)=2`. By
vertex-transitivity `AC_n` is `3`-ω̄-critical. ∎

---

## 3. k = 4 : `AC_n[C₃]` is `4`-ω̄-critical

Write `C₃ = 0→1→2→0` (`ω̄(C₃)=2`). By the substitution lower bound, `ω̄(AC_n[C₃])≥4`.

**Value `ω̄(AC_n[C₃]) = 4`.** Use the *merged order* keyed by `c(t)+d(h)` where `c` is the
`AC_n` identity-order potential (`c(0)=3`, `c=2` on `[1,m]`, `c=1` on `[m+1,2m]`) and
`d(0)=2, d(1)=d(2)=1`. A no-5-clique casework on the key classes (within-class caps `(1,2,2,1)`
plus cross-class arc-facts) gives `≤4`. (Full proof: `proof_omega_AC_n_C3.md`.)

**Deletion `ω̄(AC_n[C₃]−v) = 3`.** Delete `(0,0)` and use the `d_then_c` order (sort survivors
by `(d(h),c(t),t,h)` — the inner `C₃` coordinate first), giving five bands. With
`a₁=|{h∈\{1,2\}}|`, `a₂=|{h=0}|`: `a₂=0⇒a₁≤3`; `a₂=1⇒a₁≤2` (no `(3,1)`); `a₂=2⇒a₁≤1`
(no `(2,2)`). The crux is the **(2,2)-incompatibility**

> `¬(1+δ∈g ∧ (m+1+δ)∈g)` for `δ∈g`

(`1+δ∈g ⟺ δ∈[1,m−2]`, `(m+1+δ)∈g ⟺ δ=m+1`; no common `δ`), which makes the common dominees of
two `h=0` vertices backedge-independent. So `a₁+a₂≤3`. (Full proof, with all arc-facts proven
uniformly in `m`: `proof_deletion_AC_n_C3.md`.) Vertex-transitivity ⇒ `4`-ω̄-critical. ∎

---

## 4. k = 5 : `AC_n[AC_n]` is `5`-ω̄-critical

By the substitution lower bound, `ω̄(AC_n[AC_n])≥5`. Vertices are `(a,b)`, `a,b∈ℤ/n`.

**The cell method.** Order the survivors of `T−(0,0)` by `inner_then_outer`:
`key(a,b)=(c(b),c(a),a,b)`. The **cell** of a vertex is `χ(a,b)=(c(b),c(a))∈\{1,2,3\}²`;
`(0,0)` is the only cell-`(3,3)` vertex, so survivors fill the **8 cells** `{1,2,3}²∖{(3,3)}`.

- *One vertex per cell.* Within a cell both coordinates lie in monotone `m`-intervals, where
  gaps land in `[m+2,2m]`, disjoint from `g` — so there is **no backedge inside a cell**. A
  backedge clique therefore injects into the 8 cells.
- *No 5 cells realizable.* The obstruction is a fixed, `n`-independent list of **20 listed
  infeasible cell-sets** (10 triples, 10 quads), and every 5-subset of the 8 cells contains
  one. Each closes by one of two mechanisms: **outer-source forced-value chains** (using the
  band arc-facts of §1 in *both* bands), or the **`(2,2)`-square split** whose hard branch is

  > **Lemma H17 (in-neighbourhood).** For `x∈H`, `y∈L`, the set `N⁻(x)∩N⁻(y)=(x−g)∩(y−g)`
  > lies in a single band (`⊆[0,m−1]` if `x−y≤m`, else `⊆[m+1,2m−1]`).

  *Proof.* `N⁻(v)=v−g=[v−m−1,v−1]∖{v−m}`; for `x∈H` it is a non-wrapping arc, for `y∈L` it
  wraps. Their intersection is `[x−m−1,y−1]⊆[0,m−1]` when `x−y≤m`, and `[y+m,x−1]⊆[m+1,2m−1]`
  otherwise — single band either way. ∎

So `ω̄(AC_n[AC_n]−(0,0)) ≤ 4`; with the induced `(AC_n−0)[AC_n]` giving `≥4`, the deletion is
`4`, and the value `ω̄=5` follows as a corollary (`(0,0)` is the unique `≺`-top vertex). By
vertex-transitivity `AC_n[AC_n]` is `5`-ω̄-critical. (Full proof — all 20 listed infeasible
cell-sets derived symbolically (10 triple + 4 quad chains, all `n`-independent; 6 squares by the
alternating-`H,L` split + H17) — in `proof_AC_n_AC_n_k5.md`. Two reviews repaired: a band-`L`
arc-fact, and the originally-asserted quad chains + an inaccurate square description, now written
out and verified.) ∎

---

## 5. Common threads

The three proofs share one architecture, sharpened level by level:

| | upper bound | lower bound | criticality crux |
|---|---|---|---|
| `k=3` `AC_n` | interval/gap spread (`≥m`, `≤2m`) | `dom≥3` via **H8** autocorrelation | unique triangle uses the deleted vertex |
| `k=4` `AC_n[C₃]` | merged-key no-5-clique casework | substitution `3+2−1` | **(2,2)-incompatibility** `¬(1+δ∈g∧m+1+δ∈g)` |
| `k=5` `AC_n[AC_n]` | **cell method** (1/cell ⇒ 8 cells) | substitution `3+3−1` | **H17** in-neighbourhood single-band |

The recurring engine is the **`m`-vs-`m+1` band asymmetry** of `g`: it powers every arc-fact,
and (lesson learned the hard way) it is the source of the few false steps that adversarial
checking caught. H8 (k=3) and H17 (k=5) are the two interval-autocorrelation lemmas; the
(2,2)-incompatibility (k=4) is their additive sibling.

---

## 6. Question 5.9 fails at k = 3, 4, 5

For `T∈\{AC_n, AC_n[C₃], AC_n[AC_n]\}`, every *proper* subtournament `A⊊T` omits a vertex `v`,
so `A⊆T−v` and `ω̄(A)≤ω̄(T−v)=k−1` by monotonicity. Thus the only subtournament of `T`
certifying `ω̄≥k` is `T` itself, of order `n`, `3n`, `n²` respectively — unbounded as `n→∞`.
So no `ℓ(k)` exists: **Question 5.9 fails at `k=3,4,5`.** ∎

---

## 7. The barrier to general `k`

The most tempting route to `k≥6` was to iterate substitution (e.g. `AC_n[AC_n[…]]`) using
the proposed **substitution upper bound**

> `ω̄(S[H]) ≤ ω̄(S)+ω̄(H)−1` for all tournaments `S, H` (the matching upper bound to §1).

This bound is **false**. There is an order-7 tournament `H` with `ω̄(H)=2` for which
`ω̄(C₃[H])=4`, although the formula predicts `2+2−1=3`; in the reverse direction
`ω̄(H[C₃])=3`. Two distinct no-`K4` SAT formulations verify the lower bound, the identity
order certifies the upper bound, and exhaustive isomorphism-class enumeration finds no such
`C₃[H]` counterexample for `|H|≤6` and exactly three at order `7`. The earlier block-laminarity
reduction failed because it bounded arbitrary induced block and within-block orders by `ω̄`,
which is a **minimum over orders**. The valid general upper bound is only the block-product bound
`ω̄(S[H])≤ω̄(S)ω̄(H)`, attained by this counterexample.

Thus the general nesting route is closed. The special `AC_n[C₃]` and `AC_n[AC_n]` identities
proved above survive because they use the arithmetic structure of `AC_n`, not a universal
composition law. A direct per-`k` circulant family (the Paley(19)-at-`k=4` analogue) remains
another route, but the cheap certificates that produced witnesses at `k≤5` did not reach `k=6`
**on the scope tested** (NOT a universal statement): **42 sampled** single-orbit circulants — up to
~6 random identity-order-clique-6 generators for each of `n∈{37,39,…,49}` — all gave `ω̄≤5` under the
no-`K₆` SAT oracle; and on the domination side, an **exhaustive** order-37 census (all `2¹⁸`
circulants: `max dom=4`) plus samples at higher orders and a Paley-only scan gave `dom≤5` for all
Paley `p≤251` — so no *free* `dom≥6` lower bound was found below order `67`. These are sampled/partial
scopes, not proofs that no `k=6` single-orbit circulant exists.

So `k=3,4,5` are settled; `k≥6` still requires a genuinely new construction or a special
criticality-lifting theorem.

---

## 8. Verification

Every construction, value, deletion, and arc-fact is reproducible with the exact `ω̄` oracle
(`scripts/core.py`: brute force / branch-and-bound; `scripts/…sat…`: the validated no-K-clique
SAT betweenness oracle) and the substitution builder (`scripts/ground_lex_compose_c3.py`). The
families are checked to `n=151` (k=4 deletion), `n=41` (k=5 cell tradeoff), and the lemmas H8
(`n<520`), H17 (`n≤39`), the (2,2)-incompatibility (`m≤3000`) hold uniformly. The k=4 and k=5
proofs each passed an independent multi-skeptic adversarial red-team (k=4: all-holds; k=5:
0 broken, one arc-fact gap found and repaired).
