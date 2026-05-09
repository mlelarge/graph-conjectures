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
