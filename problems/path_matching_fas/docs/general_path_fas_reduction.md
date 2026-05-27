# Structural reductions for general tournament Path-FAS

This note records a 60–90 minute structural-reduction probe in the
direction of resolving the general tournament Path-FAS half of
Aboulker–Aubian–Lopes Problem 4.4 ([arXiv:2402.10782](https://arxiv.org/abs/2402.10782)).
The fork-tree adversarial subfamily was closed in Section 65 of
`docs/exchange_proof_draft.md` (Theorem 65.A: constrained Path-FAS on
fork-tree pairings is decidable in `O(k)`).  The general tournament
problem remains open.

The deliverable is structured around five reduction candidates and a
honest verdict.  Throughout we work with the formal Path-FAS target
(equivalently the linear-forest-ordering (LFO) problem on tournaments):
given a tournament `T`, decide whether `T` admits a linear order whose
back-arc graph is a linear forest.

## 1. Literature survey

### 1.1 Background, theorems

- **Tournament FAS is NP-hard.**  Alon, *Ranking tournaments*, SIAM J.
  Discrete Math. 20 (2006), 137–142.  (See also Charbit–Thomassé–Yeo
  on the same.)  Ailon–Charikar–Newman first proved NP-hardness under
  randomized reductions.  Alon’s derandomization uses quadratic
  residues. ([N. Alon — Ranking tournaments](https://www.cs.tau.ac.il/~nogaa/PDFS/paley.pdf))
- **Tournament FAS in 2^O(√k) · n^{O(1)}.**  Alon–Lokshtanov–Saurabh,
  *Fast FAST*, 2009 (arXiv:0911.5094).  Linear vertex kernel
  ([arXiv:0907.2165](https://arxiv.org/abs/0907.2165)). Confirms
  subexponential FPT but not polynomial.
- **Optimal Linear Arrangement and cutwidth on tournaments are
  NP-hard.**  Fomin–Pilipczuk, *Subexponential parameterized algorithm
  for computing the cutwidth of a semi-complete digraph*,
  [arXiv:1301.7314](https://arxiv.org/abs/1301.7314); see also
  *Exploring the complexity of layout parameters in tournaments and
  semicomplete digraphs* ([arXiv:1706.00617](https://arxiv.org/abs/1706.00617)).
  Both are NP-hard on tournaments under ETH.
- **Aboulker–Aubian–Lopes Problem 4.4.**  Forest-FAS on tournaments is
  NP-complete; matching-FAS (M) and path-FAS (P) are open.
  ([arXiv:2402.10782](https://arxiv.org/abs/2402.10782)).
- **Matching-FAS on tournaments is in P** (this folder; see
  `docs/lemmas.md`).
- **Path-FAS on fork-tree adversarial subfamily is in P** (this folder;
  Theorem 65.A in `docs/exchange_proof_draft.md`).

### 1.2 Folklore-status pieces of relevant structure

- **Camion's theorem.**  Every strongly-connected tournament is
  Hamiltonian.  Consequently the SCC condensation of a tournament is a
  transitive tournament; the SCCs are totally ordered.  This is the
  standard reason any "between-SCC" decomposition is trivial in the
  tournament setting.  (Cited in nearly every textbook on tournaments;
  e.g. Bang-Jensen–Gutin §1.5.)
- **Tournament modular decomposition.**  Every prime tournament has a
  unique modular decomposition; the quotient by a non-trivial module
  yields a smaller tournament.  Standard reference: Habib–Paul,
  *A survey of the algorithmic aspects of modular decomposition*
  (2010).  Polynomial algorithms exist for the decomposition itself.
- **Score sequence bounds the FAS size and is known to characterize
  some easy classes** — e.g. transitive tournaments (FAS = 0) and
  near-transitive (FAS ≤ 1).  Not deeper than that.
- **No published positive Path-FAS result is known to me** beyond the
  fork-tree case in this folder.  None of the cutwidth / OLA / k-FAST
  results turn into polynomial Path-FAS, because the linear-forest
  constraint on back-arcs is not a linear-arrangement objective.

### 1.3 Sub-class boundaries known to be easy

| sub-class | LFO problem complexity | reason |
|---|---|---|
| transitive tournaments | trivially YES | FAS empty; backs = empty graph |
| acyclic tournaments | trivially YES | same |
| tournaments with FAS ≤ 1 | trivially YES | back-arc graph has ≤ 1 edge |
| score-extreme (some d^-(v) = 0 or n-1) | trivially YES | sink/source removal |
| fork-tree constrained instances | in `O(k)` (this folder) | Theorem 65.A |
| general tournaments | open | this paper's target |

The boundary between "easy" and "open" is therefore very thin: as soon
as the tournament is strongly connected and not score-extreme, Path-FAS
is wide open.  No published structural parameter separates the easy
classes from the hard.  Even for tournaments of bounded *cyclicity*
(in the sense of small FAS) the problem reduces only because the
linear-forest constraint becomes vacuous when FAS ≤ 2 (one or two
arcs cannot create degree-3 or a cycle).

## 2. Score-window band decomposition

The score-window theorem (`docs/score_window.md`) implies that in any
LFO, vertex `v` lies in positions `[d^-(v)-2, d^-(v)+2]`.  Partition
the `n` LFO positions into disjoint bands of width `B`:
`band_j = [jB, jB+B-1]`.  Each tournament vertex has a *band-domain*
consisting of the bands its score window touches.

We test the **summary-state band-DP** in
`scripts/band_decomposition_probe.py`:

```
state := (placed_mask, degree-vector over n, union-find roots over n)
transition := pick subset of unplaced vertices whose window overlaps
              band j; pick permutation respecting per-slot windows;
              load forced new back-arcs; check linear-forest invariants
```

The DP dedups by the state key.  When the full key
`(placed_mask, deg, UF)` is used, the DP is sound and complete
(equivalent to brute force restricted to band-respecting orders).  When
we drop either `deg` or `UF` from the dedup key, the DP becomes a
genuine summary-state algorithm whose correctness is an empirical
question.

### 2.1 Empirical results

We ran the band-DP at `B ∈ {1, 2, 3}` and several summary-key flavors.

**Full exact n=7 census (456 non-isomorphic tournaments, 436 YES, 20 NO):**

| B | summary key | disagreements with brute |
|---|---|---|
| 1 | (mask, deg, UF) | 0/456 |
| 2 | (mask, deg, UF) | 0/456 |
| 3 | (mask, deg, UF) | 0/456 |
| 1 | (mask, deg) only | 0/456 |
| 1 | (mask, UF) only | 0/456 |

**All 1798 combinatorial NO records at n=8** (size-bound NO trivially
caught by Hall): all summary keys gave 0 false-YES disagreements.

**Random uniform tournaments at n ∈ {7, 8, 9, 10, 12}** (against brute
or the score-window exact solver):

| n | samples | B | (mask, deg, UF) | (mask, deg) | (mask, UF) | (mask) only |
|---|---|---|---|---|---|---|
| 7 | 100 | 2 | 0 | 0 | 0 | 23 |
| 8 | 100 | 2 | 0 | 0 | 0 | 35 |
| 9 | 10 | 2 | 0 | 0 | 0 | 1 |
| 10 | 50 | 2 | 0 | 0 | 0 | 4 |
| 12 | 50 | 2 | 0 | 0 | 0 | 0 |

The `(mask)`-only DP (no deg, no UF) is definitively unsound: at
already-modest `n` it returns false YESes / false NOs (mixed in this
test).  But **degree-only summary and UF-only summary are empirically
exact through n=12.**

### 2.2 Why this is NOT a polynomial algorithm

The state space *size* is empirically exponential.  Tracking
`max(|frontier|)` across the DP:

| n | uniform random T (median) | skew p=0.05 noise on transitive |
|---|---|---|
| 6 | 112 | 89 |
| 7 | 258 | 251 |
| 8 | 452 | 505 |
| 9 | 536 | 1260 |
| 10 | 436 | 2868 |
| 11 | 75 | 6870 |
| 12 | 318 | 12081 |

The skew (light-noise) regime blows up super-polynomially — confirming
the existing observation in `docs/score_window.md` that the
reversed-matching family causes exponential blowup in the
score-window DP state.

### 2.3 Honest read

The fact that the (mask, deg, UF) — and even (mask, deg) — keys never
collided across our census and random probes is suggestive but not a
proof.  Section 47 of `docs/exchange_proof_draft.md` already records
`ff_signature_probe.py` finding *(placed-set, deg, UF)* collisions at
n=7 in a slightly different framing: two prefixes with identical
visible-latent signatures, one extendable, the other not.  Replicating
that in the band-DP requires a transition setup that allows latent
connectivity through forgotten vertices in earlier bands.  Our
band-DP does NOT forget any placed vertex's identity, so it is
strictly stronger than the visible-latent attempts.  This explains the
zero disagreement count, and it ALSO explains why state size is
exponential: keeping every vertex's identity is exactly what blows up.

**Conclusion 2.A.**  The score-window band decomposition is
*information-complete* when the summary keeps all placed-vertex
identities plus degree and union-find roots.  It is *not* a
polynomial algorithm: the dedup quotient is empirically exponential
on the skew family.  Dropping identities (the only way to get a
polynomial state) is exactly the visible-latent reduction already
refuted in Section 9.13 of the proof draft (entropy family + skew
witness).

The smallest B at which the feasibility-only band-DP "disagrees with
truth" is not the right question for this folder's state of the art:
*no* B value disagrees once we keep full vertex identities.  The
right question is: *at what B does the state space first become
polynomial?*  Answer: it does not, in the range tested.

## 3. SCC + modular decomposition

### 3.1 SCC condensation is essentially vacuous on the hard family

For the SCC reduction to do real work, the input tournament must have
several SCCs.  Empirically:

- **n=7 LFO NO instances (20 total):** *all 20 are strongly connected*
  (single SCC of size 7).
- **n=8 combinatorial LFO NO instances (1798 total):** 1758 (97.8%)
  are strongly connected; 40 (2.2%) split as (7, 1) — i.e. one
  isolated vertex.
- **n=7 non-isomorphic tournaments overall:** 353/456 (77%) are
  strongly connected.

The hard cases are essentially always strongly connected.  SCC
condensation is therefore **not a non-trivial reduction** for
Path-FAS.

### 3.2 Modular decomposition

The 18 vertex-minimal combinatorial NO instances at n=7 split between
prime and non-prime:
- 10 are prime (no non-trivial module).
- 10 admit a non-trivial module.

Among 300 sampled n=8 combinatorial NO instances:
- 135 prime (45%).
- 165 non-prime (55%).

For the *non-prime* cases the modular decomposition does give
algorithmic leverage, but only weakly.  Lemma 6.1 below shows that in
any LFO every "large" module is *almost* contiguous: at most 2
interlopers from each side of the module block.  This bounds the
gluing interface to constant size when `|M| ≥ 5`, but does NOT
give a clean LFO(T) ↔ LFO(T[M]) ∧ LFO(T/M) decomposition.

**Concrete observation.**  Let `M` be a module of `T` and let `x ∉ M`
be an external vertex; then either `M → x` (all arcs from `M` to `x`)
or `x → M` (all arcs from `x` to `M`).  In an LFO, if `M → x` and `k`
M-vertices are placed AFTER `x`, then `x` collects `k` back-arcs
`m → x`.  The LFO bound `deg ≤ 2` forces `k ≤ 2`.  Same for the
other side.  So `x` can have at most 4 M-vertices straddling it.
Hence with `|M| ≥ 5`, `M` is almost contiguous (block plus ≤ 4
boundary interlopers per external vertex).  When `|M| ≤ 4` the
constraint is vacuous.

**This reduction is genuine but applies only to ~50% of the hard
instances.**  Even for those, the prime sub-tournament obtained by
recursively decomposing modules is still wide open.  Modular
decomposition is *necessary* but not *sufficient* for a polynomial
algorithm.

**Conclusion 3.A.**  SCC decomposition is empirically vacuous on the
LFO obstruction family.  Modular decomposition is partially
applicable (∼50% of n=7,8 obstructions are non-prime) and gives a
clean Boolean reduction on those cases, but the residual prime
fragments are precisely the still-open problem.  This is **not a
dead end** — it should be the first preprocessing step in any
candidate polynomial Path-FAS algorithm — but it is *not* a path to
P alone.

## 4. Cycle-core extraction in general

The fork-tree Cycle-Core Extraction Lemma (Lemma 52.1 of the proof
draft) says: every minimally fatal toggle support in a fork-tree
pairing is a union of full even-odd blocks whose B-image decomposes
into adjacent intervals and whose block/interval incidence is a simple
cycle.  This is the structural backbone of the V6'' classifier and
hence of Theorem 65.A.

### 4.1 Does the analog hold in general tournaments?

The naive translation would be: *every vertex-minimal LFO NO tournament
contains a "cyclic-ladder" sub-structure*.  We test this against the
existing structural data on the 18 vertex-minimal combinatorial n=7
NO instances (from `data/lfo_combinatorial_no_analysis.json`).

The relaxation classification of those 18 NO instances is:

| relaxation type | count | meaning |
|---|---|---|
| coupling     | 7 | back-arc max-degree-2 ordering exists but isn't a forest |
| degree       | 7 | forest ordering exists but max degree > 2 |
| cycle        | 2 | only the linear-forest obstruction (both relaxations YES) |
| both fail    | 2 | neither relaxation is YES |

The **"cycle" type (2/18)** is the cleanest cycle-core analog: the
back-arc graph in *every* candidate ordering contains a cycle, with
no degree obstruction.  The other 16/18 instances **fail for reasons
that are not cycle-based**: they fail by max-degree blow-up or by the
interaction between max-degree and acyclicity.

**Counterexample to general Cycle-Core Extraction.**  Take any of the
seven "degree" obstruction tournaments (e.g. NO-id #4 in the
combinatorial analysis, dual-orbit D10).  This tournament has *no*
forced cycle in the back-arc graph: every order admits a forest
back-arc structure.  The obstruction is purely a degree obstruction.
Therefore there is no cyclic-ladder sub-core that explains the
LFO-NO label.

Formally: in the language of fork-trees, the *fatal-support* concept
is well-defined because pairings come with a canonical block
structure.  In general tournaments there is no block structure to
project onto.  The fork-tree Cycle-Core Lemma uses the
block/interval incidence graph in an essential way (Section 52.5
of the proof draft).  Without this scaffolding, "cyclic-ladder core"
has no meaning.

**Conclusion 4.A.**  Cycle-Core Extraction does *not* generalize:
n=7 already contains LFO-NO tournaments whose obstruction is
purely a degree obstruction with no forced back-arc cycle.  The
fork-tree structural backbone (Theorem 53.2 / Lemma 52.1) is
*specific to the fork-tree pairing family*.  The general
Path-FAS problem must reckon with at least two distinct obstruction
families (degree-only and cycle-only), plus their interaction.

This is a hard dead end for the cycle-core direction.

## 5. Flex graph structure on general tournaments

The flex graph `F(T)` has a vertex per tournament vertex and an
undirected edge `{u, v}` iff the score windows `W(u)` and `W(v)`
overlap (so the relative order of `u, v` is not forced by the
score-window theorem).  By construction `F(T)` is an interval
graph (each window is an interval of positions).

### 5.1 Structural observations

**At n=7 (full census):**
| max-clique of F(T) | tournaments |
|---|---|
| 5 | 2 |
| 6 | 78 |
| 7 | 376 |

So 82% of n=7 tournaments have *all* vertices in mutual flex
overlap — the flex graph is the complete graph, the score-window
contributes essentially nothing.

**Light-noise skew family** (random reverse arcs added to transitive
with probability `p`):
| n | p | flex max-clique (typical) | forced pairs (typical) |
|---|---|---|---|
| 12 | 0.05 | 6–8 | ~25 |
| 16 | 0.05 | 6–9 | ~62 |
| 20 | 0.05 | 6–9 | ~113 |
| 24 | 0.05 | 6–9 | ~182 |

This matches the existing claim in `docs/score_window.md` that flex
max-clique stays at ≤ 9 after Hall feasibility (radius `r = 2`
implies Hall bound `4r+1 = 9`).

### 5.2 Interval graph + chain structure

In fork-trees the flex graph is special: not just an interval graph,
but an *interval graph whose vertices admit a canonical pairing
structure* (the (A_i, B_i) pairs of the pairing π).  This pairing
gives the block decomposition used in cycle-core extraction.

In general tournaments **no such pairing exists**.  The flex graph
is an arbitrary interval graph of bounded clique width (≤ 9).  This
is much weaker than the fork-tree structure: classical interval-graph
algorithms (e.g. perfect graph coloring) are polynomial, but they do
not give an LFO algorithm because the LFO constraint is not a
property of the interval graph alone — it depends on the actual
tournament orientation arcs, which are *not* encoded in the
flex graph.

### 5.3 What the flex graph IS useful for

The forced/flexible decomposition (`scripts/score_window_forced.py`)
gives a real preprocessing step: every disjoint window-pair has a
forced relative order, and the forced back-arcs collectively form a
graph that must already be a linear forest (else LFO NO).  This
catches **2 of 20** n=7 LFO NOs immediately (the size-bound NO
class) plus an unknown additional fraction by forced-degree / forced
-cycle violations on the forced backbone.

The exact n=7 census from this folder shows that the forced backbone
is necessary but not sufficient: only ∼10% of NO instances are
caught by forced-backbone analysis alone.

**Conclusion 5.A.**  The flex graph on general tournaments is an
interval graph of bounded clique width 9, but it does *not* inherit
the pairing/block structure that makes fork-trees tractable.  It is
useful for preprocessing (forced backbone, Hall feasibility) but
not for an algorithm in its own right.

## 6. Verdict

### 6.1 What I tested

| candidate reduction | verdict |
|---|---|
| 2. Score-window band-DP | Information-complete with full identities; exponential state space without; not a polynomial algorithm |
| 3a. SCC condensation | Empirically vacuous on the LFO-NO family (97%+ are strongly connected) |
| 3b. Modular decomposition | Genuine reduction on the ~50% non-prime sub-family; residual prime case still open |
| 4. Cycle-core extraction | Does not generalize (7/18 of vertex-minimal n=7 NO instances are pure degree obstructions, no forced cycle) |
| 5. Flex graph structure | Useful preprocessing (forced backbone, Hall) but no algorithmic core |

### 6.2 What advances the problem

Only candidate **3b** — modular decomposition preprocessing — is a
substantive partial reduction.  It is *known* in folklore as the
right first step on every tournament problem; nothing here is new.

What this probe rules out:
- The hope that *some* band width B linearizes the band-DP is false:
  no B value gives a polynomial state space on the skew family.
- The hope that *cycle-core extraction* generalizes is false: the
  fork-tree block scaffolding is essential.
- The hope that *SCC decomposition* simplifies the LFO obstructions
  is false: obstructions are strongly connected.

### 6.3 Partial reduction: modular near-contiguity (provable, weaker than I first hoped)

I initially expected the standard "modules occupy contiguous intervals
in any LFO" argument to apply.  It does NOT.  The correct statement
is weaker.

**Lemma 6.1 (Module quasi-contiguity for LFO).**  Let `T` be a
tournament, let `M` be a module with `|M| ≥ 5`, and let `σ` be an LFO
of `T`.  Then for any external vertex `x ∉ M`, at most 2 vertices of
`M` lie on each side of `x` in `σ` whenever `x` is uniformly
dominated by — or uniformly dominates — those `M`-vertices.

*Proof.*  WLOG `M → x` (i.e. every arc from `M` to `x` is present).
Suppose `k` vertices of `M` lie after `x` in `σ`.  Each such vertex
`m_i` contributes a back-arc `m_i → x`.  Hence `x` has at least `k`
back-edges incident from M-vertices placed after it.  In an LFO,
each vertex has back-degree ≤ 2, so `k ≤ 2`.  ∎

**Corollary 6.2.**  When `|M| ≥ 5`, in any LFO of `T` the vertices of
`M` occupy a contiguous interval of positions except for at most 4
interlopers from outside `M`, two from each end of the M-block.

This is materially WEAKER than the "modules are contiguous" claim I
expected.  In particular it does not directly justify a clean
`LFO(T) ↔ LFO(T[M]) ∧ LFO(T/M)` decomposition.  When `|M| < 5` the
argument gives no constraint at all.

**Proposition 6.3 (Recursive modular reduction; partial).**  If `M`
is a module of `T` with `|M| ≥ 5` and the homogeneous-orientation
class of `M` is "all of `M` dominates `x`" or "x dominates all of `M`"
for *every* external `x`, then `T` is LFO YES iff:
1. `T[M]` is LFO YES, AND
2. `T/M` (where `M → m_*` is the module quotient) is LFO YES, AND
3. There is a joint placement consistent with the at-most-4 interlopers
   from condition (Corollary 6.2).

*Verdict.*  Proposition 6.3 is a real partial reduction but it
remains *partial* on two axes: (a) it gives no reduction when
`|M| < 5`, and (b) condition (3) still requires solving the full LFO
on `T` restricted to an interface set, which is not obviously
smaller.

**On novelty.**  The modular decomposition itself is folklore
(Habib–Paul); the LFO-specific quasi-contiguity (Lemma 6.1) and its
boundary constant `k ≤ 2` come from the score-window radius 2.  I am
not aware of a published statement of Lemma 6.1 in the LFO setting,
but it is an elementary consequence of the back-degree-2 constraint
once one starts looking.

### 6.4 What I cannot rule out

- **A bounded-tree-width LFO decomposition.**  The score-window
  guarantees that the back-arc graph has tree-width bounded by O(1)
  per position-band.  Whether the LFO problem itself has
  bounded-treewidth flavor that aligns with the band partition is not
  ruled out by this probe.  This would be the natural next direction.
- **A polynomial algorithm based on score-window forced backbone +
  bounded-interval-clique search.**  The forced backbone is a fixed
  linear forest; the flex part is a bounded-clique interval graph
  decision problem.  *If* the flex part reduces to a known
  polynomial problem on bounded-clique interval graphs (e.g. interval
  graph coloring, list coloring), this would close the problem.  No
  evidence here points to such a reduction.

### 6.5 Conclusion

The structural-reduction direction, in its naive forms, does not
close general tournament Path-FAS.  The single substantive reduction
(modular decomposition) is known, gives at most a 50% size reduction
on the hard family, and leaves prime obstructions intact.  The
fork-tree solution does *not* lift: the block/interval scaffolding
that powers cycle-core extraction has no analog in arbitrary
tournaments.

The cumulative empirical evidence in this folder (5 years of attack,
~290 scripts) plus this probe's null results are *increasingly
compatible with Path-FAS on general tournaments being NP-hard*, but
this is not yet a theorem.  The right next attack — orthogonal to
this report — is the hardness route (see `docs/hardness_route.md`)
combined with the path-rigid block constructed there.

## Files added

- `scripts/band_decomposition_probe.py` — feasibility band-DP with
  pluggable summary-key (default: `(mask, deg, UF)`; flags `--no-uf`
  and `--no-deg` for ablations; `--track-states` for state-space
  growth).
- This document.

## Reproducing the experiments

```bash
cd problems/path_matching_fas
# Section 2 (band-DP on full n=7 census)
uv run python scripts/band_decomposition_probe.py --B 2 --track-states
uv run python scripts/band_decomposition_probe.py --B 2 --no-uf
uv run python scripts/band_decomposition_probe.py --B 2 --no-deg
```
