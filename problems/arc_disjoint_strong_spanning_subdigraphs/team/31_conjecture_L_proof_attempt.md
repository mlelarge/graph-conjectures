# 31 — Conjecture L: one-session proof attempt

Author: Structural Digraph Specialist
Date: 2026-05-17
Status: One focused session to close or fail honestly. Operating rule
in force (`feedback_citation_verification.md`, fifth escalation): zero
new "by Frank / BJG / Schrijver Theorem X.Y.Z" citations. Only audit-
quoted Theorem 2.5 of BJG–Yeo 2020 (audit Appendix A.5 Source 2 line
946) and the within-kind submodularity argument (`team/27_*` lines
197–207, audit-cleared) are invoked. Everything else proved from
scratch.

Prior references:
`team/30_route_c1_termination.md` §7.6 (Conjecture L statement,
authoritative); `team/29_route_c1_recoloring.md` §3 (the RECOLOR
algorithm Conjecture L would support); `team/27_*` lines 197–207
(within-kind disjointness); `team/05_audit.md` Appendices A.5, A.10,
A.12.

---

## §1 — Conjecture L verbatim

Reproduced from `team/30_route_c1_termination.md` lines 756–761:

> **Conjecture L.** *Let $T^-, U^-$ be two arc-disjoint in-branchings
> of $D^\bullet$ rooted at $r$, $a \in T^-$ with $X_a^{T^-} \subseteq
> V^\bullet \setminus \{r\}$. Then there exists $b \in U^- \cap
> \delta^+(X_a^{T^-})$ such that $X_b^{U^-} \cap X_a^{T^-} \subsetneq
> X_a^{T^-}$, with strict inclusion.*

### §1.1 Notation pin-down

For an in-branching $T^-$ rooted at $r$:

- Every vertex $w \ne r$ has a unique $T^-$-out-arc, going from $w$ to
  its **$T^-$-parent** $\pi^{T^-}(w)$.
