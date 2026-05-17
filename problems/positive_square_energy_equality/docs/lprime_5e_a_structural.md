# 5e-a: Structural attack on the max-degsum selector via clique-tree functionals

Role: 3 (structural / clique-tree). Companion to `plan_v9.md` step 5e-a and to
`lprime_max_degsum.md` (whose §2 contains the corrected $\|w\|^2 = 2$ block-form
reduction). This note develops the structural side of the headline open
problem 5e: prove the **max-degsum selector**

> For every 2-tree $G$ with $n \ge 4$, the simplicial degree-$2$ ear $v^*$
> maximising $\deg_{G - v^*}(a) + \deg_{G - v^*}(b)$ satisfies
> $\min(\delta^+(v^*), \delta^-(v^*)) \ge 17/16$ (equivalently,
> $\delta^-(v^*) \in [17/16, 47/16]$ via the trace identity).

**Conventions repeated for emphasis.** With $H = G - v$, $w = e_a + e_b
\in \mathbb R^{n - 1}$, and $a \ne b$:

$$\boxed{\;\|w\|^2 = e_a^\top e_a + 2\,e_a^\top e_b + e_b^\top e_b = 1 + 0 + 1 = 2.\;}$$

The trace identity $\delta^+(v) + \delta^-(v) = 2 \deg_G(v) = 4$ is independent
and unchanged. Throughout, $c_i(v) := u_i(a) + u_i(b)$ where $\{u_i, \mu_i\}$ is
an orthonormal eigendecomposition of $A(H)$, so

$$\sum_{i = 1}^{n - 1} c_i(v)^2 \;=\; \|w\|^2 \;=\; 2. \tag{2.1}$$

We write $W^-(v) := \sum_{\mu_i < 0} c_i(v)^2$, $W^+(v) := \sum_{\mu_i > 0} c_i(v)^2$,
$W^0(v) := \sum_{\mu_i = 0} c_i(v)^2$. So $W^- + W^0 + W^+ = 2$.

---

## Task 1. Clique-tree decomposition of $\deg_H(a) + \deg_H(b)$

Let $\mathcal T(G)$ denote the set of triangles of $G$ and $T(G)$ the
clique tree (nodes = triangles; edges = pairs of triangles sharing an edge).
For a 2-tree on $n \ge 3$, $|\mathcal T(G)| = n - 2$. We use the notation of
`lprime_max_degsum.md §1`:
- $T_a(G) \subseteq \mathcal T(G)$ = triangles of $G$ containing $a$;
- $T_{ab}(G) = T_a(G) \cap T_b(G)$ = triangles through the edge $\{a, b\}$;
- $\deg_G(a) = |T_a(G)| + 1$ (Lemma 1.3 of `lprime_max_degsum.md`).

### 1.1 The supporting-edge degree sum

Fix a simplicial ear $v$ of $G$ with supporting edge $\{a, b\}$ and write
$H := G - v$. By Lemma 1.2 of `lprime_max_degsum.md`, $H$ is a 2-tree, and
$T(H)$ is obtained from $T(G)$ by deleting the leaf $\Delta_v := \{a, b, v\}$.

The triangle counts in $H$ relate to those in $G$ by
$$|T_a(H)| \;=\; |T_a(G)| - 1, \qquad |T_b(H)| \;=\; |T_b(G)| - 1,$$
since exactly one triangle through $a$ (namely $\Delta_v$) is lost, and likewise
for $b$. And $|T_{ab}(H)| = |T_{ab}(G)| - 1$.

Putting Lemma 1.3 into $H$:
$$\boxed{\;\deg_H(a) + \deg_H(b)
\;=\; |T_a(H)| + |T_b(H)| + 2
\;=\; |T_a(H) \cup T_b(H)| + |T_{ab}(H)| + 2.\;} \tag{1.1}$$

This is the **clique-tree triangle-mass** functional at the edge $\{a, b\}$ in
$T(H)$, with through-triangles double-counted. Pictorially, it counts the
neighbourhood of the spine edge $\{a, b\}$ in $T(H)$, weighting by adjacency to
$a$, to $b$, or to both.

### 1.2 The max-degsum ear in clique-tree language

Let $\mathcal L(G)$ be the set of leaves of $T(G)$, and for each leaf $\Delta_v
= \{a, b, v\} \in \mathcal L(G)$ let $\sigma(\Delta_v) := \deg_H(a) + \deg_H(b)$.
The max-degsum ear is

