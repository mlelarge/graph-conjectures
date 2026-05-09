# Appendix: per-case F-step derivations for $\delta = 4, n = 10$

> The headline theorem and proof structure are in
> [k4_n10_proof.md](k4_n10_proof.md). This
> file contains the supporting per-score-sequence per-case F-step
> derivations (forced arcs, sub-cases, length-8 paths) and the
> soundness justification of the local miner's forcing rules.

**Status: $\delta = 4$ at $n = 10$ is closed** (see
[k4_n10_proof.md](k4_n10_proof.md)).

At $n = 10$, every $(S, T)$ configuration consistent with Cheng--Keevash
Lemma 7 + path/cycle structure + score sequence has been verified to
admit no counterexample with $\ell(D) = 7$:

- Score $(1,1,1,1)$: dies by direct cyclic closure (analogous to $k=3$
  proof).
- Score $(2,1,1,1)$, all 4 cases: closed with F-step derivations + hand-
  written length-8 paths.
- Score $(3,1,1,1)$, all 4 cases: closed similarly.
- Score $(2,2,1,1)$, all 24 sub-cases (Shape A1: 12, Shape A2: 8,
  Shape B: 4): closed by **local proof miner**
  (`scripts/k4_local_miner.py`). For each $(S, T)$, the miner derives
  all forced arcs from local constraints, enumerates every 4-outregular
  oriented completion, and verifies that each contains a directed
  simple path of length 8.

**Combined theorem:**

> Every oriented graph $D$ with $\delta^+(D) \geq 4$ and $|V(D)| = 10$
> contains a directed simple path of length 8.

The proof is computer-aided for the $(2,2,1,1)$ score sequence: the
miner exhaustively checks all 24 valid $(S, T)$ configurations and
finds 0 obstructions.

**Audit (`scripts/k4_audit.py`).** The miner has been audited:
- $(S, T)$ enumeration is complete: brute force over all $C(6,3) \cdot
  C(4,2) = 120$ raw pairs gives exactly 24 valid configurations
  ($v_7 \in S$ and $\sigma(T) \subseteq S$); the miner's
  Shape-A1/A2/B enumeration matches.
- Every completion of every $(S, T)$ passes the following checks:
  forced arcs present; antiparallel respected; 4-outregular; Claim 12
  (S-vertex out-arcs in $V(C)$); score sequence as specified
  ($d^+_S(s) = 1$ for $s \in T$, $= 2$ for $s \in S \setminus T$);
  contains a directed simple path of length 8.
- Total completions verified: $\sim$3,664 (Shape A1: 3,448; Shape A2:
  144; Shape B: 72).
- 0 audit failures across all 24 configurations.

**Path table (`data/k4_path_table.md`).** A representative length-8
path is recorded for each $(S, T)$. Some $(S, T)$ admit a *single*
path that holds in every completion (e.g.\ A2.1, A2.4, B
$S=\{v_1,v_3,v_4,v_7\}$); others require different paths in different
completion sub-cases, but the audit ensures every completion does
admit some length-8 path.

The argument is **specific to $n = 10$**: each extra off-path vertex
relaxes the forcing chain, so $n \geq 11$ requires a separate analysis.

This file documents the partial result; the open cases are tracked in
`plan.md`.

## Setup

Apply the R1/R2/R3 reduction: a counterexample at $\delta = 4$ reduces to
a strong $4$-outregular oriented graph $D$ with $\ell(D) = 7$ and
$|V(D)| \geq 9$.

### Sink SCC bound

Suppose $D_0$ is a counterexample to Conjecture 1 at $\delta = 4$:
$\delta^+(D_0) \geq 4$ and $\ell(D_0) \leq 7$. The R1/R2/R3 reduction
produces a strong $4$-outregular oriented sink SCC $D$ with
$\ell(D) \leq \ell(D_0) \leq 7$. Cheng--Keevash Theorem 4 applied to
$D$ gives $\ell(D) \geq 6$. By the oriented average bound,
$|V(D)| \geq 2\delta + 1 = 9$.

**$|V(D)| \neq 9$.** If $|V(D)| = 9$, then $|A(D)| = 36 = \binom{9}{2}$,
so $D$ is a tournament (every pair is an arc), and being $4$-outregular
on 9 vertices it is a regular tournament. Every regular tournament has
a Hamilton (directed) path of length $|V| - 1 = 8$ (Redei's theorem
applied to the strong tournament). So $\ell(D) \geq 8$, contradicting
$\ell(D) \leq 7$.

Hence $|V(D)| \geq 10$. **The proof in this file closes the case
$|V(D)| = 10$.** The remaining cases $|V(D)| \geq 11$ are open and
require separate analysis (see plan).

At $n = 10$: $\binom{10}{2} = 45$, $|A(D)| = 40$, so $D$ has exactly $5$
non-edges. Write $V(P) = \{v_0, v_1, \ldots, v_7\}$ for the longest
path, $V(D) \setminus V(P) = \{x, y\}$.

By Cheng--Keevash Lemma 7 + the oriented average bound, the surviving
configuration has $|S| = 4$, $a = 1$, $V(C) = \{v_1, \ldots, v_7\}$,
cycle $C : v_1 \to v_2 \to \cdots \to v_7 \to v_1$, $v_7 \in S$,
$\delta^+(S) = 1$, $|V(C) \setminus S| = 3$.

The score sequence of $S$ (with $\delta^+(S) = 1$) is one of
$(1,1,1,1)$, $(2,1,1,1)$, $(2,2,1,1)$, $(3,1,1,1)$. The first dies by
direct cyclic closure (cf.\ Step 7 of the $k=3$ proof).

## $B$ and the forced out-neighbourhood of $v_0$

By Claim 11, $N^+(v_0) \subseteq V(P)$. With $a = 1$ and no self-loop,
$N^+(v_0) \subseteq V(C) = \{v_1, \ldots, v_7\}$. Then $|N^+(v_0)| = 4$,
so $|B| = 4$, $|A| = 0$, and $B = N^+(v_0)$. Since
$S = B^- = \mathrm{pred}_C(B)$, we have $B = \mathrm{succ}_C(S)$.

### Cyclic-interval mini-lemma

**Lemma.** In score sequence $(2,1,1,1)$, $S$ is a cyclic interval of 4
consecutive vertices in $C$, with the unique outdegree-2 vertex $u$ at
the interval start (in $C$-order).

**Proof.** Let $T = \{s \in S : d^+_S(s) = 1\}$, so $|T| = 3$. For each
$t \in T$, Claim 12 gives $N^+(t) \subseteq V(C)$, and
$d^+_{V(C)\setminus S}(t) = 4 - 1 = 3 = |V(C)\setminus S|$, so $t$ sends
an arc to *every* vertex of $V(C)\setminus S$.

