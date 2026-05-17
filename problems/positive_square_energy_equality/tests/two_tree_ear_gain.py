"""For each enumerated 2-tree of order n>=4, for every simplicial deg-2 vertex v
with G-v != K_2, compute the ear gains delta+ = s+(G)-s+(G-v),
delta- = s-(G)-s-(G-v), and report violations of the 17/16 bound."""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import networkx as nx
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from spectrum_check import s_plus_minus  # noqa: E402


THRESHOLD = 17.0 / 16.0
FIXTURE_DIR = ROOT / "tests" / "fixtures"


def graph6(G: nx.Graph) -> str:
    return nx.to_graph6_bytes(G, header=False).decode().strip()


def from_graph6(code: str) -> nx.Graph:
    return nx.from_graph6_bytes(code.encode())


def simplicial_deg2_vertices(G: nx.Graph):
    """Vertices v with deg(v)=2 whose two neighbours a,b are adjacent."""
    for v in G.nodes():
        if G.degree(v) != 2:
            continue
        a, b = list(G.neighbors(v))
        if G.has_edge(a, b):
            yield v, a, b


def book_with_tail(k: int, t: int) -> nx.Graph:
    """Book B_k on spine {0,1}, with a 2-path of t triangles attached at edge {0,2}.

    This is the structured BT(k,t) family from docs/two_tree_ear_lemma.md.
    For t=2 and k large, the tail ear refutes the universal ear-deletion lemma.
    """
    G = nx.Graph()
    G.add_edge(0, 1)
    for j in range(k):
        G.add_edge(0, 2 + j)
        G.add_edge(1, 2 + j)
    if t >= 1:
        u = k + 2
        G.add_edge(0, u)
        G.add_edge(2, u)
    prev = 2
    prev_partner = k + 2
    for s in range(1, t):
        new_v = k + 2 + s
        G.add_edge(prev, new_v)
        G.add_edge(prev_partner, new_v)
        prev, prev_partner = prev_partner, new_v
    return G


def analyse(G: nx.Graph) -> list[dict]:
    n = G.number_of_nodes()
    full = s_plus_minus(G)
    results = []
    for v, a, b in simplicial_deg2_vertices(G):
        H = G.copy()
        H.remove_node(v)
        if H.number_of_nodes() < 3:
            continue
        if H.number_of_edges() == 1 and H.number_of_nodes() == 2:
            continue  # G-v == K_2 base case
        sub = s_plus_minus(H)
        d_plus = full["s_plus"] - sub["s_plus"]
        d_minus = full["s_minus"] - sub["s_minus"]
        results.append({
            "v": v,
            "a": a,
            "b": b,
            "deg_a_in_H": H.degree(a),
            "deg_b_in_H": H.degree(b),
            "delta_plus": d_plus,
            "delta_minus": d_minus,
            "min_delta": min(d_plus, d_minus),
            "below_threshold": min(d_plus, d_minus) < THRESHOLD - 1e-12,
        })
    return results


def summarise(per_graph: list[dict]):
    all_delta_plus, all_delta_minus = [], []
    violators = []
    min_plus_record, min_minus_record = None, None
    for entry in per_graph:
        for ear in entry["ears"]:
            all_delta_plus.append((ear["delta_plus"], entry["g6"], ear))
            all_delta_minus.append((ear["delta_minus"], entry["g6"], ear))
            if ear["below_threshold"]:
                violators.append({"g6": entry["g6"], **ear})
    if all_delta_plus:
        min_plus_record = min(all_delta_plus, key=lambda t: t[0])
    if all_delta_minus:
        min_minus_record = min(all_delta_minus, key=lambda t: t[0])
    # detect whether minimizing v differs between + and - within each graph
    differing = []
    for entry in per_graph:
        if not entry["ears"]:
            continue
        argmin_plus = min(entry["ears"], key=lambda e: e["delta_plus"])["v"]
        argmin_minus = min(entry["ears"], key=lambda e: e["delta_minus"])["v"]
        if argmin_plus != argmin_minus:
            # also report value gap
            differing.append({
                "g6": entry["g6"],
                "argmin_plus_v": argmin_plus,
                "argmin_minus_v": argmin_minus,
            })
    return {
        "min_delta_plus": min_plus_record,
        "min_delta_minus": min_minus_record,
        "violators": violators,
        "graphs_with_different_min_argmin": differing,
    }


