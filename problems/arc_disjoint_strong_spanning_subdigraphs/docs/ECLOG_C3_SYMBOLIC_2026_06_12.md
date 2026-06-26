# EC-log C=3 sharpening: symbolic per-size proof (G10 salvage)

**Claim (Theorem ECLOG-3).** Every Eulerian digraph `D` on `n >= 17` vertices with
arc-connectivity `lambda := lambda^arc(D) >= 3*log2(n)` admits a strong arc
decomposition (SAD).

This sharpens P1-ECLOG (`lambda >= 6*log2 n`, `n_0 = 3`) to `lambda >= 3*log2 n`
for `n >= 17`. It is the *written symbolic per-size* argument whose absence
blocked promotion at G10. The constant `C = 6` is retained below `n_0 = 17`.

> HONESTY NOTE (this is where the proposal that produced this doc was WRONG, and
> what the certifier `scripts/eclog_c3_shell_check.py` enforces): the proposal's
> closed form
>   `B(n) = 4 n^2 2^{-lam} + 4 (n^2)^{1-e}/(e-1)`, `e = lam/(2 log2 n)`,
> is **NOT** an upper bound on the first-moment expectation — it *under-counts* it
> by a factor `~1.62` (certifier arm (A): `2S(n)/B(n) in [1.616,1.642]`). The
> correct, certifiable first-moment bound is the geometric closed form
>   `G(n) = head/(1 - r)`, `head = 4 n^2 2^{-lam}`, `r = n^{2/lam}/2`,
> which **equals** the exact two-cut Karger sum. Likewise the proposal's claim that
> the bound is `<1` already for `n >= 13` is FALSE: `G(16) = 1.2118 >= 1`, so the
> honest threshold is `n_0 = 17` (matching the salvaged `P1.round1_note`), NOT 13.
> The theorem below is stated and proved with the honest `G(n)` and `n_0 = 17`.

---

## 1. Setup and the Eulerian identity

`D = (V,A)` Eulerian: `d^+(v) = d^-(v)` for every `v`. Let `G` be the underlying
undirected multigraph (one undirected edge per arc). For any
`emptyset != X subsetneq V`,
```
d_G(X) = |delta^+(X)| + |delta^-(X)|.
```
Eulerianness forces `|delta^+(X)| = |delta^-(X)|` for **every** `X` (in/out degree
balance summed over `X`), hence the **Eulerian cut identity**
```
d_G(X) = 2 |delta^+(X)|.                                            (1)
```
In particular the undirected min cut `c := min_X d_G(X) = 2 lambda` (each directed
cut has size `>= lambda`, and `(1)` doubles it).

## 2. Karger cut-counting (the one external ingredient)

**Theorem (Karger, PhD thesis, Theorem 4.7.6; cf. Karger 2000, JACM 47(1),
Lemma 3.2 / Theorem 3.3).** In an `n`-vertex undirected (multi)graph with min
cut `c`, the number of cuts of weight `<= alpha c` is at most `n^{2 alpha}`
for every real `alpha >= 1`.

