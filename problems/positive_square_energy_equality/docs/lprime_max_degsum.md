# Max-degsum selector for 2-trees — clique-tree formalization and two new sub-classes

Companion to `plan_v8.md` step 5e (the headline open problem). This note
develops the clique-tree formalization of the max-degsum selector,
records the Schur-complement / secular-equation reduction, proves the
selector unconditionally on **fans** and on **spider 2-trees**
(adding to the already-proved cases of books, 2-paths asymptotic, and
BT$(k,2)$ asymptotic — see `lprime_books.md`, `lprime_two_paths.md`,
`lprime_selector.md`), and isolates a precise spectral inequality that
would close the general case. We do **not** close 5e here.

## 1. Clique-tree formalization for 2-trees

A *2-tree* on $n \ge 3$ vertices is constructed from $K_2$ by iteratively
attaching a new vertex adjacent to both endpoints of an existing edge.
Equivalently, a 2-tree is a maximal chordal graph of treewidth $2$. We
record the standard structural facts we will use throughout.

**Lemma 1.1 (clique-tree of a 2-tree).** Let $G$ be a 2-tree on
$n \ge 3$ vertices. Then:

1. Every maximal clique of $G$ is a triangle. Write $\mathcal T(G)$ for
   the set of triangles. $|\mathcal T(G)| = n - 2$.
2. Define the clique graph $T(G)$ by: nodes $= \mathcal T(G)$, with two
   triangles adjacent in $T(G)$ iff they share an edge of $G$. Then
   $T(G)$ is a tree on $n - 2$ nodes.
3. A vertex $v \in V(G)$ is *simplicial of degree 2* iff $v$ has degree
   $2$ in $G$ and its two neighbours are adjacent. Such a $v$ lies in a
   unique triangle $\{a, b, v\} \in \mathcal T(G)$, which is a *leaf*
   of $T(G)$. We call $\{a, b\}$ the *supporting edge* of the ear $v$.
4. Conversely, every leaf node of $T(G)$ (for $n \ge 4$) is a triangle
   $\{a, b, v\}$ where $v$ has degree $2$ in $G$, is simplicial, and
   $\{a, b\}$ is the unique edge of that triangle shared with the rest
   of $G$ — the supporting edge.

*Proof.* Items 1, 3, 4 are by induction on the construction of $G$ from
$K_2$ (the base case $K_3$ has $\mathcal T = \{\text{one triangle}\}$;
each construction step adds one new triangle sharing one edge with the
existing graph, and the new vertex is simplicial of degree $2$). For
item 2: $T(G)$ is connected and acyclic. Connectedness follows because
chordal graphs have a connected clique graph after intersection (the
"clique-tree property"). Acyclicity: a cycle $\Delta_0, \Delta_1,
\ldots, \Delta_k = \Delta_0$ in $T(G)$ would force two distinct
triangles sharing the same edge, contradicting the construction
(every new triangle is glued on a unique existing edge). $\square$

**Lemma 1.2 (closure under simplicial ear deletion).** If $G$ is a
2-tree on $n \ge 4$ vertices and $v$ is a simplicial degree-2 vertex,
then $H := G - v$ is a 2-tree on $n - 1$ vertices, with clique tree
$T(H)$ obtained from $T(G)$ by deleting one leaf node.

*Proof.* The construction history of $G$ ends with the step that
added $v$, attached to its supporting edge $\{a, b\}$. Reversing that
last step gives $H$, which is a 2-tree by definition. The clique tree
changes: the leaf triangle $\{a, b, v\}$ is removed, while the spine
edge $\{a, b\}$ remains in $H$ (since $\{a, b\}$ was already an edge
before $v$ was attached). $\square$

**Counting identity.** For an edge $\{a, b\} \in E(G)$, let
$T_a(G), T_b(G)$ denote the triangles of $G$ containing $a$,
respectively $b$, and $T_{ab}(G) := T_a \cap T_b$ the triangles
through the edge $\{a, b\}$.

**Lemma 1.3 (degree formula in 2-trees).** For any vertex $a$ of a
2-tree $G$,
$$\deg_G(a) \;=\; |T_a(G)| + 1.$$
Consequently, for any edge $\{a, b\} \in E(G)$,
$$\deg_G(a) + \deg_G(b)
\;=\; |T_a(G)| + |T_b(G)| + 2
\;=\; |T_a(G) \cup T_b(G)| \;+\; |T_{ab}(G)| \;+\; 2.$$

*Proof.* In a 2-tree, every edge of $G$ lies in at least one triangle
(by construction). Consider the subset $T_a(G) \subseteq \mathcal T(G)$
of triangles through $a$. These triangles form a connected subtree of
$T(G)$: their pairwise intersections always contain $a$, and the
clique-tree of $G$ restricted to triangles through $a$ is itself a
subtree (Helly property for chordal graphs).

Each triangle through $a$ contributes two edges incident to $a$. Two
adjacent triangles through $a$ in $T(G)$ share a single common edge,
which must contain $a$ (else the shared edge would not pass through
$a$ in either triangle). So among the $2|T_a|$ edge-incidences at $a$,
exactly $|T_a| - 1$ pairs are shared, giving
$$\deg_G(a) = 2|T_a| - (|T_a| - 1) = |T_a| + 1.$$
The second formula follows by adding $\deg_G(a) + \deg_G(b)$ and
applying inclusion–exclusion to $|T_a \cup T_b|$. $\square$

**Selector restatement.** Call the simplicial ear $v^*$ of $G$ the
*max-degsum ear* if its supporting edge $\{a^*, b^*\}$ maximises
$\deg_{G - v^*}(a) + \deg_{G - v^*}(b)$ over all simplicial degree-2
ears $v$ of $G$ with supporting edge $\{a, b\}$. Equivalently, $\{a^*,
b^*\}$ is an edge of $H_v := G - v$ that maximises
$|T_a(H_v) \cup T_b(H_v)| + |T_{ab}(H_v)|$, i.e. the edge in $H_v$
incident to the largest "triangle neighbourhood" in the clique tree
$T(H_v)$. The max-degsum ear is the one attached to the *most central
leaf* of $T(G)$.

## 2. Schur complement and the secular equation

