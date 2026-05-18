# Fix verification — 3-decomposition workstream

**Date:** 2026-05-18
**Verifier:** Independent (post-audit, follow-up to `CORRECTNESS_REVIEW_2026_05_18.md`)
**Scope:** confirm fixes #1–#3 claimed by the mathematician in response to the review.

## Verdict

**LANDED CLEAN.** All three claimed fixes are present, syntactically correct, semantically faithful to the review request, and accompanied by comments referencing `CORRECTNESS_REVIEW_2026_05_18.md`. The full test suite still reports **33/33 passing**. No collateral edits outside the three claimed files; no contradictions introduced with `docs/plan.md` or `docs/minimal_counterexample.md`; the asserts are not exercised on any code path that would legitimately use a smaller universe.

## Per-fix checklist

### Fix #1a — assertion in `scripts/full_replacement_sweep.py::is_compatibility_universal`

- **Location:** `problems/3_decomposition_conjecture/scripts/full_replacement_sweep.py:84-92`
- **Status:** PRESENT.
- **Body (verbatim, lines 85–92):**
  ```
  # Defensive: the theoretical universe U has exactly 16 traces
  # (trace_feasibility.py / docs/minimal_counterexample.md §3.4). A stale
  # or partial lattice could silently shrink the inferred universe and
  # turn this predicate into a weaker check than §3.13 requires.
  # See CORRECTNESS_REVIEW_2026_05_18.md (CRITICAL finding).
  assert len(universe) == 16, (
      f"universe must have 16 traces (16-trace theorem, §3.4); got {len(universe)}"
  )
  ```
- **Semantics:** matches the CRITICAL recommendation in the audit (review line 172). Comment cites both `trace_feasibility.py` and §3.4, and explicitly names the review.

### Fix #1b — assertion in `scripts/compatibility_universality.py::is_compatibility_universal`

- **Location:** `problems/3_decomposition_conjecture/scripts/compatibility_universality.py:25-33`
- **Status:** PRESENT (same comment block and assert as #1a, transposed to the two-return-value variant).
- **Semantics:** identical guard; comment cites the review.

### Fix #2 — README Sub-lemma 1′ softening

- **Location:** `problems/3_decomposition_conjecture/README.md:13-26`
- **Status:** PRESENT.
- **Before:** "**First proof step done.** … Sub-lemma 1' … is computer-checked on all connected 1-port subcubic graphs with $n \le 11$ vertices …".
- **After (lines 15–26):** "**First proof step: Lemma 1 proved; Sub-lemma 1' computer-checked through n=11.**" with explicit "**not yet proved in this codebase**", the 137-graph breakdown across $n\in\{5,7,9,11\}$, the Aboomahigir–Ahanjideh–Akbari (DAM 2021) reference, and a closing caveat that bridgelessness "currently rests on this finite check together with the assumption that no counterexample to Sub-lemma 1' exists at $n \ge 13$."
- **Matches the review's recommended wording** (review line 37). Consistent with `docs/plan.md` and `docs/minimal_counterexample.md:174,188,1345` (which both label Sub-lemma 1′ as "to be proved separately").

### Fix #3 — Tests still pass

- **Command:** `/Users/lelarge/Recherche/graph-conjectures/.venv/bin/python -m pytest problems/3_decomposition_conjecture/tests/`
- **Result:**
  ```
  platform darwin -- Python 3.12.4, pytest-9.0.3, pluggy-1.6.0
  collected 33 items
  problems/3_decomposition_conjecture/tests/test_decomposition.py ........ [ 24%]
  .........................                                                [100%]
  ============================== 33 passed in 5.82s ==============================
  ```
- **Status:** 33/33 PASS in 5.82s. The previously-pinned counts at `tests/test_decomposition.py:504-525` (`compatibility_universal_class_count == 43`, `axis_characterisation_agreement_count == 59`, `min_universal_trace_count == 4`, etc.) hold — confirming the new assert fires through `build_payload(...)` on the n≤10 lattice and the universe size really is 16 there.

## Collateral-damage check

- **`git status`** lists exactly three modified files (`README.md`, `scripts/compatibility_universality.py`, `scripts/full_replacement_sweep.py`) plus the untracked `CORRECTNESS_REVIEW_2026_05_18.md`. No edits to `data/`, `docs/`, other scripts, or tests.
- **Doc consistency:** the softened README aligns with `docs/plan.md` ("Provisional reading: as soon as Sub-lemma 1' is in hand…") and `docs/minimal_counterexample.md:174` ("subcubic existence; to be proved separately") and `minimal_counterexample.md:1345` ("Theorem (target; assumes Sub-lemma 1' and Lemma 2)"). No contradiction introduced.
- **Assert reach — call graph audit:**
  - `full_replacement_sweep.py:84` is called only at `full_replacement_sweep.py:133` inside `classify_trace_set`, whose `universe` argument is `union_of_all_traces(payload)` (line 206). Per the review, this union is size 16 for both `gadget_lattice_2pole_n10_both.json` and `..._n12_both.json` — assert holds.
  - `compatibility_universality.py:25` is called at lines 80 and 147 inside `build_payload`; `universe` is `{trace_key_from_json(t) for cls in lattice["classes"] for t in cls["traces"]}` (lines 70–74). Same lattice union — size 16 — assert holds.
  - `classIII_absorber_check.py` does **not** import either function; its "is_compatibility_universal" hits are output-dict keys, not call sites.
  - No other `.py` in `scripts/` or `tests/` calls these two functions (`grep -rn`).
- **No legitimate smaller-universe code path** exists: there is no internal/test caller that feeds a deliberately-partial universe (e.g., a single class's traces) into either function. The hard-coded `universe` literal at `tests/test_decomposition.py:464-481` (size 16, asserted at line 496) is used only with `are_2pole_traces_compatible` directly, not with the guarded predicate.

## Things the mathematician may want to address next (not blockers)

1. **README.md:106–118** ("Full n=14 all-class sweep complete") still presents the 2 `compat_universal_not_contained` records and the Universal Replacement Conjecture in a tone the audit (MAJOR, review line 80) found mildly optimistic. The Sub-lemma 1′ softening did not include a parallel caveat for n=14. Consider adding a one-line "this is empirical evidence for the Universal Replacement Conjecture at n≤14, not a proof" near line 118.
2. **`docs/minimal_counterexample.md:1346–1353`** has a pointer typo (audit MINOR, review line 82): the §4 target theorem cites "Lemma 2 (§3.4)" but the right cross-reference is §3.13 / §3.20. Untouched by this fix pass.
3. **No regression test pins the new assert.** A 2-line unit test that calls `is_compatibility_universal(set(), set())` and `pytest.raises(AssertionError)` would lock the guard in place across future refactors. The current 33 tests pass *with* the assert active but do not directly cover the failure path.
4. **`tests/test_decomposition.py:441-448`** (audit MINOR, review line 166) — the "K_4 − e is not strictly replaceable" test still does not pin class membership in C0; unchanged.

## Bottom line

The three requested fixes are landed correctly, with the right citations to the review, and the test suite is green. No collateral edits, no doc contradictions, no spurious assert reach. The CRITICAL finding from `CORRECTNESS_REVIEW_2026_05_18.md` (review line 172) is now closed; the MAJOR Sub-lemma 1′ framing concern (review line 37) is closed. The MAJOR-level README framing of the Universal Replacement Conjecture (review line 80) was *not* part of this fix pass and remains open.
