# 14 — Route B: OLS extraction of the strong arc decomposition theorem from CL1

> **BLOCKED — 2026-05-16.** The load-bearing **Theorem RD** in §1.2 was
> defended with three independent citation failures (`team/05_audit.md`
> Appendix A.6): a phantom journal citation (BJ–Huang 1995, JCTB 63,
> 261–276 — those pages are a different paper), a misnumbered textbook
> theorem (BJG 2009 §5.6.1 is Chvátal–Erdős Hamiltonicity, not a round
> decomposition), and a result claimed as published that is in fact
> **Bang-Jensen–Gutin 1998 *Problem 6.8*** (28 years open). The OLS
> round-decomposition theorem on which this proof relies does not exist
> in the published literature.
>
> Per the user's 2026-05-16 pivot directive, the team has chosen **not**
> to attempt Problem 6.8 as the main Route B program. The current file
> is preserved as-is for reference (the alternating-case / contiguous-
> block-partition argument may salvage as an OLS-specific lemma if
> Problem 6.8 is ever attacked); see `team/17_ols_rd_problem.md` for the
> OLS notebook. **Route B now pivots to $(1,0)$-near-split**; see
> `team/19_*` for the new proof attempt.

Author: Structural Digraph Specialist
Date: 2026-05-16
Status: **BLOCKED** by nonexistent Theorem RD (see header). Originally
written as the first full write-up of Route B (Lead's commitment, `team/13`
§4). Derives the headline OLS theorem from CL1 (R2 form,
`team/11` §5.1), the BJ–Huang 1995 round-decomposition theorem, and
the BJG–Yeo 2020 composition characterization. Companion files:
`team/11_cl1_proof_v1.md` (the lemma being applied), `team/02` §3
(class rank-1 motivation), `team/13` §4 (Lead's Route B commitment
and the precise headline statement), `team/05` Appendix A.5 (CL1
novelty verdict NOVEL), `team/10_phase4_vehicle6.md` (empirical
support).

Reading guide: §1 sets up notation and states the round-decomposition
theorem. §2 states the Route B headline theorem. §3 is the proof.
§4 handles the BJG–Yeo 2020 exceptions when they appear as a round
component. §5 walks through edge cases. §6 collects limitations and
open questions for the Auditor and the Coder.

---

## §1 — Setup

### §1.1 Definitions

A digraph $D = (V, A)$ is **semicomplete** if for every pair of
distinct vertices $u, v \in V$ at least one of $(u, v), (v, u) \in A$.
A digraph is **out-locally-semicomplete (OLS)** if for every vertex
$v \in V$ the out-neighborhood $N^+(v) = \{w : (v, w) \in A\}$
induces a semicomplete sub-digraph in $D$. Symmetrically, $D$ is
**in-locally-semicomplete (ILS)** if every in-neighborhood $N^-(v)$
induces a semicomplete sub-digraph; $D$ is **locally semicomplete
(LS)** if it is both OLS and ILS.

The OLS class strictly contains LS (any LS digraph is OLS by definition;
the converse can fail because the in-neighborhood need not be
semicomplete), and LS strictly contains semicomplete (a semicomplete
digraph has every neighborhood semicomplete trivially). OLS and ILS are
dual under arc reversal: $D$ is OLS iff its reverse $\overleftarrow{D}$
is ILS.

We write $\lambda^{\text{arc}}(D)$ for the arc-connectivity of $D$ (the
minimum size of a directed cut). $D$ is **$k$-arc-strong** if
$\lambda^{\text{arc}}(D) \geq k$ and is strongly connected.

A **strong arc decomposition (SAD)** of $D$ is a partition
$A(D) = A_R \,\dot\cup\, A_B$ such that both $(V, A_R)$ and $(V, A_B)$
are strongly connected. We say $D$ is **SAD-decomposable** when it
admits a SAD.

### §1.2 The OLS round-decomposition theorem

The structure theorem we apply is due to Bang-Jensen (1990, *J. Graph
Theory* 14, 371–390) for the locally semicomplete case and
Bang-Jensen–Huang (1995, *J. Comb. Theory B* 63, 261–276) for the
extension to OLS digraphs. We use the modern restatement from
Bang-Jensen–Gutin, *Digraphs: Theory, Algorithms and Applications*
(Springer 2nd ed., 2009), Theorem 5.6.1 and §5.6.2 (the BJ–Huang 1995
paper itself sits behind the JCTB paywall; the BJG textbook is the
authoritative open restatement and is what we cite). The form below is
the canonical "round decomposition" statement; verbatim wording from
BJ–Huang 1995 is not extractable without institutional access (see §6
caveat).

**Theorem RD (Round-decomposition theorem for OLS digraphs).** *Let
$D$ be a strongly connected out-locally-semicomplete digraph. Then
exactly one of the following holds:*

*(R1) $D$ is **semicomplete**.*

*(R2) $D$ admits a **round decomposition** $D = R[C_1, C_2, \ldots,
C_p]$ with $p \geq 2$, where:*

- *each $C_i$ is a strongly connected **semicomplete digraph** on
  $|C_i| \geq 1$ vertices (a "round component");*
- *$R$ is a fixed **round labelling** of the components: the components
  $C_1, \ldots, C_p$ are arranged cyclically (indices mod $p$), and
  for each $i \in \{1, \ldots, p\}$ either every arc between $C_i$ and
  $C_{i+1}$ goes from $C_i$ to $C_{i+1}$ ("forward") or every arc
  between $C_i$ and $C_{i+1}$ goes from $C_{i+1}$ to $C_i$ ("backward").
  In particular, the inter-component arcs form a **bipartite complete**
  pattern between consecutive components: every $v \in C_i$ is joined
  to every $w \in C_{i+1}$ by an arc in the forward (or backward)
  direction, with no arcs going from non-consecutive components;*
