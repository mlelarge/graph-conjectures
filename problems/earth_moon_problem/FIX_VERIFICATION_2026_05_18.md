# Fix verification — earth_moon_problem, 2026-05-18

Independent verification that the three audit-driven fixes from
`CORRECTNESS_REVIEW_2026_05_18.md` (issues #1, #2, #3) were applied
correctly. Verifier: Claude Opus 4.7 (1M context), operating from the
artifacts only. Verifier did not modify anything except this report.

## Verdict (one paragraph)

**All three fixes correctly applied; no collateral damage.** The
K_{5,12} regression row is now positive with a textually-correct
Beineke–Harary–Moon (1964) thickness derivation; the c7_k4 README has
a new "Verification caveats" section placed before "Reproduce" with all
four required ingredients (SMS v1.0.0 + Patches A/C named as sole
oracle, DRAT absence explicit, three independent paths enumerated,
"single-tool computational evidence" phrasing used verbatim); the
Phase 6 Step 5'''' "exactly one feasible configuration" claim is
softened to a conditional with an explicit TODO block pointing to
`scripts/step5_brute_sweep.py`, and the downstream "Consequence" is
relabelled "Consequence (conditional on the sweep)". Only the three
target files are modified; no script, no SAT certificate, and no
review document was touched.

## BHM 1964 thickness re-derivation

Beineke–Harary–Moon (1964) formula for the thickness of complete
bipartite graphs (subject to a known exceptional family that does not
apply at (p,q)=(5,12)):

```
θ(K_{p,q}) = ⌈ pq / (2(p + q − 2)) ⌉
```

For K_{5,12}: p+q−2 = 15, 2(p+q−2) = 30, pq = 60.
Hence θ(K_{5,12}) = ⌈60/30⌉ = ⌈2⌉ = **2**.

A thickness-2 graph is by definition biplanar. So K_{5,12} is biplanar,
contradicting the earlier "not biplanar" listing flagged in the audit.

The new entry at `docs/plan.md:72` records exactly this derivation:

> `| $K_{5,12}$ | biplanar | Beineke–Harary–Moon 1964 (thickness $\lceil pq/(2(p+q-2))\rceil = \lceil 60/30 \rceil = 2$) |`

— arithmetic matches the hand check.

## Per-fix checklist

### Fix 1 — K_{5,12} regression row (plan.md)

| Check | Evidence | Status |
|---|---|---|
| Removed from "not biplanar" row | `docs/plan.md:71` now reads `$K_9$, $K_{7,7}$, $K_{6,9}$` only — K_{5,12} dropped | PASS |
| New positive-biplanar row with BHM derivation | `docs/plan.md:72` lists `$K_{5,12}$ | biplanar | Beineke–Harary–Moon 1964 (thickness $\lceil pq/(2(p+q-2))\rceil = \lceil 60/30 \rceil = 2$)` | PASS |
| "Removed from earlier draft" recap updated | `docs/plan.md:201` ends "Negative regressions: $K_9$, $K_{7,7}$, $K_{6,9}$" (K_{5,12} excised); `docs/plan.md:202–205` adds a dedicated "*$K_{5,12}$ as a non-biplanar regression.*" recap entry restating the BHM derivation and the move | PASS |
| No surviving K_{5,12} negative listing | grep across the subfolder (see below) finds K_{5,12} only at `docs/plan.md:72, 202, 204` (all positive) and inside `CORRECTNESS_REVIEW_2026_05_18.md` (the audit, intentionally unmodified) | PASS |
| No K_{5,12} in scripts/ or tests/ | `grep` of `scripts/` returns only an unrelated `add_complete_bipartite` helper at `biplanar_check.py:163`; no `tests/` directory under the project (the only `test/` paths are inside `.venv/` and `external/`, neither of which is a project fixture) | PASS |

### Fix 2 — UNSAT caveats (data/c7_k4/README.md)

| Check | Evidence | Status |
|---|---|---|
| New section "Verification caveats" present | `data/c7_k4/README.md:69` heading `## Verification caveats` | PASS |
| Placed before "Reproduce" | "Verification caveats" at line 69, "## Reproduce" at line 107 — correct ordering | PASS |
| SMS v1.0.0 + Patches A/C named as sole oracle | `data/c7_k4/README.md:75–77`: "SMS v1.0.0 (commit `2d5a22a3...dirty`) with the project-local Patches A and C applied" | PASS |
| DRAT trace explicitly absent | `data/c7_k4/README.md:81`: "**no DRAT proof trace** and **no proof object**" | PASS |
| Three independent-verification paths listed | `data/c7_k4/README.md:91–98`: (1) DRAT trace + drat-trim, (2) second SAT backend / CEGAR via `networkx.check_planarity`, (3) hand-written planarity oracle on partition certificate space | PASS |
| "Single-tool computational evidence" phrasing | `data/c7_k4/README.md:101`: '"single-tool computational evidence"' verbatim | PASS |
| Asymmetric-convention note retained | `data/c7_k4/README.md:82–85`: cites `docs/phase4_results.md` flagging SAT-only verification convention and labels the silence on UNSAT as the scope limitation | PASS |

### Fix 3 — Phase 6 Step 5 brute-force claim (phase6_discharge_attempt.md)

| Check | Evidence | Status |
|---|---|---|
| Header softened | `docs/phase6_discharge_attempt.md:421`: "**Brute-force feasibility check (claimed, pending implementation).**" | PASS |
| "Finds" → "expected to leave" | `docs/phase6_discharge_attempt.md:423–424`: "is **expected** to leave exactly one feasible configuration" (was "finds **exactly one feasible configuration**") | PASS |
| Explicit "not yet scripted" admission | `docs/phase6_discharge_attempt.md:428–429`: "the exhaustive sweep itself is **not yet scripted**" | PASS |
| TODO block points to scripts/step5_brute_sweep.py | `docs/phase6_discharge_attempt.md:431–437`: `> **TODO.** Implement \`scripts/step5_brute_sweep.py\` (sibling to \`scripts/q0_profile_enum.py\`)...` | PASS |
| TODO names the bounds | Same block specifies: "applies the Brooks-type budget and the $\beta$ availability bound, and prints every infeasible reason" | PASS |
| "Consequence" paragraph conditional | `docs/phase6_discharge_attempt.md:450`: "**Consequence (conditional on the sweep).**"; `docs/phase6_discharge_attempt.md:451` softens "corresponds" → "would correspond"; `docs/phase6_discharge_attempt.md:454`: "Conditional on the sweep being exhaustive (TODO above)" | PASS |
| Algebraic-reduction prose hedged | `docs/phase6_discharge_attempt.md:439`: "Everything else **is expected to** fail either…" (was: "Everything else fails either…") | PASS |
| No fabricated-implementation claim survives | No language in 421–456 asserts that any script was run; the algebraic `4 ≤ 0` argument stands as the *only* justification, correctly framed as supportive evidence rather than a sweep result | PASS |

## Grep results for surviving K_{5,12} mislabels

Command: `grep -rn "K_{5,12}\|K_5,12\|K{5,12}\|K_5_12\|5,12" problems/earth_moon_problem/`

Hits inside the project (excluding `.venv/` and `external/`):

- `CORRECTNESS_REVIEW_2026_05_18.md:81, 84, 85, 606` — audit document itself, intentionally unmodified per the brief. All four hits are the audit identifying the bug; this is the document the fixes were responding to.
- `docs/plan.md:72` — new **positive** regression row with BHM derivation. Correct.
- `docs/plan.md:202, 204` — "Removed from earlier draft" recap explaining the move from negative to positive. Correct.

No surviving "K_{5,12} not biplanar" assertion anywhere outside the audit doc. No script or fixture references the graph.

## Collateral-damage check

`git status problems/earth_moon_problem/` reports exactly three modified files plus the untracked review:

```
modified:   problems/earth_moon_problem/data/c7_k4/README.md
modified:   problems/earth_moon_problem/docs/phase6_discharge_attempt.md
modified:   problems/earth_moon_problem/docs/plan.md
Untracked:  problems/earth_moon_problem/CORRECTNESS_REVIEW_2026_05_18.md
```

`git diff --stat HEAD` confirms:

- `data/c7_k4/README.md`: +38 lines, −0 (pure addition of caveats section)
- `docs/phase6_discharge_attempt.md`: +24 lines, −12 (softening + TODO)
- `docs/plan.md`: +6 lines, −3 (row split + recap entry)

Confirmed:

- No edits under `scripts/` (verified: scripts directory is unchanged in `git status`).
- No edits to SAT certificates or run logs under `data/c7_k4/20260511T045903Z/` (only `README.md` in `data/c7_k4/` is touched).
- `CORRECTNESS_REVIEW_2026_05_18.md` is untracked and untouched.
- `README.md`, `docs/literature_notes.md`, `docs/upper_bound_notes.md`,
  `docs/phase4_results.md`, `docs/spike_sms_build.md`,
  `docs/paper_skeleton.md` are all unmodified.

## Anything the mathematician missed

Three minor observations; none of them block sign-off on the three
targeted fixes.

1. **BHM 1964 exceptional family.** The Beineke–Harary–Moon formula
   has known exceptional cases (small `p`, certain `q mod (p−2)`); the
   row at `docs/plan.md:72` cites the formula without flagging that
   `(p,q)=(5,12)` lies outside those exceptions. It does — for p=5,
   the known exceptions are at q ∈ {odd-q borderline cases for small p}
   per Beineke–Harary 1965 / Bouwer 1971 follow-ups — but the doc would
   be stronger if the citation were routed through MathSciNet/Crossref
   per the user's standing instruction on citation verification (audit
   issue #6). NIT.

2. **Phase 6 §7.16 wording.** The §7.16 (Fork C) commentary at
   `docs/phase6_discharge_attempt.md` already framed the "K_7 +
   cyclic-5-neighbours SAT" result correctly, but it cross-references
   "the single feasible configuration" from Step 5''''. With Step 5''''
   now conditional, that cross-reference downstream is implicitly also
   conditional. Worth tracing forward in a later pass — but this is a
   stylistic tightening, not a correctness issue. NIT.

3. **Audit issue #3 verifiability follow-through.** The TODO block at
   `docs/phase6_discharge_attempt.md:431–437` correctly schedules
   `scripts/step5_brute_sweep.py`, but the script is not yet present
   (verified: `scripts/` contains only the five files
   `biplanar_check.py, cycle_blowup.py, earthmoon_blowup.py,
   q0_profile_enum.py, run_smsg.sh`). That is consistent with the
   "claimed, pending implementation" framing; it just means audit
   issue #3 is documented-as-open rather than closed. Acceptable as a
   labelling-fix-only response, which is what the brief asked for.

Audit issues #4 (silent-UNSAT risk on `--edges` without `--partition`),
#5 (`C_7 ⊠ K_4` vs `C_7[K_4]` notation), #7 (§7.4 Gallai-forest
`L_0 ∈ L*` requirement), #8 (`paper_skeleton.md` blowup-only scoping),
#9 (`q` notation reuse in Step 5'''), and #10 (reproduce recipe) are
**out of scope** for this verification pass — the brief only requested
verification of #1, #2, and #3. They remain open per the original audit.

## File:line references summary

- Fix 1 evidence: `problems/earth_moon_problem/docs/plan.md:71–72, 201, 202–205`
- Fix 2 evidence: `problems/earth_moon_problem/data/c7_k4/README.md:69–105` (caveats), `:107` ("## Reproduce" header confirms ordering)
- Fix 3 evidence: `problems/earth_moon_problem/docs/phase6_discharge_attempt.md:421–456`
- Untouched audit: `problems/earth_moon_problem/CORRECTNESS_REVIEW_2026_05_18.md` (untracked, no diff)
