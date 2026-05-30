# D77: The Single-Port Slide Lemma

> **CORRECTION (see `docs/lemma_c_both_values.md`).**  Lemma C is the
> **both-values** statement (no EQ_2 gadget has capacity on *both* 00
> and 11), not the one-value form.  A single-port slide *from one
> equality witness* being blocked is therefore **consistent** with
> R_T = EQ_2 (the 16 n=7 cap-on-00 gadgets are exactly that) and does
> **not** by itself attack Lemma C.  What survives below as
> load-bearing is the *blocker classification* (Lemmas S1, S3); the
> actual both-values attack is the saturation sub-claim in D78.  Read
> this doc for the local-move mechanics, D78 for the corrected target.

This develops the local move and blocker classification feeding
**Lemma C** (the 2-port heart of the Fanout Barrier, see
`docs/fanout_barrier_synthesis.md`):

  > **Lemma C.**  No tournament gadget realizes R_T = EQ_2 = {00,11} on
  > two vertex-disjoint ports with joint capacity on BOTH equality
  > vectors.

Lemma R (proved, all n) reduces the whole Fanout Barrier to Lemma C.
This note develops the **Single-Port Slide Lemma**, the local move on
which a two-port contradiction will rest, with the exact blocker
classification, grounded by an exhaustive n ≤ 7 census.

## 1. Setup and the slide

Tournament T; two vertex-disjoint ports P = (a, b), Q = (c, d) with
R_T = EQ_2 = {00, 11}.  Fix a valid LFO σ realizing port-bits (0, 0)
with **joint capacity**: every port endpoint a, b, c, d has back-arc
degree ≤ 1 in σ.

The back-arc graph B_σ has max-degree ≤ 2 and is acyclic (a linear
forest), and each port endpoint sits on it with degree ≤ 1.

**The slide.**  To flip P's bit we move one endpoint of P across its
mate by adjacent transpositions.  Say we move the left endpoint x of P
(x ∈ {a, b}, whichever is earlier in σ) rightward past the vertices
between it and its mate, until it crosses the mate.

**Adjacent-transposition rule.**  Moving x rightward past an immediate
neighbour v changes exactly the arc {x, v} (no other arc):

  * if T has x → v: the arc was forward (x left of v) and **becomes a
    back-arc** — *add* {x, v}, raising deg(x) and deg(v) by 1;
  * if T has v → x: the arc was a back-arc and **stops being one** —
    *remove* {x, v}, lowering deg(x) and deg(v) by 1.

## 2. Degree-accounting lemma (PROVED)

> **Lemma S1.**  As x slides right across a set X of crossed vertices
> (in order), deg(x) changes by +1 for each crossed **out-neighbour**
> (x → v) and −1 for each crossed **in-neighbour** (v → x).  In
> particular, after crossing m out-neighbours and ℓ in-neighbours,
> deg(x) = deg_σ(x) + (running surplus of out- over in-neighbours).

Proof: immediate from the transposition rule; only {x, v} changes per
step.  ∎

Because σ has capacity, deg_σ(x) ≤ 1.  To flip P's bit, x must cross
its mate; the mate is an out- or in-neighbour of x in T.  The crossed
set is exactly the vertices strictly between x and its mate in σ, plus
the mate.

## 3. Single-Port Slide dichotomy (PROVED, modulo Q-disjointness)

> **Lemma S2.**  Suppose the slide crosses no Q-endpoint (so Q's bit is
> unchanged).  Then the slid order is **either**
>   (a) a valid LFO — in which case it realizes port-bits (1, 0), a
>       MIXED vector, contradicting R_T = EQ_2; **or**
>   (b) not a valid LFO — i.e. the linear-forest constraint fails:
>       some vertex reaches back-degree 3 (**degree saturation**) or a
>       loaded back-arc closes a **cycle**.

Proof: a vertex order is a valid LFO iff its back-arc graph is a linear
forest (max-degree ≤ 2, acyclic).  The slid order either is one or is
not; (a) and (b) are exactly these two cases.  If (a), the bit vector
lies in R_T; since P flipped and Q is unchanged, it is (1, 0) ∉ EQ_2,
contradiction.  ∎

The content is that case (a) is **impossible**, forcing (b): the slide
is always blocked.  Proving "(a) impossible for all n" is exactly the
strength of Lemma C; the slide reformulates it as **"every single-port
flip is blocked by degree saturation or cycle."**

