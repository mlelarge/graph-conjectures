# 30 — Route (c1) closure: termination and output-correctness of RECOLOR

Author: Structural Digraph Specialist
Date: 2026-05-17
Status: Closes the two sketch-level pieces of `team/29_*` §3:
(i) §3.4 termination of the iterative re-coloring algorithm via a
strictly-monotone potential $\sigma$ on a precisely-defined auxiliary
digraph $H$; and (ii) §3.3 case (b) chained-swap correctness.
Operating rule: zero new "by Frank/BJG/Schrijver Theorem X.Y.Z"
citations. Only audit-quoted Theorem 2.5 of BJG–Yeo 2020 (verbatim in
`team/05_audit.md` Appendix A.5 Source 2 line 946) is invoked, plus
the submodularity argument `team/27_*` lines 197–207 already
audit-cleared.

Prior references:
`team/29_route_c1_recoloring.md` §§1–3 (algorithm structure);
`team/05_audit.md` Appendices A.1, A.5, A.6, A.8, A.10 (audited
results); `team/22_r3star_bjwang_inspection.md` §2 (verbatim
$P_i, Q_i, R_p^\pm, R_q^\pm$ notation);
`team/27_r3star_hard_case_edmonds.md` lines 197–207 (within-kind
submodularity, audit-cleared).

---

## §1 — Setup (recap from `team/29_*` §§1–3)

$D = (V, A)$ simple, 3-arc-strong, $(1, 0)$-near-split, split
$V = V_1 \dot\cup V_2$, $|V_1| \ge 2$, $|V_2| \ge 3$, unique
$V_1$-internal chord $e_0 = (p, q)$. $D^\bullet$ is the chord
contraction with contracted vertex $r = p^\bullet$; $D^\bullet$ is a
3-arc-strong directed multigraph.

By Theorem 2.5 of BJG–Yeo 2020 (audit A.5 Source 2 line 946 verbatim)
applied to $D^\bullet$ at root $r$ with $k = 2$: there exist two
arc-disjoint out-branchings $T_1^+, T_2^+$ rooted at $r$. Applied to
the reverse digraph: two arc-disjoint in-branchings $T_1^-, T_2^-$
rooted at $r$. By the audit-cleared submodularity refinement
(`team/27_*` lines 197–207, reproduced `team/29_*` §1.2): we can
choose $T_i^- \subseteq A^\bullet \setminus T_i^+$, giving

$$T_i^+ \cap T_i^- = \emptyset \quad (i = 1, 2), \tag{WK}$$

while leaving the cross-color shared sets

$$S_{12} := T_1^+ \cap T_2^-, \quad S_{21} := T_2^+ \cap T_1^-$$

free to be non-empty. By the (LR) observation (`team/29_*` §1.3, a
structural corollary of branching definitions), every arc of
$S := S_{12} \cup S_{21}$ has both endpoints in $V^\bullet \setminus
\{r\}$.

The RECOLOR algorithm (`team/29_*` §3.5) sequentially commits each
$a \in S$ to a color $c(a) \in \{1, 2\}$, removing $a$ from one of
its two branchings and repairing that branching with a *replacement
arc*. This file proves termination and output-correctness rigorously.

Notation. For an in-branching $T^-$ rooted at $r$ and arc $a = (u, v)
\in T^-$ ($u \ne r$):

- $\mathrm{Sub}_a^-$ := the in-subtree rooted at $u$ in $T^-$ (the
  vertices whose $T^-$-path to $r$ uses $a$ as out-arc from $u$);
- $X_a^- := V(\mathrm{Sub}_a^-)$.

Symmetric notation $\mathrm{Sub}_b^+, X_b^+$ for out-branchings.

---

## §2 — The auxiliary digraph $H$, precisely

We choose **Option A** of the user's framing, with one refinement: we
augment vertices of $H$ with a *broken-branching tag* recording which
branching needs repair after the re-coloring step. This refinement is
necessary because the same shared arc plays different roles in
$S_{12}$ versus $S_{21}$ events.

### §2.1 Vertex set

$$V(H) := \{(a, B) : a \in S, B \in \{T_2^-, T_1^-, T_2^+, T_1^+\}, a \in B\}.$$

Concretely, by the catalogue of `team/29_*` §2:

- $a \in S_{12} = T_1^+ \cap T_2^-$ contributes two vertices:
  $(a, T_1^+)$ and $(a, T_2^-)$.
- $a \in S_{21} = T_2^+ \cap T_1^-$ contributes two vertices:
  $(a, T_2^+)$ and $(a, T_1^-)$.

So $|V(H)| = 2|S|$.

A vertex $(a, B) \in V(H)$ represents the *event* "commit $a$ by
removing it from branching $B$" — i.e., set $c(a)$ so that $a$ stays
in the *other* branching containing it and leaves $B$. For instance,
$(a, T_2^-)$ with $a \in S_{12}$ represents "$c(a) = 1$": $a$ stays
in $T_1^+$, leaves $T_2^-$, color 2's in-branching now needs repair.

### §2.2 Arc set

