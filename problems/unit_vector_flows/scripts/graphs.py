"""Cubic-graph constructors for unit-vector-flow experiments.

Every constructor returns a simple ``networkx.Graph`` with integer-labelled
nodes. Cubicity (3-regularity) and bridgelessness are not enforced; the
caller checks via :func:`is_cubic_bridgeless`.
"""
from __future__ import annotations

import networkx as nx


def _canonicalize(G: nx.Graph) -> nx.Graph:
    """Return a copy of G with nodes ``0..n-1`` and **sorted** iteration order.

    This is required so that ``nx.to_graph6_bytes`` (which uses iteration
    order, not sorted order) round-trips deterministically.
    """
    try:
        nodes = sorted(G.nodes())
    except TypeError:
        nodes = sorted(G.nodes(), key=repr)
    relabel = {n: i for i, n in enumerate(nodes)}
    H = nx.Graph()
    H.add_nodes_from(range(len(nodes)))
    H.add_edges_from((relabel[u], relabel[v]) for u, v in G.edges())
    return H


def is_cubic_bridgeless(G: nx.Graph) -> bool:
    if not all(d == 3 for _, d in G.degree()):
        return False
    return nx.edge_connectivity(G) >= 2


def petersen() -> nx.Graph:
    return _canonicalize(nx.petersen_graph())


def k4() -> nx.Graph:
    return _canonicalize(nx.complete_graph(4))


def q3() -> nx.Graph:
    return _canonicalize(nx.hypercube_graph(3))


def prism(n: int) -> nx.Graph:
    if n < 3:
        raise ValueError("prism order must be >= 3")
    G = nx.Graph()
    for i in range(n):
        G.add_edge(i, (i + 1) % n)
        G.add_edge(n + i, n + (i + 1) % n)
        G.add_edge(i, n + i)
    return _canonicalize(G)


def moebius_kantor() -> nx.Graph:
    """Generalised Petersen graph GP(8,3); cubic, 3-edge-colourable."""
    return _canonicalize(nx.moebius_kantor_graph())


def desargues() -> nx.Graph:
    """GP(10,3); cubic, bipartite, 3-edge-colourable."""
    return _canonicalize(nx.desargues_graph())


def heawood() -> nx.Graph:
    """Cubic, bipartite, 3-edge-colourable, girth 6."""
    return _canonicalize(nx.heawood_graph())


def flower_snark(k: int) -> nx.Graph:
    """Isaacs flower snark :math:`J_{2k+1}` for ``k >= 2``.

    Construction: ``n = 2k+1`` star-units :math:`K_{1,3}` with centres
    :math:`a_i` and leaves :math:`b_i, c_i, d_i`; add the cycle on the
    :math:`b_i`, and the doubled cycle :math:`c_0 c_1 \\dots c_{n-1}
    d_0 d_1 \\dots d_{n-1} c_0`.
    """
    if k < 2:
        raise ValueError("flower snark requires k >= 2; J_5 is the smallest")
    n = 2 * k + 1
    G = nx.Graph()
    for i in range(n):
        G.add_edge(("a", i), ("b", i))
        G.add_edge(("a", i), ("c", i))
        G.add_edge(("a", i), ("d", i))
        G.add_edge(("b", i), ("b", (i + 1) % n))
    for i in range(n - 1):
        G.add_edge(("c", i), ("c", i + 1))
        G.add_edge(("d", i), ("d", i + 1))
    G.add_edge(("c", n - 1), ("d", 0))
    G.add_edge(("d", n - 1), ("c", 0))
    return _canonicalize(G)


def blanusa_first() -> nx.Graph:
    """First Blanuša snark: 18 vertices, 27 edges. Edge list transcribed
    from SageMath ``BlanusaFirstSnarkGraph`` (smallgraphs.py)."""
    G = nx.Graph()
    extras = [
        (0, 5), (1, 17), (2, 14), (3, 8), (4, 17),
        (6, 11), (7, 17), (9, 13), (10, 15), (12, 16),
    ]
    for u, v in extras:
        G.add_edge(u, v)
    for i in range(16):
        G.add_edge(i, i + 1)
    G.add_edge(0, 16)
    return _canonicalize(G)


