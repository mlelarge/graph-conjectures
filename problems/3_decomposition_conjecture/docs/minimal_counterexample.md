# Minimal counterexample to the 3-Decomposition Conjecture

This document develops the low-connectivity reductions needed to assert
that a smallest counterexample $G^\star$ is 3-edge-connected. The first
target is unconditional: bridges. The second target is the
**essential 2-edge-cut reduction**; it is the first serious mountain.

Conventions: $G$ is a connected cubic simple graph on $n$ vertices (so
$n$ is even, $|E(G)| = 3n/2$). A 3-decomposition is a partition
$E(G) = T \sqcup C \sqcup M$ with $T$ a spanning tree, $C$ 2-regular,
$M$ a matching. The vertex types $V_T, V_M, V_C$ are as in `plan.md` §
"Vertex-type reformulation".

## §1. Preliminaries: rooted sides and boundary traces

### 1.1 Rooted subcubic sides

A **subcubic graph** is a simple graph of maximum degree $\le 3$. A
**port** is a vertex of degree $\le 2$; its **port-degree** is
$3 - \deg(v)$, i.e. the number of missing half-edges. A
**$k$-pole side** is a pair $(H, R)$ where $H$ is a connected subcubic
graph and $R = (r_1, \dots, r_k)$ is an ordered tuple of distinct port
vertices with port-degrees summing to $k$. (For a bridge: $k = 1$ and
the unique port has port-degree 1. For a proper 2-edge-cut with four
distinct endpoints: $k = 2$, each port has port-degree 1.)

### 1.2 Port states

Given a port $r$ of port-degree 1 (i.e. $\deg_H(r) = 2$), suppose $r$ is
to be glued into a cubic supergraph via a boundary edge $e$. Once the
full-graph vertex type of $r$ is fixed, the local edge colouring at $r$
inside $H$ is determined:

| Port state | Full vertex type at $r$ | $e$-colour | $H$-edge 1 | $H$-edge 2 |
|---|---|---|---|---|
| $T_T$ | $V_T$ ($\deg_T = 3$) | $T$ | $T$ | $T$ |
| $T_{TM}$ | $V_M$ ($\deg_T = 2$, $\deg_M = 1$) | $T$ | $T$ | $M$ |
| $M_{TT}$ | $V_M$ ($\deg_T = 2$, $\deg_M = 1$) | $M$ | $T$ | $T$ |
| $T_{CC}$ | $V_C$ ($\deg_T = 1$, $\deg_C = 2$) | $T$ | $C$ | $C$ |
| $C_{TC}$ | $V_C$ ($\deg_T = 1$, $\deg_C = 2$) | $C$ | $T$ | $C$ |

(The subscript names the colours of the two $H$-edges at $r$, in some
canonical order.) Five states per port-degree-1 port. The five states
partition by $e$-colour: three with $T$ ($T_T, T_{TM}, T_{CC}$), one
with $M$ ($M_{TT}$), one with $C$ ($C_{TC}$).

### 1.3 Boundary trace and trace set

For a $k$-pole side $(H, R)$, a **boundary trace** is a pair
$(\chi, \pi)$ where:

- $\chi : R \to \text{(port states)}$ assigns a port state to each $r_i$;
- $\pi$ is an equivalence relation on the $T$-incident boundary
  half-edges of the ports, recording which boundary half-edges lie in
  the same connected component of $T_H := T \cap E(H)$ inside $H$.

(For a single port of port-degree 1, $\pi$ is trivial. For two ports of
port-degree 1, $\pi$ has two possibilities when both are $T$-incident:
"same tree component inside $H$" or "different components". When some
ports are not $T$-incident, $\pi$ is correspondingly trimmed.)

A trace $(\chi, \pi)$ is **realisable on $(H, R)$** if there exists a
partition $E(H) = T_H \sqcup C_H \sqcup M_H$ with:

1. $T_H$ a forest spanning $V(H)$ minus any port vertices not
   $T$-incident under $\chi$, with every tree component incident to at
   least one $T$-coloured boundary half-edge (otherwise that component
   could never attach to the global spanning tree);
2. $C_H$ 2-regular as a subgraph of $H$;
3. $M_H$ a matching of $H$;
4. the local colouring at each $r_i$ matching $\chi(r_i)$;
5. the connected components of $T_H \cup \{\text{tree boundary stubs}\}$
   matching $\pi$.

Let $\mathrm{Trace}(H, R)$ denote the set of realisable boundary traces.

### 1.4 Gluing

Two compatible rooted sides $(H_A, R_A), (H_B, R_B)$ glue across a
fixed matching of their ports (one boundary edge per port pair) to give
a graph $G$. Traces $\sigma_A \in \mathrm{Trace}(H_A, R_A)$ and
$\sigma_B \in \mathrm{Trace}(H_B, R_B)$ are **boundary-compatible** if:

(i) the port state on each side determines the same colour for the
    shared boundary edge (so paired $V_T$-ports give $T$-colour edges,
    paired $V_M$-ports with $M$-at-boundary on one side and $T$-at-
    boundary on the other are *not* compatible, etc.);
(ii) the tree-connectivity partitions $\pi_A, \pi_B$ glue along the
    boundary edges to a single tree (i.e. the resulting graph on
    boundary half-edges using $\pi_A \cup \pi_B \cup \{\text{boundary
    edges of colour } T\}$ is a tree).

A boundary-compatible pair combines into a 3-decomposition of $G$.

## §2. Lemma 1 — Bridge reduction (unconditional)

**Lemma 1 (Bridge reduction).** Let $G$ be a connected cubic graph with
a bridge $e = uv$. Let $(G_u, u)$ and $(G_v, v)$ be the two
1-pole rooted sides of $G - e$ (each port of port-degree 1). Then $G$
admits a 3-decomposition if and only if there exist port states
$s_u, s_v \in \{T_T, T_{TM}\}$ and traces realising them on each side that
are boundary-compatible across $e$.

(The two bridge-admissible port states. $T_T$: both side edges in $T$,
boundary in $T$ (full $V_T$). $T_{TM}$: one side edge in $T$, one in $M$,
boundary in $T$ (full $V_M$). The other three states $\{M_{TT}, C_{TC},
T_{CC}\}$ are excluded at a bridge port — see proof.)

*Proof.*

$(\Rightarrow)$ Let $(T, C, M)$ be a 3-decomposition of $G$.

**Claim.** $e \in T$.

Suppose $e \in C$. Then $e$ lies on a cycle of $C$. But $e$ is a bridge,
so its removal disconnects $G$ — $e$ lies on no cycle of $G$, hence
none of $C \subseteq G$ either. Contradiction.

Suppose $e \in M$. Then in $T$, $u$ and $v$ are connected by a path $P$.
Removing $e$ from $G$ disconnects $u$ and $v$, but $P$ avoids $e$ (since
$e \in M$, not $T$), so $P$ is a $u$-$v$ path in $G - e$ — contradiction.

So $e \in T$. Then $T \setminus \{e\}$ has exactly two components whose
vertex sets are $V(G_u)$ and $V(G_v)$ (because removing a tree edge
splits the tree into two subtrees, and a bridge separates $G$ in the
same way). Hence $T_u := T \cap E(G_u)$ is a spanning tree of $G_u$ and
similarly for $T_v$. In particular $\deg_{T_u}(u) \ge 1$.

At $u$ inside $G_u$, the colours of the two side-edges are determined by
$u$'s full vertex type. Since $T_u$ is a spanning tree of $G_u$ and
$|V(G_u)| \ge 2$ (because $G$ is cubic, $u$ has 3 edges, only one of
which is $e$), $\deg_{T_u}(u) \ge 1$. So:

- $u \in V_T$ (full $\deg_T = 3$): all three $T$-edges at $u$ in full
  $G$; inside $G_u$, both side-edges are $T$. State $T_T$.
- $u \in V_M$ (full $\deg_T = 2$, $\deg_M = 1$): one of $u$'s $T$-edges
  in full $G$ is $e$; the remaining $T$-edge and the unique $M$-edge
  are inside $G_u$. State $T_{TM}$.
- $u \in V_C$ (full $\deg_T = 1$, $\deg_C = 2$): the single $T$-edge at
  $u$ must be $e$ (proved above); so $\deg_{T_u}(u) = 0$, contradicting
  $\deg_{T_u}(u) \ge 1$.

Hence the restricted port state at $u$ is $T_T$ or $T_{TM}$. The same
analysis at $v$.

Set $\sigma_u, \sigma_v$ to these. Boundary compatibility:
- both port states have $T$-colour on the boundary, matching $e \in T$;
- the bridge $e$ joins the tree components $T_u, T_v$ into a single
  spanning tree, so the tree-connectivity partition is automatically
  satisfied.