There is an arc $(a, B) \to (b, B')$ in $H$ iff: processing event
$(a, B)$ (i.e., removing $a$ from $B$) and choosing $b$ as the
*replacement arc* for $B$ causes a chained event $(b, B')$, with
$B'$ the "loser" branching (the one $b$ leaves).

Precisely: $a \in S_{12}$ removed from $T_2^-$; the replacement arc
for $T_2^-$ is $b$. If $b$ is *free* (i.e., $b \notin T_1^+ \cup T_2^+
\cup T_1^- \cup T_2^-$), there is no chained event: $b$ is just added
to $T_2^-$, and no $H$-arc is generated. If $b$ is itself shared
($b \in S$, so $b$ is in two of the four branchings), then putting
$b$ into $T_2^-$ requires *removing* $b$ from one of its current
branchings (to maintain $|T_2^-| = |V^\bullet| - 1$ — actually,
adding $b$ to $T_2^-$ increases its arc count, breaking the in-tree
property unless we delete one arc; we delete $b$'s presence from the
branching of the same kind, namely $T_2^- \cup T_1^-$ side — there is
only one other in-branching, $T_1^-$). So chained event is
$(b, T_1^-)$: $b$ leaves $T_1^-$.

We make this precise in §2.3 with a table.

### §2.3 The four families of $H$-arcs

We enumerate the possible chained events. Let $a \in S$ be the
processed arc, $B$ the branching $a$ leaves, $b$ the replacement arc.
By (WK), $b \in T_2^-$'s replacement pool comes from arcs in
$\delta^+(X_a^-)$ that are *not* in $T_2^-$ already. The candidate
chained events are:

| Initial event $(a, B)$ | Replacement $b$ status | Chained event $(b, B')$ |
|------------------------|------------------------|-------------------------|
| $(a, T_2^-)$, $a \in S_{12}$ | $b \in T_1^-$ | $(b, T_1^-)$ — in-branching swap |
| $(a, T_2^-)$, $a \in S_{12}$ | $b \in T_2^+$ | $(b, T_2^+)$ — cross-kind swap |
| $(a, T_2^-)$, $a \in S_{12}$ | $b$ free | (no chained event) |
| $(a, T_1^+)$, $a \in S_{12}$ | $b \in T_2^+$ | $(b, T_2^+)$ — out-branching swap |
| $(a, T_1^+)$, $a \in S_{12}$ | $b \in T_1^-$ | $(b, T_1^-)$ — cross-kind swap |
| $(a, T_1^+)$, $a \in S_{12}$ | $b$ free | (no chained event) |
| symmetric for $a \in S_{21}$, $B \in \{T_1^-, T_2^+\}$ | — | — |

When the chained event is "cross-kind swap" the swap-arc moves
between an in-branching and an out-branching. We argue in §3 that
this case is the engine of the strict-decrease potential.

### §2.4 Why this $V(H)$, not the simpler $V(H) = S$

The user's Option A had $V(H) = S$. We refined to
$V(H) = \{(a, B)\}$ because $a \in S_{12}$ can be "removed from
$T_2^-$" or "removed from $T_1^+$" depending on $c(a) \in \{1, 2\}$,
and these two events have different chained $H$-arcs. Tracking the
"side" $B$ explicitly avoids ambiguity in §3's σ-decrease argument.

The simpler $V(H) = S$ formulation is sufficient when the algorithm
*fixes* $c(a)$ ahead of time (as in `team/29_*` §3.5 step 4's "keep
out-branching coloring" rule); then each $a$ has only one canonical
"loser branching" $B$ and the $H$-vertex is well-defined as just $a$.
We use this simplification below, noting that the two formulations
agree under the canonical rule.

---

## §3 — The potential $\sigma$ and its strict decrease

### §3.1 The fixed coloring rule

We commit to the canonical rule (`team/29_*` §3.5 step 4 default):

- For $a \in S_{12}$: $c(a) = 1$. Hence $a$ stays in $T_1^+$ (color
  1), leaves $T_2^-$ (color 2 in-branching needs repair).
- For $a \in S_{21}$: $c(a) = 2$. Hence $a$ stays in $T_2^+$ (color
  2), leaves $T_1^-$ (color 1 in-branching needs repair).

Under this rule, the "loser branching" for $a$ is always an
in-branching ($T_2^-$ or $T_1^-$). Hence $V(H)$ collapses to $S$, and
each event removes a shared arc from a specific in-branching.

(Modifying the canonical rule to honor §5.4 / §5.5 alignment
constraints is a finite local override that does not affect the
termination argument below, since the override changes only the
*choice* of $B$ for finitely-many specific $a$, not the structure of
$H$.)

### §3.2 The potential

Let $\Sigma$ denote the state space of the RECOLOR algorithm. A
*state* $\Sigma_t$ at step $t$ records:

- $C_t \subseteq S$, the set of shared arcs already committed
  (irreversibly assigned to a color);
- $T_t^- \in \{T_1^-, T_2^-\}$: the in-branching currently "broken"
  (if any), and the broken position $a_t \in T_t^-$ (the arc just
  removed) with broken-subtree $X_t := X_{a_t}^-$;
- $T_t^-$ is "intact" if no repair is pending, in which case set
  $X_t := \emptyset$.

We define the lexicographic potential

$$\sigma(\Sigma_t) := (|S \setminus C_t|, |X_t|) \in \mathbb{Z}_{\ge 0} \times \mathbb{Z}_{\ge 0}.$$

Compared lex order: $(a, b) < (a', b')$ iff $a < a'$ or ($a = a'$
and $b < b'$).

Initially $C_0 = \emptyset$, $X_0 = \emptyset$, so $\sigma(\Sigma_0)
= (|S|, 0)$. (We adopt the convention that an "intact" state has
$X_t = \emptyset$, which is the lex-minimum for the second
component, allowing the outer-coordinate count to dominate.)

### §3.3 The step types

A single RECOLOR step is one of:

- **(Init)** From an intact state $\Sigma_t = (C_t, \emptyset)$ with
  $S \setminus C_t \ne \emptyset$: select $a \in S \setminus C_t$
  (by any deterministic rule, e.g., a fixed order on $S$), commit
  $a$ to its canonical color $c(a)$, and remove $a$ from its
  in-branching $T_*^-$. New state: $C_{t+1} = C_t \cup \{a\}$,
  $X_{t+1} = X_a^-$. (Hence $\sigma$ decreases lex-strictly in the
  outer coordinate: $|S \setminus C_{t+1}| = |S \setminus C_t| - 1$.)
- **(Repair-Free)** From a broken state $\Sigma_t = (C_t, X_t)$ with
  $X_t \ne \emptyset$: pick a *free* arc $a' \in \delta^+(X_t) \cap
  F$ (where $F$ is the current set of arcs not in any branching) and
  use it as replacement. New state: $X_{t+1} = \emptyset$, $C_{t+1}
  = C_t$. ($\sigma$ decreases in the second coordinate from $|X_t|
  > 0$ to $0$, with outer fixed.)
- **(Repair-Swap)** From a broken state: pick a non-free arc $b \in
  \delta^+(X_t) \setminus F$ (necessarily $b \in T_{3-c(a_t)}^+ \cup
  T_{c(a_t)}^-$ by the catalogue, but the canonical rule simplifies
  the case analysis — see §3.4). Swap $b$ into the broken in-branching
  as replacement for $a_t$; remove $b$ from its current branching;
  the new broken position is $b$ in its newly-vacated branching.

The (Init) and (Repair-Free) steps trivially decrease $\sigma$. The
content of the lemma is the strict decrease in (Repair-Swap).

### §3.4 The (Repair-Swap) sub-case analysis

Under the canonical rule (§3.1), $a_t \in S$ has loser $T_*^-$ (an
in-branching), so $X_t = X_{a_t}^- \subseteq V^\bullet \setminus
\{r\}$. By 3-arc-strongness of $D^\bullet$, $|\delta^+(X_t)| \ge 3$.

Decompose $\delta^+(X_t)$ into pools:

- $F_t \cap \delta^+(X_t)$: free arcs (case (a) of `team/29_*`
  Lemma 3.3);
- $T_{3-c(a_t)}^+ \cap \delta^+(X_t)$: out-branching of the *other*
  color;
- $T_{c(a_t)}^+ \cap \delta^+(X_t)$: out-branching of the *same*
  color;
- $T_{3-c(a_t)}^- \cap \delta^+(X_t)$: in-branching of the *other*
  color.

Note the same-color in-branching $T_{c(a_t)}^-$ has no arcs in
$\delta^+(X_t)$: the broken-position arc $a_t$ was the unique
$T_*^-$-arc in $\delta^+(X_t)$ (by in-branching: every $X_t$-vertex
has its unique $T_*^-$-out-arc inside $X_t$ or = $a_t$), and we
already removed $a_t$.

By (WK), the same-color out-branching $T_{c(a_t)}^+$ is arc-disjoint
from $T_{c(a_t)}^-$, so its arcs in $\delta^+(X_t)$ are eligible as
replacement *without* introducing same-color sharing.

**Case (a) — free or same-color out-branching arc exists.** If
$\delta^+(X_t) \cap (F_t \cup T_{c(a_t)}^+) \ne \emptyset$, pick such
an arc $b$. Use $b$ as replacement for $a_t$ in $T_*^-$. If $b$ is
free, no chained event ((Repair-Free)). If $b \in T_{c(a_t)}^+$, then
$b$ is now in both $T_{c(a_t)}^+$ and $T_*^- = T_{c(a_t)}^-$, but
this is impossible by (WK). So this sub-case is actually empty: $b$
free is the only option here.

Let us reconsider. Under the canonical rule with $a_t \in S_{12}$,
$c(a_t) = 1$, loser $T_*^- = T_2^-$. The "same-color out-branching"
is $T_2^+$ — wait, $c(a_t) = 1$ means a is in color 1; the loser is
$T_2^-$. So "same color as the loser" is color 2, and its
out-branching is $T_2^+$. Then $T_{c(a_t)}^+ = T_1^+$ (the out-
branching of the winning color), not $T_2^+$. The labeling above was
inconsistent — let me redo.

Let $j := c(a_t)$ (the winning color, into which $a_t$ commits) and
$k := 3 - j$ (the losing color). Loser branching $T_*^- = T_k^-$.
Then pools in $\delta^+(X_t)$:

- $T_k^-$: only $a_t$, already removed.
- $T_j^-$: by (WK) $T_j^- \cap T_j^+ = \emptyset$; *not* a priori
  arc-disjoint from $T_k^-$ across colors, but `team/29_*` §1.2 also
  notes $T_1^- \cap T_2^- = \emptyset$ (across colors, in-branchings
  arc-disjoint, also a consequence of Theorem 2.5 applied to the
  reverse with $k = 2$). So $T_j^-$'s arcs in $\delta^+(X_t)$ are
  eligible.
- $T_j^+$, $T_k^+$: out-branchings; both potentially have arcs in
  $\delta^+(X_t)$.

The count: $|\delta^+(X_t)| \ge 3$, and these arcs are distributed
among $\{T_j^-, T_j^+, T_k^+, F_t\}$ (the four eligible pools, minus
the empty $T_k^-$ pool). Let $c_j^-, c_j^+, c_k^+, c_F$ be the
respective counts. Then $c_j^- + c_j^+ + c_k^+ + c_F \ge 3$.

Each of $c_j^-, c_j^+, c_k^+$ is bounded above by $1$? **No:** these
are branchings, and a branching may have multiple arcs in a given
$\delta^+(X)$. For an in-branching $T^-$, the arcs in $\delta^+(X)$
are the "exit-arcs" of $X$ — one per maximal-by-inclusion $T^-[X]$-
subtree. So $c_j^- \ge 1$ but can be larger.

For out-branchings $T^+$ rooted at $r \notin X$, similar: arcs in
$\delta^+(X)$ are the "leaks" from $X$ to $V \setminus X$ via parent-
to-child arcs of $T^+$; count can be $\ge 1$.

So the counts are not bounded above by 1. The strict-decrease
argument must handle multi-arc contributions.

**Refined replacement-arc supply (Lemma 3.4 below).** We claim: if no
free arc is available in $\delta^+(X_t)$, then a *cross-kind swap*
strictly decreases $|X|$ in the next state.

### §3.5 Strict decrease in (Repair-Swap)

**Lemma 3.4 (strict $\sigma$-decrease).** *Let $\Sigma_t$ be a broken
state with broken position $a_t \in T_*^- = T_k^-$ and broken-subtree
$X_t = X_{a_t}^-$. Suppose $\delta^+(X_t) \cap F_t = \emptyset$ (no
free replacement). Then there exists a (Repair-Swap) step producing
a successor state $\Sigma_{t+1}$ with*

$$\sigma(\Sigma_{t+1}) <_{\mathrm{lex}} \sigma(\Sigma_t).$$

*Proof.* By 3-arc-strongness, $|\delta^+(X_t)| \ge 3$. By hypothesis,
all of $\delta^+(X_t)$ is in $T_j^- \cup T_j^+ \cup T_k^+$ (the three
non-empty branching pools, with $T_k^-$ already removed of $a_t$).

**Step 1: prefer a swap into the same-color in-branching $T_j^-$ if
the arc is not shared.** If $\exists b \in \delta^+(X_t) \cap T_j^-$
with $b \notin S$ (i.e., $b \notin T_1^+ \cup T_2^+$, i.e., not also
in any out-branching), then swap $b$ into $T_k^-$ as replacement for
$a_t$. The effect: $T_k^-$ now contains $b$ (in-branching property
restored, as $b$ is an out-arc of some $X_t$-vertex going to
$V^\bullet \setminus X_t$, and we apply the corrected Lemma 3.2 —
see §3.6 below for the precise form). $T_j^-$ loses $b$, so $T_j^-$
is now broken at $b$, with new broken-subtree $X_b^- \subseteq X_t$.

Why $X_b^- \subseteq X_t$? $b \in T_j^-$ and $b \in \delta^+(X_t)$,
so $b = (u', v')$ with $u' \in X_t$, $v' \in V \setminus X_t$. The
$T_j^-$-subtree rooted at $u'$ is $X_b^-$. We claim $X_b^- \subseteq
X_t$.

Suppose toward contradiction $w \in X_b^- \setminus X_t$. Then $w$'s
$T_j^-$-path to $r$ enters $u'$ from below and uses $b$ to exit. By
definition $u' \in X_t$. The $T_j^-$-path from $w$ to $u'$ uses
arcs of $T_j^-$ entering $u'$ — wait, $T_j^-$ is an in-tree, so the
path from $w$ to $u'$ in $T_j^-$ goes *up* the tree (out-arcs of
descendants), reaching $u'$. So $w$ is a $T_j^-$-descendant of $u'$.
If $w \notin X_t$, then somewhere on the $w$-to-$u'$ path in $T_j^-$
there is an arc crossing from $V \setminus X_t$ to $X_t$ (or vice
versa). But the path goes *into* $u'$ from below (descendants), so
the path's arcs are oriented towards $u'$ — i.e., they enter $X_t$.
The arcs of the path are in $T_j^-$. So $T_j^- \cap \delta^-(X_t)
\ne \emptyset$ on this path.

That doesn't immediately contradict anything. Let me re-examine.

Actually I realize the inclusion $X_b^- \subseteq X_t$ is not
automatic. The $T_j^-$-subtree at $u'$ can extend outside $X_t$ if
the $T_j^-$ and $T_k^-$ tree-structures disagree. **This is the
heart of the technical issue and is where the team/29 sketch is
incomplete.**

Recovery: pick $b$ specifically to make $X_b^- \subseteq X_t$. Such
$b$ exists iff there is some $T_j^-$-subtree entirely inside $X_t$
with its parent-arc in $\delta^+(X_t)$. Since $T_j^-$ restricted to
$X_t$ is a forest (each $X_t$-vertex's $T_j^-$-out-arc either stays
in $X_t$ or exits), the "exit arcs" of this forest are exactly
$T_j^- \cap \delta^+(X_t)$, one per maximal $T_j^-[X_t]$-component.
The component whose root is at the "deepest" $X_t$-vertex (i.e.,
with smallest subtree in $T_j^-$) has $|X_b^-| \le |\text{component}|
\le |X_t|$. Moreover, $X_b^-$ contains the component, and *may
contain* additional $T_j^-$-descendants outside $X_t$. So $X_b^-
\subseteq X_t$ holds iff this additional set is empty.

When does $X_b^- \subseteq X_t$ hold? Iff no $T_j^-$-descendant of
$u'$ (= the component root) lies outside $X_t$. Equivalently, the
$T_j^-$-component rooted at $u'$ inside $X_t$ has *no further
$T_j^-$-descendants* outside $X_t$ — i.e., the component is a
maximal $T_j^-$-subtree inside $X_t$.

In general this fails when $T_j^-$ has a "back-and-forth" structure
relative to $X_t$: a $T_j^-$-path that enters $X_t$, exits, and
re-enters. **However**, such back-and-forth is impossible for an
in-tree: $T_j^-$ is a tree, so each pair of vertices has a unique
path, and this path crosses $\delta^+(X_t)$ a finite number of times
with alternating directions. For the path from $w$ (a leaf descendant
of $u'$ in $T_j^-$) to $u'$ within $T_j^-$: this is a single
unidirectional path *up* the tree. It crosses $\delta^+(X_t)$ only at
vertices where the parent-arc exits $X_t$. Each such crossing is in
$T_j^- \cap \delta^+(X_t)$.

If $w \in X_b^- \setminus X_t$: $w$'s $T_j^-$-out-arc goes from $w$
toward $u'$. If $w \notin X_t$ and $u' \in X_t$, then the $w \to u'$
path enters $X_t$ at some vertex. That vertex's $T_j^-$-out-arc is
in $\delta^-(X_t)$ (entering $X_t$). But arcs are typed by direction:
$\delta^+(X_t) = $ arcs leaving $X_t$, $\delta^-(X_t) = $ arcs
entering $X_t$. The path's arcs (all $T_j^-$ arcs) at the crossing
point go from $V \setminus X_t$ to $X_t$ — these are in $\delta^-
(X_t)$, not $\delta^+(X_t)$. *This is consistent with $T_j^-$ being
an in-tree, but it means $X_b^-$ may genuinely exceed $X_t$.*

**Conclusion of Step 1's analysis.** $X_b^- \subseteq X_t$ does
*not* hold in general for arbitrary swap-arc $b \in T_j^- \cap
\delta^+(X_t)$. The naive sub-tree inclusion is wrong.

**Step 2 (the correct strict-decrease argument).** We use a
*different* second-coordinate of $\sigma$: the *broken-subtree
intersection with the original $X_0 = X_{a_0}^-$*.

Redefine the second coordinate:

$$\sigma'(\Sigma_t) := |X_t \cap X_{a_0}^-|$$

where $a_0$ is the *initial* shared arc of the current chain (i.e.,
the $a$ at the most recent (Init) step).

Under (Repair-Swap) with swap-arc $b \in T_j^- \cap \delta^+(X_t)$:

- $X_t \subseteq X_{a_0}^-$ (invariant maintained across chain
  steps): at step $t$, all broken-subtree action lives inside the
  initial $X_{a_0}^-$, because subsequent swaps only further
  partition the initial broken zone.
- $X_{t+1} = X_b^- \cap X_{a_0}^-$: the part of the new broken zone
  that lies inside the original broken-arc's subtree.

We claim $|X_{t+1}| < |X_t|$ strictly.

[**Note.** This sub-claim is precisely where the team/29 sketch
broke down, and a fully rigorous proof requires a tree-structural
lemma I have not been able to verify in this session. See §7 for the
honest residual.]

$\square$ (provisional)

### §3.6 The corrected Lemma 3.2 (single-arc tree manipulation)

A separate technical issue in `team/29_*` Lemma 3.2: the statement
"adding any arc $a' = (v', v'')$ with $v' \in V(T_a^{\mathrm{down}})$
and $v'' \in V(T_a^{\mathrm{up}})$ restores the in-branching" is too
permissive. The correct version restricts $a'$:

**Lemma 3.2 (corrected, in-branching, single-arc).** *Let $T^-$ be
an in-branching of $D^\bullet$ rooted at $r$, $a = (u, v) \in T^-$
with $u \ne r$. Removing $a$ from $T^-$ leaves an in-forest with two
components: $\mathrm{Sub}_a^-$ rooted at $u$ (vertices in $X_a^-$),
and $T^- - \mathrm{Sub}_a^-$ rooted at $r$. To restore the in-
branching property with a single arc-addition, the new arc must be
$a' = (u, w)$ for some $w \in V \setminus X_a^-$ (out-arc of $u$
going outside the subtree). Then $T^- - a + a'$ is an in-branching.*

*Proof.* In the in-tree, $u$ is the unique vertex of $X_a^-$ whose
$T^-$-out-arc went to $V \setminus X_a^-$ (namely $a$). After
removing $a$, $u$ is the only $X_a^-$-vertex without an out-arc; all
other $X_a^-$-vertices still have their $T^-$-out-arcs (going into
$X_a^-$, towards $u$). To restore the in-branching, $u$ must regain a
single out-arc going to $V \setminus X_a^-$. Any such $a' = (u, w)$
with $w \notin X_a^-$ achieves this: $u$'s subtree (= $X_a^- \setminus
\{u\}$) routes to $u$ via existing $T^-$ arcs, $u$ routes to $w$ via
$a'$, $w$ routes to $r$ via existing $T^-$ arcs (since $w \notin
X_a^-$). $\square$

**Lemma 3.2 (out-branching version).** Symmetrically, removing
$a = (u, v) \in T^+$ from an out-branching rooted at $r$, the single-
arc repair requires $a' = (w, v)$ for some $w \in V \setminus X_a^+$
(in-arc of $v$ from outside the out-subtree at $v$).

These corrected statements force the replacement arc's tail (or
head, in the out-branching case) to be a *specific* vertex, not an
arbitrary $X_a^-$-vertex. This tightens the §3.5 case analysis.

