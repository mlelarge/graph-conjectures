# Path-FAS and Matching-FAS in Tournaments

Attack on **Problem 4.4 of Aboulker–Aubian–Lopes**
([arXiv:2402.10782](https://arxiv.org/abs/2402.10782), *Finding forest-orderings of
tournaments is NP-complete*, 2024).

## The problem

Given an undirected graph class $\mathcal{C}$, a **$\mathcal{C}$-FAS** of a
tournament $T$ is a feedback arc set $F \subseteq E(T)$ whose underlying
undirected graph (forgetting arc orientations) lies in $\mathcal{C}$. The
$\mathcal{C}$-FAS Problem decides whether such an $F$ exists.

The source paper proves (Theorem 1.1) that the $\mathcal{C}$-FAS Problem is
**NP-complete when $\mathcal{C}$ is the class of all forests**. Problem 4.4
asks for the complexity in two natural subclasses:

- **(M)** $\mathcal{C}$ = all graphs of maximum degree $\le 1$ (matchings);
- **(P)** $\mathcal{C}$ = all paths.

## Status

**Matching-FAS half of Problem 4.4: internally proved polynomial; prior-art
check still needed before claiming novelty.**

[`docs/lemmas.md`](docs/lemmas.md) proves:

> **Theorem.** The matching-FAS decision problem for tournaments is in
> $\mathsf{P}$; specifically, it reduces to 2-SAT after picking one arc
> per *cyclic 3-cycle module*. Total time $O(n^3)$.

The argument has five pieces (see [`docs/lemmas.md`](docs/lemmas.md) for proofs):

- **Theorem 1 (characterization).** $T$ has a matching-FAS iff there
  exists a matching $M \subseteq A(T)$ whose every arc is *no-shortcut*
  (no $w$ with $u \to w \to v$) and every cyclic 3-cycle of $T$
  contains exactly one $M$-arc.
- **Lemma 2.** A cyclic 3-cycle has all three arcs no-shortcut iff it
  is a *module* of $T$.
- **Lemma 3.** Two distinct cyclic-3-cycle modules are vertex-disjoint.
- **Lemma 4.** No arc of a cyclic-3-cycle module belongs to any other
  cyclic 3-cycle.
- **Lemma 5.** No no-shortcut arc has exactly one endpoint in a
  cyclic-3-cycle module.

By Lemmas 3-5 the modules are completely decoupled (pick any one arc per
module; no interaction with the rest). The remaining cyclic 3-cycles
have $\le 2$ no-shortcut arcs each, so the residual exists/matching
problem encodes as 2-SAT.

The cyclic-module objects themselves are standard tournament modules.
This folder claims only a self-contained internal proof of the polynomial
decision algorithm. Before presenting it as a new result, the specific
2-SAT reduction should be checked against the tournament modular
decomposition and feedback-arc-set literature, including the sources
cited by Aboulker-Aubian-Lopes.

The algorithm is implemented in [`scripts/poly_mfas.py`](scripts/poly_mfas.py).
It is cross-checked against brute force on:

- **All 74 non-isomorphic tournaments at $n \in \{3,4,5,6\}$** (exhaustive).
- **150 random tournaments at $n \in \{7, 8\}$** — every YES answer
  also passes the deeper certificate check (returned $M$ is a matching
  and $T \oplus M$ is transitive).

Zero disagreements: see [`tests/test_poly.py`](tests/test_poly.py).

**Path-FAS half of Problem 4.4: open.**

The path case is *not* settled by these lemmas. The analogous
necessary-condition argument (which arcs may appear in $M$ for a
back-arc set to be a path?) involves max-degree 2 instead of 1, which
breaks the "at most one $M$-arc per triangle" property and admits the
"V"-shape configurations. In those configurations, two selected arcs
may lie in the same triangle, so the long-arc/no-shortcut obstruction
used for matchings no longer gives a direct 2-SAT formulation. The
structural characterization for path-FAS is left as a follow-up.

## Files

- [`docs/attack_plan.md`](docs/attack_plan.md) — original phased plan.
- [`docs/lemmas.md`](docs/lemmas.md) — Theorem 1 + Lemmas 2-5 +
  Theorem 2 (polynomial-time algorithm), with full proofs.
- [`scripts/verify.py`](scripts/verify.py) — trust-root verifier:
  classifies back-arcs of $T$ under any ordering.
- [`scripts/brute.py`](scripts/brute.py) — brute-force decider over
  all $n!$ orderings.
- [`scripts/sweep.py`](scripts/sweep.py) — full sweep over
  non-isomorphic tournaments for $n \le 6$.
- [`scripts/structural.py`](scripts/structural.py) — cyclic 3-cycle
  enumeration, no-shortcut arcs, and the original (back-tracking)
  structural decider used during exploration.
- [`scripts/poly_mfas.py`](scripts/poly_mfas.py) — the polynomial-time
  decider: reduction to 2-SAT, with built-in cross-check harness.
- [`scripts/cross_check.py`](scripts/cross_check.py) — exhaustive
  agreement check (structural vs brute) for $n \le 6$.
- [`scripts/random_check.py`](scripts/random_check.py) — random
  sampling for $n \ge 7$.
- [`tests/test_verify.py`](tests/test_verify.py) — pinning the
  verifier against hand-checked small cases.
- [`tests/test_poly.py`](tests/test_poly.py) — *the* validation
  harness: every YES from `poly_mfas` is verified end-to-end against
  a transitive-tournament certificate.
- [`data/sweep_results.json`](data/sweep_results.json) — sweep output
  for $n \in [3, 6]$.

## Reproducing the results

```bash
cd problems/path_matching_fas
python3 -m unittest tests/test_verify.py            # ~0.0s
python3 -m unittest tests/test_poly.py              # ~1 minute (n<=6 + 150 random)
python3 scripts/sweep.py --nmax 6                   # ~30s
python3 scripts/poly_mfas.py --nmax 6               # also ~30s — agreement check
python3 scripts/random_check.py --n 7 --samples 200 # ~10s
```

No external dependencies beyond the Python standard library.

## What this attack does NOT claim

- We do not attempt the **path-FAS** case; see "Status" above.
- We do not address the closely related **Problem 4.1** (triangle-free
  FAS) from the same paper.
- We do not improve the source paper's NP-hardness for the forest
  case (Theorem 1.1 of arXiv:2402.10782 stands).
- This folder does not claim that the matching-FAS algorithm is new.
  The proof is self-contained, but the novelty claim needs a prior-art
  check against tournament modular decomposition and FAS-variant
  literature.
