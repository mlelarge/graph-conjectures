# Earth–Moon disproof — plan

## Goal

Either:

- **Disproof target.** Exhibit a biplanar graph $G$ with $\chi(G) \ge 10$, falsifying the implicit folklore $\chi_{\rm EM} = 9$, or
- **Upper-bound target.** Show $\chi_{\rm EM} \le 11$ via a density theorem on 12-critical $K_9$-free graphs.

## Bracket and structural constraints

Current bracket (Ringel 1959; Sulanke / Gardner 1980; Heawood 1890):

$$9 \le \chi_{\rm EM} \le 12.$$

Any biplanar graph $G$ on $n$ vertices satisfies:

- $|E(G)| \le 2(3n-6) = 6n-12$.
- $G$ is $K_9$-free, since the thickness of $K_9$ is $3$.
- $\delta(G) \le 11$, hence any 10-critical biplanar $G$ has $\delta \ge 9$.

For $\chi(G) \ge 10$: combined with $K_9$-freeness, this forces $\omega(G) \le 8$.

For $\chi(G) \ge 12$ (12-critical, $K_9$-free, biplanar): Kostochka–Yancey (2014) gives
$|E(G)| \ge \frac{65n - 54}{11}$, while biplanarity gives $|E(G)| \le 6n - 12 = \frac{66n - 132}{11}$.
These are compatible only for $n \ge 78$. To close the upper bound to 11 by density alone,
a $K_9$-free strengthening must add more than
$(n-78)/11$ edges over Kostochka–Yancey; asymptotically, this means an extra
edge-density coefficient at least $1/11$, not merely an arbitrary positive $c n$ term.

## Phase 1 — biplanarity oracle and certificates

**Reuse, don't rebuild.** Kirchweger–Scheucher–Szeider (SAT 2023, LIPIcs.SAT.2023.14) already
ship a SAT-modulo-symmetry framework with Schnyder/Kuratowski-style planarity encodings
applied to Earth–Moon-scale instances. Imitate or fork rather than write a bespoke oracle.

For one-shot candidate testing a lazy CEGAR loop is enough:

1. SAT guesses a 2-edge-colouring $E = E_1 \sqcup E_2$.
2. Each layer is checked for planarity (`networkx.check_planarity` or boost graph).
3. On failure, extract a Kuratowski subdivision and add a clause forbidding all those edges
   from simultaneously living in the offending layer.
4. Iterate until SAT reports UNSAT (graph not biplanar) or yields a certificate.

**Certificates.**

- *Positive*: edge partition + two combinatorial embeddings, re-checked by an independent
  planarity tester (we trust the oracle iff the certificate replays).
- *Negative*: solver log + reproducible seed + minimised core. Document the trust level
  explicitly; an unaudited UNSAT is weaker evidence than a small reproducible enumeration.

**Chromatic side.**

- DSATUR for upper bounds.
- SAT or ILP for "no proper 9-colouring" lower bounds.
- "$\chi(G) \ge 10$" is a universal statement over 9-colourings, so the joint search in
  Phase 5 must use CEGAR (find a 9-colouring, add a blocking refinement, repeat) rather
  than encoding it as a single existential SAT.

## Phase 2 — regression suite

Before mining anything, the oracle must agree with known facts.

| Input | Expected | Source |
|---|---|---|
| $K_6 + C_5$ | biplanar, $\chi = 9$ | Sulanke / Gardner 1980 |
| Boutin–Gethner–Sulanke 9-critical thickness-2 graphs | biplanar, $\chi = 9$ | BGS 2008 |
| Gethner–Sulanke infinite 9-critical thickness-2 family | biplanar, $\chi = 9$ | GS 2009 |
| $K_8$ | biplanar | classical |
| $K_{5,5}$ | biplanar | classical (positive case) |
| $K_9$, $K_{7,7}$, $K_{6,9}$, $K_{5,12}$ | not biplanar | classical |
| All graphs on $n \le 13$ | every biplanar graph is 9-colourable | KSS 2023 |
| $(C_5 \boxtimes K_4) \setminus v$ on 19 vertices | not biplanar | KSS 2023 |

A failure on any of these blocks all later phases.

## Phase 3 — main miner: dense biplanar supergraphs

Generate two planar triangulations $T_1, T_2$ on a shared vertex set and consider $G = T_1 \cup T_2$.

- Edge-disjoint pairs reach the $6n - 12$ ceiling exactly.
- Non-edge-disjoint pairs are still valid candidates: every biplanar graph is a subgraph
  of some maximal biplanar graph, so we are searching the right closure.
- Generators: random Schnyder woods, random edge-flip walks on triangulation space,
  stacked / Apollonian triangulations, planar 3-trees.
- Deduplicate via nauty canonical labelling.
- For each $G$, report $(|E|, \omega, \chi\text{-bounds}, K_9\text{-free?})$. Flag anything with
  $\chi \ge 10$ for full Phase 1 verification.

This is the project's spine, not one option among several.

## Phase 4 — Catlin / Gethner blowup miner

Weighted odd-cycle clique blowups
$C_{2r+1}[K_{a_1}, \dots, K_{a_{2r+1}}]$:

- $\omega = \max_{i} (a_i + a_{i+1})$ — constrain to $\le 8$.
- $\alpha = r$ when all $a_i > 0$, since an independent set chooses at most one
  vertex from each selected cycle fibre and at most $r$ fibres from $C_{2r+1}$.
- $\chi$ is the weighted chromatic number of the odd cycle: equivalently, the least
  number of colours for assigning $a_i$ colours to cycle vertex $i$, with adjacent
  assigned sets disjoint. Lower bounds include
  $\max_i(a_i+a_{i+1})$ and $\left\lceil \sum_i a_i / r \right\rceil$.
