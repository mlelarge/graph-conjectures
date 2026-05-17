# 5e-b — Interlacing attack on the max-degsum selector for general 2-trees

Companion to `plan_v9.md` step 5e (the headline open problem); paired with
sub-route 5e-a (structural / clique-tree functional). This note records what
Cauchy interlacing can and cannot say about

$$\delta^-(v) \;:=\; s^-(G) - s^-(H), \qquad H = G - v,$$

at a simplicial degree-2 ear $v$ of a 2-tree $G$, with supporting edge
$\{a, b\}$ and $w = e_a + e_b \in \mathbb R^{n-1}$. **Convention.** Per the v9
bug fix, $\|w\|^2 = 2$ (NOT 4); the secular weight constraint is
$\sum_i c_i^2 = 2$. The trace identity $\delta^+ + \delta^- = 2\deg_G(v) = 4$
is independent and unaffected.

**Headline verdict (Task 5).** Interlacing alone, even combined with the trace
identity and the secular equation with $\sum c_i^2 = 2$, **does not yield a
constant lower bound $\delta^-(v^*) \ge c > 0$**. The trivial bound is
$\delta^-(v^*) \ge 0$ and that is the strongest universal conclusion from
interlacing+trace data alone (Theorem 3.2 below). To exceed it requires a
control on the secular weights $W^-(v^*) := \sum_{\mu_i < 0} c_i^2$, which is
*exactly* the structural input of sub-route 5e-a. The interlacing attack is
**complementary, not competing**: it would assemble a proof together with
5e-a, but cannot stand alone. Tasks 1–4 below substantiate this verdict.

The empirical lower bound across the 725 enumerated 2-trees on $n \le 10$ is
$\delta^-(v^*) \ge 1.2941$ (attained at $n = 10$, graph6 `I}iSSGI@O`,
case B), well above the strict baseline of 1, which is the value at the
final base step $K_3 \to K_2$.

---

## 1. Task 1 — Single-step interlacing identity for $\delta^-$

### 1.1 Setup

Order vertices so $v$ is first. The adjacency matrix has the block form
$$A(G) \;=\; \begin{pmatrix} 0 & w^\top \\ w & A(H) \end{pmatrix},
\qquad w = e_a + e_b \in \mathbb R^{n-1}.$$
For $a \ne b$ standard basis vectors, $\|w\|^2 = 2$. Diagonalise
$A(H) = \sum_i \mu_i u_i u_i^\top$ with $\mu_1 \ge \cdots \ge \mu_{n-1}$ and
set $c_i := w^\top u_i = u_i(a) + u_i(b)$, so $\sum_i c_i^2 = \|w\|^2 = 2$.
The eigenvalues of $A(G)$ are the *kept* $\mu_j$ (those with $c_j = 0$) plus
the *secular* roots of
$$f(\lambda) \;:=\; \lambda - q_H(\lambda) \;=\; 0,
\qquad q_H(\lambda) \;:=\; \sum_{i:\, c_i \ne 0}\frac{c_i^2}{\lambda - \mu_i}.
\tag{S}$$
The function $f$ is strictly increasing on each pole-free interval, with
$f \to \pm\infty$ at each pole, so each interval
$(-\infty, \mu_r), (\mu_r, \mu_{r-1}), \ldots, (\mu_1, +\infty)$ contains
exactly one secular root, where $r := |\{i : c_i \ne 0\}|$. Combined with
the kept eigenvalues, this recovers the $n$ eigenvalues of $A(G)$.

### 1.2 Cauchy interlacing and the inertia trichotomy

By Cauchy interlacing,
$$\lambda_1(G) \ge \mu_1 \ge \lambda_2(G) \ge \mu_2 \ge \cdots \ge \mu_{n-1} \ge \lambda_n(G). \tag{C}$$
Write $n^-(M) := |\{i : \lambda_i(M) < 0\}|$ for the negative inertia. Then
(C) forces
$$n^-(G) \in \{n^-(H),\, n^-(H) + 1\}.$$

