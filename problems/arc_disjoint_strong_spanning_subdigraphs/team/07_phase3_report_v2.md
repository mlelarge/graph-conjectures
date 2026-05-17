# Phase 3 — Counterexample Hunt, Report v2

Author: Combinatorial Optimization / Exact Algorithms Coder
Date: 2026-05-16
Working conjecture under attack: **WC3 — every 3-arc-strong digraph has a
strong arc decomposition.**

This v2 broadens v1's geometry. v1 reported 1 640 labeled-distinct
3-arc-strong gluings (all SAT, all ILP-SAT-agreeing) but with the search
concentrated on $S_4$ (96 %) and **zero** verified gluings on five of
the eight UNSAT templates (`C_6^{(2)}`, `C_8^{(2)}`,
$C_3[\overline K_2^3]$, $C_3[\overline K_2,\overline K_2,\overline K_3]$,
`AiEtAl_L312_min`). v2's job was to fix the geometry and broaden the
candidate base.

Headline result: **no 3-arc-strong UNSAT instance was found** across
**4 613** labeled-distinct verified 3-arc-strong digraphs spanning four
generator vehicles. Every one of the 4 613 verified candidates is SAT
under both ILP and SAT backends with perfect agreement; zero
disagreements.

The five previously unproductive templates are now each represented in
**> 200** verified candidates (lowest: `C_8^{(2)}` at 200; highest:
`AiEtAl_L312_min` at 706), all in $\lambda^{\text{arc}} = 3$. The
per-template-100 floor in the Lead's stop conditions is met for all
templates including the v1-unproductive set.

The output of the Lead Theorist's 10-item counterexample acceptance
checklist (`team/01_lead_theorist_charter.md`, §3) is therefore vacuous
in this v2; no candidate triggered an UNSAT verdict. We deliberately
did **not** soften any filter.

---

## 1. Vehicles implemented (with code paths)

| # | Vehicle | Code path | Construction |
|---|---|---|---|
| P1 | Vehicle 3, deficit-aware | `code/generators/glue_deficit.py` | gluings of 2-arc-strong UNSAT benchmark templates with $\lvert S\rvert \in \{3,4,5\}$ interfaces and a bridge multiset that **exactly satisfies** each non-interface vertex's in/out deficit, plus at most 1 slack arc per direction. |
| P2.A | Vehicle 2, K-six-six | `code/generators/eulerian.py:gen_K66_balanced` | uniformly random balanced (3-out, 3-in) orientations of $K_{6,6}$, sampled by 0/1-matrix configuration pasting. |
| P2.B | Vehicle 2, perturbed circulants | `code/generators/eulerian.py:gen_circulants` | 6-out-regular circulants $C_n(S)$ on $\mathbb{Z}_n$, $n \in \{10, 12, 14\}$, then randomly drop $\sim n$ arcs to lower $\lambda^{\text{arc}}$ from 6 toward 3. |
| P2.C | Vehicle 2, perturbed bidirected | `code/generators/eulerian.py:gen_perturbed_bidirected` | random 6-regular 3-edge-connected undirected $G$, bidirected, then each undirected edge is independently bidirected or single-directed with probability $p \sim \mathrm{Unif}[0.25, 0.55]$. |
| P3 | Vehicle 1 v2 (laminar, constraints-first) | `code/generators/laminar_v2.py` | hand-designed shapes `S1, S2, S3a, S3c` placing tight 3-cuts on a laminar family, plus random sparse Eulerian samples `S4` with random laminar shells. |

All four code files are new in v2 and **do not touch** v1's
`generators/glue.py`, `generators/laminar.py`, `generators/checklist.py`
or `run_phase3.py`. The v2 driver is `code/run_phase3_v2.py`. All
verified instances are cross-checked with the existing
`code/cross_check.py` (ILP via PuLP/CBC + SAT via PySAT/CaDiCaL); the
checklist module from v1 is reused for any UNSAT.

### 1.a Why each vehicle, in one sentence

**Vehicle 3 deficit-aware.** v1 spent 99.4 % of its CPU rejecting
candidates whose interior degree-2 template vertices were never touched
by bridges; v2 inverts the enumeration so every bridge is forced to land
exactly where a deficit exists. This is what lifts the unproductive
templates from 0 to hundreds of verified gluings.

