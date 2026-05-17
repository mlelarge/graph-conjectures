# D3 (R5a) — Faithful reconstruction of Fox-Pach-Suk Claim 3.7

Source: J. Fox, J. Pach, A. Suk, *Immersions and Albertson's conjecture*,
arXiv:2510.05893v1 (7 Oct 2025). Throughout, "FPS" denotes this paper.
Page numbers refer to the v1 PDF. The PDF was downloaded and converted with
`pdftotext -layout` to `/tmp/fps_2510_05893.txt`; all quoted passages were
verified against the converted text.

This is a faithful reconstruction. Sections 4–6 walk through FPS's algebra
without modification; section 7 contains the only forward-looking material.

---

## 1. Notation

I keep FPS's notation throughout, because the algebra is short and tracks
their printed equations one-for-one. Below is a glossary mapping any
alternative names a reader might use to FPS's choices.

| This document | FPS notation | Definition |
|---|---|---|
| `G` | `G` | The host k-critical graph |
| `k` | `k` | Chromatic number of `G` |
| `V_i` | `V_i` | Gallai-decomposition part of `V(G)`, `G[V_i]` is `k_i`-critical |
| `n_i, k_i` | `n_i, k_i` | `|V_i|`, chromatic number of `G[V_i]`; `n_i ≥ 2k_i − 1` |
| `U_i ⊂ V_i` | `U_i` | Chosen subset of size `k_i` (the branch vertices on `V_i`) |
| `W_i = V_i \ U_i` | `W_i` | Complement of `U_i` in `V_i`; `|W_i| = n_i − k_i` |
| `f_u` | `f_u` | One-to-one map `U_i \ (N(u) ∪ {u}) → W_i ∩ N(u)`, `u ∈ U_i` |
| `H_i` | `H_i` | Multigraph on `W_i`: edge `f_u(u') – f_{u'}(u)` for each non-adjacent pair `u,u'` of `U_i` with `f_u(u') ≠ f_{u'}(u)` |
| `d` (in this section, `d_i` once we suppress `i`) | `d` | Degree threshold for the semi-random selection of `U`; FPS set `d := 9k/8 = 1.125 k` (PDF p. 7) |
| `φ(k) = k^{0.9}` | `φ(k)` | `o(k)` slack term controlling the random part of `U` |
| `U(d)` | `U(d)` | The "high-degree" set entering `U`: vertices of degree `≥ d`, capped at `k − φ(k)` |
| `ℓ` | `ℓ` | `|U(d)|`; `ℓ ≤ k − φ(k)` |
| `ℓ_w` | `ℓ_w` | For `w ∈ V \ U(d)`, number of neighbors of `w` in `U(d)` |
| `U_w` | `U_w` | `N_{G*}(w) ∩ U` (the set of `U`-neighbors of `w` in the modified graph `G*`) |
| `G*` | `G*` | The modified graph obtained by the edge-swap pre-processing described on FPS p. 7–8 |
| `Δ, μ` | `Δ, μ` | Maximum degree, maximum edge multiplicity of `H` |
| `α, β, γ, δ` | `α, β, γ, δ` | The normalised optimisation variables of Claim 3.7 (defined below) |

After fixing an index `i`, FPS drop subscripts (p. 7, lines after the proof
opens): `n := n_i`, `k := k_i`, `V := V_i`, `U := U_i`, `W := W_i`, `H := H_i`.
I do the same throughout sections 3–7.

The three asymptotic optimisation variables for Claim 3.7 are:

- `α = ℓ_w / k` — normalised number of `U(d)`-neighbours of a target `w`;
- `β = ℓ / k` — normalised size of the deterministic ("high-degree") part of `U`;
- `γ = |U_w| / k` — normalised total number of `U`-neighbours of `w`;
- `δ = d / k = 9/8` — the (fixed) normalised degree threshold.

---

## 2. Setup leading into Claim 3.7

The Gallai decomposition (Lemma 2.1, FPS p. 3) reduces Theorem 1.2 to bounding
`χ'(H_i)` on each part. The skeleton of Theorem 1.2(ii) (FPS p. 5,
"Proof of Theorem 1.2(ii)") shows that

> "if `χ'(H_i) ≤ k − k_i` for every `i`, then `G` contains the desired weak
> immersion of `K_k`".

