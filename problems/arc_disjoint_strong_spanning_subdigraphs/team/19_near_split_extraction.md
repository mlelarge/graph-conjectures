# 19 — Route B extraction: SAD for 3-arc-strong $(1,0)$-near-split digraphs

Author: Structural Digraph Specialist
Date: 2026-05-16
Status: first write-up of Route B in its **$(1,0)$-near-split** form
(after the OLS pivot of `team/13_*` §7). This file delivers a *partial*
proof: a clean reduction skeleton, sub-cases on $|V_1|$, and explicit
identification of two structural TODOs that remain. Theorem 1 (the
headline) is **not** proved in full. This is the honest state.

Companion files: `team/11_cl1_proof_v1.md` (CL1 statement §5.1 and R2
proof §3), `team/02_structural_program.md` §3 (rank-2 near-split
motivation), `team/05_audit.md` §1 (verbatim BJ–Yeo 2004, BJ–Huang
2012, BJG–Yeo 2020, BJ–Wang 2025, Ai et al. 2024 citations),
`team/05_audit.md` Appendix A.1 (BJ–Wang Lemma 2.4 and Ai et al. Lemma
2.11 verbatim), Appendix A.4 (the $(iv)^*\times(iv)$ 6-vertex split
exception). `team/14_route_b_ols_extraction.md` is **blocked** and is
referenced only as a negative precedent (no "Theorem RD"-style
citations appear here).

---

## §1 — Setup

### §1.1 Class definition (verbatim from `team/13_*` §7)

A digraph $D = (V, A)$ is **$(1, 0)$-near-split** if $V = V_1
\,\dot\cup\, V_2$ where:

1. $V_2$ induces a *semicomplete* digraph;
2. arcs between $V_1$ and $V_2$ are unrestricted;
3. **exactly one arc lies inside $V_1$**; otherwise $V_1$ is
   independent.

The $(0, 0)$-case is the strict split-digraph class handled by BJ–Wang
2025 Theorem 1.6 / Corollary 1 and characterized at 2-arc-strength by
Ai et al. 2024 Theorem 1.8.

Throughout: simple digraphs, no loops, no multi-arcs. We write $e_0 =
(p, q)$ for the unique $V_1$-internal arc, $p, q \in V_1$. Bridges:
$B^+ := \delta_D^+(V_1)$, $B^- := \delta_D^+(V_2)$. The strict-split
case has $e_0$ absent and $V_1$ independent.

### §1.2 Cited theorems (all verbatim cross-references to `team/05`)

**(BJ–Yeo 2004 / BJG–Yeo Theorem 1.1.)** A 2-arc-strong semicomplete
digraph has a SAD iff it is not $S_4$. (Verbatim `team/05` §1.)

**(BJ–Huang 2012, BJ–Wang Theorem 1.3.)** A 2-arc-strong locally
semicomplete digraph has a SAD iff it is not the square of an even
directed cycle; every 3-arc-strong locally semicomplete digraph has a
SAD. (Verbatim `team/05` §1.)

**(BJG–Yeo 2020 Theorem 1.4.)** A semicomplete composition $T[H_1,
\ldots, H_t]$ ($T$ strong semicomplete, $t \ge 2$, $H_i$ arbitrary
digraphs) has a SAD iff it is 2-arc-strong and is not one of $S_4,
\vec{C}_3[\overline{K}_2^3], \vec{C}_3[\overline{K}_2, \overline{K}_2,
\overline{P}_2], \vec{C}_3[\overline{K}_2, \overline{K}_2,
\overline{K}_3]$. (Verbatim `team/05` §1.) Call this exception set
$\mathcal{E}_{\mathrm{BJGY}}$.

**(BJ–Wang 2025 Theorem 1.6 + Corollary 1.)** A 2-arc-strong split
digraph with min in/out-degree $\ge 3$ on $V_1$ has a SAD; every
3-arc-strong split digraph has a SAD. (Verbatim `team/05` §1.)

