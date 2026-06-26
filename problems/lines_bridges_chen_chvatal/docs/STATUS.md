# STATUS — lines + bridges (Chen–Chvátal), arXiv:1606.06011

**Phase:** 0 (substrate built, oracle verified, engine-ready).

## The question
Connected graph `G`. Define
- `ell(G)` = number of **distinct metric lines**, where `line(a,b) = {a,b} ∪ {x : [abx] or [axb] or [xab]}` and `[pqr] := d(p,q)+d(q,r)=d(p,r)` (BFS distances);
- `br(G)` = number of **bridges** (cut-edges).

Inequality under test: **`ell(G) + br(G) ≥ |G|`**. A *counter-example* is `ell+br < n`.
It is FALSE in general (C4 is the smallest CE). The paper's open **Conjecture 2.2**:
every counter-example arises from a **finite** set by replacing a bridge with a path.

## Oracle (EXACT, no heuristics, no SAT)
`scripts/core.py` — BFS all-pairs distances → metric-betweenness lines → distinct-line count `ell`; `nx.bridges` → `br`; `geng -c` connected-graph enumerator.
`scripts/oracle.py` — `check_construction`, `enumerate_counterexamples`, CLI (`check`, `enumerate`, `edges`).

```
.venv/bin/python scripts/oracle.py check c4
.venv/bin/python scripts/oracle.py enumerate 7
.venv/bin/python scripts/oracle.py edges 4 0-1,1-2,2-3,3-0
```

## Verified ground truth (RAN, not asserted)
| n | connected graphs | counter-examples | bridgeless | with bridge |
|---|---|---|---|---|
| 4 | 6   | 1 (C4) | 1 | 0 |
| 5 | 21  | 4 | 4 | 0 |
| 6 | 112 | 4 | 3 | 1 |
| 7 | 853 | 2 | 0 | 2 |

`C4`: `ell=1` (one universal line `{0,1,2,3}`), `br=0`, `ell+br=1<4` — reproduced exactly.
6/6 regression tests pass in ~0.2s. Census cached in `data/census_n{4,5,6,7}.json`.

## Open crux
Conjecture 2.2 finiteness. Oracle-able stress test: extend the census, classify
each bridge-containing counter-example, and check whether a **new irreducible
minimal bridge counter-example** appears (would REFUTE 2.2) or all reduce by
bridge→path contraction to the three known Figure-2 graphs (empirical support only).

## Live hypotheses
- **H1** bridge-family finiteness (Conj 2.2) — needs bridge→path contraction check + census to n=8,9.
- **H2** bridgeless counter-examples are structured/finite (count 1→4→3→0 over n=4..7).

## Discipline
A finite-n census *confirming* 2.2 is verification, not proof — only a refutation
(a new irreducible bridge CE) is a promotable finite certificate.
