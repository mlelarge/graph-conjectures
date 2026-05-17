# 32 — Verification attempt of (F3): cross-kind disjointness at $\lambda(D^\bullet) \ge 4$

Author: Structural Digraph Specialist
Date: 2026-05-17
Status: **Honest negative report.** Tasked with verifying the
4-arc-strong fallback (F3) of `team/30_route_c1_termination.md` §7.4
via "two cascading applications of Edmonds + submodularity," I have
found that the cascading argument **does not close** under the audit's
hard-rule "no matroid union, no Frank, no Schrijver." The
combinatorial inequality the cascade requires — $|T \cap \delta^-(X)|
\le 1$ for every out-branching $T$ rooted at $r$ and every non-empty
$X \subseteq V \setminus \{r\}$ — **is false in general**.

More serious: this is the same inequality on which the audit-cleared
**within-kind** submodularity step of `team/27_*` lines 197–207 (and
its restatement at `team/29_*` §1.2 lines 86–98) rests. On re-
examination, the within-kind step has the same gap; the auditor's
clearance at `team/05_audit.md` §A.10.6 line 2696 was over-generous.

The cross-kind statement (F3) is in fact **mathematically true** — it
is a textbook consequence of the Edmonds–Schrijver matroid-union
theorem (Frank, *Connections in Combinatorial Optimization*, 2011
§10.1; Schrijver Vol. B §53.6). But under the audit's hard-rule we
cannot cite that. The cascading argument the task requests cannot
substitute.

This file documents the honest verification attempt and recommends
two recovery paths.

Prior references: `team/05_audit.md` Appendix A.5 Source 2 (BJG–Yeo
2020 Theorem 2.5 — the only packing theorem permitted) and §A.10
(matroid-union audit, recommendation 4 is exactly (F3)); `team/27_*`
§3.1 lines 197–207 (within-kind submodularity template); `team/29_*`
§1.2 (verbatim restatement); `team/30_*` §7.4 (where (F3) was listed
as the safe fallback); `team/31_*` (abandoned Conjecture L attempt).

---

## §1 — Setup

### §1.1 Hypothesis and claim

Let $D = (V, A)$ be a simple **4-arc-strong** $(1, 0)$-near-split
digraph: $\lambda^{\text{arc}}(D) \ge 4$, split partition $V = V_1
\dot\cup V_2$, $|V_1| \ge 2$, $|V_2| \ge 3$, unique $V_1$-internal arc
$e_0 = (p, q)$. By the cut-lifting argument of `team/21_*` §3.1 (which
goes through verbatim for any $\lambda \ge k$, as recapitulated in §5
below), the chord-contraction $D^\bullet$ is a 4-arc-strong directed
multi-graph with contracted root $r := p^\bullet$, $V_1^\bullet$
independent, $V_2^\bullet$ simple semicomplete.

Imported verbatim from `team/22_*` §§2–3 and `team/26_*` §3.1: the
maps $\pi, \pi^{-1}$, the un-contracted color subgraph $D_i^\flat$,
the $P_i, Q_i$ predicates, the four side-label classes
$R_p^+, R_q^+, R_p^-, R_q^-$ at $r$, and (in the $\lambda = 3$ case)
the supply bounds $(\ast)$: $|R_p^+| \ge 2, |R_q^+| \ge 3, |R_p^-|
\ge 3, |R_q^-| \ge 2$. Under $\lambda \ge 4$ these bounds become $\ge
3, \ge 4, \ge 4, \ge 3$ uniformly — the §3.4 16-profile demand is
unchanged so the supply margin only grows.

**(F3) Cross-kind disjointness.** *If $D^\bullet$ is a 4-arc-strong
multi-digraph and $r \in V^\bullet$, then there exist two
out-branchings $T_1^+, T_2^+$ and two in-branchings $T_1^-, T_2^-$
rooted at $r$ such that all four are pairwise arc-disjoint.*
Equivalently, $S_{12} := T_1^+ \cap T_2^- = \emptyset$ and $S_{21} :=
T_2^+ \cap T_1^- = \emptyset$, in the notation of `team/29_*` §1.4.

