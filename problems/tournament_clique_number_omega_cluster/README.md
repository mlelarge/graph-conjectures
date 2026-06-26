# Clique number of tournaments — Question 5.9 (`omega_vec`-cluster)

Substrate for the autonomous research engine on **Question 5.9** of
*Aboulker, Aubian, Charbit, Thomassé et al.*, *Clique number of tournaments*
(arXiv:2310.04265). `ledger.json` records the engine through D45;
`docs/STATUS.md` contains the post-D45 corrections. In particular, H19 is
refuted by the iterated directed-triangle family; see
`docs/h19_refutation.md`.

## The invariant

For a **tournament** `T` (one arc per pair) and a total order `≺` of `V(T)`, the
**backedge graph** `T^≺` is the undirected graph with edge `uv` iff `u ≺ v` and
the arc `v→u` is *backward*. The **clique number of the tournament** is

```
omega_vec(T) = min over all total orders ≺ of  omega(T^≺)      (ordinary clique number)
```

`omega_vec(T) ≤ chi_vec(T)` always (the dichromatic number); `omega_vec` is the
tournament analogue of `omega` in χ-boundedness.

## The question

- **Question 5.9** (strong `f = id` form of Conj 5.8): is there `ℓ` with
  `omega_vec(T) ≥ k ⇒ ∃ subtournament A, |A| ≤ ℓ(k), omega_vec(A) ≥ k`?
- **Conjecture 5.10** is a sufficient route to a negative answer, not the
  literal logical negation: for every `k ≥ 3`, infinitely many
  `k`-`omega_vec`-critical tournaments (`omega_vec = k`, every deletion drops it).
- The unique 2-`omega_vec`-critical tournament is the directed `C₃`.
- In this repository Question 5.9 is already negative at `k=3` (also at
  `k=4,5`). Conjecture 5.10 is proved for `k=3,4,5` and open for `k≥6`.

## The oracle (sound, exact)

`scripts/core.py` computes `omega_vec` **exactly** — full `n!` order enumeration
(`n ≤ 7`) and an exact branch-and-bound returning the identical value (the two
are cross-checked in the tests, including on `S~₃`, `n=9`). Plus tournament
checks, criticality, and the minimal-certificate measurement for Question 5.9.

```bash
.venv/bin/python scripts/oracle.py landmarks          # paper anchor table
.venv/bin/python scripts/oracle.py check c3 --cert     # omega_vec=2, min cert order
.venv/bin/python scripts/oracle.py stilde 3            # omega_vec(S~_3)=3 (Lemma 3.8)
.venv/bin/python scripts/oracle.py scan-critical 5 3   # enumerate, find 3-critical
```

`scripts/constructions.py`: `transitive_tournament`, `directed_C3`, the `delta`
substitution `Δ(T₁,T₂,T₃)`, `S_tilde(n)` (`S~₁=TT₁`, `S~_n=Δ(S~_{n-1},·,·)`),
`random_tournament`, `all_tournaments`.

## Verified against the paper

`tests/test_oracle.py` (12 tests, ~16 s) pins the oracle to the paper's known
values: `omega_vec(C₃)=2` and `C₃` 2-`omega_vec`-critical; `omega_vec(TT_k)=1`;
`omega_vec(S~_n)=n` for `n=1,2,3` (Lemma 3.8 lower bound, BB == brute force);
the `n=3` 2-critical scan reproduces *"`C₃` is the unique 2-`omega_vec`-critical
tournament"*; no `omega_vec=3` tournament on ≤5 vertices.

## Layout

```
ledger.json                engine state (central_question, benchmark, proved,
                           open_crux, live_hypotheses, decision_log, gates)
scripts/core.py            exact omega_vec (brute force + branch-and-bound), criticality
scripts/constructions.py   tournament families (TT_k, C3, Δ, S~_n, random/all)
scripts/oracle.py          CLI: landmarks | check | stilde | scan-critical
scripts/route2_credit_deadlock.py
                           H25 credit/deadlock and demand-map checker
scripts/route2_append_partners.py
                           append-built full-raiser/partner experiment
scripts/stilde_growth_bounds.py
                           rigorous S~ growth tables and first-moment counts
scripts/stilde_pod_profiles.py
                           canonical three-poset rank profiles for S~ orders
scripts/decide_stilde_layer_product.py
                           exact SAT decisions for canonical layer volume
tests/test_oracle.py       regression suite (paper's known values)
docs/STATUS.md             current status and post-D45 corrections
docs/h19_refutation.md     iterated-C3 refutation of H19
docs/stilde_growth_and_q59.md
                           growth constant and criticality implications
docs/stilde_pod_tightness.md
                           exact reduction of the pod-tightness question
Refs/2310.04265.tex        paper source (definitions cited by line number)
```

## Setup

Uses the shared engine venv (symlinked `.venv`): `networkx` is the only
dependency for `omega_vec`. Requires nothing beyond it.

```bash
.venv/bin/python -m pytest tests/ -q
.venv/bin/python scripts/route2_append_partners.py
```