**(Ai et al. 2024 Theorem 1.8.)** A 2-arc-strong split digraph has a
SAD iff it is not isomorphic to any digraph in Lemma 2.11, Lemma 3.12,
the Appendix, or their arc-reverses. (Verbatim `team/05` §1.) Call
this exception set $\mathcal{E}_{\mathrm{AHLQW}}$.

**(BJ–Wang 2025 Lemma 2.4, verbatim `team/05` Appendix A.1.)** *Let $D$
be a directed multigraph and $X \subseteq V(D)$. If every vertex of $D
- X$ has two in-neighbors and two out-neighbors in $X$, and if
$D[X]$ has a SAD, then $D$ has a SAD.*

### §1.3 The lifting tool (CL1, R2-cleaned form)

**Lemma CL1 (verbatim `team/11` §5.1).** *Let $D = (V, A)$, $V = V_1
\,\dot\cup\, V_2$, $|V_i| \ge 2$. Write $B^\pm$ as above. Suppose (1)
$D[V_1]$ and $D[V_2]$ each admit a SAD $A(D_i) = R_i \,\dot\cup\, B_i$,
and (2) the bridges admit a partition $B^\pm = B^\pm_R \,\dot\cup\,
B^\pm_B$ with $B^+_R, B^+_B, B^-_R, B^-_B$ all non-empty. Then $A(D) =
(R_1 \cup R_2 \cup B^+_R \cup B^-_R) \,\dot\cup\, (B_1 \cup B_2 \cup
B^+_B \cup B^-_B)$ is a SAD of $D$.*

Proof: `team/11` §3 (R2 branching-witness route). CL1 hypothesis (1)
demands SAD on **both** parts; this is the binding constraint for our
near-split setting because $D[V_1]$ is a single arc on $|V_1| \ge 2$
vertices, which is not strongly connected and hence has no SAD.

### §1.4 What 3-arc-strongness buys

If $D$ is 3-arc-strong, every $v \in V$ has $d_D^\pm(v) \ge 3$. At most
one out-arc and at most one in-arc of $v$ can be the chord $e_0$, and
only for $v \in \{p, q\}$. Hence:

(F1) Every $v \in V_1$ has $\ge 2$ out-arcs into $V_2$ and $\ge 2$ in-
arcs from $V_2$; for $v \in V_1 \setminus \{p, q\}$ this strengthens to
$\ge 3$ of each.

(F2) $|B^+|, |B^-| \ge 2 |V_1|$ (in particular both $\ge 4$ for
$|V_1| \ge 2$).

(F3) Every in-arc of $p$ comes from $V_2$ (since $(q, p) \notin A$ —
the unique $V_1$-internal arc is $e_0 = (p, q)$, not its reverse — and
$V_1 = \{p, q\}$ in the smallest case, or has no other $V_1$-internal
arc by definition). Hence $|N_D^-(p) \cap V_2| = d_D^-(p) \ge 3$.
Symmetrically $|N_D^+(q) \cap V_2| \ge 3$.

---

## §2 — The headline theorem

**Theorem 1 (Route B headline, $(1, 0)$-near-split).** *Let $D = (V,
A)$ be a $(1, 0)$-near-split digraph with $V = V_1 \,\dot\cup\, V_2$
and unique $V_1$-internal arc $e_0 = (p, q)$. Suppose $D$ is 3-arc-
strong and $|V_2| \ge 2$. Then $D$ admits a strong arc decomposition.*

**Exception clause.** The hypothesis $|V_2| \ge 2$ is the only
structural assumption beyond 3-arc-strongness and the $(1, 0)$-near-
split form. No further exception list arises: the four BJG–Yeo 2020
exceptions and the Ai et al. 2024 family are all *2-arc-strong*
(`team/05` §2 benchmark table — $\lambda^{\mathrm{arc}} = 2$ for every
listed exception); they cannot serve as 3-arc-strong counterexamples
to Theorem 1. This matches BJ–Wang Corollary 1: 3-arc-strong split has
no exceptions.

**Status.** Theorem 1 is **not proved in full** by this file. Two
structural TODOs remain (see §3.5). The proof skeleton, sub-cases, and
the precise location of the gaps are below.

---

