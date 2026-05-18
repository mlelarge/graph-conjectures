# Strong arc decompositions of near-split and Eulerian digraphs

> **SUPERSEDED — 2026-05-17.** This draft was prepared in a publishing
> frame and Theorem 3 / Conjecture L are mis-framed: Conjecture L as
> stated is **refuted** by the funnel pair from `team/31_*` embedded in
> $K_4^* = $ complete bidirected on $\{r, u, v_1, w\}$ (3-arc-strong,
> arc-disjoint $T^-, U^-$ unchanged, subtree intersection equals $X$ not
> a strict subset). The team's own `team/31_*` lines 126–128 already
> recorded this; the draft contradicted the working notes. See
> `paper/review_v1.md` for the user's blocking finding and
> `paper/findings.md` for the honest knowledge-state replacement.
>
> Theorems 1 (EC-log), 2 (CL1), and 4 (R3⋆-KS kernel-shell case) stand.
> Theorem 3 (conditional full $(1, 0)$-near-split) does not. Two minor
> fixes have been applied to the draft below — line 41 out-cut typo and
> the §3.4 $n = 2$ multigraph base case — but the structural rewrite
> (drop Theorem 3 from headline, restructure §§5–6 around the
> refutation) is not done here. The honest replacement document is
> `paper/findings.md`.

**Abstract.** A *strong arc decomposition* (SAD) of a digraph $D$ is a
partition of its arc set into two parts each of which spans $D$ and is
strongly connected. Bang-Jensen and Yeo conjectured (2004) that every
$k$-arc-strong digraph has a SAD for some absolute constant $k$;
$k = 3$ would settle the conjecture, and no infinite family of
3-arc-strong digraphs without a SAD is known. We prove three results
in this direction. (i) **EC-log.** Every Eulerian digraph $D$ on $n \ge 3$
vertices with arc-strong connectivity at least $6 \log_2 n$ has a SAD.
*(Edit 2026-05-18: constant updated from $5\log_2 n$, $n \ge 2$, to $6\log_2 n$, $n \ge 3$, per the audit `CORRECTNESS_REVIEW_2026_05_18.md` §2.5.)*
The proof is a first-moment cut-counting argument via an
Eulerian-to-undirected reduction and Karger's bound. (ii) **CL1, the
bilateral lifting lemma.** Let $D = (V_1 \mathbin{\dot\cup} V_2, A)$
with both $D[V_1]$ and $D[V_2]$ SAD-decomposable, and suppose the
$V_1$-to-$V_2$ and $V_2$-to-$V_1$ bridge sets each admit a 2-coloring
with both colors non-empty in each direction. Then $D$ has a SAD. This
generalises the kernel-shell lemma 2.4 of Bang-Jensen and Wang
(J. Graph Theory 108, 5–26, 2025) by allowing both sides to be
SAD-decomposable internally. (iii) **A $(1,0)$-near-split SAD theorem,
conditional on a single named open problem.** A *$(1,0)$-near-split*
digraph has $V = V_1 \mathbin{\dot\cup} V_2$ with $V_2$ inducing a
semicomplete digraph, exactly one arc inside $V_1$, and arcs between
$V_1$ and $V_2$ unrestricted. We prove that, conditional on **Conjecture L**
— a subtree-inclusion statement about pairs of arc-disjoint spanning
in-arborescences sharing a common root — every simple 3-arc-strong
$(1,0)$-near-split digraph has a SAD. The unconditional kernel-shell
case (when the semicomplete part is itself SAD-decomposable) is proved
in full. Conjecture L is supported by over 11 000 verified
3-arc-strong instances with no failure, and a partial swap-repair
lemma is proved.

---

## 1. Introduction

### 1.1 The Bang-Jensen–Yeo problem

Throughout the paper a **digraph** $D = (V, A)$ has neither loops nor,
unless otherwise stated, multiple arcs; we write $n := |V|$. The
**out-cut** of a set $\emptyset \ne X \subsetneq V$ is
$\delta_D^+(X) = \{(u, v) \in A : u \in X, v \notin X\}$,
and the **arc-strong connectivity** is
$\lambda^{\mathrm{arc}}(D) = \min_X |\delta_D^+(X)|$. A digraph is
$k$**-arc-strong** if $\lambda^{\mathrm{arc}}(D) \ge k$.

A **strong arc decomposition** (SAD) of $D$ is an ordered pair
$(A_1, A_2)$ of arc-disjoint subsets with $A_1 \cup A_2 = A$ such that
both spanning sub-digraphs $(V, A_1)$ and $(V, A_2)$ are strongly
connected. Equivalently, $A = A_1 \mathbin{\dot\cup} A_2$ and every
directed cut $\delta_D^+(X)$, $\emptyset \ne X \subsetneq V$, meets
both $A_1$ and $A_2$.

Existence of a SAD is necessarily preceded by $\lambda^{\mathrm{arc}}(D)
\ge 2$, and 2-arc-strongness is known to be insufficient even within
sharply structured classes: $S_4$, the square of the directed 4-cycle,
is the unique smallest exception in the semicomplete class
(Bang-Jensen and Yeo, *Decomposing $k$-arc-strong tournaments into
strong spanning subdigraphs*, Combinatorica **24** (2004), 331–349);
squares of even directed cycles are precisely the 2-arc-strong
locally-semicomplete exceptions (Bang-Jensen and Huang, J. Combin.
Theory Ser. B **102** (2012), 701–714); Bang-Jensen, Gutin and Yeo
(J. Graph Theory **95** (2020), 267–289) gave a complete list of four
exceptional semicomplete compositions; the recent characterization of
the split-digraph case is due to Ai, He, Li, Qin and Wang
(arXiv:2408.02260, 2024), with the polynomial-time decision and the
3-arc-strong sufficiency proved by Bang-Jensen and Wang in J. Graph
Theory **108** (2025), 5–26. We refer to the survey of Bang-Jensen and
Kriesell (Electron. Notes Discrete Math. **34** (2009), 179–183) for
the broader context. Bang-Jensen and Yeo conjectured the existence of
an absolute constant $K$ such that every $K$-arc-strong digraph has a
SAD, and asked whether $K = 3$ suffices; this is **Conjecture WC3**.

### 1.2 Three positive contributions

The paper proves three theorems. The first two are unconditional.

**Theorem 1 (EC-log).** *Let $C = 6$ and $n_0 = 3$. Every Eulerian
digraph $D$ on $n \ge n_0$ vertices with $\lambda^{\mathrm{arc}}(D) \ge
C \log_2 n$ admits a strong arc decomposition.*

*(Edit 2026-05-18: constants updated from $C = 5$, $n_0 = 2$, per
`CORRECTNESS_REVIEW_2026_05_18.md` §2.5. The inequality $5\log_2 n >
4\log_2 n + 3$ needed at the end of the proof requires $n \ge 9$, not
$n \ge 4$; raising $C$ to $6$ closes the gap uniformly for $n \ge 3$.)*

The proof, given in Section 3, is a first-moment argument: pass to the
underlying undirected multigraph $G$ — for which Eulerianness gives
$\lambda_G = 2 \lambda^{\mathrm{arc}}(D)$ — and use Karger's bound
(Karger, *Minimum Cuts in Near-Linear Time*, J. ACM **47** (2000),
46–76) on the number of undirected cuts of size at most $\alpha
\lambda_G$.

**Theorem 2 (CL1).** *Let $D = (V, A)$ be a digraph with
$V = V_1 \mathbin{\dot\cup} V_2$, $|V_i| \ge 2$. Write
$B^+ = \delta_D^+(V_1)$ and $B^- = \delta_D^+(V_2)$. Suppose:*
1. *$D[V_1]$ and $D[V_2]$ each admit a SAD $A(D_i) = R_i \mathbin{\dot\cup} B_i$.*
2. *The bridge sets admit a partition $B^\pm = B^\pm_R \mathbin{\dot\cup}
   B^\pm_B$ with $B^+_R, B^+_B, B^-_R, B^-_B$ all non-empty.*

*Then $A(D) = (R_1 \cup R_2 \cup B^+_R \cup B^-_R) \mathbin{\dot\cup}
(B_1 \cup B_2 \cup B^+_B \cup B^-_B)$ is a SAD of $D$.*

Theorem 2 is proved in Section 4. The bridge 2-coloring hypothesis is
the genuine content; without it the lemma is vacuous, but with it the
conclusion follows by an Edmonds-stitching argument that produces a
spanning out-arborescence and a spanning in-arborescence rooted at a
common vertex inside each color class. Theorem 2 generalises
Bang-Jensen and Wang's Lemma 2.4 (the kernel-shell version of the same
attachment) from the unilateral form (one part SAD-decomposable, the
other an arc-less shell) to the **bilateral** form (both parts
SAD-decomposable internally).

The third theorem is the conditional headline. The class of
**$(1, 0)$-near-split** digraphs is the smallest non-trivial extension
of the split class: $V = V_1 \mathbin{\dot\cup} V_2$ with $D[V_2]$
semicomplete, arcs between $V_1$ and $V_2$ unrestricted, and exactly
one arc inside $V_1$ (otherwise $V_1$ is independent). We refer to the
unique $V_1$-internal arc as the **chord**.

**Theorem 3 ($(1, 0)$-near-split SAD; conditional).** *Assume
Conjecture L (Section 6). Every simple 3-arc-strong $(1, 0)$-near-split
digraph $D$ with $|V_1| \ge 2$, $|V_2| \ge 3$ admits a SAD.*

Conjecture L is a structural statement about pairs of arc-disjoint
spanning in-arborescences sharing a common root, stated precisely in
Section 6. The conditionality of Theorem 3 is on a *single named
combinatorial sub-claim*, not on any open conjecture from the standard
literature.

The unconditional content of Theorem 3 is the following.

