# H5 Lemma B (2-connected core) — toolbox, census, and the precise obstruction

Date: 2026-06-26.  Target:
`G 2-connected + pendant-free + diam>=4 ==> ell(G) >= |G|` (sharper: `proper(G) >= n`).

Status: **TRUE through n=11**, **not proved**. The full explicit subset-of-lines
charging axis was already barred (ledger G3/G5/G6/G8/G10); this round adds a clean
toolbox, a fresh census, a decisive reason the short-line route fails, and a first
SPQR probe.

## Census (this round; `scripts/two_connected_census.py`)

Genuinely 2-connected (`geng -C`), pendant-free, diam>=4:

| n  | graphs            | min(ell-n) | min(proper-n) | tight witness |
|----|-------------------|-----------|---------------|---------------|
| 8  | 48                | 2         | 1             | `G?otQg`, `GCQrV?` |
| 9  | 1944              | 2         | 1             | `HCQdarQ` |
| 10 | 96374             | 1         | 0             | `ICOeeOsk_` |
| 11 | all with m<=22 (~60M scanned) | **5** | **4** | `JCOeeOskcs_` |

KEY: the margin does **not** keep shrinking (1,1,0 → would-be threat); it **jumps
to +5/+4 at n=11**. The tight cases at n<=10 are **small sporadic graphs near F_0**.
`JCOeeOskcs_` = `ICOeeOsk_` + 1 vertex (K4→K5 fattening). Caveat: n=11 covered all
diam>=4 graphs with <=22 edges (where min-ell provably lives; the per-edge min-ell
is U-shaped and was bracketed). Denser diam>=4 graphs (m>=23) were not exhausted —
empirically irrelevant (dense ⇒ low diam / high ell) but not a proof.

## PROVED tools (adversarially verified "sound")

- **L1 (layer bound).** In a 2-connected graph, every interior BFS layer from a
  vertex has `>= 2` vertices (a singleton layer would be a cut vertex). Hence
  `n >= 2*diam`, i.e. `diam <= n/2`. (Discrete IVT / cut-vertex argument.)
- **L2 (edge / universal-line criterion).** For an edge `{a,b}`,
  `line(a,b) = V \ {z : d(a,z) = d(b,z)}`; in particular `line(a,b) = V` **iff no
  vertex is equidistant from a,b**. (Triangle inequality.)
- **ISO-MON.** If `H = G[U]` is an **isometric** induced subgraph then
  `ell(H) <= ell(G)` (single-valued restriction `L ↦ L∩U`). Reusable, rigorous.
- `ell(C_k) >= k` for `k >= 5`; cycles are never the obstruction (ell-n = Θ(n²)).

## The precise obstruction (why every attempt stalls)

All four independent attempts (sporadic+growth, ear-decomposition, two-far-
intervals, universal-line split) ultimately reduce `ell >= n` to a **short-line
functional** `D12(G) = #distinct lines from pairs at distance <= 2`. Three fatal
facts (verified):
1. `D12 <= ell` always — so `D12 >= n` is **strictly harder** than the target.
2. **Zero asymptotic slack (decisive).** Even cycles `C_{2m}` give `D12 - n = 1`
   for *every* n (C8..C40: D12 = 9,11,...,41), while `ell - n = Θ(n²)`
   (9,21,37,...,681). So an "asymptotic Ω(n) lower bound + finite census" route is
   **impossible via D12 / any short-line subset** — no `D12 >= (1+ε)n` can hold.
3. Still unproven: `D12 >= n` has only a Hall/König reformulation on the close-pair
   incidence graph, with **no lower bound on neighbourhood size** established.
The tight "thin tubes" (`n = 2D`, all interior layers size 2) realize their `>= n`
lines via **global lines spanning every BFS layer** — no layer-local or
bounded-index family captures `n` of them (the unifying lesson, again).

## Dead routes (do NOT revive)

- Open-ear induction with invariant `ell(G_i) >= |G_i|`: a **chord ear can strictly
  drop ell** with both graphs in scope (`G?qadg`: chord {0,7} sends ell 22→13).
- ISO-MON applied to isometric cycles: max ell over isometric cycles in the
  extremal witnesses is only 3 (they contain just isometric C3/C4) ≪ n.
- Any bounded-index / short-line subset-of-lines charge (zero slack or o(n)).

## SPQR probe (2026-06-26; `scripts/lemma_b_spqr_probe.py`)

This is not a proof, but it changes the shape of the Lemma B attack.

Exact marked census:

- `n=8`: 48 diam>=4 graphs, **0 three-connected**, 48 two-separable. Every best
  2-cut has component pattern `[3,3]`. The floor witness is `G?otQg`
  (`ell-n=2`, `proper-n=1`).
- `n=9`: 1944 diam>=4 graphs, **0 three-connected**, 1944 two-separable. The
  floor witness is `HCQdarQ` (`ell-n=2`, `proper-n=1`), with best 2-cut pattern
  `[4,3]`.

Known near-floor Lemma B witnesses are all 2-separable:

| witness | n | ell-n | proper-n | best 2-cut component sizes |
|---------|---|-------|----------|----------------------------|
| `G?otQg` | 8 | 2 | 1 | `[3,3]` |
| `HCQdarQ` | 9 | 2 | 1 | `[4,3]` |
| `ICOeeOsk_` | 10 | 1 | 0 | `[5,3]` |
| `JCOeeOskcs_` | 11 | 5 | 4 | `[6,3]` |

Random biconnected sampling at larger orders supports the same split. At n=10,11,12
no sampled diam>=4 graph was 3-connected. At n=13,14, three-connected samples first
appear, but with large surplus (`min ell-n` +57 at n=13 and +75 at n=14 in the
sample), while the sampled two-separable minima were still far above the exact
small sporadic floor.

Interpretation: the SPQR route should split Lemma B into two concrete claims.

1. **3-connected surplus lemma.** A 3-connected graph with diam>=4 has substantial
   line surplus, enough for `ell>=n` by a coarse global-line argument.