- $|E| \le 6n - 12$.

**Headline target.** $C_7 \boxtimes K_4 = C_7[4,4,4,4,4,4,4]$ on 28 vertices.
- $\omega = 8$ and $\alpha = 3$, so $\chi \ge \lceil 28/3 \rceil = 10$.
- $\chi = 10$: assign four colours to each of the seven $K_4$ fibres, with adjacent
  fibres receiving disjoint colour sets; for example
  $\{1,2,3,4\}, \{5,6,7,8\}, \{1,2,3,9\}, \{4,5,6,7\},
  \{1,2,8,9\}, \{3,4,5,6\}, \{7,8,9,10\}$.
- $K_9$-free (since $\omega = 8$).
- $|E| = 28 \cdot 11 / 2 = 154$ vs $6 \cdot 28 - 12 = 156$ — fits the edge bound with slack 2.

Biplanarity is the only unknown. KSS 2023 already disposed of the 19-vertex $C_5 \boxtimes K_4$
analogue; $C_7 \boxtimes K_4$ is the natural lift and the right first concrete attack.

**Wider sweep.** Enumerate all $(2r+1, a_1, \dots, a_{2r+1})$ with $\omega \le 8$, $\chi \ge 10$
forced, $|E| \le 6n - 12$, and $n \le 30$. Test each.

## Phase 5 — joint SAT-modulo-symmetry search

Only after Phases 3–4 yield either a new biplanar 9-critical graph or a near-miss
10-chromatic graph whose only unknown is biplanarity.

- Boolean $e_{ij}$ for edge presence and layer; SMS-style canonical-form generation.
- Lazy Kuratowski for both layers.
- CEGAR for "no 9-colouring": solver yields a candidate, an external 9-COL search either
  finds a colouring (add blocking clause) or proves none exists (refine the candidate's structure).
- Symmetry break by anchoring a $K_8$ (or two intersecting $K_8$s); start at $n \le 25$.

## Phase 6 — sharpened upper-bound route

To prove $\chi_{\rm EM} \le 11$ it suffices to rule out 12-critical $K_9$-free biplanar graphs.

- Kostochka–Yancey: $|E| \ge (65n - 54)/11$ for any 12-critical graph.
- Biplanarity: $|E| \le (66n - 132)/11$.
- Coexistence requires $n \ge 78$.

So either:

- prove a $K_9$-free strengthening
  $|E| > 6n - 12$ for every 12-critical $K_9$-free graph, equivalently an
  improvement over Kostochka–Yancey exceeding $(n-78)/11$ edges; or
- close the case $n \ge 78$ directly, possibly via SAT for small $n$ and a structural
  argument above some threshold.

Read sources: Kostochka–Yancey 2014 original; Postle's improvements; Kostochka–Stiebitz
on $K_t$-free critical graphs; relevant Reed / Norin–Postle–Song lines for the $K_9$-free
lower bound.

## Repository layout

```
problems/earth_moon_problem/
  README.md
  docs/
    plan.md                       ← this document
    literature_notes.md           ← KSS 2023, BGS 2008, GS 2009, KY 2014, Mansfield 1983, Hutchinson
    upper_bound_notes.md          ← Phase 6 working file
  scripts/
    biplanar_sat.py               ← CEGAR Kuratowski oracle
    chromatic_solver.py           ← DSATUR + SAT/ILP
    evaluate_candidate.py         ← entry point: graph → (biplanar?, χ, certs)
    verify_biplanar_certificate.py
    triangulation_pair_miner.py   ← Phase 3
    cycle_blowup_miner.py         ← Phase 4
  data/
    sulanke_k6_c5.graph6
    bgs_2008_examples/
    candidates/
    certificates/
  tests/
    test_oracle_regressions.py    ← Phase 2 table above
```

## Risks and exits

- **NP-completeness of biplanarity** (Mansfield 1983) puts a hard ceiling on candidate size
  without serious symmetry breaking. Reuse SMS rather than fight this from scratch.
- **$\chi_{\rm EM} = 9$ may simply be true.** Plan pivots to Phase 6; this is *not* a
  loss because the upper-bound route now has a concrete density-theorem target.
- **KSS 2023 covered considerable ground on the lower-bound side.** Avoid duplicating
  their enumerations; treat their negative results as regression targets and start the
  miner where they stopped.

## Removed from earlier draft

- *Family A — joins $K_a + H$.* Analytically exhausted: $a = 8$ creates a $K_9$;
  $a = 7$ same once $H$ has any edge; $a = 6$ forces $H$ triangle-free with
  $|E(H)| \le 9$, impossible for a 4-chromatic critical core; $a = 5$ requires a
  $K_4$-free 5-chromatic graph on $\le 7$ vertices, which doesn't exist (Dirac:
  5-critical implies $|E| \ge 2n + 1$). Kept only as a regression / sanity calibration.
- *Family B — Hajós/Ore from $K_9 - e$.* $K_9 - e$ is 8-chromatic, and Hajós/Ore
  preserve non-$k$-colourability of *both* inputs; they do not raise the chromatic
  number. The construction was wrong and is removed in full.
- *"No second 9-chromatic biplanar family in 50 years" framing.* False — Boutin–Gethner–Sulanke
  2008 and Gethner–Sulanke 2009 already published many, including an infinite family.
- *$K_{5,5}$ as a non-biplanar regression.* $K_{5,5}$ is biplanar; it is now a
  positive regression. Negative regressions: $K_9$, $K_{7,7}$, $K_{6,9}$, $K_{5,12}$.
