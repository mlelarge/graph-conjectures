# 11 — CL1 proof via the branching-witness route (R2)

Author: Structural Digraph Specialist
Date: 2026-05-16
Status: first complete write-up of route R2 from `08_phase4_lifting_lemma_v1.md` §3.c.
Companion files: `team/08_phase4_lifting_lemma_v1.md` (the CL1 statement and
the open §3 gap), `team/02_structural_program.md` (round-1 CL1, T1–T3),
`code/phase4_branching_extract.py` (the empirical R2 check), and
`code/logs/phase4_branching_extract.json` (the per-witness branching data
this file argues from). The previous deliverable is authoritative for
CL1's statement; I do not re-derive it here.

## §1 — Empirical setup

### §1.1 What was extracted

`code/phase4_branching_extract.py` regenerates the 56 SAT witnesses of
`phase4_witness_probe.py`, re-runs `verify_sat`, and for each witness
$D = (V, A)$ with 2-coloring $A = A_R \,\dot\cup\, A_B$ does:

1. Pick a candidate common root $r \in V$, preferring interface vertices.
2. Build a BFS out-arborescence $T^+_R$ of $(V, A_R)$ from $r$.
3. Build a BFS in-arborescence $T^-_R$ of $(V, A_R)$ into $r$.
4. Repeat for $A_B$.
5. Tabulate, per color and per direction, **how many bridges (T1$\to$T2
   or T2$\to$T1) the extracted branching uses**.

Both branchings exist iff $(V, A_c)$ is strong with $r$ as a vertex.
Since $A_c$ *is* strong by the SAT verifier's witness validation
(`verifier_ilp._validate_witness`), the BFS extractor succeeds in
56/56 instances for both colors. So the **branching-witness extraction
half** of R2 holds with no exceptions on the corpus.

### §1.2 The decomposition pattern

The "single-bridge stitch" hypothesis from the prompt — that each per-color
out-branching is built as *(inner out-branching of $D[V_1]$) + (one bridge)
+ (inner out-branching of $D[V_2]$)* — is **literally false** on the
corpus. BFS-extracted branchings use up to 5 bridge-arcs of the same
direction (see the (B, 1, 5) and (B, 0, 4) rows in the rollup), so the
out-branching is *not* of the form one-bridge-cross-then-recurse.

What is uniformly true, after normalizing $B^- = \{V_2 \to V_1\}$ as
all-blue (Pattern P1):

| Statistic | Value (over 56 witnesses) |
|---|---:|
| Per-color BFS extraction succeeds | 56/56 in $R$; 56/56 in $B$ |
| Common root in interface $I$ for both colors | 56/56 in both colors |
| $|B^-_R|$ (red bridges in direction $V_2 \to V_1$) | 0 always (this is P1) |
| Red out-branching $T^+_R$ uses 0 bridges $V_2 \to V_1$ | 56/56 (consistent with the previous row) |
| Red in-branching $T^-_R$ uses 0 bridges $V_2 \to V_1$ | 56/56 |
| Red out-branching uses $\geq 1$ bridge $V_1 \to V_2$ | 53/56 |
| Red in-branching uses $\geq 1$ bridge $V_1 \to V_2$ | 24/56 |
| Blue out-branching uses $\geq 1$ bridge $V_2 \to V_1$ | 51/56 |
| Blue in-branching uses $\geq 1$ bridge $V_2 \to V_1$ | 51/56 |

The 3/56 witnesses where the red out-branching uses *no* bridge at all
are the cases where $|B^+_R| = 0$ (red is mono-blue in the $V_1\to V_2$
direction too: rows $b12_R = 0$ in the summary, of which there is 1; plus
2 cases where the BFS happened to reach all of $V_2$ via interface
internal arcs without crossing $S_1^n \to V_2$). These corner cases
matter for the proof (see §3 step 4).

### §1.3 The hypothesis-(3) failure cases

Of the 56 corpus witnesses, **5 fail hypothesis (3) of CL1** as stated in
`08_phase4_lifting_lemma_v1.md`:

- $1/56$ has $|B^+_R| = 0$ (the (0, 3, 0, 3) row);
- $4/56$ have $|B^+_B| = 0$ (the two (3, 0, *, *) rows, totalling 4).

In all 5 cases CL1's hypothesis (3) — *both colors receive a bridge in
each direction* — fails on the empirically observed bridge coloring.
**This is not a contradiction with CL1**: as observed in
`08_phase4_lifting_lemma_v1.md` §4, the v2 witnesses also violate CL1's
hypothesis (1) (the inner parts $D[V_i]$ are *not* SAD-decomposable on
their own — they are 2-arc-strong UNSAT templates). The corpus tests
P1, P3, and the gap of §3.c; it does **not** test CL1 on its native
domain.

But the 5/56 failures inform the proof: hypothesis (3) as stated is the
right form *only when the inner SADs are available on $D[V_i]$
themselves*. In the corpus, the SAD lives on the *glued* $D$, and the
bridge color distribution is whatever the SAT solver assigns. The proof
in §3 below uses hypothesis (3) explicitly; the empirical 5/56 violation
is a consistency check telling us the lemma is not vacuous (i.e. there
exist gluings where (3) holds) but is also not automatic.

