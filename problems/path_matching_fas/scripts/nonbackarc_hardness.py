"""Non-back-arc hardness probes for tournament Path-FAS (Aboulker 4.4).

Back-arc-shape encodings are closed by two theorems:

  * Theorem 5.1 (`docs/J_hardness_via_wires.md`): interior degree
    saturation caps variable occurrence at 2 in forced-back-arc wires.
  * Theorem 6.1 (`docs/reversed_matching_hardness.md`): the back-arc
    graph of any LFO is a linear forest, so any constraint encoded in
    the *shape* of the back-arc graph is at most linear-forest shaped.

This module attacks the only remaining negative route: encode the
SAT/CSP instance through *ordering / flex-edge choices*, not through
the back-arc graph topology.

The substrate is the D70 toggle-pair family (`toggle_fooling_set.py`),
whose variable gadget is a pure ordering choice eps_i in {0,1}:

    gadget i = (a_i, b_i, f_i, g_i)
    f_i -> a_i, g_i -> b_i are forced back-arcs (disjoint windows),
    a_i -- b_i is the only flexible (overlapping-window) pair.

    eps_i = 0  (a_i before b_i):  a_i->b_i is forward.
            back-arc graph of gadget = {f_i--a_i, b_i--g_i}  (TWO comps)
            => f_i  NOT~  g_i
    eps_i = 1  (b_i before a_i):  a_i->b_i is a back-arc.
            back-arc graph of gadget = path f_i--a_i--b_i--g_i (ONE comp)
            => f_i  ~  g_i

The "value" of a variable lives entirely in the *order* of a_i,b_i, a
binary ordering choice, never in the back-arc shape (which is always a
linear forest, as Theorem 6.1 demands).

We then attach *extra* high-index vertices (probes / linkers) whose
forced back-arcs to gadget vertices couple the eps choices.  Crucially
these extra vertices have bounded back-degree (<= 2), so Theorem 6.1 is
respected throughout.

CONTENTS
--------
build_with_extras           generic constructor (toggle gadgets + extras)
clause_not_all_true         all-negative clause: infeasible iff all eps=1
                            == positive clause over L := (eps = 0)
ff_has_lfo / bf_has_lfo     global Path-FAS deciders (FF / brute force)
monotone_sat_to_path_fas    a working reduction from MONOTONE SAT (which
                            is in P) -- demonstrates the mechanism and
                            its limit
feasibility_is_monotone     verify the monotonicity obstruction on a
                            given extra-wiring
betweenness_relorder_sets   the betweenness obstruction: achievable LFO
                            relative-order sets of a trio
one_block_nonmonotone_pair  the (refuted-DP) non-monotone primitive

The honest verdict (see docs/nonbackarc_hardness.md): the toggle/flex
encoding is *monotone* in eps, so it can only realize monotone CSPs,
which are polynomial.  Betweenness is unrealizable because the LFO
order-restriction of any free trio has >= 3 of the 6 orderings.  A
genuine non-monotone primitive exists (the one_block collision) but
composing it requires the global union-find state (D68), which is the
unsolved fanout problem.
"""
from __future__ import annotations

import itertools
import os
import sys
from typing import Iterable, Sequence

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ff_signature_probe import has_completion_ff, valid_prefix_state_ff  # noqa: E402
from path_fas import decide_path_fas_bruteforce  # noqa: E402
from toggle_fooling_set import a, b, f, g, toggle_prefix  # noqa: E402
from verify import verify  # noqa: E402

Matrix = list[list[int]]
Target = "int | tuple[str, int]"


