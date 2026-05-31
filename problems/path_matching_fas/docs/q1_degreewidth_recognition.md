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

### 6.1 Window lemma (PROVED) — TWO-SIDED, see §6.6 correction

> **Lemma.** If `S` is a reachable prefix with `|S| = p`, then every `v∈S`
> has `d⁻(v) ≤ p+1`; i.e. `S ⊆ A_p := {v : d⁻(v) ≤ p+1}`.

*Proof.* Order `S = v_1,…,v_p` witnessing reachability. The vertex `v_k` sits
at position `k−1`, so `bd(v_k) = (k−1) + d⁻(v_k) − 2b` where `b =` #in-
neighbours of `v_k` before it; since `b ≤ k−1`, `bd(v_k) ≥ d⁻(v_k) − (k−1)`.
Reachability gives `bd(v_k) ≤ 2`, so `d⁻(v_k) ≤ (k−1)+2 = k+1 ≤ p+1`. ∎

**Correction (§6.6, D96):** the window is in fact **TWO-SIDED** —
`|i(v) − d⁻(v)| ≤ 2` for every `v∈S` — using only `bd(v)≤2`. (The earlier
"only the lower side survives" remark here was wrong; the upper side does
not need a valid suffix.)

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
cap** — and proving *that* is the open content.

### 6.5 D95 — strengthened necessary conditions and the precise gap

Two further conditions, both **PROVED** by summing/inspecting `bd ≤ 2`
(`bd(v) = (out-nbrs before) + (in-nbrs after)`, and the "after" set of a
prefix includes *all* of `V∖S`):

> **(N2) sum bound.** `Σ_{v∈S} d⁻(v) ≤ C(p,2) + 2p`. Equivalently the number
> of arcs from `V∖S` into `S` is `γ(S) ≤ 2p`. (Sum `bd(v_k)=2c_k+d⁻(v_k)−(k−1)`
> over `S`: `Σbd = 2β + (Σd⁻ − C(p,2)) ≤ 2p`, `β≥0` internal back-arcs.)

> **(N3) per-vertex closure.** Every `v∈S` has `|N⁻(v) ∖ S| ≤ 2` — at most
> two in-neighbours outside `S`. (Its omitted in-neighbours are all "after",
> so `|N⁻(v)∖S| ≤ in-nbrs-after ≤ bd(v) ≤ 2`.) Verified 0 violations in
> 336 693 checks. (N3) ⇒ (N2) and is strictly stronger.

**The reduction.** A reachable size-`p` prefix is a size-`p` subset of
`L = {d⁻ ≤ p+1}` (with `|L| ≤ 2p+3`) whose omitted-low set `C∩L` obeys (N3).
For the maximizer (transitive) `|L| = p+2`, so exactly **2 low vertices are
omitted** (`C(p+2,2)` choices) — the "2" is precisely the `bd ≤ 2` budget.

**Why the blow-up never happens (the crux, established empirically, n≤60).**
The `C(2p+3,p)` candidate explosion would require a *large band of near-equal
in-degree* (so that `|L| ≫ p`). But:
- regular/near-regular tournaments **die at the empty prefix** (`#reachable=1`:
  no vertex has `d⁻≤2`, so nothing is placeable first);
- a **regular sub-block of size ≥ 7 forces Δ\*≥3** (the whole instance is NO);
- embedding a size-`g` regular block gives per-size width `Θ(g²)`, never `2^g`;
- transitive (spread in-degrees, band width exactly 4) is the maximizer at
  `Θ(n³)`, and hill-climbing can't beat it by >2%.

So the in-degree spread that would create many candidate subsets is exactly
what makes the tournament Δ\*≥3 (kills reachability). The **open lemma** that
would finish a proof of `#reachable = poly` (hence Q1 ∈ P):

> **Crux band lemma (D95 framing — now REFUTED, see §6.6).** ~~If the
> size-`p` in-degree band is large, no prefix of size `p` is reachable.~~

### 6.6 D96 — the band lemma is FALSE; the window is two-sided (the real lemma)

I attacked the §6.5 band lemma directly and it turned out to be **false**,
because of a stronger structural fact I had missed.

**Two-sided window lemma (PROVED; corrects §6.1/D94).**
> For every vertex `v` of a reachable prefix `S`, in *any* witnessing order,
> `|i(v) − d⁻(v)| ≤ 2` (`i(v)` = position).

