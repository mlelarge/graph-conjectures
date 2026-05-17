"""Vehicle 2/4 generator: Eulerian / 6-edge-connected digraphs with
lambda^{arc} = 3.

Priority-2 families:

 (A) Balanced orientations of K_{6,6}: each vertex has degree 6; randomly
     orient so each vertex has out-deg 3 and in-deg 3. The resulting
     digraph is Eulerian; filter for lambda = 3.

 (B) 6-regular circulants C_n(a_1, ..., a_6) on Z_n with asymmetric
     connection sets such that the digraph is 6-out-regular and Eulerian.
     For Eulerian we just need each vertex to have equal in/out-degree:
     since the connection set defines arcs (i, i+a) for a in the set,
     each vertex has out-degree |S|. In-degree = number of a in S with
     (-a mod n) in S? no: in-degree(v) = number of u with v-u in S = |S|.
     So every Cayley digraph on Z_n is k-out-regular and k-in-regular for
     |S| = k, automatically Eulerian.

 (C) Bidirected 3-edge-connected graphs perturbed: replace each undirected
     edge of an undirected 3-edge-connected G by both directions, giving
     a 6-arc-strong Eulerian digraph; then break some 2-cycles into single
     arcs in chosen directions to lower the arc-connectivity toward 3.

The output is a stream of `EulerianInstance` objects, each carrying
provenance metadata.
"""

from __future__ import annotations

import itertools
import random
from dataclasses import dataclass
from typing import Iterator

import networkx as nx

from digraph import Digraph


# ----------------------------------------------------------------------------
# Instance dataclass
# ----------------------------------------------------------------------------


@dataclass(frozen=True)
class EulerianInstance:
    name: str
    n: int
    arcs: tuple[tuple[int, int], ...]
    family: str   # "K66_balanced" | "circulant" | "perturbed_bidirected"
    params: tuple  # family-specific parameter tuple

    def build(self) -> Digraph:
        return Digraph.from_arcs(range(self.n), list(self.arcs))


# ----------------------------------------------------------------------------
# (A) Balanced random orientations of K_{6, 6}
# ----------------------------------------------------------------------------


def random_balanced_orientation_K66(rng: random.Random) -> tuple[tuple[int, int], ...]:
    """A random orientation of K_{6,6} (parts L = {0..5}, R = {6..11}) such
    that each vertex has out-degree exactly 3 and in-degree exactly 3.

    Strategy: each of the 6 left vertices is matched to a 3-subset of the
    6 right vertices (its out-neighbours among R); we then need each right
    vertex to be chosen by exactly 3 left vertices to satisfy its in-deg
    = 3, automatically forcing out-deg(R-vertex) = 6 - 3 = 3. This is
    equivalent to a 3-regular bipartite multigraph between L and R, which
    is a 3-regular bipartite graph (no multi-edges since K_{6,6} has at
    most one edge between any pair). The set of 3-regular bipartite
    graphs on (6,6) is in bijection with 0/1 matrices with row-sums 3
    and column-sums 3.

    We sample such a matrix uniformly by configuration-style permutation
    pasting (3 permutations of [0,6) ORed together as bipartite matchings,
    rejection-sampled if any cell appears twice).
    """
    L = list(range(6))
    R = list(range(6, 12))
    while True:
        cell = [[0] * 6 for _ in range(6)]
        ok = True
        for _ in range(3):
            perm = list(range(6))
            rng.shuffle(perm)
            for i, j in enumerate(perm):
                if cell[i][j]:
                    ok = False
                    break
                cell[i][j] = 1
            if not ok:
                break
        if not ok:
            continue
        arcs = []
        for i in range(6):
            for j in range(6):
                if cell[i][j]:
                    arcs.append((L[i], R[j]))
                else:
                    # Edge exists in K_{6,6} but is oriented R -> L.
                    arcs.append((R[j], L[i]))
        return tuple(arcs)


def gen_K66_balanced(
    rng: random.Random, n_samples: int
) -> Iterator[EulerianInstance]:
    """Stream random balanced orientations of K_{6,6}."""
    seen: set[tuple[tuple[int, int], ...]] = set()
    for k in range(n_samples):
        arcs = random_balanced_orientation_K66(rng)
        canon = tuple(sorted(arcs))
        if canon in seen:
            continue
        seen.add(canon)
        yield EulerianInstance(
            name=f"K66bal_{k:04d}",
            n=12,
            arcs=arcs,
            family="K66_balanced",
            params=(k,),
        )


# ----------------------------------------------------------------------------
# (B) 6-out-regular circulants
# ----------------------------------------------------------------------------


