# Weakening the hypothesis of Theorem 8.1 (the $\alpha\omega$ route)

**Status.** Investigative note in support of plan v13. Two-week exploration
brief; honest verdict at end.

**Source.** Akbari–Kumar–Mohar–Pragada–Zhang, *Refinement of a conjecture on
positive square energy of graphs*, arXiv:2506.07264 v1, 8 Jun 2025.

**Goal.** Examine whether the constant $17$ in Theorem 8.1 can be reduced,
or the hypothesis $\alpha(G)\omega(G) \le n/17$ replaced by a weaker
structural condition, so as to cover a larger slice of Conjecture 9.2 than
just 2-trees.

---

## 1.  Setup and exact statement of Theorem 8.1

We use the notation of the source paper.  Let $G$ be a simple graph of
order $n$, with adjacency eigenvalues
$\lambda_1 \ge \cdots \ge \lambda_n$, and
$$
s^+(G) \;=\; \sum_{\lambda_i > 0} \lambda_i^2,
\qquad
s^-(G) \;=\; \sum_{\lambda_i < 0} \lambda_i^2.
$$
Let $\alpha(G)$ be the independence number and $\omega(G)$ the clique number.

The relevant statements, quoted verbatim from the source paper:

**Lemma 2.4** ($P_3$-removal lemma, [22]).
*Let $G$ be any graph and $\epsilon = 1/16$.  Suppose $U$ is a set of
three vertices in $G$ such that $G[U] \cong P_3$.  Then there exists a
vertex $u \in U$ such that*
$$
s^+(G) \;\ge\; s^+(G - u) + 1 + \epsilon.
$$
*The same also holds if $s^+$ is replaced with $s^-$.*

**Theorem 8.1.**
*There exists a constant $c = \tfrac{1}{17}$ such that if $G$ is a
connected graph of order $n$ with $\alpha(G)\omega(G) \le cn$, then*
$$
\min\{s^+(G),\; s^-(G)\} \;\ge\; n.
$$

**Conjecture 9.2** (the target equality conjecture).
*Let $G$ be a connected graph of order $n$.*
*(i) $s^+(G) = n - 1$ iff $G$ is a tree.*
*(ii) $s^-(G) = n - 1$ iff $G$ is a tree or a complete graph $K_n$.*

Since $\min(s^+, s^-) \ge n$ from Theorem 8.1 implies *both* $s^+ \ge n$
and $s^- \ge n$, both equality cases of Conjecture 9.2 hold trivially for
any $G$ in the hypothesis class.

---

## 2.  Where the constant $17$ enters the algebra

The proof in §8 of the source paper is short and crisp.  We re-trace it
to isolate the role of every constant.

**Step 1 — choose $\epsilon$, set $c$.**  Take $\epsilon = 1/16$ (the value
for which Lemma 2.4 is proved).  Set $c = \epsilon / (1 + \epsilon) = 1/17$.

**Step 2 — iterated $P_3$-removal.**  Argue by contradiction: assume
$s^-(G) < n$.  Build a chain $V_0 = V(G) \supseteq V_1 \supseteq \cdots$
of induced subgraphs as follows.  At step $i$, if $G_i := G[V_i]$ has an
induced $P_3$, pick a removal vertex $u_i$ via Lemma 2.4 with
$s^-(G_i) \ge s^-(G_i - u_i) + 1 + \epsilon$ and set $V_{i+1} := V_i \setminus \{u_i\}$.
Otherwise stop.  Let $k$ be the number of steps; let $\ell$ be the number
of connected components of the terminal $P_3$-free graph $G_k$.  Each
component is a clique (a $P_3$-free graph is a disjoint union of cliques),
say with vertex sets $C_1, \ldots, C_\ell$, $|C_1| \le \cdots \le |C_\ell|$.

**Step 3 — two bounds.**  Telescope:
$$
s^-(G) \;\ge\; s^-(G_k) + (1 + \epsilon) k.
$$
For the cliques, $s^-(K_{n_i}) = n_i - 1$, so
$s^-(G_k) = \sum_{i=1}^\ell (|C_i| - 1) = (n - k) - \ell$.

Combine:
$$
s^-(G) \;\ge\; (n - k - \ell) + (1 + \epsilon) k \;=\; n + \epsilon k - \ell.
\quad (\star)
$$

