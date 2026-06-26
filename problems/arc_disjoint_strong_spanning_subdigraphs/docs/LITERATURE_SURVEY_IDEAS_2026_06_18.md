# Literature survey: possible imports after D48

Date: 2026-06-18.

Status: literature scan, not a proof update.  The goal is to identify
external proof technology that might move the non-degenerate Missing
Entry Lemma or the broader WC3 program.

## Main takeaway

The best new idea is not another one-shot B3+ variant.  The promising
direction is to import the recent split-digraph proof machinery:

* splitting-off paths through independent vertices;
* pending decompositions;
* critical path-pair minimization;
* semicomplete nice decompositions.

This is close to the current near-split chord setting but avoids the
fragility of keeping the original `U` fixed.  D47 showed fixed-`U`
one-shot B3+ is false for all hard pairs; the split-digraph machinery is
designed to build and then complete partial strong decompositions by
assigning spare in/out arcs later.

The naive reduction "delete the unique chord and invoke the split-digraph
characterization" is already dead in the ledger (D4/G16): it was a
vacuous residual and an object mismatch.  The useful import is the proof
technology, not the deletion reduction.

## Directly relevant sources

### 1. Bang-Jensen and Wang, split digraphs (2023)

Paper: "Strong arc decompositions of split digraphs",
arXiv:2309.06904.

Relevant results:

* every 3-arc-strong split digraph has a strong arc decomposition,
  constructively;
* they use semicomplete nice decomposition, splitting-off, and lifting;
* Lemma 2.4: if a core `X` already has a SAD and every outside vertex has
  two in-neighbors and two out-neighbors in `X`, then the whole digraph
  has a SAD;
* Lemma 2.5: after splitting off at most two pairs at each independent
  vertex, a SAD of the semicomplete core lifts back.

Possible import:

Replace the local B3+ question "can this fixed `U` survive the rehang?"
by a pending-completion question: can we split off the problematic
chain/cage paths to get a semicomplete multigraph core with a known SAD,
then lift while assigning spare in/out arcs to cover vertices that one
colour missed?

### 2. Ai-He-Li-Qin-Wang, complete split characterization (2024)

Paper: "A complete characterization of split digraphs with a strong arc
decomposition", arXiv:2408.02260.

Relevant results:

* full characterization of split digraphs without a strong arc
  decomposition;
* resolves the Bang-Jensen-Wang split-digraph problems;
* introduces "pending decomposition": two arc-disjoint strong subdigraphs
  that already cover the semicomplete part and leave every singly-covered
  independent vertex with spare in/out arcs for the other colour;
* Lemma 2.6: a pending decomposition completes to a SAD;
* uses minimal/critical arc-disjoint path pairs after feasible
  splitting-off.

Possible import:

This looks like the right language for D47/D48.  A short-chain B3+
failure is exactly a failure of one fixed `U`, not necessarily a failure
of pending completion.  The next proof attempt should formulate a
"pending Missing Entry Lemma": in a sealed multi-crossing chain kernel,
the forced crossings and cage hooks create a critical path-pair whose
splitting-off yields a semicomplete core outside the known exceptions.

### 3. Bang-Jensen-Havet-Yeo, spanning Eulerian subdigraphs (2019)

Paper: "Spanning eulerian subdigraphs in semicomplete digraphs",
arXiv:1905.11019.

Relevant results:

* every 2-arc-strong semicomplete digraph has a spanning Eulerian
  subdigraph containing any prescribed arc;
* every 2-arc-strong semicomplete digraph has a spanning Eulerian
  subdigraph avoiding any prescribed single arc;
* for avoiding a prescribed set of `k` arcs, they prove a general
  connectivity bound and establish the conjectured `k+1` bound for
  `k<=3` and for star forests;
* every 2-arc-strong semicomplete digraph is Eulerian-connected.

Possible import:

D42-style sealed kernels have a small number of forced consumed chain
arcs, often at most three.  Instead of proving a tree-by-tree sparing
lemma, try an Eulerian scaffold in the semicomplete part that avoids the
forced arc set, then extract the needed branchings/exits from that
scaffold.  This may be useful exactly where CT/CL currently do
case-by-case forced-tail bookkeeping.

### 4. Bang-Jensen-Bessy-Havet-Yeo, arc-disjoint in/out branchings
(2020)

Paper: "Arc-disjoint in- and out-branchings in digraphs of independence
number at most 2", arXiv:2003.02107.