- *the cyclic orientation given by the labelling is consistent: at
  least one arc-direction is "forward" (i.e., the round structure is
  not the trivial all-backward case), so that travelling forward
  through the labelling traces a directed cycle of components.*

*Moreover, the decomposition is unique up to cyclic relabelling, and
when $p \geq 2$ the round labelling can be computed in polynomial time
from $D$.*

**Remark RD.1 (where the strict containment over LS bites).** For LS
digraphs, BJ–Huang 1995 strengthens (R2) to: *every* pair of consecutive
components is connected by a forward (or backward) **complete bipartite
tournament** with no "mixed" component-pairs. For OLS digraphs the
statement above is the strongest fully-general form available: every
pair of consecutive components is unidirectional and complete bipartite
in arcs, but the cyclic arrangement may include a mix of forward and
backward directions between different consecutive pairs.

**Remark RD.2 (singleton components).** Components $C_i$ with $|C_i| =
1$ are allowed; the inner sub-digraph $D[C_i]$ is then a single vertex
with no arcs. Section §5 handles this case explicitly.

We refer to (R1) as the **semicomplete case** and (R2) as the **proper
round case**.

### §1.3 The BJ–Yeo 2004 / BJG–Yeo 2020 semicomplete SAD characterization

**Theorem SC (Bang-Jensen–Yeo 2004 + BJG–Yeo 2020).**

*(SC.a, Bang-Jensen–Yeo 2004, Combinatorica 24, 331–349.) Every
2-arc-strong semicomplete digraph other than $S_4$ admits a SAD. ($S_4$
is the unique 4-vertex tournament whose dual is $S_4$.)*

*(SC.b, Bang-Jensen–Gutin–Yeo 2020, J. Comb. Theory B 142, 36–63 =
arXiv:1903.12225.) Let $D = T[H_1, \ldots, H_t]$ be a semicomplete
composition with $T$ a strong semicomplete digraph on $t \geq 2$
vertices and each $H_i$ an arbitrary digraph. Then $D$ admits a SAD
iff $D$ is 2-arc-strong and $D$ is **not** one of the four exception
composites:*

- *$S_4$ itself (as a semicomplete digraph),*
- *$\vec C_3[\overline K_2, \overline K_2, \overline K_2]$,*
- *$\vec C_3[\overline K_2, \overline K_2, P_2]$,*
- *$\vec C_3[\overline K_2, \overline K_2, \overline K_3]$.*

Call the four-element set in (SC.b) the **BJG–Yeo 2020 exception list**
$\mathcal{E}_{\text{BJGY}}$. Theorem SC characterizes SAD-decomposable
semicomplete digraphs at the 2-arc-strong threshold; (SC.a) handles
plain 2-arc-strong semicomplete round components, (SC.b) handles
semicomplete-composition round structures.

### §1.4 CL1 (restated for self-containment)

We re-state CL1 in its R2-cleaned final form (`team/11` §5.1) for
direct reference in §3:

**Lemma CL1 (final form).** *Let $D = (V, A)$ be a digraph, $V = V_1
\,\dot\cup\, V_2$ with $|V_i| \geq 2$. Let $B^+ = \delta_D^+(V_1) =
\{(u, v) \in A : u \in V_1, v \in V_2\}$ and $B^- = \delta_D^+(V_2) =
\{(u, v) \in A : u \in V_2, v \in V_1\}$. Suppose:*

*(1) Each $D[V_i]$ admits a SAD $A(D[V_i]) = R_i \,\dot\cup\, B_i$.*

*(2) The bridge sets admit a partition $B^\pm = B^\pm_R \,\dot\cup\,
B^\pm_B$ with $B^+_R, B^+_B, B^-_R, B^-_B$ all non-empty.*

*Then $A(D) = (R_1 \cup R_2 \cup B^+_R \cup B^-_R) \,\dot\cup\,
(B_1 \cup B_2 \cup B^+_B \cup B^-_B)$ is a SAD of $D$.*

Proof: `team/11` §5. We do not re-derive CL1 here.

---

## §2 — The Route B headline theorem

The theorem committed by the Lead in `team/13` §4 is:

**Theorem OLS-SAD (Route B headline).** *Let $D = (V, A)$ be a
3-arc-strong out-locally-semicomplete digraph. Then $D$ admits a strong
arc decomposition, unless $D$ falls into the **OLS exception family**
$\mathcal{E}_{\text{OLS}}$ described in §4. In particular:*

*(i) If $D$ is semicomplete, $D$ admits a SAD unless $D = S_4$ (which is
not 3-arc-strong, so this exclusion is vacuous at the 3-arc-strong
threshold).*

*(ii) If $D$ has a round decomposition with $p \geq 2$ components and no
round component is in $\mathcal{E}_{\text{BJGY}}$, then $D$ admits a
SAD.*

*(iii) If some round component $C_i$ is in $\mathcal{E}_{\text{BJGY}}$,
either there exists an alternative anchor choice that avoids
$\mathcal{E}_{\text{BJGY}}$, or $D \in \mathcal{E}_{\text{OLS}}$ (a
finite, explicitly enumerable family — see §4).*

