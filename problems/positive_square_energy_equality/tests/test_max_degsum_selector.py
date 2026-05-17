"""Verify the max-degsum selector conjecture broadly.

Conjecture:
    For every 2-tree G on n >= 4 vertices, the simplicial degree-2 ear v*
    maximizing deg_{G-v*}(a) + deg_{G-v*}(b) satisfies
        min(delta+(v*), delta-(v*)) >= 17/16.

Tests:
1. Enumerated 2-trees, n in {4..10}, using cached data/two_tree_ear_gains_n*.json.
2. Random 2-trees, n in {20, 30, 50, 100}, 50 seeds each (200 graphs total).
3. BT(k, 2) family for k in {5, 10, 25, 50, 100, 200}: max-degsum ear must be
   a page ear (degsum ~ 2k+1), not the tail (degsum 5).
"""
from __future__ import annotations

import json
import random
import sys
from pathlib import Path

import networkx as nx
import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from spectrum_check import s_plus_minus  # noqa: E402
from extreme_family import book_with_tail  # noqa: E402
from two_tree_enum import (  # noqa: E402
    enumerate_two_trees,
    from_graph6 as enum_from_graph6,
)

THRESHOLD = 17.0 / 16.0
EPS = 1e-12

DATA_DIR = ROOT / "data"
FIXTURE_DIR = ROOT / "tests" / "fixtures"


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------

def simplicial_deg2_ears(G: nx.Graph):
    """Yield (v, a, b) for simplicial degree-2 vertices v with G - v having
    at least 3 vertices."""
    for v in G.nodes():
        if G.degree(v) != 2:
            continue
        a, b = list(G.neighbors(v))
        if not G.has_edge(a, b):
            continue
        if G.number_of_nodes() - 1 < 3:
            continue
        yield v, a, b


def compute_ear_record(G: nx.Graph, full=None) -> list[dict]:
    """For each simplicial deg-2 ear v of G, return delta+/-(v), deg_a, deg_b
    in H = G - v."""
    if full is None:
        full = s_plus_minus(G)
    out = []
    for v, a, b in simplicial_deg2_ears(G):
        H = G.copy()
        H.remove_node(v)
        if H.number_of_nodes() < 3:
            continue
        sub = s_plus_minus(H)
        d_plus = full["s_plus"] - sub["s_plus"]
        d_minus = full["s_minus"] - sub["s_minus"]
        out.append({
            "v": v,
            "a": a,
            "b": b,
            "deg_a_in_H": H.degree(a),
            "deg_b_in_H": H.degree(b),
            "deg_sum_in_H": H.degree(a) + H.degree(b),
            "delta_plus": float(d_plus),
            "delta_minus": float(d_minus),
            "min_delta": float(min(d_plus, d_minus)),
        })
    return out


def max_degsum_ears(ears: list[dict]) -> list[dict]:
    """Return the sub-list of ears whose deg_sum_in_H is maximal (handle ties)."""
    if not ears:
        return []
    max_ds = max(e["deg_sum_in_H"] for e in ears)
    return [e for e in ears if e["deg_sum_in_H"] == max_ds]


def random_two_tree(n: int, seed: int) -> nx.Graph:
    """Build a random 2-tree on n>=3 vertices.

    Start with K_3 on {0,1,2}; at each step pick a uniformly random existing
    edge (a, b) and attach a new vertex v adjacent to both a and b. Deterministic
    given seed.
    """
    assert n >= 3
    rng = random.Random(seed)
    G = nx.complete_graph(3)
    while G.number_of_nodes() < n:
        edges = list(G.edges())
        a, b = rng.choice(edges)
        v = G.number_of_nodes()
        G.add_node(v)
        G.add_edge(v, a)
        G.add_edge(v, b)
    return G


