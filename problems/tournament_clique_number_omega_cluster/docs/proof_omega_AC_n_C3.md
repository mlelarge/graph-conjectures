# ω̄(AC_n[C₃]) = 4 for every odd n ≥ 7  (the H12 upper bound, for this family)

`AC_n = Cay(ℤ/n, g)`, `n=2m+1`, `g={1,…,m−1}∪{m+1}`; `C₃ = 0→1→2→0`.
`AC_n[C₃]` = lexicographic substitution (each vertex of `AC_n` → a copy of `C₃`):
arc `(t,h)→(t',h')` iff `t→t'` in `AC_n` (when `t≠t'`) or `h→h'` in `C₃` (when `t=t'`).
`ω̄(D) = min over orders ≺ of ω(backedge graph)`; a backedge clique = a set listed by `≺`
in reverse-topological order (every pair a backward arc).

This proves the substitution law `ω̄(AC_n[C₃]) = ω̄(AC_n)+ω̄(C₃)−1 = 3+2−1 = 4`.
(`ω̄(AC_n)=3` is the k=3 theorem; `ω̄(C₃)=2`.) Machine-checked: max clique `=4` and all
within-class bounds for `m=3..14`; all arc-facts are `n`-independent; engine SAT-confirmed
`=4` to order 39.

## The merged order ≺*

`c(t) =` 3 if `t=0`; 2 if `1≤t≤m`; 1 if `m+1≤t≤2m`  (= largest `AC_n` backedge-clique with
min `t`, in `AC_n`'s identity order; the unique 3-clique is `{0,m,2m}`).
`d(0)=2, d(1)=d(2)=1`.  `key(t,h)=c(t)+d(h) ∈ {2,3,4,5}`.
`≺*`: sort ascending by `(key, t, h)`. A backedge clique has keys non-decreasing, and a
**higher-key element dominates (→) every lower-key element** of the clique.

## Upper bound: `ω̄(AC_n[C₃]) ≤ 4`

Let `S` be a backedge clique, `s_K = |S∩{key=K}|`.

**Within-class cliques** (`s_K ≤ max clique inside class K`):
- `K=5`: only `(0,0)`, so `s₅≤1`.
- `K=2` = `{(t,1),(t,2): m+1≤t≤2m}`: all internal pairs are forward arcs, so `s₂≤1`.
- `K=4` = `{(0,1),(0,2)}∪{(t,0):1≤t≤m}`: internal backedges are only `{(m,0),(0,1)}` and
  `{(m,0),(0,2)}` (the `(t,0)` form a forward chain; `0→t` for `t≤m−1`; `(0,1)→(0,2)`).
  So `s₄≤2`, and a size-2 clique here contains `(m,0)`.
- `K=3` = `{(t,1),(t,2):1≤t≤m}∪{(t,0):m+1≤t≤2m}`: internal backedges occur only between a
  "low" `(a,h)` (`a≤m`) and a "high" `(b,0)` (`b≥m+1`), when `b−a∈D`. This is bipartite
  (no low–low or high–high backedge), so `s₃≤2` and a size-2 clique is one low + one high.

**Cross-class casework** (rules out `|S|≥5`):

*Case `s₄=2`.* Then `S⊇{(m,0),(0,1)}` (wlog). `(0,0)` does **not** dominate `(m,0)` (`0↛m`,
as `m∉g`), so `s₅=0`. A low `K3` vertex `(a,h)`: `(m,0)` dominates a low vertex only for
`(m,1)`, but then `(0,1)` fails to dominate `(m,1)` (`0↛m`) — impossible; so any `K3` vertex
is high `(b,0)`, and `(0,1)→(b,0)` forces `b=m+1`, with at most one high in a clique, so
`s₃≤1`. Hence `|S| ≤ 0+2+1+1 = 4`.

*Case `s₄≤1`.* The only profile summing to 5 under the caps `(1,1,2,1)` is `(s₅,s₄,s₃,s₂)=
(1,1,2,1)`. Then `(0,0)∈S` dominates everything, forcing the high `K3` vertex to be
`(m+1,0)` (`0→b` ⟺ `b=m+1`), the low `K3` vertex to be `(1,h)` (the `K3` low–high backedge `(b,0)→(a,h)` is the arc `b→a`, i.e. `(a−b)≡n−(b−a)∈g`; with `b=m+1` this needs `b−a=m`, so `a=1`), and the
`K2` vertex to be `(m+1,1)` (`0→e` ⟹ `e=m+1`; same-block backedge with `(m+1,0)` ⟹ `f=1`).
But then `(1,h)` (key 3) and `(m+1,1)` (key 2) are joined by `(m+1)→1` (since
`1−(m+1) ≡ m+1 ∈ g`) — a **forward** arc, not a backedge. Contradiction. Hence `|S| ≤ 4`.

So every backedge clique has `≤4` vertices: `ω̄(AC_n[C₃]) ≤ 4`. ∎

## Lower bound: `ω̄(AC_n[C₃]) ≥ 4` (general lex argument, `a=ω̄(T), b=ω̄(H)` ⇒ `≥ a+b−1`)

For any order `≺` of `T[H]`: each block (a copy of `H`) has a backedge `b`-clique. Let
`rep(t)` be the `≺`-minimum of block `t`; `{rep(t)}` ordered by `≺` is an order of `T`, with a
backedge `a`-clique `{rep(t_1),…,rep(t_a)}`. Let `t_1` be its `≺`-maximum — the *source*
(`t_1→t_j`, `rep(t_j)≺rep(t_1)`, all `j`). Replace `rep(t_1)` by the full backedge `b`-clique
`R_{t_1}` of block `t_1`. For `x∈R_{t_1}`: `x ⪰ rep(t_1) ≻ rep(t_j)` and `t_1→t_j`, so
`x→rep(t_j)` is a backedge. Thus `R_{t_1}∪{rep(t_2),…,rep(t_a)}` is a backedge clique of size
`a+b−1`. With `a=3, b=2`: `ω̄(AC_n[C₃]) ≥ 4`. ∎

## Status toward Conjecture 5.10 at k=4

This proves the **value** `ω̄(AC_n[C₃]) = 4` for all odd `n≥7` — an infinite family of
tournaments with `ω̄ = 4`. The remaining ingredient for Conj 5.10 (k=4) — the uniform deletion
bound `ω̄(AC_n[C₃] − v) ≤ 3` (⇒ 4-criticality) — is **now proven** in the companion document
`proof_deletion_AC_n_C3.md` (the `d_then_c` order: band casework + the `(2,2)`-lemma; by
vertex-transitivity one `v` suffices). Note the merged order `≺*` used above has 4-cliques
avoiding any single vertex, which is why the deletion needs that *separate* order/argument
rather than `≺*`; and `ω̄=4` alone would not give Conj 5.10 (infinitely many `ω̄=4` tournaments
need not contain infinitely many *critical* ones), so the deletion lemma was the genuine step.

**Conclusion (both documents together):** `AC_n[C₃]` is **4-ω̄-critical** for every odd `n≥7`,
hence there are infinitely many 4-ω̄-critical tournaments — **Conjecture 5.10 holds at `k=4`**,
and **Question 5.9 fails at `k=4`**.