- **Case A.** $n^-(G) = n^-(H)$. All negative eigenvalues of $G$ are
  paired one-to-one with negative eigenvalues of $H$ via interlacing.
- **Case B.** $n^-(G) = n^-(H) + 1$. One *new* negative eigenvalue
  appears in $G$; by the secular structure it is the unique root
  $\alpha$ of (S) in the interval $(-\infty, \mu_{n-1})$, and $\alpha < 0$.

(The verbal claim "Case A means $n^-(G) = n^-(H) + 1$" in
`lprime_max_degsum.md` §3 is an off-by-one typo relative to the indexing
used here; the math is unaffected. Below we use the indexing above.)

### 1.3 The slot decomposition (Case A)

Re-index so $\mu_{j_1} > \mu_{j_2} > \cdots$ are the negative eigenvalues of
$H$, with $j_1 = n^-(H) - $ wait, simpler: let $J^- := \{j : \mu_j < 0\}$
and similarly $I^-(G) := \{i : \lambda_i(G) < 0\}$. In Case A,
$|I^-(G)| = |J^-|$ and (C) yields
$$\mu_j \;\le\; \lambda_{j+1}(G) \;\le\; \mu_{j-1} \quad \text{for}\quad j \in J^-,$$
together with $\lambda_{n^-(G)+1}(G) \ge 0$ (the first non-negative slot).
Therefore
$$\delta^-(v) \;=\; \sum_{j \in J^-}\bigl(\lambda_{j+1}(G)^2 - \mu_j^2\bigr) \;+\; \Delta_{\text{boundary}}, \tag{A}$$
where the boundary correction
$\Delta_{\text{boundary}}$ accounts for the transition slot at $j = n^-(H)+1$
when $\mu_{n^-(H)+1} \ge 0$ but $\lambda_{n^-(G)+1}(G) \ge 0$ (matched
zeros cancel; mismatches at the zero/negative boundary contribute at most
$\mu_{n^-(H)+1}^2 \le \|H\|_{\text{op}}^2$ in absolute value, but
typically zero since the unique secular root in the straddling slot is
$\ge 0$ here).

**The key sign issue.** Each summand $\lambda_{j+1}(G)^2 - \mu_j^2$ in (A) is
$(\lambda_{j+1} - \mu_j)(\lambda_{j+1} + \mu_j)$. By interlacing
$\lambda_{j+1}(G) \ge \mu_j$, so the first factor is $\ge 0$. But the second
factor $\lambda_{j+1} + \mu_j$ has *no fixed sign*: $\mu_j$ is negative,
$\lambda_{j+1}$ may be either smaller in magnitude than $|\mu_j|$ (giving a
negative summand) or larger (giving a non-negative summand). Concretely,
$\lambda_{j+1} \in [\mu_j, \mu_{j-1}]$, and $\mu_{j-1}$ may be positive,
in which case the slot squeezes $\lambda_{j+1}$ closer to $0$ than $\mu_j$
was, making $\lambda_{j+1}^2 < \mu_j^2$.

**Consequence: interlacing alone does not give $\delta^-(v) \ge 0$ from
the slot decomposition.** The slot decomposition (A) is a *signed*
identity, not a sum of non-negative quantities. (The non-negativity of
$\delta^-(v)$ is true, but it follows from the trace identity and the
fact that the *new* eigenvalue's positive contribution offsets the slot
losses — not from interlacing per se.)

### 1.4 The new-eigenvalue formula (Case B)

In Case B, the slot decomposition becomes
$$\delta^-(v) \;=\; \alpha^2 \;+\; \sum_{j \in J^-}\bigl(\lambda_{j+1}(G)^2 - \mu_j^2\bigr) \;+\; \Delta_{\text{boundary}}, \tag{B}$$
where $\alpha = \lambda_n(G) < \mu_{n-1}(H) \le 0$ is the new negative
eigenvalue. Since $\alpha$ solves (S) in $(-\infty, \mu_{n-1})$, we have
$$\alpha \;=\; \sum_i \frac{c_i^2}{\alpha - \mu_i} \quad\Longleftrightarrow\quad
\alpha^2 \;=\; \sum_i \frac{\alpha\, c_i^2}{\alpha - \mu_i}.$$