## §3 — Proof attempt and gap analysis

The proof strategy is: in each case on $|V_1|$, build a partition $V =
V_1' \,\dot\cup\, V_2'$ to which CL1 applies. The naive choice $V_1' =
V_1, V_2' = V_2$ fails immediately: $D[V_1]$ is a single arc, hence not
strongly connected, hence has no SAD, hence CL1 hypothesis (1) fails.

**The fix to attempt:** absorb $V_2$-vertices into $V_1'$ to make
$D[V_1']$ strongly connected and ideally 2-arc-strong; keep $V_2' = V_2
\setminus W$ semicomplete (which is automatic — induced sub-digraphs of
semicomplete digraphs are semicomplete) and 2-arc-strong (which is *not*
automatic).

### §3.1 Case (a): $|V_1| = 2$

$V_1 = \{p, q\}$, chord $e_0 = (p, q)$.

#### Single-vertex absorption attempt.

Pick $w \in V_2$ and set $V_1' := \{p, q, w\}$, $V_2' := V_2 \setminus
\{w\}$. For $D[V_1']$ to be strongly connected we need a directed cycle
through $\{p, q, w\}$. The arc $(q, p) \notin A$ (no $V_1$-internal arc
besides $e_0$), so the only candidate cycle is $p \to q \to w \to p$,
which requires $(q, w), (w, p) \in A$, i.e. $w \in N_D^+(q) \cap N_D^-
(p)$.

**Existence of $w$:** From (F3), $|N_D^+(q) \cap V_2| \ge 3$ and
$|N_D^-(p) \cap V_2| \ge 3$. By inclusion-exclusion in $V_2$:
$$|N_D^+(q) \cap N_D^-(p)| \;\ge\; 3 + 3 - |V_2| \;=\; 6 - |V_2|.$$
So the desired $w$ exists whenever $|V_2| \le 5$. For $|V_2| \ge 6$ the
counting bound is vacuous and we cannot conclude $w$ exists from 3-arc-
strongness alone via this method.

**But the absorption also fails CL1 hypothesis (1).** Even when $w$
exists, $D[V_1'] = D[\{p, q, w\}]$ contains the 3-cycle $p \to q \to w
\to p$ plus possibly other arcs from $D$. Whatever arcs exist, the
forbidden $(q, p) \notin A$ creates a 1-cut: removing the arc $(q, w)$
disconnects $\{q\}$ from $\{p, w\}$ in the out-direction (since $q$'s
only $V_1'$-out-arc to $V_1'$ is $(q, w)$; $(q, p) \notin A$). Hence
$\lambda^{\mathrm{arc}}(D[V_1']) = 1$, and **$D[V_1']$ has no SAD**
(SAD requires $\lambda^{\mathrm{arc}} \ge 2$).

#### Multi-vertex absorption attempt.

Absorb $W = \{w_1, w_2, \dots\} \subseteq V_2$. For $\lambda^{\mathrm
{arc}}(D[V_1']) \ge 2$ we must give every vertex of $V_1'$ at least 2
in-arcs and 2 out-arcs *inside* $V_1'$. The bottleneck is $p$: $p$'s
only $V_1'$-in-arcs come from $W$ (no $V_1$-internal in-arcs to $p$),
so we need $|W \cap N_D^-(p)| \ge 2$. Similarly $q$'s only $V_1'$-out-
arcs to $V_1' \setminus \{p, q\} = W$ come from $W$, so we need $|W \cap
N_D^+(q)| \ge 2$. Symmetrically for the absorbed $w_i$ vertices, which
need 2 in/out-arcs in $V_1'$.

**3-arc-strongness gives $|N_D^-(p)| \ge 3$ and $|N_D^+(q)| \ge 3$
inside $V_2$ (F3),** so picking 2 vertices from each is possible. But
we also need $D[V_2 \setminus W]$ to remain 2-arc-strong (so it admits
a SAD by BJ–Yeo 2004 / BJG–Yeo 2020 modulo $S_4$). Removing 2–4
vertices from $V_2$ can drop $\lambda^{\mathrm{arc}}(D[V_2])$
substantially.

**TODO 1.** *For $D$ 3-arc-strong $(1, 0)$-near-split with $|V_1| = 2$,
there exists $W \subseteq V_2$, $|V_2 \setminus W| \ge 2$, such that
$D[V_1 \cup W]$ is 2-arc-strong and admits a SAD, and $D[V_2 \setminus
W]$ is 2-arc-strong and admits a SAD.*

We have **not proved TODO 1 from 3-arc-strongness alone**. It is a
structural distribution claim about how the arc-connectivity of $D$
splits across the chord-modified partition.

#### Alternative: chord contraction (fails).

Contract $e_0 = (p, q)$ into a single vertex $\bar{pq}$. The result
$D^\bullet$ is a *split* digraph (with $V_1^\bullet = \{\bar{pq}\}$,
$V_2^\bullet = V_2$). If $D^\bullet$ were 3-arc-strong, BJ–Wang
Corollary 1 would give it a SAD, and we could lift back. But
contraction creates parallel arcs (whenever both $(p, v), (q, v) \in A$
for some $v \in V_2$), which collapse to single arcs in the simple-
digraph convention. Each such collapse reduces some cuts of $D^\bullet$
by 1 relative to the corresponding cut of $D$. In the worst case, two
collapses can hit the same cut, dropping arc-connectivity by 2. So
$\lambda^{\mathrm{arc}}(D^\bullet) \ge 3 - 2 = 1$ only — too weak to
apply BJ–Wang.

If we allow $D^\bullet$ to be a *multi*-digraph (keeping parallel
arcs), contraction preserves 3-arc-strongness, and BJ–Wang 2025
Theorem 1.6 is stated for directed *multigraphs* (verbatim
`team/05` Appendix A.1 / §1: "Let $D = (V_1, V_2; A)$ be a 2-arc-strong
split digraph…" — the paper's text allows multigraphs; the Theorem
1.6 / Corollary 1 statements likewise. **TODO (verify multigraph
scope):** confirm BJ–Wang Theorem 1.6 / Corollary 1 apply to
multigraphs as written). If yes, the multigraph chord-contraction
route works: $D^\bullet$ is a 3-arc-strong split multi-digraph with
$|V_1^\bullet| = 1$, BJ–Wang Corollary 1 gives a SAD, and we lift back
to $D$ by un-contracting and choosing how to assign the duplicated
arcs to the two color classes. The lifting step is `team/05` Appendix
A.5 Source 1 territory (Edmonds-style attachment).

This **multigraph chord-contraction route is the most promising path
to closing §3.1**, but it requires (a) verifying BJ–Wang's multigraph
scope and (b) writing out the un-contraction step carefully. Marked as
**TODO 1' (multigraph chord-contraction route)**.

### §3.2 Case (b): $|V_1| = 3$

$V_1 = \{p, q, r\}$ with $e_0 = (p, q)$ and $r$ independent of $\{p,
q\}$ inside $V_1$.

(F1) gives every $v \in V_1$ at least 2 out-arcs and 2 in-arcs to
$V_2$; for $r$, the lower bound improves to 3 of each (no chord
adjustment). $|B^+|, |B^-| \ge 8$ by (F2).

The single-vertex absorption strategy from §3.1 carries over: pick
$w \in V_2$ to make $D[V_1 \cup \{w\}]$ strongly connected, then check
2-arc-strength. The same obstruction recurs: $p$'s in-degree inside
$V_1 \cup \{w\}$ depends entirely on $(w, p) \in A$ and any chord-
extensions, neither of which give $p$ a second in-arc inside the new
$V_1'$. So $\lambda^{\mathrm{arc}}(D[V_1']) = 1$.

Multi-vertex absorption $|W| \ge 2$ with $w_1, w_2 \in N_D^-(p) \cap
V_2$ can give $p$ two in-arcs inside $V_1'$. The bottleneck moves to
$q$ (which needs in-arcs beyond $e_0$ from $V_1' \cap V_2$) and to
each $w_i$ (which needs in/out-arcs to/from the rest of $V_1'$).

**Same TODO 1 as Case (a).**

### §3.3 Case (c): $|V_1| \ge 4$

Same structural obstruction. The arc-budget on $V_1$-vertices grows
linearly, but the chord-induced 1-cut at $\{q\}$ (or, dually, at
$\{p\}$ in the in-direction) persists inside any $V_1' \supseteq V_1$.
**Same TODO 1.**

### §3.4 Fallback: BJ–Wang Lemma 2.4 with $X = V_2$

A direct invocation of BJ–Wang Lemma 2.4 (kernel-shell asymmetric)
sidesteps CL1 entirely. Take $X := V_2$, shell $D - X = V_1$. Lemma
2.4's hypothesis: every $v \in V_1$ has 2 in- and 2 out-neighbors in
$X = V_2$. By (F1), every $v \in V_1$ has at least 2 in-arcs from $V_2$
and 2 out-arcs to $V_2$ — and since $D$ is simple, these are 2 distinct
in-neighbors and 2 distinct out-neighbors in $V_2$. ✓

**Lemma 2.4 then says: if $D[V_2]$ has a SAD, then $D$ has a SAD.**

**Does $D[V_2]$ have a SAD?** $D[V_2]$ is semicomplete by hypothesis.
By BJ–Yeo 2004, it has a SAD iff it is 2-arc-strong and $\ne S_4$.

**TODO 2.** *For $D$ a 3-arc-strong $(1, 0)$-near-split digraph,
$D[V_2]$ is 2-arc-strong and not isomorphic to $S_4$.*

Counterexample to TODO 2 in principle: 3-arc-strongness of $D$ does
**not** descend to 2-arc-strongness of $D[V_2]$. A small $V_2$-cut
inside $D[V_2]$ can be "absorbed" by bridges from $D$, leaving $D$
3-arc-strong overall while $D[V_2]$ is 1-arc-strong.

Explicit small case: $|V_1| = 4$, $|V_2| = 3$, $V_2$ a 3-cycle $w_1 \to
w_2 \to w_3 \to w_1$ with $\lambda^{\mathrm{arc}}(D[V_2]) = 1$. Each
$w_i$ has $d_{D[V_2]}^\pm = 1$. For $D$ to be 3-arc-strong, each $w_i$
needs 2 additional in-arcs and 2 additional out-arcs from/to $V_1$.
This is achievable (each $w_i$ has 2 bridges in each direction).
Construction is feasible: 4 vertices in $V_1$ × 2 in-arcs = 8 outgoing
bridges from $V_2$ to $V_1$ at minimum; etc. **The construction is
small (n = 7) and within the Coder's enumeration range.**

If TODO 2 is false (such a $D$ exists), BJ–Wang Lemma 2.4 cannot close
Theorem 1; we are forced back to TODO 1 or to a stronger structural
tool.

### §3.5 Summary of the gap

Two structural TODOs are load-bearing:

**TODO 1.** For $(1, 0)$-near-split 3-arc-strong $D$, find $W
\subseteq V_2$ so $D[V_1 \cup W]$ and $D[V_2 \setminus W]$ are both
2-arc-strong and SAD-decomposable (so CL1 applies).

**TODO 2.** For $(1, 0)$-near-split 3-arc-strong $D$, $D[V_2]$ is
2-arc-strong and $\ne S_4$ (so BJ–Wang Lemma 2.4 with $X = V_2$
applies).

Either TODO resolves the proof. Both are structural existence/
universal claims about how 3-arc-strongness distributes across the
partition; neither is derivable from CL1 + verified literature alone
by purely cut-counting arguments. **The Coder's enumeration
(`code/generators/near_split.py`, per `team/20_*`) will test which
TODO is true on small instances.**

There is also a **promising third route, TODO 1' (multigraph chord-
contraction).** Contract $e_0$ in $D$ to form a multi-digraph
$D^\bullet$. $D^\bullet$ is split (single-vertex $V_1^\bullet$),
3-arc-strong as a multigraph (no collapse, since we keep parallels).
If BJ–Wang's results hold for split *multi-digraphs* — which their
paper states — then $D^\bullet$ has a SAD, and a careful un-contraction
recovers a SAD of $D$. **TODO 1' requires verifying BJ–Wang scope and
writing the un-contraction step.**

The honest verdict: **the proof skeleton is in place but the proof is
not complete.** Two cleanly-stated structural questions remain.

---

## §4 — Exception analysis

### §4.1 BJG–Yeo 2020 exceptions

$\mathcal{E}_{\mathrm{BJGY}} = \{S_4, \vec{C}_3[\overline{K}_2^3],
\vec{C}_3[\overline{K}_2,\overline{K}_2,\overline{P}_2], \vec{C}_3[
\overline{K}_2,\overline{K}_2,\overline{K}_3]\}$ — all 2-arc-strong.
The three composition exceptions are not semicomplete in the simple-
digraph sense (the $\overline{K}_n$ layers are arc-less, so the
composition has many missing pairs in $V_2$ if it were to play that
role). Only $S_4$ is plausibly $D[V_2]$ for our setting. **The
relevant exception in our analysis is $D[V_2] = S_4$**, which only
arises if TODO 2 is invoked with a 4-vertex $V_2$.

### §4.2 Ai et al. 2024 split exceptions

$\mathcal{E}_{\mathrm{AHLQW}}$ is a finite list of 2-arc-strong **strict-
split** digraphs without SAD. The smallest is $n = 5, |V_1| = 1,
|V_2| = 4$ (`team/05` Appendix A.1; encoded in `code/benchmarks.py::
_AiEtAl_Lemma211_smallest`). The $(iv)^* \times (iv)$ case has $n = 6,
|V_1| = 2, |V_2| = 4$ (`team/05` Appendix A.4).

These are strict-split (no chord), so they are not $(1, 0)$-near-split
themselves. The Coder should enumerate $(1, 0)$-near-split analogues:
i.e., add a chord to each $\mathcal{E}_{\mathrm{AHLQW}}$ instance and
check if the augmented digraph remains an UNSAT counterexample.
**Conjecture:** any such augmentation either breaks 2-arc-strength or
restores SAD-existence. The Coder's enumeration tests this.

### §4.3 2-arc-strong $(1, 0)$-near-split — the parallel characterization

For the 2-arc-strong $(1, 0)$-near-split case (a natural weakening of
Theorem 1), the exception list is likely a finite extension of
$\mathcal{E}_{\mathrm{AHLQW}}$ to "split digraph + one chord."
Concretely:

**Conjecture (companion to Theorem 1.8 of Ai et al. 2024).** *A
2-arc-strong $(1, 0)$-near-split digraph has a SAD iff it is not
isomorphic to any digraph in a finite list $\mathcal{E}_{\mathrm{
AHLQW}}^{(1)}$, where $\mathcal{E}_{\mathrm{AHLQW}}^{(1)}$ is obtained
from $\mathcal{E}_{\mathrm{AHLQW}}$ by chord-augmentation plus
possibly a small number of new "chord-induced" structures.*

The Coder's enumeration produces $\mathcal{E}_{\mathrm{AHLQW}}^{(1)}$
empirically; the analogue of Ai et al. 2024 Theorem 1.8 proof would
deduce it structurally. This is a **plausibly publishable companion
result** even without resolving the 3-arc-strong case.

---

## §5 — Edge cases

### §5.1 $|V_1| \in \{2, 3, 4\}$

Covered in §3.1, §3.2, §3.3. All three sub-cases hit TODO 1. The
multigraph chord-contraction route TODO 1' is uniform across these
cases (it reduces all $|V_1| \ge 2$ to a single-vertex-$V_1$ split
multi-digraph problem).

### §5.2 $|V_2| \in \{2, 3, 4\}$

**$|V_2| = 2$:** $V_2 = \{w_1, w_2\}$ semicomplete (at least one of the
arcs $(w_1, w_2), (w_2, w_1) \in A$). By 3-arc-strongness, each $w_i$
has $d_D^\pm \ge 3$, so each has $\ge 2$ bridges in each direction. So
$|B^+|, |B^-| \ge 4$. $D[V_2]$ is 1- or 2-arc-strong depending on
whether both directed arcs are present.

If $D[V_2]$ has both arcs (the 2-cycle): TODO 2 is satisfied ($D[V_2]$
is 2-arc-strong on 2 vertices — wait, no: a 2-vertex 2-cycle is 1-arc-
strong, since removing any arc disconnects). **Need to recheck:** on
2 vertices, the only strongly connected digraph is the 2-cycle,
with $\lambda^{\mathrm{arc}} = 1$. So $D[V_2]$ on 2 vertices cannot
be 2-arc-strong; **TODO 2 always fails when $|V_2| = 2$.**

So $|V_2| = 2$ falls outside the BJ–Wang Lemma 2.4 fallback. CL1 also
fails as discussed. **TODO 1' (multigraph chord-contraction) remains
the only viable route.**

**$|V_2| = 3$:** $V_2$ semicomplete on 3 vertices is either the 3-
cycle ($\lambda^{\mathrm{arc}} = 1$, no SAD) or $K_3^*$ ($\lambda^{
\mathrm{arc}} = 2$, has SAD — `team/05` §2). The 3-cycle case fails
TODO 2; $K_3^*$ satisfies it.

**$|V_2| = 4$:** Semicomplete 4-vertex digraphs come in many isomorphism
types. $S_4 \in \mathcal{E}_{\mathrm{BJGY}}$ is the unique 2-arc-strong
4-vertex semicomplete without SAD. All other 2-arc-strong 4-vertex
semicomplete digraphs admit a SAD by BJ–Yeo 2004.

**TODO (Coder enumeration):** enumerate $(1, 0)$-near-split digraphs
with $D[V_2] = S_4$ and verify each is either SAT or 2-arc-strong-not-
3-arc-strong.

### §5.3 $D[V_2]$ a BJG–Yeo 2020 exception

Only $D[V_2] = S_4$ is relevant (see §4.1). When this occurs, BJ–Wang
Lemma 2.4 fails because the kernel $V_2$ has no SAD. A direct
argument using the chord plus the bridges plus the explicit structure
of $S_4$ is needed. **TODO (separate enumeration sub-case).**

---

## §6 — Limitations and open questions

### §6.1 Status

**Theorem 1 is not proved by this file.** Two structural TODOs (and a
third multigraph route) block the proof; see §3.5. The contribution of
this file is:

- a clear reduction skeleton (CL1 + bridge counting + absorption);
- identification of the load-bearing obstruction (the chord creates a
  1-cut inside $V_1'$ at $\{q\}$ whenever $V_1' \cap V_2$ is too small
  on the in-side of $p$);
- two cleanly-stated structural existence questions (TODO 1, TODO 2)
  and a promising lifting route (TODO 1', multigraph chord-
  contraction);
- a Coder hand-off: empirical enumeration on $n \le 10$ will resolve
  whether Theorem 1 is true, identify exceptions if it is false, and
  test which TODO is required for the proof.

### §6.2 $(2, 0)$-near-split

A $(2, 0)$-near-split digraph has two $V_1$-internal arcs. The same
structural obstruction applies: $D[V_1]$ on $|V_1| \ge 2$ vertices with
$\le 2$ arcs is still not strongly connected in general (two vertex-
disjoint arcs form an acyclic 4-vertex digraph; two arcs sharing a
vertex form a 2-path, also acyclic). The two chords offer slight
extra flexibility for forming directed cycles inside $V_1' = V_1 \cup
W$, but the fundamental obstacle — $D[V_1']$ being 2-arc-strong —
persists.

**The multigraph chord-contraction route TODO 1' generalizes:**
contract both chords in turn. If both chords share an endpoint (say
$e_0 = (p, q), e_1 = (q, r)$ form a 2-path), contract them sequentially
to a single vertex; the resulting $D^\bullet$ is split with $|V_1^
\bullet| = 1$. If the chords are vertex-disjoint ($e_0 = (p_0, q_0),
e_1 = (p_1, q_1)$), contract each to a vertex; $D^\bullet$ is split
with $|V_1^\bullet| = 2$. In either case, BJ–Wang Theorem 1.6 needs
verification on the resulting multi-digraph at 3-arc-strength.

### §6.3 $(k, 0)$-near-split for large $k$

As $k \to |V_1|(|V_1| - 1)$, $V_1$ becomes a semicomplete digraph, and
$D$ becomes a pair-of-semicompletes glued by bridges. CL1 applies
cleanly if both semicompletes are 2-arc-strong and $\ne S_4$; the
bridge 2-coloring exists trivially for large $|B^\pm|$. **Large $k$
is easier than $k = 1$.** The interesting regime is small $k = O(1)$.

### §6.4 ILS / OLS sibling

Out of scope. See `team/17_ols_rd_problem.md` for the OLS notebook.
The OLS problem has its own structural obstruction (BJG 1998 Problem
6.8) that is not addressed by the CL1 + BJ–Wang Lemma 2.4 toolkit.

### §6.5 2-arc-strong $(1, 0)$-near-split characterization

§4.3 above proposes a conjectural finite exception list
$\mathcal{E}_{\mathrm{AHLQW}}^{(1)}$ extending Ai et al. 2024 Theorem
1.8 to allow one chord. The Coder's enumeration produces this list
empirically. **This is plausibly publishable independently of Theorem
1.**

### §6.6 Salvageable from `team/14_*` (OLS)

`team/17` §4 notes two ideas from the blocked OLS deliverable:
(a) contiguous-block partition along two "switch positions";
(b) round-cyclic vs. alternating case split. Neither transfers
directly to the near-split setting: the near-split structure has no
"rounds" and no alternation. **Negative result: §4 of `team/17` does
not help here.**

### §6.7 Next-step deliverables

To the Coder: enumerate 3-arc-strong $(1, 0)$-near-split simple
digraphs of order $\le 10$; identify any UNSAT instances; if none,
Theorem 1 is empirically validated. Also enumerate 2-arc-strong $(1,
0)$-near-split instances to produce $\mathcal{E}_{\mathrm{AHLQW}}^{
(1)}$ (§4.3 conjecture).

To the Auditor: review TODO 1' (multigraph chord-contraction). Verify
BJ–Wang Theorem 1.6 / Corollary 1's scope on multi-digraphs by
reading the primary source directly (arXiv:2309.06904), and confirm
whether the un-contraction step preserves SAD.

To the Lead: per `team/13` §7 tripwire, if this file does not produce
a working proof by 2026-06-27, Route B re-pivots. **The current
verdict is partial progress** — a clean skeleton, two TODOs, and a
plausible third route via multigraphs.

---

## Appendix — File hygiene

This file introduces no new code. Empirical validation is delegated to
`code/generators/near_split.py` (Coder) and `team/20_*` (Coder
deliverable).

**Citations cross-checked against `team/05_audit.md`:**

- BJ–Yeo 2004 (Combinatorica 24, 331–349): `team/05` §1 verbatim.
- BJ–Huang 2012 (JCTB 102, 701–714): `team/05` §1 verbatim.
- BJG–Yeo 2020 (J. Graph Theory 95, 267–289; arXiv:1903.12225):
  `team/05` §1 verbatim Theorem 1.4 with four exceptions.
- BJ–Wang 2025 (J. Graph Theory 108, 5–26; arXiv:2309.06904):
  `team/05` §1 verbatim Theorem 1.6 + Corollary 1; Lemma 2.4 verbatim
  `team/05` Appendix A.5 Source 1.
- Ai et al. 2024 (arXiv:2408.02260): Theorem 1.8 verbatim `team/05`
  §1; Lemma 2.11 verbatim `team/05` Appendix A.1; $(iv)^* \times (iv)$
  arc list `team/05` Appendix A.4.

**CL1 cited by section:** statement `team/11` §5.1; R2 proof
`team/11` §3; disjointness remark `team/11` §3 Step 6.

**No "Theorem RD"-style citations.** The OLS round-decomposition trap
of `team/14_*` is explicitly avoided.

End of file.