If (F3) holds, the RECOLOR algorithm of `team/29_*` §3 is vacuous
(the cross-color shared-arc set $S$ is empty) and the §3.5
termination question (Conjecture L of `team/30_*` §7.6) does not
arise.

### §1.2 The only branching theorem permitted

Verbatim from `team/05_audit.md` Appendix A.5 Source 2 (line 946),
reproduced from BJG–Yeo 2020 (arXiv:1903.12225) p. 6:

> **Theorem 2.5** [12] *A directed multigraph $D = (V, A)$ with a
> vertex $z$ has $k$ arc-disjoint out-branchings rooted at $z$ if and
> only if $d^-(X) \ge k$ for all non-empty $X \subseteq V \setminus
> \{z\}$.*

The reverse-digraph form: $D$ has $k$ arc-disjoint **in-branchings**
rooted at $z$ iff $d^+(X) \ge k$ for all non-empty $X \subseteq V
\setminus \{z\}$.

No other branching-packing theorem is available under the audit's
hard rules.

---

## §2 — The cascading-Edmonds template and its gap

### §2.1 The intended argument (as stated in `team/30_*` §7.4)

**Step 1.** $D^\bullet$ is 4-arc-strong, so $d_{D^\bullet}^-(X) \ge 4
\ge 2$ for every non-empty $X \subseteq V^\bullet \setminus \{r\}$.
By Theorem 2.5 with $k = 2$, pick two arc-disjoint out-branchings
$T_1^+, T_2^+$ rooted at $r$.

**Step 2 (the claimed submodularity step).** Set $D^\bullet_1 :=
D^\bullet \setminus (T_1^+ \cup T_2^+)$. For every non-empty $X
\subseteq V^\bullet \setminus \{r\}$:

$$d_{D^\bullet_1}^+(X) \stackrel{?}{\ge} d_{D^\bullet}^+(X) - 2 \ge 4 - 2 = 2. \tag{$\star$}$$

Then apply Theorem 2.5 to the reverse of $D^\bullet_1$ with $k = 2$
to extract two arc-disjoint in-branchings $T_1^-, T_2^-$ in
$D^\bullet_1$. All four are mutually arc-disjoint by construction
($T_i^-$ avoids both $T_1^+$ and $T_2^+$).

**Step 3.** The §3.4 16-profile casework of `team/27_*` is unchanged
because the four root-arcs of $T_1^+, T_2^+, T_1^-, T_2^-$ at $r$
remain four distinct arcs (cross-kind disjointness at $r$ is
automatic by (LR) of `team/29_*` §1.3).

The argument's load-bearing inequality is ($\star$), which is the
"subtract two for two branchings removed" submodularity statement.

### §2.2 Why ($\star$) fails

($\star$) requires, for each non-empty $X \subseteq V^\bullet
\setminus \{r\}$,

$$|T_1^+ \cap \delta^+(X)| + |T_2^+ \cap \delta^+(X)| \le 2,$$

i.e.\ each $|T_i^+ \cap \delta^+(X)| \le 1$.

**Claim.** *In general, for an out-branching $T$ of $H$ rooted at $r$
and non-empty $X \subseteq V(H) \setminus \{r\}$, $|T \cap \delta^+
(X)|$ equals the number of vertices $v \in V(H) \setminus X$ whose
unique $T$-parent lies in $X$. This count can be as large as $|X|$.*

*Proof.* Each $v \ne r$ has exactly one $T$-in-arc (its parent-arc).
The arc $(u, v)$ lies in $\delta^+(X)$ iff $u \in X$ and $v \notin
X$, i.e.\ $v$ is outside $X$ and its $T$-parent $u$ is inside $X$.
Summing over $v \in V(H) \setminus X$ gives the stated count. An
extremal example: $X = \{x\}$ a single vertex with $T$-out-degree
$|V(H)| - 2$ (i.e.\ $x$ is a "star" child of $r$ and parent of
everyone else); then $|T \cap \delta^+(X)| = |V(H)| - 2$, far larger
than 1. $\square$

So Step 2's inequality ($\star$) is **not** a consequence of the
out-branching property and basic cut counting. The "subtract 1 per
branching" recipe is *wrong* in general.

