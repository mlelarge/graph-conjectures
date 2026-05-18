# Fix Verification — 2026-05-18

Independent verification of the targeted fixes the mathematician
applied in response to `CORRECTNESS_REVIEW_2026_05_18.md` findings
M1, M2, M3. This document does not re-audit the underlying proof;
it certifies only that the claimed fixes are present, correctly
positioned, and behave as advertised on the n = 10 sanity sweep.

## Verdict

All three fixes have been applied correctly. The per-completion
assertion (M3) is positioned exactly where it should be in both
miner pipelines — after the 4-outregularity check, before the
length-8 DFS — and mirrors the score-sequence and Claim-12 checks
of `scripts/k4_verify_certificate.py:127-146` faithfully. The
assertion is n-agnostic (it reads `S`, `target_S_map`/`score_map`,
`CYCLE_V`/`CYCLE_VERTICES`, and `n` via lexical closure) and
applies uniformly to all four score profiles. The n = 10 sanity
sweep I ran on both pipelines reproduces 32 configurations / 4,792
total completions / no AssertionError exactly as claimed, and the
per-(S, T) completion counts agree byte-for-byte across the two
pipelines. The "Caveats and remaining work" section added to
`docs/k4_n11_proof.md` (M1/M2 documentation fix) is accurate,
non-editorialising, and explicitly names a SAT- or naive-enumeration
third pipeline as the way to close M1. Collateral damage is nil:
only the two miner scripts and the n = 11 doc were modified;
`data/k4_n10_certificate.json` (10 MB), `docs/k3_hand_proof.md`
(δ = 3 hand proof), `scripts/k4_verify_certificate.py`, and all
other audit/test/data files are untouched.

## Assertion-code review (M3)

### `scripts/k4_score_profile_miner.py:321-350`

```python
# (after 4-outregularity at line 319, before DFS at line 352)
# M3 fix (2026-05-18): explicit per-completion assertion
# mirroring scripts/k4_verify_certificate.py lines 127-146.
# ...
for s in S:
    d_S = 0
    for (u, w) in arcs:
        if u != s:
            continue
        if w in S:
            d_S += 1
        if w not in CYCLE_V:
            raise AssertionError(
                f"Claim 12 violated at completion: S-vertex {s} "
                f"sends arc to {w} not in V(C); "
                f"S={sorted(S)}, target_S_map={target_S_map}, n={n}"
            )
    if d_S != target_S_map[s]:
        raise AssertionError(
            f"Score profile violated at completion: S-vertex {s} "
            f"has d^+_S = {d_S}, expected {target_S_map[s]}; "
            f"S={sorted(S)}, target_S_map={target_S_map}, n={n}"
        )
```

### `scripts/k4_score_profile_independent_check.py:308-338`

```python
# (after 4-outregularity at line 306, before DFS at line 340)
# M3 fix (2026-05-18): explicit per-completion assertion
# mirroring scripts/k4_verify_certificate.py lines 127-146.
# ... Symmetric to the same assertion in k4_score_profile_miner.py.
for s in S:
    d_S = 0
    for (u, w) in arcs:
        if u != s:
            continue
        if w in S:
            d_S += 1
        if w not in CYCLE_VERTICES:
            raise AssertionError(
                f"Claim 12 violated at completion: S-vertex {s} "
                f"sends arc to {w} not in V(C); "
                f"S={sorted(S)}, score_map={score_map}, n={n}"
            )
    if d_S != score_map[s]:
        raise AssertionError(
            f"Score profile violated at completion: S-vertex {s} "
            f"has d^+_S = {d_S}, expected {score_map[s]}; "
            f"S={sorted(S)}, score_map={score_map}, n={n}"
        )
```

Side-by-side findings:

- **Positioning.** Both blocks sit between the 4-outregularity
  rejection (`miner` line 319 / `independent_check` line 306) and
  the length-8 path search (`miner` line 352 / `independent_check`
  line 340), exactly as specified. They run only when `idx ==
  len(free_choices)`, i.e. on assembled completions, not on
  partial states.
