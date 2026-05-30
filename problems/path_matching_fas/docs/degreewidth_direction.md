# A new direction: the degreewidth decomposition of Path-FAS (D92)

After the four blocked/paused routes (forward-DP / D70, fanout / D90,
cutting-plane / D91, exact ILP), this opens a **global structural
invariant** for tournament Path-FAS that the project had not used, and
that connects the problem to existing literature.

## The invariant

> **Δ\*(T) = degreewidth(T)** = min over vertex orderings of the maximum
> **back-degree** (number of back-arcs incident to a vertex).

This is exactly the parameter **degreewidth** of
[Bessy et al., "Degreewidth: a New Parameter for Solving Problems on
Tournaments", arXiv:2212.06007](https://arxiv.org/abs/2212.06007)
(degreewidth 0 ⟺ acyclic; degreewidth 1 = *sparse* tournaments).

## The theorem and the decomposition

> **Theorem (immediate).**  Path-FAS(T) = YES ⟹ Δ\*(T) ≤ 2.
> *Proof.*  A YES order has a linear-forest back-arc graph, whose max
> undirected degree is ≤ 2, so that very order attains max-back-degree
> ≤ 2. ∎  Contrapositive: **Δ\*(T) ≥ 3 ⟹ NO** — a global NO-certificate
> independent of acyclicity.

Combining with the degreewidth literature gives a clean **four-layer
split of all tournaments**:

| layer | back-arc graph (at an optimal order) | Path-FAS | recognition |
|---|---|---|---|
| Δ\* = 0 | empty (acyclic) | **YES** | trivial |
| Δ\* = 1 (*sparse*) | a **matching** (⊆ linear forest) | **YES** | **poly** — cubic (arXiv:2212.06007) |
| Δ\* = 2 | paths **+ cycles** | **YES iff some degree-2 order is acyclic** | the open core |
| Δ\* ≥ 3 | — | **NO** | (recognition open; see Q1) |

So **Path-FAS YES = (Δ\* ≤ 1)  ∨  (Δ\* = 2 ∧ some degree-2 order is
acyclic)**, and the *entire* difficulty of the problem lives in the
**Δ\* = 2 layer**: Δ\* ≤ 1 is YES and poly-recognizable, Δ\* ≥ 3 is NO.

## The acyclicity-core (verified on the catalogues)

Minimal-NO instances all have Δ\* ∈ {2, 3} (no NO has Δ\* ≤ 1, since
Δ\* ≤ 1 ⟹ YES).  They split:

| n | minimal NOs | Δ\* ≥ 3 (degree-obstructed) | Δ\* = 2 (**acyclicity-core**) |
|---|---|---|---|
| 7 | 20 (all) | 11 (55 %) | 9 (45 %) |
| 8 | 300 (sample) | 211 (70 %) | 89 (29 %) |
| 9 | 150 (sample) | 78 (52 %) | 72 (48 %) |

Two clean facts:
  * the **`hall_failure`** obstruction is **entirely degree-obstructed**
    (Δ\* ≥ 3) — Hall failures are degree obstructions;
  * the **acyclicity-core (Δ\* = 2 NOs) is entirely `large_width_no`** —
    a degree-2 order exists, but every one has a cyclic back-arc graph
    (forced cycle lengths 3–7 at n = 7).  This is a *new, more
    principled* split than the project's `hall_failure` / `large_width_no`
    taxonomy: the core is a strict 29–48 % residual.

(n = 6 full census, all 32768 tournaments: every YES has Δ\* ≤ 2, none
≥ 3; 15648 YES already have Δ\* = 2, so the Δ\* = 2 layer carries both
YES and NO — exactly where acyclicity decides.)

## The two sharp open sub-questions

> **(Q1) Is "Δ\*(T) ≤ 2" decidable in polynomial time?**  (Recognition of
> degreewidth ≤ 2.)  Computing Δ\* exactly is **NP-hard** in general
> (arXiv:2212.06007), but *sparse* recognition (Δ\* ≤ 1) is cubic; the
> fixed value k = 2 is the open gateway.  A poly answer gives a poly
> NO-certificate for the degree-obstructed majority; an NP-hardness answer
> would be a **non-local hardness** lead for Path-FAS itself (note: the
> degreewidth-NP-hardness reduction does not transfer directly — Path-FAS
> is a different decision — but it is the natural construction to adapt).

> **(Q2) Among Δ\*(T) = 2 tournaments, is "∃ acyclic degree-2 order"
> polynomial?**  This is the acyclicity-core — the genuine residual once
> the degree layer is settled.  The back-arc graph of a degree-2 order is
> a union of paths and cycles; the question is whether the cycles can
> always be avoided.

## Why this is a real handle (and honest scope)

Both blocked positive routes attacked the *full* linear-forest constraint
at once.  The degreewidth split **isolates** the two halves — degree (a
global, acyclicity-free parameter with existing theory) and acyclicity (a
focused residual on a 29–48 % subfamily) — and connects them to a studied
parameter with known partial complexity.  It does **not** solve Path-FAS;
it relocates the difficulty to a precise, literature-anchored core and
poses two decidable-looking sub-questions.  Tools:
`scripts/degreewidth_decomposition.py`,
`tests/test_degreewidth_decomposition.py`.

**Next concrete steps.** (a) Settle Q1 for k = 2 — adapt the cubic
sparse-recognition or the NP-hardness construction of arXiv:2212.06007 to
the value 2.  (b) Mine the Δ\* = 2 acyclicity-core for what forces the
cycle (the forced-cycle structure, its interaction with the degree-2
budget) — this is where a poly acyclicity test or a hardness gadget would
come from, and it is non-local by construction (the cycle is global).
