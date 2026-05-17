# 26 — Side-compatible SAD lemma, kernel-shell case

Author: Structural Digraph Specialist
Date: 2026-05-17
Status: First positive sub-result on the R3⋆ residual gap of
`team/21_near_split_contraction_proof.md` §4. Closes R3⋆ — and hence
Theorem 1 — **in the kernel-shell case** where $D^\bullet \langle V_2
\rangle$ already admits a SAD. The splitting-off cases remain open and
are scoped in §7. Successor to `team/22_r3star_bjwang_inspection.md`
(diagnosis of BJ–Wang side-blindness) and `team/21_*` (conditional
Theorem 1). Prior references: `team/22_*` §§2–3 (notation); `team/21_*`
§§1.2, 3.1–3.4, 4.1–4.6; `team/05_audit.md` Appendices A.1, A.5 Source
1, A.8; `team/19_*` §3.1.

---

## §1 — Setup

### §1.1 Standing hypotheses

Throughout this file: $D = (V, A)$ is a simple 3-arc-strong
$(1,0)$-near-split digraph with split partition $V = V_1 \dot\cup V_2$,
$|V_1| \ge 2$, $|V_2| \ge 3$, unique $V_1$-internal arc $e_0 = (p, q)$,
$\lambda^{\text{arc}}(D) \ge 3$ (`team/21_*` §1.1). $D^\bullet$ is the
chord contraction with contracted vertex $r := p^\bullet$ (`team/21_*`
§1.2); $V_1^\bullet = (V_1 \setminus \{p, q\}) \cup \{r\}$, $V_2^\bullet
= V_2$. By `team/21_*` §§3.1–3.3, $D^\bullet$ is a 3-arc-strong split
multi-digraph with $V_1^\bullet$ independent and $V_2^\bullet$ simple
semicomplete.

### §1.2 Notation imported verbatim from `team/22_*` §§2–3

