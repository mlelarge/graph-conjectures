# Research plan: CDC- and gadget-based $S^2$-flow construction

Pivot away from the finite frontier (frozen at $n \le 28$) and from
pure rotation symmetry on the flower family (closed; both ansätze
ruled out — [flower_snarks.md](flower_snarks.md)). The remaining
plausible route to an infinite-family theorem is constructive: build
$S^2$-flows from cycle double covers and graph operations that
preserve $S^2$-flow existence.

## Background

Let $G$ be a bridgeless graph. A *cycle double cover* (CDC) of $G$ is
a multiset $\mathcal{C}$ of cycles such that each edge lies in
exactly two members of $\mathcal{C}$. An *oriented* CDC chooses a
direction on each cycle, and an *oriented $k$-CDC* requires that
$|\mathcal{C}| \le k$ or that the cycles are coloured with $k$
classes (definitions vary by author).

Three published facts pin our starting point.

1. **Tutte $\Rightarrow$ Petersen $\Rightarrow$ Jain.** A bridgeless
   graph has a nowhere-zero 4-flow iff it has three $\mathbb{Z}_2$-flows
   whose supports cover every edge twice (a $\{0,1\}$-edge-coloured CDC
   in disguise). Combining the three $\mathbb{Z}_2$-flows as the three
   coordinates of a unit vector gives an $S^2$-flow on any graph with
   chromatic index 3 (Petersen / Tutte). So $\chi'(G) = 3 \Rightarrow$
   $G$ admits an $S^2$-flow.
2. **Mattiolo–Mazzuoccolo–Rajnik–Tabarelli 2025**
   (arXiv:2510.19411): if $G$ has an oriented $d$-CDC, then $G$ admits
   an $S^{d-2}$-flow constructed *geometrically* from the CDC. For
   $d = 4$ this is exactly an $S^2$-flow. Their construction is a
   piecewise-linear "fan" on each cycle, scaled and signed so that
   the cycle's contribution at each vertex is a unit vector and the
   sum at the vertex is zero.
3. **CDC conjecture.** Every bridgeless graph admits a CDC (Szekeres
   / Seymour). For snarks this is a known-hard open problem; for
   *flow-admitting* snarks an oriented 5-CDC suffices to imply
   $\chi'(G) = 4 \Rightarrow$ $G$ has an oriented 4-CDC + extra
   structure that the 2025 paper exploits.

## Working theorem to attack

> *Working target.* Let $G$ be a snark admitting an oriented
> 4-cycle-double-cover. Then $G$ admits an $S^2$-flow.

This is a special case of the Mattiolo et al. (2025) result; what we
add is **an explicit, machine-checkable construction algorithm**.

A successful proof gives:

- a constructive $S^2$-flow on any snark with an oriented 4-CDC
  (this includes Petersen, the Blanušas, all flower snarks via
  their known CDCs, and presumably all 3 247 graphs we already
  certified);
- a structural witness — a 4-CDC plus a per-cycle parameter — that
  can be stored, replayed, and refined;
- a framework for *infinite-family* statements such as "all flower
  snarks admit an $S^2$-flow", "all Goldberg snarks admit an
  $S^2$-flow", etc., by exhibiting a CDC family.

## Phase 0 — Validate the equivalence on our certified frontier

Before any new construction, lift CDCs from the 3 247 already-certified
graphs and check the implied $S^2$-flow agrees with the Krawczyk
witness up to gauge.

Concrete tasks:

1. Implement `cdc.py` with a function `find_oriented_cdc(G, k_max=5)`
   that returns an oriented CDC of size at most $k_{\max}$, or
   `None`. Brute search on $k=4$ via backtracking over compatible
   cycle pairs at each edge — feasible up to $n \le 28$.
2. For each $G$ in the 3 247 frontier, find an oriented 4-CDC and
   build the Mattiolo–Mazzuoccolo–Rajnik–Tabarelli geometric flow.
   Verify Kirchhoff at every vertex; cross-check the gauge against
   the stored Krawczyk witness.
3. Tabulate coverage: which graphs have a 4-CDC? a 5-CDC? Any with no
   CDC found within $k_{\max} = 6$?

Deliverable: `data/cdc_certificates/` with one JSON per graph,
containing the CDC cycles and the per-cycle parameters that realise
the $S^2$-flow.

## Phase 1 — Flower snarks $J_{2k+1}$

Flower snarks have a well-known oriented 4-CDC:

- $n = 2k+1$ "spoke fans" (each cycle of length 4 around an internal
  $a_i b_i c_i d_i a_i$),
- one "$b$-cycle" of length $2k+1$,
- one "cd-cycle" of length $2(2k+1)$ alternating $c$ and $d$ around
  the snark.

Total $|\mathcal{C}| = 2k+3$, every edge covered twice. Orient each
cycle consistently with the $\sigma$-symmetry from
[flower_snarks.md](flower_snarks.md).

Concrete tasks:

1. Write this CDC down explicitly as a function of $k$.
2. Apply the Mattiolo et al. (2025) construction parametrically in
   $k$. The construction is local at each vertex, so the resulting
   per-edge unit vectors are an explicit polynomial-trigonometric
   function of $k$.
