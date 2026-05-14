# Weighted CDC certificates — Phase 1 status

Calibration target from
[cdc_gadget_plan.md](cdc_gadget_plan.md) §"Phase 1":

> Find a certificate strictly more general than an oriented 4-CDC that
> constructs a $\Sigma_4$-flow on snarks without forcing a
> nowhere-zero 4-flow.

The candidate certificate is the **weighted CDC** introduced in
[scripts/cdc_weighted.py](../scripts/cdc_weighted.py): pick any CDC
$\mathcal{C} = \{C_1, \ldots, C_t\}$, assign each cycle a vector
$w_k \in \mathbb{R}^4$ with $\sum_i (w_k)_i = 0$, and require every
edge vector $v_e = \sigma_{e,i} w_i + \sigma_{e,j} w_j$ to lie in
$\Sigma_4 = \{x : \sum x_i = 0, \sum x_i^2 = 2\}$.

The signs $\sigma_{e,k}$ are the cycle-direction signs relative to the
canonical edge orientation. Unlike the discrete H_4 construction, the
weighted version does **not** require these signs to be opposite on
every edge — the continuous cycle vectors absorb the difference. This
is exactly the slack that the discrete construction lacks on snarks.

## Headline result

The weighted CDC ansatz explains the canonical small snarks for which
the discrete H_4 construction is impossible:

| Graph | CDC used | $\|F\|^2$ at solution | $S^2$ verify |
|---|---|---:|:---:|
| Petersen | 6 pentagons (the standard unorientable CDC) | $6.9 \times 10^{-31}$ | ✓ |
| Blanuša-2 | lengths $\{5,5,5,5,5,5,6,9,9\}$ | $7.6 \times 10^{-31}$ | ✓ |
| $J_5$ | lengths $\{5,6,6,6,6,6,7,7,11\}$ | $1.1 \times 10^{-30}$ | ✓ |

Verification is by passing the projected $\Sigma_4 \to S^2$ vectors
through the existing `witness.verify_witness` Kirchhoff check
(max norm error $\sim 10^{-16}$, max vertex residual $\sim 10^{-16}$,
all under the $10^{-7}$ tolerance).

The single most informative cell is **Petersen**. The 6-pentagon CDC is
the canonical *unorientable* CDC (see
[cdc_negative_calibration.md](cdc_negative_calibration.md) and
[tests/test_cdc.py](../tests/test_cdc.py)
`test_orient_petersen_pentagons_fails`). The H_4 / oriented-4-CDC
construction therefore cannot use it. The weighted relaxation
succeeds anyway. This says concretely that **the weighted ansatz is
strictly stronger than the discrete one on snarks**, not just an
incidental refactor.

## Partial / open instances

| Graph | Status | Diagnostic |
|---|---|---|
| Blanuša-1 | unsolved with the first ~4 CDCs (best rss $\approx 1.1 \times 10^{-3}$) | Need to enumerate more / longer CDCs; the rss floor is far above machine zero, suggesting the tried CDCs are genuinely infeasible for the weighted ansatz rather than the optimiser being stuck. |
| $J_7$ | no CDC found within 30 s | `cdc.find_cdc` cycle enumeration is the bottleneck for $n \geq 28$. Need either a more focused cycle pool (smaller `max_cycle_length`) or a structural CDC (e.g., the flower-snark uniform CDC for Phase 2). |

These are engineering, not theoretical, gaps. Blanuša-1 is the more
interesting probe: if no CDC of Blanuša-1 admits a weighted $\Sigma_4$
flow, the abstraction has a real gap. If a CDC eventually works, the
gap is just in cycle enumeration.

## What this rules out / does not rule out

- **Does** rule out the previous false working theorem (oriented 4-CDC
  ⇒ $S^2$-flow on snarks). The weighted relaxation uses the same CDC
  scaffolding but breaks the orientability requirement.
- **Does not** prove anything about infinite families. The current
  certificate is per-graph, not parametric.
- **Does not** explain how to *choose* the CDC. The Phase 1 sweep tries
  the first CDC found by lex-min backtracking; for Blanuša-1 this is
  not enough.

## Phase 1 → Phase 2 hand-off

The next move per [cdc_gadget_plan.md](cdc_gadget_plan.md) §"Phase 2"
is to attempt a *uniform parametric* weighted-CDC for the flower-snark
family $J_{2k+1}$ via the canonical CDC (one cycle per spoke fan, one
b-cycle, one cd-cycle). If the per-$k$ system admits a solution with
the same structural shape independent of $k$, the construction lifts
to an infinite-family $S^2$-flow theorem. If not — i.e., the
parametric system is inconsistent for some $k$ — then the weighted CDC
is not the right abstraction for flower snarks and the project should
pivot to gadget composition (Phase 3) or HMM blow-up reductions.

The Phase 1 result above gives provisional confidence: $J_5$ already
admits a weighted-CDC $S^2$-flow with a CDC that *includes* the
flower-snark structural cycles (a length-5 spoke fan plus several
length-6 transverse cycles). The next experiment is to see whether
the same template (with $k$-dependent cycle lengths) carries the
parametric solution.

## Files

- [scripts/cdc_weighted.py](../scripts/cdc_weighted.py) — solver
- [scripts/cdc.py](../scripts/cdc.py) — CDC enumeration + H_4 negative
  calibration
- [tests/test_cdc_weighted.py](../tests/test_cdc_weighted.py) — 4
  regression tests
- [docs/cdc_negative_calibration.md](cdc_negative_calibration.md) —
  why the discrete H_4 route is dead for snarks