$(\Leftarrow)$ Given $\sigma_u \in \mathrm{Trace}(G_u, u)$ and
$\sigma_v \in \mathrm{Trace}(G_v, v)$ with port states in
$\{T_T, T_{TM}\}$, take the corresponding edge partitions of $E(G_u)$ and
$E(G_v)$. Put $e \in T$. The union $T_u \cup \{e\} \cup T_v$:

- spans $V(G) = V(G_u) \cup V(G_v)$ (each side tree spans its side, $e$
  joins them);
- is connected (each side tree is connected, $e$ joins them);
- is acyclic ($T_u, T_v$ acyclic; $e$ joins disjoint components, so no
  cycle through $e$; no cycle within a side is created).

So it is a spanning tree of $G$. The $C$-edges and $M$-edges of $G$ are
exactly $C_u \cup C_v$ and $M_u \cup M_v$, respectively; both
properties (2-regular, matching) are local to the sides and preserved
by disjoint union. Hence $(T, C, M)$ is a 3-decomposition of $G$. $\square$

### 2.1 From Lemma 1 to "no bridge in $G^\star$"

Lemma 1 reduces the cubic decomposition question for bridged $G$ to a
*subcubic-with-one-port* decomposition question. To conclude that a
minimal cubic counterexample has no bridge, we need a sub-lemma:

**Sub-lemma 1$'$ (subcubic existence; to be proved separately).**
For every connected subcubic graph $H$ with exactly one port $r$ of
port-degree 1, at least one of the port states $\{T_T, T_{TM}\}$ is
realisable on $(H, r)$.

Status of Sub-lemma 1$'$ in the literature:

- Aboomahigir–Ahanjideh–Akbari (*DAM* 296, 2021) prove decomposition
  results for claw-free subcubic and 4-chordal subcubic graphs; whether
  their statements directly cover both port states $\{T_T, T_{TM}\}$
  needs to be matched edge-by-edge (Phase 1 audit).
- For the general subcubic-with-one-port case we have no off-the-shelf
  reference; this is a sub-task of Track B.

**Provisional reading:** as soon as Sub-lemma 1$'$ is in hand,
"a minimal counterexample is bridgeless" follows from Lemma 1 by the
standard argument:

  Suppose $G$ is a minimal counterexample with bridge $e = uv$. By
  Lemma 1, some side $(G_w, w) \in \{(G_u, u), (G_v, v)\}$ has no
  realisable trace in either of the two port states — contradicting
  Sub-lemma 1$'$. $\square$

## §3. Lemma 2 (target) — Essential 2-edge-cut reduction

The 2-edge-cut reduction is the first hard mountain. We frame it as a
trace-containment lemma over a finite table of port-state-pairs and then
identify the work to fill the table in.

### 3.1 Essential 2-edge-cuts

A **2-edge-cut** is a set of two edges whose removal disconnects $G$.
Call a 2-edge-cut $F = \{e_1, e_2\}$ **essential** if the four edge
endpoints are all distinct. If two of the endpoints coincide
($a_1 = a_2$ on the $A$-side, say), then $a_1$ has degree 1 in $G[A]$
and is incident to two boundary edges; in this case $G[A]$ contains
a bridge incident to $a_1$ (its single side edge), which Lemma 1 has
already handled inside the larger argument. The unique remaining case
to address as "2-edge-cut" is the essential one.

### 3.2 Two-pole sides

Let $F = \{e_1, e_2\}$ be an essential 2-edge-cut of $G$ with sides
$A, B$ and $e_i = a_i b_i$. Each side $(G[A], (a_1, a_2))$ and
$(G[B], (b_1, b_2))$ is a 2-pole rooted side with two ports of
port-degree 1 each.

By §1.2, each port has 5 possible states. So a port-state-pair on side
$A$ is in $\{T_T, T_{TM}, M_{TT}, T_{CC}, C_{TC}\}^2$ — 25 a priori
options. Tree-connectivity inside $A$ adds a binary refinement
("same tree component inside $A$?" / "different?") when both ports are
$T$-incident.

### 3.3 Edge-type pair table

Coding the boundary-edge colour pair
$(\mathrm{type}(e_1), \mathrm{type}(e_2)) \in \{T, C, M\}^2$, the
admissible port-state-pairs are:

| $(t(e_1), t(e_2))$ | port state at $a_1$ | port state at $a_2$ |
|---|---|---|
| $(T, T)$ | $\in \{T_T, T_{TM}, T_{CC}\}$ | $\in \{T_T, T_{TM}, T_{CC}\}$ |
| $(T, C)$ | $\in \{T_T, T_{TM}, T_{CC}\}$ | $= C_{TC}$ |
| $(T, M)$ | $\in \{T_T, T_{TM}, T_{CC}\}$ | $= M_{TT}$ |
| $(C, T)$ | $= C_{TC}$ | $\in \{T_T, T_{TM}, T_{CC}\}$ |
| $(C, C)$ | $= C_{TC}$ | $= C_{TC}$ |
| $(C, M)$ | $= C_{TC}$ | $= M_{TT}$ |
| $(M, T)$ | $= M_{TT}$ | $\in \{T_T, T_{TM}, T_{CC}\}$ |
| $(M, C)$ | $= M_{TT}$ | $= C_{TC}$ |
| $(M, M)$ | $= M_{TT}$ | $= M_{TT}$ |

Total port-state-pairs: $3 \cdot 3 + 3 \cdot 1 + 3 \cdot 1 + 1 \cdot 3 +
1 \cdot 1 + 1 \cdot 1 + 1 \cdot 3 + 1 \cdot 1 + 1 \cdot 1 = 25$. Each
contributes a binary tree-connectivity refinement when applicable, so
the trace-set $\mathrm{Trace}(H, R)$ lives in a space of $\le 50$
boolean entries.

Notes:

- $(M, M)$: requires both ports in $V_M$ via $M_{TT}$; the matching
  uses both cut edges. Valid because the four endpoints are distinct
  (essential cut).
- $(C, C)$: both ports in $V_C$ via $C_{TC}$. Since $C$ is 2-regular,
  the two boundary edges lie on the same cycle of $C$ in $G$; on each
  side, the cycle restricted to that side is a $C$-path between the
  two ports.
- $(T, T)$: most flexible — tree crosses the cut at both edges. The
  tree restriction inside each side must "compensate" so that
  $T_A \cup \{e_1, e_2\} \cup T_B$ is acyclic; this is exactly what the
  tree-connectivity partition $\pi$ tracks.

### 3.4 16-trace realisability theorem

A central Track B result, established by combining the n≤10 lattice
sweep ([scripts/gadget_lattice.py](../scripts/gadget_lattice.py),
[data/gadget_lattice_2pole_n10_both.json](../data/gadget_lattice_2pole_n10_both.json))
with the structural impossibility proofs in
[scripts/trace_feasibility.py](../scripts/trace_feasibility.py):

**Theorem (16-trace realisability).** For every connected 2-pole subcubic
graph $(H, R)$ (with at least one internal vertex), the trace set
$\mathrm{Trace}(H, R)$ is a subset of a fixed 16-element universe
$\mathcal{U} \subset \{(\chi, \pi)\}$. The remaining 18 of the 34
a-priori traces are provably impossible by three structural patterns:

(A) **C-cycle cannot close (8 traces).** If $\chi$ has exactly one
port in state $C_{TC}$, the global $C$-cycle through that port's
$C$-boundary edge enters $H$ via the port's $C$-side-edge and cannot
return: every "$C$-exit" of $H$ requires a port in $\{C_{TC}, T_{CC}\}$
with at least one $C$-side-edge whose corresponding boundary is also
$C$. With only one $C_{TC}$ port and no other $C$-boundary edges, the
cycle has nowhere to close.

(B) **No $T$-stub for internal vertices (6 traces).** If neither port
is in $\{T_T, T_{TM}\}$ — i.e. neither has both $T$-boundary AND
$\deg_{T_H} \ge 1$ — then no port contributes a usable $T$-stub to a
$T_H$-component containing an internal vertex. Internal vertices have
$\deg_{T,\text{global}} \ge 1$ (from the vertex-type identity), forcing
them into some $T_H$-component; without a reachable $T$-stub, that
component cannot glue into the global spanning tree.

(C) **$T_{CC}$ port placed in a shared block (4 traces).** Any
$T_{CC}$ port has $\deg_{T_H} = 0$ and is therefore isolated in $T_H$.
A boundary trace with a $\pi$-block of size $\ge 2$ containing such a
port claims the $T_{CC}$ port shares a $T_H$-component with another
port — contradiction.

The n≤10 lattice realises all 16 traces in $\mathcal{U}$; the unique
maximal class $C_{58}$ has $\mathrm{Trace}(C_{58}) = \mathcal{U}$.
$\square$

Consequence: **every 2-pole side's trace set is bounded inside the
16-element universe**. The realisable trace space is fully classified.

### 3.5 Trace-containment reduction (statement)

