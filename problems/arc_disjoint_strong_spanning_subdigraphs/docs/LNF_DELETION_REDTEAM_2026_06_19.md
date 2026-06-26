# D69: Local Normal-Form Deletion Red-Team

Date: 2026-06-19.

Artifact: `scripts/local_normal_form_deletion_redteam.py`.

## Purpose

D68 reduces the remaining structural work to deriving LNF-1 and LNF-2
from sealed-block/CL/DT.  Before investing in that proof, this note
red-teams the local normal form near D42.

The search asks:

> Can we delete one or two relevant core arcs, preserve the sealed-chain
> gates and the original hard gateway, but create an extra internal low
> cut, extra external low cut, or single-exchange low cut?

If yes, LNF would need another hypothesis.  If no, the local proof
target survives this bounded attack.

## Search Scope

The script first computes all local cuts that have base out-size at most
three:

* internal cuts of `C[Q0]`;
* external cuts of `C\Q0`;
* single-exchange cuts `(Q0 \ {h}) union {w}`.

Only arcs appearing in these near-low cuts are considered for deletion.
Deleting at most two arcs cannot turn any local cut of out-size at least
four into a low cut, so this is the complete two-deletion attack against
the local profile.

The resulting risk set has 36 D-bullet arcs.  The script checks all

    36 single deletions,
    binom(36,2)=630 pair deletions.

A candidate is promoted only if it:

1. creates an LNF violation;
2. preserves the cheap sealed-chain gates;
3. preserves `lambda(D^bullet)>=3` and `lambda(host)>=3`;
4. preserves the full structural gates;
5. preserves the original hard gateway pair.

## Result

No counterkernel survives.

The exact counts are:

    lnf_violations_before_gates = 290
    cheap_pass                  = 3
    full_checks                 = 3
    hits                        = 0

The gate failures are:

    cheap:near_split = 287
    lambda_db>=3     = 3

So almost every local-profile violation destroys the semicomplete
near-split core immediately.  The only three that pass the cheap shape
still drop below 3-arc-strongness.

## Example Failures

Deleting the single D-bullet arc

    (1,5)

creates extra internal low cuts, including

    {2,3,4,5,8}
    {2,3,4,5,7,8},

but it violates the near-split semicomplete condition.

Deleting the pair

    (2,3), (2,4)

creates an extra internal low cut `{3}`, but the contraction has

    lambda(D^bullet)=1

with min-cut side `{2}`.  Thus 3-arc-strongness kills the candidate.

## Interpretation

D69 is not a universal proof of LNF-1/LNF-2.  It is a bounded
red-team result with a useful message:

* LNF-1 is tightly coupled to semicompleteness inside the head/cage
  block and to 3-arc-strongness of the cage.
* LNF-2 is stable under every one/two-deletion attack in the relevant
  outside near-low cuts.
* Single-exchange lows do not appear unless one of the local singleton
  terms is destroyed, and those attempts already fail earlier gates.

The symbolic proof should therefore use exactly these ingredients:

1. semicomplete orientation inside the head block;
2. cage packing / 3-arc-strongness for internal singleton cuts;
3. CL's forced-chain first-successor structure for outside singleton
   cuts;
4. D65's single-exchange formula to combine the singleton terms.

## Next Target

Promote LNF-1 and LNF-2 symbolically in two smaller lemmas:

* **Head-Block Internal Lemma:** in the sealed middle block, any
  internal cut below two must omit a single head; if a reverse head arc
  is present, even that cut is not active.
* **First-Successor External Lemma:** outside the sealed middle block,
  the only outside singleton cut below two is the first chain successor
  `w1`; all other outside cuts have at least two exits by CL/DT support
  and semicomplete hooks.

Once those are proved, D68 supplies the final local-to-global assembly.