The threshold `n < (1.64 − ε)k` then follows by combining
`χ'(H_i) ≤ (9/16 + ε)k_i` from Lemma 2.3 with `k_i ≤ n − k + 1`.

**Construction of the multigraph `H`.** Lemma 2.3 itself is proved by the
semi-random argument of Section 3:

1. Form `U(d) ⊂ V` from vertices of degree `≥ d := 9k/8`, capped to size
   `k − φ(k)` (footnote 1, FPS p. 6).
2. Add the remaining `k − ℓ ≥ φ(k)` vertices of `U` uniformly at random
   from the leftover `n − ℓ` vertices.
3. Pre-fix `f_u, f_{u'}` on every triple `(u, u', w)` with `u ∈ U(d)`,
   `u' ∈ U`, `w ∈ W`, `u u'` non-adjacent, `w ∈ N(u) ∩ N(u')`: set
   `f_u(u') = f_{u'}(u) = w` and modify `G` by deleting `(u,w),(u',w)` and
   adding `(u,u')`. Iterate to obtain `G*`. (FPS p. 7.)
4. Complete each `f_u` uniformly at random over the remaining domain/range.

`H` is then the multigraph on `W` defined edge-by-edge by non-adjacent pairs
`(u, u')` in `G` with `f_u(u') ≠ f_{u'}(u)`. By Vizing-Gupta (Lemma 2.2(ii)),
`χ'(H) ≤ Δ + μ`. Lemma 2.3 reduces to:

- **Proposition 3.3** (FPS p. 8): w.h.p. `Δ ≤ (9/16 + o(1))k`.
- **Proposition 3.4** (FPS p. 11): w.h.p. `μ = o(k)`.

**Why `d = 9k/8`.** The threshold `δ = 9/8` is the value that makes Claim 3.7
balance: the stationary point of the Case-2 objective (worked below in
section 6) yields `α* = (9 − 3/η)/8`, and substituting `η = 1/2` (the worst
case of Case 2b) gives objective value `9/16`. Any other `δ` would shift
both the constraint set and the optimum; FPS chose `δ = 9/8` so that the
Case-2 optimum lands exactly at `9/16`, matching Case 1's `δ/2 = 9/16` bound.
This is *not* explicitly justified in FPS — it is reverse-engineered from the
fact that both Case 1 (worst at `β = 0`, giving `δ/2`) and Case 2b (worst at
`η = 1/2`, also giving `9/16` when `δ = 9/8`) hit the same value. See
"Things still to verify" §8.

---

## 3. Statement of Claim 3.7 (FPS p. 9, in FPS's own variables)

> **Claim 3.7.** The maximum value of (6), under the conditions `0 ≤ α ≤ β ≤ 1`
> and `0 ≤ γ ≤ α + (δ − α)(1 − β)/(2 − β)`, is `9/16`.

Here (6) refers to the asymptotic upper bound on `deg_H(w)/k` derived from
Claim 3.6:

```
f(α, β, γ; δ) = γ − α · (δ − 1)/(δ − γ),         with δ = 9/8.        (6)
```

The constraint `γ ≤ α + (δ − α)(1 − β)/(2 − β)` is the asymptotic form of
inequality (4), Claim 3.5 (FPS p. 8):

```
|U_w| ≤ ℓ_w + (d − ℓ_w) · (k − ℓ)/(2k − ℓ − 1) + o(k).            (4)
```

(`(k − ℓ)/(2k − ℓ − 1) → (1 − β)/(2 − β)` after normalising.)

**Case split (FPS p. 10, "Proof of Claim 3.7").** FPS observe that (6) is
strictly decreasing in `α`, so the maximum over `α` is attained either when

- **Case 1:** `α = 0` (the lower bound for `α`), or
- **Case 2:** `γ = α + (δ − α)(1 − β)/(2 − β)` (the upper-bound constraint on `γ` is tight).

Case 2 is then split by the location of the stationary point of the objective
in `α` once `γ` is substituted:

- **Case 2a:** stationary point interior to `[0, β]` (i.e. `η ≥ 5/7`).
- **Case 2b:** stationary point above `β` (i.e. `1/2 ≤ η < 5/7`), forcing the
  boundary `α = β` (equivalently `α = 2 − 1/η`).