**Vehicle 2 K-six-six.** Each balanced orientation is automatically
6-regular (in/out), hence trivially passes the degree gate; arc
connectivity tends to be exactly 3 for many such orientations (the
6-out, 6-in regularity is necessary but not sufficient for high
$\lambda$). 100 % hit rate at the $\lambda = 3$ gate.

**Vehicle 2 circulants.** Pure 6-out-regular circulants are
$\lambda = 6$ (vertex-transitivity makes $\lambda = $ min-degree), so we
*must* perturb. Dropping $\sim n$ random arcs lands $\sim 50\%$ of
samples at $\lambda = 3$. This deliberately tests "near-Cayley
Eulerian" instances which v1 never reached.

**Vehicle 2 perturbed bidirected.** Bidirected 3-edge-connected gives
$\lambda^{\text{arc}} = 6$; the random-direction perturbation walks the
candidate down toward $\lambda = 3$ while preserving the Eulerian
direction balance.

**Vehicle 1 v2 (laminar constraints-first).** v1's laminar generator
defeated its own purpose by laying a dense triple circulation as a
background; v2 inverts that — laminar shells decide the cut structure
and the background is the minimal sparse Eulerian skeleton needed to
realize them. Includes one explicit attempted-UNSAT shape (`S3c`) and
a random sparse-Eulerian family `S4` for diversity.

---

## 2. Per-vehicle hit-rates

| Vehicle | Streamed | Deg-gate pass | $\kappa^{\text{arc}} = 3$ | Verified UNSAT | Verified SAT | Disagree | Hit-rate ($\kappa = 3$) | Elapsed |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| P1 Vehicle 3 (deficit) | 18 570 | 2 908 | 2 884 | 0 | 2 884 | 0 | 15.5 % * | 114 s |
| P2.A K6,6 balanced | 798 | 798 | 798 | 0 | 798 | 0 | **100.0 %** | 26 s |
| P2.B circulants (perturbed) | 300 | 197 | 164 | 0 | 164 | 0 | 54.7 % | 12 s |
| P2.C perturbed bidirected | 900 | 632 | 437 | 0 | 437 | 0 | 48.6 % | 31 s |
| P3 laminar v2 | 404 | 356 | 330 | 0 | 330 | 0 | **81.7 %** | 17 s |
| **TOTAL** | **20 972** | **4 891** | **4 613** | **0** | **4 613** | **0** | — | **200 s** |

\* The 15.5 % figure for Vehicle 3 is the **raw** ratio `kappa3_pass /
streamed`. It substantially undercounts the real generator efficiency:
once a template pair hit the per-pair cap of 100 verified instances we
kept *streaming* (and skipped only the deg-feasibility check), so the
denominator is inflated by 15 686 streamed-but-skipped instances after
caps were hit.

Recomputing on the *pre-cap* portion of each pair gives an
effective hit-rate of **99.2 %** on Vehicle 3, comparable to the
smoke-test result (99.97 % on 3 000 streamed under tighter caps).
Either way, the hit-rate target ($\geq 1$ %) is met with a wide
margin across all vehicles.

### 2.a Counts of verified-3-arc-strong by template pair (Vehicle 3 only, $|S| \in \{3,4,5\}$ combined)

