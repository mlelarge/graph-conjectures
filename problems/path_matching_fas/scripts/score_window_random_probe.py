"""Random and skew-score probes for the score-window solver.

This script is deliberately empirical. It answers two questions:

1. How does the score-window solver behave on labeled random
   tournaments beyond the exact n<=9 census range?
2. Does the forced/flexible decomposition become active on skew-score
   tournaments where score windows are less overlapped?
"""
from __future__ import annotations

import argparse
import json
import os
import random
import statistics
import sys
import time
from collections import defaultdict
from typing import Callable, Sequence

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lfo_score_window import find_lfo_order_score_window, indegrees  # noqa: E402
from lfo_forced_flexible import find_lfo_order_forced_flexible  # noqa: E402
from score_window_forced import forced_flexible_decomposition, forced_obstruction  # noqa: E402
from score_window_growth import regress_growth, summarize  # noqa: E402
from verify import verify  # noqa: E402


Matrix = Sequence[Sequence[int]]


def random_tournament(n: int, rng: random.Random) -> list[list[int]]:
    T = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            if rng.getrandbits(1):
                T[i][j] = 1
            else:
                T[j][i] = 1
    return T


def transitive_noise_tournament(n: int, p: float, rng: random.Random) -> list[list[int]]:
    """Start from a transitive tournament and reverse each pair with prob p."""
    T = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            if rng.random() < p:
                T[j][i] = 1
            else:
                T[i][j] = 1
    return T


def score_profile(T: Matrix) -> dict:
    ds = indegrees(T)
    return {
        "score_span": max(ds) - min(ds) if ds else 0,
        "distinct_scores": len(set(ds)),
        "score_sequence": sorted(ds),
    }


def summarize_bool(values: list[bool]) -> dict:
    return {
        "count": len(values),
        "true": sum(values),
        "false": len(values) - sum(values),
    }


def summarize_categories(values: list[str | None]) -> dict:
    out: dict[str, int] = {}
    for value in values:
        key = "none" if value is None else value
        out[key] = out.get(key, 0) + 1
    return dict(sorted(out.items()))


def analyze_sample(T: Matrix, compare_forced_flexible: bool = False) -> dict:
    solver = find_lfo_order_score_window(T)
    if solver["found"]:
        cert = verify(T, solver["order"])
        if not cert["is_linear_forest"]:
            raise AssertionError("score-window solver returned a non-LFO order")
    forced = forced_flexible_decomposition(T)
    out = {
        **score_profile(T),
        "found": solver["found"],
        "nodes": solver["nodes"],
        "max_frontier": solver["max_frontier"],
        "initial_hall": solver["initial_hall"],
        "forced_obstruction": forced_obstruction(T),
        "forced_backedge_count": forced["forced_backedge_count"],
        "flexible_pair_count": forced["flexible_pair_count"],
        "max_active_windows": forced["max_active_windows"],
        "forced_linear_forest_ok": forced["forced_linear_forest_ok"],
    }
    if compare_forced_flexible:
        ff = find_lfo_order_forced_flexible(T)
        if ff["found"]:
            cert = verify(T, ff["order"])
            if not cert["is_linear_forest"]:
                raise AssertionError("forced/flexible solver returned a non-LFO order")
        out.update({
            "ff_found": ff["found"],
            "ff_nodes": ff["nodes"],
            "ff_forced_initial_obstruction": ff["forced_initial_obstruction"],
            "ff_disagrees": ff["found"] != solver["found"],
        })
    return out


def summarize_records(records: list[dict]) -> dict:
    out = {
        "count": len(records),
        "found": summarize_bool([r["found"] for r in records]),
        "initial_hall": summarize_bool([r["initial_hall"] for r in records]),
        "forced_obstruction": summarize_categories([r["forced_obstruction"] for r in records]),
        "nodes": summarize([r["nodes"] for r in records]),
        "max_frontier": summarize([r["max_frontier"] for r in records]),
        "max_active_windows": summarize([r["max_active_windows"] for r in records]),
        "forced_backedge_count": summarize([r["forced_backedge_count"] for r in records]),
        "flexible_pair_count": summarize([r["flexible_pair_count"] for r in records]),
        "score_span": summarize([r["score_span"] for r in records]),
        "distinct_scores": summarize([r["distinct_scores"] for r in records]),
    }
    if records and "ff_nodes" in records[0]:
        out.update({
            "ff_found": summarize_bool([r["ff_found"] for r in records]),
            "ff_nodes": summarize([r["ff_nodes"] for r in records]),
            "ff_forced_initial_obstruction": summarize_categories([
                r["ff_forced_initial_obstruction"] for r in records
            ]),
            "ff_disagreements": sum(1 for r in records if r["ff_disagrees"]),
            "ff_improved_count": sum(1 for r in records if r["ff_nodes"] < r["nodes"]),
            "ff_worse_count": sum(1 for r in records if r["ff_nodes"] > r["nodes"]),
        })
    return out


