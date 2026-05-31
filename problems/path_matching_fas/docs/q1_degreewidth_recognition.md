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

---

## 6. D94 — the reachable-prefix recognizer: Q1 ∈ P modulo a counting bound

The forward DP is cleanest stated over **reachable prefixes**. A subset
`S ⊆ V` is a *reachable prefix* if it can be linearly ordered as the first
`|S|` positions so that **every vertex of S has back-degree ≤ 2** (the rest of
`V` placed afterwards). Reachability BFS, by increasing `|S|`:
`∅` reachable; `S∪{u}` reachable from reachable `S` iff
`bd(u|S) = 2·|N⁺(u)∩S| + d⁻(u) − |S| ≤ 2`. Then **Δ\*(T) ≤ 2 iff `V` is
reachable**. This BFS *is* a recognizer; its cost is `Θ(#reachable · n)`.

**The recognizer is exact (verified).** `reachable(V)` ⟺ `Δ\*≤2` with **0
disagreements** vs the exact Held-Karp solver over all 33 866 tournaments
n≤6 + 20 000 random n=7. So Q1 reduces entirely to: **is `#reachable`
polynomial?** (`scripts/q1_reachable_count.py`.)

### 6.1 One-sided window lemma (PROVED)

> **Lemma.** If `S` is a reachable prefix with `|S| = p`, then every `v∈S`
> has `d⁻(v) ≤ p+1`; i.e. `S ⊆ A_p := {v : d⁻(v) ≤ p+1}`.

*Proof.* Order `S = v_1,…,v_p` witnessing reachability. The vertex `v_k` sits
at position `k−1`, so `bd(v_k) = (k−1) + d⁻(v_k) − 2b` where `b =` #in-
neighbours of `v_k` before it; since `b ≤ k−1`, `bd(v_k) ≥ d⁻(v_k) − (k−1)`.
Reachability gives `bd(v_k) ≤ 2`, so `d⁻(v_k) ≤ (k−1)+2 = k+1 ≤ p+1`. ∎

(This is the *prefix* analogue of the score-window lemma — only the lower
side `i(v) ≥ d⁻(v)−2` survives, because a reachable prefix needs no valid
suffix. Verified: 0 violations on random n≤10.)

### 6.2 #reachable is Θ(n³) empirically (the candidate poly bound)

- **Transitive** tournaments are an exact maximizer skeleton: size-`p`
  reachable prefixes `= C(p+2,2)` (drop any 2 of the `p+2` lowest-in-degree
  vertices), total `= Θ(n³)` (ratio `#reachable/n³ → ≈ 1/6`, steady across
  n=6..60).
- **Hill-climbing** to *maximize* `#reachable` from transitive cannot beat it
  by more than ~2% (n=12: 305 vs 299; ratio stays ≈ `0.17·n³` at n=12,16,20).
- **Reversed-matching** → `Θ(n²)`; dense-YES → ~constant; **near-regular /
  regular tournaments die at the empty prefix** (`#reachable = 1`: no vertex
  has `d⁻≤2`, so none can be placed first) — the in-degree growth that would
  blow up the count is exactly what makes the tournament Δ\*≥3.
- No super-polynomial family found up to **n=60**.

⇒ **Strong evidence: `#reachable = Θ(n³)`, hence the BFS is an `O(n⁴)`
recognizer and Q1 ∈ P** — *conditional on a proof of the count bound.*

### 6.3 What is NOT the algorithm

**Greedy is incomplete (REFUTED).** "Repeatedly place any placeable vertex"
(min-back-degree, min/max-`d⁻`, or first) all FAIL: each misses thousands of
YES instances already at n≤6 (min-`d⁻` misses 2390/33 866; all rules sound
but incomplete). The placement choice genuinely matters, so Q1 is not a
one-pass greedy — the BFS (which keeps all reachable prefixes) is needed.

### 6.4 The precise open problem

> **Conjecture (Q1-poly).** For every tournament `T`, `#reachable prefixes`
> is `poly(n)` (evidence: `Θ(n³)`). This implies **Q1 ∈ P**.

The gap is sharp. The one-sided lemma gives `S ⊆ A_p`, but Landau's
inequality only forces `|A_p| ≤ 2p+3`, so the in-degree cap alone permits
`C(2p+3, p) = 2^{Θ(p)}` candidate size-`p` subsets. The actual count is
`Θ(n³)`, so **reachability prunes super-exponentially below the in-degree
cap** — and proving *that* is the open content. A proof needs to combine the
one-sided cap with the per-vertex `c(u)` (out-neighbours-already-placed)
constraint, e.g. via the sum bound `Σ_{v∈S} d⁻(v) ≤ C(|S|,2) + 2|S|` (arcs
into `S` from outside ≤ `2|S|`, proved by summing `bd ≤ 2`). Tools:
`scripts/q1_reachable_count.py`, `tests/test_q1_degreewidth.py`.
