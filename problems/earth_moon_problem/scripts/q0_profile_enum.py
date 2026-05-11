#!/usr/bin/env python3
"""
Enumerate the Q0 profile model from docs/phase6_discharge_attempt.md.

This is a necessary-condition checker for the residual Q0 case in the
isolated-low-vertex argument. It does not build graphs. Instead it sweeps
the finite arithmetic model:

    G[N(v)] = K_{s_1} + ... + K_{s_p},  sum s_i = 11, s_i <= 7,

then contracts one cross-clique non-edge. Each surviving chunk C_i has size
t_i and epsilon_i in {0,1}, where epsilon_i records whether C_i descends from
one of the two merged cliques and hence has its inherited edge to the merged
vertex w.

For each chunk:

    t_i f_i + p_i + h_i = t_i (12 - t_i - epsilon_i),

where f_i is the number of low outside vertices fully attached to C_i, p_i
the number singly attached, and h_i high-outside edges to C_i. Low outside
vertices are exclusive across chunks, and high outside vertices are packed
using the sharp necessary bound sum ceil(h_i / t_i) <= 54.

If this script reports infeasibility for every partition/merge, Q0 is killed
inside this arithmetic model. If it reports feasible profiles, those profiles
are not constructions; they are the remaining coarse shapes that the next
local lemma must attack.
"""

from __future__ import annotations

import argparse
import functools
import math
from dataclasses import dataclass
from typing import Iterable


LOW_OUTSIDE = 23
HIGH_OUTSIDE = 54
OUTSIDE_TOTAL = LOW_OUTSIDE + HIGH_OUTSIDE
GSTAR_EDGES = 511
W_DEGREE = 22
OUTSIDE_VERTEX_COUNT = 77
OUTSIDE_BIPLANAR_CAP = 6 * OUTSIDE_VERTEX_COUNT - 12
COUNT_CAP = 10**18


@dataclass(frozen=True)
class Chunk:
    """A surviving clique chunk in G*[N(v) - {u_i, u_j}]."""

    origin: int
    original_size: int
    t: int
    epsilon: int

    @property
    def demand(self) -> int:
        return self.t * (12 - self.t - self.epsilon)

    @property
    def selected(self) -> bool:
        return self.epsilon == 1


@dataclass(frozen=True)
class Option:
    """One local (f,p,h) choice for a chunk."""

    f: int
    p: int
    h: int
    low_used: int
    high_min: int
    low_nonselected: int
    high_nonselected: int


@dataclass(frozen=True)
class CaseResult:
    partition: tuple[int, ...]
    merge: tuple[int, int]
    chunks: tuple[Chunk, ...]
    feasible_count: int
    count_capped: bool
    witness: tuple[Option, ...] | None
    w_chunk_edges: int
    w_outside_edges: int
    chunk_internal_edges: int
    chunk_external_edges: int
    outside_edges: int

    @property
    def feasible(self) -> bool:
        return self.witness is not None

    @property
    def low_used(self) -> int:
        if self.witness is None:
            return 0
        return sum(o.low_used for o in self.witness)

    @property
    def high_min(self) -> int:
        if self.witness is None:
            return 0
        return sum(o.high_min for o in self.witness)

    @property
    def nonselected_vertices_min(self) -> int:
        if self.witness is None:
            return 0
        return sum(o.low_nonselected + o.high_nonselected for o in self.witness)


def integer_partitions(total: int, max_part: int, max_next: int | None = None) -> Iterable[tuple[int, ...]]:
    """Yield nonincreasing integer partitions of total with parts <= max_part."""

    if total == 0:
        yield ()
        return
    if max_next is None:
        max_next = min(total, max_part)
    for part in range(min(max_next, max_part, total), 0, -1):
        for rest in integer_partitions(total - part, max_part, part):
            yield (part,) + rest


