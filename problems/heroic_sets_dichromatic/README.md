# heroic_sets_dichromatic

Substrate for **arXiv:2009.13319 Problem 1.2** (Aboulker, Charbit, Naserasr,
*Extension of the Gyarfas–Sumner conjecture to digraphs*).

**Question.** Which finite sets `F` of digraphs are *heroic* — i.e. make
`Forb_ind(F)` (no member of `F` as an induced subdigraph) have **bounded
dichromatic number** `chi_d`? `chi_d(D)` = fewest colors so every color class
induces an acyclic subdigraph.

## Layout
```
scripts/core.py     wraps engine/lib/digraph_core.py (chi_d via SAT+lazy-cycle,
                    is_oriented/is_triangle_free, geng enum, all_orientations)
                    + named small digraphs, EXACT induced-subdigraph containment,
                    C_k substitution, the tournament tower.
scripts/oracle.py   check / measure / thm65 / tower / cyclesub  (+ CLI)
tests/test_oracle.py  7 regression tests reproducing the paper's landmarks
ledger.json         engine state (central_question, benchmark, proved, crux, ...)
docs/STATUS.md      one-screen status
Refs/               primary PDF (heroic_2009.13319.pdf)
.venv -> ../../engine/.venv   shared venv (networkx, python-sat, sympy, pytest)
```

## Run it
```bash
P=.venv/bin/python

# reproduce Theorem 6.5: chi_d(Forb_ind(K2sym,C3,P+3)) = 2
$P scripts/oracle.py thm65 6 -v

# red-team an arbitrary forbidden set over oriented triangle-free digraphs
$P scripts/oracle.py measure 6 --forbidden K2sym C3 P+3 --claimed-bound 2

# ground one explicit digraph (JSON arcs)
$P scripts/oracle.py check 4 '[[2,0],[1,2],[0,3],[3,1]]' --forbidden K2sym C3 P+3

# unbounded-dichromatic tournament tower: chi_d(D_k)=k
$P scripts/oracle.py tower 4

# Thm 2.1: chi_d(C_k(D)) = chi_d(D)+1
$P scripts/oracle.py cyclesub 3 C3

# tests
$P -m pytest tests/ -q
```

## Discipline gate
"Heroic"/"bounded" is **asymptotic**: finite enumeration **disproves** a claimed
heroic set or settles a **finite-target** subclaim exactly — it does **not**
prove boundedness. See `docs/STATUS.md` and `ledger.json:discipline_gates`.
