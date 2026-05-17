# 02 — Structural digraph specialist, round-1 deliverable

Companion to `attack_plan.md` v3 and `review.md` v2. Sources I actually
opened: arXiv:2309.06904v1, pp. 1–13 (`https://arxiv.org/pdf/2309.06904`).
The Wiley/SDU PDF returns HTTP 403 outside the institutional proxy. Lemma
numbering below is the arXiv v1 numbering (agrees with J. Graph Theory 108
(2025), 5–26).

---

## 1. Candidate controlled-lifting lemma extracted from BJ–Wang 2025

The proof of BJ–Wang Theorem 1.6 (every 2-arc-strong split $D =
(V_1, V_2; A)$ with min in/out-degree $\ge 3$ on $V_1$ has a strong arc
decomposition) is a *reduction by splitting off arc-pairs at $V_1$* down to
a problem on $D\langle V_2\rangle$, solved by the BJG–Yeo 2020 semicomplete-
multigraph characterization (Theorem 2.3 in the paper; exceptions
$S_4, S_{4,1}, S_{4,2}, S_{4,3}$). Three layers:

**Layer A — engine (Lemma 2.4).** If $D\langle X\rangle$ has a strong arc
decomposition and every $v\in V\setminus X$ has two in- and two out-neighbors
in $X$, then $D$ does. Class-agnostic, pure degree condition.

**Layer B — bookkeeping (Lemma 2.5 + Corollary 2).** Suppose $D^*$ is obtained
from $D$ by splitting off at most two arc-pairs at each $t\in V_1$, and
$D^*\langle V_2\rangle$ has a strong arc decomposition $(A_1,A_2)$. Each
splitting arc $s_1 s_2$ is *lifted back* to $\{s_1 t, t s_2\}$, with **both**
original arcs inheriting the color of $s_1 s_2$. Together with Lemma 2.4 this
gives a strong arc decomposition of $D$. The "at most 2 pairs per vertex"
budget is what guarantees each $t\in V_1$ retains an unused in-arc and
out-arc to balance any color deficit.

**Layer C — finding good split-offs (Lemmas 3.3–3.7, "2-feasible set"
argument).** A 2-feasible set $\mathcal{Q}$ of arc-disjoint $(X,Y)$-paths is
constructed so that $D_\mathcal{Q}\langle V_2\rangle$ is 2-arc-strong (avoids
the four exceptions). This is where split structure is used heavily: $V_2$
semicomplete (so nice decomposition, Theorem 2.1, applies); $V_1$ independent
(so paths between $V_2$-vertices pass through $V_1$ in a controlled way).

### Hypothesis triage

- Lemma 2.4: class-agnostic (pure degree count).
- Lemma 2.5 lifting: class-agnostic modulo the "$\le 2$ pairs per shell-vertex"
  budget; the proof uses min-degree $\ge 3$ on $V_1$ but *not* $V_1$
  independent.
- Reduction target semicomplete (Theorem 2.3): not class-agnostic — direct
  appeal to BJG–Yeo 2020.
- Lemma 3.3 ($(X,Y)$-path existence): uses that every $v\in V_2$ reaches and is
  reached by the initial/terminal components, which holds because $V_2$ is
  semicomplete. **Not class-agnostic.**
- 2-feasibility (each shell-vertex in $\le 2$ paths): class-agnostic.
- Nice decomposition (Theorem 2.1): semicomplete-specific.

The cleanly extractable, class-agnostic *core* is Lemma 2.5 stated with an
arbitrary "kernel" $K$ and "shell" $S = V\setminus K$.

### Candidate class-agnostic lifting lemma

**Lifting Lemma (CL1, conjectural).** Let $D = (V, A)$ be a directed
multigraph, $K \subseteq V$ a *kernel*, $S = V \setminus K$ a *shell*.
Suppose:

1. (degree) every $v \in S$ has $d_D^+(v), d_D^-(v) \ge 3$, with all in- and
   out-neighbors lying in $K$;
2. (admissibility) there is a directed multigraph $D^*$ obtained from $D$ by
   splitting off at most two arc-pairs at each $v \in S$, such that
   $D^*\langle K \rangle$ has a strong arc decomposition $(A_1, A_2)$;
3. (color compatibility at lifted $v$) for each splitting arc $s_1 s_2$ created
   by splitting off a pair $(s_1 v, v s_2)$ at some $v \in S$, the two
   original arcs $s_1 v, v s_2$ are *both* assigned the color of $s_1 s_2$ in
   $(A_1, A_2)$;
