# D73: Sealed-Block Primitive Certificate Derivation

Date: 2026-06-19.

Artifact: `scripts/sealed_block_primitive_certificate_audit.py`.

## Purpose

The requested target was to derive D71's HBO package and D72's
outside-core certificate OC directly from sealed-block/CL/DT primitives.

This note separates what is now genuinely derived from what is still an
unstated primitive.

Verdict:

* HBO is derived from C7 cage packing, C3 hooks, the root fan, and
  semicompleteness of the head block.  D71's total ordered-head
  hypothesis was stronger than necessary.
* OC reduces to one additional primitive: the post-first-successor
  outside core `O'` must be 2-arc-strong.  The current written CL/DT
  notes do not yet prove that statement.  D42 has it by its
  distance-graded support ladder, and the audit verifies it, but it
  should now be named as the **W-core two-support lemma**.

## Primitive HBO Derivation

Let

    Q0 = {u} union R union Z,

where `R` is the non-root cage reserve and `Z` is the head block
consisting of the escaped `AV_u` heads together with `v`.

Use the following primitive consequences.

**P-H1, reserve expansion from C7.**  For every nonempty `P subset R`,

    |A(P, ({u} union R) \ P)| >= 2.

Indeed, C7 gives three arc-disjoint in-arborescences of the cage rooted
at `u`.  Each arborescence must send at least one arc from `P` to the
complement of `P` inside the cage, so the weaker lower bound two follows.

**P-H2, root fan.**  For every `z in Z`,

    u -> z.

For `v` this is the gateway arc `a=(u,v)`.  For the other members of
`Z` this is exactly the statement that they are escaped `AV_u` heads.

**P-H3, hooks from the head block.**  For every `z in Z` and every
`r in R`,

    z -> r.

This is C3, applied to the K-side head-block normal form: the escaped
heads and `v` lie in `K \ C_u`, while `R` is the K-reserve in the cage.
This is the one type condition that must be kept explicit.  If a future
sealed block allows an I-side escaped head in `Z`, C3 alone does not
give this hook package.

**P-H4, semicomplete head block.**  `C[Z]` is semicomplete.

Consequently there is at most one head-block source, i.e. at most one
vertex `z in Z` with no entry from `Z \ {z}`.

### Head-Source Lemma

Assume P-H1 through P-H4 and `|Z|>=2`.  If

    empty != T proper subset Q0
    and |A(Q0 \ T, T)| <= 1,

then `T={z}` where `z` is the unique source of `C[Z]`.  In particular
there is at most one such singleton.  It is active only when its actual
entry count is one.

Proof.  If `u notin T` and `T cap Z` contains at least two vertices,
the root fan gives at least two entries.  If `T cap Z={z}` and `z` has a
head-block in-neighbour `z'`, then `u -> z` and `z' -> z` are two
entries.  Hence a singleton head can be low only when it is a source of
`C[Z]`.

If `u notin T`, `T cap Z={z}` is a source, and `T` also meets `R`, then
some other head `z'` exists because `|Z|>=2`; P-H3 gives an entry
`z' -> r` into `T cap R`, in addition to `u -> z`.  If
`u notin T` and `T cap Z` is empty, then `T cap R` is nonempty, and two
heads of `Z` enter it by P-H3.

Now suppose `u in T`.  If `R \ T` is nonempty, P-H1 applied to
`R \ T` gives at least two arcs into `T`.  If `R subset T`, then `T` is
proper only if some `z in Z` lies outside `T`; by P-H3 that `z` sends
arcs to every vertex of `R`, and `|R|>=2`, giving two entries.

Thus only a singleton source of `C[Z]` can have fewer than two entries.
The root fan supplies `u -> z`, so the actual entry count is at least
one.  Extra reverse-head arcs simply remove the singleton from the low
list.  QED.

This proves HBQ from the sealed-block primitives, modulo the explicit
K-side head-block normal form in P-H3.

## Primitive OC Derivation

Let `w1` be the first chain successor outside `Q0`, let

    O = V(C) \ Q0,
    O' = O \ {w1}.

D72's OC certificate was:

1. `d^+_{C[O]}({w1}) = 1`;
2. `lambda(C[O']) >= 2`;
3. `|A(O', {w1})| >= 2`.

The monotone form is slightly cleaner:

* if `d^+_{C[O]}({w1}) >= 2`, then `{w1}` is not active and there is no
  external-prefix obligation at `w1`;
* if `{w1}` is active, it is enough to prove
  `d^+_{C[O]}({w1}) >= 1`, because active means below two and therefore
  exactly one.

The primitive consequences are then:

**P-O1, first-successor support.**  In the nonterminal sealed block, the
first successor has at least one outside-core exit.  Otherwise the
successor would not enter the outside `W` support before the next forced
crossing, contradicting the CL description that every nonterminal
`W`-segment contains an `O` support vertex entered by a root/spare label.

**P-O3, returns to the first successor.**  If `{w1}` is active, then
semicompleteness plus `d^+_{C[O]}({w1}) = 1` gives at least
`|O'|-1` arcs from `O'` to `w1`.  In the nonterminal multi-crossing case
`|O'|>=3`, so there are at least two returns.

The remaining missing primitive is:

**W2, W-core two-support lemma.**  After removing the first successor
and the pending forced tails, the outside support core is 2-arc-strong:

    lambda(C[O']) >= 2.

With W2, OC follows immediately: P-O1 gives the first-successor exit
when active, W2 is OC-2, and P-O3 is OC-3.  D72 then gives FSQ.

## Why W2 Is Still A Real Obligation

The current CL statement classifies arcs from the sealed block into
`W`: every such arc is a forced chain crossing, up to the terminal
rho-label.  DT supplies distinct rho-tails in `X_P` and the root/spare
support that starts `W`.

Those facts do not, by themselves as written, state that the remaining
outside quotient `O'` has no one-arc cut.  D42's construction enforces
W2 with its distance-graded two-fan ladder, and the audit confirms

    lambda(C[O']) = 2.

But a proof for arbitrary sealed multi-crossing kernels still has to
show that the `W` support cannot degenerate to a one-exit chain after
`w1` is removed.  This is the next primitive lemma to prove or refute.

## Audit

The audit checks D42, D63 reverse-head, D66 rho-entry, and combined
D63+D66.  In all four variants:

    min_reserve_expansion = 3,
    root_fan = [(2,6),(2,7),(2,8)],
    outside_core_lambda = 2,
    w1_exits = [(10,23)],
    |A(O', {10})| = 10.

For the head block:

* D42 and D66 have the unique head source `6`, giving the active
  complement `{6}` with entry `(2,6)`;
* D63 variants have no head source because the reverse-head arc enters
  `6`, so no internal low complement remains.

## Next Target

The local cut derivation is now reduced to one primitive statement:

> Prove W2 from CL maximality, DT root/spare support, and shortest-path
> no-shortcut constraints; or construct a sealed multi-crossing kernel
> in which `C[O \ {w1}]` has a one-arc cut while all sealed-chain gates
> survive.

Once W2 is settled, HBO and OC are both primitive consequences, and the
D70-D72 local normal-form chain closes.