### §2.3 The dual error: $|T \cap \delta^-(X)| \le 1$ also fails

For completeness, consider the within-kind submodularity argument of
`team/27_*` lines 197–207 / `team/29_*` §1.2 lines 86–98, which uses
the (slightly different) inequality

$$|T_i^+ \cap \delta^-(X)| \le 1 \text{ for all non-empty } X \subseteq V \setminus \{r\}. \tag{$\dagger$}$$

By the same argument as §2.2 (with roles of $X$ and $V \setminus X$
exchanged):

$$|T \cap \delta^-(X)| = \#\{\text{connected components of } T[X]\},$$

where $T[X]$ is the sub-forest of $T$ on vertex set $X$. (Each
component of $T[X]$ has a unique "root within $X$" whose $T$-parent
lies outside $X$; that parent-arc is in $\delta^-(X)$.) For $X$ that
is $T$-disconnected — which happens generically once $|X| \ge 2$ —
this count exceeds 1. So ($\dagger$) is also false in general.

**Consequence.** The within-kind submodularity step audit-cleared in
`team/05_audit.md` §A.10.6 line 2696 ("$d^-_{D^\bullet \setminus
T_i^+}(X) \ge d^-_{D^\bullet}(X) - 1 \ge 2$") relies on the same
incorrect inequality. The clearance was based on a passing reading
that treats "branching uses at most one arc of any cut" as a
textbook fact; on careful re-derivation it is not.

### §2.4 What IS true (and how Edmonds-from-the-residual works)

The correct way to get a $(k - 1)$-arc-strong residual after
removing one out-branching is **not** by pointwise cut-counting, but
by the **converse of Edmonds**. If $D$ has $k$ arc-disjoint out-
branchings $T_1, \ldots, T_k$ (which is the case when $\lambda \ge
k$), then $D \setminus T_1 \supseteq T_2 \cup \cdots \cup T_k$ contains
$k - 1$ arc-disjoint out-branchings, so by Theorem 2.5 (necessity),

$$d^-_{D \setminus T_1}(X) \ge k - 1 \text{ for all non-empty } X \subseteq V \setminus \{r\}. \tag{$\ddagger$}$$

($\ddagger$) is genuinely true, but it is **not** a "subtract one per
removal" inequality on a *fixed* $T_1$ — it is a statement about $T_1$
chosen as part of a maximum packing. The proof goes:

> *$D$ has $k$ arc-disjoint out-branchings (Theorem 2.5 hypothesis $d^-
> \ge k$). $D \setminus T_1$ contains $T_2, \ldots, T_k$. Therefore $D
> \setminus T_1$ has $k - 1$ arc-disjoint out-branchings, hence (by
> Theorem 2.5 necessity) $d^-_{D \setminus T_1}(X) \ge k - 1$.*

**Consequence for the within-kind step (`team/27_*` lines 197–207).**
The argument salvages as follows. By Theorem 2.5 at $k = 3$ (using
$\lambda(D^\bullet) \ge 3$), there exist 3 arc-disjoint out-branchings
$T_1^+, T_2^+, T_3^+$. Pick $T_1^+, T_2^+$; the residual $D^\bullet
\setminus T_1^+$ contains $T_2^+, T_3^+$ as 2 arc-disjoint out-
branchings, so $d^-_{D^\bullet \setminus T_1^+}(X) \ge 2$. Now we
want to extract an **in-branching** $T_1^-$ from $D^\bullet \setminus
T_1^+$, which requires $d^+_{\text{residual}}(X) \ge 1$. This is a
**different** quantity from $d^-$, and the converse-of-Edmonds trick
does not give it.

In other words: **the converse-of-Edmonds salvage works for stacking
multiple out-branchings, but not for switching kinds (out → in).**
The within-kind step claimed at `team/27_*` lines 197–207 is actually
within-kind only in the sense of "out branchings stacked with out
branchings"; the *in*-branching $T_i^-$ extracted from the residual
is governed by $d^+_{\text{residual}}$, not $d^-_{\text{residual}}$,
and the converse-of-Edmonds trick does not bound $d^+_{\text
{residual}}$.

