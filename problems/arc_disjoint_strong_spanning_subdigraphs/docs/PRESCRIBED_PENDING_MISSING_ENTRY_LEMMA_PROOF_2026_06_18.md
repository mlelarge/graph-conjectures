# D58: Prefix-cut proof of the Prescribed Pending Missing Entry Lemma

Date: 2026-06-18.

Status: superseded in part by D59.  Lemma 1 and Lemma 3 below remain
valid as conditional statements, but Lemma 2 overstates what follows
from 3-arc-strongness alone: the prefix-lift profile also allows
original-chain repairs such as `v -> i1 -> w1`, not only `{u,heads}`
feeds.  See `PREFIX_PROFILE_AUDIT_AND_D58_CORRECTION_2026_06_18.md`.

## Purpose

D53 gave an exact D42 cut certificate: one pending feed
`u -> chainK` plus a second pending feed from `u` or a head into a
distinct chain successor repairs the three deficient split-core cuts and
forces `lambda(core) >= 2`.

D57 showed computationally that non-`u/head` substitute arcs cannot
replace those feeds in D42 without either collapsing the cage or creating
a shortcut on the sealed chain.  This note records the symbolic version.

## Abstract Chain-Feed Setup

Work in a non-degenerate sealed multi-crossing chain kernel with hard
gateway cage `C=C_u`.  Let the sealed shortest path be

    P = v = z0, i1, w1, i2, w2, ..., it, wt, rho

where:

* each `i_j` is a forced `I` vertex;
* each `w_j` is the `K/W` chain successor of `i_j`;
* the chain arcs on `P` are the unique `D_O` arcs out of the forced
  tails;
* `P` is the unique shortest path from `v` to `rho` in `D-u`;
* vertices of `C \ {u}` have no path to `rho` in `D-u`;
* `Heads` is the head set adjacent to the cage side, as in the D42
  chain-kernel model.

For the split-off core obtained by deleting the forced `I` vertices
`i_j` and replacing chosen pending paths `x -> i_j -> w_j` by split arcs
`x -> w_j`, assume the D42 prefix-cut profile:

    Q- = C union (Heads \ {h0}) union {v}       has out-size 1,
    Q0 = C union Heads union {v}                has out-size 0,
    Q+ = Q0 union {w1}                          has out-size 1,

and every other directed cut in the unsplit core already has out-size at
least two.  In D42 these are exactly the three cuts

    {2,3,4,5,7,8}, {2,3,4,5,6,7,8}, {2,3,4,5,6,7,8,10}.

Also assume the corresponding prefix-lift condition:

* when the prefix cut is viewed back in `D^bullet`, every extra out-arc
  that is absent from the split core and can repair the prefix has the
  form `a -> i_r`, where `i_r` is a forced `I` vertex whose chain
  successor `w_r` lies outside the prefix;
* each forced `I` vertex has a local pending mate, so after the required
  feeds are chosen we can complete the usual two-split choice through
  every forced vertex.  These extra split arcs can only increase cut
  sizes.

This prefix profile is the explicit hypothesis that still has to be
derived from the general chain-kernel axioms in any final CRUX-A proof.

## Lemma 1: Prefix-Cut Substitute Obstruction

Let `Q_j` be one of the early prefix cuts above, and suppose an added
substitute arc `a -> i_r` into a forced `I` vertex repairs `Q_j`, while
not being a feed from `{u} union Heads`.  Then one of the sealed-kernel
gates fails:

1. If `a notin Q_j`, then `a -> i_r` does not leave `Q_j`, so it does
   not repair the out-cut.
2. If `a in C \ {u}`, then in `D-u` the vertex `a` reaches
   `i_r -> w_r -> ... -> rho`, contradicting the definition of the cage.
3. If `a` is an earlier chain vertex of `P`, then the path prefix from
   `v` to `a`, followed by `a -> i_r` and the suffix
   `i_r -> w_r -> ... -> rho`, is shorter than `P`, unless
   `a -> i_r` is the original next chain arc.  The original next chain
   arc is not a substitute.  Thus uniqueness/shortestness of `P` fails.
4. If `a in {u} union Heads`, then the arc is a permitted chain feed,
   contrary to the assumption that it is a non-feed substitute.

So a non-feed substitute cannot repair the early prefix cuts while
preserving both the cage and the unique sealed path.

### Proof

Only arcs with tail inside a cut and head outside it contribute to its
out-cut.  This gives case 1.

For case 2, `i_r` lies on the sealed path and its forced chain successor
continues to `rho`.  Thus `a -> i_r` gives a path from `a` to `rho` in
`D-u`, contradicting `a in C \ {u}`.

For case 3, let `a` occur before `i_r` on `P`.  If `a -> i_r` is not
the immediate chain arc of `P`, replacing the nonempty segment of `P`
from `a` to `i_r` by the single arc `a -> i_r` gives a strictly shorter
`v -> rho` path in `D-u`.  If it is the immediate chain arc, it is one of
the fixed chain arcs and is not an added substitute.  Hence every genuine
earlier-chain substitute creates a forbidden shortcut.

