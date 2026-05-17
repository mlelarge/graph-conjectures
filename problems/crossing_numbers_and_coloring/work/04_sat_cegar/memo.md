# R1a — SAT/CP/CEGAR memo

Author: Role 4 (SAT/CP/CEGAR engineer).
Scope: implementation plan for Route R1a from `docs/plan.md` v3 — closing the
three Cranston-residual orders $(t, n) \in \{(25, 48), (26, 50), (26, 51)\}$ by a
CEGAR loop with an outer SAT/CP search over candidate graphs and an inner
verifier that (a) checks $25$-chromaticity and (b) lower-bounds $\operatorname{cr}(G)$
through Role 3's oracle.

Per `docs/plan.md` v3 the residual is *three exact pairs* (Cranston Theorem 2),
not a range. R1a is "research-grade engineering at or beyond the state of the
art" and even closing one sub-family of $(25, 48)$ would be a publishable
artefact independent of an Albertson verdict. This memo optimises for *useful
partial progress* (rule out structured sub-families, ship reusable proof-log
infrastructure) rather than a one-shot UNSAT on the full residual.

---

## 1. Encoding the search space

Target: a propositional / CP encoding $\Phi_{t,n}$ such that any model
$M \models \Phi_{t,n}$ is the adjacency matrix of an undirected simple graph $G$
on $n$ vertices that *could* be a minimum counterexample (MCE) to Albertson at
$(t, n)$. The four base ingredients are: (i) the edge variables; (ii)
$25$-chromaticity; (iii) $25$-vertex-criticality; (iv) the structural side
constraints ($\delta \ge t-1$, $|E| \ge$ KY bound, $(t-1)$-edge-connectivity,
bridgelessness).

Throughout this section the working case is $(t, n) = (25, 48)$. Sizes for
$(26, 50)$ and $(26, 51)$ scale similarly.

### 1.1 Edge variables

Boolean $e_{ij}$ for $1 \le i < j \le n$. For $n = 48$ this is $\binom{48}{2} =
1{,}128$ variables. These are the only "real" graph variables; everything else
is either a witness, a counter, or a CEGAR refinement.

### 1.2 Degree, edge count, basic structural

- **Min degree $\delta \ge t - 1 = 24$.** For each vertex $v$, post a cardinality
  constraint $\sum_{u \ne v} e_{uv} \ge 24$. With a CP solver (CP-SAT,
  Choco) this is one PB constraint per vertex; $n = 48$ such constraints.
  In pure SAT, encode via a sequential-counter or totaliser encoding — adds
  $\Theta(n^2)$ auxiliary vars per vertex (so $\sim 110{,}000$ aux vars total
  with a totaliser); CP encoding is strongly preferred.
- **Edge count lower bound.** Kostochka–Yancey says for a $t$-critical graph
  $|E(G)| \ge \tfrac12((t - \tfrac{2}{t-1}) n - t(t-3)/(t-1))$ which for $t =
  25, n = 48$ gives roughly $577$ (essentially equivalent to $\delta \ge 24$ at
  this $n$). One global PB constraint $\sum e_{ij} \ge L_{\rm KY}(t, n)$.
- **Connectedness / bridgelessness.** Both follow from $(t-1)$-edge-
  connectivity, encoded next. We do not add separate connectedness clauses.
- **$(t-1)$-edge-connectivity (Kostochka–Stiebitz).** This is genuinely
  non-trivial in SAT. The clean encoding is *flow-based*: pick a fixed source
  $s = v_1$ and for every sink $t \in \{v_2, \ldots, v_n\}$ post a max-flow
  side-constraint asserting at least $t - 1 = 24$ edge-disjoint $s$-$t$ paths.
  In CP-SAT this is a single multi-commodity-flow side block per sink (47
  sinks). In SAT it requires a per-pair flow encoding (cubic in $n$ for a single
  flow, multiplied by $n - 1$ sinks). For $n = 48$ this is borderline but doable
  with lazy clause generation. **Decision:** keep edge-connectivity as a *lazy*
  constraint enforced via a CEGAR sub-loop (Section 3), not as a flat encoding.
  Initial $\Phi_{t,n}$ only asserts $\delta \ge t - 1$ and connectedness via a
  spanning-tree witness; cuts of size $< t - 1$ produced by candidate models
  are then blocked.

