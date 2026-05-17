"""Phase 4 branching-witness extractor (route R2).

For each SAT witness produced by `phase4_witness_probe.py`, extract an
explicit out-branching T^+_c and in-branching T^-_c of (V, A_c) for each
color c in {R, B}, rooted at a common vertex r_c.  Test the structural
prediction made in `team/08_phase4_lifting_lemma_v1.md` Step 3.b route R2:

  "The per-color out-branching of D decomposes as: an inner out-branching
   of D[V_i] rooted at an interface vertex s, extended by a single bridge
   T_i -> T_{3-i} to a vertex u in V_{3-i}, plus an inner out-branching of
   D[V_{3-i}] rooted at u."

We re-derive the witnesses by re-running the SAT verifier (the JSON probe
file does not persist raw arc-by-arc coloring), then for each color:

  * pick a root r in the interface I (the shared vertices);
  * compute a BFS out-arborescence T^+ of (V, A_c) from r;
  * compute a BFS in-arborescence T^- of (V, A_c) into r;
  * classify each arc of T^+ as side1-internal, side2-internal,
    interface-internal, S<->I, or bridge S1<->S2;
  * verify the predicted single-bridge decomposition.

Output:
  logs/phase4_branching_extract.json   — per-witness data
  stdout                                — summary table
"""

from __future__ import annotations

import json
import sys
import time
from collections import Counter, defaultdict, deque
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from benchmarks import all_benchmarks  # noqa: E402
from generators.glue_deficit import (  # noqa: E402
    DeficitGenConfig,
    generate_deficit_gluings,
    passes_arc_strong_3,
)
from verifier_sat import verify_sat  # noqa: E402


# ----------------------------------------------------------------------------
# Branching extraction
# ----------------------------------------------------------------------------


def out_branching_from(root: int, n: int, arcs: list[tuple[int, int, int]]):
    """BFS out-arborescence rooted at `root` over the subdigraph induced by
    `arcs` on vertex set range(n).  Returns a list of arc-keys (n-1 of them)
    if a spanning out-branching exists, else None.

    Arcs are 3-tuples (u, v, k); we treat parallel arcs as distinct candidates
    but only need one of each parent->child pair.
    """
    out_adj: dict[int, list[tuple[int, int, int]]] = defaultdict(list)
    for ke in arcs:
        u, v, _ = ke
        out_adj[u].append(ke)
    parent: dict[int, tuple[int, int, int]] = {}
    seen = {root}
    q = deque([root])
    while q:
        u = q.popleft()
        for ke in out_adj[u]:
            _, v, _ = ke
            if v in seen:
                continue
            parent[v] = ke
            seen.add(v)
            q.append(v)
    if len(seen) != n:
        return None
    return [parent[v] for v in range(n) if v != root]


def in_branching_into(root: int, n: int, arcs: list[tuple[int, int, int]]):
    """BFS in-arborescence into `root`: every non-root vertex has a directed
    path *to* root in the tree. Equivalently: out-arborescence rooted at root
    in the reverse digraph."""
    in_adj: dict[int, list[tuple[int, int, int]]] = defaultdict(list)
    for ke in arcs:
        u, v, _ = ke
        in_adj[v].append(ke)  # arcs pointing INTO v
    # We do a reverse BFS: at each step we walk arcs backwards.
    parent: dict[int, tuple[int, int, int]] = {}
    seen = {root}
    q = deque([root])
    while q:
        v = q.popleft()
        for ke in in_adj[v]:
            u, _, _ = ke
            if u in seen:
                continue
            parent[u] = ke
            seen.add(u)
            q.append(u)
    if len(seen) != n:
        return None
    return [parent[u] for u in range(n) if u != root]


def classify_arc(ke, interface_start, interface_end):
    """Return one of S1_int, S2_int, I_int, S1_to_I, I_to_S1, S2_to_I,
    I_to_S2, b12 (S1->S2), b21 (S2->S1)."""
    u, v, _ = ke

    def side(x):
        if x < interface_start:
            return "S1"
        if x < interface_end:
            return "I"
        return "S2"

    su, sv = side(u), side(v)
    if (su, sv) == ("S1", "S1"):
        return "S1_int"
    if (su, sv) == ("S2", "S2"):
        return "S2_int"
    if (su, sv) == ("I", "I"):
        return "I_int"
    if (su, sv) == ("S1", "I"):
        return "S1_to_I"
    if (su, sv) == ("I", "S1"):
        return "I_to_S1"
    if (su, sv) == ("S2", "I"):
        return "S2_to_I"
    if (su, sv) == ("I", "S2"):
        return "I_to_S2"
    if (su, sv) == ("S1", "S2"):
        return "b12"
    if (su, sv) == ("S2", "S1"):
        return "b21"
    return f"{su}_to_{sv}"