3. Verify Kirchhoff symbolically (sympy) at the four orbit types
   $a_i, b_i, c_i, d_i$. If it holds, the construction is a *single
   formula* covering the entire infinite family.

Deliverable: `docs/flower_snarks_cdc.md` with the explicit closed-form
$S^2$-flow + symbolic Kirchhoff check + the resulting theorem.

## Phase 2 — Gadget composition

Cubic-graph operations that preserve $S^2$-flow existence:

1. **Triangle blow-up.** Houdrouge–Miraftab–Morin (2026) prove the
   cubic $S^2$-flow class is closed under blowing a vertex up into a
   triangle. Catalogue this; many large snarks are obtained from
   smaller ones by triangle blow-up.
2. **Dot product (Y-Y).** Combine two cubic graphs $G_1, G_2$ at a
   $K_4$-minor: remove a vertex from each, identify the three
   resulting half-edges in a compatible 3-edge cut. If both pieces
   have an $S^2$-flow on their respective subgraphs, the combined
   graph does too — *provided* the boundary half-edges receive
   compatible unit vectors. Track the "boundary triple" as part of
   the flow data and chain compositions.
3. **Splice / 4-cut surgery.** Generalisation of dot product to
   4-edge cuts: replace one side with another piece that carries the
   same boundary flow.
4. **Subdivision under 4-flow inheritance.** Subdividing any edge of
   a 4-flow graph gives a 4-flow graph; combined with the standard
   3-flow-to-$S^2$-flow lift, this lets us reach many bridgeless
   non-snarks. (Not the main target, but a stress-test for the
   composition machinery.)

For each operation, the deliverable is a small module:

- `gadgets/triangle_blowup.py` — input $G$ + vertex $v$ + interior
  flow; output the blown-up $G' + $ derived flow.
- `gadgets/dot_product.py` — input $(G_1, M_1, f_1), (G_2, M_2, f_2)$
  where $M_i$ is a matching of size 3 marking the dot-product
  interface and $f_i$ is the boundary triple; output the spliced
  graph and the derived global flow.

## Phase 3 — Infinite-family targets

Once Phase 1–2 land, the natural infinite-family targets are:

- *Theorem.* For every odd $n \geq 5$, the flower snark $J_n$
  admits an explicit $S^2$-flow given by the CDC construction
  of Phase 1.
- *Theorem.* Every Goldberg snark $G_{2k+1}$ admits an $S^2$-flow.
  (Goldberg snarks are also built from a uniform CDC; same argument
  pattern as flower snarks.)
- *Theorem.* The class of cubic graphs admitting an $S^2$-flow is
  closed under triangle blow-up and 3-edge-cut dot product
  (composition of HMM 2026 + explicit boundary calculus).

The serious target — Jain's full conjecture — would require either
the full CDC conjecture for bridgeless graphs (open) or a different
construction route entirely. Phase 3 is the natural ceiling without
that.

## What to *not* do

- More finite enumeration. The pipeline is fast enough to push to
  $n = 30$ with snarkhunter, but the result would be a longer
  certificate list, not a new theorem.
- More equivariant ansätze on the flower snarks beyond what
  [flower_snarks.md](flower_snarks.md) records as ruled out.
- Build a generic CDC enumerator (the 4-CDC conjecture is hard for
  arbitrary snarks; we only need *specific* families above).

## Risks and likely failure modes

1. **Phase 0 reveals a snark in the frontier with no 4-CDC.** Then
   Mattiolo et al.'s construction doesn't apply directly; we'd need
   the 5-CDC variant, and the geometric step gets messier (the
   2025 paper does $S^3$-flows from 5-CDC, not $S^2$). Plan B: use
   a 4-CDC where possible, fall back to a different geometric
   reduction for the residue.
2. **Phase 1 doesn't symbolically close.** The flower-snark CDC
   gives a finite parametric system; if its Kirchhoff residual is
   non-zero symbolically, the construction is locally consistent
   but globally inconsistent (boundary mismatch between cycles).
   That would be an interesting *new* obstruction to record, not a
   dead end.
3. **Phase 2 dot-product algebra blows up.** Boundary-triple
   tracking is well-defined but conditions for compatibility get
   long. Likely tractable for cubic boundaries (3 free
   directions); messier for higher-degree boundary structures.

## Estimated effort

- Phase 0: 1–2 weeks. Mostly engineering: CDC enumerator + applying
  the 2025 construction + cross-checking against stored witnesses.
  Most of the value is in *catching* whether the certified frontier
  is uniformly covered by 4-CDCs.
- Phase 1: 1–2 weeks if the symbolic Kirchhoff check closes; longer
  if Risk 2 fires.
- Phase 2: 2–4 weeks for both triangle blow-up and dot product.
- Phase 3: bounded by the above; once Phase 1 lands, a flower-snark
  theorem is a writeup task; Goldberg snarks similar.

Total: low single-digit months for a meaningful infinite-family
result, dominated by Phase 0 + Phase 1.

## Immediate first action

Implement `find_oriented_cdc(G, k_max=4)` and run it on the 3 247
certified graphs. If $\ge 99\%$ have a 4-CDC, Phases 1–2 are on a
solid foundation. If a substantial fraction lack a 4-CDC, the working
theorem in §"Working theorem" is the strictly weaker statement and
the immediate task shifts to characterising the residue.
