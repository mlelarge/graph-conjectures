# lines_bridges_chen_chvatal

Substrate for the open question on counter-examples to the **lines + bridges**
inequality `ell(G) + br(G) ≥ |G|` (arXiv:1606.06011, Aboulker–Matamala–Rochet–Zamora,
"A new class of graphs that satisfies the Chen–Chvátal conjecture").

- `ell(G)` = number of distinct **metric lines** of a connected graph
  (a line through `a,b` is `{a,b} ∪ {x : x is metrically between, or makes a/b between}`).
- `br(G)` = number of **bridges**.
- A **counter-example** is a connected `G` with `ell(G)+br(G) < |G|` (the inequality fails).
  C4 is the smallest. The paper's open **Conjecture 2.2** says all counter-examples
  come from a finite list by replacing a bridge with a path.

## Layout
```
scripts/core.py    EXACT oracle: BFS distances, metric lines, ell, bridges, geng -c enumerator
scripts/oracle.py  check_construction / enumerate_counterexamples + CLI
tests/             6 regression tests pinning C4 and the n=4..7 census
data/              cached census JSON for n=4..7 (incl. witness edge lists)
docs/STATUS.md     one-screen status
ledger.json        engine state (central_question, benchmark, proved, open_crux, hypotheses, decision_log)
.venv -> shared engine venv (networkx)
```

## Run
```bash
.venv/bin/python -m pytest tests/ -q
.venv/bin/python scripts/oracle.py check c4
.venv/bin/python scripts/oracle.py enumerate 7
```

## Status
Phase 0 — exact oracle built and **verified** against the paper's small-graph
data (C4: `ell=1, br=0`; full connected-graph census n=4..7: `1/4/4/2`
counter-examples, bridgeless splits `1/4/3/0`). Engine-ready. See `docs/STATUS.md`.
