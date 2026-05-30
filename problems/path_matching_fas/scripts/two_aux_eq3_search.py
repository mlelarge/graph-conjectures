"""Two-auxiliary-vertex EQ_3 splitter search for tournament Path-FAS.

This is the decisive escape-hatch experiment for the Fanout Barrier
(D73/D74).  D72 gives a genuine exactly-2-in-3 *clause* gadget, so the
only thing standing between tournament Path-FAS and NP-hardness (from
2-in-3-SAT) is a faithful **free-bit splitter**: a gadget that realizes
the all-equal relation

    EQ_3 = { 000, 111 }

on three *vertex-disjoint* ports, with **joint output capacity on BOTH
equality vectors** — i.e. some realizing LFO of 000 and some of 111,
each leaving all six port endpoints at back-degree <= 1 (residual >= 1),
so each port can still accept one D72-style clause loader.

Established (the precise invariant):
  * D73: at n <= 7, EQ_3 gadgets have R_comp = empty (capacity on
    NEITHER equality vector).
  * D74: forward-split pieces can get joint capacity on 111, reverse on
    000, but no single piece on BOTH; and a ONE-auxiliary extension of a
    pinned n=7 EQ_3 gadget (13/128 keep EQ_3) gains capacity on NEITHER.

This module decides whether **two auxiliary vertices** added to an n=7
EQ_3 base gadget — becoming part of the equality-enforcing mechanism,
not inert padding — can produce a faithful splitter.  The idea tested:
auxiliaries might *absorb* the equality-enforcing back-arcs, freeing the
six port endpoints to retain capacity.

Optimizations (the brute n_aux=2 search is 2^15 = 32768 extensions per
base gadget, each an n=9 LFO problem):

  1. A pruned backtracking LFO *enumerator* (`enum_lfos_deg`) replacing
     the n! brute force: builds the order left-to-right and kills any
     prefix whose back-arc graph already has degree > 2 or a cycle.
     ~350x faster than brute at n=9 (validated against brute at n<=7).
  2. Early R_T rejection: as soon as a partial relation contains a
     non-equality port vector (anything other than 000/111 after
     orientation), the extension cannot realize EQ_3, so we stop
     enumerating that extension.  Most of the 2^15 extensions die here.
  3. Multiple base gadgets, not just the one pinned constant: every
     distinct n=7 (T, ports, orient) realizing R_T = EQ_3 is collected
     (`collect_eq3_bases`) and used as a base, deduplicated by a
     port-individualized canonical key.
  4. A *structured* aux-placement sweep (`structured_aux_search`) that
     restricts the two auxiliaries to plausible equality-enforcing
     roles (forced-high loader-like / forced-low) rather than all 2^15
     arbitrary orientations, complementing the brute sweep.

Verdict logic: a positive find (EQ_3 base + 2 aux with joint capacity on
both {000,111}) reopens the NP-hardness route and is verified
independently (rebuild tournament, re-enumerate LFOs by brute force,
re-check ports disjoint and per-endpoint degrees).  A negative result is
certified with explicit scope.
"""
from __future__ import annotations

import argparse
import itertools
import json
import os
import sys
from typing import Iterable, Sequence

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from port_relation_census import (  # noqa: E402
    build_lfo_cache,
    tournament_reps_by_extension,
    valid_lfos,
    back_degrees,
)
from tournament_canonical import canonical_key, key_to_string  # noqa: E402

Matrix = list[list[int]]

EQ3 = frozenset({(0, 0, 0), (1, 1, 1)})


# ----------------------------------------------------------------------
# 1. Pruned backtracking LFO enumerator (with final back-degrees)
# ----------------------------------------------------------------------

