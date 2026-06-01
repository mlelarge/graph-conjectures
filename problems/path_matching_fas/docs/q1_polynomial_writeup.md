# Recognizing tournament degreewidth at most two in polynomial time

> **⚠ PRIOR WORK — NOT NOVEL (added 2026-06-01).** The result below
> (recognizing `Δ*(T) ≤ 2` for tournaments in polynomial time, and
> `k`-degreewidth in `n^{O(k)}`) is **subsumed**, and strictly improved, by
> **Keeney & Lokshtanov, "Degreewidth on Semi-Complete Digraphs" (WG 2024)**
> (`Ref/DegreewidthPaper_240419_165002.pdf`). Their **Theorem 2** decides
> `Δ*(T) ≤ k` and computes an optimal degreewidth ordering in
> `k^{O(k)} n + O(n²)` — i.e. degreewidth is **FPT** (stronger than our XP),
> and `Δ*≤2` is `O(n²)` (vs our `~O(n⁹)`). Their "restricted ordering graph"
> with windows `[i−cΔ, i+cΔ]` IS the score-window / reachable-prefix DP used
> here; their Lemma 3 / Corollary 1 is our two-sided window + forced/flexible
> split. So this chapter re-derives a known, stronger result. (Earlier project
> notes wrongly said this paper "does not settle tournament k=2" — it does.)
> **What remains open and is NOT in their paper: Path-FAS / linear-forest
> ordering (Aboulker Problem 4.4). Their FAS is standard minimum-FAS, not the
> linear-forest-shaped Path-FAS. The acyclicity core (Q2) is untouched.**



This note supersedes the quasi-polynomial writeup
`docs/q1_quasipoly_writeup.md`.  The recursive `O(log n)` diameter proof is
not needed: the outside-in-neighbour closure lemma gives an absolute exchange
bound directly.

## 1. Reachable prefixes

Let `T = (V,A)` be a tournament.  For `v ∈ V`, write

```text
N^-(v) = {u : uv ∈ A},        d^-(v) = |N^-(v)|.
```

For a linear order, a backward arc is an arc whose head is earlier than its
tail.  The degreewidth `Δ*(T)` is the minimum, over all linear orders of `V`,
of the maximum number of backward arcs incident with a vertex.

A set `S ⊆ V` is a **reachable prefix** if the vertices of `S` can be ordered
as the first `|S|` positions so that every vertex of `S` has back-degree at
most `2`, with every vertex of `V \ S` placed after the prefix.

For `u ∉ S`, its back-degree if appended after `S` is

```text
bd(u | S) = |N^+(u) ∩ S| + |N^-(u) \ (S ∪ {u})|
          = 2|N^+(u) ∩ S| + d^-(u) - |S|.
```

Thus the exact recognizer is:

```text
∅ is reachable;
from reachable S, add u ∉ S iff bd(u | S) ≤ 2.
```

The full set `V` is reachable if and only if `Δ*(T) ≤ 2`.

## 2. The closure lemma

The following elementary consequence of reachability is the entire reason the
state space is polynomial.

**Lemma 2.1 (outside in-neighbour closure).**  If `S` is a reachable prefix
and `v ∈ S`, then

```text
|N^-(v) \ S| ≤ 2.
```

**Proof.**  In a witnessing prefix order, every vertex outside `S` is after
every vertex of `S`.  Therefore each in-neighbour of `v` outside `S`
contributes a backward arc incident with `v`.  Since the witnessing order has
back-degree at most `2` at every vertex of `S`, there are at most two such
outside in-neighbours. ∎

## 3. Constant diameter

For a tournament `T`, let `R_p(T)` be the family of reachable prefixes of
size `p`.  Define the same-size reachable-prefix diameter

```text
D(p) = max |S △ S'|,
```

where the maximum is over all tournaments `T` and all
`S,S' ∈ R_p(T)`.

**Theorem 3.1 (absolute exchange bound).**  For every `p`,

```text
D(p) ≤ 8.
```

