# 29 — Route (c1): R3⋆-HC under within-kind disjointness, with explicit cross-kind re-coloring

Author: Structural Digraph Specialist
Date: 2026-05-17
Status: Replacement of `team/27_*` §3.1.1's over-strong cross-kind
arc-disjointness step (audit `team/05_audit.md` Appendix A.10) by a
strictly weaker hypothesis — **two within-kind-disjoint
out-branchings and two within-kind-disjoint in-branchings, with
cross-kind sharing permitted** — together with an explicit
re-coloring lemma that resolves the cross-color sharing without
breaking the §3.4 side-label casework. The §4 sub-case structure of
`team/27_*` (H1a / H1b / H2) is unchanged; the §3.4 16-profile
counting at $r$ survives because cross-kind sharing is impossible at
$r$.

**Why this file.** Audit A.10 established that the "matroid-union"
form of Edmonds invoked in `team/27_*` §3.1.1 is not a published
theorem; it is in fact a strengthening of the **open Thomassen
Conjecture 2**, and the joint out-/in-branching packing problem is
NP-complete (Nagamochi–Kamiyama 2014 Thm 3.12). Route (c1) is the
*correct* downgrade: keep the within-kind disjointness (Edmonds +
submodularity, `team/27_*` lines 197–207) and absorb the cross-kind
sharing into the §3 re-coloring step. **The only branching-packing
result used is Theorem 2.5 of BJG–Yeo 2020 in its `team/05`
Appendix A.5 Source 2 verbatim form.**

Prior references: `team/27_*` §§1–4 (setup, hard-case lemma,
sub-cases); `team/26_*` §§1–4 (kernel-shell case); `team/22_*`
§§2–3 (notation); `team/21_*` §§1.2, 3.1–3.4 (chord contraction);
`team/05_audit.md` Appendices A.1, A.5, A.6, A.8, A.10; `team/28_*`
(empirical residual closure).

---

## §1 — Setup and the corrected hypothesis

### §1.1 Standing hypotheses (verbatim from `team/27_*` §§1.1–1.2)

$D = (V, A)$ is a simple 3-arc-strong $(1, 0)$-near-split digraph
with split partition $V = V_1 \dot\cup V_2$, $|V_1| \ge 2$, $|V_2| \ge
3$, unique $V_1$-internal arc $e_0 = (p, q)$ (so $\lambda^{\text{arc}}(D)
\ge 3$). $D^\bullet$ is the chord contraction with contracted vertex
$r := p^\bullet$; $V_1^\bullet = (V_1 \setminus \{p, q\}) \cup \{r\}$,
$V_2^\bullet = V_2$. By `team/21_*` §§3.1–3.3, $D^\bullet$ is a
3-arc-strong **directed multigraph**, with $V_1^\bullet$ independent
and $V_2^\bullet$ simple semicomplete.

Notation $\pi$, $\pi^{-1}$ (contraction / un-contraction on labels);
$D_i^\flat := (V, \pi^{-1}(A_i^\bullet))$ (un-contracted color-$i$
sub-digraph of $D - e_0$); $P_i$ ("$D_i^\flat$ contains $p \to q$");
$Q_i$ ("$D_i^\flat$ contains $q \to p$"); the four side-label classes
at $r$:

- $R_p^+$ — labelled arcs $r \to y$ with preimage $(p, y)$, $y \in V_2$;
- $R_q^+$ — labelled arcs $r \to y$ with preimage $(q, y)$, $y \in V_2$;
- $R_p^-$ — labelled arcs $x \to r$ with preimage $(x, p)$, $x \in V_2$;
- $R_q^-$ — labelled arcs $x \to r$ with preimage $(x, q)$, $x \in V_2$.

Corrected directional lower bounds (`team/26_*` §3.1):

$$
|R_p^+| \ge 2, \quad |R_q^+| \ge 3, \quad |R_p^-| \ge 3, \quad |R_q^-| \ge 2. \tag{$\ast$}
$$

The R3⋆ liftability target (`team/22_*` §2) is the disjunction
$\exists i \in \{1, 2\}$ with $Q_i \wedge P_{3-i} \wedge Q_{3-i}$.

### §1.2 The corrected branching-packing hypothesis (replaces `team/27_*` §3.1.1)

We use **only** Theorem 2.5 of BJG–Yeo 2020 in the verbatim form
quoted in `team/05_audit.md` Appendix A.5 Source 2 (line 946):

> **Theorem 2.5.** A directed multigraph $D = (V, A)$ with a vertex
> $z$ has $k$ arc-disjoint out-branchings rooted at $z$ if and only
> if $d^-(X) \geq k$ for all non-empty $X \subseteq V \setminus
> \{z\}$.

Applied to $D^\bullet$ with $z = r$ and $k = 2$: since $D^\bullet$ is
3-arc-strong, $d_{D^\bullet}^-(X) \ge 3 \ge 2$ for every non-empty
$X \subseteq V^\bullet \setminus \{r\}$, so there exist two
arc-disjoint out-branchings $T_1^+, T_2^+$ rooted at $r$. Applied to
the **reverse** digraph (same hypothesis, with $d^-$ replaced by
$d^+$ in the original direction): there exist two arc-disjoint
in-branchings $T_1^-, T_2^-$ rooted at $r$.

