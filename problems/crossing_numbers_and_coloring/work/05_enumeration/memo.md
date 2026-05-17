# Role 5 memo — canonical enumeration and coverage accounting for $t = 25, 26$

Author role: enumeration / canonical labeling / coverage.
Date: 2026-05-16.
Status: scoping memo, not a deliverable script. Pre-registers the protocol
that Roles 2 and 4 must agree to before R1c consumes anything I generate.

This memo answers: at the Cranston-residual orders $(25, 48)$, $(26, 50)$,
$(26, 51)$ from `docs/plan.md` v3 R1, what can I realistically enumerate,
what can I dedup with proof, and what is the contract between me, Role 2
(structural restriction), Role 4 (CEGAR SAT), Role 3 (lower-bound pipeline),
and Role 6 (storage)?

The deliverable is **not** "generate graphs". The deliverable is "tell the
team, with proof, what has and has not been generated". A missed sub-family
is the same as a wrong proof. This memo is the protocol for the second
sentence.

---

## 1. State of `nauty` / `Traces` at $n = 48$

### 1.1 Raw scale

The unlabeled count of graphs on $n$ vertices is OEIS A000088. Asymptotically
$\sim 2^{\binom n2} / n!$. For $n = 48$:

- $\binom{48}{2} = 1128$, so $2^{1128} \approx 3.6 \cdot 10^{339}$ labeled
  graphs.
- After dividing by $48! \approx 1.24 \cdot 10^{61}$, the unlabeled count is
  $\sim 10^{278}$ — i.e. far past every cosmological bound one might invoke.

The count of unlabeled $24$-regular graphs on $48$ vertices is not in OEIS
in closed form, but the cage / regular-graph asymptotics of McKay–Wormald
give a number around $\bigl(\tfrac{e^{-1/2}(2 \cdot 24)!}{(24!)^2 \cdot 2^{24}}\bigr)^{24}$
per vertex orbit and lands in the $10^{200}$+ ballpark. Even if one wrote
one graph per Planck volume per Planck time, this enumeration does not finish.

### 1.2 What `geng` will actually do

`geng -d24 -D47 48` would attempt to enumerate all unlabeled simple graphs
on 48 vertices with min-degree $\ge 24$. Empirically:

- `geng` at $n = 48$ with no degree constraint is **out of reach**. McKay
  reports `geng` connected outputs up to $n = 12$ or so as "instant",
  $n = 13$ as minutes, and the count is already $\sim 5 \cdot 10^{10}$ by
  $n = 14$. Each additional vertex multiplies by a factor on the order of
  $2^{n-1}/n$. We are 35 vertices past the comfort zone.
- The degree constraint `-d24` removes a vast multiplicative factor but the
  remaining count is still astronomical (see 1.1).
- `genrang` (random sampling) on $n = 48$ at the right edge density is
  feasible per-graph but provides **no coverage guarantee**; it samples one
  graph at a time from a uniform distribution that does not respect
  criticality.

Verdict: **pure `geng` is infeasible for R1c**. The team should not propose
any pipeline that consumes "all $24$-regular graphs on 48 vertices" as input.
Anyone who suggests this in a planning meeting should be politely asked to
estimate the count first.

### 1.3 Counts of $25$-critical graphs on 48 vertices

Unknown. The honest bounds are:

- **Lower bound (existence).** $K_{25}$ is itself $25$-critical, with $|V| =
  25$, well below the threshold. Adjoining $23$ extra critical vertices to
  $K_{25}$ via blow-down or Hajós-style constructions produces an unknown but
  positive number of $25$-critical graphs on 48 vertices. **The Kostochka–
  Yancey bound** $|E(G)| \ge \lceil (t(t-3)/(2(t-1))) \cdot n + 1 \rceil$ for
  $t$-critical graphs on $n$ vertices (Kostochka–Yancey, 2014, *J. Combin.
  Theory Ser. B*) gives, for $t = 25, n = 48$:
  $|E(G)| \ge \lceil (25 \cdot 22)/(48) \cdot 48 + 1\rceil = \lceil 11 \cdot 48 + 1\rceil
  \cdot$ — recompute: the coefficient is $t(t-3)/(2(t-1)) = 550/48 \approx
  11.458$, so $|E| \ge \lceil 11.458 \cdot 48 + 1\rceil = 551$. Note that the
  trivial bound from $\delta \ge 24$ is $|E| \ge 576$, which is **stronger**
  than Kostochka–Yancey at $n = 48$. So Kostochka–Yancey does not bite here.
  Existence count: unknown, $\ge 1$ (degenerate constructions from $K_{25}$
  exist, modulo whether they truly remain $25$-critical at 48 vertices —
  must check).
