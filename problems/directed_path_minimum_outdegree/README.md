# Directed path minimum-outdegree conjecture

Self-contained project slice studying Cheng--Keevash Conjecture 1
(Thomasse's directed-path conjecture):

> Every oriented graph with minimum out-degree $\delta$ contains a directed
> simple path of length $2\delta$.

The local work combines hand arguments from Cheng--Keevash Lemma 7 with
computer-aided enumeration for the first $\delta = 4$ cases.

## Status

| Case | Status |
|---|---|
| $\delta = 1, 2$ | closed (trivial / Cheng--Keevash) |
| $\delta = 3$, all $n \geq 7$ | closed by hand |
| $\delta = 4, n = 9$ | closed (regular tournament) |
| $\delta = 4, n = 10$ | closed: hand cases plus audited/certified computer-aided case |
| $\delta = 4, n = 11$ | closed: two independent score-profile pipelines agree |
| $\delta = 4, n \geq 12$ | open |
| $\delta \geq 5$ | open |

The current strongest packaged theorem files are:

- [docs/k3_hand_proof.md](docs/k3_hand_proof.md)
- [docs/k4_n10_proof.md](docs/k4_n10_proof.md)
- [docs/k4_n11_proof.md](docs/k4_n11_proof.md)

## Layout

```
docs/                 proof files, plan, literature notes, appendices
data/                 k=4 audit output, path table, n=10 certificate, checkpoints
scripts/              miners, independent checkers, certificate verifier
```

## Reproducing

Run commands from the repository root.

`n = 10` closure:

```bash
uv run python problems/directed_path_minimum_outdegree/scripts/k4_local_miner.py
uv run python problems/directed_path_minimum_outdegree/scripts/k4_audit.py
uv run python problems/directed_path_minimum_outdegree/scripts/k4_independent_check.py
uv run python problems/directed_path_minimum_outdegree/scripts/k4_generate_certificate.py
uv run python problems/directed_path_minimum_outdegree/scripts/k4_verify_certificate.py
```

`n = 11` two-pipeline closure:

```bash
uv run python problems/directed_path_minimum_outdegree/scripts/k4_score_profile_miner.py 11
uv run python problems/directed_path_minimum_outdegree/scripts/k4_score_profile_independent_check.py 11
```

The score-profile miner writes `n >= 12` checkpoint files to
`data/k4_n<n>_checkpoint.tsv` inside this package.

## Documents

- [docs/plan.md](docs/plan.md) - project status, attack plan, and next work
- [docs/literature_notes.md](docs/literature_notes.md) - Cheng--Keevash notes and source audit
- [docs/k4_partial_appendix.md](docs/k4_partial_appendix.md) - per-case forcing derivations and rule soundness
- [docs/k4_n10_proof.md](docs/k4_n10_proof.md) - $\delta = 4, n = 10$ theorem package
- [docs/k4_n11_proof.md](docs/k4_n11_proof.md) - $\delta = 4, n = 11$ theorem package