**Lemma 2 (target form).** Let $G$ be a connected cubic graph with an
essential 2-edge-cut $F = \{e_1, e_2\}$ and sides $A, B$. The trace-
containment reduction is:

  Find a 2-pole cubic gadget $A'$ with the same boundary as $G[A]$,
  $|V(A')| < |V(G[A])|$, AND $\mathrm{Trace}(A') \subseteq
  \mathrm{Trace}(G[A])$. Replace $G[A]$ by $A'$ in $G$ to get the
  strictly smaller cubic graph $G'$.

**Direction of inclusion.** $\mathrm{Trace}(A') \subseteq
\mathrm{Trace}(G[A])$ (the replacement has *fewer or equal* realised
traces than the side being replaced). Lifting: if $G'$ has a
3-decomposition with induced $(\sigma_{A'}, \sigma_B)$ traces, then
$\sigma_{A'} \in \mathrm{Trace}(A') \subseteq \mathrm{Trace}(G[A])$,
so $\sigma_{A'}$ as a trace on $G[A]$ is compatible with $\sigma_B$,
giving a 3-decomposition of $G$. Contrapositive: $G$ inheirts
non-decomposability from $G'$, contradicting minimality of $G$ (since
$G'$ would be a smaller counterexample).

Equivalent form: $G'$ decomposable $\Rightarrow$ $G$ decomposable.
Lifting: $\sigma_{A'} \in \mathrm{Trace}(A') \subseteq \mathrm{Trace}(G[A])$,
so $\sigma_{A'}$ as a trace on $G[A]$ is compatible with the same
$\sigma_B$, yielding a 3-decomposition of $G$.

**Implementation note.** `scripts/coverage_check.py` keeps both directions
separate: `check_coverage` tests the envelope inclusion
$\mathrm{Trace}(H) \subseteq \mathrm{Trace}(C)$, while
`find_replacement_gadget(H, ports, lattice)` tests the reduction direction
$\mathrm{Trace}(C) \subseteq \mathrm{Trace}(H)$ with a strict order
decrease.

**Lemma 2 sketch (using the 16-trace theorem and the lattice).** Let
$(H, R)$ be a 2-pole side with $|V(H)| > 10$. Then $\mathrm{Trace}(H)
\subseteq \mathcal{U}$ (16-trace theorem). For Lemma 2 to apply, we
need a gadget $A' \in \mathcal{L}$ with $|V(A')| < |V(H)|$ AND
$\mathrm{Trace}(A') \subseteq \mathrm{Trace}(H)$.

This is *not* automatic — it depends on the structure of the lattice.
Specifically, the n≤10 lattice contains gadgets at orders 4, 6, 8, 10
with varying trace sets. For a side whose trace set happens to be
small (say, a subset of $C_0$'s 3-trace set), only $C_0$ gadgets are
candidates, and they must be smaller than $|V(H)|$. The smallest
candidates ($n = 4$) work for any $|V(H)| > 4$.

The Lemma 2 closure question reduces to:

  **(Lemma 2 closure question.)** For every realisable trace set
  $T \subseteq \mathcal{U}$, does the lattice $\mathcal{L}$ contain a
  gadget $A'$ with $\mathrm{Trace}(A') \subseteq T$ and "small"
  $|V(A')|$?

The n≤10 lattice has 59 trace classes with these structural features:

- $\mathrm{Trace}(C_{58}) = \mathcal{U}$ (the maximal class realises
  every possible trace);
- the 7 minimal classes $\{C_0, C_2, C_3, C_4, C_5, C_6, C_7\}$ form a
  mutually-incomparable antichain in the inclusion Hasse poset;
- every one of the 59 lattice classes contains at least one minimal
  class's trace set as a subset;
- **the union $\bigcup_i \mathrm{Trace}(C_i)$ over the 7 minimal classes
  equals $\mathcal{U}$**.

The minimal classes have minimum orders $\{4, 10, 10, 10, 6, 8, 8\}$,
respectively. In particular $C_0$ contains a gadget of order $4$ (which
is $K_4$ minus an edge), and $C_5$ has gadgets at order $6$.

The conjecture we initially hoped would close Lemma 2 via pure
trace-containment:

  **(Antichain Coverage conjecture.)** For every realisable 2-pole
  trace subset $T \subseteq \mathcal{U}$ (at any side order $|V| \ge 4$),
  at least one of the 7 minimal lattice trace sets is a subset of $T$.

Status:
- **True for the 59 lattice classes** ($n \le 10$, by direct verification).
- **Conjecture for general $|V|$**: empirical test at $n = 12$ must use
  the replacement-direction sweep, not the envelope coverage sweep.

If the conjecture holds, then **every 2-pole side $(H, R)$ with
$|V(H)| > 10$ is reducible to a minimal-class gadget** (of order $\le
10$, in fact $\le 8$ for $C_0, C_5, C_6, C_7$). Combined with the
bridge reduction (Lemma 1), this would prove

  **Theorem.** A minimal counterexample $G^\star$ to the 3-Decomposition
  Conjecture is 3-edge-connected.

since $|V(G^\star)| \ge 30$ forces at least one side of any essential
2-edge-cut to have $|V| \ge 15 > 10$, hence reducible.

The hinge is the Antichain Coverage conjecture — a finite, computable
question about subsets of the 16-trace universe.

### 3.6 Antichain Coverage conjecture: refuted at $n = 12$

Empirical test
([data/replacement_sweep_n12.json](../data/replacement_sweep_n12.json),
[scripts/replacement_sweep.py](../scripts/replacement_sweep.py)):
swept all 835 connected 2-pole subcubic graphs on $n = 12$, both
orientations, against the n≤10 lattice.

**Result.** 10 of 1670 oriented sides are **not replaceable** by any
smaller-order lattice gadget. They fall into **5 distinct trace sets**:

| Failure set | $|V|$ | $|\mathrm{Trace}(H)|$ | Example graph6 | Occurrences |
|---:|---:|---:|---|---:|
| 1 | 12 | 4 | `K?AB?pa[CWP_` (ports 3, 7) | 2 |
| 2 | 12 | 7 | ``K?`@CQWSPKCo`` (ports 1, 3) | 1 |
| 3 | 12 | 7 | ``K?`@CQWSPKCo`` (ports 3, 1) | 1 |
| 4 | 12 | 9 | `K?ABAaKh@oGW` (ports 3, 4) | 4 |
| 5 | 12 | 12 | `K?AB?qQT@WWG` (ports 2, 4) | 2 |

So the Antichain Coverage conjecture is **false**: at $n = 12$ there are
sides whose trace sets contain none of the 7 minimal class trace sets.

**Common obstruction.** Four universe traces are missing from *every*
failure trace set:

1. $\chi = (T_T, T_T), \pi = \{\{0\}, \{1\}\}$;
2. $\chi = (T_{TM}, T_{TM}), \pi = \{\{0, 1\}\}$;
3. $\chi = (T_{CC}, T_{TM}), \pi = \{\{0\}, \{1\}\}$;
4. $\chi = (T_{TM}, T_{CC}), \pi = \{\{0\}, \{1\}\}$.

Every minimal lattice class contains at least one of these four traces;
that is the structural reason the antichain fails to cover the failure
sets.

**Interpretation for Lemma 2.** Lemma 2 cannot close from the n≤10
lattice alone. Two paths forward:

(i) **Extended lattice.** Build the lattice up to $n = 12$ (835 new
unoriented gadgets, ≈ 5 hours of compute), then re-run
`replacement_sweep` at $n = 14$ to test whether new failures appear.
The 5 failure trace classes themselves become new lattice classes; a
side with one of those trace sets at $n \ge 14$ becomes reducible to
the corresponding $n = 12$ gadget. The risk: $n = 14$ may produce new
failure trace sets not covered by the extended lattice.

Use checkpointed lattice generation; the long run should be resumable:

```bash
.venv/bin/python problems/3_decomposition_conjecture/scripts/gadget_lattice.py \
  --n-max 12 \
  --checkpoint problems/3_decomposition_conjecture/data/gadget_lattice_2pole_n12_both.jsonl \
  --output problems/3_decomposition_conjecture/data/gadget_lattice_2pole_n12_both.json \
  --progress-every 25
```

(ii) **Structural theorem.** Prove that any side missing one of the 4
common-obstruction traces has additional structure (e.g., a
distinguished edge cut, a 2-vertex-cut, a forced subgraph) that admits
a different reduction, bypassing the trace-containment route.

(i) is straightforward compute and remains useful scaffolding. The
structural classification below shows that (ii) is now the proof path:
after the bridge/minimal-side and 2-vertex-cut subreductions are written,
only one essentially 3-connected n=12 pattern remains.

The failure data is archived in
[data/replacement_sweep_n12.json](../data/replacement_sweep_n12.json);
the 10 not-replaceable oriented sides give an exact target for any
new reduction lemma.

### 3.7 Structural classification of the 10 not-replaceable sides

Direct connectivity analysis of each failure side (archived in
[data/failure_structural_classification_n12.json](../data/failure_structural_classification_n12.json))
gives a clean three-class split:

**Class I — bridge or articulation present (6 oriented, 2 unoriented).**

| Graph6 | Ports | $\kappa_v$ | $\kappa_e$ | Bridges | $|\mathrm{Trace}|$ |
|---|---|---:|---:|---|---:|
| `K?AB?pa[CWP_` | $(3, 7)$ | 1 | 1 | $(3,7), (3,9), (4,7)$ | 4 |
| ``K?`@CQWSPKCo`` | $(1, 3)$ | 1 | 1 | $(1,5), (1,9)$ | 7 |
| ``K?`@CQWSPKCo`` | $(3, 1)$ | 1 | 1 | $(1,5), (1,9)$ | 7 |

In every case the bridges are incident to a port. **Reduction hint:**
in any cubic graph $G$ containing such a side, each "internal" bridge
of the side that connects the two ports through different components
produces an alternative 2-edge-cut $\{e_1, e\}$ of $G$ (smaller side).
Picking the *smallest* essential 2-edge-cut of $G^\star$ rules out
this class by construction. Sides with internal bridges separating
both ports never appear as "smallest" cut sides.

**Class II — bridgeless, non-port-trivial 2-vertex-cut (2 oriented, 1 unoriented).**

| Graph6 | Ports | $\kappa_v$ | $\kappa_e$ | Non-port-trivial 2-cut | $|\mathrm{Trace}|$ |
|---|---|---:|---:|---|---:|
| `K?ABAaKh@oGW` | $(3, 4)$ | 2 | 2 | $\{2, 7\}$ | 9 |

The 2-vertex-cut $\{2, 7\}$ is "interior" — neither $2$ nor $7$ is a
neighbour of a port, so it isn't the port-isolating cut. **Reduction
hint:** apply a recursive 2-vertex-cut reduction inside the side
(splitting the side into two smaller 2-pole sides glued along the
2-cut), reducing the gadget order further. The 2-vertex-cut machinery
required is the same as the global 2-vertex-cut reduction for cubic
graphs (independent of Lemma 2).

**Class III — essentially 3-connected (2 oriented, 1 unoriented).**

The genuine residual for ordinary trace-containment.

| Graph6 | Ports | $\kappa_v$ | $\kappa_e$ | Properties | $|\mathrm{Trace}|$ |
|---|---|---:|---:|---|---:|
| `K?AB?qQT@WWG` | $(2, 4)$ | 2 | 2 | girth 5, non-planar, ports share neighbour 10 | 12 |

The only 2-vertex-cuts are the two port-trivial ones (neighbour sets
of the two ports). Edge connectivity 2 = essential 2-edge-cut-freeness
relative to "non-port" cuts. This is the *only* unoriented n=12 graph
that is essentially 3-connected and still fails trace-containment.

This graph realises 12 of the 16 universe traces, missing exactly the
four common-obstruction traces. There is no structural deficiency
(bridge / articulation / non-trivial 2-cut) to exploit; trace-
containment is genuinely insufficient here.

The alternative reduction is given in §3.12: this side is
compatibility-universal, so replacing it by the 10-vertex universal
gadget and using minimality gives a non-trace-containment lift.

The win from this classification: the n=12 failure set no longer asks
for a uniformly bounded gadget library. Class I is a minimal-side bridge
issue, Class II is a genuine 2-vertex-cut issue, and Class III is handled
by compatibility domination.

### 3.8 Work remaining for Lemma 2

The n≤10 lattice does not give a universal trace-containment replacement
theorem. The n=12 replacement sweep turns the remaining work into a
small number of concrete subreductions:

1. **Minimal-side bridge exclusion.** Lemma 3.9 proves that if an essential
   2-edge-cut side contains an internal bridge, then either the whole
   graph has a bridge (handled by Lemma 1 plus Sub-lemma 1$'$) or there is
   a smaller essential 2-edge-cut. This rules out Class I after choosing
   a minimal essential 2-edge-cut side, except for the port-to-port-only
   bridge residual, which does not occur in the n=12 failures.

2. **Compatibility replacement.** Lemma 3.13 absorbs all 5 distinct
   n=12 failure trace sets, including the Class-II graph with a
   non-port-trivial 2-vertex-cut. This means the 2-vertex-cut lemma is
   no longer needed to close the n=12 layer of Lemma 2.

3. **Class III residual.** Lemma 3.12 handles the single graph6 pattern
   `K?AB?qQT@WWG` with ports $(2,4)$ by compatibility domination rather
   than trace-containment. The 16-trace witness table is archived in
   [data/classIII_absorber_witnesses.json](../data/classIII_absorber_witnesses.json).

4. **Universal Replacement Conjecture.** The global 2-edge-cut theorem
   still needs the all-orders statement: every essential 2-edge-cut side
   of order at least 12 is either trace-contained by a smaller lattice
   class or compatibility-universal.

5. **Keep the extended lattice as evidence, not as the spine.** The
   checkpointed n≤12 build should finish, and the combined replacement
   sweep at $n=14$ should be run against it. New failures would become
   additional structural targets, not a reason to retreat to an unbounded
   gadget library proof.

### 3.9 Lemma — minimal essential 2-edge-cut side has no Case-1/Case-2b bridge

This is the formal version of the Class-I "harmless" claim in §3.7.

**Lemma 3.9.** Let $G$ be a connected cubic simple graph satisfying:
(a) $G$ has no bridge (Lemma 1 + Sub-lemma 1$'$);
(b) $G$ has at least one essential 2-edge-cut.

Choose an essential 2-edge-cut $F = \{e_1, e_2\}$ with sides $A, B$
($e_i = a_i b_i$, $a_i \in A$, $b_i \in B$) minimizing
$\min(|V(A)|, |V(B)|)$ over all essential 2-edge-cuts of $G$; let $A$
be the smaller side. Then for every bridge $e^* = (u, v)$ of $G[A]$,
**both endpoints of $e^*$ are ports**, i.e. $\{u, v\} = \{a_1, a_2\}$.

*Proof.* Let $e^* = (u, v)$ be a bridge of $G[A]$. Let $A_1, A_2$ be
the two components of $G[A] - e^*$, with $u \in A_1, v \in A_2$.

**Case 1: At least one of $A_1, A_2$ contains no port.** WLOG $A_2$
has no port. Then in $G$, the edges from $A_2$ to the rest of $G$ are
exactly the edges of $G[A]$ between $A_1$ and $A_2$ — which is just
$\{e^*\}$. So $e^*$ is a bridge of $G$. Contradicts (a).

**Case 2: Both $A_1, A_2$ contain a port.** WLOG $a_1 \in A_1$ and
$a_2 \in A_2$. The bridge endpoints $u, v$ are each in some component.

**Case 2a: $u \notin \{a_1\}$ and $v \notin \{a_2\}$.** Consider the
cut $\{e_1, e^*\}$ in $G$. Removing both: in $G[A] - e^*$, the
component $A_1$ is connected to $B$ only via $e_1$ (its only boundary
edge); removing $e_1$ disconnects $A_1$ from $B$ in $G - \{e_1, e^*\}$.
So $\{e_1, e^*\}$ is a 2-edge-cut with side $A_1$, and
$|V(A_1)| < |V(A)|$.

Essentiality of $\{e_1, e^*\}$: endpoints are $\{a_1, b_1, u, v\}$.
- $a_1 \ne b_1$ ($e_1$ not a loop).
- $a_1 \ne u$ (by Case 2a hypothesis).
- $a_1 \ne v$: $a_1 \in A_1, v \in A_2$, disjoint.
- $b_1 \ne u, v$: $b_1 \in B$, $u, v \in A$, disjoint.
- $u \ne v$ ($e^*$ not a loop).

All four distinct. So $\{e_1, e^*\}$ is essential. Contradicts
minimality of $F$ (smaller essential cut exists).

**Case 2b: Exactly one of $u, v$ is a port.** WLOG $u = a_1$ and
$v \ne a_2$. By the same argument, $\{e_2, e^*\}$ has side $A_2$ with
$|V(A_2)| < |V(A)|$, and is essential: endpoints
$\{a_2, b_2, a_1, v\}$, all distinct (using $v \ne a_2$, $v \ne a_1$,
$a_1 \ne a_2$ essential cut, $b_2 \in B$ disjoint).

Contradicts minimality. (Symmetric for $v = a_2$.)

**Remaining case: Both $u$ and $v$ are ports** ($u = a_1, v = a_2$).
This is the "port-to-port" bridge $e^* = (a_1, a_2)$. Neither
$\{e_1, e^*\}$ nor $\{e_2, e^*\}$ is essential (each shares an
endpoint), so they don't violate minimality of $F$ over essential
cuts.

In every Case (1, 2a, 2b) the lemma's conclusion holds. $\square$

### 3.10 Corollary — Class I rule-out

**Corollary 3.10.** Let $G$ be a smallest
counterexample to the 3-Decomposition Conjecture. Suppose $G$ has an
essential 2-edge-cut. Choose the cut minimizing the smaller side.
Then by Lemma 3.9, the smaller side $G[A]$ has no bridge other than
possibly the single port-to-port edge $(a_1, a_2)$.

Empirical check at $n = 12$: the Class-I failures are 6 oriented sides,
2 unoriented graphs, represented by the 3 oriented rows below. Every row
contains a *non*-port-to-port bridge:
- `K?AB?pa[CWP_` ports $(3, 7)$: bridges $\{(3,7), (3,9), (4,7)\}$.
  Bridge $(3, 9)$ is port-to-internal; removing it leaves
  $\{1, 2, 6, 8, 9\}$ as a port-free component → Case 1 → bridge of $G$.
- ``K?`@CQWSPKCo`` ports $(1, 3)$: bridges $\{(1, 5), (1, 9)\}$.
  $(1, 5)$ port-to-internal, Case 1. $(1, 9)$ also port-to-internal,
  Case 2b → smaller essential cut.

So Lemma 3.9 + bridgelessness rules out every Class-I failure at $n = 12$.
The unresolved "port-to-port only" residual sub-case is not realised
in the $n = 12$ data.

### 3.11 Class II — needed: cubic 2-vertex-cut boundary-trace lemma

For the single Class-II failure `K?ABAaKh@oGW` ports $(3, 4)$ with
non-port-trivial 2-vertex-cut $\{2, 7\}$: the planned reduction is a
formal "2-vertex-cut boundary-trace" lemma.

**Setup.** Let $G$ be a 3-edge-connected cubic graph with a
2-vertex-cut $\{x, y\}$. Then $G - \{x, y\}$ has $\ge 2$ components.
Each component, together with $x$ and $y$, is a "2-pole side with
3-pole boundary" — specifically: the cut vertices $x, y$ each have
some edges into each component of $G - \{x, y\}$.

This generalises the 2-pole framework: a side is now a subcubic graph
with two distinguished cut vertices (degree $\le 3$ on each side, but
the cut vertex's degree splits across sides).

**Status.** The lemma statement is on the agenda for §5 but not yet
written. The Class-II failure at $n = 12$ is concrete evidence that
this lemma is needed; it is independent of Lemma 2 and aligns with
standard 3-vertex-connectivity reductions in cubic graphs (Bachtler-
Heinrich §4 informally relies on similar splits).

### 3.12 Class III — attacking `K?AB?qQT@WWG` ports $(2, 4)$

The ordinary trace-containment residual. Reproducing the structural data:

- $|V| = 12$, $|E| = 17$.
- Both ports degree 2, neighbours: $N(2) = \{6, 10\}$, $N(4) = \{7, 10\}$.
- $\kappa_v = \kappa_e = 2$; only 2-cuts are port-trivial $\{6, 10\}$,
  $\{7, 10\}$.
- Girth $5$. Non-planar. Diameter $3$.
- $|\mathrm{Trace}(H, R)| = 12$. Missing from the universe: exactly the
  four common-obstruction traces
  $\{(T_T, T_T)\pi{=}\{\{0\},\{1\}\}, (T_{TM}, T_{TM})\pi{=}\{\{0,1\}\},
  (T_{CC}, T_{TM})\pi{=}\{\{0\},\{1\}\}, (T_{TM}, T_{CC})\pi{=}\{\{0\},\{1\}\}\}$.
- The two ports share exactly one neighbour (vertex 10); the only
  port-to-port path of length $\le 4$ is $2 \to 10 \to 4$.

**Working observations.**

1. The shared-neighbour vertex $10$ is a "bottleneck": vertex $10$ has
   degree $3$ with neighbours $\{2, 4, 5\}$ — the two ports and vertex
   $5$. So $\{6, 10\}$ and $\{7, 10\}$ are the only 2-cuts because
   $10$ is on every short port-to-port path.

2. The four missing traces all involve "split $T_H$ between two
   ports of opposite-ish types" or "joined $T_H$ between two V_M
   ports". The shared-neighbour bottleneck $10$ likely forces $T_H$
   to be either entirely through $10$ (joined) or not at all through
   $10$ (no path), creating the structural obstruction.

3. **Port-trivial 2-cuts don't propagate to $G$.** Direct computer
   check: in $H = $ `K?AB?qQT@WWG`, removing $\{6, 10\}$ isolates
   vertex 2 (port); removing $\{7, 10\}$ isolates vertex 4 (port).
   But in any cubic supergraph $G$ where $H$ is a 2-edge-cut side, the
   ports are connected to the rest of $G$ via the boundary edges
   $e_1, e_2$. So $\{6, 10\}$ is **not** a 2-vertex-cut of $G$
   (port 2 still reaches $B$ via $e_1$). The naive "inherit a cut
   from $H$" route does not work.

4. **Compatibility-universal side.** Direct trace-compatibility check
   ([scripts/classIII_absorber_check.py](../scripts/classIII_absorber_check.py),
   [data/classIII_absorber_witnesses.json](../data/classIII_absorber_witnesses.json)):
   for every trace $\tau$ in the 16-element universe $\mathcal U$, there
   exists a trace $\sigma \in \mathrm{Trace}(H)$ such that $\sigma$ and
   $\tau$ glue to a valid global boundary trace. Equivalently,
   $\mathrm{Compat}(\mathrm{Trace}(H)) = \mathcal U$.

   This is stronger than the previous "constrained $B$" guess. The
   latter had the quantifier pointed the wrong way: a minimal
   counterexample does not admit a 3-decomposition. What matters is
   whether every trace that can appear on the opposite side $B$ can be
   paired with some realised trace of $H$.

5. **Universal smaller gadget.** The n≤10 lattice contains a 10-vertex
   gadget in class $C_{58}$ with $\mathrm{Trace}(C_{58}) = \mathcal U$
   (for example graph6 ``I?B@t`gs?`` with ports $(4,5)$). Thus there is a
   smaller replacement $U_{10}$ that can realise every possible opposite
   side trace, although its trace set is not a subset of
   $\mathrm{Trace}(H)$ and therefore it is not a trace-containment
   replacement in Lemma 2's narrow sense.

**Lemma 3.12 (Class-III compatibility replacement).** Let $H$ be
`K?AB?qQT@WWG` with ports $(2,4)$ or $(4,2)$. Suppose a smallest
counterexample $G$ contains $H$ as one side of an essential 2-edge-cut,
with opposite side $B$. Replace $H$ by the 10-vertex universal gadget
$U_{10}$ with the same ordered boundary, producing a smaller connected
cubic graph $G'$.

By minimality of $G$, the graph $G'$ has a 3-decomposition. Restricting
that decomposition to $B$ gives a trace $\tau_B \in \mathrm{Trace}(B)$.
By the 16-trace theorem, $\tau_B \in \mathcal U$. By observation 4,
there is $\sigma_H \in \mathrm{Trace}(H)$ compatible with $\tau_B$.
Gluing $\sigma_H$ to the same $B$-side decomposition gives a
3-decomposition of $G$, contradiction.

Therefore the Class-III n=12 residual cannot occur in a smallest
counterexample. $\square$

This is a non-trace-containment reduction: the lifted trace on $H$ need
not equal the trace used by $U_{10}$ in $G'$. The proof uses the weaker
and more flexible domination condition

\[
  \mathrm{Compat}(\mathrm{Trace}(U_{10}))
  \subseteq
  \mathrm{Compat}(\mathrm{Trace}(H)),
\]

which holds here because $\mathrm{Trace}(U_{10}) = \mathcal U$ and
$H$ is compatible with every trace in $\mathcal U$.

**Concrete next steps.**

(a) Audit `are_2pole_traces_compatible` against the formal gluing
definition. The 16 witness traces for `K?AB?qQT@WWG` are already
archived in
[data/classIII_absorber_witnesses.json](../data/classIII_absorber_witnesses.json).

(b) Generalise the replacement criterion from trace-containment to
compatibility domination. This may shrink other residuals that look
non-reducible under $\mathrm{Trace}(A') \subseteq \mathrm{Trace}(A)$ but
are reducible after quantifying over the opposite side.

### 3.13 Compatibility domination closes the $n = 12$ layer

Lemma 3.12 generalises further than the Class-III residual. Direct
sweep ([scripts/compatibility_universality.py](../scripts/compatibility_universality.py),
[data/compatibility_universality_n10_lattice.json](../data/compatibility_universality_n10_lattice.json)):

- **All 5 failure trace sets at $n = 12$ (Classes I, II, III together)
  are compatibility-universal.**
- 43 of the 59 lattice classes are compatibility-universal. The
  smallest such class is $C_5$ with `min_order = 6` and 12 members
  (e.g., the smallest universal gadget $U_6$ has only 6 vertices).

So Lemma 3.12 generalises:

**Lemma 3.13 (Compatibility replacement).** Let $G$ be a smallest
counterexample to the 3-Decomposition Conjecture with an essential
2-edge-cut. Pick the cut to minimise the smaller side $A$ and let $B$
be the larger side. Suppose $\mathrm{Trace}(B)$ is
compatibility-universal (i.e., $\mathrm{Compat}(\mathrm{Trace}(B)) =
\mathcal{U}$). Choose a $U_6 \in C_5$ — a 6-vertex 2-pole cubic gadget
with $\mathrm{Trace}(U_6)$ also compatibility-universal — and replace
$B$ by $U_6$ in $G$, producing $G'$ on $|V_A| + 6$ vertices.

Since $|V(G)| \ge 30$ and $|V_A| \le |V_B|$, $|V_B| \ge 15 > 6$,
hence $G'$ is strictly smaller than $G$. By minimality of $G$, $G'$
admits a 3-decomposition $D'$. Restrict $D'$ to $A$: gives a trace
$\tau_A \in \mathrm{Trace}(A) \subseteq \mathcal{U}$. By compatibility-
universality of $\mathrm{Trace}(B)$, there is $\sigma_B \in
\mathrm{Trace}(B)$ compatible with $\tau_A$. Glue $\tau_A$ and
$\sigma_B$ along the boundary: this gives a 3-decomposition of $G$,
contradiction. $\square$

(Symmetric argument by replacing the smaller side $A$ if $|V_A| > 6$
and $A$ is compatibility-universal.)

**Combined n=12 layer closure.** For every essential 2-edge-cut side
$H$ at $|V(H)| = 12$, the computation verifies one of:

(a) $\mathrm{Trace}(H)$ is a superset of some smaller-order lattice
class's trace set (trace-containment route, Lemma 2 narrow form), OR

(b) $\mathrm{Trace}(H)$ is compatibility-universal (Lemma 3.13).

**Empirical verification at $n = 12$.** Of the 1670 oriented 2-pole
sides at $n = 12$: 1660 satisfy (a) (trace-contained in some n≤10
class); the remaining 10 (the failures) satisfy (b) (compatibility-
universal). Combined, **every** $n = 12$ side is reducible by one of the
two mechanisms.

This does **not** by itself prove Lemma 2 for all minimal
counterexamples. A minimal counterexample $G$ with $|V(G)| \ge 30$ and
an essential 2-edge-cut has at least one side with $|V| \ge 15 > 6$, but
that side need not have order 12. Lemma 2 follows only after the same
dichotomy is proved for all side orders that can occur on the large
side.

**Open conjecture (Universal Replacement Conjecture).** For every
essential 2-edge-cut side $H$ at every $|V(H)| \ge 12$, $H$ satisfies
(a) or (b) above.

**Empirical test plan.** Once the n≤12 lattice is built, run a
combined replacement-sweep at $n = 14$ (trace-containment against
n≤12 lattice + compatibility-universality check). If every $n = 14$
side passes (a) or (b), the conjecture holds at $n = 14$, and so on.
A failure at any $n$ would identify a new structural obstacle requiring
either lattice extension or a new reduction.

### 3.14 Structural characterisation of compatibility-universal traces

**Theorem 3.14.** A 2-pole trace set $T \subseteq \mathcal{U}$ is
compatibility-universal if and only if $T$ contains all four of the
following boundary-colour / tree-connectivity "axis" traces:

(i) some $(\chi, \pi)$ with boundary $(T, T)$ and $\pi = \{\{0, 1\}\}$
    (joined);

(ii) some $(\chi, \pi)$ with boundary $(T, T)$ and $\pi = \{\{0\}, \{1\}\}$
     (split);

(iii) some $(\chi, \pi)$ with boundary $(T, M)$ (i.e. port 0 in any of
      $T_T/T_{TM}/T_{CC}$, port 1 in $M_{TT}$);

(iv) some $(\chi, \pi)$ with boundary $(M, T)$ (symmetric).

*Proof.* For each $\tau \in \mathcal{U}$, the boundary colour
pair is in $\{(T,T), (T,M), (M,T)\}$ (the only realisable types after
the 16-trace theorem). For pi-compatibility:

- $(T, T)$ boundary $\tau$: $\pi_\tau$ is joined or split. The boundary
  graph is a tree iff $\pi_\sigma$ has the opposite type. So
  $\sigma$ with $(T, T)$ joined matches $\tau$ with $(T, T)$ split, and
  vice versa. Hence both axis (i) and axis (ii) are necessary; both
  also suffice when present.

- $(T, M)$ boundary $\tau$: only port 0 is $T$-incident on each side;
  $\pi$ is forced to be a single singleton block. Any $\sigma$ with
  matching boundary colours $(T, M)$ is pi-compatible (the boundary
  graph is a single edge — a tree). Hence axis (iii) suffices.

- Symmetrically, axis (iv) covers all $(M, T)$ $\tau$'s.

The converse is the same argument in reverse: if one of the four axes is
missing, choose the opposite trace in $\mathcal U$ with the same boundary
colour and opposite required $\pi$ (for $(T,T)$), or with the missing
single-$M$ boundary direction (for $(T,M)$ or $(M,T)$). No trace in $T$
can glue to it, so $T$ is not compatibility-universal. $\square$

*Regression check.* Direct check across all 59 lattice classes matches
Theorem 3.14 in every case (59/59 agreement between "all 4 axes present"
and "compatibility-universal"; see
[data/compatibility_universality_n10_lattice.json](../data/compatibility_universality_n10_lattice.json)).

**Corollary 3.15 (Equivalent side condition for compatibility-universality).**
A 2-pole side $(H, R)$ is compatibility-universal iff $H$ realises:
(i) at least one boundary-$(T,T)$ trace with $T_H$ joined across the two
ports; (ii) at least one boundary-$(T,T)$ trace with $T_H$ split; (iii)
at least one boundary-$(T,M)$ trace; (iv) at least one boundary-$(M,T)$
trace.

In port-state language, a $T$-boundary port may be in any of
$\{T_T,T_{TM},T_{CC}\}$, while an $M$-boundary port is $M_{TT}$. Thus the
$(T,T)$ axes are **not** the same as "both ports are $V_T$"; for example
the smallest universal class $C_5$ uses a split $(T_{TM},T_{TM})$ trace.

This refocuses the Universal Replacement Conjecture: the conjecture
holds for an $H$ if either $\mathrm{Trace}(H)$ is trace-contained, or
$H$ realises all four axis traces. The working all-orders conjecture is:
**every 2-pole subcubic graph on $|V| \ge 12$ vertices either is
trace-contained by a smaller lattice class or realises all four axis
traces**. This is the Universal Replacement Conjecture with
compatibility-universality replaced by the concrete four-axis condition.

### 3.16 Trace-count threshold and atomic universal trace sets

The n≤10 lattice also shows a sharp empirical trace-count threshold:

- every lattice class with $|\mathrm{Trace}| \ge 11$ is
  compatibility-universal;
- every non-universal lattice class has $|\mathrm{Trace}| \le 10$.

This is recorded in
[data/compatibility_universality_n10_lattice.json](../data/compatibility_universality_n10_lattice.json)
as `trace_count_threshold`. It is an empirical property of the realised
n≤10 lattice classes, not a theorem about arbitrary subsets of
$\mathcal U$: an arbitrary subset of the 16-trace universe could have
more than 10 traces while missing, say, the $(T,M)$ axis.

The theoretical minimum size of a compatibility-universal trace set is
4, since the four axes in Theorem 3.14 are independent. This minimum is
realised in two currently visible ways:

1. **Lattice class $C_4$** (minimum order 10) has four traces:
   $(M_{TT},T_T)$, $(T_T,M_{TT})$, $(T_T,T_T)$ joined, and
   $(T_T,T_T)$ split.
2. **The first n=12 failure trace set** (`K?AB?pa[CWP_` with ports
   $(3,7)$) has four traces:
   $(M_{TT},T_T)$, $(T_T,M_{TT})$, $(T_T,T_T)$ joined, and
   $(T_{TM},T_{TM})$ split.

Thus the n=12 failure #1 is an atomic universal trace set, but not the
unique atomic universal trace set. The correct invariant is "one trace
from each of the four axes", not the particular port-state choice inside
an axis.

### 3.17 Complete empirical n=14 sweep

**n≤12 lattice landed** (build complete; 1944 oriented gadgets, **133
trace classes** up from 59 at n≤10, unique maximal class `C132`, 9
minimal classes — including 2 new minimal classes `C22`, `C23`
introduced at n=12). The 5 n=12 failure trace sets are now first-class
lattice members.

**n=14 stratification of 7589 unoriented 2-pole subcubic graphs:**

| Structural class | Unoriented count |
|---|---:|
| Has bridge | 685 |
| Articulation, no bridge | 0 |
| Non-port-trivial 2-vertex-cut | 3344 |
| Essentially 3-connected (only port-trivial 2-cuts) | 3560 |

**Random sample sweep (size 30 unoriented = 60 oriented):**

- 60/60 trace-contained in the n≤12 lattice.
- 0 require compatibility-universal fallback.
- 0 break the Universal Replacement Conjecture.

The n≤12 lattice already absorbs every n=14 side encountered in a
random sample. A 60-sample misses failures with high probability if
the failure rate is ~0.1%, so this is encouraging but not decisive.

**Focused essentially-3-connected sample (60 unoriented, both orientations
= 120 sides):**

- 120/120 trace-contained in the n≤12 lattice.
- 0 require compatibility-universal fallback.
- 0 break the conjecture.

Archived in
[data/n14_essential3conn_sample_sweep.json](../data/n14_essential3conn_sample_sweep.json).
Even essentially-3-conn n=14 sides (the structural class where Class III
lived at n=12) are absorbed *via trace-containment alone*, without
needing the compatibility-universal fallback. The lattice "grows into"
larger orders smoothly.

**Combined n=14 evidence:** 90 unoriented sides (180 oriented) sampled,
all trace-contained, zero failures. Statistical confidence at the
n=12 essentially-3-conn failure rate (~0.14%) is still weak: 180
independent samples would have about a 78% chance of seeing zero failures
at that rate. The evidence is directionally good, not decisive.

**Decisive empirical step — full essentially-3-connected n=14 sweep
complete.** The full stratum has 3560 unoriented graphs, hence 7120
oriented sides. Results
([data/n14_essentially_3conn_full.summary.json](../data/n14_essentially_3conn_full.summary.json),
[data/n14_essentially_3conn_full.jsonl](../data/n14_essentially_3conn_full.jsonl)):

- 7120/7120 are trace-contained in the n≤12 lattice;
- 0 are compatibility-universal-only;
- 0 are neither.

Absorption histogram:

| Absorbing class | Count | Fraction |
|---|---:|---:|
| $C_0$ | 7106 | 99.80% |
| $C_2$ | 10 | 0.14% |
| $C_5$ | 4 | 0.06% |

All three absorbing classes are minimal classes of the n≤12 lattice.
The stable absorbing core for the essentially-3-connected n=14 stratum is
therefore tiny, and $C_0$ (the $K_4$-minus-edge 3-trace class) dominates.
Class ids here are ids in the n≤12 lattice; in particular this $C_5$ is
the n=12 atomic failure class, not the n≤10 class $C_5$ used earlier as
a 6-vertex compatibility-universal replacement.

The sweep used fast trace-containment records: trace counts and
compatibility-universality are not backfilled for every trace-contained
record, because containment was enough to certify the side. The
load-bearing rows (`neither` and `compat_universal_not_contained`) are
empty.

**Full all-structural-class n=14 sweep complete.** The sweep covers all
7589 unoriented graphs, both port orientations, hence 15178 oriented
sides. The complete JSONL archive is currently
[data/n14_essentially_3conn_full.jsonl](../data/n14_essentially_3conn_full.jsonl)
despite the historical filename; the compact summary is
[data/n14_full.summary.json](../data/n14_full.summary.json).

Status counts:

| Status | Count | Fraction |
|---|---:|---:|
| trace-contained | 15176 | 99.987% |
| compatibility-universal but not trace-contained | 2 | 0.013% |
| neither | 0 | 0% |

Structural distribution:

| Structural class | Oriented count |
|---|---:|
| bridge | 1370 |
| non-port-trivial 2-vertex-cut | 6688 |
| essentially 3-connected | 7120 |

The Universal Replacement Conjecture therefore survives the complete
n=14 sweep: every side is either trace-contained in the n≤12 lattice or
compatibility-universal, and there are no `neither` failures.

Absorption histogram for the 15176 trace-contained sides:

| Absorbing class | Count | Fraction of all oriented sides |
|---|---:|---:|
| $C_0$ | 10474 | 69.0% |
| $C_6$ | 3248 | 21.4% |
| $C_8$ | 768 | 5.1% |
| $C_7$ | 296 | 1.9% |
| $C_2$ | 124 | 0.8% |
| $C_3$ | 104 | 0.7% |
| $C_4$ | 104 | 0.7% |
| $C_5$ | 26 | 0.2% |
| $C_{22}$ | 26 | 0.2% |
| $C_{23}$ | 6 | <0.1% |

These ten n≤12 lattice classes are the absorbing core for the
trace-containment branch at n=14. They do **not** absorb literally every
n=14 side: the two compatibility-universal bridge orientations in §3.18
are explicit non-contained exceptions. The correct structural target is
therefore:

> Every relevant 2-pole side is either absorbed by one of
> $\{C_0,C_2,C_3,C_4,C_5,C_6,C_7,C_8,C_{22},C_{23}\}$, or is
> compatibility-universal, or is killed by an independent bridge/cut
> reduction.

**Don't jump to n=16 prematurely.** A small n=16 sample provides less
information than a complete n=14 sweep, because n=16 sides have many
more reducible substructures, and the conjecture failure modes (if
any) most likely reveal themselves at smaller orders.

**Defer the 2-vertex-cut boundary-trace lemma.** It's still needed
for the eventual 3-edge-connected ⇒ 3-vertex-connected upgrade, but
not for closing Lemma 2 itself. The compatibility-replacement
mechanism + extended lattice does that job at n=12, and the n=14
sweep tests whether it continues to.

### 3.18 The only n=14 compatibility-universal-only side

The complete n=14 sweep produced exactly two
`compat_universal_not_contained` records against the n≤12 lattice, namely
the two orientations of one bridge graph:

| graph6 | ports | structural class | $|\mathrm{Trace}|$ | trace-contained? | compatibility-universal? |
|---|---:|---|---:|---|---|
| ``M??CB?W`cKKGF?WG?`` | $(3,4)$ | bridge | 5 | no | yes |
| ``M??CB?W`cKKGF?WG?`` | $(4,3)$ | bridge | 5 | no | yes |

The trace set has all four axes from Theorem 3.14:

1. $(M_{TT},T_{TM}), \pi=\{\{1\}\}$;
2. $(T_{TM},M_{TT}), \pi=\{\{0\}\}$;
3. $(T_T,T_{TM}), \pi=\{\{0,1\}\}$;
4. $(T_{TM},T_T), \pi=\{\{0,1\}\}$;
5. $(T_{TM},T_{TM}), \pi=\{\{0\},\{1\}\}$.

So compatibility replacement is no longer merely an n=12 clean-up
device: pure trace-containment is already false at n=14, and Lemma 3.13
is empirically load-bearing.

This particular example is not a hard obstruction. With ports
$\{3,4\}$, the side has bridges $(5,12)$ and $(8,13)$. Removing
$(5,12)$ separates the zero-port component $\{0,5,6,9,10\}$; removing
$(8,13)$ separates the zero-port component $\{1,2,7,11,13\}$. Hence in
any bridgeless cubic supergraph, this is excluded by Lemma 3.9 Case 1:
the side bridge would be a bridge of the whole graph. The example is
therefore good evidence for the two-branch replacement dichotomy, but
not evidence of a new essentially-3-connected obstruction.

### 3.19 The 10-class absorbing core and its per-stratum signature

The full n=14 sweep (15178 oriented sides) absorbs into exactly 10
distinct lattice classes. Their breakdown by structural stratum reveals
that the absorbing core is **not uniform** — it depends on the side's
structural class. Per
[data/n14_absorbing_core.json](../data/n14_absorbing_core.json):

| Class | $|T|$ | min_order | n=14 absorbs | Axes covered |
|---|---:|---:|---:|---|
| $C_0$ | 3 | 4 | 10 474 | TT_join, TT_split (no M-axes) |
| $C_6$ | 5 | 6 | 3 248 | all 4 |
| $C_8$ | 5 | 8 | 768 | TT_join, TM, MT (no TT_split) |
| $C_7$ | 5 | 8 | 296 | TT_join, TT_split (no M-axes) |
| $C_2$ | 4 | 10 | 124 | all 4 |
| $C_3$ | 4 | 10 | 104 | TT_join, TT_split, MT |
| $C_4$ | 4 | 10 | 104 | TT_join, TT_split, TM |
| $C_{22}$ | 7 | 12 | 26 | all 4 |
| $C_5$ | 4 | 12 | 26 | all 4 |
| $C_{23}$ | 7 | 12 | 6 | all 4 |

(Class ids are local to the n≤12 lattice; do not confuse with n≤10
lattice ids.)

**Striking observation:** $C_0$ (which absorbs 69% of all n=14 sides)
is **not** compatibility-universal — it lacks M-boundary traces. The
sides it absorbs nevertheless contain its three traces $(T_{CC},T_T)$
split, $(T_T,T_{CC})$ split, $(T_{TM},T_{TM})$ joined. So absorption is
strictly weaker than compatibility-universality of the absorbing class.

**Per-stratum absorption signature.**

| Stratum | Records | Distinct absorbers | Dominant (≥1%) |
|---|---:|---:|---|
| `essentially_3conn` | 7 120 | **3** | $C_0$ 99.80%, $C_2$ 0.14%, $C_5$ 0.06% |
| `non_port_2cut` | 6 688 | 5 | $C_0$ 48.65%, $C_6$ 46.05%, $C_8$ 4.01%, $C_2$ 1.20% |
| `bridge` | 1 370 | 10 | $C_8$ 36.55%, $C_7$ 21.64%, $C_6$ 12.28%, $C_0$ 8.33%, $C_3, C_4$ 7.60% each, $C_2$ 2.49%, $C_5$ 1.61%, $C_{22}$ 1.46% |

The `essentially_3conn` stratum collapses to 3 absorbing classes; the
`non_port_2cut` stratum to 5; the `bridge` stratum spreads across all
10. This is structurally informative:

1. **essentially_3conn** is the cleanest. Every side contains $C_0$'s 3
   traces (or one of the 14 occurrences of $C_2/C_5$). The "default
   absorber" is $C_0 = K_4 - e$, the smallest possible 2-pole gadget.

2. **non_port_2cut** is dominated by the pair $\{C_0, C_6\}$ (95% of
   records). This is consistent with a recursive 2-vertex-cut
   structure: the side splits along the non-port-trivial 2-cut into
   pieces, each of which can be absorbed by a small core class.

3. **bridge** spreads across all 10. But every bridge side in a
   minimal counterexample is killable by Lemma 3.9 anyway (the side
   bridges become bridges of the whole graph, contradicting
   bridgelessness). So the bridge stratum's spread doesn't constrain
   the proof.

### 3.20 Core Absorption Lemma (target statement)

The data of §3.19 supports the following theorem-shaped formulation:

**Conjecture (Core Absorption Lemma, n≤14).** Let $G$ be a smallest
counterexample to the 3-Decomposition Conjecture and let $H$ be a
2-pole side of an essential 2-edge-cut of $G$ with $|V(H)| \le 14$.
Then at least one of the following holds:

(a) $H$ contains a bridge that is also a bridge of $G$ → contradiction
   with bridgelessness (Lemma 3.9 Case 1);

(b) $H$ contains a bridge giving a strictly smaller essential
   2-edge-cut of $G$ → contradiction with minimality (Lemma 3.9 Cases
   2a, 2b);

(c) $\mathrm{Trace}(H)$ contains the trace set of at least one of the
   10 core classes
   $\{C_0, C_2, C_3, C_4, C_5, C_6, C_7, C_8, C_{22}, C_{23}\}$ in the
   n≤12 lattice → trace-containment reduction;

(d) $\mathrm{Trace}(H)$ is compatibility-universal → Lemma 3.13
   reduction.

The empirical sweep at $n=14$ verifies that exactly one of (a)-(d)
applies to every 2-pole side: 15176 sides are covered by (c), 2 sides
by (a) (since the compat-only bridge's bridges are zero-port-cutting),
and 0 sides escape.

**Proof shape (open).** Each of (a)-(d) is a finite, structural
condition. Item (a) is Lemma 3.9 Case 1 (proved). Items (b) and (a)'s
sibling are Lemma 3.9 (proved). Item (c) is a finite collection of 10
trace-containment checks against fixed gadgets. Item (d) is a finite
axis-coverage check (Theorem 3.14).

To upgrade to a theorem, one of two routes is required:

(i) **Structural classification:** prove that the disjunction of
    (a)-(d) holds for every 2-pole side of any $|V|$, not just
    $|V| \le 14$. This would require characterising when a side fails
    all four conditions — and showing no such side exists.

(ii) **Stabilisation:** show that the 10-class core is **closed** in
     the sense that any side at $|V| > 14$ contains the trace set of
     some core class. (Even smaller: the 3-class set
     $\{C_0, C_2, C_5\}$ suffices for the essentially-3-connected
     stratum, and $\{C_0, C_6, C_8, C_2, C_{22}\}$ for the
     non-port-2cut stratum.)

A stabilisation theorem of the form "every essentially-3-connected
2-pole subcubic side at $|V| \ge 14$ realises $C_0$'s 3 traces" would
close the essentially-3-connected case structurally, leaving only the
non-port-2cut analysis (which connects to the 2-vertex-cut boundary-
trace lemma the proof needs anyway) and the bridge case (Lemma 3.9).

## §4. Target theorem

**Theorem (target; assumes Sub-lemma 1$'$ and Lemma 2).**
A minimal counterexample to the 3-Decomposition Conjecture is
3-edge-connected.

*Proof.* By §2.1, $G^\star$ is bridgeless. By Lemma 2 (§3.4),
$G^\star$ has no essential 2-edge-cut. By §3.1, non-essential 2-edge-cuts
contain a bridge in $G[A]$ for one side $A$, which by Lemma 1 (applied
to the bridged subcubic side) reduces $G^\star$ further. Combining,
$G^\star$ has no 2-edge-cut at all. $\square$

Once this theorem is established, every consequence in `plan.md`
currently flagged as "conditional on 3-vertex-connectivity" becomes
"conditional on 3-vertex-connectivity given 3-edge-connectivity",
which is the standard regime in which Bachtler–Heinrich's strong
reductions (girth, surface exclusion, tree-width) live.

The next mountain after this is the **2-vertex-cut reduction** —
upgrading 3-edge-connectivity to 3-vertex-connectivity. That argument
will reuse the trace-containment framework but with three boundary
half-edges per cut vertex, hence a 6-pole side; the analogous gadget
library is larger.

## §5. Immediate sub-tasks

1. **Subcubic existence sub-lemma (Sub-lemma 1$'$).** Read
   Aboomahigir–Ahanjideh–Akbari 2021 against the two port states
   $\{T_T, T_{TM}\}$; either cite directly or fill the gap. Write up in
   `docs/subcubic_existence.md`.
2. **Computer-checked Lemma 1.** Use
   `scripts/sublemma_bridge_sweep.py`, which enumerates 1-pole subcubic
   graphs and calls `verify_bridge_side_realisable(H, r)`. The checker
   searches spanning-tree-first, so the realised bridge trace really has
   $T_H$ a spanning tree of $H$. Current sanity range: all 1-pole
   subcubic graphs on $\le 11$ vertices.
3. **Trace-set computer.** `compute_trace_set_2pole(H, [r_1, r_2])` now
   computes full 2-pole traces, including the tree-connectivity partition
   $\pi$, by enumerating candidate $T_H$ forests first. Extend this to a
   SAT-based computation only once the forest-first search becomes the
   bottleneck.
4. **Minimal essential 2-edge-cut side lemma.** Prove that a smallest
   essential 2-edge-cut side is internally bridgeless after Lemma 1. This
   turns Class I of the n=12 failures into a non-obstruction.
5. **2-vertex-cut boundary trace lemma.** Still write the cubic 2-cut
   reduction, but its role has moved: compatibility replacement handles
   the n=12 Class-II failure; the 2-cut lemma is now mainly for the later
   global 3-vertex-connectedness upgrade.
6. **Class III witness audit.** The compatibility witnesses for
   Lemma 3.12 are archived; audit the checker against the formal gluing
   definition and, if desired, inline the 16-row table in an appendix.
7. **Compatibility-domination sweep.** `scripts/compatibility_universality.py`
   re-scores the n=12 failures; next extend the combined sweep to $n=14$
   once the n≤12 lattice build finishes.
8. **Extended lattice as regression data.** Let the checkpointed n≤12
   lattice finish, then run `replacement_sweep` at $n=14$ to see whether
   additional structural targets appear.
9. **Bachtler–Heinrich gadget extraction.** Read arXiv:2104.15113 and
   extract the implicit 2-pole gadget library used in their tree-width
   $\le 3$ / path-width $\le 4$ proofs. Encode into the same
   `data/known_templates.json` format as Track A.
10. **Open the formal proof.** Begin a Lean / Rocq sketch of Lemma 1
   once the natural-language proof above stabilises; this is a useful
   forcing function for spotting holes.

Current proof status: Lemma 1 and Lemma 3.9 are written as ordinary
natural-language proofs; Sub-lemma 1$'$ and the compatibility-replacement
claims rely on finite computer checks that should be converted into
auditable witness tables or cited structural lemmas. The n=12 layer of
Lemma 2 is closed. The full Lemma 2 remains open until the Universal
Replacement Conjecture is proved beyond $n=12$ and the port-to-port
bridge residual is disposed of or shown irrelevant.
