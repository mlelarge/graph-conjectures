# `problems/` — Onboarding Overview

A reader's guide to the eight problem subfolders under `problems/`.
Each section is self-contained: the conjecture, the current status, the folder layout,
the files to open first, and the artifacts worth knowing about. Compiled 2026-05-17
from per-folder reconnaissance by a team of reviewer agents.

## At-a-glance index

| Subfolder | Conjecture / topic | State | Headline artifact |
|---|---|---|---|
| `3_decomposition_conjecture/` | Hoffmann-Ostenhof 3-decomposition of cubic graphs | Open; structural reductions advancing through `n ≤ 14` | `data/n14_full.summary.json` |
| `arc_disjoint_strong_spanning_subdigraphs/` | Bang-Jensen–Yeo SAD conjecture (WC3: `K = 3`) | Open; meaningful negative search + EC-log theorem proved | `paper/draft_v1.md`, `team/04_ec_log_proof.md` |
| `crossing_numbers_and_coloring/` | Albertson's conjecture (`cr(G) ≥ cr(K_t)` when `χ(G) ≥ t`) | Open at `t ≥ 25`; three finished side-papers | `deliverables/D8_paper/`, `D15_…/`, `D16_…/` |
| `directed_path_minimum_outdegree/` | Cheng–Keevash / Thomassé directed-path conjecture | Active; `δ = 3` and `δ = 4` for `n ≤ 11` closed | `docs/k3_hand_proof.md`, `docs/k4_n11_proof.md` |
| `earth_moon_problem/` | Ringel's biplanar chromatic number `χ_EM ∈ [9, 12]` | Open; Fork C probe ruled out one closure path | `docs/phase6_discharge_attempt.md` |
| `pebbling_cartesian_product/` | Graham's pebbling conjecture on the Lemke square | Terminal; `π(L □ L) ≤ 246` (rooted ≤ 106) | `docs/terminal_report.md` |
| `positive_square_energy_equality/` | Akbari–Kumar–Mohar–Pragada–Zhang Conjecture 9.2 for 2-trees | Open at the "slot-shift" wall; 40-page paper drafted | `paper/paper.pdf` |
| `unit_vector_flows/` | Jain's S²-flow conjecture for bridgeless graphs | Finite theorem proved for snarks on `n ≤ 28` | `THEOREM.md`, `paper/main.tex` |

## How to read this document

Each section below follows the same five-part shape:

1. **Conjecture** — the precise mathematical statement.
2. **Status** — what is proved, what was refuted, what is still open here.
3. **Layout** — one line per top-level subfolder.
4. **Start here** — 2–4 ordered file paths to open first.
5. **Notable artifacts** — papers, certificates, key scripts, recorded negative results.

If you only have ten minutes, the top of each section's "Start here" list is the right
entry point.

## 1. `3_decomposition_conjecture/`

### Conjecture

**Hoffmann-Ostenhof (2011), OPG (2017).** Every connected cubic graph `G` has a
decomposition `E(G) = T ⊔ C ⊔ M` where `T` is a spanning tree, `C` is a 2-regular
subgraph (disjoint union of cycles), and `M` is a matching. Both `C` and `M` may be
empty. Equivalently, vertices split into `V_C` (`T`-degree 1, on a cycle of `C`), `V_M`
(`T`-degree 2, matched by `M`), `V_T` (`T`-degree 3, pure tree), with
`|V_C| = |V_T| + 2`.

### Status

Open. Partial reductions are in hand:

- **Lemma 1 (bridge reduction)** proved; sub-lemma 1' verified computationally on
  subcubic graphs up to `n = 11`.
- **Antichain Coverage Conjecture refuted at `n = 12`** (10 out of 1670 oriented
  2-pole sides cannot be replaced by gadgets in the `n ≤ 10` lattice); failures are
  absorption-universal and handled via compatibility replacement.
- **`n = 14` sweep complete:** 15,176 of 15,178 oriented 2-pole sides are
  trace-contained in the `n ≤ 12` lattice; the remaining 2 are absorbed by the bridge
  lemma.
- **Live gap:** the Universal Replacement Conjecture — every 2-edge-cut side of order
  `≥ 12` is either trace-contained by a smaller gadget or compatibility-universal.

### Layout

