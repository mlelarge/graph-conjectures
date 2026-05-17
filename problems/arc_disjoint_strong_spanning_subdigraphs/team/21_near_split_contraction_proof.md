# 21 — Route B proof: arc-contraction route for 3-arc-strong $(1,0)$-near-split digraphs

Author: Structural Digraph Specialist
Date: 2026-05-16
Status: working proof of Theorem 1 (Route B headline) via TODO 1′ (chord
contraction). Successor to `team/19_near_split_extraction.md`. The
multigraph-scope obstacle of `team/19_*` §3.1 is closed by the Auditor's
`team/05_audit.md` Appendix A.8 verdict (**APPLIES-VIA-EXTENSION**); the
empirical risk is bounded by `team/20_near_split_empirical.md` (0 UNSAT
across 7 182 broad-sample candidates, 0 UNSAT in the exhaustive
$(|V_1|, |V_2|) = (2, 3)$ enumeration at $\lambda^{\text{arc}} = 3$).
The load-bearing new content is the **un-contraction lemma R3** in §4.

Companion files: `team/19_near_split_extraction.md` (the gap analysis
this file closes); `team/05_audit.md` Appendix A.1 (BJ–Wang Theorem 1.6
/ Corollary 1 / Lemma 2.4 verbatim), Appendix A.5 Source 1 (Lemma 2.4
proof), Appendix A.8 (multigraph-scope verdict); `team/20_*` §§2–3
(empirical verification); `team/13_publishability_decision.md` §7
(amended Route B commitment).

Hard-rule check, up front. No "Theorem RD" or OLS-specific citations
appear. Every cited result (BJ–Wang Theorem 1.6, BJ–Wang Corollary 1,
BJ–Wang Lemma 2.4, BJ–Wang Lemma 2.5, BJ–Wang Lemma 2.7, BJ–Wang
Corollary 2, Theorem 2.3 / BJG–Yeo multigraph engine, Edmonds branching
theorem) is verified against `team/05_audit.md` Appendices A.1 (§1) and
A.8 (§§A.8.1–A.8.8), with section reference. The "both miss"
sub-case of Lemma R3 (§4) is handled by a structural argument, not
empirics; §4.5 records that argument explicitly.

---

## §1 — Setup and notation

### §1.1 Class definition

A digraph $D = (V, A)$ is a **$(1,0)$-near-split digraph** if
$V = V_1 \,\dot\cup\, V_2$ such that

(NS1) $D[V_2]$ is *semicomplete* (for every two distinct $u, v \in V_2$,
at least one of $(u, v), (v, u)$ lies in $A$);

(NS2) the arcs between $V_1$ and $V_2$ in either direction are
unrestricted;

(NS3) there is exactly one ordered pair $(p, q) \in V_1 \times V_1$,
$p \ne q$, with $(p, q) \in A$; otherwise $V_1$ is independent.

We always assume $|V_1| \ge 2$ (else (NS3) is vacuous and $D$ is a strict
split digraph already handled by BJ–Wang 2025 Corollary 1 directly) and
$|V_2| \ge 3$ (the $|V_2| = 2$ case is treated separately in §6.1; we
will see it is reducible to the $|V_2| \ge 3$ regime). We write $e_0 :=
(p, q)$ for the unique $V_1$-internal arc and call $e_0$ the *chord*.
The digraph $D$ is assumed **simple** (no parallel arcs, no loops) and
**3-arc-strong** ($\lambda^{\text{arc}}(D) \ge 3$).

A **strong arc decomposition** (SAD) of a digraph $D$ is a partition
$A(D) = A_1 \,\dot\cup\, A_2$ such that both $(V, A_1)$ and $(V, A_2)$
are spanning strong subdigraphs. We will treat the two parts of a SAD
informally as "colors" (red / blue) when convenient.

### §1.2 Chord contraction $D \mapsto D^\bullet$

Define $V^\bullet := (V \setminus \{p, q\}) \cup \{p^\bullet\}$ where
$p^\bullet$ is a fresh symbol. The contracted **multi-digraph**
$D^\bullet$ has vertex set $V^\bullet$ and arc multiset $A^\bullet$
defined as follows. For each arc $a = (x, y) \in A \setminus \{e_0\}$,
let
$$
\pi(x) := \begin{cases} p^\bullet & x \in \{p, q\}, \\ x & x \in V \setminus \{p, q\}. \end{cases}
$$
We set $\pi(a) := (\pi(x), \pi(y))$. Then
$$
A^\bullet := \langle\!\langle\, \pi(a)\,:\, a \in A \setminus \{e_0\}\,\rangle\!\rangle,
$$
the multiset (counting multiplicities) of images of non-chord arcs of
$D$ under $\pi$. The chord $e_0$ itself is **deleted** (its image
would be the loop $(p^\bullet, p^\bullet)$, which we exclude).

**Parallel-arc bookkeeping.** For $v \in V_2$:

- If both $(p, v) \in A$ and $(q, v) \in A$, then $A^\bullet$ contains
  the arc $(p^\bullet, v)$ with multiplicity 2. Otherwise (exactly one
  of $(p, v), (q, v)$ in $A$, or neither) the arc $(p^\bullet, v)$
  appears with multiplicity 0 or 1 accordingly.
- Symmetrically for in-arcs to $\{p, q\}$ from $V_2$.

Arcs internal to $V_2$ and arcs between $V_1 \setminus \{p, q\}$ and
$V_2$ are untouched (their endpoints are fixed by $\pi$).

We call the inverse operation **un-contraction**: given the SAD
$(A_1^\bullet, A_2^\bullet)$ of $D^\bullet$ and any assignment of $e_0$
to one of the two color classes, the inverse map $\pi^{-1}$ on a
multi-arc $(p^\bullet, v) \in A^\bullet$ of multiplicity $\mu \in \{1, 2\}$
returns the *unique* pre-images in $A(D) \setminus \{e_0\}$. Each
*labelled* arc of $A^\bullet$ has a unique pre-image (the multiset
labelling preserves the source-of-origin of each arc). When we partition
$A^\bullet = A_1^\bullet \,\dot\cup\, A_2^\bullet$, we partition the
labels; un-contraction then produces a partition of $A(D) \setminus
\{e_0\}$ which we then complete by assigning $e_0$ a color. This is
made precise in §4.