2. **2-cut inheritance lemma.** If a 2-connected diam>=4 graph is assembled across
   a 2-cut, then line counts inherit enough surplus from the sides, with the small
   sporadic 2-separable torsos handled separately.

The probe bars no route; it makes the 2-cut route more plausible and more specific.

## Viable framing + current routes

"Sporadic small-n + growth" is **structurally right** (min(ell-n) = 2,2,1,5; ell-n
grows): fix `N0 = 11` (exhaustive census n<=10 + n=11 m<=22), then it suffices to
prove `ell >= n` for `n >= N0` by **any structural Ω(n) lower bound on ell itself**
(not on D12/short-lines, provably dead). The routes now are:

1. **2-cut / SPQR decomposition** — now the leading route, sharpened to the
   3-connected surplus lemma plus the 2-cut inheritance lemma above.
2. **ISO-MON "essential core" reduction** — still untried; peel isometric structure to a core
   whose ell is countable.

Both are open. Also still open: extend the exhaustive n=11 census to all edge
counts to firm up `N0`.

## SPQR workflow result (2026-06-27) — reduction to `max(D2, BIGTORSO)`

A focused workflow (16 agents) + independent review (`scripts/lemma_b_reduction_gate.py`)
produced a **sound reduction** of Lemma B (still open). For every 2-connected
pendant-free diam>=4 `G`:
> **`ell(G) >= max( D2(G), BIGTORSO(G) )`**

- `D2(G)` = #distinct lines from distance-**exactly-2** pairs; `D2 <= ell` trivially.
- `BIGTORSO(G)` = max over every 2-cut `{a,b}` and side `Ci` of `ell(torso)`, where
  `torso = Ci ∪ {a,b}` + a virtual edge `ab` of weight `d_rest(a,b)`; `BIGTORSO <= ell`
  via the **restriction identity** `line_G(p,q) ∩ V_side = line_torso(p,q)` (the
  weighted virtual-edge metric is faithful — re-verified, 0 mismatches).

Since `{3-connected}` vs `{has a 2-cut}` is exhaustive, **Lemma B follows from two
complementary sub-lemmas**:
- **(B1)** 3-connected + diam>=4  ⟹  `D2 >= n`.
- **(B2)** 2-separable + diam>=4 + `D2 < n`  ⟹  some `BIGTORSO >= n`.

**Independently verified (0 failures, `scripts/lemma_b_reduction_gate.py`):** `D2<=ell`,
`BIGTORSO<=ell`, CLAIM A (every vertex has >=2 vertices at distance exactly 2; so the
distance-2 graph has min-degree >=2, `|E|>=n`), and the **complementarity
`max(D2,BIGTORSO) >= n`** over all 2-connected pendant-free diam>=4 graphs at n=8,9
exhaustive and all 9 `D2<n` graphs at n=10. `fail_both = 0` everywhere. No
counterexample to Lemma B or the virtual-edge lemma.

**KEY INSIGHT (circumvents the dead short-line route):** `D2` is a short-line
functional, and globally it has zero slack (it collapses on cycles/thin graphs — the
G3/G6/G8/G14 obstruction). But on **3-connected** graphs `D2` has *large* slack
(min `D2-n` = +11 at n=13). The SPQR split is exactly what rescues it: `D2` carries
the dense 3-connected case, `BIGTORSO` carries the thin 2-separable case, and they
are **complementary** (every `BIGTORSO<n` graph, e.g. `ICQSjR{~?` n=10 with
`BIGTORSO=9`, has `D2>=n`, e.g. `D2=14`; every `D2<n` graph has `BIGTORSO>=n`).

**Status of the two gaps (both OPEN, verified-not-proved):**
- **(B1)** — cleaner; large slack; likely true. Reduced to a global Hall/balance:
  the `(V, E(distance-2 graph))` incidence has a `V`-saturating matching (min-deg>=2),
  and `D2>=n` ⟺ that matching survives the collapse `e ↦ line(e)`, i.e.
  `#collisions <= |E(G2)|-n`. **Refuted shortcut:** "3-connectivity makes all
  distance-2 collisions local" is FALSE (diffuse/antipodal collisions, e.g.
  `J~aK]Qc[?[?` layers [1,3,3,3,1]). So (B1) is a genuine global collision-count
  statement, not a local one.
- **(B2)** — the **bottleneck**, and provably NOT a torso-intrinsic inequality:
  the clean step R2 ("some big torso has `ell>=n`") is **FALSE** (`ICQSjR{~?`: both
  big torsos `ell` 7,9 < 10), and any invariant `ell(torso)>=|torso|` discards the
  small side each step (`ell(G) >= |V_big| < n`). It must use **crossing/global
  lines**. Worse, the `D2<n` family is **infinite** (structured geng-prefix families
  `*Xme*`, `*dff*`, `*hVf*` = fixed 2-vertex thin part + growing dense core, all
  2-separable, diam=4, `D2 ∈ {n-1,n-2}`), so it CANNOT be cleared by a finite base
  `N0`. (B2) is the same flavor as Lemma A's deficit branch (line-poor pieces near
  F_0 + crossing lines).

**Net:** Lemma B is reduced to (B1)+(B2), both open. (B1) is a self-contained
distance-2-line Hall statement on 3-connected graphs; (B2) is a crossing-line
statement on an infinite 2-separable family — the genuine hard core.

## (B1) attacked (2026-06-28 workflow + review) — reduced to G3, with proved lemmas

A focused workflow (16 agents) + independent review (`scripts/b1_g3_gate.py`)
advanced (B1) (still open, no counterexample). Notation: `G2` = distance-2 graph,
`degG2(v) = #{u : d(v,u)=2}`, `collisions = |E(G2)| − D2`, `surplus = |E(G2)| − n
= ½ Σ_v (degG2(v)−2)`, `E(S) = Σ_{v∈S} (degG2(v)−2)`, `DE = {v : ecc(v)=diam}`.

**Exact identity:** `D2 − n = surplus − collisions`, so `(B1) ⟺ collisions ≤ surplus`
(circular by itself — where all prior rounds stopped).

