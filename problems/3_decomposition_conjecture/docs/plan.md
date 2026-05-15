# 3-Decomposition Conjecture — attack plan

## Statement

Hoffmann-Ostenhof (2011, posted to OPG 2017-01-24, Arthur):

> Every connected cubic graph $G$ has a decomposition
> $E(G) = T \sqcup C \sqcup M$,
> where $T$ is a spanning tree, $C$ is a 2-regular subgraph
> (vertex-disjoint union of cycles), and $M$ is a matching. Both $M$ and $C$
> may be empty in the syntactic statement.

Throughout: $G$ is simple, connected, 3-regular on $n$ vertices ($n$ even),
with $|E| = 3n/2$ and cotree size $n/2 + 1$.

## Vertex-type reformulation (sharp consequences)

For any valid decomposition $(T, C, M)$ and any $v \in V(G)$,
$\deg_T(v) + \deg_C(v) + \deg_M(v) = 3$ with $\deg_C(v) \in \{0,2\}$ and
$\deg_M(v) \in \{0,1\}$. Since $T$ spans, $\deg_T(v) \ge 1$, so every vertex
falls in exactly one of three classes:

| Type | $\deg_T$ | $\deg_C$ | $\deg_M$ |
|---|---:|---:|---:|
| $V_C$ — on a cycle, $T$-leaf | 1 | 2 | 0 |
| $V_M$ — matched, $T$-internal | 2 | 0 | 1 |
| $V_T$ — pure tree vertex | 3 | 0 | 0 |

Let $a = |V_C|$, $b = |V_M|$, $c = |V_T|$. Counting vertices and incidences:

$$a + b + c = n, \qquad a + 2b + 3c = 2(n-1).$$

Subtracting twice the first from the second gives $b + 2c = n - 2$, and then

$$\boxed{a = c + 2}.$$

So the number of cycle-leaves exceeds the number of pure tree vertices by
exactly 2. In particular $a \ge 2$, and because cycles in a simple graph
need length $\ge 3$, in fact $a \ge 3$ and $c \ge 1$. Equivalently: the
cotree has $n/2 + 1$ edges; a matching has at most $n/2$ edges; so
**$C$ is never empty in a connected cubic graph** — it contains at least one
cycle, and $T$ has at least one degree-3 vertex.

Choosing a valid decomposition is equivalent to choosing a vertex partition
$V = V_C \sqcup V_M \sqcup V_T$ together with a 2-factor of $G[V_C]$ and a
perfect matching of $G[V_M]$ (under suitable edge-availability conditions),
such that the remaining $n-1$ edges form a spanning tree. *The minimum
degree of $G[V_C]$ being $\ge 2$ is necessary for $G[V_C]$ to admit a
2-factor; it is not sufficient.*

This vertex-typing is the same reformulation underlying Zhang–Szeider's
SAT propagators (CP 2025) and Bachtler–Krumke's "good matching" framework
(EJC 2022).

## Bridges and minimal-counterexample structure

Let $e = uv$ be a bridge of $G$. Then $e \in T$ in every decomposition:

- $e \in C$ is impossible because cycle edges lie on a cycle but $e$ is a
  bridge;
- $e \in M$ would force $T \setminus \{e\} = T$ to contain no $u$-$v$ path
  (the bridge separates $u, v$ even in $G$, hence in $T$), so $T$ would be
  disconnected — contradiction;
- therefore $e \in T$.

**Bridge boundary states.** Let $G$ be connected cubic, $e = uv$ a bridge,
$G_u, G_v$ the components of $G - e$ rooted at $u, v$. In $G_u$ the root
$u$ has degree 2.

Because $T$ is a spanning tree of $G$ and $e \in T$, $T \setminus \{e\}$
has exactly two components whose vertex sets are $V(G_u)$ and $V(G_v)$.
Hence $T_u := T \cap E(G_u)$ is a *spanning tree of $G_u$*, and in
particular $\deg_{T_u}(u) \ge 1$. This rules out the would-be
"tree-detached" state ($\deg_{T_u}(u) = 0$): at a bridge root,
$u \in V_C$ is impossible, because that would force the single $T$-edge at
$u$ in $G$ to be $e$ and leave $T_u$ missing the vertex $u$.

So the **bridge-root state is one of exactly two**, mirroring the two
full-graph types compatible with $e \in T$ at $u$:

