"""NP-hardness gadget verification toolkit for Path-FAS reduction.

This module is the verifier side of the joint Aboulker Problem 4.4
attack: the *reduction theorist* proposes variable / wire / clause
gadgets for a 1-in-3-SAT (or NAE-3SAT) -> Path-FAS reduction, and this
toolkit exhaustively checks their truth tables.

A *gadget* here is a tournament fragment T (an n x n 0/1 matrix, with
T[u][v] == 1 iff there is an arc u -> v), together with a tuple of
designated *port* vertices.  We verify a gadget by enumerating all
n! linear orderings, retaining those whose back-arc graph is a linear
forest (LFO), and aggregating an output tuple at the ports via a
caller-supplied semantic function.

Standard semantics ("placement-bit"): for a port pair (x, y) in an
ordering P, the port's bit is True iff y precedes x in P.  In
Section 16 / D6 the toggle "bit" for a single variable gadget is
bool(eps_i) := (b_i precedes a_i in P), read by
``placement_bit_first_pair_inversion``.

Key entry points:

- `enumerate_extendable_orderings(T)`     — all LFO orderings of T.
- `truth_table_from_gadget(...)`           — port truth table aggregator.
- `verify_variable_gadget(T, port)`        — 1-port truth table.
- `verify_clause_gadget(T, ports, mode)`   — 3-port, 1-in-3 or NAE.
- `minimal_obstruction_search(...)`        — shrink violating gadget.
- `gadget_compose(gadgets, cross_arcs)`    — compose tournaments.
- `enumerate_cross_arc_orientations(...)`  — sweep cross-arc choices.
- `cross_arc_audit(...)`                   — composition correctness sweep.

All enumerations are O(n!) in time and intended for n <= 10.  At
n >= 11 we refuse to enumerate by default, and the caller must pass
`allow_large=True` to override.

Trust root: every claim routes through `verify.verify(T, P)`.  We do
not re-implement back-arc classification.
"""
from __future__ import annotations

import math
import os
import sys
from collections import Counter
from itertools import permutations, product
from typing import Callable, Iterable, Iterator, Sequence

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from verify import verify  # noqa: E402

Matrix = list[list[int]]
Order = tuple[int, ...]
PortTuple = tuple[bool, ...]
TruthRow = tuple[PortTuple, int]


ENUMERATION_LIMIT = 10  # n! exhaustive enumeration cap


# ------------------------------------------------------------------
# 0. Sanity helpers
# ------------------------------------------------------------------


def _check_tournament(T: Sequence[Sequence[int]]) -> int:
    n = len(T)
    for u in range(n):
        if len(T[u]) != n:
            raise ValueError("T must be square")
        if T[u][u]:
            raise ValueError(f"self-loop at vertex {u}")
        for v in range(u + 1, n):
            a = bool(T[u][v])
            b = bool(T[v][u])
            if a == b:
                raise ValueError(
                    f"not a tournament at pair ({u}, {v}): "
                    f"T[u][v]={T[u][v]} T[v][u]={T[v][u]}"
                )
    return n


def _to_int_matrix(T: Sequence[Sequence]) -> Matrix:
    return [[1 if T[i][j] else 0 for j in range(len(T))] for i in range(len(T))]


# ------------------------------------------------------------------
# 1. Enumeration
# ------------------------------------------------------------------


def enumerate_extendable_orderings(
    T: Sequence[Sequence[int]],
    vertices_subset: Sequence[int] | None = None,
    allow_large: bool = False,
) -> list[Order]:
    """Return every ordering of `vertices_subset` (default: V(T)) whose
    back-arc graph (under the *induced sub-tournament* on the subset) is
    a linear forest.

    For `vertices_subset` strictly smaller than V(T), the induced
    sub-tournament is verified locally; the result is the set of LFOs of
    the *gadget restricted to that subset*, not of T.
    """
    T = _to_int_matrix(T)
    n = _check_tournament(T)
    if vertices_subset is None:
        vertices_subset = list(range(n))
    vs = list(vertices_subset)
    m = len(vs)
    if m > ENUMERATION_LIMIT and not allow_large:
        raise ValueError(
            f"refusing to enumerate {m}! = {math.factorial(m)} orderings; "
            f"pass allow_large=True to override"
        )

    if m == n:
        Tloc = T
        local_to_global = list(range(n))
    else:
        # Build induced sub-tournament; relabel ports to local indices.
        local_to_global = list(vs)
        idx = {v: i for i, v in enumerate(local_to_global)}
        Tloc = [[0] * m for _ in range(m)]
        for u_g in local_to_global:
            for v_g in local_to_global:
                if u_g != v_g and T[u_g][v_g]:
                    Tloc[idx[u_g]][idx[v_g]] = 1

    out: list[Order] = []
    for perm in permutations(range(m)):
        info = verify(Tloc, list(perm))
        if info["is_linear_forest"]:
            out.append(tuple(local_to_global[i] for i in perm))
    return out


