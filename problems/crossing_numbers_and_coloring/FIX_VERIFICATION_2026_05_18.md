# Fix verification (2026-05-18)

## Verdict

All four targeted fixes from `CORRECTNESS_REVIEW_2026_05_18.md` (action items
1, 2, 3) have been applied correctly and to the intended files only. The D4
README's false `(25, 48)` paragraph is replaced with the correct empty-family
statement plus the `|V| \equiv 1 \pmod{k-1}` derivation; D5 `REPORT.md` carries
an unambiguous WITHDRAWN/SUPERSEDED banner pointing to D8 with the body
preserved verbatim; D15 and D18 READMEs both replace their stale "ready"
statuses with explicit WITHDRAWN notes citing the Voigt $t=5$ counterexample
and pointing to the corresponding `.tex` banners. `git status` confirms only
the four README/REPORT files were touched (no `.tex` / `.pdf` collateral
damage), and a project-wide grep for "ready for submission" / "ready for
internal review" returns no live hits outside the audit report itself.
Action item 4 (D3 §2 and §7 retraction) and items 5–6 (FPS typo email; D16
notation nits) were not part of this fix batch and remain open.

## Per-fix checklist

### Fix 1 — D4 `(25, 48)` paragraph

File: `deliverables/D4_ore_26_51/README.md`, lines 220–236.

- **Empty-family statement present.** L222–224: "the $25$-Ore family at
  $(25, 48)$ is **empty**, not a singleton."
- **Ore-congruence derivation `|V(G)| ≡ 1 (mod k-1)` stated.** L225–227:
  "every $G \in \mathcal{O}_k$ has $|V(G)| \equiv 1 \pmod{k - 1}$ (induction
  on the DHGO composition tree, with base case $K_k$ at order
  $k \equiv 1 \pmod{k - 1}$)."
- **$K_{25} * K_{25}$ has order 49 calculation given.** L229–230: "the
  composition $K_{25} * K_{25}$ has order $25 + 25 - 1 = 49$, not $48$."
- **`{25, 49, 73, …}` admissible list given.** L227–229: "For $k = 25$ this
  forces $|V| \in \{25, 49, 73, \dots\}$, so no $25$-Ore graph exists on
  $48$ vertices."
- **Surrounding (26,51) numerics intact.** Header L8 ("exactly 12"), table
  L130–141 (12 rows, all $|E| = 649$, $\delta = 25$), $F(51, 26) = 649$ sanity
  check at L154 — all unchanged from the audit-confirmed state. Per-graph
  SHA-256 prefixes and $\Delta = \max(24+a, 49-a)$ formula at L112–114 still
  consistent.
- **Cross-reference to docs/plan.md v4.** L230–232 explicitly cites
  `docs/plan.md`'s "Ore-congruence subsection" and `docs/review_v3.md`. I
  verified `docs/plan.md:402–419` independently states the same congruence
  and the same "$(25,48)$ family is empty" conclusion — no contradiction.

### Fix 2 — D5 REPORT.md withdrawal banner

File: `deliverables/D5_sympy_freedelta/REPORT.md`, lines 3–17.

- **Banner at top, before body.** L3: "**WITHDRAWN / SUPERSEDED
  (2026-05-18).**" — inserted between L1 (title) and L19 (original "Date.").
- **Identifies the false claim.** L4–6: "re-tuning $\delta$ from $9/8$ to
  $\delta_1 \approx 1.11491$ yields $F^\star \approx 0.5574 < 9/16$ — is
  **false**."