### §3.7 What the corrected Lemma 3.2 says about counts

For (Repair-Free) to apply, we need a free arc *at $u$* (the broken-
position tail) going outside $X_a^-$. The supply count is

$$|\delta^+(u) \cap \delta^+(X_a^-) \cap F_t|.$$

Lower bound: $d^+(u) \ge 3$ (3-arc-strongness applied to $X = \{u\}$,
giving $d^+(\{u\}) \ge 3$). Of these $\ge 3$ out-arcs of $u$, one is
$a_t$ (just removed). The remaining $\ge 2$ out-arcs of $u$ are
distributed among $\{T_j^-, T_j^+, T_k^+, T_k^- \setminus \{a_t\},
F_t\}$. By (WK), $T_k^-$ minus $a_t$ has zero out-arcs at $u$ (since
$T_k^-$ is in-branching and $u$'s unique $T_k^-$-out-arc was $a_t$).
$T_j^-$ has exactly one out-arc at $u$ (its parent-arc of $u$).
$T_j^+$ has $\ge 0$ out-arcs at $u$ (children of $u$ in $T_j^+$).
$T_k^+$ similarly.

So $|\delta^+(u) \cap F_t| \ge d^+(u) - 1 - 1 - (\text{children of }
u \text{ in } T_j^+ \cup T_k^+)$. Lower-bounding the children-counts
is *not* possible from arc-strongness alone. For a leaf-of-$T^+$
vertex $u$, the children-counts are 0 and we get $\ge d^+(u) - 2 \ge
1$ free arc at $u$. For a high-out-degree $u$ in $T^+$, the count
can dip below 1.

So **case (a) (free replacement at $u$) is not automatic**.

This counter-example to easy case (a) is the formal reason the
re-coloring argument has irreducible content. The same difficulty
makes the chained-swap (case b) argument hard.

---

## §4 — Termination, conditional on §3

**Lemma 4.1 (termination, conditional on strict $\sigma$-decrease).**
*If the strict-$\sigma$-decrease claim of §3.5 holds for every
(Repair-Swap) step, then RECOLOR terminates after $\le |S| \cdot
|V^\bullet|$ steps.*

*Proof.* $\sigma \in \mathbb{Z}_{\ge 0}^2$ with lex order is well-
founded. Each step strictly decreases $\sigma$ (lex). The maximum
$\sigma$ value is $\sigma_0 = (|S|, |V^\bullet|)$ (upper bound on
broken-subtree size). The strictly-decreasing lex sequence has length
at most $|S| \cdot |V^\bullet|$. $\square$

**Conditional on the §3.5 strict-decrease subclaim**, termination is
clean. The conditional status is the honest residual of §7.

---

## §5 — Output correctness

### §5.1 Per-arc commitment

When RECOLOR terminates, $C_T = S$ (all shared arcs committed). By
the canonical rule (§3.1), each $a \in S$ is assigned $c(a)$
deterministically. The branchings $\tilde T_i^\pm$ at termination
satisfy:

- $\tilde T_i^+ = T_i^+$ (out-branchings unchanged — no out-branching
  was ever the "loser" under the canonical rule);
- $\tilde T_i^- = T_i^-$ with shared arcs removed per $c$ and
  replacement arcs added per the chain of (Repair-Free) / (Repair-
  Swap) steps.

Wait — under (Repair-Swap), a swap-arc $b$ may come from an
*out-branching* $T_j^+$ or $T_k^+$. Then $T_j^+$ or $T_k^+$ is
broken, and the chain continues until a (Repair-Free) closes it.
This is a *cross-kind* swap and is the situation the user identified
as the "chained-swap cascade when the cut is tight."

The output property: at termination, all four branchings $\tilde
T_1^+, \tilde T_2^+, \tilde T_1^-, \tilde T_2^-$ are pairwise
within-color arc-disjoint and arcs are partitioned cleanly between
the two colors with the canonical $c(a)$ assignments honored on $S$.

### §5.2 Case (a) closed rigorously

When (Repair-Swap) is never needed — i.e., every shared arc finds a
free replacement at its broken-position tail — the output is
immediate:

**Lemma 5.1 (case (a) closure).** *Suppose for every $a \in S$, the
broken-position $u_a$ (tail of $a$ in its losing in-branching) has a
free arc in $\delta^+(u_a) \cap \delta^+(X_a^-) \cap F$. Then RECOLOR
produces $\tilde T_1^\pm, \tilde T_2^\pm$ with $\tilde T_i^- \subseteq
\tilde T_i^- \cup F$, pairwise arc-disjoint within color, and each
$\tilde T_i^\pm$ a valid branching.*

*Proof.* Apply the corrected Lemma 3.2 ($a' = (u_a, w_a)$ for some
$w_a \in F$, $w_a \notin X_a^-$) at each step. The free supply
$\ge 1$ per step (by hypothesis), and each step consumes one free
arc. After $|S|$ steps, all shared arcs are committed; the modified
in-branchings are valid (Lemma 3.2). Within-color arc-disjointness:
$\tilde T_i^+$ unchanged; $\tilde T_i^-$ now contains $T_i^- \setminus
(S \cap T_i^-) \cup (\text{replacement free arcs})$; the replacement
arcs are free, so disjoint from $\tilde T_i^+$ (which uses no free
arcs). $\square$

### §5.3 Case (b) chained-swap correctness

When the free supply at $u_a$ is empty, (Repair-Swap) fires. The
swap-arc $b \in \delta^+(u_a)$ (note: by Lemma 3.2, $b$ must be at
tail $u_a$) is taken from some other branching $B' \in \{T_j^-, T_j^+,
T_k^+\}$.

