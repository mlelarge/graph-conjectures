# EC-log lemma: a publication-quality proof

Role: Probabilistic / cut-counting theorist
Round 1 deliverable for the Bang-Jensen–Yeo good-decomposition attack.
Date: 2026-05-16.

Citations to: Karger, *Minimum Cuts in Near-Linear Time*, J. ACM 47 (2000), 46–76 (arXiv:cs/9812007); cautionary mention of Cen–Li–Nanongkai–Saranurak, FOCS 2021 (arXiv:2111.08959), used only in §4 when discussing the directed analogue.

---

## 1. Statement

Throughout this note a **digraph** $D = (V, A)$ may have multiple arcs but no loops, and $n := |V|$. We write $\delta_D^+(X) = \{uv \in A : u \in X, v \notin X\}$ for the out-cut of $X$, and $\delta_D^-(X) = \delta_D^+(V\setminus X)$ for the in-cut. The **arc-strong connectivity** is
$$\lambda(D) \;:=\; \min_{\emptyset \neq X \subsetneq V} |\delta_D^+(X)|.$$
$D$ is called **Eulerian** if $d_D^+(v) = d_D^-(v)$ for every $v \in V$. A **strong arc decomposition** of $D$ is a partition $A = A_1 \mathbin{\dot\cup} A_2$ such that both spanning subdigraphs $(V, A_1)$ and $(V, A_2)$ are strongly connected; equivalently, every directed cut $\delta_D^+(X)$, $\emptyset \neq X \subsetneq V$, contains at least one arc of each color.

> **Lemma (EC-log).** Let $C = 6$ and $n_0 = 3$. Every Eulerian digraph $D$ on $n \ge n_0$ vertices with
> $$\lambda(D) \;\ge\; C \log_2 n$$
> has a strong arc decomposition.

> **Edit note (2026-05-18).** The original v4 headline of this document
> read "$C = 5$, $n_0 = 2$." That choice was inconsistent with the
> arithmetic of §2.5: the inequality $5\log_2 n > 4\log_2 n + 3$ requires
> $\log_2 n > 3$, i.e. $n \ge 9$, not $n \ge 4$ as previously stated. To
> keep the headline honest with the proof actually written below, the
> constant is raised to $C' = 6$, for which the same proof works
> uniformly down to $n = 3$ (see §2.5 for the verification: $6\log_2 n >
> 4\log_2 n + 3 \Leftrightarrow \log_2 n > 3/2 \Leftrightarrow n \ge 3$).
> The $n = 2$ case is degenerate under the simple-digraph convention and
> is no longer claimed; it is briefly noted in §2.6. See the project
> audit `CORRECTNESS_REVIEW_2026_05_18.md` §2.5 for the original flag.

We comment on $C$ in §3; the proof in §2 is written with a generic $C$ and the inequality is forced only at the end.

---

## 2. Proof

### 2.1 Reduction to undirected min-cut

Let $G = (V, E)$ be the **underlying undirected multigraph** of $D$: replace each arc $uv$ by an undirected edge $\{u, v\}$, keeping multiplicities. Parallel edges therefore arise both from parallel arcs in $D$ and from anti-parallel pairs $uv$, $vu$.

**Step 1. Cut balance.** Since $D$ is Eulerian, summing $d^+(v) = d^-(v)$ over $v \in X$ yields, after cancelling internal arcs of $D[X]$,
$$|\delta_D^+(X)| \;=\; |\delta_D^-(X)|, \qquad \emptyset \neq X \subsetneq V. \tag{1}$$

**Step 2. Undirected degree.** Each arc of $D$ contributes one edge to $G$, and an arc $uv$ with $u \in X$, $v \notin X$ contributes to $\delta_G(X)$ regardless of orientation. Hence
$$d_G(X) \;=\; |\delta_D^+(X)| + |\delta_D^-(X)| \;\stackrel{(1)}{=}\; 2\,|\delta_D^+(X)|. \tag{2}$$

In particular the undirected edge-connectivity of $G$ is
$$\lambda_G \;:=\; \min_{\emptyset \neq X \subsetneq V} d_G(X) \;=\; 2\,\lambda(D). \tag{3}$$