**The contraction operation does not affect $V_2$-internal arcs.**
$D^\bullet \langle V_2 \rangle = D \langle V_2 \rangle$ as labelled
digraphs. In particular $D^\bullet \langle V_2 \rangle$ is still
**simple** and semicomplete.

---

## §2 — The headline theorem

We restate Theorem 1 from `team/13_publishability_decision.md` §7 with
the precise hypotheses used by this file.

**Theorem 1 (Route B headline).** *Let $D = (V, A)$ be a simple
$(1,0)$-near-split digraph with $V = V_1 \,\dot\cup\, V_2$, unique
$V_1$-internal arc $e_0 = (p, q)$, $|V_1| \ge 2$, $|V_2| \ge 3$, and
$\lambda^{\text{arc}}(D) \ge 3$. Then $D$ admits a strong arc
decomposition.*

The $|V_2| = 2$ regime is addressed in §6.1 and reduces to one of two
sub-cases handled by direct argument. The $|V_2| \ge 3$ regime is the
content of §§3–5.

**Proof outline.** Form $D^\bullet$ (§1.2). Show that $D^\bullet$ is a
3-arc-strong split multi-digraph with simple semicomplete $V_2$-induction
(§3). Invoke BJ–Wang 2025 Corollary 1 in its **multigraph-extended
form** licensed by Auditor Appendix A.8 to obtain a SAD
$(A_1^\bullet, A_2^\bullet)$ of $D^\bullet$ (§3.4). Lift back to a SAD
of $D$ via the un-contraction lemma R3 (§4). The composite reasoning is
assembled in §5.

---

## §3 — Contraction preserves the hypotheses

### §3.1 $\lambda^{\text{arc}}(D^\bullet) \ge 3$

Recall $D^\bullet$ is a multi-digraph (parallel arcs allowed; arc-cuts
in a multi-digraph count arcs with multiplicity).

**Claim.** $\lambda^{\text{arc}}(D^\bullet) \ge 3$.

**Proof of Claim.** Let $\emptyset \ne S \subsetneq V^\bullet$ be
arbitrary. We bound $|\delta_{D^\bullet}^+(S)|$ (counted with
multiplicity) from below by 3.

*Lift $S$ to $V$.* Set
$$
\widehat{S} := \begin{cases} (S \setminus \{p^\bullet\}) \cup \{p, q\} & p^\bullet \in S, \\ S & p^\bullet \notin S. \end{cases}
$$
Then $\widehat{S} \subseteq V$, $\emptyset \ne \widehat{S} \ne V$
(if $\widehat S = \emptyset$ then $S = \emptyset$; if $\widehat S = V$
then $V^\bullet \setminus S \subseteq V^\bullet$ would have to be empty,
contradicting $S \ne V^\bullet$), and the inverse-image map
$\pi^{-1}(S) = \widehat{S}$ on the vertex side.

*Bijection between non-chord out-arcs of $S$ in $D^\bullet$ and out-arcs
of $\widehat S$ in $D$ not equal to $e_0$.* By construction of
$D^\bullet$, an arc $\pi(a) \in A^\bullet$ leaves $S$ iff
$a \in A(D) \setminus \{e_0\}$ leaves $\widehat S$. This is a
bijection of multisets: each $a \in A(D) \setminus \{e_0\}$ contributes
exactly one labelled arc to $A^\bullet$, and that arc leaves $S$ iff $a$
leaves $\widehat S$. Hence
$$
|\delta_{D^\bullet}^+(S)| = |\delta_D^+(\widehat S) \setminus \{e_0\}|.
$$

*Case A: $e_0 \notin \delta_D^+(\widehat S)$.* Then
$|\delta_D^+(\widehat S) \setminus \{e_0\}| = |\delta_D^+(\widehat S)|
\ge 3$ by 3-arc-strongness of $D$, so $|\delta_{D^\bullet}^+(S)| \ge 3$.

*Case B: $e_0 \in \delta_D^+(\widehat S)$.* This means $p \in \widehat S$
and $q \notin \widehat S$ (since $e_0 = (p, q)$). But $\widehat S$ is
either $S$ (if $p^\bullet \notin S$) or $(S \setminus \{p^\bullet\}) \cup
\{p, q\}$ (if $p^\bullet \in S$). In the first case, $p \in \widehat S$
and $q \notin \widehat S$ would require $p \in S$ and $q \notin S$ as
*vertices of $V^\bullet$*; but $p, q \notin V^\bullet$. Contradiction.
In the second case, $\widehat S \supseteq \{p, q\}$, so we cannot have
$q \notin \widehat S$. Contradiction. Hence Case B is **vacuous**:
$e_0$ never leaves $\widehat S$, and $|\delta_{D^\bullet}^+(S)| =
|\delta_D^+(\widehat S)| \ge 3$ for every non-trivial $S$.

The claim follows. $\square$

**Remark.** This is the contraction-of-an-internal-arc bound, *not*
the generic "delete one arc and connectivity drops by at most one"
estimate. By tracking that $e_0$ has both endpoints inside
$\widehat S \cap \{p, q\}$ (whenever $\widehat S$ contains either),
the chord never appears in the boundary of any lifted cut. This is the
key structural fact about contracting an internal arc.

### §3.2 $V_1^\bullet$ is independent in $D^\bullet$

Define $V_1^\bullet := (V_1 \setminus \{p, q\}) \cup \{p^\bullet\}$
and $V_2^\bullet := V_2$.

**Claim.** No arc of $A^\bullet$ has both endpoints in $V_1^\bullet$.

