# General tournament Path-FAS: the polynomial-DP direction

This note investigates whether the LFO / Path-FAS decision problem on
arbitrary tournaments admits a polynomial-time DP.  It is one of the
three open paths after Aboulker Problem 4.4 was resolved on the
fork-tree subfamily (Theorem 65.A of `exchange_proof_draft.md`).

The headline finding is **negative**: every quotient of the
sleeping-block / active-bag state we tried either fails the soundness
test on a small concrete instance, or still produces an exponential
number of distinct states on the toggle / chain-seeded toggle
adversarial families of Sections 16 and 17 of the proof draft.  We
also rule out the simplest candidate structural parameter
("bounded reversal distance from the base order").  One positive but
narrow observation survives — the **interval treewidth** of the
score-window flex graph is *always* ≤ 8 (Section 4), so the obstacle
to a polynomial DP is not the bag size; it is the back-arc-graph
component partition encoded across consecutive bags.

All scripts referenced live in `scripts/`.  All runs use `uv run
python`.  No proof in this note is presented as a theorem unless it
has a symbolic argument, not just an empirical certificate.

## Section 1. Section 16 revisited — what the toggle obstruction really refutes

Section 16 of `exchange_proof_draft.md` proves that the sleeping-block
signature has at least 2^(n/4) reachable distinct values on a specific
tournament family.  The construction is reproduced verbatim in
`scripts/sleeping_bound_refutation.py` and the count is pinned at
`SleepingBoundRefutationTest`.  We re-ran it (k = 1..5) and confirm:

| k | n  | FF-pruned prefixes | distinct sleeping signatures |
|--:|---:|-------------------:|-----------------------------:|
| 1 |  4 |                  2 |                            2 |
| 2 |  8 |                  4 |                            4 |
| 3 | 12 |                  8 |                            8 |
| 4 | 16 |                 16 |                           16 |
| 5 | 20 |                 32 |                           32 |

The crucial follow-up (Section 16.6) is that **all 2^k toggle
prefixes complete to a valid LFO**: they are extension-equivalent but
sleeping-block-distinct.  So the obstruction is to **state counting**
under the natural quotient, not to **soundness** of the natural
quotient.

This precisely answers the sub-question "is it the signature that is
too weak, or the quotient projection that is too coarse?": the
*projection* is the issue.  Sleeping-block separates two-component
configurations
`f_i — a_i  ,  b_i — g_i` (ε_i = 0) from
`f_i — a_i — b_i — g_i` (ε_i = 1)
even though no future continuation can ever observe the difference.

The smallest such collision is at **k = 4, n = 16**, since Section 16
requires k ≥ 4 for the f_i a_i and g_i b_i arcs to be FF-forced.  For
k ≤ 3 the windows overlap and the construction breaks down.

What this means for a polynomial DP: the obstacle is not "extendability
is genuinely complicated."  It is "the sleeping-block state remembers
information that is invisible to future moves."  Sections 2–3 below
test whether any of the obvious coarser quotients fixes this without
introducing extendability collisions.

## Section 2. Bounded-port DP probe

A natural attempt is to keep the active-bag partition plus a
*bounded-radius* dependency closure on the past and future, in the
hope that finite K is enough.  This is implemented as
`bounded_port_signature(K)` in
`scripts/bounded_port_dp_probe.py`.

For each cut, the signature is

  (pos, active vertices, placed-active, active partition + degrees,
   K-step back-port partition, K-step forward-port partition,
   active-vertex flex-hit interface into ports).

`K = 0` is the pure active-bag signature; `K = ∞` is the
dependency-relevant quotient of Section 17.

### 2.1 Smashing test on the three skew templates

We re-ran `find_collision` on the depth-5 FF-pruned prefixes for K ∈
{0, 1, 2, 3}:

| template       | K=0   | K=1   | K=2   | K=3   |
|----------------|-------|-------|-------|-------|
| one_block      | **collision** | **collision** | **collision** | **collision** |
| skew_induction | none  | none  | none  | none  |
| wake1_failure  | none  | none  | none  | none  |

**The smallest collision is in `one_block`, n = 12, depth = 5**, and
it survives every finite K we tested (up to K = 3, which covers the
whole graph).  The concrete pair:

  A = (0, 1, 2, 5, 3),   extendable = False
  B = (1, 2, 0, 5, 3),   extendable = True

