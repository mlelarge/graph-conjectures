# Flower snarks $J_{2k+1}$ via weighted CDC — Phase 2 status

## Where we are

Per [cdc_gadget_plan.md](cdc_gadget_plan.md) §"Phase 2": find a
uniform parametric weighted-CDC certificate for the flower-snark
family, or sharply rule out the template.

Result so far (with the generic `find_cdc` backtracker enumerating the
short-cycle pool of each graph):

| Graph | CDC found by `find_cdc` | Weighted-CDC | $S^2$ verify |
|---|---|---:|:---:|
| $J_5$ | size 9, lens $\{5, 6^5, 7^2, 11\}$ | $\|F\|^2 = 1.1\times10^{-30}$ | ✓ |
| $J_7$ | size 9, lens $\{6, 9^2, 10^6\}$ | $\|F\|^2 = 1.36$ | ✗ |
| $J_9$ | not enumerated within 180 s | — | — |
| $J_{11}$ | not enumerated within 180 s | — | — |

$J_5$ alone is positive evidence; everything past it is currently
**inconclusive**, not negative. Two distinct issues:

1. **Cycle enumeration is the bottleneck** at $n \geq 18$. `cdc.py`'s
   `simple_cycles_undirected` walks `nx.simple_cycles` on the directed
   double, deduplicates, and feeds the backtracker. For $J_7$ the
   short-cycle pool blows up; for $J_9, J_{11}$ even the pool doesn't
   build inside the budget.
2. **The first CDC that comes out isn't necessarily the one a Sigma_4
   flow respects.** $J_7$'s found CDC (mostly length-10 cycles) does
   not admit a weighted-CDC solution; we don't yet know whether *any*
   CDC of $J_7$ does.

These are both engineering limitations of the generic backtracker, not
mathematical statements about the family.

## What's missing

A **structural** flower-snark CDC, written down explicitly as a
function of $k$, with cycle composition by edge type (spoke_b /
spoke_c / spoke_d / b_cycle / cd_cycle) chosen so that the resulting
weighted-CDC polynomial system is invariant under index rotation. The
$J_5$ CDC found by the backtracker has heterogeneous cycle types
($\{5, 6^5, 7^2, 11\}$) which is not obviously a $k$-parametric
template.

Structural CDCs for flower snarks exist in the literature
(Brinkmann/Goedgebeur's snark survey lists known CDCs for several
infinite families). The next step is to **transcribe one such CDC
explicitly** and feed it directly to `solve_weighted_cdc`, bypassing
the generic enumerator. Two natural candidates:

1. The "$2k+3$-cycle Isaacs CDC", consisting of the $b$-cycle (length
   $n$), the $cd$-cycle (length $2n$), and $2k+1$ short cycles of
   length 6 each at the spoke fans.
2. A "rotational" CDC built from the $\mathbb{Z}/n$ orbit of one base
   cycle through $a_0, b_0, c_0, d_0$.

If either CDC, fed into the weighted solver, yields a $k$-parametric
solution pattern, we have an infinite-family $S^2$-flow theorem for
flower snarks. If neither does, the weighted CDC abstraction is not
expressive enough for this family and the project should pivot to
gadget composition (Phase 3).

## Per-graph spot result (positive direction)

The Phase 1 verification already established (via
[tests/test_cdc_weighted.py](../tests/test_cdc_weighted.py)) that
$J_5$ admits a weighted-CDC $\Sigma_4$ flow, hence an $S^2$ flow.
Combined with the existing $n = 20$ catalogue result (all 6
nontrivial snarks at $n = 20$ have Krawczyk-certified $S^2$ flows),
$J_5$ is doubly certified.

## Hand-off

Phase 2 is unfinished. To finish it requires either:

- a structural CDC for $J_n$ transcribed from the literature and fed to
  `solve_weighted_cdc`, with a numerical k-parametric check across
  $n \in \{5, 7, 9, 11, 13\}$; or
- a faster cycle enumerator focused on the flower-snark vertex types
  (spoke fans + b-cycle + cd-cycle), so that `iter_cdcs` produces a
  diverse pool quickly.

Phase 3 (gadget composition) can be started in parallel; it does not
depend on the Phase 2 outcome.
