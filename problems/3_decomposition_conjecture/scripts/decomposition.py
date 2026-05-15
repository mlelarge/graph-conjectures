"""3-decomposition primitives.

Conventions (matching docs/plan.md and docs/minimal_counterexample.md):

- A 3-decomposition of a connected cubic graph G is a partition
  E(G) = T ⊔ C ⊔ M where T is a spanning tree, C is 2-regular,
  M is a matching. Both C and M may be empty (but in a connected
  cubic G, C is always non-empty; see plan.md §"Vertex-type reformulation").

- Edge labels live in {"T", "C", "M"}.

- An edge partition is represented as a dict {frozenset({u,v}): label}.

For subcubic ports:

- A "port" is a vertex of degree < 3. Its "port-degree" is 3 - deg(v).

- A "port state" at a port of port-degree 1 is one of five codes, as in
  docs/minimal_counterexample.md §1.2:
    T_T, T_TM, M_TT, T_CC, C_TC.

- A "boundary trace" of a subcubic graph H with ordered ports R is
  (chi, pi) where chi maps each port to its port state and pi is a
  partition (frozenset of frozensets) of the T-incident boundary half-edges
  recording tree-connectivity inside H.
"""

from __future__ import annotations

import itertools
from collections.abc import Iterable, Iterator
from typing import Optional

import networkx as nx


EDGE_LABELS = ("T", "C", "M")


# -- canonical edge keys ------------------------------------------------------


def edge_key(u, v) -> frozenset:
    return frozenset((u, v))


def edges_of(G: nx.Graph) -> list[frozenset]:
    return [edge_key(u, v) for u, v in G.edges()]


# -- decomposition verifier ---------------------------------------------------


def verify_decomposition(G: nx.Graph, labels: dict[frozenset, str]) -> tuple[bool, str]:
    """Check that `labels` is a valid 3-decomposition of cubic G.

    Returns (ok, reason). On success reason is empty.
    """
    if any(d != 3 for _, d in G.degree()):
        return False, "G is not cubic"
    if not nx.is_connected(G):
        return False, "G is not connected"

    edges = set(edges_of(G))
    if set(labels.keys()) != edges:
        return False, "labels do not cover E(G) exactly"
    for v in labels.values():
        if v not in EDGE_LABELS:
            return False, f"bad label {v!r}"

    T_edges = [e for e, lab in labels.items() if lab == "T"]
    C_edges = [e for e, lab in labels.items() if lab == "C"]
    M_edges = [e for e, lab in labels.items() if lab == "M"]

    n = G.number_of_nodes()
    if len(T_edges) != n - 1:
        return False, f"|T|={len(T_edges)} != n-1={n-1}"

    T_graph = nx.Graph()
    T_graph.add_nodes_from(G.nodes())
    for e in T_edges:
        u, v = tuple(e)
        T_graph.add_edge(u, v)
    if not nx.is_tree(T_graph):
        return False, "T is not a tree"
    if T_graph.number_of_nodes() != n:
        return False, "T does not span"

    C_deg: dict = {v: 0 for v in G.nodes()}
    for e in C_edges:
        for v in e:
            C_deg[v] += 1
    if any(d not in (0, 2) for d in C_deg.values()):
        return False, "C is not 2-regular as a subgraph"

    M_endpoints: list = []
    for e in M_edges:
        for v in e:
            M_endpoints.append(v)
    if len(M_endpoints) != len(set(M_endpoints)):
        return False, "M is not a matching"

    return True, ""


# -- port-state classification ------------------------------------------------


PORT_STATES = ("T_T", "T_TM", "M_TT", "T_CC", "C_TC")

# Each port state is: (boundary edge colour, multiset of side-edge colours).
PORT_STATE_DATA: dict[str, tuple[str, tuple[str, str]]] = {
    "T_T": ("T", ("T", "T")),
    "T_TM": ("T", ("T", "M")),
    "M_TT": ("M", ("T", "T")),
    "T_CC": ("T", ("C", "C")),
    "C_TC": ("C", ("T", "C")),
}


