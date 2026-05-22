"""Small canonical labeling utilities for tournaments.

The earlier n<=8 scripts used score-respecting permutations directly.
That is good enough when score classes are small, but it is the wrong
primitive for n=9 because regular tournaments have one score class of
size 9.

This module implements a compact individualization/refinement canonical
form. It is deliberately simple, exact, and dependency-free. The
refinement invariant for a vertex is its vector of out-neighbor counts
into the current cells.
"""
from __future__ import annotations

from collections import defaultdict
from typing import Sequence


Matrix = Sequence[Sequence[int]]


def score_vector(T: Matrix) -> list[int]:
    return [sum(row) for row in T]


def initial_partition(T: Matrix) -> tuple[tuple[int, ...], ...]:
    groups: dict[int, list[int]] = defaultdict(list)
    for v, s in enumerate(score_vector(T)):
        groups[s].append(v)
    return tuple(tuple(groups[s]) for s in sorted(groups))


def refine_partition(
    T: Matrix,
    partition: tuple[tuple[int, ...], ...],
) -> tuple[tuple[int, ...], ...]:
    """Refine a partition by out-count signatures until stable."""
    while True:
        new_parts: list[tuple[int, ...]] = []
        for cell in partition:
            buckets: dict[tuple[int, ...], list[int]] = defaultdict(list)
            for v in cell:
                sig = tuple(sum(T[v][u] for u in block) for block in partition)
                buckets[sig].append(v)
            for sig in sorted(buckets):
                new_parts.append(tuple(buckets[sig]))
        new_partition = tuple(new_parts)
        if new_partition == partition:
            return partition
        partition = new_partition


def flat_key_for_order(T: Matrix, order: tuple[int, ...]) -> bytes:
    n = len(T)
    return bytes(T[order[i]][order[j]] for i in range(n) for j in range(n))


def canonical_key(T: Matrix) -> bytes:
    """Return a canonical flattened adjacency matrix as bytes of 0/1."""
    n = len(T)

    def rec(partition: tuple[tuple[int, ...], ...]) -> bytes:
        partition = refine_partition(T, partition)
        if len(partition) == n:
            return flat_key_for_order(T, tuple(cell[0] for cell in partition))

        split_idx = min(
            (i for i, cell in enumerate(partition) if len(cell) > 1),
            key=lambda i: len(partition[i]),
        )
        cell = partition[split_idx]
        best = None
        for v in cell:
            rest = tuple(x for x in cell if x != v)
            new_partition = (
                partition[:split_idx]
                + ((v,), rest)
                + partition[split_idx + 1:]
            )
            key = rec(new_partition)
            if best is None or key < best:
                best = key
        assert best is not None
        return best

    return rec(initial_partition(T))


def key_to_string(key: bytes) -> str:
    return "".join("1" if x else "0" for x in key)


def string_to_matrix(raw: str) -> list[list[int]]:
    n2 = len(raw)
    n = int(n2 ** 0.5)
    if n * n != n2:
        raise ValueError("canonical string length must be a square")
    values = [1 if ch == "1" else 0 for ch in raw]
    return [values[i * n:(i + 1) * n] for i in range(n)]


def matrix_to_upper_bits(T: Matrix) -> str:
    n = len(T)
    return "".join("1" if T[i][j] else "0" for i in range(n) for j in range(i + 1, n))


def upper_bits_to_matrix(bits: str, n: int) -> list[list[int]]:
    expected = n * (n - 1) // 2
    if len(bits) != expected:
        raise ValueError(f"expected {expected} bits for n={n}, got {len(bits)}")
    T = [[0] * n for _ in range(n)]
    idx = 0
    for i in range(n):
        for j in range(i + 1, n):
            if bits[idx] == "1":
                T[i][j] = 1
            else:
                T[j][i] = 1
            idx += 1
    return T
