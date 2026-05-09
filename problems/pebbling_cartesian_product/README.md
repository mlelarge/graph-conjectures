# Pebbling product (Graham's conjecture, Lemke / FPY graph)

Self-contained project slice studying upper bounds on the pebbling number of
the Cartesian product `L_fpy □ L_fpy` (the Lemke-style graph used by
Flocco–Pulaj–Yerger 2024).

The terminal local result is `π(L_fpy □ L_fpy) ≤ 246`, with a rooted
improvement `π(·, (v_1, v_1)) ≤ 106` (sharpening Hurlbert 2017's 108). The
project does **not** match FPY's published `≤ 96` — see [docs/terminal_report.md](docs/terminal_report.md)
for the full status, including why the FPY ingestion bridge is blocked on the
public CSVs.

## Layout

```
docs/                 status reports and notes (terminal_report.md is the entry point)
data/                 graphs/, certificates/, root_orbit_bounds.csv, ...
scripts/              all *.py for column generation, pricing, certificate checking
tests/                pytest suite (uses local conftest.py for sys.path)
external/             FPY source clone (gitignored; clone it manually — see below)
```

## Reproducing

Tests:

```bash
.venv/bin/pytest problems/pebbling_cartesian_product/tests/ -q
```

(The `tests/conftest.py` puts `problems/pebbling_cartesian_product/scripts/`
on `sys.path`, so no `PYTHONPATH` is needed when invoking pytest.)

A single rooted check, e.g. for the path-augmented v1v1 ≤ 106 certificate:

```bash
.venv/bin/python problems/pebbling_cartesian_product/scripts/check_pebbling_weight_certificate.py \
  problems/pebbling_cartesian_product/data/pebbling_product/certificates/Hurlbert_path_augmented_v1v1_le106.json
```

Aggregate the per-orbit bounds CSV:

```bash
.venv/bin/python problems/pebbling_cartesian_product/scripts/aggregate_orbit_bounds.py
```

## FPY clone (optional, for `fpy_probe.py`)

The `external/Graph_Pebbling/` directory is gitignored. To re-enable
[scripts/fpy_probe.py](scripts/fpy_probe.py):

```bash
git clone https://github.com/dominicflocco/Graph_Pebbling \
  problems/pebbling_cartesian_product/external/Graph_Pebbling
```

## Documents

- [docs/terminal_report.md](docs/terminal_report.md) — final status, headline numbers, what is and isn't proved
- [docs/plan.md](docs/plan.md) — original counterexample-search plan
- [docs/literature_notes.md](docs/literature_notes.md) — notes on Hurlbert / FPY / Graham
- [docs/phase2b_status.md](docs/phase2b_status.md) — FPY ingestion bridge status
- [docs/lp_improvement_log.md](docs/lp_improvement_log.md) — chronological LP-improvement log