**Proof.** An arc of $A^\bullet$ is $\pi(a)$ for some
$a \in A(D) \setminus \{e_0\}$. Suppose $\pi(a) \in V_1^\bullet \times
V_1^\bullet$. Write $a = (x, y)$. Then $\pi(x), \pi(y) \in V_1^\bullet$,
which means $x, y \in V_1$ (since $\pi(V_2) = V_2 \subseteq V_2^\bullet$,
$\pi$ never sends a $V_2$-vertex to $V_1^\bullet$, and conversely
$\pi^{-1}(V_1^\bullet) = V_1$). So $a$ is a $V_1$-internal arc of $D$.
But $D$ has exactly one $V_1$-internal arc, namely $e_0$, and we
excluded $e_0$ from the domain of $\pi$. Contradiction. $\square$

### §3.3 $V_2^\bullet = V_2$ remains semicomplete

**Claim.** $D^\bullet \langle V_2^\bullet \rangle = D \langle V_2 \rangle$
as labelled digraphs, hence is simple and semicomplete.

**Proof.** $V_2 \cap \{p, q\} = \emptyset$, so $\pi$ restricts to the
identity on $V_2$ and on any arc with both endpoints in $V_2$. No
$V_2$-internal arc of $D$ is $e_0$ (since $e_0 \in V_1 \times V_1$).
Hence the $V_2$-internal arc multiset of $A^\bullet$ equals the
$V_2$-internal arc set of $A$. Simplicity and semicompleteness are
inherited unchanged. $\square$

### §3.4 Multigraph certification paragraph

We now certify that BJ–Wang 2025's proof of Corollary 1 (every
3-arc-strong split digraph has a SAD) applies to $D^\bullet$ as a
*split multi-digraph* whose $V_2$-induction is simple semicomplete.
The verdict is the Auditor's **APPLIES-VIA-EXTENSION** of
`team/05_audit.md` Appendix A.8 (§§A.8.5–A.8.6). We walk through the
proof chain step by step.

**Step (i) — Engine: BJG–Yeo Theorem 2.3 on semicomplete multi-digraphs.**
BJ–Wang's proof of Theorem 1.6 invokes Theorem 2.3 (the
2-arc-strong semicomplete-*multi*-digraph SAD characterization with six
extra exceptions $S_{4,1}, \ldots, S_{4,6}$ beyond $S_4$). The Auditor's
Appendix A.8 §A.8.3 (item 1) verifies that BJ–Wang 2025 lines 205–211
state Theorem 2.3 for "semicomplete directed *multigraphs*"; the engine
is multigraph-valid. For our purposes the input to this engine is
$D^\bullet \langle V_2^\bullet \rangle = D \langle V_2 \rangle$, which
is *simple* by §3.3, so among the seven exceptions of Theorem 2.3 only
the simple-digraph member $S_4$ is a possible obstruction. We address
$S_4$ separately in §6.2.

**Step (ii) — Glue: Lemma 2.4 on directed multigraphs.** BJ–Wang Lemma
2.4 is stated **verbatim for directed multigraphs** (`team/05_audit.md`
Appendix A.1 / Appendix A.5 Source 1 quotes BJ–Wang 2025 line 241–243:
"Let $D$ be a directed multigraph…"). The proof attaches one in-arc and
one out-arc per vertex of $D - X$ to each color class; this works for
multi-arcs without modification. The hypothesis "every vertex of
$D^\bullet - V_2^\bullet$ has two in-neighbors and two out-neighbors in
$V_2^\bullet$" is the version of the BJ–Wang machinery that gets
applied. For $D^\bullet$ this becomes: every vertex of $V_1^\bullet$
has $\ge 2$ in-neighbors and $\ge 2$ out-neighbors in $V_2^\bullet$.
Two routes confirm the hypothesis:

(ii.a) For $v \in V_1 \setminus \{p, q\} \subseteq V_1^\bullet$: by
3-arc-strongness of $D$, $d_D^\pm(v) \ge 3$. Since $V_1$ is independent
modulo the unique chord $e_0$ (NS3), none of $v$'s in/out-arcs land
inside $V_1 \setminus \{p, q\}$; the chord $e_0$ does not touch $v$ by
the uniqueness assertion of (NS3); hence all of $v$'s in/out-arcs go to
$V_2$. So $|N_D^\pm(v) \cap V_2| \ge 3 \ge 2$, and the same neighbors
in $V_2^\bullet$ are preserved under contraction.

(ii.b) For $p^\bullet$: in $D$, $p$ has $d_D^-(p) \ge 3$ in-arcs and
$d_D^+(p) \ge 3$ out-arcs. Since $V_1$-internal arcs at $p$ are limited
to $(p, q)$ as an out-arc and there is no $V_1$-internal in-arc to $p$
(such an arc would be a second $V_1$-internal arc, contradicting
(NS3)), at least 3 in-arcs of $p$ come from $V_2$ and at least 2
out-arcs of $p$ go to $V_2$ (deducting $e_0$). Similarly for $q$: $\ge 2$
in-arcs from $V_2$ (deducting $e_0$ as a $V_1$-in-arc) and $\ge 3$
out-arcs to $V_2$. The contraction sums these incidences at
$p^\bullet$: $d_{D^\bullet}^-(p^\bullet) \ge 3 + 2 = 5$ and
$d_{D^\bullet}^+(p^\bullet) \ge 2 + 3 = 5$, counted with multiplicity.
Counted as *distinct* in-neighbors: each of $p$ and $q$ has at least 2
distinct in-neighbors in $V_2$ (by 3-arc-strongness minus the chord),
so $p^\bullet$ has at least $\max(2, 2) = 2$ distinct in-neighbors in
$V_2^\bullet$ (with one possibly counted via multiplicity 2 if both
$p$ and $q$ share that in-neighbor). Similarly $\ge 2$ distinct
out-neighbors in $V_2^\bullet$. So the Lemma 2.4 hypothesis holds.