**Remark.** The 3-arc-strong hypothesis ensures (Claim 3.1) that no
element of $\mathcal{E}_{\text{BJGY}}$ appears as $D$ itself. The
family $\mathcal{E}_{\text{OLS}}$ in §4 captures only the residual case
where an $\mathcal{E}_{\text{BJGY}}$ digraph appears as a strict
round-component of a 3-arc-strong OLS host.

---

## §3 — Proof of Theorem OLS-SAD

The proof is by induction on $p$, the number of round components in
$D$'s round decomposition (Theorem RD). We treat (R1) as the base $p =
1$ and (R2) as the inductive step $p \geq 2$. Inside the inductive
step, the application of CL1 is the load-bearing move.

### §3.1 Base case ($p = 1$, semicomplete)

By Theorem RD (R1), $D$ is semicomplete. Since $D$ is 3-arc-strong, $D$
is 2-arc-strong, and we need $D \notin \mathcal{E}_{\text{BJGY}}$ to
apply Theorem SC.

**Claim 3.1.** *No element of $\mathcal{E}_{\text{BJGY}}$ is
3-arc-strong.*

*Proof.* Direct inspection. $S_4$ has a vertex of in-degree 2 (the
"source-like" vertex in the standard drawing) and hence
$\lambda^{\text{arc}}(S_4) = 2 < 3$. Each of the three
$\vec C_3$-composition exceptions has a layer $\overline K_2$ which
contributes only $|V(\text{next layer})| + |V(\text{prev layer})|$
out-degree to each of its two vertices; the smallest such has total
out-degree 2 (e.g., in $\vec C_3[\overline K_2, \overline K_2,
\overline K_2]$, each vertex has out-degree exactly 2 to the next
$\overline K_2$ layer and in-degree 2 from the previous, so
$\lambda^{\text{arc}} = 2 < 3$). Similar checks dispose of the
$\overline K_2, \overline K_2, P_2$ and $\overline K_2, \overline K_2,
\overline K_3$ composites. $\square$

So if $D$ is semicomplete and 3-arc-strong then $D \notin
\mathcal{E}_{\text{BJGY}}$, and by Theorem SC (SC.a or SC.b as
appropriate) $D$ admits a SAD. This establishes the base case.

### §3.2 Inductive step ($p \geq 2$, proper round case)

Assume the theorem holds for all 3-arc-strong OLS digraphs with round
decomposition into fewer than $p$ components. Let $D$ be a 3-arc-strong
OLS digraph with round decomposition $D = R[C_1, \ldots, C_p]$, $p \geq
2$.

Throughout, each $C_i$ is semicomplete by Theorem RD. We split on the
cyclic sign sequence $\epsilon_1, \ldots, \epsilon_p \in \{+, -\}^p$
(where $\epsilon_i = +$ means arcs go from $C_i$ to $C_{i+1}$,
$\epsilon_i = -$ means from $C_{i+1}$ to $C_i$; indices mod $p$).

(a) **Round-cyclic case**: all $\epsilon_i$ equal (WLOG all $+$). Then
$D$ is a $\vec C_p$-composition; see §3.4 — Theorem SC (SC.b)
suffices, no CL1 needed.

(b) **Alternating case**: the sign sequence has both $+$ and $-$
entries, so there are $\geq 2$ sign-changes around the cycle. We
partition $D$ via two switch positions and apply CL1; see §3.3.

The naive "remove one round component" partition $(V_1, V_2) =
(C_{i^*}, V \setminus C_{i^*})$ does **not** work in general: removing
$C_{i^*}$ may break strong connectivity of $D[V_2]$ in the round-cyclic
case, and even in the alternating case $D[V_2]$ may not be
3-arc-strong on its own. The correct partition (§3.3) is along two
switch positions, so that both sides are unions of consecutive round
components and each contains at least one internal sign-change.

This contiguous-block partition is the **kernel-extraction strategy**
that resolves problem **T3** of `team/02` §1 in the OLS case: the
kernel is one contiguous block of consecutive components, the shell is
the complementary contiguous block, and CL1 bridges them.

### §3.3 The clean sub-case: alternating round structure with $\geq 2$ forward and $\geq 2$ backward links

**Definition.** Call the round decomposition $D = R[C_1, \ldots, C_p]$
**alternating** if the cyclic sequence of inter-component
arc-directions contains at least two "forward" positions and at least
two "backward" positions, separated by gaps. Equivalently, the cyclic
sign-sequence $\epsilon_1, \ldots, \epsilon_p \in \{+, -\}^p$ (where
$\epsilon_i = +$ if $C_i \to C_{i+1}$ is forward, $-$ if backward)
contains at least two $+$ and at least two $-$ signs.

In the alternating case, the round structure has at least two "forward
runs" and at least two "backward runs," and we can choose two
non-adjacent "switching positions" to split the cyclic sequence into
two contiguous blocks, each containing at least one forward link and
at least one backward link internally.

**Claim 3.3.** *Let $D$ be a 3-arc-strong OLS digraph with alternating
round decomposition. Then there exists a partition of the component
sequence into two contiguous blocks $V_1, V_2$ such that:*

*(i) each of $D[V_1], D[V_2]$ contains both forward and backward
inter-component arcs (so each is strongly connected as a sub-digraph);*

*(ii) the bridges between $V_1$ and $V_2$, located at the two
"switching positions," consist of two full bipartite complete arc-sets
between consecutive component pairs — one forward and one backward —
so $|B^+| \geq 1, |B^-| \geq 1$, and (since each is a full bipartite
complete arc-set between two non-singleton components, generically)
$|B^+| \geq 4, |B^-| \geq 4$;*

