# Infrastructure-first plan: Pebbling a cartesian product

## Headline

The second counterexample-first target from `PARTIAL_PROBLEM_SCORES.md` is
Graham's pebbling conjecture:

> For connected graphs $G$ and $H$,
> $\pi(G \Box H) \leq \pi(G)\pi(H)$.

The famous stress test is the Lemke square. The original Lemke graph $L$ is
class 0: $|V(L)|=\pi(L)=8$. Therefore

$$
\pi(L)\pi(L)=64=|V(L\Box L)|.
$$

So the Lemke-square question is the clean dichotomy:

> Is $L\Box L$ class 0? If yes, Graham is tight here. If no, Graham fails.

Equivalently, a disproof via $L\Box L$ would be a 64-pebble configuration and
a root of $L\Box L$ such that the root is unreachable.

That is a finite certificate, but it is not a realistic primary deliverable
on one workstation. Specialists have already attacked this candidate with
strong exact reachability code and MILP/weight-function machinery. The sober
goal of this local project is:

1. build a trusted exact verifier for individual configurations;
2. pin and reproduce known Lemke data and published certificates;
3. produce a sortable corpus of hardest-looking 64-pebble configurations;
4. only then run a low-cost counterexample screen because the infrastructure
   exists anyway.

A 64-pebble counterexample remains the jackpot outcome. It should not drive
the budget.

## Statement audit

Local source:

- OPG slug: `pebbling_a_cartesian_product`
- OPG statement: $p(G_1 \Box G_2)\leq p(G_1)p(G_2)$.
- The literature uses both $p$ and $\pi$ for the pebbling number; this plan
  uses $\pi$.

Notation guardrail: older pebbling papers sometimes write $G\times H$ for
the Cartesian product. In code and notes, always store the product operation
as `cartesian`, and reserve `tensor`/`direct` for the other standard product
if it ever appears.

## Strongest counterargument

The naive headline "find an unsolvable 64-pebble configuration on $L\Box L$"
is a lottery ticket. The Lemke square is famous precisely because weak attacks
fail there. Cusack--Green--Bekmetjev--Powers developed serious reachability
and Lemke-graph code; Kenter--Skipper--Wilson developed product IP bounds;
Flocco--Pulaj--Yerger developed verifiable MILP weight-function certificates.
None of this has produced a Graham-disproving 64-configuration.

Therefore:

- counterexample search is a time-boxed screen, not the main research path;
- published and certified upper-bound reproduction comes before search;
- exact verifier correctness is the first mathematical deliverable;
- negative evidence is still useful if it is reproducible and well indexed.

## Audit Queue

These facts are load-bearing. Treat every one as provisional until it is
transcribed into `PEBBLING_PRODUCT_LITERATURE_NOTES.md` from a primary source.

| Claim | Status in this plan | What to pin |
|---|---|---|
| Original Lemke graph $L$ has $|V(L)|=\pi(L)=8$ and fails the 2-pebbling property. | working assumption | exact statement, graph drawing/edge list, and pebbling-number proof/citation |
| Every connected graph on at most 7 vertices has the relevant 2-pebbling property. | working assumption | connectedness convention and exact 2-pebbling definition |
| There are 22 Lemke graphs on 8 vertices and three minimal 8-vertex examples often denoted $L,L_1,L_2$. | working assumption | Cusack et al. statement, "minimal" order, graph6/edge lists |
| $L_1,L_2$ also have pebbling number 8. | working assumption | exact table or theorem statement |
| Gao--Yin prove Graham for known Lemke graphs with trees and complete graphs. | working assumption | exact family covered; do not oversell its force |
| Flocco--Pulaj--Yerger certify $\pi(L\Box L)\leq 96$. | audit target | actual theorem/certificate statement, not a table-image paraphrase |
| Kenter reports heuristic/numerical values around 85 for $L\Box L$. | heuristic only until certified | label as numerical evidence, not a theorem |
| Best post-2024 certified upper bound for $L\Box L$. | unknown | freshness check before implementation |

Bound records must distinguish:

- `certified_upper_bound`: rationally checkable certificate or theorem;
- `heuristic_upper_value`: solver output or floating-point computation;
- `folklore_or_secondary`: useful clue, not a claim.

