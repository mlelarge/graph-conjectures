# 25 — Parallel closure status: R3-star and Appendix B catalogue

Date: 2026-05-17

This memo integrates the three parallel tasks launched after the Route-B
near-split decision point:

1. structural inspection of R3-star via the Bang-Jensen--Wang construction;
2. strict-split obstruction catalogue cleanup;
3. Appendix B.3 figure audit.

## 1. Structural branch: R3-star not closed by BJ-Wang inspection

Output: `team/22_r3star_bjwang_inspection.md`.

Conclusion:

- Direct inspection of Bang-Jensen--Wang Lemma 2.4 / Lemma 2.5 /
  Corollary 1 does **not** close R3-star.
- The published construction is side-blind at the contracted vertex
  \(r=p^\bullet\): it tracks arcs incident with \(r\), but not whether
  each arc came from \(p\) or from \(q\).
- That lost side-label information is precisely what un-contraction needs.

The structural memo also sharpens the residual condition. The old shorthand
"some \(q\)-reaching color" is too weak. The actual liftability condition is:

\[
\exists i\in\{1,2\}\quad
D_i^\flat+e_0\text{ is strong and }D_{3-i}^\flat\text{ is strong}.
\]

Equivalently, with \(P_i\) denoting a \(p\to q\) path and \(Q_i\) a
\(q\to p\) path in color \(i\) after un-contraction but before adding
\(e_0=(p,q)\):

\[
(Q_1\wedge P_2\wedge Q_2)\quad\text{or}\quad
(Q_2\wedge P_1\wedge Q_1).
\]

Next mathematical move:

> Prove a side-compatible SAD-coloring lemma for the contracted split
> multi-digraph, or first prove it in the direct kernel-shell case where
> \(D^\bullet[V_2]\) already has a SAD.

## 2. Catalogue branch: B.2 and reliable B.3 indexed

Initial output: `team/23_near_split_index_cleanup.md`.

The coder added:

- Appendix B.2 cases `(i)`, `(ii)`, `(iii)`;
- reliable Appendix B.3 UNSAT products then known safe;
- a shared `strict_split_unsat_benchmarks()` catalogue;
- arc-reverse indexing in both near-split drivers.

After the auditor resolved the five B.3 mismatches, `code/benchmarks.py` was
extended further to include the corrected 14-arc B.3 cores:

- `(i)^* x (iii)`;
- `(ii)^* x (iii)`;
- `(iii)^* x (iii)`;
- `(iii)^* x (iv)`;
- `(iii)^* x (v)`.

Current catalogue state:

- `all_benchmarks()` has 25 entries.
- `strict_split_unsat_benchmarks()` has 17 forward entries.
- `_strict_split_unsat_canonical_keys()` has 26 unique forward/reverse hashes.

Verification:

```bash
uv run python run_benchmarks.py
```

Result:

- 25/25 benchmarks passed.
- Every strict-split UNSAT catalogue entry has \(\lambda^{\rm arc}=2\).
- ILP and SAT agree on every benchmark.

## 3. Auditor branch: B.3 mismatch cause resolved

Output: `team/24_appendix_b3_figure_audit.md`.

Conclusion:

- The five B.3 paper-UNSAT / verifier-SAT mismatches were caused by **extra
  arcs**, not missing dashed arcs.
- The team encoding had incorrectly included \(v_2\to a\) in unstarred
  `(iii)` and `(v)`.
- Under the star operation, that same error became an extra \(b\to v_3\) in
  `(iii)^*` and `(v)^*`.
- Removing those extra arcs gives 14-arc cores for all B.3 cases.
- The five formerly mismatching cases are ILP=UNSAT, SAT=UNSAT, and
  brute-force UNSAT, matching the paper.

The corrected solid-core B.3 catalogue is now safe to use.

## 4. Corrected `(2,3)` near-split count

Command:

```bash
uv run python run_route_b_ns_exhaustive_l2.py --pairs "(2,3)" --instance-time-s 6 --log-tag cleanup_b3_full
```

Log:

`code/logs/route_b_ns_exh_l2_cleanup_b3_full_20260517_081322.json`

Results:

| Quantity | Value |
|---|---:|
| Enumerated | 221184 |
| \(\lambda=2\) instances | 20496 |
| \(\lambda=3\) instances | 192 |
| Canonical \(\lambda=2\) UNSAT | 10 |
| Strict-split extensions | 4 |
| NEW \((1,0)\)-near-split-specific obstructions | 6 |
| \(\lambda=3\) UNSAT counterexamples | 0 |

The six NEW obstruction hashes remain:

- `10d4d95c9bfa0684...`
- `9ad968a78d3f2357...`
- `5dada8a30f447291...`
- `1ce848bfe32fdba1...`
- `6bff7c1524259196...`
- `b28c5b6c5c481ca6...`

Thus full B.3 indexing does **not** reduce the residual NEW count below 6.
Those six are still genuinely internal-arc-dependent in the current
\((2,3)\) exhaustive sweep.

## 5. Current Route-B status

| Component | Status |
|---|---|
| 3-arc-strong \((1,0)\)-near-split theorem | Conditional; proof reduced to side-compatible R3-star lemma |
| BJ-Wang-inspection route for R3-star | Failed as a complete proof; construction is side-blind |
| Next proof route | SAD-coloring polytope / side-compatible attachment lemma |
| 2-arc-strong companion exception family | Corrected NEW count = 6 in \((2,3)\) sweep |
| Appendix B strict-split catalogue | Complete for B.2 and B.3 solid-core cases |
| Verifier status | 25/25 benchmarks pass; ILP/SAT agree |

## 6. Recommended next action

Stop spending time on Appendix B indexing for now. The catalogue is good enough.

The main mathematical task is now:

> Prove the side-compatible SAD-coloring lemma, starting with the direct
> kernel-shell case where \(D^\bullet[V_2]\) already has a SAD.

If the direct kernel-shell lemma fails, search for a small counterexample to
R3-star inside the contracted split multi-digraph model. If it holds, extend
the argument to the splitting-off cases used in Bang-Jensen--Wang Theorem 1.6.

