# Proof: the k=3 case of Conjecture 5.10 (Aboulker–Aubian–Charbit–Lopes, arXiv:2310.04265)

**Theorem.** For every **odd integer `n = 2m+1 ≥ 7`** (primality is *not* needed),
the almost-consecutive circulant tournament
$$AC_n=\operatorname{Cay}\!\bigl(\mathbb Z/n,\;\{1,\dots,m-1\}\cup\{m+1\}\bigr),
\qquad i\to j \iff (j-i)\bmod n\in g,$$
is **3-`ω⃗`-critical**. Consequently there are infinitely many 3-`ω⃗`-critical
tournaments (the **k=3 case of Conjecture 5.10**), and **Question 5.9 fails for
k=3** (no bound `ℓ(3)` exists).

Here `ω⃗(T)` is the AACL tournament clique number: the minimum, over vertex
orderings `σ`, of the clique number of the back-edge graph `B_σ(T)` (edge `{i,j}`,
`i<_σ j`, iff the arc is `j→i`). `T` is **k-`ω⃗`-critical** if `ω⃗(T)=k` and
`ω⃗(T−v)=k−1` for every vertex `v`.

## `AC_n` is a tournament (any odd `n`)

For each `k∈{1,…,m}` exactly one of `k, n−k` lies in `g`: for `k≤m−1`, `k∈g` and
`n−k = 2m+1-k ≥ m+2 ∉ g`; for `k=m`, `m∉g` but `n−m = m+1 ∈ g`. So `g` selects one
direction per antipodal pair — `AC_n` is a tournament — and it is vertex-transitive
(rotation `x↦x+1` is an automorphism). *No primality is used here, nor anywhere
below.* [Verified for all odd `7≤n≤101`.]

## Upper bound: `ω⃗(AC_n) ≤ 3`, and the unique back-edge triangle

Use the **identity order** `0<1<\dots<n−1`. Then `{i<j}` is a back-edge iff the arc
is `j→i`, i.e. `(i−j)\bmod n∈g`, i.e. the integer gap
$$j-i \;\in\; D \;=\; \{m\}\cup\{m+2,\dots,2m\}\subseteq[m,2m].$$
Every back-edge gap is `≥ m`.

*Clique bound.* A back-edge clique `a_1<\dots<a_k` has consecutive gaps each `≥m`,
so spread `a_k-a_1 ≥ (k-1)m`; but `a_k-a_1 ≤ n-1 = 2m`, hence `(k-1)m ≤ 2m`, i.e.
`k ≤ 3`. So the identity order witnesses **`ω⃗(AC_n) ≤ 3`**.

*Unique triangle.* A back-edge triangle `a_1<a_2<a_3` has both gaps `≥m` and spread
`≤2m`, forcing both gaps `=m` and spread `=2m`, i.e. `{a_1,a_1+m,a_1+2m}` with
`a_1+2m≤2m`, so `a_1=0`. The **only** back-edge triangle is `{0,m,2m}` (gaps
`m,m,2m∈D`). [Verified for all odd `7≤n≤101`.]

## Lower bound: `ω⃗(AC_n) ≥ 3` via domination and Lemma H8

Let `N₀ = N⁺[0] = \{0\}\cup g = \{0,1,\dots,m-1,m+1\}` (closed out-neighborhood,
`|N₀|=m+1`). By vertex-transitivity `N⁺[v]=N₀+v`, so a pair `{0,v}` dominates `AC_n`
iff `N₀∪(N₀+v)=ℤ/n`, i.e. `|N₀∩(N₀+v)| = 2(m+1)-n = 1`. No singleton dominates
(`|N₀|=m+1<n`). Hence `dom(AC_n) ≥ 3` **iff** `|N₀∩(N₀+v)| ≥ 2` for all `v≠0`:

> **Lemma H8.** For every odd `n=2m+1≥7`, `\min_{t≠0}|N₀∩(N₀+t)| = 2`.

*Proof.* Put `J=\{0,1,\dots,m+1\}` (an interval of `m+2` residues), so `N₀=J\setminus\{m\}`.
As `2|J|=2m+4=n+3>n`, with `K=ℤ/n\setminus J=\{m+2,\dots,2m\}` (`|K|=m-1`),
$$|J∩(J+t)| = n-|K∪(K+t)| = 3+|K∩(K+t)|.$$
For `1≤t≤m`, the length-`(m-1)` interval `K` gives `|K∩(K+t)|=\max(0,m-1-t)`, so
`|J∩(J+t)| = m+2-t` for `t≤m-1` and `=3` for `t=m`. Passing to `N₀=J\setminus\{m\}`
removes element `m` (when `m∈J+t`, i.e. `m-t∈J` — always for `1≤t≤m`) and element
`m+t` (when `m+t∈J`, i.e. only `t=1`):
$$|N₀∩(N₀+t)|=\begin{cases}(m+1)-2=m-1,&t=1\\[2pt](m+2-t)-1=m+1-t,&2≤t≤m-1\\[2pt]3-1=2,&t=m.\end{cases}$$
For `m≥3` (i.e. `n≥7`) all are `≥2`, with minimum `2`. `∎`

*Minimizers (for the record, not used below).* By the `t↔n-t` symmetry of
autocorrelation: for `n=7` (`m=3`) **every** `t≠0` attains the minimum `2`; for every
odd `n≥9` the minimizers are **exactly** `\{m-1,\,m,\,m+1,\,m+2\}`. [Verified for all
odd `n` below 520.]

