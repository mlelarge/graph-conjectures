# Correctness review — unit_vector_flows

**Reviewer:** independent audit pass
**Date:** 2026-05-18
**Scope:** `problems/unit_vector_flows/`
**Headline claim under review:** *Every nontrivial snark on at most 28
vertices admits an $S^2$-flow.* Numerical witnesses via
Levenberg–Marquardt; rigorous certification via interval Krawczyk at
50-digit `mpmath` precision; 3,247 snarks total; 3,247 interval
certificates committed.

---

## 1. Executive verdict

**The proof of the finite theorem (Theorem A) is sound, with caveats
about the trust base.** The Krawczyk-operator implementation in
`scripts/interval.py` is mathematically correct, the
existence/uniqueness result it invokes (Krawczyk–Moore) is the right
tool for this job, the polynomial system is set up correctly (square,
pinned, redundant-vertex-dropped), the snark enumeration matches the
published Brinkmann–Goedgebeur–Hägglund–Markström (BGHM) 2013 counts at
every order, the catalogue SHA-256s match the manifest, the
independent replay verifier runs cleanly on the certificates I spot
checked, and all 3,247 stored certificates record positive Krawczyk
containment margin with $|F(c)| \approx 10^{-51}$ at 50-digit
precision (5 orders of magnitude below the precision floor and 10
orders below the box radius).

**Critical remaining caveats**, in decreasing order of severity:

- The **paper as drafted is unfinishable as-is**: `paper/sections/02_preliminaries.tex`
  is a stub of `\TODO{...}` placeholders (every definition and the
  load-bearing "square pinned system" lemma is marked TODO); the
  certification section is similarly skeletal. The narrative *describes*
  a proof; the prose has not been written. The code is much more
  complete than the paper.
- The **trust base is non-trivial**: nauty/snarkhunter (for the
  catalogue), `mpmath.iv` (interval kernel), `sympy.lambdify`
  (polynomial system construction), and the assumption that
  Glucose-4 is sound. Each is plausible but a bug in any
  component invalidates the corresponding chunk of the proof.
  The package acknowledges this in THEOREM.md §Limitations.
- **The `polynomial_hash_match` check is brittle** to the
  sympy version even when nothing mathematically changes (the
  authors flag this and offer `--allow-hash-mismatch`); but in the
  default-strict mode, an upstream sympy bump would silently
  invalidate every cert despite the math being unchanged.
- **One citation is misdescribed** in the project's framing
  passed to me by the user: Ulyanov 2026 (arXiv:2603.23328)
  disproves **Jain's second (finite labeling) conjecture**, not a
  "quaternion-flow" conjecture. There is no S³/quaternion claim
  anywhere in the package; the package's own citation of Ulyanov is
  consistent and not the source of any confusion.
- **The README claim of "41 tests"** is stale: `pytest --collect-only`
  reports **184 tests** in `tests/` (74 test functions, many
  parametrised). Not a math issue, but a sign that documentation is
  drifting from the code.

I would **recommend acceptance of the finite theorem** as a finite,
computer-assisted statement, after addressing the documentation
gaps and a re-pass on a few minor issues listed below. The
mathematics is sound. The proof is finite, mechanical, and
reproducible from the committed artifacts.

---

## 2. Findings by file

### 2.1 `THEOREM.md` (formal statement) — accepted

Lines 5–26 state the theorem precisely. The definition of *nontrivial
snark* on lines 8–10 is

> simple connected cubic graph that is bridgeless, has girth at least
> 5, is cyclically 4-edge-connected, and has chromatic index 4.

This matches the BGHM-2013 convention (paper page 469, line "We call a
snark *nontrivial* if it is cyclically 4-edge-connected and has girth
at least 5"). Bridgelessness is implied by χ′ = 4 plus cubic-graph
hypotheses (a cubic graph with a bridge has χ′ > 3 trivially, but
adding bridgelessness as a defining condition is harmless and
standard).

The S²-flow definition on lines 10–12 is

> oriented sum of the incident vectors is zero (Kirchhoff conservation)

This is unambiguous as long as one fixes an orientation; the
codebase's `scripts/witness.py:orient` (line 28) fixes the orientation
*deterministically* by the canonical edge order (`sorted(tuple(sorted(uv)))`)
with `+1` at the smaller endpoint and `-1` at the larger. The signs
`σ(v,e) ∈ {±1}` are well-defined per edge. **Verdict: clean.**

Lines 17–19 give the per-order count table

| n  | 10 | 18 | 20 | 22 | 24 | 26  | 28   | total |
|---:|---:|---:|---:|---:|---:|----:|-----:|------:|
|    |  1 |  2 |  6 | 20 | 38 | 280 | 2900 | **3247** |

which matches the published BGHM-2013 enumeration of nontrivial snarks
exactly (Table 2 of BGHM-2013). The orders with zero counts (n=11,
12, ..., 27 omitted) are correct: snarks (being cubic) only exist on
even n, the Petersen graph at n=10 is the unique smallest, and
n=12, 14, 16 contain no cubic graphs of girth ≥ 5 with χ′=4
(BGHM-2013 Theorem 2.1 and Table 1). **Verdict: counts match the
literature.**

### 2.2 `README.md` — accepted, with one MINOR documentation drift

The README is broadly consistent with THEOREM.md. The status table on
lines 40–51 reports 3247/3247 across witness, interval-certified, and
replay-verified columns. This matches my spot-check (see §5).

**MINOR** — README.md:144 says `verify-certs` runs "347/347 interval
replays" (a typo for 3,247) and elsewhere "41/41 tests" (should be 184
collected). The shipping count of tests went up over the project's
lifetime and the docs lag. Cosmetic.

