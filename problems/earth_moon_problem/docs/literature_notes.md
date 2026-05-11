# Earth–Moon literature notes

Companion to [docs/plan.md](plan.md). Phase-0 audit deliverable.

## Conventions

Following [problems/pebbling_cartesian_product/docs/literature_notes.md](../../pebbling_cartesian_product/docs/literature_notes.md):

- **Primary** — quoted directly from the cited paper (PDF, arXiv, or DOI page).
- **Secondary (paraphrase)** — paraphrased from a paper or trusted source we read.
- **Repo data** — taken from a code artefact distributed with a paper.
- **User-summary (to verify)** — communicated to the project by a human collaborator
  with knowledge of the source. Promote to primary by direct PDF quote before any
  publication-grade use.

## Notation

- A graph $G$ is **biplanar** when its edge set decomposes as $E(G) = E_1 \sqcup E_2$
  with each $G_i = (V(G), E_i)$ planar. Equivalently, the *thickness* of $G$ is
  at most $2$.
- $\chi_{\rm EM} := \sup\{ \chi(G) : G \text{ biplanar} \}$.

## Kirchweger, Scheucher, Szeider — "SAT-Based Generation of Planar Graphs", SAT 2023

The methodological backbone for the project; tooling reuse vs. reimplementation
is gated on what they shipped and where.

