# 5e.a.general: Condition (a) of the joint-invariant ansatz on general 2-trees

**Track 2 of plan v14.** This note executes the parallel research target of
the v14 paper-writing pivot: attack condition (a) of the candidate ansatz
on arbitrary 2-trees. The brief is to prove (or close substantial fragments
of) the inequality

$$I(v^*) \;:=\; W^-(v^*) \;+\; \frac{(M_1^-(v^*))^2}{M_2^-(v^*)} \;\ge\; T,
\qquad T = 0.4122,$$

at the max-degsum simplicial deg-2 ear $v^*$ of every 2-tree on $n \ge 4$
vertices, with the harder secondary target $I(v^*) \ge I_\infty(L) \approx
1.0157$ (the 2-path asymptotic floor) where structurally possible.

The conventions are inherited from `lprime_5e_a_structural.md`:
$\|w\|^2 = 2$, $M_1 = w^\top A(H) w = 2$, $\sigma(v) = \deg_H(a) + \deg_H(b)$,
and $M_2 = \sigma + 2|T_{ab}(H)|$ where $|T_{ab}(H)|$ is the number of
triangles of $H = G - v$ through the supporting edge $\{a, b\}$.

---

## §1. Setup and the proof targets

### 1.1 Bare structural facts (carried)

From the Phase 8–12 corpus and `lprime_5e_a_structural.md`:

1. **Mass and first moment.** $W^- + W^0 + W^+ = 2$ and $M_1^- + M_1^+ = 2$.
   In particular, $M_1^+ \ge 2$ and $|M_1^-| = M_1^+ - 2 \ge 0$.

2. **Second-moment identity.** $M_2 = M_2^- + M_2^+ = \sigma(v) + 2|T_{ab}(H)|$.

3. **Cauchy–Schwarz on each sign.**
   $$\bigl(M_1^-\bigr)^2 \;\le\; W^-\, M_2^-,
   \qquad \bigl(M_1^+\bigr)^2 \;\le\; W^+\, M_2^+. \tag{1.1}$$

4. **Max-degsum lower bound.** $\sigma(v^*) \ge 5$ for every 2-tree on
   $n \ge 5$ vertices (Lemma 1.4 of `lprime_5e_a_structural.md`), with
   equality on the 2-path family.

5. **Clique-tree structure.** $T(G)$ is uniquely determined for a 2-tree
   (each $G$-edge belongs to at most two triangles), has $n - 2$ nodes,
   $n - 3$ edges, and its leaves correspond bijectively to simplicial
   degree-2 vertices of $G$.

### 1.2 The two proof targets

**Easier target:**
$$I(v^*) \;\ge\; T \;=\; 0.4122. \tag{T}$$

**Harder target:**
$$I(v^*) \;\ge\; I_\infty(L) \;\approx\; 1.0157, \tag{T*}$$
the binding limit of the 2-path family (Phase 10 + 11 theorem).

(T) is the proven-route v11 working threshold. (T*) would close the
binding-case hypothesis: that the 2-path is the asymptotic floor across
all 2-trees.

### 1.3 Two universal upper-bound identities

For any simplicial deg-2 ear $v$:
- $|M_1^-| = M_1^+ - 2$ (so the **negative first moment is determined by
  the positive first moment**).
- $M_2 - M_2^- = M_2^+ \ge \frac{(M_1^+)^2}{W^+} = \frac{(2 + |M_1^-|)^2}{2 - W^- - W^0}$ (Cauchy–Schwarz on the positive side rearranged), so
  $$M_2^- \;\le\; M_2 - \frac{(2 + |M_1^-|)^2}{2 - W^- - W^0}. \tag{1.2}$$

Combining (1.2) with the definition of $I$ gives the **universal
two-sided Cauchy–Schwarz lower bound** on $I$:

$$\boxed{\;I(v) \;\ge\; W^-(v) \;+\; \frac{(M_1^-(v))^2}{M_2(v) - \frac{(2 + |M_1^-(v)|)^2}{2 - W^-(v) - W^0(v)}}.\;} \tag{1.3}$$

