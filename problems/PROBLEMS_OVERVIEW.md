# `problems/` — Onboarding Overview

A reader's guide to the eight problem subfolders under `problems/`. Each
section below is **self-contained**: it states the conjecture with every
nonstandard term defined inline, then labels every claim as **PROVED /
OPEN / REFUTED / WITHDRAWN** (or *computer-checked at n ≤ X*, when the
status rests on finite-case enumeration rather than a proof). Compiled
2026-05-18 from per-folder reconnaissance plus an independent
correctness audit and a fix-verification pass; the per-folder
`CORRECTNESS_REVIEW_2026_05_18.md` and `FIX_VERIFICATION_2026_05_18.md`
files record the audit chain.

## At-a-glance index

| Subfolder | Conjecture / topic | State | Headline artifact |
|---|---|---|---|
| `3_decomposition_conjecture/` | Hoffmann-Ostenhof 3-decomposition of cubic graphs | OPEN; Lemma 1 PROVED; `n ≤ 14` sweep computer-checked | `data/n14_full.summary.json` |
| `arc_disjoint_strong_spanning_subdigraphs/` | Bang-Jensen–Yeo SAD conjecture (WC3: `K = 3`) | OPEN; EC-log theorem PROVED (`C = 6, n₀ = 3`); 4,613-instance negative search | `paper/draft_v1.md`, `team/04_ec_log_proof.md` |
| `crossing_numbers_and_coloring/` | Albertson's conjecture (`cr(G) ≥ cr(K_t)` when `χ(G) ≥ t`) | OPEN at `t ≥ 25`; Cranston PROVED `t ≤ 24`; D8 / D16 PROVED; D15 / D18 WITHDRAWN | `deliverables/D8_paper/`, `D16_…/` |
| `directed_path_minimum_outdegree/` | Cheng–Keevash / Thomassé directed-path conjecture | `δ = 3` PROVED for all `n ≥ 7`; `δ = 4` PROVED at `n = 10`, computer-verified at `n = 11`; `δ ≥ 5` OPEN | `docs/k3_hand_proof.md`, `docs/k4_n10_proof.md` |
| `earth_moon_problem/` | Ringel's biplanar chromatic number `χ_EM ∈ [9, 12]` | OPEN; folklore `χ_EM = 9` neither proved nor refuted; `C_7[K_4]` ruled out by single-tool SMS | `docs/phase6_discharge_attempt.md` |
| `pebbling_cartesian_product/` | Graham's pebbling conjecture on the Lemke square | OPEN at the conjecture's `≤ 64`; `π(L_fpy □ L_fpy) ≤ 246` PROVED (rooted `≤ 106` PROVED) | `docs/terminal_report.md` |
| `positive_square_energy_equality/` | Akbari–Kumar–Mohar–Pragada–Zhang Conjecture 9.2 for 2-trees | OPEN at the slot-shift wall; existential ear-selection lemma `(L')` OPEN; 40-page paper drafted | `paper/paper.pdf` |
| `unit_vector_flows/` | Jain's `S²`-flow conjecture for bridgeless graphs | OPEN; finite theorem PROVED for nontrivial snarks on `n ≤ 28`; Jain's *second* (finite-labeling) conjecture REFUTED (Ulyanov 2026) | `THEOREM.md`, `paper/main.tex` |

## How to read this document

Each section below follows the same five-part shape:

1. **Conjecture** — every nonstandard term defined inline, then the formal statement.
2. **Status** — explicit PROVED / OPEN / REFUTED / WITHDRAWN labels per claim, plus "computer-checked at `n ≤ X`" for finite-case computational evidence.
3. **Layout** — one line per top-level subfolder.
4. **Start here** — 2–4 ordered file paths to open first.
5. **Notable artifacts** — papers, certificates, key scripts, recorded negative results.

If you only have ten minutes, the top of each section's "Start here" list is the right
entry point.

## 1. `3_decomposition_conjecture/`

### Conjecture

**Definitions.** A *cubic graph* is a simple graph in which every vertex
has degree exactly 3; a *subcubic graph* is a simple graph of maximum
degree at most 3. A *spanning tree* of `G` is an acyclic connected
subgraph whose vertex set is `V(G)`. A *2-regular subgraph* is a subgraph
in which every vertex has degree exactly 2 (equivalently, a vertex-disjoint
union of cycles); a *matching* is a set of edges no two of which share an
endpoint. A *2-edge-cut* of a connected graph `G` is a 2-element edge set
`F = {e_1, e_2}` whose removal disconnects `G`; `F` is *essential* when
the four endpoints of `e_1, e_2` are pairwise distinct. Removing such an
`F` yields two connected components, the *sides* of the cut. A *2-pole
side* is a pair `(H, R)` where `H` is a connected subcubic graph and
`R = (r_1, r_2)` is an ordered pair of distinct degree-2 vertices (the
*ports*); the order distinguishes `(r_1, r_2)` from `(r_2, r_1)`, so we
speak of *oriented 2-pole sides*. A *boundary trace* on `(H, R)` records,
for each port, the local colours of its two `H`-edges under a candidate
edge partition `E(H) = T_H ⊔ C_H ⊔ M_H` (with `T_H` a forest, `C_H`
2-regular, `M_H` a matching), together with the partition of the
`T`-incident ports into tree-components of `T_H`. The set of realisable
boundary traces is `Trace(H, R)`; full details are in
`docs/minimal_counterexample.md` §1.3. A *gadget* is a 2-pole side
considered up to its trace set; the *gadget lattice* at order `n` is the
inclusion poset on `{Trace(H, R) : |V(H)| ≤ n}`. We say `(H', R')` is
*trace-contained* in a gadget class `C` of the lattice when
`Trace(C) ⊆ Trace(H', R')` (so plugging `C` into the supergraph in place
of `(H', R')` cannot produce new global behaviour and is therefore a
valid Lemma-2 replacement). A 2-pole side `(H, R)` is *compatibility-
universal* when, for every trace `τ` realisable on any side that could be
glued to `(H, R)` across the cut, some `σ ∈ Trace(H, R)` is
boundary-compatible with `τ`. *Absorption-universal* is the same property
read off the absorbing lattice class rather than the side itself: the
class absorbs every possible counterparty trace.

**Hoffmann-Ostenhof (2011), OPG (2017).** Every connected cubic graph `G`
has a decomposition `E(G) = T ⊔ C ⊔ M` where `T` is a spanning tree, `C`
is a 2-regular subgraph, and `M` is a matching. Both `C` and `M` may be
empty. Equivalently, the vertex set splits into `V_C` (`T`-degree 1, on a
cycle of `C`), `V_M` (`T`-degree 2, matched by `M`), `V_T` (`T`-degree 3,
pure tree), with `|V_C| = |V_T| + 2`.

### Status

Open. Partial reductions are in hand:

- **Lemma 1 (bridge reduction): PROVED unconditionally** in
  `docs/minimal_counterexample.md` §2. It reduces the conjecture for a
  bridged cubic `G` to a 1-port boundary-traced decomposition problem on
  each side of the bridge.
- **Sub-lemma 1' (subcubic existence at a bridge port): COMPUTER-CHECKED
  through `n = 11`** on all 137 connected 1-port subcubic graphs across
  `n ∈ {5, 7, 9, 11}`. Not proved in this codebase: "minimal counter-
  example is bridgeless" therefore currently rests on this finite check
  together with the assumption that no counterexample to Sub-lemma 1'
  exists at `n ≥ 13`.
- **Antichain Coverage Conjecture: REFUTED at `n = 12`.** Of 1670
  oriented 2-pole sides at `n = 12`, 10 are not trace-contained by any
  smaller gadget in the `n ≤ 10` lattice. The 5 distinct failure trace
  sets are all compatibility-universal (equivalently, absorption-
  universal) and are absorbed via compatibility replacement by a
  6-vertex gadget in class `C5`.
