# Phase 6 — bespoke discharging attempt at $k = 12$, $K_9$-free

Working file. The audit phase
([`upper_bound_notes.md`](upper_bound_notes.md)) closed the literature
routes: Brooks-type 2018 + GP Lemma 3.3 disposes of $n \le 88$;
KS+Johansson and GP 2022 are 30–9000× off in constants and don't apply
at $k = 12$ anyway. This document attempts a bespoke argument for
$n \ge 89$ using only the local structure of low-degree vertices.

## Setup

> **Working hypothesis (to refute).** $G$ is 12-critical, $K_9$-free,
> biplanar, on $n \ge 89$ vertices with $|E(G)| \le 6n - 12$.

We aim to derive a contradiction.

## Notation

- $\delta(G) = 11$ (12-critical $\Rightarrow$ $\delta \ge k-1 = 11$; we'll
  show below that the upper biplanar-edge bound forces equality on many
  vertices).
- $L := \{v \in V(G) : d_G(v) = 11\}$, the **low** vertices.
- $H := V(G) \setminus L = \{v : d_G(v) \ge 12\}$, the **high** vertices.
- $\ell := |L|$, $h := |H|$, $n = \ell + h$.
- $e_{LL}, e_{LH}, e_{HH}$: edges with both, one, no endpoints in $L$.
- $m = e_{LL} + e_{LH} + e_{HH}$.

## Step 1 — many low vertices

Sum of degrees:

$$2m = \sum_v d(v) = 11 \ell + \sum_{v \in H} d(v) \ge 11 \ell + 12 h
     = 11 n + h.$$

Combined with the biplanar bound $2m \le 12 n - 24$:

$$11 n + h \le 12 n - 24
  \quad\Longrightarrow\quad h \le n - 24
  \quad\Longrightarrow\quad \ell \ge 24.$$

Combined with Brooks-type $2m \ge 2 \lceil (65n - 43)/11 \rceil \ge (130 n - 86)/11$:

$$11 n + h \ge (130 n - 86)/11
  \quad\Longrightarrow\quad h \ge (130 n - 86)/11 - 11 n = (9 n - 86)/11.$$

So at $n = 89$: $h \ge (801 - 86)/11 = 715/11 = 65$, and $\ell \le n - 65 = 24$.
Combined with $\ell \ge 24$ above, $\ell = 24$ and $h = 65$ at $n = 89$
*if both bounds are tight*. (Both being simultaneously tight requires
every $H$ vertex to have degree exactly 12 and $|E(G)| = 6n - 12 = 522$
exactly; Brooks-type also wants $|E(G)| = \lceil(65 n - 43)/11\rceil = 522$,
so this is internally consistent.)

The interesting structural regime for the contradiction is therefore
$\ell = 24$ at $n = 89$, $\ell$ growing roughly linearly with $n$ above
that ($\ell \ge 24$, $\ell \le n - (9n-86)/11 = (2n + 86)/11$).

## Step 2 — Gallai forest structure on $L$

**Gallai's theorem.** In any $k$-critical graph, the subgraph induced
by the vertices of degree exactly $k-1$ is a *Gallai forest*: every
block is either a complete graph $K_t$ or an odd cycle.

At $k = 12$: blocks of $G[L]$ are $K_t$ ($t \ge 2$) or $C_{2r+1}$
($r \ge 1$, so block size $\ge 3$).

**Local clique cap from low-degree.** A vertex of $L$ has degree 11
*in $G$*, so it has degree at most 11 within $G[L]$. A $K_t$ block
containing $v$ contributes $t - 1$ to $\deg_{G[L]}(v)$. So $t - 1 \le 11$,
i.e. $t \le 12$. Reaching $t = 12$ would mean $v$ has all 11 neighbours
in this block, leaving no high-vertex neighbours.

**$K_9$-freeness.** A $K_t$ block in $G[L]$ is itself a $K_t$ subgraph
of $G$ (clique inheritance is automatic). So $t \le 8$.

Hence:

> **Lemma 2.1.** Every block of $G[L]$ is either $C_{2r+1}$ for some
> $r \ge 1$, or $K_t$ for some $2 \le t \le 8$.

