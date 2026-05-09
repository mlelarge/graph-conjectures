# Conjecture 1 for $\delta = 4$ at $n = 11$

## Theorem

> Every oriented graph $D$ with $\delta^+(D) \geq 4$ and $|V(D)| = 11$
> contains a directed simple path of length $8$.

This extends the $\delta = 4, n = 10$ closure
(`k4_n10_proof.md`) to the next case. The proof is
computer-aided across the four score-sequence cases.

## History (audit trail)

An earlier version of this file claimed the closure was achieved by
running `scripts/k4_general_miner.py 11` and
`scripts/k4_n11_full_run.py`. **That claim was incomplete.** The
original `k4_general_miner.py` hard-coded the score profile
`target_S = 1 if v in T else 2`, which is exactly $(2,2,1,1)$, and
its $(S, T)$ enumeration only generated $T$ with $|T| = 2$. So the
91M-completion run covered $(2,2,1,1)$ only.

The fix: a score-profile-aware miner
(`scripts/k4_score_profile_miner.py`) now enumerates configurations
for each of the four score sequences and runs the same forced-arc
derivation + completion enumeration + length-8 path search per
$(S, T)$ at any $n \geq 10$.

A second pipeline,
`scripts/k4_score_profile_independent_check.py`, was added with no
imports from `k4_score_profile_miner.py` to provide an independent
re-derivation. The two pipelines agree on every per-$(S, T)$
forced-arc count, completion count, and final closure status.

The current file reflects the fixed run, with two-pipeline agreement:
32 configurations across all four score sequences, 117,992,940 total
completions per pipeline, 0 obstructions.

## Reduction

Suppose $D_0$ is a counterexample at $\delta = 4$, $|V(D_0)| = 11$:
$\delta^+(D_0) \geq 4$, $\ell(D_0) \leq 7$. Apply R1/R2/R3 from the
$n = 10$ proof: a sink SCC $D$ of $D_0$, $4$-outregular, oriented,
strongly connected, $\ell(D) \leq 7$. The oriented average bound and
$|V(D_0)| = 11$ give $|V(D)| \in \{9, 10, 11\}$.

- $|V(D)| = 9$: regular tournament, Hamilton path of length 8;
  contradicts $\ell(D) \leq 7$.
- $|V(D)| = 10$: closed by `k4_n10_proof.md`; no such
  $D$ exists.
- $|V(D)| = 11$: this file's case.

## Setup at $n = 11$

Set $|V(D)| = 11$. Then $|A(D)| = 4 \cdot 11 = 44$ and
$\binom{11}{2} = 55$, so $D$ has exactly $11$ non-edges.

By Cheng--Keevash Theorem 4 applied to $D$, $\ell(D) \geq 6$. By the
oriented-bound argument from the $n = 10$ proof (Lemma 1 there:
$\delta^+(S) \leq 1$ on $|S| \leq 4$ rules out $\ell = 6$),
$\ell(D) = 7$.

Take a longest directed simple path $P = v_0 v_1 \cdots v_7$ in $D$,
chosen so the cycle bound is maximal. Set $V(P) = \{v_0, \ldots,
v_7\}$ and $V(D) \setminus V(P) = \{x, y, z\}$ (three off-path
vertices, vs two at $n = 10$).

By Cheng--Keevash Lemma 7 (proof internals): $|S| = 4$, $a = 1$,
$V(C) = \{v_1, \ldots, v_7\}$, $\delta^+(S) = 1$, $v_7 \in S$,
$|V(C) \setminus S| = 3$.

Lemma 2 ($|S| = 3$ impossible) carries over from the $n = 10$ proof
unchanged (only depends on $|V(C)|$ and oriented constraints).

## Score-sequence case split

The score sequence of $S$ as an oriented graph on 4 vertices with
$\delta^+(S) \geq 1$ is one of $(1,1,1,1)$, $(2,1,1,1)$, $(2,2,1,1)$,
$(3,1,1,1)$. Each is handled below.

### Case $(1,1,1,1)$: structurally impossible

If every $s \in S$ has $d^+_S(s) = 1$, then every $s$ is a T-vertex
(in the sense $T = \{s : d^+_S(s) = 1\}$), so $T = S$. The
$\sigma$-image constraint forces $\sigma(T) \subseteq S$, i.e.,
$\sigma(S) \subseteq S$. Since $|\sigma(S)| = |S| = 4$ and
$\sigma(S) \subseteq V(C)$, we have $\sigma(S) = S$, i.e., $S$ is
$\sigma$-invariant. The cyclic permutation $\sigma$ on the 7-cycle
$V(C)$ has only $\emptyset$ and $V(C)$ as invariant subsets. With
$|S| = 4$, contradiction.

