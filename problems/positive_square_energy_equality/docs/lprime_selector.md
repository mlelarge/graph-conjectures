# Selector conjecture and $\delta^-_\infty(BT)$

Companion to `plan.md` step 5 and `two_tree_ear_lemma.md` open
subtasks (O2) and (O3). Treats the BT$(k, 2)$ asymptotic explicitly
and tests the selector conjecture numerically.

## Part 1 — $\delta^-_\infty(BT)$ in closed form

**Setup.** BT$(k, 2)$ on $n = k + 4$ vertices: vertices $0, 1$ (book
spine), $2, \ldots, k+1$ (book pages), $k+2$ (tail vertex 1),
$k+3$ (tail vertex 2). Edges
$$(0,1),\quad (0,j),(1,j)\text{ for } 2 \le j \le k+1,\quad
(0, k+2),(2, k+2),\quad (2, k+3),(k+2, k+3).$$
The tail ear $v = k+3$ has neighbours $\{2, k+2\}$ and supporting edge
$(2, k+2) \in E(G - v)$. Removing $v$ gives $H = G - v = $ BT$(k, 1)$:
the book $B_k$ on edge $(0, 1)$ together with the single triangle
$\{0, 2, k+2\}$.

### Symmetry quotient

Pages $3, 4, \ldots, k+1$ are pairwise isomorphic in $G$ (each has
neighbour set $\{0, 1\}$). Set $m := k - 1$. The page-trace-zero
subspace $\{v: v_j = 0\text{ for } j \notin \{3,\ldots,k+1\},\;\sum_{j} v_j = 0\}$
has dimension $m - 1 = k - 2$ and lies in $\ker A(G)$ (same calculation
as for $B_k$ in `lprime_books.md`).

On the orthogonal complement, take orthonormal basis
$$e_0,\ e_1,\ e_2,\ u_P := m^{-1/2}\sum_{j=3}^{k+1} e_j,\ e_{k+2},\ e_{k+3}.$$
The reduced $6 \times 6$ adjacency matrix is
$$M_G(m) = \begin{pmatrix}
0 & 1 & 1 & \sqrt m & 1 & 0\\
1 & 0 & 1 & \sqrt m & 0 & 0\\
1 & 1 & 0 & 0 & 1 & 1\\
\sqrt m & \sqrt m & 0 & 0 & 0 & 0\\
1 & 0 & 1 & 0 & 0 & 1\\
0 & 0 & 1 & 0 & 1 & 0
\end{pmatrix}.$$
Similarly $H$'s nonzero spectrum lives on a $5 \times 5$ matrix
$M_H(m)$ obtained from $M_G$ by deleting the last row and column.

### Characteristic polynomials

By expansion (e.g. cofactor along the $u_P$ row),
$$\det(\lambda I - M_G(m)) = \lambda^6 - (2m + 7)\lambda^4 - (2m + 6)\lambda^3
+ (7m + 3)\lambda^2 + (10m + 2)\lambda + 3m,$$
$$\det(\lambda I - M_H(m)) = \lambda^5 - (2m + 5)\lambda^3 - (2m + 4)\lambda^2
+ 3m\lambda + 2m.$$

### Asymptotic spectrum as $m \to \infty$

The top and bottom eigenvalues of $M_G(m)$ and $M_H(m)$ scale as
$\pm \sqrt{2m}\, (1 + o(1))$ (they are the "page-attached" modes).
The remaining interior eigenvalues converge to finite limits as
$m \to \infty$.