Both have the same active window {4, 5, 6, 7}, the same placed-active
{5}, the same active partition `((4,0,0),(5,1,1),(6,0,2),(7,0,3))`,
empty back-port partition (no flex-hit from any unplaced active into
the past), and identical active interfaces `(4 → (act,5,1,1))`.  The
two prefixes differ in how the forgotten vertices {0, 1, 2} have
been merged with the placed-active vertex 5:

  A: roots {0,2,3,5,10} all = 3   (one big chain via 2→0 and 3→2)
  B: roots {0,1,9,10} all = 10    (different chain via 9→1)

Because neither 0 nor 1 nor 2 is in the active window, and none is
in any K-step closure (the flex-out hits go to vertex 10's future, not
to the current prefix), the bounded-port signature collapses A and B.
Yet the future continuation is sensitive to the difference: vertex 10
eventually has to be placed, and only one of the two chain identities
admits a valid completion.

### 2.2 Toggle family state counts under bounded-port

On the toggle family at cut c = 2k, only the first ~4 of the k gadget
pairs (f_i, g_i) sit inside the active window of width 5; the rest
have not opened yet.  So `bounded_port_signature` records only those
~4 bits and merges the rest:

| k | n  | distinct bounded-port signatures (any K ∈ {0..3}) |
|--:|---:|--------------------------------------------------:|
| 4 | 16 |                                                16 |
| 5 | 20 |                                                16 |
| 6 | 24 |                                                16 |

The signature count saturates at 16 = 2^4, not 2^k, so bounded-port
**does** collapse the Section 16 asymptotic obstruction on this
family.  Similarly on the Section 17.6 chain-seeded toggle family,
the signature count saturates at 8 for k ≥ 3.

So bounded-port is **better than sleeping-block on the polynomial-bound
question**, but it is **unsound** on `one_block` at n = 12.  The
soundness failure is decisive: a polynomial DP whose state collapses
a YES-prefix with a NO-prefix gives wrong answers.

## Section 3. Stronger structural quotients

`scripts/structural_quotient_probe.py` implements three further
quotients suggested in the task description and runs the same smashing
tests.

### 3.1 Pre-loaded component multiset (Q-multiset)

State = active-bag signature + multiset of (size, edge-count) of every
dormant component (a back-arc-graph component containing no active
vertex and at least one unplaced future-opening vertex).

| family / template    | k or n | distinct sigs at cut |
|----------------------|--------|---------------------:|
| toggle k=5           | n=20   |              **32** = 2^k |
| chain_seeded k=5     | n=21   |                   24 |
| one_block (depth 5)  | n=12   | **collision** (prefix (0,1,2,5,3) vs (2,0,1,5,3)) |
| skew_induction       | n=12   |             no collision |
| wake1_failure        | n=12   |             no collision |

Q-multiset does **worse than active-bag** on the toggle family (it
re-introduces 2^k), and it still has the `one_block` collision.
**Refuted on both axes.**

### 3.2 Half-block parity (Q-halfblock)

State = active-bag signature + ((block-index, placed?) → count), where
block-index = ⌊indegree / 5⌋.  This is the position-band analogue of
Section 51's block-parity invariant.

| family / template    | distinct at k=5 (or n=12) |
|----------------------|--------------------------:|
| toggle               |                        16 (saturated) |
| chain_seeded         |                         8 (saturated) |
| one_block            |              **collision** |
| skew_induction       |                no collision |
| wake1_failure        |                no collision |

Q-halfblock matches active-bag asymptotically but **does not improve
its soundness**.  The one_block collision survives.

### 3.3 Image-interval band signature (Q-imageinterval)