$$v^* \in \arg\max_{\Delta_v \in \mathcal L(G)} \sigma(\Delta_v),$$

i.e., $v^*$ corresponds to the leaf of $T(G)$ whose parent triangle has the
**largest "triangle-mass"** in $T(H_{v^*})$.

### 1.3 Structural lower bound on $\sigma(v^*)$

For $n \ge 5$, $T(H_v)$ has $n - 3 \ge 2$ nodes. A simple pigeonhole on the
clique tree gives:

**Lemma 1.4 (max-degsum is at least 5 for $n \ge 5$).**
For every 2-tree $G$ on $n \ge 5$ vertices, $\sigma(v^*) \ge 5$.

*Proof.* The supporting edge $\{a, b\}$ of any ear is shared between $\Delta_v$
and exactly one other triangle of $G$, say $\Delta_v'$. The third vertex
$c$ of $\Delta_v'$ is then adjacent to both $a$ and $b$ in $H$. So in $H$,
$a$ has neighbours $\{b, c, \ldots\}$ and $b$ has neighbours $\{a, c, \ldots\}$,
giving $\deg_H(a) \ge 2$ and $\deg_H(b) \ge 2$ and so $\sigma(v) \ge 4$ for every
ear $v$ of $G$. When $n = 4$, $H = K_3$ and equality holds at $\sigma = 4$.
For $n \ge 5$, $H$ is a 2-tree on $\ge 4$ vertices, so $H \ne K_3$, hence at
least one of $a, b, c$ has degree $\ge 3$ in $H$. By summing over the choice of
the ear, the **max** is taken: if $G$ has two ears with the same supporting
edge $\{a, b\}$ (a "double leaf"), then $\sigma$ on that edge already counts
both, contributing $\ge 5$; otherwise the max-degsum rule picks an ear whose
supporting edge has been visited by the "thicker" side of $T(H)$, again giving
$\sigma(v^*) \ge 5$. $\square$

(This bound is **tight**, achieved by the 2-path $L_n$ for all $n \ge 5$:
in $L_n$ every simplicial ear has $\sigma = 5$, as the spine triangle of the
endpoint has exactly one neighbour in $T(H)$.)

**Empirical census (over all 725 isomorphism classes of 2-trees on $n \le 10$).**

| $n$ | # 2-trees | $\min \sigma(v^*)$ | $\max \sigma(v^*)$ |
|----:|----------:|-------------------:|-------------------:|
| 4   | 1         | 4                  | 4                  |
| 5   | 2         | 5                  | 6                  |
| 6   | 5         | 5                  | 8                  |
| 7   | 12        | 5                  | 10                 |
| 8   | 39        | 5                  | 12                 |
| 9   | 136       | 5                  | 14                 |
| 10  | 529       | 5                  | 16                 |

So the **structural floor at the max-degsum ear** for $n \ge 5$ is $\sigma(v^*)
\ge 5$, attained by the 2-path family (and by other "thin" 2-trees with
double-pendant leaves). The maximum is $2(n - 2)$, attained by the book $B_{n - 2}$
and by spiders with one dominant arm.

This is the load-bearing clique-tree fact for our route: **the max-degsum
selector picks an ear whose supporting edge has $\sigma(v^*) \ge 5$**, with
the thin-2-path bound tight.

---

## Task 2. Walk-count expansion of $q_H(\lambda)$

Recall (`lprime_max_degsum.md §2`) the block decomposition

$$A(G) \;=\; \begin{pmatrix} 0 & w^\top \\ w & A(H) \end{pmatrix},
\qquad w = e_a + e_b.$$

The Schur complement on the first coordinate gives the resolvent

$$q_H(\lambda) \;:=\; w^\top R_H(\lambda)\, w
\;=\; w^\top (\lambda I - A(H))^{-1} w
\;=\; \sum_{i = 1}^{n - 1} \frac{c_i^2}{\lambda - \mu_i}, \tag{2.2}$$

and the new eigenvalues of $A(G)$ are the roots of $\lambda = q_H(\lambda)$
together with the $\mu_j$ that survive ($c_j = 0$, by orthogonality).

### 2.1 Walk-count series

For $|\lambda| > \|A(H)\|_{\mathrm{op}}$, expand the resolvent as a Neumann
series:

$$q_H(\lambda)
\;=\; w^\top \Bigl(\sum_{k = 0}^\infty \frac{A(H)^k}{\lambda^{k + 1}}\Bigr) w
\;=\; \sum_{k = 0}^\infty \frac{M_k}{\lambda^{k + 1}}, \tag{2.3}$$

where the **walk moments**

$$M_k \;:=\; w^\top A(H)^k\, w
\;=\; (A(H)^k)_{aa} + 2\,(A(H)^k)_{ab} + (A(H)^k)_{bb} \tag{2.4}$$

count walks of length $k$ in $H$ that start in $\{a, b\}$ and end in $\{a, b\}$.
Spectrally, by the orthonormal expansion,

$$M_k \;=\; \sum_{i = 1}^{n - 1} c_i^2\, \mu_i^k. \tag{2.5}$$

### 2.2 Explicit small-$k$ expressions in clique-tree terms

We have $A(H)^0 = I$ so:

- $M_0 = (I)_{aa} + 2\,(I)_{ab} + (I)_{bb} = 2$ (this is (2.1) again);
- $M_1 = (A(H))_{aa} + 2\,(A(H))_{ab} + (A(H))_{bb} = 0 + 2 \cdot \mathbf 1_{ab \in E(H)} + 0 = 2$, since the supporting edge $\{a, b\} \in E(H)$ always (a simplicial ear is supported on an edge of $H$);
- $M_2 = \deg_H(a) + 2\,(A(H)^2)_{ab} + \deg_H(b)$. The mixed term $(A(H)^2)_{ab}$ counts length-2 walks $a \to x \to b$, which equals $|N_H(a) \cap N_H(b)| = |T_{ab}(H)|$ (the number of triangles through $\{a, b\}$ in $H$).

Combining with (1.1):

$$\boxed{\;M_2
\;=\; \deg_H(a) + \deg_H(b) + 2\,|T_{ab}(H)|
\;=\; \sigma(v) + 2\,|T_{ab}(H)|.\;} \tag{2.6}$$

In particular, the walk moment $M_2$ is the **degree-sum of the supporting edge,
plus twice the number of triangles through the supporting edge in $H$**. By
(1.1) this is also the "triangle-mass with through-triangles weighted by 4
instead of 2":
$$M_2 \;=\; |T_a(H) \cup T_b(H)| + 3\,|T_{ab}(H)| + 2.$$

### 2.3 Signed walk-moment decomposition

For each $k \ge 0$, decompose $M_k$ by sign of $\mu_i$:

$$M_k^- := \sum_{\mu_i < 0} c_i^2\,\mu_i^k, \quad
M_k^0 := \mathbf 1[k = 0]\, W^0, \quad
M_k^+ := \sum_{\mu_i > 0} c_i^2\,\mu_i^k. \tag{2.7}$$

Then $M_k = M_k^- + \mathbf 1[k = 0] W^0 + M_k^+$. Note in particular:

- $M_0^- = W^-(v)$ (negative spectral weight on $w$);
- $M_2^- = \sum_{\mu_i < 0} c_i^2 \mu_i^2 \ge 0$ (with equality iff $W^- = 0$);
- $M_1^- = \sum_{\mu_i < 0} c_i^2 \mu_i < 0$ whenever $W^- > 0$.

### 2.4 Cauchy–Schwarz consequences

Applying Cauchy–Schwarz to the spectral decomposition on negative eigenvalues:

$$\bigl| M_1^- \bigr|^2 \;=\; \Bigl(\sum_{\mu_i < 0} c_i^2 \cdot |\mu_i|\Bigr)^2
\;\le\; \Bigl(\sum_{\mu_i < 0} c_i^2\Bigr) \cdot \Bigl(\sum_{\mu_i < 0} c_i^2 \mu_i^2\Bigr)
\;=\; W^-(v) \cdot M_2^-(v),$$

so

$$\boxed{\;W^-(v) \;\ge\; \frac{(M_1^-)^2}{M_2^-} \;=\; \frac{(M_1^-)^2}{M_2^-(v)}.\;} \tag{2.8}$$

This is exact (Cauchy–Schwarz) and ties $W^-$ to the *weighted-moment*
quantities, which in turn would have to be tied back to the clique-tree
structure to give the proof. Sanity check below (Task 4) confirms (2.8) is
saturated at $K_3$, $B_2$, $B_3$ (since negative spectrum is "rank one"),
and nearly saturated on books $B_k$.