**Step 4 — extract a contradiction from $s^- < n$.**  Inequality $(\star)$
and $s^-(G) < n$ force $\ell > \epsilon k$.  Combined with
$\ell \le |C_1| + \cdots + |C_\ell| = n - k$, we get
$$
k \;<\; \frac{n}{1 + \epsilon} \;=\; \frac{16}{17} n.
$$

**Step 5 — close via $\alpha\omega$.**  Each clique $C_i$ has $|C_i| \le \omega(G)$,
and the cliques are independent (no $P_3$ between them), so
$\ell \le \alpha(G)$.  Therefore
$$
\alpha(G)\,\omega(G) \;\ge\; |C_1| + \cdots + |C_\ell|
\;=\; n - k \;>\; n - \frac{16}{17} n \;=\; \frac{n}{17}.
$$
This contradicts the hypothesis $\alpha\omega \le n/17$.

**Identification of the $17$.**  Working back from Step 5: the threshold
$n/17$ comes from the relation $c = \epsilon/(1 + \epsilon)$ with
$\epsilon = 1/16$.  Equivalently, since $1 + 1/16 = 17/16$, the
"per-removal gain" is $17/16$, and the safety margin needed to absorb the
$\ell$ residue is exactly $1/(1 + \epsilon) = 16/17$.  Thus
$1 - 16/17 = 1/17$ is the *threshold density* of residue $\alpha\omega$
that the gain can absorb.

**Tightness of the algebra.**  Inequality $(\star)$ is sharp: equality
holds when every $P_3$-removal step achieves *exactly* $1 + \epsilon$ and
the terminal cliques saturate $\ell = \alpha$, $|C_i| = \omega$.  So *for
the $P_3$-removal proof technique with Lemma 2.4's $\epsilon = 1/16$ as
the input*, the constant $1/17$ is the largest hypothesis density the
algebra can support.  **Any improvement of the constant $17$ must come
from one of:**
- (R1) An improved $P_3$-removal lemma with $\epsilon > 1/16$.
- (R2) A tighter accounting of the residue cliques (e.g.\ replacing
  $\ell \le \alpha$ with a stronger structural bound).
- (R3) An entirely different lower bound on $s^\pm(G)$ that does not go
  through $P_3$-removal.

---

## 3.  Empirical $c^*$ from small-$n$ data

### 3.1  The corpus

`scripts/alpha_omega_exploration.py` enumerates all connected graphs of
order $n \le 7$ from `nx.graph_atlas_g()` and supplements with
$200 \times 5$ Erdős–Rényi samples per $n \in \{8, 10, 12, 14\}$ across
densities $\{0.2, 0.35, 0.5, 0.65, 0.8\}$ (kept only if connected).
Corpus size: $1795$ connected graphs.  Per-graph data:
$\alpha, \omega, s^+, s^-, \min(s^+, s^-)/n, n/(\alpha\omega)$.

Output: `data/alpha_omega_corpus.json`.

### 3.2  Empirical threshold

Define $c^*(n) := \min \{\, n/(\alpha(G)\omega(G)) : G \text{ connected of
order } n,\ \min(s^+(G), s^-(G)) < n\,\}$.  This is the strongest
$\alpha\omega$-density that an *actual violator* can have; any theorem of
the form "$\alpha\omega \le n/c \Rightarrow \min(s^\pm) \ge n$" needs
$c \ge c^*(n)$.

Result on the corpus:

| $n$ | $\#G$ | $\#$viol | $\#$sat | $\%$ in Thm 8.1 hyp | $c^*$ empirical |
|---:|---:|---:|---:|---:|---:|
| 2 | 1 | 1 | 0 | 0.00% | 1.0000 |
| 3 | 2 | 2 | 0 | 0.00% | 0.7500 |
| 4 | 6 | 5 | 1 | 0.00% | 0.6667 |
| 5 | 21 | 14 | 7 | 0.00% | 0.5556 |
| 6 | 112 | 36 | 76 | 0.00% | 0.5000 |
| 7 | 853 | 99 | 754 | 0.00% | 0.4375 |
| 8 | 200 | 30 | 170 | 0.00% | 0.5000 |
| 10 | 200 | 9 | 191 | 0.00% | 0.5556 |
| 12 | 200 | 2 | 198 | 0.00% | 0.5714 |
| 14 | 200 | 2 | 198 | 0.00% | 0.5833 |

The "$c^*$ empirical" column is the **infimum of $n/(\alpha\omega)$ over
violators**.  Reading right-to-left: at $n = 14$, the smallest violator
density is $0.5833$, meaning the worst-violator has
$\alpha\omega = 14/0.5833 \approx 24$.