**Step 3. Cut correspondence (with explicit two-to-one factor).** The directed cuts of $D$ are indexed by *ordered* nonempty proper subsets $X \subsetneq V$, of which there are $2^n - 2$. The undirected cuts of $G$ are indexed by *unordered* partitions $\{X, V\setminus X\}$, of which there are $(2^n - 2)/2 = 2^{n-1} - 1$. Each unordered cut $\{X, V\setminus X\}$ corresponds to exactly two directed cuts:
$$\delta_D^+(X) \quad\text{and}\quad \delta_D^+(V\setminus X) \;=\; \delta_D^-(X),$$
and by (1) these two directed cuts have the **same size**. So
$$\#\{X \subsetneq V \text{ nonempty} : |\delta_D^+(X)| = s\} \;=\; 2 \cdot \#\{\{X, V\setminus X\} : |\delta_G(X)| = 2s\}. \tag{4}$$

We will carry this factor of 2 explicitly through the union bound.

### 2.2 Random 2-coloring and per-cut bound

Color each arc of $D$ independently red or blue, each with probability $1/2$. A directed cut $\delta_D^+(X)$ of size $s$ is monochromatic iff all $s$ of its arcs receive the same color. By independence,
$$\Pr[\delta_D^+(X) \text{ monochromatic}] \;=\; 2 \cdot 2^{-s} \;=\; 2^{1-s}. \tag{5}$$

Call a directed cut **bad** if it is monochromatic. Existence of a strong arc decomposition is equivalent to the existence of a coloring with no bad directed cut, and we will show that, with $\lambda := \lambda(D) \ge C\log_2 n$, the expected number of bad directed cuts is $< 1$.

### 2.3 Karger's undirected cut-counting bound

We use Karger's theorem in the following standard form.

> **Theorem (Karger 2000).** Let $G$ be an undirected multigraph on $n$ vertices with minimum cut $\lambda_G$. For every real $\alpha \ge 1$, the number of distinct undirected cuts (i.e. vertex-bipartitions $\{X, V\setminus X\}$) of size at most $\alpha \lambda_G$ is at most $n^{2\alpha}$.

Reference: D. R. Karger, *Minimum Cuts in Near-Linear Time*, J. ACM 47 (2000), 46–76, Theorem 4.1 / Corollary 2.4; see also arXiv:cs/9812007. The constant in the bound is sharp up to lower-order factors via the random contraction algorithm; the only form we need is the polynomial $n^{2\alpha}$.

Two remarks. First, Karger's theorem holds for multigraphs as stated (the contraction-algorithm proof never required simplicity). Second, the bound counts **unordered** cuts, exactly the objects on the right side of (4). The factor of 2 in (4) is therefore not absorbed by Karger; it must be paid separately, as flagged in §1 of `review.md` v2.

### 2.4 Band decomposition

Set $\lambda := \lambda(D)$, so by (3) the undirected min-cut is $\lambda_G = 2\lambda$. Partition the bad-event sum by the size of the directed cut. For $j \ge 1$ define the *band*
$$B_j \;:=\; \{X \subsetneq V \text{ nonempty proper} : j\lambda \le |\delta_D^+(X)| < (j+1)\lambda\}.$$

By (2), $X \in B_j$ iff $2j\lambda \le d_G(X) < 2(j+1)\lambda$, i.e. iff the underlying undirected cut has size in $[j\lambda_G, (j+1)\lambda_G)$. The number of *unordered* undirected cuts of size $< (j+1)\lambda_G$ is, by Karger's theorem with $\alpha = j+1$, at most $n^{2(j+1)}$. By (4) the number of *directed* members of $B_j$ is therefore at most
$$|B_j| \;\le\; 2\, n^{2(j+1)}. \tag{6}$$

Every $X$ in $B_j$ has $|\delta_D^+(X)| \ge j\lambda$, hence
$$\Pr[\delta_D^+(X) \text{ monochromatic}] \;\le\; 2^{1 - j\lambda}. \tag{7}$$

### 2.5 Union bound and geometric series

Let $N$ be the number of bad directed cuts. Since $\lambda(D) = \lambda$, every $X$ belongs to some $B_j$ with $j \ge 1$, so
$$\mathbb{E}[N] \;=\; \sum_{X} \Pr[\delta_D^+(X) \text{ mono}] \;\le\; \sum_{j \ge 1} |B_j| \cdot 2^{1 - j\lambda} \;\stackrel{(6),(7)}{\le}\; \sum_{j \ge 1} 2 n^{2(j+1)} \cdot 2^{1 - j\lambda}. \tag{8}$$

