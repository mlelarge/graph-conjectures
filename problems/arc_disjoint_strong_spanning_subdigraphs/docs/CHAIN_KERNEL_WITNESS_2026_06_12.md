# The chain kernel exists in-class: the X_P program is refuted (D42)

The D40 chain kernel is realizable.  Witness:
`scripts/chain_kernel_witness.py` (n=23 contraction, host (5,19) with
V1 = {p, q, p1, p3, p5}; all class gates asserted: simple near-split
host, lambda=3 host AND contraction, host SAD=SAT with ILP agreement,
explicit verified hard gateway pair at a=(u,v) with X=C_u).

## Construction (three structural moves)

P_v = v -> p1 -> p2 -> p3 -> p4 -> p5 -> p6 -> rho, unique shortest by a
DISTANCE-GRADED LADDER (R2-pairs at depths 2..5) supplying the W-entries
(9,22), (11,18) at exactly non-tie depths, plus the spare (p6,rho)
label.  Forced vertices: v and the three I-vertices p1, p3, p5 (unique
D_O-arc = chain arc).  The moves that made it consistent:

1. **Forced crossings are I-vertices** (p2/p4-style K-forced pairs are
   impossible: semicompleteness gives one of them a second D_O-arc).
2. **u sits in K** so its never-consumed AV_u arcs (u,p1),(u,p3),(u,p5)
   feed every B*-pocket to lambda >= 3 -- invisible to P_v, which is
   computed in D-u.
3. **The forced I-vertices carry X-side arcs** (p3,heads),(p5,heads):
   usable by C_u-pair trees (so the hard gateway pair EXISTS -- T0
   routes p3, p5 through the heads, freeing two crossings for U0) but
   NOT by the program's T_out (heads are not in O).  Without these the
   sealed cut starves U and no gateway exists at all.

## Verdict

B* = {u, cage, heads, v, p1, p3, p5}; delta+(B*) =
{(p1,p2),(p3,p4),(p5,p6)} = 3 = lambda, each arc its tail's unique
D_O-arc.  Every T of the X_P program consumes all three; boundary and
O->X arcs cannot cross (W-maximality by design); so B* is SEALED in
D-hat for EVERY T and EVERY prescription pair.  **The X_P program
(branch 2's absorption recipe: good pair at X = X_P) is FALSE.**

## L-exist survives: one-shot free-entry absorption

A good pair exists on the same witness at X = {cage, p3}: T1 routes p3
through the CAGE (absorbing it into the T-side subtree), and U1 then has
TWO exits ((u,p5),(p3,p4)).  Checked in the witness script.  The lesson
mirrors D38 one level up: there the rescue changed T within X_P; here
it changes X itself.

There is a stronger rescue using the ORIGINAL hard-pair U0.  Replace
only p5's T0-arc by p5->cage.  This absorbs the old T0-subtree
{p4,p5}, giving

    X' = cage u {p4,p5}

and U0 has the three strict exits

    (u,p3), (p4,ladder), (p5,p6).

Thus the witness is a one-shot instance of the free-entry extension of
the proved B3 absorption surgery; no seal/absorb/re-seal iteration is
needed here.

The literal recipe `X_P u {forced O-vertices}` is not the rescue:
it retains all of X_P, whereas both verified good sets are small
extensions of the cage.  Moreover DT, OUT, CT, and CL use specific
properties of X_P and cannot simply be transplanted unchanged.
The next formulation should grow the cage monotonically by an
absorbable T-subtree, not enlarge X_P.