- **`n = 14` full sweep: COMPUTER-CHECKED.** Of 15,178 oriented 2-pole
  sides, 15,176 are trace-contained in the `n ≤ 12` lattice and the
  remaining 2 are eliminated by the bridge lemma (both orientations of a
  single bridge-class graph whose bridge cuts off a zero-port component).
- **Universal Replacement Conjecture: OPEN.** Statement: every 2-pole
  side `(H, R)` arising from an essential 2-edge-cut with `|V(H)| ≥ 12`
  is either trace-contained by a smaller gadget class or compatibility-
  universal. The `n = 14` sweep is empirical evidence, not a proof; the
  conjecture is open for all orders `≥ 16`.

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

**Definitions.** A *digraph* `D = (V, A)` is a finite set `V` of vertices
together with a multiset `A` of *arcs* (directed edges, ordered pairs `(u,v)`
with `u ≠ v`; parallel arcs are allowed, loops are not). A *spanning subdigraph*
of `D` is a digraph on the same vertex set `V` using a subset of the arcs.
`D` is *strongly connected* (or *strong*) if for every ordered pair of distinct
vertices `u, v ∈ V` there is a directed `u→v` path in `D`. For `∅ ≠ X ⊊ V` the
*out-cut* is `∂⁺(X) = {(u,v) ∈ A : u ∈ X, v ∉ X}`; the *in-cut* `∂⁻(X)` is
`∂⁺(V∖X)`. `D` is *k-arc-strong* if `|∂⁺(X)| ≥ k` for every `∅ ≠ X ⊊ V`
(equivalently, by Menger, every ordered pair of vertices admits `k` arc-disjoint
directed paths). The *arc-connectivity* of `D` is
`λ(D) := min { |∂⁺(X)| : ∅ ≠ X ⊊ V }`, so `D` is `k`-arc-strong iff `λ(D) ≥ k`.
`D` is *Eulerian* if it is connected and every vertex satisfies `d⁺(v) = d⁻(v)`
(in-degree equals out-degree). A *strong arc decomposition* (SAD) of `D` is a
partition `A = A₁ ⊔ A₂` such that both spanning subdigraphs `(V, A₁)` and
`(V, A₂)` are strongly connected; equivalently, every out-cut `∂⁺(X)`,
`∅ ≠ X ⊊ V`, contains at least one arc of each color. A *semicomplete digraph*
is one in which every unordered pair of distinct vertices is joined by at least
one arc (in either direction); a *tournament* is the simple case. A *split
digraph* has vertex set partitioned into a clique part and an independent part
(in the underlying graph sense). The known 2-arc-strong obstructions to SAD are
`S₄` (a specific 4-vertex semicomplete digraph), the *squares of even directed
cycles* `C_{2k}^{(2)}` (the digraph obtained from `C_{2k}` by adding for each
arc `(i, i+1)` the arc `(i, i+2)`), the four exceptional 2-arc-strong
semicomplete compositions of Bang-Jensen–Gutin–Yeo (2020), and the 2-arc-strong
split obstructions of Ai–He–Li–Qin–Wang (2024).

**Bang-Jensen–Yeo (2004).** *There exists an absolute constant `K` such that
every `K`-arc-strong digraph admits a strong arc decomposition.*

No finite value of `K` has been proved sufficient in the literature; the
existence statement itself is open.

**Working Conjecture (WC3) in this project:** `K = 3`. The motivation is that
every cited 2-arc-strong obstruction sits exactly at `λ = 2`: `S₄`, the squares
of even directed cycles inside locally semicomplete digraphs, the four
Bang-Jensen–Gutin–Yeo (2020) semicomplete-composition exceptions, and the
Ai–He–Li–Qin–Wang (2024) split exceptions. No 3-arc-strong digraph without a
SAD is known.

### Status

The Bang-Jensen–Yeo conjecture is **OPEN** (no finite `K` proved sufficient).
WC3 is **OPEN**. Phase 3 v2 closed with a meaningful negative result and two
proved side-theorems:

- **Negative computational evidence (not a theorem).** 4,613 verified
  3-arc-strong digraphs were generated across four vehicles (template gluings,
  Eulerian constructions, laminar cut systems, Cayley families) and tested with
  two independent backends (ILP cut-separation in PuLP+CBC; SAT with explicit
  out/in arborescence witnesses in pysat+CaDiCaL). Zero UNSAT, zero ILP–SAT
  disagreements; the full project sweep across all phases reached roughly
  20,600 verified `λ = 3` instances (still zero UNSAT). Either WC3 holds, or
  any counterexample lies outside the structured families tested at `n ≲ 30`.
  This is empirical evidence, not a proof.
- **Theorem (EC-log), PROVED.** Every Eulerian digraph `D` on `n ≥ 3` vertices
  with `λ(D) ≥ 6 log₂ n` admits a SAD. (Headline constants `C = 6`, `n₀ = 3`,
  post-fix; the earlier `C = 5` headline was retracted in
  `CORRECTNESS_REVIEW_2026_05_18.md` §2.5 because the binding inequality
  `5 log₂ n > 4 log₂ n + 3` requires `n ≥ 9`, not `n ≥ 4`.) Proof via the
  Eulerian-to-undirected reduction `d_G(X) = 2|∂⁺(X)|`, Karger's
  `O(n^{2α})` cut-counting bound, and a first-moment random 2-coloring; no
  alteration step is needed. The asymptotic limit of the method is
  `C → 4⁺`. The hypothesis is a *sufficient condition* for SAD on the Eulerian
  high-arc-strength regime; it says nothing about general 3-arc-strong inputs
  (Eulerianness is essential — the identity `d_G(X) = 2|∂⁺(X)|` fails without
  it — and `λ` growing at least logarithmically is essential — the union bound
  caps out at `Θ(log n)` because Karger's `n^{2α}` count is asymptotically
  tight).
- **Theorem (CL1, bilateral controlled-lifting lemma), PROVED.** Let `D` have
  vertex partition `V = V₁ ⊔ V₂`. If each induced subdigraph `D[V_i]` admits
  a SAD, and the bridge arc set between `V₁` and `V₂` admits a 2-coloring with
  each (direction, color) class non-empty, then `D` admits a SAD. The proof is
  Edmonds-stitching of out- and in-arborescences at a common root. CL1 is
  novel relative to the audited literature lineage (Bang-Jensen–Yeo 2004 /
  Bang-Jensen–Huang 2012 / Bang-Jensen–Gutin–Yeo 2020 / Bang-Jensen–Wang 2025 /
  Ai et al. 2024): prior lifting lemmas are kernel-shell asymmetric, whereas
  CL1 partitions every arc including internal arcs of both parts.
- **Conjecture L, REFUTED.** A subsidiary funnel-property conjecture used in
  the original draft to close the hard `(1, 0)`-near-split case fails on a
  small 4-vertex configuration embeddable in the bidirected `K₄*` (a
  3-arc-strong host). Two existential / swap-repair rescues (`L-exist`,
  `L-swap`) are formulated as **OPEN** in `paper/findings.md` §3.

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

**Definitions.** Graphs are *simple, undirected, finite*. The
**chromatic number** `χ(G)` is the least `k` admitting a proper
`k`-colouring. The **crossing number** `cr(G)` is the minimum number of
edge-pair crossings over plane drawings of `G`. The **Guy–Zarankiewicz
quantity**
```
Z(t) := (1/4) · ⌊t/2⌋ · ⌊(t-1)/2⌋ · ⌊(t-2)/2⌋ · ⌊(t-3)/2⌋
```
counts crossings in Guy's drawing of `K_t`, so `cr(K_t) ≤ Z(t)`;
equality is proved for `t ≤ 12` (Guy/Saaty, Pan–Richter 2007), *open*
for `t ≥ 13`. Landmarks: `Z(24) = 3630`, `Z(25) = 4356`, `Z(26) = 5148`.