- For an arc $a = (u, v) \in T^-$ (so $\pi^{T^-}(u) = v$, hence $v$
  is $u$'s $T^-$-parent), the **$T^-$-subtree below $a$** is
  $$X_a^{T^-} := \{w \in V^\bullet \,:\, \text{the unique $T^-$-walk
    } w \to r \text{ uses arc } a\}.$$
  Equivalently, $X_a^{T^-}$ is the set of $T^-$-descendants of $u$
  together with $u$ itself (the subtree "rooted at $u$" in the
  in-branching sense). In particular $u \in X_a^{T^-}$ and
  $v \notin X_a^{T^-}$.
- The hypothesis $X_a^{T^-} \subseteq V^\bullet \setminus \{r\}$ is
  automatic from $u \ne r$ (which is forced by $a \in T^-$: the root
  $r$ has no $T^-$-out-arc).

Let $X := X_a^{T^-}$ for the rest of this file. Set
$$E^+ := U^- \cap \delta^+(X), \qquad E^- := U^- \cap \delta^-(X).$$

Conjecture L asserts: $\exists\, b \in E^+$ with $X_b^{U^-} \cap X
\subsetneq X$ (i.e., **some** $b \in E^+$ has its $U^-$-subtree
**not** containing all of $X$).

The negation: $\forall\, b \in E^+$, $X \subseteq X_b^{U^-}$.

### §1.2 First sanity check: $E^+ \ne \emptyset$

Pick any $w \in X$. Its unique $U^-$-walk $w \to r$ exits $X$ at least
once (since $w \in X$, $r \notin X$). The first exiting arc is in
$E^+$. So $|E^+| \ge 1$. Good — the conjecture is at least non-vacuous
in the existential clause.

---

## §2 — The naive "subtree inclusion" fails (concrete example)

`team/30_*` §3.5 Step 1 already identified the failure of the naive
claim "$X_b^{U^-} \subseteq X$ for any $b \in E^+$". The audit-cleared
text on lines 397–399 of `team/30_*` reads:

> "**Conclusion of Step 1's analysis.** $X_b^- \subseteq X_t$ does
> *not* hold in general for arbitrary swap-arc $b \in T_j^- \cap
> \delta^+(X_t)$. The naive sub-tree inclusion is wrong."

Concrete illustration on $n = 4$ ($|V^\bullet| = 4$):

- $V^\bullet = \{r, u, v_1, w\}$.
- $T^- := \{(v_1, u), (u, r), (w, r)\}$: $v_1 \to u \to r$ and
  $w \to r$. So $\pi^{T^-}(v_1) = u$, $\pi^{T^-}(u) = r$,
  $\pi^{T^-}(w) = r$. In-tree, $r$ is the root.
- $U^- := \{(u, v_1), (v_1, r), (w, v_1)\}$: $u \to v_1 \to r$ and
  $w \to v_1$. So $\pi^{U^-}(u) = v_1$, $\pi^{U^-}(v_1) = r$,
  $\pi^{U^-}(w) = v_1$. In-tree, $r$ is the root.

Arc-disjointness: $T^- = \{(v_1, u), (u, r), (w, r)\}$ and
$U^- = \{(u, v_1), (v_1, r), (w, v_1)\}$ share no arc. ✓.

Take $a := (u, r) \in T^-$. Then $X = X_a^{T^-} = \{u, v_1\}$ (the
$T^-$-descendants of $u$, namely $u$ and $v_1$).

Compute $E^+ = U^- \cap \delta^+(\{u, v_1\})$:
- $(u, v_1)$: tail $u \in X$, head $v_1 \in X$. Internal, not in $E^+$.
- $(v_1, r)$: tail $v_1 \in X$, head $r \notin X$. In $E^+$.
- $(w, v_1)$: tail $w \notin X$, head $v_1 \in X$. In $E^-$, not $E^+$.

So $E^+ = \{(v_1, r)\}$, a single arc. Call it $b$.

Compute $X_b^{U^-}$ = $U^-$-subtree at $v_1$:
- $v_1$ is in the subtree.
- $U^-$-children of $v_1$: arcs $(?, v_1)$ in $U^-$. We have
  $(u, v_1)$ and $(w, v_1)$. So $u, w$ are $U^-$-children of $v_1$.
- $U^-$-children of $u$: arcs $(?, u)$ in $U^-$. None. So $u$ is a leaf.
- $U^-$-children of $w$: arcs $(?, w)$ in $U^-$. None. So $w$ is a leaf.

Hence $X_b^{U^-} = \{v_1, u, w\}$. Intersect with $X = \{u, v_1\}$:
$X_b^{U^-} \cap X = \{u, v_1\} = X$. **Not strict.**

Since $E^+ = \{b\}$ has only this arc, Conjecture L fails on this
pair $(T^-, U^-)$.

### §2.1 Caveat: this $D^\bullet$ is *not* 3-arc-strong

The underlying digraph $D^\bullet$ would need to contain at least
$T^- \cup U^- = \{(v_1, u), (u, r), (w, r), (u, v_1), (v_1, r),
(w, v_1)\}$, six arcs on four vertices. To make it 3-arc-strong, we
must add arcs. But the failure of Conjecture L for this *pair* is
already secured: adding arcs to $D^\bullet$ does not change the
in-branchings $T^-, U^-$ as subdigraphs, does not change their
subtree structure, does not change $X_a^{T^-}$ or $X_b^{U^-}$.

So §2 establishes:

> **Observation.** Conjecture L can fail for an *arbitrary* arc-
> disjoint pair $(T^-, U^-)$ of in-branchings, including pairs lying
> inside a 3-arc-strong host $D^\bullet$.

This is the Specialist's earlier "naive subtree-inclusion fails"
remark, made precise.

### §2.2 What's left to attack

The conjecture has the form "$\forall (T^-, U^-)$ arc-disjoint,
$\exists b$ with strict inclusion". §2 refutes the $\forall$ reading.
Two rescue options remain:

- **Attack 1.** Strengthen the hypothesis to "*for an appropriate
  choice of pair* $(T^-, U^-)$, Conjecture L holds." I.e., among all
  valid arc-disjoint pairs, some pair has the property for *every*
  $a \in T^-$.
- **Attack 2.** Replace the conjecture by a swap-based statement: an
  arbitrary pair can be modified (arc-swap) to satisfy Conjecture L
  at the specific $a$ in question, preserving arc-disjointness and
  the in-branching property.

§§3, 4 attempt each. §5 searches for a stronger structural
counterexample (defeating Attack 1).

---

## §3 — Attack 1: constructive choice of pair

### §3.1 The candidate potential

Let $\mathcal P$ denote the set of arc-disjoint pairs $(T^-, U^-)$
of spanning in-branchings of $D^\bullet$ rooted at $r$. By the
Edmonds-form audit-quoted Theorem 2.5 (verbatim, audit A.5 Source 2,
applied to the reverse of $D^\bullet$ with $k = 2$ on the 3-arc-strong
$D^\bullet$), $\mathcal P \ne \emptyset$.

**Defect.** For a pair $(T^-, U^-) \in \mathcal P$ define
$$\Delta(T^-, U^-) := \#\{a \in T^- \,:\, \forall b \in E^+_a,\,
X_a^{T^-} \subseteq X_b^{U^-}\}.$$
This counts the arcs $a \in T^-$ at which Conjecture L fails. The
conjecture holds globally for $(T^-, U^-)$ iff $\Delta = 0$.

### §3.2 What an exchange should look like

For Attack 1 to succeed by lex-minimization, we need: given any
$(T^-, U^-) \in \mathcal P$ with $\Delta(T^-, U^-) > 0$, exhibit an
arc-swap $(T^-, U^-) \to (\tilde T^-, \tilde U^-) \in \mathcal P$
with $\Delta(\tilde T^-, \tilde U^-) < \Delta(T^-, U^-)$, or with
$\Delta$ unchanged but some refining sub-potential strictly decreased.

