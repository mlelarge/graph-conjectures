# Research plan: CDC- and gadget-based $S^2$-flow construction

Pivot away from the finite frontier (frozen at $n \le 28$) and from
pure rotation symmetry on the flower family (closed; both ansatzes
ruled out -- [flower_snarks.md](flower_snarks.md)). The remaining
plausible route to an infinite-family theorem is constructive: build
$S^2$-flows from cycle-cover-like certificates and graph operations
that preserve $S^2$-flow existence.

This file is deliberately more skeptical than the first draft. The
plain oriented-4-CDC route is a trap: it gives $S^2$-flows, but in the
cubic setting it also gives nowhere-zero 4-flows, so it cannot explain
snarks.

## Background

Let $G$ be a bridgeless graph. A *cycle double cover* (CDC) of $G$ is
a multiset $\mathcal{C}$ of cycles such that each edge lies in exactly
two members of $\mathcal{C}$. Following
Mattiolo--Mazzuoccolo--Rajnik--Tabarelli (MMRT, 2025), an *oriented*
$d$-CDC is a collection of exactly $d$ directed cycles such that every
edge is covered twice and the two covering cycles traverse it in
opposite directions.

Three facts matter.

1. **4-flow positives.** A cubic graph with a nowhere-zero 4-flow has
   an $S^2$-flow by the standard three-coordinate lift from
   $\mathbb{Z}_2^2$. Thus ordinary 3-edge-colourable cubic graphs are
   already settled.

2. **MMRT Theorem 4.** A graph admits an oriented $d$-CDC if and only
   if it admits an $H_d$-flow, where
   $$
   H_d=\{e_i-e_j: i\ne j,\ 1\le i,j\le d\}\subset\mathbb{R}^d.
   $$
   Since $H_d$ lies in
   $$
   \Sigma_d=\{x\in\mathbb{R}^d:\sum_i x_i=0,\ \sum_i x_i^2=2\},
   $$
   and $\Sigma_d$ is a scaled copy of $S^{d-2}$, an oriented $d$-CDC
   gives an $S^{d-2}$-flow. For $d=4$ this gives an $S^2$-flow.

3. **Fatal caveat for snarks.** In a cubic graph, an $H_4$-flow
   induces a nowhere-zero $\mathbb{Z}_2^2$-flow. Identify the four
   coordinates with the four elements of $\mathbb{Z}_2^2$ and map
   $e_i-e_j$ to $i+j$. At a cubic vertex, three $H_4$ values sum to
   zero only as a directed triangle of coordinate labels, so the
   induced $\mathbb{Z}_2^2$ values are nonzero and sum to zero. Hence
   an oriented 4-CDC on a cubic graph implies a nowhere-zero 4-flow.
   A snark therefore cannot have an oriented 4-CDC. MMRT explicitly
   notes this phenomenon for the Petersen graph: it has an $S^2$-flow
   but no oriented 4-CDC.

## Rejected working theorem

The first draft target was:

> If $G$ is a snark admitting an oriented 4-cycle-double-cover, then
> $G$ admits an $S^2$-flow.

This is formally true, but vacuous for snarks. The hypothesis already
forces a nowhere-zero 4-flow in the cubic case.

## Corrected target

> Find a certificate strictly more general than an oriented 4-CDC that
> constructs a $\Sigma_4$-flow, equivalently an $S^2$-flow, on snarks
> without forcing a nowhere-zero 4-flow.

The certificate should be:

- structural enough to support infinite-family proofs;
- machine-checkable, ideally JSON-replayable like the interval
  certificates;
- capable of explaining Petersen, the Blanusa snarks, and flower
  snarks before we trust it on larger families.

## Phase 0 -- Negative calibration for oriented 4-CDCs

Before building new CDC machinery, make the false route fail loudly.

Concrete tasks:

1. Implement `cdc.py` with:
   - `h4_flow_to_z2x2_flow(...)`;
   - `oriented_4cdc_implies_nz4_flow(G, cert)`;
   - a tiny oriented-4-CDC checker for very small cubic graphs.
2. Regression tests:
   - 3-edge-colourable cubic graphs should admit $H_4$ / oriented
     4-CDC certificates;
   - Petersen and the Blanusa snarks should not.
3. Write `docs/cdc_negative_calibration.md`, proving in prose and by
   regression that oriented 4-CDCs are the wrong object for snarks.

Deliverable: a negative calibration document and tests. This is the
guardrail for every later CDC experiment.

## Phase 1 -- Weighted / geometric CDC certificates

The object we actually need is a continuous relaxation of the $H_4$
construction.

A useful ansatz:

1. choose a small CDC $\mathcal{C}=\{C_1,\ldots,C_t\}$;
2. assign each cycle a vector or weight parameter;
3. for each edge, add the signed contributions of its two covering
   cycles;