This is a serious gap. Let me state it cleanly.

### §2.5 The fundamental obstruction

To pack 2 out-branchings + 2 in-branchings, all pairwise arc-disjoint
in $D^\bullet$, one needs a **joint** packing theorem. The relevant
matroid structure is: the family of out-branchings rooted at $r$ is
the base family of a matroid (the *branching matroid* $\mathcal M^+$,
of rank $|V| - 1$ on the arc set); the family of in-branchings rooted
at $r$ is the base family of another matroid $\mathcal M^-$ (the
reverse branching matroid). The joint packing of $a$ out + $b$ in
branchings, all pairwise arc-disjoint, is a base-packing problem in
the direct sum $\mathcal M^+ \oplus \mathcal M^-$, equivalent (via
Edmonds–Lovász matroid-union or matroid-intersection) to a flow / cut
condition that **does** read $d^-(X) \ge a$ AND $d^+(X) \ge b$ for
all non-empty $X \subseteq V \setminus \{r\}$.

Frank's *Connections* §10.1 (Theorem 10.1.1 or thereabouts) states
this directly; BJG 2009 has it as §9.6.3 (audit `team/05_audit.md`
§A.10.5 lines 2593–2605). For $D^\bullet$ 4-arc-strong with $a = b =
2$, this gives (F3) immediately.

But this is **out of scope** per the audit's hard-rule. There is no
derivation of (F3) from Theorem 2.5 alone via pointwise cut-counting.

---

## §3 — Honest verdict on (F3)

**Mathematical content.** (F3) is true (Edmonds–Schrijver matroid
union; Frank §10.1; BJG §9.6).

**Provability under the audit's hard-rule (Theorem 2.5 only, no
matroid union, no Frank, no Schrijver).** Not derivable. The
cascading-Edmonds-via-submodularity argument requested in `team/30_*`
§7.4 (F3) and reproduced in §2.1 above relies on an inequality
($\star$) that does not follow from the out-branching property.

**Knock-on effect.** The within-kind submodularity argument of
`team/27_*` lines 197–207 / `team/29_*` §1.2 lines 86–98 (audit-
cleared at `team/05_audit.md` §A.10.6 line 2696) relies on the same
incorrect inequality ($\dagger$). The converse-of-Edmonds salvage
(§2.4) recovers $d^-_{D^\bullet \setminus T_1^+}(X) \ge 2$ when $D^
\bullet$ is 3-arc-strong, but this salvage does **not** give the in-
branching residual $d^+_{D^\bullet \setminus T_1^+}(X) \ge 2$
required to extract $T_1^-$. So the within-kind step **also** has a
gap I had not previously appreciated.

This means the team's status table at `team/30_*` §8 line
"Within-kind disjointness (WK) — Full (Theorem 2.5 + submodularity,
audit-cleared)" needs to be re-examined. The cell currently marked
"Full" is, on the analysis above, "Conditional on a residual cut
inequality the standard literature handles via matroid union but
which the audit's hard rule excludes from our toolkit."

### §3.1 Verifying the within-kind gap claim

Let me make the within-kind gap concrete. The claim of `team/29_*`
§1.2 line 91 is:

> "the out-branching $T_i^+$ contributes at most one arc to $\delta^-
> (X)$ (otherwise it would contain a cycle into $X$, contradicting
> branching)"

The parenthetical justification "otherwise it would contain a cycle
into $X$" is the source of confusion. Let me check: if $T_i^+$ has
two arcs $(u_1, v_1), (u_2, v_2)$ both in $\delta^-(X)$ — both
entering $X$ from outside — does this force a cycle? **No.** Both
arcs land at distinct $v_1, v_2 \in X$; the $T$-paths from $r$ to
$v_1$ and $r$ to $v_2$ may share a prefix but split before $v_1, v_2$
— no cycle is formed. The parenthetical is mathematically incorrect.

The correct statement is the one I derived in §2.3: $|T \cap \delta^-
(X)| = $ number of $T[X]$-components, which is $\ge 1$ but not $\le
1$ in general. The within-kind argument as written does not close.