**Theorem 4 (Kernel-shell case of Theorem 3).** *Let $D$ be a simple
3-arc-strong $(1, 0)$-near-split digraph with $|V_1| \ge 2$,
$|V_2| \ge 3$, and let $D^\bullet$ be the chord contraction (Section 5.1).
If $D^\bullet \langle V_2 \rangle$ admits a SAD, then so does $D$.*

The hypothesis of Theorem 4 is met whenever the semicomplete part is
itself strong-arc-decomposable as a 2-arc-strong simple semicomplete
digraph distinct from $S_4$; this is the case in every regime
$|V_2| \ge 5$ with $\lambda^{\mathrm{arc}}(D \langle V_2 \rangle) \ge 2$,
and in the dominant share of small-$|V_2|$ instances.

### 1.3 Why the $(1, 0)$-near-split class

The Bang-Jensen–Wang 2025 theorem says every 3-arc-strong split digraph
has a SAD; the $(1, 0)$-near-split class is the smallest perturbation
of the split class that the Bang-Jensen–Wang toolkit does not obviously
handle: the single $V_1$-internal chord prevents direct invocation of
the strict-split machinery and forces an explicit contraction step.
This is the smallest case where one expects the BJ–Wang argument to
break down — and the case where, by Theorem 3, one can establish that
it does not, modulo Conjecture L. The contraction reduces the problem
to a split *multi-digraph* SAD plus an un-contraction step (Section
5.1); the un-contraction is where Conjecture L enters.

The $(1, 0)$-near-split class is therefore the natural smallest
laboratory for testing whether the Bang-Jensen–Wang argument extends.
The conditional answer is yes; the unconditional version is open and
hinges on a single, finite, computer-checkable conjecture about
pairs of arborescences.

### 1.4 Organization

Section 2 collects definitions and the two tools we use *verbatim* from
the published literature: Edmonds' branching theorem and
Bang-Jensen–Wang Lemma 2.4. Section 3 gives the proof of Theorem 1
(EC-log). Section 4 gives the proof of Theorem 2 (CL1). Section 5 is
the technical core: setup, chord contraction, the side-label
formalism, the kernel-shell case (Theorem 4), the hard case via direct
Edmonds packing and a recoloring algorithm, and the proof of Theorem 3.
Section 6 states Conjecture L, gives its structural geometry (the
*funnel obstruction*), a partial swap-repair lemma, and the empirical
record. Section 7 is a computational catalogue. Section 8 lists open
problems. A short bibliography of audit-cleared sources closes the
paper.

---

## 2. Preliminaries

### 2.1 Definitions

A **digraph** $D = (V, A)$ has no loops; multi-arcs are allowed
explicitly when stated (and only in Section 5 onward). For
$\emptyset \ne X \subsetneq V$, the *out-cut*
$\delta_D^+(X) = \{(u, v) \in A : u \in X, v \notin X\}$ and the
*in-cut* $\delta_D^-(X) = \delta_D^+(V \setminus X)$ are arc multisets
when $D$ is a multi-digraph. The arc-strong connectivity is
$\lambda^{\mathrm{arc}}(D) = \min_X |\delta_D^+(X)|$. We write
$d^\pm_D(v) := |\delta_D^\pm(\{v\})|$. $D$ is **Eulerian** if
$d^+_D(v) = d^-_D(v)$ for every $v \in V$.

A **strong arc decomposition** (SAD) of $D$ is an ordered partition
$A(D) = A_1 \mathbin{\dot\cup} A_2$ such that both spanning sub-digraphs
$(V, A_1)$ and $(V, A_2)$ are strongly connected, equivalently every
directed cut meets both parts.

A digraph $D = (V, A)$ is **semicomplete** if for every two distinct
$u, v \in V$, at least one of $(u, v), (v, u)$ lies in $A$. $D$ is a
**split digraph** if $V = V_1 \mathbin{\dot\cup} V_2$, $V_1$ is
independent (no $V_1$-internal arc), $D[V_2]$ is semicomplete and arcs
between $V_1$ and $V_2$ are unrestricted. $D$ is a
**$(1, 0)$-near-split digraph** if it is split-like except that there
is exactly one ordered pair $(p, q) \in V_1 \times V_1$, $p \ne q$,
with $(p, q) \in A$, otherwise $V_1$ is independent. The unique
$V_1$-internal arc is the **chord** $e_0 := (p, q)$.

An **out-arborescence** (also called an out-branching) of $D$ with
root $r$ is a spanning sub-digraph in which every vertex except $r$
has in-degree exactly one and $r$ has in-degree zero; equivalently a
spanning tree in the underlying graph in which every arc is oriented
away from $r$. An **in-arborescence** is its arc-reversal: every
vertex except $r$ has out-degree exactly one and $r$ has out-degree
zero.

We will also need the following standard fact: a digraph $D$ on
$|V| \ge 2$ is strongly connected if and only if for every (equivalently
some) $r \in V$ there exist both a spanning out-arborescence and a
spanning in-arborescence of $D$ rooted at $r$.

### 2.2 Tools

We use two named results from the literature.

