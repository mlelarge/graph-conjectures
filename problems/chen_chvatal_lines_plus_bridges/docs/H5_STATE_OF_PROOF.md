# State of the H5 Proof

Date: 2026-07-01.

Target H5:

```text
G connected + pendant-free + diam(G) >= 4  ==>  ell(G) >= |G|.
```

Status: H5 is still open. The main structural split is sound, but the most
recent B1 localization route is refuted: `G3`, `DP-G3`, `DP-Hall`, and
`DP-SPLIT` are false. B1 itself is unrefuted.

The current proof has four fronts:

```text
A-easy     Lemma A easy branch: Gamma-Hall / D' >= excess.
A-deficit  Lemma A deficit branch: line-poor R amalgams.
B1         Lemma B 3-connected core: D2 >= n, equivalently collisions <= surplus.
B2         Lemma B 2-separable core: BIGTORSO crossing-line inheritance.
```

The common obstruction is now clear: local support counts, local Hall
certificates, and localized capacity budgets repeatedly either overcount or are
false. The remaining proof needs a global crossing-line counting principle.

## Global Split

Lemma A handles the non-2-connected case through a leaf-block 1-sum.

Lemma B handles the 2-connected core through a 2-cut/SPQR split.

For Lemma A, let `G` be a 1-sum of `R` and a non-bridge leaf block `B` at cut
vertex `u`, with `S=V(B)-{u}`. The following is proved:

```text
R and B are isometric in G.
Lines(R) inject into Lines(G).
Mixed lines factor as Sigma_s union T_p with no collapse.
ell(G) = Z + P.
Z >= ell(R).
ell(G) >= ell(R) + P.
```

The exact remaining inequality is:

```text
C2: P + Q >= |S| + max(0, |R|-ell(R)),   Q = Z - ell(R).
```

For Lemma B, the proved SPQR reduction is:

```text
ell(G) >= max(D2(G), BIGTORSO(G)).
```

Here `D2` is the number of distinct lines from distance-exactly-2 pairs, and
`BIGTORSO` is the maximum weighted-torso line count over 2-cuts. Lemma B follows
from:

```text
B1: 3-connected + diam>=4             ==> D2 >= n.
B2: 2-separable + diam>=4 + D2 < n    ==> BIGTORSO >= n.
```

This reduction is still sound. What failed was the attempted localized proof of
B1, not B1 itself.

## Proved Toolbox

The following tools survive the G3 refutation:

```text
Lemma A:
  1-sum/isometry scaffold.
  Lines(R) -> Lines(G) injection.
  Mixed-pair product factorization.
  T1link: P >= nSigma + Adist + D'.
  F3: every non-representative has a proper apex A_s != S.

Lemma B:
  L1: 2-connectivity gives BFS layer lower bounds and n >= 2*diam.
  L2: an edge line is V minus an equidistant set.
  ISO-MON: isometric induced subgraphs have no more lines than the ambient graph.
  Virtual-edge torso restriction: BIGTORSO <= ell(G).
  alpha': 3-connected + ecc(v)>=3 implies degG2(v)>=3.
  STAR / COLLCHAR / PERPAIR collision lemmas.
  CF: collided distance-2 line classes have strong forest-like shape in all
      verified 3-connected cases; useful as structure, not enough alone.
```

The important correction is that these tools do not justify localizing global
collision demand to `DEN=DE union N(DE)` or to one diameter pair.

## Front A-Easy: Gamma-Hall

In the easy branch `ell(R) >= |R|`, it is enough to prove `P >= |S|`.

The valid route is:

```text
T1link: P >= nSigma + Adist + D'       proved.
4':     nSigma + Adist + D' >= |S|     open.
```

The block-local inequality `(4')` has been reduced to one cardinality target.
Choose the shallowest representative in each `Sigma`-fiber. Over the
non-representatives, let:

```text
a      = number of distinct apex values,
excess = number of non-representatives - a.
```

There is a proved identity:

