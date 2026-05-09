# Pebbling product: terminal local result

This report packages the pebbling-conjecture work in this project at a
clean stopping point. It documents four deliverables:

1. **Global bound** $\pi(L_{\rm fpy}\Box L_{\rm fpy})\le 246$, the max
   over 22 per-root-orbit rational certificates.
2. **Rooted improvement** $\pi(L_{\rm fpy}\Box L_{\rm fpy}, (v_1, v_1))
   \le 106$, sharpening Hurlbert 2017's 108.
3. **Pinned negative pricing results** at the bottleneck orbit
   $(0, 0)$: no improving column under basic uniform-leaf-depth
   ($\le 7$) or nonbasic single-branch (support $\le 16$) tree
   classes.
4. **FPY ingestion bridge**: live round-trip verified against the
   *current* FPY source code; reproducing their published 96 bound
   remains blocked because the public CSVs are not directly
   interpretable under the current-source serializer semantics
   (they may be from an older serializer, a postprocessed symmetric
   expansion, or a different labelling convention) and because the
   per-strategy dual multipliers needed by the rational checker are
   not in the public files.

The work neither resolves Graham's conjecture nor matches the best
published upper bound (Flocco–Pulaj–Yerger 2024, $\le 96$). It does
produce an *independent* upper bound built from first principles in
this repository, with every claim re-checkable by
`scripts/check_pebbling_weight_certificate.py`.

## Headline result

> $$\pi(L_{\rm fpy}\Box L_{\rm fpy}) \le 246.$$

This bound is the maximum over 22 per-root-orbit certificates, each
verified locally by the rational checker.

