# H5 Lemma A (leaf-block reduction) — rigorous reduction to one inequality

Date: 2026-06-26 (multi-agent proof round + independent verification).

Target H5: `G connected + pendant-free + diam(G) >= 4  ==>  ell(G) >= |G|`.
Split: Lemma A handles the **non-2-connected** case; Lemma B the 2-connected core.

This note records what is now **rigorously proved** for Lemma A and isolates the
single remaining open inequality. All claims here are exact-oracle-verified with
**0 violations** over every leaf block of every non-2-connected pendant-free
diam>=4 graph at n=8 (77 graphs), n=9 (1117), n=10 (20190).
Reproduce: `scripts/lemma_a_reduction_gate.py 8 9 10`.

## Setup (the 1-sum / isometric amalgam)

G non-2-connected, pendant-free. Pendant-freeness forces every leaf block to be a
**non-bridge** block: a maximal 2-connected `B` with `|B| >= 3` and a unique cut
vertex `u`. Put `S = V(B)\{u}`, `R = G - S` (connected, `u in R`), `V = S ⊔ R`.
G is the **1-sum of R and B glued at the single vertex u**.

Identify each line `L` by its trace pair `(L∩S, L∩R)`.

## PROVED (verification-surviving; two independent adversarial skeptics: "sound")

**(M) Metric decomposition.** A shortest path between two vertices on the same
side cannot use the other side (the only gateway is the single vertex `u`, and a
simple path meets `u` once). Hence:
- `d_G = d_R` on R and `d_G = d_B` on B  (R, B isometric in G);
- `d_G(r,s) = d_R(r,u) + d_B(u,s)` for `r in R, s in S` (distances cross-add through u).

**(RR) Restriction / lifting.** For `a,b in R`: `line_G(a,b) ∩ R = line_R(a,b)`,
and `line_G(a,b) ∩ S ∈ {∅, S}`. So the map `line_R(a,b) ↦ line_G(a,b)` is a
well-defined **injection** `Lines(R) → Lines(G)` whose image lies in the
"Z-class" (S-trace trivial). Writing `Z = #{L : L∩S ∈ {∅,S}}`:  **`Z >= ell(R)`.**

**(CROSS) Cross-pair factorization — the historical collapse risk, which does NOT
occur.** For `s in S, p in R\{u}`: `line_G(s,p) = Σ_s ⊔ T_p`, where `Σ_s = line∩S`
depends only on `s` and `T_p = line∩R` depends only on `p`. *Proof idea:*
substitute `d_G(s,p) = d_B(s,u) + d_R(u,p)` into the three betweenness tests; the
S-side reduces to a B-condition free of `p`, the R-side to an R-condition free of
`s`, and the "cross" betweenness is killed by a **strict** triangle inequality
since `d_B(s,u) >= 1` and `d_R(u,p) >= 1`. The product `(Σ,T) ↦ Σ ⊔ T` with
`Σ ⊆ S, T ⊆ R` disjoint is injective ⇒ the mixed-line count is an honest product,
**no overcount, no collapse** (the failure mode that killed the spine/pencil/pair
charges does not recur). Oracle-clean over all 40,518 leaf blocks at n<=10.

**(THM) Partition + standalone lower bound.** With `P = #{L : ∅ ⊊ L∩S ⊊ S}`:
> `ell(G) = Z + P`  and  `Z >= ell(R)`  ⇒  **`ell(G) >= ell(R) + P`.**
This is a rigorous theorem (0 violations n<=10), independent of any property of R.

## The single remaining gap (C2)

Lemma A's target `ell(G) >= |S| + max(ell(R), |R|)` is **equivalent** to (set
`Q := Z - ell(R) >= 0`):
> **(C2)  `P + Q >= |S| + max(0, |R| - ell(R))`.**

- **Easy branch** (`ell(R) >= |R|`, no R-deficit): needs `P + Q >= |S|`. Verified
  even `P >= |S|` alone, with `min(P - |S|) = 1` at n=8,9,10 (margins 1/2/1).