def ears_from_cached_json(n: int) -> list[dict] | None:
    """Return list of {g6, n, ears} from data/two_tree_ear_gains_n{n}.json,
    augmented with deg_sum_in_H for each ear. Returns None if file missing."""
    p = DATA_DIR / f"two_tree_ear_gains_n{n}.json"
    if not p.exists():
        return None
    data = json.loads(p.read_text())
    for entry in data:
        for ear in entry["ears"]:
            ear["deg_sum_in_H"] = ear["deg_a_in_H"] + ear["deg_b_in_H"]
    return data


def graph_from_g6(code: str) -> nx.Graph:
    return nx.from_graph6_bytes(code.encode())


# ----------------------------------------------------------------------
# Test 1: enumerated 2-trees, n in {4..10}
# ----------------------------------------------------------------------

@pytest.mark.parametrize("n", [4, 5, 6, 7, 8, 9, 10])
def test_max_degsum_selector_on_enumerated_two_trees(n, record_property):
    """For every enumerated 2-tree on n vertices, every max-degsum ear
    satisfies min(delta+, delta-) >= 17/16."""
    cached = ears_from_cached_json(n)
    if cached is None:
        # Fallback: re-enumerate and compute.
        enumeration = enumerate_two_trees(n)
        codes = enumeration[n]
        cached = []
        for code in codes:
            G = graph_from_g6(code)
            ears = compute_ear_record(G)
            cached.append({"g6": code, "n": n, "ears": ears})

    min_over_max_degsum = float("inf")
    argmin_record = None
    for entry in cached:
        ears = entry["ears"]
        if not ears:
            continue
        tied = max_degsum_ears(ears)
        assert tied, f"n={n} g6={entry['g6']}: no max-degsum ear found"
        for ear in tied:
            md = ear["min_delta"]
            assert md >= THRESHOLD - EPS, (
                f"n={n} g6={entry['g6']} v={ear['v']}: max-degsum ear has "
                f"min(delta+, delta-) = {md} < 17/16 = {THRESHOLD}; "
                f"deg_sum_in_H = {ear['deg_sum_in_H']}, "
                f"delta+={ear['delta_plus']}, delta-={ear['delta_minus']}"
            )
            if md < min_over_max_degsum:
                min_over_max_degsum = md
                argmin_record = {"g6": entry["g6"], **ear}

    record_property("n", n)
    record_property("min_over_max_degsum", min_over_max_degsum)
    if argmin_record is not None:
        record_property("argmin_g6", argmin_record["g6"])
        record_property("argmin_v", argmin_record["v"])
    print(
        f"\n[max-degsum selector] n={n}: "
        f"min over max-degsum ears = {min_over_max_degsum:.10f} "
        f"(threshold 17/16 = {THRESHOLD:.10f})"
    )
    if argmin_record is not None:
        print(
            f"  argmin: g6={argmin_record['g6']} v={argmin_record['v']} "
            f"deg_sum_in_H={argmin_record['deg_sum_in_H']} "
            f"delta+={argmin_record['delta_plus']:.6f} "
            f"delta-={argmin_record['delta_minus']:.6f}"
        )


# ----------------------------------------------------------------------
# Test 2: random 2-trees
# ----------------------------------------------------------------------

@pytest.mark.parametrize("n", [20, 30, 50, 100])
@pytest.mark.parametrize("seed", list(range(50)))
def test_max_degsum_selector_on_random_two_trees(n, seed):
    """Random 2-trees on n vertices (seed-deterministic) satisfy the
    max-degsum selector conjecture."""
    G = random_two_tree(n, seed)
    assert G.number_of_nodes() == n
    ears = compute_ear_record(G)
    assert ears, f"n={n} seed={seed}: no simplicial deg-2 ears found"
    tied = max_degsum_ears(ears)
    assert tied
    for ear in tied:
        md = ear["min_delta"]
        if md < THRESHOLD - EPS:
            # Record violation, then fail loudly with full context.
            g6 = nx.to_graph6_bytes(G, header=False).decode().strip()
            violation = {
                "n": n,
                "seed": seed,
                "g6": g6,
                "v": ear["v"],
                "a": ear["a"],
                "b": ear["b"],
                "deg_sum_in_H": ear["deg_sum_in_H"],
                "delta_plus": ear["delta_plus"],
                "delta_minus": ear["delta_minus"],
                "min_delta": ear["min_delta"],
            }
            _append_violation(violation)
            pytest.fail(
                f"max-degsum selector violation: n={n} seed={seed} g6={g6} "
                f"v={ear['v']} deg_sum_in_H={ear['deg_sum_in_H']} "
                f"min_delta={md} < 17/16"
            )


