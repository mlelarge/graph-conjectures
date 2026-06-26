# D71: Head-Block Orientation Lemma

Date: 2026-06-19.

Artifact: `scripts/head_block_orientation_audit.py`.

## Purpose

D70 reduced the internal part of the local normal form to HBQ:
small in-cuts of `Q0` must be only actual singleton weak heads.  This
note proves HBQ from a concrete head-block orientation package matching
the sealed D42 block.

This is one level closer to the primitive sealed-block machinery than
D70.  The remaining task is to derive the orientation package itself
from C3 hooks, C7 cage packing, and the sealed shortest-path order.

## Head-Block Orientation Package

Write

    Q0 = {u} union R union Z,

where:

* `R` is the cage reserve `C_u \ {u}`;
* `Z=(z1,...,zk)` is the ordered escaped-head string ending at `v`;
* `|R| >= 2` and `k >= 2`.

Assume the following arcs are present.  Extra arcs are allowed.

**HBO-1, cage reserve expansion.**  For every nonempty `P subset R`,

    |A(P, ({u} union R) \ P)| >= 2.

In the intended application this is supplied by C7's three-packing
inside the cage, with the weaker lower bound two being enough here.

**HBO-2, root fan.**

    u -> z_i              for every i.

**HBO-3, hooks into the cage reserve.**

    z_i -> r              for every i and every r in R.

**HBO-4, ordered head string.**

    z_i -> z_j            whenever i < j.

These are monotone hypotheses: adding more arcs can only increase
`|A(Q0 \ T,T)|`, so it cannot create a new low complement.

## Lemma

Under HBO-1 through HBO-4, if

    empty != T proper subset Q0
    and |A(Q0 \ T,T)| <= 1,

then `T={z1}`.  Moreover `u -> z1` is present, so the actual entry count
of `{z1}` is at least one.  Hence `{z1}` is active exactly when its
actual entry count is one; if an extra reverse-head arc enters `z1`, the
weak-head prefix disappears.

Thus HBQ holds, with the only possible weak head equal to the first
vertex of the ordered head string.

## Proof

Let

    T_R = T cap R,
    T_Z = T cap Z,
    P   = R \ T.

We prove that every `T != {z1}` has at least two entries from `Q0 \ T`.

First suppose `u notin T` and `T_Z` is nonempty.  The root fan gives one
entry `u -> z` for each `z in T_Z`.  If `|T_Z| >= 2`, we are done.  If
`T_Z={z_j}` with `j>1`, then `z_1` lies outside `T` and HBO-4 supplies
`z_1 -> z_j`, giving a second entry.  If `T_Z={z1}` and `T != {z1}`,
then `T_R` is nonempty; since `k>=2`, `z2` lies outside `T`, and HBO-3
supplies an entry `z2 -> r` for any `r in T_R`.  Together with
`u -> z1`, this gives two entries.

Now suppose `u notin T` and `T_Z` is empty.  Since `T` is nonempty,
`T_R` is nonempty.  Every vertex of `Z` lies outside `T`, and every
`z in Z` sends arcs to every `r in T_R` by HBO-3.  Since `k>=2`, there
are at least two such entries.

It remains to consider `u in T`.  If `P=R\T` is nonempty, HBO-1 applied
to `P` gives at least two arcs from `P` to `({u} union R)\P`.  Because
`u in T` and `R\P = R cap T`, the heads of these arcs lie in `T`, so
they are two entries into `T`.

If `u in T` and `P` is empty, then all of `R` lies in `T`.  Since `T` is
proper, some `z_i` lies outside `T`.  By HBO-3 this `z_i` sends arcs to
every vertex of `R`; as `|R|>=2`, this gives at least two entries into
`T`.

All cases except `T={z1}` therefore have at least two entries.  For
`T={z1}`, HBO-2 supplies `u -> z1`, so the entry count is at least one
and is exactly one precisely when no extra arc enters `z1`.  QED.

## D42 Instantiation

In host labels for D42,

    u = 2,
    R = {3,4,5},
    Z = (6,7,8).

The audit verifies:

    root_fan = [(2,6),(2,7),(2,8)]
    head_order = [(6,7),(6,8),(7,8)]
    min_reserve_expansion = 3

Therefore the only possible low head complement is `{6}`.  In D42 and
the rho-entry variant its actual entry list is `[(2,6)]`, so the active
internal prefix is `Q0 \ {6}`.  In the D63 reverse-head variant the
extra arc `(7,6)` raises the entry count to two, so no internal low
prefix remains.

## Remaining Primitive Derivation

To finish the internal side from sealed-block/CL/DT, prove that every
nonterminal sealed multi-crossing block admits the HBO package:

1. `|R|>=2` and HBO-1 from C7 cage packing;
2. `u -> Z` from the escaped `AV_u` heads and the chosen gateway arc
   `a=(u,v)`;
3. `Z -> R` from C3 hooks for the K-side escaped heads and path start;
4. the ordered head string from semicompleteness plus shortest-path
   no-shortcut constraints.

After that derivation, HBQ is no longer open.  The remaining quotient
target is FSQ, the first-successor outside lemma.
