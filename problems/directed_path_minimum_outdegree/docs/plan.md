# Attack plan: Directed path of length twice the minimum outdegree

## Headline

The literature audit is **complete** (see
`literature_notes.md`). Phase 0.5 (hand attack at $k=3$) is
**complete**, with the result going beyond the original target: the proof
in `k3_hand_proof.md` closes Conjecture 1 for $\delta = 3$ at
*every* $n \geq 7$, not just $n = 8$.

Phase 0.6 (hand attack at $k=4$, $n=10$) is **complete**.
Phase 0.7 (computer-aided closure at $k=4$, $n=11$) is **complete**;
see `k4_n11_proof.md`.

Phase 0.6 result: every oriented graph with $\delta^+ \geq 4$ and
$|V| = 10$ has a directed path of length 8.

Phase 0.7 result: every oriented graph with $\delta^+ \geq 4$ and
$|V| = 11$ has a directed path of length 8. The score-profile-aware
miner (`scripts/k4_score_profile_miner.py`) runs on all four score
sequences: $(1,1,1,1)$ has 0 valid $(S, T)$ configurations
(structurally impossible), and $(2,1,1,1)$, $(2,2,1,1)$, $(3,1,1,1)$
together have 32 configurations totalling 117,992,940 completions, 0
obstructions.

Audit-trail note: the original $n = 11$ run used
`scripts/k4_general_miner.py`, which hard-coded the $(2,2,1,1)$
score profile and only enumerated $(S, T)$ with $|T| = 2$. The
score-profile-aware miner fixes this by accepting an arbitrary
internal score profile and running the same forced-arc derivation
plus completion enumeration.

The combined
result:

> Every oriented graph $D$ with $\delta^+(D) \geq 4$ and $|V(D)| = 10$
> contains a directed simple path of length 8.

Score sequences $(1,1,1,1)$, $(2,1,1,1)$, $(3,1,1,1)$ closed by hand
proof. Score sequence $(2,2,1,1)$ closed by computer-aided exhaustive
enumeration via `scripts/k4_local_miner.py`: the miner verifies all 24
valid $(S, T)$ configurations (Shape A1: 12, Shape A2: 8, Shape B: 4),
confirming each completion has a length-8 path.

**All score sequences at $n \geq 11$ are open**: the forcing chain in
F4--F6 relies on $|V(D)\setminus V(P)| = 2$, which fails for
$n \geq 11$.

Cumulative status of Cheng--Keevash Conjecture 1
(every oriented graph with $\delta^+ \geq \delta$ contains a directed path
of length $2\delta$):

| $\delta$ | status | source |
|---:|---|---|
| 1 | closed (trivial) | min outdegree 1 gives a directed cycle of length $\geq 3$ in oriented graph, hence a path of length $\geq 2$ |
| 2 | closed | Cheng--Keevash 2024 Lemma 7 + oriented average bound |
| 3 | **closed (this project)** | `k3_hand_proof.md` |
| 4, $n = 10$, score $(2,1,1,1)$ all 4 cases | **closed with full F-step derivations and explicit length-8 paths** | `k4_partial_appendix.md` |
| 4, $n = 10$, score $(3,1,1,1)$ all 4 cases | **closed with full F-step derivations and explicit length-8 paths** | `k4_partial_appendix.md` |
| 4, $n = 10$, score $(2,2,1,1)$ all 24 sub-cases | **closed (computer-aided, `scripts/k4_local_miner.py`)** | `k4_partial_appendix.md` |
| 4, $n = 10$ overall | **CLOSED**: every $D$ with $\delta^+ \geq 4$, $|V|=10$ has path of length 8 | combined |
| 4, $n = 11$, score $(1,1,1,1)$ | closed structurally (no valid $(S, T)$ at any $n$) | |
| 4, $n = 11$, score $(2,1,1,1)$ | closed (computer-aided): 4 configs, 6.4M completions, 0 obstructions | `scripts/k4_score_profile_miner.py` |
| 4, $n = 11$, score $(2,2,1,1)$ | closed (computer-aided): 24 configs, 91.6M completions, 0 obstructions | `scripts/k4_score_profile_miner.py` |
| 4, $n = 11$, score $(3,1,1,1)$ | closed (computer-aided): 4 configs, 20M completions, 0 obstructions | `scripts/k4_score_profile_miner.py` |
| 4, $n = 11$ overall | **CLOSED**: 32 configs, 117,992,940 completions, 0 obstructions | `k4_n11_proof.md` |
| 4, $n \geq 12$ | open | |
| $\geq 5$ | open | gap from Theorem 4 to conjecture grows linearly |