A standard exchange: pick $a$ violating, $E^+_a$ has all its arcs $b$
with $X \subseteq X_b^{U^-}$. We want to swap an arc out of $U^-$ and
into $U^-$ to break the inclusion at $a$. Candidates: replace some
$b \in E^+_a$ by an arc $b'$ in $\delta^+(X)$ that's currently in
neither $T^-$ nor $U^-$, or that's in $T^-$ (with compensating swap
in $T^-$ to maintain arc-disjointness).

But here is the **structural obstruction** revealed by §2's example:
when $|E^+_a| = 1$, swapping the single exit arc only relocates the
exit; the new exit may again have $X \subseteq X_{b'}^{U^-}$ because
$X$'s in-tree-structure in $U^-$ has a unique "funnel" vertex.

**The funnel structure** is the obstruction. In §2's example,
$v_1 \in X$ is a $U^-$-ancestor of every vertex of $X$ (in fact, $v_1$
is the $U^-$-ancestor of all of $V^\bullet \setminus \{r\}$). No
choice of $b \in E^+_a$ can avoid passing through this funnel, because
*any* exit from $X$ in $U^-$ must go through the unique $U^-$-path of
the deepest vertex.

### §3.3 The funnel failure mode

Suppose Conjecture L fails at $a$: every $b \in E^+_a$ has $X
\subseteq X_b^{U^-}$. Write $E^+_a = \{b_1, \ldots, b_k\}$, $b_i =
(u_i', y_i')$, $u_i' \in X$, $y_i' \notin X$.

By in-branching nesting (two $U^-$-subtrees that share the non-empty
set $X$ must be nested), the $k$ subtrees form a chain. WLOG order
$X_{b_1}^{U^-} \supseteq \cdots \supseteq X_{b_k}^{U^-} \supseteq X$.

In particular, the tails $u_1', \ldots, u_k'$ lie on a single
$U^-$-walk: the walk from $u_k'$ to $r$ passes through all
$u_j'$'s in reverse order. Between successive $u_j', u_{j+1}'$ the
$U^-$-walk exits $X$ via $b_{j+1}$ and re-enters via some arc in
$E^- := U^- \cap \delta^-(X)$. So $|E^-| \ge k - 1$.

**Funnel structure.** All of $X$ are $U^-$-descendants of $u_k'$
(since $X \subseteq X_{b_k}^{U^-}$). The $U^-$-walk from $u_k'$ goes
$u_k' \to y_k' \to \cdots \to u_{k-1}' \to y_{k-1}' \to \cdots \to
u_1' \to y_1' \to \cdots \to r$, alternately exiting and re-entering
$X$.

This is the obstruction to break.

### §3.4 Lex-min attempt

Take a $(T^-, U^-) \in \mathcal P$ minimizing $\Delta$. If $\Delta = 0$
the conjecture holds. Else, suppose $\Delta > 0$ and try to exhibit a
swap to a pair with smaller $\Delta$.

Pick $a \in T^-$ at which the funnel failure holds. Use 3-arc-
strongness *at the cut $X$*: $|\delta^+(X)| \ge 3$. Of these:
- at most 1 is in $T^-$ (the arc $a$);
- $|E^+_a| = k \ge 1$ are in $U^-$;
- the remaining $\ge 3 - 1 - k$ are *free* (not in $T^- \cup U^-$).

**Sub-case (i): $|E^+_a| = 1$.** Free reservoir at $\delta^+(X)$:
$\ge 1$ arc. Let $\beta^* = (w^*, y^*)$ be a free arc, $w^* \in X$,
$y^* \notin X$.

Attempt: in $U^-$, remove $w^*$'s current $U^-$-out-arc
$\beta(w^*)$, add $\beta^*$. Result: $U^{-\prime} = U^- -
\beta(w^*) + \beta^*$.

For $U^{-\prime}$ to be an in-branching, we need $y^* \notin
X_{\beta(w^*)}^{U^-}$ (else cycle $w^* \to y^* \to \cdots \to w^*$).
The subtree $X_{\beta(w^*)}^{U^-}$ is *not* contained in $X$ in
general (§2's failure mode is exactly that subtrees of $X$-vertices
extend outside $X$ via re-entry arcs in $E^-$). So $y^* \notin X$
does **not** imply $y^* \notin X_{\beta(w^*)}^{U^-}$.

In the funnel scenario, $X_{\beta(w^*)}^{U^-}$ for $w^* = u_1'$ (the
"largest" tail in the chain) contains a substantial outside-$X$
portion of $V^\bullet$. The single free arc's target $y^*$ may well
lie in this portion. Then the swap creates a cycle and is forbidden.

With $|E^+_a| = 1$ and only one free arc, there's no slack to retry.
**Sub-case (i) stalls.**

**Sub-case (ii): $|E^+_a| \ge 2$.** Free reservoir: $\ge 3 - 1 - k$,
which is $0$ when $k = 2$ and $|\delta^+(X)| = 3$ exactly. **No free
arc to swap in.**

Alternatives: swap two $U^-$ arcs simultaneously (replacing internal
$U^-$ structure inside $X$). This requires a careful global
re-routing argument that I have not closed.

### §3.5 Summary of Attack 1