| Full-$G$ type at $u$ | Edges at $u$ in $G_u$ | Restricted state |
|---|---|---|
| $V_T$ ($\deg_T = 3$) | both in $T_u$ | "tree-internal": $\deg_{T_u}(u) = 2$, $\deg_{C_u}(u) = \deg_{M_u}(u) = 0$ |
| $V_M$ ($\deg_T = 2$, $\deg_M = 1$) | one in $T_u$, one in $M_u$ | "tree-leaf-matched": $\deg_{T_u}(u) = 1$, $\deg_{M_u}(u) = 1$, $\deg_{C_u}(u) = 0$ |

The bridge reduction is *not* a standalone-decomposition problem on $G_u$;
it is a **boundary-traced decomposition** problem with the root state
fixed to one of the two options. This is the template-trace formalism of
Bachtler–Heinrich / Zhang–Szeider applied at the bridge boundary.

**Bridge-reduction lemma (to formalise in `scripts/reductions.py`).**
$G$ admits a 3-decomposition iff for some pair of root states
$(s_u, s_v) \in \{\text{tree-internal}, \text{tree-leaf-matched}\}^2$,
$G_u$ admits a boundary-traced decomposition with root state $s_u$ and
$G_v$ admits one with root state $s_v$. The $2 \times 2 = 4$ pairs each
have to be handled explicitly.

**Aboomahigir–Ahanjideh–Akbari (DAM 296, 2021)** address subcubic
decompositions in this regime, but their statements need to be matched to
the two bridge-root states above before being invoked.

**2-edge-cuts.** Let $F = \{e_1, e_2\}$ be a 2-edge-cut with sides $A, B$.
The edge-type pair $(t(e_1), t(e_2)) \in \{T, C, M\}^2$ gives nine cases,
constrained by: $(C, C)$ on its own creates a length-2 path in $C$ at each
endpoint, which is fine inside a cycle only if the two endpoints on each
side are joined inside that side by a $C$-path; $(C, T)$ and similar
mixed cases place a cycle endpoint at a $T$-attachment; etc. The full
table of nine cases × four root states per side is not yet written down
in our notation; **until it is, "2-edge-cut reduces" is not a
theorem-producing dependency here.** Bachtler–Heinrich establish enough
of it to settle tree-width $\le 3$ / path-width $\le 4$ for 3-connected
inputs, but the missing piece is precisely the reduction from
2-edge-connected (but not 3-edge-connected) to 3-edge-connected for the
*general* conjecture. This is a Phase 5 lemma target, not a given.

**Vertex 2-cuts.** A 2-vertex-cut $\{u, v\}$ is the *vertex* analogue and
is even more delicate; Bachtler–Heinrich's strong consequences (girth,
tree-width, embedded surfaces) are proved for **3-vertex-connected**
inputs. Reducing the general cubic conjecture to the 3-connected case via
2-vertex-cut surgery is **open in our pipeline**. Until it is written
down, every consequence below labelled "3-connected" must be read as
conditional on $G^\star$ being 3-vertex-connected.

**Provisional consequence: a minimal counterexample is bridgeless
(equivalently, 2-edge-connected).** Bridge reduction gives exactly this
and no more. Anything stronger — 3-edge-connectedness via 2-edge-cut
reduction, 3-vertex-connectedness via 2-vertex-cut reduction, girth /
surface exclusion / tree-width lower bound (which are stated only for
3-vertex-connected inputs in the literature) — is *conditional* until we
prove the 2-edge-cut and 2-vertex-cut reductions ourselves (Phase 5.0).

## Known partial results (as of 2026-05)

(Where the same class has been proved twice independently, both are
listed; only the earliest credited statement is named in body text.)

