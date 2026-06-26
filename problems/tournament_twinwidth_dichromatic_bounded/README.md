# tournament_twinwidth_dichromatic_bounded

Substrate for **Conjecture 3.12** of arXiv:2310.04265 (Aboulker, Aubian, Charbit,
Lopes, *Clique number of tournaments*): for every fixed `k`, tournaments of
twin-width `<= k` are `chiVec`-bounded — `chiVec(T) <= f(omegaVec(T))` for some
binding function `f`. Seeded lean: **disprove**.

See `docs/STATUS.md` for the one-screen state and `ledger.json` for the engine
contract.

## Layout
```
scripts/core.py            exact chiVec, omegaVec, tww  (sound, no heuristics)
scripts/constructions.py   Delta substitution into C3; families S_k, S~_m
scripts/oracle.py          check_construction + measure_S/measure_S_tilde + scan; CLI
tests/test_oracle.py       pins the oracle to the paper's known values
ledger.json                engine state (central_question, benchmark, crux, hypotheses)
docs/STATUS.md             one-screen status
Refs/                      paper PDF goes here (cite checks)
.venv -> engine/.venv      shared venv (networkx, python-sat, sympy, pytest)
```

## Invariants (all EXACT)
- `chiVec(T)` dichromatic number — SAT + lazy cycle elimination (re-uses
  `engine/lib/digraph_core`).
- `omegaVec(T)` = `min over orderings of omega(back-edge graph)` — iterative-deepening
  branch-and-bound over orderings, cross-checked against brute force for `n<=9`.
- `tww(T)` twin-width — exact contraction-sequence search on the **directed**
  arc-relation trigraph.

## Run
```bash
.venv/bin/python scripts/oracle.py S 4              # measure S_4 (chiVec, omegaVec, tww)
.venv/bin/python scripts/oracle.py S 5 --no-omega   # chiVec, tww only (omegaVec at n=31 is the open wall)
.venv/bin/python scripts/oracle.py Stilde 3         # measure S~_3
.venv/bin/python scripts/oracle.py scan 7 --chi-ge 3   # all tournaments on 7 vtx with chiVec>=3
.venv/bin/python -m pytest tests/ -q                # regression vs paper's known values
```

## Verified reproductions (RAN)
`chiVec(S_1..S_4)=1,2,3,4`; `omegaVec(S_1..S_4)=1,2,2,3`; `tww(S_2)=tww(S_3)=tww(C3)=1`,
`tww(TT_n)=0`; `omegaVec(S~_1..S~_3)=1,2,3`; smallest 3-dichromatic tournament has 7
vertices (gentourng scan).

## What is and isn't oracle-able
A **counterexample** (bounded tww + bounded omegaVec + growing chiVec) is a sound
disproof and directly detectable. The **asymptotic truth** of the conjecture is NOT
finitely certifiable — finite measurement is not a proof (see `discipline_gates`).
The open crux is the growth rate of `omegaVec(S_k)` for `k>=5`.