This is a much tighter Gallai structure than at general $k$.

## Step 3 — Block-type accounting

Let $B$ be the multiset of blocks of $G[L]$. Each block $b \in B$
has size $|V(b)| = t_b$ and edge count

$$e(b) = \begin{cases} \binom{t_b}{2} & b \cong K_{t_b}, \ 2 \le t_b \le 8 \\
                       t_b & b \cong C_{t_b}, \ t_b \in \{3, 5, 7, \dots\}
        \end{cases}$$

Counting with cut-vertex multiplicities:

$$\ell = \sum_b t_b - (\text{cut-vertex repetitions}),
  \qquad e_{LL} = \sum_b e(b).$$

For a Gallai forest (block-cut tree is a forest), if $G[L]$ is
connected (one tree), the number of blocks is exactly $\ell - 1$
"absorbed" through cut vertices — more precisely, $\sum_b (t_b - 1)$
counts each non-cut vertex once and each cut vertex once per block it
sits in, with the block-cut tree having $|B| + (\text{cut vertices})$
nodes and $|B| - 1$ edges (if connected). We'll bound this combinatorially
below rather than tracking exactly.

**Edges from L to H.** Each $v \in L$ has $d_{G[L]}(v)$ neighbours in
$L$ and $11 - d_{G[L]}(v)$ in $H$. Summing,

$$e_{LH} = 11 \ell - 2 e_{LL}.$$

**Edge constraint from biplanarity.** $m = e_{LL} + e_{LH} + e_{HH} \le 6n - 12$.

Substituting,

$$11 \ell - e_{LL} + e_{HH} \le 6 n - 12,$$

i.e.

$$e_{HH} \le 6n - 12 - 11 \ell + e_{LL}.$$

So denser $G[L]$ (more $e_{LL}$) leaves more room for $e_{HH}$.

## Step 4 — Discharging plan

The classical KY potential is $\rho_k(G) = (k-2)(k+1)|V(G)| - 2(k-1)|E(G)|$;
at $k = 12$, $\rho_{12} = 130 n - 22 m$.

For our hypothetical $G$ at $n = 89$, $m = 522$:

$$\rho_{12} = 130 \cdot 89 - 22 \cdot 522 = 11570 - 11484 = 86.$$

KY's general theorem says $\rho_{12}(G) \le 12(12-3) = 108$ for any
12-critical $G$. So $\rho_{12} = 86$ is *consistent* with KY (just shy
of the cap). Brooks-type tightens the cap: for non-12-Ore,
$\rho_{12}(G) \le y_{12} = 86$. So our hypothetical $G$ sits *exactly*
at the Brooks-type bound. **Equality in Brooks-type at $n = 89$.**

**Plan.** Pick discharging weights $w(v)$ tailored to $K_9$-freeness.
Standard KY potential gives initial charge $\rho_{12}$ per vertex via
$13 \cdot 10 = 130$. The trick is to discharge between $L$ and $H$ in
a way that exploits Lemma 2.1's block-type cap ($t \le 8$) to extract
one extra edge of potential at $n \ge 89$.

Specifically: in the standard discharging (cf. KY 2014 §4, Brooks-type
§5), low vertices in large $K_{k-1}$-clusters absorb extra charge from
their high neighbours via Rule R2. With $K_9$-free, the cluster sizes
$t \le 8$ are *strictly smaller* than the $t = k - 1 = 11$ that the
generic argument allows. The discharging accounting should then
"return" excess charge that closes the $+1$-edge gap.

Concrete target: replicate the KY/Brooks-type discharging structure
with the block-size bound $t \le 8$ from Lemma 2.1, and check that the
edge-deficit accumulated by tightened clusters exceeds the existing
Brooks-type bound by at least $\lfloor (n - 67)/11 \rfloor - 1$ edges
for $n \ge 89$.

## Step 5 — Why a crude block-frequency LP is too weak

The crude LP — block frequencies, biplanar edge bound, Brooks-type,
Gallai-forest constraint — is **already feasible at $n = 89$ via the
degenerate profile**

$$\ell = 24,\ h = 65,\ m = 522,\ e_{LL} = 0,\ e_{LH} = 264,\ e_{HH} = 258,$$

