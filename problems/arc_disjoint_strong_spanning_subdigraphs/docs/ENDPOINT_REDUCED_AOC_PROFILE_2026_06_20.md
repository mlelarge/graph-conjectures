# D80: Endpoint-Reduced AOC Profile

Date: 2026-06-20.

Artifact: `scripts/endpoint_reduced_aoc_profile_audit.py`.

## Purpose

D79 closes the top-support singleton under the strengthened SLE
primitive.  This audit lists the remaining tight AOC rows in the accepted
normal forms, so the next symbolic proof can target concrete cut types.

## AOC Rows

Recall `O' = O \ {w1}`.  AOC has two inequalities:

* cuts not containing `w1`:

      d^+_{O'}(B) + d(B,{w1}) >= 2;

* cuts containing `w1`, written `{w1} union A`:

      d^+_{O'}(A) + d({w1}, O' \ A) >= 2.

In D42 host labels,

    w1 = 10,
    tau = 23.

## Tight Rows Without The D74 Support Reversal

For D42, D63, D66, and D63+D66, the tight rows are:

**No `w1`:**

    B = {23},
    exits = (23,21),(23,22).

This is exactly the top-support row closed by SLE.

**With `w1`:**

    A = {23},
    exits = (23,21),(23,22);

and

    A = O' \ {14}
      = {12,15,16,17,18,19,20,21,22,23},
    exits = (15,14),(16,14).

The first is again the top-support row.  The second is the
root-complement row: two root/support vertices return to the missing
root-side vertex.

## Tight Rows With The D74 Support Reversal

For D74 and its D63/D66 variants, D74 adds the middle support singleton

    m = 12.

The tight rows are:

**No `w1`:**

    B = {12},
    exits = (12,23) and (12,10);

    B = {23},
    exits = (23,21),(23,22).

**With `w1`:**

    A = {12},
    exits = (12,23) and (10,23);

    A = O' \ {14},
    exits = (15,14),(16,14);

    A = {12,23},
    exits = (23,21),(23,22);

    A = {23},
    exits = (23,21),(23,22).

Thus D74's weak internal core cut is repaired exactly by the attachment
terms to and from `w1`, while the top support rows are repaired by SLE.

## Consequence

After SLE, the remaining proof obligations are:

1. **Middle-support attachment:** a middle support singleton like `{12}`
   has one internal support exit and the appropriate attachment to/from
   `w1`.
2. **Root-complement return:** the co-root row `O' \ {r}` has two exits
   to the omitted root-side vertex.
3. **No other tight rows:** every other outside cut has slack at least
   three by support-ladder expansion and semicompleteness.

These are the concrete cut types for the nonterminal AOC expansion
proof.
