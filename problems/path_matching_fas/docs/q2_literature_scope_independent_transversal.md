# Q2 literature scope: independent transversals and matroid-constrained hitting

This note scopes the next literature pass after the Q1 polynomial result and
the Q2 reduction in `q2_nonforward_attack.md`.

The target problem is:

> Given a tournament `T`, does there exist a linear forest `F ⊆ A(T)` hitting
> every directed 3-cycle and directed 4-cycle of `T`?

Equivalently, choose an edge set that is independent in the graphic matroid,
satisfies the degree-2 caps, and covers a polynomial family of 3/4-uniform
hyperedges.  The useful literature keywords are **not** just "matroid
intersection"; they are:

```text
matroid-constrained hitting set
matroid-constrained maximum coverage
matroid intersection cover
rainbow independent sets
independent transversals
representative families for matroid intersections
linear matroid parity / graphic matroid parity
```

## 1. Exact abstraction

Let

```text
E = A(T)
H = {arc-sets of directed 3-cycles and directed 4-cycles}
I = {F ⊆ E : underlying undirected graph of F is a linear forest}.
```

Then Q2 asks whether there is `F ∈ I` such that

```text
F ∩ C ≠ ∅     for every C ∈ H.
```

Two modelling warnings:

1. `I` is not a matroid.  It is the intersection of the graphic matroid
   (forest) and degree-2 constraints, and this intersection is not a matroid.
   If a paper requires one matroid independence oracle, the closest relaxation
   is "forest" alone; the degree caps must then be restored separately.
2. This is **hitting**, not a standard rainbow transversal.  A selected arc can
   hit many directed cycles.  In a rainbow/ISR formulation, each block usually
   contributes a distinct representative.  Cloning one arc per cycle-arc
   incidence destroys the shared-choice economy unless the formulation also
   enforces equality across clones, which is exactly the hard part.

## 2. Literature clusters to mine

### A. Matroid-constrained maximum coverage / set cover

Why it matters: Q2 is the decision version of covering all 3/4-cycles by an
independent set.  The coverage function

```text
f(F) = number of directed 3/4-cycles hit by F
```

is monotone submodular.  The exact question is whether

```text
max { f(F) : F is a linear forest } = |H|.
```

Known direction from the pass:

* Matroid-constrained maximum coverage is usually treated as approximation or
  FPT approximation, not exact polynomial feasibility.  For example, Sellier's
  ESA 2023 paper studies maximizing a coverage function over an independent
  set of a matroid and gives parameterized approximation machinery under
  bounded frequency.  That is close in flavour, but Q2 needs exact full
  coverage and the rank is `Θ(n)`, so generic parameterized algorithms are not
  polynomial here.

Questions to extract:

* Is there an exact polynomial island for full coverage when hyperedges have
  size at most 4 and the matroid is graphic or graphic ∩ partition?
* Do bounded-frequency results become relevant for near-transitive tournaments?
  In Q2 the *hyperedges per arc* can still be `Θ(n^2)` for 4-cycles, so
  bounded frequency probably fails.
* Are there min-max/Farkas-style certificates for "no independent set covers
  all elements" stronger than the fractional LP already tested?

Verdict before deeper reading: useful for approximation language and possible
duality certificates; unlikely to directly prove `P`.

### B. Matroid intersection cover / matroid partitioning

Why it matters: "cover by independent sets" is a classical matroid-cover
problem, and matroid intersection cover is the natural two-matroid extension.

Known direction from the pass:

* Im, Moseley, and Pruhs define matroid intersection cover as covering the
  ground set by sets independent in each of `k` matroids.  They give constant
  approximation algorithms for standard matroids, but the exact problem is not
  generally polynomial.  Their introduction records that for one matroid the
  cover problem is polynomial via Edmonds-style matroid partitioning, while
  the `k ≥ 3` version is NP-hard even for partition matroids.

Mismatch with Q2:

* Matroid intersection cover covers **elements of the matroid ground set** by
  several independent sets.  Q2 chooses **one** independent set of arcs that
  covers a separate universe of directed cycles.  That is the dual direction.
* Still, the partition-decomposition machinery may suggest a way to decompose
  the directed-cycle universe into boundedly many tractable layers.  This is
  the angle to check, not the headline theorem.

Questions to extract:

* Does their partition-decomposition idea produce exact results when only one
  independent set is allowed and the covered objects are hyperedges?
