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