Constraint count for the base structural block: $\sim 50$ PB constraints in CP,
or $\sim 10^5$ clauses in flat SAT after counter expansion.

### 1.3 The hard one: $\chi(G) \ge 25$

Encoding "no proper $24$-colouring exists" is the main risk in R1a. The plain
existential encoding is $\Pi_2$: $\forall c \exists uv \in E, c(u) = c(v)$. A
flat SAT translation either (a) Tseitins out over $24^{48} \approx 10^{66}$
candidate colourings (infeasible), or (b) needs reformulation.

Three options considered:

- **(a) co-NP certificate** (Kempe witness / Hajós derivation / Galvin frozen
  colouring). The Hajós derivation length is unbounded in $n$. **Rejected.**
- **(b) inner CEGAR layer.** Outer SAT proposes $G$. An *inner* SAT solver
  attempts a proper $24$-colouring of $G$. If SAT (colouring $c$), $G$ is not
  $25$-chromatic and the outer formula learns a blocking clause from the
  reason for $24$-colourability. If UNSAT, $G$ is at least $25$-chromatic.
  Inner formula: standard direct encoding, $24n \approx 1{,}152$ colour
  variables and $\sim 13{,}900$ clauses at $n = 48$; millisecond-scale on
  modern CDCL.
- **(c) structural surrogate.** Replace $\chi(G) \ge 25$ with "$G$ contains a
  specified $25$-critical subgraph as a spanning subgraph". Trades
  completeness for tractability. Plan v3 explicitly endorses this as the
  practical workaround.

**Decision.** Combine (b) and (c). Outer search enforces $\chi \ge 25$ only
through the inner-CEGAR layer. A *seeding* phase restricts to known
$25$-critical kernel families ($K_{24}$ containment, doubled $K_{12}$ joins,
Hajós products) — these are *complete* sub-cases of R1a and closing them is a
publishable partial result. The unrestricted residual is attacked only after
the seeded sub-cases have closed and the inner CEGAR has been tuned.

This is the Heule architecture from Schur number five and Pythagorean triples:
outer CDCL on structural constraints, inner CDCL on the colouring certificate,
lazy interaction via blocking clauses.

### 1.4 Vertex-criticality: $\chi(G - v) \le 24$ for every $v$