## 4. Exact blocker mechanism (PROVED locally; the saturating vertex is
the moved endpoint)

> **Lemma S3 (blocker localization).**  At the first blocking
> transposition, the violated linear-forest condition involves the
> **moved endpoint x itself** or the just-crossed vertex v:
>   * degree saturation: deg(x) reaches 3 (x accumulated back-arcs to
>     crossed out-neighbours, Lemma S1), or deg(v) reaches 3;
>   * cycle: the added back-arc {x, v} joins two vertices already in the
>     same component of the current back-arc forest — necessarily the
>     component containing x.

Proof: an adjacent transposition changes only {x, v}; a new violation
can therefore only be a degree-3 at an endpoint of {x, v}, or a cycle
through the newly added edge {x, v}, whose endpoints are x and v.  ∎

**Worked example (n = 7, verified).**  Gadget with ports (0,3),(2,4),
orientation (1,1); capacity witness σ = [5,4,3,6,2,1,0].  Flipping P
moves the left endpoint 3 rightward; it crosses 6 (in-neighbour:
deg(3) 1→0), then 2, 1, 0 (out-neighbours: deg(3) 0→1→2→3).  At the
crossing of the mate 0 the moved endpoint 3 reaches **degree 3** —
degree saturation, of the moved endpoint.  (It also crossed the
Q-endpoint 2, raising deg(2) to 2 — relevant to the two-port step.)

This is the typical mechanism: to cross the mate, x crosses several of
its out-neighbours, and capacity (start ≤ 1) leaves room for only one
added back-arc before saturation.

## 5. The Q-nesting subtlety (honest)

Lemma S2 assumes the slide crosses no Q-endpoint.  If a Q-endpoint lies
strictly between P's endpoints in σ, the minimal P-flip crosses it and
may flip Q's bit too, yielding (1, 1) ∈ EQ_2 — no contradiction.  The
two-port argument must therefore choose, among P and Q and the two
slide directions, a flip whose crossed set excludes the other port's
endpoints — or handle the fully-nested configuration separately.  The
census (§6) shows that in every n ≤ 7 capacity gadget *some* single-port
slide is blocked before completing, but the clean "choose an
un-nested port" step is **not yet proved in general** and is flagged as
the gap feeding the Two-Port Pigeonhole Lemma.

## 6. Census (exhaustive, n ≤ 7)

`scripts/single_port_slide.py` slides each port of every EQ_2 gadget
with capacity on 00 and classifies the first blocker.

| n | EQ_2 cap-on-00 gadgets | slides completing to a valid mixed LFO | blockers |
|---|---|---|---|
| 6 | 1 | **0** | cycle ×2 |
| 7 | 16 | **0** | degree ×16, degree+cycle ×12, cycle ×4 |

**No single-port slide ever completes to a valid mixed-vector LFO**
(0 of 34 slide attempts across n ≤ 7).  Every one is blocked by degree
saturation and/or cycle, and the degree-3 vertex is always a port
endpoint (the moved endpoint, per §4).  This is direct evidence for
Lemma C and for the blocker classification of Lemmas S2–S3.

## 7. What remains: the Two-Port Pigeonhole

Lemmas S1–S3 give: from a 00-capacity witness, each single-port flip is
blocked by a degree-3 (at the moved endpoint) or a cycle.  Lemma C
needs the **Two-Port Pigeonhole**: both P's flip and Q's flip are
blocked, and in a linear forest with all four port endpoints at degree
≤ 1, two independent blockers cannot coexist without already creating a
cycle, forcing a port endpoint to degree 2 (destroying capacity), or
admitting one flip after all.  The §4 observation — flipping P also
loaded a Q-endpoint (deg(2) → 2) — is the mechanism that should make
the two blockers compete.

**Status.**
  * Lemmas S1, S3: proved (local transposition accounting).
  * Lemma S2: proved as a dichotomy; the "(a) impossible" half is
    exactly Lemma C, verified n ≤ 7.
  * The Q-nesting step (§5) and the Two-Port Pigeonhole (§7) are the
    remaining gaps to a full proof of Lemma C.

## 8. Files and tests

| artefact | location |
|---|---|
| Slide + blocker census | `scripts/single_port_slide.py` |
| Tests | `tests/test_single_port_slide.py` |
| Lemma C context | `docs/fanout_barrier_synthesis.md`, `docs/fanout_barrier_theorem.md` |
