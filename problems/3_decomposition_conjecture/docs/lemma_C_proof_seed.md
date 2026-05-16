# Lemma C proof seed — three-part decomposition + swap mechanism

The empirical content of Lemma C, sharpened by the n=14 sweep to a
single-trace dichotomy, decomposes into three pieces:

1. **Cycle-bypass lemma** (target). Both port-bypass traces exist in
   any essentially-3-connected 2-pole subcubic side.
2. **Matching-joined / M-axis dichotomy** (target). Either
   $(T_{TM}, T_{TM})$ joined is realisable, or both M-axis traces are.
3. **Closure** (immediate from 1 and 2). In the joined case, reduce by
   $C_0$. In the M-axis case, the side is compatibility-universal via
   the M-axis pair + the bypass traces; reduce by Lemma 3.13.

## 1. Cycle-bypass lemma

**Lemma (Cycle-bypass).** Let $H$ be a 2-pole subcubic graph,
essentially-3-connected (no bridge, no articulation, only port-trivial
2-vertex-cuts) with $|V(H)| \ge 4$. Then for each port $a_i$ there is
a valid edge partition of $H$ realising the trace
$(\chi(a_i), \chi(a_{1-i})) = (T_{CC}, T_T)$ (or the mirror) with
$\pi$ split.

**Proof sketch.** Set $i = 0$ (symmetric for $i = 1$). Let $u, v$ be
the two neighbours of $a_0$ in $H$.

*Step 1 — a cycle through $a_0$ exists.* Consider $H - \{a_0\}$. By
essential 3-connectivity, $H$ has no articulation vertex; the removal
of a degree-2 vertex preserves edge-connectedness of the remaining
graph (an articulation in $H - \{a_0\}$ would already be one in $H$,
since $a_0$'s degree-2 nature contributes only to the port-trivial
2-cut). In particular, $H - \{a_0\}$ is 2-edge-connected, so $u$ and
$v$ lie on a common cycle $C^* \subseteq H - \{a_0\}$.

Let $\hat C = C^* \cup \{(a_0, u), (a_0, v)\}$. This is a cycle of
$H$ through $a_0$.

*Step 2 — designate $\hat C$ as $C_H$ on a compatible partition.*
Assign:
- $C_H := \hat C$ (the cycle through $a_0$);
- $T_H \subseteq E(H) \setminus C_H$ a spanning forest of $H - \{a_0\}$
  with $a_{1-0}$ having both incident non-boundary edges in $T_H$;
- $M_H := E(H) \setminus (C_H \cup T_H)$.

The vertex-type assignments are then forced:
- Vertices on $\hat C$ (including $u$, $v$, and the cycle interior)
  have $\deg_C = 2$. For an internal vertex on $\hat C$: $\deg_C = 2$
  + the remaining edge is in $T_H$, giving local triple $(1, 2, 0) =
  V_C$. For the port $a_0$: side $(C, C)$, boundary $T$, state $T_{CC}$.
  ✓
- $a_{1-0}$: both side-edges $T$, boundary $T$, state $T_T$. Vertex
  type $V_T$. ✓
- Other vertices: $\deg_C = 0$, so $V_T$ or $V_M$, determined by the
  $T_H/M_H$ split.

*Step 3 — feasibility of the $T_H, M_H$ split.* The graph
$H - \{a_0\} - C^*$ is the "complement of the cycle" inside $H -
\{a_0\}$. Each vertex of $C^*$ has $\deg = 1$ in this complement
(its third edge); each non-$C^*$ vertex has full degree 3 in the
complement.

Choose $T_H$ as a spanning tree of $H - \{a_0\}$ whose leaves include
exactly the $V_M$ vertices (to be matched by $M_H$). For a graph with
$|V(H-\{a_0\})| \ge 3$ that is 2-edge-connected, such a "matching-
leaf spanning tree" exists by a straightforward induction (specifically,
contract $\hat C$ to a single vertex and use the standard "every cubic
graph with a perfect matching" property, then expand back).

The resulting partition is the desired $(T_{CC}, T_T)$ split trace.
$\square$

**Empirical verification.** All 14 essentially-3-conn n=14
$C_0$-exceptions realise both bypass traces; combined with the 7106
$C_0$-absorbed sides, every essentially-3-conn n=14 side does.

**Status.** The proof sketch above has the structural form of a real
proof; the gap is Step 3 (the matching-leaf spanning tree existence).
This is a standard graph-theoretic claim that should be checkable by
ear decomposition of $H - \{a_0\}$.

## 2. Matching-joined / M-axis dichotomy

The n=14 evidence sharpens this to:

**Lemma (Matching-joined / M-axis dichotomy, target).** Let $H$ be
essentially-3-connected 2-pole subcubic with $|V(H)| \ge 4$. Then:

$$
(T_{TM}, T_{TM})_{\mathrm{joined}} \in \mathrm{Trace}(H)
\quad \text{OR} \quad
\{(M_{TT}, T_T),\ (T_T, M_{TT})\} \subseteq \mathrm{Trace}(H).
$$

The plausible proof is **edge-swap on the (T_TM, T_TM) split
partition**:

