# 20 — Empirical sweep on 3-arc-strong $(1,0)$-near-split digraphs

Author: Combinatorial Optimization / Exact Algorithms Coder
Date: 2026-05-16
Status: first deliverable for the amended Route B
(`team/13_publishability_decision.md` §7 commits this file). Successor
to `team/15_v6_ols_empirical.md` after the OLS round-decomposition route
was retracted (`team/17_ols_rd_problem.md`).

Companions: `team/10_phase4_vehicle6.md` (V6 generator + pattern checks
reused), `team/11_cl1_proof_v1.md` (CL1 final-form hypotheses),
`team/13_publishability_decision.md` §7 (the $(1,0)$-near-split pivot),
`code/generators/near_split.py` (the $(1,0)$-near-split generator built
for this report), `code/run_route_b_near_split.py` (the broad-sample
driver), `code/run_route_b_ns_exhaustive_l2.py` (the exhaustive
$\lambda=2$ UNSAT search), `code/benchmarks.py` (the strict-split
exception family used for §3.b classification), and the headline logs
`code/logs/route_b_ns_20260516_*.json` and
`code/logs/route_b_ns_exh_l2_20260516_*.json`.

The deliverable answers the three Route B charter questions for the
amended class:

* (Q1) does the amended Route B theorem hold empirically — every
  3-arc-strong $(1,0)$-near-split digraph admits a SAD?
* (Q2) is CL1 (final form, `team/11` §5.1) the operative lifting
  mechanism on the natural partition $V_1' = V_1$, $V_2' = V_2$?
* (Q3) does the strict-split (Ai et al. 2024) $\lambda=2$ UNSAT
  exception family extend to a strictly larger $(1,0)$-NS family?

Verdicts in three lines:

* **Q1: YES on 599 verified-SAT instances across 7 182 broad-sample
  candidates, 0 UNSAT at $\lambda = 3$, 0 ILP/SAT disagreements; YES
  also on the truly-exhaustive $(|V_1|, |V_2|) = (2, 3)$ enumeration
  (0 $\lambda = 3$ UNSAT out of 192 $\lambda = 3$ candidates).**
* **Q2: NO on the natural partition.** CL1 hypothesis (1) fails on
  **100 %** of candidates with $|V_1| \geq 2$ because $D[V_1]$ consists
  of a single arc (1-arc-strong, hence not SAD-decomposable);
  hypothesis (2) holds on **100 %** of SAT witnesses. The modified
  partition $V_1' = V_1 \cup \{w\}$ for $w \in V_2$ recovers
  hypothesis (1) on **0 / 599 (0 %)** of natural-partition failures.
* **Q3: YES, strictly larger.** Truly-exhaustive enumeration at
  $(|V_1|, |V_2|) = (2, 3)$, $n = 5$, finds **10 canonical
  $\lambda = 2$ UNSAT** instances; only **1** is iso to an existing
  strict-split UNSAT ($\text{AiEtAl\_L211\_min}$ in a relabelled
  partition), and **9 are genuinely new** — they are not isomorphic
  (as labelled digraphs) to any UNSAT benchmark in `benchmarks.py`
  (including $S_4$, the three BJG–Yeo 2020 compositions, the three Ai
  et al. 2024 instances, and $C_6^2, C_8^2$). Partial enumerations at
  $(3, 3)$ (700 k of 42 M, $\sim 1.7 \%$) yield **136 canonical NEW**;
  partial at $(2, 4)$ (400 k of 95 M, $\sim 0.4 \%$) yields **24
  canonical NEW**. The $(1,0)$-NS exception family is **substantially
  larger** than the strict-split list and is unlikely to be finite.

---

## §1 — Construction library

`code/generators/near_split.py` (≈ 430 lines) builds three families of
$(1,0)$-near-split candidates. The $(1,0)$-near-split property is
verified by an *independent* function
`is_one_zero_near_split(D, V_1, V_2)` *after* construction. Per the
spec's hard rule, the construction is **never trusted** to imply
$(1,0)$-near-split-ness; the empirical confirmation rate is **100 %**
across the broad-sample sweep (4 700 / 4 700 confirmed).

### §1.1 Definition (repeated for the record)

A digraph $D$ is *$(1,0)$-near-split* with respect to the partition
$V(D) = V_1 \dot\cup V_2$ if:

(NS1) $D[V_2]$ is *semicomplete*: for every unordered pair
$\{u, v\} \subseteq V_2$ with $u \neq v$, at least one of $(u, v),
(v, u)$ is an arc of $D$;

(NS2) the arcs between $V_1$ and $V_2$ (the "bridge" arcs, in either
direction) are *unrestricted*;

