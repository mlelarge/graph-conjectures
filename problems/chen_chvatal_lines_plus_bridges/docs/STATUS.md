# Chen-Chvatal lines + bridges (Conjecture 2.2) — STATUS

Compact handback summary through D30 and the n=12 `m<=25` census.

## Headline

H5 remains open:

```text
G connected + pendant-free + diam(G) >= 4  ==>  ell(G) >= |G|.
```

The structural split into Lemma A (non-2-connected graphs) and Lemma B
(2-connected graphs) is sound. The attempted localized proof of Lemma B/B1 is
not sound: `G3`, `DP-G3`, `DP-Hall`, and `DP-SPLIT` are false. B1 itself remains
unrefuted.

The proof now has four fronts:

```text
A-easy     Gamma-Hall / D' >= excess in the Lemma A easy branch.
A-deficit  ell(G) >= |G| for line-poor-R leaf-block amalgams.
B1         D2 >= n for 3-connected diam>=4 graphs.
B2         BIGTORSO crossing-line inheritance for 2-separable graphs.
```

All four fronts require a global or separator-aware crossing-line principle;
local support, Hall, and localized-capacity arguments have repeatedly failed.

## Central question

Is the set of connected, pendant-free bad graphs
`ell(G) + br(G) < |G|` finite, and is it exactly the 12 graphs in `F_0` from
Figs. 1–3? The variant allowing pendant vertices is known false.

## Verified finite evidence

- Through order 10, the bad pendant-free graphs are exactly the 12 known members
  of `F_0`, at orders 4, 5, 6, and 8. Orders 7, 9, and 10 contribute none; the
  n=10 scan covered 9,808,209 pendant-free graphs.
- Every checked pendant-free graph with diameter at least 4 through n=10
  satisfies `ell(G) >= n`. This is finite evidence, not a proof.
- The 2-connected n=11 census over all checked bands `m<=22` (about 60 million
  graphs) found no Lemma B failure; the minimum `ell-n` was +5.
- For B1, the exhaustive n=12 census over min-degree-3, 2-connected graphs with
  `m=18..25` scanned 412,255,684 graphs, including 5,601,520 three-connected
  diameter-at-least-4 graphs. It found no B1 failure. The minimum `D2-n` was +6
  at m=22 and +7 at m=23,24,25. Bands `m>=26` remain unscanned.
- No completed full n=11 pendant-free sweep is recorded.

## Sound structural reductions

For Lemma A, write `G` as the 1-sum of `R` and a non-bridge leaf block `B` at
cut vertex `u`, and put `S=V(B)-{u}`. The following scaffold is proved:

```text
R and B are isometric in G.
Lines(R) inject into Lines(G).
Mixed lines factor with no collapse.
ell(G) = Z + P, with Z >= ell(R).
ell(G) >= ell(R) + P.
```

The exact remaining inequality is

```text
C2: P + Q >= |S| + max(0, |R|-ell(R)),   Q=Z-ell(R).
```

For Lemma B, the weighted-torso restriction proves

```text
ell(G) >= max(D2(G), BIGTORSO(G)).
```

Consequently Lemma B reduces to

```text
B1: 3-connected + diam>=4             ==> D2 >= n.
B2: 2-separable + diam>=4 + D2 < n    ==> BIGTORSO >= n.
```

This reduction remains valid. Only the attempted localization of B1 failed.

## Current closure checklist

1. **Gamma-Hall (A-easy).** T1link and F3 are proved. It remains to match the
   canonical excess vertices into complement-generated `D'` lines, equivalently
   prove `D' >= excess`.
2. **Lemma A deficit.** For `ell(R)<|R|`, C2 is exactly `ell(G)>=|G|` on the
   leaf-block amalgam. Neither `Q` nor `P-|S|` pays the deficit alone, and the
   attempted numerical reduction through `(*)` has a false bridge.
3. **B1 global collision bound.** If `G2` is the distance-2 graph, then B1 is
   equivalent to `collisions <= surplus`, or
   `2*collisions <= E(V)=2*surplus`. This must be proved globally, possibly using
   collision-class structure and COLLCHAR anti-correlation.
4. **B2 crossing inheritance.** For the infinite 2-separable `D2<n` family,
   prove that crossing lines across a 2-cut force `BIGTORSO>=n`. A
   torso-intrinsic bound is false.

## G3 localization route — refuted

The inequality

```text
G3: 2*collisions <= E(DE union N(DE))
```

is false. The primary counterexample is ``K?`DDOqREaQh``
(`n=12`, `m=22`, connectivity 3, diameter 4):

```text
collisions=14, so 2*collisions=28;
DE={8,9};
E(DE union N(DE))=24.
```

B1 still holds on this graph with margin `D2-n=+6`. The counterexample shows
that global distance-2 surplus cannot be localized to `DEN=DE union N(DE)` or to
a diameter-pair neighbourhood.

Therefore the following routes are dead as load-bearing B1 targets:

```text
G3 and G3-Hall1;
D-CARD / S-RES / C-RES and DEN-SAT;
DP-G3 and pair-local DP-Hall;
DP-SPLIT and LOW-P/HIGH-P;
any DEN-localized or diameter-pair-localized capacity bound.
```

The proved alpha-prime, STAR, COLLCHAR, PERPAIR, virtual-edge, ISO-MON, L1, and
L2 tools survive. Collision-class forest structure may still inform a global
B1 argument, but its route through G3 is dead.

## Latest decisions

- **D29 (2026-07-01):** exhaustive n=12 witnesses refuted G3, DP-G3, and
  DP-SPLIT, invalidating the full D16–D28 localization tower. B1 remains open and
  unrefuted.
- **D30 (2026-07-01):** independent review confirmed the four-front closure
  checklist and expanded the exhaustive n=12 B1 census through `m=25`: no B1
  failures, minimum `D2-n=+6`.

The process lesson is load-bearing: sampled evidence missed rare dense n=12
three-connected diameter-4 graphs. Future claims in this regime require an
exhaustive `geng` check at n=12+ when feasible, a proof, or explicit labeling as
sampled evidence.

## Human handback

- `needs_human`: the four closure fronts above remain open.
- `recommend_handback`: **yes**.
- Most compact next target: the genuinely global B1 inequality
  `collisions <= surplus`.
- Most contained next target: Gamma-Hall in the Lemma A easy branch.
- Do not launch another DEN-local or diameter-pair-local capacity workflow.
  The recurring obstacle is a global crossing-line anti-concentration principle;
  human mathematical input or a targeted literature search is now appropriate.

Detailed state and derivations are in `docs/H5_STATE_OF_PROOF.md`,
`docs/H5_LEMMA_A_REDUCTION.md`, `docs/H5_LEMMA_B_OBSTRUCTION.md`, and
`ledger.json`.