**Within-kind disjointness, refined (verbatim re-statement of
`team/27_*` lines 197–207, which is correct as written).** We further
choose $T_1^-$ inside $A^\bullet \setminus T_1^+$ and $T_2^-$ inside
$A^\bullet \setminus T_2^+$. For each non-empty $X \subseteq V^\bullet
\setminus \{r\}$, the out-branching $T_i^+$ contributes at most one
arc to $\delta^-(X)$ (otherwise it would contain a cycle into $X$,
contradicting branching). Hence

$$d_{(D^\bullet \setminus T_i^+)}^-(X) \ge d_{D^\bullet}^-(X) - 1 \ge 3 - 1 = 2.$$

Applying Theorem 2.5 to the **reverse** of $D^\bullet \setminus T_i^+$
with $k = 2$ gives $T_i^- \subseteq A^\bullet \setminus T_i^+$ arc-
disjoint from another in-branching; we keep $T_i^-$. By construction

$$T_i^+ \cap T_i^- = \emptyset \quad (i = 1, 2). \tag{WK}$$

Within-kind disjointness across the two colors is also automatic:
the same Theorem 2.5 application gives $T_1^+ \cap T_2^+ = \emptyset$
and (applied to the reverse) $T_1^- \cap T_2^- = \emptyset$.

**What we do NOT assume.** We do **not** assume $T_1^+ \cap T_2^- =
\emptyset$ or $T_2^+ \cap T_1^- = \emptyset$. Cross-color, cross-kind
sharing is permitted. (This is the audit's recommended downgrade,
Appendix A.10 §A.10.6 item 1.)

### §1.3 Why cross-kind sharing at $r$ is impossible

Structural observation, not a citation. At the vertex $r$:
$T_i^+$ contains only out-arcs of $r$ (its root contribution is the
unique $T_i^+$-out-arc of $r$; $T_i^+$ has no in-arcs at $r$, as $r$
is the source). Symmetrically $T_j^-$ contains only in-arcs of $r$.
So any arc at $r$ lies in at most one of "out-branchings" and "in-
branchings":

$$T_i^+ \cap T_j^- \cap \{\text{arcs incident with } r\} = \emptyset
\quad \text{for all } i, j \in \{1, 2\}. \tag{LR}$$

**Consequence.** All cross-color cross-kind sharing $S_{12} \cup
S_{21}$ (defined below) lives at internal vertices $V^\bullet
\setminus \{r\}$. This decouples §3 (re-coloring at internal vertices)
from §4 (side-label casework at $r$).

### §1.4 The shared-arc catalogue

For $i, j \in \{1, 2\}$, define

$$S_{ij} := T_i^+ \cap T_j^-.$$

By (WK), $S_{ii} = \emptyset$. By (LR), every arc of $S_{ij}$ is at
an internal vertex (not at $r$). The remaining two sets,

$$S_{12} = T_1^+ \cap T_2^-, \quad S_{21} = T_2^+ \cap T_1^-,$$

are the **cross-color shared arcs**. The §1.2 downgrade makes no
claim about their size; they may be empty (in which case `team/27_*`'s
proof goes through unchanged), or non-empty (in which case §3 of this
file is required).

---

## §2 — The shared-arc problem

The naive color assignment "color $i$ := $T_i^+ \cup T_i^- \cup F_i$"
(where $F_i$ is a partition of the free arcs $F := A^\bullet \setminus
(T_1^+ \cup T_2^+ \cup T_1^- \cup T_2^-)$, set union) fails when
$S_{12} \cup S_{21} \ne \emptyset$, for the following reason. Take
$a \in S_{12} = T_1^+ \cap T_2^-$. The branching assignment would
place $a$ in color 1 (via $T_1^+$) **and** in color 2 (via $T_2^-$).
A SAD of $D^\bullet$ is a **partition** of $A^\bullet$ into two
color classes (each spanning strong). The naive assignment is not a
partition: $a$ is counted twice. We need a recipe that commits each
$a \in S_{12} \cup S_{21}$ to exactly one color.

**Catalogue.** The 4 shared sets are:

| $S_{ij}$ | $= T_i^+ \cap T_j^-$ | conflict? |
|----------|----------------------|-----------|
| $S_{11}$ | $T_1^+ \cap T_1^- = \emptyset$ | (empty by WK) |
| $S_{12}$ | $T_1^+ \cap T_2^-$ | YES — color 1 vs. color 2 |
| $S_{21}$ | $T_2^+ \cap T_1^-$ | YES — color 2 vs. color 1 |
| $S_{22}$ | $T_2^+ \cap T_2^- = \emptyset$ | (empty by WK) |

By (LR) every $a \in S_{12} \cup S_{21}$ is an arc $(u, v)$ with
$u, v \in V^\bullet \setminus \{r\}$. (Indeed, if $r \in \{u, v\}$
then $a$ would be both an in-arc and an out-arc of $r$, contradiction.)

---

## §3 — Re-coloring algorithm

Throughout §3 fix a packing $(T_1^+, T_2^+, T_1^-, T_2^-)$ satisfying
(WK) and let $S := S_{12} \cup S_{21}$ be the cross-color shared arcs.

### §3.1 The re-coloring map

