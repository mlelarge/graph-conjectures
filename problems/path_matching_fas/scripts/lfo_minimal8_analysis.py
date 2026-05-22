"""Structural analysis of exact order-8 minimal LFO obstructions.

Input is `data/lfo_extend_census_n8.json`. We select exactly the NO
instances that contain no induced order-7 NO subtournament. Since LFO is
hereditary, these are the order-8 minimal forbidden induced subtournaments.

The output intentionally stores compressed invariants rather than full
tournament matrices; the source census already stores the matrices.
"""
from __future__ import annotations

import argparse
import itertools
import json
import os
import sys
import time
from collections import Counter, defaultdict
from typing import Sequence

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lfo_obstruction_analysis import arc_loads, dual  # noqa: E402
from lfo_score_bucket import (  # noqa: E402
    canonical_key_with_scores,
    order_perms,
    score_vector,
)
from structural import cyclic_3_cycles  # noqa: E402
from verify import verify  # noqa: E402


def is_module(T: Sequence[Sequence[int]], subset: set[int]) -> bool:
    n = len(T)
    for w in range(n):
        if w in subset:
            continue
        vals = [T[w][x] for x in subset]
        if not (all(vals) or not any(vals)):
            return False
    return True


def module_stats(T: Sequence[Sequence[int]]) -> dict:
    n = len(T)
    modules: list[frozenset[int]] = []
    for r in range(2, n):
        for subset in itertools.combinations(range(n), r):
            S = set(subset)
            if is_module(T, S):
                modules.append(frozenset(S))

    strong = []
    for M in modules:
        ok = True
        for N in modules:
            if M == N:
                continue
            if M & N and not (M <= N or N <= M):
                ok = False
                break
        if ok:
            strong.append(M)

    return {
        "nontrivial_module_count": len(modules),
        "proper_strong_module_count": len(strong),
        "is_prime": len(modules) == 0,
        "module_size_hist": dict(sorted(Counter(len(M) for M in modules).items())),
        "strong_module_size_hist": dict(sorted(Counter(len(M) for M in strong).items())),
        "max_module_size": max((len(M) for M in modules), default=0),
    }


def has_cyclic_triangle_on(T: Sequence[Sequence[int]], vertices: Sequence[int]) -> bool:
    for a, b, c in itertools.combinations(vertices, 3):
        if (T[a][b] and T[b][c] and T[c][a]) or (T[a][c] and T[c][b] and T[b][a]):
            return True
    return False


def local_cyclic_neighborhood_stats(T: Sequence[Sequence[int]]) -> dict:
    both = []
    out_only = []
    in_only = []
    for v in range(len(T)):
        out = [u for u in range(len(T)) if T[v][u]]
        inn = [u for u in range(len(T)) if T[u][v]]
        out_cyc = has_cyclic_triangle_on(T, out)
        in_cyc = has_cyclic_triangle_on(T, inn)
        if out_cyc and in_cyc:
            both.append(v)
        elif out_cyc:
            out_only.append(v)
        elif in_cyc:
            in_only.append(v)
    return {
        "both_cyclic_neighborhood_vertices": both,
        "out_cyclic_only_vertices": out_only,
        "in_cyclic_only_vertices": in_only,
    }


def automorphism_count(T: Sequence[Sequence[int]]) -> int:
    groups: dict[int, list[int]] = defaultdict(list)
    for v, s in enumerate(score_vector(T)):
        groups[s].append(v)

    blocks = [groups[s] for s in sorted(groups)]
    count = 0
    for choices in itertools.product(*(itertools.permutations(block) for block in blocks)):
        image = list(range(len(T)))
        for domain_block, image_block in zip(blocks, choices):
            for u, v in zip(domain_block, image_block):
                image[u] = v

        ok = True
        for u in range(len(T)):
            for v in range(len(T)):
                if T[u][v] != T[image[u]][image[v]]:
                    ok = False
                    break
            if not ok:
                break
        if ok:
            count += 1
    return count


def relaxation_type(has_degree2: bool, has_forest: bool) -> str:
    if has_degree2 and has_forest:
        return "coupling"
    if has_degree2:
        return "cycle_obstruction"
    if has_forest:
        return "degree_obstruction"
    return "both_relaxations_fail"


def ordering_stats(T: Sequence[Sequence[int]]) -> dict:
    min_fas = None
    min_fas_order_count = 0
    degree2_order_count = 0
    forest_order_count = 0
    matching_order_count = 0
    exact_path_order_count = 0
    order_relaxation_hist: Counter[str] = Counter()

    for P in order_perms(len(T)):
        info = verify(T, list(P))
        count = info["count"]
        if min_fas is None or count < min_fas:
            min_fas = count
            min_fas_order_count = 1
        elif count == min_fas:
            min_fas_order_count += 1

        has_degree2 = info["max_degree"] <= 2
        has_forest = info["is_forest"]
        if has_degree2:
            degree2_order_count += 1
        if has_forest:
            forest_order_count += 1
        if info["is_matching"]:
            matching_order_count += 1
        if info["is_path"]:
            exact_path_order_count += 1
        order_relaxation_hist[relaxation_type(has_degree2, has_forest)] += 1

    return {
        "min_fas": min_fas,
        "min_fas_order_count": min_fas_order_count,
        "has_degree2_relaxation": degree2_order_count > 0,
        "has_forest_ordering": forest_order_count > 0,
        "has_matching_fas": matching_order_count > 0,
        "has_exact_path_backarcs": exact_path_order_count > 0,
        "degree2_order_count": degree2_order_count,
        "forest_order_count": forest_order_count,
        "matching_order_count": matching_order_count,
        "exact_path_order_count": exact_path_order_count,
        "relaxation_type": relaxation_type(
            degree2_order_count > 0,
            forest_order_count > 0,
        ),
        "order_relaxation_hist": dict(sorted(order_relaxation_hist.items())),
    }


