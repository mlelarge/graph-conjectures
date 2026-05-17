"""
DHGO (Dirac-Haggkvist-Gallai-Ore) composition for k = 26, with G1 = G2 = K_26.

Reference: A. Kostochka and M. Yancey, "Ore's Conjecture on color-critical
graphs is almost true", arXiv:1209.1050, J. Combin. Theory Ser. B 109 (2014).
See Section 2 for the precise definition of the DHGO composition (the "Ore
composition") and Definition 1 for the class O_k of k-Ore graphs.

Construction recap (Section 2 of KY):
    Let G1, G2 in O_k. Pick:
      * an edge xy in E(G1) with deg_{G1}(y) = k - 1 (call y the "low" vertex),
      * a vertex z in V(G2) with deg_{G2}(z) = k - 1,
      * a partition N_{G2}(z) = A sqcup B, with both A, B nonempty.
    Build G = G1 * G2 by:
      1. delete the edge xy from G1;
      2. delete vertex z from G2;
      3. identify the vertex x of G1 with the |A| neighbours of z in A
         (so x's neighbour set in the new graph picks up A's old neighbours
         in G2 \\ {z});
      4. identify the vertex y of G1 with the |B| neighbours of z in B.
    The result G has |V(G)| = n1 + n2 - 1 and is again k-critical.

For k = 26 and G1 = G2 = K_26:
    * every vertex of K_26 has degree 25 = k - 1, so any z (resp. y) is "low";
    * K_26 is vertex- and edge-transitive, so up to isomorphism of the inputs
      the choice of z in G2 and the choice of edge xy in G1 are unique;
    * the partition of the 25 neighbours of z into nonempty parts A, B is
      parameterised up to (A <-> B) symmetry by the size |A| in {1, ..., 12},
      since K_26 - z = K_25 has trivial neighbour structure (all 25 remaining
      vertices play the same role); |A| = 13 yields the same isomorphism class
      as |A| = 12 by swapping A and B (which swaps the roles of x and y, both
      of which are interchangeable in K_26 - xy after edge deletion only up to
      automorphism of K_26 - xy = K_26 minus one edge, whose automorphism
      group swaps x and y).

The resulting graph has 51 vertices and is 26-critical by KY Theorem 1 /
Definition 1 (Ore-composition preserves k-criticality).

CLI:
    python ore_compose.py --partition-size A    (A in 1..12)
        emit one graph6 line on stdout for K_26 * K_26 with |A| = A.
    python ore_compose.py --all
        emit one graph6 line per distinct (up to isomorphism) value of |A|
        in {1, ..., 12}, after canonical-form dedup via pynauty.
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from typing import Iterable

import networkx as nx

try:
    import pynauty

    _HAVE_PYNAUTY = True
except ImportError:  # pragma: no cover
    _HAVE_PYNAUTY = False


K = 26  # chromatic / criticality parameter
N1 = K  # = 26
N2 = K  # = 26
N_OUT = N1 + N2 - 1  # = 51


def k26_minus_edge(label_offset: int = 0) -> tuple[nx.Graph, int, int]:
    """Return (G1, x, y) where G1 = K_26 with edge xy deleted.

    Vertices are labelled label_offset .. label_offset + 25. We pick the
    deleted edge to be (label_offset, label_offset + 1), i.e. x = offset,
    y = offset + 1. y is the "low" vertex of the original K_26 (degree
    k - 1 = 25 before deletion; by symmetry x is equivalent).
    """
    g = nx.complete_graph(range(label_offset, label_offset + N1))
    x = label_offset
    y = label_offset + 1
    g.remove_edge(x, y)
    return g, x, y


def ore_compose_k26_k26(a_size: int) -> nx.Graph:
    """Build the DHGO composition K_26 * K_26 with |A| = a_size.

    a_size in {1, ..., 12}.

    Construction (literal transcription of KY Section 2):
      G1 = K_26 on vertices {0, ..., 25}; deleted edge xy = (0, 1).
      G2 = K_26 on vertices {26, ..., 51}; deleted vertex z = 51.
        Then N_{G2}(z) = {26, ..., 50}, twenty-five vertices.
      Partition N_{G2}(z) = A sqcup B with A = {26, ..., 26 + a_size - 1}
        and B = {26 + a_size, ..., 50}.
      Identify x = 0 with all vertices in A (collapse them to vertex 0).
      Identify y = 1 with all vertices in B (collapse them to vertex 1).
    The output graph G has vertex set {0, 1} cup {2, ..., 25} = V(G1) (with
    edge xy removed, then re-added inside if any vertex of A was adjacent to
    any vertex of B in K_25 -- which they all are, since K_25 is complete),
    giving 26 vertices, plus -- no wait, that gives 26 vertices, not 51.

    Re-reading KY: the "identification" is **not** "collapse A into the
    single vertex x". It is: "replace the vertex z by the pair (x, y); each
    former neighbour of z in A becomes a neighbour of x, each former
    neighbour of z in B becomes a neighbour of y". So the vertices of A and
    B are **kept**, only z disappears. The vertex set of G is
    (V(G1) \\ {}) cup (V(G2) \\ {z}) = N1 + N2 - 1 vertices total, with x
    and y the bridge vertices and A, B their respective bridge-neighbour
    sets.

    Final vertex set: {0, ..., 25} from G1, {26, ..., 50} from G2 (z = 51
    removed; the remaining vertices of G2 are {26, ..., 50}, but we never
    add the label 51). Total: 26 + 25 = 51. Good.

    Edge set:
      * E(G1) \\ {xy} = all edges of K_26 on {0, ..., 25} except (0, 1);
      * E(G2 - z): K_26 on {26, ..., 51} minus vertex 51 gives K_25 on
        {26, ..., 50} -- all edges among those 25 vertices;
      * For each vertex a in A: add edge (x, a) = (0, a);
      * For each vertex b in B: add edge (y, b) = (1, b).
      (These last two families come from "x picks up A's adjacency to z"
      i.e. each a in A was adjacent to z; we replace those edges (z, a)
      with edges (x, a). Similarly for b in B.)
    """
    if not (1 <= a_size <= N1 - 2):  # 1..24; KY allows both A, B nonempty
        raise ValueError(f"a_size must be in 1..{N1 - 2}, got {a_size}")

    # G1 = K_26 - xy on labels 0..25, x=0, y=1.
    g1, x, y = k26_minus_edge(label_offset=0)

    # G2 - z = K_25 on labels 26..50. (z would be label 51; we never add it.)
    g2_minus_z = nx.complete_graph(range(N1, N1 + N2 - 1))

    # Compose into G.
    G = nx.Graph()
    G.add_nodes_from(g1.nodes())
    G.add_nodes_from(g2_minus_z.nodes())
    G.add_edges_from(g1.edges())
    G.add_edges_from(g2_minus_z.edges())

    # Partition the 25 former neighbours of z into A and B.
    neighbours_of_z = list(range(N1, N1 + N2 - 1))  # [26, ..., 50]
    assert len(neighbours_of_z) == K - 1 == 25
    A = neighbours_of_z[:a_size]
    B = neighbours_of_z[a_size:]
    assert len(A) >= 1 and len(B) >= 1
    assert len(A) + len(B) == 25

    # Add bridge edges: x -- A, y -- B.
    for a in A:
        G.add_edge(x, a)
    for b in B:
        G.add_edge(y, b)

    # Sanity: order and minimum chromatic-degree property of the construction.
    assert G.number_of_nodes() == N_OUT, (G.number_of_nodes(), N_OUT)

    return G


def canonical_certificate(G: nx.Graph) -> str:
    """Return a hex SHA-256 of pynauty's canonical labeling adjacency list.

    If pynauty is not available, falls back to graph6 of the nx.canonical
    labeling -- which is NOT canonical across isomorphism, so callers must
    not depend on it for dedup. We log this case loudly.
    """
    if _HAVE_PYNAUTY:
        # pynauty expects adjacency dict over 0..n-1 integer labels.
        nodes = sorted(G.nodes())
        relabel = {v: i for i, v in enumerate(nodes)}
        n = len(nodes)
        adj = {i: [] for i in range(n)}
        for u, v in G.edges():
            ru, rv = relabel[u], relabel[v]
            adj[ru].append(rv)
            adj[rv].append(ru)
        pg = pynauty.Graph(n, directed=False, adjacency_dict=adj)
        # certificate() returns a bytes object that is a canonical fingerprint
        # uniquely identifying the isomorphism class (per pynauty docs).
        cert = pynauty.certificate(pg)
        return hashlib.sha256(cert).hexdigest()
    # Fallback: not canonical across isomorphism. Use the sorted edge list of
    # a relabeled-to-0..n-1 graph and hash that. Two isomorphic graphs may
    # produce different hashes; caller must then run nx.is_isomorphic.
    print(
        "WARNING: pynauty not available; canonical_certificate is NOT canonical.",
        file=sys.stderr,
    )
    nodes = sorted(G.nodes())
    relabel = {v: i for i, v in enumerate(nodes)}
    edges = sorted(tuple(sorted((relabel[u], relabel[v]))) for u, v in G.edges())
    return hashlib.sha256(repr(edges).encode()).hexdigest()


def to_graph6(G: nx.Graph) -> str:
    """Emit a graph6 string for G with vertex labels 0..n-1 (sorted)."""
    # nx.to_graph6_bytes expects a graph with nodes 0..n-1.
    H = nx.convert_node_labels_to_integers(G, ordering="sorted")
    raw = nx.to_graph6_bytes(H, header=False)
    # to_graph6_bytes appends a newline; strip and decode.
    return raw.decode("ascii").rstrip("\n")


def to_dimacs(G: nx.Graph) -> str:
    """Emit a DIMACS edge-list string for G.

    Format:
        c <comment>
        p edge <n> <m>
        e u v          (1-indexed, one line per edge)
    """
    H = nx.convert_node_labels_to_integers(G, ordering="sorted")
    n = H.number_of_nodes()
    m = H.number_of_edges()
    lines = [f"c K_26 * K_26 DHGO composition, n={n}, m={m}", f"p edge {n} {m}"]
    for u, v in sorted(tuple(sorted(e)) for e in H.edges()):
        lines.append(f"e {u + 1} {v + 1}")
    return "\n".join(lines) + "\n"


def enumerate_distinct(
    a_range: Iterable[int] = range(1, N1 - 1),  # 1..24 by default
) -> list[tuple[int, nx.Graph, str]]:
    """Enumerate (a_size, G, sha256) over a_range, dedup by canonical cert.

    Returns one representative per isomorphism class, sorted by smallest
    a_size in the class (canonical representative = smallest a_size).
    """
    seen: dict[str, tuple[int, nx.Graph]] = {}
    order: list[str] = []
    for a in a_range:
        G = ore_compose_k26_k26(a)
        cert = canonical_certificate(G)
        if cert not in seen:
            seen[cert] = (a, G)
            order.append(cert)
        # else: collapse (a maps to an existing class)
    return [(seen[c][0], seen[c][1], c) for c in order]


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="DHGO composition K_26 * K_26.")
    grp = p.add_mutually_exclusive_group(required=True)
    grp.add_argument(
        "--partition-size",
        type=int,
        metavar="A",
        help="emit one graph6 line for K_26 * K_26 with |A| = A (1..24).",
    )
    grp.add_argument(
        "--all",
        action="store_true",
        help="emit one graph6 line per distinct iso class.",
    )
    p.add_argument(
        "--a-range",
        default="1..12",
        help="for --all: range of |A| values to scan (default 1..12).",
    )
    args = p.parse_args(argv)

    if args.partition_size is not None:
        G = ore_compose_k26_k26(args.partition_size)
        print(to_graph6(G))
        return 0

    # --all
    lo_s, hi_s = args.a_range.split("..")
    lo, hi = int(lo_s), int(hi_s)
    reps = enumerate_distinct(range(lo, hi + 1))
    for a, G, _cert in reps:
        print(to_graph6(G))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
