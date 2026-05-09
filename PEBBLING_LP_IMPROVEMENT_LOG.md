# Pebbling certificate improvement log: $L\Box L$ at $(v_1, v_1)$

This file tracks progress on tightening the upper bound for
$\pi(L\Box L, (v_1, v_1))$ via column generation on top of Hurlbert
2017 Theorem 10's four published basic-row strategies.

All bounds in this file are **rationally checked** by
`scripts/check_pebbling_weight_certificate.py` and pinned by tests in
`tests/`. The exact $\sum_i \alpha_i b_i$ value is recorded so a future
rationalization improvement (e.g. exact LP) can re-derive whether the
"derived bound" can drop further.

## Timeline

| Date | Method | Master LP value (rational) | $\lfloor\,\rfloor + 1$ | Notes |
|---|---|---|---:|---|
| 1989 | Graham conjecture | — | $\le 64$ | tight lower bound, $\pi\ge\lvert V\rvert=64$ |
| 2017 | Hurlbert WFL Theorem 10 | $107$ | **108** | 4 published basic-row strategies, $\alpha=(1/4)^4$ |
| 2024 | Flocco-Pulaj-Yerger | (96 published; not locally checked) | $\le 96$ | MILP-driven tree-strategy search |
| this proj | branch decomposition | $107$ | $108$ | no improvement; LP optimal at uniform $\alpha$ |
| this proj | shortest-path single-anchor | $107$ | $108$ | 63 candidates, all $\alpha=0$ in LP |
| this proj | path columns max_len=5 | $47021/440$ | **107** | LP genuinely below 107 |
| this proj | path columns max_len=7 (D=4800) | $169327/1600$ | **106** | round-and-fix bumps |

The float LP optima for higher `max_len` (recorded in
`scripts/run_column_generation*.py` runs):

| max_len | n_paths | float LP | rationalized $\sum\alpha b$ | derived |
|---:|---:|---:|---|---:|
| 5 | 9676 | 106.866 | 47021/440 | 107 |
| 6 | 54050 | 106.008 | 12721/120 (approx) | 107 |
| 7 | 292986 | 105.765 | 169327/1600 | **106** |
| 8 | 1557696 | 105.519 | 507647/4800 | 106 |

**max_len=7 is the smallest where the derived bound drops to 106.** The
LP value continues to improve at max_len=8 but the rationalization
bumps push it back above 105 + 1, so the integer derived bound stays
at 106.

## Method summary

Column-generation pass:

1. Start from Hurlbert's four-strategy certificate decomposed by
   root-branch (six basic-row columns).
2. Enumerate all simple paths from root in $L_{\rm fpy}\Box L_{\rm fpy}$
   of length 2 to `max_len`. Each path induces a basic Hurlbert path
   strategy (leaf weight 1, doubling toward root).
3. Solve the master LP with all candidate columns added at once via
   SciPy HiGHS dual simplex.
4. Identify the active subset (alpha > 1e-9 at the LP optimum) and
   re-solve the reduced LP for numerical stability.
5. Rationalize alpha:
   - First: square Gauss-Jordan in `Fraction` over linearly independent
     tight rows (clean case: max_len=5 yielded $47021/440$ exactly).
   - Fallback: round to common denominator $D$ (e.g. 4800), then
     iteratively bump any alpha contributing to a violated
     dual-feasibility constraint by `deficit / T_i(v) * (1/D)`,
     rounded up to one denominator step. This inflates
     $\sum \alpha_i b_i$ slightly above the LP optimum but yields a
     rationally checkable certificate.
6. Verify dual feasibility rationally on every non-root vertex and
   feed to the existing rational checker.

## Globalization to all root orbits

After improving the rooted bound at $(v_1, v_1) = (4, 4)_{\rm fpy}$ to
106 with Hurlbert + paths, the same path-based pipeline was extended to
every orbit representative of $V(L_{\rm fpy})\times V(L_{\rm fpy})$ under
$\mathrm{Aut}(L_{\rm fpy})\times Z_2$ (coordinate swap):

- $\lvert\mathrm{Aut}(L_{\rm fpy})\rvert = 6$ ($S_3$ on the three
  degree-3 vertices $\{4, 5, 6\}$).
- 22 root orbits totalling 64 vertices (size distribution
  $6\times 6 + 1\times 3 + 10\times 2 + 5\times 1$).

Per-orbit certificates produced and rationally checked. Aggregating the
best certificate per orbit gives:

| Configuration | Global bound | Worst orbit |
|---|---:|---|
| paths max_len=5 | 280 | (0, 1) |
| paths max_len=7 (best per orbit) | **246** | (0, 0) |
| FPY 2024 (paper, not locally re-checked) | $\le 96$ | — |

The 246 bound is fully **local and rational**: every per-orbit
certificate is verified by `check_pebbling_weight_certificate.py`,
and the global bound is the max over those verified bounds.