**PROVED lemmas (re-verified, 0 oracle failures; each is 3-connectivity-essential):**
- **Lemma 0 (structure):** for `d(a,b)=2`, `line(a,b) = (N(a)∩N(b)) ∪ {x : |d(a,x)−d(b,x)|=2}`.
- **α' (Menger):** 3-connected + `ecc(v) ≥ 3` ⟹ `degG2(v) ≥ 3` (N2(v) separates N[v]
  from the far set; 3-conn ⇒ ≥3 separators). *Caveat:* FALSE for `ecc(v)=2` vertices
  (`JsaCEqe[?[?` has an ecc-2 vertex with degG2=2 — a dense-band witness invisible in
  the sparse census; a "minDegG2≥3 for all v" claim would be wrong).
- **STAR:** `line(a,p)=line(a,q)`, `d(a,p)=d(a,q)=2`, `p≠q` ⟹ `d(p,q)=4` and `a` between.
- **COLLCHAR:** under STAR, `N(a)∩N(p)` and `N(a)∩N(q)` are disjoint nonempty, and every
  `w∈N(a)∩N(p)` has `d(w,q)=3`. This is the **anti-correlation** mechanism: making
  endpoints metric-twins destroys collisions (verified: twin constructions ⇒ collisions=0).
- **PERPAIR:** for a diameter pair `{p,q}` with `k` STAR-centers,
  `E({p,q}∪N(p)∪N(q)) ≥ 2k+2`. Corollary: if all collisions are STAR centers on a
  SINGLE diameter pair, `surplus ≥ k+1 = collisions+1`, so `D2≥n` — the
  single-diameter-pair case is **closed**. (PERPAIR is FALSE on 2-separable graphs.)

**THE NEW CLEAN TARGET (verified 0 failures; strictly stronger than B1; 3-conn-essential):**
> **G3:  `2·collisions ≤ E(DE ∪ N(DE))`.**

Since `DE∪N(DE) ⊆ V` and `E(V) = 2·surplus`, **G3 ⟹ (B1)**. Independently verified:
0 failures on 3-connected diam≥4 (random n=11..14, min G3-margin ≥9; B1 slack +6
exhaustive n=11), and FALSE on every 2-separable D2<n witness (`HCQdarQ` −6,
`GCXmeW` −4, `G?qa`o` −8). G3 is the **recommended next target** — far more concrete
than "collisions ≤ surplus".

**Remaining gap + why it's global (negative results):** G3 holds, but (a) multiplicity-3
collisions and collisions exceeding `k` (≈10% of cases) aren't covered by PERPAIR
alone, and (b) PERPAIR must be combined across OVERLAPPING multi-pair supports. No
LOCAL/fractional certificate works: generous charging is provably ⟺ (B1) (circular);
lean charging (to interiors only) is false on the "blob" family (collisions share a
tiny interior, payment must route to antipodal endpoints of degG2=Θ(n)); G3's natural
decompositions (H1: `E(N(DE)\DE)≥2|DE|`, H2: `2coll ≤ Σ_DE degG2`) are both FALSE.
So proving G3 needs a **global** argument exploiting the COLLCHAR anti-correlation.
Gate: `scripts/b1_g3_gate.py`.

## G3 global-principle pass (2026-06-28) — collision forests + weighted support Hall

The requested global-argument / literature pass did **not** close G3, but it produced
a sharper target that is no longer a local charge.

### Literature filter

Generic rainbow-matching/Hall machinery is the wrong abstraction unless it uses the
metric support. The reason is structural, not just aesthetic:

- The edge-coloured graph viewpoint is: edges of `G2` are coloured by their metric
  line, and collisions are repeated colours.
- Standard large-rainbow-matching results usually need strong colour restrictions
  such as proper or low-degree colour classes, while our collided colour classes
  explicitly share endpoints.
- Recent rainbow-matching complexity results stay hard even for very small colour
  class shapes (matchings / short paths / small connected graphs). Thus "collision
  classes are small forests" is not enough by itself; the proof must use metric
  support and 3-connectivity.
- The useful analogy is the Aharoni-Haxell / topological-Hall family: replace local
  matching by a **subfamily expansion condition**. Here no topological theorem is
  needed yet; the right proposed condition is an ordinary weighted Hall inequality
  on collision supports.

Sources checked: arXiv:2511.04863 (topological Hall framing,
https://arxiv.org/abs/2511.04863), arXiv:2604.21025 (rainbow matching remains hard
for small colour-class shapes, https://arxiv.org/abs/2604.21025), and
arXiv:0906.0123 (Chen-Chvatal metric-line context, https://arxiv.org/abs/0906.0123).
This is a routing result, not an imported proof.

### New collision-forest probe

Added `scripts/b1_collision_structure_probe.py`. For each collided distance-2 line
`L`, build the **collision class graph** `F_L` whose edges are the distance-2 pairs
realizing `L`.

Observed over sampled 3-connected diam>=4 graphs:

- `F_L` is always a forest in all samples; no cyclic colour class appeared.
- `max |E(F_L)| = 3` in all samples. Existing `verify_collision_lemmas.py` also
  found no violation of `mult(L)<=3`, no star multiplicity >=3, and no equal common-
  neighbour-set collision in random n=18,24,30. The old shortcut
  "diffuse collisions are diameter" is FALSE.
- The size-3 classes have the stable shape `P2 ∪ K2`: one STAR pair plus one
  disjoint edge, with two diameter endpoints.

This suggests a clean symbolic subtarget:

> **CF:** In a 3-connected diam>=4 graph, every collided distance-2 line has a
> collision class forest `F_L` with `|E(F_L)|<=3`; size-3 classes are `P2 ∪ K2`
> of the observed type.

CF alone does **not** imply G3, but it is the right compression of the multiplicity
obstruction.

### New global target: expanded weighted support Hall

Let `DEN = DE ∪ N_G(DE)`, where `DE={v:ecc(v)=diam}`. For a collided line `L`, let
`B_L = V(F_L) ∪ L` and

> `S_L = (B_L ∪ N_G(B_L)) ∩ DEN`.

Give `L` demand `d(L)=2(|E(F_L)|-1)` and give each `v∈DEN` supply
`e(v)=degG2(v)-2`. The new target is:

> **G3-Hall1:** for every subfamily `X` of collided lines,
> `Σ_{v∈∪_{L∈X} S_L} e(v) ≥ Σ_{L∈X} d(L)`.

This immediately implies G3 by taking `X` to be all collided lines:
`2·collisions ≤ E(DEN)`.

Verification (`scripts/b1_collision_structure_probe.py`):

- **0 support_hall1 failures** on sampled 3-connected diam>=4 graphs at
  n=11,12,13,14,15,16,18,20,24,28,36,44 (sample sizes 60-120/order).
- The narrower support `S_L=(V(F_L)∪L)∩DEN` is FALSE; failures begin in random
  n=15/16 where a diffuse collision has empty direct DEN support. The one-neighbour
  expansion is load-bearing.
- G3-Hall1 is 3-connectivity-essential: it FAILS on all named 2-separable `D2<n`
  witnesses (`HCQdarQ`, `GCXmeW`, `G?qa`o`), matching the G3 guard.

