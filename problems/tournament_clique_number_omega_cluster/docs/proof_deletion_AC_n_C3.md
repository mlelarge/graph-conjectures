# ω̄(AC_n[C₃] − v) = 3 for every odd n ≥ 7  (deletion bound ⇒ Conjecture 5.10 at k=4)

With `ω̄(AC_n[C₃]) = 4` (proof_omega_AC_n_C3.md), this proves **`AC_n[C₃]` is 4-ω̄-critical
for every odd `n≥7`**, hence there are infinitely many 4-ω̄-critical tournaments
(**Conjecture 5.10 at k=4**), and **Question 5.9 fails at k=4**.

`n=2m+1`, `g={1,…,m−1}∪{m+1}`; arc `i→j ⟺ (j−i) mod n ∈ g`. `AC_n[C₃]` = substitution.
By vertex-transitivity of `AC_n[C₃]` it suffices to bound `ω̄` after deleting **`v=(0,0)`**.

**Lower bound `≥3`:** a constant-`h` copy (`h≠0`) is a full `AC_n`, `ω̄=3`. So `≥3`.

## Upper bound `≤ 3`: the `d_then_c` order

Order the `3n−1` survivors ascending by `(d(h), c(t), t, h)`, where `d(0)=2, d(1)=d(2)=1`
and `c(0)=3, c(t)=2 (1≤t≤m), c(t)=1 (m+1≤t≤2m)`. This is five **bands** by `(d,c)`:
`B1=(1,1), B2=(1,2), B3=(1,3)` (the `h∈{1,2}` vertices) and `B4=(2,1), B5=(2,2)` (the `h=0`
vertices). Higher band ⇒ dominates lower (that is what a cross-band backedge means).

For a backedge clique `S`, let `a₁=|S∩{h∈{1,2}}|`, `a₂=|S∩{h=0}|`. We show `a₁+a₂≤3`.

**(0) No within-band backedge** ⇒ ≤1 vertex per band ⇒ `a₁≤3`, `a₂≤2`.
Within a band, two vertices are either same block (`C₃` arc `1→2`, forward) or different
blocks of equal `c` (gap in `[1,m−1]⊆g`, forward). [Verified `m≤14`.]

**(1) `a₂≥1 ⇒ a₁≤2`** (no `(3,1)` clique). An `a₁=3` clique uses `B1,B2,B3`: a `B3` vertex
`(0,·)`, a `B2` vertex `(t₂,·)`, a `B1` vertex `(t₁,·)`. The backedges `B3→B1` (`0→t₁ ⟺ t₁=m+1`),
`B3→B2` (`0→t₂ ⟺ t₂≤m−1`) and `B2→B1` (`t₂→m+1 ⟺ t₂∈[2,m−1]`) force blocks
`{0, t₂∈[2,m−1], m+1}`. We show no `h=0` vertex `(s,0)`, `s∈[1,2m]`, dominates all three.
Such a vertex dominates a `d=1` vertex at block `β`: if `β≠s` it needs `(β−s)∈g`; if `β=s` the
only internal arc is `(s,0)→(s,1)`. Domination of **block 0** needs `(0−s)≡n−s∈g`, i.e.
`s∈{m}∪[m+2,2m]` (`n−s=m+1 ⟺ s=m`; `n−s∈[1,m−1] ⟺ s∈[m+2,2m]`). Split on `s`:
- `s∈[1,m−1]∪{m+1}`: then `n−s∈[m+2,2m]∪{m}`, none in `g`, so `(s,0)↛` block 0.
  (In particular `s=m+1` fails here, since `n−(m+1)=m∉g`.)
- `s=m`: `(m,0)↛(t₂,·)`, as `(t₂−m) mod n = m+1+t₂ ∈ [m+3,2m] ∉ g`.
- `s∈[m+2,2m]`: `(s,0)↛(m+1,·)`, as `(m+1−s) mod n = 3m+2−s ∈ [m+2,2m] ∉ g`.

This covers all `s∈[1,2m]`, so no `(s,0)` extends an `a₁=3` clique. ∎

**(2) `a₂=2 ⇒ a₁≤1`** (no `(2,2)` clique). Let `S₂={(s,0),(s',0)}`, `s∈[m+1,2m]` (B4),
`s'∈[1,m]` (B5), backedge `(s',0)→(s,0)` so `s'→s`, i.e. `δ:=s−s'∈g`. `S₁` lies in
`X := {d=1 vertices dominated by both (s,0),(s',0)}`; we show `X` is **backedge-independent**,
so `a₁=|S₁|≤1`.