Factor out the $j=1$ exponent:
$$\mathbb{E}[N] \;\le\; 4 n^{4} \cdot 2^{-\lambda} \cdot \sum_{j \ge 1}\!\Bigl(\frac{n^{2}}{2^{\lambda}}\Bigr)^{j-1}\!. \tag{9}$$

If $\lambda \ge 3 \log_2 n + 1$ (so $n^2 / 2^{\lambda} \le 1/(2n)$, hence $\le 1/4$ for $n \ge 2$), the geometric series sums to at most $4/3 < 2$, and
$$\mathbb{E}[N] \;\le\; 8\, n^4 \cdot 2^{-\lambda}. \tag{10}$$

We need $\mathbb{E}[N] < 1$, i.e. $2^{\lambda} > 8 n^4 = 2^3 \cdot n^4$, i.e.
$$\lambda \;>\; 4 \log_2 n + 3. \tag{11}$$

Both conditions ($\lambda \ge 3\log_2 n + 1$ and $\lambda > 4\log_2 n + 3$) are implied, for $n \ge 3$, by
$$\lambda \;\ge\; 6 \log_2 n, \qquad (n \ge 3). \tag{12}$$

**Arithmetic verification of (12).** We show that $C = 6$ implies both gating conditions used above — namely (G1) $\lambda \ge 3\log_2 n + 1$ (used in the geometric-series bound just above (10)) and (G2) the inequality $\lambda > 4\log_2 n + 3$ from (11) — for every integer $n \ge 3$.

*Gating condition (G1).* $6\log_2 n \ge 3\log_2 n + 1 \Leftrightarrow 3\log_2 n \ge 1 \Leftrightarrow \log_2 n \ge 1/3 \Leftrightarrow n \ge 2^{1/3} \approx 1.26$. Hence (G1) holds for every $n \ge 2$, in particular for $n \ge 3$.

*Gating condition (G2) = (11).* $6\log_2 n > 4\log_2 n + 3 \Leftrightarrow 2\log_2 n > 3 \Leftrightarrow \log_2 n > 3/2 \Leftrightarrow n > 2^{3/2} = 2\sqrt 2 \approx 2.828$. Hence (G2) holds for every integer $n \ge 3$.

Both gating conditions are therefore satisfied at $C = 6$ for every $n \ge 3$, with the binding constraint coming from (G2) at $n = 3$ (where $6\log_2 3 \approx 9.51$ vs. $4\log_2 3 + 3 \approx 9.34$, leaving $\approx 0.17$ of slack on the real line; in integers, $\lambda \ge \lceil 6\log_2 3 \rceil = 10$ and (11) demands $\lambda \ge 10$ — exactly tight at the integer level).

**Remark on the previous $C = 5$ headline.** The earlier version of this
document asserted that (11) and (G1) are implied for $n \ge 2$ by $\lambda
\ge 5\log_2 n$; that assertion is false. The relevant inequality
$5\log_2 n > 4\log_2 n + 3$ rearranges to $\log_2 n > 3$, i.e. $n \ge 9$.
Concretely, at $n = 4$ the bound (11) requires $\lambda > 4\log_2 4 + 3
= 11$ (integer $\lambda \ge 12$), but $\lceil 5\log_2 4\rceil = 10 < 12$;
similarly for $n \in \{5,6,7,8\}$ the integer ceiling $\lceil 5\log_2
n\rceil$ falls short of $4\log_2 n + 3 + 1$. Raising the constant to $C
= 6$ removes this gap uniformly down to $n = 3$ at the cost of a small
constant inflation, which is anyway dominated by the bound's looseness
(§5).

### 2.6 First-moment conclusion

By (12) and (11), for $\lambda(D) \ge 6\log_2 n$ and $n \ge 3$ we have $\mathbb{E}[N] < 1$. Hence there exists a 2-coloring of $A(D)$ with $N = 0$, i.e. no monochromatic directed cut. By the working equivalence (§1 of `attack_plan.md`), this is a strong arc decomposition.

The case $n = 2$ is degenerate and not in scope of the lemma's headline. (Under the loop-free multigraph convention of §1, a 2-vertex Eulerian digraph is some number of anti-parallel pairs; any such $D$ with $\lambda(D) \ge 2$ trivially has a SAD by partitioning the parallel arcs equally between the two color classes. But the lemma's hypothesis $\lambda(D) \ge 6\log_2 2 = 6$ is non-trivial only as a multigraph statement, and we leave it absorbed into the small-case folklore rather than into the lemma headline. Hence $n_0 = 3$.)

