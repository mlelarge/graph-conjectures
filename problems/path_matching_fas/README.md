# Path-FAS and Matching-FAS in Tournaments

Attack on **Problem 4.4 of Aboulker–Aubian–Lopes**
([arXiv:2402.10782](https://arxiv.org/abs/2402.10782), *Finding forest-orderings of
tournaments is NP-complete*, 2024).

## The problem

Given an undirected graph class $\mathcal{C}$, a **$\mathcal{C}$-FAS** of a
tournament $T$ is a feedback arc set $F \subseteq E(T)$ whose underlying
undirected graph (forgetting arc orientations) lies in $\mathcal{C}$. The
$\mathcal{C}$-FAS Problem decides whether such an $F$ exists.

The source paper proves (Theorem 1.1) that the $\mathcal{C}$-FAS Problem is
**NP-complete when $\mathcal{C}$ is the class of all forests**. Problem 4.4
asks for the complexity in two natural subclasses:

- **(M)** $\mathcal{C}$ = all graphs of maximum degree $\le 1$ (matchings);
- **(P)** $\mathcal{C}$ = all paths.

## Status

**Matching-FAS half of Problem 4.4: internally proved polynomial; prior-art
check still needed before claiming novelty.**

[`docs/lemmas.md`](docs/lemmas.md) proves:

> **Theorem.** The matching-FAS decision problem for tournaments is in
> $\mathsf{P}$; specifically, it reduces to 2-SAT after picking one arc
> per *cyclic 3-cycle module*. Total time $O(n^3)$.

The argument has five pieces (see [`docs/lemmas.md`](docs/lemmas.md) for proofs):

- **Theorem 1 (characterization).** $T$ has a matching-FAS iff there
  exists a matching $M \subseteq A(T)$ whose every arc is *no-shortcut*
  (no $w$ with $u \to w \to v$) and every cyclic 3-cycle of $T$
  contains exactly one $M$-arc.
- **Lemma 2.** A cyclic 3-cycle has all three arcs no-shortcut iff it
  is a *module* of $T$.
- **Lemma 3.** Two distinct cyclic-3-cycle modules are vertex-disjoint.
- **Lemma 4.** No arc of a cyclic-3-cycle module belongs to any other
  cyclic 3-cycle.
- **Lemma 5.** No no-shortcut arc has exactly one endpoint in a
  cyclic-3-cycle module.

By Lemmas 3-5 the modules are completely decoupled (pick any one arc per
module; no interaction with the rest). The remaining cyclic 3-cycles
have $\le 2$ no-shortcut arcs each, so the residual exists/matching
problem encodes as 2-SAT.

The cyclic-module objects themselves are standard tournament modules.
This folder claims only a self-contained internal proof of the polynomial
decision algorithm. Before presenting it as a new result, the specific
2-SAT reduction should be checked against the tournament modular
decomposition and feedback-arc-set literature, including the sources
cited by Aboulker-Aubian-Lopes.

The algorithm is implemented in [`scripts/poly_mfas.py`](scripts/poly_mfas.py).
It is cross-checked against brute force on:

- **All 74 non-isomorphic tournaments at $n \in \{3,4,5,6\}$** (exhaustive).
- **150 random tournaments at $n \in \{7, 8\}$** — every YES answer
  also passes the deeper certificate check (returned $M$ is a matching
  and $T \oplus M$ is transitive).

Zero disagreements: see [`tests/test_poly.py`](tests/test_poly.py).

**Path-FAS half of Problem 4.4: open.**

The first correction is definitional. A path-shaped FAS $F$ need not be
exactly the back-arc set of an order; the back-arc set is only contained
in $F$. Since every subgraph of a path is a linear forest, and every
linear forest can be completed to a path by adding extra tournament arcs
to the FAS, formal Path-FAS is equivalent to:

> Does $T$ have an order whose back-arc graph is a linear forest?

See [`docs/path_fas.md`](docs/path_fas.md). The old exact connected-path
back-arc condition is strictly stronger and is kept only as a diagnostic.

The matching proof does not transfer. A path-FAS candidate has maximum
degree 2, so a triangle can contain two selected arcs forming a "V". In
those configurations, the long-arc/no-shortcut obstruction used for
matchings becomes conditional on the second selected arc. The path half
is therefore the linear-forest ordering problem: strictly more permissive
than matching-FAS and strictly narrower than forest-FAS.

**Empirical and structural notes on LFO** are in
[`docs/path_fas_structure.md`](docs/path_fas_structure.md). Highlights:

- LFO NO instances first appear at $n = 7$.
- The Paley tournament $Q(7)$ is LFO NO because $f(Q(7)) = 7 > n - 1$;
  the size bound alone is decisive.
- The `FOREST_NOT_PATH_FAS` 7-vertex witness has $f(T) = 5 \le n - 1$
  yet still LFO NO: exactly one ordering achieves max-deg 2, and its
  back-arc graph is a Hamiltonian 7-cycle, not a forest. The
  combinatorial coupling between max-degree and acyclicity is the
  obstruction.
- Tested-and-falsified hypothesis: "vertex $v$ with both $N^+(v)$ and
  $N^-(v)$ inducing cyclic 3-cycles ⇒ LFO NO". Corrected true-LFO
  count: 460/512 such tournaments admit an LFO; the weaker degree-only
  relaxation gives 478/512.
- Full exact n=7 census: 456 non-isomorphic tournaments, 436 LFO YES,
  20 LFO NO. Only 2 are size-bound NO; the other 18 are combinatorial
  NO.
- LFO NO instances occur in exactly seven score sequences. The densest
  buckets are `(2,3,3,3,3,3,4)` with 8 NO out of 15, `(2,2,3,3,3,4,4)`
  with 5 NO out of 47, and the regular bucket with 3 NO out of 3.
- The 18 combinatorial n=7 NO instances form 15 duality orbits; all
  are vertex-minimal. They split into 7 coupling obstructions, 7
  degree obstructions, 2 cycle obstructions, and 2 instances where both
  relaxations fail.
- The n=7 obstruction list is not a complete explanation of larger
  NO instances. Exact n=8 census: 6880 non-isomorphic tournaments,
  5016 LFO YES, 1864 LFO NO. Of the NO instances, 1292 contain an
  induced n=7 NO and 572 do not; those 572 are exact order-8 minimal
  obstructions.
- The 572 minimal n=8 obstructions form 294 duality orbits; 418 are
  prime and 568 have trivial automorphism group. Their relaxation split
  is 340 degree obstructions, 189 coupling obstructions, 13 cycle
  obstructions, and 30 where both relaxations fail.
- Exact n=9 census: 191536 non-isomorphic tournaments, 67221 LFO YES,
  124315 LFO NO. Of the NO instances, 118755 contain an induced n=8
  NO and 5560 do not; those 5560 are exact order-9 minimal obstructions.
  The minimal n=9 obstructions form 2884 duality orbits, and 4303 are
  prime.
- Falsified candidate poly algorithms: "min FAS is a linear forest"
  and "matching 2-SAT extended". See `path_fas_structure.md` §
  "Candidate algorithms tried and abandoned".
- Hardness-route checkpoint: direct reuse of the AAL forest-FAS
  construction fails because its rigid Figure 1 block forces a
  degree-4 backedge tree. An anchor-safe 9-vertex path-rigid block and
  a 7-vertex exact two-state port block have been found and
  exhaustively certified. The remaining reduction obstacle is external
  wiring: inactive ports in the current two-state block do not yet all
  retain spare degree, and one-/two-auxiliary local extensions do not
  fix this.
- **Asymmetric external wiring also fails locally.** Adding a single
  external "clause" vertex $c$ to the 7-block: strict wiring (no
  inactive port hits) admits 0 orientations out of 128; relaxed wiring
  (active hits in both states, inactive hits to spare-degree vertices
  tolerated) admits exactly 1 orientation, and only because the R-state
  back-arc graph leaves $y_1$ isolated. Two external vertices: 0
  compositions where both externals provide active hits in both states.
  See [`docs/hardness_route.md`](docs/hardness_route.md) §
  "Asymmetric external wiring also fails locally". The cumulative
  negative evidence is increasingly compatible with LFO being in P,
  though not conclusive.
- **Current algorithmic attack: score-window exact solver.** If an
  order has backdegree at most 2 at every vertex, then every vertex
  $v$ must be placed within distance 2 of its indegree:
  $|i_\prec(v)-d^-(v)|\le 2$. This gives a five-position window per
  vertex. [`scripts/lfo_score_window.py`](scripts/lfo_score_window.py)
  uses that lemma, interval-Hall pruning, and forced-future
  degree/cycle pruning. It matches all exact checks so far: all
  non-isomorphic tournaments through $n=6$, the full exact $n=7$
  census, the known n=8 NO records, and a sampled exact n=9 census
  slice. See [`docs/score_window.md`](docs/score_window.md). This is
  still an exact branch-and-prune solver, not a polynomial proof.
  Hall feasibility bounds the active score-window band by 9, but the
  transitive tournament with a reversed matching has arbitrarily many
  crossing backedges despite score displacement only 1. Therefore the
  naive active-frontier DP is dead; the next formal target is a
  quotient-compressed DP for the expired pending components. A second
  probe shows component connectivity is genuinely load-bearing: same
  placed set and same degree vector can have different component
  partitions and different extendability. Repeating that probe gives
  $2^k$ distinct component pairings with the same coarse state, so any
  successful DP needs a real quotient of connectivity, not another
  bounded-frontier slogan. The first quotient probes are negative:
  degree-only, component-count, component-size multiset, and
  low-degree-set-plus-component-count all mix extendable and
  non-extendable states on the entropy family.
- **Forced/flexible score-window decomposition.** Disjoint score
  windows force the relative order of a vertex pair. Any backedge on
  such a pair is therefore mandatory in every LFO candidate; if the
  forced backedge graph is not a linear forest, the tournament is
  immediately LFO NO. The remaining choices are only overlapping-window
  pairs, an interval graph of clique number at most 9 after Hall
  feasibility. This reframes the current positive target as: combine a
  fixed forced linear forest with bounded-clique interval choices.
  The exact forced/flexible solver agrees with the score-window solver
  through the full n=7 census. On n=24 light-noise skew probes it
  improves most instances but does not remove rare search spikes, so it
  is the right DP normalization rather than the final algorithm.
- **Naive active-bag DP fails.** After forced/flexible normalization,
  the natural interval-bag state would keep active-window vertices,
  placed-active subset, active degrees, and active component partition.
  `ff_signature_probe.py` finds two prefixes of the 7-vertex component
  witness with identical active-bag signature but different
  extendability. The missing information is latent connectivity through
  forgotten vertices outside the active bag.
- **Visible-latent interface is bounded, but not complete.** An
  expired prefix vertex can still be touched by a future flexible
  backedge only through an unplaced active vertex. Since each unplaced
  active vertex has at most two remaining backdegree slots and Hall
  bounds the active band by 9, the old-prefix ports relevant to future
  flexible choices are bounded by 18; active plus old-visible ports are
  bounded by 27. The strengthened signature separates the known
  active-bag collision and survived the early n=7 / entropy-family
  probes, but a later skew n=12 witness refutes visible-latent
  extension-equivalence itself. Two pruned same-prefix-set states have
  identical visible-latent signatures, one has an LFO completion, and
  the other has none. Sleeping-block and wake-1 signatures separate
  this collision; on that witness tournament a depth-5 sweep finds
  12 visible-latent extendability collisions and 0 sleeping-block
  collisions. The current proof draft is
  [`docs/exchange_proof_draft.md`](docs/exchange_proof_draft.md). The
  positive DP target has therefore shifted from proving visible-latent
  soundness to finding a bounded refinement that records the missing
  dormant path connectivity.
- **Fixed finite wake horizon fails as a bisimulation.** A wake-$h$
  signature records vertices whose windows open within the next $h$
  cuts and the old prefix ports they can already hit. The base
  wake-chain witness defeats horizon 1; inserting transitive padding
  before the delayed dormant vertex shifts the same obstruction one
  cut later. Horizons 1-4 are pinned: same horizon-$h$ signature,
  different horizon-$h$ child transition profiles, separated by
  horizon $h+1$. Thus "track the next $h$ opening layers" is not the
  missing bounded DP state.
- **Empirical score-window growth.** A descriptive run over exact
  all-record data through $n=7$, exact n=8 NO records, and a stride-500
  n=9 sample gives maximum node counts
  $5,7,10,46,120,163,169$ for $n=3,\ldots,9$. The mixed log-log fit has
  exponent about $3.78$ for maxima and $2.88$ for p95. This is not an
  asymptotic claim, because the n=8/n=9 rows are not the same population
  as the exact small rows, but it supports the view that the
  score-window state space is the right one to attack. A fresh labeled
  random $n=10$ probe gives max 266 nodes and p95 63 over 2000 samples.
- **Skew-score probes activate forced/flexible structure.** Starting
  from transitive tournaments and independently reversing arcs with
  probability $p$, the mean forced-backedge count rises with $n$:
  at $n=24$, it is 2.89, 7.18, 13.26, 21.68 for
  $p=0.02,0.05,0.10,0.20$. Forced-degree obstructions also appear.
  The hard empirical regime is light noise ($p\approx 0.02$ to $0.05$),
  where Hall usually passes and occasional instances require many more
  score-window nodes.

## Files

- [`docs/attack_plan.md`](docs/attack_plan.md) — original phased plan.
- [`docs/lemmas.md`](docs/lemmas.md) — Theorem 1 + Lemmas 2-5 +
  Theorem 2 (polynomial-time algorithm), with full proofs.
- [`docs/path_fas.md`](docs/path_fas.md) — corrected formal target for
  Path-FAS, triangle flip table, and small separating examples.
- [`docs/score_window.md`](docs/score_window.md) — bounded
  score-displacement lemma, exact score-window solver, validation
  tables, and the bounded-frontier DP target.
- [`docs/hardness_route.md`](docs/hardness_route.md) — AAL reduction
  audit for the path case, the direct-reuse obstruction, and the
  path-rigid replacement block.
- [`scripts/verify.py`](scripts/verify.py) — trust-root verifier:
  classifies back-arcs of $T$ under any ordering.
- [`scripts/brute.py`](scripts/brute.py) — brute-force decider over
  all $n!$ orderings.
- [`scripts/sweep.py`](scripts/sweep.py) — full sweep over
  non-isomorphic tournaments for $n \le 6$.
- [`scripts/structural.py`](scripts/structural.py) — cyclic 3-cycle
  enumeration, no-shortcut arcs, and the original (back-tracking)
  structural decider used during exploration.
- [`scripts/poly_mfas.py`](scripts/poly_mfas.py) — the polynomial-time
  decider: reduction to 2-SAT, with built-in cross-check harness.
- [`scripts/path_fas.py`](scripts/path_fas.py) — formal Path-FAS
  brute-force decider plus certificate completion from linear-forest
  backarcs to an actual path-shaped FAS.
- [`scripts/path_rigid_block.py`](scripts/path_rigid_block.py) —
  exhaustive certificate and random search harness for the path-rigid
  replacement block used in the hardness route.
- [`scripts/path_state_signature.py`](scripts/path_state_signature.py)
  — finite LFO signature enumerator for two-state path port gadgets;
  records the first exact 7-vertex two-state block and its limitation.
- [`scripts/lfo_random_sample.py`](scripts/lfo_random_sample.py) —
  corrected true-LFO random sampler separating size-bound NO from
  combinatorial NO.
- [`scripts/lfo_sweep.py`](scripts/lfo_sweep.py) — exhaustive true-LFO
  sweep over non-isomorphic tournaments; slow at $n = 7$ with the current
  canonical labeling.
- [`scripts/lfo_score_bucket.py`](scripts/lfo_score_bucket.py) — exact
  non-isomorphic enumeration inside selected score-sequence buckets,
  using score-respecting canonicalization.
- [`scripts/lfo_backtrack.py`](scripts/lfo_backtrack.py) — pruned exact
  LFO solver used for the n=8 and n=9 censuses.
- [`scripts/lfo_score_window.py`](scripts/lfo_score_window.py) —
  score-window exact LFO solver using the $|i_\prec(v)-d^-(v)|\le 2$
  lemma, interval-Hall pruning, and forced-future degree/cycle pruning.
- [`scripts/lfo_forced_flexible.py`](scripts/lfo_forced_flexible.py) —
  exact forced/flexible solver: preload forced backedges, then search
  only over overlapping-window choices.
- [`scripts/ff_signature_probe.py`](scripts/ff_signature_probe.py) —
  active-bag and visible-latent signature collision search for the
  forced/flexible DP attempt.
- [`scripts/wake_signature_probe.py`](scripts/wake_signature_probe.py)
  — wake-horizon signature and one-step transition-profile probes for
  the forced/flexible DP attempt, including padded finite-horizon
  counterexamples.
- [`scripts/exchange_repair_probe.py`](scripts/exchange_repair_probe.py)
  — suffix-transfer failure detector and single-left-move exchange
  repair probe for the visible-latent proof attempt; supports exact
  census-level repair counts.
- [`scripts/score_window_growth.py`](scripts/score_window_growth.py) —
  descriptive search-node growth summaries and log/log-log fits.
- [`scripts/score_window_random_probe.py`](scripts/score_window_random_probe.py)
  — labeled random n=10 growth probe and skew-score forced/flexible
  experiments.
- [`scripts/score_window_forced.py`](scripts/score_window_forced.py) —
  forced/flexible pair decomposition induced by disjoint/overlapping
  score windows.
- [`scripts/score_window_dp_obstruction.py`](scripts/score_window_dp_obstruction.py)
  — reversed-matching obstruction to the naive active-score-frontier DP.
- [`scripts/pending_state_probe.py`](scripts/pending_state_probe.py) —
  partial-state probe showing component connectivity cannot be discarded.
- [`scripts/tournament_canonical.py`](scripts/tournament_canonical.py)
  — dependency-free tournament canonicalizer used for exact n=9
  representative generation.
- [`scripts/lfo_representatives.py`](scripts/lfo_representatives.py)
  — compact representative generator; outputs n=8/n=9 JSONL keys.
- [`scripts/lfo_extend_census.py`](scripts/lfo_extend_census.py) —
  exact n=8 census by extending and deduplicating the exact n=7
  representatives.
- [`scripts/lfo_census_from_reps.py`](scripts/lfo_census_from_reps.py)
  — resumable exact census from compact representatives, using
  hereditary lower-order NO filtering.
- [`scripts/lfo_minimal8_analysis.py`](scripts/lfo_minimal8_analysis.py)
  — analyzes the 572 exact order-8 minimal obstructions.
- [`scripts/lfo_minimal9_summary.py`](scripts/lfo_minimal9_summary.py)
  — compact summary of the 5560 exact order-9 minimal obstructions.
- [`scripts/lfo_obstruction_analysis.py`](scripts/lfo_obstruction_analysis.py)
  — analyzes the 18 exact combinatorial n=7 NO instances.
- [`scripts/lfo_forbidden7_test.py`](scripts/lfo_forbidden7_test.py)
  — tests whether random larger NO instances are explained by induced
  n=7 NO subtournaments.
- [`scripts/test_double_triangle_obstruction.py`](scripts/test_double_triangle_obstruction.py)
  — corrected double-cyclic-triangle hub enumeration.
- [`scripts/cross_check.py`](scripts/cross_check.py) — exhaustive
  agreement check (structural vs brute) for $n \le 6$.
- [`scripts/random_check.py`](scripts/random_check.py) — random
  sampling for $n \ge 7$.
- [`tests/test_verify.py`](tests/test_verify.py) — pinning the
  verifier against hand-checked small cases.
- [`tests/test_poly.py`](tests/test_poly.py) — *the* validation
  harness: every YES from `poly_mfas` is verified end-to-end against
  a transitive-tournament certificate.
- [`tests/test_path_fas.py`](tests/test_path_fas.py) — pins the formal
  Path-FAS/linear-forest equivalence and separating examples.
- [`tests/test_score_window.py`](tests/test_score_window.py) — pins the
  score-window solver against brute force and the separating examples.
- [`tests/test_score_window_dp_obstruction.py`](tests/test_score_window_dp_obstruction.py)
  — pins the reversed-matching family, component-entropy obstruction,
  active-bag signature collision, and visible-latent repair on the
  known witness.
- [`data/sweep_results.json`](data/sweep_results.json) — sweep output
  for $n \in [3, 6]$.
- [`data/lfo_sweep_3_6_corrected.json`](data/lfo_sweep_3_6_corrected.json)
  — corrected true-LFO sweep for all 74 non-isomorphic tournaments at
  $n \le 6$.
- [`data/lfo_random_n7_seed20260521.json`](data/lfo_random_n7_seed20260521.json)
  — corrected true-LFO random sample: 1500 tournaments at $n=7$.
- [`data/double_triangle_lfo_corrected.json`](data/double_triangle_lfo_corrected.json)
  — corrected 512-instance double-cyclic-triangle hub enumeration.
- [`data/lfo_score_buckets_n7.json`](data/lfo_score_buckets_n7.json) —
  exact non-isomorphic enumeration of the dominant $n=7$ score buckets.
- [`data/lfo_full_n7.json`](data/lfo_full_n7.json) — full exact
  non-isomorphic LFO census at $n=7$.
- [`data/lfo_combinatorial_no_analysis.json`](data/lfo_combinatorial_no_analysis.json)
  — structural analysis of the 18 exact combinatorial n=7 NO instances.
- [`data/lfo_extend_census_n8.json`](data/lfo_extend_census_n8.json) —
  exact non-isomorphic LFO census at n=8.
- [`data/lfo_minimal8_analysis.json`](data/lfo_minimal8_analysis.json) —
  structural analysis of the 572 exact order-8 minimal obstructions.
- [`data/lfo_reps_n8.jsonl`](data/lfo_reps_n8.jsonl) and
  [`data/lfo_reps_n9.jsonl`](data/lfo_reps_n9.jsonl) — compact exact
  representative sets.
- [`data/lfo_census_n9_results.jsonl`](data/lfo_census_n9_results.jsonl)
  and [`data/lfo_census_n9_results_summary.json`](data/lfo_census_n9_results_summary.json)
  — exact non-isomorphic LFO census at n=9.
- [`data/lfo_minimal9_summary.json`](data/lfo_minimal9_summary.json) —
  compact structural summary of the 5560 exact order-9 minimal
  obstructions.
- [`data/lfo_forbidden7_random_n8.json`](data/lfo_forbidden7_random_n8.json)
  — 200 random n=8 tournaments tested against induced n=7 NO
  containment.
- [`data/lfo_forbidden7_random_n9.json`](data/lfo_forbidden7_random_n9.json)
  — 20 random n=9 tournaments tested against induced n=7 NO
  containment.
- [`data/score_window_random_n10_seed20260522.json`](data/score_window_random_n10_seed20260522.json)
  — 2000 labeled random n=10 score-window probes.
- [`data/score_window_skew_probe_seed20260522.json`](data/score_window_skew_probe_seed20260522.json)
  — skew-score transitive-noise probes for n=12,16,20.
- [`data/score_window_skew_probe_n24_seed20260522.json`](data/score_window_skew_probe_n24_seed20260522.json)
  — skew-score transitive-noise probes for n=24.
- [`data/score_window_ff_compare_n24_seed20260522.json`](data/score_window_ff_compare_n24_seed20260522.json)
  — forced/flexible solver comparison on the n=24 light-noise regime.

## Reproducing the results

```bash
cd problems/path_matching_fas
python3 -m unittest tests/test_verify.py            # ~0.0s
python3 -m unittest tests/test_poly.py              # ~1 minute (n<=6 + 150 random)
python3 -m unittest tests/test_path_fas.py          # ~0.2s
python3 -m unittest tests/test_score_window.py      # ~0.2s
python3 -m unittest tests/test_score_window_dp_obstruction.py
python3 scripts/sweep.py --nmax 6                   # ~30s
python3 scripts/lfo_sweep.py --nmax 6               # ~35s
python3 scripts/lfo_random_sample.py --n 7 --samples 1500
python3 scripts/lfo_score_bucket.py --n 7           # exact dominant n=7 buckets
python3 scripts/lfo_score_bucket.py --n 7 --all-scores --out data/lfo_full_n7.json
python3 scripts/lfo_obstruction_analysis.py
python3 scripts/lfo_extend_census.py --out data/lfo_extend_census_n8.json
python3 scripts/lfo_minimal8_analysis.py
python3 scripts/lfo_representatives.py --target-n 9
python3 scripts/lfo_census_from_reps.py --out data/lfo_census_n9_results.jsonl
python3 scripts/lfo_minimal9_summary.py
python3 scripts/lfo_forbidden7_test.py --n 8 --samples 200 --out data/lfo_forbidden7_random_n8.json
python3 scripts/lfo_forbidden7_test.py --n 9 --samples 20 --out data/lfo_forbidden7_random_n9.json
python3 scripts/pending_state_probe.py --equivalence 4
python3 scripts/score_window_growth.py --n9-stride 500
python3 scripts/score_window_random_probe.py --mode uniform --ns 10 --samples 2000 --seed 20260522
python3 scripts/score_window_random_probe.py --mode skew --ns 12,16,20 --samples 200 --seed 20260522
python3 scripts/score_window_random_probe.py --mode skew --ns 24 --samples 100 --seed 20260522
python3 scripts/score_window_random_probe.py --mode skew --ns 24 --ps 0.02,0.05 --samples 50 --seed 20260522 --compare-forced-flexible
python3 scripts/ff_signature_probe.py --T '[[0,0,0,0,0,0,0],[1,0,0,0,0,0,0],[1,1,0,0,0,0,1],[1,1,1,0,0,0,0],[1,1,1,1,0,0,0],[1,1,1,1,1,0,0],[1,1,0,1,1,1,0]]' --depth 5 --mode active
python3 scripts/ff_signature_probe.py --census data/lfo_full_n7.json --depth 5 --mode visible
python3 scripts/wake_signature_probe.py --census data/lfo_full_n7.json --depth 5 --kind wake --horizon 1
python3 scripts/wake_signature_probe.py --census data/lfo_full_n7.json --depth 5 --kind visible --check extendability
python3 scripts/exchange_repair_probe.py --census data/lfo_full_n7.json --depth 5
python3 scripts/exchange_repair_probe.py --random skew --ns 10,12 --ps 0.02,0.05,0.1 --samples 20 --depth 5
python3 scripts/poly_mfas.py --nmax 6               # also ~30s — agreement check
python3 scripts/random_check.py --n 7 --samples 200 # ~10s
```

No external dependencies beyond the Python standard library.

## What this attack does NOT claim

- We do not resolve the **path-FAS** case; see "Status" above.
- We do not address the closely related **Problem 4.1** (triangle-free
  FAS) from the same paper.
- We do not improve the source paper's NP-hardness for the forest
  case (Theorem 1.1 of arXiv:2402.10782 stands).
- This folder does not claim that the matching-FAS algorithm is new.
  The proof is self-contained, but the novelty claim needs a prior-art
  check against tournament modular decomposition and FAS-variant
  literature.