### §3.2 Possible recoveries

**(R1) Lift the audit's hard rule against matroid union.** Edmonds–
Schrijver matroid union is a standard textbook result (Edmonds 1970;
Frank 2011 §10.1). Citing it is no more exotic than citing Theorem
2.5 itself, which is just the rank-1 special case. The audit's
strict exclusion of matroid union (`team/05_audit.md` §A.10
recommendation 4 explicitly contemplates the lift) seems unduly
restrictive given that the within-kind step **already** implicitly
relies on a matroid-flavor result the audit did not catch.

If matroid union is admitted, **(F3) is a one-line corollary**
(`team/05_audit.md` line 2705-2706, recommendation 4):

> *"Strengthen the hypothesis on $D^\bullet$: claim cross-kind
> disjointness only when $D^\bullet$ is 4-arc-strong (in which case
> the Edmonds-doubled-instance trick *does* work: add an auxiliary
> copy of each branching's 'type' tag and apply Edmonds with $k =
> 4$)."*

This is the auditor's explicit blessing of the matroid-union route at
$\lambda \ge 4$. The "Edmonds-doubled-instance trick" reduces the
joint packing to a single Edmonds application on an auxiliary
digraph; the proof is short and self-contained.

**(R2) Direct application of Frank's theorem at the citation level
only.** Cite Frank 2011 Theorem 10.1.1 or its BJG 2009 §9.6
equivalent for the joint packing, *without* using matroid union
internally in the team's proof. The result is stated and used as a
black box. This is what most digraph-theory papers do; it is
standard and unobjectionable.

**(R3) Restrict the team's claim to within-kind packing only, drop
(F3).** If the audit's hard rule against matroid union and Frank
holds firm, the team has **no** unconditional close at any $\lambda$
level. The within-kind argument is conditional on the same gap; the
cross-kind (F3) inherits it. Option (B) of the combined paper then
ships as "3-arc-strong $(1, 0)$-near-split: SAD conditional on a
within-kind residual cut inequality the team has not proved from
Theorem 2.5 alone." This is more honest than the current draft, which
classifies WK as "Full."

---

## §4 — On the §3.4 16-profile casework

**Conditional on (F3) holding** — by whichever recovery route — the
§3.4 16-profile casework of `team/27_*` transplants here unchanged.
The argument is:

- Each color class $A_i^\bullet := T_i^+ \cup T_i^- \cup F_i$ is
  strongly connected: for any $u, v \in V^\bullet$, the walk
  $u \to r \to v$ (in via $T_i^-$, out via $T_i^+$) lies in
  $A_i^\bullet$. This uses only the existence of $T_i^+$ as an out-
  branching at $r$ and $T_i^-$ as an in-branching at $r$, and the
  fact that they are arc-disjoint (so the walk is well-defined).
  Verbatim from `team/27_*` §3.2.

- For every branching profile $(\sigma_1^+, \sigma_2^+, \sigma_1^-,
  \sigma_2^-) \in \{p, q\}^4$, the §3.4 free-arc distribution
  achieves the R3⋆ side-label condition $Q_i \wedge P_{3-i} \wedge
  Q_{3-i}$ for some $i \in \{1, 2\}$, by `team/27_*` §3.4.6's
  16-row table (corrected at line 538) combined with the supply
  bounds ($\ast$). Under $\lambda \ge 4$ the supply bounds become
  $\ge 3, \ge 4, \ge 4, \ge 3$ — strictly more permissive than the
  $\lambda = 3$ case, so the casework only gets easier.

- The four branching arcs at $r$ are pairwise distinct (the
  (LR)-observation of `team/29_*` §1.3: in-arcs and out-arcs of $r$
  are disjoint sets; within-kind disjointness gives $a_1^+ \ne a_2^+$
  and $a_1^- \ne a_2^-$). This holds for any cross-kind-disjoint
  packing.

So §3.4 is sound modulo (F3). The bottleneck is §2.

---

## §5 — Lift of $\lambda$ from $D$ to $D^\bullet$