4. (residual coverage) for every $v \in S$ and every color $i \in \{1,2\}$
   such that $v$ has no in-arc (resp. out-arc) in $A_i$ after lifting,
   the unused arc budget at $v$ (i.e. the in-/out-arcs that were not split
   off) contains at least one in-arc and one out-arc not yet used by color
   $3-i$.

Then $D$ has a strong arc decomposition.

This is exactly the content of Lemma 2.5 with "$V_1$" relabeled "$S$", "$V_2$"
relabeled "$K$", and the split-structure hypothesis ($V_1$ independent, $V_2$
semicomplete) *dropped*. The proof of Lemma 2.5 as written goes through
verbatim because it never opens $V_2$.

**What CL1 buys you.** Any class $\mathcal{C}$ for which one can prove the
*existence* of a kernel $K$ and a 2-feasible family of splitting paths through
$V \setminus K$ satisfying hypothesis 2, together with $D^*\langle K \rangle$
already in a *solved* class (semicomplete, locally semicomplete, semicomplete
composition, split), inherits a strong-arc-decomposition theorem at the same
arc-connectivity threshold (3-arc-strong, modulo the local degree-3 condition
which 3-arc-strongness gives for free on the shell).

### What's missing — TODO (depth-read pass 2)

- (T1) The hypothesis "every $v \in S$ has in/out-degree $\ge 3$ with all
  neighbors in $K$" is what the paper has via $V_1$ independent. If we want
  $S$ not independent, we need an extra step: arcs *inside* $S$ must either be
  added to both color classes' "residual coverage" budget or treated by a
  recursive call. I do not yet see whether the existing proof tolerates a few
  $S$-internal arcs without breaking Lemma 2.4's accounting. Mark as **T1**.

