# D57: Chain-feed repair-and-delete search

Date: 2026-06-18.

Artifact:

    scripts/chain_feed_repair_search.py

Status: bounded counterkernel search; no hit through substitute budget 3.

## Goal

D56 showed that pure deletion of D42's `{u,heads}->forced-I` feed arcs
cannot destroy all valid two-feed pairs while preserving
`lambda(D^bullet) >= 3`.  D57 tries the next counterexample move:

1. delete enough feed arcs to kill every valid two-feed pair;
2. add substitute arcs into forced `I` vertices from non-`u/head`
   sources;
3. require the same structural chain-kernel gates.

Allowed substitute sources are all non-feed, non-forced vertices:

    2,3,4,7,9,11,13,14,15,16,17,18,19,20,21,22

Targets are the forced `I` vertices:

    8,10,12

The search rejects any repaired candidate that restores a `{u,heads}`
two-feed pair.

## Gates

The structural gates are the same as in D56:

* host remains simple `(1,0)`-near-split with the same `V1`;
* `lambda(D^bullet) >= 3`;
* `lambda(host) >= 3`;
* cage remains `{1,2,3,4}`;
* unique shortest path remains
  `7 -> 8 -> 9 -> 10 -> 11 -> 12 -> 13 -> rho`;
* forced `D_O` arcs remain exactly
  `(7,8),(8,9),(10,11),(12,13)`;
* `B*` remains sealed with out-cut
  `(8,9),(10,11),(12,13)`.

For speed, the script first checks whether the added arcs repair the
current low prefix cut, then applies the cheap cage/path/forced/seal
tests.  Full lambda checks are only needed if those filters pass.

## Budget 2

Run:

    uv run python problems/arc_disjoint_strong_spanning_subdigraphs/scripts/chain_feed_repair_search.py

Output summary:

    max_added=2
    no_good_deletions=25
    tried=19500
    hits=0
    mincut_skip=16166
    cheap_fail_counts={'cage':2352, 'unique_path':982}
    full_checks=0

No repaired no-good structural survivor exists with at most two
substitute arcs.

## Budget 3

Run:

    uv run python problems/arc_disjoint_strong_spanning_subdigraphs/scripts/chain_feed_repair_search.py --max-added 3

Output summary:

    max_added=3
    no_good_deletions=25
    tried=247975
    hits=0
    mincut_skip=184175
    cheap_fail_counts={'cage':49644, 'unique_path':14156}
    full_checks=0

Again, no repaired no-good structural survivor exists.

The important diagnostic is `full_checks=0`: every substitute set that
repairs the current low prefix cut either collapses the cage or creates
a shorter `v -> rho` path before any expensive connectivity check is
needed.

## Interpretation

D57 strengthens D56.  The obvious repaired counterkernel route is blocked
at very low budget:

* roots and ladder sources mostly cannot repair the relevant out-prefix
  cuts, because their tails are outside the deficient side;
* cage sources repair some cuts but collapse the cage by giving it a
  path to `rho` in `D-u`;
* earlier-chain sources repair cuts by jumping forward, but then create
  a shorter `v -> rho` path.

This is exactly the symbolic shape we want: maintaining the cage and the
unique sealed path appears to force the needed cut-repair arcs to come
from `u` or heads.

## Next Target

Convert the bounded-search obstruction into a prefix-cut lemma:

> In a sealed multi-crossing chain kernel, any non-`u/head` substitute
> that repairs the early deficient prefix cuts either destroys the cage
> or creates a forbidden shortcut on the unique `v -> rho` path.

If this lemma can be proved, D53's exact D42 predicate becomes a
candidate symbolic Prescribed Pending Missing Entry Lemma for the
non-degenerate chain-kernel case.