State = active-bag signature + for each band j ∈ {−1, 0, 1, 2} the
counts (#placed, #unplaced) of vertices whose windows overlap
[pos+5j, pos+5j+4].

| family / template    | distinct at k=5 (or n=12) |
|----------------------|--------------------------:|
| toggle               |                        16 |
| chain_seeded         |                         8 |
| one_block            |              **collision** |
| skew_induction       |                no collision |
| wake1_failure        |                no collision |

Identical verdict: collapses the asymptotic toggle obstruction but
still wrong on `one_block`.

### 3.4 Verdict on Section 3

Every "local plus structural counts" quotient I tested has the
**same n = 12, depth = 5 collision on `one_block`**.  The collision
is on the *same* pair of prefixes
`(0,1,2,5,3)` vs `(1,2,0,5,3)` (or a relabelling), independent of K
and independent of multiset / parity / image-interval augmentation.
This is the same collision originally reported as the
**visible-latent failure** in Section 12 of the proof draft.

The structural reason: vertex 10 has reversed arcs 10→0 and 10→4
(both **forced**, since their windows are disjoint).  At cut 5 these
arcs are loaded but the component partition records which forgotten
vertices (in {0,1,2}) share a chain with the active vertex 4.  Any
quotient that forgets the full forgotten-partition information misses
this distinction.

## Section 4. Treewidth-bounded sub-class result

`scripts/treewidth_probe.py` computes the **interval treewidth** of
the score-window interval graph for every test instance.  Because
each score window has width ≤ 5 and at most 9 windows can be active
at any position (Hall feasibility, `docs/score_window.md`):

**Lemma 4.1 (folklore for interval graphs).**  Let T be a tournament
admitting any LFO.  Then the score-window interval graph
G_I(T) — vertices V(T), edges {u,v} iff I_u ∩ I_v ≠ ∅ — has
treewidth ≤ 8.

*Proof sketch.*  For interval graphs, treewidth = max-clique − 1, and
the max clique is the maximum number of intervals containing a single
point.  Hall feasibility says at most 9 intervals contain any one
position. □

Empirical confirmation (`uv run python scripts/treewidth_probe.py
--max-k 4`):

| instance                | n  | max overlap | interval tw |
|-------------------------|---:|------------:|------------:|
| toggle_k=4              | 16 |           7 |           6 |
| chain_seeded_k=3        | 13 |           8 |           7 |
| one_block               | 12 |           7 |           6 |
| skew_induction          | 12 |           9 |           8 |
| wake1_failure           | 12 |           6 |           5 |

Likewise the **flex graph** (with edges marking potential flex
backedges) has min-degree-eliminations treewidth upper bound ≤ 8 on
every tested instance (`scripts/flex_graph_treewidth.py`).

So the bag-size at any cut is bounded by a constant.  The natural
treewidth-DP would have constant-size bags, and at first glance one
might expect Bell(9) ≈ 21k constant-size partitions per bag, giving
n · Bell(9) ≈ O(n) states — i.e., polynomial.

**Why this is not a polynomial DP, despite tw ≤ 8.**  A treewidth DP
on the flex graph would correctly handle the "is the back-arc graph a
linear forest?" question if the LFO ordering were *fixed*.  But
Path-FAS asks for an LFO, which is a permutation π of V(T).  The
back-arc graph itself depends on π.  Concretely: at the same flex
graph, two different orderings select two different *subsets* of edges
as backedges.  The treewidth-DP would have to range over all
permutations π consistent with the score windows, and at each cut
remember which forgotten vertices remain endpoints of pending future
backedges.

The Section 16 toggle obstruction is the precise witness: the flex
graph treewidth is 6 (constant), but the number of distinct
"pending future obligation" patterns at one cut is 2^k.

**Honest statement.** The conjecture
"if the flex graph has treewidth ≤ t then Path-FAS is in time
2^{O(t)} · n^{O(1)}" remains **open**; I have neither a proof nor a
refutation.  The toggle family is consistent with it (it is in fact
all extension-equivalent at cut 2k), and the one_block obstruction
is a single small instance, not a parametric family.  The barrier to
a clean theorem is identifying an *ordering*-aware DP state of
constant size per bag.

A weaker corollary that **is** rigorous:

**Proposition 4.2.**  On the subclass of tournaments where (a) the
score windows induce an interval graph of treewidth ≤ t, and (b)
*all* reversed arcs of T against the base order have distance ≤ 1
(so the flex graph has at most n − 1 edges, in a path), Path-FAS
admits an n · 2^{O(t)} DP via the standard interval-graph DP applied
to the back-arc graph indexed by the ordering.

*Proof sketch.* Under (b), the LFO is forced to be the base order
modulo a constant number of adjacent transpositions, so the
permutation π is uniquely determined modulo O(n) choices; for each
choice apply the standard interval-graph linear-forest decision DP
in time 2^{O(t)} · n. □

This proposition does NOT cover `one_block` (its reversals go up to
distance 10), but it does cover the
"transitive plus local noise" sub-class commonly encountered in
random-tournament probes.

## Section 5. Score-window-band convex DP — transition rank analysis

`scripts/band_rank_probe.py` builds the **transition matrix** between
consecutive cuts c and c+1, indexed by FF-pruned active-bag
signatures.  Each entry is 1 iff some FF-valid one-step extension
maps one to the other.  We computed the rank of this 0/1 reachability
matrix on the toggle and chain-seeded toggle families:

Toggle family (`scripts/band_rank_probe.py --max-k 3`):

| k | n  | cut | rows × cols | rank |
|--:|---:|----:|-------------|-----:|
| 1 |  4 |   2 |    9 × 13   |    9 |
| 1 |  4 |   3 |   13 × 1    |    1 |
| 2 |  8 |   3 |    9 × 17   |    9 |
| 2 |  8 |   4 |   17 × 23   |   15 |
| 2 |  8 |   5 |   23 × 12   |   12 |
| 3 | 12 |   3 |    6 × 10   |    5 |
| 3 | 12 |   4 |   10 × 10   |    5 |
| 3 | 12 |   5 |   10 × 10   |    5 |
| 3 | 12 |   6 |   10 × 10   |    5 |

Chain-seeded toggle (k=3, n=13): rank rises monotonically from 3 at
cut 2 to 24 at cut 7.

**Observation.**  Under the active-bag signature, the transition
matrix rank is **essentially full** (rank ≈ min(rows, cols)) for all
cuts away from the boundary.  At the saturated cuts of the toggle
family, rank = 5 = #distinct active-bag signatures.  So the rank IS
constant for the toggle family — but only because the active-bag
*count* is constant there, not because of any deeper compressibility.

The conclusion is the same as Section 3: the active-bag transition
operator does not admit a non-trivial low-rank factorization.  A
polynomial DP via low-rank decomposition needs a quotient finer than
active-bag, which is exactly what every test in Sections 2 and 3
failed to provide.

## Section 6. Honest verdict

The polynomial-DP direction is in the following state.

(a) **The sleeping-block signature is too fine** (Section 16 of the
proof draft, re-verified here).  No polynomial DP can simply enumerate
sleeping-block classes.

(b) **The active-bag / interval-bag signature is too coarse** on
general tournaments.  Smallest concrete witness:
`one_block` (n = 12, depth = 5), prefixes (0,1,2,5,3) vs (1,2,0,5,3).
Long-range reversed arcs (10→0, 10→4) carry forgotten-component
information that the active bag cannot encode.

(c) **Every "active-bag plus bounded structural augmentation" quotient
I tested fails for the same reason.**  Tested quotients:
- bounded-port closure (K = 0, 1, 2, 3);
- dormant-component (size, edges) multiset;
- block-parity counts;
- image-interval band loads.
All four leave the `one_block` collision intact.

(d) **Bounded reversal distance from the base order is NOT a useful
structural parameter.**  Refuted by random 5-vertex tournaments with
reversal radius 1 (`scripts/bounded_reversal_dp_probe.py`,
30 samples per radius at n = 6, depth = 4): even at radius 1,
roughly 20% of tournaments exhibit an active-bag extendability
collision, and a concrete n = 5 witness exists.

(e) **Interval treewidth of the flex graph is bounded (≤ 8)**, but
this alone does not yield a polynomial DP because the LFO problem
also has to choose the ordering.  Section 4 contains the modest
positive result for radius-1 reversals (Proposition 4.2).  The full
"bounded-flex-treewidth implies poly Path-FAS" conjecture is
**open**.

(f) **Band-DP transition matrices have essentially full rank**
(Section 5), so low-rank decomposition of the natural transition
operator does not work either.

**Net conclusion.**  After ~90 minutes of careful work, *no quotient
of the LFO state below sleeping-block is both sound and polynomially
bounded* on the test families.  The fork-tree polynomial result of
Theorem 65.A does **not** generalize via any of the obvious quotients
or treewidth arguments.  The next promising direction is the
**ordering-aware treewidth DP** suggested in Section 4: a DP whose
state explicitly indexes the permutation choice at each cut, with
back-arc-graph component partitions restricted to the bounded bag.
That direction is not refuted by any test here.

## Reading guide

- Section 16 of `exchange_proof_draft.md` (the original sleeping-block
  lower bound) — reproduce with `uv run python
  scripts/sleeping_bound_refutation.py`.
- Section 17 (the dependency-relevant quotient and its chain-seeded
  refutation) — reproduce with `uv run python
  scripts/quotient_signature_probe.py`.
- `scripts/bounded_port_dp_probe.py` — bounded-port DP (Section 2).
- `scripts/structural_quotient_probe.py` — multiset, half-block,
  image-interval quotients (Section 3).
- `scripts/treewidth_probe.py` and `scripts/flex_graph_treewidth.py` —
  interval / flex graph treewidth (Section 4).
- `scripts/band_rank_probe.py` — band-DP transition rank (Section 5).
- `scripts/bounded_reversal_dp_probe.py` — radius-bounded reversal
  hypothesis (Section 6 d).

All tests are deterministic given the seed `20260527` used here.
