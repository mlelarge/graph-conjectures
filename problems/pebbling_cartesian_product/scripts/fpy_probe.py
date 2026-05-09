"""Probe FPY (Flocco-Pulaj-Yerger) PebblingGraph + TreeStrategy semantics.

Goal: lock down the runtime vertex/root label format and the
saveCertificate matrix convention against the *current* FPY source,
then run a full round-trip through our ingest adapter to confirm the
bridge is byte-stable: live FPY classes -> CSV -> adapter -> Strategy
record with the same weights and edges we constructed.

Run with:

    source .venv/bin/activate
    python scripts/fpy_probe.py

This is a self-test, not a reproduction of FPY's 96 bound: we hand-build
a small synthetic strategy. Reproducing 96 needs FPY's MILP output,
which lives behind Gurobi.
"""
from __future__ import annotations

import os
import sys
import types
from pathlib import Path

import networkx as nx
import pandas as pd

REPO = Path(__file__).resolve().parents[1]
FPY_DIR = REPO / "external" / "Graph_Pebbling" / "py"


def stub_gurobipy() -> None:
    if "gurobipy" in sys.modules:
        return
    gp = types.ModuleType("gurobipy")
    gp.GRB = types.SimpleNamespace()
    gp.Model = lambda *a, **kw: None
    sys.modules["gurobipy"] = gp