# ------------------------------------------------------------------
# 2. Truth-table extractor
# ------------------------------------------------------------------


def placement_bit_first_pair_inversion(
    ordering: Sequence[int], port_pairs: Sequence[tuple[int, int]]
) -> PortTuple:
    """Standard port-bit semantic.

    Each port is a pair (x, y) of vertices; the port's bit is True iff
    y appears *before* x in `ordering` (the "inverted" placement).

    For the Section 16 toggle, the relevant pair is (a_i, b_i): bit 1
    corresponds to b_i appearing before a_i.
    """
    pos = {v: i for i, v in enumerate(ordering)}
    out = []
    for x, y in port_pairs:
        out.append(pos[y] < pos[x])
    return tuple(out)


def placement_bit_single(
    ordering: Sequence[int], ports: Sequence[int]
) -> PortTuple:
    """Trivial semantic: bit of a port is True iff the port sits in the
    *second half* of `ordering`.  Useful only as a baseline; prefer
    `placement_bit_first_pair_inversion` for real gadgets.
    """
    n = len(ordering)
    pos = {v: i for i, v in enumerate(ordering)}
    half = n / 2
    return tuple(pos[p] >= half for p in ports)


def truth_table_from_gadget(
    T: Sequence[Sequence[int]],
    port_vertices: Sequence,
    semantic_fn: Callable[[Order], PortTuple],
    vertices_subset: Sequence[int] | None = None,
    allow_large: bool = False,
) -> dict[PortTuple, int]:
    """Aggregate port-bit tuples over all LFOs of (T, vertices_subset).

    `port_vertices` is whatever shape `semantic_fn` expects (a flat
    list, a list of pairs, etc.).  We only forward it to `semantic_fn`.

    Returns a `dict {PortTuple: count}` covering exactly the keys that
    appear among LFOs.  Keys that do not appear have implicit count 0.
    """
    orderings = enumerate_extendable_orderings(
        T, vertices_subset=vertices_subset, allow_large=allow_large
    )
    counter: Counter[PortTuple] = Counter()
    for P in orderings:
        counter[semantic_fn(P)] += 1
    return dict(counter)


def full_truth_table(
    T: Sequence[Sequence[int]],
    port_vertices: Sequence,
    semantic_fn: Callable[[Order], PortTuple],
    width: int,
    vertices_subset: Sequence[int] | None = None,
    allow_large: bool = False,
) -> dict[PortTuple, int]:
    """Same as `truth_table_from_gadget` but pads the dict with all
    2^width keys, count 0 where absent.  Handy for equality checks
    against an expected truth table.
    """
    obs = truth_table_from_gadget(
        T, port_vertices, semantic_fn,
        vertices_subset=vertices_subset, allow_large=allow_large,
    )
    out: dict[PortTuple, int] = {}
    for bits in product((False, True), repeat=width):
        out[bits] = obs.get(bits, 0)
    return out


# ------------------------------------------------------------------
# 3. Variable / clause gadget shortcuts
# ------------------------------------------------------------------