**Current best proof route for (B1):**

1. Prove CF from Lemma 0 + STAR/COLLCHAR. This should be mostly metric algebra.
2. Prove G3-Hall1. This is the first non-circular global target: an arbitrary
   subfamily of collision forests must force enough `degG2-2` excess in its
   expanded DEN support. The 3-connectivity input should enter through Menger/fan
   paths from the collision forests to the diameter layer, not through local
   per-collision private witnesses.

## CF target attacked (2026-06-28) — classification gate and stress tests

Added `scripts/b1_cf_gate.py`, a focused gate for the first proof obligation in
the G3-Hall1 route. It verifies, for each collided distance-2 line `L`, the shape
of the collision class graph `F_L`.

CF is now a concrete forbidden-configuration target:

- no cycle in `F_L`;
- no class with `|E(F_L)| > 3`;
- no size-3 class except the observed `P2 ∪ K2` shape.

Verification:

- long 3-connected tube families (`prism`, `mobius`, `antiprism`) for
  `m=6,8,10,12,16,20,28,36`: `cf_fail=0`, diameters up to 19; these families have
  no collided distance-2 lines at all (`max_class=1`);
- exact `geng -C -d3` slice `n=13, m=20`: 989 three-connected diam-4 graphs,
  `cf_fail=0`, `max_class=3`, with all size-3 classes exactly `(3,5,2,(2,1),0)`;
- sparse random 3-connected samples at n=14,18,24,32: `cf_fail=0`, diameters up to
  8; only size-2 collision classes appeared in this sparse stress.
- five explicit earlier size-3 examples from the G3-Hall1 probe:
  `cf_fail=0`, `max_class=3`.

This still does **not** prove CF. The value is that CF is now reduced to forbidding
three small metric configurations in a same-line distance-2 colour class:
`cycle`, `P4`/longer path, and `K1,3`/larger branching. STAR already rules the
local geometry of adjacent edges (`p-a-q` geodesic of length 4); the missing proof
is to show these adjacent STAR constraints cannot be chained in a 3-connected
graph metric.

## Independent review (2026-06-28) — chain valid; CF is necessary but NOT the discriminator

- **The chain `B1 ⟸ G3 ⟸ G3-Hall1` is logically VALID** (confirmed). Taking `X` = all
  collided lines, `Σ_{∪S_L} e(v) ≥ 2·collisions`; since `e(v)=degG2(v)−2 ≥ 0` (CLAIM A)
  and `S_L ⊆ DEN`, this gives `E(DEN) ≥ 2·collisions = G3`. G3-Hall1 is 3-connectivity-
  essential (its X=all case is G3, which fails on the 2-separable `D2<n` witnesses).
- **CF reproduces** (geng `-C -d3` n=13 m=20: 989 three-connected diam-4 graphs,
  `cf_fail=0`, max_class=3, all size-3 = `(3,5,2,(2,1),0)`).
- **NUANCE (precision on the framing): CF is NOT 3-connectivity-essential.** Over the
  FULL 2-connected pendant-free diam>=4 census, CF holds on **all** graphs at n=8 (48)
  and n=9 (1944) — including the B1-**failing** witness `HCQdarQ` — and fails on only
  **34/96374 at n=10** (all 2-separable; no 3-connected graph exists at n<=12). So CF is
  a genuine, non-trivial property (it *can* fail), but it holds on B1-failing graphs, so
  **proving CF alone does not advance B1**. The 3-connectivity leverage lives in the
  G3-Hall1 *count* (how many collision forests there are and where they sit relative to
  DEN), not in CF's per-class shape. CF is a necessary local ingredient of the G3-Hall1
  proof, not the crux — the "cannot be chained in a 3-connected metric" step must be
  paired with the global count to discriminate B1-holds from B1-fails.

## G3-Hall1 dual form (2026-06-28) — capacitated Hall / anti-concentration

The right named principle for closing G3-Hall1 is **capacitated Hall**, i.e. the
standard max-flow/min-cut theorem applied to the bipartite graph

```text
collided line L  --  support vertices v in S_L ⊆ DEN,
left demand d(L)=2(|E(F_L)|-1),
right capacity e(v)=degG2(v)-2.
```

Thus G3-Hall1 is equivalent to the usual weighted expansion condition

```text
for every family X of collided lines:
    sum_{v in union_{L in X} S_L} e(v) >= sum_{L in X} d(L).
```

The min-cut dual gives a more proof-facing anti-concentration form:

```text
for every U ⊆ DEN:
    sum_{L : S_L ⊆ U} d(L) <= sum_{v in U} e(v).        (G3-Hall1-dual)
```

Interpretation: no low-excess subset of the diameter layer and its neighbours can
**trap** too much collided-line demand. This is the global count that separates the
3-connected case from the 2-separable B1-failing witnesses; CF only bounds the
shape of individual trapped collision forests.