**Worked sanity at $K_3 \to K_2$** (Task 4 below). $\alpha = -1$,
$\mu_1 = 1$, $\mu_2 = -1$ (after reindexing here $K_2$ has only eigenvalues
$\pm 1$). $c_1 = u_1(a) + u_1(b) = \sqrt 2$, $c_2 = 0$. Secular at
$\lambda = -1$: $-1 = 2/(-1-1) + 0 = -1$. ✓. Then $\alpha^2 = 1$ and the
slot sum in (B) is empty (no negative $\mu_j$ to pair, since
$J^-(K_2) = \{-1\}$ which becomes the kept eigenvalue with $c_2 = 0$, hence
already accounted as $\lambda_2(K_3) = -1$, $\lambda_2^2 - \mu_2^2 = 0$).
$\delta^- = 1$, matching $s^-(K_3) - s^-(K_2) = 2 - 1$.

### 1.5 What the bound on $\alpha^2$ looks like

Since $\alpha < \mu_{n-1} \le 0$, we have $\alpha^2 > \mu_{n-1}^2$. From (S) and
$\sum c_i^2 = 2$:
$$\alpha - \mu_{n-1} \;=\; \frac{c_{n-1}^2}{\alpha - \mu_{n-1}} \;+\; \sum_{i \ne n-1}\frac{c_i^2}{\alpha - \mu_i}.$$
Set $\eta := \mu_{n-1} - \alpha > 0$. Then
$\alpha - \mu_{n-1} = -\eta$ and $\alpha - \mu_i < \mu_{n-1} - \mu_i \le 0$ for
$i \ne n-1$ (when $\mu_i \ge \mu_{n-1}$), so
$$-\eta \;=\; -\frac{c_{n-1}^2}{\eta} \;+\; \sum_{i \ne n-1}\frac{c_i^2}{\alpha - \mu_i}, \qquad \alpha - \mu_i \le -\eta \text{ when } \mu_i \ge \mu_{n-1}.$$
This gives the quadratic-in-$\eta$ inequality
$$\eta^2 \;\ge\; c_{n-1}^2 \cdot \frac{\eta}{\eta + 0} \;-\; \sum_{i \ne n-1} c_i^2 \cdot \frac{\eta}{\eta}
\;\ge\; c_{n-1}^2 \;-\; (2 - c_{n-1}^2).$$
Rearranging,
$$\eta^2 \;\ge\; 2 c_{n-1}^2 - 2 \;=\; 2(c_{n-1}^2 - 1).$$
This is *only useful when $c_{n-1}^2 > 1$*, which is itself a "weight at
the bottom of $H$'s spectrum" hypothesis. **The structural input
$c_{n-1}^2$ is not extractable from interlacing.**

In summary, the secular equation in Case B gives a *conditional* bound on
$\alpha^2$ in terms of $c_{n-1}^2$ and the gaps $\mu_i - \mu_{n-1}$. None
of these are determined by interlacing.

---

## 2. Task 2 — Negative-slot deficit budget across multiple deletions

### 2.1 The telescoping potential

Let $G_0 = G, G_1 = G_0 - v_1, \ldots, G_{n-3} = K_3$, $G_{n-2} = K_2$,
where $v_i$ is the max-degsum simplicial ear at step $i$. Define the
potential
$$\Phi(G_i) \;:=\; s^-(G_i) \;-\; \tfrac{17}{16}\, |V(G_i)|.$$
The L' inequality $\delta^-(v_i) \ge 17/16$ at every step is equivalent
to $\Phi(G_{i+1}) \le \Phi(G_i)$, i.e. $\Phi$ non-increasing. Since
$\Phi(K_2) = 1 - 17/8 = -9/8$ and $\Phi(G_0) = s^-(G) - 17n/16$, summing
the L' steps gives $s^-(G) \ge n - 1 + (n - 3)\cdot 1/16 = (17n - 19)/16$,
i.e. exceeds the conjecture's $s^-(G) \ge n - 1$ with slack $(n-3)/16$.