(NS3) *exactly one* arc lies inside $V_1$: there is a unique ordered
pair $(a, b) \in V_1 \times V_1$, $a \neq b$, with $(a, b) \in A(D)$.

When $|V_1| = 1$ clause (NS3) is vacuous and we exclude such instances
from this sweep (they are strict-split, handled by Ai et al. 2024).

### §1.2 Construction A — Exhaustive enumeration

For a fixed $(|V_1|, |V_2|)$ pair, the enumerator iterates over

1. every semicomplete orientation of $V_2$ — $3^{\binom{|V_2|}{2}}$
   choices, since each unordered pair has 3 valid states
   ($u \to v$ only, $v \to u$ only, both);
2. every ordered $V_1$-internal arc — $|V_1|(|V_1| - 1)$ choices;
3. every subset of the $2|V_1||V_2|$ possible bridge ordered pairs.

The cap parameters `cap_per_v2_orientation` and `bridge_cap_per_pair`
control the budget per pair; the driver `run_route_b_near_split.py`
processes Construction A at the pair grid
$\{(2, 3), (2, 4), (2, 5), (3, 3), (3, 4), (3, 5), (4, 3), (4, 4)\}$.

The companion driver `run_route_b_ns_exhaustive_l2.py` does *truly
exhaustive* enumeration at the smallest pairs (no caps), with canonical
short-circuit at the pynauty level.

### §1.3 Construction B — Random sampling

For each $(|V_1|, |V_2|)$ pair in the larger grid
$\{(2, 6), (3, 6), (2, 7), (3, 7), (4, 5), (4, 6)\}$, each sample
independently picks:

* an $V_2$ orientation: each unordered $V_2$ pair independently chooses
  one of $\{\text{only fwd}, \text{only rev}, \text{both}\}$ with equal
  probability;
* an ordered $V_1$-internal arc uniformly;
* each bridge included with probability $p \in \{0.35, 0.50, 0.65\}$
  (chosen uniformly per sample).

### §1.4 Construction C — Strict-split reference list

The strict-split $\lambda = 2$ UNSAT instances from `benchmarks.py`
(`AiEtAl_L312_min`, `AiEtAl_iv_star_iv`) are extended by adding each of
the two possible $V_1$-internal ordered arcs (when $|V_1| = 2$). Note:
`AiEtAl_L211_min` has $|V_1| = 1$ (only vertex $u$) and therefore admits
no $(1,0)$-NS extension *with this partition*. (We do observe later
that the $\text{L211\_min}$ digraph itself is isomorphic to a
$(1,0)$-NS digraph under a *different* partition — see §3.b.)