* Are there constructive versions of the non-constructive "cover number of an
  intersection of two matroids" bounds that imply a small family of candidate
  forests?
* Can Q2 be reframed as a cover problem over the **dual graphic matroid** or a
  matroid union/partition instance?

Verdict before deeper reading: probably not directly applicable, but it is the
most relevant "matroid + cover" paper family to mine for terminology and
duality tricks.

### C. Independent transversals / rainbow independent sets

Why it matters: The superficial formulation is "for each directed cycle,
choose one arc, and the chosen arcs should form a linear forest."

Known direction from the pass:

* Haxell-type independent transversal results concern choosing one vertex from
  each block while remaining independent in a conflict graph, often giving
  either an independent transversal or a structural obstruction.
* Rainbow matroid results, e.g. Aharoni-Kotlar-Ziv, study partial rainbow sets
  independent in matroids or in the intersection of two matroids.

Mismatch with Q2:

* Standard rainbow/ISR choices are essentially injective at the block level.
  Q2 needs shared representatives: the same selected arc may cover hundreds of
  cycles.  Forcing distinct representatives would change the problem and
  instantly exceed the `n-1` edge budget.
* Therefore this cluster is only useful if it contains a version with
  non-injective choices, domination, or "one independent set meeting every
  member of a set family."

Questions to extract:

* Is there a "matroidal Hall theorem" for one independent set intersecting
  every member of a family, not choosing distinct representatives?
* Do topological Hall theorems for simplicial complexes yield checkable
  obstructions for the independence complex of a graphic matroid intersected
  with degree caps?
* Can the Q2 cycle family be made disjoint or laminar after quotienting
  near-transitive structure? If not, rainbow methods are a red herring.

Verdict before deeper reading: high risk of abstraction mismatch.  Read only
for obstruction/certificate machinery, not expecting a direct algorithm.

### D. Matroid parity and graphic matroid parity

Why it matters: The obstruction is selected forest topology; parity/matching
problems are the main place where graphic-matroid independence supports
nontrivial polynomial algorithms beyond intersection.

Known direction from the pass:

* Linear matroid parity is polynomial for linearly represented matroids
  (Lovasz; modern weighted algorithms by Iwata and Kobayashi).
* Graphic matroid parity has special min-max structure and is closely tied to
  packing paired edges while keeping a forest.

Mismatch with Q2:

* Q2 constraints are 3/4-ary covering constraints, not paired choices.  Turning
  every directed cycle into a small gadget of paired choices would need a
  parsimonious reduction preserving "one shared arc covers many cycles."

Questions to extract:

* Can the directed 3/4-cycle hypergraph of a tournament be represented as a
  parity instance over a linear/graphic matroid after adding auxiliary
  elements?
* Are there "matroid parity with covering constraints" results, and are they
  immediately hard?
* Does the D70 toggle family embed a matroid-parity-hard structure, suggesting
  a hardness route rather than a `P` route?

Verdict before deeper reading: this is the most plausible source of a genuinely
new algorithmic primitive, but only if the cycle constraints admit a paired or
linear representation.  Otherwise it becomes another hardness analogy.

### E. Representative families for matroid intersections

Why it matters: Q2 on the Q1 prefix DAG is a path problem with accumulated
graphic-matroid independence.  Representative families are the standard way to
compress partial solutions under a matroid independence constraint.

Known direction from the pass:

* Representative-family algorithms give strong FPT/exact exponential
  algorithms for paths, packing, covering, and matroid intersections,
  especially for linear matroids.

Mismatch with Q2:

* The graphic matroid rank here is `n-1`, not a small parameter.  Generic
  representative-family sizes are exponential in rank, so this recreates the
  D70 forward-state barrier unless the tournament/Q1 structure gives a new
  rank reduction.

Questions to extract:

* Are there representative-family bounds depending on branchwidth/pathwidth of
  the matroid representation rather than rank?
* Does the Q1 diameter bound imply that the relevant label sets live in a
  bounded-rank projection at each layer?
* Can D70 be restated as a lower bound against representative-family
  compression on the natural graphic matroid?

Verdict before deeper reading: probably yields an XP/FPT-style algorithm, not
polynomial, unless a structural rank collapse is found.

## 3. Go/no-go checklist

For each paper, record answers to these exact questions.