def enum_lfos_deg(T: Matrix) -> list[tuple[tuple[int, ...], tuple[int, ...]]]:
    """Enumerate every valid LFO of T, returning (pos_vector, back_degree
    vector) for each, using prefix pruning.

    Builds the order left to right.  When vertex x is appended after the
    placed prefix, its new back-arcs are exactly x -> p for already-placed
    p with T[x][p] = 1.  If adding them pushes any endpoint to back-degree
    > 2 or closes an undirected cycle, no completion can repair it, so the
    branch is pruned.  Validated against the brute-force enumerator.
    """
    n = len(T)
    outmask = [sum((1 << v) for v in range(n) if T[u][v]) for u in range(n)]
    results: list[tuple[tuple[int, ...], tuple[int, ...]]] = []

    def rec(prefix_mask: int, remaining_mask: int,
            degree: list[int], parent: list[int],
            order: tuple[int, ...]) -> None:
        if not remaining_mask:
            pos = [0] * n
            for i, v in enumerate(order):
                pos[v] = i
            results.append((tuple(pos), tuple(degree)))
            return
        m = remaining_mask
        while m:
            bit = m & -m
            x = bit.bit_length() - 1
            m ^= bit
            deg = degree[:]
            par = parent[:]
            ok = True
            bm = outmask[x] & prefix_mask
            while bm:
                pb = bm & -bm
                p = pb.bit_length() - 1
                bm ^= pb
                if deg[x] >= 2 or deg[p] >= 2:
                    ok = False
                    break
                rx = x
                while par[rx] != rx:
                    rx = par[rx]
                rp = p
                while par[rp] != rp:
                    rp = par[rp]
                if rx == rp:
                    ok = False
                    break
                deg[x] += 1
                deg[p] += 1
                par[rp] = rx
            if not ok:
                continue
            rec(prefix_mask | (1 << x), remaining_mask ^ (1 << x),
                deg, par, order + (x,))

    rec(0, (1 << n) - 1, [0] * n, list(range(n)), tuple())
    return results


def relation_and_joint(T: Matrix,
                       ports: Sequence[tuple[int, int]],
                       orient: Sequence[int]):
    """Return (R_T, joint_capacity) on `ports` under orientation `orient`.

    joint_capacity = set of (oriented) bit-vectors b realizable by a
    witness LFO leaving ALL six port endpoints at back-degree <= 1."""
    o = tuple(orient)
    pv = [v for x, y in ports for v in (x, y)]
    R: set[tuple[int, ...]] = set()
    joint: set[tuple[int, ...]] = set()
    for pos, deg in enum_lfos_deg(T):
        raw = tuple(1 if pos[y] < pos[x] else 0 for (x, y) in ports)
        bits = tuple(b ^ oi for b, oi in zip(raw, o))
        R.add(bits)
        if all(deg[v] <= 1 for v in pv):
            joint.add(bits)
    return frozenset(R), frozenset(joint)


# ----------------------------------------------------------------------
# 2. Collect distinct n=7 EQ_3 base gadgets
# ----------------------------------------------------------------------

def _disjoint(pt) -> bool:
    seen: set[int] = set()
    for x, y in pt:
        if x in seen or y in seen:
            return False
        seen.update((x, y))
    return True


def _relabel_to_canonical_ports(T: Matrix, ports, orient):
    """Relabel T so its ports occupy positions (0,1),(2,3),(4,5) with the
    same orientation, and the two free (non-port) vertices land at 6.. .

    Returns (T', ports', orient) on the SAME vertex count.  This normal
    form makes every base gadget's auxiliary-extension structure
    identical, and lets us deduplicate base gadgets that differ only by
    a relabeling that fixes the ports.
    """
    n = len(T)
    pv = [v for x, y in ports for v in (x, y)]
    rest = [v for v in range(n) if v not in pv]
    perm = pv + rest  # new index i hosts old vertex perm[i]
    inv = [0] * n
    for new, old in enumerate(perm):
        inv[old] = new
    Tn = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            Tn[i][j] = T[perm[i]][perm[j]]
    ports_n = [(inv[x], inv[y]) for (x, y) in ports]
    return Tn, ports_n, tuple(orient)