A second $\forall$, but per-vertex it is *positive* ("a $24$-colouring of $G -
v$ exists"), hence SAT-easy. A naive flat encoding posts colouring constraints
for $G - v$ for every $v$ (~53k colour variables, ~1.3M clauses — painful but
not exponential).

**Chosen: lift criticality into the CEGAR loop.** The outer formula does
*not* statically enforce $\chi(G - v) \le 24$. After a candidate $G$ passes
the $\chi \ge 25$ inner check, a second inner pass tests $24$-colourability of
$G - v$ for each $v$. If some $v$ fails, $G$ is not $v$-critical there; add a
blocking clause from the UNSAT core of the failed colouring attempt for $G$
itself. $n$ stays fixed at the Cranston-residual value.

**Per-vertex CEGAR cost.** $n = 48$ inner colouring calls on graphs of size
$47$, each $\sim 27{,}000$ vars / $\sim 270{,}000$ clauses, $\le 1$s each.
Per-candidate criticality check $\le 1$ min — dominates inner-loop budget.

### 1.5 The crossing-number constraint

The outer formula does *not* directly encode $\operatorname{cr}(G) < Z(25) =
4{,}356$ or $\operatorname{cr}(G) < \underline{L}(25)$. Instead, this is the
*Role 3 oracle hook*: after $G$ passes chromaticity + criticality, the oracle
is invoked to certify $\operatorname{cr}(G) \ge Z(25)$. If the oracle confirms,
$G$ is not an MCE and the outer solver learns a blocking clause from the
oracle's UNSAT core. If the oracle returns UNKNOWN or a lower bound below
$Z(25)$, $G$ is flagged as a candidate counterexample for hand verification.

See Section 3.2 for the oracle interface contract.

### 1.6 Variable / constraint count summary at $(t, n) = (25, 48)$

| Block | Variables | Constraints / clauses |
|---|---|---|
| Edge variables $e_{ij}$ | 1,128 | — |
| $\delta \ge 24$ (PB in CP) | 0 aux | 48 PB |
| Edge count $\ge L_{\rm KY}$ (PB) | 0 aux | 1 PB |
| Connectedness witness (spanning tree) | $\sim 1{,}128$ flow aux | $\sim 2{,}300$ clauses |
| $(t-1)$-edge-conn. (lazy CEGAR) | 0 statically | grows by blocking clauses |
| $\chi(G) \ge 25$ (inner CEGAR) | 0 in outer | grows by blocking clauses |
| Per-vertex criticality (inner CEGAR) | 0 in outer | grows by blocking clauses |
| Symmetry breaking (Section 2) | 0–few k aux | $10^4$–$10^5$ clauses |
| **Outer base, static** | $\sim 1{,}200$ | $\sim 5{,}000$ |
| **Outer accumulator (CEGAR-learnt)** | 0 | unbounded |

Order-of-magnitude: the outer base formula is small (low five figures). The
inner formulas are small (low six figures). The accumulator of learnt blocking
clauses is where the formula grows over the CEGAR run, and is the limiting
factor on memory.

---

## 2. Symmetry breaking

The automorphism group of any candidate is unknown a priori, but $S_n$ acts on
the encoding by vertex relabelling. Without symmetry breaking, the outer
solver re-explores every vertex permutation of every candidate — $48! \approx
10^{61}$ blowup. Symmetry breaking is mandatory.

**Approach: incomplete canonical-form ordering, Codish/Itzhakov-style.**

The clean theoretical target is to enforce a *canonical-form constraint*
$\mathrm{Can}(G)$ that holds iff the adjacency matrix of $G$ is the
lexicographically smallest among its orbit under $S_n$. This is the
Codish–Frisch–Itzhakov approach (e.g. Codish–Miller–Prosser–Stuckey, *Breaking
Symmetries in Graph Search via Canonizing Sets*, CP 2019; Itzhakov–Codish on
canonical-form SAT for graph isomorphism, arXiv:1606.04920 and follow-ups).
Exact canonical-form constraints are *exponential* in size in the worst case
for general $n$, so for $n = 48$ we have to settle for incomplete symmetry
breaking and push the residual orbit collisions to Role 5 (post-hoc isomorph
rejection).

**Layers** (deploy in order of cost):

1. **Lex-leader on degree sequence.** $\deg(v_1) \ge \cdots \ge \deg(v_n)$ via
   sequential-counter PB. $O(n^2)$ aux, removes $\Theta(n!)$ when the degree
   sequence is non-constant.
2. **Lex-leader on adjacency rows.** row$_i \ge_{\rm lex}$ row$_{i+1}$ (Codish).
   $O(n^3)$ clauses, $\sim 10^5$ at $n = 48$.
3. **Itzhakov partition-refinement.** For *degree-regular* graphs (the dense
   sub-case: $24$-regular on $n = 48$ is exactly $\delta \ge 24$ in the
   tightest case) lex on degree gives nothing. Itzhakov's encoding interleaves
   nauty-style colour refinement with SAT propagation — essentially a small
   GI solver inside the SAT. Used in the $R(4, 5)$ verification.
4. **Static seeds.** Fix neighbourhoods explicitly (e.g. hard-code $K_{24}$ on
   $\{v_1, \ldots, v_{24}\}$). Cuts $S_n$ down to $S_{24} \times S_{24}$ and
   confines residual symmetry to the $24$ outside vertices.

**Tradeoff.** Layer 1 is free, $>10^{30}$ reduction on irregular graphs.
Layer 2 adds $\sim 10^5$ clauses, another $\sim 10^5$ reduction. Layer 3 is
the right thing for the dense regular sub-cases but is non-trivial to
implement. Layer 4 is mandatory for the seeded sub-cases of Section 1.3(c).

**Honest limit.** Symmetry breaking on $48$-vertex graphs is hard; any
practical encoding leaves a non-trivial residual orbit. Role 5 owns post-hoc
isomorph rejection on the SAT survivors. Our job: deploy the cheap
canonical-form constraints, instrument the residual orbit size, hand off in
a clean format. We do *not* attempt symmetry-completeness inside the outer
SAT.

---

## 3. CEGAR architecture

```
   +-----------------------+    candidate G    +-------------------------+
   |   OUTER SAT/CP        | ---------------> |   INNER VERIFIER         |
   |   (CP-SAT or CaDiCaL  |                   |   (a) chi(G)>=25?        |
   |    with PB, on Phi_   | <--- block --- + |   (b) crit at every v?   |
   |    {t,n} + accum)     |   c_1, c_2, ...   |   (c) cr(G) >= Z(t) ?   |
   +-----------------------+                   +-------------------------+
        ^                                                  |
        |                                                  | (a),(b) inner SAT
        |                                                  | (c) Role 3 oracle
        +-------------- generalised blocking clauses ------+
```

### 3.1 Outer loop

The outer solver is CP-SAT (Google OR-Tools) or CaDiCaL with PB support. CP-SAT
is preferred because the structural constraints are natively PB and because
CP-SAT supports lazy-clause callbacks cleanly. The outer solver enumerates
models of $\Phi_{t,n} \wedge \bigwedge_i c_i$ where the $c_i$ are blocking
clauses accumulated over the CEGAR run.

A "model" is an assignment to the edge variables; everything else is auxiliary.
On each model emitted, the inner verifier runs and either accepts (in which
case we have a *real candidate counterexample* — flag and stop), rejects with a
reason (in which case the reason is converted to a blocking clause and the
outer loop continues), or times out (in which case the model is set aside as
"unverified" and skipped, with metrics logged).

### 3.2 Inner verifier — three checks

**(a) $\chi(G) \ge 25$.** Run a $24$-colouring SAT on $G$. If SAT (colouring
$c$), the generalised blocking clause uses the *monochromatic-pair cover*:
$F = \{(u,v) : c(u) = c(v),\, uv \notin E(G)\}$; post $\bigvee_{(u,v) \in F}
e_{uv}$, which blocks every $G' \supseteq G$ on which $c$ remains valid. A
$24$-colouring of a $24$-regular $48$-vertex graph has $\sim 47$ colour-class
slots, so $|F|$ is typically a few dozen — exactly the short-clause regime
CDCL likes. If UNSAT, $G$ is $\ge 25$-chromatic; emit DRAT/LRAT for the
proof-log (Section 5), proceed to (b).

**(b) Per-vertex criticality.** For each $v$, run $24$-colouring on $G - v$.
If UNSAT for some $v$, $G$ is not critical at $v$; blocking clause from the
UNSAT core (edges of $G - v$ that already force $\chi \ge 25$). If SAT for
all $v$, proceed to (c). Optimisation: warm-start the $G - v$ solvers off the
(a) solver state; since $\chi(G) = 25$ is fragile under vertex removal, most
calls return SAT in milliseconds.

**(c) Crossing number.** Hand $G$ to Role 3. Oracle returns
$(\overline{\operatorname{cr}}(G), \underline{\operatorname{cr}}(G))$ or
UNKNOWN. If $\underline{\operatorname{cr}}(G) \ge Z(25) = 4{,}356$, $G$ is
not an MCE for the *strong form*; block at minimum the canonical form of $G$,
with Role 5 the whole isomorphism orbit. If $\overline{\operatorname{cr}}(G)
< \underline{L}(25)$ for the *finite certified* lower bound (per `plan.md` v3
F1b — never an asymptotic extrapolation), $G$ is a candidate Albertson
counterexample: stop, hand off. Otherwise (UNKNOWN), park in a deferred
queue for stronger offline oracles; outer loop continues.

### 3.3 Blocking clauses and orbit propagation

The naive blocking clause from any inner-verifier rejection blocks only the
exact graph $G$. We want to block the *whole orbit* of $G$ under symmetry
breaking. Two mechanisms:

- **Generalised blocking from the UNSAT core** (inner SAT only — covers checks
  (a), (b)): the UNSAT core gives a small subset $E_0 \subseteq E(G)$ such that
  any supergraph of $E_0$ is also rejected for the same reason. The blocking
  clause is $\bigvee_{(u,v) \in E_0} \neg e_{uv}$, length $|E_0|$. UNSAT cores
  from CDCL on $24$-colouring instances at this size are typically 50–200
  edges; the blocking clauses are short.
- **Orbit blocking from canonical-form** (handles all three checks): compute
  the canonical form $\mathrm{can}(G)$ via nauty/bliss after each rejection,
  and add a blocking clause that asserts the candidate is *not* in the orbit
  of $\mathrm{can}(G)$. This requires translating the orbit information back
  into propositional form on the $e_{ij}$ — implementable by enumerating the
  $|S_n|/|\mathrm{Aut}(G)|$ permutations and posting one long clause per
  permutation, *or* by adding a single symbolic clause via the symmetry-breaking
  framework if the latter supports orbit-blocking primitives.

The plan is to use the first mechanism for (a), (b) and to push the orbit
blocking for (c) into Role 5's post-hoc rejection pipeline rather than try to
build it into the outer SAT.

### 3.4 Termination

The outer loop terminates either:

- **UNSAT** — $\Phi_{t,n} \wedge \bigwedge c_i$ is unsatisfiable. Conclusion:
  no $25$-critical MCE on $48$ vertices exists. Albertson is verified at $t =
  25$.
- **SAT with a real candidate** — outer model passes all three inner checks
  including the crossing-number lower bound being below $\underline{L}(25)$.
  Conclusion: candidate counterexample, hand off to mathematicians.
- **Timeout** — both common and likely. Conclusion: no verdict, but the
  accumulator of blocking clauses is a reusable artefact that constrains
  future re-runs (with better hardware, better oracle, or tighter encoding).

---

## 4. Tractability assessment

I will not pretend this is easy. The honest estimate at $(t, n) = (25, 48)$:

- **Outer variable count.** $\sim 1{,}200$ static, plus aux from symmetry
  breaking, totalling a low five figures.
- **Outer constraint count.** $\sim 5{,}000$ static, plus the unbounded
  CEGAR accumulator. After $K$ CEGAR rounds we have $\sim 5{,}000 + K$
  generalised clauses of average length $\sim 100$ edges.
- **CEGAR rounds expected.** Dominant uncertainty. After lex-leader symmetry,
  the outer search is roughly $2^{1{,}128}/48!$ minus structural cuts.
  Counting $24$-regular $48$-vertex graphs alone is $\exp(\Theta(n^2))$ — not
  enumerable in a CPU-year without further pruning. Per-round cost is the
  inner colouring checks ($\sim 1$ min/candidate), so $10^7$ CPU-s
  ($\sim 1$ day on 100 cores) buys $\sim 10^5$ CEGAR rounds. Whether $10^5$
  generalised clauses suffice is the open question. Heule's Schur(5)
  (arXiv:1711.08076) used cube-and-conquer over $> 2 \cdot 10^6$ subcubes on
  144 cores for weeks, producing a 2 PB DRAT proof — a fair *upper analogue*
  of what a successful R1a might look like, though Schur(5) lacked our
  $S_n$-symmetry burden.

- **Effective branching factor.** With layers 1+2 of symmetry breaking and
  CEGAR learning, optimistic factor is $\sim 3$ per CDCL decision (well below
  the worst case of $\sim 1{,}128$). With layer 3 (Itzhakov), down to $\sim
  2$. With layer 4 (structural seed), the effective $n$ drops to $\sim 24$
  (the outside vertices) and the branching factor at those vertices is
  whatever the residual problem implies.

- **Expected solve time on a modern cluster.** A 256-core cluster, run for
  one year, gives $\sim 8 \cdot 10^9$ CPU-seconds, supporting $\sim 10^8$
  CEGAR rounds. With the optimistic branching estimate above, the
  *structurally restricted sub-cases* (seeded by $K_{24}$ containment, or by
  a fixed doubled-$K_{12}$ structure, or by a specified $24$-edge-connectivity
  fingerprint) are plausibly closable to UNSAT in that budget. The
  *unrestricted* $(25, 48)$ residual is **not** plausibly closable in 1
  CPU-year — I would not bet on UNSAT in $\le 100$ CPU-years either. My
  honest estimate is that the unrestricted residual needs *either* a major
  encoding breakthrough *or* a structural theorem (Role 2) collapsing the
  search space by orders of magnitude.

- **Summary verdict (per the v3 tractability sub-score of $2/10$):**
  - $\le 1$ CPU-year: realistic *only* for one structured sub-family closure
    (e.g. "no $25$-critical graph on 48 vertices contains $K_{24}$ as a
    spanning sub-clique"). Useful, publishable, but not an Albertson result.
  - $\le 100$ CPU-years: maybe the unrestricted residual *if* the inner
    oracle is fast and the symmetry breaking is strong. Still a coin flip.
  - Beyond: the SAT path may simply not converge without help from Routes
    R2 (sharper Crossing Lemma constant) or R5 (better Fox–Pach–Suk vertex
    bound) reducing the residual structurally.

---

## 5. Proof logs and verification

The bar for "this verifies Albertson" is high: an UNSAT verdict from a SAT
solver is only as good as the proof log it emits, and only if the log is
*independently checkable*.

**Outer.** CaDiCaL/Kissat emit DRAT on UNSAT; for projected $> 10^{12}$-line
proofs use LRAT (parallel-checkable, Schur(5)-grade). CP-SAT does not emit
DRAT directly; either re-encode CP to SAT for final certification, or use
VeriPB, which supports PB natively and would handle our structural constraints.

**The hard part: CP and external-oracle CEGAR are NOT directly checkable.**

- Plain CP propagators have no DRAT/LRAT analogue. VeriPB or CPLog needed.
- Inner $24$-colouring is plain SAT and DRAT-checkable; certificates glue
  into the outer trace via the blocking-clause derivation.
- Role 3's oracle (ILP / SAT / structural) must emit a per-verdict checkable
  artefact: ILP dual, DRAT, or Coq/Lean transcript. Without this, CEGAR is
  not reproducible, much less verifiable.

**Recommendation.** Outer = VeriPB + PB; inner $24$-colouring = DRAT glued in;
Role 3 oracle emits per-verdict certificates in a Role-6-agreed format; the
global proof is a *composite* artefact (outer VeriPB + inner DRAT + oracle
certificates) and Role 6 owns the meta-checker that verifies the gluing.
External-oracle proofs are checkable iff the oracle is checkable — Role 3
must use a checkable oracle from day 1 or the CEGAR verdict is non-rigorous.

---

## 6. Dependencies

### To Role 2 (structural constraints)

- Precise $(t-1)$-edge-connectivity (Kostochka–Stiebitz) statement in a form
  suitable for flat-SAT or lazy-cut CEGAR; identify the *minimal* set of
  structural side constraints so we do not duplicate work.
- Tightest known finite Kostochka–Yancey edge bound for the three pairs.
- Any hard-codable structural reduction ("MCE cannot contain $X$ as $Y$");
  each becomes a starting blocking clause and prunes orders of magnitude.
- Confirm / refute the seeds we use: $K_{24}$ containment, doubled $K_{12}$
  joins, Hajós-product seeds. If any is provably outside the MCE space, we
  save cycles.

### To Role 3 (crossing-number oracle interface)

- API: input $(G, Z, \text{timeout})$, output $\{\ge Z + \text{certificate},
  < Z + \text{drawing witness}, \text{UNKNOWN}\}$. Both verdict branches
  must emit a checkable proof artefact (Section 5).
- Response-time distribution (median, 95th, worst) so we can budget the loop.
- *Deterministic* responses — randomised oracles break blocking-clause
  invariants. If randomised, fix and log the seed.
- Honest documentation of $\underline{L}(25)$. Per `plan.md` v3 F1b: finite
  certificate, not asymptotic extrapolation.

### To Role 5 (isomorph rejection)

- Post-hoc pipeline consuming canonical adjacency matrices (we ship
  nauty/bliss output); Role 5 deduplicates across residual orbits.
- For UNSAT-verdict sub-cases nothing is needed; for SAT survivors we need
  cross-family dedup.

### To Role 6 (infrastructure)

- Proof-log storage: VeriPB + DRAT/LRAT logs in the tens-of-TB range for an
  unrestricted closure. Persistent storage with replay tooling.
- Meta-checker harness composing outer VeriPB + inner DRAT + oracle
  certificates and running the format-specific checkers (drat-trim,
  veripb-check, oracle-specific). This is the long pole for "verdict is a
  theorem, not a number".
- Cube-and-conquer scheduler — outer solver splits into $\sim 10^5$ cubes by
  lookahead, each solved independently. Without this, single-process CDCL
  will not parallelise at this size.
- Telemetry: per-round inner-check times, blocking-clause lengths, oracle
  call counts and verdicts, accumulator size. Required for stall debugging.

---

## 7. Failure modes

1. **Chromatic encoding incompleteness.** The inner-CEGAR encoding of $\chi
   \ge 25$ via $24$-colouring is sound but the structural surrogate (option
   (c) in Section 1.3) is incomplete. If we close all the seeded sub-cases
   and declare victory, we have only closed those sub-cases. *Mitigation*:
   explicitly enumerate which sub-cases are closed; do *not* claim Albertson
   at $t = 25$ until the inner-CEGAR encoding is run on the full residual.
2. **Symmetry breaking too weak.** Without Itzhakov-strength canonical-form
   constraints, the outer search re-explores symmetric copies of the same
   graph many times. Each re-exploration triggers an inner check and a
   blocking clause; the accumulator grows quadratically rather than linearly,
   and memory becomes the bottleneck. *Mitigation*: instrument the accumulator
   growth rate from day 1; if super-linear, deploy a stronger canonical form
   (or hand off more aggressively to Role 5).
3. **Inner oracle non-determinism.** If Role 3's oracle is randomised or has
   memory-pressure-dependent timeouts, two invocations on the same input may
   return different verdicts. Blocking clauses keyed on the verdict become
   unsound. *Mitigation*: insist on determinism in the oracle contract.
4. **Proof-log corruption.** Tens of TB of DRAT/LRAT/VeriPB on shared storage,
   produced by hundreds of cluster workers, is a corruption magnet. A
   single-bit flip in the proof breaks the meta-checker. *Mitigation*:
   per-cube checksums; redundant storage; periodic checker-replay on a
   sampled subset of cubes during the run rather than only at the end.
5. **Oracle returns "unknown" too often.** If the Role 3 oracle is too weak to
   produce a verdict on most candidates, the deferred queue grows and the
   CEGAR loop makes no progress. *Mitigation*: budget the oracle's
   incrementally-stronger fallbacks; do not let the deferred queue exceed
   some fraction (say $10\%$) of the candidate stream without intervention.
6. **PB-to-SAT encoding blowup.** If we abandon CP and re-encode PB cardinality
   constraints to SAT (for proof-log uniformity), the encoding adds
   $\Theta(n^2)$ aux variables per PB constraint. The outer formula grows
   from $\sim 10^4$ to $\sim 10^6$ clauses; CDCL solve time per round grows
   correspondingly. *Mitigation*: keep CP + VeriPB unless VeriPB
   infrastructure proves unworkable.
7. **Inner-check warm-starting fails.** If the per-vertex criticality checks
   do not warm-start cleanly off the (a) solver state, we pay the full
   inner-SAT cost on each of $n = 48$ inner calls. Per-candidate cost goes
   from $\sim 1$ min to $\sim 50$ min. *Mitigation*: implement warm starting
   carefully; if it fails, batch criticality checks to amortise.
8. **Blocking clauses too specific.** If we block only the exact graph $G$
   and not its orbit, the search space is effectively never pruned and the
   CEGAR loop is a glorified enumeration. *Mitigation*: orbit-block via
   canonical-form (Section 3.3); accept slower clause generation in exchange
   for orders-of-magnitude faster outer search.
9. **Misinterpreting the residual.** The Cranston residual is $(t, n) \in
   \{(25, 48), (26, 50), (26, 51)\}$ — three pairs. Running R1a on, say, $(25,
   47)$ would be a category error: that order is excluded by Cranston, and
   any "UNSAT" we produce there is vacuous. *Mitigation*: hardcode the three
   pairs from C1 (`scripts/cranston_residual.py`) as the only legal targets.
10. **Confusing $\operatorname{cr}(K_t)$ with $Z(t)$ in the oracle target.**
    Per `plan.md` v3 F1: $\operatorname{cr}(K_{25})$ is unknown; $Z(25) =
    4{,}356$ is the known *upper* bound. To prove Albertson we target $\ge
    Z(25)$; to falsify we target $< \underline{L}(25)$. Mixing these up
    produces wrong verdicts. *Mitigation*: hardcode the two thresholds
    separately in the oracle interface; never derive one from an asymptotic
    constant (F1b).

---

## 8. First 30-day deliverables

All concrete, all falsifiable, all *before* committing cluster time.

- **Day 1–3.** `scripts/cranston_residual.py` (C1): hardcode the three pairs,
  emit implied $\delta$, $|E|$, edge-conn., Fox–Pach–Suk constraints. JSON
  spec consumed by the encoder. Cross-check KY with Role 2.
- **Day 4–10.** CP-SAT encoding of "$t$-vertex-critical on $n$ vertices,
  $\delta \ge t - 1$, edge-conn. $\ge t - 1$" for small $(t, n)$. Validate
  against known $t$-criticals at $t \in \{4, 5, 6\}$, $n$ small. Deliverable:
  `validate_small.py`.
- **Day 11–15.** Inner $24$-colouring CEGAR layer cross-checked on $K_k$
  (UNSAT for $24$-col of $K_{25}$, SAT for $K_{24}$). Deliverable: harness
  emitting DRAT on UNSAT and a blocking clause from any SAT colouring.
- **Day 16–22.** CP-SAT encoding of "$25$-vertex-critical on $n = 30$" — the
  validation step the prompt requested. The point is not to find criticals
  (they may not exist at $n = 30, t = 25$) but to verify the verdict matches
  known truth on a smaller instance. Deliverable: UNSAT in $\le 1$ CPU-hour
  or a surprising SAT for Role 2.
- **Day 23–28.** Symmetry breaking layers 1 and 2. Measure residual orbit
  size on $n = 30$ candidates via nauty offline. Deliverable: orbit-size
  histogram and a go/no-go decision on layer 3 (Itzhakov).
- **Day 29–30.** 30-day report. Green: scale to $n = 40$ on a $K_{24}$-seeded
  sub-family in days 31–60. Red: document the failure (encoding blowup?
  inner CEGAR stall? symmetry too weak?), decide between recovery and
  switching to R1b.

**60-day milestone.** Run R1a on "$G \supseteq K_{24}$, $|V| = 48$, $\delta
\ge 24$, $25$-critical, $24$-edge-connected" *without* the crossing-number
step. Exercises every encoding layer except the oracle.

**90-day milestone.** Plug in Role 3's oracle, re-run the 60-day sub-family
with the crossing step active, emit composite proof log for Role 6. Outcome:
either a closed sub-family with a verified UNSAT proof (publishable unit) or
a debug log identifying the binding constraint.

**1-year stretch goal.** Close one Cranston-residual triple in *one*
structurally seeded sub-family with a verified proof. Not the full residual.

---

## Closing note

The architecture above is consciously *modest*. The plan v3 tractability
sub-score of $2/10$ for closing $t = 25, 26$ is the operating reality. R1a is
research-grade engineering whose first publishable artefact is likely "we
closed one sub-family with a checked proof log" rather than "we closed
$(25, 48)$ outright". Building toward the latter requires either Role 2 to
deliver structural collapses or R5 (Fox–Pach–Suk vertex bound improvement) to
shrink the residual. The CEGAR pipeline is the right vehicle in any case —
even partial progress against R1a produces reusable infrastructure for the
$(26, 50)$ and $(26, 51)$ triples and for any future Cranston-style
refinement of the residual window.
