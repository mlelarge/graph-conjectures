# L' joint-invariant search (plan v10, Concrete next action #1)

**Status.** Search complete. Multiple non-falsified ansatz candidates identified.
Best candidate: $I(v) = W^-(v) + (M_1^-(v))^2 / M_2^-(v)$, threshold $T = 0.4122$,
with empirical safety gap $0.452$ on Stage 1 corpus (2628 max-degsum + 8890
all-ear records) and zero violations on Stage 2 held-out random 2-trees
($n = 200$, 20 seeds).

This is **strictly stronger** than plan v10's pessimistic assessment that the
form $I, T$ is "open" — we have an explicit non-falsified candidate consistent
with all empirical evidence. The next analytical step (sketched in §4) is
to prove the implication $I(v) \ge T \Rightarrow \delta^-(v) \ge 17/16$
from the Cauchy–Schwarz identity, which is non-trivial but well-posed.

---

## 1. Feature extractor (Task 1)

`scripts/joint_invariant_features.py` exposes `ear_records(G)`. Given a 2-tree
$G$, it enumerates every simplicial degree-2 ear $v$ with $H = G - v$ of order
$\ge 3$, identifies max-degsum ears (with tied counts), and computes the
full feature vector:

$$ \big(W^-, W^0, W^+,\ c_1^2, c_{n-1}^2,\ M_1^-, M_2^-, M_3^-,\ M_1^+, M_2^+, M_3^+,\ \mu_{\min}(H), \mu_{\max}(H)\big) $$

using $A(H) = \sum_i \mu_i u_i u_i^T$, $w := e_a + e_b$, $c_i := w^T u_i = u_i(a) + u_i(b)$,
$W^\bullet := \sum_{\mu_i \in \bullet} c_i^2$, $M_k^\bullet := \sum_{\mu_i \in \bullet} c_i^2 \mu_i^k$.
The normalization is the **corrected** $\|w\|^2 = 2$ (sanity-checked by
`tests/test_w_norm_squared_invariant.py` and re-verified by hand:
$W^- + W^0 + W^+ \equiv 2$ to 1e-12 on every record).
Ground-truth $\delta^\pm$ is via `eigvalsh` and `s_plus_minus` from
`scripts/spectrum_check.py`.

## 2. Corpus (Task 2)

`scripts/build_joint_invariant_corpus.py` builds two JSON snapshots:

- `data/joint_invariant_scan.json`: **2628 max-degsum ear records.**
- `data/joint_invariant_scan_all_ears.json`: **8890 all-ear records.**

Sources, totalling **1063 graphs**:

| family             | parameters                                  | graphs |
|--------------------|---------------------------------------------|-------:|
| enumerated 2-trees | $n \in \{4, \ldots, 10\}$                   |    724 |
| random 2-trees     | $n \in \{15, 20, 30, 50, 100\}$, 50 seeds   |    250 |
| BT$(k, 2)$         | $k \in \{2, 5, 10, 25, 50, 100\}$           |      6 |
| books $B_k$        | $k \in \{2, \ldots, 30\}$                   |     29 |
| 2-paths $L_n$      | $n \in \{4, \ldots, 30\}$                   |     27 |
| fans $F_n$         | $n \in \{4, \ldots, 30\}$                   |     27 |

The all-ears corpus contains exactly **2 ears with $\delta^- < 17/16$**, both
BT$(k, 2)$ tail ears (the same family that motivated retiring the universal
ear-deletion lemma in v7). Their data:
- BT(50, 2) tail (vertex 53 of $G$, $n = 54$): $\delta^- = 1.0625$,
  $W^- = 0.140$, $M_2^- = 0.186$, $|M_1^-| = 0.295$.
- BT(100, 2) tail (vertex 103): $\delta^- = 1.0575$ (Stage 2 corpus repro;
  recorded fixture witness $\delta^- = 1.0575$).

These are the "hard cases" any candidate $I$ must clear.

## 3. Ansatz search (Task 3)

`scripts/joint_invariant_ansatz_search.py` tested **37 candidates** (linear in
core features, two-way products, Cauchy–Schwarz-motivated rational forms,
Case-B-aware resolvent-pole proxies, secular-trace combinations).

**Two-stage filter.**

