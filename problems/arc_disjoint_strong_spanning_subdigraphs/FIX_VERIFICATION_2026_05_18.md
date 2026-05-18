# Fix verification — EC-log Option A landing (C=6, n₀=3)

**Date:** 2026-05-18
**Auditor:** Independent verifier (Claude, distinct from the
mathematician who applied the fixes).
**Companion:** `CORRECTNESS_REVIEW_2026_05_18.md` §2.5 (the original
flag); §A.14.3 N1 of `team/05_audit.md` (the now-retracted prior
verdict).

---

## Verdict (one paragraph)

**LANDED WITH ISSUES (one cosmetic).** The Option A fix (headline
$C = 5, n_0 = 2 \to C = 6, n_0 = 3$) has been applied correctly and
consistently across all seven claimed files. The proof's binding
inequality $2\log_2 n > 3$ for the new constant holds tightly at the
integer level: at $n = 3$, $\lceil 6\log_2 3\rceil = 10$ and the
first-moment bound gives $\mathbb{E}[N] \le 8 \cdot 81 / 1024 \approx
0.633 < 1$. No old-constant ($C=5$, $n_0=2$) regressions survive
outside explicit retraction context. The audit file's N1 verdict is
properly marked AUDIT-STALE and N2–N5 are preserved verbatim. The
`code/` directory is untouched (git confirms). **Single cosmetic
issue:** the slack figure "$C = 6$ has approximately **4**–17 units
of slack in the $n \in [10, 1000]$ range" in
`paper/findings.md:43` and `paper/draft_v1.md:399` is off-by-one at
the lower end — at $n = 10$ the integer slack is **3**, not 4
(see §2 below). Substantive proof is unaffected.

---

## 1. Arithmetic re-verification

I re-derive the two gating inequalities used in
`team/04_ec_log_proof.md` §2.5 at $C = 6$.

**Gating (G1).** $\lambda \ge 3\log_2 n + 1$, used between the
factored form (9) and the bound (10). Substituting $\lambda = 6\log_2 n$:
$$6\log_2 n \ge 3\log_2 n + 1 \iff 3\log_2 n \ge 1 \iff \log_2 n \ge 1/3
\iff n \ge 2^{1/3} \approx 1.260.$$
Holds for all integer $n \ge 2$, in particular for $n \ge 3$.
**Matches** `team/04_ec_log_proof.md:106` and the paper draft
`paper/draft_v1.md:382–383`.

**Gating (G2)** = (11). $\lambda > 4\log_2 n + 3$, the first-moment
$\mathbb{E}[N] < 1$ requirement. Substituting $\lambda = 6\log_2 n$:
$$6\log_2 n > 4\log_2 n + 3 \iff 2\log_2 n > 3 \iff \log_2 n > 3/2
\iff n > 2^{3/2} = 2\sqrt 2 \approx 2.828.$$
The smallest integer $n$ that satisfies $n > 2\sqrt 2$ is $n = 3$.
Hence $n_0 = 3$ is **exactly tight** for (G2). **Matches**
`team/04_ec_log_proof.md:108` and `paper/draft_v1.md:380–382`.

**Spot-check at $n = 3$.** $\lceil 6\log_2 3\rceil = \lceil 9.510\rceil
= 10$. With $\lambda = 10$:
- geometric ratio $n^2/2^\lambda = 9/1024 \approx 0.00879$, so
  $\sum_{j\ge 1} (\cdot)^{j-1} = 1/(1 - 9/1024) \approx 1.009 \le 4/3$.
  (G1) is comfortable; (10) holds.
- first-moment bound $\mathbb{E}[N] \le 8 \cdot 3^4 \cdot 2^{-10}
  = 648/1024 \approx 0.633 < 1$. ✓
- The "tight at the integer level" remark in
  `team/04_ec_log_proof.md:110` is also verified: with the strict
  inequality $\lambda > 4\log_2 3 + 3 \approx 9.34$, the smallest
  integer $\lambda$ is $10$, exactly $\lceil 6\log_2 3\rceil$.

**Conclusion of §1.** The arithmetic in
`team/04_ec_log_proof.md` §2.5 (lines 101–122) is correct and the
binding inequality is the one the user identified.