def classify_port_state(side_edge_labels: tuple[str, str]) -> Optional[str]:
    """Given the labels of the two side-edges at a port-degree-1 port,
    return the port state code (which fixes the boundary-edge colour by
    the vertex-type identity), or None if the local pattern is infeasible.

    A port of port-degree 1 corresponds to a degree-2 vertex inside H.
    The full graph contains one more edge at that vertex (the boundary
    edge); its colour is determined by the vertex-type identity:

      degT + degC + degM = 3, degC ∈ {0,2}, degM ∈ {0,1}.

    Reading (sideA, sideB) and the boundary edge:

      (T,T)         + boundary T -> V_T,   state T_T
      (T,T)         + boundary M -> V_M,   state M_TT
      (T,M) or (M,T)+ boundary T -> V_M,   state T_TM
      (C,C)         + boundary T -> V_C,   state T_CC
      (T,C) or (C,T)+ boundary C -> V_C,   state C_TC

    Any other combination is locally infeasible.
    """
    bag = tuple(sorted(side_edge_labels))
    if bag == ("T", "T"):
        # Boundary could be T or M — two states.
        return ("T_T", "M_TT")  # type: ignore[return-value]
    if bag == ("M", "T"):
        return ("T_TM",)  # type: ignore[return-value]
    if bag == ("C", "C"):
        return ("T_CC",)  # type: ignore[return-value]
    if bag == ("C", "T"):
        return ("C_TC",)  # type: ignore[return-value]
    return None  # any pattern with M+M, M+C, etc. at a port is infeasible


# -- trace-set computer for a subcubic graph with ordered ports --------------


def partitions_to_labellings(G: nx.Graph) -> Iterator[dict[frozenset, str]]:
    """Yield every map E(G) -> {T,C,M}. Use only for small G."""
    edges = edges_of(G)
    for assignment in itertools.product(EDGE_LABELS, repeat=len(edges)):
        yield dict(zip(edges, assignment))


def is_subcubic_partition_valid(
    H: nx.Graph,
    labels: dict[frozenset, str],
    ports: list,
) -> bool:
    """Check that `labels` is a valid boundary-traced partition on
    subcubic H with the given ordered port list.

    Required properties (consistent with §1.3 of minimal_counterexample.md):

    - For every internal vertex (not a port): the local colouring is
      one of the three full vertex types V_T, V_M, V_C, i.e.
      (degT, degC, degM) ∈ {(3,0,0), (2,0,1), (1,2,0)}.

    - For each port (of port-degree 1, so degree 2 in H): the two
      incident edge labels match one of the five port states.

    - The matching M is a matching in H (each vertex incident to ≤ 1
      M-edge); this is implied by the vertex-type constraint above but
      we check it directly for robustness.

    - The cycle subgraph C is 2-regular in H (degC ∈ {0,2} at every
      vertex, including ports — ports with degC=2 force state T_CC).

    - The tree T_H is a forest in H. (Spanning behaviour is determined
      separately by the boundary trace; here we only check acyclicity.)
    """
    port_set = set(ports)
    deg_T: dict = {v: 0 for v in H.nodes()}
    deg_C: dict = {v: 0 for v in H.nodes()}
    deg_M: dict = {v: 0 for v in H.nodes()}
    for e, lab in labels.items():
        for v in e:
            if lab == "T":
                deg_T[v] += 1
            elif lab == "C":
                deg_C[v] += 1
            else:
                deg_M[v] += 1

    for v in H.nodes():
        if v in port_set:
            if deg_T[v] + deg_C[v] + deg_M[v] != 2:
                return False
            triple = (deg_T[v], deg_C[v], deg_M[v])
            # Allowed (degT, degC, degM) at a port-degree-1 port:
            #   T_T  : (2, 0, 0)
            #   T_TM : (1, 0, 1)
            #   M_TT : (2, 0, 0)   -- distinguished from T_T by boundary colour
            #   T_CC : (0, 2, 0)
            #   C_TC : (1, 1, 0)
            if triple not in {(2, 0, 0), (1, 0, 1), (0, 2, 0), (1, 1, 0)}:
                return False
        else:
            if deg_T[v] + deg_C[v] + deg_M[v] != 3:
                return False
            triple = (deg_T[v], deg_C[v], deg_M[v])
            if triple not in {(3, 0, 0), (2, 0, 1), (1, 2, 0)}:
                return False

    # Acyclicity of T inside H.
    T_graph = nx.Graph()
    T_graph.add_nodes_from(H.nodes())
    for e, lab in labels.items():
        if lab == "T":
            u, v = tuple(e)
            T_graph.add_edge(u, v)
    if not nx.is_forest(T_graph):
        return False

    return True