- `docs/` — strategic plan, minimal-counterexample theory, proof logs, literature.
- `scripts/` — verifiers (`decomposition.py`), SAT interface, lattice builder, sweeps.
- `data/` — computed gadget lattices and failure classifications (JSON).
- `tests/` — 33 regression tests (`K₄`, `K₃,₃`, Petersen, prism, trace sets).
- `external/` — placeholder.

### Start here

1. `README.md` — current status and key results.
2. `docs/plan.md` — vertex-type reformulation, reductions, 7-phase attack plan.
3. `docs/minimal_counterexample.md` §1–3 — boundary-trace formalism + bridge lemma.
4. `scripts/decomposition.py` — trust-root verifier and brute-force finder.

### Notable artifacts

- `data/gadget_lattice_2pole_n12_both.json` — 274 oriented gadgets, 59 trace classes.
- `data/failure_structural_classification_n12.json` — structural breakdown of the
  10 `n = 12` failures.
- `data/n14_full.summary.json` — traces for all 15,178 `n = 14` oriented sides.
- `scripts/full_replacement_sweep.py` — reproducible, resumable sweep driver.

## 2. `arc_disjoint_strong_spanning_subdigraphs/`

### Conjecture

**Bang-Jensen–Yeo (2004).** There exists an absolute constant `K` such that every
`K`-arc-strong digraph admits a *strong arc decomposition* (SAD): a 2-coloring of arcs
into two color classes each spanning and strongly connected.

**Working Conjecture (WC3) in this project:** `K = 3`. All known obstructions sit at
arc-connectivity 2 — `S₄`, squares of even directed cycles, the four semicomplete
exceptions of Bang-Jensen–Gutin–Yeo (2020), and the 2-arc-strong split exceptions of
Ai–He–Li–Qin–Wang (2024).

### Status

Open. Phase 3 v2 closed with a meaningful negative result and two side-theorems:

- **Negative search:** 4,613 verified 3-arc-strong digraphs generated across four
  vehicles (template gluings, Eulerian constructions, laminar cut systems); zero UNSAT
  on both ILP and SAT backends. Either WC3 holds, or a counterexample lies outside
  the structured families tested at `n ≲ 30`.
- **Theorem (EC-log).** Every Eulerian digraph `D` with `λ(D) ≥ 5 log₂ n` admits a
  SAD. Proof via reduction to Karger cut counting + first-moment method.
- **Theorem (CL1, controlled-lifting lemma).** Bilateral SAD decomposition for
  near-split digraphs.

### Layout

- `code/` — cross-checked ILP (PuLP+CBC) and SAT (pysat+CaDiCaL) verifiers; generator
  modules (`glue.py`, `eulerian.py`, `laminar.py`); benchmark suite.
- `paper/` — `draft_v1.md`, `findings.md`, `outline.md`, `review_v1.md`.
- `team/` — 33 agent outputs (charter, structural program, verifier design, EC-log
  proof, phase reports v1/v2, lifting-lemma proofs, hard-case audits, recoloring,
  termination, F3 verification, parallel-closure status).

### Start here

1. `attack_plan.md` — roadmap, WC3 definition, EC-log statement, phased milestones.
2. `review.md` — auditor's sign-off on EC-log and literature corrections.
3. `paper/findings.md` — honest knowledge state: what is proved vs. open.
4. `team/07_phase3_report_v2.md` — phase 3 results in full (4,613 instances, vehicles,
   stop conditions).

### Notable artifacts

- `team/04_ec_log_proof.md` — EC-log proof.
- `team/11_cl1_proof_v1.md` — CL1 lifting-lemma proof.
- Validation suite (`code/`): `S₄`, cycle squares, semicomplete and split exceptions
  as UNSAT benchmarks; small SAT cases.
- `code/run_phase3_v2.py` — explicit families enumerated in the negative search.

## 3. `crossing_numbers_and_coloring/`

### Conjecture

**Albertson (2007).** For every graph `G` with chromatic number `χ(G) ≥ t`,
`cr(G) ≥ cr(K_t)`. A metric strengthening in the lineage of Hadwiger and (refuted)
Hajós.

### Status

Open at `t ≥ 25`. Cranston (2025, arXiv:2512.08020) closes `t ≤ 24` via repeated
applications of the Crossing Lemma.