Added a dual enumerator to `scripts/b1_collision_structure_probe.py`. It checks
`G3-Hall1-dual` directly for samples with `|DEN|<=24` and reports skips explicitly
instead of treating them as successes. The direct subfamily Hall check remains the
load-bearing verification; the dual check is a diagnostic for the intended proof.

Literature routing:

- Ordinary max-flow/min-cut is sufficient for the formal Hall dual; no topological
  Hall theorem is currently needed.
- The Aharoni-Haxell / topological-Hall language remains useful only as an analogy
  for "subfamily expansion", not as imported machinery.
- Rado/matroid Hall or gammoid language would become relevant only if the right
  side capacity `e(U)` is replaced by a rank/path-packing function. With the current
  target, that would be abstraction without leverage.

**Next proof target:** prove `G3-Hall1-dual` directly. A minimal counterexample would
be a subset `U⊆DEN` with excess deficit

```text
sum_{L : S_L ⊆ U} 2(|E(F_L)|-1) - sum_{v in U}(degG2(v)-2) > 0.
```

So the combinatorial argument should show that every trapped collision forest either
forces enough `G2`-excess inside `U`, or has three vertex-disjoint escape/fan paths
from its STAR/COLLCHAR endpoints to `DEN\U`, which create additional distance-2
neighbours counted by `e(U)`. This is the first non-circular formulation where a
global 3-connectivity/Menger argument has a specific cut to act on.

## G3-Hall1 split route (2026-06-28) — diffuse cardinal + conditional STAR reserve

Added `scripts/b1_hall_profile.py`, a focused profiler for the Hall family
`L -> S_L`. It separates collided lines into:

- **diffuse**: `F_L` has no STAR adjacent pair;
- **starry**: `F_L` contains at least one STAR adjacent pair. A size-3
  `P2 ∪ K2` class is starry because its `P2` component contributes one STAR unit.

Let `d(X)=Σ_{L∈X}2(|E(F_L)|-1)`, `U(X)=∪_{L∈X}S_L`, and
`E(U)=Σ_{v∈U}(degG2(v)-2)`.

The useful algebraic reduction is:

```text
If d(X) <= |U(X)|, then G3-Hall1 holds for X because every v in DEN has e(v)>=1.

Otherwise split X = X_diff ∪ X_star.  It is enough to prove:

  (D-CARD)    d(Y) <= |U(Y)| for every diffuse family Y.

  (S-RES)     for every cardinal-deficient X,
              E(U(X_star)) >= d(X_star) + |U(X_star)|.
```

Indeed, in the second case,

```text
E(U(X)) >= E(U(X_star)) + |U(X) \ U(X_star)|
        >= d(X_star) + |U(X_star)| + |U(X) \ U(X_star)|
         = d(X_star) + |U(X)|
        >= d(X_star) + d(X_diff),
```

where the last inequality uses `(D-CARD)` and `U(X_diff)⊆U(X)`.

This is a real sharpening of G3-Hall1: it separates the easy diffuse expansion
from the hard STAR reserve, and it explains why pure cardinal Hall sometimes fails
without losing the weighted inequality.

Verification from `scripts/b1_hall_profile.py`:

- dense random 3-connected diam>=4 samples at n=11,12,13,14,15,16,18,20
  (40-60/order): `diffuse_card_fail=0`, `conditional_split_fail=0`;
- sparse random 3-connected samples at n=14,18,24,32 (80/order):
  `diffuse_card_fail=0`, `conditional_split_fail=0`;
- exact `geng -C -d3` slice `n=13,m=20` (989 graphs):
  `diffuse_card_fail=0`, `conditional_split_fail=0`; only 1 graph has pure
  cardinal Hall failure, but its split certificates have large slack.

Important negative controls:

- Pure unit-capacity Hall is **false** in valid 3-connected graphs (first sampled
  failures at n=12). The `degG2-2` weights are genuinely needed.
- Unconditional STAR reserve is **false**: some STAR-only subfamilies have
  `E(U)<d(U)+|U|`, but only in graphs where the full family is already cardinal-safe.
  Therefore the live target is the conditional `(S-RES)` above, not unconditional
  STAR reserve.

**New proof target:** prove `(D-CARD)` and `(S-RES)`. `(D-CARD)` should be a pure
support-expansion statement for endpoint-disjoint collision forests. `(S-RES)` is
where PERPAIR and the STAR/COLLCHAR anti-correlation should enter: a cardinal-
deficient family has enough STAR mass concentrated near the diameter layer to force
one full support's worth of extra `degG2-3` reserve.

## G3-Hall1 STAR-component refinement (2026-06-28)

Added `scripts/b1_split_bundle_probe.py` to look inside the conditional `(S-RES)`
case. For a cardinal-deficient family `X`, build the support-overlap graph on
`X_star`: two starry rows are adjacent when their expanded supports `S_L` intersect.
For a component `C`, write

```text
U_C = union_{L in C} S_L,
d(C) = sum_{L in C} 2(|E(F_L)|-1),
extra(U_C) = sum_{v in U_C} (degG2(v)-3).
```

The supports of distinct components are disjoint. Therefore the following is a
strictly sharper sufficient condition for `(S-RES)`:

```text
(C-RES)  for every cardinal-deficient X and every STAR support-overlap
         component C of X_star,  extra(U_C) >= d(C).
```

Indeed, summing `(C-RES)` over components gives
`extra(U(X_star)) >= d(X_star)`, which is exactly
`E(U(X_star)) >= |U(X_star)| + d(X_star)`.

Verification:

- named cardinal-failure examples `KS_o\`JdQ_SkA`, `K\`Av?SGJWrIG`,
  `KQCnDGQXI\`^C`, `M\`]HCjA@SLoASiOD_`, `MWATK_GYiOI_BhPQ?`: `component_reserve_fail=0`;
- dense random n=11,12,13,14,15,16,18,20 (50/order): `component_reserve_fail=0`;
- sparse random n=14,18,24,32 (60/order): no cardinal-deficient families appeared;
- exact `geng -C -d3` slice `n=13,m=20` (989 diam-4 three-connected graphs):
  one cardinal-failure graph `L?ABA_goOhD_e_`, with `component_reserve_fail=0`
  and component margin +18.

