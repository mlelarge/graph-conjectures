# Bundling recommendation (D17d): 3 papers vs 2 vs 1

## Step 1 — critical re-read of D15 and D16

### D15 (List-Albertson $t \le 18$)

**Abstract framing.** Already honest. Key signals:

- "We observe that the unconditional Albertson chain ... depends on its $\chi$-hypothesis only through the Dirac minimum-degree bound"
- "Assembling these observations gives the following theorem"
- Explicit "Honesty note" in §1: *"Theorem 1 is not so much a new theorem as the observation that an existing chain of theorems lifts."*

**Critique.**
- The "Honesty note" paragraph is unusual in submission papers. It pre-empts the referee objection but also signals self-doubt — if anything, it may *invite* the rejection.
- Claim "list-Albertson appears to have received little attention" is correctly hedged ("we are not aware of").
- The actual mathematics is ~2 pages: Lemma (list-Dirac) + lift of the ACF/BT/Ackerman MCE argument with $t-1$ as the input.
- 9-page paper from 2 pages of math is generous expansion (Preliminaries + step-by-step lift + boundary analysis).

**Verdict.** D15's contribution is honestly framed; the abstract does not overstate. The question is whether 9 pages of assembly justifies a stand-alone paper at any journal that asks for a substantive new result.

### D16 (Bisection-width Crossing Lemma + Albertson corollary)

**Abstract framing.** Slightly overstates in two places:

- "[T]he contribution here is the explicit packaging of the spectral parameter $\theta$ inside the Crossing-Lemma constant, which to our knowledge has not been written down in this form." — *hedged appropriately.*
- "The theorem is the first Crossing-Lemma improvement specifically tailored to graphs whose spectrum is well-separated." — **"first" is too strong for an abstract.** Recommend softening to "we are not aware of an earlier such inequality" to match the §1 hedge.

**Critique.**
- The actual mathematics is one line of substitution after PST and Alon are quoted.
- §3 (inline derivation of the bisection-cum-crossing constant $1/80$) is the most substantive part — three short paragraphs.
- §6 Albertson corollary is "essentially vacuous in the Dirac-floor regime" by the paper's own analysis: it fires only above $n \gtrsim 30 t$ under the conservative form, well above where Albertson lives.

**Verdict.** D16's contribution is one line of explicit packaging plus a self-contained re-derivation. The novelty claim survives a literature pass (Step 2), but the corollary is honestly weak.

## Step 2 — literature pass on D16's novelty claim

**Claim under test:** "no Crossing-Lemma inequality in the literature gives an explicit dependence on $\theta$".

Sources consulted:

| Source | Coverage | Spectral content? |
|---|---|---|
| Schaefer 2022 survey on crossing-number variants (electronic J. Combin. DS21v7) | comprehensive | **None.** 0 hits for "spectral", "eigenvalue", "Ramanujan", "expand" (in the relevant sense). Survey explicitly excludes "bisection width, cut width, etc." relationships from its scope |
| Shahrokhi–Sýkora–Székely–Vrťo survey (Springer LNCS 894, 1995) | comprehensive on lower-bound techniques | Lists three techniques (Crossing Lemma, Bisection Method, Embedding Method); no explicit spectral |
| Shahrokhi–Székely 1994 ("Canonical Concurrent Flows, Crossing Number and Graph Expansion") | crossing/expansion | Uses orbit sizes + average distance; **no spectral gap** |
| Kolman–Matoušek 2004 ("Crossing number, pair-crossing number, and expansion", JCTB 92) | crossing + flow-expansion | Upper bound $cr = O(\log^3 n \cdot \text{pcr})$ via flow expansion; **not a spectral lower bound** |
| Pach–Spencer–Tóth 2025 conjecture confirmation (arXiv:2502.02301) | crossing + monotone properties | Confirms a different PST conjecture (monotone edge density); **no spectral content** |
| Direct WebSearch for "spectral gap crossing number lower bound regular graph" | broad | No hits combining both |

**Verdict.** The novelty claim survives. However:

- "Survives a reasonable literature pass" $\ne$ "no one has ever written it down". The PST + Alon substitution is so direct that someone may have mentioned it in passing in a paper on expander drawings or VLSI layout that doesn't appear in the crossing-number canon.
- The honest framing is "we are not aware of an earlier such inequality", not "the first".

## Step 3 — bundling decision

### Options revisited