A generic `(t,h)∈X` (`t∉{s,s'}`) needs `(t−s)∈g` and `(t−s')∈g`; writing `b=t−s`, this is
`b∈g` and `b+δ∈g`. (The special `t=s'` is impossible: `s↛s'` since `(s'−s)≡n−δ∉g`; the
special `t=s` gives only `(s,1)`, a `B1` vertex.) So the blocks of `X` are
`{s+b mod n : b∈g, (b+δ) mod n ∈ g}`, splitting into:
- **high** `t=s+b ≤ 2m` (`c=1`, band `B1`), together with `t=s`; and
- **wrapped** `t=s+b−n ∈ [0,m]` (`c=2`, band `B2`; or `B3` if `t=0`).

*Within `B1`*: blocks in `[s,2m]`, pairwise gap `≤m−1∈g` ⇒ forward. *Within `B2`*: blocks in
`[1,m]`, same ⇒ forward. *Cross `B1`–`B2`* (the only danger): for `t₁=s+b₁` (B1) and
`t₂=s+b₂−n` (B2), `(t₁−t₂) mod n = (b₁−b₂) mod n`, with `b₁∈{0}∪g` (`0` = the special `t=s`),
`b₂∈g`. A `B2→B1` backedge needs `(t₁−t₂)∈g`; since `b₁−b₂∈[−(m+1),−1]`, its residue lies in
`[m,2m]`, and `[m,2m]∩g={m+1}`, forcing `b₁−b₂≡−m`, i.e. `b₂=b₁+m`. With `b₁∈{0}∪g`,
`b₂∈g`: `b₁=0⇒b₂=m∉g`; `b₁∈g⇒b₂=b₁+m∈g ⟺ b₁=1, b₂=m+1`. But then membership in `X`
requires `1+δ∈g` **and** `m+1+δ∈g` — and these never both hold: `1+δ∈g ⟺ δ∈[1,m−2]`,
whereas `(m+1+δ) mod n∈g ⟺ δ=m+1`. **Contradiction.** So no cross-`B1`–`B2` backedge.

*The `B3` block.* The split above used `t≠0`; the remaining possibility is a wrapped block
`t=0`, i.e. a `B3` vertex `(0,·)∈X`. Block `0∈X` needs `b=n−s∈g` **and** `b+δ≡n−s'∈g`; the
second forces `s'=m` (the only `s'∈[1,m]` with `n−s'=m+1∈g`). Then (i) **no `B2` block is in
`X`**: a wrapped block `t∈[1,m−1]` needs `(t−s')≡t−m≡t+m+1∈[m+2,2m]∉g`, and for `t=m` note
`δ=s−m∈g` with `δ≤m` forces `δ≤m−1`, hence `s≤2m−1`, so `(m−s)≡3m+1−s∈[m+2,2m]∉g`
(equivalently `t=m=s'` is the special `t=s'` block already excluded above); (ii) **the `B3`
vertex backedges to a `B1` block only at `t=m+1`**
(`0→t ⟺ t∈g`, and `t∈[m+1,2m]⟹t=m+1`), but `m+1∉X`: `s=m+1` would give `n−s=m∉g` (so no `B3`
block exists at all), and for `s∈[m+2,2m]`, `(m+1−s)≡3m+2−s∈[m+2,2m]∉g`, so `s↛m+1`. Hence the
`B3` vertex has no backedge to any other member of `X`. So `X` is backedge-independent in every
case, giving `a₁≤1`. ∎

**Conclusion.** `a₂=0⇒a₁≤3`; `a₂=1⇒a₁≤2`; `a₂=2⇒a₁≤1`. So `a₁+a₂≤3`:
`ω̄(AC_n[C₃]−v) ≤ 3`, hence `=3`. Therefore `AC_n[C₃]` is **4-ω̄-critical** for all odd `n≥7`. ∎

## Verification

Construction `ω̄(AC_n[C₃]−v)=3`: engine, to `n=151`; SAT `=3` to `n=15`. Every arc-fact in
the casework is `n`-independent and was machine-checked uniformly in `m`: the band bounds and
`a₂`-split `(3,2,1)`; the `(3,1)`-exclusion (complete `s`-split, no `(s,0)` dominates all three
blocks, `m=3..200`); the `(2,2)` lemma `X` backedge-independent, including the `B3` sub-case
(`m=3..200`) and the core incompatibility `¬(1+δ∈g ∧ m+1+δ∈g)` (to `m=199`). **Status:
complete and red-team passed (2026-06-06); the two finite-`m` delegations flagged in review
(the `B3` sub-case and the `s=m+1` line of the `(3,1)` exclusion) are now proven uniformly.**

## Relation to arXiv:2602.09863 (same as k=3)

`AC_n[C₃]` has `ω̄=4`, so each is a witness that the threshold `f(4)>4` is necessary in
Corollary 7 (the `f`-nontrivial cluster theorem). No conflict; complementary.