- **Citation.** M. Kirchweger, M. Scheucher, S. Szeider. *SAT-Based Generation of
  Planar Graphs.* In *26th International Conference on Theory and Applications of
  Satisfiability Testing (SAT 2023)*, LIPIcs vol. 271, paper 14, Schloss Dagstuhl,
  2023. DOI: [10.4230/LIPIcs.SAT.2023.14](https://doi.org/10.4230/LIPIcs.SAT.2023.14).
- **Source code (announced in paper).** SAT modulo Symmetries (SMS):
  [github.com/markirch/sat-modulo-symmetries](https://github.com/markirch/sat-modulo-symmetries),
  MIT licensed, C++ + Python.
- **Local pin.** Initial audit inspected mainline at
  `cf890fda5e9da0f749a40b638998bbbf2a1cd092` (`v2.0.0-2-gcf890fd`,
  committed 2025-10-31). **Reproducible Earth–Moon runs pin the local
  clone to tag `v1.0.0`** (commit `2d5a22a3d3b2fcc6f5eeebdfbdbe2031b53ac55b`,
  committed 2024-12-16) plus Patch A from
  [`spike_sms_build.md`](spike_sms_build.md) (a two-line `solveArgs`
  fix in `encodings/planarity.py`). The v2 mainline silently drops
  thickness-2 enforcement, so any solver run there would be uninterpretable
  as Earth–Moon evidence — see the spike doc for the audit.
- **Documentation.** [sat-modulo-symmetries.readthedocs.io](https://sat-modulo-symmetries.readthedocs.io/).

### Abstract — primary

Verbatim from the DROPS landing page:

> To test a graph's planarity in SAT-based graph generation we develop SAT
> encodings with dynamic symmetry breaking as facilitated in the SAT modulo
> Symmetry (SMS) framework. We implement and compare encodings based on three
> planarity criteria. In particular, we consider two eager encodings utilizing
> order-based and universal-set-based planarity criteria, and a lazy encoding
> based on Kuratowski's theorem. The performance and scalability of these
> encodings are compared on two prominent problems from combinatorics: the
> computation of planar Turán numbers and the Earth-Moon problem. We further
> showcase the power of SMS equipped with a planarity encoding by verifying
> and extending several integer sequences from the Online Encyclopedia of
> Integer Sequences (OEIS) related to planar graph enumeration. Furthermore,
> we extend the SMS framework to directed graphs which might be of independent
> interest.

### Encoding details — primary, KSS §5.2 + repo data

The planarity encoding is in mainline SMS at
[`src/graphPropagators/planarity.{hpp,cpp}`](../external/sat-modulo-symmetries/src/graphPropagators/),
with a Python wrapper at
[`encodings/planarity.py`](../external/sat-modulo-symmetries/encodings/planarity.py).
Documented in [`docs/applications.md`](../external/sat-modulo-symmetries/docs/applications.md)
under "Planar graphs, Earth-Moon Problem, planar Turán Numbers and ...".

The SAT 2023 paper described the `v1.0.0` release. **For Earth–Moon
reproductions we pin the local clone to `v1.0.0`**; an inspection of the
`v2.0.0`-mainline clone (`v2.0.0-2-gcf890fd`) showed API drift in
`encodings/planarity.py` and removal of the `--thickness2` CLI flag from
`smsg`'s options — see [`spike_sms_build.md`](spike_sms_build.md) for
the full audit. Use `v1.0.0` for any solver run whose output is meant to
be cited.

**Decomposition representation** (§5.2, page 14:11, primary):

> "Instead of encoding the biplanar graph $G$ directly, we represent the
> decomposition $G_1 \uplus G_2$ as a directed graph $H$ with $\underline{H} = G$.
> $H$ represents the decomposition $G_1 \uplus G_2$ as follows.
> [bullet] $\{u,v\} \in E(G_1)$ if and only if $(u,v) \in E(H)$ and $(v,u) \in E(H)$.
> [bullet] $\{u,v\} \in E(G_2)$ if and only if either $(u,v) \in E(H)$ or
> $(v,u) \in E(H)$, but not both."

**Layer-1 maximal planar WLOG** (§5.2, page 14:11, primary):

> "W.l.o.g., we may assume for a decomposition $G = G_1 \uplus G_2$ that
> $G_1$ is maximal planar, i.e., inserting any additional edge makes the
> graph non-planar, since we can move as many edges as possible from $G_2$
> to $G_1$. We encode this by requiring that $|E(G_1)| = 3n - 6$, hence we
> can also require $|E(G_2)| \le 3n - 6$."

**Criticality** (§5.2, page 14:11, primary):

> "Further, we restrict our search on vertex-critical graphs with respect
> to the chromatic number $\chi$, i.e., deleting any vertex decreases the
> chromatic number of $G$. Hence we can assume that the minimum degree of
> $G$ is $\ge \chi - 1$."

**Chromatic encoding — eager partition-blocking** (§5.2, page 14:12, primary):

> "For ensuring at least a certain chromatic number $\chi$, we add coloring
> clauses ensuring that the underlying graph cannot be colored with
> $\chi - 1$ colors. Let $\mathcal P_n$ be the set of all partitions of $V$.
> Then [eq] ensures that every $(\chi-1)$-coloring is no proper coloring of
> the underlying graph for $\chi - 1 \ge n$, because at least one edge is
> monochromatic. Since the number of partitions $\mathcal P_n$ is exponential,
> this size of the encoding grows exponentially. However, as our experiments
> showed, this approach is still feasible for small values of $n$. We have
> also tried a lazy encoding which adds the clauses incrementally whenever
> there is a violation instead of adding all clauses right at the beginning.
> As it turned out, the results for this version were worse and hence we
> omit the results for the lazy version."

**Best planarity encoding — Kuratowski lazy** (§5.2, page 14:12, primary):

> "Our experiments again show that the Kuratowski-based encoding is superior
> by orders of magnitudes."

The CLI exposes three encodings (`--planar`, `--planar_schnyder`,
`--planar_universal`); per the paper, only Kuratowski is competitive on
Earth–Moon-scale instances.

Three planarity encodings are exposed as command-line flags:

- **Kuratowski (lazy)**: `--planar` on `pysms.graph_builder`, with a propagator
  invoked at frequency $1/5$ (every fifth node in the SAT search; on a positive
  hit a Kuratowski subgraph is extracted and used to generate a blocking clause).
- **Schnyder order (eager)**: `--planar_schnyder` on `encodings/planarity.py`.
- **Universal set (eager)**: `--planar_universal` on `encodings/planarity.py`.

For the Earth–Moon problem specifically, `encodings/planarity.py --earthmoon c`
adds the following automatic constraints (per [`docs/applications.md:166`](../external/sat-modulo-symmetries/docs/applications.md)):

> Automatically, some assumptions are made when using the parameter `--earthmoon c`
>
> - The graph $G_1$ is maximal planar
> - $K_5$ and $K_{3,3}$ are excluded explicitly as subgraph for both $G_1$ and $G_2$.
> - The underlying graph has minimum degree $\geq c - 1$.

The decomposition is encoded on a directed graph (per the abstract's directed-SMS
extension): an antiparallel arc pair encodes a layer-1 edge, a single arc a
layer-2 edge. The thickness-2 layer-2 propagator is enabled with
`--args-SMS " --thickness2 5"`, mirroring the frequency-$1/5$ check on layer 1.

### Earth–Moon results — primary, KSS §5.2 + Tables 3–4

#### Theorem 3 (page 14:12, primary, verbatim)

> "**Theorem 3.** All biplanar graphs on $n \le 13$ vertices are 9-colorable."

So any 10-chromatic biplanar graph has $n \ge 14$. That is the
"$n \le 13$ resolved" claim, fully verified.

#### Table 3 wall-times (page 14:12, primary)

KSS report a 2-day timeout (the caption: "If the timeout of 2 days is
reached we write 't.o.'."). Kuratowski-based encoding times in seconds:

| $n$ | $\chi \ge 9$ #digraph | $\chi \ge 9$ Kura | $\chi \ge 10$ #digraph | $\chi \ge 10$ Kura |
|---|---:|---:|---:|---:|
| 9 | 0 | 0.55 | — | — |
| 10 | 0 | 15.75 | 0 | 1.95 |
| 11 | 5554 | 1709.49 | 0 | 19.03 |
| 12 | — | t.o. | 0 | 837.14 |
| 13 | — | t.o. | 0 | **146 484.00** (≈40.7 h) |

The $n=13$, $\chi \ge 10$ run took ~40.7 h to UNSAT — not 2 days, but
within their cap. Anything we run at $n \ge 14$ is fresh territory.

#### Sulanke's lower bound (page 14:10, primary)

> "In 1973, Thom Sulanke constructed a biplanar graph on 11 vertices with
> chromatic number 9 by removing the edges of a $C_5$ from a $K_{11}$,
> improving an earlier lower bound by Ringel to $\chi_2 \ge 9$."

So: $K_{11} \setminus C_5 = K_6 + C_5$ (since $K_{11}$ minus a 5-cycle is
exactly the join of $K_6$ with $C_5$'s complement-in-$K_5$, and the
complement of $C_5$ in $K_5$ is another $C_5$). Sulanke's date is
**1973**, not 1974 as folklore reports.

#### Candidate1 — $C_5[4,4,4,4,3]$ (page 14:12, primary, verbatim)

> "In the literature, there are some potential candidates for the
> Earth-Moon Problem, which are known to have chromatic number 10, but
> haven't been shown to be biplanar yet [23]. One of these graphs is
> $G = C_5[4,4,4,4,3]$, i.e., a 5-cycle where the first four vertices of
> the cycle are inflated to a 4-clique, and the last to a 3-clique. The
> graph has 19 vertices and 99 edges. We can test whether this graph is
> biplanar using our planarity encodings. This can be done by adding
> constraints that ensure that the underlying graph of the resulting
> directed graph is the graph $G$:
>
> [eq]
>
> By fixing some of the directed edges, SMS is not applicable anymore for
> all permutations. We only allow permuting vertices within the 4-clique
> and 3-clique, respectively, which preserves the underlying graph $G$.
> **Within 12 hours, we are able to show that the graph is not biplanar,
> hence we can exclude the graph as a potential candidate.**"

Our `data/candidate1_calibration/20260510T090120Z` run uses a 43200 s
budget = exactly KSS's reported wall-clock. Apple-silicon SAT typically
beats x86 by ~1.5–2× on instances of this size, so an honest expectation
is UNSAT in under 12 h.

#### Candidate2 — $C_7[K_4]$: not in the paper

The flag `--earthmoon_candidate2` is in
[`encodings/planarity.py:137`](../external/sat-modulo-symmetries/encodings/planarity.py)
and creates the encoding for $C_7[4,4,4,4,4,4,4]$ on 28 vertices. **The
SAT 2023 paper body does not mention `candidate2` anywhere** — no theorem,
no table entry, no remark. Either it was scaffolded post-final and shipped
in the v1.0.0 tag without a result, or KSS attempted it and it timed out
beyond their 2-day cap. Either way, **our Phase 4 headline target is
genuinely open and tooling-ready**.

#### Table 4 — KSS state-of-knowledge map (page 14:13, paraphrased)

For $8 \le n \le 18$, $8 \le \chi \le 13$, KSS classify each cell as
{contains $K_n$ / Sulanke / new (this paper) / open / trivial / blocked}:

- $n \le 13$, $\chi = 10, 11, 12, 13$: closed by KSS ("new").
- $n = 14, 15$: $\chi = 11, 12$ closed; $\chi = 10$ **open**.
- $n = 16, 17$: $\chi = 12$ closed; $\chi = 10, 11$ **open**.
- $n = 18$: $\chi = 12$ closed by a "minimality argument"; $\chi = 10, 11$
  **open**.
- $n = 19$: all of $\chi = 10, 11, 12$ **open**.

The 19-vertex column is exactly where $C_5[4,4,4,4,3]$ sits, and it is
listed as open in the table — the candidate1 result excludes that
*specific* candidate, not the cell.

### Decision: what we fork, imitate, ignore — revised

The candidate-flag discovery flips the architecture:

- **Use SMS directly** for the Phase 4 candidate runs and the Phase 5 joint search.
  Reimplementing a local oracle that competes with `--earthmoon_candidate2`
  would be reproducing KSS line-for-line. Concretely:
  - Run `--earthmoon_candidate2` ourselves on better hardware / with longer
    budgets than the original team likely used. If it terminates UNSAT we have
    a Phase 4 ruling; if it terminates SAT we have a counterexample.
  - Run `--earthmoon` with our own weighted-blowup encodings for the Phase 4
    sweep over $(2r+1, a_1, \dots, a_{2r+1})$.
- **Local lazy-Kuratowski CEGAR** drops to a *secondary verifier*: take any
  positive certificate SMS emits and replay it through `networkx.check_planarity`
  on each layer, in our own Python. Defends against bugs in either codebase.
- **Ignore.** The Schnyder-order and universal-set planarity encodings — KSS
  found Kuratowski faster.

### Resolved / remaining

Resolved with primary quotes from the SAT 2023 PDF:

- Planarity encodings live in mainline `main`, tagged `v1.0.0`. Not a branch.
- Earth-Moon-specific encoding is exposed at the CLI.
- Theorem 3 says all biplanar graphs on $n \le 13$ are 9-colourable. (The
  $\chi \ge 10$ search is UNSAT for $n \le 13$; for $n \ge 14$ the cell
  status comes from Table 4.)
- Candidate1 wall-clock: "Within 12 hours" (page 14:12, verbatim) — UNSAT
  on $C_5[4,4,4,4,3]$.
- Candidate2 ($C_7[K_4]$) is in the code, **absent from the paper body**
  (no theorem, no table entry, no remark). Tooling-ready, result open.

Remaining (low priority, not blocking Phase 4):

- Sulanke's original 1973 reference (KSS cite [22]); Gardner 1980 is the
  popularised report.
- The "minimality argument" KSS use to close $n = 18$, $\chi = 12$ —
  presumably elsewhere in §5.2 or an extended version. Worth chasing if
  Phase 6 (upper-bound route) becomes the focus.

(Build prerequisites and host status are in
[`spike_sms_build.md`](spike_sms_build.md), not duplicated here.)

## Boutin, Gethner, Sulanke — 2008

*Placeholder.* To collect from the published version: full title, journal,
volume/pages, exact statement of which 9-critical thickness-2 graphs they
construct, the count by graph order, and any computer-search documentation.
First pass via [DBLP](https://dblp.org/pid/23/4366).

## Gethner, Sulanke — 2009

*Placeholder.* Infinite family of 9-critical thickness-2 graphs. Collect the
exact parametric construction and the smallest member by order, since both
are needed as regression inputs to the Phase 1 oracle.

## Catlin / Gethner clique-blowup line

*Placeholder.* Original Catlin reference for clique blowups of odd cycles as
chromatic-extremal graphs; Gethner's deployment of blowups in the Earth–Moon
context. Used as the construction template behind Phase 4.

## Kostochka, Yancey — 2014

- **Citation.** A. V. Kostochka, M. Yancey. *Ore's conjecture for $k = 4$ and
  Grötzsch's theorem.* *Combinatorica* 34 (2014), 781–797. The general $k$-critical
  density bound is in their companion paper *Density of $k$-critical graphs*
  ([arXiv:1209.4255](https://arxiv.org/abs/1209.4255)), JCTB 2014.
- **Statement — paraphrase, to verify against PDF.** Every $k$-critical graph $G$
  on $n$ vertices satisfies
  $$|E(G)| \ge \frac{(k+1)(k-2)}{2(k-1)} n - \frac{k(k-3)}{2(k-1)}.$$
- **Specialisation $k = 12$.** $|E(G)| \ge (65 n - 54)/11$.
- **Earth–Moon application.** Combined with $|E(G)| \le 6n - 12 = (66 n - 132)/11$,
  the inequalities are jointly satisfiable only for $n \ge 78$. A density
  strengthening exploiting $K_9$-freeness closes $\chi_{\rm EM} \le 11$ only if
  it beats the remaining gap:
  $$6n - 12 - \frac{65n - 54}{11} = \frac{n - 78}{11}.$$
  Thus the target is an improvement over Kostochka–Yancey of more than
  $(n-78)/11$ edges; asymptotically, an arbitrary $c n$ term is not enough
  unless $c \ge 1/11$ up to lower-order constants. This is the Phase 6 target.

## Mansfield — 1983

- **Citation.** A. Mansfield. *Determining the thickness of graphs is NP-hard.*
  *Math. Proc. Camb. Phil. Soc.* 93 (1983), 9–23.
- **Implication.** Biplanarity testing is NP-hard, so polynomial-time oracle is
  off the table. Justifies the SAT-based approach in Phase 1.

## Hutchinson — 1993

- **Citation.** J. P. Hutchinson. *Coloring ordinary maps, maps of empires and
  maps of the moon.* *Math. Mag.* 66 (1993), 211–226.
- **Use.** Survey / framing reference; not load-bearing.

## Sulanke / Gardner — 1973/1980

- **Construction.** The graph $K_{11} \setminus C_5 = K_6 + C_5$ (the join
  of $K_6$ with $C_5$) is biplanar with $\chi = 9$, witnessing
  $\chi_{\rm EM} \ge 9$. KSS 2023 (page 14:10) date Sulanke's construction
  to **1973** (citing their ref [22]), correcting the folklore "1974"
  attribution. Popularised by Gardner in *Sci. Amer.* 242 (1980), 14–22.

## Heawood — 1890

- **Citation.** P. J. Heawood. *Map Colour Theorems.* *Quart. J. Pure Appl. Math.*
  24 (1890), 332–338. Source of the upper bound $\chi_{\rm EM} \le 12$ via
  $\delta(G) \le 11$ and induction.