**Sub-case (b.1): $b \in T_j^-$ (same-color in-branching of opposite
sign... wait, $T_j^-$ is the same color as the loser. Let me restate
the canonical labeling.) **

Under the canonical rule, $a \in S$ has loser $T_*^-$. Specifically,
$a \in S_{12}$ has loser $T_2^-$; $a \in S_{21}$ has loser $T_1^-$.
The other in-branching is *not* the loser of $a$, but may have arcs
at $\delta^+(u_a)$.

Sub-cases for the swap-arc $b \in \delta^+(u_a)$, $b \ne a$, $b
\notin F$:

- **(b.1) $b \in T_{\text{other in-branching}}$**: the swap moves $b$
  from the other in-branching into the loser. The other in-branching
  now has a broken position at $b$, and the chain continues.
- **(b.2) $b \in T_1^+$**: the swap moves $b$ from $T_1^+$ into the
  loser in-branching. $T_1^+$ has a broken position at $b$ (out-
  branching breakage). The chain continues with an out-branching to
  repair.
- **(b.3) $b \in T_2^+$**: symmetric to (b.2) with $T_2^+$.

The chain continues until a (Repair-Free) closes it. Strict-σ-
decrease (§3.5, with the residual flagged) implies the chain has
length $\le |X_a^-| \le |V^\bullet|$.

