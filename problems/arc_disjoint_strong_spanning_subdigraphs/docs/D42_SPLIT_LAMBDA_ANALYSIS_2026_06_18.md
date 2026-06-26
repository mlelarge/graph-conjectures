# D52: D42 split-core lambda analysis

Date: 2026-06-18.

Artifact:

    scripts/d42_split_lambda_analyzer.py

Status: sampled structural diagnostic.

## Goal

D51 showed that prescribed pending completion on D42 is sparse because
most split choices leave the split semicomplete core below
2-arc-strong.  D52 ignores colour and samples more D42 split choices,
asking only which split-off endpoint regions correlate with
`lambda(core) >= 2`.

Run:

    .venv/bin/python scripts/d42_split_lambda_analyzer.py

## Result

With seed `5113`, 2000 split choices sampled from the local cap
`{9:80, 11:80, 13:80}` give:

    lambda_counts={0:813, 1:921, 2:258, 3:8}

So 266/2000 sampled choices, or 13.3%, make the split core at least
2-arc-strong.

Endpoint-region support among successful choices:

* `heads -> chainK`: present in 195/266 successes (73.3%) but only
  471/1734 failures (27.2%);
* `u -> chainK`: present in 186/266 successes (69.9%) but only
  321/1734 failures (18.5%);
* `roots -> chainK`: present in 62/266 successes (23.3%) but
  872/1734 failures (50.3%).

Thus the sampled signal is:

* useful: feed the chainK segment from the cage side, especially via
  `u -> chainK` and `heads -> chainK`;
* dangerous: spend too many split arcs as `roots -> chainK`, which tends
  to strand the core at lambda 0 or 1.

The unique lambda-3 example has:

    s=9:  heads -> chainK, roots -> cage
    s=11: u -> chainK,     roots -> heads
    s=13: u -> chainK,     roots -> heads

This looks lemma-shaped: one split path should inject from an upstream
root/head side back into the cage/head side, while at least two paths
should feed the chainK side from `u` or escaped heads.

## Next target

Make the condition exact.  A follow-up checker should enumerate the D42
local-cap sample and test candidate predicates such as:

* at least two of the six split arcs have head in `chainK`;
* at least one `u -> chainK`;
* at least one `heads -> chainK`;
* at least one `roots -> cage` or `roots -> heads`;
* no more than one `roots -> chainK`.

The goal is a small sufficient predicate for `lambda(core) >= 2`, not a
perfect classifier.  Such a predicate is the likely combinatorial heart
of the Prescribed Pending Missing Entry Lemma.