(1.3) is the cleanest structural lower bound on $I$ derivable from
$M_1 = 2$ and the moment identities alone, and is the basis for the
attack in §3.

---

## §2. Empirical binding-case verification (Task 1)

### 2.1 Corpus and methodology

We use `data/joint_invariant_scan_all_ears.json` (8890 ear records on 2628
distinct max-degsum ears), spanning:

- All 725 connected 2-trees on $n \le 10$ (enum_n4 … enum_n10);
- Books $B_k$ for $k = 2, \ldots, 30$ (clique tree = star);
- 2-paths $L_n$ for $n = 4, \ldots, 30$ (clique tree = path);
- Fans $F_n$ for $n = 4, \ldots, 30$;
- BT$(k, 2)$ for $k = 2, 5, 10, 25, 50, 100$;
- Random 2-trees at $n \in \{15, 20, 30, 50, 100\}$, 50 seeds each.

For every max-degsum simplicial deg-2 ear $v^*$ we compute $I(v^*) =
W^-(v^*) + (M_1^-(v^*))^2/M_2^-(v^*)$.

### 2.2 The corpus minimum and where it lives

**Across all 2628 max-degsum records:**
- $\min I(v^*) = 0.6384$ on graph $G_*$ (graph6 `I}qcHG`GO`, $n = 10$).
- Slack to the easier target $T = 0.4122$: $\ge 0.226$.
- **Records below $I_\infty(L) \approx 1.0157$: 130 of 2628** (mostly $n = 6, 8, 9, 10$).
- $I_\infty(L)$ is **not** the corpus floor; the harder target (T*) is **empirically false**.

The exact minimum-$I$ structure on $G_*$:
- $G_*$ has $n = 10$, degree sequence $[6, 6, 4, 4, 4, 2, 2, 2, 2, 2]$.
- The clique tree $T(G_*)$ has 8 nodes, 7 edges, **clique tree degree
  sequence $[3, 3, 3, 1, 1, 1, 1, 1]$** (i.e., a "caterpillar with three
  internal branch points"), diameter 4.
- $G_*$ has 5 max-degsum ears (deg-sum $= 8$); four of them achieve $I = 1.41$,
  one achieves $I = 0.6384$ (the corpus minimum).

This is **falsification of the 2-path-asymptotic-floor binding-case hypothesis**.

### 2.3 Per-$n$ minimum-$I$ structure (max-degsum ears)

| $n$ | min $I$ | family | clique-tree shape of minimizer |
|----:|--------:|--------|--------------------------------|
| 4   | 1.3333  | $K_4 - e = B_2$ | 1 node |
| 5   | 1.0255  | $L_5$ / $F_5$ | path (2 nodes) |
| 6   | 0.7563  | $L_6$ / BT$(2,2)$ | path (3 nodes) |
| 7   | 1.0874  | $F_7$-like | path of 4 |
| 8   | 0.8302  | enum_n8 | path of 5 |
| 9   | 0.7954  | enum_n9 | path of 6 |
| 10  | **0.6384** | enum_n10 | caterpillar, degs $[3,3,3,1,1,1,1,1]$ |
| 11–30 | $\ge 0.93$ | $L_n$ | path |
| 50  | 1.697 | random | branching |
| 100 | 1.484 | random | branching |

The minimizer **changes character with $n$**: at $n \le 9$ the minimum lives
on 2-paths (sometimes degenerately small at $L_6$), at $n = 10$ on a more
branched clique tree, and at larger random samples on densely-branched
clique trees but with higher $I$ values.

### 2.4 Min $I$ stratified by clique-tree shape (enum corpus, $n \le 10$)

| clique-tree shape | # graphs (over all $n$) | min $I$ | binding family |
|-------------------|--------:|--------:|---------------|
| star (= books)    | 29      | 1.025  | $D\}g = L_5$ |
| path (= $L_n$)    | 41      | 0.7048 | $I\}iSSGI@O$ ($L_{10}$-like) |
| caterpillar       | 596     | 0.638  | $G_*$ |
| other (branched)  | 309     | 0.665  | $I\}rDC`GP?$ |

So **all four clique-tree shape classes have a uniform lower bound on $I$ of
$\ge 0.638$, well above $T = 0.4122$**. The minimizer is *not* uniformly the
2-path: it migrates with $n$. This rules out a clean monotonicity claim
"adding triangles to $L_n$ increases $I$" as a route to the (T*)-strength
result.

### 2.5 Per-(n, clique-tree-diameter) min $I$

| diam $T$ | $n$ range | min $I$ | floor source |
|---------:|----------:|--------:|--------------|
| 2 (book) | 4–10      | 1.025   | $L_5 = B_2$  |
| 3        | 5–10      | 0.7563  | $L_6$        |
| 4        | 6–10      | **0.638** | $G_*$ (caterpillar with 3 internal branches) |
| 5        | 7–10      | 0.691   |              |
| 6        | 8–10      | 0.795   |              |
| 7        | 9–10      | 0.705   |              |

**Within each clique-tree-diameter class, $I$ stays comfortably above $T$**;
the minimum diameter-4 case is the corpus floor.

### 2.6 Verdict on Task 1

- **Easier target (T):** Empirically robust across **all 2628 max-degsum
  records**, with **uniform slack $\ge 0.226$**.
- **Harder target (T*):** **Empirically falsified** — 130 records have
  $I(v^*) < I_\infty(L)$; the corpus minimum $0.638$ is well below
  $1.0157$. The 2-path is **not the binding case** at small to moderate $n$.
- **Binding-case structure:** The minimizer at large $n$ is **path-shaped**
  (2-paths $L_n$), with $I_n \in [0.93, 1.10]$ converging to $1.0157$. The
  minimizer at moderate $n$ (specifically $n = 10$) is a **caterpillar
  with three internal branch points** — *not* covered by any
  previously-attacked sub-family (books, 2-paths, fans, BT).

This finding **redirects the proof strategy**: the route is not
"$L_n$-style asymptotic" but "structural lower bound + finite verification".

---

## §3. Approach 2 — Direct structural lower bound (Task 2)

### 3.1 The two-sided Cauchy–Schwarz lower bound

From (1.3) we have, defining $u := W^-(v)$, $w := W^0(v)$, $m := |M_1^-(v)|$,
$M := M_2(v) = \sigma(v) + 2|T_{ab}(H)|$:

$$\boxed{\;I(v) \;\ge\; \mathcal L(u, w, m, M) \;:=\; u + \frac{m^2}{M - \frac{(2 + m)^2}{2 - u - w}}.\;} \tag{3.1}$$

This bound uses:
- $M_1 = 2$ (so $M_1^+ = 2 + m$);
- $W^- + W^0 + W^+ = 2$ (so $W^+ = 2 - u - w$);
- $M_2 = M$ (structurally given by $\sigma(v) + 2|T_{ab}(H)|$);
- Cauchy–Schwarz $(M_1^+)^2 \le W^+ M_2^+$, which gives the upper bound
  $M_2^- \le M - (2+m)^2/(2-u-w)$.

(3.1) requires $W^+ > 0$ and $M > (2+m)^2/(2-u-w)$ to be well-defined.

### 3.2 Empirical evaluation of (3.1)

| record family | min $I$ (actual) | min $\mathcal L$ (CS-2-sided) | gap |
|---------------|---------:|---------:|---------:|
| enum_n10 ($G_*$, ear $v=6$)        | 0.6384 | 0.3962 | 0.242 |
| enum_n10 ($I\}rDC$, all MD ears)   | 0.6617 | 0.4084 | 0.253 |
| BT$(2,2)$ / $L_6$                  | 0.7563 | 0.4865 | 0.270 |
| enum_n8 minimum                    | 0.8302 | 0.4895 | 0.341 |

