# `new_c5_b` — `C_5[3,4,4,3,5]`

Second Phase 4 candidate run, second weight tuple of the two new 19-vertex
candidates surfaced by [`cycle_blowup.py enumerate`](../../scripts/cycle_blowup.py)
and not previously tested by KSS.

## Verdict

**Not biplanar (UNSAT).** No `Solution` lines emitted; `Search finished`
cleanly with `exit_status = 0`; `ThicknessTwoChecker` active throughout
(3 700 314 calls, 1 866 362 Kuratowski clauses added). Combined with
[`new_c5_a`](../new_c5_a/README.md), the two new 19-vertex 10-chromatic
$K_9$-free candidates we identified are both ruled out.

## Numbers

- $n = 19$, $m = 98$, $\omega = 8$, $\alpha = 2$, $\chi = 10$, slack $= 4$
- wall: 8405 s (≈2h 20m)
- SMS Total time: 3172 s (≈52.9 min)
- Calls propagator: 18 017 363
- ThicknessTwoChecker: 3 700 314 calls, 1 866 362 added clauses
- MinimalityChecker: 1 053 459 calls, 7 339 added clauses

## Structural sensitivity

The three 19-vertex C_5 candidates are structural cousins ($\omega = 8$,
$\chi = 10$, $K_9$-free) but their SMS solve times are wildly different:

| weights | slack | wall | SMS total | prop calls | Kuratowski added |
|---|---:|---:|---:|---:|---:|
| `4,4,4,4,3` (KSS) | 3 | 5062 s | 2037 s | 15.8 M | 1.26 M |
| `3,3,5,3,5` (new_c5_a) | 4 | 1207 s | 985 s | 10.2 M | 1.21 M |
| `3,4,4,3,5` (new_c5_b) | 4 | 8405 s | 3172 s | 18.0 M | 1.87 M |

Slack and the basic invariants don't predict wall-time — `3,3,5,3,5` is
≈7× faster than `3,4,4,3,5` despite identical $(n, m, \omega, \alpha, \chi)$.
A useful empirical note for sizing the C_7[K_4] budget: structural
parity in the fibre-size pattern (here, evenly split between odd and
even fibres) appears to cost the solver more than asymmetric splits.

## Reproduce

```bash
./scripts/run_smsg.sh new_c5_b 86400 \
    python /<abs>/earth_moon_problem/scripts/earthmoon_blowup.py --weights 3,4,4,3,5
```