No alteration step is needed: the first-moment method directly furnishes the coloring. This corrects the `attack_plan.md` v3 outline, which mentioned a redundant "union-bound / alteration finish".

$\square$

---

## 3. Constants

### 3.1 Where the constants come from

The argument balances:

- the factor of 2 from the directed↔undirected two-to-one correspondence (4);
- the per-cut bound $2^{1-s}$, where the leading 2 also comes from "red-mono OR blue-mono";
- the Karger bound $n^{2(j+1)}$ for $j$-th band, with the $+1$ in the exponent because we count cuts of size **up to** $(j+1)\lambda_G$ (the band ends one $\lambda_G$ above $j\lambda_G$);
- the geometric series in $n^2 / 2^\lambda$.

Tightening any of these is local. The dominant term is $n^{2(j+1)} \cdot 2^{1-j\lambda}$ at $j = 1$, which gives roughly $n^4 \cdot 2^{-\lambda}$. So $\lambda > 4 \log_2 n$ is the asymptotically right threshold, and $C \to 4^+$ is the limit of this argument. Any $C$ strictly greater than 4 works for all sufficiently large $n$; we use $C = 6$ as the headline because the binding inequality (11) requires $\log_2 n > 3/(C-4)$, which at $C = 6$ gives $n \ge 3$ (the smallest range that covers all non-trivial vertex counts) but at $C = 5$ would give only $n \ge 9$. The constant $C = 5$ remains valid asymptotically and is the smallest integer that survives the limit $C \to 4^+$, but it does not cover the full $n \ge 3$ regime under the same proof, so we drop it from the headline.

### 3.2 Table of required $\lambda$

The bound from (10) requires $2^\lambda \ge 8 n^4$ (so $\mathbb{E}[N] \le 1$; for $\mathbb{E}[N] < 1$ we need strict inequality, hence $\lceil 4\log_2 n + 3 \rceil + 1$ below).

| $n$ | $4\log_2 n + 3$ | smallest integer $\lambda$ s.t. $2^\lambda > 8 n^4$ | $C=5$: $\lceil 5\log_2 n\rceil$ (sufficient?) | $C=6$ (headline): $\lceil 6\log_2 n\rceil$ |
|---:|---:|---:|---:|---:|
| 3    | 9.34  | 10 | 8  (**NO**) | 10 |
| 4    | 11.00 | 12 | 10 (**NO**) | 12 |
| 5    | 12.29 | 13 | 12 (**NO**) | 14 |
| 6    | 13.34 | 14 | 13 (**NO**) | 16 |
| 7    | 14.23 | 15 | 15 (OK) | 17 |
| 8    | 15.00 | 16 | 15 (**NO**) | 18 |
| 9    | 15.68 | 16 | 16 (OK) | 20 |
| 10   | 16.29 | 17 | 17 (OK) | 20 |
| 20   | 20.29 | 21 | 22 (OK) | 26 |
| 50   | 25.58 | 26 | 29 (OK) | 34 |
| 100  | 29.58 | 30 | 34 (OK) | 40 |
| 1000 | 42.86 | 43 | 50 (OK) | 60 |

The "sufficient?" column shows whether $\lceil C\log_2 n\rceil$ is $\ge$ the smallest integer $\lambda$ satisfying (11). For $C = 5$ this column is NO at $n \in \{3, 4, 5, 6, 8\}$: $C = 5$ does *not* uniformly cover small $n$, contradicting the original headline "$C = 5$, $n_0 = 2$." From $n = 9$ onward the slack is non-negative integer-wise, but the irregular pattern at $n \in \{3, \dots, 10\}$ (caused by the integer ceilings $\lceil 5\log_2 n\rceil$ oscillating relative to $\lceil 4\log_2 n + 3 + \epsilon\rceil$) is why the original headline failed. This is the bookkeeping defect the audit `CORRECTNESS_REVIEW_2026_05_18.md` §2.5 surfaced. For $C = 6$ the column is OK uniformly from $n = 3$ onward, by the §2.5 verification above; the slack grows like $2\log_2 n - 3 - O(1)$ and is $\ge 4$ from $n = 20$ on.

The headline therefore uses $C = 6$, $n_0 = 3$. The asymptotic threshold $\lambda > 4\log_2 n + 3$ is unchanged; only the integer headline constant is affected.

