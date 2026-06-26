"""Witness chain for the two-free-colours lemma.

If colours 0 and 1 are backward-free, the order refines lexicographic digit
order 0<1<2.  On the {0,2}^k subcube, colour 2 is the reverse lex chain, hence it
is fully backward and has size 2^k.
"""

from __future__ import annotations

from stilde_crossing_recursion import is_below
from stilde_pod_profiles import word


def vertex_from_word(digits):
    value = 0
    for digit in digits:
        value = 3 * value + digit
    return value


def two_symbol_chain(depth, colour):
    """Maximum P_colour chain on words using symbols colour, colour+1."""

    lo = colour
    hi = (colour + 1) % 3
    # P_colour-increasing lex order has digit order colour < colour+1.
    words = []
    for mask in range(2**depth):
        digits = []
        for shift in range(depth - 1, -1, -1):
            digits.append(hi if ((mask >> shift) & 1) else lo)
        words.append(tuple(digits))
    return tuple(vertex_from_word(digits) for digits in words)


def is_colour_chain(vertices, depth, colour):
    return all(
        is_below(vertices[i], vertices[j], depth, colour)
        for i in range(len(vertices))
        for j in range(i + 1, len(vertices))
    )


def forced_missing_colour_chain(depth, missing_colour=2):
    return two_symbol_chain(depth, missing_colour)


if __name__ == "__main__":
    for depth in range(1, 7):
        chain = forced_missing_colour_chain(depth, 2)
        assert len(chain) == 2**depth
        assert is_colour_chain(chain, depth, 2)
        print(depth, len(chain), [word(v, depth) for v in chain[: min(4, len(chain))]])