The lex-min strategy stalls in the tight regime where $D^\bullet$ is
*exactly* 3-arc-strong and the cut $X$ has $|\delta^+(X)| = 3$. The
free reservoir is empty when $|E^+_a| \ge 2$; non-empty but with no
"safe target" when $|E^+_a| = 1$. **Verdict: Attack 1 inconclusive in
one session.**

---

## §4 — Attack 2: arc-swap repair

§3 already touched arc-swap mechanics. §4 reframes: given any
$(T^-, U^-)$ with Conjecture L failing at $a$, find a *local* swap
that fixes the failure at $a$ while preserving arc-disjointness, the
in-branching property of both, and not introducing new failures
elsewhere.

### §4.1 The desired swap

Failure mode (§3.3): all $b \in E^+_a$ have $X \subseteq X_b^{U^-}$.
We want to *modify $U^-$* so that some new $b' \in E^+_a$ has
$X_{b'}^{U^-} \cap X \subsetneq X$.

Equivalently, in the modified $U^{-\prime}$, the $U^{-\prime}$-tree
restricted to $X$ must have **some** $X$-vertex whose $U^{-\prime}$-
walk reaches $r$ *without* passing through the "common ancestor"
$u_{i_k}'$ (the deepest funnel vertex).

That requires re-routing some $X$-vertex $w$ to exit $X$ via a path
that bypasses $u_{i_k}'$ and all $u_{i_j}'$'s.

A concrete swap: pick $w \in X$ with $\pi^{U^-}(w) \in X$ (i.e., $w$
is currently routed via internal $U^-$ arcs). Replace $w$'s $U^-$-
parent-arc with a direct exit arc $(w, y')$, $y' \notin X$. Provided
the new exit arc is available (not in $T^-$, not in $U^-$ already)
and the swap creates no cycle.

### §4.2 The structural obstacle

The arc $(w, y')$ must exist in $D^\bullet$ (as a multigraph arc),
not be in $T^- \cup U^-$, and creating $\tilde U^- := U^- -
\pi^{U^-}\text{-arc of }w + (w, y')$ must remain an in-branching.

For $\tilde U^-$ to be an in-branching, we need $y' \notin$ the
$U^-$-subtree at $w$ (else cycle). The $U^-$-subtree at $w$ may
contain $V \setminus X$ vertices (via re-enter arcs), so the
constraint "$y' \notin X$" alone is *not* enough.

If the failure mode is the funnel of §3.3, the $U^-$-subtree at $w$
(for $w \in X$ with $\pi^{U^-}(w) \in X$) may contain a substantial
portion of $V \setminus X$. The "safe targets" $y'$ are
$V \setminus X \setminus \text{this subtree}$.

For the swap to exist:
- 3-arc-strongness gives $d^+_{D^\bullet}(w) \ge 3$. Out-arcs of $w$
  in $D^\bullet$ go to up to 3 distinct heads. Two are used (the
  $T^-$- and $U^-$-out-arcs of $w$). The remaining $\ge 1$ out-arc(s)
  may go anywhere — perhaps into $X$, perhaps into the wrong region
  of $V \setminus X$.

There is no margin for guaranteeing a $w$ and a target $y'$ exist.
The 3-arc-strongness budget is consumed exactly by "$T^-$, $U^-$,
the swap" without surplus to route around the funnel.

### §4.3 Multi-arc swap

A more ambitious swap: change *two* arcs of $U^-$ simultaneously.
E.g., swap arc $b_{i_k}$ out of $U^-$ and a different exit arc
$b' = (w, y')$ in (with $y' \notin X$). To maintain
$|U^-| = |V^\bullet| - 1$, the count is preserved.

Constraints:
- $b' \notin T^-$ (arc-disjointness preserved with $T^-$).
- $b'$ exists in $D^\bullet$. If $b'$ is currently a free arc, great.
  But in the tight case $|\delta^+(X)| = 3$, $|E^+_a| = 1$,
  $|T^- \cap \delta^+(X)| = 1$, free = $3 - 1 - 1 = 1$: a single free
  arc, the *only* candidate $b'$.
- $U^{-\prime} := U^- - b_{i_k} + b'$ is an in-branching.

For $U^{-\prime}$ to be an in-branching: removing $b_{i_k}$ from $U^-$
splits $U^-$ into two components: $U^-$-subtree at $u_{i_k}'$ (= 
$X_{b_{i_k}}^{U^-}$, includes $X$) and the rest. Adding $(w, y')$:
- If $w \in X_{b_{i_k}}^{U^-}$ and $y' \notin X_{b_{i_k}}^{U^-}$: this
  reconnects the two components, restoring a single tree. ✓.
- If $w, y' \in X_{b_{i_k}}^{U^-}$: creates a cycle. ✗.
- If $w \notin X_{b_{i_k}}^{U^-}$: $w$ already in the "rest"
  component; adding $(w, y')$ creates either a cycle (if $y' \in $
  "rest") or another disconnection (if $y' \in X_{b_{i_k}}^{U^-}$,
  re-routing in wrong direction).

So the safe case is $w \in X_{b_{i_k}}^{U^-}$, $y' \notin
X_{b_{i_k}}^{U^-}$. The single free arc $b'$ has $w \in X$ (since
$\delta^+(X) \ni b'$ means tail of $b'$ in $X$) — and $X \subseteq
X_{b_{i_k}}^{U^-}$, so $w \in X_{b_{i_k}}^{U^-}$. ✓ for the tail.

Head $y' \notin X$ by definition of $\delta^+(X)$. Need $y' \notin
X_{b_{i_k}}^{U^-}$. **This is the non-trivial constraint.**

If the funnel scenario has all of $V^\bullet \setminus \{r\} \subseteq
X_{b_{i_k}}^{U^-}$ — i.e., $u_{i_k}'$'s $U^-$-subtree is everything
except $r$ — then **every** target $y' \ne r$ is in
$X_{b_{i_k}}^{U^-}$. The only safe target is $y' = r$. So we need the
free arc to have head $r$.

Does such a free arc exist? It depends on $D^\bullet$.

### §4.4 Concrete construction in §2's example

Recall §2: $V^\bullet = \{r, u, v_1, w\}$, $X = \{u, v_1\}$, $E^+_a
= \{(v_1, r)\}$. The $U^-$-subtree at $v_1$ is $\{v_1, u, w\}$, which
is $V^\bullet \setminus \{r\}$ — everything except $r$.

So for any swap to safely re-route an $X$-vertex, the target must be
$r$. The free arc $(w', r)$ with $w' \in X$ would work. In our pair
$T^-, U^-$, the arc $(u, r) \in T^-$. Is the arc $(v_1, r)$ in $U^-$?
Yes. So if there were a *third* arc from $X$ to $r$, it could be
free. With only the arcs listed, there's no free arc; the digraph is
not 3-arc-strong.

If we extend $D^\bullet$ to be 3-arc-strong by adding, say, a multi-
arc $(u, r)_2$ (a second copy of $u \to r$): now $\delta^+(X)$
contains $(u, r), (u, r)_2, (v_1, r)$, three arcs. One in $T^-$
($(u, r)$), one in $U^-$ ($(v_1, r)$), one free ($(u, r)_2$). Now do
the swap: $U^{-\prime} := U^- - (v_1, r) + (u, r)_2$. Check
in-branching: removing $(v_1, r)$ from $U^-$ disconnects $\{v_1, u,
w\}$ from $r$. Adding $(u, r)_2$ reconnects via $u$. Resulting tree:
$v_1 \to ?$ wait, $v_1$'s parent in original $U^-$ was $r$; removing
that arc, $v_1$ has no parent. The new arc $(u, r)_2$ gives $u$ a
parent $r$. But $v_1$ still needs a parent in $U^{-\prime}$. Hmm,
that's not how the swap works.

Re-examine. $U^-$ has $|V^\bullet| - 1 = 3$ arcs (for $|V^\bullet| =
4$): $(u, v_1), (v_1, r), (w, v_1)$. We swap one arc out and one
arc in, maintaining 3 arcs.

If we swap $(v_1, r)$ out and add a free arc $(u, r)_2$: new $U^{-
\prime} = \{(u, v_1), (u, r)_2, (w, v_1)\}$. Check it's an
in-branching at $r$:
- $u$'s out-arc: $(u, r)_2$ in $U^{-\prime}$, but also $(u, v_1) \in
  U^{-\prime}$. Two out-arcs of $u$! **Not an in-branching** (in-tree
  requires out-degree exactly 1 for non-root vertices).

So this swap doesn't preserve in-branching property. The issue: $u$
now has two out-arcs $(u, v_1)$ and $(u, r)_2$ in $U^{-\prime}$.

Fix: also remove $(u, v_1)$, so $U^{-\prime} = \{(u, r)_2, (v_1, r),
(w, v_1)\}$. But we also added $(u, r)_2$ and removed only $(v_1, r)$
in the first swap. Actually $\{(u, r)_2, (v_1, r), (w, v_1)\}$ —
keeping $(v_1, r)$ and the new $(u, r)_2$, removing $(u, v_1)$.

Now check: $u$ has out-arc $(u, r)_2$, single. $v_1$ has out-arc
$(v_1, r)$, single. $w$ has out-arc $(w, v_1)$, single. $r$ has no
out-arc, ✓. Total 3 arcs. Acyclic? $w \to v_1 \to r$ and $u \to r$.
Two disjoint $\to r$ paths. ✓. In-branching at $r$. ✓.

Now recheck Conjecture L on the new pair $(T^-, U^{-\prime})$. Same
$a = (u, r) \in T^-$, same $X = \{u, v_1\}$. $E^+_a = U^{-\prime}
\cap \delta^+(X)$:
- $(u, r)_2$: tail $u \in X$, head $r \notin X$. In $E^+$.
- $(v_1, r)$: tail $v_1 \in X$, head $r \notin X$. In $E^+$.
- $(w, v_1)$: tail $w \notin X$, head $v_1 \in X$. Not in $E^+$.

So $E^+_a = \{(u, r)_2, (v_1, r)\}$, two arcs.

$X_{(u, r)_2}^{U^{-\prime}}$ = $U^{-\prime}$-subtree at $u$ = $\{u\}$
($u$ has no $U^{-\prime}$-children, since no arc has head $u$ in
$U^{-\prime}$). Intersect with $X = \{u, v_1\}$: $\{u\} \subsetneq X$.
**Strict.** ✓.

So Conjecture L is repaired by this 2-arc swap (remove $(u, v_1)$,
add $(u, r)_2$). The pair $(T^-, U^{-\prime})$ satisfies the
conjecture at $a$.

### §4.5 When does this swap exist?

The swap of §4.4 requires the free arc $(u, r)_2$ to exist in
$D^\bullet$. Generally, we need an arc from some $w \in X$ directly
to a "safe" target outside the $U^-$-subtree-funnel.

In a 3-arc-strong $D^\bullet$, the count at the cut $\delta^+(X)$ is
$\ge 3$. Distribution: at most 1 in $T^-$, $|E^+_a| \ge 1$ in $U^-$,
free $\ge 3 - 1 - |E^+_a|$. For $|E^+_a| = 1$: free $\ge 1$. For
$|E^+_a| = 2$: free $\ge 0$ (possibly empty).

Moreover, the free arc's head may not be a "safe" target — i.e., it
may be inside some $U^-$-subtree, creating cycles.

So Attack 2 succeeds when:
- $|E^+_a| = 1$ and the free arc in $\delta^+(X)$ has head outside
  the relevant $U^-$-subtree.
- $|E^+_a| \ge 2$ and… here we may have *no* free arc, and the
  multi-arc swap inside $U^-$ to break the funnel is more subtle.

**Verdict on Attack 2:** repair *succeeds* in some sub-cases (§4.4
exhibits one), but the general case — particularly when
$|E^+_a| \ge 2$ and $|\delta^+(X) \cap \text{Free}| = 0$ — is *not*
resolved in this session. A multi-arc swap involving rearrangement of
$U^-$ inside $X$ would be needed, and the case analysis grows.

---

## §5 — Attack 3: counterexample search

§§3, 4 stall at the "tight" regime where 3-arc-strongness gives no
free arc in $\delta^+(X)$ and the funnel structure is rigid. §5 asks:
can such a tight configuration actually arise, or is it excluded by
the global 3-arc-strong hypothesis?

### §5.1 What we need for a *global* counterexample

A genuine counterexample to Conjecture L (refuting Attack 1) requires:

- $D^\bullet$ 3-arc-strong directed multigraph.
- An arc-disjoint pair $(T^-, U^-)$ of spanning in-branchings of
  $D^\bullet$ rooted at $r$.
- A specific $a \in T^-$ at which the funnel failure holds.
- **No other pair** $(T^{-\prime}, U^{-\prime}) \in \mathcal P$ (the
  space of arc-disjoint in-branching pairs) has the failure repaired
  at $a$ (for Attack 1 refutation), **OR** no repair swap exists
  (Attack 2 refutation).

The space $\mathcal P$ is potentially large, so global Attack 1
refutation needs a careful argument. But even a *local* counterexample
to "the natural swap repairs the failure" is suggestive.

### §5.2 Smallest candidates

Try $|V^\bullet| = 5$, 3-arc-strong directed multigraph. The minimum
number of arcs: $\sum_v d^+(v) = \sum_v d^-(v) \ge 3|V^\bullet| = 15$
arcs (each vertex has in- and out-degree $\ge 3$, but in a multigraph
the degree counts can be at the minimum 3-edge-connected lower
bound). For comparison, a 3-arc-strong simple digraph on 5 vertices
has at least 15 arcs.

Construct $D^\bullet$ as follows:
- $V^\bullet = \{r, u_1, u_2, v_1, v_2\}$.
- Arcs (simple, no multi-edges): $r \to u_1, u_1 \to u_2, u_2 \to
  v_1, v_1 \to v_2, v_2 \to r$ (a 5-cycle), plus $r \to u_2, u_2 \to
  v_2, v_2 \to u_1, u_1 \to v_1, v_1 \to r$, plus more to reach 3-arc-
  strong.

This is tedious; let me instead **focus on the structural question**:
*can the funnel structure §3.3 occur on a 3-arc-strong $D^\bullet$
with $|E^+_a| = 1$ and zero free arcs in $\delta^+(X)$?*

For the funnel with $|E^+_a| = 1$: $|\delta^+(X)| \ge 3$, $T^- \cap
\delta^+(X) = \{a\}$ (1 arc), $U^- \cap \delta^+(X) = \{b\}$ (1 arc),
so free $\ge 1$. So in 3-arc-strong, the free reservoir is non-empty
when $|E^+_a| = 1$. Attack 2's swap of $\beta(w^*)$ for a free arc has
*at least one candidate*; the question is whether the candidate's
head is safe.

### §5.3 Local search on $n = 4$

Re-examine §2's example $V^\bullet = \{r, u, v_1, w\}$, $X = \{u,
v_1\}$. In §4.4 I extended this to a 3-arc-strong host by adding a
multi-arc $(u, r)_2$, and the swap succeeded.

What if the host $D^\bullet$ has a *different* extra arc — one that
*doesn't* allow the swap? The third arc in $\delta^+(X)$ could be
$(v_1, r)_2$ (multi-edge): then free arc is $(v_1, r)_2$. Swap
$(v_1, r) \in U^-$ for $(v_1, r)_2$? But these are parallel arcs,
"same" in graph-theoretic effect; the swap renames the arc but
doesn't change the subtree structure. Conjecture L still fails.

Alternative extra arc: $(u, w)$ — but $w \notin X$? Wait, $w \notin X
= \{u, v_1\}$, so $(u, w)$ has tail in $X$, head outside $X$, so in
$\delta^+(X)$. ✓. This is a third arc in $\delta^+(X)$, free
(assuming not in $T^- \cup U^-$).

Try swap: $\tilde U^- := U^- - (v_1, r) + (u, w)$? But removing
$(v_1, r)$ disconnects $\{v_1, u, w\}$ from $r$, and adding $(u, w)$
re-routes $u \to w$ — but $w \in V^\bullet \setminus \{r\}$, so $w$
also needs to reach $r$. Currently $w$'s out-arc in $U^-$ is
$(w, v_1)$. So $u \to w \to v_1 \to ?$ but $v_1$'s out-arc was
$(v_1, r)$, just removed. So $v_1$ has no parent in $\tilde U^-$.
Not an in-branching.

Need a two-arc swap. Remove $(v_1, r)$ and $(w, v_1)$ from $U^-$, add
$(u, w)$ and… need an arc giving $v_1$ a parent and one giving $w$ a
parent. With only one new arc $(u, w)$, this fails.

So this extra arc doesn't help.

Try a different extra: $(v_1, u)$? Wait, $v_1 \in X$, $u \in X$:
internal arc, not in $\delta^+(X)$. Doesn't help cut count.

**For 3-arc-strongness with the given $T^-, U^-$, we need
$|\delta^+(X)| \ge 3$.** The two existing exit arcs are $(u, r) \in
T^-$ and $(v_1, r) \in U^-$. A third arc in $\delta^+(X)$ has tail in
$\{u, v_1\}$, head in $\{r, w\}$. Options:
- $(u, r)_2$: §4.4 — swap succeeds.
- $(v_1, r)_2$: §5.3 above — parallel to $U^-$ arc, swap trivial /
  ineffective.
- $(u, w)$: §5.3 above — swap fails for in-branching reasons.
- $(v_1, w)$: tail $v_1 \in X$, head $w \notin X$. Similar to
  $(u, w)$ case: swap into $U^-$ requires removing some other arc,
  details below.

Try $(v_1, w) \in D^\bullet$ as free arc. Multi-arc swap: replace
$(w, v_1)$ in $U^-$ by $(v_1, w)$? But $(w, v_1) \in U^-$ goes $w \to
v_1$; $(v_1, w)$ goes $v_1 \to w$ — opposite direction. After swap,
$w$ has no in-tree out-arc (was $(w, v_1)$, now gone). So $w$ needs
new out-arc. $v_1$ now has two out-arcs $(v_1, r)$ and $(v_1, w)$.
Not an in-branching.

Multi-arc swap: remove $(v_1, r)$ and $(w, v_1)$ from $U^-$, add
$(v_1, w)$ and… need 1 more arc to keep arc count at 3. Adding an
arc, say $(w, r)$? But $(w, r) \in T^-$! Arc-disjointness fails.

So the only arc available is $(v_1, w)$, and we can't make a
2-for-1 swap.

Try free arc $(u, r)_2$ + restructuring: in §4.4 we did a swap that
removed $(u, v_1)$ and added $(u, r)_2$. That broke the funnel
because $u$'s subtree shrank from $\{u\}$ (since $u$ had no
$U^-$-children) to $\{u\}$ (still no children). Wait, $u$'s subtree
was already $\{u\}$ in original $U^-$, but the exit arc was $b = (v_1,
r)$, and the *failure* was due to $v_1$'s subtree containing all of
$X$. After the swap, $E^+_a$ has 2 arcs, and the new arc $(u, r)_2$
has subtree $\{u\} \subsetneq X$. ✓.

So the swap succeeds **when the free arc is parallel to $a$** (i.e.,
$(u, r)_2$ parallel to $a = (u, r)$). But this is a very specific
combinatorial accident — it requires a multi-arc in $D^\bullet$.

**Does 3-arc-strongness force this kind of parallelism?** No: a simple
digraph on $\ge 5$ vertices can be 3-arc-strong without multi-arcs.

So a counterexample candidate: build a *simple* 3-arc-strong $D^\bullet$
on $n \ge 5$ vertices where the funnel scenario arises and no repair
swap exists. I have not constructed one in this session, but the
structural analysis above suggests it is *plausible*.

### §5.4 Honest assessment

A fully convincing counterexample would require:
- Building a specific simple 3-arc-strong $D^\bullet$.
- Specifying $(T^-, U^-)$ exhibiting the funnel.
- Enumerating *all* valid arc-disjoint in-branching pairs of
  $D^\bullet$ (potentially many) and verifying none satisfy
  Conjecture L at the specific $a$.

This enumeration is computational and exceeds one-session budget.
The Coder's 11 869-instance empirical SAD work (`team/28_*`) is
*not* the same test — those test SAD existence (the higher-level
theorem), not the structural Conjecture L on in-branching pairs.

I have *not* found a counterexample. I have also *not* found a proof.
The §3.3 funnel structure remains a viable failure mode in 3-arc-
strong $D^\bullet$, but I have not exhibited a global counterexample
where no choice of pair / no swap repairs it.

---

## §6 — Verdict

**FAILED.** One session, no proof, no counterexample, no clean
partial progress.

What this session contributed:
- **§1** — Conjecture L is now stated verbatim with notation pinned
  down; the existential $E^+ \ne \emptyset$ is verified.
- **§2** — The naive "$X_b^{U^-} \subseteq X$" claim is refuted by
  an explicit $n = 4$ pair. Conjecture L itself can fail for a *given*
  pair: there are pairs $(T^-, U^-)$ where every $b \in E^+_a$ has
  $X \subseteq X_b^{U^-}$ (the "funnel" failure mode).
- **§3** — Attack 1 (lex-min over arc-disjoint pairs) identifies the
  structural obstacle: in 3-arc-strong $D^\bullet$ with $|\delta^+
  (X)| = 3$ (tight), $|E^+_a| = 2$, no free arc is available in
  $\delta^+(X)$, and no single-arc swap is obvious. Attack 1 stalls.
- **§4** — Attack 2 (arc-swap repair) succeeds in the specific
  $|E^+_a| = 1$ + "free arc parallel to $a$" subcase (§4.4), but the
  general repair lemma is not proved. Attack 2 stalls.
- **§5** — Attack 3 (counterexample search) does not exhibit a
  refuting digraph in the session budget. The §3.3 funnel structure
  is plausible but its persistence under all valid pairs / swaps is
  not verified.

**Recommendation.** The team should adopt **option (B)** from the
team-wide decision: combined paper draft with Conjecture L as a stated
open problem (named "subtree-exchange property for two arc-disjoint
in-branchings sharing a root"). The fallback **(F3) 4-arc-strong**
(`team/30_*` §7.4 line 723) gives an unconditional close for the
R3⋆-HC by widening the hypothesis from 3-arc-strong to 4-arc-strong;
this should be presented as the headline theorem, with the 3-arc-strong
case stated conditional on Conjecture L.

**Disciplinary note.** The Specialist's track record on the broader
"Conjecture L is a known classical result" claim now reads:

- `team/30_*` §7.6 hedged on Schrijver §53.6 ("possibly a corollary…
  but the content is paywalled and I have not verified") — **correct
  hedging**.
- Audit Appendix A.12 confirmed Schrijver §53.6 is *fundamentally
  different* (root-set exchange in branchings partitioning $A$, not
  subtree-inclusion in two spanning in-arborescences with common
  root).
- This session attempted from-scratch proof: **failed honestly**.
  Two natural attacks (lex-min, arc-swap) hit the same structural
  obstacle (tight 3-arc-strong cuts forbid free repair arcs); a
  counterexample candidate (§3.3 funnel) is plausible but not
  globally instantiated.

No further "by Frank / BJG Theorem X.Y.Z" temptations occurred; the
audit-cleared Theorem 2.5 of BJG–Yeo 2020 and the audit-cleared
within-kind submodularity (`team/27_*` lines 197–207) were the only
external invocations.

### §6.1 Concrete next-step suggestion for the team

If a future session wishes to push further, two computationally
tractable sub-problems:

1. **Counterexample search (Coder).** Enumerate simple 3-arc-strong
   $D^\bullet$ on $n = 5, 6, 7$. For each, enumerate arc-disjoint
   in-branching pairs $(T^-, U^-)$. Check whether *any* $a \in T^-$
   has the funnel failure with no repair swap available across *any*
   choice of $(T^{-\prime}, U^{-\prime}) \in \mathcal P$. Even
   verifying Conjecture L on a large set of small instances would be
   strong evidence (no counterexample found at $n \le 7$ would
   support Attack 1's plausibility).
2. **The 4-arc-strong margin (F3).** Verify cleanly that 4-arc-strong
   $D^\bullet$ admits two arc-disjoint pairs of in-branchings
   *coupled* with the two out-branching pairs s.t. cross-color
   sharing is empty (this is `team/30_*` §7.4's "(F3)"). With cross-
   color sharing empty, the RECOLOR algorithm of `team/29_*` is
   vacuous, and Conjecture L is not needed. This gives the
   unconditional 4-arc-strong R3⋆-HC headline.

The (1)-counterexample-or-evidence path is high-information; the
(2)-fallback path is the safe unconditional close. Recommend both.

---

End of file.