### Per-orbit rooted bounds at the 246 milestone

| orbit rep | bound | method |
|---|---:|---|
| (0, 0) | 246 | path max_len=7 |
| (0, 1) | 229 | path max_len=7 |
| (1, 1) | 213 | path max_len=7 |
| (0, 4) | 196 | path max_len=7 |
| (4, 4) | 185 | path max_len=5 (locally we have 106 with Hurlbert+paths but not yet ported here) |
| (4, 5) | 185 | path max_len=5 |
| (0, 2) | 173 | path max_len=7 |
| (1, 4) | 177 | path max_len=7 |
| (1, 7) | 173 | path max_len=7 |
| (1, 2) | 169 | path max_len=7 |
| (1, 3) | 161 | path max_len=7 |
| (0, 7) | 179 | path max_len=7 |
| (4, 7) | 176 | path max_len=5 |
| (0, 3) | 156 | path max_len=5 + Y-trees |
| (2, 4) | 153 | path max_len=7 |
| (3, 4) | 151 | path max_len=5 |
| (2, 7) | 141 | path max_len=7 |
| (3, 7) | 136 | path max_len=5 |
| (2, 2) | 136 | path max_len=7 |
| (7, 7) | 154 | path max_len=6 |
| (2, 3) | 120 | path max_len=7 |
| (3, 3) | 113 | path max_len=5 |

### Pricing-oracle experiments at root (0, 0)

Sparse column generation (`scripts/run_sparse_column_generation.py`)
with the path max_len=7 seed certificate at root (0, 0) gives float
LP optimum 245.533 = 196723/800 (rationalized). Branch-and-bound DFS
pricing for *basic uniform-leaf-depth* Hurlbert tree strategies under
this LP's dual:

| strategy class | parameters | nodes / time | improving column? |
|---|---|---:|---:|
| basic uniform-leaf-depth | depth ≤ 5 | 32,998,361 / 30 s | none |
| basic uniform-leaf-depth | depth ≤ 6 | 128,025,839 / 120 s | none |
| basic uniform-leaf-depth | depth ≤ 7 | 196,674,777 / 180 s | none |
| nonbasic single-branch | weights ≤ 32, support ≤ 12 | 75,237,875 / 30 s | none |

Conclusion (real, not engineering): under the LP dual at root (0, 0)
seeded by `path_orbit_0_0_max_len7.json`, no basic Hurlbert tree
strategy with all leaves at the same depth and depth at most 7
(weights at most 2^6 = 64) has negative reduced cost. By LP duality,
the LP optimum 245.533 is LP-optimal across that strategy class; the
rationalized derived bound 246 is the best achievable. Beating 246
requires either non-basic strategies (allowing different child
weights at the same parent), trees deeper than 7, or a different
strategy class entirely.

### Branching-tree experiments

Y-tree, trident, and Pi-tree column generation
(`scripts/branching_tree_columns.py`) was run on the worst orbits at
branching depth 4 with paths max_len=5:

- (0, 1): 280 → 272 with branching, but max_len=7 path-only gave 229.
  Longer paths beat branching here.
- (1, 1): 259 → 226 with branching; max_len=7 paths give 213. Paths win.
- (0, 4): 238 → 224 with branching; max_len=7 paths give 196. Paths win.
- (0, 0): no improvement at branching depth 4. Branching depth 5
  hits OOM (combinatorial enumeration explodes).

Conclusion: at this stage the LP is dominated by single-path columns
even when richer trees are available, because the LP is degenerate and
the round-and-fix rationalization inflates branching trees more than
paths. To genuinely beat the 246 bound, need either (i) Hurlbert-style
hand-crafted strategies for non-(4,4) diagonal roots, (ii) exact
rational LP solver, or (iii) MILP-driven strategy search.

## Known limitations / next steps

- **The 106 certificate is not LP-optimal.** Round-and-fix at $D=4800$
  inflates $\sum\alpha b$ from $\approx 105.76$ (LP) to $169327/1600
  \approx 105.83$. An exact rational LP solver would drop the
  rationalized value to within an $\epsilon$ of the LP optimum, but
  the derived bound (which only depends on the floor) is unchanged at
  this precision.
- **The LP value continues to improve with longer paths**, but the
  derived integer bound has stalled at 106 since max_len=7. To break
  below 106 we'd need the **rationalized** LP value to drop below 105,
  which would require either:
  - much longer paths (combinatorial explosion past max_len=10);
  - branching tree strategies (richer support per b_T cost);
  - different strategy classes (non-tree weight functions per
    Yang-Yerger-Zhou 2024);
  - the FPY 96 certificate ingested with proper format decoding.
- **No reduced-cost-based pricing oracle was used.** SciPy's dual y in
  this LP is highly degenerate (multiple optimal duals); column
  selection by reduced cost under one specific y is misleading.
  Brute-force enumeration plus LP test was more reliable.