- **Mirrors the verifier.** `scripts/k4_verify_certificate.py:127-131`
  expresses Claim 12 as "for all `s in S`, for all `(u, v) in
  arcs_set`, if `u == s` then `v in CYCLE_V`"; lines 138-146
  express the score sequence as `d^+_S = sum(1 for (u, v) in
  arcs_set if u == s and v in S)` and compare to the expected
  per-vertex target. Both miner blocks reproduce both checks in
  one fused pass, with the same logical predicates. The naming
  difference (`CYCLE_V` vs `CYCLE_VERTICES`, `target_S_map` vs
  `score_map`) is cosmetic — both refer to `frozenset(range(1,
  8))` (`miner:273`, `independent_check:268`) and the configured
  target out-degree-into-S map.
- **Error messages.** Both raise `AssertionError` (not bare
  `assert`, so `python -O` won't elide the check) and embed
  `S=sorted(S)`, the target map, and `n` in the message. The
  Claim-12 message also names the offending arc endpoint `w`.
  Informative for failure diagnosis.
- **n-agnosticity.** Neither block hard-codes `n=10` or `n=11`. The
  closure variables (`S`, `target_S_map`/`score_map`, `CYCLE_V`/
  `CYCLE_VERTICES`, `n`) are captured from `check_pair`/
  `enumerate_completions`, which themselves take `n` as a
  parameter. The assertion therefore fires the same way for any
  `n` and for any of the four profiles `(1,1,1,1)`, `(2,1,1,1)`,
  `(2,2,1,1)`, `(3,1,1,1)`.
- **Soundness equivalence.** The fused loop computes `d_S` while
  scanning for Claim-12 violations. If a Claim-12 violation is
  found (`w not in CYCLE_V/CYCLE_VERTICES`), the function raises
  before the score-sequence check fires — i.e. Claim 12 is
  short-circuit-checked first. This matches the verifier's
  ordering (Claim 12 at step 6, score sequence at step 8).

## Sanity-sweep output (n = 10)

I ran both pipelines locally with Python 3.12.4 on Darwin 25.4.0.

`python3 scripts/k4_score_profile_miner.py 10`:

- Profile (1,1,1,1): 0 configurations.
- Profile (2,1,1,1): 4 configurations, 4 × 27 = 108 completions.
- Profile (2,2,1,1): 24 configurations, mixed counts
  (343/176/18) summing to 4,212 completions.
- Profile (3,1,1,1): 4 configurations, 4 × 255 = 1,020 completions.
- **Grand summary: 32 configurations closed, 0 not closed, 4,792
  total completions, no AssertionError.**

`python3 scripts/k4_score_profile_independent_check.py 10`:

- Same four-profile breakdown, same per-(S, T) completion counts,
  same total 4,792 completions, "Independent closure check
  passed. All 32 configurations in the configuration universe
  (0 + 4 + 24 + 4) closed", no AssertionError.

Both runs finished in well under 1 second. The 4,792 figure
matches the mathematician's claim. (Note: this is the miner's
"configuration universe" count, which includes some (S, T) pairs
that the n = 10 proof's σ(T) ⊆ S filter would drop —
`docs/k4_n10_proof.md` lines 220-226 reports 24 configurations /
3,664 completions for the σ(T) ⊆ S restricted universe. The
discrepancy is by design and unrelated to the M3 fix.)

I did not re-run the n = 11 sweep; the assertion is
n-agnostic, so the n = 10 negative result (no AssertionError on
4,792 completions across all four profiles) is sufficient evidence
that the check does not spuriously fire on valid completions.

## Doc-caveats checklist (`docs/k4_n11_proof.md:238-304`)

| Item | Required | Status | Citation |
|---|---|---|---|
| "Caveats and remaining work" section exists | yes | yes | line 238 |
| Shared-spec limitation stated (M1) | yes | yes | lines 242-258 — "The two pipelines share a declarative rule specification" |
| No per-completion certificate at n = 11 stated (M2) | yes | yes | lines 260-274 — "No per-completion certificate exists at n = 11; closure is reproduction-only" |
| SAT or naive third pipeline mentioned as M1 closer | yes | yes | lines 276-290 — "a SAT/CSP encoding ... or a brute-force enumeration" |
| Mention of the M3 mitigation already in place | bonus | yes | lines 292-304 — names the per-completion assertion |
| No editorialising / no invented caveats | yes | yes | every caveat traces to M1/M2/M3 or is a direct supporting clarification |

The caveat section also correctly notes (lines 287-290) that the
SAT/naive pipeline is "out of scope for the current artifact",
keeping the doc honest about what was and was not done.

## Collateral-damage check

`git status` on `problems/directed_path_minimum_outdegree/` shows
exactly three modified files:

- `docs/k4_n11_proof.md`
- `scripts/k4_score_profile_independent_check.py`
- `scripts/k4_score_profile_miner.py`

Plus one untracked file (`CORRECTNESS_REVIEW_2026_05_18.md`, the
audit itself).

Spot-check of files that should not have been touched:

- `data/k4_n10_certificate.json` (~10 MB): mtime 9 May 16:53,
  untouched.
- `docs/k3_hand_proof.md` (δ = 3 hand proof): mtime 9 May 23:11,
  untouched.
- `scripts/k4_verify_certificate.py` (the n = 10 certificate
  verifier — reference for the assertion): mtime 9 May 23:12,
  untouched.
- `scripts/k4_audit.py`, `scripts/k4_local_miner.py`,
  `scripts/k4_independent_check.py`, `scripts/k4_general_miner.py`,
  `scripts/k4_n11_full_run.py`, `scripts/k4_n11_overflow_cases.py`:
  all mtime 9 May, untouched.
- `docs/k4_n10_proof.md`, `docs/k4_partial_appendix.md`,
  `docs/literature_notes.md`, `docs/plan.md`: all mtime 9 May,
  untouched.

No collateral damage.

## Anything the mathematician missed

Two minor observations, none blocking:

1. **No positive test of the failure path.** The assertion has
   been observed never to fire, which is consistent with "the
   propagation is correct" but also with "the assertion is
   unreachable due to a typo". I inspected the code and the
   assertion is correctly wired; a 5-line test that injects a
   bad completion and asserts the AssertionError fires would
   nonetheless harden the regression guard.

2. **The M3 fix does not extend to Lemma-A-reverse / antiparallel
   invariants** which `scripts/k4_verify_certificate.py:133-136`
   also checks at the verifier. The audit's M3 finding asked only
   for score sequence + Claim 12, so the fix is in-scope — but
   widening the assertion to cover the other verifier invariants
   would defend against a broader class of propagation regressions
   at zero asymptotic cost.

Neither qualifies as a defect in the M1/M2/M3 fix as specified.
The fixes as delivered are correct and complete with respect to
the audit's stated requirements.