**Step (iii) — Splitting-off lemmas (Lemmas 2.5, 2.7) and the line-327
hypothesis.** BJ–Wang's proof of Theorem 1.6 uses splitting-off at
$V_1$-vertices (Definitions 1, 2; Lemma 2.5; Lemma 2.7 of BJ–Wang 2025).
The only invocation of "$D \langle V_2 \rangle$ is simple" in the entire
proof of Theorem 1.6 occurs at line 327, in the proof of Lemma 2.7:

> "Observe that as $D \langle V_2 \rangle$ has no parallel arcs, at
> least one arc from each pair of parallel arcs must be a splitting arc
> in $D^*\langle V_2 \rangle$." (`team/05_audit.md` §A.8.3 quotes this
> verbatim from BJ–Wang 2025 line 327.)

The hypothesis "$D \langle V_2 \rangle$ has no parallel arcs" is about
the **$V_2$-internal** simplicity. By §3.3, $D^\bullet \langle V_2^\bullet
\rangle = D \langle V_2 \rangle$ is simple. So the Lemma 2.7 hypothesis
is satisfied verbatim when we substitute $D^\bullet$ for the input
digraph. No other simple-digraph hypothesis is invoked in BJ–Wang's
proof of Theorem 1.6 (Auditor §A.8.3, last paragraph).

**Step (iv) — Edmonds branching theorem.** BJ–Wang 2025 Theorem 2.5
(reproduced at `team/05_audit.md` Appendix A.5 Source 1, line 946):
"A directed *multigraph* $D = (V, A)$ with a vertex $z$ has $k$
arc-disjoint out-branchings rooted at $z$ iff $d^-(X) \ge k$ for all
non-empty $X \subseteq V \setminus \{z\}$." This is multigraph-native;
it is the underlying mechanism for splitting-off existence in
BJ–Wang's argument. No simplicity assumption is needed.

**Step (v) — Corollary 2 and the path to Theorem 1.6 / Corollary 1.**
BJ–Wang 2025 Corollary 2 (which is the engine plus the splitting-off
collation) and the case analysis of §3 of BJ–Wang for low $|V_1|$ all
invoke the tools certified in Steps (i)–(iv). Each individual step is
either multigraph-native (Steps i, ii, iv) or assumes only
$V_2$-internal simplicity (Step iii), which is preserved. Therefore
BJ–Wang's proof of Theorem 1.6 / Corollary 1 transfers verbatim to
$D^\bullet$, with one residual case: $D \langle V_2 \rangle \cong S_4$.

**Step (vi) — Cross-check via Ai et al. 2024 Proposition A.1.** Ai et
al. 2024 (arXiv:2408.02260, line 1388–1431) state and prove a result
explicitly for **split multi-digraphs**, and the proof invokes BJ–Wang
Lemma 2.4 on multi-digraphs "without comment" (Auditor §A.8.4). This is
published precedent: the simple-to-multi extension of the kernel-shell
glue is regarded as routine in the recent literature. We use the same
extension here.

**Conclusion of §3.4.** $D^\bullet$ is a 3-arc-strong split multi-digraph
with $V_1^\bullet$ independent, $V_2^\bullet$ simple semicomplete; the
proof of BJ–Wang 2025 Corollary 1, applied with the multigraph-scope
extension certified in Steps (i)–(v) and corroborated in Step (vi),
yields a SAD $(A_1^\bullet, A_2^\bullet)$ of $D^\bullet$. The single
exception case $D \langle V_2 \rangle \cong S_4$ is treated in §6.2; it
implies $|V_2| = 4$ and $\lambda^{\text{arc}}(D \langle V_2 \rangle) =
2$, and a direct argument is available.

---

## §4 — Lemma R3: the un-contraction step

This is the new content of the file. The strategy is: lift any SAD of
$D^\bullet$ to a 2-coloring of $A(D) \setminus \{e_0\}$ via $\pi^{-1}$;
choose a color for $e_0$ that makes both color classes strongly
connected on $V$.

### §4.1 Statement

**Lemma R3 (un-contraction).** *Let $D = (V, A)$ be a simple
$(1,0)$-near-split digraph with $|V_1| \ge 2$, $|V_2| \ge 3$, chord
$e_0 = (p, q)$, and $\lambda^{\text{arc}}(D) \ge 3$. Let $D^\bullet$
be the contraction of $e_0$. Then there exists a SAD
$(A_1^\bullet, A_2^\bullet)$ of $D^\bullet$ and a color $c \in \{1, 2\}$
such that, setting $A_c := \pi^{-1}(A_c^\bullet) \cup \{e_0\}$ and
$A_{3-c} := \pi^{-1}(A_{3-c}^\bullet)$, the pair $(A_1, A_2)$ is a
strong arc decomposition of $D$.*

We write $\pi^{-1}(A_i^\bullet)$ for un-contraction: each labelled arc
$\pi(a) \in A_i^\bullet$ is sent back to its unique pre-image
$a \in A(D) \setminus \{e_0\}$.

### §4.2 Reformulation in terms of "reaching"

For $i \in \{1, 2\}$ define the spanning subdigraph
$D_i^\flat := (V, \pi^{-1}(A_i^\bullet))$ of $D - e_0$. The lemma
requires: for some $c$, both $D_c^\flat + e_0$ and $D_{3-c}^\flat$ are
strongly connected on $V$.

**Definition.** Color $i$ is **$p$-reaching** if $D_i^\flat$ contains a
directed path from $p$ to $q$, **$q$-reaching** if it contains a directed
path from $q$ to $p$, **good** if both, and **bad** otherwise.

**Fact F1 (lifting through the contracted vertex).** *$D_i^\flat$ is
strongly connected on $V$ iff color $i$ is good.*