| Question | Why it matters |
|---|---|
| Does the result choose one independent set, or cover by many independent sets? | Q2 needs one selected forest. |
| Are representatives distinct/injective? | Q2 needs shared arc choices. |
| Is the independence system one matroid, two matroids, or graphic ∩ degree? | Linear forests are not a matroid. |
| Is the guarantee exact, approximation, or FPT in rank/solution size? | Q2 needs exact polynomial with rank `Θ(n)`. |
| Are hyperedges bounded-size and overlapping allowed? | Q2 has 3/4-edges with heavy overlap. |
| Is there a min-max obstruction certificate? | Could give a new NO proof system. |
| Does the result survive on graphic matroids specifically? | Forest topology is the real constraint. |
| Does it allow lower-bound covering constraints, not only upper-bound independence constraints? | This is the central algebraic mismatch. |

## 4. Priority reading list

1. **Im, Moseley, Pruhs — "The Matroid Intersection Cover Problem."**
   Read for matroid-cover decomposition, exact-vs-approx boundary, and
   whether any dual formulation resembles Q2.
2. **Graf & Haxell — "Finding independent transversals efficiently."**
   Read for algorithmic obstruction certificates from failed independent
   transversals.  Treat direct applicability as unlikely because Q2 is
   non-injective hitting.
3. **Aharoni, Kotlar, Ziv — "Rainbow sets in the intersection of two
   matroids."**  Read for rainbow/intersection language and the exact point
   where disjoint/injective representatives enter.
4. **Iwata, Kobayashi — "A Weighted Linear Matroid Parity Algorithm."**
   Read for whether parity formulations can absorb small covering constraints.
5. **Fomin, Lokshtanov, Panolan, Saurabh and follow-ups on representative
   families.**  Read only after deciding whether a rank/pathwidth collapse is
   plausible; otherwise it is another exponential-in-rank framework.
6. **Matroid-constrained maximum coverage / submodular maximization under a
   matroid constraint.**  Read for certificate and kernel ideas, not expecting
   exact polynomial feasibility.

## 5. Seed references checked

These are not endorsements as applicable theorems; they are the first papers
to read because they sit closest to the abstraction.

| Cluster | Reference | Initial relevance |
|---|---|---|
| Matroid intersection cover | Im, Moseley, Pruhs, "The Matroid Intersection Cover Problem," Operations Research Letters 2020, `https://www.contrib.andrew.cmu.edu/~moseleyb/papers/2020-ORL-matroid-cover.pdf` | Defines the closest "matroid + cover" family; mostly covers by many independent sets, so likely dual/mismatched. |
| Independent transversals | Graf, Haxell, "Finding independent transversals efficiently," Combinatorics, Probability and Computing 2020, DOI `10.1017/S0963548320000127` | Gives algorithmic ISR-or-obstruction output; likely mismatched because Q2 allows shared representatives. |
| Rainbow matroids | Aharoni, Kotlar, Ziv, "Rainbow sets in the intersection of two matroids," arXiv:1405.3119 | Useful for rainbow/intersection vocabulary; explicit partial choice-function model highlights the injectivity issue. |
| Matroid parity | Iwata, Kobayashi, "A Weighted Linear Matroid Parity Algorithm," arXiv:1905.13371 | Best candidate for a genuinely different algebraic primitive; only relevant if 3/4-cycle covering can be encoded as paired choices. |
| Representative families | Fomin, Lokshtanov, Panolan, Saurabh, "Efficient Computation of Representative Sets...", arXiv:1304.4626 | Gives matroid compression for paths/packing; probably exponential in rank here. |
| Representative families for intersections | van Bevern, Tsidulko, Zschoche, "Representative families for matroid intersections...", Discrete Applied Mathematics 2021, DOI `10.1016/j.dam.2021.03.014` | Covers set packing/covering with multiple matroid constraints in FPT regimes; mine for rank/pathwidth dependence. |
| Matroid-constrained maximum coverage | Sellier, "Parameterized Matroid-Constrained Maximum Coverage," ESA 2023, DOI `10.4230/LIPIcs.ESA.2023.94` | Shows the modern bounded-frequency/FPT-AS framing for coverage over a matroid. |

## 6. Expected outcomes

The literature pass should aim for one of three concrete outputs:

1. **Positive target.**  A theorem whose hypotheses almost match Q2, leaving a
   small tournament-specific lemma to prove.
2. **Hardness target.**  A known hard matroid-constrained-covering problem that
   can plausibly be encoded as directed 3/4-cycles in a tournament while
   preserving a linear-forest transversal.