Case 4 is just the definition of a feed.  These cases exhaust tails able
to repair the early prefix cuts: roots, ladder, and later chain vertices
are outside the relevant prefix and fall under case 1.  QED.

## Lemma 2: Chain-Feed Existence From 3-Arc-Strongness

Under the prefix-cut profile, if `D^bullet` is 3-arc-strong, then there
exist two pending paths

    x_r -> i_r -> w_r,    x_s -> i_s -> w_s

with distinct targets `w_r != w_s`, with
`x_r,x_s in {u} union Heads`, and with at least one of `x_r,x_s` equal
to `u`.

### Proof

The unsplit split-core cut `Q0` has out-size zero.  In the original
3-arc-strong `D^bullet`, the corresponding prefix cut must have out-size
at least three.  Its sealed chain arcs account for the fixed exits; any
additional repair of the missing split-core exits must be through arcs
entering forced `I` vertices whose chain successors lie outside `Q0`, by
the prefix-lift condition.  By Lemma 1, every such repair arc that
preserves the cage and the unique sealed path must have tail in
`{u} union Heads`.  Since `Q0` needs two new exits in the split core,
there must be at least two such feeds into distinct chain successors.

The cut `Q-` has out-size one and excludes at least one head.  A head
feed from the omitted head does not leave `Q-`; a non-feed substitute is
forbidden by Lemma 1.  Therefore the missing repair of `Q-` must be a
feed from `u`.

The cut `Q+` has out-size one and already contains the first chain
successor `w1`.  Thus at least one of the two feeds must target a later
successor `w_j` with `j >= 2`; otherwise it would not leave `Q+`.
Because one local pending split through a fixed forced vertex uses its
chain successor at most once, the two feeds can be chosen through
distinct forced `I` vertices.  QED.

## Lemma 3: D53 Three-Cut Repair

If the two feeds of Lemma 2 are split off to arcs

    x_r -> w_r,    x_s -> w_s,

then the split semicomplete core is 2-arc-strong.

### Proof

By the prefix-cut profile, only `Q-`, `Q0`, and `Q+` have out-size below
two before the split arcs are added.

* `Q0` has out-size zero.  Both feed arcs leave `Q0`, so after adding
  them its out-size is at least two.
* `Q-` has out-size one.  Lemma 2 gives a `u` feed, and `u in Q-`, so
  this feed leaves `Q-`; its out-size becomes at least two.
* `Q+` has out-size one.  Lemma 2 gives a feed into a later chain
  successor beyond `w1`; its tail lies in `Q+` and its head lies outside
  `Q+`, so `Q+` is repaired.

Every other cut already had out-size at least two, and adding split arcs
cannot decrease an out-cut.  Therefore every directed cut of the split
core has out-size at least two, i.e. the split core has
`lambda >= 2`.  QED.

## Prescribed Pending Missing Entry Lemma

**Connectivity form.**  In any non-degenerate sealed multi-crossing chain
kernel satisfying the prefix-cut and prefix-lift profiles above, the
forced `I` vertices admit pending split paths whose split-off
semicomplete core is 2-arc-strong.  More specifically, one path starts
at `u`, a second path starts at `u` or a head, and the two paths enter
distinct chain successors.  Completing the remaining local two-split
choices through forced vertices cannot reduce the split-core
arc-connectivity.

This is now proved by Lemmas 1-3.

**Colour-prescribed completion form.**  Add the following external
pending-completion hypothesis:

> Every 2-arc-strong semicomplete split core arising from the above
> pending split-off admits a SAD respecting the prescribed opposite
> colours on the two split arcs through each forced `I` vertex.

Then the same chain kernel admits a prescribed pending decomposition:
colour the split core by that SAD, replace each prescribed split arc
`x -> w_j` by the two-step path `x -> i_j -> w_j` in the same colour,
and keep the opposite-colour pending mate through `i_j`.  The lifted
colour classes are spanning and strongly connected by the pending
completion hypothesis.

Thus the non-degenerate chain-kernel obstruction is removed, conditional
only on the semicomplete pending-completion theorem.

## What Is Proved And What Remains

Proved here:

* the prefix-cut substitute obstruction;
* existence of the two required feeds from 3-arc-strongness, assuming the
  D42 prefix-cut and prefix-lift profiles;
* D53's three-cut repair in symbolic form;
* the connectivity form of the Prescribed Pending Missing Entry Lemma.

Still not proved in this note:

* derivation of the prefix-cut and prefix-lift profiles from the most
  general chain-kernel axioms;
* the external colour-prescribed semicomplete pending-completion theorem.

So D58 is a real symbolic advance, but not yet a full CRUX-A closure.
The next target is to derive the prefix-cut/prefix-lift profiles
intrinsically from the sealed-block and CL/DT hypotheses, or to
cite/prove the exact semicomplete pending-completion theorem needed for
the colour lift.
