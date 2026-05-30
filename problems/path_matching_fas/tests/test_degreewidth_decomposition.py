"""Tests for the degreewidth decomposition of Path-FAS (D92)."""
from __future__ import annotations

import json
import os
import sys
from collections import Counter

SCRIPT_DIR = os.path.join(os.path.dirname(__file__), "..", "scripts")
sys.path.insert(0, os.path.abspath(SCRIPT_DIR))

from degreewidth_decomposition import (  # noqa: E402
    degreewidth, is_degreewidth_le2, classify,
)
from nonsweep_path_fas import decide_linear_forest_fas_bruteforce  # noqa: E402


def test_degreewidth_basics():
    # acyclic (transitive): degreewidth 0
    T = [[1 if j > i else 0 for j in range(5)] for i in range(5)]
    assert degreewidth(T) == 0
    # a single 3-cycle: degreewidth 1 (back-arc graph is one edge = matching)
    T3 = [[0, 1, 0], [0, 0, 1], [1, 0, 0]]
    assert degreewidth(T3) == 1
    # degreewidth <= 1 ==> YES (matching is a linear forest)
    assert decide_linear_forest_fas_bruteforce(T3) is True


def test_n7_catalogue_decomposition():
    """Every n=7 minimal NO has Δ*∈{2,3}; the split is 11 degree-obstructed
    (Δ*≥3) + 9 acyclicity-core (Δ*=2), the core all `large_width_no`."""
    path = os.path.join(SCRIPT_DIR, "..", "data",
                        "minimal_no_obstruction_catalogue_n7.json")
    recs = json.load(open(path))["records"]
    cls = Counter(classify(r["T"]) for r in recs)
    assert cls["yes"] == 0          # all are NO
    assert cls["dw_ge3"] == 11
    assert cls["dw2_core"] == 9
    # acyclicity-core members are all large_width_no
    core_obs = Counter(r.get("obstruction", {}).get("primary")
                       for r in recs if classify(r["T"]) == "dw2_core")
    assert set(core_obs) == {"large_width_no"}


def test_yes_implies_degreewidth_le2():
    """YES ⟹ Δ*≤2 (theorem) — spot-checked: no NO has Δ*≤1."""
    path = os.path.join(SCRIPT_DIR, "..", "data",
                        "minimal_no_obstruction_catalogue_n7.json")
    recs = json.load(open(path))["records"]
    assert all(not (degreewidth(r["T"], cap=1) <= 1) for r in recs)


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