The constants are not the point of the lemma; we record them here only to support the write-up and to anchor the comparison in §5.

---

## 4. Where the argument fails to generalize

For each relaxation below, we identify the specific step that breaks.

### (a) Drop Eulerianness

The reduction (2) used $|\delta^+(X)| = |\delta^-(X)|$. Without it, all we have for a $\lambda$-arc-strong $D$ is
$$d_G(X) \;=\; |\delta^+(X)| + |\delta^-(X)| \;\ge\; 2\lambda, \tag{13}$$
which gives $\lambda_G \ge 2\lambda$. **The lower bound $\lambda_G \ge 2\lambda$ is enough for Karger's cut count to apply to $G$**, and (5) is still true with $s = |\delta^+(X)|$. What is destroyed is the *equality* $d_G(X) = 2|\delta^+(X)|$, hence the band correspondence. A directed cut of size $s$ now sits inside an undirected cut of size $s + s'$, where $s' = |\delta^-(X)| \in [\lambda, \infty)$ is uncontrolled.

Concretely, the band $B_j$ should now be replaced by the set of $X$ with $|\delta^+(X)| \in [j\lambda, (j+1)\lambda)$ *regardless of $|\delta^-(X)|$*. Karger's bound counts undirected cuts by total size $d_G(X) = s + s'$, but $s'$ can be arbitrarily large, so the number of $X$ with $|\delta^+(X)| \in [j\lambda, (j+1)\lambda)$ is **not** controlled by counting undirected cuts up to size $(j+1)\lambda_G$. There is no useful upper bound of the form $n^{2\alpha}$.

Status: **probably hard by this method**. Karger gives no useful bound on the number of directed cuts of size $\le \alpha \lambda(D)$ in a general digraph — that is precisely what Cen–Li–Nanongkai–Saranurak (FOCS 2021, arXiv:2111.08959) attack via partial sparsification, but their bound is for *minimum* directed cuts and is not yet of the form $n^{O(\alpha)}$. A near-min directed cut count of that strength would be a research-level result in its own right.

### (b) Replace $\log n$ by a constant

The expected number of bad cuts in band $j$ is bounded by $2 n^{2(j+1)} \cdot 2^{1-j\lambda}$. For this to be $< 1/j^2$ (so that the sum is $< 1$) one needs $j\lambda \ge 2(j+1)\log_2 n + O(\log j)$. The $\log_2 n$ on the right cannot be eliminated by any reweighting of bands while we use Karger's bound $n^{2\alpha}$, because that bound already has $n^{2\alpha}$ many cuts of size $\le \alpha \lambda_G$ — i.e. polynomially many even when $\alpha = 1$.

Worse: $n^{2\alpha}$ is asymptotically tight (cycles, low-connectivity Cayley graphs), so no "better Karger" will save us. To replace $\log_2 n$ by a constant via this argument one would need an alternative that exploits *Eulerianness beyond just $\lambda_G = 2\lambda$* — for instance, a much tighter count of "directed-realizable" undirected cuts, or a structural argument bypassing the union bound entirely.

Status: **open / probably hard**. This is the Phase 5(a) target in `attack_plan.md` v3 and is openly flagged as a high-risk extension. No first-moment / LLL refinement of EC-log can deliver it because the union bound over $\Theta(n^4)$ near-min cuts already eats the entire $C \log n$ budget.

### (c) Bounded-defect Eulerianness: $\bigl|\,|\delta^+(X)| - |\delta^-(X)|\,\bigr| \le f(\lambda)$

Now $d_G(X) = 2|\delta^+(X)| + \epsilon(X)$ with $|\epsilon(X)| \le f(\lambda)$. So
$$d_G(X) \in [2|\delta^+(X)| - f(\lambda),\; 2|\delta^+(X)| + f(\lambda)].$$

The band correspondence still works approximately: a directed cut of size $s$ has undirected size in $[2s - f(\lambda), 2s + f(\lambda)]$. Suppose $f(\lambda) \le \lambda/2$. Then for $s \in [j\lambda, (j+1)\lambda)$ we get $d_G(X) \in [2j\lambda - \lambda/2, 2(j+1)\lambda + \lambda/2] \subseteq [(2j - 1/2)\lambda, (2j+5/2)\lambda)$. The undirected min-cut is now bounded by $\lambda_G \ge 2\lambda - f(\lambda) \ge 3\lambda/2$; relative cut-size $\alpha$ for the undirected cut is at most $(2j+5/2)\lambda / (3\lambda/2) = (4j+5)/3$, so Karger's bound becomes $n^{2(4j+5)/3}$. The exponent at $j=1$ is $6$ instead of $4$, the geometric ratio is $n^{8/3} / 2^\lambda$, and the same argument goes through with a worse but still $\Theta(\log n)$ threshold (constant inflated by $4/3$ ish).