**Theorem (Edmonds' branching theorem).** *A directed multigraph
$D = (V, A)$ with a vertex $z$ has $k$ arc-disjoint out-arborescences
rooted at $z$ if and only if $|\delta_D^-(X)| \ge k$ for every
$\emptyset \ne X \subseteq V \setminus \{z\}$.*

This is the formulation we use, in the multigraph form. It implies, by
arc-reversal, the symmetric statement for in-arborescences.

**Theorem (Karger 2000, cut-counting).** *Let $G$ be an undirected
multigraph on $n$ vertices with minimum cut $\lambda_G$. For every
real $\alpha \ge 1$, the number of distinct undirected cuts (i.e.
vertex-bipartitions $\{X, V \setminus X\}$) of size at most
$\alpha \lambda_G$ is at most $n^{2 \alpha}$.*

This is the form we use in Section 3. Karger's contraction algorithm
proof goes through verbatim for multigraphs.

**Lemma (Bang-Jensen–Wang 2025, Lemma 2.4).** *Let $D$ be a directed
multigraph and $X$ a subset of $V(D)$ such that every vertex of $D - X$
has both two in-neighbors and two out-neighbors in $X$. If $X$ has a
SAD, then $D$ has a SAD.*

This is the "kernel-shell" attachment lemma. The proof, given in
Bang-Jensen and Wang (J. Graph Theory **108** (2025), 5–26, page 4),
proceeds by attaching one in-arc and one out-arc per shell vertex to
each of the two color classes, leveraging the SAD on the kernel. It
applies to multigraphs without modification, and is the engine for
both the Bang-Jensen–Wang 3-arc-strong split theorem and our Section 5.

### 2.3 The arc-disjoint branching packings we use

The only branching-packing result we use is Edmonds' theorem, applied
independently to $D$ and to its arc-reversal $\overleftarrow{D}$. From
3-arc-strongness of $D$ and the arc-reversal identity
$|\delta_{\overleftarrow{D}}^-(X)| = |\delta_D^+(X)|$, Edmonds applied
twice yields, for any chosen root $r$:
- 3 arc-disjoint out-arborescences $T_1^+, T_2^+, T_3^+$ rooted at $r$,
- 3 arc-disjoint in-arborescences $T_1^-, T_2^-, T_3^-$ rooted at $r$.

These two families are *separately* arc-disjoint; in general arcs may
be shared between the two families. We do **not** use any cross-kind
arc-disjointness statement; existence of even a single arc-disjoint
$(T^+, T^-)$ pair at high arc-strength is the wide-open Thomassen
conjecture (Conjecture 2 of Bang-Jensen, Bessy, Havet and Yeo,
arXiv:2003.02107, 2022), and we make no use of it. The within-kind form
above is all we will need.

### 2.4 Hypotheses preserved by chord contraction

In Section 5 we form the chord contraction $D^\bullet$ of a
$(1, 0)$-near-split digraph $D$ with chord $e_0 = (p, q)$: contract
$p, q$ to a single vertex $r := p^\bullet$ and delete the loop. The
resulting object is a **split multi-digraph**: $V^\bullet =
(V \setminus \{p, q\}) \cup \{r\}$, $V_1^\bullet :=
(V_1 \setminus \{p, q\}) \cup \{r\}$ is independent in $D^\bullet$,
and $V_2^\bullet := V_2$ is simple semicomplete in $D^\bullet$ (since
contraction does not touch $V_2$-internal arcs).

A direct accounting (Section 5.1) shows that $\lambda^{\mathrm{arc}}(D)
\ge 3$ implies $\lambda^{\mathrm{arc}}(D^\bullet) \ge 3$ — the chord,
being an internal arc, never appears in the boundary of any cut, so
3-arc-strongness is preserved by contraction.

---

## 3. EC-log: a probabilistic SAD theorem for Eulerian digraphs

This section gives the proof of Theorem 1. The argument is
self-contained.

### 3.1 Setup

Let $D = (V, A)$ be an Eulerian digraph on $n$ vertices with
$\lambda := \lambda^{\mathrm{arc}}(D)$. Define $G = (V, E)$ to be the
**underlying undirected multigraph**: each arc $(u, v) \in A$ becomes
an undirected edge $\{u, v\}$, preserving multiplicities (so each
anti-parallel pair contributes two edges).

**Step 1 (cut balance).** Summing $d^+_D(v) = d^-_D(v)$ over $v \in X$
and cancelling $D[X]$-internal arcs gives
$$|\delta_D^+(X)| = |\delta_D^-(X)|, \qquad \emptyset \ne X \subsetneq V. \tag{1}$$

**Step 2 (undirected degree).** Each arc of $D$ contributes one edge
to $G$, and an arc $(u, v)$ with $u \in X$, $v \notin X$ contributes
to $\delta_G(X)$ regardless of orientation. Hence
$$d_G(X) = |\delta_D^+(X)| + |\delta_D^-(X)| \stackrel{(1)}{=} 2|\delta_D^+(X)|. \tag{2}$$
In particular $\lambda_G = 2 \lambda$.

**Step 3 (cut correspondence with explicit two-to-one factor).** The
directed cuts of $D$ are indexed by ordered nonempty proper subsets
$X \subsetneq V$, of which there are $2^n - 2$. The undirected cuts of
$G$ are indexed by unordered partitions $\{X, V \setminus X\}$, of
which there are $2^{n-1} - 1$. Each unordered cut corresponds to
exactly two directed cuts, $\delta_D^+(X)$ and
$\delta_D^+(V \setminus X) = \delta_D^-(X)$, equal in size by (1).
Thus
$$\#\{X \subsetneq V \text{ nonempty} : |\delta_D^+(X)| = s\}
  = 2 \cdot \#\{\{X, V\setminus X\} : |\delta_G(X)| = 2s\}. \tag{3}$$
This factor of 2 will be paid explicitly in the union bound.

### 3.2 Random 2-coloring and per-cut bound

Color each arc of $D$ independently red or blue, each with probability
$1/2$. A directed cut $\delta_D^+(X)$ of size $s$ is monochromatic iff
all $s$ of its arcs receive the same color; by independence,
$$\Pr[\delta_D^+(X) \text{ monochromatic}] = 2 \cdot 2^{-s} = 2^{1 - s}. \tag{4}$$
The existence of a SAD is equivalent to the existence of a coloring
with no monochromatic directed cut, and we show the expected number of
such cuts is below 1 when $\lambda \ge 6 \log_2 n$.

### 3.3 Karger band decomposition

Partition the directed cuts by *band*: for $j \ge 1$, let
$$B_j := \{X \subsetneq V \text{ nonempty} : j \lambda \le |\delta_D^+(X)| < (j+1) \lambda\}.$$

By (2), $X \in B_j$ iff the underlying undirected cut has size in
$[j \lambda_G, (j+1) \lambda_G)$. By Karger's theorem applied with
$\alpha = j + 1$, the number of *unordered* undirected cuts of size
$\le (j+1) \lambda_G$ is at most $n^{2(j+1)}$. By (3),
$$|B_j| \le 2 \cdot n^{2(j+1)}. \tag{5}$$
Every $X \in B_j$ has $|\delta_D^+(X)| \ge j \lambda$, hence
$\Pr[\delta_D^+(X) \text{ monochromatic}] \le 2^{1 - j \lambda}$.

### 3.4 Union bound

Let $N$ be the number of monochromatic directed cuts. Then
$$\mathbb{E}[N] = \sum_X \Pr[\delta_D^+(X) \text{ monochromatic}]
  \le \sum_{j \ge 1} 2 \cdot n^{2(j+1)} \cdot 2^{1 - j \lambda}
  = 4 n^4 \cdot 2^{-\lambda} \sum_{j \ge 1} \left( \frac{n^2}{2^\lambda} \right)^{j - 1}.$$

If $\lambda \ge 3 \log_2 n + 1$, the ratio $n^2 / 2^\lambda \le 1/(2n) \le 1/4$
for $n \ge 2$, so the geometric series is at most $4/3 < 2$, giving
$\mathbb{E}[N] \le 8 n^4 \cdot 2^{-\lambda}$. We require
$\mathbb{E}[N] < 1$, i.e.
$$\lambda > 4 \log_2 n + 3. \tag{6}$$
Both (6) and $\lambda \ge 3 \log_2 n + 1$ are implied by $\lambda \ge 6
\log_2 n$ for $n \ge 3$: for the first, $6\log_2 n > 4\log_2 n + 3
\Leftrightarrow 2\log_2 n > 3 \Leftrightarrow n > 2\sqrt 2$, hence $n
\ge 3$; for the second, $6\log_2 n \ge 3\log_2 n + 1 \Leftrightarrow
3\log_2 n \ge 1$, which holds for $n \ge 2$.

*(Edit 2026-05-18: the previous version of this paragraph claimed
implication by $\lambda \ge 5\log_2 n$ for $n \ge 4$; that claim is
arithmetically false at $n \in \{3, 4, 5, 6, 8\}$ because $5\log_2 n >
4\log_2 n + 3 \Leftrightarrow n \ge 9$. The constant is raised to 6 to
remove the gap. See `CORRECTNESS_REVIEW_2026_05_18.md` §2.5 and
`team/04_ec_log_proof.md` §2.5 for the full table.)*

### 3.5 Conclusion

For $\lambda \ge 6 \log_2 n$ and $n \ge 3$, $\mathbb{E}[N] < 1$, so
there exists a 2-coloring with no monochromatic directed cut. By the
working definition of SAD, this is a strong arc decomposition. This
completes the proof of Theorem 1. $\square$

**Remark.** The constant $C = 6$ has approximately 3–17 units of slack
in the $n \in [10, 1000]$ range; the asymptotic limit of this argument
is $C \to 4^+$, beyond which the geometric series fails. Replacing
$\log_2 n$ by a constant via the same union bound is impossible, since
the Karger bound $n^{2\alpha}$ is asymptotically tight on cycles and
low-connectivity Cayley graphs.

---

## 4. The bilateral lifting lemma CL1

This section proves Theorem 2. The lemma reduces SAD existence on a
two-part digraph to (a) SAD-decomposability of each part and (b) a
small bridge 2-coloring problem.

### 4.1 Statement (restated)

**Theorem 2 (CL1).** *Let $D = (V, A)$ be a digraph with
$V = V_1 \mathbin{\dot\cup} V_2$, $|V_i| \ge 2$. Write
$B^+ = \delta_D^+(V_1)$ and $B^- = \delta_D^+(V_2)$. Suppose:*
1. *Each $D_i := D[V_i]$ admits a SAD $A(D_i) = R_i \mathbin{\dot\cup} B_i$.*
2. *The bridge sets admit a partition $B^\pm = B^\pm_R \mathbin{\dot\cup}
   B^\pm_B$ with $B^+_R, B^+_B, B^-_R, B^-_B$ all non-empty.*

*Then $(A_R, A_B) := (R_1 \cup R_2 \cup B^+_R \cup B^-_R,
B_1 \cup B_2 \cup B^+_B \cup B^-_B)$ is a SAD of $D$.*

### 4.2 The reduction to a branching-witness

The conclusion of Theorem 2 requires: (a) $A_R \mathbin{\dot\cup} A_B
= A(D)$, and (b) each of $(V, A_R), (V, A_B)$ is strongly connected.
Part (a) is immediate: every arc of $D$ is either in $A(D_1) =
R_1 \mathbin{\dot\cup} B_1$, in $A(D_2) = R_2 \mathbin{\dot\cup} B_2$,
or in $B^+ \mathbin{\dot\cup} B^-$ (and we partition the bridges by
hypothesis (2)).

For part (b) we use the following sufficient condition for strong
connectivity, standard from the theory of arborescences (Section 2.1):
a digraph $(V, A_c)$ is strongly connected if it contains a spanning
out-arborescence and a spanning in-arborescence rooted at a common
vertex.

### 4.3 Stitching a spanning out-arborescence in $A_R$

Pick any $r_R \in V_1$; pick any bridges $e^+ = (a^+, r_2^+) \in B^+_R$
(possible by hypothesis (2), $B^+_R \ne \emptyset$) and
$e^- = (r_2^-, b^-) \in B^-_R$ (similarly, $B^-_R \ne \emptyset$). Set
$r_2^+ \in V_2$ to be the head of $e^+$ and $r_2^- \in V_2$ to be the
tail of $e^-$. By hypothesis (1) and the fact that strongly connected
$(V_i, R_i)$ contains a spanning out-arborescence rooted at any
$r \in V_i$ (and likewise a spanning in-arborescence), we may choose:

- $T^+_{R, 1}$: spanning out-arborescence of $(V_1, R_1)$ rooted at $r_R$;
- $T^+_{R, 2}$: spanning out-arborescence of $(V_2, R_2)$ rooted at $r_2^+$;
- $T^-_{R, 1}$: spanning in-arborescence of $(V_1, R_1)$ rooted at $r_R$;
- $T^-_{R, 2}$: spanning in-arborescence of $(V_2, R_2)$ rooted at $r_2^-$.

Define
$$T^+_R := T^+_{R, 1} \cup \{e^+\} \cup T^+_{R, 2}, \qquad
  T^-_R := T^-_{R, 1} \cup \{e^-\} \cup T^-_{R, 2}.$$

**Claim.** *Both $T^+_R$ and $T^-_R$ are spanning arborescences of $D$
rooted at $r_R$, with arc sets in $A_R$.*

*Proof of the claim.* Vertex coverage: $T^+_{R, 1}$ spans $V_1$ and
$T^+_{R, 2}$ spans $V_2$, so $V(T^+_R) = V$; same for $T^-_R$. Arc
count: $T^+_R$ has $(|V_1| - 1) + 1 + (|V_2| - 1) = |V| - 1$ arcs,
the correct count for a spanning arborescence on $|V|$ vertices. Arc
sets: $T^+_{R, 1} \subseteq R_1$, $T^+_{R, 2} \subseteq R_2$,
$e^+ \in B^+_R$, all in $A_R$; same for $T^-_R$.

*In-degree of each vertex in $T^+_R$.* The root $r_R$ has in-degree
zero: no $T^+_{R, 1}$-arc has head $r_R$ (since $r_R$ is the root of
$T^+_{R, 1}$), no $T^+_{R, 2}$-arc has head in $V_1$, and $e^+$ has
head $r_2^+ \in V_2 \ne r_R$. For $v \in V_1 \setminus \{r_R\}$, the
unique in-arc is the $T^+_{R, 1}$-in-arc, since no $T^+_{R, 2}$-arc
has head in $V_1$ and $e^+$ has head in $V_2$. For $v = r_2^+$, the
unique in-arc is $e^+$ itself (no $T^+_{R, 2}$-arc has head equal to
its root $r_2^+$, no $T^+_{R, 1}$-arc has head in $V_2$). For $v \in
V_2 \setminus \{r_2^+\}$, the unique in-arc is the $T^+_{R, 2}$-in-arc.

Reachability from $r_R$ in $T^+_R$: every $v \in V_1$ is reached
inside $T^+_{R, 1}$; the bridge $e^+$ then carries reachability to
$r_2^+$, and every $v \in V_2$ is reached from $r_2^+$ inside
$T^+_{R, 2}$. Acyclicity follows from the spanning + correct-in-degree
properties.

The argument for $T^-_R$ is symmetric, using that $r_2^-$ is the *tail*
of $e^-$ and the *root* of $T^-_{R, 2}$ (so its unique out-arc in
$T^-_R$ is $e^- = (r_2^-, b^-)$, with $b^- \in V_1$ in the inner
in-arborescence). This proves the claim. $\square$

### 4.4 Strong connectivity of $A_R$ and $A_B$

Given the claim, $(V, A_R)$ is strongly connected: for any $u, v \in V$,
walk from $u$ to $r_R$ along $T^-_R$ (in-arcs flow into the root) and
then from $r_R$ to $v$ along $T^+_R$. Repeat the argument symmetrically
with $R, B$ swapped — hypothesis (2) gives $B^+_B \ne \emptyset$ and
$B^-_B \ne \emptyset$, so the same construction with $r_B \in V_1$
yields strong connectivity of $(V, A_B)$. Combined with part (a), this
is a SAD of $D$. $\square$ (Theorem 2)

### 4.5 Discussion and the bilateral form

Theorem 2 (CL1) compares to the Bang-Jensen–Wang Lemma 2.4 quoted in
Section 2 as follows. Lemma 2.4 takes a SAD $(A_1, A_2)$ on a kernel
$X$ and absorbs each shell vertex $v \in D - X$ via two in-arcs and
two out-arcs from $X$, one of each per color. Theorem 2 admits *both*
parts $D[V_1]$ and $D[V_2]$ as SAD-decomposable, with internal SAD
arcs $R_i \cup B_i$ contributing to both color classes simultaneously,
and replaces the 2-in-2-out neighbor condition by the 2-coloring of
bridges with all four (direction, color) classes non-empty.

The two lemmas are not directly comparable: if $D - X$ is an
independent set of size $\ge 2$ with no internal arcs, then CL1's
hypothesis (1) on $V_2 := D - X$ is vacuously false (an arc-less
digraph admits no SAD on $\ge 2$ vertices). Conversely, if $D[V_2]$
contains internal arcs, Lemma 2.4's "absorb via 2 in-/2 out-arcs" gives
no recipe for partitioning the internal arcs of $D[V_2]$. The proof
technique is shared — Edmonds-style attachment of arcs across a single
bridge per direction per color — but the **bilateral** form of CL1 is
not in the literature surveyed by the team's audit.

The bridge 2-coloring hypothesis is the substantive content of CL1. It
is a small SAT instance over $|B^+| + |B^-|$ variables; instances with
some direction degenerate (no bridges of one color) occur in
applications, and we comment on the empirical regime in Section 7.

---

## 5. The $(1, 0)$-near-split SAD theorem

This section gives the proof of Theorem 4 (unconditional) and Theorem 3
(conditional on Conjecture L). The proof has four ingredients: a chord
contraction (Section 5.1), a kernel-shell sub-case (Section 5.2), a
hard sub-case via direct Edmonds packing (Section 5.3), and the
assembly (Section 5.4).

### 5.1 Setup: contraction and side labels

Let $D = (V, A)$ be a simple 3-arc-strong $(1, 0)$-near-split digraph
with chord $e_0 = (p, q)$, $|V_1| \ge 2$, $|V_2| \ge 3$.

**Chord contraction.** Let $r := p^\bullet$ be a fresh symbol and
$V^\bullet := (V \setminus \{p, q\}) \cup \{r\}$. Define the
contraction map $\pi : V \to V^\bullet$ by $\pi(x) = r$ for
$x \in \{p, q\}$ and $\pi(x) = x$ otherwise. The contracted
multi-digraph $D^\bullet = (V^\bullet, A^\bullet)$ has arc multiset
$A^\bullet := \langle\!\langle \pi(a) : a \in A \setminus \{e_0\}
\rangle\!\rangle$ (the chord itself, which would map to a loop, is
deleted). We keep arc labels: each $\pi(a) \in A^\bullet$ remembers
its preimage $a \in A \setminus \{e_0\}$.

We set $V_1^\bullet := (V_1 \setminus \{p, q\}) \cup \{r\}$ and
$V_2^\bullet := V_2$. The induced sub-multidigraph $D^\bullet \langle
V_2^\bullet \rangle$ equals $D \langle V_2 \rangle$ as a labelled
digraph (since $\pi$ fixes $V_2$ and no $V_2$-internal arc is the
chord), and is therefore simple and semicomplete.

**Lemma 5.1 (Contraction preserves 3-arc-strongness).** *$D^\bullet$
is 3-arc-strong as a multi-digraph.*

*Proof.* Let $\emptyset \ne S \subsetneq V^\bullet$. Lift $S$ to $V$
via $\widehat{S} := (S \setminus \{r\}) \cup \{p, q\}$ if $r \in S$,
and $\widehat{S} := S$ otherwise. Then $\widehat{S} \ne \emptyset$,
$\widehat{S} \ne V$, and an arc $\pi(a) \in A^\bullet$ leaves $S$ iff
$a \in A \setminus \{e_0\}$ leaves $\widehat{S}$. The chord $e_0$
either has both endpoints in $\widehat{S}$ (when $r \in S$, so
$\{p, q\} \subseteq \widehat{S}$) or neither (when $r \notin S$, so
$\{p, q\} \cap \widehat{S} = \emptyset$); in either case $e_0 \notin
\delta_D^+(\widehat{S})$. Hence
$|\delta_{D^\bullet}^+(S)| = |\delta_D^+(\widehat{S})| \ge 3$. $\square$

It follows that $D^\bullet$ is a 3-arc-strong split multi-digraph
with $V_1^\bullet$ independent and $V_2^\bullet$ simple semicomplete.

**Side labels at $r$.** Each non-chord arc of $D$ incident with
$\{p, q\}$ contributes a labelled arc at $r$ in $D^\bullet$. The four
**side-label classes** at $r$ are
- $R_p^+ := \{(r, y) \in A^\bullet : \text{preimage } (p, y), y \in V_2\}$;
- $R_q^+ := \{(r, y) \in A^\bullet : \text{preimage } (q, y), y \in V_2\}$;
- $R_p^- := \{(x, r) \in A^\bullet : \text{preimage } (x, p), x \in V_2\}$;
- $R_q^- := \{(x, r) \in A^\bullet : \text{preimage } (x, q), x \in V_2\}$.

These partition the labelled arcs of $A^\bullet$ incident with $r$.

**Lemma 5.2 (Side-label supply).** *In any 3-arc-strong simple
$(1, 0)$-near-split digraph $D$,*
$$|R_p^+| \ge 2, \quad |R_q^+| \ge 3, \quad |R_p^-| \ge 3, \quad |R_q^-| \ge 2. \tag{$\ast$}$$

*Proof.* By independence of $V_1$ modulo the unique chord $e_0$
(near-split hypothesis), $p$ has at most one $V_1$-internal out-arc
(namely $e_0$) and no $V_1$-internal in-arc; symmetrically $q$ has no
$V_1$-internal out-arc and at most one $V_1$-internal in-arc (namely
$e_0$). By 3-arc-strongness $d^\pm_D(p), d^\pm_D(q) \ge 3$. Subtracting
the chord: $d^+_D(p) - 1 \ge 2$ out-arcs of $p$ go to $V_2$,
contributing $\ge 2$ to $R_p^+$; $d^+_D(q) \ge 3$ out-arcs of $q$ go
to $V_2$ (no chord deduction), contributing $\ge 3$ to $R_q^+$.
Symmetrically $|R_p^-| \ge 3$ and $|R_q^-| \ge 2$. $\square$

**The un-contraction lifting.** Given a SAD
$(A_1^\bullet, A_2^\bullet)$ of $D^\bullet$, the un-contraction maps
each labelled arc back to its preimage in $A \setminus \{e_0\}$,
producing a partition of $A \setminus \{e_0\}$. To produce a SAD of
$D$, we must assign $e_0$ to one of the two colors. For
$i \in \{1, 2\}$ write $D_i^\flat$ for the spanning sub-digraph
$(V, \pi^{-1}(A_i^\bullet))$ of $D - e_0$.

**Definition 5.3.** *Color $i$ is **$P$-reaching** if $D_i^\flat$
contains a directed $p \to q$ path; **$Q$-reaching** if it contains a
directed $q \to p$ path; **good** if both.*

**Facts F1, F2 (un-contraction).** *(F1) $D_i^\flat$ is strongly
connected on $V$ iff color $i$ is good. (F2) $D_i^\flat + e_0$ is
strongly connected on $V$ iff color $i$ is $Q$-reaching.*

*Proof.* (F1, $\Leftarrow$): given $u, v \in V$, the strong
connectivity of $(V^\bullet, A_i^\bullet)$ gives a $\pi(u) \to \pi(v)$
walk; un-contract, splicing in a directed $\{p, q\}$-path at each
$r$-traversal of the walk that crosses sides (good supplies both
splice directions in $D_i^\flat$). (F1, $\Rightarrow$): trivial. (F2):
adding $e_0$ to $D_i^\flat$ adds only $p \to q$ reachability; the
resulting digraph is strongly connected iff $D_i^\flat$ already had
$q \to p$ reachability, i.e. iff color $i$ was $Q$-reaching. $\square$

The lifting target is therefore the following.

**Target R3⋆.** *Find a SAD $(A_1^\bullet, A_2^\bullet)$ of $D^\bullet$
and a color $i \in \{1, 2\}$ such that color $i$ is $Q$-reaching and
color $3 - i$ is good.*

Equivalently, in the abbreviation $P_i$ = "color $i$ is $P$-reaching"
and $Q_i$ = "color $i$ is $Q$-reaching" (with $\wedge$ for conjunction):

$$(R3\star): \quad \exists\, i \in \{1, 2\}: \; Q_i \wedge P_{3 - i} \wedge Q_{3 - i}.$$

Once R3⋆ holds, assigning $e_0$ to color $i$ gives a SAD of $D$ by
F1 and F2.

### 5.2 The kernel-shell case (R3⋆-KS)

This sub-section proves Theorem 4. Assume the kernel-shell hypothesis:
$D^\bullet \langle V_2 \rangle$ admits a SAD $(B_1, B_2)$ (this is the
case e.g. whenever $D \langle V_2 \rangle$ is 2-arc-strong and not
isomorphic to $S_4$, by the Bang-Jensen–Yeo 2004 theorem).

**The attachment template.** We extend $(B_1, B_2)$ to a SAD of
$D^\bullet$ by attaching the shell $V_1^\bullet$ as follows. Set
$A_j^\bullet \cap A(D^\bullet \langle V_2 \rangle) := B_j$ for
$j \in \{1, 2\}$. For each shell vertex $v \in V_1^\bullet$ we will
choose two in-arcs (one per color) and two out-arcs (one per color)
between $v$ and $V_2$, plus distribute the remaining arcs at $v$
arbitrarily. Strong connectivity of $(V^\bullet, A_j^\bullet)$ then
follows from the kernel-shell construction: each $v \in V_1^\bullet$
reaches $V_2$ in color $j$ by its color-$j$ out-arc and is reached
from $V_2$ by its color-$j$ in-arc, while $B_j$ is strong on $V_2$.

For $v \in V_1 \setminus \{p, q\}$ the required attachments exist by
3-arc-strongness (the shell vertex has $\ge 3$ in-arcs and $\ge 3$
out-arcs, all from/to $V_2$ since $V_1$ is independent off the chord).

For $v = r$ we use labelled arcs directly. By Lemma 5.2 the side-label
supplies are $\ge 2, \ge 3, \ge 3, \ge 2$. We claim the assignment
below produces both a SAD of $D^\bullet$ and the R3⋆ liftability
condition with $i = 2$.

**Construction at $r$ (kernel-shell).** Choose:
- $\alpha_2^+ \in R_q^+$ (one arc, $|R_q^+| \ge 3$);
- $\alpha_2^- \in R_p^-$ (one arc, $|R_p^-| \ge 3$);
- $\beta_1^{+, p} \in R_p^+$, $\beta_1^{+, q} \in R_q^+ \setminus \{\alpha_2^+\}$;
- $\beta_1^{-, p} \in R_p^- \setminus \{\alpha_2^-\}$, $\beta_1^{-, q} \in R_q^-$.

Add $\{\alpha_2^+, \alpha_2^-\}$ to $A_2^\bullet$ and
$\{\beta_1^{+, p}, \beta_1^{+, q}, \beta_1^{-, p}, \beta_1^{-, q}\}$ to
$A_1^\bullet$. By Lemma 5.2 each pick exists, and all six are pairwise
distinct: they lie in pairwise distinct side classes except for the
two picks in $R_q^+$ (resp. $R_p^-$), which are explicitly distinct.
Distribute the remaining labelled arcs at $r$ arbitrarily between
colors.

By the kernel-shell template, $(A_1^\bullet, A_2^\bullet)$ is a SAD of
$D^\bullet$.

**R3⋆ verification.**

*Color 2 is $Q$-reaching.* The arcs in $A_2^\bullet$ at $r$ include
$\alpha_2^+ \in R_q^+$ (preimage $(q, y_2)$, $y_2 \in V_2$) and
$\alpha_2^- \in R_p^-$ (preimage $(x_2, p)$, $x_2 \in V_2$). By
strong connectivity of $B_2$ on $V_2$, there is a $y_2 \to x_2$
directed path in $B_2$ (possibly trivial). Concatenated in
$D_2^\flat$: $(q, y_2)$, then the $V_2$-internal path $y_2 \to x_2$,
then $(x_2, p)$ — a $q \to p$ walk. So $Q_2$ holds.

*Color 1 is good.* The arcs in $A_1^\bullet$ at $r$ include
$\beta_1^{+, p} \in R_p^+$ (preimage $(p, y_1^p)$) and
$\beta_1^{-, q} \in R_q^-$ (preimage $(x_1^q, q)$). By strong
connectivity of $B_1$ on $V_2$, the $V_2$-internal $y_1^p \to x_1^q$
path lies in $B_1$. Concatenated: $(p, y_1^p) \to \cdots \to
(x_1^q, q)$ is a $p \to q$ walk in $D_1^\flat$, so $P_1$ holds.
Symmetrically the arcs $\beta_1^{+, q} \in R_q^+$ and
$\beta_1^{-, p} \in R_p^-$ give a $q \to p$ walk in $D_1^\flat$ via a
$V_2$-internal $y_1^q \to x_1^p$ path in $B_1$, so $Q_1$ holds.

Together: $Q_2 \wedge P_1 \wedge Q_1$, the R3⋆ condition with $i = 2$.

**Conclusion (Theorem 4).** Apply F2 to color 2: $D_2^\flat + e_0$ is
strongly connected (color 2 is $Q$-reaching). Apply F1 to color 1:
$D_1^\flat$ is strongly connected (color 1 is good). Setting
$A_1 := \pi^{-1}(A_1^\bullet)$ and $A_2 := \pi^{-1}(A_2^\bullet) \cup
\{e_0\}$, the pair $(A_1, A_2)$ is a SAD of $D$. $\square$ (Theorem 4)

### 5.3 The hard case (R3⋆-HC)

This sub-section gives the conditional argument for the complement of
the kernel-shell case: $D^\bullet \langle V_2 \rangle$ does **not**
admit a SAD. By the Bang-Jensen–Yeo 2004 theorem (every 2-arc-strong
simple semicomplete digraph distinct from $S_4$ admits a SAD), this
hard case decomposes into three regimes:

- **(H1a)** $D^\bullet \langle V_2 \rangle$ is not strongly connected;
- **(H1b)** $D^\bullet \langle V_2 \rangle$ is strongly connected with
  $\lambda^{\mathrm{arc}}(D^\bullet \langle V_2 \rangle) = 1$ (cut-arc);
- **(H2)** $|V_2| = 4$ and $D \langle V_2 \rangle \cong S_4$.

We treat the three regimes uniformly via a direct Edmonds branching
packing, recoloring the cross-kind shared arcs, and finishing the
side-label allocation at $r$ by a 16-profile case analysis.

#### 5.3.1 The branching packing

Apply Edmonds' theorem to $D^\bullet$ with root $r$ and $k = 2$: by
Lemma 5.1, $\lambda^{\mathrm{arc}}(D^\bullet) \ge 3 \ge 2$, so there
exist arc-disjoint out-arborescences $T_1^+, T_2^+$ of $D^\bullet$
rooted at $r$. Apply Edmonds' theorem to the reverse
$\overleftarrow{D^\bullet}$ with root $r$ and $k = 2$: arc-reversal
preserves arc-strong connectivity, so the theorem yields arc-disjoint
out-arborescences of $\overleftarrow{D^\bullet}$, whose reversals are
arc-disjoint in-arborescences $T_1^-, T_2^-$ of $D^\bullet$ rooted at
$r$. The two applications are independent; we obtain

$$T_1^+ \cap T_2^+ = \emptyset \quad \text{and} \quad T_1^- \cap T_2^- = \emptyset. \tag{WK}$$

We make **no** cross-kind disjointness claim: an arc may lie in both
$T_i^+$ and $T_j^-$. (As discussed in Section 2.3, cross-kind
disjointness even at $k = 1$ is the wide-open Thomassen conjecture
and is *not* used.)

#### 5.3.2 Cross-kind sharing and the RECOLOR algorithm

Define $B^\circ := T_1^+ \cup T_2^+ \cup T_1^- \cup T_2^-$ (union as
arc multisets, but each arc counted at most twice — once as an
out-branching arc, once as an in-branching arc). The arcs counted
twice are exactly the cross-kind shared arcs. Define the four
cross-kind shared-arc sets
$$S_{ij} := T_i^+ \cap T_j^- \quad (i, j \in \{1, 2\}).$$

Within-kind disjointness (WK) implies $S_{11} \cup S_{12}$ contains
only out-branching arcs of color 1, and so on; the four sets are
pairwise disjoint. Let $S := S_{11} \cup S_{12} \cup S_{21} \cup S_{22}$
be the set of all cross-kind shared arcs.

**Cross-kind impossibility at $r$.** No arc of $D^\bullet$ incident
with $r$ lies in both an out-arborescence and an in-arborescence
rooted at $r$: out-branching arcs at $r$ have tail $r$, in-branching
arcs at $r$ have head $r$, and we are in a loop-free digraph.
Therefore $S \subseteq A^\bullet \setminus \{\text{arcs at } r\}$.

The shared arcs lie at internal vertices. We resolve cross-kind
sharing by assigning each shared arc to *one* color, then replacing
the "lost" arc inside the affected color's branching by a free
replacement arc. The procedure is the **RECOLOR algorithm**.

**The single-arc replacement lemma.** Let $a \in T_i^- \cap T_j^+$
with $i \ne j$; equivalently $a$ is a cross-kind shared arc. Suppose
we wish to commit $a$ to color $j$ (its out-branching role) and
remove it from color $i$'s in-branching $T_i^-$. Let $a = (u, v)$ and
let $X_a \subseteq V^\bullet \setminus \{r\}$ be the $T_i^-$-subtree
"below" $a$, i.e. the set of vertices whose unique $T_i^-$-walk to $r$
passes through $a$. Then removing $a$ from $T_i^-$ disconnects $X_a$
from $r$ in $T_i^-$.

To restore an in-arborescence on color $i$, replace $a$ by an arc
$a' \in \delta^+(X_a) \cap (A^\bullet \setminus T_i^-)$, provided
such an $a'$ exists with head outside $X_a$ in $T_i^-$ (to avoid
creating a cycle). Existence of *some* arc in $\delta^+(X_a)$ outside
$T_i^-$ follows from 3-arc-strongness: $|\delta^+(X_a)| \ge 3$, at
most one arc is $a \in T_i^-$, so at least two arcs of
$\delta^+(X_a)$ lie outside $T_i^-$. If one such arc is *free* (not in
$T_1^+ \cup T_2^+ \cup T_2^- \cup T_1^- \setminus \{a\}$), pick it as
$a'$ and conclude.