Equivalently: the score-profile-aware miner
(`scripts/k4_score_profile_miner.py`) reports **0 valid $(S, T)$
configurations** for the $(1,1,1,1)$ profile at any $n$.

### Cases $(2,1,1,1)$, $(2,2,1,1)$, $(3,1,1,1)$: computer-aided

For each of these three score sequences, the score-profile-aware
miner enumerates every valid $(S, T)$ configuration and verifies
that every $4$-outregular oriented completion contains a directed
simple path of length 8.

## Lemma (computer-aided $n = 11$ closure)

> For every valid $(S, T)$ configuration at $n = 11$ with score
> sequence $(2,1,1,1)$, $(2,2,1,1)$, or $(3,1,1,1)$, every
> 4-outregular oriented completion satisfying the local
> Cheng--Keevash constraints contains a directed simple path of
> length 8.

**Proof (computer-aided).** Run

```bash
uv run python scripts/k4_score_profile_miner.py 11
```

The miner derives forced arcs from the rule list (R-path, R-cycle,
R-T, R-F3, R-Claim12, R-LemmaA-rev, R-loop, R-AP, R-out, R-score,
R-VCS, P1, P2) parameterised by an arbitrary score profile,
enumerates every 4-outregular oriented completion, and verifies a
length-8 path in each via DFS.

Result across all four score sequences:

| Score sequence | Configs | Completions per case (range) | Total completions |
|---|---:|---:|---:|
| $(1,1,1,1)$ | 0 | — | 0 |
| $(2,1,1,1)$ | 4 | 1,602,603 | 6,410,412 |
| $(2,2,1,1)$ | 24 | 1,620,762–6,945,136 | 91,574,016 |
| $(3,1,1,1)$ | 4 | 5,002,128 | 20,008,512 |
| **Total** | **32** | | **117,992,940** |

**0 obstructions across all 32 configurations.** Wall-clock: ~21
minutes on M-class Mac, single core. $\square$

## Conclusion

By Lemma 2 (impossibility of $|S| = 3$, carried over from the
$n = 10$ proof), Cheng--Keevash Lemma 7 forces $|S| = 4$ at
$n = 11$. By the score-sequence case split: the $(1,1,1,1)$ case is
structurally impossible (no valid $(S, T)$); the other three cases
admit no obstructions per the computer-aided lemma above. Hence no
$4$-outregular oriented graph on 11 vertices has $\ell(D) \leq 7$,
and by the R1/R2/R3 reductions, no oriented graph with
$\delta^+ \geq 4$ and $|V| = 11$ has $\ell \leq 7$. $\blacksquare$

## Reproduction

System: macOS Darwin 25.4.0, Python 3.12.4 (via `uv run python`).

```bash
uv run python scripts/k4_score_profile_miner.py 11
```

The script enumerates all valid $(S, \text{score profile})$
configurations for each of the four score sequences, derives forced
arcs, enumerates completions, and verifies length-8 paths. Expected
output: 32 configurations, 117,992,940 total completions, 0
obstructions.

A sanity-check run at $n = 10$ produces the same 32 configurations
(0 + 4 + 24 + 4) and ~4,792 total completions, all closed.
The hand proofs in `k4_n10_proof.md` cover the
$(2,1,1,1)$ and $(3,1,1,1)$ cases at $n = 10$ as an alternative.

Output SHA-256 hashes (recorded 2026-05-09):

- `k4_score_profile_miner.py 11` stdout:
  `2e6bd6b564f688d021d201f8b90658a6f543f9f412e3843c0ddee5570254779f`
- `k4_score_profile_independent_check.py 11` stdout:
  `70c9d406d9d7ecc8b7573bff876cda28e984e77d6be3d149c137e056b51a44b4`

Expected output: 32 configurations across 4 score sequences,
117,992,940 total completions, 0 obstructions, ~21 minutes
wall-clock per pipeline on M-class Mac single core.

Independent re-derivation (`k4_score_profile_independent_check.py`)
agrees with the miner on every per-$(S, T)$ forced-arc count, every
per-$(S, T)$ completion count, every per-profile total, and reports
the same 0 obstructions across all 32 configurations.

## Why no per-completion certificate at $n = 11$