Lineage. **Hadwiger (1943, open for `t ≥ 7`):** `χ(G) ≥ t` forces a
`K_t`-minor. **Hajós (1961, REFUTED):** `χ(G) ≥ t` forces a `K_t`
subdivision; Catlin (1979) refutes for `t ≥ 7`. Albertson is the
**metric strengthening**: replace the topological substructure by the
metric `cr(G)`.

A graph is **`k`-critical** if `χ(G) = k` and `χ(H) < k` for every
proper `H ⊊ G`. The **Ore composition** `G_1 ∗ G_2` picks
`xy ∈ E(G_1)`, `z ∈ V(G_2)`, splits `z` into `z', z''` partitioning
`N_{G_2}(z)`, and identifies `x = z'`, `y = z''`;
`|V(G_1 ∗ G_2)| = |V(G_1)| + |V(G_2)| − 1`. The **Ore family** `𝒪_k`
is the closure of `{K_k}` under Ore composition; the **Ore-order
congruence** `|V(G)| ≡ 1 (mod k − 1)` follows by induction. The
**Kostochka–Yancey bound** for `k`-critical `G` (`k ≥ 4`),
`|E(G)| ≥ F(k, n) := ((k+1)(k−2) n − k(k−3)) / (2(k−1))`, is tight
exactly on `𝒪_k`.

The **Crossing Lemma** (Ajtai–Chvátal–Newborn–Szemerédi 1982; Leighton
1983) states `cr(G) ≥ c · m³ / n²` for `m ≥ 4n`. Current best constant
(verified against `D2_literature_verification.md` §4):
**`c > 1/27.48` at threshold `m ≥ 6.95 n`** (Büngener–Kaufmann 2024,
arXiv:2409.01733; BK's abstract gives `6.77 n`, but Cranston's
downstream chain uses `6.95 n`). Improvement chain:
`1/64` (1997) → `1/31.1` (2006) → `1/29` (Ackerman 2019) → `1/27.48`
(BK 2024).

The **list-chromatic number** `χ_ℓ(G)` is the least `k` such that for
every assignment of `k`-element lists `L(v)`, `G` admits a proper
colouring with `v` taking a colour from `L(v)`; `χ_ℓ ≥ χ`. The
**DP-chromatic number** `χ_{DP}(G)` (Dvořák–Postle 2018) replaces lists
by arbitrary matchings between adjacent colour-classes; `χ_{DP} ≥ χ_ℓ`.
**Degeneracy** is `max_{H ⊆ G} δ(H)`; **arboricity** is the minimum
number of forests partitioning `E(G)` (Nash-Williams). Both upper-bound
`χ_{DP}` and feed the average-edge floor input to the Albertson chain.

**Albertson (2007).** `χ(G) ≥ t ⇒ cr(G) ≥ cr(K_t)`.

### Status

**OPEN at `t ≥ 25`.** Cranston (2025, arXiv:2512.08020) **PROVED** the
conjecture for `t ≤ 24` via repeated Crossing-Lemma applications at
BK's `1/27.48`.

- **Track A (residual hunt) — OPEN, demoted.** Cranston's Theorem 2
  pins possible `t`-critical counterexamples to
  `(t, |G|) ∈ {(25, 48), (26, 50), (26, 51)}`. The Ore-order congruence
  `|V(G)| ≡ 1 (mod k − 1)` **rules `(25, 48)` and `(26, 50)` out of the
  Ore family** — both *empty*, not singletons:
  - `(25, 48)`: `48 ≢ 1 (mod 24)`; `𝒪_{25}` at order 48 is **empty**.
    Admissible 25-Ore orders: `{25, 49, 73, …}` (`K_{25} ∗ K_{25}` has
    order `49`). The earlier "12 Ore classes at `(25, 48)`" tally was
    **WITHDRAWN** (`FIX_VERIFICATION_2026_05_18.md`).
  - `(26, 50)`: `50 ≢ 1 (mod 25)`; `𝒪_{26}` at order 50 is **empty**.
  - `(26, 51)`: `51 ≡ 1 (mod 25)`; D4 enumerates 12 Ore classes.

  Non-Ore counterexamples remain unexcluded; unrestricted search is
  intractable.

- **Track B (structural sub-results).**
  - **R5a — FPS Claim 3.7 sharpness — PROVED (D8, 2026-05-17).** The
    FPS threshold `δ = 9/8` is sharp *within the Vizing–Gupta +
    semi-random framework*, via the witness identity
    `f_{2b}(4/7, δ) − 9/16 = 12 (δ − 9/8)² / [7 (4 δ − 1)]`; `9/16` is
    binding in this framework. The earlier `D5` claim that re-tuning
    `δ ≈ 1.114907` beats `9/16` was **WITHDRAWN** (silent monotonicity
    assumption; transition at `δ_crit = −3 + √17 ≈ 1.12311`).
  - **D16 — bisection-width Crossing Lemma for spectral expanders —
    PROVED.** For `d_0`-regular `G` with `|λ_2(G)| ≤ θ d_0`,
    `θ ∈ [0, 1)`,
    `cr(G) ≥ (1 − θ)² d_0² (⌊n/2⌋ ⌈n/2⌉)² / (80 n²) − d_0² n / 16`.
    Pach–Spencer–Tóth packaging + Alon spectral bisection. Does **not**
    close any Cranston residual — Ore populators are not expanders.
  - Front-runners: **R2c** (min-degree-refined Crossing Lemma on
    `t`-critical graphs); **R3.6** (fractional / list / DP analogues).