def collect_eq3_bases(n: int = 7, limit: int | None = None) -> list[dict]:
    """Every distinct n-vertex EQ_3 base gadget (R_T = {000,111} on
    disjoint ports, some orientation), normalized to canonical port
    positions (0,1),(2,3),(4,5) and deduplicated.

    Deduplication key: canonical key of the tournament with port vertices
    INDIVIDUALIZED (so a relabeling that permutes ports counts as the
    same base, but one that maps a port to a non-port vertex does not).
    Returns a list of {"T", "ports", "orient"} records.
    """
    reps = tournament_reps_by_extension(n)
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    port_tuples = [pt for pt in itertools.combinations(pairs, 3) if _disjoint(pt)]
    orientations = list(itertools.product((0, 1), repeat=3))

    def flip(rel, o):
        return frozenset(tuple(b ^ oi for b, oi in zip(t, o)) for t in rel)

    seen: set[str] = set()
    bases: list[dict] = []
    for T in reps:
        cache = build_lfo_cache(T)
        if not cache:
            continue
        for pt in port_tuples:
            R_base = set()
            for pos, _deg in cache:
                R_base.add(tuple(1 if pos[y] < pos[x] else 0 for (x, y) in pt))
            R_base = frozenset(R_base)
            for o in orientations:
                if flip(R_base, o) != EQ3:
                    continue
                Tn, ports_n, orient_n = _relabel_to_canonical_ports(T, pt, o)
                key = _port_individualized_key(Tn, ports_n)
                if key in seen:
                    continue
                seen.add(key)
                bases.append({"T": [r[:] for r in Tn],
                              "ports": [list(p) for p in ports_n],
                              "orient": list(orient_n)})
                if limit and len(bases) >= limit:
                    return bases
    return bases


def _port_individualized_key(T: Matrix, ports) -> str:
    """Dedup key for a base gadget whose ports are already PINNED to fixed
    positions (0,1),(2,3),(4,5) by `_relabel_to_canonical_ports`.

    Since the ports occupy fixed labels, two records with the same raw
    labeled adjacency string are the same labeled base.  We therefore key
    on the raw labeled matrix.  This is conservative: it treats two
    gadgets related by a port-permuting or within-port-swapping
    isomorphism as DISTINCT bases, so the base set it produces is a
    superset of the iso-classes — which only BROADENS the search scope,
    never narrows it (soundness for the negative result).  (`canonical_key`
    is imported and available for a stricter port-colored dedup if ever
    needed, but the conservative labeled key is what we use.)
    """
    raw = "".join("1" if T[i][j] else "0"
                  for i in range(len(T)) for j in range(len(T)))
    return raw  # labeled key: ports already pinned to fixed positions


# ----------------------------------------------------------------------
# 3. Two-aux extension search over one base
# ----------------------------------------------------------------------

def two_aux_search_one_base(base: dict, n_aux: int = 2,
                            collect_examples: int = 5) -> dict:
    """Brute sweep of all arc-orientations incident to n_aux auxiliary
    vertices added on top of `base`, with early R_T rejection.

    Returns counts of EQ_3-preserving extensions and any with joint
    capacity on one / both equality vectors.
    """
    G = base["T"]
    ports = [tuple(p) for p in base["ports"]]
    orient = tuple(base["orient"])
    g = len(G)
    n = g + n_aux
    pv = [v for x, y in ports for v in (x, y)]
    free_pairs = [(i, j) for i in range(n) for j in range(i + 1, n)
                  if i >= g or j >= g]

    eq3_preserved = 0
    both_cap: list[dict] = []
    one_cap: list[dict] = []

    base_block = [[G[i][j] if (i < g and j < g) else 0 for j in range(n)]
                  for i in range(n)]

    for mask in range(1 << len(free_pairs)):
        T = [row[:] for row in base_block]
        for bit, (i, j) in enumerate(free_pairs):
            if (mask >> bit) & 1:
                T[i][j] = 1
            else:
                T[j][i] = 1
        R, joint = _relation_joint_with_eq_pruning(T, ports, orient)
        if R != EQ3:
            continue
        eq3_preserved += 1
        if EQ3 <= joint:
            if len(both_cap) < collect_examples:
                both_cap.append({"mask": mask, "T": [r[:] for r in T],
                                 "joint": sorted(tuple(b) for b in joint)})
        elif joint & EQ3:
            if len(one_cap) < collect_examples:
                one_cap.append({"mask": mask,
                                "joint": sorted(tuple(b) for b in joint)})

    return {
        "n_aux": n_aux,
        "n_total": n,
        "free_arc_pairs": len(free_pairs),
        "extensions_tried": 1 << len(free_pairs),
        "eq3_preserved": eq3_preserved,
        "both_equality_capacity_found": len(both_cap) > 0,
        "both_equality_capacity_count": len(both_cap),
        "both_equality_examples": both_cap,
        "one_equality_capacity_found": len(one_cap) > 0,
        "one_equality_capacity_count": len(one_cap),
        "one_equality_examples": one_cap[:3],
    }