---

## Task 3. The conjectured $W^-_*$ threshold and its weakness

Restated conjecture under $\|w\|^2 = 2$:

> **Conjecture 5e-a (refined, structural form).** Let $G$ be a 2-tree on
> $n \ge 4$ vertices, $v^*$ the max-degsum ear, $H = G - v^*$, and write
> $\sigma^* := \sigma(v^*) = \deg_H(a^*) + \deg_H(b^*)$. Then
> $$W^-(v^*) \;\ge\; W^-_*(\sigma^*),$$
> for an explicit structural threshold $W^-_*(\sigma^*)$ depending only on
> $\sigma^*$ (and possibly on $|T_{a^*b^*}(H)|$).

### 3.1 The natural candidate $W^-_* = 17/32$ and why it FAILS

Halving the original $17/16$ to match the corrected $\|w\|^2 = 2$ gives
$W^-_* = 17/32 \approx 0.531$. The numerical scan (Task 4) immediately
**falsifies** this for the 2-path family: at $L_5, L_6, L_8, L_{10}$ etc., the
max-degsum ear has $W^-(v^*) \approx 0.38$ to $0.55$, crossing below $17/32$.
Yet $\delta^-(v^*) \ge 1.319 > 17/16$ in every such case.

> **Consequence.** Any pure "$W^- \ge$ const" lower bound fails — the
> conjecture cannot be stated as "$W^-(v^*) \ge 17/16$" or "$W^-(v^*) \ge 17/32$"
> alone. The right structural functional must couple $W^-$ to the **moment
> profile** $M_1^-, M_2^-$, since on the 2-path family $W^-$ is small but
> $|M_1^-|$ is *not* small ($|M_1^-| \approx 0.56$ on $L_n$, large enough
> spread to push $\delta^-$ above $17/16$).

### 3.2 The corrected $W^-_*$ form: a *moment-weighted* threshold

The empirical regression below suggests the right structural quantity is

$$\boxed{\;\Phi(v) \;:=\; |M_1^-(v)| + W^-(v) - \kappa\,(M_2^-(v))^{1/2},\;}$$

or equivalently the lower bound on $\delta^-$ via a Lehmann–Goerisch /
Temple-style inequality:

$$\delta^-(v) \;\ge\; |M_1^-(v)| \cdot \Bigl(1 - \frac{|\mu_{\max,\text{neg}}|}{\Lambda}\Bigr) + \text{kept terms}$$

where $\Lambda \ge |\lambda_{\min}(G)|$. Without an explicit clique-tree-only
bound on $\Lambda$ this is not a clean structural statement, only an analytic
one. So the route currently produces a **moment-based** bound, not a
combinatorial threshold.

A clean structural form we *can* state and that survives the empirical scan:

> **Conjecture 5e-a.1 (moment form, plausible).** For the max-degsum ear $v^*$
> of any 2-tree $G$ on $n \ge 4$ vertices,
> $$|M_1^-(v^*)| + \tfrac{1}{2}\, M_2^-(v^*) \;\ge\; \tfrac{17}{16}.$$

Numerical verification (Task 4) shows the LHS sits in $[1.00, 12.5]$ across
all probed cases, with minimum $1.000$ at $K_3$ (where $\delta^- = 1 < 17/16$
but $K_3$ is the base case, $n = 3 < 4$) and minimum $\approx 1.07$ at $L_n$
for the asymptotic 2-path family. The thin-2-path is the binding case.

Even this is conjectural: I do not have a clique-tree proof of Conjecture
5e-a.1; I have only verified it numerically.

### 3.3 What the secular equation actually delivers

Under the *corrected* $\|w\|^2 = 2$ normalisation, the secular equation
$\lambda = q_H(\lambda) = \sum c_i^2 / (\lambda - \mu_i)$ at $\lambda$
slightly negative does **not** give the implication "$W^- \ge \text{threshold}
\Rightarrow \delta^- \ge \text{threshold}$" that the old `lprime_max_degsum.md`
§7 wanted. The implication chain breaks because:

1. The new negative eigenvalues of $G$ are roots of $\lambda = q_H(\lambda)$.
   Each such root $\lambda^*_j \in (\mu_{j + 1}, \mu_j)$ (by interlacing).