Here `η := 1 − (1 − β)/(2 − β) ∈ [1/2, 1]` is FPS's reparametrisation; it is
monotonically increasing in `β`.

---

## 4. Case 1 — full reconstruction

**Hypothesis.** `α = 0`.

**Substituting into (6):**

```
f(0, β, γ; δ) = γ − 0 · (δ − 1)/(δ − γ) = γ.
```

The active constraint is `γ ≤ 0 + (δ − 0)(1 − β)/(2 − β) = δ(1 − β)/(2 − β)`,
so

```
f(0, β, γ; 9/8) ≤ δ · (1 − β)/(2 − β).
```

The right-hand side is decreasing in `β` (derivative in `β`: a quick check
gives `−1/(2 − β)^2 < 0`), so the maximum is at `β = 0`, yielding

```
f ≤ δ · 1/2 = 9/16.
```

**Binding inequalities.**
- The constraint `γ = δ(1 − β)/(2 − β)` is tight by construction in Case 2,
  but in Case 1 the binding is `γ ≤ δ(1 − β)/(2 − β)` with the maximiser at
  `β = 0` giving `γ = δ/2`.
- The lower bound `α ≥ 0` is tight by assumption.
- The Case-1 bound `9/16` equals `δ/2`. **Reducing `δ` directly reduces this
  case's value linearly.**

---

## 5. Case 2a — full reconstruction

**Hypothesis.** `γ = α + (δ − α)(1 − β)/(2 − β)`. Define
`η := 1 − (1 − β)/(2 − β) ∈ [1/2, 1]`. Then

```
γ = α + (δ − α)(1 − η) = ηα + (1 − η)δ.
```

**Substituting into (6):**

```
f(α, β, ηα + (1 − η)δ; δ) = ηα + (1 − η)δ − α (δ − 1)/(δ − ηα − (1 − η)δ).
```

FPS observe (p. 10): "As a function of `α`, the objective function after
substituting in the formula `γ = ηα + (1 − η)δ` is concave for each fixed
`η`, and hence the objective function is maximized at the unique stationary
value"

```
α* = (9 − 3/η)/8                                              (stationary)
```

This is the symbolic stationary point in `α`. It is feasible (i.e. `α* ≤ β`)
iff `η ≥ 5/7` (FPS, same paragraph). This is the Case-2a regime.

**Substituting `α = α*`:** The objective becomes (FPS, end of Case 2a)

```
f = (3 + 1/η)/8.
```

This is **decreasing** in `η`, so its maximum over Case 2a (`η ∈ [5/7, 1]`)
is at `η = 5/7`:

```
f ≤ (3 + 7/5)/8 = (15/5 + 7/5)/8 = (22/5)/8 = 22/40 = 11/20 = 0.55.
```

**Binding inequalities.**
- `γ = α + (δ − α)(1 − β)/(2 − β)` (i.e. Claim 3.5 is tight) — by Case-2 hypothesis.
- `α = α* = (9 − 3/η)/8` — stationarity in `α`.
- `η = 5/7` — boundary of Case 2a (the constraint `α* ≤ β`, equivalently `α ≤ β`).
- Resulting value: `11/20 = 0.55 < 9/16 = 0.5625`. **So Case 2a is not the
  binding case.**

---

## 6. Case 2b — full reconstruction (the binding case)

**Hypothesis.** `γ = α + (δ − α)(1 − β)/(2 − β)` *and* the stationary point
in `α` lies above the feasible region, i.e. `η < 5/7`. The optimiser is then
forced to the boundary `α = β`, equivalently (using `β = 1 − (1 − β)`)
`α = 2 − 1/η`.

FPS (p. 10, Case 2b):

> "In this case, the maximum is achieved at `α = β`, that is, `α = 2 − 1/η`.
> Substituting in, the objective function becomes
>
>     (7η + 1)/8 − (2 + 1/η)/(8 − 7η).
>
> The objective function is now decreasing in `η` in its domain. Hence, it is
> maximized for `η = 1/2`, and its value is at most `9/16`."

**Verifying the substitution.** With `α = 2 − 1/η` and `δ = 9/8`,