- **Deficit branch** (`ell(R) < |R|` — LIVE: 39/77 at n=8, 352/1117 at n=9): needs
  the extra `|R| - ell(R)`. This is where the block's mixed/`S`-trace lines must
  repair R's line-deficit.

C2 holds with **min margin 1** over every leaf block at n=8,9,10
(`min_c2_margin = 1,2,1`); it is the *entire* remaining content of Lemma A.
Structure: a 2-D incidence count (S-trace variation ⟂ R-trace variation). The
intended closing argument is **Hall/SDR saturation of the bipartite incidence
between S and the proper-S-trace lines, using 2-connectivity of the block B**
(B supplies the SS/Su lines that break collisions). No closed form in
`(ell(B), |R|, deficit)` works — all refuted; e.g. the block can be a C4
(`ell(B)=1`), so the `+|S|` comes entirely from the interaction, not from B's
internal lines (canonical tight case `G?r@do`).

## Dead routes (do NOT revive — each refuted at n=10)

- **Signature split** `(A') nS>=|S|` ∧ `(C') excessS>=max(ell(R),|R|)`: strictly
  stronger than Lemma A and **(C') is FALSE at n=10** (`ICOcaQoR?`, `I?`@C`SI_`:
  margin −1 on every leaf block).
- **R-mirror Hall** `Q_rmirror := #{L : ∅ ⊊ L∩R ⊊ R} >= |R|`: **FALSE at n=10**
  (`I?AB?rCM?` block u=8: `Q_rmirror = 7 < |R| = 8`; several more). The asymmetry
  is structural — S is the 2-connected side and has a line supply R lacks.

## C2 round (2026-06-26, data-driven Hall attack) — finer reduction

C2 is **still open**, but it splits cleanly into a near-closed easy branch and a
hard deficit branch. All claims below independently re-verified, **0 violations**
n=8,9,10 (`scripts/c2_partial_gate.py`).

Define, for a leaf block, the **u-rays**: `Σ_s = line_G(s,p0) ∩ S` (u-ray of B at
s; independent of `p0∈R\{u}` by CROSS), `T_p = line_G(s0,p) ∩ R` (u-ray of R at p;
independent of `s0`). `nSigma = #distinct Σ_s`, `nSigmaP = #proper (≠S) Σ_s`,
`nT = #distinct T_p`.

**PROVED (0 violations):**
- **(LEVER)** `P ≥ nSigmaP · nT` — the proper-S-trace mixed lines `{Σ_s ⊔ T_p :
  Σ_s ≠ S}` are `nSigmaP·nT` distinct P-class lines (exact/tight, min(P−nSigmaP·nT)=0).
  *(The naive `P ≥ nSigma·nT` is FALSE — it miscounts Σ_s=S lines into the Z-class.)*
- **(n2)** `nSigma ≥ 2` and `nT ≥ 2` (from 2-connectivity of B; `deg_R(r) ≥ 2` for
  `r∈R\{u}`, peeling induction).

**EASY branch (`ell(R) ≥ |R|`), goal `P ≥ |S|`:**
- **PROVED whenever `nSigmaP·nT ≥ |S|`** — covers all but **4 / 4 / 44** leaf blocks
  at n=8,9,10. (E.g. if all u-rays of B are distinct, `nSigmaP ≥ |S|−1`, `nT ≥ 2`,
  so `P ≥ 2(|S|−1) ≥ |S|`.)
