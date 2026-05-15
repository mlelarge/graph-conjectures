# Autopsy of the 10-class absorbing core

For each of the 10 classes that absorb the 15178 oriented 2-pole sides
at n=14, this document records the structural data needed to convert
the absorption histogram into proof. Empirical counts are from
[data/n14_absorbing_core.json](../data/n14_absorbing_core.json); the
representative gadgets and trace sets are from
[data/gadget_lattice_2pole_n12_both.json](../data/gadget_lattice_2pole_n12_both.json).

## Overview

| Class | $|T|$ | min_order | Total | essentially_3conn | non_port_2cut | bridge | Compat-univ. | Axes missing |
|---|---:|---:|---:|---:|---:|---:|:---:|---|
| $C_0$ | 3 | 4 | 10474 | 7106 | 3254 | 114 | no | TM, MT |
| $C_6$ | 5 | 6 | 3248 | 0 | 3080 | 168 | **yes** | — |
| $C_8$ | 5 | 8 | 768 | 0 | 268 | 500 | no | TT_split |
| $C_7$ | 5 | 8 | 296 | 0 | 0 | 296 | no | TM, MT |
| $C_2$ | 4 | 10 | 124 | 10 | 80 | 34 | **yes** | — |
| $C_3$ | 4 | 10 | 104 | 0 | 0 | 104 | no | TM |
| $C_4$ | 4 | 10 | 104 | 0 | 0 | 104 | no | MT |
| $C_{22}$ | 7 | 12 | 26 | 0 | 6 | 20 | **yes** | — |
| $C_5$ | 4 | 12 | 26 | 4 | 0 | 22 | **yes** | — |
| $C_{23}$ | 7 | 12 | 6 | 0 | 0 | 6 | **yes** | — |

Five of the ten classes are compatibility-universal ($C_2, C_5, C_6,
C_{22}, C_{23}$); the other five ($C_0, C_3, C_4, C_7, C_8$) absorb
purely by trace containment without supplying full axis coverage on
their own. **$C_0$ dominates the essentially-3-connected stratum
despite not being compatibility-universal**, which is the central
clue.

## The dominant pair: $C_0$ and $C_6$

### $C_0$ — the diamond gadget ($K_4 - e$)

Representative: graph6 ``C^``, ports $(0, 1)$.

```
edges:  {(0,2), (0,3), (1,2), (1,3), (2,3)}
ports:  {0, 1}  (each degree 2)
non-port vertices: {2, 3}  (each degree 3)
```

This is $K_4$ minus the edge $(0, 1)$: a "diamond" of two triangles
sharing edge $(2, 3)$. The ports $\{0, 1\}$ are the two non-shared
vertices.

- **Connectivity:** $\kappa_v = \kappa_e = 2$ (the two port-trivial
  2-cuts $\{2, 3\} = N(0) = N(1)$ are the only 2-cuts; they coincide,
  which is special).
- **Girth:** 3. Planar. Not bipartite.
- **|T|:** 3.

**Trace set** (all 3 with $(T, T)$ boundary):

1. $(T_{CC}, T_T), \pi = \{\{0\}, \{1\}\}$.
   Port 0 is $V_C$ (side $(C, C)$); port 1 is $V_T$ (side $(T, T)$).
   $T_H$ has two components: $\{2, 3, 1\}$ (containing port 1) and
   the isolated singleton $\{0\}$.
2. $(T_T, T_{CC}), \pi = \{\{0\}, \{1\}\}$.
   Symmetric to (1).
3. $(T_{TM}, T_{TM}), \pi = \{\{0, 1\}\}$.
   Both ports are $V_M$ (side $(T, M)$); $T_H$ is a single spanning
   tree of $H$ with both ports as degree-1 leaves.

**Missing axes:** $(T, M)$ and $(M, T)$. $C_0$ realises no trace with
$M$-boundary at any port. Therefore $C_0$ is **not**
compatibility-universal; sides absorbed by $C_0$ realise $C_0$'s 3
traces but may also realise additional traces.

**n=14 absorption:** 10474 / 15178 = 69%.

- essentially_3conn: 7106 / 7120 = **99.80%**.
- non_port_2cut: 3254 / 6688 = 48.65%.
- bridge: 114 / 1370 = 8.33%.

**Structural interpretation.** The three $C_0$ traces correspond to
three "natural" partitions of any 2-pole subcubic side:

- *Cycle-bypass at port 0*: there is a $C$-cycle through port 0
  that uses both of port 0's side-edges. Equivalently, port 0's two
  neighbours are joined by a $C$-path in $H$ avoiding port 0 itself.
  This is realisable whenever the subgraph $H - \{\text{port 0}\}$
  has a Hamilton path or cycle covering the requisite vertices in
  the right colouring; in practice, $\kappa_v \ge 2$ supplies it.
- *Cycle-bypass at port 1*: symmetric.
- *Both ports matched, spanning $T_H$*: there is a spanning tree of
  $H$ where both ports are leaves. Such a tree exists in any
  2-edge-connected 2-pole subcubic graph with enough internal
  structure (a deletion argument suffices for $|V(H)| \ge 4$).

