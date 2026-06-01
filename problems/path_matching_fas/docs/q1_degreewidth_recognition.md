# Q1: recognizing Δ*(T) ≤ 2 for tournaments

**Q1.** Is "Δ*(T) ≤ 2" (degreewidth ≤ 2) decidable in polynomial time for
tournaments?  This memo records the forward-DP line of attack.

> **⚠ ALREADY SOLVED IN THE LITERATURE — this whole Q1 chapter is NOT novel
> (2026-06-01).** We wrongly believed `Δ*≤2` was open for tournaments. It is
> not: Keeney & Lokshtanov, "Degreewidth on Semi-Complete Digraphs" (WG 2024,
> `Ref/DegreewidthPaper_240419_165002.pdf`) Theorem 2 decides `Δ*≤k` and
> computes an optimal degreewidth ordering in `k^{O(k)} n + O(n²)` — i.e.
> degreewidth is **FPT** (so `Δ*≤2` is `O(n²)`), strictly stronger than our
> XP `n^{O(k)}` / `O(n⁹)`. Their restricted-ordering-graph DP (windows
> `[i−cΔ, i+cΔ]`) IS our score-window / reachable-prefix DP; their Lemma 3 /
> Corollary 1 is our two-sided window + forced/flexible split. (Earlier notes
> mischaracterized this paper as "3-approx only, does not settle k=2".)
> The genuinely-open problem — Path-FAS / linear-forest ordering (Aboulker
> 4.4) — is NOT in their paper (their FAS is standard min-FAS).

For consolidated writeups, see `docs/q1_quasipoly_writeup.md` (D94–D102,
superseded) and `docs/q1_polynomial_writeup.md` (D103, current theorem).  The
present file is the research log.

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

### 6.9 D99 — proof attempt for |D△D'|=O(1): budget-localization proved, not closed

Goal: prove the deep part of the diameter, `|D△D'| = O(1)` (would close
Q1 ∈ P via §6.8). **Not achieved.** Progress + honest blocker below.

**Budget-localization lemma — PROVED** (verified 0 violations / 6.46M checks,
exhaustive n≤6 + random n≤11):
> For a reachable size-`p` prefix `S` and any `s < p`,
> `#{w ∉ S : d⁻(w) ≤ s} · (p − s) ≤ 2p`.

*Proof.* Each omitted `w` with `d⁻(w) ≤ s` has out-degree `≥ n−1−s`, so
`|N⁺(w)∩S| ≥ (n−1−s) − (|C|−1) = p − s`. Summing, `(#such)·(p−s) ≤
Σ_{w∈C}|N⁺(w)∩S| = γ = Σ_{v∈S}|N⁻(v)∩C| ≤ 2p` (the last by (N3): each `v∈S`
has `≤2` in-neighbours in `C`). ∎

**Consequence.** `#{omitted with d⁻ ≤ p−k} ≤ 2p/k`. In particular
`#{omitted with d⁻ ≤ p/2} ≤ 4` — a **constant**. So the contribution to
`D△D'` from omissions of in-degree `≤ p/2` is `≤ 8`. Combining with the
proved band bound (§6.8):
> `diameter ≤ 8 (band) + 8 (omissions d⁻≤p/2) + |differences among omissions
> with d⁻ ∈ (p/2, p−3]|`.

**The fully-localized remaining gap.** Only omissions in the in-degree window
`(p/2, p−3]` (just below the band) are not bounded by the budget — there the
bound is only `≤ 2p/3`. So `|D△D'| = O(1)` is now equivalent to: *the omitted
vertices of in-degree in `(p/2, p−3]` are determined up to `O(1)` across all
reachable size-`p` prefixes.* Empirically the whole deep part is `≤ 4`
(exhaustive n≤6, hill-climb, every construction to n≤30), so even this window
contributes `O(1)` — but a proof is missing.

**Honest blocker.** Many omissions in `(p/2, p−3]` would require a tournament
with many vertices of in-degree just below `p` — a *clustered* in-degree
profile, which pushes toward near-regular and hence `Δ\*≥3` (unreachable). So
the dangerous regime is plausibly empty (which is *why* `|D△D'|` stays
`O(1)`), but formalizing "clustered just-below-`p` ⟹ no reachable size-`p`
prefix, OR the omissions there are arc-forced" is exactly the unproved step.
The budget argument cannot reach it (it gives `2p/3` in that window); a proof
needs the arc structure / the actual ordering, not a counting bound.

**Status.** Q1 ∈ P remains OPEN. Across D94–D99 it is reduced to a single,
well-isolated, heavily-tested pairwise statement (`|D△D'| = O(1)`, the band
part proved, the low-`d⁻≤p/2` part proved, only the `(p/2,p−3]` window open),
robust under adversarial search (hill-climb cannot break the diameter past 8).
A proof appears to require a genuinely arc-level argument in the just-below-
band window; the counting/budget toolkit is exhausted there.

