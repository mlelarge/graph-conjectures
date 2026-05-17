# Bundle notes — cross-cutting submission strategy

## Bundle composition

| Paper | Title | Pages | Primary target | Fallback |
|---|---|---:|---|---|
| D8 | An algebraic explanation for the degree threshold $9/8$ in Fox–Pach–Suk's bound towards Albertson's conjecture | 7 | *Discrete Mathematics* (Note) | EJC |
| D15 | List-coloring Albertson up to chromatic number $18$ | 9 | *European J. Combin.* | EJC, *Discrete Math* |
| D16 | A bisection-width Crossing Lemma for regular spectral expanders, with an Albertson corollary | 9 | *Journal of Graph Theory* | *Combinatorica*, EJC |

Total: 25 pages of LaTeX, three independent theorems, **none closing the Cranston residual at $t \in \{25, 26\}$.**

## Author-list strategy

Each `.tex` currently has `(draft) Marc Lelarge \thanks{marc.lelarge@gmail.com}` as the placeholder author. Decision matrix:

| Paper | Solo Marc viable? | Natural co-author? |
|---|---|---|
| D8 | Yes — the paper is one elementary identity, no domain handover needed | Optional: FPS team as a "see also" rather than co-author |
| D15 | Yes — the paper is an assembly, no list-coloring novelty | Consider: a list-coloring specialist for credibility on §5 conditional theorem |
| D16 | Yes — but spectral content benefits from a spectral-graph-theory co-author | Consider: someone with PST/Alon background |

**Recommendation:** post all three solo as preprints under Marc; offer co-authorship to journal-quality reviewers post-feedback if their input merits it.

## Coordinated arXiv timing

**Strong recommendation: same-day burst.** The three papers cross-reference each other (D15 cites D8; D16 cites D8, D13, D15 in §7). Posting them on the same day, with each abstract noting "companion paper [N]" reads cleanly. Posting one at a time creates an awkward bibliography (forward-references to "in preparation" papers that have not yet appeared).

**Suggested sequence on the same day:**
1. Post D8 first (the obstruction theorem is the load-bearing piece; D15 and D16 cite it).
2. Post D15 second (the lift; cites D8 as a companion).
3. Post D16 third (the spectral packaging; cites D8, D15 as companions).

This sequence ensures the arXiv numbers can be filled into each paper's bibliography in the same day.

## Citation-of-companion-papers policy

The current `.tex` files use `\bibitem{D8}`, `\bibitem{D13}`, `\bibitem{D15}` as placeholder labels for the companion preprints. Before posting:

1. Replace all four (`D8`, `D13`, `D15`, plus the now-removed `D16`) with the arXiv numbers obtained on posting day.
2. Update the bibitem entries from `Companion note, 2026.` to `arXiv:YYMM.NNNNN, 2026.`
3. Update the cross-paper textual references that currently say "the companion note" to say "[N]" or "the companion preprint arXiv:YYMM.NNNNN" once available.

The `D13` reference in D16's §7 is to the internal R2c attack memo (not a paper). Decision: either (a) post D13 as a separate arXiv note (it's a clean negative result with a structural identification), or (b) remove the `D13` reference from D16 and replace it with a one-sentence summary of the failed approach.

**Recommendation:** option (b). The D13 memo is internal team material; a referee shouldn't be asked to follow an external reference for a negative result that's not load-bearing for the present paper.

## "Email first" matrix

| Person / team | Why | Which papers |
|---|---|---|
| **Fox, Pach, Suk** (arXiv:2510.05893 team) | D8 sharpens their result; courteous to give them a heads-up before posting. D16 also uses their framework as motivation. | D8 (strongly recommended), D16 (light mention) |
| **Cranston** (arXiv:2512.08020) | D15 §5 conditional theorem references his $t \le 24$ extension; D16 §5 mentions the residual. Courteous note worth sending. | D15, D16 |
| **Borodin, Kostochka, Woodall** | D15 §5 conditional theorem hinges on a list-edge-coloring constant from their 1997 paper. Worth a "is there a sharper unpublished version?" email before posting. | D15 |
| **Ackerman** | D15 lifts his ordinary Albertson at $t \le 18$ proof to lists. Not strictly needed but courteous. | D15 |

## What to NOT do (per PI directive 2026-05-17)

- Do NOT start a fourth paper. The autonomous research arc was stopped after D16; only the D16 §3 constant fix was permitted as a closeout edit.
- Do NOT attempt to close the Cranston residual at $t \in \{25, 26\}$ from this team's toolkit. Per the addendum: closure requires Role 9 SDP work (parked) or state-of-the-art exact crossing-number ILP at $n \sim 51$ (beyond SOTA).
- Do NOT rescue or revisit the `tighter_fps_RETRACTED` draft. It is preserved for traceability only.
- Do NOT revisit the D12 Ore-corner certification attempt. Best certified lower bound is $3825 < Z(26) = 5148$ with a gap of $1323$; the gap is structural and not closable by R2c or R3.6 (per D13 and D14).

## Project record for external description

> The Albertson team's 12-month output is a bundle of three theorem-grade papers on the structural neighbourhood of the conjecture: (i) sharpness of the constant $9/16$ in Fox–Pach–Suk's chromatic-index lemma (D8); (ii) a lift of the unconditional Albertson chain to list-coloring at chromatic numbers up to $18$, with a conditional extension to $24$ (D15); (iii) a bisection-width Crossing Lemma with explicit spectral coefficient, plus an Albertson corollary on regular spectral-expander critical graphs (D16). None of the three closes the Cranston residual at $t \in \{25, 26\}$; closure is beyond the team's accessible toolkit and is recorded as parked work for a future team or a different mathematical approach.

## Next decision points (in order)

1. **Author lists for each paper** (Marc's call; affects all three packets above).
2. **Coordinated posting date** (set a single arXiv timestamp).
3. **Replace placeholder bibitem labels with arXiv numbers** (a 10-minute pass once #2 is decided).
4. **Send "email first" notes per the matrix above** (a few days before #2).
5. **Submit each paper to its primary journal target** (after #2).