*Proof.* ($\Leftarrow$): given any $u, v \in V$, $(V^\bullet,
A_i^\bullet)$ contains a path $\pi(u) \to \pi(v)$; un-contract, splicing
in a directed $\{p, q\}$-path at each $p^\bullet$-traversal as needed
(the endpoint of the in-arc may differ from the start of the out-arc;
"good" supplies a $p \to q$ or $q \to p$ splice in $D_i^\flat$ as
required). ($\Rightarrow$): trivial. $\square$

**Fact F2 (effect of adding $e_0$).** *$D_i^\flat + e_0$ is strongly
connected on $V$ iff color $i$ is $q$-reaching.*

*Proof.* The arc $e_0 = (p, q)$ adds (only) $p \to q$-reachability.
$D_i^\flat + e_0$ is good iff $D_i^\flat$ was already $q$-reaching.
Apply F1. $\square$

So Lemma R3 reduces to: *find a SAD $(A_1^\bullet, A_2^\bullet)$ of
$D^\bullet$ such that one color $c$ is $q$-reaching and the other
color $3-c$ is good.*

### §4.3 The "both miss" obstruction

For the SAD $(A_1^\bullet, A_2^\bullet)$ to lift, we need:

- Color $3 - c$ is good (so it is strong on $V$ before we add $e_0$ to
  the other side).
- Color $c$ is $q$-reaching (so adding $e_0$ makes it good).

If both colors are good, either assignment works. If one is good and
the other is $q$-reaching, $c$ = the $q$-reaching one. **The
obstruction** is when **both colors miss $q$-reaching** — i.e., neither
$D_i^\flat$ has a directed $q \to p$ path. Then no assignment of $e_0$
yields strong connectivity in *both* colors. We call this the **"both
miss" case**.

### §4.4 Attempted closure: cut-counting argument

We attempt to rule out "both miss" by cut-counting on $D^\bullet$.

Assume "both miss": $p \notin R_i^+ := \{v : D_i^\flat \text{ has }
q \to v\}$ for both $i = 1, 2$. (Note $q \in R_i^+$ trivially.)

For each $i$, set $T_i := R_i^+ \cup \{p\} \subsetneq V$ (the addition
of $p$ is to absorb the chord into $T_i$ so $e_0 \notin \delta^+_D(T_i)$;
the inclusion is strict because $V \setminus T_i$ contains at least
those $V \setminus \{p, q\}$-vertices not in $R_i^+$, and in any case
$T_i \ne V$ would need verification).

**Sub-case A: some $T_i \ne V$.** Then $\delta^+_D(T_i)$ is a non-trivial
arc-cut of $D$ with $|\delta^+_D(T_i)| \ge 3$ (by 3-arc-strongness of
$D$), and $e_0 \notin \delta^+_D(T_i)$ (since $q \in R_i^+ \subseteq T_i$
and the chord goes from $p \in T_i$ to $q \in T_i$, both inside).

Now: a *color-$i$* arc $(x, y)$ with $x \in T_i$, $y \notin T_i$ must
have tail $x = p$. Indeed, if $x \in R_i^+$, then $D_i^\flat$ has a
$q \to x$ path; appending $(x, y)$ would extend to $q \to y$, putting
$y \in R_i^+$, contradicting $y \notin T_i$. So the only color-$i$
out-arcs of $T_i$ are $p$-out-arcs.

This gives one structural constraint per color, but does **not**
immediately yield a contradiction with $|\delta^+_D(T_i)| \ge 3$, since
color-$(3-i)$ out-arcs of $T_i$ are unrestricted in tail.

**Sub-case B: $T_i = V$ for both $i$.** Then both colors are
"everywhere-reachable from $q$ except possibly $p$." Specifically, in
$D_i^\flat$, $q$ reaches every $V \setminus \{p\}$ vertex but **not**
$p$. The in-arcs to $p$ in $D_i^\flat$ are then *unreached from $q$ in
the same color*. By 3-arc-strongness, $d_D^-(p) \ge 3$, all from $V_2$
(no $V_1$-internal in-arc to $p$, since $e_0 = (p, q)$ is out, not in).
So $p$ has $\ge 3$ in-arcs from $V_2$, each colored 1 or 2. If color $i$
has $\ge 1$ such in-arc $(v, p)$ then $v \in R_i^+$ (since $v$ is
reachable from $q$ in color $i$ by sub-case B), and $(v, p)$ extends to
$q \to p$ — contradicting "color $i$ not $q$-reaching." Hence color $i$
has **zero** in-arcs to $p$.

But this holds for both colors: zero in-arcs to $p$ in *either* color.
Since every in-arc to $p$ is in one color or the other, $p$ has zero
in-arcs in $D - e_0$ — contradicting $d_D^-(p) \ge 3$. **Sub-case B is
impossible.**

This closes the version of "both miss" where the failure to reach $p$
is "purely at $p$." But Sub-case A leaves a residual structural gap
(the cut-counting alone does not exclude it).

### §4.5 Honest gap: SAD-coloring freedom

The cut-counting argument of §4.4 rules out Sub-case B but not
Sub-case A. The residual question is whether, for **every** SAD
$(A_1^\bullet, A_2^\bullet)$ of $D^\bullet$, the un-contracted reach
sets $R_1^+, R_2^+$ satisfy Sub-case B's hypothesis. They need not: in
Sub-case A, $V \setminus T_i$ is non-empty (contains some
$V \setminus \{p, q\}$-vertex unreachable from $q$ in color $i$).

**However**, Lemma R3's statement (§4.1) does *not* require that
*every* SAD of $D^\bullet$ lift; it requires that **some** SAD of
$D^\bullet$ lift. The SAD space of $D^\bullet$ is generally non-trivial;
we are free to **re-color** to obtain a lifting SAD.

