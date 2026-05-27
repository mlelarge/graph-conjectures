# D66: Refined width theorem, J+ diagnostics, and flex-only hardness target

## 1. Refined width theorem

The empirical conjecture
\[
\operatorname{pw}(J),\operatorname{tw}(J)=O(|H|)
\]
is now a theorem, with an explicit bound.

**Theorem 1.1.**  Let \(T\) be a tournament whose Path-FAS
score windows are Hall-feasible.  Let \(H\) be the forced-backedge
graph, \(G_{\rm flex}\) the score-window overlap graph, and
\[
J=H\cup G_{\rm flex}
\]
viewed as an undirected graph.  Then
\[
\operatorname{pw}(J)\le 8+2|H|,\qquad
\operatorname{tw}(J)\le 8+2|H|.
\]

Proof.  \(G_{\rm flex}\) is an interval graph.  Under Hall
feasibility, at most 9 score windows can contain any fixed position:
if they all contain \(p\), then they are all contained in
\([p-4,p+4]\), which has 9 integer positions.  Hence
\(\omega(G_{\rm flex})\le 9\).  The standard interval sweep gives a
path decomposition of \(G_{\rm flex}\) whose bags are the windows
active at each position, so \(\operatorname{pw}(G_{\rm flex})\le 8\).
The same bound also holds for treewidth.

Let \(S\) be the set of endpoints of edges of \(H\).  Starting with a
width-8 path decomposition of \(G_{\rm flex}\), add every vertex of
\(S\) to every bag.  This covers every edge of \(H\), and increases
bag size by at most \(|S|\le 2|H|\).  Therefore
\(\operatorname{pw}(J)\le 8+2|H|\), and treewidth is no larger.  ∎

This proof does **not** need \(H\) to be a linear forest.  The
linear-forest condition is needed by the LFO decision problem; the
width bound itself only uses Hall feasibility and the number of
forced-backedge arcs.

## 2. Consequence

Combined with the σ-on-bag DP of `J_pathwidth_dp.py`, the theorem
gives the promised bounded-\(|H|\) partial result:

> Path-FAS is fixed-parameter tractable parameterised by \(|H|\), and
> polynomial on every class with bounded \(|H|\).

The state function is still enormous because the DP must retain the
bag ordering σ; this is unavoidable by the n=12 collision documented
in `docs/J_pathwidth_dp.md`.

## 3. Directed interaction graph J+

D66 defines
\[
J^+
\]
as the directed graph containing:

* every forced backedge of \(H\), directed as a backedge;
* every flexible pair, directed by its tournament arc.

Implementation: `scripts/directed_interaction_graph.py`.

This is a diagnostic object, not yet a DP theorem.  It tests whether
directed information collapses the near-complete undirected minimal-NO
instances into a small directed-width object.

The first diagnostic is negative:

| catalogue | records checked | largest SCC | exact FVS histogram |
|---|---:|---:|---|
| n=7 minimal NO | 20 | 7 on all records | {1: 1, 2: 7, 3: 11, 4: 1} |
| n=8 minimal NO | 572 | 8 on all records | {2: 41, 3: 449, 4: 82} |
| n=9 minimal NO sample | 100 | 9 on all records | {2: 3, 3: 52, 4: 45} |

So J+ is strongly connected on the minimal-NO substrate.  Any directed
DP route cannot merely exploit acyclicity or small feedback vertex
number of J+; it needs a genuinely subtler directed-width parameter.

## 4. Flex-only hardness target

The wire route is dead because forced-path interiors are already
degree-saturated.  A hardness proof, if it exists along the observed
minimal-NO substrate, must be **flex-only**:

* \(H=\varnothing\) or negligible;
* Hall-feasible score windows;
* constraints carried by the tournament orientation on flexible pairs.

This is a much sharper target than generic SAT gadgetry.  In
particular, the variable signal cannot be transmitted by a forced
path; it has to be encoded by the relative order inside a dense
flexible bag.  The natural reductions to try next are therefore not
ordinary 3-SAT fanout reductions, but dense-ordering problems such as:

* Betweenness / cyclic ordering variants;
* feedback-arc constraints under a degree-2 backgraph budget;
* permutation CSPs where each constraint is a small tournament
  subtournament and the global certificate is the LFO order.

## 5. Updated status

| component | status after D66 |
|---|---|
| Constant-width J conjecture | refuted |
| Refined \(8+2|H|\) width bound | proved |
| Bounded-\(|H|\) partial algorithm | follows from width + σ-on-bag DP |
| J+ acyclic / small-FVS hope | refuted on minimal-NO catalogues |
| Wire hardness | blocked by interior saturation |
| Flex-only hardness | open, now the clean hardness target |
| General Aboulker Problem 4.4 | open |

## 6. D67 follow-up: forced-frontier compression test

The immediate post-D66 question was whether the \(2|H|\) endpoint term
in Theorem 1.1 is an artifact.  `scripts/forced_frontier_probe.py`
tests the most natural compression attempt: sweep the flexible
interval decomposition and keep only active windows plus two boundary
handles for each live forced-backedge component.

The result is negative in the simplest possible family.  In the
reversed-matching tournament on \(2m\) vertices, \(H\) is a matching
and at the middle sweep cut all \(m\) forced components are live.
The active score-window band has size 7, but the optimistic compressed
frontier has size \(7+2m\).

So a componentwise forced-frontier compression does **not** beat the
refined width theorem.  Any polynomial positive route has to quotient
many dormant forced components collectively, not merely summarize each
component by two endpoints.  See `docs/forced_frontier_probe.md`.