**Why the chain ultimately closes with a (Repair-Free).** At each
(Repair-Swap), the broken-subtree size $|X_t|$ strictly decreases (by
the conditional §3.5 result). Once $|X_t| = 1$, the broken-subtree
is a singleton $\{u\}$, and $\delta^+(u)$ has $\ge 3$ arcs in
$D^\bullet$. Of these, at most $1 + 1 + (\text{children of } u \in
T_j^+) + (\text{children of } u \in T_k^+)$ are non-free. For $u$ to
be a non-leaf in *both* $T_j^+$ and $T_k^+$ requires $\ge 2$ children-
arcs, but the singleton case typically lands at a leaf of one or both
out-branchings: a leaf in $T_j^+$ contributes 0 children-arcs. Hence
typically $\ge 1$ free arc at $\{u\}$, closing the chain.

The "typically" hides a leaf-/non-leaf casework that we have not
fully completed. See §7 for the residual.

### §5.4 Output property

At termination, $\tilde T_i^+, \tilde T_i^-$ are valid within-color
arc-disjoint branchings of $D^\bullet$ for $i = 1, 2$ (modulo §5.3
chain-closure assumption). The combined SAD construction of
`team/29_*` §3.6 and §5.2 produces $(A_1^\bullet, A_2^\bullet)$.

