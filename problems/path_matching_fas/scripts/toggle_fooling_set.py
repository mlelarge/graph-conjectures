"""Forward-DP lower bound via the toggle-pair fooling set (D70).

Section 16 of `docs/exchange_proof_draft.md` proves the *sleeping-block
signature* takes 2^(n/4) distinct values on the toggle-pair family.
This module strengthens that to a *fundamental* lower bound on any
forward score-window DP: the 2^k toggle prefixes are pairwise
**extension-distinguishable**.

Construction.  The toggle-pair family on n = 4k vertices (Section 16.1):

    a_i = 2i,      b_i = 2i+1         (i = 0..k-1)
    f_i = 2k+2i,   g_i = 2k+2i+1      (i = 0..k-1)

Base transitive orientation (u -> v iff u < v), then reverse exactly
the arcs f_i -> a_i and g_i -> b_i.  For k >= 4 these are forced
backedges (disjoint score windows).

Probe.  For a chosen gadget j, add one vertex z = 4k at the top and
reverse z -> f_j and z -> g_j.  Because z is the highest index, the
arcs from every prefix vertex a_i, b_i go a_i -> z, b_i -> z
(unchanged) — so adding the probe leaves every prefix vertex's
in-degree, hence its score window, unchanged.

Claim (fooling set).  With the probe at gadget j, the toggle prefix
P_eps extends to a valid LFO **iff eps_j = 0**:

  * eps_j = 1: the flexible edge a_j-b_j loads (b_j before a_j), so the
    gadget back-arc graph is the path f_j-a_j-b_j-g_j and f_j ~ g_j.
    The probe forces z -> f_j and z -> g_j, closing a cycle.  Infeasible.
  * eps_j = 0: f_j and g_j lie in different components; the probe joins
    them through z into a single path.  Feasible.

Since the prefix windows are probe-independent, two prefixes that differ
at gadget j are distinguished by the gadget-j probe.  Hence any forward
DP whose state is a function of the prefix needs >= 2^k = 2^(n/4)
states.  This subsumes the sleeping-block (Section 16), dormant-quotient
(D68), and sigma-trace (D69) signature failures: *every* forward
signature inherits this bound.

Consistency with D66.  The toggle family has |H| = 2k = n/2 forced
edges, so it lies in the large-|H| regime where the FPT-by-|H| theorem
(pw(J), tw(J) <= 8 + 2|H|) makes no polynomiality claim.  No
contradiction.
"""
from __future__ import annotations

import argparse
import itertools
import json
import os
import sys
from typing import Sequence

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ff_signature_probe import has_completion_ff, valid_prefix_state_ff  # noqa: E402


Matrix = list[list[int]]


def a(i: int) -> int:
    return 2 * i


def b(i: int) -> int:
    return 2 * i + 1


def f(k: int, i: int) -> int:
    return 2 * k + 2 * i


def g(k: int, i: int) -> int:
    return 2 * k + 2 * i + 1


def build_toggle_family(k: int) -> Matrix:
    """Base toggle-pair tournament on n = 4k vertices (Section 16.1)."""
    n = 4 * k
    T = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            T[i][j] = 1  # transitive base
    for i in range(k):
        # reverse f_i -> a_i
        T[f(k, i)][a(i)] = 1
        T[a(i)][f(k, i)] = 0
        # reverse g_i -> b_i
        T[g(k, i)][b(i)] = 1
        T[b(i)][g(k, i)] = 0
    return T


def build_toggle_with_probe(k: int, j: int, pad: int = 6) -> Matrix:
    """Toggle family with `pad` padding vertices above the f/g block and
    one probe vertex z at the very top reversing z -> f_j and z -> g_j.

    The padding pushes z's score window strictly above the windows of
    f_j and g_j, so that z -> f_j and z -> g_j become *forced* backedges
    (Section 16's disjoint-window criterion).  Padding vertices are
    transitive and sit above every gadget vertex, so they leave the
    in-degrees (hence score windows) of all prefix vertices a_i, b_i
    unchanged.  n = 4k + pad + 1."""
    n = 4 * k + pad + 1
    z = n - 1
    T = [[0] * n for _ in range(n)]
    for i in range(n):
        for jj in range(i + 1, n):
            T[i][jj] = 1
    for i in range(k):
        T[f(k, i)][a(i)] = 1
        T[a(i)][f(k, i)] = 0
        T[g(k, i)][b(i)] = 1
        T[b(i)][g(k, i)] = 0
    # probe reversals: z -> f_j, z -> g_j (z is highest index)
    T[z][f(k, j)] = 1
    T[f(k, j)][z] = 0
    T[z][g(k, j)] = 1
    T[g(k, j)][z] = 0
    return T


