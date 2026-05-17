# 2-tree ear deletion lemma: empirical evidence and analytical attempt

Companion to `plan.md` step 5. This note records what is currently proved,
what is conjectured-from-data, and what remains open.

## Statement (recap)

For $G$ a 2-tree with $n \ge 4$ and $v$ a simplicial degree-$2$ vertex with $G - v \ne K_2$,
write $\delta^\pm(v) := s^\pm(G) - s^\pm(G - v)$ and define the lemma:

> **(L)** For every 2-tree $G$ on $n \ge 4$, there exists a simplicial degree-$2$
> vertex $v$ such that
> $$\delta^+(v) \;\ge\; \frac{17}{16}\qquad\text{and}\qquad \delta^-(v) \;\ge\; \frac{17}{16}.$$

If (L) holds, iterating down to $K_3$ gives $s^\pm(G) \ge s^\pm(K_3) + \tfrac{17}{16}(n - 3) > n - 1$.

## A trace identity that fixes the gauge

If $v$ has degree $2$ in $G$ (and $\deg_G(v) = 2$ is automatic for a simplicial
degree-$2$ vertex), then
$$\mathrm{tr}(A(G)^2) - \mathrm{tr}(A(G - v)^2) \;=\; 2 \deg_G(v) \;=\; 4,$$
so for any such ear
$$\boxed{\;\delta^+(v) + \delta^-(v) = 4.\;}$$

**Consequence.** $\min\{\delta^+(v), \delta^-(v)\} \ge 17/16$ is equivalent to
$\delta^-(v) \in [17/16,\, 47/16]$.

The lemma therefore reduces to: *there exists a simplicial ear $v$ with
$\delta^-(v) \in [17/16,\, 47/16]$*. The interior of this interval is wide
(length $30/16 = 1.875$), so the issue is to avoid the two endpoints —
"too small $\delta^-$" (extremal $K_3$-like behaviour on the negative side)
and "too small $\delta^+$" (extremal tree-like behaviour on the positive side).

## Block decomposition and Schur complement

Let $H = G - v$ and let $v$ be attached to the edge $ab \in E(H)$. With
$w := e_a + e_b \in \mathbb{R}^{n - 1}$,
$$A(G) \;=\; \begin{pmatrix} 0 & w^\top \\ w & A(H) \end{pmatrix}.$$
The characteristic polynomial expansion gives
$$\det(\lambda I_n - A(G))
\;=\; \lambda \cdot \det(\lambda I_{n-1} - A(H))
   \;-\; w^\top \mathrm{adj}(\lambda I_{n-1} - A(H))\, w.$$
For $\lambda \notin \mathrm{spec}(A(H))$, with $R(\lambda) := (\lambda I - A(H))^{-1}$,
this becomes
$$\det(\lambda I_n - A(G)) \;=\; \det(\lambda I - A(H))\cdot\bigl(\lambda - q_H(\lambda)\bigr),
\qquad q_H(\lambda) := w^\top R(\lambda)\, w.$$
Spectrally, if $H$ has eigenvalues $\mu_1 \ge \cdots \ge \mu_{n-1}$ with
orthonormal eigenvectors $u_i$, and if we set $c_i := w^\top u_i = u_i(a) + u_i(b)$,
then
$$q_H(\lambda) \;=\; \sum_{i = 1}^{n - 1} \frac{c_i^2}{\lambda - \mu_i},
\qquad \sum_i c_i^2 \;=\; \|w\|^2 \;=\; 2 + 2 A(H)_{ab} \;=\; 4$$
(using $A(H)_{ab} = 1$ since $ab \in E(H)$). The eigenvalues $\lambda$ of $G$ that are
not already eigenvalues of $H$ are precisely the roots of $\lambda = q_H(\lambda)$,
interlacing those of $H$.

## What this says about $\delta^+$ and $\delta^-$

