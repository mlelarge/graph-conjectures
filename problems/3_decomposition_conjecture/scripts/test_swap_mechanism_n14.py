"""Test the simple swap mechanism on the 7 essentially-3-conn n=14
exception graphs.

For each: enumerate all (T_TM, T_TM) split partitions sigma. For each
sigma, identify w_0 (other endpoint of port 0's M-edge inside H) and
from pathlib import Path
w_1 (similar for port 1), then compute T_H's two components A
(containing port 0) and B (containing port 1).

The simple swap (w_0 in B) yields (M_TT, T_TM) by toggling m_0 to T.
Symmetric for w_1 in A. A "good swap pair" needs w_0 in B AND w_1 in A
simultaneously to give (M_TT, T_T) via double-swap (which may also
require T-edge demotion to break a cycle).

Report per-exception:
- count of (T_TM, T_TM) split partitions
- count where w_0 in B
- count where w_1 in A
- count where both (the "ideal" simple-swap)

This is a sanity check on the swap construction.
"""
import json, sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import networkx as nx
import itertools
from decomposition import (
    edges_of, edge_key, is_subcubic_partition_valid, BOUNDARY_COLOUR,
    PORT_STATE_DATA,
)


def find_TTM_TTM_split_partitions(H, ports):
    """Enumerate all valid partitions realising (T_TM, T_TM) split."""
    out = []
    edges = edges_of(H)
    n = H.number_of_nodes()
    # T_TM,T_TM split: both ports V_M, side (T,M), pi has 2 components
    # |T_H| = n - 2 (split into 2 components)
    for T_subset in itertools.combinations(edges, n - 2):
        T_set = set(T_subset)
        T_graph = nx.Graph()
        T_graph.add_nodes_from(H.nodes())
        for e in T_set:
            u, v = tuple(e)
            T_graph.add_edge(u, v)
        if not nx.is_forest(T_graph):
            continue
        comps = list(nx.connected_components(T_graph))
        if len(comps) != 2:
            continue
        # T_H must have port 0 in one component and port 1 in the other.
        p0, p1 = ports
        comp_of_p0 = next(i for i, c in enumerate(comps) if p0 in c)
        comp_of_p1 = next(i for i, c in enumerate(comps) if p1 in c)
        if comp_of_p0 == comp_of_p1:
            continue
        # Iterate cotree partitions
        cotree = [e for e in edges if e not in T_set]
        for mask in range(1 << len(cotree)):
            labels = {e: "T" for e in T_set}
            for i, e in enumerate(cotree):
                labels[e] = "C" if (mask >> i) & 1 else "M"
            if not is_subcubic_partition_valid(H, labels, ports):
                continue
            # Check port states are T_TM at both
            # For T_TM: deg_T_H=1, deg_C_H=0, deg_M_H=1
            def port_state(p):
                deg_t = sum(1 for w in H.neighbors(p) if labels[edge_key(p, w)] == "T")
                deg_c = sum(1 for w in H.neighbors(p) if labels[edge_key(p, w)] == "C")
                deg_m = sum(1 for w in H.neighbors(p) if labels[edge_key(p, w)] == "M")
                return (deg_t, deg_c, deg_m)
            s0 = port_state(p0)
            s1 = port_state(p1)
            if s0 != (1, 0, 1) or s1 != (1, 0, 1):
                continue
            out.append({
                "labels": labels,
                "comp_A": comps[comp_of_p0],
                "comp_B": comps[comp_of_p1],
            })
    return out


def analyse_swap(partition, ports, H):
    """Compute w_0 and w_1 from a (T_TM, T_TM) split partition and
    check the swap conditions."""
    p0, p1 = ports
    labels = partition["labels"]
    A = partition["comp_A"]
    B = partition["comp_B"]

    def find_m_neighbor(p):
        for w in H.neighbors(p):
            if labels[edge_key(p, w)] == "M":
                return w
        return None

    w0 = find_m_neighbor(p0)
    w1 = find_m_neighbor(p1)
    w0_in_B = w0 in B
    w1_in_A = w1 in A
    return {"w0": w0, "w1": w1, "w0_in_B": w0_in_B, "w1_in_A": w1_in_A}


def main():
    with open(str(Path(__file__).resolve().parent.parent / 'data') + '/n14_essentially_3conn_C0_exceptions.json') as f:
        exc = json.load(f)

    # Group by graph6
    by_g6 = {}
    for r in exc['records']:
        by_g6.setdefault(r['graph6'], r['ports'])

    for g6 in sorted(by_g6):
        ports = by_g6[g6]
        G = nx.from_graph6_bytes(g6.encode())
        print(f"\n{g6} ports={ports}", flush=True)
        partitions = find_TTM_TTM_split_partitions(G, ports)
        print(f"  (T_TM, T_TM) split partitions: {len(partitions)}", flush=True)
        if not partitions:
            print("  WARNING: no split partitions found!", flush=True)
            continue
        w0_in_B_count = 0
        w1_in_A_count = 0
        both_count = 0
        for p in partitions:
            r = analyse_swap(p, ports, G)
            if r["w0_in_B"]:
                w0_in_B_count += 1
            if r["w1_in_A"]:
                w1_in_A_count += 1
            if r["w0_in_B"] and r["w1_in_A"]:
                both_count += 1
        print(f"  w_0 in B: {w0_in_B_count}/{len(partitions)}", flush=True)
        print(f"  w_1 in A: {w1_in_A_count}/{len(partitions)}", flush=True)
        print(f"  BOTH (simple double-swap candidate): {both_count}/{len(partitions)}", flush=True)


if __name__ == "__main__":
    main()
