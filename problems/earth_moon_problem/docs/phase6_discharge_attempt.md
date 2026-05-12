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

### Step 4+ — strengthened K_9-preservation requirement

The original Step 4 was: *some* non-edge in $N(v)$ contracts without
creating $K_9$. For the induced-$P_3$ corollary below to fire, we
actually need:

> **Step 4+.** If $N(v)$ contains a non-edge with $q \ge 1$, then *at
> least one such $q \ge 1$ non-edge* admits no split-$K_8$ obstruction
> (i.e. contracts to a $K_9$-free $G^*$).

A bare Step 4 doesn't suffice — the $K_9$-free-preserving non-edge it
guarantees might happen to have $q = 0$, leaving the $q \ge 1$ non-edges
out of reach.

### Step 6 — induced-$P_3$ corollary (no more Case B for non-disjoint-clique $N(v)$)

Combining Step 5'''' with Case A (which closes immediately to
$n \ge 92$): if there exists a non-edge $\{u_i, u_j\}$ in $N(v)$ with
$q \ge 1$ **and Step 4+ holds**, the lemma closes.

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

### Step 6½ — Q0 attack via Gallai structure of $G^*$

In Subcase Q0, the contracted $G^*$ is itself a 12-critical $K_9$-free
graph on 87 vertices with exactly 511 edges. Its degree sequence at
$q = 0$ is:

$$|V(G^*)| = 87, \quad |E(G^*)| = 511,$$

with degree distribution

| vertex class | count | degree |
|---|---:|---:|
| $w$ (merged from $u_i, u_j$) | 1 | 22 |
| $L - \{v\}$ (low vertices of $G$ apart from $v$) | 23 | 11 |
| $N(v) - \{u_i, u_j\}$ (high vertices of $G$ in $N(v)$, lost edge to $v$) | 9 | 11 |
| $H \setminus N(v)$ (high vertices of $G$ outside $N(v)$) | 54 | 12 |

Verification: $1 \cdot 22 + 32 \cdot 11 + 54 \cdot 12 = 22 + 352 + 648 = 1022 = 2 \cdot 511$. ✓

Define

$$L^* := (L - \{v\}) \cup (N(v) - \{u_i, u_j\}),
  \qquad |L^*| = 32.$$

These are exactly the degree-11 vertices of $G^*$. By Gallai's theorem
applied to $G^*$ (which is 12-critical by Q0), $G^*[L^*]$ is a Gallai
forest: every block is $K_t$ or odd $C_s$.

**Inherited clique structure on $N(v) - \{u_i, u_j\}$.** By the
disjoint-cliques structure on $N(v)$ (from Step 6), the induced
subgraph $G^*[N(v) - \{u_i, u_j\}]$ is itself a disjoint union of
cliques — the original $G[N(v)]$ partition minus the two merged
vertices. The 9 vertices in $N(v) - \{u_i, u_j\}$ thus form a clique
configuration $(t_1', t_2', \dots)$ with $\sum t_i' = 9$ and each
$t_i' \le 7$.

For example, if $G[N(v)]$ had partition $(7, 4)$ and the cross-clique
non-edge merges one vertex from each, the remainder is $K_6 + K_3$ in
$G^*[N(v) - \{u_i, u_j\}]$.

**Attachment of $L_0 \in L - \{v\}$ to a clique chunk $K_t$.** Consider
a single $L_0 \in L - \{v\}$ and a clique chunk $K_t$ (with $t \ge 2$)
in $G^*[N(v) - \{u_i, u_j\}]$. Let $d_t(L_0) := |N_{G^*}(L_0) \cap V(K_t)|$.

Since $K_t$ is 2-connected (for $t \ge 3$), if $d_t(L_0) \ge 2$ then
$L_0$ lies in the same block of $G^*[L^*]$ as $K_t$ — there are two
vertex-disjoint paths from $L_0$ into $K_t$ (the direct edges). For
this block to be $K_s$ or odd $C_s$:

- The block can be a clique iff $L_0$ is adjacent to *all* of $K_t$,
  making $K_t \cup \{L_0\} = K_{t+1}$. By $K_9$-freeness of $G$,
  $t + 1 \le 8$, so $t \le 7$ (already known).
- The block cannot be an odd cycle: $K_t$ has too many edges for
  $t \ge 3$, and a cycle on $t + 1 \ge 4$ vertices has $t + 1$ edges
  whereas $K_t \cup \{L_0\}$ has $\binom{t}{2} + d_t(L_0) > t + 1$ for
  $t \ge 3$, $d_t(L_0) \ge 2$.

So **$d_t(L_0) \in \{0, 1, t\}$ for each chunk $K_t$ with $t \ge 3$**
(and trivially $\in \{0, 1, 2\}$ for $t = 2$). This is the "rigidity"
the user flagged.

Moreover, if $d_t(L_0) = t$ (the all-of-$K_t$ case), the block becomes
$K_{t+1}$. Additional $L_0' \in L - \{v\}$ with $d_t(L_0') = t$ must be
adjacent to $L_0$ (else the block is not a clique), and the resulting
block is $K_{t + r_t}$ where $r_t$ is the number of such $L_0$'s.
$K_9$-freeness forces $t + r_t \le 8$, so $r_t \le 8 - t$.

**Consequence for chunk edges.** Edges from $L - \{v\}$ to a clique
chunk $K_t$ split as

$$e(L - \{v\}, K_t) = (\text{degree-1 attachments}) \cdot 1 + r_t \cdot t,$$

with $r_t \le 8 - t$.

For each chunk's vertices: each $x \in K_t$ has $\deg_{G^*}(x) = 11$.
Of these:
- $t - 1$ to other vertices of $K_t$;
- $1$ to $w$ (since $K_t$ inherits the join to the merged vertex via
  the original clique structure: $x$ was adjacent in $G$ to either
  $u_i$ or $u_j$ within the original clique, so $x$ is adjacent to $w$
  in $G^*$);
- $11 - t$ remaining, distributed among $L - \{v\}$ and $H \setminus N(v)$.

So each chunk vertex sends $11 - t$ edges to the rest.

Summing over $K_t$: total $t(11 - t)$ external edges from $K_t$ in
$G^*$.

For partition $(K_6, K_3)$ remainder (when original was $(7, 4)$
cross-clique merged): $K_6$ sends $6 \cdot 5 = 30$ external edges,
$K_3$ sends $3 \cdot 8 = 24$ external edges.

**Critical observation.** Each external edge from $K_t$ goes to either
$L - \{v\}$ (size 23) or $H \setminus N(v)$ (size 54). Edges to $L - \{v\}$
are constrained by $d_t \in \{0, 1, t\}$. Edges to $H \setminus N(v)$
are unconstrained at this level.

So we have a balance:

$$e(K_t, L - \{v\}) + e(K_t, H \setminus N(v)) = t(11 - t),$$

with $e(K_t, L - \{v\}) \le 23 - r_t + r_t \cdot t = 23 + r_t(t - 1)$.

(The $r_t$ vertices contributing $t$ edges replace what would have
been a degree-1 contribution.)

At $r_t = 0$: $e(K_t, L - \{v\}) \le 23$.
At $r_t = 8 - t$: $e(K_t, L - \{v\}) \le 23 + (8-t)(t-1)$.

For $K_6$: $t = 6$, $r_t \le 2$. Max edges to $L - \{v\}$: $23 + 2 \cdot 5 = 33$, but capped by total external edges $30$. So $e(K_6, L) \le 30$.

For $K_3$: $t = 3$, $r_t \le 5$. Max edges to $L - \{v\}$: $23 + 5 \cdot 2 = 33$, capped by $24$. So $e(K_3, L) \le 24$.

**These caps are not tight enough alone to give a contradiction.** But
combined with biplanarity of $G$ and the structural constraints on $L$
(also a Gallai forest, since $G$ itself is 12-critical), we have an
accumulating set of constraints. The next concrete attack: bound the
edges from *every* clique chunk plus the cross-chunk Gallai constraints
in $G^*[L^*]$ jointly, and check against the actual edge count of
$G^*$.

**Open: complete the Q0 ruling.** The Gallai-forest constraints on
$G^*[L^*]$ are concrete: 32 vertices, blocks are $K_s$ ($s \le 8$) or
odd $C_s$, with the 9-vertex $N(v) - \{u_i, u_j\}$ region forming
inherited clique chunks. The exact edge budget and the criticality
condition on the $H \setminus N(v) \cup \{w\}$ part should jointly
overdetermine the system. Concrete next-session task: enumerate the
possible Gallai-forest structures on $L^*$ consistent with the
inherited clique structure and check whether any produces a graph
consistent with $\rho_{12}(G^*) = 86$.

## Step 7 — Q0 profile model (corrected accounting)

Per review: the $\varepsilon_t$ correction and the outside-vertex
exclusivity together give a far smaller search space than enumerating
Gallai forests on 32 vertices.

### 7.1 Setup

Fix the partition $G[N(v)] = K_{s_1} \sqcup K_{s_2} \sqcup \cdots \sqcup K_{s_p}$
with $\sum s_i = 11$ and each $s_i \le 7$. Fix a cross-clique non-edge
$\{u_i, u_j\}$ with $u_i \in K_{s_a}$, $u_j \in K_{s_b}$, $a \ne b$.
After contraction:

- $K_{s_a}$ becomes the chunk $K_{s_a - 1}$ in $G^*[N(v) - \{u_i, u_j\}]$.
- $K_{s_b}$ becomes $K_{s_b - 1}$.
- All other cliques $K_{s_c}$ ($c \ne a, b$) are unchanged.

Define $\varepsilon_i = 1$ if chunk $i$ came from $K_{s_a}$ or $K_{s_b}$
(i.e. it's adjacent to $w$ via the inherited edge to $u_i$ or $u_j$),
else $\varepsilon_i = 0$.

### 7.2 Corrected chunk-vertex degree accounting

Each vertex of chunk $C_i$ (size $t_i$) in $G^*$ has degree 11. Decomposed:

- $t_i - 1$ within $C_i$;
- $\varepsilon_i$ edges to $w$ (only chunks descended from $K_{s_a}$ or
  $K_{s_b}$);
- the remaining $12 - t_i - \varepsilon_i$ edges go to
  $(L - \{v\}) \cup (H \setminus N(v))$ — i.e. to vertices outside
  $N(v)$ in $G$.

(Edges from $C_i$ to other chunks $C_j$ are zero, since $G[N(v)]$ is
disjoint cliques.)

Total external edges from chunk $C_i$:

$$e_i^{ext} = t_i \, (12 - t_i - \varepsilon_i).$$

### 7.3 Outside-vertex exclusivity (the sharper Q0 lever)

**Claim.** In Q0, every vertex $w' \in V(G) \setminus (N(v) \cup \{v\})$
is adjacent (in $G$) to vertices in **at most one** original clique of
$G[N(v)]$.

*Proof.* If $w'$ were adjacent to $u \in K_{s_a}$ and $u' \in K_{s_b}$
with $a \ne b$, then $\{u, u'\}$ is a non-edge in $N(v)$ (cliques are
disjoint) and $w' \in N(u) \cap N(u')$. So $q(u, u') \ge 1$, contradicting
Q0. $\square$

So the 77 outside vertices partition into $p + 1$ classes by which
clique they're attached to (or unattached): $O_0$ (unattached) plus
$O_1, \ldots, O_p$ (attached only to $C_i$).

### 7.4 Low-vertex quantized attachment

**Claim.** For each surviving chunk $C_i$ with size $t_i \ge 3$ and each
$L_0 \in L - \{v\}$ (low outside vertex), the attachment
$|N_{G^*}(L_0) \cap V(C_i)| \in \{0, 1, t_i\}$.
For $t_i = 2$, the attachment is in $\{0, 1, 2\}$.

(For $t_i = 1$, the clique is a singleton; $L_0$ adjacent to it or not.)

*Proof.* Same Gallai-forest argument: partial attachment $2..t_i-1$ would
make the block containing $C_i \cup \{L_0\}$ neither a clique nor an
odd cycle. $\square$

Moreover, vertices fully attached to $C_i$ (i.e. with $L_0$ adjacent
to all $t_i$ vertices of $C_i$) form a clique with $C_i$ in $G^*[L^*]$,
so the count $f_i$ of such $L_0$'s satisfies $f_i \le 8 - t_i$ from $K_9$-freeness.

(Note: by Q0 outside-vertex exclusivity, $L_0$ can be fully attached to at
most one chunk; so the $f_i$'s are over disjoint sets of $L_0$'s.)

### 7.5 The profile variables

For each chunk $C_i$ ($i = 1, \dots, p'$, where $p' = $ number of chunks
in $G^*[N(v) - \{u_i, u_j\}]$ — equals $p$ if $s_a, s_b \ge 2$, but a
$K_1$ component disappears):

- $f_i \in [0, 8 - t_i]$ — low vertices fully attached to $C_i$;
- $p_i \in [0, 23 - \sum_j f_j]$ — low vertices singly attached to $C_i$;
- $h_i$ — high outside edges to $C_i$, with $h_i = e_i^{ext} - (t_i f_i + p_i)$.

(High = $H \setminus N(v)$, since $w$-edges are already counted via $\varepsilon_i$.)

For each $i$:

$$\boxed{t_i f_i + p_i + h_i = t_i (12 - t_i - \varepsilon_i).}$$

### 7.6 Outside-vertex packing

- Total low vertices in $L - \{v\}$: 23. Each $L_0$ is at most fully
  attached to one chunk, plus may have additional single attachments —
  *but* the exclusivity (7.3) says no, $L_0$ attaches to **at most one
  $C_i$**. So even a single attachment uses up the $L_0$'s
  "attachment quota". Hence

$$\sum_i (f_i + p_i) \le 23.$$

- Total high outside vertices (= $H \setminus N(v)$): 54. Each may attach
  to one $C_i$ with some number of edges. By exclusivity, each
  $w' \in H \setminus N(v)$ has all its $N(v)$-edges to one specific $C_i$.

  For each $w' \in H \setminus N(v) \cap O_i$, let $h_i(w') = |N(w') \cap V(C_i)|$.
  $w'$ has degree 12 in $G$, so $h_i(w')$ edges to $C_i$, plus $12 - h_i(w')$
  edges to $(V \setminus N(v) \setminus \{v\}) \cup \{v\}$ — but $w' \not\in N(v)$
  and $v \not\in V(G - v)$, so $12 - h_i(w')$ edges to other vertices in
  $V(G) \setminus N(v) \setminus \{v, w'\}$.

  Total $h_i$ from this class: $h_i = \sum_{w' \in O_i \cap (H \setminus N(v))} h_i(w')$.

Same Gallai-forest argument applies for $h_i(w')$ at the high vertices
in $G^*[L^* \cup ?]$... wait, $w'$ is a degree-12 vertex of $G^*$, not
in $L^*$. So the Gallai-forest constraint doesn't apply to $w'$ directly.

The "$0, 1,$ or $t_i$" quantization is a property of *low* outside
vertices (those in $L - \{v\}$) attaching to a clique $C_i$ via the
Gallai-forest constraint on $G^*[L^*]$.

For high outside vertices $w'$, the attachment can be any number
$0 \le h_i(w') \le t_i$, with no Gallai constraint. (High vertices are
not in $L^*$, so they don't participate in the Gallai forest.)

### 7.7 The finite enumeration

Variables, per partition $\{s_1, \dots, s_p\}$ and cross-clique merge
choice $(a, b)$:

- chunk sizes $t_1, \dots, t_{p'}$ derived from the partition and merge;
- $\varepsilon_i \in \{0, 1\}$ derived (1 iff chunk comes from $K_{s_a}$ or $K_{s_b}$);
- $f_i \in [0, 8 - t_i]$;
- $p_i \ge 0$;
- $h_i \ge 0$;
- subject to:
  - $t_i f_i + p_i + h_i = t_i (12 - t_i - \varepsilon_i)$ per chunk;
  - $\sum (f_i + p_i) \le 23$;
  - $\sum_i \lceil h_i/t_i \rceil \le 54$ (high outside vertices can
    contribute at most $t_i$ chunk-edges to $C_i$ and attach to at most
    one original clique);
  - $w$-outside capacity: with
    $w_{\mathrm{out}} = 22 - \sum_i \varepsilon_i t_i$, vertices already
    committed to non-selected chunks cannot also be $w$-neighbours, so
    $$w_{\mathrm{out}} \le 77 -
      \sum_{\varepsilon_i = 0}\left(f_i + p_i + \lceil h_i/t_i\rceil\right).$$

Plus the overall edge count of $G^*$: $|E(G^*)| = 511$, with edges
partitioned into intra-chunk + chunk-to-$w$ + chunk-to-outside +
outside-outside + $w$-outside.

This is a small system. For each partition, the enumeration runs in
seconds.

### 7.8 Enumeration result

Implemented in [`scripts/q0_profile_enum.py`](../scripts/q0_profile_enum.py).
With symmetric equal-size merge choices collapsed, the run checks 49
partitions and 160 genuine merge types:

```text
$ python3 scripts/q0_profile_enum.py --limit 80
# partitions=49 merge_cases=160
# feasible_cases=143 infeasible_cases=17 capped_counts=0
# verdict: FEASIBLE profiles remain (necessary-condition model only)
```

With symmetric duplicates included, this corresponds to 396 feasible
merge choices out of 652.

So the Step 7 profile system **does not kill Q0**. The obstruction is
plain in the witnesses: for most surviving cases, taking $f_i=p_i=0$
for every chunk and routing all chunk-external demand to high outside
vertices satisfies the low-packing, high-packing, $w$-outside capacity,
and outside-edge-count constraints. For instance, the $(7,4)$ partition
with the unique cross-merge leaves chunks $(6,\varepsilon=1)$ and
$(3,\varepsilon=1)$ and has the witness

$$
(f,p,h) = (0,0,30),\ (0,0,24),
$$

using only 13 high outside vertices in the packing bound and no low
outside vertices.

The 17 infeasible merge types are all-small partitions, e.g.
$(1^{11})$, $(2,1^9)$, $(2,2,1^7)$, $(2,2,2,1^5)$,
$(3,1^8)$, $(3,2,1^6)$, and $(4,1^7)$; this is much too narrow to
settle Q0.

**Conclusion.** The current Q0 profile model is a diagnostic filter,
not a contradiction. The next local lemma has to rule out the high-only
witness shape: either force some chunk-to-low attachment, or prove that
the high outside vertices cannot absorb all chunk demand without
violating biplanarity / $K_9$-freeness / criticality elsewhere.

### 7.9 Why naive local biplanarity does not tighten the model

The natural first attempt is to apply the biplanar edge bound on
$C_i \cup A_i$ (the chunk plus its $a_i$ high-outside attached
vertices):

$$\binom{t_i}{2} + \underbrace{t_i(12 - t_i - \varepsilon_i)}_{\text{demand } D_i}
  \le 6(t_i + a_i) - 12.$$

Rearranging gives $a_i \ge \big(\binom{t_i}{2} + D_i + 12\big)/6 - t_i$.
But this is *weaker* than the existing packing bound
$a_i \ge \lceil D_i/t_i \rceil = 12 - t_i - \varepsilon_i$
(because each high vertex contributes at most $t_i$ chunk-edges) in
every relevant case. Concretely:

| $t$ | $\varepsilon$ | demand $D$ | packing LB | local-biplanar LB |
|---:|---:|---:|---:|---:|
| 6 | 1 | 30 | **5** | 4 |
| 3 | 1 | 24 | **8** | 4 |
| 6 | 0 | 36 | **6** | 5 |
| 7 | 0 | 35 | **5** | 5 |

So the raw $6(n)-12$ count on $C_i \cup A_i$ never beats packing in
the surviving regime. Plain edge-count biplanarity will not close
Q0 high-only.

### 7.10 Next move — layer-aware local capacity

The right replacement for the trivial $h_i \le t_i a_i$ bound is the
**exact biplanar capacity**: for fixed $(t, \varepsilon, a)$, compute

$$\mathrm{cap}(t, \varepsilon, a) :=
  \max \big\{ |E(C_i, A)| \mid G' \supseteq K_t,
              G' \text{ biplanar},
              |A| = a,
              \deg_{G'}(w) \ge \varepsilon \cdot t \big\},$$

over all biplanar graphs $G'$ on $t + a + \varepsilon$ vertices
containing $K_t$ as a subgraph and (if $\varepsilon = 1$) a vertex $w$
adjacent to all of $K_t$.

If $\mathrm{cap}(6, 1, 5) < 30$, the $(7,4)$ witness dies. If
$\mathrm{cap}(3, 1, 8) < 24$, the $K_3$-chunk side dies. Likewise for
the other surviving regimes $(6, 0, 6)$ and $(7, 0, 5)$.

The trivial upper bound is $\mathrm{cap}(t, \varepsilon, a) \le t \cdot a$
(every outside vertex contributes at most $t$ chunk-edges), achieved by
all-attached configurations when those are biplanar. The question is
whether the biplanar constraint forces a strict inequality.

**Sub-target.** Determine $\mathrm{cap}(6, 1, 5)$. The all-attached
upper bound is $30$. Each of the 5 outside vertices fully attached to
$K_6$ forms a $K_7$ with $K_6$, and pairwise structural constraints
from $K_9$-freeness (at most 2 of the 5 fully-attached can be mutually
adjacent, else $K_9$) + biplanarity (need to actually embed the
resulting subgraph in two planar layers) may force
$\mathrm{cap}(6, 1, 5) \le 29$ or smaller.

### 7.11 Layer-aware probes — first results

Implemented `scripts/biplanar_check.py` (generic biplanarity tester via
SMS v1.0.0 with fixed edge constraints + initial-partition for the
correct automorphism group). Four probes:

| graph | $(t, \varepsilon, a)$ | edges | biplanar? | wall |
|---|---|---:|---|---:|
| $K_4 + \overline{K_8}$ | $(3, 1, 8)$ saturated | 38 | SAT | 0.006s |
| $K_6 + \overline{K_6}$ | $(6, 0, 6)$ saturated | 51 | SAT | 0.010s |
| $K_7 + \overline{K_5}$ | $(7, 0, 5)$ / sat. $(6, 1, 5)$ | 56 | **UNSAT** | **13.1s** |
| $K_7 \cup \overline{K_5}$ to $K_6$ only | weak $(6, 1, 5)$ | 51 | SAT | 0.086s |

**Headline.** $K_7 + \overline{K_5}$ is not biplanar.

So $\mathrm{cap}(6, 1, 5) = 30$ on the chunk-to-outside edges *alone*,
but if those 5 outside vertices are *additionally* all adjacent to $w$
(the $\varepsilon = 1$ merged vertex), the local subgraph becomes
$K_7 + \overline{K_5}$ and biplanarity fails. So the saturated
$(7, 0, 5)$ and $(6, 1, 5)$-with-also-adjacent-to-$w$ profiles die.

**What this does NOT kill.** The weaker $(6, 1, 5)$ profile, where the
5 outside vertices each have $h_{u'} = 6$ to the $K_6$ chunk but are
*not* adjacent to $w$: it is biplanar. So Q0 survives if the
chunk-serving outside vertices can avoid being among $w$'s neighbours.

**Structural question.** In the Q0 setup, the
vertex $u_i$ (the merged endpoint contributing to $w$) has 5 outside
neighbours in $G$ — these become the 5 $u_i$-attached neighbours of
$w$ in $G^*$. The 5 chunk-fully-attached outside vertices may overlap
with this set or be disjoint:

- *Fully overlapping* (all 5 chunk-attached are also $u_i$-neighbours):
  local subgraph is $K_7 + \overline{K_5}$, UNSAT, contradiction. Killed.
- *Disjoint* (none of the 5 chunk-attached are $u_i$-neighbours):
  local subgraph is the weak version, SAT (biplanar). Survives.
- *Partial overlap* (some): transition computed below.

Added `--chunk-overlap t,a,s` to `scripts/biplanar_check.py`, where
$t=6$, $a=5$, and $s$ is the number of chunk-attached outside vertices
also adjacent to $w$. This mode also supplies the correct SMS initial
partition, avoiding the custom-edges over-pruning issue.

The overlap sweep gives:

| $s$ | edges | biplanar? | wall |
|---:|---:|---|---:|
| 0 | 51 | SAT | 0.013s |
| 1 | 52 | SAT | 0.013s |
| 2 | 53 | SAT | 0.019s |
| 3 | 54 | **UNSAT** | 55.5s |
| 4 | 55 | **UNSAT** | 44.5s |
| 5 | 56 | **UNSAT** | 35.3s |

So there is a genuine threshold: local biplanarity kills overlap
$s \ge 3$ but permits $s \le 2$.

**Conclusion.** The $(7,4)$ high-only witness survives only if the
5 chunk-serving vertices overlap the $u_i$-outside-neighbour set in at
most two vertices. The next structural target is therefore not
"any overlap" but the sharper statement

$$
|A(K_6) \cap N_G(u_i) \setminus N(v)| \ge 3,
$$

where $A(K_6)$ is the set of high outside vertices serving the $K_6$
chunk. If degree counting, Q0 exclusivity, or the $K_3$ chunk side can
force this $\ge 3$ overlap, the $(7,4)$ Q0 case dies.

### 7.12 Larger one-sided probe — adding the $u_i$-only vertices

The next natural test is to include not only the $K_6$ chunk and its
5 chunk-serving vertices, but also the $5-s$ outside vertices adjacent
to $u_i$ and not to the $K_6$ chunk. This is the pre-contraction local
graph on

$$
K_6 \cup \{u_i\} \cup A(K_6) \cup (U_i \setminus A(K_6)).
$$

Added `--chunk-endpoint-overlap t,a,u,s` to
`scripts/biplanar_check.py` for this pattern. In the $(7,4)$ case,
$(t,a,u)=(6,5,5)$; the forced edge count is always 56, while the
vertex count is $17-s$.

The low-overlap cases, which are the only cases not already killed by
the smaller overlap probe, are all biplanar:

| $s$ | vertices | edges | biplanar? | wall |
|---:|---:|---:|---|---:|
| 0 | 17 | 56 | SAT | 0.028s |
| 1 | 16 | 56 | SAT | 0.019s |
| 2 | 15 | 56 | SAT | 0.018s |

For $s \ge 3$, the graph contains the previously tested non-biplanar
chunk-overlap subgraph, so those cases are already UNSAT by monotonicity.

**Conclusion.** Adding the $u_i$-only vertices does not create a
one-sided local biplanarity obstruction. The $(7,4)$ Q0 high-only case
still survives whenever $s \le 2$. The next attack must either prove
the overlap lower bound $s \ge 3$ from global structure, or couple the
$K_6/u_i$ side with the $K_3/u_j$ side in a single local probe.

## Status

Phase 6 is now reduced to two concrete combinatorial problems:

1. **Step 4+**: of the $\ge 6$ non-edges in $N(v)$, at least one with
   $q \ge 1$ must contract without creating a split $K_8$.
2. **Q0 high-only closure** (Step 7 above): the profile enumeration
   leaves 143 feasible merge types, mostly with $f_i=p_i=0$. The current
   sharp subtarget in the $(7,4)$ case is forcing the $K_6$ overlap
   $s \ge 3$, or else coupling the $K_6/u_i$ and $K_3/u_j$ sides.

Either piece, if closed, eliminates the isolated-low-vertex subcase
at $n = 89$ and is the first non-trivial step beyond Brooks-type's
$n \le 88$ closure.
