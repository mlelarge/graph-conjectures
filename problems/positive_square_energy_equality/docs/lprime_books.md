# (L') on books $B_k$ — closed-form proof

Companion to `plan.md` step 5 and `two_tree_ear_lemma.md`. Proves
(L') unconditionally on the book family.

## Statement

For every $k \ge 2$ and every simplicial degree-2 ear $v$ of the book
$B_k$ on $n = k + 2$ vertices,
$$\min\bigl(\delta^+(v), \delta^-(v)\bigr) \;\ge\; 17/16 \;=\; 1.0625.$$
Equivalently $\delta^-(v) \in [17/16,\, 47/16]$.

In closed form
$$\boxed{\;\delta^-(B_k) \;=\; 2 - \frac{4}{\sqrt{8k+1}+\sqrt{8k-7}},
\qquad
\delta^+(B_k) \;=\; 2 + \frac{4}{\sqrt{8k+1}+\sqrt{8k-7}}.\;}$$
Both are $\ge 17/16$ for all $k \ge 2$, and they bracket $2$ with
$\delta^-(B_k) \uparrow 2$ and $\delta^+(B_k) \downarrow 2$ as $k \to \infty$.

## Setup

$B_k = K_{1,1,k}$: vertices $a, b, v_1, \ldots, v_k$ with $a \sim b$,
$a \sim v_i$, $b \sim v_i$, $v_i \not\sim v_j$.
All page vertices $v_i$ are pairwise isomorphic and simplicial of degree
$2$; deleting any one of them gives $B_{k-1}$. We may therefore identify
$\delta^\pm(v) = s^\pm(B_k) - s^\pm(B_{k-1})$ once $k \ge 2$.

## Step 1: spectrum of $A(B_k)$

Decompose $\mathbb{R}^{n}$ into three $A$-invariant subspaces using the
automorphism group of $B_k$ (which contains the symmetric group $S_k$
permuting the pages, and the involution swapping $a \leftrightarrow b$).

1. **$(a - b)$-antisymmetric direction.** Span of $(e_a - e_b)/\sqrt 2$:
   on this $1$-dim subspace,
   $A(e_a - e_b) = (e_b + \sum_i e_{v_i}) - (e_a + \sum_i e_{v_i}) = -(e_a - e_b)$,
   so eigenvalue $-1$ with multiplicity $1$.

2. **Page-trace-zero subspace.** $\{v : v_a = v_b = 0,\; \sum_i v_{v_i} = 0\}$,
   dimension $k - 1$. For any such $v$, the $a$- and $b$-components of $Av$
   are both $\sum_i v_{v_i} = 0$, and the $v_j$-component of $Av$ is
   $v_a + v_b = 0$. Thus $Av = 0$, giving eigenvalue $0$ with multiplicity
   $k - 1$.

3. **$(a+b)$-symmetric, $\{v_i\}$-symmetric block.** Orthonormal basis
   $u_{ab} := (e_a + e_b)/\sqrt 2$, $u_P := k^{-1/2}\sum_i e_{v_i}$.
   Direct computation:
   - $A(e_a + e_b) = (e_a + e_b) + 2\sum_i e_{v_i}$, so
     $A u_{ab} = u_{ab} + \sqrt{2k}\, u_P$.
   - $A\sum_i e_{v_i} = k(e_a + e_b)$, so
     $A u_P = \sqrt{2k}\, u_{ab}$.

   The reduced matrix is
   $$\tilde M = \begin{pmatrix} 1 & \sqrt{2k} \\ \sqrt{2k} & 0 \end{pmatrix},$$
   with characteristic polynomial $\lambda^2 - \lambda - 2k = 0$ and roots
   $\lambda_\pm = \tfrac{1 \pm \sqrt{1 + 8k}}{2}$.

Collecting,
$$\mathrm{spec}(A(B_k)) = \left\{ \tfrac{1 + \sqrt{1+8k}}{2},\ -1,\ 0^{(k-1)},\ \tfrac{1 - \sqrt{1+8k}}{2}\right\}.$$
Total $1 + 1 + (k-1) + 1 = k + 2 = n$ eigenvalues. ✓

## Step 2: closed form for $s^\pm(B_k)$

With $\lambda_+ = \tfrac{1 + \sqrt{1+8k}}{2} > 0$ and
$\lambda_- = \tfrac{1 - \sqrt{1+8k}}{2} < 0$:
$$s^+(B_k) = \lambda_+^2,\qquad s^-(B_k) = \lambda_-^2 + 1.$$
Expanding,
$$\lambda_\pm^2 = \frac{1 \pm 2\sqrt{1+8k} + (1+8k)}{4} = \frac{2 + 8k \pm 2\sqrt{1+8k}}{4}
= 2k + \frac{1}{2} \pm \frac{\sqrt{1+8k}}{2}.$$
Hence
$$s^+(B_k) = 2k + \frac{1}{2} + \frac{\sqrt{1+8k}}{2},\qquad
  s^-(B_k) = 2k + \frac{3}{2} - \frac{\sqrt{1+8k}}{2}.$$

Sanity check at $k = 5$: $s^-(B_5) = 10 + 1.5 - \sqrt{41}/2 = 8.29844\ldots$,
matching `np.linalg.eigvalsh` on $B_5$ to twelve decimals.

## Step 3: $\delta^\pm(B_k)$

Replacing $k$ by $k - 1$ and subtracting,
$$\delta^-(B_k) = s^-(B_k) - s^-(B_{k-1})
= 2 - \frac{\sqrt{8k+1} - \sqrt{8k-7}}{2}.$$
Rationalising the difference of square roots,
$$\sqrt{8k+1} - \sqrt{8k-7} = \frac{(8k+1)-(8k-7)}{\sqrt{8k+1}+\sqrt{8k-7}}
= \frac{8}{\sqrt{8k+1}+\sqrt{8k-7}},$$
so
$$\boxed{\;\delta^-(B_k) = 2 - \frac{4}{\sqrt{8k+1}+\sqrt{8k-7}}.\;}$$
The trace identity $\delta^+(B_k) + \delta^-(B_k) = 4$ gives
$$\delta^+(B_k) = 2 + \frac{4}{\sqrt{8k+1}+\sqrt{8k-7}}.$$

## Step 4: monotonicity and the $17/16$ bound

**Boundary case $k = 2$.** Rationalising,
$$\frac{4}{\sqrt{17}+3} \cdot \frac{\sqrt{17}-3}{\sqrt{17}-3}
= \frac{4(\sqrt{17}-3)}{17-9} = \frac{\sqrt{17}-3}{2},$$
so
$$\delta^-(B_2) = 2 - \frac{\sqrt{17}-3}{2} = \frac{7 - \sqrt{17}}{2}
\;\approx\; 1.43845.$$
This matches `data/two_tree_ear_gains_n4.json` to twelve decimals.

**Monotonicity.** The function
$\phi(k) := \frac{4}{\sqrt{8k+1}+\sqrt{8k-7}}$ has both denominator
terms strictly increasing in $k$, hence $\phi$ is strictly decreasing.
Therefore $\delta^-(B_k) = 2 - \phi(k)$ is strictly increasing in $k$
and $\delta^+(B_k) = 2 + \phi(k)$ is strictly decreasing in $k$. Both
converge to $2$ as $k \to \infty$.

**Quantitative $17/16$ bound.** Since $\delta^-(B_k) \ge \delta^-(B_2) = \tfrac{7-\sqrt{17}}{2}$
for every $k \ge 2$,
$$\min\bigl(\delta^+(B_k), \delta^-(B_k)\bigr)
\;=\; \delta^-(B_k)
\;\ge\; \frac{7 - \sqrt{17}}{2}.$$
We have $\frac{7-\sqrt{17}}{2} > \frac{17}{16}$ iff
$56 - 8\sqrt{17} > 17$ iff $39 > 8\sqrt{17}$ iff $39^2 > 64 \cdot 17$ iff
$1521 > 1088$. ✓ The slack is
$$\frac{7-\sqrt{17}}{2} - \frac{17}{16} = \frac{39 - 8\sqrt{17}}{16}
\;\approx\; 0.376.$$

## Verification

The closed-form $\delta^\pm(B_k)$ is checked against `np.linalg.eigvalsh`
for $k = 2, \ldots, 50$ in `tests/test_lprime_subfamilies.py`. Maximum
observed deviation is $< 10^{-12}$.

## Status of (L') on books

**Proved.** Every simplicial degree-2 ear $v$ of $B_k$ ($k \ge 2$,
$n = k+2 \ge 4$) satisfies
$$\min\bigl(\delta^+(v), \delta^-(v)\bigr)
\;=\; \delta^-(B_k)
\;\ge\; \frac{7 - \sqrt{17}}{2} \;>\; \frac{17}{16}.$$
The bound is tight at $k = 2$.
