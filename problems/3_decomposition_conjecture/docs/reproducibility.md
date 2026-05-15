# Reproducibility checkpoint for the n=14 milestone

This document records the commit, exact commands, and SHA-256 hashes for
the load-bearing artefacts at the n=14 milestone. To reproduce all
results from scratch, run the commands below in order against commit
`9b8d0ef`.

## Repository state

- Commit: `9b8d0ef` (3-decomposition: trace replacement framework + n=14 sweep results)
- Python: 3.12 with `networkx`, `pytest` (use `uv` per the project policy).
- External tool: nauty `geng` on `PATH`.

## Artefact hashes (SHA-256)

| Path | Hash |
|---|---|
| `data/gadget_lattice_2pole_n10_both.json` | computed by `shasum -a 256` at build time |
| `data/gadget_lattice_2pole_n12_both.json` | `036eb628789f0883eda5e2606594973ed79b57fea0ec6da493833b81dd4abd73` |
| `data/n14_full.jsonl` | `2c34c7ffe48604f32a816991eb6850167d3a7c41bd9d2bdd2e50da8c703ef837` |
| `data/n14_full.summary.json` | `237795adb40c31444c9c4fbb40b278d94d1004d2ee6a165790bc361426c79a78` |

Verify locally:

```bash
shasum -a 256 \
  problems/3_decomposition_conjecture/data/gadget_lattice_2pole_n12_both.json \
  problems/3_decomposition_conjecture/data/n14_full.summary.json \
  problems/3_decomposition_conjecture/data/n14_full.jsonl
```

## Build commands (in order)

### 1. n≤10 gadget lattice

```bash
.venv/bin/python problems/3_decomposition_conjecture/scripts/gadget_lattice.py \
  --n-max 10 \
  --orientations both \
  --output problems/3_decomposition_conjecture/data/gadget_lattice_2pole_n10_both.json
```

(~minutes.)

### 2. n=12 replacement sweep against n≤10 lattice (Universal Replacement test)

```bash
.venv/bin/python problems/3_decomposition_conjecture/scripts/replacement_sweep.py \
  --n 12 \
  --lattice problems/3_decomposition_conjecture/data/gadget_lattice_2pole_n10_both.json \
  --output problems/3_decomposition_conjecture/data/replacement_sweep_n12.json
```

This produces the 5 failure trace sets that motivate compatibility
replacement.

### 3. Compatibility universality classification

```bash
.venv/bin/python problems/3_decomposition_conjecture/scripts/compatibility_universality.py \
  --lattice problems/3_decomposition_conjecture/data/gadget_lattice_2pole_n10_both.json \
  --output problems/3_decomposition_conjecture/data/compatibility_universality_n10_lattice.json
```

### 4. Trace feasibility (16/34 realisable theorem)

```bash
.venv/bin/python problems/3_decomposition_conjecture/scripts/trace_feasibility.py \
  --lattice problems/3_decomposition_conjecture/data/gadget_lattice_2pole_n10_both.json \
  --output problems/3_decomposition_conjecture/data/trace_feasibility.json
```

### 5. Class III absorber witnesses

```bash
.venv/bin/python problems/3_decomposition_conjecture/scripts/classIII_absorber_check.py \
  --lattice problems/3_decomposition_conjecture/data/gadget_lattice_2pole_n10_both.json \
  --output problems/3_decomposition_conjecture/data/classIII_absorber_witnesses.json
```

### 6. n=12 failure structural classification

The artefact `data/failure_structural_classification_n12.json` was
produced by ad-hoc inspection of the 5 n=12 failure trace sets (no
single script). It records bridge/articulation/non-port-trivial 2-cut
class for each.

### 7. Extended n≤12 gadget lattice (resumable)

```bash
.venv/bin/python problems/3_decomposition_conjecture/scripts/gadget_lattice.py \
  --n-max 12 \
  --orientations both \
  --checkpoint problems/3_decomposition_conjecture/data/gadget_lattice_2pole_n12_both.jsonl \
  --output problems/3_decomposition_conjecture/data/gadget_lattice_2pole_n12_both.json \
  --progress-every 25
```

This is the long-running build (~hours on a 16-core macOS host). The
intermediate `.jsonl` checkpoint is excluded from the commit (see
`.gitignore`).

### 8. Full n=14 sweep against n≤12 lattice (sharded, 8 workers)

```bash
for i in 0 1 2 3 4 5 6 7; do
  .venv/bin/python problems/3_decomposition_conjecture/scripts/full_replacement_sweep.py \
    --n 14 \
    --filter all \
    --checkpoint problems/3_decomposition_conjecture/data/n14_all.shard${i}.jsonl \
    --read-checkpoint problems/3_decomposition_conjecture/data/n14_full.jsonl \
    --summary-output /dev/null \
    --shard-mod 8 --shard-index ${i} \
    --progress-every 50 \
    2> problems/3_decomposition_conjecture/data/n14_all.shard${i}.log &
done
wait
```

(Each shard exits cleanly; the orientation-pair fast-path + C0
early-termination + 8-way parallel made this run in ~1.5 days on a
16-core MacBook.)

Originally the essentially-3-connected stratum was swept first (single
worker pre-fast-path) and produced the initial 1790 oriented records;
the all-class sweep above resumes from those (via `--read-checkpoint`).

### 9. Merge shards into the unified n=14 archive

```bash
.venv/bin/python problems/3_decomposition_conjecture/scripts/merge_shards.py \
  --main problems/3_decomposition_conjecture/data/n14_full.jsonl \
  --shards problems/3_decomposition_conjecture/data/n14_all.shard*.jsonl \
  --summary-output problems/3_decomposition_conjecture/data/n14_full.summary.json \
  --lattice problems/3_decomposition_conjecture/data/gadget_lattice_2pole_n12_both.json
```

Final `data/n14_full.jsonl` contains exactly 15178 records; verify with
the `verify_n14_summary.py` script.

## Verification

```bash
.venv/bin/python problems/3_decomposition_conjecture/scripts/verify_n14_summary.py
```

Expected output:
- Total: 15178 records.
- Status: `{trace_contained: 15176, compat_universal_not_contained: 2, neither: 0}`.
- Structural: `{bridge: 1370, essentially_3conn: 7120, non_port_2cut: 6688}`.
- 10 distinct absorbing classes.
- 2 compat-only records, both the same bridge graph `M??CB?W`cKKGF?WG?`.