```text
nSigma + Adist + D' - |S| = (Adist-a) + (D'-excess).
```

F3 is proved and gives `Adist >= a`. Therefore A-easy reduces to:

```text
D' >= excess.
```

Live formulation: build the complement incidence graph `Gamma` from canonical
excess vertices to complement-generated `D'` lines `L(s,w)` with `w notin A_s`.
A left-saturating matching implies `D' >= excess`.

What is verified:

```text
Gamma Hall failures: 0 in marked census n<=9 and sampled n<=16.
Component deficit failures: 0.
Large trapped Hall-tight sets: none beyond size 2 after alternating closure.
```

What is false:

```text
line-degree <= 2 globally,
fixed complement choices,
private-line assignments,
apex-class disjointness.
```

So A-easy needs a genuine Gamma expansion proof, not a local witness rule.

## Front A-Deficit: Line-Poor R Amalgams

In the deficit branch `ell(R) < |R|`, C2 is exactly:

```text
ell(G) >= |G|.
```

The live inequality is the coupled statement:

```text
(P-|S|) + Q >= |R|-ell(R).
```

Neither piece works alone:

```text
Q >= deficit(R)          false.
P-|S| >= deficit(R)      false.
```

The attempted reduction through

```text
Q + nSigmaP*nT - nSigma >= deficit(R)
```

is invalid as a reduction. The standalone inequality is true in checked data,
but the bridge from that block quantity to `P-|S|` is false. This is the same
overcount trap as earlier pair/shell counting attempts.

The deficient `R` side is line-poor and close to `F_0` objects such as C4,
octahedral/K3,3-like pieces, and small sporadic cores. This branch needs a
global R-aware crossing-line argument: a line-poor side glued to a 2-connected
leaf block must create enough new global lines.

## Front B1: 3-Connected Core

B1 is:

```text
3-connected + diam>=4  ==> D2 >= n.
```

Let `G2` be the distance-2 graph. Then:

```text
D2 - n = surplus - collisions,
surplus   = |E(G2)| - n,
collisions = |E(G2)| - D2.
```

Thus B1 is exactly:

```text
collisions <= surplus.
```

Equivalently:

```text
2*collisions <= E(V) = 2*surplus.
```