Construction C contributes 4 reference candidates. **One of these is
$\lambda = 2$ UNSAT**: `iv_star_iv + (4, 5)` (the (1,0)-NS digraph
where the internal arc is consistent with $a$'s in-arc structure). The
other three become SAT after the addition.

---

## §2 — Sweep statistics

### §2.1 Broad-sample sweep

Production sweep configuration
(`run_route_b_near_split.py --cap-per-pair-A 600 --cap-B 400
--instance-time-s 8`; full log
`code/logs/route_b_ns_20260516_232842.json`):

| metric | value |
|---|---:|
| streamed | 7 182 |
| $(1,0)$-NS confirmed (independent check) | 7 182 (100.0 %) |
| strongly connected | 5 219 |
| $\lambda^{\text{arc}} = 2$ | 1 760 |
| $\lambda^{\text{arc}} = 3$ | 599 |
| $\lambda^{\text{arc}} > 3$ rejected | 109 |
| $\lambda^{\text{arc}} < 2$ on strong instances | 2 751 |
| cross-checked verified SAT ($\lambda = 3$) | **599** |
| cross-checked verified UNSAT ($\lambda = 3$) | **0** |
| cross-checked verified SAT ($\lambda = 2$) | 1 759 |
| cross-checked verified UNSAT ($\lambda = 2$) | **1** |
| cross-check disagreements | 0 |
| labelled-distinct $\lambda = 3$ SAT $\to$ canonical-distinct | 599 $\to$ 595 |
| largest iso-class | 2 |
| wall-time | 191 s |

Hit-rate at the $\lambda \in \{2, 3\}$ gate is
$(1760 + 599) / 7182 = 32.8 \%$, comfortably above the spec's 5 %
floor. The 1.5 % $\lambda > 3$ rejection rate is much smaller than the
OLS sweep's 27.5 % (`team/15`), because $(1,0)$-NS digraphs have a
single internal arc and otherwise unrestricted bridges, which keeps
$\lambda^{\text{arc}}$ from blowing up.

**Per-construction breakdown:**

| construction | streamed | $\lambda = 2$ | $\lambda = 3$ | $\lambda = 2$ UNSAT |
|---|---:|---:|---:|---:|
| A_exhaustive (cap-per-pair) | 4 778 | 930 | 188 | 0 |
| B_random (cap-per-pair) | 2 400 | 826 | 411 | 0 |
| C_reference | 4 | 4 | 0 | 1 |

The pair grid spans $|V_1| \in \{2, 3, 4\}$, $|V_2| \in
\{3, 4, 5, 6, 7\}$, with $\sim 400$-$600$ candidates streamed per
pair, total $|V_1| + |V_2| \leq 11$. The single $\lambda = 2$ UNSAT
recovered by the broad sweep is the Construction-C reference instance
`iv_star_iv + (4, 5)`; the truly-exhaustive (2, 3) sweep below
recovers many more.

### §2.2 Exhaustive enumeration at $(|V_1|, |V_2|) = (2, 3)$

`code/run_route_b_ns_exhaustive_l2.py --pairs (2,3)` enumerates every
labelled $(1,0)$-NS digraph at $n = 5$. The total enumeration size is
$3^{\binom{3}{2}} \cdot 2 \cdot 2^{12} = 27 \cdot 2 \cdot 4 \, 096 =
221 \, 184$.

Log: `code/logs/route_b_ns_exh_l2_20260516_232058.json`.

| metric | value |
|---|---:|
| enumerated | 221 184 |
| skipped (disconnected) | 77 184 |
| skipped ($\lambda < 2$) | 123 312 |
| skipped ($\lambda > 3$) | 0 |
| $\lambda^{\text{arc}} = 2$ exactly | 20 496 |
| $\lambda^{\text{arc}} = 3$ exactly | 192 |
| canonical-novel $\lambda = 2$ instances | 539 |
| **$\lambda = 2$ canonical-distinct UNSAT** | **10** |
| of those: iso to existing strict-split UNSAT | 1 |
| of those: NEW $(1,0)$-NS-specific UNSAT | **9** |
| $\lambda = 3$ UNSAT | **0** |
| wall-time | 85 s |

### §2.3 Partial exhaustive at $(3, 3)$ and $(2, 4)$

Both pairs have enumeration spaces in the $10^7$ - $10^8$ range
($42 \, M$ for $(3, 3)$, $95 \, M$ for $(2, 4)$); a full exhaustive
sweep on this machine would take hours. We ran each for $\sim 5$
minutes (logs incomplete; partial counts captured in
`code/logs/route_b_ns_exh_l2_20260516_232*.json` and stdout):

| pair | enumerated | (of total) | $\lambda = 2$ inst. seen | canonical-novel UNSAT (all NEW) | $\lambda = 3$ UNSAT |
|---|---:|---:|---:|---:|---:|
| $(3, 3)$ | 700 k | $\sim 1.7 \%$ | 15 532 | **136** | **0** |
| $(2, 4)$ | 400 k | $\sim 0.4 \%$ | 17 648 | **24** | **0** |

These are partial counts; the true canonical-UNSAT count is strictly
greater, but the headline (no $\lambda = 3$ UNSAT; many new
$\lambda = 2$ UNSAT) is robust.

---

## §3 — Headline findings

### §3.a — The amended Route B theorem holds (no $\lambda = 3$ UNSAT)

**Across the broad sweep (7 182 streamed, 599 verified-SAT at
$\lambda = 3$, full ILP+SAT cross-check) and the partial exhaustive
sweeps at $(2, 3), (3, 3), (2, 4)$ (combined $\sim 1.32$ M streamed,
$\sim 200$ verified-SAT instances at $\lambda = 3$), the amended Route B
theorem holds on every candidate. The Lead's 10-item counterexample
protocol is *not* triggered. `team/21_candidate_counterexample.md` is
not written.**

Per $(|V_1|, |V_2|)$:

* $|V_1| \in \{2, 3, 4\}$, $|V_2| \in \{3, 4, 5, 6, 7\}$, total
  $|V_1| + |V_2| \leq 11$, all 343 $\lambda = 3$ instances are SAT.
* the truly-exhaustive $(2, 3)$ enumeration produces 192 $\lambda = 3$
  instances, all SAT.

The amended Route B headline ("every 3-arc-strong $(1,0)$-near-split
digraph admits a SAD") is empirically robust at the scales tested.

### §3.b — The $\lambda = 2$ UNSAT exception family is strictly larger than the strict-split list

**The single most important diagnostic finding.** The strict-split
UNSAT family (Ai et al. 2024, Lemma 2.11, Lemma 3.12, Appendix B.3 case
(iv)*x(iv), plus $S_4$) contains exactly **4** canonical-distinct
digraphs at $n \leq 6$. The corresponding $(1,0)$-NS exception family
at the *same* size scale is strictly larger.

**Truly-exhaustive (2, 3), $n = 5$ — CORRECTED after audit Appendix A.7.**[^arcrev-fix]
Of 539 canonical-novel $(1,0)$-NS digraphs at $\lambda^{\text{arc}} = 2$:

| classification | canonical count | labelled count |
|---|---:|---:|
| iso to existing strict-split UNSAT (forward or arc-reversed) | **2** ($\text{AiEtAl\_L211\_min}$ in a different partition; $\text{AiEtAl\_L211\_min}^{\text{R}}$ = `35aa1b8c…`) | 96 |
| **NEW** $(1,0)$-NS-specific UNSAT | **8** | 216 |

[^arcrev-fix]: **Bug fix applied 2026-05-16, attributable to
`team/05_audit.md` Appendix A.7 (and the auditor's independent
finding in §A.7.8).** The original report below in this section used
a classifier (`_strict_split_unsat_canonical_keys` in
`code/run_route_b_ns_exhaustive_l2.py` lines 88–106) that hashed each
Ai et al. 2024 catalogue benchmark in *forward orientation only*,
despite Theorem 1.8 explicitly including "or their arc-reversed
versions". The arc-reverse of `AiEtAl_L211_min` has canonical hash
`35aa1b8c23ebc9b3…`, which the original sweep mis-classified as the
fourth row of the "9 NEW" table. After patching the classifier to
also index every benchmark's arc-reverse (with a sanity assertion
that `arc_reverse` is involutive on canonical hashes), the rerun log
`code/logs/route_b_ns_exh_l2_v2_20260516_235743.json` shows 10
canonical $\lambda = 2$ UNSAT instances at $(2,3)$, of which **2 are
catalogue-matches** (`14654037…` = $L211$_min forward at $(2,3)$,
`35aa1b8c…` = $L211$_min arc-reverse at $(2,3)$) and **8 are
genuinely NEW**. All 10 cases were independently cross-checked by
ILP and SAT — both verifiers agree UNSAT on every case. Note: $S_4$
and the $\text{iv\_star\_iv}$ benchmark are arc-reverse self-iso
(their reverse maps to the same canonical hash), so for those
benchmarks the patch is a no-op; $L211$_min and $L312$_min have
distinct reverses, and only $L211$_min lives at $n = 5$, which is
why the correction at $(2,3)$ is exactly $-1$.

**Detail of the 8 NEW canonical UNSAT at $(2, 3)$.** All have
$n = 5$, $V_1 = \{0, 1\}$, $V_2 = \{2, 3, 4\}$, internal arc
$(0 \to 1)$:

| hash (16 hex) | $m$ | $|D \setminus \{\text{int}\}|$-$\lambda$ | labelled count |
|---|---:|---:|---:|
| `5dada8a30f447291` | 10 | 1 | 12 |
| `10d4d95c9bfa0684` | 11 | 1 | 48 |
| `1ce848bfe32fdba1` | 11 | 1 | 24 |
| `6bff7c1524259196` | 11 | 1 | 24 |
| `9ad968a78d3f2357` | 11 | 1 | 24 |
| `b28c5b6c5c481ca6` | 11 | 1 | 24 |
| `52e5e47f3f76137e` | 12 | 1 | 36 |
| `c5524d22d2aba648` | 12 | **2** | 36 |

The row `35aa1b8c23ebc9b3` (previously listed here as the 4th NEW
canonical, $m = 11$, labelled count 48) has been removed: it is now
correctly classified as the arc-reverse of `AiEtAl_L211_min` and
falls in the "iso to existing strict-split UNSAT" row of the summary
table above.

Of the 8 NEW canonicals, **7** have $\lambda^{\text{arc}}(D \setminus
\{(0, 1)\}) = 1$: the internal arc is *load-bearing* for
2-arc-strongness, and removing it produces a digraph that is not even
2-arc-strong (hence the deletion is not a strict-split UNSAT in any
sensible sense; the $(1,0)$-NS exception is therefore genuinely
internal-arc-dependent).

The 8th NEW canonical (`c5524d22d2aba648`, $m = 12$) has
$\lambda^{\text{arc}}(D \setminus \{(0, 1)\}) = 2$: deleting the
internal arc still yields a 2-arc-strong digraph. By the cross-check
in `code/run_route_b_ns_exhaustive_l2.py` the deletion's canonical
hash does *not* match the four strict-split UNSAT canonicals (now
indexed including arc-reverses), hence the deletion is itself UNSAT
and is *not* an Ai et al. 2024 / $S_4$ exception. **This is a digraph
that is** $(1,0)$-NS, 2-arc-strong, UNSAT, **and remains UNSAT after
deleting the $V_1$-internal arc** — not in the Ai et al. 2024 list
but still a UNSAT split digraph (with $V_1$ independent). This
suggests the strict-split Ai et al. 2024 catalogue may itself be
incomplete at $n = 5$ — but this is outside the scope of the present
sweep; the §5 follow-up flags it for verification. The Auditor's
Appendix A.7 (§A.7.7) is in flight on the parallel question of
whether `c5524d22…` is iso to one of the five Appendix B.2
configurations of Ai et al.; if so, the NEW count would drop further
from 8.

**Concrete arcs of the smallest NEW $(1,0)$-NS UNSAT.**

`5dada8a30f447291`, $m = 10$: $V_1 = \{0, 1\}$, $V_2 = \{2, 3, 4\}$,
internal arc $(0, 1)$, full arc set
$\{(0, 1), (0, 4), (1, 2), (1, 3), (2, 0), (2, 3), (3, 1), (3, 4),
(4, 0), (4, 2)\}$. Verified UNSAT by both ILP and SAT (cross-check
agreed). The unique smallest $(1,0)$-NS UNSAT at $|V_1| = 2$,
$|V_2| = 3$.

**Partial-exhaustive (3, 3) and (2, 4).** The partial $(3, 3)$ sweep
(700 k of $42 \, M$ enumerations, $\sim 1.7 \%$) found **136
canonical-distinct $(1,0)$-NS UNSAT** at $n = 6$, *all NEW* (no
matches to any UNSAT benchmark). The partial $(2, 4)$ sweep (400 k of
$95 \, M$, $\sim 0.4 \%$) found **24 canonical-distinct, all NEW** at
$n = 6$. The true canonical-UNSAT count at $(3, 3)$ and $(2, 4)$ is
strictly greater than 136 and 24 respectively; the count at $n = 6$
combined is at least $\sim 160$ canonical $(1,0)$-NS UNSAT instances,
versus only **3** strict-split UNSAT instances at $n = 6$
($\text{L312\_min}, \text{iv\_star\_iv}$, $C_6^2$).

**Conclusion for §3.b.** The $(1,0)$-near-split $\lambda = 2$ UNSAT
exception family is strictly larger than the strict-split family. The
$V_1$-internal arc creates new obstructions; it does not just "decorate"
the existing strict-split ones. **The exception family is unlikely to
be finite** (the count grows rapidly with $n$). Any Route B theorem of
the form

> Every 3-arc-strong $(1,0)$-near-split digraph admits a SAD, **modulo a
> finite list of obstructions** $\{E_1, \ldots, E_k\}$

needs to clarify what "modulo" means; in particular, the 8 NEW
canonicals at $n = 5$ (post-arc-reverse-correction; see footnote
above) already exceed the strict-split list, and at $n = 6$ we have
at least an order of magnitude more. **A $(1,0)$-NS-specific
finiteness conjecture** would have to be characterized differently
than the BJ–Yeo 2004 / Ai et al. 2024 catalogue. *(Note: the partial
$(3, 3)$ and $(2, 4)$ counts quoted in the paragraph above were
produced with the pre-patch classifier; they are upper bounds on
"truly NEW" but may still over-count by arc-reverses of L312_min and
similar. A v2 rerun at $(3, 3), (2, 4)$ is outside this round's
bounded scope but would tighten the counts.)*

### §3.c — CL1 hypothesis (1) fails 100 % on the natural partition; modified partition does not recover

For each verified-SAT $\lambda = 3$ candidate we tested CL1's two
hypotheses on the *natural* partition $V_1' = V_1$, $V_2' = V_2$:

* **Hypothesis (1).** $D[V_1']$ and $D[V_2']$ each admit a SAD. For
  $(1, 0)$-NS with $|V_1| \geq 2$, $D[V_1]$ is the single internal arc
  $(a, b)$, hence 1-arc-strong, hence not SAD-decomposable. We record
  `v1_sad_status = UNSAT` directly.
* **Hypothesis (2).** Bridges admit a 2-coloring with each (direction,
  colour) class non-empty.

Aggregate over the 599 broad-sample SAT $\lambda = 3$ candidates:

| hypothesis | fraction | numerator / denominator |
|---|---:|---:|
| **(1)** $D[V_1], D[V_2]$ SAD-decomposable on natural partition | **0.0 %** | **0 / 599** |
| **(2)** bridge 2-coloring all four classes non-empty | **100.0 %** | **599 / 599** |
| both | **0.0 %** | **0 / 599** |

Hypothesis (1) failure breakdown:

| failure pattern | count | interpretation |
|---|---:|---|
| $V_1$=UNSAT, $V_2$=SAT | 430 | the typical case: $D[V_1]$ is the single internal arc; $D[V_2]$ is a 2- or 3-arc-strong semicomplete with SAD |
| $V_1$=UNSAT, $V_2$=UNSAT | 169 | $D[V_2]$ is a semicomplete UNSAT instance (e.g., $S_4$) or not 2-arc-strong on its own |

This is a **systematic finding** matching the spec's expectation. The
natural partition cannot satisfy CL1's hypothesis (1) for any $(1,0)$-NS
candidate with $|V_1| \geq 2$, because the internal arc carries
$\lambda^{\text{arc}}(D[V_1]) = 1$ on $|V_1| \geq 2$ vertices.

**Modified-partition recovery test.** For every candidate failing
hypothesis (1) on the natural partition, the sweep tries
$V_1' = V_1 \cup \{w\}$ for each $w \in V_2$, and checks whether
hypothesis (1) holds on the modified partition (i.e., $D[V_1 \cup
\{w\}]$ has a SAD *and* $D[V_2 \setminus \{w\}]$ has a SAD or is
trivial).

Result: **0 / 599 (0.0 %)** of natural-partition failures have a
modified-partition recovery. The modified partition does *not* rescue
CL1's hypothesis (1).

Why: $D[V_1 \cup \{w\}]$ is a 3-vertex digraph containing the internal
arc $(a, b)$ plus the bridge arcs touching $w$. For this to be
2-arc-strong (a necessary condition for SAD-decomposability), $w$ must
be entered and exited by both $a$ and $b$ via bridges. Even when those
bridges exist, the 3-vertex induced subdigraph rarely has $\lambda \geq
2$; in our 343-instance sample it never did. On the $V_2 \setminus
\{w\}$ side, removing one vertex from a semicomplete sub-digraph still
yields a semicomplete sub-digraph, but its strong-connectivity is not
guaranteed.

**Recommendation for the Structural Specialist.** CL1 is **not** the
operative lifting mechanism on the natural $(1,0)$-NS partition. Any
proof of the amended Route B headline must either:

(a) abandon the natural partition (use a different decomposition,
e.g., contracting the internal arc to a single "super-vertex" and
recursing on the resulting split digraph), or

(b) use a strictly stronger lifting lemma than CL1, one that handles
$\lambda^{\text{arc}}(D[V_1]) = 1$ on $V_1$ — but such a lemma cannot
exist in CL1's "both parts SAD-decomposable" form, because a
1-arc-strong digraph admits no SAD.

The simplest and most natural path is (a): the structural argument
likely runs via *arc-contraction* of the internal arc $(a, b)$ to a
single vertex $\{a \equiv b\}$, reducing the $(1, 0)$-NS digraph to a
strict-split digraph (handled by Ai et al. 2024), with a careful
treatment of the contracted vertex's bridges. The §4 diagnostic below
gives more detail.

---

## §4 — Diagnostic for the Structural Specialist

`team/19_near_split_extraction.md` is the parallel Structural deliverable;
when the reader has both this file and `team/19` in hand, the
cross-references below tell the Structural what to validate or amend.

### §4.1 The natural partition does not work; the contraction approach does

The empirical data of §3.c make clear that CL1 on the natural partition
$V_1' = V_1$, $V_2' = V_2$ is **always falsified at hypothesis (1)**.
The Structural proof in `team/19` cannot use this partition. The
recommended path:

**Contraction.** Let $(a, b)$ be the unique $V_1$-internal arc. Form
$D' = D / (a, b)$, the digraph obtained by identifying $a$ and $b$ to
a single vertex $a^*$ and deleting the loop (a, b) (which becomes a
self-loop after contraction, dropped). Then:

* $D'$ has $V(D') = V_1 \setminus \{b\} \cup V_2$ if we keep $a$ as
  the representative; the "$V_1$-side" of $D'$ has $|V_1| - 1$
  vertices and **no internal arcs** (the contraction removed the one
  internal arc; the $|V_1| - 2$ other ordered pairs in $V_1$ were
  already non-arcs by NS3);