def main() -> None:
    stub_gurobipy()
    sys.path.insert(0, str(FPY_DIR))
    from PebblingGraph import PebblingGraph
    from TreeStrategy import TreeStrategy

    # Lemke graph (FPY's L_fpy labelling, copied verbatim from main.py).
    lemke_edges = [
        (0, 1), (0, 2), (1, 3), (2, 4), (2, 5), (2, 6),
        (3, 4), (3, 5), (3, 6), (3, 7), (4, 7), (5, 7), (6, 7),
    ]
    lemke = PebblingGraph(lemke_edges, 0)
    lemke_square_g = nx.cartesian_product(lemke.graph, lemke.graph)
    lemke_square_edges = list(lemke_square_g.edges())

    # Mimic main() (live path): root iterates `initPebblingGraph.nodes`
    # which are strings like "('0', '1')".
    init_pg = PebblingGraph(lemke_square_edges, 0)
    print("=== runtime node labels in cartesian Pebbling graph ===")
    sample_nodes = list(init_pg.nodes)[:8]
    for v in sample_nodes:
        print(f"  node repr: {v!r}  type={type(v).__name__}  v[2]={v[2]!r}  v[7]={v[7]!r}")

    # Pick an off-diagonal easy root, "('0', '1')".
    root_label = "('0', '1')"
    assert root_label in init_pg.nodes, "expected root_label to be present in nodes"
    pg = PebblingGraph(lemke_square_edges, root_label)
    print(f"\n=== PebblingGraph constructed with root={root_label!r} ===")
    print(f"  pg.root = {pg.root!r}")
    print(f"  root in pg.graph: {pg.root in pg.graph.nodes}")
    print(f"  |V| = {len(pg.nodes)}, |E| = {len(pg.edges)}")

    # Build a tiny synthetic basic Hurlbert tree:
    #   root r = ('0','1')
    #   neighbour u = ('0','0')   weight 2
    #   neighbour w = ('1','1')   weight 2  (in L, edge 0-1)
    # Dummy weights at non-support nodes are 0.
    r = pg.root
    u = "('0', '0')"
    w = "('1', '1')"
    assert pg.graph.has_edge(r, u), f"missing edge {r}-{u}"
    assert pg.graph.has_edge(r, w), f"missing edge {r}-{w}"

    ts = TreeStrategy(pg, root=r, length=2)
    ts.addEdge(r, u)
    ts.addEdge(r, w)
    ts.addWeight(r, 0)
    ts.addWeight(u, 2)
    ts.addWeight(w, 2)
    # Pad zeros for every other vertex (saveCertificate iterates only
    # ts.nodes, so this is not strictly needed; included for clarity).
    print("\n=== synthetic strategy ===")
    print(f"  edges: {ts.edges}")
    print(f"  weights: {ts.weights}")
    print(f"  ts.nodes: {ts.nodes}")
    print(f"  ts.size() (=|edges|): {ts.size()}")

    # Save via FPY API and read back.
    out_dir = REPO / "data" / "fpy_probe"
    out_dir.mkdir(parents=True, exist_ok=True)
    cert_path = out_dir / "synthetic_cert.csv"
    edges_path = out_dir / "synthetic_edges.csv"
    cwd = os.getcwd()
    try:
        os.chdir(out_dir)  # in case FPY uses relative paths internally
        ts.saveCertificate(str(cert_path))
        ts.saveEdges(str(edges_path))
    finally:
        os.chdir(cwd)

    print(f"\n=== saved certificate: {cert_path} ===")
    df = pd.read_csv(cert_path, index_col=0)
    print(df.to_string())

    # Verify saveCertificate convention: cert[i][j] == w(vertex (i, j)).
    # Our weights: r=('0','1') -> 0, u=('0','0') -> 2, w=('1','1') -> 2.
    expected = {(0, 1): 0.0, (0, 0): 2.0, (1, 1): 2.0}
    print("\n=== matrix-cell convention check ===")
    ok = True
    for (i, j), wexp in expected.items():
        got = float(df.iat[i, j])
        flag = "OK" if abs(got - wexp) < 1e-9 else "MISMATCH"
        print(f"  cert[{i}][{j}] = {got}  (expected {wexp})  {flag}")
        if abs(got - wexp) > 1e-9:
            ok = False
    print(f"\nconvention: cert[i][j] = w(vertex (i, j))  -- {'CONFIRMED' if ok else 'WRONG'}")

    print(f"\n=== saved edges: {edges_path} ===")
    print(pd.read_csv(edges_path).to_string())

    # ---------- Round-trip through our ingest adapter ----------
    sys.path.insert(0, str(REPO / "scripts"))
    from ingest_flocco_pulaj_yerger import parse_edges_csv, parse_weight_csv
    from pebbling_graphs import pair_to_index

    weight_text = cert_path.read_text()
    edges_text = edges_path.read_text()
    weights, w_warn = parse_weight_csv(weight_text, h_n=8)
    edges_parsed, e_warn = parse_edges_csv(edges_text, h_n=8)

    print("\n=== round-trip via ingest_flocco_pulaj_yerger ===")
    print(f"  weight warnings: {w_warn or 'none'}")
    print(f"  edges  warnings: {e_warn or 'none'}")
    print(f"  parsed weights (flat idx -> Fraction):")
    for v in sorted(weights):
        i, j = divmod(v, 8)
        print(f"    idx={v} ((i,j)=({i},{j})) -> {weights[v]}")
    print(f"  parsed edges (flat-idx unordered pairs): {edges_parsed}")

    # Rebuild ground truth from the synthetic strategy.
    expected_weights_pairs = {(0, 0): 2, (1, 1): 2}  # w(r)=0 dropped
    expected_weights_flat = {
        pair_to_index(i, j, 8): w for (i, j), w in expected_weights_pairs.items()
    }
    r_idx = pair_to_index(0, 1, 8)  # 1
    u_idx = pair_to_index(0, 0, 8)  # 0
    w_idx = pair_to_index(1, 1, 8)  # 9
    expected_edges_flat = sorted({tuple(sorted((r_idx, u_idx))), tuple(sorted((r_idx, w_idx)))})

    from fractions import Fraction
    weights_match = weights == {k: Fraction(v) for k, v in expected_weights_flat.items()}
    edges_match = sorted(edges_parsed) == expected_edges_flat
    print(f"\n  weights match expected: {weights_match}")
    print(f"  edges match expected:   {edges_match}")
    if not (weights_match and edges_match):
        print("\nROUND-TRIP FAILED")
        sys.exit(1)
    print("\nROUND-TRIP OK: live FPY save -> ingest adapter agrees on weights and edges.")


if __name__ == "__main__":
    main()
