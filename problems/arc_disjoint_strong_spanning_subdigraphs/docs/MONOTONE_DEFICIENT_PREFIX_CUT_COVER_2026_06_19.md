# D64: Monotone Deficient-Prefix Cut-Cover Lemma

Date: 2026-06-19.

Artifact: `scripts/monotone_deficient_cut_cover_audit.py`.

## Purpose

D63 refuted the exact structural profile

    Q- subset Q0 subset Q+,     out-sizes 1,0,1.

The failure is monotone: the old `Q-` cut gains an extra core exit and
therefore no longer needs pending repair.  This note replaces the fixed
D42 demand vector `(1,2,1)` by the actual deficiency vector.

## Setup

Let `C` be the split semicomplete core obtained after deleting the
pending forced-chain vertices.  Assume we have a nested candidate triad

    Q- subset Q0 subset Q+

and write

    b_sigma = |delta_C^+(Q_sigma)|,
    r_sigma = max(0, 2 - b_sigma)

for `sigma in {-,0,+}`.  The vector

    r = (r_-, r_0, r_+)

is the actual pending-repair demand.  In the chain-kernel profiles under
discussion it satisfies

    r <= (1,2,1)

coordinatewise: the side candidates have at least one old core exit when
they are deficient, and the sealed middle candidate can have demand two.

For a set `S` of pending split arcs define

    c_sigma(S) = |S cap delta^+(Q_sigma)|.

The active deficient prefixes are exactly those coordinates with
`r_sigma > 0`.

## Exact Monotone Criterion

Assume the structural core property:

> Every split-core cut of out-size at most one is one of the active
> candidate prefixes `Q_sigma`.

Then for any pending split arc set `S`, the repaired core `C+S` has
`lambda >= 2` if and only if

    c_sigma(S) >= r_sigma       for every sigma in {-,0,+}.      (MC)

### Proof

If `r_sigma=0`, then `b_sigma >= 2`, so `Q_sigma` is already repaired.
If `r_sigma>0`, then `b_sigma` is either zero or one and the new out-size
of `Q_sigma` is exactly

    b_sigma + c_sigma(S).

Thus `Q_sigma` reaches out-size at least two exactly when
`c_sigma(S) >= 2-b_sigma = r_sigma`.

Every other split-core cut has out-size at least two by the structural
core property, and adding pending split arcs is monotone on directed
out-cuts.  Therefore no other cut can become bad.  This proves both
necessity and sufficiency of (MC).  QED.

## Variable Selection Lemma

Assume in addition the prefix-plus-pending cut formula from D62: for
each candidate prefix `Q` and every pending subset `J`,

    d^+(Q union J)
      = b(Q)
        + sum_{i notin J} e_i(Q)
        + sum_{i in J} f_i(Q),

with endpoint-cleanliness removing all correction terms.  Since the
original host is 3-arc-strong, minimizing over `J` gives

    sum_i min(e_i(Q), f_i(Q)) >= 3 - b(Q).       (CAP)

In particular, for every active candidate,

    sum_i min(e_i(Q), f_i(Q)) >= r(Q).

For a pending vertex `i`, the quantity `min(e_i(Q), f_i(Q))` is the
maximum number of locally pairwise source-and-target-disjoint two-step
paths through `i` that cross `Q`.

Therefore, for each coordinate `sigma`, choose `r_sigma` raw two-step
pending witnesses crossing `Q_sigma`.  The total requested demand is at
most four because `r <= (1,2,1)`.

Group the raw witnesses by their pending middle vertex.  Apply the D61
interval-compression lemma to each group.  That lemma produces at most
two legal paths through the same pending vertex and preserves the cover
vector after truncation by `(1,2,1)`.  Since the present demand vector
`r` is coordinatewise at most `(1,2,1)`, the same compressed local paths
still dominate the truncated demand needed by this group.

After all groups are compressed, the union of the local choices is a
legal partial pending split choice and its total repair vector dominates
`r`.  The pending-completion theorem supplies the unused mate at every
pending vertex with only one prescribed path and completes all remaining
forced pending vertices.

Combining this selection with the exact monotone criterion proves:

> If the monotone deficient-prefix profile and endpoint-clean
> prefix-plus-pending formula hold, then the pending split paths can be
> chosen so that the repaired split core has `lambda >= 2`.

## Audit: D42 and the D63 Perturbation

The executable audit keeps the same three coordinates
`Q-,Q0,Q+` but computes the demand from `max(0,2-b)`.

For the original D42 core:

    core_outs    = (1,0,1)
    requirements = (1,2,1)
    success      = 84014 / 512000

This is exactly the D60 criterion.

For the D63 reverse-head perturbation, adding the host arc `7 -> 6`:

    core_outs    = (2,0,1)
    requirements = (0,2,1)
    success      = 87064 / 512000

The active deficient prefixes are only `Q0` and `Q+`.  The old `Q-`
coordinate is retained in the table with demand zero, and the audit
checks that covering `(0,2,1)` is exactly equivalent to repairing all
core cuts of out-size at most one.

## Consequence

D64 closes the correction forced by D63: the cut-cover proof stack no
longer needs the false assertion that the one-head-deleted prefix always
has out-size one.  Extra core exits simply delete coordinates from the
repair demand.

The remaining structural task is now sharply separated:

1. derive the sealed middle prefix `Q0` from the sealed block;
2. include the one-head-deleted and successor prefixes only when their
   actual core out-size is below two;
3. prove that no other split-core cut has out-size below two;
4. prove the endpoint-cleanliness hypotheses needed for the D62
   prefix-plus-pending formula;
5. supply or cite the colour-prescribed semicomplete pending-completion
   theorem used to finish partially prescribed local splits.
