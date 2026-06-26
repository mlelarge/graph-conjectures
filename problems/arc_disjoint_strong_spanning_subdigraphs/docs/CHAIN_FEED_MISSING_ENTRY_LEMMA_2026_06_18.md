# D54: Chain-Feed Missing Entry Lemma skeleton

Date: 2026-06-18.

Status: proof skeleton, not promoted.

## Translation From D53

In the D42 host, the pending split vertices are:

    host 9,11,13

These correspond to the forced `I` vertices in the contracted D-bullet
chain:

    8,10,12

Their chain successors in the semicomplete side are:

    host 10,12,14  =  D-bullet 9,11,13

Those successors are the `K/W` chain vertices on the path

    v -> 8 -> 9 -> 10 -> 11 -> 12 -> 13 -> rho

D53's predicate

    u_chainK >= 1  and  u_or_heads_chainK >= 2

therefore says:

> Among the forced `I` vertices of the sealed chain, choose two pending
> split paths into their chain successors.  One path starts at `u`; the
> other starts at `u` or at a head.  The two targets are distinct chain
> successors.

The target-distinctness is automatic in D42: a local two-split choice
through a forced vertex uses its chain successor at most once, and the
successor of host `9` is `10`, of `11` is `12`, and of `13` is `14`.

## Cut-Repair Lemma

For the D42 split core, before adding the six pending split arcs, the
only directed cuts of out-size at most one are:

    Q1 = {2,3,4,5,7,8}        out=1
    Q0 = {2,3,4,5,6,7,8}      out=0
    Q2 = {2,3,4,5,6,7,8,10}   out=1

Here `Q0` is the main cage/head/v prefix cut; `Q1` is the same prefix
with one head removed; `Q2` is the same prefix after adding the first
chain successor.

The chain-feed predicate repairs them as follows:

1. `Q0` needs two new exits.  Every `u/head -> chainK` split arc exits
   `Q0`, so two such arcs repair it.
2. `Q1` needs one new exit.  A `u -> chainK` split arc always exits
   `Q1`, so the explicit `u` feed repairs it.
3. `Q2` needs one new exit.  Since two `u/head -> chainK` arcs target
   distinct chain successors, at least one target is beyond the first
   successor `10`, hence exits `Q2`.

All other cuts already have out-size at least two and cannot be damaged
by adding split arcs.  This is the exact finite certificate behind D53:
`56264` predicate-selected capped choices, `0` bad rows.

## Candidate Abstract Lemma

**Chain-Feed Missing Entry Lemma.**  In a non-degenerate sealed
multi-crossing chain kernel with hard gateway cage `C=C_u`, let

    v = z0, i1, w1, i2, w2, ..., it, wt, rho

be the forced chain segment of the shortest `v -> rho` path, where the
`i_j` are forced `I` vertices and the `w_j` are their `K/W` chain
successors.  Then there exist two indices `r != s` and two pending split
paths

    x_r -> i_r -> w_r
    x_s -> i_s -> w_s

with `{x_r,x_s} subseteq {u} union Heads`, at least one of
`x_r,x_s` equal to `u`.

For the D42 cut pattern, this implies `lambda(split core) >= 2`.
The intended general form should say the same for the corresponding
three prefix cuts of any sealed multi-crossing chain kernel.

## What Is Already Accounted For

The D42 witness has exactly the desired supply:

    through 9:  (2,10), (6,10), (7,10)
    through 11: (2,12), (6,12), (7,12)
    through 13: (2,14)

In D-bullet labels this is:

    through 8:  u/head -> 9
    through 10: u/head -> 11
    through 12: u      -> 13

So D42 is stronger than the lemma: `u` feeds every forced `I` vertex,
and heads feed the first two.

The old D46 B3+ Missing Entry Lemma asks for a rehang vertex with a
U-free entry into the cage and enough U-exits after enlargement.  The
D53 chain-feed route is different: it does not need root returns or a
one-shot B3+ rehang.  It needs pending split paths that repair the three
prefix cuts in the split semicomplete core.

## Real Gap

The unproved step is now precise:

> Why must an arbitrary non-degenerate sealed multi-crossing chain kernel
> have two forced `I` vertices whose incoming pending paths come from
> `{u} union Heads`, with at least one from `u`?

The likely sources are:

* the `AV_u` arcs in the original chain-kernel setup;
* the CL classification of forced tails as single-`D_O` path vertices;
* shortest-path no-shortcut constraints, which restrict alternative
  sources into the forced `I` vertices;
* `d^-(rho) >= 5` and `|R| >= 3`, which force multiple W entries and
  prevent the whole sealed chain from being fed only from roots/ladder.

None of these has yet been assembled into the required supply lemma.

## Next Technical Move

Build a symbolic "feed-source audit" for a chain kernel:

1. list every forced `I` vertex on the sealed path;
2. classify its possible in-neighbours by region: `u`, heads, roots,
   ladder, earlier chain, cage;
3. prove or refute that at least two forced vertices have feed sources
   in `{u} union Heads`, with at least one `u` source.

A counterexample to this audit would be a stronger generalized
chain-kernel obstruction than D47, because it would defeat the pending
decomposition route rather than just one-shot B3+.