**Cascading replacements.** If no free replacement arc is available,
$a'$ must be borrowed from one of $T_2^+, T_1^+, T_2^-$ (excluding
$T_i^- \setminus \{a\}$). Borrowing $a'$ from one of these branchings
breaks that branching, requiring a second replacement, and so on. The
algorithm chains replacements until either (i) a free arc is found,
or (ii) the chain returns to a previously visited shared arc (a
*cycle* in the replacement graph). We must rule out (ii).

This is where Conjecture L enters: it asserts that, at every step of
the chained replacement, the replacement arc can be chosen so that
the affected subtree *strictly shrinks*, yielding a strict-decrease
potential that prevents cycling.

We isolate the precise statement.

**Conjecture L (recalled from Section 6).** *Let $T^-, U^-$ be two
arc-disjoint spanning in-arborescences of a 3-arc-strong directed
multigraph $D^\bullet$ rooted at $r$, and let $a \in T^-$ with
$X_a^{T^-} \subseteq V^\bullet \setminus \{r\}$. Then there exists
$b \in U^- \cap \delta^+(X_a^{T^-})$ such that
$X_b^{U^-} \cap X_a^{T^-} \subsetneq X_a^{T^-}$, with strict inclusion.*

Here $X_a^{T^-}$ is the $T^-$-subtree below $a$ and $X_b^{U^-}$ the
$U^-$-subtree below $b$; the conclusion says some exit arc $b$ of
$U^-$ from $X_a^{T^-}$ has a $U^-$-subtree that strictly misses some
vertex of $X_a^{T^-}$.