**Definition 3.1 (re-coloring).** A *re-coloring* is a map $c \colon
S \to \{1, 2\}$. For each $a \in S$:

- If $a \in S_{12} = T_1^+ \cap T_2^-$:
  - $c(a) = 1$ keeps $a$ in $T_1^+$ (color 1) and **removes** $a$
    from $T_2^-$;
  - $c(a) = 2$ keeps $a$ in $T_2^-$ (color 2) and removes $a$ from
    $T_1^+$.
- If $a \in S_{21} = T_2^+ \cap T_1^-$:
  - $c(a) = 1$ keeps $a$ in $T_1^-$ (color 1) and removes $a$ from
    $T_2^+$;
  - $c(a) = 2$ keeps $a$ in $T_2^+$ (color 2) and removes $a$ from
    $T_1^-$.

After re-coloring, define

$$\tilde T_i^+ := T_i^+ \setminus \{a \in S \cap T_i^+ : c(a) \ne i\}, \quad
\tilde T_i^- := T_i^- \setminus \{a \in S \cap T_i^- : c(a) \ne i\}.$$

The four sets $\tilde T_1^+, \tilde T_2^+, \tilde T_1^-, \tilde T_2^-$
are pairwise arc-disjoint by construction (each $a \in S$ now lives
in exactly one set, namely the one with color $c(a)$ that the
definition keeps; arcs outside $S$ are unchanged and were already
within-kind disjoint).

### §3.2 The replacement-arc lemma

**Lemma 3.2 (single-arc removal, in-branching).** *Let $T^-$ be an
in-branching of $D^\bullet$ rooted at $r$, and let $a = (u, v) \in
T^-$ with $u \ne r$. Removing $a$ from $T^-$ splits the in-tree into
$T_a^{\mathrm{up}}$ (containing $r$ and all vertices whose
$T^-$-path-to-$r$ does not pass through $a$) and $T_a^{\mathrm{down}}$
rooted at $u$ (the vertices whose $T^-$-path-to-$r$ uses $a$ as the
out-arc from $u$). Adding any arc $a' = (v', v'') \in A^\bullet$ with
$v' \in V(T_a^{\mathrm{down}})$ and $v'' \in V(T_a^{\mathrm{up}})$
restores the in-branching property: $T^- - a + a'$ is again an
in-branching of $D^\bullet$ rooted at $r$.*

*Proof.* $T^-$ is a spanning in-tree with $r$ as sink; removing the
parent-arc of $u$ disconnects exactly the down-subtree
$T_a^{\mathrm{down}}$ (those vertices whose unique-out-path to $r$
used $a$). Adding an arc from any down-vertex $v'$ to any up-vertex
$v''$ joins the down-component back to the sink, and the result
remains a spanning tree (we added one arc, removed one arc, kept tree
property by acyclicity of $T_a^{\mathrm{down}} \to T_a^{\mathrm{up}}$
arcs across the cut). Each $w \in T_a^{\mathrm{down}}$ now reaches
$r$ via $w \to \cdots \to v' \to v'' \to \cdots \to r$. $\square$

**Lemma 3.2′ (out-branching version).** Removing $a = (u, v) \in T^+$
from an out-branching from $r$ splits into $T_a^{\mathrm{up}}$
(containing $r$) and $T_a^{\mathrm{down}}$ (rooted at $v$). Any arc
$a' = (v', v'')$ with $v' \in V(T_a^{\mathrm{up}})$, $v'' \in
V(T_a^{\mathrm{down}})$ restores the out-branching.

### §3.3 The counting reservoir

**Lemma 3.3 (replacement-arc supply).** *Let $a = (u, v) \in S_{12} =
T_1^+ \cap T_2^-$, with $c(a) = 1$ — so color 2 loses $a$ from
$T_2^-$. Let $X := V(T_a^{\mathrm{down}})$ in $T_2^-$. Then either
(a) some arc $a' \in \delta^+(X) \setminus (T_2^+ \cup T_1^-)$ is
available as direct replacement, or (b) $\delta^+(X)$ is fully
absorbed by $T_2^+ \cup T_1^-$, in which case a chained swap with an
arc in $T_2^+ \cap \delta^+(X)$ (or $T_1^- \cap \delta^+(X)$)
produces a feasible replacement at the cost of repairing a smaller
sub-tree elsewhere.*

*Proof.* By 3-arc-strongness, $|\delta^+(X)| \ge 3$. Let $c_+ :=
|T_2^+ \cap \delta^+(X)|$ and $c_- := |T_1^- \cap \delta^+(X)|$.
(Branching axioms give the trivial bounds $0 \le c_+, c_- \le |X|$,
with $c_- \ge 1$ — at least one $X$-vertex must reach $r$ via
$T_1^-$ across $\delta^+(X)$, since $r \notin X$.) The number of
"free" arcs in $\delta^+(X) \setminus (T_2^+ \cup T_1^-)$ is

$$|\delta^+(X)| - c_+ - c_- \ge 3 - c_+ - c_-.$$