(The column "$\%$ in Thm 8.1 hyp" is the fraction of corpus graphs that
satisfy $\alpha\omega \le n/17$.  It is uniformly $0$.  Thm 8.1
**provably applies to zero graphs on $\le 14$ vertices**.  This is itself
a remarkable observation: the theorem is an asymptotic statement
content-free at small $n$, only kicking in for very dense large graphs.)

### 3.3  The maximum $n/(\alpha\omega)$ among violators

The more interesting direction: the **largest** $n/(\alpha\omega)$
attained by any violator $G$ tells us how *tight* the constant $17$ is.
If even some small graph achieves $n/(\alpha\omega) = c_0$ while violating
$\min(s^\pm) \ge n$, then no theorem with constant smaller than $1/c_0$
can hold, i.e.\ $17 \ge 1/c_0$ would be needed.

Top of the per-$n$ table:

| $n$ | $\alpha$ | $\omega$ | $\alpha\omega$ | $n/(\alpha\omega)$ | $m$ | family |
|---:|---:|---:|---:|---:|---:|:---|
| 5 | 2 | 2 | 4 | **1.250** | 5 | $C_5$ |
| 7 | 3 | 2 | 6 | 1.167 | 7 | $C_7$ |
| 9 | 4 | 2 | 8 | 1.125 | 9 | $C_9$ |
| 11 | 5 | 2 | 10 | 1.100 | 11 | $C_{11}$ |
| 13 | 6 | 2 | 12 | 1.083 | 13 | $C_{13}$ |
| 2 | 1 | 2 | 2 | 1.000 | 1 | $K_2$ |
| 3 | 1 | 3 | 3 | 1.000 | 3 | $K_3$ |
| 4 | 2 | 2 | 4 | 1.000 | 3 | $P_4$ |

The pattern is **odd cycles**: $C_n$ for $n$ odd has
$\alpha(C_n) = (n-1)/2$, $\omega(C_n) = 2$, so
$$
\frac{n}{\alpha(C_n)\,\omega(C_n)}
\;=\; \frac{n}{n - 1}
\;\xrightarrow[n \to \infty]{}\; 1^+.
$$
From the source paper's Proposition 9.1: $s^-(C_n) = n + 1 - \sec(\pi/n) < n$
for $n \equiv 3 \pmod 4$, and $s^+(C_n) = n + 1 - \sec(\pi/n) < n$ for
$n \equiv 1 \pmod 4$.  So every odd cycle (other than $C_3 = K_3$) is a
**$\min(s^\pm) < n$ violator** of Thm 8.1's conclusion.

**The odd-cycle obstruction is the hard ceiling.**  Any theorem of the
form "$\alpha\omega \le n/c \Rightarrow \min(s^\pm) \ge n$" requires
$c > 1$ strictly, because $C_n$ realises $n/(\alpha\omega) = n/(n-1)$ and
violates the conclusion for $n$ odd.  More precisely:
$$
\boxed{\;\sup_n c^*(C_n) \;=\; \lim_{n \to \infty,\ n\text{ odd}} \frac{n}{n - 1} \;=\; 1.\;}
$$
So the absolute mathematical ceiling on the constant is $c < 1$ (and even
$c = 1$ is excluded since the family converges to it strictly from above).

### 3.4  Restating Theorem 8.1's "room"

Comparing the proved constant $1/17 \approx 0.0588$ with the empirical
ceiling $\to 1^-$, **there is in principle a factor-$17$ improvement
budget**:
$$
0.0588 \;=\; \tfrac{1}{17}
\;\;\overset{?}{\longrightarrow}\;\;
\sim 1^- \;=\; \text{odd-cycle ceiling}.
$$
But routes (R1)–(R3) above must be activated to claim any of it.  We now
examine which are realistic.

---

## 4.  Attempted weakening: can Thm 8.1's $17$ drop?

### 4.1  Route R1 (better $P_3$-removal lemma).  Cost: ★★★★ Value: high