def verify_variable_gadget(
    T: Sequence[Sequence[int]],
    port_pair: tuple[int, int],
) -> dict:
    """Verify a 1-port variable gadget against the standard
    `placement_bit_first_pair_inversion` semantic.

    Returns:
      {
        "truth_table": {(False,): k0, (True,): k1},
        "is_balanced": bool   # whether both port values are realized,
        "total_lfos": int,
      }
    """
    tt = full_truth_table(
        T, [port_pair],
        lambda P: placement_bit_first_pair_inversion(P, [port_pair]),
        width=1,
    )
    total = sum(tt.values())
    return {
        "truth_table": tt,
        "is_balanced": tt[(False,)] > 0 and tt[(True,)] > 0,
        "total_lfos": total,
    }


# 1-in-3-SAT allowed clause patterns: exactly one True among three.
ALLOWED_1IN3 = {
    (True, False, False),
    (False, True, False),
    (False, False, True),
}

# NAE-3SAT allowed clause patterns: not-all-equal among three.
ALLOWED_NAE3 = {
    bits for bits in product((False, True), repeat=3)
    if not (bits == (False, False, False) or bits == (True, True, True))
}


def verify_clause_gadget(
    T: Sequence[Sequence[int]],
    port_pairs: Sequence[tuple[int, int]],
    mode: str = "1in3",
) -> dict:
    """Verify a 3-port clause gadget against the standard semantic.

    `port_pairs` must have length 3.  `mode` is "1in3" or "nae3".

    Returns:
      {
        "truth_table": {bits: count for bits in {F,T}^3},
        "expected_allowed": set of allowed bits,
        "observed_allowed": set of bits actually realized,
        "missing": expected \\ observed (allowed but never realized),
        "spurious": observed \\ expected (realized but disallowed),
        "ok": missing == set() and spurious == set(),
      }
    """
    if len(port_pairs) != 3:
        raise ValueError("3-port clause gadget requires 3 port pairs")
    if mode == "1in3":
        allowed = ALLOWED_1IN3
    elif mode == "nae3":
        allowed = ALLOWED_NAE3
    else:
        raise ValueError(f"unknown mode {mode!r}; expected '1in3' or 'nae3'")

    tt = full_truth_table(
        T, list(port_pairs),
        lambda P: placement_bit_first_pair_inversion(P, list(port_pairs)),
        width=3,
    )
    observed = {bits for bits, c in tt.items() if c > 0}
    missing = allowed - observed
    spurious = observed - allowed
    return {
        "truth_table": tt,
        "expected_allowed": allowed,
        "observed_allowed": observed,
        "missing": missing,
        "spurious": spurious,
        "ok": not missing and not spurious,
    }


# ------------------------------------------------------------------
# 4. Minimal obstruction search
# ------------------------------------------------------------------


def minimal_obstruction_search(
    T: Sequence[Sequence[int]],
    target_property: Callable[[Sequence[Sequence[int]]], bool],
    keep_vertices: Sequence[int] = (),
    allow_large: bool = False,
) -> dict:
    """Shrink T to a minimum induced sub-tournament still satisfying
    `target_property` (a predicate on tournament matrices).

    `keep_vertices` is a set of vertices that must remain in every
    candidate sub-tournament (e.g. port vertices).

    Returns {"vertices": ..., "matrix": ..., "size": ...}, or None if
    no sub-tournament satisfies the property.
    """
    T = _to_int_matrix(T)
    n = _check_tournament(T)
    keep = set(keep_vertices)
    if not target_property(T):
        return None
    if n > ENUMERATION_LIMIT and not allow_large:
        raise ValueError(
            f"refusing to search 2^{n} subsets; pass allow_large=True"
        )

    candidates: list[tuple[int, list[int]]] = []
    rest = [v for v in range(n) if v not in keep]
    for mask in range(1 << len(rest)):
        verts = sorted(keep | {rest[i] for i in range(len(rest)) if (mask >> i) & 1})
        if len(verts) < max(1, len(keep)):
            continue
        idx = {v: i for i, v in enumerate(verts)}
        sub = [[0] * len(verts) for _ in verts]
        for u in verts:
            for v in verts:
                if u != v and T[u][v]:
                    sub[idx[u]][idx[v]] = 1
        if target_property(sub):
            candidates.append((len(verts), verts))
    if not candidates:
        return None
    candidates.sort(key=lambda x: x[0])
    size, verts = candidates[0]
    idx = {v: i for i, v in enumerate(verts)}
    sub = [[0] * size for _ in range(size)]
    for u in verts:
        for v in verts:
            if u != v and T[u][v]:
                sub[idx[u]][idx[v]] = 1
    return {"vertices": verts, "matrix": sub, "size": size}


