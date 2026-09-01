# chen_chvatal_lines_plus_bridges

Verified substrate for **Conjecture 2.2** of arXiv:1606.06011 (Beaudou, Kahn,
Rochet, *A new class of graphs that satisfies the Chen-Chvatal Conjecture*).

> There is a finite set `F_0` of connected graphs such that every connected
> graph `G ∉ F_0` either has a pendant edge or satisfies `ell(G)+br(G) ≥ |G|`.

`ell(G)` = #distinct metric-betweenness lines; `br(G)` = #bridges; pendant edge
⟺ a degree-1 vertex. A **bad** graph is connected, pendant-free, `ell+br<|G|`;
the conjecture says the bad set is finite (= `F_0`).

## Layout
```
scripts/core.py            BFS metric, lines, ell(G), bridges, pendant, is_bad   (exact)
scripts/constructions.py   named graphs: C4, K2,3, W4, wheels, K_n, C_n, K_{p,q}, Petersen
scripts/oracle.py          CLI: check / g6 / scan / landmarks
tests/test_oracle.py       14 regression tests (Lemma 3.1 anchors + scan picture)
data/scan_n{4..9}.json     full geng enumeration output (bad-graph census)
docs/STATUS.md             one-screen state
docs/H5_STATE_OF_PROOF.md  current H5 handback and four-front closure checklist
docs/H5_LEMMA_A_REDUCTION.md       non-2-connected reduction and remaining C2 gap
docs/H5_LEMMA_B_OBSTRUCTION.md     2-connected reduction, B1/B2, and dead routes
ledger.json                engine state (central_question, benchmark, proved, crux, hypotheses)
```

## Run
```
.venv/bin/python -m pytest tests/ -q                 # 14/14 pass
.venv/bin/python scripts/oracle.py landmarks         # Lemma 3.1: ell(C4)=1, ell(K2,3)=4=|K2,3|-1
.venv/bin/python scripts/oracle.py scan 8            # census of bad graphs on 8 vertices
```

The venv is the shared engine venv (`.venv` → `engine/.venv`), with networkx;
`geng` (nauty) must be on PATH for `scan`.

## Status

As a baseline, the oracle is **verified** against Lemma 3.1 (RUN). Full
enumeration n=4..9 finds exactly **12** pendant-free bad graphs (orders
4,5,6,8), matching `|F_0|=12`; none beyond F_0, none at n=7 or n=9.

H5 remains open. See `docs/STATUS.md` for the current D30 four-front handback,
and `docs/H5_STATE_OF_PROOF.md` plus the two lemma notes above for the detailed
reductions, finite evidence, and refuted routes.
