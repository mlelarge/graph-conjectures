# D85: Source-Clause Reversal Red-Team

Date: 2026-06-21.

Artifact: `scripts/source_clause_reversal_redteam.py`.

## Purpose

D84 decomposes the D83 residual ladder skeleton into source clauses
S0--S5.  That skeleton is sufficient for ER-4, hence for AOC and FSQ
after D79/D81/D82/D83.  The next proposed target was to prove every D84
source clause from the raw sealed-block/CL/DT/no-shortcut gates.

This note red-teams that target against the currently formalized raw
gates.  It enumerates every single D42 arc reversal that preserves the
checked structural gates, records which D84 source arcs disappear, and
then checks AOC directly.

## Result

There are 27 gate-preserving single reversals.  Among them:

    missing D84 source arc, AOC still true:   18
    missing D84 source arc, AOC false:         2
    D84 source intact, AOC false:              0

Thus the exact D84 source skeleton is not forced by the currently
checked raw gates.  It is a sufficient normal form, not a necessary
normal form.

The only source-category failure that coincides with AOC failure in this
single-reversal neighbourhood is `top_two_fan`, namely deletion of one
of the two exits from `tau`:

    (22,20) -> (20,22), missing (23,21)
    (22,21) -> (21,22), missing (23,22)

These are exactly the SLE/top-support failures already isolated in D76
and repaired by D79.

Many other individual D84 source arcs are slack for AOC.  The audit
finds AOC-preserving reversals that remove arcs from:

    robust_middle_support,
    terminal_support_backfan,
    r2_boundary_L_to_P,
    internal_L,
    r2_boundary_H_to_L,
    internal_H,
    shortcut_H_to_M,
    shortcut_S_to_M,
    r2_boundary_S_to_H,
    internal_S.

## Consequence

Do not try to prove the exact D84 skeleton from only the present
formalized sealed-block/CL/DT gates.  That statement is too strong.

D84 remains useful: if the skeleton is available, D83 proves ER-4 by
monotonicity.  What D85 changes is the next raw structural target.  The
right target is now a relaxed residual source profile, not exact
containment of every D84 arc.

## Replacement Target: RRSP

The relaxed residual source profile should prove cut-count capacity
rather than exact source-arc containment.

Mandatory pieces:

1. active first-successor attachment, including `w1 -> tau` and the
   semicomplete returns to `w1`;
2. SLE/top two-fan at `tau`;
3. enough residual ladder capacity so every non-endpoint `eta` and
   `zeta` row has value at least three after the endpoint rows handled
   in D81/D82 are removed.

Allowed slack:

* individual internal ladder arcs may be absent if the affected
  `eta`/`zeta` rows still have value at least three;
* individual R2 boundary, shortcut, or backfan arcs may be absent if
  another source term supplies the same row capacity;
* the D74 weak-middle deletion remains allowed and is handled by the
  endpoint-reduced profile.

Equivalently, the raw CL/DT proof should establish lower bounds on the
families of residual row counts, not a literal copy of every arc in the
D84 skeleton.

## Audit

The script asserts:

* `structural_survivors = 27`;
* `missing_source_aoc_ok = 18`;
* `missing_source_aoc_bad = 2`;
* `source_intact_aoc_bad = 0`;
* the AOC-bad missing category set is exactly `top_two_fan`.

This preserves the useful part of D84 while preventing proof effort from
being spent on a false exact-normal-form obligation.