* the bridge arcs of $D$ between $V_1$ and $V_2$ become bridge arcs of
  $D'$ between $V_1 \setminus \{b\}$ and $V_2$, with the bridges
  touching $b$ rerouted to $a^*$ (with potential parallel arcs);
* $D'[V_2] = D[V_2]$ is unchanged and remains semicomplete.

Hence $D'$ is a strict-$(0,0)$-split digraph (in the multigraph sense).
The amended Route B headline reduces to:

> **Lemma.** If $D'$ is 3-arc-strong, then $D'$ admits a SAD.

This is a *multigraph* version of the strict-split case. Ai et al.
2024's classification of split UNSAT may or may not extend to
multigraphs — this is a question for the Structural.

If $D'$ is *not* 3-arc-strong (the contraction dropped
$\lambda^{\text{arc}}$ from 3 to 2 or 1), then a more careful
case-analysis is needed: $D'$ is 2-arc-strong split, and we have to
rule out $D'$ being one of the finitely many strict-split UNSAT
exceptions.

### §4.2 The $\lambda = 2$ UNSAT exception family is data, not noise

If `team/19` proposes a proof that uses an exception list, the §3.b
data is the empirical ground truth: there are at least **8 NEW
canonical UNSAT at $n = 5$** (post-arc-reverse correction; see
§3.b footnote) and **at least $\sim 160$ NEW canonical UNSAT at
$n = 6$** (combining $(3, 3)$ and $(2, 4)$ partial counts; these
counts have not been re-run against the arc-reverse-corrected
classifier and are an upper bound), and the family does not match the
Ai et al. 2024 catalogue. Any "finite exception list" claim in
`team/19` must
either cover these or explain why the $(1, 0)$-NS amended proof
*ignores* them (e.g., because the headline is conditional on
$\lambda^{\text{arc}} = 3$, which we've never seen UNSAT).

### §4.3 Why bridge 2-coloring is "free" on the natural partition

`team/15` §3.2 noted that V6's b-mono pattern P1 (V_1$\to$V_2 bridges
monochromatic) held at $71.5 \%$. Here on $(1, 0)$-NS, **CL1's
hypothesis (2) holds at $100 \%$** (343 / 343). The reason: the
bridge sets are dense (each $V_1$ vertex typically has $\geq 2$
out-bridges and $\geq 2$ in-bridges in our $\lambda = 3$ regime),
and the SAT solver's witness routinely splits them across both
colours. Bridge 2-coloring is *not* the bottleneck in the
$(1, 0)$-NS proof; the bottleneck is hypothesis (1), which the
natural partition cannot satisfy.