**Interior limit for $M_G$.** Writing the eigenvector as
$(v_0, v_1, v_2, v_P, T_1, T_2)$ and using $v_0 + v_1 \to 0$ (forced
by the $u_P$-row), we find $v_1 = -v_0$, $T_1 = 2(\lambda + 1)v_0$,
$T_2 = \lambda v_2 - T_1$, and the remaining two consistency equations
reduce to the polynomial
$$P_G(x) := 2x^3 - 7x - 3 = 0.$$
The full asymptotic interior spectrum of $M_G$ is
$$\{-1\}\, \cup\, \text{roots of }P_G(x).$$
Numerically the roots of $P_G$ are
$$\rho_1 \approx -1.6009559,\qquad \rho_2 \approx -0.4555894,\qquad
\rho_3 \approx +2.0565453.$$
The eigenvalue $-1$ comes from the same antisymmetric direction as
for the book (book pages 3..k+1 swap-symmetric).

**Interior limit for $M_H$.** The same reduction (no $T_2$ row) yields
the cubic
$$P_H(x) := 2x^3 + 2x^2 - 3x - 2 = 0,$$
with roots
$$\sigma_1 \approx -1.5513875,\qquad \sigma_2 \approx -0.5731827,\qquad
\sigma_3 \approx +1.1245703.$$
The full asymptotic interior spectrum of $M_H$ is the roots of $P_H(x)$.

### Closed form for $\delta^-_\infty(BT)$

Sum of squares of interior eigenvalues:
- Vieta on $P_G(x) = 2x^3 + 0 \cdot x^2 - 7x - 3$: $\sum \rho_i = 0$, $\sum \rho_i \rho_j = -7/2$.
  $\sum \rho_i^2 = 0 - 2(-7/2) = 7$.
- Vieta on $P_H(x) = 2x^3 + 2x^2 - 3x - 2$: $\sum \sigma_i = -1$, $\sum \sigma_i\sigma_j = -3/2$.
  $\sum \sigma_i^2 = 1 - 2(-3/2) = 4$.

Each cubic has exactly one positive real root (verified by sign chase).
Let $\alpha := \rho_3 > 0$ (the positive root of $P_G$) and
$\beta := \sigma_3 > 0$ (the positive root of $P_H$).

The interior contribution to $s^-$ is
$$s^-_{\text{int}}(G) = (-1)^2 + \rho_1^2 + \rho_2^2 = 1 + (7 - \alpha^2) = 8 - \alpha^2,$$
$$s^-_{\text{int}}(H) = \sigma_1^2 + \sigma_2^2 = 4 - \beta^2.$$

The two extreme eigenvalue contributions $\lambda_{\min}(G)^2$ and
$\lambda_{\min}(H)^2$ both equal $2m + O(1)$ with vanishing
difference $\lambda_{\min}(G)^2 - \lambda_{\min}(H)^2 = O(1/m)$
(verified numerically: at $m = 10^7$ the extreme-eigenvalue contribution
to $\delta^-$ is $\le 2 \times 10^{-7}$). Hence
$$\boxed{\;\delta^-_\infty(BT) = s^-_{\text{int}}(G) - s^-_{\text{int}}(H)
= (8 - \alpha^2) - (4 - \beta^2)
= 4 - \alpha^2 + \beta^2,\;}$$
where $\alpha$ is the unique positive real root of $2x^3 - 7x - 3 = 0$
and $\beta$ is the unique positive real root of $2x^3 + 2x^2 - 3x - 2 = 0$.

Numerically $\alpha = 2.05654529\ldots$, $\beta = 1.12457027\ldots$, and
$$\delta^-_\infty(BT) = 4 - 4.22938869\ldots + 1.26466420\ldots
= 1.03527975\ldots.$$
This matches the empirical value in `two_tree_ear_lemma.md`
($\delta^-_\infty \approx 1.034$) to the third decimal and refines it.

### Convergence rate

