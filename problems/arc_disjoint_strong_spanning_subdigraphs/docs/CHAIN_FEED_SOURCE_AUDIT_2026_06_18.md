# D55: Chain-feed source audit

Date: 2026-06-18.

Artifact:

    scripts/chain_feed_source_audit.py

Status: D42 witness audit; not a universal proof.

## Goal

D54 isolated the feed-source audit as the next symbolic task.  This
script makes the D42 source table explicit in D-bullet labels: for each
forced `I` vertex on the sealed chain, list the region of every
available in-neighbour and count the feed options from `{u} union Heads`.

Run from the repository root:

    uv run python problems/arc_disjoint_strong_spanning_subdigraphs/scripts/chain_feed_source_audit.py

## Result

The D42 sealed path is:

    7 -> 8 -> 9 -> 10 -> 11 -> 12 -> 13 -> rho

The forced `I` vertices are `8,10,12`; their chain successors are
`9,11,13`.

The source table is:

    i=8,  successor=9:
      u:     1
      heads: 5,6
      roots: 14,15
      v:     7

    i=10, successor=11:
      u:      1
      heads:  5,6
      roots:  14,15
      chainK: 9

    i=12, successor=13:
      u:      1
      roots:  14,15
      chainK: 11

Thus D42 has seven feed options from `{u} union Heads`:

    (1,8,9), (5,8,9), (6,8,9),
    (1,10,11), (5,10,11), (6,10,11),
    (1,12,13)

There are 11 valid two-feed pairs using distinct forced `I` vertices and
at least one `u` source.

## Interpretation

D42 is stronger than the D54 candidate lemma requires:

* every forced `I` vertex has a `u` feed;
* the first two forced `I` vertices also have head feeds;
* roots can feed all three, but root feeds are unnecessary for D53's
  `lambda(core)>=2` condition.

The audit points to the exact symbolic pressure point.  A proof of the
Chain-Feed Missing Entry Lemma should explain why non-degenerate sealed
multi-crossing kernels cannot have all forced `I` vertices fed only from
roots, ladder, or earlier chain vertices.  A counterexample should try
to preserve the three deficient prefix cuts while deleting the `u/head`
feed options listed above.

## Next Target

Generalize the audit predicates:

1. define the forced `I` vertices and their chain successors abstractly;
2. classify all possible in-neighbour regions under shortest-path and CL
   constraints;
3. prove that at least two forced vertices keep `{u} union Heads` feeds,
   with at least one `u` feed, or construct a sealed multi-crossing
   counterkernel without that supply.