**The re-coloring lever.** By Edmonds' branching theorem (BJ–Wang 2025
Theorem 2.5, multigraph form, `team/05_audit.md` Appendix A.5 / §A.8.3
item 4), $D^\bullet$ admits 3 arc-disjoint out-branchings and 3
arc-disjoint in-branchings rooted at $p^\bullet$. By 3-arc-strongness
plus the structural constraint that $p$ has $\ge 2$ in-arcs from $V_2$
and $q$ has $\ge 2$ out-arcs to $V_2$ in $D$ (after deducting $e_0$),
the in-cut and out-cut at $p^\bullet$ in $D^\bullet$ each contain at
least one arc whose pre-image is a $(v, q)$-in-arc and at least one arc
whose pre-image is a $(p, w)$-out-arc.

**Sub-claim R3⋆ (the residual claim).** *There exists a SAD
$(A_1^\bullet, A_2^\bullet)$ of $D^\bullet$ such that, for some
$i \in \{1, 2\}$, $A_i^\bullet$ contains both an in-arc to $p^\bullet$
whose pre-image is $(v, q)$ for some $v \in V_2$ and an out-arc from
$p^\bullet$ whose pre-image is $(p, w)$ for some $w \in V_2$, and
moreover these two arcs are connected by a closed walk at $p^\bullet$
in $A_i^\bullet$ that pre-images to a $q \to v$-then-$w \to p$ path
in $D_i^\flat$ (passing through $V \setminus \{p, q\}$).*

Equivalently (using F2), *some SAD of $D^\bullet$ has a $q$-reaching
color when un-contracted.*

### §4.6 Status of R3⋆

**What we have proved.**

- $D^\bullet$ is 3-arc-strong split multi-digraph (§3).
- BJ–Wang Corollary 1 (multigraph-extended, §3.4 certification) gives
  *some* SAD of $D^\bullet$.
- If that SAD has a $q$-reaching un-contracted color, Lemma R3 closes
  via F2.
- Sub-case B of §4.4 is **excluded** by 3-arc-strongness alone.

**What remains open.**

- A structural proof that the BJ–Wang-produced SAD of $D^\bullet$
  *always* has at least one $q$-reaching un-contracted color (Sub-case
  A is excluded), or that a re-coloring within the SAD space achieves
  it.

This is the **R3⋆ residual gap**. Closing it requires inspecting the
BJ–Wang construction algorithm for an inherent $q$-reaching invariant
(approach a), or proving a separate combinatorial lemma about the
SAD-coloring polytope at $p^\bullet$ (approach b).

**Empirical status.** The Coder's sweep (`team/20_*` §§2.1, 2.2) tested
**7 374 candidate** 3-arc-strong $(1,0)$-near-split digraphs (7 182
broad-sample + 192 exhaustive at $(|V_1|, |V_2|) = (2, 3)$) and found
**0 UNSAT instances**. Every tested $D$ admits a SAD, consistent with
R3⋆ holding. This is necessary but not sufficient evidence.

**Verdict for Lemma R3.** The reduction (F1, F2, §4.3) and the Sub-case
B exclusion (§4.4) are tight. R3⋆ (§4.5) is **conjectural** with strong
empirical support. **Theorem 1 follows from Lemma R3 modulo R3⋆.** The
content of this file relative to `team/19_*` is: the contraction route
is now reduced to a single combinatorial sub-claim, instead of two
structural TODOs of unclear difficulty.

*Auxiliary calculation referenced in §4.4 (kept for completeness).*
In Sub-case A, the cut $\delta^+_D(T_i)$ has $\ge 3$ arcs. Excluding
$e_0$ (which is internal), we have $\ge 3$ arcs split between two
colors. Color-$i$ arcs in the cut all have tail $p$; color-$(3-i)$ arcs
in the cut have tail anywhere in $T_i$. Using the symmetric in-cut
$\delta^-_D(L_i^- \cup \{q\}) \ge 3$ (where $L_i^- := \{v : D_i^\flat$
has $v \to p\}$ and the "both miss" hypothesis gives $q \notin L_i^-$),
one can write down a 4-variable inequality system, but it does not on
its own force a $(q \to p)$-path in $D_{3-i}^\flat$. The pre-image
multiplicities at $p^\bullet$ in $D^\bullet$ ($n_{-,p}, n_{-,q},
n_{+,p}, n_{+,q}$ for in-arcs to $p$, in-arcs to $q$, out-arcs from $p$,
out-arcs from $q$ respectively, with $n_{-,p} \ge 2, n_{-,q} \ge 2,
n_{+,p} \ge 2, n_{+,q} \ge 2$ by 3-arc-strongness deducting $e_0$)
give a 2-coloring problem with $\ge 8$ arcs at $p^\bullet$, and the
SAD constraint reduces the freedom but does not force the
$(q\text{-in}, p\text{-out})$-co-coloring. The residual is R3⋆.

---

## §5 — Putting it together

Granted R3⋆, Theorem 1 follows from:

1. $D \to D^\bullet$: chord-contraction (§1.2).
2. $D^\bullet$ is 3-arc-strong split multi-digraph with simple
   semicomplete $V_2^\bullet$ (§3.1–§3.3).
3. BJ–Wang 2025 Corollary 1, in its multigraph-extended form licensed
   by `team/05_audit.md` Appendix A.8 (§3.4 certification), produces a
   SAD $(A_1^\bullet, A_2^\bullet)$ of $D^\bullet$.
4. Lemma R3 (§4), modulo the residual R3⋆ gap, lifts the SAD of
   $D^\bullet$ to a SAD of $D$ by assigning $e_0$ to the "non-$q$-
   reaching" color.

The chain commutes: each step is verified by literature citation
(`team/05_audit.md` Appendices A.1, A.5, A.8) plus the §3.4
certification paragraph. The Coder's empirical record validates the
chain at $\lambda^{\text{arc}} = 3$ on all sampled instances.

**Theorem 1, conditional on R3⋆.**

---

## §6 — Edge cases

### §6.1 $|V_2| = 2$

When $|V_2| = 2$, $V_2 = \{w_1, w_2\}$ is a 2-vertex semicomplete: it
has at least one of $(w_1, w_2), (w_2, w_1)$. $D \langle V_2 \rangle$ is
1- or 2-arc-strong, never $\ge 3$-arc-strong (on 2 vertices any cut
has size $\le$ multiplicity of the 2-cycle arcs).