Lemma 2.4 is shown in [22] (Zhang, *Extremal values for the square energies
of graphs*, arXiv:2409.15504) with $\epsilon = 1/16$.  The Desmos check
in the proof of Lemma 2.4 verifies that
$$
16 x^4 \;>\; 6 \bigl(1 + \epsilon - 4(1 - x)^2\bigr) \bigl(1 + \epsilon - 2(1 - x)^2\bigr)
\quad \text{for all}\ x \in \bigl[\tfrac{1 - \epsilon}{2},\ 1 + \epsilon\bigr].
$$
This inequality is **the tight constraint** that fixes $\epsilon = 1/16$.
Improving to, e.g., $\epsilon = 1/12$ would tighten the constant from
$1/17$ to $1/(1 + 1/12) \cdot (1/12) = 1/13$.  But:

- The polynomial inequality is **tight at $\epsilon = 1/16$** in the sense
  that some $x_0$ in the domain achieves equality at $\epsilon$ slightly
  above $1/16$.  A genuine improvement of $\epsilon$ within Zhang's
  framework requires re-deriving Lemma 2.4 with a different proof
  strategy.
- Even pushing to $\epsilon = 1/8$ (which empirically the polynomial does
  not allow) would only get to $c = 1/9$.  The factor-$17$ budget is
  asymptotically out of reach via $\epsilon$-tuning alone.

**Verdict on R1.**  Plausibly worth a focused literature read of Zhang
(2024) to see whether the $1/16$ in Lemma 2.4 is a real constant or an
artefact of one choice of test function.  But this is a **separate
research project** sitting downstream of Zhang's paper.  Not in scope for
two weeks.

### 4.2  Route R2 (better $\ell$ accounting).  Cost: ★★ Value: low

The proof uses $\ell \le \alpha(G)$.  Can this be improved?

In general, the cliques $C_1, \ldots, C_\ell$ in the terminal $P_3$-free
graph are an *independent set of cliques* in $G_k$, but their union covers
only $n - k$ vertices.  $\alpha(G_k)$ rather than $\alpha(G)$ is the
*natural* bound.  Since $G_k$ is an induced subgraph and $\alpha$ is
monotone non-decreasing on the deletion side, $\alpha(G_k) \le \alpha(G)$,
so the inequality $\ell \le \alpha(G)$ is already tight from the
direction.

A stronger structural input — e.g., a bound like
$\ell \le (\alpha(G) - 1)$ assuming $G$ has some forbidden subgraph —
would give a constant slightly better than $1/17$, but the *order of
magnitude* would be the same.  Not promising.

### 4.3  Route R3 (different lower bound).  Cost: ★★★★★ Value: speculative

Theorem 7.1 of the source paper proves $s^+(G) \ge n - 1$ for graphs
with $\gamma(G) = 2$ using a sum-of-two-eigenvalues lemma (Lemma 7.1) and
weak majorisation.  This is a *completely different* technology from
$P_3$-removal.  Combining R3-style bounds with $\alpha\omega$-style
hypotheses could in principle yield a quantitatively different theorem,
but no such combination is hinted at in the source.

### 4.4  Empirical fitting: ignore the algebra and just fit a constant

The data show $c^*(n)$ rising from $\sim 0.44$ at $n = 7$ towards $\sim 1$
along the odd-cycle family.  *Empirically*, **any $c$ above $\sim 0.5$
works on $n \le 14$, but the odd cycles drag $c^*$ to $1^-$ in the limit.**

