"""Probe whether partial component connectivity is genuinely necessary.

This is not a solver. It searches for two valid partial LFO construction
states in the same tournament with the same coarse data

    (placed set, current degree vector)

but different connected-component partitions of the partial backedge
forest, and different extendability to a full LFO.

Such a witness proves that a DP cannot forget component connectivity
and remember only remaining vertices plus degrees.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from collections import defaultdict
from functools import lru_cache
from itertools import product, permutations
from typing import Iterable, Sequence

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

Matrix = Sequence[Sequence[int]]


COMPONENT_WITNESS_T = [
    [0, 0, 0, 0, 0, 0, 0],
    [1, 0, 0, 0, 0, 0, 0],
    [1, 1, 0, 0, 0, 0, 1],
    [1, 1, 1, 0, 0, 0, 0],
    [1, 1, 1, 1, 0, 0, 0],
    [1, 1, 1, 1, 1, 0, 0],
    [1, 1, 0, 1, 1, 1, 0],
]

COMPONENT_PREFIX_BAD = [5, 2, 6, 3]
COMPONENT_PREFIX_GOOD = [6, 3, 5, 2]
COMPONENT_PREFIX_SET = frozenset(COMPONENT_PREFIX_BAD)


def _find(parent: list[int], x: int) -> int:
    while parent[x] != x:
        parent[x] = parent[parent[x]]
        x = parent[x]
    return x


def _union(parent: list[int], a: int, b: int) -> None:
    ra = _find(parent, a)
    rb = _find(parent, b)
    if ra != rb:
        parent[rb] = ra


def _iter_bits(mask: int):
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask ^= bit


def _canonical_parent(parent: Sequence[int]) -> tuple[int, ...]:
    par = list(parent)
    blocks: dict[int, list[int]] = defaultdict(list)
    for v in range(len(parent)):
        blocks[_find(par, v)].append(v)
    out = [0] * len(parent)
    for block in blocks.values():
        rep = min(block)
        for v in block:
            out[v] = rep
    return tuple(out)


def _component_blocks(parent: Sequence[int], placed_mask: int) -> tuple[tuple[int, ...], ...]:
    par = list(parent)
    blocks: dict[int, list[int]] = defaultdict(list)
    for v in _iter_bits(placed_mask):
        blocks[_find(par, v)].append(v)
    return tuple(sorted(tuple(sorted(block)) for block in blocks.values()))


def _outmasks(T: Matrix) -> list[int]:
    n = len(T)
    return [
        sum((1 << v) for v in range(n) if T[u][v])
        for u in range(n)
    ]


def _add_vertex(
    outmask: Sequence[int],
    prefix_mask: int,
    degree: Sequence[int],
    parent: Sequence[int],
    x: int,
) -> tuple[tuple[int, ...], tuple[int, ...]] | None:
    deg = list(degree)
    par = list(parent)
    for p in _iter_bits(outmask[x] & prefix_mask):
        if deg[x] >= 2 or deg[p] >= 2:
            return None
        if _find(par, x) == _find(par, p):
            return None
        deg[x] += 1
        deg[p] += 1
        _union(par, x, p)
    return tuple(deg), tuple(par)


def has_completion(
    T: Matrix,
    prefix_mask: int,
    degree: tuple[int, ...],
    parent: tuple[int, ...],
) -> bool:
    n = len(T)
    outmask = _outmasks(T)
    all_mask = (1 << n) - 1

    @lru_cache(maxsize=None)
    def rec(prefix: int, deg: tuple[int, ...], par_sig: tuple[int, ...]) -> bool:
        if prefix == all_mask:
            return True
        par = list(par_sig)
        remaining = all_mask ^ prefix
        candidates = sorted(
            _iter_bits(remaining),
            key=lambda x: (outmask[x] & prefix).bit_count(),
            reverse=True,
        )
        for x in candidates:
            nxt = _add_vertex(outmask, prefix, deg, par, x)
            if nxt is None:
                continue
            nd, np = nxt
            if rec(prefix | (1 << x), nd, _canonical_parent(np)):
                return True
        return False

    return rec(prefix_mask, degree, _canonical_parent(parent))


def valid_prefix_state(
    T: Matrix,
    prefix: Sequence[int],
) -> tuple[tuple[int, ...], tuple[int, ...]] | None:
    n = len(T)
    outmask = _outmasks(T)
    prefix_mask = 0
    degree: tuple[int, ...] = tuple([0] * n)
    parent: tuple[int, ...] = tuple(range(n))
    for x in prefix:
        nxt = _add_vertex(outmask, prefix_mask, degree, parent, x)
        if nxt is None:
            return None
        degree, parent = nxt
        prefix_mask |= 1 << x
    return degree, parent


def prefixes(n: int, depth: int) -> Iterable[tuple[int, ...]]:
    for k in range(1, depth + 1):
        yield from permutations(range(n), k)


def find_component_connectivity_witness(T: Matrix, depth: int = 5) -> dict | None:
    """Return a witness where component partition changes extendability."""
    n = len(T)
    grouped: dict[tuple[int, tuple[int, ...]], list[dict]] = defaultdict(list)
    checked = 0
    for prefix in prefixes(n, depth):
        state = valid_prefix_state(T, prefix)
        if state is None:
            continue
        checked += 1
        degree, parent = state
        prefix_mask = sum(1 << v for v in prefix)
        key = (prefix_mask, degree)
        blocks = _component_blocks(parent, prefix_mask)
        ext = has_completion(T, prefix_mask, degree, parent)
        row = {
            "prefix": list(prefix),
            "prefix_mask": prefix_mask,
            "degree": list(degree),
            "components": [list(block) for block in blocks],
            "extendable": ext,
        }
        for other in grouped[key]:
            if other["components"] != row["components"] and other["extendable"] != ext:
                return {
                    "n": n,
                    "depth": depth,
                    "checked_valid_prefixes": checked,
                    "coarse_key": {
                        "prefix_mask": prefix_mask,
                        "degree": list(degree),
                    },
                    "state_a": other,
                    "state_b": row,
                    "T": [list(r) for r in T],
                }
        grouped[key].append(row)
    return None


def load_lfo_full_n7_records(path: str) -> list[dict]:
    data = json.load(open(path))
    records = []
    for bucket in data["buckets"]:
        records.extend(bucket["records"])
    return records


def search_n7_census(path: str, depth: int = 5, limit: int | None = None) -> dict:
    records = load_lfo_full_n7_records(path)
    for i, rec in enumerate(records[:limit]):
        witness = find_component_connectivity_witness(rec["T"], depth=depth)
        if witness is not None:
            witness["record_index"] = i
            witness["score_sequence"] = rec["score_sequence"]
            witness["has_lfo"] = rec["has_lfo"]
            return witness
    return {
        "found": False,
        "records_checked": len(records if limit is None else records[:limit]),
        "depth": depth,
    }


def cut_isolated_sum(T: Matrix, prefix_set: set[int] | frozenset[int], copies: int) -> list[list[int]]:
    """Repeat a prefix witness without cross-copy backedges at the cut.

    Vertices in the chosen prefix set of every copy form the global
    prefix side; all other vertices form the suffix side. Cross-copy arcs
    are oriented forward in the cut order

        prefix copy 0, ..., prefix copy k-1, suffix copy 0, ..., suffix copy k-1.

    Thus, when each copy contributes its local prefix first and its local
    suffix later, all cross-copy arcs are forward. Extendability then
    factors through the copies.
    """
    if copies < 1:
        raise ValueError("copies must be positive")
    block = len(T)
    n = block * copies
    out = [[0] * n for _ in range(n)]

    def key(v: int) -> tuple[int, int]:
        c, local = divmod(v, block)
        return (0 if local in prefix_set else 1, c)

    for u in range(n):
        cu, lu = divmod(u, block)
        for v in range(u + 1, n):
            cv, lv = divmod(v, block)
            if cu == cv:
                if T[lu][lv]:
                    out[u][v] = 1
                else:
                    out[v][u] = 1
            elif key(u) < key(v):
                out[u][v] = 1
            else:
                out[v][u] = 1
    return out


def component_family_prefix(pattern: Sequence[str]) -> list[int]:
    """Return a global prefix for a good/bad pattern over witness copies."""
    block = len(COMPONENT_WITNESS_T)
    out: list[int] = []
    for c, tag in enumerate(pattern):
        if tag == "good":
            local = COMPONENT_PREFIX_GOOD
        elif tag == "bad":
            local = COMPONENT_PREFIX_BAD
        else:
            raise ValueError("pattern entries must be 'good' or 'bad'")
        out.extend(c * block + v for v in local)
    return out


def analyze_component_family(pattern: Sequence[str]) -> dict:
    """Analyze a repeated component-connectivity pattern."""
    T = cut_isolated_sum(COMPONENT_WITNESS_T, COMPONENT_PREFIX_SET, len(pattern))
    prefix = component_family_prefix(pattern)
    state = valid_prefix_state(T, prefix)
    if state is None:
        raise AssertionError("constructed prefix should be valid")
    degree, parent = state
    prefix_mask = sum(1 << v for v in prefix)
    return {
        "pattern": list(pattern),
        "n": len(T),
        "prefix_len": len(prefix),
        "prefix_mask": prefix_mask,
        "degree": list(degree),
        "components": [list(block) for block in _component_blocks(parent, prefix_mask)],
        "extendable": has_completion(T, prefix_mask, degree, parent),
    }


def component_family_entropy(copies: int) -> dict:
    """Enumerate the repeated good/bad component states.

    All patterns have the same placed set and degree vector. The only
    changing datum is the component pairing inside each copy.
    """
    if copies < 1:
        raise ValueError("copies must be positive")
    rows = []
    for bits in product(["good", "bad"], repeat=copies):
        row = analyze_component_family(bits)
        rows.append(row)
    coarse_keys = {
        (
            row["prefix_mask"],
            tuple(row["degree"]),
        )
        for row in rows
    }
    component_keys = {
        tuple(tuple(block) for block in row["components"])
        for row in rows
    }
    extendable_patterns = [
        row["pattern"]
        for row in rows
        if row["extendable"]
    ]
    return {
        "copies": copies,
        "states": len(rows),
        "coarse_key_count": len(coarse_keys),
        "component_partition_count": len(component_keys),
        "extendable_count": len(extendable_patterns),
        "extendable_patterns": extendable_patterns,
        "all_same_coarse_key": len(coarse_keys) == 1,
        "all_component_partitions_distinct": len(component_keys) == len(rows),
    }


def _candidate_signature(row: dict, name: str):
    components = [tuple(block) for block in row["components"]]
    degree = tuple(row["degree"])
    if name == "degree_only":
        return (row["prefix_mask"], degree)
    if name == "component_count":
        return (row["prefix_mask"], degree, len(components))
    if name == "component_size_multiset":
        return (row["prefix_mask"], degree, tuple(sorted(len(c) for c in components)))
    if name == "low_degree_set_and_component_count":
        low = tuple(i for i, d in enumerate(degree) if d < 2)
        return (row["prefix_mask"], degree, low, len(components))
    if name == "component_partition":
        return (row["prefix_mask"], degree, tuple(sorted(components)))
    raise ValueError(f"unknown candidate signature: {name}")


def component_equivalence_summary(copies: int) -> dict:
    """Test simple component-state quotients on the repeated family."""
    if copies < 1:
        raise ValueError("copies must be positive")
    rows = [
        analyze_component_family(bits)
        for bits in product(["good", "bad"], repeat=copies)
    ]
    names = [
        "degree_only",
        "component_count",
        "component_size_multiset",
        "low_degree_set_and_component_count",
        "component_partition",
    ]
    out = {
        "copies": copies,
        "states": len(rows),
        "candidates": {},
    }
    for name in names:
        buckets: dict[object, list[dict]] = defaultdict(list)
        for row in rows:
            buckets[_candidate_signature(row, name)].append(row)
        mixed = [
            bucket for bucket in buckets.values()
            if len({row["extendable"] for row in bucket}) > 1
        ]
        out["candidates"][name] = {
            "bucket_count": len(buckets),
            "largest_bucket": max(len(bucket) for bucket in buckets.values()),
            "mixed_extendability_buckets": len(mixed),
            "mixed_largest_bucket": max((len(bucket) for bucket in mixed), default=0),
            "sound_on_family": not mixed,
        }
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n7-json", default=os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "data",
        "lfo_full_n7.json",
    ))
    parser.add_argument("--depth", type=int, default=5)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--component-family", nargs="*", choices=["good", "bad"])
    parser.add_argument("--entropy", type=int)
    parser.add_argument("--equivalence", type=int)
    args = parser.parse_args()
    if args.equivalence is not None:
        out = component_equivalence_summary(args.equivalence)
    elif args.entropy is not None:
        out = component_family_entropy(args.entropy)
    elif args.component_family:
        out = analyze_component_family(args.component_family)
    else:
        out = search_n7_census(args.n7_json, args.depth, args.limit)
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
