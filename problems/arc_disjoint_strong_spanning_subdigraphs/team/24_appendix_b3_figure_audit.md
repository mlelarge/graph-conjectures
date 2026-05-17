# Appendix B.3 figure audit: Ai--He--Li--Qin--Wang 2024

Auditor: Codex.  Date: 2026-05-17.

Scope: resolve the five Appendix B.3 cases where the paper says UNSAT but the
team's current transcription in `team/05_audit.md` Appendix A.9.4 / `/tmp/check_b3_minimal.py`
returns SAT.  The affected cases are
`(i)^* x (iii)`, `(ii)^* x (iii)`, `(iii)^* x (iii)`,
`(iii)^* x (iv)`, and `(iii)^* x (v)`.

Write boundary respected: no code edited.  This file is the only repository edit.

## Sources inspected

- `team/05_audit.md`, especially Appendix A.3, A.4, A.7, A.9.
- `/private/tmp/aietal2024.txt` and `/private/tmp/aihelxqw2024.txt`, especially
  lines 1617--1788, the Appendix B.3 text and proof block.
- `/private/tmp/aihelxqw2024.pdf`, pages 31--34, rendered locally with
  `pdftoppm -f 31 -l 34 -r 300 -png`.
- Rendered inspection images:
  `/private/tmp/ai_b3_page-31.png`, `/private/tmp/ai_b3_page-32.png`,
  `/private/tmp/ai_b3_page-33.png`, `/private/tmp/ai_b3_page-34.png`,
  plus crops `/private/tmp/ai_b3_page31_configs.png` and
  `/private/tmp/ai_b3_page32_starred_configs2.png`.
- Team transcription scripts/output:
  `/private/tmp/check_b3_minimal.py`, `/private/tmp/check_b3_alt.py`,
  `/private/tmp/appendix_b_verify.py`, `/private/tmp/b3_min_out.txt`.

## Verdict

The five mismatches are resolved locally.

They are not caused by missing arcs.  They are caused by two extra arcs in the
team's current B.3 model:

- `v2 -> a` was incorrectly included in unstarred configurations `(iii)` and
  `(v)`.
- Under the paper's `*` operation, that same extra arc becomes `b -> v3`; it was
  incorrectly included in starred configurations `(iii)^*` and `(v)^*`.

After deleting exactly those wrongly promoted arcs, all 15 Appendix B.3
representatives have 14 arcs, lambda_arc = 2, and the verifier agrees with the
paper in every case.  For the five formerly mismatching paper-UNSAT cases, I
also ran an independent brute-force check over all `2^14` arc colorings; all
five are brute-force UNSAT.

The practical rule is:

> In B.3, configurations `(iii)` and `(v)` use `a -> v4` as the second out-arc
> of `a`; they do not use a solid core arc `v2 -> a`.  Consequently
> `(iii)^*` and `(v)^*` do not use a solid core arc `b -> v3`.

Any visually ambiguous/dashed occurrence of those arcs must remain provisional.
Do not promote it to canonical benchmark status.  The canonical paper-core
benchmarks should use the 14-arc versions below.

## Corrected B.3 core model

Use the following vertex convention:

- `V_2 = {v1, v2, v3, v4}`;
- `V_1 = {a, b}`;
- `(e)^* x (f)` means `a` realizes configuration `(f)` and `b` realizes
  configuration `(e)^*`.

The common base is

```text
S_{4,-2}:
v1->v2, v2->v3, v3->v4, v4->v1, v1->v3, v2->v4
```

The common B.3 arcs from the paper text are

```text
v4->a, a->v2, v3->b, b->v1
```

The corrected unstarred extras at `a` are:

| Config | Extra arcs at `a` beyond `v4->a, a->v2` | Comment |
|---|---|---|
| `(i)` | `v2->a, a->v4` | full adjacency to `v2` and `v4` |
| `(ii)` | `v2->a, a->v1` | `a->v1`, not `v1->a` |
| `(iii)` | `v1->a, a->v4` | no solid `v2->a` |
| `(iv)` | `v2->a, a->v3` | matches existing `(iv)^* x (iv)` benchmark |
| `(v)` | `v3->a, a->v4` | no solid `v2->a` |

Applying the paper's `*` operation, i.e. reverse arcs and rotate/relabel by
`v1 <-> v4`, `v2 <-> v3`, `a -> b`, gives the corrected starred extras at `b`:

| Config | Extra arcs at `b` beyond `v3->b, b->v1` |
|---|---|
| `(i)^*` | `b->v3, v1->b` |
| `(ii)^*` | `b->v3, v4->b` |
| `(iii)^*` | `b->v4, v1->b` |
| `(iv)^*` | `b->v3, v2->b` |
| `(v)^*` | `b->v2, v1->b` |