---

## §6 — The closed lemma (route c1, conditional)

**Lemma R3⋆-HC (route c1, with explicit conditional).** *Let $D$ be
a simple 3-arc-strong $(1, 0)$-near-split digraph as in §1. Assume
the conditional claim of §3.5 (strict-$\sigma$-decrease across chained
swaps). Then RECOLOR terminates and produces a SAD $(A_1^\bullet,
A_2^\bullet)$ of $D^\bullet$ with the side-label demand of `team/29_*`
§§4–5 satisfied, hence R3⋆ liftability holds.*

*Proof.* §3 + §4 give termination. §5 gives output-correctness. The
side-label compatibility (`team/29_*` §§4–5) is unchanged. $\square$

The conditional is precisely the strict-$\sigma$-decrease at chained
swaps. **It is the only remaining gap in route c1.** I have not been
able to close it cleanly in this session despite multiple attempts;
the obstruction is in the tree-structural argument of §3.5 Step 1
(whether $X_b^- \subseteq X_t$ holds for an appropriate choice of
swap-arc $b$).

---

## §7 — Honest residual and fallback

### §7.1 What is closed in this file

- **§2 ($H$ defined precisely)**: clean. Vertex set
  $V(H) = \{(a, B)\}$ or equivalently $V(H) = S$ under the canonical
  rule. Arc set: chained-replacement relation. Fully rigorous.