More precisely, if $f(\lambda) = \rho\,\lambda$ for some constant $\rho < 1$, the argument generalizes with a worse constant $C(\rho)$ tending to infinity as $\rho \to 1$. If $f(\lambda) = O(\lambda^{1-\epsilon})$, the constant $C$ degrades only by additive $o(1)$ and the lemma is essentially unchanged in regime.

Status: **tractable, with quantitative degradation**. A clean writeup of bounded-defect EC-log is a reasonable Phase 5(b) deliverable: it is the natural bridge from Eulerian to mildly-non-Eulerian inputs, and the proof above already does the load-bearing work.

Summary table:

| Relaxation | Verdict | Reason |
|---|---|---|
| (a) drop Eulerianness | probably hard | Karger no longer constrains directed cut counts |
| (b) replace $\log n$ by constant | probably hard | Karger's $n^{2\alpha}$ count is asymptotically tight |
| (c) $\|\delta^+\| - \|\delta^-\|\| \le \rho\lambda$ for $\rho < 1$ | tractable | same proof, constants degraded by factor $\le 1/(1-\rho)$ |

---

## 5. Sanity check on a small case

Take $D$ to be the **directed 4-cycle with all arcs doubled**: $V = \mathbb{Z}/4$, arcs $\{(i, i+1) \times 2 : i \in \mathbb{Z}/4\}$. Then $D$ is Eulerian (each vertex has $d^+ = d^- = 2$), and the arc-strong connectivity is
$$\lambda(D) \;=\; \min_X |\delta_D^+(X)| \;=\; 2,$$
attained for every "arc" $X = \{i, i+1, \dots, j\}$ along the cycle. The underlying undirected graph $G$ is the 4-cycle with each edge of multiplicity 2; its min-cut is $\lambda_G = 4 = 2\lambda(D)$, as predicted by (3).

There are $2^4 - 2 = 14$ ordered nonempty proper $X$, hence $7$ unordered cuts. Directly:

- 4 cuts of type "single vertex": $|\delta_G| = 4$, hence $|\delta_D^+(X)| = 2$.
- 2 cuts of type "antipodal pair" $\{0,2\}, \{1,3\}$: $|\delta_G| = 8$, hence $|\delta_D^+(X)| = 4$.
- 4 cuts of type "consecutive pair" $\{i, i+1\}$: $|\delta_G| = 4$, hence $|\delta_D^+(X)| = 2$.

(That's 4 + 2 + 4 = 10 ordered single-side $X$, but wait — antipodal-pair cuts are self-paired under complement: $\{0,2\}^c = \{1,3\}$, while single-vertex $\{i\}$ and three-vertex $\{i\}^c$ are different ordered $X$ but the same unordered cut. So total unordered = 4 (singletons) / 2 (paired with complements) + ... let me re-do: unordered cuts are $\{\{i\}, \text{rest}\}$ for $i \in \{0,1,2,3\}$ → 4 cuts; $\{\{i,i+1\}, \text{rest}\}$ for $i \in \{0,1,2,3\}$ → 4 cuts; $\{\{0,2\}, \{1,3\}\}$ → 1 cut; total $9$? Re-count: there are $(2^4 - 2)/2 = 7$ unordered cuts, so I am over-counting. The fix: $\{\{i, i+1\}, \text{rest}\}$ and $\{\text{rest}, \{i,i+1\}\}$ are the *same* unordered cut, so the 4 consecutive-pair ordered $X$ pair up into 2 unordered cuts. Total: $2 + 2 + 1 = $ no — singletons pair with their three-vertex complements ($i$ vs $\{0,1,2,3\}\setminus\{i\}$), so 4 ordered singletons → 4 unordered cuts (since each singleton's complement is the unique three-set containing the other three vertices, and these are *different* unordered cuts unless I conflate them — actually $\{\{0\},\{1,2,3\}\}$ and $\{\{1\},\{0,2,3\}\}$ are different unordered cuts). So 4 (singletons) + 2 (consecutive pairs, paired with their complement which is the *other* consecutive pair: $\{0,1\}^c = \{2,3\}$, both consecutive!) + 1 (antipodal) = 7. ✓)