No MILP or solver output is reported as a bound until a separate rational
checker verifies the certificate.

## Strategy Posture

The main strategy is not "beat Graham by search." It is:

1. Reproduce the factor graph facts, especially $\pi(L)=8$.
2. Build a trusted exact reachability verifier for individual configurations.
3. Build an independent rational certificate checker.
4. Reproduce at least one published certified upper bound at a reachable
   scale, then attempt $L\Box L$ if the solver stack can support it.
5. Use the verifier to rank 64-pebble configurations by hardness.
6. If a candidate looks unsolvable, require an exact certificate/log before
   calling it anything more than "hard."

The product-counterexample screen is valuable because it stress-tests the
verifier and generates examples. A null result is expected.

## Mathematical and Computational Guardrails

1. **Class-0 dichotomy.** Since $L$ is class 0, Graham for $L\Box L$ is
   equivalent to $L\Box L$ being class 0. Any certified upper-bound improvement
   toward 64 is evidence toward a genuine theorem, even if it does not close
   the case.

2. **Rooted formulation.** To refute Graham for fixed $G,H$, find
   $r\in V(G\Box H)$ and a configuration $C$ with
   $|C|=\pi(G)\pi(H)$ that is not $r$-solvable.

3. **The threshold is exactly 64 for $L\Box L$.** A 63-pebble unsolvable
   configuration is irrelevant to Graham. A 64-pebble unsolvable configuration
   is a disproof.

4. **Reachability is exponential in the hard cases.** Pebbling reachability and
   solvability variants are computationally hard; pebbling-number decision is
   even worse. Single-configuration unsolvability checks on a 64-vertex,
   64-pebble product may take hours. The verifier budget must reflect that.

5. **Dominance pruning must be stated precisely.** If $C\leq C'$ componentwise,
   every move legal from $C$ is legal from $C'$, and solvability is monotone:
   $C$ solvable implies $C'$ solvable; $C'$ unsolvable implies $C$ unsolvable.
   In forward search from $C_0$, do not expand a successor if it is
   coordinatewise dominated by an already-expanded state.

6. **2-pebbling failure is central but not evidence of product failure.** It is
   the reason the standard inductive proof route breaks. It is also the reason
   naive "bad slice" products often fail to become counterexamples: the local
   factor obstruction does not automatically glue across the product.

7. **Slice summaries are canonical data.** Every candidate record should store
   slice totals, slice supports, and per-slice 0/1/2-delivery flags relative
   to the projected root. This is the main sortable representation.

8. **Root orbits help modestly.** Compute $\operatorname{Aut}(L)$ and product
   root orbits, but expect a useful constant-factor reduction rather than a
   transformation.

9. **Relaxed flow models are nomination tools only.** Integer move-count
   constraints and floating-point MILPs may generate candidates. They do not
   certify unsolvability. Bounded-horizon CP-SAT is deferred until the rest of
   the pipeline is working and there is a specific reason to pay its modelling
   cost.

10. **Weight functions are upper-bound certificates.** They can prove
    $\pi(G)\leq N$. They do not prove counterexamples; they are the credible
    theorem-producing branch for shrinking the certified gap.

## Phase 0: literature and data audit

Deliverable: `PEBBLING_PRODUCT_LITERATURE_NOTES.md`.

Budget: half a day for the first pass; continue only when a missing fact blocks
implementation.

Tasks:

1. Transcribe the exact $L,L_1,L_2$ edge lists or graph6 strings from a
   primary source.
2. Pin $\pi(L)=\pi(L_1)=\pi(L_2)=8$, if true, with exact citations.
3. Pin the 2-pebbling and monotonic 2-pebbling support tables for these graphs.
4. Build `data/pebbling_product/known_bounds.csv` with columns:
   `product`, `root_orbit`, `value`, `kind`, `source`, `certificate_path`,
   `notes`.
5. Freshness check the best certified bound for $L\Box L$ and whether any
   post-2024 source reaches 64 or improves the certified 90s-range bounds.
6. Separate theorem/certificate statements from heuristic solver values.

Stop condition: exact graph data and a clean certified-vs-heuristic bounds
table for the minimal Lemke products.

