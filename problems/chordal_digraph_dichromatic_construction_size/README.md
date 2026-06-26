# chordal_digraph_dichromatic_construction_size

Substrate for the open size-reduction question in **arXiv:2202.01006**
(Aboulker, Bousquet, de Verclos, *Chordal directed graphs are not directed
chi-bounded*, Section 3 "Further works").

## The question
The paper proves the class `C_3` is **not** directed chi-bounded by building,
for every `k`, a `(k+1)`-dichromatic digraph in `C_3` of order `n^(2^poly(n))`
(doubly exponential), and asks whether **the size of that example can be
reduced**.

`C_3` = oriented digraphs (no digon) with **no transitive triangle `TT3`** and
**no induced directed cycle of length `>= 4`**. It allows the directed triangle
`C3` (the paper's `G_2`).

## The oracle handle
```
m(k) = minimum order of a C_3 digraph with dichromatic number >= k.
```
The construction is a doubly-exponential **upper bound** on `m(k)`; any small
`C_3` witness with `chi_vec >= k` beats it. Both ingredients are EXACT on small
instances:
- **C_3 membership** -- pure combinatorial test (`core.is_C3`): no digon, no
  `TT3` (ordered-triple scan), no induced dicycle `>= 4`
  (`nx.simple_cycles` + inducedness check).
- **dichromatic number** -- SAT + lazy cycle elimination, reused verbatim from
  `engine/lib/digraph_core.py`.

## Layout
```
scripts/core.py      C_3 membership + exact chi_vec/acyclic_number (shared lib)
scripts/oracle.py    check_construction / extremal_small_n / m_of_k + CLI
tests/test_oracle.py 9 regression tests (membership + landmarks)
ledger.json          engine state (central_question, benchmark, proved, crux...)
docs/STATUS.md        one-screen status
.venv -> engine/.venv (shared)
```

## Quick start
```bash
.venv/bin/python scripts/oracle.py mk 2              # -> m(2) = 3 (directed triangle)
.venv/bin/python scripts/oracle.py extremal 7 --ub 3 # -> max_chi_in_C3 = 2 (=> m(3) >= 8)
.venv/bin/python -m pytest tests/ -q                 # 9 passed
```

## Verified landmarks (run, not asserted)
- `m(1) = 1`, `m(2) = 3` (directed triangle `= G_2`) -- EXACT.
- `m(3) >= 8` -- EXACT new lower bound: no `C_3` digraph on `<= 7` vertices has
  `chi_vec >= 3` (full `geng` x all-orientations scan).

See `docs/STATUS.md` and `ledger.json` for the open crux and live hypotheses.
