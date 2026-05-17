# Near-Split Strict-Split Index Cleanup

Date: 2026-05-17

## Scope

Implemented the Lead's cleanup request for the Bang-Jensen--Yeo near-split
route:

- extend the strict-split UNSAT canonical-key index with verified Appendix
  B.2 and B.3 entries;
- add canonical benchmarks for reliable Appendix B cases;
- rerun the `(2,3)` exhaustive near-split sweep;
- do not add the five B.3 paper-UNSAT/verifier-SAT mismatch cases.

## Code Changes

Touched only allowed code files:

- `code/benchmarks.py`
  - Added B.2 helpers for `S_{4,-1}` and cases `(i)`, `(ii)`, `(iii)`.
  - Added benchmarks:
    - `AiEtAl_B2_case_i`
    - `AiEtAl_B2_case_ii`
    - `AiEtAl_B2_case_iii`
  - Added B.3 helpers for `S_{4,-2}`, the reliable component cases
    `(i)`, `(ii)`, `(iv)`, and the star operation.
  - Added benchmarks:
    - `AiEtAl_B3_i_star_i`
    - `AiEtAl_B3_i_star_ii`
    - `AiEtAl_B3_i_star_iv`
    - `AiEtAl_B3_ii_star_ii`
    - `AiEtAl_B3_ii_star_iv`
  - Kept existing `AiEtAl_iv_star_iv` as the sixth verified B.3 UNSAT
    iso-class.
  - Added `strict_split_unsat_benchmarks()` as the single safe source for
    strict-split UNSAT catalogue indexing.

- `code/run_route_b_near_split.py`
  - Updated `_strict_split_unsat_canonical_keys()` to consume
    `strict_split_unsat_benchmarks()`.
  - Added arc-reverse indexing for every safe strict-split benchmark.
  - Uses forward names first, then reverse aliases only for otherwise-unused
    hashes.

- `code/run_route_b_ns_exhaustive_l2.py`
  - Same index update as the main near-split driver.

## Source Discipline

B.2 arc lists are exactly the ones recorded in `team/05_audit.md` Appendix
A.9.6:

- B.2 `(i)`: hash `e19fcf9b6d693745...`
- B.2 `(ii)`: hash `c5524d22d2aba648...`
- B.2 `(iii)`: hash `52e5e47f3f76137e...`

B.3 arc lists follow `/tmp/check_b3_minimal.py`, which is the script cited by
`team/05_audit.md` Appendix A.9.4 and reproduces the audit hashes:

- `(i)* x (i)`: `92edbcb1560d099f...`
- `(i)* x (ii)`: `dc835befa7a474f0...`
- `(i)* x (iv)`: `e6e7a2494bfa5cd4...`
- `(ii)* x (ii)`: `10fae725561067fd...`
- `(ii)* x (iv)`: `0cab4a53e5e81027...`
- `(iv)* x (iv)`: `2970657e95d7b8ad...` already existed as
  `AiEtAl_iv_star_iv`.

I did not use `/tmp/appendix_b_verify.py` as the B.3 source because it
disagrees with the audit-final B.3 table for several products. The committed
B.3 constructors follow the audit-final `/tmp/check_b3_minimal.py` source.

The five unresolved B.3 paper-UNSAT/verifier-SAT mismatch cases involving
configurations `(iii)` or `(v)` remain excluded. No dashed-arc guess was
committed.

## Verification Commands

Run from `problems/arc_disjoint_strong_spanning_subdigraphs/code`:

```bash
uv run python benchmarks.py
uv run python -c "from benchmarks import all_benchmarks, strict_split_unsat_benchmarks; from generators.canonicalize import canonical_key; print('all', len(all_benchmarks()), 'strict', len(strict_split_unsat_benchmarks())); [print(f'{b.name:24s} {canonical_key(b.build())[:16]}') for b in strict_split_unsat_benchmarks()]"
uv run python run_benchmarks.py
uv run python -c "from run_route_b_ns_exhaustive_l2 import _strict_split_unsat_canonical_keys; idx=_strict_split_unsat_canonical_keys(); print(len(idx)); [print(k[:16], idx[k]) for k in sorted(idx) if idx[k].startswith('AiEtAl_B2') or idx[k].startswith('AiEtAl_B3')]"
uv run python run_route_b_ns_exhaustive_l2.py --pairs "(2,3)" --instance-time-s 6 --log-tag cleanup_final
```

## Results

Benchmark suite:

- 20/20 passed.
- Every new B.2/B.3 benchmark is `lambda^arc = 2`, expected `UNSAT`, and
  verified `UNSAT` by both ILP and SAT.
- No ILP/SAT disagreements.

Strict-split index:

- `strict_split_unsat_benchmarks()` has 12 forward catalogue entries.
- `_strict_split_unsat_canonical_keys()` has 17 unique forward/reverse hashes.
- The B.2 hashes now resolve to the intended forward names:
  - `e19fcf9b6d693745...` -> `AiEtAl_B2_case_i`
  - `c5524d22d2aba648...` -> `AiEtAl_B2_case_ii`
  - `52e5e47f3f76137e...` -> `AiEtAl_B2_case_iii`

Final `(2,3)` exhaustive rerun:

- Log:
  `code/logs/route_b_ns_exh_l2_cleanup_final_20260517_080529.json`
- Enumerated: 221184
- `lambda = 2`: 20496
- `lambda = 3`: 192
- Canonical lambda-2 UNSAT: 10
- Strict-split extensions: 4
- Corrected `NEW`: 6
- Lambda-3 UNSAT counterexamples: 0

The four strict-split extensions are:

- `35aa1b8c23ebc9b3...` -> `AiEtAl_L211_min_arcrev`
- `52e5e47f3f76137e...` -> `AiEtAl_B2_case_iii`
- `14654037f4046821...` -> `AiEtAl_L211_min`
- `c5524d22d2aba648...` -> `AiEtAl_B2_case_ii`

The six remaining `NEW` hashes are:

- `10d4d95c9bfa0684...`
- `9ad968a78d3f2357...`
- `5dada8a30f447291...`
- `1ce848bfe32fdba1...`
- `6bff7c1524259196...`
- `b28c5b6c5c481ca6...`

## Blockers

- The five B.3 mismatch cases involving `(iii)` or `(v)` still require the
  Auditor's dashed-arc figure read or a cleaner publication source. They are
  not safe benchmark material yet.
- I reran the requested `(2,3)` exhaustive sweep. I did not rerun the full
  default `(2,3),(3,3),(2,4)` exhaustive set because the latter two are much
  larger enumerations and were not needed to establish the corrected `(2,3)`
  count.