| Option | Description | Honest about scope? | Submission risk |
|---|---|---|---|
| **A: 3 papers** (current plan) | D8, D15, D16 each stand alone | Each individually OK; the bundle as a whole looks like padding | High — D15 and D16 each at risk of "is this a paper?" |
| **B: 2 papers** | D8 alone + (D15 + D16) combined as "Two structural observations" | More honest; combined paper has a unified narrative | Lower — fewer papers to defend individually |
| **C: 1 paper** | All three combined as "Three remarks on Albertson's conjecture" | Most honest; reads as a survey-style note | Medium — loses the focused-paper structure; harder to place at a top venue |
| **D: D8 only** | Drop D15 and D16; keep as arXiv-only notes | Most ruthless | Lowest — but wastes real-but-modest work |

### Recommended: **Option B (two papers)**

**Paper 1: D8** (R5a sharpness, 7 pages).
- Stand-alone. Has a genuinely new identity ($f_{2b}(4/7, \delta) - 9/16 = 12(\delta-9/8)^2/[7(4\delta-1)]$).
- Primary target: *Discrete Math* Note section.
- Email FPS first before posting.

**Paper 2: D15 + D16 combined** ("Two structural observations in the neighbourhood of Albertson's conjecture", ~15 pages).

Suggested abstract for the combined paper:

> We record two observations arising from an analysis of the structural slacks in the chain of partial results towards Albertson's conjecture. **First**, the Albertson--Cranston--Fox / Barát--Tóth / Ackerman chain establishing the conjecture unconditionally at chromatic number up to $t = 18$ depends on its $\chi$-hypothesis only through the Dirac minimum-degree bound, which lifts verbatim to list-coloring via the list versions of Dirac's and Brooks' theorems (Borodin 1977; Erdős--Rubin--Taylor 1979). Assembling these observations gives list-Albertson at $t \le 18$, strictly stronger than ordinary Albertson at the same range. **Second**, the Pach--Spencer--Tóth bisection-width Crossing Lemma, combined with Alon's spectral bisection lower bound, yields an explicit-$\theta$ Crossing Lemma for $d_0$-regular spectral $\theta$-expanders, $\operatorname{cr}(G) \ge (1-\theta)^2 d_0^2 n^2 / 1280 - d_0^2 n / 16$, with an Albertson-type corollary on regular spectral-expander critical graphs. Neither observation closes the Cranston residual at $t \in \{25, 26\}$; both are recorded as side-observations in the structural neighbourhood of the conjecture.

**Why combining is more honest than three separate papers:**
- Both D15 and D16 are "$\sim 2$ pages of math expanded to $\sim 9$ pages each". Combined they're ~12–15 pages of math with a unified "structural neighbourhood" narrative.
- Both have the same scope-honesty caveat: "does not address Cranston residual at $t \in \{25, 26\}$". Stating it once in a combined paper reads better than twice.
- Both are "we observe that an existing chain lifts / packages to one degree of generality higher". Same conceptual move; natural pair.

**Why not Option C (one paper):**
- D8's content is structurally distinct: a sharpness theorem with a new identity, not an "observation that an existing chain lifts".
- Combining D8 with D15/D16 would dilute D8's contribution and confuse the venue selection (D8 wants *DM Note*; D15/D16 want a regular-article venue).

**Why not Option D (D8 only):**
- D15 and D16 are real-but-modest. Discarding them throws away ~9 pages of useful exposition each. The combined Paper 2 is the right home for that work.

### Implementation cost for Option B

1. Combine D15 and D16 source files into a new directory (`D18_combined_observations/`) with a single .tex.
2. Update the joint abstract (above).
3. Merge the bibliographies (drop duplicates: `Ackerman`, `BK24`, `Cranston`, `Diestel`, `Dirac1952`, `FPS`).
4. Update the cross-references (D15's reference to D8 stays; D16's references to D13 and D15 become internal section references).
5. Recompile.
6. Update `D17_submission_packets/` to remove `paper_D15.md` and `paper_D16.md`, add `paper_D18.md` for the combined note.
7. Update `INTEGRATION.md`'s Decision 2026-05-17-3 to record the bundling change.

Estimated effort: 1–2 hours of editorial work, no new math.

## Decision required

The above is a recommendation, not a unilateral change. The decision is between:

- (A) **Ship 3 papers** as currently set up — accept the "is this a paper?" risk for D15 and D16 individually.
- (B) **Ship 2 papers** (D8 + combined D15+D16) — most honest framing per the contribution review; recommended.
- (C) Ship 1 combined paper — most honest but loses D8's focused structure.
- (D) Ship D8 only — most ruthless but wastes D15/D16's work.

If you say "do B", I'll execute the implementation steps above. If you say "stay with A" or "B" or other, I'll act accordingly.