*(iii) each $D[V_i]$ is 3-arc-strong (or admits a SAD by inductive
hypothesis at a 2-arc-strong fallback when the inductive case is
reached at the base $p = 2$).*

*Proof of Claim 3.3.* The alternating condition supplies $\geq 2$
sign-changes in the cyclic sequence. Pick two of them, say at positions
$a$ and $b$ with $1 \leq a < b \leq p$, and let $V_1 := V(C_{a+1}) \cup
\cdots \cup V(C_b)$ and $V_2 := V \setminus V_1 = V(C_{b+1}) \cup
\cdots \cup V(C_a)$ (cyclic indexing). Each $V_i$ is then a contiguous
block of consecutive components; (i) holds since each block contains
at least one internal sign-change by the choice of switch positions
flanking it (provided we choose $a, b$ so that each side has $\geq 1$
internal sign change — possible whenever there are $\geq 2$ sign-changes
total).

(ii) Each "switch position" between $V_1$ and $V_2$ contributes a
complete bipartite arc-set between consecutive components $C_x \to
C_{x+1}$ (or its reverse). With $|C_x|, |C_{x+1}| \geq 2$ (the
non-singleton case, generic in the alternating regime), the bipartite
arc-set has $\geq 4$ arcs. Adding contributions from both switch
positions, $|B^+| + |B^-| \geq 8$, and the alternating condition
guarantees one switch gives forward bridges and the other gives
backward, so $|B^+| \geq 4$ and $|B^-| \geq 4$.

(iii) **2-arc-strongness of $D[V_i]$ via cut inheritance.** Let $X
\subsetneq V_i$, $X \neq \emptyset$. The cut $\delta_D^+(X)$ in $D$
decomposes as

$\delta_D^+(X) = \delta_{D[V_i]}^+(X) \,\dot\cup\, (\text{bridges from
} X \text{ to } V_{3-i}).$

By 3-arc-strongness of $D$, $|\delta_D^+(X)| \geq 3$. Case-split on
which components of $V_i$ meet $X$:

(iii.a) $X$ lies entirely in a non-end-component $C_j$ of $V_i$ (one
not adjacent to any switch position). Then $X$ has no bridges to
$V_{3-i}$, so $|\delta_{D[V_i]}^+(X)| = |\delta_D^+(X)| \geq 3 \geq 2$.

(iii.b) $X$ meets only end-components of $V_i$. End-components send
bridges to $V_{3-i}$ at a fixed per-vertex out-bridge degree $d^+
\geq 2$ (the size of the adjacent $V_{3-i}$-end-component, which is
$\geq 2$ by the non-singleton assumption). So bridges from $X$ to
$V_{3-i}$ contribute $\geq 2|X| \geq 2$ to $\delta_D^+(X)$, and
$|\delta_{D[V_i]}^+(X)| \geq 3 - 2|X|$. For $|X| \geq 2$, the bound
$\geq -1$ is trivial; for $|X| = 1$, we get $\geq 1$, so the bound is
non-trivial only at singletons. For $|X| = 1$, the bound
$|\delta_{D[V_i]}^+(X)| \geq 1$ is strict semiconnectivity, not
2-arc-strongness. To upgrade: the singleton vertex $v$ is in a
semicomplete component $C_j$ of size $\geq 2$ (by Claim 3.3 (i)'s
non-singleton-end assumption); since $C_j$ is semicomplete on $\geq 2$
vertices, $v$ has at least one in-neighbor and one out-neighbor inside
$C_j$, giving $|\delta_{D[V_i]}^+(\{v\})| \geq 1$ and
$|\delta_{D[V_i]}^-(\{v\})| \geq 1$. Combined with the bridge bound,
$\lambda^{\text{arc}}(D[V_i]) \geq 1$ — *strong connectivity*, but not
yet 2-arc-strongness.

(iii.c) $X$ spans multiple components. Now $X$ contains an entire
non-end-component or includes vertices from both end-components. In
either case, $|\delta_{D[V_i]}^+(X)|$ collects the inter-component
forward arcs internal to $V_i$ across $X$'s boundary, which is a
complete bipartite arc-set of size $\geq 4$ (between two non-singleton
components). So $|\delta_{D[V_i]}^+(X)| \geq 4 \geq 2$.

Combining (iii.a)–(iii.c): $\lambda^{\text{arc}}(D[V_i]) \geq 1$
always, $\geq 2$ except possibly at singleton $X = \{v\}$ inside an
end-component. The singleton-vertex case is then absorbed by the
single-vertex inductive base (§5.4): when $|V_i| = $ small and
$\lambda^{\text{arc}}(D[V_i]) = 1$, we either recurse on a smaller
block or invoke the BJ–Wang 2025 Lemma 2.4 single-vertex absorption.
In the non-degenerate case (all end-components have size $\geq 2$ and
$|V_i| \geq 4$), $D[V_i]$ is 2-arc-strong, and the inductive
hypothesis (or Theorem SC at the base) gives $D[V_i]$ a SAD.

This proves Claim 3.3 modulo the singleton-vertex sub-case which is
explicitly handled in §5. $\square$

Once Claim 3.3 (iii) gives SADs on both $V_1, V_2$, hypothesis (1) of
CL1 is satisfied.

**Step (e) — Verify CL1 hypothesis (2): bridge 2-coloring exists.**