# ----------------------------------------------------------------------------
# Per-witness analysis
# ----------------------------------------------------------------------------


def analyse_witness(inst):
    """Re-run SAT, extract branchings, classify their arcs by region."""
    D = inst.build()
    if not passes_arc_strong_3(D, exact=True):
        return None
    res = verify_sat(D, time_limit_s=30.0)
    if res["status"] != "SAT":
        return {"name": inst.name, "status": res["status"]}

    red, blue = res["witness"]  # each is a list of (u, v, k) keys
    red_set = set(red)
    blue_set = set(blue)

    bench = {b.name: b for b in all_benchmarks()}
    T1 = bench[inst.template1]
    s = len(inst.S1)
    n_non1 = T1.n - s
    interface_start = n_non1
    interface_end = n_non1 + s

    # Reconstruct keyed arcs in insertion order.
    parallel_ctr: Counter = Counter()
    keyed_arcs: list[tuple[int, int, int]] = []
    for u, v in inst.arcs:
        k = parallel_ctr[(u, v)]
        keyed_arcs.append((u, v, k))
        parallel_ctr[(u, v)] += 1

    color_of = {}
    for ke in keyed_arcs:
        if ke in red_set:
            color_of[ke] = "R"
        elif ke in blue_set:
            color_of[ke] = "B"

    interface = list(range(interface_start, interface_end))

    # Per color: try each interface vertex as candidate root, pick the first
    # which admits BOTH an out-branching and an in-branching in A_c.
    per_color = {}
    for color in ("R", "B"):
        A_c = [ke for ke in keyed_arcs if color_of.get(ke) == color]
        found = None
        for r in interface + list(range(inst.n)):  # interface first
            out_tree = out_branching_from(r, inst.n, A_c)
            if out_tree is None:
                continue
            in_tree = in_branching_into(r, inst.n, A_c)
            if in_tree is None:
                continue
            found = (r, out_tree, in_tree)
            break
        if found is None:
            # Strong-connectivity of A_c must guarantee both; flag as bug.
            per_color[color] = {"error": "no_common_root_found"}
            continue

        r, out_tree, in_tree = found

        # Classify the arcs of each tree by region.
        out_class = Counter(classify_arc(ke, interface_start, interface_end) for ke in out_tree)
        in_class = Counter(classify_arc(ke, interface_start, interface_end) for ke in in_tree)

        # Test the "single-bridge stitch" prediction:
        #   the out-branching uses exactly one b12 + exactly one b21 (since
        #   the root sits in I, you may need 0 if both V_i are reached purely
        #   through I); more generally, count bridge arcs in T^+.
        out_b12 = out_class.get("b12", 0)
        out_b21 = out_class.get("b21", 0)
        in_b12 = in_class.get("b12", 0)
        in_b21 = in_class.get("b21", 0)

        # Check "inner sub-branchings" structure:
        #   restrict T^+ to side1-internal-or-interface arcs and check it
        #   contains a spanning sub-tree of S1 ∪ I rooted at some vertex.
        # We just record the structure: in T^+ rooted at r in I, the
        # restriction to arcs with both endpoints in V_1 ∪ I and the
        # restriction to V_2 ∪ I should be inner branchings, joined by the
        # bridge arcs from I/S1 to S2 (or via I).
        per_color[color] = {
            "root": r,
            "out_tree_size": len(out_tree),
            "in_tree_size": len(in_tree),
            "out_class": dict(out_class),
            "in_class": dict(in_class),
            "out_b12": out_b12,
            "out_b21": out_b21,
            "in_b12": in_b12,
            "in_b21": in_b21,
        }

    # Bridge color totals.
    b12_color = Counter()
    b21_color = Counter()
    for ke in keyed_arcs:
        cls = classify_arc(ke, interface_start, interface_end)
        c = color_of.get(ke, "?")
        if cls == "b12":
            b12_color[c] += 1
        elif cls == "b21":
            b21_color[c] += 1

    return {
        "name": inst.name,
        "n": inst.n,
        "m": len(inst.arcs),
        "template1": inst.template1,
        "template2": inst.template2,
        "interface": interface,
        "side1_non": list(range(0, interface_start)),
        "side2_non": list(range(interface_end, inst.n)),
        "b12_color": dict(b12_color),
        "b21_color": dict(b21_color),
        "per_color": per_color,
    }


# ----------------------------------------------------------------------------
# Main: regenerate the 56 witnesses, extract branchings, summarise
# ----------------------------------------------------------------------------


