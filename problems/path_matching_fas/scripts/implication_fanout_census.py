"""Implication-style fanout census for tournament Path-FAS (D74).

D73 ruled out EQ-style (all-equal) capacity splitters at n <= 7
(padding-robust).  But the all-equal relation EQ_3 forbids 6 of 8
vectors — heavy back-arc loading that saturates the ports.  An
IMPLICATION relation forbids only 3 vectors, so it loads the ports
less and may retain output capacity.

Two role-sensitive implication relations on ports (x, y, z):

    Forward split  x -> y, x -> z :  R = {000,001,010,011,111}
        (x is the SOURCE; y, z are OUTPUTS)
    Reverse split  y -> x, z -> x :  R = {000,100,101,110,111}
        (x is the SINK; y, z are SOURCES)

A forward gadget x->y plus a reverse gadget y->x on the same internal
port y pp-composes to x = y (equivalence), so forward + reverse
implications can in principle build an equality splitter — *if* the
internal propagated port y keeps enough residual back-degree for both
its upstream and downstream connection.  That role-sensitive capacity
is exactly where the degree-2 budget should bite.

This module:
  1. censuses whether forward/reverse implication relations appear as
     R_T on disjoint 3-ports (n <= 7), and with what per-port capacity;
  2. distinguishes SOURCE-port capacity from OUTPUT-port capacity
     (role-sensitive);
  3. (if implications carry capacity) tests pp-composition of a forward
     and a reverse gadget into an equality splitter, watching the
     internal port's residual.
"""
from __future__ import annotations

import argparse
import itertools
import json
import os
import sys
from typing import Sequence

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from port_relation_census import (  # noqa: E402
    build_lfo_cache,
    tournament_iso_reps,
    tournament_reps_by_extension,
)


Matrix = list[list[int]]


# ----------------------------------------------------------------------
# 1. Target implication relations and their symmetry orbit
# ----------------------------------------------------------------------

def implication_relation(source: int, targets: Sequence[int], k: int = 3) -> frozenset:
    """{ b in {0,1}^k : b[source]=1 => b[t]=1 for all t in targets }."""
    out = []
    for b in itertools.product((0, 1), repeat=k):
        if b[source] == 1 and any(b[t] == 0 for t in targets):
            continue
        out.append(b)
    return frozenset(out)


def forward_split_orbit() -> set[frozenset]:
    """All coordinate-relabelings of the forward split x->y,z (3 ports)."""
    orbit = set()
    for source in range(3):
        targets = [t for t in range(3) if t != source]
        orbit.add(implication_relation(source, targets))
    return orbit


def reverse_split_orbit() -> set[frozenset]:
    """All coordinate-relabelings of the reverse split y,z->x (3 ports)."""
    orbit = set()
    for sink in range(3):
        sources = [s for s in range(3) if s != sink]
        rel = []
        for b in itertools.product((0, 1), repeat=3):
            if any(b[s] == 1 and b[sink] == 0 for s in sources):
                continue
            rel.append(b)
        orbit.add(frozenset(rel))
    return orbit


FWD_ORBIT = forward_split_orbit()
REV_ORBIT = reverse_split_orbit()


# ----------------------------------------------------------------------
# 2. Per-port (role-sensitive) capacity
# ----------------------------------------------------------------------

def relation_and_port_capacity(
    lfo_cache: Sequence[tuple[tuple[int, ...], tuple[int, ...]]],
    ports: Sequence[tuple[int, int]],
):
    """Return (R_T, per_port_capacity) where per_port_capacity[i] is the
    set of bit-vectors realizable by a witness whose port-i endpoints
    BOTH have back-degree <= 1 (residual >= 1 for one attachment on
    port i).  Role-sensitive: capacity is tracked per port, not jointly."""
    k = len(ports)
    R: set[tuple[int, ...]] = set()
    per_port: list[set] = [set() for _ in range(k)]
    # also joint: all ports have capacity simultaneously
    joint: set[tuple[int, ...]] = set()
    for pos, deg in lfo_cache:
        bits = tuple(1 if pos[y] < pos[x] else 0 for (x, y) in ports)
        R.add(bits)
        port_ok = []
        for i, (x, y) in enumerate(ports):
            ok = deg[x] <= 1 and deg[y] <= 1
            port_ok.append(ok)
            if ok:
                per_port[i].add(bits)
        if all(port_ok):
            joint.add(bits)
    return frozenset(R), [frozenset(s) for s in per_port], frozenset(joint)