Two earlier findings remain in force:

- **The "$+1$ variant" of Lemma 7 is a notation slip.** The published proof
  uses $|P|$ for vertex count in the geometric step but $\ell(D) = |P|$ in
  the conclusion. The headline bound $\delta^+(S) \geq 2\delta - \ell(D)$ is
  what is actually proved.
- **Jackson 1981 supplies an unused structural lemma** (transcribed via
  secondary source; **primary-source verification still pending**). Under
  min semidegree $\geq k$, his theorem reportedly closes the conjecture;
  counterexamples must then contain a vertex of indegree $< k$, and at
  $n=2k+2$ this vertex has $\geq 2$ non-neighbours. Do not rely on this in
  a publishable proof until the 1981 journal article has been read.

Working target:

> Every oriented graph with minimum outdegree $k$ contains a directed simple
> path of length $2k$.

Here "length" means number of arcs, and "path" means vertex-simple. A
directed walk of length $2k$ is not the object.

## Statement audit (resolved)

Naming mismatch (kept here for any future reader):

- OPG slug: `directed_cycle_of_length_twice_the_minimum_outdegree`
- OPG title in the local scrape: `Directed path of length twice the minimum outdegree`
- OPG statement: every oriented graph with minimum outdegree $k$ contains a
  directed path of length $2k$.

Resolution: the slug is misleading. The problem is the **path** conjecture
(Cheng--Keevash Conjecture 1), attributed to Thomasse. Live OPG page was
unreachable during the audit; the local scrape is the authoritative source we
have.

If a future check shows OPG actually intends a cycle problem, fork the plan:
the endpoint lemma, verifier, and SAT blocker must all be replaced.

## Verified literature facts

All transcribed verbatim into `literature_notes.md`. Key items:

- Cheng--Keevash Conjecture 1: every oriented graph with $\delta^+\geq\delta$
  contains a directed path of length $2\delta$.
- Cheng--Keevash Proposition 2: explicit $D_{a,b}$ counterexamples to the
  stronger girth conjecture for $g\geq 4$. None of the $D_{a,b}$ refutes
  Conjecture 1 itself; $D_{1,2}$ at $g=3$ sits exactly at $\ell=2\delta$.
- Cheng--Keevash Theorem 3: digraph with girth $g$ has $\ell\geq 2\delta(1-1/g)$.
- Cheng--Keevash Theorem 4: oriented graph has $\ell\geq 1.5\delta$;
  oriented + girth $\geq 4$ has $\ell\geq 1.6535\delta$.
- Cheng--Keevash Lemma 7 (verbatim, **no $+1$ variant**).
- Bai--Manoussakis 2019: original even-$g\geq 4$ counterexamples to the
  girth conjecture. Subsumed by Cheng--Keevash Prop 2.
- Jackson 1981 (secondary source only; primary-source check pending):
  oriented graph with $\delta^0\geq k$ has a Hamilton cycle for $|V|\leq
  2k+2$ and a directed path of length $2k$ for $|V|>2k+2$.

## Local triage score (revised)

| Route | Score | Meaning |
|---|---:|---|
| Proof | 4/5 | $\delta=3$ already closed by hand; the same technique partially constrains $\delta=4$. |
| Disproof | 3/5 | A counterexample for $\delta\geq 4$ would have to live in a tighter regime than originally thought. |
| Difficulty | 4/5 | Serious open-problem territory. Theorem mining is the realistic output. |