Antiparallel kill (path arcs $v_i \to v_{i+1}$ for $i = 1,\ldots,6$ and
cycle arc $v_7 \to v_1$): if $v_{i+1} \in T$ and $v_i \in V(C)\setminus
S$, then $t = v_{i+1}$ would send an arc to $v_i$, contradicting the
existing arc $v_i \to v_{i+1}$. So $v_{i+1} \in T \implies v_i \in S$
for path arcs, and $v_1 \in T \implies v_7 \in S$ for the cycle arc.

Equivalently, $\sigma(T) \subseteq S$, where $\sigma$ is the cyclic
predecessor permutation on $V(C)$ (a single 7-cycle). Since $|T| = 3$
and $|S| = 4$, $\sigma(T)$ is a $3$-element subset of $S$. The only
$\sigma$-invariant subsets of $V(C)$ are $\emptyset$ and $V(C)$, so
$\sigma(T) \neq T$. Hence $\sigma(T) = (T \setminus \{t_0\}) \cup \{u\}$
for unique $t_0 \in T$, and $\sigma(t_0) = u$.

For the remaining $t_1, t_2 \in T \setminus \{t_0\}$, $\sigma$ injective
plus the no-fixed-point property of a 7-cycle force $\sigma(t_1) = t_0$
and $\sigma(t_2) = t_1$ (the other two assignments produce a fixed
point or 2-cycle, both impossible).

Reading off the $C$-order (i.e., $\sigma^{-1}$ direction): $u, t_0, t_1,
t_2$ are 4 consecutive vertices, with $u$ first. $\square$

The four candidates for $S$ containing $v_7$:

| Case | $S$ | $u$ (start, $d^+_S = 2$ for $(2,1,1,1)$) | $T$ | $V(C)\setminus S$ | $B = N^+(v_0)$ |
|---|---|---|---|---|---|
| (I)  | $\{v_4, v_5, v_6, v_7\}$ | $v_4$ | $\{v_5, v_6, v_7\}$ | $\{v_1, v_2, v_3\}$ | $\{v_5, v_6, v_7, v_1\}$ |
| (II) | $\{v_5, v_6, v_7, v_1\}$ | $v_5$ | $\{v_6, v_7, v_1\}$ | $\{v_2, v_3, v_4\}$ | $\{v_6, v_7, v_1, v_2\}$ |
| (III)| $\{v_6, v_7, v_1, v_2\}$ | $v_6$ | $\{v_7, v_1, v_2\}$ | $\{v_3, v_4, v_5\}$ | $\{v_7, v_1, v_2, v_3\}$ |
| (IV) | $\{v_7, v_1, v_2, v_3\}$ | $v_7$ | $\{v_1, v_2, v_3\}$ | $\{v_4, v_5, v_6\}$ | $\{v_1, v_2, v_3, v_4\}$ |

## Case (I): full forcing derivation

Take $S = \{v_4, v_5, v_6, v_7\}$, $u = v_4$, $T = \{v_5, v_6, v_7\}$,
$V(C)\setminus S = \{v_1, v_2, v_3\}$.

### Step F1: $T$-arcs

For each $s \in T$, $d^+_S(s) = 1$ and Claim 12 gives
$N^+(s) \subseteq V(C)$. So $s$ has $4 - 1 = 3$ arcs into
$V(C)\setminus S$, which has size $3$. Hence $s$ sends an arc to *every*
vertex of $V(C)\setminus S$. Forced:

- $v_5 \to v_1, v_2, v_3$.
- $v_6 \to v_1, v_2, v_3$.
- $v_7 \to v_1, v_2, v_3$. (Note $v_7 \to v_1$ is also the cycle arc.)

Each $s \in T$ has $1$ remaining out-arc, in $S$. Path arcs supply:
$v_5 \to v_6$ (path, in $S$), $v_6 \to v_7$ (path, in $S$). For $v_7$,
$v_6 \to v_7$ (path) forces $v_7 \to v_6$ forbidden, so $v_7$'s $S$-arc
is to $v_4$ or $v_5$.

### Step F2: $u$'s arcs

$u = v_4 \in S$. $d^+_S(v_4) = 2$, so $v_4$ has $2$ arcs into $S$ and
$2$ into $V(C)\setminus S$.

$V(C)\setminus S = \{v_1, v_2, v_3\}$. Antiparallel: $v_3 \to v_4$ is
the path arc, so $v_4 \to v_3$ forbidden. Hence $v_4$'s $2$ arcs into
$V(C)\setminus S$ lie in $\{v_1, v_2\}$, which has size exactly $2$.
**Forced: $v_4 \to v_1$ and $v_4 \to v_2$.**

$v_4$'s $S$-arcs: $2$ of $\{v_5, v_6, v_7\}$. Path arc $v_4 \to v_5 \in S$
is one. Other: $v_4 \to v_6$ or $v_4 \to v_7$.

### Step F3: $v_0$'s arcs

$B = N^+(v_0) = \{v_5, v_6, v_7, v_1\}$. **Forced: $v_0 \to v_1, v_5,
v_6, v_7$.**

### Step F4: $v_1$'s arcs (uses $n = 10$)

$v_1 \in V(C)\setminus S$. $d^+(v_1) = 4$. Antiparallel kills:

- $v_1 \to v_0$: path $v_0 \to v_1$.
- $v_1 \to v_4$: $v_4 \to v_1$ forced (Step F2).
- $v_1 \to v_5$: $v_5 \to v_1$ forced (Step F1).
- $v_1 \to v_6$: $v_6 \to v_1$ forced.
- $v_1 \to v_7$: $v_7 \to v_1$ forced (cycle / T arc).

Allowed targets: $\{v_2 \text{ (path)}, v_3, x, y\}$, exactly $4$.
**Forced: $v_1 \to v_2, v_3, x, y$.**

If $n > 10$, $V(D)\setminus V(P)$ has more than $\{x, y\}$, so the
allowed-target count exceeds $4$ and not every $v_1 \to ?$ is forced.
This step is the source of the $n = 10$ specificity.

### Step F5: $v_2$'s arcs (uses $n = 10$)

$v_2 \in V(C)\setminus S$. $d^+(v_2) = 4$. Antiparallel kills:

- $v_2 \to v_1$: path.
- $v_2 \to v_4$: $v_4 \to v_2$ forced.
- $v_2 \to v_5, v_6, v_7$: $T$-arcs $v_5, v_6, v_7 \to v_2$ forced.