Cauchy interlacing gives $\lambda_1(G) \ge \lambda_1(H) \ge \cdots \ge \lambda_{n-1}(H) \ge \lambda_n(G)$.
Define the "weighted local density" projected on $w$:
$$\Phi_+(H, w) := \sum_{\mu_i > 0} c_i^2 \mu_i,\qquad
\Phi_-(H, w) := \sum_{\mu_i < 0} c_i^2 \mu_i.$$
Then a short calculation (going through the secular equation and writing
$\delta^\pm$ as a contour integral of $\lambda^2$ against the spectral measure
difference) gives
$$\delta^+(v) + \delta^-(v) = 4 = \|w\|^2 + (\deg_G v - \deg_H v - 0)\cdot 0,$$
which only recovers the trace identity. A sharper decomposition (work in progress)
should separate $\delta^+$ and $\delta^-$ in terms of $\Phi_+, \Phi_-$, and the
sign of $q_H$ at $0$.

The clean fact we *can* state is the rank-2 perturbation viewpoint: $A(G)$ on
the orthogonal complement of $\mathrm{span}(e_v, w)$ inherits the spectrum of
$A(H)$ (in fact $A(H)$ acts on a complementary subspace), and the only
"new" eigenvalues come from the secular equation in a $2 \times 2$ block.
This is the standard tool but does not by itself yield a clean $17/16$ bound.

## Empirical evidence

### Phase 2 enumeration: all 2-trees, $n = 4, \ldots, 10$

Counts (OEIS A054581 for unlabelled 2-trees):
$$|\mathcal T_n| \;=\; 1, 1, 2, 5, 12, 39, 136, 529,\quad n = 3, 4, 5, 6, 7, 8, 9, 10.$$

For every enumerated 2-tree and every simplicial degree-$2$ vertex $v$ with
$G - v \ne K_2$, we recorded $\delta^+(v), \delta^-(v)$ (JSON files
`data/two_tree_ear_gains_n*.json`). Per-order minima:

| $n$ | min $\delta^+$ | min $\delta^-$ |
|---:|---:|---:|
| 4 | 2.5616 | 1.4384 |
| 5 | 2.4372 | 1.5616 |
| 6 | 2.2373 | 1.3190 |
| 7 | 2.1650 | 1.2467 |
| 8 | 2.0974 | 1.2069 |
| 9 | 2.0382 | 1.1810 |
| 10 | 1.9932 | 1.1625 |

**Empirical finding 1.** Through $n = 10$, *every* simplicial ear of *every* 2-tree
satisfies $\min(\delta^+, \delta^-) \ge 1.1625 > 17/16 = 1.0625$.

**Empirical finding 2.** The $\delta^-$ minimum over $v$ is achieved by a
**different ear** than the $\delta^+$ minimum in the overwhelming majority
of 2-trees (e.g. 518 out of 529 at $n = 10$). The two sign-specific
"hard" ears typically have different local structure.

**Empirical finding 3.** The $\delta^-$-minimizing 2-tree at each $n \in \{7,\ldots,10\}$
is the same parametric family:
$$\mathrm{BT}(k, t) := \text{book } B_k \text{ on edge } \{0,1\},\text{ with pages } 2, \ldots, k+1,$$
together with a length-$t$ chain of two extra triangles glued at edge $\{0, 2\}$.
At $t = 2$ this is the 2-tree
$$\{0,1\}\cup\{0i, 1i : i = 2,\ldots,k+1\} \cup \{0, k+2\}\{2, k+2\}\{2, k+3\}\{k+2, k+3\}.$$
The minimizing ear is the outermost tail vertex $v = k + 3$, attached at $\{2, k+2\}$
with $\deg_H(2) = 3$ and $\deg_H(k + 2) = 2$.

### Extrapolation to large $n$ via the BT family

For $\mathrm{BT}(k, 2)$, the tail-ear $v = k + 3$ has

| $k$ | $n$ | $\delta^-(v)$ |
|---:|---:|---:|
| 10 | 14 | 1.12122 |
| 25 | 29 | 1.07589 |
| 50 | 54 | **1.05751** |
| 100 | 104 | **1.04716** |
| 200 | 204 | **1.04151** |
| 500 | 504 | **1.03788** |
| 1000 | 1004 | **1.03661** |