- **Withdrawn deliverables.**
  - **D15 `list_albertson_le_18.pdf` — WITHDRAWN (2026-05-17).** Main
    theorem (`χ_ℓ(G) ≥ t ⇒ cr(G) ≥ cr(K_t)` for `t ≤ 18`) **REFUTED at
    `t = 5`** by Voigt's 1993 planar `G` with `χ_ℓ = 5`, `cr = 0 < 1 =
    cr(K_5)`. The "lifts-for-free" argument is also structurally wrong
    (Ackerman §3.1 uses `f_r(n)`; the list analogue Krivelevich 1997
    is provably weaker).
  - **D18 `two_structural_observations` — WITHDRAWN (2026-05-17).**
    Observation 1 was the false D15 claim; Observation 2 was salvaged
    as standalone D16.

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
- `D15_list_albertson_paper/` — `list_albertson_le_18.pdf` (9 pages):
  list-chromatic Albertson for `t ≤ 18`; **WITHDRAWN** (Voigt 1993 t=5
  counterexample).
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

- **PROVED:** `D8` `sharpness_9_8.pdf` (theorem-grade R5a sharpness).
- **PROVED, publication-ready:** `D16` `expander_crossing.pdf`.
- **WITHDRAWN:** `D15` (Voigt 1993 t=5 counterexample to χ_ℓ-Albertson);
  `D18` (false observation at t=5; D16 was salvaged as standalone).
- Cite-grade audit: `D2_literature_verification.md` (Cranston's three pairs;
  Kostochka–Yancey edge bounds 588/638/650; BK crossing threshold 6.77 n vs.
  Cranston's 6.95 n).

## 4. `directed_path_minimum_outdegree/`

### Conjecture

**Definitions.** A **digraph** `D = (V, A)` has arc set `A ⊆ V × V`; we write
`u → v` for the arc `(u, v)`. For a vertex `v`, the **out-degree**
`d⁺(v)` and **in-degree** `d⁻(v)` are the numbers of arcs with tail `v` and
head `v` respectively. Set `δ⁺(D) := min_v d⁺(v)` and `δ⁻(D) := min_v d⁻(v)`.
An **oriented graph** is a digraph with no 2-cycle (for no `u ≠ v` do both
arcs `u → v` and `v → u` appear); equivalently, an orientation of a simple
undirected graph. This is strictly more general than a **tournament**, which
is an orientation of a complete graph. A **directed path of length `k`** is
a sequence of **distinct** vertices `v_0, v_1, …, v_k` with `v_{i-1} → v_i`
for every `1 ≤ i ≤ k`; the **length is the number of arcs (`k`)**, not the
number of vertices. Write `ℓ(D)` for the length of a longest directed simple
path in `D`. The **score profile** (or **score sequence**) of `D` is the
sorted list of out-degrees `(d⁺(v))_{v ∈ V}`; the profiles `(1,1,1,1)`,
`(2,1,1,1)`, `(2,2,1,1)`, `(3,1,1,1)` arise as the possible out-degree
multisets of a `4`-vertex induced subgraph `S` in the `δ = 4` case analysis.
A digraph is **`4`-outregular** if `d⁺(v) = 4` for every vertex.

**Cheng–Keevash Lemma 7 (key structural tool, arXiv:2402.16776v4, verbatim).**
*If `D` is an oriented graph with `δ⁺(D) ≥ δ`, then either `D` contains a
directed path of length `2δ`, or there is an induced subgraph `S` with
`|S| ≤ δ` and `δ⁺(S) ≥ 2δ − ℓ(D)`.* (No `+1` strengthening: the published
proof's final inequality silently swaps the arc-count and vertex-count of the
path; the headline statement above is the correct one.)

**Cheng–Keevash Conjecture 1 (oriented-graph form; attributed in the paper to
Thomassé as the `g = 3` corollary of the stronger girth-`g` conjecture).**
Every oriented graph `D` with `δ⁺(D) ≥ δ` contains a directed path of length
`2δ`.

### Status

Active; recent partial closures by this project.

| `δ` | `n` | Status |
|---|---|---|
| `1`, `2` | all | **PROVED** (trivial; `δ = 2` falls out of Lemma 7 plus the oriented average bound, Cheng–Keevash (2024)) |
| `3` | all `n ≥ 7` | **PROVED**, hand proof (`docs/k3_hand_proof.md`): Lemma 7 + oriented average bound + antiparallel cyclic-closure on the endpoint cycle |
| `4` | `n = 10` | **PROVED**, hand + computer-aided. Score profiles `(1,1,1,1)`, `(2,1,1,1)`, `(3,1,1,1)` by hand; `(2,2,1,1)` by exhaustive enumeration on a per-completion certificate (`data/k4_n10_certificate.json`, 3 664 completions) replayed end-to-end by the auditor with `scripts/k4_verify_certificate.py` |
| `4` | `n = 11` | **Computer-verified, reproduction-only**: two pipelines under a **shared declarative rule specification** (32 configurations, 117 992 940 completions, 0 obstructions). **No per-completion certificate at `n = 11`**; a shared-spec bug would survive both pipelines. Closing the residual trust gap needs a third independent pipeline (SAT/CSP or naive enumeration) |
| `4` | `n ≥ 12` | **OPEN**. Miner ready (`scripts/k4_score_profile_miner.py 12` is the next computational target, est. 2–4 h); exact search planned through `n ≤ 15`, beyond which no claim of computational closure may be made |
| `δ ≥ 5` | all | **OPEN**. Best general bound is Cheng–Keevash Theorem 4: `ℓ(D) ≥ ⌈1.5 δ⌉` for any oriented graph |

The `δ = 4, n ∈ {10, 11}` closures both reduce to a `4`-outregular oriented
graph and enumerate the four possible score profiles of the Lemma-7 witness
`S` on `≤ 4` vertices, with `δ⁺(S) ≥ 2δ − ℓ(D) ≥ 1` providing the structural
anchor. The `n = 11` weakening is audit finding **M1** (shared specification
across the two pipelines) and **M2** (no per-completion certificate at
`n = 11`, in contrast to `n = 10`); the per-completion runtime assertions
(`M3` fix) now mirror the `n = 10` verifier inside both miners but do not by
themselves close the shared-spec gap.

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

**Definitions.** All graphs are finite and simple.

- *Planar graph.* `G` is **planar** if it admits an embedding in the
  plane with no edge crossings. Equivalently (Kuratowski/Wagner), `G`
  contains neither `K_5` nor `K_{3,3}` as a minor. Euler's formula and
  the face-length bound give `|E(G)| ≤ 3n − 6` for every planar `G`
  with `n ≥ 3`.

- *Thickness, biplanar.* `θ(G)` is the minimum number of planar
  subgraphs into which `E(G)` partitions (vertices shared, edges
  partitioned). `G` is **biplanar** iff `θ(G) ≤ 2`. Since each planar
  layer obeys `m_i ≤ 3n − 6`, every biplanar graph satisfies
  `|E(G)| ≤ 6n − 12`. Ringel's Earth–Moon problem asks for
  `χ_EM := max{ χ(G) : G biplanar }`.

- *Chromatic number, criticality.* `χ(G)` is the minimum number of
  colours in a proper colouring. `G` is **`k`-critical** if `χ(G) = k`
  but every proper subgraph is `(k−1)`-colourable; then `δ(G) ≥ k−1`.

- *Heawood 1890, `χ_EM ≤ 12`.* Biplanarity is hereditary, and
  `|E(H)| ≤ 6|V(H)| − 12` for every subgraph `H ⊆ G` gives average
  degree `< 12` in every subgraph, so some vertex has degree `≤ 11`.
  Iterating, `G` is `11`-degenerate, and greedy colouring in
  degeneracy order uses ≤ 12 colours.

- *Sulanke/Gardner 1980, `χ_EM ≥ 9`.* The biplanar graph `K_6 + C_5`
  on 11 vertices has `χ = 9`. So `9` is realised; the lower bound is
  *not* in dispute.

- *Kostochka–Yancey 2014.* Every `k`-critical graph satisfies
  `|E(G)| ≥ ((k+1)(k−2) n − k(k−3)) / (2(k−1))`. At `k = 12`:
  `|E(G)| ≥ (65 n − 54)/11`. Combined with the biplanar cap
  `|E(G)| ≤ 6n − 12 = (66 n − 132)/11`, a 12-critical biplanar graph
  needs `n ≥ 78`.

- *`K_9`-free, the upper-bound program.* Every biplanar graph is
  `K_9`-free because `θ(K_9) = 3`. A `K_9`-free strengthening of
  Kostochka–Yancey that adds at least `(1/11) · n` edges would close
  `χ_EM ≤ 11`; this is the target of `docs/phase6_discharge_attempt.md`.

- *Graph products.* `C_7[K_4]` is the **lexicographic product** (the
  *clique blowup* when the second factor is complete): replace each
  vertex of `C_7` by a copy of `K_4` and join every pair of vertices
  in `C_7`-adjacent fibres. When the second factor is complete, this
  agrees with the strong product `C_7 ⊠ K_4` (verified in
  `CORRECTNESS_REVIEW_2026_05_18.md` §4 by direct NetworkX
  isomorphism check; both labels denote the same 28-vertex graph).
  The Cartesian product `C_7 □ K_4` is a *different* graph and is not
  the candidate.

- *Beineke–Harary–Moon 1964.* Outside a small exceptional family
  (not containing `(5,12)`), `θ(K_{p,q}) = ⌈ pq / (2(p+q−2)) ⌉`. In
  particular `θ(K_{5,12}) = ⌈60/30⌉ = 2`, so `K_{5,12}` is biplanar.

**Ringel (1959).** With the definitions above, the problem is to
determine `χ_EM`. The current bracket is `9 ≤ χ_EM ≤ 12` (Sulanke /
Gardner 1980 below, Heawood 1890 above). The folklore guess
`χ_EM = 9` is unproven.

### Status

- **`χ_EM ≤ 12`: PROVED** (Heawood 1890; see derivation above).
- **`χ_EM ≥ 9`: PROVED** (Sulanke/Gardner 1980, witness `K_6 + C_5`).
- **`χ_EM = 9`: OPEN** (folklore, neither proved nor refuted).
- **`χ_EM ≤ 11`: OPEN** (density-based program in progress).
- **`χ_EM ≥ 10`: OPEN** (no biplanar 10-chromatic graph known).

Two complementary tracks:

- **Disprove `χ_EM = 9` by exhibiting a 10-chromatic biplanar graph.**
  *OPEN, with empirical negative evidence.* The headline candidate
  `C_7[K_4]` (28 vertices, `χ = 10`, `ω = 8`, hence `K_9`-free,
  `|E| = 154 ≤ 156 = 6n−12`) was reported UNSAT by the project's
  biplanarity oracle (SMS v1.0.0 with Patches A and C; 9.7 h wall,
  May 2026). Per `data/c7_k4/README.md` (§ Verification caveats) and
  `FIX_VERIFICATION_2026_05_18.md`, this is **single-tool
  computational evidence, not a theorem**: there is no DRAT trace, no
  proof object, and no independent biplanarity oracle has replayed
  the verdict. The same SMS codebase produced every UNSAT in the
  cycle-clique-blowup family (`candidate1`, `new_c5_a`, `new_c5_b`,
  `c7_k4`). The four such blowups with `n ≤ 30`, `ω ≤ 8`, `χ ≥ 10`,
  `|E| ≤ 6n − 12` from `scripts/cycle_blowup.py` are empirically
  non-biplanar under this single oracle, exhausting the cycle
  clique blowup template; non-blowup 28-vertex candidates are not
  ruled out.

- **Tighten `χ_EM ≤ 11` via density on 12-critical `K_9`-free biplanar
  graphs.** *OPEN, in-progress.* Kostochka–Yancey gives `n ≥ 78`;
  adding Kostochka–Yancey's 2018 Brooks-type bound pushes the
  threshold to `n ≥ 89`. The discharging attempt in
  `docs/phase6_discharge_attempt.md` then faces two open obstacles:
  - *Step 4+:* preserving `K_9`-freeness under a chosen non-edge
    contraction inside `N(v)`.
  - *Q0 high-only closure:* eliminating the 143 feasible Q0
    profiles by a non-local argument.
  Neither is "almost done".

- **Fork C probe (commit 204282a, May 16, 2026).** A non-saturated
  `K_7` witness on partition `(7, 3, 1)` (14 vertices, 56 edges; seven
  outside vertices each adjacent to a cyclic 5-subset of the central
  `K_7`, no outside-outside edges) is biplanar in 0.011 s, even
  though the saturated `K_7 + K̄_5` (12 vertices, 56 edges) is UNSAT
  in 13.1 s. This blocks one Q0-closure path; the argument now
  branches to Forks A/B (structural Gallai arguments on low-degree
  vertices), both speculative.

- **Classical regression sanity checks.** `K_8`, `K_{5,5}`,
  `K_{5,12}` are biplanar (the last via BHM 1964, `⌈60/30⌉ = 2`);
  `K_9`, `K_{7,7}`, `K_{6,9}` are not.

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
4. `data/c7_k4/README.md` — how `C_7[K_4]` was ruled out; scaling vs. `C_5` cases.

### Notable artifacts

- `biplanar_check.py` — flexible biplanarity tester (SMS wrapper).
- `phase6_discharge_attempt.md` — sections 7.15–7.16 document Forks A/B/C.
- Fork C result: `K_7` + 7 cyclic 5-neighbours (n = 14, m = 56) is biplanar.
- `c7_k4` run: 34,834 CPU s, 64 M propagator calls, 3.84 M Kuratowski clauses.

## 6. `pebbling_cartesian_product/`

### Conjecture

**Definitions.**

- **Pebble distribution / configuration.** Let `G = (V, E)` be a finite simple
  connected graph. A *configuration* (or *t-pebble distribution*) is a function
  `C: V → Z_{≥0}` assigning a non-negative integer number of pebbles to each
  vertex; its *size* is `|C| = Σ_v C(v)`. A *t-pebble distribution* is one with
  `|C| = t`.
- **Pebbling move.** A pebbling move on `C` removes 2 pebbles from some vertex
  `u` with `C(u) ≥ 2` and places 1 pebble on a neighbor `v` of `u` (so `C(u) ←
  C(u) − 2` and `C(v) ← C(v) + 1`). Each move strictly decreases the total
  pebble count by 1.
- **`r`-solvable distribution.** A distribution `C` is *`r`-solvable* (or
  "`r`-reachable") if some finite sequence of pebbling moves applied to `C`
  produces a configuration with at least one pebble on the root `r`. Otherwise
  `C` is *`r`-unsolvable*.
- **Rooted pebbling number `π(G, r)`.** The minimum `t` such that *every*
  `t`-pebble distribution on `G` is `r`-solvable. Equivalently, the smallest
  `t` such that no `t`-pebble distribution `C` with `C(r) = 0` is
  `r`-unsolvable.
- **Pebbling number `π(G)`.** The minimum `t` such that every `t`-pebble
  distribution is `r`-solvable for *every* choice of root `r`. Equivalently,
  `π(G) = max_{r ∈ V} π(G, r)`. (This is the "all-root" pebbling number — the
  convention used throughout this project; the terminal report writes
  `π(G, r)` for the rooted version and the bare `π(G)` for the all-root
  version.)
- **Cartesian product `G □ H`.** The graph with vertex set `V(G) × V(H)` in
  which two vertices `(u, v)` and `(u', v')` are adjacent iff either (i)
  `u = u'` and `vv' ∈ E(H)`, or (ii) `v = v'` and `uu' ∈ E(G)`.
- **Lemke graph `L` (this project's `L_fpy`).** The 8-vertex graph on
  `V = {0, 1, …, 7}` with the 13 edges
  `{0-1, 0-2, 1-3, 2-4, 2-5, 2-6, 3-4, 3-5, 3-6, 3-7, 4-7, 5-7, 6-7}`
  (degree sequence `(5, 4, 4, 3, 3, 3, 2, 2)`). This is the labelling used in
  the Flocco–Pulaj–Yerger codebase and stored in
  `data/pebbling_product/graphs/L_fpy.json`. It is isomorphic to Hurlbert's
  original Lemke graph on vertices `{a, b, c, d, w, x, y, z}` (the bijection is
  recorded in `docs/literature_notes.md`). For this graph `π(L) = 8 = |V(L)|`,
  i.e. `L` is "class 0". `L` was historically the first known graph failing
  the 2-pebbling property, which is why `L □ L` is the classical stress test
  for the conjecture below.
- **Weight-function strategy (Hurlbert).** Given a root `r ∈ V(G)`, a
  *strategy* is a subtree `T ⊆ G` containing `r` together with a rational
  weight function `w: V(G) → Q_{≥0}` such that (i) `w(r) = 0`, (ii)
  `w(v) = 0` for `v ∉ V(T)`, and (iii) for every `v ∈ V(T) \ {r}` whose
  parent `v⁺` in `T` is not `r`, either `w(v⁺) = 2 w(v)` ("basic") or
  `w(v⁺) ≥ 2 w(v)` ("nonbasic"). Set `b_T = Σ_{v ∈ V(T)\{r}} w(v)`. The
  **Weight Function Lemma** (Hurlbert) states that every `r`-unsolvable
  configuration `C` with `C(r) = 0` satisfies `Σ_v w(v) C(v) ≤ b_T`.
- **Weight-function certificate.** A list of strategies `T_1, …, T_k` with
  weights `w_1, …, w_k` and non-negative rational multipliers `α_1, …, α_k`
  such that `Σ_i α_i w_i(v) ≥ 1` for every `v ≠ r`. Summing the WFL inequality
  with multipliers `α_i` yields `|C| ≤ Σ_i α_i b_i` for every `r`-unsolvable
  `C` with `C(r) = 0`, hence
  `π(G, r) ≤ ⌊Σ_i α_i b_i⌋ + 1`. The verifier
  `scripts/check_pebbling_weight_certificate.py` checks this entirely in
  `fractions.Fraction` arithmetic (no floats in the acceptance decision).
- **Root orbit.** The equivalence class of a root `(u, v) ∈ V(L) × V(L)`
  under the group `Aut(L_fpy) ⋊ Z_2` acting diagonally on the two coordinates
  plus the factor-swap involution `(u, v) ↦ (v, u)`. This is a strict subgroup
  of `Aut(L □ L)`; the project finds 22 orbits (Wood–Pulaj 2024 report 21
  under the full automorphism group — both are valid covers, and 22 is
  conservative for upper bounds).
- **Hurlbert 2017.** G. Hurlbert, *A Linear Optimization Technique for Graph
  Pebbling*, arXiv:1101.5641 (preprint 2011, journal version *J. Combin.
  Optim.* 34(2) (2017), 343–361). Theorem 10 proves `π(L □ L) ≤ 108` via four
  hand-built weight-function strategies averaged with `α = 1/4`.
- **Flocco–Pulaj–Yerger (FPY) 2024.** D. Flocco, J. Pulaj, C. Yerger,
  *Automating weight function generation in graph pebbling*, *Discrete Appl.
  Math.* 347 (2024), arXiv:2312.12618. Uses a Gurobi MILP to search the WFL
  strategy class and obtains the published bound `π(L □ L) ≤ 96`.

**Graham's pebbling conjecture.** For all connected graphs `G` and `H`,
`π(G □ H) ≤ π(G) · π(H)`. Specialized to the Lemke square,
`π(L □ L) ≤ π(L) · π(L) = 8 · 8 = 64`. Any verified upper bound `π(L □ L) ≤ N`
with `N > 64` is consistent with the conjecture; a verified `r`-unsolvable
64-pebble distribution at some root would refute it. This project produces
rational weight-function certificates that yield upper bounds on
`π(L_fpy □ L_fpy, r)` for every root `r`, hence on `π(L_fpy □ L_fpy)`.

### Status

- **PROVED (computer-verified rational certificate).** `π(L_fpy □ L_fpy) ≤ 246`.
  The bound is the maximum over 22 per-root-orbit certificates aggregated by
  `scripts/aggregate_orbit_bounds.py`; the bottleneck is the orbit of root
  `(0, 0)`, certified by `path_orbit_0_0_max_len7.json` with rational LP value
  `295021/1200` and `⌊·⌋ + 1 = 246`. Every certificate is independently
  re-checkable under `Fraction` arithmetic via
  `scripts/check_pebbling_weight_certificate.py`.
- **PROVED (computer-verified rational certificate).** Rooted bound
  `π(L_fpy □ L_fpy, (v_1, v_1)) ≤ 106`, certificate
  `Hurlbert_path_augmented_v1v1_le106.json`, rational LP value `169327/1600`.
  This sharpens Hurlbert 2017 Theorem 10's value `108` at the same root
  `(v_1, v_1) = (4, 4)` in the `L_fpy` labelling.
- **EMPIRICAL EVIDENCE ONLY (not a proof).** At the bottleneck orbit `(0, 0)`,
  no improving column was found under basic uniform-leaf-depth trees up to
  depth ≤ 7 (≈ 196 M nodes) or nonbasic single-branch trees with support ≤ 16
  and weights ≤ 32 (≈ 292 M nodes). The pricing oracles use **float**
  arithmetic against a single SciPy HiGHS dual on a **degenerate** LP with
  multiple optimal duals; rational reduced-cost arithmetic was not run. Per
  `docs/terminal_report.md:159-167`, this is "empirical evidence, not a proof
  of LP-optimality". The 246 bound itself does not depend on this claim.
- **BLOCKED (not refuted, not reproduced).** FPY's published `π(L □ L) ≤ 96`
  bound has not been re-verified locally. The live FPY classes round-trip
  byte-stably through the ingestion adapter (`scripts/fpy_probe.py`,
  regression-tested), but reproducing 96 end-to-end is blocked on (a) a
  Gurobi license to re-run FPY's MILP and dump per-strategy dual multipliers
  `α_i`, or (b) a structured author dump containing those multipliers — the
  public CSVs supply per-strategy weights and tree edges but not the duals,
  and they are also serialized in a convention the current FPY source code
  cannot decode (transpose / vertex-labelling mismatch).
- **OPEN.** Graham's pebbling conjecture for `L □ L`, i.e.
  `π(L □ L) ≤ 64`, is **not settled by this project**. The verified upper
  bound `≤ 246` is consistent with the conjecture but far above the
  conjectural ceiling `64`; no 64-pebble counterexample search was run.
  Graham's conjecture in full generality also remains open.

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

**Definitions.** A *graph* `G = (V, E)` is a finite simple undirected graph;
its *order* is `n := |V|`. `G` is *connected* if every pair of vertices is
joined by a path. The *adjacency matrix* `A(G)` is the symmetric `n × n`
0/1 matrix with `A_{ij} = 1` iff `ij ∈ E`. Because `A(G)` is real symmetric,
its eigenvalues are real and listed in non-increasing order as
`λ_1(G) ≥ λ_2(G) ≥ ⋯ ≥ λ_n(G)`; these are the *adjacency eigenvalues* of `G`.

The two *square energies* are

- `s⁺(G) := Σ_{i : λ_i(G) > 0} λ_i(G)²` — sum of **squares** of the
  **positive** adjacency eigenvalues.
- `s⁻(G) := Σ_{i : λ_i(G) < 0} λ_i(G)²` — sum of **squares** of the
  **negative** adjacency eigenvalues.

(Note: `s⁺` and `s⁻` are sums of *squares*, not sums of eigenvalues. A
common misreading is to drop the squaring; the conjecture below is then
false.) Trace-identity: since `tr A² = Σ_i λ_i² = 2|E|` and the positive
and negative eigenvalues partition the nonzero spectrum,
`s⁺(G) + s⁻(G) = 2|E|`.

**Baseline (Elphick–Farber–Goldberg–Wocjan, [arXiv:1409.2079](https://arxiv.org/abs/1409.2079)).**
For every connected graph `G` of order `n ≥ 1`,

> `s⁺(G) ≥ n − 1`  and  `s⁻(G) ≥ n − 1`.

(Open in general as a conjecture; theorem in many classes. The conjecture
being refined here adds an equality characterisation.)

**Akbari–Kumar–Mohar–Pragada–Zhang Conjecture 9.2**
([arXiv:2506.07264](https://arxiv.org/abs/2506.07264), June 2025).
For every connected graph `G` of order `n`,

- (i) `s⁺(G) = n − 1`  iff  `G` is a tree.
- (ii) `s⁻(G) = n − 1`  iff  `G` is a tree or a complete graph `K_n`.

Here a *tree* is a connected acyclic graph (it has exactly `n − 1` edges);
a *complete graph* `K_n` is the graph in which every pair of vertices is
adjacent. The easy `(⇐)` direction holds by direct computation:

- For a tree `T`, `tr A(T)² = 2|E(T)| = 2(n − 1)`, and the adjacency
  spectrum of a tree (a bipartite graph) is symmetric about `0`, hence
  `s⁺(T) = s⁻(T) = (n − 1)`.
- For `K_n`, the spectrum is `{n − 1, −1, −1, …, −1}` (one eigenvalue
  `n − 1`, the rest equal to `−1`), so
  `s⁻(K_n) = (n − 1) · 1² = n − 1` (and `s⁺(K_n) = (n − 1)²`, which
  exceeds `n − 1` once `n ≥ 3`, consistent with (i) since `K_n` is not a
  tree for `n ≥ 3`).

The substantive content is the `(⇒)` direction: if `s⁺(G) = n − 1` (resp.
`s⁻(G) = n − 1`) then `G` is a tree (resp. tree or `K_n`). Equivalently,
defining the *square-energy gaps*

> `δ⁺(G) := s⁺(G) − (n − 1)`,    `δ⁻(G) := s⁻(G) − (n − 1)`,

the conjecture reads: `δ⁺(G) > 0` iff `G` is not a tree, and `δ⁻(G) > 0`
iff `G` is neither a tree nor a `K_n`. The project tracks `δ⁺` and `δ⁻` —
it is the *gap above the EFGW baseline* that all proofs control.

**Restriction to 2-trees.** A graph is *chordal* if it has no induced
cycle of length `≥ 4` (every cycle of length `≥ 4` has a chord). The
*treewidth* of `G` is the minimum, over all tree-decompositions of `G`,
of `(max bag size) − 1`; equivalently a graph has treewidth `≤ k` iff it
is a subgraph of a `k`-tree. A *`2`-tree* is built recursively: `K_3` is
a `2`-tree, and any `2`-tree on `k + 1 ≥ 4` vertices is obtained from a
`2`-tree on `k` vertices by adding one new vertex adjacent to both
endpoints of an existing edge. `2`-trees are exactly the maximal chordal
graphs of treewidth `2`. For `n ≥ 4` no `2`-tree is a tree (it has
`2n − 3` edges, not `n − 1`) and no `2`-tree is a `K_n` (since `K_n` has
treewidth `n − 1 ≥ 3`); so on the `n ≥ 4` slice of `2`-trees, Conjecture
9.2 reduces to the strict inequalities `s⁺(G) > n − 1` and `s⁻(G) > n − 1`,
or equivalently `δ⁺(G) > 0` and `δ⁻(G) > 0`.

A vertex `v` of `G` is *simplicial* if its neighbourhood `N(v)` induces a
clique. In a `2`-tree, every simplicial vertex has degree exactly `2`
(its two neighbours are adjacent), and `2`-trees on `n ≥ 4` vertices
always have at least two simplicial degree-`2` vertices (the "ears" of
the recursive construction).

Two named `2`-tree subfamilies appear in the contribution stack:

- **Books `B_k`**: `k` triangles sharing one common edge (the "spine"
  edge). `B_k` has `n = k + 2` vertices; `B_1 = K_3`, `B_2 = K_4 − e`.
- **`2`-paths `L_n`**: the "thin" `2`-tree where each new vertex is
  attached to the most recently added edge. Equivalently `L_n` is the
  square of the path graph `P_n`: vertex set `{1, …, n}` with `i ∼ j`
  iff `|i − j| ∈ {1, 2}`. The adjacency matrix is pentadiagonal Toeplitz.

The headline open subproblem of the workstream is

> **`(L')` existential ear-selection lemma.** For every `2`-tree `G` on
> `n ≥ 4` vertices, there exists a simplicial degree-`2` vertex `v*` with
> both `δ⁺(v*) ≥ 17/16` and `δ⁻(v*) ≥ 17/16` (equivalently, with
> `δ⁻(v* viewed as an ear) ∈ [17/16, 47/16]`).

Here `δ±(v)` denotes the gain in `s±` upon deleting `v` from `G` to obtain
`G − v` on `n − 1` vertices. The constant `17/16` is the per-ear "gain"
that, telescoped through `n − 3` ear deletions down to `K_3`, would yield
`s±(G) ≥ 2 + (17/16)(n − 3) > n − 1` for every `2`-tree on `n ≥ 4`
vertices — i.e. would close Conjecture 9.2 on the `2`-tree class. The
implication `(L') ⇒ 9.2 on 2-trees` is proved in
`paper/sections/03_lprime_reformulation.tex` (Proposition 3.5).

### Status

- **Conjecture 9.2 in general — OPEN.** Not proved, not refuted.
- **Conjecture 9.2 on `2`-trees — OPEN.** Reduced to the existential
  ear-selection lemma `(L')`, which is itself open. Substantial partial
  progress documented below.
- **`(L')` on `2`-trees — OPEN.** Stated as Conjecture in
  `paper/sections/03_lprime_reformulation.tex`. The principal analytical
  obstacle is the *slot-shift sum bound* (condition (b) of the candidate
  ansatz, problem O12.2): a quantitative interlacing-style inequality
  for which no standard tool (Lehmann–Goerisch, Temple, Aronszajn,
  Cauchy interlacing, secular-equation residue control) currently
  suffices. Estimated 6 person-months to 2 years for an expert.
- **`(L')` on books `B_k` — PROVED.** Via the closed form
  `δ⁻(B_k) = 2 − 4 / (√(8k + 1) + √(8k − 7))` for `k ≥ 2`, which
  exceeds `17/16` for all `k ≥ 2` (Theorem,
  `paper/sections/04_subfamily_theorems.tex`).
- **`2`-paths Cesàro Szegő limit — PROVED.**
  `s⁻(L_n) / n → c_1⁻ := (32π − 27√3) / (12π) ≈ 1.4262`
  (Szegő–Cesàro via the symbol `f(θ) = 2 cos θ + 2 cos 2θ` of the
  pentadiagonal Toeplitz adjacency matrix). The corresponding
  first-difference statement `δ⁻(L_n) → c_1⁻` is **OPEN**
  (subobligation O13.1); empirically supported on `n ≤ 200`.
- **`2`-paths finite-`n` floor `δ⁻(L_n) ≥ 17/16` (in fact `≥ 21/16`)
  on `n ∈ [4, 1000]` — PROVED** (engineering-rigorous, not
  interval-rigorous). Established by a Demmel–Kahan a-posteriori
  forward-error certificate using `numpy.linalg.eigvalsh` plus the
  envelope constant `c ≤ 10` (script-implemented in
  `scripts/mpmath_certify.py`; the paper also displays a looser
  *a-fortiori* envelope `c ≤ 10⁴`). The worst-case empirical value is
  `δ⁻(L_6) ≈ 1.3190`, with rigorous lower bound dominating
  `17/16 = 1.0625` by slack `≈ 0.257` — three orders of magnitude above
  the propagated forward-error bound `≈ 1.42 · 10⁻⁴`. The bound is *not*
  yet certified for `n > 1000` (mechanical extension, no new
  mathematics required).
- **Stieltjes asymptotic `I_∞(L) ≈ 1.0157` — PROVED.** Closed form
  `I_∞(L) = 2(310π² − 837√3π + 2187) / (27π(20π − 27√3))`, identified via
  half-line Stieltjes transforms plus a Portmanteau closure step.
- **Lemma B1 and Lemma B1⁺ (Rayleigh bounds) — PROVED.** Trial-vector
  lower bounds on `λ_min²` (B1, Phase 8) and `λ_max²` (B1⁺, Phase 12.A).
- **Bad-tail-ear asymptotic `BT(k, 2)`: `δ⁻ → 4 − α² + β² ≈ 1.0353 < 17/16`
  — PROVED (computational/asymptotic, conditional on a sketched
  `O(1/√k)` secular-rate substep).** This **refutes the *universal*
  form of `(L')`** — i.e. shows that the ear-selection in `(L')` must be
  existential, not "every simplicial degree-`2` ear works". The
  existential form remains open.
- **Failure-mode catalogue F1–F15 — established as negative results.**
  Notably F14 (the trace-identity reformulation `δ⁺ + δ⁻ = 4` does *not*
  decouple the slot-shift wall, because the Rayleigh trial-vector
  technique delivers the wrong direction of inequality on the positive
  side) and F15 (Theorem 8.1's `α(G) · ω(G) ≤ n/17` hypothesis is
  satisfied by **zero** connected graphs at `n ≤ 14` in the corpus, and
  is structurally inapplicable to `2`-trees where `α · ω ≈ n`).

The workstream has pivoted from research-attack mode to paper-writing
mode: the principal remaining open problem (the slot-shift wall) is
genuinely research-grade, and the substantial proved partial results
are being banked as a paper.

### Layout

- `paper/` — 40-page LaTeX submission draft (7 sections + appendices); `\stub{}`
  markers for unfilled proofs.
- `docs/` — 30 technical notes: phase logs, failure-mode catalogues (F1–F15),
  structural analyses of books / 2-paths / bad-ears.
- `scripts/` — corpus builders, moment calculations, Stieltjes transforms,
  Demmel–Kahan verification.
- `tests/` — 14 regression test files (539 passing tests).
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

**Definitions.** All graphs are **finite, simple, undirected**. A **bridge**
(or **cut-edge**) is an edge whose removal disconnects the graph;
**bridgeless** means having none. A graph is **cubic** if every vertex has
degree 3. A **3-edge-coloring** is a proper edge coloring with 3 colors (no
two edges sharing an endpoint receive the same color); by Vizing's theorem a
cubic graph has chromatic index `χ'(G) ∈ {3, 4}`, so "not 3-edge-colorable"
is equivalent to `χ'(G) = 4`. The **girth** is the length of a shortest
cycle. The **cyclic edge-connectivity** `λ_c(G)` of a cubic graph (with at
least two disjoint cycles) is the minimum size of an edge cut both sides of
which contain a cycle.

A **snark** here is a simple connected cubic bridgeless graph with
`χ'(G) = 4` (`paper/sections/02_preliminaries.tex` §2.2). A snark is
**nontrivial** if additionally it has **girth ≥ 5** and is **cyclically
4-edge-connected** (`paper/sections/02_preliminaries.tex:79–83`, BGHM 2013
convention). This is *not* the "snark minus Petersen" convention: the
Petersen graph (the unique snark on 10 vertices) *is* nontrivial here.

Fix an orientation of every edge once and for all: for `e = {u, v}` with
`u < v`, set the sign `σ(u, e) = +1` and `σ(v, e) = −1`
(`paper/sections/02_preliminaries.tex:14–20`, mirroring
`scripts/witness.py:orient`). An **`S²`-flow** on `G` is a map
`φ : E(G) → S² ⊂ ℝ³` such that, for every vertex `v`,

>   Σ_{e ∋ v} σ(v, e) · φ(e) = 0 in ℝ³  (**Kirchhoff conservation**).

Reversing an edge flips the sign of its contribution at each endpoint
(Definition 2.1). For cubic `G`, Kirchhoff forces the three incident unit
vectors at each vertex to be coplanar and pairwise at angle `2π/3`
(Lemma 2.2).

Jain (Open Problem Garden, 2007) posed two conjectures:

> **Jain's first conjecture (S²-flow conjecture).** Every bridgeless graph
> admits an `S²`-flow.

> **Jain's second conjecture (finite-labeling conjecture).** There exists a
> map `q : S² → {±1, ±2, ±3, ±4}` with `q(−x) = −q(x)` such that
> `q(v₁) + q(v₂) + q(v₃) = 0` whenever `v₁ + v₂ + v₃ = 0`
> (`paper/sections/01_intro.tex:44–48`).

Were both true they would jointly imply Tutte's 5-flow conjecture.

**Krawczyk operator / Krawczyk–Moore theorem.** For a polynomial system
`F : ℝⁿ → ℝⁿ` and an interval box `I` with centre `c`, the **Krawczyk
operator** is `K(I) = c − YF(c) + (E − YJ(I))(I − c)` with `Y = J(c)⁻¹`
and `J(I)` an interval Jacobian enclosure. **Krawczyk–Moore:** if
`K(I) ⊂ int(I)` componentwise, then `F` has a unique root in `I` and the
Jacobian is nonsingular there (`paper/sections/03_certification.tex` §3.3).
An **interval certificate** is a JSON bundle (schema v2: graph6, edge order,
pinning data, system SHA-256, 50-digit centre, per-coordinate margins)
letting an independent verifier reconstruct the system from the graph alone
and re-check containment in its own interval kernel.

### Status

- **PROVED (finite theorem; computer-assisted).** *Every nontrivial snark
  on at most 28 vertices admits an `S²`-flow* (`THEOREM.md:5–7`). For each
  of the 3 247 nontrivial snarks on `n ∈ {10, 18, 20, 22, 24, 26, 28}`
  (BGHM 2013 enumeration; `n = 28` via `snarkhunter`): Levenberg–Marquardt
  witness, Newton refinement at 50 decimal digits in `mpmath`, Krawczyk
  certificate on a box of radius `10⁻⁵`. All 3 247 certificates are
  independently replayable from the committed `graph6` strings and
  SHA-256 manifest.

- **OPEN.** *Jain's first conjecture:* every bridgeless graph admits an
  `S²`-flow. The finite theorem covers a bounded class and does not imply
  the conjecture for any infinite family (`THEOREM.md:115–118`).

- **REFUTED — by Ulyanov 2026, not by this project.** Jain's *second*
  (finite-labeling) conjecture is disproved in Ulyanov, arXiv:2603.23328
  (2026), via two finite point-set obstructions (a 25-antipodal-pair SAT
  instance and a 36-point Lean 4 / `bv_decide` instance at extended label
  range `{±1, …, ±5}`; `paper/sections/01_intro.tex:51–58`). The first
  (`S²`-flow) conjecture is untouched. The earlier overview phrasing
  "quaternion-flow conjecture" was a misdescription: no `S³` or quaternion
  claim appears anywhere in Jain, Ulyanov, or this project
  (`FIX_VERIFICATION_2026_05_18.md:162–171`).

- **NEGATIVE result (intra-project; not a refutation of any Jain
  conjecture).** Symmetric ansätze for the flower-snark family `J_{2k+1}`
  are obstructed: the `ℤ/(2n)`-equivariant ansatz forces `u_b = 0` in
  closed form; the `ℤ/n`-equivariant ansatz admits no numerical solution
  for `n ∈ {5, 7, 9, 11, 13}` over 1 280 random initialisations
  (`docs/flower_snarks.md`). This rules out one construction technique
  only; `J_{2k+1}` with `2k+1 ≤ 28` are still covered (with non-symmetric
  flows) by the finite theorem.

Preprint complete (`paper/main.tex`, 5 sections). Regression suite: **184
tests**, plus replay of **3 247** interval certificates.

### Layout

- `docs/` — `plan.md` (phases 1–4), literature review, flower-snark analysis,
  cycle-double-cover obstruction notes.
- `scripts/` — `catalogue.py` (snark enumeration + SAT filter), `sweep.py`
  (numerical witness), `interval.py` (Krawczyk certifier), `verify_sweep.py`
  (replay verifier).
- `data/` — 3,247 snark catalogue (g6), witness JSON, 3,247 interval certificates
  (schema v2), manifest with SHA-256 provenance.
- `tests/` — 184 regression tests; negative calibration confirms rejection of bridged
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