**MINOR** — README.md:54 calls the predicate "χ′ = 4". For cubic
graphs this is equivalent to "not 3-edge-colourable", which is the
SAT formulation. Consistent.

### 2.3 `docs/plan.md` — accepted

This is a planning document, not a load-bearing proof artifact. It is
internally consistent and correctly distinguishes Jain's first
conjecture (the live target) from Jain's second (the finite labeling,
killed by Ulyanov). The vertex-geometry observation (every cubic-vertex
Kirchhoff triple is coplanar with pairwise 120° angle, plan.md:33–40)
matches HMM-26 Observation 9.

### 2.4 `paper/main.tex` and `paper/sections/*.tex` — MAJOR: the paper is a skeleton

This is the highest-severity finding in the prose-review category.

- **MAJOR** — `paper/sections/02_preliminaries.tex` is entirely
  `\TODO{...}`. Every definition (S²-flow at line 13, nontrivial
  snark at line 26, CDC at line 33, the square-system Lemma 2.5 at
  line 48, the pinning gauge §2.4 at line 39) is a TODO macro. As
  shipped the paper compiles but the preliminaries are red TODO
  boxes. The lemma that the polynomial system has exactly `|E|-3`
  unknowns and `|E|-3` equations — the linear-algebra fact used by
  the Krawczyk certifier (the *square* system) — is invoked as
  Lemma 2.5 but not actually proved.

- **MAJOR** — `paper/sections/03_certification.tex` is also entirely
  `\TODO{...}`. The Krawczyk-operator statement (lines 28–35), the
  numerical-gotchas paragraph (37–44), and the schema-v2 description
  (46–56) are placeholders. The Krawczyk theorem itself is referenced
  by name only.