i.e. $G[L]$ is *edgeless* (24 isolated low vertices, no $G[L]$ edges
at all). Every constraint we have so far is satisfied:

- Every low vertex has degree 11 entirely into $H$. ✓
- Average degree on $H$ is $(11 \cdot 24 - 0 + 2 \cdot 258)/65
  = (264 + 516)/65 = 12$ exactly, consistent with $H$ vertices having
  $d \ge 12$. ✓
- $m = 6n - 12 = 522$. ✓ (Biplanar bound tight.)
- $e_{HH} = 258 \le 6 h - 12 = 378$. ✓ (Biplanar bound on $G[H]$.)
- Gallai forest condition on $G[L]$: an edgeless graph is trivially
  a forest with every component a 1-vertex block. ✓
- Brooks-type: $522 = \lceil (65 \cdot 89 - 43)/11 \rceil$. ✓ Tight.

So **the crude LP cannot rule out a biplanar 12-critical $K_9$-free
graph at $n = 89$**. The missing ingredient is *criticality*: the LP
as drafted only encodes biplanarity (edges) and degree-distribution
(Gallai forest exists), not the fact that *every* vertex deletion is
$(\chi - 1)$-colourable.

## Step 6 — Endblock list-colouring constraints (the missing ingredient)

For 12-criticality to bite locally on $G[L]$, look at endblocks
of the block-cut tree.

**Setup.** Let $B$ be an endblock of $G[L]$ — a block adjacent to at
most one cut vertex (or a singleton if $G[L]$ is disconnected /
has isolated vertices). By Lemma 2.1, $B$ is either:

- $K_t$ for $2 \le t \le 8$;
- $C_{2r+1}$ for $r \ge 1$;
- a single isolated vertex (the $t = 1$ degenerate case).

**Criticality at $B$.** $G$ is 12-critical, so $G - B$ (delete the
non-cut vertices of $B$) is 11-colourable. Fix any proper 11-colouring
$\varphi$ of $G - B$. For each $v \in B$ that's a *non-cut* vertex of
$G[L]$, the set of colours used on $v$'s neighbours in $G - B$ is

$$\text{Used}(v) := \{\varphi(u) : u \in N_G(v) \setminus B\}.$$