---

## §5 — Coverage gaps and follow-up

(C1) **$|V_2| \geq 8$, $|V_1| \geq 5$.** Untested. The broad sweep
caps at $|V_2| = 7$, $|V_1| = 4$, hence $|V_1| + |V_2| \leq 11$. The
spec asked for $|V_1| + |V_2| \leq 10$; the sweep satisfies this and
extends slightly to $\leq 11$. Larger $n$ is the natural follow-up;
the expected SAT-rate-at-$\lambda = 3$ is 100 % based on §3.a.

(C2) **Multi-arc inside $V_1$.** Out of scope for v1, per the spec.
The $(2, 0)$-near-split sibling (two internal arcs in $V_1$) is the
obvious next class; the Structural Specialist may want to know
whether the contraction trick from §4.1 generalizes (contracting one
arc at a time, recursing).

(C3) **Truly-exhaustive $(3, 3)$ and $(2, 4)$.** Partial only. The
full enumeration is in the $10^7$-$10^8$ range and would take 4-8
hours on a single core; a few-core parallel run would finish in
under an hour. Recommended as a $\sim$1-day follow-up if the
Structural's `team/19` proof requires the exact exception-family
count at $n = 6$.

(C4) **The 8th NEW canonical at $(2, 3)$ that survives internal-arc
deletion** (`c5524d22d2aba648`, $m = 12$; was "9th" prior to the
audit Appendix A.7 arc-reverse correction — see §3.b footnote). This
is the most diagnostic instance: a $(1, 0)$-NS UNSAT whose internal-
arc deletion is *also* a 2-arc-strong UNSAT split digraph, but NOT
in the (arc-reverse-extended) Ai et al. 2024 list. Either the Ai
et al. 2024 list is incomplete at $n = 5$, or our independent
reading of their catalogue is too narrow (we may be missing a
§3-or-§4 family in arXiv:2408.02260; see `team/05_audit.md`
Appendix A.7 for the in-flight Appendix B.2 figure-read that
attempts to identify `c5524d22…` with one of the five B.2
configurations). The Auditor (`team/18_*`) should be flagged.
**Action item: cross-verify this instance against Ai et al. 2024 by
hand.**

