"""Block-crossing recursion for the layer heights q_c of B_k = C3[B_{k-1}].

Decompose B_k into modules M_0, M_1, M_2 (top coordinate fixed), each a copy
of B_{k-1}, with the cyclic inter-module relation M_b => M_{b+1} carrying
colour b at the top coordinate.

A backward colour-c chain in an order pi is P_c-increasing and pi-decreasing.
Because the only top-level colour-c comparabilities run M_c => M_{c+1}, every
colour-c chain lies either entirely inside M_{c+2}, or inside M_c cup M_{c+1}
crossing once (the M_c part on the pi-suffix, the M_{c+1} part on the prefix).
Hence

    q_c(pi) = max( q_c(pi|M_{c+2}),
                   max_p [ suffix_c(M_c, p) + prefix_c(M_{c+1}, p) ] )

where suffix_c(M, p) / prefix_c(M, p) are the longest backward colour-c chains
inside module M restricted to pi-positions >= p / < p.

This module verifies that identity against the direct computation of q_c
(longest backward colour-c chain) on arbitrary orders.
"""

from __future__ import annotations

from stilde_pod_profiles import arc_colour, word


def is_below(left, right, depth, colour):
    """True iff left <_{P_colour} right, i.e. arc left->right has this colour."""
    a, b = word(left, depth), word(right, depth)
    for x, y in zip(a, b):
        if x != y:
            return x == colour and y == (x + 1) % 3
    return False


def longest_backward_chain(vertices, position, depth, colour):
    """Longest backward colour-`colour` chain among `vertices` (a subset)."""
    ordered = sorted(vertices, key=position.__getitem__)  # pi-increasing
    best = {v: 1 for v in ordered}
    # A chain is P_colour-increasing and pi-decreasing; scan pi-increasing and
    # let each v extend chains of vertices that come AFTER it in pi (already
    # seen are pi-smaller, so v sits on top as the pi-largest = chain start).
    for i, v in enumerate(ordered):
        for u in ordered[:i]:  # position[u] < position[v]
            if is_below(v, u, depth, colour):  # v <_{P} u, u is pi-backward of v
                best[v] = max(best[v], best[u] + 1)
    return max(best.values(), default=0)


def direct_q(order, depth, colour):
    position = {v: i for i, v in enumerate(order)}
    return longest_backward_chain(order, position, depth, colour)


def crossing_term(order, depth, colour):
    """max_p [ suffix_c(M_c, p) + prefix_c(M_{c+1}, p) ]."""
    position = {v: i for i, v in enumerate(order)}
    m_lo = [v for v in order if word(v, depth)[0] == colour]            # M_c
    m_hi = [v for v in order if word(v, depth)[0] == (colour + 1) % 3]  # M_{c+1}
    best = 0
    for p in range(len(order) + 1):
        suffix = longest_backward_chain(
            [v for v in m_lo if position[v] >= p], position, depth, colour
        )
        prefix = longest_backward_chain(
            [v for v in m_hi if position[v] < p], position, depth, colour
        )
        best = max(best, suffix + prefix)
    return best


def recursion_q(order, depth, colour):
    position = {v: i for i, v in enumerate(order)}
    m_far = [v for v in order if word(v, depth)[0] == (colour + 2) % 3]  # M_{c+2}
    inner = longest_backward_chain(m_far, position, depth, colour)
    return max(inner, crossing_term(order, depth, colour))


def check_order(order, depth):
    return all(
        direct_q(order, depth, c) == recursion_q(order, depth, c)
        for c in range(3)
    )


if __name__ == "__main__":
    import itertools
    import random

    for depth in (1, 2):  # exhaustive
        n = 3**depth
        count = 0
        for perm in itertools.permutations(range(n)):
            assert check_order(list(perm), depth), (depth, perm)
            count += 1
        print(f"depth {depth}: all {count} orders OK")

    rng = random.Random(0)  # depth 3 (n!=27! too large): random sample
    for depth in (3,):
        n = 3**depth
        trials = 2000
        for _ in range(trials):
            perm = list(range(n))
            rng.shuffle(perm)
            assert check_order(perm, depth), (depth, perm)
        print(f"depth {depth}: {trials} random orders OK")