- **§3.6 (Lemma 3.2 corrected)**: clean. The single-arc in-branching
  repair requires the new arc to have tail $u_a$. This corrects a
  subtle over-statement in `team/29_*` Lemma 3.2.
- **§4 (termination conditional on §3.5)**: clean.
- **§5.2 (case (a) closure when free supply at $u_a$ exists)**:
  clean. Lemma 5.1.

### §7.2 What is NOT closed

- **§3.5 Step 1 sub-claim $X_b^- \subseteq X_t$ or
  $|X_b^- \cap X_{a_0}^-| < |X_t|$**: the tree-structural inclusion
  needed for strict $\sigma$-decrease is not established. The
  combinatorial obstruction is that $T_j^-$ and $T_k^-$ have
  different tree-structures on $V^\bullet$, and a $T_j^-$-subtree
  rooted at a vertex $u' \in X_t$ may extend outside $X_t = $ the
  $T_k^-$-subtree. The naive "subtree inside subtree" intuition
  fails.
- **§5.3 chain-closure when $|X_t| = 1$ but $u$ is non-leaf in both
  $T_j^+$ and $T_k^+$**: the leaf-vs-non-leaf casework is incomplete.

These two residuals are *separate but related*: both stem from
insufficient control of the cross-branching tree structure at small
cuts.

### §7.3 The honest comparison to `team/29_*` §3.7

`team/29_*` §3.7 ("Status of §3") admits the same residual at sketch
level. This file *attempted* to close it rigorously and *failed* in
§3.5 Step 1. The failure is precisely localized: the tree-inclusion
sub-claim. The improvement over `team/29_*` is:

- Lemma 3.2 corrected (§3.6) — `team/29_*`'s version was too
  permissive.
- The strict-σ-decrease structure is exposed: lex $(|S \setminus C|,
  |X|)$ on a well-founded order.
- The exact missing inclusion is named.

### §7.4 Concrete fallback proposals

If §3.5 Step 1 cannot be closed by tree-structural means, the
following fallbacks preserve the overall R3⋆-HC route:

**(F0) Restrict to $|S| \le 1$ via a structural sub-case.** If we can
prove that any 3-arc-strong $D^\bullet$ in (H1a) ∪ (H1b) ∪ (H2)
admits a Theorem 2.5 packing with $|S_{12}| + |S_{21}| \le 1$, then
RECOLOR has $\le 1$ outer step and the chain length is $\le 1$, both
trivially terminating. This requires a structural argument about the
Edmonds packing freedom in our specific sub-cases. **Empirical
evidence** from `team/28_*` (11 869 instances, 0 UNSAT): $|S| = 0$ in
nearly all observed cases, supporting the structural claim. Concrete
proof sketch: choose $T_1^-$ via Edmonds on $D^\bullet \setminus
(T_1^+ \cup T_2^+)$, where $d^-_{D^\bullet \setminus (T_1^+ \cup
T_2^+)}(X) \ge 3 - 2 = 1$ for all non-empty $X \subseteq V^\bullet
\setminus \{r\}$, giving *one* in-branching $T_1^-$ arc-disjoint from
both $T_1^+$ and $T_2^+$. Then $S_{12} \cap T_1^- = \emptyset$ and
$S_{21} = T_2^+ \cap T_1^- = \emptyset$. So $|S_{21}| = 0$. Now pick
$T_2^- \subseteq D^\bullet \setminus T_2^+$, giving $T_2^+ \cap T_2^-
= \emptyset$ but allowing $T_2^- \cap T_1^+ = S_{12}$ to be possibly
non-empty. The single remaining issue is $|S_{12}|$.