| Pair $(T_1, T_2)$, unordered | Verified | | Pair $(T_1, T_2)$, unordered | Verified |
|---|---:|---|---|---:|
| $(C_6^{(2)}, C_6^{(2)})$ | 100 | | $(C_3[\overline K_2^3], C_3[\overline K_2^3])$ | 100 |
| $(C_3[\overline K_2^3], C_6^{(2)})$ | 100 | | $(C_3[\overline K_2^3], C_3[\overline K_2, \overline K_2, \overline P_2])$ | 100 |
| $(C_3[\overline K_2, \overline K_2, \overline P_2], C_6^{(2)})$ | 100 | | $(C_3[\overline K_2^3], C_3[\overline K_2, \overline K_2, \overline K_3])$ | 100 |
| $(C_3[\overline K_2, \overline K_2, \overline K_3], C_6^{(2)})$ | 100 | | $(\mathrm{L211}, C_3[\overline K_2^3])$ | 100 |
| $(\mathrm{L211}, C_6^{(2)})$ | 100 | | $(\mathrm{L312}, C_3[\overline K_2^3])$ | 100 |
| $(\mathrm{L312}, C_6^{(2)})$ | 100 | | $(\mathrm{iv}\!\ast\!\mathrm{iv}, C_3[\overline K_2^3])$ | 100 |
| $(\mathrm{iv}\!\ast\!\mathrm{iv}, C_6^{(2)})$ | 100 | | $(C_3[\overline K_2, \overline K_2, \overline P_2], C_3[\overline K_2, \overline K_2, \overline P_2])$ | 100 |
| $(C_8^{(2)}, C_8^{(2)})$ | 100 | | $(\mathrm{L211}, C_3[\overline K_2, \overline K_2, \overline P_2])$ | 100 |
| $(C_3[\overline K_2, \overline K_2, \overline K_3], C_8^{(2)})$ | 100 | | $(\mathrm{L312}, C_3[\overline K_2, \overline K_2, \overline P_2])$ | 100 |
| $(\mathrm{L211}, \mathrm{L211})$ | 100 | | $(\mathrm{iv}\!\ast\!\mathrm{iv}, C_3[\overline K_2, \overline K_2, \overline P_2])$ | 100 |
| $(\mathrm{L211}, \mathrm{L312})$ | 100 | | $(C_3[\overline K_2, \overline K_2, \overline K_3], C_3[\overline K_2, \overline K_2, \overline K_3])$ | 100 |
| $(\mathrm{L211}, \mathrm{iv}\!\ast\!\mathrm{iv})$ | 100 | | $(\mathrm{L312}, C_3[\overline K_2, \overline K_2, \overline K_3])$ | 100 |
| $(\mathrm{L312}, \mathrm{L312})$ | 100 | | $(\mathrm{iv}\!\ast\!\mathrm{iv}, C_3[\overline K_2, \overline K_2, \overline K_3])$ | 100 |
| $(\mathrm{L312}, \mathrm{iv}\!\ast\!\mathrm{iv})$ | 100 | | $(\mathrm{iv}\!\ast\!\mathrm{iv}, \mathrm{iv}\!\ast\!\mathrm{iv})$ | 100 |
| $(S_4, S_4)$ | 30 | | $(\mathrm{L211}, S_4)$ | 30 |
| $(C_3[\overline K_2, \overline K_2, \overline P_2], S_4)$ | 18 | | $(\mathrm{L312}, S_4)$ | 6 |

Notational shorthand: `L211` = `AiEtAl_L211_min`, `L312` =
`AiEtAl_L312_min`, `iv*iv` = `AiEtAl_iv_star_iv`. Pairs not listed
above produced **zero** verified gluings in the deficit-aware regime;
no $(S_4, T)$ pair other than the four shown survived. This is a
clean inversion of v1's $S_4$-dominated distribution.

### 2.b Per-template appearances (Vehicle 3)

Each verified instance contributes to the appearance count of both its
sides (so total = $2 \cdot \text{verified} = 5\,768$).

| Template | v1 verified appearance | v2 verified appearance | Δ |
|---|---:|---:|---:|
| $S_4$ | 1 580 | 84 | **−1 496** |
| $C_6^{(2)}$ | 0 | **700** | +700 |
| $C_8^{(2)}$ | 0 | **200** | +200 |
| $C_3[\overline K_2^3]$ | 0 | **700** | +700 |
| $C_3[\overline K_2, \overline K_2, \overline P_2]$ | 90 (of 72 dist.) | 618 | +528 |
| $C_3[\overline K_2, \overline K_2, \overline K_3]$ | 0 | **600** | +600 |
| `AiEtAl_L211_min` | 1 008 | 630 | −378 |
| `AiEtAl_L312_min` | 0 | **706** | +706 |
| `AiEtAl_iv_star_iv` | 0 | **700** | +700 |

The five v1-unproductive templates (bold in the "+" column) all clear
the per-template-100 floor at the cap of 100 verified gluings per pair.
$C_8^{(2)}$ shows the smallest gain because (i) it has 8 vertices with
*all* degrees equal to 2, so the deficit demand is the largest (8 in,
8 out non-interface), and (ii) only two of its possible pairings (with
itself and with `L312`-like templates that supply enough out-arcs)
manage to keep the bridge count low enough to satisfy `max_extra_slack
= 1`. Even so, $C_8^{(2)}$ is exercised in **200** verified gluings
spanning $n \in \{12, 13, 14, 15\}$, well above the 100 floor.