*Citation status (D25 review):* the REAL-alpha `n^{2 alpha}` statement is
exactly Karger's thesis Theorem 4.7.6
(https://people.csail.mit.edu/karger/Papers/thesis.pdf); the companion forms
are Karger 2000 Lemma 3.2 / Theorem 3.3 (https://arxiv.org/pdf/cs/9812007).
Two fallbacks previously advertised here are RETRACTED:
* the "half-integral `2^{2 alpha} C(n, 2 alpha)` substitution" is FALSE as a
  repair — it OVER-counts via the central binomial (`H(17) = 3.18 >= 1`;
  see G31 and `scripts/eclog_c3_halfintegral_check.py`);
* the "floor-form `n^{floor(2 alpha)}` re-derivation with `n_0 = 11`"
  (recorded at D22) is UNSUPPORTED: Karger 2000's floor-form bound carries an
  alpha-dependent constant (with a denominator that can approach zero) and
  cannot be inserted coefficient-one into the shell sum.
Neither fallback is needed: thesis Theorem 4.7.6 supplies the real-alpha
bound directly, and Sections 3–6 stand on it.

## 3. Per-size shell count for directed out-cuts

Fix a size `k >= lambda`. A bipartition with `|delta^+(X)| = k` has, by `(1)`,
undirected weight `2k = (2k/c) * c = (k/lambda) * c`, i.e. it is a
`(k/lambda)`-approximate undirected cut. By Karger with `alpha = k/lambda >= 1`,
the number of **undirected** cuts of weight `<= 2k` is at most
```
N_undir(<= 2k) <= n^{2 alpha} = n^{2k/lambda}.                       (2)
```
Each undirected cut `{X, V\X}` carries exactly **two** directed cuts,
`delta^+(X)` and `delta^-(X) = delta^+(V\X)`. So the number of directed out-cuts
of size exactly `k` is at most `2 * n^{2k/lambda}` (honest factor 2; this is the
"two directed cuts per bipartition" accounting the proposal flagged as step (3)).

## 4. First moment under a uniform random 2-colouring

Colour each arc red/blue independently uniformly. A directed cut `F = delta^+(X)`
of size `|F| = k` is *monochromatic* (a SAD obstruction) with probability
`2 * 2^{-k} = 2^{1-k}`. Summing over all directed out-cuts (size `>= lambda`),
using the per-shell count `2 n^{2k/lambda}` from Section 3:
```
E[# monochromatic directed out-cuts]
   <= sum_{k >= lambda} (2 n^{2k/lambda}) * 2^{1-k}
    = 4 * sum_{k >= lambda} n^{2k/lambda} 2^{-k}
    =: 2S(n).                                                        (3)
```
This is a **geometric series** with first term
`head = 4 n^{2} 2^{-lambda}` (at `k = lambda`, since `n^{2 lambda/lambda}=n^2`)
and ratio
```
r = n^{2/lambda} / 2.
```
Because `lambda >= 3 log2 n` we have `n^{2/lambda} <= n^{2/(3 log2 n)} = 2^{2/3}`,
hence
```
r <= 2^{2/3}/2 = 2^{-1/3} = 0.793700... < 1                          (4)
```
**exactly** (equality on `n = 2^j`). The series converges and
```
2S(n) = G(n) = head / (1 - r) = (4 n^2 2^{-lambda}) / (1 - n^{2/lambda}/2).   (5)
```

## 5. The honest bound `G(n) < 1` for `n >= 17`

Two symbolic dominators:
* **head:** `lambda >= 3 log2 n => 2^{-lambda} <= n^{-3} => head = 4 n^2 2^{-lambda} <= 4/n`.
* **ratio:** `(4)` gives `1 - r >= 1 - 2^{-1/3}`.

Therefore
```
G(n) = head/(1 - r) <= (4/n) / (1 - 2^{-1/3}) = (4 / (1 - 2^{-1/3})) / n
     = 19.389... / n,                                                (6)
```
which is `< 1` for `n >= 20`. The three residual sizes are checked directly from
`(5)` (with `lambda = ceil(3 log2 n)`):
```
G(17) = 0.6221,  G(18) = 0.7191,  G(19) = 0.8256   (all < 1).
```
Hence `G(n) < 1` for **all** `n >= 17`. (Certifier arm (B) confirms `G(n) < 1`
for every `17 <= n <= 2^20`, worst `0.9423` at `n = 20`, zero violations.)

`n_0 = 17` is **tight for this argument**: `G(16) = 1.2118 >= 1` (certifier arm
(C)). So the bound cannot be pushed below 17 without a sharper count; the
proposal's `n_0 = 13` claim is refuted here.

**Remark (D25 review): the method is NOT exhausted at `C = 3`.**  The same
proof gives, for every fixed `C > 2` and `lambda >= C log2 n`:
`head <= 4 n^{2-C}` and `r <= 2^{2/C - 1} < 1`, hence
```
G(n) <= 4 n^{2-C} / (1 - 2^{2/C-1})  ->  0.
```
So static first moment proves `lambda >= (2 + eps) log2 n` suffices for all
`n >= n_0(eps)`; only `C = 2` is the apparent barrier of the method
(`r -> 1`, the series diverges).  What IS specific to `C = 3` is the
threshold: `n_0 = 17` is tight for that constant.  The earlier ledger claim
"static first moment exhausted at C = 3" was false and is retracted.

## 6. Conclusion: first moment => a SAD

`E[# monochromatic directed out-cuts] = 2S(n) = G(n) < 1` for `n >= 17`, so some
2-colouring leaves **every** directed cut bichromatic. By the standard criterion
(every directed cut bichromatic <=> both colour classes are spanning strongly
connected; cf. P1-ECLOG / team/04), that colouring is a SAD. QED.

---

## 7. What changed vs G10 (and vs the proposal that generated this doc)

* G10 died for (i) `n_0 ~ 10` (false; true `n_0 = 17`) and (ii) "theorem-covered"
  with no written symbolic argument. This doc supplies the symbolic per-size
  argument (Sections 1–6) AND uses the honest `n_0 = 17`.
* The proposal that produced this doc *also* contained the too-small-`n_0`
  error in a milder form (it claimed `n_0 = 13`) and used an **under-counting**
  closed form `B(n)` in place of the true first-moment sum. Both are corrected
  here: the load-bearing bound is the exact geometric `G(n) = head/(1-r)`, and
  `n_0 = 17`. The honest symbolic one-liner is `G(n) <= 19.39/n` (not the
  proposal's `12/n`), giving `n >= 20` plus three direct checks for `17,18,19`.

## 8. Certificates (all foreground, this turn)

* `scripts/eclog_c3_shell_check.py` — arms (A) B under-counts; (B) `G(n)<1`
  for `17<=n<=2^20`; (C) `n_0=13` refuted, `n_0=17`; (D) honest dominator
  `G<=19.39/n`; plus `r=2^{-1/3}` exactly on powers of two. ALL PASS.
* `scripts/eclog_c3_bound.py` (pre-existing) — exact two-cut sum `2S`,
  independently reports `n0_doubled = 17`, `max ratio = 0.7937`. Agreement.
* `scripts/eclog_c3_boundary_confirm.py` — Eulerian circulant on `Z_17`,
  out-deg = in-deg = 13, oracle `lambda = 13 = ceil(3 log2 17)`,
  oracle `SAD = SAT`, both backends agree. The boundary instance is SAT,
  as the theorem predicts.

## 9. Promotion status

REVIEWED AND ACCEPTED (D25, human review: "conditional pass", conditions now
applied).  What passed review: the Eulerian cut identity (1), the factor-two
directed-cut accounting (S3), the monochromatic probability and geometric
summation (S4–S5), and the `n_0 = 17` threshold for the specific `C = 3`,
`n^{2 alpha}` bound — with the citation now resting on Karger's thesis
Theorem 4.7.6 (real alpha), not on the retracted floor/half-integral
fallbacks.  Exact-arithmetic certification of the finitely many load-bearing
inequalities is `scripts/eclog_c3_exact_check.py` (pure integers: `n = 16`
fails, `n = 17,18,19` pass, the `n >= 20` dominator via a cube comparison);
the earlier floating-point sweeps remain as redundant checks.  NOT promoted:
"floor-form gives `n_0 = 11`" and "static first moment exhausted at `C = 3`"
(both retracted, see S2 and the S5 remark).