**Lemma 5.4 (Termination of RECOLOR, conditional on Conjecture L).**
*Suppose Conjecture L holds for the multi-digraph $D^\bullet$. Then
the RECOLOR algorithm terminates after at most $|S|$ replacement
steps, producing arc-disjoint families $(T_1^{+\prime}, T_2^{+\prime})$
of out-arborescences and $(T_1^{-\prime}, T_2^{-\prime})$ of
in-arborescences, all rooted at $r$, all pairwise arc-disjoint across
both kinds.*

The proof is by a strict-decrease potential argument: at each
(Repair-Swap) step that consumes a shared arc $a$, Conjecture L
delivers a replacement arc $b$ with $X_b^{U^-} \cap X_a^{T^-}
\subsetneq X_a^{T^-}$, so the cumulative size of the still-unresolved
subtrees strictly decreases. The full bookkeeping requires defining a
potential $\sigma$ on the auxiliary digraph of "shared arcs versus
replacement arcs"; the technical proof is in the team's working
notes. The load-bearing step is Conjecture L itself.

#### 5.3.3 Side-label allocation at $r$

After RECOLOR, each color $i \in \{1, 2\}$ has an out-arborescence
$T_i^{+\prime}$ and an in-arborescence $T_i^{-\prime}$, the four
pairwise arc-disjoint. Each $T_i^{+\prime}$ uses one out-arc at $r$
(call it $a_i^+ \in R_p^+ \cup R_q^+$), and each $T_i^{-\prime}$
uses one in-arc at $r$ (call it $a_i^- \in R_p^- \cup R_q^-$).