Tools: `scripts/q1_reachable_count.py`, `tests/test_q1_degreewidth.py`.

### 6.10 D100 — cluster-excision lemma (PROVED): a near-regular cluster cannot be split

The arc-level lemma behind the "clustered ⟹ dies" tension, now proved.

> **Cluster-excision lemma.** Let `B ⊆ V(T)` with every vertex of `B` having
> `≥ 3` in-neighbours *within* `B` (internal in-degree `≥3`; e.g. `T[B]`
> regular or near-regular with `|B| ≥ 7`). Then `S ∩ B = ∅` for **every**
> reachable prefix `S` of `T`.

*Proof.* In `T[B]`, a size-1 reachable prefix is a single vertex `v` placed
first, with within-`B` back-degree `= |N⁺_B(v) ∩ ∅| + |N⁻_B(v) ∩ (B∖v)| =`
internal in-degree of `v`. If every internal in-degree is `≥3`, no vertex
admits a size-1 reachable prefix, so `μ(T[B]) = 0` (the only reachable prefix
of `T[B]` is `∅`). By the recursion lemma (D97), `S∩B` is a reachable prefix
of `T[B]`; hence `S∩B = ∅`. ∎

Verified: `μ(regular circulant) = 0` for all `g≥7` (internal in-degree
`(g−1)/2 ≥ 3`), while `g=3,5` give `μ=g` (Δ\*≤2). An embedded regular block
of size 7 or 9 — at in-degrees `6,7,8,11,12`, including just below the band —
has **0** block-vertices in any reachable prefix (across all of them).

**What this settles.** A regular (or min-internal-in-degree-`≥3`) cluster of
size `≥7` placed anywhere — in particular *just below `p`* — is entirely
excluded from every reachable prefix: it is **not split**, it is uniformly
omitted. So such a cluster contributes **0** to `D△D'` (every reachable
prefix omits all of it). This also makes the "clustered ⟹ dies" tension
rigorous: if such a cluster is large (`> 2p/3` vertices, each beating `≥3` of
any size-`p` prefix), the (N3) budget `γ≤2p` is violated, so `T` has **no**
reachable size-`p` prefix at all.

**Honest scope — does NOT close `|D△D'|=O(1)`.** The lemma forces *dense*
clusters (min internal in-degree `≥3`) to be uniformly omitted. But a cluster
just below `p` that is *internally sparse* (some vertex with `≤2` internal
in-neighbours, so `μ(T[B]) ≥ 1`) can have a nonempty `S∩B`, and *which*
vertices are included may vary across reachable prefixes. Bounding that
variation across the (possibly many) internally-sparse near-band levels is
the part the excision lemma does not reach — the level-multiplication issue
of D97 persists for sparse clusters. So Q1 ∈ P remains **open**; the
excision lemma proves the requested "regular cluster can't be split" and
explains the mechanism, but the full `|D△D'|=O(1)` needs control of the
internally-sparse near-band levels too.

Tools: `scripts/q1_reachable_count.py`, `tests/test_q1_degreewidth.py`.

### 6.11 D101 — bounding the variation: a SUBEXPONENTIAL recognizer (proved)

Attempting to bound the diameter, the budget-localization (D99) and a
generalized window bound combine to give a proved `O(√p)` diameter, hence a
subexponential algorithm for Q1 — short of poly, but a genuine new result.

**Window-`U_k` bound (PROVED; verified 0 / 10.15M checks).**
> For a reachable size-`p` prefix `S` and any `k ≥ 0`,
> `|S ∩ {v : d⁻(v) ∈ [p−k, p+1]}| ≤ k + 2`.

*Proof.* A vertex `v∈S` with `d⁻(v) ≥ p−k` sits (two-sided window) at a
position `≥ d⁻(v)−2 ≥ p−k−2`, and `≤ p−1`. That is `k+2` positions, so at
most `k+2` such vertices. ∎ (W3 is the case `k=3`.)

**Diameter bound (PROVED).**
> For reachable size-`p` prefixes `S, S'`, `|S △ S'| ≤ 6√p + 4`.

*Proof.* Split at threshold `s = p − ⌈√p⌉`.
- `d⁻ ≤ s`: every differing vertex here is omitted from one of `S, S'`, so
  `|(S△S')∩{d⁻≤s}| ≤ #{omitted from S, d⁻≤s} + #{omitted from S', d⁻≤s}`.
  By budget-localization, each term is `≤ 2p/(p−s) = 2p/⌈√p⌉ ≤ 2√p`, total
  `≤ 4√p`.
- `d⁻ > s` (i.e. `d⁻ ∈ [p−⌈√p⌉+1, p+1]`): by the window-`U_k` bound with
  `k = ⌈√p⌉−1`, `|S ∩ {d⁻>s}| ≤ ⌈√p⌉+1`, same for `S'`; variation
  `≤ 2(⌈√p⌉+1) ≤ 2√p + 4`.