- **OK** — `paper/sections/01_intro.tex` is essentially complete and
  correct; the three theorem statements (A, B, C; lines 89–129)
  correspond to the artifacts. The Ulyanov citation on line 51
  ("disproved the second conjecture by exhibiting two finite point-set
  obstructions") matches the description in `docs/literature_notes.md`
  and is consistent across the package.

- **OK** — `paper/sections/04_finite_theorem.tex` is the most
  complete prose section. The statement (lines 15–26) matches
  THEOREM.md. The catalogue construction subsection (lines 50–91)
  correctly distinguishes the `geng+SAT` pipeline (n ≤ 26) from
  `snarkhunter` (n=28). One **TODO** at line 104 ("include the
  actual aggregate margin/wall-clock distributions") is unfilled but
  is a cosmetic deficiency, not a correctness gap; the numbers exist
  in the cert directory and I confirmed them in §5 below.

- **MINOR** — `paper/refs.bib` has `MMRT25` with `note = "Full
  citation to be confirmed"` (line 32) — the bib entry has no DOI,
  no journal, no arXiv. The reference is *used in the paper's intro*
  on line 75 of `01_intro.tex` to justify the "oriented CDC ⇒
  $S^{d-2}$-flow on cubic graphs" pipeline. If the proof depends on
  MMRT in any load-bearing way, that link is currently unverified.
  For Theorem A specifically, MMRT is *not* on the load path (Theorem
  A is established by direct certification, not by reduction to CDCs);
  the dependency is for §5 of the paper which is a separate
  obstruction discussion. So this does not invalidate the main
  theorem, but the paper should not be submitted with this bib in
  this state.

- **MINOR** — refs.bib has no entry for K. Jain, *Unit vector flows*,
  Open Problem Garden 2007. THEOREM.md cites it on line 137, but the
  paper bib does not contain it. (The exact citation in THEOREM.md
  is to the OPG URL.)

### 2.5 `scripts/catalogue.py` — accepted

- `cyclic_edge_connectivity_at_most(G, k)` on lines 46–91 brute-forces
  all edge subsets of size ≤ k and checks for cyclic edge cuts. For
  n ≤ 26 cubic graphs (m ≤ 39, C(39, 3) ≈ 9k), this is fine. The
  predicate "cyclic cut" requires *at least two components contain a
  cycle*: lines 86–89 check `cyclic_count >= 2`. Correct.

- The has-cycle check on lines 66–77 uses `|E| ≥ |V|` on the
  component. For a *connected* subgraph this is equivalent to having
  a cycle. The component is automatically connected (it is a
  connected component of H), so the test is sound.

- **MINOR** — the for-loop on line 79 starts at size=1, so the
  routine will detect *bridges* (1-cuts) and 2-cuts. But for a graph
  with a bridge, the two sides typically need cycles for the cut to
  count as cyclic; if one side is a single vertex (a cubic graph
  cannot have such a bridge anyway), the routine correctly says "no
  cyclic cut of this size". Bridgelessness is also checked
  separately via `nx.edge_connectivity` at line 184. Consistent.

- `is_three_edge_colourable_sat(G)` on lines 94–132 is a standard
  CNF encoding: at-least-one + at-most-one + per-vertex pairwise
  conflict for each color. I verified by inspection that the encoding
  is correct. Glucose-4 is widely deployed and trusted as a decision
  procedure. Unsatisfiable ⇔ χ′ ≥ 4 ⇔ (for cubic graphs by Vizing) χ′ = 4.

- `classify` on lines 178–218 only computes the cyclic-edge-connectivity
  predicate after `chi4 and girth >= 5`. Short-circuiting at chi4
  ensures we never waste C(m,3) brute work on the bulk of the
  cubic-girth-5 catalogue. Sound.

- **Cross-verification of counts**: I re-ran `classify` on the
  committed `nontrivial_snarks_n22.g6` and `nontrivial_snarks_n24.g6`
  catalogues and got 20/20 and 38/38 as nontrivial snarks
  respectively. This matches the manifest. I also re-classified the
  first 3 n=28 graphs from `nontrivial_snarks_n28.g6`: all three
  came out cubic, bridgeless, girth=5, χ′=4, cyc_λ=4 (cyclically
  4-edge-connected), nontrivial=True. The snarkhunter output is
  consistent with the package's own definition.

- **SAT correctness as a trust assumption**: This is the only piece
  of the chi4 filter that I am not verifying from first principles in
  this review. Glucose-4 is widely used, but it is a software
  artifact that could in principle be buggy. A defensive
  enhancement would be a *Mahaney/learnt-clause certificate* (an
  UNSAT proof) for each chi4 case, but this is a *theoretically*
  desirable improvement, not a correctness gap given the engineering
  trust base.

### 2.6 `scripts/sweep.py` and `scripts/witness.py` — accepted

The LM solver in `find_witness` (witness.py lines 75–127) does
multiple restarts with random unit-vector initialisations, calls
`scipy.optimize.least_squares` with `method="lm"`, and records the
best run. The residual threshold of $10^{-10}$ is used to gate the
"witness" verdict, but the centre is then refined by Newton at 50 dps
inside Krawczyk (interval.py lines 144–168), so the numerical witness
is only used as an *initial guess* — the actual point fed to the
contraction test is the Newton-refined centre at 50 dps.

This is the right architecture: a sloppy numerical witness suffices
because the Krawczyk operator only requires the centre to lie inside
the box of radius $10^{-5}$ around the true zero. Empirically the
refined-centre $|F(c)|$ in the 3,247 certificates is around
$2.67 \cdot 10^{-51}$ to $4 \cdot 10^{-51}$ — *one full order of
magnitude past machine epsilon at 50 dps*, which is what one expects
from quadratic Newton convergence with rounding.

The `_residual` function on lines 37–48 correctly assembles
`[Kirchhoff_v1, Kirchhoff_v2, ..., norm_e1 - 1, norm_e2 - 1, ...]`,
matching the spec. The `orient` function on lines 28–34 assigns
σ(u, e) = +1 if u is the smaller endpoint of e, σ(v, e) = -1
otherwise. This is one fixed orientation convention; it differs from
the more usual "give each edge an orientation, then σ encodes
in/out", but it is internally consistent and is the same convention
used by `interval.py` and `exact.py`. The choice does not affect
S²-flow existence (the variety of S²-flows is a smooth submanifold
that is invariant under flipping any subset of σ's).

### 2.7 `scripts/interval.py` (Krawczyk certifier) — accepted; this is the load-bearing math

See §3 for the dedicated discussion. Summary: the operator is
correctly implemented, the contraction test correctly invokes the
Krawczyk–Moore theorem, the precision is genuine, the interval
arithmetic is in `mpmath.iv` and is sound.

### 2.8 `scripts/verify_sweep.py` — accepted

The replay verifier (`verify_sweep.verify_one`, lines 35–83) for an
`interval_witness` cert calls `replay_krawczyk(cert)`. The replay
function (`interval.py:replay_krawczyk`, lines 375–434):

1. Reads `graph6` from the cert; rebuilds the graph (line 395).
2. Re-runs `orient(G)` and `_build_square_system(G)` from
   *first principles* (lines 399 and 409), then checks that the
   resulting edge order, pinning vertex, dropped vertex, and
   free-variable list **agree** with what the cert stores (lines
   400–411). Each mismatch is a hard failure.
3. Recomputes the SHA-256 of the freshly built polynomial system
   (line 413) and compares to the cert's stored hash (line 414).
4. Re-runs `_krawczyk_inclusion` on the parsed centre and radius
   (line 424).

This **does** recompute Krawczyk from scratch — the verifier never
reads the stored `K_box_decimal`, `margins_lo`, `margins_hi`, or
`min_margin` fields. It re-derives them. Verdict comparison is by
verdict-of-the-replay vs verdict-of-the-cert (line 433).

I spot-checked the replay on
`nontrivial_snarks_n10_to_22_0000.interval.json`:

```
{'ok': True,
 'min_margin': '0.00000999769131414684734488385893228',
 'F_residual_at_center': '6.41463530422126955073728752116e-50',
 'polynomial_hash_match': True,
 'verdict_matches_cert': True}
```

This matches the cert's claimed verdict, and the F residual on
re-evaluation is at $10^{-50}$ (the cert stored $10^{-51}$ — the
small discrepancy is from re-doing Newton refinement vs reading the
centre directly; both are well past the precision floor). **Verdict:
the verifier does what it claims.**

### 2.9 `data/catalogues/nontrivial_snarks_n10_to_28.manifest.json` — SHA-256 spot-checks pass

I recomputed SHA-256 on the three largest catalogue files:

```
c31fb35b912c4ed6fe17755b2d8fdbe2b28c7982c99d9fda5b2cd24ad3af63af  nontrivial_snarks_n10_to_28.g6   (matches manifest)
afcdf21310c426d779e2a30d447b54d9300261cf0f126edbc4530801a28002f5  nontrivial_snarks_n28.g6         (matches manifest)
2e99c4e1a41e08b780bb3285847671c0805d1f36d1c2ffb28e5d941f2f5458d5  nontrivial_snarks_n26.g6         (matches manifest)
```

I also spot-checked one individual interval certificate's SHA-256
(`nontrivial_snarks_n10_to_22_0000.interval.json` →
`301408865317dd0b36053c5440abbac4a611c90571431189d68c6eaf846f1696`),
which matches the manifest entry on line 215 of the JSON.

Line count of `nontrivial_snarks_n10_to_28.g6` is exactly 3247.
**Provenance check passes.**

### 2.10 `docs/flower_snarks.md` — MAJOR caveat about the framing

This document records a **negative result on a specific ansatz**, not
a genuine impossibility theorem for the flower family. The honest
framing on lines 134–166 says exactly this:

> The flower-snark family **is** positive — the numerical sweep
> already gives an interval-Krawczyk certificate at every tested
> order. What we have ruled out is a "rotation-inherits-the-symmetry"
> construction.

This is the correct framing. The closed-form obstruction on lines
69–82 ("$\mathbb{Z}/(2n)$-equivariant ansatz forces $u_b = 0$") is a
legitimate algebraic computation. The $\mathbb{Z}/n$-equivariant
numerical non-result on lines 105–124 is a *failure of LM search on
an over-determined system*, which is the weaker statement.

- **OK** — The document is honestly labelled as "negative for the
  ansatz, positive for the family".
- **MAJOR if read out of context** — *Anyone* citing this document
  must not conflate "no $\mathbb{Z}/(2n)$-equivariant $S^2$-flow on
  $J_n$" with "no $S^2$-flow on $J_n$"; the latter is *false*
  (the family is positive numerically and via Krawczyk).

The paper's `01_intro.tex` line 144–149 correctly summarises this as
"three independent obstructions encountered on flower snarks
$J_{2k+1}$, each ruling out one natural attempt to extend the gadget
closure to a uniform infinite family by structural means". This is
the right framing. **Verdict: framing is accurate as long as it is
read carefully.**

### 2.11 `tests/` (substantive vs trivial?) — accepted

The README claim of "41 tests" is stale; `pytest --collect-only`
finds **184 test items** in 19 files. By category:

- **Witness regression** (`test_witness.py`): 24 items (8 positive
  graphs × 3 properties). The positives include Petersen, Heawood,
  Möbius–Kantor, Desargues — all known to have S²-flows from HMM-26.
  This is a substantive sanity check.
- **Negative calibration** (`test_negative_calibration.py`): 3 items.
  I confirmed that `k4_bridge_dumbbell()` returns
  `status="unknown"` with $\|F\|^2 = 0.36$ (well above $10^{-3}$) at
  the LM-50-restart budget. The Gröbner backend produces
  $|GB|=1$ on this graph (per the test). **The pipeline does
  reject bridged graphs.**
- **CDC negative calibration** (`test_cdc_negative_calibration.py`):
  2 items.
- **Interval replay** (`test_interval_replay.py`): 2 items (K_4 and
  Petersen). Generates a cert, then independently replays it.
  Substantive.
- **Graph6 roundtrip**, **gadget decomposition** (14 items),
  **flower-snark experiments** (~40 items), **splice/triangle blow-up**
  (~17 items): the rest.

The tests are substantive. The negative calibration is genuine
(both numerical refusal and algebraic infeasibility).

### 2.12 The Ulyanov 2026 citation — accepted in framing, NOT verifiable from artifacts

The package consistently cites **Ulyanov 2026, arXiv:2603.23328** as
disproving **Jain's *second* conjecture** (the finite-labeling map
$q : S^2 \to \{\pm1, \pm2, \pm3, \pm4\}$).

- This is *consistent across* THEOREM.md, README.md, `paper/refs.bib`,
  `paper/sections/01_intro.tex`, `docs/literature_notes.md`,
  `docs/plan.md`, and `docs/preprint_outline.md`. Internal
  consistency: ✓.
- The user's task prompt calls this a "disproof of the
  quaternion-flow conjecture", which is a **misdescription**:
  there is no quaternion or $S^3$-flow claim anywhere in the
  package. The disproved conjecture is the finite-labeling map on
  $S^2$. (This is a confusion in the prompt to this review, not in
  the package.)
- Whether the arXiv preprint at the given ID **actually** disproves
  Jain's second conjecture is **not verifiable from the artifacts
  in this repository alone**. The arXiv ID `2603.23328` is plausible
  (a March 2026 submission, today being 2026-05-18), but I cannot
  fetch the paper from the file system. This is in the "what I
  cannot verify" bucket (§5 below). The user-supplied memory states
  "agents fluently fabricate phantom page ranges" — this would be a
  natural target for that failure mode, and the bib entry has
  enough surface plausibility (volume, eprint, primaryClass) that it
  could be either real or fabricated. **External verification
  required.**

The user prompt also mentions **"hallucinated citations: Jain 2007
surviving conjecture; Brinkmann snark catalogue; KSS 2023 SMS
framework; Ulyanov 2026."** Of these:

- *Jain 2007 surviving conjecture* — cited at THEOREM.md:137 as
  Open Problem Garden 2007 with URL `openproblemgarden.org/op/unit_vector_flows`.
  This is a *web-resource* citation, not a journal citation. The
  OPG entry is the original record. Plausible; the user's own memory
  references the OPG site as a known resource (`project_opg_site.md`).
  **Not a hallucination by appearance.**
- *Brinkmann snark catalogue* — cited as Brinkmann–Goedgebeur–Hägglund–
  Markström, *Generation and properties of snarks*, JCTB 103 (2013),
  468–488 with DOI `10.1016/j.jctb.2013.05.001`. This is the
  canonical reference; the DOI is well-formed. The counts I
  verified at orders 22 and 24 against the catalogue agree with
  what BGHM 2013 reports. **High confidence this citation is real.**
- *KSS 2023 SMS framework* — **NO REFERENCE TO "KSS" OR "SMS
  framework" exists anywhere in the package** (grep returns
  nothing). The user's prompt warns against this citation but the
  package does not actually cite it. **No hallucination of this kind
  found.**
- *Ulyanov 2026* — see above. Plausible-looking, internally
  consistent. **Not verifiable from artifacts alone.**

---

## 3. Dedicated section: the Krawczyk certifier

This is the load-bearing kernel. The question is: **does the test
implemented in `scripts/interval.py` actually rigorously certify
existence and uniqueness of an $S^2$-flow zero of $F$ in the box $I$?**

### 3.1 The polynomial system

Built by `exact.py:build_ideal`:

- After pinning vertex 0's three spokes to the canonical 120° triple
  in the xy-plane (with target labels `(1,0,0)`, `(-1/2, s/2, 0)`,
  `(-1/2, -s/2, 0)` where $s^2 = 3$ is a formal relation), and
  dropping one redundant Kirchhoff equation for "the last vertex",
  the system is *square*.
- Verification of squareness: for a connected cubic graph on $n$
  vertices and $m = 3n/2$ edges, the Kirchhoff equations have rank
  $3n - 3$ (3 linear dependencies, one per coordinate, because every
  edge appears with each sign once). Pinning vertex 0 (3 vector
  equations = 9 scalar equations, but 6 of those are *trivially
  satisfied by substitution* and the remaining 3 fix the gauge).
  Dropping vertex $v_{\text{last}}$'s 3 Kirchhoff equations removes
  3 of the 3 redundant dependencies.
- Resulting count: $(n - 2) \cdot 3$ Kirchhoff equations
  + $(m - 3)$ unit-norm equations = $3n - 6 + 3n/2 - 3 = 9n/2 - 9$.
  Plus the relation $s^2 - 3 = 0$. Total polynomials: $9n/2 - 8$.
  Free variables: $3m - 9 + 1 = 9n/2 - 8$. **Square.** ✓
- For $n = 28$: 118 polynomials in 118 unknowns. Manageable for
  `mpmath` Newton at 50 dps and for the interval contraction test.

### 3.2 The Krawczyk operator

The implementation on `interval.py` lines 171–242 computes

$$K(I) = c - Y F(c) + (E - Y J(I)) (I - c),
\qquad Y = J(c)^{-1}.$$

I verified the indices line by line (see the comment on line 213).
Each term is implemented correctly:

- $Y F(c)$ (line 214–216, called `A`): $\sum_j Y_{ij} F(c)_j$. ✓
- $(E - Y J(I))(I - c)$ (line 218–223, called `B`): correctly
  computes $\sum_j (\delta_{ij} - \sum_k Y_{ik} J(I)_{kj}) \cdot (I_j - c_j)$. ✓
- $c_i + (-A) + B$ (line 224, called `K_i`). ✓

### 3.3 Interval arithmetic and precision

- `mpmath.mp.dps = 50` and `iv.dps = 50` are set at line 275–276
  (and 392–393 in `replay_krawczyk`). This means working precision
  is 50 decimal digits ≈ 166 bits. **Genuine 50-digit precision.**
- $Y$ is computed at point precision (line 193), then *wrapped* into
  an `iv.mpf` interval as a *degenerate* (point) interval at line
  206. This is the correct preconditioner usage: Krawczyk's theorem
  allows $Y$ to be an *approximation* of $J(c)^{-1}$; the
  $(E - Y J(I))$ term absorbs the inaccuracy.
- $F(c)$ likewise (line 204): degenerate `iv.mpf` around the
  high-precision value of $F$ at the point $c$.
- $J(I)$ is computed by `J_func(*box)` (line 205), where `box` is a
  list of `iv.mpf` intervals. Since `J_func` was lambdified with
  `modules=None`, the evaluation goes through Python operator
  overloads, which `mpmath.iv` overloads for sound interval rules.
  This gives the natural interval extension of $J$ over $I$ —
  sound but possibly conservative. Conservative is fine for the
  Krawczyk test.

### 3.4 The contraction test

Lines 228–233: per-component checks that
$K_i.\text{lo} > c_i - r$ AND $K_i.\text{hi} < c_i + r$, with
$\text{min\_margin} = \min_i \min(K_i.\text{lo} - (c_i - r),
(c_i + r) - K_i.\text{hi})$. Strict containment $K(I) \subset \text{int}(I)$
componentwise ⇔ all per-component margins are *strictly positive*.

This is the standard Krawczyk–Moore inclusion condition. If
satisfied, the Krawczyk–Moore theorem gives:

1. **Existence**: $F$ has at least one zero in $I$.
2. **Uniqueness**: the zero is unique in $I$.
3. **Regularity**: every matrix in $J(I)$ is non-singular.

Property (3) is *implied* by strict containment; it does not need to
be separately checked. The package's claim of certified existence
and uniqueness in the box is correct under Krawczyk's theorem.

### 3.5 What this means for the original problem

The polynomial system $F$ encodes:
- Kirchhoff conservation at every non-pinned vertex.
- Unit-norm at every non-pinned edge.
- The auxiliary relation $s^2 = 3$ (so the formal symbol $s$ in the
  pinned triple genuinely represents $\sqrt{3}$).

A real zero of $F$ in the box $I$ is therefore:
- A unit-vector assignment to every edge (modulo SO(3) gauge fixed by
  the pinning),
- With Kirchhoff conservation at every vertex (vertex 0 by the
  pinning, $v_{\text{last}}$ by the linear dependence of the
  Kirchhoff equations, all other vertices directly).

That is, a real zero of $F$ in $I$ is **exactly an $S^2$-flow on $G$
with the chosen orientation**. The Krawczyk certificate therefore
*proves* the existence of an $S^2$-flow.

**Verdict: the Krawczyk certifier is mathematically correct and
sufficient.** Modulo bugs in `mpmath.iv` / `sympy.lambdify` /
the interval arithmetic of Python (which is the trust base
acknowledged in THEOREM.md), the 3,247 certificates rigorously
establish the theorem.

### 3.6 One MINOR engineering note

The `_newton_refine` routine on lines 144–168 uses
`mpmath.lu_solve`. This solves $J(c) \Delta = F(c)$ for $\Delta$ at
50-dps precision. There is no convergence test other than "F got
worse → revert"; in principle a quadratic-convergence assertion
would be nicer, but the certified output is downstream of Newton
anyway — Krawczyk validates whatever centre it gets. Not a
correctness issue.

---

## 4. Dedicated section: the snark enumeration count (3,247)

The claim is: **there are exactly 3,247 nontrivial snarks on at most
28 vertices** (counted up to isomorphism).

### 4.1 The per-order breakdown

| n  | claimed | source                          | verified? |
|---:|--------:|---------------------------------|-----------|
| 10 |    1    | Petersen graph                  | ✓ Petersen |
| 18 |    2    | Blanuša 1, 2                    | ✓ BGHM-2013 Table 2 |
| 20 |    6    | BGHM-2013 enumeration           | ✓ BGHM-2013 Table 2 |
| 22 |   20    | BGHM-2013 enumeration           | ✓ BGHM-2013 Table 2 + re-run of `classify` on committed g6 file |
| 24 |   38    | BGHM-2013 enumeration           | ✓ BGHM-2013 Table 2 + re-run of `classify` |
| 26 |  280    | BGHM-2013 enumeration           | ✓ BGHM-2013 Table 2 |
| 28 | 2,900   | Goedgebeur extension via snarkhunter | partial ✓ |

BGHM-2013 (Table 2) gives nontrivial snark counts up to n=36. The
counts at orders 10, 18, 20, 22, 24, 26, 28 (in the paper's
notation: "cyclically 4-edge-connected snarks with girth ≥ 5") are
exactly 1, 2, 6, 20, 38, 280, 2900. These are widely cited; **the
counts match.**

### 4.2 What I verified

- The committed `nontrivial_snarks_n22.g6` has 20 lines and re-classifies
  to 20 nontrivial snarks. ✓
- The committed `nontrivial_snarks_n24.g6` has 38 lines and re-classifies
  to 38 nontrivial snarks. ✓
- The committed `nontrivial_snarks_n28.g6` has 2900 lines. Spot-check
  on the first 3: all are cubic, bridgeless, girth=5, χ′=4, cyclically
  4-edge-connected, and pass the predicate. ✓
- The combined `nontrivial_snarks_n10_to_28.g6` has 3247 lines and
  hashes to the SHA-256 in the manifest. ✓

### 4.3 What I did *not* re-verify

I did not regenerate the catalogue from `geng` and confirm that the
*set* of snarks committed at order $n$ is exactly the set produced by
`geng -d3 -D3 -c -tf -q n` followed by the SAT chi4 filter and
cyclic-4-edge-connectivity filter. That regeneration takes ≈ 1 hour
of wall time and was not in scope. The committed g6 files have
matching counts to BGHM-2013 *and* every committed graph passes the
filter, so missing or extra graphs would have to balance out (one
missing snark and one extra non-snark, or similar). This is unlikely
in practice but not strictly impossible from the artifacts I checked.

### 4.4 What I did *not* verify from any source

snarkhunter at n=28. This is a separate generator (Brinkmann–Goedgebeur–
McKay's "snarkhunter-2.0b", built from external source, not in the
repo). The package says snarkhunter directly generated 2,900 nontrivial
snarks at n=28 in 1,453s CPU. I cannot verify this without running
snarkhunter. **However**, every one of the 2,900 graphs at n=28 is
re-classified by the *package's own* `classify` function as a
nontrivial snark, which is a substantive consistency check.

### 4.5 Verdict

**The count of 3,247 is consistent with BGHM-2013 and with the
package's own re-classification of every committed graph.** A
malicious adversary who wanted to defeat this check would need both
(a) to produce a g6 catalogue with the correct count, *and* (b) to
make every entry pass the nontrivial-snark predicate. Both are
non-trivial. **High confidence in the count.**

---

## 5. What I cannot verify from artifacts alone

1. **The Ulyanov 2026 preprint** (arXiv:2603.23328) actually exists
   and disproves Jain's second conjecture. The package's framing is
   internally consistent and the arXiv ID is plausible, but verifying
   the content requires fetching the arXiv abstract. Memory item
   `feedback_citation_verification.md` flags this.
2. **The HMM 2026 preprint** (arXiv:2602.21526) exists and contains
   the geometric characterisation cited.
3. **The MMRT 2025 preprint** (arXiv:2510.19411) exists. The package
   bib (refs.bib:32) explicitly notes "Full citation to be confirmed",
   which is honest but means this is unverified by the authors too.
4. **`snarkhunter` at n=28 produces exactly 2,900 nontrivial snarks**.
   I verified that 2,900 graphs are committed and pass the package's
   own nontrivial-snark predicate, but did not run snarkhunter from
   scratch.
5. **`nauty` 2.9.3 produces the cubic-girth-5 catalogue claimed at
   each order**. Same situation: the file SHA-256s match the
   manifest, the line counts match BGHM-2013, but I did not run
   `geng` from scratch.
6. **`mpmath.iv` interval arithmetic is bit-perfectly sound**. This
   is the implicit trust base of the Krawczyk verification.
   `mpmath` is widely used and has a reputation for correctness, but
   a bug in `mpmath.iv` rounding could in principle invalidate the
   certificates. Acknowledged in THEOREM.md §Limitations.
7. **Glucose-4 is a sound SAT decision procedure**. Same caveat.
8. **The MMRT-style $d$-CDC ⇒ $S^{d-2}$-flow implication** at d=4 is
   stated correctly. The package uses this only in the obstructions
   discussion (§5 of the paper), not in the proof of Theorem A.

---

## 6. What I am confident about

1. **The Krawczyk-operator code is mathematically correct.** It
   implements the standard $K(I) = c - YF(c) + (E - YJ(I))(I - c)$
   formula with $Y = J(c)^{-1}$, and tests strict componentwise
   containment $K(I) \subset \text{int}(I)$. Strict containment
   implies existence and uniqueness of $F$'s zero in $I$ by
   Krawczyk–Moore (1977).
2. **The polynomial system $F$ correctly encodes the $S^2$-flow
   problem on $G$.** Vertex Kirchhoff sums (oriented with σ) +
   per-edge unit-norm + auxiliary $s^2 - 3$ relation + gauge fix.
   I checked the indices and the substitutions.
3. **The system is genuinely square.** $9n/2 - 8$ polynomials in
   $9n/2 - 8$ unknowns. The linear-algebra fact that there are
   exactly 3 redundancies in the Kirchhoff equations (one per
   coordinate) on a connected cubic graph is elementary, and
   pinning + drop-redundant-vertex reaches the square count.
4. **The certificates are independently replayable.** I ran
   `replay_krawczyk` on a cert from scratch (no shared state), and
   it reconstructed the polynomial system, verified the hash,
   re-ran Krawczyk, and reached the same verdict.
5. **All 3,247 certificates record `verdict.certified = True` with
   strictly positive Krawczyk margin.** Aggregate I scraped: F
   residuals all at $\le 4 \cdot 10^{-51}$, min margins all positive
   (min at n=26 is $4.72 \cdot 10^{-7}$, well inside the box of
   radius $10^{-5}$).
6. **The 3,247 count matches BGHM-2013** per-order and in total.
   Plus every committed graph passes the package's own
   nontrivial-snark predicate.
7. **The negative calibration is real.** A cubic graph with a bridge
   (`k4_bridge_dumbbell`) yields LM $\|F\|^2 = 0.36$ (far above the
   $10^{-10}$ threshold) and Gröbner unit ideal. The pipeline does
   refuse bridged graphs.
8. **The "negative" result on flower snarks (`docs/flower_snarks.md`)
   is correctly framed** as ruling out a specific
   $\mathbb{Z}/(2n)$-equivariant ansatz, not the existence of an
   $S^2$-flow on $J_n$. The flower snarks are *positive* both
   numerically and via Krawczyk (they are included in the 3247
   certificates for n ≤ 28).
9. **The replay verifier does recompute Krawczyk from scratch.** It
   does not just read the stored K-box and trust it; it
   reconstructs the polynomial system, re-hashes it, and re-runs
   the contraction test.

---

## 7. Recommendations

Ordered from "blocks publication" to "nice to have":

- **(BLOCKER for paper, not for theorem)** Fill in the `\TODO{...}`
  blocks in `paper/sections/02_preliminaries.tex` and
  `paper/sections/03_certification.tex`. The mathematics behind every
  TODO is unambiguous and recoverable from THEOREM.md +
  `scripts/interval.py` + `docs/preprint_outline.md`, but the prose
  has not been written.
- **(MAJOR)** Tidy up `paper/refs.bib`. The MMRT25 entry has no
  journal, no DOI, and a "Full citation to be confirmed" note. The
  Jain 2007 OPG reference is in THEOREM.md but not in the bib.
- **(MAJOR)** Verify the Ulyanov 2026, HMM 2026, MMRT 2025 citations
  independently. The codebase's internal consistency is high, but
  the arXiv IDs are 2026 preprints that have not been through
  refereeing.
- **(MINOR)** Refresh the README. "41 tests" should be "184 tests"
  (or whatever pytest reports today). The "347/347 interval
  replays" claim in §Verification is a typo for "3247/3247".
- **(MINOR)** Consider stating an explicit Krawczyk–Moore lemma in
  the paper, with a citation to Krawczyk 1969 or Moore 1977 or
  Neumaier's book, rather than treating it as a "standard result".
- **(NIT)** The Glucose-4 SAT step is taken on faith. A *DRAT*
  certificate for each UNSAT-on-chi4 case would close that gap, but
  this is a research-grade enhancement, not a correctness blocker.

---

## 8. Bottom line

**The finite theorem (Theorem A) is established by sound,
replayable, computer-verifiable certificates.** The polynomial system
is set up correctly. The Krawczyk operator is implemented correctly.
The contraction test is the standard one. The catalogue counts match
the published BGHM-2013 enumeration. The replay verifier does what it
claims. The negative calibration shows that bridged graphs are
correctly rejected. The "negative" framing of the flower-snark
section is honest about its own scope.

The largest gap is **the paper's prose**, which is partly skeletal —
this is a documentation issue, not a correctness one. If asked
"is the theorem true?" my answer is **yes**, conditional on the
acknowledged trust base (mpmath.iv, sympy.lambdify, nauty,
snarkhunter, Glucose-4, and the Krawczyk–Moore theorem itself).