- **Upper bound (trivial).** $2^{\binom{48}{2}} / 48! \approx 10^{278}$. We
  are not getting a useful upper bound from any structural theorem the team
  currently has.

So the actual count of $25$-critical graphs on $48$ vertices with $\delta \ge
24$ is **unknown**, bounded below by a small positive integer (constructible
examples), bounded above by $10^{278}$ (trivial). Anyone who states a more
precise count is making it up.

**Operational implication.** I cannot promise R1c a finite enumeration of
$25$-critical graphs on 48 vertices. I can promise:

- a canonical-form dedup pipeline that is correct *on whatever stream Role 4
  hands me*;
- a structurally restricted sub-enumeration *if and only if* Role 2 hands me
  a predicate $P$ such that the sub-family $\{G : G \text{ is }25\text{-critical},
  |V| = 48, P(G)\}$ has small enough multiplicity to be tractable;
- a coverage audit that says exactly what fraction of the residual MCE space
  the sub-enumeration covers.

---

## 2. Hybrid generation pipelines

Three patterns are candidate. Two are explicitly infeasible; one is
research-grade.

### 2.1 `geng` + degree constraint + post-filter

`geng -c -d24 48 | filter_critical | filter_cr_lower_bound`. Out of reach
as established. The leading cost is `geng` itself, which generates without
the criticality test. Quantitatively:

- A 24-regular graph on 48 vertices has $|E| = 576$. The number of
  *labeled* such graphs is on the order of the configuration-model count
  $\approx \tfrac{(48 \cdot 24)!}{(2!)^{576} \cdot 576! \cdot \prod 24!} \cdot
  \text{simple-graph correction}$, which is well over $10^{200}$.
- `geng` enumerates the *unlabeled* count, but the canonical-labeling work
  per graph (linear in $n$ at best, often $n^2$ in practice) multiplied by
  even $10^{50}$ surviving candidates is infeasible.

**Verdict: do not propose this pipeline.** Document in the protocol that the
team has explicitly considered and rejected it.

### 2.2 CP-SAT enumeration via Role 4's encoding with model-blocking

Role 4 ships a CEGAR loop that finds *one* graph $G$ at a time satisfying
the conjunction $\{ \delta \ge 24, \, t\text{-critical}, \, (t-1)\text{-edge-
connected}, \, \overline{\operatorname{cr}}(G) < Z(t) \}$. Enumeration mode
runs the same loop and after each solve adds a *model-blocking* clause that
forbids that exact solution (and ideally its isomorphism class). The cost
profile:

- Each solve is whatever Role 4's CEGAR costs per solve. Plan v3 marks this
  as "at or beyond the boundary" of CP-SAT capability for $n \sim 50$,
  $m \sim 600$.
- The number of solutions to enumerate is unbounded a priori. The
  enumeration terminates either by exhausting the model count (which means
  the model count was small enough to enumerate, i.e. $\le 10^9$ in
  practice) or by the team giving up.
- A *naive* blocking clause forbids only the labeled solution. The CP-SAT
  model then re-finds the same unlabeled graph under a permutation of
  vertex labels. To avoid this, Role 4's encoding **must include
  static symmetry-breaking** (lex-leader on the adjacency matrix, or
  orbit-based dynamic SBPs). Otherwise the enumeration walks the full
  $S_{48}$-orbit of each unlabeled graph — a factor of $48!$ blow-up.