- **Track A (residual hunt).** Cranston's Theorem 2 isolates pairs
  `(t, |G|) ∈ {(25,48), (26,50), (26,51)}` as the only possible counterexamples. The
  Ore-order congruence `|V(G)| ≡ 1 (mod k−1)` eliminates `(25,48)` and `(26,50)` from
  the Ore-critical family; only `(26,51)` survives. Demoted from the headline target.
- **Track B (structural).** R5a — sharpness of Claim 3.7 in Fox–Pach–Suk — closed on
  2026-05-17. D8 proves the FPS degree threshold `δ = 9/8` is sharp within the
  Vizing–Gupta + semi-random construction, via the witness identity
  `f_{2b}(4/7, δ) − 9/16 = 12(δ − 9/8)² / [7(4δ − 1)]`. The constant `9/16` is
  binding in this framework. New front-runners: R2c (min-degree-refined Crossing
  Lemma) and R3.6 (fractional / list / DP Albertson).

### Layout

- `docs/` — planning, reviews, literature audit.
- `work/` — nine roles (teams) with per-role memos.
- `deliverables/` — published papers and supporting computation, indexed `D2`–`D18`.

Deliverable highlights:

- `D2_literature_verification.md` — audit of Cranston, Kostochka–Yancey,
  Büngener–Kaufmann thresholds.
- `D3_R5a_reconstruction.md` — faithful reconstruction of FPS Claim 3.7.
- `D4_ore_26_51/` — Ore-graph enumeration at `(26,51)`.
- `D5_sympy_freedelta/` — SymPy verification of Case 2b monotonicity / witness
  identity.
- `D8_paper/` — `sharpness_9_8.pdf` (7 pages, theorem-grade); plus the retracted
  `tighter_fps_RETRACTED.pdf` with preserved error analysis.
- `D12_ore_c3/` — Ore composition tables; lower bound for the C3 construction.
- `D13_r2c_attack/`, `D14_r36_attack/` — in-progress attack memos.
- `D15_list_albertson_paper/` — `list_albertson_le_18.pdf` (9 pages): list-chromatic
  Albertson for `t ≤ 18`.
- `D16_expander_crossing_paper/` — `expander_crossing.pdf` (9 pages): explicit
  bisection-width Crossing Lemma for spectral expanders.
- `D17_submission_packets/` — bundling and journal recommendations.
- `D18_combined_observations/` — withdrawn (false observation at `t = 5`); preserved.

### Start here

1. `docs/plan.md` v4 — 12-month roadmap; six routes, three tracks, four open
   questions. Begin at "Honest tractability verdict".
2. `docs/review_v3.md` — senior post-team audit; the "Main correction" kills the
   false `(25,48)` Ore corner.
3. `deliverables/D8_paper/README.md` — R5a context, witness identity, retraction
   notes.
4. `work/01_principal_lead/INTEGRATION.md` — role contract, R-route ownership, R5a
   closeout + next steps.

### Notable artifacts

