"""Analyze the exact n=7 combinatorial LFO obstructions.

This is not another enumerator. It consumes `data/lfo_full_n7.json` and
extracts structural information about the instances with

    min FAS <= n - 1, but no linear-forest ordering.

The current target is modest and useful: understand whether the 18 exact
combinatorial NO instances collapse under duality, are vertex-minimal, and
which relaxation each one violates.
"""
from __future__ import annotations

import argparse
import itertools
import json
import os
import sys
from collections import Counter, defaultdict
from typing import Sequence

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lfo_score_bucket import analyze_lfo, order_perms, score_sequence  # noqa: E402
from structural import cyclic_3_cycles  # noqa: E402
from verify import verify  # noqa: E402


def full_canonical_key(T: Sequence[Sequence[int]]) -> tuple[int, ...]:
    """Canonical key under all vertex relabelings."""
    n = len(T)
    best = None
    for P in order_perms(n):
        key = tuple(T[P[i]][P[j]] for i in range(n) for j in range(n))
        if best is None or key < best:
            best = key
    assert best is not None
    return best


def dual(T: Sequence[Sequence[int]]) -> list[list[int]]:
    """Return the tournament obtained by reversing every arc."""
    n = len(T)
    return [[0 if i == j else int(T[j][i]) for j in range(n)] for i in range(n)]


def induced(T: Sequence[Sequence[int]], keep: Sequence[int]) -> list[list[int]]:
    return [[int(T[u][v]) for v in keep] for u in keep]


def automorphism_count(T: Sequence[Sequence[int]]) -> int:
    n = len(T)
    count = 0
    for P in order_perms(n):
        ok = True
        for i in range(n):
            for j in range(n):
                if T[i][j] != T[P[i]][P[j]]:
                    ok = False
                    break
            if not ok:
                break
        if ok:
            count += 1
    return count


def is_cyclic_triangle_on(T: Sequence[Sequence[int]], vertices: Sequence[int]) -> bool:
    a, b, c = vertices
    return (
        (T[a][b] and T[b][c] and T[c][a])
        or (T[a][c] and T[c][b] and T[b][a])
    )


def double_triangle_hubs(T: Sequence[Sequence[int]]) -> list[int]:
    n = len(T)
    hubs: list[int] = []
    for v in range(n):
        out = [u for u in range(n) if T[v][u]]
        inn = [u for u in range(n) if T[u][v]]
        if len(out) == 3 and len(inn) == 3:
            if is_cyclic_triangle_on(T, out) and is_cyclic_triangle_on(T, inn):
                hubs.append(v)
    return hubs


def arc_loads(T: Sequence[Sequence[int]]) -> dict:
    loads: Counter[tuple[int, int]] = Counter()
    for cyc in cyclic_3_cycles(T):
        for arc in cyc:
            loads[arc] += 1
    values = list(loads.values())
    return {
        "max": max(values) if values else 0,
        "hist": dict(sorted(Counter(values).items())),
    }


def ordering_stats(T: Sequence[Sequence[int]]) -> dict:
    min_fas = None
    min_fas_orders = 0
    degree2_orders = 0
    forest_orders = 0
    exact_path_orders = 0
    by_relaxation: Counter[str] = Counter()

    for P in order_perms(len(T)):
        info = verify(T, list(P))
        count = info["count"]
        if min_fas is None or count < min_fas:
            min_fas = count
            min_fas_orders = 1
        elif count == min_fas:
            min_fas_orders += 1

        if info["max_degree"] <= 2:
            degree2_orders += 1
        if info["is_forest"]:
            forest_orders += 1
        if info["is_path"]:
            exact_path_orders += 1

        if info["max_degree"] <= 2 and info["is_forest"]:
            by_relaxation["lfo"] += 1
        elif info["max_degree"] <= 2:
            by_relaxation["degree2_only"] += 1
        elif info["is_forest"]:
            by_relaxation["forest_only"] += 1
        else:
            by_relaxation["neither"] += 1

    return {
        "min_fas": min_fas,
        "min_fas_order_count": min_fas_orders,
        "degree2_order_count": degree2_orders,
        "forest_order_count": forest_orders,
        "exact_path_order_count": exact_path_orders,
        "order_relaxation_hist": dict(sorted(by_relaxation.items())),
    }


def relaxation_type(record: dict) -> str:
    d2 = record["has_degree2_relaxation"]
    forest = record["has_forest_ordering"]
    if d2 and forest:
        return "coupling"
    if d2 and not forest:
        return "cycle_obstruction"
    if forest and not d2:
        return "degree_obstruction"
    return "both_relaxations_fail"