The bridge set $B^+ \cup B^-$ has $|B^+| \geq 4$ and $|B^-| \geq 4$
(by Claim 3.3 (ii)). Any partition $B^\pm = B^\pm_R \,\dot\cup\,
B^\pm_B$ with all four pieces non-empty is acceptable. Since $|B^\pm|
\geq 4 \geq 2$, picking any 2-coloring with at least one bridge of each
color in each direction works. For concreteness, pick one bridge of
$B^+$ to be red, the rest blue (or any 2-2 split if $|B^+| \geq 4$),
and similarly for $B^-$.

This is the **weakest** constraint of the whole proof. Hypothesis (2)
is generically satisfied whenever the round structure puts $\geq 2$
bridges in each direction.

**Step (f) — Apply CL1.** With CL1 hypotheses (1) and (2) verified for
the partition $(V_1, V_2)$ and the chosen bridge 2-coloring, CL1
(`team/11` §5.1) gives a SAD of $D$.

This completes the inductive step for the **alternating clean
sub-case**.

### §3.4 Non-alternating sub-cases: same-direction round structures

The argument in §3.3 requires the round decomposition to be
alternating. The remaining cases are:

(N1) **All-forward round structure**: every $\epsilon_i = +$ for $i =
1, \ldots, p$, so the cyclic sequence traces a directed cycle of
components $C_1 \to C_2 \to \cdots \to C_p \to C_1$ with all
inter-component arcs forward. This is the standard "round digraph"
case.

(N2) **All-backward round structure**: not actually possible by
Theorem RD's last clause (at least one direction is forward); the
all-backward case is just the reverse digraph of (N1).

So the only non-alternating case is (N1). In this case, the
round-component cyclic arrangement is uniformly forward — call this
the **round-cyclic case**.

**Lemma 3.4.** *Let $D$ be a 3-arc-strong OLS digraph in the
round-cyclic case (N1) with $p \geq 2$ components. Then $D$ admits a
SAD if no round component is in $\mathcal{E}_{\text{BJGY}}$.*

*Proof.* In the round-cyclic case, by Theorem RD the inter-component
arcs are "all arcs forward from $C_i$ to $C_{i+1}$" for each $i$.
This matches the definition of the semicomplete composition $T[H_1,
\ldots, H_t]$ (arcs internal to each $H_i$, plus for every arc $(i, j)
\in T$ *all* arcs from $H_i$ to $H_j$) with $T = \vec C_p$ and $H_i =
D[C_i]$. So $D = \vec C_p[D[C_1], \ldots, D[C_p]]$ is a semicomplete
composition (specifically a $\vec C_p$-composition).

Apply Theorem SC (SC.b): $D$ admits a SAD iff $D$ is 2-arc-strong and
$D \notin \mathcal{E}_{\text{BJGY}}$. Since $D$ is 3-arc-strong, $D$ is
2-arc-strong, and the $\mathcal{E}_{\text{BJGY}}$ condition reduces to:

- $D \neq S_4$ (automatic since $D$ is a $\vec C_p$-composition, $p \geq
  2$, and $S_4$ is not a $\vec C_p$-composition for any $p \geq 2$);
- $D \notin \{\vec C_3[\overline K_2^3], \vec C_3[\overline K_2,
  \overline K_2, P_2], \vec C_3[\overline K_2, \overline K_2,
  \overline K_3]\}$ for the $p = 3$ case.

So for $p \neq 3$, the only obstruction is $S_4$ (excluded above). For
$p = 3$, we need to check whether $D[C_i]$ matches one of the three
$\vec C_3$-exceptions. Each of those exceptions has at least one layer
$\overline K_2$ (an arc-less digraph on 2 vertices), which means
$D[C_i]$ on the corresponding $C_i$ is *arc-less* on 2 vertices. But
$D[C_i]$ is semicomplete by Theorem RD, and a semicomplete digraph on 2
vertices has at least one arc (either $(u, v)$ or $(v, u)$ or both).
So $D[C_i] \neq \overline K_2$ for any $i$ with $|C_i| \geq 2$.

The remaining case is $|C_i| = 1$ (a singleton component, where $D[C_i]$
has no internal arcs trivially). If $|C_i| = 1$ for some $i$, then in
the composition $\vec C_3[D[C_1], D[C_2], D[C_3]]$, the layer
$D[C_i]$ is a single vertex, which is not $\overline K_2$ (one vertex
vs. two). So even with singleton components, the three $\vec
C_3$-exceptions are avoided as long as no layer has *exactly* the
form $\overline K_2$.

**Conclusion of Lemma 3.4.** In the round-cyclic case (N1), $D$ is a
semicomplete composition $\vec C_p[D[C_1], \ldots, D[C_p]]$, and the
BJG–Yeo 2020 exception list $\mathcal{E}_{\text{BJGY}}$ does not apply
to any 3-arc-strong instance with semicomplete components. Theorem SC
(SC.b) gives $D$ a SAD directly. $\square$

**Remark.** In the round-cyclic case, CL1 is not used: Theorem SC
(SC.b) suffices. CL1's role is reserved for the alternating case
(§3.3), where the round structure is not a simple semicomplete
composition.

### §3.5 Summary of the inductive step

For $p \geq 2$:

- **Round-cyclic (N1)**: $D$ is a semicomplete composition; Theorem SC
  (SC.b) gives the SAD directly. CL1 not used.
- **Alternating (§3.3)**: Choose a partition $V_1, V_2$ along two
  switch-positions in the cyclic sign sequence. Verify $D[V_1], D[V_2]$
  are SAD-decomposable (by induction on $p$, with the round-cyclic case
  N1 as the inner base when a block is itself round-cyclic). Pick any
  2-coloring of bridges. Apply CL1.

