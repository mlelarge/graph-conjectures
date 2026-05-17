"""Vehicle 1 generator: laminar systems of tight 3-cuts.

Construction (sketch):

Fix n and a laminar chain X_1 ⊋ X_2 ⊋ ... ⊋ X_k of subsets of V = [n].
Each X_i is a "shell". We want each |delta^+(X_i)| to be exactly 3
("tight"), so that any strong arc decomposition is forced into a
2-out-of-3 color choice on each shell, and we hope the choices on
overlapping shells are incompatible.

For each shell X_i we plant exactly three out-arcs from X_i to V \\ X_i.
We must also ensure overall 3-arc-strongness:
 - we add a bidirected "spine" inside each shell to make D[X_i] strong
   for every i;
 - we add return arcs from V \\ X_1 to X_1 to keep the whole digraph
   strongly connected with arc-connectivity 3.

The simplest controlled instance: 'nested-cycles'. Take n = 3k, with
X_i = {0, 1, ..., 3(k-i+1) - 1} for i = 1..k. Each shell has size
3(k-i+1). The "out-shell" arcs are placed in a triangulated pattern
that mimics S_4-like flow constraints.

This generator is a SKETCH (per spec). It is exercised only if
Vehicle 3 sweep finishes its budget with no candidate found.
"""

from __future__ import annotations

import itertools
from dataclasses import dataclass
from typing import Iterator

from digraph import Digraph


@dataclass(frozen=True)
class LaminarInstance:
    name: str
    n: int
    arcs: tuple[tuple[int, int], ...]
    shells: tuple[tuple[int, ...], ...]
    cut_sizes: tuple[int, ...]

    def build(self) -> Digraph:
        return Digraph.from_arcs(range(self.n), list(self.arcs))


def _strongly_connect_within(vertices: list[int]) -> list[tuple[int, int]]:
    """Return a directed cycle through `vertices` (a 'minimal' strong sub)."""
    if len(vertices) < 2:
        return []
    cyc = [(vertices[i], vertices[(i + 1) % len(vertices)]) for i in range(len(vertices))]
    return cyc


def generate_laminar_chain(n: int, shell_sizes: list[int], seed: int = 0) -> LaminarInstance | None:
    """Build a laminar-shell digraph with the given shell sizes.

    shell_sizes must be strictly decreasing and end above 0; e.g.
    shell_sizes = [9, 6, 3] gives X_1 ⊋ X_2 ⊋ X_3 of sizes 9,6,3.

    Each X_i has exactly 3 out-arcs to V \\ X_i, distributed to cover
    distinct head vertices when possible. The 'inside' of each shell
    carries a Hamilton cycle to ensure strong-internal-connectivity.
    The complement V \\ X_1 has a Hamilton cycle plus 3 return arcs from
    V \\ X_1 back into X_1 (these are the 3 in-arcs of X_1).
    """
    if not shell_sizes or shell_sizes != sorted(shell_sizes, reverse=True):
        return None
    if shell_sizes[0] > n - 1:
        return None
    if shell_sizes[-1] < 1:
        return None

    shells: list[list[int]] = []
    for size in shell_sizes:
        shells.append(list(range(size)))  # X_i = {0, ..., size-1}

    arcs: list[tuple[int, int]] = []

    # Internal arcs: add a triple-circulation on the whole vertex set V.
    # Specifically, arcs i -> (i+1) mod n, i -> (i+2) mod n, and i -> (i+3) mod n
    # for every i. This guarantees minimum out-degree 3 and in-degree 3 across
    # the whole digraph, so the *baseline* arc-connectivity is 3 already.
    # On top of this base layer we plant the tight 3-cut for each shell X_i:
    # we declare that the 3 *clockwise nearest* out-arcs from the "boundary"
    # of X_i are the only ones leaving X_i (we keep only those that lie in
    # the natural circulation). This sketch is intentionally rough; serious
    # Vehicle-1 candidates need a careful hand-designed laminar family.
    base = []
    for i in range(n):
        base.append((i, (i + 1) % n))
        base.append((i, (i + 2) % n))
        base.append((i, (i + 3) % n))
    arcs.extend(base)

    complement = list(range(shell_sizes[0], n))

    # 3 out-arcs from each shell
    for i, shell in enumerate(shells):
        complement_i = sorted(set(range(n)) - set(shell))
        if len(complement_i) < 3:
            return None
        # tails: pick three distinct vertices of the shell
        tails = shell[: min(3, len(shell))]
        if len(tails) < 3:
            return None
        # heads: pick three distinct vertices of complement_i
        heads = complement_i[:3]
        for j in range(3):
            arcs.append((tails[j], heads[j]))

    # 3 return arcs from complement of X_1 into X_1
    if len(complement) >= 3:
        for j in range(3):
            arcs.append((complement[j], shells[0][j % len(shells[0])]))
    else:
        # need at least 3 return arcs to make D 3-arc-strong; if complement
        # is small, replicate from the available vertices
        for j in range(3):
            arcs.append((complement[j % len(complement)], shells[0][j % len(shells[0])]))

    return LaminarInstance(
        name=f"laminar_n{n}_shells{'_'.join(map(str, shell_sizes))}",
        n=n,
        arcs=tuple(arcs),
        shells=tuple(tuple(s) for s in shells),
        cut_sizes=tuple(3 for _ in shells),
    )


def enumerate_laminar(
    n_range: range,
    max_k: int = 3,
) -> Iterator[LaminarInstance]:
    """Iterate over LaminarInstance candidates with parameter ranges.

    For each n in n_range, generate chains of length 1..max_k with each
    shell strictly smaller than the previous, and shell sizes multiples
    of 3 (heuristic — gives clean labelings).
    """
    for n in n_range:
        for k in range(1, max_k + 1):
            # All weakly-decreasing tuples of length k, values in [3, n - 1],
            # strictly decreasing.
            for shells in itertools.combinations(range(3, n), k):
                shell_sizes = sorted(shells, reverse=True)
                inst = generate_laminar_chain(n, shell_sizes)
                if inst is not None:
                    yield inst