Let $L(v) := \{1, \dots, 11\} \setminus \text{Used}(v)$, the
list of *available* colours at $v$. Since $G$ is *not* 11-colourable
(it's 12-critical), every 11-colouring of $G - B$ must fail to extend
to $B$: i.e. the subgraph $B$ is **not** $L$-colourable for every list
assignment $L$ arising this way.

**List sizes.** Each $v \in B$ has total degree 11, of which $d_B(v)$
are inside $B$ and $11 - d_B(v)$ go to $V(G) \setminus B$ (which lives
in $G - B$). So $|\text{Used}(v)| \le 11 - d_B(v)$, hence

$$|L(v)| \ge 11 - (11 - d_B(v)) = d_B(v).$$

For $B = K_t$: every non-cut $v$ has $d_B(v) = t - 1$, so $|L(v)| \ge t - 1$.
$B$ not $L$-colourable means $K_t$ is not $L$-colourable for some
$L$ with $|L(v)| \ge t - 1$ for all $v$. But $K_t$ is $(t-1)$-choosable
*only when* $t \le 2$ (trivially, and the standard list-chromatic-of-$K_t$
fact). For $t \ge 3$, $K_t$ requires lists of size $t$. So in fact
$K_t$ as endblock of $G[L]$ has $t = 1$ or $t = 2$ only?

Wait — that can't be right; KY's discharging works with larger
clusters. Let me re-examine. $|L(v)| \ge d_B(v)$ is a *lower* bound;
the actual list could be larger. $K_t$ is $L$-colourable when *all*
$|L(v)| \ge t$. So non-$L$-colourability requires at least one $v$
with $|L(v)| \le t - 1$, i.e. with $|\text{Used}(v)| \ge 11 - (t - 1)
= 12 - t$.

For a *non-cut* $v \in K_t$ endblock: $v$ has $11 - (t - 1) = 12 - t$
external neighbours (in $V(G) \setminus B$). All of them must contribute
*distinct* colours that exhaust $\{1, \dots, 11\} \setminus L(v)$, i.e.
$|\text{Used}(v)| = 12 - t$ (no waste from coincident colours).

This is a strong rigidity condition: every endblock $K_t$ has at least
one vertex whose external neighbours are *rainbow-coloured* under
$\varphi$ — and this must hold across *every* 11-colouring of $G - B$.

For $t \le 8$ (the $K_9$-free cap), $v$ has $12 - t \ge 4$ external
neighbours, all of which must take distinct colours. This is highly
non-vacuous and is what we should encode in the LP.

**Refined endblock constraint.** For each $K_t$ endblock $B$ with
$t \le 8$, the $12 - t$ external neighbours of some non-cut $v \in B$
must form a rainbow-coloured set in every 11-colouring of $G - B$.
Equivalently, there is no $(t-1)$-uniform colour collision on those
neighbours.

**For isolated low vertices ($t = 1$):** an isolated $v \in L$ has all
11 neighbours in $H$. Criticality says $G - v$ is 11-colourable; the
11 neighbours in $H$ must take all 11 colours, i.e. they are
*rainbow-coloured* in every 11-colouring of $G - v$. This is the
strongest case — every isolated low vertex pins a full rainbow on its
neighbourhood, *in every* 11-colouring of the rest.

The all-isolated profile in Step 5 has 24 such rainbow constraints —
each on a distinct 11-set of $H$-neighbours — and these must mutually
agree under *some* (in fact every) 11-colouring of $G[H]$. That is a
combinatorial obstruction we can plausibly use.

## Step 6½ — First lemma attempt: isolated low vertex forces $n \ge 91$

**Lemma (attempted).** Let $G$ be a 12-critical $K_9$-free biplanar
graph with $|E(G)| \le 6n - 12$. If $G[L]$ has an isolated vertex, then
$n \ge 91$.

**Proof (modulo one open sub-step).**

*Setup.* Let $v \in L$ with $d_{G[L]}(v) = 0$. Then $N(v) \subseteq H$
and $|N(v)| = 11$.

*Step 1: rainbow.* $G - v$ is 11-colourable. No 11-colouring of $G - v$
extends to $v$, so in every proper 11-colouring $\varphi$ of $G - v$,
$\{\varphi(u) : u \in N(v)\} = \{1, \dots, 11\}$. $N(v)$ is
rainbow-coloured in every 11-colouring of $G - v$.

*Step 2: at least 6 non-edges in $N(v)$.* $K_9$-freeness with $v$
adjacent to all of $N(v)$ forces $\omega(G[N(v)]) \le 7$, so $G[N(v)]$
is $K_8$-free. Biplanarity of $G[\{v\} \cup N(v)]$ (a 12-vertex
subgraph) gives $|E(G[\{v\} \cup N(v)])| \le 6 \cdot 12 - 12 = 60$,
hence $|E(G[N(v)])| \le 49$. The number of non-edges in $N(v)$ is
$\binom{11}{2} - 49 = 6$.

*Step 3: contract a non-edge.* Pick any non-edge $\{u_i, u_j\}$ in
$N(v)$. Let $G^* := (G - v) / \{u_i, u_j\}$ be the graph obtained by
identifying $u_i$ with $u_j$ (and replacing parallel edges with a
single edge). Then $|V(G^*)| = n - 2$. By the rainbow condition, no
11-colouring of $G - v$ assigns $u_i$ and $u_j$ the same colour, so
$G^*$ is *not* 11-colourable: $\chi(G^*) \ge 12$. Therefore $G^*$
contains a 12-critical subgraph $H$.

*Step 4 (preserving $K_9$-freeness under contraction).* Suppose we
can choose the non-edge $\{u_i, u_j\}$ in Step 3 so that $G^*$ is
$K_9$-free. Concretely: a $K_9$ in $G^*$ must involve the merged
vertex (else it is a $K_9$ in $G - v \subseteq G$, contradicting
$K_9$-free) and corresponds to a set of 8 pairwise-adjacent vertices in
$N_{G-v}(u_i) \cup N_{G-v}(u_j)$, with at least one in
$N(u_i) \setminus N(u_j)$ and at least one in $N(u_j) \setminus N(u_i)$
(else the $K_8$ together with $u_i$ or $u_j$ alone already gives $K_9$
in $G$). Call such a $K_8$ a *split obstruction* for the non-edge.

*Step 5 (was: invoke Theorem B). **Gap identified.*** Theorem B's
$n \ge 89$ lower bound is for 12-critical $K_9$-free **biplanar**
graphs. Contraction destroys planarity in general: identifying two
non-adjacent vertices in a planar graph can produce $K_5$ or $K_{3,3}$.
So $G^*$ is not automatically biplanar even when $G$ is, and Theorem B
does not directly apply to a 12-critical subgraph $H \subseteq G^*$.

*Step 5' (case split that repairs the argument for one half).* Let $H$
be a 12-critical subgraph of $G^*$ (exists since $\chi(G^*) \ge 12$
by Step 3). Let $w$ be the merged vertex.

- **Case A: $w \notin V(H)$.** Then $V(H) \subseteq V(G^*) \setminus \{w\}
  = V(G) \setminus \{v, u_i, u_j\}$, and every edge of $H$ is an edge of
  $G$ (the contraction only modifies edges incident to $w$). So
  $H \subseteq G$ is a subgraph of a biplanar graph, hence biplanar.
  Combining $K_9$-freeness (granted by Step 4) and biplanarity, Theorem
  B gives $|V(H)| \ge 89$. But $|V(H)| \le n^* - 1 = n - 3$. So
  $n \ge 92$.

- **Case B: $w \in V(H)$.** $H$ contains the merged vertex, whose
  "un-contraction" returns a structure in $G - v$. $H$ is 12-critical
  but may not be biplanar (the merge can destroy planarity precisely
  through $w$'s edges). Theorem B does not apply directly. **This is
  the genuine remaining open case.**

So the conditional conclusion, modulo Step 4, is

> If $G[L]$ has an isolated vertex, then **either** $n \ge 92$
> (Case A), **or** some 12-critical subgraph of $G^*$ contains the
> merged vertex (Case B).

That is still not the lemma we want. To close Case B we need one of
the three repairs the user suggested:

**Case B repair option 1 — biplanarity-preserving contraction.** Pick
$\{u_i, u_j\}$ so that the contraction of the non-edge stays biplanar.
Layer-dependent; probably hard.

**Case B repair option 2 — edge-cap on critical subgraph.** Show that
every 12-critical subgraph $H \subseteq G^*$ has $|E(H)| \le 6|V(H)| - 12$
even though $G^*$ itself is not biplanar — i.e., the biplanar edge
budget survives the contraction within any critical core. Possible if
the merged vertex $w$ has few "fresh" edges.

**Case B repair option 3 — direct potential argument on $G^*$.** Per
the review note:

$$\rho_{12}(G^*) = 130 (n - 2) - 22 (m - 11 - q) = 68 + 22 q
\quad\text{at } n = 89, m = 522,$$

where $q = |N_{G-v}(u_i) \cap N_{G-v}(u_j)|$ (common neighbours
collapsed by the contraction). For a 12-critical non-Ore subgraph
$H \subseteq G^*$, $\rho_{12, G^*}(V(H)) \le y_{12} = 86$ (Brooks-type
+ GP Lemma 3.3, since $K_9$-free implies non-Ore — *granted that
Step 4 ensures $H$ stays $K_9$-free*).

This gives a Brooks-type budget constraint: $|E(H)| \ge \lceil (65 |V(H)| - 43)/11 \rceil$.
For $H = G^*$ itself ($|V(H)| = 87$): Brooks demands $|E(H)| \ge 511$
edges, but $|E(G^*)| = 511 - q$. So **if $q \ge 1$, $G^*$ itself
cannot be 12-critical $K_9$-free** — $H$ must be a *proper*
subgraph.

For a proper subgraph $H \subsetneq G^*$ in Case B (containing $w$),
$|V(H)| \le 86$ and $|E(H)| \le |E(G^*)| - $ (edges lost to dropping
$\ge 1$ vertex) $\le 511 - q - $ something. The required Brooks bound
shrinks with $|V(H)|$ at rate $65/11 \approx 5.91$ per vertex, while
the edge-loss rate from $G^*$ depends on vertex degrees. The exact
arithmetic determines whether any $n_H$ admits feasible $H$.

### Step 5'' — Sharpened conditional conclusion

Assuming Step 4 (no $K_9$ created), the lemma now reduces to:

> Either Case A holds, giving $n \ge 92$, **or** Case B holds with
> $q \ge 1$ and there is a 12-critical $K_9$-free graph $H$ on
> $|V(H)| \le 86$ vertices, containing the merged vertex $w$, with
> $|E(H)| \le 511 - q - \Delta$ for $\Delta$ counting edge loss from
> $V(G^*) \setminus V(H)$. Brooks-type then bounds $|V(H)|$ from below.

The cleanest path forward is Repair Option 3 (Brooks-type budget),
because it sidesteps biplanarity of $H$ entirely. The remaining
arithmetic is whether the Brooks edge demand at each $n_H \le 86$
can be met by the $G^*$ edge budget *given that $H$ contains $w$*.

### Step 5''' — Tight calculation, $q = 0$ case

If $q = 0$ (no common neighbours): $\rho_{12}(G^*) = 68 \le 86 = y_{12}$,
so $G^*$ as a whole already sits below the Brooks-type threshold. But
$G^*$ has $\chi(G^*) \ge 12$, and there's no immediate KY-type
contradiction since $\rho_{12} \le k(k-3) = 108$ is consistent with
12-criticality.

So $q = 0$ does *not* yield a free contradiction via Brooks-type, and
Case A's $n \ge 92$ does not extend to $q = 0$. The natural sub-case
is $q = 0$ with Case B (i.e., $w \in V(H)$, no common neighbours
between $u_i$ and $u_j$). Here the contracted graph is essentially
a "disjoint" merge, and biplanarity might in fact survive — we may
get a cleaner repair via Option 1 specifically when $q = 0$.

### Step 5'''' — Case B arithmetic worked through

Let $\alpha := |N(v) \cap N(u_i) \cap N(u_j)|$ be the number of
degree-10 vertices in $G^*$ (these have $\deg_{G^*} = 10$ and are
forced into $S$). Let $\beta, \gamma$ be the number of degree-11 and
degree-12 vertices in $S$ respectively. So $\alpha + \beta + \gamma = r$.

Edge balance + biplanarity of $G[S]$ (which holds because $S$ contains
only original $G$-vertices, $w \notin S$):

$$|E(H)| = (511 - q) - 11r + \alpha - \gamma + e(S),
  \quad e(S) \le 6r - 12 \ (r \ge 3).$$

Brooks-type lower bound (using $K_9$-free $\Rightarrow$ non-Ore via
GP Lemma 3.3): $|E(H)| \ge \lceil(65(87 - r) - 43)/11\rceil =
\lceil(5612 - 65r)/11\rceil$.

Vertex availability for degree-11 in $S$: $\beta \le 9 + q - 2\alpha$
(the 9 vertices in $N(v) \setminus \{u_i, u_j\}$ minus the $\alpha$
forced into degree-10, plus the $q - \alpha$ outside vertices in
$N(u_i) \cap N(u_j)$ that became degree-11).

**Brute-force feasibility check.** A sweep over all
$(r, q, \alpha, \gamma)$ with $r \in [0, 30]$, $q \in [0, 11]$,
$\alpha \in [0, \min(q, 9)]$, $\gamma \ge 0$, finds **exactly one
feasible configuration**:

$$(r, q, \alpha, \gamma) = (0, 0, 0, 0).$$

Everything else fails either the Brooks-type budget or the $\beta$
availability bound. In algebraic form, the joint constraints at
$r = 13 + k$ ($k \ge 0$) give

$$\underbrace{\alpha + k + 4 - q}_{\text{β availability}} \le \gamma \le
  \underbrace{\alpha - q + k}_{\text{Brooks budget}},$$

forcing $4 \le 0$. For $r \le 12$, the Brooks bound is even stricter.
For $r \in \{0, 1, 2\}$, the simpler $e(S) \le \binom{r}{2}$ bound
still forces $q = 0, r = 0$.

**Consequence.** The single feasible configuration $(r, q) = (0, 0)$
corresponds to $H = G^*$ itself being a 12-critical $K_9$-free graph
on 87 vertices with exactly $|E(G^*)| = 511$ edges (Brooks-tight). For
any non-edge $\{u_i, u_j\}$ in $N(v)$ with $q \ge 1$, Case B is
**unconditionally infeasible**.

### Step 6 — induced-$P_3$ corollary (no more Case B for non-disjoint-clique $N(v)$)

Combining Step 5'''' with Case A (which closes immediately to
$n \ge 92$): if there exists a non-edge $\{u_i, u_j\}$ in $N(v)$ with
$q \ge 1$, the lemma closes (assuming Step 4 $K_9$-free preservation
also holds at that non-edge).

The contrapositive: if the lemma fails (i.e. $G[L]$ has an isolated
vertex $v$ with the $n = 89$ tight hypotheses), then **every** non-edge
$\{u_i, u_j\}$ in $N(v)$ has $q = 0$ — no common neighbour in $G - v$.

Now: $q$ counts common neighbours in $G - v$, which includes both
$N(v) \setminus \{u_i, u_j\}$ and $V(G) \setminus N(v) \setminus \{v\}$.
If any third vertex $u_k \in N(v) \setminus \{u_i, u_j\}$ is adjacent
to both $u_i$ and $u_j$ in $G$, then $u_k$ is a common neighbour and
$q \ge 1$. Equivalently, the path $u_i - u_k - u_j$ in $G[N(v)]$ with
$u_i u_j$ a non-edge is an *induced $P_3$* on $\{u_i, u_k, u_j\}$.

So $q = 0$ on every non-edge forces $G[N(v)]$ to have **no induced
$P_3$**, i.e. $G[N(v)]$ is a disjoint union of cliques. Combined with
$K_9$-freeness ($\omega(G[N(v)]) \le 7$), each clique has size $\le 7$.

> **Partial Lemma (proved modulo Step 4).** Under the $n=89$ extremal
> hypotheses, if $v$ is isolated in $G[L]$, then $G[N(v)]$ is a
> disjoint union of cliques each of size at most 7. In particular,
> the 11-vertex set $N(v)$ admits only the partitions
> $\{7,4\}, \{7,3,1\}, \{7,2,2\}, \dots, \{1,1,1,\dots,1\}$.

This is the right shape: dramatically more rigid than "no isolated
low vertex." The remaining work has two parts:

1. **Step 4 (still open).** Some non-edge in $N(v)$ must contract
   $K_9$-free-preservingly. The partial lemma forces $G[N(v)]$ disjoint
   cliques, so most non-edges in $N(v)$ are *cross-clique*. Need to
   show at least one cross-clique non-edge contracts without creating
   a split $K_8$ obstruction.
2. **Subcase Q0 closure.** Rule out the residual scenario where
   $G[N(v)]$ is a disjoint union of cliques **and** for every cross-clique
   non-edge, the contracted $G^* = (G-v)/\{u_i, u_j\}$ is itself a
   12-critical $K_9$-free graph on 87 vertices with exactly 511 edges.

### Step 7 — Revised plan

**Consequence (conditional).** If Step 4 is provable, then a
biplanar 12-critical $K_9$-free graph at $n \in \{89, 90\}$ has no
isolated low vertex. Combined with the analogous (still-to-prove)
absorption of the next-smallest endblock types ($K_2$, $C_3$, …), this
pushes the lower bound past 90 by similar 2-vertex contractions.

**Why this is the right shape, even if Step 4 isn't closed yet.**

- It uses *every* hypothesis: criticality (rainbow), $K_9$-free (via
  $\omega(G[N(v)]) \le 7$ and contraction preservation), biplanarity
  (via $|E(G[\{v\} \cup N(v)])| \le 60$).
- It targets the degenerate isolated-low-vertex profile that defeats
  the crude LP (Step 5 above). Every isolated $v$ would have to admit
  an obstructed non-edge — a much more constrained condition than
  block-frequency feasibility.
- The argument generalises: replace "isolated $v$" by "$v$ in a small
  endblock" by combining several rainbow conditions on the endblock's
  external neighbours.

**Step 4 attack plan.**

The split-obstruction condition requires a $K_8$ in
$N_{G-v}(u_i) \cup N_{G-v}(u_j)$ with vertices on both sides. Bound
the number of $K_8$ subgraphs in biplanar $K_9$-free graphs at
$n = 89$, $m = 522$. Each $K_8$ has $\binom{8}{2} = 28$ edges; in
biplanarity, neither planar layer can host a $K_5$ (non-planar), so
each $K_8$'s 28 edges split between layers with neither side holding
$K_5$. By Turán the layer-$K_5$-free max is $\text{ex}(8, K_5) =
|E(T(8,4))| = 24$. So each $K_8$ has between $4$ and $24$ edges per
layer (summing to 28). This gives a structural constraint per $K_8$;
combined with the global edge bound and degree sequence, the total
number of $K_8$'s in $G$ at $n = 89$ is bounded — concrete bound
deferred.

## Step 7 — Revised plan

1. **Fix the exact block accounting** (cut-vertex-free formulation).
   For $F = G[L]$ let
   - $z$ = number of isolated vertices of $F$;
   - $c$ = number of nontrivial connected components of $F$;
   - $b_t$ = number of $K_t$-blocks, $2 \le t \le 8$;
   - $c_s$ = number of $C_s$-blocks for each odd $s \ge 3$.
   Then
   $$\ell = z + c + \sum_{\text{nontrivial blocks } B}(|B| - 1),$$
   $$e_{LL} = \sum_{t=2}^8 \binom{t}{2} b_t + \sum_{s \text{ odd}} s \cdot c_s.$$
   $e_{LH}$ and $e_{HH}$ as in Step 3.

2. **Derive the first endblock list-colouring lemma.** Concrete first
   target: prove that an *isolated* low vertex $v$ forces its 11
   $H$-neighbours to be pairwise non-adjacent in $G$ (or some weaker
   structural condition forced by every 11-colouring placing distinct
   colours on them). This is the leanest non-trivial criticality
   constraint.

3. **Encode the lemma in an LP/ILP** alongside the block-frequency
   variables. Recheck feasibility. The isolated-low-vertex profile
   from Step 5 should *no longer* be feasible after the lemma is
   encoded.

4. **If still feasible:** identify what additional bad-list constraint
   the LP solution violates, prove that, iterate.

5. **Sanity-check empirically:** for $n = 89$, the LP without
   criticality should be feasible (per Step 5). After adding the
   isolated-vertex lemma it should be infeasible or give a different
   extremal profile (e.g. forcing $G[L]$ to have many short cycles or
   small cliques rather than isolated vertices). Either outcome moves
   Phase 6 forward concretely.

The crude LP run is still worth doing once *as a check on the
formulation*, with the explicit prediction that it returns the
isolated-low-vertex profile. That confirms the plumbing works before
we add the structural lemma.

## Step 6 — Anticipated obstacles

1. **The biplanar bound is global, the Gallai structure is local.**
   Local structural improvements via Gallai-forest accounting may not
   propagate to a global edge count without a careful averaging.
2. **Cut-vertex multiplicities are awkward.** The block-cut tree structure
   means a single low vertex can sit in multiple blocks; counting edges
   without double-counting needs care.
3. **The biplanar edge bound $6n - 12$ does not interact with criticality
   beyond the global level.** A finer biplanarity input would be: for any
   $W \subseteq V(G)$, $|E(G[W])| \le 6|W| - 12$ — using the *induced*
   biplanar bound on subsets. This is the right hook for a local-to-global
   reduction.

## Status

Drafted; not yet executed. Next concrete tasks:

1. Work out the cut-vertex accounting cleanly so $\sum t \cdot n_t$ matches
   $\ell$ exactly (up to a tracked slack).
2. Set up the LP and solve numerically at $n = 89, 100, 150$ to see
   whether feasibility actually fails.
3. If LP feasible: identify the extremal block-type profile and look
   for a local-structure lemma forbidding it.
4. If LP infeasible at small $n$ but feasible asymptotically: characterise
   the threshold $n^*$ above which the LP is feasible — that's a partial
   result on its own (closes a wider interval beyond Brooks-type's $n \le 88$).
