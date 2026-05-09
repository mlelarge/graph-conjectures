# Conjecture 1 for $\delta = 4$ at $n = 10$

## Theorem

> Every oriented graph $D$ with $\delta^+(D) \geq 4$ and $|V(D)| = 10$
> contains a directed simple path of length $8$.

This is the $\delta = 4, n = 10$ case of Cheng--Keevash Conjecture 1
(Thomassé's path conjecture for oriented graphs).

The proof combines hand argument with a single computer-aided lemma
(the $(2,2,1,1)$ score-sequence case). The computational step is
auditable and reproducible from the scripts in this repository.

## Notation

- $D$: oriented graph (no antiparallel arcs, no loops).
- $\delta^+(D) = \min_v d^+(v)$: minimum out-degree.
- $\ell(D)$: maximum length (in arcs) of a directed simple path.
- For an induced subgraph $S \subseteq V(D)$, $d^+_S(v) = |N^+(v) \cap S|$.
- $V(P), V(C)$: vertex sets of a path/cycle.

We adopt Cheng--Keevash 2024 notation: $P = v_0 v_1 \cdots v_{\ell(D)}$
is a longest directed simple path in $D$, $a = \min\{i : v_{\ell(D)} \to
v_i\}$ is the first-return index, and $C = v_a v_{a+1} \cdots v_{\ell(D)}
v_a$ is the resulting cycle. The construction defines $A, B, B^-, S$
as in Section 4 of [arXiv:2402.16776v4](https://arxiv.org/abs/2402.16776);
in particular Claims 11 and 12 there give $N^+(v_{a-1}) \subseteq V(P)$
and $N^+(B^-) \subseteq V(C)$.

## Reductions to strong 4-outregular $n = 10$

**R1.** Suppose $D_0$ is a counterexample to the theorem at $\delta = 4$:
$\delta^+(D_0) \geq 4$ and $\ell(D_0) \leq 7$. Pass to a sink strongly
connected component $H_0$ of $D_0$. Out-arcs of a sink SCC stay inside,
so $\delta^+(H_0) \geq 4$. Paths in $H_0$ are paths in $D_0$, so
$\ell(H_0) \leq 7$.

**R2.** Choose, for each $v \in H_0$, exactly four outgoing arcs and
delete the rest. The spanning subdigraph $H_1$ has $d^+(v) = 4$ for
every $v$, but is not necessarily strong. Deleting arcs cannot create
new paths, so $\ell(H_1) \leq \ell(H_0) \leq 7$.

**R3.** Pass to a sink SCC $D$ of $H_1$. By the sink-SCC property in
$H_1$, every $v \in D$ has all four of its $H_1$-out-arcs inside $D$.
Hence $D$ is $4$-outregular. $D$ is oriented (subgraph of an oriented
graph), strongly connected (SCC by definition), $\ell(D) \leq 7$.

By Cheng--Keevash Theorem 4 applied to $D$ (oriented, $\delta^+ \geq
4$): $\ell(D) \geq \lceil 1.5 \cdot 4 \rceil = 6$. The oriented average
bound forces $|V(D)| \geq 2\delta + 1 = 9$.

**Sink SCC has order at least 10.** If $|V(D)| = 9$, then
$|A(D)| = 4 \cdot 9 = 36 = \binom{9}{2}$, so $D$ is a tournament — in
fact a regular tournament (all out-degrees equal $\delta = 4$). Every
regular tournament is strongly connected (Camion 1959) and has a
Hamilton directed path (Redei 1934) of length $|V| - 1 = 8$. So
$\ell(D) \geq 8$, contradicting $\ell(D) \leq 7$.

Hence $|V(D)| \geq 10$. Since the original graph has
$|V(D_0)| = 10$ and $D$ is an induced/sink SCC subgraph of $D_0$,
$|V(D)| \geq 10$ forces $|V(D)| = 10$. **The proof in this file
closes the case $|V(D)| = 10$.** The remaining cases $|V(D)| \geq 11$
arise from larger $D_0$ and are open.

## Setup at $n = 10$

Set $|V(D)| = 10$. Then $\binom{10}{2} = 45$, $|A(D)| = 40$, so $D$
has exactly $5$ non-edges (unordered pairs not connected by any arc).
Suppose $\ell(D) = 7$ (since $\ell(D) \in \{6, 7\}$; we handle
$\ell = 6$ in Lemma 1 below).

Take a longest directed simple path $P = v_0 v_1 \cdots v_7$ in $D$,
and among all such, choose one whose cycle bound $|C|$ (with $C =
v_a v_{a+1} \cdots v_7 v_a$) is maximal. Set $V(P) = \{v_0, \ldots,
v_7\}$ and $V(D) \setminus V(P) = \{x, y\}$.

By Cheng--Keevash Lemma 7 applied to $D$ (with $\ell(D) = 7 < 2\delta =
8$): there is an induced subgraph $S \subseteq V(D)$ with $|S| \leq 4$
and $\delta^+(S) \geq 2\delta - \ell(D) = 1$. The proof's specific
construction yields $S = B^- = \mathrm{pred}_C(N^+(v_{a-1}) \cap V(C))$.

The geometric count $|V(C)| \geq |S| + \delta - \delta^+(S)$ combined
with the oriented average bound $\delta^+(S) \leq \lfloor (|S|-1)/2
\rfloor$ forces $|S| = 4$ (see Lemma 2 below) and $|V(C)| \geq 7$,
hence $a = 1$ and $V(C) = \{v_1, \ldots, v_7\}$. The path arc
$v_0 \to v_1$ gives $v_1 \in B = N^+(v_0)$, so
$v_7 = \mathrm{pred}_C(v_1) \in S$.

## Lemma 1 ($\ell = 6$ impossible)

If $\ell(D) = 6$, Lemma 7 gives an induced $S$ with $|S| \leq 4$ and
$\delta^+(S) \geq 2$. But the oriented average bound forces
$\delta^+(S) \leq \lfloor 3/2 \rfloor = 1$ on $|S| \leq 4$.
Contradiction. Hence $\ell(D) = 7$ in any surviving case.

## Lemma 2 ($|S| = 3$ impossible)

If $|S| = 3$, then $|B| = 3$ (since $|B^-| = |B|$), so
$|A| = \delta - |B| = 1$. With $A \subseteq \{v_0, \ldots, v_{a-1}\}$
and self-loops forbidden, $|A| \leq a - 1$, forcing $a \geq 2$. At
$a = 2$, $A \subseteq \{v_0, v_1\} \setminus \{v_1\} = \{v_0\}$, so
$A = \{v_0\}$, requiring $v_1 \to v_0$. But the path arc $v_0 \to v_1$
makes this antiparallel — forbidden. The geometric bound
$|V(C)| \geq |S| + \delta - \delta^+(S) = 3 + 4 - 1 = 6$ with
$|V(C)| = 8 - a$ forces $a \leq 2$. Contradiction.

So $|S| = 4$.

## Score-sequence case split

The score sequence of $S$ (as an oriented graph on 4 vertices with
$\delta^+(S) \geq 1$) is one of $(1,1,1,1)$, $(2,1,1,1)$, $(2,2,1,1)$,
$(3,1,1,1)$.

### Case $(1,1,1,1)$ — direct cyclic closure

If every $s \in S$ has $d^+_S(s) = 1$, then by Claim 12 + 4-outregular,
each $s$ sends $\delta - 1 = 3$ arcs to $V(C) \setminus S$, which has
$|V(C)| - |S| = 3$ vertices. So every $s \in S$ sends arcs to *every*
$V(C)\setminus S$-vertex.

For each path arc $v_i \to v_{i+1}$ ($i \in \{1, \ldots, 6\}$) and the
cycle arc $v_7 \to v_1$, the antiparallel constraint forces $S$ to be
closed under the cyclic predecessor permutation $\sigma$ on $V(C)$ (a
single 7-cycle; details mirror the $k=3$ proof, Step 7). The only
$\sigma$-invariant subsets of $V(C)$ are $\emptyset$ and $V(C)$. With
$|S| = 4$ and $v_7 \in S$ ($S$ non-empty): $S = V(C)$, $|S| = 7$.
Contradiction with $|S| = 4$.

### Case $(2,1,1,1)$ — hand proof

The cyclic-interval mini-lemma (Lemma 3 below) forces $S$ to be 4
consecutive vertices in $C$ with the unique outdegree-2 vertex $u$ at
the interval start. Four cases by which interval contains $v_7$:

- Case (I): $S = \{v_4, v_5, v_6, v_7\}$, $u = v_4$.
- Case (II): $S = \{v_5, v_6, v_7, v_1\}$, $u = v_5$.
- Case (III): $S = \{v_6, v_7, v_1, v_2\}$, $u = v_6$.
- Case (IV): $S = \{v_7, v_1, v_2, v_3\}$, $u = v_7$.

Each case admits an explicit length-8 directed simple path, derived in
the F-step structure (forced T-arcs, forced $u$-arcs, forced $v_0$-arcs,
forced $V(C)\setminus S$-arcs from allowed-target counts at $n = 10$).
See `k4_partial_appendix.md` for the per-case derivations and
arc-by-arc justifications. $\square$

### Case $(3,1,1,1)$ — hand proof

The same cyclic-interval structure applies (Lemma 3 only uses
T-vertices' predecessor closure, which is unchanged when the dominant
vertex has $d^+_S = 3$ instead of 2). Four cases, each with explicit
length-8 path. See `k4_partial_appendix.md`. $\square$

### Case $(2,2,1,1)$ — computer-aided

See Lemma 4 below.

## Lemma 3 (cyclic-interval mini-lemma for score $(2,1,1,1)$ and $(3,1,1,1)$)

In score sequence $(2,1,1,1)$ or $(3,1,1,1)$, $S$ is a cyclic interval
of 4 consecutive vertices in $C$, with the unique outdegree-$\geq 2$
vertex $u$ at the interval start (in $C$-order).

**Proof.** Let $T = \{s \in S : d^+_S(s) = 1\}$. In score $(2,1,1,1)$,
$|T| = 3$; in score $(3,1,1,1)$, $|T| = 3$ also. For each $t \in T$,
Claim 12 + 4-outregular + $d^+_S(t) = 1$ give
$d^+_{V(C)\setminus S}(t) = 3 = |V(C)\setminus S|$, so $t$ sends an
arc to every $V(C)\setminus S$-vertex.

Antiparallel kill (path arcs $v_i \to v_{i+1}$ for $i \in \{1, \ldots,
6\}$ and cycle arc $v_7 \to v_1$): if $v_{i+1} \in T$ and
$v_i \in V(C)\setminus S$, then the forced arc $t = v_{i+1} \to v_i$
contradicts the existing arc $v_i \to v_{i+1}$. So $v_{i+1} \in T
\Rightarrow v_i \in S$ for path arcs, and $v_1 \in T \Rightarrow
v_7 \in S$ for the cycle arc. Equivalently, $\sigma(T) \subseteq S$.

Since $|T| = 3$ and $|S| = 4$, $\sigma(T)$ is a $3$-element subset of
$S$. The 7-cycle $\sigma$ on $V(C)$ has only $\emptyset$ and $V(C)$ as
invariant subsets, so $\sigma(T) \neq T$. Hence $\sigma(T) = (T
\setminus \{t_0\}) \cup \{u\}$ for unique $t_0 \in T$ and $u \in S
\setminus T$.

The remaining elements $t_1, t_2 \in T \setminus \{t_0\}$ satisfy
$\sigma(t_i) \in T$ (by the argument above). $\sigma$ injective
forbids $\sigma(t_1) = \sigma(t_2)$; $\sigma$ has no fixed points or
2-cycles. By elimination, $\sigma(t_2) = t_1$ and $\sigma(t_1) = t_0$.

Reading in the $\sigma^{-1}$ direction, $u, t_0, t_1, t_2$ are
consecutive in $C$-order. $\square$

## Lemma 4 (the computer-aided $(2,2,1,1)$ closure)

> **Lemma.** For every valid $(S, T)$ configuration with score
> sequence $(2,2,1,1)$ at $n = 10$ — i.e., $|S| = 4$, $|T| = 2$,
> $v_7 \in S$, and $\sigma(T) \subseteq S$ — every $4$-outregular
> oriented completion of $D$ satisfying the local Cheng--Keevash
> constraints contains a directed simple path of length $8$.

**Proof (computer-aided).** Brute-force enumeration over all
$\binom{6}{3} \cdot \binom{4}{2} = 120$ raw $(S, T)$ pairs with $v_7
\in S$, $|S| = 4$, $|T| = 2$ identifies exactly $24$ valid
configurations with $\sigma(T) \subseteq S$. These split into three
shapes:

- **Shape A1** (4-cyclic-interval): 12 configurations.
- **Shape A2** (3-block + isolated $u'$): 8 configurations.
- **Shape B** (2 separated pairs): 4 configurations.

For each $(S, T)$, the local proof miner
(`scripts/k4_local_miner.py`) derives all forced and forbidden arcs
from the rules R-path, R-cycle, R-T, R-F3, R-Claim12, R-LemmaA-rev,
R-loop, R-AP, R-out, R-score, R-VCS, plus the iterative propagation
rules P1, P2, P3 (see "Soundness of forcing rules" section in
`k4_partial_appendix.md`). The miner then enumerates every
$4$-outregular oriented completion consistent with these constraints
and checks each completion for a directed simple path of length 8 via
DFS.

The miner reports $0$ obstructions across all $24$ configurations:
every enumerated completion has a length-8 path. The audit
(`scripts/k4_audit.py`) re-enumerates and validates each completion's
forced arcs, antiparallel constraint, $4$-outregularity, score
sequence, Claim 12, and length-8 path. Across all $24$ configurations,
the audit reports $24/24$ pass and $0$ failures, validating $\sim$3,664
total completions (Shape A1: 3,448; Shape A2: 144; Shape B: 72). The
path table (`data/k4_path_table.md`) records a representative
length-8 path per $(S, T)$.

This completes the proof of Lemma 4. $\square$

## Conclusion of theorem

By Lemmas 1, 2, 3, and 4, all score-sequence cases at $n = 10$ lead to
contradiction. Hence no $4$-outregular oriented graph on 10 vertices
has $\ell(D) \leq 7$. By the R1/R2/R3 reductions, no oriented graph
$D_0$ with $\delta^+(D_0) \geq 4$ and $|V(D_0)| = 10$ has $\ell(D_0)
\leq 7$. $\blacksquare$

## Reproduction

System: macOS Darwin 25.4.0, Python 3.12.4 (via `uv run python`).

### Primary pipeline

```bash
uv run python scripts/k4_local_miner.py
uv run python scripts/k4_audit.py
uv run python scripts/k4_path_table.py > data/k4_path_table.md
```

### Independent re-derivation (no shared code with miner)

```bash
uv run python scripts/k4_independent_check.py
```

This script re-implements the (S, T) enumeration, forced-arc derivation,
completion enumeration, and length-8 path search with no imports from
`k4_local_miner.py`. It agrees with the miner: 24/24 closed,
3664 total completions, 0 obstructions.

### Certificate generation and verification

```bash
uv run python scripts/k4_generate_certificate.py
uv run python scripts/k4_verify_certificate.py
```

This produces `data/k4_n10_certificate.json` (the machine-readable
certificate) and verifies it without re-running the enumeration. The
certificate stores each completion's full arc set, SHA-256 hash, and
witness length-8 path. The verifier mechanically checks for every
one of the 3,664 completions:
- (S, T) coverage matches the brute-force enumeration of 24 valid
  configurations.
- SHA-256 hash recomputation matches the certificate's stored hash.
- 4-outregularity (every vertex has out-degree exactly 4).
- Oriented (no loops, no antiparallel pair).
- All forced arcs are present in the completion's arc set.
- Claim 12 (S-vertex out-arcs lie in V(C)).
- Lemma A reverse (no in-arc to v_0 from x or y).
- Score sequence ($d^+_S(t) = 1$ for $t \in T$, $d^+_S(u) = 2$ for
  $u \in S \setminus T$).
- Witness path is contained in the completion (every consecutive arc
  exists), is simple (vertices distinct), and has length $\geq 8$.

### Output SHA-256 hashes (recorded 2026-05-09)

- `k4_local_miner.py` stdout: `334cfe4f8e94f30fffb255df39e9dfd4de8066bf579ca239891130380a6b523b`
- `k4_audit.py` stdout: `ae846aaaba0b53ea95c80434e9effc7f35dde757104793740126ac88389ebe6f`
- `k4_path_table.py` stdout: `310a9472d0a4b413cd7dbb7f98c795258b464a24316be53d627a15c428813ea9`
- `k4_independent_check.py` stdout: `a40e53c51acbb2760753106f0e64d3aee9bf3185bd97126b8776eb64bb84964f`
- `k4_generate_certificate.py` stdout: `174fb8783bb93d0b8cabbc9f75faa934c17a9b63e1ee3942e5f5f3bcbb880dac`
- `k4_verify_certificate.py` stdout: `84515d83a7f5c2f9d2d9fb58412433d3d49bfd3dca6634dfdffb8ddfbf99c913`

Expected outputs:
- Miner: 24 configurations, 0 obstructions each.
- Audit: 24 passed, 0 failed, 3664 total completions.
- Independent check: 24/24 closed, agrees with miner.
- Certificate: 3664 completions mechanically verified (hash, 4-outreg,
  oriented, forced arcs, Claim 12, Lemma A reverse, score sequence,
  witness path containment + simplicity + length).

## Audit and trust boundary

Two independent computer-aided pipelines agree:

1. **Miner + audit** (`scripts/k4_local_miner.py`,
   `scripts/k4_audit.py`): the audit shares the forcing engine with
   the miner, so it verifies post-conditions (forced arcs present,
   score sequence, Claim 12, length-8 path) under the same forced/
   forbidden model.
2. **Independent check** (`scripts/k4_independent_check.py`): a
   from-scratch re-implementation of (S, T) enumeration, forced-arc
   derivation, completion enumeration, and length-8 path search, with
   no imports from `k4_local_miner.py`. It agrees with the miner on
   every (S, T): 24/24 closed, 3664 completions, 0 obstructions, and
   the per-(S, T) completion counts match exactly (e.g., A1 with
   $T = \{b,c\}$ gives 176, with $T \in \{\{b,d\}, \{c,d\}\}$ gives
   343, A2/B give 18).

Two pipelines reaching the same conclusion via independently
implemented logic substantially reduces the risk of a shared bug in
the forcing rules.

The trust boundary for the computer-aided portion is:

1. The forcing rules R-path, R-cycle, R-T, R-F3, R-Claim12,
   R-LemmaA-rev, R-loop, R-AP, R-out, R-score, R-VCS, and the
   iterative propagation P1, P2 are sound (each "forced" arc is a
   logical consequence of the assumed configuration; each "forbidden"
   arc is incompatible with it). Per-rule justifications are in
   `k4_partial_appendix.md` and re-implemented declaratively in
   `scripts/k4_independent_check.py`.
2. The length-8 path search is a standard DFS with visited-set
   tracking; correct by construction. Both pipelines implement it.
3. The configuration enumeration is verified complete by brute force
   over $\binom{6}{3} \cdot \binom{4}{2} = 120$ raw $(S, T)$ pairs in
   both pipelines.
4. The certificate (`data/k4_n10_certificate.json`) records each
   completion's full arc set, SHA-256 hash, and witness length-8 path.
   `scripts/k4_verify_certificate.py` independently checks, for every
   one of the 3,664 completions: SHA-256 hash recomputation,
   4-outregularity, no loops, no antiparallel pair, presence of every
   forced arc, Claim 12 (S-vertex out-arcs in V(C)), Lemma A reverse
   (no in-arc to v_0 from x or y), score sequence
   ($d^+_S(t) = 1$ for $t \in T$, $d^+_S(u) = 2$ for $u \in S \setminus
   T$), witness path containment, simplicity, and length $\geq 8$.

Items 1, 2, 3 require mathematical trust (the rules are sound);
item 4 is mechanically checkable end-to-end.

## Cross-references

Documentation:

- Hand-proof details for $(2,1,1,1)$ and $(3,1,1,1)$ Cases (I)--(IV),
  per-score F-step derivations, and the soundness rules:
  `k4_partial_appendix.md`.
- Cheng--Keevash 2024 verbatim statements:
  `literature_notes.md`.
- Project-wide plan and status:
  `plan.md`.
- The $\delta = 3$ closure (all $n \geq 7$):
  `k3_hand_proof.md`.

Scripts:

- `scripts/k4_local_miner.py`: primary proof miner.
- `scripts/k4_audit.py`: validation of miner completions (shares code).
- `scripts/k4_path_table.py`: per-(S, T) path table generator.
- `scripts/k4_independent_check.py`: independent re-derivation
  (no shared code with miner).
- `scripts/k4_generate_certificate.py`: machine-readable certificate
  builder.
- `scripts/k4_verify_certificate.py`: certificate verifier.
- `scripts/verify_directed_path_counterexample.py`: standalone
  verifier for arbitrary candidate counterexamples (oriented,
  min-out-degree, strong-connectivity, longest-path checks).

Data:

- `data/k4_n10_certificate.json`: machine-readable proof certificate.
- `data/k4_path_table.md`: per-(S, T) representative length-8 path.
- `data/k4_audit_output.txt`: audit log.