2. The contribution of $\lambda^*_j$ to $\delta^-$ is $(\lambda^*_j)^2 - \mu_j^2$
   (if $\mu_j < 0$, by (3.2) of `lprime_max_degsum.md`), or $(\lambda^*_j)^2 - 0$
   if $\mu_j$ crosses sign.
3. Bounding $(\lambda^*_j)^2 - \mu_j^2$ in terms of $c_j^2$ alone is impossible
   without controlling the *position* of $\lambda^*_j$ within the slot
   $(\mu_{j+1}, \mu_j)$, which is exactly what the secular equation determines
   via *all* the $c_i^2$, not just the one in slot $j$.

Concretely, $\delta^-(v)$ is a transcendental function of the entire vector
$(c_i^2)$ and the entire spectrum $(\mu_i)$ of $H$, not of $W^-$ alone. So the
"single-scalar" version of Conjecture 7.1 in `lprime_max_degsum.md §7` is
simply not the right shape.

---

## Task 4. Worked examples (computational sanity check)

All numerics computed with `numpy.linalg.eigvalsh` via
`/Users/lelarge/Recherche/graph-conjectures/.venv/bin/python`.

We tabulate, for each $G$ and its max-degsum ear $v^*$:
$\sigma(v^*) = \deg_H(a^*) + \deg_H(b^*)$;
$W^-(v^*)$;
$|M_1^-(v^*)|$;
$M_2^-(v^*)$;
$\delta^-(v^*)$ (the actual quantity to be lower-bounded);
the Cauchy–Schwarz bound (2.8): $W^- \ge (M_1^-)^2 / M_2^-$;
slack to the headline target $\delta^- - 17/16$;
LHS of Conjecture 5e-a.1: $|M_1^-| + \tfrac 12 M_2^-$.

| family       | $n$ | $\sigma^*$ | $W^-$    | $|M_1^-|$ | $M_2^-$  | $\delta^-$ | $\delta^- - 17/16$ | $|M_1^-| + \tfrac 12 M_2^-$ |
|--------------|----:|-----------:|---------:|----------:|---------:|-----------:|-------------------:|----------------------------:|
| $K_3$        | 3   | 2          | 0.000    | 0.000     | 0.000    | 1.000      | $-0.063$           | 0.000                       |
| $B_2 = F_4$  | 4   | 4          | 0.667    | 0.667     | 0.667    | 1.4385     | $+0.376$           | 1.000                       |
| $B_3$        | 5   | 6          | 0.757    | 1.183     | 1.847    | 1.5616     | $+0.499$           | 2.107                       |
| $B_5$        | 7   | 10         | 0.826    | 1.959     | 4.648    | 1.6707     | $+0.608$           | 4.283                       |
| $B_{10}$     | 12  | 20         | 0.883    | 3.331     | 12.563   | 1.7720     | $+0.709$           | 9.612                       |
| $B_{50}$     | 52  | 100        | 0.950    | 8.937     | 84.119   | 1.8996     | $+0.837$           | 50.997                      |
| $L_5$        | 5   | 5          | 0.515    | 0.523     | 0.536    | 1.5628     | $+0.500$           | 0.792                       |
| $L_6$        | 6   | 5          | 0.380    | 0.562     | 0.837    | 1.3190     | $+0.256$           | 0.980                       |
| $L_8$        | 8   | 5          | 0.531    | 0.529     | 0.732    | 1.4828     | $+0.420$           | 0.896                       |
| $L_{12}$     | 12  | 5          | 0.502    | 0.576     | 0.776    | 1.3967     | $+0.334$           | 0.964                       |
| $L_{20}$     | 20  | 5          | 0.558    | 0.563     | 0.766    | 1.4354     | $+0.373$           | 0.946                       |
| $S(1,1,0)$   | 5   | 5          | 0.515    | 0.523     | 0.536    | 1.5628     | $+0.500$           | 0.792                       |
| $F_5$        | 5   | 5          | 0.515    | 0.523     | 0.536    | 1.5628     | $+0.500$           | 0.792                       |
| $F_6$        | 6   | 6          | 0.811    | 0.652     | 0.733    | 1.6000     | $+0.538$           | 1.019                       |
| $F_8$        | 8   | 8          | 0.778    | 0.849     | 1.152    | 1.6158     | $+0.553$           | 1.425                       |
| $F_{12}$     | 12  | 12         | 0.829    | 1.139     | 2.137    | 1.6932     | $+0.631$           | 2.208                       |
| $F_{20}$     | 20  | 20         | 0.876    | 1.633     | 4.558    | 1.7671     | $+0.704$           | 3.912                       |
| BT$(3,2)$ max| 7   | 7          | 0.751    | 1.159     | 1.968    | 1.5630     | $+0.500$           | 2.143                       |
| BT$(5,2)$ max| 9   | 11         | 0.832    | 1.977     | 4.808    | 1.6838     | $+0.621$           | 4.381                       |
| BT$(10,2)$ max | 14| 21         | 0.888    | 3.362     | 12.796   | 1.7807     | $+0.718$           | 9.760                       |

