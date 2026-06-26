# D62: Prefix-Plus-Pending Profile Audit

Date: 2026-06-18.

Artifact: `scripts/d42_prefix_pending_profile_audit.py`.

## Purpose

D61 proves the generalized cut-cover selection lemma assuming the full
prefix-plus-pending profile.  This note identifies which part of that
profile is formal bookkeeping and which part remains structural.

## Bookkeeping Lemma

Let `C` be the split semicomplete core obtained after deleting pending
vertices `I`.  Let `Q` be a core-side set and let `J subseteq I`.  Assume:

1. pending vertices are independent;
2. pending vertices have no arcs to or from the chord endpoints in the
   relevant cut calculation;
3. `Q` has no out-arcs to the chord endpoints.

Write:

    b(Q)   = |delta_C^+(Q)|,
    e_i(Q) = |A(Q, i)|,
    f_i(Q) = |A(i, C \ Q)|.

Then in the original host

    |delta^+(Q union J)|
      = b(Q)
        + sum_{i notin J} e_i(Q)
        + sum_{i in J} f_i(Q).                 (PP)

This is just the directed cut partition.  Core arcs contribute `b(Q)`.
For each pending vertex `i`, if `i notin J`, the only new crossing arcs
through `i` are entries from `Q` to `i`; if `i in J`, the only new
crossing arcs through `i` are exits from `i` to `C \ Q`.  Independence
of the pending side removes arcs among pending vertices, and the
endpoint-cleanliness assumptions remove chord-endpoint correction terms.

If the original host is 3-arc-strong, (PP) applied to every `J` gives

    sum_i min(e_i(Q), f_i(Q)) >= 3 - b(Q).      (CAP)

Indeed the minimizing choice puts `i` in `J` exactly when
`f_i(Q) <= e_i(Q)`.

Thus the prefix-plus-pending algebra in D61 is not a new combinatorial
gap once endpoint-cleanliness and the core prefix cuts are known.

## D42 Audit

For the D42 host, the pending vertices are `(9,11,13)`.  The audit
checks the three deficient core prefixes and every subset of pending
vertices.

For `Q- = {2,3,4,5,7,8}`, `b(Q-)=1`:

    s=9:  e=3, f=1, min=1
    s=11: e=2, f=2, min=2
    s=13: e=1, f=2, min=1

So `sum min = 4 >= 2 = 3-b(Q-)`.

For `Q0 = {2,3,4,5,6,7,8}`, `b(Q0)=0`:

    s=9:  e=4, f=1, min=1
    s=11: e=3, f=1, min=1
    s=13: e=1, f=1, min=1

So `sum min = 3 = 3-b(Q0)`.

For `Q+ = {2,3,4,5,6,7,8,10}`, `b(Q+)=1`:

    s=9:  e=4, f=0, min=0
    s=11: e=4, f=1, min=1
    s=13: e=1, f=1, min=1

So `sum min = 2 = 3-b(Q+)`.

The tight witness cuts are:

    Q0 union {9,11}:       out-size 3,
    Q0 union {9,11,13}:    out-size 3,
    Q+ union {9,11}:       out-size 3,
    Q+ union {9,11,13}:    out-size 3.

These are the actual 3-arc-strong cuts forcing the D61 capacities.

The audit also verifies the endpoint-cleanliness conditions:

* no deficient prefix has an out-arc to chord endpoints `{0,1}`;
* no chord endpoint enters a deficient prefix;
* no pending vertex has an arc to or from non-core vertices.

For every `J subseteq {9,11,13}`, the script asserts

    actual_host_out(Q union J) = formula_PP(Q,J) >= 3.

## Consequence

D62 reduces the remaining profile problem to the structural core:

1. derive the three core prefixes `Q- subset Q0 subset Q+` from the
   sealed-block, CL, and DT hypotheses;
2. prove their split-core out-sizes are `1,0,1`;
3. prove no other split-core cut has out-size below two;
4. prove the endpoint-cleanliness conditions needed for (PP).

Once these are established, D62 gives the prefix-plus-pending capacity
inequalities and D61 supplies the pending choices covering `(1,2,1)`.