# ------------------------------------------------------------------
# 5. Composition
# ------------------------------------------------------------------


def gadget_compose(
    gadgets: Sequence[Sequence[Sequence[int]]],
    cross_arcs: dict[tuple[tuple[int, int], tuple[int, int]], int],
) -> Matrix:
    """Compose `gadgets` into one tournament.

    Each gadget is a tournament matrix.  Vertices are relabeled to a
    common range by concatenating: gadget i occupies indices
    `[offset_i, offset_i + n_i)`.

    `cross_arcs` is a mapping from `((gi, li), (gj, lj))` -> orientation
    bit, where (gi, li) means "local vertex li of gadget gi" and gi <
    gj.  Orientation 1 means arc from gi.li -> gj.lj; 0 means the
    reverse.

    EVERY unordered cross-gadget pair must appear as a key (otherwise
    the composition is undefined and we raise).
    """
    offsets = []
    o = 0
    for G in gadgets:
        offsets.append(o)
        n_g = len(G)
        _check_tournament(G)
        o += n_g
    N = o
    T = [[0] * N for _ in range(N)]

    # Intra-gadget arcs.
    for k, G in enumerate(gadgets):
        off = offsets[k]
        for u in range(len(G)):
            for v in range(len(G)):
                if u != v and G[u][v]:
                    T[off + u][off + v] = 1

    # Cross-gadget arcs.
    pair_keys = {}
    for (gi, li), (gj, lj) in [
        ((gi, li), (gj, lj))
        for gi in range(len(gadgets))
        for gj in range(gi + 1, len(gadgets))
        for li in range(len(gadgets[gi]))
        for lj in range(len(gadgets[gj]))
    ]:
        pair_keys[((gi, li), (gj, lj))] = None
    missing = []
    for key in pair_keys:
        if key not in cross_arcs:
            missing.append(key)
    if missing:
        raise ValueError(
            f"missing {len(missing)} cross-arcs; first few: {missing[:5]}"
        )

    for ((gi, li), (gj, lj)), bit in cross_arcs.items():
        ui = offsets[gi] + li
        uj = offsets[gj] + lj
        if bit:
            T[ui][uj] = 1
        else:
            T[uj][ui] = 1
    _check_tournament(T)
    return T


def enumerate_cross_arc_orientations(
    gadgets: Sequence[Sequence[Sequence[int]]],
    fixed: dict | None = None,
) -> Iterator[dict[tuple[tuple[int, int], tuple[int, int]], int]]:
    """Yield every cross-arc orientation dict consistent with `fixed`.

    `fixed` is an optional partial assignment of cross-arc bits, of
    the same shape as `cross_arcs` in `gadget_compose`.  The remaining
    cross-arcs are enumerated over {0, 1}.

    Use with care: 2^E grows fast in the number of cross-arcs E.
    """
    fixed = dict(fixed or {})
    all_keys: list = []
    for gi in range(len(gadgets)):
        for gj in range(gi + 1, len(gadgets)):
            for li in range(len(gadgets[gi])):
                for lj in range(len(gadgets[gj])):
                    all_keys.append(((gi, li), (gj, lj)))
    free = [k for k in all_keys if k not in fixed]
    if len(free) > 16:
        raise ValueError(
            f"refusing to enumerate 2^{len(free)} cross-arc orientations"
        )
    for bits in product((0, 1), repeat=len(free)):
        assignment = dict(fixed)
        for k, b in zip(free, bits):
            assignment[k] = b
        yield assignment