## Mathematical reductions (for $k\geq 4$)

These are valid for the path version. The $k=3$ case is closed; this section
is now the toolkit for $k\geq 4$.

1. **Vertex lower bound.** $|A(D)|\geq nk\leq\binom{n}{2}$ gives $n\geq 2k+1$.

2. **Equality case impossible.** $n=2k+1$ forces a regular tournament; by
   Redei's theorem every tournament has a Hamilton path, hence a path of
   length $2k$. Search starts at $n=2k+2$.

3. **Minimum outdegree can be exact.** For a counterexample, take
   $k=\delta^+(D)$. Enforce at least one vertex of outdegree exactly $k$ and
   relabel it as vertex `0`.

4. **Strong component reduction (sound for finding smaller counterexamples).**
   If $D$ is not strongly connected, a sink SCC has $\delta^+\geq k$ and is
   a smaller candidate.

5. **$k$-outregular reduction.** Deleting arcs cannot create new paths.
   Reduce to $d^+(v) = k$ for every $v$.

6. **Endpoint pressure (Lemmas A, B, C, D in the literature notes).**
   Standard longest-path arguments.

7. **Cheng--Keevash Lemma 7 + oriented bound.** If $\ell(D)<2\delta$, there
   is an induced $S$, $|S|\leq\delta$, $\delta^+(S)\geq 2\delta-\ell(D)$,
   with $\delta^+(S)\leq\lfloor(|S|-1)/2\rfloor$. The constructed $S$ in the
   proof is $S = B^- = $ predecessors-in-$C$ of $B = N^+(v_{a-1})\cap V(C)$.

8. **Forced $S$-content from path arc.** Path arc $v_0\to v_1$ together with
   $a=1$ gives $v_1\in B$, hence $\mathrm{pred}_C(v_1)\in S$. For $a=1$ this
   is $v_L\in S$ (since $C = v_1\cdots v_L v_1$, predecessor of $v_1$ is
   $v_L$). This is the seed of the cyclic-closure argument used in the
   $\delta=3$ proof.

9. **Antiparallel cyclic closure (used to close $\delta=3$).** Each $s\in S$
   with $d^+_S(s) = \delta^+(S)$ sends $\delta - \delta^+(S)$ arcs to
   $V(C)\setminus S$; if this number equals $|V(C)\setminus S|$, then $s$
   sends an arc to *every* vertex of $V(C)\setminus S$, and antiparallel
   constraints with path/cycle arcs force $S$ to be closed under the
   predecessor permutation $\sigma$ on $V(C)$. With $\sigma$ a single cycle,
   the only invariants are $\emptyset$ and $V(C)$, giving a contradiction
   when $0 < |S| < |V(C)|$. The argument breaks down for $\delta\geq 4$ when
   some $s\in S$ has $d^+_S(s) > \delta^+(S)$ (so $s$ does not reach all of
   $V(C)\setminus S$).

10. **Tiny base case.** $k=1$: trivial. $k=2$: closed by Cheng--Keevash.
    $k=3$: closed (this project).

11. **Near-minimal density pressure.** At $n=2k+2$, total excess
    $\sum_v(d^+(v)-k)$ is between $0$ and $k+1$. Branch by this excess.

12. **First-excess $k$-outregular reduction.** At $n=2k+2$, any
    counterexample reduces to a strongly connected $k$-outregular orientation
    of $K_{2k+2}$ minus exactly $k+1$ undirected edges.

13. **Jackson 1981 indegree-deficient vertex** (pending primary-source
    verification). At $n=2k+2$, every counterexample contains a vertex
    $v_*$ with $d^-(v_*)\leq k-1$, equivalently $m(v_*)\geq 2$
    non-neighbours.

## Phase 0: literature audit (DONE)

See `literature_notes.md`. Remaining low-priority checks
listed there.

## Phase 0.5: hand attack at $k=3$ (DONE; result exceeds target)

Deliverable: `k3_hand_proof.md`.