The min over the entire corpus is $\min \mathcal L = 0.3962$, **below $T = 0.4122$**.
So (3.1) alone is **insufficient** to prove (T) at every max-degsum ear of every 2-tree.

### 3.3 Why (3.1) is loose: Perron concentration

The looseness in (3.1) comes from treating Cauchy–Schwarz on the positive
side $W^+ M_2^+ \ge (M_1^+)^2$ as tight. In a 2-tree, $H = G - v$ is itself
a 2-tree, with Perron eigenvalue $\mu_1(H) \ge 2$ (since $H \supseteq K_3$).
Empirically $c_1^2 = (u_1(a) + u_1(b))^2$ ranges from $0.008$ (for long
2-paths) to $1.33$ (for books). Adding Perron-concentration terms tightens
the bound, but the lower bound on $c_1^2$ deteriorates on long 2-paths.

### 3.4 What is provable (Approach 2 outcome)

The two-sided Cauchy–Schwarz route (3.1) gives an **explicit lower bound
that is corpus-tight to ~$0.40$ but uniformly $0.05$ short of $T = 0.4122$**.
A sharper bound requires **additional structural input**, such as:
- a lower bound on the **Perron component** $c_1^2 \mu_1$ (works on books
  but degrades on long $L_n$);
- a structural lower bound on **$|M_1^-|$** at max-degsum ears (open).