def main():
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
    rollup = {
        "n_witnesses": 0,
        "with_both_branchings_R": 0,
        "with_both_branchings_B": 0,
        "out_branch_uses_one_b12_one_b21": Counter(),
        "in_branch_uses_one_b12_one_b21": Counter(),
        "bridge_color_summary": Counter(),
    }
    for class_label, (n1, n2) in pair_classes.items():
        if n1 not in bench or n2 not in bench:
            continue
        templates = [bench[n1]] if n1 == n2 else [bench[n1], bench[n2]]
        rows = []
        t0 = time.time()
        for inst in generate_deficit_gluings(templates, cfg):
            if (inst.template1, inst.template2) != (n1, n2):
                continue
            row = analyse_witness(inst)
            if row is None:
                continue
            if "per_color" not in row:
                continue
            rows.append(row)
            rollup["n_witnesses"] += 1
            for color in ("R", "B"):
                pc = row["per_color"].get(color, {})
                if "root" in pc:
                    rollup[f"with_both_branchings_{color}"] += 1
                    rollup["out_branch_uses_one_b12_one_b21"][
                        (color, pc["out_b12"], pc["out_b21"])
                    ] += 1
                    rollup["in_branch_uses_one_b12_one_b21"][
                        (color, pc["in_b12"], pc["in_b21"])
                    ] += 1
            rollup["bridge_color_summary"][
                (row["b12_color"].get("R", 0), row["b12_color"].get("B", 0),
                 row["b21_color"].get("R", 0), row["b21_color"].get("B", 0))
            ] += 1
            if len(rows) >= 8:
                break
            if time.time() - t0 > 120:
                break
        results[class_label] = {"pair": (n1, n2), "n_witnesses": len(rows), "rows": rows}
        print(f"[{class_label}] {n1} + {n2}: {len(rows)} witnesses in {time.time()-t0:.1f}s")

    # Compact rollup print.
    print("\n=========== ROLLUP ===========")
    print(f"Total witnesses: {rollup['n_witnesses']}")
    print(f"With both T^+ and T^- in R: {rollup['with_both_branchings_R']}")
    print(f"With both T^+ and T^- in B: {rollup['with_both_branchings_B']}")
    print("\nOut-branching (color, #b12 used, #b21 used) -> count:")
    for k, v in sorted(rollup["out_branch_uses_one_b12_one_b21"].items()):
        print(f"  {k} -> {v}")
    print("\nIn-branching (color, #b12 used, #b21 used) -> count:")
    for k, v in sorted(rollup["in_branch_uses_one_b12_one_b21"].items()):
        print(f"  {k} -> {v}")
    print("\nBridge color summary (b12_R, b12_B, b21_R, b21_B) -> count:")
    for k, v in sorted(rollup["bridge_color_summary"].items()):
        print(f"  {k} -> {v}")

    # Detail per class: bridges used by trees.
    print("\n=========== PER-CLASS DETAIL ===========")
    for class_label, payload in results.items():
        print(f"\n--- {class_label} ({payload['pair'][0]} + {payload['pair'][1]}) ---")
        for r in payload["rows"]:
            iface = r["interface"]
            line = (
                f"  n={r['n']:2d} iface={iface} b12={r['b12_color']} b21={r['b21_color']} | "
            )
            for color in ("R", "B"):
                pc = r["per_color"].get(color, {})
                if "root" not in pc:
                    line += f"{color}:ERR "
                    continue
                line += (
                    f"{color}: root={pc['root']} "
                    f"T+ b12={pc['out_b12']} b21={pc['out_b21']} "
                    f"T- b12={pc['in_b12']} b21={pc['in_b21']}  "
                )
            print(line)

    out_path = Path(HERE) / "logs" / "phase4_branching_extract.json"
    # Convert Counter-with-tuple-keys to JSON-friendly form.
    json_rollup = {
        "n_witnesses": rollup["n_witnesses"],
        "with_both_branchings_R": rollup["with_both_branchings_R"],
        "with_both_branchings_B": rollup["with_both_branchings_B"],
        "out_branch_bridge_counts": {
            f"{c},{b12},{b21}": cnt
            for (c, b12, b21), cnt in rollup["out_branch_uses_one_b12_one_b21"].items()
        },
        "in_branch_bridge_counts": {
            f"{c},{b12},{b21}": cnt
            for (c, b12, b21), cnt in rollup["in_branch_uses_one_b12_one_b21"].items()
        },
        "bridge_color_summary": {
            f"b12_R={k[0]},b12_B={k[1]},b21_R={k[2]},b21_B={k[3]}": v
            for k, v in rollup["bridge_color_summary"].items()
        },
    }
    out_path.write_text(json.dumps({"rollup": json_rollup, "by_class": results}, indent=2, default=str))
    print(f"\nWritten {out_path}")


if __name__ == "__main__":
    main()
