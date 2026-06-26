# heroic_sets_hero_forest

Substrate for **Conjecture 4.2** of Aboulker, Charbit & Naserasr, *Extension of
the Gyárfás–Sumner conjecture to digraphs* (arXiv:2009.13319).

> **Conjecture 4.2.** Let `H` be a *hero* and `F` an *oriented forest*. The set
> `{digon, H, F}` is **heroic** — i.e. `Forb_ind({digon, H, F})` has **bounded**
> dichromatic number `chi_d` — **iff** `F` is a disjoint union of oriented stars,
> **or** `H` is a transitive tournament.

The *only if* direction is proved in the paper. The open content is the *if*
direction; the smallest open instance is **Conjecture 6.2**
(`chi_d(Forb_ind(digon, →C3, S2+)) = 2`) and the smallest *proved* instance is
**Theorem 6.1** (`chi_d(Forb_ind(digon, →C3, →K2+K1)) = 2`).

## Why this is oracle-able (and how)
"Heroic"/"bounded" is asymptotic over an **infinite** class — not closeable by
enumeration. But the members are enumerable on small `n` (geng + all
orientations, filtered by induced-avoidance) and `chi_d` is **exactly** computable
(SAT + lazy directed-cycle elimination, `engine/lib/digraph_core.py`). So the
oracle is a **sound falsifier/measurer**: it reproduces proved finite landmarks,
measures `max chi_d` up to each `n`, and **disproves any claimed finite bound** by
exhibiting a member above it. It can **never** confirm boundedness (a discipline
gate).

## Layout
```
scripts/core.py     named forbidden digraphs (→K2+K1, S2+, S2-, ...), induced
                    containment, C_k substitution, hero/oriented-star classifiers
scripts/oracle.py   check_construction · measure_heroic_set · thm61 · conj62 ·
                    tower · cyclesub  (+ CLI)
tests/              9 regression tests (Thm 6.1, Conj 6.2, identities)
ledger.json         engine state (LEDGER_CONTRACT.md)
docs/STATUS.md      one-screen status
Refs/               primary source PDF
.venv -> shared engine venv
```

## Run
```bash
.venv/bin/python scripts/oracle.py thm61 6           # Theorem 6.1: chi_d = 2
.venv/bin/python scripts/oracle.py conj62 7          # Conjecture 6.2 sweep
.venv/bin/python scripts/oracle.py measure 7 \
    --forbidden K2_digon C3 S2+ --claimed-bound 2    # red-team a bound
.venv/bin/python scripts/oracle.py check 4 "[[0,1],[1,2],[2,3],[3,0]]" \
    --forbidden K2_digon C3 arrowK2_K1 S2+           # ground a digraph (directed C4)
.venv/bin/python -m pytest tests/ -q
```

## Verified landmarks
- **Theorem 6.1** (proved, exact): `max chi_d = 2` over `Forb_ind` members up to
  n=6, first attained at n=4 (witness = directed C4), distribution `{1:504,2:412}`.
- **Conjecture 6.2** (open): consistent with `chi_d = 2` through n=7
  (distribution `{1:426,2:96}`, no `chi_d≥3` member).
- Tower `chi_d(D_k)=k` (k=1..4); substitution `chi_d(C_k(D))=chi_d(D)+1`.

Forbidden-digraph defs and the `chi_d` engine are documented in
`scripts/core.py`; see `docs/STATUS.md` for the discipline gates and the
member-count caveat.