---

## 2. Slack-figure check (minor issue)

The remark "$C = 6$ has approximately 4–17 units of slack in the
$n \in [10, 1000]$ range" appears at:
- `paper/findings.md:43`
- `paper/draft_v1.md:399`

Numerical sweep with the actual integer rounding used in the proof
(smallest integer $\lambda$ such that $2^\lambda > 8 n^4$):

| $n$ | $\lceil 6\log_2 n\rceil$ | smallest int $\lambda$ s.t. $2^\lambda > 8 n^4$ | slack |
|---:|---:|---:|---:|
| 10   | 20 | 17 | **3** |
| 20   | 26 | 21 | 5  |
| 50   | 34 | 26 | 8  |
| 100  | 40 | 30 | 10 |
| 200  | 46 | 34 | 12 |
| 500  | 54 | 39 | 15 |
| 1000 | 60 | 43 | 17 |

The lower end is **3**, not 4. `team/04_ec_log_proof.md:168`
("the slack ... is $\ge 4$ from $n = 20$ on") is correct;
`findings.md:43` and `draft_v1.md:399` are off-by-one at $n = 10$.
This is a cosmetic-level wording mismatch (text says 4–17 in a paper
context where 17 is the upper end; the upper end is correct). It
does not affect proof validity. Recommended one-character fix:
"4–17" → "3–17".

---

## 3. Per-file fix-confirmation table

| File | Claimed update | Verified at | Status |
|---|---|---|---|
| `team/04_ec_log_proof.md` | Headline + §2.5 + §2.6 + §3.1 + §3.2 table + §5 ledger | lines 17 (headline `$C = 6$, $n_0 = 3$`), 21–31 (Edit note 2026-05-18), 101–122 (arithmetic verification §2.5), 124–128 (§2.6 first-moment conclusion + $n_0$ rationale), 147 (§3.1 constants discussion), 153–168 (§3.2 table with $C=5$/$C=6$ columns), 251–261 (§5 sanity ledger says "EC-log promises decomposition? no ($6\log_2 4 = 12 > 2$)") | **OK** |
| `paper/findings.md` | Theorem 1 statement and slack figure | lines 22–24 (Theorem 1 at $C=6$, $n\ge3$), 26–32 (Edit note), 43 (slack figure "4–17") | **OK** (with the slack-figure off-by-one noted in §2) |
| `paper/draft_v1.md` | Abstract, §1.2, §3.4, §3.5, §10 | lines 27–29 (abstract: $6\log_2 n$, $n\ge3$, edit note), 96–103 (§1.2 Theorem 1 at $C=6$, $n_0=3$ + edit note), 352 / 374–390 (§3.4 union bound rewritten with verification of both gating conditions at $C=6$), 394 (§3.5 conclusion at $\lambda \ge 6\log_2 n$ and $n \ge 3$), 1227 (§10 restatement "$\lambda \ge 6\log_2 n$ (with $n \ge 3$)") | **OK** (slack figure note as in findings.md) |
| `paper/outline.md` | Theorem A statement | lines 34–40 (Theorem A at $C=6$, $n_0=3$ + edit note) | **OK** |
| `attack_plan.md` | EC-log mention | line 44 (`team/04_ec_log_proof.md` now described as "proof with $C = 6$, $n_0 = 3$" with an explicit retraction note for the prior $C = 5, n_0 = 2$ wording) | **OK** |
| `team/13_publishability_decision.md` | §1 + Route C bundle | lines 26 (§1 says "EC-log lemma at $C = 6$, $n_0 = 3$" with retraction parenthetical), 95–96 (Route C "EC-log at $C = 6$" with retraction reference) | **OK** |
| `team/05_audit.md` | N1 → AUDIT-STALE; §A.14.3 partially retracted | lines 3844–3854 (audit-stale note attached to N1 verbatim), 3951–3956 (§A.14.3 verdict explicitly says "CLEAN as of the audit date, **partially retracted 2026-05-18** for N1"), 3967 (cross-reference table for `team/04_*` adds "**AUDIT-STALE 2026-05-18**" tag), 4137 (final summary §A.14.7 numerical claims updated with parenthetical) | **OK** |

