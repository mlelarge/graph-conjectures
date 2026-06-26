# Oriented triangle-free extremal numbers — `a⃗(n)` and `t⃗(n)`

Attack on the two open conjectures of **Aboulker, Havet, Pirot, Schabanel**,
*Minimum acyclic number and maximum dichromatic number of oriented triangle-free
graphs of a given order* (arXiv:2403.02298). This is the **pilot problem for the
autonomous research engine** (see the project methodology); `ledger.json` is the
engine's single source of truth.

## The problem

For an oriented graph `D` (digraph with no 2-cycle) whose underlying graph is
triangle-free:

- `α⃗(D)` = acyclic number = max order of an induced acyclic subdigraph;
- `χ⃗(D)` = dichromatic number = least `k` partitioning `V(D)` into `k` acyclic sets.

Over all oriented triangle-free graphs of order `n`:

- `a⃗(n) = min α⃗(D)`  — **Conjecture 3:** `a⃗(n) = Θ(√(n log n))`
- `t⃗(n) = max χ⃗(D)`  — **Conjecture 4:** `t⃗(n) = Θ(√(n/log n))`  (implied by Conj 3)

Proved bounds (the **benchmark**):

```
(1/√2 − ε)·√(n log n) ≤ a⃗(n) ≤ (107/8)·√n·log n
(8/107)·√n/log n      ≤ t⃗(n) ≤ (√2 + ε)·√(n/log n)
```

**Open crux:** a factor `√(log n)` gap on each — tighten `a⃗`'s upper bound
(conjecturally via an orientation of the triangle-free *process* graph), or
dually push `t⃗`'s lower bound up.

## The oracle (sound, exact)

`scripts/core.py` computes — exactly, via SAT/MaxSAT with lazy cycle
elimination — the acyclic number and dichromatic number of any explicit oriented
graph, plus triangle-free / oriented checks and `nauty geng -t` enumeration.
This is the ground truth every agent-proposed construction is checked against.

```bash
.venv/bin/python scripts/oracle.py check d25        # the 25-vertex 3-dicritical witness
.venv/bin/python scripts/oracle.py blowup 5 7       # C5←7 backward-blowup
.venv/bin/python scripts/oracle.py extremal 6       # exact a⃗(6), t⃗(6) by enumeration
```

`scripts/constructions.py` holds the explicit families: `D25` (= `C₅←5`, Prop 4.6),
the general `backward_blowup_directed_cycle(ℓ, m)`, Paley tournaments, transitive
tournaments, directed cycles, random orientations.

## Verified against the paper

`tests/test_oracle.py` (11 tests, ~2s) pins the oracle to known values:
`χ⃗(P₇)=3`, `χ⃗(P₁₁)=4`, **`χ⃗(D₂₅)=3` and D₂₅ 3-dicritical**, the `C₅←m` threshold
(m=5 is the smallest with `χ⃗=3`, reproducing Prop 4.6's improvement over Lemma
4.2's m=9), and small-`n` extremal values `t⃗(3)=1, t⃗(4)=2, a⃗(4)=3, a⃗(5)=a⃗(6)=4`.

## Layout

```
ledger.json            engine state: central_question, benchmark, proved, open_crux,
                       live_hypotheses, graveyard, decision_log, discipline_gates
scripts/core.py        exact α⃗, χ⃗, structure checks, geng enumeration
scripts/constructions.py  explicit oriented-graph families (incl. D25)
scripts/oracle.py      CLI + benchmark + check_construction + extremal_small_n
tests/test_oracle.py   regression suite (paper's known values)
Refs/2403.02298.pdf    the paper (+ .txt extraction)
docs/STATUS.md         human-readable status mirror of the ledger
```

## Setup

```bash
cd problems/oriented_triangle_free_extremal
uv venv --python 3.12 && uv pip install networkx pytest python-sat
.venv/bin/python -m pytest tests/ -q
```
Requires `nauty` (`geng` on PATH).