Given a split $(T_{TM}, T_{TM})$ realisation $\sigma$ (which always
exists in essentially-3-connected $H$: cycle-bypass + standard tree
arguments produce one), we attempt a matching-swap at each port to
build $(M_{TT}, T_T)$ and its mirror.

## 3. Swap mechanism (formal statement and proof obligations)

Let $\sigma$ be a $(T_{TM}, T_{TM})$ split realisation of $H$:
- both ports $a_0, a_1$ in $V_M$ state with side $(T, M)$;
- $T_H$ split into two components $A$ (containing $a_0$) and $B$
  (containing $a_1$);
- $C_H$ 2-regular; $M_H$ a matching;
- at each port $a_i$, let $m_i$ denote the unique inside M-edge,
  connecting $a_i$ to internal vertex $w_i$, and let $t_i$ denote
  the unique inside T-edge, connecting $a_i$ to internal vertex
  $u_i$.

**Lemma (Swap, statement).** Suppose $w_0 \in B$ (so $m_0$ crosses
the T-cut between $A$ and $B$). Then the partition $\sigma'$ obtained
from $\sigma$ by:

- changing $m_0$ from $M$ to $T$;
- changing the boundary edge of $a_0$ from $T$ to $M$;
- if necessary, demoting one $T$-edge on the cycle of $T_H \cup
  \{m_0\}$ to break the cycle (see below);

is a valid realisation of $(M_{TT}, T_{TM})$ or $(M_{TT}, T_T)$ in
$H$ (depending on what else is touched).

**Proof obligations** (each must be discharged for the swap lemma to
hold):

(a) *Forest preservation.* After adding $m_0$ to $T_H$, the result is
   $T_H \cup \{m_0\}$ which connects $A$ to $B$ (since $w_0 \in B$).
   By itself this is a tree on all of $V(H)$, i.e. $|T_H \cup \{m_0\}|
   = n - 1$ ✓.

(b) *Vertex-type validity at $w_0$.* The vertex $w_0$ had local triple
   $(\deg_T, \deg_C, \deg_M) = (2, 0, 1) = V_M$ in $\sigma$ (since
   $m_0$ was its M-edge). After removing $m_0$ from $M$ and adding it
   to $T$: $(3, 0, 0) = V_T$. ✓

(c) *Vertex-type validity elsewhere.* No other vertex changes type
   except $w_0$ and $a_0$, so all other vertices retain valid local
   triples. ✓

(d) *Matching property.* Removing $m_0$ from $M$ removes one edge.
   The boundary edge at $a_0$ is added to $M$ globally (the matching
   now extends across the cut). At $a_0$: $\deg_M = 1$ (the boundary
   edge). At $b_0$ (the other endpoint of the boundary edge in $B$):
   $\deg_M = 1$, requiring $b_0$ to be $V_M$ on the other side. This
   is a constraint on the $B$-side trace, exactly the boundary
   constraint matching $(M_{TT}, *)$ says.

(e) *2-regularity of $C_H$.* $C_H$ unchanged ✓.

If $w_0 \in A$ (same component as $a_0$): adding $m_0$ creates a cycle
$P$ in $T_H \cup \{m_0\}$, where $P$ runs from $a_0$ to $w_0$ in
$T_H \cap A$ and then back via $m_0$. To restore a forest, demote some
edge of $P$ from $T$. The candidate edge must satisfy (b)-(c) after
demotion:

- It can become $C$: only valid if its endpoints have room in their
  $C$-degree (most internal vertices in $\sigma$ are $V_T$ or $V_M$,
  with $\deg_C = 0$). Adding $C$-edges would force them to $V_C$,
  which requires $\deg_C = 2$. Need to find a *pair* of edges to
  promote to $C$ simultaneously, forming a new cycle of $C_H$.
- It can become $M$: only valid if both endpoints are $V_M$ with
  $\deg_M = 0$ (no other matching edge). Possible if the swapped edge
  has both endpoints currently $V_T$ (degT = 3) and they have flexibility.

The cleanest case is **Case (a): $w_0 \in B$** — adjusted, no
demotion needed. The harder Case (b) requires the demotion argument
above.

**Empirical test of the simple swap.** The simple-swap case
($w_0 \in B$) should suffice for the 14 exceptions, since they all
realise the M-axis traces. A direct check is the next concrete
deliverable: scan all $(T_{TM}, T_{TM})$ split partitions of each of
the 7 exception graphs, and confirm at least one has $w_0 \in B$ AND
$w_1 \in A$ (the symmetric condition for the mirror swap to give
$(T_T, M_{TT})$).

If yes, the swap mechanism is the right one and Lemma C will close.
If no, the demotion argument or a different transition is needed.

## 4. Combined Lemma C statement (target)

**Lemma C (essentially-3-conn dichotomy, target).** Let $H$ be an
essentially-3-connected 2-pole subcubic graph with $|V(H)| \ge 4$.
Then:

- both bypass traces $(T_{CC}, T_T)$ split and $(T_T, T_{CC})$ split
  are in $\mathrm{Trace}(H)$ (Cycle-bypass lemma, §1);