# ----------------------------------------------------------------------
# 3. Census
# ----------------------------------------------------------------------

def census(n: int, use_iso_reps: bool = True) -> dict:
    if use_iso_reps:
        reps = (tournament_reps_by_extension(n) if n >= 7
                else tournament_iso_reps(n))
    else:
        from port_relation_census import all_tournaments
        reps = list(all_tournaments(n))

    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]

    def disjoint(pt) -> bool:
        seen: set[int] = set()
        for x, y in pt:
            if x in seen or y in seen:
                return False
            seen.update((x, y))
        return True

    port_tuples = [pt for pt in itertools.combinations(pairs, 3) if disjoint(pt)]
    orientations = list(itertools.product((0, 1), repeat=3))

    def flip(rel, o):
        return frozenset(tuple(b ^ oi for b, oi in zip(t, o)) for t in rel)

    fwd_as_RT = 0
    rev_as_RT = 0
    fwd_full_capacity = []   # forward split with ALL ports capacity (joint)
    rev_full_capacity = []
    fwd_output_capacity = []  # forward: both OUTPUT ports have capacity for the relevant vectors
    tournaments_seen = 0

    for T in reps:
        tournaments_seen += 1
        cache = build_lfo_cache(T)
        if not cache:
            continue
        for pt in port_tuples:
            R_base, per_port_base, joint_base = relation_and_port_capacity(cache, pt)
            for o in orientations:
                R = flip(R_base, o)
                if R in FWD_ORBIT:
                    fwd_as_RT += 1
                    joint = flip(joint_base, o)
                    if joint == R and len(fwd_full_capacity) < 10:
                        fwd_full_capacity.append({
                            "T": [r[:] for r in T], "ports": list(pt),
                            "orientation": list(o),
                            "R_T": sorted(tuple(b) for b in R)})
                    # identify source = the coordinate s with R == impl(s, others)
                    src = _source_of_forward(R)
                    outs = [i for i in range(3) if i != src]
                    per_port = [flip(per_port_base[i], o) for i in range(3)]
                    # OUTPUT capacity: each output port has capacity on
                    # every vector where that output bit must be read
                    out_cap = all(per_port[i] == R for i in outs)
                    if out_cap and len(fwd_output_capacity) < 10:
                        fwd_output_capacity.append({
                            "T": [r[:] for r in T], "ports": list(pt),
                            "orientation": list(o), "source_port": src,
                            "R_T": sorted(tuple(b) for b in R),
                            "per_port_capacity": [sorted(tuple(b) for b in per_port[i]) for i in range(3)]})
                if R in REV_ORBIT:
                    rev_as_RT += 1
                    joint = flip(joint_base, o)
                    if joint == R and len(rev_full_capacity) < 10:
                        rev_full_capacity.append({
                            "T": [r[:] for r in T], "ports": list(pt),
                            "orientation": list(o),
                            "R_T": sorted(tuple(b) for b in R)})

    return {
        "n": n,
        "tournaments_seen": tournaments_seen,
        "disjoint_port_tuples": len(port_tuples),
        "forward_split_as_RT_count": fwd_as_RT,
        "reverse_split_as_RT_count": rev_as_RT,
        "forward_full_capacity_found": len(fwd_full_capacity) > 0,
        "forward_full_capacity_examples": fwd_full_capacity[:3],
        "forward_output_capacity_found": len(fwd_output_capacity) > 0,
        "forward_output_capacity_examples": fwd_output_capacity[:3],
        "reverse_full_capacity_found": len(rev_full_capacity) > 0,
        "reverse_full_capacity_examples": rev_full_capacity[:3],
    }


def _source_of_forward(R: frozenset) -> int:
    for s in range(3):
        if R == implication_relation(s, [t for t in range(3) if t != s]):
            return s
    return -1


# ----------------------------------------------------------------------
# 4. Refined capacity audit (equality-slice, not joint==R)
# ----------------------------------------------------------------------