All seven claimed files were touched; all seven carry the new
constant; all seven explicitly reference
`CORRECTNESS_REVIEW_2026_05_18.md` §2.5 as the trigger.

---

## 4. Grep results for surviving old-constant references

Running across the subfolder (excluding the unchanged audit report
`CORRECTNESS_REVIEW_2026_05_18.md` itself):

```
team/04_ec_log_proof.md:22  > read "$C = 5$, $n_0 = 2$." That choice ...   [retraction context]
team/04_ec_log_proof.md:23,114,115,117,118,147,153,168                    [retraction / comparison context inside §2.5 remark, §3.1, §3.2 table]
team/05_audit.md:3828,3834,3839,3847,3849                                  [these are the original audit's verbatim quotes of the old headline + the new audit-stale note]
team/05_audit.md:3967,4137                                                 [the cross-reference table now flagged AUDIT-STALE]
team/13_publishability_decision.md:26,96                                   [retraction parenthetical]
attack_plan.md:44                                                          [retraction parenthetical]
paper/findings.md:27,29                                                    [edit note recording previous headline]
paper/outline.md:38                                                        [edit note]
paper/draft_v1.md:29,100,386,387                                          [abstract edit note + §1.2 edit note + §3.4 retraction]
```

**Every surviving occurrence of "$C = 5$" / "$n_0 = 2$" / "$5 \log_2 n$"
is in a documented retraction-or-comparison context.** No live
statement uses the broken constants. The grep is clean.

A second pass for "$n \ge 2$" in EC-log context:
- `team/04_ec_log_proof.md:106` — for (G1), $n \ge 2$ is a lower bound
  on where the inequality $3\log_2 n \ge 1$ first holds; the lemma
  headline $n_0 = 3$ is *stronger*. Internally consistent.
- `team/04_ec_log_proof.md:128` — degenerate $n = 2$ case explicitly
  excluded from the lemma headline by setting $n_0 = 3$.
- `paper/draft_v1.md:375, 383` — same internal use of "$n \ge 2$" as a
  lower bound on (G1), with the lemma's $n_0 = 3$ taking precedence.

No regression.

---

## 5. Internal coherence

Reading each updated file end-to-end on the EC-log thread:

- `team/04_ec_log_proof.md` — headline (line 17), edit note (21–31),
  full proof §2 with the new verification in §2.5 (101–122), $n_0 = 3$
  rationale in §2.6 (128), §3.1 constants discussion (147 — explicit
  "$C \to 4^+$ is the limit; $C = 6$ chosen so binding ineq gives $n \ge 3$"),
  table §3.2 with both $C=5$ and $C=6$ columns (153–168), §5 sanity
  ledger row "EC-log promises decomposition? no ($6\log_2 4 = 12 > 2$)"
  at line 261. **Internally consistent throughout.**

- `paper/draft_v1.md` — abstract (27–29), §1.2 Theorem 1 (96–103),
  §3.4 union bound and arithmetic verification (374–390), §3.5
  conclusion (394), §10 restatement (1227). **All five sites quote
  $\lambda \ge 6 \log_2 n$ and $n \ge 3$ consistently.**

- `paper/findings.md` — Theorem 1 (22–24, with edit note 26–32),
  method paragraph (37–44). **Coherent.**

- `paper/outline.md` — Theorem A (34–40). **Coherent.**

- `attack_plan.md` — single EC-log mention at line 44 fully updated.
  The rest of the file's references to EC-log (e.g. lines 30, 38, 51,
  62, 83, 85, 113, 117, 118, 142, 144, 151, 155) are name-only and
  unaffected by the constant. **Coherent.**

- `team/13_publishability_decision.md` — §1 (line 26) and Route C
  bundle (lines 95–96) updated. **Coherent.**

- `team/05_audit.md` — N1 retraction note (3844–3854), §A.14.3
  verdict updated (3951–3956), cross-reference table flagged
  (3967), final summary parenthetical (4137). **Coherent.**

---

## 6. Audit file integrity

Diff of `team/05_audit.md` shows exactly four edit hunks:
1. Insertion of the "Audit-stale note (2026-05-18)" block at lines
   3844–3854, immediately after N1's original "OK" verdict.