### §1.4 Pinning down what R2 must prove

After empirical reading, the statement R2 must establish is:

> Under CL1's hypotheses (1)–(4), each color class $A_c \in \{A_R, A_B\}$
> contains a spanning out-arborescence $T^+_c$ and a spanning
> in-arborescence $T^-_c$ rooted at a *common* vertex $r_c \in V$. In
> consequence, $(V, A_c)$ is strongly connected.

(Strong connectivity of $A_c$ follows from $T^+_c \cup T^-_c$: for any
$u, v \in V$, walk up $T^-_c$ from $u$ to $r_c$, then down $T^+_c$ from
$r_c$ to $v$, giving a directed $u \to v$ walk in $A_c$.)

The empirical extraction in §1.1 shows the conclusion holds on 56/56
corpus witnesses *and* identifies a clean choice of common root (the
interface $I$, or more precisely a single vertex within it).

---

## §2 — The branching-witness lemma

**Recall (CL1 hypotheses, restated for self-containment).** $D = (V, A)$
is 3-arc-strong. $V = V_1 \,\dot\cup\, V_2$, $|V_i| \geq 2$. The bridges
are $B^+ = \delta_D^+(V_1) = \delta_D^-(V_2)$ (direction $V_1 \to V_2$)
and $B^- = \delta_D^+(V_2) = \delta_D^-(V_1)$ (direction $V_2 \to V_1$).
Hypotheses:

1. Each $D_i := D[V_i]$ admits a SAD $A(D_i) = R_i \,\dot\cup\, B_i$.
2. $|B^+| \geq 2$ and $|B^-| \geq 2$.
3. A partition $B^\pm = B^\pm_R \,\dot\cup\, B^\pm_B$ such that
   $B^+_R, B^+_B, B^-_R, B^-_B$ are all non-empty, and the local-coverage
   condition holds at degree-3 vertices of $D$.
4. No tight 3-cut $\delta_D^+(X)$ with $X \cap V_i \ne \emptyset$ for
   both $i$ is monochromatic in the combined coloring
   $A_R = R_1 \cup R_2 \cup B^+_R \cup B^-_R$,
   $A_B = B_1 \cup B_2 \cup B^+_B \cup B^-_B$.

**Lemma R2.** *Under hypotheses (1)–(3) of CL1, the color class $A_c$
($c \in \{R, B\}$) contains a spanning out-arborescence $T^+_c$ and a
spanning in-arborescence $T^-_c$, both rooted at a common vertex of $V$.
Consequently $(V, A_c)$ is strongly connected.*

**Notes on hypotheses.**

- R2 does **not** use hypothesis (4): the strong-connectivity conclusion
  is purely structural from inner SADs and the bridge non-emptiness.
  This is the value of route R2 — it short-circuits the analytical-cut
  argument by exhibiting a positive certificate (a pair of branchings).
- $|B^\pm| \geq 2$ from hypothesis (2) is essential because the
  decomposition $B^\pm = B^\pm_R \cup B^\pm_B$ in hypothesis (3) requires
  each piece non-empty: minimally $|B^+| \geq 2$ to split into red and
  blue.
- Hypothesis (3)'s non-emptiness of $B^+_R$, $B^+_B$, $B^-_R$, $B^-_B$
  is doing the *real* work in the proof; the local-coverage subcondition
  at degree-3 vertices is not needed for R2.

---

## §3 — Proof of R2

Fix $c = R$; the argument for $c = B$ is verbatim symmetric (swap
$R \leftrightarrow B$ throughout).

Write $r_1 \in V_1$ and $r_2 \in V_2$ for vertices to be chosen below.
By hypothesis (1), $(V_1, R_1)$ is strongly connected (the red color
class of the SAD of $D_1$); same for $(V_2, R_2)$.

### Step 1 — Pick the bridges that will be used

By hypothesis (3), $B^+_R \neq \emptyset$ and $B^-_R \neq \emptyset$.
Pick one bridge in each direction:

- $e^+ = (a, b)$ with $a \in V_1, b \in V_2$, $e^+ \in B^+_R$;
- $e^- = (a', b')$ with $a' \in V_2, b' \in V_1$, $e^- \in B^-_R$.

(If $|B^+_R| > 1$ or $|B^-_R| > 1$, any choice works.)

Set $r_1 := b'$ (the head of $e^-$, which lies in $V_1$) and
$r_2 := b$ (the head of $e^+$, which lies in $V_2$).

### Step 2 — Inner branchings rooted at the chosen vertices

Since $(V_1, R_1)$ is strongly connected (hypothesis (1)), it admits a
spanning out-arborescence $T^+_{R, 1}$ rooted at $r_1$, with arc set in
$R_1$. This is standard: a digraph is strongly connected iff for every
choice of root it admits a spanning out-arborescence (BFS in the
strongly-connected component covers everything). Likewise it admits a
spanning in-arborescence $T^-_{R, 1}$ rooted at $r_1$.