At $n = 10$ the per-completion certificate
(`data/k4_n10_certificate.json`, ~10 MB) stores every completion's
full arc set, hash, and witness length-8 path. At $n = 11$ with
~118M completions, the analogous certificate would be tens to
hundreds of GB — impractical for a research artifact. Verification
is reproducible by re-running the miner instead.

If a per-completion certificate is needed, a sampled or hash-only
variant could be generated. This is a deliberate design choice for
$n = 11$ and beyond: trust the miner's output, with stdout SHA-256
as reproducibility evidence and the two-pipeline agreement (see the
trust boundary section below) as the substantive correctness check.

## Audit and trust boundary

Two independent computer-aided pipelines agree at $n = 11$:

1. **Score-profile miner** (`scripts/k4_score_profile_miner.py`):
   parameterised by an arbitrary score profile, enumerates the
   $(S, T)$ configurations and completions per the rule list.
2. **Independent checker** (`scripts/k4_score_profile_independent_check.py`):
   from-scratch re-implementation with no imports from
   `k4_score_profile_miner.py`. It re-derives configuration
   enumeration, forced-arc rules, completion enumeration, and
   length-8 path search.

Both agree exactly on every configuration: same per-$(S, T)$ forced
arc counts (e.g., 19, 21, 22 for $(2,2,1,1)$), same completion counts
(1,602,603 for $(2,1,1,1)$ each; 1,620,762 / 4,140,946 / 6,945,136
for $(2,2,1,1)$; 5,002,128 for $(3,1,1,1)$ each), same total
117,992,940, and zero obstructions across all 32 configurations.

The trust boundary for the computer-aided portion is:

1. **Soundness of the forcing rules** (R-loop, R-path, R-cycle, R-T,
   R-F3, R-Claim12, R-LemmaA-rev, R-AP, R-out, R-score, R-VCS, plus
   iterative propagation P1, P2). Per-rule justifications in
   `k4_partial_appendix.md`. Both pipelines implement the rules
   independently from the same logical specification.
2. **Completeness of $(S, T)$ enumeration** for each score profile:
   brute force over all $\binom{6}{3} \cdot \binom{4}{|T|}$ raw
   $(S, T)$ pairs with $v_7 \in S$ and $\sigma(T) \subseteq S$. Both
   pipelines compute the enumeration; the independent checker also
   prints per-profile expected counts (0, 4, 24, 4) for cross-check.
3. **Length-8 path search soundness**: DFS with visited-set tracking,
   correct by construction. Both pipelines implement it.
4. **Computational integrity**: 117,992,940 completions enumerated
   in each pipeline, 0 obstructions. Stdout SHA-256 hashes
   recorded in the Reproduction section.

Items 1, 2, 3 are mathematical trust; item 4 is reproduction
evidence. The two-pipeline agreement substantially reduces the risk
of a shared bug in the forcing rules — the same closure conclusion
is reached via independently coded logic.

## Cross-references

Documentation:
- $\delta = 4, n = 10$ closure: `k4_n10_proof.md`.
- Per-case F-step derivations and soundness rules:
  `k4_partial_appendix.md`.
- Cheng--Keevash 2024 verbatim statements:
  `literature_notes.md`.
- Project plan: `plan.md`.
- $\delta = 3$ closure (all $n \geq 7$):
  `k3_hand_proof.md`.

Scripts:
- `scripts/k4_score_profile_miner.py`: parameterised miner accepting
  arbitrary $n$ and arbitrary score profile. **This is the
  authoritative tool for $n \geq 11$.**
- `scripts/k4_score_profile_independent_check.py`: independent
  re-implementation. No imports from `k4_score_profile_miner.py`.
  Re-derives configurations, forcing rules, completion enumeration,
  and length-8 search. **Agrees with the miner at $n = 10$ and
  $n = 11$ on every per-$(S, T)$ count and total.**
- `scripts/k4_general_miner.py`: earlier miner that hard-coded
  $(2,2,1,1)$. **Do not use as the sole closure tool**; superseded
  by `k4_score_profile_miner.py`.
- `scripts/k4_n11_overflow_cases.py`,
  `scripts/k4_n11_full_run.py`: short-circuit / cap-bumped runs of
  `k4_general_miner.py` for the $(2,2,1,1)$ case only. Useful for
  verifying the $(2,2,1,1)$ portion of $n = 11$ but **does not cover
  $(2,1,1,1)$ or $(3,1,1,1)$**.