4. require every resulting edge vector to lie in $\Sigma_4$.

When the cycle parameters are coordinate basis vectors and the two
covering orientations are opposite on every edge, this collapses to
the discrete $H_4$ / oriented-4-CDC construction. The point is to allow
continuous parameters so that snarks are no longer excluded.

Concrete tasks:

1. Enumerate small CDCs for Petersen and the two Blanusa snarks.
2. For each CDC, solve the induced continuous system for $\Sigma_4$
   edge vectors.
3. Verify the resulting flow directly with the existing
   `witness.verify_witness` logic after projecting $\Sigma_4$ to
   $\mathbb{R}^3$.
4. Compare any successful CDC-derived flow against the stored
   interval-certified witness.

Deliverable: `scripts/cdc_weighted.py` and
`docs/weighted_cdc_certificates.md`.

## Phase 2 -- Flower snarks $J_{2k+1}$

The flower-snark task is no longer "write down an oriented 4-CDC";
that cannot exist. The correct target is a uniform weighted/geometric
CDC or gadget certificate.

Concrete tasks:

1. Write known CDCs of $J_{2k+1}$ explicitly as functions of $k$.
2. Feed those CDCs into the weighted-certificate solver from Phase 1.
3. If a pattern appears, verify Kirchhoff symbolically at the four
   vertex types $a_i,b_i,c_i,d_i$.

Deliverable: `docs/flower_snarks_cdc.md` with either:

- an explicit closed-form $S^2$-flow for all flower snarks; or
- a sharp negative statement saying the tested CDC template cannot
  realise a $\Sigma_4$-flow.

## Phase 3 -- Gadget composition

Cubic-graph operations that preserve $S^2$-flow existence:

1. **Triangle blow-up.** Houdrouge--Miraftab--Morin (2026) prove the
   cubic $S^2$-flow class is closed under blowing a vertex up into a
   triangle. Catalogue this; many large snarks are obtained from
   smaller ones by triangle blow-up.
2. **Dot product (Y-Y).** Combine two cubic graphs $G_1, G_2$ at a
   3-edge interface. If both pieces have $S^2$-flows with compatible
   boundary triples, the combined graph should inherit an $S^2$-flow.
   Track the boundary triple as part of the certificate.
3. **Splice / 4-cut surgery.** Generalise dot product to 4-edge cuts:
   replace one side with another piece carrying the same boundary flow.

For each operation, the deliverable is a small module:

- `gadgets/triangle_blowup.py`;
- `gadgets/dot_product.py`;
- `gadgets/splice4.py`.

## Phase 4 -- Infinite-family targets

Once Phase 1--3 land, the natural infinite-family targets are:

- *Theorem.* For every odd $n \geq 5$, the flower snark $J_n$ admits
  an explicit $S^2$-flow given by a weighted CDC or gadget
  construction.
- *Theorem.* Every Goldberg snark $G_{2k+1}$ admits an $S^2$-flow.
- *Theorem.* The class of cubic graphs admitting an $S^2$-flow is
  closed under triangle blow-up and compatible dot product.

The serious target -- Jain's full conjecture -- would require either
the full CDC conjecture plus a genuinely stronger geometric bridge to
$\Sigma_4$, or a different construction route entirely.

## What to not do

- More finite enumeration. The theorem through $n\le 28$ is already a
  strong finite artifact; pushing the list longer is not a new idea.
- More pure equivariant ansatzes on flower snarks beyond what
  [flower_snarks.md](flower_snarks.md) records as ruled out.
- Search for oriented 4-CDCs in snarks. The negative calibration above
  explains why this is impossible in the cubic snark setting.

## Risks and likely failure modes

1. **Weighted CDC certificates fail on Petersen.** Then the CDC route
   is probably the wrong abstraction for $S^2$-flows, and the project
   should pivot to HMM immersions and gadget composition.
2. **The flower CDC template fails symbolically.** That would be an
   interesting obstruction to record, not a dead end.
3. **Dot-product algebra blows up.** Boundary-triple tracking is
   well-defined but compatibility conditions may become too long for a
   clean theorem.

## Estimated effort

- Phase 0: 1--2 days.
- Phase 1: 1--2 weeks.
- Phase 2: 1--2 weeks if the symbolic flower check closes.
- Phase 3: 2--4 weeks for triangle blow-up, dot product, and 4-cut
  splice.

Total: low single-digit months for a meaningful infinite-family
result, dominated by Phase 1 and Phase 2.

## Immediate first action

Implement the negative calibration:

1. prove/encode `oriented_4cdc => NZ4-flow` for cubic graphs;
2. test it on Petersen and a few 3-edge-colourable cubic positives;
3. write `docs/cdc_negative_calibration.md`.

Only after that should we build the weighted CDC solver.