Two useful negative controls:

- The stronger "one STAR component = one diameter pair" claim is **false**.
  The exact graph `L?ABA_goOhD_e_` has a cardinal-deficient family whose starry
  component has two STAR keys, `(7,11)` and `(8,9)`, sharing the same support.
- A uniform min-degree split is also **false**. `KQCnDGQXI\`^C` has a
  cardinal-deficient STAR component with `d=10`, `|U|=8`, and `min degG2(U)=4`;
  nevertheless `extra(U)=15`, so the reserve comes from the endpoint/common-support
  degree distribution, not from a blanket `min degG2>=5` bound.

**Updated proof target:** prove `(D-CARD)` and `(C-RES)`. `(C-RES)` is now the
load-bearing STAR lemma: every support-overlap component of a cardinal-deficient
STAR family must pay its own demand in `degG2-3` reserve. The proof should use the
diameter-pair endpoints that see all STAR centers, plus the extra `P2 ∪ K2` edge
in size-3 collision classes; key-wise reserve is tempting but can overcount when
two STAR keys share one support component.

## Independent review (2026-06-29) — (D-CARD)+(C-RES) split is VALID

Confirmed the implication chain `B1 ⟸ G3 ⟸ G3-Hall1 ⟸ (D-CARD)+(S-RES) ⟸ (D-CARD)+(C-RES)`:
- `(C-RES) ⟹ (S-RES)` is sound — the STAR support-overlap **components have disjoint
  supports by construction**, so `extra(U(X_star)) = Σ_C extra(U_C) ≥ Σ_C d(C) = d(X_star)`,
  i.e. `E(U(X_star)) ≥ |U(X_star)| + d(X_star)` since `extra(U)=E(U)−|U|`. (Each collided
  line lies in exactly one component, so demand is additive too.)
- `(C-RES)` reproduces: `component_reserve_fail = single_pair_fail = 0` on the named
  cardinal-failure graphs, the geng `-C -d3` n=13 m=20 slice, and dense samples
  n=11..20 — *including on the cardinal-deficient families that actually arise*
  (3 at n=12, 1 at n=13, 2 at n=14/15/16), where the bound has margin.
- The recorded false shortcuts are correct negative controls (pure unit-capacity Hall,
  unconditional STAR reserve, one-STAR-pair localization, uniform min-degG2 reserve all
  fail). So the live target is genuinely the **conditional** `(C-RES)`.

Net: a valid, well-scoped sharpening. The open obligations are now `(D-CARD)` (support
expansion for endpoint-disjoint diffuse forests) and `(C-RES)` (each STAR overlap
component pays its own demand via `Σ(degG2−3)`), both verified, both unproved.

## Correction / new obstruction attack (2026-06-29) -- D-CARD false, replace by overlap-reserve Hall

The `(D-CARD)+(C-RES)` implication chain above is still logically sound as a
**sufficient** condition, but it is no longer a viable proof route: `(D-CARD)` is
false in the intended 3-connected class.

New counterexample to `(D-CARD)`:

```text
graph6: MGdD@OC?S_GECE@g?
n=14, diam=5, 3-connected
five collided rows, all diffuse
demand = 10
common expanded support U = {1,3,4,5,8,10,12,13}
|U| = 8
cardinal deficit = demand-|U| = 2
extra(U) = sum_{v in U}(degG2(v)-3) = 6
weighted margin = |U| + extra(U) - demand = 4
```

So diffuse families can be cardinal-deficient. The missing payment is not STAR
reserve; it is ordinary `degG2-3` reserve already present in the same support.
This is exactly the global obstruction in miniature: the unit-support count fails,
but the weighted Hall count still has slack.

The corrected formulation is support-overlap component Hall. For any family `X`
of collided lines, put a graph on `X` by joining two rows when their supports
intersect. For a connected component `C`, write:

```text
U(C) = union_{L in C} S_L
d(C) = sum_{L in C} 2(|E(F_L)|-1)
extra(U) = sum_{v in U}(degG2(v)-3)
```

Distinct support-overlap components have disjoint supports, so demand and supply
are additive over the components. Therefore `G3-Hall1` is equivalent to the
connected-component reserve inequality:

```text
(OR-Hall)  for every connected support-overlap family C,
           sum_{v in U(C)}(degG2(v)-2) >= d(C).
```

Equivalently, only the cardinal-deficient components need proof:

```text
(OR-reserve)  if d(C) > |U(C)|, then extra(U(C)) >= d(C)-|U(C)|.
```

This strictly supersedes the false split. It keeps the valid unit-capacity idea
when `d(C)<=|U(C)|`, but it does not try to separate diffuse and starry rows.

Auxiliary probes:

- `scripts/b1_diffuse_overlap_probe.py` found the diffuse-only `(D-CARD)`
  counterexample above.
- `scripts/b1_overlap_reserve_probe.py` checks connected support-overlap families.
  It verifies `connected_target_fail=0` on the named counterexample, exact
  `geng -C -d3 n=13,m=20` (989 graphs), sparse samples n=14,18,24,32, and dense
  samples n=11,12,13,14,15,16,18,20.
- A tempting cycle-rank refinement is not load-bearing. The inequality
  `extra(U)>=cycle_rank` survived these checks, but `card_deficit<=cycle_rank`
  is false: `Ke_PAWkGq\y?` has a connected starry subfamily with cardinal deficit
  2, cycle rank 1, and extra 12. So the proof cannot route through cycle rank
  alone.

**Updated proof target:** prove `(OR-reserve)` directly. The likely metric lemma is:
when many collided distance-2 lines have overlapping expanded support in `DEN`,
3-connectivity forces the same support vertices to acquire enough additional
distance-2 neighbours to pay the overlap loss. This is the global anti-concentration
statement the previous split was trying to approximate.

## OR-reserve attacked (2026-06-29) -- DEN-saturation reduction, then correction