def _relation_joint_with_eq_pruning(T: Matrix,
                                    ports: Sequence[tuple[int, int]],
                                    orient: Sequence[int]):
    """Like relation_and_joint, but ABORTS as soon as a non-equality port
    vector appears (returns a sentinel R != EQ3).  This is the main
    per-extension speedup: most extensions emit a mixed vector on an
    early LFO and are rejected without enumerating the rest.

    Returns (R, joint).  If a non-EQ3 vector is found, R is returned
    immediately (a frozenset containing that vector) and joint is empty.
    """
    n = len(T)
    o = tuple(orient)
    pv = [v for x, y in ports for v in (x, y)]
    outmask = [sum((1 << v) for v in range(n) if T[u][v]) for u in range(n)]
    R: set[tuple[int, ...]] = set()
    joint: set[tuple[int, ...]] = set()
    aborted = [False]

    def rec(prefix_mask: int, remaining_mask: int,
            degree: list[int], parent: list[int],
            order: tuple[int, ...]) -> None:
        if aborted[0]:
            return
        if not remaining_mask:
            pos = [0] * n
            for i, v in enumerate(order):
                pos[v] = i
            raw = tuple(1 if pos[y] < pos[x] else 0 for (x, y) in ports)
            bits = tuple(b ^ oi for b, oi in zip(raw, o))
            if bits not in EQ3:
                aborted[0] = True
                R.add(bits)
                return
            R.add(bits)
            if all(degree[v] <= 1 for v in pv):
                joint.add(bits)
            return
        m = remaining_mask
        while m:
            if aborted[0]:
                return
            bit = m & -m
            x = bit.bit_length() - 1
            m ^= bit
            deg = degree[:]
            par = parent[:]
            ok = True
            bm = outmask[x] & prefix_mask
            while bm:
                pb = bm & -bm
                p = pb.bit_length() - 1
                bm ^= pb
                if deg[x] >= 2 or deg[p] >= 2:
                    ok = False
                    break
                rx = x
                while par[rx] != rx:
                    rx = par[rx]
                rp = p
                while par[rp] != rp:
                    rp = par[rp]
                if rx == rp:
                    ok = False
                    break
                deg[x] += 1
                deg[p] += 1
                par[rp] = rx
            if not ok:
                continue
            rec(prefix_mask | (1 << x), remaining_mask ^ (1 << x),
                deg, par, order + (x,))

    rec(0, (1 << n) - 1, [0] * n, list(range(n)), tuple())
    if aborted[0]:
        # R now contains a non-EQ3 vector -> reject
        return frozenset(R), frozenset()
    return frozenset(R), frozenset(joint)


# ----------------------------------------------------------------------
# 4. Driver across all bases
# ----------------------------------------------------------------------

def _worker(args):
    idx, base, n_aux = args
    res = two_aux_search_one_base(base, n_aux=n_aux)
    return idx, base, res


def run_all_bases(n_aux: int = 2, base_limit: int | None = None,
                  verbose: bool = False, workers: int | None = None) -> dict:
    bases = collect_eq3_bases(7, limit=base_limit)
    per_base: list[dict] = []
    total_eq3 = 0
    total_both = 0
    total_one = 0
    any_both_example = None
    any_one_example = None

    tasks = [(idx, base, n_aux) for idx, base in enumerate(bases)]
    if workers is None:
        workers = max(1, (os.cpu_count() or 2) - 2)

    if workers == 1:
        results = []
        for t in tasks:
            out = _worker(t)
            results.append(out)
            if verbose:
                idx, _b, res = out
                print(f"  base {idx}: eq3_preserved={res['eq3_preserved']} "
                      f"both={res['both_equality_capacity_count']} "
                      f"one={res['one_equality_capacity_count']}", flush=True)
    else:
        import multiprocessing as mp
        # Use a fork context: avoids re-importing/re-running the module in
        # each child (the spawn default on macOS), which was deadlocking
        # pool startup here.  The workload is pure Python (no threads, no
        # native libs), so fork is safe.
        ctx = mp.get_context("fork")
        with ctx.Pool(workers) as pool:
            results = []
            for out in pool.imap_unordered(_worker, tasks):
                results.append(out)
                if verbose:
                    idx, _b, res = out
                    print(f"  base {idx}: eq3_preserved={res['eq3_preserved']} "
                          f"both={res['both_equality_capacity_count']} "
                          f"one={res['one_equality_capacity_count']}",
                          flush=True)
    results.sort(key=lambda r: r[0])

    for idx, base, res in results:
        total_eq3 += res["eq3_preserved"]
        total_both += res["both_equality_capacity_count"]
        total_one += res["one_equality_capacity_count"]
        if res["both_equality_capacity_found"] and any_both_example is None:
            any_both_example = {"base_index": idx, "base": base, "result": res}
        if res["one_equality_capacity_found"] and any_one_example is None:
            any_one_example = {"base_index": idx, "base": base,
                               "one_examples": res["one_equality_examples"]}
        per_base.append({"base_index": idx,
                         "eq3_preserved": res["eq3_preserved"],
                         "both": res["both_equality_capacity_count"],
                         "one": res["one_equality_capacity_count"]})
    return {
        "n_aux": n_aux,
        "num_bases": len(bases),
        "total_eq3_preserved_extensions": total_eq3,
        "total_both_capacity": total_both,
        "total_one_capacity": total_one,
        "both_capacity_found": total_both > 0,
        "one_capacity_found": total_one > 0,
        "both_capacity_example": any_both_example,
        "one_capacity_example": any_one_example,
        "per_base": per_base,
    }