def _append_violation(record: dict) -> None:
    FIXTURE_DIR.mkdir(parents=True, exist_ok=True)
    path = FIXTURE_DIR / "max_degsum_violations.json"
    if path.exists():
        try:
            cur = json.loads(path.read_text())
        except Exception:
            cur = []
    else:
        cur = []
    cur.append(record)
    path.write_text(json.dumps(cur, indent=2))


def test_max_degsum_violations_fixture_initialized():
    """Ensure the violations fixture exists; default content is an empty list."""
    FIXTURE_DIR.mkdir(parents=True, exist_ok=True)
    path = FIXTURE_DIR / "max_degsum_violations.json"
    if not path.exists():
        path.write_text(json.dumps([]))
    cur = json.loads(path.read_text())
    assert isinstance(cur, list)


# ----------------------------------------------------------------------
# Test 3: BT(k, 2) family
# ----------------------------------------------------------------------

@pytest.mark.parametrize("k", [5, 10, 25, 50, 100, 200])
def test_max_degsum_selector_on_BT_family(k):
    """In BT(k, 2), the max-degsum ear must be a book-page ear (degsum 2k+1),
    not the tail (degsum 5). It satisfies min(delta+, delta-) >= 17/16."""
    G = book_with_tail(k, 2)
    n = G.number_of_nodes()
    assert n == k + 4  # B_k has k+2 vertices; t=2 adds 2 more
    ears = compute_ear_record(G)
    assert ears, f"k={k}: no simplicial deg-2 ears"

    tied = max_degsum_ears(ears)
    assert tied

    # The tail vertex is k + 3 (added on edge (2, k+2) after first tail step).
    tail_vertex = k + 3
    page_vertices = set(range(2, k + 2))  # pages of B_k on spine (0,1)

    for ear in tied:
        assert ear["v"] != tail_vertex, (
            f"k={k}: tail vertex {tail_vertex} is incorrectly picked as a "
            f"max-degsum ear (degsum_in_H = {ear['deg_sum_in_H']})"
        )
        assert ear["v"] in page_vertices, (
            f"k={k}: max-degsum ear v={ear['v']} is not a book page; "
            f"page_vertices={sorted(page_vertices)}"
        )
        # The page ear in BT(k, 2) has neighbors 0 and 1. In H = G - v,
        # deg(0) = k+2 (n-2 of the (n-1)-vertex H minus 2? actually):
        # We just sanity-check the deg sum is the maximum and equals 2k+1.
        assert ear["deg_sum_in_H"] == 2 * k + 1, (
            f"k={k}: max-degsum page ear deg_sum_in_H = {ear['deg_sum_in_H']}, "
            f"expected 2k+1 = {2*k+1}"
        )
        # Min(delta+, delta-) >= 17/16.
        md = ear["min_delta"]
        assert md >= THRESHOLD - EPS, (
            f"k={k}: max-degsum page ear v={ear['v']} has min_delta={md} "
            f"< 17/16 = {THRESHOLD}"
        )

    # Also verify the tail ear (degsum 5) is NOT the max-degsum ear.
    tail_ears = [e for e in ears if e["v"] == tail_vertex]
    assert len(tail_ears) == 1, f"k={k}: tail vertex not found among ears"
    assert tail_ears[0]["deg_sum_in_H"] == 5, (
        f"k={k}: tail ear deg_sum_in_H = {tail_ears[0]['deg_sum_in_H']}, "
        f"expected 5"
    )


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v", "-s"]))