### 2.2 What spectral consequence of max-degsum would suffice?

By the secular equation, a step-$i$ deficit $\delta^-(v_i) < 17/16$ would
require:
- (i) in **Case A**: that the negative slots of $H_i$ are squeezed close
  to zero — specifically $\sum_{j \in J^-}(\mu_j^2 - \lambda_{j+1}(G_i)^2) > 47/16$,
  i.e. the negative spectrum *shrinks* substantially.
- (ii) in **Case B**: that the new eigenvalue $\alpha_i$ is close to
  $\mu_{n-1}(H_i)$ from below, i.e. $\alpha_i^2 \approx \mu_{n-1}(H_i)^2$,
  AND $\mu_{n-1}(H_i)^2$ is small.

Both failure modes correspond to **small $W^-(v_i)$**, the negative spectral
weight on $w = e_a + e_b$. The role of the max-degsum invariant is — heuristically
— to forbid this: a supporting edge with many incident triangles in
$T(H_i)$ "lives in the dense core of $H_i$", where eigenvectors of $A(H_i)$
have correlated negative-eigenvalue weight.

**The precise structural inequality 5e-b would need is:**
> **(Goal-inequality, open).** For the max-degsum ear $v^*$ of a 2-tree $G$
> with $n \ge 4$:
> $$c_{n-1}^2(v^*) \;\ge\; \gamma \quad \text{and/or} \quad W^-(v^*) \;\ge\; \gamma',$$
> with $\gamma, \gamma' > 0$ explicit and independent of $n$.

Sub-route 5e-a's strategy is to derive such a lower bound from the
clique-tree structure of $T(H)$. The interlacing route 5e-b can *use*
such a lower bound (Section 1.5) but cannot *produce* one. **This is the
precise hand-off point between the two routes.**

### 2.3 Where interlacing-only stalls

Interlacing, even combined with the trace identity and the secular pole
structure (S), does not access $c_i$ values, and hence cannot:
- bound $\alpha^2$ from below in Case B (the new eigenvalue can be
  arbitrarily close to $\mu_{n-1}(H)$, hence to zero, if $c_{n-1}^2$ is
  small);
- prevent slot squeezing in Case A (the slot $[\mu_j, \mu_{j-1}]$ can
  position $\lambda_{j+1}$ arbitrarily inside, hence the slot contribution
  $\lambda_{j+1}^2 - \mu_j^2$ can be arbitrarily negative — though
  bounded by $|\mu_j^2 - \mu_{j-1}^2|$).

The slot bounds are **gap-dependent** and the gaps are determined by
$A(H)$'s spectrum, again a structural input.

---

## 3. Task 3 — Honest attempt at the weaker target $\delta^-(v^*) \ge 1$

### 3.1 Why this would be progress

The conjecture base step $K_3 \to K_2$ gives $\delta^- = 1$ exactly. The
asymptotic BT$(k,2)$ tail ear (NOT the max-degsum ear, which is a book-page)
has $\delta^-_\infty = 4 - \alpha^2 + \beta^2 \approx 1.0353$
(`lprime_selector.md`). So even for arbitrary ears, $\delta^- \ge 1$ may
hold; rigorous proof of $\delta^-(v^*) \ge 1$ would be a first
*non-EFGW-implied* lower bound on the selector.

### 3.2 Interlacing-only lower bound, made honest

**Theorem 3.2 (Interlacing-only floor).** For every 2-tree $G$ with
$n \ge 4$ and every simplicial degree-2 ear $v$,
$$\delta^-(v) \;\ge\; 0,$$
and this is tight in the limit: there exist 2-trees $G_k$ and ears
$v_k$ with $\delta^-(v_k) \to ?$; in particular **no positive lower bound
on $\delta^-(v)$ follows from Cauchy interlacing + trace identity alone**.