| Class | Result | Reference |
|---|---|---|
| Hamiltonian cubic | proved | credited in standard surveys to Akbari et al.; **citation to be verified in Phase 1** before use |
| Traceable cubic (Hamiltonian path) | proved | derived from the Hamiltonian argument; recorded in Bachtler–Heinrich §2 |
| Connected planar | proved | Hoffmann-Ostenhof, Kaiser, Ozeki, *J. Graph Theory* 88(4) (2018) |
| 3-connected plane (planar embedded) | proved | Ozeki, Ye, *Electron. J. Combin.* 23(4) #P4.6 (2016) |
| 3-connected projective-plane embedded | proved | Ozeki, Ye, EJC 2016 (same paper) |
| 3-connected torus / Klein-bottle embedded | proved | Bachstein, *3-decompositions of surface graphs*, M.Sc. thesis, TU Wien, 2015 |
| 3-connected, tree-width $\le 3$ | proved | Bachtler–Heinrich, arXiv:2104.15113 (2021) |
| 3-connected, path-width $\le 4$ | proved | Bachtler–Heinrich, arXiv:2104.15113 (2021) |
| 2-factor consisting of three cycles | proved | Xie, Zhou, Zhou, *Discrete Math.* 343 (2020) 111839 |
| 3-connected star-like (contracted 2-factor is a star) | proved | Bachtler–Krumke, *Electron. J. Combin.* 29(4) #P4.23 (2022) |
| Claw-free cubic | proved (independently) | Ahanjideh–Aboomahigir, arXiv:1810.00074 (2018); Hong–Liu–Yu (independent; published version to locate) |
| Claw-free subcubic & 4-chordal subcubic | proved | Aboomahigir, Ahanjideh, Akbari, *Discrete Applied Math.* 296 (2021) |
| Near-decomposition with bounded $P_2$ count | proved | Fan, Zhou, *Discrete Math.* 348 (2025) 114454; Fan, Guo, Zhou, *Sci. China Math.* (2025) — these papers must be obtained and audited before reuse |
| All connected cubic with $n \le 28$ | computationally verified | Zhang, Szeider, *CP 2025*, LIPIcs vol. **340** paper 39; specialised propagators integrated in SAT-Modulo-Symmetries (SMS); roughly 4.0 CPU-years for $n = 28$ |

Fan and Zhou's introduction is the most compact and current survey; treat
it as the reference checklist while reading the underlying papers.

## What we know about a minimal counterexample $G^\star$

Two layers, separated by what reductions we can actually prove.

**Unconditional (from results that apply to all connected cubic graphs):**

- $G^\star$ is **bridgeless** (equivalently, 2-edge-connected) — bridge
  reduction above. Stronger edge-connectivity (3-edge-connected) waits on
  the 2-edge-cut reduction (Phase 5.0);
- $G^\star$ is **not Hamiltonian** and **not traceable**;
- $G^\star$ is **not planar** (Hoffmann-Ostenhof–Kaiser–Ozeki applies to *all*
  connected planar cubic graphs);
