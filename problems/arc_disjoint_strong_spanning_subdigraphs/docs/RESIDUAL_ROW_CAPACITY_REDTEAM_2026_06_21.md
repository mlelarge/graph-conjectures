# D86: Residual Row-Capacity Red-Team

Date: 2026-06-21.

Artifact: `scripts/residual_row_capacity_redteam.py`.

## Purpose

The requested next target was to prove the residual row-capacity lower
bounds from raw sealed-block/CL/DT:

    eta(B) >= 3
    zeta(A) >= 3

for every unlisted endpoint-reduced row.

D85 showed that exact D84 source-arc containment is too strong for AOC.
This note checks the stronger ER-4/RRSP target against the same
gate-preserving single-reversal neighbourhood.

## Result

The proof target is still not derivable from the currently formalized
raw gates alone.

Among the 27 single-reversal variants preserving the current structural
gates:

    residual row-capacity failures:        6
    failures with AOC still true:          4
    failures with AOC false:               2
    active attachment failures:            0
    SLE/top-fan failures:                  2

The two AOC-false failures are the already known `top_two_fan` failures.
The new information is the four AOC-true residual-capacity failures:

    (16,14) -> (14,16), missing (17,15),
    (16,15) -> (15,16), missing (17,16),
    (17,14) -> (14,17), missing (18,15),
    (17,15) -> (15,17), missing (18,16).

In host labels these delete one counted `L -> P` entry.  AOC survives
because the affected row still has value two, but ER-4 fails because the
row no longer has slack three.

For example, after reversing `(16,14)` in D-bullet labels, the residual
zeta row

    A = O' \ {15}

has only the two counted exits

    16 -> 15,    18 -> 15.

Thus `zeta(A)=2`, and `A` is not one of the endpoint-reduced named rows.

## Consequence

Do not claim that residual row-capacity follows from the currently
checked sealed-chain structural gates plus SLE.  It does not.

The raw CL/DT proof needs an explicit **root/spare co-support capacity
clause**:

> For each root/spare support vertex `p in P`, the co-singleton row
> `O' \ {p}` has at least three counted entries into `p`.

In the D42 labels this is witnessed by the two `L -> P` entries together
with the opposite internal `P` entry:

    for p=15: 16 -> 15, 17 -> 15, 18 -> 15,
    for p=16: 15 -> 16, 17 -> 16, 18 -> 16.

Equivalently, the CL/DT derivation must prove the capacity of the
root/spare pair, not merely AOC.  This is weaker than literal D84 source
containment but stronger than the current structural gates.

## Capacity-Critical Clauses

Deleting a single arc from the D83/D84 skeleton identifies which source
pieces are actually critical for ER-4 row capacity.

In the robust middle case the critical categories are:

    active_first_successor,
    semicomplete_active_returns,
    middle_to_top,
    robust_middle_support,
    top_two_fan,
    terminal_support_backfan into the first L support,
    H -> first-L support entries,
    L -> P entries,
    both internal P orientations.

In the weak middle case the critical categories are:

    semicomplete_active_returns,
    top_two_fan,
    terminal_support_backfan into the first L support,
    H -> first-L support entries,
    L -> P entries,
    both internal P orientations,
    the S -> H entries needed for the weak `{m,s,tau}` row.

The non-critical D84 arcs are still harmless and useful as a sufficient
skeleton, but they are not the right raw target.

## Revised Target

The next symbolic target is now sharper:

1. prove the root/spare co-support capacity clause from DT root/spare
   support plus CL/no-shortcut;
2. prove the first lower-support co-support capacity clause for the
   first `L` vertex;
3. prove the weak-middle top-pair capacity clause in the D74 case;
4. combine those capacity clauses with D82 active attachment and D79 SLE
   to recover ER-4.

Only after these capacity-critical clauses are available can the
residual row-capacity theorem be honestly promoted from the raw
sealed-block/CL/DT package.