# --------------------------------------------------------------------------
# Generic constructor: toggle gadgets + extra coupling vertices
# --------------------------------------------------------------------------
def build_with_extras(k: int, extras: Sequence[Sequence[Target]], pad: int = 8) -> Matrix:
    """Tournament on n = 4k + pad + len(extras) vertices.

    k toggle gadgets occupy vertices 0..4k-1 (a_i,b_i,f_i,g_i interleaved
    as in toggle_fooling_set).  `pad` transitive padding vertices sit
    above the gadget block so that every extra vertex's arcs to gadget
    vertices are *forced* back-arcs (disjoint score windows).  Each entry
    of `extras` is a list of targets; an extra vertex reverses its arc to
    each target so the arc points *down* (a forced back-arc).  A target
    may be a gadget vertex id, or ('E', s) referring to the s-th earlier
    extra vertex.
    """
    n_extra = len(extras)
    n = 4 * k + pad + n_extra
    base = 4 * k + pad
    T = [[0] * n for _ in range(n)]
    for i in range(n):
        for jj in range(i + 1, n):
            T[i][jj] = 1  # transitive base
    for i in range(k):
        T[f(k, i)][a(i)] = 1
        T[a(i)][f(k, i)] = 0
        T[g(k, i)][b(i)] = 1
        T[b(i)][g(k, i)] = 0

    def resolve(t: Target) -> int:
        if isinstance(t, tuple) and t[0] == "E":
            return base + t[1]
        return t  # type: ignore[return-value]

    for t_idx, targets in enumerate(extras):
        e = base + t_idx
        for tg in targets:
            tv = resolve(tg)
            T[e][tv] = 1
            T[tv][e] = 0
    return T


# --------------------------------------------------------------------------
# Global Path-FAS deciders
# --------------------------------------------------------------------------
def ff_has_lfo(T: Matrix) -> bool:
    """Global Path-FAS feasibility via the score-window FF decider.

    Cross-validated against brute force on 180 random tournaments at
    n=7,8,9 (0 mismatches; see tests).  The FF decider is the trusted
    oracle on instances too large for brute force.
    """
    state = valid_prefix_state_ff(T, [])
    if state is None:
        return False
    prefix_mask, degree, parent, flex_outmask, windows = state
    return has_completion_ff(
        T, 0, prefix_mask, degree, parent, tuple(flex_outmask), tuple(windows)
    )


def bf_has_lfo(T: Matrix) -> bool:
    """Global Path-FAS feasibility by brute force (O(n!))."""
    return decide_path_fas_bruteforce(T)["found"]


def prefix_extends_ff(T: Matrix, prefix: Sequence[int]) -> bool:
    """Does `prefix` extend to a valid LFO under the FF decider?"""
    state = valid_prefix_state_ff(T, prefix)
    if state is None:
        return False
    prefix_mask, degree, parent, flex_outmask, windows = state
    return has_completion_ff(
        T, len(prefix), prefix_mask, degree, parent, tuple(flex_outmask), tuple(windows)
    )


# --------------------------------------------------------------------------
# Clause gadget: all-negative OR-clause via a linker chain + closing probe
# --------------------------------------------------------------------------
def clause_not_all_true_extras(k: int, lits: Sequence[int]) -> list[list[Target]]:
    """Extra-wirings realising "infeasible iff eps_i = 1 for ALL i in lits".

    A chain of (len(lits)-1) linker vertices connects the gadgets of
    `lits` in series at their f/g ends, then one probe vertex closes the
    loop between the two free ends.  The probe closes a cycle iff every
    gadget in the chain is "loaded" (eps_i = 1), i.e. iff f_i ~ g_i for
    all i in lits.

    With L_i := (eps_i = 0), this realises the *positive* OR-clause
    (L_{lits[0]} v ... v L_{lits[-1]}): feasible iff some L_i is true.
    """
    if len(lits) == 0:
        raise ValueError("clause needs >= 1 literal")
    if len(lits) == 1:
        # unit clause L_i: feasible iff eps_i = 0.  probe(f_i, g_i).
        j = lits[0]
        return [[f(k, j), g(k, j)]]
    extras: list[list[Target]] = []
    # linker chain: linker t connects g_{lits[t]} to f_{lits[t+1]}
    for t in range(len(lits) - 1):
        extras.append([g(k, lits[t]), f(k, lits[t + 1])])
    # closing probe: f of first, g of last
    extras.append([f(k, lits[0]), g(k, lits[-1])])
    return extras