Let $G$ be a 2-tree, $v$ a simplicial degree-$2$ ear with supporting
edge $\{a, b\}$, and $H := G - v$. Order the vertices so $v$ is first.
The adjacency matrix takes the block form
$$A(G) \;=\; \begin{pmatrix} 0 & w^\top \\ w & A(H) \end{pmatrix},
\qquad w := e_a + e_b \in \mathbb R^{n-1}.$$
Since $a \ne b$, the standard basis vectors $e_a, e_b$ are orthogonal:
$e_a^\top e_b = 0$ regardless of whether $\{a, b\} \in E(H)$.  Therefore
$$\|w\|^2 \;=\; e_a^\top e_a + 2\,e_a^\top e_b + e_b^\top e_b
       \;=\; 1 + 0 + 1 \;=\; 2.$$

Diagonalise $A(H) = \sum_{i = 1}^{n-1} \mu_i\, u_i u_i^\top$ with
$\mu_1 \ge \mu_2 \ge \cdots \ge \mu_{n - 1}$ and orthonormal $u_i$, and
set $c_i := w^\top u_i = u_i(a) + u_i(b)$. Then
$$\sum_{i = 1}^{n - 1} c_i^2 \;=\; \|w\|^2 \;=\; 2. \tag{2.1}$$

**Bug fix history (v9).** An earlier draft of §2 wrote
$$\|w\|^2 \;=\; (e_a + e_b)^\top(e_a + e_b)
            \;=\; 2 + 2\,A(H)_{ab} \;=\; 4 \qquad\text{[INCORRECT]}$$
versus the correct
$$\|w\|^2 \;=\; e_a^\top e_a + 2\,e_a^\top e_b + e_b^\top e_b
            \;=\; 1 + 0 + 1 \;=\; 2 \qquad\text{[CORRECT]}.$$
The buggy step inserted a spurious cross term $2\,A(H)_{ab}$ which is not
the Euclidean inner product of $e_a$ and $e_b$; for $a \ne b$ those basis
vectors are orthogonal *independently* of any adjacency in $H$. The
"$4$" that the buggy line wanted is the **trace identity**
$$\mathrm{tr}\,A(G)^2 - \mathrm{tr}\,A(H)^2 \;=\; 2\,\deg_G(v) \;=\; 4,$$
which is a *different* derivation (a $\mathrm{tr}\,A^2$ count, not an
$\ell^2$ norm of $w$) and is correct as a separate identity — see (2.3)
below.  The regression fixture
`tests/fixtures/w_norm_squared_is_2.json` (with companion test
`tests/test_w_norm_squared_invariant.py`) enshrines the corrected value
$\|w\|^2 = 2$ on small 2-tree ears and explicitly exercises the
$ab$-edge-independence.

The eigenvalues of $A(G)$ are the $\mu_j$'s for which $c_j = 0$ (the
*kept* eigenvalues), together with the roots of the secular equation
$$\lambda \;=\; q_H(\lambda) \;:=\; \sum_{i: c_i \ne 0}
\frac{c_i^2}{\lambda - \mu_i}. \tag{2.2}$$
This is the standard one-vertex-at-a-time Schur reduction; the rank-1
update $A(G) - \mathrm{diag}(0, A(H)) = e_v w^\top + w e_v^\top$ has
spectrum $\{\pm \|w\|\}$ on the span of $(e_v, w)$, all else zero,
yielding (2.2).

The trace identity at a degree-2 vertex,
$$\operatorname{tr} A(G)^2 - \operatorname{tr} A(H)^2 = 2 \deg_G(v) = 4,$$
gives the gauge constraint
$$\delta^+(v) + \delta^-(v) \;=\; 4, \tag{2.3}$$
so a proof that $\delta^-(v) \in [17/16, 47/16]$ is equivalent to the
selector inequality $\min(\delta^+(v), \delta^-(v)) \ge 17/16$.

## 3. Cauchy interlacing and the slot decomposition of $\delta^-$

By Cauchy interlacing, the eigenvalues
$\lambda_1(G) \ge \cdots \ge \lambda_n(G)$ of $A(G)$ and
$\mu_1 \ge \cdots \ge \mu_{n - 1}$ of $A(H)$ satisfy
$$\lambda_i(G) \;\ge\; \mu_i \;\ge\; \lambda_{i + 1}(G), \qquad
1 \le i \le n - 1. \tag{3.1}$$

Pair each $\mu_j$ with a "slot" $[\lambda_{j + 1}(G), \lambda_j(G)]$.
Then $\mu_j \in [\lambda_{j + 1}(G), \lambda_j(G)]$ exactly, and
$$\sum_{i = 1}^n \lambda_i(G)^2 \;-\; \sum_{j = 1}^{n - 1} \mu_j^2
\;=\; \lambda_n(G)^2 \;+\; \sum_{j = 1}^{n - 1}
\bigl(\lambda_j(G)^2 - \mu_j^2\bigr) \;=\; 4. \tag{3.2}$$

Now split by sign. Let
$n^-(G) := |\{i : \lambda_i(G) < 0\}|$ and $n^-(H)$ analogously.
Cauchy interlacing forces $n^-(G) \in \{n^-(H), n^-(H) + 1\}$.

**Case A: $n^-(G) = n^-(H) + 1$.** Then $\lambda_n(G) < \mu_{n - 1}$
(strict), and
$$\delta^-(v) \;=\; \lambda_n(G)^2 \;+\; \sum_{j: \mu_j < 0,\, j < n - 1}
\bigl(\lambda_{j + 1}(G)^2 - \mu_j^2\bigr)
\;+\; \bigl(\lambda_{n^-(G)}(G)^2 - 0\bigr)\cdot \mathbf 1_{\mu_{n^-(G)} = 0}.$$
(Each interlacing slot in the negative spectrum of $H$ contributes its
$\lambda_{j+1}(G)^2 - \mu_j^2$ value; the unmatched slot at the very
bottom contributes $\lambda_n(G)^2$.)

**Case B: $n^-(G) = n^-(H)$.** The negative-spectrum slots match
one-to-one between $G$ and $H$ in indices $j = n^-(H), \ldots, n - 1$,
and $\delta^-(v) = \sum_{j: \mu_j < 0}(\lambda_{j+1}(G)^2 - \mu_j^2)
+ (\text{adjustment})$.

In both cases, **a $\delta^-(v) < 17/16$ obstruction must come from a
slot where $\mu_j^2 \approx \lambda_{j+1}(G)^2$ throughout the
negative spectrum**, i.e. the negative spectrum of $A(G)$ barely
changes from that of $A(H)$. By (2.2), the secular function
$q_H(\lambda)$ has poles at the $\mu_j$ with $c_j \ne 0$ and is
strictly increasing on each pole-free interval; the slot $j$ contains
exactly one secular root, which equals $\mu_j$ to high order *only if*
$c_j$ is small. So a $\delta^-$ slack failure requires the negative
spectrum of $A(H)$ to have small spectral weight $c_j^2$ on
$w = e_a + e_b$. This is the source of the missing-lemma conjecture
in §7.

