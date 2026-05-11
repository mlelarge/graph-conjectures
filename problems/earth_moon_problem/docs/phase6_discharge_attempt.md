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

## Step 5 — Computational fallback: LP over block-type profiles

If the hand-discharging gets murky, parameterise by block-type
frequencies. Let

$$n_t = \#\{K_t\text{-blocks in } G[L]\}, \quad 2 \le t \le 8,$$
$$c_r = \#\{C_{2r+1}\text{-blocks in } G[L]\}, \quad r \ge 1.$$

The Gallai-forest structure + biplanarity + Brooks-type tightness gives
a system of linear inequalities in $(n_t, c_r, \ell, h, e_{HH})$:

- $\sum t \cdot n_t + \sum (2r+1) c_r \le \ell +$ (cut-vertex slack)
- $\sum \binom{t}{2} n_t + \sum (2r+1) c_r = e_{LL}$
- $11 \ell + 12 h \le 2 m \le 12 n - 24$
- $m \ge \lceil (65 n - 43)/11 \rceil$ (Brooks-type)
- $|V(G)| = n$, $\ell + h = n$
- block-cut-tree balance equations

Solving this LP (or a small ILP) tells us whether the constraint system
is feasible. **Infeasible $\Rightarrow$ contradiction $\Rightarrow$
Phase 6 closed.** Feasible $\Rightarrow$ the LP solution identifies
the structural profile of the obstruction, which then guides what extra
local lemma is needed to rule it out.

This is a small enough LP to solve by hand or via `pulp`/`scipy.linprog`.
The optimisation is: maximise $m$ (equivalently, $e_{HH}$) subject to
the Gallai/biplanarity/Brooks-type constraints; if max $< 6n - 12$ we
contradict biplanarity directly, otherwise the extremal profile is
what we attack with structure.

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