def chunks_after_merge(partition: tuple[int, ...], a: int, b: int) -> tuple[Chunk, ...]:
    """Return surviving chunks after merging one vertex from parts a and b."""

    chunks: list[Chunk] = []
    selected = {a, b}
    for i, s in enumerate(partition):
        if i in selected:
            t = s - 1
            epsilon = 1
        else:
            t = s
            epsilon = 0
        if t > 0:
            chunks.append(Chunk(origin=i, original_size=s, t=t, epsilon=epsilon))
    return tuple(chunks)


def chunk_options(chunk: Chunk) -> list[Option]:
    """Enumerate local options for one chunk.

    For t=1, "full" and "single" low attachments are the same operation, so
    we put all low chunk edges into p and force f=0 to avoid duplicate profiles.
    """

    options: list[Option] = []
    t = chunk.t
    demand = chunk.demand
    max_f = 0 if t == 1 else min(8 - t, LOW_OUTSIDE, demand // t)
    for f in range(max_f + 1):
        low_edges_from_full = t * f
        remaining = demand - low_edges_from_full
        if remaining < 0:
            continue
        max_p = min(LOW_OUTSIDE - f, remaining)
        for p in range(max_p + 1):
            h = remaining - p
            high_min = 0 if h == 0 else math.ceil(h / t)
            if high_min > HIGH_OUTSIDE:
                continue
            low_used = f + p
            low_nonselected = 0 if chunk.selected else low_used
            high_nonselected = 0 if chunk.selected else high_min
            options.append(
                Option(
                    f=f,
                    p=p,
                    h=h,
                    low_used=low_used,
                    high_min=high_min,
                    low_nonselected=low_nonselected,
                    high_nonselected=high_nonselected,
                )
            )

    # Prefer witnesses that expose high demand rather than burning all low
    # vertices immediately; this tends to give more informative extremal shapes.
    options.sort(key=lambda o: (o.low_used, o.high_min, o.f, o.p, o.h))
    return options


def saturated_add(a: int, b: int) -> int:
    total = a + b
    return COUNT_CAP if total >= COUNT_CAP else total


def edge_accounting(chunks: tuple[Chunk, ...]) -> tuple[int, int, int, int, int]:
    """Return edge counts forced outside the profile choices."""

    w_chunk_edges = sum(c.t for c in chunks if c.selected)
    w_outside_edges = W_DEGREE - w_chunk_edges
    chunk_internal_edges = sum(c.t * (c.t - 1) // 2 for c in chunks)
    chunk_external_edges = sum(c.demand for c in chunks)
    outside_edges = (
        GSTAR_EDGES
        - chunk_internal_edges
        - w_chunk_edges
        - chunk_external_edges
        - w_outside_edges
    )
    return (
        w_chunk_edges,
        w_outside_edges,
        chunk_internal_edges,
        chunk_external_edges,
        outside_edges,
    )


def edge_accounting_possible(chunks: tuple[Chunk, ...]) -> bool:
    """Check profile-independent edge constraints."""

    _, w_outside_edges, _, _, outside_edges = edge_accounting(chunks)
    if w_outside_edges < 0 or w_outside_edges > OUTSIDE_TOTAL:
        return False
    if outside_edges < 0 or outside_edges > OUTSIDE_BIPLANAR_CAP:
        return False

    # Degree check on the outside-induced graph. This is equivalent to the
    # total edge count but kept explicit as a guard against formula drift.
    chunk_external_edges = sum(c.demand for c in chunks)
    outside_stubs = LOW_OUTSIDE * 11 + HIGH_OUTSIDE * 12 - chunk_external_edges - w_outside_edges
    if outside_stubs < 0 or outside_stubs % 2 != 0:
        return False
    return outside_stubs // 2 == outside_edges


def evaluate_case(partition: tuple[int, ...], a: int, b: int) -> CaseResult:
    chunks = chunks_after_merge(partition, a, b)
    (
        w_chunk_edges,
        w_outside_edges,
        chunk_internal_edges,
        chunk_external_edges,
        outside_edges,
    ) = edge_accounting(chunks)

    if not edge_accounting_possible(chunks):
        return CaseResult(
            partition=partition,
            merge=(a, b),
            chunks=chunks,
            feasible_count=0,
            count_capped=False,
            witness=None,
            w_chunk_edges=w_chunk_edges,
            w_outside_edges=w_outside_edges,
            chunk_internal_edges=chunk_internal_edges,
            chunk_external_edges=chunk_external_edges,
            outside_edges=outside_edges,
        )

    options_by_chunk = tuple(tuple(chunk_options(c)) for c in chunks)

    @functools.lru_cache(maxsize=None)
    def dp(
        i: int,
        low_used: int,
        high_min: int,
        nonselected_vertices_min: int,
    ) -> tuple[int, tuple[Option, ...] | None, bool]:
        if low_used > LOW_OUTSIDE or high_min > HIGH_OUTSIDE:
            return 0, None, False
        if nonselected_vertices_min > OUTSIDE_TOTAL:
            return 0, None, False
        if i == len(options_by_chunk):
            # w-neighbours outside N(v) must come from the two selected original
            # cliques, so vertices already committed to nonselected chunks cannot
            # also cover those w-outside edges.
            if w_outside_edges > OUTSIDE_TOTAL - nonselected_vertices_min:
                return 0, None, False
            return 1, (), False

        total = 0
        capped = False
        witness: tuple[Option, ...] | None = None
        for opt in options_by_chunk[i]:
            sub_count, sub_witness, sub_capped = dp(
                i + 1,
                low_used + opt.low_used,
                high_min + opt.high_min,
                nonselected_vertices_min + opt.low_nonselected + opt.high_nonselected,
            )
            if sub_count == 0:
                continue
            if witness is None and sub_witness is not None:
                witness = (opt,) + sub_witness
            new_total = saturated_add(total, sub_count)
            capped = capped or sub_capped or new_total == COUNT_CAP
            total = new_total
        return total, witness, capped

    count, witness, capped = dp(0, 0, 0, 0)
    return CaseResult(
        partition=partition,
        merge=(a, b),
        chunks=chunks,
        feasible_count=count,
        count_capped=capped,
        witness=witness,
        w_chunk_edges=w_chunk_edges,
        w_outside_edges=w_outside_edges,
        chunk_internal_edges=chunk_internal_edges,
        chunk_external_edges=chunk_external_edges,
        outside_edges=outside_edges,
    )


def enumerate_cases(include_symmetric_duplicates: bool = False) -> list[CaseResult]:
    results: list[CaseResult] = []
    for partition in integer_partitions(11, 7):
        if len(partition) < 2:
            continue
        seen_merge_sizes: set[tuple[int, int]] = set()
        for a in range(len(partition)):
            for b in range(a + 1, len(partition)):
                merge_sizes = (partition[a], partition[b])
                if not include_symmetric_duplicates and merge_sizes in seen_merge_sizes:
                    continue
                seen_merge_sizes.add(merge_sizes)
                results.append(evaluate_case(partition, a, b))
    return results


def fmt_chunks(chunks: tuple[Chunk, ...]) -> str:
    return ",".join(f"{c.t}:{c.epsilon}" for c in chunks) or "-"


def fmt_profile(chunks: tuple[Chunk, ...], witness: tuple[Option, ...] | None) -> str:
    if witness is None:
        return "-"
    parts = []
    for c, o in zip(chunks, witness):
        parts.append(f"t={c.t},eps={c.epsilon},f={o.f},p={o.p},h={o.h}")
    return " | ".join(parts)


def print_summary(results: list[CaseResult], args: argparse.Namespace) -> None:
    partitions = {r.partition for r in results}
    feasible = [r for r in results if r.feasible]
    infeasible = [r for r in results if not r.feasible]
    capped = [r for r in results if r.count_capped]

    print("# Q0 profile enumeration")
    print(f"# partitions={len(partitions)} merge_cases={len(results)}")
    print(f"# feasible_cases={len(feasible)} infeasible_cases={len(infeasible)} capped_counts={len(capped)}")
    print(
        "# constraints: sum(f+p)<=23, sum ceil(h/t)<=54, "
        "w_outside capacity after nonselected chunks, outside biplanar edge cap"
    )
    if not feasible:
        print("# verdict: INFEASIBLE in this profile model")
        return
    print("# verdict: FEASIBLE profiles remain (necessary-condition model only)")

    rows = feasible
    if args.only_min_low:
        min_low = min(r.low_used for r in feasible)
        rows = [r for r in feasible if r.low_used == min_low]
        print(f"# showing only min-low witnesses: low_used={min_low}")
    if args.limit is not None:
        rows = rows[: args.limit]

    cols = [
        "partition",
        "merge_sizes",
        "chunks(t:eps)",
        "count",
        "low_used",
        "high_min",
        "nonselected_min",
        "w_out",
        "outside_edges",
        "witness",
    ]
    print("# " + "\t".join(cols))
    for r in rows:
        count = f">={COUNT_CAP}" if r.count_capped else str(r.feasible_count)
        merge_sizes = f"{r.partition[r.merge[0]]},{r.partition[r.merge[1]]}"
        row = [
            ",".join(map(str, r.partition)),
            merge_sizes,
            fmt_chunks(r.chunks),
            count,
            str(r.low_used),
            str(r.high_min),
            str(r.nonselected_vertices_min),
            str(r.w_outside_edges),
            str(r.outside_edges),
            fmt_profile(r.chunks, r.witness),
        ]
        print("\t".join(row))


def print_all(results: list[CaseResult]) -> None:
    cols = [
        "partition",
        "merge_indices",
        "merge_sizes",
        "chunks(t:eps)",
        "feasible",
        "count",
        "low_used",
        "high_min",
        "nonselected_min",
        "w_chunk",
        "w_out",
        "chunk_internal",
        "chunk_external",
        "outside_edges",
        "witness",
    ]
    print("# " + "\t".join(cols))
    for r in results:
        count = f">={COUNT_CAP}" if r.count_capped else str(r.feasible_count)
        merge_sizes = f"{r.partition[r.merge[0]]},{r.partition[r.merge[1]]}"
        row = [
            ",".join(map(str, r.partition)),
            f"{r.merge[0]},{r.merge[1]}",
            merge_sizes,
            fmt_chunks(r.chunks),
            "yes" if r.feasible else "no",
            count,
            str(r.low_used),
            str(r.high_min),
            str(r.nonselected_vertices_min),
            str(r.w_chunk_edges),
            str(r.w_outside_edges),
            str(r.chunk_internal_edges),
            str(r.chunk_external_edges),
            str(r.outside_edges),
            fmt_profile(r.chunks, r.witness),
        ]
        print("\t".join(row))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Enumerate Q0 arithmetic profiles for the Earth-Moon Phase 6 isolated-low subcase."
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="print every partition/merge case instead of a feasible summary",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=40,
        help="maximum feasible rows to print in summary mode (default: 40; use -1 for no limit)",
    )
    parser.add_argument(
        "--only-min-low",
        action="store_true",
        help="in summary mode, show only feasible witnesses using the fewest low outside vertices",
    )
    parser.add_argument(
        "--include-symmetric-duplicates",
        action="store_true",
        help="do not collapse equal-size merge choices inside the same partition",
    )
    args = parser.parse_args()
    if args.limit is not None and args.limit < 0:
        args.limit = None
    return args


def main() -> None:
    args = parse_args()
    results = enumerate_cases(include_symmetric_duplicates=args.include_symmetric_duplicates)
    if args.all:
        print_all(results)
    else:
        print_summary(results, args)


if __name__ == "__main__":
    main()