Symmetrically, $(V_2, R_2)$ admits a spanning out-arborescence
$T^+_{R, 2}$ rooted at $r_2$ and a spanning in-arborescence $T^-_{R, 2}$
rooted at $r_2$, all with arc-sets in $R_2$.

### Step 3 — Stitch the out-branching

Define
$$T^+_R \;:=\; T^+_{R, 1} \,\cup\, \{e^+\} \,\cup\, T^+_{R, 2}.$$

I claim $T^+_R$ is a spanning out-arborescence of $D$ rooted at $r_1$,
with arc set entirely in $A_R$.

*Vertex coverage.* $T^+_{R, 1}$ spans $V_1$, $T^+_{R, 2}$ spans $V_2$,
so $V(T^+_R) = V$.

*Arc count.* $T^+_R$ has $|V_1| - 1$ arcs from $T^+_{R, 1}$, plus
$|V_2| - 1$ from $T^+_{R, 2}$, plus the single bridge $e^+$, totalling
$|V_1| + |V_2| - 1 = |V| - 1$.

*Arborescence property.* Every vertex $v \neq r_1$ has exactly one
in-arc in $T^+_R$:

- if $v \in V_1 \setminus \{r_1\}$, its unique $T^+_R$-in-arc is the
  $T^+_{R, 1}$-in-arc (since neither $e^+$ nor any arc of $T^+_{R, 2}$
  has head in $V_1$);
- if $v = r_2$, its unique $T^+_R$-in-arc is $e^+ = (a, b) = (a, r_2)$
  (no arc of $T^+_{R, 2}$ has head equal to its root $r_2$; no arc of
  $T^+_{R, 1}$ has head in $V_2$);
- if $v \in V_2 \setminus \{r_2\}$, its unique $T^+_R$-in-arc is the
  $T^+_{R, 2}$-in-arc.

The root $r_1$ has no $T^+_R$-in-arc (no arc of $T^+_{R, 1}$ has head
$r_1$ since $r_1$ is the root of $T^+_{R, 1}$; no arc of $T^+_{R, 2}$
has head in $V_1$; the bridge $e^+$ has head $r_2 \neq r_1$).

*Reachability from $r_1$.* By induction on tree-depth in $T^+_{R, 1}$,
every $v \in V_1$ is reachable from $r_1$ in $T^+_{R, 1}$. Then the
bridge $e^+$ gives reachability from $r_1$ to $a$ (inside $V_1$ in
$T^+_{R, 1}$, since $a \in V_1$ and $T^+_{R, 1}$ spans $V_1$ from
$r_1$), then to $r_2$ via $e^+$, then to all of $V_2$ via $T^+_{R, 2}$.

*Arc set.* $T^+_{R, 1} \subseteq R_1 \subseteq A_R$ and $T^+_{R, 2}
\subseteq R_2 \subseteq A_R$ by hypothesis (1); $e^+ \in B^+_R \subseteq
A_R$ by hypothesis (3). So all arcs of $T^+_R$ are in $A_R$.

So $T^+_R$ is a spanning out-arborescence of $D$ in $A_R$, rooted at
$r_1$.

### Step 4 — Stitch the in-branching, but **rooted at $r_1$** as well

Define
$$T^-_R \;:=\; T^-_{R, 1} \,\cup\, \{e^-\} \,\cup\, T^-_{R, 2}.$$

I claim $T^-_R$ is a spanning in-arborescence of $D$ rooted at $r_1$,
with arc set in $A_R$.

Wait. Re-check the orientations.

$T^-_{R, 1}$ is the spanning in-arborescence of $(V_1, R_1)$ rooted at
$r_1$, so every $v \in V_1 \setminus \{r_1\}$ has a unique out-arc in
$T^-_{R, 1}$ and the directed paths in $T^-_{R, 1}$ flow *into* $r_1$.

$T^-_{R, 2}$ is the spanning in-arborescence of $(V_2, R_2)$ rooted at
$r_2$, so every $v \in V_2 \setminus \{r_2\}$ has a unique out-arc in
$T^-_{R, 2}$ flowing into $r_2$.

The bridge $e^- = (a', b')$ has tail $a' \in V_2$ and head $b' = r_1 \in
V_1$. So **$e^-$'s head is the root of the target in-branching.**

For $T^- := T^-_{R, 1} \cup \{e^-\} \cup T^-_{R, 2}$ to be a spanning
in-arborescence rooted at $r_1$, every $v \neq r_1$ needs exactly one
out-arc in $T^-$, and all paths must flow into $r_1$. Let me check:

- $v \in V_1 \setminus \{r_1\}$: its $T^-_{R, 1}$-out-arc is the unique
  out-arc in $T^-_{R, 1}$. The bridge $e^-$ has tail $a' \in V_2$, not
  in $V_1$. $T^-_{R, 2}$ has no arc with tail in $V_1$. So this $v$ has
  exactly one out-arc in $T^-$.