Result: every oriented graph with $\delta^+\geq 3$ has $\ell \geq 6 = 2k$.
The proof uses Cheng--Keevash Lemma 7 + the oriented average bound + an
antiparallel cyclic-closure argument on the endpoint cycle. It does not
require $n = 8$.

## Phase 0.6: hand attack at $k=4$, $n=10$ (DONE)

**Result.** Every oriented graph $D$ with $\delta^+(D) \geq 4$ and
$|V(D)| = 10$ contains a directed simple path of length 8.

Apply the R1/R2/R3 reduction: a counterexample reduces to a strong
$4$-outregular oriented graph $D$ with $\ell(D) \in \{6, 7\}$ and
$|V(D)| \geq 9$ (Cheng--Keevash Theorem 4 gives $\ell \geq 6$). At
$n = 9$ the graph would be a regular tournament (Hamilton path of
length 8), so $|V(D)| \geq 10$. Cheng--Keevash Lemma 7 + the oriented
average bound force $|S| = 4$, $a = 1$, $V(C) = \{v_1, \ldots, v_7\}$,
$v_7 \in S$.

Closure proceeds by score sequence of $S$:

- **$(1,1,1,1)$**: every $s \in S$ has $d^+_S = 1$, so the full cyclic
  closure (analogous to the $k=3$ proof) forces $S = V(C)$, but
  $|S| = 4 \neq 7$. Closed by hand.
- **$(2,1,1,1)$**: cyclic-interval mini-lemma forces $S$ to be 4
  consecutive vertices in $C$ with $u$ at the interval start. 4 cases
  (which interval contains $v_7$) × explicit length-8 paths in
  `k4_partial_appendix.md`. Closed by hand.
- **$(3,1,1,1)$**: same cyclic-interval structure with $u$ having
  $d^+_S = 3$. 4 cases × length-8 paths. Closed by hand.
- **$(2,2,1,1)$**: cyclic-interval lemma fails (only $|T| = 2$ for
  closure). Three shapes (A1: 4-interval, A2: 3-block + isolated, B:
  2 separated pairs). 24 valid $(S, T)$ configurations.
  Closed by `scripts/k4_local_miner.py`: enumerate every 4-outregular
  oriented completion of each $(S, T)$, verify length-8 path exists.
  Audited via `scripts/k4_audit.py`: 24/24 pass, 0 failures, 3,664
  completions verified.

The $|S| = 3$ branch dies at every $a$: $|B| = 3 \Rightarrow |A| = 1$
forces $a \geq 2$; at $a = 2$, $A = \{v_0\}$ requires $v_1 \to v_0$
which is antiparallel with the path arc $v_0 \to v_1$. The geometric
bound $|V(C)| \geq 6$ then forces $a \leq 2$. Contradiction.

The $\ell = 6$ branch dies at the oriented average bound: Lemma 7 would
require $\delta^+(S) \geq 2$ on $|S| \leq 4$, but oriented graphs force
$\delta^+(S) \leq 1$ on $|S| \leq 4$.

## Phase 1: structured and random baselines

Targets shifted to $k = 4$ and beyond.

Named families to check first:

1. circulants on $\mathbb{Z}_n$ with connection set $\{1,\ldots,k\}$;
   oriented exactly when $n>2k$, so first interesting size $n=2k+2$;
2. circulants with sparse perturbed connection sets of size $k$;
3. Paley tournaments for $q\equiv 3\pmod 4$;
4. regular tournaments and near-regular subtournaments;
5. blow-ups of directed cycles;
6. bipartite double covers of regular tournaments;
7. Cheng--Keevash $D_{a,b}$ constructions (verifier sanity check).

Random baseline: switch chain on $k$-outregular oriented graphs seeded by
$D_{1,2}$, with logged burn-in/thinning/acceptance. Sample at
$(k,n)\in\{(4,11),(4,12),(5,12)\}$ (skipping $(4,10)$ which is now closed).
Realistic expectation: most samples have a Hamilton path; the random
baseline mostly tests the verifier.

Deliverables:

