# D17 — Submission packets for the two-paper bundle (post-D18-retraction)

This directory contains submission-ready metadata for the **two** theorem-grade papers being shipped, after a substantial repair on 2026-05-17.

**Current shipping plan (after D18 was withdrawn):**

- **Paper 1 = D8** (R5a sharpness, 7 pp, stand-alone) → primary target *Discrete Math* Note.
- **Paper 2 = D16** (Bisection-width Crossing Lemma for regular spectral expanders, 10 pp, stand-alone) → primary target *Journal of Graph Theory*.

**Trajectory.** The original plan (`bundling_recommendation.md`, Option B) was D8 + a combined D15+D16 paper (D18). A senior referee pass on 2026-05-17 identified that D15's main theorem is **provably false at $t = 5$** (Voigt's planar non-4-choosable graph). D18 was therefore withdrawn (D15 too). D16's spectral content survived the audit cleanly — four fixable errors were identified and patched, and D16 is reinstated as Paper 2 of the bundle. See `paper_D16.md` for the patch summary.

**Status:** both papers compile cleanly, are theorem-grade, and are awaiting Marc's decisions on author lists, journal targets, and "email first" contacts before submission.

## Files in this packet

- `paper_D8.md` — submission packet for the R5a sharpness paper. **Active.**
- `paper_D16.md` — submission packet for the bisection-width Crossing Lemma paper. **Active (reinstated after D18 retraction with 4 patches).**
- `paper_D18.md` — **withdrawn** (combined paper containing the false Observation 1; preserved with banner).
- `paper_D15.md` — **withdrawn** (false main theorem; preserved with banner).
- `bundle_notes.md` — cross-cutting notes (author-list strategy, coordinated arXiv timing, citation-of-companion-papers policy, what to email FPS first). Note: written under earlier plans; the current 2-paper plan inherits the same author-list strategy and most of the "email first" matrix.
- `bundling_recommendation.md` — the original Option B decision document (now historical).

## Submission readiness check

| Paper | Title | Pages | Compile clean? | Self-cites cleaned? |
|---|---|---:|---|---|
| D8 | An algebraic explanation for the degree threshold $9/8$ in Fox–Pach–Suk's bound towards Albertson's conjecture | 7 | yes | yes |
| D16 | A bisection-width Crossing Lemma for regular spectral expanders, with an Albertson corollary | 10 | yes | yes (self-cite removed previously; D15 cross-cite was in D18 only, not D16) |

## What the project deliberately does NOT contain

- A closure of Albertson at $t \in \{25, 26\}$. This is the Cranston
  residual and is parked. Per the integration addendum of 2026-05-17,
  closure requires either Role 9 SDP work on $\operatorname{cr}(K_t)$
  (currently parked) or exact crossing-number ILP at $n \sim 51$
  (beyond current SOTA per Role 3's memo).
- A fourth theorem chase. The autonomous research arc was stopped on
  2026-05-17; the only mathematical revision was the D16 §3 PST
  constant fix (now downgraded to the inline-provable $1/1280$ form,
  with the sharper PST $1/640$ recorded as a remark).

## What still requires human-in-the-loop decisions

- **Author lists.** Each packet has a placeholder
  `(draft) Marc Lelarge` in the .tex; co-author additions are Marc's
  call.
- **Journal targets.** Each packet proposes a primary and a fallback
  target with reasons.
- **"Email first" contacts.** D8 in particular may benefit from a
  pre-submission heads-up to the Fox–Pach–Suk team, since it is a
  sharpness theorem on their result.
- **Coordinated arXiv posting.** The three papers cross-cite each
  other; posting them in a coordinated burst (same day, with
  matching arXiv companion-paper notes) reads cleaner than posting
  one at a time.