# ----------------------------------------------------------------------
# 4b. Structured / composition search (the D74 §5 escape)
# ----------------------------------------------------------------------

def structured_compose_search(collect_examples: int = 5,
                              verbose: bool = False) -> dict:
    """Search the D74 §5 "two private auxiliaries" escape directly, NOT
    by extending a pre-existing n=7 EQ_3 sub-gadget.

    Topology (9 vertices): three disjoint ports
        p0 = (0, 1), p1 = (2, 3), p2 = (4, 5)
    plus two auxiliaries a = 6, b = 7, plus one top-padding vertex f = 8.

    The auxiliaries are meant to ABSORB the equality-enforcing back-arcs
    so the six port endpoints retain capacity.  Following D74 §5, we let
    the coupling between ports flow THROUGH the two auxiliaries: the arcs
    we enumerate are exactly the arcs incident to an auxiliary (a or b),
    while
      * the arcs among the six port vertices are held at a fixed,
        low-loading transitive baseline (0<1<...<5) that on its own
        forces NO port relation, and
      * vertex 8 is fixed top padding (every gadget vertex -> 8), which
        raises auxiliary score windows so an auxiliary can act as a
        FORCED router/loader (cf. D72's score-window separation).

    So the ONLY mechanism that can force equality is the auxiliary
    coupling -- exactly the hypothesis under test.  Free arcs: pairs
    incident to {6,7} = C(2,2)+2*7 = 1+14 = 15, i.e. 2^15 masks (same
    cost as one brute base), enumerated with early-EQ pruning.
    """
    n = 9
    ports = [(0, 1), (2, 3), (4, 5)]
    orient = (0, 0, 0)
    AUX = (6, 7)
    PAD = 8
    # Fixed baseline among the six port vertices: transitive 0<1<...<5
    # (i -> j for i<j).  On its own this is acyclic, forcing no port bit.
    base = [[0] * n for _ in range(n)]
    for i in range(6):
        for j in range(i + 1, 6):
            base[i][j] = 1
    # Top padding: every non-pad vertex -> PAD (8).  Raises aux windows.
    for v in range(n):
        if v != PAD:
            base[v][PAD] = 1
    # Free arcs: incident to an auxiliary, EXCLUDING the PAD vertex (its
    # arcs stay fixed forward so PAD is genuine top padding).
    free_pairs = [(i, j) for i in range(n) for j in range(i + 1, n)
                  if (i in AUX or j in AUX) and i != PAD and j != PAD]
    eq3_preserved = 0
    both_cap: list[dict] = []
    one_cap: list[dict] = []
    n_masks = 1 << len(free_pairs)
    for mask in range(n_masks):
        T = [row[:] for row in base]
        for bit, (i, j) in enumerate(free_pairs):
            if (mask >> bit) & 1:
                T[i][j] = 1
            else:
                T[j][i] = 1
        R, joint = _relation_joint_with_eq_pruning(T, ports, orient)
        if R != EQ3:
            continue
        eq3_preserved += 1
        if EQ3 <= joint:
            if len(both_cap) < collect_examples:
                both_cap.append({"mask": mask, "T": [r[:] for r in T],
                                 "joint": sorted(tuple(b) for b in joint)})
        elif joint & EQ3:
            if len(one_cap) < collect_examples:
                one_cap.append({"mask": mask, "T": [r[:] for r in T],
                                "joint": sorted(tuple(b) for b in joint)})
        if verbose and eq3_preserved % 50 == 0:
            print(f"  [structured] eq3_preserved={eq3_preserved} "
                  f"both={len(both_cap)} one={len(one_cap)}", flush=True)
    return {
        "topology": "3 ports + 2 aux + 1 free, inter-port arcs fixed transitive",
        "n_total": n,
        "free_arc_pairs": len(free_pairs),
        "extensions_tried": n_masks,
        "eq3_preserved": eq3_preserved,
        "both_equality_capacity_found": len(both_cap) > 0,
        "both_equality_capacity_count": len(both_cap),
        "both_equality_examples": both_cap,
        "one_equality_capacity_found": len(one_cap) > 0,
        "one_equality_capacity_count": len(one_cap),
        "one_equality_examples": one_cap[:3],
    }