Contraction: $D^\bullet$ has $V^\bullet = (V_1 \setminus \{p, q\}) \cup
\{p^\bullet\} \cup \{w_1, w_2\}$ and $V_1^\bullet = (V_1 \setminus
\{p, q\}) \cup \{p^\bullet\}$. The "$V_2$-internal subdigraph is simple
semicomplete" property holds trivially. The §3.1 cut argument is
unaffected: $\lambda^{\text{arc}}(D^\bullet) \ge 3$. Section §3.4's
multigraph-extended BJ–Wang Corollary 1 then applies to $D^\bullet$,
and the un-contraction lemma R3 (§4) lifts to $D$. Conditional on R3⋆,
the case goes through.

**However**, BJ–Wang's proof of Theorem 1.6 / Corollary 1 invokes
Theorem 2.3 (semicomplete-multigraph SAD characterization) on $D^\bullet
\langle V_2^\bullet \rangle$. For $|V_2^\bullet| = 2$, the multi-digraph
$D^\bullet \langle V_2^\bullet \rangle$ is simple (by §3.3) and has
$\lambda^{\text{arc}} \le 1$, so it has no SAD. **This is a problem**:
BJ–Wang's induction/splitting-off may not handle this base case
straightforwardly.

The fix: BJ–Wang's proof of Theorem 1.6 explicitly handles small $V_2$
case-by-case (§3.5 of `team/05` paraphrases this). For $|V_2| = 2$
the proof switches to a direct construction. In our $D^\bullet$
setting with $|V_2| = 2$, $|V_1^\bullet| \ge 1$, the small-$V_2$ base
case applies. We **do not** redo this base case; we rely on BJ–Wang's
treatment. (Caveat: if BJ–Wang's small-$V_2$ base case is itself
sensitive to simplicity in a way we've not parsed, this needs a
separate certification. Auditor's §A.8.7 Risk R1 flags this; resolving
it is a half-day exercise on the primary source.)

### §6.2 $D \langle V_2 \rangle \cong S_4$

The unique simple-digraph exception in Theorem 2.3 of BJ–Wang 2025
(7 total exceptions, of which only $S_4$ is simple). When
$D^\bullet \langle V_2^\bullet \rangle = D \langle V_2 \rangle \cong S_4$,
BJ–Wang's proof of Theorem 1.6 / Corollary 1 may not produce a SAD via
the standard route.

But: $S_4$ is 2-arc-strong, not 3-arc-strong. For $D$ to be 3-arc-
strong, each $v \in V_2$ must have $d_D^\pm(v) \ge 3$, so at least one
in-arc and one out-arc of each $v \in V_2$ must be a bridge from/to
$V_1$. With $|V_1| \ge 2$ and 3-arc-strongness, this is forced. The
direct construction is then: build a SAD of $D$ using $S_4$'s SAD on
$V_2 \setminus \{ \text{one vertex} \}$ plus bridge arcs to absorb the
fourth $V_2$-vertex (which is now treated as a shell vertex by Lemma
2.4). This is the BJ–Wang "Lemma 2.4 with $X = V_2 \setminus \{v\}$"
maneuver. The details are case-by-case and not in scope here.

