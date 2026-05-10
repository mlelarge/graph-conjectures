# `--earthmoon_candidate2` smoke runs

Provenance-rich, time-boxed runs of SMS's `--earthmoon_candidate2`
(weighted clique blowup $C_7[K_4]$ on 28 vertices, our Phase 4 headline
target). These runs are not expected to terminate within the allotted
budget; they exist to (a) prove the pipeline reaches the solver and
(b) bank reproducible null evidence with full metadata.

## Layout

Each run produces a paired `(meta.txt, log)` keyed by ISO-8601 UTC
timestamp:

- `run_YYYYMMDDTHHMMSSZ.meta.txt` — host, date, SMS commit and describe,
  any local patches in effect, full command, wall budget.
- `run_YYYYMMDDTHHMMSSZ.log` — solver stdout + stderr.

## Patches applied

The runs rely on **Patch A** from
[`../../docs/spike_sms_build.md`](../../docs/spike_sms_build.md):
a two-line fix to `encodings/planarity.py` in the vendored SMS clone that
restores the `solveArgs(args, forwarding_args)` arity. This patch is
v1.0.0-internal — the release shipped with `solveArgs(args)` while
`pysms` already required the two-arg form. It is why the `sms_describe`
field reads `v1.0.0-dirty` rather than `v1.0.0`.

The patch lives only in the gitignored clone tree
([`external/sat-modulo-symmetries/encodings/planarity.py`](../../external/sat-modulo-symmetries/encodings/planarity.py)).
Re-apply on every fresh clone.

## Runs

### `run_20260510T073917Z` — 600 s, no decision

First time-boxed candidate2 run, on the v1.0.0 pin. The encoding
generated cleanly (28 vertices, 602 initial clauses, 756 variables) and
CaDiCaL printed `Starting to solve`; no further output before
`gtimeout 600` fired. No SAT, no UNSAT, no decision/conflict
intermediate counters. Treat as evidence that the pipeline reaches the
solver but that 10 minutes is far too short for any signal — KSS report
~12 h on the smaller candidate1, so candidate2 needs hours-to-days of
budget to be interpretable.

## Next runs (planned)

1. `run_<ts>` for `--earthmoon_candidate1` (19 vertices) as a calibration
   reproduction against KSS's reported ~12 h UNSAT.
2. `run_<ts>` for `--earthmoon_candidate2` at a multi-hour budget, only
   after candidate1 calibrates the wall-clock regime.