## Phase 1: verifier and graph harness

Deliverables:

- `scripts/verify_pebbling_configuration.py`
- `scripts/pebbling_graphs.py`
- `data/pebbling_product/graphs/*.json`

Budget: two weeks for a trustworthy version, not one day. A one-day version is
only a prototype.

Verifier input:

- graph edge list or graph6;
- optional factor graphs plus `cartesian` product request;
- root vertex;
- pebble configuration.

Verifier checks:

1. graph is simple, undirected, and connected;
2. product graph is the intended Cartesian product;
3. configuration is nonnegative and has the claimed total size;
4. root index is valid;
5. exact `r`-reachability.

Verifier outputs:

- `invalid_input`: the graph, root, product convention, or configuration fails
  validation;
- `solvable`: the root is reachable, with an explicit move sequence;
- `unsolvable`: the search/proof has exhausted the relevant state space without
  hitting the stated resource limits;
- `inconclusive_within_budget`: the configured time, memory, node, or antichain
  limit was hit.

The `inconclusive_within_budget` outcome is expected on hard 64-pebble
configurations. It is not an error; it is a ranked-candidate result that can be
retried with a larger budget.

Implementation:

- Start with exact forward state search using identity-based deduplication;
  add coordinatewise dominance pruning later if hard candidates make it
  necessary.
- Emit an explicit move sequence for solvable configurations.
- For unsolvability or inconclusive outcomes, emit root, configuration,
  verifier version, explored-state count, deterministic state hash, and
  resource limits.
- Add a second engine inspired by the merge-pebbles method for cross-checking
  individual configurations. Do not expect it to compute $\pi(L\Box L)$ as a
  black box. This second engine is a correctness check on bookkeeping, not an
  independent mathematical certificate of unsolvability.
- Add ILP relaxations only as candidate generators or quick filters. Defer
  CP-SAT bounded-horizon modelling.

Acceptance tests:

1. reproduce known pebbling numbers for paths, cycles, and small cubes;
2. recompute $\pi(L)=8$ from scratch;
3. recompute $\pi(L_1)=8$ and $\pi(L_2)=8$, if the Phase 0 audit confirms
   those values and graph data;
4. recover known 2-pebbling violators for $L,L_1,L_2$;
5. verify product construction and root orbits on small examples;
6. produce deterministic logs so repeated runs agree.

Until the audited Lemke-factor pebbling numbers are reproduced locally, no
product-search result is trusted.

## Phase 2a: rational certificate checker

This phase comes before any $L\Box L$ certificate attempt.

Deliverable: an independent rational checker, e.g.
`scripts/check_pebbling_weight_certificate.py`.

The checker reads certificate data and verifies every weight-function
inequality with exact rational arithmetic. It must not call the same routines
that generated the certificate, except for shared graph-loading code.

Acceptance tests:

1. verify a textbook tree-strategy bound on a path, cycle, or cube;
2. reject a deliberately perturbed invalid certificate;
3. produce a compact human-readable failure report for the first failed
   inequality;
4. store accepted certificates as data, not screenshots or solver logs.

## Phase 2b: reproduce a certified upper bound

This is the hard gate before the Lemke-square screen.

Deliverables:

- `scripts/pebbling_weight_milp.py`
- certificate data under `data/pebbling_product/certificates/`
- a checker transcript from Phase 2a

Solver assumption:

- Default assumption: no commercial solver is available unless explicitly
  verified.
- If a Gurobi/commercial license is available, attempt the audited
  $L\Box L$ published certificate target.
- If only open-source solvers are available, first target a strictly smaller
  published example, such as a Lemke factor crossed with a path, small cycle,
  tree, or complete graph where the known value is reachable.

Goal hierarchy:

1. Reproduce the standard tree-strategy / weight-function framework.
2. Reproduce a small published certificate end to end with the Phase 2a
   checker.
3. Attempt the audited $L\Box L$ certified bound only after the small
   certificate succeeds.
4. If the $L\Box L$ reproduction does not succeed within two weeks, stop and
   pivot. Do not slide into Phase 3 as if the certificate gate passed.

Rules:

- Start with the standard tree-strategy / weight-function framework.
- Use commercial solvers only as optional accelerators.
- Do not report floating-point solver values as bounds.
- Non-tree strategies, lollipop strategies, and cubic strategies are later
  upgrades, not the first implementation.

Expected outcome: a local certificate pipeline that reaches the published
state of the art, or a clear reason why it does not.

## Phase 3: low-cost Lemke-square screen

This is a one-week time-box after Phase 1 and the Phase 2 gate. It is not the
main deliverable. If Phase 2b stalls at $L\Box L$ scale, run this screen only
as a verifier stress test and label the output as infrastructure, not as a
research result.

Primary product:

- $L\Box L$, with 64 pebbles.

Secondary products only if the first screen is cheap:

- $L\Box L_1$;
- $L\Box L_2$;
- $L_1\Box L_1$;
- $L_1\Box L_2$;
- $L_2\Box L_2$.

Search strategy:

1. Compute product root orbits.
2. Reproduce baseline slice templates already suggested by the literature:
   heavy bad slices, multiple medium bad slices, low-support configurations
   far from the root, and perturbations of known factor violators.
3. Store every candidate in canonical slice-summary form.
4. Verify candidates subject to explicit resource limits.
5. Rank by verifier result, difficulty, `inconclusive_within_budget` logs,
   heuristic disagreement, support pattern, and distance profile.

Expected result: no counterexample. Useful output is
`data/pebbling_product/hard_64_configs.csv` plus candidate files and logs.

## Phase 4: candidate generation by optimization

This phase generates harder examples for the verifier. It does not certify
anything.

Deliverable: `scripts/search_pebbling_product_configs.py`.

Model families:

1. **Distance-weight minimization.** Generate configurations with poor simple
   rooted weights under support constraints.
2. **Slice-deficit MILP.** Choose slice totals/supports that avoid easy
   0/1/2-delivery routes based on factor data.
3. **Local search.** Mutate candidates inside the 64-pebble simplex, scored by
   exact-verifier difficulty and slice summaries.
4. **Bounded-horizon CP-SAT, deferred.** Do not build this until everything
   else is working and there is a concrete modelling question it answers.
   Move ordering, intermediate states, and horizon symmetry are a separate
   research-grade modelling problem.

Hard rule: every nominated candidate is passed to the exact verifier before
being recorded as anything more than a heuristic candidate.

## Phase 5: improve certificates

This is the credible theorem-producing branch.

Goal hierarchy:

1. Improve or simplify a reproduced certificate for $L\Box L$.
2. Produce a rationally checked bound below the best certified value from
   Phase 0.
3. Extend the same certificate method to the other minimal Lemke products.
4. Only after tree-strategy reproduction succeeds, test non-tree/lollipop/cubic
   strategies.

Do not describe "closing the gap to 64" as a budgeted stretch goal. That is
the hard open problem for the canonical candidate.

## Deferred: broader graph-pair search

The old Phase 6 is deferred. Searching all 8- or 9-vertex non-2-pebbling graph
pairs is a separate project.

If broader search is ever attempted, restrict it to a tiny pre-screen:

1. import only graph pairs with known $\pi(G)$ and $\pi(H)$;
2. skip pairs covered by positive theorems;
3. compute root orbits and cheap slice summaries;
4. run only bounded candidate generation, not full product pebbling-number
   computation.

## Expected Outcomes

This is a high-risk infrastructure project, not a high-yield disproof project.
The likely outcomes, in descending order, are:

1. a trusted verifier that reproduces $\pi(L)=8$ and small-graph facts;
2. an end-to-end certificate checker plus a reproduced small published
   certificate;
3. a reproduced certified $L\Box L$ upper bound, if the solver stack is strong
   enough;
4. a modest certified improvement;
5. a 64-pebble disproof, which should be treated as essentially a jackpot.

If the intended time budget cannot tolerate stopping after item 1 or 2, choose
a different problem from the shortlist.

## Revised Budget