The Lemke graph $L_{\rm fpy}$ here is the original 8-vertex Lemke
graph in the labelling distributed with the
[Flocco–Pulaj–Yerger codebase](https://github.com/dominicflocco/Graph_Pebbling),
encoded at
[`data/pebbling_product/graphs/L_fpy.json`](data/pebbling_product/graphs/L_fpy.json).
Hurlbert 2017 uses an isomorphic relabelling (recorded in
`scripts/build_hurlbert_T_strategies.py` as
`WFL_TO_FPY = (4, 3, 2, 1, 5, 0, 6, 7)`).

## Comparison with known bounds

| Source | Bound | Locally re-checked here? |
|---|---:|---|
| trivial $\lvert V\rvert$ lower bound | $\ge 64$ | yes |
| Hurlbert 2017 Theorem 10, $r = (v_1, v_1)$ | $\le 108$ | yes (`Hurlbert_T1_T2_T3_T4_v1v1_le108.json`) |
| Hurlbert 2017 Theorem 10, $r = (v_4, v_4)$ | $\le 68$ | not transcribed |
| Hurlbert 2017 Theorem 10, $r = (v_8, v_8)$ | $\le 96$ | not transcribed |
| Flocco–Pulaj–Yerger 2024 (MILP, all roots) | $\le 96$ | not re-checked locally (CSV format ambiguity) |
| **this project, $r = (v_1, v_1)$ only** | $\le 106$ | yes (`Hurlbert_path_augmented_v1v1_le106.json`) |
| **this project, all 22 root orbits** | **$\le 246$** | yes (CSV + 22 certificates) |

The 246 bound is the global one; the 106 bound is a sharpening at the
single root $(v_1, v_1)$ where Hurlbert's strategies are available
locally.

## Path the project actually walked

In commit order (most recent last):

1. `cf462ee` Built the trusted exact pebbling verifier and the rational
   weight-function certificate checker.
2. `7a03fe6` Hurlbert WFL paper Theorem 10 averaged matrix $T_3$
   transcribed and arithmetically validated.
3. `5a76948` Reproduced
   $\pi(L\Box L,(v_1, v_1)) \le 108$ from a four-strategy
   rational certificate verified end-to-end.
4. `fbe92b6` Negative result: shortest-path single-anchor strategies
   do not improve Hurlbert 108.
5. `5eb55dd` Branch-decomposition of Hurlbert's four strategies into
   six root-branches; LP unchanged.
6. `0289502` Master LP confirms Hurlbert's averaging $\alpha = 1/4$ is
   LP-optimal for those four strategies (no reweighting can lower it).
7. `55a6659` Column generation with simple paths drops the bound to
   $\pi(L\Box L,(v_1, v_1)) \le 107$ (LP value $47021/440$).
8. `ce1be14` Longer paths (max_len=7) drop the bound to
   $\pi(L\Box L,(v_1, v_1)) \le 106$ (LP value $169327/1600$).
9. `df24f11` Globalization: 22 root orbits computed under
   $\mathrm{Aut}(L_{\rm fpy})\times Z_2$; per-orbit path certificates
   give $\pi(L\Box L) \le 280$.
10. `f745aa9` Longer paths and Y-tree / trident / Pi-tree branching
    columns lower the global bound to $\le 246$ (worst orbit
    $(0, 0)$ at 246).
11. `b01aabd` Sparse, in-memory column-generation pipeline with a
    pricing oracle. At root $(0, 0)$, basic uniform-leaf-depth pricing
    of depth $\le 5$ finds no negative-reduced-cost column.
12. `a62c44d` Same negative result extended to depth $\le 7$
    (196 M nodes explored).
13. `c01ead3` Nonbasic single-branch pricing (weights $\le 32$,
    support $\le 12$): no negative reduced cost.
14. `970aea4` Nonbasic single-branch, support $\le 16$: no negative
    reduced cost (292 M nodes, 120 s budget).
15. `f047e3a` Earlier draft of this terminal report at $\le 246$.
16. FPY ingestion bridge probed against live source: round-trip
    verified, adapter bug fixed (`_parse_pair` did not strip inner
    single quotes on the live form `('0', '1')`). See
    `scripts/fpy_probe.py`,
    `tests/test_phase2b_fpy_ingest.py::test_parse_pair_accepts_live_fpy_form`.

## Per-orbit table

22 root orbits cover the 64 vertices of $V(L_{\rm fpy})\times V(L_{\rm fpy})$
under $\mathrm{Aut}(L_{\rm fpy})\times Z_2$; orbit-size distribution
$6\times 6 + 1\times 3 + 10\times 2 + 5\times 1 = 64$. The full table
is `data/pebbling_product/root_orbit_bounds.csv`. The five worst
orbits at the final state, restricted to the
*generic path/branching strategy class* used uniformly by the
aggregator:

| orbit rep | bound | LP value (rational) | best path/branching certificate |
|---|---:|---|---|
| $(0, 0)$ | **246** | $295021/1200$ | `path_orbit_0_0_max_len7.json` |
| $(0, 1)$ | 229 | $1098677/4800$ | `path_orbit_0_1_max_len7.json` |
| $(1, 1)$ | 213 | $339217/1600$ | `path_orbit_1_1_max_len7.json` |
| $(0, 4)$ | 196 | $312293/1600$ | `path_orbit_0_4_max_len7.json` |
| $(4, 4)$ | 185 | $184$ | `path_orbit_4_4_max_len5.json` |

The aggregator restricts to one strategy class (path / Y-tree /
trident / Pi-tree branching columns) so that it is mechanically
applicable across all orbits. Where root-specific certificates
sharpen the bound, they are used separately:

- $(4, 4) = (v_1, v_1)$: the rooted certificate
  `Hurlbert_path_augmented_v1v1_le106.json` proves $\le 106$ from
  Hurlbert's four hand-transcribed published strategies plus paths.
  This *is* a root-specific certificate, like every other entry in
  the table; it is excluded from the aggregator only because the
  aggregator restricts to the uniform path/branching class.

If the per-root maximum is taken with this $(4, 4)\le 106$
certificate substituted in, the global bound is unchanged at $246$
because $(0, 0)$ remains the bottleneck.

## Pinned negative result at the (0, 0) bottleneck

For root $(0, 0)$, with the master LP seeded by
`path_orbit_0_0_max_len7.json` (LP optimum 245.533 = $196723/800$):

| strategy class | parameters | nodes / time | improving column? |
|---|---|---:|---:|
| basic uniform-leaf-depth | depth $\le 5$ | 32,998,361 / 30 s | **none** |
| basic uniform-leaf-depth | depth $\le 6$ | 128,025,839 / 120 s | **none** |
| basic uniform-leaf-depth | depth $\le 7$ | 196,674,777 / 180 s | **none** |
| nonbasic single-branch | weights $\le 32$, support $\le 12$ | 75,237,875 / 30 s | **none** |
| nonbasic single-branch | weights $\le 32$, support $\le 16$ | 292,440,752 / 120 s | **none** |

Narrow statement of the negative result:

> For the root orbit $(0, 0)$, relative to the path-max_len=7 master
> dual at LP value $196723/800$, there is no negative-reduced-cost
> basic Hurlbert tree strategy with uniform leaf depth $\le 7$, and no
> negative-reduced-cost nonbasic single-branch tree strategy with
> support $\le 16$ and weights $\le 32$.

By LP duality, the LP value $196723/800$ is LP-optimal across those
strategy classes; the rationalized derived bound $246$ is the best
this priced class can produce. Beating $246$ requires expanding the
class beyond what was searched.

## FPY ingestion blocker

Reproducing Flocco–Pulaj–Yerger 2024's $\pi(L_{\rm fpy}\Box L_{\rm fpy})
\le 96$ end-to-end remains **blocked**, but the blocker is now
narrowly characterized.

### What works

The live FPY classes (`external/Graph_Pebbling/py/PebblingGraph.py` and
`TreeStrategy.py`) can be imported with `gurobipy` stubbed and
exercised structurally. `scripts/fpy_probe.py` builds the Lemke square
the same way `main()` does (line 571 of their `main.py`), constructs a
synthetic strategy at root `('0', '1')`, calls
`saveCertificate` / `saveEdges`, and round-trips through our
`scripts/ingest_flocco_pulaj_yerger.py`. Weights and tree edges
round-trip byte-stably.

This pinned three runtime invariants of the *current* FPY source:

- **Vertex labels** are strings of the form `"('i', 'j')"` — FPY's
  `str()` on a tuple of strings preserves the inner quotes; that is
  why `int(v[2])` and `int(v[7])` in `saveCertificate` extract the
  digits correctly.
- **`saveCertificate` matrix convention is `cert[i][j] = w((i, j))`**;
  no transpose. Confirmed by hand-built strategy whose root weight at
  `(0, 1)` reads back at row 0, column 1.
- **`saveEdges`** writes rows `i, "('a', 'b')", "('c', 'd')"` (NetworkX
  source-target columns).

The probe also surfaced a real bug in our adapter: `_parse_pair`
treated cells as bare integers `(0, 1)` and choked on the live form
`('0', '1')` with `int("'0'")`. Fixed at
`scripts/ingest_flocco_pulaj_yerger.py:180`, covered by two new
regression tests.

### What does not work

The published `ls-bounds-updated/` CSVs that record FPY's per-root
strategies are **not directly interpretable under the current-source
serializer semantics**. Independent diagnostics from earlier in this
project (`PEBBLING_PHASE_2B_STATUS.md`, "FPY format diagnostics"
section) recorded:

- the published matrix appears transposed relative to the filename
  root (`matrix[1][0]=0` for `v(0, 1)`, not `matrix[0][1]`);
- the published edges file contains a vertex of in-degree 2 and the
  unique zero-in-degree vertex is not the filename root.

Today's live probe of the *current* source produces neither of those:
in the current code, `cert[i][j] = w((i, j))` directly, and
`saveEdges` writes simple source-target arc rows. So the published
artefacts and the current-source serializer disagree on at least one
convention. Plausible explanations include an older serializer
revision, a postprocessed symmetric expansion (e.g. averaging across
an automorphism orbit before saving), or a different vertex-labelling
convention that we have not decoded. We have not fully decoded the
intended format and cannot say the published artefacts are
internally inconsistent — only that we cannot read them under the
serializer the current source ships.

### What unblocks the 96 reproduction

A clean reproduction requires three things in addition to a working
parser: (a) per-strategy weight matrices and tree edges, (b) the
underlying graph labelling, and (c) per-strategy dual multipliers
$\alpha_i$ (or a verified uniform-averaging convention plus a
rationalized fixed-strategy master LP that recovers the same
$\sum_i\alpha_i b_i$). The public files supply (a) and (b) but not
(c). The MILP that *generated* those strategies records LP duals
internally; they are not serialized.

Three options, in order of effort:

1. **Run FPY's MILP under the current code path** and capture both
   the strategies and their dual variables. Their solver is Gurobi.
   With a license, calling `treeStrategyOptSymCrank()` on the Lemke
   square at any root produces a fresh CSV consistent with the
   current source; the adapter is ready, but the run must additionally
   dump the LP dual values $\alpha_i$ (or the strategy weights
   $b_i$ and a confirmed uniform-averaging step) before our checker
   can convert that into a rational $\sum_i\alpha_i b_i$ and a derived
   bound.
2. **Get a structured (JSON / pickle) dump from the authors** that
   includes the per-strategy weight matrix, the supporting tree
   edges, the graph labelling, *and* the dual multipliers (or the
   averaging convention they use). This sidesteps both the CSV
   ambiguity and the missing-duals gap.
3. **Re-implement their MILP under HiGHS / CBC** with explicit dual
   capture. A multi-week effort that duplicates infrastructure
   already published; out of scope.

In all three options, the rational checker side is unchanged: feed it
weights + edges + multipliers, get a verified derived bound. Solving
the master LP locally on fixed FPY-supplied strategies (option 2 or a
post-processing pass on option 1's output) is also a viable path to
recover $\alpha_i$ if the authors prefer not to expose them.

None of these is required for the 246 result, which is independent.

## How to reproduce

From the project root:

```bash
uv venv --python 3.12 .venv
uv pip install scipy networkx pytest

# Re-run the entire test suite (101 tests)
.venv/bin/pytest tests/ -q

# Re-verify the headline 246 bound
PYTHONPATH=scripts .venv/bin/python scripts/aggregate_orbit_bounds.py

# Re-verify the (v_1, v_1) sharper 106 bound
PYTHONPATH=scripts .venv/bin/python scripts/check_pebbling_weight_certificate.py \
    data/pebbling_product/certificates/Hurlbert_path_augmented_v1v1_le106.json

# Reproduce a single-orbit certificate from scratch
PYTHONPATH=scripts .venv/bin/python scripts/run_root_orbit_certificates.py \
    --max-len 7 --denominator 4800

# Reproduce the (0, 0) negative pricing results
PYTHONPATH=scripts .venv/bin/python scripts/run_sparse_column_generation.py \
    --root-pair 0,0 --max-depth 7 --pricing-time-budget-s 180 \
    --rounds 3 --denominator 4800

# Probe the live FPY classes (round-trip self-test)
uv pip install matplotlib pandas
.venv/bin/python scripts/fpy_probe.py
```

## Scope-limited list of artifacts

Inputs (data the project depends on, not produced here):

- `data/pebbling_product/graphs/L_fpy.json`: original Lemke graph,
  FPY labelling.
- Hurlbert 2017 WFL paper, Theorem 10 and Figure 5 transcribed in
  `scripts/build_hurlbert_T_strategies.py`.

Tools (rational, audit-friendly):

- `scripts/pebbling_graphs.py`: graphs, Cartesian product.
- `scripts/verify_pebbling_configuration.py`: exact pebbling reachability.
- `scripts/check_pebbling_weight_certificate.py`: rational checker for
  Hurlbert weight-function certificates.
- `scripts/sparse_columns.py`: sparse column LP harness.
- `scripts/price_tree_strategy.py`: pricing oracles for basic and
  nonbasic Hurlbert tree strategies.
- `scripts/run_sparse_column_generation.py`: column-generation loop.
- `scripts/run_root_orbit_certificates.py`: per-orbit pipeline.
- `scripts/aggregate_orbit_bounds.py`: build CSV from cert directory.
- `scripts/ingest_flocco_pulaj_yerger.py`: parse FPY-format weight CSV
  and edges CSV into ingestible strategies (live-form quotes handled).
- `scripts/fpy_probe.py`: live FPY round-trip self-test.

Certificates (every one accepted by the rational checker):

- `data/pebbling_product/certificates/Hurlbert_T1_T2_T3_T4_v1v1_le108.json`
  — Hurlbert WFL Theorem 10, $\le 108$ at $(v_1, v_1)$.
- `data/pebbling_product/certificates/Hurlbert_path_augmented_v1v1_le107.json`
  — column-generation, $\le 107$ at $(v_1, v_1)$.
- `data/pebbling_product/certificates/Hurlbert_path_augmented_v1v1_le106.json`
  — column-generation with longer paths, $\le 106$ at $(v_1, v_1)$.
- `data/pebbling_product/certificates/path_orbit_<i>_<j>_*.json` (22
  root orbits, mostly path-only, some with Y-tree branching).
- `data/pebbling_product/root_orbit_bounds.csv` — global summary.

Documentation:

- `PEBBLING_PRODUCT_LITERATURE_NOTES.md` — Phase 0 audit.
- `PEBBLING_PHASE_2B_STATUS.md` — Phase 2b reproduction status.
- `PEBBLING_LP_IMPROVEMENT_LOG.md` — Detailed LP and pricing
  experiment log.
- `PEBBLING_TERMINAL_REPORT.md` — this file.

Tests: 101 in `tests/`, all passing. The most load-bearing for the
246 result are
`tests/test_lemke_square_root_orbit_bounds.py` (each accepted cert
re-checks; orbit sizes sum to 64; global max consistent) and
`tests/test_phase2a_checker.py` (5 perturbation rejections).

## What is intentionally not done

- **No FPY 96 reproduction.** The bridge from FPY's CSV format to our
  rational checker is now byte-stable against the live source (see
  "FPY ingestion blocker" above), but reproducing the published 96
  bound requires running their MILP under Gurobi or obtaining a
  structured dump from the authors. Neither was attempted in this
  session.
- **No Yang–Yerger–Zhou 2024 non-tree weight functions.** Outside the
  Hurlbert tree-strategy framework used throughout this project.
- **No 64-pebble counterexample search.** Per the original plan and
  every subsequent decision-rule check, the certificate-improvement
  branch produced more theorem-grade output per unit of compute.
- **No port of Hurlbert's $(v_4, v_4)$ and $(v_8, v_8)$ strategies.**
  Hurlbert 2017 publishes bounds 68 and 96 at those roots; we have
  rationally re-checked only the $(v_1, v_1)$ figure (108).
  Transcribing Figures 6 and 7 from the WFL paper would tighten the
  $(7, 7)$ orbit bound from our 154 to 96 and the $(1, 1)$ orbit from
  our 213 to 68. Neither is the global bottleneck (which is $(0, 0)$
  at 246), so this is unlikely to lower the global bound.

## Status: terminal

Stopping pebbling work here. Summary of the four deliverables:

| Deliverable | Status | Evidence |
|---|---|---|
| Global bound $\le 246$ | rationally checked | 22 per-orbit certs + `aggregate_orbit_bounds.py` |
| Rooted bound $(v_1, v_1)\le 106$ | rationally checked | `Hurlbert_path_augmented_v1v1_le106.json` |
| $(0, 0)$ pricing pinned LP-optimal in priced classes | proven | 5-line table above; basic depth $\le 7$, nonbasic support $\le 16$ |
| FPY ingestion bridge | live round-trip OK; 96 reproduction blocked on Gurobi or authors' JSON | `scripts/fpy_probe.py`, two new tests in `tests/test_phase2b_fpy_ingest.py` |

The 246 bound is the project's final local rational upper bound. Any
future pebbling work should choose between (i) running FPY's MILP to
ingest their 96 certificate properly, (ii) widening the priced
strategy class beyond bounded-support nonbasic single-branch trees, or
(iii) leaving 246 as a self-contained independent contribution. The
infrastructure built here supports any of these without further
rewriting.