def run_group(
    label: str,
    n: int,
    samples: int,
    rng: random.Random,
    make_tournament: Callable[[int, random.Random], list[list[int]]],
    compare_forced_flexible: bool = False,
) -> dict:
    t0 = time.time()
    records = [
        analyze_sample(make_tournament(n, rng), compare_forced_flexible)
        for _ in range(samples)
    ]
    return {
        "label": label,
        "n": n,
        "samples": samples,
        "seconds": round(time.time() - t0, 3),
        "summary": summarize_records(records),
    }


def run_uniform(ns: list[int], samples: int, seed: int, compare_forced_flexible: bool = False) -> dict:
    rng = random.Random(seed)
    groups = [
        run_group(f"uniform_n{n}", n, samples, rng, random_tournament, compare_forced_flexible)
        for n in ns
    ]
    rows = [
        {
            "n": group["n"],
            "max": group["summary"]["nodes"]["max"],
            "p95": group["summary"]["nodes"]["p95"],
            "median": group["summary"]["nodes"]["median"],
        }
        for group in groups
    ]
    return {
        "mode": "uniform",
        "seed": seed,
        "samples_per_n": samples,
        "compare_forced_flexible": compare_forced_flexible,
        "groups": groups,
        "regression_max": regress_growth(rows, "max") if len(rows) >= 2 else None,
        "regression_p95": regress_growth(rows, "p95") if len(rows) >= 2 else None,
    }


def run_skew(
    ns: list[int],
    ps: list[float],
    samples: int,
    seed: int,
    compare_forced_flexible: bool = False,
) -> dict:
    rng = random.Random(seed)
    groups = []
    for n in ns:
        for p in ps:
            groups.append(run_group(
                f"transitive_noise_n{n}_p{p}",
                n,
                samples,
                rng,
                lambda size, r, prob=p: transitive_noise_tournament(size, prob, r),
                compare_forced_flexible,
            ))
    by_n: dict[int, list[dict]] = defaultdict(list)
    for group in groups:
        by_n[group["n"]].append(group)
    return {
        "mode": "skew",
        "seed": seed,
        "samples_per_group": samples,
        "compare_forced_flexible": compare_forced_flexible,
        "ps": ps,
        "groups": groups,
        "by_n_forced_backedges_mean": {
            str(n): {
                group["label"]: group["summary"]["forced_backedge_count"]["mean"]
                for group in rows
            }
            for n, rows in sorted(by_n.items())
        },
    }


def parse_ints(raw: str) -> list[int]:
    return [int(x) for x in raw.split(",") if x]


def parse_floats(raw: str) -> list[float]:
    return [float(x) for x in raw.split(",") if x]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["uniform", "skew"], required=True)
    parser.add_argument("--ns", required=True, help="Comma-separated n values")
    parser.add_argument("--samples", type=int, default=200)
    parser.add_argument("--seed", type=int, default=20260522)
    parser.add_argument("--ps", default="0.02,0.05,0.1,0.2")
    parser.add_argument("--compare-forced-flexible", action="store_true")
    parser.add_argument("--out")
    args = parser.parse_args()

    if args.mode == "uniform":
        out = run_uniform(
            parse_ints(args.ns),
            args.samples,
            args.seed,
            args.compare_forced_flexible,
        )
    else:
        out = run_skew(
            parse_ints(args.ns),
            parse_floats(args.ps),
            args.samples,
            args.seed,
            args.compare_forced_flexible,
        )

    text = json.dumps(out, indent=2)
    if args.out:
        with open(args.out, "w") as f:
            f.write(text)
            f.write("\n")
    print(text)


if __name__ == "__main__":
    main()