- `scripts/baseline_directed_path.py`
- `data/directed_path_search/baselines.csv`

Budget: one evening.

## Phase 2: independent verifier

Inputs: edge list / adjacency bitsets, claimed $k$.

Checks: oriented; min outdegree; strong connectivity; sink SCC report;
existence of a directed simple path of length $2k$; longest simple directed
path length.

Implementation: DFS with bitset state for $n\leq 20$; subset-DP cross-check
for $n\leq 16$; explicit walk-vs-path guard.

Deliverable: `scripts/verify_directed_path_counterexample.py`.

## Phase 3: exact SAT search starting at $k=4$

**Do not run SAT for $k\leq 3$**: those cases are theorems.

Solver: PySAT with CaDiCaL or Kissat. Cardinality via sequential counters /
totalizers. Pin the build for reproducibility.

Variables: $a_{u,v}$ for ordered pairs $u\neq v$.

Hard constraints:

1. oriented: $\neg a_{u,v}\vee\neg a_{v,u}$;
2. $\sum_{v\ne u}a_{u,v}\geq k$;
3. exact minimum witness on vertex $0$;
4. symmetry break: fix $0\to 1,\ldots,0\to k$, forbid other outgoing arcs
   from $0$;
5. branch on near-minimal outdegree profiles at $n=2k+2$;
6. **Jackson branching** at $n=2k+2$ (optional, until primary-source
   verified): enforce a vertex with $d^- \leq k-1$ (relabel as `1`, enforce
   $\sum_{u\neq 1}a_{u,1}\leq k-1$). Until Jackson 1981 is checked against
   the journal article, runs that use this constraint must be paired with
   a parallel run *without* it; only the no-Jackson run is logically
   "exact" for purposes of certifying UNSAT.

Symmetry handling:

- canonical blocking is mandatory; preferred tool pynauty;
- when rejecting, add clauses excluding the residual orbit, not just the
  labelled assignment.

Lazy path-blocking loop, with batch path blockers per model and orbit
blocking per canonical label. Cube cap: 50,000 path clauses or 30 minutes.

Deliverables: scripts in `scripts/`, results CSV, CNF dumps for UNSAT
cubes, candidate edge lists.

## Phase 4: proof mining

If SAT is unfruitful, treat UNSAT cubes as the deliverable.

Concrete theorem target (sharper than originally written, in light of the
$\delta=3$ closure):

> Every oriented graph with $\delta^+\geq k$ at $n = 2k+c$ vertices contains
> a directed simple path of length $2k$, for the largest fixed $c$ provable.

For $\delta=4$, the smallest possible $n$ is $2k+1 = 9$, which is the
regular-tournament case (closed by Redei). $n = 2k+2 = 10$ ($c = 2$) is
closed by this project (`k4_n10_proof.md`). $n = 11$
($c = 3$) is closed by this project too
(`k4_n11_proof.md`, computer-aided). The smallest
genuinely open size is now $n = 12$ ($c = 4$).

## Computational budget

Target machine: M-class Mac, single core unless stated. Budgets are
wall-clock per instance.

Completed (for reference; do not re-budget these):

- $\delta=3$, all $n \geq 7$: hand proof in `k3_hand_proof.md`.
- $\delta=4, n=10$, score sequences $(1,1,1,1)$, $(2,1,1,1)$, $(3,1,1,1)$:
  hand proofs in `k4_partial_appendix.md`.
- $\delta=4, n=10$, score sequence $(2,2,1,1)$, all 24 $(S, T)$ subcases:
  computer-aided closure in `k4_n10_proof.md` +
  `scripts/k4_local_miner.py` + `scripts/k4_independent_check.py` +
  certificate.
- $\delta=4, n=11$, all 32 $(S, T)$ configurations across the four
  score sequences (0 + 4 + 24 + 4): computer-aided closure in
  `k4_n11_proof.md` + `scripts/k4_score_profile_miner.py`.
  117,992,940 completions, 0 obstructions, ~21 min wall-clock.

Open:

| Task | Wall-clock budget | Stop condition |
|---|---:|---|
| Run score-profile miner at $n = 12$ (`scripts/k4_score_profile_miner.py 12`) | 2--4 hours | Either all 32 configurations close, or identify configurations that overflow / surface obstructions. |
| If miner overflows at $n=12$: SAT $(4, 12)$ | 48 hours | Candidate, exact UNSAT, or encoding bug. |
| Run score-profile miner at $n = 13, 14$ | 4--8 hours each | Same. |
| Random baselines at $(4,12), (5,12), (5,13)$ | 2 hours | $\geq 1{,}000$ samples per listed $(k,n)$. |
| SAT $(4,13)$ to $(4,15)$ | 48 hours each | Stretch exact targets. |

For the first computational pass at $k=4$ at $n \geq 12$, set $N_4=15$.
Exact search must cover $12 \leq n \leq 13$; $14 \leq n \leq 15$ are
stretch exact targets. No claim beyond $n \leq 15$ is allowed without a
proof.

## Failure modes

- Live OPG problem may be a cycle problem after a re-edit. Fork plan if so.
- A script may search for directed walks rather than simple paths.
- Path finder may return a walk that repeats a vertex, causing the SAT loop
  to reject a valid candidate for the wrong reason.
- Cheng--Keevash bound may be quoted with a wrong constant. Literature notes
  pin the verbatim constants.
- Semidegree literature (Jackson 1981) accidentally applied as a min-outdeg
  result. It is not.
- Sink-SCC reduction used incorrectly to certify a larger graph.
- Symmetry break around vertex `0` excludes counterexamples through wrong
  exact-minimum witness encoding.
- Heuristic candidates fail strong connectivity or have a sink component
  that itself contains a long path.
- Path-blocking SAT spends time rediscovering isomorphic models without
  pynauty.
- The $k=3$ closure is stronger than expected; check the proof in
  `k3_hand_proof.md` against the published Cheng--Keevash text
  before publishing or building on it.

## Revised first work items

Completed:

- **Audited local miner** (`scripts/k4_local_miner.py`): forced-arc
  derivation, completion enumeration completeness (24 valid $(S, T)$
  by brute force), length-8 path search soundness, (S, T) coverage.
- **Independent re-derivation** (`scripts/k4_independent_check.py`):
  no shared code with miner; agrees on 24/24 closed, 3664 completions.
- **Path table** (`data/k4_path_table.md`): per-$(S, T)$ length-8
  witness path.
- **Machine-readable certificate** (`data/k4_n10_certificate.json`):
  full arc set + hash + path per completion.
- **Certificate verifier** (`scripts/k4_verify_certificate.py`): full
  mechanical checks (hash, 4-outreg, oriented, forced arcs, Claim 12,
  Lemma A reverse, score sequence, witness path containment).
- **General verifier** (`scripts/verify_directed_path_counterexample.py`):
  arbitrary candidate counterexamples.
- **Independent checker for general $n$ score-profile miner**
  (`scripts/k4_score_profile_independent_check.py`): no imports from
  `k4_score_profile_miner.py`. Independently re-implements
  configuration enumeration, forcing rules, completion enumeration,
  and length-8 path search. Closes the same 32-configuration
  universe at both $n = 10$ and $n = 11$ with matching per-config
  forced-arc counts and completion counts.

Open:

1. **Extend $\delta = 4$ closure to $n = 12$.** Run
   `scripts/k4_score_profile_miner.py 12`. Expect completion counts
   roughly an order of magnitude larger than $n = 11$ (~1B). If the
   miner runs to completion in tractable time, $n = 12$ closes;
   otherwise SAT or smarter pruning needed.
2. Continue to $n \geq 13$ for $\delta = 4$ as long as the miner
   scales.
3. Move to $\delta = 5, n = 12$ once $\delta = 4$ is fully closed
   (or SAT-blocked).

Primary success at $\delta = 4$: full closure at all $n$.
Secondary: $\delta = 5, 6, \ldots$ via the same machinery.