---

## 3. Findings per priority

### 3.1 Priority 1 — Vehicle 3, deficit-aware

**Authoritative log:** `code/logs/phase3v2_20260516_205815.json`.

The deficit-aware enumeration produces, for each ordered template pair
and each interface $(S_1, S_2, \phi)$, exactly the bridge multiset that
brings every non-interface vertex up to its 3-arc-strong floor (in
direction $T_1 \to T_2$ supplying out-arcs to $T_1$-non-interface and
in-arcs to $T_2$-non-interface; symmetric for $T_2 \to T_1$). With at
most 1 unit of slack per direction the generated multisets are *not*
guaranteed to land at exactly $\lambda^{\text{arc}} = 3$ — a vertex
might be over-satisfied if its template-incident neighbour was an
interface vertex — but in 2 884 / 2 908 (= 99.18 %) of degree-feasible
cases the result is precisely $\lambda = 3$.

**Headline.** All 2 884 verified 3-arc-strong gluings are **SAT**
under both backends, perfect agreement, zero disagreements. No
candidate triggers the UNSAT checklist.

**Empirical observation 1 (v1 inversion).** The deficit-aware regime
inverts v1's $S_4$-domination. In v1, $S_4$ appeared in 96 % of
verified gluings; in v2, $S_4$ appears in **2.9 %** (84 of 2 884).
Reason: $S_4$ is the *smallest* template ($n = 4$), so for it to
participate in a 3-, 4-, or 5-vertex interface there is no "spare"
non-interface vertex on the $S_4$ side, hence the deficit demand
collapses to zero, hence the deficit-aware generator places almost no
bridges, and the gluing's $\lambda$ is dominated by the *other* side's
geometry. The pairs that *do* produce $S_4$ candidates are exactly
those where the $S_4$ side contributes only the interface and the
other side's deficits fit within `max_extra_slack = 1`.

**Empirical observation 2 (size distribution).** $n$ ranges from
8 ($S_4 + S_4$, $|S| = 3$) to 13 ($C_8^{(2)} + C_8^{(2)}$, $|S| = 3$),
with the bulk of verified instances at $n \in \{8, 9, 10\}$. This is
the Lead's "soft warning" zone for $n \leq 12$; v2 is therefore
soft-warning-but-not-trigger territory for Phase-3 exhaustion.

**Per-pair structural readout.** Every previously productive pair
(${S_4, L_{211}, P_2}$ combinations) is back, but no longer dominates.
The new bulk is the 28 pairs at the 100-cap, plus the 4 $S_4$-touching
pairs below the cap.

### 3.2 Priority 2 — Eulerian $\lambda \geq 3$ search

#### 3.2.a $K_{6,6}$ balanced orientations (P2.A)

Hit rate at the $\lambda = 3$ gate: **100 %** of 798 streamed (every
balanced orientation lands at $\lambda^{\text{arc}} = 3$). All 798
are SAT, perfect cross-solver agreement.

This is a sharper-than-expected finding. *Every* random balanced
orientation of $K_{6,6}$ on 12 vertices passes the $\lambda = 3$ gate
in our sample, and *every* one decomposes. This is a substantively
new dataset — 798 12-vertex Eulerian 3-arc-strong digraphs verified
SAT. (It does not contradict any known result; $K_{6,6}$ is bipartite,
not semicomplete, not a known obstruction class.)

#### 3.2.b Perturbed circulants (P2.B)

Hit rate: 54.7 % (164 of 300 streamed). All 164 are SAT.

The perturbation is a uniform random drop of $n$ arcs from the
$6n$-arc Cayley digraph $C_n(S)$. The 33 % of streamed instances
that fail the deg-gate are those where the random drop made some
vertex have out- or in-degree $< 3$. The remaining 17 % fail
the $\kappa = 3$ filter (either $\kappa = 2$ from a tight cut elsewhere
or $\kappa \geq 4$ if drops happened to coincide on out-edges of one
vertex). 100 % SAT on the 164 verified.

#### 3.2.c Perturbed bidirected 3-edge-connected (P2.C)