**Forcing lemma candidate (Lemma C₀):**

> Let $H$ be an essentially-3-connected 2-pole subcubic graph with
> $|V(H)| \ge 4$. Then $\mathrm{Trace}(C_0) \subseteq \mathrm{Trace}(H)$.

Empirical support at $n = 14$: 7106 / 7120 essentially-3-connected
sides satisfy this, with only 14 exceptions (absorbed by $C_2$ or
$C_5$ instead). The 14 exceptions are candidates for explicit
structural analysis (see §"Open: the 14 essentially-3-connected
exceptions" below).

A proof of Lemma C₀ would close the essentially-3-connected stratum
almost entirely, reducing the proof problem to bridges (Lemma 3.9),
non-port-2cuts (Lemma C₆ candidate below), and the 14 finite
exceptions plus their analogues at higher $n$.

### $C_6$ — the non-port-2cut workhorse

Representative: graph6 ``EUZO``, ports $(2, 4)$.

```
edges: {(0,2), (0,3), (0,5), (1,3), (1,4), (1,5), (2,4), (3,5)}
ports: {2, 4}  (each degree 2)
non-port vertices: {0, 1, 3, 5}  (each degree 3)
```

A 6-vertex graph with edge $(2, 4)$ between the two ports themselves,
plus structure connecting both to the 4-vertex "core" $\{0, 1, 3, 5\}$.

- **Connectivity:** $\kappa_v = \kappa_e = 2$.
- **Girth:** 3. Planar. Not bipartite.
- **|T|:** 5. **Compatibility-universal** (all 4 axes).

**Trace set:**

1. $(M_{TT}, T_T), \pi = \{\{1\}\}$ — $(M, T)$ axis.
2. $(T_T, M_{TT}), \pi = \{\{0\}\}$ — $(T, M)$ axis.
3. $(T_T, T_T), \pi = \{\{0, 1\}\}$ — $(T, T)$-joined axis.
4. $(T_{TM}, T_{TM}), \pi = \{\{0\}, \{1\}\}$ — $(T, T)$-split axis.
5. $(T_{TM}, T_{TM}), \pi = \{\{0, 1\}\}$ — extra $(T, T)$-joined trace.

**Missing:** 11 traces; notably $(T_{CC}, *)$ are absent. $C_6$ has
no $V_C$-port trace, distinguishing it from $C_0$.

**n=14 absorption:** 3248 / 15178 = 21%.

- essentially_3conn: 0 (!). $C_6$ never absorbs an essentially-3-conn
  side; those go to $C_0$ or its tiny rivals.
- non_port_2cut: **3080 / 6688 = 46.05%**.
- bridge: 168 / 1370 = 12.28%.

**Structural interpretation.** $C_6$'s defining traces include $V_M$
at both ports with the matching edge at the boundary — i.e., the
ports "communicate via the matching", not via the tree. This is the
natural absorption target for 2-pole sides with a non-port-trivial
2-vertex-cut: such a cut splits $H$ into pieces, and the
"matching-at-boundary" partition often suits the splitting pattern.

**Forcing lemma candidate (Lemma C₆ / non-port-2cut recursion):**

> Let $H$ be a 2-pole subcubic side with a non-port-trivial 2-vertex-cut.
> Then either $H$ recursively splits along that cut into smaller
> 2-pole pieces (each handled by induction), or $\mathrm{Trace}(C_6)
> \subseteq \mathrm{Trace}(H)$.

Empirical support: 3080/6688 of non_port_2cut n=14 sides realise $C_6$
directly, and 3254 realise $C_0$. The pair $\{C_0, C_6\}$ covers 95%
of the stratum. The structural reason: a non-port-trivial 2-vertex-cut
gives a "two-piece" picture where $C_0$ handles the $(T_T, T_T)$
+ $V_C$/$V_M$-port cases and $C_6$ handles the $M_{TT}$-port cases.

## The bridge-class absorbers

These five classes ($C_3, C_4, C_7, C_8, C_{23}$) absorb mostly bridge
graphs. Lemma 3.9 already rules bridge graphs out of any minimal
counterexample (a side bridge is either a bridge of $G$ or gives a
smaller essential 2-edge-cut). So these absorbers are
**not load-bearing for the proof** — they are book-keeping for the
bridge stratum that is killed structurally.

### $C_8$ — bridged 8-vertex gadget

Representative graph6 ``GCXe`W``, ports $(0, 3)$.

- Has bridge $(1, 6)$ and articulation points $\{1, 6\}$ (so $\kappa_v = 1$).
- |T| = 5; missing $(T, T)$-split. Not compat-universal.
- Absorbs 500 bridge n=14 sides (36.55% of stratum) plus 268 non_port_2cut.

### $C_7$ — bridged with $V_C$/$V_M$ port mix

Representative graph6 ``GCdbM_``, ports $(2, 4)$.

- Bridge $(1, 7)$, articulations $\{1, 7\}$; $\kappa_v = 1$.
- |T| = 5; misses M-axes. Not compat-universal.
- Absorbs **only bridge** sides at n=14: 296 / 1370 = 21.64%.

### $C_3$, $C_4$ — orientation pair at min_order 10

Same 10-vertex graph ``ICOce_kJ?`` with ports $(1, 6)$ and $(6, 1)$.

- 2 bridges, 3 articulations. $\kappa_v = 1$.
- |T| = 4. Each misses one M-axis (so individually not universal, but
  jointly the unordered pair covers everything).
- Absorbs 104 each, all bridge.

### $C_{23}$

Same 12-vertex graph as $C_{22}$ but with reversed ports.

- 2 bridges, 3 articulations. $\kappa_v = 1$. Compat-universal.
- Absorbs 6 bridge sides.

## The "rare" absorbers

These three classes — $C_2, C_{22}, C_5$ — are smaller but absorb
sides that the dominant $\{C_0, C_6\}$ pair miss.

### $C_2$ — pure-$V_T$ absorber at min_order 10

Representative graph6 ``I?`adQWP_``, ports $(2, 3)$.

- 10 vertices, $\kappa_v = \kappa_e = 2$ (no bridges, no articulations).
- |T| = 4. Compat-universal.
- Trace set is concentrated on $V_T$-port states:
  $(M_{TT}, T_T), (T_T, M_{TT}), (T_T, T_T)$-split and -joined.
- Absorbs 10 essentially-3-connected n=14 sides (the only non-$C_0$
  essentially-3-conn absorptions). Also 80 non_port_2cut and 34 bridge.

**Significance:** $C_2$ is the secondary absorber for essentially-3-
connected sides. The 10 essentially-3-conn n=14 sides absorbed by $C_2$
do NOT realise $C_0$'s traces but DO realise $C_2$'s 4 traces. These
are the structural exceptions to a Lemma C₀.

### $C_{22}$ — small bridged 12-vertex

Representative graph6 ``K?`@CQWSPKCo``, ports $(1, 3)$. The same
graph as $C_{23}$ with port order $(1, 3)$.

- 12 vertices with 2 bridges, $\kappa_v = 1$.
- |T| = 7 (the largest in the core). Compat-universal.
- Absorbs 26 sides (20 bridge + 6 non_port_2cut).

### $C_5$ — n=12 failure echo at min_order 12

Representative graph6 ``K?AB?pa[CWP_``, ports $(3, 7)$.

This is **exactly the n=12 failure trace set #1** from earlier
analysis (see [docs/minimal_counterexample.md §3.7](minimal_counterexample.md)).

- 12 vertices, 3 bridges, 4 articulations. $\kappa_v = 1$.
- |T| = 4. Compat-universal (atomic axis realisation).
- Absorbs 4 essentially-3-conn (!) + 22 bridge.

That $C_5$ absorbs 4 essentially-3-connected n=14 sides is interesting:
those sides realise the same 4-trace pattern as the n=12 failure side,
which is itself a bridge graph. Worth a closer look.

## Open: the 14 essentially-3-connected exceptions

Among the 7120 essentially-3-connected n=14 oriented sides:

- 7106 absorbed by $C_0$;
- 10 absorbed by $C_2$ (5 unoriented graphs × 2 orientations);
- 4 absorbed by $C_5$ (2 unoriented graphs × 2 orientations).

These 14 sides are the **only obstructions to Lemma C₀**. Each is an
explicit graph6 we can study. Possible structural patterns:

- the 4 $C_5$-absorbed sides may share the "atomic 4-trace" pattern
  identifying them as descendants of the n=12 failure structure;
- the 10 $C_2$-absorbed sides may share a "pure-$V_T$" obstruction
  (cannot realise $V_C$ port states for either port).

Extracting their graph6 strings and inspecting them is the next step
for sharpening Lemma C₀.

## Synthesis: what to prove next

The 10-class core decomposes by load-bearing role:

| Role | Classes | Used for |
|---|---|---|
| Essentially-3-conn workhorse | $C_0$ (+ $C_2, C_5$ for 14 exceptions) | Lemma C₀ |
| Non-port-2cut workhorse | $C_0, C_6$ (+ $C_8, C_2, C_{22}$) | Lemma C₆ / 2-cut recursion |
| Bridge-class book-keeping | $C_3, C_4, C_7, C_8, C_{22}, C_{23}$ | Subsumed by Lemma 3.9 |

The proof spine is:

- **Lemma A** (proved): bridge → either bridge of $G$ (contradicting
  bridgelessness) or smaller essential 2-edge-cut (contradicting
  minimality). — Lemma 3.9.
- **Lemma B** (target): non-port-trivial 2-vertex-cut → recursive
  split, or $C_6$ trace-containment.
- **Lemma C** (target): essentially-3-connected at $|V| \ge 4$ →
  $\mathrm{Trace}(C_0) \subseteq \mathrm{Trace}(H)$.
- **Lemma D** (proved as Lemma 3.13): compatibility-universal →
  replacement via the universal gadget.

Together, A ∨ B ∨ C ∨ D covers every 2-pole side that can appear in
a minimal essential 2-edge-cut of a counterexample.

The single hardest unknown is the strength of Lemma C: how does one
prove that essentially-3-connected 2-poles always contain the diamond
trace set?
