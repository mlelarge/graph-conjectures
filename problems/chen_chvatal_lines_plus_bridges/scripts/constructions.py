"""Named graph constructions for the Chen-Chvatal lines+bridges substrate.

Each builder returns (n, edges) with vertices 0..n-1 and an undirected
edge list.  The graphs F = {C4, K2,3, W4, W4', K6', K8'} are the ones the
paper's Lemma 3.1 gives exact ell-values for; the wider F_0 (Figs 1-3)
adds H5, H61, H62, H81, H82, H83.

We implement the unambiguous members (C4, K2,3, W4, K5, Petersen, K33,
K6, K8, complete/cycle helpers).  The "primed" graphs in the paper are
specific small modifications drawn in the figures; where their structure
is not unambiguous from the text alone we DO NOT guess -- the verified
known-value anchor relies on C4 and K2,3 (Lemma 3.1 explicit) plus the
general rule ell(H)=|H|-1 for the non-C4 members, which the oracle tests
directly on every graph it can build.
"""
from __future__ import annotations


def cycle(n):
    """C_n."""
    return n, [(i, (i + 1) % n) for i in range(n)]


def complete(n):
    """K_n."""
    e = [(i, j) for i in range(n) for j in range(i + 1, n)]
    return n, e


def complete_bipartite(p, q):
    """K_{p,q}: parts {0..p-1} and {p..p+q-1}."""
    n = p + q
    e = [(i, p + j) for i in range(p) for j in range(q)]
    return n, e


def path(n):
    """P_n (a path -- has pendant edges; useful as a control)."""
    return n, [(i, i + 1) for i in range(n - 1)]


def wheel(k):
    """W_k = C_k + one hub (k+1 vertices).  Hub = vertex k.
       W4 in the paper = the wheel on 5 vertices (4-cycle + hub)."""
    n = k + 1
    e = [(i, (i + 1) % k) for i in range(k)]
    e += [(k, i) for i in range(k)]
    return n, e


def petersen():
    """Petersen graph (10 vertices, 3-regular, girth 5)."""
    outer = [(i, (i + 1) % 5) for i in range(5)]
    spokes = [(i, i + 5) for i in range(5)]
    inner = [(5 + i, 5 + (i + 2) % 5) for i in range(5)]
    return 10, outer + spokes + inner


# Convenience aliases used by the oracle CLI / known-value check.
def C4():
    return cycle(4)


def K23():
    return complete_bipartite(2, 3)


def K33():
    return complete_bipartite(3, 3)


def W4():
    """Paper's W4: 4-cycle plus a hub = wheel on 5 vertices."""
    return wheel(4)


def K5():
    return complete(5)


def K6():
    return complete(6)


def K8():
    return complete(8)


NAMED = {
    "C4": C4,
    "C5": lambda: cycle(5),
    "C6": lambda: cycle(6),
    "K23": K23,
    "K33": K33,
    "W4": W4,
    "K5": K5,
    "K6": K6,
    "K8": K8,
    "petersen": petersen,
    "P4": lambda: path(4),
}