def port_state_from_partition(
    H: nx.Graph,
    labels: dict[frozenset, str],
    port,
) -> Optional[str]:
    """Read the port state at `port` from a valid partition `labels`.

    Distinguishes the two patterns with side-degree (2,0,0) by examining
    the labels of the two incident edges: if both are T, the boundary
    edge would be T -> T_T or M -> M_TT; we return T_T (the boundary
    edge type is determined by the full-graph vertex type, which is
    encoded in the *combination* of side-edge labels and the choice we
    make for the missing boundary edge). To disambiguate, we use a
    convention: the partition itself encodes only the inside, so we
    label as T_T by default and let the gluing step pick M_TT when the
    boundary edge is M. See compute_trace_set below.
    """
    incident = [
        labels[edge_key(port, w)] for w in H.neighbors(port)
    ]
    bag = tuple(sorted(incident))
    if bag == ("T", "T"):
        return "T_T_or_M_TT"
    if bag == ("M", "T"):
        return "T_TM"
    if bag == ("C", "C"):
        return "T_CC"
    if bag == ("C", "T"):
        return "C_TC"
    return None


def compute_trace_set(
    H: nx.Graph,
    ports: list,
) -> set[tuple[str, ...]]:
    """Brute-force trace set on subcubic H with ordered ports.

    Returns a set of port-state tuples (one entry per port). The
    ambiguity between T_T (full V_T) and M_TT (full V_M with M at
    boundary) is resolved by recording *both* whenever the inside
    pattern (T,T) at a port is realised by a valid partition — these
    two only differ in the colour of the (not-here) boundary edge.

    Tree-connectivity inside H is *not* recorded in this version
    (added later for the 2-edge-cut Lemma 2 case).

    Use only on small H (|E| ≤ 14 or so, so 3^14 ≈ 5e6 partitions).
    """
    out: set[tuple[str, ...]] = set()
    for labels in partitions_to_labellings(H):
        if not is_subcubic_partition_valid(H, labels, ports):
            continue
        tup_options: list[list[str]] = []
        ok = True
        for p in ports:
            raw = port_state_from_partition(H, labels, p)
            if raw is None:
                ok = False
                break
            if raw == "T_T_or_M_TT":
                tup_options.append(["T_T", "M_TT"])
            else:
                tup_options.append([raw])
        if not ok:
            continue
        for combo in itertools.product(*tup_options):
            out.add(tuple(combo))
    return out


# -- 2-pole trace set with tree-connectivity partition ----------------------


# Map port state -> boundary edge colour.
BOUNDARY_COLOUR: dict[str, str] = {s: data[0] for s, data in PORT_STATE_DATA.items()}


def are_2pole_traces_compatible(
    trace_a: tuple[tuple[str, str], frozenset],
    trace_b: tuple[tuple[str, str], frozenset],
) -> bool:
    """Return True iff two 2-pole traces can be glued across matching ports.

    Compatibility means:
      - paired boundary half-edges have the same colour; and
      - the T-boundary connectivity graph obtained by joining the two
        pi-partitions along T-coloured boundary edges is a tree.

    This is the executable version of docs/minimal_counterexample.md §1.4.
    """
    chi_a, pi_a = trace_a
    chi_b, pi_b = trace_b
    if len(chi_a) != 2 or len(chi_b) != 2:
        raise ValueError("2-pole traces must have exactly two port states")

    for i in (0, 1):
        if BOUNDARY_COLOUR[chi_a[i]] != BOUNDARY_COLOUR[chi_b[i]]:
            return False

    boundary_graph = nx.Graph()
    for side, chi, pi in (("A", chi_a, pi_a), ("B", chi_b, pi_b)):
        for i, state in enumerate(chi):
            if BOUNDARY_COLOUR[state] == "T":
                boundary_graph.add_node((side, i))
        for block in pi:
            block_list = list(block)
            for j in range(1, len(block_list)):
                boundary_graph.add_edge((side, block_list[0]), (side, block_list[j]))

    for i in (0, 1):
        if BOUNDARY_COLOUR[chi_a[i]] == "T":
            boundary_graph.add_edge(("A", i), ("B", i))

    return boundary_graph.number_of_nodes() > 0 and nx.is_tree(boundary_graph)