def summarize_deletions(T: Sequence[Sequence[int]]) -> dict:
    rows = []
    all_lfo_yes = True
    for v in range(len(T)):
        keep = [u for u in range(len(T)) if u != v]
        Tv = induced(T, keep)
        info = analyze_lfo(Tv)
        rows.append({
            "deleted_vertex": v,
            "score_sequence": list(score_sequence(Tv)),
            "has_lfo": info["has_lfo"],
            "min_fas": info["min_fas"],
        })
        all_lfo_yes = all_lfo_yes and info["has_lfo"]
    return {"all_vertex_deletions_lfo_yes": all_lfo_yes, "rows": rows}


def load_records(path: str) -> list[dict]:
    with open(path) as f:
        data = json.load(f)
    records = []
    for bucket in data["buckets"]:
        for record in bucket["records"]:
            rec = dict(record)
            rec["record_id"] = (
                f"{tuple(record['score_sequence'])}#{record['iso_index']}"
            )
            records.append(rec)
    return records


def main() -> None:
    here = os.path.dirname(os.path.abspath(__file__))
    default_in = os.path.join(here, "..", "data", "lfo_full_n7.json")
    default_out = os.path.join(here, "..", "data", "lfo_combinatorial_no_analysis.json")

    p = argparse.ArgumentParser()
    p.add_argument("--input", default=default_in)
    p.add_argument("--out", default=default_out)
    args = p.parse_args()

    all_records = load_records(args.input)
    no_records = [
        r for r in all_records
        if not r["has_lfo"] and r["no_kind"] == "combinatorial"
    ]

    key_to_id = {}
    for r in all_records:
        key_to_id[full_canonical_key(r["T"])] = r["record_id"]

    orbit_keys = {}
    details = []
    for idx, r in enumerate(no_records):
        T = r["T"]
        key = full_canonical_key(T)
        dT = dual(T)
        dkey = full_canonical_key(dT)
        orbit_key = min(key, dkey)
        if orbit_key not in orbit_keys:
            orbit_keys[orbit_key] = f"D{len(orbit_keys)}"

        deletion = summarize_deletions(T)
        row = {
            "no_id": idx,
            "record_id": r["record_id"],
            "dual_record_id": key_to_id.get(dkey),
            "dual_orbit_id": orbit_keys[orbit_key],
            "self_dual": key == dkey,
            "score_sequence": r["score_sequence"],
            "relaxation_type": relaxation_type(r),
            "min_fas": r["min_fas"],
            "has_degree2_relaxation": r["has_degree2_relaxation"],
            "has_forest_ordering": r["has_forest_ordering"],
            "has_matching_fas": r["has_matching_fas"],
            "has_exact_path_backarcs": r["has_exact_path_backarcs"],
            "cyclic_3cycles": len(cyclic_3_cycles(T)),
            "double_triangle_hubs": double_triangle_hubs(T),
            "arc_cyclic_triangle_loads": arc_loads(T),
            "automorphism_count": automorphism_count(T),
            "vertex_deletion": deletion,
            "ordering_stats": ordering_stats(T),
        }
        details.append(row)

    dual_orbits: defaultdict[str, list[str]] = defaultdict(list)
    for row in details:
        dual_orbits[row["dual_orbit_id"]].append(row["record_id"])

    summary = {
        "input": os.path.relpath(args.input, os.path.join(here, "..")),
        "n": 7,
        "combinatorial_no_count": len(details),
        "dual_orbit_count": len(dual_orbits),
        "self_dual_count": sum(1 for row in details if row["self_dual"]),
        "all_vertex_minimal": all(
            row["vertex_deletion"]["all_vertex_deletions_lfo_yes"]
            for row in details
        ),
        "relaxation_type_hist": dict(sorted(Counter(
            row["relaxation_type"] for row in details
        ).items())),
        "score_sequence_hist": dict(sorted(Counter(
            str(tuple(row["score_sequence"])) for row in details
        ).items())),
        "cyclic_3cycle_hist": dict(sorted(Counter(
            row["cyclic_3cycles"] for row in details
        ).items())),
        "automorphism_count_hist": dict(sorted(Counter(
            row["automorphism_count"] for row in details
        ).items())),
        "double_triangle_hub_count_hist": dict(sorted(Counter(
            len(row["double_triangle_hubs"]) for row in details
        ).items())),
        "dual_orbits": dict(sorted((k, sorted(v)) for k, v in dual_orbits.items())),
    }

    out = {"summary": summary, "records": details}
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w") as f:
        json.dump(out, f, indent=2)
    print(json.dumps(summary, indent=2))
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