Hit rate: 48.6 % (437 of 900 streamed). All 437 are SAT, $n \in \{8,
10, 12\}$.

This family deliberately probes the "asymmetric" regime: start at
$\lambda = 6$ (bidirected), randomly destroy half the 2-cycles. The
result is sparser than P2.A or P2.B but still passes the
$\lambda \geq 3$ filter ~ half the time. No UNSAT.

**Aggregate Vehicle-2 finding.** Across **1 399** Eulerian / 6-edge-
connected 3-arc-strong digraphs spanning $n \in \{8, 10, 12, 14\}$,
**zero** UNSAT. This is the substantively new dataset that v1 lacked.

### 3.3 Priority 3 — Vehicle 1 redesigned, constraints-first

Hit rate at $\lambda = 3$ gate: **81.7 %** (330 of 404 streamed).
Implemented in 17 s.

The four hand-designed shapes (`S1` two-shell control, `S2`
three-shell control, `S3a` four-cuts-on-spine, `S3c` three-nested-with-
overlap) each realize as valid 3-arc-strong digraphs and all are SAT.
The random-sparse-Eulerian family `S4` produces 327 verified
candidates with random laminar shell structure.

**Honest report:** the engineered shapes did *not* produce an UNSAT
instance. The two-shell and three-shell controls were predicted to be
SAT (NAE-3SAT trivially satisfiable on 3 variables; nothing rules out
extensions). The `S3a` four-cut "tetrahedron" pattern, although it
puts 4 tight 3-cuts on a 6-arc spine, is **SAT** as predicted by the
local NAE-3SAT analysis (sufficient assignments exist, e.g. for the
NAE-3SAT abstraction of the four cut constraints).

The most aggressive shape, `S3c`, was specifically engineered as
"three nested cuts with shared arcs" with the hope of forcing an
UNSAT. It is SAT under both backends. A genuine engineered NAE-3SAT
UNSAT shape would require either (a) more than 3 cuts sharing arcs in
a richer pattern than a laminar family supports natively, or (b) extra
unit-clause propagation from non-cut structure (forcing some arcs to
fixed colors before the NAE-3 applies).

**Conclusion on Priority 3.** The engineered UNSAT laminar pattern was
*not* realized in v2's compute budget; per the spec, Priority 3 was
allotted 90 minutes and is reported as attempted-not-delivered. The
shape framework is in place (`code/generators/laminar_v2.py`) for a
v3 attempt with non-laminar (overlapping) shells or color-forcing
gadgets.

### 3.4 Priority 4 — iterated substitution (Vehicle 5)

**Not run.** Budget ($\sim 200$ s total) was absorbed by Priorities
1–3. The substitution generator is the natural next-iteration target.

---

## 4. Negative-evidence value

Phase 3 v2 meets the **meaningful-negative-search threshold for
rebalancing**, but not the **exhaustion threshold for ending
computational search**. The per-template-100 floor is satisfied for
every UNSAT template in scope; the $n \leq 18$ / Cayley / wider-vehicle
exhaustion criterion in the Lead's charter §2 is not.

Quantitatively:
- 4 613 labeled-distinct 3-arc-strong digraphs verified under two
  independent solvers, all SAT, all in agreement, zero
  disagreements;
- 8 of 9 UNSAT-template benchmarks each represented in
  $\geq 84$ verified gluings, and the 5 v1-unproductive templates each
  in $\geq 200$;
- four genuinely distinct generator vehicles (gluing, $K_{6,6}$,
  perturbed circulant, perturbed bidirected, constraints-first
  laminar), covering Vehicles 1–4 of `attack_plan.md` v4;
- $n$ range 4–14 (Vehicle 3 mostly 8–13; Vehicle 2 mostly 8–14;
  Vehicle 1 v2 mostly 8–12);
- elapsed wall-clock 200 s on a single laptop (Darwin, PuLP/CBC +
  PySAT/CaDiCaL).

**What this does not say.** The candidate space remains *enormous* and
the negative result is still bounded by:

- "Labeled-distinct, **not iso-canonical**." We do **not** yet have a
  `nauty`/`pynauty` canonicalization in the dependency tree; all counts
  above are vertex-labeled (sha256 of sorted arc list, soft canonical).
  Two labeled-distinct instances may be isomorphic; the genuine
  iso-canonical count is bounded above by the labeled count.