def compute_trace_set_2pole(
    H: nx.Graph,
    ports: list,
) -> set[tuple[tuple[str, str], frozenset]]:
    """Brute-force 2-pole trace set with tree-connectivity partition.

    Requires: |ports| == 2, each port of degree 2 in H, other vertices of
    degree 3, H connected.

    Returns: set of (chi, pi) where
      chi = (state_r1, state_r2) in {T_T, T_TM, M_TT, T_CC, C_TC}^2;
      pi  = frozenset of frozensets of port indices (0 or 1), encoding the
            partition of T-incident port boundary stubs by their T_H
            component (with T_CC ports each in their own block, since the
            T_CC port is isolated in T_H and its T-boundary stub still
            counts as its own T-component for gluing purposes).

      Concretely the possible pi values are:
        frozenset()                                         -- no port is T-incident
        frozenset({frozenset({0})})                         -- only port 0 is T-incident
        frozenset({frozenset({1})})                         -- only port 1 is T-incident
        frozenset({frozenset({0, 1})})                      -- both, same T-component
        frozenset({frozenset({0}), frozenset({1})})         -- both, distinct T-components

    A (chi, pi) is realisable iff there is a partition of E(H) satisfying
    every clause of docs/minimal_counterexample.md §1.3 (with the
    "every T_H component touches a T-boundary half-edge" clause now
    enforced — see below).
    """
    if len(ports) != 2:
        raise ValueError(f"expected 2 ports, got {len(ports)}")
    if any(H.degree(p) != 2 for p in ports):
        raise ValueError("each port must have degree 2 in H")
    if any(H.degree(v) != 3 for v in H.nodes() if v not in ports):
        raise ValueError("non-port vertices must have degree 3 in H")
    if not nx.is_connected(H):
        raise ValueError("H must be connected")

    out: set[tuple[tuple[str, str], frozenset]] = set()
    edges = edges_of(H)
    n = H.number_of_nodes()
    port_set = set(ports)

    # Every T_H component must touch one of the two T-coloured boundary stubs.
    # Thus T_H has one or two components, so |T_H| is n-1 or n-2. Enumerating
    # these candidate forests is much smaller than all 3^|E| labellings.
    for t_count in (n - 1, n - 2):
        if t_count < 0 or t_count > len(edges):
            continue
        for T_subset in itertools.combinations(edges, t_count):
            T_set = set(T_subset)
            T_graph = nx.Graph()
            T_graph.add_nodes_from(H.nodes())
            for e in T_set:
                u, v = tuple(e)
                T_graph.add_edge(u, v)
            if not nx.is_forest(T_graph):
                continue
            t_components = [set(c) for c in nx.connected_components(T_graph)]
            if len(t_components) not in (1, 2):
                continue

            cotree = [e for e in edges if e not in T_set]
            for mask in range(1 << len(cotree)):
                labels: dict[frozenset, str] = {e: "T" for e in T_set}
                for i, e in enumerate(cotree):
                    labels[e] = "C" if (mask >> i) & 1 else "M"
                if not is_subcubic_partition_valid(H, labels, ports):
                    continue
                _add_2pole_traces_from_partition(H, ports, labels, t_components, out)

    return out