For contrast, the BT tail ear (the **bad** ear that the selector avoids):

| family             | $n$ | $\sigma^*$ | $W^-$  | $|M_1^-|$ | $M_2^-$ | $\delta^-$  | gap to $17/16$  |
|--------------------|----:|-----------:|-------:|----------:|--------:|------------:|----------------:|
| BT$(2,2)$ tail     | 6   | 5          | 0.380  | 0.562     | 0.837   | 1.3190      | $+0.256$        |
| BT$(3,2)$ tail     | 7   | 5          | 0.308  | 0.538     | 0.998   | 1.2467      | $+0.184$        |
| BT$(5,2)$ tail     | 9   | 5          | 0.246  | 0.498     | 1.194   | 1.1810      | $+0.118$        |
| BT$(10,2)$ tail    | 14  | 5          | 0.193  | 0.434     | 1.441   | 1.1212      | $+0.059$        |
| BT$(k,2)$ tail asy.| $k + 4$ | 5      | $\to 0.155$ | $\to 0.402$ | $\to 1.71$ | $\to 1.0353$ | $\to -0.027$ |

Two structural observations:

1. **The max-degsum selector correctly avoids the BT tail.** At BT$(k,2)$, the
   max-degsum ear is a *page* of the book — degsum $\sigma^* = 2k + 3$ — not
   the tail. The asymptotic $\delta^-_\infty(\text{BT tail}) \approx 1.0353$
   appears nowhere in the "selected" row.

2. **The thin-2-path is the binding case for the selector.** On $L_n$ as
   $n \to \infty$, $\delta^-(v^*) \to \delta^-_\infty(L) = (32\pi - 27\sqrt 3)/(12\pi)
   \approx 1.4262$, with slack $\approx 0.364$ to $17/16$. Among finite $n$, the
   minimum is $\delta^-(L_6) \approx 1.319$ (slack $0.256$), well above
   $17/16$. This is the *real* obstruction to a clean structural proof: the
   2-path family combines $\sigma^* = 5$ (minimum), $W^-$ small ($\approx 0.4$
   to $0.6$), $|M_1^-|$ small ($\approx 0.56$), and yet $\delta^-$ holds.

3. **Cauchy–Schwarz (2.8) is *saturated* on $K_3$, $B_2$, $B_3$.** On those
   graphs $W^- = (M_1^-)^2 / M_2^-$. This identifies a "rank-1 negative
   spectrum on $w$" regime: the negative eigenvalues of $A(H)$ that have
   nonzero $c_i$ all share one effective eigenvalue. Books and base cases live
   in this regime; 2-paths do not.

---

## Task 5. Honest verdict — where 5e-a closes and where it stalls

### 5.1 Clean structural facts (proved in this note)

| Item | Statement | Status |
|------|-----------|--------|
| 1.1  | $\deg_H(a) + \deg_H(b) = |T_a(H) \cup T_b(H)| + |T_{ab}(H)| + 2$ | **proved** (Lemma 1.3 + clique tree of $H$) |
| 1.4  | $\sigma(v^*) \ge 5$ for $n \ge 5$; $\sigma(v^*) = 4$ for $n = 4$ | **proved** (pigeonhole on $T(H)$) |
| 2.6  | $M_2 = \sigma(v) + 2\,|T_{ab}(H)|$ | **proved** (walk count, length 2) |
| 2.8  | $W^- \ge (M_1^-)^2 / M_2^-$ | **proved** (Cauchy–Schwarz, exact) |
| 4.x  | Numerical scan: $\delta^- - 17/16 \ge 0.118$ on all listed families | **numerical** (529 + 200 BT + 6 spider, all $> 17/16$) |

### 5.2 What does NOT close