| Task | Realistic budget | Stop condition |
|---|---:|---|
| Phase 0 literature/data audit | 0.5-1 day | Exact graph data and certified-vs-heuristic bounds table. |
| Verifier prototype | 1-2 days | Runs on toy examples; not trusted yet. |
| Trusted verifier + graph harness | 1-2 weeks | Reproduces audited Lemke-factor pebbling numbers and known factor violators. |
| Phase 2a rational checker | 2-4 days | Accepts a small valid certificate and rejects a perturbed one. |
| Phase 2b small certificate reproduction | 1 week | End-to-end published small example checked rationally. |
| Phase 2b $L\Box L$ reproduction attempt | up to 2 weeks | Reproduced certified bound, or stop/pivot report. |
| Lemke-square slice screen | 1 week | Only after the gate, or clearly labelled verifier stress test. |
| Optimization candidate generation | 1-2 weeks | Harder candidates than templates, or no improvement. |
| Certificate improvement attempt | open-ended | Any rationally checked improvement is a meaningful result. |
| Broader graph-pair search | deferred | Separate project. |

## Failure Modes

- Treating the 64-configuration search as the main deliverable.
- Confusing $\pi(G)$ with rooted $\pi(G,r)$.
- Searching for 63-pebble obstructions on $L\Box L$.
- Accidentally using tensor/direct product instead of Cartesian product.
- Calling floating-point or heuristic MILP output a bound.
- Checking a certificate with substantially the same code that produced it.
- Failing to reproduce a certified bound at $L\Box L$ scale and quietly moving
  on as if Phase 2b passed.
- Having no commercial solver and still budgeting as though a commercial-solver
  certificate can be reproduced.
- Trusting a relaxed integer-flow solution that has no executable move order.
- Getting `inconclusive_within_budget` on every candidate produced by the
  screen; this is foreseeable and must be recorded, not treated as a crash.
- Treating 2-pebbling failure as evidence of product failure.
- Applying the merge-pebbles algorithm at 64 vertices as if it scales like the
  8- or 9-vertex Lemke computations.
- Underestimating single-configuration unsolvability checks.
- Missing modest but useful root-orbit reductions.
- Failing to record verifier version, explored-state count, and deterministic
  state hash for hard candidates.
- Importing path notation incorrectly: some papers index paths by length and
  others by vertex count.
- Reporting a candidate without factor graphs, product convention, root, and
  full configuration.

## Revised First Work Items

1. Create `PEBBLING_PRODUCT_LITERATURE_NOTES.md` and pin every load-bearing
   Lemke fact from primary sources.
2. Encode $L,L_1,L_2$, then reproduce their audited pebbling numbers before
   touching products.
3. Implement the exact verifier with deterministic logs, identity-based
   deduplication, and `inconclusive_within_budget`; keep coordinatewise
   dominance pruning as a later optimization.
4. Add `known_bounds.csv` with certified/heuristic/folklore separation.
5. Write the independent rational certificate checker and validate it on a
   small example.
6. Reproduce a published small certificate, then attempt the $L\Box L$ bound
   only if the solver stack is adequate.
7. Run the one-week slice-template screen and store ranked hard
   configurations.
8. Decide whether the next useful branch is certificate improvement or better
   candidate generation.

Primary success is credible local infrastructure plus a reproduced certified
bound. Secondary success is a high-quality hard-candidate corpus. A
Graham-disproving 64-configuration is possible in principle but should be
treated as an unlikely byproduct, not the plan.

## Source Links for the Audit

- Local review: `data/reviews/pebbling_a_cartesian_product.json`
- OPG scrape: `data/problems.json`, slug `pebbling_a_cartesian_product`
- Kenter--Skipper--Wilson 2020:
  https://www.sciencedirect.com/science/article/pii/S0304397519306206
- Cusack--Green--Bekmetjev--Powers 2019:
  https://digitalcommons.hope.edu/faculty_publications/1486/
- Gao--Yin 2017:
  https://www.sciencedirect.com/science/article/pii/S0012365X16302916
- Flocco--Pulaj--Yerger 2024:
  https://www.sciencedirect.com/science/article/pii/S0166218X24000027
- Pleanmani 2020:
  https://digitalcommons.georgiasouthern.edu/tag/vol7/iss1/1/
- Xia--Pan--Xu--Cheng 2017:
  https://arxiv.org/abs/1705.00191
- Yang--Yerger--Zhou 2024/2025:
  https://arxiv.org/abs/2310.00580
