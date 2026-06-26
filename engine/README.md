# Research engine

A generic, autonomous, multi-agent research engine for attacking open math
conjectures **without babysitting**. It encodes the research loop a strong
mathematician runs in a long chain of thought (propose an idea, ground it,
ruthlessly kill it against a fixed benchmark, keep the thread, pivot when dry) as
a deterministic agent workflow — so the *mathematical* direction and the
*operational* monitoring both move off the human.

- **Engine:** `.claude/workflows/research-attack.js` (launch by name `research-attack`).
  This file ships in the repo — it is tracked despite the blanket `.claude/`
  gitignore (via an explicit un-ignore in `.gitignore`). Claude Code registers
  workflows from the project's `.claude/workflows/`, so a fresh clone can launch
  it directly; to launch from any directory, also copy it to `~/.claude/workflows/`.
- **Contract:** `engine/LEDGER_CONTRACT.md` — the two things a problem must provide
  (`ledger.json` + a sound oracle). Nothing else is problem-specific.
- **Pilot:** `problems/oriented_triangle_free_extremal/` (Aboulker–Havet–Pirot–Schabanel,
  arXiv:2403.02298).

## The round

```
startup gate ─▶  refuse to re-launch a ledger already handed back, nothing queued
   │             (clears if a concrete next_action is queued, or no hand-back stands)
   ▼   each round, until a stop condition:
execute + propose ─▶ ground ─▶ skeptic ─▶ verify ─▶ synthesize ─▶ decide
(run queued          (oracle,  (refute,   (independent (rewrite     (continue /
 next_action;         kill      default    re-derive,   ledger.json)  pivot /
 N diverse lenses)    fast)     kill)      gate empirical)            hand back)
```

A **startup gate** runs first: it refuses to launch on a ledger that already
records a standing hand-back (`needs_human`, or a `recommend_handback` in its
latest `decision_log`) with no concrete `next_action` queued — so a relaunch
never burns a round just to re-derive the same hand-back. The **ledger is
authoritative**; a stale `docs/STATUS.md` may flag exhaustion but never blocks.

Inside a round, a first-class **executor** runs whatever concrete experiment the
last round queued (`next_action`), while N proposers cycle four generic lenses
(explicit-construction, asymptotic-argument, literature-reduction, dual-attack).
The **graveyard** stops re-proposing killed ideas; the **discipline gates**
(empirical≠proof, audit≠red-team, citations-verified, universal-needs-generic-
census) are enforced by the synthesis step. The engine hands back when synthesis
sets `needs_human`/`recommend_handback`, after `dry_limit` rounds with no ledger
change, or after `drought_limit` rounds with no new frontier result.

## Launch

```
Workflow({ name: 'research-attack',
           args: { problem_dir: '<abs path to problems/X>', rounds: 4, proposers: 4 } })
```

State lives entirely in `<problem_dir>/ledger.json`, rewritten each round — so a
run is resumable and a human can inspect or correct the ledger between launches.
`args`: `problem_dir` (required, absolute), `rounds` (default **1** — pass e.g.
`rounds: 4` to make real progress), `proposers` (default 3), `dry_limit`
(default 2), `drought_limit` (default 3).

**Relaunching continues the thread; it does not restart.** The ledger's `proved`
/ `graveyard` / `open_crux` / `next_action` are loaded and built on; the executor
runs the queued `next_action` first; proposers steer clear of the graveyard. The
patience counters (`dry`, `drought`) reset each launch. If the ledger already
stands handed-back with nothing queued, the startup gate stops the run at **0
rounds** — queue a concrete `next_action` (or clear `needs_human`) in the ledger
to direct another push. The override is deliberately ledger-level (not a CLI
flag), so the ledger history records *why* each re-run was warranted.

## Adding a new problem

1. Create `problems/<new>/` with a venv + a sound `scripts/oracle.py`.
2. Seed `problems/<new>/ledger.json` per the contract (central_question,
   benchmark incl. oracle_cmd, proved, open_crux, discipline_gates).
3. Launch the engine at it. No engine changes.

For bulk preparation, `engine/substrate-factory.js` triages a candidate list,
builds each oracle, then **independently re-runs** every oracle + test suite
before marking a problem engine-ready (readiness is computed from those measured
results, not from a build agent's self-report), and emits `engine/manifest.json`
(engine-ready vs parked).