3. **Certificate target.**  A min-max or topological obstruction theorem that
   produces polynomially checkable NO certificates for the acyclicity-core.

If none of these appear, the honest conclusion is that "independent
transversal" is mostly a false friend, and the next research move should be
either a tournament-specific structural theorem for the 3/4-cycle hypergraph
or an NP-hardness reduction into that hypergraph.

## 7. Reviewer addendum (2026-06-01): citations verified, angles re-weighted

Independent review of this scope note.  The central "false friend" call is
**correct**: Q2 is matroid-constrained *hitting* (one forest, arcs shared
across cycles), not an injective ISR/rainbow transversal.

**Citations spot-checked (vs arXiv / DOI):** Iwata–Kobayashi parity
(arXiv:1905.13371, SIAM J. Comput. 51 (2022)) ✓; Sellier ESA 2023
(arXiv:2308.06520) ✓; "Finding Independent Transversals Efficiently" =
**Graf & Haxell**, CPC 29(5) 2020, arXiv:1811.02687 ✓ (priority-list author
fixed). Im–Moseley–Pruhs and the representative-family refs not independently
re-verified (assessed as mismatched anyway).

**Re-weighting of the angles:**

- **Cluster E (representative families) is not "probably exponential" — it is
  PROVABLY so here, by D70.** D70 is exactly a `2^Ω(n)` lower bound against
  forward compression of the back-arc-forest (graphic-matroid) state, and the
  Q1 diameter bound compresses the prefix *set* but gives **no rank collapse**
  (the back-arc forest still has rank `Θ(n)`). So every DP / forward /
  representative-family / bounded-bandwidth route is dead absent a
  tournament-specific rank collapse that D70 says does not exist on the
  Δ\*=2 toggle family. Treat cluster E as closed, not "XP-maybe".

- **Cluster D (parity) is OVER-weighted.** Matroid parity solves
  pairing/perfect-matching-type problems; Q2's constraints are covering
  *disjunctions* (`≥1 of 3`, `≥1 of 4`), which parity does not natively
  encode. "Covering ≠ parity" is a structural, not cosmetic, gap. Demote to a
  long shot unless a genuine pairing structure is exhibited.

- **Cluster A/B (matroid coverage / intersection cover) — agree:**
  approximation / multi-set-cover, wrong shape (exact full coverage by ONE
  independent set). Mine only for duality/certificate language.

**The realistic next moves (sharper than §6's three options):**

1. **coNP certificate (most tractable, may not need P).** The honest near-term
   win is a polynomially-checkable NO-certificate for the acyclicity-core, not
   a P algorithm. The cutting-plane audit (D91) already attempted this and
   found the cycle-cut LP fractional on NOs; a *min-max / topological-Hall*
   obstruction for "no linear forest hits all 3/4-cycles" would be new and is
   the lowest-risk target. Pair with the §9 cycle-count NO-certificate
   (`q2_nonforward_attack.md`).

2. **Expressiveness dichotomy (decides P vs hardness — NEW, concrete).** The
   session's hardness reductions all failed on *expressiveness*: tournament
   directed cycles cannot encode arbitrary structure. So the decisive question
   is: **which 3/4-uniform hypergraphs arise as the directed-3/4-cycle
   hypergraph of a tournament?** If that class is expressive enough to embed a
   known NP-hard matroid-constrained hitting-set instance (preserving a
   linear-forest transversal), Path-FAS is NP-hard; if it is structurally
   restricted (e.g. bounded VC dimension, laminar/interval after score-window
   quotient), that restriction is the handle for P. This is the cleanest
   undecided fork and is independent of the matroid literature.

3. **Disjoint-path-transversal framing (minor, new).** `F` is a forest of
   max-degree 2 = a set of vertex-disjoint *paths*. So Q2 = "do vertex-disjoint
   paths exist hitting every directed 3/4-cycle?" — a disjoint-paths /
   path-cover transversal, a different (flow/matching-adjacent) primitive than
   the matroid framings; worth a separate small probe.

**Net:** the literature pass confirms "independent transversal" is a false
friend and that no off-the-shelf theorem matches. The two genuinely live
directions are a coNP min-max certificate and the 3/4-cycle-hypergraph
expressiveness dichotomy; the matroid-coverage / parity / representative-family
clusters are either shape-mismatched (A,B,C,D) or D70-dead (E).