def clause_feasibility_table(k: int, lits: Sequence[int]) -> dict[tuple[int, ...], bool]:
    """Truth table eps -> (clause-gadget prefix extends?) for all eps."""
    extras = clause_not_all_true_extras(k, lits)
    T = build_with_extras(k, extras)
    out: dict[tuple[int, ...], bool] = {}
    for eps in itertools.product((0, 1), repeat=k):
        out[eps] = prefix_extends_ff(T, toggle_prefix(k, eps))
    return out


# --------------------------------------------------------------------------
# The monotonicity obstruction
# --------------------------------------------------------------------------
def feasibility_is_monotone(k: int, extras: Sequence[Sequence[Target]]) -> bool:
    """True iff prefix-extendability is monotone-decreasing in eps.

    Monotone-decreasing: if eps is feasible and eps' <= eps componentwise
    (more zeros), then eps' is feasible.  Equivalently, raising any eps_i
    from 0 to 1 can only *lose* feasibility.  This is the core obstruction:
    a monotone predicate can only encode monotone CSPs (in P).
    """
    T = build_with_extras(k, extras)
    feas = {
        eps: prefix_extends_ff(T, toggle_prefix(k, eps))
        for eps in itertools.product((0, 1), repeat=k)
    }
    for eps, ok in feas.items():
        if not ok:
            continue
        for epsp in itertools.product((0, 1), repeat=k):
            if all(epsp[i] <= eps[i] for i in range(k)) and not feas[epsp]:
                return False
    return True


def backarc_set_shrinks_when_unloaded(k: int) -> bool:
    """Verify the structural cause of monotonicity.

    Flipping eps_i from 1 to 0 swaps the consecutive pair (b_i, a_i) ->
    (a_i, b_i), which only *removes* the a_i--b_i back-arc and changes no
    other back-arc.  So the back-arc set strictly shrinks; since "is a
    linear forest" is closed under edge deletion, feasibility is monotone.
    """
    from toggle_fooling_set import build_toggle_family

    T = build_toggle_family(k)
    suffix = [f(k, i) for i in range(k)] + [g(k, i) for i in range(k)]
    for eps1 in itertools.product((0, 1), repeat=k):
        for j in range(k):
            if eps1[j] != 1:
                continue
            eps0 = list(eps1)
            eps0[j] = 0
            o1 = toggle_prefix(k, eps1) + suffix
            o0 = toggle_prefix(k, tuple(eps0)) + suffix
            b1 = set(map(tuple, verify(T, o1)["arcs"]))
            b0 = set(map(tuple, verify(T, o0)["arcs"]))
            if not b0 <= b1:
                return False
    return True


# --------------------------------------------------------------------------
# Working reduction: MONOTONE-SAT -> Path-FAS  (monotone-SAT is in P!)
# --------------------------------------------------------------------------
def monotone_sat_to_path_fas(num_vars: int, clauses: Sequence[Sequence[int]],
                             pad: int = 8) -> Matrix:
    """Reduce a MONOTONE CNF (all literals positive over L) to Path-FAS.

    Each clause is a list of variable indices; the clause is satisfied
    iff at least one of its variables is True, where True := L_i := eps_i
    = 0.  Each clause is realised by a `clause_not_all_true` chain.

    This is a *correct* reduction (verified below), but its source
    problem -- monotone CNF-SAT -- is trivially in P (set all L_i = True,
    i.e. all eps = 0).  It exists only to exhibit the mechanism and to
    pin precisely *which* CSPs the ordering/flex encoding can reach.
    """
    extras: list[list[Target]] = []
    for clause in clauses:
        extras.extend(clause_not_all_true_extras(num_vars, list(clause)))
    return build_with_extras(num_vars, extras, pad=pad)