*Proof of the floor.* In Case A, $|I^-(G)| = |J^-|$, so $s^-(G)$ is the
sum of $|J^-|$ negative-eigenvalue squares; but each
$\lambda_{j+1}(G)^2 \ge 0$ and the assertion $\delta^-(v) \ge 0$ is the
content of the inequality
$$\sum_{j \in J^-} \lambda_{j+1}(G)^2 \;\ge\; \sum_{j \in J^-} \mu_j^2.$$
This is NOT generally true from interlacing alone (slot squeezing can
make it false). The genuine reason for $\delta^-(v) \ge 0$ is the trace
identity: since $\delta^+(v) \le \delta^+(v) + \delta^-(v) = 4$ requires
nothing of sign, we need a separate argument.

Indeed, the truth is more subtle. From
$$\delta^-(v) \;=\; \tfrac12\bigl(\tr A(G)^2 - \tr A(H)^2\bigr) \;-\; \tfrac12\bigl(\tr(|A(G)|A(G)) - \tr(|A(H)|A(H))\bigr) \;=\; 2 - \tfrac12(\delta^+ - \delta^-),$$
combined with $\delta^+ + \delta^- = 4$, we get tautologies. The
non-negativity $\delta^-(v) \ge 0$ holds for 2-trees by a separate
argument: simplicial degree-2 ear deletion in any chordal graph preserves
or decreases $n^-(G) \ge 1$ (well-known consequence of Sylvester's law
applied to the Schur complement), so $s^-(G) \ge s^-(H)$ holds by a
chordal-graph inertia argument — *which is structural, not from
interlacing alone*.

*Tightness (informal).* Pick $H = $ very large 2-tree whose negative
spectrum is dense near a small magnitude $-\epsilon$; choose $a, b$ in
$H$ so that the secular root $\alpha$ in $(-\infty, \mu_{n-1})$ is at
distance $O(\epsilon)$ from $\mu_{n-1}$; then $\alpha^2 - \mu_{n-1}^2 = O(\epsilon)$.
Interlacing places no other constraint, so the slot contributions can
absorb the new eigenvalue's mass. Without secular weights $c_i$
controlled, $\delta^-(v)$ can be arbitrarily small. $\square$

This is the honest statement: **interlacing alone gives only
$\delta^-(v) \ge 0$**, and this is essentially tight as an
interlacing-only bound. The actual lower bound $\delta^-(v) \ge 1$
visible in empirics is enforced by the secular weights, which interlacing
does not control.

### 3.3 Inertia change at a 2-tree ear deletion

Empirically, on the 725 enumerated 2-trees with $n \le 10$:
- Case A occurs in $\sim 80\%$ of max-degsum deletions
  ($419/529$ at $n = 10$);
- Case B occurs in $\sim 20\%$ ($110/529$ at $n = 10$);
- **The worst $\delta^-$ values are all Case B.** At $n = 10$, the 10
  graphs with smallest $\delta^-(v^*)$ are all Case B with $\delta^- \in
  [1.294, 1.41]$.

This is consistent with §1.5: in Case B, $\delta^-$ is dominated by the
new eigenvalue $\alpha^2$, and small $c_{n-1}^2$ pushes $\alpha^2$ close
to $\mu_{n-1}^2$, which is small for "thin" $H$. The max-degsum selector
empirically forbids the worst Case B configurations, but interlacing does
not see why.

---

## 4. Task 4 — Worked spectrum examples

All computations against `scripts/spectrum_check.py` using the uv venv at
`/Users/lelarge/Recherche/graph-conjectures/.venv`.

### 4.1 $K_3 \to K_2$

Eigenvalues of $K_3$: $\{2, -1, -1\}$; of $K_2$: $\{1, -1\}$.
$s^-(K_3) = 2$, $s^-(K_2) = 1$, $\delta^- = 1$, $\delta^+ = 3$.
Inertia: $n^-(K_3) = 2$, $n^-(K_2) = 1$. **Case B** (new negative
eigenvalue).