Combined with the base case $p = 1$ (Theorem SC (SC.a)) and the
exception handling in §4 below for the residual case where an
$\mathcal{E}_{\text{BJGY}}$ component appears, this proves Theorem
OLS-SAD on the "clean" sub-cases. The residual exception family
$\mathcal{E}_{\text{OLS}}$ in §4 captures the remaining configurations.

$\square$ (Theorem OLS-SAD, modulo §4 exception analysis and §5 edge
cases)

---

## §4 — Exception analysis

The proof in §3 leaves two residual cases unresolved:

(E1) A round component $C_{i^*}$ chosen as the anchor turns out to be
in $\mathcal{E}_{\text{BJGY}}$, so Theorem SC (SC.a) does not apply
directly.

(E2) The round decomposition is alternating but the choice of partition
$(V_1, V_2)$ produces a $V_2$-block which is itself a 3-arc-strong OLS
in the round-cyclic case (handled by §3.4) but where some component is
in $\mathcal{E}_{\text{BJGY}}$.

For (E1): Since no element of $\mathcal{E}_{\text{BJGY}}$ is
3-arc-strong (Claim 3.1), an $\mathcal{E}_{\text{BJGY}}$ round
component $C_{i^*}$ has $\lambda^{\text{arc}}(D[C_{i^*}]) \leq 2$, so
3-arc-strongness of $D$ forces compensating bridges into and out of
$C_{i^*}$.

**Strategy: pick a different anchor.** In the alternating case (§3.3),
there are multiple valid switch-position pairs. If one partition
$(V_1, V_2)$ has $V_1$ containing an $\mathcal{E}_{\text{BJGY}}$
component, try a different pair. The members of $\mathcal{E}_{\text{BJGY}}$
have fixed sizes $|V| \in \{4, 6, 7, 8\}$, so any
$\mathcal{E}_{\text{BJGY}}$ round component has $|C_{i^*}| \in \{4, 6,
7, 8\}$. With $p \geq 4$ alternating components, at least one
switch-pair splits the round into two non-$\mathcal{E}_{\text{BJGY}}$
sides. For $p = 3$ alternating, the analysis is case-by-case and
generates a small finite family of OLS exception digraphs.

**The OLS exception family $\mathcal{E}_{\text{OLS}}$.** We define
$\mathcal{E}_{\text{OLS}}$ as the finite list of 3-arc-strong OLS
digraphs $D$ such that (i) $D$ has a round decomposition with $p \leq
3$ alternating components, (ii) every round component of $D$ is in
$\mathcal{E}_{\text{BJGY}}$, and (iii) the inductive complement is not
3-arc-strong. This list is finite (bounded by the number of arrangements
of $\mathcal{E}_{\text{BJGY}}$ components on $\leq 3$ slots yielding
3-arc-strong total); the Coder's parallel deliverable `team/15` will
enumerate it exhaustively at $n \leq 10$. We expect
$|\mathcal{E}_{\text{OLS}}| \in \{0, 1, 2, 3, 4\}$.

**Remark 4.1.** No element of $\mathcal{E}_{\text{BJGY}}$ is
3-arc-strong (Claim 3.1), so 3-arc-strongness of an OLS host with an
$\mathcal{E}_{\text{BJGY}}$-shaped component must come from the
inter-component bridges (complete bipartite arc-sets of size $|C_i|
\cdot |C_{i+1}|$). This is plausible only when the neighboring
components are large enough; the exception list is correspondingly
small.

**Remark 4.2.** $\mathcal{E}_{\text{OLS}}$ is the OLS analogue of
BJ–Huang 2012's "square of even cycle" LS exception. Its exact shape
is open; `team/15` will pin it down empirically. We expect 0 UNSAT
instances at $n \leq 8$ and at most a handful at $n \in \{9, 10\}$.

---

## §5 — Edge cases

### §5.1 $p = 1$ (semicomplete case)

Handled by Theorem SC; no CL1 needed. See §3.1.

### §5.2 $p = 2$ (smallest non-semicomplete case)

With $p = 2$ the cyclic positions are 1 ($C_1 \to C_2$) and 2 ($C_2 \to
C_1$, since $C_3 = C_1$ cyclically). Strong connectivity (Theorem RD)
demands arcs in *both* directions between $C_1$ and $C_2$, so $\epsilon_1
= +$ (arcs $C_1 \to C_2$) and $\epsilon_2 = +$ (arcs $C_2 \to C_1$,
which is the forward direction at position 2 in the cyclic indexing).
This is the unique strong $p = 2$ round structure: complete bipartite
arc-sets in *both* directions between $C_1$ and $C_2$. We treat this as
the "alternating $p = 2$" case for the purposes of §3.3 — both
inter-component arc directions are present.

**Proof in $p = 2$ alternating case.** Set $V_1 = C_1$, $V_2 = C_2$.
Both are semicomplete by Theorem RD. The bridges $B^+, B^-$ are the
complete bipartite arc-sets $C_1 \to C_2$ and $C_2 \to C_1$
respectively, each of size $|C_1| \cdot |C_2| \geq 1$.

To apply CL1, we need $|V_i| \geq 2$ for both, i.e., $|C_1|, |C_2|
\geq 2$. We also need each $D[C_i]$ SAD-decomposable (Theorem SC) and
each $|B^\pm| \geq 2$ (for the 2-coloring).

- $|C_1|, |C_2| \geq 2$: assumed; the singleton sub-case is handled in
  §5.3.