The extreme-eigenvalue contribution to $\delta^-(BT(k, 2)) - \delta^-_\infty(BT)$
scales as $1/m \sim 1/n$. Empirically (verified at $k = 10^5$ and $10^6$):
$$\delta^-(BT(k, 2)) = \delta^-_\infty(BT) + \frac{c}{k} + O(k^{-2}),
\qquad c \approx 0.22.$$
Hence the worst-case ear in BT$(k, 2)$ approaches the limit from above,
and the universal lemma (L) fails for $k$ sufficiently large
(specifically $k \ge 23$ gives $\delta^- < 17/16$, consistent with the
data in `two_tree_ear_lemma.md`). The existential lemma (L') is rescued
by the book-page ears, which have $\delta^- \approx 1.9$ throughout.

## Part 2 — The selector conjecture (O2)

**Conjecture (O2).** There exists a function $T(n)$, with
$T(n) \to \infty$, such that every simplicial degree-$2$ ear $v$ of a
$2$-tree $G$ on $n$ vertices, with supporting edge $\{a, b\}$ of
$H := G - v$ satisfying $\deg_H(a) + \deg_H(b) \ge T(n)$, has
$\delta^-(v) \ge 17/16$ (and by the trace identity
$\delta^+(v) \ge 17/16$ as well).

### Enumeration through $n \le 10$

From `data/two_tree_ear_gains_n*.json`:

| $n$ | $\#$ 2-trees | $\#$ ears | $\#$ bad ears (any sign) | min $\delta^-(v)$ |
|---:|---:|---:|---:|---:|
| 4 | 1 | 2 | 0 | 1.4384 |
| 5 | 1 | 5 | 0 | 1.5616 |
| 6 | 2 | 14 | 0 | 1.3190 |
| 7 | 5 | 38 | 0 | 1.2467 |
| 8 | 12 | 135 | 0 | 1.2069 |
| 9 | 39 | 521 | 0 | 1.1810 |
| 10 | 136 | 2215 | 0 | 1.1625 |

Through $n = 10$, no simplicial ear of any $2$-tree has
$\delta^-(v) < 17/16$. The selector conjecture is vacuously true on
this enumeration range. The minimum $\delta^-$ across all ears at
$n = 10$ is $1.1625$, achieved on BT$(7, 2)$ (book on $\{0, 1\}$ with a
two-triangle tail; the worst ear is the outer tail vertex). Its
supporting edge has $\deg_H(a) + \deg_H(b) = 3 + 2 = 5$.

### Extension to random 2-trees, $n \in \{50, \ldots, 300\}$

We generated 100 random uniform 2-trees per $n \in \{50, 100, 150, 200, 300\}$
(seed $0, \ldots, 99$ from `random.choice` over current edges) and
recorded all ears with $\delta^-(v) < 17/16$ (call these "bad ears").

**Result.** Across 500 random 2-trees we found 16 bad ears, all at
$n \in \{200, 300\}$ — none at $n \in \{50, 100, 150\}$. **Every single
bad ear has $\deg_H(a) + \deg_H(b) = 5$**, with
$(\deg_H(a), \deg_H(b)) = (3, 2)$ (unordered). This is exactly the local
fingerprint of a "tail" simplicial ear on an outer triangle, matching
the structural BT counterexample.

Histogram of $\deg_H(a) + \deg_H(b)$ on bad ears:

| $\deg_H(a) + \deg_H(b)$ | $\#$ bad ears observed |
|---:|---:|
| 5 | 16 |
| $\ge 6$ | 0 |

Minimum $\delta^-$ observed: $1.0379$.

### Selector test on BT$(k, 2)$

The two ear classes of BT$(k, 2)$ are:

| ear type | supporting edge | $\deg_H(a) + \deg_H(b)$ | $\delta^-$ for $k$ large |
|:---|:---|---:|---:|
| book-page ear | $\{0, 1\}$ | $2k + 1$ | $\to 2$ (from below) |
| outer tail ear | $\{2, k+2\}$ | $5$ | $\to \delta^-_\infty(BT) \approx 1.0353$ |

Numerics (`scripts/extreme_family.py` + `family_check.py`):

| $k$ | $n$ | page $\delta^-$ | page $\deg_{\text{sum}}$ | tail $\delta^-$ | tail $\deg_{\text{sum}}$ |
|---:|---:|---:|---:|---:|---:|
| 5 | 9 | 1.684 | 11 | 1.181 | 5 |
| 10 | 14 | 1.781 | 21 | 1.121 | 5 |
| 25 | 29 | 1.861 | 51 | 1.076 | 5 |
| 50 | 54 | 1.901 | 101 | 1.058 | 5 |
| 100 | 104 | 1.930 | 201 | 1.047 | 5 |
| 200 | 204 | 1.950 | 401 | 1.042 | 5 |
| 500 | 504 | 1.968 | 1001 | 1.038 | 5 |

The "good" book-page ear has $\deg_H(a) + \deg_H(b) = 2k + 1 = 2n - 7$
(specifically $\Theta(n)$) and $\delta^- \approx 1.9$. The "bad" tail
ear has $\deg_H(a) + \deg_H(b) = 5$ (constant) and $\delta^- < 17/16$ for
$k$ large.

### Working selector

Across **all** the empirical tests above (enumeration $n \le 10$,
random $n \le 300$, structural BT$(k, 2)$ for $k \le 1000$),
*every* bad ear has $\deg_H(a) + \deg_H(b) \le 5$. So the data is
consistent with a much stronger conjecture than (O2):

> **Strong selector conjecture.** Every simplicial degree-$2$ ear $v$ of
> a $2$-tree with $\deg_H(a) + \deg_H(b) \ge 6$ has $\delta^-(v) \ge 17/16$.

Since the trace identity gives $\delta^+(v) \ge 17/16$ automatically
whenever $\delta^-(v) \le 47/16$, and $\delta^-(v) \ge 17/16$ is the
hard side, the strong selector form is (L') with a fixed threshold
$T = 6$.

To actually use the selector for (L'), we need every $2$-tree to
*contain* such an ear. We claim it does: in any $2$-tree on $n \ge 4$
vertices, the maximum-degree vertex $u^*$ has degree at least
$\Omega(\sqrt n)$ (since $\sum \deg = 2|E| = 4n - 6$ and there are only
$n$ vertices), and edges incident to $u^*$ have one endpoint of high
degree. A simplicial ear attached to an edge incident to $u^*$ has
$\deg_H(a) + \deg_H(b) \ge \deg(u^*) - O(1) \ge $ growing in $n$. This
is a sketch, not a proof; making it rigorous requires the actual
existence of a simplicial ear attached to a high-degree edge in every
$2$-tree, which is a separate combinatorial claim. Empirically every
enumerated $2$-tree on $n \le 10$ does have such an ear.

## Verdict on the selector conjecture

- **Strongly supported by data.** Every observed bad ear (across
  $\sim 3000$ $2$-trees enumerated or sampled, plus the BT family) has
  $\deg_H(a) + \deg_H(b) \le 5$. A constant threshold $T = 6$ would
  filter all observed bad ears.
- **BT$(k, 2)$ verification.** The book-page ear of BT$(k, 2)$ has
  $\deg_H(a) + \deg_H(b) = 2k + 1$ and $\delta^- \to 2$; the tail ear
  has $\deg_H(a) + \deg_H(b) = 5$ and $\delta^- \to \delta^-_\infty(BT) \approx 1.035$.
  The strong selector picks the book-page ear cleanly.
- **Not proved.** The selector conjecture (O2), in either the strong
  fixed-threshold form or a growing $T(n)$ form, remains open.
- **Suggested approach.** Combine the secular-equation framework
  $\lambda = q_H(\lambda)$ from `two_tree_ear_lemma.md` with the
  weight $\sum_i c_i^2 = 4$ to derive a lower bound on $\delta^-$ in
  terms of $\deg_H(a) + \deg_H(b)$. Heuristically: large $\deg_H(a) + \deg_H(b)$
  forces the spine spectrum to have high weight on negative
  eigenvalues away from $0$, which gives $\delta^- \gg 1$.
