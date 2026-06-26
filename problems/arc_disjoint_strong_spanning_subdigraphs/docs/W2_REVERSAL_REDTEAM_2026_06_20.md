# D74: W2 Reversal Red-Team

Date: 2026-06-20.

Artifact: `scripts/w2_reversal_redteam.py`.

## Purpose

D73 reduced the outside-core certificate OC to the W-core two-support
lemma W2:

    lambda(C[O \ {w1}]) >= 2.

The requested target was to prove W2 from sealed-block/CL/DT primitives.
The red-team check shows that this statement is too strong for the
currently formalized primitive package.

## Construction

Start from the D42 chain kernel and reverse the D-bullet support arc

    11 -> 18

to

    18 -> 11.

In host/core labels this reverses the outside-core pair

    12 -> 19

to

    19 -> 12.

This is a semicomplete-preserving perturbation: it changes the
orientation of one pair inside the semicomplete side rather than deleting
the pair.

## Preserved Structure

The audit verifies that the reversed kernel still satisfies the checked
sealed-chain gates:

    structural_gates = ok,
    lambda(D-bullet) = lambda(host) = 3.

Thus the near-split host, cage, unique shortest sealed path, forced
`D_O` arcs, and sealed `B*` out-cut all survive.

The primitive head-block package used for HBO also survives:

    min_reserve_expansion = 3,
    root_fan = [(2,6),(2,7),(2,8)],
    head_sources = [6],
    low_head_complements = [({6}, (2,6))].

The original displayed hard gateway pair used `11 -> 18` in `U`, so that
particular `U` no longer realizes.  However the hard gateway itself
survives with the same `T` and the single reroute

    U(11) = 22.

The resulting pair has

    X = {1,2,3,4},
    U-exits from X = [(1,10)],
    free exits from X = [(1,5),(1,6),(1,8),(1,12)].

All free exits still have tail `u=1`, so this is the same hard-gateway
shape.

## W2 Failure

For D42 in host labels,

    w1 = 10,
    O' = O \ {w1}
       = {12,14,15,16,17,18,19,20,21,22,23}.

After the reversal,

    lambda(C[O']) = 1.

The exact low cut in `C[O']` is

    {12}, with the sole outgoing edge (12,23).

The lost second outside-core exit is exactly the reversed support edge
`12 -> 19`.  The edge `12 -> 10` still exists, but it goes to the first
successor `w1`, so it is not counted inside `C[O']`.

Therefore W2 is false under the current sealed-block/CL/DT primitive
package.

## Important Qualification

This does not refute FSQ itself.  In the full outside quotient `O`, the
only low outside cut remains

    {10}, with exit (10,23).

The weak core cut `{12}` is harmless for FSQ because it has two exits in
`O`:

    12 -> 23, and 12 -> 10.

So D72's W2-based OC certificate is sufficient but not necessary.  The
right replacement is an attachment-aware outside lemma: low cuts of
`O'` are allowed when the missing support is supplied by an exit to
`w1`, and cuts containing `w1` must also receive the first-successor
exit unless that exit lands inside the cut.

## Consequence

The next symbolic target should not be W2.  Replace it by an attached
outside-cut certificate proving FSQ directly:

* `w1` has the single allowed outside exit;
* every nonempty `B subseteq O'` has
  `d^+_{O'}(B) + d(B,{w1}) >= 2`;
* every nonempty proper `A subset O'` has
  `d^+_{O'}(A) + d({w1}, O' \ A) >= 2`.

Those two inequalities are exactly what the W2 proof was trying to buy
uniformly.  D74 shows they must be proved with the attachment terms
visible.