Relevant results:

* every digraph with independence number at most 2 and arc-connectivity
  at least 2 has an arc-disjoint out-branching and in-branching;
* this settles Thomassen's branching conjecture in that class;
* for semicomplete digraphs they give small rooted exception structures.

Possible import:

Check whether the contraction or residual pieces in CRUX-A often have
`alpha <= 2` after deleting the cage/root.  If so, the L-exist search may
be replaceable by a known good-pair theorem on a residual plus a lifting
argument.  This is weaker than SAD, but it matches the branchings that
the local Conjecture-L machinery manipulates.

### 5. Semicomplete compositions and strong-subgraph packing

Sources:

* Bang-Jensen-Gutin-Yeo, "Arc-disjoint Strong Spanning Subdigraphs of
  Semicomplete Compositions", arXiv:1903.12225 / JGT 2020.
* Sun-Gutin-Ai, "Arc-disjoint strong spanning subdigraphs in
  compositions and products of digraphs", arXiv:1812.08809.
* Sun-Gutin-Zhang, "Packing Strong Subgraph in Digraphs",
  arXiv:2110.12783.

Relevant results:

The semicomplete-composition characterization is already present in the
ledger.  The 2021 packing paper is mostly complexity/algorithmic and
does not look like a direct proof lever, but it reinforces that
composition structure is the tractable frontier.

## Best next technical move

Do not try another broad B3+ selection statement.  Instead:

1. Add a `pending_decomposition_probe.py` for the checked-in witnesses.
   For each near-split host, identify feasible split-off path pairs
   through `V1`, split them to a semicomplete multigraph on `V2`, and
   test whether the resulting core avoids the semicomplete exceptions.

2. Add a `nice_decomposition_probe.py` for the semicomplete residuals.
   Compute the nice decomposition / cut-arc order in the relevant
   semicomplete core and compare it with D42 forced chain crossings.
   The hope is that the no-nesting/order constraints force a B3+
   eligible forced tail.

3. If both probes line up on D42 and separate D47, try to state:

   **Pending Missing Entry Lemma.**  In a non-degenerate sealed
   multi-crossing chain kernel, the forced crossing block admits a
   feasible critical path pair whose split core has a pending
   decomposition; lifting it yields either the B3+ entry or a direct
   two-colour completion.

This would move the proof away from fixed-`U` one-shot repair and toward
the stronger completion mechanism used in the split-digraph literature.

## D49 probe result

The first concrete probe has now been added:

    scripts/pending_decomposition_probe.py

It implements the split-off/pending idea at witness level.  For each
near-split host, it chooses two paths `x -> s -> y` through each
independent-side vertex `s in V1\{p,q}`, replaces them by split arcs
`x -> y` in the semicomplete side, SAD-colours the split core, and checks
whether each pair of split arcs receives opposite colours.

Results:

* pending hits on D17/D47 host, D18, D19, D38, and D42;
* D42 is especially important: all three independent forced-chain
  vertices receive opposite-colour split arcs, so the realized chain
  kernel is compatible with pending completion;
* no pending hit on D28 in the naive two-split probe: every tested split
  core remains lambda 1 / UNSAT.

Interpretation: the split-digraph technology is genuinely aligned with
the D42 chain-kernel geometry, but the tournament-core D28 example warns
that a pending proof needs either a more flexible critical path-pair
operation or a separate cut-avoidance treatment.

## D50 prescribed-colour strengthening

`scripts/pending_decomposition_prescribed_probe.py` now forces one split
arc through each independent-side vertex to be red and the other blue
before solving the split core SAD instance.

It finds prescribed hits on D17/D47 host, D18, D19, D38, and D42.  In
D42 the first split choice already works under prescribed opposite
colours through the three forced-chain host vertices.  D28 again remains
outside the naive pending picture.

This is the strongest support so far for importing pending
decompositions into the chain-kernel proof: the colouring needed for
lifting can be demanded up front, not merely observed after the solver
chooses a SAD.

## Lower-priority / caution

* The Ai split-characterization should not be used through chord deletion;
  that route was already killed by D4/G16.
* Mader/Frank splitting-off remains useful for census generation, but the
  minimal-degree count transfer to multidigraphs failed at D41/G45.
* Random regular or random `k`-in/`k`-out digraph results are unlikely to
  help the worst-case constant-lambda problem; the ledger already killed
  that as an asymptotic route.