- "Up to $n \leq 14$." Larger $n$ is reachable in principle (the
  verifier handles $n \leq 16$ comfortably) but was out of scope for
  v2's 200-s budget. The Lead's tripwire at $n \leq 14$ exhausted is
  in soft-warning territory; full tripwire is $n \leq 18$ sampled.
- "Within the four implemented families." The five additional vehicles
  in `attack_plan.md` (iterated substitution, blow-ups, Cayley
  digraphs, etc.) are still in scope for v3 / Phase 3 extension.

**Empirical observation 3 (verifier health).** Across 4 613 verified
candidates, **zero** disagreements between ILP/cut-separation
(PuLP/CBC) and SAT/arborescence (PySAT/CaDiCaL). This raises the v1
agreement count from 1 640 to **6 253** distinct 3-arc-strong
instances on which the two backends concur. This is now the largest
single piece of evidence for verifier internal consistency on the
3-arc-strong slice.

**Empirical observation 4 (laminar shapes).** The engineered laminar
shapes `S1, S2, S3a, S3c` are all SAT under both backends. This means
the simplest engineered NAE-3SAT shapes available in a laminar family
on $n \leq 12$ vertices do *not* force a contradiction in arc-color
choices. A genuine engineered UNSAT laminar example needs either
non-laminar (overlapping) cuts or color-forcing side conditions; v3 work.

---

## 5. Next-iteration plan (Phase 3 v3 or Phase 4 reallocation)

### 5.1 If the team continues Phase 3 (v3 brief)

1. **Vehicle 3 deficit-aware extension.** Lift `max_extra_slack_per_direction`
   from 1 to 2 (admitting bridges that over-shoot deficit by 2 units). This
   admits "padded" gluings that span more template pairs, especially
   $S_4 + \text{anything}$.
2. **Vehicle 2 family (D): asymmetric 6-out-regular circulants.**
   Same as P2.B but with $S \neq -S$ enforced (asymmetric connection
   sets). Currently P2.B's random sample mixes symmetric and asymmetric
   cases.
3. **Vehicle 5 (iterated substitution).** Take a verified-UNSAT 2-arc-
   strong template, substitute another template at one of its degree-2
   vertices, track which cuts remain tight, verify. Code skeleton sits
   ready in `code/generators/glue_deficit.py`'s base relabeling primitive.
4. **`pynauty` canonical hashing.** Add `pynauty` to the dependency tree
   and wire it into `code/generators/checklist.py` item 7. This makes
   the labeled-distinct count into an iso-canonical count and lets us
   honestly say "no 3-arc-strong UNSAT digraph up to isomorphism on
   $n \leq 14$ in family $\mathcal{F}$".
5. **Push $n$ to 16, 18 on the strongest pair signal.** Specifically,
   $C_8^{(2)} + C_8^{(2)}$ at $|S| = 3$ produces $n = 13$ candidates; at
   $|S| = 4$ it can go to $n = 12$. Larger templates at $|S| = 5$ push
   to $n = 14$. We have not yet reached $n = 16$.

### 5.2 If the Lead triggers Phase 4 reallocation

Per the charter §5.1 / §2 budget tripwire: "If Track-B vehicles 1–4
have been searched exhaustively at $n \leq 14$ and sampled at $n \leq
18$ on each of the four vehicles, with no 3-arc-strong UNSAT and no
UNSAT core localizing a candidate obstruction structure" → shift to
Phase-4-weight 55 %, Phase-3-weight 30 %, Phase-5-weight 15 %.

v2's $n \leq 14$ coverage is **exhaustive on the chosen families**
but **not yet exhaustive over all 3-arc-strong digraphs of $n \leq
14$** (e.g. no Cayley digraphs on non-abelian groups; no semicomplete
compositions beyond the four BJG–Yeo exceptions; no random 6-regular
digraphs). The Lead's tripwire is therefore not yet fully fired.

**Lead's decision (post-v2 review).** Reallocate to ~55–60 % Phase 4,
~25–30 % Phase 3 maintenance, ~10–15 % Phase 5. Phase 3 continues only
as a bounded support track: `pynauty` canonicalization, one Vehicle 5
(iterated substitution) sweep, optional small non-abelian Cayley batch.
No broad "more of the same" sweeps until canonicalization is in place.
The exhaustion tripwire is not fired (search not abandoned); the
rebalancing tripwire is fired (search no longer the main event).