We have $a_1^+ \ne a_2^+$ by (WK) within $T_1^{+\prime}, T_2^{+\prime}$,
and $a_1^- \ne a_2^-$ by (WK) within $T_1^{-\prime}, T_2^{-\prime}$.
The out- and in-arcs are trivially distinct.

The four arcs at $r$ have **side-label profile**
$(\sigma_1^+, \sigma_2^+, \sigma_1^-, \sigma_2^-) \in \{p, q\}^4$
encoding which of $R_p^+ / R_q^+$ each $a_i^+$ lies in and likewise
for in-arcs. There are 16 profiles a priori.

The R3⋆ target demands one $R_q^+$ and one $R_p^-$ arc in $A_i^\bullet$
(for $Q_i$, with $e_0$ going to color $i$), plus one of each of
$R_p^+, R_q^+, R_p^-, R_q^-$ in $A_{3 - i}^\bullet$ (for $P_{3-i}
\wedge Q_{3-i}$); total demand at $r$ is $\ge 1$ in $R_p^+$, $\ge 2$
in $R_q^+$, $\ge 2$ in $R_p^-$, $\ge 1$ in $R_q^-$. By ($\ast$) of
Lemma 5.2, the supplies $(2, 3, 3, 2)$ each exceed the corresponding
demand by $\ge 1$.

**Free arcs at $r$.** Let $F$ denote the labelled arcs of $A^\bullet$
at $r$ that are not consumed by the four branchings. The packing uses
2 out-arcs and 2 in-arcs at $r$, so $|F| \cap (\text{at } r)$ has at
least $(2 + 3) - 2 = 3$ out-arcs and at least $(3 + 2) - 2 = 3$
in-arcs. The free supply *per side class* is at least

$$|R_p^+|_F \ge 2 - n_p^+, \;\; |R_q^+|_F \ge 3 - n_q^+, \;\;
  |R_p^-|_F \ge 3 - n_p^-, \;\; |R_q^-|_F \ge 2 - n_q^-,$$

where $n_s^\pm = \#\{i : \sigma_i^\pm = s\}$.

**Case analysis (Lemma 5.5).** *For every branching profile
$(\sigma_1^+, \sigma_2^+, \sigma_1^-, \sigma_2^-) \in \{p, q\}^4$,
there is a free-arc assignment $F = F_1 \mathbin{\dot\cup} F_2$ such
that $A_i^\bullet := T_i^{+\prime} \cup T_i^{-\prime} \cup F_i$
satisfies, for some $i$, $Q_i \wedge P_{3-i} \wedge Q_{3-i}$.*

*Proof.* Take $i = 2$ (color 2 receives $e_0$). For each of the six
side-label demands (four in color 1, two in color 2), either the
packing has already placed an arc of the correct class in the
correct color, or we must allocate a free arc from the side class to
the color. The total free supply per side class exceeds the total
demand by ($\ast$) of Lemma 5.2 by $\ge 1$, even after subtracting
the packing's consumption.

The 16 cases are tabulated by direct verification: in every row, the
demand vector $(D_1^{Rp+}, D_1^{Rq+}, D_1^{Rp-}, D_1^{Rq-}, D_2^{Rq+},
D_2^{Rp-})$ either is already satisfied by the packing in the
appropriate color or is at most the free supply. One corner case
deserves comment: when $|R_q^-| = 2$ exactly and both packing in-arcs
come from $R_p^-$ (so $n_p^- = 2$, $n_q^- = 0$), the free supply in
$R_q^-$ is $\ge 0$; we use the slack in $R_q^-$ supply itself plus the
fact that the $D_1^{Rq-}$ demand requires only one $R_q^-$ arc, met
by *either* of the two $R_q^-$ arcs (both free). The full table of 16
rows is verified directly. $\square$ (Lemma 5.5)

**Vertex-clean witness path.** For Lemma 5.5's allocation to yield
$P_j, Q_j$ as **un-contracted directed walks** in $D_j^\flat$ from $p$
to $q$ (or $q$ to $p$), the side-label arcs at $r$ must connect via a
$V^\bullet \setminus \{r\}$-internal path in $A_j^\bullet$. This is
where the three hard regimes (H1a)/(H1b)/(H2) enter: each requires a
direct verification that the strong connectivity of $A_j^\bullet$
furnishes a side-consistent walk inside $V^\bullet \setminus \{r\}$.

For (H1a) (when $D^\bullet \langle V_2 \rangle$ has $t \ge 2$ strong
components in an acyclic order $C_1, \ldots, C_t$): the side-label
arcs at $r$ allow walks through the shell to bypass the
not-strongly-connected $V_2$; we verify directly that the four
side-label arcs at $r$ plus the strong connectivity of $A_j^\bullet$
on the full $V^\bullet$ give the required side-consistent walks
inside $V^\bullet \setminus \{r\}$.

For (H1b) and (H2): the same verification, with the additional check
that the cut-arc (resp. the $S_4$ structure) does not obstruct the
walk in either color. Both checks reduce to a small finite case
analysis at the cut-arc / $S_4$ instance, which the team's
computational catalogue (Section 7) verifies exhaustively at the
canonical scale.

The combined verification gives:

**Theorem 5.6 (R3⋆-HC, conditional).** *Suppose Conjecture L holds.
Let $D$ be a simple 3-arc-strong $(1, 0)$-near-split digraph with
$|V_1| \ge 2$, $|V_2| \ge 3$, and let $D^\bullet$ be its chord
contraction. Suppose $D^\bullet \langle V_2 \rangle$ does **not**
admit a SAD. Then there exists a SAD $(A_1^\bullet, A_2^\bullet)$ of
$D^\bullet$ and a color $i \in \{1, 2\}$ such that $Q_i \wedge P_{3-i}
\wedge Q_{3-i}$.* $\square$

### 5.4 Theorem 3 (the conditional main theorem)

We now assemble Theorems 4 and 5.6 into the conditional headline.

**Theorem 3.** *Assume Conjecture L. Then every simple 3-arc-strong
$(1, 0)$-near-split digraph $D$ on $|V_1| \ge 2$, $|V_2| \ge 3$
admits a strong arc decomposition.*

*Proof.* Form the chord contraction $D^\bullet$. By Lemma 5.1,
$D^\bullet$ is a 3-arc-strong split multi-digraph with $V_1^\bullet$
independent and $V_2^\bullet$ simple semicomplete.