2. Replacement of the original "§A.14.3 verdict: CLEAN. All five
   numerical claims (N1–N5) match..." (3 lines) with "§A.14.3
   verdict: CLEAN as of the audit date, **partially retracted
   2026-05-18** for N1..." (6 lines) at 3951–3956.
3. One-line update to the cross-reference table row for `team/04_*`
   at line 3967 (verdict column now reads
   "OK at audit date; AUDIT-STALE 2026-05-18 — ...").
4. Inline parenthetical added to summary §A.14.7 numerical-claims
   bullet at line 4137.

**N2 (11 869 empirical instances), N3 (6 canonical $(1,0)$-near-split
exceptions), N4 (BJG–Yeo 2020 four compositions), N5 (bridge cardinality
Lemma 5.2) — all four verdicts are UNTOUCHED.** Likewise A.5, A.6,
A.10, A.11, A.12, A.13 and the other forensic appendices are not
modified. The mathematician scoped the audit edit minimally to N1
exactly as instructed.

---

## 7. Code drift

`git status` confirms only seven files modified in the subfolder, all
of them `.md`:

```
modified: problems/.../attack_plan.md
modified: problems/.../paper/draft_v1.md
modified: problems/.../paper/findings.md
modified: problems/.../paper/outline.md
modified: problems/.../team/04_ec_log_proof.md
modified: problems/.../team/05_audit.md
modified: problems/.../team/13_publishability_decision.md
```

The `code/` directory is untouched. A keyword grep over `code/` for
EC-log, `C = 5`, `C = 6`, $n_0$, `log_2`, etc. finds **only**
unrelated identifiers (a logging variable `log: V6Log` in
`run_phase4_vehicle6.py`; a component-size variable `n_0` in
`generators/ols.py:240`). **No code constants were ever tied to the
EC-log threshold; no code drift.** ✓

---

## 8. Anything the mathematician missed

Substantively, no. Cosmetically, one item:

- **Slack-figure off-by-one at $n = 10$** in `paper/findings.md:43`
  and `paper/draft_v1.md:399` — both read "$C = 6$ has approximately
  4–17 units of slack in the $n \in [10, 1000]$ range," but the
  integer slack at $n = 10$ is $20 - 17 = 3$, not 4. The
  `team/04_ec_log_proof.md:168` description ("slack ... is $\ge 4$
  from $n = 20$ on") is internally accurate; the paper-level wording
  inherits a stale figure from the previous $C = 5$ draft. Suggested
  one-character fix: "4–17" → "3–17". Severity: cosmetic.

Procedurally, all the documented retraction trails are well-placed
(headline notes carry dated edit annotations, the audit cross-
references the corrected files), so any future reader will trace
the chain back to `CORRECTNESS_REVIEW_2026_05_18.md` §2.5 cleanly.

One observation worth flagging: the prose at
`team/04_ec_log_proof.md:147` says "$C = 5$ remains valid
asymptotically and is the smallest integer that survives the limit
$C \to 4^+$." This is true but slightly distracting in a paragraph
whose punch line is "we drop $C=5$ from the headline." A future
revision could shorten this to "any $C \in (4, \infty)$ works
asymptotically; we take $C = 6$ for full $n \ge 3$ coverage."
Severity: stylistic only.

---

## 9. Bottom line

The Option A fix landed cleanly on the proof content. The one
substantive defect identified in `CORRECTNESS_REVIEW_2026_05_18.md`
§2.5 — that $5\log_2 n > 4\log_2 n + 3$ requires $n \ge 9$, not
$n \ge 4$ — is now resolved by the $C = 6$, $n_0 = 3$ choice, which
gives $n > 2\sqrt 2$, i.e. $n \ge 3$. Spot-check at $n = 3$:
$\mathbb{E}[N] \le 0.633 < 1$. All seven claimed files updated; no
old-constant regression; audit file scoped minimally to N1; code
directory untouched. Single cosmetic slack-figure off-by-one
flagged for an editorial pass.

**Recommendation:** accept the fix. Optional one-character cleanup:
`paper/findings.md:43` and `paper/draft_v1.md:399`, "4–17" → "3–17".