- Closed: `D8` `sharpness_9_8.pdf` (theorem-grade).
- Published-ready: `D15` and `D16` papers.
- Refuted/withdrawn: `D18`.
- Cite-grade audit: `D2_literature_verification.md` (Cranston's three pairs;
  Kostochka–Yancey edge bounds 588/638/650; BK crossing threshold 6.77 n vs.
  Cranston's 6.95 n).

## 4. `directed_path_minimum_outdegree/`

### Conjecture

**Cheng–Keevash Conjecture 1 (attributed to Thomassé).** Every oriented graph with
minimum out-degree `δ` contains a directed simple path of length `2δ` (length =
number of arcs; vertex-simple).

### Status

Active; recent significant closures.

| `δ` | Status |
|---|---|
| 1–2 | Closed (trivial / Cheng–Keevash 2024) |
| 3 | **Closed**, hand proof, all `n ≥ 7` |
| 4, `n = 10` | **Closed**, hand + computer-aided; audited |
| 4, `n = 11` | **Closed**, computer-aided; two independent pipelines agree |
| 4, `n ≥ 12` | Open; miner ready, computationally demanding |
| `δ ≥ 5` | Open |

For `δ = 4, n = 10`: Cheng–Keevash Lemma 7 + forced-arc derivation + exhaustive
enumeration on the `(2,2,1,1)` score profile. For `n = 11`: 32 configurations,
117.9 M completions, zero obstructions.

### Layout

- `docs/` — proof manuscripts (`k3_hand_proof.md`, `k4_n10_proof.md`,
  `k4_n11_proof.md`, `k4_partial_appendix.md`), `literature_notes.md`, `plan.md`.
- `data/` — audit outputs, certificates, path tables (e.g., `k4_n10_certificate.json`,
  10 MB).
- `scripts/` — miners (`k4_local_miner.py`, `k4_score_profile_miner.py`), independent
  re-implementations (`k4_score_profile_independent_check.py`), verifiers
  (`k4_verify_certificate.py`, `verify_directed_path_counterexample.py`).

### Start here

1. `README.md` — status table + reproducer commands.
2. `docs/plan.md` (attack plan, status audit, verified literature facts).
3. `docs/k3_hand_proof.md` — simplest closed case; Lemma 7 + cyclic-closure technique.
4. `docs/k4_n10_proof.md` (theorem + reductions).

### Notable artifacts

- Lemma 7 + oriented average bound (core structural tool from Cheng–Keevash 2024).
- Two independent miners agree on all 24 `(S,T)` configurations / 3,664 completions
  for `n = 10`.
- Mechanical certificate verifier: hash, 4-outregularity, forced-arc compliance,
  witness paths.
- `k4_score_profile_miner.py 12` is the next computational target (~2–4 h).

## 5. `earth_moon_problem/`

### Conjecture

**Ringel (1959).** Define a graph as *biplanar* if its edges can be partitioned into
two planar subgraphs. What is the maximum chromatic number `χ_EM` of a biplanar
graph? Known bounds: `9 ≤ χ_EM ≤ 12` (Sulanke/Gardner 1980 lower; Heawood 1890
upper). The folklore `χ_EM = 9` is unproven.

### Status

Open. Two complementary tracks:

- **Disprove `χ_EM = 9`** by exhibiting a 10-chromatic biplanar graph. Headline
  candidate `C₇ ⊗ K₄` (28 vertices, `χ = 10`, `K_9`-free) ruled **UNSAT** after
  9.7 h (Phase 4, May 2026).
- **Tighten `χ_EM ≤ 11`** via density: `K_9`-free 12-critical biplanar graphs need
  `≥ (65 n − 54) / 11` edges by Kostochka–Yancey, but biplanarity caps them at
  `6 n − 12`. The gap closes for `n ≥ 78`; further `K_9`-free strengthening would
  tighten it.

**Recent (commit 204282a, May 16):** Fork C probe — a non-saturated `K_7` witness on
partition `(7,3,1)` (14 vertices, 56 edges) is biplanar in 0.011 s, even though
`K_7 + K̄_5` is not. This blocks one Q0-closure path; the discharge argument now
branches to Forks A/B (structural Gallai arguments on low-degree vertices).

### Layout

- `docs/` — Phase 6 discharge attempt (50+ pages), literature notes, plan,
  upper-bound audit, paper skeleton.
- `scripts/` — biplanar oracle (SMS wrapper), profile enumerator, cycle-blowup
  generator, SAT runner.
- `data/` — test runs: `c7_k4` (28 V, 9.7 h UNSAT), `candidate1/2`, `new_c5_a/b`.
- `external/sat-modulo-symmetries` — KSS 2023 SAT-modulo-symmetry framework
  (submodule).

### Start here

1. `README.md` — 2-minute problem statement and status.
2. `docs/plan.md` — Phase structure (oracle, regression, mining, upper bounds).
3. `docs/phase6_discharge_attempt.md` — current frontier: 89-vertex 12-critical
   structure, Gallai forest on low vertices, the Fork C `K_7` finding.
4. `data/c7_k4/README.md` — how `C₇ ⊗ K₄` was ruled out; scaling vs. `C₅` cases.

### Notable artifacts

- `biplanar_check.py` — flexible biplanarity tester (SMS wrapper).
- `phase6_discharge_attempt.md` — sections 7.15–7.16 document Forks A/B/C.
- Fork C result: `K_7` + 7 cyclic 5-neighbours (n = 14, m = 56) is biplanar.
- `c7_k4` run: 34,834 CPU s, 64 M propagator calls, 3.84 M Kuratowski clauses.

## 6. `pebbling_cartesian_product/`

### Conjecture

**Graham's pebbling conjecture.** For connected graphs `G, H`:
`π(G □ H) ≤ π(G) · π(H)`. This project targets the **Lemke square** `L_fpy □ L_fpy`
(`π(L) = |V(L)| = 8`), the classical stress test that would yield a 64-pebble
counterexample if the conjecture fails on it. Rational weight-function certificates
via column generation produce upper bounds.

### Status

**Terminal — clean stopping point.** Four verified deliverables:

- Global bound: `π(L_fpy □ L_fpy) ≤ 246` (rational, re-checkable).
- Rooted: `π(·, (v₁, v₁)) ≤ 106` (sharpens Hurlbert 2017's 108).
- Negative pricing: the bottleneck orbit `(0,0)` is LP-optimal under two bounded
  strategy classes; no improving column found.
- FPY ingestion bridge with current Flocco–Pulaj–Yerger source works; reproducing
  their published `≤ 96` bound is blocked on Gurobi or author JSON (missing dual
  multipliers; CSV ambiguity vs. published artefacts).

No FPY 96 reproduction or 64-pebble counterexample search — scope limits documented
in the terminal report.

### Layout

- `docs/` — `terminal_report.md` (entry point), `phase2b_status.md` (FPY blocker),
  `lp_improvement_log.md`, `literature_notes.md`, `plan.md`.
- `data/pebbling_product/` — 22 root-orbit certificates (JSON),
  `root_orbit_bounds.csv`, `known_bounds.csv`, `L_fpy.json`.
- `scripts/` — 19 Python tools: exact verifier, rational checker, LP harness,
  column-generation oracles (paths, Y-tree, trident, Π-tree), FPY adapter, orbit
  aggregator.
- `tests/` — 16 pytest modules (101 tests, all passing).
- `external/` — gitignored FPY clone directory.

### Start here

1. `docs/terminal_report.md` — headline results, comparison table, FPY blocker.
2. `README.md` — 2-minute orientation; reproduction commands.
3. `scripts/check_pebbling_weight_certificate.py` — the verifiable core (~700 lines).
4. `data/pebbling_product/root_orbit_bounds.csv` — 22 orbits, bounds 68–246.

### Notable artifacts

- `Hurlbert_path_augmented_v1v1_le106.json` — sharpened rooted bound.
- `path_orbit_0_0_max_len7.json` — bottleneck certificate (orbit `(0,0)` at 246).
- `price_tree_strategy.py` — pricing oracle, 196 M+ nodes explored at depth ≤ 7.
- `fpy_probe.py` — live FPY round-trip self-test.

Last updated 9 May 2025. Self-contained, independently verified; future work options:
(i) run FPY's MILP with Gurobi, (ii) widen the priced strategy class, (iii) leave 246
as standalone.

## 7. `positive_square_energy_equality/`

### Conjecture

**Akbari–Kumar–Mohar–Pragada–Zhang Conjecture 9.2** (arXiv:2506.07264, June 2025).
For a connected graph `G` of order `n`:

- (i) `s⁺(G) = n − 1` iff `G` is a tree.
- (ii) `s⁻(G) = n − 1` iff `G` is a tree or a complete graph `K_n`.

Here `s±(G)` is the sum of squares of the positive (resp. negative) adjacency
eigenvalues. Refines Elphick–Farber–Goldberg–Wocjan (`s± ≥ n − 1`).

### Status

Conjecture 9.2 is open in general. For **2-trees** (maximal chordal, treewidth 2)
substantial progress is in:

- **Unconditional proofs.** Books `B_k`:
  `δ⁻(B_k) = 2 − 4 / (√(8k+1) + √(8k−7))`. 2-paths asymptotic:
  `δ⁻_∞(L) = (32π − 27√3) / (12π) ≈ 1.4262` per vertex (Szegő–Cesàro via Stieltjes
  transforms, Phases 10–11). Lemmas B1 and B1⁺ (Rayleigh bounds).
- **Finite-`n` rigorous.** `δ⁻(L_n) ≥ 17/16` for `n ∈ [4, 2000]` via
  Demmel–Kahan a-posteriori certificates.
- **Headline open.** "(L') existential ear-selection lemma" — does every 2-tree
  admit a simplicial degree-2 vertex with `δ± ≥ 17/16`?
- **The wall.** Condition (b) — the slot-shift sum bound (O12.2). Estimated
  6 person-months to 2 years.

### Layout

- `paper/` — 40-page LaTeX submission draft (7 sections + appendices); `\stub{}`
  markers for unfilled proofs.
- `docs/` — 30 technical notes: phase logs, failure-mode catalogues (F1–F15),
  structural analyses of books / 2-paths / bad-ears.
- `scripts/` — corpus builders, moment calculations, Stieltjes transforms,
  Demmel–Kahan verification.
- `tests/` — 14 regression test files (519 passing tests).
- `data/` — JSON fixtures: 2235-record max-degsum census, 1795-graph corpus,
  1063+ graph-family database.

### Start here

1. `README.md` — executive summary; verdict after Phase 12 reviews.
2. `docs/plan_v14.md` — strategic map of what works, what failed, why.
3. `paper/paper.pdf` (rebuild via `make` in `paper/`).
4. `docs/corollaries_AB.md` — two short corollaries (claw-free, diameter ≤ 2).

### Notable artifacts

- Phase 8 Lemma B1 + Phase 12.A Lemma B1⁺ (Rayleigh bounds).
- Phase 10–11 asymptotic: `lim_n I(L_n, v*) = I_∞(L) ≈ 1.0157` via spectral measure
  theory.
- Books closed form; 2-paths asymptotic via half-line Stieltjes + Portmanteau.
- Failure modes (Appendix B): F14 (trace-identity reformulation does not decouple
  the slot-shift wall); F15 (Theorem 8.1 hypothesis empirically inapplicable to
  2-trees).
- Workstream has pivoted from research-attack to paper-writing.

## 8. `unit_vector_flows/`

### Conjecture

A **unit vector flow** assigns to each edge of a graph a unit vector in `ℝ³` (a point
on `S²`) such that the oriented sum of incident vectors at every vertex is zero
(Kirchhoff conservation). **Jain's surviving conjecture** (2007):

> Every bridgeless graph admits an `S²`-flow.

A related quaternion-flow conjecture was recently disproved by Ulyanov (2026).

### Status

A finite theorem, rigorously proved by computer assistance:

> **Theorem.** Every nontrivial snark on at most 28 vertices admits an `S²`-flow.

All 3,247 nontrivial snarks `n ≤ 28` carry independently replayable
interval-Krawczyk certificates: numerical witness (Levenberg–Marquardt on the
polynomial Kirchhoff system) + 50-digit interval verification.

Jain's conjecture itself remains open for general bridgeless graphs.

Preprint finished (`paper/main.tex`, 5 sections); covers algorithm, enumeration,
and negative results on symmetric flower-snark constructions.

### Layout

- `docs/` — `plan.md` (phases 1–4), literature review, flower-snark analysis,
  cycle-double-cover obstruction notes.
- `scripts/` — `catalogue.py` (snark enumeration + SAT filter), `sweep.py`
  (numerical witness), `interval.py` (Krawczyk certifier), `verify_sweep.py`
  (replay verifier).
- `data/` — 3,247 snark catalogue (g6), witness JSON, 3,247 interval certificates
  (schema v2), manifest with SHA-256 provenance.
- `tests/` — 41 regression tests; negative calibration confirms rejection of bridged
  graphs.
- `paper/` — LaTeX preprint (intro, preliminaries, certification pipeline, finite
  theorem, CDC obstructions).

### Start here

1. `THEOREM.md` — formal statement, enumeration provenance, Krawczyk algorithm,
   replay protocol.
2. `README.md` — context, headline table, reproduction instructions.
3. `docs/plan.md` — phase roadmap.
4. `paper/main.tex` — full certification algorithm and limitations.

### Notable artifacts

- Theorem statement: `THEOREM.md` lines 5–26.
- `Makefile` targets: `verify`, `verify-certs`, `catalogue`, `sweep`, `certs`.
- Certificate manifest: `data/catalogues/nontrivial_snarks_n10_to_28.manifest.json`.
- Replay verifier: `scripts/verify_sweep.py` (recomputes Krawczyk from scratch).
- Negative result: `docs/flower_snarks.md` (symmetric constructions fail for
  `J_{2k+1}`).
- Quick reproduction: `make -C problems/unit_vector_flows verify-certs` (~70 min).