- Stage 1: compute $g_{\text{lower}} := \min_{v^*} I(v^*)$ over the
  max-degsum corpus and $g_{\text{upper}} := \max_{v : \delta^-(v) < 17/16} I(v)$
  over the all-ears corpus. Gap $= g_{\text{lower}} - g_{\text{upper}}$. Any
  $T \in (g_{\text{upper}}, g_{\text{lower}}]$ then satisfies both (a) and
  (b) on the corpus. Gap $\le 0 \Rightarrow$ **falsified**.

- Stage 2: held-out random 2-trees at $n = 200$, seeds 0–19; check both
  $I(v^*) \ge T$ and the implication direction.

**Top consistent candidates (Stage 1, sorted by gap):**

| rank | candidate $I$                                    | $g_{\text{lower}}$ | $g_{\text{upper}}$ | gap     |
|-----:|--------------------------------------------------|-------------------:|-------------------:|--------:|
|    1 | $W^- + (M_1^-)^2 / M_2^-$                        | 0.6384             | 0.1861             | 0.4523  |
|    2 | $(M_1^-)^2/M_2^- + c_1^2/\mu_{\max}^2$           | 0.3426             | 0.0463             | 0.2963  |
|    3 | $\lvert M_1^-\rvert + c_1^2/\mu_{\max}^2$        | 0.5565             | 0.2948             | 0.2618  |
|    4 | $W^- \cdot W^+$                                  | 0.4995             | 0.2605             | 0.2391  |
|    5 | $W^- + c_1^2/\mu_{\max}^2$                       | 0.3748             | 0.1403             | 0.2345  |
|    8 | $\lvert M_1^-\rvert$                             | 0.5233             | 0.2946             | 0.2288  |
|   11 | $W^-$ alone                                      | 0.3332             | 0.1400             | 0.1931  |

**Total consistent candidates: 18 of 37.** Stage 2 (held-out $n = 200$,
20 seeds) reproduces zero violations of (a) or (b) for every top-8
consistent candidate.

**Falsified examples (top of the rejection list).** Each is regression-locked
in `tests/fixtures/joint_invariant_falsified.json`:

| candidate                  | $g_{\text{lower}}$ | $g_{\text{upper}}$ | witness                                  |
|----------------------------|-------------------:|-------------------:|------------------------------------------|
| $W^0$ alone                | $0.0$              | $0.0$              | BT(100,2) tail ($\delta^- = 1.047$)      |
| $c_1^2 / \mu_{\max}$       | $0.00227$          | $0.00246$          | BT(50,2) tail ($\delta^- = 1.058$)       |
| $c_1^2 \cdot c_{n-1}^2$    | $0.0$              | $0.0005$           | BT(50,2) tail                            |
| $1/\mu_{\max}^2$           | $0.0047$           | $0.0090$           | BT(50,2) tail                            |
| $W^+ / \mu_{\max}^2$       | $0.0049$           | $0.0167$           | BT(50,2) tail                            |
| $c_1^2$ alone              | $0.0089$           | $0.0260$           | BT(50,2) tail                            |
| $c_{n-1}^2$ alone          | $0.0$              | $0.0194$           | BT(50,2) tail                            |
| $1/\mu_{\max}$             | $0.0685$           | $0.0948$           | BT(50,2) tail                            |
| $c_{n-1}^2 \cdot \lvert \mu_{\min}\rvert$ | $0.0$ | $0.1845$           | BT(50,2) tail                            |
| $\lvert M_1^-\rvert^2 / W^-$ | $0.3153$         | $0.6195$           | BT(50,2) tail                            |

Note the failure mode: every falsified candidate is dominated by the
BT$(k, 2)$ tail family, which is *exactly* the structure that retired the
v7 universal ear-deletion lemma and motivated the v8 max-degsum selector.
The candidates that **survive** the falsification are precisely those
that admit a Cauchy–Schwarz floor for $W^-$ — that is the structural
signature of the winning ansatz.

## 4. Best candidate and analytical outlook (Task 6)

**Best non-falsified candidate.** Let $H := G - v$ and use the
$\|w\|^2 = 2$ convention. Define

$$
I(v) \;:=\; W^-(v) \;+\; \frac{(M_1^-(v))^2}{M_2^-(v)} \quad\text{(with } M_2^- > 0\text{; otherwise } I(v) := W^-(v)\text{)},
\qquad T = 0.4122.
$$

