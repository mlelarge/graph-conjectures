# D56: Chain-feed deletion stress

Date: 2026-06-18.

Artifact:

    scripts/chain_feed_deletion_stress.py

Status: bounded refutation attempt; no counterkernel found.

## Goal

D55 found seven D42 feed arcs from `{u} union Heads` into the forced
`I` vertices:

    (1,8), (1,10), (1,12), (5,8), (6,8), (5,10), (6,10)

The direct way to refute the Chain-Feed Missing Entry Lemma is to delete
some of these arcs while preserving the sealed multi-crossing
chain-kernel gates.  If a deletion pattern preserved the gates but left
no two-feed pair, it would be a counterkernel candidate for the pending
decomposition route.

The stress tester enumerates all `2^7 = 128` deletion patterns.

## Gates

For each deletion pattern, the script checks:

* host remains simple `(1,0)`-near-split with the same `V1`;
* `lambda(D^bullet) >= 3`;
* `lambda(host) >= 3`;
* the cage remains `{1,2,3,4}`;
* the unique shortest path remains
  `7 -> 8 -> 9 -> 10 -> 11 -> 12 -> 13 -> rho`;
* forced `D_O` arcs remain exactly
  `(7,8),(8,9),(10,11),(12,13)`;
* `B*` remains sealed with out-cut
  `(8,9),(10,11),(12,13)`;
* the remaining feed-source table has or lacks a valid two-feed pair.

The script separately reports whether the original explicit hard pair
`(T0,U0)` remains available.  That is not part of the structural gate:
deleting feed arcs can destroy the original fixed pair without
destroying the chain-kernel geometry.

## Result

Summary:

    patterns=128
    structural_survivors=56
    weak_feed_structural_survivors=55
    counter_candidates=0
    no_good_patterns=25
    original_hard_pair_survivors=2

Every deletion pattern with no valid two-feed pair fails the structural
gate at `lambda(D^bullet) >= 3`:

    no_good_first_failed_gate_counts={'lambda_db>=3': 25}

The nearest structural survivors still have exactly one valid two-feed
pair.  Examples:

    deleted=(1,8),(1,10),(5,8),(6,8),(5,10)
    remaining feeds=(6,10,11),(1,12,13)

    deleted=(1,8),(1,10),(5,8),(6,8),(6,10)
    remaining feeds=(5,10,11),(1,12,13)

    deleted=(1,8),(5,8),(6,8),(5,10),(6,10)
    remaining feeds=(1,10,11),(1,12,13)

So the direct deletion family can reduce D42 to a single two-feed pair,
but cannot destroy the two-feed condition while preserving
3-arc-strongness of `D^bullet`.

## Failed No-Feed Patterns

The common obstruction is a prefix cut dropping below three.  For
example, deleting all three `u` feeds:

    deleted=(1,8),(1,10),(1,12)

gives

    lambda(D^bullet)=2
    min cut side={1,2,3,4,5,6,7,8,9,10}

Another no-feed attempt:

    deleted=(1,10),(1,12),(5,10),(6,10)

gives

    lambda(D^bullet)=1
    min cut side={1,2,3,4,5,6,7,8}

These are exactly the early prefix cuts that D53's two-feed predicate
repairs in the split core.

## Interpretation

D56 does not prove the abstract Chain-Feed Missing Entry Lemma, but it
rules out the simplest counterkernel: delete the D42 `{u,heads}` feed
arcs and rely on roots/ladder/earlier-chain feeds.  In this family,
removing enough feed arcs to kill all two-feed pairs also destroys
`lambda(D^bullet) >= 3`.

This suggests the symbolic proof should focus on 3-arc-strongness across
prefix cuts of the sealed chain.  The feed arcs are not just convenient
pending-decomposition choices; in D42 they are part of the cut slack that
keeps the chain kernel in class.

## Next Target

Try a repair-and-delete search rather than pure deletion:

* delete `{u,heads}` feeds;
* add substitute arcs from roots/ladder/earlier chain to restore
  `lambda(D^bullet) >= 3`;
* require the same sealed path, forced `D_O` arcs, and `B*` out-cut;
* test whether the two-feed condition can remain false.

If such a repaired kernel exists, it is the desired counterkernel.  If
not, the prefix-cut argument is likely promotable into the symbolic
Chain-Feed Missing Entry Lemma.