- either $(T_{TM}, T_{TM})$ joined is in $\mathrm{Trace}(H)$
  (giving full $C_0$ containment, with the bypass traces above), or
  both M-axis traces $(M_{TT}, T_T)$ and $(T_T, M_{TT})$ are in
  $\mathrm{Trace}(H)$ (giving compatibility-universality via the
  bypass + M-axis combo).

In either branch, $H$ is reducible: by $C_0$ in the joined branch, by
Lemma 3.13 in the M-axis branch.

## 5. Empirical test of the simple swap on the 7 exception graphs

Computed via `/tmp/test_swap_mechanism.py`: for each of the 7 essentially-
3-conn n=14 C₀-exception graphs, enumerate every $(T_{TM}, T_{TM})$ split
partition; for each, identify $w_0, w_1$ (the M-side-edge neighbours)
and check whether they are in the opposite T-components from their
respective ports.

| graph6 | split parts | $w_0 \in B$ | $w_1 \in A$ | BOTH |
|---|---:|---:|---:|---:|
| `M??CB?WDU_OoI_PG?` | 28 | 22 | 22 | **16** |
| `M??CB?WPU_EOB_gG?` | 18 | 10 | 16 | **8** |
| `M??CB?WSRGT?B_`G?` | 8 | 8 | **0** | **0** |
| `M??CB?WSUGT?H_BG?` | 8 | 8 | **0** | **0** |
| `M??CB?WXB_PGB_`G?` | 12 | 12 | **0** | **0** |
| `M??ED@OBCSF?DGWC?` | 12 | 6 | 6 | **0** |
| `M?AA@AOY@c@WPOaG?` | 8 | 6 | 6 | **4** |

**Key observation.** The simple double-swap (requiring $w_0 \in B$
AND $w_1 \in A$ in the same partition) succeeds on **3 of 7** exception
graphs (the three with BOTH > 0:
$M??CB?WDU$ at 16/28, $M??CB?WPU$ at 8/18, $M?AA@AOY$ at 4/8) and
**fails on 4** ($M??CB?WSRGT,\ M??CB?WSUGT,\ M??CB?WXB,\ M??ED@OBCSF$
— each has 0 BOTH-feasible partitions).

In the 3 "hard" graphs, every $(T_{TM}, T_{TM})$ split partition has
$w_1 \in B$ (port 1's M-edge has both endpoints inside $B$, the
T-component of port 1). The swap at port 1 would create a cycle in
$T_H$; the simple swap mechanism does not produce $(M_{TT}, T_T)$.

But the trace $(M_{TT}, T_T)$ IS realised in these 3 graphs — they
are absorbed by $C_2$, which contains $(M_{TT}, T_T)$. So the trace
exists; it is just **not obtainable by simple swap from any
$(T_{TM}, T_{TM})$ split partition**.

The realising $(M_{TT}, T_T)$ partition has a structurally different
$T_H$ (spanning tree on 13 edges with port 0 and port 1 both of
degree 2), not obtainable as a local modification of any split
$(T_{TM}, T_{TM})$ realisation.

## 6. Implications for Lemma C

The simple-swap mechanism is **not sufficient** as the universal
mechanism. Lemma C needs either:

(i) **A more global swap construction** — possibly via an alternating
    path argument that handles the cycle-creation by demoting a
    T-edge on the cycle (Case (b) of the original swap lemma);

(ii) **An independent construction** for $(M_{TT}, T_T)$ — directly
    finding a spanning tree of $H$ with both ports having degree 2,
    plus a compatible cotree decomposition.

For the 3 "hard" graphs, route (ii) is the only path: their split
$(T_{TM}, T_{TM})$ partitions structurally cannot be transformed
into $(M_{TT}, T_T)$ by a local edge swap.

**Structural observation about the 3 hard graphs.** All three have
identical port set $\{3, 6\}$ in `M??CB?WSRGT...`, `M??CB?WSUGT...`,
`M??CB?WXB...` — three closely-related 14-vertex graphs (the prefix
`M??CB?W` is shared). Their structural relationship suggests they may
be a localised family where port 1's neighbourhood traps the matching.

## 7. Next deliverable (revised)

1. **Prove the cycle-bypass lemma rigorously** (§1).

2. **Run the dichotomy check on the 7106 $C_0$-contained sides** to
   confirm that for them, simple-swap *would* succeed if applied —
   the simple swap is the "regular" mechanism and the 3 hard graphs
   are an exceptional pattern.

3. **Find the structurally-different mechanism for $(M_{TT}, T_T)$
   in the 3 hard graphs**. Direct enumeration of valid
   $(M_{TT}, T_T)$ partitions and inspection of their structure.

4. **Identify the structural feature** that distinguishes the 4
   "swap-feasible" exceptions from the 3 "swap-hard" exceptions.
   The 3 hard graphs share the prefix `M??CB?WS` (vs the 4
   feasible: `M??CB?WD`, `M??CB?WP`, `M??ED@O`, `M?AA@AO`); is there
   a common subgraph structure?

5. **Generalise Lemma C statement** to allow both swap-derivable and
   independent realisations.