This is the minimal solid-core reading supported by the figures and by the
proof text.  It also makes the paper's degree statements coherent.  For example,
in `(iii)^* x (iii)`, the proof divides `a` into the two paths
`v4-a-v2` and `v1-a-v4`, and divides `b` into `v3-b-v1` and `v1-b-v4`.
The team's old extra arcs `v2->a` and `b->v3` destroy that forced-pairing
argument and, computationally, make the graph SAT.

## The five mismatches

The "current team" column refers to the A.9.4 / `/tmp/check_b3_minimal.py`
encoding, not to a canonical benchmark.  These five current encodings must not
be benchmarked as paper-UNSAT instances.

| Case | Current team extra(s) beyond corrected core | Current m / verdict / hash16 | Paper verdict | Corrected m / checks / hash16 | Confidence | Safe to benchmark? |
|---|---|---|---|---|---|---|
| `(i)^* x (iii)` | erroneous `v2->a` in `(iii)` | `m=15`, SAT, `e3acdbe730421415` | UNSAT | `m=14`, ILP=UNSAT, SAT=UNSAT, brute=UNSAT, `a1f7f5c0affb7c24` | High. The `(iii)` panel/proof core uses `v1->a, a->v4`, not solid `v2->a`. | Yes, corrected 14-arc core only. |
| `(ii)^* x (iii)` | erroneous `v2->a` in `(iii)` | `m=15`, SAT, `2e2329098dcee9fb` | UNSAT | `m=14`, ILP=UNSAT, SAT=UNSAT, brute=UNSAT, `44d9c8615673ee23` | High. Page-33 proof uses `v1->a, a->v4` and its degree forcing fails with the extra in-arc. | Yes, corrected 14-arc core only. |
| `(iii)^* x (iii)` | erroneous `v2->a` in `(iii)` and erroneous `b->v3` in `(iii)^*` | `m=16`, SAT, `6559d26f2f42acf2` | UNSAT | `m=14`, ILP=UNSAT, SAT=UNSAT, brute=UNSAT, `a29504a9ad838340` | Very high. The proof explicitly treats the two `a`-paths and two `b`-paths; the old extras are exactly the extra escape arcs. | Yes, corrected 14-arc core only. |
| `(iii)^* x (iv)` | erroneous `b->v3` in `(iii)^*` | `m=15`, SAT, `2e65f165dfbd8d63` | UNSAT | `m=14`, ILP=UNSAT, SAT=UNSAT, brute=UNSAT, `c2e80a596786422b` | High. The drawn `(iii)^*` core and proof use `b->v4, v1->b`, not solid `b->v3`. | Yes, corrected 14-arc core only. |
| `(iii)^* x (v)` | erroneous `v2->a` in `(v)` and erroneous `b->v3` in `(iii)^*` | `m=16`, SAT, `0c4d48ddebf877f7` | UNSAT | `m=14`, ILP=UNSAT, SAT=UNSAT, brute=UNSAT, `0544a0fa8afaeeb2` | High. The proof's contradiction uses the 14-arc core; the old extras give a real SAD. | Yes, corrected 14-arc core only. |

## Full B.3 table after correction

Every row below uses:

```text
base = v1->v2, v2->v3, v3->v4, v4->v1, v1->v3, v2->v4
common = v4->a, a->v2, v3->b, b->v1
```

The table lists only arcs incident with `a` or `b`, including the common arcs,
because the base is fixed.