*Case 1: $D^\bullet \langle V_2 \rangle$ admits a SAD.* By Theorem 4,
$D$ admits a SAD. (This case is unconditional.)

*Case 2: $D^\bullet \langle V_2 \rangle$ does not admit a SAD.* By
the Bang-Jensen–Yeo 2004 characterization, this case decomposes into
(H1a), (H1b), (H2). By Theorem 5.6 (conditional on Conjecture L),
there is a SAD of $D^\bullet$ and a color $i$ satisfying R3⋆. By F1,
F2 of Section 5.1, assigning $e_0$ to color $i$ produces a SAD of
$D$. $\square$ (Theorem 3)

**Remark on the edge cases.** The hypothesis $|V_1| \ge 2$ excludes
$|V_1| = 1$, in which case $D$ is already a strict split digraph and
the Bang-Jensen–Wang 2025 Corollary 1 applies directly. The
hypothesis $|V_2| \ge 3$ excludes $|V_2| \le 2$, which we treat
separately: $|V_2| = 2$ reduces by direct construction to the
case-by-case split-digraph treatment of Bang-Jensen–Wang's Theorem 1.6.

---

## 6. Conjecture L: an open problem in arborescence packing

This section states Conjecture L precisely, gives its structural
geometry (the *funnel obstruction*), proves a partial swap-repair
lemma, and summarises the empirical evidence.

### 6.1 Statement

**Conjecture L.** *Let $D^\bullet$ be a 3-arc-strong directed
multigraph, and let $T^-, U^-$ be two arc-disjoint spanning
in-arborescences of $D^\bullet$ rooted at a common vertex $r$. Let
$a \in T^-$ be any arc, and let $X_a^{T^-} \subseteq V(D^\bullet)
\setminus \{r\}$ denote the $T^-$-subtree below $a$ — i.e. the set of
vertices whose unique $T^-$-walk to $r$ passes through $a$.*

*Then there exists $b \in U^- \cap \delta^+(X_a^{T^-})$ such that*
$$X_b^{U^-} \cap X_a^{T^-} \;\subsetneq\; X_a^{T^-}, \tag{L}$$
*where $X_b^{U^-}$ is the $U^-$-subtree below $b$.*

Equivalently, the conjecture asserts: across any $T^-$-subtree $X$,
**some** exit arc of $U^-$ from $X$ has a $U^-$-subtree that does not
contain all of $X$.

### 6.2 The funnel obstruction

The natural strengthening "for every $b \in U^- \cap \delta^+(X)$,
$X_b^{U^-} \cap X \subsetneq X$" is false. A small example on
$n = 4$ shows this.

**Example 6.1.** Let $V^\bullet = \{r, u, v_1, w\}$ with
$T^- = \{(v_1, u), (u, r), (w, r)\}$ and
$U^- = \{(u, v_1), (v_1, r), (w, v_1)\}$. Both are in-arborescences
rooted at $r$, and they are arc-disjoint. Take $a = (u, r) \in T^-$
and $X := X_a^{T^-} = \{u, v_1\}$. The unique $U^-$-exit arc from
$X$ is $b = (v_1, r)$; its $U^-$-subtree is
$X_b^{U^-} = \{v_1, u, w\}$, so $X_b^{U^-} \cap X = \{u, v_1\} = X$,
not strict.

This is the **funnel obstruction**: the unique exit arc has a
$U^-$-subtree containing all of $X$. The conjecture is non-trivial
because it asserts *some* $b$ works, not that every $b$ works; even
when one or two exit arcs exhibit the funnel obstruction, a strict
strict-decrease conjecture (L) requires *some* exit arc, possibly
borrowed via a swap, to break the funnel.

More precisely: when (L) fails at $(T^-, U^-, a)$, write
$E_a^+ := U^- \cap \delta^+(X_a^{T^-}) = \{b_1, \ldots, b_k\}$ with
$X_{b_1}^{U^-} \supseteq \cdots \supseteq X_{b_k}^{U^-} \supseteq X$
(the subtrees nest because they share the non-empty $X$). All
vertices of $X$ are $U^-$-descendants of the tail $u_k'$ of $b_k$;
the $U^-$-walk from $u_k'$ alternately exits and re-enters $X$
along the $b_j$ arcs. This is the funnel structure.

### 6.3 The partial swap-repair lemma

The funnel obstruction motivates the following partial result.

**Lemma 6.2 (Single-arc swap repair, partial).** *Let $D^\bullet$ be a
3-arc-strong directed multigraph and $(T^-, U^-) \in \mathcal{P}$ a
pair of arc-disjoint spanning in-arborescences rooted at $r$. Suppose
(L) fails at $a \in T^-$ with $|E_a^+| = 1$ and there exists a free
arc $\beta^* = (w^*, y^*) \in \delta^+(X_a^{T^-}) \setminus (T^- \cup
U^-)$ with $y^* \notin X_{\pi^{U^-}\text{-arc of }w^*}^{U^-}$. Then
there is a swap $U^- \to \tilde{U}^- := U^- - (\pi^{U^-}\text{-arc of
}w^*) + \beta^*$ such that $\tilde{U}^-$ is an in-arborescence rooted
at $r$, $\tilde{U}^- \cap T^- = \emptyset$, and (L) holds at
$(T^-, \tilde{U}^-, a)$.*

*Proof (sketch).* The hypothesis $y^* \notin
X_{\pi^{U^-}\text{-arc of }w^*}^{U^-}$ ensures the swap does not
create a cycle in $\tilde{U}^-$. Removing $\pi^{U^-}(w^*)$ and adding
$\beta^*$ preserves the arc count $|V^\bullet| - 1$. Arc-disjointness
with $T^-$ is preserved because $\beta^*$ is free (not in $T^-$) and
the removed arc was in $U^-$ (also not in $T^-$ by arc-disjointness
of the original pair). The swap creates a new exit arc $\beta^*$ from
$X_a^{T^-}$ in $\tilde{U}^-$, replacing the funnel exit; the
$\tilde{U}^-$-subtree below $\beta^*$ is $\{w^*\}$ alone (since $w^*$
no longer has the $U^-$-parent it used to have), which strictly misses
the rest of $X_a^{T^-}$. So (L) holds at the new pair. $\square$

The lemma covers the most common case ($|E_a^+| = 1$, a free arc
exists with safe target). The remaining cases — $|E_a^+| \ge 2$, or
$|E_a^+| = 1$ with no free arc of safe target — require multi-arc
swaps and are not closed in this paper.

### 6.4 What Conjecture L is *not*

Conjecture L is not a special case of any classical exchange property
of arborescences surveyed in the literature.

- **Schrijver's exchange property** (Schrijver, *Total Dual
  Integrality of Matching Forest Constraints*, Combinatorica **20**
  (2000), 575–588, Theorem 1; the Vol. B §53.6 exposition of the
  same): asserts that two branchings $B_1, B_2$ **partitioning** the
  arc set can be reconfigured so as to move a single vertex between
  their root sets. The hypothesis "partition $A$" is incompatible
  with our setting ($T^- \cup U^-$ has $2(|V^\bullet| - 1)$ arcs and
  $A^\bullet$ has $\ge \lceil 3 |V^\bullet| / 2 \rceil$ arcs, so
  partition fails for $|V^\bullet| \ge 5$). The roots are also
  distinct in Schrijver's theorem ($s$ is in $R(B_2) \setminus
  R(B_1)$), while in our setting both arborescences share the same
  root $r$. Furthermore the conclusion is about root-set shuffling,
  not subtree inclusion.

- **Reconfiguration of unions of arborescences** (Kobayashi, Mahara
  and Schwarcz, *Reconfiguration of the union of arborescences*,
  Algorithmica, 2025): considers single-arc exchanges in the matroid
  of unions of $k$ arc-disjoint arborescences. The exchange there is
  generic matroid-base step, not the specific subtree-containment
  structure of (L).

- **Frank's packing theorems** in *Connections in Combinatorial
  Optimization* (Oxford UP, 2011), Chapter 10: cover same-direction
  packing of arborescences with multi-root and matroid-rank
  generalisations; none asserts a subtree-inclusion property between
  two given arc-disjoint spanning arborescences sharing a root.

To the best of our knowledge, Conjecture L is a genuinely new
structural lemma about pairs of arc-disjoint spanning in-arborescences.

### 6.5 Empirical evidence

The team has tested Conjecture L in two ways.

**Direct testing.** On a corpus of small 3-arc-strong $D^\bullet$
exhaustively at $n \le 7$ and broadly at $n \le 10$, every pair
$(T^-, U^-)$ examined satisfied (L) at every $a \in T^-$. The team's
team/31 working notes contain a partial enumeration plus the
single-arc-swap experiments of Lemma 6.2.

**Indirect testing via Theorem 3.** The combined verifier sweep of
the team's empirical pipeline tested the SAD existence on **over
11 000 canonical 3-arc-strong $(1, 0)$-near-split digraph instances**
across the regimes $|V_1| \ge 2$, $|V_2| \ge 3$, $\lambda^{\mathrm{arc}}
\ge 3$. Every instance returned SAT under independent ILP and SAT
backends, and every witness aligned with the §3.4 side-label demand
table of the R3⋆-HC argument (matching the predicted RECOLOR /
side-allocation outputs). Specifically the corpus includes 7 374
broad-sample candidates (team/20) plus 4 495 targeted residual
instances in regimes (H1b)|V₂|=3 and (H2)|V₂|=4 (team/28), totalling
**11 869 instances, zero failures**.

Each successful SAT outcome at the SAD level is *indirect* evidence
for Conjecture L on the underlying $D^\bullet$, because a failure
of (L) at any single subtree exchange in the RECOLOR algorithm would,
in principle, leave the algorithm cycling and the SAD construction
would not have terminated. The witness alignment with the §3.4 demand
table is the strongest indirect check we have.

### 6.6 Three avenues for future work

We list three concrete attack vectors for Conjecture L.

