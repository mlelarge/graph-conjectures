# `new_c5_a` — `C_5[3,3,5,3,5]`

Time-boxed SMS biplanarity test of the weighted clique blowup
$C_5[K_3, K_3, K_5, K_3, K_5]$ on 19 vertices, surfaced by
[`scripts/cycle_blowup.py enumerate`](../../scripts/cycle_blowup.py) and
launched via
[`scripts/earthmoon_blowup.py --weights 3,3,5,3,5`](../../scripts/earthmoon_blowup.py).

## Verdict

**Not biplanar (UNSAT).** No `Solution` lines emitted; `Search finished`
cleanly with `exit_status = 0`; `ThicknessTwoChecker` was active throughout
(2 124 878 calls, 1 212 620 Kuratowski blocking clauses added). The
chromatic number is $\chi = 10$ (exact, from the weighted-odd-cycle
formula), so a biplanar realization would have witnessed
$\chi_{\rm EM} \ge 10$. Since none exists, this candidate is excluded
without disturbing the bracket.

## Numbers

- $n = 19$, $m = 98$, $\omega = 8$, $\alpha = 2$, $\chi = 10$, slack $= 4$
- wall: 1207 s (≈20.1 min)
- SMS Total time: 985 s (≈16.4 min)
- Calls propagator: 10 162 478
- ThicknessTwoChecker: 2 124 878 calls, 1 212 620 added clauses
- MinimalityChecker: 651 138 calls, 5 427 added clauses

## Comparison to KSS candidate1

The two C_5 candidates are structural cousins ($n = 19$, $\omega = 8$,
$\chi = 10$) differing only in weight tuple (KSS used `4,4,4,4,3`, ours
`3,3,5,3,5`). Despite our candidate having one more edge of slack (4 vs 3),
SMS converged ≈4× faster wall and ≈2× faster internal — likely because
the more uneven fibre sizes give the symmetry-breaker more leverage. Both
yield UNSAT, so neither candidate alone settles the Earth–Moon problem,
but two more 19-vertex 10-chromatic biplanar candidates have been ruled
out for the literature.

## Reproduce

```bash
./scripts/run_smsg.sh new_c5_a 86400 \
    python /<abs>/earth_moon_problem/scripts/earthmoon_blowup.py --weights 3,3,5,3,5
```

Run from `problems/earth_moon_problem/`. The `earthmoon_blowup.py` wrapper
imports `PlanarGraphBuilder` from the v1.0.0 SMS clone (Patches A and C
applied — see [`docs/spike_sms_build.md`](../../docs/spike_sms_build.md)).