# ----------------------------------------------------------------------
# 5. Independent verification of a positive find
# ----------------------------------------------------------------------

def verify_splitter(T: Matrix, ports, orient) -> dict:
    """Independently re-verify a claimed two-aux EQ_3 splitter:
      * T is a valid tournament;
      * ports are pairwise vertex-disjoint;
      * R_T = {000,111} on `ports` under `orient` (BRUTE-FORCE LFOs);
      * joint capacity on BOTH equality vectors, with EACH realized by a
        witness whose six port endpoints are all at back-degree <= 1.
    """
    n = len(T)
    # tournament validity
    is_tournament = all(T[i][i] == 0 for i in range(n)) and all(
        (T[i][j] == 0) != (T[j][i] == 0)
        for i in range(n) for j in range(i + 1, n))
    # disjoint ports
    pv = [v for x, y in ports for v in (x, y)]
    ports_disjoint = len(set(pv)) == len(pv)
    o = tuple(orient)
    lfos = valid_lfos(T)  # brute-force, the trust root
    R: set[tuple[int, ...]] = set()
    witnesses: dict[tuple[int, ...], list] = {}
    for P in lfos:
        pos = [0] * n
        for i, v in enumerate(P):
            pos[v] = i
        raw = tuple(1 if pos[y] < pos[x] else 0 for (x, y) in ports)
        bits = tuple(b ^ oi for b, oi in zip(raw, o))
        R.add(bits)
        deg = back_degrees(T, P)
        if all(deg[v] <= 1 for v in pv):
            witnesses.setdefault(bits, []).append(
                {"order": list(P), "port_degrees": {v: deg[v] for v in pv}})
    R = frozenset(R)
    cap000 = (0, 0, 0) in witnesses
    cap111 = (1, 1, 1) in witnesses
    return {
        "is_tournament": is_tournament,
        "ports_disjoint": ports_disjoint,
        "num_lfos_brute": len(lfos),
        "R_T": sorted(tuple(b) for b in R),
        "R_T_is_EQ3": R == EQ3,
        "joint_capacity_000": cap000,
        "joint_capacity_111": cap111,
        "is_faithful_splitter": (is_tournament and ports_disjoint
                                 and R == EQ3 and cap000 and cap111),
        "witness_000": witnesses.get((0, 0, 0), [])[:1],
        "witness_111": witnesses.get((1, 1, 1), [])[:1],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n-aux", type=int, default=2)
    parser.add_argument("--base-limit", type=int, default=None)
    parser.add_argument("--workers", type=int, default=None)
    parser.add_argument("--list-bases", action="store_true")
    parser.add_argument("--structured", action="store_true",
                        help="Run the D74 §5 structured composition search.")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()
    if args.list_bases:
        bases = collect_eq3_bases(7, limit=args.base_limit)
        print(json.dumps({"num_bases": len(bases), "bases": bases},
                         indent=2, default=list))
        return
    if args.structured:
        print(json.dumps(structured_compose_search(verbose=args.verbose),
                         indent=2, default=list))
        return
    out = run_all_bases(n_aux=args.n_aux, base_limit=args.base_limit,
                        verbose=args.verbose, workers=args.workers)
    print(json.dumps(out, indent=2, default=list))


if __name__ == "__main__":
    main()