Therefore `dom(AC_n) ≥ 3`. By **Property 3.2 of arXiv:2310.04265**
(`dom(T) ≤ ω⃗(T) ≤ dic(T)`; source `Refs/2310.04265.tex:486`),
$$\boxed{ω⃗(AC_n) ≥ 3.}$$
With the upper bound, `ω⃗(AC_n) = 3` for every odd `n ≥ 7`.

## Criticality: `ω⃗(AC_n − v) = 2`

By vertex-transitivity it suffices to delete `v=0`.

*`≤2`.* The unique back-edge triangle `{0,m,2m}` uses vertex `0`, so the identity
order restricted to `V\setminus\{0\}` has a triangle-free back-edge graph:
`ω⃗(AC_n−0) ≤ 2`.

*`≥2`.* `AC_n−0` contains the directed triangle `1\to 2\to m+3\to 1`: the gaps are
`2-1=1`, `(m+3)-2=m+1`, and `1-(m+3)\equiv m-1 \pmod n`, all in `g`; the three
vertices `1, 2, m+3` are distinct and nonzero with `m+3 ≤ 2m = n-1` for `m≥3`. A
directed triangle forces `ω⃗ ≥ 2`.

Hence `ω⃗(AC_n−v) = 2` for every `v`, and **`AC_n` is 3-`ω⃗`-critical for every odd
`n ≥ 7`.** [Verified for all odd `7≤n≤101`; exact `(ω⃗(AC_n),ω⃗(AC_n-0))=(3,2)` at
`n=7,9,11`.]

## Conclusion

Distinct odd `n` give tournaments of distinct orders, hence non-isomorphic. So
`\{AC_n : n≥7\text{ odd}\}` is an infinite family of 3-`ω⃗`-critical tournaments,
proving the **k=3 case of Conjecture 5.10**.

For **Question 5.9** (is there `ℓ(k)` such that every tournament with `ω⃗≥k` has a
subtournament `A` with `|A|≤ℓ(k)` and `ω⃗(A)≥k`?): every **proper** subtournament
`A⊊AC_n` omits some vertex `v`, so `A⊆AC_n−v` and by monotonicity
`ω⃗(A) ≤ ω⃗(AC_n−v) = 2`. Thus the *only* subtournament of `AC_n` certifying
`ω⃗≥3` is `AC_n` itself, of order `n`. Since `n` is unbounded, no `ℓ(3)` exists —
**Question 5.9 fails for `k=3`.** `∎`

## Relation to Crew–Fan–Koerts–Moore–Spirkl (arXiv:2602.09863) — no conflict

That paper proves **Conjecture 5.8** of arXiv:2310.04265 (their Corollary 7): there exist
**two functions `f` and `ℓ`** such that every tournament with `ω̄(T) ≥ f(k)` contains a
subtournament `X` with `|X| ≤ ℓ(k)` and `ω̄(X) ≥ k` — with `f` **nontrivial**, not the
identity. That paper does **not settle** the `f`=identity strengthening (**Question 5.9**):
it does not mention Question 5.9, identity thresholds, or `ω̄`-critical tournaments.

Our theorem proves **Conjecture 5.10** for `k=3`, and (independently, via the direct
monotonicity argument above) answers **Question 5.9 in the negative at `k=3`**. Hence `AC_n`
shows `f` **cannot** be the identity for `k=3`. This is **consistent with and complementary
to** Corollary 7: each `AC_n` has `ω̄=3 < f(3)`, so Corollary 7 never applies to it; `AC_n`
is precisely a witness that the threshold `f(3) > 3` in Corollary 7 is necessary.

*A logical caveat (to avoid overstating the link).* Conjecture 5.10 — *for **every** `k≥3`
there are unbounded `k`-`ω̄`-critical tournaments* — **implies** a negative answer to
Question 5.9, but the two are **not** equivalent: `¬Q5.9` only asserts unboundedness for
**some** `k`, so the negation of Conjecture 5.10 does **not** give a positive answer to
Question 5.9. We therefore do not rest the `k=3` result on the paper's "5.10 false ⇒ 5.9 YES"
remark; the `k=3` negation of Question 5.9 is established directly by the monotonicity
argument (lines above: every proper subtournament of `AC_n` has `ω̄≤2`).

## Provenance / dependencies

- **Self-contained & machine-verified** (all odd `7≤n≤101`, H8 to `n<520`):
  `AC_n` is a tournament; the identity-order upper bound and unique-triangle bound;
  Lemma H8; the explicit post-deletion triangle; criticality.
- **One cited input:** Property 3.2 of arXiv:2310.04265 (`dom(T) ≤ ω⃗(T)`), used
  only to pass from `dom≥3` to `ω⃗≥3`. (Confirmed against the bundled source
  `Refs/2310.04265.tex:486`.)
- **Engine contribution:** the `AC_n` construction, the `dom`-reduction, and the
  reduction of the lower bound to H8. **Human contribution:** the proof of H8, the
  identity-order upper-bound/criticality arguments, and (per review) the direct
  `ℓ(3)`-nonexistence argument, the explicit `ω⃗≥2` triangle, the `n=7` minimizer
  correction, and the removal of the primality hypothesis.