def refined_capacity_audit(n: int, use_iso_reps: bool = True) -> dict:
    """For composition into EQ_3 a forward/reverse piece needs JOINT
    (all-port) capacity only on the EQUALITY SLICE {000,111}, not on all
    implication-allowed vectors.  This audit checks, over every forward
    and reverse split gadget at size n:

      * the set of vectors with joint (all-port) capacity;
      * whether 111 (the active branching vector) is ever joint-capacity;
      * whether {000,111} (both equality vectors) is ever joint-capacity;
      * whether the SOURCE port ever has capacity on a source-bit-1
        vector (the universal version of the "source saturates on
        active value" claim).
    """
    if use_iso_reps:
        reps = (tournament_reps_by_extension(n) if n >= 7
                else tournament_iso_reps(n))
    else:
        from port_relation_census import all_tournaments
        reps = list(all_tournaments(n))

    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]

    def disjoint(pt) -> bool:
        seen: set[int] = set()
        for x, y in pt:
            if x in seen or y in seen:
                return False
            seen.update((x, y))
        return True

    port_tuples = [pt for pt in itertools.combinations(pairs, 3) if disjoint(pt)]
    orientations = list(itertools.product((0, 1), repeat=3))

    def flip(rel, o):
        return frozenset(tuple(b ^ oi for b, oi in zip(t, o)) for t in rel)

    ZERO = (0, 0, 0)
    ONE = (1, 1, 1)

    fwd_111_joint = []          # forward gadgets with 111 in joint capacity
    fwd_both_eq_joint = []      # forward with {000,111} <= joint
    rev_000_joint = []          # reverse with 000 in joint
    rev_both_eq_joint = []
    fwd_source_bit1_capacity = []  # forward where source has capacity on a bit-1 vector
    fwd_gadgets = 0
    rev_gadgets = 0

    for T in reps:
        cache = build_lfo_cache(T)
        if not cache:
            continue
        for pt in port_tuples:
            R_base, per_port_base, joint_base = relation_and_port_capacity(cache, pt)
            for o in orientations:
                R = flip(R_base, o)
                joint = flip(joint_base, o)
                if R in FWD_ORBIT:
                    fwd_gadgets += 1
                    src = _source_of_forward(R)
                    per_port = [flip(per_port_base[i], o) for i in range(3)]
                    if ONE in joint and len(fwd_111_joint) < 10:
                        fwd_111_joint.append({"T": [r[:] for r in T],
                                              "ports": list(pt), "orientation": list(o),
                                              "joint": sorted(tuple(b) for b in joint)})
                    if {ZERO, ONE} <= joint and len(fwd_both_eq_joint) < 10:
                        fwd_both_eq_joint.append({"T": [r[:] for r in T],
                                                  "ports": list(pt), "orientation": list(o)})
                    # source capacity on any source-bit-1 vector
                    src_cap = per_port[src]
                    if any(b[src] == 1 for b in src_cap) and len(fwd_source_bit1_capacity) < 10:
                        fwd_source_bit1_capacity.append({
                            "T": [r[:] for r in T], "ports": list(pt),
                            "orientation": list(o), "source_port": src,
                            "source_capacity": sorted(tuple(b) for b in src_cap)})
                if R in REV_ORBIT:
                    rev_gadgets += 1
                    if ZERO in joint and len(rev_000_joint) < 10:
                        rev_000_joint.append({"T": [r[:] for r in T],
                                              "ports": list(pt), "orientation": list(o)})
                    if {ZERO, ONE} <= joint and len(rev_both_eq_joint) < 10:
                        rev_both_eq_joint.append({"T": [r[:] for r in T],
                                                  "ports": list(pt), "orientation": list(o)})

    return {
        "n": n,
        "forward_gadgets_seen": fwd_gadgets,
        "reverse_gadgets_seen": rev_gadgets,
        "forward_111_in_joint_found": len(fwd_111_joint) > 0,
        "forward_111_in_joint_examples": fwd_111_joint[:3],
        "forward_both_equality_in_joint_found": len(fwd_both_eq_joint) > 0,
        "reverse_000_in_joint_found": len(rev_000_joint) > 0,
        "reverse_both_equality_in_joint_found": len(rev_both_eq_joint) > 0,
        "forward_source_has_bit1_capacity_found": len(fwd_source_bit1_capacity) > 0,
        "forward_source_bit1_capacity_examples": fwd_source_bit1_capacity[:3],
    }


# ----------------------------------------------------------------------
# 5. Auxiliary-vertex extension search (composition-capacity probe)
# ----------------------------------------------------------------------