- (T2) Color-compatibility hypothesis 3 above is what I read off the proof
  ("Lifting every splitting arc $s_1 s_2$, that is, replacing $s_1 s_2$ with
  the two arcs $s_1 t, t s_2$ in its corresponding splitting pair, we obtain
  two disjoint arc sets $A_1', A_2'$ of $A(D)$" — Lemma 2.5 proof, p. 5).
  The paper does *not* permit splitting the two arcs in a pair across colors.
  Whether a more permissive version (allow opposite colors on $s_1 v$ and
  $v s_2$ provided $v$ has a 2-cycle to some neighbor that compensates) is
  provable is open. Mark as **T2**.

- (T3) Lemma 3.4's "either $D_\mathcal{Q}\langle V_2 \rangle$ is 2-arc-strong
  or the cut-arc has a very restricted form" is the technical heart of
  Section 3 and it is genuinely semicomplete-specific. A class-agnostic
  analogue would need a substitute for the nice decomposition (Theorem 2.1).
  Mark as **T3** — this is the real obstacle to applying CL1 outside split
  digraphs.

---

## 2. Quasi-transitive: absorbed by BJG–Yeo 2020

**Yes.** Bang-Jensen–Huang's 1995 structure theorem: every strong
quasi-transitive $Q$ has the form $T[H_1,\dots,H_t]$ with $T$ strong
semicomplete on $t\ge 2$ vertices and each $H_i$ either a single vertex or a
(possibly non-strong) quasi-transitive digraph. BJG–Yeo 2020 (= Theorem 1.4 in
BJ–Wang) characterizes $T[H_1,\dots,H_t]$ with $T$ strong semicomplete,
$t\ge 2$, and *arbitrary* $H_i$: strong arc decomposition exists iff
2-arc-strong and not one of $S_4, C_3[\overline{K_2},\overline{K_2},K_2],
C_3[\overline{K_2},\overline{K_2},P_2], C_3[\overline{K_2},\overline{K_2},K_3]$.
The "arbitrary $H_i$" matters: no recursion needed inside the factors.
Recursion bottoms out at semicomplete (BJ–Yeo 2004) or non-strong (excluded by
2-arc-strong hypothesis). So every 3-arc-strong quasi-transitive digraph has a
strong arc decomposition.

**Roster update.** Quasi-transitive: **DONE**, absorbed under BJG–Yeo 2020.
Removed as a Track C1 candidate.

---

## 3. Ranked feasibility of the new candidate classes

I rank from most to least likely to produce a publishable positive theorem
within 6 months given CL1, the verifier, and the team's coding capacity.

**Rank 1. In-locally / out-locally semicomplete (ILS / OLS).** A digraph is
ILS if every pair of in-neighbors of any vertex is adjacent; OLS symmetric.
ILS strictly contains locally semicomplete and is **not** subsumed by
BJ–Huang 2012 (whose classification needs both-sided local semicompleteness).
Strong OLS digraphs admit a *round decomposition* on the out-side; CL1 fits
naturally with $K =$ a semicomplete in-component of that decomposition and
$S =$ the periphery, which inherits in-degree $\ge 3$ from 3-arc-strongness.
First sub-question: **does every 3-arc-strong OLS digraph admit a kernel $K$
inducing a semicomplete sub-multigraph with $V\setminus K$ satisfying the CL1
degree hypothesis?**

**Rank 2. Near-split digraphs.** Proposed precise definition: $D$ is
$(k,0)$-near-split if $V = V_1\dot\cup V_2$ with $V_2$ semicomplete, all arcs
between $V_1$ and $V_2$ unrestricted, and at most $k$ arcs inside $V_1$.
Target $(O(1),0)$-near-split. CL1's proof goes through modulo **T1** below
(residual coverage budget at vertices incident to the $V_1$-internal arcs).
First sub-question: **prove or disprove strong arc decomposition for
$(1,0)$-near-split 3-arc-strong digraphs.** Verifier can enumerate $n\le 10$.

**Rank 3. Eulerian 3-arc-strong digraphs with many minimum directed cuts.**
Overlaps Track B vehicle 2. A structural lemma here would assert: tight
3-cuts form a (near-)laminar system, so the induced 2-SAT instance is
satisfiable. EC-log already kills the high-$\lambda$ Eulerian regime. No
obvious kernel to lift to — strictly harder than 1, 2.

**Rank 4. Bounded independence number $\alpha(D)\le c$.** BJG (*Digraphs* 2nd
ed., Ch. 14) gives a covering by $c$ paths (Gallai–Milgram). Path interiors
are not in a solved class; needs more work to identify a kernel. Exploratory.

**Rank 5. Bounded directed treewidth / DAG-width.** No angle — the
obstruction is global (laminar tight-cut systems), not bag-local. Skip.

### Justification of top two

*Rank 1 (one-sided LS).* (a) The semicomplete kernel CL1 needs is already
present in the round decomposition, no new structural theorem required. (b)
Strictly extends BJ–Huang 2012; a positive theorem here is a publishable
short paper. (c) ILS / OLS digraphs of order $\le 8$ are enumerable, so the
verifier can test the candidate hypothesis immediately.

*Rank 2 (near-split).* (a) Proof technique transfers from BJ–Wang modulo T1.
(b) Parametric class: "how near to split can we go" generates a sequence of
theorems. (c) Either outcome is a win — a positive theorem extends BJ–Wang,
a $(2,0)$-near-split 3-arc-strong counterexample is a Track B publishable.

---

## 4. What I need from the Coder and Auditor

- **Coder, benchmark 1.** Enumerate (canonical-form, `nauty`) all
  2-arc-strong ILS digraphs of order $\le 8$; run ILP verifier; report all
  UNSAT instances. Hypothesis: only obstructions are squares of even directed
  cycles. Confirms or kills the rank-1 program.
- **Coder, benchmark 2.** Enumerate $(1,0)$-near-split 2-arc-strong digraphs
  with $|V_2|\le 5$, $|V_1|\le 4$. On UNSAT cases, tag whether the
  $V_1$-internal arc appears in the minimal unsat core.
- **Coder, benchmark 3.** On the four BJG–Yeo 2020 composition exceptions,
  extract the minimal unsat core over cut/color constraints; report whether
  the same laminar 2-SAT pattern appears in all four. Seeds Track B vehicle 3.
- **Auditor, statement check.** Verify CL1 (§1) is implied by Lemma 2.5 +
  Corollary 2 of BJ–Wang once $V_1$ independent / $V_2$ semicomplete are
  dropped from the *statement* (kept in the reduction target). Specifically:
  does the proof of Lemma 2.5 invoke $V_2$ semicomplete anywhere besides
  Theorem 2.3?
- **Auditor, T2 check.** In Lemma 2.5, both arcs of a split-off pair inherit
  the color of the splitting arc. Confirm this is necessary, or produce a
  small counterexample showing it is. Decides whether T2 (§1) is open.
- **Auditor, BJ–Huang absorption.** Independently confirm §2's argument that
  strong quasi-transitive digraphs are BJG–Yeo compositions and inherit the
  strong arc decomposition theorem at 3-arc-strongness, before we strike
  quasi-transitive from the roster.