- *Dynamic* symmetry breaking via canonical-labeling rejection in the loop
  is the alternative: each candidate from Role 4 is canonicalized by Role 5
  and inserted into a dedup set; duplicates are blocked back into the SAT
  model. This is the "Role 5 dedups, Role 4 trusts" contract (see Section 6).

**Feasibility threshold.** Pure CP-SAT enumeration becomes infeasible when
the model count exceeds roughly $10^9$ — the dedup hash set in 16 GB RAM at
16 bytes per hash holds about $10^9$ entries, and each solver iteration is
not free. Once the model count exceeds $10^{10}$ we are into "this pipeline
does not terminate" territory unless symmetry breaking is near-perfect.

**Sub-feasibility threshold.** If Role 2's R1b restriction (Section 4) shrinks
the model count to $\le 10^6$ or so, CP-SAT enumeration becomes a reliable
generator and Role 5's role is reduced to canonical dedup + audit.

### 2.3 Custom orderly-generation (McKay-style canonical augmentation)

The McKay 1998 paper *Isomorph-free exhaustive generation* (JAlgorithms 26)
specifies the canonical-augmentation framework that `geng`, `plantri`,
`directg`, `genbg`, `multig`, etc. implement. The framework: enumerate
graphs by orderly extension from a smaller graph, accepting only those
extensions whose *added* vertex/edge is the canonical choice in the augmented
graph. This produces every unlabeled graph exactly once with no a-posteriori
dedup needed.

Tailoring this to $25$-criticality is **research-grade**, not standard. The
issues:

- Criticality is not a hereditary property — a $25$-critical graph plus one
  more vertex is *not* in general $25$-critical, and a $25$-critical graph
  minus one vertex drops in chromatic number. The McKay augmentation
  invariant (the new vertex is the canonical removal candidate) does not
  align with the natural criticality augmentation invariant.
- The Hajós-construction route gives an augmentation operator that
  *preserves* $25$-criticality, but is not exhaustive (not every
  $25$-critical graph is obtainable by Hajós moves from $K_{25}$, modulo
  the open Hajós-construction question).
- Plantri-style generation works only for planar graphs; we are looking for
  *non-planar* $25$-critical graphs, so plantri is the wrong tool. (It is
  the right tool only for the chromatic-conjecture variants in low-crossing
  classes, e.g. checking Albertson for $1$-planar at $t \le 7$.)

**Concrete proposal.** I will *not* commit to a custom orderly generator in
the 30-day window. I will commit to:

1. a reference implementation of canonical labeling via `nauty`/`Traces`
   adapter (Section 3);
2. a *post-hoc* dedup pipeline that consumes whatever Role 4 emits;
3. a scoped feasibility study for a Hajós-augmentation generator restricted
   to the R1b sub-family Role 2 picks. If the sub-family admits a clean
   augmentation operator (e.g. "all R1b graphs are obtained from $K_{25}$ by
   a bounded sequence of Hajós moves of type $X$"), this becomes a viable
   research project for months 4–9.

---

## 3. Coverage accounting protocol

This is the actual theorem-grade contribution from Role 5. The protocol must
let the team write a sentence of the form:

> *Theorem (coverage).* Let $\mathcal{F}_{t,n,P}$ be the set of unlabeled
> graphs $G$ on $n$ vertices that are $t$-critical, satisfy $\delta(G) \ge
> t - 1$, and satisfy structural predicate $P$. Then the enumeration
> pipeline of `work/05_enumeration/run_<id>.log` outputs every element of
> $\mathcal{F}_{t,n,P}$ exactly once, certified by canonical labeling $C =
> \mathrm{nauty}/\mathrm{Traces}$ with options $\langle \dots \rangle$. No
> isomorph was emitted twice and no element of $\mathcal{F}_{t,n,P}$ was
> rejected.

For this sentence to be a theorem and not a hope, six things are needed.

### 3.1 Canonical-form invariant

Use `nauty`'s `densenauty` (our density makes `Traces` not the right
choice). Canonical form = output of `densenauty(..., &options, ..., canon_g)`
with `options.getcanon = TRUE`. **Pin** `options.invarproc` (default
`NULL`), `options.defaultptn`, `options.digraph = FALSE`,
`options.maxinvarlevel` (default 0), and compile-time `MAXN`/`WORDSIZE`.
Hash the canonical bytes (Section 3.2).