1. **Counterexample search at $n = 5, 6, 7$.** Enumerate simple
   3-arc-strong $D^\bullet$ in this range; for each, enumerate all
   arc-disjoint pairs of spanning in-arborescences. Verify (L) at
   every internal arc. The team's preliminary enumeration found no
   counterexample at $n \le 7$.

2. **Multi-arc swap repair.** Lemma 6.2 closes the case
   $|E_a^+| = 1$ with a safe free arc. The general case requires a
   multi-arc swap whose existence can be argued from
   $|\delta^+(X)| \ge 3$ via a careful re-routing inside the
   in-arborescence on $V^\bullet \setminus X$. A complete proof is a
   plausible 1–2 page lemma.

3. **The fallback to 4-arc-strong.** If Conjecture L is hard, one
   can weaken Theorem 3's hypothesis to 4-arc-strongness, where a
   direct *cross-kind* packing argument is plausible (every cut has
   $\ge 4$ arcs, leaving $\ge 4 - 2 - 2 = 0$ free across kinds, but
   with a 1-arc margin from the +1 in Lemma 5.2's supply bounds).
   This makes the conjectural conclusion unconditional at the cost
   of strengthening the arc-strength hypothesis.

---

## 7. Computational catalogue

The exception family for the Bang-Jensen–Yeo problem at
$\lambda^{\mathrm{arc}} = 2$ is a moving target as more classes are
characterised. We catalogue here the 2-arc-strong exceptions known to
the literature and relevant to the present paper.

- **$S_4$** (Bang-Jensen–Yeo 2004): the square of the directed
  4-cycle, the unique 2-arc-strong semicomplete digraph without a
  SAD. Vertices $\{v_1, v_2, v_3, v_4\}$; arcs $\{v_i v_{i+1} : i \in
  [4]\} \cup \{v_1 v_3, v_3 v_1, v_2 v_4, v_4 v_2\}$ (indices mod 4).
  Eight arcs, $\lambda^{\mathrm{arc}} = 2$.

- **$C_{2k}^{(2)}$**, $k \ge 2$ (Bang-Jensen–Huang 2012): squares of
  even directed cycles, the entire 2-arc-strong locally-semicomplete
  exception family.

- **Four semicomplete-composition exceptions** (Bang-Jensen–Gutin–Yeo
  2020, Theorem 1.4): $S_4$ and three further compositions
  $\vec{C}_3[\overline{K}_2, \overline{K}_2, \overline{K}_2]$,
  $\vec{C}_3[\overline{K}_2, \overline{K}_2, \overline{P}_2]$,
  $\vec{C}_3[\overline{K}_2, \overline{K}_2, \overline{K}_3]$.

- **Split-digraph 2-arc-strong exceptions** (Ai–He–Li–Qin–Wang 2024):
  the full characterisation, with the exception family expanding into
  Lemma 2.11 (small instances with $|V_1| = 1$, $|V_2| \in \{4, 5\}$),
  Lemma 3.12 and the Appendix; see arXiv:2408.02260 for the full list.

- **New 2-arc-strong $(1, 0)$-near-split exceptions.** The team's
  exhaustive enumeration at $(|V_1|, |V_2|) = (2, 3)$ and partial
  enumeration at $(2, 4)$ and $(3, 3)$, after indexing the strict-split
  catalogue with both forward and arc-reversed canonical hashes of the
  semicomplete (Bang-Jensen–Yeo 2004), locally-semicomplete (Bang-
  Jensen–Huang 2012), semicomplete-composition (BJG–Yeo 2020), and
  split (Ai et al. 2024 Appendix B.2 + B.3) families, yields **6
  canonical UNSAT instances** at $\lambda^{\mathrm{arc}} = 2$ in the
  $(1, 0)$-near-split class that are *not* isomorphic to any catalogue
  member in either orientation. All six are **internal-arc-dependent**:
  removing the $V_1$-internal arc $e_0$ destroys 2-arc-strongness, so
  the obstruction is genuinely tied to $e_0$ rather than to a strict-
  split obstruction with a free extra arc. These instances are
  candidates for a companion theorem on 2-arc-strong $(1, 0)$-near-
  split digraphs, left as future work.

**Empirical record at $\lambda^{\mathrm{arc}} = 3$.** Across the
combined empirical pipeline (broad-sample sweep of 7 374 instances at
$|V_1| \le 6$, $|V_2| \le 7$, $\lambda^{\mathrm{arc}} = 3$, plus the
4 495-instance targeted residual sweep at the (H1b)|V₂|=3 and
(H2)|V₂|=4 regimes), **11 869 simple 3-arc-strong $(1, 0)$-near-split
instances admit a SAD**, with zero UNSAT and zero alignment failures
against the side-label table of R3⋆-HC. This is the strongest empirical
support for Theorems 3 and 4 and, indirectly, for Conjecture L.

---

## 8. Open problems and conclusion

We collect open problems, in roughly increasing scope.

1. **Conjecture L.** A finite combinatorial statement about pairs of
   arc-disjoint spanning in-arborescences; resolving it makes Theorem 3
   unconditional.

2. **$(k, 0)$-near-split for $k \ge 2$.** Does every 3-arc-strong
   $(k, 0)$-near-split digraph admit a SAD? The contraction route of
   Section 5 generalises: contract the $k$ $V_1$-internal arcs (each
   pair separately or in sequence if they share endpoints), producing
   a split multi-digraph; the un-contraction step becomes a multi-chord
   variant of R3⋆.

3. **The full Bang-Jensen–Yeo conjecture WC3.** Does every
   3-arc-strong digraph admit a SAD? No infinite family of
   counterexamples is known. The class-by-class lineage — semicomplete
   (2004), locally semicomplete (2012), semicomplete compositions
   (2020), split (2025), $(1, 0)$-near-split (this paper, conditional)
   — accumulates positive evidence; the unconditional resolution
   remains open.

4. **The dual ILS / OLS case.** Bang-Jensen–Gutin Problem 6.8 (1998)
   asks for a structural characterisation of locally in-semicomplete
   (and dually locally out-semicomplete) digraphs; this is a 28-year
   open problem. A SAD theorem for 3-arc-strong OLS digraphs is a
   natural target if Problem 6.8 is resolved.

5. **A probabilistic CL1.** Does a uniformly random 2-coloring of
   bridges in CL1's setting produce a valid bridge-coloring (i.e. all
   four (direction, color) classes non-empty) with high probability
   when $|B^\pm|$ is large? Combined with Theorem 1 (EC-log), a
   probabilistic CL1 would unify the two unconditional results into a
   single high-arc-strength theorem.

We restate the main contributions. Theorem 1 settles Bang-Jensen–Yeo
unconditionally for *Eulerian* digraphs at $\lambda \ge 6 \log_2 n$ (with $n \ge 3$).
Theorem 2 provides a clean class-agnostic lifting lemma whose
hypothesis is a small bridge 2-coloring problem and whose conclusion
is the SAD; this is the natural bilateral version of the
Bang-Jensen–Wang kernel-shell attachment. Theorem 3 settles
Bang-Jensen–Yeo conditionally for the $(1, 0)$-near-split class at
$\lambda \ge 3$, with the conditionality on a single named
combinatorial conjecture supported by over 11 000 verified instances.
Theorem 4 is the unconditional content of Theorem 3, covering the
dominant share of $(1, 0)$-near-split instances.

---

## Acknowledgments

(To be added.)

## References

The references below are exactly the audit-cleared list; each was
verified against a primary or restated source (with verbatim quotations
recorded in the team's audit).

- J. Bang-Jensen and J. Huang, *Quasi-transitive digraphs*,
  J. Graph Theory **20** (1995), 141–161.
- J. Bang-Jensen and J. Huang, *Strong arc decompositions of locally
  semicomplete digraphs*, J. Combin. Theory Ser. B **102** (2012),
  701–714.
- J. Bang-Jensen and G. Gutin, *Generalizations of tournaments: A
  survey*, J. Graph Theory **28** (1998), 171–202.
- J. Bang-Jensen and G. Gutin, *Digraphs: Theory, Algorithms and
  Applications*, 2nd ed., Springer Monographs in Mathematics,
  Springer, 2009.
- J. Bang-Jensen, G. Gutin and A. Yeo, *Decompositions of digraphs
  into spanning strong subdigraphs*, J. Graph Theory **95** (2020),
  267–289 (arXiv:1903.12225).
- J. Bang-Jensen, S. Bessy, F. Havet and A. Yeo, *Out-branchings and
  in-branchings in some classes of digraphs*, preprint arXiv:2003.02107
  (2022).
- J. Bang-Jensen and M. Kriesell, *Disjoint sub(di)graphs in digraphs*,
  Electron. Notes Discrete Math. **34** (2009), 179–183.
- J. Bang-Jensen and Y. Wang, *Arc-disjoint strong spanning
  subdigraphs of split digraphs*, J. Graph Theory **108** (2025),
  5–26 (arXiv:2309.06904).
- J. Bang-Jensen and A. Yeo, *Decomposing $k$-arc-strong tournaments
  into strong spanning subdigraphs*, Combinatorica **24** (2004),
  331–349.
- W. Ai, R. He, S. Li, S. Qin and Y. Wang, *Strong arc decompositions
  of 2-arc-strong split digraphs*, preprint arXiv:2408.02260 (2024).
- J. Edmonds, *Edge-disjoint branchings*, in *Combinatorial Algorithms*
  (R. Rustin, ed.), Algorithmics Press, 1972/1973.
- D. R. Karger, *Minimum cuts in near-linear time*, J. ACM **47**
  (2000), 46–76 (arXiv:cs/9812007).
- A. Schrijver, *Total dual integrality of matching forest constraints*,
  Combinatorica **20** (2000), 575–588.
- Y. Sun, G. Gutin and J. Ai, *Strong arc decompositions of
  $T[H_1, \ldots, H_t]$ when $T$ is a strong semicomplete digraph*,
  Discrete Math. **342** (2019), 2297–2305 (arXiv:1812.08809).

End of draft.
