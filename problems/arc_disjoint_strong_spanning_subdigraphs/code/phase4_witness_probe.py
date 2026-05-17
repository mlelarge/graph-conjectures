"""Phase 4 lifting-lemma witness probe.

For the three hard pair-classes flagged in the Phase-3-v2 report, regenerate
a small number of deficit-aware glued candidates, re-run the SAT verifier
to extract a 2-coloring witness, and tabulate how the colors distribute
across the gluing interface and the bridges.

The three classes:
  C1.  (C8_square, C8_square)
  C2.  AiEtAl_L312_min on at least one side
  C3.  AiEtAl_iv_star_iv on at least one side

This script prints structured output (one row per instance) and writes a
compact JSON file `code/logs/phase4_lifting_probe.json` for later use.
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path
from collections import Counter

# Make the package layout match how `run_phase3_v2.py` is launched.
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from benchmarks import all_benchmarks  # noqa: E402
from digraph import Digraph  # noqa: E402
from generators.glue_deficit import (  # noqa: E402
    DeficitGenConfig,
    generate_deficit_gluings,
    passes_arc_strong_3,
)
from verifier_sat import verify_sat  # noqa: E402


# --------------------------------------------------------------------------- #
# Cut analysis primitives                                                       #
# --------------------------------------------------------------------------- #


def out_cut(arcs: list[tuple[int, int]], X: frozenset[int]) -> list[tuple[int, int]]:
    return [(u, v) for u, v in arcs if u in X and v not in X]


def in_cut(arcs: list[tuple[int, int]], X: frozenset[int]) -> list[tuple[int, int]]:
    return [(u, v) for u, v in arcs if u not in X and v in X]


def color_of_arc(arc, red_set, blue_set):
    # arc is (u,v,k); red/blue are lists of (u,v,k) keys
    if arc in red_set:
        return "R"
    if arc in blue_set:
        return "B"
    return "?"


def split_witness_arcs(witness):
    """Convert verifier witness (red_list, blue_list) of arc-keys (u,v,k) to
    two arc-multisets, keeping multiplicities."""
    red, blue = witness
    return red, blue


def color_split_of_cut(cut_arcs: list[tuple[int, int]], red, blue):
    """Given a list of (u,v) arcs (with possible multiplicities — but each
    arc-key (u,v,k) appears at most once), count how many are in each color.

    We use multiset matching: an arc (u,v) appears once for each (u,v,k) key
    in either red or blue.
    """
    red_pairs = [(u, v) for (u, v, k) in red]
    blue_pairs = [(u, v) for (u, v, k) in blue]
    nR = 0
    nB = 0
    red_ctr = Counter(red_pairs)
    blue_ctr = Counter(blue_pairs)
    for uv in cut_arcs:
        if red_ctr.get(uv, 0) > 0:
            nR += 1
            red_ctr[uv] -= 1
        elif blue_ctr.get(uv, 0) > 0:
            nB += 1
            blue_ctr[uv] -= 1
        else:
            # Should not happen if cut_arcs is drawn from the same arc multiset
            pass
    return nR, nB


def vertex_partition(n: int, n_non1: int, s: int) -> dict[str, frozenset[int]]:
    """Return the three pieces of the labelling produced by
    `_glue_along_interface`:
      side1_non = {0, ..., n_non1 - 1}
      interface = {n_non1, ..., n_non1 + s - 1}
      side2_non = {n_non1 + s, ..., n - 1}
    """
    side1_non = frozenset(range(0, n_non1))
    interface = frozenset(range(n_non1, n_non1 + s))
    side2_non = frozenset(range(n_non1 + s, n))
    return {"S1_non": side1_non, "interface": interface, "S2_non": side2_non}


# --------------------------------------------------------------------------- #
# Per-instance analysis                                                        #
# --------------------------------------------------------------------------- #


def analyse_instance(inst):
    """Run SAT verifier on `inst`, then describe color routing across the
    gluing interface and bridges.
    """
    D = inst.build()
    if not passes_arc_strong_3(D, exact=True):
        return None
    res = verify_sat(D, time_limit_s=30.0)
    if res["status"] != "SAT":
        return {"name": inst.name, "status": res["status"]}

    red, blue = res["witness"]
    arcs = inst.arcs
    n_non1 = inst.n - len(inst.S2) - (inst.n - len(inst.S1) - len(inst.S2))  # = side1 non-iface
    # Easier: recompute from the labelling convention.
    s = len(inst.S1)
    n_non1 = (inst.n - s) - (inst.n - len(inst.S1) - len([v for v in range(inst.n) if v not in inst.S1]))
    # Use the relabel scheme: side1 non-iface live in [0, T1.n - s),
    # interface in [T1.n - s, T1.n), side2 non-iface in [T1.n, n).
    # We can deduce T1.n by reading bridges_12 tails (they live in T1's non-iface
    # or interface but not in T2's non-iface).
    # Cleaner: get from inst attributes (n, S1, S2): T1.n_non = n - s - T2.n_non.
    # But T2.n_non = number of side-2 non-iface vertices = n - s - T1.n_non.
    # Bridges_12 are pairs (u, v) with u in side-1 and v in side-2.
    # So min head over bridges_12 - 0 + 1 ≈ start of side-2 = T1.n_non + s.
    # Use bridges_12.
    if inst.bridges_12:
        side2_start = min(v for (u, v) in inst.bridges_12)
        # but some bridges might go u -> interface; we want non-iface side-2 only.
        # Interface labels are [T1.n_non, T1.n_non + s).
        # Safer: pick min(v for (u,v) in bridges_12 if v >= T1.n_non + s) — but
        # we don't know T1.n_non yet. Just iterate.
        # Take heads of bridges_12 and find the consistent split.
    # Fallback: look up T1.n_non via benchmark lookup.
    bench = {b.name: b for b in all_benchmarks()}
    T1 = bench[inst.template1]
    T2 = bench[inst.template2]
    n_non1 = T1.n - s
    interface_start = n_non1
    interface_end = n_non1 + s
    side2_start = interface_end

    # Compute side-arcs vs interface vs bridge classification.
    side1_arcs = []
    side2_arcs = []
    interface_internal_arcs = []  # both endpoints in interface
    side1_to_interface = []
    interface_to_side1 = []
    side2_to_interface = []
    interface_to_side2 = []
    bridges_1_to_2 = []  # tail side1-non-iface, head side2-non-iface or interface (latter unlikely)
    bridges_2_to_1 = []

    def side_of(v):
        if v < interface_start:
            return "S1"
        if v < interface_end:
            return "I"
        return "S2"

    # arcs come from inst.arcs; for the verifier these were inserted in
    # MultiDiGraph order so the arc-keys (u,v,k) are 0-indexed by appearance.
    # We need to map back to color. Easier: build the same MultiDiGraph and
    # iterate arcs in matching order. The Digraph.from_arcs adds arcs in the
    # provided order. The verifier's arc-key (u, v, k) is what we see in red/blue.
    # We reconstruct (u,v,k) by counting parallel arcs in order.
    parallel_ctr: Counter = Counter()
    keyed_arcs: list[tuple[int, int, int]] = []
    for (u, v) in arcs:
        k = parallel_ctr[(u, v)]
        keyed_arcs.append((u, v, k))
        parallel_ctr[(u, v)] += 1

    red_set = set(red)
    blue_set = set(blue)
    color_of = {}
    for ke in keyed_arcs:
        if ke in red_set:
            color_of[ke] = "R"
        elif ke in blue_set:
            color_of[ke] = "B"

    for ke in keyed_arcs:
        u, v, _ = ke
        su, sv = side_of(u), side_of(v)
        c = color_of.get(ke, "?")
        if (su, sv) == ("S1", "S1"):
            side1_arcs.append((ke, c))
        elif (su, sv) == ("S2", "S2"):
            side2_arcs.append((ke, c))
        elif (su, sv) == ("I", "I"):
            interface_internal_arcs.append((ke, c))
        elif (su, sv) == ("S1", "I"):
            side1_to_interface.append((ke, c))
        elif (su, sv) == ("I", "S1"):
            interface_to_side1.append((ke, c))
        elif (su, sv) == ("S2", "I"):
            side2_to_interface.append((ke, c))
        elif (su, sv) == ("I", "S2"):
            interface_to_side2.append((ke, c))
        elif (su, sv) == ("S1", "S2"):
            bridges_1_to_2.append((ke, c))
        elif (su, sv) == ("S2", "S1"):
            bridges_2_to_1.append((ke, c))
        # other combinations impossible

    def color_count(lst):
        ctr = Counter(c for _, c in lst)
        return {"R": ctr.get("R", 0), "B": ctr.get("B", 0)}

    # Tight cuts to inspect:
    #   - delta^+(S1_non U interface) ... no, that includes interface arcs S1<->I
    #   - We focus on cuts that the gluing structure makes "interface-like":
    #     delta^+(S1_non) [bordering interface and possibly carrying S1->S2 bridges]
    #     delta^+(S1_non U I) [crossing the interface "outward"]
    #     delta^+(S2_non) [symmetric]
    #     delta^+(I) [the interface as outflow source]
    # These four cuts are not necessarily tight 3-cuts, but for any
    # 3-arc-strong gluing each has size >= 3.

    S1n = frozenset(range(0, interface_start))
    I = frozenset(range(interface_start, interface_end))
    S2n = frozenset(range(interface_end, inst.n))
    cuts_to_inspect = [
        ("delta+(S1_non)", S1n),
        ("delta+(S1_non U I)", S1n | I),
        ("delta+(S2_non)", S2n),
        ("delta+(I)", I),
        ("delta+(S1_non U S2_non)", S1n | S2n),  # = complement of I
    ]
    cut_summary = {}
    for name, X in cuts_to_inspect:
        cut_pairs = [(u, v) for (u, v, _) in keyed_arcs if u in X and v not in X]
        # find their colors
        in_R = 0
        in_B = 0
        for ke in keyed_arcs:
            u, v, _ = ke
            if u in X and v not in X:
                if color_of.get(ke) == "R":
                    in_R += 1
                elif color_of.get(ke) == "B":
                    in_B += 1
        cut_summary[name] = {"size": in_R + in_B, "R": in_R, "B": in_B}

    # All directed cuts of size 3 (tight 3-cuts): expensive in general,
    # but for n <= 14 manageable. Enumerate subsets X with 1 <= |X| <= n-1
    # whose out-cut has exactly 3 arcs, and tabulate color split.
    tight3 = []
    if inst.n <= 13:
        from itertools import combinations
        V = list(range(inst.n))
        for r in range(1, inst.n):
            for X_tup in combinations(V, r):
                X = frozenset(X_tup)
                size = 0
                for u, v, _ in keyed_arcs:
                    if u in X and v not in X:
                        size += 1
                        if size > 3:
                            break
                if size == 3:
                    # count colors
                    in_R = 0
                    in_B = 0
                    for ke in keyed_arcs:
                        u, v, _ = ke
                        if u in X and v not in X:
                            if color_of.get(ke) == "R":
                                in_R += 1
                            elif color_of.get(ke) == "B":
                                in_B += 1
                    tight3.append({"X_size": len(X), "R": in_R, "B": in_B})

    # Bridge color majority pattern
    b12_colors = Counter(c for _, c in bridges_1_to_2)
    b21_colors = Counter(c for _, c in bridges_2_to_1)

    return {
        "name": inst.name,
        "n": inst.n,
        "m": len(inst.arcs),
        "template1": inst.template1,
        "template2": inst.template2,
        "S1": list(inst.S1),
        "S2": list(inst.S2),
        "interface_labels": list(range(interface_start, interface_end)),
        "side1_non_labels": list(range(0, interface_start)),
        "side2_non_labels": list(range(interface_end, inst.n)),
        "status": "SAT",
        "color_counts": {
            "side1_internal": color_count(side1_arcs),
            "side2_internal": color_count(side2_arcs),
            "interface_internal": color_count(interface_internal_arcs),
            "side1_to_interface": color_count(side1_to_interface),
            "interface_to_side1": color_count(interface_to_side1),
            "side2_to_interface": color_count(side2_to_interface),
            "interface_to_side2": color_count(interface_to_side2),
            "bridges_S1_to_S2": color_count(bridges_1_to_2),
            "bridges_S2_to_S1": color_count(bridges_2_to_1),
        },
        "named_cuts": cut_summary,
        "tight3_cuts": tight3,
        "tight3_distribution": Counter(
            (tc["R"], tc["B"]) for tc in tight3
        ).most_common(),
        "n_tight3": len(tight3),
    }


# --------------------------------------------------------------------------- #
# Main                                                                         #
# --------------------------------------------------------------------------- #


def main():
    # Templates to look at on either side.
    bench = {b.name: b for b in all_benchmarks()}

    pair_classes = {
        "C1_C8sq_C8sq": ("C8_square", "C8_square"),
        "C2a_C6sq_L312": ("C6_square", "AiEtAl_L312_min"),
        "C2b_L211_L312": ("AiEtAl_L211_min", "AiEtAl_L312_min"),
        "C2c_L312_L312": ("AiEtAl_L312_min", "AiEtAl_L312_min"),
        "C3a_iv_iv": ("AiEtAl_iv_star_iv", "AiEtAl_iv_star_iv"),
        "C3b_L211_iv": ("AiEtAl_L211_min", "AiEtAl_iv_star_iv"),
        "C3c_C6sq_iv": ("C6_square", "AiEtAl_iv_star_iv"),
    }

    # Configure the generator to produce just a handful of candidates per pair.
    cfg = DeficitGenConfig(
        interface_sizes=(3, 4),
        max_interfaces_per_pair_per_size=30,
        max_bridges_per_interface=24,
        max_extra_slack_per_direction=1,
        allow_self_glue=True,
        ordered_pairs=True,
        require_arc_conn_exactly_3=True,
        verified_per_pair_cap=8,
        seed=20260516,
    )

    results = {}
    for class_label, (n1, n2) in pair_classes.items():
        if n1 not in bench or n2 not in bench:
            results[class_label] = {"error": "template missing", "pair": (n1, n2)}
            continue
        templates = [bench[n1]] if n1 == n2 else [bench[n1], bench[n2]]
        # We need generator to actually emit instances for (n1, n2); the
        # generator iterates pairs in `templates`, ordered_pairs=True yields
        # both orientations. Restrict to the one we want.
        rows = []
        t0 = time.time()
        for inst in generate_deficit_gluings(templates, cfg):
            if (inst.template1, inst.template2) != (n1, n2):
                continue
            row = analyse_instance(inst)
            if row is None:
                continue  # not arc-strong 3
            if row.get("status") != "SAT":
                continue
            rows.append(row)
            if len(rows) >= 8:
                break
            if time.time() - t0 > 90:
                break
        results[class_label] = {"pair": (n1, n2), "n_witnesses": len(rows), "rows": rows}
        print(f"[{class_label}] {n1} + {n2}: {len(rows)} witnesses collected in {time.time()-t0:.1f}s")

    out = Path(HERE) / "logs" / "phase4_lifting_probe.json"
    out.write_text(json.dumps(results, indent=2, default=str))
    print(f"\nWritten {out}")
    print(f"Total bytes: {out.stat().st_size}")

    # Print compact summaries.
    for class_label, payload in results.items():
        rows = payload.get("rows", [])
        if not rows:
            continue
        print(f"\n=== {class_label} ({payload['pair'][0]} + {payload['pair'][1]}): {len(rows)} witnesses ===")
        for r in rows:
            cc = r["color_counts"]
            b12 = cc["bridges_S1_to_S2"]
            b21 = cc["bridges_S2_to_S1"]
            ic = cc["interface_internal"]
            named = r["named_cuts"]
            tight = r["tight3_distribution"]
            print(
                f"  n={r['n']:2d} m={r['m']:3d} | "
                f"S1int R/B={cc['side1_internal']['R']}/{cc['side1_internal']['B']} "
                f"S2int R/B={cc['side2_internal']['R']}/{cc['side2_internal']['B']} "
                f"Iint R/B={ic['R']}/{ic['B']} "
                f"b12 R/B={b12['R']}/{b12['B']} "
                f"b21 R/B={b21['R']}/{b21['B']} | "
                f"d+(I) R/B={named['delta+(I)']['R']}/{named['delta+(I)']['B']} "
                f"d+(S1nUI) R/B={named['delta+(S1_non U I)']['R']}/{named['delta+(S1_non U I)']['B']} | "
                f"#3cuts={r['n_tight3']} dist={tight}"
            )


if __name__ == "__main__":
    main()