We do not redefine. Use exactly: $\pi$ and $\pi^{-1}$ (contraction map
and un-contraction on labels); $D_i^\flat := (V, \pi^{-1}(A_i^\bullet))$
(un-contracted color-$i$ subdigraph of $D - e_0$); $P_i$ ("$D_i^\flat$
contains $p \to q$"); $Q_i$ ("$D_i^\flat$ contains $q \to p$"); the
four label classes $R_p^+, R_q^+, R_p^-, R_q^-$ at $r$ defined in
`team/22_*` §3 (out from $p$ / out from $q$ / in to $p$ / in to $q$,
respectively).

The four sets partition the labelled arcs of $A^\bullet$ at $r$: each
non-chord arc at $\{p, q\}$ in $D$ contributes exactly one labelled arc
at $r$, with its label recording preimage endpoint and direction.

### §1.3 The liftability target

R3⋆ (`team/22_*` §2): $\exists i \in \{1, 2\}$ such that
$Q_i \wedge P_{3-i} \wedge Q_{3-i}$, equivalently
$(Q_1 \wedge P_2 \wedge Q_2) \vee (Q_2 \wedge P_1 \wedge Q_1)$.

Assigning $e_0$ to color $i$ then supplies $P_i$ on top of the held
$Q_i$, so color $i$ is good; color $3-i$ is already good. By `team/22_*`
Fact F1, both colors strongly span $V$.

---

## §2 — Statement of the kernel-shell lemma

The *kernel-shell case* is the sub-case of R3⋆ in which $D^\bullet
\langle V_2 \rangle$ already admits a SAD, so the kernel $X := V_2$ of
the BJ–Wang Lemma 2.4 attachment is non-trivial. (Recall: `team/22_*`
§3, **the partial positive statement** at the end of §3 anticipates
this is the easy case.)

**Lemma R3⋆-KS (kernel-shell side-compatible SAD).** *Let $D$ be a
simple 3-arc-strong $(1,0)$-near-split digraph with $|V_2| \ge 3$ and
chord $e_0 = (p, q)$. Let $D^\bullet$ be its chord contraction with
contracted vertex $r = p^\bullet$. If $D^\bullet \langle V_2 \rangle$
admits a SAD $(B_1, B_2)$, then there exist a SAD
$(A_1^\bullet, A_2^\bullet)$ of $D^\bullet$ extending $(B_1, B_2)$ (i.e.
$A_i^\bullet \cap A(D^\bullet \langle V_2 \rangle) = B_i$) and a color
$i \in \{1, 2\}$ such that*

$$Q_i \wedge P_{3-i} \wedge Q_{3-i}.$$

The conclusion is the R3⋆ liftability condition of `team/22_*` §2.

The construction will follow the BJ–Wang Lemma 2.4 template (verbatim
quote: `team/05_audit.md` Appendix A.1 / A.5 Source 1 line 925; analysis:
`team/22_*` §3), but with **deliberate choice** of the four attachment
classes at $r$ and of the assignment of the remaining labelled arcs at
$r$ to colors. The construction is elementary; the content is a counting
verification that supply exceeds demand on each of the four label
classes $R_p^+, R_q^+, R_p^-, R_q^-$.

We will use the following explicit form of the kernel-shell attachment
argument. It is the proof of BJ-Wang Lemma 2.4 with the only feature
needed here made visible: for strongness, a color needs one selected
out-arc from each shell vertex to the kernel and one selected in-arc
from the kernel to that shell vertex. The endpoints need not be distinct
across the two colors when parallel labelled arcs exist; the selected
arcs themselves must be distinct because they are being partitioned.

**Attachment observation.** Let $H$ be a directed multigraph, let
$X \subseteq V(H)$, and suppose $H \langle X \rangle$ has a SAD
$(B_1,B_2)$. Suppose that for every $s \in V(H)\setminus X$ and every
$j\in\{1,2\}$ we prescribe a set $C_j(s)$ of labelled arcs incident
with $s$ such that:

- the sets $C_j(s)$ are pairwise disjoint as labelled arc sets;
- $C_j(s)$ contains at least one arc $s\to x_j^+(s)$ with
  $x_j^+(s)\in X$;
- $C_j(s)$ contains at least one arc $x_j^-(s)\to s$ with
  $x_j^-(s)\in X$.

Put $C_j(s)$ in color $j$, put $B_j$ in color $j$, and distribute every
remaining arc of $H$ arbitrarily between the two colors. Then both color
classes are spanning strong subdigraphs of $H$.

Indeed, in color $j$, every shell vertex $s$ reaches $X$ by
$s\to x_j^+(s)$ and is reached from $X$ by $x_j^-(s)\to s$, while
$B_j$ is strong on $X$. Hence any vertex reaches any other by going
through $X$ if necessary. Adding arbitrary leftover arcs cannot destroy
strong connectivity.

---

## §3 — Counting argument

### §3.1 Lower bounds on the four label classes at $r$

We derive precise lower bounds on $|R_p^+|, |R_q^+|, |R_p^-|, |R_q^-|$
from 3-arc-strongness of $D$ and the $(1,0)$-near-split structure.

For each case, recall: by (NS3) the only $V_1$-internal arc is $e_0 =
(p, q)$. The chord contributes to $d_D^+(p)$ and to $d_D^-(q)$, but not
to $d_D^+(q)$ or $d_D^-(p)$. The chord is deleted under contraction, so
it never produces a labelled arc at $r$.

*Out-arcs from $p$.* $d_D^+(p) \ge 3$. One out-arc, $e_0$, lies in
$V_1$; the rest, $\ge 2$, go to $V_2$ (since outside $\{q\}$ no other
$V_1$-target is available to $p$ by (NS3)). Each $V_2$-bound out-arc
$(p, y)$ contributes a labelled arc $\pi((p, y)) = (r, y) \in R_p^+$;
distinctness of heads follows from simplicity of $D$. Hence
$|R_p^+| \ge 2$.

*In-arcs to $q$.* $d_D^-(q) \ge 3$. One in-arc, $e_0$, lies in $V_1$;
the rest, $\ge 2$, come from $V_2$. Each contributes to $R_q^-$. Hence
$|R_q^-| \ge 2$.

*Out-arcs from $q$.* $d_D^+(q) \ge 3$. No out-arc of $q$ lies in $V_1$
(by (NS3) $e_0$ leaves $p$ not $q$; no other $V_1$-internal arc exists).
All $d_D^+(q) \ge 3$ go to $V_2$. Each contributes to $R_q^+$. Hence
$|R_q^+| \ge 3$.

*In-arcs to $p$.* $d_D^-(p) \ge 3$. No in-arc of $p$ lies in $V_1$ ($e_0$
enters $q$ not $p$; (NS3) forbids a second $V_1$-internal arc). All
$d_D^-(p) \ge 3$ come from $V_2$. Each contributes to $R_p^-$. Hence
$|R_p^-| \ge 3$.

*Summary:*
$$|R_p^+| \ge 2, \quad |R_q^+| \ge 3, \quad |R_p^-| \ge 3, \quad |R_q^-| \ge 2. \tag{$\ast$}$$

The bounds are *asymmetric* in the diagonal pairs: the chord $e_0$
subtracts 1 from $d^+(p)$ and from $d^-(q)$, but not from $d^+(q)$ or
$d^-(p)$. The downstream demand calculation is symmetric enough that
the conclusion holds with these bounds.

### §3.2 Demand on each label class

We aim to find a SAD $(A_1^\bullet, A_2^\bullet)$ of $D^\bullet$ and a
color $i$ such that, after un-contraction and assignment of $e_0$ to
color $i$:

- Color $i$ holds $Q_i$ — i.e., $D_i^\flat$ has a $q \to p$ path. By
  `team/22_*` §2 ("direction bookkeeping"), a clean $q \to p$ witness
  in color $i$ requires an out-arc at $r$ in $A_i^\bullet$ whose
  preimage *leaves $q$* (so a $R_q^+$ arc) **and** an in-arc at $r$ in
  $A_i^\bullet$ whose preimage *enters $p$* (so a $R_p^-$ arc),
  together with a $V_2$-path connecting them in $A_i^\bullet$.
- Color $3 - i$ holds both $P_{3-i}$ and $Q_{3-i}$ — i.e., $D_{3-i}^\flat$
  has both a $p \to q$ path and a $q \to p$ path. By the same direction
  bookkeeping: a clean $p \to q$ witness needs a $R_p^+$ arc out of $r$
  **and** a $R_q^-$ arc into $r$, both in $A_{3-i}^\bullet$; a clean
  $q \to p$ witness needs $R_q^+$ **and** $R_p^-$ in $A_{3-i}^\bullet$.

Compiling demands per label class:

| label  | required for color $i$ | required for color $3-i$ | **total** |
|--------|------------------------|---------------------------|-----------|
| $R_p^+$ | — (color $i$ gets $P_i$ from $e_0$) | 1 ($p\to q$ witness) | 1 |
| $R_q^+$ | 1 ($q\to p$ witness) | 1 ($q\to p$ witness) | 2 |
| $R_p^-$ | 1 ($q\to p$ witness) | 1 ($q\to p$ witness) | 2 |
| $R_q^-$ | — | 1 ($p\to q$ witness) | 1 |

The "$V_2$-path connecting them in $A_i^\bullet$" qualifier is supplied
by the assumption that $(B_1, B_2) = (A_1^\bullet \cap A(D^\bullet
\langle V_2 \rangle), A_2^\bullet \cap A(D^\bullet \langle V_2 \rangle))$
is a SAD of $D^\bullet \langle V_2 \rangle$: each $B_j$ is spanning
strong on $V_2$, so any pair of distinct $V_2$-vertices is mutually
reachable inside $B_j$.

### §3.3 Supply meets demand

From ($\ast$) and §3.2:

| label  | supply | demand | slack |
|--------|--------|--------|-------|
| $R_p^+$ | $\ge 2$ | $1$ | $\ge 1$ |
| $R_q^+$ | $\ge 3$ | $2$ | $\ge 1$ |
| $R_p^-$ | $\ge 3$ | $2$ | $\ge 1$ |
| $R_q^-$ | $\ge 2$ | $1$ | $\ge 1$ |

Every label class has supply at least one more than demand. So a valid
allocation exists; in fact, on each class there is **strict slack** of
at least one arc. All slack arcs can be distributed arbitrarily, because
the attachment observation has already supplied the in/out attachments
needed for strongness in each color.

### §3.4 Explicit attachment and assignment

We now construct $(A_1^\bullet, A_2^\bullet)$ explicitly. Choose a
labelling so that color **2** is the "$q$-reaching" color (the one that
will receive $e_0$ on un-contraction) and color **1** is the "good"
color. Thus $i = 2$ below.

**Step 1: choose the SAD on the kernel $X = V_2$.**

By hypothesis, $D^\bullet \langle V_2 \rangle$ has a SAD $(B_1, B_2)$.
Each $B_j$ is a spanning strong subdigraph of $D^\bullet \langle V_2
\rangle = D \langle V_2 \rangle$ (the contraction does not touch
$V_2$-internal arcs; `team/21_*` §3.3). Fix $(B_1, B_2)$ and set, for
each $j \in \{1, 2\}$, $A_j^\bullet \cap A(D^\bullet \langle V_2 \rangle)
:= B_j$.

**Step 2: attach the shell $V_1^\bullet$.**

For each shell vertex $v \in V_1^\bullet$ we will use the attachment
observation above. For $v \in V_1 \setminus \{p,q\}$, the required
two in-arcs and two out-arcs are immediate: by 3-arc-strongness
$d_D^\pm(v)\ge 3$, and by (NS3) no arc incident with such a $v$ is
$V_1$-internal, so all these arcs go between $v$ and $V_2$. Choose one
in-arc and one out-arc for each color, and distribute the rest
arbitrarily.

For $v = r$, we do not appeal to the literal neighbor formulation of
BJ-Wang Lemma 2.4. We use labelled arcs directly, because after
contracting $p,q$ there may be parallel arcs with the same $V_2$
endpoint. Parallelism is harmless for the attachment observation:
strongness needs one labelled out-arc and one labelled in-arc per
color, not distinct endpoints. The required labelled arcs are chosen
side-compatibly in Step 3.

**Step 3: assignments at $r$.**

By ($\ast$) we have, in $A^\bullet$, the labelled arcs at $r$:

- $R_p^+ \subseteq \{r \to y : y \in V_2\}$ with $|R_p^+| \ge 2$;
- $R_q^+ \subseteq \{r \to y : y \in V_2\}$ with $|R_q^+| \ge 3$;
- $R_p^- \subseteq \{x \to r : x \in V_2\}$ with $|R_p^-| \ge 3$;
- $R_q^- \subseteq \{x \to r : x \in V_2\}$ with $|R_q^-| \ge 2$.

Distribute as follows.

**Color 2 (the $q$-reaching color, will receive $e_0$):**
- Pick one arc $\alpha_2^+ \in R_q^+$ (preimage $q \to y_2$ for some
  $y_2 \in V_2$). Add to $A_2^\bullet$.
- Pick one arc $\alpha_2^- \in R_p^-$ (preimage $x_2 \to p$ for some
  $x_2 \in V_2$). Add to $A_2^\bullet$.

**Color 1 (the good color):**
- Pick one arc $\beta_1^{+,p} \in R_p^+$ (preimage $p \to y_1^p$). Add
  to $A_1^\bullet$.
- Pick one arc $\beta_1^{+,q} \in R_q^+ \setminus \{\alpha_2^+\}$
  (available since $|R_q^+| \ge 3 \ge 2$). Add to $A_1^\bullet$.
- Pick one arc $\beta_1^{-,p} \in R_p^- \setminus \{\alpha_2^-\}$
  (available since $|R_p^-| \ge 3 \ge 2$). Add to $A_1^\bullet$.
- Pick one arc $\beta_1^{-,q} \in R_q^-$. Add to $A_1^\bullet$.

**Leftover at $r$:** all remaining labelled arcs at $r$ (in any of
$R_p^+, R_q^+, R_p^-, R_q^-$ not assigned above) are distributed
arbitrarily between the two colors. By Lemma 2.4's standard "adding
arcs to a strong digraph preserves strong connectivity" remark
(`team/22_*` §3 Lemma 2.4 construction step 3), this preserves the
strong-on-$V^\bullet$ property of both colors in $D^\bullet$.

**Verification that this is a valid attachment at $r$:**
Color 2 has one selected in-attachment $\alpha_2^-$ and one selected
out-attachment $\alpha_2^+$. Color 1 has at least one selected
in-attachment and at least one selected out-attachment; in fact it has
two of each, because it must witness both $P_1$ and $Q_1$ after
un-contraction. The selected labelled arcs are pairwise distinct:
different $R$-classes are disjoint, and the two selections inside
$R_q^+$ and inside $R_p^-$ were explicitly chosen to be different.
Thus the attachment observation applies at $r$. No distinct-endpoint
claim is needed.

(Distinctness of the four $\beta_1$ arcs follows from each being in a
distinct $R$-class. Distinctness of $\beta_1^{+,q}$ from $\alpha_2^+$
and of $\beta_1^{-,p}$ from $\alpha_2^-$ is by explicit choice. The
single attachment of color 2 ($\alpha_2^+, \alpha_2^-$) uses one arc
per direction.)

**Step 4: verify side constraints.**

We claim color 2 has $Q_2$ (the $q$-reaching property), and color 1 has
$P_1$ and $Q_1$ (good).

*Color 2 has $Q_2$.* The labelled arcs assigned to $A_2^\bullet$ at
$r$ include $\alpha_2^+ \in R_q^+$ (preimage $q \to y_2$, $y_2 \in V_2$)
and $\alpha_2^- \in R_p^-$ (preimage $x_2 \to p$, $x_2 \in V_2$). The
SAD $B_2 \subseteq A_2^\bullet$ on $V_2$ is spanning strong on $V_2$,
hence contains a directed $y_2 \to x_2$ path inside $V_2$ (possibly
trivial if $y_2 = x_2$, in which case zero arcs). In $D_2^\flat$, the
preimages give: $(q, y_2)$ — the preimage of $\alpha_2^+$; a $y_2 \to
x_2$ path internal to $V_2$ — the preimages of the $B_2$-arcs are
$V_2$-internal arcs, fixed by $\pi$; $(x_2, p)$ — the preimage of
$\alpha_2^-$. Concatenated, this is a $q \to p$ directed walk in
$D_2^\flat$. Hence $Q_2$ holds.

*Color 1 has $P_1$.* The labelled arcs assigned to $A_1^\bullet$ at
$r$ include $\beta_1^{+,p} \in R_p^+$ (preimage $p \to y_1^p$) and
$\beta_1^{-,q} \in R_q^-$ (preimage $x_1^q \to q$), with $y_1^p, x_1^q
\in V_2$. By strongness of $B_1$ on $V_2$, there is a $y_1^p \to x_1^q$
directed path inside $V_2$ in $B_1$. Concatenation in $D_1^\flat$:
$(p, y_1^p)$, then $V_2$-internal path $y_1^p \to x_1^q$, then $(x_1^q,
q)$. This is a $p \to q$ directed walk in $D_1^\flat$. Hence $P_1$
holds.

*Color 1 has $Q_1$.* Symmetric: the labelled arcs assigned to
$A_1^\bullet$ at $r$ include $\beta_1^{+,q} \in R_q^+$ (preimage $q
\to y_1^q$) and $\beta_1^{-,p} \in R_p^-$ (preimage $x_1^p \to p$),
$y_1^q, x_1^p \in V_2$. By strongness of $B_1$ on $V_2$, there is a
$y_1^q \to x_1^p$ path inside $B_1$. Concatenation in $D_1^\flat$:
$(q, y_1^q)$, $V_2$-path $y_1^q \to x_1^p$, $(x_1^p, p)$. This is a
$q \to p$ directed walk in $D_1^\flat$. Hence $Q_1$ holds.

Therefore $Q_2 \wedge P_1 \wedge Q_1$, which is the R3⋆ liftability
condition with $i = 2$. $\square$ (proof-of-§3 outline).

---

## §4 — Proof of Lemma R3⋆-KS

We assemble §§1–3 into a single proof.

**Proof of Lemma R3⋆-KS.** Let $(B_1, B_2)$ be the SAD of $D^\bullet
\langle V_2 \rangle$ guaranteed by hypothesis.

Use the attachment observation with kernel $X = V_2$. At each shell
vertex $v \in V_1^\bullet \setminus \{r\}$, choose any one in-arc and
one out-arc for each color, possible by 3-arc-strongness of $D$ and
(NS3), and distribute leftover arcs arbitrarily.

At $r$, use the explicit assignment of §3.4 Step 3: $\alpha_2^- \in
R_p^-$ and $\alpha_2^+ \in R_q^+$ to color 2; $\beta_1^{+,p} \in R_p^+$,
$\beta_1^{+,q} \in R_q^+ \setminus \{\alpha_2^+\}$, $\beta_1^{-,p} \in
R_p^- \setminus \{\alpha_2^-\}$, and $\beta_1^{-,q} \in R_q^-$ to color
1. Such choices exist by the supply bounds of ($\ast$) (every supply
exceeds the corresponding demand by $\ge 1$). Distribute remaining
arcs at $r$ to either color arbitrarily.

By the attachment observation in §2, the resulting pair
$(A_1^\bullet, A_2^\bullet)$ is a SAD of $D^\bullet$. This is exactly
the BJ-Wang Lemma 2.4 proof template, with the contracted vertex $r$
handled at the level of labelled arcs rather than unlabelled neighbors.

By §3.4 Step 4, color 2 of this SAD satisfies $Q_2$ and color 1
satisfies both $P_1$ and $Q_1$. Thus the R3⋆ liftability condition of
`team/22_*` §2 holds with $i = 2$:
$$Q_2 \wedge P_1 \wedge Q_1.$$

This completes the proof. $\square$

---

## §5 — Consequence for Theorem 1 in the kernel-shell case

Combining Lemma R3⋆-KS with the contraction-route argument of
`team/21_*` §5:

**Corollary (Theorem 1, kernel-shell case).** *Let $D = (V, A)$ be a
simple 3-arc-strong $(1,0)$-near-split digraph with $|V_1| \ge 2$,
$|V_2| \ge 3$, chord $e_0 = (p, q)$. Let $D^\bullet$ be the
chord contraction. Suppose $D^\bullet \langle V_2 \rangle$ admits a
SAD. Then $D$ admits a SAD.*

**Proof.** By Lemma R3⋆-KS (§4), there is a SAD $(A_1^\bullet,
A_2^\bullet)$ of $D^\bullet$ and a color $i \in \{1, 2\}$ such that
$Q_i \wedge P_{3-i} \wedge Q_{3-i}$. By `team/22_*` §2 Fact F2 (effect
of adding $e_0$) and Fact F1 (un-contracted-color goodness ⟺ strong
on $V$), assigning $e_0$ to color $i$ yields a SAD of $D$:
- color $i$ acquires $P_i$ (from $e_0$) on top of $Q_i$, hence is
  good and strongly spans $V$;
- color $3 - i$ has both $P_{3-i}$ and $Q_{3-i}$ already, hence is good
  and strongly spans $V$.

This is the SAD of $D$ promised by Theorem 1. $\square$

The corollary is **unconditional** within its kernel-shell scope. It is
the first unconditional Route B result on $(1,0)$-near-split digraphs.

---

## §6 — Edge cases

The kernel-shell hypothesis "$D^\bullet \langle V_2 \rangle$ admits a
SAD" is satisfied in many regimes but not all. We examine the relevant
edge cases and indicate which fall in scope.

### §6.1 $|V_2| = 3$

$D \langle V_2 \rangle$ is a simple semicomplete digraph on 3 vertices.
By BJ–Yeo 2004 (every 2-arc-strong semicomplete digraph $\ne S_4$ has
a SAD; cf.\ `team/05_audit.md` Appendix A.5), and since $S_4$ has 4
vertices, the kernel-shell hypothesis holds iff $\lambda^{\text{arc}}(D
\langle V_2 \rangle) \ge 2$.

A sub-digraph of a 3-arc-strong digraph need *not* be 2-arc-strong
(`team/19_*` §3.1): a 2-cut of $D \langle V_2 \rangle$ may be patched
in $D$ by a $V_1$-detour. So R3⋆-KS does not apply automatically when
$|V_2| = 3$; the $\lambda(D \langle V_2 \rangle) \ge 2$ test must be
made instance-by-instance. *Sufficient condition:* every $v \in V_2$
has $\ge 2$ in- and $\ge 2$ out-neighbors in $V_2$. On a 3-vertex
semicomplete this forces a 2-arc-strong tournament, which has a SAD.
The exhaustive $(|V_1|,|V_2|)=(2,3)$ run at $\lambda(D) = 3$
(`team/20_*` §2.2, 192 instances, 0 UNSAT) is dominated by such cores.

When $D \langle V_2 \rangle$ is a 3-cycle (1-arc-strong), the
kernel-shell hypothesis fails; this is a splitting-off case (see §7).

### §6.2 $|V_2| = 4$

$D \langle V_2 \rangle$ is simple semicomplete on 4 vertices. The
kernel-shell hypothesis holds iff $\lambda(D \langle V_2 \rangle) \ge 2$
and $D \langle V_2 \rangle \ne S_4$ (the only simple exception in
Theorem 2.3; six others $S_{4,1},\ldots,S_{4,6}$ are non-simple and
hence excluded by `team/21_*` §3.3). When $D \langle V_2 \rangle \cong
S_4$, R3⋆-KS does not apply; this case is the $S_4$-subcase of
`team/21_*` §6.2, handled by BJ–Wang with kernel $X = V_2 \setminus
\{v\}$. Whether that handling produces a side-aware liftable SAD is
open (see §7).

### §6.3 $|V_2| \ge 5$

By BJG–Yeo 2020 / BJ–Yeo 2004, every 2-arc-strong semicomplete digraph
on $\ge 5$ vertices has a SAD. Kernel-shell holds iff
$\lambda(D \langle V_2 \rangle) \ge 2$. This is the asymptotically
dominant regime.

### §6.4 Outside the kernel-shell scope

Complement of kernel-shell: $\lambda(D \langle V_2 \rangle) \le 1$ (any
$|V_2| \ge 3$), or $|V_2| = 4$ with $D \langle V_2 \rangle \cong S_4$.
These are precisely the BJ–Wang splitting-off cases (`team/21_*` §3.4
Steps (iii)–(v)), constituting the residual R3⋆ gap.

---

## §7 — What remains for the full R3⋆

### §7.1 Residual case description

When $D^\bullet \langle V_2 \rangle$ does **not** admit a SAD (per
§6.4: low connectivity or $S_4$-isomorphism), the BJ–Wang Theorem 1.6
proof on $D^\bullet$ proceeds via splitting-off:

1. choose a set $Q$ of arc-disjoint paths with endpoints in $V_2$ and
   internal vertices in $V_1^\bullet$ (the shell);
2. perform splitting-off — replace each path $x_0 \to x_1 \to \cdots
   \to x_k$ (with $x_0, x_k \in V_2$, interior in $V_1^\bullet$) by a
   single arc $x_0 \to x_k$, deleting the path arcs;
3. the resulting multi-digraph $D_Q^\bullet \langle V_2 \rangle$ is
   semicomplete and 2-arc-strong, and now admits a SAD by Theorem 2.3
   (with $S_4$-type exceptions handled by Lemma 2.7);
4. lift each splitting arc back through its $V_1^\bullet$-vertex per
   Lemma 2.5;
5. absorb still-uncovered shell vertices by Lemma 2.4.

In this trajectory, the shell vertex $r = p^\bullet$ may participate
in splitting paths in either of two distinct ways:

- **(I) $r$ as a splitting-path interior vertex.** A path $x_0 \to r
  \to x_1$ in $D^\bullet$ becomes a splitting arc $x_0 \to x_1$ in
  $D_Q^\bullet \langle V_2 \rangle$; on lift-back, the path is restored
  with its two arcs at $r$. These two arcs at $r$ are labelled (in one
  of $R_p^+, R_q^+, R_p^-, R_q^-$ each), but the BJ–Wang construction
  is **side-blind** — the choice of $Q$ does not control labels.
- **(II) $r$ as a kernel vertex.** Some labelled arcs at $r$ may be
  absorbed by Lemma 2.4 in step 5 rather than by splitting. The Lemma
  2.4 absorption is again side-blind.

### §7.2 The side-blindness of BJ–Wang's splitting

`team/22_*` §5 diagnoses the four points where BJ–Wang loses the labels
$\{p, q\}$ at $r$: choice of $Q$; SAD-coloring of $D_Q^\bullet \langle
V_2 \rangle$; Lemma 2.5 lift-back; Lemma 2.5 spare-arc step. Each
choice is consistent with strong connectivity in $D^\bullet$ but
indifferent to side labels.

### §7.3 What additional ingredient is needed

The full R3⋆ requires one of:

**(7.3.a) Side-aware splitting-off.** Strengthen BJ–Wang's splitting
so that splitting paths at $r$ are chosen to produce a side-compatible
attachment at $r$ in the final SAD. Obstruction: the splitting-path
packing is already constrained by 2-arc-strongness of $D_Q^\bullet
\langle V_2 \rangle$ and by minimization of $|W_Q^+| + |W_Q^-|$; adding
side-compatibility at $r$ may over-constrain.

**(7.3.b) Recoloring within the SAD polytope.** Given any SAD of
$D_Q^\bullet \langle V_2 \rangle$, ask whether a recoloring — swapping
labelled arcs at $r$ between colors while preserving strong
connectivity in both — can achieve the 4-cell label-distribution of
§3.2. The recoloring lemma would be a standalone polytope-theoretic
statement; empirics (`team/20_*` §2.2) are consistent with this route.

**(7.3.c) Direct branching argument.** Use 3-arc-strongness of
$D^\bullet$ plus the Edmonds branching theorem (`team/05_audit.md`
Appendix A.5 Source 1 line 946) to construct three arc-disjoint
out-branchings and three arc-disjoint in-branchings at $r$, then
combine two out + two in into a side-aware SAD. Side-awareness is
controlled by which $R_\bullet^\bullet$ class each branching arc at $r$
lies in; by ($\ast$) the supply is sufficient. This route bypasses
BJ–Wang's splitting-off machinery entirely.

### §7.4 Scope reduction

Lemma R3⋆-KS reduces the full R3⋆ to: prove R3⋆ in the residual case
of §6.4. The reduction is exact — outside the kernel-shell scope, the
labelled-arc supply bounds of ($\ast$) still hold (they are derived from
3-arc-strongness, not from $D \langle V_2 \rangle$'s SAD), but the
construction of §3.4 requires the kernel $B_j$ to be strong on $V_2$ —
which fails outside the scope.

The residual case is at most $\le 2\%$ of empirical instances
(estimated from `team/20_*` §§2.1–2.2: in 7 374 candidates, the
$|V_2| \ge 5$ cases dominate; the small-$V_2$ exceptional cases are
$O(1)$ in count but cannot be ruled out at large $|V_2|$ without
further argument).

### §7.5 Honest scope of this file

This file proves Lemma R3⋆-KS and hence Theorem 1 in the kernel-shell
case. It does **not** prove the full Theorem 1.

Empirical record (`team/20_*` §§2.1, 2.2): 7 374 tested instances at
$\lambda^{\text{arc}}(D) = 3$, all SAT. This empirical record covers
**both** the kernel-shell case (which §§3–5 prove) and the residual
case (which §7 scopes). Hence the empirical record alone does not
distinguish whether Theorem 1 fails in any residual instance. The
true status of the residual case is: **conjecturally true**, supported
by empirics, but unproved.

The next deliverable should attack one of (7.3.a)–(7.3.c). The
specialist's recommendation: **(7.3.c)** (Edmonds-branching
construction) is the most self-contained and likely to yield a clean
proof, avoiding the labyrinth of BJ–Wang's nice-decomposition machinery.

---

## Appendix — File hygiene and citations

No new code. The proof of Lemma R3⋆-KS is purely combinatorial.

**Citations cross-checked against `team/05_audit.md` and `team/22_*`:**

- BJ–Wang 2025 Lemma 2.4 (multigraph): `team/05` Appendix A.1 / A.5
  Source 1, line 925.
- BJ–Wang 2025 Theorem 2.5 (Edmonds, multigraph): `team/05` A.5 Source
  1, line 946.
- BJG–Yeo 2020 / BJ–Yeo 2004 (semicomplete-multi-digraph SAD
  characterization): `team/05` A.8 §A.8.3 item 1.
- $P_i, Q_i, R_p^+, R_q^+, R_p^-, R_q^-$ definitions: `team/22_*` §§2–3
  verbatim, **not redefined here**.
- Contraction maps: `team/21_*` §§1.2, 3.1–3.3.
- Facts F1, F2: `team/22_*` §2; `team/21_*` §4.2.
- 3-arc-strongness of $D^\bullet$: `team/21_*` §3.1.
- Lemma 2.4 hypothesis at $r$: `team/21_*` §3.4 Step (ii.b).
- Empirical record: `team/20_*` §§2.1, 2.2.

No "Theorem RD"-style citations.

**Status after this file:** kernel-shell case closed; residual case
open. Theorem 1 unconditional in kernel-shell scope, conditional in
residual scope. The kernel-shell hypothesis is testable on any instance
(BJ–Yeo 2004 plus a $\lambda$-check on $D \langle V_2 \rangle$).

End of file.