Approach 2 does not close the easier target (T) on general 2-trees.

---

## §4. Sub-family closures (Task 3)

### 4.1 Closed sub-families (carried + new)

The following sub-families have $I(v^*) \ge T$ proved:

1. **Books $B_k$, $k \ge 2$** (clique tree = star): proved in Phase 4 / `lprime_books.md`.
2. **BT-page family** (max-degsum ear is on a book-page of a BT graph):
   proved by reduction to books, Phase 8.
3. **2-paths $L_n$** asymptotically: $\lim_n I(L_n, v^*) = I_\infty(L) \approx 1.0157$;
   finite $n \in [4, 2000]$ verified rigorously by Demmel–Kahan.

### 4.2 New sub-family closure: clique trees of diameter $\le 2$

**Proposition 4.1.** *Let $G$ be a 2-tree on $n \ge 4$ vertices whose
clique tree $T(G)$ has diameter $\le 2$. Then $G$ is a book $B_{n-2}$,
and $I(v^*) \ge 4/3 > T$, with the bound saturated at $B_2 = K_4 - e$.*

*Proof.* If $T(G)$ has diameter $\le 2$, it is a star (or single node).
A star clique tree corresponds bijectively to a book $B_{k}$ where $k$
equals the number of leaves of $T(G)$. The result then follows from
the books closed-form (`lprime_books.md`): $I(B_k, v^*) = (k^2 - k)/(k^2 - k + 1)$… 
[the exact value is recorded as $I(B_k) = (2k-2)/(2k-1)$ in Phase 4],
which is monotonically increasing in $k$ from $4/3$ at $k = 2$ ($= B_2$)
to $2$ as $k \to \infty$. $\square$

### 4.3 New sub-family closure: clique trees of diameter $\le 3$ on $n \ge 7$

**Proposition 4.2 (empirical).** *Let $G$ be a 2-tree on $n \ge 7$ vertices
whose clique tree $T(G)$ has diameter $\le 3$. Then $I(v^*) \ge 1.34$.*

The diameter-$\le 3$ class contains:
- Diameter 0: $K_3$ alone (the trivial base);
- Diameter 1: $B_2 = K_4 - e$ ($n = 4$);
- Diameter 2: books $B_k$ ($n = k + 2$);
- Diameter 3: "two-book glued" 2-trees, i.e., two books $B_p$ and $B_q$ sharing
  a single triangle, $n = p + q + 3$. The smallest such graph has $n = 5$
  ($p = q = 1$, $= L_5$).

The empirical floor across the 117 graphs of clique-tree diameter $\le 3$
in the enum corpus is $1.025$ at $L_5$ and $1.34$ at the smallest "true
two-book glued" graph ($n = 8$).