def _add_2pole_traces_from_partition(
    H: nx.Graph,
    ports: list,
    labels: dict[frozenset, str],
    t_components: list[set],
    out: set[tuple[tuple[str, str], frozenset]],
) -> None:
    """Add all 2-pole traces induced by one valid inside-edge partition."""
    port_set = set(ports)
    port_state_options: list[tuple[str, ...]] = []
    for p in ports:
        raw = port_state_from_partition(H, labels, p)
        if raw is None:
            return
        if raw == "T_T_or_M_TT":
            port_state_options.append(("T_T", "M_TT"))
        else:
            port_state_options.append((raw,))

    for state_combo in itertools.product(*port_state_options):
        t_incident = [BOUNDARY_COLOUR[s] == "T" for s in state_combo]
        valid = True
        for comp in t_components:
            if len(comp) == 1:
                v = next(iter(comp))
                if v in port_set:
                    idx = ports.index(v)
                    if state_combo[idx] == "T_CC":
                        continue
                valid = False
                break
            has_t_inc_port = any(
                v in port_set
                and t_incident[ports.index(v)]
                and state_combo[ports.index(v)] != "T_CC"
                for v in comp
            )
            if not has_t_inc_port:
                valid = False
                break
        if not valid:
            continue

        blocks: dict[tuple, set[int]] = {}
        for i, p in enumerate(ports):
            if not t_incident[i]:
                continue
            if state_combo[i] == "T_CC":
                blocks.setdefault(("alone", i), set()).add(i)
            else:
                for j, comp in enumerate(t_components):
                    if p in comp:
                        blocks.setdefault(("comp", j), set()).add(i)
                        break
        pi = frozenset(frozenset(s) for s in blocks.values())
        out.add(((state_combo[0], state_combo[1]), pi))

    return


def realises_target_traces(
    H: nx.Graph,
    ports: list,
    targets: set[tuple[tuple[str, str], frozenset]],
) -> bool:
    """Return True iff every trace in `targets` is realized by some
    valid edge partition of H with the given port ordering.

    Same partition enumeration as compute_trace_set_2pole, but early-exits
    as soon as all `targets` are accumulated. Caller uses this to test
    whether a specific lattice class's trace set is contained in
    Trace(H, R) without paying for the full trace-set computation.
    """
    if len(ports) != 2:
        raise ValueError(f"expected 2 ports, got {len(ports)}")
    if any(H.degree(p) != 2 for p in ports):
        raise ValueError("each port must have degree 2 in H")
    if any(H.degree(v) != 3 for v in H.nodes() if v not in ports):
        raise ValueError("non-port vertices must have degree 3 in H")
    if not nx.is_connected(H):
        raise ValueError("H must be connected")

    if not targets:
        return True

    found: set[tuple[tuple[str, str], frozenset]] = set()
    edges = edges_of(H)
    n = H.number_of_nodes()

    for t_count in (n - 1, n - 2):
        if t_count < 0 or t_count > len(edges):
            continue
        for T_subset in itertools.combinations(edges, t_count):
            T_set = set(T_subset)
            T_graph = nx.Graph()
            T_graph.add_nodes_from(H.nodes())
            for e in T_set:
                u, v = tuple(e)
                T_graph.add_edge(u, v)
            if not nx.is_forest(T_graph):
                continue
            t_components = [set(c) for c in nx.connected_components(T_graph)]
            if len(t_components) not in (1, 2):
                continue

            cotree = [e for e in edges if e not in T_set]
            for mask in range(1 << len(cotree)):
                labels: dict[frozenset, str] = {e: "T" for e in T_set}
                for i, e in enumerate(cotree):
                    labels[e] = "C" if (mask >> i) & 1 else "M"
                if not is_subcubic_partition_valid(H, labels, ports):
                    continue
                _add_2pole_traces_from_partition(H, ports, labels, t_components, found)
                if targets <= found:
                    return True

    return False


# -- bridge-side existence check ----------------------------------------------


BRIDGE_PORT_STATES = ("T_T", "T_TM")
# In a bridge side rooted at u of port-degree 1, the only realisable states
# are T_T (full V_T at u, both side-edges in T) and T_TM (full V_M at u, one
# side-edge in T and one in M). See docs/minimal_counterexample.md §2.
#
# Excluded:
#   M_TT  - boundary colour M, but the bridge must be in T.
#   C_TC  - boundary colour C, but the bridge must be in T.
#   T_CC  - boundary colour T (OK), inside (C,C), so deg_{T_u}(u)=0, but
#           T_u is a spanning tree of G_u on >=2 vertices and so must
#           contain u; impossible.


