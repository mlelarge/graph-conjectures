# Correctness review — earth_moon_problem, 2026-05-18

Independent audit of `problems/earth_moon_problem/` as of git HEAD
`204282a` (May 16, 2026). Reviewer: Claude Opus 4.7 (1M context),
operating from the artifacts only.

Scope: README, docs/plan.md, docs/phase6_discharge_attempt.md,
docs/upper_bound_notes.md, docs/literature_notes.md,
docs/phase4_results.md, docs/spike_sms_build.md, docs/paper_skeleton.md,
scripts/biplanar_check.py, scripts/cycle_blowup.py,
scripts/earthmoon_blowup.py, scripts/q0_profile_enum.py,
scripts/run_smsg.sh, data/c7_k4/.

## Executive verdict

The project is in a healthy state. The clean separation between
"empirically verified by SMS runs", "proved from primary citations", and
"open / next-session" is respected throughout. The Phase 4 computational
result (Theorem A in the manuscript skeleton) is solid; the Phase 6
isolated-low-vertex argument is honestly labelled as conditional on
**Step 4+** and an open **Q0 closure**, and these labels are accurate.

No claim that I checked is overstated. There are a handful of MINOR
infelicities (mostly notation collisions and one mildly misleading
README claim about what the C_7[K_4] run "rules out") and one MAJOR
limitation in the verifiability story: the negative SMS result on
C_7[K_4] is not, and from artifacts alone cannot be, independently
cross-checked. I did not find any bug in the discharging arithmetic; I
did find one structural place (Step 7.4 "Low-vertex quantized
attachment") whose claimed Gallai-rigidity argument needs more care
than the doc currently gives, and one notation reuse (`q`) that briefly
made the budget arithmetic in Step 5''' read as a typo.

The biggest substantive worry, and it is acknowledged in the doc, is
that the load-bearing UNSAT verdicts come from a single SAT framework
(SMS v1.0.0) which is *exactly* the same code that produced the
positive smoke and reproduced KSS's published candidate1. Any
"reproducibility-by-independent-tool" claim is not yet made and should
not be made until the SMS UNSAT cores are replayed elsewhere.

Bottom line for the reader of the paper skeleton:

* **Theorem A** (every cycle clique-blowup with `n ≤ 30, ω ≤ 8, χ ≥ 10`
  is non-biplanar): empirically established by SMS v1.0.0 UNSAT runs.
  The combinatorial graph theory (chi, omega, alpha, m, K_9-free) is
  proved, independently from the SMS run, in `cycle_blowup.py` and I
  independently re-verified it. The non-biplanar UNSAT verdicts depend
  entirely on trusting one SAT codebase. This is not a theorem; it is
  a computational result, and the manuscript skeleton labels it
  correctly as "computational" in §2 but as "Theorem A" in the same
  paragraph. Choose one.

* **Theorem B** (12-critical K_9-free biplanar implies `n ≥ 89`):
  Proved, modulo trust in the cited literature (KY 2014; KY 2018
  Brooks-type; GP 2022 Lemma 3.3). No proof gap.

* **Theorem C / Phase 6**: not a theorem; correctly framed as a
  conjecture and a plan. Two named obstacles (Step 4+ and Q0
  high-only closure) are not closed.

---

## Section 1 — README.md and docs/plan.md

**File: `README.md`.** Lightweight overview. Accurate.
- Line 16: "Headline candidate: C_7 ⊠ K_4 on 28 vertices (χ=10, ω=8,
  K_9-free)." Independently re-verified: `n=28, m=154, ω=8, α=3, χ=10`,
  and `K_9-free` follows from `ω=8`. The notation `C_7 ⊠ K_4` is the
  strong product. **MINOR**: in the rest of the project the same graph
  is called `C_7[K_4]` (lexicographic / clique-blowup notation). These
  two are isomorphic when the second factor is complete (verified by
  `networkx.is_isomorphic`), so the conflation is harmless, but the
  reader should be told once that `C_7[K_4] = C_7 ⊠ K_4` because the
  literature treats them as distinct constructions in general (the
  Cartesian product `C_7 □ K_4` would *not* give this graph).

**File: `docs/plan.md`.** Strategy doc; well-written. A few notes:
- Lines 24–29: KY arithmetic. I re-checked `F(12,78)=456, 6·78−12=456`
  (KY tight); `F(12,89)=521 < 522 = 6·89−12`. The claim that the
  inequalities are compatible only for `n ≥ 78` is correct.
- Line 71: `K_{6,9}, K_{5,12}` listed as not biplanar (negative
  regressions). The thickness of `K_{p,q}` is
  `⌈pq/(2(p+q−2))⌉` (Beineke–Harary–Moon 1964); `K_{6,9}`
  gives `⌈54/26⌉ = 3`, and `K_{5,12}` gives `⌈60/30⌉ = 2`. So
  **`K_{5,12}` is plausibly *biplanar*, not non-biplanar**. Worth
  rechecking the BHM 1964 paper before promoting this row of the
  regression table to production; the regression list is currently in
  the plan only and not yet wired into a test runner, but it would
  silently fail. **MAJOR**.
- Lines 137–146: the n ≥ 78 reduction is correct.
- Lines 187–200: the "Removed from earlier draft" block is excellent
  defensive engineering. Specifically the `K_{5,5}` correction: the
  original draft had `K_{5,5}` as a negative regression, but `K_{5,5}`
  has 25 edges on 10 vertices ≤ 6·10−12 = 48, and `K_{5,5}` is in fact
  biplanar (genus 1, easy direct construction). Catching this is the
  kind of thing that distinguishes honest research from rubber-stamping.

---

## Section 2 — scripts/biplanar_check.py and SMS wrapper

**File: `scripts/biplanar_check.py`.** Plain, well-commented, calls into
the vendored SMS v1.0.0 clone for biplanarity testing. The encoding
strategy: SMS represents the layer split as a directed graph; an edge
`{u,v}` of layer 1 is encoded as both `(u,v)` and `(v,u)`; an edge of
layer 2 is encoded as exactly one of the two directions. The
ThicknessTwoChecker propagator checks this representation against an
actual planarity oracle per layer. This is the textbook KSS 2023
encoding from §5.2; the project's literature notes quote the relevant
paragraphs primary-source.

What the script does:

- `parse_edges`, `join_kp_kq`, `chunk_overlap_graph`,
  `chunk_endpoint_overlap_graph`, `coupled_74_graph` construct edge
  sets in `[0..n)` for the canonical Phase 6 local subgraphs.
  `chunk_overlap_graph(t=6, a=5, s=3)` for instance has 14 vertices
  (K_6 + w + 5 outside) and the right edge count `21 + 6 + 30 + 3 = 60`.
  The 14-vertex variant is consistent with `--chunk-overlap 6,5,5`
  yielding the documented 56-edge `K_7 + bar K_5` graph.
- `add_fixed_edge_constraints` (lines 218–240) is the load-bearing
  piece. It (i) forces every desired edge to be present as an
  antiparallel arc pair *or* a single arc (here the script forces them
  all to be the antiparallel direction `(j,i)`, which says "edge in
  layer 1"... no, see CRITICAL below), (ii) forces every non-edge to
  be absent, (iii) sets `thickness2 = 5` so the layer-2 propagator
  fires every 5th node, and (iv) sets the `initial-partition` SMS flag
  so symmetry breaking respects the fixed graph's automorphism group.

**CRITICAL — re-check edge encoding.** The code does

```python
for i, j in sorted(edges):
    builder.append([builder.var_edge_dir(j, i)])
```

This is a *single* unit clause asserting `var_edge_dir(j,i)`. In KSS's
directed-graph layer split, an edge of `G_1` (layer 1, the maximal
planar layer) needs *both* `(i,j)` and `(j,i)` to be present, while an
edge of `G_2` (layer 2) needs *exactly one*. So `var_edge_dir(j,i)`
alone fixes the *underlying* edge to be present (since either layer
yields at least one of the two directed arcs) but leaves the *layer
assignment* free. That is what we want — we want SAT to assign edges
to layers freely. So the encoding is correct **provided** the SMS
propagator interprets "underlying-edge present" as "either
`var_edge_dir(i,j)` or `var_edge_dir(j,i)`". Cross-checked against
KSS's published encoding (`candidate1_calibration` reproduces the same
DIMACS modulo Patch C, per `spike_sms_build.md`) and the smoke test
result. Accept.

**MAJOR — silent-UNSAT risk.** The `initial-partition` flag is
critical: without it SMS may over-prune via permutations that change
the underlying graph, producing a spurious UNSAT. The script always
passes one (see `partition=[t, 1, s, a-s]` etc.). The comment at
biplanar_check.py:225–229 explicitly warns about this. Good.
The risk that remains is: if a caller adds new graph shapes and
forgets to pass `--partition`, the SMS run may falsely UNSAT.
`--edges` with no `--partition` defaults to `None`; this is a
foot-gun and should be either a hard error or a no-symmetry-breaking
default. **MINOR**.

**File: `scripts/cycle_blowup.py`.** Pure NetworkX graph theory; no
SAT. Computes `(n, m, omega, alpha, chi)` of `C_{2r+1}[K_{a_1}, ...]`
with a formula and cross-checks against networkx. I re-verified the
formula for `(4,4,4,4,4,4,4)`: `n=28, m=154, ω=8, α=3, χ=10`. The
chromatic-number formula uses the weighted-odd-cycle identity
`χ = max(max_i (a_i + a_{i+1}), ⌈Σa_i / r⌉)` — this is the
Stahl/Vince/Bondy result for fractional chromatic number of weighted
cycles, but specialised to integer chromatic number it is the
weighted-circular-chromatic-number bound, which **is tight for cycles
of odd length but I want to flag that the result is non-trivial**.

For the specific cases enumerated (n ≤ 30, ω ≤ 8, χ ≥ 10) the script
finds 4 canonical-form representatives. The published witness 10-colouring
in plan.md (lines 109–112) for `(4,4,4,4,4,4,4)` I checked by hand: no
monochromatic edges, max colour 10. So `χ ≤ 10`. The matching lower
bound `χ ≥ ⌈28/3⌉ = 10` comes from `α = 3`. Both bounds verified.

**File: `scripts/earthmoon_blowup.py`.** Thin wrapper that builds the
blowup graph and ships it through the SMS encoding. The partition
passed to SMS is "per-fibre", which is exactly the right automorphism
group quotient for a cycle clique-blowup (rotations of the cycle plus
in-fibre permutations). Matches KSS's hand-coded `candidate1` and
`candidate2` partitions per the SMS source. Accept.

**File: `scripts/q0_profile_enum.py`.** Necessary-condition enumerator
for the Q0 profile model from `phase6_discharge_attempt.md` §7. I ran
it: 49 partitions, 160 merge cases, 143 feasible. Matches the doc.
The internal arithmetic (degree balance, chunk demand `t(12-t-ε)`,
LOW_OUTSIDE=23, HIGH_OUTSIDE=54) lines up with §7.5. **MINOR**: the
"sharp necessary bound `sum ceil(h_i/t_i) ≤ 54`" packs all high
outside vertices into at most one chunk each, which is correct under
the Q0 exclusivity claim (7.3) — the proof of which is one paragraph
and looks right (a vertex adjacent to two cliques creates a common
neighbour for a cross-clique non-edge, contradicting Q0). I accept
7.3.

**File: `scripts/run_smsg.sh`.** Detached nohup wrapper with meta
capture. Records SMS commit hash and dirty status (and the v1.0.0 tag
is consistently `2d5a22a3...dirty` with the Patch A/C local
modifications, audited in `spike_sms_build.md`). Provenance is clean.

---

## Section 3 — docs/phase6_discharge_attempt.md (centerpiece)

This is the load-bearing 1153-line working file. I read every line.

### 3.1 Setup and Step 1 (lines 9–55) — correct

The working hypothesis is "G is 12-critical, K_9-free, biplanar, n ≥
89". The simple double-counting at lines 28–44 gives `ℓ ≥ 24` from the
biplanar edge cap and `h ≥ (9n−86)/11` from Brooks-type, yielding at
n=89 the tight regime `ℓ=24, h=65, m=522`. All arithmetic re-verified:
`130·89 − 22·522 = 86 = y_{12}`, Brooks-tight exactly.

### 3.2 Step 2 — Lemma 2.1 (lines 56–80) — correct

Gallai's theorem: in a k-critical graph, the subgraph induced by
degree-`(k-1)` vertices is a Gallai forest (every block is K_t or odd
cycle). Specialised to k=12: blocks of `G[L]` are K_t (t ≤ 12) or
C_{2r+1}. The K_9-free cap gives t ≤ 8. The local-degree cap from
δ(G)=11 gives `t ≤ 12` anyway. The conclusion `t ∈ {1,...,8}` ∪
{odd cycle} is correct.

### 3.3 Steps 3–4 (block accounting, discharging plan) — sound

The KY potential `ρ_{12} = 130n − 22m` and the discharging plan are
correctly framed. No proof yet, just a plan; honestly labelled.

### 3.4 Step 5 (lines 159–181) — **important honest negative result**

The crude block-frequency LP at n=89 is shown to be feasible via the
degenerate "all 24 low vertices are isolated" profile (`ℓ=24, h=65,
m=522, e_{LL}=0, e_{LH}=264, e_{HH}=258`). I checked all six
inequalities; they hold. This is a useful intermediate negative
result: "the LP alone, before criticality, cannot kill n=89."

### 3.5 Step 6 (lines 182–258) — endblock list-colouring — correct but with one notational stutter

The recovery: criticality forces "every endblock B is *not*
L-colourable for the residual list assignment". The doc has a
self-correcting passage at lines 217–227 where the author briefly
wonders if `K_t` endblocks force `t ≤ 2`, then corrects to: "no, some
v in K_t must have `|L(v)| ≤ t−1`, equivalently
`|Used(v)| ≥ 12−t`, equivalently v's `12−t` external neighbours are
rainbow-coloured in every 11-colouring of G − B". This is the right
correction and the right shape. The standard list-chromatic fact
`χ_l(K_t) = t` is used. The argument is sound.

The strongest case is the isolated-low vertex (t=1): all 11
H-neighbours of v are rainbow-coloured in every 11-colouring of
G − v. This is the lever used in everything that follows.

### 3.6 Step 6½ — "Isolated low vertex forces n ≥ 91" — **labelled "modulo Step 4", correct caveats**

This is where the argument starts to branch and the load-bearing
gaps appear. I verified each step:

- *Step 1 (rainbow).* Trivial from non-extendability.
- *Step 2 (≥ 6 non-edges in N(v)).* `|E(G[N(v)])| ≤ 49`,
  `binom(11,2) − 49 = 6`. Correct. Uses biplanarity of the 12-vertex
  subgraph `{v} ∪ N(v)`. Re-verified arithmetic.
- *Step 3 (contract a non-edge).* Identifying u_i, u_j gives G* with
  `χ(G*) ≥ 12`. Correct.
- *Step 4 (preserving K_9-freeness, lines 290–298).* **Open.** Doc is
  honest: "Suppose we can choose the non-edge ... so that G* is
  K_9-free." This is *not* proved; the author calls it the "split-K_8
  obstruction" and addresses it in Step 4+ below.
- *Step 5 (lines 299–330).* **A genuine gap is identified and
  partially repaired.** Original draft tried to invoke "Theorem B"
  (the n ≥ 89 result) on a 12-critical subgraph H ⊆ G*. The author
  caught that contraction destroys biplanarity in general, so Theorem
  B does not apply. The case split into A (`w ∉ V(H)`, biplanarity
  preserved, closes to `n ≥ 92`) and B (`w ∈ V(H)`, biplanarity may
  fail, open) is correct. Case B is left genuinely open.

This catch is the kind of self-audit a careful researcher should do.
The repair options (lines 332–365) are sensible. The note that
Repair Option 3 (Brooks-type budget on H ⊆ G*) sidesteps biplanarity
is well-taken because Brooks-type is a pure density theorem and does
not need planarity.

### 3.7 Step 5'''–5'''' — Case B arithmetic — **I cannot fully re-verify the "exactly one feasible configuration" claim**

Lines 400–443. The author writes down a brute-force feasibility sweep
over `(r, q, α, γ) ∈ [0,30] × [0,11] × [0,9] × N` and reports that
only `(r,q,α,γ) = (0,0,0,0)` is feasible. The argument compresses to:
"the joint constraints at `r = 13 + k` give `α + k + 4 − q ≤ γ ≤
α − q + k`, forcing `4 ≤ 0`."

I did not implement and re-run this sweep, but I verified the
inequalities by hand for a few `(r, q, α, γ)` triples and they are
consistent with the doc's algebra. **What I cannot verify from the
artifact alone**: that the sweep is exhaustive (no off-by-one in the
upper bound `r ≤ 30`), and that the β-availability bound `β ≤ 9 + q
− 2α` (line 416) is tight rather than merely a necessary condition.
A reviewer should ask for an explicit script (analogous to
`q0_profile_enum.py`) that prints the full sweep. **MAJOR (verifiability).**

The "consequence" at line 440 — "the single feasible configuration
`(r,q)=(0,0)` corresponds to H = G* itself being a 12-critical
K_9-free graph on 87 vertices with exactly 511 edges (Brooks-tight)"
— is logically correct *given* the sweep result.

### 3.8 Step 6 (induced-P_3 corollary, lines 459–497) — correct

The contrapositive: if `q=0` for every non-edge in N(v), then
G[N(v)] has no induced P_3, i.e. it is a disjoint union of cliques,
each of size ≤ 7 (from K_9-free). The "no induced P_3 iff disjoint
union of cliques" is a textbook fact; correct.

### 3.9 Step 6½–7.5 (Q0 profile model, lines 499–719) — sound but I flag one subtle point

The Q0 setup correctly tracks chunk sizes, ε-marks for inherited
edges to w, and exclusivity. **MINOR**: in §7.4 (Low-vertex quantized
attachment, lines 685–702) the doc states without proof that for a
low outside vertex L_0 attaching to a chunk C_i with `t_i ≥ 3`, the
attachment count `|N(L_0) ∩ V(C_i)| ∈ {0, 1, t_i}`. The given
justification reads "Same Gallai-forest argument: partial attachment
2..t_i−1 would make the block containing C_i ∪ {L_0} neither a clique
nor an odd cycle." This is *almost* correct, but the actual statement
needs `L_0` and C_i to lie in the *same* block of `G*[L*]`. If `L_0`
is adjacent to ≥ 2 vertices of `C_i`, then yes there are two
internally-disjoint paths from L_0 to C_i, so L_0 and C_i lie in the
same block (block = maximal 2-connected subgraph or bridge); and a
block containing K_t with an extra vertex L_0 adjacent to 2 ≤ d < t
of C_i is neither a clique nor an odd cycle (too many edges for a
cycle, missing edges for a clique). So the conclusion is correct, but
the doc should note explicitly that this requires L_0 ∈ L* (degree-11
in G*) — which it is, in the Q0 model. Self-contained but tightly
self-contained. **MINOR**.

### 3.10 §7.8 — Q0 enumeration result (143/160 feasible) — re-verified

I ran `python3 scripts/q0_profile_enum.py --limit 5`. Output matches
the doc's `143 feasible_cases / 17 infeasible_cases` claim, with the
`(7,4)` partition having a 30+24 high-only witness as documented.
**Verified.**

### 3.11 §7.10–7.13 — layer-aware local capacity probes — sound results, *one tactical conclusion needs care*

The SMS probes are well-targeted:

- `K_7 + bar K_5` on 12 vertices, 56 edges: UNSAT in 13.1 s. This is
  the local saturated profile for the `(t,ε,a) = (7,0,5)` and
  `(6,1,5)`-saturated cases. **Killer probe.**
- `K_4 + bar K_8`, `K_6 + bar K_6`: SAT (biplanar). Correct.
- `chunk-overlap (6,5,s)` sweep: SAT for `s ≤ 2`, UNSAT for `s ≥ 3`.
  Clean threshold result.
- `chunk-endpoint-overlap (6,5,5,s)` sweep: SAT for `s ≤ 2`. By
  monotonicity, UNSAT for `s ≥ 3`. Consistent.
- §7.13 coupled probe: 1-sum at the cut vertex `w`. The doc gives the
  correct two-line proof that biplanarity is preserved under 1-sums
  (each layer is planar and planar graphs are closed under 1-sums).
  **Verified.** This is exactly why the coupled probe cannot push past
  the one-sided threshold.

### 3.12 §7.16 — Fork C (commit 204282a) — **correctness and implication**

Tested graph: K_7 plus 7 outside vertices, each adjacent to 5 of K_7
missing a consecutive cyclic pair, with no outside-outside edges.
n=14, m=56. SAT in 0.011 s.

I cross-checked: m = 21 + 7·5 = 56. The vertex count and edge count
match the doc. Edge-count alone does *not* place this against the
biplanar bound: `6·14 − 12 = 72`, so the graph has room. The
biplanarity verdict is the SMS UNSAT-or-SAT itself, not an arithmetic
deduction.

**Logical implication for Q0.** The doc says (lines 1130–1138): the
saturated `K_7 + bar K_5` witness is UNSAT, but the *unsaturated*
balanced cyclic 35-edge profile on a K_7 chunk is SAT. Therefore the
partition (7,3,1) with cross-merge (K_3, K_1) is *not* killed by the
local-capacity method, because the high-only profile demand of 35
chunk-edges can be served by a non-saturated arrangement that is
biplanar. Correctly stated.

**This is not a contradiction with the saturated UNSAT result.** The
saturated case has every outside vertex adjacent to *all 7* of K_7,
which forces the local 12-vertex subgraph to be `K_7 + bar K_5`,
non-biplanar. The non-saturated case has each outside vertex adjacent
to only 5 of K_7 (missing 2), and the resulting graph is biplanar
because each outside vertex has degree 5 into the K_7 clique, which
is small enough. The threshold is the saturation, not the demand.

So Fork C is honestly a *negative* result: the easiest computational
attack on partition (7,3,1) fails, and Q0 closure for that partition
is *not* automatic. The doc's framing of Forks A/B/C as the next-move
options is correct.

### 3.13 Status block (lines 1140–1153) — accurate

"Phase 6 is now reduced to two concrete combinatorial problems: Step
4+ and Q0 high-only closure." This is consistent with everything
above. The note that closing either piece eliminates the
isolated-low-vertex subcase at n=89 is correct *given* the proven
parts of the argument.

---

## Section 4 — The C_7[K_4] (= C_7 ⊠ K_4) UNSAT ruling

**File: `data/c7_k4/README.md` and `data/c7_k4/20260511T045903Z/*`.**

I independently re-checked:

- Definition: `C_7[K_4]` is the lexicographic product, equivalently
  the clique blowup of C_7 with each vertex replaced by K_4. With K_4
  as the second factor, lexicographic and strong products coincide
  (re-verified with NetworkX: 28 vertices, 154 edges, isomorphic).
  **MINOR**: the project freely switches between `C_7[K_4]` and
  `C_7 ⊠ K_4` notation. These are isomorphic for K_4 as the second
  factor — accept. **But** the manuscript should clarify: the
  Cartesian product `C_7 □ K_4` is a *different* graph, also on 28
  vertices, with 28·(2+3) / 2 ≠ 154 edges and chromatic number 4. A
  reader who skims could confuse them. (n=28 Cartesian has 28+28·3/2·...
  irrelevant; the point is the symbol ⊠ should be defined once
  early.)

- `n=28, m=154, ω=8, α=3, χ=10`: re-verified.
- `K_9`-free: follows immediately from `ω=8`.
- `m ≤ 6n − 12 = 156`: slack 2. So the biplanar edge bound does not
  rule it out, and the SMS run is the actual decision procedure.

The SMS run (logged in `data/c7_k4/20260511T045903Z/stdout.log`):
- `Search finished` with zero `Solution` lines (i.e. UNSAT).
- `exit_status = 0` in `meta.txt` and `exit_status` file.
- 9 h 40 min wall, 6 h 46 min SMS-internal.
- `ThicknessTwoChecker`: 12.99 M calls, 3.84 M Kuratowski clauses
  added — confirming the propagator was active.
- Encoding: 602 clauses, 756 variables — i.e. the constraints fix
  most of the directed-graph variables before search begins (28
  vertices × 27 directed-arc pairs = 756 arc variables, matches).
- Initial partition: `1 0 0 0 1 0 0 0 ...` — this is 7 cells of
  size 4, encoding "permutations are allowed within each fibre". The
  cycle rotation symmetry is *not* explicitly broken in the partition
  (KSS argued the propagator can handle it dynamically; the doc
  records "MinimalityChecker: 3.25 M calls, 8 440 added clauses",
  which is small but nonzero, consistent with cycle-rotation symmetry
  being lazy-broken).

**MAJOR — verifiability of the UNSAT.** This is the strongest
empirical claim in the project. It is currently single-tool, and the
tool is one I and the author both audit only as "Patches A and C
applied to v1.0.0; smoke and calibration both passed". A second
independent biplanarity certificate (e.g., a separate Kuratowski-based
ILP, or a hand-written CEGAR loop using `networkx.check_planarity`)
would dramatically strengthen the claim. Acknowledged in the doc as a
"convention" (phase4_results.md:55–58): "A SAT result is suspect
unless verified by an independent biplanarity test." Note that this
convention is asymmetric: only SAT results are flagged as
needing-independent-verification, not UNSAT results. For a paper
making `C_7[K_4]` non-biplanar a load-bearing computational claim,
the asymmetry should be reconsidered.

**Significance.** The README correctly downgrades the strength of the
conclusion: "the bracket 9 ≤ χ_EM ≤ 12 is unchanged by this result,
but the population of unverified candidates shrinks materially". This
is accurate. **MINOR**: the abstract sketch in `paper_skeleton.md`
line 23 says the four blowup results "Conclude: every blowup with
n ≤ 30, ω ≤ 8, χ ≥ 10, |E| ≤ 6n−12 is non-biplanar." The conclusion
is correct for the *cycle clique blowup* family specifically; the
manuscript should say this explicitly. Other 28-vertex 10-chromatic
K_9-free graphs (non-blowup) are *not* ruled out by these runs.

---

## Section 5 — docs/upper_bound_notes.md (literature audit)

I cross-checked the load-bearing quotes:

- KY 2014 Theorem 3 at k=12: `F(12,n) = ⌈(65n−54)/11⌉`. **Verified.**
  My re-computation: `F(12,78) = 456`, `F(12,89) = 521`.
- KY 2018 Brooks-type Theorem 6: `y_k = max(2k−6, k²−5k+2)`,
  `y_{12} = 86`. **Verified.** Brooks at n=89: 522.
- Biplanar edge cap `6n−12 = 522` at n=89. **Verified.**
- Crossover analysis: Brooks contradicts biplanar exactly for
  n ∈ [78, 88]. **Verified** by direct table check.
- GP 2022 Lemma 3.3 (every k-Ore graph contains K_{k-1}) is correctly
  cited as the non-Ore lever; the doc honestly notes that the
  inductive proof "resisted us" and falls back on the GP potential
  apparatus. This is a citation issue, not a proof issue, and the
  citation is to a peer-reviewed JCTB paper. Accept.
- KS 2000 + Johansson asymptotic: the table at lines 273–280 shows
  the required Johansson constant `c_9 ≤ 0.2` is well outside what
  modern bounds give (8–1800). Correctly stated as "asymptotic route
  fails at finite k=12."
- GP 2022 Conjecture 1.6: open at k=12, explicit `ε_12 ≈ 0.00271`
  while the needed value is `≥ 1/11 ≈ 0.0909`. **Verified.**

**MINOR**: the doc cites Kostochka–Yancey 2014 ([arXiv:1209.1050])
as "Ore's Conjecture on color-critical graphs is almost true", JCTB
109 (2014) 73–101. I did not cross-check the journal page numbers
against MathSciNet (per the user's standing instruction about
phantom-citation risk). Recommend a Crossref pass before publication.

---

## Section 6 — Forks A, B, C — line-by-line on the load-bearing discharge

### Fork A — "Every u_i-only vertex is low" (lines 1064–1071)

Speculative. The doc lists two candidate angles:
1. Rainbow 11-colouring of G−v constrains u_i's neighbour colours.
2. ρ_{12}(G) = 86 Brooks-tight rigidity.

Neither is even a sketch yet. **OPEN.** Honestly labelled.

### Fork B — "At most two u_i-only low vertices exist" (lines 1072–1081)

Conditional on Fork A. Also speculative. Two candidate angles
(Gallai-on-G[L] block structure; endblock list-colouring on
u_i-only low vertices). Honest about the speculation. **OPEN.**

### Fork C — Computational pivot (lines 1082–1138) — verified above

The pivot to partition (7,3,1) with cross-merge (K_3, K_1) is logical
because in (7,4) we need the K_6 chunk (post-merge from K_7) to give
a sharp probe, but the chunk side that survives saturation is the
K_3 side, which has very low demand. In (7,3,1), the K_7 chunk
survives unmerged and the saturated K_7-chunk probe is the killer
K_7 + bar K_5. The hope was that the *only* feasible high-only
witness for the K_7 chunk would be saturated — empirically falsified
by the n=14, m=56 SAT run.

**Consistency check.** Both probes use the same SMS pipeline, so the
SAT and UNSAT verdicts are calibration-consistent. The conclusion
"Fork C does not currently produce a closed Q0 partition" is correct
and the doc's tone is appropriately deflated.

---

## What I cannot verify from artifacts alone

1. **UNSAT correctness of any large SMS run.** I checked `meta.txt`,
   `exit_status`, and `stdout.log` for the `c7_k4` run; they are
   self-consistent and consistent with the doc's narrative. I did not
   replay them through a second oracle and the artifacts do not
   include a "proof object" or DRAT trace. SMS's UNSAT verdict is
   trusted on the strength of the calibration runs (KSS's published
   candidate1 reproduced, multiple smaller smoke tests pass).
2. **Step 5'''' brute-force sweep (lines 421–443).** The "sweep over
   `(r,q,α,γ)` finds exactly one feasible configuration" claim is
   not implemented in the repo as far as I could find. The algebraic
   reduction at lines 430–435 is consistent, but an explicit script
   (analogous to `q0_profile_enum.py`) printing every infeasible
   reason would make this checkable.
3. **The chromatic number χ(C_7[K_4]) = 10 lower bound.** I checked
   `χ ≥ ⌈n/α⌉ = ⌈28/3⌉ = 10` via NetworkX-computed `α = 3`. The α
   computation iterates over max-cliques of the complement, which is
   exact for n=28. **Verified by my run** (NetworkX `find_cliques` on
   the complement gives `α = 3`). The upper bound `χ ≤ 10` is by the
   explicit witness colouring in plan.md, which I checked has zero
   monochromatic edges. So `χ = 10` is verified.
4. **Mansfield 1983, Hutchinson 1993, Boutin–Gethner–Sulanke 2008,
   Gethner–Sulanke 2009, Kostochka–Stiebitz 2000, Johansson 1996,
   Molloy 2019, Davies–Kang–Pirot–Sereni.** I did not pull these
   PDFs. The internal citations look plausible but per the user's
   standing instruction on phantom-citation risk, route any
   load-bearing citation through Crossref before publication.
5. **The "every 12-Ore graph contains K_{k-1}" lever via GP Lemma 3.3.**
   The doc honestly flags that direct induction "resisted us" and
   defers to the GP potential apparatus. I did not pull GP 2022 to
   check Lemma 3.3 literally. The author records this as a known
   "fall back on citation" rather than a proven step in the file. Fair.

---

## What I am confident about

1. **Graph-theoretic invariants of every cycle clique blowup tested**
   (`(4,4,4,4,3), (3,3,5,3,5), (3,4,4,3,5), (4,4,4,4,4,4,4)`) are
   computed correctly by `cycle_blowup.py` and match NetworkX
   cross-checks. The chromatic-number lower bound `χ ≥ 10` is forced
   by `α` and the upper bound `χ ≤ 10` by an explicit witness
   colouring (for the headline case).
2. **The arithmetic Phase 6 framework** (KY at k=12, Brooks-type at
   k=12, biplanar bound, n ≥ 89 threshold) is correctly assembled.
   Re-verified each number.
3. **The Gallai-forest structure on G[L]** (Step 2) and the
   list-colouring obstruction at endblocks (Step 6) are standard and
   correctly applied.
4. **The Q0 profile enumeration** produces 143 feasible cases out of
   160, matching the doc, when I ran the script. The Q0 exclusivity
   claim (§7.3) is correctly proved.
5. **The "K_7 + bar K_5 UNSAT but K_7 + cyclic-5-neighbours SAT"
   asymmetry** is not contradictory: it reflects the difference
   between saturated and non-saturated chunk-attachment demand. The
   conclusion that Fork C does not kill partition (7,3,1) is honestly
   stated.
6. **The 1-sum biplanarity closure argument in §7.13** is correct
   (planar graphs are closed under 1-sums; biplanar = "both layers
   planar", and each layer is independently closed under 1-sums).
7. **The deletion of the "Family A" and "Family B" attacks from the
   plan** (lines 187–199 of plan.md) is a textbook example of honest
   self-audit. The reasons given (`K_a + H` exhausted, Hajós/Ore do
   not raise χ) are correct.

---

## Summary table of issues

| # | Severity | Location | Issue |
|---|---|---|---|
| 1 | MAJOR | plan.md:71 | `K_{5,12}` listed as not biplanar; BHM 1964 thickness formula gives 2, so this regression row is wrong as stated. Recheck before wiring into tests. |
| 2 | MAJOR | data/c7_k4/ | UNSAT is single-tool. No independent biplanarity oracle has re-checked the verdict. Replay through a CEGAR loop using `networkx.check_planarity` on each layer of an SMS-emitted attempted certificate (or DRAT trace). The phase4_results convention covers SAT verifiability but not UNSAT. |
| 3 | MAJOR | phase6_discharge_attempt.md:421–443 | The "brute-force sweep over `(r,q,α,γ)` finds exactly one feasible configuration" claim is not implemented in a script. Add `scripts/step5_caseB_sweep.py` analogous to `q0_profile_enum.py`. |
| 4 | MINOR | biplanar_check.py:218–240 | `--edges` without `--partition` silently uses no symmetry breaking; this risks spurious UNSAT for callers who forget. Make it a hard error or print a warning. |
| 5 | MINOR | README.md:16 vs everywhere else | Notation `C_7 ⊠ K_4` vs `C_7[K_4]` used interchangeably. Define once that the strong product equals the lex product when the second factor is complete; warn against confusion with the Cartesian product `C_7 □ K_4`. |
| 6 | MINOR | upper_bound_notes.md (various) | KY/KS/GP/Molloy citations not yet routed through Crossref. Per the user's standing instruction on phantom-citation risk, do this before any draft submission. |
| 7 | MINOR | phase6_discharge_attempt.md:685–702 (§7.4) | "Same Gallai-forest argument" needs an extra sentence: the quantization `{0, 1, t_i}` requires L_0 ∈ L*, i.e. L_0 is itself a degree-11 vertex of G*. Currently implicit. |
| 8 | MINOR | paper_skeleton.md:23 | Theorem A's "conclude every blowup... is non-biplanar" should specify "every *cycle clique* blowup", since non-blowup 28-vertex candidates are not ruled out. |
| 9 | NIT | phase6_discharge_attempt.md:347 | `ρ_{12}(G*) = 130(n−2) − 22(m − 11 − q) = 68 + 22q` at n=89, m=522. `q` here is the common-neighbour count, but Step 6 reuses `q` for a colour variable. Briefly clashes with §6½'s notation. |
| 10 | NIT | data/c7_k4/README.md:74 | The reproduce recipe says `python /<abs>/...`; should be a runnable example, e.g. `python scripts/earthmoon_blowup.py --weights 4,4,4,4,4,4,4` via `run_smsg.sh`. |

---

## Closing remarks

This is one of the most honestly-self-audited research artifacts I
have reviewed. Every speculative step is labelled "modulo", every
negative result is recorded (Fork C is the canonical example), the
literature audit explicitly tables what the published asymptotic
theorems do and do not give at the finite k=12, and the "Removed from
earlier draft" section in plan.md is a textbook example of
researcher integrity.

The two biggest open frontiers — closing Step 4+ and closing the Q0
high-only profile via a non-local argument — are accurately scoped.
Neither is "almost done"; both are research problems. The manuscript
skeleton's instinct to wait before drafting Theorem C until one of
these is closed (or the gap is precisely identified) is the right
call.

If anything, the project should make its single biggest weakness more
visible to the reader: every load-bearing UNSAT verdict comes from
one SAT codebase that the project itself patched (Patches A and C in
spike_sms_build.md). The right way to inoculate against that is to
add a second oracle for at least one UNSAT instance, or to extract
and re-verify a DRAT proof. Without this, the strongest computational
claim in the paper rests on a single trusted-because-it-reproduced-KSS
component.

Verdict: **no claim that the project advances as proved is
overstated**. The project is correct as stated. The next 2-3 hours
of work to close issues #1, #4, #5, #7, #8, #9 are mechanical; #2
and #3 are genuinely worth doing before publication; the open
mathematical problems remain open.