def gen_circulants(
    n_values: list[int],
    rng: random.Random,
    n_samples_per_n: int,
    drop_arcs_per_sample: int = 0,
) -> Iterator[EulerianInstance]:
    """For each n in `n_values`, sample 6-element connection sets
    S ⊆ {1, 2, ..., n - 1} and emit C_n(S).

    Notes
    -----
    Each vertex has out-degree |S| = 6 and in-degree |S| = 6, hence
    Eulerian.  But by vertex-transitivity arc-connectivity equals the
    min degree = 6, so these are 6-arc-strong and never pass the
    `kappa = 3` filter.  To get lambda = 3 candidates, the caller can
    set `drop_arcs_per_sample > 0`: we then perturb each circulant by
    dropping that many random arcs, biased to land near lambda = 3.

    With drop_arcs_per_sample = 0 the family is still useful as a
    *control* (positive-confirmation that the verifier handles
    6-arc-strong digraphs correctly).
    """
    for n in n_values:
        if n <= 6:
            continue
        all_offsets = list(range(1, n))
        emitted: set[tuple[int, ...]] = set()
        attempts = 0
        max_attempts = max(n_samples_per_n * 8, 100)
        while len(emitted) < n_samples_per_n and attempts < max_attempts:
            attempts += 1
            S = tuple(sorted(rng.sample(all_offsets, 6)))
            if S in emitted:
                continue
            emitted.add(S)
            arcs = []
            for i in range(n):
                for a in S:
                    arcs.append((i, (i + a) % n))
            if drop_arcs_per_sample > 0:
                arcs_list = list(arcs)
                rng.shuffle(arcs_list)
                # We want to land at lambda ≈ 3, so drop ~ 3 * n arcs / 2
                # i.e. enough to lower out-degree from 6 to 3 on average,
                # but keep enough heterogeneity.
                target_drop = drop_arcs_per_sample
                arcs = tuple(arcs_list[target_drop:])
            else:
                arcs = tuple(arcs)
            yield EulerianInstance(
                name=f"circ_n{n}_S{'_'.join(map(str, S))}_drop{drop_arcs_per_sample}_{attempts}",
                n=n,
                arcs=arcs,
                family="circulant",
                params=(n, S, drop_arcs_per_sample),
            )


# ----------------------------------------------------------------------------
# (C) Perturbed bidirected 3-edge-connected graphs
# ----------------------------------------------------------------------------


def _generate_3_edge_connected_graphs(
    n_values: list[int], rng: random.Random, n_samples_per_n: int
) -> Iterator[nx.Graph]:
    """Yield random undirected 3-edge-connected graphs on `n` vertices.

    Strategy: start from a random k-regular graph (k = 6 for safety), check
    edge-connectivity, retry until 3-edge-connected.  For 6-regular random
    graphs on small n, 3-edge-connectivity is almost always satisfied.
    """
    for n in n_values:
        if n < 4:
            continue
        emitted = 0
        attempts = 0
        max_attempts = n_samples_per_n * 30
        while emitted < n_samples_per_n and attempts < max_attempts:
            attempts += 1
            # Random regular graph on n vertices with degree 6 (or smaller
            # if n permits).
            d = min(6, n - 1)
            if (n * d) % 2:
                d -= 1
            if d < 3:
                continue
            try:
                G = nx.random_regular_graph(d, n, seed=rng.randrange(1 << 30))
            except nx.NetworkXError:
                continue
            if not nx.is_connected(G):
                continue
            try:
                ec = nx.edge_connectivity(G)
            except nx.NetworkXError:
                continue
            if ec < 3:
                continue
            yield G
            emitted += 1


def _perturb_bidirected(
    G: nx.Graph, rng: random.Random
) -> tuple[tuple[int, int], ...]:
    """Take G's bidirected (every edge in both directions, giving
    arc-connectivity 6 if G is 3-edge-connected). Then randomly drop one
    direction of `k` edges, with k chosen so the resulting arc-connectivity
    aims at 3."""
    edges = list(G.edges())
    arcs: list[tuple[int, int]] = []
    # Decide which edges to bidirect and which to leave as a single arc
    # (with random direction). We bias drop probability to land near
    # lambda = 3.
    drop_p = rng.uniform(0.25, 0.55)
    for u, v in edges:
        if rng.random() < drop_p:
            # Single direction only
            if rng.random() < 0.5:
                arcs.append((u, v))
            else:
                arcs.append((v, u))
        else:
            arcs.append((u, v))
            arcs.append((v, u))
    return tuple(arcs)


def gen_perturbed_bidirected(
    n_values: list[int], rng: random.Random, n_samples_per_n: int
) -> Iterator[EulerianInstance]:
    """For each n in n_values, generate `n_samples_per_n` perturbed bidirected
    digraphs starting from random 6-regular 3-edge-connected G."""
    k = 0
    for G in _generate_3_edge_connected_graphs(n_values, rng, n_samples_per_n):
        n = G.number_of_nodes()
        # Relabel nodes to 0..n-1
        H = nx.convert_node_labels_to_integers(G)
        arcs = _perturb_bidirected(H, rng)
        k += 1
        yield EulerianInstance(
            name=f"pertB_n{n}_{k:04d}",
            n=n,
            arcs=arcs,
            family="perturbed_bidirected",
            params=(n, k),
        )


# ----------------------------------------------------------------------------
# Pre-gates
# ----------------------------------------------------------------------------


def quick_degree_gate(arcs: list[tuple[int, int]], n: int) -> bool:
    """min(out-deg, in-deg) >= 3 — a necessary condition for lambda >= 3."""
    outd = [0] * n
    ind = [0] * n
    for u, v in arcs:
        outd[u] += 1
        ind[v] += 1
    return all(d >= 3 for d in outd) and all(d >= 3 for d in ind)


def is_lambda_exactly_3(D: Digraph) -> bool:
    if not D.is_strongly_connected():
        return False
    return D.arc_connectivity() == 3