Total `≤ 6√p + 4`. ∎ (Verified: `diameter / (6√p+4) ≤ 0.42` over all tests.)

**Consequence — Q1 ∈ subexponential time.**
> `#reachable size-p ≤ #{S : |S△S₀| ≤ 6√p+4} ≤ Σ_{j≤3√p+2} C(p,j)C(n−p,j)
> ≤ n^{O(√p)}`. Summed, `#reachable ≤ n^{O(√n)}`. So the reachable-prefix BFS
> **decides Δ\*(T) ≤ 2 in time `n^{O(√n)}`** — subexponential, vs the `2ⁿ`
> Held–Karp DP.

**Status of Q1 ∈ P.** Still open, but the gap is now exactly the `√p` slack:
the diameter is *proved* `O(√p)` and *empirically* `O(1)` (`≤8`, flat to
n=40, hill-climb-robust). Closing to `O(1)` needs a better bound on the
variation inside the near-band window `(p−√p, p+1]` than the trivial window
count — exactly where the cluster-excision lemma (D100) removes the *dense*
clusters, leaving only internally-sparse near-band levels. A recursion
(`S∩W` is a reachable prefix of `T[W]`, D97) suggests an inductive `O(log p)`
diameter bound (→ quasi-polynomial `n^{O(log n)}`), but the induction's
size-reduction is unverified. **Net: Q1 ∈ DTIME(`n^{O(√n)}`) proved;
Q1 ∈ P conjectured (O(1) diameter), strongly supported.**

Tools: `scripts/q1_reachable_count.py`, `tests/test_q1_degreewidth.py`.

### 6.12 D102 — the induction closes: Q1 ∈ QUASI-POLYNOMIAL time n^{O(log n)}

The recursion `S∩W` = reachable prefix of `T[W]` (D97) makes the diameter
bound inductive, improving D101's `O(√p)` to `O(log p)`.

**Theorem (logarithmic diameter).** Let `D(p)` = the maximum of `|S △ S'|`
over same-size reachable prefixes of size `p`, over **all** tournaments, and
let `F(p) = max_{q ≤ p} D(q)` be its monotone envelope. Then `F(p) = O(log p)`.

*(Two bookkeeping points, both handled below. (i) The recursion compares two
prefixes of `T[W]` of a COMMON size `q ≤ ⌈p/2⌉+1` that is not necessarily
exactly `⌈p/2⌉+1`, so we bound by the monotone envelope `F`, not `D` at a
fixed argument. (ii) Under ordinary symmetric difference the base value is not
`p`: e.g. in transitive `T_4`, two size-2 reachable prefixes can have
`|S△S'| = 4`. We use the trivial bound `D(q) ≤ 2q`, so `F(4) ≤ 8`; this only
changes the additive constant.)*

*Proof.* Split at `s = ⌊p/2⌋`; let `W = {v : d⁻(v) ∈ [s+1, p+1]}`. For
same-size reachable `S, S'` (every reachable prefix excludes `{d⁻ ≥ p+2}` by
the window, so `S, S' ⊆ {d⁻ ≤ ⌊p/2⌋} ∪ W`):
1. **Low part `≤ 8`.** Each vertex of `(S△S')∩{d⁻≤s}` is omitted from one of
   `S, S'`; by budget-localization (D99), `#{omitted, d⁻≤s} ≤ 2p/(p−s) ≤ 4`,
   so `|(S△S')∩{d⁻≤s}| ≤ 8`.
2. **Window part.** `(S△S')∩W = (S∩W) △ (S'∩W)`, and by the recursion lemma
   (D97) `S∩W`, `S'∩W` are reachable prefixes of `T[W]`. By window-`U_k`
   (D101), `|S∩W|, |S'∩W| ≤ ⌈p/2⌉+1`, and by (1)'s budget bound their sizes
   differ by `≤ 4`. Let `q = min(|S∩W|, |S'∩W|) ≤ ⌈p/2⌉+1`. Truncating the
   larger to size `q` (drop its last `≤4` placed vertices — a suffix of a
   witnessing order, so still a reachable prefix of `T[W]`) costs `≤4` and
   leaves two **same-size-`q`** reachable prefixes of `T[W]`, so
   `|(S∩W)△(S'∩W)| ≤ 4 + D(q) ≤ 4 + F(⌈p/2⌉+1)` (monotone envelope, fix (i)).