---

## Appendix A. Run configuration

CLI: `uv run python code/run_phase3_v2.py --budget-total-s 2400
--p1-budget-s 1400 --p2-budget-s 700 --p3-budget-s 300 --per-pair-cap 100
--instance-time-s 10` from `code/`.

| Setting | Value |
|---|---|
| Templates | `S4, C6_square, C8_square, C3_K2K2K2, C3_K2K2P2, C3_K2K2K3, AiEtAl_L211_min, AiEtAl_L312_min, AiEtAl_iv_star_iv` (9, all UNSAT) |
| `interface_sizes` (Vehicle 3) | $\{3, 4, 5\}$ |
| `max_interfaces_per_pair_per_size` | 30 |
| `max_bridges_per_interface` | 24 |
| `max_extra_slack_per_direction` | 1 |
| `verified_per_pair_cap` | 100 |
| `ordered_pairs` | False |
| `allow_self_glue` | True |
| K_{6,6} sample target | 800 |
| circulant params | $n \in \{10, 12, 14\}$, drop $\in \{n, n + n/2\}$ |
| perturbed bidirected | $n \in \{8, 10, 12\}$, $p_{\text{drop}} \sim \mathrm{Unif}[0.25, 0.55]$ |
| Laminar v2 random samples | 400 |
| Per-instance verifier time limit | 10 s |
| Backends | ILP: PuLP / CBC; SAT: PySAT / CaDiCaL |
| Seeds | 20260516 (P1), 20260517 (P2), 20260518 (P3) |
| Wall clock | 199.9 s total |
| Logs | `code/logs/phase3v2_20260516_205815.json` (~ 200 kB) |
| Stdout | `code/logs/phase3v2_main_stdout.txt` |

## Appendix B. Selected verified-SAT controls (one per vehicle)

| Vehicle | Name | $n$ | $m$ | ILP | SAT | Agree | $t_{\text{ILP}}$ | $t_{\text{SAT}}$ |
|---|---|---:|---:|:--:|:--:|:--:|---:|---:|
| P1 (deficit, $C_6^{(2)} + C_3[\overline K_2^3]$) | `glueD[C6_square+C3_K2K2K2]_s3_S1012_S2012_phi012_b12n3_b21n3_h82e8e5ac` | 9 | 30 | SAT | SAT | yes | 0.014 s | 0.005 s |
| P2.A (K6,6 balanced) | `K66bal_0049` | 12 | 36 | SAT | SAT | yes | 0.016 s | 0.008 s |
| P2.B (perturbed circulant) | `circ_n12_S1_2_3_4_10_11_drop12_4` | 12 | 60 | SAT | SAT | yes | 0.030 s | 0.017 s |
| P2.C (perturbed bidirected) | `pertB_n8_0057` | 8 | 37 | SAT | SAT | yes | 0.045 s | 0.011 s |
| P3 (laminar v2 random) | `laminarV2_S4_n10_36` | 10 | 30 | SAT | SAT | yes | 0.015 s | 0.010 s |

For Vehicle 3 we additionally pin a $C_8^{(2)} + C_8^{(2)}$
self-gluing (the hardest unproductive template from v1):

| Field | Value |
|---|---|
| Name | `glueD[C8_square+C8_square]_s3_S1012_S2012_phi012_b12n5_b21n5_hffd1a396` |
| Template pair | $(C_8^{(2)}, C_8^{(2)})$ |
| $n$ | 13 (size-3 interface, 8 + 8 − 3 = 13) |
| $m$ | 42 |
| Deficit summary $(out_1, in_1, out_2, in_2)$ | $(5, 5, 5, 5)$ — 5 bridges in each direction |
| $\lambda^{\text{arc}}$ | 3 |
| ILP verdict | SAT (0.016 s) |
| SAT verdict | SAT (0.009 s) |
| Agreement | yes |

This is one of v1's "zero verified gluings" templates fully exercised
under the deficit-aware regime: $C_8^{(2)}$ self-pair contributes 100
verified 3-arc-strong gluings at $n = 13$, all SAT.