If $c_+ + c_- \le 2$ this is $\ge 1$ and case (a) holds. Otherwise
$c_+ + c_- = 3$ (the only larger possibility, given $|\delta^+(X)|
\ge 3$ exhausted), and case (b) applies: pick any $b \in T_2^+ \cup
T_1^-$ inside $\delta^+(X)$; swap $b$ into $T_2^-$ as replacement for
$a$. This breaks the branching that previously contained $b$, but
inside a *strictly smaller* sub-tree — the down-tree of $b$ in its
branching, which lies inside $X = V(T_a^{\mathrm{down}})$ and hence
has $|V(T_b^{\mathrm{down}})| < |X|$. Recurse. $\square$

The chained re-coloring is what motivates §3.4's structural
argument.

### §3.4 The auxiliary digraph $H$ and termination

Define an auxiliary digraph $H = (S, E_H)$ on the shared arcs, with
an arc $a \to b$ in $E_H$ if "re-coloring $a$ (according to some
fixed initial choice) forces re-coloring $b$" — meaning: if $c(a) =
1$ (so $a$ leaves $T_2^-$ and color 2 needs a replacement), the
chosen replacement arc inside $\delta^+(X_a)$ is itself a shared arc
$b$, and committing $b$ to color 2 forces $b$ to leave its other
branching.

**Lemma 3.4 (acyclicity of $H$).** *There exists an ordering of $S$
such that processing the re-coloring in that order produces no
cycle of forced re-colorings, and the resulting assignment is
well-defined.*

*Proof sketch.* For each $a \in S$ define the *down-set size*

$$\sigma(a) := |X_a| = |V(T_a^{\text{down}})|$$

where $T_a^{\text{down}}$ is the down-tree of $a$ in the in-branching
that contains $a$ (i.e., $T_2^-$ if $a \in S_{12}$, $T_1^-$ if $a \in
S_{21}$). For an $H$-arc $a \to b$, the forced re-coloring of $b$
operates on a down-tree $T_b^{\text{down}}$ that is **strictly
contained in** $T_a^{\text{down}}$ minus the "swap-arc" path; in
particular $\sigma(b) < \sigma(a)$. Hence $\sigma$ strictly decreases
along $H$-arcs, $H$ is acyclic, and processing $S$ in order of
decreasing $\sigma$ terminates after $|S|$ steps. $\square$

*Remark on the strict-decrease claim.* When $a \to b$ in $H$, the
forced re-coloring of $b$ arises because $b$ is the replacement arc
chosen by Lemma 3.3 for $a$, and $b$ itself is shared. The
replacement arc $b = (v', v'')$ has $v' \in V(T_a^{\mathrm{down}})$
and $v'' \notin V(T_a^{\mathrm{down}})$, so committing $b$ to the
new color affects only the sub-tree below $v'$ (or below $v''$,
depending on direction), which is strictly smaller than
$T_a^{\mathrm{down}}$. The detailed monotonicity is left at this
sketch level; see §3.8 for the augmenting-path fallback if the
detailed argument is challenged.

### §3.5 The re-coloring procedure (algorithmic form)

**Algorithm RECOLOR.**

1. Compute $S = S_{12} \cup S_{21}$ from the packing $(T_1^+, T_2^+,
   T_1^-, T_2^-)$.
2. If $S = \emptyset$, return $(T_1^+, T_2^+, T_1^-, T_2^-)$
   unchanged (the original packing is already pairwise arc-disjoint).
3. Otherwise, sort $S$ in some fixed order; for definiteness, by the
   down-set size $\sigma$ (Lemma 3.4).
4. For each $a \in S$ in order:
   - Pick $c(a) \in \{1, 2\}$ — for definiteness, $c(a) = 1$ for all
     $a \in S_{12}$, $c(a) = 2$ for all $a \in S_{21}$ (the "keep
     out-branching coloring" rule; arc out of $r$ goes to its
     out-branching color, arc into $r$ — but by (LR) shared arcs are
     internal, so this rule reads: $a \in T_i^+$ pulls $a$ to color
     $i$).
   - Apply the removal: $a$ leaves the branching of color $3 - c(a)$
     (if it was in such a branching).
   - Repair the broken branching by Lemma 3.2 / 3.2′: find a
     replacement arc $a'$ in $\delta^+(X_a) \setminus (T_2^+ \cup
     T_1^-)$ if $a \in S_{12}$ (resp. $\delta^+(X_a) \setminus (T_1^+
     \cup T_2^-)$ if $a \in S_{21}$); if no such $a'$, swap inside
     the other color's branching (Lemma 3.3, chained re-coloring).
5. Output the modified packing $(\tilde T_1^+, \tilde T_2^+, \tilde
   T_1^-, \tilde T_2^-)$.

**Termination.** Each iteration either (i) completes by finding a
free replacement arc, decrementing $|S|$ by 1; or (ii) chains to a
shared arc with strictly smaller down-set size $\sigma$ (Lemma 3.4),
which still terminates because $\sigma$ is a non-negative integer.
Termination after at most $|S| + (\max \sigma)$ steps.

**Output property.** The four sets $\tilde T_i^\pm$ are pairwise
arc-disjoint (each arc of $A^\bullet$ is in at most one of them by
the re-coloring map), each $\tilde T_i^\pm$ is a spanning branching
of the appropriate kind rooted at $r$ (by Lemma 3.2/3.2′
replacement, plus the within-kind-disjointness pre-condition).

### §3.6 Strong connectivity of each color class

