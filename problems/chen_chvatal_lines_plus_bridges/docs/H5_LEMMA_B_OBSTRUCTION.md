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