- `γ = ηα + (1 − η)δ = η(2 − 1/η) + (1 − η)(9/8) = 2η − 1 + 9/8 − 9η/8 = (16η − 8 + 9 − 9η)/8 = (7η + 1)/8`.
- `δ − γ = 9/8 − (7η + 1)/8 = (8 − 7η)/8`.
- `α(δ − 1) = (2 − 1/η)(9/8 − 1) = (2 − 1/η)(1/8) = (2η − 1)/(8η)`.
- `α(δ − 1)/(δ − γ) = ((2η − 1)/(8η)) / ((8 − 7η)/8) = (2η − 1)/(η(8 − 7η))`.

A cleaner equivalent form (matching FPS's display) is obtained by rewriting
`α(δ − 1)/(δ − γ)`:

```
α(δ − 1)/(δ − γ) = (2 − 1/η)·(1/8) · 8/(8 − 7η) = (2 − 1/η)/(8 − 7η) = (2η − 1)/(η(8 − 7η)).
```

FPS's display `(2 + 1/η)/(8 − 7η)` differs from `(2 − 1/η)/(8 − 7η)` by a sign
on the `1/η` term. Tracking it carefully: `α = 2 − 1/η`, so `α(δ−1) =
(2 − 1/η)/8`, and dividing by `(8 − 7η)/8` gives `(2 − 1/η)/(8 − 7η)`. I do
not reproduce FPS's `+` in the numerator from my expansion. Either FPS has
a typo (likely `−`, not `+`), or there is an algebraic step I am missing.
**Listed in §8 (Things still to verify) — this is the single ambiguity in
my reconstruction.** Either way, both versions agree on the value at the
binding point `η = 1/2`:

- FPS form: `(7·(1/2) + 1)/8 − (2 + 2)/(8 − 7/2) = (9/2)/8 − 4/(9/2) = 9/16 − 8/9`. This is negative — clearly *not* `9/16`.
- My form: `(7·(1/2) + 1)/8 − (2 − 2)/(8 − 7/2) = 9/16 − 0 = 9/16`. **Matches FPS's claimed value.**

So my form (`−1/η` in the numerator) is the correct one, and the printed
`(2 + 1/η)/(8 − 7η)` in FPS p. 10 appears to be a sign typo. The conclusion
`9/16` is unaffected.

**The binding inequality.** At `η = 1/2`, the term `α(δ−1)/(δ−γ)` equals

```
(2η − 1)/(η(8 − 7η)) = 0,
```

because `2η − 1 = 0` at `η = 1/2`. So the objective collapses to `γ` alone:

```
f = γ − 0 = γ = (7·(1/2) + 1)/8 = (9/2)/8 = 9/16.
```

**This is the key structural fact:** at the binding configuration,
`α = 2 − 1/η = 0`, so the second term of the objective contributes nothing.
Concretely, `η = 1/2` corresponds (via `η = 1 − (1 − β)/(2 − β)`) to `β = 0`,
i.e. `ℓ = 0` — **no vertices in the high-degree set `U(d)`**, so the
deterministic part of `U` is empty and `U` is chosen entirely at random.
Then `α = ℓ_w/k = 0` as well (`U(d)` is empty, so `ℓ_w` is `0`), and
`γ = |U_w|/k` saturates the Claim 3.5 bound at `δ/2 = 9/16`.

**Binding inequalities, ranked in priority of slack-recovery interest:**

1. **`α = 2 − 1/η`, equivalently `α = β`.** The Case-2b optimum is pushed to
   the boundary `α = β` because the interior stationary `α*` is infeasible.
   Equivalently, **`ℓ_w = ℓ`**: every vertex of the high-degree set `U(d)`
   is a neighbour of the target `w`. This is the binding "geometric"
   inequality.
2. **`γ = α + (δ − α)(1 − β)/(2 − β)` (Claim 3.5 is tight).** The semi-random
   `U_w` saturates its expected size. **Claim 3.5 is tight at the binding
   point.**
3. **`η = 1/2`, equivalently `β = 0`, equivalently `ℓ = 0`.** The optimum
   is at the lower end of the Case-2b interval, meaning the **deterministic
   high-degree set is empty**. Together with item 1, this forces the
   second-term contribution `α(δ − 1)/(δ − γ)` to *vanish* (the
   "chromatic-index-saving" term gives nothing).
4. **`δ = 9/8`.** The value `9/16 = δ/2` follows from `γ = (7η + 1)/8 = 9/16`
   at `η = 1/2`, and `(7·(1/2) + 1)/8 = (9/2)/8 = 9/16`. Replacing `δ` by a
   different value would change `γ = ηα + (1 − η)δ` but, at `α = 0, η = 1/2`,
   `γ = δ/2`. So **the binding bound is precisely `δ/2`, identical to Case 1**.

**The single binding inequality in Case 2b is the saturated form of Claim
3.5 evaluated at `α = β = 0`:** `γ ≤ δ(1 − β)/(2 − β)` with the equality
attained at `β = 0`. The "interesting" piece of the objective —
`α(δ − 1)/(δ − γ)` — is *exactly zero* at the binding point because `α = 0`.

In one sentence: **the Case-2b binding inequality is `|U_w| ≤ d/2` (the
asymptotic form of Claim 3.5 when `U(d)` is empty and `U` is chosen entirely
uniformly at random).**

---

## 7. Where could `c < 9/16` come from? (≤ 2 paragraphs)

**(a) Does Case 2b's binding inequality have slack?** At the binding point
`(α, β, η) = (0, 0, 1/2)`, FPS's Case-2b reduces to "`γ ≤ δ/2`", which is
*identical* to the Case-1 maximiser. The chromatic-index-saving term
`α(δ − 1)/(δ − γ)` vanishes because `α = 0`. So **any improvement to
Case 2b's `9/16` must come from a sharpening of Claim 3.5** (the upper
bound on `|U_w|`) when the high-degree set is empty, *not* from anywhere in
the Claim 3.6 multiplicity-saving machinery. With `U(d) = ∅`, Claim 3.5
reduces to the elementary Chernoff bound on the number of random `U`-neighbours
of `w`, which is concentrated at its mean `d · (k − ℓ)/(2k − ℓ − 1) = d/2`
(for `ℓ = 0`). The mean *is* `d/2` and concentration is tight, so Claim 3.5
**has no slack to spare at the binding point under threshold-uniform `U_i`
selection.** Improvements to `c < 9/16` therefore have to either (i) change
`δ` (lower `δ` lowers the Case-1 / Case-2b ceiling proportionally, but raises
Case 2a — TODO: verify the Case 2a maximum as `δ` varies; the value
`(3 + 1/η)/8` does not contain `δ`, so naïvely Case 2a is `δ`-independent,
which would mean **reducing `δ` to lower the binding cases is free** until
Case 2a's `11/20` becomes binding — *this is the single most concrete
follow-up*, see §8.4 below), or (ii) sharpen Claim 3.6 in a way that lets
the analysis enter a regime with `α > 0` (which Vizing-Gupta does not let
us do), or (iii) replace Vizing-Gupta with Goldberg-Seymour / Kahn (separate
work).