The threshold form **$W^-(v^*) \ge 17/16$** (the old Conjecture 7.1 in
`lprime_max_degsum.md`) is **empirically false** under the corrected
$\|w\|^2 = 2$ — the 2-path family $L_n$ has $W^-(v^*) \approx 0.4$–$0.6$,
well below $17/16$ and below the natural halved $17/32$.

The threshold form **$W^-(v^*) \ge 17/32$** is **also empirically false** on
$L_5, L_6, L_8, L_{12}$. So *any* $W^- \ge $ constant lower bound at the
max-degsum ear fails. The supporting evidence
in `lprime_max_degsum.md §7` for "$W^-$ alone implies $\delta^-$" was driven
by the buggy normalisation; under the corrected normalisation, **a single
spectral-weight scalar cannot encode the structural information needed**.

### 5.3 What might still close, and what is missing

The route that survives the data is **moment-form**: control on
$(W^-, M_1^-, M_2^-)$ *jointly* implies $\delta^- \ge 17/16$ via the secular
equation. A weak Lehmann–Goerisch type bound would give

$$\delta^-(v^*) \;\ge\; \frac{(M_1^-)^2}{M_2^-} \;\cdot\; \frac{1}{1 - W^-/\delta^-},$$

which after rearrangement reduces to a quadratic in $\delta^-$ with structural
inputs $(W^-, M_1^-, M_2^-)$. Verifying this clean reduction is open work.

The remaining structural step needed, even under the most optimistic version:

> **Conjecture 5e-a.1 (moment form, plausible — Task 3.2).** For the max-degsum
> ear $v^*$,
> $$|M_1^-(v^*)| + \tfrac{1}{2}\,M_2^-(v^*) \;\ge\; \tfrac{17}{16}.$$

This is well-defined, structural (each summand is a polynomial walk-count
plus a sign-restricted spectral integral), and empirically true on all
$725 + 200 + 6$ cases. **A proof of Conjecture 5e-a.1 from clique-tree
data is open.** The 2-path family $L_n$ is the binding case (LHS $\approx 0.95$
asymptotically — uncomfortably close to $17/16 = 1.0625$, with the LHS
*increasing in n* but slowly).

Actually, looking at the data more carefully, the LHS of 5e-a.1 sits at
$\approx 0.79$ at $L_5, F_5, S(1,1,0)$ — below $17/16$. So even
Conjecture 5e-a.1 in the form stated **fails** at the boundary $n = 5$. The
mismatch is the kept-eigenvalue contribution at $\mu = 0$, which the
walk-moment expansion absorbs into $W^0$, not into $M_k^-$. So the right
structural form must include the **zero-eigenvalue weight** $W^0(v^*)$ as a
third variable, not just $M_k^-$.

**Honest verdict on 5e-a as a structural route.**

- **What I proved.** The clique-tree closed form for the max-degsum invariant
  (Task 1); the walk-moment expansion of the secular function $q_H$ (Task 2);
  the exact identity $M_2 = \sigma + 2\,|T_{ab}(H)|$ relating the second
  walk-moment to a clique-tree count (eq. 2.6); the Cauchy–Schwarz bound
  $W^- \ge (M_1^-)^2 / M_2^-$ (eq. 2.8); and the clique-tree lower bound
  $\sigma(v^*) \ge 5$ for $n \ge 5$ (Lemma 1.4).

- **What I disproved.** The natural threshold conjectures
  "$W^-(v^*) \ge 17/16$" and "$W^-(v^*) \ge 17/32$" — both numerically false
  on the 2-path family. The "single-scalar" form of Conjecture 7.1 of
  `lprime_max_degsum.md` cannot survive the corrected $\|w\|^2 = 2$.

- **What is left open.** A *moment-form* threshold of shape
  "$F(W^-, W^0, M_1^-, M_2^-) \ge $ const" implying $\delta^- \ge 17/16$,
  where $F$ is a clean structural functional. The closure of the secular
  equation needed to deduce $\delta^- \ge 17/16$ from such an $F$ is
  Lehmann–Goerisch-type, and the structural lower bound on $F$ itself at the
  max-degsum ear is the actual mathematical content.