### 3.2 Dedup hash strategy

Hash the canonical adjacency matrix (1128 bits = 141 bytes at $n = 48$)
with SHA-256 (32 bytes). Collision probability at $10^{12}$ entries
$\approx 10^{-55}$, less than a hardware cosmic-ray flip. BLAKE3 (16
bytes, $\approx 10^{-15}$ at $10^{12}$) is fine for prototyping; SHA-256
for theorem-grade.

**Do not** hash the graph6 string directly without canonicalization —
graph6 encodes a *labeled* graph, so one unlabeled graph has up to $48!$
graph6 strings; matches are coincidence, not correctness.

### 3.3 Audit log

Per-run log records, one line per emitted graph:

```
<seq>\t<source>\t<canon_sha256>\t<graph6>\t<filter_chain>\t<wall_time>
```

- `seq` — monotonic sequence ID, gives total ordering for replay.
- `source` — which generator (`role4_sat`, `r1b_hajos`, `r1c_random`, ...)
- `canon_sha256` — the dedup key.
- `graph6` — canonical-form graph6 string. (Yes, store the graph6 of the
  *canonical* labeling, not the input labeling. Verifiable downstream.)
- `filter_chain` — which acceptance / rejection filters fired and in what
  order.
- `wall_time` — for cost accounting.

Rejected isomorphs also get a log line with `source = duplicate_reject` and
a back-pointer to the first sequence ID. **The log is the proof that no
isomorph was double-counted.**

### 3.4 Replay determinism

Two failure modes for replay:

- **Solver non-determinism.** SAT/CP-SAT solvers are deterministic if the
  random seed is fixed and the parallelism is single-threaded. Role 4's
  CEGAR loop must run with `seed = N` and `num_workers = 1` for replay; the
  production parallel runs must serialize each worker's audit log
  separately and merge.
- **Canonical-labeling non-determinism.** `nauty`/`Traces` is deterministic
  for fixed compile-time options and fixed input. Pin the version (e.g.,
  nauty 2.8.9) and record the version in each run's log header. Different
  nauty versions may produce different canonical forms for the same
  unlabeled graph; the canonical-form *contract* is "two graphs are
  isomorphic iff their canonical forms are equal", which is preserved
  across versions, but the actual bytes differ.

Replay protocol: rerun with same seed, same nauty version, same compile
flags, single-threaded; check that the audit log is byte-identical modulo
timestamps. If not, the pipeline is non-deterministic and must be fixed
before producing theorem-grade output.

### 3.5 Coverage certificate

The audit log proves *injectivity* (no duplicates emitted). It does **not**
prove *surjectivity* (every element of $\mathcal{F}_{t,n,P}$ was emitted).
Surjectivity is the hard half. Two routes:

- **Generator-correctness proof.** Show that the generator's search space
  is a superset of $\mathcal{F}_{t,n,P}$. For SAT (Section 2.2), this
  reduces to showing the encoding is *complete* — every model of the SAT
  formula corresponds to a graph in $\mathcal{F}_{t,n,P}$ and conversely.
  Role 4 owns this.
