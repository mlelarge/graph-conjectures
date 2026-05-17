# SAD Verifier — Strong Arc Decomposition

ILP + SAT verifier for the question *does digraph D admit a 2-coloring of its
arcs so that both color classes are strongly connected?* This is the decision
problem at the core of the Bang-Jensen–Yeo good-decomposition conjecture; see
`../attack_plan.md` v3 §"Computational backbone" and the design document
`../team/03_verifier_design.md` for the contract this code implements.

## Install (uv, macOS or Linux, Python 3.11+)

```sh
cd code
uv venv --python 3.11
uv sync
```

If `uv sync` is not available in your uv version, equivalent:

```sh
uv pip install -r <(uv pip compile pyproject.toml)
```

or just install the deps directly:

```sh
uv pip install 'networkx>=3.2' 'pulp>=2.7' 'python-sat>=0.1.8.dev16'
```

Optional accelerators:

```sh
uv pip install gurobipy            # if you have a Gurobi license
uv pip install ortools             # for the CP-SAT alternative
```

## Run

```sh
uv run python run_benchmarks.py
```

Expected output table on a clean install (sample timings; your numbers may
differ but the **status** columns must match):

```
name                 n    m  kappa  expect     ILP     SAT     tILP     tSAT  agree
--------------------------------------------------------------------------------------------
S4                   4    8      2   UNSAT   UNSAT   UNSAT    0.1s     0.0s  OK
C6_square            6   12      2   UNSAT   UNSAT   UNSAT    0.5s     0.1s  OK
C8_square            8   16      2   UNSAT   UNSAT   UNSAT    2.0s     0.5s  OK
QR7_tournament       7   21      3     SAT     SAT     SAT    0.3s     0.1s  OK
K5_bidirected        5   20      4     SAT     SAT     SAT    0.1s     0.0s  OK
C5_doubled           5   10      2     SAT     SAT     SAT    0.0s     0.0s  OK
--------------------------------------------------------------------------------------------
All 6 benchmarks passed in <total>s.
```

## What the verifier decides

Input: a finite digraph `D` (`networkx.MultiDiGraph`, parallel arcs allowed).
Output: `SAT` with a 2-partition `(A_R, A_B)` such that `(V, A_R)` and
`(V, A_B)` are both strongly connected; `UNSAT` with a refutation
certificate; or `UNKNOWN` on timeout.

## Two backends, must agree

`verifier_ilp.py` runs a feasibility ILP with cut-separation constraints
`1 <= sum_{e in delta^+(X)} x_e <= |delta^+(X)| - 1`. Cuts are added
**lazily**, never enumerated upfront. With Gurobi we use a `cbLazy` callback;
with CBC we run a cutting-plane outer loop that re-solves after each cut
batch.

`verifier_sat.py` runs a SAT encoding with **arborescence witnesses**: per
color and per direction we pick a rooted branching whose arcs must be of
that color. No transitive-closure encoding is used.

`cross_check.py` runs both on each instance and aborts on disagreement.

## Critical correctness rules

1. **Cuts are lazy** in both backends. Neither code enumerates `2^n - 2`
   subsets.
2. **Arborescence color compatibility is hard-clauses.** Any arc used in
   color `c`'s branching must be colored `c` (`verifier_sat.py:_build_cnf`).
3. **Every `SAT` answer is independently re-validated** by recomputing
   strong connectivity of `(V, A_R)` and `(V, A_B)` in Python via
   `networkx.is_strongly_connected`. A failed re-validation is a fatal bug
   and is returned as `UNKNOWN` with reason flagged.
4. **`UNSAT` is never declared without a proof artifact.** ILP returns the
   list of separating cuts that triggered infeasibility (with a best-effort
   deletion-filter minimization for the CBC backend); SAT relies on the
   solver-level proof and tags it as such.
5. **`UNKNOWN` is allowed on timeout.** It never silently becomes UNSAT.

## Layout

```
code/
  pyproject.toml      uv-managed deps; pins python>=3.11
  digraph.py          minimal MultiDiGraph wrapper (strong-conn, kappa', Eulerian, cut extraction)
  benchmarks.py       hand-encoded canonical instances with citations
  verifier_ilp.py     ILP cut-separation backend (Gurobi or PuLP/CBC)
  verifier_sat.py     SAT arborescence-witness backend (pysat / CaDiCaL)
  cross_check.py      both backends, asserts agreement
  run_benchmarks.py   full validation pass/fail table
```

## Fallbacks

If Gurobi is not installed, the ILP backend automatically falls back to
PuLP+CBC and uses a cutting-plane outer loop. This is slower but
mathematically equivalent and verified to give identical answers on the
small benchmark set.

If `python-sat` is not installed, install it with `uv pip install
python-sat`. We do not maintain a SAT fallback because the cross-check
contract requires two independent backends.

## Extending the benchmark set

Add entries to `benchmarks.py:all_benchmarks` with `name`, `n`, `arcs`,
`expected`, and a `source` citation. The auditor will cross-check the arc
set against the literature; the verifier itself will then confirm the
expected answer.

The benchmark stubs for the four Bang-Jensen–Gutin–Yeo 2020 exceptional
semicomplete-composition digraphs and the Ai–He–Li–Qin–Wang 2024 split
exceptions are **not** yet encoded. They depend on the math team supplying
arc lists; once provided they are drop-in additions to `benchmarks.py`.