# A concrete n=7 EQ_3 gadget (R_T = {000,111} on disjoint ports), with
# R_comp = empty (D73): no equality vector has joint capacity.  Used to
# test whether ADDING AUXILIARY VERTICES (part of the equality
# mechanism, not inert padding) can free port capacity on the equality
# slice {000,111}.
EQ3_GADGET = [
    [0, 0, 0, 1, 0, 1, 0],
    [1, 0, 0, 0, 0, 1, 0],
    [1, 1, 0, 0, 0, 0, 0],
    [0, 1, 1, 0, 1, 0, 0],
    [1, 1, 1, 0, 0, 0, 0],
    [0, 0, 1, 1, 1, 0, 1],
    [1, 1, 1, 1, 1, 0, 0],
]
EQ3_GADGET_PORTS = [(0, 2), (1, 3), (4, 5)]
EQ3_GADGET_ORIENT = (0, 0, 0)

EQ3 = frozenset({(0, 0, 0), (1, 1, 1)})


def aux_extension_search(
    G: Matrix,
    ports: Sequence[tuple[int, int]],
    orient: Sequence[int],
    n_aux: int,
) -> dict:
    """Extend EQ_3 gadget G by n_aux auxiliary vertices, enumerating ALL
    orientations of the arcs incident to the auxiliaries (existing-
    existing arcs fixed by G).  For each extension that keeps R_T = EQ_3,
    record whether the (composed) gadget gains joint output capacity on
    the equality slice.

    Returns counts:
      * eq3_preserved        — extensions with R_T still = EQ_3;
      * both_equality_capacity — of those, {000,111} <= joint;
      * one_equality_capacity  — of those, exactly one of 000/111 in joint.
    """
    g = len(G)
    n = g + n_aux
    pv = [v for x, y in ports for v in (x, y)]
    o = tuple(orient)
    # free arc pairs: those incident to at least one auxiliary vertex
    free_pairs = [(i, j) for i in range(n) for j in range(i + 1, n)
                  if i >= g or j >= g]
    eq3_preserved = 0
    both_cap = []
    one_cap = []
    for mask in range(1 << len(free_pairs)):
        T = [[0] * n for _ in range(n)]
        for i in range(g):
            for j in range(g):
                T[i][j] = G[i][j]
        for bit, (i, j) in enumerate(free_pairs):
            if (mask >> bit) & 1:
                T[i][j] = 1
            else:
                T[j][i] = 1
        cache = build_lfo_cache(T)
        if not cache:
            continue
        R = set()
        joint = set()
        for pos, deg in cache:
            raw = tuple(1 if pos[y] < pos[x] else 0 for (x, y) in ports)
            bits = tuple(b ^ oi for b, oi in zip(raw, o))
            R.add(bits)
            if all(deg[v] <= 1 for v in pv):
                joint.add(bits)
        if frozenset(R) != EQ3:
            continue
        eq3_preserved += 1
        if EQ3 <= joint:
            if len(both_cap) < 5:
                both_cap.append({"mask": mask})
        elif joint & EQ3:
            if len(one_cap) < 5:
                one_cap.append({"mask": mask, "joint": sorted(tuple(b) for b in joint)})
    return {
        "n_aux": n_aux,
        "n_total": n,
        "free_arc_pairs": len(free_pairs),
        "extensions_tried": 1 << len(free_pairs),
        "eq3_preserved": eq3_preserved,
        "both_equality_capacity_found": len(both_cap) > 0,
        "both_equality_capacity_count": len(both_cap),
        "one_equality_capacity_found": len(one_cap) > 0,
        "one_equality_capacity_count": len(one_cap),
        "one_equality_examples": one_cap[:3],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=6)
    parser.add_argument("--audit", action="store_true",
                        help="Run refined_capacity_audit(n) instead.")
    parser.add_argument("--aux", type=int, default=0,
                        help="Run aux_extension_search with this many aux vertices.")
    args = parser.parse_args()
    if args.aux:
        print(json.dumps(
            aux_extension_search(EQ3_GADGET, EQ3_GADGET_PORTS,
                                 EQ3_GADGET_ORIENT, args.aux),
            indent=2, default=list))
    elif args.audit:
        print(json.dumps(refined_capacity_audit(args.n), indent=2, default=list))
    else:
        print(json.dumps(census(args.n), indent=2, default=list))


if __name__ == "__main__":
    main()