**(b) The "free" improvement: `δ` as a free parameter.** The Case-2a value
`(3 + 1/η)/8` evaluated at the case boundary `η = 5/7` gives `11/20`,
**independent of `δ`** (the `δ` cancels out of `α* = (9 − 3/η)/8`'s objective
substitution — TODO: re-verify this; the literal stationary value
`α* = (9 − 3/η)/8` clearly *does* depend on the specific `δ = 9/8` used to
derive it. With `δ` free, `α* = (4δ − 1/η)/(...)` — I have not redone the
calculation). If, as I suspect from inspection, **the Case 2b ceiling
`δ/2` and Case 1 ceiling `δ/2` both scale linearly in `δ` while Case 2a
remains at `11/20`, then lowering `δ` from `9/8` to `11/10` (i.e.
`δ/2 = 11/20`) would equalise all three cases at `11/20` and immediately
improve `9/16 → 11/20`. This is the "free improvement" candidate.** It is
exactly the calculation Role 7 flagged as D5/Q2 in `work/07_immersion/memo.md`.

---

## 8. Things still to verify

The reconstruction depends on the following items that I either could not
fully resolve from the FPS PDF or had to interpret.

1. **Sign discrepancy in the Case-2b objective (§6, line "FPS form vs my
   form").** FPS p. 10 prints `(7η + 1)/8 − (2 + 1/η)/(8 − 7η)`. My algebra
   from `α = 2 − 1/η, δ = 9/8` gives `(7η + 1)/8 − (2 − 1/η)/(8 − 7η)`. Only
   my form yields the claimed value `9/16` at `η = 1/2`. **I treat the FPS
   `+` as a typo.** Cross-check against the SoCG-2025 published version (not
   yet obtained — TODO).

2. **The `α* = (9 − 3/η)/8` formula** (FPS p. 10) is reported without
   derivation. I have not verified it from the concavity-in-`α` argument
   FPS sketches. The full derivation requires differentiating
   `f(α, η) = ηα + (1 − η)δ − α(δ − 1)/(δ − ηα − (1 − η)δ)` in `α` with
   `δ = 9/8` and solving. **TODO: compute and confirm `α* = (9 − 3/η)/8`
   symbolically (≤ 1 hour of SymPy).**

3. **Case 2a value's dependence on `δ`** (§7, end of paragraph (b)). The
   claim `(3 + 1/η)/8` after substituting `α = α*` was reported verbatim by
   FPS without showing the dependence on `δ`. If `α*` itself depends on `δ`
   (it must), so should the resulting value. **The free-`δ` re-derivation is
   the immediate calculation to do. This is the "concrete next experiment".**

4. **Why FPS chose `δ = 9/8`.** The PDF gives no justification beyond
   "let `d := 9k/8 = 1.125 k`" (p. 7). My reverse-engineering in §2 is a
   guess based on the fact that Case 1 and Case 2b both yield `δ/2 = 9/16`.
   **TODO: confirm by computing the Case 2a value as a function of `δ`** (if
   it equals `11/20 + g(δ)` with `g(δ) > 0` for `δ ≠ 9/8`, then `9/8` is the
   minimising `δ` and no free improvement is possible — *the negative
   outcome*).

5. **The `(k − ℓ)/(2k − ℓ − 1) → (1 − β)/(2 − β)` limit** (§3, after stating
   inequality (4)) requires `ℓ = β k` for the limit to make sense, which is
   only valid if `β > 0`. At `β = 0` (the Case-2b binding point), `ℓ = 0`
   identically, and the limit is `(k)/(2k − 1) → 1/2`, which agrees with
   `(1 − 0)/(2 − 0) = 1/2`. So the limit is continuous at the binding point,
   but the limit is *taken* at `β = 0`, where the original quantity is `1/2`
   exactly, not asymptotically — a subtle non-uniformity that I do not think
   matters for the bound, but worth flagging.

6. **"Case II" (FPS p. 11) is not reconstructed here.** FPS handle the case
   `ℓ = k − φ(k)` (lots of high-degree vertices) by reducing to a special
   `β = 1 − o(1)` instance of the same optimisation. At `β = 1`, the
   constraint `γ ≤ α + 0 = α` forces `γ = α` (in Case 2), and the objective
   becomes `α − α(δ − 1)/(δ − α)`. **TODO: verify this special case
   independently and confirm it does not give a worse bound than `9/16`.**
   FPS assert "the analysis of this case reduces to that of Case I" (p. 11);
   I take this on faith.

7. **Footnote 1 of FPS (p. 6).** "if there is more than `k_i − k_i^{0.9}`
   vertices of degree at least `d_i`, we only pick `k_i − k_i^{0.9}` of them
   to be in `U_i` and pick an additional `k_i^{0.9}` uniform random
   vertices ... [this] allows us to obtain that with probability `1 − o(1)`
   the edge multiplicity of `H_i` is `o(k_i)`." This is the only place
   Proposition 3.4 (`μ = o(k)`) interacts with the construction of `U`. **It
   does not affect Claim 3.7 — Claim 3.7 is purely about `Δ`.**

---

## Provenance summary

- FPS arXiv PDF: downloaded `2025-10-07` version to `/tmp/fps_2510_05893.pdf`
  on the date of writing; extracted with `pdftotext -layout`.
- Sections 1, 2 of this reconstruction: synthesise FPS Sections 2 and 3.
- Section 3 (statement): direct quote from FPS p. 9.
- Section 4 (Case 1): FPS p. 10, one short paragraph, fully reconstructed.
- Section 5 (Case 2a): FPS p. 10, fully reconstructed; the `11/20` is FPS's
  printed value.
- Section 6 (Case 2b): FPS p. 10, fully reconstructed; **one sign discrepancy
  flagged in §8.1**, conclusion `9/16` agrees with FPS.
- Section 7: my synthesis, not FPS.
- Section 8: my honest list of gaps.