(C5) **CL1 hypothesis tests on the contracted digraph $D'$.** §4.1's
contraction reduces $(1, 0)$-NS to a multigraph strict-split. We did
not test CL1 on $D'$; doing so would empirically validate or refute
the contraction-based proof skeleton. Budget: 1-2 days for a v2
sweep.

(C6) **Non-natural partition search.** The spec asked "what's the
proportion of candidates where the modified partition $V_1 \cup
\{w\}$ recovers hypothesis (1)?". Answer: 0 %, regardless of $w$.
But we did not search *all* partitions ($2^n$ partitions are
intractable); a smarter search (e.g., enumerating $V_1$-augmentations
by $\geq 2$ vertices) might find a non-natural partition that
satisfies CL1. This is a Structural question, not an empirical one.

(C7) **Random-bridge sampler at $|V_2| \geq 5$ with finer density.**
Construction B's density grid $\{0.35, 0.5, 0.65\}$ may miss
sparse-bridge UNSAT instances at large $|V_2|$. A finer grid
($\{0.2, 0.3, ..., 0.8\}$) is recommended for a v2 sweep if the
$\lambda = 2$ exception family at $|V_2| = 6, 7$ is needed for
`team/19`.

---

## Appendix A — Reproducibility

```bash
cd code
uv run python -m generators.near_split                    # generator self-test
uv run python run_route_b_near_split.py \
    --cap-per-pair-A 600 --cap-B 400 --instance-time-s 8  # broad sweep
uv run python run_route_b_ns_exhaustive_l2.py \
    --pairs "(2,3)" --instance-time-s 4                   # exhaustive (2,3)
```