def cross_arc_audit(
    gadgets: Sequence[Sequence[Sequence[int]]],
    local_port_pairs_per_gadget: Sequence[Sequence[tuple[int, int]]],
    expected_truth_tables: Sequence[set[PortTuple]],
    fixed_cross_arcs: dict | None = None,
    max_orientations: int | None = None,
) -> dict:
    """For every cross-arc orientation, check that the composed
    tournament's per-gadget local truth tables (projected to each
    gadget's ports) still match `expected_truth_tables`.

    Per-gadget ports are given in LOCAL labels (i.e. as vertex indices
    inside each gadget's own matrix).  Inside the audit we project the
    composed tournament back to each gadget's local vertex range, so
    LFOs and port bits are sound with respect to *each gadget's
    induced sub-tournament* — exactly the truth-table we want to
    preserve under composition.

    The semantic used is the standard
    `placement_bit_first_pair_inversion`.

    Returns:
      {
        "tested": int,
        "ok": int,
        "violations": list of {"orientation": dict,
                               "per_gadget": [{"missing":..., "spurious":...}, ...]},
      }
    """
    if len(local_port_pairs_per_gadget) != len(gadgets):
        raise ValueError(
            "local_port_pairs_per_gadget length must equal number of gadgets"
        )
    if len(expected_truth_tables) != len(gadgets):
        raise ValueError(
            "expected_truth_tables length must equal number of gadgets"
        )

    offsets = []
    o = 0
    for G in gadgets:
        offsets.append(o)
        o += len(G)

    tested = 0
    ok = 0
    violations: list[dict] = []
    for assignment in enumerate_cross_arc_orientations(gadgets, fixed_cross_arcs):
        if max_orientations is not None and tested >= max_orientations:
            break
        T = gadget_compose(gadgets, assignment)
        per_gadget = []
        gadget_ok = True
        for k, G in enumerate(gadgets):
            off = offsets[k]
            global_ports = [(off + a, off + b) for (a, b) in local_port_pairs_per_gadget[k]]
            vs = list(range(off, off + len(G)))
            obs = truth_table_from_gadget(
                T,
                global_ports,
                lambda P, _gp=global_ports: placement_bit_first_pair_inversion(P, _gp),
                vertices_subset=vs,
            )
            observed = {bits for bits, c in obs.items() if c > 0}
            expected = expected_truth_tables[k]
            missing = expected - observed
            spurious = observed - expected
            per_gadget.append({"missing": missing, "spurious": spurious})
            if missing or spurious:
                gadget_ok = False
        tested += 1
        if gadget_ok:
            ok += 1
        else:
            violations.append({"orientation": assignment, "per_gadget": per_gadget})
    return {"tested": tested, "ok": ok, "violations": violations}


# ------------------------------------------------------------------
# 6. Section 16 toggle helpers
# ------------------------------------------------------------------


def section16_toggle_tournament(k: int = 1) -> Matrix:
    """Build the Section 16 toggle-pair tournament on 4k vertices.

    Vertices:
        a_i = 2i,  b_i = 2i+1,
        f_i = 2k + 2i,  g_i = 2k + 2i + 1.
    Start transitive; reverse f_i -> a_i and g_i -> b_i for each i.
    """
    if k <= 0:
        raise ValueError("k must be positive")
    n = 4 * k
    T = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            T[i][j] = 1
    for i in range(k):
        a = 2 * i
        b = 2 * i + 1
        f = 2 * k + 2 * i
        g = 2 * k + 2 * i + 1
        T[a][f] = 0
        T[f][a] = 1
        T[b][g] = 0
        T[g][b] = 1
    return T


def section16_toggle_ports(k: int = 1) -> list[tuple[int, int]]:
    """Return the (a_i, b_i) port pairs for the Section 16 toggle."""
    return [(2 * i, 2 * i + 1) for i in range(k)]


# ------------------------------------------------------------------
# 7. CLI smoke test
# ------------------------------------------------------------------


if __name__ == "__main__":
    import json

    print("=== Section 16 single toggle (k=1) ===")
    T = section16_toggle_tournament(1)
    ports = section16_toggle_ports(1)
    res = verify_variable_gadget(T, ports[0])
    print(json.dumps({k: str(v) for k, v in res.items()}, indent=2))

    print()
    print("=== Section 16 toggle k=2 (composition-style) ===")
    T = section16_toggle_tournament(2)
    ports = section16_toggle_ports(2)
    tt = full_truth_table(
        T, ports,
        lambda P: placement_bit_first_pair_inversion(P, ports),
        width=2,
    )
    for bits, c in sorted(tt.items()):
        print(f"  {bits}: {c}")