For completeness: the cut-lifting argument of `team/21_*` §3.1 proves
$\lambda^{\text{arc}}(D^\bullet) \ge \lambda^{\text{arc}}(D)$. The
proof is via the bijection $|\delta^+_{D^\bullet}(S)| = |\delta^+_D
(\widehat S) \setminus \{e_0\}|$ where $\widehat S = (S \setminus \{r\})
\cup \{p, q\}$ if $r \in S$, else $S$; combined with the structural
observation that $e_0 = (p, q)$ never crosses $\widehat S$ (both
endpoints land in $\widehat S$ whenever either does). The proof reads
"$\ge 3$" in `team/21_*` §3.1 but applies verbatim with $k$ in place
of 3, yielding $\lambda(D^\bullet) \ge k$ for any $k$. In particular,
$D$ 4-arc-strong implies $D^\bullet$ 4-arc-strong.

This step is sound and independent of the §2 gap.

---

## §6 — Status

**On (F3).**

| Statement | Status |
|-----------|--------|
| (F3) is mathematically true | YES — by Edmonds–Schrijver / Frank §10.1, standard literature |
| (F3) derivable from Theorem 2.5 + naive submodularity | **NO** — the inequality ($\star$) is false in general (§2.2) |
| Auditor's recommendation 4 (`team/05_audit.md` §A.10.6 item 4) is sound | YES, but it invokes matroid union explicitly, which the audit's hard rule excludes |

**On the within-kind step (collateral finding).**

| Statement | Status |
|-----------|--------|
| `team/27_*` lines 197–207 / `team/29_*` §1.2 lines 86–98 within-kind submodularity | **GAP** — same inequality ($\dagger$) is false in general (§2.3) |
| Auditor's clearance at `team/05_audit.md` §A.10.6 line 2696 | over-generous on re-examination |
| Converse-of-Edmonds salvage (§2.4) | recovers $d^-_{D \setminus T_1^+}(X) \ge 2$ but not $d^+_{D \setminus T_1^+}(X) \ge 2$, so does not give an in-branching from the residual |

**On Option (B) of the combined paper.**

- The original plan was: ship (F3) as the unconditional 4-arc-strong
  headline, with route-c1's conditional 3-arc-strong result as a
  secondary result.
- Under the hard-rule against matroid union, (F3) is **not**
  unconditionally proved. Worse, the within-kind step of route c1 is
  on the same shaky ground.
- The team has three honest options:
  - **(R1)** Lift the hard rule against Edmonds–Schrijver matroid
    union (standard tool, attributed to Edmonds 1970). (F3) becomes a
    short corollary; within-kind also closes. Ship 4-arc-strong
    unconditionally.
  - **(R2)** Cite Frank 2011 §10.1 (or BJG 2009 §9.6) for the joint
    packing as a black box. Equivalent to (R1) but with a heavier
    citation.
  - **(R3)** Keep the hard rule; admit that both within-kind and
    cross-kind are conditional on a residual-cut inequality the team
    has not derived from Theorem 2.5 alone. Ship Option (B) at
    3-arc-strong with full honest conditionality.

My recommendation is **(R1)**. The audit's hard rule against matroid
union appears overly strict, especially given that the team's
within-kind step (audit-cleared!) already implicitly relies on
matroid-flavor reasoning. Edmonds–Schrijver is no more exotic than
Theorem 2.5; both go back to Edmonds 1970, and both have short
self-contained proofs in any standard reference.

**Load-bearing addition to the chain `team/29_*` / `team/30_*` /
`team/31_*`.** The intended load-bearing addition was a clean
verification of (F3) closing R3⋆-HC unconditionally at $\lambda \ge
4$. The actual load-bearing addition is **a request for the auditor
to revisit the within-kind submodularity step**, since the cross-
kind extension hits exactly the same gap and that gap turns out to
be present in the audit-cleared within-kind step too. Until the
within-kind step is either re-derived from Theorem 2.5 alone (which I
have shown is not possible by the naive submodularity recipe) or
re-cited via matroid union, the entire route-c1 chain — both at $
\lambda = 3$ and at $\lambda = 4$ — is conditional on a residual cut
inequality outside the audit's currently-permitted toolkit.

End of file.
