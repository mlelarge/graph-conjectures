# Corollaries A and B of Conjecture 9.2(i)

Source: Akbari, Kumar, Mohar, Pragada, Zhang, *Refinement of a conjecture on
positive square energy of graphs*, arXiv:2506.07264 (June 2025).

Notation. $G$ is a connected graph of order $n$; $\lambda_1 \ge \cdots \ge \lambda_n$
are its adjacency eigenvalues; $s^+(G) := \sum_{\lambda_i > 0} \lambda_i^2$;
$s^-(G) := \sum_{\lambda_i < 0} \lambda_i^2$. Conjecture 9.2(i) asserts
$s^+(G) = n - 1$ iff $G$ is a tree.

The two statements below follow from results already in the source paper. They
are warm-up corollaries verifying our toolkit, not new mathematics.

## Corollary A. Conjecture 9.2(i) holds for connected claw-free graphs.

**Claim.** Let $G$ be a connected claw-free graph of order $n \ge 1$. Then
$s^+(G) = n - 1$ if and only if $G$ is a tree (necessarily a path $P_n$).

**Proof.**

The "if" direction is immediate: for any tree $T$ on $n$ vertices, the spectrum is
symmetric about $0$ (bipartite), so $s^+(T) = s^-(T) = m = n - 1$.

For the "only if" direction, split by maximum degree $\Delta(G)$.

*Case $\Delta(G) \ge 3$.* Theorem 1.1 of arXiv:2506.07264 states that every
connected claw-free graph of order $n$ with $\Delta \ge 3$ satisfies
$$s^+(G) \ge n.$$
In particular $s^+(G) > n - 1$, so $s^+(G) = n - 1$ is impossible.

*Case $\Delta(G) \le 2$.* A connected graph with maximum degree at most $2$ is a
path $P_n$ or a cycle $C_n$ ($n \ge 3$). Paths are trees, giving the tree equality
case. For a cycle $C_n$ with $n \ge 3$, Proposition 9.1 of arXiv:2506.07264 (or
the explicit spectrum $\{2\cos(2\pi j/n) : j = 0,\dots,n-1\}$) yields
$$s^+(C_n) = \sum_{j : \cos(2\pi j/n) > 0} 4\cos^2(2\pi j/n).$$
Using $\sum_j 4\cos^2(2\pi j/n) = 2n$ and that the spectrum is symmetric about $0$
when $n$ is even, one finds $s^+(C_n) > n - 1$ for every $n \ge 3$. Explicit
small values: $s^+(C_3) = 4$, $s^+(C_4) = 4$, $s^+(C_5) = 4.7639\ldots$,
$s^+(C_6) = 6$, $s^+(C_7) = 6.0489\ldots$; in each case the value strictly
exceeds $n - 1$.

Combining the two cases, $s^+(G) = n - 1$ in a connected claw-free $G$ forces
$G$ to be a path, hence a tree. $\square$

**Remark (review caveat).** Claw-free unicyclic graphs include the infinite family
$P(j, k, \ell)$ obtained by attaching three paths at one vertex of a cycle. The
$\Delta \ge 3$ members of this family are handled by Theorem 1.1; the corollary
does *not* reprove the strict EFGW inequality $s^+ > n - 1$ for the bare cycles
beyond what Proposition 9.1 supplies.

## Corollary B. Conjecture 9.2(i) holds for connected graphs of diameter at most $2$.

**Claim.** Let $G$ be a connected graph of order $n \ge 1$ with $\mathrm{diam}(G) \le 2$.
Then $s^+(G) = n - 1$ if and only if $G$ is a tree.

**Proof.** Split on the diameter.

*Diameter $0$.* Then $G = K_1$, $n = 1$, $s^+(K_1) = 0 = n - 1$, and $K_1$ is a
tree. $\checkmark$

*Diameter $1$.* Then $G = K_n$ with $n \ge 2$. The spectrum of $K_n$ is
$\{n-1,\, -1^{(n-1)}\}$, so $s^+(K_n) = (n-1)^2$. The equation $(n-1)^2 = n - 1$
forces $n - 1 \in \{0, 1\}$, i.e. $n \in \{1, 2\}$. Since $n \ge 2$ here,
$n = 2$ and $G = K_2 = P_2$ is a tree. $\checkmark$

*Diameter $2$.* Theorem 1.2 of arXiv:2506.07264 states that every connected
graph of order $n$ and diameter exactly $2$ satisfies $s^+(G) \ge n$, with the
two exceptions $G \in \{K_{1, n-1}, C_5\}$.

- $K_{1, n-1}$ is a star, hence a tree, with $s^+(K_{1, n-1}) = n - 1$. This is
  the allowed tree-equality case. $\checkmark$
- $C_5$ has spectrum $\{2, 2\cos(2\pi/5), 2\cos(2\pi/5), 2\cos(4\pi/5), 2\cos(4\pi/5)\}$,
  so $s^+(C_5) = 4 + 2 \cdot (2\cos(2\pi/5))^2 = 4 + 8\cos^2(2\pi/5)
  = 4 + 8 \cdot \tfrac{3 - \sqrt{5}}{8} = 7 - \sqrt{5} = 4.7639\ldots > 4 = n - 1.$
  So $C_5$ is not an equality case.

For all other connected graphs of diameter $2$, $s^+(G) \ge n > n - 1$. $\square$

## Joint statement

**Corollary (A + B).** Conjecture 9.2(i) holds for every connected graph that is
claw-free *or* has diameter at most $2$.

Both arguments are entirely citations from arXiv:2506.07264, plus an explicit
spectral computation for the small exceptions. They contribute no new
mathematical content, but they are useful sanity checks that the toolkit and the
notation are set up correctly for the more serious 2-tree target.