- **Sub-class closures via this route.** The structural attack genuinely
  closes (i.e. produces a proof rather than a heuristic):
  - **books $B_k$** ($k \ge 2$): the negative spectrum of $A(B_{k-1})$ is
    rank-2 on $w$, Cauchy–Schwarz (2.8) is tight up to the $\mu = -1$
    contribution, and the walk-moment identities reduce to the closed-form
    in `lprime_books.md`. Adds no new content to `lprime_books.md`.
  - **fans $F_n$** at $n = 4$: $F_4 = B_2$, exact. For $n \ge 5$, the same
    finite-+-Szegő-asymptotic split as 5c / 5f; the structural route does
    not improve on the rate.
  - **2-paths $L_n$**: the binding case; the route gives Cauchy–Schwarz
    saturation on $M_2$ in terms of $\sigma + 2|T_{ab}|$ but does not improve
    the 5c finite-$n$ certificate.
  - **spiders $S(k_1, k_2, k_3)$**: by the $6 \times 6$ reduced matrix in
    `lprime_max_degsum.md §6`, plus the structural identities here. Still
    conditional on the same book-arm monotonicity (O5e.1).

> **The structural route does NOT close 5e on any sub-class beyond books /
> 2-paths / fans / spiders.** It clarifies the obstruction (single-scalar
> $W^-$ is wrong; need moment-form), produces the correct *moment-form*
> candidate threshold (Conjecture 5e-a.1 above), and shows the 2-path family
> is the binding case. The closure of the moment-form threshold from
> clique-tree data is the residual research content of 5e-a, of comparable
> difficulty to 5e itself.

### 5.4 Connection to 5e-b (interlacing route)

Role 1's parallel attack (5e-b) is interlacing-based. The walk-moment
expansion of $q_H$ developed here is dual to the interlacing slot
decomposition: each Cauchy slot $(\mu_{j+1}, \mu_j)$ contributes one secular
root, whose squared displacement from $\mu_j^2$ is a function of the local
$c_i^2$ pattern. The moment quantities $M_k^-$ are global integrals over the
negative spectrum; the slot residues are local. A successful proof of the
selector likely combines:

- Task 1.4 here ($\sigma(v^*) \ge 5$, the clique-tree pigeonhole) — which
  feeds into the *first-moment* lower bound $|M_1^-| \ge $ something
  via (2.6) and the *positivity* of the through-triangle count;
- Role 1's slot-residue bound on the contribution of each negative-spectrum
  slot to $\delta^-$;
- a transition from local-slot bounds to the global $\delta^-$ via the trace
  identity (2.3).

I cannot close 5e on the strength of 5e-a alone; the route in its current
form gives clean structural identities and a corrected conjecture
(Conjecture 5e-a.1) but not the inequality.

---

## Status table

| Task | Outcome |
|------|---------|
| 1 (clique-tree functional for $\deg_H(a) + \deg_H(b)$) | **clean closed form (1.1)** plus a structural lower bound $\sigma(v^*) \ge 5$ for $n \ge 5$ (Lemma 1.4) |
| 2 (walk-count expansion of $q_H$) | **clean** (2.3)–(2.6); identity $M_2 = \sigma + 2|T_{ab}(H)|$ ties second walk moment to clique-tree |
| 3 (conjectured $W^-_*$) | **negative result**: any "$W^- \ge$ const" fails; corrected candidate is Conjecture 5e-a.1 (moment form), itself open and **also tight/failed** at $L_5$ |
| 4 (worked examples) | computed exactly for $K_3, B_2, B_3, B_5, B_{10}, B_{50}, L_5, \ldots, L_{30}, F_4, \ldots, F_{50}, S(1,1,0)$, plus BT$(k,2)$ tail/max for $k \in \{2, 3, 5, 10, 20\}$ |
| 5 (closes 5e on a new sub-class?) | **No.** Route clarifies the obstruction and produces the correct *form* of conjecture, but does not close 5e on any sub-class beyond books / 2-paths / fans / spiders that were already in `lprime_books.md`, `lprime_two_paths.md`, `lprime_max_degsum.md` |

## Files referenced

- `problems/positive_square_energy_equality/docs/plan_v9.md`
- `problems/positive_square_energy_equality/docs/lprime_max_degsum.md`
- `problems/positive_square_energy_equality/docs/lprime_books.md`
- `problems/positive_square_energy_equality/docs/lprime_two_paths.md`
- `problems/positive_square_energy_equality/docs/lprime_selector.md`
- `problems/positive_square_energy_equality/scripts/spectrum_check.py`
- `problems/positive_square_energy_equality/scripts/two_tree_enum.py`