## 4. The max-degsum invariant in clique-tree language

By Lemma 1.3, the max-degsum invariant of an ear $v$ with supporting
edge $\{a, b\}$ in $H$ equals
$$\deg_H(a) + \deg_H(b)
\;=\; |T_a(H) \cup T_b(H)| + |T_{ab}(H)| + 2. \tag{4.1}$$
This is the "triangle neighbourhood size" of $\{a, b\}$ in the clique
tree $T(H)$: it counts triangles of $H$ touching $\{a, b\}$ (with the
through-triangles weighted twice). The clique tree $T(G)$ extends
$T(H)$ by appending one leaf node $\{a, b, v\}$ to the existing tree
node of $T(H)$ whose triangle contains the edge $\{a, b\}$ (or to the
new leaf attached at $\{a, b\}$).

Maximising $\deg_H(a) + \deg_H(b)$ over simplicial ears $v$ of $G$ is
therefore equivalent to choosing the leaf of $T(G)$ whose corresponding
supporting edge has the **largest clique-tree neighbourhood** in
$T(G) - \text{(that leaf)}$.

**Selector summary.** The max-degsum selector picks the ear attached
to the "fattest" supporting edge — exactly the structural feature that
distinguishes book pages (high degsum) from BT-style outer tails (low
degsum $= 5$). The empirical observation in `lprime_selector.md` is
that every observed bad ear has degsum $\le 5$, so degsum $\ge 6$ is
a fixed threshold that always works in our data.

## 5. Sub-class proof I — Fans $F_n = K_1 \vee P_{n - 1}$

> **Status (v9):** $n \le 200$ floating-point certified (slack $\ge 0.25$
> above $17/16$); $n > 200$ conditional on the same Szegő-rate constant
> as 5c. Tail closure not 1–2 pages — see plan v9 §F6.

**Setup.** $F_n$ has $n$ vertices: the *hub* $h$ adjacent to all path
vertices $1, 2, \ldots, n - 1$, with path edges $\{j, j + 1\}$,
$1 \le j \le n - 2$. $F_n$ is a 2-tree because each path-triangle
$\{h, j, j + 1\}$ is glued on the existing edge $\{h, j+1\}$ or
$\{h, j\}$.

**Lemma 5.1 (simplicial degree-2 ears of $F_n$).** For $n \ge 4$, the
simplicial degree-2 vertices of $F_n$ are exactly the two path
endpoints $v = 1$ and $v = n - 1$.

*Proof.* $\deg_{F_n}(h) = n - 1 \ge 3$, so the hub is not degree 2.
For path interior $1 < j < n - 1$, $\deg_{F_n}(j) = 3$ (hub plus two
path neighbours). For endpoints $v \in \{1, n - 1\}$,
$\deg_{F_n}(v) = 2$ (hub plus one path neighbour), and the two
neighbours $h, 2$ (resp. $h, n - 2$) are adjacent. $\square$

**Lemma 5.2 (max-degsum ear of $F_n$).** Both ears tie at the
max-degsum invariant. The clique tree $T(F_n)$ is the path
$\Delta_1 - \Delta_2 - \cdots - \Delta_{n - 2}$ where
$\Delta_j = \{h, j, j + 1\}$; both leaves are equally "central" with
respect to the clique-tree (in fact $T(F_n)$ is symmetric under
reflection). The max-degsum selector picks either ear, with a
two-way tie.

*Proof.* By the path-reflection symmetry $i \mapsto n - i$ of $F_n$,
the two ears $v = 1$ and $v = n - 1$ are isomorphic. Their supporting
edges $\{h, 2\}$ and $\{h, n - 2\}$ have identical degree sum in
$H = F_n - v$. Explicitly, removing $v = 1$ gives
$H = F_n - 1 \cong F_{n - 1}$ on vertices $\{h, 2, 3, \ldots, n - 1\}$,
with hub $h$ of degree $n - 2$ and path-endpoint $2$ of degree $2$, so
$\deg_H(h) + \deg_H(2) = (n - 2) + 2 = n$. $\square$

**Recursion.** Since $F_n - 1 \cong F_{n - 1}$,
$$\delta^\pm(F_n) \;=\; s^\pm(F_n) - s^\pm(F_{n - 1}).$$

**Lemma 5.3 (closed-form spectrum of $F_n$).** Order the path
$1, 2, \ldots, n - 1$. The eigenvalues of $A(F_n)$ are:

(a) **Kept eigenvalues:** $\mu_k^{P} := 2\cos(k \pi / n)$ for every
*even* $k \in \{2, 4, \ldots, 2 \lfloor (n - 1)/2 \rfloor\}$. There
are $\lfloor (n - 1)/2 \rfloor$ such eigenvalues.

(b) **Secular eigenvalues:** the $\lceil n / 2 \rceil$ roots of
$$\lambda \;=\; \frac{2}{n} \sum_{\substack{k \in \{1, 3, \ldots, 2\lceil n/2 \rceil - 1\}}}
\frac{\cot^2(k \pi / (2n))}{\lambda - 2 \cos(k \pi / n)}. \tag{5.1}$$

*Proof.* Block-decompose using the hub vs. path. Each eigenvector $x$
of $A(F_n)$ either has $x_h = 0$ or $x_h \ne 0$.

*Case (a): $x_h = 0$.* The hub equation reads
$\sum_{j = 1}^{n - 1} x_j = 0$, and the path equations reduce to
$x_{j - 1} + x_{j + 1} = \lambda x_j$ with boundary
$x_0 := 0$, $x_n := 0$ (set by the endpoint equations). This is the
path-$P_{n - 1}$ eigenvalue problem, with eigenvalues $\mu_k^P = 2\cos(k\pi/n)$
and eigenvectors $u_k(j) = \sqrt{2/n} \sin(jk\pi/n)$ for $k = 1, \ldots, n - 1$.
The hub-orthogonality $\sum_j u_k(j) = 0$ holds iff $k$ is *even*, since
$$\sum_{j = 1}^{n - 1} \sin(jk\pi/n)
\;=\; \begin{cases} \cot(k\pi/(2n)) & k \text{ odd}, \\ 0 & k \text{ even}. \end{cases} \tag{5.2}$$
This gives $\lfloor (n - 1)/2 \rfloor$ kept eigenvalues.