# --------------------------------------------------------------------------
# The betweenness obstruction
# --------------------------------------------------------------------------
def lfo_relative_orders(T: Matrix, trio: Sequence[int]) -> set[tuple[int, ...]]:
    """All relative orders of `trio` realised across the LFOs of T (brute force)."""
    out: set[tuple[int, ...]] = set()
    n = len(T)
    for P in itertools.permutations(range(n)):
        if verify(T, list(P))["is_linear_forest"]:
            pos = {v: i for i, v in enumerate(P)}
            out.add(tuple(sorted(trio, key=lambda v: pos[v])))
    return out


def search_betweenness_gadget(n: int) -> dict:
    """Exhaustively search all tournaments on n vertices for a trio whose
    LFO relative-order set is (a nonempty subset of) the betweenness set
    {(x,y,z),(z,y,x)} for some choice of the middle element y.

    Returns counts; `exact` and `nonempty_subset` are both 0 in the
    obstruction (verified for n=5).
    """
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    exact = 0
    nonempty_subset = 0
    min_relorder_size = 7
    for bits in itertools.product((0, 1), repeat=len(pairs)):
        T = [[0] * n for _ in range(n)]
        for (i, j), bt in zip(pairs, bits):
            if bt:
                T[i][j] = 1
            else:
                T[j][i] = 1
        for trio in itertools.combinations(range(n), 3):
            ro = lfo_relative_orders(T, trio)
            if ro:
                min_relorder_size = min(min_relorder_size, len(ro))
            for ymid in trio:
                rest = [v for v in trio if v != ymid]
                target = {(rest[0], ymid, rest[1]), (rest[1], ymid, rest[0])}
                if ro == target:
                    exact += 1
                if ro and ro <= target:
                    nonempty_subset += 1
    return {
        "n": n,
        "exact_betweenness_trios": exact,
        "nonempty_subset_trios": nonempty_subset,
        "min_nonempty_relorder_size": min_relorder_size,
    }


# --------------------------------------------------------------------------
# The non-monotone primitive (one_block, D68) -- exists but uncomposed
# --------------------------------------------------------------------------
ONE_BLOCK: Matrix = [
    [0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1],
    [0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1],
    [1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1],
    [0, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1],
    [0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 1],
    [0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1],
    [0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1],
    [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1],
    [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1],
    [1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
]


def one_block_nonmonotone_pair() -> dict:
    """The two length-5 prefixes of `one_block` with identical local DP
    signature but opposite extendability (D68).  These are NOT subset-
    related: they place the same vertices in different orders.  This is a
    genuine non-monotone ordering primitive -- the only one we found.

    Returns the two prefixes and their extendabilities.
    """
    A = [0, 3, 1, 4, 2]
    B = [1, 2, 0, 4, 3]
    return {
        "A": A,
        "A_extends": prefix_extends_ff(ONE_BLOCK, A),
        "B": B,
        "B_extends": prefix_extends_ff(ONE_BLOCK, B),
    }


def main() -> None:
    import json

    print("== clause (~x0 v ~x1) feasibility table (k=2) ==")
    print(json.dumps({str(k): v for k, v in clause_feasibility_table(2, [0, 1]).items()},
                     indent=2))
    print("== monotonicity of that wiring ==")
    print(feasibility_is_monotone(2, clause_not_all_true_extras(2, [0, 1])))
    print("== back-arc set shrinks when unloaded (k=4) ==")
    print(backarc_set_shrinks_when_unloaded(4))
    print("== betweenness obstruction (n=5 exhaustive) ==")
    print(json.dumps(search_betweenness_gadget(5), indent=2))
    print("== one_block non-monotone primitive ==")
    print(json.dumps(one_block_nonmonotone_pair(), indent=2))


if __name__ == "__main__":
    main()