- $G^\star$ contains an induced **$K_{1,3}$** (claw-free cubic is settled);
- $G^\star$ has **no 2-factor consisting of exactly three cycles**
  (Xie–Zhou–Zhou's theorem is stated for connected cubic graphs);
- $|V(G^\star)| \ge 30$ (Zhang–Szeider).

**Conditional on $G^\star$ being 3-vertex-connected** (the partial results
below are stated for the 3-connected class; until we close the
2-vertex-cut reduction, treat these as: "if $G^\star$ is 3-connected, then…"):

- not embeddable in the projective plane, torus, or Klein bottle;
- tree-width $\ge 4$, path-width $\ge 5$;
- girth $\ge 4$ (triangle-free), via Bachtler–Heinrich's triangle
  reduction for 3-connected inputs;
- no 2-factor of the form "star-like contraction" (Bachtler–Krumke).

Closing the 2-vertex-cut reduction is the highest-leverage internal
deliverable: it upgrades every conditional bullet above to unconditional.

This is the working "shape" of $G^\star$. The conditional list collapses
to unconditional only after the 2-vertex-cut reduction lemma is in place.

## Two-track plan

The plan has two parallel tracks that exchange artefacts.

**Track A — computational theorem-search.** Reproduce and extend
Zhang–Szeider exactly, ingest their reducible-template library, build a
verifier for template-compatibility, and search for new templates beyond
their bounds.

**Track B — minimal-counterexample structural theory.** Sharpen the
$G^\star$ shape above: turn each row of the list into a free-standing
lemma in our own notation; look for the next forced property.

Each new reducible template (Track A) becomes a new row in the $G^\star$
shape (Track B). Each new structural restriction on $G^\star$ (Track B)
prunes the Track A search space.

A discharging argument is *not* a phase in this plan. Generic cubic graphs
have no Euler-characteristic charge reservoir; the 4CT-style mechanism is
not available without an embedding or a different global potential. If
discharging is to play any role it will be planar-conditional (already
settled) or charge-on-a-different-invariant (currently aspirational); we
do not commit compute to it.

## Phase 1 — literature lockdown (1–2 weeks)

Mandatory primary documents, in priority order. Each gets a brief in
`docs/literature_notes.md` with one-line statements of every result used
elsewhere.

1. Zhang, Szeider, *The 3-Decomposition Conjecture: A SAT-Based Approach
   with Specialized Propagators*, CP 2025, LIPIcs **vol. 340** paper 39.
   Also pull their **Zenodo artifact** with reducible templates and CNF
   encodings.
2. Bachtler, Heinrich, *Reductions for the 3-Decomposition Conjecture*,
   arXiv:2104.15113 (2021). Full reduction list with proofs;
   tree-width / path-width arguments; embedded-surface cases.
3. Bachtler, Krumke, *Towards Obtaining a 3-Decomposition From a Perfect
   Matching*, EJC 29(4) #P4.23 (2022). The "good matching" formalism, the
   star-like 2-factor result.
4. Fan, Zhou, *Hoffmann-Ostenhof's 3-Decomposition Conjecture*, Discrete
   Math. 348 (2025) 114454. *Obtain via interlibrary loan; ScienceDirect
   returns 403 for the local fetcher.*
5. Fan, Guo, Zhou, *The 3-decomposition conjecture of cubic graphs*,
   Sci. China Math. (2025), DOI 10.1007/s11425-025-2498-x. *Same access
   action.*
6. Xie, Zhou, Zhou, *Decomposition of cubic graphs with a 2-factor
   consisting of three cycles*, Discrete Math. 343 (2020) 111839.
7. Aboomahigir, Ahanjideh, Akbari, *Discrete Applied Math.* 296 (2021),
   claw-free / 4-chordal subcubic.
8. Ahanjideh, Aboomahigir, arXiv:1810.00074 (2018), claw-free cubic;
   Hong, Liu, Yu (independent claw-free) — locate the published version.
9. **Hamiltonian cubic — citation audit.** Standard surveys credit
   Akbari et al. for this case; we have not yet verified the canonical
   reference. Track down the published version (likely Akbari, Jensen, or
   Akbari, Maimani et al.) and read end-to-end before relying on it
   anywhere else in the plan.
10. Hoffmann-Ostenhof, Kaiser, Ozeki, *J. Graph Theory* 88(4) (2018) —
    connected planar.
11. Ozeki, Ye, *Electron. J. Combin.* 23(4) #P4.6 (2016) — 3-connected
    plane and projective-plane.
12. Bachstein, M.Sc. thesis, TU Wien (2015) — 3-connected torus / Klein
    bottle. Obtain a copy from TU Wien's repository.

The literature pass produces three artefacts:

- a markdown table of all reducible configurations in print, with the
  exact boundary trace each one resolves;
- a markdown table of all settled classes with one-line proofs sketched;
- a JSON file `data/known_templates.json` listing (graph6, boundary,
  reduction kind, source).

## Phase 2 — decision oracle (replication, not invention)

The oracle is `has_3_decomposition(G) -> {True, False, certificate}` on
connected cubic graphs.

### 2a. Replay Zhang–Szeider

Implement the SAT encoding from CP 2025 verbatim. Use their reducible
templates from the Zenodo artifact. Confirm we reproduce their headline
numbers on a small subset (e.g. all $n \le 18$ from `nauty geng` plus
hand-picked harder $n \in \{22, 24\}$ graphs).

If propagators are custom, **DRAT proof logging is not automatic**. Our
target during replay is *not* a DRAT proof, but a structured certificate:

- for **True**: an emitted $(T, C, M)$ checked by
  `scripts/verify_decomposition.py` (set partition + spanning-tree DFS +
  2-regularity per vertex + matching per vertex). This check is propagator-
  agnostic.
- for **False**: an unsatisfiability certificate is bound to the propagators
  used. If the propagator is "no-op enrichment" (only adds clauses that
  are valid consequences of the partition constraints), then DRAT logging
  on the enriched CNF is sufficient. If the propagator is more aggressive
  (e.g. learned cycle-cut clauses), each learned schema must be paired
  with a stand-alone soundness lemma in `docs/propagator_soundness.md`.

We do not currently have a counterexample candidate, so the False-side
proof story is theoretical; document it but do not over-engineer ahead of
a candidate.

### 2b. Cross-check encoding

Implement an independent textbook SAT encoding with no specialised
propagators (slow but proof-producing CNF). For every disagreement with
2a on small graphs, dig in until both agree.

### 2c. Heuristic positive search

For frontier extension (Phase 3 below), wrap the SAT oracle with a fast
heuristic: try Bachtler–Krumke from a few perfect matchings, then a
DFS-tree greedy, then SAT. Heuristic hits skip SAT. The heuristic is *not*
sound by itself — every "True" still goes through the verifier.

## Phase 3 — frontier, calibrated to reality

The combinatorial scale matters. From OEIS A002851 (connected cubic simple
graphs):

| $n$ | count |
|---:|---:|
| 24 | 117,940,535 |
| 26 | 2,094,480,864 |
| 28 | 40,497,138,011 |
| 30 | 845,480,228,069 |

Zhang–Szeider explicitly note that naive generate-and-test is infeasible
after $n = 20$; their $n = 28$ run cost ~4.0 CPU-years and depended on
SMS-level isomorph rejection plus their specialised propagators. A "geng
+ SAT" sweep at $n = 30$ is **not** a realistic deliverable.

Frontier plan, instead:

- **$n \le 18$**: full reverification on the local machine, end-to-end.
- **$n \in \{20, 22, 24\}$**: shard via `geng -res` and Zhang–Szeider's
  reducibility-first dispatch; verify a small uniform random sample plus
  every graph in any catalogue of "candidate hard cases" (e.g. snarks at
  those orders).
- **$n = 26, 28$**: re-confirm by trusting Zhang–Szeider's SMS run,
  spot-checking certificates they publish.
- **$n \ge 30$**: do **not** attempt a uniform sweep. Instead target
  *specific structured families* that survive the Track B shape constraints
  (large-girth cubic, snark-hunter outputs, generalized Petersen
  variants, large-girth Cayley cubic).

In other words: the headline computational deliverable is *new reducible
templates* (Phase 4), not *more $n$*.

## Phase 4 — reducible-template extension

**Start from the Zhang–Szeider template library, not from scratch.** Their
work computes reducible templates up to index 6 and order 18 and integrates
them with SMS.

### Template formalism (Bachtler–Heinrich / Zhang–Szeider)

A **template** is a subcubic graph $H$ together with a labelling of its
boundary half-edges (those incident to a vertex of degree $< 3$ in $H$).
The finite object to verify is the **local behaviour table**: it records,
for each possible **boundary trace** $\tau$, whether $H$ admits an
edge-partition $E(H) = T_H \sqcup C_H \sqcup M_H$ extending $\tau$. The
boundary trace specifies, for each boundary half-edge, both
- its assigned colour in $\{T, C, M\}$, and
- when the colour is $T$, the **green-forest connectivity partition** —
  i.e. which other boundary half-edges its tree-component connects to
  inside $H$.

Together, colour + connectivity partition is the data Bachtler–Heinrich
and Zhang–Szeider use; "trace" below always means this combined data.

A template (configuration) $H$ is **reducible** when it comes paired with
a strictly smaller **replacement** $H'$ (same boundary, $|E(H')| < |E(H)|$
or $|V(H')| < |V(H)|$ under a well-founded measure) such that

$$\mathrm{Trace}(H') \subseteq \mathrm{Trace}(H),$$

where $\mathrm{Trace}(X)$ denotes the set of boundary traces extendable to
a partition $E(X) = T_X \sqcup C_X \sqcup M_X$. Equivalently: every local
behaviour of a 3-decomposition on $H'$ lifts to a local behaviour on $H$
with the same boundary trace. Consequently, in any putative minimal
counterexample $G$ containing $H$, we may substitute $H \mapsto H'$ to
obtain a strictly smaller connected cubic graph $G'$; if $G'$ admits a
3-decomposition, lifting it back through the trace containment gives a
3-decomposition of $G$ — contradiction. So no minimal counterexample
contains $H$.

The pair $(H, H')$ is the verifiable artefact. This is exactly the
reduction logic of Bachtler–Heinrich §3 and the Zhang–Szeider templates.

### Our additions

1. **Verifier.** Build `scripts/verify_template.py` taking the pair
   $(H, H')$ and confirming
   $\mathrm{Trace}(H') \subseteq \mathrm{Trace}(H)$. This is a **finite**
   check: enumerate partitions of $E(H')$ and of $E(H)$ (small, bounded
   objects) to compute $\mathrm{Trace}(H')$ and $\mathrm{Trace}(H)$, then
   verify containment trace-by-trace. The well-foundedness of the
   reduction measure (e.g. $|E|$ strictly decreasing) is checked
   separately. Do *not* enumerate cubic supergraphs of $H$ — the trace
   formalism exists precisely to avoid that. Independently re-verify a
   sample of Zhang–Szeider's templates with this tool; this is the trust
   handshake to their library.

2. **Beyond index 6 / order 18.** Push the search to index 7–8 / order
   20–22. The marginal cost grows rapidly with index (the number of
   boundary traces explodes as a function of boundary size); instrument
   the runtime per candidate and stop when wall time per new template
   exceeds a budget.

3. **Templates compatible with the $G^\star$ shape.** Use the Track B
   restrictions (claws, large girth, large tree-width) to bias the
   candidate generator toward configurations a minimal counterexample
   must contain.

Every new template enters `data/known_templates.json`; every entry has a
machine-checked local behaviour table, the SAT solver version (if SAT was
used in the local check), a soundness reference for any propagator used,
and the template's graph6.

## Phase 5 — structural theory of $G^\star$ (Track B)

The known restrictions on $G^\star$ above give a starting list. The work
is to make each row a free-standing, citation-light lemma in our notation,
then push for new rows.

### 5.0. Highest priority: reductions to the 3-connected case

The biggest leverage is upgrading the conditional bullets of the $G^\star$
shape to unconditional. Two lemmas to prove ourselves:

- **2-edge-cut reduction.** Build the full nine-case boundary-trace table
  for a 2-edge-cut $F = \{e_1, e_2\}$ with sides $A, B$. For each case,
  exhibit either a reduction to two strictly smaller boundary-traced
  instances or a direct construction of a 3-decomposition. Until every
  case is closed, "$G^\star$ is essentially 4-edge-connected" is *not*
  ours.
- **2-vertex-cut reduction.** A 2-vertex-cut $\{u, v\}$ in a cubic graph
  is more subtle (each cut vertex sends edges to both sides). Bachtler–
  Heinrich's $\le 4$-edge-cut reductions partially cover this. We need
  either a clean lemma in our notation or an explicit citation chain;
  without it, every result currently stated for "3-connected cubic"
  remains conditional on us proving $G^\star$ is 3-connected.

Both are concrete, finite case analyses; both are realistic on this
workstream's timescale. Doing them first multiplies the value of
everything in §5.1–§5.5.

### 5.1–5.5. Further targets

- **Cyclic edge-connectivity.** Show $G^\star$ is cyclically
  $k$-edge-connected for the largest $k$ we can prove. (Cubic graphs have
  vertex connectivity $\le 3$, so vertex connectivity ceilings out;
  cyclic edge-connectivity is the useful refinement.) Bachtler–Heinrich
  should give $\lambda_c(G^\star) \ge 4$ once 5.0 is closed; then push to
  $\lambda_c \ge 5, 6$.
- **Girth.** Triangle-freedom is conditional on 3-connectivity (above).
  Once 5.0 is closed, push to $g(G^\star) \ge 5, 6, 7$ by enumerating
  4-cycle / 5-cycle / 6-cycle configurations as templates (Phase 4).
- **Matching contraction.** Bachtler–Krumke's "$F/{\sim}$ is a star"
  generalises naturally to "$F/{\sim}$ has bounded matching number" or
  "bounded diameter". Try $F/{\sim}$ a caterpillar; broom; spider. Each
  gives a new settled class.
- **Tree-width / path-width.** Bachtler–Heinrich settle tree-width $\le 3$
  and path-width $\le 4$ in the 3-connected class. Push to tree-width
  $\le 4$.
- **Forbidden induced configurations.** Beyond $K_{1,3}$-free, what
  *forced* induced subgraphs does $G^\star$ contain? Configurations
  forced by avoiding all known reducible templates are a candidate list.

Each lemma lives in `docs/minimal_counterexample.md`, with the inverted
hypothesis ($G^\star$'s property), the proof sketch, and the dependencies
on Phase 4 templates.

## Phase 6 — synthesis and exits

A proof comes together when Track A's reducible-template library and
Track B's structural restrictions on $G^\star$ meet in the middle:
i.e. every connected cubic graph satisfying all Track B properties of a
hypothetical $G^\star$ must contain at least one reducible template from
Track A. Equivalently, no graph satisfies the conjunction of "is a
minimal counterexample" and "avoids every known reducible template". The
plan does not promise this meeting will happen on its timescale; it
arranges artefacts so that any third-party advance on either track slots
in immediately.

Realistic outcomes, in order of plausibility:

1. **Partial:** several new reducible templates; one or two new settled
   classes (e.g. caterpillar $F/{\sim}$); independent re-verification of
   Zhang–Szeider's $n \le 28$ certificates on our infrastructure;
   $G^\star$ shape sharpened with new forced properties. Publishable as a
   *Reducible configurations for the 3-Decomposition Conjecture, II* paper.
2. **Mostly null:** confirm the state of the art, identify which Track B
   lemmas we cannot push further, document the obstruction. Useful to the
   community as a survey + verifier code.
3. **Theorem:** unlikely on the timescale of this workstream, but the
   plan is structured so a theorem from a third party slots in
   immediately (we have the verifier infrastructure).
4. **Counterexample:** very unlikely given $n \le 28$ verification; would
   require two independent SAT solvers, manual SAT proof inspection,
   minimization under all known reductions.

## What this plan deliberately omits

- **Generic discharging on cubic graphs.** No global Euler reservoir;
  not a viable mechanism without an embedding or a new charge potential.
- **A "geng + SAT" sweep at $n = 30$.** A002851 says there are
  $8.45 \times 10^{11}$ such graphs; Zhang–Szeider's $n = 28$ run cost
  ~4 CPU-years with their full machinery. We will not budget this.
- **An appeal to the 4-flow conjecture.** A nowhere-zero 4-flow on a
  cubic graph is equivalent to 3-edge-colourability; snarks are the
  obstruction class. The implication from "3-edge-colourable cubic" to
  "has a 3-decomposition" is **not** immediate (a 3-edge-colouring
  partitions $E$ into three perfect matchings $M_1 \sqcup M_2 \sqcup M_3$;
  $M_1 \cup M_2$ is a 2-factor; recovering a spanning tree from a 2-factor
  plus a matching requires extra surgery, and the cleanest known route
  for this case still passes through Bachtler–Krumke). No free lunch is
  claimed.
- **Uncited results from Fan–Zhou (2025) and Fan–Guo–Zhou (2025).** Both
  appear to give quantitative bounds on near-decompositions; once
  obtained, they may strengthen Phase 5 substantially, but they are not
  used until read end-to-end.
- **Higher vertex-connectivity assumptions.** Cubic graphs have vertex
  connectivity $\le 3$; "$n$-connected for $n \ge 4$" is empty. The
  refined invariant is cyclic edge-connectivity (above).

## Immediate engineering tasks

1. Create `problems/3_decomposition_conjecture/{scripts,data,tests}` and a
   `Makefile` mirroring `unit_vector_flows/`.
2. Pull the Zhang–Szeider Zenodo artifact into
   `problems/3_decomposition_conjecture/external/zhang_szeider_2025/`
   with a checksum manifest.
3. Implement `scripts/verify_decomposition.py` (graph + certificate →
   pass / fail). Propagator-agnostic; this is the trust root.
4. Implement `scripts/verify_template.py` (reduction pair $(H, H')$ →
   compute $\mathrm{Trace}(H), \mathrm{Trace}(H')$ by finite enumeration;
   verify $\mathrm{Trace}(H') \subseteq \mathrm{Trace}(H)$ and a
   well-founded size decrease; emit reducibility verdict).
5. Build `data/known_templates.json` from the Zhang–Szeider library and
   `data/known_classes.json` from Phase 1's lit pass.
6. Stand up `scripts/decomposition_sat.py` (textbook CNF encoding,
   no custom propagators, DRAT logging) for cross-checking.
7. Write `docs/literature_notes.md` and `docs/minimal_counterexample.md`
   skeletons.