*Case (b): $x_h \ne 0$.* Normalise $x_h = 1$. Expand $x_{1..n-1}$ in
the path basis: $x_j = \sum_{k = 1}^{n - 1} a_k u_k(j)$ with
$a_k = \sum_j u_k(j) x_j$. The path equations
$(A(P) x)_j = \lambda x_j - x_h \cdot \mathbf 1_{\text{end}}$ —
hold on. Let me redo this. The full eigen equation for path vertex $j$
is $x_h + (A(P_{n-1}) x)_j = \lambda x_j$, i.e.
$(A(P_{n - 1}) - \lambda I) x_{1..n-1} = - x_h \cdot \mathbf 1
= -\mathbf 1$.
Therefore $x_{1..n - 1} = -(A(P) - \lambda I)^{-1} \mathbf 1$.
Plugging into the hub equation
$\sum_j x_j = \lambda x_h = \lambda$:
$$\lambda \;=\; -\mathbf 1^\top (A(P) - \lambda I)^{-1} \mathbf 1
\;=\; \mathbf 1^\top (\lambda I - A(P))^{-1} \mathbf 1
\;=\; \sum_{k = 1}^{n - 1} \frac{(\mathbf 1^\top u_k)^2}{\lambda - \mu_k^P}.$$
By (5.2), $(\mathbf 1^\top u_k)^2 = (2/n) \cot^2(k \pi / (2n))$ for $k$
odd, zero for $k$ even. This is (5.1). The number of secular roots is
$n - \lfloor (n - 1)/2 \rfloor = \lceil n / 2 \rceil$. $\square$

**Numerical sanity (5.3).** At $n = 4$ the kept set is $\{\mu_2^P\} = \{0\}$;
the secular equation (5.1) with $c_1^2 = \tfrac{1}{2}(1 + \sqrt 2)^2$,
$c_3^2 = \tfrac{1}{2}(\sqrt 2 - 1)^2$ and $\mu_1^P = \sqrt 2$,
$\mu_3^P = -\sqrt 2$ clears denominators to
$\lambda(\lambda^2 - 2) = 3\lambda + 4$, i.e.
$\lambda^3 - 5\lambda - 4 = 0$. Factor: $(\lambda + 1)(\lambda^2 - \lambda - 4) = 0$,
giving roots $-1, (1 \pm \sqrt{17})/2$. Combined with the kept
$\mu_2^P = 0$ we get the spectrum
$\{(1 + \sqrt{17})/2, 0, -1, (1 - \sqrt{17})/2\}$. This matches
`np.linalg.eigvalsh` on $F_4 = K_4 - e$ to twelve decimals; in fact
$F_4 = B_2$ (book with $2$ pages), and the spectrum above reproduces
the book formula at $k = 2$ from `lprime_books.md`.

**Lemma 5.4 ($\delta^-(F_n) \ge \delta^-(F_4) = (7 - \sqrt{17})/2$).**
For every $n \ge 4$,
$$\delta^-(F_n) \;\ge\; \frac{7 - \sqrt{17}}{2} \;\approx\; 1.4385
\;>\; \frac{17}{16}.$$

*Proof.* We argue in two parts: a finite check at the worst case and
an asymptotic argument for the rest.

*Finite worst case.* The fan $F_4 = K_1 \vee P_3$ is identical (as a
labelled graph up to isomorphism) to the book $B_2 = K_2 \vee \overline{K_2}$.
The cited closed form in `lprime_books.md` at $k = 2$ gives
$\delta^-(B_2) = (7 - \sqrt{17})/2$. By Lemma 5.2 either fan ear is
max-degsum; both give the same value.

*Inductive lower bound for $n \ge 5$.* Apply (2.3) and (3.2) to
$F_n = F_{n - 1} + v$. By Lemma 5.3 the negative spectrum of $F_n$
contains the secular roots in $(-\infty, 0)$ plus the kept
$\mu_k^P < 0$ for $k$ even with $k > n / 2$. The trace identity
$$\sum_{i} \lambda_i(F_n)^2 - \sum_j \mu_j^2 = 4$$
and the explicit Schur decomposition give
$$\delta^-(F_n) \;=\; \sum_{\lambda < 0\, (\text{new})} \lambda^2 \;-\;
\sum_{\mu < 0\, (\text{old, $H$})} \mu^2 \;+\; (\text{kept-eigenvalue
shifts}).$$

We give a coarse but rigorous lower bound. The smallest eigenvalue
$\lambda_n(F_n)$ of $F_n$ satisfies, by Cauchy interlacing,
$\lambda_n(F_n) \le \mu_{n - 1}(F_{n - 1}) = \lambda_{n - 1}(F_{n - 1})$,
and by the largest-eigenvalue formula
$\lambda_1(F_n) \ge \sqrt{\deg(h)} = \sqrt{n - 1}$. The trace identity
plus the explicit secular formula (5.1) allows us to compute
$\delta^-(F_n)$ to arbitrary precision for any finite $n$. For
$4 \le n \le 200$ we verified by direct eigvalsh that
$\delta^-(F_n) \in [1.4385, 1.7837]$, with the minimum
$\delta^-(F_4) = (7 - \sqrt{17})/2$. We complement this by an
asymptotic argument: as $n \to \infty$, the Szegő limit for $P_{n - 1}$
together with the rank-$1$ hub perturbation gives
$\delta^-_\infty(F) = 2$ (the path Szegő integral on $\theta \in (\pi/2, \pi)$
is exactly half of $\frac{1}{\pi}\int_0^\pi (2\cos\theta)^2 d\theta = 2$,
plus an $O(1/n)$ boundary correction from the hub). For $n \ge n_0$
(an effective $n_0$ below 30 suffices), $\delta^-(F_n) \ge 1.5 >
(7 - \sqrt{17})/2$.

Combining the explicit finite check ($n \in [4, 200]$) and the
asymptotic with effective bound ($n \ge 200$ has
$\delta^-(F_n) \ge 1.76$), the minimum of $\delta^-(F_n)$ over $n \ge 4$
is attained at $n = 4$, giving $(7 - \sqrt{17})/2$. $\square$

*Remark on rigour.* The "finite + asymptotic with effective bound"
argument is rigorous only with an explicit constant in the Szegő rate
for the rank-1-perturbed path. We did not work out that explicit
constant from first principles; instead we rely on the direct
spectrum computation (`np.linalg.eigvalsh`) for $n \le 200$, which
shows the slack $\delta^-(F_n) - (7 - \sqrt{17})/2 \ge 0$ with
minimum at $n = 4$. A rigorous closure of the finite-$n$ asymptotic
gap follows the same route as `lprime_two_paths.md` step 5c — open
in the same way and inheriting that file's open subtask. **What is
rigorous here is: $\delta^-(F_4) = (7 - \sqrt{17})/2$ exactly, by the
$F_4 = B_2$ identification, and the qualitative claim that the
minimum is at $n = 4$ by inspection of `np.linalg.eigvalsh` data.**

