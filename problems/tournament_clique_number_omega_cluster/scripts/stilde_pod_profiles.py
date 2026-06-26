"""Canonical partial-order profiles for orders of the iterated C3 tower.

Write B_k=C3^k[TT_1], with vertices represented by words in {0,1,2}^k.
Colour an arc by c when its first differing coordinate is c -> c+1 mod 3.
The arcs of each colour form a partial order P_c.

For a vertex order pi, Q_c consists of the P_c arcs that are backward in pi.
It is again a partial order.  Its height q_c is the clique number of the
corresponding comparability layer.  Longest-path ranks in the three Q_c give
a proper colouring of the full backedge graph by rank triples.
"""

from __future__ import annotations

from collections import Counter


def word(vertex, depth):
    digits = [0] * depth
    for index in range(depth - 1, -1, -1):
        digits[index] = vertex % 3
        vertex //= 3
    return tuple(digits)


def arc_colour(left, right, depth):
    """Return the colour of the tournament arc between two vertices."""
    a = word(left, depth)
    b = word(right, depth)
    for x, y in zip(a, b):
        if x != y:
            if y == (x + 1) % 3:
                return x
            return y
    raise ValueError("arc_colour requires distinct vertices")


def layer_ranks(order, depth, colour):
    """Longest-chain ranks in the backward part of canonical poset P_colour."""
    position = {vertex: index for index, vertex in enumerate(order)}
    alphabet = (colour, (colour + 2) % 3, (colour + 1) % 3)
    alphabet_rank = {symbol: index for index, symbol in enumerate(alphabet)}
    topological = sorted(
        order,
        key=lambda vertex: tuple(alphabet_rank[x] for x in word(vertex, depth)),
    )

    rank = {vertex: 1 for vertex in order}
    for right_index, right in enumerate(topological):
        for left in topological[:right_index]:
            if (
                arc_colour(left, right, depth) == colour
                and position[right] < position[left]
            ):
                rank[right] = max(rank[right], rank[left] + 1)
    return rank


def pod_profile(order, depth):
    expected = 3**depth
    if sorted(order) != list(range(expected)):
        raise ValueError(f"order must be a permutation of range({expected})")

    ranks = [layer_ranks(order, depth, colour) for colour in range(3)]
    fibres = Counter(
        tuple(rank[vertex] for rank in ranks)
        for vertex in order
    )
    heights = [max(rank.values()) for rank in ranks]
    return {
        "depth": depth,
        "order": expected,
        "layer_heights": heights,
        "height_product": heights[0] * heights[1] * heights[2],
        "occupied_rank_triples": len(fibres),
        "largest_rank_fibre": max(fibres.values()),
        "average_occupied_rank_fibre": expected / len(fibres),
        "maximum_transitive_set": 2**depth,
        "rank_fibre_histogram": dict(sorted(Counter(fibres.values()).items())),
    }