Added two proof-facing probes:

- `scripts/b1_or_reserve_profile.py` records the deficient connected
  support-overlap components, their `DEN` support, row kinds, support incidence,
  and where the `degG2-3` reserve is paid.
- `scripts/b1_or_saturation_gate.py` tests the sharper saturation target below,
  and keeps two negative controls explicit.

The new empirical target is:

```text
(DEN-SAT)  If C is a connected support-overlap family and d(C)>|U(C)|,
           then U(C)=DEN.
```

This is stronger than `(OR-reserve)` only on proper supports. If it holds, then
`(OR-reserve)` is no longer an independent obstruction beyond the original global
`G3` inequality:

```text
d(C) <= total_demand = 2*collisions
     <= E(DEN)                         by G3
     = |DEN| + sum_{v in DEN}(degG2(v)-3)
     = |U(C)| + extra(U(C))            by DEN-SAT.
```

So the B1 route can be reorganized as:

```text
proper-support unit Hall (DEN-SAT) + global G3  =>  OR-reserve
OR-reserve                                      =>  G3-Hall1
G3-Hall1                                       =>  G3  =>  B1.
```

Verification:

- `MGdD@OC?S_GECE@g?`: the diffuse `(D-CARD)` counterexample has
  `DEN=U`, `den_size=8`, `den_extra=6`, `total_demand=10`, `g3_margin=4`,
  and deficit `2`.
- `Ke_PAWkGq\y?`: proper deficient subfamilies exist, but every deficient
  connected family still has `U=DEN`; the full support has `den_extra=12`,
  `total_demand=12`, and `g3_margin=8`.
- exact `geng -C -d3 n=13,m=20`: 989 graphs, `support_not_den_fail=0`,
  `or_fail=0`, `min_proper_card_margin=1`, `max_deficit=5`.
- sparse samples n=14,18,24,32 and dense samples n=11,12,13,14,15,16,18,20:
  `support_not_den_fail=0`, `or_fail=0`. Dense n=15 shows
  `min_proper_card_margin=0`, so a strict positive proper-support margin is
  false, but no proper-support deficient component appears.

Negative controls:

- A private-row induction is false: proper-support components can have no row
  whose private support pays its own demand. In the exact `n=13,m=20` slice,
  `private_row_fail=10`; these are high-slack, non-deficient components, so they
  do not refute `DEN-SAT`, but they kill that proof shortcut.
- The earlier cycle-rank shortcut remains false (`card_deficit<=cycle_rank`
  fails), and `(D-CARD)` remains false.

**Initial B1 proof target, now refuted:** prove `DEN-SAT`, equivalently:

```text
For every connected support-overlap family C with U(C) != DEN,
    d(C) <= |U(C)|.
```

This would have made the proper Hall obstruction disappear. It is false.

### DEN-SAT refuted; proper weighted certificate survives

Added `scripts/b1_den_sat_profile.py`, which profiles proper-support components
and tests the replacement certificate.

Counterexamples to `DEN-SAT`:

```text
graph6: QsAWODG?QOGOGkGP@QOAGEBSCj?
n=18, 3-connected, diam>=4
chosen rows = [0,1,2], all diffuse
demand d = 6
proper support U = {0,3,5,12,16}, |U|=5
DEN = {0,3,5,7,9,12,14,16}
cardinal deficit = 1
extra(U) = 27, weighted margin = 26
```

and a sparse singleton-support witness:

```text
graph6: ]??S?AI?_?c?G?OD@GA?Cq?GD????g_??_?BPG_??DCQ????RO?KC?G?_AH?OO?G?B?@CB?D??
n=30, 3-connected, diam>=4
chosen rows = [0], diffuse
demand d = 2
proper support U = {27}, |U|=1
cardinal deficit = 1
extra(U)=5, weighted margin=4
```

So proper-support unit Hall is false. The weighted target still survives, and the
data isolate a simpler sufficient certificate for every proper deficient
component:

```text
(MIN4)  if U(C) != DEN and d(C)>|U(C)|, then degG2(v) >= 4 for all v in U(C).
(2CAP)  if U(C) != DEN and d(C)>|U(C)|, then d(C) <= 2|U(C)|.
```

Together they imply proper-support `(OR-reserve)` immediately:

```text
extra(U(C)) = sum_{v in U(C)}(degG2(v)-3) >= |U(C)|
            >= d(C)-|U(C)|.
```

Verification:

- named DEN-SAT failures above: `min4_fail=0`, `half_fail=0`,
  `min4_half_cert_fail=0`;
- exact `geng -C -d3 n=13,m=20`: 989 graphs, `den_sat_fail=0`,
  `min4_fail=0`, `half_fail=0`, `min4_half_cert_fail=0`, with proper margin
  floor 1;
- dense samples n=11,12,13,14,15,16,18,20,22,24: no certificate failure;
  tight proper margin 0 appears, and DEN-SAT failures appear in separate samples,
  but `(MIN4)+(2CAP)` continues to pay them;
- sparse samples n=18,24,30,36: no certificate failure; the n=30 singleton
  witness refutes DEN-SAT but satisfies `(MIN4)+(2CAP)`.

Important status correction: an all-`DEN` support component is necessarily the
whole row family, so paying it by `G3` is exactly the original global G3
inequality, not a proof of it. The Hall route therefore reduces to:

```text
proper components: prove (MIN4)+(2CAP)  =>  OR-reserve locally;
all-DEN component: prove global G3.
```

This is a real cleanup of the support-overlap layer, but it does not close B1.
The remaining load-bearing target is still global `G3`, with `(MIN4)+(2CAP)` as
the live proper-support sublemma.

## Proper `(MIN4)+(2CAP)` attacked; global G3 re-attacked (2026-06-29)

Added two focused profilers:

- `scripts/b1_min4_2cap_probe.py` profiles proper cardinal-deficient
  support-overlap components.
- `scripts/b1_g3_global_profile.py` profiles the remaining global `G3`
  inequality on `DEN`.

### Proper components