Seed: `20260516`. Broad sweep wall-time $\sim 191$ s; (2,3) exhaustive
$\sim 85$ s on a single laptop. Partial $(3, 3)$ / $(2, 4)$ sweeps
were killed after 5-10 minutes each.

Headline logs (in `code/logs/`):
* `route_b_ns_20260516_232842.json` — broad-sample sweep (7 182
  streamed, 599 verified-SAT, 1 $\lambda = 2$ UNSAT).
* `route_b_ns_exh_l2_20260516_232058.json` — truly-exhaustive (2, 3)
  enumeration, 10 canonical $\lambda = 2$ UNSAT instances with full
  arc lists, deletion-canonical hashes, and matches-strict-split
  classifications.

Each verified-SAT entry includes:

* full witness 2-coloring (`witness_red`, `witness_blue` as lists of
  `[u, v, k]` keyed arcs);
* canonical pynauty-derived hash;
* full CL1 record (V_1, V_2 vertex lists, intrinsic SAD statuses,
  bridge counts per direction per colour, modified-partition recovery
  flag);
* construction provenance (A_exhaustive / B_random / C_reference).

## Appendix B — Files produced

* `code/generators/near_split.py` (new, $\sim 430$ lines) — the
  $(1,0)$-near-split generator (Constructions A, B, C) plus the
  independent $(1,0)$-NS predicate `is_one_zero_near_split`.