def verify_bridge_side_realisable(H: nx.Graph, port) -> bool:
    """Return True iff (H, port) realises at least one bridge-side state
    in {T_T, T_TM}.

    This is deliberately stricter than mere membership in compute_trace_set:
    for a true bridge side, the restriction of the global spanning tree to H
    must itself be a spanning tree of H. A disconnected T-forest with the
    right local port colours is not enough, because the single bridge edge can
    attach only the component containing the port.
    """
    if H.degree(port) != 2:
        return False
    if any(d not in (2, 3) for _, d in H.degree()):
        return False

    edges = edges_of(H)
    n = H.number_of_nodes()
    for T_subset in itertools.combinations(edges, n - 1):
        T_graph = nx.Graph()
        T_graph.add_nodes_from(H.nodes())
        for e in T_subset:
            u, v = tuple(e)
            T_graph.add_edge(u, v)
        if not nx.is_tree(T_graph) or T_graph.number_of_nodes() != n:
            continue

        T_set = set(T_subset)
        port_T_deg = sum(1 for w in H.neighbors(port) if edge_key(port, w) in T_set)
        if port_T_deg not in (1, 2):
            continue

        cotree = [e for e in edges if e not in T_set]
        for mask in range(1 << len(cotree)):
            labels: dict[frozenset, str] = {e: "T" for e in T_set}
            for i, e in enumerate(cotree):
                labels[e] = "C" if (mask >> i) & 1 else "M"

            if not is_subcubic_partition_valid(H, labels, [port]):
                continue
            raw = port_state_from_partition(H, labels, port)
            if raw == "T_T_or_M_TT" and port_T_deg == 2:
                return True
            if raw == "T_TM" and port_T_deg == 1:
                return True
    return False


# -- brute-force 3-decomposition finder (small cubic graphs) ------------------


def find_3_decomposition(G: nx.Graph) -> Optional[dict[frozenset, str]]:
    """Brute-force search over edge labellings; return one valid
    3-decomposition or None if none exists.

    Tractable for |E| up to ~16. Use a SAT encoding for larger graphs.
    """
    edges = edges_of(G)
    # Prune: T edge count is exactly n - 1. Don't iterate all 3^|E| labelings;
    # instead choose T as an n-1 subset, check it's a spanning tree, then
    # partition the remaining edges into C and M.
    n = G.number_of_nodes()
    if any(d != 3 for _, d in G.degree()):
        return None

    for T_subset in itertools.combinations(edges, n - 1):
        T_graph = nx.Graph()
        T_graph.add_nodes_from(G.nodes())
        for e in T_subset:
            u, v = tuple(e)
            T_graph.add_edge(u, v)
        if not nx.is_tree(T_graph) or T_graph.number_of_nodes() != n:
            continue
        T_set = set(T_subset)
        cotree = [e for e in edges if e not in T_set]
        # Partition cotree into C (2-regular) and M (matching).
        for mask in range(1 << len(cotree)):
            C_edges = [e for i, e in enumerate(cotree) if (mask >> i) & 1]
            M_edges = [e for i, e in enumerate(cotree) if not ((mask >> i) & 1)]
            # Check C is 2-regular (every vertex has degree 0 or 2 in C-subgraph).
            C_deg: dict = {v: 0 for v in G.nodes()}
            for e in C_edges:
                for v in e:
                    C_deg[v] += 1
            if any(d not in (0, 2) for d in C_deg.values()):
                continue
            # Connectedness of each connected component of the C-subgraph
            # is automatic from C being 2-regular and a subgraph: every
            # component must be a cycle, which our 2-regularity ensures
            # provided the subgraph induced on V(C) is well-formed.
            # Verify by walking each component.
            C_graph = nx.Graph()
            for e in C_edges:
                u, v = tuple(e)
                C_graph.add_edge(u, v)
            ok_C = True
            for comp in nx.connected_components(C_graph):
                sub = C_graph.subgraph(comp)
                if any(d != 2 for _, d in sub.degree()):
                    ok_C = False
                    break
            if not ok_C:
                continue
            # Check M is a matching.
            M_endpoints: list = []
            for e in M_edges:
                for v in e:
                    M_endpoints.append(v)
            if len(M_endpoints) != len(set(M_endpoints)):
                continue
            labels: dict[frozenset, str] = {}
            for e in T_set:
                labels[e] = "T"
            for e in C_edges:
                labels[e] = "C"
            for e in M_edges:
                labels[e] = "M"
            return labels
    return None


if __name__ == "__main__":
    G = nx.complete_graph(4)
    sol = find_3_decomposition(G)
    print("K_4 brute-force:", "found" if sol else "NONE")
    ok, _ = verify_decomposition(G, sol)
    print("  verified:", ok)