Hence `D(p) ≤ 8 + 4 + F(⌈p/2⌉+1) = 12 + F(⌈p/2⌉+1)`, and since the RHS is
non-decreasing in `p`, `F(p) ≤ 12 + F(⌈p/2⌉+1)`. For `p ≥ 5`, `⌈p/2⌉+1 < p`,
so with base `F(4) ≤ 8` (fix (ii)) unrolling gives
`F(p) ≤ 12⌈log₂ p⌉ + 8 = O(log p)`, hence `D(p) ≤ F(p) = O(log p)`. ∎

(Verified 0 violations over millions of reachable pairs: low part `≤8`,
size-difference `≤4`, `|S∩W| ≤ ⌈p/2⌉+1`; and `diameter ≤ 12⌈log₂p⌉+12`
holds with ratio `≤0.22`.)

**Theorem (quasi-polynomial recognizer).**
> `#reachable size-p ≤ #{S : |S△S₀| ≤ D(p)} ≤ Σ_{j ≤ 6⌈log₂p⌉+2}
> C(p,j)·C(n−p,j) ≤ n^{O(log n)}`. Summed over `p`, `#reachable ≤ n^{O(log n)}`.
> So the reachable-prefix BFS **decides Δ\*(T) ≤ 2 in quasi-polynomial time
> `n^{O(log n)}`.**

This supersedes D101 (`n^{O(√n)}`): **degreewidth-≤2 recognition for
tournaments is in quasi-polynomial time.**

**Positioning (precise).** State it as: *Δ\*≤2 recognition for tournaments is
quasi-polynomial; polynomiality remains open and is equivalent, for this
route, to proving that the same-size reachable-prefix diameter is bounded by
an absolute constant.* (Do not write "almost P".) The gap is exactly `O(log n)`
(proved) vs `O(1)` (the equivalent open statement; empirically the diameter is
`≤8`, flat to n=40, hill-climb-robust). The recursion adds a genuine `+12` per
level over `O(log p)` levels — the low-part-`8` and size-difference-`4` do not
telescope — so closing to `P` needs a **non-recursive** proof of constant
diameter, not a refinement of this recursion.

**Literature anchoring (verified vs sources, 2026-06-01).** Degreewidth was
introduced by **Davot, Isenmann, Roy & Thiebaut** (arXiv:2212.06007): sparse
tournaments = degreewidth 1, recognized in cubic time; computing tournament
degreewidth is NP-hard. **Aboulker et al.** (arXiv:2407.19270, DMTCS 2026)
prove `k`-Degreewidth NP-complete for every `k≥1` on **oriented graphs**.
D102 addressed the tournament `Δ\*≤2` case with a quasi-polynomial algorithm;
D103 below supersedes it with a polynomial-time algorithm. (Earlier drafts
misattributed the first paper to "Bessy et al."; corrected.)

Tools: `scripts/q1_reachable_count.py`, `tests/test_q1_degreewidth.py`.

### 6.13 D103 — the missing exchange argument: Q1 ∈ P

The constant-diameter target from D98/D102 is now closed.  The proof is a
one-line use of (N3) on both prefixes; the recursive window machinery was
overkill.

**Theorem (absolute diameter).** Let `S,S'` be reachable prefixes of the same
size `p` in a tournament. Then `|S △ S'| ≤ 8`.

*Proof.* Put `A = S∖S'`, `B = S'∖S`; since `|S|=|S'|`, let
`|A|=|B|=m`.  For every `a∈A`, all vertices of `B` lie outside `S`, so (N3)
for the reachable prefix `S` gives at most two arcs from `B` into `a`.
Hence `e(B,A) ≤ 2m`.  For every `b∈B`, all vertices of `A` lie outside `S'`,
so (N3) for `S'` gives at most two arcs from `A` into `b`; hence
`e(A,B) ≤ 2m`.  But between `A` and `B` the tournament has exactly one arc
per pair, so

`m² = e(A,B)+e(B,A) ≤ 4m`.

Thus either `m=0` or `m≤4`, and `|S△S'|=2m≤8`. ∎

**Polynomial recognizer.** Fix any reachable `S₀` of size `p`.  Every
reachable size-`p` prefix differs from `S₀` by at most four removals and four
insertions, so

`#reachable size-p ≤ Σ_{j=0}^4 C(p,j)C(n−p,j) = O(n⁸)`.

Summing over `p` gives `O(n⁹)` reachable prefixes; trying all one-vertex
extensions gives a straightforward polynomial-time recognizer (e.g. `O(n¹⁰)`
extension checks, before bit-operation costs).  Therefore **tournament
degreewidth-≤2 recognition is in P**.

**General fixed-`k` form.** The same argument gives same-size reachable-prefix
diameter `≤4k` for the `Δ*≤k` reachable-prefix DP, hence tournament
`k`-Degreewidth is decidable in `n^{O(k)}` time.  For Q1, `k=2`, this is the
desired polynomial theorem.

Tools: `docs/q1_polynomial_writeup.md`, `tests/test_q1_degreewidth.py`
(`test_constant_diameter_exchange_bound`).