- **RESIDUAL** = the blocks with `nSigmaP·nT < |S|`; these **all have nT = 2** (R has
  only two u-rays — a "thin" R). There `P ≥ |S|` reduces to a **block-local, tight,
  unproved inequality (4')** `nSigma + Adist + D' ≥ |S|` about the 2-connected block
  B alone (D' = cross-class u-avoiding lines of B, which exist by 2-connectivity but
  were not lower-bounded). This is a clean self-contained open problem on 2-connected
  graphs with a marked vertex — independent of R.

**DEFICIT branch (`ell(R) < |R|`):** the synthesis's key finding —
> when `ell(R) < |R|`, `max(ell(R),|R|) = |R|`, so **C2 is *exactly* `ell(G) ≥ n`**
> (verified: `|S|+max(ell(R),|R|) = n`, 0 failures).

The true bound is the **coupled** `(P−|S|) + Q ≥ deficit` (= C2 itself, margin
1,2,1); neither `Q ≥ deficit` nor `P−|S| ≥ deficit` holds alone (both fail at
n=10). So **no single-family deficit-repair injection can exist** — provably, not a
patchable gap. The deficient R's are line-poor graphs near F_0 (C4 with deficit 3,
octahedron/K3,3 deficit 2, sporadic 5-vertex deficit 1). **The deficit branch is
morally a chunk of the Chen-Chvatal conjecture itself** (ell ≥ n on an amalgam with
a line-poor side). It does NOT reduce to the 2-connected core; it needs a global,
R-structure-aware argument.

**Net:** Lemma A only *half*-reduces the non-2-connected case. Easy branch → the
clean block-local lemma (4'). Deficit branch → ell ≥ n on line-poor-R amalgams, a
genuine frontier. This is a natural handback point for human mathematical input.

## T1/T2 follow-up attack (2026-06-26)

The handback targets were attacked again.  Neither is fully proved, but both are
now sharper than the C2-round state.

### T1: block-local inequality (4')

The target

```text
nSigma + Adist + D' >= |S|
```

survives in the stronger setting of **all 2-connected marked graphs** through 9
vertices, not only H5 leaf blocks.  More importantly, it has a stronger Hall/SDR
form:

> Choose one representative from each distinct `Sigma`-fiber.  Every remaining
> vertex of `S` can be matched injectively to either its own proper apex trace
> `A_s != S` or to a `D'` line containing it.

This matching statement implies `(4')`, since it gives
`Adist + D' >= |S| - nSigma`.

Verified:

```text
scripts/c2_t1_hall_gate.py 8 9 10             # H5 leaf blocks: 0 failures
scripts/c2_t1_hall_gate.py --all-marked 3..9  # all 2-connected marked graphs: 0 failures
```

This is now the cleanest T1 proof target.  The old pure-apex matching is false;
`D'` is genuinely needed.

### T2: deficit branch

The deficit branch also split further.  The already-proved product decomposition
and T1 would give

```text
P - |S| >= nSigmaP*nT - nSigma.
```

So it is enough to prove the ray/split numerical inequality

```text
Q + nSigmaP*nT - nSigma >= deficit(R).          (*)
```

This is strictly sharper than the previous opaque coupled inequality.  It holds
over every deficient block at `n<=10`:

```text
scripts/c2_t2_split_gate.py 8 9 10
```

Diagnostics also show the useful R-side bound

```text
deficit(R) <= Q + nT
```

with no violations at `n<=10`.  In the generic block-side case,
`nSigmaP*nT - nSigma >= nT`, so this R-side bound would close T2.  The only
observed exceptions have `nSigma=3`, `nSigmaP=2`, `nT=2`, and `deficit=1`, where
`Q + nSigmaP*nT - nSigma >= deficit` still holds tightly.

Thus T2 is no longer just "global line-poor amalgams"; the next symbolic target is
`(*)`, with the R-side lemma `deficit <= Q+nT` as the likely main ingredient.

## REVIEW CORRECTION (2026-06-26) — T1 needs a second lemma; the T2 reduction is INVALID

Independent adversarial review (`scripts/c2_bridge_review_gate.py`, exhaustive
n=8,9,10). The gates `c2_t1_hall_gate.py` / `c2_t2_split_gate.py` reproduce exactly,
and `(4')` and `(*)` are genuinely TRUE and tight. **But the gates verify standalone
block-quantity inequalities, NOT the bridge to `P`** (the count of proper-S-trace
G-lines that actually controls C2). Testing those bridges changes both conclusions.

**T1 (easy branch) — valid but INCOMPLETE.** `(4')` alone does NOT imply `P >= |S|`:
`(4')` is a statement about S-trace *subsets*, whereas `P` counts *G-lines*. The
missing connector is
> **(T1link)  `P >= nSigma + Adist + D'`** — verified TRUE, 0 failures, margin >=1.

Then `(4') + (T1link) ⟹ P >= |S|` is a valid route. T1link is a distinctness lemma
the writeup omits and neither gate checks; it must be stated and proved alongside
`(4')`. *(The form `P >= nSigmaP*nT + Adist + D'` asserted in the `c2_t2` docstring
is FALSE — 85 / 726 / 7563 failures at n=8/9/10, e.g. `G?` + backtick + `Drg`. The
correct bridge uses `nSigma`, not `nSigmaP*nT`.)*

**T2 (deficit branch) — the reduction to `(*)` is INVALID.** Its stated basis
"T1 + product give `P-|S| >= nSigmaP*nT - nSigma`" is FALSE: it fails at `G?r@do`
(`P-|S| = 2` but `nSigmaP*nT - nSigma = 4`) and at 7 / 13 blocks at n=9 / 10. Every
natural VALID reduction of the deficit branch was tested and **all fail** (each
first at `G?r@do`):
- `P >= nSigmaP*nT + Adist + D'` (the stated product bridge): 85 / 726 / 7563 fails;
- lever-valid `Q + nSigmaP*nT - |S| >= deficit`: 0 / 0 / 7 fails;
- T1link-valid `Q + nSigma + Adist + D' - |S| >= deficit`: 1 / 10 / 28 fails.

Only `(*)` itself is true (0 failures) — but precisely because it uses the most
generous `-nSigma` term, crediting more slack than any real lower bound on `P`
supplies. So **`(*)` is true but DISCONNECTED: proving it would NOT prove the
deficit branch.** This is the overcount / "empty counting engine" trap (cf.
graveyard G8 `sum_per_class`). **T2 is NOT reduced**; the deficit branch remains
exactly `ell(G) >= n` on line-poor-R amalgams.

LESSON: any C2 reduction must verify the **bridge** `P >= <block-quantity>`, not
just the block-quantity inequality in isolation. Gate: `scripts/c2_bridge_review_gate.py`.

## T1link proof (2026-06-26) — the easy-branch bridge is closed

The missing bridge from the review correction is now symbolic:

```text
(T1link)  P >= nSigma + Adist + D'.
```

Partition the `P`-class G-lines by their R-trace:

```text
P_mix    : empty != L∩R != R
P_upper  : L∩R = R
P_inside : L∩R = empty
```

These three classes are disjoint and all have nonempty proper S-trace.

**Inside lines give `D'`.** If `a,b∈B` and the B-line `L_B(a,b)` avoids `u` and
is not all of `S`, then no vertex of `R` lies on the G-line `L_G(a,b)`: any such
vertex would force one of the three betweenness conditions putting `u` on
`L_B(a,b)`. Hence `L_G(a,b)=L_B(a,b)⊂S`, and distinct `D'` traces give distinct
`P_inside` lines. So `P_inside >= D'` (in fact equality for this family).

**Upper lines give `Adist`.** For each `s∈S`, the line `L_G(u,s)` contains all of
`R`, since `u` lies between every `r∈R` and `s`. Its S-trace is exactly the apex
trace `A_s=L_B(u,s)-{u}`. Distinct proper apex traces therefore give distinct
`P_upper` lines, so `P_upper >= Adist`.

**Mixed lines give `nSigma`.** For `s∈S` and `p∈R\{u}`,

```text
L_G(s,p) = Sigma_s ⊔ T_p,
```

where `T_p` is the rooted R-ray from `u` through `p`
(`x∈T_p` iff `[u x p]` or `[u p x]` in `R`). Thus the lines with
`Sigma_s != S` and `T_p != R` give at least

```text
nSigmaP * nT_proper
```

distinct `P_mix` lines. Now `nSigmaP >= nSigma-1`, because at most one distinct
`Sigma`-trace is the full set `S`.

Also `nSigma >= 2`: since `B` is 2-connected, `u` has two distinct neighbours in
`B`, and their rooted rays exclude each other. Finally `nT_proper >= 2`: in the
connected rooted graph `R`, every vertex except possibly `u` has degree at least
2. Take a vertex `p` of maximum distance from `u`. If `p` has a same-layer
neighbour `q`, then `q∉T_p` and `p∉T_q`; otherwise `p` has two distinct
predecessors `q_1,q_2`, and `q_2∉T_{q_1}`, `q_1∉T_{q_2}`. In either case there
are two distinct proper R-rays. Therefore

```text
P_mix >= nSigmaP * nT_proper >= 2(nSigma-1) >= nSigma.
```

Combining the three disjoint R-trace classes gives `T1link`.

Verification after the proof target was isolated:

```text
scripts/c2_chain_verify.py 7 8 9 10   # all bridge subclaims, 0 failures
scripts/c2_tight.py 7 8 9             # tight-case helper, now using D'
```

So Lemma A's easy branch is now reduced to the single block-local Hall inequality
`(4') nSigma + Adist + D' >= |S|`. The deficit branch is unchanged and still not
reduced.

**Independent review-confirmation (2026-06-26, `scripts/c2_t1link_review_gate.py`).**
Re-verified every per-class sub-claim by a separate code path (Adist computed
directly as `L_G(u,s) ∩ S`, with `R ⊆ L_G(u,s)` checked explicitly; partition
exhaustiveness; `Pin = #{lines ⊊ S}`): **0 failures at n=7,8,9,10**, and the
G-side and B-side `Adist` agree everywhere. The aggregate `T1link` and the stronger
`P >= nSigmaP*nT_proper + Adist + D'` both hold (0 failures). One harmless nuance:
`P_mix >= nSigmaP*nT_proper` holds with *slack* (`P_mix` is strictly larger in
24/643/14845 blocks at n=8/9/10, never smaller) — fully consistent with the proof's
"give **at least** `nSigmaP*nT_proper` distinct P_mix lines". The proof is sound.

## (4') attacked (2026-06-26 workflow + independent review) — reduced to `D' >= excess`

A focused workflow (`scripts/wf_four_prime.js`, 16 agents) did NOT prove (4') but
**reduced it to a single cardinality inequality**, independently re-verified here
(`scripts/c2_four_prime_review_gate.py`, 0 failures: 2-connected marked graphs
n<=8, H5 leaf blocks n<=9).

Notation. Rep = the shallowest (min-depth) member of each Sigma-fiber; the
`|S| - nSigma` other members are NON-reps (depth >= 2). Over the non-reps, let
`a = #distinct apex values A_s` and `excess = (#non-reps) - a` (the total
apex-collision count). `Adist = #distinct proper apex values over ALL s`.

**The reduction (logic valid; pure-cardinality, no matching needed):**
- **Identity** (trivial algebra, 0 failures): `margin4 := nSigma + Adist + D' - |S|
  = (Adist - a) + (D' - excess)`.
- **F3** (every non-rep has a PROPER apex `A_s != S`) ⟹ `Adist >= a` ⟹ `Adist-a >= 0`.
- Hence **`F3 + (D' >= excess) ⟹ (4')`**. The three families `nSigma/Adist/D'` are
  counted in separate slots, so no Hall matching / containment / degree condition is
  needed (the per-member "private-D'-line" rule and the "degree condition" that
  earlier attempts chased are **red herrings** — refuted at `FCpd_` (n=7) and an n=14
  graph, but neither is required).

**Status of the pieces (updated after the follow-up attack below):**
- **F3 is now proved.** The workflow only verified it, but the metric cut proof below
  closes it.
- **`D' >= excess` — the whole remaining gap. VERIFIED only.** 0 failures over the
  full census n<=9, leaf blocks n<=10, and 364k sparse biconnected markings n=10..16;
  min slack 2 (n<=9), 3 (sparse n<=16). Never refuted. No closed-form lower bound on
  `D'` is known; the obstruction is GLOBAL (a flat fiber-chain of size k contributes
  k-2 to `excess` but 2-connectivity forces only ONE u-avoiding witness from that
  chain — the rest must come from elsewhere, so no chain-local/vertex-local count
  works). Proposed partial: `D' >= B1` with `B1 = Σ_fibers max(0, size-2)` (verified,
  tight, isolates the residual to cross-fiber apex merges — only 4/56984 blocks at
  n=8) — but `D' >= B1` is itself unproved.

**Net:** Lemma A's easy branch is now reduced to **`D' >= excess`**. Cleaner than the
Hall-matching framing, but still open. No counterexample to (4') was found.

## F3 proof (2026-06-26 follow-up) — closed

Let `B` be 2-connected with root `u`. Write `x <= y` when `x` lies on a shortest
`u-y` path, i.e. `d(u,x)+d(x,y)=d(u,y)`. For `s∈S`, put

```text
Sigma_s = {x∈S : x<=s or s<=x}
F_s     = {x∈S : [x u s]}
A_s     = Sigma_s ⊔ F_s.
```

We prove: if `s` is not the shallowest member of its `Sigma`-fiber, then `A_s != S`.

First, a non-representative has depth at least 2. If `d(u,s)=1` and some
`r≠s` has `Sigma_r=Sigma_s` with `d(u,r)<=d(u,s)`, then `d(u,r)=1` and
`r∈Sigma_s`, so two distinct neighbours of `u` would be comparable. That is
impossible because comparability would force `d(r,s)=0`.

Now suppose `A_s=S` and `k=d(u,s)>=2`. There is no edge between `Sigma_s` and
`F_s`. Indeed, let `a∈Sigma_s`, `b∈F_s`, and assume `ab` is an edge. Since
`b∈F_s`, `d(b,s)=d(b,u)+k`. If `a<=s`, then

```text
d(b,u)+k = d(b,s) <= 1+d(a,s) = 1+k-d(u,a),
```

so `d(b,u)+d(u,a)<=1`, impossible. If `s<=a`, then

```text
d(u,a)=k+d(a,s) <= d(u,b)+1
```

while the edge also gives

```text
d(u,b)+k = d(b,s) <= 1+d(a,s).
```

Combining yields `k<=1`, again impossible. Thus no such edge exists. Since
`A_s=S`, the sets `Sigma_s` and `F_s` partition `S`; if `F_s` were nonempty, then
removing `u` would disconnect `F_s` from the nonempty set `Sigma_s`, contradicting
2-connectivity. Hence `F_s=empty`, so `Sigma_s=S`.

Finally, a vertex with `Sigma_s=S` is alone in its fiber. If there were
`y≠s` with `s<=y`, then removing `s` would separate the vertices above `s` from
`u` and the vertices below `s`; no edge can cross that cut without shortening the
distance from `u` to a vertex above `s`. Thus 2-connectivity forces `s` to be
maximal in the rooted order. Consequently any other `r` with `Sigma_r=S` would be
comparable with `s`; either `s<=r` or `r<=s` contradicts maximality unless `r=s`.
So the full-Sigma fiber is a singleton, and such an `s` cannot be a non-rep.

This proves F3. The only remaining easy-branch inequality is therefore

```text
D' >= excess.
```

## New proof route for `D' >= excess`: excess-only Hall / complement lines

The raw count `D' >= excess` is global, but the follow-up probes show a more
structured target. For a duplicated apex class `A`, every `s` in that class and
every `w∈S\A` produce a u-avoiding line `L_B(s,w)`. The useful candidate family is

```text
C(A) = { L_B(s,w) : s in the duplicated apex class A, w∈S\A,
         u∉L_B(s,w), L_B(s,w) != S }.
```

Verified facts over the full marked census n<=9 and random larger 2-connected
blocks (`scripts/c2_excess_hall_gate.py`):

- each duplicated apex class has `|C(A)| >= |class|-1`;
- the union of all such complement-generated lines has size at least total
  `excess`;
- stronger: the canonical excess vertices have an SDR using only their own
  complement-generated lines `L_B(s,w)` with `w∉A_s`;
- equivalently, the reduced bipartite graph from canonical excess vertices to
  containing `D'` lines has an SDR in the census (`scripts/probe_collisions.py` reports
  `excess_saturate_fail=0` through n=9).

This is not a proof yet, but it is a sharper target than a blind lower bound on
`D'`: prove Hall only for the excess vertices and only using complement-generated
u-avoiding lines. The known false conditions remain false: a fixed shallowest/deepest
choice of `w` does not always work, and private lines are not guaranteed.

## Incidence-graph reduction of complement Hall (2026-06-26 continuation)

The Hall target above has now been reduced one more step. Build the bipartite
incidence graph `Gamma`:

```text
left  = canonical excess vertices s;
right = complement-generated D' lines L_B(s,w), w notin A_s;
s--L  iff L = L_B(s,w) for some w notin A_s.
```

Two additional structural conditions would be enough:

```text
(LD) every right vertex of Gamma has degree at most 2;
(CS) every connected component of Gamma has #right >= #left.
```

Indeed, under `(LD)` suppress each right vertex of degree 2 to an ordinary edge
between its two incident excess vertices, and each right vertex of degree 1 to a
private half-edge. In a connected component with at least as many line-edges as
vertices, every proper vertex subset has at least one boundary/private incident
line per induced connected piece, while the whole component is covered by `(CS)`.
Thus every subset of excess vertices has at least as many incident line-nodes as
vertices: Hall holds. This is a purely combinatorial lemma; no metric input is used
after `(LD)` and `(CS)`.

However, `(LD)` is **not universal**. It holds in the full marked census n<=9, but
larger random sparse blocks refute it (e.g. `J_Csa?gHGA_` at n=11 has a
complement line incident with four excess vertices). So `(LD)+(CS)` is a valid
small-census explanation, not the final proof route.

The strengthened gate now records the surviving expansion profile
(`scripts/c2_excess_hall_gate.py`):

- marked census n=7,8,9: `line_degree_fail=0`, `component_deficit=0`,
  `comp_hall_fail=0`;
- random n=10..16 (300 trials/order): `comp_hall_fail=0`, `component_deficit=0`,
  `large_tight_fail=0`; `line_degree_fail>0` at n=11,12,15, so line-degree is
  diagnostic only;
- true cross-excess overlaps do occur (`cross_overlap_lines=15` at n=8 and
  `132` at n=9), so disjointness of apex-class neighborhoods is false;
- all observed Hall-tight subsets are harmless: only singleton same-class tight
  sets and five two-vertex/two-class tight sets through n<=9; no subset of size
  >=3 is tight (`large_tight_fail=0`);
- the stronger "shared line equals every cross-pair line" rule is false
  (`pair_overlap_fail=5` at n=9, e.g. `H?b@bRS`), so do not use it.

**New live target:** use `(LD)+(CS)` only as the low-degree subcase, and in general
prove the observed expansion profile directly:

```text
for every X of canonical excess vertices with |X| >= 3,
    |N_Gamma(X)| > |X|,
with no deficiency for |X|=1,2.
```

This is still a Hall statement, but the obstruction has been narrowed: any failure
must be a large-subset expansion failure, not a class-local failure, component
deficit, fixed-choice issue, or pair-line/disjointness issue.

## Independent review (2026-06-26) — F3 proof CONFIRMED; Γ framing sound

- **F3 is now rigorously proved** (upgrade confirmed). Each step of the metric-cut
  proof was checked: (P1) non-reps have depth >= 2; (P2) when `A_s=S`, `k>=2` there
  is no `Sigma_s`–`F_s` edge (the two triangle-inequality cases are correct), so
  `S = Sigma_s ⊔ F_s` with no cross-edge forces `u` to be a cut vertex unless
  `F_s=∅`, giving `Sigma_s=S`; (P3) `Sigma_s=S` ⟹ `s` maximal in `<=_u` (else any
  edge from the "up" set to `{u}∪`down forces its lower end to be `s`, so removing
  `s` is a cut — contradiction), hence the `Sigma=S` fiber is a singleton. All
  internal lemmas verified 0 failures over marked n=6,7,8 (`scripts/c2_f3_proof_review_gate.py`).
- **The Γ reduction is logically VALID**: complement-generated lines `L_B(s,w)`
  (`w∉A_s`, u-avoiding, `!=S`) are a SUBSET of the `D'` lines, so any SDR of the
  excess vertices into them gives `D' >= excess`. The live claims reproduce: marked
  n=7,8,9 and random n<=16 give `comp_hall_fail = component_deficit = large_tight_fail = 0`.
- **The line-degree<=2 correction is correct** (`J_Csa?gHGA_`, u=2: max line-degree 4).
  Good catch — a "true in small census, false in random" lemma (the generic-census trap).
- **The large-tight cap is now repaired**: `c2_excess_hall_gate.py` no longer silently
  skips blocks with `excess > 14`. It uses the exact alternating-closure test below,
  with a brute-force cross-check when `excess <= 14`.
- Status unchanged otherwise: the remaining gap `D' >= excess` (now a Γ-expansion
  Hall statement) is VERIFIED on census n<=9 + sampled n<=16, NOT proved.

## Γ large-tight check repaired (2026-06-26 continuation)

Assume the complement graph `Gamma` has a left-saturating matching `M`. Direct each
left vertex `s` to a left vertex `t` when `s` is incident to the line matched to
`t`, and direct `s` to a sink when it is incident to an unmatched line. Then:

```text
X is Hall-tight, |N_Gamma(X)| = |X|,
iff X is nonempty, closed in this dependency digraph, and avoids the sink.
```

Thus a tight subset of size at least 3 exists iff the set of left vertices that
cannot reach the sink has size at least 3. This removes the old exponential cap.

Updated verification (`scripts/c2_excess_hall_gate.py`):

- marked n=7,8,9: `large_tight_skipped=0`, `large_tight_mismatch=0`,
  `large_tight_fail=0`, max trapped set size 2;
- random n=10..16 (300 trials/order): `large_tight_skipped=0`,
  `large_tight_mismatch=0`, `large_tight_fail=0`, max trapped set size 0.

So the proof target is cleaner: prove complement Hall, and once saturated prove
that the trapped dependency set has size at most 2.

**Independent review (2026-06-26):** confirmed. The alternating-closure is the
standard Dulmage–Mendelsohn characterization (given a left-saturating `M`, the
left vertices that cannot reach the sink are exactly the maximal Hall-tight set,
and every tight set is contained in it), so `∃ tight X, |X|>=3 ⟺ |non_reaching|>=3`.
I re-derived Γ from raw definitions and brute-forced the maximal tight set on every
excess block at marked n=8,9: **0 boolean mismatch** vs the gate, independent max
tight-set size 1 (n=8) / 2 (n=9) — matching the gate. The silent cap is genuinely
removed (the alternating test always runs; the brute-force is only a cross-check at
`excess<=14`). Note: this sharpens the *structural* target; the load-bearing
verification of `D' >= excess` still rests on `comp_hall_ok` (a saturating matching
exists), which is unchanged.

## Witness clarification (correct a prior conflation)

`G?r@do` (n=8) and `I?`bCaWTO` (n=10) are **NOT 2-connected** (cut vertices 7, 9)
— they are **Lemma A** graphs. `G?r@do` is the tightest *overall* H5 graph at n=8
(margin 1) precisely because it is non-2-connected. The genuine **2-connected**
extremal witnesses (Lemma B) are `G?otQg` (n=8), `HCQdarQ` (n=9), `ICOeeOsk_`
(n=10); these margin numbers (ell-n: 2,2,1 / proper-n: 1,1,0) are correct.