So the cut sizes are: directed-cut size $|\delta_D^+(X)|$ takes value $2$ on $4 + 4 = 8$ ordered $X$ (singletons and consecutive pairs and their complements: $4 + 4 + 4 = 12$ ordered, half by complementation → 8? let me just list) — for clarity, the 14 ordered nonempty proper $X$ split as

- 8 of directed-cut-size 2 (the four singletons, their three-set complements, and the four consecutive pairs which are self-complementary in pairs);
- 2 of directed-cut-size 4 (the two antipodal pairs).

Wait — $\{0,1\}^c = \{2,3\}$, which is also consecutive, so the four consecutive pairs *are* all 4 of them as ordered $X$; their unordered cuts are $\{\{0,1\},\{2,3\}\}$ and $\{\{1,2\},\{3,0\}\}$, only 2 unordered cuts. The directed-cut size of $X = \{0,1\}$ in $D$ is: arcs leaving $\{0,1\}$ are $(1,2) \times 2$ → size 2. Yes, size 2. So:

- singletons: 4 ordered, size 2 each;
- three-sets: 4 ordered (complements of singletons), size 2 each ($|\delta^+(V\setminus\{i\})| = $ arcs leaving $V\setminus\{i\}$ = arcs entering $\{i\}$ = 2);
- consecutive pairs: 4 ordered, size 2 each;
- antipodal pairs: 2 ordered, size 4 each.

Total: $4 + 4 + 4 + 2 = 14$ ✓; sum of sizes $= 4\cdot 2 + 4\cdot 2 + 4\cdot 2 + 2\cdot 4 = 32 = 2|A(D)|$ ✓.

Now apply our bound. Here $\lambda = 2$, $\lambda_G = 4$, $n = 4$. Our union bound (8) gives
$$\mathbb{E}[N] \;\le\; \sum_j 2 \cdot 4^{2(j+1)} \cdot 2^{1 - 2j}.$$
At $j = 1$: $2 \cdot 4^4 \cdot 2^{-1} = 256$. The actual expectation is $\sum_X 2^{1-|\delta^+(X)|} = 12 \cdot 2^{-1} + 2 \cdot 2^{-3} = 6 + 0.25 = 6.25$. So our bound overshoots by about $256/6.25 \approx 41$. That is the expected looseness — the geometric series and Karger upper bound are both extremely loose at $n = 4$, $\lambda = 2$.

Of course $\lambda(D) = 2$ is far below the $6\log_2 4 = 12$ that EC-log (with the corrected headline $C = 6$) requires, so the lemma promises nothing here, but a direct check shows that $D$ does have a strong arc decomposition: color one copy of each doubled arc red, the other blue; each color class is a directed 4-cycle, which is strong. The sanity ledger:

| quantity | value at $D$ = doubled $\vec C_4$ |
|---|---|
| $n$ | 4 |
| $\lambda(D)$ | 2 |
| $\lambda_G$ | 4 |
| # directed cuts | 14 |
| $\mathbb{E}[N]$ exact | 6.25 |
| our union bound (8) at $j=1$ | 256 |
| EC-log promises decomposition? | no ($6\log_2 4 = 12 > 2$) |
| does it actually decompose? | yes (split doubled arcs) |

The looseness factor $\sim 40$ at $n = 4$ is consistent with the bound's $n^{2(j+1)}/2^{j\lambda} \cdot \text{(true number of cuts)}^{-1}$ scaling, which is benign for the asymptotic argument.

---

## Appendix: redirections to the team

- The factor of 2 in (4) is the bookkeeping flag from `review.md` §"Major remaining issue 2" / Phase-1 punch-list item 1. It is paid here and only here; downstream code does not need to worry about it.
- The "no alteration finish" point (review punch-list item 2) is observed in §2.6.
- Constants in §3 are deliberately conservative; tightening them is not the bottleneck.
- The boundary work for §4(c) is the natural Phase 5(b) starting point and the proof in §2 ports almost verbatim with $\lambda_G \ge (2 - \rho)\lambda$ and a degraded Karger exponent.
- The sanity check in §5 is a ledger for the coder building the ILP/SAT verifier (Phase 2): on the doubled $\vec C_4$, both the ILP and the SAT model should return SAT, and the explicit certificate "split each doubled arc" is the simplest possible regression test.
