# A new direction: the degreewidth decomposition of Path-FAS (D92)

After the four blocked/paused routes (forward-DP / D70, fanout / D90,
cutting-plane / D91, exact ILP), this opens a **global structural
invariant** for tournament Path-FAS that the project had not used, and
that connects the problem to existing literature.

## The invariant

> **Δ\*(T) = degreewidth(T)** = min over vertex orderings of the maximum
> **back-degree** (number of back-arcs incident to a vertex).

This is exactly the parameter **degreewidth** of
[Davot, Isenmann, Roy & Thiebaut, "Degreewidth: a New Parameter for Solving Problems on
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

---

## D93 — tooling, exact census, and first Q1 probes

### Literature status of Q1 pinned (verified vs PDFs, 2026-05-30)

`Δ*≤2` recognition is **class-sensitive** and **open for tournaments**:
  * **Oriented graphs:** `k`-Degreewidth is NP-complete for every `k≥1`
    ("Computing the degreewidth of a digraph is hard", arXiv:2407.19270 v3,
    Thm 2.3 — on 1-subdivisions of multidigraphs; the `k=1` case answers a
    Keeney–Lokshtanov question).
  * **Tournaments:** `Δ*≤1` cubic (Davot et al.); computing `Δ*` NP-hard; but
    **`Δ*≤2` is explicitly OPEN** (also open: FPT-compute-`Δ*` of a
    tournament, FAS-tournament FPT-by-`Δ*`).  The `k=1` poly/NP-hard split
    between tournaments and oriented graphs shows the tournament structure
    is essential — so Q1 is a legitimate, non-duplicative target.

### Efficient exact solver (replaces the O(n!·n²) scan)

`scripts/degreewidth_exact.py` — **Held-Karp subset DP, O(2ⁿ·n)**, exact
to ~n=22.  Rests on the observation that when vertex `v` is appended to a
prefix occupying set `S`, every other vertex is decided (in `S` = before,
else after), so `v`'s back-degree is **fixed at placement**:
> `bd(v | before=S) = |N⁺(v)∩S| + |N⁻(v)∩(V∖S∖{v})|`,
> and `f[S] = min_{v∈S} max(f[S∖v], bd(v|S∖v))`, `Δ*(T)=f[V]`.

Validated: **0 disagreements vs the correct full-permutation scan over all
33 866 labeled tournaments n≤6**; order-reconstruction achieves the value
on random n≤10.  (This also **fixed a latent bug** in
`degreewidth_decomposition.degreewidth`: its `if best<=1: return` early-exit
overestimated `Δ*` as 1 when the true value was 0 — 867/33 866 cases.  Benign
for the YES/NO split, but wrong as an exact value.)

### Exact acyclicity-core census (replaces the doc's 300/150 samples)

Over the **full** certified minimal-NO catalogues:

| n | minimal NOs | Δ\* = 2 (**acyclicity-core**) | Δ\* = 3 (degree-obstructed) |
|---|---|---|---|
| 7 | 20 | 9 (45 %) | 11 |
| 8 | 572 | **202** (35 %) | 370 |
| 9 | 5560 | **2316** (42 %) | 3244 |

Two facts now hold **exactly** (not on a sample):
  * **Every minimal NO has `Δ*∈{2,3}`** — none reaches `Δ*≥4`.  Minimal
    obstructions are degreewidth exactly 2 or 3.
  * **`hall_failure` ⟺ `Δ*≥3`** across all 6152 minimal NOs (0 exceptions);
    the acyclicity-core is exactly `large_width_no ∩ {Δ*=2}`.

### The bd identity and necessary conditions (proved)

For any order, with `i(v)` = position and `b(v)` = #in-neighbours placed
before `v`:
> **`bd(v) = i(v) + d⁻(v) − 2·b(v)`.**

Corollaries (necessary for `Δ*≤2`, PROVED): the **first** vertex has
back-degree `d⁻` and the **last** has back-degree `d⁺`, so a `Δ*≤2`
tournament has a vertex with `d⁻≤2` (a legal first) and one with `d⁺≤2` (a
legal last).  More generally `bd(v)≤2 ⇔ b(v) ≥ (i(v)+d⁻(v)−2)/2`: at least
that many of `v`'s in-neighbours must precede it — an order-dependent
coupling, not a pure positional constraint.

### Two natural Q1 certificates — both REFUTED

`scripts/degreewidth_q1_probe.py` (exhaustive n≤6, random n≤12, hard
catalogues):
  * **(A) in-degree-sorted order is NOT exact.** It misses `Δ*≤2` on
    15 748/32 768 tournaments at n=6 — it is only the known 3-approx, never
    a decision procedure.
  * **(B) Hall-feasibility of the radius-2 windows is necessary but NOT
    sufficient.** `Δ*≤2-but-not-Hall = 0` everywhere (re-confirms the
    score-window lemma), but **`Hall-but-Δ*>2` is nonzero from n=7 on**
    (273 / 459 / 1077 / … at n=7/8/9). So `Δ*≤2` is **not** interval
    scheduling: the gap is exactly the order-dependent `b(v)` term — a
    window-respecting placement can still leave a vertex with too few
    in-neighbours before it.

**Takeaway for Q1.** The obvious poly certificates fail; the live target is
a flow/matching formulation that also controls `b(v)` (in-neighbours
before), or a structural theorem extending Davot et al.'s `Δ*≤1` characterization
to value 2.  The window-prefix count is **not** poly-bounded on near-regular
tournaments (the band `[p−2,p+1]` can contain all `n` vertices when
`d⁻≈(n−1)/2`), so a naive window-DP does not settle Q1 — consistent with the
project's hardness living in the near-regular regime.

**Tools added:** `scripts/degreewidth_exact.py`,
`scripts/degreewidth_q1_probe.py`, `tests/test_degreewidth_exact.py`.