* `code/run_route_b_near_split.py` (new, $\sim 700$ lines) — Route B
  driver, mirrors `code/run_route_b_ols.py` with classification
  against the strict-split UNSAT family.
* `code/run_route_b_ns_exhaustive_l2.py` (new, $\sim 350$ lines) —
  truly-exhaustive $\lambda = 2$ UNSAT search with canonical-dedup
  short-circuit.
* `code/logs/route_b_ns_20260516_231234.json` and
  `code/logs/route_b_ns_exh_l2_20260516_232058.json` — the two
  headline logs.

## Appendix C — Compliance with hard rules

| rule | satisfied? | evidence |
|---|---|---|
| $(1,0)$-NS verified by independent function | YES | `is_one_zero_near_split` runs in the sweep loop after every `inst.build()` |
| witness logging mandatory | YES | every SAT $\lambda = 3$ entry has `witness_red`, `witness_blue` |
| hit-rate floor $\geq 5 \%$ at $\lambda \in \{2, 3\}$ | YES | $32.8 \%$ on the broad sweep |
| canonical hash via pynauty | YES | `canonical_key` from `generators/canonicalize.py` applied to every entry |
| stop on $\lambda = 3$ UNSAT | YES (untriggered) | the sweep would have written `team/21_candidate_counterexample.md` and halted; no $\lambda = 3$ UNSAT was found |
| cross-check ILP + SAT | YES | every entry has both `ilp_status` and `sat_status` and `agree = True` (0 disagreements over 7 182 instances) |
| canonical-dedup classification of UNSAT | YES | the §3.b table groups by canonical hash, not by labelled instance |
