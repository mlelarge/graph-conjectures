# D51: robustness count for prescribed pending split-offs

Date: 2026-06-18.

Artifact:

    scripts/pending_decomposition_robustness_count.py

Status: bounded diagnostic evidence.

## Probe

D50 found one prescribed pending split-off completion per positive
witness host.  D51 counts robustness.  For each sampled split-off choice,
the script tests every prescribed red/blue orientation of the two split
arcs through each independent-side vertex.

For the one-independent-vertex cases, all local split choices are
exhausted under the D49 local-choice cap.  For D42, the product is large
(`80^3` choices under the local cap), so the script samples 120 global
choices deterministically.

Run:

    .venv/bin/python scripts/pending_decomposition_robustness_count.py

## Results

The four non-D42 positive hosts are completely robust under this probe:

* `rho_headless_D17_and_D47_host`: 18/18 split choices work; 36/36
  prescribed orientations SAT; all split cores have `lambda=2`.
* `dominated_D18_host`: 18/18 choices; 36/36 orientations SAT;
  `lambda=2`.
* `relay_free_D19_host`: 18/18 choices; 36/36 orientations SAT;
  `lambda=2`.
* `saturation_kernel_D38_host`: 18/18 choices; 36/36 orientations SAT;
  `lambda=2`.

D42 is sparse but genuinely positive:

    local_counts={9:80, 11:80, 13:80}
    sampled choices=120 out of 512000 under the local cap
    choices with any SAT prescription = 24/120 = 20.0%
    SAT prescriptions = 98/960 = 10.2%
    lambda_counts={0:58, 1:38, 2:23, 3:1}

Thus most random split choices fail before colouring can help: they leave
the split core below 2-arc-strong.  But there is a nontrivial family of
working choices, and the first D50 split choice is among them.

D28 remains sharply isolated:

    choices with any SAT prescription = 0/18
    SAT prescriptions = 0/36
    lambda_counts={1:18}

Every naive two-split core for D28 has `lambda=1`, so the obstruction is
not colour assignment; it is insufficient split-off connectivity of the
tournament core.

## Consequence

The pending-decomposition route now has a precise shape:

1. For ordinary rho-headless/relay/saturation hosts, the pending split
   choices are maximally robust in this probe.
2. For the D42 chain kernel, the right proof obligation is existence of
   split paths that make the semicomplete core at least 2-arc-strong;
   prescribed colour completion then frequently succeeds.
3. D28 should not be forced into the same naive pending lemma.  It is a
   tournament-core exception whose failure mode is core connectivity,
   not prescribed colour compatibility.

## Next proof target

A plausible Prescribed Pending Missing Entry Lemma should assert:

> In a non-degenerate sealed multi-crossing chain kernel, the forced-chain
> independent vertices admit opposite-colour split-off path pairs such
> that the split semicomplete core is 2-arc-strong.

Once the split core is 2-arc-strong and semicomplete, the split-digraph
literature suggests the prescribed pending completion should follow from
semicomplete SAD/branching machinery.  The next concrete task is to
derive the D42 split-path existence condition symbolically from the
chain geometry, or to write a focused checker that characterizes exactly
which D42 split choices have `lambda>=2`.