- **Cross-validation against an independent generator.** If two independent
  generators (e.g., Role 4's SAT and a Hajós-augmentation generator) both
  output the same canonical multiset, that is empirical evidence of
  surjectivity. Not a proof, but high-confidence.

For R1c output to be coverage-certified, the team needs *both* an
injectivity proof (the audit log) and a surjectivity argument (the
encoding-completeness theorem from Role 4 plus a structural-completeness
theorem from Role 2). I cannot produce surjectivity alone.

### 3.6 What the audit certifies and what it does not

The audit log certifies:

- every emitted graph is in $\mathcal{F}_{t,n,P}$ (by the filter chain);
- no two emitted graphs are isomorphic (by the canonical-form dedup);
- the run is replayable bit-for-bit.

The audit log does **not** certify:

- that every graph in $\mathcal{F}_{t,n,P}$ was emitted (needs Role 2 + 4);
- that $\mathcal{F}_{t,n,P}$ is the full MCE residual at $(t, n)$ (needs
  Role 2's structural theorem that $P$ is wlog);
- that any emitted $G$ is or is not a counterexample (needs Role 3's
  certified lower bound).

---

## 4. Sub-family carve-outs (joint with Role 2)

For each plausible R1b restriction from `docs/plan.md` v3 R1b, my generation
strategy and an order-of-magnitude count estimate.

### 4.1 $K_{24}$-containing 25-critical graphs

If $G \supseteq K_{24}$ on a fixed 24-vertex set $S$, the remaining 24
vertices each have $\ge 24$ neighbors. Generation: fix the $K_{24}$, choose
neighborhoods $N(v) \subseteq V$ for $v \in V \setminus S$ with $|N(v)| \ge
24$, canonical-augment at each step. Raw multiplicity is $\binom{47}{24}^{24}
\approx 10^{336}$ before dedup; expected post-dedup count is still **at
least $10^{20}$**, not tractable without further restriction.

### 4.2 $K_{25}$-saturated (edge-minimal not 24-colorable)

Right class iff Role 2 can prove the MCE is edge-saturated relative to
$K_{25}$. Each such graph is built by Hajós moves from $K_{25}$. Plantri
does **not** apply (it is planar-only); we'd need a custom Hajós
augmentation. Expected count: unknown; the Hajós lattice on 48 vertices
has no known finite-depth bound.

### 4.3 Two disjoint $K_{12}$ joined by bipartite $B$

If $G = K_{12} \cup K_{12} \cup B$, the search reduces to enumerating
bipartite $B$ on $12 + 12$ vertices with min-degree $\ge 12$ via
`genbg -d12:12 12 12`. **Massively more tractable**, likely $\le 10^{15}$
graphs total. **But** Role 2 must certify that an MCE necessarily contains
two disjoint $K_{12}$ — probably **not** wlog, so this restriction covers
only a sub-family. The audit will say so explicitly.

### 4.4 Bounded vertex-cut structure

If Role 2 proves an MCE has a specified small vertex cut $S$ (despite
vertex connectivity not being forced — plan v3 F7), build $G$ as $G_1
\cup_S G_2$. Generation: feasible, count multiplicative over $G_1, G_2, S$.

### 4.5 Edge-connectivity exactly $t - 1 = 24$

Forced by Kostochka–Stiebitz so wlog, but does not appreciably shrink the
count (most degree-24 graphs are already 24-edge-connected). Useful as a
*filter*, not a *generator*.

### 4.6 Hajós-construction descendants of $K_{25}$

Apply Hajós moves to $K_{25}$ and descendants; each move preserves
25-chromaticity. **Conditional** on Hajós-construction-completeness for
$t = 25$, which is open (Catlin 1979 refuted the subdivision form for
$t \ge 7$; the construction form for chromatic-$t$ critical graphs is a
separate open question). Any output must disclose this condition.

**Operational stance.** Role 2 must pick the R1b restriction by month 1
(Section 7.1).

---

## 5. Graph6 / sparse6 IO and storage

### 5.1 Per-graph byte cost

graph6 encodes an undirected simple graph using $\lceil (n + \binom n2)/6
\rceil$ bytes plus newline. For $n = 48$: $\binom{48}{2} = 1128$ bits =
$\lceil 1128/6\rceil = 188$ payload chars + 1 char for $n$ + 1 newline =
**190 bytes per graph**. sparse6 is *larger* at our density ($|E| \ge 576$,
density $\ge 0.51$) — use graph6. Binary packed (141 + 4 bytes) saves
little; graph6 is the de facto standard and interoperates with
`nauty`/`Traces`/`showg`.

### 5.2 Expected on-disk size and sharding

For an R1b sub-enumeration of $10^9$ graphs: graph6 = 190 GB; audit log
(Section 3.3, ~200 bytes/line) = 200 GB; total ~400 GB. At $10^{12}$ this
is 400 TB and exceeds any plausible Role 6 budget — the team must either
shrink the sub-family or stream-process without storing the full list.

For parallel consumption by Role 3, shard graph6 by canonical-form hash
prefix (SHA-256 prefix mod $K$ gives uniform partitioning, dedup-clean
across shards). Recommended 64–128 shards per campaign, each 1–10 GB,
sized for one Role 3 worker's RAM. **Never** write one file per graph
($10^9$ inodes exhausts most filesystems); use a single sharded graph6
file per shard.

Sequential read of 190 GB on NVMe at 3 GB/s = 63 s, so IO is not the
bottleneck — downstream lower-bound computation is.

---

## 6. Isomorphism collisions as a failure mode

Role 4's CP-SAT enumeration with model-blocking emits *labeled* graphs. If
its symmetry breaking is incomplete, the same unlabeled graph appears under
multiple vertex labelings.

**Contract.**

- **Role 4** owns first-line symmetry breaking via static SBPs (lex-leader
  on the adjacency matrix). It reports the expected duplicate factor.
- **Role 5** owns second-line dedup via canonical-form hashing (Section 3).
  Every emission is canonicalized; duplicates are rejected and logged.
- **Back-channel.** When Role 5 rejects a duplicate, it sends a blocking
  clause back to Role 4's SAT instance forbidding that *canonical* graph
  (not just the labeled instance), so Role 4 does not rediscover the same
  isomorphism class.

**Replay.** The dedup decision is part of the audit log (Section 3.3).
Replay: rerun Role 4 with same seed and same blocking-clause sequence;
rerun Role 5 with same nauty version; confirm the audit log is
byte-identical modulo timestamps. Pitfall: an asynchronous back-channel
must be serialized into the audit log so replay is from a single linear
log.

**Broken-SBP regimes.** Perfect SBP: 0 duplicate rejections. No SBP: each
canonical class is rediscovered up to $|\mathrm{Aut}(G)|^{-1}\cdot n!$ times;
for typical $25$-critical graphs $|\mathrm{Aut}(G)|$ is small (1 or 2), so
the duplicate factor is essentially $48! \approx 10^{61}$ — pipeline does
not terminate. **Diagnostic:** if the duplicate-rejection rate exceeds
~50%, Role 4 must fix its SBP before continuing.

---

## 7. Dependencies

### 7.1 Asks of Role 2 (structural restriction) — month 1

1. A precise structural predicate $P(G)$ for the R1b sub-family. Pick one
   from Section 4 (or propose another) and commit. Without this I cannot
   write a tailored generator.
2. A *coverage statement*: is $P$ wlog at $(t, n)$, or only a sub-family?
   If the latter, what complement?
3. The forced-properties checklist at $(25, 48)$: $\delta \ge 24$,
   $(t-1)$-edge-connectivity, 2-connectivity, $|E| \ge 576$, no $K_{25}$
   subgraph (vacuous since $|V(K_{25})| = 25 < 48$), etc., so the generator
   and the audit filter agree on what to enforce.

### 7.2 Asks of Role 4 (CEGAR SAT) — months 1–2

1. **(M1)** Interface contract: graph6 stdout, one labeled solution per
   line, plus optional solver-state fields for the dedup back-channel.
2. **(M1)** Symmetry-breaking specification (lex-leader on adjacency
   matrix? orbit-based? none?) and the expected duplicate factor.
3. **(M1)** Dedup back-channel format. Proposed: JSON-lines RPC or UNIX
   FIFO carrying canonical adjacency-matrix bitstrings.
4. **(M2)** The encoding of $t$-criticality: $\forall v\,\chi(G - v) < t$
   via inner SAT (CEGAR), or a structural surrogate? The choice determines
   whether Role 5's generator and Role 4's verifier agree on the
   sub-family.

### 7.3 Asks of Role 6 (storage)

**(M1)** Storage budget (GB/TB), inode budget, parallel shard-write
throughput target, audit-log archival policy. **(M3)** Provision for the
largest realistic R1b campaign (Section 5.2): 200 GB – 2 TB depending on
Role 2's choice.

### 7.4 Asks of Role 3 (lower-bound pipeline) — month 1

1. Input format confirmation: graph6, one graph per line, canonical
   labeling.
2. Per-worker throughput estimate at $n = 48, m \ge 576$ (sets the shard
   sizing).
3. Output schema: at minimum $(G, \underline{\operatorname{cr}}(G),
   \overline{\operatorname{cr}}(G), \text{certificate})$, joinable to the
   audit log on the canonical-form hash.

---

## 8. First 30-day deliverables

Five concrete, falsifiable items.

**D1 (week 1) — `nauty` canonical-form Python adapter.** Wrap `pynauty` or
a `ctypes` binding to nauty 2.8.9. Function `canonical_form(g) -> bytes`
returning the canonical adjacency-matrix bitstring; SHA-256 on top.
Validate: all unlabeled graphs on $n \le 6$ canonicalize to distinct forms
(known counts from OEIS A000088); the Petersen graph reports
$|\mathrm{Aut}| = 120$.

**D2 (weeks 1–2) — Test fixtures: small $t$-critical graphs.** Known
testable corpora:

- $K_t$ for all $t \le 26$ (trivially $t$-critical).
- Mycielski $M_4$ = Grötzsch (11 vertices, 4-critical), $M_5$, $M_6$.
  $M_t$ has $|V(M_t)| \approx 3 \cdot 2^{t-2}$, so $|V(M_{25})| \approx 5
  \cdot 10^7$ — **no Mycielski test fixture at the target order exists**.
- Royle's catalogues of small 4- and 5-chromatic critical graphs (works
  through $t \le 10$).
- Toft graphs for $t = 4$ with specified edge counts.

State honestly: small-case validation goes up to $t \le 10$; at $t = 25$
the test corpus is essentially *just* $K_{25}$ plus whatever Role 2 hands
me from R1b. We are flying without a strong empirical safety net at the
target order.

**D3 (week 2) — Dedup pipeline + audit log.** Implement Sections 3.2/3.3:
SHA-256 dedup of canonical forms, line-per-graph audit log, JSON header
with run metadata (nauty version, compile flags, seed, date). Validate on
$10^4$ random graphs from `genrang` against `geng | sort | uniq`.

**D4 (week 3) — graph6 throughput benchmark + sharder.** Measure: graph6
read/write, canonical-form throughput (graphs/sec at $n = 48$), SHA-256
throughput. Estimate end-to-end pipeline throughput for an R1b campaign.
Sharder: graph6 stdin -> $K$ shard files keyed by canonical-hash prefix.

**D5 (week 4) — Coverage-protocol document.** A short formal write-up of
the Section 3 contract, suitable for inclusion in any paper that cites a
Role 5 enumeration. Required so Role 4's SAT result and any Role 2
structural theorem are jointly citable.

---

## Self-assessment and honest caveats

- **Counts.** I have not promised a count of $25$-critical graphs on 48
  vertices, because no honest one exists. I have given a lower bound (small
  positive integer, from $K_{25}$ + Hajós descendants) and a trivial upper
  bound ($10^{278}$). Anyone presenting a tighter number without a
  certificate is wrong.
- **Tooling.** `nauty`/`Traces` works at $n = 48$ per-graph in
  milliseconds; canonical labeling is not the bottleneck. The bottleneck is
  the *number of graphs Role 4 emits*, which is bounded by the structural
  restriction from Role 2.
- **Coverage gaps.** The dangerous failure mode is not "I generated the
  wrong graphs" (caught by the audit) but "I missed an entire sub-family
  because Role 2's predicate $P$ is not wlog". This is a Role 2 problem
  that becomes a Role 5 problem when the team forgets the audit only
  certifies injectivity.
- **Hajós completeness.** If R1b restricts to Hajós descendants of
  $K_{25}$, the coverage statement is conditional on a known-open
  construction-completeness question. Disclose this in any output.
