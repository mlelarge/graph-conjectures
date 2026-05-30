# Q1: recognizing Δ*(T) ≤ 2 for tournaments

**Q1.** Is "Δ*(T) ≤ 2" (degreewidth ≤ 2) decidable in polynomial time for
tournaments?  OPEN in the literature: NP-hard for general oriented graphs
(arXiv:2407.19270, Thm 2.3, all k≥1); for tournaments only `Δ*≤1` is settled
(cubic, Bessy et al.).  This memo records the forward-DP line of attack.

## 1. The clean forward reformulation (PROVED)

Build the order left to right.  Appending vertex `u` to a prefix occupying
set `S` (current position `p = |S|`), every other vertex is decided, so `u`'s
back-degree is **fixed at placement**.  With `c(u) = |N⁺(u) ∩ S|` (out-
neighbours of `u` already placed = back-arcs `u` has accrued):

> **bd(u | S) = 2·c(u) + d⁻(u) − |S|.**

(Verified identically against the exact masks DP on samples n≤11.)  So `u` is
**legally placeable next iff `2·c(u) + d⁻(u) − p ≤ 2`**, i.e.
`c(u) ≤ (2 + p − d⁻(u))/2`.  `c(u)` is monotone non-decreasing as the prefix
grows.  This gives a forward reachability DP whose state is the prefix set
`S`; the **only** information about `S` that matters for the future is the
multiset of counts `c(u)` over unplaced `u` (the **active profile**).

## 2. Why Q1 is NOT blocked by the D70 lower bound

The project's forward-DP lower bound (D70) gives `2^Ω(n)` states for
**Path-FAS** — but its fooling family distinguishes prefixes by **acyclicity**
of the back-arc graph at fixed back-degree ≤2 (verified: the D70 toggle+probe
family is Δ*=2 and every fooling failure is a *cycle*, never a degree-3 vertex
— see `docs/q2_acyclicity_core.md`).  **Q1 is the degree-only question** and
ignores acyclicity entirely, so D70 imposes **no** lower bound on the Q1
forward DP.  This is the key Q1/Q2 asymmetry: the same forward-DP idea that is
provably dead for Q2 is a **live poly candidate for Q1**.

## 3. Empirical state size of the Q1 forward DP

`scripts/q1_state_compress.py`, `scripts/q1_frontier_on_yes.py`, and the
adversarial sweep measure the reachable state on YES (Δ*≤2) instances (the
hard regime — random tournaments are mostly NO and die instantly).

* **active-frontier** (# unplaced `u` with `c(u)>0`) **grows linearly** with
  `n` — so the naive subset state is not trivially bounded.
* **distinct active-profiles per size** stays **small and roughly flat**:
  ~20–33 across n=7..14 on generic YES; and on adversarial dense-back-arc
  YES (back-arc prob 0.95, near degree-saturated, 800 samples each) the
  **MAX distinct profiles/size was 22 at n=12 and 20 at n=16** — i.e. it
  does **not** grow with n.  No super-polynomial blow-up family was found
  (regular circulants, the natural near-regular candidates, are all Δ*≥3 and
  thus not even YES).

This is **evidence (not proof)** that the number of distinct reachable active
profiles is polynomially bounded, which would put Q1 in P.  It is the exact
analogue of the question that *failed* for Q2 (where the D70 family forces
`~3^{n/4}` distinct extension-classes) — but for Q1 no such family is known,
consistent with §2.

## 4. Structural facts

* **First Δ*≥3 tournament appears at n = 7** (all n≤6 tournaments are Δ*≤2,
  exhaustive).  Necessary conditions (from the identity): a Δ*≤2 tournament
  has a vertex of in-degree ≤2 (legal first) and one of out-degree ≤2 (legal
  last).
* **Regular circulant tournaments** (`i → i+1..i+⌊n/2⌋`) are **Δ*≥3** for all
  odd n=7..27 — the maximally symmetric near-regular family is degree-
  obstructed, so the hard YES instances for Q1 are *not* the regular ones.
* Refuted certificates (from `docs/degreewidth_direction.md` D93): in-degree
  sort is not exact; Hall-feasibility of radius-2 windows is necessary but not
  sufficient.

## 5. Verdict and next step

**Verdict on Q1:** unresolved, but the forward-DP route is **not refuted** and
looks promising — unlike Q2 it carries no D70 lower bound, and the reachable
active-profile count is empirically bounded.  The concrete open target is a
**proof that the number of distinct reachable active profiles of the Δ*≤2
forward DP is poly(n)** (equivalently: a structural bound on how many unplaced
vertices can simultaneously carry distinct `c`-obligations in a surviving
prefix).  A proof gives Q1 ∈ P; a counterexample YES family with
super-poly distinct profiles would refute it (none found to n=28).

Tools (all `q1_`-prefixed): `scripts/q1_frontier.py` (identity check),
`scripts/q1_state_compress.py`, `scripts/q1_frontier_on_yes.py`,
`scripts/q1_min_obstructions.py`.