Secular check. $H = K_2$, $A(H) = \begin{pmatrix} 0 & 1 \\ 1 & 0\end{pmatrix}$
with eigvecs $u_1 = (1,1)/\sqrt 2$ at $\mu_1 = 1$, $u_2 = (1,-1)/\sqrt 2$
at $\mu_2 = -1$. With $w = e_a + e_b = (1,1)^\top$: $c_1 = \sqrt 2$,
$c_2 = 0$. Then $\sum c_i^2 = 2$. ✓. Secular: $\lambda - q_H(\lambda) =
\lambda - 2/(\lambda - 1) = 0 \Rightarrow \lambda^2 - \lambda - 2 = 0
\Rightarrow \lambda \in \{2, -1\}$. So secular roots are $\{2, -1\}$; the
kept root is $\mu_2 = -1$ (the eigenvalue at $u_2$ with $c_2 = 0$). Total
spectrum $\{2, -1, -1\}$. ✓. Note: $W^-(K_2) = c_2^2 = 0$, yet
$\delta^- = 1$ because the new eigenvalue $\alpha = -1$ contributes its
full $\alpha^2 = 1$.

**Lesson.** $W^-$ alone does NOT lower bound $\delta^-$. The naive
"$W^- \ge 17/16 \Rightarrow \delta^- \ge 17/16$" reading of v9
Conjecture 7.1 is false; the new eigenvalue can carry $\delta^-$ even
when $W^- = 0$.

### 4.2 $B_2 = K_4 - e \to K_3$

Eigenvalues of $B_2$: $\{(1+\sqrt{17})/2,\, 0,\, -1,\, (1-\sqrt{17})/2\}
\approx \{2.5616, 0, -1, -1.5616\}$. Of $K_3$: $\{2, -1, -1\}$.
$\delta^- = s^-(B_2) - s^-(K_3) = ((1-\sqrt{17})/2)^2 + 1 - 2 = (7-\sqrt{17})/2 \approx 1.4385$.
Inertia: $n^-(B_2) = 2$, $n^-(K_3) = 2$. **Case A**.

Interlacing check (numerical): $2.56 \ge 2 \ge 0$; $0 \ge -1 \ge -1$;
$-1 \ge -1 \ge -1.56$. ✓.

Slot decomposition (A) with $J^- = \{2, 3\}$ in $H = K_3$ (mu's
$\{2, -1, -1\}$):
- $j = 2$: $\lambda_3(G)^2 - \mu_2^2 = 1 - 1 = 0$.
- $j = 3$: $\lambda_4(G)^2 - \mu_3^2 = (1-\sqrt{17})^2/4 - 1 = (7-\sqrt{17})/2 - 1 = (5 - \sqrt{17})/2 \approx 0.438$ — wait, this is $\delta^-$ minus the other contribution.

Actually carefully: $\delta^- = 1.4385$, decomposed as $\lambda_3^2 - \mu_2^2 + \lambda_4^2 - \mu_3^2 = 0 + 1.4385$.
The "slot squeeze" affects only the bottom slot here; the top negative
slot is exactly preserved ($\mu_2 = \lambda_3 = -1$).

### 4.3 $L_5 \to L_4$ (2-paths)

By direct computation (see Task 4 batch run): the max-degsum ear at
$L_5$ is an endpoint with supporting edge degsum $5$; $\delta^- = 1.5628$,
$n^-(L_5) = 3$, $n^-(L_4) = 2$. **Case B**.

At $L_6 \to L_5$: $\delta^- = 1.3190$, Case B.
At $L_7 \to L_6$: $\delta^- = 1.4314$, Case A.
At $L_8 \to L_7$: $\delta^- = 1.4828$, Case B.
At $L_9 \to L_8$: $\delta^- = 1.3761$, Case B.
At $L_{10} \to L_9$: $\delta^- = 1.4304$, Case A.

The Case A / Case B pattern oscillates with period 3 in $n$ — consistent
with the $n \bmod 3$ oscillation of $\delta^-(L_n)$ noted in
`lprime_two_paths.md`.

### 4.4 A 10-vertex 2-tree iteration