def load_minimal_records(path: str) -> list[dict]:
    with open(path) as f:
        data = json.load(f)
    return [r for r in data["no_records"] if not r["contains_order7_no"]]


def main() -> None:
    here = os.path.dirname(os.path.abspath(__file__))
    default_input = os.path.join(here, "..", "data", "lfo_extend_census_n8.json")
    default_out = os.path.join(here, "..", "data", "lfo_minimal8_analysis.json")

    p = argparse.ArgumentParser()
    p.add_argument("--input", default=default_input)
    p.add_argument("--out", default=default_out)
    p.add_argument("--progress", type=int, default=25)
    args = p.parse_args()

    t0 = time.time()
    records = load_minimal_records(args.input)
    key_to_id = {
        canonical_key_with_scores(r["T"]): f"8#{r['iso_index']}"
        for r in records
    }

    orbit_keys: dict[tuple[int, ...], str] = {}
    details = []
    for i, r in enumerate(records, start=1):
        T = r["T"]
        key = canonical_key_with_scores(T)
        dkey = canonical_key_with_scores(dual(T))
        orbit_key = min(key, dkey)
        if orbit_key not in orbit_keys:
            orbit_keys[orbit_key] = f"D{len(orbit_keys)}"

        order_info = ordering_stats(T)
        modules = module_stats(T)
        cycles = cyclic_3_cycles(T)
        local = local_cyclic_neighborhood_stats(T)
        row = {
            "record_id": f"8#{r['iso_index']}",
            "iso_index": r["iso_index"],
            "dual_record_id": key_to_id.get(dkey),
            "dual_orbit_id": orbit_keys[orbit_key],
            "self_dual": key == dkey,
            "score_sequence": r["score_sequence"],
            "no_kind": r["no_kind"],
            "contains_order7_no": r["contains_order7_no"],
            "cyclic_3cycles": len(cycles),
            "arc_cyclic_triangle_loads": arc_loads(T),
            "automorphism_count": automorphism_count(T),
            "module_stats": modules,
            "local_cyclic_neighborhood_stats": local,
            "ordering_stats": order_info,
        }
        details.append(row)

        if args.progress and i % args.progress == 0:
            print(f"analyzed {i}/{len(records)} "
                  f"({round(time.time() - t0, 1)}s)", flush=True)

    dual_orbits: defaultdict[str, list[str]] = defaultdict(list)
    for row in details:
        dual_orbits[row["dual_orbit_id"]].append(row["record_id"])

    summary = {
        "input": os.path.relpath(args.input, os.path.join(here, "..")),
        "n": 8,
        "minimal_no_count": len(details),
        "seconds": round(time.time() - t0, 2),
        "dual_orbit_count": len(dual_orbits),
        "self_dual_count": sum(1 for row in details if row["self_dual"]),
        "missing_dual_count": sum(1 for row in details if row["dual_record_id"] is None),
        "no_kind_hist": dict(sorted(Counter(row["no_kind"] for row in details).items())),
        "relaxation_type_hist": dict(sorted(Counter(
            row["ordering_stats"]["relaxation_type"] for row in details
        ).items())),
        "score_sequence_hist": dict(sorted(Counter(
            str(tuple(row["score_sequence"])) for row in details
        ).items())),
        "min_fas_hist": dict(sorted(Counter(
            row["ordering_stats"]["min_fas"] for row in details
        ).items())),
        "cyclic_3cycle_hist": dict(sorted(Counter(
            row["cyclic_3cycles"] for row in details
        ).items())),
        "automorphism_count_hist": dict(sorted(Counter(
            row["automorphism_count"] for row in details
        ).items())),
        "module_count_hist": dict(sorted(Counter(
            row["module_stats"]["nontrivial_module_count"] for row in details
        ).items())),
        "prime_count": sum(1 for row in details if row["module_stats"]["is_prime"]),
        "both_cyclic_neighborhood_vertex_count_hist": dict(sorted(Counter(
            len(row["local_cyclic_neighborhood_stats"]["both_cyclic_neighborhood_vertices"])
            for row in details
        ).items())),
        "dual_orbit_size_hist": dict(sorted(Counter(
            len(v) for v in dual_orbits.values()
        ).items())),
    }

    out = {"summary": summary, "records": details}
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w") as f:
        json.dump(out, f, indent=2)
    print(json.dumps(summary, indent=2))
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