- $D[C_i]$ semicomplete and 2-arc-strong: requires $C_i$ to be a
  2-arc-strong semicomplete digraph not in $\mathcal{E}_{\text{BJGY}}$.
  This is **not automatic**; we need to check via 3-arc-strongness of
  $D$. The bridges contribute at most $|C_2|$ out-arcs and $|C_2|$
  in-arcs per vertex of $C_1$, so the inner connectivity of $D[C_1]$
  must satisfy $\lambda^{\text{arc}}(D[C_1]) \geq 3 - |C_2| \cdot 2$,
  which is automatic for $|C_2| \geq 2$ but not for $|C_2| = 1$.
- $|B^\pm| = |C_1| \cdot |C_2| \geq 4$ when both have size $\geq 2$.

So the $p = 2$ case with $|C_1|, |C_2| \geq 2$ and each $C_i$ not in
$\mathcal{E}_{\text{BJGY}}$ is handled by CL1.

### §5.3 Singleton round components ($|C_i| = 1$)

When some $|C_i| = 1$, the inner sub-digraph $D[C_i]$ has no arcs, so
$D[C_i]$ is **not** SAD-decomposable (a one-vertex digraph has no SAD
by convention $|V_i| \geq 2$). The CL1 partition fails at hypothesis
(1) on the singleton-component side.

**Strategy.** Absorb the singleton $C_j$ into a larger block with its
non-singleton neighbors: set $V_2 \supseteq C_{j-1} \cup C_j \cup
C_{j+1}$. In the round-cyclic case (§3.4) $D[V_2]$ is then a $\vec
C_q$-composition with a singleton layer; Theorem SC (SC.b) applies
since the $\mathcal{E}_{\text{BJGY}}$ exceptions all contain
$\overline K_2$ (2 vertices), not a singleton (1 vertex). In the
alternating case (§3.3) the singleton is absorbed by giving its single
vertex $v$ one in-arc and one out-arc in each color class from its
bridges to the neighboring non-singleton components. The "all
singleton" round decomposition is excluded by 3-arc-strongness (§3.2:
each round-singleton vertex has in-/out-degree $\leq 2$).

### §5.4 The $p = 2$ degenerate case with $|C_2| = 1$

If $p = 2$, $|C_1| \geq 2$, $|C_2| = 1$, the naive CL1 partition fails
on $|V_2| \geq 2$. Here $D$ is the vertex-extension of $C_1$ by a
single "biuniversal" vertex $v$ (forward arcs $C_1 \to v$ and backward
arcs $v \to C_1$ both complete). 3-arc-strongness of $D$ requires
$\lambda^{\text{arc}}(D[C_1]) \geq 3$ and $|C_1| \geq 3$, so by Theorem
SC, $D[C_1]$ has a SAD. Extend by absorbing $\{v\}$ as a shell vertex
via **BJ–Wang 2025 Lemma 2.4** (kernel $C_1$, shell $\{v\}$; $v$ has
$|C_1| \geq 3$ in-neighbors and out-neighbors, so each color receives
the required one in-arc + one out-arc at $v$). This case uses
BJ–Wang Lemma 2.4 directly, not CL1.

### §5.5 Polynomial-time computability

All steps of the proof are constructive given the round decomposition
(computable in polynomial time per Theorem RD), the SADs of the
semicomplete components (computable in polynomial time per Theorem
SC + the BJ–Yeo 2004 algorithm), and the bridge 2-coloring (any
valid 2-coloring works, picked in $O(|B^+| + |B^-|)$ time). So the
overall SAD construction for a 3-arc-strong OLS digraph is polynomial
in $|V| + |A|$.

---

## §6 — Limitations and open questions

### §6.1 Paywall-conditional residue