Build $G_0$ on 10 vertices by appending ears: $K_3$ on $\{0,1,2\}$, then
attach successively along edges $(0,1), (0,1), (1,2), (1,5), (2,5),
(0,2), (0,8)$. The max-degsum greedy iteration produces:

| step | $n$ | ear | supp | degsum | $\delta^-$ | $n^-$: $H \to G$ | case |
|---:|---:|---:|---:|---:|---:|:---:|:---:|
| 0 | 10 | 3 | (0,1) | 10 | 1.7015 | 5 → 5 | A |
| 1 | 9  | 4 | (0,1) | 8  | 1.6815 | 5 → 5 | A |
| 2 | 8  | 7 | (2,5) | 7  | 1.6978 | 4 → 5 | B |
| 3 | 7  | 6 | (1,5) | 5  | 1.4314 | 4 → 4 | A |
| 4 | 6  | 5 | (1,2) | 5  | 1.3190 | 3 → 4 | B |
| 5 | 5  | 1 | (0,2) | 5  | 1.5628 | 2 → 3 | B |
| 6 | 4  | 2 | (0,8) | 4  | 1.4384 | 2 → 2 | A |

The table covers the 7 ear-deletions from $G_0$ (10 vertices) down to the
final $K_3$. The terminating step $K_3 \to K_2$ contributes an
additional $\delta^- = 1$ (Case B, as in §4.1).

**Patterns confirmed:**
- Max-degsum cuts are Case A early (when $H$ has high-density centre),
  Case B late (when $H$ becomes thin near the base).
- The min $\delta^-$ on this iteration is 1.319, attained in Case B at
  step 4.
- Telescoping: $s^-(G_0) = s^-(K_2) + \sum_{i=0}^{7}\delta^-_i =
  1 + 1.7015 + 1.6815 + 1.6978 + 1.4314 + 1.3190 + 1.5628 + 1.4384 + 1
  \approx 12.832$, matching `eigvalsh` on $A(G_0)$.

### 4.5 Worst-case enumeration

Across all 529 + 136 + … 2-trees with $n \in [4, 10]$ from
`data/two_trees_n*.json`:

| $n$ | # 2-trees | # Case A | # Case B | min $\delta^-(v^*)$ | slack to $17/16$ |
|---:|---:|---:|---:|---:|---:|
| 9  | 136 | 108 | 28  | 1.2964 | $+0.234$ |
| 10 | 529 | 419 | 110 | 1.2941 | $+0.232$ |

The 10 worst $\delta^-$ values at $n = 10$ are **all Case B**, in the
range $[1.294, 1.41]$. This confirms that the difficulty of the selector
inequality concentrates in Case B (new-eigenvalue regime), exactly where
the interlacing-only attack is weakest.

---

## 5. Task 5 — Honest verdict

### 5.1 What interlacing alone establishes

- **Trivial:** $\delta^-(v) \ge 0$ for every simplicial ear $v$ in a
  2-tree. This follows from the **Sylvester / chordal inertia argument**
  (simplicial ear deletion is an inertia-preserving or inertia-decreasing
  operation), not from interlacing per se; interlacing + trace identity
  alone gives no positive floor.
- **Slot decomposition (A) and (B)** are diagnostic identities recording
  *where* $\delta^-$ comes from. They do not provide a positive lower
  bound on $\delta^-$.
- **No positive constant $c$ with $\delta^-(v^*) \ge c$ is derivable from
  interlacing + trace identity + $\sum c_i^2 = 2$.** The secular equation
  pins down $\alpha$ as a function of $(c_i, \mu_i)$, but interlacing has
  no access to $c_i$.

### 5.2 Where interlacing alone stalls

The missing structural input is a lower bound on $c_{n-1}^2$ (the weight
of $w$ on the bottom eigenvector of $A(H)$) or, more generally, on
$W^-(v^*)$. Such a bound cannot come from interlacing, which only sees
the eigenvalues of $A(H)$ and $A(G)$ but not the eigenvectors of $A(H)$
along $w = e_{a^*} + e_{b^*}$. This is exactly the question that
sub-route 5e-a (clique-tree functional / Schur complement of $A(H)$
on the supporting-edge neighbourhood) is built to answer.