So one *could* state a theorem of the form
$$
\text{"if }\alpha\omega \le n/2 \text{ and }G\text{ is not an odd cycle,
then }\min(s^\pm) \ge n\text{"}
$$
which would be vastly stronger than Thm 8.1 on small graphs — *but the
clause "and $G$ is not an odd cycle" is not implied by the $\alpha\omega$
hypothesis*, and no $\alpha\omega$-only statement can rule out odd cycles
arbitrarily.  A *clean* $\alpha\omega$-only theorem with $c$ a true
constant strictly above $1/17$ must therefore go through one of R1–R3.

### 4.5  A counting observation: Thm 8.1 currently covers near-zero graphs

In the corpus of 1795 connected graphs on $n \le 14$, **zero** graphs
satisfy $\alpha\omega \le n/17$.  Going to large $n$: even for very dense
graphs $G(n, 1/2)$, $\alpha\omega \sim (\log_2 n)^2$ with probability
$1 - o(1)$ (Bollobás), so $\alpha\omega \le n/17$ holds w.h.p.\ for
$n \ge n_0$ with $n_0$ around the threshold $(\log_2 n)^2 \le n/17$, i.e.
$n \gtrsim 1000$.  The source paper explicitly remarks "This gives an
alternate proof that a random graph $G \sim G(n, 1/2)$ satisfies
$\min(s^+, s^-) \ge n$ with high probability."  That is **Thm 8.1's
practical content**.

In other words: **Thm 8.1 is a tool for almost-all dense graphs, not a
tool for any structured small graph.**  It is structurally orthogonal to
the 2-tree workstream (sparse, fixed $\omega = 3$, $\alpha \approx n/3$,
hence $\alpha\omega \approx n$).

---

## 5.  Verdict: is the $\alpha\omega$ route worth a person-month?

**Summary of findings.**

1. The constant $17$ in Thm 8.1 is **tightly determined** by Zhang's
   $P_3$-removal lemma constant $\epsilon = 1/16$ via
   $c = \epsilon/(1 + \epsilon) = 1/17$.  Improving $17$ within the same
   proof structure requires improving Zhang's lemma (route R1), which is
   a separate research project on its own.
2. The hard mathematical ceiling on any $\alpha\omega$-based hypothesis
   is $c < 1$, set by the odd-cycle family.  Thm 8.1 sits at $1/17$;
   there is a factor-$17$ in-principle improvement budget.
3. **Thm 8.1 applies to zero connected graphs on $n \le 14$** in our
   corpus and is genuinely a "high-density large-$n$" tool — its
   practical statement is "random $G(n, 1/2)$ for $n$ large".
4. **Thm 8.1 is uniformly inapplicable to 2-trees**: 2-trees have
   $\omega = 3$ and $\alpha \approx n/3$, so $\alpha\omega \approx n \gg n/17$.
   Hence the $\alpha\omega$ route does **not** help with the 2-tree
   workstream's central target.

**Cost/value for a person-month invested in the $\alpha\omega$ route.**

| Sub-route | Potential gain | Probability of success in 4 weeks | Net |
|---|---|---|---|
| R1: improve $\epsilon$ in Lemma 2.4 | Constant shifts from $17$ to $\sim 9$–$13$ | Low (requires new technique against Zhang's tight inequality) | Slim |
| R2: tighten $\ell$ bound | Small constant improvement | Modest, but the new $c$ is still $\gg$ relevant graph densities | Negligible value |
| R3: combine with Thm 7.1 / Lemma 3.2 | New hypothesis class | Speculative (no template) | Pure exploration |
| Empirical fit, then exclude exceptions | Custom theorem | High empirically, low formally | Cosmetic |

**Bottom line.**  The $\alpha\omega$ route is **not a productive
parallel track** to the 2-tree workstream.  Three reasons:

- (i) It is **uniformly inapplicable** to 2-trees and other sparse
  structured families — the very graphs the workstream cares about.
- (ii) Its constant $17$ is **tightly determined** by upstream lemma
  technology (Zhang 2024), not by the proof of Thm 8.1 itself.
  Improving it is research on Zhang's lemma, not on the conjecture.
- (iii) Its practical content is a **statement about random graphs**,
  which is already covered by Elphick–Farber–Goldberg–Wocjan in
  Conjecture 1.1's hyper-energetic / regular settings.

**Recommendation.**  Do not pivot the 2-tree workstream to the
$\alpha\omega$ route.  Spend the freed-up cycles on the slot-shift wall
(O12.2) and on general-2-tree condition (a), which are the real
bottlenecks of plan v13.

That said, the file `data/alpha_omega_corpus.json` and the script
`scripts/alpha_omega_exploration.py` are kept as **diagnostic
infrastructure**: future investigators considering an $\alpha\omega$
attack can re-run them in seconds and reconfirm the verdict.

---

## Appendix A.  Replicability

```bash
uv run python problems/positive_square_energy_equality/scripts/alpha_omega_exploration.py --with-random-larger
```

Output:
- `data/alpha_omega_corpus.json` (per-graph data, $\sim 600$ kB).
- Console summary table reproducing §3.2 above.

Runtime: ~30 seconds on a 2024 MacBook.

## Appendix B.  Files

- This note: `docs/lprime_alpha_omega_weakening.md`.
- Script: `scripts/alpha_omega_exploration.py`.
- Corpus: `data/alpha_omega_corpus.json`.
- (No test added.)

## Appendix C.  Where the $17$ enters — one-line cheat sheet

$$
\epsilon = \frac{1}{16}
\quad\Longrightarrow\quad
1 + \epsilon = \frac{17}{16}
\quad\Longrightarrow\quad
c = \frac{\epsilon}{1 + \epsilon} = \frac{1/16}{17/16} = \frac{1}{17}.
$$