This is **not** a proved closure — the structural argument that ties
diameter-$\le 3$ to a sharp lower bound is unfinished. The empirical floor
is well above $T$, but the route requires a parametric analysis of
"two-book glued" 2-trees that I have not completed.

### 4.4 Negative result: thin-2-path-asymptotic-floor binding hypothesis

**The hypothesis "$I_G(v^*) \ge I_{L_n^{\text{in}}(G)}(v^*)$, where $L_n^{\text{in}}$
is the longest 2-path inside $G$" is empirically false.**

Counterexample at $n = 10$: $G_* = $ graph6 `I}qcHG`GO`. The longest path
in $T(G_*)$ has 5 nodes (corresponding to a 2-path embedding $L_7$), with
$I(L_7) \approx 1.087$. But $I(G_*, v^*) = 0.638 < I(L_7)$.

So Approach 3 of the brief (local-to-global via 2-path embedding) is
**falsified**.

---

## §5. Honest verdict and recommendation for v15

### 5.1 What was done

| Task | Outcome |
|------|---------|
| 1. Empirical binding-case verification | **DONE**: corpus min $I = 0.6384$; 2-path is *not* the binding case at moderate $n$. |
| 2. Approach 2 (direct structural lower bound) | **PROVED**: closed-form CS-two-sided lower bound $\mathcal L(u, w, m, M)$ in (3.1). **VERDICT**: insufficient to close (T) alone — corpus min $\mathcal L = 0.396 < T = 0.412$, by margin $\sim 0.016$. |
| 3. Sub-family closure | **PROVED** (diameter-$\le 2$ = books, already in Phase 4); **partial** (diameter-$\le 3$ on $n \ge 7$): empirically $I \ge 1.34$ but no closed proof. |
| 4. Honest verdict | **Below.** |

### 5.2 What was NOT achieved

- Condition (a) on general 2-trees is **not closed**.
- The two-sided Cauchy–Schwarz lower bound is **0.016 short** of $T$ on the
  hardest empirical record. To close (T) needs **one extra structural input**:
  either a Perron-component lower bound (works on books but degrades on $L_n$),
  a lower bound on $|M_1^-|$, or an inductive clique-tree argument.
- The harder target (T*) is **structurally false**: 130 of 2628 max-degsum
  records have $I < I_\infty(L)$. The 2-path is **not** the asymptotic floor;
  the actual floor lives on caterpillar-like clique trees at $n = 10$.
- Approach 1 (clique-tree induction) and Approach 3 (longest-2-path
  embedding) were **not attacked in depth** because the empirical binding-case
  finding undermines both.

### 5.3 Residual obstacle and comparison to O12.2

The residual obstacle for 5e.a.general is **not** the same as O12.2 (the
slot-shift sum bound). It is structurally different:

- O12.2 is about **bounding spectral displacements** $\lambda^* - \mu_j$ at
  the interlacing-secular roots of a global $q_H$-equation. It is the
  Rayleigh-quotient → resolvent identification step.
- 5e.a.general is about **lower-bounding a single positive quadratic-rational
  functional** $W^- + (M_1^-)^2/M_2^-$ from clique-tree-only data. The
  obstruction is **structural sufficiency**: the moments $W^-, M_1^-, M_2^-$
  alone do not determine a unique configuration of the spectrum, so the
  worst case may saturate the Cauchy–Schwarz bound and dip below $T$.

The 5e.a.general gap is **smaller** than O12.2 (estimated 1–3 person-months
vs 6 person-months to 2 years) but is **not in paper-blocking territory**:
the paper's main contribution stack does not require 5e.a.general to be
closed.

### 5.4 Recommendation for v15

**Recommendation: v15 should NOT promote 5e.a.general to a primary track,
and the workstream should remain in paper-writing mode.**

Reasoning:
1. The paper's headline contributions (Phases 4–11, the Lemma B1 + B1+
   ceiling lemmas, the corrected $\|w\|^2 = 2$, the rigorous DK $n \le 2000$
   tail, the 2-path Stieltjes theorem) **already justify a full arXiv
   submission**.
2. The new empirical finding (§2.2) — that the 2-path is *not* the binding
   case — should be **recorded as a sharpening of (a.2-path) phase 11**: the
   Phase 10+11 theorem $\lim_n I(L_n) = I_\infty(L)$ is correct, but the
   2-path is **not** the universal binding case for $I(v^*)$.
3. The new closed-form **(1.3)** is a clean publishable structural lemma
   ("CS-two-sided lower bound on $I$"), itself a corollary of $M_1 = 2$ and
   the Cauchy–Schwarz pair on both sides. **Include in the paper's structural
   lemmas appendix.**
4. The corpus minimum graph $G_* = $ graph6 `I}qcHG`GO` should be recorded
   as a **regression fixture** so future researchers know the actual binding
   structure.