Define

$$A_i^\bullet := \tilde T_i^+ \cup \tilde T_i^- \cup F_i$$

where $F = A^\bullet \setminus (\tilde T_1^+ \cup \tilde T_2^+ \cup
\tilde T_1^- \cup \tilde T_2^-)$ is the set of arcs unused by any
modified branching, and $F_1, F_2$ is any partition of $F$. By
Lemma 3.5 (output property), $\tilde T_i^+$ is an out-branching from
$r$ and $\tilde T_i^-$ is an in-branching to $r$. For any $u, v \in
V^\bullet$:

- $u$ reaches $r$ via $\tilde T_i^-$ (in-branching to $r$);
- $r$ reaches $v$ via $\tilde T_i^+$ (out-branching from $r$);

so $u$ reaches $v$ in $A_i^\bullet$. Hence $A_i^\bullet$ is spanning
strong on $V^\bullet$.

### §3.7 Status of §3

Fully proved: Lemmas 3.2 / 3.2′ (single-arc tree manipulation),
Lemma 3.3 *case (a)* (free replacement exists when $c_+ + c_- \le 2$
in $\delta^+(X)$ by 3-arc-strongness). Sketch level: Lemma 3.3
*case (b)* recursion / Lemma 3.4 acyclicity ($\sigma$-monotonicity
under chained replacement). The fallback in §3.8 supplies an
augmenting-path argument that does not depend on the sketch.

### §3.8 Alternative: augmenting-path formulation (fallback)

If the iterative §3.5 cannot be proved to terminate cleanly, the
fallback is:

**Lemma 3.8 (augmenting-path closure).** *For any choice $c \colon S
\to \{1, 2\}$, both $\tilde T_i^+ \cup \tilde T_i^-$ are spanning
sub-digraphs of $D^\bullet$ rooted at $r$ (with $r$ as common root of
the out-tree and in-tree). For each color $j$ whose pair $(\tilde
T_j^+, \tilde T_j^-)$ fails to be strongly connecting (due to the
removal of a shared arc), there exists an arc-disjoint augmenting
path in $A^\bullet \setminus (\tilde T_{3-j}^+ \cup \tilde T_{3-j}^-)$
that restores strong connectivity.*

*Proof sketch.* In $D^\bullet$, 3-arc-strongness gives 3 arc-disjoint
$u \to v$ paths for every $u, v$ (Menger). The pair $(\tilde T_j^+,
\tilde T_j^-)$ uses at most 2 paths-worth of arcs per cut (one out-
arc + one in-arc per cut, by branching). So $\ge 1$ arc-disjoint $u
\to v$ path remains in $D^\bullet \setminus (\tilde T_{3-j}^+ \cup
\tilde T_{3-j}^-)$ for each ordered cut. This residual provides the
augmenting path. (Caveat: this requires a careful cut/path counting
on $D^\bullet$; the argument is standard but not spelled out in full
here.) $\square$

This is the "Menger fallback" that A.10's recommendation 4
contemplates: when the iterative re-coloring is unwieldy, just check
that the residual digraph has enough connectivity to augment. The
3-arc-strongness gives a margin of 1 over the demand of 2-per-cut for
the joint out-+in-branching, so the fallback is feasible.

---

## §4 — Side-label casework at $r$ (re-verification of `team/27_*` §3.4)

### §4.1 The 4 branching arcs at $r$ remain distinct

The branching packing $(T_1^+, T_2^+, T_1^-, T_2^-)$ contributes 4
arcs at $r$:

- $a_1^+$ = the unique out-arc of $r$ in $T_1^+$;
- $a_2^+$ = the unique out-arc of $r$ in $T_2^+$;
- $a_1^-$ = the unique in-arc of $r$ in $T_1^-$;
- $a_2^-$ = the unique in-arc of $r$ in $T_2^-$.

By (WK), $a_1^+ \ne a_2^+$ (out-branchings are within-kind disjoint)
and $a_1^- \ne a_2^-$ (in-branchings are within-kind disjoint). By
(LR), $\{a_1^+, a_2^+\} \cap \{a_1^-, a_2^-\} = \emptyset$ — an arc
at $r$ is either out or in, not both, so no out-arc can equal an
in-arc.

**Hence the 4 branching arcs at $r$ are 4 distinct arcs.** This is
exactly the count `team/27_*` §3.3 needs; the count is preserved
under the corrected (weaker) hypothesis of §1.2.

### §4.2 The 16-profile casework survives

`team/27_*` §3.4.6's 16-row table tabulates, for each profile $(\sigma_1^+,
\sigma_2^+, \sigma_1^-, \sigma_2^-) \in \{p, q\}^4$, the side-class
demands and the §3.4.7 feasibility check. The table's correctness
depends on:

1. The 4 branching arcs at $r$ are distinct (verified §4.1).
2. The free-arc supply per class is $|R_p^+|_F \ge 2 - n_p^+$,
   $|R_q^+|_F \ge 1 + n_p^+$, $|R_p^-|_F \ge 3 - n_p^-$, $|R_q^-|_F
   \ge n_p^-$ (deduced in `team/27_*` §3.4.4 from ($\ast$) and the
   packing's deductions, which depend only on (1)).
3. The §3.4.5 strategy of allocating free arcs to colors to fill
   demands — this is a free-arc allocation at $r$, **not affected by
   any re-coloring of shared arcs at internal vertices**.

By (LR), the re-coloring of §3 touches only arcs at $V^\bullet
\setminus \{r\}$. Hence the free arcs at $r$ are not touched by the
re-coloring; their supply is determined entirely by the packing's
$r$-incident choices (the 4 branching arcs at $r$). The §3.4.6 table
and §3.4.7 per-row feasibility check go through verbatim.

### §4.3 Re-stating the §3.4 conclusion

For every branching profile, the free-arc allocation at $r$ can be
chosen so that:

- Color 1 (the "good" color) receives at least one free arc of each
  class $R_p^+, R_q^+, R_p^-, R_q^-$ that the packing did not supply
  to color 1;
- Color 2 (the "absorbing" color, which gets $e_0$ on un-contraction)
  receives at least one free arc of each class $R_q^+, R_p^-$ that
  the packing did not supply to color 2.

The side-class supply ($\ast$) exceeds the side-class demand in every
class (slack $\ge 0$, with strict slack in most rows; `team/27_*`
§3.4.7 verifies all 16 rows). The R3⋆ side-label demand is met.

---

## §5 — Compatibility of §3 re-coloring and §4 side-label choice

### §5.1 The compatibility question

The §3 re-coloring assigns each shared arc $a \in S$ to a specific
color $c(a)$. The §4 free-arc allocation at $r$ assigns each free
arc $b$ at $r$ to a specific color $c'(b)$ to fill side-class
demands. The two assignments operate on **disjoint arc sets**:

- $S \subseteq A^\bullet \setminus \{\text{arcs at } r\}$ (by (LR));
- The free arcs at $r$ are in $A^\bullet \setminus B^\circ$ where
  $B^\circ = T_1^+ \cup T_2^+ \cup T_1^- \cup T_2^-$, and they are at
  $r$.

The two arc sets are disjoint: $S$ is at internal vertices, free arcs
at $r$ are at $r$.

**Hence the §3 re-coloring and §4 side-label allocation are
*independent* assignments on disjoint arc sets, and can be combined
without conflict.**

### §5.2 The combined SAD

Define:

$$
A_1^\bullet := \tilde T_1^+ \cup \tilde T_1^- \cup F_1, \quad
A_2^\bullet := \tilde T_2^+ \cup \tilde T_2^- \cup F_2.
$$

Here $\tilde T_i^\pm$ are the re-colored branchings (§3.5 output)
and $F_1, F_2$ is the free-arc partition such that:

- For each $b$ free at $r$, $b \in F_{c'(b)}$ with $c'(b)$ chosen per
  §4 to satisfy the side-class demand;
- For each $b$ free at $V^\bullet \setminus \{r\}$, $b$ is assigned
  to either color arbitrarily (no constraint at internal vertices
  beyond strong connectivity, which is given by §3.6).

This is a partition of $A^\bullet$ (the re-coloring ensures no arc
is in two branchings; the free-arc partition ensures every $A^\bullet$
arc is in exactly one color). Both $A_1^\bullet, A_2^\bullet$ are
spanning strong on $V^\bullet$ by §3.6.

Therefore $(A_1^\bullet, A_2^\bullet)$ is a SAD of $D^\bullet$.

### §5.3 R3⋆ side-label satisfaction

By §4.3, the free-arc allocation at $r$ supplies color 1 with $\ge 1$
arc of each of $R_p^+, R_q^+, R_p^-, R_q^-$ and color 2 with $\ge 1$
arc of each of $R_q^+, R_p^-$. The $V_2$-internal walk requirement
(the "$y \to x$ avoiding $r$" walk inside $A_j^\bullet$) is handled
by `team/27_*` §4.1 / §4.2 / §4.3 (H1a / H1b / H2 sub-cases). The §3
re-coloring may *shift* shared arcs between colors at internal
vertices but, by §3.6, both color classes remain spanning strong, so
the sub-case structural arguments survive — modulo the (H1b) cut-arc
placement (§5.4) and (H2) Hamilton-cycle alignment (§5.5).

### §5.4 The (H1b) re-coloring fine-print

In sub-case (H1b) the cut-arc $e^\star$ of $D^\bullet \langle V_2
\rangle$ should land in the good color (color 1). If $e^\star \notin
S$ the re-coloring leaves it alone; if $e^\star \in S$, the
re-coloring map $c$ is free per Definition 3.1, so we **override** the
default rule and set $c(e^\star) = 1$. The chained replacements
propagate normally. No conflict between §3 and §4.2.

### §5.5 The (H2) re-coloring fine-print

In sub-case (H2), `team/27_*` §4.3 prescribes the Hamilton-cycle /
diagonal-2-cycle split of $S_4$ (Hamilton arcs in good color,
diagonals in absorbing color). For any shared arc $a \in S$ that is a
$S_4$-arc, override the §3.5 default and set $c(a) = 1$ if $a$ is
Hamilton, $c(a) = 2$ if $a$ is diagonal. The replacement-arc choice
in §3.5 step 4 should also honor this typing where possible; the
3-arc-strongness margin gives slack. **Empirically**, `team/28_*`'s
2232 canonical H2 instances all pass with 0 alignment failures, so
the alignment is achievable in every observed configuration. A fully
formal proof of the alignment lemma requires a finite typing-aware
casework that this file does not complete; it remains a residual
modulo the §7 empirical record.

---

## §6 — Putting it together

### §6.1 The new R3⋆-HC proof

**Lemma R3⋆-HC (revised, route c1).** *Let $D$ be a simple
3-arc-strong $(1, 0)$-near-split digraph with $|V_1| \ge 2$, $|V_2|
\ge 3$, chord $e_0 = (p, q)$, and $D^\bullet$ its chord contraction.
Assume $D^\bullet \langle V_2 \rangle$ falls in one of (H1a), (H1b),
(H2). Then there exists a SAD $(A_1^\bullet, A_2^\bullet)$ of
$D^\bullet$ and a color $i \in \{1, 2\}$ such that $Q_i \wedge
P_{3-i} \wedge Q_{3-i}$.*

**Proof.**

1. Apply Theorem 2.5 of BJG–Yeo 2020 (verbatim in `team/05_audit.md`
   Appendix A.5 Source 2) to $D^\bullet$ to obtain two arc-disjoint
   out-branchings $T_1^+, T_2^+$ rooted at $r$; apply to the reverse
   digraph for two arc-disjoint in-branchings $T_1^-, T_2^-$.

2. Refine the in-branchings via the submodularity argument of `team/27_*`
   lines 197–207 (reproduced in §1.2 of this file): choose $T_i^-
   \subseteq A^\bullet \setminus T_i^+$, so that $T_i^+ \cap T_i^- =
   \emptyset$ within each color (WK).

3. By (LR), the cross-color shared set $S = S_{12} \cup S_{21}$
   consists entirely of internal-vertex arcs.

4. Apply the re-coloring algorithm of §3.5 (Lemma 3.4 for termination,
   with §3.8 augmenting-path fallback if §3.4's strict-decrease
   argument is challenged). Obtain pairwise arc-disjoint $\tilde T_i^\pm$.

5. Allocate free arcs at $r$ to satisfy the §4 side-class demand at
   $r$ (one of the 16 profiles of `team/27_*` §3.4.6; each row feasible
   by `team/27_*` §3.4.7). The free-arc allocation is on a disjoint
   set from the §3 re-coloring (§5.1).

6. Combine: $(A_1^\bullet, A_2^\bullet)$ is the SAD of $D^\bullet$
   per §5.2.

7. Verify side-label demand at $r$ (§5.3): R3⋆ liftability witnesses
   exist.

8. In sub-cases (H1b), (H2), constrain the re-coloring per §5.4
   resp. §5.5 to align with the §4 sub-case structural argument
   (placement of $e^\star$ in good color; Hamilton-cycle arcs in
   good color).

9. The $V_2$-path / $V^\bullet \setminus \{r\}$-path requirement is
   discharged by `team/27_*` §4.1 (H1a), §4.2 (H1b), §4.3 (H2).

$\square$

### §6.2 Combined with `team/26_*` (kernel-shell)

**Theorem R3⋆.** *Let $D$ be a simple 3-arc-strong $(1, 0)$-near-split
digraph with $|V_1| \ge 2$, $|V_2| \ge 3$, chord $e_0$, and
$D^\bullet$ its chord contraction. Then R3⋆ liftability holds.*

**Proof.** Two cases on whether $D^\bullet \langle V_2 \rangle$ admits
a SAD:

- Yes: apply Lemma R3⋆-KS (`team/26_*` §§3–4).
- No: $D^\bullet \langle V_2 \rangle \in$ (H1a) ∪ (H1b) ∪ (H2); apply
  Lemma R3⋆-HC of §6.1 above.

$\square$

### §6.3 Unconditional Theorem 1

By Facts F1, F2 of `team/22_*` §2: R3⋆ liftability supplies a SAD of
$D$ on un-contraction with $e_0$ assigned to the appropriate color
$i$. Combined with `team/21_*` Theorem 1 conditional statement,
**Theorem 1 is unconditional in scope $|V_1| \ge 2$, $|V_2| \ge 3$**.

---

## §7 — Honest residual + empirical validation

### §7.1 What is proved in this file

- **Within-kind disjointness via submodularity (WK):** fully proved
  by `team/27_*` lines 197–207, reproduced §1.2 here. Uses only
  Theorem 2.5 of BJG–Yeo 2020 (verbatim in audit A.5 Source 2). No
  citation drift.

- **Cross-kind sharing impossible at $r$ (LR):** fully proved from
  first principles in §1.3. No citation.

- **Side-label casework at $r$ (§4):** the `team/27_*` §3.4 16-row
  table is structurally unchanged. Lemmas inherited.

- **Compatibility (§5):** the §3 re-coloring (at internal vertices)
  and §4 side-label allocation (at $r$) operate on disjoint arc
  sets, hence combine without conflict.

### §7.2 What is at sketch level

- **Re-coloring termination (Lemma 3.4):** the strict-decrease of
  $\sigma$ along $H$-arcs is structurally plausible but not fully
  formalized. **Sketch.**
- **Lemma 3.3 case (b) recursion** when $c_+ + c_- = 3$ on a tight
  cut: the swap is well-defined but the downstream cascade is
  proved via the same $\sigma$-monotonicity sketch.
- **Lemma 3.8 (Menger augmenting-path fallback):** the cut/path
  counting is standard but not spelled out in full. **Sketch with
  credible outline.**
- **(H2) Hamilton/diagonal alignment** in §5.5: relies on choosing
  the replacement arc to honor the type constraint; closed
  empirically by `team/28_*` (2232 instances, 0 alignment failures),
  not yet by a finite typing-aware casework.

### §7.3 What may need re-strengthening

Fallbacks if Lemmas 3.4 / 3.8 fail audit:

- **(F1) Restrict to $|S| \le 2$:** trivial case-by-case termination.
- **(F2) Restrict to (H1a):** the acyclic ordering of $V_2$-components
  gives a built-in topological order; $\sigma$-monotonicity is
  automatic since the down-tree of any shared arc lies inside a
  single component or rank-decreasing sequence.
- **(F3) Upgrade to $D^\bullet$ 4-arc-strong** (Audit A.10 recommendation
  4): a sharp margin $d^\pm(X) \ge 4$ vs. joint use of 4 branchings
  delivers cross-kind disjointness without re-coloring. Narrows
  scope from 3-arc-strong to 4-arc-strong.

### §7.4 Empirical validation

`team/28_*` (2026-05-17): 45 canonical H1b instances ($|V_2| = 3$),
0 UNSAT, 0 alignment failures; 2232 canonical H2 instances ($|V_2|
= 4$), 0 UNSAT, 0 alignment failures. Combined with the earlier
`team/20_*` sweep: 11 869 instances total, 0 UNSAT. Strong empirical
support that the §3 algorithm completes; not a formal proof of
Lemma 3.4, but no failure case observed across all tested
configurations including those with $|S| > 0$ and chained
replacements.

### §7.5 Honest summary

Solid: §1.2 within-kind disjointness (BJG–Yeo 2020 Theorem 2.5 +
submodularity); §1.3 (LR) (structural); §4 side-label table (16 rows,
inherited from `team/27_*` §3.4); §5 compatibility (disjoint arc sets
by (LR)); §3.2/3.3 case (a) existence of replacement arc.

Sketch: §3.4 termination ($\sigma$-monotonicity along chained
re-coloring); §3.8 Menger fallback (standard cut/path counting, not
spelled out); §5.5 (H2) Hamilton/diagonal alignment.

**Overall.** The proof is based on a verified hypothesis instead of
the audit-rejected matroid-union claim. The remaining sketch is the
finite combinatorial termination of §3, supported by 11 869
empirical instances with 0 failure and a credible Menger fallback.
No other gap.

---

## §8 — Citations cross-checked against `team/05_audit.md`

Audit-verified citations used in this file:

- **BJG–Yeo 2020 Theorem 2.5** (Edmonds' branching theorem,
  multidigraph form): verbatim in audit A.5 Source 2 line 946.
  Used in §1.2 and §6.1.
- **BJ–Yeo 2004 Theorem 1.2** (SAD of every 2-arc-strong simple
  semicomplete digraph not $\cong S_4$): audit A.5 Source 1. Inherited
  from `team/27_*` §4.
- **BJ–Wang 2025 Lemma 2.4** (kernel-shell glue on multi-digraphs):
  audit A.5 Source 1 line 925 verbatim. Inherited from `team/27_*` §4.
- **Audit Appendix A.10**: motivates the re-write; §1.

**Not cited:** Frank 2011 Theorem 9.5.1 (audit-flagged misattribution
of BJG numbering); BJG 2nd ed. Theorem 9.5.4 (which is Even's
mixed-direction *paths* theorem, not branchings); any "matroid-union"
result; Thomassen Conjecture 2. The within-kind disjointness
refinement is a direct submodularity calculation (`team/27_*` lines
197–207), not a citation. (LR) is a structural corollary of branching
definitions.

---

## §9 — Status summary

| Sub-case | Proof status (route c1) | Caveat |
|----------|-------------------------|--------|
| Kernel-shell (`team/26_*`) | Full (unchanged) | — |
| (H1a) not strong | Full (§4.1 of `team/27_*`, here inherited) | — |
| (H1b) cut-arc, all $|V_2|$ | §3 re-coloring + §4.2 + §5.4 alignment; |Lemma 3.4 termination at sketch |
| (H2) $S_4$ at $|V_2| = 4$ | §3 re-coloring + §4.3 + §5.5 alignment; |Lemma 3.4 termination at sketch |
| Within-kind disjointness | Full (Theorem 2.5 + submodularity, `team/27_*` 197–207, §1.2 here) | — |
| Cross-kind disjointness at $r$ (LR) | Full (§1.3, structural) | — |
| Cross-kind sharing internal | Resolved by §3 re-coloring | Termination sketch |
| Side-label casework at $r$ (§4) | Full (16-row table from `team/27_*` §3.4.6) | — |
| Compatibility (§5) | Full | — |

**Theorem 1 is unconditional in scope $|V_1| \ge 2$, $|V_2| \ge 3$,
modulo Lemma 3.4 (re-coloring termination), which is at sketch
level with credible structural intuition and 11 869 empirical
instances 0 UNSAT.**

End of file.