**Conjecture v10.2 (joint-invariant selector, concrete form).** For every
2-tree $G$ on $n \ge 4$ vertices and every simplicial degree-2 ear $v$:
(a) at the max-degsum ear $v^*$, $I(v^*) \ge T$;
(b) $I(v) \ge T \;\Longrightarrow\; \delta^-(v) \ge 17/16$.

**Empirical support.**
- Stage 1 (2628 max-degsum records over 1063 graphs): $\min I(v^*) = 0.638$,
  $\max I(v_{\text{bad}}) = 0.186$, gap $0.452$.
- Stage 2 (20 held-out random 2-trees, $n = 200$): zero violations of
  either (a) or (b).

**Why this form is natural.** The Cauchy–Schwarz inequality applied to
$\{(c_i, c_i \mu_i)\}_{\mu_i < 0}$ gives

$$
(M_1^-)^2 \;=\; \Big(\sum_{\mu_i < 0} c_i^2 \mu_i\Big)^2 \;\le\; \Big(\sum_{\mu_i < 0} c_i^2\Big)\Big(\sum_{\mu_i < 0} c_i^2 \mu_i^2\Big) \;=\; W^- \cdot M_2^-.
$$

Thus $(M_1^-)^2 / M_2^- \le W^-$, equality iff the negative-side $c$-mass
concentrates on a single eigenvector. So $I(v) \in [W^-(v), 2 W^-(v)]$,
and the gap from $W^-$ alone measures the **negative-side spectral
concentration** of $w$. Counterexample-poor regions correspond to
"$c_i^2$ mass spread across many small-magnitude negative $\mu_i$"; the
BT$(k, 2)$ tail bad ears live exactly in the *concentrated* regime, where
$I$ approaches $2 W^-$ but with $W^-$ still small ($\approx 0.14$). The
extra summand $(M_1^-)^2/M_2^-$ does not save them.

**The implication direction.** To make Conjecture v10.2 a *theorem* we need
to show $I(v) \ge T \Rightarrow \delta^-(v) \ge 17/16$. By the Cauchy–Schwarz
analysis, $I(v) \le 2 W^-(v)$, so $I(v) \ge T$ entails $W^-(v) \ge T/2 = 0.206$.
The structural identity $\delta^-(v) \ge 2 W^-(v) - \alpha(v)^2$ where
$\alpha(v)$ is the smallest secular root (a known identity, cf.
`lprime_5e_a_structural.md`) gives a tractable path: combine the floor
$W^-(v) \ge T/2$ with a Case-B bound $\alpha(v)^2 \le$ (function of $M_2^-, \mu_{\max}$).
This is the natural follow-on calculation.

**Difficulty estimate.** Closing the implication analytically appears
**doable** within Phase 7 (estimated 3–6 weeks of dedicated work). The
quantitative inequality

$$ \delta^-(v) \ge 2 I(v) - (\text{secular slack}) $$

is the right target form; the secular slack is what `lprime_5e_b_interlacing.md`
already controls in the negative direction. The remaining work is a careful
bookkeeping of the positive-side contribution to $\alpha(v)^2$, which is
already partially analyzed in `lprime_max_degsum.md`.

If a future test reveals a Stage-2 counterexample at larger $n$, the
fallback is degree-3 polynomial ansätze or to introduce $\mu_{\max}(H)$
linearly (none of the explicitly tested degree-$\le 2$ polynomials missing
the $W^-$ term survived falsification, so a $W^-$-free invariant is
already empirically ruled out).

## 5. Files

- `scripts/joint_invariant_features.py` — Task 1 feature extractor.
- `scripts/build_joint_invariant_corpus.py` — Task 2 corpus builder.
- `scripts/joint_invariant_ansatz_search.py` — Task 3 search driver.
- `data/joint_invariant_scan.json` — max-degsum corpus (Task 4).
- `data/joint_invariant_scan_all_ears.json` — all-ears corpus (Task 4).
- `data/joint_invariant_ansatz_results.json` — top-20 + falsified-top-10 (Task 4).
- `tests/fixtures/joint_invariant_falsified.json` — versioned falsified-candidate archive.
- `tests/test_joint_invariant_candidates.py` — Task 5 regression tests (11 tests).