def ear_by_vertex(G: nx.Graph, v: int) -> dict:
    for ear in analyse(G):
        if ear["v"] == v:
            return ear
    raise AssertionError(f"vertex {v} is not an analysed simplicial ear")


def fixture_counterexamples() -> list[dict]:
    path = FIXTURE_DIR / "two_tree_universal_counterexamples.json"
    return json.loads(path.read_text())


def test_universal_two_tree_ear_lemma_is_false_on_bt_fixtures():
    """Regression: do not revive the false universal ear-deletion lemma."""
    for fixture in fixture_counterexamples():
        assert fixture["family"] == "book_with_tail"
        G = book_with_tail(fixture["k"], fixture["t"])
        assert G.number_of_nodes() == fixture["n"]
        ear = ear_by_vertex(G, fixture["tail_vertex"])
        assert {ear["a"], ear["b"]} == set(fixture["supporting_edge"])
        assert ear["delta_minus"] < fixture["expected_delta_minus_max"]
        assert ear["min_delta"] < THRESHOLD


def test_existential_two_tree_ear_rescue_holds_on_bt_fixtures():
    """The same fixtures still have a good ear, so only the universal form dies."""
    for fixture in fixture_counterexamples():
        G = book_with_tail(fixture["k"], fixture["t"])
        ears = analyse(G)
        best = max(ears, key=lambda ear: ear["min_delta"])
        assert best["min_delta"] >= THRESHOLD


def main():
    max_n = int(sys.argv[1]) if len(sys.argv) > 1 else 9
    data_dir = ROOT / "data"
    path = data_dir / f"two_trees_n{max_n}.json"
    enumeration = json.loads(path.read_text())

    per_n_min_plus, per_n_min_minus = {}, {}
    for n_str, codes in enumeration.items():
        n = int(n_str)
        if n < 4:
            continue
        per_graph = []
        for code in codes:
            G = from_graph6(code)
            ears = analyse(G)
            per_graph.append({"g6": code, "n": n, "ears": ears})

        # Save per-n JSON
        (data_dir / f"two_tree_ear_gains_n{n}.json").write_text(json.dumps(per_graph))

        summary = summarise(per_graph)
        mp = summary["min_delta_plus"]
        mm = summary["min_delta_minus"]
        per_n_min_plus[n] = mp[0] if mp else math.inf
        per_n_min_minus[n] = mm[0] if mm else math.inf
        print(f"n={n}: {len(codes)} 2-trees, "
              f"min delta+ = {mp[0]:.10f}, min delta- = {mm[0]:.10f}, "
              f"violators = {len(summary['violators'])}, "
              f"argmin differs in {len(summary['graphs_with_different_min_argmin'])} graphs")
        if mp:
            print(f"  argmin delta+: g6={mp[1]}, v={mp[2]['v']}, "
                  f"deg_a_in_H={mp[2]['deg_a_in_H']}, deg_b_in_H={mp[2]['deg_b_in_H']}")
        if mm:
            print(f"  argmin delta-: g6={mm[1]}, v={mm[2]['v']}, "
                  f"deg_a_in_H={mm[2]['deg_a_in_H']}, deg_b_in_H={mm[2]['deg_b_in_H']}")
        if summary["violators"]:
            print(f"  VIOLATOR(S) below 17/16 = {THRESHOLD:.10f}:")
            for v in summary["violators"][:5]:
                print(f"    g6={v['g6']} v={v['v']} delta+={v['delta_plus']:.6f} "
                      f"delta-={v['delta_minus']:.6f}")

    print("\nPer-order minimums (delta+, delta-):")
    for n in sorted(per_n_min_plus):
        print(f"  n={n}: delta+={per_n_min_plus[n]:.10f}, "
              f"delta-={per_n_min_minus[n]:.10f}")


if __name__ == "__main__":
    main()
