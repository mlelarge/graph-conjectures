"""Fanout / Splitter census for tournament Path-FAS (D73).

D72 confirmed a genuine exactly-2-in-3 CLAUSE gadget.  A full
NP-hardness reduction from 2-in-3-SAT additionally needs FANOUT: one
variable bit read by >= 3 clauses.  Sharing a single port pair across
three clauses is degree-blocked (each clause loader consumes back-degree
at the SAME endpoints, exceeding 2).  The only escape is a **splitter**:
a gadget that COPIES one ordering bit onto FRESH port pairs, each
retaining residual capacity to feed one clause.

The cleanest splitter is an all-equal relation on disjoint ports:

    EQ_k = { 00...0, 11...1 } subseteq {0,1}^k

with every port endpoint at internal back-degree <= 1 (residual >= 1),
so each output port can still accept one clause loader.

  * EQ_3 splitter (one gadget, 3 equal ports): feed each port to one
    clause -> a variable read by 3 clauses -> occurrence-3 -> hardness.
  * EQ_2 copy (1 -> fresh pair): chaining copies hits a degree-3 wall at
    internal chain nodes, so EQ_3-direct is the meaningful target.

This module enumerates disjoint k-port gadgets and searches for a
splitter relation with output capacity.  Decision:

  * a capacity-EQ_3 splitter exists -> fanout is realizable -> the
    2-in-3 clause + this splitter give an NP-hardness reduction (modulo
    an explicit composition);
  * none exists up to the feasible size -> extract the invariant (every
    branch consumes a third back-edge at some port endpoint) -> P-lean
    returns with a precise structural reason.
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
    schaefer_flags,
    tournament_iso_reps,
    tournament_reps_by_extension,
)


Matrix = list[list[int]]


def eq_relation(k: int) -> frozenset:
    return frozenset({tuple([0] * k), tuple([1] * k)})


def port_relation_with_capacity(
    lfo_cache: Sequence[tuple[tuple[int, ...], tuple[int, ...]]],
    ports: Sequence[tuple[int, int]],
) -> tuple[frozenset, frozenset]:
    """Return (R_T, R_comp) where R_comp is the lenient shadow: bit
    vectors with SOME witness leaving every port endpoint at back-degree
    <= 1 (residual capacity to accept one external clause loader)."""
    port_vertices = {v for x, y in ports for v in (x, y)}
    R: set[tuple[int, ...]] = set()
    R_comp: set[tuple[int, ...]] = set()
    for pos, deg in lfo_cache:
        bits = tuple(1 if pos[y] < pos[x] else 0 for (x, y) in ports)
        R.add(bits)
        if all(deg[v] <= 1 for v in port_vertices):
            R_comp.add(bits)
    return frozenset(R), frozenset(R_comp)


def census(n: int, k: int, use_iso_reps: bool = True) -> dict:
    """Search disjoint k-port gadgets at size n for splitter relations.

    Reports, in increasing strength:
      * realizes EQ_k as R_T (R_T == EQ_k, forces all ports equal);
      * EQ_k with one free value (EQ_k subseteq R_T);
      * capacity splitter: R_T == EQ_k AND R_comp == EQ_k (both equal
        vectors realizable with all ports at residual capacity)."""
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

    port_tuples = [pt for pt in itertools.combinations(pairs, k) if disjoint(pt)]
    orientations = list(itertools.product((0, 1), repeat=k))
    EQ = eq_relation(k)

    def flip(rel, o):
        return frozenset(tuple(b ^ oi for b, oi in zip(t, o)) for t in rel)

    realizes_eq_as_RT = []        # R_T == EQ_k
    eq_subset_RT = []             # EQ_k subseteq R_T (both equal vectors realizable)
    capacity_splitter = []        # R_T == EQ_k AND R_comp == EQ_k
    eq_with_partial_capacity = []  # R_T == EQ_k, R_comp contains >=1 equal vec
    tournaments_seen = 0

    for T in reps:
        tournaments_seen += 1
        cache = build_lfo_cache(T)
        if not cache:
            continue
        for pt in port_tuples:
            R_base, Rc_base = port_relation_with_capacity(cache, pt)
            for o in orientations:
                R = flip(R_base, o)
                Rc = flip(Rc_base, o)
                if R == EQ:
                    rec = {"T": [row[:] for row in T], "ports": list(pt),
                           "orientation": list(o),
                           "R_comp": sorted(tuple(b) for b in Rc)}
                    if len(realizes_eq_as_RT) < 10:
                        realizes_eq_as_RT.append(rec)
                    if Rc == EQ and len(capacity_splitter) < 10:
                        capacity_splitter.append(rec)
                    elif (Rc & EQ) and len(eq_with_partial_capacity) < 10:
                        eq_with_partial_capacity.append(rec)
                if EQ <= R and len(eq_subset_RT) < 10:
                    eq_subset_RT.append({
                        "T": [row[:] for row in T], "ports": list(pt),
                        "orientation": list(o),
                        "R_T": sorted(tuple(b) for b in R),
                        "R_comp": sorted(tuple(b) for b in Rc),
                    })

    return {
        "n": n,
        "k": k,
        "tournaments_seen": tournaments_seen,
        "disjoint_port_tuples_per_tournament": len(port_tuples),
        "realizes_EQ_as_RT": len(realizes_eq_as_RT) > 0,
        "realizes_EQ_examples": realizes_eq_as_RT[:3],
        "EQ_subset_RT_found": len(eq_subset_RT) > 0,
        "EQ_subset_RT_examples": eq_subset_RT[:3],
        "capacity_splitter_found": len(capacity_splitter) > 0,
        "capacity_splitter_examples": capacity_splitter[:5],
        "EQ_with_partial_capacity_found": len(eq_with_partial_capacity) > 0,
        "EQ_with_partial_capacity_examples": eq_with_partial_capacity[:3],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=6)
    parser.add_argument("--k", type=int, default=3)
    parser.add_argument("--all-labeled", action="store_true")
    args = parser.parse_args()
    out = census(args.n, args.k, use_iso_reps=not args.all_labeled)
    print(json.dumps(out, indent=2, default=list))


if __name__ == "__main__":
    main()