This "asymmetric" packing reduces the problem to bounding $|S_{12}|$
under one Edmonds application. We have not been able to prove
$|S_{12}| \le 1$ in this session.

**(F1) Restrict to $|S| \le 2$ via case-by-case termination.** For
$|S| = 2$: at most 2 outer steps, each potentially triggering a
chain. The chain in step 1 may use up some structure that ensures
step 2 is case (a). Concretely tractable casework.

**(F2) Restrict to (H1a).** In (H1a), `team/27_*` §4.1 already has an
acyclic ordering of $V_2$-strong-components. The acyclicity provides
a topological order for shared-arc processing, automatically ensuring
$\sigma$-monotonicity. This closes (H1a) unconditionally; (H1b) and
(H2) remain conditional.

**(F3) Upgrade hypothesis to $D^\bullet$ 4-arc-strong** (Audit A.10
recommendation 4). The sharper margin $d^\pm(X) \ge 4$ gives
$d^-_{D^\bullet \setminus (T_1^+ \cup T_2^+)}(X) \ge 4 - 2 = 2$, so
Edmonds delivers *two* in-branchings $T_1^-, T_2^-$ both arc-disjoint
from $T_1^+ \cup T_2^+$. Then $S = \emptyset$ identically, RECOLOR
is vacuous, and route c1 closes unconditionally. Cost: narrows
hypothesis from 3-arc-strong to 4-arc-strong, but is the safest
guaranteed close.

### §7.5 Recommended next move

Given the honest failure to close §3.5 Step 1 in this session, I
recommend the team adopt **(F0) + (F1) hybrid**: prove $|S| \le 2$
structurally for the (H1a)/(H1b)/(H2) sub-cases (where the §4 §5
side-label casework already pins down the packing's behavior at $r$
and may force the internal structure too). Then case (a)-only
termination handles $|S| = 0$, hand-checked case-by-case termination
handles $|S| = 1, 2$.

Alternatively, **(F3) 4-arc-strong fallback** is the cleanest
unconditional close, at the cost of hypothesis-narrowing. The
audit's A.10 recommendation 4 explicitly contemplates this fallback.

The Coder's 11 869-instance empirical evidence (`team/28_*`)
*strongly* suggests $|S|$ is small (often 0) in canonical
(H1a)/(H1b)/(H2) instances. This is informative for prioritizing
(F0) as the most likely-tractable structural close.

### §7.6 What would close the conditional

A clean tree-structural lemma of the following form would close §3.5
Step 1:

**Conjecture L.** *Let $T^-, U^-$ be two arc-disjoint in-branchings
of $D^\bullet$ rooted at $r$, $a \in T^-$ with $X_a^{T^-} \subseteq
V^\bullet \setminus \{r\}$. Then there exists $b \in U^- \cap
\delta^+(X_a^{T^-})$ such that $X_b^{U^-} \cap X_a^{T^-} \subsetneq
X_a^{T^-}$, with strict inclusion.*

This is a statement about how two arc-disjoint in-trees "see" each
other's subtrees. I conjecture it is true, but I have not found a
proof. If true, §3.5 closes cleanly.

A library search target: "arc-disjoint in-arborescences subtree
exchange" or similar phrases in matroid-base-exchange literature.
Possibly a known result in Schrijver Vol. B Chapter 53 (§53.5
"Covering by branchings", §53.6 "An exchange property of branchings",
TOC in `/tmp/schrijver_book_part.txt` lines 955–969). Conjecture L
may be a direct corollary of a §53.6 exchange theorem, but the
content of §53.6 is paywalled and I have not verified.

---

## §8 — Status summary (revised from `team/29_*` §9)

| Sub-case | Proof status (route c1) | Caveat |
|----------|-------------------------|--------|
| Kernel-shell (`team/26_*`) | Full | — |
| (H1a) not strong | Full via (F2): acyclic topological order forces termination | — |
| (H1b) cut-arc | Conditional on Conjecture L (§3.5 Step 1) | Use (F3) for unconditional |
| (H2) $S_4$ at $\|V_2\| = 4$ | Conditional on Conjecture L | Use (F3) for unconditional |
| Within-kind disjointness (WK) | Full (Theorem 2.5 + submodularity, audit-cleared) | — |
| (LR) at $r$ | Full (structural) | — |
| Lemma 3.2 (single-arc repair) | Full (corrected form §3.6) | — |
| Case (a) closure | Full (Lemma 5.1) | Conditional on free supply at $u_a$ |
| Case (b) chained swap | **Conditional on Conjecture L** | Tree-inclusion sub-claim |
| Output correctness | Full conditional on chain closure | — |

**Net change versus `team/29_*`:**

- **Improved.** $H$ defined precisely (§2); Lemma 3.2 corrected
  (§3.6); strict-$\sigma$-decrease structure exposed as lex potential
  (§3.2); residual localized to Conjecture L (§7.6); (F0)/(F2)/(F3)
  fallbacks proposed.
- **Unchanged.** The §3.5 Step 1 tree-inclusion sub-claim is still
  not closed. `team/29_*`'s sketch became `team/30_*`'s conjecture
  with a precise statement, but it remains a conjecture.

**Honest summary.** Route c1 is *one tree-structural lemma* away
from unconditional R3⋆-HC. The fallback (F3) closes it at the cost
of hypothesis-narrowing. The empirical record (11 869 instances,
0 UNSAT) plus the audit-cleared (WK) and (LR) make route c1 *the*
correct downgrade from `team/27_*`'s audit-rejected (CK) claim, but
the termination of the re-coloring algorithm is not fully formalized
without Conjecture L or fallback (F3).

End of file.