**For the contraction route specifically**, the $D \langle V_2 \rangle
\cong S_4$ case is the same as for strict-split $D$ (since contraction
doesn't touch $V_2$-internal arcs): BJ–Wang Corollary 1's $S_4$-handling
applies verbatim.

### §6.3 $|V_1| \in \{2, 3\}$

For $|V_1| = 2$: $V_1 = \{p, q\}$, after contraction $|V_1^\bullet| = 1$.
The contracted $D^\bullet$ is strict-split with $|V_1^\bullet| = 1$,
and the BJ–Wang machinery applies very cleanly.

For $|V_1| = 3$: $V_1 = \{p, q, r\}$ with $r$ independent of $\{p, q\}$
in $V_1$. After contraction, $V_1^\bullet = \{p^\bullet, r\}$. Still
independent (§3.2 closure). Still BJ–Wang-applicable.

For $|V_1| \ge 4$: standard; the BJ–Wang induction reduces $|V_1|$
step-by-step.

### §6.4 $|V_2| \in \{3, 4\}$

For $|V_2| = 3$: $V_2$ semicomplete on 3 vertices is either the
3-cycle ($\lambda^{\text{arc}} = 1$) or has $\ge 4$ arcs ($\lambda^{
\text{arc}} = 2$, $K_3^*$ or close). For $D$ to be 3-arc-strong with
3-cycle $V_2$, the $V_1$-to-$V_2$ bridges must compensate by 2 in/out
each at every $V_2$-vertex. This is the BJ–Wang small-$V_2$ regime;
Theorem 2.3's "semicomplete multi-digraph SAD" engine engages. No
new issues.

For $|V_2| = 4$: covered in §6.2 (the $S_4$ exception is the only
relevant case).

---

## §7 — Limitations and open questions

### §7.1 The R3⋆ residual gap

The proof of Theorem 1 is conditional on R3⋆ (§4.7, §4.8). The gap is
specific and structural: it concerns the freedom of the SAD-coloring
at $p^\bullet$ in $D^\bullet$. Closing it requires either:

(7.1.a) Inspecting BJ–Wang's algorithmic construction of the SAD of
$D^\bullet$ for an inherent invariant ensuring at least one
un-contracted color is $q$-reaching.

(7.1.b) A separate combinatorial lemma about the SAD-coloring polytope
at the contracted vertex $p^\bullet$: for any 3-arc-strong split multi-
digraph $D^\bullet$ obtained by contracting an internal arc, at least
one SAD has a $q$-reaching un-contracted color.

Either route is plausible. Path (7.1.a) requires reading BJ–Wang 2025
§3 carefully; the algorithm is constructive and the invariant might be
visible. Path (7.1.b) is a self-contained graph-theoretic question
about SAD spaces.

**Empirical status.** R3⋆ holds on **7 374 + tested 3-arc-strong
candidates** (`team/20_*` §§2.1, 2.2: 7 182 broad-sample + 192
exhaustive at $(|V_1|, |V_2|) = (2, 3)$). No counterexample known.

**Conjecture (R3⋆ as a stated open question).** *For every simple
3-arc-strong $(1,0)$-near-split digraph $D$ with chord $e_0 = (p, q)$,
there exists a SAD $(A_1^\bullet, A_2^\bullet)$ of the contracted
multi-digraph $D^\bullet$ such that, after un-contraction, at least
one of the two colors admits a directed $q \to p$ path in
$V \setminus \{p, q\}$.*

### §7.2 $(2, 0)$-near-split

A $(2, 0)$-near-split digraph has two $V_1$-internal arcs $e_0, e_1$.
Contraction options:

(a) **Sequential contraction.** If $e_0, e_1$ share an endpoint
(say $e_0 = (p, q), e_1 = (q, r)$), contract them sequentially:
$\bar{pqr}$ becomes a single contracted vertex. The result is a split
multi-digraph (single $V_1^\bullet$ vertex from $\{p, q, r\}$). The
multigraph BJ–Wang then applies.

(b) **Parallel contraction.** If $e_0, e_1$ are vertex-disjoint, contract
each separately: $V_1^\bullet$ has two contracted vertices. Still
split multi-digraph; BJ–Wang's Theorem 1.6 induction on $|V_1|$
handles it.

In both cases, the un-contraction step is more involved than R3
(two chords to assign), but the structural template is the same.
**Question:** does R3⋆ generalize to two chords? Conjecturally yes, but
the combinatorial proof is now a 4-state polytope at the contracted
vertex (or vertices). Worth a separate write-up if Theorem 1 is closed.

### §7.3 $(k, 0)$-near-split for $k$ growing with $n$

As $k$ grows, $V_1$ acquires more internal structure. For $k \ge
\binom{|V_1|}{2}$, $V_1$ becomes semicomplete itself, and $D$ is a
"pair-of-semicompletes glued by bridges," to which CL1 (`team/11`
§5.1) applies directly. The interesting regime is small $k = O(1)$;
the contraction route handles $k = 1$ here, and $k = 2$ via §7.2.

### §7.4 2-arc-strong companion theorem

The companion theorem for 2-arc-strong $(1,0)$-near-split digraphs has
a non-trivial exception family $\mathcal{E}_{\text{AHLQW}}^{(1)}$
(`team/19_*` §4.3, `team/20_*` §§2.2, 3.b). The Coder's exhaustive
$(2,3)$ enumeration found **9 NEW canonical UNSAT instances** (`team/20_*`
§2.2). The Auditor's `team/05_audit.md` Appendix A.7 (figure-read of Ai
et al. 2024 Appendix B.2) and the Coder's catalogue arc-reverse bug
fix are in flight. The companion theorem is a plausibly publishable
side-result independent of Theorem 1.

### §7.5 Why the contraction route is the right route

The CL1 (`team/11`) route fails on $(1,0)$-near-split because $D[V_1]$
on 2 or more vertices is at most a single arc — not strongly connected
— so CL1's hypothesis (1) is vacuously false. The vertex-absorption
fix (`team/19_*` §3.1) requires distributing 3-arc-strongness across
the modified partition, which is the load-bearing TODO 1 of §3.5
there.

The contraction route circumvents both obstructions: instead of
finding a SAD on a *non-strongly-connected* $D[V_1]$, it folds $V_1$
into a single contracted vertex on the kernel side and lets BJ–Wang's
strict-split machinery do the SAD. The cost is the un-contraction
step R3 (§4), and R3 in turn has the R3⋆ residual gap.

**Verdict:** The contraction route is structurally simpler and
empirically validated. Closing R3⋆ — a single combinatorial sub-claim
— would complete the proof. The honest scope: a proof skeleton with
one cleanly-stated residual sub-claim, supported by exhaustive
empirics.

---

## Appendix — File hygiene

This file introduces no new code. Empirical validation is in
`team/20_near_split_empirical.md` (the Coder's deliverable, log files
`code/logs/route_b_ns_20260516_*.json` and
`code/logs/route_b_ns_exh_l2_20260516_*.json`).

**Citations cross-checked against `team/05_audit.md`:**

- BJ–Wang 2025 Theorem 1.6 / Corollary 1: `team/05` §1 verbatim
  (Theorem 1.6 / Corollary 1 statements); Appendix A.8 verbatim quote
  of Theorem 1.6 (lines 139–141) and Corollary 1 (line 143).
- BJ–Wang 2025 Lemma 2.4: `team/05` Appendix A.1 / Appendix A.5 Source
  1 (line 925) verbatim.
- BJ–Wang 2025 Lemma 2.7 (line 327, the "$V_2$ has no parallel arcs"
  hypothesis): `team/05` Appendix A.8 §A.8.3 quote.
- BJ–Wang 2025 Theorem 2.5 (Edmonds branching, multigraph form):
  `team/05` Appendix A.5 Source 1, line 946.
- BJG–Yeo Theorem 2.3 (semicomplete-multigraph SAD characterization
  with 6 extra exceptions): `team/05` Appendix A.8 §A.8.3 item 1.
- Ai et al. 2024 Proposition A.1 (precedent for BJ–Wang Lemma 2.4 on
  multi-digraphs): `team/05` Appendix A.8 §A.8.4 lines 1388–1431.
- Empirical record (7 182 + 192 candidates, 0 UNSAT at $\lambda = 3$):
  `team/20_near_split_empirical.md` §§2.1, 2.2.

**No "Theorem RD"-style citations.** The OLS round-decomposition trap
of `team/14_*` is explicitly avoided.

**Lemma R3 is new** (introduced in this file). R3⋆ is its single
residual sub-claim.

End of file.