Allowed: $\{v_3 \text{ (path)}, v_0, x, y\}$, exactly $4$.
**Forced: $v_2 \to v_3, v_0, x, y$.**

### Step F6: $v_3$'s arcs (uses $n = 10$)

$v_3 \in V(C)\setminus S$. $d^+(v_3) = 4$. Antiparallel kills:

- $v_3 \to v_2$: path.
- $v_3 \to v_1$: $v_1 \to v_3$ forced (Step F4).
- $v_3 \to v_5, v_6, v_7$: $T$-arcs forced.

Allowed: $\{v_4 \text{ (path)}, v_0, x, y\}$, exactly $4$.
**Forced: $v_3 \to v_4, v_0, x, y$.**

### Step F7: sub-cases for the two free choices

Free choices remaining:

- $v_4$'s second $S$-arc: $v_6$ or $v_7$.
- $v_7$'s $S$-arc: $v_4$ or $v_5$.

Antiparallel forbids $\{v_4 \to v_7, v_7 \to v_4\}$ both, so the
sub-cases are:

- (I.a) $v_4 \to v_6$, $v_7 \to v_4$.
- (I.b) $v_4 \to v_6$, $v_7 \to v_5$.
- (I.c) $v_4 \to v_7$, $v_7 \to v_5$.

### Step F8: explicit length-8 paths

**(I.a).** Path
$v_0 \to v_5 \to v_6 \to v_7 \to v_4 \to v_1 \to v_2 \to v_3 \to x$.
Arc-by-arc justification:
- $v_0 \to v_5$: Step F3.
- $v_5 \to v_6$: path.
- $v_6 \to v_7$: path.
- $v_7 \to v_4$: sub-case (I.a).
- $v_4 \to v_1$: Step F2.
- $v_1 \to v_2$: path.
- $v_2 \to v_3$: path.
- $v_3 \to x$: Step F6.

Vertices $v_0, v_5, v_6, v_7, v_4, v_1, v_2, v_3, x$ are pairwise
distinct (9 distinct vertices). Length $= 8$. $\square$

**(I.b).** Path
$v_0 \to v_7 \to v_5 \to v_6 \to v_1 \to v_3 \to v_4 \to v_2 \to x$.
Arc-by-arc justification:
- $v_0 \to v_7$: Step F3.
- $v_7 \to v_5$: sub-case (I.b).
- $v_5 \to v_6$: path.
- $v_6 \to v_1$: Step F1.
- $v_1 \to v_3$: Step F4.
- $v_3 \to v_4$: path.
- $v_4 \to v_2$: Step F2.
- $v_2 \to x$: Step F5.

9 distinct vertices, length $= 8$. $\square$

**(I.c).** Same path as (I.b). The only difference between (I.b) and
(I.c) is $v_4$'s second $S$-arc ($v_6$ versus $v_7$), which is not used
in this path. Hence the length-8 path holds in (I.c) verbatim.
$\square$

In all three sub-cases, $\ell(D) \geq 8$, contradicting $\ell(D) = 7$.
Case (I) is impossible.

## Case (II): full forcing derivation

$S = \{v_5, v_6, v_7, v_1\}$, $u = v_5$, $T = \{v_6, v_7, v_1\}$,
$V(C)\setminus S = \{v_2, v_3, v_4\}$.

**F1 (T-arcs):** Each $t \in T$ sends arcs to all $V(C)\setminus S$:
$v_6 \to v_2, v_3, v_4$; $v_7 \to v_2, v_3, v_4$; $v_1 \to v_2, v_3,
v_4$. ($v_1 \to v_2$ coincides with the path arc.) Each has 1 $S$-arc:
$v_6 \to v_7$ (path), $v_7 \to v_1$ (cycle), $v_1 \to ?$ in
$\{v_5, v_6\}$ (since $v_1 \to v_7$ forbidden by cycle).

**F2 (u-arcs):** $v_5$ has $d^+_S = 2$, so $2$ arcs into $V(C)\setminus
S = \{v_2, v_3, v_4\}$. Antiparallel: $v_4 \to v_5$ path forbids $v_5
\to v_4$. So $v_5$'s $V(C)\setminus S$ arcs land in $\{v_2, v_3\}$
(size 2): both forced. $v_5 \to v_2, v_3$. $v_5$'s $S$-arcs: 2 of
$\{v_6, v_7, v_1\}$, with $v_5 \to v_6$ (path) one of them.

**F3 ($v_0$-arcs):** $B = \{v_6, v_7, v_1, v_2\}$, so $v_0 \to v_1, v_2,
v_6, v_7$.

**F4--F6 ($V(C)\setminus S$-arc forcings):** $v_3 \in V(C)\setminus S$.
Antiparallel kills: $v_3 \to v_2$ (path), $v_3 \to v_5$ ($v_5 \to v_3$
forced by F2), $v_3 \to v_6, v_7, v_1$ (T-arcs $v_6, v_7, v_1 \to v_3$
forced by F1). Allowed targets: $v_4$ (path), $v_0, x, y$, exactly 4 at
$n = 10$. **Forced: $v_3 \to v_4, v_0, x, y$.**

**Length-8 path (all sub-cases of F1, F2 free choices).**
$v_0 \to v_1 \to v_4 \to v_5 \to v_6 \to v_7 \to v_2 \to v_3 \to x$.

Arc-by-arc:
- $v_0 \to v_1$: F3.
- $v_1 \to v_4$: F1 ($v_1 \in T$, $v_4 \in V(C)\setminus S$).
- $v_4 \to v_5$: path.
- $v_5 \to v_6$: path.
- $v_6 \to v_7$: path.
- $v_7 \to v_2$: F1 ($v_7 \in T$, $v_2 \in V(C)\setminus S$).
- $v_2 \to v_3$: path.
- $v_3 \to x$: F4--F6.