- **States the silent assumption.** L6–10 names "$f_{2b}^{\max}(\delta) =
  \delta/2$ at *every* $\delta$" and points at `case2b_check.py /
  case2b_check.log`. Threshold $-3 + \sqrt{17} \approx 1.12311$ given.
- **Redirects to D8.** L11–15: cites `deliverables/D8_paper/sharpness_9_8.tex`
  and the witness identity $f_{2b}(4/7,\delta) - 9/16 = 12(\delta-9/8)^2 /
  [7(4\delta-1)]$.
- **Body preservation explicit.** L15–17: "The body of this file is preserved
  unchanged below as an error-mode archive; do not cite its conclusions."
- **Body actually preserved.** `git diff` shows the banner is a pure
  insertion at the top (no body deletions). L19–163 reproduce verbatim the
  original report including the `F^* ≈ 0.557454` Headline table at L29 and
  the "Verdict" block at L33–38 — the banner now contextualises them rather
  than letting them mislead.

### Fix 3 — D15 README withdrawal

File: `deliverables/D15_list_albertson_paper/README.md`, lines 88–103.

- **Status section rewritten.** Old text "Draft, ready for internal review.
  […] no mathematical gap was identified" is gone (confirmed by `git diff`);
  L90 now reads "**WITHDRAWN (2026-05-17).** The main theorem stated above
  is **false** at $t = 5$".
- **Voigt $t=5$ counterexample stated.** L91–94: planar $G$ with
  $\chi_\ell(G) = 5$ (Thomassen 5-choosability) and $\operatorname{cr}(G) = 0
  < 1 = \operatorname{cr}(K_5)$.
- **Structural defect noted.** L95–99: "ACF / BT / Ackerman chain does not
  use $\chi \ge t$ only through $\delta \ge t - 1$" — Ackerman §3.1 uses
  $f_r(n)$; Krivelevich 1997 list analogue is weaker.
- **Points to .tex banner.** L99–101: "See the withdrawal banner at the top
  of `list_albertson_le_18.tex` (lines 33--60)".
- **Notes D18 bundling withdrawn.** L102–103.

### Fix 4 — D18 README withdrawal

File: `deliverables/D18_combined_observations/README.md`, lines 79–89.

- **Old text replaced.** Old "**Ready for submission**, pending author/journal
  decisions" is gone (confirmed by `git diff`).
- **Unambiguous WITHDRAWN line.** L81: "**WITHDRAWN (2026-05-17) — false
  observation at $t = 5$.**"
- **Identifies Observation 1 as the failed piece.** L82–85: Voigt $t=5$ planar
  graph with $\chi_\ell = 5$ and $\operatorname{cr} = 0$ refutes the
  list-Albertson claim.
- **D16 carve-out preserved.** L85–87: "D16's expander Crossing Lemma is
  unaffected and is shipped separately (see `../D17_submission_packets/`)."
- **Points to .tex banner.** L87–89: "See the withdrawal banner at the top of
  `two_structural_observations.tex` (lines 36--69)".

## Cross-check: READMEs vs. .tex banner states

| Artifact | .tex banner status | README status | Consistent? |
| --- | --- | --- | --- |
| D15 (`list_albertson_le_18.tex` L32–60) | WITHDRAWN — Voigt $t=5$, ACF/BT/Ackerman uses $f_r(n)$ | WITHDRAWN — same two reasons (`README.md:90–101`) | Yes |
| D18 (`two_structural_observations.tex` L35–68) | WITHDRAWN — Observation 1 false at $t=5$; Observation 2 salvageable, shipped as standalone D16 | WITHDRAWN — same; redirects to `D17_submission_packets/` (`README.md:81–89`) | Yes |
| D5 (no `.tex`; companion logs) | n/a (the report itself is the artifact) | WITHDRAWN/SUPERSEDED → D8 + `case2b_check.log` (`REPORT.md:3–17`) | Yes — consistent with `case2b_check.log` and D8 paper |
| D4 (no `.tex`; enumeration) | n/a | Empty-family statement at L222–236 matches `docs/plan.md:402–419` and `docs/review_v3.md` | Yes |

No new contradictions between any README and any `.tex` source.

## Collateral-damage check

`git status problems/crossing_numbers_and_coloring/`:

```
modified:   deliverables/D15_list_albertson_paper/README.md
modified:   deliverables/D18_combined_observations/README.md
modified:   deliverables/D4_ore_26_51/README.md
modified:   deliverables/D5_sympy_freedelta/REPORT.md
```

Exactly the four files the audit listed as needing edits. No `.tex`, `.pdf`,
`.py`, `.log`, or `docs/` file was modified. `git diff` on each confirms the
edits are localised to the Status section (D15, D18), the top banner (D5),
or the single Role-5-memo bullet at L222–236 (D4).

## Broader hygiene grep

```
grep -rni "ready for submission\|ready for internal review" \
  problems/crossing_numbers_and_coloring/deliverables/
```

Returns no matches. Project-wide grep finds only four quoted occurrences
inside `CORRECTNESS_REVIEW_2026_05_18.md` itself
(L84, L383, L730, L732) — all are the audit quoting the original stale
strings as evidence of the regression it was asking to fix, not live status
claims. No regression.

## Anything the mathematician missed

Of the six action items in the audit (`CORRECTNESS_REVIEW_2026_05_18.md`
L716–743), this batch addresses items 1–3 fully. The remaining items are out
of scope for the current fix-pass but are worth flagging so they are not
forgotten:

- **Action item 4 (MINOR).** `deliverables/D3_R5a_reconstruction.md` still
  carries §2's reverse-engineering "FPS chose $9/8$ to balance Case 1 and
  Case 2b" and §7's speculation "$\delta = 11/10$" — both should be marked
  superseded by D8's monotonicity-transition explanation at
  $\delta = -3 + \sqrt{17}$. Not a correctness regression, but a future
  reader of D3 may still be misled.
- **Action item 5 (NIT).** The FPS-side sign typo $(2 + 1/\eta) \to
  (2 - 1/\eta)$ on FPS arXiv:2510.05893v1 p. 10 has not been reported
  upstream. Doesn't affect any conclusion here.
- **Action item 6 (NIT).** D16 (`expander_crossing.tex`) notation harmonisation
  ($\lambda_2$ vs. $\max(|\lambda_2|, |\lambda_n|)$) and explicit closed-form
  $\theta$-bound in Corollary 5.1 are still pending. The paper is correct as
  is; these are referee-friendliness edits.
- **Minor verification artefact.** I did not re-run `case2b_check.py` to
  regenerate the log; the banner relies on the existing log being correct,
  which the original audit confirmed.

No regressions introduced. The four targeted fixes are complete and
consistent with the rest of the project's state.