**Proof.**  Let `S,S' ∈ R_p(T)`.  Put

```text
A = S \ S',        B = S' \ S.
```

Since `|S| = |S'|`, we have `|A| = |B| = m`, and

```text
|S △ S'| = 2m.
```

Consider the complete bipartite tournament between `A` and `B`.  For each
`a ∈ A`, all vertices of `B` lie outside `S`.  By Lemma 2.1 applied to the
prefix `S`, at most two vertices of `B` can point into `a`.  Hence the number
of arcs directed from `B` to `A` is at most `2m`.

Similarly, for each `b ∈ B`, all vertices of `A` lie outside `S'`.  By Lemma
2.1 applied to the prefix `S'`, at most two vertices of `A` can point into
`b`.  Hence the number of arcs directed from `A` to `B` is at most `2m`.

Every pair `(a,b) ∈ A × B` has exactly one arc between it, so

```text
m^2 = e(A,B) + e(B,A) ≤ 2m + 2m = 4m.
```

If `m = 0` there is nothing to prove.  Otherwise `m ≤ 4`, and therefore

```text
|S △ S'| = 2m ≤ 8.
```

This bound is uniform in `p`, `n`, and `T`. ∎

This is the non-recursive exchange argument the quasi-polynomial writeup was
missing.  It uses no degree-window decomposition, no budget localization, and
no induction.

## 4. Counting reachable prefixes

**Lemma 4.1 (diameter-to-count).**  If `R_p(T)` is nonempty and has diameter
at most `8`, then

```text
|R_p(T)| ≤ Σ_{j=0}^{4} C(p,j) C(n-p,j) = O(n^8).
```

**Proof.**  Fix one reachable prefix `S_0 ∈ R_p(T)`.  Any other
`S ∈ R_p(T)` satisfies `|S △ S_0| ≤ 8`.  Since `|S|=|S_0|`, the set `S` is
obtained from `S_0` by removing `j ≤ 4` vertices and inserting `j ≤ 4`
vertices.  There are at most `C(p,j)C(n-p,j)` choices for each `j`. ∎

**Theorem 4.2 (polynomial recognizer).**  Tournament degreewidth at most two
is decidable in polynomial time.

**Proof.**  For every size `p`, Lemma 4.1 gives `O(n^8)` reachable prefixes.
There are `n+1` possible prefix sizes, so the total number of reachable
prefixes is `O(n^9)`.  The exact reachable-prefix recognizer tries at most
`n` extensions from each reachable prefix.  Therefore the straightforward
implementation runs in polynomial time, for example `O(n^{10})` extension
checks before bit-operation costs.  By exactness of the reachable-prefix
recurrence, it accepts exactly the tournaments with `Δ*(T) ≤ 2`. ∎

The empirical diameter bound `≤8` was not an accident; it is exactly the
constant forced by applying outside-in-neighbour closure to the two halves of
the symmetric difference.

## 5. General fixed-`k` form

The same proof works verbatim for every fixed `k`.  If `S` is a reachable
prefix for the threshold `Δ*(T) ≤ k`, then every `v ∈ S` has at most `k`
in-neighbours outside `S`.  For two same-size reachable prefixes, the same
bipartite count gives

```text
|S \ S'|^2 ≤ 2k |S \ S'|,
```

so

```text
|S △ S'| ≤ 4k.
```

Consequently, for fixed `k`, the reachable-prefix recognizer has at most

```text
Σ_{j=0}^{2k} C(p,j) C(n-p,j) = n^{O(k)}
```

states at each size.  Thus tournament `k`-Degreewidth is in `n^{O(k)}` time.
For Q1, `k=2`, this gives the polynomial theorem above.

## 6. Verification artifacts

The focused regression test is in `tests/test_q1_degreewidth.py`:

```text
test_constant_diameter_exchange_bound
```

It checks the bipartite exchange inequality and the resulting
`|S △ S'| ≤ 8` bound on exhaustive small tournaments and random samples.  The
older tests still cover the exact recognizer and the lemmas from the
quasi-polynomial route.
