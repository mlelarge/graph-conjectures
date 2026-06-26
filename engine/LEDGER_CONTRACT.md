# The ledger contract — what a problem must provide to be attackable

The research engine (`.claude/workflows/research-attack.js`) is **problem-agnostic**.
To launch it on a new problem you provide exactly two things in the problem folder;
the engine needs no code changes.

## 1. `ledger.json` — the engine's state (single source of truth)

A JSON file with these keys (see `problems/oriented_triangle_free_extremal/ledger.json`
for a worked example):

| key | role |
|---|---|
| `central_question` | the one-paragraph statement of what we are trying to settle |
| `benchmark` | the fixed yardstick every proposal is scored against, **including `oracle_cmd` and `oracle_api`** (how to call the oracle) and any `ground_truth_landmarks` |
| `proved[]` | claims that survived independent verification (NOT empirical-only); each tagged with `claim_form` and stated **at the scope it was verified** (see auto-scoping below) |
| `open_crux` | the single load-bearing hole the engine drives at |
| `live_hypotheses[]` | candidate moves, each with a falsifiable prediction and a `claim_form` |
| `graveyard[]` | killed ideas + one-line reason (never re-proposed) |
| `decision_log[]` | append-only D-numbered history |
| `next_action`, `needs_human`, `budget_spent_tokens` | control |
| `discipline_gates` | the hard rules the engine enforces (empirical≠proof; audit≠red-team; citations verified; **universal_needs_generic_census**) |

### Claim form & the universal-claim gate

Every claim is tagged by **logical form** — `existential` / `universal` / `asymptotic` / `structural` —
because the verification bar differs:

- **existential** ("a witness exists") → one oracle-verified construction settles it;
- **asymptotic / family** ("infinitely many …") → needs a *symbolic* proof; finite-`n` survival is not a
  theorem (`empirical_not_proof`);
- **universal** ("for **all** `X` in class `C`, `P(X)`") → **`universal_needs_generic_census`**: it can never
  be supported by examples from a *structured* sub-family (circulants, the construction the conjecture came
  from) — those are exactly where special identities hold, the worst possible sample. It must survive an
  **exhaustive census over generic** small members of the full class (e.g. `gentourng` / all-objects),
  aimed at the *generic* part. One counterexample kills it; structured confirmations prove nothing.

**Auto-scoping.** The synthesis step records each claim at the scope its verification actually covered. A
claim supported only by one structured family is recorded *at family scope* ("holds for circulant factors"),
never as universal; scope is widened to universal only when an exhaustive generic census passes. (This is the
fix for the `H16` failure: `ω̄(S[H])=ω̄(S)+ω̄(H)−1` was verified on circulant factors only and wrongly
recorded as universal — it is false in general, true at circulant scope.)

**Quantifier-trap check** (the skeptic enforces it): an argument must not give an *induced* sub-object its
*optimal / minimum-over-orders* invariant when it actually inherits an *arbitrary* induced one (canonical
warning: a transitive triple has tournament-clique-number 1, yet its reverse order has a 3-clique).

## 2. An oracle — sound, exact, computational ground truth

A script the agents can call (declared in `benchmark.oracle_cmd` / `oracle_api`)
that, given an explicit finite object, returns the **exact** invariants the
conjecture is about. It must be *sound* (every reported value is correct, no
heuristics) — this is the engine's anti-hallucination spine: a proposal that
contradicts the oracle is killed instantly and cheaply.

Convention: a Python venv at `<problem_dir>/.venv` and `<problem_dir>/scripts/oracle.py`
with a `check_construction`-style entry point and a CLI. The engine invokes it as
`<problem_dir>/.venv/bin/python <problem_dir>/scripts/oracle.py ...`.

## Launching

```
# by name (workflow registered in .claude/workflows/)
Workflow({ name: 'research-attack',
           args: { problem_dir: '/abs/path/to/problems/<p>', rounds: 4, proposers: 4 } })
```

`args`: `problem_dir` (required, absolute), `rounds` (default 1), `proposers`
(default 3, cycles the 4 generic lenses), `dry_limit` (default 2 — stop after
this many rounds with no ledger movement).

## What one round does

`propose` (N diverse-lens proposers, read-only) → `pipeline(ground → skeptic →
verify)` per proposal → `synthesize` (one lead rewrites `ledger.json`: promote /
graveyard / update crux / append decision / set `needs_human`). The engine stops
early when a round sets `needs_human` or after `dry_limit` dry rounds — that is
the "launch-and-report" boundary where it hands back to you.