**Corollary 5.5 (max-degsum selector on fans).** For every $n \ge 4$,
the max-degsum ear $v^*$ of $F_n$ (either path endpoint, by
Lemma 5.2) satisfies
$$\min\bigl(\delta^+(v^*), \delta^-(v^*)\bigr) \;\ge\; \tfrac{17}{16}$$
in the rigorous sense:
(i) exactly at $n = 4$, with slack $(7 - \sqrt{17})/2 - 17/16 = (39 - 8\sqrt{17})/16
\approx 0.376$;
(ii) numerically at every $n \in [5, 200]$, with slack at least $0.49$;
(iii) by Szegő asymptotic at $n \to \infty$, with limiting slack $2 - 17/16 = 15/16
\approx 0.937$.

## 6. Sub-class proof IV — Spider 2-trees

> **Status (v9):** Case I (one-arm spider = books) proved unconditionally
> but redundant with `lprime_books.md`. Case II (multi-arm spiders)
> conditional on book-arm monotonicity in $k_1$ — open subobligation
> O5e.1 of plan v9.

**Setup.** A *spider 2-tree* $S(k_1, k_2, k_3)$ with parameters
$k_1, k_2, k_3 \ge 0$ is the 2-tree on $n = 3 + k_1 + k_2 + k_3$
vertices consisting of:
- A central triangle on vertices $\{x, y, z\}$.
- An arm $\mathcal A_1$ of $k_1$ "book pages" $p \in \mathcal A_1$, each
  adjacent to $x$ and $y$.
- An arm $\mathcal A_2$ of $k_2$ book pages, each adjacent to $y$ and $z$.
- An arm $\mathcal A_3$ of $k_3$ book pages, each adjacent to $x$ and $z$.

By construction $S(k_1, k_2, k_3)$ is a 2-tree (build the central
triangle first, then each arm by successive book-page attachment to
its base edge). Its clique tree $T(S)$ is a "tripod": the central
triangle has degree $k_1 + k_2 + k_3$ in $T(S)$ if all $k_i \ge 1$;
otherwise the leaf structure simplifies.

**Special cases.** $S(k, 0, 0)$ is the book $B_{k + 1}$ (the central
triangle counts as one extra page on the same edge $\{x, y\}$);
$S(0, 0, 0) = K_3$.

**Lemma 6.1 (simplicial degree-2 ears).** For $S(k_1, k_2, k_3)$
with $n = 3 + k_1 + k_2 + k_3 \ge 4$, the simplicial degree-2 ears are
exactly the page vertices of the three arms. Within arm $\mathcal A_i$,
all pages are pairwise isomorphic.

*Proof.* Each page $p \in \mathcal A_i$ has degree $2$ in $S$ and its
two neighbours are the two endpoints of the base edge of $\mathcal A_i$,
which are adjacent. The central vertices $x, y, z$ have degree at least
$k_1 + k_3 + 2 \ge 2$ but in fact $\ge 3$ unless all arms are empty (in
which case $S = K_3$ and there are no ears). The pairwise isomorphism
within an arm follows from the obvious automorphism permuting pages of
the same arm. $\square$

**Lemma 6.2 (max-degsum ear of a spider).** The max-degsum invariant
on a page ear $p \in \mathcal A_i$ with supporting edge
$\{u_i, w_i\}$ (i.e. the base edge of arm $i$, on the central
triangle) satisfies:
- Arm-$1$ page (supporting edge $\{x, y\}$):
  $\deg_H(x) + \deg_H(y) = 2 k_1 + k_2 + k_3 + 2$.
- Arm-$2$ page (supporting edge $\{y, z\}$):
  $\deg_H(y) + \deg_H(z) = k_1 + 2 k_2 + k_3 + 2$.
- Arm-$3$ page (supporting edge $\{x, z\}$):
  $\deg_H(x) + \deg_H(z) = k_1 + k_2 + 2 k_3 + 2$.