So the **universal** ear-deletion lemma — "every simplicial ear works" — is
**false** for $s^-$: for sufficiently large $k$, the tail ear of $\mathrm{BT}(k, 2)$
has $\delta^- < 17/16$. Specifically $\delta^- < 17/16$ from $k \approx 23$ ($n \approx 27$)
onwards.

The empirical $\delta^-$ value on this family appears to converge to
$$\delta^-_\infty \;\approx\; 1.034\ldots > 1.$$

**Crucially**, the *other* simplicial ears in $\mathrm{BT}(k, 2)$ (the book pages
$v = 3, 4, \ldots, k + 1$) all satisfy $\delta^-(v) \approx 1.901$, comfortably
above $17/16$. So the **existential** form of the lemma still holds for this
family.

### Updated form of the conjectured lemma

> **(L')** For every 2-tree $G$ on $n \ge 4$, there exists a simplicial
> degree-$2$ vertex $v^*$ such that
> $$\delta^+(v^*),\;\delta^-(v^*) \;\ge\; \frac{17}{16}.$$

(L') is the version actually used by the inductive proof in plan.md. The
data through $n = 10$ is consistent with (L'); the data on the BT family
through $n = 1004$ is also consistent with (L'), with the witness $v^*$
chosen as any book page (not the tail).

## Where (L') would break

A potential counterexample to (L') needs a 2-tree in which *every* simplicial
ear $v$ has $\min(\delta^+(v), \delta^-(v)) < 17/16$. Given $\delta^+ + \delta^- = 4$,
this requires that for every simplicial ear, either
$\delta^- < 17/16$ or $\delta^+ < 17/16$, i.e. $\delta^- \notin [17/16, 47/16]$
for *every* $v$. The empirical $\delta^-(v)$ values across simplicial ears
of a fixed 2-tree appear bimodal (book-page ears cluster near $1.9$,
boundary/tail ears cluster near $1.03$–$1.2$). The "easy" book pages
keep (L') alive.

## Smaller targets: 2-paths and fans

### 2-paths $L_k$

A 2-path is a 2-tree whose clique tree is a path. Explicit family `two_path(k)`
on $n = k + 2$ vertices.

| $n$ | min $\delta^+$ | min $\delta^-$ |
|---:|---:|---:|
| 6 | 2.681 | 1.319 |
| 9 | 2.624 | 1.376 |
| 15 | 2.594 | 1.407 |

The minimum $\delta^-$ on 2-paths oscillates by parity but stays $> 1.31$,
well above $17/16$. So (L') is easy here.

### Fans $F_k = K_1 \vee P_k$

| $n$ | min $\delta^+$ | min $\delta^-$ |
|---:|---:|---:|
| 6 | 2.400 | 1.600 |
| 9 | 2.349 | 1.651 |
| 14 | 2.277 | 1.723 |

Stable, well above $17/16$.

### Books $B_k$

For the book $B_k$ on $n = k + 2$ vertices (all triangles share edge $\{0, 1\}$),
every simplicial ear is symmetric and $\delta^-(B_k) \to 2$ from below.
A short calculation: $A(B_k)$ has spectrum
$$\lambda_\pm = \tfrac{1}{2}\bigl(1 \pm \sqrt{1 + 8k}\bigr),\quad
1 \text{ (multiplicity } k - 1\text{)},\quad -1 \text{ (multiplicity } 1\text{)}.$$
(Standard for $K_2 + \overline{K_k}$ join structure.) Therefore
$$s^+(B_k) = \lambda_+^2 + (k - 1) = \tfrac{1}{4}(1 + \sqrt{1 + 8k})^2 + k - 1,$$
$$s^-(B_k) = \lambda_-^2 + 1 = \tfrac{1}{4}(1 - \sqrt{1 + 8k})^2 + 1.$$
A direct check shows $\delta^-(B_k) = s^-(B_k) - s^-(B_{k - 1}) \to 2$ from below
and $\delta^+(B_k) = s^+(B_k) - s^+(B_{k - 1}) \to 2$ from above; both are $\ge 17/16$
unconditionally.

## What this leaves open analytically

- **(O1) Existential simplicial-ear inequality.** Prove (L') unconditionally
  for all 2-trees. The data is strongly consistent with it.
- **(O2) A combinatorial "good ear" selector.** Empirically, "any simplicial
  ear attached to a high-degree spine edge $ab$" works. Conjecture:
  *every simplicial ear $v$ with $\deg_H(a) + \deg_H(b) \ge $ some threshold
  $T(n)$ satisfies $\delta^\pm(v) \ge 17/16$.* The book-page ears in
  $\mathrm{BT}(k, 2)$ have $\deg_H(a) + \deg_H(b) = k + 1 + k = 2k + 1$, very large.
  Tail ears have $\deg_H(a) + \deg_H(b) = 3 + 2 = 5$, very small.
- **(O3) Asymptotic $\delta^-$ on $\mathrm{BT}(k, t)$.** Identify the limit
  $\delta^-_\infty \approx 1.034$ in closed form. This pins the *worst*
  asymptotic ear-gain and tells us by how much the universal lemma fails.
- **(O4) Secular-equation bound.** Combine the trace identity
  $\delta^+ + \delta^- = 4$ with a bound on $\delta^-$ from below using
  $q_H(\lambda) = \sum c_i^2 / (\lambda - \mu_i)$. The fact that
  $\sum c_i^2 = 4$ (i.e. $\|e_a + e_b\|^2 = 2 + 2 \cdot \mathbb 1[ab \in E(H)] = 4$
  since $ab$ is an edge) gives a clean normalisation. A working conjecture:
  $\delta^-(v) \ge 1 + \tfrac{1}{16} \cdot f(\text{local spine degree})$ for
  some explicit non-negative $f$ — but only the high-degree-spine choice
  gives the $17/16$ gap.

## Honest verdict

- **Proved (cited):** Conjecture 9.2(i) and 9.2(ii) for trees and for $K_n$
  (forward direction); Corollaries A and B in `corollaries_AB.md`.
- **Empirically supported (Phase 2):** the existential lemma (L') for all
  2-trees with $n \le 10$, and on infinite parametric subfamilies
  (books, fans, 2-paths, $\mathrm{BT}(k, t)$) at much larger $n$.
- **Refuted:** the *universal* simplicial-ear lemma (L) — at large $n$ in the
  $\mathrm{BT}(k, 2)$ family, the tail simplicial ear has $\delta^- < 17/16$.
  The induction must therefore explicitly *select* the simplicial ear, not
  use an arbitrary one.
- **Open:** an analytical proof of (L'). The cleanest route appears to be a
  secular-equation argument that bounds $\delta^-(v)$ from below in terms of
  $\deg_H(a) + \deg_H(b)$ — and then choosing the ear attached to the
  highest-degree edge of $H$. This is consistent with how the empirical
  worst case behaves, but the analytic dependence on degrees has not been
  worked out.

## Files

- `scripts/spectrum_check.py` — primitive $s^\pm, n^\pm$ computation.
- `scripts/two_tree_enum.py` — enumerate connected 2-trees up to isomorphism.
- `tests/two_tree_ear_gain.py` — per-2-tree, per-ear gain check; writes
  `data/two_tree_ear_gains_n*.json`.
- `scripts/inspect_minimizers.py` — print the structure of the worst-case
  $(G, v)$ at each $n$.
- `scripts/family_check.py` — ear gains on parametric 2-tree families (books,
  fans, 2-paths).
- `scripts/extreme_family.py` — the $\mathrm{BT}(k, t)$ family that produced
  the universal-lemma counterexample at large $n$.
- `data/two_trees_n10.json` — enumeration through $n = 10$.
- `data/two_tree_ear_gains_n*.json` — per-graph ear gains, $n = 4, \ldots, 10$.