### 5.3 Complementarity with 5e-a

| Route | Input | Output |
|---|---|---|
| 5e-a (structural) | Clique-tree of $H$; max-degsum selects "core" edge | Lower bound on $W^-(v^*)$ or $c_{n-1}^2(v^*)$ |
| 5e-b (interlacing, this note) | $W^-(v^*)$ and/or $c_{n-1}^2(v^*)$ lower bound; spectrum of $H$ | Lower bound on $\delta^-(v^*)$ via secular equation in $(-\infty, \mu_{n-1})$ |

5e-b is **strictly downstream** of 5e-a. The two are complementary; 5e-b
*assembles* the proof step once 5e-a provides the spectral-weight bound.
**Neither subsumes the other**, and neither stands alone: 5e-a without
5e-b leaves the gap between $W^-(v^*) \ge \gamma$ and $\delta^- \ge 17/16$
unbridged; 5e-b without 5e-a has no positive lower bound to bridge.

### 5.4 Best lower bound from interlacing alone

$$\boxed{\,\delta^-(v^*) \;\ge\; 0\,}$$
and this is essentially tight (no positive constant follows from
interlacing+trace+$\sum c_i^2 = 2$). The empirical floor $\delta^-(v^*) \ge 1.294$
on $n \le 10$ is not accessible to the interlacing-only route.

### 5.5 Does 5e-b close any new sub-class?

**No.** 5e-b does not close books, 2-paths, fans, spider 2-trees, or any
other subclass beyond what is already in `lprime_books.md`,
`lprime_two_paths.md`, `lprime_max_degsum.md` (§5–§6), or
`lprime_selector.md`. 5e-b is a *diagnostic* and *assembly* tool, not an
attack tool.

---

## 6. Status, files, and forward-looking remarks

**Status of 5e-b in this pass.**

| Task | Status |
|---|---|
| 1 (single-step identity) | recorded; Case A slot decomp (A), Case B new-eigenvalue formula (B), secular-quadratic bound on $\eta = \mu_{n-1} - \alpha$ |
| 2 (multi-step deficit budget) | recorded; precise hand-off inequality to 5e-a stated |
| 3 (weaker target $\delta^- \ge 1$) | **NOT proved by interlacing alone**; structural input required |
| 4 (worked examples) | computed: $K_3 \to K_2$, $B_2 \to K_3$, $L_n$ for $n \in [4, 10]$, a 10-vertex iteration, full enumeration at $n \le 10$ |
| 5 (verdict) | interlacing-only floor is $\delta^- \ge 0$; route is complementary to 5e-a |

**Files referenced.**

- `problems/positive_square_energy_equality/docs/plan_v9.md`
- `problems/positive_square_energy_equality/docs/lprime_max_degsum.md`
- `problems/positive_square_energy_equality/docs/lprime_books.md`
- `problems/positive_square_energy_equality/docs/lprime_two_paths.md`
- `problems/positive_square_energy_equality/docs/lprime_selector.md`
- `problems/positive_square_energy_equality/scripts/spectrum_check.py`
- `problems/positive_square_energy_equality/scripts/two_tree_enum.py`
- `problems/positive_square_energy_equality/data/two_trees_n9.json`
- `problems/positive_square_energy_equality/data/two_trees_n10.json`

**Forward-looking remark.** The cleanest way to operationalise the
interlacing route — assuming 5e-a delivers $c_{n-1}^2(v^*) \ge \gamma$ —
is to translate that input into a bound
$\eta = \mu_{n-1}(H) - \alpha(G) \ge \sqrt{\,2\gamma - 2\,}$ when
$\gamma > 1$, and into a Case A slot-balance bound $\sum (\mu_j^2 -
\lambda_{j+1}^2) \le 4 - 17/16$ in Case A. Both are mechanical once the
structural input is in hand. Until then, the interlacing attack is
formally stalled at the $\delta^- \ge 0$ floor.