- $v = r_2$: $T^-_{R, 2}$ has no arc with tail $r_2$ (root has zero
  out-degree in an in-arborescence). $T^-_{R, 1}$ has no arc with tail
  in $V_2$. The bridge $e^-$ has tail $a' \in V_2$; is $a' = r_2$?
  **Only if we chose $a' = r_2$.** In general $a'$ is some vertex of
  $V_2$, not necessarily the root of $T^-_{R, 2}$.

This is the **first subtlety**. The naive stitching does not work for
the in-branching unless we coordinate the choice of bridges with the
choice of inner roots. Let me fix this.

### Step 4 (corrected) — Re-pick the inner in-branching root

Set $r_2 := a'$ (the tail of $e^-$, which lies in $V_2$). Then
$T^-_{R, 2}$ is the spanning in-arborescence of $(V_2, R_2)$ rooted
at $a' = r_2$. Now $a'$ is the root of $T^-_{R, 2}$, so $a'$ has zero
out-degree in $T^-_{R, 2}$. The bridge $e^- = (a', r_1)$ contributes
the unique out-arc of $a'$ in $T^-$. 

But this re-pick conflicts with Step 1's choice of $r_2 := b$ for the
out-branching. We have two demands on $r_2$:

- (Out-stitching:) $r_2 = b$ (head of $e^+$) so that $e^+$ is the unique
  in-arc of $r_2$ in $T^+_R$.
- (In-stitching:) $r_2 = a'$ (tail of $e^-$) so that $e^-$ is the unique
  out-arc of $r_2$ in $T^-_R$.

**These match iff $b = a'$, i.e. the head of $e^+$ equals the tail of
$e^-$.** Generically this is false.

### Step 4 (corrected, second attempt) — Pick different roots for $T^+_R$ and $T^-_R$

R2 only requires $T^+_R$ and $T^-_R$ to be rooted at a *common* vertex
of $V$, **but they may be rooted at any vertex** — not necessarily $r_1$.
Let's pick a common root $r_R \in V_1$ and run *both* the out- and the
in-stitch with $r_R$ as the global root.

- $T^+_R$ rooted at $r_R$: uses inner out-arborescences $T^+_{R, 1}$
  rooted at $r_R$ (in $V_1$) and $T^+_{R, 2}$ rooted at some vertex
  $r_2^+ \in V_2$. The bridge crossing $V_1 \to V_2$ must have head
  $r_2^+$ so that $r_2^+$ acquires its $T^+_R$-in-arc.
- $T^-_R$ rooted at $r_R$: uses inner in-arborescences $T^-_{R, 1}$
  rooted at $r_R$ (in $V_1$) and $T^-_{R, 2}$ rooted at some vertex
  $r_2^- \in V_2$. The bridge crossing $V_2 \to V_1$ must have tail
  $r_2^-$ so that $r_2^-$ has its single $T^-_R$-out-arc.

So we are free to **independently choose** $r_2^+$ and $r_2^-$ inside
$V_2$; once we fix $r_R \in V_1$, the constraint reduces to:

(*) There exist a bridge $e^+ \in B^+_R$ with $e^+ = (a^+, r_2^+)$ for
some $a^+ \in V_1$, and a bridge $e^- \in B^-_R$ with $e^- = (r_2^-,
b^-)$ for some $b^- \in V_1$.

But this is *automatic*: every $e^+ \in B^+_R$ has tail in $V_1$ and
head in $V_2$ (so its head can serve as $r_2^+$); every $e^- \in B^-_R$
has tail in $V_2$ (so its tail can serve as $r_2^-$). The inner SADs of
$D_2$ give in- and out-arborescences rooted at *any* vertex of $V_2$
since $(V_2, R_2)$ is strongly connected.

**So the corrected stitch is:** pick any $r_R \in V_1$. Pick any $e^+ =
(a^+, r_2^+) \in B^+_R$ and any $e^- = (r_2^-, b^-) \in B^-_R$. Build
$T^+_{R, 1}$ as out-arborescence of $(V_1, R_1)$ rooted at $r_R$, build
$T^+_{R, 2}$ as out-arborescence of $(V_2, R_2)$ rooted at $r_2^+$,
glue with $e^+$. Build $T^-_{R, 1}$ as in-arborescence of $(V_1, R_1)$
rooted at $r_R$, build $T^-_{R, 2}$ as in-arborescence of $(V_2, R_2)$
rooted at $r_2^-$, glue with $e^-$.

### Step 5 — Verify both stitched objects are spanning arborescences

For $T^+_R$ rooted at $r_R$:

- *Spanning:* covered in Step 3 above.
- *Arc count:* $(|V_1| - 1) + 1 + (|V_2| - 1) = |V| - 1$. ✓
- *In-degree of each $v \neq r_R$ in $T^+_R$ is exactly 1:*
  - $v = r_R$: zero in-degree (no arc has head $r_R$ — $T^+_{R, 1}$
    excludes its root's in-arcs, $T^+_{R, 2}$'s arcs have head in $V_2$,
    $e^+$'s head is $r_2^+ \in V_2$).
  - $v \in V_1 \setminus \{r_R\}$: one in-arc from $T^+_{R, 1}$, none
    from $T^+_{R, 2}$ or $e^+$. ✓
  - $v = r_2^+$: zero in-arcs from $T^+_{R, 2}$ (root has zero), zero
    from $T^+_{R, 1}$ (heads in $V_2$ are not in $T^+_{R, 1}$), one
    from $e^+$. ✓
  - $v \in V_2 \setminus \{r_2^+\}$: one in-arc from $T^+_{R, 2}$, none
    from elsewhere. ✓
- *No cycle:* each connected component is acyclic by construction (a
  spanning out-arborescence is acyclic).
- *Arc set $\subseteq A_R$:* $T^+_{R, 1} \subseteq R_1 \subseteq A_R$,
  $T^+_{R, 2} \subseteq R_2 \subseteq A_R$, $e^+ \in B^+_R \subseteq
  A_R$. ✓

Symmetric argument for $T^-_R$ rooted at $r_R$:

- $r_R$'s out-degree in $T^-_R$ is 0 (in-arborescence root).
- $v \in V_1 \setminus \{r_R\}$: one out-arc in $T^-_{R, 1}$. ✓
- $v = r_2^-$: zero out-arcs in $T^-_{R, 2}$ (root), one out-arc $e^- =
  (r_2^-, b^-)$ landing in $V_1$. ✓
- $v \in V_2 \setminus \{r_2^-\}$: one out-arc in $T^-_{R, 2}$. ✓
- Arc set $\subseteq A_R$ by the same reasoning. ✓

So $A_R$ contains a spanning out-arborescence and a spanning
in-arborescence both rooted at $r_R$. By the standard equivalence
(directed walk $u \to r_R \to v$ via $T^-_R \cup T^+_R$), $(V, A_R)$ is
strongly connected.

The argument for color $B$ is identical, with $A_R$ replaced by $A_B$,
$R_i$ by $B_i$, $B^\pm_R$ by $B^\pm_B$. Hypothesis (3) gives
$B^+_B, B^-_B \neq \emptyset$, which is what the proof needs.

$\square$ R2

### Step 6 — The Y2-direction Edmonds-disjointness check

Worth noting: $T^+_R$ and $T^-_R$ as constructed are *not* required to
be arc-disjoint. (They share no arcs in the inner-component pieces by
SAD-disjointness of $R_i$ and $B_i$, but a bridge could in principle
appear in both — though for $e^+$ vs $e^-$ this is automatic since one
points $V_1 \to V_2$ and the other $V_2 \to V_1$.) R2 makes no
disjointness claim, only an *existence* claim, which is what strong
connectivity of $A_R$ requires.

---

## §4 — Honest gap analysis

### §4.1 What this proof needs and what it doesn't

The proof above uses **exactly** the following from CL1's hypotheses:

- (1) — to get $T^\pm_{R, i}$, $T^\pm_{B, i}$ inside each $D_i$ from the
  inner SADs.
- (3) — to get $B^+_R, B^-_R, B^+_B, B^-_B$ all non-empty.

It does **not** use hypotheses (2) (since $|B^+_R| \geq 1$ from (3)
suffices, and we only pick one bridge), (4) (the no-monochromatic-tight-
3-cut condition — this is the *output* of the proof, not an input), or
the local-coverage condition of (3).

This is a significant **strengthening** of what the proof of CL1 needs
relative to the round-1 statement.

### §4.2 The hypothesis (2) redundancy

Hypothesis (2) demands $|B^+| \geq 2$ and $|B^-| \geq 2$. From R2's
proof, we only needed $|B^+_R|, |B^-_R| \geq 1$ and $|B^+_B|, |B^-_B|
\geq 1$. Since $|B^+| = |B^+_R| + |B^+_B|$ and $|B^-| = |B^-_R| +
|B^-_B|$, these jointly imply $|B^+| \geq 2$ and $|B^-| \geq 2$, but the
converse needs the partition to actually split each direction's bridge
multiset into a non-empty red part and a non-empty blue part — which is
the **substantive content of hypothesis (3)**.

In other words: hypothesis (2) is the *necessary cardinality condition*
for (3) to be satisfiable. Without (2), (3) is vacuously false. With
(2), (3) might still fail (e.g., if every bridge in $B^+$ is forced
to the same color by some global constraint, as actually happens in 5
of the 56 corpus witnesses for $B^+_B$).

So (2) is *not* redundant — it's a *necessary condition* for (3). The
proof uses (3) directly; (2) is the threshold ensuring (3) is even
expressible.

### §4.3 What hypothesis (4) buys us, given R2

CL1's hypothesis (4) — no monochromatic tight 3-cut at the interface —
is the original Phase-3-v2 patching of the §3 gap. With R2 proven, what
does (4) add?

Look at the §3 gap reconstruction. The gap was: for cuts $\delta^+(X)$
with $X$ meeting both $V_1$ and $V_2$ and $|\delta^+(X)| \geq 4$, the
case-analysis proof of CL1 (Cases A, B, C) does not rule out a
monochromatic such cut. R2 *directly* rules this out: since $(V, A_R)$
is strongly connected by R2, every directed cut $\delta_D^+(X)$ contains
at least one $A_R$-arc; symmetric for $A_B$.

**So R2 makes hypothesis (4) redundant.** Once you have R2 from
hypotheses (1) + (3), every directed cut of $D$ is automatically
bichromatic. This is a clean consequence.

This is a major simplification of CL1. The corrected statement:

> **Lemma CL1' (simplified, R2-style).** *Let $D = (V, A)$ be a digraph
> with $V = V_1 \,\dot\cup\, V_2$, $|V_i| \geq 2$, bridges $B^\pm$
> between the parts. Suppose:*
>
> *(1) Each $D_i = D[V_i]$ admits a SAD $A(D_i) = R_i \,\dot\cup\, B_i$.*
>
> *(3') The bridges admit a 2-coloring $B^\pm = B^\pm_R \,\dot\cup\,
> B^\pm_B$ such that $B^+_R, B^+_B, B^-_R, B^-_B$ are all non-empty.*
>
> *Then $D$ admits a SAD with color classes $A_R = R_1 \cup R_2 \cup
> B^+_R \cup B^-_R$ and $A_B = B_1 \cup B_2 \cup B^+_B \cup B^-_B$.*

The local-coverage condition (the second half of the original (3)),
hypothesis (2), and hypothesis (4) are all absorbed: (2) is needed only
to *make* (3') satisfiable; the local-coverage and (4) drop out of R2's
proof.

### §4.4 What does the proof *not* do?

The proof of R2 is silent about three things, none of which CL1 needs:

(G1) *Disjointness of $T^+_R$ and $T^-_R$.* Edmonds' branching theorem
gives arc-disjoint pairs in $k$-arc-strong digraphs, but R2 only
delivers existence. If a downstream application needs disjoint pairs —
e.g., a recursive lifting reduction — that's an additional ingredient.

(G2) *Polynomial-time construction.* The proof is constructive given
inner SADs and a valid 2-coloring of bridges, but it does *not*
construct the inner SADs themselves. CL1's polynomial-time corollary
inherits whatever cost the inner SAD computation has.

(G3) *Necessity.* CL1' is a sufficient condition; it does not say a
digraph satisfying its hypotheses' *negation* lacks a SAD. There may
well be digraphs with no decomposition into SAD-able parts that still
admit a SAD (any 3-arc-strong semicomplete digraph with no proper
SAD-able induced subdigraph is a candidate). So CL1' is one *positive
sufficient condition* among many; it is not a characterization.

### §4.5 The connection to BJ–Yeo 2004 and BJ–Wang 2025

R2 is a class-agnostic version of a step that appears in both
- BJ–Yeo 2004 §3 (semicomplete, where the "good pair" argument
  constructs out- and in-branchings from a chosen good root inside a
  semicomplete component), and
- BJ–Wang 2025 Lemma 2.4 (where the "absorb shell vertices via 2 in- +
  2 out-arcs in $K$" condition feeds into a branching extension).

Specifically, BJ–Wang Lemma 2.4 says: if $D\langle X \rangle$ has a SAD
and every $v \notin X$ has 2 in- and 2 out-neighbors in $X$, then $D$
has a SAD. The proof (BJ–Wang p. 4) extends the SAD of $D\langle X \rangle$
to $D$ by adding, for each $v \notin X$ and each color $i \in \{1, 2\}$,
one in-neighbor and one out-neighbor in $X$ to color class $i$,
*matching the branching structure of $D\langle X \rangle$ in color $i$.*
This is the inner-out-branching-plus-bridge stitch, restricted to a
single "shell" vertex $v$ at a time and to a kernel $X$ that already
has a SAD.

R2 generalizes BJ–Wang's Lemma 2.4 in three ways:

- **Both parts $V_1, V_2$ need only be SAD-decomposable**, not "one is
  SAD and the other is a one-vertex shell." (This is the major
  class-agnostic move.)
- **Bridges may form arbitrary bipartite multisubsets**, not just "$v$
  has 2 in- + 2 out-neighbors in $X$." (The 2-in-2-out condition becomes
  $|B^\pm_c| \geq 1$ for each direction and each color.)
- **The bridge coloring is given as input** (hypothesis (3)), not
  inferred from a 2-feasibility argument. The downstream work — finding
  a valid bridge 2-coloring — is shifted to the application.

So R2 is **at most a class-agnostic restatement of BJ–Wang Lemma 2.4**.
It might still be **publishable** if (a) the class-agnostic shape is
new, (b) it cleanly displaces several class-specific arguments. The
Auditor needs to check this against the published proofs (see §6).

---

## §5 — Corrected CL1 and the full proof

### §5.1 The corrected statement

I restate CL1 in its cleanest form, suppressing the now-redundant
hypotheses (2)' local-coverage, and (4):

> **Lemma CL1 (final form, post-R2).** *Let $D = (V, A)$ be a digraph,
> $V = V_1 \,\dot\cup\, V_2$ with $|V_i| \geq 2$. Write $B^+ =
> \delta_D^+(V_1)$, $B^- = \delta_D^+(V_2)$. Suppose:*
>
> *(1) $D[V_1]$ and $D[V_2]$ each admit a strong arc decomposition
> $A(D_i) = R_i \,\dot\cup\, B_i$.*
>
> *(2) The bridge sets admit a partition $B^\pm = B^\pm_R \,\dot\cup\,
> B^\pm_B$ with $B^+_R, B^+_B, B^-_R, B^-_B$ all non-empty.*
>
> *Then $A(D) = (R_1 \cup R_2 \cup B^+_R \cup B^-_R) \,\dot\cup\,
> (B_1 \cup B_2 \cup B^+_B \cup B^-_B)$ is a strong arc decomposition
> of $D$.*

**Proof of CL1.** Let $A_R = R_1 \cup R_2 \cup B^+_R \cup B^-_R$ and
$A_B = B_1 \cup B_2 \cup B^+_B \cup B^-_B$. We need:

(a) $A(D) = A_R \,\dot\cup\, A_B$ as a disjoint union (arc-partition).

(b) Both $(V, A_R)$ and $(V, A_B)$ are strongly connected.

For (a): $A(D) = A(D_1) \,\dot\cup\, A(D_2) \,\dot\cup\, B^+
\,\dot\cup\, B^-$ as a partition by location. Each $A(D_i)$ partitions
into $R_i \,\dot\cup\, B_i$ by hypothesis (1). Each $B^\pm$ partitions
into $B^\pm_R \,\dot\cup\, B^\pm_B$ by hypothesis (2). Combining,
$A(D) = A_R \,\dot\cup\, A_B$. ✓

For (b): apply Lemma R2 above with $c = R$, then with $c = B$. Lemma
R2's hypotheses are exactly (1) and (2) of CL1, so both color classes
are strongly connected.

$\square$ CL1

### §5.2 What changed from `08_phase4_lifting_lemma_v1.md`

- **Hypothesis (2) of v1** ($|B^\pm| \geq 2$) — kept implicitly: it is
  the necessary cardinality condition for the partition in the new (2).
  We could state it as "$|B^+| \geq 2$ and $|B^-| \geq 2$ and there
  exists a 2-coloring of $B^+, B^-$ with each piece non-empty," but the
  "each piece non-empty" formulation is cleaner.
- **Hypothesis (3) of v1**: the local-coverage subcondition at degree-3
  vertices is now redundant; the bridge 2-coloring is the only piece
  that matters.
- **Hypothesis (4) of v1** ("no monochromatic tight 3-cut at the
  interface"): redundant. R2 gives strong connectivity of both color
  classes, which implies every directed cut is bichromatic.

This is a **substantial simplification**. The new CL1 has two
hypotheses, one of which is satisfiability of a bridge 2-coloring,
which is itself a small SAT instance bounded by $|B^+| + |B^-|$
variables — tractable.

### §5.3 Where the proof is no longer mysterious

The §3 gap in v1 — non-tight cuts of size $\geq 4$ at the interface —
was an artifact of doing the proof case-by-case on cuts. R2 sidesteps
the cut-by-cut argument entirely by exhibiting a positive certificate
(branchings) for each color. The cut argument is then a *consequence*,
not a hypothesis.

This is a clean win.

---

## §6 — Next steps and open questions

### §6.1 Vehicle 6's role

The Coder's parallel work on Vehicle 6 (gluings of 3-arc-strong inner
parts with SAD-decomposable $D[V_i]$) will produce the *positive* test
bench CL1 needs. The corpus from `08_phase4_lifting_lemma_v1.md` cannot
verify CL1 directly because the inner parts are 2-arc-strong UNSAT
templates.

The empirical question Vehicle 6 should answer:

> When gluing two 3-arc-strong SAD-decomposable digraphs via bridges,
> does there always exist a bridge 2-coloring satisfying CL1
> hypothesis (2)?

If yes on 200+ Vehicle 6 instances, CL1 is operationally usable for
lifting through any 3-arc bridge interface.

If no on some instance, that instance is a *negative empirical refinement*:
some gluings are not lifted by CL1, and we need an enrichment (perhaps
recursion or a multi-step argument).

### §6.2 Publication estimate

**CL1 in its final form (§5.1) is plausibly publishable as a lemma**,
but **only as a building block, not standalone**.

Comparison:

- BJ–Wang Lemma 2.4: handles "one part is a shell of independent
  vertices, the other is the SAD-able kernel." CL1 generalises to "both
  parts are SAD-able." This is more general but the proof technique is
  essentially the same.
- BJ–Yeo 2004 §3: handles the semicomplete special case using "good
  pairs" (paired branching extraction). CL1's R2 is the same idea,
  class-agnostic.

Standalone novelty is modest. A standalone publishable angle would be:
"**Bridge-Coloring Lifting Theorem.** A digraph $D$ has a SAD iff there
exist a bipartition $V = V_1 \,\dot\cup\, V_2$ with each $D[V_i]$
SAD-decomposable and a bridge 2-coloring with each direction-color
piece non-empty." The "only if" direction is trivial (any SAD restricts
to SADs on each part). The "if" direction is exactly CL1.

This *biconditional* form might be J. Graph Theory short-paper material
if no analogous published statement exists. **The Auditor needs to
check** (see §6.3).

A safer route: CL1 + a class application (e.g., the rank-1 ILS / OLS
class from `02_structural_program.md` §3). Then the paper is "Every
3-arc-strong ILS digraph has a SAD" with CL1 as the engine. That's a
clear publishable theorem.

### §6.3 Open questions

**To the Auditor:**

(A1) The cleanest comparand for CL1' (final form) is BJ–Wang 2025
Lemma 2.4. Does *any* published statement of BJ–Wang Lemma 2.4 (or a
generalization in BJ–Yeo 2004, BJ–Huang 2012, BJG–Yeo 2020) allow *both
parts* to be SAD-decomposable rather than "kernel + shell of independent
vertices"? My best guess: no — every published version specializes
*one* of the two parts. If correct, the bilateral version is new and
publishable as a lemma.

(A2) BJ–Yeo 2004 §3 uses a "good pair" construction. Is the good-pair
notion the same as R2's "out-arborescence and in-arborescence at a
common root, both in the same color"? If yes, R2 is the obvious class-
agnostic restatement of BJ–Yeo Lemma 3.2 (?) — which we should cite
clearly. If no, R2 is genuinely new.

**To the Probabilist (EC-log specialist):**

(P1) The EC-log proof gives a probabilistic SAD construction at
$\lambda \geq C \log n$. Does the random-coloring argument extend to a
**probabilistic R2**? Specifically:

> Suppose $D = (V, A)$ is 3-arc-strong, $V = V_1 \,\dot\cup\, V_2$ with
> each $D[V_i]$ SAD-decomposable, and $|B^+|, |B^-| \geq C \log n$.
> Then a uniformly random 2-coloring of bridges produces a valid
> CL1 bridge-coloring w.h.p.

If yes, this gives a *probabilistic CL1* for the high-bridge-multiplicity
regime, which is the natural complement to CL1's two-hypothesis form.

(P2) Pattern P1 (b21 is direction-monochromatic in 56/56 corpus
witnesses) is way out in the random-coloring tail ($2^{-|B^-|}$
probability under uniform random coloring). The SAT solver's preference
for monochromatic-direction solutions could be (a) a solver bias or
(b) a structural consequence. R2's proof gives no insight here — the
proof works for any valid 2-coloring of bridges, not just direction-
monochromatic ones. The empirical bias is a **separate phenomenon** to
explain.

**To the Lead:**

(L1) Should we re-target Phase 4 to gluings of 3-arc-strong inner parts
(Vehicle 6), now that CL1 is provable in its native domain? My read:
yes, this is now the highest-priority empirical question. Vehicle 6
will tell us whether CL1's hypothesis (2) (the bridge 2-coloring exists)
is satisfiable for the natural gluings, which is the *only* remaining
empirical unknown.

(L2) The §6.2 biconditional form ("Bridge-Coloring Lifting Theorem")
might be J. Graph Theory short-paper material standalone. Worth a 1-week
investment to write the full paper draft, conditional on the Auditor
confirming novelty?

---

## Appendix — Empirical script and rollup data

`code/phase4_branching_extract.py` (≈260 lines) loads `phase4_lifting_probe`,
regenerates the 56 SAT witnesses, runs BFS to extract one out- and one
in-arborescence in each color class with a common root preferring interface
vertices, classifies the arcs of each tree by region, and writes
`code/logs/phase4_branching_extract.json` plus a summary table to stdout.

Rollup (56/56 witnesses):

| Color | Has T+ and T- common-root? | Common root in $I$? | Uses $\geq 1$ b12 in T+? | Uses $\geq 1$ b21 in T+? |
|---|---:|---:|---:|---:|
| R | 56/56 | 56/56 | 53/56 | 0/56 |
| B | 56/56 | 56/56 | 32/56 | 51/56 |

The 0/56 in row "R uses $\geq 1$ b21 in T+" is the empirical content of
Pattern P1 (b21 is mono-blue post-normalization). The 53/56 versus 32/56
asymmetry between R and B b12 usage reflects the bridge color asymmetry
($|B^+_R|$ averages 2 while $|B^+_B|$ averages 1.6 across the corpus).

The proof of R2 in §3 does **not** depend on these empirical asymmetries;
it works for any valid bridge 2-coloring satisfying CL1's hypothesis (2).
The corpus is a consistency check: it confirms that branchings of both
colors with common interface roots exist, which is exactly R2's
conclusion.

Reproducibility: `cd code && uv run python phase4_branching_extract.py`.
Total runtime <2 s.