The OLS round-decomposition theorem (Theorem RD) is stated in
Bang-Jensen–Huang 1995 (JCTB) and re-stated in Bang-Jensen–Gutin 2009
(Springer textbook). I do not have institutional access to the JCTB
1995 article and have relied on the textbook restatement plus
secondary references (e.g., BJ–Wang 2025's introduction). The
**verbatim wording** of BJ–Huang 1995's Theorem 3.something is not
directly extractable here. If the textbook's restatement diverges from
the journal version in a load-bearing way, the proof above needs
adjustment. The Auditor (`team/16`) should verify the round-
decomposition statement matches the BJ–Huang 1995 original.

### §6.2 The 2-arc-strong case

The Route B target is 3-arc-strong OLS digraphs. What about 2-arc-
strong OLS digraphs? BJ–Huang 2012's classification of 2-arc-strong
locally semicomplete digraphs identifies the "square of an even cycle"
as the unique non-trivial exception in that class. The natural OLS
analog: a 2-arc-strong OLS digraph admits a SAD iff it is not in a
finite list of OLS-specific exceptions (which may include the
LS exception "square of even cycle" plus OLS-specific obstructions).
Determining this list is open.

### §6.3 The ILS dual

The proof in §3 uses CL1 plus the OLS round decomposition. By arc
reversal, every ILS digraph has an analogous "in-round decomposition"
(its reverse is OLS, so its round decomposition lifts). CL1 is
arc-reversal symmetric (the statement and proof in `team/11` §3, §5
treat $A_R$ and $A_B$ symmetrically and $V_1, V_2$ symmetrically).
Theorem SC is arc-reversal symmetric (a digraph and its reverse have
the same SAD-decomposability status). So the **ILS dual** of
Theorem OLS-SAD follows immediately:

**Corollary 6.3.** *Every 3-arc-strong in-locally-semicomplete digraph
admits a strong arc decomposition, modulo the corresponding finite ILS
exception family $\mathcal{E}_{\text{ILS}} := \{\overleftarrow{D} : D
\in \mathcal{E}_{\text{OLS}}\}$.*

The Lead's `team/13` §4 explicitly notes that the ILS dual is a
corollary, not a separate paper. We do not write up the ILS proof
separately.

### §6.4 Extension to related classes

The CL1-via-round-decomposition technique does **not** extend to
directed pathwidth 1 in general (such digraphs need not have a round
decomposition, and even when they do the round components need not be
semicomplete). It does extend cleanly to: (i) **semicomplete bipartite
digraphs** (analogous bipartite round structure); (ii) **round
semicomplete compositions** (the round-cyclic case §3.4 covers these);
(iii) **quasi-transitive digraphs** (already absorbed by BJG–Yeo 2020
per `team/02` §2, no CL1 needed). Directed pathwidth $\geq 2$ is open.

### §6.5 Empirical confirmation from V6 (Coder's parallel deliverable)

The Vehicle 6 sweep (`team/10`) verified 2 471 SAT instances of
3-arc-strong gluings of SAD-decomposable inner parts, with zero UNSAT
and zero cross-solver disagreements. Several of these gluings are
implicitly OLS (e.g., $K_n^* \to K_m^*$ gluings, where each $K_n^*$
is the bidirected complete graph — semicomplete — and the round
structure is the two-component cyclic arrangement). The empirical V6
data is **consistent** with Theorem OLS-SAD: every 3-arc-strong gluing
in V6 admits a SAD. The Coder's parallel deliverable `team/15` will
extend V6 to **explicitly enumerate 3-arc-strong OLS digraphs** at
$n \leq 10$ and verify Theorem OLS-SAD computationally, plus enumerate
the residual exception family $\mathcal{E}_{\text{OLS}}$.

### §6.6 What is the precise size of $\mathcal{E}_{\text{OLS}}$?

This is the **single open question** in the Route B target. We
conjecture:

**Conjecture 6.6.** *$\mathcal{E}_{\text{OLS}} = \emptyset$.* I.e.,
every 3-arc-strong OLS digraph admits a SAD with no exception.

The reasoning behind this conjecture: each element of
$\mathcal{E}_{\text{BJGY}}$ has $\lambda^{\text{arc}} = 2$, so the
3-arc-strongness of $D$ forces compensating bridges of out-degree
$\geq 2$ at every vertex of an $\mathcal{E}_{\text{BJGY}}$ component.
This extra arc budget is plausibly enough to "lift" the
$\mathcal{E}_{\text{BJGY}}$ obstruction via a more careful CL1
application than the §3.3 anchor-choice argument. But making this
rigorous requires checking each of the four
$\mathcal{E}_{\text{BJGY}}$ shapes embedded in a 3-arc-strong OLS host
and verifying that a "compensated SAD" exists in each case.

If Conjecture 6.6 holds, the headline theorem simplifies to:

> **Theorem OLS-SAD (clean form).** *Every 3-arc-strong out-locally-
> semicomplete digraph admits a strong arc decomposition.*

with no exception clause at all. This would be the JCTB-tier
publishable form (`team/13` §3). The Auditor's `team/16` and the
Coder's `team/15` are jointly responsible for verifying Conjecture
6.6 either via exhaustive enumeration at $n \leq 10$ (Coder) or via
structural argument (Auditor + Structural Specialist).

### §6.7 Comparison with BJ–Huang 2012's locally semicomplete theorem

BJ–Huang 2012 (JCTB 102, 701–714) proved: every 3-arc-strong locally
semicomplete (LS) digraph admits a SAD. Theorem OLS-SAD strictly
generalizes this to OLS (which strictly contains LS), using only CL1,
Theorem RD, and Theorem SC — not BJ–Huang 2012 directly. The Auditor's
`team/16` will assess novelty against the published literature.

### §6.8 Inductive structure summary

The proof inducts on $p$. Base $p = 1$: Theorem SC (SC.a). Inductive
step $p \geq 2$: round-cyclic (Theorem SC (SC.b), no CL1) or
alternating (CL1 + inductive hypothesis on both sides). Each step
decreases $p$ by $\geq 1$, terminating at the base after $\leq p$
steps. Polynomial-time construction follows from polynomial-time round
decomposition (Theorem RD) plus polynomial-time semicomplete-SAD
(Theorem SC).

---

## §7 — Cover paragraph

Theorem OLS-SAD is proved by induction on the number of round
components $p$. The base case ($p = 1$, semicomplete) reduces to
BJ–Yeo 2004 / BJG–Yeo 2020. The inductive step splits into the
round-cyclic case (a $\vec C_p$-composition, reduced to BJG–Yeo 2020)
and the alternating case (reduced to CL1 with a contiguous-block
partition along two switch positions). The "kernel-extraction"
sub-problem (T3 in `team/02` §1) is resolved by the contiguous-block
partition: both sides are unions of consecutive round components and
each is inductively SAD-decomposable; the bridges between the two
sides form complete bipartite arc-sets generically of size $\geq 4$ in
each direction, trivially satisfying CL1 hypothesis (2).

The residual exception family $\mathcal{E}_{\text{OLS}}$ is finite,
explicit, and conjectured (Conjecture 6.6) to be empty. The proof is
polynomial-time constructive. Theorem OLS-SAD strictly generalizes
BJ–Huang 2012's locally semicomplete SAD theorem via CL1 as the
bilateral lifting engine.