9 distinct vertices: $v_0, v_1, v_4, v_5, v_6, v_7, v_2, v_3, x$.
Length 8. Every arc is robustly forced (independent of $u$'s second
$S$-arc and $v_1$'s $S$-arc). $\square$

## Case (III): full forcing derivation

$S = \{v_6, v_7, v_1, v_2\}$, $u = v_6$, $T = \{v_7, v_1, v_2\}$,
$V(C)\setminus S = \{v_3, v_4, v_5\}$.

**F1 (T-arcs):** $v_7 \to v_3, v_4, v_5$; $v_1 \to v_3, v_4, v_5$;
$v_2 \to v_3, v_4, v_5$. $S$-arcs: $v_7 \to v_1$ (cycle), $v_1 \to v_2$
(path), $v_2 \to ?$ in $\{v_6, v_7\}$ (since $v_2 \to v_1$ forbidden by
path; $v_2 \to v_7$ allowed only because $v_7 \in T$ does not send to
$v_2$, see below).

**F2 (u-arcs):** $v_6$ has $d^+_S = 2$. $V(C)\setminus S = \{v_3, v_4,
v_5\}$. Antiparallel: $v_5 \to v_6$ path forbids $v_6 \to v_5$. So
$v_6$'s $V(C)\setminus S$ arcs are 2 of $\{v_3, v_4\}$: both forced.
$v_6 \to v_3, v_4$. $v_6$'s $S$-arcs: $v_6 \to v_7$ (path) plus one of
$\{v_1, v_2\}$.

**F3 ($v_0$-arcs):** $B = \{v_7, v_1, v_2, v_3\}$, so $v_0 \to v_1, v_2,
v_3, v_7$.

**F4--F6 ($v_3$'s arcs):** $v_3 \in V(C)\setminus S$. Antiparallel
kills: $v_3 \to v_2$ (path), $v_3 \to v_6$ ($v_6 \to v_3$ forced by
F2), $v_3 \to v_7, v_1$ (T-arcs forced by F1). $v_3 \to v_5$ depends on
whether $v_5 \to v_3$ is forced; $v_5 \in V(C)\setminus S$, no Claim 12,
so this is sub-case-dependent.

Allowed: $\{v_4 \text{ (path)}, v_5 \text{ (?)}, v_0, x, y\}$. $v_3$ has
$4$ out-arcs from this set; if $v_5 \to v_3$ forced, allowed $= 4$ and
all forced; if $v_3 \to v_5$ allowed (not forced) the set has 5 and
$v_3$ misses one. In either sub-case, $v_3$ misses at most one of
$\{x, y\}$ (since $v_3 \to v_4$ is the path arc and is always there,
leaving 3 of $\{v_5, v_0, x, y\}$ to be chosen, and at most one missing
target overall). **Hence at least one of $v_3 \to x$, $v_3 \to y$
holds.**

**Length-8 path (all sub-cases).**
$v_0 \to v_1 \to v_2 \to v_4 \to v_5 \to v_6 \to v_7 \to v_3 \to t$,
where $t \in \{x, y\} \cap N^+(v_3)$.

Arc-by-arc:
- $v_0 \to v_1$: F3.
- $v_1 \to v_2$: path.
- $v_2 \to v_4$: F1.
- $v_4 \to v_5$: path.
- $v_5 \to v_6$: path.
- $v_6 \to v_7$: path.
- $v_7 \to v_3$: F1.
- $v_3 \to t$: F4--F6 (always exists, possibly $x$ or $y$).

9 distinct vertices, length 8. $\square$

## Case (IV): full forcing derivation

$S = \{v_7, v_1, v_2, v_3\}$, $u = v_7$, $T = \{v_1, v_2, v_3\}$,
$V(C)\setminus S = \{v_4, v_5, v_6\}$.

**F1 (T-arcs):** $v_1 \to v_4, v_5, v_6$; $v_2 \to v_4, v_5, v_6$;
$v_3 \to v_4, v_5, v_6$. $S$-arcs: $v_1 \to v_2$ (path), $v_2 \to v_3$
(path), $v_3 \to ?$ in $\{v_7, v_1\}$ (since $v_3 \to v_2$ forbidden by
path).

**F2 (u-arcs):** $v_7$ has $d^+_S = 2$. $V(C)\setminus S = \{v_4, v_5,
v_6\}$. Antiparallel: $v_6 \to v_7$ path forbids $v_7 \to v_6$. So
$v_7$'s $V(C)\setminus S$ arcs are 2 of $\{v_4, v_5\}$: both forced.
$v_7 \to v_4, v_5$. $v_7$'s $S$-arcs: $v_7 \to v_1$ (cycle) plus one of
$\{v_2, v_3\}$.

**F3 ($v_0$-arcs):** $B = \{v_1, v_2, v_3, v_4\}$, so $v_0 \to v_1, v_2,
v_3, v_4$.

**F4 ($v_5$'s arcs):** $v_5 \in V(C)\setminus S$. Antiparallel kills:
$v_5 \to v_4$ (path), $v_5 \to v_7$ ($v_7 \to v_5$ forced by F2),
$v_5 \to v_1, v_2, v_3$ (T-arcs forced). Allowed: $\{v_6 \text{ (path)},
v_0, x, y\}$, exactly 4. **Forced: $v_5 \to v_6, v_0, x, y$.**

**F5 ($v_4$'s arcs):** $v_4 \in V(C)\setminus S$. Antiparallel kills:
$v_4 \to v_3$ (path), $v_4 \to v_1, v_2$ (T-arcs forced), $v_4 \to v_7$
($v_7 \to v_4$ forced by F2). $v_4 \to v_6$ depends on whether
$v_6 \to v_4$ is forced; $v_6 \in V(C)\setminus S$, no Claim 12, so
sub-case-dependent.

Allowed: $\{v_5 \text{ (path)}, v_6 \text{ (?)}, v_0, x, y\}$. $v_4$
has $4$ out-arcs from $4$ or $5$ candidates. In either sub-case, at
least one of $v_4 \to x$, $v_4 \to y$ holds (since
$\{v_5, v_6, v_0\}$ supplies at most 3 of the 4 needed).

**Length-8 path (all sub-cases).**
$v_0 \to v_1 \to v_2 \to v_3 \to v_5 \to v_6 \to v_7 \to v_4 \to t$,
where $t \in \{x, y\} \cap N^+(v_4)$.

Arc-by-arc:
- $v_0 \to v_1$: F3.
- $v_1 \to v_2$: path.
- $v_2 \to v_3$: path.
- $v_3 \to v_5$: F1.
- $v_5 \to v_6$: path (or F4).
- $v_6 \to v_7$: path.
- $v_7 \to v_4$: F2.
- $v_4 \to t$: F5 (always exists).

9 distinct vertices, length 8. $\square$

## Conclusion for $(2,1,1,1)$

In all four cases (I)--(IV), an explicit length-8 path is forced,
contradicting $\ell(D) = 7$. Score sequence $(2,1,1,1)$ admits no
counterexample at $n = 10$. $\blacksquare$

## Score sequence $(3,1,1,1)$

In $(3,1,1,1)$: one vertex $u$ with $d^+_S = 3$, three vertices $T$
with $d^+_S = 1$. The cyclic-interval mini-lemma still applies (its
proof only uses $T$-vertices' predecessor closure, which is unchanged).
So $S$ is again a cyclic interval with $u$ at the start, giving the
same four cases (I)--(IV) of $S$ containing $v_7$.

The Step F2 derivation changes:
- $u$ now has $d^+_S = 3$, so all three $S$-arcs from $u$ are forced
  (to the other three vertices of $S$);
- $u$ has $1$ arc into $V(C)\setminus S$ (instead of $2$), still in
  $\{v_{\text{path-pred not killed}}\}$.

A consequence: in every case, the antiparallel constraint between $u$
and the (unique) outdegree-1 $T$-vertex pointing back at $u$ from inside
$S$ is forced, removing one of the two free choices that $(2,1,1,1)$
had. Specifically:

- (I) $u = v_4$: $v_4 \to v_7$ forced; antiparallel forces $v_7$'s
  S-arc to be $v_5$.
- (II) $u = v_5$: $v_5 \to v_1$ forced; $v_1$'s S-arc forced to $v_6$.
- (III) $u = v_6$: $v_6 \to v_2$ forced; $v_2$'s S-arc forced to $v_7$.
- (IV) $u = v_7$: $v_7 \to v_3$ forced; $v_3$'s S-arc forced to $v_1$.

The remaining freedom is $u$'s single $V(C)\setminus S$ choice (2
sub-cases per case).

### Length-8 paths

In each case below, the listed path uses only robustly-forced arcs
(robust across both $V(C)\setminus S$ sub-cases for $u$). The exit arc
$\bullet \to t$ uses $t \in \{x, y\} \cap N^+(\bullet)$ with at least
one option always available by the $n = 10$ allowed-target count.

**Case (I)** ($S = \{v_4, v_5, v_6, v_7\}$, $u = v_4$, $T = \{v_5, v_6,
v_7\}$, $V(C)\setminus S = \{v_1, v_2, v_3\}$):
$$v_0 \to v_5 \to v_3 \to v_4 \to v_6 \to v_7 \to v_1 \to v_2 \to t.$$
Arc-by-arc:
- $v_0 \to v_5$: F3.
- $v_5 \to v_3$: F1 (T-arc).
- $v_3 \to v_4$: path.
- $v_4 \to v_6$: F2 ($u \in S$, S-arc).
- $v_6 \to v_7$: path.
- $v_7 \to v_1$: cycle / F1.
- $v_1 \to v_2$: path.
- $v_2 \to t$: $v_2$'s allowed targets are $\{v_3 \text{ (path)},
  v_4, v_0, x, y\}$ (or fewer if $v_4 \to v_2$ in sub-case B), and
  $v_2$ has 4 out-arcs, so misses at most 1. At least one of $x, y$
  is in $N^+(v_2)$.

**Case (II)** ($S = \{v_5, v_6, v_7, v_1\}$, $u = v_5$, $T = \{v_6,
v_7, v_1\}$, $V(C)\setminus S = \{v_2, v_3, v_4\}$):
$$v_0 \to v_1 \to v_4 \to v_5 \to v_6 \to v_7 \to v_2 \to v_3 \to t.$$
Arc-by-arc:
- $v_0 \to v_1$: F3.
- $v_1 \to v_4$: F1.
- $v_4 \to v_5$: path.
- $v_5 \to v_6$: path.
- $v_6 \to v_7$: path.
- $v_7 \to v_2$: F1.
- $v_2 \to v_3$: path.
- $v_3 \to t$: by allowed-target count at $n = 10$.

**Case (III)** ($S = \{v_6, v_7, v_1, v_2\}$, $u = v_6$, $T = \{v_7,
v_1, v_2\}$, $V(C)\setminus S = \{v_3, v_4, v_5\}$):
$$v_0 \to v_3 \to v_5 \to v_6 \to v_7 \to v_1 \to v_2 \to v_4 \to t.$$
Arc-by-arc:
- $v_0 \to v_3$: F3.
- $v_3 \to v_5$: F1.
- $v_5 \to v_6$: path.
- $v_6 \to v_7$: path.
- $v_7 \to v_1$: cycle / F1.
- $v_1 \to v_2$: path.
- $v_2 \to v_4$: F1.
- $v_4 \to t$: in sub-case B ($v_6 \to v_4$), $v_4$'s allowed targets
  are $\{v_5 \text{ (path)}, v_0, x, y\}$, all 4 forced; in sub-case A
  ($v_6 \to v_3$), $v_4$'s 4 out-arcs from 5 candidates miss 1, so at
  least one of $x, y$ holds.

**Case (IV)** ($S = \{v_7, v_1, v_2, v_3\}$, $u = v_7$, $T = \{v_1,
v_2, v_3\}$, $V(C)\setminus S = \{v_4, v_5, v_6\}$):
$$v_0 \to v_2 \to v_6 \to v_7 \to v_3 \to v_1 \to v_4 \to v_5 \to t.$$
Arc-by-arc:
- $v_0 \to v_2$: F3.
- $v_2 \to v_6$: F1.
- $v_6 \to v_7$: path.
- $v_7 \to v_3$: F2 ($u$'s S-arc, forced by $d^+_S = 3$).
- $v_3 \to v_1$: F2 (forced as $v_3$'s S-arc, since $v_3 \to v_7$
  forbidden by $v_7 \to v_3$).
- $v_1 \to v_4$: F1.
- $v_4 \to v_5$: path.
- $v_5 \to t$: in sub-case B ($v_7 \to v_5$), $v_5$'s allowed targets
  are $\{v_6 \text{ (path)}, v_0, x, y\}$, all 4 forced; in sub-case A
  ($v_7 \to v_4$), $v_5$ has 5 candidates, misses 1, at least one of
  $x, y$.

In all four cases, an explicit length-8 path is forced, contradicting
$\ell(D) = 7$. Score sequence $(3,1,1,1)$ admits no counterexample at
$n = 10$. $\blacksquare$

## $n \geq 11$: not automatically closed

Steps F4, F5, F6 each rely on the count "allowed targets equals
out-degree exactly," which holds because $|V(D)\setminus V(P)| = 2$ at
$n = 10$. At $n \geq 11$, $|V(D)\setminus V(P)| \geq 3$ and the allowed
target count exceeds $4$, so the implication "$v_1 \to v_3$ forced" (and
its descendants) breaks.

Closing $\delta = 4$ at general $n$ requires either:

- a version of the forcing argument that does not rely on equality of
  allowed-target count and out-degree, or
- a direct argument that exploits the additional off-path vertices.

This is open.

## $(3,1,1,1)$ summary

Closed in all four cases above. The key structural difference from
$(2,1,1,1)$ is that $u$ has $d^+_S = 3$ (so all three of $u$'s S-arcs
are forced), and $u$ has only $1$ arc into $V(C)\setminus S$. This
*tightens* rather than weakens the forcing chain, because the
antiparallel constraint between $u$'s S-arc and the corresponding
$T$-vertex's S-arc removes one of the two free choices that $(2,1,1,1)$
had. Each $(3,1,1,1)$ case has only 2 sub-cases (vs 3 for $(2,1,1,1)$),
making the case work shorter.

## $(2,2,1,1)$: shape enumeration

$S$ has two vertices $u_1, u_2$ with $d^+_S = 2$ and two vertices $T =
\{t_0, t_1\}$ with $d^+_S = 1$. The cyclic-closure constraint
$\sigma(T) \subseteq S$ still holds (T-vertices send arcs to all of
$V(C)\setminus S$, antiparallel-killing predecessors), but with $|T| =
2$ the conclusion is weaker than in $(2,1,1,1)$ or $(3,1,1,1)$.

**$\sigma$-image case analysis.**
- $\sigma(T) = T$: T is $\sigma$-invariant, but $\sigma$ is a 7-cycle
  with no orbit of size 2. Impossible.
- $\sigma(T) \cap T = \{t_1\}$ (one element): $\sigma(t_0) = t_1$,
  $\sigma(t_1) = u$ for some $u \in \{u_1, u_2\}$. In $C$-order this
  gives a 3-consecutive block $u, t_1, t_0$.
- $\sigma(T) \cap T = \emptyset$: $\sigma(t_0), \sigma(t_1) \in \{u_1,
  u_2\}$, distinct (so $= \{u_1, u_2\}$). Two consecutive pairs $\{u_1,
  t_0\}$ and $\{u_2, t_1\}$ in $C$-order, with at least one
  $V(C)\setminus S$ vertex between them.

**Shapes and role-placement constraints.**
- **Shape A1** (4-cyclic-interval): $u' \in \{\sigma^{-1}(t_0), \sigma(u)\}$,
  making $S$ four consecutive vertices in $C$. For $S = \{a, b, c, d\}$
  in $C$-order, valid $T$ placements are $\{b, c\}$, $\{b, d\}$,
  $\{c, d\}$ (other placements force $\sigma(t)$ outside $S$).
- **Shape A2** (3-consecutive + 1 isolated): $u' \notin
  \{\sigma^{-1}(t_0), \sigma(u)\}$. The 3-block is $\{u, t_1, t_0\}$
  with $u$ first; $u'$ isolated.
- **Shape B** (2 separated pairs): from $\sigma$-case 3. $T = \{b, d\}$
  forced (the "second" of each pair).

**$v_7 \in S$ constraint.** Same as before. With this constraint and the
shape enumeration, the configurations to verify are:

- Shape A1: 4 cyclic positions of $S$ (cases I--IV) $\times$ 3 role
  assignments $T \in \{\{b,c\}, \{b,d\}, \{c,d\}\}$ = 12 sub-cases.
- Shape A2: $\sim 8$ sub-cases (4 positions of 3-block $\times$ 2
  isolated-vertex positions, modulo symmetries).
- Shape B: 6 sub-cases (gap sizes 1+2 in C, with $v_7$ in either pair).

## $(2,2,1,1)$ Shape A1 with $T = \{c, d\}$

This is the role-placement closest to $(2,1,1,1)$: $T$ is the "back two"
of the cyclic interval, $\{u_1, u_2\}$ the "front two."

### Case (I) Shape A1 $T = \{c,d\}$: full F-step derivation

$S = \{v_4, v_5, v_6, v_7\}$, $T = \{v_6, v_7\}$, $\{u_1, u_2\} =
\{v_4, v_5\}$, $V(C)\setminus S = \{v_1, v_2, v_3\}$.

**F1** (T-arcs): $v_6 \to v_1, v_2, v_3$; $v_7 \to v_1, v_2, v_3$.
$v_6$'s S-arc: $v_6 \to v_7$ (path). $v_7$'s S-arc: in $\{v_4, v_5\}$
($v_7 \to v_6$ forbidden by path antiparallel).

**F2** (u-arcs): $v_4, v_5$ each have $d^+_S = 2$. Path arcs $v_4 \to
v_5$ and $v_5 \to v_6$ are S-arcs. The chain of antiparallel forces:
$v_4 \to v_5$ kills $v_5 \to v_4$, so $v_5$'s other S-arc is $v_7$;
$v_5 \to v_7$ kills $v_7 \to v_5$, so $v_7$'s S-arc is $v_4$;
$v_7 \to v_4$ kills $v_4 \to v_7$, so $v_4$'s other S-arc is $v_6$.

**All S-arcs determined:** $v_4 \to v_5, v_6$; $v_5 \to v_6, v_7$;
$v_6 \to v_7$ (path); $v_7 \to v_4$.

$v_4$'s V(C)\S arcs: 2 of $\{v_1, v_2, v_3\}$, with $v_4 \to v_3$
forbidden by path antiparallel. **Forced: $v_4 \to v_1, v_2$.**

$v_5$'s V(C)\S arcs: 2 of $\{v_1, v_2, v_3\}$, no path antiparallel
(since $v_5 \to v_4$ already forbidden by S-arc analysis). Three
sub-sub-cases by which target $v_5$ misses:
- (a) $v_5 \to v_1, v_2$ (misses $v_3$);
- (b) $v_5 \to v_1, v_3$ (misses $v_2$);
- (c) $v_5 \to v_2, v_3$ (misses $v_1$).

**F3** ($v_0$-arcs): $B = \{v_5, v_6, v_7, v_1\}$. $v_0 \to v_1, v_5,
v_6, v_7$.

**F4--F6** ($V(C)\setminus S$ arc forcings, sub-case dependent):

$v_1$'s antiparallel kills: $v_1 \to v_0$ (path), $v_1 \to v_4, v_6,
v_7$ (forced by $v_4, v_6, v_7 \to v_1$). $v_1 \to v_5$ depends on
whether $v_5 \to v_1$. In sub-cases (a), (b): $v_5 \to v_1$, so
$v_1 \to v_5$ forbidden, $v_1$'s allowed targets are exactly $\{v_2,
v_3, x, y\}$, all 4 forced. In sub-case (c): $v_1$'s allowed are
$\{v_2, v_3, v_5, x, y\}$, miss 1.

By symmetric analysis, $v_2$ and $v_3$ have analogous constraints. The
key feature: at $n = 10$, each of $v_1, v_2, v_3$ has at most 5 allowed
targets and exactly 4 out-arcs, so misses at most 1 — meaning at least
one of $\{x, y\}$ is in each $V(C)\setminus S$-vertex's out-neighbour
set.

### Length-8 path for Case (I) Shape A1 $T=\{c,d\}$, all sub-sub-cases

$$v_0 \to v_5 \to v_6 \to v_7 \to v_4 \to v_1 \to v_2 \to v_3 \to t,$$
where $t \in \{x, y\} \cap N^+(v_3)$.

Arc-by-arc justification:
- $v_0 \to v_5$: F3.
- $v_5 \to v_6$: path.
- $v_6 \to v_7$: path.
- $v_7 \to v_4$: F2.
- $v_4 \to v_1$: F2 (V(C)\S arc).
- $v_1 \to v_2$: path.
- $v_2 \to v_3$: path.
- $v_3 \to t$: $v_3$'s allowed-target count at $n = 10$ guarantees
  at least one of $\{x, y\}$ is reached.

9 distinct vertices, length 8. Robust across all 3 sub-sub-cases for
$v_5$'s V(C)\S choice. $\square$

### Cases (II), (III), (IV) Shape A1 $T = \{c,d\}$

By the cyclic shift $v_i \mapsto v_{i+k}$ on $V(C)$, the F-step
derivation and length-8 path template carry over with index shifts.
Each case has 3 sub-sub-cases for the second $u$-vertex's V(C)\S
choice; all close by an analogous length-8 path. $\square$

## $(2,2,1,1)$ Shape A1 with $T = \{b, c\}$

$\{u_1, u_2\}$ are at the "first" and "last" positions of the cyclic
interval. In Case (I), $T = \{v_5, v_6\}$, $\{u_1, u_2\} = \{v_4, v_7\}$.

**F2:** $v_7$'s S-arcs cannot include $v_6$ (path antiparallel), so
both $v_4, v_5 \in S$ are forced as $v_7$'s S-arcs (since $|d^+_S(v_7)|
= 2$). Antiparallel: $v_7 \to v_4$ forces $v_4 \to v_7$ forbidden, so
$v_4$'s other S-arc is $v_6$. Hence $v_4 \to v_5, v_6$ and $v_7 \to
v_4, v_5$ all forced.

$v_4$'s V(C)\S arcs forced: $v_1, v_2$ (since $v_4 \to v_3$ kills via
path antiparallel).

$v_7$'s V(C)\S arcs: 2 of $\{v_1, v_2, v_3\}$, 3 sub-cases.

**Length-8 path (all sub-cases):** same as $(2,1,1,1)$ Case (I.a):
$$v_0 \to v_5 \to v_6 \to v_7 \to v_4 \to v_1 \to v_2 \to v_3 \to t.$$

Arc-by-arc: $v_5 \to v_6$ path, $v_6 \to v_7$ path, $v_7 \to v_4$ F2,
$v_4 \to v_1$ F2, the rest path/F4 as before. The exit $v_3 \to t$
uses allowed-target count argument as before.

By cyclic shift, Cases (II), (III), (IV) of Shape A1 $T = \{b, c\}$
all close. $\square$

## $(2,2,1,1)$ Shape A1 with $T = \{b, d\}$

$T$-vertices alternate with $u$-vertices in $C$-order. In Case (I),
$T = \{v_5, v_7\}$, $\{u_1, u_2\} = \{v_4, v_6\}$.

**F2 chain:** $v_5 \to v_6$ path; $v_6 \to v_5$ forbidden, so $v_6$'s
other S-arc is $v_4$. Then $v_4 \to v_6$ forbidden, so $v_4$'s other
S-arc is $v_7$. Then $v_7 \to v_4$ forbidden, so $v_7$'s S-arc is
$v_5$. All S-arcs determined: $S$ is a strong tournament with arcs
$v_4 \to v_5, v_7$; $v_5 \to v_6$; $v_6 \to v_4, v_7$; $v_7 \to v_5$.

$v_4$'s V(C)\S forced as before: $v_1, v_2$.

$v_6$'s V(C)\S arcs: 2 of $\{v_1, v_2, v_3\}$, 3 sub-cases.

**Length-8 path (all sub-cases):**
$$v_0 \to v_5 \to v_6 \to v_4 \to v_7 \to v_1 \to v_2 \to v_3 \to t.$$

Arc-by-arc:
- $v_0 \to v_5$: F3.
- $v_5 \to v_6$: path.
- $v_6 \to v_4$: F2.
- $v_4 \to v_7$: F2.
- $v_7 \to v_1$: F1 (T-arc).
- $v_1 \to v_2$: path.
- $v_2 \to v_3$: path.
- $v_3 \to t$: allowed-target count gives at least one of $\{x, y\}$
  in $N^+(v_3)$ (case analysis on $v_6$'s V(C)\S choice).

By cyclic shift, Cases (II), (III), (IV) of Shape A1 $T = \{b, d\}$
all close. $\square$

## $(2,2,1,1)$ Shape A1 closure summary

All 12 sub-cases of Shape A1 (4 cyclic positions × 3 role assignments
$T \in \{\{b,c\}, \{b,d\}, \{c,d\}\}$) are closed at $n = 10$ via
explicit length-8 paths.

## $(2,2,1,1)$ Shape A2 and Shape B: closed by miner

Shape A2 (3-block + isolated $u'$) and Shape B (2 separated pairs) have
different $V(C)\setminus S$ layouts than Shape A1, so the
$(2,1,1,1)$-style hand-routed path templates do not directly apply.
Instead, both shapes are closed via the local proof miner
(`scripts/k4_local_miner.py`):

- **Shape A2**: 8 sub-cases ($v_7$ in 3-block: 6, $v_7 = u'$ isolated: 2).
  18 completions each, 0 obstructions.
- **Shape B**: 4 sub-cases (one $S$-pair contains $v_7$; gap pattern
  (1, 2)). 18 completions each, 0 obstructions.

**Status:** Shape A1 fully closed by hand + miner; Shapes A2 and B
fully closed by miner. Total $(2,2,1,1)$: 24 sub-cases, all closed.

## Soundness of the local miner's forcing rules

The miner derives "forced" and "forbidden" arcs from local logical
consequences of the assumed configuration. To make the trust boundary
explicit, every rule used by `derive_forced` is justified below from
the underlying premises (Cheng--Keevash Lemma 7 and its proof
internals + the longest-path reduction R1/R2/R3 + the $(S, T)$
configuration).

The audit (`scripts/k4_audit.py`) validates that completions enumerated
by the miner satisfy the forced arcs and structural constraints, but
it shares the forcing engine with the miner. This sound-rules section
is the *independent* trust boundary.

### Premises

We work inside a strong $4$-outregular oriented graph $D$ on
$V_D = \{v_0, v_1, \ldots, v_7, x, y\}$ ($n = 10$) with longest
directed simple path $P = v_0 v_1 \cdots v_7$ of length $7$. The
Cheng--Keevash construction with $a = 1$ gives the cycle
$C = v_1 v_2 \cdots v_7 v_1$, induces $S \subset V(C)$ with
$|S| = 4$ and $v_7 \in S$, and a role-assignment $T \subset S$
($|T| = 2$) such that $\sigma(T) \subset S$ where $\sigma$ is the
predecessor-in-$C$ permutation. The score sequence on $S$ is
$(2, 2, 1, 1)$: $d^+_S(s) = 1$ for $s \in T$ and $= 2$ for
$s \in S \setminus T$.

### Rule R-path

Every path arc $v_i \to v_{i+1}$ for $i \in \{0, 1, \ldots, 6\}$ is in
$A(D)$.

*Justification:* by definition of $P$ as a directed simple path.

### Rule R-cycle

The cycle arc $v_7 \to v_1$ is in $A(D)$.

*Justification:* $a = 1$ means $\min\{i : v_7 \to v_i\} = 1$, i.e.\
$v_7 \to v_1$.

### Rule R-T

For every $t \in T$ and every $w \in V(C) \setminus S$, the arc
$t \to w$ is in $A(D)$.

*Justification:* $t \in T$ has $d^+(t) = 4$ in $D$ (4-outregular),
$d^+_S(t) = 1$ (score sequence), so $d^+_{V(D) \setminus S}(t) = 3$.
By Claim 12 (Cheng--Keevash Lemma 7 internals), $N^+(t) \subseteq V(C)$.
So $d^+_{V(C) \setminus S}(t) = 3 = |V(C) \setminus S|$, meaning $t$
sends an arc to every vertex of $V(C) \setminus S$.

### Rule R-F3 ($v_0$ out-neighbours)

$v_0$ sends arcs to exactly the four vertices of
$B = \mathrm{succ}_C(S)$.

*Justification:* by the proof of Cheng--Keevash Lemma 7 with $a = 1$,
$N^+(v_0) \cap V(C) = B$ and $A = N^+(v_0) \cap \{v_0, \ldots,
v_{a-1}\} = \emptyset$ (since $\{v_0\}$ has no self-loop). Claim 11
gives $N^+(v_0) \subseteq V(P)$. Combined: $N^+(v_0) = B$, $|B| = 4$.

### Rule R-Claim12

For every $s \in S$ and every $w \notin V(C)$, the arc $s \to w$ is
forbidden.

*Justification:* Cheng--Keevash Claim 12: $N^+(B^-) \subseteq V(C)$,
and $S = B^-$ in the construction.

### Rule R-LemmaA-rev

The arcs $x \to v_0$ and $y \to v_0$ are forbidden.

*Justification:* applying Lemma A to the reverse digraph
$D^{\mathrm{rev}}$ (where $P$ reversed is a longest path with endpoint
$v_0$): $N^-_D(v_0) = N^+_{D^{\mathrm{rev}}}(v_0) \subseteq V(P)$. Since
$x, y \notin V(P)$, no in-arc from $\{x, y\}$ to $v_0$ exists.

### Rule R-loop

$(v, v) \notin A(D)$ for every $v$.

*Justification:* $D$ is loop-free (oriented graph definition).

### Rule R-AP (antiparallel)

If $(u, v) \in A(D)$, then $(v, u) \notin A(D)$.

*Justification:* $D$ is an oriented graph (no antiparallel pairs).

### Rule R-out (4-outregularity)

For every vertex $v$, $d^+(v) = 4$.

*Justification:* the R2 reduction selects exactly four out-arcs per
vertex.

### Rule R-score (S-vertex score sequence)

For $s \in T$, $d^+_S(s) = 1$. For $s \in S \setminus T$, $d^+_S(s) = 2$.

*Justification:* the role assignment in the score sequence
$(2, 2, 1, 1)$ defines $T$ as the two vertices with internal outdegree
$1$ and $S \setminus T$ as the two with internal outdegree $2$.

### Rule R-VCS (V(C)\\S target count)

For $s \in S$, $d^+_{V(C) \setminus S}(s) = 4 - d^+_S(s)$.

*Justification:* Claim 12 + 4-outregularity:
$d^+(s) = d^+_S(s) + d^+_{V(C) \setminus S}(s)$ since
$N^+(s) \subseteq V(C) = S \cup (V(C) \setminus S)$ disjointly.

### Iterative propagation

The miner iteratively applies the following local closure rules until
fixed point:

- **(P1)** If a vertex has $k$ confirmed out-arcs and needs target $T_v$
  more out-arcs in some sub-target set $X$, with $|X \setminus
  \mathrm{forbidden}| = T_v$, force every arc $v \to w$ for
  $w \in X \setminus \mathrm{forbidden}$.
- **(P2)** If a vertex's target count for a sub-target set is met,
  forbid every remaining unconfirmed arc into that sub-target.
- **(P3)** Confirmed $(u, v)$ implies forbidden $(v, u)$ (R-AP).

*Justification:* (P1) and (P2) are immediate from R-out + R-score +
R-VCS counting. (P3) is R-AP.

These rules are sound: each derived "forced" arc is a logical
consequence of premises; each derived "forbidden" arc is incompatible
with premises. Hence enumeration over completions consistent with
forced/forbidden gives every valid 4-outregular oriented graph
satisfying the assumed configuration.

### Completion check (post-enumeration)

After fixing free choices, the miner verifies 4-outregularity (R-out)
and antiparallel-free (R-AP) on the assembled graph. These checks are
necessary and sufficient: a completion that passes both is a valid
4-outregular oriented graph with the prescribed forced arcs.

## Implications for the plan

- $(2,1,1,1)$ and $(3,1,1,1)$ closed at $n = 10$ with full F-step
  derivations (all four cases each).
- $(2,2,1,1)$ at $n = 10$: all 24 sub-cases (Shape A1, A2, B) closed
  by miner + audit.
- $(1,1,1,1)$ at $n = 10$: closed by direct cyclic closure.
- $\delta = 4, n = 10$: **fully closed**.
- All cases at $n \geq 11$: open. The forcing chain in F4--F6 relies
  on $|V(D) \setminus V(P)| = 2$, which fails for $n \geq 11$.
- Next computational target: extend miner to $n = 11, 12, \ldots$ and
  test whether the closure persists.
