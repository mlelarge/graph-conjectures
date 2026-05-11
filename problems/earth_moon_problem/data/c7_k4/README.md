# `c7_k4` — `C_7[K_4] = C_7 \boxtimes K_4`

Phase 4 headline run. Biplanarity test of the clique blowup
$C_7[K_4, K_4, K_4, K_4, K_4, K_4, K_4]$ on 28 vertices — the natural
lift of KSS's $C_5[4,4,4,4,3]$ candidate1 to the 7-fold cyclic family.
The flag `--earthmoon_candidate2` is shipped in
[`encodings/planarity.py`](../../external/sat-modulo-symmetries/encodings/planarity.py)
at v1.0.0, but the SAT 2023 paper reports no result on it.

## Verdict

**Not biplanar (UNSAT).** No `Solution` lines emitted; `Search finished`
cleanly with `exit_status = 0`. `ThicknessTwoChecker` was active
throughout (12 985 926 calls, 3 844 963 Kuratowski clauses added).
The most prominently cited candidate for $\chi_{\rm EM} \ge 10$ in the
weighted-clique-blowup family is now ruled out.

## Numbers

- $n = 28$, $m = 154$, $\omega = 8$, $\alpha = 3$, $\chi = 10$, slack $= 2$
- wall: 34 834 s (9 h 40 min 34 s)
- SMS Total time: 24 372 s (6 h 46 min)
- Calls propagator: 64 932 163
- ThicknessTwoChecker: 12 985 926 calls, 3 844 963 added clauses
- MinimalityChecker: 3 248 494 calls, 8 440 added clauses
- Within KSS's published 2-day timeout cap with ample margin.

## Significance

$C_7[K_4]$ has been on the Earth–Moon shortlist for years as the
"natural" 28-vertex 10-chromatic $K_9$-free candidate, sitting at edge
slack 2 against the biplanar edge bound $6n - 12 = 156$. Ruling it out
removes the most-mentioned construction-based candidate for raising the
lower bound to 10. The bracket $9 \le \chi_{\rm EM} \le 12$ is unchanged
by this result, but the population of unverified candidates shrinks
materially.

## Scaling against the C_5 cases

| weights | n | wall | SMS total | prop calls | Kuratowski added |
|---|---:|---:|---:|---:|---:|
| `4,4,4,4,3` (candidate1) | 19 | 5062 s | 2037 s | 15.8 M | 1.26 M |
| `3,3,5,3,5` (new_c5_a) | 19 | 1207 s | 985 s | 10.2 M | 1.21 M |
| `3,4,4,3,5` (new_c5_b) | 19 | 8405 s | 3172 s | 18.0 M | 1.87 M |
| `4,4,4,4,4,4,4` (c7_k4) | 28 | 34 834 s | 24 372 s | 64.9 M | 3.84 M |

The 19 → 28 vertex jump cost roughly 8–24× SMS internal time depending
on the C_5 baseline. The 7-fold cyclic symmetry of the underlying odd
cycle is broken effectively by SMS (only 8.4 K minimality-check
clauses) but the planarity propagator does substantially more work
(3.84 M Kuratowski clauses vs 1.2–1.9 M for the C_5 cases).

## Phase 4 closure

All four candidates surfaced by
[`cycle_blowup.py enumerate`](../../scripts/cycle_blowup.py) under the
default constraints ($n \le 30$, $\omega \le 8$, $\chi \ge 10$,
$m \le 6n - 12$) are now ruled out as non-biplanar. The Phase 4
construction template — weighted clique blowups of odd cycles — has
been exhausted.

The Earth-Moon bracket remains $9 \le \chi_{\rm EM} \le 12$. Next
natural directions: relax the enumerator constraints (allow $\omega = 9$
admitting $K_8$ subgraphs other than fibre joins), broaden the
construction template beyond cycle clique blowups (Catlin's
constructions, replacement products), or pivot to Phase 6 (the
Kostochka–Yancey + $K_9$-free density route to $\chi_{\rm EM} \le 11$).

## Reproduce

```bash
./scripts/run_smsg.sh c7_k4 172800 \
    python /<abs>/earth_moon_problem/scripts/earthmoon_blowup.py --weights 4,4,4,4,4,4,4
```