| Case | Arcs incident with `a` or `b` | m | lambda_arc | ILP | SAT | Hash16 | Paper | Benchmark status |
|---|---|---:|---:|---|---|---|---|---|
| `(i)^* x (i)` | `v4->a, a->v2, v3->b, b->v1, v2->a, a->v4, b->v3, v1->b` | 14 | 2 | UNSAT | UNSAT | `92edbcb1560d099f` | UNSAT | Safe UNSAT |
| `(i)^* x (ii)` | `v4->a, a->v2, v3->b, b->v1, v2->a, a->v1, b->v3, v1->b` | 14 | 2 | UNSAT | UNSAT | `dc835befa7a474f0` | UNSAT | Safe UNSAT |
| `(i)^* x (iii)` | `v4->a, a->v2, v3->b, b->v1, v1->a, a->v4, b->v3, v1->b` | 14 | 2 | UNSAT | UNSAT | `a1f7f5c0affb7c24` | UNSAT | Safe UNSAT |
| `(i)^* x (iv)` | `v4->a, a->v2, v3->b, b->v1, v2->a, a->v3, b->v3, v1->b` | 14 | 2 | UNSAT | UNSAT | `e6e7a2494bfa5cd4` | UNSAT | Safe UNSAT |
| `(i)^* x (v)` | `v4->a, a->v2, v3->b, b->v1, v3->a, a->v4, b->v3, v1->b` | 14 | 2 | SAT | SAT | `68b112ef0703c2fe` | SAT | Safe SAT control |
| `(ii)^* x (ii)` | `v4->a, a->v2, v3->b, b->v1, v2->a, a->v1, b->v3, v4->b` | 14 | 2 | UNSAT | UNSAT | `10fae725561067fd` | UNSAT | Safe UNSAT |
| `(ii)^* x (iii)` | `v4->a, a->v2, v3->b, b->v1, v1->a, a->v4, b->v3, v4->b` | 14 | 2 | UNSAT | UNSAT | `44d9c8615673ee23` | UNSAT | Safe UNSAT |
| `(ii)^* x (iv)` | `v4->a, a->v2, v3->b, b->v1, v2->a, a->v3, b->v3, v4->b` | 14 | 2 | UNSAT | UNSAT | `0cab4a53e5e81027` | UNSAT | Safe UNSAT |
| `(ii)^* x (v)` | `v4->a, a->v2, v3->b, b->v1, v3->a, a->v4, b->v3, v4->b` | 14 | 2 | SAT | SAT | `4c8ebeaf2a0fe224` | SAT | Safe SAT control |
| `(iii)^* x (iii)` | `v4->a, a->v2, v3->b, b->v1, v1->a, a->v4, b->v4, v1->b` | 14 | 2 | UNSAT | UNSAT | `a29504a9ad838340` | UNSAT | Safe UNSAT |
| `(iii)^* x (iv)` | `v4->a, a->v2, v3->b, b->v1, v2->a, a->v3, b->v4, v1->b` | 14 | 2 | UNSAT | UNSAT | `c2e80a596786422b` | UNSAT | Safe UNSAT |
| `(iii)^* x (v)` | `v4->a, a->v2, v3->b, b->v1, v3->a, a->v4, b->v4, v1->b` | 14 | 2 | UNSAT | UNSAT | `0544a0fa8afaeeb2` | UNSAT | Safe UNSAT |
| `(iv)^* x (iv)` | `v4->a, a->v2, v3->b, b->v1, v2->a, a->v3, b->v3, v2->b` | 14 | 2 | UNSAT | UNSAT | `2970657e95d7b8ad` | UNSAT | Already benchmarked |
| `(iv)^* x (v)` | `v4->a, a->v2, v3->b, b->v1, v3->a, a->v4, b->v3, v2->b` | 14 | 2 | SAT | SAT | `8a91be116d9d6dce` | SAT | Safe SAT control |
| `(v)^* x (v)` | `v4->a, a->v2, v3->b, b->v1, v3->a, a->v4, b->v2, v1->b` | 14 | 2 | SAT | SAT | `35c413943cd8eba4` | SAT | Safe SAT control |

## Why the old transcription failed

Appendix A.9.4 encoded `(iii)` and `(v)` by assuming a full 2-cycle on
`{a, v2}` in every configuration.  That assumption is correct for `(i)`, `(ii)`,
and `(iv)`, where `v2->a` supplies a needed second in-arc to `a`.  It is not
correct for `(iii)` or `(v)`, because:

- `(iii)` already has in-arcs `v4->a` and `v1->a`, and out-arcs `a->v2` and
  `a->v4`.
- `(v)` already has in-arcs `v4->a` and `v3->a`, and out-arcs `a->v2` and
  `a->v4`.

Thus `v2->a` is not forced by 2-arc-strongness in `(iii)` or `(v)`.  The figures
do not justify promoting it as a solid core arc, and the proofs on pages 32--34
use degree/path arguments consistent with its absence.  Its star image is
`b->v3`, so the same mistake contaminates starred `(iii)^*` and `(v)^*`.

Computationally, the old extra arcs are not harmless.  The old five mismatch
graphs are genuinely SAT.  I verified this by ILP, SAT, and a direct brute-force
enumeration.  Therefore the verifier was not merely failing on paper-UNSAT
instances; it was correctly finding decompositions of over-augmented graphs.

## Benchmark recommendations

1. The current `AiEtAl_iv_star_iv` benchmark remains correct.
2. The five old mismatch hashes must not be added as UNSAT benchmarks:
   `e3acdbe730421415`, `2e2329098dcee9fb`, `6559d26f2f42acf2`,
   `2e65f165dfbd8d63`, `0c4d48ddebf877f7`.
3. The corrected 14-arc hashes for those five cases are safe UNSAT benchmark
   candidates:
   `a1f7f5c0affb7c24`, `44d9c8615673ee23`, `a29504a9ad838340`,
   `c2e80a596786422b`, `0544a0fa8afaeeb2`.
4. Do not encode any dashed/provisional variant unless its arc set is separately
   documented.  The solid-core catalogue above is sufficient to match the
   paper's 11 UNSAT / 4 SAT Appendix B.3 split.

This audit supersedes the "likely missing/dashed arcs" interpretation in
Appendix A.9.4.  The local resolution is sharper: the problematic arcs were
extra, not missing.