The proper-support certificate is not proved, but it sharpened to three smaller
targets.

For every proper deficient component seen so far:

```text
(PD-SHAPE)  every row is diffuse and every collision class has size 2
            (so each row has demand 2);

(PD-MATCH)  the bipartite graph row -- support vertex has a row-saturating
            matching;

(LOW3-SLACK) if a proper component contains a support vertex with degG2=3,
             then it is not cardinal-deficient.
```

These imply the live certificate:

- `(PD-SHAPE)+(PD-MATCH)` gives `d(C)=2|rows(C)| <= 2|U(C)|`, i.e. `(2CAP)`.
- `(LOW3-SLACK)` gives `(MIN4)` for every proper deficient component.
- Then `extra(U)>=|U|>=d(C)-|U|`, so proper `(OR-reserve)` follows.

Verification:

- named DEN-SAT failures:
  - `QsAWODG?QOGOGkGP@QOAGEBSCj?`: three diffuse size-2 rows, demand 6,
    support size 5, row matching exists, `min_degG2(U)=8`;
  - the sparse n=30 singleton witness:
    one diffuse size-2 row, demand 2, support size 1, row matching exists,
    `min_degG2(U)=8`.
- exact `geng -C -d3 n=13,m=20`: no proper deficient component; all proper
  components touching `degG2=3` have unit margin at least 4.
- dense samples n=11,12,13,14,15,16,18,20 and sparse samples n=18,24,30,36:
  no failures of `(PD-SHAPE)`, `(PD-MATCH)`, `(LOW3-SLACK)`, `(MIN4)`, or
  `(2CAP)` on proper deficient components.

This is progress, but still not a proof. The proper-support target is now:
prove `(PD-SHAPE)`, `(PD-MATCH)`, and `(LOW3-SLACK)` from the metric collision
lemmas and 3-connectivity.

### Global G3

For the all-`DEN` component, the problem is exactly global `G3`:

```text
total_demand = 2*collisions <= E(DEN) = sum_{v in DEN}(degG2(v)-2).
```

The global re-attack produced useful negative controls:

- A global `2|DEN|` cap is false. Example
  `SkF@@NdgGXkWgwO_gmkHx_lIxS^?_lo?O` has `total_demand=22`,
  `|DEN|=10`, so `total_demand>2|DEN|`; nevertheless `den_extra=75` and
  `g3_margin=63`.
- `extra(DEN)>=# {v in DEN : degG2(v)=3}` is false in low-order samples and is
  not the right reserve statement.

The low-margin global examples split into two regimes:

- **low-degree, low-demand:** e.g. `MGdD@OC?S_GECE@g?`, with
  `total_demand=10`, `|DEN|=8`, `den_extra=6`, `g3_margin=4`, and four
  `degG2=3` vertices;
- **high-degree, high-demand:** examples with `total_demand>2|DEN|`, but
  `min degG2(DEN)` is large and the reserve is overwhelming.

So the remaining global proof target is an anti-correlation statement, not a
plain cardinal cap: high collision demand must force high `degG2` reserve inside
`DEN`, while low-degree `DEN` vertices suppress demand.

## Anti-correlation attacked: diameter-pair localization (2026-06-30)

Added `scripts/b1_diameter_pair_g3_probe.py`.

The main new insight is that the global anti-correlation appears to localize to
**any fixed diameter pair**, not just to the full set `DEN`.

For a diameter pair `{p,q}`, put

```text
P_pq = N[p] union N[q],
E(U) = sum_{v in U}(degG2(v)-2).
```

The new scalar target is:

```text
(DP-G3)  for every diameter pair {p,q},
         2*collisions <= E(P_pq).
```

Since `P_pq subset DEN`, `(DP-G3)` immediately implies global `G3`.

The stronger Hall form also survives. For a collided line `L`, let

```text
S_L^pq = S_L cap P_pq,
```

where `S_L=(B_L union N(B_L)) cap DEN` is the existing expanded support. The
pair-local Hall target is:

```text
(DP-Hall) for every diameter pair {p,q} and every collided-line family X,
          sum_{v in union_{L in X} S_L^pq}(degG2(v)-2)
          >= sum_{L in X} 2(|E(F_L)|-1).
```

`(DP-Hall)` implies `(DP-G3)` by taking `X` to be all collided lines. This is a
strictly more proof-facing anti-correlation target: demand must expand into the
two endpoint-neighbourhoods of a single diameter pair.

Verification:

- named stress cases `MGdD@OC?S_GECE@g?`, `JGdSJ?eKSP?`,
  `SkF@@NdgGXkWgwO_gmkHx_lIxS^?_lo?O`, and
  `QsAWODG?QOGOGkGP@QOAGEBSCj?`: `dp_fail=0`,
  `pair_hall_fail=0`, minimum pair/Hall margin `3`;
- exact `geng -C -d3 n=13,m=20`: 989 graphs, `dp_fail=0`,
  `pair_hall_fail=0`, minimum pair/Hall margin `7`;
- dense samples n=11,12,13,14,15,16,18,20 (80/order):
  `dp_fail=0`, `pair_hall_fail=0`; minimum pair margins grow from `4` at n=11
  to `41` at n=20;
- sparse samples n=14,18,24,32 (80/order): `dp_fail=0`,
  `pair_hall_fail=0`, even with many diameter pairs and many off-geodesic
  vertices.

Negative control: the target is still genuinely 3-connectivity-sensitive. Direct
checks on the 2-separable `D2<n` witnesses give pair margins

```text
HCQdarQ : -7
GCXmeW  : -4
G?qa`o  : -8
```

and each has an explicit pair-local Hall cut failure.

So the global proof target is now:

```text
For a fixed diameter pair {p,q}, prove DP-Hall.
Equivalently, in the Hall dual, no U subset P_pq can trap more collided-line
demand than E(U).
```

This is a cleaner place for the Menger/fan argument: the cut is now inside the
two endpoint neighbourhoods of a single diameter pair, and low `degG2` vertices
can only remain low by suppressing the trapped collision rows that would need
their capacity.