This global statement is still unrefuted. Independent exhaustive census at
n=12 over ALL edge counts m=18..25 (412,255,684 graphs scanned; 5,601,520
three-connected diam>=4; `scripts/b1_n12_exhaustive_census.py`): **0 B1
failures**, min(D2-n)=+6 attained at m=22 and RISING with density (+7 at
m=23,24,25). (The earlier "exhaustive n=12 = 479,322 graphs" figure was
exhaustive only for m<=22; m>=26 remains unscanned, ~1.2B graphs per band, but
the rising margin makes a dense breach implausible.) The primary G3
counterexample has B1 margin +6. A fourth G3 failure exists at m=23
(``K?`DDOqREaRh``, margin -1), so the G3 refutation spans edge bands.

### The Refuted G3 Route

The following localization is false:

```text
G3: 2*collisions <= E(DE union N(DE)).
```

Primary counterexample:

```text
graph6: K?`DDOqREaQh
n=12, m=22, kappa=3, diam=4
unique diameter pair: (8,9)
collisions = 14
2*collisions = 28
DE = {8,9}
E(DE union N(DE)) = 24
G3 margin = -4
```

Consequently all stronger descendants are dead:

```text
G3-Hall1,
(D-CARD)+(S-RES),
(C-RES),
CF as a route to B1,
DP-G3,
DP-Hall,
DP-SPLIT,
LOW-P/HIGH-P.
```

The failure mode is structural. In dense diameter-4 pockets with `DE={p,q}`,
`DEN` can collapse to a small endpoint-neighbourhood. Collision demand is paid
by global distance-2 surplus spread across `V`, not by local excess on `DEN` or
one diameter pair.

The remaining B1 target is therefore global:

```text
prove collisions <= surplus directly.
```

The likely usable ingredients are the CF forest shape of collision classes and
the COLLCHAR anti-correlation: making many distance-2 pairs collapse to the same
line should force enough non-colliding distance-2 edges elsewhere. No localized
capacity budget should be used as a load-bearing target.

## Front B2: 2-Separable Core

B2 is:

```text
2-separable + diam>=4 + D2 < n  ==>  BIGTORSO >= n.
```

This front is still open and was not affected by the G3 refutation.

Known facts:

```text
BIGTORSO <= ell(G) is proved by weighted torso restriction.
max(D2, BIGTORSO) >= n is verified in the checked 2-connected census.
R2, the torso-intrinsic claim "some big torso has ell >= n", is false.
D2<n families are infinite, so no finite sporadic base case closes B2.
```

The problem is crossing-line inheritance. When `D2` is too small, lines crossing
a 2-cut must supply the missing count, but this cannot be seen from a single
torso alone.

This is the same type of separator problem as A-deficit.

## Dead Routes To Avoid

Do not revive these as proof targets:

```text
Explicit subset-of-lines charges:
  geodesic spine charge,
  pencil/bipencil shell charge,
  pair/shell cross-charge,
  bounded-distance short-line asymptotic charges.

Lemma A:
  signature split,
  R-mirror Hall,
  T2 reduction through (*),
  any block-only count without a verified bridge to P.

Lemma B B1:
  D-CARD,
  DEN-SAT / proper unit Hall,
  global total_demand <= 2|DEN|,
  pair-local DP-Hall,
  DP-SPLIT / DP-G3,
  any DEN-localized or diameter-pair-localized capacity bound.

Lemma B B2:
  torso-intrinsic ell(torso)>=n,
  finite-census closure of the D2<n family.
```

The G3 route is especially important: all implications in that tower were valid,
but they were rooted in a false statement. Future B1 work must attack the global
identity `collisions <= surplus` directly.

## Unifying Obstruction

All four fronts now point at the same missing principle:

```text
small local supports cannot account for global metric-line collapse.
```

Local witnesses fail because metric lines collapse across classes. Local Hall
targets fail because a row can be invisible to a chosen support. Local capacity
targets fail because the true surplus lives outside the localized set. Standalone
numeric inequalities fail when there is no bridge to actual distinct `G`-lines.

The proof needs a separator-aware, global crossing-line anti-concentration
principle for `F_0`-amalgams:

```text
if many candidate lines collapse locally,
then enough new global lines or enough global distance-2 surplus must appear
outside that local support.
```

This principle is visible in four forms:

```text
A-easy:    Gamma-Hall for D' lines.
A-deficit: line-poor R must be repaired by cross-amalgam lines.
B1:        collision classes must be paid by global distance-2 surplus.
B2:        2-cut thin sides must be repaired by crossing torso lines.
```

## Current H5 Closure Checklist

H5 would follow from these four statements:

```text
1. Gamma-Hall:
   canonical excess vertices in Lemma A easy branch have an SDR into
   complement-generated D' lines.

2. Lemma A deficit:
   every line-poor-R leaf-block amalgam satisfies ell(G) >= |G|.

3. B1 global collision principle:
   every 3-connected diam>=4 graph satisfies collisions <= surplus.

4. B2 crossing inheritance:
   every 2-separable diam>=4 graph with D2<n satisfies BIGTORSO>=n.
```

The most compact next mathematical target is (3), but it must be global. The
most contained target is (1). The two separator fronts, (2) and (4), likely need
the same crossing-line idea in different decompositions.

## Verification Discipline

The G3 failure exposed a process bug:

```text
random sampling missed rare 3-connected diam>=4 graphs at n=12.
exhaustive geng found the counterexamples.
```

Load-bearing claims on 3-connected diameter-at-least-4 graphs now require:

```text
exhaustive geng at n=12+ when feasible,
or a proof,
or explicit wording that the claim is only sampled evidence.
```

This applies especially to B1, where rare dense diameter-4 pockets are the
current source of false local principles.
