"""Compact summary of exact order-9 minimal LFO obstructions.

The full n=9 census already classifies every representative. This script
only summarizes the minimal NO rows: those with no induced order-8 NO.
It avoids expensive 9! relaxation scans.
"""
from __future__ import annotations

import itertools
import json
import os
import sys
import time
from collections import Counter, defaultdict
from typing import Sequence

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from structural import cyclic_3_cycles  # noqa: E402
from tournament_canonical import canonical_key, key_to_string, string_to_matrix  # noqa: E402


def dual(T: Sequence[Sequence[int]]) -> list[list[int]]:
    n = len(T)
    return [[0 if i == j else int(T[j][i]) for j in range(n)] for i in range(n)]


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
    modules = []
    for r in range(2, n):
        for subset in itertools.combinations(range(n), r):
            S = set(subset)
            if is_module(T, S):
                modules.append(frozenset(S))
    return {
        "nontrivial_module_count": len(modules),
        "is_prime": len(modules) == 0,
        "module_size_hist": dict(sorted(Counter(len(M) for M in modules).items())),
        "max_module_size": max((len(M) for M in modules), default=0),
    }


def has_cyclic_triangle_on(T: Sequence[Sequence[int]], vertices: Sequence[int]) -> bool:
    for a, b, c in itertools.combinations(vertices, 3):
        if (T[a][b] and T[b][c] and T[c][a]) or (T[a][c] and T[c][b] and T[b][a]):
            return True
    return False


def both_cyclic_neighborhood_count(T: Sequence[Sequence[int]]) -> int:
    count = 0
    for v in range(len(T)):
        out = [u for u in range(len(T)) if T[v][u]]
        inn = [u for u in range(len(T)) if T[u][v]]
        if has_cyclic_triangle_on(T, out) and has_cyclic_triangle_on(T, inn):
            count += 1
    return count


def load_keys(path: str) -> list[str]:
    keys = []
    with open(path) as f:
        for line in f:
            if line.strip():
                keys.append(json.loads(line)["key"])
    return keys


def load_minimal_rows(path: str) -> list[dict]:
    rows = []
    with open(path) as f:
        for line in f:
            if not line.strip():
                continue
            r = json.loads(line)
            if not r["has_lfo"] and not r["contains_lower_no"]:
                rows.append(r)
    return rows


def main() -> None:
    here = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.abspath(os.path.join(here, "..", "data"))
    reps_path = os.path.join(data_dir, "lfo_reps_n9.jsonl")
    census_path = os.path.join(data_dir, "lfo_census_n9_results.jsonl")
    out_path = os.path.join(data_dir, "lfo_minimal9_summary.json")

    t0 = time.time()
    keys = load_keys(reps_path)
    rows = load_minimal_rows(census_path)
    key_by_index = {i: key for i, key in enumerate(keys)}
    all_keys = set(keys)

    orbit_keys = set()
    self_dual = 0
    missing_dual = 0
    module_counter: Counter[int] = Counter()
    prime_count = 0
    module_size_counter: Counter[str] = Counter()
    cyclic_counter: Counter[int] = Counter()
    both_neighborhood_counter: Counter[int] = Counter()

    for row in rows:
        key = key_by_index[row["iso_index"]]
        T = string_to_matrix(key)
        dkey = key_to_string(canonical_key(dual(T)))
        orbit_keys.add(min(key, dkey))
        if dkey == key:
            self_dual += 1
        if dkey not in all_keys:
            missing_dual += 1

        ms = module_stats(T)
        module_counter[ms["nontrivial_module_count"]] += 1
        prime_count += int(ms["is_prime"])
        module_size_counter[str(ms["module_size_hist"])] += 1
        cyclic_counter[len(cyclic_3_cycles(T))] += 1
        both_neighborhood_counter[both_cyclic_neighborhood_count(T)] += 1

    summary = {
        "n": 9,
        "minimal_no_count": len(rows),
        "seconds": round(time.time() - t0, 2),
        "dual_orbit_count": len(orbit_keys),
        "self_dual_count": self_dual,
        "missing_dual_count": missing_dual,
        "no_kind_hist": dict(sorted(Counter(r["no_kind"] for r in rows).items())),
        "min_fas_hist": dict(sorted(Counter(r["min_fas"] for r in rows).items())),
        "score_sequence_hist_top20": [
            [list(seq), count]
            for seq, count in Counter(tuple(r["score_sequence"]) for r in rows).most_common(20)
        ],
        "cyclic_3cycle_hist": dict(sorted(cyclic_counter.items())),
        "module_count_hist": dict(sorted(module_counter.items())),
        "prime_count": prime_count,
        "module_size_hist_hist": dict(sorted(module_size_counter.items())),
        "both_cyclic_neighborhood_vertex_count_hist": dict(sorted(both_neighborhood_counter.items())),
    }
    with open(out_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(json.dumps(summary, indent=2))
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