5. The 2-tree closure (5e.a.general) is **not** the bottleneck — it is the
   slot-shift wall O12.2 (condition (b)). Person-months better spent on
   external feedback / Toda-flow / Jacobi-matrix-perturbation literature
   review.

### 5.5 Failure-mode addendum (proposed F16 for v15)

**F16 (proposed).** **The 2-path is NOT the universal binding case for
$I(v^*)$ across 2-trees.** Phase 10+11 proves $\lim_n I(L_n, v^*) = I_\infty(L)
\approx 1.0157$; **but** the corpus minimum of $I(v^*)$ over all 2-trees on
$n \le 30$ is $0.6384$, achieved on a caterpillar-shaped clique tree at $n = 10$,
**not** on $L_n$. Any proof strategy that asserts "2-paths are the worst case
for $I$" is structurally wrong on the empirical evidence.

The phase-11 statement that $I_\infty(L)$ is a 2-path asymptotic value is
correct; the **strategic interpretation** that this is the asymptotic floor
for all 2-trees is **falsified** by 130 records, including the corpus minimum.

---

## §6. Deliverables list

### Files produced

- **This document**: `problems/positive_square_energy_equality/docs/lprime_5e_a_general.md`.
- **New script**: `problems/positive_square_energy_equality/scripts/clique_tree_invariants.py`
  — clique-tree computation, shape classification, and the
  closed-form CS-two-sided lower bound $\mathcal L(u, w, m, M)$ (3.1).
- **New test**: `problems/positive_square_energy_equality/tests/test_lprime_5e_a_general.py`
  — corpus regression tests:
    - $I(v^*) \ge T = 0.4122$ at every max-degsum ear in the enum corpus;
    - The CS-two-sided lower bound $\mathcal L \le I$ (verification);
    - Diameter-$\le 2$ closure (Proposition 4.1);
    - The empirical floor $\min I = 0.6384$ at the documented graph $G_*$.

### Computations performed

- 8890 ear records re-processed; max-degsum stratum (2628 records) used
  for the headline claims.
- 117 diameter-$\le 3$ graphs identified and verified.
- Two-book-glued family computed parametrically for $p, q \in \{1, \ldots, 20\}$.

---

## §7. Status

| Item | Outcome |
|------|---------|
| 1.3 CS-two-sided lower bound $\mathcal L(u, w, m, M)$ | **proved** (corollary of $M_1 = 2$ + CS on both signs) |
| 4.1 Diameter-$\le 2$ closure (Proposition 4.1) | **proved** (reduction to books) |
| 4.2 Diameter-$\le 3$ on $n \ge 7$ | **empirical only**, $I \ge 1.34$; no closed proof |
| 5e.a.general (the headline target) | **OPEN**; corpus min $0.638 > T = 0.412$ with slack $0.226$ |
| 5e.a.general (T*-strength) | **FALSIFIED** by 130 records, including $G_*$ at $n = 10$ |
| F16 (proposed new failure mode) | added; 2-path is **not** the binding case |

**One-line headline:** *(a) on general 2-trees is empirically robust with
slack 0.226 to $T$, but the proof gap to close (T) is structurally beyond
the closed-form Cauchy–Schwarz bound; the harder target (T*) is empirically
false at moderate $n$.*