*Proof.* `bd(v) = i(v) + d⁻(v) − 2b(v)` with `b(v)` = #in-neighbours of `v`
before it, and `b(v) ≤ min(i(v), d⁻(v))`. Hence `bd(v) ≥ |i(v) − d⁻(v)|`
(using `b≤d⁻` for one side, `b≤i` for the other). Reachability gives
`bd(v) ≤ 2`. ∎ — verified: max `|i−d⁻| = 2` over all reachable prefixes,
exhaustive n≤6 + random n≤9. (D94 wrongly claimed the upper side needs a
valid suffix; it does not — it only uses `v`'s own back-degree.)

**Consequences (PROVED).** The `p` vertices of `S` occupy positions
`0..p−1` with `v` at a position in `[d⁻(v)−2, d⁻(v)+2]`. Therefore:
- **(W1) per-level cap:** at most **5** vertices of any single in-degree
  value `t` lie in `S` (they need distinct positions in `[t−2,t+2]`);
- **(W2) profile pinned:** sorting `S`'s in-degrees `e_0≤…≤e_{p−1}` gives
  `|e_i − i| ≤ 2`, so `|S ∩ {d⁻ ≤ t}| ∈ [t−1, t+3]` for all `t` — the
  in-degree *profile* of any reachable prefix is fixed to within an `O(1)`
  band, so there are only `poly(n)` valid profiles;
- **(W3) band split:** `|S ∩ {d⁻ ∈ [p−2,p+1]}| ≤ 4`.

**Why the band lemma is FALSE.** By (W3) only ≤4 band vertices are in `S`;
a large band is fine — it is just mostly *omitted*. Explicit witness: embed
a 5-vertex regular block (in-degree 7) in transitive padding at n=15 — a
band of **5** equal-in-degree vertices, yet `Δ\*=2` (the full set is
reachable). So "large band ⇒ unreachable" is wrong; the D95 framing is
retracted. (What actually dies is a large *regular* block of size ≥7 —
because a regular tournament on ≥7 vertices has degreewidth ≥3 *internally* —
not "large band" per se.)

**The genuinely remaining gap (sharpened, still OPEN).** The window/(W1–W3)
conditions are *arc-independent* (they depend only on in-degrees), so they
pin the profile but not *which* vertices at each level are chosen. With `n_t`
vertices of in-degree `t`, the window permits `C(n_t, s_t)` choices per level
(`s_t≤5`), and `∏_t C(n_t,s_t)` can be `2^{Θ(n)}` — e.g. many levels with
`n_t=2`, `s_t=1`. So **the window alone does NOT give a polynomial count.**
The poly bound must come from the *arc-level* condition (N3): equal-in-degree
vertices are **not** freely interchangeable — swapping which one is in `S`
changes the back-arc structure, and reachability (not just the window) forces
the selection. Empirically this pruning is total (`#reachable = Θ(n³)`,
n≤60), but a clean proof that **within-level selection is poly-bounded** is
the open content. This is the corrected, precise residual — narrower than the
(false) band lemma.

Tools: `scripts/q1_reachable_count.py`, `tests/test_q1_degreewidth.py`. (Note:
§6.8/D98 below gives a working GLOBAL reduction — read it for the current
best path; §6.5–6.7 are the local attempts it supersedes.)

### 6.7 D97 — reduction schema + a third refuted conjecture; proof still open

Attacking "within-level selection is poly" produced one clean PROVED lemma,
a reduction schema, and a third refuted bounding conjecture. Honest status:
**Q1 ∈ P is still open.**

**Recursion (hereditary) lemma — PROVED.** For any vertex subset `B`, if `S`
is a reachable prefix of `T` then `S∩B` is a reachable prefix of the induced
sub-tournament `T[B]`. *Proof.* For `v∈S∩B`, the within-`B` back-degree under
the order induced from `S`'s witness is `≤ bd_T(v) ≤ 2` (both the out-before
and in-after sets shrink when restricting to `B`). ∎ Verified 0/523. (So the
within-level choice is a *reachable prefix of the level-block*, restricting
it to the block's low-internal-degree vertices — `O(1)` options per level by
the window, improving D96's `C(n_t,s_t)`.)

**Reduction schema.** Write `low = {d⁻≤p−3}`, `band = {d⁻∈[p−2,p+1]}`, and
`D` = the *deep omissions* `= {w∉S : d⁻(w)≤p−3}`. Then (decomposition,
verified 0 violations, exhaustive n≤7 / 109M prefixes)
`S = (low ∖ D) ∪ (S∩band)`, with `|S∩band| ≤ 4` (W3). So a reachable prefix
is determined by `(D, S∩band)`, and **if `|D| = O(1)` then
`#reachable size-p ≤ C(|low|, |D|)·O(1) = poly`, giving Q1 ∈ P.**

**The deep-omission conjecture `|D| ≤ 2` — REFUTED.** Exhaustive n≤7 gives
`max|D| = 2`, but random n=10 gives `max|D| = 3`. So `|D|` is **not** bounded
by 2 and appears to grow slowly with `n`. The budget argument only yields
`|D| ≤ 2p/3` (3 deep omissions are consistent with (N3) by counting: each
S-vertex absorbs ≤2, ≥9 incidences spread over ≥5 victims is feasible). So
the reduction schema does **not** close the proof: `C(|low|,|D|) = n^{Θ(|D|)}`
is super-polynomial if `|D|` grows.

**Where this leaves Q1 (honest).** The candidate recognizer (reachable-prefix
BFS) and the direct evidence `#reachable = Θ(n³)` (n≤60, hill-climb-robust)
stand. But **a proof of Q1 ∈ P remains open.** The pattern across D94–D97 is
clear and worth recording: every *clean, local* bounding conjecture is
refuted (one-sided window → actually two-sided; band lemma → false; `|D|≤2` →
false). The PROVED necessary conditions (two-sided window, W1–W3, N2, N3,
recursion) are all **arc-independent or local**, and each permits an
exponential count; the true pruning to `Θ(n³)` is a *global* effect (the
shared `bd≤2` budget across the whole order) that none of these local
certificates captures. A proof likely needs a genuinely global argument
(a potential/exchange argument over full orders, or an amortized charging
that ties the per-size choices to the global budget) rather than another
necessary-condition-plus-counting decomposition.

Tools: `scripts/q1_reachable_count.py`, `tests/test_q1_degreewidth.py`.

### 6.8 D98 — a GLOBAL exchange/diameter reduction (band part proved; one piece left)

The local routes (§6.5–6.7) all failed because their conditions are
arc-independent and permit exponential counts. A **global** (pairwise)
statement does better. Define the *diameter* at size `p` as the maximum
symmetric difference `|S △ S'|` over reachable prefixes `S, S'` of size `p`.

> **Diameter reduction (PROVED).** If the diameter at every size is `≤ c`
> (a constant), then `#reachable size-p ≤ Σ_{j=0}^{c/2} C(p,j)·C(n−p,j) =
> O(n^c)`, so the reachable-prefix BFS runs in `poly(n)` and **Q1 ∈ P**.

*Proof.* Fix any reachable `S₀` of size `p`. Every reachable `S` of size `p`
has `|S △ S₀| ≤ c`, i.e. `S` is obtained from `S₀` by removing `j ≤ c/2`
vertices and adding `j`. The number of such `S` is `Σ_{j≤c/2} C(p,j)C(n−p,j)`.
Summing over `p` gives `O(n^{c+1})` total. ∎

So Q1 ∈ P reduces to: **the diameter is bounded by a constant.** This is a
genuine exchange statement — any two reachable prefixes of the same size
differ by `≤ c/2` element-swaps.

**Decomposition of the diameter (PROVED, partially).** `S △ S' ⊆ L =
low ∪ band` (the high vertices `d⁻ > p+1` are excluded from every reachable
prefix by the window), so
`|S △ S'| = |(S△S') ∩ band| + |D △ D'|`, where `D, D'` are the deep-omission
sets `{w∉S : d⁻(w) ≤ p−3}`.
- **Band part `≤ 8` — PROVED:** `(S△S') ∩ band ⊆ (S∩band) ∪ (S'∩band)`, and
  `|S∩band|, |S'∩band| ≤ 4` by (W3). So `|(S△S')∩band| ≤ 8`, *with no
  dependence on `n`*.
- **Deep part `|D △ D'|` — the one open piece.** Empirically `≤ 4`
  (exhaustive n≤6: deep-part ≤1; adversarial n≤20: ≤4). Crucially, this is a
  *pairwise difference*: even though a single prefix's `|D|` grows with `n`
  (D97), any two reachable prefixes omit **nearly the same** deep vertices.

**Evidence for bounded diameter.** Exhaustive over all tournaments n≤6:
**max diameter = 6**. Adversarial (random + dense-YES + transitive +
reversed-matching) n = 8,10,12,14,16,20: max diameter `8,8,8,6,6,6` —
**bounded, not growing.** Transitive and reversed-matching give exactly 4.

**Status.** This is the cleanest reduction obtained: Q1 ∈ P now follows from
a single bounded-diameter (exchange) statement, whose band component is fully
proved and whose only open component is `|D △ D'| = O(1)` — a *pairwise*
deep-omission bound, robust under all testing (unlike the refuted *single*
bound `|D|≤2` of D97). Proving `|D △ D'| = O(1)` — equivalently, that the
omitted deep vertices are determined up to `O(1)` across all reachable
size-`p` prefixes — would close Q1 ∈ P. This is the recommended next target.

Tools: `scripts/q1_reachable_count.py`, `tests/test_q1_degreewidth.py`.