def blanusa_second() -> nx.Graph:
    """Second Blanuša snark: 18 vertices, 27 edges. Adjacency transcribed
    from SageMath ``BlanusaSecondSnarkGraph`` (smallgraphs.py)."""
    G = nx.Graph()
    c0, c1 = ("c", 0), ("c", 1)
    explicit = [
        (c0, (0, 0)), (c0, (1, 4)), (c0, c1),
        (c1, (0, 3)), (c1, (1, 1)),
        ((0, 2), (0, 5)), ((0, 6), (0, 4)), ((0, 7), (0, 1)),
        ((1, 7), (1, 2)), ((1, 0), (1, 6)), ((1, 3), (1, 5)),
    ]
    for u, v in explicit:
        G.add_edge(u, v)
    cycles = [
        [(0, i) for i in range(5)],
        [(1, i) for i in range(5)],
        [(0, 5), (0, 6), (0, 7), (1, 5), (1, 6), (1, 7)],
    ]
    for cyc in cycles:
        for i, u in enumerate(cyc):
            G.add_edge(u, cyc[(i + 1) % len(cyc)])
    return _canonicalize(G)


def flower_snark_with_labels(k: int) -> tuple[nx.Graph, dict[tuple[int, int], str]]:
    """Same as :func:`flower_snark`, but also returns a map from each
    canonical edge ``(u, v)`` (with ``u < v``) to its type label, one of:

    * ``"spoke_b"``: edge :math:`a_i b_i`
    * ``"spoke_c"``: edge :math:`a_i c_i`
    * ``"spoke_d"``: edge :math:`a_i d_i`
    * ``"b_cycle"``: edge :math:`b_i b_{i+1 \\bmod n}`
    * ``"cd_cycle"``: edge in the alternating ``c/d`` cycle
    """
    if k < 2:
        raise ValueError("flower snark requires k >= 2; J_5 is the smallest")
    n = 2 * k + 1
    G = nx.Graph()
    raw_labels: dict[tuple, str] = {}
    for i in range(n):
        for tag, leaf in (("spoke_b", "b"), ("spoke_c", "c"), ("spoke_d", "d")):
            u, v = ("a", i), (leaf, i)
            G.add_edge(u, v)
            raw_labels[tuple(sorted((u, v), key=str))] = tag
        u, v = ("b", i), ("b", (i + 1) % n)
        G.add_edge(u, v)
        raw_labels[tuple(sorted((u, v), key=str))] = "b_cycle"
    for i in range(n - 1):
        for leaf in ("c", "d"):
            u, v = (leaf, i), (leaf, i + 1)
            G.add_edge(u, v)
            raw_labels[tuple(sorted((u, v), key=str))] = "cd_cycle"
    for u, v in ((("c", n - 1), ("d", 0)), (("d", n - 1), ("c", 0))):
        G.add_edge(u, v)
        raw_labels[tuple(sorted((u, v), key=str))] = "cd_cycle"

    # canonicalise to integer labels and translate raw_labels accordingly.
    # Match _canonicalize: prefer the natural tuple ordering and fall back
    # to repr only when nodes are heterogeneous.
    try:
        nodes = sorted(G.nodes())
    except TypeError:
        nodes = sorted(G.nodes(), key=repr)
    relabel = {n_: i for i, n_ in enumerate(nodes)}
    H = nx.Graph()
    H.add_nodes_from(range(len(nodes)))
    label: dict[tuple[int, int], str] = {}
    for (u, v), tag in raw_labels.items():
        i, j = relabel[u], relabel[v]
        a, b = (i, j) if i < j else (j, i)
        H.add_edge(a, b)
        label[(a, b)] = tag
    return H, label


def k4_bridge_dumbbell() -> nx.Graph:
    """Two copies of ``K_4`` with one edge subdivided, joined by a bridge
    between the two subdivision vertices. 10 vertices, 15 edges, cubic,
    bridgeless = False (one bridge by construction).

    No S²-flow: summing the Kirchhoff equations over either side of the
    bridge forces the bridge's flow vector to be zero, contradicting its
    unit-norm constraint. Used as a negative-calibration target.
    """
    G = nx.Graph()
    A = [(0, 2), (0, 3), (1, 2), (1, 3), (2, 3), (0, 4), (1, 4)]
    B = [(5, 7), (5, 8), (6, 7), (6, 8), (7, 8), (5, 9), (6, 9)]
    bridge = [(4, 9)]
    for u, v in A + B + bridge:
        G.add_edge(u, v)
    return _canonicalize(G)


def from_graph6(text: str) -> nx.Graph:
    return nx.from_graph6_bytes(text.encode("ascii"))


def to_graph6(G: nx.Graph) -> str:
    return nx.to_graph6_bytes(G, header=False).decode("ascii").rstrip()