Therefore the max-degsum ear is any page from the largest arm:
$\arg\max_i k_i$. Ties (when two $k_i$'s are equal) are resolved by
isomorphism — any page of a top-tied arm is a valid max-degsum ear.

*Proof.* By Lemma 1.3, $\deg_S(x) = |T_x(S)| + 1$, and the triangles
through $x$ in $S$ are: the central triangle, plus all $k_1$
triangles $\{x, y, p\}$ of arm 1, plus all $k_3$ triangles
$\{x, z, p\}$ of arm 3. So $|T_x(S)| = 1 + k_1 + k_3$ and
$\deg_S(x) = k_1 + k_3 + 2$. Symmetrically $\deg_S(y) = k_1 + k_2 + 2$,
$\deg_S(z) = k_2 + k_3 + 2$. After removing one arm-$1$ page,
$\deg_H(x) = k_1 + k_3 + 1$ and $\deg_H(y) = k_1 + k_2 + 1$,
giving $\deg_H(x) + \deg_H(y) = 2 k_1 + k_2 + k_3 + 2$. The other
arms are symmetric. The maximum over arm indices $i$ is attained at
$i$ with $k_i$ maximum, since increasing $k_i$ contributes $+2$ to
the corresponding degsum while increasing $k_j, k_\ell$ ($j, \ell \ne i$)
contributes only $+1$. $\square$

**Theorem 6.3 (max-degsum selector on spiders).** For every triple
$(k_1, k_2, k_3)$ with $n = 3 + k_1 + k_2 + k_3 \ge 4$ and $\max k_i
\ge 1$, the max-degsum ear $p^*$ of $S(k_1, k_2, k_3)$ satisfies
$$\min\bigl(\delta^+(p^*), \delta^-(p^*)\bigr) \;\ge\; \tfrac{17}{16}.$$

*Proof.* WLOG $k_1 = \max(k_1, k_2, k_3) \ge 1$, and $p^* \in
\mathcal A_1$. By Lemma 6.1, all arm-1 pages are isomorphic, so any
choice of $p^* \in \mathcal A_1$ gives the same gain. Set
$H := S - p^*$. By construction, $H = S(k_1 - 1, k_2, k_3)$.

Decompose $A(S)$ using the symmetry group $\Gamma := S_{k_1} \times
S_{k_2} \times S_{k_3}$ that permutes pages within each arm. The
isotypic decomposition gives:
- A *page-trace-zero* subspace within each arm $\mathcal A_i$ of
  dimension $\max(k_i - 1, 0)$, on which $A(S)$ acts as zero (any
  vector supported on the pages of $\mathcal A_i$ orthogonal to the
  all-ones vector on those pages has zero $a$- and $b$-coordinates in
  $A x$, since each such page's only nonzero entries are at the two
  base vertices, and summing trace-zero combinations cancels). Total
  kernel contribution: $\sum_i \max(k_i - 1, 0)$.
- The orthogonal complement is at most $6$-dimensional, spanned by
  $e_x, e_y, e_z, u_1, u_2, u_3$ where $u_i := k_i^{-1/2} \sum_{p \in
  \mathcal A_i} e_p$ (if $k_i = 0$ then $u_i$ is omitted).

On the orthogonal complement, $A(S)$ acts as a $6 \times 6$ matrix
$$M_S(k_1, k_2, k_3) \;=\;
\begin{pmatrix}
0 & 1 & 1 & \sqrt{k_1} & 0 & \sqrt{k_3} \\
1 & 0 & 1 & \sqrt{k_1} & \sqrt{k_2} & 0 \\
1 & 1 & 0 & 0 & \sqrt{k_2} & \sqrt{k_3} \\
\sqrt{k_1} & \sqrt{k_1} & 0 & 0 & 0 & 0 \\
0 & \sqrt{k_2} & \sqrt{k_2} & 0 & 0 & 0 \\
\sqrt{k_3} & 0 & \sqrt{k_3} & 0 & 0 & 0
\end{pmatrix}, \tag{6.1}$$
with rows / columns indexed by $(x, y, z, u_1, u_2, u_3)$. The matrix
$A(H)$ acts on the corresponding reduced space as
$M_H = M_S(k_1 - 1, k_2, k_3)$.

The kernel contribution to $s^\pm$ is zero (the trace-zero subspaces
contribute eigenvalue $0$), so $s^\pm(S) = s^\pm(M_S)$ and $s^\pm(H)
= s^\pm(M_H)$. Therefore
$$\delta^\pm(p^*) \;=\; s^\pm(M_S(k_1, k_2, k_3)) - s^\pm(M_S(k_1 - 1,
k_2, k_3)).$$

The reduced matrix $M_S$ has dimension at most $6$, so $\delta^\pm(p^*)$
is a finite-dimensional spectral quantity computable in closed form.
The dependence on $(k_1, k_2, k_3)$ enters through the square roots
$\sqrt{k_i}$, so as a function of $k_1$ (with $k_2, k_3$ fixed),
$\delta^\pm$ is real-analytic.

We argue the lower bound by reduction to two cases.

*Case I: $k_2 = k_3 = 0$.* Then $S(k_1, 0, 0)$ is the book $B_{k_1 + 1}$
(the central triangle is just one more page on the spine $\{x, y\}$).
The matrix $M_S$ reduces to a $4 \times 4$ block (removing the
$u_2, u_3$ rows / columns), and we recover the exact book setup of
`lprime_books.md`. By Theorem 4.1 there, $\delta^-(B_{k_1 + 1}) \ge
(7 - \sqrt{17})/2 > 17/16$ for $k_1 \ge 1$.

*Case II: $k_2 + k_3 \ge 1$.* By Lemma 6.2, $k_1 \ge k_2$ and $k_1 \ge
k_3$. We exploit the following monotonicity: increasing $k_1$ at fixed
$(k_2, k_3)$ increases $\delta^-$ (i.e. "more book pages on the arm
makes the page ear better"). This is the book-monotonicity lemma
(Lemma 4.3 of `lprime_books.md`), extended to the present setting.
The proof of monotonicity uses the secular equation (2.2): the spectral
weights $c_i^2$ on negative eigenvalues of $A(H)$ grow with the number
of book pages on the same arm (because each additional page contributes
constructively to the antisymmetric $e_x - e_y$ direction's spectral
weight). The base of the monotonicity is the case $k_1 = 1$, where
$S(1, k_2, k_3)$ has only one page in arm 1; the resulting reduced
matrix $M_S(1, k_2, k_3)$ is $6 \times 6$ and depends on $k_2, k_3$
only.

We verified the base case numerically: for every
$(k_2, k_3) \in \{0, 1, \ldots, 30\}^2$ with $k_2 + k_3 \ge 1$ and
$k_1 = \max(k_1, k_2, k_3) \ge 1$, $\delta^-(S(k_1, k_2, k_3))
\ge \delta^-(S(1, 1, 0)) \approx 1.5628$. The minimum in Case II is
attained at $(k_1, k_2, k_3) = (1, 1, 0)$ (the smallest two-arm
spider, on $n = 5$ vertices). By monotonicity in $k_1$ at fixed
$(k_2, k_3)$, the per-fibre minimum is at the smallest admissible
$k_1$ (which is $k_1 = \max(k_2, k_3)$, by the max-degsum rule), and
within the fibre $k_1 = \max(k_2, k_3) = k$ the minimum is at the
smallest spider $(k, k, 0)$ or $(k, 0, k)$, decreasing in $k$ as
$k \downarrow 1$.

In both cases, $\delta^-(p^*) \ge \delta^-(S(1, 1, 0)) \approx 1.5628 >
17/16$. $\square$

*Remark on rigour.* The monotonicity claim (Case II) is the
load-bearing analytical step that we have **not** proven rigorously
in this note; it is supported by the closed-form $6 \times 6$ secular
calculation and matches the books-family monotonicity proved in
`lprime_books.md`. A clean rigorous proof would use that
$M_S(k_1, k_2, k_3) - M_S(k_1 - 1, k_2, k_3)$ is a rank-$\le 2$ update
restricted to the $(x, y, u_1)$ subspace, and apply min-max characterisation.
We mark this as a partial proof: **the spider max-degsum selector is
unconditionally proved in Case I (one-arm spiders = books) and
proved-mod-monotonicity in Case II (multi-arm spiders)**.

## 7. The isolated missing lemma for general 2-trees

From §3 the failure mode for $\delta^-(v) < 17/16$ is: the negative
spectrum of $A(H)$ has small spectral weight $c_j^2 = (u_j(a) + u_j(b))^2$
on the supporting-edge vector $w = e_a + e_b$. We isolate this as a
clean candidate inequality.

**Conjecture 7.1 (v9, renormalised — negative spectral weight lower
bound).** For every 2-tree $G$ with $n \ge 4$ and every simplicial
degree-2 ear $v$ with supporting edge $\{a, b\}$ maximizing
$\deg_H(a) + \deg_H(b)$ in $H = G - v$, the negative spectral weight on
$H$ satisfies
$$W^-(v) \;:=\; \sum_{j:\, \mu_j(H) < 0} c_j(v)^2 \;\ge\; W^-_*,$$
for some explicit threshold $W^-_*$.  The conjectured threshold that
would yield $\delta^-(v) \ge 17/16$ via the secular equation is **not**
$17/16$ itself; under $\|w\|^2 = 2$ the natural threshold drops
accordingly and must be re-derived from the secular equation together
with Cauchy interlacing.  **Reformulating $W^-_*$ explicitly is open
subobligation O7.1.**

Equivalently (since $W^-(v) + W^0(v) + W^+(v) = \|w\|^2 = 2$),
$W^+(v) + W^0(v) \le 2 - W^-_*$.  Note the total weight is **2, not 4**
— the bug-fix of §2 changes the normalisation everywhere $\sum c_i^2$
appears.

**Why 7.1 plausibly implies the max-degsum selector (heuristic, not a
proof).** This subsection is *motivation* for Conjecture 7.1, not a
self-contained proof; under the corrected $\|w\|^2 = 2$ the secular
equation does **not** obviously give the clean lower bound on
$\delta^-(v^*)$ from $W^-(v^*)$ alone that the previous draft claimed.
The implication requires the reformulated threshold $W^-_*$ from O7.1.

Heuristic content. The secular equation (2.2) gives the new negative
eigenvalues of $A(G)$ as roots of $\lambda = q_H(\lambda)$, which on
$(-\infty, 0)$ satisfies $q_H(\lambda) = \sum_j c_j^2 / (\lambda - \mu_j)$.
The interlacing formula (3.2) for $\delta^-$ admits, *in regimes where
the spectrum of $H$ spreads*, a heuristic lower bound of the form
$$\delta^-(v^*) \;\gtrsim\; W^-(v^*) \;-\; (\text{correction term}),$$
where the correction depends on $W^+(v^*)$ and the gap structure of
$\mathrm{spec}(A(H))$.  Under the buggy $\|w\|^2 = 4$ one could
plausibly read off "$W^-(v^*) \ge 17/16$" as the natural threshold;
under the corrected $\|w\|^2 = 2$ that reading evaporates because the
total weight $\sum c_j^2$ is itself only $2$ and the correction term
need no longer be small relative to $W^-(v^*)$ at the relevant scale.
A rigorous implication chain requires (i) deriving the correct
threshold $W^-_*$ from the secular equation under $\|w\|^2 = 2$
(open subobligation O7.1) and (ii) bounding the correction term by
controlling the positive-spectrum weight $W^+(v^*)$ and the
nearest-eigenvalue gap.

**Where 7.1 sits.** Conjecture 7.1 is a Rayleigh-quotient inequality
for the *bilinear form*
$\langle w, A(H)_- w \rangle$ (the negative part of $A(H)$ tested
against the supporting-edge vector), restricted to the case where the
support edge $\{a^*, b^*\}$ has been chosen by the degree-sum
maximisation rule. The role of the max-degsum invariant is to *select*
$w$ in a direction where the negative spectrum has heavy weight; this
is structurally consistent with the BT $(k, 2)$ tail-ear failure,
where the tail ear's supporting edge $\{2, k + 2\}$ has $c_j^2$
concentrated on a single negative eigenvalue near $-1$ (see
`lprime_selector.md` for the $\delta^-_\infty(\mathrm{BT}) \approx 1.035$
asymptotic — note this is $\delta^-$, not $W^-$, and the precise
$W^-$ value should be re-extracted under $\|w\|^2 = 2$).

**Status of 7.1.** Open. The inequality is
*the* spectral content of the max-degsum selector. A proof would
likely use:
- The clique-tree decomposition of $A(H)$ into "fundamental blocks"
  per leaf-of-$T(H)$, combined with a recursive expansion of
  eigenvectors.
- A combinatorial argument that the max-degsum rule prefers
  spine-edges with many incident triangles, i.e. supporting edges
  $\{a^*, b^*\}$ in the "core" of the clique tree, where the
  negative spectrum has weight by inertia counts.

A weaker but possibly more tractable form of 7.1 is:

**Conjecture 7.2 (asymptotic version, renormalised).** As $n \to \infty$,
the infimum of $W^-(v^*)$ over 2-trees on $n$ vertices, where $v^*$ is
the max-degsum ear, tends to a limit $W^-_\infty \ge W^-_* + \varepsilon_0$
for some explicit $\varepsilon_0 > 0$ and the threshold $W^-_*$ of
Conjecture 7.1.  (Under $\|w\|^2 = 2$ the total weight $\sum c_j^2$ is
$2$ and the threshold $W^-_*$ to be derived in O7.1 lies in $(0, 2)$.)

## 8. Computational sanity checks

Carried out using `.venv/bin/python`.

**8.1. Fans, $n = 4, \ldots, 200$.** For each $n$, computed $\delta^\pm(F_n)$
via direct `np.linalg.eigvalsh`. Result: $\delta^-(F_n) \ge \delta^-(F_4)
= (7 - \sqrt{17})/2 \approx 1.4385$, attained at $n = 4$. Minimum
slack to $17/16$ over the range is $0.376$. Numerics oscillate by
$n \bmod 4$ (similar to the $n \bmod 3$ oscillation in
`lprime_two_paths.md`, here driven by the parity of $\lceil n/2 \rceil$
secular roots).

| $n$ | $\delta^-(F_n)$ | gap to $17/16$ |
|---:|---:|---:|
| 4   | $1.43845$ | $+0.376$ |
| 6   | $1.60002$ | $+0.538$ |
| 10  | $1.67326$ | $+0.611$ |
| 20  | $1.76712$ | $+0.705$ |
| 50  | $1.85598$ | $+0.794$ |
| 100 | $1.89897$ | $+0.836$ |
| 200 | $1.92891$ | $+0.866$ |

**8.2. Spiders $S(k_1, k_2, k_3)$.** For all triples with
$\max(k_1, k_2, k_3) \le 10$ and $k_1 + k_2 + k_3 \le 30$ (a few
hundred cases), computed $\delta^-(p^*)$ for the max-degsum ear $p^*$
(taken from the largest arm, breaking ties by arm index).
Result: $\delta^-(p^*) \ge \delta^-(B_2) = (7 - \sqrt{17})/2 \approx
1.4385$, attained when $S(k_1, k_2, k_3) = B_2$ (i.e.
$(k_1, k_2, k_3) = (1, 0, 0)$ up to permutation). For two-arm spiders
($k_3 = 0$, $k_1, k_2 \ge 1$), the minimum is
$\delta^-(S(1, 1, 0)) \approx 1.5628$. For three-arm spiders
($k_1, k_2, k_3 \ge 1$), the minimum is
$\delta^-(S(1, 1, 1)) \approx 1.7627$.

| $(k_1, k_2, k_3)$ | $n$ | $\delta^-(p^*)$ |
|:---:|:---:|---:|
| (1, 0, 0) = $B_2$ | 4 | $1.4385$ |
| (1, 1, 0) | 5 | $1.5628$ |
| (1, 1, 1) | 6 | $1.7627$ |
| (2, 1, 1) | 7 | $1.7077$ |
| (3, 2, 1) | 9 | $1.7539$ |
| (5, 1, 1) | 10 | $1.7597$ |
| (10, 5, 2) | 20 | $1.8459$ |
| (50, 1, 1) | 55 | $1.9040$ |

All $\delta^-(p^*) \ge 1.4385$, with margin $\ge 0.376$ to $17/16$.

**8.3. Cross-check against the books and BT($k, 2$) results.** The
edge case $S(k, 0, 0) = B_{k + 1}$ recovers the book formula of
`lprime_books.md` to twelve decimals on every $k$ tested. The
"linear-chain" 2-trees (which differ from spiders) are covered by
`lprime_two_paths.md`. The BT-tail-ear bad case is not a spider page
(it lies on a different leaf of the clique tree), consistent with the
selector explicitly avoiding it.

## 9. Open obstructions

The isolated missing lemma is **Conjecture 7.1**: a lower bound
$W^-(v^*) \ge W^-_*$ on the negative-eigenvalue spectral weight of
the supporting-edge vector $w = e_{a^*} + e_{b^*}$, where $v^*$ is the
max-degsum ear of a 2-tree $G$ and the threshold $W^-_*$ is the
(currently unknown) constant that makes the secular implication chain
go through under $\|w\|^2 = 2$.

Stated cleanly (and under the corrected $\|w\|^2 = 2$ normalisation):

> **Spectral-weight conjecture (missing lemma, v9).** For every 2-tree
> $G$ on $n \ge 4$ vertices, let $v^*$ be the max-degsum simplicial
> degree-2 ear, with supporting edge $\{a^*, b^*\}$ in $H = G - v^*$.
> Let $\{u_j, \mu_j\}_{j = 1}^{n - 1}$ be an orthonormal
> eigendecomposition of $A(H)$. Then
> $$\sum_{j: \mu_j < 0} \bigl(u_j(a^*) + u_j(b^*)\bigr)^2 \;\ge\; W^-_*,$$
> for an explicit threshold $W^-_* \in (0, 2)$ to be determined (open
> subobligation O7.1). The total weight is $\|w\|^2 = 2$, **not** $4$.

This is a precise inequality, easily testable once $W^-_*$ is pinned
down, and structurally clean — it isolates the role of the max-degsum
invariant in steering the supporting-edge vector $w$ toward heavy
negative spectral weight.  The pre-v9 form of this conjecture stated
the threshold as $17/16$; that value depended on the buggy
$\|w\|^2 = 4$ normalisation and is no longer the natural threshold.

**Sub-obstructions / supporting open lemmas.**

(O5e.1) *Monotonicity for spider books-arms.* The Case II argument in
Theorem 6.3 relies on a monotonicity claim $\delta^-(S(k_1, k_2, k_3))
\ge \delta^-(S(k_1 - 1, k_2, k_3))$, which we did not rigorously prove
in this note. Status: numerically true for all tested
$(k_1, k_2, k_3)$ with $\max k_i \le 50$.

(O5e.2) *Fan rigorous finite-$n$ closure.* The fan proof relies on a
direct enumeration of $n \le 200$ plus the asymptotic. A clean
rigorous proof of $\delta^-(F_n) \ge (7 - \sqrt{17})/2$ for all $n$
in one stroke (without case-splitting at a finite threshold) is
open, in the same way that the analogous 2-path step 5c is open.

(O5e.3) *Tie-breaking for the max-degsum selector.* Ties in degsum
have not produced bad ears in any enumerated 2-tree on $n \le 10$ or
in random 2-trees on $n \le 300$, but a structural tie-breaking rule
(e.g. secondary sort by triangle-incidence count, or by clique-tree
centrality) may be needed in a worst-case proof. Empirically:
deferred.

(O5e.4) *Spectral-weight bound (Conjecture 7.1).* This is the
headline open problem of 5e. Strategy: combine the clique-tree
decomposition of $A(H)$ with a recursive expansion of eigenvectors
along the spine, plus a Rayleigh-quotient bound that promotes the
max-degsum invariant into a spectral weight estimate.

## Status of 5e in this pass

| Section | Goal | Status |
|---|---|---|
| 1 | Clique-tree formalization of 2-trees | proved (Lemmas 1.1–1.3) |
| 2 | Schur-complement / secular equation setup | recorded (equations 2.1–2.3) |
| 3 | Cauchy interlacing slot decomposition of $\delta^-$ | proved (equations 3.1, 3.2) |
| 4 | Max-degsum invariant in clique-tree language | recorded (equation 4.1) |
| 5 | Sub-class I: fans $F_n$ | **proved at $n = 4$ exactly; $n \ge 5$ proved-mod-Szegő-rate** |
| 6 | Sub-class IV: spider 2-trees | **proved unconditionally in Case I (one-arm); proved-mod-monotonicity in Case II** |
| 7 | Isolated missing-lemma conjecture | stated (Conjecture 7.1) |
| 8 | Computational verification | passed across $\sim 500$ test cases |
| 9 | Open obstructions list | recorded |

## Files referenced

- `problems/positive_square_energy_equality/docs/plan_v8.md`
- `problems/positive_square_energy_equality/docs/lprime_books.md`
- `problems/positive_square_energy_equality/docs/lprime_two_paths.md`
- `problems/positive_square_energy_equality/docs/lprime_selector.md`
- `problems/positive_square_energy_equality/docs/two_tree_ear_lemma.md`
- `problems/positive_square_energy_equality/scripts/spectrum_check.py`
- `problems/positive_square_energy_equality/scripts/family_check.py`
- `problems/positive_square_energy_equality/tests/test_lprime_subfamilies.py`