def toggle_prefix(k: int, eps: Sequence[int]) -> list[int]:
    """Prefix placing pair i as (a_i, b_i) if eps_i = 0 else (b_i, a_i)."""
    prefix: list[int] = []
    for i in range(k):
        if eps[i] == 0:
            prefix.extend([a(i), b(i)])
        else:
            prefix.extend([b(i), a(i)])
    return prefix


def prefix_extends(T: Matrix, prefix: Sequence[int]) -> bool:
    """Does the given prefix extend to a valid LFO of T (linear-forest
    back-arc graph) under the FF score-window decider?"""
    state = valid_prefix_state_ff(T, prefix)
    if state is None:
        return False
    prefix_mask, degree, parent, flex_outmask, windows = state
    return has_completion_ff(
        T,
        len(prefix),
        prefix_mask,
        degree,
        parent,
        tuple(flex_outmask),
        tuple(windows),
    )


def verify_fooling_set(k: int) -> dict:
    """For every gadget j and every toggle eps, check that P_eps extends
    in the probe-j tournament iff eps_j = 0.

    Returns a report; `fooling_set_holds` is True iff the claim holds for
    all (j, eps)."""
    violations: list[dict] = []
    checks = 0
    for j in range(k):
        T = build_toggle_with_probe(k, j)
        for eps in itertools.product((0, 1), repeat=k):
            prefix = toggle_prefix(k, eps)
            extends = prefix_extends(T, prefix)
            expected = (eps[j] == 0)
            checks += 1
            if extends != expected:
                if len(violations) < 5:
                    violations.append({
                        "probe_gadget": j,
                        "eps": list(eps),
                        "extends": extends,
                        "expected": expected,
                    })
    return {
        "k": k,
        "n_base": 4 * k,
        "n_with_probe": 4 * k + 1,
        "checks": checks,
        "violations": len(violations),
        "first_violations": violations,
        "fooling_set_holds": not violations,
        "distinguishable_prefixes": 2 ** k,
        "lower_bound": f"2^{k} = 2^(n/4)",
    }


def verify_prefix_windows_probe_invariant(k: int) -> dict:
    """Confirm that adding the probe z does not change the score window
    of any prefix vertex a_i, b_i (the fooling-set soundness condition).

    Compares score windows of prefix vertices between the base toggle
    family and the probe-j tournament for every j."""
    from lfo_score_window import score_windows  # noqa: E402

    base = build_toggle_family(k)
    base_win = score_windows(base)
    prefix_vertices = [a(i) for i in range(k)] + [b(i) for i in range(k)]
    mismatches: list[dict] = []
    for j in range(k):
        T = build_toggle_with_probe(k, j)
        win = score_windows(T)
        for v in prefix_vertices:
            if tuple(win[v]) != tuple(base_win[v]):
                mismatches.append({
                    "probe_gadget": j,
                    "vertex": v,
                    "base_window": list(base_win[v]),
                    "probe_window": list(win[v]),
                })
    return {
        "k": k,
        "prefix_vertices_checked": len(prefix_vertices),
        "mismatches": len(mismatches),
        "first_mismatches": mismatches[:5],
        "windows_invariant": not mismatches,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--k", type=int, default=4)
    parser.add_argument("--check-windows", action="store_true")
    args = parser.parse_args()
    if args.check_windows:
        print(json.dumps(verify_prefix_windows_probe_invariant(args.k), indent=2))
    print(json.dumps(verify_fooling_set(args.k), indent=2))


if __name__ == "__main__":
    main()
